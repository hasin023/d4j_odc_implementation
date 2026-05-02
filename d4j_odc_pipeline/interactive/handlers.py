"""Command handler implementations for every slash command."""
from __future__ import annotations

import json
import os
import signal
import shlex
import shutil
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

from rich.console import Console

from . import rendering
from .banner import VERSION
from .completer import (
    discover_classifications,
    discover_context_files,
    discover_manifests,
    pick_file_interactive,
)

if TYPE_CHECKING:
    from .app import ODCApp


# ---------------------------------------------------------------------------
# Session & Config
# ---------------------------------------------------------------------------

def handle_help(app: "ODCApp", args: str) -> None:
    from .commands import COMMAND_REGISTRY
    rendering.render_help_table(app.console, COMMAND_REGISTRY)


def handle_status(app: "ODCApp", args: str) -> None:
    rendering.render_status_panel(app.console, app.state)


def handle_config(app: "ODCApp", args: str) -> None:
    parts = args.split(None, 1)
    if not parts:
        handle_status(app, "")
        return
    key = parts[0]
    value = parts[1] if len(parts) > 1 else None
    config_map = {
        "provider": ("provider", str),
        "model": ("model", str),
        "skip-coverage": ("skip_coverage", lambda v: v.lower() in ("true", "1", "yes")),
        "include-fix-diff": ("include_fix_diff", lambda v: v.lower() in ("true", "1", "yes")),
        "prompt-style": ("prompt_style", str),
        "snippet-radius": ("snippet_radius", int),
    }
    if key not in config_map:
        app.console.print(f"[red]Unknown config key: {key}[/red]")
        app.console.print(f"[dim]Available: {', '.join(config_map)}[/dim]")
        return
    attr, converter = config_map[key]
    if value is None:
        app.console.print(f"  {key} = {getattr(app.state, attr)}")
    else:
        try:
            setattr(app.state, attr, converter(value))
            app.console.print(f"  [green]✓[/green] {key} = {getattr(app.state, attr)}")
        except (ValueError, TypeError) as exc:
            app.console.print(f"[red]Invalid value: {exc}[/red]")


def handle_provider(app: "ODCApp", args: str) -> None:
    if not args.strip():
        app.console.print(f"  Provider: [cyan]{app.state.provider}[/cyan]")
        app.console.print("  [dim]Available: gemini, openrouter, groq, openai-compatible[/dim]")
        return
    valid = {"gemini", "openrouter", "groq", "openai-compatible"}
    choice = args.strip()
    if choice not in valid:
        app.console.print(f"[red]Unknown provider: {choice}[/red]")
        return
    app.state.provider = choice
    # Reset model so auto-detection kicks in
    app.state.model = ""
    app.console.print(f"  [green]✓[/green] Provider set to [cyan]{choice}[/cyan] (model will auto-detect)")


def handle_model(app: "ODCApp", args: str) -> None:
    if not args.strip():
        app.console.print(f"  Model: [cyan]{app.state.model or '(auto)'}[/cyan]")
        return
    app.state.model = args.strip()
    app.console.print(f"  [green]✓[/green] Model set to [cyan]{app.state.model}[/cyan]")


def handle_history(app: "ODCApp", args: str) -> None:
    n = int(args.strip()) if args.strip().isdigit() else 20
    history = app.state.command_history[-n:]
    if not history:
        app.console.print("  [dim]No command history yet.[/dim]")
        return
    for i, entry in enumerate(history, 1):
        app.console.print(f"  {i:3d}. [cyan]{entry['cmd']}[/cyan]  [dim]{entry.get('at', '')}[/dim]")


def handle_bugs(app: "ODCApp", args: str) -> None:
    if not app.state.recent_bugs:
        app.console.print("  [dim]No recent bugs. Use /run or /collect to start.[/dim]")
        return
    from rich.table import Table
    table = Table(show_header=True, header_style="bold", expand=False)
    table.add_column("#", style="dim")
    table.add_column("Project", style="cyan")
    table.add_column("Bug", style="white")
    table.add_column("When", style="dim")
    for i, b in enumerate(app.state.recent_bugs, 1):
        table.add_row(str(i), b["project"], str(b["bug"]), b.get("at", "")[:19])
    app.console.print(table)


def handle_clear(app: "ODCApp", args: str) -> None:
    sub = args.strip().lower()
    if sub == "session":
        app.state.clear()
        app.state.save()
        app.console.print("  [green]✓[/green] Session reset.")
    else:
        os.system("cls" if os.name == "nt" else "clear")


def handle_doctor(app: "ODCApp", args: str) -> None:
    checks: list[tuple[str, bool, str]] = []
    # Python version
    v = sys.version.split()[0]
    checks.append(("Python >= 3.10", sys.version_info >= (3, 10), v))
    # .env file
    env_exists = Path(".env").exists()
    checks.append((".env file", env_exists, str(Path(".env").resolve()) if env_exists else "Not found"))
    # Defects4J
    d4j_cmd = os.environ.get("DEFECTS4J_CMD", "defects4j")
    d4j_ok = shutil.which(d4j_cmd.split()[0]) is not None if " " not in d4j_cmd else True
    checks.append(("Defects4J reachable", d4j_ok, d4j_cmd))
    # API keys
    for env_key in ["GEMINI_API_KEY", "OPENROUTER_API_KEY", "GROQ_API_KEY"]:
        val = os.environ.get(env_key, "")
        checks.append((env_key, bool(val), "set" if val else "NOT SET"))
    # .dist directory
    dist = Path(".dist")
    checks.append((".dist directory", dist.is_dir(), str(dist.resolve()) if dist.is_dir() else "Will be created on first run"))
    # prompt_toolkit
    try:
        import prompt_toolkit
        checks.append(("prompt_toolkit", True, prompt_toolkit.__version__))
    except ImportError:
        checks.append(("prompt_toolkit", False, "NOT INSTALLED"))
    rendering.render_doctor_report(app.console, checks)


