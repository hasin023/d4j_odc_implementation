# RQ Standing Assessment — plain-language version

**Date:** 2026-09-15, evening revision — **now includes Closure (153 bugs)**. Supersedes the
morning version of the same day, which covered only the five smaller projects (257 bugs).

This document answers one question: **for each of our five research questions, do we have enough
data to defend it in front of faculty and reviewers, and what exactly should we say?**

Every RQ below is written in the same six parts:

1. **What the RQ asks** — in plain words.
2. **What we did** — the experiment behind it.
3. **What we found** — the numbers.
4. **What the statistics say** — the tests, and what they mean.
5. **How to explain it to faculty** — the argument, including the likely attack and the answer.
6. **What we can claim / what we cannot claim** — the exact boundary.

Headline numbers are for **all six projects (410 bugs)**. Where Closure moves a number, the
five-project figure (257 bugs) is shown next to it so the change is visible, not hidden.

---

## The data behind everything in this document

| Thing | Value |
| --- | --- |
| Bugs | **410** — Chart 26, **Closure 153**, Lang 61, Math 106, Mockito 38, Time 26 |
| Main dataset | `.dist/study/artifacts_v2/` |
| Conditions in the main dataset | `scientific-open` and `few-open` |
| Evidence modes | **pre-fix** (buggy code + failing tests only) and **post-fix** (same, plus the developer's real fix diff) |
| Total classifications | 2 conditions × 2 modes × 410 bugs = **1,640** (1,028 before Closure) |
| Baseline dataset | `.dist/study/artifacts_full/` — the `zero-free` condition (no taxonomy at all), which covers **all 410 bugs**, both modes |
| Model | gemini-3.1-flash-lite-preview (one model, everywhere) |

**Closure coverage, exactly.** 155 Closure bugs are collected in `artifacts_v2`. **153** have all four
classifications; Closure_49 and Closure_143 do not and are excluded. Closure_50–69 were not collected
(Closure_63 and Closure_93 are deprecated in Defects4J anyway). So "Closure" below means 153 of the
174 active Closure bugs.

**Three words we use constantly:**

- **pre-fix** — what the pipeline sees at triage time: the buggy code and the failing tests. No fix.
- **post-fix** — the same bug, but the developer's actual fix diff is also in the prompt.
- **drift** — the pre-fix label and the post-fix label are different for the same bug.

**Three conditions we compare:**

- `zero-free` — no taxonomy. The model invents its own label in its own words.
- `few-open` — the 7 ODC types plus an "Other" escape, taught in one prompt with examples.
- `scientific-open` — the same taxonomy, but the model must run a hypothesis → prediction → probe →
  observation loop before answering.

**How the numbers were produced.** Every figure was recomputed straight from the
`classification.*.json` files using the pipeline's own functions (`compare_classifications`,
`compute_cohens_kappa`, `compute_taxonomy_grounding_metrics`). As a correctness check, the same script
was first run on the original 257 bugs and reproduced the morning version's published figures
(73.5%, κ 0.577, Δκ 0.141, McNemar 46/31, 228 free-form labels, …). The Closure workbook
(`reports/artifacts_v2/per_project/Closure_2026-09-15.xlsx`, all six tabs) was cross-checked against
the artifacts: **0 mismatches across all 612 Closure labels**, and its Type Distribution, Type Drift
and both Strategy Drift tabs match the recomputed numbers exactly.

---

## What Closure changed — read this first

Closure is a compiler, and it is the single largest project in Defects4J. Adding it was the first
real test of whether the five-project picture generalises. The short version: **the structural
findings held; the agreement numbers dropped; one claim no longer holds.**

| Finding | 5 projects (257) | 6 projects (410) | Closure alone (153) | Verdict |
| --- | --- | --- | --- | --- |
| Three types cover almost everything | 98.4% | **97.8%** | 96.7% | Holds |
| "Other" escapes | 0 / 1,028 | **0 / 1,640** | 0 / 612 | Holds, bound tightens to 0.2% |
| Pre-fix reproduces fix-aware label (scientific) | 73.5% | **70.2%** | 64.7% | Drops |
| Cohen's κ (scientific) | 0.577 | **0.505** | 0.359 | Drops, still "moderate" overall |
| Loop beats few-shot on κ | Δκ 0.141, p ≈ 0.012 | **Δκ 0.115, p ≈ 0.012** | Δκ 0.065, not significant | Holds overall, not on Closure alone |
| Scientific has higher κ per project | 5 of 5 | **6 of 6** | — | Holds |
| Loop "halves" cross-project spread | sd 0.079 vs 0.141 | **sd 0.108 vs 0.130** | — | **No longer true** — drop the claim |
| Type mix does not differ by project (scientific) | p = 0.38 | **p = 0.096** | — | Holds at 5%, but weaker |
| Drift stays inside the three-type triangle | 74% | **80%** | 89% | Holds, stronger |
| Strategies agree more post-fix than pre-fix | 5 of 5 | **6 of 6** | 68.0% → 75.8% | Holds |

**The one claim to retire:** "the loop halves cross-project variance." With Closure it does not. The
loop's per-project κ spread is 17% tighter than few-shot's, not 44%, because Closure is the
scientific condition's weakest project by a wide margin (κ 0.359).

**The one new thing to say:** Closure is hard for *both* strategies, and hard in one specific way —
**43 of its 54 scientific drifts are the Algorithm/Method ↔ Checking boundary**. A compiler's defects
are overwhelmingly "the analysis computed the wrong thing" versus "the analysis failed to test a
condition", which is exactly the ODC boundary that is hardest to call.

---

## Summary — where we stand

**All five RQs remain defensible.** Closure lowers the agreement numbers but does not overturn any
RQ. It removes one sub-claim (variance halving) and weakens one test (RQ1 p-value).

