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
from seo_incident_copilot.detectors.cannibalization import detect_keyword_cannibalization
from seo_incident_copilot.detectors.content_decay import detect_content_decay
from seo_incident_copilot.detectors.demand_shift import detect_demand_shift
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
    # trust in the automation. However, if ranking is stable while impressions drop,
    # we still surface a no-SEO-incident demand signal for context.
    if not rank_drop["triggered"]:
        gsc_metrics = load_gsc_metrics(config.data_dir, snapshot["gsc_file"])
        demand = detect_demand_shift(gsc_metrics)
        if demand["likely_demand_shift"]:
            return {
                "status": "no_seo_incident",
                "reason": (
                    "Ranking movement did not meet the SEO incident threshold, "
                    "but GSC-style demand signals declined while average position stayed stable."
                ),
                "snapshot": snapshot,
                "rank_drop": rank_drop,
                "deterministic_checks": {"demand": demand},
            }
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
    cannibalization = detect_keyword_cannibalization(snapshot, old_serp, new_serp)
    demand = detect_demand_shift(gsc_metrics)

    retriever = KnowledgeBaseRetriever(config.data_dir / "knowledge_base")
    retrieval_query = _build_retrieval_query(technical, intent, content, cannibalization, demand)
    playbooks = retriever.retrieve(retrieval_query, top_k=4)

    evidence_catalog = _build_evidence_catalog(
        snapshot,
        rank_drop,
        technical,
        intent,
        content,
        cannibalization,
        demand,
        page_audit,
        gsc_metrics,
        playbooks,
    )
    evidence_bundle = {
        "ranking_snapshot": snapshot,
        "rank_drop": rank_drop,
        "technical_checks": technical,
        "serp_intent_comparison": intent,
        "content_decay_checks": content,
        "cannibalization_checks": cannibalization,
        "demand_shift_checks": demand,
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
        cannibalization=cannibalization,
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
            "cannibalization": cannibalization,
            "demand": demand,
        },
        "analysis": analysis,
        "cost": cost,
    }

    payload = build_slack_payload(incident)
    slack_result = send_or_write_slack_payload(payload, config.outputs_dir, dry_run=dry_run_slack)
    incident["slack_result"] = str(slack_result)
    incident["incident_log"] = str(append_incident(config.outputs_dir, incident))
    return incident


def _build_retrieval_query(
    technical: dict[str, Any],
    intent: dict[str, Any],
    content: dict[str, Any],
    cannibalization: dict[str, Any],
    demand: dict[str, Any],
) -> str:
    """Create a compact query for the knowledge-base retriever."""

    terms = []
    if technical["has_technical_regression"]:
        terms.append("noindex robots canonical technical regression")
    if intent["likely_intent_shift"]:
        terms.append("intent shift listicle comparison review page")
    if content["likely_content_decay"]:
        terms.append("content decay pricing integrations faq comparison modules")
    if cannibalization["likely_cannibalization"]:
        terms.append("keyword cannibalization wrong ranking url internal links canonical")
    if demand["likely_demand_shift"]:
        terms.append("demand shift seasonality stable ranking impressions decline")
    return " ".join(terms) or "seo incident"


