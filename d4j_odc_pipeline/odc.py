from __future__ import annotations

import re

ODC_TYPES: dict[str, dict[str, str]] = {
    "Algorithm/Method": {
        "summary": (
            'Efficiency or correctness problems that affect the task and can be fixed by '
            '(re)implementing an algorithm or local data structure without the need for requesting a '
            'design change. Problem in the procedure, template, or overloaded function that describes a '
            'service offered by an object.'
        ),
        "indicators": (
            "The defect is in the procedure itself: wrong iteration strategy, wrong search logic, "
            "incorrect algorithmic step ordering, or an incorrect method-level computational strategy."
        ),
        "distinguish_from": (
            "If the fix is primarily a missing/incorrect guard, use Checking. "
            "If the fix is mainly a wrong value or initialization, use Assignment/Initialization. "
            "If a formal design capability is missing, use Function/Class/Object."
        ),
        "examples": (
            '(1) The low-level design called for the use of an algorithm that improves throughput over '
            'the link by delaying transmission of some messages, but the implementation transmitted all '
            'messages as soon as they arrived. The algorithm that delayed transmission was missing. (2) '
            'The algorithm for searching a chain of control blocks was corrected to use a linear-linked '
            'list instead of a circular-linked list. (3) The number and/or types of parameters of a '
            'method or an operation are incorrectly specified. (4) A method or an operation is not made '
            'public in the specification of a class.'
        ),
        "family": "Control and Data Flow",
    },
    "Assignment/Initialization": {
        "summary": (
            'Value(s) assigned incorrectly or not assigned at all; but note that a fix involving '
            'multiple assignment corrections may be of type Algorithm.'
        ),
        "indicators": (
            "The correction is about setting or initializing a value correctly rather than "
            "reworking overall procedural logic."
        ),
        "distinguish_from": (
            "If the fix requires changes to control predicates or guards, use Checking. "
            "If the correction requires algorithmic/procedural rewrite, use Algorithm/Method. "
            "A fix involving multiple coordinated assignment corrections may be of type "
            "Algorithm/Method."
        ),
        "examples": (
            '(1) Internal variable or variable within a control block did not have correct value, or '
            "did not have any value at all. (2) Initialization of parameters (3) Resetting a variable's "
            'value. (4) The instance variable capturing a characteristic of an object (e.g., the color '
            'of a car) is omitted. (5) The instance variables that capture the state of an object are '
            'not correctly initialized.'
        ),
        "family": "Control and Data Flow",
    },
    "Checking": {
        "summary": (
            'Errors caused by missing or incorrect validation of parameters or data in conditional '
            'statements. It might be expected that a consequence of checking for a value would require '
            'additional code such as a do while loop or branch. If the missing or incorrect check is '
            'the critical error, checking would still be the type chosen.'
        ),
        "indicators": (
            "The main issue is in predicate logic, boundary checks, loop stop conditions, or "
            "parameter/data validation."
        ),
        "distinguish_from": (
            "If values are simply wrong but condition logic is correct, use Assignment/Initialization. "
            "If the procedure itself is wrong, use Algorithm/Method."
        ),
        "examples": (
            '(1) Value greater than 100 is not valid, but the check to make sure that the value was '
            'less than 100 was missing. (2) The conditional loop should have stopped on the ninth '
            'iteration. But it kept looping while the counter was <= 10.'
        ),
        "family": "Control and Data Flow",
    },
    "Timing/Serialization": {
        "summary": (
            'Necessary serialization of shared resource was missing, the wrong resource was serialized, '
            'or the wrong serialization technique was employed.'
        ),
        "indicators": (
            "The bug depends on operation order, lock/serialization strategy, or concurrency-aware "
            "coordination of shared resources."
        ),
        "distinguish_from": (
            "If the issue is primarily value assignment, use Assignment/Initialization. "
            "If the issue is guard validation rather than ordering/serialization, use Checking."
        ),
        "examples": (
            '(1) Serialization is missing when making updates to a shared control block. (2) A '
            'hierarchical locking scheme is in use, but the defective code failed to acquire the locks '
            'in the prescribed sequence.'
        ),
        "family": "Control and Data Flow",
    },
    "Function/Class/Object": {
        "summary": (
            'The error should require a formal design change, as it affects significant capability, '
            'end-user interfaces, product interfaces, interface with hardware architecture, or global '
            'data structure(s); The error occurred when implementing the state and capabilities of a '
            'real or an abstract entity.'
        ),
        "indicators": (
            "A major function/class/object capability is absent or incorrectly designed in a way "
            "that goes beyond local procedural correction."
        ),
        "distinguish_from": (
            "If the defect is local algorithmic logic, use Algorithm/Method. "
            "If it is an API contract mismatch between components, use Interface/O-O Messages."
        ),
        "examples": (
            '(1) A database did not include a field for street address, although the requirements '
            'specified it. (2) A database included a field for postal zip code, but it was too small to '
            'contain international postal codes as specified in the requirements. (3) A C++ or '
            'SmallTalk class was omitted during system design.'
        ),
        "family": "Structural",
    },
    "Interface/O-O Messages": {
        "summary": (
            'Communication problems between: modules, components, device drivers, objects, functions '
            'via: macros, call statements, control blocks, parameter lists.'
        ),
        "indicators": (
            "The defect is at a boundary where one party expects a different contract, type, "
            "service name, or parameter signature than the other."
        ),
        "distinguish_from": (
            "If the main issue is internal computation within one component, use Algorithm/Method. "
            "If it is a design-level capability omission, use Function/Class/Object."
        ),
        "examples": (
            '(1) A database implements both insertion and deletion functions, but the deletion '
            'interface was not made callable. (2) The interface specifies a pointer to a number, but '
            'the implementation is expecting a pointer to a character. (3) The OO-message incorrectly '
            'specifies the name of a service. (4) The number and/or types of parameters of the '
            'OO-message do not conform with the signature of the requested service.'
        ),
        "family": "Structural",
    },
    "Relationship": {
        "summary": (
            'Problems related to associations among procedures, data structures and objects. Such '
            'associations may be conditional.'
        ),
        "indicators": (
            "Correctness depends on consistency between related structures or procedures in different "
            "parts of the codebase."
        ),
        "distinguish_from": (
            "If the issue is clearly a boundary message/signature mismatch, use Interface/O-O Messages. "
            "If the issue is local procedural logic with no cross-entity relationship issue, use Algorithm/Method."
        ),
        "examples": (
            '(1) The structure of code/data in one place assumes a certain structure of code/data in '
            'another. Without appropriate consideration of their relationship, program will not execute '
            'or it executes incorrectly. (2) The inheritance relationship between two classes is '
            'missing or incorrectly specified. (3) The limit on the number of objects that may be '
            'instantiated from a given class is incorrect and causes performance degradation of the '
            'system.'
        ),
        "family": "Structural",
    },
}

