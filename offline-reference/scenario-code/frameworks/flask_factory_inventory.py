"""Flask 3.1 app factory, blueprint, validation and stable JSON errors. No server."""
from flask import Blueprint, Flask, current_app, jsonify, request
from werkzeug.exceptions import BadRequest, HTTPException

def create_app(testing=True):
    app = Flask(__name__)
    app.config.update(TESTING=testing, MAX_CONTENT_LENGTH=2048)
    app.extensions["inventory"] = {}
    api = Blueprint("inventory_api",__name__,url_prefix="/api")

    @api.post("/items")
    def add_item():
        if not request.is_json:
            return jsonify(error="JSON required"),415
        body = request.get_json()  # Malformed JSON raises BadRequest.
        if not isinstance(body,dict) or set(body) != {"sku","quantity"}:
            raise BadRequest("Expected sku and quantity only")
        if not isinstance(body["sku"],str) or not body["sku"].isalnum() or len(body["sku"]) > 30:
            raise BadRequest("Invalid SKU")
        if type(body["quantity"]) is not int or not 0 <= body["quantity"] <= 10000:
            raise BadRequest("Quantity must be integer 0..10000")
        store = current_app.extensions["inventory"]
        if body["sku"] in store:
            return jsonify(error="SKU exists"),409
        store[body["sku"]] = body["quantity"]
        return jsonify(body),201

    @api.get("/items/<sku>")
    def get_item(sku):
        store = current_app.extensions["inventory"]
        if sku not in store:
            return jsonify(error="Not found"),404
        return jsonify(sku=sku,quantity=store[sku])

    @app.errorhandler(HTTPException)
    def json_error(error):
        response = error.get_response()
        response.data = app.json.dumps({"error":error.name,"status":error.code})
        response.content_type = "application/json"
        return response
    app.register_blueprint(api)
    return app

def self_test():
    app = create_app()
    client = app.test_client()
    assert client.post("/api/items",json={"sku":"BOOK","quantity":4}).status_code == 201
    assert client.get("/api/items/BOOK").json == {"sku":"BOOK","quantity":4}
    assert client.post("/api/items",json={"sku":"BOOK","quantity":4}).status_code == 409
    for body in [{"sku":"BAD","quantity":True},{"sku":"BAD","quantity":-1},["BAD"],{"sku":"BAD","quantity":1,"admin":True}]:
        assert client.post("/api/items",json=body).status_code == 400
    assert client.post("/api/items",data="{broken",content_type="application/json").status_code == 400
    assert client.post("/api/items",data="plain").status_code == 415
    assert client.get("/missing").json == {"error":"Not Found","status":404}
    assert create_app().test_client().get("/api/items/BOOK").status_code == 404
    print("PASS: app isolation, blueprint routing, strict validation, JSON errors")

if __name__ == "__main__":
    self_test()
