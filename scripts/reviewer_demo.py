"""
Business Objective:
    Provide a one-command reviewer demo for the YOYABA SEO AI Engineer case study.

    The command is designed for an interviewer who wants to understand the project
    quickly without manually running every scenario. It validates code quality,
    exercises normal SEO incidents and AI-failure cases, and summarizes business
    metrics such as model-tier usage, average cost, grounding quality, and
    hallucination-risk signals.

    It also prints an AI engineering maturity timeline so the reviewer can see
    where RAG, agent skills, structured outputs, model routing, grounding,
    observability, MCP readiness, and future live integrations fit into the system.

Technical Objective:
    Run pytest, Ruff, and every demo scenario from one Python entry point. Parse the
    JSON output from each scenario, calculate aggregate metrics, and write both a
    human-readable Markdown report and a machine-readable JSON report.

    The script uses only the Python standard library so it stays portable and does
    not introduce extra dependencies for reviewers.
"""

from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "reviewer_demo"

SCENARIOS = [
    "no_trigger",
    "demand_drop_not_seo_issue",
    "technical_regression",
    "canonical_regression",
    "content_decay",
    "keyword_cannibalization",
    "intent_shift",
    "timeout_fallback",
    "hallucinated_competitor_claim",
    "action_mismatch",
    "invalid_schema_output",
    "overconfident_weak_evidence",
]

AI_ENGINEERING_TIMELINE = [
    {
        "stage": "1. Quality gates",
        "concept": "Testability / CI readiness",
        "current_status": "implemented",
        "current_implementation": "pytest + Ruff run before scenarios",
        "future_direction": "Move the same gates into GitHub Actions.",
    },
    {
        "stage": "2. Evidence collection",
        "concept": "Data contracts / tool boundaries",
        "current_status": "implemented",
        "current_implementation": "Ranking, SERP, GSC, page-audit, and playbook fixtures",
        "future_direction": "Connect the interfaces to GSC, DataForSEO, crawler exports, and logs.",
    },
    {
        "stage": "3. Deterministic SEO skills",
        "concept": "Agent skills / controlled tools",
        "current_status": "implemented",
        "current_implementation": "Rank-drop, noindex, canonical, demand, and cannibalization checks",
        "future_direction": "Expose the same skills through an internal tool registry with permissions.",
    },
    {
        "stage": "4. Playbook retrieval",
        "concept": "RAG / retrieval grounding",
        "current_status": "implemented-lite",
        "current_implementation": "Local SEO playbook retrieval from data/knowledge_base",
        "future_direction": "Upgrade to embedding search over client playbooks and incident memory.",
    },
    {
        "stage": "5. Model selection",
        "concept": "Cost-aware model routing",
        "current_status": "implemented",
        "current_implementation": "cheap / middle / expensive tier routing by evidence and impact",
        "future_direction": "Track real token cost, latency, and confidence by provider/model.",
    },
    {
        "stage": "6. AI analysis",
        "concept": "Structured output",
        "current_status": "implemented-as-fixtures",
        "current_implementation": "Manual prompts + schema-validated JSON model-output fixtures",
        "future_direction": "Replace fixtures with strict JSON-schema outputs from live LLM APIs.",
    },
    {
        "stage": "7. Safety layer",
        "concept": "Grounding / hallucination guard",
        "current_status": "implemented",
        "current_implementation": "Unsupported-claim, action-mismatch, invalid-schema, overconfidence checks",
        "future_direction": "Add claim extraction, contradiction checks, and retrieval citations.",
    },
    {
        "stage": "8. Delivery layer",
        "concept": "Slack alerting / human-in-the-loop",
        "current_status": "implemented-dry-run",
        "current_implementation": "Slack-compatible payload preview + human-review flag",
        "future_direction": "Connect a Slack webhook/app and add owner routing / escalation rules.",
    },
    {
        "stage": "9. Observability",
        "concept": "AI workflow metrics",
        "current_status": "implemented",
        "current_implementation": "Cost, model share, grounding, hallucination-risk, warning-code metrics",
        "future_direction": "Persist run history to warehouse dashboards and alert on drift/failure spikes.",
    },
    {
        "stage": "10. MCP readiness",
        "concept": "MCP / tool-server architecture",
        "current_status": "design-ready",
        "current_implementation": "Python skills are cleanly separated but not exposed as an MCP server",
        "future_direction": "Expose approved SEO skills as MCP tools with auth, logs, and rate limits.",
    },
]


