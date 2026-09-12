import json
import shutil
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

from d4j_odc_pipeline.batch import (
    _compute_collect_manifest_hash,
    _compute_manifest_hash,
    _discard_work_dir,
    analyze_batch_artifacts,
    append_run_ledger,
    generate_study_manifest,
    write_analysis_markdown,
)


class _FakeDefects4JClient:
    def __init__(self) -> None:
        self._projects = ["Lang", "Math", "Chart"]
        self._bugs = {
            "Lang": ["1", "2", "3"],
            "Math": ["1", "2", "3"],
            "Chart": ["1", "2", "3"],
        }

    def pids(self) -> list[str]:
        return list(self._projects)

    def bids(self, project_id: str, *, include_deprecated: bool = False) -> list[str]:
        _ = include_deprecated
        return list(self._bugs[project_id])


class BatchPlanningTests(unittest.TestCase):
    def test_generate_study_manifest_covers_all_projects(self) -> None:
        client = _FakeDefects4JClient()
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "manifest.json"
            manifest = generate_study_manifest(
                defects4j=client,
                output_path=output,
                target_bugs=7,
                min_per_project=1,
                seed=123,
            )

            self.assertTrue(output.exists())
            self.assertEqual(7, manifest["selected_bugs"])
            self.assertEqual({"Lang", "Math", "Chart"}, set(manifest["projects_covered"]))

            covered = {(item["project_id"], item["bug_id"]) for item in manifest["entries"]}
            self.assertGreaterEqual(len(covered), 7)


