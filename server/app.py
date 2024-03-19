import json
import logging

from typing import Optional, cast

from sqlalchemy.exc import NoResultFound
from flask_cors import CORS
from flask import Flask, Response, request, send_file
from configure import CONFIG
from receipt import Receipt, Tag
from io import BytesIO

from storage_hooks.hook_config_factory import get_file_hook, get_meta_hook

from app_logging import init_logging

init_logging(logging.DEBUG)


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


def create_app(file_hook=None, meta_hook=None):
    if file_hook is None:
        file_hook = get_file_hook(CONFIG.StorageHooks.file_hook)

    if meta_hook is None:
        meta_hook = get_meta_hook(CONFIG.StorageHooks.meta_hook)

    logging.info(f"Starting flask app: {__name__}")
    app = Flask(__name__)
    CORS(app)

    @app.errorhandler(FileNotFoundError)
    @app.errorhandler(NoResultFound)
    def code_404(_e) -> Response:
        return response_code(404)

    @app.route("/api/receipt/", methods=["POST"])
    def upload_receipt():
        """API Endpoint for uploading a receipt image"""
        if "file" not in request.files:
            return error_response(
                404, "Missing Key", "The file has not been specified."
            )

        file = request.files["file"]
        logging.debug(f"Filename: {file.filename}, Stream: {file.stream}")

        if file is None or len(im_bytes := file.stream.read()) == 0:
            logging.error("UPLOAD ENDPOINT: API client did not send file")
            return error_response(404, "Missing File", "No file has been sent.")

        if file.filename is None or file.filename == "":
            logging.error("UPLOAD ENDPOINT: API client sent file with no filename")
            return error_response(
                404, "Missing Filename", "The file has been sent but with no filename."
            )

        logging.debug(f"UPLOAD ENDPOINT: {request.form}")
        tags = request.form.getlist("tag", type=int)

        filename = file.filename
        filename = cast(str, filename)

        file.close()

        storage_key = file_hook.save(im_bytes, filename)

        receipt = Receipt()
        receipt.name = request.form.get("name", None)
        receipt.storage_key = storage_key
        receipt.tags = meta_hook.fetch_tags(tag_ids=tags)

        receipt = meta_hook.create_receipt(receipt)
        logging.info(f"UPLOAD ENDPOINT: Saving uploaded file: {storage_key}")

        return receipt.export()

    @app.route("/api/receipt/<int:id>/image")
    def view_receipt(id: int):
        """API Endpoint for viewing a receipt

        This endpoint returns the bytes of the image to the caller

        Args:
            id: The id of the receipt to view
        """
        receipt: Optional[Receipt] = None

        receipt = meta_hook.fetch_receipt(id)

        if receipt is None:
            return error_response(
                404,
                "Missing Key Error",
                f"The key, {id}, was not found in the database",
            )

        # If we made it this far, receipt can not be None so we should be able to safely type cast
        receipt = cast(Receipt, receipt)

        # FileNotFoundError will be converted to 404 by flask
        raw_bytes = file_hook.fetch(receipt.storage_key)

        # Convert receipt image into BytesIO object
        receipt_bytes = BytesIO(raw_bytes)

        file = send_file(receipt_bytes, download_name=receipt.storage_key)
        file.headers["Upload-Date"] = str(receipt.upload_dt)
        logging.info(
            f"GET_KEY ENDPOINT: Returning file, {receipt.storage_key}, to client. Size: {len(raw_bytes)};"
        )
        logging.debug(f"GET_KEY ENDPOINT: Headers: {file.headers}")
        return file

    @app.route("/api/receipt/<int:id_>", methods=["PUT"])
    def update_receipt(id_: int):
        """API Endpoint for updating a receipt"""
        logging.debug(f"UPDATE ENDPOINT: {request.form}")

        receipt = meta_hook.update_receipt(
            receipt_id=id_,
            name=request.form.get("name", None),
            set_tags=request.form.getlist("tag", type=int) or None,
            add_tags=request.form.getlist("add tag", type=int),
            remove_tags=request.form.getlist("remove tag", type=int),
        )

        if (file := request.files.get("file", None)) is not None:
            im_bytes = file.stream.read()
            file.close()
            file_hook.replace(receipt.storage_key, im_bytes)

        return receipt.export()

    @app.route("/api/receipt/<int:id>/")
    def fetch_receipt(id: int):
        """API Endpoint for viewing receipt metadata

        Args:
            id: The id of the receipt to fetch
        """
        if (receipt := meta_hook.fetch_receipt(id)) is None:
            return error_response(
                404,
                "Missing Key Error",
                f"The key, {id}, was not found in the database",
            )
        return receipt.export()

    @app.route("/api/receipt/")
    def fetch_receipt_keys():
        receipts = meta_hook.fetch_receipts()

        response = [r.export() for r in receipts]

        logging.info(f"FETCH_MANY_KEYS ENDPOINT: Returning {len(receipts)} receipts")
        logging.debug(f"FETCH_MANY_KEYS ENDPOINT: Response: {json.dumps(response)}")

        # TODO: Maybe allow the user to customize how they want the response to be sorted
        sorted(response, key=lambda receipt: receipt["name"])

        return response

    @app.route("/api/receipt/<int:id>", methods=["DELETE"])
    def delete_receipt(id: int):
        """Deletes a receipt in the AWS bucket

        Args:
            id: The id of the receipt to delete
        """
        r = meta_hook.fetch_receipt(id)

        if r is None:
            logging.info(
                f"Client attempted to delete receipt -- {id} -- that doesn't exists"
            )
            return error_response(
                404, "Missing Key Error", f"The key, {id} was not found in the database"
            )

        storage_key = r.storage_key
        meta_hook.delete_receipt(id)
        file_hook.delete(storage_key)

        logging.info(f"DELETE ENDPOINT: Deleting Receipt {id}")

        return response_code(204)

    @app.route("/api/tag/", methods=["POST"])
    def upload_tag():
        """API Endpoint for uploading a receipt image.

        Returns:
            The id for the newly created tag
        Raises:
            400 if tag_name is empty
        """

        tag_name = request.form.get("name", "")

        if tag_name == "":
            logging.error("UPLOAD ENDPOINT: API client tried making tag with no name")
            return error_response(404, "Missing Name", "Tag Name not specified")

        tag = Tag(name=tag_name)
        return str(meta_hook.create_tag(tag))

    @app.route("/api/tag/<int:tag_id>")
    def fetch_tag(tag_id: int):
        tag = meta_hook.fetch_tag(tag_id)

        if tag is None:
            return error_response(
                404, "Tag Not Found", "The provided tag does not exists in the database"
            )

        response = tag.export()

        logging.info("FETCH_TAG ENDPOINT: Returning 1 tag")
        logging.debug(f"FETCH_TAG ENDPOINT: Response: {json.dumps(response)}")

        return response

    @app.route("/api/tag/")
    def fetch_tags():
        tags = meta_hook.fetch_tags()

        response = [t.export() for t in tags]

        logging.info(f"FETCH_TAGS ENDPOINT: Returning {len(tags)} tags")
        logging.debug(f"FETCH_TAGS ENDPOINT: Response: {json.dumps(response)}")

        return response

    @app.route("/api/tag/<int:tag_id>/", methods=["PUT"])
    def update_tag(tag_id: int):
        """Updates a tag

        Args:
            tag_id: The id of the tag to update
        """
        if (tag := meta_hook.fetch_tag(tag_id)) is None:
            return response_code(404)

        if "name" in request.form:
            tag.name = request.form.get("name")

        return meta_hook.update_tag(tag).export()

    @app.route("/api/tag/<int:tag_id>", methods=["DELETE"])
    def delete_tag(tag_id: int):
        """Deletes a Tag

        Args:
            tag_id: The  name to delete
        """
        meta_hook.delete_tag(tag_id)

        logging.info(f"DELETE TAG ENDPOINT: Deleting tag: {tag_id}")

        return response_code(204)

    return app
