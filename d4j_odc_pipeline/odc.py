from __future__ import annotations

ODC_TYPES: dict[str, dict[str, str]] = {
    "Function": {
        "summary": "The defect is in high-level capability, missing logic, or wrong feature behavior.",
        "examples": "Missing method behavior, incomplete implementation, wrong overall function result.",
        "coarse_group": "Structural",
    },
    "Interface": {
        "summary": "The defect is in interaction across components, APIs, contracts, or data boundaries.",
        "examples": "Wrong method signature usage, incorrect object interaction, serialization or protocol mismatch at boundaries.",
        "coarse_group": "Structural",
    },
    "Checking": {
        "summary": "The defect comes from missing or incorrect validation, condition, guard, or exception checking.",
        "examples": "Bad null check, missing bounds check, wrong conditional branch, incorrect error handling gate.",
        "coarse_group": "Control and Data",
    },
    "Assignment": {
        "summary": "The defect comes from wrong value assignment, initialization, update, or state propagation.",
        "examples": "Wrong variable value, stale field update, incorrect constant, incorrect copied state.",
        "coarse_group": "Control and Data",
    },
    "Timing/Serialization": {
        "summary": "The defect depends on order, timing, concurrency, lifecycle, persistence, or serialization behavior.",
        "examples": "Race-sensitive ordering, wrong lifecycle sequence, bad serialization/deserialization state.",
        "coarse_group": "Control and Data",
    },
    "Build/Package/Merge": {
        "summary": "The defect is caused by packaging, configuration, dependency, or integration/merge issues.",
        "examples": "Wrong packaging metadata, missing dependency wiring, merge-induced integration breakage.",
        "coarse_group": "Structural",
    },
    "Algorithm": {
        "summary": "The defect lies in the core procedure or computation itself rather than a local check or assignment.",
        "examples": "Wrong iteration logic, incorrect math or data structure algorithm, flawed transformation procedure.",
        "coarse_group": "Control and Data",
    },
}

ODC_TYPE_NAMES = list(ODC_TYPES)


def taxonomy_markdown() -> str:
    lines = [
        "Use the following ODC defect types exactly as written.",
        "",
    ]
    for name, meta in ODC_TYPES.items():
        lines.append(f"- {name}: {meta['summary']} Examples: {meta['examples']}")
    return "\n".join(lines)


def coarse_group_for(odc_type: str) -> str | None:
    meta = ODC_TYPES.get(odc_type)
    return meta["coarse_group"] if meta else None
