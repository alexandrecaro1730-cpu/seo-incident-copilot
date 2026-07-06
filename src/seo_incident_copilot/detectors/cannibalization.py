"""
Business objective:
Detect when a ranking loss may be caused by the wrong client URL becoming the
ranking URL for a valuable keyword.

Coding objective:
Use deterministic URL-switch signals from the rank tracker/SERP fixtures. This is
kept outside the LLM because cannibalization is a data relationship, not a prose
interpretation task.
"""

from __future__ import annotations

from typing import Any


def detect_keyword_cannibalization(
    snapshot: dict[str, Any],
    old_serp: dict[str, Any],
    new_serp: dict[str, Any],
) -> dict[str, Any]:
    """Return whether another client URL appears to have taken over the query.

    Business explanation:
    B2B SaaS sites often have product pages, glossary pages, blogs, and comparison
    pages competing for the same query. If the wrong page ranks, the team may lose
    conversion intent even when the domain still has visibility.

    Technical explanation:
    The fixture can provide explicit ranking URL fields. If not, the detector falls
    back to scanning old/new SERP results for the configured primary and competing
    URLs.
    """

    primary_url = str(snapshot.get("url", ""))
    before_url = str(snapshot.get("ranking_url_before") or primary_url)
    after_url = str(snapshot.get("ranking_url_after") or "")
    competing_url = str(snapshot.get("competing_url") or "")

    if not after_url:
        after_url = _find_highest_matching_url(new_serp, [primary_url, competing_url]) or primary_url

    before_matches_primary = before_url == primary_url
    after_is_competing = bool(after_url and after_url != primary_url)
    explicit_competing_match = bool(competing_url and after_url == competing_url)

    likely = before_matches_primary and after_is_competing

    return {
        "likely_cannibalization": likely,
        "primary_url": primary_url,
        "ranking_url_before": before_url,
        "ranking_url_after": after_url,
        "competing_url": competing_url or after_url if likely else competing_url,
        "explicit_competing_match": explicit_competing_match,
        "old_serp_primary_seen": bool(_find_highest_matching_url(old_serp, [primary_url])),
        "new_serp_primary_seen": bool(_find_highest_matching_url(new_serp, [primary_url])),
    }


def _find_highest_matching_url(serp: dict[str, Any], urls: list[str]) -> str | None:
    """Find the highest-ranking URL from a small candidate list."""

    clean_urls = {url for url in urls if url}
    if not clean_urls:
        return None

    for result in sorted(serp.get("results", []), key=lambda item: int(item.get("position", 999))):
        result_url = str(result.get("url", ""))
        if result_url in clean_urls:
            return result_url
    return None
