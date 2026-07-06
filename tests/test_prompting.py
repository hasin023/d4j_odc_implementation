import unittest

from d4j_odc_pipeline.models import BugContext, Failure, StackFrame
from d4j_odc_pipeline.prompting import build_messages


def _make_context(**kwargs) -> BugContext:
    """Helper to build a BugContext with sensible defaults."""
    return BugContext(
        project_id=kwargs.get("project_id", "Lang"),
        bug_id=kwargs.get("bug_id", 1),
        version_id=kwargs.get("version_id", "1b"),
        work_dir=kwargs.get("work_dir", "C:/tmp/Lang_1b"),
        created_at=kwargs.get("created_at", "2026-04-13T00:00:00+00:00"),
        defects4j_command=kwargs.get("defects4j_command", ["defects4j"]),
        metadata=kwargs.get("metadata", {
            "classes.modified": "org.example.Hidden",
            "tests.trigger": "FooTest::testOne",
        }),
        failures=kwargs.get("failures", [
            Failure(
                test_name="org.example.FooTest::testOne",
                test_class="org.example.FooTest",
                test_method="testOne",
                headline="java.lang.AssertionError",
                stack_trace=[],
                frames=[StackFrame("org.example.Foo", "fail", "Foo.java", 42, "raw")],
            )
        ]),
    )


class PromptingTests(unittest.TestCase):
    def test_prompt_excludes_hidden_oracle(self) -> None:
        context = _make_context()
        messages = build_messages(context, "closed", "few")
        combined = "\n".join(message["content"] for message in messages)
        self.assertIn("tests.trigger", combined)
        self.assertNotIn("org.example.Hidden", combined)
        self.assertIn('"odc_opener_hints"', combined)
        self.assertIn('"odc_closer_hints"', combined)

    # ── Direct style isolation tests ─────────────────────────────────







    def test_few_includes_protocol(self) -> None:
        context = _make_context()
        messages = build_messages(context, "closed", "few")
        system = messages[0]["content"]
        self.assertIn("Scientific Debugging Protocol", system)
        self.assertIn("Classification Decision Process", system)
        self.assertIn("Classification Examples", system)

    # ── Evidence parity between styles (RQ2.2 confound control) ──────

    def test_user_payload_identical_between_strategies(self) -> None:
        """few and zero must receive the SAME evidence payload (no evidence confound):
        only the instructions differ, the Evidence JSON block is byte-identical."""
        context = _make_context()
        few_user = build_messages(context, "closed", "few")[1]["content"]
        zero_user = build_messages(context, "free", "zero")[1]["content"]
        few_payload = few_user.split("Evidence:\n", 1)[1]
        zero_payload = zero_user.split("Evidence:\n", 1)[1]
        self.assertEqual(few_payload, zero_payload)

    # ── Naive style tests (RQ2.3) ─────────────────────────────────────

    def test_naive_excludes_odc_taxonomy(self) -> None:
        """Naive prompt must not contain any ODC type names or taxonomy."""
        context = _make_context()
        messages = build_messages(context, "free", "zero")
        system = messages[0]["content"]
        # No ODC type names at all
        self.assertNotIn("Algorithm/Method", system)
        self.assertNotIn("Checking", system)
        self.assertNotIn("Function/Class/Object", system)
        self.assertNotIn("Interface/O-O Messages", system)
        self.assertNotIn("Timing/Serialization", system)
        self.assertNotIn("Assignment/Initialization", system)
        self.assertNotIn("Relationship", system)
        # No ODC terminology
        self.assertNotIn("Orthogonal Defect Classification", system)
        self.assertNotIn("ODC", system)

    def test_naive_excludes_anti_bias_rules(self) -> None:
        context = _make_context()
        messages = build_messages(context, "free", "zero")
        system = messages[0]["content"]
        self.assertNotIn("Do NOT default to", system)
        self.assertNotIn("Do not use benchmark familiarity", system)

    def test_naive_excludes_scientific_protocol(self) -> None:
        context = _make_context()
        messages = build_messages(context, "free", "zero")
        system = messages[0]["content"]
        self.assertNotIn("Scientific Debugging Protocol", system)
        self.assertNotIn("Classification Decision Process", system)
        self.assertNotIn("Classification Examples", system)

    def test_naive_excludes_odc_json_contract(self) -> None:
        """Naive prompt uses a simplified JSON schema without ODC fields."""
        context = _make_context()
        messages = build_messages(context, "free", "zero")
        system = messages[0]["content"]
        self.assertNotIn('"odc_type"', system)
        self.assertNotIn('"family"', system)
        self.assertNotIn('"qualifier"', system)
        self.assertNotIn('"alternative_types"', system)

    def test_naive_includes_simplified_schema(self) -> None:
        """Naive prompt includes its own simplified JSON schema."""
        context = _make_context()
        messages = build_messages(context, "free", "zero")
        system = messages[0]["content"]
        self.assertIn('"defect_type"', system)
        self.assertIn('"confidence"', system)
        self.assertIn('"reasoning_summary"', system)

    def test_naive_user_prompt_excludes_odc_references(self) -> None:
        """Naive user prompt must not reference ODC type names."""
        context = _make_context()
        messages = build_messages(context, "free", "zero")
        user = messages[1]["content"]
        self.assertNotIn("odc_type must be one of", user)
        self.assertNotIn("Algorithm/Method", user)

    def test_naive_payload_has_same_evidence(self) -> None:
        """Naive prompt evidence payload has same structure as scientific/direct."""
        import json
        context = _make_context()
        naive_user = build_messages(context, "free", "zero")[1]["content"]
        sci_user = build_messages(context, "closed", "few")[1]["content"]
        # Both should contain the same evidence JSON (after the rules header)
        naive_json = naive_user.split("Evidence:\n", 1)[1]
        sci_json = sci_user.split("Evidence:\n", 1)[1]
        naive_payload = json.loads(naive_json)
        sci_payload = json.loads(sci_json)
        # Same project, bug, snippets
        self.assertEqual(naive_payload["project_id"], sci_payload["project_id"])
        self.assertEqual(naive_payload["bug_id"], sci_payload["bug_id"])


if __name__ == "__main__":
    unittest.main()
