"""
Business objective:
Make the path from deterministic fixture mode to live LLM APIs explicit without
requiring reviewers to provide credentials.

Coding objective:
Provide a small provider-aware live LLM client that fails safely when credentials
are missing and can optionally call OpenAI or Anthropic when network access is
explicitly enabled.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


ALLOWED_PROVIDERS = {"fixture", "openai", "anthropic"}
DEFAULT_MODEL_BY_TIER = {
    "cheap": "gpt-4.1-mini",
    "middle": "gpt-4.1-mini",
    "expensive": "gpt-4.1",
}


@dataclass(frozen=True)
class LiveLLMResult:
    """Structured result returned by the live LLM smoke path."""

    status: str
    provider: str
    model: str | None
    tier: str
    message: str
    payload: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation for CLI output and tests."""

        return {
            "status": self.status,
            "provider": self.provider,
            "model": self.model,
            "tier": self.tier,
            "message": self.message,
            "payload": self.payload,
        }


def get_provider_from_env() -> str:
    """Read the desired LLM provider from environment variables."""

    return os.getenv("LLM_PROVIDER", "fixture").strip().lower() or "fixture"


def get_model_for_tier(tier: str) -> str:
    """Resolve the model name for a cost tier using environment variables."""

    env_name = {
        "cheap": "CHEAP_MODEL_NAME",
        "middle": "MIDDLE_MODEL_NAME",
        "expensive": "EXPENSIVE_MODEL_NAME",
    }.get(tier, "EXPENSIVE_MODEL_NAME")

    return os.getenv(env_name, "").strip() or DEFAULT_MODEL_BY_TIER.get(
        tier, DEFAULT_MODEL_BY_TIER["expensive"]
    )


def validate_minimal_analysis_payload(payload: dict[str, Any]) -> list[str]:
    """Validate the minimum JSON contract expected from a live model response."""

    errors: list[str] = []

    if not isinstance(payload.get("issue_type"), str) or not payload.get("issue_type"):
        errors.append("missing_or_invalid_issue_type")

    confidence = payload.get("confidence_score")
    if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
        errors.append("missing_or_invalid_confidence_score")

    if not isinstance(payload.get("recommended_action"), str) or not payload.get(
        "recommended_action"
    ):
        errors.append("missing_or_invalid_recommended_action")

    return errors


