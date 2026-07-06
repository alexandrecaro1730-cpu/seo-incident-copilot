import json

from seo_incident_copilot.config import default_config
from seo_incident_copilot.schemas import validate_llm_response


INTENTIONALLY_INVALID_FIXTURES = {"invalid_schema_output_response.json"}


def test_valid_manual_model_outputs_match_schema() -> None:
    """All normal manual outputs should satisfy the shared AI response schema."""

    config = default_config()
    output_files = list((config.model_outputs_dir).glob("*/*.json"))
    assert output_files, "Expected manual model output fixtures"
    for path in output_files:
        if path.name in INTENTIONALLY_INVALID_FIXTURES:
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        result = validate_llm_response(payload)
        assert result.is_valid, f"{path} failed schema validation: {result.errors}"


def test_invalid_schema_fixture_is_intentionally_rejected() -> None:
    """The invalid fixture proves the fallback path handles broken model output."""

    config = default_config()
    path = config.model_outputs_dir / "expensive" / "invalid_schema_output_response.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    result = validate_llm_response(payload)

    assert not result.is_valid
    assert "confidence_score must be a number between 0 and 1" in result.errors
