import os.path

from sqlalchemy import create_engine

from configure import CONFIG
from storage_hooks.storage_hooks import DatabaseHook


class SQLite3(DatabaseHook):
    """Connection to SQLite3"""

    def __init__(self):
        super().__init__()
        self.config = CONFIG.SQLite3

        os.makedirs(os.path.dirname(self.config.db_path), exist_ok=True)
        self.engine = create_engine(f"sqlite:///{self.config.db_path}")

    def update_storage(self) -> bool:
        """Migrates a copy of the database to the current scheme version.

        Returns:
            True if successful, False otherwise.
        """
        raise NotImplementedError
