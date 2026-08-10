import unittest
from pathlib import Path

from d4j_odc_pipeline.models import CodeSnippet, CoverageClass, CoverageLine, Failure, StackFrame
from d4j_odc_pipeline.pipeline import (
    _augment_frames_with_coverage,
    _discover_production_classes,
    _extract_test_source,
    _merge_coverage,
)


class AugmentFramesWithCoverageTests(unittest.TestCase):
    """Mirrors the Closure-150 case: the stack trace never touches the
    actually-buggy class (an assertTrue fails inside the test itself), so
    _select_suspicious_frames falls back to test-only frames. Coverage
    should be able to rescue the real production class."""

    def test_adds_coverage_only_production_class(self) -> None:
        suspicious_frames = [
            StackFrame("com.example.FooTest", "testBar", "FooTest.java", 42, "raw", origin="stack_trace"),
        ]
        coverage = [
            CoverageClass(class_name="com.example.Foo", filename="Foo.java", line_rate=0.8, branch_rate=0.5),
        ]
        added = _augment_frames_with_coverage(suspicious_frames, coverage)
        self.assertEqual(added, 1)
        new_frame = suspicious_frames[-1]
        self.assertEqual(new_frame.class_name, "com.example.Foo")
        self.assertEqual(new_frame.origin, "coverage")
        self.assertIsNone(new_frame.line_number)

    def test_focuses_on_hottest_covered_line_not_top_of_file(self) -> None:
        """Regression: a coverage-derived frame with no line_number made
        _extract_code_snippets fall back to lines 1..2*radius of the file —
        for a real class that's the license header/imports, not anything
        relevant. Must focus on the most-executed line instead."""
        suspicious_frames: list[StackFrame] = []
        coverage = [
            CoverageClass(
                class_name="com.example.Foo",
                filename="Foo.java",
                line_rate=0.8,
                branch_rate=0.5,
                covered_lines=[CoverageLine(line_number=87, hits=58), CoverageLine(line_number=254, hits=33)],
            ),
        ]
        _augment_frames_with_coverage(suspicious_frames, coverage)
        self.assertEqual(suspicious_frames[0].line_number, 87)
        self.assertIn("hottest line 87", suspicious_frames[0].raw)

    def test_skips_classes_already_present(self) -> None:
        suspicious_frames = [
            StackFrame("com.example.Foo", "bar", "Foo.java", 10, "raw"),
        ]
        coverage = [CoverageClass(class_name="com.example.Foo", filename="Foo.java", line_rate=0.9, branch_rate=0.5)]
        added = _augment_frames_with_coverage(suspicious_frames, coverage)
        self.assertEqual(added, 0)
        self.assertEqual(len(suspicious_frames), 1)

    def test_skips_test_and_framework_classes(self) -> None:
        suspicious_frames: list[StackFrame] = []
        coverage = [
            CoverageClass(class_name="com.example.FooTest", filename="FooTest.java", line_rate=0.9, branch_rate=0.5),
            CoverageClass(class_name="org.junit.Assert", filename="Assert.java", line_rate=1.0, branch_rate=1.0),
            CoverageClass(class_name="com.example.Foo", filename="Foo.java", line_rate=0.5, branch_rate=0.5),
        ]
        added = _augment_frames_with_coverage(suspicious_frames, coverage)
        self.assertEqual(added, 1)
        self.assertEqual(suspicious_frames[0].class_name, "com.example.Foo")

    def test_zero_line_rate_excluded(self) -> None:
        suspicious_frames: list[StackFrame] = []
        coverage = [CoverageClass(class_name="com.example.Foo", filename="Foo.java", line_rate=0.0, branch_rate=0.0)]
        added = _augment_frames_with_coverage(suspicious_frames, coverage)
        self.assertEqual(added, 0)

    def test_respects_cap(self) -> None:
        suspicious_frames = [
            StackFrame(f"com.example.Existing{i}", "m", "F.java", 1, "raw") for i in range(11)
        ]
        coverage = [
            CoverageClass(class_name="com.example.A", filename="A.java", line_rate=0.9, branch_rate=0.5),
            CoverageClass(class_name="com.example.B", filename="B.java", line_rate=0.8, branch_rate=0.5),
        ]
        added = _augment_frames_with_coverage(suspicious_frames, coverage, cap=12)
        self.assertEqual(added, 1)
        self.assertEqual(len(suspicious_frames), 12)

    def test_ranked_by_line_rate_descending(self) -> None:
        suspicious_frames: list[StackFrame] = []
        coverage = [
            CoverageClass(class_name="com.example.Low", filename="Low.java", line_rate=0.2, branch_rate=0.1),
            CoverageClass(class_name="com.example.High", filename="High.java", line_rate=0.9, branch_rate=0.5),
        ]
        _augment_frames_with_coverage(suspicious_frames, coverage, cap=1)
        self.assertEqual(len(suspicious_frames), 1)
        self.assertEqual(suspicious_frames[0].class_name, "com.example.High")


