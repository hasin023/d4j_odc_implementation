"""Slash command registry — inspired by claw-code's SlashCommandSpec pattern.

Every interactive command is declared as a ``SlashCommandSpec`` in the
``COMMAND_REGISTRY`` list.  The registry drives tab-completion, ``/help``
rendering, and command dispatch.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from .app import ODCApp


@dataclass(frozen=True)
class SlashCommandSpec:
    """Declarative specification for a single slash command."""

    name: str
    summary: str
    aliases: tuple[str, ...] = ()
    argument_hint: str | None = None
    subcommands: tuple[str, ...] = ()
    category: str = "general"
    handler_name: str = ""  # attribute name on handlers module


# ──────────────────────────────────────────────────────────────────────────────
# Registry — every slash command the REPL understands
# ──────────────────────────────────────────────────────────────────────────────

COMMAND_REGISTRY: list[SlashCommandSpec] = [
    # ── Session & Config ────────────────────────────────────────────────
    SlashCommandSpec(
        name="help",
        summary="Show available slash commands",
        category="session",
        handler_name="handle_help",
    ),
    SlashCommandSpec(
        name="status",
        summary="Show current session state",
        category="session",
        handler_name="handle_status",
    ),
    SlashCommandSpec(
        name="config",
        summary="Show or modify configuration",
        argument_hint="[key] [value]",
        subcommands=("provider", "model", "skip-coverage", "include-fix-diff", "prompt-style", "snippet-radius"),
        category="session",
        handler_name="handle_config",
    ),
    SlashCommandSpec(
        name="provider",
        summary="Show or switch active LLM provider",
        argument_hint="[gemini|openrouter|groq|openai-compatible]",
        subcommands=("gemini", "openrouter", "groq", "openai-compatible"),
        category="session",
        handler_name="handle_provider",
    ),
    SlashCommandSpec(
        name="model",
        summary="Show or switch active LLM model",
        argument_hint="[model-name]",
        category="session",
        handler_name="handle_model",
    ),
    SlashCommandSpec(
        name="history",
        summary="Show recent command history",
        argument_hint="[N]",
        category="session",
        handler_name="handle_history",
    ),
    SlashCommandSpec(
        name="bugs",
        summary="List recently worked-on bugs",
        category="session",
        handler_name="handle_bugs",
    ),
    SlashCommandSpec(
        name="clear",
        summary="Clear terminal or reset session",
        argument_hint="[screen|session]",
        subcommands=("screen", "session"),
        category="session",
        handler_name="handle_clear",
    ),
    SlashCommandSpec(
        name="doctor",
        summary="Check environment health",
        category="session",
        handler_name="handle_doctor",
    ),
    SlashCommandSpec(
        name="version",
        summary="Show pipeline version info",
        category="session",
        handler_name="handle_version",
    ),
    SlashCommandSpec(
        name="exit",
        summary="Exit the interactive session",
        aliases=("quit", "q"),
        category="session",
        handler_name="handle_exit",
    ),

    # ── Pipeline Commands ───────────────────────────────────────────────
    SlashCommandSpec(
        name="collect",
        summary="Collect bug evidence (prefix or postfix mode)",
        argument_hint="[--project P --bug N] [--postfix]",
        category="pipeline",
        handler_name="handle_collect",
    ),
    SlashCommandSpec(
        name="classify",
        summary="Classify a saved context (path, run folder, or picker)",
        argument_hint="[context-path|run-folder]",
        category="pipeline",
        handler_name="handle_classify",
    ),
    SlashCommandSpec(
        name="run",
        summary="End-to-end collect + classify",
        argument_hint="[--project P --bug N] [--postfix]",
        category="pipeline",
        handler_name="handle_run",
    ),
    SlashCommandSpec(
        name="compare",
        summary="Compare pre-fix and post-fix classifications",
        argument_hint="--prefix P --postfix Q",
        category="pipeline",
        handler_name="handle_compare",
    ),
    SlashCommandSpec(
        name="compare-batch",
        summary="Batch compare multiple classification pairs",
        aliases=("cb",),
        argument_hint="--prefix-dir D1 --postfix-dir D2",
        category="pipeline",
        handler_name="handle_compare_batch",
    ),

    # ── Show / Inspect ──────────────────────────────────────────────────
    SlashCommandSpec(
        name="show",
        summary="Pretty-print last context, classification, report, or prompt",
        argument_hint="<context|classification|report|prompt>",
        subcommands=("context", "classification", "report", "prompt"),
        category="inspect",
        handler_name="handle_show",
    ),

    # ── Defects4J Proxy ─────────────────────────────────────────────────
    SlashCommandSpec(
        name="d4j",
        summary="Defects4J proxy commands",
        argument_hint="<pids|bids|info> [options]",
        subcommands=("pids", "bids", "info"),
        category="defects4j",
        handler_name="handle_d4j",
    ),

    # ── Multi-Fault ─────────────────────────────────────────────────────
    SlashCommandSpec(
        name="multifault",
        summary="Query multi-fault data for a bug",
        aliases=("mf",),
        argument_hint="[--project P --bug N]",
        category="multifault",
        handler_name="handle_multifault",
    ),
    SlashCommandSpec(
        name="enrich",
        summary="Enrich classification with multi-fault context",
        argument_hint="[classification_path]",
        category="multifault",
        handler_name="handle_enrich",
    ),

    # ── Study Commands ──────────────────────────────────────────────────
    SlashCommandSpec(
        name="study",
        summary="Batch study operations (plan, run, analyze, baseline, naive, export)",
        argument_hint="<plan|run|analyze|baseline|naive|export> [options]",
        subcommands=("plan", "run", "analyze", "baseline", "naive", "export"),
        category="study",
        handler_name="handle_study",
    ),
]


def get_command(name: str) -> SlashCommandSpec | None:
    """Look up a command by name or alias."""
    needle = name.lower().lstrip("/")
    for cmd in COMMAND_REGISTRY:
        if cmd.name == needle:
            return cmd
        if needle in cmd.aliases:
            return cmd
    return None


def all_command_names() -> list[str]:
    """Return all command names and aliases prefixed with /."""
    names: list[str] = []
    for cmd in COMMAND_REGISTRY:
        names.append(f"/{cmd.name}")
        for alias in cmd.aliases:
            names.append(f"/{alias}")
    return sorted(set(names))


def all_completion_entries() -> list[str]:
    """Return all completion strings including subcommands."""
    entries: list[str] = []
    for cmd in COMMAND_REGISTRY:
        entries.append(f"/{cmd.name}")
        for alias in cmd.aliases:
            entries.append(f"/{alias}")
        for sub in cmd.subcommands:
            entries.append(f"/{cmd.name} {sub}")
    return sorted(set(entries))
