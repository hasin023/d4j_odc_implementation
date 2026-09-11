import json
import unittest

from d4j_odc_pipeline.models import BugContext, Failure, StackFrame
from d4j_odc_pipeline.prompting import (
    _filter_stack_trace_noise,
    _strip_bug_info_noise,
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
        """few's system prompt is exactly taxonomy + decision tree + worked
        examples (docs/condition_model.md §4.3) — the "Scientific Debugging
        Protocol" block was a vestige of the retired narrated-single-shot
        condition (pilot-proven to change 0/6 labels) and was removed; it
        must not resurface."""
        context = _make_context()
        messages = build_messages(context, "closed", "few")
        system = messages[0]["content"]
        self.assertNotIn("Scientific Debugging Protocol", system)
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

    def test_sanitize_bug_report_formatted_comment_thread(self) -> None:
        """Regression (found via a live Closure-150 collect): web_fetch's
        _format_tracker_json now renders the Google Code comment array as
        "Comment N (date): text" lines instead of raw JSON, so the old
        _JSON_SECOND_COMMENT_RE truncation no longer matched — a
        fix-revealing final comment ("closed by revision r2240") leaked
        into the pre-fix arm undetected."""
        report = (
            "id: 61\n\n"
            "summary: Type checker misses annotations\n"
            "Comment 0 (2009-11-25): What steps will reproduce the problem?\n"
            "Comment 1 (2009-12-03): thanks for the report, still investigating.\n"
            "Comment 2 (2012-10-05): This issue was closed by revision r2240."
        )
        cleaned = sanitize_bug_report(report)
        self.assertIn("What steps will reproduce the problem", cleaned)
        self.assertNotIn("closed by revision", cleaned)
        self.assertNotIn("still investigating", cleaned)
        self.assertNotIn("Comment 1", cleaned)

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


class BugInfoNoiseStrippingTests(unittest.TestCase):
    """Local-machine paths / corpus-size stats carry zero signal for a
    single bug and strip in BOTH arms (unlike the fix-revealing sections),
    see docs/suspicious_frame_selection.md."""

    _RAW = """Summary of configuration for Project: Closure
--------------------------------------------------------------------------------
    Script dir: /root/defects4j/framework
      Base dir: /root/defects4j
    Major root: /root/defects4j/major
      Repo dir: /root/defects4j/project_repos
--------------------------------------------------------------------------------
    Project ID: Closure
       Program: closure-compiler
--------------------------------------------------------------------------------
           Vcs: Vcs::Git
    Repository: /root/defects4j/project_repos/closure-compiler.git
     Commit db: /root/defects4j/framework/projects/Closure/active-bugs.csv
Number of bugs: 174
--------------------------------------------------------------------------------"""

    def test_strips_local_paths_and_corpus_stats(self) -> None:
        cleaned = _strip_bug_info_noise(self._RAW)
        self.assertNotIn("Script dir:", cleaned)
        self.assertNotIn("Base dir:", cleaned)
        self.assertNotIn("Major root:", cleaned)
        self.assertNotIn("Repo dir:", cleaned)
        self.assertNotIn("Commit db:", cleaned)
        self.assertNotIn("Number of bugs:", cleaned)

    def test_keeps_legitimate_project_info(self) -> None:
        cleaned = _strip_bug_info_noise(self._RAW)
        self.assertIn("Project ID: Closure", cleaned)
        self.assertIn("Program: closure-compiler", cleaned)

    def test_empty_input(self) -> None:
        self.assertEqual("", _strip_bug_info_noise(""))

    def test_applies_in_both_arms_via_build_messages(self) -> None:
        prefix_context = _make_context(bug_info=self._RAW)
        postfix_context = _make_context(bug_info=self._RAW, fix_diff="--- a\n+++ b\n")
        prefix_user = build_messages(prefix_context, "closed", "few")[1]["content"]
        postfix_user = build_messages(postfix_context, "closed", "few")[1]["content"]
        self.assertNotIn("Script dir:", prefix_user)
        self.assertNotIn("Script dir:", postfix_user)


class StackTraceNoiseFilterTests(unittest.TestCase):
    """The raw first-N-lines excerpt used to be dominated by JDK reflection /
    Ant / JUnit runner boilerplate for assertion-style failures — filter
    those out so the budget goes to signal lines instead."""

    _TRACE = [
        "junit.framework.AssertionFailedError",
        "\tat junit.framework.Assert.fail(Assert.java:55)",
        "\tat junit.framework.Assert.assertTrue(Assert.java:22)",
        "\tat com.example.FooTest.testBar(FooTest.java:251)",
        "\tat java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)",
        "\tat org.apache.tools.ant.taskdefs.optional.junit.JUnitTestRunner.run(JUnitTestRunner.java:520)",
    ]

    def test_drops_framework_frames_keeps_signal(self) -> None:
        filtered = _filter_stack_trace_noise(self._TRACE, limit=15)
        self.assertIn("junit.framework.AssertionFailedError", filtered[0])
        joined = "\n".join(filtered)
        self.assertIn("com.example.FooTest.testBar", joined)
        self.assertNotIn("NativeMethodAccessorImpl", joined)
        self.assertNotIn("JUnitTestRunner", joined)
        self.assertNotIn("junit.framework.Assert.fail", joined)

    def test_respects_limit_on_kept_frames(self) -> None:
        trace = ["Exception"] + [f"\tat com.example.Foo{i}.bar(Foo{i}.java:{i})" for i in range(20)]
        filtered = _filter_stack_trace_noise(trace, limit=5)
        self.assertEqual(len(filtered), 6)  # headline + 5 frames

    def test_empty_trace(self) -> None:
        self.assertEqual(_filter_stack_trace_noise([], limit=15), [])

    def test_all_framework_keeps_only_headline(self) -> None:
        trace = ["Exception", "\tat java.lang.Thread.run(Thread.java:1)"]
        filtered = _filter_stack_trace_noise(trace, limit=15)
        self.assertEqual(filtered, ["Exception"])


class MetadataTestsRelevantCappingTests(unittest.TestCase):
    def test_relevant_list_collapsed_to_count(self) -> None:
        context = _make_context(metadata={
            "classes.modified": "org.example.Hidden",
            "tests.trigger": "FooTest::testOne",
            "tests.relevant": ";".join(f"org.example.Test{i}" for i in range(23)),
        })
        user = build_messages(context, "closed", "few")[1]["content"]
        self.assertNotIn("org.example.Test0", user)
        self.assertNotIn("org.example.Test22", user)
        self.assertIn("23 relevant test classes", user)
        self.assertIn("FooTest::testOne", user)


class FewContentCoverageRegressionTests(unittest.TestCase):
    """docs/condition_model.md §4.3: few must remain "the strongest static
    prompt" — the loop (scientific) has to outperform taxonomy + decision
    tree + worked examples, not a handicapped version of it. This guards
    that invariant against future conciseness edits: wording may shrink,
    but none of the 7 type definitions or 5 worked examples may disappear."""

    def test_all_seven_odc_types_present(self) -> None:
        context = _make_context()
        system = build_messages(context, "closed", "few")[0]["content"]
        for name in (
            "Algorithm/Method",
            "Assignment/Initialization",
            "Checking",
            "Timing/Serialization",
            "Function/Class/Object",
            "Interface/O-O Messages",
            "Relationship",
        ):
            self.assertIn(name, system)

    def test_all_five_worked_examples_present(self) -> None:
        context = _make_context()
        system = build_messages(context, "closed", "few")[0]["content"]
        for i in range(1, 6):
            self.assertIn(f"### Example {i}:", system)

    def test_decision_tree_still_covers_all_seven_boundaries(self) -> None:
        context = _make_context()
        system = build_messages(context, "closed", "few")[0]["content"]
        self.assertIn("Classification Decision Process", system)
        # 7 numbered diagnostic questions, one per type.
        for i in range(1, 8):
            self.assertIn(f"{i}. **", system)


class NotesExcludedFromPayloadTests(unittest.TestCase):
    """notes carries collection-run bookkeeping (compile/test/coverage exit
    codes, raw Ant stderr) — zero classification signal, never forwarded to
    the LLM. Kept in context.json for provenance only."""

    def test_notes_not_in_prompt(self) -> None:
        context = _make_context()
        context.notes = [
            "Compilation exit code: 0",
            "Coverage stderr (some.Test): Running ant (compile.tests)... OK",
        ]
        user = build_messages(context, "closed", "few")[1]["content"]
        self.assertNotIn("Compilation exit code", user)
        self.assertNotIn("Running ant", user)
        self.assertNotIn('"notes"', user)


if __name__ == "__main__":
    unittest.main()
