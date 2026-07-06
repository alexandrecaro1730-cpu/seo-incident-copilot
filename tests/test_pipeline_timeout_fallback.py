from seo_incident_copilot.config import default_config
from seo_incident_copilot.pipeline import run_pipeline


def test_pipeline_timeout_returns_safe_unknown_incident(tmp_path):
    config = default_config()
    config = config.__class__(
        project_root=config.project_root,
        data_dir=config.data_dir,
        prompts_dir=config.prompts_dir,
        model_outputs_dir=config.model_outputs_dir,
        outputs_dir=tmp_path,
        rank_drop_threshold=config.rank_drop_threshold,
        high_revenue_risk_eur=config.high_revenue_risk_eur,
        model_cost_eur_per_analysis=config.model_cost_eur_per_analysis,
    )
    incident = run_pipeline(config, "timeout_fallback")
    assert incident["status"] == "incident_detected"
    assert incident["analysis"]["issue_type"] == "unknown"
    assert incident["analysis"]["confidence_score"] == 0.2
    assert incident["analysis"]["requires_human_review"] is True
