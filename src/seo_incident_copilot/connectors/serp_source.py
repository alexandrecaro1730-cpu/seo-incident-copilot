"""
Business objective:
Load SERP snapshots so the system can compare whether Google changed the type of
content it prefers for a query.

Coding objective:
Keep SERP access behind a small connector function. Production code can replace
JSON fixtures with live SERP API calls without touching detectors.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_serp(data_dir: Path, relative_file: str) -> dict[str, Any]:
    """Load a SERP snapshot from a path relative to the data directory."""

    return json.loads((data_dir / relative_file).read_text(encoding="utf-8"))
