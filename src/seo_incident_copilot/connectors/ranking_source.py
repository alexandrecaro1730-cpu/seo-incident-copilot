"""
Business objective:
Represent rank-tracker or Google Search Console movement as a stable input contract.

Coding objective:
Load deterministic fixture data from JSON. In production this connector would call
GSC, DataForSEO, Semrush, Ahrefs, or a warehouse table.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_ranking_snapshots(data_dir: Path) -> dict[str, dict[str, Any]]:
    """Load all ranking scenarios from the local fixture file."""

    path = data_dir / "ranking_snapshots.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_ranking_snapshot(data_dir: Path, scenario: str) -> dict[str, Any]:
    """Load one named ranking scenario and fail loudly if the name is wrong."""

    snapshots = load_ranking_snapshots(data_dir)
    if scenario not in snapshots:
        raise KeyError(f"Unknown scenario {scenario!r}. Available: {sorted(snapshots)}")
    snapshot = dict(snapshots[scenario])
    snapshot["scenario"] = scenario
    return snapshot
