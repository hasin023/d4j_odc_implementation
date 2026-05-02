from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from . import console
from .defects4j import Defects4JClient, Defects4JError
from .pipeline import classify_bug_context, collect_bug_context, load_context, write_markdown_report


def build_parser() -> argparse.ArgumentParser:
    default_provider = os.environ.get("DEFAULT_LLM_PROVIDER", "gemini")
    default_model = os.environ.get("DEFAULT_LLM_MODEL", "gemini-3.1-flash-lite-preview")
    parser = argparse.ArgumentParser(
        prog="python -m d4j_odc_pipeline",
        description="Defects4J ODC Pipeline — Collect bug context and classify into ODC defect types with an LLM.",
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        default=False,
        help="Suppress all rich console output (for scripting/CI).",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ── collect ──────────────────────────────────────────────────────────
    collect_parser = subparsers.add_parser(
        "collect",
        help="Checkout a buggy Defects4J version and build context JSON.",
    )
    _add_common_bug_args(collect_parser)
    collect_parser.add_argument("--output", type=Path, default=None, help="Where to write the context JSON. Defaults to .dist/runs/<project>_<bug>/context.json.")
    collect_parser.add_argument("--snippet-radius", type=int, default=12)
    collect_parser.add_argument("--skip-coverage", action="store_true")
    collect_parser.add_argument(
        "--include-fix-diff", action="store_true",
        help="Include the buggy->fixed diff as post-fix oracle evidence (improves accuracy but is not pre-fix).",
    )

    # ── classify ─────────────────────────────────────────────────────────
    classify_parser = subparsers.add_parser(
        "classify",
        help="Classify an existing context JSON with an LLM (includes optional ODC opener/closer metadata when inferable).",
    )
    classify_parser.add_argument("--context", type=Path, required=True, help="Path to context JSON.")
    classify_parser.add_argument("--output", type=Path, default=None, help="Where to write classification JSON. Defaults to same directory as --context.")
    classify_parser.add_argument("--report", type=Path, default=None, help="Markdown report output path. Defaults to same directory as --context.")
    classify_parser.add_argument("--prompt-output", type=Path, help="Optional path to save rendered prompt messages.")
    classify_parser.add_argument("--prompt-style", choices=["direct", "scientific", "naive"], default="scientific")
    _add_llm_args(classify_parser, default_provider, default_model)

    # ── run ───────────────────────────────────────────────────────────────
    run_parser = subparsers.add_parser(
        "run",
        help="End-to-end collection plus classification.",
    )
    _add_common_bug_args(run_parser)
    run_parser.add_argument("--context-output", type=Path, default=None, help="Defaults to .dist/runs/<project>_<bug>/context.json.")
    run_parser.add_argument("--classification-output", type=Path, default=None, help="Defaults to .dist/runs/<project>_<bug>/classification.json.")
    run_parser.add_argument("--report", type=Path, default=None, help="Defaults to .dist/runs/<project>_<bug>/report.md.")
    run_parser.add_argument("--prompt-output", type=Path)
    run_parser.add_argument("--snippet-radius", type=int, default=12)
    run_parser.add_argument("--skip-coverage", action="store_true")
    run_parser.add_argument(
        "--include-fix-diff", action="store_true",
        help="Include the buggy->fixed diff as post-fix oracle evidence (improves accuracy but is not pre-fix).",
    )
    run_parser.add_argument("--prompt-style", choices=["direct", "scientific", "naive"], default="scientific")
    _add_llm_args(run_parser, default_provider, default_model)

    # ── compare ───────────────────────────────────────────────────────────
    compare_parser = subparsers.add_parser(
        "compare",
        help="Compare a pre-fix and post-fix classification for accuracy evaluation.",
    )
    compare_parser.add_argument("--prefix", type=Path, required=True,
                                help="Path to pre-fix classification JSON.")
    compare_parser.add_argument("--postfix", type=Path, required=True,
                                help="Path to post-fix classification JSON.")
    compare_parser.add_argument("--output", type=Path, required=True,
                                help="Path to write comparison JSON.")
    compare_parser.add_argument("--report", type=Path,
                                help="Optional markdown comparison report.")

    # ── compare-batch ─────────────────────────────────────────────────────
    batch_parser = subparsers.add_parser(
        "compare-batch",
        help="Batch compare multiple pre-fix/post-fix classification pairs.",
    )
    batch_parser.add_argument("--prefix-dir", type=Path, required=True,
                              help="Directory containing *_prefix/classification.json files.")
    batch_parser.add_argument("--postfix-dir", type=Path, required=True,
                              help="Directory containing *_postfix/classification.json files.")
    batch_parser.add_argument("--output", type=Path, required=True,
                              help="Path to write batch comparison JSON.")
    batch_parser.add_argument("--report", type=Path,
                              help="Optional markdown batch report.")

    # ── multifault ──────────────────────────────────────────────────────
    mf_parser = subparsers.add_parser(
        "multifault",
        help="Query multi-fault data from defects4j-mf for a single bug version.",
    )
    mf_parser.add_argument("--project", "-p", required=True,
                           help="Defects4J project id (Chart, Closure, Lang, Math, Time).")
    mf_parser.add_argument("--bug", "-b", type=int, required=True,
                           help="Defects4J bug id.")
    mf_parser.add_argument("--fault-data-dir", type=Path, default=None,
                           help="Path to fault_data/ directory. Defaults to MULTIFAULT_DATA_DIR env or implementation/fault_data/.")
    mf_parser.add_argument("--output", type=Path,
                           help="Optional path to write multi-fault summary JSON.")

    # ── multifault-enrich ───────────────────────────────────────────────
    mfe_parser = subparsers.add_parser(
        "multifault-enrich",
        help="Enrich an existing classification JSON with multi-fault context.",
    )
    mfe_parser.add_argument("--classification", type=Path, required=True,
                            help="Path to existing classification.json.")
    mfe_parser.add_argument("--fault-data-dir", type=Path, default=None,
                            help="Path to fault_data/ directory.")
    mfe_parser.add_argument("--output", type=Path, default=None,
                            help="Path to write enriched classification JSON. Defaults to classification_enriched.json alongside input.")

    # ── study-plan ──────────────────────────────────────────────────────
    plan_parser = subparsers.add_parser(
        "study-plan",
        help="Generate a balanced bug manifest for large-scale pre/post studies.",
    )
    plan_parser.add_argument("--output", type=Path, default=None, help="Path to write study manifest JSON. Defaults to .dist/study/manifest_<target_bugs>.json.")
    plan_parser.add_argument("--target-bugs", type=int, default=68,
                             help="Target number of bugs to include (recommended 50-70).")
    plan_parser.add_argument("--min-per-project", type=int, default=1,
                             help="Minimum bug count per project to enforce.")
    plan_parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducible sampling.")
    plan_parser.add_argument("--include-deprecated", action="store_true",
                             help="Include deprecated bug IDs while sampling.")
    plan_parser.add_argument("--projects", nargs="+",
                             help="Optional project IDs. Omit to include all Defects4J projects.")
    plan_parser.add_argument("--allow-partial-project-coverage", action="store_true",
                             help="Allow manifests that do not cover all discovered projects.")
    plan_parser.add_argument(
        "--defects4j-cmd",
        default=None,
        help="Optional Defects4J command prefix.",
    )

    # ── study-run ───────────────────────────────────────────────────────
    study_run_parser = subparsers.add_parser(
        "study-run",
        help="Execute prefix and postfix runs for every bug in a study manifest.",
    )
    study_run_parser.add_argument("--manifest", type=Path, required=True, help="Path to study manifest JSON. Bare filenames are resolved under .dist/study/.")
    study_run_parser.add_argument("--artifacts-root", type=Path, default=None,
                                  help="Root directory for generated artifacts. Defaults to .dist/study/artifacts_<target_bugs>.")
    study_run_parser.add_argument("--work-root", type=Path, default=None,
                                  help="Root directory for Defects4J checkouts. Defaults to .dist/study/work.")
    study_run_parser.add_argument("--summary-output", type=Path, default=None,
                                  help="Path to write batch execution summary JSON. Defaults to .dist/study/summary.json.")
    study_run_parser.add_argument("--prompt-style", choices=["direct", "scientific", "naive"], default="scientific")
    study_run_parser.add_argument("--snippet-radius", type=int, default=12)
    study_run_parser.add_argument("--skip-coverage", action="store_true")
    study_run_parser.add_argument("--no-skip-existing", action="store_true",
                                  help="Re-run artifacts even when output files already exist.")
    study_run_parser.add_argument("--prompt-output", action="store_true",
                                  help="Persist prompt JSON for each run.")
    study_run_parser.add_argument("--require-all-projects", action="store_true",
                                  help="Fail when the manifest does not include all discovered projects.")
    study_run_parser.add_argument(
        "--defects4j-cmd",
        default=None,
        help="Optional Defects4J command prefix.",
    )
    _add_llm_args(study_run_parser, default_provider, default_model)

    # ── study-analyze ───────────────────────────────────────────────────
    study_analyze_parser = subparsers.add_parser(
        "study-analyze",
        help="Cross-artifact analysis over prefix/postfix study outputs.",
    )
    study_analyze_parser.add_argument("--prefix-dir", type=Path, default=None,
                                      help="Directory containing *_prefix run folders. Defaults to .dist/study/artifacts_<N>/prefix.")
    study_analyze_parser.add_argument("--postfix-dir", type=Path, default=None,
                                      help="Directory containing *_postfix run folders. Defaults to .dist/study/artifacts_<N>/postfix.")
    study_analyze_parser.add_argument("--output", type=Path, default=None,
                                      help="Path to write analysis JSON. Defaults to .dist/study/analysis_<N>.json.")
    study_analyze_parser.add_argument("--report", type=Path, default=None,
                                      help="Markdown analysis report. Defaults to .dist/study/analysis_<N>.md.")
    study_analyze_parser.add_argument("--manifest", type=Path,
                                      help="Optional manifest JSON to derive expected projects.")
    study_analyze_parser.add_argument("--expected-projects", nargs="+",
                                      help="Optional explicit expected project list.")
    study_analyze_parser.add_argument("--require-all-projects", action="store_true",
                                      help="Fail when analysis does not cover all expected projects.")
    study_analyze_parser.add_argument(
        "--defects4j-cmd",
        default=None,
        help="Optional Defects4J command prefix. Used to infer expected projects if needed.",
    )

    # ── study-baseline ────────────────────────────────────────────────────
    study_baseline_parser = subparsers.add_parser(
        "study-baseline",
        help="Run baseline (direct prompt) classifications for RQ2.2 comparison.",
    )
    study_baseline_parser.add_argument("--manifest", type=Path, required=True,
                                       help="Path to study manifest JSON.")
    study_baseline_parser.add_argument("--baseline-root", type=Path, default=None,
                                       help="Root directory for baseline artifacts. Defaults to .dist/study/baseline_<N>.")
    study_baseline_parser.add_argument("--work-root", type=Path, default=None,
                                       help="Root directory for Defects4J checkouts. Defaults to .dist/study/work.")
    study_baseline_parser.add_argument("--scientific-artifacts-root", type=Path, default=None,
                                       help="Root of scientific artifacts to reuse context.json from.")
    study_baseline_parser.add_argument("--summary-output", type=Path, default=None)
    study_baseline_parser.add_argument("--prompt-style", choices=["direct", "scientific", "naive"], default="direct")
    study_baseline_parser.add_argument("--snippet-radius", type=int, default=12)
    study_baseline_parser.add_argument("--skip-coverage", action="store_true")
    study_baseline_parser.add_argument("--no-skip-existing", action="store_true")
    study_baseline_parser.add_argument("--prompt-output", action="store_true")
    study_baseline_parser.add_argument(
        "--defects4j-cmd", default=None,
        help="Optional Defects4J command prefix.",
    )
    _add_llm_args(study_baseline_parser, default_provider, default_model)

    # ── study-naive ──────────────────────────────────────────────────────
    study_naive_parser = subparsers.add_parser(
        "study-naive",
        help="Run naive (taxonomy-free) classifications for RQ2.3 comparison.",
    )
    study_naive_parser.add_argument("--manifest", type=Path, required=True,
                                     help="Path to study manifest JSON.")
    study_naive_parser.add_argument("--naive-root", type=Path, default=None,
                                     help="Root directory for naive artifacts. Defaults to .dist/study/naive_<N>.")
    study_naive_parser.add_argument("--work-root", type=Path, default=None,
                                     help="Root directory for Defects4J checkouts. Defaults to .dist/study/work.")
    study_naive_parser.add_argument("--scientific-artifacts-root", type=Path, default=None,
                                     help="Root of scientific artifacts to reuse context.json from.")
    study_naive_parser.add_argument("--summary-output", type=Path, default=None)
    study_naive_parser.add_argument("--snippet-radius", type=int, default=12)
    study_naive_parser.add_argument("--skip-coverage", action="store_true")
    study_naive_parser.add_argument("--no-skip-existing", action="store_true")
    study_naive_parser.add_argument("--prompt-output", action="store_true")
    study_naive_parser.add_argument(
        "--defects4j-cmd", default=None,
        help="Optional Defects4J command prefix.",
    )
    _add_llm_args(study_naive_parser, default_provider, default_model)

    # ── study-export ──────────────────────────────────────────────────────
    study_export_parser = subparsers.add_parser(
        "study-export",
        help="Export analysis results as LaTeX tables and/or CSV files.",
    )
    study_export_parser.add_argument("--analysis", type=Path, required=True,
                                     help="Path to analysis JSON.")
    study_export_parser.add_argument("--format", choices=["latex", "csv", "both"], default="both",
                                     dest="export_format")
    study_export_parser.add_argument("--output-dir", type=Path, default=None,
                                     help="Output directory for export files. Defaults to same dir as --analysis.")

    # ── d4j (Defects4J proxy commands) ────────────────────────────────────
    d4j_parser = subparsers.add_parser(
        "d4j",
        help="Defects4J proxy commands with formatted output.",
    )
    d4j_subparsers = d4j_parser.add_subparsers(dest="d4j_command", required=True)

    d4j_subparsers.add_parser("pids", help="List all available Defects4J project IDs.")

    bids_parser = d4j_subparsers.add_parser("bids", help="List bug IDs for a project.")
    bids_parser.add_argument("--project", "-p", required=True, help="Defects4J project id.")
    bids_parser.add_argument("--all", "-A", action="store_true", dest="include_deprecated",
                             help="Include deprecated bug IDs.")

    info_parser = d4j_subparsers.add_parser("info", help="Show project or bug information.")
    info_parser.add_argument("--project", "-p", required=True, help="Defects4J project id.")
    info_parser.add_argument("--bug", "-b", type=int, default=None, help="Optional bug id for detailed info.")

    # Add --defects4j-cmd to d4j parent
    d4j_parser.add_argument(
        "--defects4j-cmd",
        default=None,
        help="Optional Defects4J command prefix.",
    )

    return parser


def _add_common_bug_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--project", required=True, help="Defects4J project id, for example Lang.")
    parser.add_argument("--bug", type=int, required=True, help="Defects4J bug id.")
    parser.add_argument("--work-dir", type=Path, default=None, help="Checkout directory for the buggy version. Defaults to work/<project>_<bug>_prefix (or _postfix with --include-fix-diff).")
    parser.add_argument(
        "--defects4j-cmd",
        default=None,
        help="Optional Defects4J command prefix. Example on Windows: \"perl C:\\\\path\\\\to\\\\defects4j\"",
    )


def _add_llm_args(parser: argparse.ArgumentParser, default_provider: str, default_model: str) -> None:
    parser.add_argument("--provider", default=default_provider, choices=["gemini", "openrouter", "groq", "openai-compatible"])
    parser.add_argument("--model", default=default_model)
    parser.add_argument("--api-key-env", default=None)
    parser.add_argument("--base-url")
    parser.add_argument("--dry-run", action="store_true", help="Render the prompt but skip the LLM call.")


def main() -> int:
    load_dotenv()

    # If no arguments provided, launch the interactive REPL
    if len(sys.argv) == 1:
        from .interactive import launch_repl
        return launch_repl()

    parser = build_parser()
    args = parser.parse_args()

    # Resolve per-provider default model if --model wasn't explicitly given.
    # When the user switches provider (e.g. --provider groq), this auto-selects
    # the provider-specific model from env (e.g. GROQ_MODEL) instead of the
    # global DEFAULT_LLM_MODEL which might be a Gemini model ID.
    if hasattr(args, "provider") and hasattr(args, "model"):
        from .llm import default_model_for_provider
        args.model = default_model_for_provider(args.provider, args.model)

    # Initialize rich console (respects --quiet)
    console.init_console(quiet=args.quiet)

    try:
        if args.command == "collect":
            return _cmd_collect(args)
        if args.command == "classify":
            return _cmd_classify(args)
        if args.command == "run":
            return _cmd_run(args)
        if args.command == "compare":
            return _cmd_compare(args)
        if args.command == "compare-batch":
            return _cmd_compare_batch(args)
        if args.command == "study-plan":
            return _cmd_study_plan(args)
        if args.command == "study-run":
            return _cmd_study_run(args)
        if args.command == "study-analyze":
            return _cmd_study_analyze(args)
        if args.command == "study-baseline":
            return _cmd_study_baseline(args)
        if args.command == "study-export":
            return _cmd_study_export(args)
        if args.command == "study-naive":
            return _cmd_study_naive(args)
        if args.command == "multifault":
            return _cmd_multifault(args)
        if args.command == "multifault-enrich":
            return _cmd_multifault_enrich(args)
        if args.command == "d4j":
            return _cmd_d4j(args)
    except Defects4JError as exc:
        console.error_panel(
            "Defects4J Error",
            str(exc),
            hint="Check that WSL is running and DEFECTS4J_CMD is correct in your .env file.",
        )
        if console.is_quiet():
            print(f"Error: {exc}", file=sys.stderr)
        return 1
    except FileNotFoundError as exc:
        console.error_panel("File Not Found", str(exc))
        if console.is_quiet():
            print(f"Error: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        console.error_panel(
            "Value Error",
            str(exc),
            hint="This may indicate an issue with the LLM response format.",
        )
        if console.is_quiet():
            print(f"Error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        console.warn("Interrupted by user")
        return 130
    return 0


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

def _cmd_collect(args: argparse.Namespace) -> int:
    client = Defects4JClient(command=args.defects4j_cmd)
    mode_suffix = "postfix" if args.include_fix_diff else "prefix"
    # Default work-dir to work/<project>_<bug>_<mode>
    if args.work_dir is None:
        args.work_dir = Path("work") / f"{args.project}_{args.bug}_{mode_suffix}"
    # Default output to .dist/runs/<project>_<bug>_<mode>/context.json
    if args.output is None:
        args.output = Path(".dist") / "runs" / f"{args.project}_{args.bug}_{mode_suffix}" / "context.json"
    collect_bug_context(
        defects4j=client,
        project_id=args.project,
        bug_id=args.bug,
        work_dir=args.work_dir,
        output_path=args.output,
        snippet_radius=args.snippet_radius,
        run_coverage=not args.skip_coverage,
        include_fix_diff=args.include_fix_diff,
    )
    return 0


def _cmd_classify(args: argparse.Namespace) -> int:
    context = load_context(args.context)
    # Default output/report to same directory as the context file
    context_dir = args.context.parent
    if args.output is None:
        args.output = context_dir / "classification.json"
    if args.report is None:
        args.report = context_dir / "report.md"
    classification = classify_bug_context(
        context=context,
        prompt_style=args.prompt_style,
        output_path=args.output,
        provider=args.provider,
        model=args.model,
        api_key_env=args.api_key_env,
        base_url=args.base_url,
        prompt_output_path=args.prompt_output,
        dry_run=args.dry_run,
    )
    if args.report:
        write_markdown_report(context=context, classification=classification, output_path=args.report)
    return 0


def _cmd_run(args: argparse.Namespace) -> int:
    client = Defects4JClient(command=args.defects4j_cmd)
    # Default outputs to .dist/runs/<project>_<bug>_<mode>/
    mode_suffix = "postfix" if args.include_fix_diff else "prefix"
    run_dir = Path(".dist") / "runs" / f"{args.project}_{args.bug}_{mode_suffix}"
    # Default work-dir to work/<project>_<bug>_<mode>
    if args.work_dir is None:
        args.work_dir = Path("work") / f"{args.project}_{args.bug}_{mode_suffix}"
    if args.context_output is None:
        args.context_output = run_dir / "context.json"
    if args.classification_output is None:
        args.classification_output = run_dir / "classification.json"
    if args.report is None:
        args.report = run_dir / "report.md"
    context = collect_bug_context(
        defects4j=client,
        project_id=args.project,
        bug_id=args.bug,
        work_dir=args.work_dir,
        output_path=args.context_output,
        snippet_radius=args.snippet_radius,
        run_coverage=not args.skip_coverage,
        include_fix_diff=args.include_fix_diff,
    )
    classification = classify_bug_context(
        context=context,
        prompt_style=args.prompt_style,
        output_path=args.classification_output,
        provider=args.provider,
        model=args.model,
        api_key_env=args.api_key_env,
        base_url=args.base_url,
        prompt_output_path=args.prompt_output,
        dry_run=args.dry_run,
    )
    write_markdown_report(context=context, classification=classification, output_path=args.report)
    return 0


def _cmd_compare(args: argparse.Namespace) -> int:
    import json
    from .comparison import compare_classifications, write_comparison_report
    from .pipeline import write_json

    prefix_data = json.loads(args.prefix.read_text(encoding="utf-8"))
    postfix_data = json.loads(args.postfix.read_text(encoding="utf-8"))

    result = compare_classifications(prefix_data, postfix_data)

    console.header_panel(
        f"Comparison: {result.project_id}-{result.bug_id}",
        f"Pre-fix: {result.prefix_odc_type}  vs  Post-fix: {result.postfix_odc_type}",
    )

    write_json(args.output, result.to_dict())
    console.step(f"Comparison JSON written -> {args.output}")

    if args.report:
        write_comparison_report(result, args.report)
        console.step(f"Comparison report written -> {args.report}")

    strict_icon = "MATCH" if result.strict_match else "MISS"
    top2_icon = "MATCH" if result.top2_match else "MISS"
    family_icon = "MATCH" if result.family_match else "MISS"

    console.result_panel("Comparison complete", [
        ("Pre-fix Type", f"{result.prefix_odc_type} ({result.prefix_confidence:.2f})"),
        ("Post-fix Type", f"{result.postfix_odc_type} ({result.postfix_confidence:.2f})"),
        ("Strict Match", strict_icon),
        ("Top-2 Match", top2_icon),
        ("Family Match", family_icon),
        ("Detail", result.match_detail),
    ])
    return 0


def _cmd_compare_batch(args: argparse.Namespace) -> int:
    import json
    from .comparison import batch_compare, write_comparison_report
    from .pipeline import write_json

    prefix_dir: Path = args.prefix_dir
    postfix_dir: Path = args.postfix_dir

    if not prefix_dir.is_dir():
        console.error_panel("Directory Not Found", f"Pre-fix directory not found: {prefix_dir}")
        return 1
    if not postfix_dir.is_dir():
        console.error_panel("Directory Not Found", f"Post-fix directory not found: {postfix_dir}")
        return 1

    # Auto-discover matching pairs
    # Expected: prefix_dir/ProjectName_BugId_prefix/classification.json
    #           postfix_dir/ProjectName_BugId_postfix/classification.json
    pairs: list[tuple[dict, dict]] = []
    matched_bugs: list[str] = []

    prefix_files: dict[str, Path] = {}
    for child in sorted(prefix_dir.iterdir()):
        if child.is_dir():
            cls_file = child / "classification.json"
            if cls_file.exists():
                key = child.name
                if key.endswith("_prefix"):
                    key = key[:-7]
                prefix_files[key] = cls_file

    for child in sorted(postfix_dir.iterdir()):
        if child.is_dir():
            cls_file = child / "classification.json"
            if cls_file.exists():
                key = child.name
                if key.endswith("_postfix"):
                    key = key[:-8]
                if key in prefix_files:
                    prefix_data = json.loads(prefix_files[key].read_text(encoding="utf-8"))
                    postfix_data = json.loads(cls_file.read_text(encoding="utf-8"))
                    pairs.append((prefix_data, postfix_data))
                    matched_bugs.append(key)

    if not pairs:
        console.warn("No matching pre-fix/post-fix pairs found.")
        console.step(
            "Expected naming: <Project>_<Bug>_prefix/ and <Project>_<Bug>_postfix/ "
            "each containing classification.json"
        )
        return 1

    console.header_panel(
        f"Batch Comparison: {len(pairs)} bug(s)",
        f"Bugs: {', '.join(matched_bugs)}",
    )

    result = batch_compare(pairs)

    write_json(args.output, result.to_dict())
    console.step(f"Batch comparison JSON written -> {args.output}")

    if args.report:
        write_comparison_report(result, args.report)
        console.step(f"Batch comparison report written -> {args.report}")

    kappa_str = f"{result.cohens_kappa:.3f}" if result.cohens_kappa is not None else "N/A"

    console.result_panel("Batch Comparison complete", [
        ("Total Bugs", str(result.total_bugs)),
        ("Strict Match", f"{result.strict_match_rate:.0%} ({result.strict_match_count}/{result.total_bugs})"),
        ("Top-2 Match", f"{result.top2_match_rate:.0%} ({result.top2_match_count}/{result.total_bugs})"),
        ("Family Match", f"{result.family_match_rate:.0%} ({result.family_match_count}/{result.total_bugs})"),
        ("Cohen's Kappa", kappa_str),
    ])
    return 0


def _cmd_multifault(args: argparse.Namespace) -> int:
    from .multifault import get_multifault_summary, SUPPORTED_PROJECTS
    from .pipeline import write_json

    project = args.project
    bug_id = args.bug
    fault_data_dir = args.fault_data_dir

    console.header_panel(
        f"Multi-Fault Query: {project}-{bug_id}",
        f"Supported projects: {', '.join(sorted(SUPPORTED_PROJECTS))}",
    )

    summary = get_multifault_summary(project, bug_id, fault_data_dir)

    if not summary.data_available:
        for note in summary.notes:
            console.warn(note)
        return 1

    result_rows = [
        ("Project", summary.project_id),
        ("Bug ID", str(summary.bug_id)),
        ("Version", summary.version_id),
        ("Total Co-existing Faults", str(summary.total_coexisting_faults)),
        ("Fault IDs", ", ".join(str(f) for f in summary.coexisting_fault_ids)),
    ]

    # Show fault details
    for fault in summary.coexisting_faults:
        tests_str = "; ".join(fault.triggering_tests[:3])
        if len(fault.triggering_tests) > 3:
            tests_str += f" (+{len(fault.triggering_tests) - 3} more)"
        loc_str = "; ".join(f"{loc.file_path}:{loc.lines}" for loc in fault.locations[:3])
        if len(fault.locations) > 3:
            loc_str += f" (+{len(fault.locations) - 3} more)"
        result_rows.append((f"Fault #{fault.fault_id}", f"tests=[{tests_str}] locs=[{loc_str}]"))

    console.result_panel(f"Multi-Fault Summary: {project}-{bug_id}", result_rows)

    for note in summary.notes:
        console.step(note)

    if args.output:
        write_json(args.output, summary.to_dict())
        console.step(f"Summary JSON written -> {args.output}")

    return 0


def _cmd_multifault_enrich(args: argparse.Namespace) -> int:
    import json as json_mod
    from .multifault import enrich_classification
    from .pipeline import write_json

    cls_path: Path = args.classification
    if not cls_path.exists():
        console.error_panel("File Not Found", f"Classification file not found: {cls_path}")
        return 1

    # Default output to classification_enriched.json alongside input
    if args.output is None:
        args.output = cls_path.parent / "classification_enriched.json"

    classification = json_mod.loads(cls_path.read_text(encoding="utf-8"))
    project = classification.get("project_id", "")
    bug_id = classification.get("bug_id", 0)

    console.header_panel(
        f"Multi-Fault Enrichment: {project}-{bug_id}",
        f"Source: {cls_path}",
    )

    enriched = enrich_classification(classification, args.fault_data_dir)
    mf_ctx = enriched.get("multifault_context", {})

    write_json(args.output, enriched)

    console.result_panel(f"Enrichment Complete: {project}-{bug_id}", [
        ("Data Available", str(mf_ctx.get("data_available", False))),
        ("Co-existing Faults", str(mf_ctx.get("total_coexisting_faults", 0))),
        ("Fault IDs", ", ".join(str(f) for f in mf_ctx.get("coexisting_fault_ids", []))),
        ("Output", str(args.output)),
    ])

    for note in mf_ctx.get("notes", []):
        console.step(note)

    return 0


def _cmd_study_plan(args: argparse.Namespace) -> int:
    from .batch import generate_study_manifest

    client = Defects4JClient(command=args.defects4j_cmd)
    discovered_projects = sorted(client.pids())

    # Default output to .dist/study/manifest_<target_bugs>.json
    if args.output is None:
        args.output = Path(".dist") / "study" / f"manifest_{args.target_bugs}.json"
    elif not args.output.parent.parts:
        # Bare filename — resolve under .dist/study/
        args.output = Path(".dist") / "study" / args.output

    manifest = generate_study_manifest(
        defects4j=client,
        output_path=args.output,
        target_bugs=args.target_bugs,
        min_per_project=args.min_per_project,
        include_deprecated=args.include_deprecated,
        seed=args.seed,
        projects=args.projects,
    )

    covered_projects = set(manifest.get("projects_covered", []))
    expected_projects = set(args.projects) if args.projects else set(discovered_projects)
    missing_projects = sorted(expected_projects - covered_projects)

    if missing_projects and not args.allow_partial_project_coverage:
        raise ValueError(
            "Study manifest does not cover all requested projects. "
            f"Missing: {', '.join(missing_projects)}"
        )

    console.result_panel("Study plan generated", [
        ("Output", str(args.output)),
        ("Target bugs", str(manifest.get("target_bugs"))),
        ("Selected bugs", str(manifest.get("selected_bugs"))),
        ("Projects covered", str(len(covered_projects))),
        ("Missing projects", ", ".join(missing_projects) if missing_projects else "none"),
    ])
    return 0


def _cmd_study_run(args: argparse.Namespace) -> int:
    from .batch import install_signal_handlers, load_manifest, reset_shutdown, run_batch_from_manifest
    from .pipeline import write_json

    # Install signal handlers for graceful Ctrl+C
    install_signal_handlers()
    reset_shutdown()

    # Resolve bare manifest filename under .dist/study/
    if args.manifest and not args.manifest.parent.parts:
        args.manifest = Path(".dist") / "study" / args.manifest

    client = Defects4JClient(command=args.defects4j_cmd)
    manifest = load_manifest(args.manifest)

    # Derive target_bugs from manifest for default folder naming
    target_bugs = manifest.get("target_bugs", manifest.get("selected_bugs", 0))

    # Default output paths to .dist/study/ with target_bugs suffix
    dist_study = Path(".dist") / "study"
    if args.artifacts_root is None:
        args.artifacts_root = dist_study / f"artifacts_{target_bugs}"
    if args.work_root is None:
        args.work_root = dist_study / "work"
    if args.summary_output is None:
        args.summary_output = dist_study / "summary.json"

    console.header_panel("Study Run Configuration", None)
    console.step(f"Manifest: {args.manifest}")
    console.step(f"Artifacts: {args.artifacts_root}")
    console.step(f"Work dir: {args.work_root}")
    console.step(f"Summary: {args.summary_output}")
    console.step("Ctrl+C to gracefully stop and save checkpoint")

    if args.require_all_projects:
        expected_projects = set(client.pids())
        covered_projects = set(manifest.get("projects_covered", []))
        missing_projects = sorted(expected_projects - covered_projects)
        if missing_projects:
            raise ValueError(
                "Manifest is missing project coverage required for this run: "
                + ", ".join(missing_projects)
            )

    summary = run_batch_from_manifest(
        defects4j=client,
        manifest=manifest,
        artifacts_root=args.artifacts_root,
        work_root=args.work_root,
        provider=args.provider,
        model=args.model,
        api_key_env=args.api_key_env,
        base_url=args.base_url,
        prompt_style=args.prompt_style,
        snippet_radius=args.snippet_radius,
        run_coverage=not args.skip_coverage,
        skip_existing=not args.no_skip_existing,
        prompt_output=args.prompt_output,
    )

    write_json(args.summary_output, summary)

    status_label = "Study run interrupted (checkpoint saved)" if summary.get("interrupted") else "Study run complete"
    console.result_panel(status_label, [
        ("Summary", str(args.summary_output)),
        ("Total entries", str(summary.get("total_entries", 0))),
        ("Completed", str(summary.get("completed_entries", 0))),
        ("Interrupted", "Yes" if summary.get("interrupted") else "No"),
        ("Prefix ready", str(summary.get("prefix_ok", 0))),
        ("Postfix ready", str(summary.get("postfix_ok", 0))),
        ("Paired compare", str(summary.get("paired_for_compare", 0))),
        ("Projects covered", str(len(summary.get("projects_covered", [])))),
    ])
    return 0


def _cmd_study_analyze(args: argparse.Namespace) -> int:
    from .batch import analyze_batch_artifacts, load_manifest, write_analysis_markdown
    from .pipeline import write_json

    # Resolve bare manifest filename under .dist/study/
    if args.manifest and not args.manifest.parent.parts:
        args.manifest = Path(".dist") / "study" / args.manifest

    # Derive target_bugs from manifest for default paths
    target_bugs: int | str = ""
    if args.manifest and args.manifest.exists():
        manifest = load_manifest(args.manifest)
        target_bugs = manifest.get("target_bugs", manifest.get("selected_bugs", ""))
    else:
        manifest = None

    dist_study = Path(".dist") / "study"

    # Default prefix/postfix dirs from artifacts_<N>/
    if args.prefix_dir is None:
        artifacts_folder = f"artifacts_{target_bugs}" if target_bugs else "artifacts"
        args.prefix_dir = dist_study / artifacts_folder / "prefix"
    if args.postfix_dir is None:
        artifacts_folder = f"artifacts_{target_bugs}" if target_bugs else "artifacts"
        args.postfix_dir = dist_study / artifacts_folder / "postfix"

    # Default output/report with _<N> suffix
    if args.output is None:
        suffix = f"_{target_bugs}" if target_bugs else ""
        args.output = dist_study / f"analysis{suffix}.json"
    elif not args.output.parent.parts:
        args.output = dist_study / args.output

    if args.report is None:
        suffix = f"_{target_bugs}" if target_bugs else ""
        args.report = dist_study / f"analysis{suffix}.md"
    elif not args.report.parent.parts:
        args.report = dist_study / args.report

    expected_projects: list[str] | None = None
    if args.expected_projects:
        expected_projects = sorted(set(args.expected_projects))
    elif manifest:
        expected_projects = sorted(set(manifest.get("projects_requested", [])))
    elif args.require_all_projects:
        client = Defects4JClient(command=args.defects4j_cmd)
        expected_projects = sorted(client.pids())

    summary = analyze_batch_artifacts(
        prefix_dir=args.prefix_dir,
        postfix_dir=args.postfix_dir,
        expected_projects=expected_projects,
    )

    if args.require_all_projects and summary.get("missing_projects"):
        raise ValueError(
            "Analysis failed all-project requirement. Missing projects: "
            + ", ".join(summary["missing_projects"])
        )

    write_json(args.output, summary)
    if args.report:
        write_analysis_markdown(summary, args.report)

    console.result_panel("Study analysis complete", [
        ("Output", str(args.output)),
        ("Report", str(args.report)),
        ("Total pairs", str(summary.get("total_pairs", 0))),
        ("Projects seen", str(summary.get("unique_projects", 0))),
        ("Missing projects", ", ".join(summary.get("missing_projects", [])) or "none"),
        ("Type changed", str(summary.get("type_changed_count", 0))),
    ])
    return 0


def _cmd_study_baseline(args: argparse.Namespace) -> int:
    from .batch import install_signal_handlers, load_manifest, reset_shutdown, run_baseline_from_manifest
    from .pipeline import write_json

    install_signal_handlers()
    reset_shutdown()

    # Resolve bare manifest filename under .dist/study/
    if args.manifest and not args.manifest.parent.parts:
        args.manifest = Path(".dist") / "study" / args.manifest

    client = Defects4JClient(command=args.defects4j_cmd)
    manifest = load_manifest(args.manifest)
    target_bugs = manifest.get("target_bugs", manifest.get("selected_bugs", 0))
    dist_study = Path(".dist") / "study"

    if args.baseline_root is None:
        args.baseline_root = dist_study / f"baseline_{target_bugs}"
    if args.work_root is None:
        args.work_root = dist_study / "work"
    if args.summary_output is None:
        args.summary_output = dist_study / "baseline_summary.json"

    console.header_panel("Study Baseline Configuration", None)
    console.step(f"Manifest: {args.manifest}")
    console.step(f"Baseline root: {args.baseline_root}")
    console.step(f"Prompt style: {args.prompt_style}")
    console.step(f"Reuse context from: {args.scientific_artifacts_root or '(none — will collect fresh)'}")

    summary = run_baseline_from_manifest(
        defects4j=client,
        manifest=manifest,
        baseline_root=args.baseline_root,
        work_root=args.work_root,
        scientific_artifacts_root=args.scientific_artifacts_root,
        provider=args.provider,
        model=args.model,
        api_key_env=args.api_key_env,
        base_url=args.base_url,
        prompt_style=args.prompt_style,
        snippet_radius=args.snippet_radius,
        run_coverage=not args.skip_coverage,
        skip_existing=not args.no_skip_existing,
        prompt_output=args.prompt_output,
    )

    write_json(args.summary_output, summary)

    status_label = "Baseline run interrupted" if summary.get("interrupted") else "Baseline run complete"
    console.result_panel(status_label, [
        ("Summary", str(args.summary_output)),
        ("Prompt style", summary.get("prompt_style", "")),
        ("Completed", str(summary.get("completed_entries", 0))),
        ("Reused context", str(summary.get("reused_context_count", 0))),
    ])
    return 0


def _cmd_study_naive(args: argparse.Namespace) -> int:
    from .batch import install_signal_handlers, load_manifest, reset_shutdown, run_baseline_from_manifest
    from .pipeline import write_json

    install_signal_handlers()
    reset_shutdown()

    # Resolve bare manifest filename under .dist/study/
    if args.manifest and not args.manifest.parent.parts:
        args.manifest = Path(".dist") / "study" / args.manifest

    client = Defects4JClient(command=args.defects4j_cmd)
    manifest = load_manifest(args.manifest)
    target_bugs = manifest.get("target_bugs", manifest.get("selected_bugs", 0))
    dist_study = Path(".dist") / "study"

    if args.naive_root is None:
        args.naive_root = dist_study / f"naive_{target_bugs}"
    if args.work_root is None:
        args.work_root = dist_study / "work"
    if args.summary_output is None:
        args.summary_output = dist_study / "naive_summary.json"

    console.header_panel("Study Naive (Taxonomy-Free) Configuration", None)
    console.step(f"Manifest: {args.manifest}")
    console.step(f"Naive root: {args.naive_root}")
    console.step(f"Prompt style: naive (no ODC taxonomy)")
    console.step(f"Reuse context from: {args.scientific_artifacts_root or '(none — will collect fresh)'}")

    summary = run_baseline_from_manifest(
        defects4j=client,
        manifest=manifest,
        baseline_root=args.naive_root,
        work_root=args.work_root,
        scientific_artifacts_root=args.scientific_artifacts_root,
        provider=args.provider,
        model=args.model,
        api_key_env=args.api_key_env,
        base_url=args.base_url,
        prompt_style="naive",
        snippet_radius=args.snippet_radius,
        run_coverage=not args.skip_coverage,
        skip_existing=not args.no_skip_existing,
        prompt_output=args.prompt_output,
    )

    write_json(args.summary_output, summary)

    status_label = "Naive run interrupted" if summary.get("interrupted") else "Naive run complete"
    console.result_panel(status_label, [
        ("Summary", str(args.summary_output)),
        ("Prompt style", "naive (taxonomy-free)"),
        ("Completed", str(summary.get("completed_entries", 0))),
        ("Reused context", str(summary.get("reused_context_count", 0))),
    ])
    return 0


def _cmd_study_export(args: argparse.Namespace) -> int:
    import json as json_mod
    from .results_export import (
        export_accuracy_table_latex,
        export_baseline_comparison_latex,
        export_confusion_matrix_latex,
        export_per_project_kappa_latex,
        export_type_distribution_latex,
        export_all_csv,
    )

    analysis_path: Path = args.analysis
    if not analysis_path.exists():
        console.error_panel("File Not Found", f"Analysis file not found: {analysis_path}")
        return 1

    analysis = json_mod.loads(analysis_path.read_text(encoding="utf-8"))
    output_dir = args.output_dir or analysis_path.parent

    written: list[str] = []

    if args.export_format in ("latex", "both"):
        latex_dir = output_dir / "latex"
        latex_dir.mkdir(parents=True, exist_ok=True)

        tables = [
            ("type_distribution.tex", export_type_distribution_latex),
            ("accuracy.tex", export_accuracy_table_latex),
            ("confusion_matrix.tex", export_confusion_matrix_latex),
            ("per_project_kappa.tex", export_per_project_kappa_latex),
        ]
        if analysis.get("baseline_comparison"):
            tables.append(("baseline_comparison.tex", export_baseline_comparison_latex))

        for filename, func in tables:
            try:
                content = func(analysis)
                (latex_dir / filename).write_text(content, encoding="utf-8")
                written.append(f"latex/{filename}")
            except Exception as exc:  # noqa: BLE001
                console.warn(f"Skipped {filename}: {exc}")

    if args.export_format in ("csv", "both"):
        csv_dir = output_dir / "csv"
        csv_files = export_all_csv(analysis, csv_dir)
        written.extend(f"csv/{p.name}" for p in csv_files)

    console.result_panel("Export complete", [
        ("Output directory", str(output_dir)),
        ("Files written", str(len(written))),
    ])
    for w in written:
        console.step(f"  {w}")
    return 0


def _cmd_d4j(args: argparse.Namespace) -> int:
    client = Defects4JClient(command=args.defects4j_cmd)

    if args.d4j_command == "pids":
        return _d4j_pids(client)
    if args.d4j_command == "bids":
        return _d4j_bids(client, args)
    if args.d4j_command == "info":
        return _d4j_info(client, args)
    return 0


# ---------------------------------------------------------------------------
# d4j subcommand handlers
# ---------------------------------------------------------------------------

def _d4j_pids(client: Defects4JClient) -> int:
    with console.spinner_step("Fetching project IDs"):
        projects = client.pids()

    if not projects:
        console.warn("No project IDs returned")
        return 1

    console.print_table(
        "Defects4J Projects",
        ["#", "Project ID"],
        [[str(i + 1), pid] for i, pid in enumerate(projects)],
    )
    console.success(f"{len(projects)} project(s) available")
    return 0


def _d4j_bids(client: Defects4JClient, args: argparse.Namespace) -> int:
    label = f"bug IDs for {args.project}"
    if args.include_deprecated:
        label += " (including deprecated)"

    with console.spinner_step(f"Fetching {label}"):
        bugs = client.bids(args.project, include_deprecated=args.include_deprecated)

    if not bugs:
        console.warn(f"No bug IDs returned for project {args.project}")
        return 1

    # Display in a compact multi-column format
    console.header_panel(f"Bug IDs: {args.project}", f"{len(bugs)} bug(s)")

    # Group into rows of 15 for display
    row_size = 15
    rows: list[list[str]] = []
    for i in range(0, len(bugs), row_size):
        rows.append([", ".join(bugs[i:i + row_size])])

    console.print_table(
        f"{args.project} Bug IDs",
        ["IDs"],
        rows,
    )
    console.success(f"{len(bugs)} bug(s) found")
    return 0


def _d4j_info(client: Defects4JClient, args: argparse.Namespace) -> int:
    target = f"{args.project}" + (f"-{args.bug}" if args.bug else "")

    with console.spinner_step(f"Fetching info for {target}"):
        info_text = client.info(args.project, bug_id=args.bug)

    if not info_text:
        console.warn(f"No info returned for {target}")
        return 1

    console.header_panel(f"Info: {target}", None)

    # Print the raw info text (Defects4J already formats it nicely)
    con = console.get_console()
    if con is not None:
        con.print()
        for line in info_text.splitlines():
            con.print(f"  {line}")
        con.print()
    else:
        print(info_text)

    return 0


# ---------------------------------------------------------------------------
# Dotenv loader
# ---------------------------------------------------------------------------

def load_dotenv(path: Path | None = None) -> None:
    dotenv_path = path or Path(".env")
    if not dotenv_path.exists():
        return
    for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key or key in os.environ:
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        os.environ[key] = value
