"""
utils/logger.py  —  Logger centralizado.
"""

import logging
from config.settings import LOG_FILE

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
)
_logger = logging.getLogger("drud")


def log(action: str, detail: str, level: str = "info"):
    getattr(_logger, level.lower(), _logger.info)(f"[{action}] {detail}")
