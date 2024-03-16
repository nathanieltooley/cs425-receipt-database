from os import walk
from typing import List, cast, Any
from boto3 import logging
from flask.testing import FlaskClient
from flask import Flask
from storage_hooks.storage_hooks import DatabaseHook, FileHook, StorageHook
from werkzeug.datastructures import MultiDict
from receipt import Tag

import pytest
import io

from temp_hooks import sqlite3, MemorySQLite3, file_system, aws_s3


@pytest.fixture(params=[MemorySQLite3, sqlite3])
def db_hook(request):
    hook: DatabaseHook = request.param()
    hook.initialize_storage()
    return hook


@pytest.fixture(params=[file_system, aws_s3])
def file_hook(request):
    hook: FileHook = request.param()
    hook.initialize_storage(True)
    return hook


@pytest.fixture()
def app(db_hook, file_hook):
    from app import create_app

    app = create_app(file_hook, db_hook)

    app.config.update(
        {
            "TESTING": True,
        }
    )

    yield app


@pytest.fixture()
def client(app: Flask):
    return app.test_client()


@pytest.fixture()
def test_tag(db_hook: DatabaseHook):
    tag = Tag(name="1")
    db_hook.create_tag(tag)

    yield tag

    db_hook.delete_objects(tag)


@pytest.fixture()
def test_tags(db_hook: DatabaseHook):
    num_tags = 3
    tags = []
    for i in range(0, num_tags):
        tag = Tag(name=f"{i}")
        tags.append(tag)
        db_hook.create_tag(tag)

    yield tags

    db_hook.delete_objects(*tags)


def test_upload_receipt(
    db_hook: DatabaseHook,
    file_hook: FileHook,
    client: FlaskClient,
    test_tags: List["Tag"],
):
    test_data = None

    with open("./tests/test_image1.png", "rb") as file:
        test_data = file.read()

    form_data = MultiDict()
    form_data.add("file", (io.BytesIO(test_data), "test_image1.png"))
    form_data.add("name", "test")

    for t in test_tags:
        form_data.add("tag", t.id)

    response = client.post(
        "/api/receipt/", data=form_data, content_type="multipart/form-data"
    )

    assert response.status_code == 200
    assert response.json is not None

    j = cast(Any, response.json)

    assert j["name"] == "test"
    assert len(j["tags"]) == 3
    assert j["storage_key"] is not None

    assert test_data == file_hook.fetch(j["storage_key"])
