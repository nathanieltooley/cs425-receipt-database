import logging


def init_logging(level: int):
    logging.basicConfig(
        format="%(asctime)s:%(module)s - %(levelname)s - %(message)s", level=level
    )
