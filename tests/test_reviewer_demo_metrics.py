"""
Business Objective:
    Test the one-command reviewer demo metrics so the case-study summary is not
    just a presentation layer but a validated reporting artifact.

Technical Objective:
    Import the reviewer demo script directly and verify that aggregate metrics
    such as model usage, average cost, grounding pass rate, and hallucination risk
    are calculated correctly from controlled scenario summaries.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REVIEWER_DEMO_PATH = PROJECT_ROOT / "scripts" / "reviewer_demo.py"


def load_reviewer_demo_module() -> ModuleType:
    """Load scripts/reviewer_demo.py as a testable Python module."""

    spec = importlib.util.spec_from_file_location("reviewer_demo", REVIEWER_DEMO_PATH)
    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    sys.modules["reviewer_demo"] = module
    spec.loader.exec_module(module)
    return module


def test_reviewer_metrics_show_cost_routing_and_grounding_quality() -> None:
    """The reviewer summary should prove cost-aware routing and grounded AI output."""

    reviewer_demo = load_reviewer_demo_module()

    summaries = [
        {
            "scenario": "no_trigger",
            "status": "no_incident",
            "severity": "low",
        },
        {
            "scenario": "technical_regression",
            "status": "incident_detected",
            "issue_type": "technical_regression",
            "model_tier": "cheap",
            "estimated_cost_eur": 0.002,
            "confidence_score": 0.97,
            "grounding_score": 1.0,
            "grounding_passed": True,
            "grounding_warning_count": 0,
            "human_review_required": True,
            "severity": "critical",
        },
        {
            "scenario": "content_decay",
            "status": "incident_detected",
            "issue_type": "content_decay",
            "model_tier": "middle",
            "estimated_cost_eur": 0.02,
            "confidence_score": 0.74,
            "grounding_score": 1.0,
            "grounding_passed": True,
            "grounding_warning_count": 0,
            "human_review_required": True,
            "severity": "medium",
        },
        {
            "scenario": "intent_shift",
            "status": "incident_detected",
            "issue_type": "intent_shift",
            "model_tier": "expensive",
            "estimated_cost_eur": 0.12,
            "confidence_score": 0.90,
            "grounding_score": 1.0,
            "grounding_passed": True,
            "grounding_warning_count": 0,
            "human_review_required": True,
            "severity": "high",
        },
        {
            "scenario": "timeout_fallback",
            "status": "incident_detected",
            "issue_type": "unknown",
            "model_tier": "expensive",
            "estimated_cost_eur": 0.12,
            "confidence_score": 0.20,
            "grounding_score": 1.0,
            "grounding_passed": True,
            "grounding_warning_count": 0,
            "human_review_required": True,
            "severity": "high",
        },
    ]

    metrics = reviewer_demo.calculate_reviewer_metrics(summaries)

    assert metrics["total_scenarios"] == 5
    assert metrics["incident_count"] == 4
    assert metrics["no_incident_count"] == 1
    assert metrics["model_usage_counts"] == {"cheap": 1, "middle": 1, "expensive": 2}
    assert metrics["model_usage_share"]["expensive"] == 0.5
    assert metrics["total_estimated_cost_eur"] == 0.262
    assert metrics["average_cost_per_incident_eur"] == 0.0655
    assert metrics["grounding_pass_rate"] == 1.0
    assert metrics["estimated_hallucination_risk_rate"] == 0.0
    assert metrics["human_review_rate"] == 1.0
    assert metrics["timeout_or_unknown_fallback_rate"] == 0.25


def test_reviewer_metrics_raise_hallucination_risk_when_grounding_fails() -> None:
    """Grounding failures should appear as non-zero hallucination risk in the demo."""

    reviewer_demo = load_reviewer_demo_module()

    summaries = [
        {
            "scenario": "bad_output",
            "status": "incident_detected",
            "issue_type": "intent_shift",
            "model_tier": "expensive",
            "estimated_cost_eur": 0.12,
            "confidence_score": 0.85,
            "grounding_score": 0.5,
            "grounding_passed": False,
            "grounding_warning_count": 1,
            "human_review_required": True,
            "severity": "high",
        }
    ]

    metrics = reviewer_demo.calculate_reviewer_metrics(summaries)

    assert metrics["grounding_pass_rate"] == 0.0
    assert metrics["estimated_hallucination_risk_rate"] == 1.0
