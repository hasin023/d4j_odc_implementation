"""Filesystem hygiene only — never touches the pipeline.

study-collect's automatic checkout cleanup (shutil.rmtree) fails on this
machine: Defects4J/git leave some checkout files read-only, and plain
rmtree can't remove those on Windows. A failed cleanup is silent-ish (one
warning line) and the run continues, so leaked checkouts accumulate under
--work-root over a long run.

This script deletes ONLY checkouts whose bug+mode already has a finished
context.json under --artifacts-root — i.e. exactly the ones the pipeline
itself intended to delete and couldn't. It never touches:
  - the bug currently being collected (no context.json yet -> skipped)
  - a bug whose collection failed outright (no context.json -> skipped,
    left for manual inspection)

Safe to run anytime, including while study-collect is running in another
terminal.

Usage:
    python scripts/sweep_work_v2.py
    python scripts/sweep_work_v2.py --artifacts-root .dist/study/artifacts_v2 --work-root .dist/study/work_v2
    python scripts/sweep_work_v2.py --dry-run
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import stat
from pathlib import Path

WORK_DIR_RE = re.compile(r"^([A-Za-z][A-Za-z0-9]*)_(\d+)b(_fixed)?$")


def _force_rmtree(path: Path) -> None:
    def _on_error(func, target, exc_info):
        # Clear the read-only bit git leaves on object files, then retry once.
        os.chmod(target, stat.S_IWRITE)
        func(target)

    shutil.rmtree(path, onerror=_on_error)


def _dir_size(path: Path) -> int:
    total = 0
    for root, _dirs, files in os.walk(path):
        for name in files:
            try:
                total += os.path.getsize(os.path.join(root, name))
            except OSError:
                pass
    return total


def sweep(artifacts_root: Path, work_root: Path, dry_run: bool) -> None:
    freed = 0
    skipped = 0
    for mode in ("prefix", "postfix"):
        mode_dir = work_root / mode
        if not mode_dir.is_dir():
            continue
        for entry in sorted(mode_dir.iterdir()):
            match = WORK_DIR_RE.match(entry.name)
            if not match:
                continue
            project_id, bug_id, _fixed = match.groups()
            context_path = artifacts_root / mode / f"{project_id}_{bug_id}_{mode}" / "context.json"
            if not context_path.exists():
                skipped += 1
                continue
            size = _dir_size(entry)
            if dry_run:
                print(f"[dry-run] would delete {entry} ({size / 1024 / 1024:.1f} MB)")
            else:
                _force_rmtree(entry)
                print(f"deleted {entry} ({size / 1024 / 1024:.1f} MB)")
            freed += size

    verb = "would free" if dry_run else "freed"
    print(f"\n{verb} {freed / 1024 / 1024 / 1024:.2f} GB total"
          f" ({skipped} in-progress/failed checkout(s) left untouched)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--artifacts-root", type=Path, default=Path(".dist/study/artifacts_v2"))
    parser.add_argument("--work-root", type=Path, default=Path(".dist/study/work_v2"))
    parser.add_argument("--dry-run", action="store_true", help="List what would be deleted without deleting.")
    args = parser.parse_args()
    sweep(args.artifacts_root, args.work_root, args.dry_run)
