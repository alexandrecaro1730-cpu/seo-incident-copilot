# SEO Incident Copilot

Production-shaped Python project for the **(Senior) SEO AI Engineer** case study.

This project simulates an SEO incident automation system that detects high-value ranking drops, collects supporting evidence, diagnoses the likely root cause, validates AI-generated analysis, estimates model cost, controls hallucination risk, and generates an actionable Slack-ready alert.

The goal is not to build a generic AI chatbot. The goal is to demonstrate how an SEO AI Engineer can combine **technical SEO fundamentals**, **deterministic automation**, **LLM-assisted reasoning**, **cost-aware model routing**, **RAG-style playbook grounding**, **failure-mode handling**, **observability**, and **testing** into a workflow that could scale inside a real agency or B2B SaaS growth environment.

---

## Business objective

Reduce SEO incident diagnosis time before traffic loss becomes visible.

A high-value B2B SaaS landing page dropping from position 2 to position 9 can represent meaningful pipeline risk. The system is designed to detect that movement, understand whether the likely cause is technical, content-related, SERP-related, or AI-output-related, and alert the team with recommended next steps.

---

## Technical objective

Build a production-shaped, testable AI-first SEO workflow where deterministic logic handles what should not be delegated to an LLM.

The system deliberately does **not** ask an LLM to do everything. Python handles the checks that are safer, cheaper, and more reliable when deterministic:

- rank-drop threshold detection
- `noindex` detection
- canonical regression detection
- SERP result-type comparison
- content module coverage checks
- keyword cannibalization detection
- demand-drop false-positive prevention
- strict JSON validation
- timeout fallback
- model cost tracking
- Slack payload generation
- incident logging

The AI layer is used where judgment and synthesis add value:

- interpreting old vs. new SERP intent
- distinguishing content decay from intent shift
- synthesizing evidence into a clear diagnosis
- recommending next actions
- generating a human-readable incident explanation
- escalating uncertain or unsafe outputs to human review

---

## What reviewers should notice

This repo is designed to show more than a working script.

It demonstrates:

1. **SEO fundamentals**
   The scenarios are grounded in realistic B2B SaaS and technical SEO risks: accidental `noindex`, canonical regressions, SERP intent shifts, content decay, keyword cannibalization, and demand drops.

2. **Systems thinking**
   The workflow follows a production-style pipeline: collect, validate, enrich, analyze, ground, alert, and log.

3. **AI pragmatism**
   The LLM is not treated as an oracle. It is routed by business impact, constrained by schema, checked against evidence, and bypassed when deterministic logic is enough.

4. **Cost awareness**
   Incidents are routed to `cheap`, `middle`, or `expensive` model tiers depending on severity, ambiguity, and business value.

5. **Failure-mode thinking**
   The system intentionally tests hallucinated claims, invalid schema output, overconfidence, contradictory recommendations, timeouts, and false positives.

6. **Operational readiness**
   The project includes tests, linting, dry-run Slack alerts, incident logs, runtime summaries, aggregate metrics, and a one-command reviewer demo.

7. **Architectural honesty**
   RAG-style retrieval is implemented in a lightweight local form. MCP and live APIs are presented as production extension points, not falsely claimed as fully implemented.

---

## One-command reviewer demo

Run:

```bash
make reviewer-demo
```

This command runs the full reviewer experience:

- pytest
- Ruff
- all SEO incident scenarios
- model routing checks
- cost summary
- hallucination-risk summary
- grounding summary
- invalid-schema detection
- action-mismatch detection
- Slack payload generation
- incident logging
- AI engineering maturity timeline

Expected quality result:

```text
37 passed
All checks passed!
Reviewer demo completed successfully.
```

The demo writes reviewer artifacts to:

```text
outputs/reviewer_demo/reviewer_summary.md
outputs/reviewer_demo/reviewer_summary.json
outputs/slack_payload_preview.json
outputs/incidents.jsonl
```

