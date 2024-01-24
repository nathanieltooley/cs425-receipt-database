import argparse
from datetime import datetime
import importlib
import json
import os
from typing import Any

import platformdirs

CURRENT_VERSION = "0.1.0-1.0"
DIRS = platformdirs.PlatformDirs("Paperless", "Papertrail")


# TODO: Add checks for mismatching types and throw errors when possible
def resolve_default_values(
    default_values: dict[str, Any], new_config_values: dict[str, Any]
) -> dict[str, Any]:
    """Recursively add default values to a dict created from a json file

    Args:
        default_values (dict[str, Any]): The default values for the config
        new_config_values (dict[str, Any]): The actual values from the config file

    Returns:
        dict[str, Any]: A completed config dict with defaults add to replace missing values
    """
    return_dict: dict[str, Any] = {}

    # Check every possible config item
    for key in default_values:
        # If the config file set a new value for an item
        if key in new_config_values:
            # And the item is itself a dict
            if isinstance(new_config_values[key], dict):
                # Recursively fill in defaults
                return_dict.update(
                    {
                        key: resolve_default_values(
                            # we don't want the whole dict,
                            # just the values pertaining to this key
                            default_values[key],
                            new_config_values[key],
                        )
                    }
                )
            # Otherwise, use the item from the config file
            else:
                return_dict.update({key: new_config_values[key]})
        # If no new value is set, return the default
        else:
            return_dict.update({key: default_values[key]})

    return return_dict


class _ConfigManager:
    DEFAULT_FILE_PATH = os.path.normpath(DIRS.user_config_dir + "/config.json")
    DEFAULT_VALUES = {
        "SQLite3": {"db_path": ""},
        "StorageHooks": {"hook": "FS"},  # Can be AWS, SQLite, or FS
    }

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return repr(self.__dict__)

    def get(self, key, default=None):
        """Get config section"""
        return self.__dict__.get(key)

    def __getitem__(self, item):
        return self.get(item)

    def set(self, key, value):
        """Set config section"""
        self.__dict__[key] = value

    def __setitem__(self, key, value):
        self.set(key, value)

    @classmethod
    def make_backup(cls):
        if os.path.exists(cls.DEFAULT_FILE_PATH):
            time = datetime.now().astimezone()
            time_str = time.isoformat(timespec="minutes")
            os.rename(cls.DEFAULT_FILE_PATH, f"{cls.DEFAULT_FILE_PATH}.{time_str}.bak")
            print(f"Config file backed up to {cls.DEFAULT_FILE_PATH}.{time_str}.bak")

    def save(self, make_backup=False):
        os.makedirs(os.path.dirname(self.DEFAULT_FILE_PATH), exist_ok=True)
        if make_backup:
            self.make_backup()
        with open(self.DEFAULT_FILE_PATH, "w") as file:
            json.dump(self.__dict__, file, indent=4)
            print(f"Config file saved to {self.DEFAULT_FILE_PATH}")

    def load(self, file_path=None):
        chosen_file_path = self.DEFAULT_FILE_PATH

        if file_path is not None and os.path.exists(file_path):
            chosen_file_path = file_path

        with open(chosen_file_path) as file:
            data = json.load(file)

        self.__dict__.update(
            resolve_default_values(_ConfigManager.DEFAULT_VALUES, data)
        )


CONFIG = _ConfigManager()
CONFIG.load("config.json")


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser("Receipt Database Configuration")
    subparsers = parser.add_subparsers(dest="cmd")

    # Options to initialize a new database
    initialize = subparsers.add_parser("initialize", help="Initialize a new database.")
    initialize.add_argument("service", choices=["SQLite3", "AWS"])

    # Options to migrate services or versions
    migration = subparsers.add_parser(
        "migrate", help="Migrate database to different service or version."
    )
    migration.add_argument("service", choices=["SQLite3", "AWS"])

    return parser


def main():
    parser = make_parser()
    args = parser.parse_args()
    print(args)
    match args.cmd:
        case "initialize":
            module = importlib.import_module(f"storage_hooks.{args.service}")
            print(module)
            module.init_script()
        case "migrate":
            pass
    pass


if __name__ == "__main__":
    print(CONFIG)
    # main()
