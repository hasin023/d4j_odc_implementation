"""Cross-study statistical analysis for JSS research questions.

This module provides the analytical functions that transform raw classification
and comparison artifacts into the empirical results needed for each RQ:

- RQ1.1: ODC type distribution and per-project correlation
- RQ1.2: Impact vs Type separation analysis
- RQ2.1: Overall pipeline efficacy metrics (per-type P/R/F1)
- RQ2.2: Baseline vs scientific protocol comparison
- RQ3.1: Semantic gap quantification
- RQ4.1: Per-project Cohen's Kappa
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from .odc import ODC_TYPE_NAMES, ODC_TYPES, family_for


# ---------------------------------------------------------------------------
# RQ1.1: Type Distribution Analysis
# ---------------------------------------------------------------------------

def compute_type_distribution(
    classifications: list[dict[str, Any]],
) -> dict[str, Any]:
    """Compute ODC type and family frequency distributions.

    Returns a dict with:
      - type_counts: {odc_type: count}
      - family_counts: {family: count}
      - per_project: {project: {type: count}}
      - total: int
    """
    type_counter: Counter[str] = Counter()
    family_counter: Counter[str] = Counter()
    per_project: dict[str, Counter[str]] = {}

    for cls in classifications:
        odc_type = cls.get("odc_type", "")
        project = cls.get("project_id", "Unknown")
        if odc_type not in ODC_TYPE_NAMES:
            continue
        type_counter[odc_type] += 1
        family = family_for(odc_type) or "Unknown"
        family_counter[family] += 1
        per_project.setdefault(project, Counter())[odc_type] += 1

    total = sum(type_counter.values())
    return {
        "type_counts": dict(type_counter.most_common()),
        "type_rates": {t: round(c / total, 4) if total else 0.0 for t, c in type_counter.items()},
        "family_counts": dict(family_counter.most_common()),
        "family_rates": {f: round(c / total, 4) if total else 0.0 for f, c in family_counter.items()},
        "per_project": {p: dict(c.most_common()) for p, c in sorted(per_project.items())},
        "total": total,
    }


def compute_project_type_correlation(
    classifications: list[dict[str, Any]],
) -> dict[str, Any]:
    """Test whether ODC type distribution differs significantly across projects.

    Uses a chi-squared test of independence. Returns:
      - observed: contingency table {project: {type: count}}
      - chi2: test statistic (None if scipy unavailable)
      - p_value: p-value (None if scipy unavailable)
      - dof: degrees of freedom
      - significant: bool (p < 0.05)
    """
    per_project: dict[str, Counter[str]] = {}
    for cls in classifications:
        odc_type = cls.get("odc_type", "")
        project = cls.get("project_id", "Unknown")
        if odc_type not in ODC_TYPE_NAMES:
            continue
        per_project.setdefault(project, Counter())[odc_type] += 1

    projects = sorted(per_project.keys())
    types_seen = sorted({t for c in per_project.values() for t in c})

    if len(projects) < 2 or len(types_seen) < 2:
        return {
            "observed": {p: dict(c) for p, c in per_project.items()},
            "chi2": None,
            "p_value": None,
            "dof": 0,
            "significant": False,
            "note": "Insufficient data for chi-squared test (need ≥2 projects and ≥2 types).",
        }

    # Build contingency table as a 2D list
    table: list[list[int]] = []
    for project in projects:
        row = [per_project[project].get(t, 0) for t in types_seen]
        table.append(row)

    try:
        from scipy.stats import chi2_contingency  # type: ignore[import-untyped]
        chi2, p_value, dof, _ = chi2_contingency(table)
        return {
            "observed": {p: dict(per_project[p]) for p in projects},
            "chi2": round(chi2, 4),
            "p_value": round(p_value, 6),
            "dof": int(dof),
            "significant": p_value < 0.05,
        }
    except ImportError:
        # Fallback: report the contingency table without the test
        return {
            "observed": {p: dict(per_project[p]) for p in projects},
            "chi2": None,
            "p_value": None,
            "dof": (len(projects) - 1) * (len(types_seen) - 1),
            "significant": False,
            "note": "scipy not installed — chi-squared test skipped. Install scipy for full analysis.",
        }


# ---------------------------------------------------------------------------
# RQ1.2: Impact vs Type Separation
# ---------------------------------------------------------------------------

def analyze_impact_vs_type(
    classifications: list[dict[str, Any]],
) -> dict[str, Any]:
    """Track how LLM inferred_impact aligns or conflicts with odc_type.

    Demonstrates the IBM v5.2 principle that Impact ≠ Type.  For example,
    when impact='Reliability' (crash/hang) but type='Checking' (missing guard),
    the pipeline correctly separates symptom from root cause.

    Returns:
      - total_with_impact: int
      - impact_type_pairs: [{impact, odc_type, count}]
      - separation_examples: cases where impact doesn't trivially map to type
      - symptom_label_accuracy: how often a naive symptom→type mapping would match
    """
    impact_type_counter: Counter[tuple[str, str]] = Counter()
    total_with_impact = 0

    for cls in classifications:
        odc_type = cls.get("odc_type", "")
        impacts = cls.get("inferred_impact", [])
        if not impacts or odc_type not in ODC_TYPE_NAMES:
            continue
        total_with_impact += 1
        for impact in impacts:
            impact_type_counter[(impact, odc_type)] += 1

    # Build the pairs list sorted by frequency
    pairs = [
        {"impact": impact, "odc_type": odc_type, "count": count}
        for (impact, odc_type), count in impact_type_counter.most_common()
    ]

    # Naive symptom→type mapping (the mapping a non-ODC classifier might use)
    _NAIVE_MAP: dict[str, str] = {
        "Performance": "Timing/Serialization",
        "Reliability": "Checking",
        "Capability": "Function/Class/Object",
        "Integrity/Security": "Checking",
        "Documentation": "Function/Class/Object",
    }
    naive_correct = 0
    naive_total = 0
    separation_examples: list[dict[str, str]] = []

    for (impact, odc_type), count in impact_type_counter.items():
        naive_type = _NAIVE_MAP.get(impact)
        if naive_type:
            naive_total += count
            if naive_type == odc_type:
                naive_correct += count
            else:
                separation_examples.append({
                    "impact": impact,
                    "actual_type": odc_type,
                    "naive_would_be": naive_type,
                    "count": count,
                })

    symptom_accuracy = round(naive_correct / naive_total, 4) if naive_total else None

    return {
        "total_with_impact": total_with_impact,
        "impact_type_pairs": pairs,
        "separation_examples": sorted(separation_examples, key=lambda x: x["count"], reverse=True),
        "symptom_label_accuracy": symptom_accuracy,
        "naive_total": naive_total,
        "naive_correct": naive_correct,
    }


# ---------------------------------------------------------------------------
# RQ2.1: Per-type Precision / Recall / F1
# ---------------------------------------------------------------------------

def compute_per_type_metrics(
    pairs: list[tuple[dict[str, Any], dict[str, Any]]],
) -> dict[str, dict[str, float | None]]:
    """Compute precision, recall, and F1 for each ODC type.

    Treats post-fix classifications as the reference (closer to ground truth
    because they see the actual fix), and pre-fix as the prediction.

    Returns: {odc_type: {"precision": float, "recall": float, "f1": float}}
    """
    # Build confusion counts: tp, fp, fn per type
    tp: Counter[str] = Counter()
    fp: Counter[str] = Counter()
    fn: Counter[str] = Counter()

    for prefix_cls, postfix_cls in pairs:
        pred = prefix_cls.get("odc_type", "")
        true = postfix_cls.get("odc_type", "")
        if pred not in ODC_TYPE_NAMES or true not in ODC_TYPE_NAMES:
            continue
        if pred == true:
            tp[pred] += 1
        else:
            fp[pred] += 1  # pred was wrong → false positive for pred type
            fn[true] += 1  # true was missed → false negative for true type

    result: dict[str, dict[str, float | None]] = {}
    for odc_type in ODC_TYPE_NAMES:
        t = tp[odc_type]
        f_p = fp[odc_type]
        f_n = fn[odc_type]
        precision = round(t / (t + f_p), 4) if (t + f_p) > 0 else None
        recall = round(t / (t + f_n), 4) if (t + f_n) > 0 else None
        if precision is not None and recall is not None and (precision + recall) > 0:
            f1 = round(2 * precision * recall / (precision + recall), 4)
        else:
            f1 = None
        result[odc_type] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "tp": t,
            "fp": f_p,
            "fn": f_n,
        }

    return result


# ---------------------------------------------------------------------------
# RQ2.2: Baseline vs Scientific Protocol Comparison
# ---------------------------------------------------------------------------

def compare_baseline_vs_scientific(
    *,
    scientific_classifications: list[dict[str, Any]],
    baseline_classifications: list[dict[str, Any]],
    postfix_classifications: list[dict[str, Any]],
) -> dict[str, Any]:
    """Compare the scientific prompt protocol against the direct (zero-shot) baseline.

    Both sets are compared against the post-fix classifications as reference.
    Metrics: strict/top2/family match rates for each, confidence distributions.

    All three lists must be aligned by index (same bug order).
    """
    def _match_stats(
        predictions: list[dict[str, Any]],
        references: list[dict[str, Any]],
    ) -> dict[str, Any]:
        strict = top2 = family = 0
        confidences: list[float] = []
        n = 0
        for pred, ref in zip(predictions, references):
            pred_type = pred.get("odc_type", "")
            ref_type = ref.get("odc_type", "")
            if pred_type not in ODC_TYPE_NAMES or ref_type not in ODC_TYPE_NAMES:
                continue
            n += 1
            if pred_type == ref_type:
                strict += 1
            # Top-2: check alternatives
            pred_alts = {
                a.get("type", "") for a in pred.get("alternative_types", [])
                if isinstance(a, dict)
            }
            if pred_type == ref_type or ref_type in pred_alts:
                top2 += 1
            # Family match
            pred_family = family_for(pred_type)
            ref_family = family_for(ref_type)
            if pred_family and pred_family == ref_family:
                family += 1
            confidences.append(float(pred.get("confidence", 0.0)))

        return {
            "total": n,
            "strict_match_count": strict,
            "strict_match_rate": round(strict / n, 4) if n else 0.0,
            "top2_match_count": top2,
            "top2_match_rate": round(top2 / n, 4) if n else 0.0,
            "family_match_count": family,
            "family_match_rate": round(family / n, 4) if n else 0.0,
            "mean_confidence": round(sum(confidences) / len(confidences), 4) if confidences else 0.0,
        }

    sci_stats = _match_stats(scientific_classifications, postfix_classifications)
    base_stats = _match_stats(baseline_classifications, postfix_classifications)

    # Compute improvement deltas
    deltas: dict[str, float] = {}
    for metric in ("strict_match_rate", "top2_match_rate", "family_match_rate"):
        deltas[metric] = round(sci_stats[metric] - base_stats[metric], 4)

    return {
        "scientific": sci_stats,
        "baseline": base_stats,
        "improvement_deltas": deltas,
        "confidence_delta": round(sci_stats["mean_confidence"] - base_stats["mean_confidence"], 4),
    }


# ---------------------------------------------------------------------------
# RQ3.1: Semantic Gap Quantification
# ---------------------------------------------------------------------------

def compute_semantic_gap_metrics(
    pairs: list[tuple[dict[str, Any], dict[str, Any]]],
) -> dict[str, Any]:
    """Quantify the semantic gap between pre-fix and post-fix classifications.

    Returns aggregate and per-project semantic distance metrics, confidence
    delta distribution, and divergence pattern breakdown.
    """
    from .comparison import semantic_distance, classify_divergence_pattern

    distances: list[float] = []
    confidence_deltas: list[float] = []
    per_project_distances: dict[str, list[float]] = {}
    per_family_distances: dict[str, list[float]] = {}
    pattern_counter: Counter[str] = Counter()
    per_bug: list[dict[str, Any]] = []

    for prefix_cls, postfix_cls in pairs:
        prefix_type = prefix_cls.get("odc_type", "")
        postfix_type = postfix_cls.get("odc_type", "")
        project = prefix_cls.get("project_id", "Unknown")

        if prefix_type not in ODC_TYPE_NAMES or postfix_type not in ODC_TYPE_NAMES:
            continue

        dist = semantic_distance(prefix_type, postfix_type)
        distances.append(dist)

        conf_delta = abs(
            float(prefix_cls.get("confidence", 0)) - float(postfix_cls.get("confidence", 0))
        )
        confidence_deltas.append(conf_delta)

        per_project_distances.setdefault(project, []).append(dist)

        prefix_family = family_for(prefix_type) or "Unknown"
        per_family_distances.setdefault(prefix_family, []).append(dist)

        strict = prefix_type == postfix_type
        # Top-2 check
        prefix_alts = {
            a.get("type", "") for a in prefix_cls.get("alternative_types", [])
            if isinstance(a, dict)
        }
        postfix_alts = {
            a.get("type", "") for a in postfix_cls.get("alternative_types", [])
            if isinstance(a, dict)
        }
        top2 = strict or postfix_type in prefix_alts or prefix_type in postfix_alts
        fam_match = prefix_family == (family_for(postfix_type) or "")
        pattern = classify_divergence_pattern(strict, top2, fam_match, dist)
        pattern_counter[pattern] += 1

        per_bug.append({
            "project_id": project,
            "bug_id": prefix_cls.get("bug_id"),
            "prefix_type": prefix_type,
            "postfix_type": postfix_type,
            "semantic_distance": round(dist, 4),
            "confidence_delta": round(conf_delta, 4),
            "divergence_pattern": pattern,
        })

    n = len(distances)
    sorted_dists = sorted(distances)
    median_dist = sorted_dists[n // 2] if n else 0.0

    return {
        "total_pairs": n,
        "mean_semantic_distance": round(sum(distances) / n, 4) if n else 0.0,
        "median_semantic_distance": round(median_dist, 4),
        "max_semantic_distance": round(max(distances), 4) if distances else 0.0,
        "mean_confidence_delta": round(sum(confidence_deltas) / n, 4) if n else 0.0,
        "divergence_patterns": dict(pattern_counter.most_common()),
        "per_project": {
            p: {
                "mean_distance": round(sum(ds) / len(ds), 4) if ds else 0.0,
                "count": len(ds),
            }
            for p, ds in sorted(per_project_distances.items())
        },
        "per_family": {
            f: {
                "mean_distance": round(sum(ds) / len(ds), 4) if ds else 0.0,
                "count": len(ds),
            }
            for f, ds in sorted(per_family_distances.items())
        },
        "per_bug": per_bug,
    }


# ---------------------------------------------------------------------------
# RQ2.3: Taxonomy Grounding Effect (Naive Label Analysis)
# ---------------------------------------------------------------------------

# Keyword sets for mapping free-form labels to ODC types.
# Derived from odc.py indicator text and common developer terminology.
_NAIVE_TO_ODC_KEYWORDS: dict[str, list[str]] = {
    "Checking": [
        "null", "check", "guard", "validation", "missing check", "bounds",
        "boundary", "null pointer", "npe", "assert", "condition", "if-condition",
        "exception handling", "missing validation", "range check", "overflow",
        "underflow", "missing guard", "null check", "type check",
    ],
    "Assignment/Initialization": [
        "initialization", "assignment", "initial value", "default value",
        "wrong value", "constant", "variable assignment", "init", "initialized",
        "wrong constant", "incorrect value", "wrong default", "misconfiguration",
        "configuration error", "wrong assignment", "uninitialized",
    ],
    "Algorithm/Method": [
        "algorithm", "logic", "computation", "formula", "calculation",
        "wrong logic", "incorrect logic", "loop", "iteration", "sorting",
        "wrong formula", "procedure", "wrong computation", "incorrect algorithm",
        "off-by-one", "index", "indexing", "mathematical", "arithmetic",
        "wrong order", "sequence error", "data processing",
    ],
    "Interface/O-O Messages": [
        "interface", "api", "parameter", "argument", "method signature",
        "contract", "caller", "callee", "type mismatch", "parameter order",
        "wrong parameter", "api misuse", "method call", "invocation",
        "interoperability", "compatibility", "protocol",
    ],
    "Timing/Serialization": [
        "timing", "race", "concurrency", "thread", "synchronization",
        "deadlock", "serialization", "order", "lifecycle", "async",
        "parallel", "mutex", "lock", "race condition", "thread safety",
    ],
    "Function/Class/Object": [
        "missing feature", "not implemented", "design", "capability",
        "missing method", "missing class", "unimplemented", "stub",
        "missing functionality", "design flaw", "architectural",
        "missing implementation", "feature gap",
    ],
    "Relationship": [
        "relationship", "association", "coupling", "dependency",
        "data structure", "inheritance", "polymorphism", "mapping",
        "linked", "reference", "foreign key", "association error",
    ],
}


def map_naive_to_odc(naive_label: str) -> tuple[str, float]:
    """Map a free-form defect label to the closest ODC type using keyword heuristics.

    Returns (best_odc_type, confidence_score) where confidence is 0.0-1.0.
    If no keywords match, returns ("Unknown", 0.0).
    """
    label_lower = naive_label.lower().strip()
    if not label_lower:
        return ("Unknown", 0.0)

    scores: dict[str, float] = {}
    for odc_type, keywords in _NAIVE_TO_ODC_KEYWORDS.items():
        score = 0.0
        for kw in keywords:
            if kw in label_lower:
                # Longer keyword matches are weighted more heavily
                score += len(kw.split())
        scores[odc_type] = score

    best_type = max(scores, key=scores.get)  # type: ignore[arg-type]
    best_score = scores[best_type]

    if best_score == 0.0:
        return ("Unknown", 0.0)

    # Normalize confidence: cap at 1.0
    total_score = sum(scores.values())
    confidence = round(best_score / total_score, 4) if total_score > 0 else 0.0
    return (best_type, confidence)


def analyze_naive_labels(
    naive_classifications: list[dict[str, Any]],
) -> dict[str, Any]:
    """Analyze free-form labels from naive (taxonomy-free) classifications.

    Returns:
      - unique_labels: number of distinct free-form labels
      - label_counts: {label: count} frequency distribution
      - label_entropy: Shannon entropy of the label distribution
      - odc_mapping: {naive_label: {odc_type, confidence}} for each unique label
      - odc_coverage: how many of the 7 ODC types are naturally discovered
      - mapped_distribution: {odc_type: count} after mapping
    """
    import math

    labels: list[str] = []
    for cls in naive_classifications:
        label = cls.get("odc_type", cls.get("defect_type", "")).strip()
        if label:
            labels.append(label)

    if not labels:
        return {
            "unique_labels": 0,
            "label_counts": {},
            "label_entropy": 0.0,
            "odc_mapping": {},
            "odc_coverage": 0,
            "mapped_distribution": {},
            "total": 0,
        }

    label_counter = Counter(labels)
    total = len(labels)
    unique = len(label_counter)

    # Shannon entropy
    entropy = 0.0
    for count in label_counter.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)

    # Map each unique label to closest ODC type
    odc_mapping: dict[str, dict[str, Any]] = {}
    mapped_counter: Counter[str] = Counter()
    for label in label_counter:
        odc_type, confidence = map_naive_to_odc(label)
        odc_mapping[label] = {
            "odc_type": odc_type,
            "confidence": confidence,
            "count": label_counter[label],
        }
        mapped_counter[odc_type] += label_counter[label]

    # ODC coverage: how many of the 7 canonical types are represented
    odc_coverage = len(
        {t for t in mapped_counter if t in ODC_TYPE_NAMES}
    )

    return {
        "unique_labels": unique,
        "label_counts": dict(label_counter.most_common()),
        "label_entropy": round(entropy, 4),
        "odc_mapping": odc_mapping,
        "odc_coverage": odc_coverage,
        "odc_coverage_types": sorted(t for t in mapped_counter if t in ODC_TYPE_NAMES),
        "mapped_distribution": dict(mapped_counter.most_common()),
        "total": total,
    }


def compute_taxonomy_grounding_metrics(
    *,
    naive_classifications: list[dict[str, Any]],
    direct_classifications: list[dict[str, Any]],
    scientific_classifications: list[dict[str, Any]],
) -> dict[str, Any]:
    """Compare all three prompt tiers for RQ2.3 taxonomy grounding analysis.

    Returns vocabulary size, entropy, and ODC coverage for each tier,
    plus the improvement from naive→direct (taxonomy effect) and
    direct→scientific (protocol effect).
    """
    naive_analysis = analyze_naive_labels(naive_classifications)

    # Direct and scientific use fixed ODC labels — compute their stats for comparison
    direct_labels = [c.get("odc_type", "") for c in direct_classifications if c.get("odc_type") in ODC_TYPE_NAMES]
    scientific_labels = [c.get("odc_type", "") for c in scientific_classifications if c.get("odc_type") in ODC_TYPE_NAMES]

    direct_unique = len(set(direct_labels))
    scientific_unique = len(set(scientific_labels))

    # Vocabulary reduction ratio: how much the taxonomy constrains label space
    naive_unique = naive_analysis["unique_labels"]
    vocab_reduction = round(1.0 - (7 / naive_unique), 4) if naive_unique > 7 else 0.0

    return {
        "naive": {
            "unique_labels": naive_unique,
            "label_entropy": naive_analysis["label_entropy"],
            "odc_coverage": naive_analysis["odc_coverage"],
            "odc_coverage_types": naive_analysis.get("odc_coverage_types", []),
            "total": naive_analysis["total"],
            "mapped_distribution": naive_analysis["mapped_distribution"],
        },
        "direct": {
            "unique_labels": direct_unique,
            "total": len(direct_labels),
        },
        "scientific": {
            "unique_labels": scientific_unique,
            "total": len(scientific_labels),
        },
        "vocabulary_reduction_ratio": vocab_reduction,
        "taxonomy_constrains_labels": naive_unique > 7,
        "naive_label_details": naive_analysis["label_counts"],
        "naive_odc_mapping": naive_analysis["odc_mapping"],
    }

