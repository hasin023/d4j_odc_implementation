from __future__ import annotations

import json
from pathlib import Path

from .defects4j import DEFAULT_EXPORT_PROPERTIES, DEFAULT_QUERY_FIELDS, Defects4JClient
from .llm import LLMClient, LLMError
from .models import BugContext, ClassificationResult, CodeSnippet, StackFrame, ensure_parent, utc_now_iso
from .odc import ODC_TYPE_NAMES, coarse_group_for
from .parsing import extract_json_object
from .prompting import build_messages
from . import console


def collect_bug_context(
    *,
    defects4j: Defects4JClient,
    project_id: str,
    bug_id: int,
    work_dir: Path,
    output_path: Path,
    snippet_radius: int = 12,
    run_coverage: bool = True,
) -> BugContext:
    version_id = f"{bug_id}b"

    console.header_panel(
        f"Collecting bug context: {project_id}-{bug_id}",
        f"Version {version_id}  •  Work dir: {work_dir}",
    )

    with console.spinner_step("Querying bug metadata"):
        metadata = defects4j.query_bug_metadata(project_id, bug_id, DEFAULT_QUERY_FIELDS)
    if metadata:
        console.step("Metadata retrieved", detail=f"{len(metadata)} fields")
    else:
        console.warn("No metadata fields returned by Defects4J query")

    with console.spinner_step(f"Checking out {project_id} {version_id}"):
        defects4j.checkout(project_id, version_id, work_dir)

    with console.spinner_step("Compiling buggy version"):
        compile_result = defects4j.compile(work_dir)

    with console.spinner_step("Running tests on buggy version"):
        test_result = defects4j.test(work_dir)

    console.step("Parsing test failures...")
    failures = defects4j.read_failures(work_dir, test_result.stdout + "\n" + test_result.stderr)
    if failures:
        console.step(f"Failing tests found: {len(failures)}", detail=", ".join(f.test_name for f in failures[:3]))
    else:
        console.warn("No failing tests were parsed")

    with console.timed_step("Exporting Defects4J properties"):
        exports = defects4j.export_properties(work_dir, DEFAULT_EXPORT_PROPERTIES)
    console.step("Properties exported", detail=f"{len(exports)} properties")

    notes: list[str] = []
    notes.append(f"Compilation exit code: {compile_result.returncode}")
    notes.append(f"Test exit code on buggy version: {test_result.returncode}")

    console.step("Selecting suspicious stack frames...")
    suspicious_frames = _select_suspicious_frames(failures)
    console.step(f"Suspicious frames: {len(suspicious_frames)}")

    console.step("Discovering source directories...")
    source_dirs = _discover_source_dirs(work_dir, exports)
    console.step(f"Source directories: {len(source_dirs)}")

    with console.timed_step("Extracting code snippets"):
        code_snippets = _extract_code_snippets(source_dirs, suspicious_frames, radius=snippet_radius)
    console.step(f"Code snippets extracted: {len(code_snippets)}")

    hidden_oracles = {}
    if metadata.get("classes.modified"):
        hidden_oracles["classes.modified"] = metadata["classes.modified"]
        notes.append("Stored classes.modified as hidden oracle only; it is excluded from the LLM prompt by default.")
        console.step("Hidden oracle stored", detail="classes.modified (excluded from prompt)")

    coverage = []
    if run_coverage:
        interesting_classes = {frame.class_name for frame in suspicious_frames}
        if interesting_classes:
            instrument_file = output_path.parent / "instrument_classes.txt"
            ensure_parent(instrument_file)
            instrument_file.write_text("\n".join(sorted(interesting_classes)), encoding="utf-8")
            single_test = failures[0].test_name if failures else None
            with console.spinner_step(f"Running coverage on {len(interesting_classes)} class(es)"):
                coverage_result = defects4j.coverage(
                    work_dir,
                    single_test=single_test,
                    instrument_classes_file=instrument_file,
                )
            notes.append(f"Coverage exit code: {coverage_result.returncode}")
            coverage = defects4j.parse_coverage_reports(work_dir, interesting_classes=interesting_classes)
            if coverage:
                console.step(f"Coverage parsed: {len(coverage)} class(es)")
            else:
                console.warn("No parseable coverage XML found after running defects4j coverage")
                notes.append("No parseable coverage XML was found after running defects4j coverage.")
        else:
            console.step("Coverage skipped", detail="no suspicious source frames available")
            notes.append("Coverage skipped because no suspicious source frames were available.")
    else:
        console.step("Coverage skipped", detail="--skip-coverage flag set")

    context = BugContext(
        project_id=project_id,
        bug_id=bug_id,
        version_id=version_id,
        work_dir=str(work_dir),
        created_at=utc_now_iso(),
        defects4j_command=list(defects4j.command),
        metadata=metadata,
        exports=exports,
        failures=failures,
        suspicious_frames=suspicious_frames,
        code_snippets=code_snippets,
        coverage=coverage,
        hidden_oracles=hidden_oracles,
        notes=notes,
    )

    console.step(f"Writing context → {output_path}")
    write_json(output_path, context.to_dict())

    console.result_panel("Collection complete", [
        ("Project", f"{project_id}-{bug_id} ({version_id})"),
        ("Failing tests", str(len(failures))),
        ("Suspicious frames", str(len(suspicious_frames))),
        ("Code snippets", str(len(code_snippets))),
        ("Coverage classes", str(len(coverage))),
        ("Output", str(output_path)),
    ])

    return context


