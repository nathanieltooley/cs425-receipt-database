import os
import json
import tempfile
from flask_cors import CORS

from flask import Flask, Response, flash, request, send_file
from receipt import Receipt
from storage_hooks.AWS import AWSHook
from io import BytesIO

app = Flask(__name__)
CORS(app)


def error_response(status: int, error_name: str, error_message: str) -> Response:
    """Create and return a Flask Response object that contains error information

    Args:
        status: HTML Status code to send with the response
        error_name: Name of the error
        error_message: Message to go along with the error

    Returns:
        Response
    """
    res_json = {"error_name": error_name, "error_message": error_message}
    return Response(json.dumps(res_json), status=status, mimetype="application/json")


def response_code(status: int) -> Response:
    """Create an empty response with a status code

    Args:
        status: HTML Status code

    Returns:
        Response
    """
    return Response("", status=status, mimetype="application/json")


@app.route("/api/receipt/upload", methods=["POST"])
def upload_receipt():
    """API Endpoint for uploading a receipt image"""
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
    """API Endpoint for viewing a receipt

    This endpoint returns the bytes of the image to the caller

    Args:
        file_key: The AWS file name to view
    """
    aws = AWSHook()
    receipt = aws.fetch_receipt(file_key)

    r_bytes = BytesIO(receipt.ph_body)
    return send_file(r_bytes, download_name=file_key)


@app.route("/api/receipt/delete/<file_key>")
def delete_receipt(file_key: str):
    """Deletes a receipt in the AWS bucket

    Args:
        file_key: The AWS file name to delete

    """
    aws = AWSHook()
    aws.delete_receipt_by_id(file_key)

    return response_code(200)
