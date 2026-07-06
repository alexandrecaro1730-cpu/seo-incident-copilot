"""
Business Objective:
    Ensure the reviewer demo explicitly communicates mature AI-engineering concepts
    without overclaiming unimplemented production integrations.

Technical Objective:
    Import scripts/reviewer_demo.py and verify that the AI maturity map includes
    implemented, implemented-lite, design-ready, and extension-point capabilities.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REVIEWER_DEMO_PATH = PROJECT_ROOT / "scripts" / "reviewer_demo.py"


def load_reviewer_demo_module() -> ModuleType:
    """Load scripts/reviewer_demo.py as a testable Python module."""

    spec = importlib.util.spec_from_file_location("reviewer_demo", REVIEWER_DEMO_PATH)
    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    sys.modules["reviewer_demo"] = module
    spec.loader.exec_module(module)
    return module


def test_ai_maturity_timeline_highlights_core_ai_engineering_concepts() -> None:
    """The reviewer demo should name the AI-engineering concepts we want to showcase."""

    reviewer_demo = load_reviewer_demo_module()
    timeline = reviewer_demo.ai_maturity_timeline()

    concepts = {item["concept"] for item in timeline}

    assert "RAG / retrieval grounding" in concepts
    assert "Agent skills / controlled tools" in concepts
    assert "Structured output" in concepts
    assert "Cost-aware model routing" in concepts
    assert "Grounding / hallucination guard" in concepts
    assert "AI workflow metrics" in concepts
    assert "MCP / tool-server architecture" in concepts


def test_ai_maturity_timeline_does_not_overpromise_mcp_or_live_apis() -> None:
    """MCP should be shown as design-ready, not falsely marked as fully implemented."""

    reviewer_demo = load_reviewer_demo_module()
    timeline = reviewer_demo.ai_maturity_timeline()

    mcp_items = [item for item in timeline if "MCP" in item["concept"]]
    assert len(mcp_items) == 1
    assert mcp_items[0]["current_status"] == "design-ready"
    assert "not exposed as an MCP server" in mcp_items[0]["current_implementation"]

    live_api_phrases = [item["future_direction"] for item in timeline]
    assert any("GSC" in phrase or "DataForSEO" in phrase for phrase in live_api_phrases)


def test_quality_summary_extracts_pytest_and_ruff_summaries() -> None:
    """The demo should show readable quality gate summaries to the interviewer."""

    reviewer_demo = load_reviewer_demo_module()

    pytest_result = reviewer_demo.CommandResult(
        name="pytest",
        command=["python", "-m", "pytest"],
        return_code=0,
        stdout="============================= test session starts =============================\n"
        "============================== 35 passed in 0.42s ==============================",
        stderr="",
    )
    ruff_result = reviewer_demo.CommandResult(
        name="ruff",
        command=["python", "-m", "ruff", "check", "."],
        return_code=0,
        stdout="All checks passed!",
        stderr="",
    )

    assert reviewer_demo.quality_summary(pytest_result) == "35 passed in 0.42s"
    assert reviewer_demo.quality_summary(ruff_result) == "All checks passed!"