class MergeCoverageTests(unittest.TestCase):
    def test_merges_max_line_rate_and_unions_lines(self) -> None:
        accumulated: dict[str, CoverageClass] = {}
        _merge_coverage(
            accumulated,
            [CoverageClass("com.example.Foo", "Foo.java", 0.3, 0.1, [CoverageLine(10, 1)])],
        )
        _merge_coverage(
            accumulated,
            [CoverageClass("com.example.Foo", "Foo.java", 0.7, 0.4, [CoverageLine(10, 2), CoverageLine(20, 1)])],
        )
        merged = accumulated["com.example.Foo"]
        self.assertEqual(merged.line_rate, 0.7)
        self.assertEqual(merged.branch_rate, 0.4)
        # line 10 kept once (first-seen), line 20 added
        self.assertEqual(sorted(l.line_number for l in merged.covered_lines), [10, 20])

    def test_new_class_added(self) -> None:
        accumulated: dict[str, CoverageClass] = {}
        _merge_coverage(accumulated, [CoverageClass("com.example.Bar", "Bar.java", 0.5, 0.2)])
        self.assertIn("com.example.Bar", accumulated)


class DiscoverProductionClassesTests(unittest.TestCase):
    def test_walks_src_dir_and_builds_fqcn(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            work_dir = Path(tmp)
            src = work_dir / "src"
            pkg_dir = src / "com" / "example"
            pkg_dir.mkdir(parents=True)
            (pkg_dir / "Foo.java").write_text("package com.example; class Foo {}", encoding="utf-8")
            classes = _discover_production_classes(work_dir, {"dir.src.classes": "src"})
            self.assertEqual(classes, {"com.example.Foo"})

    def test_missing_export_key_returns_empty(self) -> None:
        classes = _discover_production_classes(Path("."), {})
        self.assertEqual(classes, set())


class ExtractTestSourceDedupeTests(unittest.TestCase):
    """See docs/suspicious_frame_selection.md: when _select_suspicious_frames
    fell back to test frames, _extract_code_snippets already produced a
    "Stack frame from ..." entry for the same (class, line) — the
    corresponding "Test source: ..." entry would be near-duplicate content."""

    def _failure(self) -> Failure:
        return Failure(
            test_name="com.example.FooTest::testBar",
            test_class="com.example.FooTest",
            test_method="testBar",
            headline="junit.framework.AssertionFailedError",
            stack_trace=[],
            frames=[StackFrame("com.example.FooTest", "testBar", "FooTest.java", 251, "raw")],
        )

    def test_skips_when_already_covered(self) -> None:
        failure = self._failure()
        existing = [
            CodeSnippet(
                class_name="com.example.FooTest",
                file_path="FooTest.java",
                start_line=239,
                end_line=263,
                focus_line=251,
                reason="Stack frame from com.example.FooTest.testBar",
                content="...",
            )
        ]
        result = _extract_test_source([], [failure], existing_snippets=existing)
        self.assertEqual(result, [])

    def test_still_extracted_when_not_covered(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp)
            pkg_dir = src / "com" / "example"
            pkg_dir.mkdir(parents=True)
            lines = ["package com.example;", "class FooTest {"] + [f"  // line {i}" for i in range(3, 260)]
            (pkg_dir / "FooTest.java").write_text("\n".join(lines), encoding="utf-8")

            failure = self._failure()
            result = _extract_test_source([src], [failure], existing_snippets=[])
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].class_name, "com.example.FooTest")


if __name__ == "__main__":
    unittest.main()
