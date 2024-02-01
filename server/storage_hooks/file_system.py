from datetime import datetime, timezone
import os

from configure import CONFIG
from storage_hooks.storage_hooks import FileHook

UTC = timezone.utc


class FileSystemHook(FileHook):
    def __init__(self):
        config = CONFIG.FileSystem
        self.file_path = config.file_path
        os.makedirs(self.file_path, exist_ok=True)

    def save(self, image: bytes) -> str:
        # ToDo: Find choose appropriate key, may require more params
        key = datetime.now(UTC).isoformat(timespec="seconds")
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
