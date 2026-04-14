"""Centralized rich console helpers for pipeline status output."""

from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Generator

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

_THEME = Theme(
    {
        "step": "cyan",
        "success": "bold green",
        "error": "bold red",
        "warn": "bold yellow",
        "info": "dim",
        "label": "bold white",
        "value": "white",
    }
)

_console: Console | None = None
_quiet: bool = False


def init_console(*, quiet: bool = False) -> None:
    """Initialize the global console. Call once at CLI entry."""
    global _console, _quiet
    _quiet = quiet
    _console = Console(theme=_THEME, highlight=False) if not quiet else None


def get_console() -> Console | None:
    """Return the console, or None if quiet mode."""
    return _console


def is_quiet() -> bool:
    return _quiet


# ---------------------------------------------------------------------------
# Status helpers
# ---------------------------------------------------------------------------

def step(message: str, *, detail: str | None = None) -> None:
    """Print a pipeline step message."""
    if _quiet or _console is None:
        return
    text = Text()
    text.append("  * ", style="step")
    text.append(message)
    if detail:
        text.append(f"  {detail}", style="info")
    _console.print(text)


def success(message: str) -> None:
    if _quiet or _console is None:
        return
    text = Text()
    text.append("  + ", style="success")
    text.append(message, style="success")
    _console.print(text)


def warn(message: str) -> None:
    if _quiet or _console is None:
        return
    text = Text()
    text.append("  ! ", style="warn")
    text.append(message, style="warn")
    _console.print(text)


def error(message: str) -> None:
    if _quiet or _console is None:
        return
    text = Text()
    text.append("  x ", style="error")
    text.append(message, style="error")
    _console.print(text)


# ---------------------------------------------------------------------------
# Panels
# ---------------------------------------------------------------------------

def header_panel(title: str, subtitle: str | None = None) -> None:
    """Print a header panel for a pipeline phase."""
    if _quiet or _console is None:
        return
    content = Text(subtitle, style="info") if subtitle else Text("")
    _console.print()
    _console.print(Panel(content, title=f"[bold]{title}[/bold]", border_style="cyan", expand=True))


def result_panel(title: str, rows: list[tuple[str, str]]) -> None:
    """Print a result panel with key-value pairs."""
    if _quiet or _console is None:
        return
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Key", style="label", no_wrap=True)
    table.add_column("Value", style="value")
    for key, value in rows:
        table.add_row(key, value)
    _console.print()
    _console.print(Panel(table, title=f"[bold green]{title}[/bold green]", border_style="green", expand=True))


def error_panel(title: str, message: str, *, hint: str | None = None) -> None:
    """Print an error panel."""
    if _quiet or _console is None:
        return
    content = Text()
    content.append(message)
    if hint:
        content.append(f"\n\nHint: {hint}", style="info")
    _console.print()
    _console.print(Panel(content, title=f"[bold red]{title}[/bold red]", border_style="red", expand=True))


# ---------------------------------------------------------------------------
# Timed step context manager
# ---------------------------------------------------------------------------

@contextmanager
def timed_step(message: str) -> Generator[None, None, None]:
    """Context manager that prints a step and then its elapsed time."""
    if _quiet or _console is None:
        yield
        return
    start = time.monotonic()
    _console.print(Text.assemble(("  * ", "step"), (f"{message}...", "")), end="")
    try:
        yield
        elapsed = time.monotonic() - start
        _console.print(f"  [success]done[/success] [info]({elapsed:.1f}s)[/info]")
    except Exception:
        elapsed = time.monotonic() - start
        _console.print(f"  [error]failed[/error] [info]({elapsed:.1f}s)[/info]")
        raise


@contextmanager
def spinner_step(message: str) -> Generator[None, None, None]:
    """Context manager with a rich spinner for long-running operations."""
    if _quiet or _console is None:
        yield
        return
    start = time.monotonic()
    with _console.status(f"  [step]*[/step] {message}...", spinner="dots"):
        yield
    elapsed = time.monotonic() - start
    text = Text()
    text.append("  * ", style="step")
    text.append(f"{message}  ")
    text.append("done", style="success")
    text.append(f" ({elapsed:.1f}s)", style="info")
    _console.print(text)


# ---------------------------------------------------------------------------
# Data display helpers
# ---------------------------------------------------------------------------

def print_list(title: str, items: list[str], *, style: str = "white") -> None:
    """Print a titled list of items."""
    if _quiet or _console is None:
        return
    _console.print(f"\n[bold]{title}[/bold]")
    if not items:
        _console.print("  [info](none)[/info]")
        return
    for item in items:
        _console.print(f"  - {item}", style=style)


def print_table(title: str, headers: list[str], rows: list[list[str]]) -> None:
    """Print a formatted table."""
    if _quiet or _console is None:
        return
    table = Table(title=title, show_lines=False, header_style="bold cyan")
    for header in headers:
        table.add_column(header)
    for row in rows:
        table.add_row(*row)
    _console.print()
    _console.print(table)
