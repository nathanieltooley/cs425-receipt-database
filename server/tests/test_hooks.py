import pytest

from storage_hooks.storage_hooks import FileHook
from storage_hooks.file_system import FileSystemHook
from storage_hooks.AWS import AWSS3Hook


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
