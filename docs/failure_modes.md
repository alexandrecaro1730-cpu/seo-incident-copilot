# Failure Modes and Controls

| Failure mode | Business risk | Control in this repo |
|---|---|---|
| LLM returns invalid JSON | automation breaks or alerts become unreliable | strict schema validation |
| LLM invents evidence | team acts on false diagnosis | grounding guard checks evidence IDs |
| API timeout | incident missed | timeout fallback creates unknown incident |
| noisy rank movement | alert fatigue | rank-drop threshold |
| noindex regression misclassified as content issue | delayed recovery | deterministic technical checks prioritized |
| expensive model overuse | high operating cost | model router and cost tracker |
| secrets sent to LLM | client/security risk | prompt design and `.env.example` separation |