| RQ | Standing | The one-line reason |
| --- | --- | --- |
| **RQ1** — what types of bugs are these, and does it differ by project? | Defensible, weaker than before | 97.8% of bugs are three types; under the default condition the mix does not differ significantly by project (p = 0.096), but few-shot's does (p = 0.010) |
| **RQ2** — do the 7 ODC types cover everything? | Defensible (a clean empirical result) | We offered an "Other" escape 1,640 times. It was used **0 times** |
| **RQ3** — how closely does pre-fix reproduce the fix-aware reference? | Defensible, with the reference standard named honestly | 70.2% strict; *unrelated* to the reference on only 2.4% of bugs |
| **RQ4** — what does each part of the pipeline contribute? | Defensible, split in two | The loop significantly beats few-shot on κ (Δκ = 0.115, CI [0.026, 0.208], p ≈ 0.012) and wins in 6 of 6 projects, but its gain on Closure alone is small and not significant |
| **RQ5** — does seeing the fix change the label? | Strongest RQ | 29.8% of labels change, 80% of those changes stay inside the same three ambiguous types, aggregate distribution moves by TVD 0.05 |

**Two problems in our own writing — both fixed earlier today (2026-09-15):**

1. The misattributed "experts confuse Algorithm and Checking 80% of the time" / "Chillarege: 70–80%
   inter-rater agreement" claim — replaced with five properly sourced studies. **Section 6**.
2. Sentences that treated *agreement* as *correctness* — rewritten. **Section 7**.

---

# RQ1 — What types of bugs are in Defects4J, and does the mix change by project?

### 1. What the RQ asks

Take 410 real bugs. Label each one with an ODC defect type. Two questions: which types dominate, and
do Closure or Math bugs look different from Mockito bugs?

### 2. What we did

Ran all 410 bugs through the pipeline and counted the labels. We report the pre-fix, default
condition (`scientific-open`) as the main result, and show the other three runs so nobody thinks we
cherry-picked.

### 3. What we found

| ODC type | Scientific pre-fix | Few-shot pre-fix | Scientific post-fix | Few-shot post-fix |
| --- | --- | --- | --- | --- |
| Checking | 198 (48.3%) | 119 | 192 | 151 |
| Algorithm/Method | 175 (42.7%) | 265 | 160 | 218 |
| Assignment/Initialization | 28 (6.8%) | 11 | 37 | 28 |
| Relationship | 5 | 5 | 12 | 6 |
| Function/Class/Object | 3 | 8 | 4 | 2 |
| Interface/O-O Messages | 1 | 2 | 5 | 5 |
| Timing/Serialization | 0 | 0 | 0 | 0 |
| Other | 0 | 0 | 0 | 0 |

Two things stand out:

- **Three types cover almost everything.** Checking + Algorithm/Method + Assignment/Initialization =
  **97.8%** of all 410 bugs (98.4% before Closure). All three belong to the same ODC family,
  "Control and Data Flow".
- **Timing/Serialization never appears.** Not once in 1,640 classifications. Defects4J is a benchmark
  of single-threaded, reproducible unit-test failures, so concurrency bugs are essentially absent by
  construction.

Per-project counts, scientific pre-fix (Algorithm / Checking / Assignment / everything else):

| Project | n | Alg | Chk | Asn | Rest |
| --- | --- | --- | --- | --- | --- |
| Chart | 26 | 5 | 15 | 6 | 0 |
| **Closure** | **153** | **69** | **77** | **2** | **5** |
| Lang | 61 | 22 | 33 | 5 | 1 |
| Math | 106 | 53 | 42 | 9 | 2 |
| Mockito | 38 | 17 | 16 | 4 | 1 |
| Time | 26 | 9 | 15 | 2 | 0 |

**Closure's profile is visibly different in one respect:** Assignment/Initialization almost vanishes
(2 of 153, 1.3%, against 26 of 257, 10.1%, in the other five projects). Closure's bugs sit almost
entirely on the Algorithm/Method–Checking axis.

### 4. What the statistics say

Chi-squared test on the 6 × 6 project-by-type table, as a **Monte Carlo** test (10,000 label
shuffles), because several cells are sparse and the asymptotic test's expected-count assumption fails.

| Run | chi-squared | dof | Monte Carlo p | Cramér's V |
| --- | --- | --- | --- | --- |
| Scientific pre-fix | 36.11 | 25 | **0.096** | 0.133 |
| Few-shot pre-fix | 49.48 | 25 | **0.010** | 0.155 |
| *(5 projects, for reference)* | *21.35 / 30.95* | *20* | *0.381 / 0.058* | *0.144 / 0.174* |

**In plain words:** under the default condition, the type mix still does **not** differ significantly
across projects at the 5% level (p = 0.096), and the association is weak (V = 0.13). But the result is
weaker than before, and it is driven by Closure's near-absence of Assignment/Initialization.

Under few-shot, the difference **is** significant (p = 0.010). That sharpens the pattern first seen
with five projects: the single-call prompt lets project-specific surface detail influence the label
more than the enforced loop does.

### 5. How to explain it to faculty

> "Across six projects and 410 bugs, three ODC types account for 97.8% of the labels. We tested
> whether the mix differs by project with a Monte Carlo permutation test, because several cells are
> sparse. Under our default condition it does not differ significantly (p = 0.096), although Closure
> stands out for having almost no Assignment/Initialization defects. Under the single-call few-shot
> prompt the mix does differ by project (p = 0.010), which suggests the enforced loop is the more
> project-independent classifier."

**The likely attack:** *"These are LLM labels, not real ODC labels. Your distribution is whatever your
prompt produced."*

**The answer — concede it, and quantify it.** The total variation distance between the scientific and
few-shot pre-fix distributions is **0.23**. The shift between pre-fix and post-fix within the
scientific condition is only **0.05**. The prompting strategy moves the distribution *more* than the
oracle does, which is why RQ1 is reported for one stated condition, conditional on the configuration.

### 6. What we can and cannot claim

