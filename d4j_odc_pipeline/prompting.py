from __future__ import annotations

import json

from .models import BugContext
from .odc import ODC_TYPE_NAMES, taxonomy_markdown


def build_messages(context: BugContext, prompt_style: str) -> list[dict[str, str]]:
    system_prompt = _build_system_prompt(prompt_style)
    user_prompt = _build_user_prompt(context, prompt_style)
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def _build_system_prompt(prompt_style: str) -> str:
    base = [
        "You are an expert software defect analyst specializing in Orthogonal Defect Classification (ODC).",
        "Your job is to classify one bug into exactly one ODC defect type using ONLY the provided pre-fix evidence.",
        "",
        "CRITICAL RULES:",
        "- Do NOT default to 'Function'. Function means the capability was NEVER IMPLEMENTED.",
        "- Most Defects4J bugs are in EXISTING code that produces wrong results — these are typically Checking, Algorithm, or Assignment.",
        "- Read the code snippets carefully. The type of fix needed determines the ODC type.",
        "- Do not use benchmark familiarity, project reputation, or hidden fix knowledge.",
        "",
        taxonomy_markdown(),
        "",
        "Return only valid JSON matching this schema:",
        _json_contract(),
    ]
    if prompt_style == "scientific":
        base.extend(
            [
                "",
                _scientific_debugging_instructions(),
                "",
                "## Classification Decision Process",
                "",
                "Before classifying, you MUST answer these diagnostic questions in your reasoning:",
                "",
                "1. **Is a condition/guard/validation missing or wrong?**",
                "   → Look for: missing null checks, wrong if-conditions, missing bounds checks, incorrect exception handling.",
                "   → If YES → strongly consider **Checking**.",
                "",
                "2. **Is a specific value, constant, or initialization wrong?**",
                "   → Look for: wrong default values, wrong constants, wrong variable used in assignment.",
                "   → If YES and the fix is a single value change → strongly consider **Assignment**.",
                "",
                "3. **Is the computational logic or procedure itself wrong?**",
                "   → Look for: wrong formula, wrong loop logic, wrong sort order, wrong data structure operation.",
                "   → If YES → strongly consider **Algorithm**.",
                "",
                "4. **Is the problem at a component boundary or API interaction?**",
                "   → Look for: wrong parameter order, type mismatch between caller/callee, contract violation.",
                "   → If YES → strongly consider **Interface**.",
                "",
                "5. **Does the problem depend on execution order or timing?**",
                "   → Look for: race conditions, lifecycle ordering, serialization order.",
                "   → If YES → strongly consider **Timing/Serialization**.",
                "",
                "6. **Is functionality completely missing (never implemented)?**",
                "   → Look for: no existing code handles this case at all; requires adding new methods/classes.",
                "   → If YES → consider **Function**.",
                "",
                "7. **Is the problem in build/packaging/configuration?**",
                "   → Look for: build script issues, dependency problems, classpath errors.",
                "   → If YES → consider **Build/Package/Merge**.",
                "",
                "Work through these questions using the evidence provided, then choose the BEST matching type.",
            ]
        )
    # Add few-shot examples for both styles
    base.extend(["", _few_shot_examples()])
    return "\n".join(base)


def _scientific_debugging_instructions() -> str:
    return """## Scientific Debugging Protocol

Follow this structured reasoning process:

**Step 1 — OBSERVE**: Examine the failure symptoms carefully.
- What does the error message say?
- What does the stack trace reveal about WHERE the failure occurs?
- What does the test name tell you about WHAT is being tested?

**Step 2 — HYPOTHESIZE**: Form a specific root-cause hypothesis.
- Do NOT just say "the feature doesn't work." Be specific about the MECHANISM.
- Is it a wrong condition? A wrong value? A wrong computation step? A missing check?

**Step 3 — PREDICT**: What would we expect to see in the code if your hypothesis is correct?
- If it's a Checking bug: we'd see a missing/wrong if-condition or guard.
- If it's an Algorithm bug: we'd see wrong iteration, formula, or procedure.
- If it's an Assignment bug: we'd see a wrong value or initialization.

**Step 4 — EXAMINE EVIDENCE**: Look at the code snippets provided.
- Do the code snippets confirm or refute your hypothesis?
- What specific lines or constructs in the code support your classification?

**Step 5 — CONCLUDE**: Choose the ODC type that best matches the ROOT CAUSE mechanism."""


