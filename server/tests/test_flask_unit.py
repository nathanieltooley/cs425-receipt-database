import io
from typing import Any, cast
from flask import Flask, json
from flask.testing import FlaskClient

import pytest
from pytest_mock import MockerFixture
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