| We CAN claim | We CANNOT claim |
| --- | --- |
| Three Control-and-Data-Flow types cover 97.8% of these six projects | That this is the true ODC distribution of Defects4J independent of our method |
| Under the default condition, the mix does not differ significantly by project (p = 0.096) | That the mix is "identical" across projects — Closure's Assignment share is clearly lower, and p = 0.096 is not strong |
| Few-shot's mix is significantly project-dependent (p = 0.010); scientific's is not | That this generalises to the 11 projects we have not run |
| Timing/Serialization is absent, consistent with what Defects4J is | Anything about types that never fire |

---

# RQ2 — Do the seven ODC types cover every bug?

### 1. What the RQ asks

A simple empirical question: are there bugs in Defects4J that do not fit any of the seven standard
ODC defect types?

### 2. What we did

We ran the **open** taxonomy: the 7 types **plus an explicit "Other"**, with the instruction that a
bug that does not fit must be classified Other with a written justification. All 410 bugs, both
strategies, both evidence modes — **1,640 chances to escape**.

### 3. What we found

**Zero escapes, again.** Closure — a compiler, the project most likely to hold unusual defects — added
612 more chances and zero escapes.

| Observation | Count |
| --- | --- |
| Classifications that chose "Other" as the primary type | **0 / 1,640** |
| Classifications that listed "Other" even as an alternative | 1 (Math_12, scientific pre-fix) |
| `other_justification` fields ever filled in | 0 |
| ODC types actually used | 6 of 7 (Timing/Serialization never fires) |
| `needs_human_review` flags | 16 / 1,640 — 9 scientific pre-fix, 7 few-shot pre-fix, **0 in either post-fix arm**. None was an escape. |
| Bugs in the 13-bug manual reading that did not fit ODC | 0 |

### 4. What the statistics say

Rule of three (0 events in n trials → 95% upper bound ≈ 3/n):

- Per condition (n = 410): true escape rate **at most 0.7%**.
- Pooling all 1,640 classifications: **at most 0.2%**.

### 5. How to explain it to faculty

> "We did not assume the seven ODC types are sufficient — we tested it. Every classification offered
> an explicit 'Other' escape with a mandatory justification. Across 1,640 classifications, six
> projects including the Closure compiler, two strategies and two evidence modes, it was chosen zero
> times. The 95% upper bound on the true escape rate is 0.2%."

**The likely attack:** *"Maybe the model is just unwilling to say 'Other'."*

**The answer — two pieces of counter-evidence.**

1. The model reaches for rare types when a bug warrants it: Relationship 28 times, Function/Class/Object
   17, Interface/O-O Messages 13. The full label space is live.
2. With the taxonomy removed (`zero-free`), the same model produced **366 different free-form labels**
   for the same 410 bugs. It is not short of vocabulary. It never judged a bug to be outside ODC once
   ODC was offered.

**The second likely question:** *"Where is the closed-taxonomy pass?"* — a scoping decision, stated
openly: with a measured escape rate of 0%, there are no escapes for a closed pass to reabsorb, so it
could only measure prompt-wording noise, at the cost of ~1,640 more LLM calls.

### 6. What we can and cannot claim

| We CAN claim | We CANNOT claim |
| --- | --- |
| The 7 ODC types are sufficient for these six projects — 0 escapes in 1,640 chances, upper bound 0.2% | That they are sufficient for all software |
| The escape category was genuinely available and genuinely unused | That we have proven the model *would* have used it |
| Not running the closed pass is a justified decision | That we measured the closed-vs-open shift |

---

# RQ3 — How closely does pre-fix classification reproduce the fix-aware reference?

### 1. What the RQ asks

How well does the pipeline classify a bug when it can only see the buggy code and the failing tests —
the realistic situation at triage time?

### 2. What we did

**Defects4J has no ODC labels**, so there is no answer key and "accuracy against ground truth" does not
exist. Our reference is the **post-fix run**: same model, same taxonomy, same prompt, same bug, plus
the developer's fix diff. We ask how often the pre-fix run produces the same label.

**Why the post-fix run is a legitimate reference — three reasons:**

1. **It sees the evidence that defines the answer.** An ODC defect type describes the nature of the
   corrective change; the post-fix run sees that change.
2. **This is the standard move when no ground truth exists** — a two-rater design where the second
   rater has more information.
3. **The data confirms the post-fix arm is the more stable one.** `needs_human_review` fires 16 times
   pre-fix and **0 times** post-fix. The two strategies agree with each other more post-fix
   (76.3%, κ = 0.614) than pre-fix (68.0%, κ = 0.451), and this holds in **6 of 6 projects**.

### 3. What we found

The four-tier framework, in the order the approved JSS draft uses (strict, top-2, family, κ):

| Tier | What it measures | Scientific (410) | Few-shot (410) | Scientific, 5 proj. | Scientific, Closure |
| --- | --- | --- | --- | --- | --- |
| **T1 — Strict match** | Exactly the same ODC type | **70.2%** (CI 65.6–74.9) | 66.6% (CI 62.0–71.2) | 73.5% | 64.7% |
| **T2 — Top-2 match** | The other label was already an alternative | 97.1% | 98.5% | 96.1% | 98.7% |
| **T3 — Family match** | Same ODC family | 94.1% | 95.6% | 93.0% | 96.1% |
| **T4 — Cohen's κ** | Strict match, corrected for chance | **0.505** (CI 0.433–0.574) | 0.389 (CI 0.310–0.468) | 0.577 | 0.359 |

**T2 and T3 look great, and that is the problem.** Shuffle the post-fix labels randomly and you still
get 92.5% and 92.9%. On their own they prove almost nothing. **Read them as severity, over the
disagreeing bugs only:**

| Among bugs where pre-fix ≠ post-fix | Scientific (122 bugs) | Few-shot (137 bugs) |
| --- | --- | --- |
| The post-fix label was already on the pre-fix shortlist ("near miss") | **90.2%** | 95.6% |
| Both labels in the same ODC family | **80.3%** | 86.9% |
| **Genuinely unrelated** (not shortlisted AND different family) | **10 bugs** = 8.2% of drifts = **2.4% of all bugs** | 2 bugs = 0.5% of all bugs |