def handle_version(app: "ODCApp", args: str) -> None:
    app.console.print(f"  D4J ODC Pipeline  v{VERSION}")
    app.console.print(f"  Python            {sys.version.split()[0]}")


def handle_exit(app: "ODCApp", args: str) -> None:
    raise EOFError  # Caught by the REPL loop


# ---------------------------------------------------------------------------
# Pipeline Commands
# ---------------------------------------------------------------------------

def _resolve_project_bug(app: "ODCApp", args: str) -> tuple[str | None, int | None, str]:
    """Parse --project/--bug from args, falling back to session state.
    Returns (project, bug, remaining_args_str).
    """
    project = app.state.active_project
    bug = app.state.active_bug
    remaining = []
    tokens = shlex.split(args) if args.strip() else []
    i = 0
    while i < len(tokens):
        if tokens[i] in ("--project", "-p") and i + 1 < len(tokens):
            project = tokens[i + 1]; i += 2
        elif tokens[i] in ("--bug", "-b") and i + 1 < len(tokens):
            bug = int(tokens[i + 1]); i += 2
        else:
            remaining.append(tokens[i]); i += 1
    return project, bug, " ".join(remaining)


def _get_client(app: "ODCApp"):
    from ..defects4j import Defects4JClient
    return Defects4JClient(command=os.environ.get("DEFECTS4J_CMD"))


def _get_llm_kwargs(app: "ODCApp") -> dict[str, Any]:
    """Build LLM kwargs from session state."""
    model = app.state.model
    if not model:
        from ..llm import default_model_for_provider
        model = default_model_for_provider(app.state.provider, "")
    return dict(
        provider=app.state.provider,
        model=model,
        api_key_env=None,
        base_url=None,
        dry_run=False,
    )


def _resolve_context_path_input(context_arg: str, runs_base: Path | None = None) -> list[Path]:
    """Resolve a classify argument into one or more candidate context.json paths.

    Supported inputs:
      - direct path to context.json
      - direct path to a run directory containing context.json
      - bare run directory name, e.g. ``Lang_1_prefix``
    """
    raw = context_arg.strip()
    if not raw:
        return []

    runs_base = runs_base or (Path(".dist") / "runs")
    candidates: list[Path] = []

    def _add(path: Path) -> None:
        resolved = path.resolve()
        if resolved.exists() and resolved.is_file() and resolved.name == "context.json" and resolved not in candidates:
            candidates.append(resolved)

    direct = Path(raw)
    if direct.exists():
        if direct.is_dir():
            _add(direct / "context.json")
        else:
            _add(direct)

    if direct.suffix.lower() != ".json":
        _add(runs_base / raw / "context.json")

    for found in discover_context_files(runs_base):
        if found.parent.name == raw:
            _add(found)

    return candidates


def handle_collect(app: "ODCApp", args: str) -> None:
    project, bug, rest = _resolve_project_bug(app, args)
    postfix = "--postfix" in rest or app.state.include_fix_diff
    if not project or bug is None:
        app.console.print("[red]Specify bug: /collect --project Lang --bug 1[/red]")
        return
    mode = "postfix" if postfix else "prefix"
    from ..pipeline import collect_bug_context
    client = _get_client(app)
    work_dir = Path("work") / f"{project}_{bug}_{mode}"
    output = Path(".dist") / "runs" / f"{project}_{bug}_{mode}" / "context.json"
    app.console.print(f"  [cyan]Collecting {project}-{bug} ({mode})...[/cyan]")
    with app.console.status("  Collecting bug evidence...", spinner="dots"):
        collect_bug_context(
            defects4j=client, project_id=project, bug_id=bug,
            work_dir=work_dir, output_path=output,
            snippet_radius=app.state.snippet_radius,
            run_coverage=not app.state.skip_coverage,
            include_fix_diff=postfix,
        )
    app.state.set_active_bug(project, bug)
    app.state.last_context_path = str(output)
    app.state.save()
    app.console.print(f"  [green]✓[/green] Context written → {output}")


def handle_classify(app: "ODCApp", args: str) -> None:
    context_path = args.strip() if args.strip() else None
    if not context_path:
        # Interactive file picker
        files = discover_context_files()
        if not files:
            files = discover_context_files(Path(".dist"))
        if files:
            picked = pick_file_interactive(files, title="Select context.json")
            if picked:
                context_path = str(picked)
        if not context_path and app.state.last_context_path:
            context_path = app.state.last_context_path
    else:
        matches = _resolve_context_path_input(context_path)
        if len(matches) == 1:
            if context_path != str(matches[0]):
                app.console.print(f"  [dim]Resolved to {matches[0]}[/dim]")
            context_path = str(matches[0])
        elif len(matches) > 1:
            picked = pick_file_interactive(matches, title=f"Select context.json for '{context_path}'")
            if picked:
                context_path = str(picked)
    if not context_path:
        app.console.print("[red]No context file found. Run /collect first or specify a path.[/red]")
        return
    path = Path(context_path)
    if not path.exists():
        app.console.print(f"[red]Context not found: {context_path}[/red]")
        app.console.print("  [dim]Tip: use /classify with no arguments for the picker, or pass a run folder like Lang_1_prefix[/dim]")
        return
    if path.is_dir():
        path = path / "context.json"
        if not path.exists():
            app.console.print(f"[red]Directory does not contain context.json: {context_path}[/red]")
            return
    from ..pipeline import classify_bug_context, load_context, write_markdown_report
    context = load_context(path)
    out_dir = path.parent
    cls_output = out_dir / "classification.json"
    report_output = out_dir / "report.md"
    llm = _get_llm_kwargs(app)
    app.console.print(f"  [cyan]Classifying with {llm['provider']}...[/cyan]")
    with app.console.status("  Classifying with LLM...", spinner="dots"):
        classification = classify_bug_context(
            context=context, prompt_style=app.state.prompt_style,
            output_path=cls_output, prompt_output_path=None, **llm,
        )
    write_markdown_report(context=context, classification=classification, output_path=report_output)
    app.state.last_classification_path = str(cls_output)
    app.state.last_report_path = str(report_output)
    app.state.save()
    app.console.print(f"  [green]✓[/green] Classification → {cls_output}")
    # Show result inline
    if classification is not None:
        payload = classification.to_dict() if hasattr(classification, "to_dict") else classification
        if isinstance(payload, dict):
            rendering.render_classification_panel(app.console, payload)


