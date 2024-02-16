import argparse
import json
import os

from dataclasses import dataclass, field, asdict
from typing import Literal
from pydantic import TypeAdapter

import platformdirs

from storage_hooks.hook_config_factory import get_meta_hook

CURRENT_VERSION = "0.1.0-1.0"
DIRS = platformdirs.PlatformDirs("Paperless", "Papertrail")


@dataclass
class _StorageHooks:
    file_hook: Literal["FS", "AWS"]
    meta_hook: Literal["SQLite3"]

    @classmethod
    def default(cls) -> "_StorageHooks":
        return _StorageHooks("FS", "SQLite3")


@dataclass
class _SQLite3Config:
    db_path: str

    @classmethod
    def default(cls) -> "_SQLite3Config":
        return _SQLite3Config(
            os.path.normpath(DIRS.user_data_dir + "/receipts.sqlite3")
        )


@dataclass
class _FileSystemConfig:
    file_path: str

    @classmethod
    def default(cls) -> "_FileSystemConfig":
        return _FileSystemConfig(os.path.normpath(DIRS.user_data_dir))


@dataclass
class _Config:
    SQLite3: _SQLite3Config = field(default_factory=_SQLite3Config.default)
    StorageHooks: _StorageHooks = field(default_factory=_StorageHooks.default)
    FileSystem: _FileSystemConfig = field(default_factory=_FileSystemConfig.default)

    DEFAULT_FILE_PATH = os.path.normpath(DIRS.user_config_dir + "/config.json")

    def save(self, path: str):
        with open(path, "w") as file:
            json.dump(asdict(self), file)

    @classmethod
    def from_file(cls, path: str) -> "_Config":
        """Creates a Config object from a JSON file

        The pydantic TypeAdapter class will handle parsing and validation.
        However, this code will throw a ValidationError if the JSON file does not
        follow the schema

        Args:
            path (str): Path to JSON file

        Returns:
            _Config: A valid Config object
        """
        if os.path.exists(path):
            with open(path) as file:
                # Throws ValidationError if it fails
                return TypeAdapter(_Config).validate_python(json.load(file))

        if not os.path.exists(cls.DEFAULT_FILE_PATH):
            default_config = _Config()
            default_config.save(cls.DEFAULT_FILE_PATH)

            return default_config

        return _Config()


# This attempts to load from a config.json file in the cwd, but if one is not found
# it will default to DEFAULT_FILE_PATH
CONFIG = _Config.from_file("config.json")


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser("Receipt Database Configuration")
    subparsers = parser.add_subparsers(dest="cmd")

    # Options for the config file(s)
    file = subparsers.add_parser("file", help="Manage config file(s)")
    file_parsers = file.add_subparsers(dest="file_cmd")
    file_create = file_parsers.add_parser("create", help="Create a default config file")
    file_create.add_argument(
        "--path", default="config.json", help="Path to create config file"
    )
    file_parsers.add_parser("list", help="List the paths checked for config files")

    # Options to initialize (a) hook(s)
    initialize = subparsers.add_parser(
        "initialize", help="Initialize hooks (based on config files)"
    )
    initialize.add_argument("hook", choices=["file", "meta", "both"])
    initialize.add_argument(
        "--clean",
        action="store_true",
        help="Remove most existing data. "
        "This will help ensure proper setup, "
        "but results in loss of previous data.",
    )
    return parser


def main():
    parser = make_parser()
    args = parser.parse_args()
    print(args)
    match args.cmd:
        case "file":
            match args.file_cmd:
                case "create":
                    pass
                case "list":
                    pass
                case _:
                    raise ValueError
        case "initialize":
            if args.hook in {"meta", "both"}:
                get_meta_hook(CONFIG.StorageHooks.meta_hook).initialize_storage()
            if args.hook in {"file", "both"}:
                get_meta_hook(CONFIG.StorageHooks.file_hook).initialize_storage()
        case _:
            raise ValueError


if __name__ == "__main__":
    print(CONFIG)
    main()
