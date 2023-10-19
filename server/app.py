import os
import json

from flask import Flask, Response, flash, request
from receipt import Receipt
from storage_hooks import AWSHook

app = Flask(__name__)


def error_response(status: int, error_name: str, error_message: str) -> Response:
    res_json = {"error_name": error_name, "error_message": error_message}
    return Response(json.dumps(res_json), status=status, mimetype="application/json")


@app.route("/api/receipt/upload", methods=["POST"])
def upload_receipt():
    if "file" not in request.files:
        return error_response(400, "Missing Key", "The file has not been specified.")

    file = request.files["file"]

    if file.filename == "":
        return error_response(400, "Missing Filename", "The file has been sent but with no filename.")
        pass

    if file:
        filename = file.filename

        # Read all bytes from file and join them into a single list
        im_bytes = b''.join(file.stream.readlines())
        file.close()

        aws = AWSHook()
        aws.upload_receipt(Receipt(filename, im_bytes))

    return error_response(400, "Missing File", "No file has been sent.")


@app.route("/api/receipt/view")
def view_receipt():
    return error_response(501, "ImplementationError", "Not Fully Implemented")
