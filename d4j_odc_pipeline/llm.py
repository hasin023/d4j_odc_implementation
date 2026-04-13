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
    temperature: float = 0.0


class OpenAICompatibleClient:
    def __init__(self, settings: LLMSettings) -> None:
        self.settings = settings

    @classmethod
    def from_env(
        cls,
        *,
        provider: str,
        model: str,
        api_key_env: str,
        base_url: str | None = None,
    ) -> "OpenAICompatibleClient":
        api_key = os.environ.get(api_key_env)
        if not api_key:
            raise LLMError(f"Missing API key in environment variable {api_key_env}.")
        resolved_base_url = base_url or os.environ.get("OPENAI_BASE_URL") or "https://api.openai.com/v1"
        return cls(
            LLMSettings(
                provider=provider,
                model=model,
                api_key=api_key,
                base_url=resolved_base_url.rstrip("/"),
            )
        )

    def complete(self, messages: list[dict[str, str]]) -> str:
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
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=300) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise LLMError(f"LLM request failed with status {exc.code}: {body}") from exc
        except urllib.error.URLError as exc:
            raise LLMError(f"LLM request failed: {exc}") from exc
        data = json.loads(raw)
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMError(f"Unexpected LLM response shape: {raw}") from exc
