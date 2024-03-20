import os

from sqlalchemy import create_engine

from configure import CONFIG, DIRS
from storage_hooks.AWS import AWSS3Hook
from storage_hooks.SQLite3 import SQLite3
from storage_hooks.file_system import FileSystemHook
from storage_hooks.storage_hooks import DatabaseHook


class MemorySQLite3(DatabaseHook):
    """Like sqlite3 but in raw memory rather a memory only file."""

    def __init__(self):
        super().__init__()
        self.engine = create_engine("sqlite://")
        self.engine.echo = True


def sqlite3() -> SQLite3:
    """Make a SQLite3 db stored in the runtime dir a.k.a. temp."""
    runtime_dir = DIRS.user_runtime_dir
    filename = "test_receipts.sqlite3"
    CONFIG.SQLite3.db_path = os.path.join(runtime_dir, filename)
    return SQLite3()


def file_system() -> FileSystemHook:
    """Use a filesystem location at a runtime dir a.k.a. temp."""
    CONFIG.FileSystem.file_path = DIRS.user_runtime_dir
    return FileSystemHook()


def aws_s3() -> AWSS3Hook:
    """Use a specific (possibly different) bucket for testing."""
    hook = AWSS3Hook()
    hook.bucket_name = "cs425-3-test-bucket2"
    return hook
