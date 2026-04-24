"""Rich rendering helpers specific to the interactive REPL.

Extends the existing ``console.py`` with interactive-mode output:
  - classification panels
  - context summaries
  - comparison tables
  - help tables
  - status panels
  - doctor reports
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from rich.columns import Columns
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

if TYPE_CHECKING:
    from .commands import SlashCommandSpec
    from .session import SessionState


def render_help_table(console: Console, commands: list["SlashCommandSpec"]) -> None:
    """Render the /help output grouped by category."""
    categories = {
        "pipeline": "🔧  Pipeline Commands",
        "study": "📊  Study Commands",
        "defects4j": "🐛  Defects4J Proxy",
        "multifault": "🔗  Multi-Fault",
        "inspect": "🔍  Inspection",
        "session": "⚙️   Session & Config",
    }

    for cat_key, cat_title in categories.items():
        cat_cmds = [c for c in commands if c.category == cat_key]
        if not cat_cmds:
            continue

        table = Table(
            show_header=False,
            box=None,
            padding=(0, 2),
            expand=True,
        )
        table.add_column("Command", style="bold green", no_wrap=True, min_width=22)
        table.add_column("Description", style="white")

        for cmd in cat_cmds:
            name_str = f"/{cmd.name}"
            if cmd.argument_hint:
                name_str += f" {cmd.argument_hint}"
            aliases = ""
            if cmd.aliases:
                aliases = f"  (aliases: {', '.join('/' + a for a in cmd.aliases)})"
            table.add_row(name_str, cmd.summary + aliases)

        console.print(Panel(
            table,
            title=f"[bold]{cat_title}[/bold]",
            border_style="dim",
            expand=True,
        ))


def render_status_panel(console: Console, state: "SessionState") -> None:
    """Render current session state."""
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Key", style="bold white", no_wrap=True)
    table.add_column("Value", style="cyan")

    table.add_row("Session ID", state.session_id)
    table.add_row("Workspace", state.workspace_root)
    table.add_row("Active Bug", state.active_bug_label)
    table.add_row("Provider", state.provider)
    table.add_row("Model", state.model or "(auto)")
    table.add_row("Mode", "postfix (oracle)" if state.include_fix_diff else "prefix (realistic)")
    table.add_row("Skip Coverage", str(state.skip_coverage))
    table.add_row("Prompt Style", state.prompt_style)
    table.add_row("Commands Run", str(len(state.command_history)))

    if state.last_context_path:
        table.add_row("Last Context", state.last_context_path)
    if state.last_classification_path:
        table.add_row("Last Classification", state.last_classification_path)
    if state.last_report_path:
        table.add_row("Last Report", state.last_report_path)

    console.print(Panel(
        table,
        title="[bold]Session Status[/bold]",
        border_style="cyan",
        expand=True,
    ))


def render_classification_panel(console: Console, data: dict[str, Any]) -> None:
    """Render a classification result as a rich panel."""
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Field", style="bold white", no_wrap=True)
    table.add_column("Value", style="white")

    odc_type = data.get("odc_type") or data.get("odc_defect_type") or "?"
    table.add_row("ODC Type", f"[bold cyan]{odc_type}[/bold cyan]")
    table.add_row("Confidence", f"{float(data.get('confidence', 0) or 0):.2f}")

    qualifier = data.get("qualifier") or data.get("odc_qualifier")
    if qualifier:
        table.add_row("Qualifier", str(qualifier))
    if data.get("family"):
        table.add_row("Family", str(data["family"]))
    if data.get("target"):
        table.add_row("Target", str(data["target"]))
    if data.get("evidence_mode"):
        table.add_row("Evidence Mode", str(data["evidence_mode"]))
    if "needs_human_review" in data:
        table.add_row("Needs Review", "Yes" if data.get("needs_human_review") else "No")

    alternatives = data.get("alternative_types") or []
    if alternatives:
        first_alt = alternatives[0]
        if isinstance(first_alt, dict):
            table.add_row("Alt Type", str(first_alt.get("type", "?")))

    reasoning = data.get("reasoning_summary") or data.get("reasoning") or ""
    if reasoning:
        table.add_row("Reasoning", reasoning[:200] + ("..." if len(reasoning) > 200 else ""))

    console.print(Panel(
        table,
        title="[bold green]Classification Result[/bold green]",
        border_style="green",
        expand=True,
    ))


def render_context_summary(console: Console, data: dict[str, Any]) -> None:
    """Render a condensed context.json summary."""
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Field", style="bold white", no_wrap=True)
    table.add_column("Value", style="white")

    table.add_row("Project", data.get("project_id", "?"))
    table.add_row("Bug", str(data.get("bug_id", "?")))
    failures = data.get("failures") or data.get("failing_tests") or []
    table.add_row("Failing Tests", str(len(failures)))
    table.add_row("Suspicious Frames", str(len(data.get("suspicious_frames", []))))
    table.add_row("Code Snippets", str(len(data.get("code_snippets", []))))
    table.add_row("Coverage Classes", str(len(data.get("coverage", []))))
    table.add_row("Has Fix Diff", str(bool(data.get("fix_diff"))))

    report = data.get("bug_report_content") or data.get("bug_report_text")
    if report:
        table.add_row("Bug Report", report[:150] + ("..." if len(report) > 150 else ""))

    console.print(Panel(
        table,
        title="[bold]Context Summary[/bold]",
        border_style="blue",
        expand=True,
    ))


def render_json_panel(console: Console, data: Any, title: str = "JSON") -> None:
    """Render any JSON data with syntax highlighting."""
    json_str = json.dumps(data, indent=2, default=str)
    syntax = Syntax(json_str, "json", theme="monokai", line_numbers=False)
    console.print(Panel(
        syntax,
        title=f"[bold]{title}[/bold]",
        border_style="dim",
        expand=True,
    ))


def render_markdown_panel(console: Console, md_text: str, title: str = "Report") -> None:
    """Render markdown content in the terminal."""
    console.print(Panel(
        Markdown(md_text),
        title=f"[bold]{title}[/bold]",
        border_style="dim",
        expand=True,
    ))


def render_text_panel(console: Console, text: str, title: str = "Text") -> None:
    """Render plain text content without JSON or markdown assumptions."""
    console.print(Panel(
        Text(text),
        title=f"[bold]{title}[/bold]",
        border_style="dim",
        expand=True,
    ))


def render_doctor_report(console: Console, checks: list[tuple[str, bool, str]]) -> None:
    """Render environment health check results.

    Each check is (name, passed, detail).
    """
    table = Table(show_header=True, header_style="bold", expand=True)
    table.add_column("Check", style="white")
    table.add_column("Status", no_wrap=True)
    table.add_column("Detail", style="dim")

    for name, passed, detail in checks:
        icon = "[bold green]✓[/bold green]" if passed else "[bold red]✗[/bold red]"
        table.add_row(name, icon, detail)

    console.print(Panel(
        table,
        title="[bold]Environment Health[/bold]",
        border_style="cyan",
        expand=True,
    ))


def render_tip(console: Console, message: str) -> None:
    """Render a subtle tip message."""
    console.print(f"  [dim]💡 Tip: {message}[/dim]")