ODC_TYPE_NAMES = list(ODC_TYPES)

# ── RQ2 open-taxonomy support ────────────────────────────────────────────
# "Other" is a measurement instrument for the RQ2 coverage study, NOT a
# permanent 8th ODC category. It exists so the coverage of the official 7
# types can be measured empirically (escape rate) instead of assumed.
# It is only offered to the LLM when taxonomy_mode == "open".

OTHER_TYPE_NAME = "Other"


# ── Experimental condition variables ─────────────────────────────────────
# Every classification is a coordinate (taxonomy, strategy). The authoritative
# description of this model (levels, valid combinations, rationale, defaults)
# is docs/condition_model.md — read that before changing anything here.
#
#   taxonomy — what label space the LLM may answer in:
#       free   = no taxonomy; answer in own words
#       closed = the 7 ODC types, forced choice          (closed-set)
#       open   = 7 + "Other" escape category             (open-set; DEFAULT)
#   strategy — the prompting strategy:
#       zero       = zero-shot: no taxonomy, no worked examples
#                    (implies taxonomy=free; the unstructured baseline)
#       few        = few-shot single call: taxonomy + diagnostic tree +
#                    worked classification examples (the strong static prompt)
#       scientific = the enforced scientific loop (agent.py):
#                    hypothesis→prediction→probe→observation turns (DEFAULT)
#
# Valid conditions (5): free-zero, closed-few, open-few,
#                       closed-scientific, open-scientific.
TAXONOMY_FREE = "free"
TAXONOMY_CLOSED = "closed"
TAXONOMY_OPEN = "open"
TAXONOMY_MODES = (TAXONOMY_FREE, TAXONOMY_CLOSED, TAXONOMY_OPEN)
DEFAULT_TAXONOMY = TAXONOMY_OPEN

