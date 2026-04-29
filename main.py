"""Entry point for the Classic Clock application."""

import logging
import os
import sys

# Ensure the clock_app directory is on the Python path so that
# 'src.*' imports resolve correctly when running from the project root.
_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from src.utils.constants import LOG_FORMAT, LOG_DATE_FORMAT, LOG_LEVEL
from src.app import App


def _configure_logging() -> None:
    """Set up root logger with console output."""
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL, logging.DEBUG),
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT,
    )


def main() -> None:
    """Instantiate and run the clock application."""
    _configure_logging()
    app = App()
    app.run()


if __name__ == "__main__":
    main()
