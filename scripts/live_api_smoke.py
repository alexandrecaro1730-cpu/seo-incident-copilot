"""
Business objective:
Give reviewers and engineers a separate command that proves live LLM API readiness
without disrupting the deterministic SEO incident reviewer demo.

Coding objective:
Expose a small CLI around LiveLLMClient that prints JSON and exits successfully for
safe skipped/ready states, while returning a non-zero code only for real errors.
"""

from __future__ import annotations

import argparse
import json
import sys

from seo_incident_copilot.ai.live_llm_client import LiveLLMClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Live LLM API smoke test.")
    parser.add_argument(
        "--provider",
        choices=["fixture", "openai", "anthropic"],
        default=None,
        help="Override LLM_PROVIDER for this smoke test.",
    )
    parser.add_argument(
        "--tier",
        choices=["cheap", "middle", "expensive"],
        default="expensive",
        help="Model cost tier to smoke test.",
    )
    parser.add_argument(
        "--allow-network",
        action="store_true",
        help="Actually call the provider API if credentials are configured.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = LiveLLMClient(
        provider=args.provider,
        tier=args.tier,
        allow_network=args.allow_network,
    ).smoke_test()

    print(json.dumps(result.to_dict(), indent=2, sort_keys=True))

    return 1 if result.status == "error" else 0


if __name__ == "__main__":
    sys.exit(main())
