"""Results export utilities for LaTeX tables and CSV files.

Converts analysis JSON into formats suitable for direct inclusion
in the JSS manuscript or processing in external statistical tools.
"""

from __future__ import annotations

import csv
import io
from pathlib import Path
from typing import Any

from .odc import ODC_TYPE_NAMES


# ---------------------------------------------------------------------------
# LaTeX table helpers
# ---------------------------------------------------------------------------

def _latex_header(caption: str, label: str, columns: list[str]) -> str:
    n = len(columns)
    col_spec = "l" + "r" * (n - 1)
    header = " & ".join(f"\\textbf{{{c}}}" for c in columns)
    return (
        f"\\begin{{table}}[htbp]\n"
        f"\\centering\n"
        f"\\caption{{{caption}}}\n"
        f"\\label{{{label}}}\n"
        f"\\begin{{tabular}}{{{col_spec}}}\n"
        f"\\toprule\n"
        f"{header} \\\\\n"
        f"\\midrule\n"
    )


def _latex_footer() -> str:
    return "\\bottomrule\n\\end{tabular}\n\\end{table}\n"


def _esc(text: str) -> str:
    """Escape LaTeX special characters."""
    return text.replace("_", "\\_").replace("&", "\\&").replace("%", "\\%")


# ---------------------------------------------------------------------------
# RQ1.1: Type Distribution
# ---------------------------------------------------------------------------

def export_type_distribution_latex(analysis: dict[str, Any]) -> str:
    """Generate a LaTeX table of ODC type frequencies.

    Expects either a top-level analysis dict with ``type_distribution_prefix``
    or a direct output from ``compute_type_distribution()``.
    """
    dist = analysis.get("type_distribution_prefix", analysis)
    type_counts: dict[str, int] = dist.get("type_counts", {})
    type_rates: dict[str, float] = dist.get("type_rates", {})
    total = dist.get("total", sum(type_counts.values()))

    lines = _latex_header(
        "ODC Defect Type Distribution (Pre-fix Mode)",
        "tab:type_distribution",
        ["ODC Type", "Count", "Rate (\\%)"],
    )
    for odc_type in ODC_TYPE_NAMES:
        count = type_counts.get(odc_type, 0)
        rate = type_rates.get(odc_type, 0.0)
        lines += f"{_esc(odc_type)} & {count} & {rate * 100:.1f} \\\\\n"
    lines += f"\\midrule\n\\textbf{{Total}} & {total} & 100.0 \\\\\n"
    lines += _latex_footer()
    return lines


# ---------------------------------------------------------------------------
# RQ2.1: 4-Tier Accuracy Metrics
# ---------------------------------------------------------------------------

def export_accuracy_table_latex(analysis: dict[str, Any]) -> str:
    """Generate a LaTeX table for the 4-tier accuracy metrics."""
    lines = _latex_header(
        "Pre-fix vs.\ Post-fix Classification Agreement",
        "tab:accuracy",
        ["Metric", "Count", "Rate", "Interpretation"],
    )
    total = analysis.get("total_pairs", 0)

    metrics = [
        ("Strict Match", analysis.get("strict_match_count", 0),
         analysis.get("strict_match_rate", 0), "Exact type agreement"),
        ("Top-2 Match", analysis.get("top2_match_count", 0),
         analysis.get("top2_match_rate", 0), "Primary or alternative overlap"),
        ("Family Match", analysis.get("family_match_count", 0),
         analysis.get("family_match_rate", 0), "Same ODC family"),
    ]
    for name, count, rate, interp in metrics:
        rate_pct = f"{rate * 100:.1f}\\%" if isinstance(rate, float) else str(rate)
        lines += f"{name} & {count}/{total} & {rate_pct} & {_esc(interp)} \\\\\n"

    kappa = analysis.get("cohens_kappa")
    kappa_str = f"{kappa:.3f}" if kappa is not None else "N/A"
    lines += f"Cohen's $\\kappa$ & -- & {kappa_str} & Inter-rater reliability \\\\\n"
    lines += _latex_footer()
    return lines


# ---------------------------------------------------------------------------
# RQ2.1: Confusion Matrix
# ---------------------------------------------------------------------------

def export_confusion_matrix_latex(analysis: dict[str, Any]) -> str:
    """Generate a LaTeX confusion matrix (prefix × postfix)."""
    matrix = analysis.get("type_confusion_matrix", {})
    types_present = sorted({t for row in matrix.values() for t in row} | set(matrix.keys()))
    # Use short labels
    short = {t: t.split("/")[0][:6] for t in types_present}

    header_cols = [""] + [f"\\rotatebox{{90}}{{{_esc(short[t])}}}" for t in types_present]
    lines = _latex_header(
        "ODC Type Confusion Matrix (Pre-fix $\\times$ Post-fix)",
        "tab:confusion",
        header_cols,
    )
    for row_type in types_present:
        row_data = matrix.get(row_type, {})
        cells = [str(row_data.get(col_type, 0)) for col_type in types_present]
        lines += f"{_esc(short[row_type])} & {' & '.join(cells)} \\\\\n"
    lines += _latex_footer()
    return lines


# ---------------------------------------------------------------------------
# RQ2.2: Baseline Comparison
# ---------------------------------------------------------------------------

