import logging
from typing import Optional


def configure_logging(verbosity: int = 1) -> None:
    """Configure root logging according to verbosity level.

    verbosity: 0 = warnings+ only, 1 = info, 2 = debug
    """
    level = logging.INFO
    if verbosity <= 0:
        level = logging.WARNING
    elif verbosity >= 2:
        level = logging.DEBUG

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def get_logger(name: Optional[str] = None) -> logging.Logger:
    return logging.getLogger(name if name else __name__)


