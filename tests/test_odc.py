import unittest

from d4j_odc_pipeline.odc import model_slug, resolve_effective_tag


class ModelSlugTests(unittest.TestCase):
    def test_sanitizes_slashes(self) -> None:
        self.assertEqual(model_slug("groq", "openai/gpt-oss-120b"), "groq-openai-gpt-oss-120b")

    def test_keeps_dots_and_dashes(self) -> None:
        self.assertEqual(model_slug("sambanova", "DeepSeek-V3.2"), "sambanova-DeepSeek-V3.2")

    def test_different_providers_same_model_name_dont_collide(self) -> None:
        a = model_slug("groq", "llama-3.3-70b")
        b = model_slug("openrouter", "llama-3.3-70b")
        self.assertNotEqual(a, b)


class ResolveEffectiveTagTests(unittest.TestCase):
    """See odc.py::resolve_effective_tag docstring for the 4 rules — this
    mechanism is what lets a second --model run the same condition without
    colliding with or renaming the first model's (or the committed 854-bug
    corpus's) artifacts."""

    def test_no_existing_checkpoint_stays_bare(self) -> None:
        tag = resolve_effective_tag("few-open", "gemini", "gemini-2.5-flash", None)
        self.assertEqual(tag, "few-open")

    def test_legacy_checkpoint_without_model_keys_stays_bare(self) -> None:
        """Every checkpoint written before this mechanism existed — including
        the committed 854-bug corpus — has no model/provider keys at all."""
        tag = resolve_effective_tag("few-open", "gemini", "gemini-2.5-flash", {"manifest_hash": "abc"})
        self.assertEqual(tag, "few-open")

    def test_same_model_resume_stays_bare(self) -> None:
        existing = {"provider": "gemini", "model": "gemini-2.5-flash"}
        tag = resolve_effective_tag("few-open", "gemini", "gemini-2.5-flash", existing)
        self.assertEqual(tag, "few-open")

    def test_different_model_gets_suffixed(self) -> None:
        existing = {"provider": "gemini", "model": "gemini-2.5-flash"}
        tag = resolve_effective_tag("few-open", "sambanova", "DeepSeek-V3.2", existing)
        self.assertEqual(tag, "few-open.sambanova-DeepSeek-V3.2")

    def test_different_provider_same_model_name_gets_suffixed(self) -> None:
        existing = {"provider": "groq", "model": "llama-3.3-70b"}
        tag = resolve_effective_tag("zero-free", "openrouter", "llama-3.3-70b", existing)
        self.assertEqual(tag, "zero-free.openrouter-llama-3.3-70b")


if __name__ == "__main__":
    unittest.main()
