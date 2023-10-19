import os
import json

from flask import Flask, Response, flash, request
from storage_hooks import AWSHook

app = Flask(__name__)


def error_response(status: int, error_name: str, error_message: str) -> Response:
    res_json = {"error_name": error_name, "error_message": error_message}
    return Response(json.dumps(res_json), status=status, mimetype="application/json")


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

    return error_response(501, "ImplementationError", "Not Fully Implemented")


@app.route("/api/receipt/view")
def view_receipt():
    return error_response(501, "ImplementationError", "Not Fully Implemented")
