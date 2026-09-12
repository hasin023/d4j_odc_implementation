# Excel report specifications

Two report shapes exist. One has a script in the repo; the other does not and must be rebuilt from
the spec below if it is ever needed again.

> ⚠️ **Impact was removed from the pipeline on 2026-09-10.** Any tab or block below that reports
> Impact describes reports built *before* that date. Those parts are **no longer producible** —
> `classification.*.json` written after 2026-09-10 has no `impact` field. They are recorded here so
> the six committed workbooks in `.dist/study/` remain interpretable, not as a build target.

---

## A. Cross-project workbook — script exists

**Script:** `scripts/reports/generate_combined_report.py`
**Output:** `.dist/study/combined_report.scientific-open.xlsx`
**Scope:** the six full-project manifests — Chart 26, Closure 174, Lang 61, Math 106, Mockito 38,
Time 26 = 431 bugs. Condition `scientific-open` only.

Three sheets:

1. **Defect Types** — `Project | Bug ID | URL | Bug Type (Pre-fix) | Bug Type (Post-fix) | Note`.
   URL is a real clickable hyperlink. The whole row is highlighted where pre ≠ post.
2. **Type Distribution** — counts and percentages over all 7 ODC types plus `Other`, pooled across
   projects first, then one block per project. Percentage columns carry a white→orange heat
   gradient; raw counts do not.
3. **Type Drift** — pre × post confusion matrix, same pooled-then-per-project layout.

It hard-asserts that every expected bug has both classifications and stops at the first gap. Edit
`ARTIFACTS_ROOT` near the top of the file to point at whichever corpus you mean.

The committed workbook from 2026-07-26 has **six** sheets — the three above plus Impacts, Impact
Distribution and Impact Drift. Re-running the script today produces three and overwrites the file,
so write to a new name if the old one still matters.

---

## B. Per-project workbook — script lost, rebuild from this spec

The six `*_report.xlsx` files in `.dist/study/` (`lang61`, `chart26`, `time26`, `mockito38`,
`math106`, `closure174`) were produced by a generator that lived in a scratchpad and was lost twice
to resets. This section is the authoritative record of what it built.

Data source: `classification.<tag>.json` for one project, both evidence modes.

### Tab 1 — "Defect Types"

`Project | Bug ID | URL | Bug Type (Pre-fix) | Bug Type (Post-fix)`, `scientific-open` only. The
condition name never appears in the sheet. URL must be a **real clickable hyperlink**, not text.
Highlight the whole row where pre-fix type ≠ post-fix type. Compute the drifted set live from the
data; never hardcode it. (For Lang-61 this was 8 of 61: Lang-21, 26, 29, 34, 43, 53, 60, 61.)

### Tab 2 — "Impacts" *(no longer producible)*

Same shape as Tab 1 with `Impact (Pre-fix)` / `Impact (Post-fix)` instead of type. Row highlighted
where impact drifted. For Lang-61 that was 3 of 61: Lang-35, 56, 65.

### Tab 3 — "Analysis"

Three blocks stacked on one sheet:

- **Block A — Defect Type distribution.** All 7 ODC types plus `Other`, listed even at zero count.
  Count and percentage for both pre-fix and post-fix.
- **Block B — Impact distribution** *(no longer producible)*. All 13 v5.2 categories, listed even at
  zero, same count-and-percentage treatment.
- **Block C — drift rationale.** One row per type-drifted bug (the same set as Tab 1), each with a
  one- to two-sentence rationale **sourced from that bug's own `reasoning_summary` field** in
  `classification.scientific-open.json`, comparing pre-fix against post-fix.

  The rationale must be traceable to a field the model actually populated. Do not synthesise it.

- **There is deliberately no Block D for Impact drift rationale.** It was built once and removed at
  the user's request: Impact has no per-bug justification field in the pipeline, unlike Type which
  has `reasoning_summary` and `alternative_types`. Any "rationale" for an Impact-only drift would be
  inference from how the surrounding type reasoning happens to be phrased, not something grounded in
  the data. Do not re-add it. (Moot since 2026-09-10 anyway.)

### Tab 4 — "Ablation Study"

Conditions shown: **Scientific, Few, Zero** — labels carry no `open`/`closed`/`free` suffix, because
closed variants are not shown in this tab and the suffix would be noise.

Columns: `Bug ID (merged across 2 rows) | Metric | Scientific: Prefix, Postfix | Few: Prefix,
Postfix | Zero: Prefix, Postfix`.

Each bug occupies **two physical rows** — a `Type` row and an `Impact` row — with the Bug ID cell
vertically merged across both. Zero's Impact cells are always empty (an em-dash), never zero, since
`zero-free` never populated impact. *(With Impact gone, this tab is now a single Type row per bug.)*

**Highlighting rule** — the part that took the most iterations to settle:

- Compare **Scientific vs Few only**. Zero is excluded: its labels are free text and therefore
  near-guaranteed to differ, so any mismatch signal from it is meaningless.
- The comparison unit is the **whole `(Prefix, Postfix)` tuple**, not each cell independently. If
  `(Sci-Prefix, Sci-Postfix) != (Few-Prefix, Few-Postfix)`, highlight **all four cells** — both
  conditions, both evidence modes — together. Not just the cell that differs.
- The Type row and the Impact row are judged **completely independently**. A bug can have Type
  highlighted with Impact clean, or the reverse, or both, or neither.

---

## Practical notes

- `openpyxl>=3.1` is in `requirements.txt`. Nothing needs pandas.
- Run generators from the repo root. `generate_combined_report.py` inserts the repo root on
  `sys.path` itself, so it needs no `PYTHONPATH`. A script that does **not** do that will fail to
  import `d4j_odc_pipeline` when invoked as a file path, because Python puts the *script's own*
  directory on `sys.path` rather than the working directory — set `PYTHONPATH=<repo-root>` in that
  case.
- Relative output paths passed to `generate_combined_report.py` resolve against the **repo root**,
  not your current directory.
- Before building any report, run `python scripts/check_contexts.py <manifest> <artifacts-root>`.
  The generators assert on missing data and die at the first gap.
- Worth reusing: the original spec was agreed via a plain-text mockup (markdown tables with a marker
  standing in for cell fill) before any file was generated. Cheaper than building the wrong workbook.
