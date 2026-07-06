"""
Business objective:
Avoid treating every traffic decline as an SEO incident. Sometimes demand drops
while rankings remain stable, and the right response is market monitoring rather
than technical remediation.

Coding objective:
Use GSC-style trend fixtures to detect demand decline when impressions fall
materially but average position is stable.
"""

from __future__ import annotations

from typing import Any


def detect_demand_shift(gsc_metrics: dict[str, Any]) -> dict[str, Any]:
    """Detect demand decline without a ranking-loss pattern."""

    before_impressions = float(gsc_metrics.get("impressions_28d_before", 0) or 0)
    after_impressions = float(gsc_metrics.get("impressions_28d_after", 0) or 0)
    before_position = float(gsc_metrics.get("average_position_before", 0) or 0)
    after_position = float(gsc_metrics.get("average_position_after", 0) or 0)

    impression_change = 0.0
    if before_impressions > 0:
        impression_change = (after_impressions - before_impressions) / before_impressions

    position_delta = after_position - before_position
    ranking_stable = abs(position_delta) <= 1.0
    demand_decline = impression_change <= -0.25

    return {
        "likely_demand_shift": bool(demand_decline and ranking_stable),
        "impression_change_pct": round(impression_change, 3),
        "position_delta": round(position_delta, 3),
        "ranking_stable": ranking_stable,
        "demand_decline": demand_decline,
    }
