"""Tests for Phase 3 self-consistency voting (k independent samples, majority label)."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from d4j_odc_pipeline.models import BugContext, ClassificationResult, utc_now_iso
from d4j_odc_pipeline.pipeline import _apply_self_consistency, classify_bug_context


def _mk(label: str) -> ClassificationResult:
    return ClassificationResult(
        project_id="Lang", bug_id=1, version_id="1b", prompt_style="scientific",
        model="m", provider="gemini", created_at=utc_now_iso(), odc_type=label,
        family=None, confidence=0.9, needs_human_review=False,
        observation_summary="", hypothesis="", prediction="", experiment_rationale="",
        reasoning_summary="", evidence_used=[], evidence_gaps=[], alternative_types=[],
    )


def _payload(label: str) -> str:
    return json.dumps({
        "odc_type": label, "confidence": 0.8, "needs_human_review": False,
        "observation_summary": "o", "hypothesis": "h", "prediction": "p",
        "experiment_rationale": "e", "reasoning_summary": "r",
        "evidence_used": [], "evidence_gaps": [], "alternative_types": [],
    })


class VoteLogicTests(unittest.TestCase):
    def test_single_sample_passthrough(self) -> None:
        result = _apply_self_consistency([_mk("Checking")])
        self.assertEqual(1, result.consistency_k)
        self.assertIsNone(result.consistency_confidence)

    def test_unanimous_no_review(self) -> None:
        result = _apply_self_consistency([_mk("Checking")] * 3)
        self.assertEqual(1.0, result.consistency_confidence)
        self.assertFalse(result.needs_human_review)

    def test_majority_vote_forces_review_on_flip(self) -> None:
        result = _apply_self_consistency(
            [_mk("Checking"), _mk("Algorithm/Method"), _mk("Checking")]
        )
        self.assertEqual("Checking", result.odc_type)
        self.assertEqual(round(2 / 3, 4), result.consistency_confidence)
        self.assertTrue(result.needs_human_review)
        self.assertEqual(
            ["Checking", "Algorithm/Method", "Checking"], result.sample_labels
        )

    def test_tie_broken_by_first_occurrence(self) -> None:
        result = _apply_self_consistency([_mk("Algorithm/Method"), _mk("Checking")])
        self.assertEqual("Algorithm/Method", result.odc_type)
        self.assertTrue(result.needs_human_review)


class EndToEndKSamplingTests(unittest.TestCase):
    def test_k3_samples_vote_and_persist(self) -> None:
        ctx = BugContext(project_id="Lang", bug_id=1, version_id="1b", work_dir="/tmp",
                         created_at=utc_now_iso(), defects4j_command=["d"])
        fake = MagicMock()
        fake.complete.side_effect = [
            _payload("Checking"), _payload("Checking"), _payload("Algorithm/Method")
        ]
        out = Path(tempfile.mkdtemp(prefix="sc_test_")) / "classification.closed-scientific.json"
        with patch("d4j_odc_pipeline.pipeline.LLMClient") as client_cls:
            client_cls.from_env.return_value = fake
            result = classify_bug_context(
                context=ctx, output_path=out, provider="gemini", model="m",
                api_key_env=None, taxonomy="closed", strategy="few", self_consistency=3,
            )
            # sampling temperature requested for k > 1
            self.assertEqual(0.7, client_cls.from_env.call_args.kwargs["temperature"])
        self.assertEqual(3, fake.complete.call_count)
        self.assertEqual("Checking", result.odc_type)
        self.assertEqual(round(2 / 3, 4), result.consistency_confidence)
        self.assertTrue(result.needs_human_review)
        saved = json.loads(out.read_text())
        self.assertEqual(3, saved["consistency_k"])

    def test_k1_uses_zero_temperature(self) -> None:
        ctx = BugContext(project_id="Lang", bug_id=1, version_id="1b", work_dir="/tmp",
                         created_at=utc_now_iso(), defects4j_command=["d"])
        fake = MagicMock()
        fake.complete.return_value = _payload("Checking")
        out = Path(tempfile.mkdtemp(prefix="sc_test_")) / "classification.closed-scientific.json"
        with patch("d4j_odc_pipeline.pipeline.LLMClient") as client_cls:
            client_cls.from_env.return_value = fake
            classify_bug_context(
                context=ctx, output_path=out, provider="gemini", model="m",
                api_key_env=None, taxonomy="closed", strategy="few",
            )
            self.assertEqual(0.0, client_cls.from_env.call_args.kwargs["temperature"])
        self.assertEqual(1, fake.complete.call_count)


if __name__ == "__main__":
    unittest.main()
