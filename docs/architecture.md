# Architecture Notes

## Business objective

Detect ranking regressions early, classify likely root cause, and alert the team with enough evidence to act before the client sees a traffic decline.

## Coding objective

Keep every step modular and testable so simulated data can be replaced by live APIs without changing the core pipeline.

## Production mapping

- `connectors/` would wrap Google Search Console, rank tracker, crawling, Slack, and warehouse APIs.
- `detectors/` contains deterministic SEO logic.
- `ai/` contains prompt loading, model routing, strict output validation, and fixture-based LLM behavior.
- `rag/` retrieves playbook snippets to ground AI recommendations.
- `observability/` tracks cost and execution metadata.
- `storage/` writes incident logs.

## Pragmatism vs perfection

Fast n8n/Claude workflows are useful for early prototypes and one-off alerts. The rank-drop detector, JSON schema validation, grounding guard, cost router, and incident storage should be custom code because they are business-critical controls.
