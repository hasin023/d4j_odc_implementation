"""Session state management for the interactive CLI.

Persists active bug context, provider/model settings, and command history
across REPL launches.  Auto-resumes on startup by default.
"""

from __future__ import annotations

import json
import os
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


_SESSION_FILE = Path(".dist") / ".odc_session.json"


@dataclass
class SessionState:
    """Mutable state that persists across REPL turns and sessions."""

    # ── identity ─────────────────────────────────────────────────────────
    session_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    workspace_root: str = field(default_factory=lambda: str(Path.cwd()))

    # ── active bug context ───────────────────────────────────────────────
    active_project: str | None = None
    active_bug: int | None = None

    # ── LLM / provider config (session-only, not persisted to .odc.json) ─
    provider: str = field(
        default_factory=lambda: os.environ.get("DEFAULT_LLM_PROVIDER", "gemini")
    )
    model: str = field(
        default_factory=lambda: os.environ.get("DEFAULT_LLM_MODEL", "")
    )

    # ── pipeline settings ────────────────────────────────────────────────
    skip_coverage: bool = True
    include_fix_diff: bool = False
    prompt_style: str = "scientific"
    snippet_radius: int = 12

    # ── last-result references ───────────────────────────────────────────
    last_context_path: str | None = None
    last_classification_path: str | None = None
    last_report_path: str | None = None

    # ── command history (last N commands) ────────────────────────────────
    command_history: list[dict[str, Any]] = field(default_factory=list)

    # ── recent bugs worked on ────────────────────────────────────────────
    recent_bugs: list[dict[str, Any]] = field(default_factory=list)

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self, path: Path | None = None) -> Path:
        """Persist session state to JSON."""
        path = path or _SESSION_FILE
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")
        return path

    @classmethod
    def load(cls, path: Path | None = None) -> "SessionState":
        """Load session state from JSON, falling back to defaults."""
        path = path or _SESSION_FILE
        if not path.exists():
            return cls()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            # Filter out unknown keys for forward-compat
            known = {f.name for f in cls.__dataclass_fields__.values()}
            filtered = {k: v for k, v in data.items() if k in known}
            return cls(**filtered)
        except (json.JSONDecodeError, TypeError, KeyError):
            return cls()

    @classmethod
    def auto_resume(cls) -> "SessionState":
        """Auto-resume the last session, or start fresh."""
        state = cls.load()
        # Re-derive provider/model from env on every launch so .env changes
        # are picked up, but keep active bug context
        state.provider = os.environ.get("DEFAULT_LLM_PROVIDER", state.provider)
        if not state.model:
            state.model = os.environ.get("DEFAULT_LLM_MODEL", "")
        return state

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def set_active_bug(self, project: str, bug: int) -> None:
        self.active_project = project
        self.active_bug = bug
        # Track in recent bugs
        entry = {"project": project, "bug": bug, "at": datetime.now(timezone.utc).isoformat()}
        # Remove duplicate if exists
        self.recent_bugs = [
            b for b in self.recent_bugs
            if not (b.get("project") == project and b.get("bug") == bug)
        ]
        self.recent_bugs.insert(0, entry)
        # Keep last 20
        self.recent_bugs = self.recent_bugs[:20]

    def record_command(self, command: str) -> None:
        self.command_history.append({
            "cmd": command,
            "at": datetime.now(timezone.utc).isoformat(),
        })
        # Keep last 100
        self.command_history = self.command_history[-100:]

    def clear(self) -> None:
        """Reset session state (fresh start)."""
        new = SessionState()
        # Preserve provider/model from env
        new.provider = self.provider
        new.model = self.model
        self.__dict__.update(new.__dict__)

    @property
    def has_active_bug(self) -> bool:
        return self.active_project is not None and self.active_bug is not None

    @property
    def active_bug_label(self) -> str:
        if self.has_active_bug:
            return f"{self.active_project}-{self.active_bug}"
        return "(none)"

    @property
    def mode_suffix(self) -> str:
        return "postfix" if self.include_fix_diff else "prefix"
