import os
import tempfile
import unittest
from pathlib import Path

from d4j_odc_pipeline.defects4j import Defects4JClient, windows_to_wsl_path


class Defects4JClientTests(unittest.TestCase):
    def test_windows_to_wsl_path_formats_drive_letter(self) -> None:
        raw = Path(r"C:\WORK\IUT\Research\implementation\work\Lang_1b")
        self.assertEqual(
            "/mnt/c/WORK/IUT/Research/implementation/work/Lang_1b",
            windows_to_wsl_path(raw),
        )

    def test_normalize_args_converts_work_dir_for_wsl(self) -> None:
        old_value = os.environ.get("DEFECTS4J_PATH_STYLE")
        os.environ["DEFECTS4J_PATH_STYLE"] = "wsl"
        try:
            client = Defects4JClient(command="wsl perl /mnt/c/tools/defects4j/framework/bin/defects4j")
            normalized = client._normalize_args(["-p", "Lang", "-w", r"work\Lang_1b"], cwd=Path(r"C:\repo"))
            self.assertEqual("-w", normalized[2])
            self.assertEqual("/mnt/c/repo/work/Lang_1b", normalized[3])
        finally:
            if old_value is None:
                os.environ.pop("DEFECTS4J_PATH_STYLE", None)
            else:
                os.environ["DEFECTS4J_PATH_STYLE"] = old_value


class ParseCoverageReportsTests(unittest.TestCase):
    """Regression: Cobertura XML lists each line under BOTH the class-level
    aggregate <lines> AND its containing <method>'s <lines> sub-block.
    Matching ".//line" (any descendant) double-counted every line that
    belongs to a method — i.e. nearly all of them. Found via a live Closure-
    150 collect once coverage started actually populating (see
    docs/suspicious_frame_selection.md): every covered_lines entry appeared
    exactly twice."""

    _COBERTURA_XML = """<?xml version="1.0"?>
<coverage line-rate="0.78" branch-rate="0.42">
  <packages>
    <package name="com.example">
      <classes>
        <class name="com/example/Foo" filename="com/example/Foo.java" line-rate="0.78" branch-rate="0.42">
          <methods>
            <method name="bar" signature="()V" line-rate="1.0" branch-rate="1.0">
              <lines>
                <line number="87" hits="58" branch="false"/>
              </lines>
            </method>
          </methods>
          <lines>
            <line number="87" hits="58" branch="false"/>
            <line number="254" hits="33" branch="false"/>
          </lines>
        </class>
      </classes>
    </package>
  </packages>
</coverage>"""

    def test_line_covered_by_a_method_is_not_double_counted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            work_dir = Path(tmp)
            (work_dir / "coverage.xml").write_text(self._COBERTURA_XML, encoding="utf-8")
            client = Defects4JClient(command="defects4j")
            classes = client.parse_coverage_reports(work_dir)
            self.assertEqual(len(classes), 1)
            line_numbers = [line.line_number for line in classes[0].covered_lines]
            self.assertEqual(sorted(line_numbers), [87, 254])  # not [87, 87, 254, 254]


if __name__ == "__main__":
    unittest.main()
