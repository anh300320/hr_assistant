from __future__ import annotations

import logging
import logging.config
import sys
from logging.handlers import RotatingFileHandler


_logger = logging.getLogger(__name__)


def init_logging() -> None:
    fmt = "%(levelname)-9.9s %(asctime)s [%(name)s][%(module)s:%(lineno)d] %(message)s"
    date_fmt = "%Y-%m-%d %H:%M:%S"

    file_handler = RotatingFileHandler(
        filename="main.log",
        mode="a",
        maxBytes=1024 * 1024 * 1024 * 2,
        backupCount=10,
    )
    file_handler.setLevel(logging.DEBUG)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)

    logging.basicConfig(
        level=logging.INFO,
        format=fmt,
        datefmt=date_fmt,
        handlers=[file_handler, stream_handler],
    )
    _logger.info("Init logger")
