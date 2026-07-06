"""
Business Objective:
    Validate the enriched SEO incident scenarios used to show robustness in the
    final case-study presentation.

Technical Objective:
    Exercise canonical regression, keyword cannibalization, demand-shift/no-SEO
    incident, and AI-risk scenarios through the real pipeline.
"""

from __future__ import annotations

from pathlib import Path

from seo_incident_copilot.config import AppConfig, default_config
from seo_incident_copilot.pipeline import run_pipeline


def config_with_tmp_outputs(tmp_path: Path) -> AppConfig:
    """Create a config that writes runtime artifacts into pytest's temp folder."""

    config = default_config()
    return AppConfig(
        project_root=config.project_root,
        data_dir=config.data_dir,
        prompts_dir=config.prompts_dir,
        model_outputs_dir=config.model_outputs_dir,
        outputs_dir=tmp_path,
        rank_drop_threshold=config.rank_drop_threshold,
        high_revenue_risk_eur=config.high_revenue_risk_eur,
        model_cost_eur_per_analysis=config.model_cost_eur_per_analysis,
    )


def test_pipeline_detects_canonical_regression_as_cheap_technical_case(tmp_path: Path) -> None:
    """Canonical mistakes should be caught deterministically and routed cheaply."""

    incident = run_pipeline(config_with_tmp_outputs(tmp_path), "canonical_regression")

    assert incident["status"] == "incident_detected"
    assert incident["analysis"]["issue_type"] == "technical_regression"
    assert incident["analysis"]["model_tier"] == "cheap"
    assert incident["deterministic_checks"]["technical"]["issues"][0]["code"] == "CANONICAL_MISMATCH"
    assert incident["analysis"]["grounding"]["grounding_passed"] is True


def test_pipeline_detects_keyword_cannibalization(tmp_path: Path) -> None:
    """The system should detect when the wrong Maydup URL ranks for the target keyword."""

    incident = run_pipeline(config_with_tmp_outputs(tmp_path), "keyword_cannibalization")

    assert incident["status"] == "incident_detected"
    assert incident["analysis"]["issue_type"] == "keyword_cannibalization"
    assert incident["analysis"]["model_tier"] == "middle"
    assert incident["deterministic_checks"]["cannibalization"]["likely_cannibalization"] is True
    assert incident["analysis"]["grounding"]["grounding_passed"] is True


def test_pipeline_classifies_demand_drop_as_no_seo_incident(tmp_path: Path) -> None:
    """Stable ranking plus declining impressions should avoid a false SEO alert."""

    result = run_pipeline(config_with_tmp_outputs(tmp_path), "demand_drop_not_seo_issue")

    assert result["status"] == "no_seo_incident"
    assert result["rank_drop"]["triggered"] is False
    assert result["deterministic_checks"]["demand"]["likely_demand_shift"] is True


def test_pipeline_flags_hallucinated_competitor_claim(tmp_path: Path) -> None:
    """Unsupported competitor claims should create grounding warnings."""

    incident = run_pipeline(config_with_tmp_outputs(tmp_path), "hallucinated_competitor_claim")
    grounding = incident["analysis"]["grounding"]

    assert incident["status"] == "incident_detected"
    assert grounding["grounding_passed"] is False
    assert "unsupported_claim" in grounding["warning_codes"]
    assert grounding["hallucination_risk_level"] in {"medium", "high"}


def test_pipeline_flags_issue_action_mismatch(tmp_path: Path) -> None:
    """A valid-looking JSON response can still be unsafe if action contradicts diagnosis."""

    incident = run_pipeline(config_with_tmp_outputs(tmp_path), "action_mismatch")
    grounding = incident["analysis"]["grounding"]

    assert incident["analysis"]["issue_type"] == "intent_shift"
    assert grounding["grounding_passed"] is False
    assert "issue_action_mismatch" in grounding["warning_codes"]


def test_pipeline_falls_back_on_invalid_schema_output(tmp_path: Path) -> None:
    """Invalid model JSON should become a safe fallback, not a broken automation."""

    incident = run_pipeline(config_with_tmp_outputs(tmp_path), "invalid_schema_output")
    analysis = incident["analysis"]

    assert analysis["issue_type"] == "unknown"
    assert analysis["fallback_reason"] == "invalid_model_output"
    assert analysis["validation_errors"]
    assert "invalid_schema_output" in analysis["grounding"]["warning_codes"]


def test_pipeline_flags_overconfident_weak_evidence(tmp_path: Path) -> None:
    """High-confidence recommendations with fake evidence IDs should be downgraded."""

    incident = run_pipeline(config_with_tmp_outputs(tmp_path), "overconfident_weak_evidence")
    grounding = incident["analysis"]["grounding"]

    assert grounding["grounding_passed"] is False
    assert "unknown_evidence_id" in grounding["warning_codes"]
    assert "overconfident_weak_evidence" in grounding["warning_codes"]
