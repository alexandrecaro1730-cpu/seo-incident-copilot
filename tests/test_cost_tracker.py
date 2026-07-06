from seo_incident_copilot.observability.cost_tracker import estimate_analysis_cost


def test_cost_tracker_estimates_tier_cost():
    result = estimate_analysis_cost("expensive", {"cheap": 0.002, "middle": 0.02, "expensive": 0.12})
    assert result["model_tier"] == "expensive"
    assert result["estimated_cost_eur"] == 0.12