def handle_run(app: "ODCApp", args: str) -> None:
    project, bug, rest = _resolve_project_bug(app, args)
    postfix = "--postfix" in rest or app.state.include_fix_diff
    if not project or bug is None:
        app.console.print("[red]Specify bug: /run --project Lang --bug 1[/red]")
        return
    mode = "postfix" if postfix else "prefix"
    from ..pipeline import classify_bug_context, collect_bug_context, load_context, write_markdown_report
    client = _get_client(app)
    work_dir = Path("work") / f"{project}_{bug}_{mode}"
    run_dir = Path(".dist") / "runs" / f"{project}_{bug}_{mode}"
    ctx_out = run_dir / "context.json"
    cls_out = run_dir / "classification.json"
    rpt_out = run_dir / "report.md"
    llm = _get_llm_kwargs(app)
    app.console.print(f"  [cyan]Running {project}-{bug} ({mode}) with {llm['provider']}...[/cyan]")
    with app.console.status("  Collecting bug evidence...", spinner="dots"):
        context = collect_bug_context(
            defects4j=client, project_id=project, bug_id=bug,
            work_dir=work_dir, output_path=ctx_out,
            snippet_radius=app.state.snippet_radius,
            run_coverage=not app.state.skip_coverage,
            include_fix_diff=postfix,
        )
    app.console.print("  [green]✓[/green] Collection complete")
    with app.console.status("  Classifying with LLM...", spinner="dots"):
        classification = classify_bug_context(
            context=context, prompt_style=app.state.prompt_style,
            output_path=cls_out, prompt_output_path=None, **llm,
        )
    write_markdown_report(context=context, classification=classification, output_path=rpt_out)
    app.state.set_active_bug(project, bug)
    app.state.last_context_path = str(ctx_out)
    app.state.last_classification_path = str(cls_out)
    app.state.last_report_path = str(rpt_out)
    app.state.save()
    app.console.print(f"  [green]✓[/green] Complete → {run_dir}")
    if classification is not None:
        payload = classification.to_dict() if hasattr(classification, "to_dict") else classification
        if isinstance(payload, dict):
            rendering.render_classification_panel(app.console, payload)


def handle_compare(app: "ODCApp", args: str) -> None:
    tokens = shlex.split(args) if args.strip() else []
    prefix_path = postfix_path = output_path = report_path = None
    i = 0
    while i < len(tokens):
        if tokens[i] == "--prefix" and i + 1 < len(tokens):
            prefix_path = tokens[i + 1]; i += 2
        elif tokens[i] == "--postfix" and i + 1 < len(tokens):
            postfix_path = tokens[i + 1]; i += 2
        elif tokens[i] == "--output" and i + 1 < len(tokens):
            output_path = tokens[i + 1]; i += 2
        elif tokens[i] == "--report" and i + 1 < len(tokens):
            report_path = tokens[i + 1]; i += 2
        else:
            i += 1
    if not prefix_path or not postfix_path:
        app.console.print("[red]Usage: /compare --prefix PATH --postfix PATH[/red]")
        return
    from ..comparison import compare_classifications, write_comparison_report
    from ..pipeline import write_json
    pre = json.loads(Path(prefix_path).read_text(encoding="utf-8"))
    post = json.loads(Path(postfix_path).read_text(encoding="utf-8"))
    result = compare_classifications(pre, post)
    if output_path:
        write_json(Path(output_path), result.to_dict())
        app.console.print(f"  [green]✓[/green] Comparison → {output_path}")
    if report_path:
        write_comparison_report(result, Path(report_path))
    from rich.table import Table
    t = Table(show_header=False, box=None, padding=(0, 2))
    t.add_column("K", style="bold white"); t.add_column("V")
    t.add_row("Pre-fix", f"{result.prefix_odc_type} ({result.prefix_confidence:.2f})")
    t.add_row("Post-fix", f"{result.postfix_odc_type} ({result.postfix_confidence:.2f})")
    t.add_row("Strict Match", "✓" if result.strict_match else "✗")
    t.add_row("Family Match", "✓" if result.family_match else "✗")
    app.console.print(t)


def handle_compare_batch(app: "ODCApp", args: str) -> None:
    app.console.print("[dim]Use the script-mode command for batch compare:[/dim]")
    app.console.print("  python -m d4j_odc_pipeline compare-batch --prefix-dir ... --postfix-dir ...")


# ---------------------------------------------------------------------------
# Show / Inspect
# ---------------------------------------------------------------------------

