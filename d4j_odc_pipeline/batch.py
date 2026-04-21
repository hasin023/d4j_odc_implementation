from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

from .comparison import compare_classifications
from .defects4j import Defects4JClient
from .models import ensure_parent, utc_now_iso
from .pipeline import (
    classify_bug_context,
    collect_bug_context,
    write_json,
    write_markdown_report,
)


def generate_study_manifest(
    *,
    defects4j: Defects4JClient,
    output_path: Path,
    target_bugs: int,
    min_per_project: int = 1,
    include_deprecated: bool = False,
    seed: int = 42,
    projects: list[str] | None = None,
) -> dict[str, Any]:
    if target_bugs <= 0:
        raise ValueError("target_bugs must be > 0")
    if min_per_project <= 0:
        raise ValueError("min_per_project must be > 0")

    project_ids = sorted(projects) if projects else sorted(defects4j.pids())
    if not project_ids:
        raise ValueError("No Defects4J projects were discovered.")

    minimum_required = len(project_ids) * min_per_project
    if target_bugs < minimum_required:
        raise ValueError(
            f"target_bugs={target_bugs} is too small for {len(project_ids)} projects with "
            f"min_per_project={min_per_project}. Minimum required is {minimum_required}."
        )

    rng = random.Random(seed)
    bug_pool: dict[str, list[int]] = {}
    for project_id in project_ids:
        raw_bug_ids = defects4j.bids(project_id, include_deprecated=include_deprecated)
        bug_ids = []
        for raw in raw_bug_ids:
            value = raw.strip()
            if value.isdigit():
                bug_ids.append(int(value))
        bug_ids = sorted(set(bug_ids))
        if not bug_ids:
            raise ValueError(f"No bug IDs returned for project {project_id}.")
        rng.shuffle(bug_ids)
        bug_pool[project_id] = bug_ids

    selected: list[dict[str, Any]] = []
    selected_set: set[tuple[str, int]] = set()

    # Pass 1: guarantee per-project coverage.
    for project_id in project_ids:
        bugs = bug_pool[project_id]
        if len(bugs) < min_per_project:
            raise ValueError(
                f"Project {project_id} has only {len(bugs)} bug(s), but min_per_project={min_per_project}."
            )
        for _ in range(min_per_project):
            bug_id = bugs.pop(0)
            selected.append(
                {
                    "project_id": project_id,
                    "bug_id": bug_id,
                    "selection_phase": "min-coverage",
                }
            )
            selected_set.add((project_id, bug_id))

    # Pass 2: fill remaining slots in project round-robin order.
    while len(selected) < target_bugs:
        progressed = False
        for project_id in project_ids:
            if len(selected) >= target_bugs:
                break
            if not bug_pool[project_id]:
                continue
            bug_id = bug_pool[project_id].pop(0)
            if (project_id, bug_id) in selected_set:
                continue
            selected.append(
                {
                    "project_id": project_id,
                    "bug_id": bug_id,
                    "selection_phase": "round-robin",
                }
            )
            selected_set.add((project_id, bug_id))
            progressed = True
        if not progressed:
            break

    manifest = {
        "created_at": utc_now_iso(),
        "target_bugs": target_bugs,
        "selected_bugs": len(selected),
        "min_per_project": min_per_project,
        "seed": seed,
        "include_deprecated": include_deprecated,
        "projects_requested": project_ids,
        "projects_covered": sorted({item["project_id"] for item in selected}),
        "entries": selected,
    }

    write_json(output_path, manifest)
    return manifest


