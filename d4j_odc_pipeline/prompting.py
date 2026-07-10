from __future__ import annotations

import json
import re

from .models import BugContext
from .odc import (
    STRATEGY_FEW,
    STRATEGY_ZERO,
    TAXONOMY_CLOSED,
    TAXONOMY_FREE,
    TAXONOMY_OPEN,
    allowed_impact_names,
    allowed_type_names,
    impact_markdown,
    taxonomy_markdown,
    validate_condition,
)


def build_messages(
    context: BugContext,
    taxonomy: str,
    strategy: str,
) -> list[dict[str, str]]:
    """Build the single-call LLM messages for one classification condition.

    Only the STATIC strategies are built here:
    - zero (taxonomy-free, no examples — the unstructured baseline)
    - few  (taxonomy + diagnostic tree + worked examples — the strong static prompt)
    The 'scientific' strategy (the enforced loop) builds its own conversation
    in agent.py and never calls this. See docs/condition_model.md.
    """
    validate_condition(taxonomy, strategy)
    if strategy not in (STRATEGY_ZERO, STRATEGY_FEW):
        raise ValueError(
            f"build_messages only handles static strategies (zero|few); got {strategy!r} — "
            "the scientific strategy is driven by agent.run_agentic_classification."
        )
    has_fix_diff = bool(context.fix_diff)
    system_prompt = _build_system_prompt(
        taxonomy=taxonomy, strategy=strategy, has_fix_diff=has_fix_diff
    )
    user_prompt = _build_user_prompt(context, taxonomy=taxonomy, strategy=strategy)
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def _build_system_prompt(
    *,
    taxonomy: str,
    strategy: str,
    has_fix_diff: bool = False,
) -> str:
    # zero: no ODC types, no structured labels, no anti-bias rules.
    # The LLM answers in its own words (simplified JSON contract).
    if strategy == STRATEGY_ZERO:
        return _build_zero_system_prompt(has_fix_diff=has_fix_diff)
    taxonomy_mode = taxonomy

    base = [
        "You are an expert software defect analyst specializing in Orthogonal Defect Classification (ODC).",
    ]

    if has_fix_diff:
        base.extend([
            "You are classifying a bug using BOTH pre-fix evidence AND the actual buggy-to-fixed diff.",
            "The diff shows exactly what was changed to fix the bug. Use it to determine the nature of the fix:",
            "  - If the diff ADDS a missing null/bounds check → Checking",
            "  - If the diff CHANGES a value, constant, or initialization → Assignment/Initialization",
            "  - If the diff REWRITES a computation or local procedure → Algorithm/Method",
            "  - If the diff CHANGES method signatures or API contracts → Interface/O-O Messages",
            "  - If the diff ADDS synchronization or reorders operations → Timing/Serialization",
            "  - If the diff FIXES associations among procedures/data structures/objects → Relationship",
            "  - If the diff REQUIRES a design-level capability correction → Function/Class/Object",
            "",
            "IMPORTANT: The diff is the GROUND TRUTH of what was fixed. Your classification should be",
            "consistent with the nature of the change shown in the diff.",
        ])
    else:
        base.extend([
            "Your job is to classify one bug into exactly one ODC defect type using ONLY the provided pre-fix evidence.",
        ])

    base.extend([
        "",
        "CRITICAL RULES:",
        "- Do NOT default to 'Function/Class/Object'. This type implies a design-level capability issue.",
        "- Choose the type whose root-cause mechanism the evidence best supports; 'Function/Class/Object' requires evidence of a design-level capability gap, not merely wrong behaviour in existing code.",
        "- Read the code snippets carefully. The type of fix needed determines the ODC type.",
        "- Do not use benchmark familiarity, project reputation, or hidden fix knowledge.",
        "",
        taxonomy_markdown(taxonomy_mode),
        "",
        impact_markdown(),
        "",
        "Return only valid JSON matching this schema:",
        _json_contract(taxonomy_mode),
    ])
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
            "   → If YES and the fix is a value/initialization correction → strongly consider **Assignment/Initialization**.",
            "",
            "3. **Is the computational logic or procedure itself wrong?**",
            "   → Look for: wrong formula, wrong loop logic, wrong sort order, wrong data structure operation.",
            "   → If YES → strongly consider **Algorithm/Method**.",
            "",
            "4. **Is the problem at a component boundary or API interaction?**",
            "   → Look for: wrong parameter order, type mismatch between caller/callee, contract violation.",
            "   → If YES → strongly consider **Interface/O-O Messages**.",
            "",
            "5. **Does the problem depend on execution order or timing?**",
            "   → Look for: race conditions, lifecycle ordering, serialization order.",
            "   → If YES → strongly consider **Timing/Serialization**.",
            "",
            "6. **Is the issue centered on associations among procedures/data structures/objects?**",
            "   → Look for: broken assumptions between related entities that must stay aligned.",
            "   → If YES → consider **Relationship**.",
            "",
            "7. **Does the defect require a formal design-level capability correction?**",
            "   → Look for: significant capability/class/object/interface structure correction.",
            "   → If YES → consider **Function/Class/Object**.",
            "",
            "Work through these questions using the evidence provided, then choose the BEST matching type.",
        ]
    )
    # Worked classification examples — the "shots" that make this the few-shot strategy.
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
- If it's an Algorithm/Method bug: we'd see wrong iteration, formula, or procedure.
- If it's an Assignment/Initialization bug: we'd see a wrong value or initialization.

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
**NOT Function/Class/Object**: The method exists and works — it just lacks a validation check.
**NOT Algorithm/Method**: The computation (checking length) is correct — only the guard is missing.

