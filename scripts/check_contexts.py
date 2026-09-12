#!/usr/bin/env python3
"""Check whether an artifacts root is ready for classification.

Run this BEFORE classifying, especially when the contexts were collected on a
different machine. Classification never invokes Defects4J as long as every
context already exists — but a single missing context makes that bug fall
through to collection, which fails on a machine without Defects4J installed.

Usage:
    python scripts/check_contexts.py <manifest.json> <artifacts_root>

Example:
    python scripts/check_contexts.py .dist/study/manifest_lang61.json \\
                                     .dist/study/artifacts_v2

Exit codes:
    0  every bug in the manifest has a usable context for both evidence modes
    1  something is missing or stale — do not start classifying
    2  bad arguments

Why `created_at` and not the `origin` key:
    Commit 6878d90 (2026-08-10) changed what evidence is collected, and added
    an `origin` field to each entry in `suspicious_frames`. Testing for a
    missing `origin` looks like the obvious staleness check, but it has a false
    negative: a bug whose failure produced no stack frames at all (Compress-44
    in the old corpus) has no frame to carry the key, so it passes incorrectly.
    `created_at` is present in every context of both generations.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Contexts collected before this date predate 6878d90 and carry the old,
# thinner evidence (coverage empty, buggy class often absent entirely).
EVIDENCE_CUTOFF = "2026-08-10"

EVIDENCE_MODES = ("prefix", "postfix")


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__.strip())
        return 2

    manifest_path, root = Path(argv[1]), Path(argv[2])
    if not manifest_path.exists():
        print(f"error: manifest not found: {manifest_path}")
        return 2

    entries = json.loads(manifest_path.read_text(encoding="utf-8")).get("entries", [])
    if not entries:
        print(f"error: manifest has no entries: {manifest_path}")
        return 2

    missing: list[str] = []
    stale: list[str] = []
    unreadable: list[str] = []
    usable = 0

    for entry in entries:
        bug_key = f"{entry['project_id']}_{entry['bug_id']}"
        for mode in EVIDENCE_MODES:
            path = root / mode / f"{bug_key}_{mode}" / "context.json"
            if not path.exists():
                missing.append(f"{bug_key} {mode}")
                continue
            try:
                created = json.loads(path.read_text(encoding="utf-8")).get("created_at") or ""
            except (json.JSONDecodeError, OSError) as exc:
                unreadable.append(f"{bug_key} {mode} ({exc.__class__.__name__})")
                continue
            if created[:10] < EVIDENCE_CUTOFF:
                stale.append(f"{bug_key} {mode}")
            else:
                usable += 1

    expected = len(entries) * len(EVIDENCE_MODES)
    print(f"manifest      : {manifest_path}  ({len(entries)} bugs, {expected} contexts expected)")
    print(f"artifacts root: {root}")
    print()
    print(f"usable (collected on/after {EVIDENCE_CUTOFF}): {usable}")
    _report("MISSING contexts", missing)
    _report(f"STALE (collected before {EVIDENCE_CUTOFF})", stale)
    _report("UNREADABLE contexts", unreadable)

    if missing or stale or unreadable:
        print()
        print("NOT READY — classifying now would either fail on a machine without")
        print("Defects4J, or mix old and new evidence in one result set.")
        return 1

    print()
    print("READY — every bug has a current context for both evidence modes.")
    return 0


def _report(label: str, items: list[str], preview: int = 10) -> None:
    print(f"{label}: {len(items)}")
    if items:
        shown = ", ".join(items[:preview])
        more = f" ... and {len(items) - preview} more" if len(items) > preview else ""
        print(f"   {shown}{more}")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
