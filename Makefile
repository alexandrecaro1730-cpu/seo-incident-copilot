install:
	python -m pip install -e ".[dev]"

test:
	python -m pytest

lint:
	python -m ruff check .

quality: test lint

reviewer-demo:
	python scripts/reviewer_demo.py

run-intent:
	python -m seo_incident_copilot.main --scenario intent_shift --dry-run-slack

run-technical:
	python -m seo_incident_copilot.main --scenario technical_regression --dry-run-slack

run-canonical:
	python -m seo_incident_copilot.main --scenario canonical_regression --dry-run-slack

run-content:
	python -m seo_incident_copilot.main --scenario content_decay --dry-run-slack

run-cannibalization:
	python -m seo_incident_copilot.main --scenario keyword_cannibalization --dry-run-slack

run-demand-drop:
	python -m seo_incident_copilot.main --scenario demand_drop_not_seo_issue --dry-run-slack

run-timeout:
	python -m seo_incident_copilot.main --scenario timeout_fallback --dry-run-slack

run-hallucination:
	python -m seo_incident_copilot.main --scenario hallucinated_competitor_claim --dry-run-slack

run-action-mismatch:
	python -m seo_incident_copilot.main --scenario action_mismatch --dry-run-slack

run-invalid-schema:
	python -m seo_incident_copilot.main --scenario invalid_schema_output --dry-run-slack

run-overconfident:
	python -m seo_incident_copilot.main --scenario overconfident_weak_evidence --dry-run-slack

run-no-trigger:
	python -m seo_incident_copilot.main --scenario no_trigger --dry-run-slack

run-all-scenarios:
	python -m seo_incident_copilot.main --scenario no_trigger --dry-run-slack
	python -m seo_incident_copilot.main --scenario demand_drop_not_seo_issue --dry-run-slack
	python -m seo_incident_copilot.main --scenario technical_regression --dry-run-slack
	python -m seo_incident_copilot.main --scenario canonical_regression --dry-run-slack
	python -m seo_incident_copilot.main --scenario content_decay --dry-run-slack
	python -m seo_incident_copilot.main --scenario keyword_cannibalization --dry-run-slack
	python -m seo_incident_copilot.main --scenario intent_shift --dry-run-slack
	python -m seo_incident_copilot.main --scenario timeout_fallback --dry-run-slack
	python -m seo_incident_copilot.main --scenario hallucinated_competitor_claim --dry-run-slack
	python -m seo_incident_copilot.main --scenario action_mismatch --dry-run-slack
	python -m seo_incident_copilot.main --scenario invalid_schema_output --dry-run-slack
	python -m seo_incident_copilot.main --scenario overconfident_weak_evidence --dry-run-slack
live-api-smoke:
	python scripts/live_api_smoke.py