def load_manifest(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_batch_from_manifest(
    *,
    defects4j: Defects4JClient,
    manifest: dict[str, Any],
    artifacts_root: Path,
    work_root: Path,
    provider: str,
    model: str,
    api_key_env: str | None,
    base_url: str | None,
    prompt_style: str,
    snippet_radius: int = 12,
    run_coverage: bool = False,
    skip_existing: bool = True,
    prompt_output: bool = False,
) -> dict[str, Any]:
    entries = list(manifest.get("entries", []))
    if not entries:
        raise ValueError("Manifest contains no entries.")

    ensure_parent(artifacts_root / "placeholder.json")
    ensure_parent(work_root / "placeholder.txt")

    records: list[dict[str, Any]] = []

    for index, entry in enumerate(entries, start=1):
        project_id = str(entry.get("project_id", "")).strip()
        bug_id = int(entry.get("bug_id", 0))
        if not project_id or bug_id <= 0:
            records.append(
                {
                    "index": index,
                    "project_id": project_id,
                    "bug_id": bug_id,
                    "prefix_status": "invalid-manifest-entry",
                    "postfix_status": "invalid-manifest-entry",
                    "error": "Entry must include valid project_id and bug_id",
                }
            )
            continue

        bug_key = f"{project_id}_{bug_id}"
        record: dict[str, Any] = {
            "index": index,
            "project_id": project_id,
            "bug_id": bug_id,
            "bug_key": bug_key,
            "prefix_status": "pending",
            "postfix_status": "pending",
        }

        for evidence_mode in ("prefix", "postfix"):
            run_name = f"{bug_key}_{evidence_mode}"
            include_fix_diff = evidence_mode == "postfix"
            run_artifacts_dir = artifacts_root / evidence_mode / run_name
            run_work_dir = work_root / evidence_mode / f"{project_id}_{bug_id}b"
            context_path = run_artifacts_dir / "context.json"
            classification_path = run_artifacts_dir / "classification.json"
            report_path = run_artifacts_dir / "report.md"
            prompt_path = run_artifacts_dir / "prompt.json" if prompt_output else None

            status_key = f"{evidence_mode}_status"
            path_key = f"{evidence_mode}_paths"
            record[path_key] = {
                "context": str(context_path),
                "classification": str(classification_path),
                "report": str(report_path),
            }

            if (
                skip_existing
                and context_path.exists()
                and classification_path.exists()
                and report_path.exists()
            ):
                record[status_key] = "skipped-existing"
                continue

            try:
                context = collect_bug_context(
                    defects4j=defects4j,
                    project_id=project_id,
                    bug_id=bug_id,
                    work_dir=run_work_dir,
                    output_path=context_path,
                    snippet_radius=snippet_radius,
                    run_coverage=run_coverage,
                    include_fix_diff=include_fix_diff,
                )

                classification = classify_bug_context(
                    context=context,
                    prompt_style=prompt_style,
                    output_path=classification_path,
                    provider=provider,
                    model=model,
                    api_key_env=api_key_env,
                    base_url=base_url,
                    prompt_output_path=prompt_path,
                    dry_run=False,
                )

                if classification is None:
                    raise ValueError("Classification returned None. Disable dry-run for batch execution.")

                write_markdown_report(
                    context=context,
                    classification=classification,
                    output_path=report_path,
                )
                record[status_key] = "ok"
            except Exception as exc:  # noqa: BLE001
                record[status_key] = "failed"
                record[f"{evidence_mode}_error"] = str(exc)

        # Include pairwise comparison inline when both runs are available.
        try:
            prefix_classification_path = Path(record["prefix_paths"]["classification"])
            postfix_classification_path = Path(record["postfix_paths"]["classification"])
            if prefix_classification_path.exists() and postfix_classification_path.exists():
                prefix_data = json.loads(prefix_classification_path.read_text(encoding="utf-8"))
                postfix_data = json.loads(postfix_classification_path.read_text(encoding="utf-8"))
                cmp_result = compare_classifications(prefix_data, postfix_data)
                record["comparison"] = cmp_result.to_dict()
        except Exception as exc:  # noqa: BLE001
            record["comparison_error"] = str(exc)

        records.append(record)

    summary = {
        "created_at": utc_now_iso(),
        "manifest_target_bugs": manifest.get("target_bugs"),
        "manifest_selected_bugs": len(entries),
        "total_entries": len(records),
        "prefix_ok": sum(1 for r in records if r.get("prefix_status") in {"ok", "skipped-existing"}),
        "postfix_ok": sum(1 for r in records if r.get("postfix_status") in {"ok", "skipped-existing"}),
        "paired_for_compare": sum(1 for r in records if isinstance(r.get("comparison"), dict)),
        "projects_covered": sorted({str(r.get("project_id", "")) for r in records if r.get("project_id")}),
        "records": records,
    }
    return summary


def analyze_batch_artifacts(
    *,
    prefix_dir: Path,
    postfix_dir: Path,
    expected_projects: list[str] | None = None,
) -> dict[str, Any]:
    pairs = _discover_pairs(prefix_dir, postfix_dir)
    rows: list[dict[str, Any]] = []
    transitions: dict[str, int] = {}
    per_project: dict[str, dict[str, int]] = {}

    for key, pair in pairs.items():
        prefix_cls = _load_json(pair["prefix"] / "classification.json")
        postfix_cls = _load_json(pair["postfix"] / "classification.json")
        prefix_ctx = _load_json(pair["prefix"] / "context.json")
        postfix_ctx = _load_json(pair["postfix"] / "context.json")
        prefix_report = _read_text(pair["prefix"] / "report.md")
        postfix_report = _read_text(pair["postfix"] / "report.md")

        cmp_result = compare_classifications(prefix_cls, postfix_cls)

        prefix_alts = _alternative_type_set(prefix_cls)
        postfix_alts = _alternative_type_set(postfix_cls)
        alt_overlap = sorted(prefix_alts & postfix_alts)
        primary_cross = (
            cmp_result.prefix_odc_type in postfix_alts
            or cmp_result.postfix_odc_type in prefix_alts
        )
        no_common_alternative = (
            not cmp_result.strict_match
            and not primary_cross
            and not alt_overlap
        )

        transition = f"{cmp_result.prefix_odc_type} -> {cmp_result.postfix_odc_type}"
        transitions[transition] = transitions.get(transition, 0) + 1

        project_bucket = per_project.setdefault(
            cmp_result.project_id,
            {
                "total": 0,
                "type_changed": 0,
                "top2_match": 0,
                "family_match": 0,
            },
        )
        project_bucket["total"] += 1
        if not cmp_result.strict_match:
            project_bucket["type_changed"] += 1
        if cmp_result.top2_match:
            project_bucket["top2_match"] += 1
        if cmp_result.family_match:
            project_bucket["family_match"] += 1

        reason_lines = _compose_reason_lines(
            cmp_result=cmp_result,
            prefix_context=prefix_ctx,
            postfix_context=postfix_ctx,
            prefix_report=prefix_report,
            postfix_report=postfix_report,
            alt_overlap=alt_overlap,
            primary_cross=primary_cross,
            no_common_alternative=no_common_alternative,
        )

        confidence_gap = abs(cmp_result.prefix_confidence - cmp_result.postfix_confidence)

        row = {
            "key": key,
            "project_id": cmp_result.project_id,
            "bug_id": cmp_result.bug_id,
            "prefix_odc_type": cmp_result.prefix_odc_type,
            "postfix_odc_type": cmp_result.postfix_odc_type,
            "strict_match": cmp_result.strict_match,
            "top2_match": cmp_result.top2_match,
            "family_match": cmp_result.family_match,
            "confidence_gap": round(confidence_gap, 4),
            "alternative_overlap": alt_overlap,
            "primary_cross_alternative_match": primary_cross,
            "no_common_alternative": no_common_alternative,
            "reason_lines": reason_lines,
            "comparison_detail": cmp_result.match_detail,
        }
        rows.append(row)

    total = len(rows)
    type_changed = sum(1 for row in rows if not row["strict_match"])
    top2 = sum(1 for row in rows if row["top2_match"])
    family = sum(1 for row in rows if row["family_match"])

    projects_seen = sorted({row["project_id"] for row in rows})
    missing_projects: list[str] = []
    if expected_projects is not None:
        missing_projects = sorted(set(expected_projects) - set(projects_seen))

    alt_candidates = [
        row
        for row in rows
        if not row["strict_match"] and row["primary_cross_alternative_match"]
    ]
    no_common_candidates = [
        row
        for row in rows
        if row["no_common_alternative"]
    ]

    alt_candidates.sort(key=lambda item: (item["confidence_gap"], not item["family_match"]), reverse=True)
    no_common_candidates.sort(
        key=lambda item: (item["confidence_gap"], not item["family_match"]),
        reverse=True,
    )

    summary = {
        "created_at": utc_now_iso(),
        "total_pairs": total,
        "unique_projects": len(projects_seen),
        "projects_seen": projects_seen,
        "missing_projects": missing_projects,
        "type_changed_count": type_changed,
        "type_changed_rate": (type_changed / total) if total else 0.0,
        "top2_match_count": top2,
        "top2_match_rate": (top2 / total) if total else 0.0,
        "family_match_count": family,
        "family_match_rate": (family / total) if total else 0.0,
        "per_project": per_project,
        "type_transitions": dict(sorted(transitions.items(), key=lambda item: item[1], reverse=True)),
        "top3_alternative_match": alt_candidates[:3],
        "top3_no_common_alternative": no_common_candidates[:3],
        "rows": rows,
    }
    return summary


def write_analysis_markdown(summary: dict[str, Any], output_path: Path) -> None:
    lines: list[str] = [
        "# Batch Study Analysis",
        "",
        f"- Created: `{summary.get('created_at', '')}`",
        f"- Total pairs: **{summary.get('total_pairs', 0)}**",
        f"- Projects covered: **{summary.get('unique_projects', 0)}**",
        f"- Type changed: **{summary.get('type_changed_count', 0)}** ({summary.get('type_changed_rate', 0.0):.1%})",
        f"- Top-2 match: **{summary.get('top2_match_count', 0)}** ({summary.get('top2_match_rate', 0.0):.1%})",
        f"- Family match: **{summary.get('family_match_count', 0)}** ({summary.get('family_match_rate', 0.0):.1%})",
        "",
    ]

    missing = summary.get("missing_projects", []) or []
    if missing:
        lines.append("## Missing Projects")
        lines.append("")
        for item in missing:
            lines.append(f"- {item}")
        lines.append("")

    lines.extend([
        "## Top 3: Alternative Match Cases",
        "",
    ])
    top_alt = summary.get("top3_alternative_match", []) or []
    if not top_alt:
        lines.append("- No qualifying cases found.")
    for row in top_alt:
        lines.append(f"### {row['project_id']}-{row['bug_id']}")
        for reason in row.get("reason_lines", [])[:6]:
            lines.append(f"- {reason}")
        lines.append("")

    lines.extend([
        "## Top 3: No Common Alternative Cases",
        "",
    ])
    top_no_common = summary.get("top3_no_common_alternative", []) or []
    if not top_no_common:
        lines.append("- No qualifying cases found.")
    for row in top_no_common:
        lines.append(f"### {row['project_id']}-{row['bug_id']}")
        for reason in row.get("reason_lines", [])[:6]:
            lines.append(f"- {reason}")
        lines.append("")

    lines.extend([
        "## Type Transitions",
        "",
    ])
    transitions = summary.get("type_transitions", {}) or {}
    if not transitions:
        lines.append("- No transitions recorded.")
    else:
        for transition, count in transitions.items():
            lines.append(f"- {transition}: {count}")

    ensure_parent(output_path)
    output_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _discover_pairs(prefix_dir: Path, postfix_dir: Path) -> dict[str, dict[str, Path]]:
    if not prefix_dir.is_dir():
        raise ValueError(f"Prefix directory does not exist: {prefix_dir}")
    if not postfix_dir.is_dir():
        raise ValueError(f"Postfix directory does not exist: {postfix_dir}")

    prefix_map: dict[str, Path] = {}
    for child in sorted(prefix_dir.iterdir()):
        if not child.is_dir():
            continue
        if not (child / "classification.json").exists():
            continue
        key = child.name[:-7] if child.name.endswith("_prefix") else child.name
        prefix_map[key] = child

    pairs: dict[str, dict[str, Path]] = {}
    for child in sorted(postfix_dir.iterdir()):
        if not child.is_dir():
            continue
        if not (child / "classification.json").exists():
            continue
        key = child.name[:-8] if child.name.endswith("_postfix") else child.name
        if key not in prefix_map:
            continue
        pairs[key] = {
            "prefix": prefix_map[key],
            "postfix": child,
        }
    return pairs


def _alternative_type_set(payload: dict[str, Any]) -> set[str]:
    result: set[str] = set()
    for item in payload.get("alternative_types", []):
        if isinstance(item, dict):
            candidate = str(item.get("type", "")).strip()
            if candidate:
                result.add(candidate)
    return result


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def _first_failure_headline(context: dict[str, Any]) -> str:
    failures = context.get("failures", [])
    if not failures:
        return "No parsed failures"
    first = failures[0]
    headline = str(first.get("headline", "")).strip()
    test_name = str(first.get("test_name", "")).strip()
    if headline and test_name:
        return f"{test_name}: {headline}"
    if test_name:
        return test_name
    if headline:
        return headline
    return "No failure headline"


def _first_suspicious_frame(context: dict[str, Any]) -> str:
    frames = context.get("suspicious_frames", [])
    if not frames:
        return "No suspicious frames"
    frame = frames[0]
    class_name = str(frame.get("class_name", "")).strip()
    method_name = str(frame.get("method_name", "")).strip()
    line_number = frame.get("line_number")
    if class_name and method_name and line_number:
        return f"{class_name}.{method_name}:{line_number}"
    if class_name and method_name:
        return f"{class_name}.{method_name}"
    return class_name or "Unknown frame"


def _extract_report_odc_excerpt(report_text: str) -> str:
    if not report_text.strip():
        return "No report excerpt"
    lines = report_text.splitlines()
    start = None
    for idx, line in enumerate(lines):
        if line.strip().lower() == "## odc result":
            start = idx + 1
            break
    if start is None:
        return "No ODC section found"
    excerpt_lines: list[str] = []
    for line in lines[start:start + 10]:
        value = line.strip()
        if not value:
            continue
        excerpt_lines.append(value)
    if not excerpt_lines:
        return "ODC section was empty"
    return " ".join(excerpt_lines)[:240]


def _compose_reason_lines(
    *,
    cmp_result: Any,
    prefix_context: dict[str, Any],
    postfix_context: dict[str, Any],
    prefix_report: str,
    postfix_report: str,
    alt_overlap: list[str],
    primary_cross: bool,
    no_common_alternative: bool,
) -> list[str]:
    lines = [
        f"Type shift: {cmp_result.prefix_odc_type} -> {cmp_result.postfix_odc_type}.",
        f"Comparison detail: {cmp_result.match_detail}",
        f"Prefix reasoning summary: {cmp_result.prefix_reasoning_summary[:220] or 'N/A'}",
        f"Postfix reasoning summary: {cmp_result.postfix_reasoning_summary[:220] or 'N/A'}",
        f"Prefix context signal: {_first_failure_headline(prefix_context)}",
        f"Postfix context signal: {_first_failure_headline(postfix_context)}",
        f"Prefix suspicious frame: {_first_suspicious_frame(prefix_context)}",
        f"Postfix suspicious frame: {_first_suspicious_frame(postfix_context)}",
        f"Prefix report cue: {_extract_report_odc_excerpt(prefix_report)}",
        f"Postfix report cue: {_extract_report_odc_excerpt(postfix_report)}",
    ]
    if primary_cross:
        lines.append("Primary type appears in the opposite side alternative list.")
    if alt_overlap:
        lines.append(f"Alternative overlap: {', '.join(alt_overlap)}")
    if no_common_alternative:
        lines.append("No shared alternative support across the two runs.")
    return lines