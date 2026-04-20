from __future__ import annotations

import json
import re
from pathlib import Path

from .defects4j import DEFAULT_EXPORT_PROPERTIES, DEFAULT_QUERY_FIELDS, Defects4JClient
from .llm import LLMClient, LLMError
from .models import BugContext, ClassificationResult, CodeSnippet, StackFrame, ensure_parent, utc_now_iso
from .odc import ODC_TYPE_NAMES, family_for
from .parsing import extract_json_object
from .prompting import build_messages
from .web_fetch import fetch_bug_report
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
    include_fix_diff: bool = False,
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

    # ── Fetch bug info from d4j info command ──────────────────────────
    bug_info = ""
    try:
        with console.spinner_step(f"Fetching bug info ({project_id}-{bug_id})"):
            bug_info = defects4j.info(project_id, bug_id)
        if bug_info:
            console.step("Bug info retrieved", detail=f"{len(bug_info)} chars")
        else:
            console.warn("No bug info returned")
    except Exception as exc:
        console.warn(f"Could not fetch bug info: {exc}")

    # ── Fetch bug report content from URL ─────────────────────────────
    bug_report_content = ""
    report_url = metadata.get("report.url", "")
    if report_url:
        with console.spinner_step("Fetching bug report page"):
            fetch_result = fetch_bug_report(report_url)
        bug_report_content = fetch_result.content
        if fetch_result.error:
            console.warn(f"Bug report fetch issue: {fetch_result.error}")
        elif bug_report_content:
            console.step(
                "Bug report fetched",
                detail=f"{fetch_result.content_length} chars via {fetch_result.source_type} ({fetch_result.duration_ms}ms)",
            )
        else:
            console.warn("Bug report page returned empty content")
    else:
        console.step("Bug report fetch skipped", detail="no report.url in metadata")

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

    # ── Extract production code snippets ──────────────────────────────
    with console.timed_step("Extracting code snippets from suspicious frames"):
        code_snippets = _extract_code_snippets(source_dirs, suspicious_frames, radius=snippet_radius)
    console.step(f"Production code snippets: {len(code_snippets)}")

    # ── Extract test source code snippets ─────────────────────────────
    with console.timed_step("Extracting test source code"):
        test_snippets = _extract_test_source(source_dirs, failures, radius=snippet_radius + 6)
    console.step(f"Test code snippets: {len(test_snippets)}")
    code_snippets.extend(test_snippets)

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

            # Attempt 1: Run coverage with instrument file for focused results
            with console.spinner_step(f"Running coverage on {len(interesting_classes)} class(es)"):
                coverage_result = defects4j.coverage(
                    work_dir,
                    single_test=single_test,
                    instrument_classes_file=instrument_file,
                )
            notes.append(f"Coverage exit code: {coverage_result.returncode}")

            # If coverage command failed, retry without instrument file
            if coverage_result.returncode not in (0, 1):
                console.warn(
                    f"Coverage failed (exit {coverage_result.returncode}), retrying without instrument file..."
                )
                if coverage_result.stderr:
                    notes.append(f"Coverage stderr (attempt 1): {coverage_result.stderr[:300]}")
                with console.spinner_step("Retrying coverage without instrument filter"):
                    coverage_result = defects4j.coverage(
                        work_dir,
                        single_test=single_test,
                    )
                notes.append(f"Coverage retry exit code: {coverage_result.returncode}")

            coverage = defects4j.parse_coverage_reports(work_dir, interesting_classes=interesting_classes)
            if coverage:
                console.step(f"Coverage parsed: {len(coverage)} class(es)")
            else:
                # Try parsing without the class filter as a last resort
                coverage = defects4j.parse_coverage_reports(work_dir)
                if coverage:
                    console.step(f"Coverage parsed (unfiltered): {len(coverage)} class(es)")
                else:
                    console.warn("No parseable coverage XML found after running defects4j coverage")
                    notes.append("No parseable coverage XML was found after running defects4j coverage.")
                    if coverage_result.stderr:
                        notes.append(f"Coverage stderr: {coverage_result.stderr[:300]}")
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
        bug_info=bug_info,
        bug_report_content=bug_report_content,
    )

    # ── Collect fix diff (optional, post-fix oracle) ──────────────────
    if include_fix_diff:
        with console.timed_step("Collecting buggy→fixed diff (post-fix oracle)"):
            fix_diff = _collect_fix_diff(
                defects4j=defects4j,
                project_id=project_id,
                bug_id=bug_id,
                work_dir=work_dir,
                source_dirs=source_dirs,
                modified_classes=metadata.get("classes.modified", ""),
            )
        if fix_diff:
            context.fix_diff = fix_diff
            context.notes.append(f"Fix diff collected ({len(fix_diff)} chars). This is post-fix oracle information.")
            console.step("Fix diff collected", detail=f"{len(fix_diff)} chars")
        else:
            console.warn("Could not collect fix diff")
            context.notes.append("Fix diff requested but could not be collected.")

    console.step(f"Writing context → {output_path}")
    write_json(output_path, context.to_dict())

    total_snippets_prod = len(code_snippets) - len(test_snippets)
    console.result_panel("Collection complete", [
        ("Project", f"{project_id}-{bug_id} ({version_id})"),
        ("Failing tests", str(len(failures))),
        ("Suspicious frames", str(len(suspicious_frames))),
        ("Production snippets", str(total_snippets_prod)),
        ("Test snippets", str(len(test_snippets))),
        ("Bug report", "fetched" if bug_report_content else "not available"),
        ("Bug info", "fetched" if bug_info else "not available"),
        ("Fix diff", f"{len(context.fix_diff)} chars" if context.fix_diff else ("not requested" if not include_fix_diff else "not available")),
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

    optional_rows: list[tuple[str, str]] = []
    if result.target:
        optional_rows.append(("Target", result.target))
    if result.qualifier:
        optional_rows.append(("Qualifier", result.qualifier))
    if result.age:
        optional_rows.append(("Age", result.age))
    if result.source:
        optional_rows.append(("Source", result.source))
    if result.inferred_activity:
        optional_rows.append(("Inferred Activity", result.inferred_activity))
    if result.inferred_triggers:
        optional_rows.append(("Inferred Triggers", ", ".join(result.inferred_triggers)))
    if result.inferred_impact:
        optional_rows.append(("Inferred Impact", ", ".join(result.inferred_impact)))

    summary_rows = [
        ("ODC Type", result.odc_type),
        ("Family", result.family or "—"),
        ("Confidence", f"{result.confidence:.2f}"),
        ("Evidence Mode", result.evidence_mode),
        ("Needs Human Review", review_text),
        ("Output", str(output_path)),
    ]
    summary_rows.extend(optional_rows)

    console.result_panel("Classification complete", summary_rows)

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
        evidence_label = (
            "\u26a0\ufe0f Post-fix (with buggy->fixed diff)"
            if classification.evidence_mode == "post-fix"
            else "\u2705 Pre-fix only"
        )
        lines.extend(
            [
                f"- **Evidence Mode**: {evidence_label}",
                f"- ODC Type: `{classification.odc_type}`",
                f"- Family: `{classification.family}`",
                f"- Target: `{classification.target or 'Design/Code'}`",
                f"- Confidence: `{classification.confidence}`",
                f"- Needs Human Review: `{classification.needs_human_review}`",
                "",
                classification.reasoning_summary,
            ]
        )
        closer_lines = []
        if classification.qualifier:
            closer_lines.append(f"- Qualifier: `{classification.qualifier}`")
        if classification.age:
            closer_lines.append(f"- Age: `{classification.age}`")
        if classification.source:
            closer_lines.append(f"- Source: `{classification.source}`")
        opener_lines = []
        if classification.inferred_activity:
            opener_lines.append(f"- Inferred Activity: `{classification.inferred_activity}`")
        if classification.inferred_triggers:
            opener_lines.append(f"- Inferred Triggers: `{', '.join(classification.inferred_triggers)}`")
        if classification.inferred_impact:
            opener_lines.append(f"- Inferred Impact: `{', '.join(classification.inferred_impact)}`")

        if closer_lines or opener_lines:
            lines.extend(["", "## ODC Attribute Mapping (Optional)"])
            lines.extend(closer_lines)
            lines.extend(opener_lines)
    ensure_parent(output_path)
    output_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    console.step(f"Report written → {output_path}")


def write_json(path: Path, payload: dict) -> None:
    ensure_parent(path)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_context(path: Path) -> BugContext:
    return BugContext.from_dict(json.loads(path.read_text(encoding="utf-8")))


# ---------------------------------------------------------------------------
# Framework class blocklist — these NEVER belong in suspicious frames
# ---------------------------------------------------------------------------

_FRAMEWORK_PREFIXES: tuple[str, ...] = (
    # JUnit
    "org.junit.",
    "junit.",
    # Test runners and utilities
    "org.hamcrest.",
    "org.mockito.",
    "org.powermock.",
    "org.easymock.",
    "org.assertj.",
    # Build tools
    "org.apache.tools.ant.",
    "org.apache.maven.",
    "org.gradle.",
    # JDK internals
    "java.",
    "javax.",
    "jdk.",
    "sun.",
    "com.sun.",
    # Reflection
    "jdk.internal.reflect.",
)


def _is_framework_class(class_name: str) -> bool:
    """Return True if the class belongs to a test/build/JDK framework."""
    for prefix in _FRAMEWORK_PREFIXES:
        if class_name.startswith(prefix):
            return True
    return False


def _looks_like_test_class(class_name: str) -> bool:
    """Return True if the class appears to be a test class."""
    simple = class_name.rsplit(".", 1)[-1].split("$")[0]
    lowered = simple.lower()
    return (
        lowered.endswith("test")
        or lowered.endswith("tests")
        or lowered.startswith("test")
        or "test" in class_name.lower().split("$")[-1:]
    )


def _select_suspicious_frames(failures: list) -> list[StackFrame]:
    """Select frames most likely to contain the bug.

    Strategy:
      1. Collect ALL non-framework, non-test frames from every failure.
      2. Prioritize project source frames (these are most useful for code extraction).
      3. Fall back to test frames only if zero project frames exist.
    """
    project_frames: list[StackFrame] = []
    test_frames: list[StackFrame] = []
    seen: set[tuple[str, int | None]] = set()

    for failure in failures:
        for frame in failure.frames:
            # Skip frames with missing/empty class names
            if not frame.class_name or not frame.class_name.strip():
                continue
            # Always skip framework / JDK / build-tool classes
            if _is_framework_class(frame.class_name):
                continue

            key = (frame.class_name, frame.line_number)
            if key in seen:
                continue
            seen.add(key)

            if _looks_like_test_class(frame.class_name):
                test_frames.append(frame)
            else:
                project_frames.append(frame)

    # Prefer project source frames; include test frames only as fallback
    selected = project_frames[:12]
    if not selected:
        selected = test_frames[:6]
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
    class_name = (frame.class_name or "").strip()
    if not class_name:
        return None

    # Convert e.g. "org.example.Foo$Inner" → "org/example/Foo.java"
    outer_class = class_name.split("$")[0]
    parts = [p for p in outer_class.split(".") if p]
    if not parts:
        return None

    try:
        relative = Path(*parts).with_suffix(".java")
    except (TypeError, ValueError):
        return None

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


# ---------------------------------------------------------------------------
# Fix diff collection (post-fix oracle)
# ---------------------------------------------------------------------------

def _collect_fix_diff(
    *,
    defects4j: Defects4JClient,
    project_id: str,
    bug_id: int,
    work_dir: Path,
    source_dirs: list[Path],
    modified_classes: str,
    max_chars: int = 8000,
) -> str:
    """Checkout the fixed version and diff modified classes against the buggy version.

    This is POST-FIX oracle information. It should only be included when
    the --include-fix-diff flag is used. The diff dramatically improves
    classification accuracy but violates the pre-fix-only methodology.
    """
    import difflib
    import shutil

    if not modified_classes:
        return ""

    # Parse the modified classes list (semicolon or comma separated)
    class_list = [c.strip() for c in modified_classes.replace(";", ",").split(",") if c.strip()]
    if not class_list:
        return ""

    # Checkout the fixed version in a sibling directory
    fixed_dir = work_dir.parent / f"{work_dir.name}_fixed"
    fixed_version = f"{bug_id}f"

    try:
        if fixed_dir.exists():
            shutil.rmtree(fixed_dir, ignore_errors=True)

        defects4j.checkout(project_id, fixed_version, fixed_dir)

        # Discover source dirs in the fixed checkout
        fixed_exports = defects4j.export_properties(fixed_dir, ["dir.src.classes"])
        fixed_source_dirs = _discover_source_dirs(fixed_dir, fixed_exports)

        diff_parts: list[str] = []
        total_chars = 0

        for class_name in class_list:
            if total_chars >= max_chars:
                diff_parts.append(f"\n... [truncated at {max_chars} chars, {len(class_list)} classes total]")
                break

            # Find the source file in both buggy and fixed versions
            dummy_frame = StackFrame(
                class_name=class_name,
                method_name="",
                file_name=None,
                line_number=None,
                raw="",
            )
            buggy_file = _resolve_java_file(source_dirs, dummy_frame)
            fixed_file = _resolve_java_file(fixed_source_dirs, dummy_frame)

            if not buggy_file or not buggy_file.exists():
                diff_parts.append(f"--- {class_name}: buggy source not found")
                continue
            if not fixed_file or not fixed_file.exists():
                diff_parts.append(f"--- {class_name}: fixed source not found")
                continue

            buggy_lines = buggy_file.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
            fixed_lines = fixed_file.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)

            diff = list(difflib.unified_diff(
                buggy_lines,
                fixed_lines,
                fromfile=f"{class_name} (buggy)",
                tofile=f"{class_name} (fixed)",
                n=3,
            ))

            if diff:
                diff_text = "".join(diff)
                diff_parts.append(diff_text)
                total_chars += len(diff_text)
            else:
                diff_parts.append(f"--- {class_name}: no differences found (identical)")

        return "\n".join(diff_parts).strip()

    except Exception:
        return ""
    finally:
        # Clean up the fixed checkout to save disk space
        if fixed_dir.exists():
            shutil.rmtree(fixed_dir, ignore_errors=True)




# ---------------------------------------------------------------------------
# Test source code extraction
# ---------------------------------------------------------------------------

def _extract_test_source(
    source_dirs: list[Path],
    failures: list,
    radius: int = 18,
) -> list[CodeSnippet]:
    """Extract source code of failing test methods.

    The test code shows WHAT the expected behavior is, which is critical
    for ODC classification — e.g., a null-check test hints at Checking,
    a numerical assertion hints at Algorithm/Assignment.
    """
    snippets: list[CodeSnippet] = []
    seen_tests: set[str] = set()

    for failure in failures[:3]:  # Limit to first 3 failures
        test_class = failure.test_class
        if not test_class or test_class in seen_tests:
            continue
        seen_tests.add(test_class)

        # Build a StackFrame-like object to resolve the test file
        test_frame = StackFrame(
            class_name=test_class,
            method_name=failure.test_method or "",
            file_name=None,
            line_number=None,
            raw="",
        )
        source_file = _resolve_java_file(source_dirs, test_frame)
        if not source_file or not source_file.exists():
            continue

        content = source_file.read_text(encoding="utf-8", errors="replace").splitlines()

        # Try to find the specific test method in the source
        method_name = failure.test_method
        if method_name:
            method_start, method_end = _find_method_bounds(content, method_name)
        else:
            method_start, method_end = None, None

        if method_start is not None and method_end is not None:
            # Extract just the test method + some context
            start_line = max(1, method_start - 2)
            end_line = min(len(content), method_end + 2)
        else:
            # Fallback: extract a chunk around the assertion line from the stack trace
            assertion_line = _find_test_assertion_line(failure)
            if assertion_line:
                start_line = max(1, assertion_line - radius)
                end_line = min(len(content), assertion_line + radius)
            else:
                # Last resort: first N lines of the test class
                start_line = 1
                end_line = min(len(content), 60)

        snippet_lines = []
        for line_no in range(start_line, end_line + 1):
            snippet_lines.append(f"  {line_no:4d}: {content[line_no - 1]}")

        snippets.append(
            CodeSnippet(
                class_name=test_class,
                file_path=str(source_file),
                start_line=start_line,
                end_line=end_line,
                focus_line=_find_test_assertion_line(failure),
                reason=f"Test source: {failure.test_name} (shows expected behavior)",
                content="\n".join(snippet_lines),
            )
        )

    return snippets


def _find_method_bounds(lines: list[str], method_name: str) -> tuple[int | None, int | None]:
    """Find the start and end line of a method in Java source."""
    method_start = None
    brace_depth = 0

    for i, line in enumerate(lines, start=1):
        if method_start is None:
            # Look for method declaration
            if method_name in line and ("void" in line or "public" in line or "@Test" in lines[max(0, i-2):i-1+1]):
                method_start = i
                brace_depth = line.count("{") - line.count("}")
        else:
            brace_depth += line.count("{") - line.count("}")
            if brace_depth <= 0:
                return method_start, i

    return method_start, len(lines) if method_start else (None, None)


def _find_test_assertion_line(failure) -> int | None:
    """Find the line number in the test class where the assertion failed."""
    test_class = failure.test_class
    if not test_class:
        return None
    for frame in failure.frames:
        if frame.class_name == test_class and frame.line_number:
            return frame.line_number
    return None


def _validate_classification_payload(
    *,
    payload: dict,
    context: BugContext,
    prompt_style: str,
    model: str,
    provider: str,
    raw_response: str,
) -> ClassificationResult:
    def _opt_text(value: object) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    def _opt_list(value: object) -> list[str]:
        if not isinstance(value, list):
            return []
        return [str(item).strip() for item in value if str(item).strip()]

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
        family=family_for(odc_type),  # Always use canonical mapping, never trust LLM
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
        target=_opt_text(payload.get("target")) or "Design/Code",
        qualifier=_opt_text(payload.get("qualifier")),
        age=_opt_text(payload.get("age")),
        source=_opt_text(payload.get("source")),
        inferred_activity=_opt_text(payload.get("inferred_activity")),
        inferred_triggers=_opt_list(payload.get("inferred_triggers")),
        inferred_impact=_opt_list(payload.get("inferred_impact")),
        evidence_mode="post-fix" if context.fix_diff else "pre-fix",
        raw_response=raw_response,
    )
