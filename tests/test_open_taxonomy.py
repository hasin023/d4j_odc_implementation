"""Tests for the RQ2 open-taxonomy mode (7 ODC types + "Other" escape category).

Covers: odc.py mode gating, prompt rendering, response schema shape,
pipeline validation rules for "Other", and the coverage metrics.
"""

import json
import tempfile
import unittest
from pathlib import Path

from d4j_odc_pipeline.llm import LLMError, classification_response_schema
from d4j_odc_pipeline.models import BugContext
from d4j_odc_pipeline.odc import (
    ODC_TYPE_NAMES,
    OTHER_TYPE_NAME,
    allowed_type_names,
    family_for,
    taxonomy_markdown,
)
from d4j_odc_pipeline.pipeline import _validate_classification_payload
from d4j_odc_pipeline.prompting import build_messages


def _make_context() -> BugContext:
    return BugContext(
        project_id="Lang",
        bug_id=1,
        version_id="1b",
        work_dir="/tmp/Lang_1b",
        created_at="2026-07-06T00:00:00+00:00",
        defects4j_command=["defects4j"],
    )


def _base_payload(**overrides) -> dict:
    payload = {
        "odc_type": "Checking",
        "confidence": 0.8,
        "needs_human_review": False,
        "observation_summary": "o",
        "hypothesis": "h",
        "prediction": "p",
        "experiment_rationale": "e",
        "reasoning_summary": "r",
        "evidence_used": [],
        "evidence_gaps": [],
        "alternative_types": [],
    }
    payload.update(overrides)
    return payload


def _validate(payload: dict, taxonomy_mode: str = "closed"):
    return _validate_classification_payload(
        payload=payload,
        context=_make_context(),
        model="test-model",
        provider="gemini",
        raw_response=json.dumps(payload),
        taxonomy=taxonomy_mode,
        reasoning="scientific",
    )


class OdcModeGatingTests(unittest.TestCase):
    def test_closed_mode_has_seven_types(self) -> None:
        self.assertEqual(allowed_type_names(), ODC_TYPE_NAMES)
        self.assertEqual(len(allowed_type_names("closed")), 7)

    def test_open_mode_appends_other(self) -> None:
        names = allowed_type_names("open")
        self.assertEqual(len(names), 8)
        self.assertEqual(names[-1], OTHER_TYPE_NAME)
        self.assertEqual(names[:-1], ODC_TYPE_NAMES)

    def test_taxonomy_markdown_gates_other(self) -> None:
        self.assertNotIn(OTHER_TYPE_NAME, taxonomy_markdown())
        open_md = taxonomy_markdown("open")
        self.assertIn("LAST RESORT", open_md)
        self.assertIn("other_justification", open_md)
        self.assertIn("nearest_type", open_md)
        self.assertIn("other_confidence", open_md)

    def test_other_has_no_family(self) -> None:
        self.assertIsNone(family_for(OTHER_TYPE_NAME))


class OpenTaxonomyPromptTests(unittest.TestCase):
    def _combined(self, taxonomy: str, reasoning: str) -> str:
        messages = build_messages(_make_context(), taxonomy, reasoning)
        return "\n".join(message["content"] for message in messages)

    def test_default_condition_is_open_scientific(self) -> None:
        # The no-args default must be byte-identical to explicit open-scientific
        # (the user-chosen CLI default), and closed must exclude the Other fields.
        default_messages = build_messages(_make_context())
        open_messages = build_messages(_make_context(), "open", "scientific")
        self.assertEqual(default_messages, open_messages)
        self.assertNotIn("other_justification", self._combined("closed", "scientific"))

    def test_open_prompt_includes_other_rules(self) -> None:
        combined = self._combined("open", "scientific")
        self.assertIn("LAST RESORT", combined)
        self.assertIn("other_justification", combined)
        self.assertIn(", ".join(allowed_type_names("open")), combined)

    def test_open_prompt_zero_reasoning(self) -> None:
        combined = self._combined("open", "zero")
        self.assertIn("other_justification", combined)
        self.assertNotIn("Scientific Debugging Protocol", combined)


class ResponseSchemaTests(unittest.TestCase):
    def test_closed_schema_has_no_other_fields(self) -> None:
        schema = classification_response_schema()
        self.assertNotIn("other_justification", schema["properties"])

    def test_open_schema_adds_nullable_other_fields(self) -> None:
        schema = classification_response_schema("open")
        for field in ("other_justification", "nearest_type", "other_confidence"):
            self.assertIn(field, schema["properties"])
            self.assertNotIn(field, schema["required"])

    def test_required_lists_identical_across_modes(self) -> None:
        # Minimal schema perturbation between passes (taxonomy-shift validity).
        self.assertEqual(
            classification_response_schema()["required"],
            classification_response_schema("open")["required"],
        )


