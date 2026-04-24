"""Main REPL application — the interactive ODC pipeline shell."""
from __future__ import annotations

import re
import sys
from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from rich.console import Console
from rich.theme import Theme

from .banner import print_banner
from .commands import COMMAND_REGISTRY, all_completion_entries, get_command
from .completer import SlashCommandCompleter
from .handlers import HANDLER_MAP
from .rendering import render_tip
from .session import SessionState

_THEME = Theme({
    "step": "cyan",
    "success": "bold green",
    "error": "bold red",
    "warn": "bold yellow",
    "info": "dim",
    "label": "bold white",
    "value": "white",
})

# Pattern to detect bare "Project Bug" shorthand (e.g. "Lang 1")
_BARE_RUN_RE = re.compile(r"^([A-Z][a-z]+)\s+(\d+)(.*)$")


class ODCApp:
    """Interactive REPL application for the D4J ODC Pipeline."""

    def __init__(self) -> None:
        self.console = Console(theme=_THEME, highlight=False)
        self.state = SessionState.auto_resume()
        self.prompt_session: PromptSession | None = None

    def run(self) -> int:
        """Main REPL loop. Returns exit code."""
        # Load dotenv
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass

        # Create prompt session (needs a real console, so defer to run-time)
        history_path = Path(".dist") / ".odc_history"
        history_path.parent.mkdir(parents=True, exist_ok=True)
        self.prompt_session = PromptSession(
            completer=SlashCommandCompleter(all_completion_entries()),
            history=FileHistory(str(history_path)),
            complete_while_typing=True,
        )

        print_banner(self.console, self.state)

        while True:
            try:
                text = self.prompt_session.prompt("odc> ").strip()
                if not text:
                    continue
                self.dispatch(text)
            except KeyboardInterrupt:
                self.console.print()  # blank line after ^C
                continue
            except EOFError:
                self.console.print("\n  [dim]Goodbye![/dim]")
                self.state.save()
                return 0

    def dispatch(self, text: str) -> None:
        """Route input to the appropriate handler."""
        self.state.record_command(text)

        if text.startswith("/"):
            self._handle_slash(text)
        else:
            self._handle_bare_input(text)

        # Auto-save after every command
        self.state.save()

    def _handle_slash(self, text: str) -> None:
        """Parse and dispatch a /command."""
        # Split "/command args..." 
        parts = text[1:].split(None, 1)
        cmd_name = parts[0] if parts else ""
        args_str = parts[1] if len(parts) > 1 else ""

        spec = get_command(cmd_name)
        if spec is None:
            self.console.print(f"  [red]Unknown command: /{cmd_name}[/red]")
            self.console.print("  [dim]Type /help for available commands[/dim]")
            return

        handler = HANDLER_MAP.get(spec.handler_name)
        if handler is None:
            self.console.print(f"  [yellow]/{spec.name} is not yet implemented.[/yellow]")
            return

        try:
            handler(self, args_str)
        except (EOFError, KeyboardInterrupt):
            raise  # Let these propagate to the REPL loop
        except Exception as exc:
            self.console.print(f"  [red]Error: {exc}[/red]")
            self.console.print(f"  [dim]{type(exc).__name__}[/dim]")

    def _handle_bare_input(self, text: str) -> None:
        """Handle input without a / prefix — smart shorthand for /run."""
        m = _BARE_RUN_RE.match(text)
        if m:
            project, bug, rest = m.group(1), m.group(2), m.group(3).strip()
            render_tip(
                self.console,
                f"Interpreted as: /run --project {project} --bug {bug}"
                + (f" {rest}" if rest else "")
                + "\n        Next time, use /run directly for explicit control.",
            )
            args = f"--project {project} --bug {bug}"
            if rest:
                args += f" {rest}"
            handler = HANDLER_MAP.get("handle_run")
            if handler:
                try:
                    handler(self, args)
                except Exception as exc:
                    self.console.print(f"  [red]Error: {exc}[/red]")
            return

        self.console.print(f"  [yellow]Unknown input: {text!r}[/yellow]")
        render_tip(self.console, "Commands start with /. Type /help for the full list.")
