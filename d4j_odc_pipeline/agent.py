"""The scientific strategy engine (--strategy scientific): the enforced loop.

Implements the scientific method at BOTH levels (see AGENTS.md §11.13):
- Process level (Zeller): the loop is SEEDED with the failure observation —
  the same truncated evidence payload the single-shot prompt uses.
- Loop-iteration level (AutoSD, Kang et al. EMSE 2024, Fig. 1): each turn the
  LLM judges the previous experiment (Conclusion: supported / refuted /
  inconclusive), commits Hypothesis → Prediction, then either runs an
  Experiment (an evidence probe the harness executes) or concludes. The probe
  result is the exogenous Observation: it is returned by the harness from
  recorded evidence, so the model cannot fabricate it.

The system prompt carries the SAME ODC guidance as `few` (taxonomy, diagnostic
decision process, worked examples, post-fix diff guidance — shared helpers in
prompting.py), so `scientific` = `few` + the loop, nothing else.

When the evidence is enough (the evidence gate, enforced by the harness — not
left to the model; see `_evidence_gate`): a conclusion is accepted only if the
experiment just run returned real evidence, the model judged it SUPPORTED with
a verbatim quote the harness finds in that observation, it states the concrete
fix (ODC types the nature of the fix), and the concluded type is one of the two
types that experiment was designed to discriminate. This is AutoSD's
<DONE>-after-a-supported-hypothesis rule, made verifiable. A rejected
conclusion costs a turn; running out of turns forces a conclusion that is
flagged for human review.

Probes:
- Tier 1 serve held-back parts of the already-collected context.json (the
  single-shot prompt truncates to 5 failures / 15 trace lines / 8+3 snippets
  / 6 coverage classes).
- Tier 2 `source` reads the buggy program's source from a Defects4J checkout
  (RepairAgent-style read tools: outline / method / line range), annotated
  with the lines the failing tests executed per recorded coverage. Only
  available when the caller passes `source_dirs`.
"""

from __future__ import annotations

import json
import re
import time
from functools import lru_cache
from pathlib import Path
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
from .prompting import (
    _critical_rules,
    _evidence_mode_guidance,
    _few_shot_examples,
    sanitize_bug_report,
)

AGENT_MAX_TURNS = 8

# Per-turn cap on the persisted observation payload. The observation is what
# makes the loop auditable — without it the transcript shows what the model
# predicted but never what came back, so a prediction can never be scored
# confirmed or refuted. Full payloads are unbounded (a `snippet` probe can
# return a whole Java class), so they are stored truncated, with the original
# length recorded alongside.
OBSERVATION_MAX_CHARS = 2000

# `source` probe: files up to this many lines are returned whole; longer ones
# return an outline, and a method body / line range is capped at this length.
SOURCE_MAX_LINES = 150
# How many executed classes list_evidence names.
EXECUTED_CLASSES_LIMIT = 40
# Shortest evidence quote the gate accepts (after whitespace normalisation);
# shorter strings ("null", "return") match almost any observation.
MIN_QUOTE_CHARS = 12

PROBE_NAMES = (
    "list_evidence",
    "full_stack_trace",
    "snippet",
    "source",
    "coverage",
    "bug_report",
)
VERDICTS = ("supported", "refuted", "inconclusive", "none")


# ---------------------------------------------------------------------------
# Per-turn response schema (the seam added to llm.complete in the refactor)
# ---------------------------------------------------------------------------

def turn_response_schema(taxonomy: str) -> dict:
    """Schema for ONE loop turn: verdict on the last experiment, hypothesis,
    the two types it discriminates, prediction; then either a probe request
    (experiment) or a full conclusion."""
    conclusion = classification_response_schema(taxonomy)
    types = allowed_type_names(taxonomy)
    return {
        "type": "object",
        "properties": {
            "verdict": {"type": "string", "enum": list(VERDICTS)},
            "evidence_quote": {"type": ["string", "null"]},
            "hypothesis": {"type": "string"},
            "leading_type": {"type": "string", "enum": types},
            "rival_type": {"type": "string", "enum": types},
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
            "predicted_fix": {"type": ["string", "null"]},
            "conclusion": {**conclusion, "type": ["object", "null"]},
        },
        "required": ["verdict", "hypothesis", "leading_type", "rival_type", "prediction", "action"],
    }


