"""The scientific strategy engine (--strategy scientific): the enforced loop.

Implements the scientific method at BOTH levels (see AGENTS.md §11.13):
- Process level (Zeller): the loop is SEEDED with the failure observation —
  the same truncated evidence payload the single-shot prompt uses.
- Loop-iteration level (AutoSD, Kang et al. EMSE 2024, Fig. 1): each turn the
  LLM commits Hypothesis → Prediction, then either runs an Experiment (an
  evidence probe the harness executes against the FULL context.json) or
  Concludes. The probe result is the exogenous Observation: it is returned by
  the harness from recorded execution evidence, so the model cannot fabricate
  it — the falsifiability property the single-shot narration lacks.

Tier-1 probes serve ONLY held-back parts of the already-collected context.json
(the single-shot prompt truncates to 5 failures / 15 trace lines / 8+3 snippets
/ 6 coverage classes). No Defects4J execution, no filesystem access.
"""

from __future__ import annotations

import json
import time
from typing import Any

from .llm import LLMClient, LLMError, classification_response_schema
from .models import BugContext, ClassificationResult
from .odc import (
    OTHER_TYPE_NAME,
    TAXONOMY_OPEN,
    allowed_type_names,
    taxonomy_markdown,
)
from .parsing import extract_json_object
from .prompting import sanitize_bug_report

AGENT_MAX_TURNS = 6

# Per-turn cap on the persisted observation payload. The observation is what
# makes the loop auditable — without it the transcript shows what the model
# predicted but never what came back, so a prediction can never be scored
# confirmed or refuted. Full payloads are unbounded (a `snippet` probe can
# return a whole Java class), so they are stored truncated, with the original
# length recorded alongside.
OBSERVATION_MAX_CHARS = 2000

PROBE_NAMES = (
    "list_evidence",
    "full_stack_trace",
    "snippet",
    "coverage",
    "bug_report",
)


# ---------------------------------------------------------------------------
# Per-turn response schema (the seam added to llm.complete in the refactor)
# ---------------------------------------------------------------------------

def turn_response_schema(taxonomy: str) -> dict:
    """Schema for ONE loop turn: hypothesis + prediction always required;
    then either a probe request (experiment) or a full conclusion."""
    conclusion = classification_response_schema(taxonomy)
    return {
        "type": "object",
        "properties": {
            "hypothesis": {"type": "string"},
            "prediction": {"type": "string"},
            "action": {"type": "string", "enum": ["request_evidence", "conclude"]},
            "probe": {
                "type": ["object", "null"],
                "properties": {
                    "name": {"type": "string", "enum": list(PROBE_NAMES)},
                    "argument": {"type": ["string", "null"]},
                },
                "required": ["name"],
            },
            "conclusion": {**conclusion, "type": ["object", "null"]},
        },
        "required": ["hypothesis", "prediction", "action"],
    }


# ---------------------------------------------------------------------------
# Tier-1 probes over the full BugContext
# ---------------------------------------------------------------------------

