import argparse
import importlib


CURRENT_VERSION = "0.1.0-1.0"


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