# ---------------------------------------------------------------------------
# Class-name matching shared by every probe that takes a class argument
# ---------------------------------------------------------------------------

def _looks_like_test(class_name: str) -> bool:
    from .pipeline import _looks_like_test_class

    return _looks_like_test_class(class_name) or ".junit." in class_name


def _match_classes(names, argument: str) -> list[str]:
    """Resolve a class argument against known class names, most specific first:
    exact FQCN → simple name → substring. Substring matches drop test classes
    unless the argument itself names a test — the old bare-substring match
    served `DfpTest` for `Dfp` and `ShapeUtilitiesTests` for `ShapeUtilities`,
    and the model then reasoned as if it had read production code."""
    arg = (argument or "").strip()
    if not arg:
        return []
    names = list(dict.fromkeys(names))
    candidates = [arg]
    # `Foo.method` / `org.x.Foo.method` → also try the class part.
    head, _, last = arg.rpartition(".")
    if head and last[:1].islower():
        candidates.append(head)
    for candidate in candidates:
        exact = [n for n in names if n == candidate]
        if exact:
            return exact
        simple = candidate.rsplit(".", 1)[-1]
        by_simple = [n for n in names if n.rsplit(".", 1)[-1].split("$")[0] == simple]
        if by_simple:
            return by_simple
        substring = [n for n in names if candidate in n]
        if not _looks_like_test(candidate):
            substring = [n for n in substring if not _looks_like_test(n)]
        if substring:
            return substring
    return []


def _executed_lines(context: BugContext, class_name: str) -> set[int]:
    """Lines of `class_name` (incl. its inner classes) the failing tests hit."""
    outer = class_name.split("$")[0]
    return {
        line.line_number
        for cov in context.coverage
        if cov.class_name.split("$")[0] == outer
        for line in cov.covered_lines
        if line.hits and line.hits > 0
    }


# ---------------------------------------------------------------------------
# Tier-2 `source` probe: read the buggy program (RepairAgent-style read tools)
# ---------------------------------------------------------------------------

# ponytail: regex outline, not a Java parser — misses odd formatting (a
# signature split before its name, braces inside string literals). Swap in
# javalang/tree-sitter if outlines prove unreliable.
_DECLARATION = re.compile(
    r"^\s*(?:@\w+(?:\([^)]*\))?\s+)*"
    r"((?:public|protected|private|static|final|abstract|synchronized|native|strictfp|default)\s+)*"
    r"(?:<[^>]*>\s+)?"
    r"([\w$.]+(?:<[^()]*?>)?(?:\[\])*\s+)?"
    r"([A-Za-z_$][\w$]*)\s*\("
)
_NOT_A_DECLARATION = {
    "if", "for", "while", "switch", "catch", "return", "new", "throw", "else",
    "synchronized", "super", "this", "assert", "case", "do", "try",
}


def _declarations(lines: list[str]) -> list[tuple[int, str]]:
    """(1-based line, name) of every method/constructor declaration."""
    found = []
    for number, line in enumerate(lines, start=1):
        match = _DECLARATION.match(line)
        if not match:
            continue
        modifiers, return_type, name = match.groups()
        first_word = line.strip().split(maxsplit=1)[0]
        if name in _NOT_A_DECLARATION or first_word in _NOT_A_DECLARATION:
            continue
        if not modifiers and not return_type:
            continue  # a bare call `foo(x,` — not a declaration
        found.append((number, name))
    return found


def _block_end(lines: list[str], start: int) -> int:
    """Last line of the brace block opened at/after `start` (1-based)."""
    depth, opened = 0, False
    for number in range(start, len(lines) + 1):
        text = lines[number - 1]
        depth += text.count("{") - text.count("}")
        opened = opened or "{" in text
        if opened and depth <= 0:
            return number
        if not opened and text.rstrip().endswith(";"):
            return number  # abstract / interface method
    return len(lines)


