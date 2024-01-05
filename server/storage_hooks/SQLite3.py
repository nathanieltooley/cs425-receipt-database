import contextlib
import datetime as dt
import json
import os.path
import sqlite3

import platformdirs

from receipt import Receipt
from storage_hooks.storage_hooks import StorageHook, Sort

DIRS = platformdirs.PlatformDirs("Paperless", "Papertrail")
DEFAULT_SETTINGS = {
    "db_path": os.path.normpath(DIRS.user_data_dir + "/receipts.sqlite3"),
    "image_dir": DIRS.user_data_dir,
    "table_receipts": "Receipt",
    "table_images": "Image",
    "table_items": "Item",
    "table_tags": "Tags",
    "table_receipt_tags": "ReceiptTags"
}


def init_script():
    """Script to initialize SQLite3 Database."""
    config = SQLite3Config(try_from_file=False)
    print(config)
    config.save(make_backup=True)
    hook = SQLite3()
    hook.initialize_storage()


# def init_script():
#     """Script to initialize SQLite3 Database."""
#     db_location, img_location = '', ''
#     while True:
#         db_location = input("Location for SQLite file: ")
#         if os.path.isdir(db_location):
#             print(f'{db_location} is a directory, adjusting path to a file')
#             db_location += r'/receipts.db'
#         db_location = os.path.abspath(db_location)
#         print(f'Selected Path: {db_location}')
#         if os.path.exists(db_location):
#             print(f'{db_location} exists')
#             with sqlite3.connect(db_location) as con, con.cursor() as cursor:
#                 try:
#                     cursor.execute("PRAGMA integrity_check").fetchone()
#                 except sqlite3.DatabaseError:
#                     valid_existing = False
#                 else:
#                     valid_existing = True
#             if valid_existing:
#                 if not y_n_prompt(f'{db_location} is a valid SQLite3 Database, use this file?'):
#                     continue
#             else:
#                 if not y_n_prompt(f'{db_location} exists, overwrite this file?', False):
#                     continue
#         else:
#             if not y_n_prompt(f'Use {db_location}?', True):
#                 continue
#         if not path_is_writeable(db_location):
#             print(f'Missing Write Access to {db_location}')
#             continue
#
#     while True:
#         img_location = input('Location for Image Files: ')
#
#         if os.path.isfile(img_location):
#             print(f'{img_location} is a file, please select a directory.')
#             continue
#         img_location = os.path.abspath(img_location)
#         print(f'Selected Path: {img_location}')
#         if os.path.exists(img_location) and len(os.listdir(img_location)) != 0:
#             if not y_n_prompt(f'{img_location} is not empty, use anyways?', False):
#                 continue
#         else:
#             if not y_n_prompt(f'Use {img_location}?', True):
#                 continue
#         if not path_is_writeable(img_location):
#             print(f'Missing Write Access to {img_location}')
#             continue
#
#     hook.initialize_storage()


def get_sort_meaning(sort: Sort | None) -> str:
    order_by = "ORDER BY"
    ascending = "ASC"
    descending = "DESC"
    match sort:
        case None:
            return ""
        case Sort.newest:
            return f"{order_by} ph_key {descending}"
        case Sort.oldest:
            return f"{order_by} ph_key {ascending}"
        case _:
            raise ValueError


class SQLite3Config:
    FILE_PATH = os.path.normpath(DIRS.user_config_dir + "/SQLite3.json")

    def __str__(self):
        return repr(self)

    def __init__(self, try_from_file: bool = True, **kwargs):
        # Set to defaults
        self.db_path = DEFAULT_SETTINGS["db_path"]
        self.image_dir = DEFAULT_SETTINGS["image_dir"]
        self.table_receipts = DEFAULT_SETTINGS["table_receipts"]
        self.table_images = DEFAULT_SETTINGS["table_images"]
        self.table_items = DEFAULT_SETTINGS["table_items"]
        self.table_tags = DEFAULT_SETTINGS["table_tags"]
        self.table_receipt_tags = DEFAULT_SETTINGS["table_receipt_tags"]

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


class SQLite3(StorageHook):
    """Connection to SQLite3"""

    def __init__(self):
        super().__init__()
        self.config = SQLite3Config(try_from_file=True)
        os.makedirs(os.path.dirname(self.config.db_path), exist_ok=True)
        self.connection = sqlite3.connect(self.config.db_path)

    def __del__(self):
        self.close()

    def close(self):
        self.connection.close()

    @contextlib.contextmanager
    def cursor(self):
        cursor = self.connection.cursor()
        try:
            yield cursor
            cursor.connection.commit()
        finally:
            cursor.close()

    def upload_receipt(self, receipt: Receipt) -> bool:
        self.connection.execute(
            f"INSERT OR REPLACE INTO {self.config.table_receipts} (ph_key, ph_body) "
            f"VALUES (?, ?)",
            [receipt.ph_key, receipt.ph_body],
        ).close()  # Closes the implicit cursor
        self.connection.commit()
        return True

    def fetch_receipt(self, identifier) -> Receipt:
        with self.cursor() as cursor:
            cursor.execute(
                f"SELECT ph_body FROM {self.config.table_receipts} WHERE ph_key == ?",
                [identifier],
            )
            return Receipt(identifier, *cursor.fetchone())

    def fetch_receipts(
        self, limit: int = None, sort: Sort = Sort.newest
    ) -> list[Receipt]:
        receipts = []
        with self.cursor() as cursor:
            if limit:
                cursor.execute(
                    f"SELECT ph_key, ph_body FROM {self.config.table_receipts} "
                    f"{get_sort_meaning(sort)} LIMIT ?",
                    [limit],
                )
            else:
                cursor.execute(
                    f"SELECT ph_key, ph_body FROM {self.config.table_receipts} "
                    f"{get_sort_meaning(sort)}"
                )
            for row in cursor:
                receipts.append(Receipt(*row))
        return receipts

    def fetch_receipts_between(
        self,
        after: dt.datetime,
        before: dt.datetime,
        limit: int = None,
        sort: Sort = Sort.newest,
    ) -> list[Receipt]:
        pass

    def edit_receipt(self, receipt: Receipt) -> bool:
        return self.upload_receipt(receipt)

    def delete_receipt(self, receipt) -> bool:
        with self.cursor() as cursor:
            cursor.execute(
                f"DELETE FROM {self.config.table_receipts} WHERE ph_key == ?"
            )
        return True

    @property
    def storage_version(self) -> str:
        """Return scheme version the database is using."""
        return "0.1.0"

    def initialize_storage(self):
        """Initialize storage / database with current scheme."""
        if os.path.exists(self.config.db_path):
            time = dt.datetime.now().astimezone()
            time_str = time.isoformat(timespec="minutes")
            os.rename(self.config.db_path, f"{self.config.db_path}.{time_str}.bak")
            print(f"DB file backed up to {self.config.db_path}.{time_str}.bak")
            self.connection = sqlite3.connect(self.config.db_path)

        with self.cursor() as cursor:
            cursor.execute(f"DROP TABLE IF EXISTS {self.config.table_receipts}")
            # self.connection.execute('DROP TABLE ?', self.config.table_images)
            # self.connection.execute('DROP TABLE ?', self.config.table_items)
            print("Dropped Tables")
            cursor.execute(
                f"CREATE TABLE {self.config.table_receipts} ("
                "   ph_key TEXT PRIMARY KEY,"
                "   ph_body BLOB NOT NULL"
                ")"
            )
            print("Created Tables")

    def update_storage(self) -> bool:
        """Migrates a copy of the database to the current scheme version.

        Returns:
            True if successful, False otherwise.
        """
        return True