def execute_probe(context: BugContext, name: str, argument: str | None) -> dict[str, Any]:
    """Run one evidence probe. Always returns a JSON-serializable observation;
    unknown targets return an 'available' inventory instead of failing, so the
    model can self-correct on the next turn."""
    argument = (argument or "").strip()

    if name == "list_evidence":
        return {
            "failing_tests": [f.test_name for f in context.failures],
            "production_snippet_classes": sorted({
                s.class_name for s in context.code_snippets
                if not s.reason.startswith("Test source:")
            }),
            "test_snippet_classes": sorted({
                s.class_name for s in context.code_snippets
                if s.reason.startswith("Test source:")
            }),
            "coverage_classes": [c.class_name for c in context.coverage],
            "bug_report_available": bool(context.bug_report_content),
        }

    if name == "full_stack_trace":
        matches = [f for f in context.failures if argument and argument in f.test_name]
        if not matches:
            return {
                "error": f"no failing test matches {argument!r}",
                "available": [f.test_name for f in context.failures],
            }
        return {
            "traces": [
                {"test_name": f.test_name, "headline": f.headline, "stack_trace": f.stack_trace}
                for f in matches
            ]
        }

    if name == "snippet":
        matches = [s for s in context.code_snippets if argument and argument in s.class_name]
        if not matches:
            return {
                "error": f"no snippet matches {argument!r}",
                "available": sorted({s.class_name for s in context.code_snippets}),
            }
        return {
            "snippets": [
                {
                    "class_name": s.class_name,
                    "reason": s.reason,
                    "file_path": s.file_path,
                    "start_line": s.start_line,
                    "end_line": s.end_line,
                    "focus_line": s.focus_line,
                    "content": s.content,
                }
                for s in matches
            ]
        }

    if name == "coverage":
        matches = [c for c in context.coverage if argument and argument in c.class_name]
        if not matches:
            return {
                "error": f"no coverage matches {argument!r}",
                "available": [c.class_name for c in context.coverage],
            }
        return {
            "coverage": [
                {
                    "class_name": c.class_name,
                    "line_rate": c.line_rate,
                    "branch_rate": c.branch_rate,
                    "covered_lines": [
                        {"line_number": line.line_number, "hits": line.hits}
                        for line in c.covered_lines
                    ],
                }
                for c in matches
            ]
        }

    if name == "bug_report":
        if not context.bug_report_content:
            return {"error": "no bug report was collected for this bug"}
        # Pre-fix arm: the probe must honour the same sanitization as the seed
        # payload — comments/status post-date the report and leak fix knowledge.
        report = (
            context.bug_report_content
            if context.fix_diff
            else sanitize_bug_report(context.bug_report_content)
        )
        return {"bug_report": report}

    return {"error": f"unknown probe {name!r}", "available": list(PROBE_NAMES)}


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

def _agent_system_prompt(taxonomy: str) -> str:
    parts = [
        "You are an expert software defect analyst specializing in Orthogonal Defect "
        "Classification (ODC), working as a scientific-debugging agent.",
        "",
        "You classify ONE bug through an iterative scientific loop. The failure has "
        "already been OBSERVED — its evidence summary is in the first user message. "
        "Each turn you MUST:",
        "1. HYPOTHESIS: a specific root-cause mechanism consistent with all observations so far.",
        "2. PREDICTION: what specific evidence you expect to see IF the hypothesis is true.",
        "3. Then EITHER request one evidence probe to TEST the prediction "
        "(action=request_evidence) OR conclude (action=conclude) with the full classification.",
        "",
        "Available probes (the harness executes them against recorded evidence and "
        "returns the real result — you cannot see anything except what probes return):",
        "- list_evidence: inventory of all available evidence (no argument)",
        "- full_stack_trace: full trace of a failing test (argument: test-name substring)",
        "- snippet: full source snippet(s) of a class (argument: class-name substring)",
        "- coverage: full covered-line data of a class (argument: class-name substring)",
        "- bug_report: the full bug report text (no argument)",
        "",
        "RULES:",
        "- Commit the prediction BEFORE seeing the probe result; if the result refutes it, "
        "revise the hypothesis on the next turn.",
        "- Do not re-request evidence you already received.",
        "- Conclude as soon as the evidence supports one type; probes are limited.",
        "- Do NOT default to 'Function/Class/Object'; it requires evidence of a "
        "design-level capability gap, not merely wrong behaviour in existing code.",
        f"- The final odc_type must be one of: {', '.join(allowed_type_names(taxonomy))}.",
        "",
        taxonomy_markdown(taxonomy),
        "",
        "Every response must be a single JSON object matching the turn schema "
        "(hypothesis, prediction, action, probe?, conclusion?).",
    ]
    if taxonomy == TAXONOMY_OPEN:
        parts.append(
            "If concluding with 'Other', the conclusion MUST include other_justification, "
            "nearest_type, and other_confidence."
        )
    return "\n".join(parts)


def _force_conclude_message() -> str:
    return (
        "Probe budget exhausted. You MUST now conclude (action=conclude) with the full "
        "classification based on the evidence gathered so far. Set needs_human_review "
        "to true if the evidence remained insufficient."
    )


# ---------------------------------------------------------------------------
# The loop
# ---------------------------------------------------------------------------