The 10 unrelated scientific bugs: Chart_23, Lang_4, Lang_29, Math_12, Math_34, Math_70, Mockito_4,
Mockito_14, Mockito_23, and **Closure_171** (the only Closure bug in the set).

**Headline to publish:**

> The pipeline assigns the same defect type as the fix-aware reference on **70.2%** of 410 bugs. On a
> further 27%, it disagrees but had already shortlisted the reference label or landed in the same ODC
> family. On only **2.4% of bugs (10 of 410)** is the pre-fix label genuinely unrelated.

### 4. What the statistics say

- **κ = 0.505 is "moderate"** on the Landis–Koch scale, clearly below "substantial" (0.61). Closure
  alone is κ = 0.359, which is "fair". State both plainly.
- **Closure is where agreement is lowest, but not where disagreement is worst.** Closure's drifts are
  almost all near misses (96.3% shortlisted, 88.9% same family, 1 unrelated bug). Closure is *hard*
  in the sense of sitting on the Algorithm/Method–Checking boundary, not in the sense of producing
  wild labels.
- **The ceiling.** Give *both* strategies the fix diff and they still disagree on 23.7% of bugs
  (76.3% match, κ = 0.614). Against that ceiling, 70.2% is a gap of about 6 points, not a gap to
  chance.

### 5. How to explain it to faculty

> "Defects4J has no ODC ground truth, so we do not claim absolute accuracy. We treat the fix-aware
> classification as a reference standard, because an ODC defect type is defined by the nature of the
> fix. Across 410 bugs, a classification made before any fix exists reproduces the fix-aware one on
> 70.2% of bugs, and on only 2.4% are the two labels unrelated. Closure, the compiler, is the hardest
> project at 64.7%, but its disagreements are almost entirely near misses on one ODC boundary. Even
> two fix-aware runs agree with each other only 76.3% of the time."

**The likely attack:** *"Agreement is not correctness."* — **Agree, and show we know it.** Chart_17 and
Math_90 agree perfectly across pre-fix and post-fix and are both wrong. We claim reproduction of a
better-informed reference, not correctness.

**Nuance to report:** scientific is more decisive (higher T1 and κ) but when it misses, it misses harder
(8.2% of its drifts unrelated vs 1.5% for few-shot). Few-shot hedges; scientific commits.

### 6. What we can and cannot claim

| We CAN claim | We CANNOT claim |
| --- | --- |
| Pre-fix reproduces the fix-aware classification on 70.2% of 410 bugs (κ = 0.505) | That 70.2% of our labels are *correct* |
| Only 2.4% of bugs get a genuinely unrelated pre-fix label | That agreement implies correctness — Chart_17 and Math_90 disprove that |
| Closure is the hardest project (64.7%, κ 0.359), with near-miss disagreements | That κ = 0.505 is "substantial"; it is moderate, and Closure is fair |

**RQ3's wording** (`docs/RQs_JSS.md`, 2026-09-15) asks how closely pre-fix classification
**reproduces the fix-aware reference**, not about "the correct defect types".

**Optional, if we want more:** a random sample of 60–80 bugs labelled independently by two of us from
the fix diff, blind to model output, then adjudicated — the single most valuable addition left.

---

# RQ4 — What does each part of the pipeline actually contribute?

### 1. What the RQ asks

Two ingredients beyond "ask an LLM": (a) the ODC taxonomy, (b) the scientific-debugging loop.

- **RQ4a** — what does the taxonomy buy over free-form labels? *The control condition.* Report briefly.
- **RQ4b** — **what does the enforced loop add over a strong few-shot prompt?** *The real question*,
  because both arms already have the taxonomy.

### 2. What we did

Three tiers on the **same 410 bugs**: `zero-free` (no taxonomy), `few-open` (taxonomy, one call),
`scientific-open` (taxonomy + enforced loop). The `zero-free` data lives in `artifacts_full`, verified
to cover all 410 bugs in both modes.

---

## RQ4a — The taxonomy baseline (control condition, report briefly)

### 3a. What we found

| Tier | Distinct labels | Label entropy | Same label pre-fix and post-fix? | κ |
| --- | --- | --- | --- | --- |
| `zero-free` (no taxonomy) | **366** | **8.376 bits** | **15.1%** | **0.150** |
| `few-open` | 6 | 1.291 | 66.6% | 0.389 |
| `scientific-open` | 6 | 1.446 | **70.2%** | **0.505** |
| *(5 projects: zero-free)* | *228 of 257* | *7.662* | *18.7%* | *0.184* |

**366 different labels for 410 bugs**; **342 used exactly once** (93.4%). The most common free-form
label, "Null Pointer Dereference", covers 15 bugs. On Closure alone: 141 labels for 153 bugs, and the
model reproduced its own label across the two modes only **9.2%** of the time. The vocabulary
reduction ratio (1 − 7/366) is **0.981**. 153 of the 410 free-form labels map to no ODC type under the
pipeline's keyword mapper (partly a mapper limitation).

Concrete examples (from the manual analysis) still apply: Chart_9 "Improper input validation logic" →
"incorrect boundary condition logic"; Math_23 "Logic error in optimization result selection" → "logic
error in optimization result tracking". Same meaning, never counted together.

### 4a. What the statistics say

McNemar's exact test on per-bug pre/post consistency (free-form labels compared case-insensitively):

| Comparison | Consistent under A only | Consistent under B only | Exact p |
| --- | --- | --- | --- |
| scientific-open vs zero-free | 223 | 18 | **3.8 × 10⁻⁴⁶** |
| few-open vs zero-free | 204 | 14 | **2.1 × 10⁻⁴⁴** |