def handle_show(app: "ODCApp", args: str) -> None:
    sub = args.strip().lower()
    if sub == "context":
        path = app.state.last_context_path
        if not path or not Path(path).exists():
            app.console.print("[red]No context available. Run /collect first.[/red]")
            return
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        rendering.render_context_summary(app.console, data)
    elif sub == "classification":
        path = app.state.last_classification_path
        if not path or not Path(path).exists():
            app.console.print("[red]No classification available. Run /classify first.[/red]")
            return
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        rendering.render_classification_panel(app.console, data)
    elif sub == "report":
        path = app.state.last_report_path
        if not path or not Path(path).exists():
            app.console.print("[red]No report available.[/red]")
            return
        md = Path(path).read_text(encoding="utf-8")
        rendering.render_markdown_panel(app.console, md)
    elif sub == "prompt":
        # Look for prompt.json alongside last context
        if app.state.last_context_path:
            prompt_path = Path(app.state.last_context_path).parent / "prompt.json"
            if prompt_path.exists():
                data = json.loads(prompt_path.read_text(encoding="utf-8"))
                rendering.render_json_panel(app.console, data, title="LLM Prompt")
                return
        app.console.print("[dim]No prompt output found. Use --prompt-output when running.[/dim]")
    else:
        app.console.print("[yellow]Usage: /show <context|classification|report|prompt>[/yellow]")


# ---------------------------------------------------------------------------
# Defects4J Proxy
# ---------------------------------------------------------------------------

def handle_d4j(app: "ODCApp", args: str) -> None:
    parts = args.strip().split(None, 1)
    sub = parts[0] if parts else ""
    sub_args = parts[1] if len(parts) > 1 else ""

    if sub == "pids":
        client = _get_client(app)
        pids = client.pids()
        app.console.print(f"  [bold]Defects4J Projects ({len(pids)}):[/bold]")
        for pid in pids:
            app.console.print(f"    - {pid}")

    elif sub == "bids":
        project, _, _ = _resolve_project_bug(app, sub_args)
        if not project:
            app.console.print("[red]Specify project: /d4j bids --project Lang[/red]")
            return
        client = _get_client(app)
        include_deprecated = "--all" in shlex.split(sub_args) if sub_args.strip() else False
        bids = client.bids(project, include_deprecated=include_deprecated)
        app.console.print(f"  [bold]{project} — {len(bids)} bugs:[/bold]")
        # Print in rows of 15
        for i in range(0, len(bids), 15):
            chunk = bids[i:i+15]
            app.console.print("    " + ", ".join(str(b) for b in chunk))

    elif sub == "info":
        project, bug, _ = _resolve_project_bug(app, sub_args)
        if not project:
            app.console.print("[red]Specify: /d4j info --project Lang --bug 1[/red]")
            return
        client = _get_client(app)
        if bug is not None:
            info = client.info(project, bug_id=bug)
            rendering.render_text_panel(app.console, info, title=f"{project}-{bug} Info")
            app.state.set_active_bug(project, bug)
            app.state.save()
        else:
            info = client.info(project)
            rendering.render_text_panel(app.console, info, title=f"{project} Info")
    else:
        app.console.print("[yellow]Usage: /d4j <pids|bids|info> [options][/yellow]")


# ---------------------------------------------------------------------------
# Multi-Fault
# ---------------------------------------------------------------------------

def handle_multifault(app: "ODCApp", args: str) -> None:
    project, bug, _ = _resolve_project_bug(app, args)
    if not project or bug is None:
        app.console.print("[red]Specify: /multifault --project Lang --bug 1[/red]")
        return
    try:
        from ..multifault import get_multifault_summary

        summary = get_multifault_summary(project, bug)
        rendering.render_json_panel(
            app.console,
            summary.to_dict(),
            title=f"Multi-Fault: {project}-{bug}",
        )
        app.state.set_active_bug(project, bug)
        app.state.save()
    except Exception as exc:
        app.console.print(f"[red]Multi-fault query failed: {exc}[/red]")


def handle_enrich(app: "ODCApp", args: str) -> None:
    cls_path = args.strip() if args.strip() else None
    if not cls_path:
        files = discover_classifications()
        if files:
            picked = pick_file_interactive(files, title="Select classification.json")
            if picked:
                cls_path = str(picked)
        if not cls_path and app.state.last_classification_path:
            cls_path = app.state.last_classification_path
    if not cls_path or not Path(cls_path).exists():
        app.console.print("[red]No classification file found.[/red]")
        return
    try:
        from ..multifault import enrich_classification

        classification_path = Path(cls_path)
        classification = json.loads(classification_path.read_text(encoding="utf-8"))
        result = enrich_classification(classification)
        rendering.render_json_panel(app.console, result, title="Enriched Classification")
    except Exception as exc:
        app.console.print(f"[red]Enrichment failed: {exc}[/red]")


# ---------------------------------------------------------------------------
# Study Commands
# ---------------------------------------------------------------------------

def handle_study(app: "ODCApp", args: str) -> None:
    parts = args.strip().split(None, 1)
    sub = parts[0] if parts else ""
    sub_args = parts[1] if len(parts) > 1 else ""

    if sub == "plan":
        _study_plan(app, sub_args)
    elif sub == "run":
        _study_run(app, sub_args)
    elif sub == "analyze":
        _study_analyze(app, sub_args)
    elif sub == "baseline":
        _study_baseline(app, sub_args)
    elif sub == "naive":
        _study_naive(app, sub_args)
    elif sub == "export":
        _study_export(app, sub_args)
    else:
        app.console.print("[yellow]Usage: /study <plan|run|analyze|baseline|naive|export> [options][/yellow]")


def _study_plan(app: "ODCApp", args: str) -> None:
    tokens = shlex.split(args) if args.strip() else []
    target = 68
    for i, t in enumerate(tokens):
        if t == "--target-bugs" and i + 1 < len(tokens):
            target = int(tokens[i + 1])
    from ..batch import generate_study_manifest
    client = _get_client(app)
    output = Path(".dist") / "study" / f"manifest_{target}.json"
    app.console.print(f"  [cyan]Generating manifest for {target} bugs...[/cyan]")
    with app.console.status("  Generating study manifest...", spinner="dots"):
        generate_study_manifest(
            defects4j=client, output_path=output,
            target_bugs=target, min_per_project=1, seed=42,
        )
    app.console.print(f"  [green]✓[/green] Manifest → {output}")


