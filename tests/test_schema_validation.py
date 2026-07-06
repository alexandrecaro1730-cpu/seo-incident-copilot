from seo_incident_copilot.schemas import validate_llm_response


def valid_payload():
    return {
        "issue_type": "intent_shift",
        "confidence_score": 0.86,
        "recommended_action": "Create a comparison asset and add internal links to the commercial page.",
        "evidence": [{"evidence_id": "SERP_001", "claim": "SERP shifted toward listicles."}],
        "next_steps": ["Create comparison asset."],
        "requires_human_review": True,
    }


def test_valid_llm_response_passes():
    result = validate_llm_response(valid_payload())
    assert result.is_valid is True
    assert result.errors == []


def test_invalid_issue_type_fails():
    payload = valid_payload()
    payload["issue_type"] = "made_up"
    result = validate_llm_response(payload)
    assert result.is_valid is False
    assert any("Invalid issue_type" in error for error in result.errors)


def test_confidence_outside_range_fails():
    payload = valid_payload()
    payload["confidence_score"] = 1.4
    result = validate_llm_response(payload)
    assert result.is_valid is False
