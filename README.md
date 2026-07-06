# SEO Incident Copilot

Production-shaped Python mini-project for the **(Senior) SEO AI Engineer** case study.

This project simulates an automation that detects high-value SEO ranking drops, diagnoses whether the likely cause is a **technical regression**, **search-intent shift**, or **content decay**, validates structured AI output, controls hallucination risk through evidence grounding, estimates AI model cost, and generates an actionable Slack alert.

The goal is not to build a toy chatbot. The goal is to show how an SEO AI Engineer can combine **SEO fundamentals**, **deterministic automation**, **LLM reasoning**, **cost control**, **testing**, and **operational alerting** into a system that could scale inside a real agency environment.

---

## Why this repo exists

### Business objective

Reduce SEO incident diagnosis time before traffic loss becomes visible.

In B2B SaaS SEO, a valuable landing page dropping from position 2 to position 9 can represent meaningful pipeline risk. The system is designed to detect that movement, collect evidence, classify the likely root cause, and alert the team with recommended next steps.

### Technical objective

Show a robust AI-first workflow that is still deterministic where deterministic logic is safer, cheaper, and faster.

The system deliberately does **not** ask an LLM to do everything. Python handles the checks that should be deterministic, such as:

* rank-drop threshold detection
* `noindex` detection
* SERP result-type counting
* content module coverage
* schema validation
* timeout fallback
* cost tracking
* Slack payload generation

The AI layer is used where judgment and synthesis add value:

* interpreting old vs. new SERP intent
* choosing the likely root cause
* summarizing evidence
* recommending next actions
* formatting an executive-friendly incident explanation

---

## What reviewers should notice

This repo is designed to demonstrate:

1. **SEO fundamentals**
   The scenarios are grounded in realistic technical SEO and B2B SaaS organic growth issues: accidental `noindex`, SERP intent shifts, content decay, and noisy rank fluctuations.

2. **Systems thinking**
   The pipeline follows a production-style flow: collect, validate, enrich, analyze, ground, alert, and log.

3. **AI pragmatism**
   The LLM is not treated as an oracle. It is routed by business impact, constrained by schema, checked against evidence, and bypassed when deterministic logic is enough.

4. **Cost awareness**
   The system routes incidents to `cheap`, `middle`, or `expensive` model tiers depending on severity, ambiguity, and business value.

5. **Reliability and safety**
   The project includes timeout fallback, structured output validation, grounding checks, human-review flags, and automated tests.

6. **Scalability path**
   The demo uses local JSON fixtures, but the interfaces are designed so production data sources can later be connected without rewriting the core pipeline.

---

## Manual prompt and JSON fixture strategy

This case-study version uses manual prompt files and manually curated JSON model-output fixtures for three model tiers:

* `cheap`: fast triage and obvious deterministic cases
* `middle`: standard root-cause analysis
* `expensive`: high-impact or ambiguous incident analysis

This is intentional.

Before connecting a real LLM API, the project validates the most important contracts:

* prompt design
* model tier routing
* structured JSON response shape
* issue-type classification
* evidence requirements
* grounding and hallucination checks
* timeout fallback behavior
* Slack alert formatting
* incident logging

This makes the system deterministic, testable, and easy to review in a technical interview.

---

## Demo scenarios

| Scenario               | Expected root cause                                                      | What it proves                                          |
| ---------------------- | ------------------------------------------------------------------------ | ------------------------------------------------------- |
| `intent_shift`         | Google now favors listicles, comparison pages, and review/category pages | SERP intent comparison plus RAG-grounded recommendation |
| `technical_regression` | Accidental `noindex` tag                                                 | Deterministic SEO check beats unnecessary LLM reasoning |
| `content_decay`        | Competitors improved page depth, modules, and freshness                  | Content decay and competitor-change reasoning           |
| `no_trigger`           | Ranking movement is too small                                            | System avoids noisy false alerts                        |
| `timeout_fallback`     | LLM analysis times out                                                   | Controlled fallback instead of broken automation        |

---

## Architecture

```text
Ranking snapshot
    ↓
Data validation
    ↓
Rank-drop detection
    ↓
Evidence collection
    ├─ SERP comparison
    ├─ page audit checks
    ├─ GSC trend fixture
    └─ SEO playbook retrieval
    ↓
Cost-aware model routing
    ↓
Manual prompt + JSON fixture output
    ↓
Strict schema validation
    ↓
Grounding and hallucination guard
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
├── model_outputs/
│   ├── cheap/
│   ├── middle/
│   └── expensive/
├── prompts/
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
python -m pytest -q
python -m ruff check .
```

Expected result:

```text
21 passed
All checks passed!
```

---

## Run demo incidents

Intent shift:

```bash
python -m seo_incident_copilot.main --scenario intent_shift --dry-run-slack
```

Technical regression:

```bash
python -m seo_incident_copilot.main --scenario technical_regression --dry-run-slack
```

Content decay:

```bash
python -m seo_incident_copilot.main --scenario content_decay --dry-run-slack
```