The `outputs/` folder is intentionally ignored by Git because it contains runtime artifacts.

---

## AI engineering maturity timeline

The reviewer demo is organized as a logical AI workflow timeline:

1. **Quality gates**
   Pytest and Ruff run before the scenarios. This shows testability and CI readiness.

2. **Evidence collection**
   Ranking, SERP, GSC, page-audit, and playbook fixtures simulate the production SEO data sources.

3. **Deterministic SEO skills**
   Rank-drop, `noindex`, canonical, demand, and cannibalization checks run before LLM reasoning.

4. **Playbook retrieval**
   Lightweight RAG-style retrieval pulls relevant SEO playbooks from `data/knowledge_base`.

5. **Model selection**
   Incidents are routed to cheap, middle, or expensive model tiers based on impact, ambiguity, and evidence quality.

6. **AI analysis**
   Manual prompts and schema-validated JSON fixtures simulate structured LLM output.

7. **Safety layer**
   Grounding, hallucination-risk, invalid-schema, action-mismatch, and overconfidence checks validate the AI output.

8. **Delivery layer**
   Slack-compatible payloads are generated in dry-run mode with human-review flags.

9. **Observability**
   The demo reports cost, model share, grounding, hallucination-risk, warning codes, and incident metrics.

10. **MCP readiness**
    The current Python skills are cleanly separated and could be exposed as MCP tools in production.

MCP and live APIs are intentionally presented as production extension points, not as fully implemented features in this case-study version.

---

## Current demo scenarios

| Scenario | Expected behavior | What it proves |
|---|---|---|
| `no_trigger` | No incident | Small ranking movement should not create noisy alerts |
| `demand_drop_not_seo_issue` | No SEO incident | Traffic or impression drops are not always SEO regressions |
| `technical_regression` | Technical regression | Accidental `noindex` is caught deterministically |
| `canonical_regression` | Technical regression | Canonical mismatches are caught without unnecessary LLM reasoning |
| `content_decay` | Content decay | Outdated page depth/modules can explain ranking decline |
| `keyword_cannibalization` | Keyword cannibalization | Another page competing for the same query is diagnosed |
| `intent_shift` | Search intent shift | SERP changed from vendor pages to listicles/comparison/review pages |
| `timeout_fallback` | Safe fallback | LLM timeout does not break the automation |
| `hallucinated_competitor_claim` | Grounding warning | Unsupported competitor claims are flagged |
| `action_mismatch` | Business-logic warning | Diagnosis and recommended action must be consistent |
| `invalid_schema_output` | Schema fallback | Invalid AI output is rejected safely |
| `overconfident_weak_evidence` | Confidence warning | High confidence with weak evidence is treated as risky |

---

## Interpreting reviewer-demo metrics

Some scenarios are intentionally adversarial.

For example:

- `hallucinated_competitor_claim`
- `action_mismatch`
- `invalid_schema_output`
- `overconfident_weak_evidence`

These are designed to fail grounding, schema, or business-logic checks.

Therefore, a lower grounding pass rate in the reviewer demo is expected. It does **not** mean the production-like scenarios are failing. It means the guardrails are detecting unsafe AI outputs instead of blindly trusting them.

Example aggregate metrics include:

```text
Incident detection rate
No-alert rate
Deterministic resolution rate
Average cost per incident
Total estimated demo cost
Model usage share
Average confidence
Grounding pass rate
Hallucination-risk scenario rate
Unsupported-claim rate
Action-mismatch rate
Invalid-schema rate
Human-review rate
Warning-code counts
```

This is the intended story:

> The system does not only produce SEO alerts. It also tests whether the AI layer can be trusted.

---

## Architecture

```text
Ranking snapshot
    ↓
Data validation
    ↓
Rank-drop and false-positive checks
    ↓
Evidence collection
    ├─ SERP comparison
    ├─ page audit checks
    ├─ GSC trend fixture
    ├─ cannibalization signals
    └─ SEO playbook retrieval
    ↓
Deterministic SEO checks
    ↓
Cost-aware model routing
    ↓
Manual prompt + JSON fixture output
    ↓
Strict schema validation
    ↓
Grounding and hallucination-risk guard
    ↓
Slack payload generation
    ↓
Incident JSONL log
```

