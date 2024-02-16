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
    data["file"] = (io.BytesIO(b""), "test.jpg")

    fs_save_patch = mocker.patch("storage_hooks.file_system.FileSystemHook.save")
    mocker.patch("storage_hooks.storage_hooks.DatabaseHook.fetch_tags")
    mocker.patch(
        "storage_hooks.storage_hooks.DatabaseHook.create_receipt", return_value=1
    )
    response = test_client.post("/api/receipt/upload", data=data)
    response_json = cast(Any, response.json)

    assert response.status == "200 OK"
    assert response_json["id"] == 1
    assert fs_save_patch.call_count == 1
