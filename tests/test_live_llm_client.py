"""
Business objective:
Verify that live LLM API readiness exists without forcing reviewers to provide
network access or credentials.

Coding objective:
Test fixture mode, missing-key behavior, ready-with-key behavior, minimal payload
validation, and unsupported provider handling.
"""

from __future__ import annotations

from seo_incident_copilot.ai.live_llm_client import (
    LiveLLMClient,
    validate_minimal_analysis_payload,
)


def test_fixture_mode_is_safe_default(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)

    result = LiveLLMClient().smoke_test()

    assert result.status == "skipped"
    assert result.provider == "fixture"


def test_openai_mode_without_key_is_skipped(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    result = LiveLLMClient().smoke_test()

    assert result.status == "skipped"
    assert "OPENAI_API_KEY" in result.message


def test_openai_mode_with_key_is_ready_when_network_disabled(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-placeholder-key")
    monkeypatch.setenv("EXPENSIVE_MODEL_NAME", "test-model")

    result = LiveLLMClient(allow_network=False).smoke_test()

    assert result.status == "ready"
    assert result.provider == "openai"
    assert result.model == "test-model"


def test_unsupported_provider_returns_clean_error():
    result = LiveLLMClient(provider="unsupported").smoke_test()

    assert result.status == "error"
    assert "Unsupported" in result.message


def test_minimal_analysis_payload_validation():
    valid_payload = {
        "issue_type": "intent_shift",
        "confidence_score": 0.82,
        "recommended_action": "Create a comparison page.",
    }

    invalid_payload = {
        "issue_type": "",
        "confidence_score": 1.2,
        "recommended_action": "",
    }

    assert validate_minimal_analysis_payload(valid_payload) == []
    assert validate_minimal_analysis_payload(invalid_payload) == [
        "missing_or_invalid_issue_type",
        "missing_or_invalid_confidence_score",
        "missing_or_invalid_recommended_action",
    ]