def _study_run(app: "ODCApp", args: str) -> None:
    tokens = shlex.split(args) if args.strip() else []
    manifest_path = None
    artifacts_root: Path | None = None
    work_root: Path | None = None
    summary_output: Path | None = None
    no_skip_existing = False
    prompt_output = False
    require_all_projects = False

    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token == "--manifest" and i + 1 < len(tokens):
            manifest_path = tokens[i + 1]
            i += 2
        elif token == "--artifacts-root" and i + 1 < len(tokens):
            artifacts_root = Path(tokens[i + 1])
            i += 2
        elif token == "--work-root" and i + 1 < len(tokens):
            work_root = Path(tokens[i + 1])
            i += 2
        elif token == "--summary-output" and i + 1 < len(tokens):
            summary_output = Path(tokens[i + 1])
            i += 2
        elif token == "--no-skip-existing":
            no_skip_existing = True
            i += 1
        elif token == "--prompt-output":
            prompt_output = True
            i += 1
        elif token == "--require-all-projects":
            require_all_projects = True
            i += 1
        else:
            i += 1
    if not manifest_path:
        # Interactive manifest picker
        manifests = discover_manifests()
        if manifests:
            picked = pick_file_interactive(manifests, title="Select study manifest")
            if picked:
                manifest_path = str(picked)
    if not manifest_path:
        app.console.print("[red]No manifest found. Run /study plan first.[/red]")
        return
    mp = Path(manifest_path)
    if not mp.exists():
        # Try resolving under .dist/study/
        mp = Path(".dist") / "study" / manifest_path
    if not mp.exists():
        app.console.print(f"[red]Manifest not found: {manifest_path}[/red]")
        return

    from .. import console as pipeline_console
    from ..batch import install_signal_handlers, load_manifest, reset_shutdown, run_batch_from_manifest
    from ..pipeline import write_json

    previous_console = pipeline_console.get_console()
    previous_quiet = pipeline_console.is_quiet()
    previous_sigint = signal.getsignal(signal.SIGINT)
    previous_sigbreak = signal.getsignal(signal.SIGBREAK) if hasattr(signal, "SIGBREAK") else None

    pipeline_console.bind_console(app.console, quiet=False)
    install_signal_handlers()
    reset_shutdown()

    try:
        client = _get_client(app)
        manifest = load_manifest(mp)
        target_bugs = manifest.get("target_bugs", manifest.get("selected_bugs", 0))
        dist_study = Path(".dist") / "study"
        if artifacts_root is None:
            artifacts_root = dist_study / f"artifacts_{target_bugs}"
        if work_root is None:
            work_root = dist_study / "work"
        if summary_output is None:
            summary_output = dist_study / "summary.json"

        if require_all_projects:
            expected_projects = set(client.pids())
            covered_projects = set(manifest.get("projects_covered", []))
            missing_projects = sorted(expected_projects - covered_projects)
            if missing_projects:
                app.console.print(
                    "[red]Manifest is missing project coverage required for this run: "
                    + ", ".join(missing_projects)
                    + "[/red]"
                )
                return

        llm = _get_llm_kwargs(app)
        app.console.print(f"  [cyan]Running study from {mp.name}...[/cyan]")
        app.console.print(f"  [dim]Artifacts -> {artifacts_root}[/dim]")
        app.console.print(f"  [dim]Work dir  -> {work_root}[/dim]")
        app.console.print(f"  [dim]Summary   -> {summary_output}[/dim]")
        app.console.print("  [dim]This may take a while for large manifests.[/dim]")
        app.console.print("  [dim]Ctrl+C once for graceful stop, twice to force stop.[/dim]")
        try:
            summary = run_batch_from_manifest(
                defects4j=client,
                manifest=manifest,
                artifacts_root=artifacts_root,
                work_root=work_root,
                provider=llm["provider"],
                model=llm["model"],
                api_key_env=llm["api_key_env"],
                base_url=llm["base_url"],
                prompt_style=app.state.prompt_style,
                snippet_radius=app.state.snippet_radius,
                run_coverage=not app.state.skip_coverage,
                skip_existing=not no_skip_existing,
                prompt_output=prompt_output,
            )
        except SystemExit as exc:
            if exc.code == 130:
                app.console.print("  [yellow]Force stop requested. Returning to the interactive prompt.[/yellow]")
                app.console.print("  [dim]The current external command may need a moment to terminate cleanly.[/dim]")
                return
            raise
        except KeyboardInterrupt:
            app.console.print("  [yellow]Interrupted. Returning to the interactive prompt.[/yellow]")
            return

        write_json(summary_output, summary)

        status_label = "Study run interrupted (checkpoint saved)" if summary.get("interrupted") else "Study run complete"
        app.console.print(f"  [green]✓[/green] {status_label}")
        app.console.print(f"  [dim]Summary saved to {summary_output}[/dim]")
        rendering.render_json_panel(
            app.console,
            {
                "summary_output": str(summary_output),
                "total_entries": summary.get("total_entries", 0),
                "completed_entries": summary.get("completed_entries", 0),
                "interrupted": bool(summary.get("interrupted")),
                "prefix_ok": summary.get("prefix_ok", 0),
                "postfix_ok": summary.get("postfix_ok", 0),
                "paired_for_compare": summary.get("paired_for_compare", 0),
                "projects_covered": summary.get("projects_covered", []),
            },
            title="Study Run Summary",
        )
    finally:
        reset_shutdown()
        signal.signal(signal.SIGINT, previous_sigint)
        if hasattr(signal, "SIGBREAK") and previous_sigbreak is not None:
            signal.signal(signal.SIGBREAK, previous_sigbreak)
        pipeline_console.bind_console(previous_console, quiet=previous_quiet)