---

## Repository structure

```text
seo_incident_copilot/
├── data/
│   ├── gsc/
│   ├── knowledge_base/
│   ├── page_audits/
│   ├── ranking_snapshots.json
│   └── serp/
├── docs/
│   └── ai_engineering_maturity_map.md
├── model_outputs/
│   ├── cheap/
│   ├── middle/
│   └── expensive/
├── prompts/
├── scripts/
│   └── reviewer_demo.py
├── src/
│   └── seo_incident_copilot/
│       ├── ai/
│       ├── connectors/
│       ├── detectors/
│       ├── observability/
│       ├── rag/
│       ├── storage/
│       ├── config.py
│       ├── main.py
│       ├── pipeline.py
│       └── schemas.py
├── tests/
├── Makefile
├── pyproject.toml
└── README.md
```

---

## Manual prompt and JSON fixture strategy

This case-study version uses manual prompt files and manually curated JSON model-output fixtures for three model tiers:

- `cheap`: fast triage and obvious technical cases
- `middle`: standard SEO root-cause analysis
- `expensive`: high-impact or ambiguous incident analysis

This is intentional.

Before connecting a real LLM API, the project validates the most important contracts:

- prompt structure
- model tier routing
- structured JSON response shape
- allowed issue types
- evidence requirements
- grounding behavior
- hallucination-risk checks
- timeout fallback behavior
- Slack alert formatting
- incident logging

This makes the system deterministic, testable, and easy to review in a technical interview.

---

## Model routing logic

The model router uses business impact, ambiguity, and deterministic evidence.

```text
cheap model:
- obvious technical regression
- deterministic evidence is strong
- no complex synthesis required

middle model:
- content decay
- keyword cannibalization
- moderate ambiguity
- standard SEO root-cause analysis

expensive model:
- high-value keyword
- likely intent shift
- ambiguous strategic recommendation
- unsafe or adversarial AI-output test case
- fallback path after lower-tier failure
```

Key principle:

> Spend AI budget where judgment creates value, not where deterministic automation is enough.

---

## Grounding and hallucination-risk control

The AI output is not accepted blindly.

The system validates:

- the output matches the expected JSON schema
- `issue_type` is one of the allowed values
- confidence score is within range
- evidence is present
- recommendations are supported by evidence IDs
- unsupported claims are flagged
- issue type and recommended action are consistent
- overconfident answers with weak evidence are warned
- timeout fallback produces a safe human-review incident

The grounding logic is intentionally inspectable for the case study. In production, it could be extended with stricter claim extraction, retrieval citations, contradiction detection, and model-based verification.

---

## RAG-style SEO playbook retrieval

The project includes a lightweight local knowledge base in:

```text
data/knowledge_base/
```

The system retrieves relevant SEO playbook guidance for the incident type, such as:

- intent-shift response playbook
- noindex regression playbook
- content decay playbook
- B2B SaaS landing page recommendations
- cannibalization response guidance
- demand-shift interpretation guidance

The retrieved playbook content helps ensure that recommendations are tied to approved SEO methodology instead of generic AI advice.

This is intentionally implemented as local retrieval for the case-study version. In production, the same interface could be upgraded to embeddings and vector search across client playbooks, historical incidents, technical SEO SOPs, CMS documentation, and strategy notes.

---

## Agent skills / controlled tools

The project treats agent skills as controlled, testable capabilities rather than free-form autonomous behavior.

Examples of current tool-like skills:

```text
detect_rank_drop
detect_technical_regression
detect_canonical_regression
detect_content_decay
detect_keyword_cannibalization
detect_demand_shift
retrieve_seo_playbook
route_model_tier
validate_structured_output
validate_grounding
generate_slack_payload
log_incident
```

