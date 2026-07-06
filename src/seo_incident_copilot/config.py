"""
Business objective:
Centralize project paths and model pricing so the system can be operated, tested,
and audited without hidden configuration.

Coding objective:
Expose a small immutable configuration object. This avoids scattering filesystem
paths, thresholds, and cost assumptions across the codebase.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    """Runtime configuration for local and production-like runs."""

    project_root: Path
    data_dir: Path
    prompts_dir: Path
    model_outputs_dir: Path
    outputs_dir: Path
    rank_drop_threshold: int = 5
    high_revenue_risk_eur: int = 40000

    # Business explanation:
    # These are illustrative costs, not vendor commitments. They let the case
    # study show budget-aware routing without requiring a live model provider.
    model_cost_eur_per_analysis: dict[str, float] | None = None

    def __post_init__(self) -> None:
        if self.model_cost_eur_per_analysis is None:
            object.__setattr__(
                self,
                "model_cost_eur_per_analysis",
                {"cheap": 0.002, "middle": 0.02, "expensive": 0.12},
            )


def default_config() -> AppConfig:
    """Create default local config rooted at the repository directory."""

    project_root = Path(__file__).resolve().parents[2]
    return AppConfig(
        project_root=project_root,
        data_dir=project_root / "data",
        prompts_dir=project_root / "prompts",
        model_outputs_dir=project_root / "model_outputs",
        outputs_dir=project_root / "outputs",
    )
