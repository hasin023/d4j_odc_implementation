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
        "You are a software defect analyst.",
        "Your job is to classify one bug into exactly one ODC defect type using only the provided pre-fix evidence.",
        "Do not use benchmark familiarity, project reputation, or hidden fix knowledge.",
        taxonomy_markdown(),
        "",
        "Return only valid JSON.",
        _json_contract(),
    ]
    if prompt_style == "scientific":
        base.extend(
            [
                "",
                "Follow a Scientific Debugging structure internally:",
                "1. Observe the failure symptoms.",
                "2. Form a root-cause hypothesis.",
                "3. Predict what code behavior that hypothesis implies.",
                "4. Use the provided code and runtime evidence as the experiment.",
                "5. Conclude with the best supported ODC type.",
            ]
        )
    return "\n".join(base)


def _build_user_prompt(context: BugContext, prompt_style: str) -> str:
    payload = _context_payload(context, prompt_style)
    return (
        "Classify this bug into one ODC defect type.\n\n"
        "Important rules:\n"
        "- Use only evidence in this prompt.\n"
        "- Prefer stack traces, failing tests, executed lines, and code snippets over guesswork.\n"
        "- If evidence is incomplete, lower confidence and set needs_human_review accordingly.\n"
        "- The output odc_type must be one of: "
        + ", ".join(ODC_TYPE_NAMES)
        + "\n\nEvidence:\n"
        + json.dumps(payload, indent=2)
    )


def _context_payload(context: BugContext, prompt_style: str) -> dict:
    payload = {
        "project_id": context.project_id,
        "bug_id": context.bug_id,
        "version_id": context.version_id,
        "metadata": {key: value for key, value in context.metadata.items() if key != "classes.modified"},
        "failing_tests": [],
        "suspicious_frames": [],
        "code_snippets": [],
        "coverage_summary": [],
        "notes": list(context.notes),
    }
    for failure in context.failures[:5]:
        payload["failing_tests"].append(
            {
                "test_name": failure.test_name,
                "headline": failure.headline,
                "stack_trace_excerpt": failure.stack_trace[:20],
            }
        )
    for frame in context.suspicious_frames[:10]:
        payload["suspicious_frames"].append(
            {
                "class_name": frame.class_name,
                "method_name": frame.method_name,
                "file_name": frame.file_name,
                "line_number": frame.line_number,
                "raw": frame.raw,
            }
        )
    snippet_limit = 6 if prompt_style == "scientific" else 4
    for snippet in context.code_snippets[:snippet_limit]:
        payload["code_snippets"].append(
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
    return payload


def _json_contract() -> str:
    return (
        "{"
        '"odc_type": "one of the allowed ODC types", '
        '"coarse_group": "Control and Data or Structural or null", '
        '"confidence": "number between 0 and 1", '
        '"needs_human_review": "boolean", '
        '"observation_summary": "short paragraph", '
        '"hypothesis": "short paragraph", '
        '"prediction": "short paragraph", '
        '"experiment_rationale": "short paragraph that explains how evidence supports or weakens the hypothesis", '
        '"reasoning_summary": "short paragraph", '
        '"evidence_used": ["specific evidence items"], '
        '"evidence_gaps": ["missing evidence or ambiguity"], '
        '"alternative_types": [{"type": "ODC type", "why_not_primary": "reason"}]'
        "}"
    )