def classify_bug_context(
    *,
    context: BugContext,
    prompt_style: str,
    output_path: Path,
    provider: str,
    model: str,
    api_key_env: str,
    base_url: str | None = None,
    prompt_output_path: Path | None = None,
    dry_run: bool = False,
) -> ClassificationResult | None:
    console.header_panel(
        f"Classifying: {context.project_id}-{context.bug_id}",
        f"Provider: {provider}  •  Model: {model}  •  Style: {prompt_style}",
    )

    with console.timed_step(f"Building prompt ({prompt_style})"):
        messages = build_messages(context, prompt_style)

    if prompt_output_path:
        ensure_parent(prompt_output_path)
        prompt_output_path.write_text(json.dumps(messages, indent=2), encoding="utf-8")
        console.step(f"Prompt saved → {prompt_output_path}")

    if dry_run:
        console.warn("Dry run — skipping LLM call")
        console.result_panel("Dry run complete", [
            ("Prompt style", prompt_style),
            ("Prompt saved", str(prompt_output_path) if prompt_output_path else "not saved"),
        ])
        return None

    with console.spinner_step(f"Calling {provider} ({model})"):
        client = LLMClient.from_env(
            provider=provider,
            model=model,
            api_key_env=api_key_env,
            base_url=base_url,
        )
        raw_response = client.complete(messages)

    console.step("Parsing LLM response...")
    payload = extract_json_object(raw_response)
    result = _validate_classification_payload(
        payload=payload,
        context=context,
        prompt_style=prompt_style,
        model=model,
        provider=provider,
        raw_response=raw_response,
    )

    console.step(f"Writing classification → {output_path}")
    write_json(output_path, result.to_dict())

    confidence_style = "green" if result.confidence >= 0.7 else "yellow" if result.confidence >= 0.4 else "red"
    review_text = "Yes" if result.needs_human_review else "No"

    console.result_panel("Classification complete", [
        ("ODC Type", result.odc_type),
        ("Coarse Group", result.coarse_group or "—"),
        ("Confidence", f"{result.confidence:.2f}"),
        ("Needs Human Review", review_text),
        ("Output", str(output_path)),
    ])

    return result


def write_markdown_report(
    *,
    context: BugContext,
    classification: ClassificationResult | None,
    output_path: Path,
) -> None:
    lines = [
        f"# Defects4J ODC Classification Report: {context.project_id}-{context.bug_id}",
        "",
        f"- Version: `{context.version_id}`",
        f"- Work directory: `{context.work_dir}`",
        f"- Generated: `{utc_now_iso()}`",
        "",
        "## Failure Summary",
    ]
    if context.failures:
        for failure in context.failures:
            lines.append(f"- `{failure.test_name}`: {failure.headline or 'No headline captured'}")
    else:
        lines.append("- No failing tests were parsed.")
    lines.extend(["", "## Suspicious Frames"])
    if context.suspicious_frames:
        for frame in context.suspicious_frames[:10]:
            location = f"{frame.file_name}:{frame.line_number}" if frame.file_name and frame.line_number else frame.raw
            lines.append(f"- `{frame.class_name}.{frame.method_name}` at `{location}`")
    else:
        lines.append("- No suspicious stack frames were extracted.")

    lines.extend(["", "## ODC Result"])
    if classification is None:
        lines.append("- No classification was executed. Prompt messages were generated only.")
    else:
        lines.extend(
            [
                f"- ODC Type: `{classification.odc_type}`",
                f"- Coarse Group: `{classification.coarse_group}`",
                f"- Confidence: `{classification.confidence}`",
                f"- Needs Human Review: `{classification.needs_human_review}`",
                "",
                classification.reasoning_summary,
            ]
        )
    ensure_parent(output_path)
    output_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    console.step(f"Report written → {output_path}")


def write_json(path: Path, payload: dict) -> None:
    ensure_parent(path)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_context(path: Path) -> BugContext:
    return BugContext.from_dict(json.loads(path.read_text(encoding="utf-8")))


