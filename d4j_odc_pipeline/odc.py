from __future__ import annotations

ODC_TYPES: dict[str, dict[str, str]] = {
    "Algorithm/Method": {
        "summary": (
            "Efficiency or correctness problems that affect the task and can be fixed by "
            "(re)implementing an algorithm or local data structure without requesting a formal "
            "design change."
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
            "The low-level design required delaying transmission of some messages, but implementation "
            "transmitted all messages immediately. The delay algorithm was missing. "
            "A chain search algorithm was corrected from circular-linked list traversal to linear-linked list traversal. "
            "A method operation had incorrect parameter specification and required method-level correction."
        ),
        "family": "Control and Data Flow",
    },
    "Assignment/Initialization": {
        "summary": (
            "Value(s) assigned incorrectly or not assigned at all, including incorrect initialization "
            "of variables or object state."
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
            "An internal variable or control-block field had an incorrect value or no value. "
            "Parameter initialization was incorrect and required correction. "
            "An instance variable capturing object state was omitted or initialized incorrectly."
        ),
        "family": "Control and Data Flow",
    },
    "Checking": {
        "summary": (
            "Errors caused by missing or incorrect validation of parameters or data in conditional "
            "statements. If the missing or incorrect check is the critical error, the type stays "
            "Checking even when the fix must also add consequence code such as a loop, branch, or "
            "early return."
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
            "A value greater than 100 was invalid, but the check ensuring value < 100 was missing. "
            "A loop should have stopped at iteration 9 but continued because of an incorrect condition."
        ),
        "family": "Control and Data Flow",
    },
    "Timing/Serialization": {
        "summary": (
            "Necessary serialization of a shared resource was missing, the wrong resource was "
            "serialized, or the wrong serialization technique was employed."
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
            "Serialization was missing while updating a shared control block. "
            "A hierarchical locking scheme existed, but locks were acquired in the wrong sequence."
        ),
        "family": "Control and Data Flow",
    },
    "Function/Class/Object": {
        "summary": (
            "The error requires a formal design-level correction because it affects significant "
            "capability, end-user interfaces, product interfaces, hardware interface, or global "
            "data structures."
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
            "A database design omitted a required street-address field specified in requirements. "
            "A postal code field existed but was too small for international codes. "
            "A required class in the system design was omitted."
        ),
        "family": "Structural",
    },
    "Interface/O-O Messages": {
        "summary": (
            "Communication problems between modules, components, device drivers, objects, or "
            "functions via call signatures, parameter lists, control blocks, or messages."
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
            "A deletion interface existed but was not made callable from the external boundary. "
            "An interface specified pointer-to-number while implementation expected pointer-to-character. "
            "An OO message used the wrong service name or non-conforming parameter signature."
        ),
        "family": "Structural",
    },
    "Relationship": {
        "summary": (
            "Problems related to associations among procedures, data structures, and objects. "
            "These associations can be conditional and cross-cutting."
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
            "Code/data in one location assumed a specific structure in another location; "
            "without honoring that association, execution failed or produced incorrect behavior. "
            "A fix corrected the association constraints among related procedures, structures, or objects."
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

# ── ODC Impact (opener attribute, v5.2 §3.3) ─────────────────────────────
# The 13 official impact categories with definitions faithful to
# docs/odc_doc.md §3.3. Impact is judged from the customer/end-user
# perspective at the time the defect is OPENED — it is fix-independent by
# definition, which is what makes it usable as a negative control in the
# prefix/postfix drift analysis (see docs/odc_alignment_audit.md §6.3).
# "Unknown" is permitted at open time per v5.2 §5.1.

ODC_IMPACTS: dict[str, str] = {
    "Installability": (
        "The ability of the customer to prepare and place the software in position "
        "for use (does not include Usability)."
    ),
    "Integrity/Security": (
        "The protection of systems, programs, and data from inadvertent or malicious "
        "destruction, alteration, or disclosure."
    ),
    "Performance": (
        "The speed of the software as perceived by the customer and the customer's "
        "end users, in terms of their ability to perform their tasks."
    ),
    "Maintenance": (
        "The ease of applying preventive or corrective fixes to the software "
        "(e.g. fixes cannot be applied, or applying them takes excessive manual effort)."
    ),
    "Serviceability": (
        "The ability to diagnose failures easily and quickly, with minimal impact "
        "to the customer (e.g. misleading or unlocatable error diagnostics)."
    ),
    "Migration": (
        "The ease of upgrading to a current release, particularly the impact on "
        "existing customer data and operations (including changed external interfaces "
        "that break existing applications)."
    ),
    "Documentation": (
        "The degree to which the publication aids provided for understanding the "
        "structure and intended uses of the software are correct and complete."
    ),
    "Usability": (
        "The degree to which the software and publication aids enable the product to "
        "be easily understood and conveniently employed by its end user."
    ),
    "Standards": (
        "The degree to which the software complies with established pertinent standards."
    ),
    "Reliability": (
        "The ability of the software to consistently perform its intended function "
        "without unplanned interruption. Severe interruptions (crash, hang, abend) "
        "are always Reliability."
    ),
    "Requirements": (
        "A customer expectation, with regard to capability, which was not known, "
        "understood, or prioritized as a requirement for the current product or release."
    ),
    "Accessibility": (
        "Ensuring that successful access to information and use of information "
        "technology is provided to people who have disabilities."
    ),
    "Capability": (
        "The ability of the software to perform its intended functions and satisfy "
        "KNOWN requirements, where the customer is not impacted in any of the other "
        "categories. The explicit fallback when no other impact applies."
    ),
}

IMPACT_UNKNOWN = "Unknown"
ODC_IMPACT_NAMES = list(ODC_IMPACTS)


def allowed_impact_names() -> list[str]:
    """Canonical impact label set: the 13 v5.2 categories plus 'Unknown' (§5.1)."""
    return ODC_IMPACT_NAMES + [IMPACT_UNKNOWN]


def impact_markdown() -> str:
    """Prompt section teaching the v5.2 Impact attribute (opener side).

    Included in the few and scientific prompts only — never in zero-free,
    which must stay free of ODC concepts."""
    lines = [
        "## ODC Impact (opener attribute — judged from behaviour, not the fix)",
        "",
        "Separately from the defect type, select exactly ONE Impact: the effect the",
        "failure has (or would have) on the customer/end user. Judge it from the bug",
        "report and the observable failure behaviour. Impact is recorded when a defect",
        "is OPENED — the nature of the eventual fix does not define it.",
        "",
    ]
    for name, definition in ODC_IMPACTS.items():
        lines.append(f"- **{name}**: {definition}")
    lines.extend(
        [
            f"- **{IMPACT_UNKNOWN}**: only when the evidence does not support any judgment "
            "of the user-visible effect.",
            "",
            "Guidance:",
            "- Severe unplanned interruption reaching the user (crash, hang, unhandled "
            "exception) → Reliability.",
            "- Wrong results / a function not doing its job, with no other category "
            "applying → Capability (the explicit fallback).",
            "- Do not derive impact from the code mechanism; derive it from the failure "
            "as the user would experience it.",
        ]
    )
    return "\n".join(lines)


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
    lines = [
        "## ODC Defect Type Taxonomy",
        "",
        f"You MUST classify the bug into exactly ONE of these {type_count}.",
        "Read the definitions carefully — each type has specific indicators and boundaries.",
        "",
    ]
    for name, meta in ODC_TYPES.items():
        lines.append(f"### {name} (Family: {meta['family']})")
        lines.append(f"**Definition**: {meta['summary']}")
        lines.append(f"**When to choose this type**: {meta['indicators']}")
        lines.append(f"**When NOT to choose this type**: {meta['distinguish_from']}")
        lines.append(f"**Examples**: {meta['examples']}")
        lines.append("")
    if open_mode:
        lines.extend(
            [
                f"### {OTHER_TYPE_NAME} (escape category — LAST RESORT ONLY)",
                "**Definition**: The defect's root-cause mechanism genuinely does not fit ANY of the "
                "7 ODC types above, even approximately.",
                "**When to choose this type**: ONLY after you have explicitly worked through all 7 "
                "diagnostic questions and can state, for EACH of the 7 types, a concrete evidence-based "
                "reason why it does not apply. Choosing Other is a strong claim that the taxonomy has a gap.",
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
