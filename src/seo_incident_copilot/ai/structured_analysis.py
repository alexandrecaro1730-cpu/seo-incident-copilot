"""
Business objective:
Turn raw SEO evidence into a validated, grounded, model-tiered incident analysis.

Coding objective:
Compose prompts, call the model client, validate schema, handle timeouts, handle
invalid model output, and add an evidence-grounding score.
"""

from __future__ import annotations

from typing import Any

from seo_incident_copilot.ai.grounding_guard import evaluate_grounding
from seo_incident_copilot.ai.llm_client import LLMTimeoutError, ManualFixtureLLMClient
from seo_incident_copilot.ai.prompt_manager import PromptManager
from seo_incident_copilot.schemas import validate_llm_response


def run_structured_analysis(
    scenario: str,
    tier: str,
    evidence_bundle: dict[str, Any],
    evidence_catalog: dict[str, str],
    prompt_manager: PromptManager,
    llm_client: ManualFixtureLLMClient,
    force_timeout: bool = False,
) -> dict[str, Any]:
    """Run the LLM-like analysis step and return a validated response."""

    prompt = prompt_manager.compose_prompt(tier, evidence_bundle)
    validation_errors: list[str] = []
    fallback_reason: str | None = None

    try:
        response = llm_client.analyze(
            scenario=scenario,
            tier=tier,
            prompt=prompt,
            force_timeout=force_timeout,
        )
    except LLMTimeoutError:
        # Business explanation:
        # Missing an incident entirely is worse than surfacing a lower-confidence
        # fallback that asks a human to review the evidence.
        fallback_reason = "llm_timeout"
        response = _safe_fallback_response(
            recommended_action=(
                "LLM analysis timed out; review the deterministic evidence bundle "
                "and rerun analysis before making production changes."
            ),
            next_steps=[
                "Review deterministic technical checks.",
                "Review old and new SERP snapshots manually.",
                "Retry model analysis or escalate to the SEO owner.",
            ],
        )

    validation = validate_llm_response(response)
    if not validation.is_valid:
        # Business explanation:
        # Invalid structured output should not break the automation or flow into
        # Slack as if it were reliable. We preserve the validation errors, then
        # emit a safe human-review incident.
        validation_errors = validation.errors
        fallback_reason = "invalid_model_output"
        response = _safe_fallback_response(
            recommended_action=(
                "Model output failed schema validation; review deterministic evidence "
                "and fix the prompt or fixture before using this recommendation."
            ),
            next_steps=[
                "Inspect the validation errors in the reviewer summary.",
                "Repair the prompt contract or model-output schema.",
                "Rerun the scenario before making production SEO changes.",
            ],
        )
        fallback_validation = validate_llm_response(response)
        if not fallback_validation.is_valid:  # defensive programming for future edits
            raise ValueError(f"Safe fallback response is invalid: {fallback_validation.errors}")

    grounding = evaluate_grounding(response, evidence_catalog)
    if validation_errors:
        grounding = _add_grounding_warning(
            grounding,
            code="invalid_schema_output",
            message=f"Original model output failed validation: {validation_errors}",
        )

    result = {
        **response,
        "model_tier": tier,
        "grounding": grounding,
    }
    if fallback_reason:
        result["fallback_reason"] = fallback_reason
    if validation_errors:
        result["validation_errors"] = validation_errors
    return result


def _safe_fallback_response(recommended_action: str, next_steps: list[str]) -> dict[str, Any]:
    """Build a low-confidence valid response when the model layer is unsafe."""

    return {
        "issue_type": "unknown",
        "confidence_score": 0.2,
        "recommended_action": recommended_action,
        "evidence": [
            {
                "evidence_id": "RANK_001",
                "claim": "A significant ranking movement or validation failure triggered review.",
            }
        ],
        "next_steps": next_steps,
        "requires_human_review": True,
    }


def _add_grounding_warning(
    grounding: dict[str, Any],
    code: str,
    message: str,
) -> dict[str, Any]:
    """Attach an additional warning to an already computed grounding result."""

    warnings = list(grounding.get("warnings", []))
    warning_codes = set(grounding.get("warning_codes", []))
    warnings.append(message)
    warning_codes.add(code)

    risk = max(float(grounding.get("hallucination_risk_score", 0)), 0.5)
    return {
        **grounding,
        "grounding_passed": False,
        "warnings": warnings,
        "warning_codes": sorted(warning_codes),
        "hallucination_risk_score": risk,
        "hallucination_risk_level": "high" if risk >= 0.5 else "medium",
    }
