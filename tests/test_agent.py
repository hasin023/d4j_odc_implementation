"""Tests for the agentic engine (--reasoning agentic): probes, loop, transcript."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from d4j_odc_pipeline.agent import (
    AGENT_MAX_TURNS,
    _agent_system_prompt,
    execute_probe,
    run_agentic_classification,
    turn_response_schema,
)
from d4j_odc_pipeline.llm import LLMError
from d4j_odc_pipeline.models import (
    BugContext, CodeSnippet, CoverageClass, CoverageLine, Failure, StackFrame, utc_now_iso,
)
from d4j_odc_pipeline.pipeline import classify_bug_context


def _rich_context() -> BugContext:
    return BugContext(
        project_id="Lang", bug_id=1, version_id="1b", work_dir="/tmp",
        created_at=utc_now_iso(), defects4j_command=["d"],
        failures=[
            Failure(
                test_name="org.example.FooTest::testOne", test_class="org.example.FooTest",
                test_method="testOne", headline="java.lang.AssertionError",
                stack_trace=[f"line {i}" for i in range(30)],
                frames=[StackFrame("org.example.Foo", "run", "Foo.java", 42, "raw")],
            )
        ],
        code_snippets=[
            CodeSnippet(class_name="org.example.Foo", file_path="Foo.java",
                        start_line=1, end_line=9, focus_line=5,
                        reason="Suspicious frame", content="int x = -1;"),
            CodeSnippet(class_name="org.example.FooTest", file_path="FooTest.java",
                        start_line=1, end_line=5, focus_line=3,
                        reason="Test source: testOne", content="assertEquals(0, x);"),
        ],
        coverage=[CoverageClass(class_name="org.example.Foo", filename="Foo.java",
                                line_rate=0.9, branch_rate=0.5,
                                covered_lines=[CoverageLine(5, 3)])],
        bug_report_content="The foo value is wrong when bar is empty.",
    )


def _turn(action: str, probe=None, conclusion=None) -> str:
    return json.dumps({
        "hypothesis": "wrong initial value",
        "prediction": "x initialized to -1 instead of 0",
        "action": action,
        "probe": probe,
        "conclusion": conclusion,
    })


def _conclusion_payload(label="Assignment/Initialization") -> dict:
    return {
        "odc_type": label, "confidence": 0.9, "needs_human_review": False,
        "observation_summary": "o", "hypothesis": "h", "prediction": "p",
        "experiment_rationale": "e", "reasoning_summary": "r",
        "evidence_used": [], "evidence_gaps": [], "alternative_types": [],
    }


class ProbeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.ctx = _rich_context()

    def test_list_evidence_inventory(self) -> None:
        obs = execute_probe(self.ctx, "list_evidence", None)
        self.assertIn("org.example.FooTest::testOne", obs["failing_tests"])
        self.assertIn("org.example.Foo", obs["production_snippet_classes"])
        self.assertTrue(obs["bug_report_available"])

    def test_full_stack_trace_returns_untruncated(self) -> None:
        obs = execute_probe(self.ctx, "full_stack_trace", "testOne")
        self.assertEqual(30, len(obs["traces"][0]["stack_trace"]))

    def test_unknown_target_returns_available_not_failure(self) -> None:
        obs = execute_probe(self.ctx, "snippet", "NoSuchClass")
        self.assertIn("error", obs)
        self.assertIn("org.example.Foo", obs["available"])

    def test_coverage_and_bug_report(self) -> None:
        self.assertEqual(0.9, execute_probe(self.ctx, "coverage", "Foo")["coverage"][0]["line_rate"])
        self.assertIn("bar is empty", execute_probe(self.ctx, "bug_report", None)["bug_report"])

    def test_bug_report_probe_sanitizes_prefix_arm(self) -> None:
        """The bug_report probe must honour the same pre-fix sanitization as
        the seed payload (docs/odc_alignment_audit.md §7) — otherwise a probe
        would leak fix knowledge the seed deliberately withheld."""
        ctx = _rich_context()
        ctx.bug_report_content = (
            "Title: Foo is wrong\n"
            "Type: Bug | Priority: Major | Status: Resolved | Resolution: Fixed\n"
            "\nDescription:\nThe foo value is wrong when bar is empty.\n"
            "\nComments:\n\n[dev]: Fixed in commit abc123."
        )
        observation = execute_probe(ctx, "bug_report", None)
        self.assertIn("wrong when bar is empty", observation["bug_report"])
        self.assertNotIn("Fixed in commit", observation["bug_report"])
        self.assertNotIn("Resolution:", observation["bug_report"])

    def test_bug_report_probe_untouched_on_postfix_arm(self) -> None:
        ctx = _rich_context()
        ctx.fix_diff = "--- a/Foo.java\n+++ b/Foo.java\n@@ -1 +1 @@\n-old\n+new\n"
        ctx.bug_report_content = (
            "Title: Foo is wrong\n\nComments:\n\n[dev]: Fixed in commit abc123."
        )
        observation = execute_probe(ctx, "bug_report", None)
        self.assertIn("Fixed in commit", observation["bug_report"])


class LoopTests(unittest.TestCase):
    def test_probe_then_conclude(self) -> None:
        fake = MagicMock()
        fake.complete.side_effect = [
            _turn("request_evidence", probe={"name": "snippet", "argument": "Foo"}),
            _turn("conclude", conclusion=_conclusion_payload()),
        ]
        seen_payloads = []

        def validate(payload):
            seen_payloads.append(payload)
            from d4j_odc_pipeline.pipeline import _validate_classification_payload
            return _validate_classification_payload(
                payload=payload, context=_rich_context(), model="m", provider="g",
                raw_response="", taxonomy="closed", strategy="scientific")

        result = run_agentic_classification(
            context=_rich_context(), client=fake, taxonomy="closed",
            validate_conclusion=validate)
        self.assertEqual("Assignment/Initialization", result.odc_type)
        self.assertEqual(2, len(result.turns))
        self.assertEqual("request_evidence", result.turns[0]["action"])
        self.assertEqual("snippet", result.turns[0]["probe"]["name"])
        self.assertFalse(result.needs_human_review)
        # observation was appended into the conversation (probe result served)
        conversation = fake.complete.call_args_list[1].args[0]
        observation_messages = [
            m["content"] for m in conversation
            if m["role"] == "user" and "Observation" in m["content"]
        ]
        self.assertTrue(any("int x = -1;" in c for c in observation_messages))

    def test_forced_conclusion_sets_review(self) -> None:
        fake = MagicMock()
        fake.complete.side_effect = (
            [_turn("request_evidence", probe={"name": "list_evidence"})] * (AGENT_MAX_TURNS - 1)
            + [_turn("conclude", conclusion=_conclusion_payload())]
        )

        def validate(payload):
            from d4j_odc_pipeline.pipeline import _validate_classification_payload
            return _validate_classification_payload(
                payload=payload, context=_rich_context(), model="m", provider="g",
                raw_response="", taxonomy="closed", strategy="scientific")

        result = run_agentic_classification(
            context=_rich_context(), client=fake, taxonomy="closed",
            validate_conclusion=validate)
        self.assertTrue(result.needs_human_review)  # concluded under duress
        self.assertEqual(AGENT_MAX_TURNS, len(result.turns))
        # duplicate probe requests were rejected, not re-served
        self.assertIn("already served", json.dumps(result.turns))

    def test_never_concludes_raises(self) -> None:
        fake = MagicMock()
        fake.complete.side_effect = [
            _turn("request_evidence", probe={"name": "bug_report"})
        ] * AGENT_MAX_TURNS
        with self.assertRaises(LLMError):
            run_agentic_classification(
                context=_rich_context(), client=fake, taxonomy="closed",
                validate_conclusion=lambda p: None)


class PipelineIntegrationTests(unittest.TestCase):
    def test_classify_agentic_end_to_end(self) -> None:
        fake = MagicMock()
        fake.complete.side_effect = [
            _turn("request_evidence", probe={"name": "snippet", "argument": "Foo"}),
            _turn("conclude", conclusion=_conclusion_payload()),
        ]
        out = Path(tempfile.mkdtemp(prefix="agent_test_")) / "classification.closed-agentic.json"
        with patch("d4j_odc_pipeline.pipeline.LLMClient") as client_cls:
            client_cls.from_env.return_value = fake
            result = classify_bug_context(
                context=_rich_context(), output_path=out, provider="gemini",
                model="m", api_key_env=None, taxonomy="closed", strategy="scientific",
            )
        self.assertEqual("Assignment/Initialization", result.odc_type)
        self.assertEqual("scientific", result.strategy)
        self.assertEqual(2, result.llm_calls_used)
        saved = json.loads(out.read_text())
        self.assertEqual(2, len(saved["turns"]))
        # per-turn schema (not the final classification schema) was sent
        schema = fake.complete.call_args_list[0].kwargs["response_schema"]
        self.assertIn("action", schema["properties"])


if __name__ == "__main__":
    unittest.main()


class LoopObservabilityTests(unittest.TestCase):
    """What the defence has to show: what came back from each probe, why the
    loop stopped, how long it took, and how often a probe missed. None of
    this is recoverable after the run, so it is recorded at run time."""

    @staticmethod
    def _validate(payload):
        from d4j_odc_pipeline.pipeline import _validate_classification_payload
        return _validate_classification_payload(
            payload=payload, context=_rich_context(), model="m", provider="g",
            raw_response="", taxonomy="closed", strategy="scientific")

    def test_observation_payload_is_persisted(self) -> None:
        fake = MagicMock()
        fake.complete.side_effect = [
            _turn("request_evidence", probe={"name": "snippet", "argument": "Foo"}),
            _turn("conclude", conclusion=_conclusion_payload()),
        ]
        result = run_agentic_classification(
            context=_rich_context(), client=fake, taxonomy="closed",
            validate_conclusion=self._validate)

        probe_turn = result.turns[0]
        # The actual snippet body must survive into the artifact, not just the
        # observation's key names.
        self.assertIn("int x = -1;", probe_turn["observation"])
        self.assertIn("observation_chars", probe_turn)
        self.assertFalse(probe_turn["observation_truncated"])

    def test_long_observation_is_truncated_but_reports_full_length(self) -> None:
        from d4j_odc_pipeline.agent import OBSERVATION_MAX_CHARS, _render_observation
        rendered = _render_observation({"snippets": ["x" * (OBSERVATION_MAX_CHARS * 3)]})
        self.assertTrue(rendered["observation_truncated"])
        self.assertEqual(OBSERVATION_MAX_CHARS, len(rendered["observation"]))
        self.assertGreater(rendered["observation_chars"], OBSERVATION_MAX_CHARS)

    def test_voluntary_conclusion_is_recorded_as_concluded(self) -> None:
        fake = MagicMock()
        fake.complete.side_effect = [_turn("conclude", conclusion=_conclusion_payload())]
        result = run_agentic_classification(
            context=_rich_context(), client=fake, taxonomy="closed",
            validate_conclusion=self._validate)
        self.assertEqual("concluded", result.termination_reason)
        self.assertEqual(0, result.probe_misses)
        self.assertFalse(result.needs_human_review)

    def test_forced_conclusion_is_recorded_as_forced(self) -> None:
        fake = MagicMock()
        fake.complete.side_effect = (
            [_turn("request_evidence", probe={"name": "list_evidence"})] * (AGENT_MAX_TURNS - 1)
            + [_turn("conclude", conclusion=_conclusion_payload())]
        )
        result = run_agentic_classification(
            context=_rich_context(), client=fake, taxonomy="closed",
            validate_conclusion=self._validate)
        self.assertEqual("forced_max_turns", result.termination_reason)
        self.assertTrue(result.needs_human_review)
        # `forced` marks only turns that ran after the force-conclude message.
        self.assertTrue(result.turns[-1]["forced"])
        self.assertFalse(any(t["forced"] for t in result.turns[:-1]))

    def test_repeated_probe_counts_as_a_miss(self) -> None:
        fake = MagicMock()
        fake.complete.side_effect = [
            _turn("request_evidence", probe={"name": "snippet", "argument": "Foo"}),
            _turn("request_evidence", probe={"name": "snippet", "argument": "Foo"}),
            _turn("conclude", conclusion=_conclusion_payload()),
        ]
        result = run_agentic_classification(
            context=_rich_context(), client=fake, taxonomy="closed",
            validate_conclusion=self._validate)
        self.assertEqual(1, result.probe_misses)
        self.assertIn("already served", result.turns[1]["observation_summary"])

    def test_bad_probe_argument_counts_as_a_miss(self) -> None:
        fake = MagicMock()
        fake.complete.side_effect = [
            _turn("request_evidence", probe={"name": "snippet", "argument": "NoSuchClass"}),
            _turn("conclude", conclusion=_conclusion_payload()),
        ]
        result = run_agentic_classification(
            context=_rich_context(), client=fake, taxonomy="closed",
            validate_conclusion=self._validate)
        self.assertEqual(1, result.probe_misses)

    def test_durations_are_recorded(self) -> None:
        fake = MagicMock()
        fake.complete.side_effect = [
            _turn("request_evidence", probe={"name": "list_evidence"}),
            _turn("conclude", conclusion=_conclusion_payload()),
        ]
        result = run_agentic_classification(
            context=_rich_context(), client=fake, taxonomy="closed",
            validate_conclusion=self._validate)
        self.assertIsNotNone(result.loop_duration_seconds)
        self.assertGreaterEqual(result.loop_duration_seconds, 0.0)
        for turn in result.turns:
            self.assertIn("duration_seconds", turn)

    def test_single_shot_result_has_no_loop_metadata(self) -> None:
        result = self._validate(_conclusion_payload())
        self.assertIsNone(result.termination_reason)
        self.assertIsNone(result.loop_duration_seconds)
        self.assertEqual([], result.turns)


class LoopReportRenderingTests(unittest.TestCase):
    """The report is the thing an audience actually reads."""

    def _report_for(self, side_effect) -> str:
        from d4j_odc_pipeline.pipeline import write_markdown_report
        fake = MagicMock()
        fake.complete.side_effect = side_effect
        result = run_agentic_classification(
            context=_rich_context(), client=fake, taxonomy="closed",
            validate_conclusion=LoopObservabilityTests._validate)
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "report.md"
            write_markdown_report(
                context=_rich_context(), classification=result, output_path=path)
            return path.read_text(encoding="utf-8")

    def test_report_shows_turns_probes_and_observations(self) -> None:
        markdown = self._report_for([
            _turn("request_evidence", probe={"name": "snippet", "argument": "Foo"}),
            _turn("conclude", conclusion=_conclusion_payload()),
        ])
        self.assertIn("## Scientific Loop", markdown)
        self.assertIn("### Turn 1", markdown)
        self.assertIn("**Probe.**", markdown)
        self.assertIn("**Observation.**", markdown)
        self.assertIn("int x = -1;", markdown)
        self.assertIn("model concluded on its own", markdown)

    def test_report_marks_a_forced_conclusion(self) -> None:
        markdown = self._report_for(
            [_turn("request_evidence", probe={"name": "list_evidence"})] * (AGENT_MAX_TURNS - 1)
            + [_turn("conclude", conclusion=_conclusion_payload())]
        )
        self.assertIn("forced — turn budget ran out", markdown)
        self.assertIn("(forced to conclude)", markdown)

    def test_single_shot_report_has_no_loop_section(self) -> None:
        from d4j_odc_pipeline.pipeline import write_markdown_report
        result = LoopObservabilityTests._validate(_conclusion_payload())
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "report.md"
            write_markdown_report(
                context=_rich_context(), classification=result, output_path=path)
            self.assertNotIn("## Scientific Loop", path.read_text(encoding="utf-8"))


class LegacyTranscriptRenderingTests(unittest.TestCase):
    """The 1,120 scientific artifacts written before 2026-09 store only the
    observation's key names and carry no termination/miss fields. They must
    still render, and their derived numbers must be right rather than a
    misleading zero."""

    @staticmethod
    def _legacy_result(turns):
        from d4j_odc_pipeline.pipeline import _validate_classification_payload
        result = _validate_classification_payload(
            payload=_conclusion_payload(), context=_rich_context(), model="m",
            provider="g", raw_response="", taxonomy="closed", strategy="scientific")
        result.turns = turns
        return result

    def test_derives_forced_termination_and_miss_count(self) -> None:
        from d4j_odc_pipeline.pipeline import _scientific_loop_lines
        turns = [
            {"turn": 1, "action": "request_evidence", "forced": False,
             "probe": {"name": "snippet", "argument": "Nope"},
             "observation_summary": "no snippet matches 'Nope'"},
            {"turn": 2, "action": "request_evidence", "forced": False,
             "probe": {"name": "list_evidence", "argument": None},
             "observation_summary": ["failing_tests"]},
            {"turn": 3, "action": "request_evidence", "forced": False,
             "probe": {"name": "snippet", "argument": "Nope"},
             "observation_summary": "probe already served this exact request"},
            {"turn": 4, "action": "conclude", "forced": True,
             "conclusion_odc_type": "Checking"},
        ]
        markdown = "\n".join(_scientific_loop_lines(self._legacy_result(turns)))
        self.assertIn("forced — turn budget ran out", markdown)
        self.assertIn("- Probe misses: `2`", markdown)
        self.assertIn("- Turns: `4`", markdown)
        # Falls back to the key-name summary when no payload was stored.
        self.assertIn("**Observation.** `['failing_tests']`", markdown)

    def test_derives_voluntary_termination(self) -> None:
        from d4j_odc_pipeline.pipeline import _scientific_loop_lines
        turns = [{"turn": 1, "action": "conclude", "forced": False,
                  "conclusion_odc_type": "Checking"}]
        markdown = "\n".join(_scientific_loop_lines(self._legacy_result(turns)))
        self.assertIn("model concluded on its own", markdown)
        self.assertIn("- Probe misses: `0`", markdown)

    def test_recorded_values_win_over_derivation(self) -> None:
        from d4j_odc_pipeline.pipeline import _scientific_loop_lines
        result = self._legacy_result(
            [{"turn": 1, "action": "conclude", "forced": True,
              "conclusion_odc_type": "Checking"}])
        result.termination_reason = "concluded"
        result.probe_misses = 7
        markdown = "\n".join(_scientific_loop_lines(result))
        self.assertIn("model concluded on its own", markdown)
        self.assertIn("- Probe misses: `7`", markdown)

    def test_recorded_zero_misses_beats_a_nonzero_derivation(self) -> None:
        """A clean current run reports 0 — it must not fall through to the
        legacy derivation just because 0 is falsy."""
        from d4j_odc_pipeline.pipeline import _scientific_loop_lines
        result = self._legacy_result([
            {"turn": 1, "action": "request_evidence", "forced": False,
             "probe": {"name": "snippet", "argument": "Foo"},
             "observation_summary": "no snippet matches 'Foo'"},
            {"turn": 2, "action": "conclude", "forced": False,
             "conclusion_odc_type": "Checking"},
        ])
        result.termination_reason = "concluded"
        result.probe_misses = 0
        markdown = "\n".join(_scientific_loop_lines(result))
        self.assertIn("- Probe misses: `0`", markdown)