def export_baseline_comparison_latex(analysis: dict[str, Any]) -> str:
    """Generate a LaTeX table comparing scientific vs direct baseline."""
    baseline_data = analysis.get("baseline_comparison", {})
    sci = baseline_data.get("scientific", {})
    base = baseline_data.get("baseline", {})
    deltas = baseline_data.get("improvement_deltas", {})

    lines = _latex_header(
        "Scientific Protocol vs.\ Direct Baseline",
        "tab:baseline",
        ["Metric", "Scientific", "Baseline", "$\\Delta$"],
    )
    for metric, label in [
        ("strict_match_rate", "Strict Match"),
        ("top2_match_rate", "Top-2 Match"),
        ("family_match_rate", "Family Match"),
    ]:
        s_val = f"{sci.get(metric, 0) * 100:.1f}\\%"
        b_val = f"{base.get(metric, 0) * 100:.1f}\\%"
        d_val = f"{deltas.get(metric, 0) * 100:+.1f}pp"
        lines += f"{label} & {s_val} & {b_val} & {d_val} \\\\\n"

    s_conf = f"{sci.get('mean_confidence', 0):.3f}"
    b_conf = f"{base.get('mean_confidence', 0):.3f}"
    d_conf = f"{baseline_data.get('confidence_delta', 0):+.3f}"
    lines += f"Mean Confidence & {s_conf} & {b_conf} & {d_conf} \\\\\n"
    lines += _latex_footer()
    return lines


# ---------------------------------------------------------------------------
# RQ4.1: Per-project Kappa
# ---------------------------------------------------------------------------

def export_per_project_kappa_latex(analysis: dict[str, Any]) -> str:
    """Generate a LaTeX table of per-project Kappa values."""
    per_project = analysis.get("per_project_kappa", {})
    lines = _latex_header(
        "Cohen's $\\kappa$ by Defects4J Project",
        "tab:per_project_kappa",
        ["Project", "$\\kappa$", "Interpretation"],
    )
    for project in sorted(per_project.keys()):
        kappa = per_project[project]
        if kappa is None:
            k_str = "N/A"
            interp = "Insufficient data"
        else:
            k_str = f"{kappa:.3f}"
            if kappa >= 0.81:
                interp = "Almost perfect"
            elif kappa >= 0.61:
                interp = "Substantial"
            elif kappa >= 0.41:
                interp = "Moderate"
            elif kappa >= 0.21:
                interp = "Fair"
            else:
                interp = "Slight"
        lines += f"{_esc(project)} & {k_str} & {interp} \\\\\n"

    global_kappa = analysis.get("cohens_kappa")
    g_str = f"{global_kappa:.3f}" if global_kappa is not None else "N/A"
    lines += f"\\midrule\n\\textbf{{Global}} & {g_str} & -- \\\\\n"
    lines += _latex_footer()
    return lines


# ---------------------------------------------------------------------------
# RQ2.3: Taxonomy Grounding Effect
# ---------------------------------------------------------------------------

def export_taxonomy_grounding_latex(analysis: dict[str, Any]) -> str:
    """Generate a LaTeX table comparing naive vs direct vs scientific tiers."""
    grounding = analysis.get("taxonomy_grounding", {})
    naive = grounding.get("naive", {})
    direct = grounding.get("direct", {})
    scientific = grounding.get("scientific", {})

    lines = _latex_header(
        "Taxonomy Grounding Effect: Naive vs.\\ Direct vs.\\ Scientific",
        "tab:taxonomy_grounding",
        ["Metric", "Naive", "Direct", "Scientific"],
    )
    lines += (
        f"Unique Labels & {naive.get('unique_labels', 0)} "
        f"& {direct.get('unique_labels', 0)} "
        f"& {scientific.get('unique_labels', 0)} \\\\\n"
    )
    lines += (
        f"Label Entropy & {naive.get('label_entropy', 0):.2f} "
        f"& -- & -- \\\\\n"
    )
    lines += (
        f"ODC Coverage & {naive.get('odc_coverage', 0)}/7 "
        f"& {direct.get('unique_labels', 0)}/7 "
        f"& {scientific.get('unique_labels', 0)}/7 \\\\\n"
    )
    vocab_reduction = grounding.get("vocabulary_reduction_ratio", 0)
    lines += f"Vocab Reduction & \\multicolumn{{3}}{{c}}{{{vocab_reduction * 100:.1f}\\%}} \\\\\n"
    lines += _latex_footer()
    return lines


# ---------------------------------------------------------------------------
# CSV Export
# ---------------------------------------------------------------------------

def export_all_csv(analysis: dict[str, Any], output_dir: Path) -> list[Path]:
    """Export analysis data as CSV files suitable for R or SPSS.

    Returns list of written file paths.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    # Per-bug comparison detail
    per_bug = analysis.get("per_bug", [])
    if per_bug:
        path = output_dir / "per_bug_comparison.csv"
        _write_csv(path, per_bug)
        written.append(path)

    # Type distribution
    dist = analysis.get("type_distribution_prefix", {})
    if dist.get("type_counts"):
        rows = [
            {"odc_type": t, "count": c, "rate": dist.get("type_rates", {}).get(t, 0)}
            for t, c in dist["type_counts"].items()
        ]
        path = output_dir / "type_distribution.csv"
        _write_csv(path, rows)
        written.append(path)

    # Per-project Kappa
    ppk = analysis.get("per_project_kappa", {})
    if ppk:
        rows = [{"project": p, "kappa": k} for p, k in sorted(ppk.items())]
        path = output_dir / "per_project_kappa.csv"
        _write_csv(path, rows)
        written.append(path)

    # Semantic gap per-bug
    sg = analysis.get("semantic_gap", {})
    if sg.get("per_bug"):
        path = output_dir / "semantic_gap_per_bug.csv"
        _write_csv(path, sg["per_bug"])
        written.append(path)

    # Per-type metrics
    ptm = analysis.get("per_type_metrics", {})
    if ptm:
        rows = [{"odc_type": t, **metrics} for t, metrics in sorted(ptm.items())]
        path = output_dir / "per_type_metrics.csv"
        _write_csv(path, rows)
        written.append(path)

    return written


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    """Write a list of dicts to a CSV file."""
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