Timeout fallback:

```bash
python -m seo_incident_copilot.main --scenario timeout_fallback --dry-run-slack
```

No-trigger scenario:

```bash
python -m seo_incident_copilot.main --scenario no_trigger --dry-run-slack
```

Generated incident logs and Slack payload previews are written into:

```text
outputs/
```

The `outputs/` folder is intentionally ignored by Git because it contains runtime artifacts.

---

## Example behavior

### Intent shift

A high-value keyword drops from position 2 to position 9.

The old SERP favors vendor landing pages.
The new SERP favors listicles, review pages, and comparison content.

Expected result:

```text
issue_type: intent_shift
model_tier: expensive
recommended_action: create or update comparison-led supporting content while protecting the commercial landing page
human_review_required: true
```

### Technical regression

A critical landing page drops after an accidental `noindex` directive appears.

Expected result:

```text
issue_type: technical_regression
model_tier: cheap
recommended_action: remove noindex, validate template, request reindexing, add deployment-time indexability checks
human_review_required: true
```

### Content decay

A landing page loses visibility while the SERP remains mostly commercial, but competitors now have stronger modules such as pricing, integrations, case studies, FAQs, comparison tables, and security proof.

Expected result:

```text
issue_type: content_decay
model_tier: middle
recommended_action: refresh the landing page with missing commercial modules and improve internal links
human_review_required: true
```

### Timeout fallback

The system simulates an LLM timeout.

Expected result:

```text
issue_type: unknown
confidence_score: 0.20
recommended_action: review deterministic evidence and rerun analysis before making production changes
human_review_required: true
```

---

## How model routing works

The model router uses business impact, ambiguity, and deterministic evidence.

```text
cheap model:
- obvious technical regression
- deterministic evidence is strong
- no complex synthesis required

middle model:
- content decay
- moderate ambiguity
- standard SEO root-cause analysis

expensive model:
- high-value keyword
- likely intent shift
- ambiguous or strategically important recommendation
- fallback retry path after lower-tier failure
```

This demonstrates a key operational principle:

> Spend AI budget where judgment creates value, not where deterministic automation is enough.

---

## Grounding and hallucination control

The AI output is not accepted blindly.

The system validates:

* the output matches the expected JSON schema
* `issue_type` is one of the allowed values
* confidence score is within range
* evidence is present
* recommendations are supported by evidence IDs
* unsupported claims are flagged
* timeout fallback produces a safe human-review incident

The grounding logic is intentionally simple and inspectable for the case study. In production, this could be extended with stricter claim extraction, retrieval citations, and model-based verification.

---

## RAG-style playbook retrieval

The project includes a lightweight local knowledge base in:

```text
data/knowledge_base/
```

The system retrieves relevant SEO playbook guidance for the incident type, such as:

* intent-shift response playbook
* noindex regression playbook
* content decay playbook
* B2B SaaS landing page recommendations

The retrieved playbook content helps ensure that AI recommendations are tied to approved SEO methodology instead of generic advice.

---

## Slack alerting

The project generates a Slack-compatible payload in dry-run mode.

The alert includes:

* client
* keyword
* URL
* ranking movement
* estimated monthly revenue at risk
* likely root cause
* confidence score
* grounding score
* model tier
* estimated AI cost
* recommended action
* evidence
* next steps
* human-review requirement

In production, this dry-run payload can be sent through a Slack webhook or Slack app integration.

---

## How this maps to production

This repo uses fixture JSON instead of live APIs so the case study remains deterministic and easy to test.

In production, the same interfaces can be connected to:

* Google Search Console API
* DataForSEO or another rank tracker API
* Screaming Frog / Sitebulb crawl exports
* server logs
* CMS metadata APIs
* Slack webhooks
* BigQuery, Snowflake, or Databricks
* MCP-exposed SEO tools
* agency reporting dashboards
* client-specific content and SEO playbooks

---

## Possible MCP extension

In this mini-project, SEO capabilities are implemented as Python interfaces first.

In a larger YOYABA environment, the same capabilities could be exposed as MCP tools, for example:

```text
fetch_ranking_snapshot
compare_serp_intent
inspect_page_indexability
retrieve_seo_playbook
estimate_revenue_risk
generate_slack_alert
log_seo_incident
```

This would allow approved AI agents to call SEO tools safely while keeping business logic, permissions, and observability centralized.

---

## Testing strategy

The test suite covers:

* rank-drop detection
* no-trigger behavior
* technical-regression detection
* intent-shift scoring
* content-decay scoring
* model routing
* manual model-output loading
* schema validation
* grounding validation
* timeout fallback
* Slack payload generation
* end-to-end pipeline behavior

Run:

```bash
python -m pytest -q
```

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
   If the AI layer times out or returns invalid output, the system still produces a controlled incident requiring human review.

---

## Data disclaimer

All client names, URLs, ranking snapshots, SERP examples, GSC trends, audit findings, and revenue-risk estimates in this repository are synthetic.

They are designed to look realistic enough to test the workflow without exposing real client data.
