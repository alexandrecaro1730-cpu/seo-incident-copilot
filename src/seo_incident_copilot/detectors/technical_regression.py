"""
Business objective:
Catch technical SEO regressions before teams waste time rewriting content that is
not the true root cause.

Coding objective:
Perform deterministic checks for indexability, canonicalization, status code, and
robots blocking. LLMs should not be used for values that code can inspect directly.
"""

from __future__ import annotations

from typing import Any


def detect_technical_regression(page_audit: dict[str, Any]) -> dict[str, Any]:
    """Inspect technical SEO fields and return issue flags."""

    issues: list[dict[str, str]] = []
    meta_robots = str(page_audit.get("meta_robots", "")).lower()
    if "noindex" in meta_robots:
        issues.append({"code": "NOINDEX", "message": "Meta robots contains noindex."})

    if bool(page_audit.get("blocked_by_robots_txt")):
        issues.append({"code": "ROBOTS_BLOCK", "message": "URL is blocked by robots.txt."})

    if int(page_audit.get("status_code", 0)) != 200:
        issues.append({"code": "NON_200", "message": "URL does not return HTTP 200."})

    if not bool(page_audit.get("canonical_matches_url", True)):
        issues.append({"code": "CANONICAL_MISMATCH", "message": "Canonical URL does not match page URL."})

    return {
        "has_technical_regression": bool(issues),
        "issues": issues,
        "priority": "urgent" if issues else "normal",
    }
