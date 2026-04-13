from __future__ import annotations

import argparse
from pathlib import Path

from .defects4j import Defects4JClient, Defects4JError
from .pipeline import classify_bug_context, collect_bug_context, load_context, write_markdown_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m d4j_odc_pipeline",
        description="Collect Defects4J bug context and classify it into ODC defect types with an LLM.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    collect_parser = subparsers.add_parser("collect", help="Checkout a buggy Defects4J version and build context JSON.")
    _add_common_bug_args(collect_parser)
    collect_parser.add_argument("--output", type=Path, required=True, help="Where to write the context JSON.")
    collect_parser.add_argument("--snippet-radius", type=int, default=12)
    collect_parser.add_argument("--skip-coverage", action="store_true")

    classify_parser = subparsers.add_parser("classify", help="Classify an existing context JSON with an LLM.")
    classify_parser.add_argument("--context", type=Path, required=True, help="Path to context JSON.")
    classify_parser.add_argument("--output", type=Path, required=True, help="Where to write classification JSON.")
    classify_parser.add_argument("--report", type=Path, help="Optional markdown report output path.")
    classify_parser.add_argument("--prompt-output", type=Path, help="Optional path to save rendered prompt messages.")
    classify_parser.add_argument("--prompt-style", choices=["direct", "scientific"], default="scientific")
    classify_parser.add_argument("--provider", default="openai-compatible")
    classify_parser.add_argument("--model", required=True)
    classify_parser.add_argument("--api-key-env", default="OPENAI_API_KEY")
    classify_parser.add_argument("--base-url")
    classify_parser.add_argument("--dry-run", action="store_true", help="Render the prompt but skip the LLM call.")

    run_parser = subparsers.add_parser("run", help="End-to-end collection plus classification.")
    _add_common_bug_args(run_parser)
    run_parser.add_argument("--context-output", type=Path, required=True)
    run_parser.add_argument("--classification-output", type=Path, required=True)
    run_parser.add_argument("--report", type=Path, required=True)
    run_parser.add_argument("--prompt-output", type=Path)
    run_parser.add_argument("--snippet-radius", type=int, default=12)
    run_parser.add_argument("--skip-coverage", action="store_true")
    run_parser.add_argument("--prompt-style", choices=["direct", "scientific"], default="scientific")
    run_parser.add_argument("--provider", default="openai-compatible")
    run_parser.add_argument("--model", required=True)
    run_parser.add_argument("--api-key-env", default="OPENAI_API_KEY")
    run_parser.add_argument("--base-url")
    run_parser.add_argument("--dry-run", action="store_true")
    return parser


def _add_common_bug_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--project", required=True, help="Defects4J project id, for example Lang.")
    parser.add_argument("--bug", type=int, required=True, help="Defects4J bug id.")
    parser.add_argument("--work-dir", type=Path, required=True, help="Checkout directory for the buggy version.")
    parser.add_argument(
        "--defects4j-cmd",
        default=None,
        help="Optional Defects4J command prefix. Example on Windows: \"perl C:\\\\path\\\\to\\\\defects4j\"",
    )


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.command == "collect":
            client = Defects4JClient(command=args.defects4j_cmd)
            collect_bug_context(
                defects4j=client,
                project_id=args.project,
                bug_id=args.bug,
                work_dir=args.work_dir,
                output_path=args.output,
                snippet_radius=args.snippet_radius,
                run_coverage=not args.skip_coverage,
            )
            return 0

        if args.command == "classify":
            context = load_context(args.context)
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

        if args.command == "run":
            client = Defects4JClient(command=args.defects4j_cmd)
            context = collect_bug_context(
                defects4j=client,
                project_id=args.project,
                bug_id=args.bug,
                work_dir=args.work_dir,
                output_path=args.context_output,
                snippet_radius=args.snippet_radius,
                run_coverage=not args.skip_coverage,
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
    except (Defects4JError, FileNotFoundError, ValueError) as exc:
        parser.exit(status=1, message=f"{exc}\n")
    return 0
