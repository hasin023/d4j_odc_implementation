import os
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


if __name__ == "__main__":
    unittest.main()
