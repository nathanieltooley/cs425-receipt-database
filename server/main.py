import os

from flask import Flask, Response, flash, request
from storage_hooks import AWSHook

app = Flask(__name__)


@app.route("/api/receipt/upload", method=["POST"])
def upload_receipt():
    if "file" not in request.files:
        pass

    file = request.files["file"]

    if file.filename == "":
        pass

    if file:
        filename = file.filename
        file.save(os.path.join(".", filename))

    return Response("", status=501, mimetype="application/json")


@app.route("/api/receipt/view")
def view_receipt():
    return Response("", status=501, mimetype="application/json")
