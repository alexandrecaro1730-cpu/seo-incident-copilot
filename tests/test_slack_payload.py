from seo_incident_copilot.connectors.slack_client import build_slack_payload


def test_slack_payload_contains_actionable_blocks():
    incident = {
        "snapshot": {
            "client": "Maydup Manufacturing Cloud",
            "keyword": "manufacturing training software",
            "url": "https://maydup.example.com/manufacturing-training-software",
            "estimated_monthly_revenue_at_risk_eur": 42000,
        },
        "rank_drop": {"old_position": 2, "new_position": 9},
        "analysis": {
            "issue_type": "intent_shift",
            "confidence_score": 0.86,
            "model_tier": "middle",
            "recommended_action": "Create comparison asset.",
            "evidence": [{"evidence_id": "SERP_001", "claim": "SERP changed."}],
            "next_steps": ["Create asset."],
            "grounding": {"grounding_score": 0.92},
        },
        "cost": {"estimated_cost_eur": 0.02},
    }
    payload = build_slack_payload(incident)
    assert payload["text"].startswith("SEO Incident")
    assert len(payload["blocks"]) >= 5
    joined = str(payload)
    assert "manufacturing training software" in joined
    assert "Grounding score" in joined
