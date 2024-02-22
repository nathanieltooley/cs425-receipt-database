import io
from typing import Any, cast
from flask import Flask
from flask.testing import FlaskClient

import pytest
import modulefinder
import sys
import pathlib
from receipt import Receipt, Tag

file_path = pathlib.Path(__file__).absolute()
sys.path.append(str(file_path.parent.parent))
from storage_hooks.SQLite3 import SQLite3
from tests.temp_hooks import MemorySQLite3, FileSystemHook


@pytest.fixture()
def app():
    from app import create_app

    app = create_app(FileSystemHook(), MemorySQLite3())

    app.config.update(
        {
            "TESTING": True,
        }
    )

    return app


@pytest.fixture()
def test_client(app: Flask):
    return app.test_client()


@pytest.fixture()
def runner(app: Flask):
    return app.test_cli_runner()


def test_upload_receipt(test_client: FlaskClient, mocker):
    data = {}
    data["file"] = (io.BytesIO(b"Test"), "test.jpg")

    test_receipt = Receipt()
    test_receipt.id = 1
    test_receipt.name = "Test"

    tags = [Tag(id=1, name="Test Tag")]
    test_receipt.tags = tags

    fs_save_patch = mocker.patch("storage_hooks.file_system.FileSystemHook.save")
    mocker.patch("storage_hooks.storage_hooks.DatabaseHook.fetch_tags")
    mocker.patch(
        "storage_hooks.storage_hooks.DatabaseHook.create_receipt",
        return_value=test_receipt,
    )
    response = test_client.post("/api/receipt/", data=data)
    response_json = cast(Any, response.json)

    assert response.status_code == 200
    assert response_json["id"] == 1
    assert response_json["name"] == "Test"
    assert len(response_json["tags"]) >= 1
    assert response_json["tags"][0] == 1
    assert fs_save_patch.call_count == 1

    fs_save_patch.assert_called_once_with(b"", "test.jpg")


def test_upload_receipt_missing_file_key(test_client: FlaskClient):
    response = test_client.post("/api/receipt/")
    response_json = cast(Any, response.json)
    assert response.status_code == 404
    assert response_json["error_name"] == "Missing Key"


def test_upload_receipt_missing_file_data(test_client: FlaskClient):
    data = {}
    data["file"] = (io.BytesIO(b""), "test.jpg")

    response = test_client.post("/api/receipt/", data=data)

    assert response.status_code == 404
    assert cast(Any, response.json)["error_name"] == "Missing File"


def test_upload_receipt_missing_filename(test_client: FlaskClient):
    data = {"file": (io.BytesIO(b"test"), "")}

    response = test_client.post(
        "/api/receipt/", data=data, content_type="multipart/form-data"
    )

    assert response.status_code == 404
    assert cast(Any, response.json)["error_name"] == "Missing Filename"


def test_view_receipt(test_client: FlaskClient, mocker):
    test_image = b"test image"
    test_receipt = Receipt(id=1, name="Test", storage_key="~/test/test.jpg")

    fetch_receipt_mock = mocker.patch(
        "storage_hooks.storage_hooks.DatabaseHook.fetch_receipt",
        return_value=test_receipt,
    )
    fetch_mock = mocker.patch(
        "storage_hooks.file_system.FileSystemHook.fetch",
        return_value=test_image,
    )

    response = test_client.get("/api/receipt/1/image")

    assert response.data == test_image

    fetch_receipt_mock.assert_called_once_with(1)
    fetch_mock.assert_called_once_with("~/test/test.jpg")


def test_view_receipt_no_receipt(test_client: FlaskClient, mocker):
    mocker.patch(
        "storage_hooks.storage_hooks.DatabaseHook.fetch_receipt", return_value=None
    )

    response = test_client.get("/api/receipt/1/image")

    j = cast(Any, response.json)

    assert response.status_code == 404
    assert j["error_name"] == "Missing Key Error"
    assert j["error_message"] == "The key, 1, was not found in the database"
