from seo_incident_copilot.ai.model_router import choose_model_tier


def base_snapshot(revenue=42000):
    return {"estimated_monthly_revenue_at_risk_eur": revenue}


def test_router_uses_cheap_for_obvious_technical_regression():
    tier = choose_model_tier(
        snapshot=base_snapshot(65000),
        technical={"has_technical_regression": True},
        intent={"likely_intent_shift": True},
        content={"likely_content_decay": True},
        high_revenue_risk_eur=40000,
    )
    assert tier == "cheap"


def test_router_uses_expensive_for_high_value_intent_shift():
    tier = choose_model_tier(
        snapshot=base_snapshot(42000),
        technical={"has_technical_regression": False},
        intent={"likely_intent_shift": True},
        content={"likely_content_decay": False},
        high_revenue_risk_eur=40000,
    )
    assert tier == "expensive"


def test_router_uses_middle_for_medium_value_content_decay():
    tier = choose_model_tier(
        snapshot=base_snapshot(18000),
        technical={"has_technical_regression": False},
        intent={"likely_intent_shift": False},
        content={"likely_content_decay": True},
        high_revenue_risk_eur=40000,
    )
    assert tier == "middle"
