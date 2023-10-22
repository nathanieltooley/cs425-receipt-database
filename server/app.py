import os
import json

from flask import Flask, Response, flash, request, send_file
from receipt import Receipt
from storage_hooks import AWSHook

app = Flask(__name__)


def error_response(status: int, error_name: str, error_message: str) -> Response:
    res_json = {"error_name": error_name, "error_message": error_message}
    return Response(json.dumps(res_json), status=status, mimetype="application/json")


def response_code(status: int) -> Response:
    return Response("", status=status, mimetype="application/json")


@app.route("/api/receipt/upload", methods=["POST"])
def upload_receipt():
    if "file" not in request.files:
        return error_response(400, "Missing Key", "The file has not been specified.")

    file = request.files["file"]

    if file.filename == "":
        return error_response(
            400, "Missing Filename", "The file has been sent but with no filename."
        )
        pass

    if file:
        filename = file.filename

        # Read all bytes from file and join them into a single list
        im_bytes = b"".join(file.stream.readlines())
        file.close()

        aws = AWSHook()
        aws.upload_receipt(Receipt(filename, im_bytes))
        return response_code(200)
    else:
        return error_response(400, "Missing File", "No file has been sent.")


@app.route("/api/receipt/view/<file_key>")
def view_receipt(file_key: str):
    aws = AWSHook()
    receipt = aws.fetch_receipt(file_key)
    file_path = os.path.join(".temp", file_key)

    with open(f"{file_path}", "wb") as file:
        file.write(receipt.ph_body)

    return send_file(file_path)


@app.route("/api/receipt/delete/<file_key>")
def delete_receipt(file_key: str):
    aws = AWSHook()
    aws.delete_receipt_by_id(file_key)

    return response_code(200)