class BatchAnalysisTests(unittest.TestCase):
    def test_analyze_batch_artifacts_extracts_top_buckets(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prefix_dir = root / "prefix"
            postfix_dir = root / "postfix"

            self._write_case(
                prefix_dir / "Lang_1_prefix",
                classification={
                    "project_id": "Lang",
                    "bug_id": 1,
                    "version_id": "1b",
                    "odc_type": "Checking",
                    "family": "Control and Data Flow",
                    "confidence": 0.7,
                    "alternative_types": [{"type": "Algorithm/Method", "why_not_primary": "close"}],
                    "reasoning_summary": "prefix reasoning for Lang-1",
                },
            )
            self._write_case(
                postfix_dir / "Lang_1_postfix",
                classification={
                    "project_id": "Lang",
                    "bug_id": 1,
                    "version_id": "1b",
                    "odc_type": "Algorithm/Method",
                    "family": "Control and Data Flow",
                    "confidence": 0.9,
                    "alternative_types": [{"type": "Checking", "why_not_primary": "close"}],
                    "reasoning_summary": "postfix reasoning for Lang-1",
                },
            )

            self._write_case(
                prefix_dir / "Math_2_prefix",
                classification={
                    "project_id": "Math",
                    "bug_id": 2,
                    "version_id": "2b",
                    "odc_type": "Checking",
                    "family": "Control and Data Flow",
                    "confidence": 0.2,
                    "alternative_types": [{"type": "Assignment/Initialization", "why_not_primary": "uncertain"}],
                    "reasoning_summary": "prefix reasoning for Math-2",
                },
            )
            self._write_case(
                postfix_dir / "Math_2_postfix",
                classification={
                    "project_id": "Math",
                    "bug_id": 2,
                    "version_id": "2b",
                    "odc_type": "Relationship",
                    "family": "Structural",
                    "confidence": 0.8,
                    "alternative_types": [{"type": "Function/Class/Object", "why_not_primary": "uncertain"}],
                    "reasoning_summary": "postfix reasoning for Math-2",
                },
            )

            summary = analyze_batch_artifacts(
                prefix_dir=prefix_dir,
                postfix_dir=postfix_dir,
                expected_projects=["Lang", "Math", "Chart"],
                taxonomy="closed",
                strategy="scientific",
            )

            self.assertEqual(2, summary["total_pairs"])
            self.assertEqual(2, summary["unique_projects"])
            self.assertIn("Chart", summary["missing_projects"])
            self.assertEqual(2, summary["type_changed_count"])
            self.assertTrue(summary["top3_alternative_match"])
            self.assertTrue(summary["top3_no_common_alternative"])

            # RQ1: type distribution over prefix classifications (both are Checking).
            self.assertEqual(2, summary["type_distribution_prefix"]["type_counts"].get("Checking"))

            # RQ3: strict-match alias matches type_unchanged (both pairs changed → 0),
            # per-type precision/recall/F1, overall Cohen's kappa, and confusion matrix.
            self.assertEqual(0, summary["strict_match_count"])
            self.assertEqual(summary["type_unchanged_rate"], summary["strict_match_rate"])
            self.assertIn("Checking", summary["per_type_metrics"])
            self.assertIsNotNone(summary["cohens_kappa"])
            self.assertEqual(
                {"Algorithm/Method": 1, "Relationship": 1},
                summary["type_confusion_matrix"]["Checking"],
            )

            # RQ5: per-project kappa is None for projects with < 2 bugs (both here).
            self.assertIsNone(summary["per_project_kappa"]["Lang"])
            self.assertIsNone(summary["per_project_kappa"]["Math"])

    @staticmethod
    def _write_case(case_dir: Path, *, classification: dict) -> None:
        case_dir.mkdir(parents=True, exist_ok=True)
        (case_dir / "classification.scientific-closed.json").write_text(
            json.dumps(classification, indent=2),
            encoding="utf-8",
        )
        (case_dir / "context.json").write_text(
            json.dumps(
                {
                    "project_id": classification["project_id"],
                    "bug_id": classification["bug_id"],
                    "failures": [
                        {
                            "test_name": "org.example.Test::testCase",
                            "headline": "java.lang.AssertionError",
                        }
                    ],
                    "suspicious_frames": [
                        {
                            "class_name": "org.example.Target",
                            "method_name": "run",
                            "line_number": 42,
                        }
                    ],
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        (case_dir / "report.scientific-closed.md").write_text(
            "# Report\n\n## ODC Result\n- ODC Type: sample\n- Confidence: sample\n",
            encoding="utf-8",
        )


class SignalHandlingTests(unittest.TestCase):
    def setUp(self) -> None:
        from d4j_odc_pipeline.batch import reset_shutdown
        reset_shutdown()

    def tearDown(self) -> None:
        from d4j_odc_pipeline.batch import reset_shutdown
        reset_shutdown()

    def test_shutdown_flag_set_on_request(self) -> None:
        from d4j_odc_pipeline.batch import _request_shutdown, is_shutdown_requested
        self.assertFalse(is_shutdown_requested())
        _request_shutdown(2, None)
        self.assertTrue(is_shutdown_requested())

    def test_second_shutdown_raises_system_exit(self) -> None:
        from d4j_odc_pipeline.batch import _request_shutdown, is_shutdown_requested
        _request_shutdown(2, None)
        self.assertTrue(is_shutdown_requested())
        with self.assertRaises(SystemExit) as cm:
            _request_shutdown(2, None)
        self.assertEqual(cm.exception.code, 130)

    def test_reset_clears_flag(self) -> None:
        from d4j_odc_pipeline.batch import _request_shutdown, is_shutdown_requested, reset_shutdown
        _request_shutdown(2, None)
        self.assertTrue(is_shutdown_requested())
        reset_shutdown()
        self.assertFalse(is_shutdown_requested())


class CheckpointTests(unittest.TestCase):
    def test_checkpoint_round_trip(self) -> None:
        from d4j_odc_pipeline.batch import _write_checkpoint, _load_checkpoint
        with tempfile.TemporaryDirectory() as temp_dir:
            cp_path = Path(temp_dir) / "checkpoint.json"
            records = [
                {"bug_key": "Lang_1", "prefix_status": "ok", "postfix_status": "ok"},
                {"bug_key": "Math_2", "prefix_status": "ok", "postfix_status": "ok"},
                {"bug_key": "Chart_3", "prefix_status": "failed", "postfix_status": "pending"},
            ]
            _write_checkpoint(cp_path, records, manifest_hash="abc123", interrupted=False)
            self.assertTrue(cp_path.exists())

            completed = _load_checkpoint(cp_path, manifest_hash="abc123")
            self.assertEqual(completed, {"Lang_1", "Math_2"})
            self.assertNotIn("Chart_3", completed)

    def test_checkpoint_stale_manifest_returns_empty(self) -> None:
        from d4j_odc_pipeline.batch import _write_checkpoint, _load_checkpoint
        with tempfile.TemporaryDirectory() as temp_dir:
            cp_path = Path(temp_dir) / "checkpoint.json"
            records = [
                {"bug_key": "Lang_1", "prefix_status": "ok", "postfix_status": "ok"},
            ]
            _write_checkpoint(cp_path, records, manifest_hash="abc123", interrupted=False)

            # Different manifest hash → should return empty
            completed = _load_checkpoint(cp_path, manifest_hash="different_hash")
            self.assertEqual(completed, set())

    def test_checkpoint_missing_file_returns_empty(self) -> None:
        from d4j_odc_pipeline.batch import _load_checkpoint
        with tempfile.TemporaryDirectory() as temp_dir:
            cp_path = Path(temp_dir) / "nonexistent.json"
            completed = _load_checkpoint(cp_path, manifest_hash="abc123")
            self.assertEqual(completed, set())

    def test_manifest_hash_deterministic(self) -> None:
        from d4j_odc_pipeline.batch import _compute_manifest_hash
        entries = [
            {"project_id": "Lang", "bug_id": 1},
            {"project_id": "Math", "bug_id": 2},
        ]
        hash1 = _compute_manifest_hash(entries)
        hash2 = _compute_manifest_hash(list(reversed(entries)))
        # Hash should be the same regardless of order (sorted internally)
        self.assertEqual(hash1, hash2)

    def test_manifest_hash_changes_with_different_entries(self) -> None:
        from d4j_odc_pipeline.batch import _compute_manifest_hash
        entries_a = [{"project_id": "Lang", "bug_id": 1}]
        entries_b = [{"project_id": "Math", "bug_id": 2}]
        self.assertNotEqual(_compute_manifest_hash(entries_a), _compute_manifest_hash(entries_b))


class _FakeCompareResult:
    def to_dict(self) -> dict:
        return {"strict_match": True, "match_detail": "stub"}


class BatchResumeTests(unittest.TestCase):
    @staticmethod
    def _scratch_dir(name: str) -> Path:
        base = Path(".dist") / "test_tmp_batch" / f"{name}_{uuid.uuid4().hex[:8]}"
        base.mkdir(parents=True, exist_ok=True)
        return base

    def setUp(self) -> None:
        from d4j_odc_pipeline.batch import reset_shutdown
        reset_shutdown()

    def tearDown(self) -> None:
        from d4j_odc_pipeline.batch import reset_shutdown
        reset_shutdown()

    def test_resume_skips_completed_entries_from_checkpoint(self) -> None:
        from d4j_odc_pipeline.batch import _request_shutdown, reset_shutdown, run_batch_from_manifest

        manifest = {
            "target_bugs": 2,
            "entries": [
                {"project_id": "Lang", "bug_id": 1},
                {"project_id": "Math", "bug_id": 2},
            ],
        }
        client = _FakeDefects4JClient()
        temp_root = self._scratch_dir("resume_checkpoint_skip")
        artifacts_root = temp_root / "artifacts"
        work_root = temp_root / "work"
        checkpoint_path = artifacts_root / "checkpoint.pairs.scientific-closed.json"
        first_run_calls: list[tuple[str, str, int, str]] = []
        second_run_calls: list[tuple[str, str, int, str]] = []
        shutdown_once = {"done": False}

        def fake_collect(*, project_id: str, bug_id: int, output_path: Path, **kwargs):
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(
                json.dumps({"project_id": project_id, "bug_id": bug_id}),
                encoding="utf-8",
            )
            log = first_run_calls if not shutdown_once["done"] else second_run_calls
            log.append(("collect", project_id, bug_id, output_path.parent.name))
            return {"project_id": project_id, "bug_id": bug_id}

        def fake_classify(*, context: dict, output_path: Path, **kwargs):
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(
                json.dumps(
                    {
                        "project_id": context["project_id"],
                        "bug_id": context["bug_id"],
                        "version_id": f"{context['bug_id']}b",
                        "odc_type": "Checking",
                        "family": "Control and Data Flow",
                        "confidence": 0.9,
                    }
                ),
                encoding="utf-8",
            )
            log = first_run_calls if not shutdown_once["done"] else second_run_calls
            log.append(("classify", context["project_id"], context["bug_id"], output_path.parent.name))
            return {
                "project_id": context["project_id"],
                "bug_id": context["bug_id"],
            }

        def fake_report(*, context: dict, classification: dict, output_path: Path):
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text("# report", encoding="utf-8")
            log = first_run_calls if not shutdown_once["done"] else second_run_calls
            log.append(("report", context["project_id"], context["bug_id"], output_path.parent.name))
            if output_path.parent.name == "Lang_1_postfix" and not shutdown_once["done"]:
                shutdown_once["done"] = True
                _request_shutdown(2, None)

        with (
            patch("d4j_odc_pipeline.batch.collect_bug_context", side_effect=fake_collect),
            patch("d4j_odc_pipeline.batch.classify_bug_context", side_effect=fake_classify),
            patch("d4j_odc_pipeline.batch.write_markdown_report", side_effect=fake_report),
            patch("d4j_odc_pipeline.batch.compare_classifications", return_value=_FakeCompareResult()),
        ):
            first_summary = run_batch_from_manifest(
                defects4j=client,
                manifest=manifest,
                artifacts_root=artifacts_root,
                work_root=work_root,
                provider="gemini",
                model="test-model",
                api_key_env=None,
                base_url=None,
                taxonomy="closed",
                strategy="scientific",
            )

            checkpoint_after_first = json.loads(checkpoint_path.read_text(encoding="utf-8"))

            reset_shutdown()

            second_summary = run_batch_from_manifest(
                defects4j=client,
                manifest=manifest,
                artifacts_root=artifacts_root,
                work_root=work_root,
                provider="gemini",
                model="test-model",
                api_key_env=None,
                base_url=None,
                taxonomy="closed",
                strategy="scientific",
            )

        checkpoint_after_second = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        self.assertTrue(first_summary["interrupted"])
        self.assertEqual(1, first_summary["completed_entries"])
        self.assertEqual(["Lang_1"], checkpoint_after_first["completed_keys"])
        self.assertFalse(second_summary["interrupted"])
        self.assertEqual(2, second_summary["completed_entries"])
        self.assertEqual(["Lang_1", "Math_2"], checkpoint_after_second["completed_keys"])
        self.assertTrue(second_run_calls)
        self.assertTrue(all(call[1] == "Math" and call[2] == 2 for call in second_run_calls))

    def _run_minimal_batch(self, *, artifacts_root: Path, work_root: Path, provider: str, model: str) -> dict:
        """Shared minimal fake for the multi-model plumbing tests below —
        doesn't need the shutdown/interrupt machinery BatchResumeTests above
        exercises, just needs collect/classify/report to produce real files
        so checkpoint + artifact paths can be inspected."""
        from d4j_odc_pipeline.batch import run_batch_from_manifest

        manifest = {
            "target_bugs": 1,
            "entries": [{"project_id": "Lang", "bug_id": 1}],
        }
        client = _FakeDefects4JClient()

        def fake_collect(*, project_id: str, bug_id: int, output_path: Path, **kwargs):
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps({"project_id": project_id, "bug_id": bug_id}), encoding="utf-8")
            return {"project_id": project_id, "bug_id": bug_id}

        def fake_classify(*, context: dict, output_path: Path, **kwargs):
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(
                json.dumps({
                    "project_id": context["project_id"],
                    "bug_id": context["bug_id"],
                    "version_id": f"{context['bug_id']}b",
                    "odc_type": "Checking",
                    "family": "Control and Data Flow",
                    "confidence": 0.9,
                }),
                encoding="utf-8",
            )
            return {"project_id": context["project_id"], "bug_id": context["bug_id"]}

        def fake_report(*, context: dict, classification: dict, output_path: Path):
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text("# report", encoding="utf-8")

        def fake_load_context(path: Path) -> dict:
            # A second --model run reuses the FIRST model's already-written
            # context.json (shared evidence, per CLAUDE.md) via the real
            # load_context — patched here to skip actual BugContext parsing
            # since fake_collect's context.json is a minimal stub.
            return json.loads(path.read_text(encoding="utf-8"))

        with (
            patch("d4j_odc_pipeline.batch.collect_bug_context", side_effect=fake_collect),
            patch("d4j_odc_pipeline.pipeline.load_context", side_effect=fake_load_context),
            patch("d4j_odc_pipeline.batch.classify_bug_context", side_effect=fake_classify),
            patch("d4j_odc_pipeline.batch.write_markdown_report", side_effect=fake_report),
            patch("d4j_odc_pipeline.batch.compare_classifications", return_value=_FakeCompareResult()),
        ):
            return run_batch_from_manifest(
                defects4j=client,
                manifest=manifest,
                artifacts_root=artifacts_root,
                work_root=work_root,
                provider=provider,
                model=model,
                api_key_env=None,
                base_url=None,
                taxonomy="closed",
                strategy="few",
            )

    def test_second_model_does_not_collide_with_first(self) -> None:
        """The capability this whole mechanism exists for: running the same
        condition under a second --model must not overwrite or skip the
        first model's artifacts."""
        temp_root = self._scratch_dir("multi_model_no_collision")
        artifacts_root = temp_root / "artifacts"
        work_root = temp_root / "work"

        first_summary = self._run_minimal_batch(
            artifacts_root=artifacts_root, work_root=work_root, provider="gemini", model="model-a"
        )
        self.assertEqual(first_summary["effective_tag"], "few-closed")

        run_dir = artifacts_root / "prefix" / "Lang_1_prefix"
        bare_classification = run_dir / "classification.few-closed.json"
        self.assertTrue(bare_classification.exists())
        bare_content_before = bare_classification.read_text(encoding="utf-8")

        second_summary = self._run_minimal_batch(
            artifacts_root=artifacts_root, work_root=work_root, provider="sambanova", model="model-b"
        )
        self.assertEqual(second_summary["effective_tag"], "few-closed.sambanova-model-b")

        # First model's file untouched.
        self.assertEqual(bare_classification.read_text(encoding="utf-8"), bare_content_before)
        # Second model got its own suffixed file, same run folder.
        suffixed_classification = run_dir / "classification.few-closed.sambanova-model-b.json"
        self.assertTrue(suffixed_classification.exists())
        # Both checkpoints exist, separately.
        self.assertTrue((artifacts_root / "checkpoint.pairs.few-closed.json").exists())
        self.assertTrue((artifacts_root / "checkpoint.pairs.few-closed.sambanova-model-b.json").exists())
        # Second model actually processed the bug, not skipped.
        self.assertEqual(second_summary["completed_entries"], 1)

    def test_legacy_checkpoint_without_model_keys_is_untouched(self) -> None:
        """A checkpoint written before this mechanism existed (every file in
        the committed 854-bug corpus) has no model/provider keys — any
        --model run against it must keep writing the bare tag, never rename
        or suffix it."""
        temp_root = self._scratch_dir("multi_model_legacy_checkpoint")
        artifacts_root = temp_root / "artifacts"
        work_root = temp_root / "work"
        artifacts_root.mkdir(parents=True, exist_ok=True)
        legacy_checkpoint = artifacts_root / "checkpoint.pairs.few-closed.json"
        legacy_checkpoint.write_text(
            json.dumps({"manifest_hash": "stale", "completed_keys": [], "total_attempted": 0, "interrupted": False}),
            encoding="utf-8",
        )

        summary = self._run_minimal_batch(
            artifacts_root=artifacts_root, work_root=work_root, provider="gemini", model="any-model"
        )
        self.assertEqual(summary["effective_tag"], "few-closed")
        run_dir = artifacts_root / "prefix" / "Lang_1_prefix"
        self.assertTrue((run_dir / "classification.few-closed.json").exists())

    def test_resume_continues_partial_bug_via_skip_existing(self) -> None:
        from d4j_odc_pipeline.batch import _request_shutdown, reset_shutdown, run_batch_from_manifest

        manifest = {
            "target_bugs": 1,
            "entries": [
                {"project_id": "Lang", "bug_id": 1},
            ],
        }
        client = _FakeDefects4JClient()
        temp_root = self._scratch_dir("resume_partial_bug")
        artifacts_root = temp_root / "artifacts"
        work_root = temp_root / "work"
        checkpoint_path = artifacts_root / "checkpoint.pairs.scientific-closed.json"
        first_run_calls: list[tuple[str, str, int, str]] = []
        second_run_calls: list[tuple[str, str, int, str]] = []
        shutdown_once = {"done": False}

        def fake_collect(*, project_id: str, bug_id: int, output_path: Path, **kwargs):
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(
                json.dumps({"project_id": project_id, "bug_id": bug_id}),
                encoding="utf-8",
            )
            log = first_run_calls if not shutdown_once["done"] else second_run_calls
            log.append(("collect", project_id, bug_id, output_path.parent.name))
            return {"project_id": project_id, "bug_id": bug_id}

        def fake_classify(*, context: dict, output_path: Path, **kwargs):
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(
                json.dumps(
                    {
                        "project_id": context["project_id"],
                        "bug_id": context["bug_id"],
                        "version_id": f"{context['bug_id']}b",
                        "odc_type": "Checking",
                        "family": "Control and Data Flow",
                        "confidence": 0.9,
                    }
                ),
                encoding="utf-8",
            )
            log = first_run_calls if not shutdown_once["done"] else second_run_calls
            log.append(("classify", context["project_id"], context["bug_id"], output_path.parent.name))
            return {
                "project_id": context["project_id"],
                "bug_id": context["bug_id"],
            }

        def fake_report(*, context: dict, classification: dict, output_path: Path):
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text("# report", encoding="utf-8")
            log = first_run_calls if not shutdown_once["done"] else second_run_calls
            log.append(("report", context["project_id"], context["bug_id"], output_path.parent.name))
            if output_path.parent.name == "Lang_1_prefix" and not shutdown_once["done"]:
                shutdown_once["done"] = True
                _request_shutdown(2, None)

        with (
            patch("d4j_odc_pipeline.batch.collect_bug_context", side_effect=fake_collect),
            patch("d4j_odc_pipeline.batch.classify_bug_context", side_effect=fake_classify),
            patch("d4j_odc_pipeline.batch.write_markdown_report", side_effect=fake_report),
            patch("d4j_odc_pipeline.batch.compare_classifications", return_value=_FakeCompareResult()),
        ):
            first_summary = run_batch_from_manifest(
                defects4j=client,
                manifest=manifest,
                artifacts_root=artifacts_root,
                work_root=work_root,
                provider="gemini",
                model="test-model",
                api_key_env=None,
                base_url=None,
                taxonomy="closed",
                strategy="scientific",
            )

            checkpoint_after_first = json.loads(checkpoint_path.read_text(encoding="utf-8"))

            reset_shutdown()

            second_summary = run_batch_from_manifest(
                defects4j=client,
                manifest=manifest,
                artifacts_root=artifacts_root,
                work_root=work_root,
                provider="gemini",
                model="test-model",
                api_key_env=None,
                base_url=None,
                taxonomy="closed",
                strategy="scientific",
            )

        checkpoint_after_second = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        self.assertTrue(first_summary["interrupted"])
        self.assertEqual([], checkpoint_after_first["completed_keys"])
        self.assertFalse(second_summary["interrupted"])
        self.assertEqual(1, second_summary["completed_entries"])
        self.assertEqual(["Lang_1"], checkpoint_after_second["completed_keys"])
        self.assertTrue(second_run_calls)
        self.assertTrue(all(call[3] == "Lang_1_postfix" for call in second_run_calls))


if __name__ == "__main__":
    unittest.main()


class BudgetGuardTests(unittest.TestCase):
    @staticmethod
    def _scratch_dir(name: str) -> Path:
        base = Path(".dist") / "test_tmp_batch" / f"{name}_{uuid.uuid4().hex[:8]}"
        base.mkdir(parents=True, exist_ok=True)
        return base

    @staticmethod
    def _fakes(calls: list):
        def fake_collect(*, project_id, bug_id, output_path, **kwargs):
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(
                json.dumps({
                    "project_id": project_id, "bug_id": bug_id,
                    "version_id": f"{bug_id}b", "work_dir": "w",
                    "created_at": "t", "defects4j_command": [],
                }), encoding="utf-8")
            return {"project_id": project_id, "bug_id": bug_id}

        def fake_classify(*, context, output_path, **kwargs):
            pid = context["project_id"] if isinstance(context, dict) else context.project_id
            bid = context["bug_id"] if isinstance(context, dict) else context.bug_id
            calls.append((pid, bid, output_path.name))
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps({
                "project_id": pid, "bug_id": bid, "odc_type": "Checking",
            }), encoding="utf-8")
            return {"project_id": pid, "bug_id": bid}

        def fake_report(*, context, classification, output_path):
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text("# report", encoding="utf-8")

        return fake_collect, fake_classify, fake_report

    def test_pairs_runner_stops_at_budget_and_resumes(self) -> None:
        from d4j_odc_pipeline.batch import reset_shutdown, run_batch_from_manifest
        reset_shutdown()
        manifest = {"target_bugs": 2, "entries": [
            {"project_id": "Lang", "bug_id": 1},
            {"project_id": "Math", "bug_id": 2},
        ]}
        temp_root = self._scratch_dir("budget_pairs")
        calls: list = []
        fake_collect, fake_classify, fake_report = self._fakes(calls)
        common = dict(
            defects4j=_FakeDefects4JClient(),
            manifest=manifest,
            artifacts_root=temp_root / "artifacts",
            work_root=temp_root / "work",
            provider="gemini", model="m", api_key_env=None, base_url=None,
            taxonomy="closed", strategy="scientific",
        )
        with (
            patch("d4j_odc_pipeline.batch.collect_bug_context", side_effect=fake_collect),
            patch("d4j_odc_pipeline.batch.classify_bug_context", side_effect=fake_classify),
            patch("d4j_odc_pipeline.batch.write_markdown_report", side_effect=fake_report),
            patch("d4j_odc_pipeline.batch.compare_classifications", return_value=_FakeCompareResult()),
        ):
            # 2 bugs x 2 evidence modes = 4 calls needed; budget allows 3
            first = run_batch_from_manifest(**common, daily_call_budget=3)
            self.assertTrue(first["budget_reached"])
            self.assertEqual(3, first["llm_calls_made"])
            math_record = next(r for r in first["records"] if r.get("bug_key") == "Math_2")
            self.assertEqual("budget-stopped", math_record["postfix_status"])

            # Resume with fresh budget: only the missing postfix call is made
            second = run_batch_from_manifest(**common, daily_call_budget=1400)
            self.assertFalse(second["budget_reached"])
            self.assertEqual(1, second["llm_calls_made"])
        self.assertEqual(4, len(calls))
        shutil.rmtree(temp_root, ignore_errors=True)

    def test_discover_ladder_collects_each_tag_across_bug_folders(self) -> None:
        from d4j_odc_pipeline.batch import discover_ladder

        temp_root = self._scratch_dir("discover_ladder")
        prefix_dir = temp_root / "prefix"
        bug_a = prefix_dir / "Lang_1_prefix"
        bug_b = prefix_dir / "Math_2_prefix"
        bug_a.mkdir(parents=True)
        bug_b.mkdir(parents=True)

        (bug_a / "classification.zero-free.json").write_text(
            json.dumps({"odc_type": "Function"}), encoding="utf-8"
        )
        (bug_a / "classification.scientific-open.json").write_text(
            json.dumps({"odc_type": "Function"}), encoding="utf-8"
        )
        (bug_b / "classification.zero-free.json").write_text(
            json.dumps({"odc_type": "Checking"}), encoding="utf-8"
        )
        # bug_b has no scientific-open pass — should just be absent, not error.

        result = discover_ladder(prefix_dir, ["zero-free", "scientific-open"])
        self.assertEqual(2, len(result["zero-free"]))
        self.assertEqual(1, len(result["scientific-open"]))
        shutil.rmtree(temp_root, ignore_errors=True)

    def test_discover_ladder_missing_dir_raises(self) -> None:
        from d4j_odc_pipeline.batch import discover_ladder

        with self.assertRaises(ValueError):
            discover_ladder(Path("/nonexistent/prefix/dir"), ["zero-free"])


class RunSignatureHashTests(unittest.TestCase):
    """The checkpoint hash must identify the RUN, not just the bug set.

    Before this, re-running one manifest under a different strategy or model
    produced a matching hash, so the checkpoint resumed and every bug was
    skipped as already-complete — an empty run rather than a comparison."""

    ENTRIES = [
        {"project_id": "Lang", "bug_id": 1},
        {"project_id": "Math", "bug_id": 2},
    ]

    def _hash(self, **kwargs):
        base = dict(
            taxonomy="open", strategy="few",
            provider="gemini", model="gemini-3.1-flash-lite", self_consistency=1,
        )
        base.update(kwargs)
        return _compute_manifest_hash(self.ENTRIES, **base)

    def test_identical_parameters_produce_identical_hash(self) -> None:
        self.assertEqual(self._hash(), self._hash())

    def test_bug_order_does_not_matter(self) -> None:
        reordered = list(reversed(self.ENTRIES))
        self.assertEqual(
            self._hash(),
            _compute_manifest_hash(
                reordered, taxonomy="open", strategy="few",
                provider="gemini", model="gemini-3.1-flash-lite", self_consistency=1,
            ),
        )

    def test_strategy_change_changes_hash(self) -> None:
        self.assertNotEqual(self._hash(), self._hash(strategy="scientific"))

    def test_taxonomy_change_changes_hash(self) -> None:
        self.assertNotEqual(self._hash(), self._hash(taxonomy="closed"))

    def test_model_change_changes_hash(self) -> None:
        self.assertNotEqual(self._hash(), self._hash(model="other-model"))

    def test_provider_change_changes_hash(self) -> None:
        self.assertNotEqual(self._hash(), self._hash(provider="groq"))

    def test_self_consistency_change_changes_hash(self) -> None:
        self.assertNotEqual(self._hash(), self._hash(self_consistency=3))

    def test_different_bug_set_changes_hash(self) -> None:
        other = _compute_manifest_hash(
            [{"project_id": "Lang", "bug_id": 99}], taxonomy="open", strategy="few",
            provider="gemini", model="gemini-3.1-flash-lite", self_consistency=1,
        )
        self.assertNotEqual(self._hash(), other)


class RunLedgerTests(unittest.TestCase):
    """The ledger is append-only: it is what makes "did results change?"
    answerable across runs."""

    def test_appends_one_line_per_run_and_preserves_order(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            append_run_ledger(root, {"run_id": "aaa", "effective_tag": "few-open"})
            append_run_ledger(root, {"run_id": "bbb", "effective_tag": "scientific-open"})

            lines = (root / "runs.jsonl").read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(2, len(lines))
            self.assertEqual("aaa", json.loads(lines[0])["run_id"])
            self.assertEqual("bbb", json.loads(lines[1])["run_id"])
            self.assertEqual("scientific-open", json.loads(lines[1])["effective_tag"])

    def test_creates_the_root_directory_if_absent(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "not_yet" / "artifacts_v2"
            path = append_run_ledger(root, {"run_id": "ccc"})
            self.assertTrue(path.exists())


class WorkDirCleanupTests(unittest.TestCase):
    """Checkouts are per (bug, arm) and nothing reads them once context.json
    exists — but this is an rmtree, so the guards matter more than the happy
    path."""

    def _checkout(self, root: Path, name: str) -> Path:
        d = root / "prefix" / name
        (d / "src" / "main").mkdir(parents=True)
        (d / "src" / "main" / "Foo.java").write_text("x" * 4096, encoding="utf-8")
        return d

    def test_removes_checkout_and_reports_bytes_freed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "work"
            checkout = self._checkout(root, "Lang_1b")
            freed = _discard_work_dir(checkout, root)
            self.assertFalse(checkout.exists())
            self.assertGreaterEqual(freed, 4096)

    def test_sibling_checkouts_are_untouched(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "work"
            target = self._checkout(root, "Lang_1b")
            sibling = self._checkout(root, "Lang_2b")
            _discard_work_dir(target, root)
            self.assertFalse(target.exists())
            self.assertTrue(sibling.exists())

    def test_refuses_to_delete_outside_the_work_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "work"
            root.mkdir(parents=True)
            outsider = Path(temp_dir) / "precious"
            outsider.mkdir()
            (outsider / "keep.txt").write_text("do not delete", encoding="utf-8")
            self.assertIsNone(_discard_work_dir(outsider, root))
            self.assertTrue((outsider / "keep.txt").exists())

    def test_refuses_to_delete_the_work_root_itself(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "work"
            root.mkdir(parents=True)
            self.assertIsNone(_discard_work_dir(root, root))
            self.assertTrue(root.exists())

    def test_missing_checkout_is_a_no_op(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "work"
            root.mkdir(parents=True)
            self.assertIsNone(_discard_work_dir(root / "prefix" / "Gone_1b", root))


class CollectManifestHashTests(unittest.TestCase):
    """Collection has no taxonomy/strategy/provider/model — the hash must not
    fold those in, unlike `_compute_manifest_hash` (see its docstring)."""

    def test_bug_order_does_not_matter(self) -> None:
        a = [{"project_id": "Lang", "bug_id": 1}, {"project_id": "Math", "bug_id": 2}]
        b = [{"project_id": "Math", "bug_id": 2}, {"project_id": "Lang", "bug_id": 1}]
        self.assertEqual(_compute_collect_manifest_hash(a), _compute_collect_manifest_hash(b))

    def test_different_bug_set_changes_hash(self) -> None:
        a = [{"project_id": "Lang", "bug_id": 1}]
        b = [{"project_id": "Lang", "bug_id": 2}]
        self.assertNotEqual(_compute_collect_manifest_hash(a), _compute_collect_manifest_hash(b))


class CollectOnlyBatchTests(unittest.TestCase):
    """study-collect's core promise: writes context.json for every bug,
    never touches classify_bug_context, and needs no provider/model/LLM
    config to run at all."""

    @staticmethod
    def _scratch_dir(name: str) -> Path:
        base = Path(".dist") / "test_tmp_batch" / f"{name}_{uuid.uuid4().hex[:8]}"
        base.mkdir(parents=True, exist_ok=True)
        return base

    def setUp(self) -> None:
        from d4j_odc_pipeline.batch import reset_shutdown
        reset_shutdown()

    def tearDown(self) -> None:
        from d4j_odc_pipeline.batch import reset_shutdown
        reset_shutdown()

    def _fake_collect(self, *, project_id: str, bug_id: int, output_path: Path, **kwargs):
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps({"project_id": project_id, "bug_id": bug_id}),
            encoding="utf-8",
        )
        return {"project_id": project_id, "bug_id": bug_id}

    def test_writes_context_for_every_bug_and_never_calls_classify(self) -> None:
        from d4j_odc_pipeline.batch import collect_batch_from_manifest

        manifest = {
            "target_bugs": 2,
            "entries": [
                {"project_id": "Lang", "bug_id": 1},
                {"project_id": "Math", "bug_id": 2},
            ],
        }
        client = _FakeDefects4JClient()
        temp_root = self._scratch_dir("collect_writes_context")
        artifacts_root = temp_root / "artifacts"
        work_root = temp_root / "work"

        with (
            patch("d4j_odc_pipeline.batch.collect_bug_context", side_effect=self._fake_collect),
            patch("d4j_odc_pipeline.batch.classify_bug_context") as mock_classify,
        ):
            summary = collect_batch_from_manifest(
                defects4j=client,
                manifest=manifest,
                artifacts_root=artifacts_root,
                work_root=work_root,
            )

        mock_classify.assert_not_called()
        self.assertEqual(2, summary["completed_entries"])
        self.assertEqual("collect-only", summary["mode"])
        self.assertTrue((artifacts_root / "prefix" / "Lang_1_prefix" / "context.json").exists())
        self.assertTrue((artifacts_root / "postfix" / "Lang_1_postfix" / "context.json").exists())
        self.assertTrue((artifacts_root / "checkpoint.collect.json").exists())
        self.assertNotIn("provider", summary)
        self.assertNotIn("condition_tag", summary)

    def test_resume_skips_completed_bugs_via_checkpoint(self) -> None:
        from d4j_odc_pipeline.batch import _request_shutdown, collect_batch_from_manifest

        manifest = {
            "target_bugs": 2,
            "entries": [
                {"project_id": "Lang", "bug_id": 1},
                {"project_id": "Math", "bug_id": 2},
            ],
        }
        client = _FakeDefects4JClient()
        temp_root = self._scratch_dir("collect_resume")
        artifacts_root = temp_root / "artifacts"
        work_root = temp_root / "work"
        calls: list[tuple[str, int]] = []
        shutdown_once = {"done": False}

        def fake_collect(*, project_id: str, bug_id: int, output_path: Path, **kwargs):
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(
                json.dumps({"project_id": project_id, "bug_id": bug_id}),
                encoding="utf-8",
            )
            calls.append((project_id, bug_id))
            if project_id == "Lang" and bug_id == 1 and output_path.parent.name == "Lang_1_postfix" and not shutdown_once["done"]:
                shutdown_once["done"] = True
                _request_shutdown(2, None)
            return {"project_id": project_id, "bug_id": bug_id}

        with patch("d4j_odc_pipeline.batch.collect_bug_context", side_effect=fake_collect):
            first_summary = collect_batch_from_manifest(
                defects4j=client, manifest=manifest, artifacts_root=artifacts_root, work_root=work_root,
            )
            from d4j_odc_pipeline.batch import reset_shutdown
            reset_shutdown()
            second_summary = collect_batch_from_manifest(
                defects4j=client, manifest=manifest, artifacts_root=artifacts_root, work_root=work_root,
            )

        self.assertTrue(first_summary["interrupted"])
        self.assertEqual(1, first_summary["completed_entries"])
        self.assertFalse(second_summary["interrupted"])
        self.assertEqual(2, second_summary["completed_entries"])
        self.assertTrue(all(call[0] == "Math" for call in calls[2:]))

    def test_keep_work_preserves_checkout(self) -> None:
        from d4j_odc_pipeline.batch import collect_batch_from_manifest

        manifest = {"target_bugs": 1, "entries": [{"project_id": "Lang", "bug_id": 1}]}
        client = _FakeDefects4JClient()
        temp_root = self._scratch_dir("collect_keep_work")
        artifacts_root = temp_root / "artifacts"
        work_root = temp_root / "work"

        captured_work_dirs: list[Path] = []

        def fake_collect(*, project_id: str, bug_id: int, work_dir: Path, output_path: Path, **kwargs):
            work_dir.mkdir(parents=True, exist_ok=True)
            (work_dir / "marker.txt").write_text("checkout", encoding="utf-8")
            captured_work_dirs.append(work_dir)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps({"project_id": project_id, "bug_id": bug_id}), encoding="utf-8")
            return {"project_id": project_id, "bug_id": bug_id}

        with patch("d4j_odc_pipeline.batch.collect_bug_context", side_effect=fake_collect):
            collect_batch_from_manifest(
                defects4j=client, manifest=manifest, artifacts_root=artifacts_root,
                work_root=work_root, keep_work=True,
            )

        self.assertTrue(all(d.exists() for d in captured_work_dirs))

    def test_ledger_entry_has_no_condition_or_provider_fields(self) -> None:
        from d4j_odc_pipeline.batch import collect_batch_from_manifest

        manifest = {"target_bugs": 1, "entries": [{"project_id": "Lang", "bug_id": 1}]}
        client = _FakeDefects4JClient()
        temp_root = self._scratch_dir("collect_ledger")
        artifacts_root = temp_root / "artifacts"
        work_root = temp_root / "work"

        with patch("d4j_odc_pipeline.batch.collect_bug_context", side_effect=self._fake_collect):
            collect_batch_from_manifest(
                defects4j=client, manifest=manifest, artifacts_root=artifacts_root, work_root=work_root,
            )

        ledger_lines = (artifacts_root / "runs.jsonl").read_text(encoding="utf-8").strip().splitlines()
        entry = json.loads(ledger_lines[-1])
        self.assertEqual("collect-only", entry["mode"])
        self.assertNotIn("provider", entry)
        self.assertNotIn("condition_tag", entry)
        self.assertNotIn("llm_calls_made", entry)
