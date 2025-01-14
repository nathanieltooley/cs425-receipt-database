import io
from typing import Any, List, cast

import pytest
from flask import Flask
from flask.testing import FlaskClient
from werkzeug.datastructures import MultiDict

from receipt import Receipt, Tag
from storage_hooks.storage_hooks import DatabaseHook, FileHook
from temp_hooks import MemorySQLite3, aws_s3, file_system, sqlite3


@pytest.fixture(params=[MemorySQLite3, sqlite3])
def db_hook(request):
    hook: DatabaseHook = request.param()
    hook.initialize_storage()
    yield hook


@pytest.fixture(params=[file_system, aws_s3])
def file_hook(request):
    hook: FileHook = request.param()
    hook.initialize_storage(True)
    yield hook


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
def receipt_tag_db(tags_db: List[Tag], db_hook: DatabaseHook, file_hook: FileHook):
    with open("./tests/test_image1.png", "rb") as file:
        r_image = file.read()

    receipt = Receipt()
    receipt.name = "Test"
    receipt.tags = tags_db

    storage_key = file_hook.save(r_image, receipt.name)

    receipt.storage_key = storage_key

    receipt = db_hook.create_receipt(receipt)

    yield receipt

    db_hook.delete_receipt(receipt.id)


@pytest.fixture()
def tag():
    tag = Tag(name="1")
    return tag


@pytest.fixture()
def tag_db(db_hook: DatabaseHook):
    tag = Tag(name="test_tag_1")
    db_hook.create_tag(tag)

    yield tag

    db_hook.delete_objects(tag)


@pytest.fixture()
def tags():
    num_tags = 3
    tags = []
    for i in range(0, num_tags):
        tag = Tag(name=f"Test{i}")
        tags.append(tag)

    return tags


@pytest.fixture()
def tags_db(db_hook: DatabaseHook):
    num_tags = 3
    tags = []
    for i in range(0, num_tags):
        tag = Tag(name=f"Test{i}")
        tags.append(tag)
        db_hook.create_tag(tag)

    yield tags

    db_hook.delete_objects(*tags)


def test_upload_receipt(
    db_hook: DatabaseHook,
    file_hook: FileHook,
    client: FlaskClient,
    tags_db: List["Tag"],
):
    with open("./tests/test_image1.png", "rb") as file:
        test_data = file.read()

    form_data = MultiDict()
    form_data.add("file", (io.BytesIO(test_data), "test_image1.png"))
    form_data.add("name", "test")

    for t in tags_db:
        form_data.add("tag", t.id)

    response = client.post(
        "/api/receipt/", data=form_data, content_type="multipart/form-data"
    )

    assert response.status_code == 200
    assert response.json is not None

    j = cast(Any, response.json)

    storage_key = j["storage_key"]
    _id = int(j["id"])

    assert j["name"] == "test"
    assert len(j["tags"]) == 3
    assert storage_key is not None
    assert _id is not None

    db_data = db_hook.fetch_receipt(_id)

    assert db_data is not None
    assert db_data.name == "test"
    assert len(db_data.tags) == 3
    assert db_data.storage_key == storage_key

    assert test_data == file_hook.fetch(storage_key)

    db_hook.delete_receipt(_id)
    file_hook.delete(storage_key)


def test_view_receipt(
    receipt_tag_db: Receipt,
    file_hook: FileHook,
    client: FlaskClient,
):
    response = client.get(f"/api/receipt/{receipt_tag_db.id}/image")

    print(response)

    assert response.get_data(False) == file_hook.fetch(receipt_tag_db.storage_key)
    assert response.headers["Upload-Date"] == str(receipt_tag_db.upload_dt)


# TODO: Test updating the receipt image data through update_receipt()
def test_update_receipt(
    receipt_tag_db: Receipt,
    client: FlaskClient,
):
    tag_id = 3

    form = MultiDict()
    form.add("name", "new")
    form.add("remove tag", tag_id)

    response = client.put(
        f"/api/receipt/{receipt_tag_db.id}",
        data=form,
        content_type="multipart/form-data",
    )

    j = cast(Any, response.json)

    assert j["name"] == "new"
    assert len(j["tags"]) == 2
    assert j["tags"] == [1, 2]

    form = MultiDict()
    form.add("add tag", tag_id)

    response = client.put(
        f"/api/receipt/{receipt_tag_db.id}",
        data=form,
        content_type="multipart/form-data",
    )

    j = cast(Any, response.json)

    assert j["name"] == "new"
    assert len(j["tags"]) == 3
    assert j["tags"] == [1, 2, 3]


