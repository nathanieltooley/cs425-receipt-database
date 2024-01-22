import os.path

import platformdirs
from sqlalchemy import create_engine

from configure import CONFIG
from storage_hooks.storage_hooks import DatabaseHook

CONFIG_KEY = "SQLite3"
DIRS = platformdirs.PlatformDirs("Paperless", "Papertrail")
DEFAULT_SETTINGS = {
    "db_path": os.path.normpath(DIRS.user_data_dir + "/receipts.sqlite3"),
}


def init_script():
    """Script to initialize SQLite3 Database."""
    CONFIG[CONFIG_KEY] = DEFAULT_SETTINGS.copy()
    print(CONFIG[CONFIG_KEY])
    CONFIG.save(make_backup=True)
    hook = SQLite3()
    hook.initialize_storage()


class SQLite3(DatabaseHook):
    """Connection to SQLite3"""

    storage_version = "0.2.0"

    def __init__(self):
        super().__init__()
        self.config = CONFIG.get(CONFIG_KEY, DEFAULT_SETTINGS)
        os.makedirs(os.path.dirname(self.config.db_path), exist_ok=True)
        self.engine = create_engine(f"sqlite:///{self.config.db_path}")

    def update_storage(self) -> bool:
        """Migrates a copy of the database to the current scheme version.

        Returns:
            True if successful, False otherwise.
        """
        raise NotImplementedError
