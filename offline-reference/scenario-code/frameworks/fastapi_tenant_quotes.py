"""Python 3.11+. Requires FastAPI, Pydantic 2 and httpx. No listening server.
Fixed tokens are trusted test fixtures, not production authentication.
"""
from typing import Annotated
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict, Field, StrictInt

TOKENS = {"Bearer fixture-acme": "acme", "Bearer fixture-bravo": "bravo"}

class QuoteInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    sku: str = Field(min_length=1, max_length=40, pattern=r"^[A-Z0-9-]+$")
    quantity: StrictInt = Field(ge=1, le=100)

def verified_tenant(authorization: Annotated[str | None, Header()] = None):
    tenant = TOKENS.get(authorization)
    if tenant is None:
        raise HTTPException(401, "Invalid fixture credential")
    return tenant

def create_app():
    app = FastAPI()
    # Price is server-owned. Caller cannot supply tenant or price in request body.
    prices = {("acme", "BOOK"): 1250, ("bravo", "BOOK"): 1500}

    @app.post("/quotes")
    def quote(body: QuoteInput, tenant: Annotated[str, Depends(verified_tenant)]):
        unit = prices.get((tenant, body.sku))
        if unit is None:
            raise HTTPException(404, "SKU unavailable")
        return {"tenant": tenant, "total_cents": unit * body.quantity}
    return app

def self_test():
    app = create_app()
    with TestClient(app) as client:
        headers = {"Authorization": "Bearer fixture-acme", "X-Tenant": "bravo"}
        result = client.post("/quotes", headers=headers, json={"sku": "BOOK", "quantity": 2})
        assert result.status_code == 200 and result.json() == {"tenant": "acme", "total_cents": 2500}
        assert client.post("/quotes", json={"sku": "BOOK", "quantity": 1}).status_code == 401
        for quantity in [0, 101, "2", True]:
            assert client.post("/quotes", headers=headers, json={"sku": "BOOK", "quantity": quantity}).status_code == 422
        assert client.post("/quotes", headers=headers, json={"sku": "BOOK", "quantity": 1, "tenant": "bravo"}).status_code == 422
        assert client.post("/quotes", headers=headers, json={"sku": "UNKNOWN", "quantity": 1}).status_code == 404
    # Dependency override demonstrates testing a policy seam without remote auth.
    app.dependency_overrides[verified_tenant] = lambda: "bravo"
    with TestClient(app) as client:
        assert client.post("/quotes", json={"sku": "BOOK", "quantity": 2}).json()["total_cents"] == 3000
    app.dependency_overrides.clear()
    print("PASS: validation, authorization seam, tenant isolation, override cleanup")

if __name__ == "__main__":
    self_test()
