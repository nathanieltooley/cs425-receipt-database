import json
import logging
import botocore.exceptions

from typing import Optional, cast
from flask_cors import CORS
from flask import Flask, Response, request, send_file
from configure import CONFIG
from receipt import Receipt, Tag
from storage_hooks.AWS import AWSS3Hook
from io import BytesIO

from storage_hooks.hook_config_factory import get_file_hook, get_meta_hook

from app_logging import init_logging

init_logging(logging.DEBUG)

logging.info(f"Starting flask app: {__name__}")
app = Flask(__name__)
CORS(app)

file_hook = get_file_hook(CONFIG.StorageHooks.file_hook)
meta_hook = get_meta_hook(CONFIG.StorageHooks.meta_hook)


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


@app.route("/api/tag/", methods=["POST"])
def upload_tag():
    """API Endpoint for uploading a receipt image.

    Returns:
        ~~The id for the newly created tag~~ Code 200
    Raises:
        400 if tag_name is empty
    """

    tag_name = request.form.get("name", "")

    if tag_name == "":
        logging.error("UPLOAD ENDPOINT: API client tried making tag with no name")
        return error_response(
            400, "Missing Name", "Tag Name not specified"
        )

    tag = Tag(name=tag_name)
    return str(meta_hook.create_tag(tag))


@app.route("/api/tag/<int:tag_id>")
def fetch_tag(tag_id: int):
    tag = meta_hook.fetch_tag(tag_id)

    response = {"result": {"id": tag.id, "name": tag.name}}

    response_j_string = json.dumps(response)
    logging.info(f"FETCH_TAG ENDPOINT: Returning 1 tag")
    logging.debug(f"FETCH_TAG ENDPOINT: Response: {response_j_string}")

    return Response(response_j_string, 200)


@app.route("/api/tag/")
def fetch_tags():
    tags = meta_hook.fetch_tags()

    response = {"results": []}

    for tag in tags:
        response["results"].append({"id": tag.id, "name": tag.name})

    response_j_string = json.dumps(response)
    logging.info(f"FETCH_TAGS ENDPOINT: Returning {len(tags)} tags")
    logging.debug(f"FETCH_TAGS ENDPOINT: Response: {response_j_string}")

    return Response(response_j_string, 200)


@app.route("/api/tag/<int:tag_id>", methods=['DELETE'])
def delete_tag(tag_id: int):
    """Deletes a Tag

    Args:
        tag_id: The  name to delete
    """
    tag = meta_hook.fetch_tag(tag_id)
    meta_hook.delete_objects(tag)

    logging.info(f"DELETE TAG ENDPOINT: Deleting tag: {tag_id}")

    return response_code(200)


@app.route("/api/receipt/upload", methods=["POST"])
def upload_receipt():
    """API Endpoint for uploading a receipt image"""
    if "file" not in request.files:
        return error_response(400, "Missing Key", "The file has not been specified.")

    file = request.files["file"]

    if file.filename == "":
        logging.error("UPLOAD ENDPOINT: API client sent file with no filename")
        return error_response(
            400, "Missing Filename", "The file has been sent but with no filename."
        )

    if file:
        filename = file.filename
        filename = cast(str, filename)

        # Read all bytes from file and join them into a single list
        im_bytes = b"".join(file.stream.readlines())
        file.close()

        r_key = file_hook.save(im_bytes)

        receipt = Receipt()
        receipt.key = r_key
        receipt.body = b""

        meta_hook.save_objects(receipt)
        logging.info(f"UPLOAD ENDPOINT: Saving uploaded file: {r_key}")
        return response_code(200)
    else:
        logging.error("UPLOAD ENDPOINT: API client did not send file")
        return error_response(400, "Missing File", "No file has been sent.")


@app.route("/api/receipt/view/<file_key>")
def view_receipt(file_key: str):
    """API Endpoint for viewing a receipt

    This endpoint returns the bytes of the image to the caller

    Args:
        file_key: The AWS file name to view
    """
    receipt: Optional[Receipt] = None

    try:
        receipt = meta_hook.fetch_receipt(file_key)
    except botocore.exceptions.ClientError as error:
        if error.response["Error"]["Code"] == "NoSuchKey":
            return error_response(
                400,
                "No such key",
                f"The key, {file_key}, was not found in the database",
            )

    # If we made it this far, receipt can not be None so we should be able to safely type cast
    receipt = cast(Receipt, receipt)

    raw_bytes = file_hook.fetch(receipt.key)
    # Convert receipt image into BytesIO object
    receipt_bytes = BytesIO(raw_bytes)

    file = send_file(receipt_bytes, download_name=file_key)
    file.headers["Upload-Date"] = str(receipt.upload_dt)
    logging.info(
        f"GET_KEY ENDPOINT: Returning file, {file_key}, to client. Size: {len(raw_bytes)};"
    )
    logging.debug(f"GET_KEY ENDPOINT: Headers: {file.headers}")
    return file


@app.route("/api/receipt/fetch_many_keys")
def fetch_receipt_keys():
    receipts = meta_hook.fetch_receipts()

    response = {"results": []}

    for r in receipts:
        response["results"].append(
            {"key": r.key, "metadata": {"upload_dt": str(r.upload_dt)}}
        )

    response_j_string = json.dumps(response)
    logging.info(f"FETCH_MANY_KEYS ENDPOINT: Returning {len(receipts)} receipts")
    logging.debug(f"FETCH_MANY_KEYS ENDPOINT: Response: {response_j_string}")

    return Response(response_j_string, 200)


@app.route("/api/receipt/delete/<file_key>")
def delete_receipt(file_key: str):
    """Deletes a receipt in the AWS bucket

    Args:
        file_key: The AWS file name to delete

    """
    file_hook.delete(file_key)

    r = meta_hook.fetch_receipt(file_key)
    meta_hook.delete_objects(r)

    logging.info(f"DELETE ENDPOINT: Deleting {file_key}")

    return response_code(200)
