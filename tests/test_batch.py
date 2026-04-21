import json
import tempfile
import unittest
from pathlib import Path

from d4j_odc_pipeline.batch import analyze_batch_artifacts, generate_study_manifest


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
            )

            self.assertEqual(2, summary["total_pairs"])
            self.assertEqual(2, summary["unique_projects"])
            self.assertIn("Chart", summary["missing_projects"])
            self.assertEqual(2, summary["type_changed_count"])
            self.assertTrue(summary["top3_alternative_match"])
            self.assertTrue(summary["top3_no_common_alternative"])

    @staticmethod
    def _write_case(case_dir: Path, *, classification: dict) -> None:
        case_dir.mkdir(parents=True, exist_ok=True)
        (case_dir / "classification.json").write_text(
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
        (case_dir / "report.md").write_text(
            "# Report\n\n## ODC Result\n- ODC Type: sample\n- Confidence: sample\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    unittest.main()