class LiveLLMClient:
    """Small live provider client with safe default behavior.

    By default, this client never calls the network. That keeps the repo
    deterministic for reviewers. Real API calls require `allow_network=True`.
    """

    def __init__(
        self,
        provider: str | None = None,
        tier: str = "expensive",
        allow_network: bool = False,
        timeout_seconds: int = 30,
    ) -> None:
        self.provider = (provider or get_provider_from_env()).strip().lower()
        self.tier = tier
        self.allow_network = allow_network
        self.timeout_seconds = timeout_seconds
        self.model = get_model_for_tier(tier)

    def smoke_test(self) -> LiveLLMResult:
        """Check whether live mode is configured without forcing network access."""

        if self.provider not in ALLOWED_PROVIDERS:
            return LiveLLMResult(
                status="error",
                provider=self.provider,
                model=None,
                tier=self.tier,
                message="Unsupported LLM_PROVIDER. Use fixture, openai, or anthropic.",
            )

        if self.provider == "fixture":
            return LiveLLMResult(
                status="skipped",
                provider=self.provider,
                model=None,
                tier=self.tier,
                message=(
                    "Fixture mode is active. Deterministic model_outputs/ JSON files "
                    "remain the default reviewer path."
                ),
            )

        missing_secret = self._missing_secret_name()
        if missing_secret:
            return LiveLLMResult(
                status="skipped",
                provider=self.provider,
                model=self.model,
                tier=self.tier,
                message=(
                    f"Live provider is selected but {missing_secret} is not set. "
                    "Set it in your local environment or secret manager, not in Git."
                ),
            )

        if not self.allow_network:
            return LiveLLMResult(
                status="ready",
                provider=self.provider,
                model=self.model,
                tier=self.tier,
                message=(
                    "Live provider credentials are present. Network calls are disabled "
                    "for this smoke test unless --allow-network is passed."
                ),
            )

        return self._call_live_model()

    def _missing_secret_name(self) -> str | None:
        if self.provider == "openai" and not os.getenv("OPENAI_API_KEY"):
            return "OPENAI_API_KEY"
        if self.provider == "anthropic" and not os.getenv("ANTHROPIC_API_KEY"):
            return "ANTHROPIC_API_KEY"
        return None

    def _call_live_model(self) -> LiveLLMResult:
        prompt = (
            "Return strict JSON only with keys: issue_type, confidence_score, "
            "recommended_action. Use this toy SEO incident: a high-value landing page "
            "dropped from position 2 to 9 and the new SERP contains more comparison "
            "listicles than vendor landing pages."
        )

        try:
            if self.provider == "openai":
                raw_text = self._call_openai(prompt)
            elif self.provider == "anthropic":
                raw_text = self._call_anthropic(prompt)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
        except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
            return LiveLLMResult(
                status="error",
                provider=self.provider,
                model=self.model,
                tier=self.tier,
                message=f"Live API call failed safely: {exc}",
            )

        parsed = _parse_json_object(raw_text)
        if parsed is None:
            return LiveLLMResult(
                status="error",
                provider=self.provider,
                model=self.model,
                tier=self.tier,
                message="Live API response was not valid JSON.",
                payload={"raw_text": raw_text[:500]},
            )

        errors = validate_minimal_analysis_payload(parsed)
        if errors:
            return LiveLLMResult(
                status="error",
                provider=self.provider,
                model=self.model,
                tier=self.tier,
                message=f"Live API JSON failed minimal contract: {errors}",
                payload=parsed,
            )

        return LiveLLMResult(
            status="ok",
            provider=self.provider,
            model=self.model,
            tier=self.tier,
            message="Live API returned a valid minimal SEO analysis payload.",
            payload=parsed,
        )

    def _call_openai(self, prompt: str) -> str:
        api_key = os.environ["OPENAI_API_KEY"]
        body = {
            "model": self.model,
            "input": prompt,
            "text": {"format": {"type": "json_object"}},
        }
        request = urllib.request.Request(
            "https://api.openai.com/v1/responses",
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            data = json.loads(response.read().decode("utf-8"))
        return _extract_openai_text(data)

    def _call_anthropic(self, prompt: str) -> str:
        api_key = os.environ["ANTHROPIC_API_KEY"]
        body = {
            "model": self.model,
            "max_tokens": 500,
            "messages": [{"role": "user", "content": prompt}],
        }
        request = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=json.dumps(body).encode("utf-8"),
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            data = json.loads(response.read().decode("utf-8"))
        return _extract_anthropic_text(data)


def _parse_json_object(raw_text: str) -> dict[str, Any] | None:
    """Parse a JSON object from model text without trusting surrounding prose."""

    raw_text = raw_text.strip()
    try:
        parsed = json.loads(raw_text)
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        start = raw_text.find("{")
        end = raw_text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return None
        try:
            parsed = json.loads(raw_text[start : end + 1])
        except json.JSONDecodeError:
            return None
        return parsed if isinstance(parsed, dict) else None


def _extract_openai_text(data: dict[str, Any]) -> str:
    """Extract text from common OpenAI Responses API shapes."""

    output_text = data.get("output_text")
    if isinstance(output_text, str):
        return output_text

    output = data.get("output")
    if isinstance(output, list):
        chunks: list[str] = []
        for item in output:
            for content in item.get("content", []) if isinstance(item, dict) else []:
                if isinstance(content, dict) and isinstance(content.get("text"), str):
                    chunks.append(content["text"])
        if chunks:
            return "\n".join(chunks)

    return json.dumps(data)


def _extract_anthropic_text(data: dict[str, Any]) -> str:
    """Extract text from common Anthropic Messages API shapes."""

    content = data.get("content")
    if isinstance(content, list):
        chunks = [
            item.get("text", "")
            for item in content
            if isinstance(item, dict) and item.get("type") == "text"
        ]
        if chunks:
            return "\n".join(chunks)

    return json.dumps(data)
