"""Comparison logic for evaluating pre-fix vs post-fix ODC classifications.

Implements a multi-tier accuracy framework:
  Tier 1 — Strict Match:       exact odc_type agreement
  Tier 2 — Top-2 Match:        primary or alternative_types overlap
    Tier 3 — Family Match:       same high-level category
  Tier 4 — Cohen's Kappa:      inter-rater agreement statistic
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


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

    # Post-fix side
    postfix_odc_type: str
    postfix_family: str | None
    postfix_confidence: float
    postfix_alternatives: list[str]
    postfix_evidence_mode: str
    postfix_reasoning_summary: str

    # Tier metrics
    strict_match: bool
    top2_match: bool
    family_match: bool
    match_detail: str

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
    per_bug: list[dict[str, Any]] = field(default_factory=list)
    type_confusion_matrix: dict[str, dict[str, int]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def compare_classifications(
    prefix_data: dict[str, Any],
    postfix_data: dict[str, Any],
) -> ComparisonResult:
    """Compare a pre-fix and post-fix classification for the same bug."""

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

    return ComparisonResult(
        project_id=prefix_data.get("project_id", ""),
        bug_id=prefix_data.get("bug_id", 0),
        version_id=prefix_data.get("version_id", ""),
        prefix_odc_type=prefix_type,
        prefix_family=prefix_family,
        prefix_confidence=float(prefix_data.get("confidence", 0)),
        prefix_alternatives=prefix_alts,
        prefix_evidence_mode=prefix_data.get("evidence_mode", "pre-fix"),
        prefix_reasoning_summary=prefix_data.get("reasoning_summary", ""),
        postfix_odc_type=postfix_type,
        postfix_family=postfix_family,
        postfix_confidence=float(postfix_data.get("confidence", 0)),
        postfix_alternatives=postfix_alts,
        postfix_evidence_mode=postfix_data.get("evidence_mode", "post-fix"),
        postfix_reasoning_summary=postfix_data.get("reasoning_summary", ""),
        strict_match=strict,
        top2_match=top2,
        family_match=family,
        match_detail=detail,
        model=prefix_data.get("model", ""),
        provider=prefix_data.get("provider", ""),
    )


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

    return BatchComparisonResult(
        total_bugs=n,
        strict_match_count=strict_count,
        top2_match_count=top2_count,
        family_match_count=family_count,
        strict_match_rate=strict_count / n,
        top2_match_rate=top2_count / n,
        family_match_rate=family_count / n,
        cohens_kappa=kappa,
        per_bug=[r.to_dict() for r in results],
        type_confusion_matrix=confusion,
    )


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
        "",
        "## Classification Comparison",
        "",
        "| Aspect | Pre-fix | Post-fix |",
        "|--------|---------|----------|",
        f"| **Primary Type** | {r.prefix_odc_type} | {r.postfix_odc_type} |",
        f"| **Family** | {r.prefix_family} | {r.postfix_family} |",
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
        "",
        f"**Detail**: {r.match_detail}",
        "",
        "## Reasoning Comparison",
        "",
        "### Pre-fix Reasoning",
        r.prefix_reasoning_summary,
        "",
        "### Post-fix Reasoning",
        r.postfix_reasoning_summary,
    ]
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
        "",
    ]

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
            "| Bug | Pre-fix Type | Post-fix Type | Strict | Top-2 | Family | Detail |",
            "|-----|-------------|---------------|--------|-------|--------|--------|",
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
                f"| {bug['match_detail'][:60]}... |"
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