STRATEGY_ZERO = "zero"
STRATEGY_FEW = "few"
STRATEGY_SCIENTIFIC = "scientific"
STRATEGY_LEVELS = (STRATEGY_ZERO, STRATEGY_FEW, STRATEGY_SCIENTIFIC)
DEFAULT_STRATEGY = STRATEGY_SCIENTIFIC


def validate_condition(taxonomy: str, strategy: str) -> None:
    """Reject invalid (taxonomy, strategy) combinations.

    - zero is BY DEFINITION taxonomy-free (no label space in the prompt);
      pairing it with closed/open is contradictory.
    - few/scientific require a taxonomy to classify into; free would leave
      them without a label space.
    """
    if taxonomy not in TAXONOMY_MODES:
        raise ValueError(f"Unknown taxonomy: {taxonomy!r} (expected one of {TAXONOMY_MODES})")
    if strategy not in STRATEGY_LEVELS:
        raise ValueError(f"Unknown strategy: {strategy!r} (expected one of {STRATEGY_LEVELS})")
    if strategy == STRATEGY_ZERO and taxonomy != TAXONOMY_FREE:
        raise ValueError(
            "strategy 'zero' is taxonomy-free by definition — use --taxonomy free "
            "(or omit --taxonomy only if you set --strategy few|scientific)."
        )
    if strategy != STRATEGY_ZERO and taxonomy == TAXONOMY_FREE:
        raise ValueError(
            f"strategy {strategy!r} requires a taxonomy (closed|open); "
            "taxonomy 'free' is only valid with --strategy zero."
        )


def condition_tag(taxonomy: str, strategy: str) -> str:
    """Filename tag for a condition, e.g. 'scientific-open'.

    Strategy comes first: it's the primary study axis (zero/few/scientific
    ladder); taxonomy (closed/open) is the secondary RQ2 escape-rate side-study.
    Used as classification.<tag>.json / report.<tag>.md / checkpoint suffixes.
    Always explicit — there is no untagged default filename."""
    return f"{strategy}-{taxonomy}"


_SLUG_UNSAFE_RE = re.compile(r"[^A-Za-z0-9._-]+")


def model_slug(provider: str, model: str) -> str:
    """Filesystem-safe identifier for a (provider, model) pair, e.g.
    ("groq", "openai/gpt-oss-120b") -> "groq-openai-gpt-oss-120b". Keyed on
    both provider and model, not model alone, so two providers serving an
    identically-named model can't collide on the same slug."""
    raw = f"{provider}-{model}"
    return _SLUG_UNSAFE_RE.sub("-", raw).strip("-")


def resolve_effective_tag(
    tag: str, provider: str, model: str, existing_checkpoint: dict | None
) -> str:
    """Decide whether a (provider, model) run needs a model-suffixed tag.

    ``existing_checkpoint`` is the parsed JSON of the BARE tag's
    checkpoint.pairs.<tag>.json (or None if it doesn't exist yet) — the
    caller reads that file once and passes it in; this function is pure.

    Rules, in order:
      1. No existing checkpoint → first model for this (root, condition) →
         bare tag, unchanged filenames forever.
      2. Existing checkpoint has no "model"/"provider" keys (every
         checkpoint written before this mechanism existed, including the
         committed 854-bug corpus) → treated as compatible → bare tag.
         This is what guarantees old artifacts are never renamed.
      3. Existing checkpoint's (provider, model) matches the caller's →
         same-model resume → bare tag (today's behavior, unchanged).
      4. Existing checkpoint's (provider, model) differs → suffixed:
         f"{tag}.{model_slug(provider, model)}".

    See docs/condition_model.md and docs/suspicious_frame_selection.md for
    the backward-compatibility rationale."""
    if existing_checkpoint is None:
        return tag
    prior_provider = existing_checkpoint.get("provider")
    prior_model = existing_checkpoint.get("model")
    if prior_provider is None and prior_model is None:
        return tag
    if prior_provider == provider and prior_model == model:
        return tag
    return f"{tag}.{model_slug(provider, model)}"


