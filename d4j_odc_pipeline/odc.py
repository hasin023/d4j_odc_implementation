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
            "If the correction requires algorithmic/procedural rewrite, use Algorithm/Method."
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
            "statements."
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


def taxonomy_markdown() -> str:
    lines = [
        "## ODC Defect Type Taxonomy",
        "",
        "You MUST classify the bug into exactly ONE of these 7 types.",
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
    return "\n".join(lines)


def family_for(odc_type: str) -> str | None:
    meta = ODC_TYPES.get(odc_type)
    return meta["family"] if meta else None


def coarse_group_for(odc_type: str) -> str | None:
    """Backward-compatible alias for older callers and artifacts."""
    return family_for(odc_type)
