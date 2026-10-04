import re
import unittest
from pathlib import Path

from d4j_odc_pipeline.odc import ODC_TYPES, model_slug, resolve_effective_tag

IBM_DOC = Path(__file__).resolve().parent.parent / "docs" / "odc_doc.md"


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


class IbmDefinitionTests(unittest.TestCase):
    """Definitions and examples in ODC_TYPES must be IBM ODC v5.2 §4.2.1 word for word
    (docs/odc_doc.md). They drifted once: a paraphrase written before the doc was in the repo
    dropped 4 examples and 3 definition clauses. Our own guidance lives in `indicators` and
    `distinguish_from`, which this test does not check."""

    def _ibm_sections(self) -> dict[str, tuple[str, str]]:
        doc = IBM_DOC.read_text(encoding="utf-8")
        section = doc[doc.index("##### 4.2.1.1"):doc.index("#### 4.2.2")]
        parts = re.split(r"^##### 4\.2\.1\.\d (.+)$", section, flags=re.M)[1:]
        sections = {}
        for name, body in zip(parts[::2], parts[1::2]):
            definition, _, examples = body.partition("Examples:")
            items = re.findall(r"^\d+\. (.+)$", examples, flags=re.M)
            if name.strip() == "Interface/O-O Messages":
                # IBM writes this definition as two numbered lists; ODC_TYPES joins them.
                between, _, via = definition.partition("via")
                join = lambda t: ", ".join(re.findall(r"^\d+\. (.+)$", t, flags=re.M))
                definition = f"Communication problems between: {join(between)} via: {join(via)}."
            sections[name.strip()] = (
                " ".join(definition.split()),
                " ".join(f"({i}) {item.strip()}" for i, item in enumerate(items, 1)),
            )
        return sections

    def test_same_seven_types(self) -> None:
        self.assertEqual(set(self._ibm_sections()), set(ODC_TYPES))

    def test_definitions_are_ibm_verbatim(self) -> None:
        for name, (definition, _) in self._ibm_sections().items():
            with self.subTest(odc_type=name):
                self.assertEqual(ODC_TYPES[name]["summary"], definition)

    def test_examples_are_ibm_verbatim(self) -> None:
        for name, (_, examples) in self._ibm_sections().items():
            with self.subTest(odc_type=name):
                self.assertEqual(ODC_TYPES[name]["examples"], examples)
