"""
Business objective:
Avoid alert fatigue by only triggering incident analysis for meaningful ranking drops.

Coding objective:
Use a transparent threshold-based detector that can be unit-tested and adjusted
per client or keyword priority.
"""

from __future__ import annotations

from typing import Any


def detect_rank_drop(snapshot: dict[str, Any], threshold: int = 5) -> dict[str, Any]:
    """Return rank-drop metadata for a keyword snapshot.

    Google ranking positions are better when lower, so a move from 2 to 9 is a
    drop of 7 positions. A move from 5 to 6 is noise for this workflow.
    """

    old_position = int(snapshot["old_position"])
    new_position = int(snapshot["new_position"])
    positions_lost = new_position - old_position
    triggered = positions_lost >= threshold
    return {
        "triggered": triggered,
        "old_position": old_position,
        "new_position": new_position,
        "positions_lost": positions_lost,
        "threshold": threshold,
        "severity": _severity(positions_lost, snapshot.get("business_priority", "medium")),
    }


def _severity(positions_lost: int, priority: str) -> str:
    """Map ranking movement and business priority to a human-readable severity."""

    if positions_lost >= 10 or priority == "critical":
        return "critical"
    if positions_lost >= 7 or priority == "high":
        return "high"
    if positions_lost >= 5:
        return "medium"
    return "low"