@dataclass(frozen=True)
class CommandResult:
    """Store subprocess metadata for quality gates and scenario runs."""

    name: str
    command: list[str]
    return_code: int
    stdout: str
    stderr: str

    @property
    def passed(self) -> bool:
        """Return True when the subprocess finished successfully."""

        return self.return_code == 0


def run_command(name: str, command: list[str]) -> CommandResult:
    """Run one validation or demo step exactly as a reviewer would run it."""

    completed = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    return CommandResult(
        name=name,
        command=command,
        return_code=completed.returncode,
        stdout=completed.stdout.strip(),
        stderr=completed.stderr.strip(),
    )


def quality_summary(result: CommandResult) -> str:
    """
    Business explanation:
        Make the quality gate output more useful for reviewers by showing the real
        pytest or Ruff summary, not only PASS/FAIL.

    Technical explanation:
        Extract the most relevant final summary line from pytest or Ruff output.
        Fall back safely if the tool output format changes.
    """

    combined_output = "\n".join(
        line.strip()
        for line in [result.stdout, result.stderr]
        if line.strip()
    )

    if result.name == "pytest":
        for line in reversed(combined_output.splitlines()):
            clean_line = line.strip()
            if " passed" in clean_line or " failed" in clean_line or " error" in clean_line:
                return clean_line.replace("=", "").strip()

    if result.name == "ruff" and "All checks passed!" in combined_output:
        return "All checks passed!"

    return "OK" if result.passed else "See failure output"


def scenario_command(scenario: str) -> list[str]:
    """Run a scenario in Slack dry-run mode."""

    return [
        sys.executable,
        "-m",
        "seo_incident_copilot.main",
        "--scenario",
        scenario,
        "--dry-run-slack",
    ]


def extract_json_from_stdout(stdout: str) -> dict[str, Any]:
    """Parse scenario output into structured data without crashing the demo."""

    try:
        parsed = json.loads(stdout)
    except json.JSONDecodeError as exc:
        return {"status": "parse_error", "error": str(exc), "raw_stdout": stdout}

    if not isinstance(parsed, dict):
        return {
            "status": "parse_error",
            "error": "Scenario output was valid JSON but not an object.",
            "raw_stdout": stdout,
        }

    return parsed


