"""
ICSEA sub-paper: "Can an LLM Write the Missing Test?"

Automated JUnit 4 test generation from Defects4J bug reports.
All functions are additive — the ODC pipeline is not modified.
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .defects4j import Defects4JClient, Defects4JError
from .llm import LLMClient
from .models import BugContext, utc_now_iso


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class TestGenResult:
    project_id: str
    bug_id: int
    prefix_work_dir: str
    postfix_work_dir: str
    model: str
    provider: str
    created_at: str

    prompt_style: str
    generated_class_name: str
    generated_method_name: str
    generated_test_code: str
    raw_llm_response: str

    compilation_success: bool
    compilation_error: str | None

    fails_on_buggy: bool | None
    passes_on_fixed: bool | None
    oracle_match: bool | None

    # Ground-truth comparison (against actual Defects4J trigger tests)
    trigger_methods: list[str]      # from exports["tests.trigger"]
    trigger_test_source: str        # actual source of the trigger test method(s)
    method_name_match: bool
    trigger_class_targeted: bool
    modified_class: str | None

    buggy_stdout: str
    buggy_stderr: str
    fixed_stdout: str
    fixed_stderr: str

    notes: list[str] = field(default_factory=list)

    # Self-correction loop tracking
    refine_iterations: int = 0
    refine_history: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Oracle-clean failure headline stripping
# ---------------------------------------------------------------------------

# Matches the "expected:<…> but " part of JUnit ComparisonFailure messages.
# This value IS the correct post-fix expected value — stripping it prevents
# the LLM from trivially copying the answer.
_EXPECTED_RE = re.compile(r"expected:<[^>]*>\s+but\s+", re.IGNORECASE)


def _clean_failure_headline(headline: str) -> str:
    """Strip `expected:<X> but ` from JUnit assertion messages; keep `was:<Y>`."""
    return _EXPECTED_RE.sub("", headline).strip()


# ---------------------------------------------------------------------------
# Test class source processing — strip trigger method bodies
# ---------------------------------------------------------------------------

def _find_method_end(lines: list[str], start: int) -> int:
    """Return the index of the line containing the closing brace of the method
    starting at `start`. Uses brace counting."""
    depth = 0
    started = False
    for j in range(start, len(lines)):
        for ch in lines[j]:
            if ch == "{":
                depth += 1
                started = True
            elif ch == "}":
                depth -= 1
        if started and depth == 0:
            return j
    return len(lines) - 1


def _strip_trigger_methods(source: str, trigger_names: set[str]) -> str:
    """Return the test class source with every trigger test method body replaced
    by a one-line stub comment. Everything else (constants, helpers, imports,
    non-trigger tests) is kept verbatim so the LLM sees real infrastructure."""
    if not trigger_names:
        return source

    lines = source.splitlines()
    result: list[str] = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Detect a trigger method declaration:
        # the method name must appear followed by "(" and the line must contain "void "
        matched: str | None = None
        for name in trigger_names:
            if name + "(" in line and "void " in line:
                matched = name
                break

        if matched is not None:
            # Find where the method body ends (brace counting)
            end = _find_method_end(lines, i)
            # Emit a stub comment instead of the full body
            indent = " " * (len(line) - len(line.lstrip()))
            result.append(f"{indent}// [trigger test '{matched}' — body omitted]")
            i = end + 1
        else:
            result.append(line)
            i += 1

    return "\n".join(result)


def _build_test_class_section(
    test_class_sources: dict[str, str],
    trigger_raw: str,
) -> str:
    """Build the 'TEST CLASS INFRASTRUCTURE' prompt section.

    Shows the full test class source MINUS trigger method bodies, giving the
    LLM access to constants (e.g. ZONE_MOSCOW) and helper methods
    (e.g. doTest_getOffsetFromLocal) without leaking ground-truth assertions.
    """
    if not test_class_sources:
        return ""

    trigger_names: set[str] = {
        t.split("::")[-1]
        for t in re.split(r"[,\n]+", trigger_raw)
        if "::" in t and t.strip()
    }

    parts: list[str] = []
    for fqn, full_source in test_class_sources.items():
        stripped = _strip_trigger_methods(full_source, trigger_names)
        if stripped.strip():
            parts.append(f"// Test infrastructure: {fqn}\n{stripped}")

    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------

def build_test_gen_prompt(
    context: BugContext,
    prompt_style: str = "full",
) -> list[dict[str, str]]:
    """
    Build [system, user] messages for LLM test generation.

    prompt_style:
      "full"        – bug report + failure headlines + code snippets + test class infrastructure
      "report_only" – bug report + failure headlines only
      "code_only"   – code snippets + test class infrastructure only

    Oracle rules enforced here:
      - failure headlines: expected:<X> stripped, only was:<Y> shown
      - test class: trigger method bodies replaced with stub comments
      - trigger method names from tests.trigger: never mentioned in prompt
    """
    package_name, class_name = infer_package_and_class(context)

    system_content = (
        "You are an expert Java developer working with JUnit 4.\n\n"
        "Your task: given a bug report and relevant source code, write a complete Java test class "
        "with exactly ONE @Test method that:\n"
        "  1. FAILS when run against the buggy version of the code\n"
        "  2. PASSES when run against the fixed version\n"
        "  3. Is minimal and targeted — it proves the bug exists\n\n"
        "Return ONLY the complete Java source file (package declaration + imports + class + one @Test method).\n"
        "No markdown fences, no explanation — just the .java file content.\n"
        f"Use JUnit 4 (org.junit.*) only. Use package: {package_name or '(root package)'}."
    )

    sections: list[str] = []

    # Derive trigger raw once — used for both headline cleaning and class-section building
    trigger_raw = context.exports.get("tests.trigger", "")

    if prompt_style in ("full", "report_only"):
        if context.bug_report_content:
            sections.append(f"=== BUG REPORT ===\n{context.bug_report_content}")

        # Strip expected:<X> from headlines; keep was:<Y> (what the buggy code produced)
        failure_headlines = [
            _clean_failure_headline(f.headline)
            for f in context.failures
            if f.headline
        ]
        if failure_headlines:
            sections.append(
                "=== OBSERVED FAILURES ===\n" + "\n".join(f"- {h}" for h in failure_headlines)
            )

    if prompt_style in ("full", "code_only"):
        prod_snippets = [
            s for s in context.code_snippets
            if not _is_test_snippet(s.class_name, s.reason)
        ]

        if prod_snippets:
            parts = []
            for snippet in prod_snippets:
                parts.append(
                    f"// File: {snippet.file_path} (lines {snippet.start_line}-{snippet.end_line})\n"
                    f"// Class: {snippet.class_name}\n"
                    f"{snippet.content}"
                )
            sections.append("=== BUGGY PRODUCTION CODE ===\n" + "\n\n".join(parts))

        # Primary path: use stored full test class sources with trigger bodies stripped
        if context.test_class_sources:
            infra = _build_test_class_section(context.test_class_sources, trigger_raw)
            if infra:
                sections.append(
                    "=== TEST CLASS INFRASTRUCTURE (trigger test bodies omitted) ===\n" + infra
                )
        else:
            # Fallback for old context.json without test_class_sources:
            # show class header only (package + imports + class declaration)
            test_snippets = [
                s for s in context.code_snippets
                if _is_test_snippet(s.class_name, s.reason)
            ]
            if test_snippets:
                ref_parts = []
                for snippet in test_snippets[:2]:
                    header = _extract_class_header(snippet.content)
                    if header:
                        ref_parts.append(
                            f"// Existing test class reference (structure only): {snippet.class_name}\n{header}"
                        )
                if ref_parts:
                    sections.append(
                        "=== EXISTING TEST STRUCTURE (for reference) ===\n" + "\n\n".join(ref_parts)
                    )

    user_content = (
        f"Write a JUnit 4 test for {context.project_id} bug #{context.bug_id}.\n\n"
        + "\n\n".join(sections)
        + (
            f"\n\nRequired class name: {class_name}\n"
            f"Required package: {package_name or '(root package)'}"
        )
    )

    return [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_content},
    ]


def _is_test_snippet(class_name: str, reason: str) -> bool:
    simple = class_name.split(".")[-1]
    return (
        simple.startswith("Test") or simple.endswith("Test") or simple.endswith("Tests")
        or "test" in reason.lower()
    )


def _extract_class_header(java_source: str) -> str:
    """Extract package declaration + imports + class opening line from Java source.

    Returns empty string if no package or class declaration is found
    (e.g. for line-windowed snippets that start mid-class).
    The empty-string return is intentional — callers skip empty results rather
    than falling back to raw snippet content, which would leak method bodies.
    """
    lines = java_source.splitlines()
    header_lines: list[str] = []
    in_class = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("package ") or stripped.startswith("import "):
            header_lines.append(line)
        elif "class " in stripped and "{" in stripped and not in_class:
            header_lines.append(line)
            header_lines.append("    // ... (existing test methods omitted)")
            header_lines.append("}")
            in_class = True
            break
    # Return empty string if we never found a package/class — the old
    # java_source[:500] fallback was the source of oracle leakage.
    return "\n".join(header_lines)


# ---------------------------------------------------------------------------
# Trigger test source extraction (ground truth — never sent to LLM)
# ---------------------------------------------------------------------------

def extract_trigger_test_source(context: BugContext) -> str:
    """
    Read the actual Defects4J trigger test method(s) from the work_dir source tree.

    Returns the concatenated source of all trigger test methods found, or an
    empty string if the files cannot be located.

    NOTE: This is ground-truth data used only for post-generation comparison.
    It is NEVER included in the LLM prompt.

    The trigger format in exports["tests.trigger"] is:
        org.joda.time.TestDateTimeZoneCutover::test_DateTime_constructor_Moscow_Autumn
    Multiple triggers are newline-separated.
    """
    trigger_raw = context.exports.get("tests.trigger", "")
    if not trigger_raw:
        return ""

    triggers = [t.strip() for t in re.split(r"[,\n]+", trigger_raw) if t.strip()]
    test_src_dir = context.exports.get("dir.src.tests", "src/test/java")
    work_path = Path(context.work_dir)

    extracted: list[str] = []
    for trigger in triggers:
        if "::" not in trigger:
            continue
        class_fqn, method_name = trigger.split("::", 1)
        rel_path = class_fqn.replace(".", "/") + ".java"
        java_file = work_path / test_src_dir / rel_path
        if not java_file.exists():
            continue
        source = java_file.read_text(encoding="utf-8", errors="replace")
        method_body = _extract_method_body(source, method_name)
        if method_body:
            extracted.append(f"// Source: {trigger}\n{method_body}")

    return "\n\n".join(extracted)


def _extract_method_body(java_source: str, method_name: str) -> str:
    """Extract the body of a named method from Java source using brace counting."""
    lines = java_source.splitlines()
    start_idx: int | None = None
    for i, line in enumerate(lines):
        if method_name in line and ("void " in line or "public " in line or "protected " in line):
            look_back = max(0, i - 3)
            for j in range(i, look_back - 1, -1):
                if "@Test" in lines[j]:
                    start_idx = j
                    break
            if start_idx is None:
                start_idx = i
            break

    if start_idx is None:
        return ""

    depth = 0
    body_lines: list[str] = []
    started = False
    for line in lines[start_idx:]:
        body_lines.append(line)
        for ch in line:
            if ch == "{":
                depth += 1
                started = True
            elif ch == "}":
                depth -= 1
        if started and depth == 0:
            break

    return "\n".join(body_lines)


# ---------------------------------------------------------------------------
# Java code extraction
# ---------------------------------------------------------------------------

def extract_java_code(llm_response: str) -> str:
    """Extract Java source from LLM response, stripping markdown fences."""
    match = re.search(r"```java\s*(.*?)```", llm_response, re.DOTALL)
    if match:
        return match.group(1).strip()
    match = re.search(r"```\s*(.*?)```", llm_response, re.DOTALL)
    if match:
        return match.group(1).strip()
    return llm_response.strip()


# ---------------------------------------------------------------------------
# Package / class / method inference
# ---------------------------------------------------------------------------

def infer_package_and_class(context: BugContext) -> tuple[str, str]:
    """Infer Java package from context code snippets. Class name is always LLMGeneratedTest."""
    for snippet in context.code_snippets:
        if "." in snippet.class_name:
            package = snippet.class_name.rsplit(".", 1)[0]
            return package, "LLMGeneratedTest"
    return "", "LLMGeneratedTest"


def infer_method_name_from_response(java_source: str) -> str:
    """Extract first @Test public void <name> from generated Java source."""
    match = re.search(r"@Test\s+(?:public\s+)?void\s+(\w+)", java_source)
    if match:
        return match.group(1)
    return "unknownTestMethod"


# ---------------------------------------------------------------------------
# File I/O
# ---------------------------------------------------------------------------

def write_test_file(
    java_source: str,
    work_dir: str,
    test_src_dir: str,
    class_name: str,
    package_name: str,
) -> Path:
    """Write Java source to work_dir/test_src_dir/package_path/ClassName.java."""
    package_path = package_name.replace(".", "/") if package_name else ""
    dest_dir = Path(work_dir) / test_src_dir
    if package_path:
        dest_dir = dest_dir / package_path
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"{class_name}.java"
    dest.write_text(java_source, encoding="utf-8")
    return dest


def _cleanup_generated_test(
    work_dir: str,
    test_src_dir: str,
    bin_tests_dir: str,
    class_name: str,
    package_name: str,
) -> None:
    package_path = package_name.replace(".", "/") if package_name else ""

    src_dir = Path(work_dir) / test_src_dir
    if package_path:
        src_dir = src_dir / package_path
    java_file = src_dir / f"{class_name}.java"
    if java_file.exists():
        java_file.unlink()

    if bin_tests_dir:
        bin_dir = Path(work_dir) / bin_tests_dir
        if package_path:
            bin_dir = bin_dir / package_path
        if bin_dir.is_dir():
            for cls_file in bin_dir.glob(f"{class_name}*.class"):
                cls_file.unlink()


# ---------------------------------------------------------------------------
# Defects4J compile / test
# ---------------------------------------------------------------------------

def compile_version(d4j: Defects4JClient, work_dir: str) -> tuple[bool, str]:
    """Run defects4j compile. Returns (success, error_message)."""
    try:
        result = d4j.compile(Path(work_dir))
        if result.returncode != 0:
            return False, (result.stderr or result.stdout).strip()
        return True, ""
    except Defects4JError as exc:
        return False, str(exc)


def run_generated_test(
    d4j: Defects4JClient,
    work_dir: str,
    class_name: str,
    method_name: str,
) -> tuple[bool, str, str]:
    """
    Run defects4j test -t ClassName::methodName.

    Returns (test_passed, stdout, stderr).
    test_passed=True means our specific test did NOT appear in failures.
    """
    work_path = Path(work_dir)
    result = d4j.test(work_path, single_test=f"{class_name}::{method_name}")
    failures = d4j.read_failures(work_path, result.stdout)
    our_test_failed = any(
        f.test_class == class_name
        or f.test_name == f"{class_name}::{method_name}"
        or (f.test_class.endswith(class_name) and f.test_method == method_name)
        for f in failures
    )
    return not our_test_failed, result.stdout, result.stderr


# ---------------------------------------------------------------------------
# Ground-truth comparison
# ---------------------------------------------------------------------------

def compare_to_trigger(
    generated_method: str,
    trigger_methods: list[str],
    modified_class: str | None,
    java_source: str,
) -> tuple[bool, bool]:
    """
    Returns (method_name_match, trigger_class_targeted).

    method_name_match: generated method name overlaps any trigger method name.
    trigger_class_targeted: the modified class's simple name appears in the generated test.
    """
    method_name_match = False
    for trigger in trigger_methods:
        trigger_method = trigger.split("::")[-1] if "::" in trigger else trigger
        if (
            generated_method == trigger_method
            or generated_method in trigger_method
            or trigger_method in generated_method
        ):
            method_name_match = True
            break

    trigger_class_targeted = False
    if modified_class:
        simple_name = modified_class.split(".")[-1]
        trigger_class_targeted = simple_name in java_source

    return method_name_match, trigger_class_targeted


# ---------------------------------------------------------------------------
# Single attempt execution (shared by initial run and refine loop)
# ---------------------------------------------------------------------------

def _run_single_attempt(
    java_source: str,
    context_prefix: BugContext,
    d4j: Defects4JClient,
    package_name: str,
    class_name: str,
    method_name: str,
) -> tuple[bool, str | None, bool | None, str, str]:
    """
    Write the test, compile, run on the buggy version, clean up.

    Returns (compilation_success, compilation_error, fails_on_buggy, buggy_stdout, buggy_stderr).
    """
    prefix_work_dir = context_prefix.work_dir
    test_src_dir = context_prefix.exports.get("dir.src.tests", "src/test/java")
    bin_tests_dir = context_prefix.exports.get("dir.bin.tests", "")

    compilation_success = False
    compilation_error: str | None = None
    fails_on_buggy: bool | None = None
    buggy_stdout = buggy_stderr = ""

    try:
        write_test_file(java_source, prefix_work_dir, test_src_dir, class_name, package_name)
        compilation_success, compilation_error = compile_version(d4j, prefix_work_dir)
        if compilation_success:
            test_passed_buggy, buggy_stdout, buggy_stderr = run_generated_test(
                d4j, prefix_work_dir, class_name, method_name
            )
            fails_on_buggy = not test_passed_buggy
        else:
            compilation_error = compilation_error or ""
    finally:
        _cleanup_generated_test(prefix_work_dir, test_src_dir, bin_tests_dir, class_name, package_name)

    return compilation_success, compilation_error, fails_on_buggy, buggy_stdout, buggy_stderr


def _run_postfix_attempt(
    java_source: str,
    context_postfix: BugContext,
    d4j: Defects4JClient,
    package_name: str,
    class_name: str,
    method_name: str,
) -> tuple[bool | None, str, str]:
    """
    Write, compile, and run the test on the fixed version.

    Returns (passes_on_fixed, fixed_stdout, fixed_stderr).
    Passes_on_fixed is None if compilation fails.
    """
    postfix_work_dir = context_postfix.work_dir
    test_src_dir = context_postfix.exports.get("dir.src.tests", "src/test/java")
    bin_tests_dir = context_postfix.exports.get("dir.bin.tests", "")
    passes_on_fixed: bool | None = None
    fixed_stdout = fixed_stderr = ""
    try:
        write_test_file(java_source, postfix_work_dir, test_src_dir, class_name, package_name)
        compiled, _ = compile_version(d4j, postfix_work_dir)
        if compiled:
            test_passed, fixed_stdout, fixed_stderr = run_generated_test(
                d4j, postfix_work_dir, class_name, method_name
            )
            passes_on_fixed = test_passed
    finally:
        _cleanup_generated_test(postfix_work_dir, test_src_dir, bin_tests_dir, class_name, package_name)
    return passes_on_fixed, fixed_stdout, fixed_stderr


# ---------------------------------------------------------------------------
# Self-correction loop
# ---------------------------------------------------------------------------

def _build_refine_feedback(
    result: "TestGenResult",
    reason: str,
    context: BugContext,
) -> str:
    """Build the feedback message for the LLM refinement iteration.

    Oracle integrity: never mentions expected:<X> values, trigger method names,
    or any post-fix information.
    """
    package_name, class_name = infer_package_and_class(context)

    if reason == "compile_failed":
        error_text = (result.compilation_error or "").strip()
        return (
            f"Your test failed to compile. Compiler error:\n"
            f"```\n{error_text}\n```\n\n"
            f"Fix the compilation error. "
            f"Keep package `{package_name}` and class name `{class_name}`.\n"
            "Return ONLY the corrected complete Java source file."
        )

    if reason == "oracle_fail":
        return (
            "Your test correctly FAILS on the buggy version — good! "
            "However, it also FAILS on the fixed version. "
            "A valid regression test must PASS after the bug is fixed.\n\n"
            "This means one of the following:\n"
            "  - Your assertion expects the wrong value for the fixed behaviour, or\n"
            "  - Your test exercises a code path that produces an error in both versions.\n\n"
            "Revise your test so that it:\n"
            "  1. Still FAILS on the buggy version (keep probing the defective behaviour)\n"
            "  2. PASSES on the fixed version (the assertion must match correct post-fix output)\n\n"
            "Check the bug report for clues about what the correct behaviour should be "
            "after the fix is applied.\n\n"
            f"Keep package `{package_name}` and class name `{class_name}`.\n"
            "Return ONLY the revised complete Java source file."
        )

    # reason == "passed_on_buggy"
    return (
        "Your test compiled and ran successfully, but it **passed** on the buggy version "
        "of the code. A valid regression test must **fail** on the buggy version.\n\n"
        "This means one of the following:\n"
        "  - Your assertion matches what the buggy code already produces "
        "(you are testing the bug's symptom as if it were correct behaviour), or\n"
        "  - Your test exercises a code path that the bug does not affect.\n\n"
        "Reconsider which inputs or method calls would expose the specific defect "
        "described in the bug report. Try different concrete argument values, "
        "a different API entry point, or an additional assertion that probes the "
        "incorrect behaviour more precisely.\n\n"
        f"Keep package `{package_name}` and class name `{class_name}`.\n"
        "Return ONLY the revised complete Java source file."
    )


def refine_test_generation(
    initial_result: "TestGenResult",
    context_prefix: BugContext,
    client: LLMClient,
    d4j: Defects4JClient,
    max_iterations: int = 3,
    context_postfix: BugContext | None = None,
) -> "TestGenResult":
    """
    Self-correction loop for test generation.

    Iterates up to max_iterations times to fix three failure modes in priority order:
      1. compile_failed   — test does not compile
      2. passed_on_buggy  — test passes on the buggy version (wrong direction)
      3. oracle_fail      — test fails on both buggy AND fixed versions (requires context_postfix)

    Stops as soon as oracle_match=True (fails buggy AND passes fixed) or iterations exhausted.
    If context_postfix is not provided, stops after achieving fails_on_buggy=True.

    Oracle integrity: feedback never contains expected:<X> values or trigger method names.
    """
    result = initial_result

    # Determine if we're already done
    if context_postfix:
        if result.oracle_match is True:
            return result
    else:
        if result.fails_on_buggy is True:
            return result

    original_messages = build_test_gen_prompt(context_prefix, result.prompt_style)
    package_name, class_name = infer_package_and_class(context_prefix)
    history: list[dict] = list(result.refine_history)

    # Carry forward postfix results from the initial attempt
    passes_on_fixed: bool | None = result.passes_on_fixed
    fixed_stdout: str = result.fixed_stdout
    fixed_stderr: str = result.fixed_stderr

    for iteration in range(1, max_iterations + 1):
        # Stop condition
        if context_postfix:
            if result.oracle_match is True:
                break
        else:
            if result.fails_on_buggy is True:
                break

        # Determine failure mode in priority order
        if not result.compilation_success:
            reason = "compile_failed"
        elif result.fails_on_buggy is not True:
            reason = "passed_on_buggy"
        else:
            reason = "oracle_fail"  # fails buggy but also fails fixed

        feedback = _build_refine_feedback(result, reason, context_prefix)

        messages = original_messages + [
            {"role": "assistant", "content": result.raw_llm_response},
            {"role": "user", "content": feedback},
        ]

        raw_response = client.complete_text(messages)
        java_source = extract_java_code(raw_response)
        method_name = infer_method_name_from_response(java_source) if java_source else "unknownTestMethod"

        compilation_success: bool = False
        compilation_error: str | None = None
        fails_on_buggy: bool | None = None
        buggy_stdout = buggy_stderr = ""
        passes_on_fixed = None
        fixed_stdout = fixed_stderr = ""

        if java_source:
            compilation_success, compilation_error, fails_on_buggy, buggy_stdout, buggy_stderr = (
                _run_single_attempt(java_source, context_prefix, d4j, package_name, class_name, method_name)
            )
            # Evaluate on fixed version if fault detection is achieved and postfix is available
            if fails_on_buggy is True and context_postfix and Path(context_postfix.work_dir).is_dir():
                passes_on_fixed, fixed_stdout, fixed_stderr = _run_postfix_attempt(
                    java_source, context_postfix, d4j, package_name, class_name, method_name
                )

        oracle_match: bool | None = (True if (fails_on_buggy is True and passes_on_fixed is True) else
                                     False if (fails_on_buggy is not None or passes_on_fixed is not None) else None)

        history.append({
            "iteration": iteration,
            "reason": reason,
            "java_source": java_source,
            "compilation_success": compilation_success,
            "fails_on_buggy": fails_on_buggy,
            "passes_on_fixed": passes_on_fixed,
        })

        # Carry all original ground-truth fields; update only the attempt-specific fields
        result = TestGenResult(
            project_id=result.project_id,
            bug_id=result.bug_id,
            prefix_work_dir=result.prefix_work_dir,
            postfix_work_dir=result.postfix_work_dir,
            model=result.model,
            provider=result.provider,
            created_at=result.created_at,
            prompt_style=result.prompt_style,
            generated_class_name=class_name,
            generated_method_name=method_name,
            generated_test_code=java_source,
            raw_llm_response=raw_response,
            compilation_success=compilation_success,
            compilation_error=compilation_error,
            fails_on_buggy=fails_on_buggy,
            passes_on_fixed=passes_on_fixed,
            oracle_match=oracle_match,
            trigger_methods=result.trigger_methods,
            trigger_test_source=result.trigger_test_source,
            method_name_match=result.method_name_match,
            trigger_class_targeted=result.trigger_class_targeted,
            modified_class=result.modified_class,
            buggy_stdout=buggy_stdout,
            buggy_stderr=buggy_stderr,
            fixed_stdout=fixed_stdout,
            fixed_stderr=fixed_stderr,
            notes=result.notes,
            refine_iterations=iteration,
            refine_history=history,
        )

    return result


# ---------------------------------------------------------------------------
# Full pipeline
# ---------------------------------------------------------------------------

def run_test_generation(
    context_prefix: BugContext,
    context_postfix: BugContext | None,
    client: LLMClient,
    d4j: Defects4JClient | None = None,
    prompt_style: str = "full",
) -> TestGenResult:
    """
    Full test-generation pipeline for one bug.

    The LLM only receives prefix (buggy) data — postfix is never in the prompt.
    context_postfix is optional: if None (or its work_dir is missing), the
    "passes on fixed" evaluation is skipped and passes_on_fixed stays None.

    Steps:
    1. Build oracle-clean prompt from prefix context only
    2. LLM call → extract Java source
    3. Extract actual trigger test source from prefix work_dir (ground truth, not sent to LLM)
    4. Write generated test to prefix work_dir → compile → run (must fail)
    5. If postfix provided: write → compile → run (must pass)
    6. Clean up generated files from both work_dirs
    """
    if d4j is None:
        d4j = Defects4JClient()

    notes: list[str] = []

    # -- LLM call (prefix only, oracle-clean prompt) -------------------------
    messages = build_test_gen_prompt(context_prefix, prompt_style)
    raw_response = client.complete_text(messages)
    java_source = extract_java_code(raw_response)

    package_name, class_name = infer_package_and_class(context_prefix)
    method_name = infer_method_name_from_response(java_source) if java_source else "unknownTestMethod"

    # -- Ground truth from Defects4J trigger tests (NEVER sent to LLM) ------
    trigger_raw = context_prefix.exports.get("tests.trigger", "")
    trigger_methods = [t.strip() for t in re.split(r"[,\n]+", trigger_raw) if t.strip()]
    if not trigger_methods:
        trigger_raw_meta = context_prefix.metadata.get("tests", {})
        if isinstance(trigger_raw_meta, dict):
            trigger_raw = trigger_raw_meta.get("trigger", "")
            trigger_methods = [t.strip() for t in re.split(r"[,\n]+", trigger_raw) if t.strip()]

    trigger_test_source = extract_trigger_test_source(context_prefix)

    modified_class: str | None = context_prefix.hidden_oracles.get("classes.modified")
    method_match, class_targeted = compare_to_trigger(
        method_name, trigger_methods, modified_class, java_source
    )

    prefix_work_dir = context_prefix.work_dir
    postfix_work_dir = context_postfix.work_dir if context_postfix else ""
    test_src_dir = context_prefix.exports.get("dir.src.tests", "src/test/java")
    bin_tests_dir = context_prefix.exports.get("dir.bin.tests", "")

    compilation_success = False
    compilation_error: str | None = None
    fails_on_buggy: bool | None = None
    passes_on_fixed: bool | None = None
    oracle_match: bool | None = None
    buggy_stdout = buggy_stderr = fixed_stdout = fixed_stderr = ""

    if not java_source:
        notes.append("LLM returned empty or unparseable Java source.")
        return _make_result(
            context_prefix, postfix_work_dir, client, prompt_style,
            class_name, method_name, java_source, raw_response,
            compilation_success, compilation_error,
            fails_on_buggy, passes_on_fixed, oracle_match,
            trigger_methods, trigger_test_source, method_match, class_targeted, modified_class,
            buggy_stdout, buggy_stderr, fixed_stdout, fixed_stderr, notes,
        )

    # -- Prefix: write → compile → test (buggy) ------------------------------
    try:
        write_test_file(java_source, prefix_work_dir, test_src_dir, class_name, package_name)
    except Exception as exc:
        notes.append(f"Failed to write test file to prefix work_dir: {exc}")
        return _make_result(
            context_prefix, postfix_work_dir, client, prompt_style,
            class_name, method_name, java_source, raw_response,
            compilation_success, compilation_error,
            fails_on_buggy, passes_on_fixed, oracle_match,
            trigger_methods, trigger_test_source, method_match, class_targeted, modified_class,
            buggy_stdout, buggy_stderr, fixed_stdout, fixed_stderr, notes,
        )

    try:
        compilation_success, compilation_error = compile_version(d4j, prefix_work_dir)
        if compilation_success:
            test_passed_buggy, buggy_stdout, buggy_stderr = run_generated_test(
                d4j, prefix_work_dir, class_name, method_name
            )
            fails_on_buggy = not test_passed_buggy
        else:
            notes.append(f"Prefix compilation failed: {compilation_error}")
    finally:
        _cleanup_generated_test(prefix_work_dir, test_src_dir, bin_tests_dir, class_name, package_name)

    if not compilation_success:
        return _make_result(
            context_prefix, postfix_work_dir, client, prompt_style,
            class_name, method_name, java_source, raw_response,
            compilation_success, compilation_error,
            fails_on_buggy, passes_on_fixed, oracle_match,
            trigger_methods, trigger_test_source, method_match, class_targeted, modified_class,
            buggy_stdout, buggy_stderr, fixed_stdout, fixed_stderr, notes,
        )

    # -- Postfix: write → compile → test (fixed) — optional -----------------
    if context_postfix and postfix_work_dir and Path(postfix_work_dir).is_dir():
        postfix_test_src_dir = context_postfix.exports.get("dir.src.tests", test_src_dir)
        postfix_bin_tests_dir = context_postfix.exports.get("dir.bin.tests", "")
        try:
            write_test_file(java_source, postfix_work_dir, postfix_test_src_dir, class_name, package_name)
            postfix_compiled, postfix_compile_error = compile_version(d4j, postfix_work_dir)
            if postfix_compiled:
                test_passed_fixed, fixed_stdout, fixed_stderr = run_generated_test(
                    d4j, postfix_work_dir, class_name, method_name
                )
                passes_on_fixed = test_passed_fixed
            else:
                notes.append(f"Postfix compilation failed: {postfix_compile_error}")
        except Exception as exc:
            notes.append(f"Failed during postfix execution: {exc}")
        finally:
            _cleanup_generated_test(
                postfix_work_dir, postfix_test_src_dir, postfix_bin_tests_dir, class_name, package_name
            )
    elif context_postfix:
        notes.append(f"Postfix work_dir not available ({postfix_work_dir}), skipping fixed-version evaluation.")
    else:
        notes.append("No postfix context provided — fixed-version evaluation skipped.")

    if fails_on_buggy is not None and passes_on_fixed is not None:
        oracle_match = fails_on_buggy and passes_on_fixed

    return _make_result(
        context_prefix, postfix_work_dir, client, prompt_style,
        class_name, method_name, java_source, raw_response,
        compilation_success, compilation_error,
        fails_on_buggy, passes_on_fixed, oracle_match,
        trigger_methods, trigger_test_source, method_match, class_targeted, modified_class,
        buggy_stdout, buggy_stderr, fixed_stdout, fixed_stderr, notes,
    )


def _make_result(
    context_prefix: BugContext,
    postfix_work_dir: str,
    client: LLMClient,
    prompt_style: str,
    class_name: str,
    method_name: str,
    java_source: str,
    raw_response: str,
    compilation_success: bool,
    compilation_error: str | None,
    fails_on_buggy: bool | None,
    passes_on_fixed: bool | None,
    oracle_match: bool | None,
    trigger_methods: list[str],
    trigger_test_source: str,
    method_name_match: bool,
    trigger_class_targeted: bool,
    modified_class: str | None,
    buggy_stdout: str,
    buggy_stderr: str,
    fixed_stdout: str,
    fixed_stderr: str,
    notes: list[str],
) -> TestGenResult:
    return TestGenResult(
        project_id=context_prefix.project_id,
        bug_id=context_prefix.bug_id,
        prefix_work_dir=context_prefix.work_dir,
        postfix_work_dir=postfix_work_dir,
        model=client.settings.model,
        provider=client.settings.provider,
        created_at=utc_now_iso(),
        prompt_style=prompt_style,
        generated_class_name=class_name,
        generated_method_name=method_name,
        generated_test_code=java_source,
        raw_llm_response=raw_response,
        compilation_success=compilation_success,
        compilation_error=compilation_error,
        fails_on_buggy=fails_on_buggy,
        passes_on_fixed=passes_on_fixed,
        oracle_match=oracle_match,
        trigger_methods=trigger_methods,
        trigger_test_source=trigger_test_source,
        method_name_match=method_name_match,
        trigger_class_targeted=trigger_class_targeted,
        modified_class=modified_class,
        buggy_stdout=buggy_stdout,
        buggy_stderr=buggy_stderr,
        fixed_stdout=fixed_stdout,
        fixed_stderr=fixed_stderr,
        notes=notes,
    )
