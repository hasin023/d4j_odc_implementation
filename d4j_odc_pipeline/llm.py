from __future__ import annotations

import itertools
import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Callable, Iterator

from .odc import allowed_impact_names

_USER_AGENT = "d4j-odc-pipeline/1.0"


class LLMError(RuntimeError):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


@dataclass
class LLMSettings:
    provider: str
    model: str
    api_key: str
    base_url: str
    default_headers: dict[str, str]
    temperature: float = 0.0


# Key rotation is resolved fresh per HTTP request (not baked into LLMSettings at
# construction time), because one LLMClient instance is reused across every turn
# of a --strategy scientific loop (up to 6 calls), and a fresh LLMClient is built
# per bug in the batch loop. Per-construction rotation would starve both: a
# single bug's turns would always share one key, and single-call strategies
# (zero/few) would always land on key #1 since a new client resets per bug.
# The cycle is cached at module scope, keyed by the env var it was read from, so
# rotation advances continuously across the whole process regardless of how many
# LLMClient instances get built.
_key_rotation_cycles: dict[str, "Iterator[str]"] = {}


def _resolve_api_keys(provider: str, api_key_env: str | None) -> tuple[str, list[str]]:
    """Resolve the API key(s) for a provider.

    <ENV_VAR>S (e.g. GEMINI_API_KEYS), comma-separated, rotates across
    multiple keys — useful for spreading a small team's free-tier quota across
    several accounts. Falls back to the singular <ENV_VAR> for single-key setups
    (unchanged behavior). Returns (cache_key, keys) where cache_key identifies
    this env var for the shared rotation cycle.
    """
    resolved_singular_env = api_key_env or default_api_key_env(provider)
    plural_env = f"{resolved_singular_env}S"

    raw_plural = os.environ.get(plural_env)
    if raw_plural:
        keys = [key.strip() for key in raw_plural.split(",") if key.strip()]
        if keys:
            return plural_env, keys

    singular_key = os.environ.get(resolved_singular_env)
    if singular_key:
        return resolved_singular_env, [singular_key]

    raise LLMError(
        f"Missing API key in environment variable {resolved_singular_env} "
        f"(or {plural_env} for multiple, comma-separated)."
    )


def _get_key_cycle(cache_key: str, keys: list[str]) -> Iterator[str]:
    cycle = _key_rotation_cycles.get(cache_key)
    if cycle is None:
        cycle = itertools.cycle(keys)
        _key_rotation_cycles[cache_key] = cycle
    return cycle


_KEY_SPECIFIC_STATUS_CODES = {401, 403, 429}


