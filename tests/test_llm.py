import os
import unittest

from d4j_odc_pipeline.llm import LLMClient, classification_response_schema, default_api_key_env


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
        self.assertIn("age", schema["properties"])
        self.assertIn("source", schema["properties"])
        self.assertIn("inferred_activity", schema["properties"])
        self.assertIn("inferred_triggers", schema["properties"])
        self.assertIn("inferred_impact", schema["properties"])
        self.assertNotIn("target", schema["required"])


if __name__ == "__main__":
    unittest.main()
