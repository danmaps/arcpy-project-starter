from __future__ import annotations

import logging


def configure_logging(level: str = "INFO") -> logging.Logger:
    normalized = level.upper()
    numeric_level = getattr(logging, normalized, logging.INFO)

    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    return logging.getLogger("arcpy_project")
