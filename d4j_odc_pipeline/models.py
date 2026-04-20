from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass
class StackFrame:
    class_name: str
    method_name: str
    file_name: str | None
    line_number: int | None
    raw: str


@dataclass
class Failure:
    test_name: str
    test_class: str
    test_method: str | None
    headline: str | None
    stack_trace: list[str]
    frames: list[StackFrame] = field(default_factory=list)


@dataclass
class CodeSnippet:
    class_name: str
    file_path: str
    start_line: int
    end_line: int
    focus_line: int | None
    reason: str
    content: str


@dataclass
class CoverageLine:
    line_number: int
    hits: int
    branch: bool = False


@dataclass
class CoverageClass:
    class_name: str
    filename: str | None
    line_rate: float | None
    branch_rate: float | None
    covered_lines: list[CoverageLine] = field(default_factory=list)


@dataclass
class BugContext:
    project_id: str
    bug_id: int
    version_id: str
    work_dir: str
    created_at: str
    defects4j_command: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)
    exports: dict[str, str] = field(default_factory=dict)
    failures: list[Failure] = field(default_factory=list)
    suspicious_frames: list[StackFrame] = field(default_factory=list)
    code_snippets: list[CodeSnippet] = field(default_factory=list)
    coverage: list[CoverageClass] = field(default_factory=list)
    hidden_oracles: dict[str, Any] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    bug_info: str = ""
    bug_report_content: str = ""
    fix_diff: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BugContext":
        failures = [
            Failure(
                test_name=item["test_name"],
                test_class=item["test_class"],
                test_method=item.get("test_method"),
                headline=item.get("headline"),
                stack_trace=item.get("stack_trace", []),
                frames=[StackFrame(**frame) for frame in item.get("frames", [])],
            )
            for item in data.get("failures", [])
        ]
        suspicious_frames = [StackFrame(**frame) for frame in data.get("suspicious_frames", [])]
        code_snippets = [CodeSnippet(**snippet) for snippet in data.get("code_snippets", [])]
        coverage = []
        for item in data.get("coverage", []):
            coverage.append(
                CoverageClass(
                    class_name=item["class_name"],
                    filename=item.get("filename"),
                    line_rate=item.get("line_rate"),
                    branch_rate=item.get("branch_rate"),
                    covered_lines=[CoverageLine(**line) for line in item.get("covered_lines", [])],
                )
            )
        return cls(
            project_id=data["project_id"],
            bug_id=int(data["bug_id"]),
            version_id=data["version_id"],
            work_dir=data["work_dir"],
            created_at=data.get("created_at", utc_now_iso()),
            defects4j_command=list(data.get("defects4j_command", [])),
            metadata=dict(data.get("metadata", {})),
            exports=dict(data.get("exports", {})),
            failures=failures,
            suspicious_frames=suspicious_frames,
            code_snippets=code_snippets,
            coverage=coverage,
            hidden_oracles=dict(data.get("hidden_oracles", {})),
            notes=list(data.get("notes", [])),
            bug_info=str(data.get("bug_info", "")),
            bug_report_content=str(data.get("bug_report_content", "")),
            fix_diff=str(data.get("fix_diff", "")),
        )


@dataclass
class ClassificationResult:
    project_id: str
    bug_id: int
    version_id: str
    prompt_style: str
    model: str
    provider: str
    created_at: str
    odc_type: str
    family: str | None
    confidence: float
    needs_human_review: bool
    observation_summary: str
    hypothesis: str
    prediction: str
    experiment_rationale: str
    reasoning_summary: str
    evidence_used: list[str]
    evidence_gaps: list[str]
    alternative_types: list[dict[str, str]]
    target: str | None = None
    qualifier: str | None = None
    age: str | None = None
    source: str | None = None
    inferred_activity: str | None = None
    inferred_triggers: list[str] = field(default_factory=list)
    inferred_impact: list[str] = field(default_factory=list)
    evidence_mode: str = "pre-fix"
    raw_response: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
