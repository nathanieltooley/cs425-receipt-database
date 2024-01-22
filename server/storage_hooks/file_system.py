from datetime import datetime, UTC
import os

from configure import CONFIG, DIRS
from storage_hooks import FileHook


DEFAULT_SETTINGS = {"file_path": os.path.normpath(DIRS.user_data_dir + "/receipts")}


class FileSystemHook(FileHook):
    def __init__(self):
        config = CONFIG.get("FileSystem", DEFAULT_SETTINGS.copy())
        self.file_path = os.path.dirname(config["file_path"])
        os.makedirs(self.file_path, exist_ok=True)

    def save(self, image: bytes) -> str:
        # ToDo: Find choose appropriate key, may require more params
        key = datetime.now(UTC).isoformat(timespec="seconds")
        with open(key, "wb+") as file:
            file.write(image)
        return key

    def replace(self, location: str, image: bytes):
        if not os.path.exists(self.file_path + location):
            raise FileNotFoundError(self.file_path + location)
        with open(self.file_path + location, "wb+") as file:
            file.write(image)

    def fetch(self, location: str) -> bytes:
        with open(self.file_path + location, "rb") as file:
            return file.read()

    def delete(self, location: str):
        if not os.path.exists(self.file_path + location):
            raise FileNotFoundError(self.file_path + location)
        os.remove(self.file_path + location)
