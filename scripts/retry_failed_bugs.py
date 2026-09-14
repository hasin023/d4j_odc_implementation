"""Retry collection for specific bugs that study-collect recorded as failed,
without touching the pipeline or re-running the whole manifest.

Calls the existing single-bug `collect` CLI per bug (same code path
study-collect itself uses under the hood: collect_bug_context), writing
straight into the study artifacts layout so the result is indistinguishable
from what study-collect would have written. Cleans up its own checkout
afterwards (force-delete, since plain rmtree can't remove Defects4J's
read-only git objects on this machine).

Skips a bug entirely if its context.json already exists (idempotent/safe to
re-run).

Usage:
    python scripts/retry_failed_bugs.py --project Closure --bugs 2,3,4,5 --postfix
    python scripts/retry_failed_bugs.py --project Closure --bugs 2,3,4,5 --prefix --postfix
"""
from __future__ import annotations

import argparse
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path


def _force_rmtree(path: Path) -> None:
    def _on_error(func, target, exc_info):
        os.chmod(target, stat.S_IWRITE)
        func(target)

    shutil.rmtree(path, onerror=_on_error)


def retry_one(project: str, bug: int, mode: str, artifacts_root: Path, work_root: Path) -> bool:
    context_path = artifacts_root / mode / f"{project}_{bug}_{mode}" / "context.json"
    if context_path.exists():
        print(f"[skip] {project}-{bug} {mode}: context.json already exists")
        return True

    work_dir = work_root / mode / f"{project}_{bug}b"
    if work_dir.exists():
        # A stale checkout left by a previous failed attempt makes Defects4J
        # refuse to reuse the directory ("not a previously used working
        # directory") — every retry into the same path fails identically
        # until it's cleared first.
        print(f"[clean] removing stale checkout {work_dir}")
        try:
            _force_rmtree(work_dir)
        except OSError as exc:
            print(f"[warn] could not remove stale {work_dir}: {exc}")

    cmd = [
        sys.executable, "-m", "d4j_odc_pipeline", "collect",
        "--project", project, "--bug", str(bug),
        "--output", str(context_path),
        "--work-dir", str(work_dir),
    ]
    if mode == "postfix":
        cmd.append("--include-fix-diff")

    print(f"\n=== {project}-{bug} {mode} ===")
    print(" ".join(cmd))
    result = subprocess.run(cmd)
    ok = result.returncode == 0 and context_path.exists()

    if work_dir.exists():
        try:
            _force_rmtree(work_dir)
        except OSError as exc:
            print(f"[warn] could not clean up {work_dir}: {exc}")

    print(f"[{'ok' if ok else 'FAILED'}] {project}-{bug} {mode} (exit {result.returncode})")
    return ok


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--project", required=True)
    parser.add_argument("--bugs", required=True, help="Comma-separated bug ids, e.g. 2,3,4,5")
    parser.add_argument("--prefix", action="store_true", help="Retry prefix mode too (usually not needed).")
    parser.add_argument("--postfix", action="store_true", help="Retry postfix mode.")
    parser.add_argument("--artifacts-root", type=Path, default=Path(".dist/study/artifacts_v2"))
    parser.add_argument("--work-root", type=Path, default=Path(".dist/study/work_v2"))
    args = parser.parse_args()

    if not args.prefix and not args.postfix:
        parser.error("pass --prefix and/or --postfix")

    bug_ids = [int(b.strip()) for b in args.bugs.split(",") if b.strip()]
    modes = [m for m, flag in (("prefix", args.prefix), ("postfix", args.postfix)) if flag]

    results = {}
    for bug in bug_ids:
        for mode in modes:
            results[(bug, mode)] = retry_one(args.project, bug, mode, args.artifacts_root, args.work_root)

    print("\n=== summary ===")
    for (bug, mode), ok in results.items():
        print(f"{args.project}-{bug} {mode}: {'OK' if ok else 'FAILED'}")
    if not all(results.values()):
        sys.exit(1)
