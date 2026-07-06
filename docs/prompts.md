# Prompt Contract

The prompts in `/prompts` are intentionally plain text because the case-study workflow tests prompts as versioned artifacts.

Each model tier must return the same schema:

```json
{
  "issue_type": "intent_shift | technical_regression | content_decay | competitor_improvement | mixed | unknown",
  "confidence_score": 0.0,
  "recommended_action": "string",
  "evidence": [{"evidence_id": "string", "claim": "string"}],
  "next_steps": ["string"],
  "requires_human_review": true
}
```

The manual JSON files in `/model_outputs` simulate what each model tier should return. Tests validate that these fixtures are usable before a real LLM API is connected.
