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
        messages = build_messages(context, "scientific")
        combined = "\n".join(message["content"] for message in messages)
        self.assertIn("tests.trigger", combined)
        self.assertNotIn("org.example.Hidden", combined)
        self.assertIn('"odc_opener_hints"', combined)
        self.assertIn('"odc_closer_hints"', combined)

    # ── Direct style isolation tests ─────────────────────────────────

    def test_direct_excludes_scientific_protocol(self) -> None:
        context = _make_context()
        messages = build_messages(context, "direct")
        system = messages[0]["content"]
        self.assertNotIn("Scientific Debugging Protocol", system)
        self.assertNotIn("Step 1 — OBSERVE", system)
        self.assertNotIn("Step 5 — CONCLUDE", system)

    def test_direct_excludes_diagnostic_tree(self) -> None:
        context = _make_context()
        messages = build_messages(context, "direct")
        system = messages[0]["content"]
        self.assertNotIn("Classification Decision Process", system)
        self.assertNotIn("Is a condition/guard/validation missing or wrong?", system)
        self.assertNotIn("strongly consider **Checking**", system)

    def test_direct_excludes_few_shot_examples(self) -> None:
        context = _make_context()
        messages = build_messages(context, "direct")
        system = messages[0]["content"]
        self.assertNotIn("Classification Examples", system)
        self.assertNotIn("Example 1: Checking", system)
        self.assertNotIn("Example 3: Algorithm/Method", system)

    def test_direct_includes_odc_taxonomy(self) -> None:
        context = _make_context()
        messages = build_messages(context, "direct")
        system = messages[0]["content"]
        self.assertIn("Algorithm/Method", system)
        self.assertIn("Checking", system)
        self.assertIn("Function/Class/Object", system)
        self.assertIn("Interface/O-O Messages", system)

    def test_direct_includes_json_contract(self) -> None:
        context = _make_context()
        messages = build_messages(context, "direct")
        system = messages[0]["content"]
        self.assertIn('"odc_type"', system)
        self.assertIn('"confidence"', system)
        self.assertIn('"reasoning_summary"', system)

    def test_direct_includes_anti_bias_rules(self) -> None:
        context = _make_context()
        messages = build_messages(context, "direct")
        system = messages[0]["content"]
        self.assertIn("Do NOT default to", system)
        self.assertIn("Do not use benchmark familiarity", system)

    # ── Scientific style includes everything ──────────────────────────

    def test_scientific_includes_protocol(self) -> None:
        context = _make_context()
        messages = build_messages(context, "scientific")
        system = messages[0]["content"]
        self.assertIn("Scientific Debugging Protocol", system)
        self.assertIn("Classification Decision Process", system)
        self.assertIn("Classification Examples", system)

    # ── Evidence parity between styles (RQ2.2 confound control) ──────

    def test_user_payload_identical_between_styles(self) -> None:
        """Both prompt styles must produce the same user payload (identical evidence)."""
        context = _make_context()
        sci_user = build_messages(context, "scientific")[1]["content"]
        dir_user = build_messages(context, "direct")[1]["content"]
        self.assertEqual(sci_user, dir_user)

    # ── Naive style tests (RQ2.3) ─────────────────────────────────────

    def test_naive_excludes_odc_taxonomy(self) -> None:
        """Naive prompt must not contain any ODC type names or taxonomy."""
        context = _make_context()
        messages = build_messages(context, "naive")
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
        messages = build_messages(context, "naive")
        system = messages[0]["content"]
        self.assertNotIn("Do NOT default to", system)
        self.assertNotIn("Do not use benchmark familiarity", system)

    def test_naive_excludes_scientific_protocol(self) -> None:
        context = _make_context()
        messages = build_messages(context, "naive")
        system = messages[0]["content"]
        self.assertNotIn("Scientific Debugging Protocol", system)
        self.assertNotIn("Classification Decision Process", system)
        self.assertNotIn("Classification Examples", system)

    def test_naive_excludes_odc_json_contract(self) -> None:
        """Naive prompt uses a simplified JSON schema without ODC fields."""
        context = _make_context()
        messages = build_messages(context, "naive")
        system = messages[0]["content"]
        self.assertNotIn('"odc_type"', system)
        self.assertNotIn('"family"', system)
        self.assertNotIn('"qualifier"', system)
        self.assertNotIn('"alternative_types"', system)

    def test_naive_includes_simplified_schema(self) -> None:
        """Naive prompt includes its own simplified JSON schema."""
        context = _make_context()
        messages = build_messages(context, "naive")
        system = messages[0]["content"]
        self.assertIn('"defect_type"', system)
        self.assertIn('"confidence"', system)
        self.assertIn('"reasoning_summary"', system)

    def test_naive_user_prompt_excludes_odc_references(self) -> None:
        """Naive user prompt must not reference ODC type names."""
        context = _make_context()
        messages = build_messages(context, "naive")
        user = messages[1]["content"]
        self.assertNotIn("odc_type must be one of", user)
        self.assertNotIn("Algorithm/Method", user)

    def test_naive_payload_has_same_evidence(self) -> None:
        """Naive prompt evidence payload has same structure as scientific/direct."""
        import json
        context = _make_context()
        naive_user = build_messages(context, "naive")[1]["content"]
        sci_user = build_messages(context, "scientific")[1]["content"]
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
