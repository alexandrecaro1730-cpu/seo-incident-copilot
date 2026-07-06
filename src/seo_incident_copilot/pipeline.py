"""
Business objective:
Orchestrate the complete SEO incident workflow from rank movement to Slack-ready
recommendation.

Coding objective:
Keep the pipeline readable and testable. Every step returns structured data, which
makes failures easier to isolate during the technical interview.
"""

from __future__ import annotations

from typing import Any

from seo_incident_copilot.ai.llm_client import ManualFixtureLLMClient
from seo_incident_copilot.ai.model_router import choose_model_tier
from seo_incident_copilot.ai.prompt_manager import PromptManager
from seo_incident_copilot.ai.structured_analysis import run_structured_analysis
from seo_incident_copilot.config import AppConfig
from seo_incident_copilot.connectors.page_audit_source import load_gsc_metrics, load_page_audit
from seo_incident_copilot.connectors.ranking_source import load_ranking_snapshot
from seo_incident_copilot.connectors.serp_source import load_serp
from seo_incident_copilot.connectors.slack_client import build_slack_payload, send_or_write_slack_payload
from seo_incident_copilot.detectors.content_decay import detect_content_decay
from seo_incident_copilot.detectors.intent_shift import compare_serp_intent
from seo_incident_copilot.detectors.rank_drop import detect_rank_drop
from seo_incident_copilot.detectors.technical_regression import detect_technical_regression
from seo_incident_copilot.observability.cost_tracker import estimate_analysis_cost
from seo_incident_copilot.rag.retriever import KnowledgeBaseRetriever
from seo_incident_copilot.storage.incident_store import append_incident


def run_pipeline(config: AppConfig, scenario: str, dry_run_slack: bool = True) -> dict[str, Any]:
    """Run the complete incident pipeline for one scenario."""

    snapshot = load_ranking_snapshot(config.data_dir, scenario)
    rank_drop = detect_rank_drop(snapshot, threshold=config.rank_drop_threshold)

    # Business explanation:
    # Not every movement deserves an alert. Avoiding false positives preserves team
    # trust in the automation.
    if not rank_drop["triggered"]:
        return {
            "status": "no_incident",
            "reason": "Rank movement did not meet trigger threshold.",
            "snapshot": snapshot,
            "rank_drop": rank_drop,
        }

    old_serp = load_serp(config.data_dir, snapshot["old_serp_file"])
    new_serp = load_serp(config.data_dir, snapshot["new_serp_file"])
    page_audit = load_page_audit(config.data_dir, snapshot["page_audit_file"])
    gsc_metrics = load_gsc_metrics(config.data_dir, snapshot["gsc_file"])

    technical = detect_technical_regression(page_audit)
    intent = compare_serp_intent(old_serp, new_serp)
    content = detect_content_decay(page_audit, new_serp)

    retriever = KnowledgeBaseRetriever(config.data_dir / "knowledge_base")
    retrieval_query = _build_retrieval_query(technical, intent, content)
    playbooks = retriever.retrieve(retrieval_query, top_k=3)

    evidence_catalog = _build_evidence_catalog(snapshot, rank_drop, technical, intent, content, page_audit, gsc_metrics, playbooks)
    evidence_bundle = {
        "ranking_snapshot": snapshot,
        "rank_drop": rank_drop,
        "technical_checks": technical,
        "serp_intent_comparison": intent,
        "content_decay_checks": content,
        "page_audit_summary": page_audit,
        "gsc_metrics": gsc_metrics,
        "retrieved_playbooks": playbooks,
        "evidence_catalog": evidence_catalog,
    }

    tier = choose_model_tier(
        snapshot=snapshot,
        technical=technical,
        intent=intent,
        content=content,
        high_revenue_risk_eur=config.high_revenue_risk_eur,
    )

    prompt_manager = PromptManager(config.prompts_dir)
    llm_client = ManualFixtureLLMClient(config.model_outputs_dir)
    analysis = run_structured_analysis(
        scenario=scenario,
        tier=tier,
        evidence_bundle=evidence_bundle,
        evidence_catalog=evidence_catalog,
        prompt_manager=prompt_manager,
        llm_client=llm_client,
        force_timeout=bool(snapshot.get("force_timeout")),
    )

    cost = estimate_analysis_cost(analysis["model_tier"], config.model_cost_eur_per_analysis or {})
    incident = {
        "status": "incident_detected",
        "snapshot": snapshot,
        "rank_drop": rank_drop,
        "deterministic_checks": {
            "technical": technical,
            "intent": intent,
            "content": content,
        },
        "analysis": analysis,
        "cost": cost,
    }

    payload = build_slack_payload(incident)
    slack_result = send_or_write_slack_payload(payload, config.outputs_dir, dry_run=dry_run_slack)
    incident["slack_result"] = str(slack_result)
    incident["incident_log"] = str(append_incident(config.outputs_dir, incident))
    return incident


