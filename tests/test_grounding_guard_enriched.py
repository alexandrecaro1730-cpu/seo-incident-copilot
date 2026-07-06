"""
Business Objective:
    Prove that hallucination and contradiction checks cover more than JSON shape.

Technical Objective:
    Unit test the grounding guard directly with controlled evidence catalogs.
"""

from __future__ import annotations

from seo_incident_copilot.ai.grounding_guard import evaluate_grounding


def test_grounding_guard_flags_sensitive_unsupported_claim() -> None:
    """A claim about competitor pricing last week should require actual evidence."""

    response = {
        "issue_type": "content_decay",
        "confidence_score": 0.88,
        "recommended_action": "Add a comparison section after human validation.",
        "evidence": [
            {
                "evidence_id": "SERP_001",
                "claim": "Competitor A added transparent pricing last week.",
            }
        ],
    }
    catalog = {"SERP_001": "SERP shifted toward comparison articles and review pages."}

    grounding = evaluate_grounding(response, catalog)

    assert grounding["grounding_passed"] is False
    assert "unsupported_claim" in grounding["warning_codes"]


def test_grounding_guard_accepts_supported_claims() -> None:
    """Evidence IDs with supported claim language should pass the guard."""

    response = {
        "issue_type": "technical_regression",
        "confidence_score": 0.96,
        "recommended_action": "Fix the canonical mismatch and validate the template.",
        "evidence": [
            {
                "evidence_id": "TECH_001",
                "claim": "The page audit reports a canonical mismatch.",
            }
        ],
    }
    catalog = {"TECH_001": "The page audit reports a canonical mismatch."}

    grounding = evaluate_grounding(response, catalog)

    assert grounding["grounding_passed"] is True
    assert grounding["hallucination_risk_score"] == 0.0


def test_grounding_guard_flags_action_mismatch() -> None:
    """Intent-shift diagnosis should not recommend noindex remediation."""

    response = {
        "issue_type": "intent_shift",
        "confidence_score": 0.91,
        "recommended_action": "Remove the noindex tag and request reindexing.",
        "evidence": [{"evidence_id": "SERP_001", "claim": "SERP shifted."}],
    }
    catalog = {"SERP_001": "SERP shifted toward listicles."}

    grounding = evaluate_grounding(response, catalog)

    assert grounding["grounding_passed"] is False
    assert "issue_action_mismatch" in grounding["warning_codes"]
