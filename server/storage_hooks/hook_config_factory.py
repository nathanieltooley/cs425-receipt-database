# We may find a better way of doing this that is more scalable
# however we have very few cases to deal with anyway
from storage_hooks.file_system import FileSystemHook
from storage_hooks.SQLite3 import SQLite3
from storage_hooks.AWS import AWSS3Hook
from storage_hooks.storage_hooks import FileHook, DatabaseHook


def get_file_hook(file_hook_str) -> FileHook:
    match file_hook_str:
        case "FS":
            return FileSystemHook()
        case "AWS":
            return AWSS3Hook()


def get_meta_hook(meta_hook_str) -> DatabaseHook:
    match meta_hook_str:
        case "SQLite3":
            return SQLite3()
