"""
Business objective:
Identify when a landing page is losing because competitor pages became richer,
more current, or better aligned with commercial decision-making.

Coding objective:
Use transparent page and competitor signals to produce a decay score that can be
validated in tests.
"""

from __future__ import annotations

from typing import Any

IMPORTANT_COMMERCIAL_MODULES = {
    "pricing",
    "roi_calculator",
    "comparison_table",
    "integrations",
    "case_studies",
    "faq",
    "security",
    "alternatives",
}


def detect_content_decay(page_audit: dict[str, Any], new_serp: dict[str, Any]) -> dict[str, Any]:
    """Estimate whether the client's page is weaker than current winners."""

    client_modules = set(page_audit.get("modules", []))
    competitor_modules: set[str] = set()
    for result in new_serp.get("results", [])[:5]:
        competitor_modules.update(result.get("features", []))

    missing_modules = sorted((competitor_modules & IMPORTANT_COMMERCIAL_MODULES) - client_modules)
    age_days = int(page_audit.get("last_updated_days_ago", 0))
    word_count = int(page_audit.get("word_count", 0))
    low_internal_links = int(page_audit.get("internal_links_in", 0)) < 15

    score = 0.0
    if age_days > 180:
        score += 0.3
    if word_count < 1100:
        score += 0.2
    if missing_modules:
        score += min(0.3, 0.05 * len(missing_modules))
    if low_internal_links:
        score += 0.1

    return {
        "content_decay_score": round(min(score, 1.0), 3),
        "likely_content_decay": score >= 0.5,
        "missing_modules": missing_modules,
        "age_days": age_days,
        "word_count": word_count,
        "low_internal_links": low_internal_links,
    }
