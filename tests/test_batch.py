import json
import shutil
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

from d4j_odc_pipeline.batch import analyze_batch_artifacts, generate_study_manifest, write_analysis_markdown


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

    def test_impact_distribution_and_stability_wired_into_summary(self) -> None:
        """Impact (opener attribute) analyses ride alongside type drift in the
        same study-drift summary (docs/odc_alignment_audit.md §6)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prefix_dir = root / "prefix"
            postfix_dir = root / "postfix"

            self._write_case(
                prefix_dir / "Lang_1_prefix",
                classification={
                    "project_id": "Lang", "bug_id": 1, "version_id": "1b",
                    "odc_type": "Checking", "family": "Control and Data Flow",
                    "impact": "Reliability", "confidence": 0.7,
                    "alternative_types": [], "reasoning_summary": "prefix",
                },
            )
            self._write_case(
                postfix_dir / "Lang_1_postfix",
                classification={
                    "project_id": "Lang", "bug_id": 1, "version_id": "1b",
                    "odc_type": "Checking", "family": "Control and Data Flow",
                    "impact": "Reliability", "confidence": 0.9,
                    "alternative_types": [], "reasoning_summary": "postfix",
                },
            )
            self._write_case(
                prefix_dir / "Math_2_prefix",
                classification={
                    "project_id": "Math", "bug_id": 2, "version_id": "2b",
                    "odc_type": "Algorithm/Method", "family": "Control and Data Flow",
                    "impact": "Capability", "confidence": 0.6,
                    "alternative_types": [], "reasoning_summary": "prefix",
                },
            )
            self._write_case(
                postfix_dir / "Math_2_postfix",
                classification={
                    "project_id": "Math", "bug_id": 2, "version_id": "2b",
                    "odc_type": "Algorithm/Method", "family": "Control and Data Flow",
                    "impact": "Reliability", "confidence": 0.9,
                    "alternative_types": [], "reasoning_summary": "postfix",
                },
            )

            summary = analyze_batch_artifacts(
                prefix_dir=prefix_dir, postfix_dir=postfix_dir,
                taxonomy="closed", strategy="scientific",
            )

            self.assertEqual(2, summary["impact_distribution_prefix"]["with_impact"])
            self.assertEqual(1, summary["impact_distribution_prefix"]["impact_counts"]["Reliability"])
            self.assertEqual(1, summary["impact_distribution_prefix"]["impact_counts"]["Capability"])
            self.assertTrue(summary["impact_vs_type_prefix"]["impact_type_pairs"])
            # Lang-1 impact agrees prefix/postfix; Math-2 impact disagrees.
            self.assertEqual(2, summary["impact_stability"]["pairs_with_impact"])
            self.assertEqual(1, summary["impact_stability"]["agreement_count"])

            md_path = root / "analysis.md"
            write_analysis_markdown(summary, md_path)
            markdown = md_path.read_text()
            self.assertIn("Impact (Opener Attribute", markdown)
            self.assertIn("Impact Stability", markdown)

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
