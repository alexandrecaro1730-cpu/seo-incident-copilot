"""
Business objective:
Provide a simple command-line entry point so reviewers can run the SEO incident
workflow without reading the code first.

Coding objective:
Parse CLI arguments, run the pipeline, and print compact JSON output.
"""

from __future__ import annotations

import argparse
import json

from seo_incident_copilot.config import default_config
from seo_incident_copilot.pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""

    parser = argparse.ArgumentParser(description="Run SEO Incident Copilot demo pipeline.")
    parser.add_argument(
        "--scenario",
        required=True,
        choices=["intent_shift", "technical_regression", "content_decay", "no_trigger", "timeout_fallback"],
        help="Demo scenario to execute.",
    )
    parser.add_argument(
        "--dry-run-slack",
        action="store_true",
        help="Write Slack payload preview to outputs instead of sending.",
    )
    return parser


def main() -> None:
    """CLI entry point."""

    args = build_parser().parse_args()
    result = run_pipeline(default_config(), scenario=args.scenario, dry_run_slack=args.dry_run_slack)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
