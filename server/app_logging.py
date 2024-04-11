import logging
import os
import sys
import time
from logging.handlers import RotatingFileHandler

from configure import DIRS

LOG_NAME = "receipt_database"
LOGGER = log = logging.getLogger(LOG_NAME)
# Allow accessing log levels from this module instead of logging
CRITICAL, ERROR, WARNING, INFO, DEBUG = (
    logging.CRITICAL,
    logging.ERROR,
    logging.WARNING,
    logging.INFO,
    logging.DEBUG,
)


def init_logging(
    to_stdout: bool = True,
    local_level: int = logging.INFO,
    root_level: int = logging.WARNING,
):
    logging.Formatter.converter = time.gmtime  # Set logs to UTC

    root_logger = logging.getLogger()  # Logger for whole process
    local_logger = logging.getLogger(LOG_NAME)  # Logger for our app, excluding libs

    log_dir = DIRS.user_log_dir
    os.makedirs(log_dir, exist_ok=True)

    root_error_handler = RotatingFileHandler(  # Logs all warning level
        f"{log_dir}/{LOG_NAME}_notable_root.log",
        maxBytes=524288,
        backupCount=3,
    )
    local_error_handler = RotatingFileHandler(  # Logs local warning level
        f"{log_dir}/{LOG_NAME}_notable_local.log",
        maxBytes=524288,
        backupCount=3,
    )
    standard_log_handler = RotatingFileHandler(  # Logs local info or debug level
        f"{log_dir}/{LOG_NAME}_standard.log",
        maxBytes=524288,
        backupCount=3,
    )
    console_handler = logging.StreamHandler(sys.stdout)  # Logs to console

    formatter = logging.Formatter(
        "%(asctime)s:%(module)s - %(levelname)s - %(message)s"
    )

    root_error_handler.setFormatter(formatter)
    local_error_handler.setFormatter(formatter)
    standard_log_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    root_error_handler.setLevel(logging.WARNING)
    local_error_handler.setLevel(logging.WARNING)

    root_logger.setLevel(root_level)
    local_logger.setLevel(local_level)

    root_logger.addHandler(root_error_handler)
    local_logger.addHandler(local_error_handler)
    local_logger.addHandler(standard_log_handler)
    if to_stdout:
        local_logger.addHandler(console_handler)