### Example 2: Assignment/Initialization
**Symptom**: `assertEquals(expected, actual)` fails because a method returns -1 instead of 0.
**Code snippet**: `int result = -1;` (wrong initial value; should be `0`)
**Classification**: **Assignment/Initialization** — The control flow and algorithm are correct, but a single value is initialized wrong. The fix is changing `-1` to `0`.
**NOT Checking**: No condition or guard is missing — the value itself is wrong.
**NOT Algorithm/Method**: The procedure is correct — only the assigned constant is wrong.

### Example 3: Algorithm/Method
**Symptom**: `testMultiply` fails with wrong numerical result.
**Code snippet**: `total += values[i] * weights[i+1];` (should be `weights[i]`, not `weights[i+1]`)
**Classification**: **Algorithm/Method** — The computation procedure uses the wrong index in its formula. The fix changes the array indexing logic in the computation.
**NOT Assignment/Initialization**: The issue isn't a wrong constant — it's wrong indexing logic in the computation.
**NOT Checking**: No guard or condition is missing — the computation steps are wrong.

### Example 4: Interface/O-O Messages
**Symptom**: `testSerialize` fails because the deserialized object has swapped fields.
**Code snippet**: `writer.write(name, value);` but reader does `reader.read(value, name);` — parameter order mismatch.
**Classification**: **Interface/O-O Messages** — Two components disagree on the parameter contract at their boundary.
**NOT Algorithm/Method**: Each component's logic is correct internally — the mismatch is at the boundary.

### Example 5: Function/Class/Object
**Symptom**: `testHandleSpecialCharacters` fails with UnsupportedOperationException.
**Code snippet**: The method has `throw new UnsupportedOperationException("not yet implemented");`
**Classification**: **Function/Class/Object** — The capability was never implemented at all. The fix requires writing new design-level behavior.
**NOT Algorithm/Method**: There's no wrong computation — there is no computation for this capability."""


