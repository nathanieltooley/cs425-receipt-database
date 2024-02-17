import io
from typing import Any, cast
from flask import Flask
from flask.testing import FlaskClient

import pytest
import modulefinder
import sys
import pathlib

file_path = pathlib.Path(__file__).absolute()
sys.path.append(str(file_path.parent.parent))
from storage_hooks.SQLite3 import SQLite3
from storage_hooks.file_system import FileSystemHook
from storage_hooks.storage_hooks import FileHook, StorageHook


@pytest.fixture()
def app():
    from app import create_app

    app = create_app(FileSystemHook(), SQLite3())

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

    fs_save_patch = mocker.patch("storage_hooks.file_system.FileSystemHook.save")
    mocker.patch("storage_hooks.storage_hooks.DatabaseHook.fetch_tags")
    mocker.patch(
        "storage_hooks.storage_hooks.DatabaseHook.create_receipt", return_value=1
    )
    response = test_client.post("/api/receipt/upload", data=data)
    response_json = cast(Any, response.json)

    assert response.status_code == 200
    assert response_json["id"] == 1
    assert fs_save_patch.call_count == 1

    fs_save_patch.assert_called_once_with(b"", "test.jpg")


def test_upload_receipt_missing_file_key(test_client: FlaskClient):
    response = test_client.post("/api/receipt/upload")
    response_json = cast(Any, response.json)
    assert response.status_code == 404
    assert response_json["error_name"] == "Missing Key"


def test_upload_receipt_missing_file_data(test_client: FlaskClient):
    data = {}
    data["file"] = (io.BytesIO(b""), "test.jpg")

    response = test_client.post("/api/receipt/upload", data=data)

    assert response.status_code == 404
    assert cast(Any, response.json)["error_name"] == "Missing File"


def test_upload_receipt_missing_filename(test_client: FlaskClient):
    none_data = {"file": (io.BytesIO(b"test"), None)}

    none_response = test_client.post("/api/receipt/upload", data=none_data)

    assert none_response.status_code == 404
    assert cast(Any, none_response.json)["error_name"] == "Missing Filename"


# I wanted to do this in the previous test
# however, there seems to be some sort of state or side effect that causes
# the wrong error to be triggered in a second post request
def test_upload_receipt_missing_filename_empty(test_client: FlaskClient):
    empty_data = {"file": (io.BytesIO(b"test"), "")}

    empty_response = test_client.post("/api/receipt/upload", data=empty_data)

    assert empty_response.status_code == 404
    assert cast(Any, empty_response.json)["error_name"] == "Missing Filename"