A sanity check that passed on a comparison nobody disputed — not the finding.

### 5a. How to explain it — two sentences, then move on

> "Without a taxonomy the model produced 366 distinct labels for 410 bugs, and reproduced its own label
> across two views of the same bug only 15% of the time. That output cannot be counted, so taxonomy
> grounding is a precondition rather than a result; the interesting question is what the loop adds
> once both arms have the taxonomy."

⚠️ **Do not frame RQ4a as the strongest result.** It validates ODC, which predates us.

### 6a. What we can and cannot claim

| We CAN claim | We CANNOT claim |
| --- | --- |
| Without a taxonomy, labels are near-unique per bug (366/410) and unstable (15.1% reproducible) | That the free-form labels are *wrong* |
| Taxonomy grounding is a precondition for aggregation | That this validates our design — it validates ODC |
| This rules out "why not just ask the LLM?" | That 0.981 vocabulary reduction measures quality |

---

## RQ4b — What the scientific loop buys: **the headline of RQ4**

Same model, same taxonomy, same evidence store, same 410 bugs. The **only** difference is the enforced
hypothesis → prediction → probe → observation loop.

### 3b. What we found

| Metric | `few-open` | `scientific-open` | Gain | *5 proj. gain* |
| --- | --- | --- | --- | --- |
| Pre-fix reproduces the fix-aware label (strict) | 66.6% | **70.2%** | **+3.7 pts** | *+5.8* |
| Cohen's κ | 0.389 | **0.505** | **+0.115** | *+0.141* |
| Matches the post-fix consensus (313 bugs where both post-fix runs agree) | 71.6% | **74.8%** | +3.2 pts | *+3.6* |
| Projects where its κ is higher | 0 of 6 | **6 of 6** | — | *5 of 5* |
| Worst-project κ | 0.212 (Time) | **0.359** (Closure) | 1.69× | *2.26×* |
| Spread of κ across projects (sd) | 0.130 | **0.108** | 17% tighter | *44% tighter* |

Per-project κ gain (scientific − few-shot): Chart +0.323, Time +0.268, Mockito +0.227, Math +0.066,
**Closure +0.065**, Lang +0.049.

### 4b. What the statistics say

**Primary test — still significant with Closure.** Paired bootstrap over the 410 bugs (5,000
resamples, both conditions resampled on the same bugs):

> **Δκ = 0.115, 95% CI [0.026, 0.208], two-sided p ≈ 0.012.**

**Independent check:** scientific has the higher κ in **all six** projects; sign test one-sided
**p = 0.016**.

**Tests that do not reach significance — report them:**

| Test | Result | Why it differs |
| --- | --- | --- |
| McNemar on raw per-bug agreement | sci-only 73, few-only 58, **p = 0.221** | Raw flips, no chance correction. Few-shot puts 265 of 410 bugs on Algorithm/Method, inflating its *expected* agreement; κ prices that in, McNemar does not |
| McNemar on matching the post-fix consensus | sci-only 43, few-only 33, **p = 0.302** | Restricted to 313 consensus bugs, raw-count based, underpowered |
| **Paired bootstrap, Closure alone** | Δκ = 0.065, CI [−0.108, 0.237], **p ≈ 0.46** | **The loop's gain on Closure is not distinguishable from zero.** Both strategies reach exactly 64.7% strict match on Closure (99 of 153 each) |

**Why κ is primary, and why this is not post-hoc:** κ is Tier 4 of the four-tier framework, fixed in
the approved JSS draft before these runs.

**Where the loop earns its keep — revised with Closure.** The gain is large where few-shot is weakest
(Chart, Time, Mockito) and small elsewhere (Math, Closure, Lang). With five projects this looked like
"the loop halves variance". **With Closure, say this instead:** the loop raises the floor on the
projects where few-shot collapses (Time: few-shot κ 0.212 with a CI containing zero; scientific
0.480), but it does not rescue Closure, where both strategies are weak together.

**Is evidence coverage the explanation? No — do not claim it.** The class Defects4J marks as modified is
in the evidence store for only 8.5% of Closure bugs, which is tempting. But Mockito has it for **0%**
and shows a +0.227 gain, while Lang has it for 98% and gains only +0.049. Coverage does not explain the
per-project pattern.

**Corroboration from RQ1, now stronger:** few-shot's type mix is significantly project-dependent
(p = 0.010), scientific's is not (p = 0.096).

### The honest limitation: the loop is under-exercised, so this is a floor

Recomputed over 410 bugs with one definition (a snippet probe that actually returned the modified
class):

- **37** scientific pre-fix runs (and **126** post-fix runs) concluded with **zero probes**.
- The modified class is in the evidence store for only **125 / 410** bugs (30.5%) — **13 / 153 on
  Closure** — and a pre-fix probe actually retrieved it for only **64 / 410** (15.6%).
- Agreement by probe count: 0 probes → 86.5% (n=37); 1 → 69.1% (n=136); 2 → 63.8% (n=127);
  3+ → 73.6% (n=110). Probe count tracks bug difficulty, not success.

⚠️ **Recount note.** The morning version said the modified class was in the store for 105 of 257 bugs
and retrieved for 55. Re-running on today's `artifacts_v2` contexts with the stricter definition above
gives 112 and 59 for the same 257 bugs. The difference is definitional; quote the recomputed figures.

Frame as a floor: **a significant improvement measured while the modified class was absent from the
evidence store for 70% of bugs.**

### One counter-signal we must report: few-shot is better *with* the oracle

13-bug manual analysis (no Closure bugs in it; unchanged): scientific pre-fix 6/13, few-shot pre-fix
4/13, scientific post-fix 6/13, **few-shot post-fix 11/13**. The scientific run commits to its own chain
of reasoning and under-uses the oracle when handed one. ⚠️ n = 13, adversarially selected, single
rater — mechanism observation, not accuracy.

### 5b. How to explain it to faculty