def summarize_scenario(scenario: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Extract reviewer-relevant fields from a verbose scenario payload."""

    analysis = payload.get("analysis", {})
    cost = payload.get("cost", {})
    grounding = analysis.get("grounding", {})
    rank_drop = payload.get("rank_drop", {})
    grounding_warnings = grounding.get("warnings", []) or []
    warning_codes = grounding.get("warning_codes", []) or []

    return {
        "scenario": scenario,
        "status": payload.get("status"),
        "reason": payload.get("reason"),
        "positions_lost": rank_drop.get("positions_lost"),
        "severity": rank_drop.get("severity"),
        "issue_type": analysis.get("issue_type"),
        "confidence_score": analysis.get("confidence_score"),
        "model_tier": analysis.get("model_tier"),
        "estimated_cost_eur": cost.get("estimated_cost_eur"),
        "grounding_score": grounding.get("grounding_score"),
        "grounding_passed": grounding.get("grounding_passed"),
        "grounding_warning_count": len(grounding_warnings),
        "warning_codes": warning_codes,
        "hallucination_risk_score": grounding.get("hallucination_risk_score"),
        "hallucination_risk_level": grounding.get("hallucination_risk_level"),
        "human_review_required": analysis.get("requires_human_review"),
        "fallback_reason": analysis.get("fallback_reason"),
        "validation_error_count": len(analysis.get("validation_errors", []) or []),
        "recommended_action": analysis.get("recommended_action"),
    }


def _safe_float(value: Any) -> float | None:
    """Convert numeric-looking values to float while preserving missing values."""

    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _percentage(numerator: int | float, denominator: int | float) -> float:
    """Return a decimal percentage between 0 and 1."""

    if denominator == 0:
        return 0.0

    return float(numerator) / float(denominator)


def calculate_reviewer_metrics(summaries: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Business explanation:
        Calculate reviewer-facing metrics that prove the system is not only a demo,
        but an operating model: model usage, cost, grounding, hallucination risk,
        invalid-output rate, contradiction rate, and deterministic resolution rate.

    Technical explanation:
        Metrics are calculated from scenario summary dictionaries, which makes this
        function easy to unit test without invoking subprocesses.
    """

    total_scenarios = len(summaries)
    incident_summaries = [
        item for item in summaries if item.get("status") == "incident_detected"
    ]
    analyzed_count = len(incident_summaries)

    model_counts = Counter(
        item["model_tier"] for item in incident_summaries if item.get("model_tier")
    )
    issue_counts = Counter(
        item["issue_type"] for item in incident_summaries if item.get("issue_type")
    )
    severity_counts = Counter(item["severity"] for item in summaries if item.get("severity"))
    warning_code_counts = Counter(
        code for item in incident_summaries for code in item.get("warning_codes", [])
    )

    costs = [
        value
        for value in (
            _safe_float(item.get("estimated_cost_eur")) for item in incident_summaries
        )
        if value is not None
    ]
    confidences = [
        value
        for value in (
            _safe_float(item.get("confidence_score")) for item in incident_summaries
        )
        if value is not None
    ]
    grounding_scores = [
        value
        for value in (
            _safe_float(item.get("grounding_score")) for item in incident_summaries
        )
        if value is not None
    ]
    risk_scores = [
        value
        for value in (
            _safe_float(item.get("hallucination_risk_score"))
            for item in incident_summaries
        )
        if value is not None
    ]

    grounding_pass_count = sum(
        1 for item in incident_summaries if item.get("grounding_passed")
    )
    human_review_count = sum(
        1 for item in incident_summaries if item.get("human_review_required") is True
    )
    fallback_count = sum(
        1 for item in incident_summaries if item.get("issue_type") == "unknown"
    )
    validation_error_count = sum(
        1 for item in incident_summaries if item.get("validation_error_count", 0) > 0
    )
    warning_scenario_count = sum(
        1
        for item in incident_summaries
        if int(item.get("grounding_warning_count") or 0) > 0
    )
    hallucination_risk_count = sum(
        1
        for item in incident_summaries
        if (_safe_float(item.get("hallucination_risk_score")) or 0) > 0
        or item.get("grounding_passed") is False
        or int(item.get("grounding_warning_count") or 0) > 0
    )
    deterministic_resolution_count = sum(
        1
        for item in summaries
        if item.get("status") in {"no_incident", "no_seo_incident"}
        or (
            item.get("status") == "incident_detected"
            and item.get("model_tier") == "cheap"
            and item.get("issue_type") == "technical_regression"
        )
    )

    average_grounding = sum(grounding_scores) / len(grounding_scores) if grounding_scores else 0.0
    average_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0.0

    return {
        "total_scenarios": total_scenarios,
        "incident_count": analyzed_count,
        "no_incident_count": total_scenarios - analyzed_count,
        "incident_detection_rate": _percentage(analyzed_count, total_scenarios),
        "no_alert_rate": _percentage(total_scenarios - analyzed_count, total_scenarios),
        "deterministic_resolution_rate": _percentage(
            deterministic_resolution_count,
            total_scenarios,
        ),
        "model_usage_counts": dict(model_counts),
        "model_usage_share": {
            tier: _percentage(count, analyzed_count)
            for tier, count in sorted(model_counts.items())
        },
        "issue_type_counts": dict(issue_counts),
        "severity_counts": dict(severity_counts),
        "warning_code_counts": dict(warning_code_counts),
        "total_estimated_cost_eur": sum(costs),
        "average_cost_per_incident_eur": sum(costs) / len(costs) if costs else 0.0,
        "average_cost_per_scenario_eur": sum(costs) / total_scenarios
        if total_scenarios
        else 0.0,
        "average_confidence_score": sum(confidences) / len(confidences)
        if confidences
        else 0.0,
        "average_grounding_score": average_grounding,
        "average_hallucination_risk_score": average_risk,
        "grounding_pass_rate": _percentage(grounding_pass_count, analyzed_count),
        "human_review_rate": _percentage(human_review_count, analyzed_count),
        "timeout_or_unknown_fallback_rate": _percentage(fallback_count, analyzed_count),
        "invalid_schema_rate": _percentage(validation_error_count, analyzed_count),
        "warning_scenario_rate": _percentage(warning_scenario_count, analyzed_count),
        "estimated_hallucination_risk_rate": _percentage(
            hallucination_risk_count,
            analyzed_count,
        ),
        "unsupported_claim_rate": _percentage(
            warning_code_counts.get("unsupported_claim", 0),
            analyzed_count,
        ),
        "action_mismatch_rate": _percentage(
            warning_code_counts.get("issue_action_mismatch", 0),
            analyzed_count,
        ),
    }


def ai_maturity_timeline() -> list[dict[str, str]]:
    """
    Business explanation:
        Return the implementation timeline that explains where mature AI-engineering
        concepts sit in the workflow without overpromising that every future-facing
        capability is already fully implemented.

    Technical explanation:
        Keeping the map as data makes it easy to print in the terminal, serialize
        to JSON, test, and reuse in the Markdown reviewer report.
    """

    return AI_ENGINEERING_TIMELINE


def format_percent(value: Any) -> str:
    """Format a decimal score as a reviewer-friendly percentage."""

    numeric = _safe_float(value)
    if numeric is None:
        return "-"

    return f"{numeric * 100:.0f}%"


def format_cost(value: Any) -> str:
    """Format a cost value as EUR."""

    numeric = _safe_float(value)
    if numeric is None:
        return "-"

    return f"€{numeric:.4f}"


def format_count_dict(counts: dict[str, int]) -> str:
    """Format small count dictionaries for terminal and Markdown output."""

    if not counts:
        return "-"

    return ", ".join(f"{key}: {value}" for key, value in sorted(counts.items()))


def format_share_dict(shares: dict[str, float]) -> str:
    """Format model-usage percentages for reports."""

    if not shares:
        return "-"

    return ", ".join(f"{key}: {format_percent(value)}" for key, value in sorted(shares.items()))


def write_reports(
    quality_results: list[CommandResult],
    scenario_summaries: list[dict[str, Any]],
    raw_scenarios: dict[str, dict[str, Any]],
    aggregate_metrics: dict[str, Any],
) -> None:
    """Write reviewer-friendly Markdown and JSON reports."""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    maturity_timeline = ai_maturity_timeline()

    report_json = {
        "quality_results": [
            {
                "name": result.name,
                "command": " ".join(result.command),
                "passed": result.passed,
                "return_code": result.return_code,
                "summary": quality_summary(result),
            }
            for result in quality_results
        ],
        "ai_engineering_timeline": maturity_timeline,
        "aggregate_metrics": aggregate_metrics,
        "scenario_summaries": scenario_summaries,
        "raw_scenarios": raw_scenarios,
    }

    (OUTPUT_DIR / "reviewer_summary.json").write_text(
        json.dumps(report_json, indent=2),
        encoding="utf-8",
    )

    lines = [
        "# SEO Incident Copilot — Reviewer Demo Summary",
        "",
        "## Quality Gates",
        "",
        "| Check | Result | Summary |",
        "|---|---|---|",
    ]

    for result in quality_results:
        status = "PASS" if result.passed else "FAIL"
        lines.append(f"| `{result.name}` | {status} | {quality_summary(result)} |")

    lines.extend(
        [
            "",
            "## AI Engineering Maturity Timeline",
            "",
            "| Pipeline Stage | Concept | Current Status | Current Implementation | Future Direction |",
            "|---|---|---|---|---|",
        ]
    )

    for item in maturity_timeline:
        lines.append(
            "| "
            f"{item['stage']} | "
            f"{item['concept']} | "
            f"{item['current_status']} | "
            f"{item['current_implementation']} | "
            f"{item['future_direction']} |"
        )

    lines.extend(
        [
            "",
            "## Aggregate Metrics",
            "",
            f"- Incident detection rate: {format_percent(aggregate_metrics['incident_detection_rate'])}",
            f"- No-alert rate: {format_percent(aggregate_metrics['no_alert_rate'])}",
            (
                "- Deterministic resolution rate: "
                f"{format_percent(aggregate_metrics['deterministic_resolution_rate'])}"
            ),
            (
                "- Average cost per incident: "
                f"{format_cost(aggregate_metrics['average_cost_per_incident_eur'])}"
            ),
            f"- Total estimated demo cost: {format_cost(aggregate_metrics['total_estimated_cost_eur'])}",
            f"- Model usage share: {format_share_dict(aggregate_metrics['model_usage_share'])}",
            f"- Average confidence: {format_percent(aggregate_metrics['average_confidence_score'])}",
            f"- Grounding pass rate: {format_percent(aggregate_metrics['grounding_pass_rate'])}",
            (
                "- Estimated hallucination-risk scenario rate: "
                f"{format_percent(aggregate_metrics['estimated_hallucination_risk_rate'])}"
            ),
            f"- Unsupported-claim rate: {format_percent(aggregate_metrics['unsupported_claim_rate'])}",
            f"- Action-mismatch rate: {format_percent(aggregate_metrics['action_mismatch_rate'])}",
            f"- Invalid-schema rate: {format_percent(aggregate_metrics['invalid_schema_rate'])}",
            f"- Human-review rate: {format_percent(aggregate_metrics['human_review_rate'])}",
            f"- Warning codes: {format_count_dict(aggregate_metrics['warning_code_counts'])}",
            "",
            "## Scenario Summary",
            "",
            (
                "| Scenario | Status | Issue Type | Severity | Model | Confidence | Grounding | "
                "Risk | Cost | Warnings |"
            ),
            "|---|---|---|---|---|---:|---:|---:|---:|---|",
        ]
    )

    for summary in scenario_summaries:
        lines.append(
            "| "
            f"`{summary['scenario']}` | "
            f"{summary.get('status') or '-'} | "
            f"{summary.get('issue_type') or '-'} | "
            f"{summary.get('severity') or '-'} | "
            f"{summary.get('model_tier') or '-'} | "
            f"{format_percent(summary.get('confidence_score'))} | "
            f"{format_percent(summary.get('grounding_score'))} | "
            f"{format_percent(summary.get('hallucination_risk_score'))} | "
            f"{format_cost(summary.get('estimated_cost_eur'))} | "
            f"{', '.join(summary.get('warning_codes') or []) or '-'} |"
        )

    lines.extend(
        [
            "",
            "## Key Takeaway",
            "",
            (
                "The system demonstrates deterministic SEO checks first, cost-aware model routing, "
                "RAG-style playbook grounding, structured AI output, hallucination-risk examples, "
                "controlled timeout fallback, Slack-ready incident communication, and a clear path "
                "toward MCP/live API productionization without claiming those future layers are already "
                "fully implemented."
            ),
            "",
            "## Generated Files",
            "",
            f"- `{OUTPUT_DIR / 'reviewer_summary.md'}`",
            f"- `{OUTPUT_DIR / 'reviewer_summary.json'}`",
            "- `outputs/slack_payload_preview.json`",
            "- `outputs/incidents.jsonl`",
            "",
        ]
    )

    (OUTPUT_DIR / "reviewer_summary.md").write_text("\n".join(lines), encoding="utf-8")


def print_terminal_summary(
    quality_results: list[CommandResult],
    scenario_summaries: list[dict[str, Any]],
    aggregate_metrics: dict[str, Any],
) -> None:
    """Print an immediate executive summary for the terminal."""

    print("\nSEO Incident Copilot — Reviewer Demo")
    print("=" * 80)

    print("\n1) Quality gates")
    for result in quality_results:
        status = "PASS" if result.passed else "FAIL"
        summary = quality_summary(result)
        print(f"  {status:<4} {result.name} — {summary}")

    print("\n2) AI engineering maturity timeline")
    for item in ai_maturity_timeline():
        print(
            "  "
            f"{item['stage']:<27} "
            f"{item['concept']:<34} "
            f"status={item['current_status']}"
        )
        print(f"      now:  {item['current_implementation']}")
        print(f"      next: {item['future_direction']}")

    print("\n3) Scenario outcomes")
    for summary in scenario_summaries:
        print(
            "  "
            f"{summary['scenario']:<34} "
            f"status={summary.get('status') or '-':<18} "
            f"issue={summary.get('issue_type') or '-':<24} "
            f"model={summary.get('model_tier') or '-':<10} "
            f"risk={format_percent(summary.get('hallucination_risk_score')):<5} "
            f"cost={format_cost(summary.get('estimated_cost_eur'))}"
        )

    print("\n4) Aggregate operating metrics")
    print(
        "  Incident detection rate:          "
        f"{format_percent(aggregate_metrics['incident_detection_rate'])}"
    )
    print(f"  No-alert rate:                    {format_percent(aggregate_metrics['no_alert_rate'])}")
    print(
        "  Deterministic resolution rate:    "
        f"{format_percent(aggregate_metrics['deterministic_resolution_rate'])}"
    )
    print(
        "  Average cost per incident:        "
        f"{format_cost(aggregate_metrics['average_cost_per_incident_eur'])}"
    )
    print(
        "  Total estimated demo cost:        "
        f"{format_cost(aggregate_metrics['total_estimated_cost_eur'])}"
    )
    print(
        "  Model usage share:                "
        f"{format_share_dict(aggregate_metrics['model_usage_share'])}"
    )
    print(
        "  Average confidence:               "
        f"{format_percent(aggregate_metrics['average_confidence_score'])}"
    )
    print(
        "  Grounding pass rate:              "
        f"{format_percent(aggregate_metrics['grounding_pass_rate'])}"
    )
    print(
        "  Hallucination-risk scenario rate: "
        f"{format_percent(aggregate_metrics['estimated_hallucination_risk_rate'])}"
    )
    print(
        "  Unsupported-claim rate:           "
        f"{format_percent(aggregate_metrics['unsupported_claim_rate'])}"
    )
    print(
        "  Action-mismatch rate:             "
        f"{format_percent(aggregate_metrics['action_mismatch_rate'])}"
    )
    print(
        "  Invalid-schema rate:              "
        f"{format_percent(aggregate_metrics['invalid_schema_rate'])}"
    )
    print(
        "  Human-review rate:                "
        f"{format_percent(aggregate_metrics['human_review_rate'])}"
    )
    print(
        "  Warning codes:                    "
        f"{format_count_dict(aggregate_metrics['warning_code_counts'])}"
    )

    print("\n5) Generated reviewer artifacts")
    print(f"  {OUTPUT_DIR / 'reviewer_summary.md'}")
    print(f"  {OUTPUT_DIR / 'reviewer_summary.json'}")
    print(f"  {PROJECT_ROOT / 'outputs' / 'slack_payload_preview.json'}")
    print(f"  {PROJECT_ROOT / 'outputs' / 'incidents.jsonl'}")

    print("\nNote:")
    print(
        "  MCP and live APIs are marked as design-ready/extension points, not claimed as "
        "fully implemented. The implemented core is the SEO evidence pipeline, "
        "tool-like skills, routing, structured outputs, grounding, and observability."
    )


def main() -> int:
    """Run the full reviewer experience in one command."""

    quality_results = [
        run_command("pytest", [sys.executable, "-m", "pytest"]),
        run_command("ruff", [sys.executable, "-m", "ruff", "check", "."]),
    ]

    raw_scenarios: dict[str, dict[str, Any]] = {}
    scenario_summaries: list[dict[str, Any]] = []
    scenario_command_results: list[CommandResult] = []

    for scenario in SCENARIOS:
        result = run_command(name=f"scenario:{scenario}", command=scenario_command(scenario))
        scenario_command_results.append(result)

        payload = extract_json_from_stdout(result.stdout)
        raw_scenarios[scenario] = payload
        scenario_summaries.append(summarize_scenario(scenario, payload))

    aggregate_metrics = calculate_reviewer_metrics(scenario_summaries)
    write_reports(
        quality_results=quality_results,
        scenario_summaries=scenario_summaries,
        raw_scenarios=raw_scenarios,
        aggregate_metrics=aggregate_metrics,
    )
    print_terminal_summary(
        quality_results=quality_results,
        scenario_summaries=scenario_summaries,
        aggregate_metrics=aggregate_metrics,
    )

    all_results = quality_results + scenario_command_results
    failed_results = [result for result in all_results if not result.passed]

    if failed_results:
        print("\nFailures detected:")
        for result in failed_results:
            print(f"\n--- {result.name} ---")
            print(result.stderr or result.stdout or "No output captured.")
        return 1

    print("\nReviewer demo completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
