"""
Business objective:
Create an audit trail of SEO incidents and AI recommendations for client review,
postmortems, and continuous improvement.

Coding objective:
Write one JSON object per line so the storage format is append-only, simple, and
warehouse-friendly.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def append_incident(outputs_dir: Path, incident: dict[str, Any]) -> Path:
    """Append an incident to a JSONL file and return the log path."""

    outputs_dir.mkdir(parents=True, exist_ok=True)
    path = outputs_dir / "incidents.jsonl"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(incident, ensure_ascii=False) + "\n")
    return path
