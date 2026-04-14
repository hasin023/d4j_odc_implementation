from __future__ import annotations

ODC_TYPES: dict[str, dict[str, str]] = {
    "Function": {
        "summary": (
            "The defect requires adding entirely new capability, a new method, a new parameter, "
            "or a significant change to high-level feature design that was never implemented. "
            "This is NOT about incorrect logic — it is about MISSING functionality that was "
            "never coded at all."
        ),
        "indicators": (
            "A required feature, method, or behavior is completely absent. The fix would "
            "involve adding substantial new code (new methods, new classes, new parameters) "
            "rather than correcting existing code."
        ),
        "distinguish_from": (
            "If existing code produces a WRONG result, that is Algorithm, Checking, or Assignment — "
            "not Function. Function means the capability was never implemented. "
            "If a condition/guard is missing, that is Checking. If a computation is wrong, that is Algorithm."
        ),
        "examples": (
            "A method that should handle a specific input type but has no handler for it at all. "
            "A feature that was specified but the implementation was never written. "
            "A CLI option that was documented but never wired up."
        ),
        "coarse_group": "Structural",
    },
    "Interface": {
        "summary": (
            "The defect is in the interaction between components, modules, or APIs. "
            "Wrong method signature, incorrect parameter passing, wrong return type handling, "
            "protocol or contract mismatch at a component boundary."
        ),
        "indicators": (
            "The bug occurs at the boundary between two modules, classes, or subsystems. "
            "The caller and callee disagree on types, parameter order, return semantics, "
            "or protocol. Serialization/deserialization format mismatches also qualify."
        ),
        "distinguish_from": (
            "If the logic within a single method is wrong, that is Algorithm or Checking. "
            "Interface is specifically about CROSS-COMPONENT mismatches: wrong parameter order, "
            "type confusion between caller/callee, or API contract violations."
        ),
        "examples": (
            "Passing arguments in the wrong order to another module's API. "
            "Misinterpreting the return value of a library method. "
            "Serialization format mismatch between writer and reader components."
        ),
        "coarse_group": "Structural",
    },
    "Checking": {
        "summary": (
            "The defect is a missing or incorrect validation, condition, guard, boundary check, "
            "or exception handling. The core logic may be correct, but a protective check is "
            "absent or wrong."
        ),
        "indicators": (
            "The fix involves adding, removing, or correcting an if/else condition, a null check, "
            "a bounds check, a loop guard, an instanceof test, a try/catch block, or an assertion. "
            "The underlying algorithm or data flow is correct — it just lacks proper validation."
        ),
        "distinguish_from": (
            "If the computation itself is wrong (wrong formula, wrong iteration order), that is Algorithm. "
            "If a variable holds the wrong value, that is Assignment. Checking is specifically about "
            "CONDITIONAL LOGIC that guards against invalid states, inputs, or edge cases."
        ),
        "examples": (
            "Missing null check before dereferencing an object. "
            "Wrong boundary condition in an if-statement (off-by-one in a comparison). "
            "Missing validation of user input or method parameters. "
            "Incorrect exception type in a catch block. "
            "A flag or boolean condition that evaluates incorrectly."
        ),
        "coarse_group": "Control and Data",
    },
    "Assignment": {
        "summary": (
            "The defect is a wrong value assignment, incorrect initialization, wrong constant, "
            "or incorrect variable/field update. The control flow and algorithm are correct, "
            "but a specific data value is wrong."
        ),
        "indicators": (
            "The fix is localized: changing a single value, constant, initialization expression, or "
            "field assignment. The surrounding logic and control flow remain untouched. "
            "Typically a one-line or two-line fix that changes WHAT value is stored."
        ),
        "distinguish_from": (
            "If the fix requires changing a condition or adding a guard, that is Checking. "
            "If the fix requires changing algorithmic logic (loops, recursion, data structure operations), "
            "that is Algorithm. Assignment is specifically about a WRONG DATA VALUE in otherwise correct code."
        ),
        "examples": (
            "A constant set to 0 instead of 1. "
            "A variable initialized with the wrong default. "
            "A field set to 'false' when it should be 'true'. "
            "Using the wrong variable name in a simple assignment (e.g., x = a instead of x = b). "
            "Returning the wrong variable from a method."
        ),
        "coarse_group": "Control and Data",
    },
    "Timing/Serialization": {
        "summary": (
            "The defect depends on execution order, timing, concurrency, lifecycle sequencing, "
            "or serialization/deserialization behavior."
        ),
        "indicators": (
            "The fix involves reordering operations, adding synchronization, fixing race conditions, "
            "correcting lifecycle callbacks, or fixing serialization order/format. The code may work "
            "correctly in isolation but fails under specific timing or ordering conditions."
        ),
        "distinguish_from": (
            "If the order doesn't matter and the value is simply wrong, that is Assignment. "
            "If a guard against concurrent access is missing, that overlaps with Checking but "
            "belongs here if the root cause is fundamentally about ORDERING or TIMING."
        ),
        "examples": (
            "A race condition between two threads. "
            "Operations executed in the wrong lifecycle order (init before config). "
            "State corrupted because serialization and deserialization use different field ordering."
        ),
        "coarse_group": "Control and Data",
    },
    "Build/Package/Merge": {
        "summary": (
            "The defect is caused by build configuration, packaging, dependency wiring, "
            "or source-integration/merge issues."
        ),
        "indicators": (
            "The fix involves build scripts, dependency declarations, packaging metadata, "
            "classpath configuration, or resolving merge conflicts. The source logic itself may be correct "
            "but the built artifact is wrong."
        ),
        "distinguish_from": (
            "If the source code logic is wrong, use one of the other types. "
            "Build/Package/Merge is reserved for problems in the build/deploy pipeline, "
            "not in application logic."
        ),
        "examples": (
            "Missing dependency in pom.xml or build.gradle. "
            "Wrong classpath causing ClassNotFoundException at runtime. "
            "A merge conflict that introduced duplicate or contradictory code."
        ),
        "coarse_group": "Structural",
    },
    "Algorithm": {
        "summary": (
            "The defect is in the core computational logic, procedure, or data-structure manipulation. "
            "The code exists and executes, but it computes the wrong result because the algorithm "
            "or procedure is incorrect."
        ),
        "indicators": (
            "The fix changes HOW a computation works: correcting a formula, fixing loop logic, "
            "changing iteration order, fixing a sort comparator, correcting a data structure operation, "
            "or restructuring a multi-step procedure. More complex than a simple assignment fix "
            "but contained within a single component (not cross-component like Interface)."
        ),
        "distinguish_from": (
            "If the fix is just changing a single value/constant, that is Assignment. "
            "If the fix is adding a guard/condition, that is Checking. "
            "Algorithm is specifically about wrong PROCEDURAL LOGIC — the steps of the computation "
            "are incorrect, not just a missing guard or wrong value."
        ),
        "examples": (
            "Wrong mathematical formula in a calculation method. "
            "Incorrect loop iteration logic (e.g., iterating forward instead of backward). "
            "Wrong comparator in a sort or wrong key in a hash lookup. "
            "Off-by-one in array indexing within a data processing loop. "
            "Using add() where multiply() is needed in a numerical method."
        ),
        "coarse_group": "Control and Data",
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
        lines.append(f"### {name} (Coarse group: {meta['coarse_group']})")
        lines.append(f"**Definition**: {meta['summary']}")
        lines.append(f"**When to choose this type**: {meta['indicators']}")
        lines.append(f"**When NOT to choose this type**: {meta['distinguish_from']}")
        lines.append(f"**Examples**: {meta['examples']}")
        lines.append("")
    return "\n".join(lines)


def coarse_group_for(odc_type: str) -> str | None:
    meta = ODC_TYPES.get(odc_type)
    return meta["coarse_group"] if meta else None
