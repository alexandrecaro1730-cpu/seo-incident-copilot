"""
Business objective:
Make the AI layer testable and reviewable before paying for real API calls.

Coding objective:
Provide a fixture-based LLM client that reads manually curated JSON outputs. This
allows prompt/schema tests to be deterministic and green in CI.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class LLMTimeoutError(TimeoutError):
    """Raised when a simulated or real LLM call times out."""


class ManualFixtureLLMClient:
    """Load expected model output from JSON fixture files.

    A real implementation can keep the same `analyze` method and call an API.
    The rest of the pipeline does not need to know whether the model is real or
    fixture-based.
    """

    def __init__(self, model_outputs_dir: Path) -> None:
        self.model_outputs_dir = model_outputs_dir

    def analyze(self, scenario: str, tier: str, prompt: str, force_timeout: bool = False) -> dict[str, Any]:
        """Return a model output fixture for the scenario and tier."""

        # `prompt` is accepted intentionally even though fixtures do not use it.
        # This mirrors the real API signature and makes tests closer to production.
        if force_timeout:
            raise LLMTimeoutError("Simulated LLM timeout for resilience testing.")

        filename = _fixture_filename_for_scenario(scenario)
        path = self.model_outputs_dir / tier / filename
        if not path.exists():
            # If a higher tier fixture is not available, use the middle-tier
            # response when possible. This mirrors a safe fallback hierarchy.
            fallback = self.model_outputs_dir / "middle" / filename
            if fallback.exists():
                path = fallback
            else:
                raise FileNotFoundError(f"No fixture output found for {scenario=} {tier=}")
        return json.loads(path.read_text(encoding="utf-8"))


def _fixture_filename_for_scenario(scenario: str) -> str:
    """Map scenario names to output fixture files."""

    if scenario == "technical_regression":
        return "technical_regression_response.json"
    if scenario == "content_decay":
        return "content_decay_response.json"
    return "intent_shift_response.json"
