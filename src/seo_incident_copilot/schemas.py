"""
Business objective:
Protect SEO teams from unreliable AI output by enforcing a clear incident schema.

Coding objective:
Implement dependency-free validation for the model contract. In production this
could be replaced by Pydantic or provider-native structured outputs, but the
business rule stays the same: no valid schema, no trusted alert.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

ALLOWED_ISSUE_TYPES = {
    "intent_shift",
    "technical_regression",
    "content_decay",
    "keyword_cannibalization",
    "demand_shift",
    "competitor_improvement",
    "mixed_issue",
    "mixed",
    "unknown",
}

REQUIRED_RESPONSE_KEYS = {
    "issue_type",
    "confidence_score",
    "recommended_action",
    "evidence",
    "next_steps",
    "requires_human_review",
}


@dataclass(frozen=True)
class ValidationResult:
    """Small result object used by tests and pipeline code."""

    is_valid: bool
    errors: list[str]


def validate_llm_response(payload: dict[str, Any]) -> ValidationResult:
    """Validate the strict JSON response expected from every model tier.

    Business explanation:
    A Slack alert can influence client work and engineering priorities. We should
    not let malformed or unsupported AI responses enter the operational workflow.

    Technical explanation:
    The function checks required keys, enum values, numeric ranges, and evidence
    list structure. It returns all errors at once so debugging prompts is faster.
    """

    errors: list[str] = []
    missing = REQUIRED_RESPONSE_KEYS - set(payload)
    if missing:
        errors.append(f"Missing required keys: {sorted(missing)}")

    issue_type = payload.get("issue_type")
    if issue_type not in ALLOWED_ISSUE_TYPES:
        errors.append(f"Invalid issue_type: {issue_type!r}")

    confidence = payload.get("confidence_score")
    if not isinstance(confidence, (int, float)) or not 0 <= float(confidence) <= 1:
        errors.append("confidence_score must be a number between 0 and 1")

    action = payload.get("recommended_action")
    if not isinstance(action, str) or len(action.strip()) < 20:
        errors.append("recommended_action must be a descriptive string")

    evidence = payload.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        errors.append("evidence must be a non-empty list")
    else:
        for idx, item in enumerate(evidence):
            if not isinstance(item, dict):
                errors.append(f"evidence[{idx}] must be an object")
                continue
            if not isinstance(item.get("evidence_id"), str) or not item["evidence_id"].strip():
                errors.append(f"evidence[{idx}].evidence_id must be a non-empty string")
            if not isinstance(item.get("claim"), str) or not item["claim"].strip():
                errors.append(f"evidence[{idx}].claim must be a non-empty string")

    next_steps = payload.get("next_steps")
    if not isinstance(next_steps, list) or not next_steps:
        errors.append("next_steps must be a non-empty list")
    elif not all(isinstance(step, str) and step.strip() for step in next_steps):
        errors.append("every next step must be a non-empty string")

    if not isinstance(payload.get("requires_human_review"), bool):
        errors.append("requires_human_review must be boolean")

    return ValidationResult(is_valid=not errors, errors=errors)