def _few_shot_examples() -> str:
    return """## Classification Examples

These examples show how to distinguish between ODC types using pre-fix evidence:

### Example 1: Checking
**Symptom**: NullPointerException in `StringUtils.isEmpty()` when called with a null locale parameter.
**Code snippet**: `return input.length() == 0;` (no null check before `.length()`)
**Classification**: **Checking** — The logic is correct for non-null inputs, but a null guard is MISSING. The fix is adding `if (input == null) return true;`.
**NOT Function**: The method exists and works — it just lacks a validation check.
**NOT Algorithm**: The computation (checking length) is correct — only the guard is missing.

### Example 2: Assignment
**Symptom**: `assertEquals(expected, actual)` fails because a method returns -1 instead of 0.
**Code snippet**: `int result = -1;` (wrong initial value; should be `0`)
**Classification**: **Assignment** — The control flow and algorithm are correct, but a single value is initialized wrong. The fix is changing `-1` to `0`.
**NOT Checking**: No condition or guard is missing — the value itself is wrong.
**NOT Algorithm**: The procedure is correct — only the assigned constant is wrong.

### Example 3: Algorithm
**Symptom**: `testMultiply` fails with wrong numerical result.
**Code snippet**: `total += values[i] * weights[i+1];` (should be `weights[i]`, not `weights[i+1]`)
**Classification**: **Algorithm** — The computation procedure uses the wrong index in its formula. The fix changes the array indexing logic in the computation.
**NOT Assignment**: The issue isn't a wrong constant — it's wrong indexing logic in the computation.
**NOT Checking**: No guard or condition is missing — the computation steps are wrong.

### Example 4: Interface
**Symptom**: `testSerialize` fails because the deserialized object has swapped fields.
**Code snippet**: `writer.write(name, value);` but reader does `reader.read(value, name);` — parameter order mismatch.
**Classification**: **Interface** — Two components disagree on the parameter contract at their boundary.
**NOT Algorithm**: Each component's logic is correct internally — the mismatch is at the boundary.

### Example 5: Function
**Symptom**: `testHandleSpecialCharacters` fails with UnsupportedOperationException.
**Code snippet**: The method has `throw new UnsupportedOperationException("not yet implemented");`
**Classification**: **Function** — The capability was never implemented at all. The fix requires writing entirely new logic.
**NOT Algorithm**: There's no wrong computation — there's NO computation. The feature is absent."""


def _build_user_prompt(context: BugContext, prompt_style: str) -> str:
    payload = _context_payload(context, prompt_style)
    rules = [
        "Classify this bug into one ODC defect type.",
        "",
        "IMPORTANT ANALYSIS RULES:",
        "- Use ONLY the evidence in this prompt.",
        "- Examine code snippets line-by-line to determine the root cause mechanism.",
        "- Consider: Is the root cause a missing CHECK, a wrong VALUE, a wrong COMPUTATION, a BOUNDARY mismatch, or truly MISSING functionality?",
        "- If code snippets show existing logic producing wrong results, this is NOT 'Function'.",
        "- If evidence is incomplete, lower confidence and set needs_human_review=true.",
        "- The output odc_type must be one of: " + ", ".join(ODC_TYPE_NAMES),
    ]
    return "\n".join(rules) + "\n\nEvidence:\n" + json.dumps(payload, indent=2)


