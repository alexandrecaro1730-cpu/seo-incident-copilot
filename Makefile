install:
	python -m pip install -e ".[dev]"

test:
	python -m pytest

run-intent:
	python -m seo_incident_copilot.main --scenario intent_shift --dry-run-slack

run-technical:
	python -m seo_incident_copilot.main --scenario technical_regression --dry-run-slack

run-content:
	python -m seo_incident_copilot.main --scenario content_decay --dry-run-slack
