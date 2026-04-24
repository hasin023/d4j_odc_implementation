"""Welcome banner and version display for the interactive REPL."""

from __future__ import annotations

from typing import TYPE_CHECKING

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

if TYPE_CHECKING:
    from .session import SessionState

VERSION = "1.0.0"


def print_banner(console: Console, state: "SessionState") -> None:
    """Print the welcome banner with current session info."""
    lines = Text()
    lines.append("🔬 D4J ODC Pipeline", style="bold cyan")
    lines.append(" — Interactive Mode\n\n", style="dim")

    lines.append("  Provider   ", style="bold white")
    lines.append(f"{state.provider}\n", style="cyan")

    lines.append("  Model      ", style="bold white")
    lines.append(f"{state.model or '(auto)'}\n", style="cyan")

    lines.append("  Mode       ", style="bold white")
    lines.append(f"{'postfix (oracle)' if state.include_fix_diff else 'prefix (realistic)'}\n", style="yellow" if state.include_fix_diff else "green")

    if state.has_active_bug:
        lines.append("  Active Bug ", style="bold white")
        lines.append(f"{state.active_bug_label}\n", style="magenta")

    lines.append("\n  Type ", style="dim")
    lines.append("/help", style="bold green")
    lines.append(" for available commands\n", style="dim")
    lines.append("  Type ", style="dim")
    lines.append("/exit", style="bold red")
    lines.append(" or ", style="dim")
    lines.append("Ctrl+D", style="bold red")
    lines.append(" to quit", style="dim")

    console.print()
    console.print(Panel(
        lines,
        border_style="cyan",
        expand=True,
        padding=(0, 2),
    ))
    console.print()
