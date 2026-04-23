from __future__ import annotations

import hashlib
import json
import random
import signal
import threading
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
from . import console


# ---------------------------------------------------------------------------
# Graceful shutdown via signal handling
# ---------------------------------------------------------------------------

_shutdown_requested = threading.Event()


def _request_shutdown(signum: int, frame: object) -> None:
    """Signal handler: first Ctrl+C sets the flag; second force-exits."""
    if _shutdown_requested.is_set():
        # Second interrupt → force exit immediately
        raise SystemExit(130)
    _shutdown_requested.set()
    console.warn("Shutdown requested — finishing current entry then stopping (press Ctrl+C again to force-quit)")


def install_signal_handlers() -> None:
    """Install SIGINT/SIGBREAK handlers for graceful batch shutdown."""
    signal.signal(signal.SIGINT, _request_shutdown)
    if hasattr(signal, "SIGBREAK"):  # Windows
        signal.signal(signal.SIGBREAK, _request_shutdown)


def reset_shutdown() -> None:
    """Clear the shutdown flag (call before starting a new batch)."""
    _shutdown_requested.clear()


def is_shutdown_requested() -> bool:
    """Check whether a graceful shutdown has been requested."""
    return _shutdown_requested.is_set()


# ---------------------------------------------------------------------------
# Checkpoint persistence for resume capability
# ---------------------------------------------------------------------------

def _compute_manifest_hash(entries: list[dict[str, Any]]) -> str:
    """Deterministic hash of manifest entries so we can detect stale checkpoints."""
    keys = sorted(f"{e.get('project_id', '')}_{e.get('bug_id', '')}" for e in entries)
    return hashlib.sha256("|".join(keys).encode()).hexdigest()[:16]


def _is_entry_complete(record: dict[str, Any]) -> bool:
    return (
        record.get("prefix_status") in {"ok", "skipped-existing"}
        and record.get("postfix_status") in {"ok", "skipped-existing"}
    )


def _write_checkpoint(
    checkpoint_path: Path,
    records: list[dict[str, Any]],
    manifest_hash: str,
    interrupted: bool,
) -> None:
    data = {
        "manifest_hash": manifest_hash,
        "updated_at": utc_now_iso(),
        "completed_keys": [r["bug_key"] for r in records if _is_entry_complete(r)],
        "total_attempted": len(records),
        "interrupted": interrupted,
    }
    write_json(checkpoint_path, data)


