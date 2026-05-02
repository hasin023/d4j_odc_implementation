"""Comparison logic for evaluating pre-fix vs post-fix ODC classifications.

Implements a multi-tier accuracy framework grounded in ODC literature:

  Tier 1 — Strict Match:       exact odc_type agreement
  Tier 2 — Top-2 Match:        primary or alternative_types overlap
  Tier 3 — Family Match:       same high-level category (Control and Data Flow / Structural)
  Tier 4 — Cohen's Kappa:      inter-rater agreement statistic (batch only)

Extended analysis layers (added for thesis defense):

  Layer A — Semantic Distance:  0.0–1.0 ODC type proximity score
  Layer B — Evidence Asymmetry: explains WHY pre-fix ≠ post-fix
  Layer C — Attribute Concordance: agreement on target/qualifier/age/source
  Layer D — Divergence Pattern: match / soft-divergence / hard-divergence
  Layer E — Insights:           actionable interpretive text for each bug

References:
  Chillarege et al. (1992) — ODC inter-rater disagreement is expected (~20-30%).
  Thung et al. (2012)     — Even with post-fix code, accuracy caps at ~77.8%.
  Kang et al. (2023)      — Evidence-dependent hypothesis generation is fundamental.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# ODC Semantic Distance Matrix
# ---------------------------------------------------------------------------
# Grounded in the ODC taxonomy structure.  Types within the same family are
# semantically closer.  Distance is 0.0 (identical), 0.2–0.4 (same-family
# neighbor), 0.6–0.8 (cross-family), 1.0 (maximum divergence).
#
# The matrix is symmetric.  Values are calibrated from ODC literature analysis
# of common mis-classifications (Thung 2012, Chillarege 1992).

_FAMILY_MAP: dict[str, str] = {
    "Algorithm/Method": "Control and Data Flow",
    "Assignment/Initialization": "Control and Data Flow",
    "Checking": "Control and Data Flow",
    "Timing/Serialization": "Control and Data Flow",
    "Function/Class/Object": "Structural",
    "Interface/O-O Messages": "Structural",
    "Relationship": "Structural",
}

_SEMANTIC_DISTANCE: dict[tuple[str, str], float] = {
    # Same type = 0.0 (auto-handled)
    # Control and Data Flow intra-family
    ("Algorithm/Method", "Checking"): 0.25,
    ("Algorithm/Method", "Assignment/Initialization"): 0.30,
    ("Checking", "Assignment/Initialization"): 0.30,
    ("Algorithm/Method", "Timing/Serialization"): 0.40,
    ("Checking", "Timing/Serialization"): 0.40,
    ("Assignment/Initialization", "Timing/Serialization"): 0.35,
    # Structural intra-family
    ("Function/Class/Object", "Interface/O-O Messages"): 0.30,
    ("Function/Class/Object", "Relationship"): 0.35,
    ("Interface/O-O Messages", "Relationship"): 0.30,
    # Cross-family
    ("Algorithm/Method", "Function/Class/Object"): 0.65,
    ("Algorithm/Method", "Interface/O-O Messages"): 0.70,
    ("Algorithm/Method", "Relationship"): 0.75,
    ("Checking", "Function/Class/Object"): 0.70,
    ("Checking", "Interface/O-O Messages"): 0.75,
    ("Checking", "Relationship"): 0.80,
    ("Assignment/Initialization", "Function/Class/Object"): 0.65,
    ("Assignment/Initialization", "Interface/O-O Messages"): 0.70,
    ("Assignment/Initialization", "Relationship"): 0.75,
    ("Timing/Serialization", "Function/Class/Object"): 0.70,
    ("Timing/Serialization", "Interface/O-O Messages"): 0.75,
    ("Timing/Serialization", "Relationship"): 0.80,
}


def semantic_distance(type_a: str, type_b: str) -> float:
    """Return the ODC semantic distance between two defect types (0.0–1.0)."""
    if type_a == type_b:
        return 0.0
    key = (type_a, type_b)
    if key in _SEMANTIC_DISTANCE:
        return _SEMANTIC_DISTANCE[key]
    # Try reverse
    rkey = (type_b, type_a)
    if rkey in _SEMANTIC_DISTANCE:
        return _SEMANTIC_DISTANCE[rkey]
    # Unknown types — maximum distance
    return 1.0


# ---------------------------------------------------------------------------
# Divergence pattern classification
# ---------------------------------------------------------------------------

def classify_divergence_pattern(
    strict_match: bool,
    top2_match: bool,
    family_match: bool,
    distance: float,
) -> str:
    """Classify the divergence into a named pattern.

    Returns one of:
      - "exact-match"        — identical types
      - "soft-divergence"    — same family or alternative overlap (distance < 0.5)
      - "moderate-divergence" — cross-family but with alternative support
      - "hard-divergence"    — no match at any tier
    """
    if strict_match:
        return "exact-match"
    if top2_match and family_match:
        return "soft-divergence"
    if top2_match or (family_match and distance < 0.5):
        return "soft-divergence"
    if family_match:
        return "moderate-divergence"
    return "hard-divergence"


# ---------------------------------------------------------------------------
# Evidence asymmetry analysis
# ---------------------------------------------------------------------------

_EVIDENCE_ASYMMETRY_RULES: list[dict[str, str]] = [
    {
        "condition": "pre-fix sees symptoms only; post-fix sees the actual code change",
        "explanation": (
            "Pre-fix classification is based on observable symptoms (stack traces, "
            "failing tests, error messages) which often surface the effect rather than "
            "the root cause.  Post-fix classification has access to the diff showing "
            "exactly what changed, revealing the true nature of the fix.  Different "
            "evidence bases legitimately produce different classifications."
        ),
        "literature": "Kang et al. (2023) — AutoSD: evidence-dependent hypothesis generation",
    },
    {
        "condition": "ODC boundary ambiguity between similar types",
        "explanation": (
            "The ODC taxonomy has known boundary ambiguity zones, especially between "
            "Algorithm/Method ↔ Checking, and Function/Class/Object ↔ Interface/O-O "
            "Messages.  Even expert human classifiers disagree on 20-30% of bugs "
            "(Chillarege 1992).  Cohen's Kappa of 0.6-0.8 is considered 'substantial' "
            "agreement in defect classification — not perfection."
        ),
        "literature": "Chillarege et al. (1992), Thung et al. (2012) — 77.8% ceiling",
    },
    {
        "condition": "multi-fault versions contain overlapping defects",
        "explanation": (
            "Defects4J versions typically contain ~9.2 co-existing faults (Callaghan "
            "2024).  When the LLM sees only symptoms, it may describe a different "
            "facet of the bug cluster than when it sees the specific fix diff for "
            "one fault.  Both classifications can be valid perspectives on a "
            "multi-faceted defect landscape."
        ),
        "literature": "Callaghan (2024) — Mining Bug Repositories for Multi-Fault Programs",
    },
]


def analyze_evidence_asymmetry(
    prefix_data: dict[str, Any],
    postfix_data: dict[str, Any],
    divergence_pattern: str,
) -> dict[str, Any]:
    """Analyze why pre-fix and post-fix classifications might legitimately differ.

    Returns a structured explanation with applicable rules and an overall
    assessment.
    """
    applicable_rules: list[dict[str, str]] = []

    # Rule 1 always applies when evidence modes differ
    prefix_mode = prefix_data.get("evidence_mode", "pre-fix")
    postfix_mode = postfix_data.get("evidence_mode", "post-fix")
    if prefix_mode != postfix_mode:
        applicable_rules.append(_EVIDENCE_ASYMMETRY_RULES[0])

    # Rule 2 applies when types are in known ambiguity zones
    prefix_type = prefix_data.get("odc_type", "")
    postfix_type = postfix_data.get("odc_type", "")
    ambiguous_pairs = {
        frozenset({"Algorithm/Method", "Checking"}),
        frozenset({"Function/Class/Object", "Interface/O-O Messages"}),
        frozenset({"Algorithm/Method", "Assignment/Initialization"}),
        frozenset({"Interface/O-O Messages", "Relationship"}),
        frozenset({"Function/Class/Object", "Relationship"}),
    }
    if frozenset({prefix_type, postfix_type}) in ambiguous_pairs:
        applicable_rules.append(_EVIDENCE_ASYMMETRY_RULES[1])

    # Rule 3 applies for projects known to have multi-fault data
    from .multifault import SUPPORTED_PROJECTS
    project = prefix_data.get("project_id", "")
    if project in SUPPORTED_PROJECTS:
        applicable_rules.append(_EVIDENCE_ASYMMETRY_RULES[2])

    # Overall assessment
    if divergence_pattern == "exact-match":
        overall = "No divergence to explain — classifications are identical."
    elif divergence_pattern == "soft-divergence":
        overall = (
            "Soft divergence: the classifications differ at the primary type level "
            "but agree at the family or alternative-type level.  This is within "
            "expected ODC inter-rater variability (Chillarege 1992)."
        )
    elif divergence_pattern == "moderate-divergence":
        overall = (
            "Moderate divergence: types differ across families but have some "
            "overlap in alternative types.  Evidence asymmetry is the most "
            "likely explanation."
        )
    else:
        overall = (
            "Hard divergence: no agreement at any tier.  This may indicate "
            "a genuinely ambiguous bug or significant evidence asymmetry.  "
            "Manual review is recommended."
        )

    return {
        "applicable_rules": [
            {"condition": r["condition"], "explanation": r["explanation"], "literature": r["literature"]}
            for r in applicable_rules
        ],
        "overall_assessment": overall,
        "divergence_pattern": divergence_pattern,
    }


# ---------------------------------------------------------------------------
# Attribute concordance
# ---------------------------------------------------------------------------

def compute_attribute_concordance(
    prefix_data: dict[str, Any],
    postfix_data: dict[str, Any],
) -> dict[str, Any]:
    """Track agreement on ODC closer attributes beyond the primary type.

    Returns a concordance record showing which attributes agree, disagree,
    or are missing.
    """
    attributes = ["target", "qualifier", "age", "source"]
    concordance: dict[str, Any] = {}
    agreed = 0
    total = 0

    for attr in attributes:
        pre_val = prefix_data.get(attr)
        post_val = postfix_data.get(attr)

        # Normalize None / empty string
        pre_norm = (str(pre_val).strip() if pre_val else "").lower()
        post_norm = (str(post_val).strip() if post_val else "").lower()

        if not pre_norm and not post_norm:
            concordance[attr] = {"status": "both-missing", "pre": pre_val, "post": post_val}
        elif pre_norm == post_norm:
            concordance[attr] = {"status": "agree", "pre": pre_val, "post": post_val}
            agreed += 1
            total += 1
        else:
            concordance[attr] = {"status": "disagree", "pre": pre_val, "post": post_val}
            total += 1

    concordance["concordance_rate"] = (agreed / total) if total > 0 else None
    concordance["agreed_count"] = agreed
    concordance["compared_count"] = total
    return concordance


# ---------------------------------------------------------------------------
# Insight generation
# ---------------------------------------------------------------------------

def generate_comparison_insights(
    prefix_data: dict[str, Any],
    postfix_data: dict[str, Any],
    result: "ComparisonResult",
    distance: float,
    divergence_pattern: str,
    attribute_concordance: dict[str, Any],
) -> list[str]:
    """Generate actionable insights for a single-bug comparison.

    Returns a list of human-readable insight strings suitable for
    inclusion in reports and defense documents.
    """
    insights: list[str] = []

    # 1. Headline insight
    if result.strict_match:
        insights.append(
            f"✅ Both pre-fix and post-fix classifications agree on '{result.prefix_odc_type}'. "
            f"High confidence in classification accuracy."
        )
    elif result.top2_match:
        insights.append(
            f"🔄 Primary types differ ({result.prefix_odc_type} → {result.postfix_odc_type}) but "
            f"overlap through alternative types.  Semantic distance: {distance:.2f} — "
            f"this is within expected ODC ambiguity."
        )
    elif result.family_match:
        insights.append(
            f"📊 Types differ but both belong to the '{result.prefix_family}' family.  "
            f"Semantic distance: {distance:.2f}.  The LLM identified the correct "
            f"defect family but chose different granular types."
        )
    else:
        insights.append(
            f"⚠️ Hard divergence: '{result.prefix_odc_type}' ({result.prefix_family}) vs "
            f"'{result.postfix_odc_type}' ({result.postfix_family}).  "
            f"Semantic distance: {distance:.2f}.  This requires evidence asymmetry analysis."
        )

    # 2. Confidence analysis
    conf_delta = abs(result.prefix_confidence - result.postfix_confidence)
    if conf_delta < 0.05:
        insights.append(
            f"📏 Confidence alignment: both modes show similar confidence "
            f"(pre-fix: {result.prefix_confidence:.2f}, post-fix: {result.postfix_confidence:.2f}).  "
            f"The LLM was equally certain in both evidence conditions."
        )
    elif result.postfix_confidence > result.prefix_confidence:
        insights.append(
            f"📈 Post-fix confidence is higher by {conf_delta:.2f} "
            f"({result.prefix_confidence:.2f} → {result.postfix_confidence:.2f}).  "
            f"The fix diff provides clearer evidence, as expected."
        )
    else:
        insights.append(
            f"📉 Pre-fix confidence is higher by {conf_delta:.2f} "
            f"({result.prefix_confidence:.2f} → {result.postfix_confidence:.2f}).  "
            f"The symptoms may have been more diagnostically clear than the fix diff."
        )

    # 3. Alternative type overlap analysis
    prefix_alt_set = set(result.prefix_alternatives)
    postfix_alt_set = set(result.postfix_alternatives)
    shared_alts = prefix_alt_set & postfix_alt_set
    if shared_alts:
        insights.append(
            f"🔗 Shared alternative types: {', '.join(sorted(shared_alts))}.  "
            f"Both modes recognized these as plausible secondary classifications."
        )

    # Cross-alternative insight (primary appears in other's alternatives)
    if not result.strict_match:
        if result.prefix_odc_type in postfix_alt_set and result.postfix_odc_type in prefix_alt_set:
            insights.append(
                f"↔️ Cross-alternative match: each mode's primary type appears in "
                f"the other's alternative list.  This is strong evidence that both "
                f"types are valid perspectives on the same defect."
            )
        elif result.prefix_odc_type in postfix_alt_set:
            insights.append(
                f"➡️ Pre-fix primary '{result.prefix_odc_type}' recognized as alternative by post-fix."
            )
        elif result.postfix_odc_type in prefix_alt_set:
            insights.append(
                f"⬅️ Post-fix primary '{result.postfix_odc_type}' recognized as alternative by pre-fix."
            )

    # 4. Attribute concordance summary
    conc_rate = attribute_concordance.get("concordance_rate")
    if conc_rate is not None:
        if conc_rate >= 0.75:
            insights.append(
                f"🏷️ High attribute concordance ({conc_rate:.0%}): closer attributes "
                f"(target/qualifier/age/source) largely agree across modes."
            )
        elif conc_rate >= 0.50:
            insights.append(
                f"🏷️ Moderate attribute concordance ({conc_rate:.0%}): some closer attributes "
                f"agree but others diverge."
            )
        elif conc_rate > 0:
            insights.append(
                f"🏷️ Low attribute concordance ({conc_rate:.0%}): closer attributes "
                f"show significant disagreement."
            )

    return insights


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class ComparisonResult:
    """Detailed comparison of one pre-fix vs post-fix classification pair."""

    project_id: str
    bug_id: int
    version_id: str

    # Pre-fix side
    prefix_odc_type: str
    prefix_family: str | None
    prefix_confidence: float
    prefix_alternatives: list[str]
    prefix_evidence_mode: str
    prefix_reasoning_summary: str
    prefix_target: str | None
    prefix_qualifier: str | None
    prefix_age: str | None
    prefix_source: str | None

    # Post-fix side
    postfix_odc_type: str
    postfix_family: str | None
    postfix_confidence: float
    postfix_alternatives: list[str]
    postfix_evidence_mode: str
    postfix_reasoning_summary: str
    postfix_target: str | None
    postfix_qualifier: str | None
    postfix_age: str | None
    postfix_source: str | None

    # Tier metrics
    strict_match: bool
    top2_match: bool
    family_match: bool
    match_detail: str

    # Extended analysis
    semantic_distance: float = 0.0
    divergence_pattern: str = "exact-match"
    evidence_asymmetry: dict[str, Any] = field(default_factory=dict)
    attribute_concordance: dict[str, Any] = field(default_factory=dict)
    insights: list[str] = field(default_factory=list)

    # Additional context
    model: str = ""
    provider: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class BatchComparisonResult:
    """Aggregate comparison across multiple bug pairs."""

    total_bugs: int
    strict_match_count: int
    top2_match_count: int
    family_match_count: int
    strict_match_rate: float
    top2_match_rate: float
    family_match_rate: float
    cohens_kappa: float | None
    avg_semantic_distance: float = 0.0
    divergence_pattern_counts: dict[str, int] = field(default_factory=dict)
    avg_attribute_concordance: float | None = None
    per_project_kappa: dict[str, float | None] = field(default_factory=dict)
    per_bug: list[dict[str, Any]] = field(default_factory=list)
    type_confusion_matrix: dict[str, dict[str, int]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Core comparison functions
# ---------------------------------------------------------------------------

def compare_classifications(
    prefix_data: dict[str, Any],
    postfix_data: dict[str, Any],
) -> ComparisonResult:
    """Compare a pre-fix and post-fix classification for the same bug.

    Produces tier-based accuracy metrics plus extended analysis layers
    including semantic distance, evidence asymmetry, attribute concordance,
    divergence pattern, and actionable insights.
    """

    # Extract alternative type names
    prefix_alts = [
        item.get("type", "") for item in prefix_data.get("alternative_types", [])
        if isinstance(item, dict) and item.get("type")
    ]
    postfix_alts = [
        item.get("type", "") for item in postfix_data.get("alternative_types", [])
        if isinstance(item, dict) and item.get("type")
    ]

    prefix_type = prefix_data.get("odc_type", "")
    postfix_type = postfix_data.get("odc_type", "")
    # Backward compatibility: older artifacts use coarse_group instead of family.
    prefix_family = prefix_data.get("family", prefix_data.get("coarse_group"))
    postfix_family = postfix_data.get("family", postfix_data.get("coarse_group"))
    prefix_target = prefix_data.get("target")
    postfix_target = postfix_data.get("target")
    prefix_qualifier = prefix_data.get("qualifier")
    postfix_qualifier = postfix_data.get("qualifier")
    prefix_age = prefix_data.get("age")
    postfix_age = postfix_data.get("age")
    prefix_source = prefix_data.get("source")
    postfix_source = postfix_data.get("source")

    # Tier 1: Strict match
    strict = prefix_type == postfix_type

    # Tier 2: Top-2 match (primary or in alternatives)
    top2 = (
        strict
        or prefix_type in postfix_alts
        or postfix_type in prefix_alts
    )

    # Tier 3: Family match
    family = prefix_family == postfix_family

    # Build detail string
    if strict:
        detail = f"Exact match: both classified as '{prefix_type}'"
    elif prefix_type in postfix_alts and postfix_type in prefix_alts:
        detail = (
            f"Cross-alternative match: pre-fix '{prefix_type}' is in post-fix alternatives, "
            f"and post-fix '{postfix_type}' is in pre-fix alternatives"
        )
    elif prefix_type in postfix_alts:
        detail = f"Pre-fix primary '{prefix_type}' found in post-fix alternative types"
    elif postfix_type in prefix_alts:
        detail = f"Post-fix primary '{postfix_type}' found in pre-fix alternative types"
    elif family:
        detail = (
            f"Family match only: both '{prefix_family}' but types differ "
            f"('{prefix_type}' vs '{postfix_type}')"
        )
    else:
        detail = (
            f"No match: pre-fix '{prefix_type}' ({prefix_family}) vs "
            f"post-fix '{postfix_type}' ({postfix_family})"
        )

    # Extended Layer A: Semantic distance
    distance = semantic_distance(prefix_type, postfix_type)

    # Extended Layer D: Divergence pattern
    pattern = classify_divergence_pattern(strict, top2, family, distance)

    # Extended Layer B: Evidence asymmetry
    asymmetry = analyze_evidence_asymmetry(prefix_data, postfix_data, pattern)

    # Extended Layer C: Attribute concordance
    concordance = compute_attribute_concordance(prefix_data, postfix_data)

    result = ComparisonResult(
        project_id=prefix_data.get("project_id", ""),
        bug_id=prefix_data.get("bug_id", 0),
        version_id=prefix_data.get("version_id", ""),
        prefix_odc_type=prefix_type,
        prefix_family=prefix_family,
        prefix_confidence=float(prefix_data.get("confidence", 0)),
        prefix_alternatives=prefix_alts,
        prefix_evidence_mode=prefix_data.get("evidence_mode", "pre-fix"),
        prefix_reasoning_summary=prefix_data.get("reasoning_summary", ""),
        prefix_target=prefix_target,
        prefix_qualifier=prefix_qualifier,
        prefix_age=prefix_age,
        prefix_source=prefix_source,
        postfix_odc_type=postfix_type,
        postfix_family=postfix_family,
        postfix_confidence=float(postfix_data.get("confidence", 0)),
        postfix_alternatives=postfix_alts,
        postfix_evidence_mode=postfix_data.get("evidence_mode", "post-fix"),
        postfix_reasoning_summary=postfix_data.get("reasoning_summary", ""),
        postfix_target=postfix_target,
        postfix_qualifier=postfix_qualifier,
        postfix_age=postfix_age,
        postfix_source=postfix_source,
        strict_match=strict,
        top2_match=top2,
        family_match=family,
        match_detail=detail,
        semantic_distance=distance,
        divergence_pattern=pattern,
        evidence_asymmetry=asymmetry,
        attribute_concordance=concordance,
        model=prefix_data.get("model", ""),
        provider=prefix_data.get("provider", ""),
    )

    # Extended Layer E: Generate insights
    result.insights = generate_comparison_insights(
        prefix_data, postfix_data, result, distance, pattern, concordance,
    )

    return result


def batch_compare(pairs: list[tuple[dict, dict]]) -> BatchComparisonResult:
    """Compare multiple pre-fix / post-fix classification pairs and compute aggregate metrics."""

    results: list[ComparisonResult] = []
    for prefix_data, postfix_data in pairs:
        results.append(compare_classifications(prefix_data, postfix_data))

    n = len(results)
    if n == 0:
        return BatchComparisonResult(
            total_bugs=0,
            strict_match_count=0,
            top2_match_count=0,
            family_match_count=0,
            strict_match_rate=0.0,
            top2_match_rate=0.0,
            family_match_rate=0.0,
            cohens_kappa=None,
        )

    strict_count = sum(1 for r in results if r.strict_match)
    top2_count = sum(1 for r in results if r.top2_match)
    family_count = sum(1 for r in results if r.family_match)

    # Build confusion matrix
    confusion: dict[str, dict[str, int]] = {}
    for r in results:
        pre = r.prefix_odc_type
        post = r.postfix_odc_type
        if pre not in confusion:
            confusion[pre] = {}
        confusion[pre][post] = confusion[pre].get(post, 0) + 1

    # Compute Cohen's Kappa
    kappa = compute_cohens_kappa(
        [(r.prefix_odc_type, r.postfix_odc_type) for r in results]
    )

    # Per-project Cohen's Kappa (RQ4.1)
    ppk = compute_per_project_kappa(results)

    # Extended aggregate metrics
    avg_dist = sum(r.semantic_distance for r in results) / n
    pattern_counts: dict[str, int] = {}
    for r in results:
        pattern_counts[r.divergence_pattern] = pattern_counts.get(r.divergence_pattern, 0) + 1

    conc_rates = [
        r.attribute_concordance.get("concordance_rate")
        for r in results
        if r.attribute_concordance.get("concordance_rate") is not None
    ]
    avg_conc = (sum(conc_rates) / len(conc_rates)) if conc_rates else None

    return BatchComparisonResult(
        total_bugs=n,
        strict_match_count=strict_count,
        top2_match_count=top2_count,
        family_match_count=family_count,
        strict_match_rate=strict_count / n,
        top2_match_rate=top2_count / n,
        family_match_rate=family_count / n,
        cohens_kappa=kappa,
        avg_semantic_distance=round(avg_dist, 4),
        divergence_pattern_counts=pattern_counts,
        avg_attribute_concordance=round(avg_conc, 4) if avg_conc is not None else None,
        per_project_kappa=ppk,
        per_bug=[r.to_dict() for r in results],
        type_confusion_matrix=confusion,
    )


def compute_per_project_kappa(
    results: list[ComparisonResult],
) -> dict[str, float | None]:
    """Compute Cohen's Kappa for each Defects4J project separately.

    Returns: {"Lang": 0.72, "Math": 0.58, ...}
    Projects with fewer than 2 bugs return None.
    """
    from collections import defaultdict
    per_project: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for r in results:
        per_project[r.project_id].append((r.prefix_odc_type, r.postfix_odc_type))

    ppk: dict[str, float | None] = {}
    for project in sorted(per_project):
        kappa = compute_cohens_kappa(per_project[project])
        ppk[project] = round(kappa, 4) if kappa is not None else None
    return ppk


def compute_cohens_kappa(pairs: list[tuple[str, str]]) -> float | None:
    """Compute Cohen's Kappa for inter-rater agreement between two classifiers.

    pairs: list of (rater1_label, rater2_label) tuples.
    Returns kappa value, or None if computation is not possible.
    """
    if len(pairs) < 2:
        return None

    n = len(pairs)

    # Collect all unique labels
    all_labels = sorted(set(label for pair in pairs for label in pair))
    if len(all_labels) < 2:
        return 1.0 if all(a == b for a, b in pairs) else 0.0

    # Count agreements and marginals
    label_to_idx = {label: i for i, label in enumerate(all_labels)}
    k = len(all_labels)

    # Build the contingency matrix
    matrix = [[0] * k for _ in range(k)]
    for rater1, rater2 in pairs:
        i = label_to_idx[rater1]
        j = label_to_idx[rater2]
        matrix[i][j] += 1

    # Observed agreement
    observed = sum(matrix[i][i] for i in range(k)) / n

    # Expected agreement by chance
    expected = 0.0
    for i in range(k):
        row_sum = sum(matrix[i][j] for j in range(k)) / n
        col_sum = sum(matrix[j][i] for j in range(k)) / n
        expected += row_sum * col_sum

    if expected >= 1.0:
        return 1.0 if observed >= 1.0 else 0.0

    return (observed - expected) / (1.0 - expected)


# ---------------------------------------------------------------------------
# Report writing
# ---------------------------------------------------------------------------

def write_comparison_report(
    result: ComparisonResult | BatchComparisonResult,
    output_path: Path,
) -> None:
    """Write a human-readable markdown comparison report."""
    from .models import ensure_parent

    lines: list[str] = []

    if isinstance(result, ComparisonResult):
        lines.extend(_single_comparison_report(result))
    else:
        lines.extend(_batch_comparison_report(result))

    ensure_parent(output_path)
    output_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _single_comparison_report(r: ComparisonResult) -> list[str]:
    strict_icon = "✅" if r.strict_match else "❌"
    top2_icon = "✅" if r.top2_match else "❌"
    family_icon = "✅" if r.family_match else "❌"

    lines = [
        f"# ODC Comparison Report: {r.project_id}-{r.bug_id}",
        "",
        f"- Version: `{r.version_id}`",
        f"- Model: `{r.model}` ({r.provider})",
        f"- Divergence Pattern: **{r.divergence_pattern}**",
        f"- Semantic Distance: **{r.semantic_distance:.2f}**",
        "",
        "## Classification Comparison",
        "",
        "| Aspect | Pre-fix | Post-fix |",
        "|--------|---------|----------|",
        f"| **Primary Type** | {r.prefix_odc_type} | {r.postfix_odc_type} |",
        f"| **Family** | {r.prefix_family} | {r.postfix_family} |",
        f"| **Target** | {r.prefix_target or '—'} | {r.postfix_target or '—'} |",
        f"| **Qualifier** | {r.prefix_qualifier or '—'} | {r.postfix_qualifier or '—'} |",
        f"| **Age** | {r.prefix_age or '—'} | {r.postfix_age or '—'} |",
        f"| **Source** | {r.prefix_source or '—'} | {r.postfix_source or '—'} |",
        f"| **Confidence** | {r.prefix_confidence:.2f} | {r.postfix_confidence:.2f} |",
        f"| **Evidence Mode** | {r.prefix_evidence_mode} | {r.postfix_evidence_mode} |",
        f"| **Alternatives** | {', '.join(r.prefix_alternatives) or 'none'} | {', '.join(r.postfix_alternatives) or 'none'} |",
        "",
        "## Accuracy Metrics",
        "",
        f"| Metric | Result |",
        f"|--------|--------|",
        f"| Strict Match (exact type) | {strict_icon} |",
        f"| Top-2 Match (incl. alternatives) | {top2_icon} |",
        f"| Family Match | {family_icon} |",
        f"| Semantic Distance | {r.semantic_distance:.2f} |",
        f"| Divergence Pattern | {r.divergence_pattern} |",
        "",
        f"**Detail**: {r.match_detail}",
        "",
    ]

    # Insights section
    if r.insights:
        lines.extend([
            "## Insights",
            "",
        ])
        for insight in r.insights:
            lines.append(f"- {insight}")
        lines.append("")

    # Evidence asymmetry section
    if r.evidence_asymmetry and r.divergence_pattern != "exact-match":
        lines.extend([
            "## Evidence Asymmetry Analysis",
            "",
            f"**Overall**: {r.evidence_asymmetry.get('overall_assessment', '')}",
            "",
        ])
        for rule in r.evidence_asymmetry.get("applicable_rules", []):
            lines.append(f"### {rule['condition']}")
            lines.append(f"{rule['explanation']}")
            lines.append(f"*Reference*: {rule['literature']}")
            lines.append("")

    # Attribute concordance section
    if r.attribute_concordance:
        conc_rate = r.attribute_concordance.get("concordance_rate")
        if conc_rate is not None:
            lines.extend([
                "## Attribute Concordance",
                "",
                f"Overall concordance rate: **{conc_rate:.0%}**",
                "",
                "| Attribute | Status | Pre-fix | Post-fix |",
                "|-----------|--------|---------|----------|",
            ])
            for attr in ["target", "qualifier", "age", "source"]:
                if attr in r.attribute_concordance and isinstance(r.attribute_concordance[attr], dict):
                    a = r.attribute_concordance[attr]
                    status_icon = "✅" if a["status"] == "agree" else ("—" if a["status"] == "both-missing" else "❌")
                    lines.append(
                        f"| {attr.capitalize()} | {status_icon} {a['status']} "
                        f"| {a.get('pre', '—') or '—'} | {a.get('post', '—') or '—'} |"
                    )
            lines.append("")

    # Reasoning comparison
    lines.extend([
        "## Reasoning Comparison",
        "",
        "### Pre-fix Reasoning",
        r.prefix_reasoning_summary,
        "",
        "### Post-fix Reasoning",
        r.postfix_reasoning_summary,
    ])
    return lines


def _batch_comparison_report(r: BatchComparisonResult) -> list[str]:
    kappa_str = f"{r.cohens_kappa:.3f}" if r.cohens_kappa is not None else "N/A"
    kappa_interp = _interpret_kappa(r.cohens_kappa)

    lines = [
        f"# ODC Batch Comparison Report",
        "",
        f"Total bugs evaluated: **{r.total_bugs}**",
        "",
        "## Aggregate Accuracy",
        "",
        "| Metric | Accuracy | Count |",
        "|--------|----------|-------|",
        f"| Strict Match (exact type) | {r.strict_match_rate:.0%} | {r.strict_match_count}/{r.total_bugs} |",
        f"| Top-2 Match (incl. alternatives) | {r.top2_match_rate:.0%} | {r.top2_match_count}/{r.total_bugs} |",
        f"| Family Match | {r.family_match_rate:.0%} | {r.family_match_count}/{r.total_bugs} |",
        f"| Cohen's Kappa | {kappa_str} | {kappa_interp} |",
        f"| Avg Semantic Distance | {r.avg_semantic_distance:.3f} | — |",
        "",
    ]

    # Per-project Kappa table (RQ4.1)
    if r.per_project_kappa:
        lines.extend([
            "## Per-Project Cohen's Kappa",
            "",
            "| Project | κ | Interpretation |",
            "|---------|---|----------------|",
        ])
        for project, pk in sorted(r.per_project_kappa.items()):
            pk_str = f"{pk:.3f}" if pk is not None else "N/A"
            pk_interp = _interpret_kappa(pk)
            lines.append(f"| {project} | {pk_str} | {pk_interp} |")
        lines.append("")

    # Attribute concordance
    if r.avg_attribute_concordance is not None:
        lines.append(f"Average attribute concordance: **{r.avg_attribute_concordance:.0%}**")
        lines.append("")

    # Divergence pattern breakdown
    if r.divergence_pattern_counts:
        lines.extend([
            "## Divergence Pattern Breakdown",
            "",
            "| Pattern | Count | Rate |",
            "|---------|-------|------|",
        ])
        for pattern, count in sorted(r.divergence_pattern_counts.items()):
            rate = count / r.total_bugs if r.total_bugs else 0
            lines.append(f"| {pattern} | {count} | {rate:.0%} |")
        lines.append("")

    # Confusion matrix
    if r.type_confusion_matrix:
        all_types = sorted(set(
            list(r.type_confusion_matrix.keys()) +
            [t for row in r.type_confusion_matrix.values() for t in row.keys()]
        ))
        lines.extend([
            "## Confusion Matrix (Pre-fix → Post-fix)",
            "",
            "| Pre-fix \\ Post-fix | " + " | ".join(all_types) + " |",
            "|" + "|".join(["---"] * (len(all_types) + 1)) + "|",
        ])
        for pre_type in all_types:
            row_data = r.type_confusion_matrix.get(pre_type, {})
            cells = [str(row_data.get(post_type, 0)) for post_type in all_types]
            lines.append(f"| **{pre_type}** | " + " | ".join(cells) + " |")
        lines.append("")

    # Per-bug details
    if r.per_bug:
        lines.extend([
            "## Per-Bug Results",
            "",
            "| Bug | Pre-fix Type | Post-fix Type | Strict | Top-2 | Family | Distance | Pattern |",
            "|-----|-------------|---------------|--------|-------|--------|----------|---------|",
        ])
        for bug in r.per_bug:
            s = "✅" if bug["strict_match"] else "❌"
            t = "✅" if bug["top2_match"] else "❌"
            c = "✅" if bug["family_match"] else "❌"
            lines.append(
                f"| {bug['project_id']}-{bug['bug_id']} "
                f"| {bug['prefix_odc_type']} "
                f"| {bug['postfix_odc_type']} "
                f"| {s} | {t} | {c} "
                f"| {bug.get('semantic_distance', 0):.2f} "
                f"| {bug.get('divergence_pattern', '—')} |"
            )
        lines.append("")

    return lines


def _interpret_kappa(kappa: float | None) -> str:
    if kappa is None:
        return "insufficient data"
    if kappa >= 0.81:
        return "almost perfect"
    if kappa >= 0.61:
        return "substantial"
    if kappa >= 0.41:
        return "moderate"
    if kappa >= 0.21:
        return "fair"
    if kappa >= 0.01:
        return "slight"
    return "no agreement"