@lru_cache(maxsize=8)
def _source_index(source_dirs: tuple[str, ...]) -> dict[str, str]:
    """FQCN → .java path for every source file under the checkout's dirs."""
    index: dict[str, str] = {}
    for directory in source_dirs:
        root = Path(directory)
        for java_file in root.rglob("*.java"):
            fqcn = ".".join(java_file.relative_to(root).with_suffix("").parts)
            index.setdefault(fqcn, str(java_file))
    return index


def _render_lines(lines: list[str], start: int, end: int, executed: set[int]) -> str:
    return "\n".join(
        f"{'*' if n in executed else ' '} {n:5d}: {lines[n - 1]}" for n in range(start, end + 1)
    )


def _source_probe(context: BugContext, argument: str, source_dirs) -> dict[str, Any]:
    if not source_dirs:
        return {"error": "source unavailable: this run has no checkout of the buggy program; "
                         "use snippet/coverage/full_stack_trace instead"}
    target, _, method = argument.partition("#")
    line_range = None
    if not method and ":" in target:
        target, _, spec = target.partition(":")
        bounds = re.fullmatch(r"\s*(\d+)\s*-\s*(\d+)\s*", spec)
        if not bounds:
            return {"error": f"bad line range {spec!r}; use Class:START-END"}
        line_range = (int(bounds.group(1)), int(bounds.group(2)))
    index = _source_index(tuple(str(d) for d in source_dirs))
    matches = sorted({m.split("$")[0] for m in _match_classes(index.keys(), target.strip())})
    if not matches:
        return {"error": f"no source file for {target.strip()!r}",
                "hint": "call list_evidence for executed_production_classes"}
    if len(matches) > 1:
        return {"error": f"{target.strip()!r} is ambiguous; use a fully-qualified name",
                "candidates": matches[:20]}
    class_name = matches[0]
    lines = Path(index[class_name]).read_text(encoding="utf-8", errors="replace").splitlines()
    executed = _executed_lines(context, class_name)
    result: dict[str, Any] = {
        "class_name": class_name,
        "total_lines": len(lines),
        "legend": "'*' = line executed by the failing test(s) per recorded coverage",
    }

    if method:
        starts = [n for n, name in _declarations(lines) if name == method.strip()]
        if not starts:
            # Executed methods first — those are the ones worth reading.
            ranked = sorted(
                _declarations(lines),
                key=lambda d: (-sum(1 for n in executed if d[0] <= n <= _block_end(lines, d[0])), d[0]),
            )
            names = list(dict.fromkeys(name for _, name in ranked))
            return {"error": f"no method {method.strip()!r} in {class_name}", "methods": names[:80]}
        bodies = []
        for start in starts[:3]:  # overloads
            end = min(_block_end(lines, start), start + SOURCE_MAX_LINES - 1)
            bodies.append(_render_lines(lines, start, end, executed))
        result["content"] = "\n\n".join(bodies)
        return result

    if line_range:
        start = max(1, min(line_range))
        end = min(len(lines), max(line_range), start + SOURCE_MAX_LINES - 1)
        result["content"] = _render_lines(lines, start, end, executed)
        return result

    if len(lines) <= SOURCE_MAX_LINES:
        result["content"] = _render_lines(lines, 1, len(lines), executed)
        return result

    outline = []
    for start, name in _declarations(lines):
        end = _block_end(lines, start)
        outline.append({
            "line": start,
            "end_line": end,
            "signature": lines[start - 1].strip()[:160],
            "executed_lines": sum(1 for n in executed if start <= n <= end),
        })
    result["outline"] = outline
    result["hint"] = (f"file is {len(lines)} lines; request 'Class#methodName' or "
                      f"'Class:START-END' (max {SOURCE_MAX_LINES} lines)")
    return result


# ---------------------------------------------------------------------------
# Probe dispatch
# ---------------------------------------------------------------------------

