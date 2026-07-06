"""
Business objective:
Detect when Google changes the preferred result format so the team can adapt the
content strategy instead of blindly optimizing the existing landing page.

Coding objective:
Compute simple, explainable SERP composition metrics that the LLM can later use
as grounded evidence.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

INVESTIGATION_TYPES = {
    "listicle",
    "review_category_page",
    "comparison_article",
    "comparison_landing_page",
    "buyers_guide",
}

VENDOR_TYPES = {"vendor_landing_page"}


def summarize_serp(serp: dict[str, Any], top_n: int = 5) -> dict[str, Any]:
    """Summarize result types and intent labels in the top N results."""

    top_results = serp.get("results", [])[:top_n]
    type_counts = Counter(result.get("result_type") for result in top_results)
    intent_counts = Counter(result.get("intent_label") for result in top_results)
    investigation_count = sum(type_counts.get(t, 0) for t in INVESTIGATION_TYPES)
    vendor_count = sum(type_counts.get(t, 0) for t in VENDOR_TYPES)
    return {
        "top_n": top_n,
        "type_counts": dict(type_counts),
        "intent_counts": dict(intent_counts),
        "investigation_ratio": investigation_count / max(len(top_results), 1),
        "vendor_ratio": vendor_count / max(len(top_results), 1),
    }


def compare_serp_intent(old_serp: dict[str, Any], new_serp: dict[str, Any]) -> dict[str, Any]:
    """Compare old and new SERP composition and estimate intent-shift strength."""

    old_summary = summarize_serp(old_serp)
    new_summary = summarize_serp(new_serp)
    investigation_delta = new_summary["investigation_ratio"] - old_summary["investigation_ratio"]
    vendor_delta = new_summary["vendor_ratio"] - old_summary["vendor_ratio"]
    shift_score = max(0.0, min(1.0, investigation_delta + max(0.0, -vendor_delta)))
    return {
        "old_summary": old_summary,
        "new_summary": new_summary,
        "investigation_delta": round(investigation_delta, 3),
        "vendor_delta": round(vendor_delta, 3),
        "intent_shift_score": round(shift_score, 3),
        "likely_intent_shift": shift_score >= 0.5,
    }
