# Defence maths — verification and study guide

Everything numerical in the defence book (`latex/defence book/main.tex`), checked and explained, so the team
can defend every formula and value.

**Date:** 2026-09-15 · **Corpus:** 410 bugs (`.dist/study/artifacts_v2`), plus the thirteen manually analysed
bugs for the cross-model analysis.

## Read in this order

| Doc | What it gives you |
| --- | --- |
| [`01_verification_report.md`](01_verification_report.md) | **Start here.** Every number in the book, how it was checked, and its status. The "Issues found" table lists the eight things to fix or be ready for. |
| [`02_cohens_kappa.md`](02_cohens_kappa.md) | Cohen's κ: the formula, where the pipeline computes it, a worked example, why κ instead of raw agreement. |
| [`03_agreement_metrics.md`](03_agreement_metrics.md) | The four tiers, why Tiers 2–3 need conditional reading, near misses, drift, the agreement ceiling, post-fix consensus, "reproducible". |
| [`04_statistical_tests.md`](04_statistical_tests.md) | Permutation χ² and Cramér's V, rule of three, bootstrap intervals, paired bootstrap on Δκ, McNemar, sign test. |
| [`05_distribution_metrics.md`](05_distribution_metrics.md) | Type shares, total variation distance (with worked sums), entropy, vocabulary reduction ratio. |

## Bottom line

- **Corpus results:** every Chapter 6 number was recomputed from the raw classification files and matches the
  book (bootstrap and permutation values are Monte Carlo estimates and match at the book's precision).
- **Pipeline settings** quoted in Chapters 4–5 match the code.
- **Literature numbers:** Henningsson & Wohlin, Rahman & Farhana, and Agnelo et al. were checked against their
  PDFs and are correct, with two wording caveats. KnowBug, Hernández-González et al., the 77–82% prior-accuracy
  figure, and the sizes of the three prior Defects4J studies were not re-checked.
- **Book edits applied (2026-09-15):** the Landis–Koch label (Issue #1) and the near-miss wording (Issue #8).
  The one-week collection time (Issue #5) was confirmed as correct for the 410-bug re-collection.

## Reproduce

```
python scripts/analysis/recompute_rq_statistics.py six
```

Runs from the repo root with the project venv; prints every RQ figure for all six projects (`closure` and
`five` give the sub-scopes).