def _build_retrieval_query(technical: dict[str, Any], intent: dict[str, Any], content: dict[str, Any]) -> str:
    """Create a compact query for the knowledge-base retriever."""

    terms = []
    if technical["has_technical_regression"]:
        terms.append("noindex robots canonical technical regression")
    if intent["likely_intent_shift"]:
        terms.append("intent shift listicle comparison review page")
    if content["likely_content_decay"]:
        terms.append("content decay pricing integrations faq comparison modules")
    return " ".join(terms) or "seo incident"


def _build_evidence_catalog(
    snapshot: dict[str, Any],
    rank_drop: dict[str, Any],
    technical: dict[str, Any],
    intent: dict[str, Any],
    content: dict[str, Any],
    page_audit: dict[str, Any],
    gsc_metrics: dict[str, Any],
    playbooks: list[dict[str, Any]],
) -> dict[str, str]:
    """Create evidence IDs that the model must reference.

    Business explanation:
    Evidence IDs are the backbone of hallucination control. If the AI references
    an ID that does not exist, the grounding guard can block or downgrade trust.
    """

    catalog = {
        "RANK_001": f"Keyword dropped from position {rank_drop['old_position']} to {rank_drop['new_position']}.",
        "SERP_001": f"Intent-shift score is {intent['intent_shift_score']} with top-result composition changing.",
        "SERP_002": f"New SERP vendor ratio is {intent['new_summary']['vendor_ratio']} and investigation ratio is {intent['new_summary']['investigation_ratio']}.",
        "PAGE_001": f"Page modules are {page_audit.get('modules', [])}.",
        "PAGE_002": f"Page age is {page_audit.get('last_updated_days_ago')} days, word count is {page_audit.get('word_count')}, and internal links in are {page_audit.get('internal_links_in')}.",
        "GSC_001": f"GSC metrics show clicks {gsc_metrics.get('clicks_28d_before')} to {gsc_metrics.get('clicks_28d_after')} and impressions {gsc_metrics.get('impressions_28d_before')} to {gsc_metrics.get('impressions_28d_after')}.",
    }

    if technical["has_technical_regression"]:
        catalog["TECH_001"] = "; ".join(issue["message"] for issue in technical["issues"])

    for playbook in playbooks:
        doc_id = str(playbook["doc_id"])
        if "intent" in doc_id:
            catalog["PLAYBOOK_INTENT_001"] = "Intent-shift playbook retrieved."
        elif "noindex" in doc_id:
            catalog["PLAYBOOK_NOINDEX_001"] = "Noindex regression playbook retrieved."
        elif "content" in doc_id:
            catalog["PLAYBOOK_CONTENT_001"] = "Content decay playbook retrieved."
        elif "security" in doc_id:
            catalog["PLAYBOOK_SECURITY_001"] = "SEO AI security playbook retrieved."

    # Ensure common playbook evidence IDs exist when matching detectors fired.
    if intent["likely_intent_shift"]:
        catalog.setdefault("PLAYBOOK_INTENT_001", "Intent-shift playbook retrieved.")
    if content["likely_content_decay"]:
        catalog.setdefault("PLAYBOOK_CONTENT_001", "Content decay playbook retrieved.")
    if technical["has_technical_regression"]:
        catalog.setdefault("PLAYBOOK_NOINDEX_001", "Noindex regression playbook retrieved.")

    return catalog
