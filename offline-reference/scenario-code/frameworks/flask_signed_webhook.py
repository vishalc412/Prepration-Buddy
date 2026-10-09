"""Flask 3.1 + stdlib signature/replay fixture. No real payment provider.
Signature format is tutorial-defined; use exact provider specification in production.
"""
import hashlib
import hmac
import json
import re
import sqlite3
import tempfile
from pathlib import Path
from flask import Flask, jsonify, request

FIXTURE_SECRET = b"trusted-offline-fixture-secret-not-production"
FIXTURE_NOW = 2_000_000_000

def signature(timestamp,raw):
    return hmac.new(FIXTURE_SECRET,str(timestamp).encode()+b"."+raw,hashlib.sha256).hexdigest()

def create_app(database,now=lambda:FIXTURE_NOW):
    app = Flask(__name__)
    app.config.update(TESTING=True,MAX_CONTENT_LENGTH=2048)
    with sqlite3.connect(database) as db:
        db.execute("CREATE TABLE IF NOT EXISTS events(id TEXT PRIMARY KEY,digest TEXT,amount_cents INTEGER)")

    @app.post("/webhooks")
    def webhook():
        raw = request.get_data(cache=True)
        try:
            stamp = int(request.headers.get("X-Timestamp",""))
        except ValueError:
            return jsonify(error="invalid timestamp"),401
        supplied = request.headers.get("X-Signature","")
        if (abs(now()-stamp) > 300 or re.fullmatch(r"[0-9a-f]{64}", supplied) is None
                or not hmac.compare_digest(signature(stamp,raw),supplied)):
            return jsonify(error="invalid signature or stale request"),401
        try:
            body = json.loads(raw)
            if not isinstance(body,dict) or set(body) != {"id","amount_cents"}:
                raise ValueError("Unexpected fields")
            if not isinstance(body["id"],str) or not 1 <= len(body["id"]) <= 80:
                raise ValueError("Invalid ID")
            if type(body["amount_cents"]) is not int or not 0 <= body["amount_cents"] <= 1_000_000:
                raise ValueError("Invalid amount")
        except (ValueError,TypeError,UnicodeDecodeError):
            return jsonify(error="invalid event"),400
        digest = hashlib.sha256(raw).hexdigest()
        with sqlite3.connect(database,timeout=2) as db:
            db.execute("BEGIN IMMEDIATE")
            existing = db.execute("SELECT digest FROM events WHERE id=?",(body["id"],)).fetchone()
            if existing:
                if existing[0] != digest:
                    return jsonify(error="event ID payload conflict"),409
                return jsonify(replayed=True),200
            db.execute("INSERT INTO events VALUES(?,?,?)",(body["id"],digest,body["amount_cents"]))
        # Record is durable before acknowledging. No separate side effect in fixture.
        return jsonify(replayed=False),200
    return app

def self_test():
    with tempfile.TemporaryDirectory() as directory:
        database = str(Path(directory)/"events.sqlite3")
        client = create_app(database).test_client()
        raw = b'{"id":"evt-1","amount_cents":250}'
        def send(client,body,stamp=FIXTURE_NOW,sig=None):
            return client.post("/webhooks",data=body,content_type="application/json",
                headers={"X-Timestamp":str(stamp),"X-Signature":signature(stamp,body) if sig is None else sig})
        assert send(client,raw).json == {"replayed":False}
        assert send(client,raw).json == {"replayed":True}
        assert send(client,b'{"id":"evt-1","amount_cents":251}').status_code == 409
        assert send(client,raw,sig="0"*64).status_code == 401
        assert send(client,raw,sig="é").status_code == 401
        assert send(client,raw,sig="").status_code == 401
        assert send(client,raw,stamp=FIXTURE_NOW-301).status_code == 401
        assert send(client,b"bad json").status_code == 400
        assert send(client,b'{"id":"bad","amount_cents":true}').status_code == 400
        assert send(client,b"x"*3000).status_code == 413
        restarted = create_app(database).test_client()
        assert send(restarted,raw).json == {"replayed":True}
        with sqlite3.connect(database) as db:
            assert db.execute("SELECT count(*),sum(amount_cents) FROM events").fetchone() == (1,250)
    print("PASS: raw-byte signature, freshness, durable replay, conflict and validation")

if __name__ == "__main__":
    self_test()