def _study_analyze(app: "ODCApp", args: str) -> None:
    tokens = shlex.split(args) if args.strip() else []
    manifest_path = None
    prefix_dir: Path | None = None
    postfix_dir: Path | None = None
    output_path: Path | None = None
    report_path: Path | None = None
    expected_projects: list[str] = []
    require_all_projects = False

    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token == "--manifest" and i + 1 < len(tokens):
            manifest_path = tokens[i + 1]
            i += 2
        elif token == "--prefix-dir" and i + 1 < len(tokens):
            prefix_dir = Path(tokens[i + 1])
            i += 2
        elif token == "--postfix-dir" and i + 1 < len(tokens):
            postfix_dir = Path(tokens[i + 1])
            i += 2
        elif token == "--output" and i + 1 < len(tokens):
            output_path = Path(tokens[i + 1])
            i += 2
        elif token == "--report" and i + 1 < len(tokens):
            report_path = Path(tokens[i + 1])
            i += 2
        elif token == "--require-all-projects":
            require_all_projects = True
            i += 1
        elif token == "--expected-projects":
            i += 1
            while i < len(tokens) and not tokens[i].startswith("--"):
                expected_projects.append(tokens[i])
                i += 1
        else:
            i += 1
    if not manifest_path:
        manifests = discover_manifests()
        if manifests:
            picked = pick_file_interactive(manifests, title="Select study manifest")
            if picked:
                manifest_path = str(picked)
    if not manifest_path:
        app.console.print("[red]No manifest found.[/red]")
        return

    from ..batch import analyze_batch_artifacts, load_manifest, write_analysis_markdown
    from ..pipeline import write_json

    mp = Path(manifest_path)
    if not mp.exists():
        mp = Path(".dist") / "study" / manifest_path
    if not mp.exists():
        app.console.print(f"[red]Manifest not found: {manifest_path}[/red]")
        return

    manifest = load_manifest(mp)
    target_bugs = manifest.get("target_bugs", manifest.get("selected_bugs", ""))
    dist_study = Path(".dist") / "study"
    artifacts_folder = f"artifacts_{target_bugs}" if target_bugs else "artifacts"
    if prefix_dir is None:
        prefix_dir = dist_study / artifacts_folder / "prefix"
    if postfix_dir is None:
        postfix_dir = dist_study / artifacts_folder / "postfix"
    if output_path is None:
        suffix = f"_{target_bugs}" if target_bugs else ""
        output_path = dist_study / f"analysis{suffix}.json"
    elif not output_path.parent.parts:
        output_path = dist_study / output_path
    if report_path is None:
        suffix = f"_{target_bugs}" if target_bugs else ""
        report_path = dist_study / f"analysis{suffix}.md"
    elif not report_path.parent.parts:
        report_path = dist_study / report_path

    expected: list[str] | None = None
    if expected_projects:
        expected = sorted(set(expected_projects))
    else:
        expected = sorted(set(manifest.get("projects_requested", [])))

    app.console.print(f"  [cyan]Analyzing study results for {mp.name}...[/cyan]")
    app.console.print(f"  [dim]Prefix dir  -> {prefix_dir}[/dim]")
    app.console.print(f"  [dim]Postfix dir -> {postfix_dir}[/dim]")

    summary = analyze_batch_artifacts(
        prefix_dir=prefix_dir,
        postfix_dir=postfix_dir,
        expected_projects=expected,
    )

    if require_all_projects and summary.get("missing_projects"):
        app.console.print(
            "[red]Analysis failed all-project requirement. Missing projects: "
            + ", ".join(summary["missing_projects"])
            + "[/red]"
        )
        return

    write_json(output_path, summary)
    write_analysis_markdown(summary, report_path)
    app.console.print("  [green]✓[/green] Study analysis complete")
    app.console.print(f"  [dim]JSON   -> {output_path}[/dim]")
    app.console.print(f"  [dim]Report -> {report_path}[/dim]")
    rendering.render_json_panel(
        app.console,
        {
            "output": str(output_path),
            "report": str(report_path),
            "total_pairs": summary.get("total_pairs", 0),
            "unique_projects": summary.get("unique_projects", 0),
            "missing_projects": summary.get("missing_projects", []),
            "type_changed_count": summary.get("type_changed_count", 0),
        },
        title="Study Analysis Summary",
    )