def test_fetch_receipt(
    receipt_tag_db: Receipt,
    client: FlaskClient,
):
    response = client.get(f"/api/receipt/{receipt_tag_db.id}/")

    assert response.json == receipt_tag_db.export()


def test_fetch_receipt_keys(
    tags_db: List[Tag], db_hook: DatabaseHook, file_hook: FileHook, client: FlaskClient
):
    with open("./tests/test_image1.png", "rb") as f:
        test_image_data = f.read()

    receipt1 = Receipt()
    receipt1.name = "Test1"
    receipt1.tags = tags_db
    receipt1.storage_key = file_hook.save(test_image_data, receipt1.name)
    receipt1 = db_hook.create_receipt(receipt1)

    receipt2 = Receipt()
    receipt2.name = "Test2"
    receipt2.tags = tags_db
    receipt2.storage_key = file_hook.save(test_image_data, receipt2.name)
    receipt2 = db_hook.create_receipt(receipt2)

    receipt3 = Receipt()
    receipt3.name = "Test3"
    receipt3.tags = tags_db
    receipt3.storage_key = file_hook.save(test_image_data, receipt3.name)
    receipt3 = db_hook.create_receipt(receipt3)

    response = client.get("/api/receipt/")

    j = cast(Any, response.json)
    tag_ids = [1, 2, 3]

    assert j is not None

    assert len(j) == 3
    assert j[0]["name"] == "Test1"
    assert j[0]["tags"] == tag_ids
    assert j[0]["storage_key"] == receipt1.storage_key
    assert j[1]["name"] == "Test2"
    assert j[1]["tags"] == tag_ids
    assert j[1]["storage_key"] == receipt2.storage_key
    assert j[2]["name"] == "Test3"
    assert j[2]["tags"] == tag_ids
    assert j[2]["storage_key"] == receipt3.storage_key


def test_delete_receipt(
    receipt_tag_db: Receipt,
    db_hook: DatabaseHook,
    client: FlaskClient,
):
    id_ = receipt_tag_db.id
    response = client.delete(f"/api/receipt/{receipt_tag_db.id}")

    assert response.status_code == 204
    assert db_hook.fetch_receipt(id_) is None


def test_delete_receipt_none(
    receipt_tag_db: Receipt,
    client: FlaskClient,
):
    response = client.delete("/api/receipt/100")

    assert response.status_code == 404


def test_upload_tag(db_hook: DatabaseHook, client: FlaskClient):
    tag_name = "test_tag"
    response = client.post(
        "/api/tag/", data={"name": tag_name}, content_type="multipart/form-data"
    )

    tag_id = int(response.data)

    tag = db_hook.fetch_tag(tag_id)

    assert tag is not None
    assert tag_name == tag.name


def test_fetch_tag(tag_db: Tag, client: FlaskClient):
    response = client.get(f"/api/tag/{tag_db.id}")

    j = cast(Any, response.json)
    assert j["name"] == tag_db.name
    assert j["id"] == tag_db.id


def test_fetch_tags(tags_db: List[Tag], client: FlaskClient):
    response = client.get("/api/tag/")

    j = cast(Any, response.json)
    j = sorted(j, key=lambda x: x["name"])

    assert len(j) == 3
    assert j[0]["name"] == "Test0"
    assert j[0]["id"] == 1
    assert j[1]["name"] == "Test1"
    assert j[1]["id"] == 2
    assert j[2]["name"] == "Test2"
    assert j[2]["id"] == 3


def test_update_tag(tag_db: Tag, client: FlaskClient):
    response = client.put(
        f"/api/tag/{tag_db.id}/",
        data={"name": "new_name"},
        content_type="multipart/form-data",
    )

    j = cast(Any, response.json)

    assert j["id"] == tag_db.id
    assert j["name"] == "new_name"


def test_delete_tag(tags_db: List[Tag], db_hook: DatabaseHook, client: FlaskClient):
    response = client.delete("/api/tag/3")

    assert response.status_code == 204
    assert db_hook.fetch_tag(1) is not None
    assert db_hook.fetch_tag(2) is not None
    assert db_hook.fetch_tag(3) is None
