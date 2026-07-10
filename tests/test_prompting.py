import json
import unittest

from d4j_odc_pipeline.models import BugContext, Failure, StackFrame
from d4j_odc_pipeline.prompting import (
    build_messages,
    sanitize_bug_info,
    sanitize_bug_report,
)


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
        bug_info=kwargs.get("bug_info", ""),
        bug_report_content=kwargs.get("bug_report_content", ""),
        fix_diff=kwargs.get("fix_diff", ""),
    )


class PromptingTests(unittest.TestCase):
    def test_prompt_excludes_hidden_oracle(self) -> None:
        context = _make_context()
        messages = build_messages(context, "closed", "few")
        combined = "\n".join(message["content"] for message in messages)
        self.assertIn("tests.trigger", combined)
        self.assertNotIn("org.example.Hidden", combined)
        # The old odc_opener_hints/odc_closer_hints heuristic payload was
        # removed entirely (docs/odc_alignment_audit.md §4.4) — it anchored
        # the LLM's opener judgments and leaked ODC vocabulary into zero-free.
        self.assertNotIn('"odc_opener_hints"', combined)
        self.assertNotIn('"odc_closer_hints"', combined)

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

    def test_naive_excludes_impact_vocabulary(self) -> None:
        """zero-free must stay ODC-free: no Impact attribute anywhere."""
        context = _make_context()
        messages = build_messages(context, "free", "zero")
        combined = "\n".join(message["content"] for message in messages)
        self.assertNotIn("ODC Impact", combined)
        self.assertNotIn("Integrity/Security", combined)
        self.assertNotIn('"impact"', combined)


class ImpactPromptTests(unittest.TestCase):
    """The v5.2 §3.3 Impact attribute must be taught to few/scientific prompts."""

    def test_few_includes_impact_definitions(self) -> None:
        context = _make_context()
        system = build_messages(context, "open", "few")[0]["content"]
        self.assertIn("ODC Impact", system)
        # Spot-check a handful of the 13 categories are actually defined.
        for name in ("Reliability", "Performance", "Capability", "Usability", "Accessibility"):
            self.assertIn(name, system)
        self.assertIn("Unknown", system)

    def test_few_json_contract_requires_impact(self) -> None:
        context = _make_context()
        system = build_messages(context, "closed", "few")[0]["content"]
        self.assertIn('"impact"', system)

    def test_few_user_prompt_instructs_impact_selection(self) -> None:
        context = _make_context()
        user = build_messages(context, "closed", "few")[1]["content"]
        self.assertIn("impact", user.lower())


