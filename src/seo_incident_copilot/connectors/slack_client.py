"""
Business objective:
Turn technical SEO diagnosis into an actionable team alert that clearly states
impact, evidence, recommended action, and owner suggestions.

Coding objective:
Build a Slack Block Kit-compatible payload. The default dry-run mode writes the
payload to disk instead of making network calls, keeping tests deterministic.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib import request


def build_slack_payload(incident: dict[str, Any]) -> dict[str, Any]:
    """Create a Slack message payload from the incident record."""

    snapshot = incident["snapshot"]
    analysis = incident["analysis"]
    grounding = analysis["grounding"]
    rank = incident["rank_drop"]
    evidence_lines = "\n".join(
        f"• `{item['evidence_id']}` — {item['claim']}" for item in analysis["evidence"]
    )
    next_steps = "\n".join(f"{idx + 1}. {step}" for idx, step in enumerate(analysis["next_steps"]))

    text = (
        f"SEO Incident: {snapshot['keyword']} dropped "
        f"{rank['old_position']} → {rank['new_position']}"
    )

    return {
        "text": text,
        "blocks": [
            {"type": "header", "text": {"type": "plain_text", "text": "🚨 SEO Incident Detected"}},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"*Client:* {snapshot['client']}\n"
                        f"*Keyword:* `{snapshot['keyword']}`\n"
                        f"*URL:* {snapshot['url']}\n"
                        f"*Position change:* {rank['old_position']} → {rank['new_position']}\n"
                        f"*Estimated monthly revenue at risk:* €{snapshot['estimated_monthly_revenue_at_risk_eur']:,}"
                    ),
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"*Likely cause:* `{analysis['issue_type']}`\n"
                        f"*Confidence:* {analysis['confidence_score']:.0%}\n"
                        f"*Grounding score:* {grounding['grounding_score']:.0%}\n"
                        f"*Model tier:* `{analysis['model_tier']}`\n"
                        f"*Estimated AI cost:* €{incident['cost']['estimated_cost_eur']:.4f}"
                    ),
                },
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Recommended action:*\n{analysis['recommended_action']}"},
            },
            {"type": "section", "text": {"type": "mrkdwn", "text": f"*Evidence:*\n{evidence_lines}"}},
            {"type": "section", "text": {"type": "mrkdwn", "text": f"*Next steps:*\n{next_steps}"}},
            {"type": "context", "elements": [{"type": "mrkdwn", "text": "Human review required before production changes."}]},
        ],
    }


def send_or_write_slack_payload(
    payload: dict[str, Any], outputs_dir: Path, webhook_url: str | None = None, dry_run: bool = True
) -> Path | str:
    """Write the Slack payload locally or send it to a webhook.

    The network path uses urllib to avoid adding dependencies. Tests use dry-run.
    """

    if dry_run or not webhook_url:
        outputs_dir.mkdir(parents=True, exist_ok=True)
        path = outputs_dir / "slack_payload_preview.json"
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path

    body = json.dumps(payload).encode("utf-8")
    req = request.Request(webhook_url, data=body, headers={"Content-Type": "application/json"})
    with request.urlopen(req, timeout=10) as response:  # nosec: case-study controlled usage
        return response.read().decode("utf-8")
