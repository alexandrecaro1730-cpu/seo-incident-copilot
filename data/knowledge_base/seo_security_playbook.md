# SEO AI Security Playbook

Business objective: protect clients while using AI to speed up diagnosis.

Do not send secrets, raw customer PII, authentication tokens, or confidential exports to an LLM. Redact sensitive values before prompts. Store prompt inputs and outputs for auditability. Do not allow the AI system to directly modify production SEO settings without human approval.

Recommended controls:
- environment variables for credentials
- prompt redaction
- allow-listed tool calls
- schema validation
- human approval for production changes
- structured incident logs