def _build_user_prompt(
    context: BugContext,
    *,
    taxonomy: str,
    strategy: str,
) -> str:
    payload = _context_payload(context)
    evidence_mode = "post-fix (with buggy->fixed diff)" if context.fix_diff else "pre-fix only"
    taxonomy_mode = taxonomy

    # zero-shot: no ODC references in user prompt either.
    if strategy == STRATEGY_ZERO:
        rules = [
            "Classify this bug based on the evidence below.",
            f"Evidence mode: {evidence_mode}",
            "",
            "ANALYSIS RULES:",
            "- Use ONLY the evidence provided.",
            "- Examine code snippets carefully to determine the root cause.",
            "- Focus on WHAT is wrong in the code, not just the symptom.",
            "- Be specific and technical in your defect type label.",
        ]
        if context.fix_diff:
            rules.append("- Examine the fix diff to see exactly what was changed.")
        return "\n".join(rules) + "\n\nEvidence:\n" + json.dumps(payload, indent=2)

    rules = [
        "Classify this bug into one ODC defect type.",
        f"Evidence mode: {evidence_mode}",
        "",
        "IMPORTANT ANALYSIS RULES:",
        "- Use ONLY the evidence in this prompt.",
        "- Examine code snippets line-by-line to determine the root cause mechanism.",
        "- Consider: Is the root cause a missing CHECK, a wrong VALUE, a wrong COMPUTATION, a BOUNDARY mismatch, or truly MISSING functionality?",
        "- If code snippets show existing logic producing wrong results, this is usually NOT 'Function/Class/Object'.",
        "- If evidence is incomplete, lower confidence and set needs_human_review=true.",
        "- The output odc_type must be one of: " + ", ".join(allowed_type_names(taxonomy_mode)),
        "- Also set `impact` (ODC opener attribute) per the Impact section of the system prompt: "
        "judged from the bug report and failure behaviour, one of "
        + ", ".join(allowed_impact_names()) + ".",
    ]
    if taxonomy_mode == TAXONOMY_OPEN:
        rules.append(
            "- 'Other' is a LAST RESORT: only when the root-cause mechanism fits none of the 7 ODC "
            "types. Uncertainty or incomplete evidence is NOT a reason to choose Other. If you choose "
            "Other, you MUST fill other_justification, nearest_type, and other_confidence."
        )
    if context.fix_diff:
        rules.append("- CAREFULLY examine the fix_diff_oracle to see exactly what was changed. The nature of the change determines the ODC type.")
    return "\n".join(rules) + "\n\nEvidence:\n" + json.dumps(payload, indent=2)


# ── Pre-fix payload sanitization ──────────────────────────────────────────
# The pre-fix arm must contain NO fix-derived information (see
# docs/odc_alignment_audit.md §7). Two channels are sanitized at payload-build
# time — context.json artifacts are never modified:
#   - bug_info: raw `defects4j info` output carries "List of modified sources"
#     (the classes changed by the FIX commit — the same oracle hidden as
#     hidden_oracles["classes.modified"]) and the fixed-revision id/date.
#   - bug_report_content: tracker pages/API responses carry post-fix material
#     (comments like "Fixed in …", Status/Resolution fields, close transitions).
# Post-fix payloads (context.fix_diff set) keep both untouched: that arm
# legitimately knows the fix.

_BUG_INFO_FIX_SECTIONS = (
    "revision id (fixed version)",
    "revision date (fixed version)",
    "list of modified sources",
)

# Comment-thread markers for flattened tracker pages (SourceForge, archives).
# Truncating at the earliest marker keeps the original report body, which
# always precedes the comment thread.
# NOTE: "If you would like to refer to this comment" / "Logged In: YES" are
# boilerplate APPENDED AFTER each individual comment, not before the thread —
# truncating there still keeps the first comment's own text intact (which is
# exactly where a "Good spot, I've committed the fix" disclosure typically
# lives). "Discussion" is SourceForge's section header preceding the FIRST
# comment, so it must be tried first; the others remain as a fallback for
# pages where "Discussion" doesn't appear. Verified against the corpus:
# 23/832 reports contain "Discussion", 100% as this section-header pattern
# (never inside legitimate description prose).
_REPORT_COMMENT_MARKERS = (
    "\nComments:",                                  # our own JIRA/GitHub API format
    "Discussion",                                    # SourceForge section header (precedes ALL comments)
    "If you would like to refer to this comment",   # SourceForge per-comment boilerplate (fallback)
    "Logged In: YES",                               # SourceForge comment header (fallback)
    "Log in to post a comment",                     # SourceForge page footer (fallback)
)

# Google Code-style trackers (e.g. Closure) store the report as a raw JSON
# object: {"status": "...", "comments": [{"id":0,...="original report"},
# {"id":1,...="follow-up discussion, routinely reveals the fix"}, ...]}.
# The first comment IS the original report; truncate at the second comment
# object's start regardless of its "id" value (ids are not guaranteed to
# start at a specific number).
_JSON_SECOND_COMMENT_RE = re.compile(r'\{"id":\d+,\s*"commenterId"')

# Meta segments that reveal post-open state on API-format report meta lines
# (e.g. "Type: Bug | Priority: Major | Status: Resolved | Resolution: Fixed").
_REPORT_META_KEYS = ("Type", "State", "Priority", "Status", "Resolution", "Labels")
_REPORT_META_DROP = ("State", "Status", "Resolution")

