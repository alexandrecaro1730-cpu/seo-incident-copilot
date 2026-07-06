"""
Business objective:
Version prompts as explicit project artifacts so reviewers can inspect, critique,
and improve the AI behavior.

Coding objective:
Load prompt text by model tier and compose it with runtime evidence. The composed
prompt can be logged or manually tested before connecting to a live LLM.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROMPT_FILES = {
    "cheap": "cheap_model_triage.txt",
    "middle": "middle_model_root_cause.txt",
    "expensive": "expensive_model_executive_decision.txt",
}


class PromptManager:
    """Load and compose prompts for the selected model tier."""

    def __init__(self, prompts_dir: Path) -> None:
        self.prompts_dir = prompts_dir

    def load_prompt(self, tier: str) -> str:
        """Load the manual prompt text for a model tier."""

        if tier not in PROMPT_FILES:
            raise ValueError(f"Unknown model tier: {tier}")
        system = (self.prompts_dir / "system_guardrails.txt").read_text(encoding="utf-8")
        tier_prompt = (self.prompts_dir / PROMPT_FILES[tier]).read_text(encoding="utf-8")
        return system + "\n\n" + tier_prompt

    def compose_prompt(self, tier: str, evidence_bundle: dict[str, Any]) -> str:
        """Create the final prompt string that would be sent to the model."""

        base_prompt = self.load_prompt(tier)
        return base_prompt + "\n\n# Evidence Bundle\n" + json.dumps(evidence_bundle, indent=2)