def _study_baseline(app: "ODCApp", args: str) -> None:
    tokens = shlex.split(args) if args.strip() else []
    manifest_path = None
    baseline_root: Path | None = None
    work_root: Path | None = None
    scientific_artifacts_root: Path | None = None
    summary_output: Path | None = None
    no_skip_existing = False
    prompt_output = False

    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token == "--manifest" and i + 1 < len(tokens):
            manifest_path = tokens[i + 1]; i += 2
        elif token == "--baseline-root" and i + 1 < len(tokens):
            baseline_root = Path(tokens[i + 1]); i += 2
        elif token == "--work-root" and i + 1 < len(tokens):
            work_root = Path(tokens[i + 1]); i += 2
        elif token == "--scientific-artifacts-root" and i + 1 < len(tokens):
            scientific_artifacts_root = Path(tokens[i + 1]); i += 2
        elif token == "--summary-output" and i + 1 < len(tokens):
            summary_output = Path(tokens[i + 1]); i += 2
        elif token == "--no-skip-existing":
            no_skip_existing = True; i += 1
        elif token == "--prompt-output":
            prompt_output = True; i += 1
        else:
            i += 1

    if not manifest_path:
        manifests = discover_manifests()
        if manifests:
            picked = pick_file_interactive(manifests, title="Select study manifest")
            if picked:
                manifest_path = str(picked)
    if not manifest_path:
        app.console.print("[red]No manifest found. Run /study plan first.[/red]")
        return

    mp = Path(manifest_path)
    if not mp.exists():
        mp = Path(".dist") / "study" / manifest_path
    if not mp.exists():
        app.console.print(f"[red]Manifest not found: {manifest_path}[/red]")
        return

    from .. import console as pipeline_console
    from ..batch import install_signal_handlers, load_manifest, reset_shutdown, run_baseline_from_manifest
    from ..pipeline import write_json

    previous_console = pipeline_console.get_console()
    previous_quiet = pipeline_console.is_quiet()
    previous_sigint = signal.getsignal(signal.SIGINT)
    previous_sigbreak = signal.getsignal(signal.SIGBREAK) if hasattr(signal, "SIGBREAK") else None

    pipeline_console.bind_console(app.console, quiet=False)
    install_signal_handlers()
    reset_shutdown()

    try:
        client = _get_client(app)
        manifest = load_manifest(mp)
        target_bugs = manifest.get("target_bugs", manifest.get("selected_bugs", 0))
        dist_study = Path(".dist") / "study"

        if baseline_root is None:
            baseline_root = dist_study / f"baseline_{target_bugs}"
        if work_root is None:
            work_root = dist_study / "work"
        if summary_output is None:
            summary_output = dist_study / "baseline_summary.json"

        llm = _get_llm_kwargs(app)
        app.console.print(f"  [cyan]Running baseline from {mp.name}...[/cyan]")
        app.console.print(f"  [dim]Baseline root  -> {baseline_root}[/dim]")
        app.console.print(f"  [dim]Prompt style   -> direct[/dim]")
        if scientific_artifacts_root:
            app.console.print(f"  [dim]Reuse context  -> {scientific_artifacts_root}[/dim]")
        app.console.print("  [dim]Ctrl+C once for graceful stop, twice to force stop.[/dim]")

        try:
            summary = run_baseline_from_manifest(
                defects4j=client,
                manifest=manifest,
                baseline_root=baseline_root,
                work_root=work_root,
                scientific_artifacts_root=scientific_artifacts_root,
                provider=llm["provider"],
                model=llm["model"],
                api_key_env=llm["api_key_env"],
                base_url=llm["base_url"],
                prompt_style="direct",
                snippet_radius=app.state.snippet_radius,
                run_coverage=not app.state.skip_coverage,
                skip_existing=not no_skip_existing,
                prompt_output=prompt_output,
            )
        except SystemExit as exc:
            if exc.code == 130:
                app.console.print("  [yellow]Force stop. Returning to interactive prompt.[/yellow]")
                return
            raise
        except KeyboardInterrupt:
            app.console.print("  [yellow]Interrupted. Returning to interactive prompt.[/yellow]")
            return

        write_json(summary_output, summary)

        status_label = "Baseline interrupted" if summary.get("interrupted") else "Baseline complete"
        app.console.print(f"  [green]✓[/green] {status_label}")
        rendering.render_json_panel(
            app.console,
            {
                "summary_output": str(summary_output),
                "completed": summary.get("completed_entries", 0),
                "reused_context": summary.get("reused_context_count", 0),
            },
            title="Baseline Summary",
        )
    finally:
        reset_shutdown()
        signal.signal(signal.SIGINT, previous_sigint)
        if hasattr(signal, "SIGBREAK") and previous_sigbreak is not None:
            signal.signal(signal.SIGBREAK, previous_sigbreak)
        pipeline_console.bind_console(previous_console, quiet=previous_quiet)


