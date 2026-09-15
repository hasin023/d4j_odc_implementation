# Verification report — every number and formula in the defence book

**Date:** 2026-09-15 · **Checked against:** `latex/defence book/main.tex` as of this date

**How each item was checked**

- **Recomputed** — recomputed from the raw `classification.*.json` files in `.dist/study/artifacts_v2`
  (and `artifacts_full` for `zero-free`) with `scripts/analysis/recompute_rq_statistics.py` or a one-off
  check, and compared to the book.
- **Code** — read from the pipeline source.
- **Source** — checked against the cited paper's PDF.
- **Arithmetic** — derived from other verified numbers.

**Status:** ✅ verified · ⚠️ verified with a caveat or wording issue · ❓ not verified in this session

---

## Issues found (read these first)

| # | Where in the book | Issue | Suggested fix |
| --- | --- | --- | --- |
| 1 | §2.5 Human Agreement, sentence after Table 2.3 | "On the Landis–Koch scale, this is a range from **poor** to almost perfect". On Landis–Koch, κ = 0.16 is **"slight"**. Henningsson & Wohlin call it "poor" on **Altman's** scale. | **Fixed 2026-09-15:** now reads "from slight to almost perfect" |
| 2 | §2.5 Table 2.3, Rahman & Farhana row | Numbers are correct, but their categories are COVID-software bug categories, **not ODC types**; the 95.1% / κ 0.93 figure comes from their closed-coding step. The table caption says "ODC-style". | Acceptable as "defect classification"; be ready to say it is not ODC |
| 3 | §2.5 Table 2.3, Agnelo et al. (NoSQL) row | κ = 0.93 is correct, but it comes from a **verification** procedure (a second researcher checking the first researcher's classification), not independent blind labelling. | Be ready to say so if asked |
| 4 | RQ4b, Time's few-shot κ interval [−0.138, 0.530] | Bootstrap endpoints move between runs (re-runs gave [−0.145, 0.549], [−0.175, 0.558]). The conclusion — the interval includes zero — holds in every run. | Fine as is; say "Monte Carlo estimate" if asked |
| 5 | §5.3 Data Collection | Says the "410 pre-fix and 410 post-fix" corpus took "approximately one week" to collect. The team confirmed the 410-bug re-collection also took about one week. | **Confirmed by the team:** the re-collection of the 410 bugs also took about one week; no change needed |
| 6 | §4.8 Validation | "Transient HTTP errors (429, 500, 502, 503) are retried with exponential backoff." 500/502/503 are always retried; **429 is retried only when no other API key is available** (otherwise the pipeline switches keys). | Fine as a summary |
| 7 | Reproducibility | The Chapter 6 statistics were computed by a script that lived only in `/tmp`. | **Fixed:** saved as `scripts/analysis/recompute_rq_statistics.py` (reproduces the book's values exactly) |
| 8 | RQ3 severity table (Table 6.7), the "further 27.3%" sentence, and the Closure near-miss sentence | **Wording does not match the metric.** The book says "reference label already among the **pre-fix** alternatives" (90.2% / 95.6%; Closure 96.3%). The pipeline's top-2 match counts **either direction**: the post-fix label is among the pre-fix alternatives, *or* the pre-fix label is among the post-fix alternatives. Counting only the stated direction gives **77.0% / 80.3%; Closure 88.9%**. The "unrelated" count (10 bugs, 2.4%) also uses the either-direction definition. | **Fixed 2026-09-15:** wording changed to "one label among the other classification's alternatives" in the table row, the 27.3% sentence, the Closure sentence, and the §1.2 tier definition; numbers unchanged |

---

## Abstract and Chapter 1

| Claim | Value | How checked | Status |
| --- | --- | --- | --- |
| Corpus | 410 bugs, 6 projects | Recomputed | ✅ |
| Classifications | 1,640 = 410 × 2 conditions × 2 modes | Arithmetic | ✅ |
| Three types cover | 97.8% (401 of 410) | Recomputed | ✅ |
| Escape upper bound | 0.2% (3 / 1,640) | Arithmetic | ✅ |
| Pre-fix reproduces reference | 70.2%, κ = 0.505 | Recomputed | ✅ |
| Unrelated labels | 2.4% (10 of 410) | Recomputed | ✅ |
| "Roughly 30%" labels change | 29.8% | Recomputed | ✅ |
| "80%" stay in three types | 80.3% (98 of 122) | Recomputed | ✅ |
| Prior work sizes | 488 (Van der Spuy), 395 (Sobreira), 50 (Jiang) | — | ❓ taken from the cited papers, not re-opened this session |

## Chapter 2 — Related Works

| Claim | Value | How checked | Status |
| --- | --- | --- | --- |
| Earlier SVM / Naive Bayes ODC systems | 77–82% accuracy | — | ❓ not re-verified (Huang 2015, Thung 2012) |
| KnowBug label-definition gains | TensorFlow 26.44→33.17%, MXNET 29.08→41.39%, PaddlePaddle 17.81→31.14% | — | ❓ paywalled; not re-verified |
| Henningsson & Wohlin study size | 8 raters, 30 faults | Source | ✅ |
| Mean pairwise κ | 0.16; 0.24 after merging the two most-confused classes | Source | ✅ |
| "Poor" label | Their text: "poor according to Table 3" (Altman's scale); book now says "slight" on Landis–Koch | Source | ✅ (fixed, Issue #1) |
| Most-confused pair | Assignment–Algorithm; "22 of the 28 pairs" (rater pairs) | Source | ✅ |
| Confusion occasions | AS–AL 184, IN–AL 77, CH–AL 68, AS–IN 59, AS–CH 49 | Source | ✅ |
| Hernández-González et al. | Majority reached on 481/962 and 394/675 defects | — | ❓ paywalled; not re-verified |
| Rahman & Farhana | 72.7%, κ 0.70 (open coding); 95.1%, κ 0.93 (closed coding) | Source | ⚠️ Issue #2 |
| Agnelo et al. (NoSQL ODC) | κ 0.93 for Defect Type | Source | ⚠️ Issue #3 |
| Landis–Koch bands | 0.21–0.40 fair, 0.41–0.60 moderate, ≥ 0.61 substantial | Standard (Landis & Koch 1977) | ✅ |
| ODC Impact values | 13 values | IBM ODC v5.2 (`docs/odc_doc.md`) | ✅ |

## Chapter 4 — Methodology

| Claim | Value | How checked | Status |
| --- | --- | --- | --- |
| Production snippet window | ±12 lines | Code: `pipeline.py` `snippet_radius = 12` | ✅ |
| Test snippet window | ±18 lines | Code: `radius = snippet_radius + 6` | ✅ |
| Test snippets | first 3 failing tests | Code: `failures[:3]` | ✅ |
| Loop turn limit | 6 | Code: `agent.py` `AGENT_MAX_TURNS = 6` | ✅ |
| Probe payload truncation | 2,000 characters | Code: `OBSERVATION_MAX_CHARS = 2000` | ✅ |
| Worked examples / decision questions | 5 / 7 | Code: `prompting.py` | ✅ |
| Evidence probes (Table 4.x, added 2026-09-15) | 5: list_evidence, full_stack_trace, snippet, coverage, bug_report | Code: `agent.py` `PROBE_NAMES`, `execute_probe` | ✅ |
| Retried HTTP codes | 429, 500, 502, 503 | Code: `llm.py` | ⚠️ Issue #6 |
| κ formula | (p_o − p_e) / (1 − p_e) | Code: `comparison.py` | ✅ (see `02_cohens_kappa.md`) |
| Tiers 2–3 chance level | > 90% under random shuffling | Recomputed (92.5% / 92.9%) | ✅ |
| Human-review flags | 16 pre-fix, 0 post-fix | Recomputed | ✅ |
| Strategies agree more post-fix, every project | 6 of 6 | Recomputed | ✅ |

## Chapter 5 — Experimental Design

| Claim | Value | How checked | Status |
| --- | --- | --- | --- |
| Defects4J table total | 836 | Arithmetic (sum of 17 rows) | ✅ |
| Study corpus | Chart 26, Closure 153, Lang 61, Math 106, Mockito 38, Time 26 = 410 | Recomputed | ✅ |
| Closure coverage | 153 of 174 | Recomputed + table | ✅ |
| Workbook cross-check | 612 Closure labels, 0 mismatches | Recomputed | ✅ |
| Collection time | "approximately one week" | Team confirmation | ✅ |
| Vocabulary reduction formula | 1 − k/u | Code: `analysis.py` | ✅ |

## Chapter 6 — RQ1

| Claim | Value | How checked | Status |
| --- | --- | --- | --- |
| Distribution table (all four runs) | e.g. sci pre-fix CHK 198, ALG 175, ASN 28, REL 5, FCO 3, INT 1 | Recomputed | ✅ |
| Shares | 48.3%, 42.7%, 6.8% | Arithmetic | ✅ |
| Timing/Serialization | 0 in 1,640 | Recomputed | ✅ |
| Per-project table | Closure 69/77/2/5, etc. | Recomputed | ✅ |
| Closure Assignment share | 2/153 = 1.3% vs 26/257 = 10.1% | Arithmetic | ✅ |
| χ² (scientific) | 36.11, dof 25, p = 0.096, V = 0.133 | Recomputed | ✅ |
| χ² (few-shot) | 49.48, dof 25, p = 0.010, V = 0.155 | Recomputed | ✅ |
| Five projects without Closure | p = 0.381 | Recomputed | ✅ |
| TVD sci vs few, pre-fix | 0.23 | Recomputed (0.234) | ✅ |
| TVD sci pre vs post | 0.05 | Recomputed (0.051) | ✅ |

## Chapter 6 — RQ2

| Claim | Value | How checked | Status |
| --- | --- | --- | --- |
| "Other" as primary | 0 / 1,640 | Recomputed | ✅ |
| "Other" as alternative | 1 | Recomputed | ✅ |
| Justification fields filled | 0 | Recomputed | ✅ |
| Types used | 6 of 7 | Recomputed | ✅ |
| Closure classifications | 612, no escapes | Recomputed | ✅ |
| Rule-of-three bounds | 0.7% (n = 410), 0.2% (n = 1,640) | Arithmetic; exact bound 0.73% / 0.18% | ✅ |
| Rare types | REL 28, FCO 17, INT 13 | Recomputed | ✅ |
| Free-form labels | 366 | Recomputed | ✅ |

## Chapter 6 — RQ3

| Claim | Value | How checked | Status |
| --- | --- | --- | --- |
| Tier 1 strict | 70.2% [65.6, 74.9] / few 66.6% [62.0, 71.2] | Recomputed | ✅ |
| Tier 2 top-2 | 97.1% / 98.5% | Recomputed | ✅ |
| Tier 3 family | 94.1% / 95.6% | Recomputed | ✅ |
| Tier 4 κ | 0.505 [0.433, 0.574] / 0.389 [0.310, 0.468] | Recomputed | ✅ |
| Shuffle baseline | 92.5% top-2, 92.9% family | Recomputed | ✅ |
| Conditional severity | 90.2 / 80.3 / 10 bugs (sci); 95.6 / 86.9 / 2 bugs (few) | Recomputed | ✅ (wording fixed, Issue #8) |
| "Further 27.3%" | (410 − 288 − 10) / 410 | Arithmetic | ✅ |
| Closure near misses | 96.3%, 88.9%, 1 unrelated (Closure_171) | Recomputed | ✅ (wording fixed, Issue #8) |
| Ceiling | 76.3% (κ 0.614) with fix; 68.0% (κ 0.451) without | Recomputed | ✅ |
| "About six points" | 76.3 − 70.2 = 6.1 | Arithmetic | ✅ |
| Drift rates | 122 (29.8%) / 137 (33.4%); five projects 26.5%, Closure 35.3% | Recomputed | ✅ |
| TVD pre vs post | 0.051 / 0.129 | Recomputed | ✅ |
| Drift pairs | ALG–CHK 75 (38/37), ALG–ASN 12 (10/2), CHK–ASN 11 (8/3) | Recomputed | ✅ |
| Triangle share; Alg–Chk share | 98/122 = 80.3%; 75/122 = 61% | Arithmetic | ✅ |
| Closure boundary | 43 of 54 drifts | Recomputed | ✅ |
| Alg/Method partner by project | Checking (Closure, Lang, Math, Time), Assignment (Chart), spread (Mockito) | Recomputed (drifts pooled across both strategies) | ✅ |
| Confidence examples | flagged at 0.9 (e.g. Chart_26); four probes and confidence 1.0 (Chart_11) | Recomputed | ✅ |
| Severe-drift shares | 8.2% (10/122) vs 1.5% (2/137) | Arithmetic | ✅ |

## Chapter 6 — RQ4

| Claim | Value | How checked | Status |
| --- | --- | --- | --- |
| RQ4a ladder | 366 / 8.376 / 15.1% / 0.150; 6 / 1.291 / 66.6% / 0.389; 6 / 1.446 / 70.2% / 0.505 | Recomputed | ✅ |
| Singletons, top label | 342; "Null Pointer Dereference" 15 | Recomputed | ✅ |
| Vocabulary reduction | 0.981 = 1 − 7/366 | Arithmetic | ✅ |
| Closure free-form reproducibility | 9.2% | Recomputed | ✅ |
| McNemar vs zero-free | 223/18, p = 3.8e-46; 204/14, p = 2.1e-44 | Recomputed | ✅ |
| RQ4b table | 66.6/70.2; 0.389/0.505; consensus 313: 71.6/74.8; 6 of 6; lowest 0.212 (Time) / 0.359 (Closure); sd 0.130/0.108 | Recomputed | ✅ |
| Paired bootstrap | Δκ = 0.115 [0.026, 0.208], p ≈ 0.012 | Recomputed | ✅ |
| Sign test | 6 of 6, one-sided p = 1/64 = 0.016 | Arithmetic | ✅ |
| McNemar raw | 73 vs 58, p = 0.221 | Recomputed | ✅ |
| McNemar consensus | 43 vs 33, p = 0.302 | Recomputed | ✅ |
| Closure paired bootstrap | Δκ = 0.065 [−0.108, 0.237]; both 64.7% | Recomputed | ✅ |
| Few-shot Algorithm/Method | 265 of 410 | Recomputed | ✅ |
| Per-project κ gains | Chart +0.323, Time +0.268, Mockito +0.227, Math +0.066, Closure +0.065, Lang +0.049 | Recomputed | ✅ |
| Time intervals | few [−0.138, 0.530]; sci κ 0.480 | Recomputed | ⚠️ Issue #4 |
| Probe usage | 37 pre / 126 post zero-probe runs; 125 of 410 in store; 13 of 153 Closure; 64 retrieved | Recomputed | ✅ |
| Agreement by probe count | 86.5% (37), 69.1% (136), 63.8% (127), 73.6% (110) | Recomputed | ✅ |
| Mockito / Lang coverage | 0% / ~98% in store | Recomputed | ✅ |

## Chapter 6 — Qualitative and cross-model analyses

| Claim | Value | How checked | Status |
| --- | --- | --- | --- |
| Thirteen-bug labels (Table 6.14) | all four Gemini labels per bug | Recomputed + workbook | ✅ |
| Chart_9 retrieved the modified class | yes | Recomputed | ✅ |
| Chart_17, Math_90 | Checking, confidence 1.0, 1 turn, 0 probes, both modes | Recomputed | ✅ |
| Chart_11 | 5 turns, 4 probes, confidence 1.0 | Recomputed | ✅ |
| Mockito_26 | 4 pre-fix probes | Recomputed | ✅ |
| Manual reading scores | Gemini 6/4/6/11; gpt-5-mini 6/4/11/12 | Recomputed + workbook | ✅ |
| Cross-model behaviour table | drifts 8/5, 9/8; probes 1.7/0.6 vs 3.0/1.9; turn limit 0 vs 4 | Recomputed | ✅ |
| Shared correct sci pre-fix labels | 3 of 6 | Recomputed | ✅ |
| Same label across models | 10/13 few, 7/13 scientific | Recomputed | ✅ |
| gpt-5-mini confidence omitted | 18 of 52 | Recomputed (raw responses) | ✅ |
| Reasoning-effort pilot | default 3 vs high 2 of 4 | Workbook only (hand-entered pilot) | ⚠️ not backed by stored artifacts |

---

## How to re-run the checks

```
python scripts/analysis/recompute_rq_statistics.py six
python scripts/analysis/recompute_rq_statistics.py closure
python scripts/analysis/recompute_rq_statistics.py five
```

The cited PDFs used for the source checks: Henningsson & Wohlin (`https://www.wohlin.eu/isese04.pdf`),
Rahman & Farhana (`https://arxiv.org/pdf/2006.00586`), Agnelo et al. preprint
(`https://eden.dei.uc.pt/~cnl/papers/2020-jss-odc-joao-v64-submitted.pdf`).