def execute_probe(
    context: BugContext,
    name: str,
    argument: str | None,
    source_dirs: list[Path] | None = None,
) -> dict[str, Any]:
    """Run one evidence probe. Always returns a JSON-serializable observation;
    unknown targets return an 'available' inventory instead of failing, so the
    model can self-correct on the next turn."""
    argument = (argument or "").strip()

    if name == "list_evidence":
        executed = sorted(
            (
                (sum(1 for line in c.covered_lines if line.hits and line.hits > 0), c.class_name)
                for c in context.coverage
                if not _looks_like_test(c.class_name)
            ),
            reverse=True,
        )
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
            "executed_production_classes": [
                {"class_name": class_name, "executed_lines": count}
                for count, class_name in executed[:EXECUTED_CLASSES_LIMIT]
                if count
            ],
            "source_probe_available": bool(source_dirs),
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
        wanted = set(_match_classes((s.class_name for s in context.code_snippets), argument))
        if not wanted:
            observation: dict[str, Any] = {
                "error": f"no snippet matches {argument!r}",
                "available": sorted({s.class_name for s in context.code_snippets}),
            }
            if source_dirs:
                observation["hint"] = "snippets are pre-extracted windows; use `source` to read any class"
            return observation
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
                for s in context.code_snippets
                if s.class_name in wanted
            ]
        }

    if name == "source":
        return _source_probe(context, argument, source_dirs)

    if name == "coverage":
        wanted = set(_match_classes((c.class_name for c in context.coverage), argument))
        if not wanted:
            return {
                "error": f"no coverage matches {argument!r}",
                "available": [c.class_name for c in context.coverage if c.covered_lines][:80],
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
                for c in context.coverage
                if c.class_name in wanted
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
# The evidence gate: when is the evidence enough to conclude?
# ---------------------------------------------------------------------------

def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _string_leaves(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [leaf for item in value.values() for leaf in _string_leaves(item)]
    if isinstance(value, list):
        return [leaf for item in value for leaf in _string_leaves(item)]
    return []


def _quote_found(quote: str | None, observation: dict[str, Any] | None) -> bool:
    """Is `quote` a verbatim excerpt of what the probe actually returned?

    Checked against both the JSON the model was shown (escaped quotes) and
    the raw string values (unescaped), whitespace-normalised."""
    if not quote or observation is None:
        return False
    needle = _normalize(quote.strip().strip("`'\""))
    if len(needle) < MIN_QUOTE_CHARS:
        return False
    haystack = _normalize(json.dumps(observation) + "\n" + "\n".join(_string_leaves(observation)))
    return needle in haystack


def _evidence_gate(
    turn: dict[str, Any],
    last_experiment: dict[str, Any] | None,
) -> str | None:
    """Return why a conclusion is NOT yet justified, or None if it is.

    `last_experiment` is the most recent probe that returned evidence:
    {"observation": ..., "leading_type": ..., "rival_type": ...} as committed
    on the turn that requested it."""
    if last_experiment is None:
        return ("no experiment has returned evidence yet — run a probe that tests your "
                "prediction before concluding")
    if turn.get("verdict") != "supported":
        return (f"verdict is {turn.get('verdict')!r}; you may only conclude after an "
                "experiment SUPPORTS the hypothesis")
    if not _quote_found(turn.get("evidence_quote"), last_experiment["observation"]):
        return (f"evidence_quote was not found verbatim (min {MIN_QUOTE_CHARS} chars) in the "
                "last experiment's observation — quote the exact text that supports it")
    if len(str(turn.get("predicted_fix") or "").strip()) < 10:
        return "predicted_fix is missing — state the concrete code change that would fix the defect"
    concluded = (turn.get("conclusion") or {}).get("odc_type")
    tested = {last_experiment.get("leading_type"), last_experiment.get("rival_type")} - {None}
    if tested and concluded not in tested and concluded != OTHER_TYPE_NAME:
        return (f"concluded type {concluded!r} was not under test — the last experiment "
                f"discriminated {' vs '.join(sorted(tested))}; test {concluded!r} first")
    return None


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

def _agent_system_prompt(taxonomy: str, has_fix_diff: bool = False) -> str:
    parts = [
        "You are an expert software defect analyst specializing in Orthogonal Defect "
        "Classification (ODC), working as a scientific-debugging agent.",
        "",
    ]
    # Same task statement as `few` in both evidence modes (the pre-fix line used
    # to exist only in `few`, although the strategies should differ only by the
    # loop — docs/prompt_review_v3.md, block 1b).
    parts.extend(_evidence_mode_guidance(has_fix_diff))
    parts.append("")
    parts.extend([
        "You classify ONE bug through an iterative scientific loop. The failure has "
        "already been OBSERVED — its evidence summary is in the first user message. "
        "Each turn you MUST:",
        "1. VERDICT on your previous experiment: supported / refuted / inconclusive "
        "(verdict=none on turn 1), with evidence_quote = a short VERBATIM excerpt of that "
        "observation that decides it. The harness checks the quote against the real observation.",
        "2. HYPOTHESIS: a specific root-cause mechanism consistent with ALL observations so far. "
        "After a refuted verdict the hypothesis must change.",
        "3. leading_type = the ODC type your hypothesis implies; rival_type = the most plausible "
        "competing type.",
        "4. PREDICTION: what the next evidence will show if the hypothesis is true — chosen so it "
        "would come out DIFFERENTLY if rival_type were right (e.g. 'no null guard before the "
        "dereference at line N' vs 'the guard exists but the formula is wrong').",
        "5. EITHER request ONE probe that tests the prediction (action=request_evidence) OR "
        "conclude (action=conclude).",
        "",
        "Available probes (the harness executes them and returns the real result):",
        "- list_evidence: inventory — failing tests, snippet classes, the production classes the "
        "failing tests executed, whether `source` is available (no argument)",
        "- source: read the buggy program's code (argument: 'Class' for the whole file or an "
        "outline of a long one, 'Class#method' for a method body, 'Class:START-END' for a line "
        "range). Lines marked '*' were executed by the failing tests. Best probe for production code.",
        "- snippet: the pre-extracted code windows around stack frames (argument: class name)",
        "- full_stack_trace: full trace of a failing test (argument: test-name substring)",
        "- coverage: covered-line data of a class (argument: class name)",
        "- bug_report: the full bug report text (no argument)",
        "",
        "WHEN THE EVIDENCE IS ENOUGH — the harness enforces this; a conclusion that fails it is "
        "rejected and costs a turn. Conclude only when ALL hold:",
        "a. your previous turn ran a probe that returned evidence (not an error);",
        "b. verdict=supported for that experiment, with evidence_quote copied verbatim from it;",
        "c. predicted_fix states the concrete code change that would fix the defect — the ODC "
        "type is the nature of THAT change, so classify the fix, not the symptom or the context;",
        "d. conclusion.odc_type is the leading_type or rival_type of that experiment.",
        "Until then keep experimenting. If the turn budget runs out you are forced to conclude "
        "and the result is flagged for human review.",
        "",
        "RULES:",
        "- Commit the prediction BEFORE seeing the probe result.",
        "- Never repeat a probe: every result stays in this conversation.",
        "- If a probe returns an error or the wrong class, change the argument or the probe.",
        f"- The final odc_type must be one of: {', '.join(allowed_type_names(taxonomy))}.",
    ])
    parts.extend(_critical_rules())
    parts.extend(["", taxonomy_markdown(taxonomy)])
    parts.extend(["", _few_shot_examples(), ""])
    parts.append(
        "Every response must be a single JSON object matching the turn schema (verdict, "
        "evidence_quote, hypothesis, leading_type, rival_type, prediction, action, probe?, "
        "predicted_fix?, conclusion?)."
    )
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
    source_dirs: list[Path] | None = None,
) -> ClassificationResult:
    """Run the verdict→hypothesis→prediction→experiment→observation loop.

    ``validate_conclusion(payload) -> ClassificationResult`` is injected by
    pipeline.classify_bug_context so validation rules stay in one place.
    ``source_dirs`` enables the tier-2 `source` probe (a checkout's source
    roots). Returns the validated result with the full turn transcript attached.
    """
    from .prompting import _context_payload  # same-package reuse of the seed payload

    seed = _context_payload(context)
    messages: list[dict[str, str]] = [
        {"role": "system", "content": _agent_system_prompt(taxonomy, bool(context.fix_diff))},
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
    served_at: dict[tuple[str, str], int] = {}
    last_experiment: dict[str, Any] | None = None
    forced = False
    probe_misses = 0
    gate_rejections = 0
    loop_started = time.monotonic()

    for turn_index in range(1, max_turns + 1):
        turn_started = time.monotonic()
        raw = client.complete(messages, response_schema=schema)
        turn = extract_json_object(raw)
        messages.append({"role": "assistant", "content": raw})

        record: dict[str, Any] = {
            "turn": turn_index,
            "verdict": turn.get("verdict"),
            "evidence_quote": turn.get("evidence_quote"),
            # Checked against the observation the verdict judges, so the
            # confirm/refute record is exogenous rather than self-reported.
            "quote_verified": _quote_found(
                turn.get("evidence_quote"),
                last_experiment["observation"] if last_experiment else None,
            ),
            "hypothesis": str(turn.get("hypothesis", "")).strip(),
            "leading_type": turn.get("leading_type"),
            "rival_type": turn.get("rival_type"),
            "prediction": str(turn.get("prediction", "")).strip(),
            "action": turn.get("action"),
            # True only on a turn that ran AFTER the force-conclude message,
            # i.e. the model was told turns had run out.
            "forced": forced,
        }
        remaining = max_turns - turn_index

        if turn.get("action") == "conclude" and isinstance(turn.get("conclusion"), dict):
            gate_failure = _evidence_gate(turn, last_experiment)
            record["predicted_fix"] = turn.get("predicted_fix")
            record["conclusion_odc_type"] = turn["conclusion"].get("odc_type")
            record["gate_failure"] = gate_failure
            if gate_failure is None or forced or remaining == 0:
                record["duration_seconds"] = round(time.monotonic() - turn_started, 3)
                transcript.append(record)
                result = validate_conclusion(turn["conclusion"])
                result.turns = transcript
                result.termination_reason = (
                    "concluded" if gate_failure is None and not forced else "forced_max_turns"
                )
                result.loop_duration_seconds = round(time.monotonic() - loop_started, 3)
                result.probe_misses = probe_misses
                result.gate_rejections = gate_rejections
                result.evidence_gate_passed = gate_failure is None
                result.predicted_fix = turn.get("predicted_fix")
                if forced or gate_failure is not None:
                    result.needs_human_review = True
                return result

            # Rejected: the model is not allowed to decide it has enough evidence.
            gate_rejections += 1
            record["action"] = "conclude_rejected"
            record["duration_seconds"] = round(time.monotonic() - turn_started, 3)
            transcript.append(record)
            message = f"Conclusion REJECTED by the evidence gate: {gate_failure}."
            if remaining == 1:
                forced = True
                message += "\n\n" + _force_conclude_message()
            messages.append({"role": "user", "content": message})
            continue

        # request_evidence (or malformed) → execute probe, append observation
        probe = turn.get("probe") if isinstance(turn.get("probe"), dict) else {}
        probe_name = str(probe.get("name", "list_evidence"))
        probe_argument = probe.get("argument")
        probe_key = (probe_name, str(probe_argument or "").strip())
        if probe_key in served_at:
            observation: dict[str, Any] = {
                "error": (
                    f"probe already served this exact request at turn {served_at[probe_key]} — "
                    "the result is unchanged and is earlier in this conversation. If it did not "
                    "show what you needed, request DIFFERENT evidence (e.g. `source` with "
                    "'Class#method' for production code)."
                )
            }
        else:
            served_at[probe_key] = turn_index
            observation = execute_probe(context, probe_name, probe_argument, source_dirs)

        record["probe"] = {"name": probe_name, "argument": probe_argument}
        record["observation_summary"] = (
            sorted(observation.keys()) if "error" not in observation else observation["error"]
        )
        if "error" in observation:
            probe_misses += 1
        else:
            last_experiment = {
                "observation": observation,
                "leading_type": turn.get("leading_type"),
                "rival_type": turn.get("rival_type"),
            }
        record.update(_render_observation(observation))
        record["duration_seconds"] = round(time.monotonic() - turn_started, 3)
        transcript.append(record)

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