def resolve_effective_tag_from_root(artifacts_root, tag: str, provider: str | None, model: str | None) -> str:
    """Convenience wrapper around resolve_effective_tag for read-side callers
    (analyze_batch_artifacts, compute_coverage_metrics, study-escape's
    pre-flight glob check): reads the bare tag's checkpoint under
    artifacts_root (if any) and resolves it. Returns the bare tag unchanged
    when provider or model is falsy (single-model / not specified)."""
    if not provider or not model:
        return tag
    import json
    from pathlib import Path

    bare_checkpoint_path = Path(artifacts_root) / f"checkpoint.pairs.{tag}.json"
    existing: dict | None = None
    if bare_checkpoint_path.exists():
        try:
            existing = json.loads(bare_checkpoint_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            existing = None
    return resolve_effective_tag(tag, provider, model, existing)


def legacy_prompt_style(taxonomy: str, strategy: str) -> str:
    """Retired preset name kept in artifacts for old readers."""
    if taxonomy == TAXONOMY_FREE:
        return "naive"
    return "scientific"


def allowed_type_names(taxonomy_mode: str = TAXONOMY_CLOSED) -> list[str]:
    """Canonical label set for a taxonomy mode: the 7 ODC types, plus
    'Other' in open mode."""
    if taxonomy_mode == TAXONOMY_OPEN:
        return ODC_TYPE_NAMES + [OTHER_TYPE_NAME]
    return list(ODC_TYPE_NAMES)


def taxonomy_markdown(taxonomy_mode: str = TAXONOMY_CLOSED) -> str:
    open_mode = taxonomy_mode == TAXONOMY_OPEN
    type_count = "8 types (7 ODC types + Other)" if open_mode else "7 types"
    # Each type shows IBM ODC v5.2's Definition and Examples only. Our own
    # `indicators` / `distinguish_from` guidance (written April 2026, no recorded
    # source) is no longer rendered: it paraphrased IBM with drift and conflicted
    # with the approved worked examples — docs/prompt_review_v3.md, block 4b.
    lines = [
        "## ODC Defect Type Taxonomy",
        "",
        "<odc_taxonomy>",
        f"You MUST classify the bug into exactly ONE of these {type_count}.",
        "Read the definitions carefully.",
        "",
    ]
    for name, meta in ODC_TYPES.items():
        lines.append(f"### {name} (Family: {meta['family']})")
        lines.append(f"**Definition**: {meta['summary']}")
        lines.append(f"**Examples**: {meta['examples']}")
        lines.append("")
    if open_mode:
        lines.extend(
            [
                f"### {OTHER_TYPE_NAME} (escape category — LAST RESORT ONLY)",
                "**Definition**: The defect's root-cause mechanism genuinely does not fit ANY of the "
                "7 ODC types above, even approximately.",
                "**When to choose this type**: ONLY after you can state, for EACH of the 7 types, a "
                "concrete evidence-based reason why it does not apply. Choosing Other is a strong claim "
                "that the taxonomy has a gap.",
                "**When NOT to choose this type**: Do NOT use Other because evidence is incomplete, "
                "because you are uncertain between two types (pick the better one and lower confidence), "
                "or because the bug is complex or spans multiple types (pick the dominant mechanism). "
                "Uncertainty is NOT a reason to escape the taxonomy.",
                "**If you choose Other you MUST also provide**: `other_justification` (why every one of "
                "the 7 types fails, citing evidence), `nearest_type` (which of the 7 comes closest), and "
                "`other_confidence` (0-1: how confident you are that this is a true taxonomy gap).",
                "",
            ]
        )
    lines.append("</odc_taxonomy>")
    return "\n".join(lines)


def family_for(odc_type: str) -> str | None:
    # The two-family grouping (Control and Data Flow / Structural) is NOT part
    # of IBM's v5.2 document — it is this project's coarse grouping for the
    # Tier-3 family-match agreement level. Present it as such in any write-up.
    meta = ODC_TYPES.get(odc_type)
    return meta["family"] if meta else None


def coarse_group_for(odc_type: str) -> str | None:
    """Backward-compatible alias for older callers and artifacts."""
    return family_for(odc_type)
