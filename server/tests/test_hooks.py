import pytest

from receipt import Receipt, Tag
from storage_hooks.storage_hooks import DatabaseHook, FileHook
from storage_hooks.file_system import FileSystemHook
from storage_hooks.AWS import AWSS3Hook
from storage_hooks.SQLite3 import SQLite3


class TestDatabaseHook:
    @pytest.fixture()
    def sqlite3_hook(self) -> SQLite3:
        return SQLite3()

    @pytest.fixture(params=[SQLite3])
    def hook(self, request) -> DatabaseHook:
        hook: DatabaseHook = request.param()
        hook.initialize_storage()
        return hook

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
    def receipt(self, hook, tags) -> tuple[int, Receipt]:
        receipt = Receipt(storage_key="where?", tags=tags)
        yield hook.create_receipt(receipt), receipt
        hook.delete_objects(receipt)

    def test_fetch_receipt(self, hook, receipt):
        r_id, receipt = receipt
        fetched = hook.fetch_receipt(r_id)
        assert fetched is not receipt
        assert fetched.id == r_id
        assert fetched.storage_key == receipt.storage_key
        assert fetched.upload_dt == receipt.upload_dt

        # fetched.tags and receipts.tags aren't loaded...
        # assert len(fetched.tags) == len(receipt.tags)
        # ToDo: Validate that all tags match

    # fetch_receipts

    # def test_update_receipt(self, receipt, tags):
    #     return NotImplemented

    def test_delete_receipt(self, hook, receipt):
        r_id, receipt = receipt
        assert hook.delete_receipt(r_id) == receipt.storage_key
        assert hook.fetch_receipt(r_id) is None

    # create_tag
    # fetch_tag
    # fetch_tags
    # update_tag
    # delete_tag


class TestFileHook:
    """Base class for hooks that store image files."""

    @pytest.fixture
    def aws_s3_hook(self) -> AWSS3Hook:
        return AWSS3Hook()

    @pytest.fixture
    def file_system_hook(self) -> FileSystemHook:
        return FileSystemHook()

    @pytest.fixture(params=[FileSystemHook])
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
