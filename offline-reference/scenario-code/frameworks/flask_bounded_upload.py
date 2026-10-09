"""Flask 3.1 bounded text upload. Storage only inside self-test TemporaryDirectory.
Extension/UTF-8 checks are not malware detection or document-parser hardening.
"""
import io
import tempfile
import uuid
from pathlib import Path
from flask import Flask, jsonify, request

def create_app(storage):
    app = Flask(__name__)
    app.config.update(TESTING=True,MAX_CONTENT_LENGTH=4096)
    storage = Path(storage).resolve()

    @app.post("/documents")
    def upload():
        file = request.files.get("document")
        if file is None or not file.filename:
            return jsonify(error="document required"),400
        if Path(file.filename).suffix.lower() != ".txt":
            return jsonify(error="only txt allowed"),415
        raw = file.stream.read(1025)
        if len(raw) > 1024:
            return jsonify(error="file too large"),413
        if not raw:
            return jsonify(error="empty file"),400
        try:
            text = raw.decode("utf-8",errors="strict")
        except UnicodeDecodeError:
            return jsonify(error="UTF-8 required"),415
        if "\x00" in text:
            return jsonify(error="NUL forbidden"),415
        # Client filename is metadata only; generated ID determines storage path.
        document_id = uuid.uuid4().hex
        target = storage / f"{document_id}.txt"
        with target.open("xb") as handle:
            handle.write(raw)
        return jsonify(id=document_id,bytes=len(raw)),201

    @app.errorhandler(413)
    def oversized(error):
        return jsonify(error="request too large"),413
    return app

def self_test():
    with tempfile.TemporaryDirectory() as directory:
        client = create_app(directory).test_client()
        def send(raw,name):
            return client.post("/documents",data={"document":(io.BytesIO(raw),name)})
        first = send(b"hello","../../escape.txt")
        assert first.status_code == 201
        files = list(Path(directory).iterdir())
        assert len(files) == 1 and files[0].parent.resolve() == Path(directory).resolve()
        assert files[0].name == first.json["id"] + ".txt" and files[0].read_bytes() == b"hello"
        assert send(b"x"*1024,"limit.txt").status_code == 201
        assert send(b"x"*1025,"too-large.txt").status_code == 413
        assert send(b"x"*5000,"request-too-large.txt").status_code == 413
        assert send(b"","empty.txt").status_code == 400
        assert send(b"\xff","bad.txt").status_code == 415
        assert send(b"binary\x00","bad.txt").status_code == 415
        assert send(b"hello","script.py").status_code == 415
        assert client.post("/documents",data={}).status_code == 400
        assert len(list(Path(directory).iterdir())) == 2
    print("PASS: body/file bounds, generated names, UTF-8, empty/rejected uploads")

if __name__ == "__main__":
    self_test()