> "Both arms use the same model, taxonomy and evidence. The only difference is the enforced
> hypothesis-and-probe loop. Across 410 bugs it raises chance-corrected agreement with the fix-aware
> reference from κ 0.389 to 0.505; a paired bootstrap puts the difference at 0.115 with a 95% interval
> of 0.026 to 0.208, and the loop has the higher κ in all six projects.
>
> The gain is not uniform. It is largest where few-shot is weakest — at Time, few-shot's reliability is
> indistinguishable from chance and the loop reaches 0.480 — and it is small on Closure, where both
> strategies land on exactly the same strict agreement. And we measured it while the buggy class was
> missing from the evidence store for 70% of bugs, so it is a lower bound."

**Likely attack:** *"McNemar says p = 0.221."* — the tests measure different things; κ corrects for
few-shot's concentration on Algorithm/Method; we report all of them.

**Likely attack:** *"On Closure your loop does nothing."* — **concede it.** On Closure the gain is not
significant. The overall result holds with Closure included, and we state the Closure exception
rather than hide it inside the pooled number.

### 6b. What we can and cannot claim

| We CAN claim | We CANNOT claim |
| --- | --- |
| The loop significantly improves chance-corrected agreement: Δκ = 0.115, CI [0.026, 0.208], p ≈ 0.012 | That it improves raw per-bug agreement significantly — McNemar p = 0.221 |
| Higher κ in 6 of 6 projects (sign test p = 0.016) | That it helps on Closure — Δκ 0.065, CI includes zero |
| Largest gains where few-shot is weakest (Chart, Time, Mockito) | ~~That it halves cross-project variance~~ — **retired**: sd 0.108 vs 0.130 |
| This is a floor, measured with the modified class absent from the store for 70% of bugs | That evidence coverage explains the per-project gains — Mockito contradicts it |

---

# RQ5 — Does seeing the fix change how a bug gets classified?

### 1. What the RQ asks

Same bug, classified without the fix and with it. How often does the label change, and is there a
pattern?

### 2. What we did

All 410 bugs in both modes under both strategies, compared per bug, per project, per type pair.

### 3. What we found

**How much the label moves:**

- Scientific: **122 / 410 bugs (29.8%)** change, κ = 0.505. (5 projects: 26.5%; Closure: 35.3%.)
- Few-shot: **137 / 410 (33.4%)**, κ = 0.389.

**But the overall distribution barely moves.** TVD between pre-fix and post-fix distributions:
**0.051** (scientific), 0.129 (few-shot).

**Where the movement happens** (scientific, 122 drifts):

| Type pair | Drifts | Direction split |
| --- | --- | --- |
| Algorithm/Method ↔ Checking | **75** | 38 Alg→Chk, 37 Chk→Alg |
| Algorithm/Method ↔ Assignment/Initialization | 12 | 10 Alg→Asn, 2 Asn→Alg |
| Checking ↔ Assignment/Initialization | 11 | 8 Chk→Asn, 3 Asn→Chk |

**98 of 122 drifts (80.3%) stay inside those three types** (74% before Closure). On Closure alone,
**43 of 54 drifts are Algorithm/Method ↔ Checking** and 48 of 54 (89%) stay in the triangle.

**Three patterns that hold across all six projects:**

1. **The two strategies agree more post-fix than pre-fix — 6 of 6 projects.** Chart 73.1% vs 65.4%,
   **Closure 75.8% vs 68.0%**, Lang 78.7% vs 68.9%, Math 75.5% vs 71.7%, Mockito 76.3% vs 68.4%,
   Time 80.8% vs 53.8%. Direction fully consistent; size ranges 3.8–27 points.
2. **Algorithm/Method is an attractor in every project, but its partner is project-dependent:**
   Checking in Closure, Lang, Time and Math; Assignment/Initialization in Chart; a diffuse spread
   including Interface/O-O Messages in Mockito.
3. **The model's own confidence signals are useless as a filter.** 16 `needs_human_review` flags and 0
   low-confidence flags in 1,640 classifications. Chart_26 was flagged while stating 0.9 confidence;
   Chart_11 probed four times, reached nothing, and concluded at 1.0.

### 4. What the statistics say

**Per-project reliability, bootstrap 95% CIs** (2,000 resamples):

| Project | n | Scientific strict | Scientific κ [95% CI] | Few-shot strict | Few-shot κ [95% CI] |
| --- | --- | --- | --- | --- | --- |
| Chart | 26 | 80.8% | 0.672 [0.419, 0.906] | 57.7% | 0.349 [0.105, 0.616] |
| **Closure** | **153** | **64.7%** | **0.359 [0.228, 0.489]** | **64.7%** | **0.294 [0.143, 0.435]** |
| Lang | 61 | 73.8% | 0.546 [0.360, 0.714] | 73.8% | 0.497 [0.293, 0.692] |
| Math | 106 | 75.5% | 0.603 [0.472, 0.726] | 74.5% | 0.537 [0.392, 0.671] |
| Mockito | 38 | 65.8% | 0.499 [0.285, 0.701] | 52.6% | 0.272 [0.060, 0.485] |
| Time | 26 | 69.2% | 0.480 [0.159, 0.754] | 57.7% | 0.212 [−0.138, 0.530] |