# Inline status/resolution tokens on flattened generic-HTML/JSON tracker pages
# (SourceForge, Google Code), which are neither a clean " | "-delimited meta
# line NOR past the comment-thread truncation point — a ticket header like
# "#868 ... Status: closed-fixed Owner: ..." precedes the description itself,
# and Google Code JSON has an unquoted-colon '"status":"Fixed"' top-level key.
# Also catches transition-log phrasing ("status : open --> closed-fixed").
# Trade-off: a rare false positive eating 1-2 incidental words beats the
# alternative of a resolved-ticket status token surviving sanitization.
_INLINE_STATUS_RE = re.compile(
    r'\bstatus"?\s*:\s*"?[\w-]+"?(?:\s*-+>\s*"?[\w-]+"?)?', re.IGNORECASE
)
_INLINE_RESOLUTION_RE = re.compile(
    r'\bresolution"?\s*:\s*"?[\w-]+"?(?:\s*-+>\s*"?[\w-]+"?)?', re.IGNORECASE
)


def _is_separator_line(line: str) -> bool:
    stripped = line.strip()
    return len(stripped) >= 10 and set(stripped) == {"-"}


def sanitize_bug_info(text: str) -> str:
    """Strip fix-derived sections from raw `defects4j info` output.

    Drops the "List of modified sources" and "Revision ID/date (fixed
    version)" sections wholesale; everything else (project summary, bug
    report id/url, triggering tests) is legitimately pre-fix and kept."""
    if not text:
        return text
    out: list[str] = []
    skipping = False
    for line in text.splitlines():
        if skipping:
            if _is_separator_line(line):
                skipping = False
                out.append(line)  # keep one delimiter between surviving sections
            continue
        header = line.strip().lower().rstrip(":")
        if header in _BUG_INFO_FIX_SECTIONS:
            # Drop the delimiter we just emitted for this section, then skip
            # until the section's closing delimiter.
            if out and _is_separator_line(out[-1]):
                out.pop()
            skipping = True
            continue
        out.append(line)
    return "\n".join(out)


def sanitize_bug_report(text: str) -> str:
    """Strip post-fix material from bug report text.

    Keeps the report as filed (title, metadata, description); removes the
    comment thread (which post-dates the report and frequently discusses the
    fix), Status/Resolution/State segments from API meta lines, and inline
    status/resolution tokens on flattened generic-HTML tracker pages."""
    if not text:
        return text
    # 1. Truncate at the earliest comment-thread marker.
    cut = len(text)
    for marker in _REPORT_COMMENT_MARKERS:
        idx = text.find(marker)
        if idx != -1:
            cut = min(cut, idx)
    # 1b. Google Code-style JSON comments[] array: keep only the first
    # (original-report) comment object.
    json_comments = list(_JSON_SECOND_COMMENT_RE.finditer(text))
    if len(json_comments) >= 2:
        cut = min(cut, json_comments[1].start())
    text = text[:cut].rstrip()
    # 2. Drop post-open segments from meta lines. Only lines whose every
    #    " | "-separated segment is a known meta key are rewritten, so
    #    description text containing pipes is never touched.
    lines = text.splitlines()
    meta_re = re.compile(r"^(%s): " % "|".join(_REPORT_META_KEYS))
    for i, line in enumerate(lines):
        segments = line.split(" | ")
        if len(segments) > 1 and all(meta_re.match(seg.strip()) for seg in segments):
            kept = [
                seg for seg in segments
                if not seg.strip().startswith(tuple(f"{key}: " for key in _REPORT_META_DROP))
            ]
            lines[i] = " | ".join(kept)
    text = "\n".join(lines).strip()
    # 3. Sweep any remaining inline status/resolution tokens — covers ticket
    #    headers on flattened generic-HTML pages that precede the truncation
    #    point (step 1 only removes the comment-thread TAIL).
    text = _INLINE_STATUS_RE.sub("", text)
    text = _INLINE_RESOLUTION_RE.sub("", text)
    return _collapse_line_whitespace(text)


def _collapse_line_whitespace(text: str) -> str:
    """Collapse runs of spaces left by token removal, without merging lines."""
    return "\n".join(" ".join(line.split()) for line in text.split("\n")).strip()


