"""Combined cross-project supervisor report (scientific-open only).

Pools all 6 classified Defects4J projects into one workbook: bug-level defect
type tables plus pooled-then-per-project distribution and drift-matrix
tabs. No cross-strategy (ablation) content and no per-bug rationale text;
this report is deliberately narrower than the per-project reports.

Usage: python scripts/reports/generate_combined_report.py [output_path]
(output_path defaults to .dist/study/combined_report.xlsx, relative to repo root)
"""
import sys
import re
import json
from pathlib import Path
from collections import Counter

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_ROOT = REPO_ROOT / ".dist/study/artifacts_full"

sys.path.insert(0, str(REPO_ROOT))
from d4j_odc_pipeline.odc import ODC_TYPE_NAMES, OTHER_TYPE_NAME

PROJECTS = [
    ("Chart", "manifest_chart26", 26),
    ("Closure", "manifest_closure174", 174),
    ("Lang", "manifest_lang61", 61),
    ("Math", "manifest_math106", 106),
    ("Mockito", "manifest_mockito38", 38),
    ("Time", "manifest_time26", 26),
]
CONDITION_TAG = "scientific-open"

HEADER_FILL = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
HEADER_FONT = Font(bold=True)
HIGHLIGHT = PatternFill(start_color="FFF3B0", end_color="FFF3B0", fill_type="solid")
TITLE_FONT = Font(bold=True)

HEAT_LOW = (255, 255, 255)
HEAT_HIGH = (230, 81, 0)  # deep orange


def load_classification(project, bug_id, arm, tag):
    p = ARTIFACTS_ROOT / arm / f"{project}_{bug_id}_{arm}" / f"classification.{tag}.json"
    if not p.exists():
        return None
    return json.loads(p.read_text())


def load_bug_url(project, bug_id):
    p = ARTIFACTS_ROOT / "prefix" / f"{project}_{bug_id}_prefix" / "context.json"
    if not p.exists():
        return "UNKNOWN"
    ctx = json.loads(p.read_text())
    url = ctx.get("metadata", {}).get("report.url")
    if url:
        return url
    bug_info = ctx.get("bug_info", "")
    m = re.search(r"Bug report url:\s*\n(.*)", bug_info)
    if m:
        return m.group(1).strip()
    return "UNKNOWN"


def set_url_cell(ws, row, col, url):
    cell = ws.cell(row=row, column=col, value=url)
    if url and url != "UNKNOWN":
        cell.hyperlink = url
        cell.font = Font(color="0563C1", underline="single")


def style_header(ws, row, ncols):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row, column=c)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL


def heat_fill(value, max_value):
    if max_value <= 0 or value <= 0:
        return None
    t = 0.2 + 0.8 * (value / max_value)
    rgb = tuple(int(HEAT_LOW[i] + (HEAT_HIGH[i] - HEAT_LOW[i]) * t) for i in range(3))
    hexcolor = "%02X%02X%02X" % rgb
    return PatternFill(start_color=hexcolor, end_color=hexcolor, fill_type="solid")


def pct(n, total):
    return f"{(100.0 * n / total) if total else 0.0:.1f}%"


def build_bug_level_tab(wb, sheet_name, records, pre_key, post_key, pre_header, post_header):
    ws = wb.create_sheet(sheet_name)
    ws.append(["Project", "Bug ID", "URL", pre_header, post_header, "Note"])
    style_header(ws, 1, 6)
    sorted_records = sorted(records, key=lambda r: (r["project"], r["bug_id"]))
    for r in sorted_records:
        row = ws.max_row + 1
        ws.cell(row=row, column=1, value=r["project"])
        ws.cell(row=row, column=2, value=r["bug_id"])
        set_url_cell(ws, row, 3, r["url"])
        pre_v = r[pre_key] or "—"
        post_v = r[post_key] or "—"
        ws.cell(row=row, column=4, value=pre_v)
        ws.cell(row=row, column=5, value=post_v)
        if pre_v != post_v:
            for c in range(1, 6):
                ws.cell(row=row, column=c).fill = HIGHLIGHT
    widths = [10, 8, 45, 24, 24, 30]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w


def write_distribution_block(ws, title, records, key_pre, key_post, names, first_col_header):
    ws.append([title])
    ws.cell(row=ws.max_row, column=1).font = TITLE_FONT
    ws.append([first_col_header, "Pre-fix Count", "Pre-fix %", "Post-fix Count", "Post-fix %"])
    style_header(ws, ws.max_row, 5)
    total = len(records)
    counts_pre = Counter(r[key_pre] for r in records if r[key_pre] in names)
    counts_post = Counter(r[key_post] for r in records if r[key_post] in names)
    max_count = max(list(counts_pre.values()) + list(counts_post.values()) + [0])
    for name in names:
        pre_n = counts_pre.get(name, 0)
        post_n = counts_post.get(name, 0)
        ws.append([name, pre_n, pct(pre_n, total), post_n, pct(post_n, total)])
        row = ws.max_row
        fp = heat_fill(pre_n, max_count)
        if fp:
            ws.cell(row=row, column=3).fill = fp
        fq = heat_fill(post_n, max_count)
        if fq:
            ws.cell(row=row, column=5).fill = fq
    total_pre = sum(counts_pre.values())
    total_post = sum(counts_post.values())
    ws.append(["Total", total_pre, pct(total_pre, total), total_post, pct(total_post, total)])
    for c in range(1, 6):
        ws.cell(row=ws.max_row, column=c).font = TITLE_FONT
    ws.append([])