class SanitizationTests(unittest.TestCase):
    """Pre-fix payloads must contain no fix-derived information
    (docs/odc_alignment_audit.md §7)."""

    _BUG_INFO = """Summary of configuration for Project: Chart
--------------------------------------------------------------------------------
    Project ID: Chart
--------------------------------------------------------------------------------

Summary for Bug: Chart-10
--------------------------------------------------------------------------------
Revision ID (fixed version):
1065
--------------------------------------------------------------------------------
Revision date (fixed version):
2008-06-10 00:32:29 -0700
--------------------------------------------------------------------------------
Bug report id:
UNKNOWN
--------------------------------------------------------------------------------
Root cause in triggering tests:
 - org.jfree.chart.imagemap.junit.StandardToolTipTagFragmentGeneratorTests::testGenerateURLFragment
   --> junit.framework.ComparisonFailure: expected but was
--------------------------------------------------------------------------------
List of modified sources:
 - org.jfree.chart.imagemap.TheActualFixedClass
--------------------------------------------------------------------------------"""

    def test_sanitize_bug_info_drops_modified_sources(self) -> None:
        cleaned = sanitize_bug_info(self._BUG_INFO)
        self.assertNotIn("List of modified sources", cleaned)
        self.assertNotIn("TheActualFixedClass", cleaned)

    def test_sanitize_bug_info_drops_fixed_revision(self) -> None:
        cleaned = sanitize_bug_info(self._BUG_INFO)
        self.assertNotIn("Revision ID (fixed version)", cleaned)
        self.assertNotIn("Revision date (fixed version)", cleaned)
        self.assertNotIn("1065", cleaned)

    def test_sanitize_bug_info_keeps_triggering_tests(self) -> None:
        cleaned = sanitize_bug_info(self._BUG_INFO)
        self.assertIn("Root cause in triggering tests", cleaned)
        self.assertIn("testGenerateURLFragment", cleaned)
        self.assertIn("Project ID: Chart", cleaned)

    def test_sanitize_bug_info_empty_input(self) -> None:
        self.assertEqual("", sanitize_bug_info(""))

    def test_sanitize_bug_report_jira_api_format(self) -> None:
        report = (
            "Title: NPE in Foo\n"
            "Type: Bug | Priority: Major | Status: Resolved | Resolution: Fixed\n"
            "\nDescription:\nFoo throws NPE when bar is null.\n"
            "\nComments:\n"
            "\n[dev]: Fixed in commit abc123, thanks for the report."
        )
        cleaned = sanitize_bug_report(report)
        self.assertIn("Foo throws NPE when bar is null", cleaned)
        self.assertIn("Type: Bug", cleaned)
        self.assertIn("Priority: Major", cleaned)
        self.assertNotIn("Status:", cleaned)
        self.assertNotIn("Resolution:", cleaned)
        self.assertNotIn("Fixed in commit", cleaned)
        self.assertNotIn("Comments:", cleaned)

    def test_sanitize_bug_report_github_api_format(self) -> None:
        report = (
            "Title: Crash on empty input\n"
            "State: closed | Labels: bug\n"
            "\nDescription:\nCrashes when input is empty.\n"
            "\nComments:\n"
            "\n[maintainer]: Fixed by #123, closing."
        )
        cleaned = sanitize_bug_report(report)
        self.assertIn("Crashes when input is empty", cleaned)
        self.assertIn("Labels: bug", cleaned)
        self.assertNotIn("State:", cleaned)
        self.assertNotIn("Fixed by #123", cleaned)

    def test_sanitize_bug_report_sourceforge_flattened(self) -> None:
        report = (
            "JFreeChart / Bugs / #868 ShapeUtilities.equal Summary Files ... "
            "Description of the actual bug goes here. "
            "Logged In: YES user_id=112975 Originator: NO Fixed in CVS for the "
            "upcoming 1.0.13 release. Regards, Dave Gilbert "
            "If you would like to refer to this comment somewhere else in this "
            "project, copy and paste the following link: Log in to post a comment."
        )
        cleaned = sanitize_bug_report(report)
        self.assertIn("Description of the actual bug goes here", cleaned)
        self.assertNotIn("Fixed in CVS", cleaned)
        self.assertNotIn("Logged In", cleaned)

    def test_sanitize_bug_report_sourceforge_first_comment_leak(self) -> None:
        """Regression (found via corpus scan, Chart_1): the leak-revealing
        text lives INSIDE the first comment, textually BEFORE the per-comment
        boilerplate link — truncating only at that link leaves the first
        comment's own disclosure intact. Must truncate at the 'Discussion'
        section header instead, which precedes ALL comments including the
        first."""
        report = (
            "The variable dataset is guaranteed to be null in this location. "
            "This is trunk as of 2010-02-08. "
            "Discussion David Gilbert - 2010-02-09 Good spot. That was the "
            "result of a careless commit by me. I've committed the fix. "
            "If you would like to refer to this comment somewhere else in "
            "this project, copy and paste the following link: "
            "Log in to post a comment."
        )
        cleaned = sanitize_bug_report(report)
        self.assertIn("guaranteed to be null in this location", cleaned)
        self.assertNotIn("I've committed the fix", cleaned)
        self.assertNotIn("Discussion", cleaned)

    def test_sanitize_bug_report_json_status_and_second_comment(self) -> None:
        """Regression (found via corpus scan, Closure_90): Google Code-style
        raw JSON reports carry an unquoted-colon '\"status\":\"Fixed\"' key,
        and comments[1:] (everything after the original report) routinely
        discusses the fix."""
        report = (
            '{"id":274,"status":"Fixed","summary":"warning when used with typedef",'
            '"comments":[{"id":0,"commenterId":-123,"content":'
            '"What steps will reproduce the problem? 1. Compile this code.",'
            '"timestamp":1288303422,"attachments":[]},'
            '{"id":1,"commenterId":-456,"content":'
            '"thanks for the report. the fix will get committed on monday.",'
            '"timestamp":1288394328,"attachments":[]}]}'
        )
        cleaned = sanitize_bug_report(report)
        self.assertIn("What steps will reproduce the problem", cleaned)
        self.assertIn("warning when used with typedef", cleaned)
        self.assertNotIn('"status":"Fixed"', cleaned)
        self.assertNotIn("will get committed on monday", cleaned)
        self.assertNotIn('"id":1,"commenterId"', cleaned)

    def test_sanitize_bug_report_preserves_pipes_in_description(self) -> None:
        """Only pure meta lines (every segment a known key) get rewritten —
        a description that happens to contain '|' must survive untouched."""
        report = "Title: Foo\n\nDescription:\nUse a | separator in your config.\n"
        cleaned = sanitize_bug_report(report)
        self.assertIn("Use a | separator in your config.", cleaned)

    def test_sanitize_bug_report_empty_input(self) -> None:
        self.assertEqual("", sanitize_bug_report(""))


class PairedArmSanitizationRegressionTests(unittest.TestCase):
    """End-to-end regression: build_messages must sanitize the pre-fix arm
    and leave the post-fix arm untouched (docs/odc_alignment_audit.md §7)."""

    _BUG_INFO = SanitizationTests._BUG_INFO
    _BUG_REPORT = (
        "Title: Off-by-one in URL fragment\n"
        "Type: Bug | Priority: Major | Status: Resolved | Resolution: Fixed\n"
        "\nDescription:\nThe generated URL fragment double-encodes quotes.\n"
        "\nComments:\n\n[dev]: Fixed in CVS, closed-fixed."
    )

    def test_prefix_payload_has_no_fix_leaks(self) -> None:
        context = _make_context(bug_info=self._BUG_INFO, bug_report_content=self._BUG_REPORT)
        user = build_messages(context, "closed", "few")[1]["content"]
        self.assertNotIn("List of modified sources", user)
        self.assertNotIn("TheActualFixedClass", user)
        self.assertNotIn("Fixed in CVS", user)
        self.assertNotIn("closed-fixed", user)
        self.assertNotIn("Resolution:", user)
        # Legitimate pre-fix content must survive.
        self.assertIn("double-encodes quotes", user)
        self.assertIn("triggering tests", user)

    def test_postfix_payload_keeps_bug_info_and_report_untouched(self) -> None:
        context = _make_context(
            bug_info=self._BUG_INFO,
            bug_report_content=self._BUG_REPORT,
            fix_diff="--- a/Foo.java\n+++ b/Foo.java\n@@ -1 +1 @@\n-old\n+new\n",
        )
        user = build_messages(context, "closed", "few")[1]["content"]
        self.assertIn("List of modified sources", user)
        self.assertIn("TheActualFixedClass", user)
        self.assertIn("Fixed in CVS", user)
        self.assertIn("Resolution:", user)


if __name__ == "__main__":
    unittest.main()
