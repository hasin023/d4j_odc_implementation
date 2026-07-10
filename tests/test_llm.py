import io
import json
import os
import unittest
import urllib.error
from unittest.mock import patch

from d4j_odc_pipeline.llm import (
    LLMClient,
    LLMError,
    classification_response_schema,
    default_api_key_env,
    naive_response_schema,
)


class LLMTests(unittest.TestCase):
    def test_default_api_key_env_for_gemini(self) -> None:
        self.assertEqual("GEMINI_API_KEY", default_api_key_env("gemini"))
        self.assertEqual("OPENROUTER_API_KEY", default_api_key_env("openrouter"))

    def test_gemini_client_uses_gemini_base_url(self) -> None:
        old_api_key = os.environ.get("GEMINI_API_KEY")
        old_base_url = os.environ.get("GEMINI_BASE_URL")
        os.environ["GEMINI_API_KEY"] = "test-key"
        os.environ["GEMINI_BASE_URL"] = "https://example.invalid/v1beta"
        try:
            client = LLMClient.from_env(provider="gemini", model="gemini-3.1-flash-lite-preview")
            self.assertEqual("https://example.invalid/v1beta", client.settings.base_url)
        finally:
            if old_api_key is None:
                os.environ.pop("GEMINI_API_KEY", None)
            else:
                os.environ["GEMINI_API_KEY"] = old_api_key
            if old_base_url is None:
                os.environ.pop("GEMINI_BASE_URL", None)
            else:
                os.environ["GEMINI_BASE_URL"] = old_base_url

    def test_classification_schema_requires_key_fields(self) -> None:
        schema = classification_response_schema()
        self.assertEqual("object", schema["type"])
        self.assertIn("odc_type", schema["required"])
        self.assertIn("alternative_types", schema["properties"])
        self.assertIn("target", schema["properties"])
        self.assertIn("qualifier", schema["properties"])
        self.assertNotIn("target", schema["required"])

    def test_classification_schema_impact_is_enum_and_required(self) -> None:
        """Impact (v5.2 §3.3 opener attribute) is single-select and required —
        'Unknown' is the escape hatch, not an unconstrained/omittable field."""
        schema = classification_response_schema()
        self.assertIn("impact", schema["required"])
        impact_prop = schema["properties"]["impact"]
        self.assertEqual("string", impact_prop["type"])
        self.assertIn("Reliability", impact_prop["enum"])
        self.assertIn("Capability", impact_prop["enum"])
        self.assertIn("Unknown", impact_prop["enum"])
        self.assertEqual(14, len(impact_prop["enum"]))  # 13 v5.2 categories + Unknown

    def test_naive_schema_has_no_odc_or_impact_fields(self) -> None:
        """zero-free's schema must stay ODC-free — no impact field either."""
        schema = naive_response_schema()
        self.assertNotIn("impact", schema["properties"])
        self.assertNotIn("odc_type", schema["properties"])


def _fake_gemini_response(text: str) -> str:
    return json.dumps({"candidates": [{"content": {"parts": [{"text": text}]}}]})


def _http_error(code: int) -> urllib.error.HTTPError:
    return urllib.error.HTTPError(
        url="https://example.invalid",
        code=code,
        msg="error",
        hdrs={},
        fp=io.BytesIO(b'{"error": "boom"}'),
    )


class _FakeResponse:
    """Minimal context-manager stand-in for urlopen()'s successful response."""

    def __init__(self, body: bytes) -> None:
        self._body = body

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, *exc_info: object) -> bool:
        return False

    def read(self) -> bytes:
        return self._body


def _key_from_request(request) -> str | None:
    for key, value in request.headers.items():
        if key.lower() == "x-goog-api-key":
            return value
    return None


