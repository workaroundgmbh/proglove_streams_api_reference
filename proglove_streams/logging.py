"""Logging abstraction to facade systemd journal."""
import logging
import sys

from colorlog import ColoredFormatter

FORMATTER = ColoredFormatter(
    "[%(asctime)s]" + " %(log_color)s%(message)s%(reset)s", datefmt="%H:%M:%S"
)


def init_logging(logging_level: int = logging.DEBUG) -> None:
    """Initialize the logging."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(FORMATTER)
    handler.setLevel(logging_level)

    logger = logging.getLogger()
    logger.setLevel(logging_level)
    logger.addHandler(handler)