def _context_payload(context: BugContext) -> dict:
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

    # ── Bug info / bug report (sanitized in the pre-fix arm only) ─────
    prefix_arm = not context.fix_diff
    bug_info = sanitize_bug_info(context.bug_info) if prefix_arm else context.bug_info
    if bug_info:
        payload["bug_info"] = bug_info

    bug_report = (
        sanitize_bug_report(context.bug_report_content) if prefix_arm else context.bug_report_content
    )
    if bug_report:
        payload["bug_report_description"] = bug_report

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

    # Both styles get the same evidence budget to avoid confounds in RQ2.2.
    # The only difference between scientific and direct is the system prompt.
    snippet_limit = 8
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
    # ── Fix diff (post-fix oracle, optional) ────────────────────────────
    if context.fix_diff:
        payload["fix_diff_oracle"] = {
            "note": "This is POST-FIX oracle information (the actual buggy→fixed diff). "
                    "Use it to confirm your classification, but remember: in a real scenario "
                    "this information would NOT be available before the fix.",
            "unified_diff": context.fix_diff,
        }

    # ── Notes ─────────────────────────────────────────────────────────
    if context.notes:
        payload["notes"] = list(context.notes)

    # NOTE: the old odc_opener_hints/odc_closer_hints keyword heuristics were
    # removed (docs/odc_alignment_audit.md §4.4): they anchored the LLM's
    # opener judgments, used unsound age/qualifier rules, and leaked ODC
    # vocabulary into the zero-free baseline payload.

    return payload


def _json_contract(taxonomy_mode: str = TAXONOMY_CLOSED) -> str:
    other_fields = ""
    if taxonomy_mode == TAXONOMY_OPEN:
        other_fields = (
            '"other_justification": "REQUIRED if odc_type is Other: why each of the 7 ODC types fails, citing evidence (else omit)", '
            '"nearest_type": "REQUIRED if odc_type is Other: the closest of the 7 ODC types (else omit)", '
            '"other_confidence": "REQUIRED if odc_type is Other: number 0-1, confidence that this is a true taxonomy gap (else omit)", '
        )
    return (
        "{"
        '"odc_type": "one of the allowed ODC types", '
        + other_fields +
        '"family": "Control and Data Flow or Structural", '
        '"impact": "ODC opener Impact — exactly one of: ' + ", ".join(allowed_impact_names()) + '", '
        '"target": "Design/Code (optional; closer attribute)", '
        '"qualifier": "Missing or Incorrect or Extraneous (optional; closer attribute, determinable from the fix diff)", '
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


def _build_zero_system_prompt(*, has_fix_diff: bool = False) -> str:
    """Build the zero-shot system prompt (free taxonomy, no worked examples).

    This prompt intentionally excludes ALL ODC concepts:
    - No ODC type names or descriptions
    - No taxonomy guidance or family groupings
    - No anti-bias rules referencing ODC types
    - No JSON schema with ODC fields
    - No diagnostic decision tree or worked examples

    This is the unstructured baseline (the retired 'naive' preset): the LLM
    classifies in its own words using the simplified JSON contract.
    """
    parts = [
        "You are a software defect analyst.",
        "Your job is to analyze a software bug and determine what TYPE of defect it is.",
    ]

    if has_fix_diff:
        parts.extend([
            "",
            "You have access to both the buggy code evidence AND the actual code change that fixed the bug.",
            "Use the fix diff to understand the NATURE of the coding error.",
        ])
    else:
        parts.extend([
            "",
            "You have access to pre-fix evidence only: failing tests, stack traces, and code snippets.",
            "Determine the root cause based on the available symptoms and code.",
        ])

    parts.extend([
        "",
        "Focus on the ROOT CAUSE of the defect, not just the observable symptom.",
        "Be specific and technical — describe the nature of the coding error.",
        "",
        "Return only valid JSON matching this schema:",
        _naive_json_contract(),
    ])
    return "\n".join(parts)


def _naive_json_contract() -> str:
    """Simplified JSON contract for naive baseline — no ODC fields."""
    return (
        "{"
        '"defect_type": "a short, specific label for the type of defect (your own words)", '
        '"confidence": "number between 0 and 100", '
        '"reasoning_summary": "a paragraph explaining your classification and what evidence supports it", '
        '"root_cause": "one sentence describing the specific coding error", '
        '"symptom": "one sentence describing the observable failure"'
        "}"
    )