def _study_naive(app: "ODCApp", args: str) -> None:
    tokens = shlex.split(args) if args.strip() else []
    manifest_path = None
    naive_root: Path | None = None
    work_root: Path | None = None
    scientific_artifacts_root: Path | None = None
    summary_output: Path | None = None
    no_skip_existing = False
    prompt_output = False

    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token == "--manifest" and i + 1 < len(tokens):
            manifest_path = tokens[i + 1]; i += 2
        elif token == "--naive-root" and i + 1 < len(tokens):
            naive_root = Path(tokens[i + 1]); i += 2
        elif token == "--work-root" and i + 1 < len(tokens):
            work_root = Path(tokens[i + 1]); i += 2
        elif token == "--scientific-artifacts-root" and i + 1 < len(tokens):
            scientific_artifacts_root = Path(tokens[i + 1]); i += 2
        elif token == "--summary-output" and i + 1 < len(tokens):
            summary_output = Path(tokens[i + 1]); i += 2
        elif token == "--no-skip-existing":
            no_skip_existing = True; i += 1
        elif token == "--prompt-output":
            prompt_output = True; i += 1
        else:
            i += 1

    if not manifest_path:
        manifests = discover_manifests()
        if manifests:
            picked = pick_file_interactive(manifests, title="Select study manifest")
            if picked:
                manifest_path = str(picked)
    if not manifest_path:
        app.console.print("[red]No manifest found. Run /study plan first.[/red]")
        return

    mp = Path(manifest_path)
    if not mp.exists():
        mp = Path(".dist") / "study" / manifest_path
    if not mp.exists():
        app.console.print(f"[red]Manifest not found: {manifest_path}[/red]")
        return

    from .. import console as pipeline_console
    from ..batch import install_signal_handlers, load_manifest, reset_shutdown, run_baseline_from_manifest
    from ..pipeline import write_json

    previous_console = pipeline_console.get_console()
    previous_quiet = pipeline_console.is_quiet()
    previous_sigint = signal.getsignal(signal.SIGINT)
    previous_sigbreak = signal.getsignal(signal.SIGBREAK) if hasattr(signal, "SIGBREAK") else None

    pipeline_console.bind_console(app.console, quiet=False)
    install_signal_handlers()
    reset_shutdown()

    try:
        client = _get_client(app)
        manifest = load_manifest(mp)
        target_bugs = manifest.get("target_bugs", manifest.get("selected_bugs", 0))
        dist_study = Path(".dist") / "study"

        if naive_root is None:
            naive_root = dist_study / f"naive_{target_bugs}"
        if work_root is None:
            work_root = dist_study / "work"
        if summary_output is None:
            summary_output = dist_study / "naive_summary.json"

        llm = _get_llm_kwargs(app)
        app.console.print(f"  [cyan]Running naive (taxonomy-free) from {mp.name}...[/cyan]")
        app.console.print(f"  [dim]Naive root     -> {naive_root}[/dim]")
        app.console.print(f"  [dim]Prompt style   -> naive (no ODC taxonomy)[/dim]")
        if scientific_artifacts_root:
            app.console.print(f"  [dim]Reuse context  -> {scientific_artifacts_root}[/dim]")
        app.console.print("  [dim]Ctrl+C once for graceful stop, twice to force stop.[/dim]")

        try:
            summary = run_baseline_from_manifest(
                defects4j=client,
                manifest=manifest,
                baseline_root=naive_root,
                work_root=work_root,
                scientific_artifacts_root=scientific_artifacts_root,
                provider=llm["provider"],
                model=llm["model"],
                api_key_env=llm["api_key_env"],
                base_url=llm["base_url"],
                prompt_style="naive",
                snippet_radius=app.state.snippet_radius,
                run_coverage=not app.state.skip_coverage,
                skip_existing=not no_skip_existing,
                prompt_output=prompt_output,
            )
        except SystemExit as exc:
            if exc.code == 130:
                app.console.print("  [yellow]Force stop. Returning to interactive prompt.[/yellow]")
                return
            raise
        except KeyboardInterrupt:
            app.console.print("  [yellow]Interrupted. Returning to interactive prompt.[/yellow]")
            return

        write_json(summary_output, summary)

        status_label = "Naive run interrupted" if summary.get("interrupted") else "Naive run complete"
        app.console.print(f"  [green]\u2713[/green] {status_label}")
        rendering.render_json_panel(
            app.console,
            {
                "summary_output": str(summary_output),
                "completed": summary.get("completed_entries", 0),
                "reused_context": summary.get("reused_context_count", 0),
            },
            title="Naive Summary",
        )
    finally:
        reset_shutdown()
        signal.signal(signal.SIGINT, previous_sigint)
        if hasattr(signal, "SIGBREAK") and previous_sigbreak is not None:
            signal.signal(signal.SIGBREAK, previous_sigbreak)
        pipeline_console.bind_console(previous_console, quiet=previous_quiet)


def _study_export(app: "ODCApp", args: str) -> None:
    tokens = shlex.split(args) if args.strip() else []
    analysis_path = None
    output_dir: Path | None = None
    export_format = "both"

    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token == "--analysis" and i + 1 < len(tokens):
            analysis_path = tokens[i + 1]; i += 2
        elif token == "--output-dir" and i + 1 < len(tokens):
            output_dir = Path(tokens[i + 1]); i += 2
        elif token == "--format" and i + 1 < len(tokens):
            export_format = tokens[i + 1]; i += 2
        else:
            i += 1

    if not analysis_path:
        # Try to find the most recent analysis JSON
        study_dir = Path(".dist") / "study"
        candidates = sorted(study_dir.glob("analysis_*.json")) if study_dir.is_dir() else []
        if candidates:
            analysis_path = str(candidates[-1])
        else:
            app.console.print("[red]No analysis JSON found. Run /study analyze first or pass --analysis PATH.[/red]")
            return

    ap = Path(analysis_path)
    if not ap.exists():
        ap = Path(".dist") / "study" / analysis_path
    if not ap.exists():
        app.console.print(f"[red]Analysis file not found: {analysis_path}[/red]")
        return

    from ..results_export import (
        export_accuracy_table_latex,
        export_baseline_comparison_latex,
        export_confusion_matrix_latex,
        export_per_project_kappa_latex,
        export_type_distribution_latex,
        export_all_csv,
    )

    analysis = json.loads(ap.read_text(encoding="utf-8"))
    out_dir = output_dir or ap.parent

    written: list[str] = []

    if export_format in ("latex", "both"):
        latex_dir = out_dir / "latex"
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
                app.console.print(f"  [yellow]Skipped {filename}: {exc}[/yellow]")

    if export_format in ("csv", "both"):
        csv_dir = out_dir / "csv"
        csv_files = export_all_csv(analysis, csv_dir)
        written.extend(f"csv/{p.name}" for p in csv_files)

    app.console.print(f"  [green]✓[/green] Export complete → {out_dir}")
    for w in written:
        app.console.print(f"    {w}")


# ---------------------------------------------------------------------------
# Handler dispatch map
# ---------------------------------------------------------------------------

HANDLER_MAP: dict[str, Any] = {
    "handle_help": handle_help,
    "handle_status": handle_status,
    "handle_config": handle_config,
    "handle_provider": handle_provider,
    "handle_model": handle_model,
    "handle_history": handle_history,
    "handle_bugs": handle_bugs,
    "handle_clear": handle_clear,
    "handle_doctor": handle_doctor,
    "handle_version": handle_version,
    "handle_exit": handle_exit,
    "handle_collect": handle_collect,
    "handle_classify": handle_classify,
    "handle_run": handle_run,
    "handle_compare": handle_compare,
    "handle_compare_batch": handle_compare_batch,
    "handle_show": handle_show,
    "handle_d4j": handle_d4j,
    "handle_multifault": handle_multifault,
    "handle_enrich": handle_enrich,
    "handle_study": handle_study,
}
