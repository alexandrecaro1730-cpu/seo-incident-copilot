import json

from seo_incident_copilot.config import default_config
from seo_incident_copilot.schemas import validate_llm_response


def test_all_manual_model_outputs_match_schema():
    config = default_config()
    output_files = list((config.model_outputs_dir).glob("*/*.json"))
    assert output_files, "Expected manual model output fixtures"
    for path in output_files:
        payload = json.loads(path.read_text(encoding="utf-8"))
        result = validate_llm_response(payload)
        assert result.is_valid, f"{path} failed schema validation: {result.errors}"
