import argparse


CURRENT_VERSION = "0.1.0-1.0"


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser("Receipt Database Setup")

    # Options to initialize a new database
    initialize = parser.add_subparsers(help="Initialize a new database.").add_parser(
        "initialize"
    )
    initialize.add_argument("service", choices=["SQLite3", "AWS"], required=True)

    # Options to migrate services or versions
    migration = parser.add_subparsers(
        help="Migrate database to different service or version."
    ).add_parser("migrate")
    initialize.add_argument("service", choices=["SQLite3", "AWS"], required=True)

    return parser


def main():
    parser = make_parser()
    args = parser.parse_args()
    pass


if __name__ == "__main__":
    main()