def _context_payload(context: BugContext, prompt_style: str) -> dict:
    # Filter metadata — exclude hidden oracles
    filtered_metadata = {key: value for key, value in context.metadata.items() if key != "classes.modified"}

    payload: dict = {
        "project_id": context.project_id,
        "bug_id": context.bug_id,
        "version_id": context.version_id,
        "metadata": filtered_metadata,
        "failing_tests": [],
        "suspicious_frames": [],
        "production_code_snippets": [],
        "test_code_snippets": [],
        "coverage_summary": [],
    }

    # ── Bug info from d4j info command ────────────────────────────────
    if context.bug_info:
        payload["bug_info"] = context.bug_info

    # ── Bug report content from JIRA/GitHub ───────────────────────────
    if context.bug_report_content:
        payload["bug_report_description"] = context.bug_report_content

    # ── Failing tests ─────────────────────────────────────────────────
    for failure in context.failures[:5]:
        payload["failing_tests"].append(
            {
                "test_name": failure.test_name,
                "headline": failure.headline,
                "stack_trace_excerpt": failure.stack_trace[:15],
            }
        )

    # ── Suspicious frames ─────────────────────────────────────────────
    for frame in context.suspicious_frames[:10]:
        payload["suspicious_frames"].append(
            {
                "class_name": frame.class_name,
                "method_name": frame.method_name,
                "file_name": frame.file_name,
                "line_number": frame.line_number,
            }
        )

    # ── Separate production vs test code snippets ─────────────────────
    snippet_limit = 8 if prompt_style == "scientific" else 5
    prod_count = 0
    test_count = 0
    for snippet in context.code_snippets:
        is_test = snippet.reason.startswith("Test source:")
        if is_test and test_count < 3:
            payload["test_code_snippets"].append(
                {
                    "class_name": snippet.class_name,
                    "reason": snippet.reason,
                    "file_path": snippet.file_path,
                    "start_line": snippet.start_line,
                    "end_line": snippet.end_line,
                    "focus_line": snippet.focus_line,
                    "content": snippet.content,
                }
            )
            test_count += 1
        elif not is_test and prod_count < snippet_limit:
            payload["production_code_snippets"].append(
                {
                    "class_name": snippet.class_name,
                    "reason": snippet.reason,
                    "file_path": snippet.file_path,
                    "start_line": snippet.start_line,
                    "end_line": snippet.end_line,
                    "focus_line": snippet.focus_line,
                    "content": snippet.content,
                }
            )
            prod_count += 1

    # ── Coverage ──────────────────────────────────────────────────────
    for coverage in context.coverage[:6]:
        payload["coverage_summary"].append(
            {
                "class_name": coverage.class_name,
                "line_rate": coverage.line_rate,
                "branch_rate": coverage.branch_rate,
                "top_covered_lines": [
                    {"line_number": line.line_number, "hits": line.hits}
                    for line in coverage.covered_lines[:10]
                ],
            }
        )

    # ── Notes ─────────────────────────────────────────────────────────
    if context.notes:
        payload["notes"] = list(context.notes)

    return payload


def _json_contract() -> str:
    return (
        "{"
        '"odc_type": "one of the allowed ODC types", '
        '"coarse_group": "Control and Data or Structural", '
        '"confidence": "number between 0 and 1", '
        '"needs_human_review": "boolean", '
        '"observation_summary": "short paragraph describing failure symptoms", '
        '"hypothesis": "short paragraph with specific root-cause mechanism", '
        '"prediction": "short paragraph predicting what the code would look like", '
        '"experiment_rationale": "short paragraph explaining how evidence confirms or weakens the hypothesis", '
        '"reasoning_summary": "short paragraph explaining WHY this ODC type was chosen over alternatives", '
        '"evidence_used": ["specific evidence items from the input"], '
        '"evidence_gaps": ["missing evidence or ambiguity"], '
        '"alternative_types": [{"type": "ODC type", "why_not_primary": "specific reason based on evidence"}]'
        "}"
    )