def run_agentic_classification(
    *,
    context: BugContext,
    client: LLMClient,
    taxonomy: str,
    max_turns: int = AGENT_MAX_TURNS,
    validate_conclusion,
) -> ClassificationResult:
    """Run the hypothesis→prediction→experiment→observation loop for one bug.

    ``validate_conclusion(payload) -> ClassificationResult`` is injected by
    pipeline.classify_bug_context so validation rules stay in one place.
    Returns the validated result with the full turn transcript attached.
    """
    from .prompting import _context_payload  # same-package reuse of the seed payload

    seed = _context_payload(context)
    messages: list[dict[str, str]] = [
        {"role": "system", "content": _agent_system_prompt(taxonomy)},
        {
            "role": "user",
            "content": (
                "Initial failure observation (truncated evidence summary — use probes "
                "for anything held back):\n" + json.dumps(seed, indent=2)
            ),
        },
    ]
    schema = turn_response_schema(taxonomy)
    transcript: list[dict[str, Any]] = []
    served_probes: set[tuple[str, str]] = set()
    forced = False
    probe_misses = 0
    loop_started = time.monotonic()

    for turn_index in range(1, max_turns + 1):
        turn_started = time.monotonic()
        raw = client.complete(messages, response_schema=schema)
        turn = extract_json_object(raw)
        messages.append({"role": "assistant", "content": raw})

        record: dict[str, Any] = {
            "turn": turn_index,
            "hypothesis": str(turn.get("hypothesis", "")).strip(),
            "prediction": str(turn.get("prediction", "")).strip(),
            "action": turn.get("action"),
            # True only on a turn that ran AFTER the force-conclude message,
            # i.e. the model was told turns had run out.
            "forced": forced,
        }

        if turn.get("action") == "conclude" and isinstance(turn.get("conclusion"), dict):
            record["conclusion_odc_type"] = turn["conclusion"].get("odc_type")
            record["duration_seconds"] = round(time.monotonic() - turn_started, 3)
            transcript.append(record)
            result = validate_conclusion(turn["conclusion"])
            result.turns = transcript
            result.termination_reason = "forced_max_turns" if forced else "concluded"
            result.loop_duration_seconds = round(time.monotonic() - loop_started, 3)
            result.probe_misses = probe_misses
            if forced:
                result.needs_human_review = True
            return result

        # request_evidence (or malformed) → execute probe, append observation
        probe = turn.get("probe") if isinstance(turn.get("probe"), dict) else {}
        probe_name = str(probe.get("name", "list_evidence"))
        probe_argument = probe.get("argument")
        probe_key = (probe_name, str(probe_argument or ""))
        if probe_key in served_probes:
            observation: dict[str, Any] = {
                "error": "probe already served this exact request — use a different probe or conclude"
            }
        else:
            served_probes.add(probe_key)
            observation = execute_probe(context, probe_name, probe_argument)

        record["probe"] = {"name": probe_name, "argument": probe_argument}
        record["observation_summary"] = (
            sorted(observation.keys()) if "error" not in observation else observation["error"]
        )
        if "error" in observation:
            probe_misses += 1
        record.update(_render_observation(observation))
        record["duration_seconds"] = round(time.monotonic() - turn_started, 3)
        transcript.append(record)

        remaining = max_turns - turn_index
        observation_message = f"Observation (probe {probe_name!r}):\n" + json.dumps(observation, indent=2)
        if remaining == 1:
            forced = True
            observation_message += "\n\n" + _force_conclude_message()
        messages.append({"role": "user", "content": observation_message})

    raise LLMError(
        f"Agentic loop exhausted {max_turns} turns without a conclusion "
        f"(probe misses: {probe_misses}; transcript: {json.dumps(transcript)[:500]})"
    )


def _render_observation(observation: dict[str, Any]) -> dict[str, Any]:
    """Persist what the probe actually returned, capped at OBSERVATION_MAX_CHARS.

    Records the full length either way, so a truncated observation is still
    honest about how much was withheld."""
    text = json.dumps(observation, indent=2, default=str)
    truncated = len(text) > OBSERVATION_MAX_CHARS
    return {
        "observation": text[:OBSERVATION_MAX_CHARS],
        "observation_truncated": truncated,
        "observation_chars": len(text),
    }