def build_distribution_tab(wb, sheet_name, records, key_pre, key_post, names, label):
    ws = wb.create_sheet(sheet_name)
    ws.append([
        f"{label} Distribution: Pre-fix and Post-fix counts and percentages "
        f"per category, pooled across all projects and then per project below."
    ])
    ws.cell(row=1, column=1).font = TITLE_FONT
    ws.append([])
    write_distribution_block(ws, "All Projects", records, key_pre, key_post, names, label)
    for project, _, _ in PROJECTS:
        proj_records = [r for r in records if r["project"] == project]
        write_distribution_block(ws, project, proj_records, key_pre, key_post, names, label)
    widths = [24, 14, 14, 14, 14]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w


def write_confusion_block(ws, title, records, key_pre, key_post, names):
    ws.append([title])
    ws.cell(row=ws.max_row, column=1).font = TITLE_FONT
    ws.append(["Pre-fix \\ Post-fix"] + list(names))
    style_header(ws, ws.max_row, len(names) + 1)
    matrix = {p: Counter() for p in names}
    for r in records:
        p, q = r[key_pre], r[key_post]
        if p in matrix and q in names:
            matrix[p][q] += 1
    max_count = max((v for row in matrix.values() for v in row.values()), default=0)
    for p in names:
        row_vals = [matrix[p].get(q, 0) for q in names]
        ws.append([p] + row_vals)
        row_idx = ws.max_row
        for j, v in enumerate(row_vals, start=2):
            f = heat_fill(v, max_count)
            if f:
                ws.cell(row=row_idx, column=j).fill = f
    ws.append([])


def build_drift_tab(wb, sheet_name, records, key_pre, key_post, names, label):
    ws = wb.create_sheet(sheet_name)
    ws.append([
        f"{label} Drift Matrix: rows are Pre-fix {label.lower()}, columns are "
        f"Post-fix {label.lower()}, each cell is a bug count. Pooled across all "
        f"projects, then per project below."
    ])
    ws.cell(row=1, column=1).font = TITLE_FONT
    ws.append([])
    write_confusion_block(ws, "All Projects", records, key_pre, key_post, names)
    for project, _, _ in PROJECTS:
        proj_records = [r for r in records if r["project"] == project]
        write_confusion_block(ws, project, proj_records, key_pre, key_post, names)
    ws.column_dimensions["A"].width = 26
    for i in range(2, len(names) + 2):
        ws.column_dimensions[get_column_letter(i)].width = 16


def load_records():
    records = []
    for project, slug, expected in PROJECTS:
        manifest = json.loads((REPO_ROOT / f".dist/study/{slug}.json").read_text())
        bug_ids = sorted({e["bug_id"] for e in manifest["entries"]})
        assert len(bug_ids) == expected, f"{project}: expected {expected} bugs, got {len(bug_ids)}"
        for b in bug_ids:
            pre = load_classification(project, b, "prefix", CONDITION_TAG)
            post = load_classification(project, b, "postfix", CONDITION_TAG)
            assert pre is not None and post is not None, f"{project}-{b}: missing {CONDITION_TAG} classification"
            url = load_bug_url(project, b)
            records.append({
                "project": project,
                "bug_id": b,
                "url": url,
                "pre_type": pre.get("odc_type"),
                "post_type": post.get("odc_type"),
            })
    return records


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else f".dist/study/combined_report.{CONDITION_TAG}.xlsx"
    records = load_records()

    type_names = list(ODC_TYPE_NAMES) + [OTHER_TYPE_NAME]

    wb = Workbook()
    wb.remove(wb.active)

    build_bug_level_tab(wb, "Defect Types", records, "pre_type", "post_type",
                         "Bug Type (Pre-fix)", "Bug Type (Post-fix)")
    build_distribution_tab(wb, "Type Distribution", records, "pre_type", "post_type",
                            type_names, "ODC Type")
    build_drift_tab(wb, "Type Drift", records, "pre_type", "post_type",
                     type_names, "Type")

    out_file = REPO_ROOT / out_path
    out_file.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out_file)
    print(f"wrote {out_file}: {len(records)} bugs across {len(PROJECTS)} projects")


if __name__ == "__main__":
    main()
