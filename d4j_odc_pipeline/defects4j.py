from __future__ import annotations

import csv
import os
import shlex
import shutil
import subprocess
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .models import CoverageClass, CoverageLine
from .parsing import parse_failing_tests, parse_failing_tests_from_output

DEFAULT_QUERY_FIELDS = [
    "bug.id",
    "report.id",
    "report.url",
    "classes.modified",
    "classes.relevant",
    "tests.trigger",
    "tests.relevant",
]

DEFAULT_EXPORT_PROPERTIES = [
    "dir.src.classes",
    "dir.bin.classes",
    "dir.src.tests",
    "dir.bin.tests",
    "cp.compile",
    "cp.test",
    "tests.trigger",
    "tests.relevant",
]


class Defects4JError(RuntimeError):
    pass


@dataclass
class CommandResult:
    args: list[str]
    cwd: str
    returncode: int
    stdout: str
    stderr: str


class Defects4JClient:
    def __init__(self, command: str | None = None, timeout_seconds: int = 1800) -> None:
        raw_command = command or os.environ.get("DEFECTS4J_CMD") or "defects4j"
        self.command = shlex.split(raw_command, posix=False)
        self.timeout_seconds = timeout_seconds
        self.path_style = (os.environ.get("DEFECTS4J_PATH_STYLE") or "").strip().lower()
        if not self.path_style:
            self.path_style = "wsl" if self.command and self.command[0].lower() == "wsl" else "native"

    def ensure_available(self) -> None:
        executable = self.command[0]
        if len(self.command) == 1 and shutil.which(executable) is None:
            raise Defects4JError(
                f"Could not find '{executable}' on PATH. Set DEFECTS4J_CMD if you need a custom command prefix."
            )

    def run(
        self,
        subcommand: str,
        *args: str,
        cwd: Path | None = None,
        allow_failure: bool = False,
    ) -> CommandResult:
        self.ensure_available()
        normalized_args = self._normalize_args(args, cwd=cwd)
        cmd = [*self.command, subcommand, *normalized_args]
        env = os.environ.copy()
        env["TZ"] = "America/Los_Angeles"
        completed = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            env=env,
            capture_output=True,
            text=True,
            timeout=self.timeout_seconds,
            check=False,
        )
        result = CommandResult(
            args=cmd,
            cwd=str(cwd) if cwd else os.getcwd(),
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )
        if not allow_failure and completed.returncode != 0:
            raise Defects4JError(self._format_error(result))
        return result

    def checkout(self, project_id: str, version_id: str, work_dir: Path) -> CommandResult:
        work_dir.parent.mkdir(parents=True, exist_ok=True)
        return self.run("checkout", "-p", project_id, "-v", version_id, "-w", str(work_dir))

    # ------------------------------------------------------------------
    # Proxy / convenience methods for interactive CLI use
    # ------------------------------------------------------------------

    def pids(self) -> list[str]:
        """Return all available project IDs."""
        result = self.run("pids")
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]

    def bids(self, project_id: str, *, include_deprecated: bool = False) -> list[str]:
        """Return bug IDs for a project."""
        extra_args: list[str] = []
        if include_deprecated:
            extra_args.append("-A")
        result = self.run("bids", "-p", project_id, *extra_args)
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]

    def info(self, project_id: str, bug_id: int | None = None) -> str:
        """Return project or bug info as raw text."""
        args = ["-p", project_id]
        if bug_id is not None:
            args.extend(["-b", str(bug_id)])
        result = self.run("info", *args)
        return result.stdout.strip()

    def compile(self, work_dir: Path) -> CommandResult:
        return self.run("compile", "-w", str(work_dir))

    def test(self, work_dir: Path, single_test: str | None = None) -> CommandResult:
        args = ["-w", str(work_dir)]
        if single_test:
            args.extend(["-t", single_test])
        return self.run("test", *args, allow_failure=True)

    def coverage(
        self,
        work_dir: Path,
        *,
        single_test: str | None = None,
        instrument_classes_file: Path | None = None,
    ) -> CommandResult:
        args = ["-w", str(work_dir)]
        if single_test:
            args.extend(["-t", single_test])
        if instrument_classes_file and instrument_classes_file.exists():
            args.extend(["-i", str(instrument_classes_file)])
        return self.run("coverage", *args, allow_failure=True)

    def export_property(self, work_dir: Path, property_name: str) -> str | None:
        result = self.run("export", "-p", property_name, "-w", str(work_dir), allow_failure=True)
        if result.returncode != 0:
            return None
        return result.stdout.strip()

    def export_properties(self, work_dir: Path, property_names: Iterable[str]) -> dict[str, str]:
        exported: dict[str, str] = {}
        for property_name in property_names:
            value = self.export_property(work_dir, property_name)
            if value:
                exported[property_name] = value
        return exported

    def query_available_fields(self, project_id: str) -> list[str]:
        result = self.run("query", "-p", project_id, "-H", allow_failure=True)
        if result.returncode not in (0, 1):
            raise Defects4JError(self._format_error(result))
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            prefix = "Available fields:"
            if line.startswith(prefix):
                raw_fields = line[len(prefix) :].strip()
                return [field.strip() for field in raw_fields.split(",") if field.strip()]
        raise Defects4JError(
            "Defects4J did not return the available query fields in the expected format.\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )

    def query_bug_metadata(self, project_id: str, bug_id: int, preferred_fields: Iterable[str]) -> dict[str, str]:
        available = set(self.query_available_fields(project_id))
        fields = [field for field in preferred_fields if field in available]
        if not fields:
            return {}
        result = self.run("query", "-p", project_id, "-q", ",".join(fields))
        row_fields = list(fields)
        if "bug.id" not in row_fields:
            row_fields = ["bug.id", *row_fields]
        reader = csv.reader(result.stdout.splitlines())
        target_id = str(bug_id)
        for row in reader:
            if not row:
                continue
            if row[0] != target_id:
                continue
            record = {field: value for field, value in zip(row_fields, row)}
            return {field: record.get(field, "") for field in fields}
        return {}

    def read_failures(self, work_dir: Path, test_output: str) -> list:
        failing_tests_path = work_dir / "failing_tests"
        if failing_tests_path.exists():
            contents = failing_tests_path.read_text(encoding="utf-8", errors="replace")
            failures = parse_failing_tests(contents)
            if failures:
                return failures
        return parse_failing_tests_from_output(test_output)

    def parse_coverage_reports(
        self,
        work_dir: Path,
        interesting_classes: set[str] | None = None,
    ) -> list[CoverageClass]:
        reports = sorted(work_dir.rglob("coverage*.xml")) + sorted(work_dir.rglob("cobertura*.xml"))
        parsed: dict[str, CoverageClass] = {}
        for report in reports:
            try:
                root = ET.parse(report).getroot()
            except ET.ParseError:
                continue
            for class_element in root.findall(".//class"):
                class_name = class_element.attrib.get("name")
                if not class_name:
                    continue
                normalized = class_name.replace("/", ".")
                if interesting_classes and normalized not in interesting_classes:
                    continue
                line_rate = _float_or_none(class_element.attrib.get("line-rate"))
                branch_rate = _float_or_none(class_element.attrib.get("branch-rate"))
                coverage_class = parsed.setdefault(
                    normalized,
                    CoverageClass(
                        class_name=normalized,
                        filename=class_element.attrib.get("filename"),
                        line_rate=line_rate,
                        branch_rate=branch_rate,
                        covered_lines=[],
                    ),
                )
                for line_element in class_element.findall(".//line"):
                    try:
                        hits = int(line_element.attrib.get("hits", "0"))
                        line_number = int(line_element.attrib.get("number", "0"))
                    except ValueError:
                        continue
                    if hits <= 0 or line_number <= 0:
                        continue
                    coverage_class.covered_lines.append(
                        CoverageLine(
                            line_number=line_number,
                            hits=hits,
                            branch=line_element.attrib.get("branch", "false") == "true",
                        )
                    )
        for coverage_class in parsed.values():
            coverage_class.covered_lines.sort(key=lambda line: (-line.hits, line.line_number))
        return list(parsed.values())

    @staticmethod
    def _format_error(result: CommandResult) -> str:
        return (
            f"Defects4J command failed with exit code {result.returncode}\n"
            f"cwd: {result.cwd}\n"
            f"command: {' '.join(result.args)}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )

    def _normalize_args(self, args: Iterable[str], cwd: Path | None = None) -> list[str]:
        normalized: list[str] = []
        path_flags = {"-w", "-i", "-o"}
        args_list = list(args)
        index = 0
        while index < len(args_list):
            value = args_list[index]
            normalized.append(value)
            if value in path_flags and index + 1 < len(args_list):
                normalized.append(self._normalize_path_arg(args_list[index + 1], cwd=cwd))
                index += 2
                continue
            index += 1
        return normalized

    def _normalize_path_arg(self, value: str, cwd: Path | None = None) -> str:
        if self.path_style != "wsl":
            return value
        base_dir = cwd or Path.cwd()
        path = Path(value)
        if not path.is_absolute():
            path = (base_dir / path).resolve()
        else:
            path = path.resolve()
        return windows_to_wsl_path(path)


def _float_or_none(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def windows_to_wsl_path(path: Path) -> str:
    raw = str(path)
    drive, tail = os.path.splitdrive(raw)
    if not drive:
        return raw.replace("\\", "/")
    drive_letter = drive[0].lower()
    tail = tail.replace("\\", "/")
    if not tail.startswith("/"):
        tail = "/" + tail
    return f"/mnt/{drive_letter}{tail}"
