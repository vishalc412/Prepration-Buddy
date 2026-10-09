"""Durable local job submission, no broker/provider. Requires FastAPI/Pydantic 2/httpx.
SQLite fixture proves sequential contracts; production concurrency requires its DB tests.
"""
import hashlib
import json
import sqlite3
import tempfile
from pathlib import Path
from typing import Annotated
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict, Field
from fastapi_tenant_quotes import verified_tenant

class JobInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    document: str = Field(min_length=1, max_length=500)

def create_app(database):
    with sqlite3.connect(database) as db:
        db.execute("CREATE TABLE IF NOT EXISTS jobs (id INTEGER PRIMARY KEY, tenant TEXT, key TEXT, digest TEXT, document TEXT, state TEXT, UNIQUE(tenant,key))")
    app = FastAPI()

    @app.post("/jobs", status_code=202)
    def submit(body: JobInput, tenant: Annotated[str, Depends(verified_tenant)],
               key: Annotated[str, Header(alias="Idempotency-Key", min_length=1, max_length=80)]):
        digest = hashlib.sha256(json.dumps(body.model_dump(), sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        with sqlite3.connect(database, timeout=2) as db:
            db.execute("BEGIN IMMEDIATE")
            existing = db.execute("SELECT id,digest,state FROM jobs WHERE tenant=? AND key=?", (tenant,key)).fetchone()
            if existing:
                if existing[1] != digest:
                    raise HTTPException(409, "Key reused with different request")
                return {"id": existing[0], "state": existing[2], "replayed": True}
            cursor = db.execute("INSERT INTO jobs(tenant,key,digest,document,state) VALUES(?,?,?,?,?)", (tenant,key,digest,body.document,"pending"))
            return {"id": cursor.lastrowid, "state": "pending", "replayed": False}

    @app.get("/jobs/{job_id}")
    def status(job_id: int, tenant: Annotated[str, Depends(verified_tenant)]):
        with sqlite3.connect(database) as db:
            row = db.execute("SELECT state FROM jobs WHERE id=? AND tenant=?", (job_id,tenant)).fetchone()
        if row is None:
            raise HTTPException(404, "Job not found")
        return {"id": job_id, "state": row[0]}
    return app

def complete_one(database, job_id):
    # Simulated worker: state transition only. Real effects need downstream idempotency.
    with sqlite3.connect(database) as db:
        return db.execute("UPDATE jobs SET state='succeeded' WHERE id=? AND state='pending'", (job_id,)).rowcount

def self_test():
    with tempfile.TemporaryDirectory() as directory:
        path = str(Path(directory) / "jobs.sqlite3")
        headers = {"Authorization": "Bearer fixture-acme", "Idempotency-Key": "order-7"}
        with TestClient(create_app(path)) as client:
            first = client.post("/jobs", headers=headers, json={"document": "hello"})
            replay = client.post("/jobs", headers=headers, json={"document": "hello"})
            assert first.status_code == replay.status_code == 202
            job_id = first.json()["id"]
            assert replay.json()["id"] == job_id and replay.json()["replayed"]
            assert client.post("/jobs", headers=headers, json={"document": "changed"}).status_code == 409
            assert client.get(f"/jobs/{job_id}", headers={"Authorization": "Bearer fixture-bravo"}).status_code == 404
        # New app instance simulates web-process restart; records survive.
        with TestClient(create_app(path)) as client:
            assert client.post("/jobs", headers=headers, json={"document": "hello"}).json()["id"] == job_id
            assert complete_one(path, job_id) == 1 and complete_one(path, job_id) == 0
            assert client.get(f"/jobs/{job_id}", headers=headers).json()["state"] == "succeeded"
        with sqlite3.connect(path) as db:
            assert db.execute("SELECT count(*) FROM jobs").fetchone()[0] == 1
    print("PASS: replay, conflict, restart, ownership, conditional transition")

if __name__ == "__main__":
    self_test()