In the current implementation, these are Python modules and functions. In production, they could be exposed as internal tools, OpenAI function-calling tools, n8n workflow steps, or MCP tools.

---

## MCP readiness

This project does not claim to implement a full MCP server.

Instead, the system is designed so that the core SEO capabilities are separated into clean interfaces that could later be exposed as MCP tools.

Possible production MCP tools:

```text
fetch_ranking_snapshot
compare_serp_intent
inspect_page_indexability
detect_keyword_cannibalization
retrieve_seo_playbook
estimate_revenue_risk
generate_slack_alert
log_seo_incident
```

This would allow approved AI agents to call SEO tools safely while keeping business logic, permissions, logging, and rate limits centralized.

---

## Setup

This project has been validated with **Python 3.12**.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

---

## Run quality checks

```bash
python -m pytest
python -m ruff check .
```

Expected result:

```text
37 passed
All checks passed!
```

---

## Run the full reviewer demo

```bash
make reviewer-demo
```

This is the recommended way to review the project because it runs the quality gates, all scenarios, aggregate metrics, and AI maturity timeline in one command.

---

## Run demo scenarios manually

Intent shift:

```bash
python -m seo_incident_copilot.main --scenario intent_shift --dry-run-slack
```

Technical regression:

```bash
python -m seo_incident_copilot.main --scenario technical_regression --dry-run-slack
```

Canonical regression:

```bash
python -m seo_incident_copilot.main --scenario canonical_regression --dry-run-slack
```

Content decay:

```bash
python -m seo_incident_copilot.main --scenario content_decay --dry-run-slack
```

Keyword cannibalization:

```bash
python -m seo_incident_copilot.main --scenario keyword_cannibalization --dry-run-slack
```

Demand drop that should not become an SEO incident:

```bash
python -m seo_incident_copilot.main --scenario demand_drop_not_seo_issue --dry-run-slack
```

Timeout fallback:

```bash
python -m seo_incident_copilot.main --scenario timeout_fallback --dry-run-slack
```

AI failure-mode examples:

```bash
python -m seo_incident_copilot.main --scenario hallucinated_competitor_claim --dry-run-slack
python -m seo_incident_copilot.main --scenario action_mismatch --dry-run-slack
python -m seo_incident_copilot.main --scenario invalid_schema_output --dry-run-slack
python -m seo_incident_copilot.main --scenario overconfident_weak_evidence --dry-run-slack
```

---

## Slack alerting

The project generates a Slack-compatible payload in dry-run mode.

The alert includes:

- client
- keyword
- URL
- ranking movement
- estimated monthly revenue at risk
- likely root cause
- confidence score
- grounding score
- model tier
- estimated AI cost
- recommended action
- evidence
- next steps
- human-review requirement

In production, the dry-run payload can be sent through a Slack webhook or Slack app integration.

---

## Robustness and observability

The project includes several production-oriented safeguards:

- structured schema validation
- deterministic checks before LLM reasoning
- model timeout fallback
- invalid-output fallback
- grounding and hallucination-risk warnings
- action-mismatch warnings
- overconfidence warnings
- cost estimation
- model usage reporting
- incident JSONL logging
- reviewer summary artifacts
- human-review requirement for risky or production-changing recommendations

The reviewer demo summarizes operating metrics such as:

```text
Model usage share
Average cost per incident
Grounding pass rate
Hallucination-risk scenario rate
Warning-code counts
Human-review rate
Deterministic resolution rate
```

---

## How this maps to production

This repo uses fixture JSON instead of live APIs so the case study remains deterministic and easy to test.

In production, the same interfaces could be connected to:

- Google Search Console API
- DataForSEO / DFSEO or another rank tracker API
- Screaming Frog or Sitebulb crawl exports
- server logs
- CMS metadata APIs
- Slack webhooks
- BigQuery, Snowflake, or Databricks
- MCP-exposed SEO tools
- agency reporting dashboards
- client-specific SEO and content playbooks
- previous incident memory