class KeyRotationTests(unittest.TestCase):
    """--<PROVIDER>_API_KEYS rotation: resolved per-request, not per-construction.

    Uses a distinct api_key_env per test so each test gets its own rotation
    cache entry (the cycle cache is module-level, shared across the process).
    """

    def _capture_keys_used(self, header_name: str) -> list[str]:
        # urllib.request.Request stores header keys via str.capitalize()
        # (e.g. "x-goog-api-key" -> "X-goog-api-key"), so match case-insensitively
        # rather than assuming a specific casing convention.
        seen: list[str] = []

        def fake_urlopen(request, **kwargs):
            matches = [v for k, v in request.headers.items() if k.lower() == header_name.lower()]
            seen.append(matches[0] if matches else None)
            return _fake_gemini_response("ok")

        return seen, fake_urlopen

    def test_single_key_is_stable_across_calls(self) -> None:
        with patch.dict(os.environ, {"TEST_ROTATION_SINGLE_KEY": "only-key"}, clear=False):
            client = LLMClient.from_env(
                provider="gemini", model="m", api_key_env="TEST_ROTATION_SINGLE_KEY"
            )
            seen, fake_urlopen = self._capture_keys_used("x-goog-api-key")
            with patch("d4j_odc_pipeline.llm._urlopen_json", side_effect=fake_urlopen):
                for _ in range(4):
                    client.complete([{"role": "user", "content": "hi"}])
            self.assertEqual(["only-key"] * 4, seen)

    def test_multiple_keys_rotate_per_request_within_one_client(self) -> None:
        with patch.dict(
            os.environ, {"TEST_ROTATION_MULTI_KEYS": "k1, k2, k3"}, clear=False
        ):
            client = LLMClient.from_env(
                provider="gemini", model="m", api_key_env="TEST_ROTATION_MULTI_KEY"
            )
            seen, fake_urlopen = self._capture_keys_used("x-goog-api-key")
            with patch("d4j_odc_pipeline.llm._urlopen_json", side_effect=fake_urlopen):
                for _ in range(5):
                    client.complete([{"role": "user", "content": "hi"}])
            # Every single request rotates — even within ONE client instance,
            # e.g. across the multiple turns of one bug's scientific loop.
            self.assertEqual(["k1", "k2", "k3", "k1", "k2"], seen)

    def test_rotation_continues_across_separately_constructed_clients(self) -> None:
        """Simulates the real batch pattern: a fresh LLMClient is built per bug."""
        with patch.dict(
            os.environ, {"TEST_ROTATION_CROSS_CLIENT_KEYS": "a,b"}, clear=False
        ):
            seen, fake_urlopen = self._capture_keys_used("x-goog-api-key")
            with patch("d4j_odc_pipeline.llm._urlopen_json", side_effect=fake_urlopen):
                # Bug 1: new client, one call (e.g. a zero/few-strategy bug).
                client_bug1 = LLMClient.from_env(
                    provider="gemini", model="m", api_key_env="TEST_ROTATION_CROSS_CLIENT_KEY"
                )
                client_bug1.complete([{"role": "user", "content": "hi"}])
                # Bug 2: a BRAND NEW client (as classify_bug_context builds per
                # bug) must NOT reset back to key "a" — rotation is continuous.
                client_bug2 = LLMClient.from_env(
                    provider="gemini", model="m", api_key_env="TEST_ROTATION_CROSS_CLIENT_KEY"
                )
                client_bug2.complete([{"role": "user", "content": "hi"}])
            self.assertEqual(["a", "b"], seen)

    def test_plural_env_var_takes_priority_over_singular(self) -> None:
        with patch.dict(
            os.environ,
            {
                "TEST_ROTATION_PRIORITY": "singular-key",
                "TEST_ROTATION_PRIORITYS": "plural-key-1,plural-key-2",
            },
            clear=False,
        ):
            client = LLMClient.from_env(
                provider="gemini", model="m", api_key_env="TEST_ROTATION_PRIORITY"
            )
            seen, fake_urlopen = self._capture_keys_used("x-goog-api-key")
            with patch("d4j_odc_pipeline.llm._urlopen_json", side_effect=fake_urlopen):
                client.complete([{"role": "user", "content": "hi"}])
                client.complete([{"role": "user", "content": "hi"}])
            self.assertEqual(["plural-key-1", "plural-key-2"], seen)