(Five-project CIs are the morning run's; re-bootstrapping moves them by ±0.02, noise only.)

Closure's κ interval is narrow because n = 153 — it is precisely estimated, and precisely low. Time's
few-shot interval still includes zero.

**The ceiling:** with the fix visible to both, the strategies still disagree on 23.7% of bugs (76.3%,
κ = 0.614).

### 5. How to explain it to faculty

> "Just under a third of labels change when the fix becomes visible — 29.8% under our default condition.
> But four fifths of those changes stay inside the same three ODC types that the literature documents
> human raters confusing, and on Closure the drift is almost entirely one boundary, Algorithm/Method
> versus Checking. The aggregate type distribution barely moves: TVD 0.05. The effect of the oracle is
> real per bug and negligible in aggregate — the level ODC was designed for."

**Back it with the literature:** Henningsson & Wohlin (2004), descriptions only → κ = 0.16; NoSQL ODC
study (JSS 2020), full code and change context → κ = 0.93. Human agreement depends on evidence, which is
our pre-fix vs post-fix design restated.

**Back it with mechanism (13-bug manual analysis):** the fix helps (Time_3, Chart_11); the fix hurts
(Math_23, Math_17); the fix is ignored (Chart_17, Math_90); the bug report anchors the label (Math_90).

### 6. What we can and cannot claim

| We CAN claim | We CANNOT claim |
| --- | --- |
| 29.8% of labels change when the fix is visible; 80% of changes stay in the 3 ambiguous types | That the post-fix label is correct and the pre-fix one wrong |
| The aggregate distribution barely moves (TVD 0.05) | That drift is harmless; 10 bugs drift to an unrelated type |
| Post-fix strategy agreement exceeds pre-fix in 6/6 projects | A single effect size — it ranges 3.8 to 27 points |
| Closure's reliability is precisely estimated and low (κ 0.359 [0.228, 0.489]) | That Chart or Time κ is precise; n = 26 |

---

# Section 6 — ✅ FIXED: the "experts confuse Algorithm and Checking 80% of the time" claim

**Status: corrected across the repo on 2026-09-15.** Unchanged by the Closure update.

**Canonical evidence table: `docs/eval_defence.md` §1 Pillar 2.**

### What we checked before removing the claim

The claim was *"Chillarege et al. (1992): human inter-rater agreement ~70–80%."* We searched
Chillarege et al. (1992) IEEE TSE 18(11); the Chillarege Inc. ODC concept article; Chillarege's "ODC
for Process Measurement, Analysis and Control"; the IBM ODC v5.2 reference (`docs/odc_doc.md`); and the
Wikipedia ODC article. **None of them reports an inter-rater agreement figure.**

### The finding that replaces it

Agreement on ODC classification is **evidence-dependent**:

| Evidence the rater had | Study | Agreement |
| --- | --- | --- |
| Fault **descriptions only** | Henningsson & Wohlin (2004), 8 raters, 30 faults | mean pairwise **κ = 0.16** |
| Report **text only** | Hernández-González et al. (2018), 5 annotators, 962 + 675 defects | majority of 5 reached on only **481/962** and **394/675** |
| **Code available** | El Emam & Wieczorek (1998) | "in general repeatable" (no κ recovered — do not quote one) |
| Full repository context | Rahman & Farhana (2020), COVID-19 projects | **72.7% / κ 0.70** (open coding), 95.1% / κ 0.93 (closed) — ⚠️ verify against PDF |
| Full code + change | NoSQL ODC study (JSS 2020) | **κ = 0.93** (a verification step, not blind labelling) |

The literature's explanation for human disagreement — insufficient evidence — **is our experimental
variable**. It also explains why our drift concentrates in the Assignment / Algorithm / Checking
triangle, and why the post-fix arm is the better-informed reference.

### Where the "80%" actually came from

A garbled reading of Henningsson & Wohlin (2004):

- **Wrong pair.** Their most-confused pair was **Assignment ↔ Algorithm**: *"The most frequent mix-up
  is the interchange between AS and AL, in total, 22 of the 28 pairs mixed these two classes up a
  number of times."*
- **Wrong unit.** 22/28 = 79% counts **rater pairs**, not bugs.
- Their Table 6 by occasions: Assignment–Algorithm 184; Interface–Algorithm 77; **Checking–Algorithm
  68 (third)**; Assignment–Interface 59; Assignment–Checking 49.

⚠️ **Never write "experts confuse Algorithm and Checking about 80% of the time."**

### What was fixed, and where — ✅ 2026-09-15

| File | What it said | Status |
| --- | --- | --- |
| `docs/eval_defence.md` §1 Pillar 2 | "Chillarege et al. (1992): human inter-rater agreement ~70–80%" and "Typical ODC studies: κ 0.60–0.80" | ✅ Replaced |
| `docs/eval_defence.md` §6 talking point 1 | "Even human ODC experts disagree 20-30% of the time" | ✅ Replaced with the measured two-strategy ceiling |
| `docs/Research Paper Roadmap_ Defect Classification.md` | "Chillarege's foundational work … peaks at 70% to 80%" | ✅ Rewritten around evidence-dependence |
| `d4j_odc_pipeline/comparison.py` module docstring | "Chillarege et al. (1992) — ODC inter-rater disagreement is expected (~20-30%)" | ✅ Replaced |
| `d4j_odc_pipeline/comparison.py` insight text (~line 146) | "Even expert human classifiers disagree on 20-30% of bugs (Chillarege 1992)" — written into generated reports | ✅ Replaced |
| `docs/classification_engine_plan.md` (stale doc) | "κ vs the ~20–30% human-disagreement ceiling" | ✅ Replaced |

Also corrected: the AutoSD citation is **Kang, Chen, Yoo & Lou, EMSE**, not "Kang, Yoo & Ryu (2023)".

⚠️ **Deliberately NOT fixed:** `iut_submissions/presentation/generate_presentation.py:736` cites "Kang
et al. (2023)". That directory is **frozen** per `CLAUDE.md`.

---

# Section 7 — ✅ FIXED: the "agreement means correctness" framing

**Status: corrected in `docs/eval_defence.md` on 2026-09-15.**

| Location | What it said | Now |
| --- | --- | --- |
| §1 Pillar 1 | "Both classifications are *correct from their evidence perspective*" | "Each classification is reasonable given the evidence that produced it", plus a Chart_17 / Math_90 warning |
| §6 talking point 2 | "both are correct, but they may name the condition differently" | "two evidence positions, not two truths" |

**Problem 1: agreement is not correctness.** Chart_17 and Math_90 agree perfectly and are both wrong.
Write "reproduces the fix-aware reference", never "agreement proves correctness".

**Problem 2: ODC defect type is not a work-assignment scheme.** ODC gives process feedback from
**distributions**. Do not claim "right type → right developer".

### The version to actually use (updated for 410 bugs)

- **At the aggregate level — ODC's intended use.** Pre-fix classifications produce almost the same
  type distribution as fix-aware ones (TVD **0.05** under scientific).
- **The disagreements are the known-ambiguous ones.** 80% of drifts stay inside the triangle where
  humans also disagree; only **2.4% of bugs** are genuinely unrelated.
- **Offer a confidence tier for triage.** All four runs agree on **191 / 410 bugs (46.6%)**. On the 313
  bugs where both post-fix runs agree, scientific pre-fix matches that consensus **74.8%** of the time.
- **Describe post-fix correctly.** A better-informed reference rater. Not an oracle for truth.

---

# Section 8 — Is the 13-bug manual analysis worth presenting?

**For explaining the pipeline, and as the "why" behind RQ5: yes.** Unchanged by Closure (none of the 13
is a Closure bug — a Closure case study on the Algorithm/Method ↔ Checking boundary would be a natural
addition).

| Bug | What it demonstrates |
| --- | --- |
| Chart_9 | The loop working exactly as designed |
| Chart_11 | The loop starved — 4 probes, none reached the code, confidence still 1.0 |
| Time_3, Math_104 | Right mechanism, wrong label |
| Chart_17, Math_90 | Confident, consistent, and wrong — never ran an experiment |
| Math_23 | The oracle actively hurting |
| Chart_7 | Right label, wrong reason |

**As a measure of accuracy: no.** Selected to show failure modes; one person's reading.

**Three things that would make it count for more:** two independent labellers from the fix diff before
reading model output; present as qualitative mechanism study; grade label and reasoning separately.

---

# Section 9 — Threats to validity (disclose all of these)

1. **A real bug in our probe implementation.** `execute_probe` matches class names by substring
   (`argument in s.class_name`, `d4j_odc_pipeline/agent.py`). `snippet(...Dfp)` returns **DfpTest**;
   `snippet(Gamma)` returns **GammaTest**. **Fix before any rerun.** Weakens RQ4b.
2. **Evidence coverage is poor, and worst on Closure.** The modified class is missing from
   `context.json` for **285 of 410 bugs** (69.5%) — **140 of 153 on Closure** (91.5%), and every
   Mockito bug. Caps what the loop can contribute.
3. **One model.** gemini-3.1-flash-lite-preview everywhere, via a rolling `-preview` alias (see
   `interesting_findings.md` on label churn between runs two months apart). Pin a dated snapshot next
   time.
4. **Possible memorization.** Defects4J bugs and fixes are public.
5. **Bug-report anchoring.** Math_90 is the clearest case.
6. **Statistical limitations, and what we did.** Sparse RQ1 cells → Monte Carlo test. Small per-project
   n → bootstrap CIs. Near-ceiling T2/T3 → reported conditional on disagreement.
7. **Partial benchmark.** 410 bugs from 6 of 17 projects; Closure itself is 153 of 174. Say so plainly.
8. **Baseline context mismatch.** The `zero-free` baseline was classified from `artifacts_full`
   contexts, while `few-open` and `scientific-open` use the re-collected `artifacts_v2` contexts. This
   applies to all six projects equally. It does not plausibly explain a 366-vs-6 vocabulary gap, but it
   means the RQ4a comparison is not evidence-identical.

---

# Sources

- K. Henningsson and C. Wohlin, "Assuring Fault Classification Agreement: An Empirical Evaluation,"
  ISESE 2004, pp. 95–104. [PDF](https://www.wohlin.eu/isese04.pdf) ·
  [IEEE Xplore](https://ieeexplore.ieee.org/document/1334897)
- K. El Emam and I. Wieczorek, "The Repeatability of Code Defect Classifications," ISSRE 1998,
  pp. 322–333. [IEEE Xplore](https://ieeexplore.ieee.org/document/730897/)
- J. Agnelo, N. Laranjeiro and J. Bernardino, "Using Orthogonal Defect Classification to Characterize
  NoSQL Database Defects," Journal of Systems and Software, 2020.
  [Preprint PDF](https://eden.dei.uc.pt/~cnl/papers/2020-jss-odc-joao-v64-submitted.pdf) ·
  [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0164121219302250)
- R. Chillarege et al., "Orthogonal Defect Classification: A Concept for In-Process Measurements,"
  IEEE TSE 18(11), 1992. [ACM DL](https://dl.acm.org/doi/10.1109/32.177364)
- Chillarege Inc., ODC concept article. [Link](https://www.chillarege.com/articles/odc-concept.html)
- S. Kang, B. Chen, S. Yoo and J.-G. Lou, "Explainable Automated Debugging via Large Language
  Model-driven Scientific Debugging" (AutoSD), Empirical Software Engineering — the loop-iteration
  ordering our `scientific` strategy implements.
- F. Thung, D. Lo and L. Jiang, "Automatic Defect Categorization," WCRE 2012.
  [ACM DL](https://dl.acm.org/doi/10.1109/WCRE.2012.30)

---

## Where the numbers come from

All figures were recomputed from the `classification.*.json` artifacts with the pipeline's own
functions. The analysis script was validated by reproducing the 257-bug figures before being run on
Closure and on all 410 bugs. Bootstrap and permutation p-values carry Monte Carlo noise of about
±0.005; bootstrap CI endpoints move by about ±0.01–0.02 between runs.

Related documents: `docs/RQs_JSS.md` (RQ wording, canonical),
`.dist/study/reports/artifacts_v2/interesting_findings.md` (running per-project notes),
`analysis_v2/manual_analysis/` (the 13-bug shortlist), `docs/JSS_HANDOFF.md` (paper-drafting entry
point), `latex/defence book/main.tex` (the defence book, updated from this document).
