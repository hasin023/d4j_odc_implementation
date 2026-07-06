"""Tests for the agentic engine (--reasoning agentic): probes, loop, transcript."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from d4j_odc_pipeline.agent import (
    AGENT_MAX_TURNS,
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