class OtherValidationTests(unittest.TestCase):
    def _other_payload(self, **overrides) -> dict:
        payload = _base_payload(
            odc_type=OTHER_TYPE_NAME,
            other_justification="None of the 7 types fit because ...",
            nearest_type="Checking",
            other_confidence=0.7,
        )
        payload.update(overrides)
        return payload

    def test_closed_mode_rejects_other(self) -> None:
        with self.assertRaises(LLMError):
            _validate(self._other_payload(), taxonomy_mode="closed")

    def test_open_mode_accepts_valid_other(self) -> None:
        result = _validate(self._other_payload(), taxonomy_mode="open")
        self.assertEqual(result.odc_type, OTHER_TYPE_NAME)
        self.assertIsNone(result.family)
        self.assertEqual(result.nearest_type, "Checking")
        self.assertEqual(result.other_confidence, 0.7)
        self.assertEqual(result.taxonomy_mode, "open")

    def test_other_always_forces_human_review(self) -> None:
        result = _validate(self._other_payload(needs_human_review=False), taxonomy_mode="open")
        self.assertTrue(result.needs_human_review)

    def test_other_requires_justification(self) -> None:
        with self.assertRaises(LLMError):
            _validate(self._other_payload(other_justification=None), taxonomy_mode="open")
        with self.assertRaises(LLMError):
            _validate(self._other_payload(other_justification="   "), taxonomy_mode="open")

    def test_other_requires_canonical_nearest_type(self) -> None:
        with self.assertRaises(LLMError):
            _validate(self._other_payload(nearest_type=None), taxonomy_mode="open")
        with self.assertRaises(LLMError):
            _validate(self._other_payload(nearest_type=OTHER_TYPE_NAME), taxonomy_mode="open")
        with self.assertRaises(LLMError):
            _validate(self._other_payload(nearest_type="Made Up Type"), taxonomy_mode="open")

    def test_other_requires_numeric_confidence(self) -> None:
        with self.assertRaises(LLMError):
            _validate(self._other_payload(other_confidence=None), taxonomy_mode="open")
        with self.assertRaises(LLMError):
            _validate(self._other_payload(other_confidence="high"), taxonomy_mode="open")

    def test_other_confidence_clamped(self) -> None:
        result = _validate(self._other_payload(other_confidence=1.7), taxonomy_mode="open")
        self.assertEqual(result.other_confidence, 1.0)

    def test_open_mode_normal_type_leaves_other_fields_empty(self) -> None:
        result = _validate(_base_payload(), taxonomy_mode="open")
        self.assertIsNone(result.other_justification)
        self.assertIsNone(result.nearest_type)
        self.assertIsNone(result.other_confidence)
        self.assertFalse(result.needs_human_review)

    def test_closed_mode_result_records_mode(self) -> None:
        result = _validate(_base_payload())
        self.assertEqual(result.taxonomy_mode, "closed")


class CoverageMetricsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="cov_metrics_test_"))
        self.closed = self.tmp / "closed"
        self.open = self.tmp / "open"
        bugs = {
            "Lang_1": ("Checking", "Checking"),
            "Lang_2": ("Algorithm/Method", "Algorithm/Method"),
            "Math_1": ("Checking", "Assignment/Initialization"),
            "Math_2": ("Relationship", OTHER_TYPE_NAME),
            "Time_1": ("Checking", "Checking"),
            "Time_2": ("Interface/O-O Messages", "Interface/O-O Messages"),
        }
        for key, (closed_label, open_label) in bugs.items():
            project = key.split("_")[0]
            for root, label in ((self.closed, closed_label), (self.open, open_label)):
                run_dir = root / f"{key}_prefix"
                run_dir.mkdir(parents=True)
                payload = {"project_id": project, "odc_type": label}
                if label == OTHER_TYPE_NAME:
                    payload.update(
                        nearest_type="Relationship",
                        other_confidence=0.6,
                        other_justification="spans multiple structural concerns",
                    )
                (run_dir / "classification.json").write_text(json.dumps(payload))

    def _metrics(self) -> dict:
        from d4j_odc_pipeline.analysis import compute_coverage_metrics

        return compute_coverage_metrics(
            closed_prefix_dir=self.closed, open_prefix_dir=self.open
        )

    def test_escape_and_coverage_rates(self) -> None:
        metrics = self._metrics()
        self.assertEqual(metrics["total_paired_bugs"], 6)
        self.assertEqual(metrics["escape_count"], 1)
        self.assertEqual(metrics["escape_rate"], round(1 / 6, 4))
        self.assertEqual(metrics["coverage_rate"], round(5 / 6, 4))

    def test_per_project_escape_rate(self) -> None:
        metrics = self._metrics()
        self.assertEqual(
            metrics["per_project_escape_rate"],
            {"Lang": 0.0, "Math": 0.5, "Time": 0.0},
        )

    def test_taxonomy_shift(self) -> None:
        shift = self._metrics()["taxonomy_shift"]
        self.assertEqual(shift["shifted_count"], 2)
        self.assertIsNotNone(shift["cohens_kappa_8cat"])
        self.assertIsNotNone(shift["cohens_kappa_non_escaped"])

    def test_escaped_bugs_audit_fields(self) -> None:
        escaped = self._metrics()["escaped_bugs"]
        self.assertEqual(len(escaped), 1)
        entry = escaped[0]
        self.assertEqual(entry["bug_key"], "Math_2")
        self.assertEqual(entry["closed_pass_type"], "Relationship")
        self.assertEqual(entry["nearest_type"], "Relationship")
        self.assertIsNone(entry["audit_is_true_gap"])

    def test_kl_divergence_positive_when_distributions_differ(self) -> None:
        divergence = self._metrics()["distribution_divergence"]
        self.assertGreater(divergence["kl_closed_to_open_bits"], 0)
        self.assertGreater(divergence["kl_open_to_closed_bits"], 0)


if __name__ == "__main__":
    unittest.main()
