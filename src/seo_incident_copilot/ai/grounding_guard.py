"""
Business objective:
Reduce hallucination risk by requiring every AI claim to point back to known input
or playbook evidence, and by flagging recommendations that conflict with the
root-cause diagnosis.

Coding objective:
Score evidence coverage, detect unknown evidence IDs, flag unsupported claim
language, and detect obvious action/issue mismatches. The implementation is kept
transparent and dependency-free so it can be discussed line-by-line in interview.
"""

from __future__ import annotations

import re
from typing import Any


TECHNICAL_ACTION_TERMS = {"noindex", "robots", "canonical", "status code", "reindex"}
INTENT_ACTION_TERMS = {"comparison", "listicle", "buyer", "alternatives", "internal links"}
CONTENT_ACTION_TERMS = {"refresh", "modules", "faq", "pricing", "integrations", "case studies"}
CANNIBALIZATION_TERMS = {"cannibal", "wrong url", "ranking url", "consolidate"}
DEMAND_TERMS = {"demand", "seasonality", "impressions", "market"}

# Business explanation:
# These terms often appear in confident but unsupported model claims. They are not
# forbidden, but if the supporting evidence text does not contain them, the guard
# should ask for human review.
CLAIM_SENSITIVE_TERMS = {
    "last week",
    "yesterday",
    "competitor a",
    "competitor added",
    "transparent pricing",
    "pricing page launched",
    "new feature",
}

STOPWORDS = {
    "about",
    "after",
    "because",
    "before",
    "between",
    "claim",
    "contains",
    "current",
    "evidence",
    "from",
    "have",
    "into",
    "page",
    "pages",
    "playbook",
    "position",
    "recommends",
    "result",
    "results",
    "score",
    "shows",
    "that",
    "their",
    "there",
    "this",
    "toward",
    "with",
}


def evaluate_grounding(response: dict[str, Any], evidence_catalog: dict[str, str]) -> dict[str, Any]:
    """Return grounding score, warning flags, and hallucination-risk proxy.

    Business explanation:
    A model can produce valid JSON and still be unsafe. This guard checks whether
    the recommendation is actually tied to known evidence and whether the action
    matches the diagnosed SEO root cause.

    Technical explanation:
    The score is based on evidence ID coverage. Warnings add extra risk signals:
    unknown evidence IDs, unsupported claim text, overconfident weak evidence, and
    issue/action contradictions.
    """

    referenced = [item.get("evidence_id") for item in response.get("evidence", [])]
    supported = [evidence_id for evidence_id in referenced if evidence_id in evidence_catalog]
    total = max(len(referenced), 1)
    grounding_score = len(supported) / total

    warnings: list[str] = []
    warning_codes: list[str] = []

    unknown = sorted(set(referenced) - set(evidence_catalog))
    if unknown:
        warnings.append(f"Unknown evidence IDs: {unknown}")
        warning_codes.append("unknown_evidence_id")

    unsupported_claims = _find_unsupported_claims(response, evidence_catalog)
    if unsupported_claims:
        warnings.extend(unsupported_claims)
        warning_codes.append("unsupported_claim")

    contradiction = _detect_action_contradiction(
        issue_type=response.get("issue_type", "unknown"),
        recommended_action=response.get("recommended_action", ""),
    )
    if contradiction:
        warnings.append(contradiction)
        warning_codes.append("issue_action_mismatch")

    if float(response.get("confidence_score", 0)) > 0.9 and grounding_score < 0.8:
        warnings.append("Confidence is too high for weak evidence grounding.")
        warning_codes.append("overconfident_weak_evidence")

    if float(response.get("confidence_score", 0)) > 0.9 and unsupported_claims:
        warnings.append("Confidence is too high for unsupported claim text.")
        warning_codes.append("overconfident_unsupported_claim")

    unique_codes = sorted(set(warning_codes))
    hallucination_risk_score = _risk_score(grounding_score, unique_codes)

    return {
        "grounding_score": round(grounding_score, 3),
        "grounding_passed": grounding_score >= 0.8 and not unique_codes,
        "warnings": warnings,
        "warning_codes": unique_codes,
        "hallucination_risk_score": hallucination_risk_score,
        "hallucination_risk_level": _risk_level(hallucination_risk_score),
    }


def _find_unsupported_claims(
    response: dict[str, Any],
    evidence_catalog: dict[str, str],
) -> list[str]:
    """Flag claims that appear materially disconnected from their evidence text."""

    unsupported: list[str] = []
    for item in response.get("evidence", []):
        evidence_id = item.get("evidence_id")
        claim = str(item.get("claim", ""))
        if evidence_id not in evidence_catalog:
            continue

        evidence_text = evidence_catalog[evidence_id]
        if _has_sensitive_term_without_support(claim, evidence_text):
            unsupported.append(f"Potential unsupported claim for {evidence_id}: {claim}")
            continue

    return unsupported


def _has_sensitive_term_without_support(claim: str, evidence_text: str) -> bool:
    """Return True when a risky claim term is not present in the evidence."""

    claim_lower = claim.lower()
    evidence_lower = evidence_text.lower()
    return any(term in claim_lower and term not in evidence_lower for term in CLAIM_SENSITIVE_TERMS)


def _claim_overlap_too_low(claim: str, evidence_text: str) -> bool:
    """Use a lightweight token-overlap proxy for claim support."""

    claim_tokens = _meaningful_tokens(claim)
    if len(claim_tokens) < 3:
        return False

    evidence_tokens = _meaningful_tokens(evidence_text)
    overlap = claim_tokens & evidence_tokens
    return len(overlap) / len(claim_tokens) < 0.12


def _meaningful_tokens(text: str) -> set[str]:
    """Tokenize text for simple evidence-overlap checks."""

    tokens = set(re.findall(r"[a-zA-Z][a-zA-Z0-9_\-]{3,}", text.lower()))
    return {token for token in tokens if token not in STOPWORDS}


def _detect_action_contradiction(issue_type: str, recommended_action: str) -> str | None:
    """Flag basic mismatch between diagnosis and action language."""

    action = recommended_action.lower()
    if issue_type == "intent_shift" and any(term in action for term in TECHNICAL_ACTION_TERMS):
        return "Intent-shift diagnosis recommends a technical-regression action."
    if issue_type == "technical_regression" and any(term in action for term in INTENT_ACTION_TERMS):
        return "Technical-regression diagnosis recommends an intent-shift action."
    if issue_type == "content_decay" and "noindex" in action:
        return "Content-decay diagnosis recommends a noindex fix."
    if issue_type == "keyword_cannibalization" and any(term in action for term in DEMAND_TERMS):
        return "Cannibalization diagnosis recommends a demand-shift action."
    if issue_type == "demand_shift" and any(term in action for term in TECHNICAL_ACTION_TERMS):
        return "Demand-shift diagnosis recommends a technical-regression action."
    return None


def _risk_score(grounding_score: float, warning_codes: list[str]) -> float:
    """Convert grounding weakness and warning codes into a simple risk proxy."""

    base = 1.0 - grounding_score
    warning_weight = min(1.0, 0.25 * len(warning_codes))
    return round(max(base, warning_weight), 3)


def _risk_level(score: float) -> str:
    """Map a numeric risk proxy to a readable level."""

    if score >= 0.5:
        return "high"
    if score >= 0.25:
        return "medium"
    if score > 0:
        return "low"
    return "none"
