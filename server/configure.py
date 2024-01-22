import argparse
from datetime import datetime
import importlib
import json
import os

import platformdirs

CURRENT_VERSION = "0.1.0-1.0"
DIRS = platformdirs.PlatformDirs("Paperless", "Papertrail")


class _ConfigManager:
    FILE_PATH = os.path.normpath(DIRS.user_config_dir + "/config.json")

    def __init__(self):
        self.data = {}

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return repr(self.data)

    def get(self, key, default=None):
        """Get config section"""
        return self.data.get(key, default)

    def __getitem__(self, item):
        return self.get(item)

    def set(self, key, value):
        """Set config section"""
        self.data[key] = value

    def __setitem__(self, key, value):
        self.set(key, value)

    @classmethod
    def make_backup(cls):
        if os.path.exists(cls.FILE_PATH):
            time = datetime.now().astimezone()
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


CONFIG = _ConfigManager()


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
    main()
