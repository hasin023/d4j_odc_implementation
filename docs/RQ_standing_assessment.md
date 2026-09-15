# RQ Standing Assessment — plain-language version

**Date:** 2026-09-15 (rewritten for readability; supersedes the 2026-09-14 draft)

This document answers one question: **for each of our five research questions, do we have enough
data to defend it in front of faculty and reviewers, and what exactly should we say?**

Every RQ below is written in the same six parts:

1. **What the RQ asks** — in plain words.
2. **What we did** — the experiment behind it.
3. **What we found** — the numbers.
4. **What the statistics say** — the tests, and what they mean.
5. **How to explain it to faculty** — the argument, including the likely attack and the answer.
6. **What we can claim / what we cannot claim** — the exact boundary.

---

## The data behind everything in this document

| Thing | Value |
|---|---|
| Bugs | **257** — Chart 26, Lang 61, Math 106, Mockito 38, Time 26. Closure not included yet. |
| Main dataset | `.dist/study/artifacts_v2/` |
| Conditions in the main dataset | `scientific-open` and `few-open` |
| Evidence modes | **pre-fix** (buggy code + failing tests only) and **post-fix** (same, plus the developer's real fix diff) |
| Total classifications | 2 conditions × 2 modes × 257 bugs = **1,028** |
| Baseline dataset | `.dist/study/artifacts_full/` — the `zero-free` condition (no taxonomy at all), which covers **exactly the same 257 bugs**, both modes |
| Model | gemini-3.1-flash-lite-preview (one model, everywhere) |

**Three words we use constantly:**

- **pre-fix** — what the pipeline sees at triage time: the buggy code and the failing tests. No fix.
- **post-fix** — the same bug, but the developer's actual fix diff is also in the prompt.
- **drift** — the pre-fix label and the post-fix label are different for the same bug.

**Three conditions we compare:**

- `zero-free` — no taxonomy. The model invents its own label in its own words.
- `few-open` — the 7 ODC types plus an "Other" escape, taught in one prompt with examples.
- `scientific-open` — the same taxonomy, but the model must run a hypothesis → prediction → probe →
  observation loop before answering.

All numbers were recomputed straight from the `classification.*.json` files using the pipeline's own
code. We also checked the five Excel workbooks in `analysis_v2/` against the artifacts: **0 mismatches
across all 257 bugs and all 4 conditions**, so the workbooks and the artifacts tell the same story.

---

## Summary — where we stand

**All five RQs are defensible.** That is a change from the previous draft, which rejected RQ3 and RQ4.
Two things changed: we found the `zero-free` baseline data already exists for all 257 bugs, and we
fixed how RQ3 is worded and measured.

| RQ | Standing | The one-line reason |
|---|---|---|
| **RQ1** — what types of bugs are these, and does it differ by project? | Defensible | 98.4% of bugs are three types, and the mix does not differ significantly between projects |
| **RQ2** — do the 7 ODC types cover everything? | Defensible (a clean empirical result) | We offered an "Other" escape 1,028 times. It was used **0 times** |
| **RQ3** — how accurate is the pipeline? | Defensible, once we name our reference standard honestly | Pre-fix reproduces the fix-aware label 73.5% of the time, and is *unrelated* to it on only 3.5% of bugs |
| **RQ4** — what does each part of the pipeline contribute? | Defensible, split in two | Taxonomy grounding is a huge effect (p < 1e-33); the loop is a small but consistent one |
| **RQ5** — does seeing the fix change the label? | Strongest RQ | 26.5% of labels change, 74% of those changes stay inside the same three ambiguous types |

**Two things to fix in our own writing before someone else finds them:** the "experts confuse Algorithm
and Checking 80% of the time" claim (Section 6) and any sentence that treats *agreement* as
*correctness* (Section 7).

---

# RQ1 — What types of bugs are in Defects4J, and does the mix change by project?

### 1. What the RQ asks

Take 257 real bugs. Label each one with an ODC defect type. Two questions: which types dominate, and
do Math bugs look different from Mockito bugs?

### 2. What we did

Ran all 257 bugs through the pipeline and counted the labels. We report the pre-fix, default condition
(`scientific-open`) as the main result, and show the other three runs so nobody thinks we cherry-picked.

### 3. What we found

| ODC type | Scientific pre-fix | Few-shot pre-fix | Scientific post-fix | Few-shot post-fix |
|---|---|---|---|---|
| Checking | 121 (47.1%) | 79 | 113 | 93 |
| Algorithm/Method | 106 (41.2%) | 156 | 96 | 132 |
| Assignment/Initialization | 26 (10.1%) | 9 | 32 | 24 |
| Relationship | 2 | 5 | 8 | 4 |
| Interface/O-O Messages | 1 | 2 | 5 | 4 |
| Function/Class/Object | 1 | 6 | 3 | 0 |
| Timing/Serialization | 0 | 0 | 0 | 0 |
| Other | 0 | 0 | 0 | 0 |

Two things stand out:

- **Three types cover almost everything.** Checking + Algorithm/Method + Assignment/Initialization =
  **98.4%** of all 257 bugs. These three all belong to the same ODC family, "Control and Data Flow".
- **Timing/Serialization never appears.** Not once in 1,028 classifications. That makes sense —
  Defects4J is a benchmark of single-threaded, reproducible unit-test failures, so concurrency and
  serialization bugs are essentially absent by construction.

Per-project counts, scientific pre-fix (Algorithm / Checking / Assignment / everything else):

| Project | n | Alg | Chk | Asn | Rest |
|---|---|---|---|---|---|
| Chart | 26 | 5 | 15 | 6 | 0 |
| Lang | 61 | 22 | 33 | 5 | 1 |
| Math | 106 | 53 | 42 | 9 | 2 |
| Mockito | 38 | 17 | 16 | 4 | 1 |
| Time | 26 | 9 | 15 | 2 | 0 |

### 4. What the statistics say

We tested whether the type mix differs by project with a chi-squared test on the 5 × 6 table.

The usual chi-squared test assumes every cell has an expected count of at least 5. Ours does not —
several types are rare. So instead of trusting the approximation, we ran a **Monte Carlo chi-squared**:
shuffle the labels randomly across bugs 10,000 times, and see how often the shuffled table looks as
uneven as ours. This needs no assumption about cell counts.

| Run | chi-squared | dof | Monte Carlo p | Cramér's V (effect size) |
|---|---|---|---|---|
| Scientific pre-fix | 21.35 | 20 | **0.381** | 0.144 |
| Few-shot pre-fix | 30.95 | 20 | **0.058** | 0.174 |

**In plain words:** p = 0.381 means the differences we see between projects are exactly what random
variation would produce. There is **no significant difference between projects** under our default
condition. Cramér's V of 0.14 says the same thing — a very weak association.

Few-shot's p = 0.058 is close to the 0.05 line but still not significant. That is interesting in
itself: the weaker prompt lets project-specific surface details influence the label a little more than
the enforced loop does.

### 5. How to explain it to faculty

Say this:

> "Across five projects and 257 bugs, three ODC types account for 98.4% of the benchmark. We tested
> whether the mix differs by project using an exact permutation test rather than the standard
> chi-squared, because several cells are sparse. It does not differ significantly (p = 0.38). So the
> ODC profile of Defects4J is stable — it is a property of the benchmark, not of any one project."

**The likely attack:** *"These are LLM labels, not real ODC labels. Your distribution is whatever your
prompt produced."*

**The answer — concede it, and quantify it.** We measured how much the distribution moves when we
change the prompt. The total variation distance between the scientific and few-shot pre-fix
distributions is **0.23**. For comparison, the shift between pre-fix and post-fix within the scientific
condition is only **0.07**. So yes — the prompting strategy moves the distribution *more* than the
oracle does. That is why we report RQ1 for one stated condition and label it as conditional on the
pipeline configuration, instead of presenting it as "the" distribution of Defects4J.

### 6. What we can and cannot claim

| We CAN claim | We CANNOT claim |
|---|---|
| Three Control-and-Data-Flow types cover 98.4% of these five projects | That this is the true ODC distribution of Defects4J independent of our method |
| The type mix is statistically stable across projects (exact test, p = 0.38) | That it generalises to Closure or to the full 17-project benchmark — we have not run those |
| Timing/Serialization is absent, consistent with what Defects4J is | Anything about types that never fire; absence here is about the benchmark, not about ODC |

---

# RQ2 — Do the seven ODC types cover every bug?

### 1. What the RQ asks

A simple yes/no empirical question: are there bugs in Defects4J that do not fit any of the seven
standard ODC defect types?

### 2. What we did

We ran the **open** taxonomy. That means the prompt gives the model the 7 types **plus an explicit
eighth option, "Other"**, and tells it that if a bug does not fit, it must choose Other and write a
justification for why. In other words, we deliberately built the escape hatch and left the door open.

We did this for all 257 bugs, in both strategies, in both evidence modes. 1,028 chances to escape.

### 3. What we found

**Zero escapes. Not one.**

| Observation | Count |
|---|---|
| Classifications that chose "Other" as the primary type | **0 / 1,028** |
| Classifications that listed "Other" even as a secondary/alternative type | 1 (Math_12, scientific pre-fix) |
| `other_justification` fields ever filled in | 0 |
| ODC types actually used | 6 of 7 (Timing/Serialization never fires) |
| `needs_human_review` flags raised | 11 / 1,028 — 6 scientific pre-fix, 5 few-shot pre-fix, **0 in either post-fix arm**. None of the 11 was an escape. |
| Bugs in the 13-bug manual reading that did not fit ODC | 0 |

### 4. What the statistics say

You cannot compute a p-value on a count of zero, but you can bound it.

Using the **rule of three**: if you observe 0 events in n trials, the 95% upper bound on the true rate
is roughly 3/n.

- Per condition (n = 257): true escape rate is **at most 1.2%**.
- Pooling all 1,028 classifications: **at most 0.3%**.

**In plain words:** even in the worst case consistent with our data, fewer than 1 bug in 80 would fall
outside the seven types. Practically, the taxonomy is exhaustive for this benchmark.

### 5. How to explain it to faculty

This is the easiest RQ to present, because it is a clean empirical finding with no modelling in it:

> "We did not assume the seven ODC types are sufficient — we tested it. Every classification was run
> with an explicit 'Other' escape category that the model was told to use, with justification, for any
> bug that did not fit. Across 1,028 classifications, covering five projects, two prompting strategies
> and two evidence modes, the escape category was chosen zero times. The 95% upper bound on the true
> escape rate is 0.3%."

**The likely attack:** *"Maybe the model is just unwilling to say 'Other'. Zero could be reluctance,
not coverage."*

**The answer — two pieces of counter-evidence.**

1. The model is not collapsing onto safe defaults. It **did** reach for the rare types when the bug
   warranted it: Relationship 19 times, Interface/O-O Messages 12, Function/Class/Object 10. So the
   full label space is live, not just the top three.
2. The same model, with the taxonomy removed (`zero-free`, see RQ4), produced **228 different
   free-form labels** for these same 257 bugs. It is clearly not short of vocabulary or unwilling to
   name unusual things. It simply never judged a bug to be outside ODC once ODC was offered.

**The second likely question:** *"Your design said you would also run a closed-taxonomy pass. Where is
it?"*

**The answer — this is a scoping decision, and we state it openly.** The closed pass (7 types, no
escape) was designed to measure whether *removing the escape option* changes ordinary labels. With a
measured escape rate of exactly 0%, there are no escapes for the closed pass to reabsorb — so it could
only measure prompt-wording noise, at a cost of ~900 additional LLM calls. We chose not to spend that.

Write it in the paper as: *"Because the open taxonomy produced no escapes, a closed-taxonomy pass could
only have measured prompt-perturbation noise; we did not run it."*

### 6. What we can and cannot claim

| We CAN claim | We CANNOT claim |
|---|---|
| The 7 ODC types are sufficient for Defects4J — 0 escapes in 1,028 chances, upper bound 0.3% | That the 7 types are sufficient for all software; Defects4J is a specific kind of benchmark |
| The escape category was genuinely available and genuinely unused | That we have proven the model *would* have used it; we can only show it had both the option and the vocabulary |
| Not running the closed pass is a justified decision, not a gap | That we measured the closed-vs-open shift, because we did not |

---

# RQ3 — How accurate is the pipeline?

### 1. What the RQ asks

How well does the pipeline classify a bug when it can only see the buggy code and the failing tests —
which is the realistic situation at triage time, before anyone has written a fix?

### 2. What we did

**First, the honest problem: Defects4J has no ODC labels.** Nobody has ever labelled these 438 bugs
with ODC defect types. There is no answer key. So "accuracy" cannot mean "accuracy against ground
truth" — that data does not exist.

What we do instead is build the **best available reference standard** and measure against it.

Our reference is the **post-fix run**: the same model, the same taxonomy, the same prompt, on the same
bug — but with the developer's actual fix diff included in the evidence. Then we ask: *how often does
the pre-fix run produce the same label as the fix-aware run?*

**Why the post-fix run is a legitimate reference standard — three reasons:**

1. **It sees the evidence that defines the answer.** An ODC defect type describes *the nature of the
   corrective change*. The post-fix run sees that change. The pre-fix run has to guess it. When the
   defining evidence is present, the label is better grounded.
2. **This is the standard move when no ground truth exists.** It is a two-rater design where the second
   rater is deliberately given more information. Reporting agreement with a better-informed rater is
   exactly what inter-rater reliability studies do.
3. **The data confirms the post-fix arm is the more stable one.** `needs_human_review` fires 11 times in
   pre-fix and **0 times** in post-fix. And the two strategies agree with each other more in post-fix
   (76.7%, κ = 0.633) than in pre-fix (68.1%, κ = 0.469). Give both strategies the fix, and they
   converge. Take it away, and they diverge. That is what you expect if the fix resolves ambiguity.

### 3. What we found

We grade agreement on **four levels**, from "identical" to "not even related":

| Level | What it measures | Scientific | Few-shot |
|---|---|---|---|
| **L1 — Strict match** | Exactly the same ODC type | **73.5%** (95% CI 68.1–79.0) | 67.7% (CI 62.3–73.2) |
| **L2 — Cohen's κ** | Same, corrected for agreement you'd get by luck | **0.577** (CI 0.498–0.655) | 0.437 (CI 0.344–0.527) |
| **L3 — Top-2 match** | The other run's label was already listed as an alternative | 96.1% | 97.7% |
| **L4 — Family match** | Both labels sit in the same ODC family | 93.0% | 94.2% |

Now — **L3 and L4 look great, and that is exactly the problem.** 96% and 93% are near the ceiling. If
you shuffle the labels randomly, you still get 90.6% and 92.4%. So quoted on their own, they prove
almost nothing.

**The fix is to read them as severity, not as accuracy.** L3 and L4 are not four separate accuracy
tests — they describe *how bad the disagreement is* on the bugs where L1 already failed. So report them
**only over the disagreeing bugs**:

| Among bugs where pre-fix ≠ post-fix | Scientific (68 bugs) | Few-shot (83 bugs) |
|---|---|---|
| The post-fix label was already on the pre-fix run's shortlist ("near miss") | **85.3%** | 92.8% |
| Both labels in the same ODC family | **73.5%** | 81.9% |
| **Genuinely unrelated** (not on the shortlist AND different family) | **9 bugs** = 13.2% of drifts = **3.5% of all bugs** | 2 bugs = 2.4% of drifts = **0.8% of all bugs** |

**This is the headline number to publish:**

> The pipeline assigns the same defect type as the fix-aware reference on **73.5%** of bugs. On a
> further 23%, it disagrees but had already shortlisted the reference label or landed in the same ODC
> family. On only **3.5% of bugs (9 of 257)** is the pre-fix label genuinely unrelated to the fix-aware
> one.

### 4. What the statistics say

- **Cohen's κ = 0.577** is "moderate" on the Landis–Koch scale. Note that this is *below* the
  "substantial" (0.6–0.8) target written in `docs/eval_defence.md`. Do not quietly drop that target —
  either revise it, or state that we fell just short of it and why.
- **Confidence intervals matter more than the point estimate.** The scientific κ CI is [0.498, 0.655]
  and the few-shot CI is [0.344, 0.527]. They barely overlap, which is why scientific is the better
  condition but not dramatically so.
- **A useful ceiling, and this is important.** Give *both* strategies the fix diff, and they still
  disagree with each other on 23.3% of bugs (76.7% match, κ = 0.633). Two runs of the same model, both
  holding the answer, cannot exceed ~77% agreement. Against that ceiling, our pre-fix 73.5% is not
  "moderate" — it is close to the maximum achievable.

### 5. How to explain it to faculty

Lead with the honesty, not the number:

> "Defects4J has no ODC ground truth, so we do not claim absolute accuracy. What we do is give the same
> classifier the developer's actual fix and treat that fix-aware classification as our reference
> standard — because the ODC defect type is defined by the nature of the fix, so the run that sees the
> fix is the better-informed rater. Our question is then precise: how well does a classification made
> before any fix exists reproduce the classification made after it exists? The answer is 73.5% exactly,
> and on only 3.5% of bugs are the two labels unrelated. For calibration: even when both of our
> strategies are given the fix, they only agree with each other 76.7% of the time — so 73.5% is close
> to the practical ceiling, not close to chance."

**The likely attack:** *"Agreement is not correctness. Both runs can be wrong together."*

**The answer — agree completely, and show that we already know it.** In our 13-bug manual analysis,
Chart_17 and Math_90 agree perfectly across pre-fix and post-fix and are **both wrong**. We do not
claim agreement proves correctness. We claim reproduction of a better-informed reference, which is a
weaker and defensible claim, and it is exactly the claim that matters operationally: at triage time the
fix does not exist, so what you need to know is whether the early label will survive contact with the
fix.

**Note this honest nuance in the paper:** scientific is more decisive (higher L1, higher κ) but when it
does miss, it misses harder (13.2% of its drifts are hard, versus 2.4% for few-shot). Few-shot hedges;
scientific commits. Report both — it makes the analysis look careful rather than promotional.

### 6. What we can and cannot claim

| We CAN claim | We CANNOT claim |
|---|---|
| Pre-fix classification reproduces the fix-aware classification on 73.5% of bugs (κ = 0.577) | That 73.5% of our labels are *correct* — there is no answer key |
| Only 3.5% of bugs get a genuinely unrelated pre-fix label | That agreement implies correctness — Chart_17 and Math_90 disprove that |
| 73.5% sits close to the ~77% two-strategy ceiling | That κ = 0.577 meets the "substantial agreement" bar; it does not, and we should say so |

**RQ3's wording was changed** in `docs/RQs_JSS.md` on 2026-09-15. The old version asked about "the
correct defect types", which promises ground truth we do not have. The new version asks how closely
pre-fix classification **reproduces the fix-aware reference classification**. Same data, same tables,
no over-claim.

**Optional, if we want more:** a random sample of 60–80 bugs, labelled independently by two of us from
the fix diff without seeing any model output, then adjudicated. That would give a real human reference
and let us score *both* arms against it. It is the single most valuable addition left — but RQ3 stands
without it, because the RQ now asks about reproduction, not absolute correctness.

---

# RQ4 — What does each part of the pipeline actually contribute?

### 1. What the RQ asks

Our pipeline has two ingredients beyond "ask an LLM": (a) we force it to use the ODC taxonomy, and
(b) we force it to run a scientific-debugging loop. How much does each one actually buy?

**We rewrote this RQ on 2026-09-15.** The old version lumped both ingredients into one question. They
have wildly different effect sizes, so bundling them hides the strongest result in the study. It is now
two sub-questions:

- **RQ4a** — what does the ODC taxonomy buy, compared to letting the model use its own words?
- **RQ4b** — what does the enforced loop buy, on top of a strong single-call few-shot prompt?

### 2. What we did

Three tiers, all on the **same 257 bugs**:

| Tier | What the model was told |
|---|---|
| `zero-free` | Nothing. No taxonomy, no examples. "What kind of bug is this?" — answer in your own words. |
| `few-open` | The 7 ODC types + Other, a diagnostic tree, and worked examples. One call. |
| `scientific-open` | Same taxonomy, but must run hypothesis → prediction → probe → observation first. |

The `zero-free` data lives in `.dist/study/artifacts_full/` rather than `artifacts_v2`, which is why an
earlier draft thought it was missing. It is not missing: we verified by set intersection that it covers
**exactly the same 257 bugs**, in both evidence modes.

---

## RQ4a — What the ODC taxonomy buys: almost everything

### 3a. What we found

| Tier | Distinct labels used | Label entropy | Same label pre-fix and post-fix? | κ |
|---|---|---|---|---|
| `zero-free` (no taxonomy) | **228** | **7.662 bits** | **18.7%** | **0.184** |
| `few-open` | 6 | 1.421 | 67.7% | 0.437 |
| `scientific-open` | 6 | 1.490 | **73.5%** | **0.577** |

Read the first row carefully. **228 different labels for 257 bugs.** Of those 228, **215 were used
exactly once** (83.7%). The most common free-form label, "Null Pointer Dereference", covers 14 bugs.
Everything else is essentially one label per bug.

The **vocabulary reduction ratio** (the pipeline's own metric, 1 − 7/228) is **0.969**.

And the labels are not even stable. Show the model the same bug twice — once without the fix, once with
it — and it produces the identical label string only **18.7%** of the time.

Here is what that looks like concretely, using bugs from our manual analysis:

| Bug | `zero-free` label, pre-fix | `zero-free` label, post-fix |
|---|---|---|
| Chart_9 | "Improper input validation logic" | "incorrect boundary condition logic" |
| Math_23 | "Logic error in optimization result selection" | "logic error in optimization result tracking" |
| Time_3 | "incorrect state mutation during time arithmetic" | "unnecessary state mutation during zero-value arithmetic" |
| Chart_11 | "Incorrect state management in object comparison" | "incorrect object reference in comparison logic" |

Every pair describes roughly the same thing — and **no pair would ever be counted together** by any
counting program. That is the whole problem in four rows.

One more number: **71 of the 257** free-form labels do not map onto any ODC type under the pipeline's
keyword mapper. Treat that partly as a limitation of the mapper, but it makes the point concrete.

### 4a. What the statistics say

We compared, bug by bug, whether the pre-fix and post-fix labels matched, under each condition, using
McNemar's exact test:

| Comparison | Consistent under A only | Consistent under B only | Exact p |
|---|---|---|---|
| scientific-open vs zero-free | 139 | 6 | **5.4 × 10⁻³⁴** |
| few-open vs zero-free | 126 | 8 | **2.0 × 10⁻²⁸** |

**In plain words:** this is not a marginal effect. A p-value of 5 × 10⁻³⁴ means there is essentially no
chance this difference is luck. This is the strongest statistical result in the entire study.

### 5a. How to explain it to faculty

This is the result that justifies the whole project:

> "People ask why we impose ODC at all, instead of just asking the LLM what kind of bug it is. We ran
> that experiment. Without a taxonomy, the model produced 228 distinct labels for 257 bugs — 215 of
> them used exactly once. Worse, the labels are not reproducible: shown the same bug twice, the model
> produced the identical label only 18.7% of the time, against 73.5% with the taxonomy. So free-form
> LLM labels cannot be counted, cannot be compared across projects, and cannot support the kind of
> process feedback ODC exists to provide. Imposing the taxonomy is what makes the output usable at all,
> and the difference is significant at p < 10⁻³³."

### 6a. What we can and cannot claim

| We CAN claim | We CANNOT claim |
|---|---|
| Without a taxonomy, LLM labels are near-unique per bug (228/257) and unstable (18.7% reproducible) | That the free-form labels are *wrong* — many are sensible descriptions; they are just not aggregatable |
| Taxonomy grounding is the dominant component, p < 1e-33 | That 0.969 vocabulary reduction is a quality measure; it measures constraint, not correctness |
| This is a quantitative justification for using ODC rather than free-form LLM output | That the 71 "Unknown" mappings prove those bugs escape ODC — that is a limit of our keyword mapper too |

---

## RQ4b — What the scientific loop buys: real but modest

### 3b. What we found

| Metric | `few-open` | `scientific-open` |
|---|---|---|
| Pre-fix matches post-fix (strict) | 67.7% | **73.5%** |
| Cohen's κ | 0.437 | **0.577** |
| Matches the post-fix consensus (the 197 bugs where both post-fix runs agree) | 75.6% | **79.2%** |
| Projects where it has the higher κ | 0 of 5 | **5 of 5** |

### 4b. What the statistics say

Two tests that disagree in an instructive way — report both:

- **Per-project sign test: consistent.** Scientific has the higher κ in all five projects (Chart 0.672
  vs 0.349, Lang 0.546 vs 0.497, Math 0.603 vs 0.537, Mockito 0.499 vs 0.272, Time 0.480 vs 0.212).
  Winning 5 out of 5 gives a one-sided p of **0.031**. The direction is real and not cherry-picked.
- **Per-bug McNemar test: not significant.** Counting individual bugs, 46 were consistent under
  scientific only and 31 under few-shot only. Exact **p = 0.110**. At n = 257 we are underpowered to
  call this per bug.

**In plain words:** the loop helps, in every project, in the same direction — but the size of the help
is small enough that 257 bugs cannot prove it bug-by-bug. Say exactly that. It is an honest result and
reviewers respect it more than an overstated one.

**And there is a concrete reason the effect is small — we measured it.** The loop often never runs:

- **31** scientific pre-fix runs (and 82 post-fix runs) finished at turn 1 with **zero probes**.
- The class Defects4J marks as modified is in the evidence store for only **105 / 257** bugs, and a
  pre-fix probe actually retrieved it for only **55 / 257**.
- Agreement by number of probes: 0 probes → 87.1% (n=31); 1 → 66.7% (n=84); 2 → 71.9% (n=57); 3+ →
  76.5% (n=85). More probes does **not** mean better agreement — probe count tracks how hard the bug
  is, it does not cause a better answer.

### 5b. How to explain it to faculty

> "The enforced loop improves agreement with the fix-aware reference in every one of the five projects
> — 73.5% versus 67.7% overall, and a higher κ in 5 of 5 projects, which a sign test puts at p = 0.031.
> But per bug the improvement is not statistically significant at our sample size (McNemar p = 0.110),
> and we are explicit about why: the loop is frequently starved. In 152 of 257 bugs the buggy class is
> not even in the evidence store, so there is nothing useful for a probe to retrieve. Improving
> evidence collection, not the loop itself, is the obvious next lever."

**The likely attack:** *"You are claiming your loop works based on an insignificant result."*

**The answer:** we are not. We claim a **consistent direction across five projects** (p = 0.031 on the
sign test) and we openly report the non-significant per-bug test. And we identified the mechanism
limiting the effect and quantified it.

### 6b. What we can and cannot claim

| We CAN claim | We CANNOT claim |
|---|---|
| Scientific beats few-shot in all 5 projects, sign test p = 0.031 | That the loop significantly improves per-bug agreement — McNemar p = 0.110 |
| The loop is under-exercised: buggy class missing for 152/257 bugs | That more probing causes better answers — the probe-count data says otherwise |
| Evidence coverage, not loop design, is the current bottleneck | Anything about the loop's ceiling, since we have never run it with full evidence |

---

# RQ5 — Does seeing the fix change how a bug gets classified?

### 1. What the RQ asks

Take the same bug. Classify it once without the fix, once with it. How often does the label change, and
is there a pattern to the changes?

This is the RQ the whole pre-fix/post-fix design exists to answer, and it is our strongest.

### 2. What we did

Every one of the 257 bugs was classified in both modes, under both strategies. We then compared, per
bug, per project, and per type pair.

### 3. What we found

**How much the label moves:**

- Scientific: labels changed on **68 / 257 bugs (26.5%)**, κ = 0.577.
- Few-shot: labels changed on **83 / 257 bugs (32.3%)**, κ = 0.437.

**But the overall distribution barely moves.** Total variation distance between the pre-fix and post-fix
distributions is only **0.07** (scientific) and **0.12** (few-shot). Individual labels shuffle; the
aggregate picture stays the same. That distinction is the key to Section 7.

**Where the movement happens** (scientific, 68 drifts):

| Type pair | Drifts | Direction split |
|---|---|---|
| Checking ↔ Algorithm/Method | **32** | 17 one way, 15 the other |
| Algorithm/Method ↔ Assignment/Initialization | 11 | 9 + 2 |
| Checking ↔ Assignment/Initialization | 7 | 5 + 2 |

**50 of 68 drifts (74%) stay inside those three types** — and those are the same pairs the ODC
literature documents human raters confusing (Section 6).

**Three patterns that hold across all five projects:**

1. **The two strategies always agree more in post-fix than in pre-fix. 5 of 5 projects, no exceptions.**
   Chart 73.1% vs 65.4%, Lang 78.7% vs 68.9%, Math 75.5% vs 71.7%, Mockito 76.3% vs 68.4%, Time 80.8%
   vs 53.8%. The *direction* is completely consistent. The *size* ranges from 3.8 to 27 points — so
   never quote one number as "the" effect.
2. **Algorithm/Method is an attractor category in every project**, but what it gets confused *with*
   depends on the project: Checking in Lang/Time/Math (the three biggest), Assignment/Initialization in
   Chart, and a diffuse spread including Interface/O-O Messages in Mockito — which makes sense, since a
   mocking framework has far more interface-heavy code. Report both halves, not just the punchier
   "same pair every time" version that only looked true after two projects.
3. **The model's own confidence signals are useless as a filter.** In 1,028 classifications there were
   11 `needs_human_review` flags and 0 low-confidence flags. Chart_26 was flagged for review *while*
   stating 0.9 confidence. Chart_11 made 4 probes, none of which reached the code, and still concluded
   with confidence 1.0. Do not build any filtering story on these fields.

### 4. What the statistics say

**Per-project reliability, with bootstrap confidence intervals** (2,000 resamples, because n = 26 for
Chart and Time is small enough that a bare κ would be misleading):

| Project | n | Scientific strict | Scientific κ [95% CI] | Few-shot strict | Few-shot κ [95% CI] |
|---|---|---|---|---|---|
| Chart | 26 | 80.8% | 0.672 [0.419, 0.906] | 57.7% | 0.349 [0.105, 0.616] |
| Lang | 61 | 73.8% | 0.546 [0.360, 0.714] | 73.8% | 0.497 [0.293, 0.692] |
| Math | 106 | 75.5% | 0.603 [0.472, 0.726] | 74.5% | 0.537 [0.392, 0.671] |
| Mockito | 38 | 65.8% | 0.499 [0.285, 0.701] | 52.6% | 0.272 [0.060, 0.485] |
| Time | 26 | 69.2% | 0.480 [0.159, 0.754] | 57.7% | 0.212 [−0.138, 0.530] |

Notice how wide the small-project intervals are — Time's few-shot κ CI runs from −0.138 to 0.530, which
includes zero. **That is exactly why we report intervals.** Quoting "Time κ = 0.212" alone would be
misleading; the honest statement is that Time's few-shot reliability is not distinguishable from chance
at n = 26.

**The ceiling result, again, because it matters here too:** with the fix visible to both, scientific and
few-shot still disagree on 23.3% of bugs (76.7% match, κ = 0.633). Some of what we call "drift" is not
about the fix at all — it is irreducible ambiguity in ODC itself.

### 5. How to explain it to faculty

> "Just over a quarter of labels change when the fix becomes visible — 26.5% under our default
> condition. But three quarters of those changes stay inside the same three ODC types, which are
> exactly the types the ODC literature documents human raters confusing. And the overall type
> distribution barely moves at all: total variation distance of 0.07. So the effect of the oracle is
> real at the level of individual bugs and negligible at the level of aggregate statistics — which is
> the level ODC was designed to operate at."

**Back it with the literature, because it lines up almost perfectly.** Henningsson & Wohlin (2004) had
8 humans classify faults from *written descriptions only* and got κ = 0.16. A 2020 JSS study of NoSQL
defects, where raters had *full code and change context*, reports κ = 0.93. Human agreement on ODC type
depends enormously on how much information the rater has — which is exactly our pre-fix vs post-fix
design, restated. Our drift concentrating in the Assignment/Algorithm/Checking triangle is the same
phenomenon those studies report.

**Back it with mechanism, from the 13-bug manual analysis.** We can show *why* labels drift, in four
distinct ways:

- **The fix helps:** Time_3, Chart_11 — the post-fix run gets it right where the pre-fix run did not.
- **The fix hurts:** Math_23, Math_17 — the post-fix run relabels based on the *surface form* of the
  patch (a new variable appeared; a branch was added) instead of the definition.
- **The fix is ignored:** Chart_17, Math_90 — the diff was right there in the prompt and the scientific
  run never used it, while few-shot did.
- **The bug report anchors the label:** Math_90's report says "could be fixed by checking that the
  object is Comparable" — and that suggestion becomes the label.

That combination — a solid number, a cross-project pattern, a literature match, and four named
mechanisms — is why RQ5 is our strongest result.

### 6. What we can and cannot claim

| We CAN claim | We CANNOT claim |
|---|---|
| 26.5% of labels change when the fix is visible; 74% of changes stay in the 3 ambiguous types | That the post-fix label is correct and the pre-fix one wrong — neither is verified |
| The aggregate distribution barely moves (TVD 0.07) | That drift is harmless; 9 bugs drift to a genuinely unrelated type |
| Post-fix strategy agreement exceeds pre-fix in 5/5 projects | A single effect size — it ranges 3.8 to 27 points by project |
| Per-project κ, honestly bounded | That Chart or Time κ is precise; n = 26 gives very wide intervals |

---

# Section 6 — Fixing the "experts confuse Algorithm and Checking 80% of the time" claim

**As we have been stating it, this claim is wrong.** It traces back to a real study, but we have the
wrong pair of types and the wrong quantity. The corrected version is actually *more* useful to us.

### Where it comes from: Henningsson & Wohlin (2004)

- **Setup:** 8 people classified 30 faults with an ODC-based scheme, working from **written fault
  descriptions only** — no code.
- **Result:** average pairwise κ was **0.16** ("poor"). Merging the two most-confused classes only
  raised it to 0.24.
- **The most confused pair was Assignment ↔ Algorithm, not Checking ↔ Algorithm.** Their exact words:
  *"The most frequent mix-up is the interchange between AS and AL, in total, 22 of the 28 pairs mixed
  these two classes up a number of times."* 22/28 = **79%** — that is almost certainly where our "80%"
  came from, but it counts **rater pairs**, not classifications, and it is about **Assignment ↔
  Algorithm**.
- Ranking of confusions in their Table 6: Assignment–Algorithm 184 occasions; Interface–Algorithm 77;
  **Checking–Algorithm 68 (third)**; Assignment–Interface 59; Assignment–Checking 49.
- **Their own conclusion:** the impoverished fault description was the likely cause of the low
  agreement. They recommend giving raters **source code and change information**.

### The counter-evidence we must cite alongside it

- **El Emam & Wieczorek (1998):** found the ODC-derived scheme "in general repeatable" — with raters
  classifying at detection time, **with code available**.
- **NoSQL ODC study (JSS 2020):** reports **κ = 0.93** for Defect Type. Important caveat to state: that
  was a *verification* of an existing classification, not blind independent labelling.

### Why the corrected version helps us more

The real finding is not "ODC is unreliable". It is: **human agreement on ODC type depends on how much
information the rater has.** Descriptions only → κ 0.16. Full code and change context → κ 0.93.

That is our entire pre-fix / post-fix design, restated by two independent groups. It explains why our
drift concentrates in the Assignment/Algorithm/Checking triangle. And it is the literature
justification for treating the post-fix run as the better-informed reference standard in RQ3.

### Claims in our own docs to remove or source

- `docs/eval_defence.md` and `docs/Research Paper Roadmap_ Defect Classification.md` say *"Chillarege
  et al. (1992): human inter-rater agreement ~70–80%"*. We could not find it in our ODC v5.2 reference
  (`docs/odc_doc.md`), and Chillarege's own concept article reports no agreement figures at all.
  **Remove it unless someone finds a page-level citation.**
- `docs/eval_defence.md` says *"Typical ODC studies: κ 0.60–0.80"* with no source. Replace it with the
  three concrete studies above.

---

# Section 7 — Fixing the "pre-fix agrees with post-fix, so pre-fix is enough" argument

The strong version of this argument will get attacked, for two good reasons. Both are avoidable by
wording, not by dropping the argument.

**Problem 1: agreement is not correctness.** Chart_17 and Math_90 agree perfectly between pre-fix and
post-fix and are both wrong. The post-fix run is a better-informed second rater, not a validator of
truth. Never write "agreement proves correctness"; write "reproduces the fix-aware reference".

**Problem 2: ODC defect type is not a work-assignment scheme.** ODC was built to give process feedback
from **distributions** of defect types, not to route individual bugs to individual developers. "Right
type → right developer" would need its own evidence and we have none. Do not claim it.

### The version to actually use

- **At the aggregate level — which is ODC's intended use.** Pre-fix classifications produce almost the
  same type distribution as fix-aware ones (TVD **0.07** under scientific). So early, pre-fix ODC
  analytics are viable *for exactly the purpose ODC was designed for*.
- **The disagreements are the known-ambiguous ones.** 74% of drifts stay inside the type triangle where
  humans also disagree, and only **3.5% of bugs** are genuinely unrelated. Drift is a documented
  property of ODC, not random noise from our pipeline.
- **Offer a confidence tier for triage.** All four runs agree on **130 / 257 bugs (50.6%)** — that is a
  high-confidence tier you could act on. And on the 197 bugs where both post-fix runs agree with each
  other, the scientific pre-fix run matches that consensus **79.2%** of the time.
- **Describe post-fix correctly.** A better-informed reference rater. Not an oracle for truth.

---

# Section 8 — Is the 13-bug manual analysis worth presenting?

**For explaining the pipeline to faculty, and as the "why" behind RQ5: yes, strongly.** It is the only
place we can show what the pipeline actually *does*, rather than what it scores:

| Bug | What it demonstrates |
|---|---|
| Chart_9 | The loop working exactly as designed |
| Chart_11 | The loop starved — 4 probes, none reached the code, confidence still 1.0 |
| Time_3, Math_104 | Right mechanism, wrong label — it predicted the exact fix, then labelled by context |
| Chart_17, Math_90 | Confident, consistent, and wrong — never ran an experiment at all |
| Math_23 | The oracle actively hurting |
| Chart_7 | Right label, wrong reason — the mechanism it described was invented |

**As a measure of accuracy: no.** The 13 bugs were deliberately picked to show failure modes, and the
"ground truth" is one person's reading. `analysis_v2/manual_analysis/README.md` already says this
("proposals for the human reviewers to confirm or overrule") — keep that framing.

**Three things that would make it count for more:**

1. Have at least two team members label each bug **from the fix diff, before reading any model output**,
   and report our own κ.
2. Present it as a qualitative study of mechanisms, not as an accuracy estimate.
3. Grade the **label** and the **reasoning** separately. Chart_7 and Math_17 show the two can diverge —
   and a label-only metric is structurally blind to that. This is the single strongest argument for
   doing manual analysis at all.

---

# Section 9 — Threats to validity (disclose all of these)

1. **A real bug in our probe implementation.** `execute_probe` matches class names by substring
   (`argument in s.class_name`, `d4j_odc_pipeline/agent.py`). So asking for
   `snippet(org.apache.commons.math3.dfp.Dfp)` returns **DfpTest**, and `snippet(Gamma)` returns
   **GammaTest**. The model then reasons as if it had seen production code when it had seen a test
   (Math_17, Math_104, Time_3, Math_23). **Fix this before any rerun.** It weakens RQ4b specifically.
2. **Evidence coverage is poor.** The class Defects4J marks as modified is missing from `context.json`
   for **152 of 257 bugs**. For assertion-failure bugs the buggy method is often neither in a stack
   frame nor among the most-executed classes. This caps what the loop can contribute and is the main
   reason RQ4b's effect is modest.
3. **One model.** Everything uses gemini-3.1-flash-lite-preview. The artifact scheme already supports a
   model axis (`docs/condition_model.md` §5), so running a second model on a subset would address this
   cheaply.
4. **Possible memorization.** Defects4J bugs and their fixes are public and well known. The model may
   have seen them.
5. **Bug-report anchoring.** When a bug report proposes a fix, that proposal tends to become the label
   (Math_90 is the clearest case).
6. **Statistical limitations, and what we did about each.** Sparse cells in RQ1 → replaced the
   asymptotic chi-squared with a Monte Carlo permutation test. Small per-project n in RQ5 → added
   bootstrap confidence intervals. Near-ceiling L3/L4 in RQ3 → now reported conditional on
   disagreement.
7. **Closure is not included.** 257 bugs from 5 projects, not the full benchmark. Collection is ongoing.
   Say so plainly.

---

# Section 10 — What to do next, in priority order

1. **Fix the substring match** in the snippet probe (`agent.py::execute_probe`). Cheap, and it is a
   genuine bug regardless of the paper.
2. **Write RQ4 in the new two-part shape** (RQ4a taxonomy, RQ4b loop). The `zero-free` data already
   exists for all 257 bugs — nothing to run.
3. **Rewrite the RQ3 accuracy section** — name the post-fix arm as the reference standard, lead with L1
   and κ, and report L3/L4 only conditional on disagreement.
4. **Optional but highest remaining value:** random-sample human ground truth (60–80 bugs, 2 blind
   raters, report κ, adjudicate disagreements). Upgrades RQ3 from "reproduces the reference" to "is
   correct", and strengthens RQ5.
5. **Correct the literature claims** in `docs/eval_defence.md` and the roadmap doc — see Section 6.
6. **Do not run** `scientific-closed` / `few-closed` (the escape rate is 0, so there is nothing to
   measure) and do not re-run `zero-free` (it already exists). Record both as deliberate decisions in
   the paper, not as gaps.

**No further Defects4J evidence collection is needed for any of the five RQs as currently worded.**

---

# Sources

- K. Henningsson and C. Wohlin, "Assuring Fault Classification Agreement: An Empirical Evaluation,"
  ISESE 2004, pp. 95–104. [PDF](https://www.wohlin.eu/isese04.pdf) ·
  [IEEE Xplore](https://ieeexplore.ieee.org/document/1334897)
- K. El Emam and I. Wieczorek, "The Repeatability of Code Defect Classifications," ISSRE 1998,
  pp. 322–333. [IEEE Xplore](https://ieeexplore.ieee.org/document/730897/)
- "Using Orthogonal Defect Classification to Characterize NoSQL Database Defects," Journal of Systems
  and Software, 2020. [Preprint PDF](https://eden.dei.uc.pt/~cnl/papers/2020-jss-odc-joao-v64-submitted.pdf) ·
  [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0164121219302250)
- R. Chillarege et al., "Orthogonal Defect Classification: A Concept for In-Process Measurements,"
  IEEE TSE 18(11), 1992. [ACM DL](https://dl.acm.org/doi/10.1109/32.177364)
- Chillarege Inc., ODC concept article. [Link](https://www.chillarege.com/articles/odc-concept.html)
- S. Kang, B. Chen, S. Yoo and J.-G. Lou, "A Quantitative and Qualitative Evaluation of LLM-Based
  Explainable Fault Localization" (AutoSD), EMSE 2024 — the loop-iteration ordering our `scientific`
  strategy implements.
- F. Thung, D. Lo and L. Jiang, "Automatic Defect Categorization," WCRE 2012.
  [ACM DL](https://dl.acm.org/doi/10.1109/WCRE.2012.30) (the 77.8% figure cited in our docs was not
  re-verified here)

---

## Where the numbers come from

All figures were recomputed from the `classification.*.json` artifacts using the pipeline's own
functions — `compare_classifications`, `compute_cohens_kappa`, `compute_taxonomy_grounding_metrics`,
`family_for`. The five workbooks in `analysis_v2/` were cross-checked against the artifacts: **0
mismatches** across all 257 bugs and all 4 conditions, so the workbooks and the raw artifacts agree
exactly.

Related documents: `docs/RQs_JSS.md` (the RQ wording, canonical),
`.dist/study/reports/artifacts_v2/interesting_findings.md` (the running per-project notes),
`analysis_v2/manual_analysis/` (the 13-bug shortlist), `docs/JSS_HANDOFF.md` (paper-drafting entry
point).
