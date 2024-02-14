import pytest

from storage_hooks.storage_hooks import FileHook
from storage_hooks.file_system import FileSystemHook
from storage_hooks.AWS import AWSS3Hook


class TestFileHook:
    """Base class for hooks that store image files."""

    @pytest.fixture()
    def aws_s3_hook(self) -> AWSS3Hook:
        yield AWSS3Hook()

    @pytest.fixture()
    def file_system_hook(self) -> FileSystemHook:
        return FileSystemHook()

    @pytest.fixture(params=[FileSystemHook])
    def hook(self, request) -> FileHook:
        return request.param()

    def test_file_hook(self, hook: FileHook):
        # Save and Read
        file_name = "test_image1.png"
        with open("tests/" + file_name, "br") as test_image:
            test_bytes = test_image.read()
        save_key = hook.save(test_bytes, file_name)
        assert test_bytes == hook.fetch(save_key)

        # Replace
        file_name = "test_image2.png"
        with open("tests/" + file_name, "br") as test_image:
            test_bytes = test_image.read()
        hook.replace(save_key, test_bytes)
        assert test_bytes == hook.fetch(save_key)

        # Delete
        hook.delete(save_key)
        with pytest.raises(FileNotFoundError):
            hook.fetch(save_key)
        with pytest.raises(FileNotFoundError):
            hook.replace(save_key, test_bytes)
        with pytest.raises(FileNotFoundError):
            hook.delete(save_key)
