from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass


class LLMError(RuntimeError):
    pass


@dataclass
class LLMSettings:
    provider: str
    model: str
    api_key: str
    base_url: str
    default_headers: dict[str, str]
    temperature: float = 0.0


class LLMClient:
    def __init__(self, settings: LLMSettings) -> None:
        self.settings = settings

    @classmethod
    def from_env(
        cls,
        *,
        provider: str,
        model: str,
        api_key_env: str | None = None,
        base_url: str | None = None,
    ) -> "LLMClient":
        provider = provider.strip().lower()
        resolved_api_key_env = api_key_env or default_api_key_env(provider)
        api_key = os.environ.get(resolved_api_key_env)
        if not api_key:
            raise LLMError(f"Missing API key in environment variable {resolved_api_key_env}.")
        default_headers: dict[str, str] = {}
        if provider == "gemini":
            resolved_base_url = (
                base_url
                or os.environ.get("GEMINI_BASE_URL")
                or "https://generativelanguage.googleapis.com/v1beta"
            )
        elif provider == "openrouter":
            resolved_base_url = (
                base_url
                or os.environ.get("OPENROUTER_BASE_URL")
                or "https://openrouter.ai/api/v1"
            )
            referer = os.environ.get("OPENROUTER_HTTP_REFERER", "").strip()
            title = os.environ.get("OPENROUTER_APP_TITLE", "").strip()
            if referer:
                default_headers["HTTP-Referer"] = referer
            if title:
                default_headers["X-OpenRouter-Title"] = title
        else:
            resolved_base_url = base_url or os.environ.get("OPENAI_BASE_URL") or "https://api.openai.com/v1"
        return cls(
            LLMSettings(
                provider=provider,
                model=model,
                api_key=api_key,
                base_url=resolved_base_url.rstrip("/"),
                default_headers=default_headers,
            )
        )

    def complete(self, messages: list[dict[str, str]]) -> str:
        if self.settings.provider == "gemini":
            return self._complete_gemini(messages)
        return self._complete_openai_compatible(messages)

    def _complete_openai_compatible(self, messages: list[dict[str, str]]) -> str:
        payload = {
            "model": self.settings.model,
            "messages": messages,
            "temperature": self.settings.temperature,
        }
        request = urllib.request.Request(
            url=f"{self.settings.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.settings.api_key}",
                **self.settings.default_headers,
            },
            method="POST",
        )
        raw = _urlopen_json(request)
        data = json.loads(raw)
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMError(f"Unexpected LLM response shape: {raw}") from exc

    def _complete_gemini(self, messages: list[dict[str, str]]) -> str:
        payload: dict[str, object] = {
            "contents": _gemini_contents(messages),
            "generationConfig": {
                "temperature": self.settings.temperature,
                "responseMimeType": "application/json",
                "responseJsonSchema": classification_response_schema(),
            },
        }
        system_instruction = _gemini_system_instruction(messages)
        if system_instruction:
            payload["system_instruction"] = {
                "parts": [{"text": system_instruction}],
            }

        request = urllib.request.Request(
            url=f"{self.settings.base_url}/models/{self.settings.model}:generateContent",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": self.settings.api_key,
            },
            method="POST",
        )
        raw = _urlopen_json(request)
        data = json.loads(raw)
        try:
            parts = data["candidates"][0]["content"]["parts"]
            text_parts = [part.get("text", "") for part in parts if isinstance(part, dict)]
            combined = "\n".join(part for part in text_parts if part).strip()
            if combined:
                return combined
        except (KeyError, IndexError, TypeError):
            pass
        raise LLMError(f"Unexpected Gemini response shape: {raw}")


def default_api_key_env(provider: str) -> str:
    provider = provider.strip().lower()
    if provider == "gemini":
        return "GEMINI_API_KEY"
    if provider == "openrouter":
        return "OPENROUTER_API_KEY"
    return "OPENAI_API_KEY"


def classification_response_schema() -> dict:
    return {
        "type": "object",
        "properties": {
            "odc_type": {"type": "string"},
            "coarse_group": {"type": ["string", "null"]},
            "confidence": {"type": "number"},
            "needs_human_review": {"type": "boolean"},
            "observation_summary": {"type": "string"},
            "hypothesis": {"type": "string"},
            "prediction": {"type": "string"},
            "experiment_rationale": {"type": "string"},
            "reasoning_summary": {"type": "string"},
            "evidence_used": {"type": "array", "items": {"type": "string"}},
            "evidence_gaps": {"type": "array", "items": {"type": "string"}},
            "alternative_types": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string"},
                        "why_not_primary": {"type": "string"},
                    },
                    "required": ["type", "why_not_primary"],
                },
            },
        },
        "required": [
            "odc_type",
            "coarse_group",
            "confidence",
            "needs_human_review",
            "observation_summary",
            "hypothesis",
            "prediction",
            "experiment_rationale",
            "reasoning_summary",
            "evidence_used",
            "evidence_gaps",
            "alternative_types",
        ],
    }


def _gemini_system_instruction(messages: list[dict[str, str]]) -> str | None:
    chunks = [message["content"] for message in messages if message.get("role") == "system" and message.get("content")]
    return "\n\n".join(chunks).strip() or None


def _gemini_contents(messages: list[dict[str, str]]) -> list[dict]:
    contents: list[dict] = []
    for message in messages:
        role = message.get("role")
        content = message.get("content", "")
        if not content or role == "system":
            continue
        gemini_role = "model" if role == "assistant" else "user"
        contents.append({"role": gemini_role, "parts": [{"text": content}]})
    if not contents:
        raise LLMError("Gemini request did not contain any non-system content.")
    return contents


def _urlopen_json(request: urllib.request.Request) -> str:
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise LLMError(f"LLM request failed with status {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise LLMError(f"LLM request failed: {exc}") from exc
