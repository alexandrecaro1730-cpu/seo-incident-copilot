from seo_incident_copilot.config import default_config
from seo_incident_copilot.pipeline import run_pipeline


def test_pipeline_content_decay_detects_stale_page(tmp_path):
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
    incident = run_pipeline(config, "content_decay")
    assert incident["analysis"]["issue_type"] == "content_decay"
    assert incident["analysis"]["model_tier"] == "middle"
    assert "pricing" in incident["deterministic_checks"]["content"]["missing_modules"]
