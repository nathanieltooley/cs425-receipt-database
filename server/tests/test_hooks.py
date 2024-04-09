import warnings

import pytest

from receipt import Receipt, Tag
from storage_hooks.AWS import AWSS3Hook
from storage_hooks.RemoteSQL import RemoteSQL, RemoteSQLConfig
from storage_hooks.SQLite3 import SQLite3
from storage_hooks.file_system import FileSystemHook
from storage_hooks.storage_hooks import DatabaseHook, FileHook
from temp_hooks import aws_s3, file_system, sqlite3


class TestDatabaseHook:
    @pytest.fixture()
    def sqlite3_hook(self) -> SQLite3:
        return SQLite3()

    @pytest.fixture(params=[sqlite3])
    def hook(self, request) -> DatabaseHook:
        hook: DatabaseHook = request.param()
        hook.initialize_storage()
        return hook

    @pytest.fixture
    def tag(self, hook) -> Tag:
        tag = Tag(name="test_tag")
        hook.create_tag(tag)
        yield tag
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            hook.delete_objects(tag)

    @pytest.fixture(params=[i for i in range(4)])
    def tags(self, request, hook) -> list[Tag]:
        tags = []
        for i in range(request.param):
            tags.append(Tag(name=f"t{i}"))
            hook.create_tag(tags[-1])
        yield tags
        hook.delete_objects(*tags)

    @pytest.fixture
    def tag_ids(self, tags) -> list[int]:
        return [t.id for t in tags]

    @pytest.fixture
    def tag_less_receipt(self, hook) -> Receipt:
        receipt = Receipt(storage_key="where?", tags=[])
        receipt = hook.create_receipt(receipt)
        yield receipt
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            hook.delete_objects(receipt)

    @pytest.fixture
    def receipt(self, hook, tags) -> Receipt:
        receipt = Receipt(storage_key="where?", tags=tags)
        receipt = hook.create_receipt(receipt)
        yield receipt
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            hook.delete_objects(receipt)

    def test_fetch_receipt(self, hook, receipt):
        fetched = hook.fetch_receipt(receipt.id)
        assert fetched is not receipt
        assert fetched.id == receipt.id
        assert fetched.storage_key == receipt.storage_key
        assert fetched.upload_dt == receipt.upload_dt

        # fetched.tags and receipts.tags aren't loaded...
        # assert len(fetched.tags) == len(receipt.tags)
        # assert all(t in fetched.tags for t in receipt.tags)
        # ToDo: Validate that all tags match

    # fetch_receipts

    def test_update_receipt(self, hook, tag_less_receipt, tags):
        receipt = tag_less_receipt
        tag_ids = [tag.id for tag in tags]
        hook.update_receipt(receipt.id, name="New Name")
        assert hook.fetch_receipt(receipt.id).name == "New Name"

        hook.update_receipt(receipt.id, set_tags=tag_ids)
        assert hook.fetch_receipt(receipt.id).tags == tags

        if len(tags) != 0:
            hook.update_receipt(receipt.id, remove_tags=[tag_ids[0]])
            f_tags = hook.fetch_receipt(receipt.id).tags
            assert len(f_tags) == len(tags[1:])
            for tag in tags[1:]:
                assert tag in f_tags

            hook.update_receipt(receipt.id, add_tags=[tag_ids[0]])
            f_tags = hook.fetch_receipt(receipt.id).tags
            assert len(f_tags) == len(tags)
            for tag in tags:
                assert tag in f_tags

    def test_delete_receipt(self, hook, receipt):
        hook.delete_receipt(receipt.id)
        assert hook.fetch_receipt(receipt.id) is None

    def test_fetch_tag(self, hook, tag):
        assert hook.fetch_tag(tag.id) == tag

    def test_fetch_tags(self, hook, tags):
        fetched = hook.fetch_tags([t.id for t in tags])
        assert len(fetched) == len(tags)
        for tag in fetched:
            assert tag in tags

    def test_update_tag(self, hook, tag):
        tag.name = "new name"
        assert hook.update_tag(tag).export() == tag.export()

    def test_delete_tag(self, hook, tag):
        hook.delete_tag(tag.id)
        assert hook.fetch_tag(tag.id) is None

    def test_build_url(self):
        def build_url(*args, **kwargs) -> str:
            return str(RemoteSQL.build_url(RemoteSQLConfig(*args, **kwargs)))

        assert build_url("sqlite", *([None] * 6)) == "sqlite://"
        assert build_url("sqlite", *([None] * 5), "/dev/null") == "sqlite:////dev/null"
        assert build_url(
            dialect="postgresql",
            driver="pg8000",
            username="dbuser",
            password="kx@jj5/g",
            host="pghost10",
            port=None,
            database="appdb",
        ) in (
            "postgresql+pg8000://dbuser:kx%40jj5%2Fg@pghost10/appdb",  # Manual
            "postgresql+pg8000://dbuser:***@pghost10/appdb",  # Via SQLAlchemy
        )


class TestFileHook:
    """Base class for hooks that store image files."""

    @pytest.fixture
    def aws_s3_hook(self) -> AWSS3Hook:
        return AWSS3Hook()

    @pytest.fixture
    def file_system_hook(self) -> FileSystemHook:
        return FileSystemHook()

    @pytest.fixture(params=[file_system, aws_s3])
    def hook(self, request) -> FileHook:
        return request.param()

    @pytest.fixture
    def save_file(self, hook) -> tuple[str, bytes]:
        file_name = "test_image1.png"
        with open("tests/" + file_name, "br") as test_image:
            test_bytes = test_image.read()
        save_key = hook.save(test_bytes, file_name)

        yield save_key, test_bytes

        try:
            hook.delete(save_key)
        except FileNotFoundError:
            pass

    def test_read(self, hook: FileHook, save_file):
        save_key, test_bytes = save_file
        assert test_bytes == hook.fetch(save_key)

    def test_replace(self, hook: FileHook, save_file):
        save_key, old_bytes = save_file
        file_name = "test_image2.png"
        with open("tests/" + file_name, "br") as test_image:
            test_bytes = test_image.read()
            assert test_bytes != old_bytes

        hook.replace(save_key, test_bytes)
        fetched_bytes = hook.fetch(save_key)
        assert test_bytes == fetched_bytes
        assert old_bytes != fetched_bytes

    def test_delete(self, hook: FileHook, save_file):
        save_key, test_bytes = save_file
        hook.delete(save_key)
        with pytest.raises(FileNotFoundError):
            hook.fetch(save_key)
        with pytest.raises(FileNotFoundError):
            hook.replace(save_key, test_bytes)
        with pytest.raises(FileNotFoundError):
            hook.delete(save_key)
