"""Tab-completion and interactive file/manifest selection.

Provides:
  - ``SlashCommandCompleter``  — autocomplete for /commands and subcommands
  - ``pick_file_interactive``  — arrow-key navigable file selector for
    context.json and manifest files (user's review comment requirement)
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import radiolist_dialog


class SlashCommandCompleter(Completer):
    """Autocomplete slash commands, subcommands, and provider/model names."""

    def __init__(self, completion_entries: list[str]) -> None:
        # All entries are pre-built strings like "/run", "/d4j pids", "/provider gemini"
        self.entries = sorted(set(completion_entries))

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor.lstrip()
        if not text.startswith("/"):
            return

        for entry in self.entries:
            if entry.startswith(text) and entry != text:
                yield Completion(
                    entry,
                    start_position=-len(text),
                    display=entry,
                    display_meta=self._meta_for(entry),
                )

    @staticmethod
    def _meta_for(entry: str) -> str:
        """Short meta hint shown beside completion candidate."""
        # Could be enhanced with command summaries
        return ""


# ──────────────────────────────────────────────────────────────────────────────
# Interactive file pickers  (arrow-key navigable dropdown)
# ──────────────────────────────────────────────────────────────────────────────

def discover_context_files(base: Path | None = None) -> list[Path]:
    """Find all context.json files under .dist/runs/ by default."""
    base = base or (Path(".dist") / "runs")
    if not base.exists():
        return []
    return sorted(base.rglob("context.json"))


def discover_manifests(base: Path | None = None) -> list[Path]:
    """Find all manifest*.json files under .dist/study/."""
    base = base or Path(".dist") / "study"
    if not base.exists():
        return []
    return sorted(
        p for p in base.glob("manifest*.json")
        if p.is_file()
    )


def discover_classifications(base: Path | None = None) -> list[Path]:
    """Find all classification.json files under .dist/."""
    base = base or Path(".dist")
    if not base.exists():
        return []
    return sorted(base.rglob("classification.json"))


def pick_file_interactive(
    files: list[Path],
    title: str = "Select a file",
    text: str = "Use ↑↓ arrow keys to navigate, Enter to select:",
) -> Path | None:
    """Show an arrow-key navigable radiolist dialog for file selection.

    Returns the selected Path, or None if the user cancelled.
    """
    if not files:
        return None

    values = [
        (f, str(f.relative_to(Path.cwd())) if f.is_relative_to(Path.cwd()) else str(f))
        for f in files
    ]

    result = radiolist_dialog(
        title=HTML(f"<b>{title}</b>"),
        text=text,
        values=values,
    ).run()

    return result
