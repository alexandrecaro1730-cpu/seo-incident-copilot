from seo_incident_copilot.config import default_config
from seo_incident_copilot.pipeline import run_pipeline


def test_pipeline_no_trigger_suppresses_small_movements(tmp_path):
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
    result = run_pipeline(config, "no_trigger")
    assert result["status"] == "no_incident"
    assert result["rank_drop"]["triggered"] is False