class LLMClient:
    def __init__(
        self,
        settings: LLMSettings,
        key_cycle: Iterator[str] | None = None,
        key_pool_size: int = 1,
    ) -> None:
        self.settings = settings
        self._key_cycle = key_cycle or itertools.cycle([settings.api_key])
        self._key_pool_size = max(1, key_pool_size)

    def _next_api_key(self) -> str:
        return next(self._key_cycle)

    def _request_with_key_failover(
        self, build_request: Callable[[str], urllib.request.Request]
    ) -> str:
        """Build+send a request, failing over to the next key in the rotation
        pool when a response looks like a problem with THIS key (401/403
        invalid/revoked, 429 rate-limited) rather than a transient server issue.

        With more than one key available, a 429 fails over to the next key
        immediately instead of backing off on the same (likely still-limited)
        key. With only one key, falls back to the original same-key backoff
        (unchanged behavior) since there is nothing else to try.
        """
        from . import console

        last_error: LLMError | None = None
        for attempt in range(self._key_pool_size):
            api_key = self._next_api_key()
            request = build_request(api_key)
            can_fail_over = attempt < self._key_pool_size - 1
            # Only let 429 exhaust its own same-key backoff when there is no
            # other key to fall back to; otherwise fail fast so we can swap.
            retry_codes = {500, 502, 503} | (set() if can_fail_over else {429})
            try:
                return _urlopen_json(request, retry_status_codes=retry_codes)
            except LLMError as exc:
                last_error = exc
                if can_fail_over and exc.status_code in _KEY_SPECIFIC_STATUS_CODES:
                    console.warn(
                        f"Key attempt {attempt + 1}/{self._key_pool_size} failed "
                        f"(status {exc.status_code}) — trying next key."
                    )
                    continue
                raise
        assert last_error is not None
        raise last_error

    @classmethod
    def from_env(
        cls,
        *,
        provider: str,
        model: str,
        api_key_env: str | None = None,
        base_url: str | None = None,
        temperature: float = 0.0,
    ) -> "LLMClient":
        provider = provider.strip().lower()
        cache_key, keys = _resolve_api_keys(provider, api_key_env)
        api_key = keys[0]
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
        elif provider == "groq":
            resolved_base_url = (
                base_url
                or os.environ.get("GROQ_BASE_URL")
                or "https://api.groq.com/openai/v1"
            )
        else:
            resolved_base_url = base_url or os.environ.get("OPENAI_BASE_URL") or "https://api.openai.com/v1"
        return cls(
            LLMSettings(
                provider=provider,
                model=model,
                api_key=api_key,
                base_url=resolved_base_url.rstrip("/"),
                default_headers=default_headers,
                temperature=temperature,
            ),
            key_cycle=_get_key_cycle(cache_key, keys),
            key_pool_size=len(keys),
        )

    def complete(
        self,
        messages: list[dict[str, str]],
        *,
        response_schema: dict | None = None,
    ) -> str:
        if self.settings.provider == "gemini":
            return self._complete_gemini(messages, response_schema=response_schema)
        return self._complete_openai_compatible(messages)

    def _complete_openai_compatible(self, messages: list[dict[str, str]]) -> str:
        payload = {
            "model": self.settings.model,
            "messages": messages,
            "temperature": self.settings.temperature,
        }

        def build_request(api_key: str) -> urllib.request.Request:
            return urllib.request.Request(
                url=f"{self.settings.base_url}/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                    "User-Agent": _USER_AGENT,
                    **self.settings.default_headers,
                },
                method="POST",
            )

        raw = self._request_with_key_failover(build_request)
        data = json.loads(raw)
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMError(f"Unexpected LLM response shape: {raw}") from exc

    def _complete_gemini(
        self,
        messages: list[dict[str, str]],
        *,
        response_schema: dict | None = None,
    ) -> str:
        payload: dict[str, object] = {
            "contents": _gemini_contents(messages),
            "generationConfig": {
                "temperature": self.settings.temperature,
                "responseMimeType": "application/json",
                "responseJsonSchema": response_schema or classification_response_schema(),
            },
        }
        system_instruction = _gemini_system_instruction(messages)
        if system_instruction:
            payload["system_instruction"] = {
                "parts": [{"text": system_instruction}],
            }

        def build_request(api_key: str) -> urllib.request.Request:
            return urllib.request.Request(
                url=f"{self.settings.base_url}/models/{self.settings.model}:generateContent",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "x-goog-api-key": api_key,
                    "User-Agent": _USER_AGENT,
                },
                method="POST",
            )

        raw = self._request_with_key_failover(build_request)
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
    if provider == "groq":
        return "GROQ_API_KEY"
    return "OPENAI_API_KEY"


def default_model_for_provider(provider: str, fallback: str) -> str:
    """Resolve per-provider default model from environment variables.

    Lookup order:
    1. Provider-specific env var (GEMINI_MODEL, OPENROUTER_MODEL, GROQ_MODEL)
    2. Global DEFAULT_LLM_MODEL env var
    3. The provided fallback value
    """
    provider = provider.strip().lower()
    _ENV_MAP = {
        "gemini": "GEMINI_MODEL",
        "openrouter": "OPENROUTER_MODEL",
        "groq": "GROQ_MODEL",
    }
    env_key = _ENV_MAP.get(provider)
    if env_key:
        val = os.environ.get(env_key, "").strip()
        if val:
            return val
    return fallback


def naive_response_schema() -> dict:
    """JSON schema for free-taxonomy (own-words) classification responses.

    Matches prompting._naive_json_contract. Previously the Gemini path forced
    the ODC schema even for the naive prompt; free taxonomy now gets its own.
    """
    return {
        "type": "object",
        "properties": {
            "defect_type": {"type": "string"},
            "confidence": {"type": "number"},
            "reasoning_summary": {"type": "string"},
            "root_cause": {"type": "string"},
            "symptom": {"type": "string"},
        },
        "required": ["defect_type", "confidence", "reasoning_summary", "root_cause", "symptom"],
    }


