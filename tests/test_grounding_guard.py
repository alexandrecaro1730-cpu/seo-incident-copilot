from seo_incident_copilot.ai.grounding_guard import evaluate_grounding


def test_grounding_passes_with_known_evidence():
    response = {
        "issue_type": "intent_shift",
        "confidence_score": 0.86,
        "recommended_action": "Create a comparison asset and improve internal links.",
        "evidence": [{"evidence_id": "SERP_001", "claim": "SERP changed."}],
    }
    result = evaluate_grounding(response, {"SERP_001": "SERP changed."})
    assert result["grounding_passed"] is True
    assert result["grounding_score"] == 1.0


def test_grounding_flags_unknown_evidence():
    response = {
        "issue_type": "intent_shift",
        "confidence_score": 0.86,
        "recommended_action": "Create a comparison asset and improve internal links.",
        "evidence": [{"evidence_id": "FAKE_001", "claim": "Unsupported."}],
    }
    result = evaluate_grounding(response, {"SERP_001": "SERP changed."})
    assert result["grounding_passed"] is False
    assert result["grounding_score"] == 0.0


def test_grounding_flags_issue_action_contradiction():
    response = {
        "issue_type": "intent_shift",
        "confidence_score": 0.86,
        "recommended_action": "Remove noindex and request reindexing.",
        "evidence": [{"evidence_id": "SERP_001", "claim": "SERP changed."}],
    }
    result = evaluate_grounding(response, {"SERP_001": "SERP changed."})
    assert result["grounding_passed"] is False
    assert any("technical-regression" in warning for warning in result["warnings"])
