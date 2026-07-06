"""
Business objective:
Control AI spend by routing only high-impact or ambiguous incidents to expensive
models while keeping obvious cases cheap and fast.

Coding objective:
Implement deterministic routing logic that can be tested without any model API.
"""

from __future__ import annotations

from typing import Any


def choose_model_tier(
    snapshot: dict[str, Any],
    technical: dict[str, Any],
    intent: dict[str, Any],
    content: dict[str, Any],
    high_revenue_risk_eur: int,
    cannibalization: dict[str, Any] | None = None,
) -> str:
    """Choose cheap, middle, or expensive model tier for analysis."""

    revenue_risk = int(snapshot.get("estimated_monthly_revenue_at_risk_eur", 0))
    cannibalization = cannibalization or {}

    # Technical explanation:
    # An obvious noindex/canonical/status issue does not need premium reasoning.
    # Business explanation:
    # Spend money where judgment is needed, not where deterministic checks are clear.
    if technical["has_technical_regression"]:
        return "cheap"

    if cannibalization.get("likely_cannibalization"):
        return "middle"

    ambiguous = intent["likely_intent_shift"] and content["likely_content_decay"]
    if revenue_risk >= high_revenue_risk_eur and (ambiguous or intent["likely_intent_shift"]):
        return "expensive"

    if intent["likely_intent_shift"] or content["likely_content_decay"]:
        return "middle"

    return "cheap"
