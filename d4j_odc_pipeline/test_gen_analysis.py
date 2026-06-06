"""
ICSEA sub-paper: batch analysis for test generation results.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .test_gen import TestGenResult


def load_results(results_dir: Path) -> list[TestGenResult]:
    """Load all test_gen_result.json files under results_dir."""
    results: list[TestGenResult] = []
    for json_file in sorted(results_dir.rglob("test_gen_result.json")):
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
            results.append(_result_from_dict(data))
        except Exception:
            continue
    return results


def _result_from_dict(data: dict[str, Any]) -> TestGenResult:
    return TestGenResult(
        project_id=data["project_id"],
        bug_id=int(data["bug_id"]),
        prefix_work_dir=data["prefix_work_dir"],
        postfix_work_dir=data["postfix_work_dir"],
        model=data["model"],
        provider=data["provider"],
        created_at=data["created_at"],
        prompt_style=data["prompt_style"],
        generated_class_name=data["generated_class_name"],
        generated_method_name=data["generated_method_name"],
        generated_test_code=data["generated_test_code"],
        raw_llm_response=data["raw_llm_response"],
        compilation_success=bool(data["compilation_success"]),
        compilation_error=data.get("compilation_error"),
        fails_on_buggy=data.get("fails_on_buggy"),
        passes_on_fixed=data.get("passes_on_fixed"),
        oracle_match=data.get("oracle_match"),
        trigger_methods=list(data.get("trigger_methods", [])),
        trigger_test_source=data.get("trigger_test_source", ""),
        method_name_match=bool(data.get("method_name_match", False)),
        trigger_class_targeted=bool(data.get("trigger_class_targeted", False)),
        modified_class=data.get("modified_class"),
        buggy_stdout=data.get("buggy_stdout", ""),
        buggy_stderr=data.get("buggy_stderr", ""),
        fixed_stdout=data.get("fixed_stdout", ""),
        fixed_stderr=data.get("fixed_stderr", ""),
        notes=list(data.get("notes", [])),
        refine_iterations=int(data.get("refine_iterations", 0)),
        refine_history=list(data.get("refine_history", [])),
    )


def compute_aggregate_metrics(results: list[TestGenResult]) -> dict[str, Any]:
    total = len(results)
    compiled = sum(1 for r in results if r.compilation_success)
    fails_on_buggy = sum(1 for r in results if r.fails_on_buggy is True)
    passes_on_fixed = sum(1 for r in results if r.passes_on_fixed is True)
    oracle = sum(1 for r in results if r.oracle_match is True)
    method_match = sum(1 for r in results if r.method_name_match)
    class_targeted = sum(1 for r in results if r.trigger_class_targeted)

    def rate(n: int, d: int) -> float:
        return round(n / d, 4) if d > 0 else 0.0

    per_project: dict[str, dict[str, Any]] = {}
    for r in results:
        proj = r.project_id
        if proj not in per_project:
            per_project[proj] = {
                "total": 0, "compiled": 0, "fails_on_buggy": 0,
                "passes_on_fixed": 0, "oracle_match": 0,
            }
        per_project[proj]["total"] += 1
        if r.compilation_success:
            per_project[proj]["compiled"] += 1
        if r.fails_on_buggy is True:
            per_project[proj]["fails_on_buggy"] += 1
        if r.passes_on_fixed is True:
            per_project[proj]["passes_on_fixed"] += 1
        if r.oracle_match is True:
            per_project[proj]["oracle_match"] += 1

    for proj, counts in per_project.items():
        counts["compilation_rate"] = rate(counts["compiled"], counts["total"])
        counts["fault_detection_rate"] = rate(counts["fails_on_buggy"], counts["compiled"])
        counts["oracle_pass_rate"] = rate(counts["oracle_match"], counts["compiled"])

    prompt_styles = sorted({r.prompt_style for r in results})
    per_style: dict[str, dict[str, Any]] = {}
    for style in prompt_styles:
        style_results = [r for r in results if r.prompt_style == style]
        n = len(style_results)
        c = sum(1 for r in style_results if r.compilation_success)
        fb = sum(1 for r in style_results if r.fails_on_buggy is True)
        pf = sum(1 for r in style_results if r.passes_on_fixed is True)
        om = sum(1 for r in style_results if r.oracle_match is True)
        per_style[style] = {
            "total": n,
            "compiled": c,
            "fails_on_buggy": fb,
            "passes_on_fixed": pf,
            "oracle_match": om,
            "compilation_rate": rate(c, n),
            "fault_detection_rate": rate(fb, c),
            "oracle_pass_rate": rate(om, c),
        }

    # Refinement loop metrics
    refined_used = [r for r in results if r.refine_iterations > 0]
    # Maintained fault detection through refinement (did not regress)
    refined_fault_kept = [r for r in refined_used if r.fails_on_buggy is True]
    # Actually achieved oracle_match through refinement
    refined_oracle_match = [r for r in refined_used if r.oracle_match is True]
    avg_iters = (
        round(sum(r.refine_iterations for r in refined_used) / len(refined_used), 2)
        if refined_used else 0.0
    )

    return {
        "total": total,
        "compiled": compiled,
        "fails_on_buggy": fails_on_buggy,
        "passes_on_fixed": passes_on_fixed,
        "oracle_match": oracle,
        "method_name_match": method_match,
        "class_targeted": class_targeted,
        "compilation_rate": rate(compiled, total),
        "fault_detection_rate": rate(fails_on_buggy, compiled),
        "oracle_pass_rate": rate(oracle, compiled),
        "method_name_match_rate": rate(method_match, total),
        "class_targeting_rate": rate(class_targeted, total),
        "refinement_used_count": len(refined_used),
        "refinement_used_rate": rate(len(refined_used), total),
        "refined_fault_kept_count": len(refined_fault_kept),
        "refined_fault_kept_rate": rate(len(refined_fault_kept), len(refined_used)),
        "refined_oracle_match_count": len(refined_oracle_match),
        "refined_oracle_match_rate": rate(len(refined_oracle_match), len(refined_used)),
        "avg_refine_iterations": avg_iters,
        "per_project": per_project,
        "per_style": per_style,
    }


def generate_report(metrics: dict[str, Any], results: list[TestGenResult]) -> str:
    lines: list[str] = [
        "# Test Generation Analysis Report",
        "",
        "## Aggregate Metrics",
        "",
        f"- **Total bugs**: {metrics['total']}",
        f"- **Compiled**: {metrics['compiled']} ({metrics['compilation_rate']:.0%})",
        f"- **Fails on buggy** (of compiled): {metrics['fails_on_buggy']} ({metrics['fault_detection_rate']:.0%})",
        f"- **Passes on fixed** (of compiled): {metrics['passes_on_fixed']}",
        f"- **Oracle match** (fails buggy AND passes fixed): {metrics['oracle_match']} ({metrics['oracle_pass_rate']:.0%})",
        f"- **Method name match rate**: {metrics['method_name_match_rate']:.0%}",
        f"- **Modified class targeted rate**: {metrics['class_targeting_rate']:.0%}",
        f"- **Refinement used**: {metrics['refinement_used_count']} ({metrics['refinement_used_rate']:.0%})",
        f"- **Fault detection kept through refinement**: {metrics['refined_fault_kept_count']} ({metrics['refined_fault_kept_rate']:.0%} of refined)",
        f"- **Oracle match achieved through refinement**: {metrics['refined_oracle_match_count']} ({metrics['refined_oracle_match_rate']:.0%} of refined)",
        f"- **Avg refine iterations** (when used): {metrics['avg_refine_iterations']}",
        "",
    ]

    if metrics.get("per_style"):
        lines += [
            "## Per Prompt Style (Ablation)",
            "",
            "| Style | Total | Compiled | Fault Detection | Oracle Match |",
            "|-------|-------|----------|-----------------|--------------|",
        ]
        for style, s in sorted(metrics["per_style"].items()):
            lines.append(
                f"| {style} | {s['total']} | {s['compiled']} ({s['compilation_rate']:.0%}) "
                f"| {s['fails_on_buggy']} ({s['fault_detection_rate']:.0%}) "
                f"| {s['oracle_match']} ({s['oracle_pass_rate']:.0%}) |"
            )
        lines.append("")

    if metrics.get("per_project"):
        lines += [
            "## Per Project Breakdown",
            "",
            "| Project | Total | Compiled | Fault Detection | Oracle Match |",
            "|---------|-------|----------|-----------------|--------------|",
        ]
        for proj, p in sorted(metrics["per_project"].items()):
            lines.append(
                f"| {proj} | {p['total']} | {p['compiled']} ({p['compilation_rate']:.0%}) "
                f"| {p['fails_on_buggy']} ({p['fault_detection_rate']:.0%}) "
                f"| {p['oracle_match']} ({p['oracle_pass_rate']:.0%}) |"
            )
        lines.append("")

    lines += [
        "## Per-Bug Details",
        "",
        "| Bug | Style | Compiled | Fails Buggy | Passes Fixed | Oracle | Notes |",
        "|-----|-------|----------|-------------|--------------|--------|-------|",
    ]
    for r in sorted(results, key=lambda x: (x.project_id, x.bug_id)):
        compiled = "Y" if r.compilation_success else "N"
        fb = ("Y" if r.fails_on_buggy else "N") if r.fails_on_buggy is not None else "-"
        pf = ("Y" if r.passes_on_fixed else "N") if r.passes_on_fixed is not None else "-"
        om = ("Y" if r.oracle_match else "N") if r.oracle_match is not None else "-"
        notes_str = "; ".join(r.notes[:1]) if r.notes else ""
        lines.append(
            f"| {r.project_id}-{r.bug_id} | {r.prompt_style} | {compiled} | {fb} | {pf} | {om} | {notes_str} |"
        )

    return "\n".join(lines) + "\n"


def export_csv(results: list[TestGenResult], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "project_id", "bug_id", "prompt_style", "model", "provider",
        "compilation_success", "compilation_error",
        "fails_on_buggy", "passes_on_fixed", "oracle_match",
        "method_name_match", "trigger_class_targeted", "modified_class",
        "trigger_methods", "generated_method_name", "notes",
    ]
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow({
                "project_id": r.project_id,
                "bug_id": r.bug_id,
                "prompt_style": r.prompt_style,
                "model": r.model,
                "provider": r.provider,
                "compilation_success": r.compilation_success,
                "compilation_error": r.compilation_error or "",
                "fails_on_buggy": r.fails_on_buggy,
                "passes_on_fixed": r.passes_on_fixed,
                "oracle_match": r.oracle_match,
                "method_name_match": r.method_name_match,
                "trigger_class_targeted": r.trigger_class_targeted,
                "modified_class": r.modified_class or "",
                "trigger_methods": "|".join(r.trigger_methods),
                "generated_method_name": r.generated_method_name,
                "notes": "; ".join(r.notes),
            })
