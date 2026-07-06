# AI Engineering Maturity Map

This document explains how the case-study project uses mature AI-engineering concepts without overstating what is implemented in the local demo.

The important design principle is:

> The LLM is one controlled reasoning component inside an SEO evidence pipeline. It is not the whole system.

## Implementation map

| Capability | Current implementation | Status | Production direction |
|---|---|---|---|
| Data contracts | Fixture JSON for ranking, SERP, GSC, page audits, and model outputs | Implemented | Replace fixtures with API connectors while keeping the same schemas |
| Agent skills / tool boundaries | Deterministic Python modules for ranking drops, noindex, canonical checks, demand shift, content decay, cannibalization, model routing, grounding, Slack payloads, and incident logging | Implemented | Expose the same skills through a permissions-aware tool registry |
| RAG / retrieval grounding | Local SEO playbook retrieval from `data/knowledge_base/` | Implemented-lite | Upgrade to embedding search over client playbooks, previous incidents, strategy docs, and SOPs |
| Structured output | Manual prompts plus schema-validated JSON model-output fixtures | Implemented-as-fixtures | Replace fixtures with live LLM calls using strict JSON-schema output |
| Cost-aware routing | Cheap/middle/expensive model-tier selection based on issue type, ambiguity, and business impact | Implemented | Track real token cost, latency, retry cost, and quality per provider/model |
| Hallucination / grounding guard | Unsupported-claim, unknown evidence ID, action mismatch, invalid schema, and overconfidence checks | Implemented | Add claim extraction, contradiction detection, retrieval citations, and optional model-based verification |
| Observability | Reviewer demo metrics, model usage share, warning codes, estimated cost, grounding rates, JSONL incident logs | Implemented | Push run history to warehouse dashboards and alert on drift/failure spikes |
| Slack alerting | Dry-run Slack-compatible payload generation | Implemented-dry-run | Connect Slack webhook/app, owner routing, escalation rules, and incident acknowledgement |
| MCP readiness | Python skills are separated in a way that could be exposed as MCP tools | Design-ready | Add an MCP server exposing approved SEO tools with auth, rate limits, and audit logs |
| Live API integrations | Not required for deterministic case-study review | Extension point | Connect Google Search Console, DataForSEO, crawler exports, server logs, CMS APIs, and warehouse tables |

## Why the project uses fixtures first

The project intentionally uses local fixtures instead of live APIs for the case-study demo.

This makes the workflow:

- deterministic
- easy to test
- safe to review
- independent of credentials
- easy to run in an interview
- focused on business logic and failure modes

The same interfaces can later be connected to live systems.

## How to describe RAG in the interview

The current RAG layer is a lightweight playbook retriever. It retrieves approved SEO guidance from local markdown playbooks and makes that guidance available to the analysis layer.

A good interview explanation:

> I kept RAG local and deterministic for the case study. In production, I would replace the simple retriever with embedding-based retrieval over client playbooks, previous incidents, SEO SOPs, and strategic documentation.

## How to describe MCP in the interview

The project does not claim to run an MCP server. Instead, it is MCP-ready because the core skills are already separated behind clear Python interfaces.

A good interview explanation:

> I did not add a fake MCP server just to name-drop MCP. I structured the SEO skills as clean tool-like interfaces first. In production, those skills could be exposed as MCP tools with permissions, audit logs, and rate limits.

Example future MCP tools:

```text
fetch_ranking_snapshot
compare_serp_intent
inspect_page_indexability
detect_canonical_regression
detect_keyword_cannibalization
retrieve_seo_playbook
route_model_tier
validate_model_output
generate_slack_alert
log_incident
```

## How to describe agent skills

The system is agentic, but it is not an uncontrolled autonomous chatbot.

The pipeline orchestrates controlled skills:

```text
collect evidence -> run deterministic SEO checks -> retrieve playbook guidance -> route model tier -> validate structured AI output -> ground against evidence -> generate Slack alert -> log incident
```

A good interview explanation:

> The agent is the workflow, not a free-running chatbot. Each skill has a defined input, output, and test coverage. The LLM receives constrained evidence and its output must pass schema, grounding, and business-logic checks.

## How to describe hallucination metrics

The reviewer demo includes intentionally adversarial scenarios. A lower grounding pass rate is expected in those cases.

A good interview explanation:

> The hallucination-risk scenarios are intentionally unsafe model outputs. The goal is not to show that the system hallucinates; the goal is to show that the system detects unsafe AI outputs before they become operational alerts.

## One-command reviewer path

Run:

```bash
make reviewer-demo
```

The command shows the maturity map in the logical order of the pipeline:

1. quality gates
2. evidence collection
3. deterministic SEO skills
4. playbook retrieval / RAG
5. model routing
6. structured AI output
7. grounding and hallucination guard
8. Slack/human-in-the-loop delivery
9. observability
10. MCP/live API future direction
