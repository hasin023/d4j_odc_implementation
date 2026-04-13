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
    collect_parser.add_argument("--output", type=Path, required=True, help="Where to write the context JSON.")
    collect_parser.add_argument("--snippet-radius", type=int, default=12)
    collect_parser.add_argument("--skip-coverage", action="store_true")

    # ── classify ─────────────────────────────────────────────────────────
    classify_parser = subparsers.add_parser(
        "classify",
        help="Classify an existing context JSON with an LLM.",
    )
    classify_parser.add_argument("--context", type=Path, required=True, help="Path to context JSON.")
    classify_parser.add_argument("--output", type=Path, required=True, help="Where to write classification JSON.")
    classify_parser.add_argument("--report", type=Path, help="Optional markdown report output path.")
    classify_parser.add_argument("--prompt-output", type=Path, help="Optional path to save rendered prompt messages.")
    classify_parser.add_argument("--prompt-style", choices=["direct", "scientific"], default="scientific")
    _add_llm_args(classify_parser, default_provider, default_model)

    # ── run ───────────────────────────────────────────────────────────────
    run_parser = subparsers.add_parser(
        "run",
        help="End-to-end collection plus classification.",
    )
    _add_common_bug_args(run_parser)
    run_parser.add_argument("--context-output", type=Path, required=True)
    run_parser.add_argument("--classification-output", type=Path, required=True)
    run_parser.add_argument("--report", type=Path, required=True)
    run_parser.add_argument("--prompt-output", type=Path)
    run_parser.add_argument("--snippet-radius", type=int, default=12)
    run_parser.add_argument("--skip-coverage", action="store_true")
    run_parser.add_argument("--prompt-style", choices=["direct", "scientific"], default="scientific")
    _add_llm_args(run_parser, default_provider, default_model)

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
    parser.add_argument("--work-dir", type=Path, required=True, help="Checkout directory for the buggy version.")
    parser.add_argument(
        "--defects4j-cmd",
        default=None,
        help="Optional Defects4J command prefix. Example on Windows: \"perl C:\\\\path\\\\to\\\\defects4j\"",
    )


def _add_llm_args(parser: argparse.ArgumentParser, default_provider: str, default_model: str) -> None:
    parser.add_argument("--provider", default=default_provider, choices=["gemini", "openrouter", "openai-compatible"])
    parser.add_argument("--model", default=default_model)
    parser.add_argument("--api-key-env", default=None)
    parser.add_argument("--base-url")
    parser.add_argument("--dry-run", action="store_true", help="Render the prompt but skip the LLM call.")


def main() -> int:
    load_dotenv()
    parser = build_parser()
    args = parser.parse_args()

    # Initialize rich console (respects --quiet)
    console.init_console(quiet=args.quiet)

    try:
        if args.command == "collect":
            return _cmd_collect(args)
        if args.command == "classify":
            return _cmd_classify(args)
        if args.command == "run":
            return _cmd_run(args)
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


def _cmd_classify(args: argparse.Namespace) -> int:
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


def _cmd_run(args: argparse.Namespace) -> int:
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
