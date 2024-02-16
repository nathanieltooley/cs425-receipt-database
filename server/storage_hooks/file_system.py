import os

from configure import CONFIG
from storage_hooks.storage_hooks import FileHook


class FileSystemHook(FileHook):
    def __init__(self):
        config = CONFIG.FileSystem
        self.file_path = config.file_path

    def save(self, image: bytes, original_name: str) -> str:
        key = self._make_key(original_name)
        with open(os.path.join(self.file_path, key), "wb+") as file:
            file.write(image)
        return key

    def replace(self, location: str, image: bytes):
        r_path = os.path.join(self.file_path, location)

        if not os.path.exists(r_path):
            raise FileNotFoundError(r_path)
        with open(r_path, "wb+") as file:
            file.write(image)

    def fetch(self, location: str) -> bytes:
        with open(os.path.join(self.file_path, location), "rb") as file:
            return file.read()

    def delete(self, location: str):
        r_path = os.path.join(self.file_path, location)

        if not os.path.exists(r_path):
            raise FileNotFoundError(r_path)
        os.remove(r_path)

    def initialize_storage(self):
        os.makedirs(self.file_path, exist_ok=True)
