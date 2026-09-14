"""Split a study manifest into N disjoint manifests over NOT-yet-collected
bugs, so multiple study-collect processes can run in parallel against the
same --artifacts-root without ever touching the same bug's checkout at once.

Does not touch the pipeline — just slices the existing manifest JSON.

Usage:
    python scripts/split_manifest.py --manifest .dist/study/manifest_closure174.json \
        --artifacts-root .dist/study/artifacts_v2 --workers 3
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def already_done(entry: dict, artifacts_root: Path) -> bool:
    project = entry["project_id"]
    bug = entry["bug_id"]
    prefix_ctx = artifacts_root / "prefix" / f"{project}_{bug}_prefix" / "context.json"
    postfix_ctx = artifacts_root / "postfix" / f"{project}_{bug}_postfix" / "context.json"
    return prefix_ctx.exists() and postfix_ctx.exists()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--artifacts-root", type=Path, required=True)
    parser.add_argument("--workers", type=int, required=True)
    parser.add_argument("--out-prefix", default=None, help="Defaults to <manifest stem>_worker")
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    remaining = [e for e in manifest["entries"] if not already_done(e, args.artifacts_root)]
    done_count = len(manifest["entries"]) - len(remaining)
    print(f"{done_count}/{len(manifest['entries'])} bugs already fully collected (both modes) — excluded.")
    print(f"{len(remaining)} bugs remaining, splitting into {args.workers} manifests.")

    out_prefix = args.out_prefix or f"{args.manifest.stem}_worker"
    chunk_size = -(-len(remaining) // args.workers)  # ceil div
    for i in range(args.workers):
        chunk = remaining[i * chunk_size : (i + 1) * chunk_size]
        if not chunk:
            continue
        out_path = args.manifest.parent / f"{out_prefix}{i + 1}.json"
        worker_manifest = dict(manifest)
        worker_manifest["entries"] = chunk
        worker_manifest["target_bugs"] = len(chunk)
        worker_manifest["selected_bugs"] = len(chunk)
        worker_manifest["note"] = (
            f"Auto-split from {args.manifest.name} for parallel collection "
            f"(worker {i + 1}/{args.workers}); bugs already done in "
            f"{args.artifacts_root} excluded."
        )
        out_path.write_text(json.dumps(worker_manifest, indent=2), encoding="utf-8")
        bug_ids = [e["bug_id"] for e in chunk]
        print(f"  {out_path.name}: {len(chunk)} bugs (ids {min(bug_ids)}-{max(bug_ids)})")
