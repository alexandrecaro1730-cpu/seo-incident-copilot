"""
Business objective:
Turn raw SEO evidence into a validated, grounded, model-tiered incident analysis.

Coding objective:
Compose prompts, call the model client, validate schema, handle timeouts, and add
an evidence-grounding score.
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
    try:
        response = llm_client.analyze(scenario=scenario, tier=tier, prompt=prompt, force_timeout=force_timeout)
    except LLMTimeoutError:
        # Business explanation:
        # Missing an incident entirely is worse than surfacing a lower-confidence
        # fallback that asks a human to review the evidence.
        response = {
            "issue_type": "unknown",
            "confidence_score": 0.2,
            "recommended_action": "LLM analysis timed out; review the deterministic evidence bundle and rerun analysis before making production changes.",
            "evidence": [{"evidence_id": "RANK_001", "claim": "A significant ranking drop triggered the incident workflow."}],
            "next_steps": [
                "Review deterministic technical checks.",
                "Review old and new SERP snapshots manually.",
                "Retry model analysis or escalate to the SEO owner."
            ],
            "requires_human_review": True,
        }

    validation = validate_llm_response(response)
    if not validation.is_valid:
        raise ValueError(f"Invalid LLM response: {validation.errors}")

    grounding = evaluate_grounding(response, evidence_catalog)
    return {
        **response,
        "model_tier": tier,
        "grounding": grounding,
    }