def _select_suspicious_frames(failures: list) -> list[StackFrame]:
    selected: list[StackFrame] = []
    seen: set[tuple[str, int | None]] = set()
    for failure in failures:
        for frame in failure.frames:
            if _looks_like_test_class(frame.class_name):
                continue
            key = (frame.class_name, frame.line_number)
            if key in seen:
                continue
            seen.add(key)
            selected.append(frame)
            if len(selected) >= 12:
                return selected
    return selected


def _discover_source_dirs(work_dir: Path, exports: dict[str, str]) -> list[Path]:
    candidates = []
    for key in ("dir.src.classes", "dir.src.tests"):
        value = exports.get(key)
        if not value:
            continue
        for part in value.split(":"):
            part = part.strip()
            if not part:
                continue
            candidates.append((work_dir / part).resolve())
    if not candidates:
        for fallback in ("src/main/java", "src/java", "source", "src"):
            path = (work_dir / fallback).resolve()
            if path.exists():
                candidates.append(path)
    deduped: list[Path] = []
    seen = set()
    for candidate in candidates:
        if candidate.exists() and candidate not in seen:
            deduped.append(candidate)
            seen.add(candidate)
    return deduped


def _extract_code_snippets(source_dirs: list[Path], frames: list[StackFrame], radius: int) -> list[CodeSnippet]:
    snippets: list[CodeSnippet] = []
    seen_paths: set[tuple[str, int | None]] = set()
    for frame in frames:
        source_file = _resolve_java_file(source_dirs, frame)
        if not source_file or not source_file.exists():
            continue
        key = (str(source_file), frame.line_number)
        if key in seen_paths:
            continue
        seen_paths.add(key)
        content = source_file.read_text(encoding="utf-8", errors="replace").splitlines()
        focus_line = frame.line_number if frame.line_number and frame.line_number > 0 else None
        if focus_line:
            start_line = max(1, focus_line - radius)
            end_line = min(len(content), focus_line + radius)
        else:
            start_line = 1
            end_line = min(len(content), 2 * radius + 1)
        snippet_lines = []
        for line_no in range(start_line, end_line + 1):
            marker = ">>" if focus_line == line_no else "  "
            snippet_lines.append(f"{marker} {line_no:4d}: {content[line_no - 1]}")
        snippets.append(
            CodeSnippet(
                class_name=frame.class_name,
                file_path=str(source_file),
                start_line=start_line,
                end_line=end_line,
                focus_line=focus_line,
                reason=f"Stack frame from {frame.class_name}.{frame.method_name}",
                content="\n".join(snippet_lines),
            )
        )
    return snippets


def _resolve_java_file(source_dirs: list[Path], frame: StackFrame) -> Path | None:
    relative = Path(*frame.class_name.split("$")[0].split(".")).with_suffix(".java")
    for source_dir in source_dirs:
        candidate = source_dir / relative
        if candidate.exists():
            return candidate
    if frame.file_name:
        for source_dir in source_dirs:
            matches = list(source_dir.rglob(frame.file_name))
            if matches:
                return matches[0]
    return None


def _looks_like_test_class(class_name: str) -> bool:
    lowered = class_name.lower()
    return lowered.endswith("test") or ".test" in lowered or "$test" in lowered


def _validate_classification_payload(
    *,
    payload: dict,
    context: BugContext,
    prompt_style: str,
    model: str,
    provider: str,
    raw_response: str,
) -> ClassificationResult:
    odc_type = payload.get("odc_type")
    if odc_type not in ODC_TYPE_NAMES:
        raise LLMError(f"Invalid or missing odc_type in LLM output: {odc_type!r}")
    confidence = float(payload.get("confidence", 0.0))
    confidence = min(1.0, max(0.0, confidence))
    return ClassificationResult(
        project_id=context.project_id,
        bug_id=context.bug_id,
        version_id=context.version_id,
        prompt_style=prompt_style,
        model=model,
        provider=provider,
        created_at=utc_now_iso(),
        odc_type=odc_type,
        coarse_group=payload.get("coarse_group") or coarse_group_for(odc_type),
        confidence=confidence,
        needs_human_review=bool(payload.get("needs_human_review", False)),
        observation_summary=str(payload.get("observation_summary", "")).strip(),
        hypothesis=str(payload.get("hypothesis", "")).strip(),
        prediction=str(payload.get("prediction", "")).strip(),
        experiment_rationale=str(payload.get("experiment_rationale", "")).strip(),
        reasoning_summary=str(payload.get("reasoning_summary", "")).strip(),
        evidence_used=[str(item) for item in payload.get("evidence_used", [])],
        evidence_gaps=[str(item) for item in payload.get("evidence_gaps", [])],
        alternative_types=[
            {"type": str(item.get("type", "")), "why_not_primary": str(item.get("why_not_primary", ""))}
            for item in payload.get("alternative_types", [])
            if isinstance(item, dict)
        ],
        raw_response=raw_response,
    )