class KeyFailoverTests(unittest.TestCase):
    """A key that's dead (401/403) or rate-limited (429) fails over to the
    next key in the pool instead of retrying/erroring on that same key."""

    def test_failover_to_next_key_on_403(self) -> None:
        with patch.dict(os.environ, {"TEST_FAILOVER_403_KEYS": "bad-key,good-key"}, clear=False):
            client = LLMClient.from_env(
                provider="gemini", model="m", api_key_env="TEST_FAILOVER_403_KEY"
            )
            calls: list[str] = []

            def fake_urlopen(request, **kwargs):
                key = _key_from_request(request)
                calls.append(key)
                if key == "bad-key":
                    raise _http_error(403)
                return _FakeResponse(_fake_gemini_response("classified").encode())

            with patch(
                "d4j_odc_pipeline.llm.urllib.request.urlopen", side_effect=fake_urlopen
            ):
                result = client.complete([{"role": "user", "content": "hi"}])
            self.assertEqual("classified", result)
            self.assertEqual(["bad-key", "good-key"], calls)

    def test_failover_to_next_key_on_429_skips_backoff_delay(self) -> None:
        with patch.dict(
            os.environ, {"TEST_FAILOVER_429_KEYS": "limited-key,fresh-key"}, clear=False
        ):
            client = LLMClient.from_env(
                provider="gemini", model="m", api_key_env="TEST_FAILOVER_429_KEY"
            )
            calls: list[str] = []

            def fake_urlopen(request, **kwargs):
                key = _key_from_request(request)
                calls.append(key)
                if key == "limited-key":
                    raise _http_error(429)
                return _FakeResponse(_fake_gemini_response("classified").encode())

            with (
                patch("d4j_odc_pipeline.llm.urllib.request.urlopen", side_effect=fake_urlopen),
                patch("time.sleep") as mock_sleep,
            ):
                result = client.complete([{"role": "user", "content": "hi"}])
            self.assertEqual("classified", result)
            self.assertEqual(["limited-key", "fresh-key"], calls)
            # With another key available, 429 fails over immediately rather
            # than burning the same-key exponential-backoff wait.
            mock_sleep.assert_not_called()

    def test_single_key_429_still_backs_off_same_key(self) -> None:
        """No other key to fall back to -> preserves the original same-key
        backoff-and-retry behavior exactly as before failover existed."""
        with patch.dict(
            os.environ, {"TEST_FAILOVER_SINGLE_429_KEY": "only-key"}, clear=False
        ):
            client = LLMClient.from_env(
                provider="gemini", model="m", api_key_env="TEST_FAILOVER_SINGLE_429_KEY"
            )
            call_count = {"n": 0}

            def fake_urlopen(request, **kwargs):
                call_count["n"] += 1
                if call_count["n"] < 3:
                    raise _http_error(429)
                return _FakeResponse(_fake_gemini_response("classified").encode())

            with (
                patch("d4j_odc_pipeline.llm.urllib.request.urlopen", side_effect=fake_urlopen),
                patch("time.sleep") as mock_sleep,
            ):
                result = client.complete([{"role": "user", "content": "hi"}])
            self.assertEqual("classified", result)
            self.assertEqual(3, call_count["n"])
            self.assertEqual(2, mock_sleep.call_count)

    def test_all_keys_exhausted_raises_with_status_code(self) -> None:
        with patch.dict(
            os.environ, {"TEST_FAILOVER_ALL_BAD_KEYS": "bad1,bad2"}, clear=False
        ):
            client = LLMClient.from_env(
                provider="gemini", model="m", api_key_env="TEST_FAILOVER_ALL_BAD_KEY"
            )

            def fake_urlopen(request, **kwargs):
                raise _http_error(403)

            with patch(
                "d4j_odc_pipeline.llm.urllib.request.urlopen", side_effect=fake_urlopen
            ):
                with self.assertRaises(LLMError) as ctx:
                    client.complete([{"role": "user", "content": "hi"}])
            self.assertEqual(403, ctx.exception.status_code)


if __name__ == "__main__":
    unittest.main()