def _build_evidence_catalog(
    snapshot: dict[str, Any],
    rank_drop: dict[str, Any],
    technical: dict[str, Any],
    intent: dict[str, Any],
    content: dict[str, Any],
    cannibalization: dict[str, Any],
    demand: dict[str, Any],
    page_audit: dict[str, Any],
    gsc_metrics: dict[str, Any],
    playbooks: list[dict[str, Any]],
) -> dict[str, str]:
    """Create evidence IDs that the model must reference.

    Business explanation:
    Evidence IDs are the backbone of hallucination control. If the AI references
    an ID that does not exist, or makes a claim not supported by the evidence text,
    the grounding guard can block or downgrade trust.
    """

    catalog = {
        "RANK_001": (
            f"Keyword {snapshot.get('keyword')} dropped from position "
            f"{rank_drop['old_position']} to {rank_drop['new_position']} with "
            f"{snapshot.get('estimated_monthly_revenue_at_risk_eur')} EUR estimated monthly risk."
        ),
        "SERP_001": (
            f"Old SERP vendor ratio was {intent['old_summary']['vendor_ratio']} and new SERP vendor "
            f"ratio is {intent['new_summary']['vendor_ratio']}; old investigation ratio was "
            f"{intent['old_summary']['investigation_ratio']} and new investigation ratio is "
            f"{intent['new_summary']['investigation_ratio']}; intent-shift score is "
            f"{intent['intent_shift_score']}."
        ),
        "SERP_002": (
            f"New SERP result-type counts are {intent['new_summary']['type_counts']} and "
            f"intent counts are {intent['new_summary']['intent_counts']}."
        ),
        "PAGE_001": (
            f"Page modules are {page_audit.get('modules', [])}; missing modules are "
            f"{content.get('missing_modules', [])}."
        ),
        "PAGE_002": (
            f"Page age is {page_audit.get('last_updated_days_ago')} days, word count is "
            f"{page_audit.get('word_count')}, and internal links in are "
            f"{page_audit.get('internal_links_in')}."
        ),
        "GSC_001": (
            f"GSC metrics show clicks {gsc_metrics.get('clicks_28d_before')} to "
            f"{gsc_metrics.get('clicks_28d_after')}, impressions "
            f"{gsc_metrics.get('impressions_28d_before')} to "
            f"{gsc_metrics.get('impressions_28d_after')}, CTR "
            f"{gsc_metrics.get('ctr_before')} to {gsc_metrics.get('ctr_after')}, and average "
            f"position {gsc_metrics.get('average_position_before')} to "
            f"{gsc_metrics.get('average_position_after')}."
        ),
    }

    if technical["has_technical_regression"]:
        catalog["TECH_001"] = "; ".join(issue["message"] for issue in technical["issues"])

    if cannibalization["likely_cannibalization"]:
        catalog["CANNIBAL_001"] = (
            f"Primary URL {cannibalization['primary_url']} ranked before, but ranking URL after "
            f"is {cannibalization['ranking_url_after']}; competing URL is "
            f"{cannibalization['competing_url']}."
        )

    if demand["likely_demand_shift"]:
        catalog["DEMAND_001"] = (
            f"Impressions changed by {demand['impression_change_pct']} while average position "
            f"changed by {demand['position_delta']}; ranking_stable={demand['ranking_stable']}."
        )

    for playbook in playbooks:
        doc_id = str(playbook["doc_id"])
        text = str(playbook.get("text", ""))[:400]
        if "intent" in doc_id:
            catalog["PLAYBOOK_INTENT_001"] = f"Intent-shift playbook retrieved: {text}"
        elif "noindex" in doc_id:
            catalog["PLAYBOOK_NOINDEX_001"] = f"Noindex regression playbook retrieved: {text}"
        elif "content" in doc_id:
            catalog["PLAYBOOK_CONTENT_001"] = f"Content decay playbook retrieved: {text}"
        elif "cannibal" in doc_id:
            catalog["PLAYBOOK_CANNIBAL_001"] = f"Cannibalization playbook retrieved: {text}"
        elif "demand" in doc_id:
            catalog["PLAYBOOK_DEMAND_001"] = f"Demand-shift playbook retrieved: {text}"
        elif "security" in doc_id:
            catalog["PLAYBOOK_SECURITY_001"] = f"SEO AI security playbook retrieved: {text}"

    # Ensure common playbook evidence IDs exist when matching detectors fired.
    if intent["likely_intent_shift"]:
        catalog.setdefault("PLAYBOOK_INTENT_001", "Intent-shift playbook retrieved.")
    if content["likely_content_decay"]:
        catalog.setdefault("PLAYBOOK_CONTENT_001", "Content decay playbook retrieved.")
    if technical["has_technical_regression"]:
        catalog.setdefault("PLAYBOOK_NOINDEX_001", "Noindex or technical regression playbook retrieved.")
    if cannibalization["likely_cannibalization"]:
        catalog.setdefault("PLAYBOOK_CANNIBAL_001", "Keyword cannibalization playbook retrieved.")
    if demand["likely_demand_shift"]:
        catalog.setdefault("PLAYBOOK_DEMAND_001", "Demand-shift playbook retrieved.")

    return catalog
