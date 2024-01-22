import datetime as dt
import json
import os.path

import platformdirs
from sqlalchemy import create_engine

from storage_hooks.storage_hooks import DatabaseHook

DIRS = platformdirs.PlatformDirs("Paperless", "Papertrail")
DEFAULT_SETTINGS = {
    "db_path": os.path.normpath(DIRS.user_data_dir + "/receipts.sqlite3"),
}


def init_script():
    """Script to initialize SQLite3 Database."""
    config = SQLite3Config(try_from_file=False)
    print(config)
    config.save(make_backup=True)
    hook = SQLite3()
    hook.initialize_storage()


class SQLite3Config:
    FILE_PATH = os.path.normpath(DIRS.user_config_dir + "/SQLite3.json")

    def __str__(self):
        return repr(self)

    def __init__(self, try_from_file: bool = True, **kwargs):
        # Set to defaults
        self.db_path = DEFAULT_SETTINGS["db_path"]

        # Update from file
        if try_from_file:
            try:
                self.load()
            except IOError as e:
                pass
                # logger.error(e.message)

        # Update from kwargs
        self.__dict__.update(kwargs)

    @classmethod
    def make_backup(cls):
        if os.path.exists(cls.FILE_PATH):
            time = dt.datetime.now().astimezone()
            time_str = time.isoformat(timespec="minutes")
            os.rename(cls.FILE_PATH, f"{cls.FILE_PATH}.{time_str}.bak")
            print(f"Config file backed up to {cls.FILE_PATH}.{time_str}.bak")

    def save(self, make_backup: False):
        os.makedirs(os.path.dirname(self.FILE_PATH), exist_ok=True)
        if make_backup:
            self.make_backup()
        with open(self.FILE_PATH, "w") as file:
            json.dump(self.__dict__, file, indent=4)
            print(f"Config file saved to {self.FILE_PATH}")

    def load(self):
        with open(self.FILE_PATH) as file:
            data = json.load(file)
        self.__dict__.update(data)


class SQLite3(DatabaseHook):
    """Connection to SQLite3"""

    storage_version = "0.2.0"

    def __init__(self):
        super().__init__()
        self.config = SQLite3Config(try_from_file=True)
        os.makedirs(os.path.dirname(self.config.db_path), exist_ok=True)
        self.engine = create_engine(f'sqlite:///{self.config.db_path}')

    def update_storage(self) -> bool:
        """Migrates a copy of the database to the current scheme version.

        Returns:
            True if successful, False otherwise.
        """
        raise NotImplementedError
