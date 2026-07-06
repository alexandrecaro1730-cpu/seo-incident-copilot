"""
Business objective:
Make AI spend visible so the team can scale automations without silent cost creep.

Coding objective:
Estimate per-incident model cost using tier-level assumptions from configuration.
"""

from __future__ import annotations


def estimate_analysis_cost(tier: str, cost_table: dict[str, float]) -> dict[str, float | str]:
    """Return a small cost record for the selected model tier."""

    cost = float(cost_table.get(tier, 0.0))
    return {"model_tier": tier, "estimated_cost_eur": round(cost, 4)}