def _load_checkpoint(checkpoint_path: Path, manifest_hash: str) -> set[str]:
    """Load completed bug keys from a checkpoint, or empty set if stale/missing."""
    if not checkpoint_path.exists():
        return set()
    try:
        data = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return set()
    if data.get("manifest_hash") != manifest_hash:
        console.warn("Checkpoint manifest hash mismatch — starting fresh")
        return set()
    completed = set(data.get("completed_keys", []))
    if completed:
        console.step(f"Resuming from checkpoint: {len(completed)} entries already complete")
    return completed


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

    # ── Checkpoint setup ──────────────────────────────────────────────
    manifest_hash = _compute_manifest_hash(entries)
    checkpoint_path = artifacts_root / "checkpoint.json"
    completed_keys = _load_checkpoint(checkpoint_path, manifest_hash)

    records: list[dict[str, Any]] = []
    interrupted = False

    # ── Progress bar ──────────────────────────────────────────────────
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, MofNCompleteColumn, TimeElapsedColumn

    con = console.get_console()
    progress_ctx = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        console=con,
        disable=console.is_quiet() or con is None,
    )

    with progress_ctx as progress:
        task_id = progress.add_task("Processing bugs", total=len(entries))

        for index, entry in enumerate(entries, start=1):
            # ── Check for graceful shutdown ────────────────────────────
            if is_shutdown_requested():
                console.warn(f"Shutdown requested — stopping after {index - 1}/{len(entries)} entries")
                interrupted = True
                break

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
                progress.advance(task_id)
                continue

            bug_key = f"{project_id}_{bug_id}"

            # ── Skip if already completed in a previous run ───────────
            if bug_key in completed_keys:
                progress.update(task_id, description=f"[dim]{bug_key} (checkpoint-skip)[/dim]")
                records.append(
                    {
                        "index": index,
                        "project_id": project_id,
                        "bug_id": bug_id,
                        "bug_key": bug_key,
                        "prefix_status": "skipped-existing",
                        "postfix_status": "skipped-existing",
                    }
                )
                progress.advance(task_id)
                continue

            progress.update(task_id, description=f"[cyan]{bug_key}[/cyan] [{index}/{len(entries)}]")

            record: dict[str, Any] = {
                "index": index,
                "project_id": project_id,
                "bug_id": bug_id,
                "bug_key": bug_key,
                "prefix_status": "pending",
                "postfix_status": "pending",
            }

            for evidence_mode in ("prefix", "postfix"):
                # Check shutdown between evidence modes too
                if is_shutdown_requested():
                    record[f"{evidence_mode}_status"] = "interrupted"
                    interrupted = True
                    break

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

                    # Check shutdown between collect and classify
                    if is_shutdown_requested():
                        record[status_key] = "interrupted"
                        interrupted = True
                        break

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

            # If we broke out of the evidence_mode loop due to shutdown
            if interrupted:
                records.append(record)
                break

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

            # ── Write checkpoint after each completed entry ────────────
            _write_checkpoint(checkpoint_path, records, manifest_hash, interrupted=False)

            progress.advance(task_id)

    # ── Final checkpoint ──────────────────────────────────────────────
    _write_checkpoint(checkpoint_path, records, manifest_hash, interrupted=interrupted)

    completed_count = sum(1 for r in records if _is_entry_complete(r))

    summary = {
        "created_at": utc_now_iso(),
        "manifest_target_bugs": manifest.get("target_bugs"),
        "manifest_selected_bugs": len(entries),
        "total_entries": len(records),
        "completed_entries": completed_count,
        "interrupted": interrupted,
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
    transitions: dict[str, dict[str, Any]] = {}
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
        if transition not in transitions:
            transitions[transition] = {"count": 0, "bugs": []}
        transitions[transition]["count"] += 1
        transitions[transition]["bugs"].append(f"{cmp_result.project_id}-{cmp_result.bug_id}")

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
    type_unchanged = total - type_changed
    top2 = sum(1 for row in rows if row["top2_match"])
    family = sum(1 for row in rows if row["family_match"])
    no_family_match = sum(1 for row in rows if not row["strict_match"] and not row["family_match"])

    projects_seen = sorted({row["project_id"] for row in rows})
    missing_projects: list[str] = []
    if expected_projects is not None:
        missing_projects = sorted(set(expected_projects) - set(projects_seen))

    alt_candidates = [
        row
        for row in rows
        if not row["strict_match"] and row["primary_cross_alternative_match"]
    ]
    no_alternative_candidates = [
        row
        for row in rows
        if not row["strict_match"] and not row["primary_cross_alternative_match"]
    ]
    no_common_candidates = [
        row
        for row in rows
        if row["no_common_alternative"]
    ]

    alt_candidates.sort(key=lambda item: (item["confidence_gap"], not item["family_match"]), reverse=True)
    no_alternative_candidates.sort(key=lambda item: (item["confidence_gap"], not item["family_match"]), reverse=True)
    no_common_candidates.sort(
        key=lambda item: (item["confidence_gap"], not item["family_match"]),
        reverse=True,
    )

    # Separate transitions into changed and unchanged, and track no-alternative and no-family-match bugs
    transitions_changed = {}
    transitions_unchanged = {}
    no_alternative_bug_set = {row["project_id"] + "-" + str(row["bug_id"]) for row in no_alternative_candidates}
    no_family_match_bug_set = {
        row["project_id"] + "-" + str(row["bug_id"])
        for row in rows
        if not row["strict_match"] and not row["family_match"]
    }
    
    for transition, data in transitions.items():
        prefix_type, postfix_type = transition.split(" -> ")
        # Mark bugs with no alternative overlap and/or no family match
        marked_bugs = []
        for bug in data["bugs"]:
            markers = []
            if bug in no_alternative_bug_set:
                markers.append("no alt overlap")
            if bug in no_family_match_bug_set:
                markers.append("no family match")
            if markers:
                marked_bugs.append(f"{bug} ({', '.join(markers)})")
            else:
                marked_bugs.append(bug)
        data["bugs"] = marked_bugs
        
        if prefix_type == postfix_type:
            transitions_unchanged[transition] = data
        else:
            transitions_changed[transition] = data

    transitions_changed = dict(sorted(transitions_changed.items(), key=lambda item: item[1]["count"], reverse=True))
    transitions_unchanged = dict(sorted(transitions_unchanged.items(), key=lambda item: item[1]["count"], reverse=True))

    summary = {
        "created_at": utc_now_iso(),
        "total_pairs": total,
        "unique_projects": len(projects_seen),
        "projects_seen": projects_seen,
        "missing_projects": missing_projects,
        "type_changed_count": type_changed,
        "type_changed_rate": (type_changed / total) if total else 0.0,
        "type_unchanged_count": type_unchanged,
        "type_unchanged_rate": (type_unchanged / total) if total else 0.0,
        "no_alternative_count": len(no_alternative_candidates),
        "no_alternative_rate": (len(no_alternative_candidates) / total) if total else 0.0,
        "no_family_match_count": no_family_match,
        "no_family_match_rate": (no_family_match / total) if total else 0.0,
        "top2_match_count": top2,
        "top2_match_rate": (top2 / total) if total else 0.0,
        "family_match_count": family,
        "family_match_rate": (family / total) if total else 0.0,
        "per_project": per_project,
        "type_transitions_changed": transitions_changed,
        "type_transitions_unchanged": transitions_unchanged,
        "top3_alternative_match": alt_candidates,
        "type_changed_no_alternative": no_alternative_candidates,
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
        f"- Type unchanged: **{summary.get('type_unchanged_count', 0)}** ({summary.get('type_unchanged_rate', 0.0):.1%})",
        f"- No alternative overlap: **{summary.get('no_alternative_count', 0)}** ({summary.get('no_alternative_rate', 0.0):.1%})",
        f"- No family match: **{summary.get('no_family_match_count', 0)}** ({summary.get('no_family_match_rate', 0.0):.1%})",
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
        "## Alternative Match Cases (Type Changed)",
        "",
    ])
    alt_match = summary.get("top3_alternative_match", []) or []
    if not alt_match:
        lines.append("- No qualifying cases found.")
    for row in alt_match:
        lines.append(f"### {row['project_id']}-{row['bug_id']}")
        for reason in row.get("reason_lines", [])[:6]:
            lines.append(f"- {reason}")
        lines.append("")

    lines.extend([
        "## Type Changed (No Alternative Overlap)",
        "",
    ])
    no_alt_match = summary.get("type_changed_no_alternative", []) or []
    if not no_alt_match:
        lines.append("- No qualifying cases found.")
    for row in no_alt_match:
        lines.append(f"### {row['project_id']}-{row['bug_id']}")
        for reason in row.get("reason_lines", [])[:6]:
            lines.append(f"- {reason}")
        lines.append("")

    lines.extend([
        "## Type Transitions",
        "",
    ])

    transitions_changed = summary.get("type_transitions_changed", {}) or {}
    transitions_unchanged = summary.get("type_transitions_unchanged", {}) or {}

    if transitions_changed:
        lines.append("### Type Changed (Prefix → Postfix)")
        lines.append("")
        for transition, data in transitions_changed.items():
            count = data.get("count", 0)
            bugs = data.get("bugs", [])
            lines.append(f"- {transition}: {count}")
            if bugs:
                lines.append(f"  - Bugs: {', '.join(bugs)}")
        lines.append("")

    if transitions_unchanged:
        lines.append("### Type Unchanged")
        lines.append("")
        for transition, data in transitions_unchanged.items():
            count = data.get("count", 0)
            bugs = data.get("bugs", [])
            lines.append(f"- {transition}: {count}")
            if bugs:
                lines.append(f"  - Bugs: {', '.join(bugs)}")
        lines.append("")

    if not transitions_changed and not transitions_unchanged:
        lines.append("- No transitions recorded.")

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
        f"Prefix reasoning summary: {cmp_result.prefix_reasoning_summary or 'N/A'}",
        f"Postfix reasoning summary: {cmp_result.postfix_reasoning_summary or 'N/A'}",
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