def classification_response_schema(taxonomy_mode: str = "closed") -> dict:
    """JSON schema for the classification response.

    In open taxonomy mode (RQ2 coverage study) three extra fields are added
    for the "Other" escape label. They are nullable here; the requirement
    that they be present when odc_type == "Other" is enforced in
    pipeline._validate_classification_payload, keeping the schema
    perturbation between the closed and open passes minimal.
    """
    other_properties: dict[str, dict] = {}
    if taxonomy_mode == "open":
        other_properties = {
            "other_justification": {"type": ["string", "null"]},
            "nearest_type": {"type": ["string", "null"]},
            "other_confidence": {"type": ["number", "null"]},
        }
    return {
        "type": "object",
        "properties": {
            "odc_type": {"type": "string"},
            **other_properties,
            "family": {"type": ["string", "null"]},
            # Opener attribute (v5.2 §3.3): single-select, enum-constrained.
            # The 13 official categories + "Unknown" (§5.1). Impact is judged
            # from failure behaviour, never from the fix.
            "impact": {"type": "string", "enum": allowed_impact_names()},
            "target": {"type": ["string", "null"]},
            "qualifier": {"type": ["string", "null"]},
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
            "family",
            "impact",
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


def _urlopen_json(
    request: urllib.request.Request,
    *,
    max_retries: int = 5,
    base_delay: float = 2.0,
    max_delay: float = 60.0,
    retry_status_codes: set[int] | None = None,
) -> str:
    """Make an HTTP request with automatic retry on transient failures.

    Retries on the codes in retry_status_codes (default {429, 500, 502, 503})
    with exponential backoff + jitter. Anything else fails immediately, and
    every raised LLMError carries .status_code so callers doing multi-key
    failover (LLMClient._request_with_key_failover) can tell a key-specific
    problem (401/403/429) from an unrelated one.
    """
    import random
    import time
    from . import console

    _RETRYABLE_STATUS_CODES = retry_status_codes if retry_status_codes is not None else {429, 500, 502, 503}

    last_exception: Exception | None = None

    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(request, timeout=300) as response:
                return response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            last_exception = exc

            if exc.code not in _RETRYABLE_STATUS_CODES:
                # Non-retryable (or, for the failover wrapper, deliberately
                # not-retried-on-this-key) — fail immediately.
                raise LLMError(f"LLM request failed with status {exc.code}: {body}", status_code=exc.code) from exc

            # Check for Retry-After header (some APIs send it with 429)
            retry_after = exc.headers.get("Retry-After") if exc.headers else None
            if retry_after:
                try:
                    wait = min(float(retry_after), max_delay)
                except ValueError:
                    wait = base_delay * (2 ** attempt)
            else:
                # Exponential backoff + jitter
                wait = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)

            remaining = max_retries - attempt - 1
            console.warn(
                f"LLM request failed (HTTP {exc.code}). "
                f"Retrying in {wait:.1f}s... ({remaining} attempt(s) left)"
            )
            time.sleep(wait)

            # Rebuild the request since the body stream is consumed
            request = urllib.request.Request(
                url=request.full_url,
                data=request.data,
                headers=dict(request.headers),
                method=request.get_method(),
            )

        except urllib.error.URLError as exc:
            last_exception = exc
            remaining = max_retries - attempt - 1
            if remaining <= 0:
                raise LLMError(f"LLM request failed after {max_retries} attempts: {exc}") from exc

            wait = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
            console.warn(
                f"LLM network error: {exc.reason}. "
                f"Retrying in {wait:.1f}s... ({remaining} attempt(s) left)"
            )
            time.sleep(wait)

            # Rebuild the request
            request = urllib.request.Request(
                url=request.full_url,
                data=request.data,
                headers=dict(request.headers),
                method=request.get_method(),
            )

    # All retries exhausted
    if isinstance(last_exception, urllib.error.HTTPError):
        raise LLMError(
            f"LLM request failed after {max_retries} attempts "
            f"(last status: {last_exception.code}). The API may be under heavy load. "
            f"Try again in a few minutes.",
            status_code=last_exception.code,
        ) from last_exception
    raise LLMError(f"LLM request failed after {max_retries} attempts: {last_exception}") from last_exception

