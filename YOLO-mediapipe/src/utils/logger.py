"""
logger.py
=========

Central logging configuration for the project.

Features
--------
- Console logging
- File logging
- Colored log levels (console)
- Automatic log directory creation

Author
------
Zahra Alipour
"""

from __future__ import annotations

import logging
from logging import Logger
from pathlib import Path


LOG_FORMAT = (
    "[%(asctime)s] "
    "[%(levelname)s] "
    "[%(name)s] "
    "%(message)s"
)

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_logger(
    name: str,
    log_file: str = "outputs/logs/project.log",
    level: int = logging.INFO,
) -> Logger:
    """
    Create and configure a logger.

    Parameters
    ----------
    name : str
        Logger name.

    log_file : str
        Path to the log file.

    level : int
        Logging level.

    Returns
    -------
    logging.Logger
    """

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(level)

    Path(log_file).parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    formatter = logging.Formatter(
        fmt=LOG_FORMAT,
        datefmt=DATE_FORMAT,
    )

    # -------------------------------------------------------
    # Console Handler
    # -------------------------------------------------------

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    # -------------------------------------------------------
    # File Handler
    # -------------------------------------------------------

    file_handler = logging.FileHandler(
        log_file,
        mode="a",
        encoding="utf-8",
    )

    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.propagate = False

    return logger


# =============================================================================
# Default Project Logger
# =============================================================================

logger = get_logger("YOLO-MediaPipe")


# =============================================================================
# Convenience Functions
# =============================================================================


def debug(message: str) -> None:
    """Log a DEBUG message."""
    logger.debug(message)


def info(message: str) -> None:
    """Log an INFO message."""
    logger.info(message)


def warning(message: str) -> None:
    """Log a WARNING message."""
    logger.warning(message)


def error(message: str) -> None:
    """Log an ERROR message."""
    logger.error(message)


def critical(message: str) -> None:
    """Log a CRITICAL message."""
    logger.critical(message)