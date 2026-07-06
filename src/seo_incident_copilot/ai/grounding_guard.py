"""
Business objective:
Reduce hallucination risk by requiring every AI claim to point back to known input
or playbook evidence.

Coding objective:
Score evidence coverage and detect obvious contradictions between issue type and
recommendation text.
"""

from __future__ import annotations

from typing import Any


TECHNICAL_ACTION_TERMS = {"noindex", "robots", "canonical", "status code", "reindex"}
INTENT_ACTION_TERMS = {"comparison", "listicle", "buyer", "alternatives", "internal links"}
CONTENT_ACTION_TERMS = {"refresh", "modules", "faq", "pricing", "integrations", "case studies"}


def evaluate_grounding(response: dict[str, Any], evidence_catalog: dict[str, str]) -> dict[str, Any]:
    """Return grounding score and warning flags for a model response."""

    referenced = [item.get("evidence_id") for item in response.get("evidence", [])]
    supported = [evidence_id for evidence_id in referenced if evidence_id in evidence_catalog]
    total = max(len(referenced), 1)
    grounding_score = len(supported) / total

    warnings: list[str] = []
    unknown = sorted(set(referenced) - set(evidence_catalog))
    if unknown:
        warnings.append(f"Unknown evidence IDs: {unknown}")

    contradiction = _detect_action_contradiction(
        issue_type=response.get("issue_type", "unknown"),
        recommended_action=response.get("recommended_action", ""),
    )
    if contradiction:
        warnings.append(contradiction)

    if float(response.get("confidence_score", 0)) > 0.9 and grounding_score < 0.8:
        warnings.append("Confidence is too high for weak evidence grounding.")

    return {
        "grounding_score": round(grounding_score, 3),
        "grounding_passed": grounding_score >= 0.8 and not warnings,
        "warnings": warnings,
    }


def _detect_action_contradiction(issue_type: str, recommended_action: str) -> str | None:
    """Flag basic mismatch between diagnosis and action language."""

    action = recommended_action.lower()
    if issue_type == "intent_shift" and any(term in action for term in TECHNICAL_ACTION_TERMS):
        return "Intent-shift diagnosis recommends a technical-regression action."
    if issue_type == "technical_regression" and any(term in action for term in INTENT_ACTION_TERMS):
        return "Technical-regression diagnosis recommends an intent-shift action."
    if issue_type == "content_decay" and "noindex" in action:
        return "Content-decay diagnosis recommends a noindex fix."
    return None