---

## Pragmatism vs. perfection

Some parts of this system are appropriate for quick workflow automation. Other parts deserve a robust custom codebase.

Good candidates for n8n or lightweight workflow automation:

- scheduled API pulls
- Slack notification routing
- simple enrichment steps
- report distribution
- prototype workflows
- low-risk internal notifications

Better candidates for a tested Python codebase:

- data contracts and schema validation
- ranking-drop logic
- canonical/indexability checks
- model routing
- grounding and hallucination-risk guardrails
- fallback behavior
- incident logging
- reusable SEO skills
- tests and CI

The principle is:

> Use workflow automation for orchestration and speed, but keep core SEO business logic in tested, version-controlled code.

---

## Testing strategy

The test suite covers:

- rank-drop detection
- no-trigger behavior
- demand-drop false-positive prevention
- technical-regression detection
- canonical-regression detection
- intent-shift scoring
- content-decay scoring
- keyword-cannibalization behavior
- model routing
- manual model-output loading
- schema validation
- invalid-schema fallback
- grounding validation
- unsupported-claim detection
- action-mismatch detection
- overconfidence warning
- timeout fallback
- Slack payload generation
- reviewer-demo aggregate metrics
- AI maturity reviewer timeline
- end-to-end pipeline behavior

Run:

```bash
python -m pytest
```

---

## Case-study requirement mapping

| YOYABA requirement | Where it is addressed |
|---|---|
| Part 1: SCQA methodology for SEO → GEO | Submission PDF / Notion document |
| Part 2: SEO-first architecture | Submission PDF / Notion document + README architecture |
| Collect → Normalize → Validate → Enrich → Surface | README architecture + pipeline code |
| LLM placement in the pipeline | AI maturity timeline + `src/seo_incident_copilot/ai/` |
| API rate limits / robustness / observability | Reviewer demo metrics, fallback logic, future production notes |
| Pragmatism vs. perfection | README section above |
| Part 3: Trigger/input | `data/ranking_snapshots.json` |
| Part 3: Old/new SERP analysis | `data/serp/`, `detectors/intent_shift.py`, model-output fixtures |
| Part 3: Structured output | `schemas.py`, `tests/test_schema_validation.py` |
| Part 3: Slack alerting | `connectors/slack_client.py` |
| Hallucination handling | `grounding_guard.py`, enriched failure-mode scenarios |
| API timeout handling | `timeout_fallback` scenario |
| Prompts | `prompts/` |
| Code/workflow deliverable | GitHub repository |
| Part 4: Real-world value examples | Submission PDF / Notion document |

---

## Design principles

1. **Deterministic checks first**
   Do not ask an LLM whether a page has `noindex` when Python can inspect the value.

2. **AI where judgment matters**
   Use LLMs for SERP intent interpretation, synthesis, prioritization, and communication.

3. **Structured output only**
   Every model tier must return the same schema.

4. **Evidence required**
   Recommendations must reference evidence IDs from input data or retrieved playbooks.

5. **Cost-aware routing**
   Expensive models are reserved for high-impact or ambiguous cases.

6. **Human escalation by design**
   The system recommends action; it does not silently change production SEO settings.

7. **Safe failure modes**
   If the AI layer times out, returns invalid output, hallucinates unsupported claims, or gives contradictory recommendations, the system flags the risk and requires human review.

8. **Reviewability**
   A reviewer can run one command, `make reviewer-demo`, to see quality gates, scenario outcomes, cost metrics, model usage, hallucination-risk checks, maturity timeline, and generated artifacts.

9. **Honest architecture**
   Implemented-lite, design-ready, and future-extension components are clearly labeled instead of overstated.

---

## Data disclaimer

All client names, URLs, ranking snapshots, SERP examples, GSC trends, audit findings, model outputs, and revenue-risk estimates in this repository are synthetic.

They are designed to look realistic enough to test the workflow without exposing real client data.
