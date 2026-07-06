"""
Business objective:
Provide readable execution events for debugging SEO automations during incidents.

Coding objective:
Use standard-library logging so the project has no runtime dependency burden.
"""

from __future__ import annotations

import logging


def get_logger(name: str = "seo_incident_copilot") -> logging.Logger:
    """Return a configured project logger."""

    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
