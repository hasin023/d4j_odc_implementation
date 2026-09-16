# Cohen's κ — how it is computed, where it is used, and how to defend it

**Date:** 2026-09-15 · **Scope:** the defence book (`latex/defence book/main.tex`), 410-bug `artifacts_v2` corpus

Short answer: **yes, Cohen's κ is really computed by the pipeline, the formula in the book is exactly the
one implemented, and the numbers in the book match the stored analysis outputs and a hand recomputation.**

---

## 1. The formula, and where it lives in the code

The book (§4.9, Evaluation Framework, Tier 4) states:

```
κ = (p_o − p_e) / (1 − p_e)
```

- **p_o** — observed agreement: the share of bugs whose two labels are identical.
- **p_e** — agreement expected by chance: for each ODC type, (share of bugs with that type in the first
  classification) × (share with that type in the second), summed over all types.

Implementation: `d4j_odc_pipeline/comparison.py` → `compute_cohens_kappa(pairs)`. It builds the
contingency matrix over the union of labels, computes `observed` (diagonal / n) and `expected`
(Σ row-marginal × column-marginal), and returns `(observed − expected) / (1 − expected)`. It returns
`None` for fewer than 2 pairs.

## 2. Where the pipeline calls it

| Caller | What it computes | Output |
| --- | --- | --- |
| `batch.py` (the `study-drift` command) | κ over every bug's (pre-fix label, post-fix label) pair, plus `compute_per_project_kappa` | `cohens_kappa`, `per_project_kappa` in `analysis.<tag>.json` |
| `comparison.py::batch_compare` | κ for a batch of comparisons (`compare-batch`) | batch comparison report |
| `analysis.py` (`study-escape`) | κ between the closed and open taxonomy passes | `cohens_kappa_8cat`, `cohens_kappa_non_escaped` |
| `results_export.py` | per-project κ LaTeX table | `per_project_kappa.tex` |

Stored results for the defence corpus (`.dist/study/reports/artifacts_v2/analysis/`):

| File | `cohens_kappa` | Book value |
| --- | --- | --- |
| `analysis.scientific-open.json` | 0.50461 | **0.505** |
| `analysis.few-open.json` | 0.38944 | **0.389** |

## 3. Worked example (recomputed by hand from the 410 classification files)

| Condition | p_o (observed) | p_e (chance) | κ (hand) | κ (pipeline) |
| --- | --- | --- | --- | --- |
| scientific-open | 0.7024 | 0.3993 | 0.5046 | 0.5046 |
| few-open | 0.6659 | 0.4527 | 0.3894 | 0.3894 |

Marginals that drive p_e (top three types):

| Condition | Pre-fix | Post-fix |
| --- | --- | --- |
| scientific-open | Checking 198, Algorithm/Method 175, Assignment 28 | Checking 192, Algorithm/Method 160, Assignment 37 |
| few-open | **Algorithm/Method 265**, Checking 119, Assignment 11 | Algorithm/Method 218, Checking 151, Assignment 28 |

**One sentence for the panel:** *"κ = 0.505 means the pre-fix and post-fix labels agree on 70% of bugs
where chance alone would give 40%, so we capture about half of the agreement that isn't explained by the
label distribution."* — that is (0.702 − 0.399) / (1 − 0.399).

## 4. Where κ appears in the defence book

| Place | What is compared | Value(s) |
| --- | --- | --- |
| §4.9 Evaluation Framework | Defined as Tier 4 of the four-tier framework, with the formula | — |
| RQ3, Tier 4 | Pre-fix vs post-fix label of each bug | scientific 0.505 [0.433, 0.574]; few-shot 0.389 [0.310, 0.468] |
| RQ3, agreement ceiling | Scientific vs few-shot, both with the fix / both without | 0.614 / 0.451 |
| RQ4a | Free-form (`zero-free`) label, pre-fix vs post-fix | 0.150 |
| RQ4b, primary test | Difference in κ between scientific and few-shot, paired bootstrap | Δκ = 0.115, CI [0.026, 0.208], p ≈ 0.012 |
| RQ4b, per-project pattern | κ per project for each strategy; sign test on which is higher | 6 of 6 projects, one-sided p = 0.016 |
| §2.5 Human agreement | Human κ from other studies (cited, **not computed by us**) | 0.16 (descriptions only), 0.93 (code and change) |

(Per-project reliability as its own RQ3 analysis was removed from the book on 2026-09-15; the
per-project κ values are still used inside RQ4b.)

## 5. Why κ and not just raw agreement — the defence argument

Raw agreement is inflated when a classifier concentrates its labels on one type. Few-shot labels
**265 of 410** bugs Algorithm/Method in pre-fix mode, so two of its classifications agree often by chance
alone: its **p_e = 0.453**, against 0.399 for scientific.

| Measure | scientific-open | few-open | Difference | Significant? |
| --- | --- | --- | --- | --- |
| Raw agreement (strict match) | 70.2% | 66.6% | +3.7 pts | No — McNemar p = 0.221 |
| Cohen's κ | 0.505 | 0.389 | +0.115 | Yes — paired bootstrap CI [0.026, 0.208], p ≈ 0.012 |

κ separates real agreement from agreement produced by a label bias. That is why it is Tier 4 of the
framework and the primary measure for RQ4b. Both tests are reported in the book, with this explanation of
why they differ.

## 6. Questions to be ready for

1. **"Is this inter-rater agreement?"** Not human inter-rater agreement. Our κ compares two
   classifications produced by the same model (pre-fix vs post-fix, or scientific vs few-shot). The
   Landis–Koch scale (0.21–0.40 fair, 0.41–0.60 moderate, ≥ 0.61 substantial) is a conventional reference
   borrowed from inter-rater studies, and the book uses it only as a reference scale.
2. **"Why is the free-form κ so low (0.150)?"** It compares free-form label *strings* exactly, so two
   phrasings of the same idea count as disagreement. That is the point RQ4a makes — free-form labels cannot
   be aggregated — but call it "string-level agreement" if asked.
3. **"κ 0.505 is only moderate."** Correct, and the book says so. Context: with the fix visible to both,
   scientific and few-shot agree only at κ = 0.614, so a large part of the remaining disagreement is
   ambiguity in the classification task itself.
4. **"How do you know your κ implementation is right?"** Hand recomputation from the raw classification
   files (Section 3) reproduces the pipeline to four decimals. **Gap:** the unit tests
   (`tests/test_batch.py`, `tests/test_open_taxonomy.py`) only assert that κ is produced, not its numeric
   value — a small test against a textbook example would close this.

## 7. Reproduce the check

```
python -c "from d4j_odc_pipeline.comparison import compute_cohens_kappa; print(compute_cohens_kappa([('A','A'),('A','B'),('B','B'),('B','B')]))"
```

For every κ in the book (including bootstrap intervals and Δκ), run
`python scripts/analysis/recompute_rq_statistics.py six`. Alternatively, read `cohens_kappa` from
`.dist/study/reports/artifacts_v2/analysis/analysis.scientific-open.json` and `analysis.few-open.json`,
or re-run `study-drift` for the condition against `--artifacts-root .dist/study/artifacts_v2`.
