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
| --- | --- |
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
| --- | --- | --- |
| **RQ1** — what types of bugs are these, and does it differ by project? | Defensible | 98.4% of bugs are three types, and the mix does not differ significantly between projects |
| **RQ2** — do the 7 ODC types cover everything? | Defensible (a clean empirical result) | We offered an "Other" escape 1,028 times. It was used **0 times** |
| **RQ3** — how accurate is the pipeline? | Defensible, once we name our reference standard honestly | Pre-fix reproduces the fix-aware label 73.5% of the time, and is *unrelated* to it on only 3.5% of bugs |
| **RQ4** — what does each part of the pipeline contribute? | Defensible, split in two | The scientific loop significantly beats few-shot on chance-corrected agreement (Δκ = 0.141, CI [0.037, 0.247], p ≈ 0.012) and halves cross-project variance. Taxonomy grounding is the control condition |
| **RQ5** — does seeing the fix change the label? | Strongest RQ | 26.5% of labels change, 74% of those changes stay inside the same three ambiguous types |

**Two problems in our own writing — both now fixed (2026-09-15):**

1. The "experts confuse Algorithm and Checking 80% of the time" claim, and the unsourced
   "Chillarege: 70–80% inter-rater agreement" figure behind it. ✅ Searched, found to be
   misattributed, and replaced across six locations in four files with five properly sourced
   studies — **Section 6**.
2. Sentences that treated *agreement* as *correctness*. ✅ Rewritten in `docs/eval_defence.md`
   (Pillar 1 and talking point 2) — **Section 7**.

Sections 6 and 7 now record what was wrong, what replaced it, and the wording to use from here on.

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
| --- | --- | --- | --- | --- |
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
| --- | --- | --- | --- | --- | --- |
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
| --- | --- | --- | --- | --- |
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
| --- | --- |
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
| --- | --- |
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
| --- | --- |
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
| --- | --- | --- | --- |
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
| --- | --- | --- |
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
| --- | --- |
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

**We rewrote this RQ on 2026-09-15**, into two sub-questions that carry very different weight:

- **RQ4a** — what does the ODC taxonomy buy, compared to letting the model use its own words?
  *This is the control condition.* The answer is large but unsurprising — nobody expects free-form
  labels to aggregate. We report it because a reviewer will ask for the baseline, not because it is
  a discovery. Keep it short.
- **RQ4b** — **what does the enforced scientific loop add on top of a strong few-shot prompt?**
  *This is the real question*, because both arms already have the taxonomy, so the loop is the only
  thing that differs. This is where the contribution of our pipeline actually lives, and it is the
  half that deserves the space.

### 2. What we did

Three tiers, all on the **same 257 bugs**:

| Tier | What the model was told |
| --- | --- |
| `zero-free` | Nothing. No taxonomy, no examples. "What kind of bug is this?" — answer in your own words. |
| `few-open` | The 7 ODC types + Other, a diagnostic tree, and worked examples. One call. |
| `scientific-open` | Same taxonomy, but must run hypothesis → prediction → probe → observation first. |

The `zero-free` data lives in `.dist/study/artifacts_full/` rather than `artifacts_v2`, which is why an
earlier draft thought it was missing. It is not missing: we verified by set intersection that it covers
**exactly the same 257 bugs**, in both evidence modes.

---

## RQ4a — The taxonomy baseline (the control condition, reported briefly)

This is the expected result, and we treat it as such: it establishes that the taxonomy is doing its
job, and it rules out the obvious "why not just ask the LLM?" objection. It is not the finding.

### 3a. What we found

| Tier | Distinct labels used | Label entropy | Same label pre-fix and post-fix? | κ |
| --- | --- | --- | --- | --- |
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
| --- | --- | --- |
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
| --- | --- | --- | --- |
| scientific-open vs zero-free | 139 | 6 | **5.4 × 10⁻³⁴** |
| few-open vs zero-free | 126 | 8 | **2.0 × 10⁻²⁸** |

**In plain words:** this is not a marginal effect. A p-value of 5 × 10⁻³⁴ means there is essentially no
chance this difference is luck. It is the largest p-value gap in the study — but on a comparison
nobody disputed, so treat it as a sanity check that passed, not as a finding. The result that has to
carry RQ4 is the loop comparison below, where both arms already have the taxonomy.

### 5a. How to explain it to faculty — two sentences, then move on

Do **not** dwell on this. It answers an objection; it is not a contribution. Anyone would predict
that free-form labels do not aggregate, and a large p-value on an obvious comparison impresses
nobody. Say it once, plainly, and spend the time on RQ4b:

> "We checked the obvious alternative first. Without a taxonomy the model produced 228 distinct
> labels for 257 bugs, and reproduced its own label across two views of the same bug only 18.7% of
> the time. That output cannot be counted or compared, so taxonomy grounding is a precondition
> rather than a result. The interesting question is what the loop adds once both arms already have
> the taxonomy."

⚠️ **Do not frame RQ4a as "the strongest result in the study."** It is the largest *number*, but a
huge effect on a comparison nobody doubted is weak evidence for our design. The scientific loop is
what we built; that is what has to earn its place.

### 6a. What we can and cannot claim

| We CAN claim | We CANNOT claim |
| --- | --- |
| Without a taxonomy, LLM labels are near-unique per bug (228/257) and unstable (18.7% reproducible) | That the free-form labels are *wrong* — many are sensible descriptions; they are just not aggregatable |
| Taxonomy grounding is a precondition for aggregation, confirmed empirically | That this validates our pipeline design — it validates ODC, which predates us. The loop is our contribution |
| This rules out "why not just ask the LLM?" | That 0.969 vocabulary reduction is a quality measure; it measures constraint, not correctness |
| — | That the 71 "Unknown" mappings prove those bugs escape ODC — that is a limit of our keyword mapper too |

---

## RQ4b — What the scientific loop buys: **the headline of RQ4**

This is the comparison that matters. Both arms have the same model, the same taxonomy, the same
evidence store and the same 257 bugs. The **only** difference is whether the model is forced to run
hypothesis → prediction → probe → observation before committing to a label. Any difference we
measure is attributable to the loop.

### 3b. What we found

| Metric | `few-open` | `scientific-open` | Gain |
| --- | --- | --- | --- |
| Pre-fix reproduces the fix-aware label (strict) | 67.7% | **73.5%** | **+5.8 points** |
| Cohen's κ | 0.437 | **0.577** | **+0.141** |
| Matches the post-fix consensus (197 bugs where both post-fix runs agree) | 75.6% | **79.2%** | +3.6 points |
| Projects where its κ is higher | 0 of 5 | **5 of 5** | — |
| Worst-project κ | 0.212 (Time) | **0.480** (Time) | **2.26× higher** |
| Spread of κ across projects (sd) | 0.141 | **0.079** | **44% tighter** |

### 4b. What the statistics say

**The primary test: the loop's improvement in κ is statistically significant.**

A paired bootstrap over the 257 bugs (5,000 resamples, both conditions resampled on the same bugs)
gives:

> **Δκ = 0.141, 95% CI [0.037, 0.247], two-sided p ≈ 0.012.**

The interval excludes zero. **The enforced loop produces a significantly higher chance-corrected
agreement with the fix-aware reference than a strong few-shot prompt does.**

**A second, independent check agrees on direction.** Scientific has the higher κ in **all five**
projects — Chart +0.323, Time +0.268, Mockito +0.227, Math +0.066, Lang +0.049. A sign test on 5/5
gives one-sided **p = 0.031**.

**Report the two tests that do *not* reach significance, and explain why — this is what makes the
result credible rather than cherry-picked:**

| Test | Result | Why it differs |
| --- | --- | --- |
| McNemar on raw per-bug agreement flips | scientific-only 46, few-only 31, **p = 0.110** | Counts raw agreement flips and ignores chance correction. Few-shot assigns Algorithm/Method to 156 of 257 bugs, which inflates its *expected* agreement — so its raw agreement is worth less than scientific's. κ prices that in; McNemar does not. |
| McNemar on matching the post-fix consensus | sci-only 26, few-only 19, **p = 0.371** | Restricted to the 197 consensus bugs, and again raw-count based. Underpowered. |

**Why κ is the right primary measure here, and why this is not post-hoc selection:** Cohen's κ was
already **Tier 4 of our own four-level framework** (`docs/eval_defence.md` §2), fixed before this
comparison was run. It is the metric the framework designates for exactly this question. We did not
go looking for a test that gave a better number — we report all four tests, and explain the
mechanism that makes them differ.

**Where the loop actually earns its keep: it is variance reduction, not a uniform lift.**

Look at the per-project gains. Scientific is barely ahead where few-shot is already strong (Lang
+0.049, Math +0.066) and far ahead where few-shot collapses (Chart +0.323, Time +0.268, Mockito
+0.227). Few-shot's κ ranges from 0.212 to 0.537; scientific's from 0.480 to 0.672 — **half the
spread (sd 0.079 vs 0.141)**. At Time, few-shot's κ confidence interval [−0.138, 0.530] includes
zero, i.e. its reliability there is indistinguishable from chance; scientific's is 0.480.

**The claim to make is therefore about a floor, not a mean:** the loop does not make easy bugs
easier. It stops the classifier falling apart on the projects where a single-shot prompt has nothing
to latch onto. That is a more useful property for a production triage tool than a small average gain,
and it is exactly what an evidence-gathering loop *should* do.

**A corroborating signal from RQ1:** the same asymmetry appears in the label distribution. Few-shot's
per-project type mix is near-significantly project-dependent (Monte Carlo p = 0.058), while
scientific's is clearly not (p = 0.381). Two independent measurements, same conclusion —
**scientific is the more project-independent condition.**

### The honest limitation: the loop is under-exercised, so this is a floor on its effect

We measured why the gain is +5.8 points and not larger:

- **31** scientific pre-fix runs (and 82 post-fix runs) concluded at turn 1 with **zero probes**.
- The class Defects4J marks as modified is in the evidence store for only **105 / 257** bugs, and a
  pre-fix probe actually retrieved it for only **55 / 257**.
- Agreement by probe count: 0 probes → 87.1% (n=31); 1 → 66.7% (n=84); 2 → 71.9% (n=57); 3+ → 76.5%
  (n=85). More probing does **not** cause better agreement — probe count tracks bug difficulty.

Frame this as a floor, not an excuse: **we measured a significant improvement even though the loop
could not reach the buggy code in 59% of bugs.** Fixing evidence collection is the obvious next
lever, and it can only raise this number.

### One counter-signal we must report: few-shot is better *with* the oracle

In the 13-bug manual analysis, scored against the manually-read ground truth:

| Condition | Matches manual ground truth |
| --- | --- |
| Scientific pre-fix | **6 / 13** |
| Few-shot pre-fix | 4 / 13 |
| Scientific post-fix | 6 / 13 |
| Few-shot post-fix | **11 / 13** |

Scientific is better in the pre-fix setting (the one that matters operationally), but few-shot is
far better once the fix diff is in the prompt. That is consistent with the mechanism we documented
in Chart_17 and Math_90: **the scientific run commits to its own chain of reasoning and under-uses
the oracle when it is handed one.** Few-shot, having no reasoning to defend, just reads the diff.

⚠️ n = 13, adversarially selected to show failure modes, single rater. Do **not** treat this as an
accuracy measurement. Report it as a mechanism observation, and note that it is a limitation of the
loop worth naming before a reviewer names it.

### 5b. How to explain it to faculty

> "Both arms use the same model, the same taxonomy and the same evidence. The only difference is
> whether the model must run an explicit hypothesis-and-probe loop before answering. The loop raises
> chance-corrected agreement with the fix-aware reference from κ 0.437 to 0.577 — a paired bootstrap
> puts that difference at 0.141 with a 95% interval of 0.037 to 0.247, so it excludes zero, and
> scientific has the higher κ in all five projects independently.
>
> What is more interesting than the average is *where* the gain sits. Scientific is barely ahead on
> the projects where few-shot already works, and far ahead where few-shot collapses — at Time,
> few-shot's reliability is statistically indistinguishable from chance while scientific reaches
> 0.480. Across projects, scientific's spread is half of few-shot's. So the loop is not buying a
> uniform accuracy lift; it is putting a floor under the classifier on the hard projects. And we
> measured that while the loop could not even reach the buggy class in 59% of bugs, so this is a
> lower bound on what it can do."

**The likely attack:** *"Your McNemar test says p = 0.110. You are reporting the test that suits you."*

**The answer — this is why we report all four.** The two tests measure different things. McNemar
counts raw agreement flips and ignores the fact that few-shot concentrates 156 of 257 labels on one
type, which inflates the agreement it would get by chance. Cohen's κ corrects for exactly that, and
κ was already Tier 4 of our published four-level framework before this comparison was run. We
present the bootstrap κ result as primary, the sign test as independent corroboration, and both
McNemar results openly, with the mechanism that explains the difference.

**The second likely attack:** *"5.8 points is small."*

**The answer:** the average is small; the worst case is not. Few-shot's weakest project sits at
κ 0.212 with a confidence interval containing zero. Scientific's weakest sits at 0.480. For a triage
tool, the number that matters is how badly it can fail, not how well it does on the easy projects.

### 6b. What we can and cannot claim

| We CAN claim | We CANNOT claim |
| --- | --- |
| The loop significantly improves chance-corrected agreement: Δκ = 0.141, CI [0.037, 0.247], p ≈ 0.012 | That it improves raw per-bug agreement significantly — McNemar p = 0.110. Report both |
| Scientific has the higher κ in 5 of 5 projects (sign test p = 0.031) | That any single project's advantage is significant on its own — the per-project CIs overlap |
| The loop halves cross-project variance (sd 0.079 vs 0.141) and more than doubles the worst-project κ | That it helps uniformly — on Lang and Math the gain is near zero |
| This is a **floor**: measured while the loop could not reach the buggy class in 59% of bugs | Anything about the loop's ceiling — we have never run it with complete evidence |
| Scientific is the more project-independent condition (corroborated by RQ1's p = 0.381 vs 0.058) | That scientific is better in every setting — with the oracle visible, few-shot beat it 11/13 vs 6/13 on the manual sample |

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
| --- | --- | --- |
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
| --- | --- | --- | --- | --- | --- |
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
| --- | --- |
| 26.5% of labels change when the fix is visible; 74% of changes stay in the 3 ambiguous types | That the post-fix label is correct and the pre-fix one wrong — neither is verified |
| The aggregate distribution barely moves (TVD 0.07) | That drift is harmless; 9 bugs drift to a genuinely unrelated type |
| Post-fix strategy agreement exceeds pre-fix in 5/5 projects | A single effect size — it ranges 3.8 to 27 points by project |
| Per-project κ, honestly bounded | That Chart or Time κ is precise; n = 26 gives very wide intervals |

---

# Section 6 — ✅ FIXED: the "experts confuse Algorithm and Checking 80% of the time" claim

**Status: corrected across the repo on 2026-09-15.** We searched for the source. It does not exist
as stated — but the underlying point is real, and the correctly sourced version is stronger for us.

**Canonical evidence table: `docs/eval_defence.md` §1 Pillar 2.** That is the single place to update.
This section records what we searched and what we concluded.

### What we checked before removing the claim (2026-09-15)

The claim was *"Chillarege et al. (1992): human inter-rater agreement ~70–80%."* We searched:
Chillarege et al. (1992) IEEE TSE 18(11); the Chillarege Inc. ODC concept article; Chillarege's
"ODC for Process Measurement, Analysis and Control"; the IBM ODC v5.2 reference we hold locally
(`docs/odc_doc.md`); and the Wikipedia ODC article.

**None of them reports an inter-rater agreement figure.** The process-control paper acknowledges
classification is "a human process, and is subject to the usual problems of human error, confusion"
but offers only procedural mitigations, never a number. The only quantitative claim on the
Wikipedia page is that a trained person can classify a defect in under 3 minutes.

So the attribution is wrong. **But we do need this argument**, and there are five real studies that
support it better than one disputed percentage would.

### The finding that replaces it

Agreement on ODC classification is **evidence-dependent**, not fixed:

| Evidence the rater had | Study | Agreement |
| --- | --- | --- |
| Fault **descriptions only** | Henningsson & Wohlin (2004), 8 raters, 30 faults | mean pairwise **κ = 0.16** |
| Report **text only** | Hernández-González et al. (2018), 5 annotators, 962 + 675 defects | majority of 5 reached on only **481/962** and **394/675** |
| **Code available** | El Emam & Wieczorek (1998) | "in general repeatable" (no κ recovered — do not quote one) |
| Full repository context | Rahman & Farhana (2020), COVID-19 projects | **72.7% / κ 0.70** (open coding), 95.1% / κ 0.93 (closed) — ⚠️ verify against PDF |
| Full code + change | NoSQL ODC study (JSS 2020) | **κ = 0.93** (a verification step, not blind labelling) |

**Why this is better than the old claim.** The literature's own explanation for why human raters
disagree — insufficient evidence — **is our experimental variable**. The old sentence merely excused
our error rate. This one predicts it. It also explains why our drift concentrates in the
Assignment / Algorithm / Checking triangle, and it is the literature justification for treating the
post-fix arm as the better-informed reference standard in RQ3.

Note in passing: Rahman & Farhana's 72.7% shows the 70–80% band **is** reachable in real ODC work —
so whoever wrote the original sentence was not inventing the magnitude, only the attribution.

### Where the "80%" actually came from

It is a garbled reading of Henningsson & Wohlin (2004), and both halves of our version were wrong:

- **Wrong pair.** Their most-confused pair was **Assignment ↔ Algorithm**, not Checking ↔ Algorithm.
  Exact words: *"The most frequent mix-up is the interchange between AS and AL, in total, 22 of the
  28 pairs mixed these two classes up a number of times."*
- **Wrong unit.** 22/28 = 79% counts **rater pairs**, not bugs or classifications.
- Their Table 6 ranks confusions by occasions: Assignment–Algorithm 184; Interface–Algorithm 77;
  **Checking–Algorithm 68 (third)**; Assignment–Interface 59; Assignment–Checking 49.
- Their own conclusion: the impoverished fault description caused the low agreement. They recommend
  giving raters **source code and change information** — which is our post-fix arm.

⚠️ **Never write "experts confuse Algorithm and Checking about 80% of the time."** A reviewer who
opens the cited paper finds both errors in under a minute.

### What was fixed, and where — ✅ 2026-09-15

The unsourced claims were found in **five** places, not just `eval_defence.md`. All five are now
corrected, each with a visible correction banner so nobody reintroduces the old number:

| File | What it said | Status |
| --- | --- | --- |
| `docs/eval_defence.md` §1 Pillar 2 | "Chillarege et al. (1992): human inter-rater agreement ~70–80%" and "Typical ODC studies: κ 0.60–0.80" | ✅ Replaced with the Henningsson / El Emam / NoSQL / Thung table, plus an explicit "never write 'Algorithm and Checking 80%'" warning |
| `docs/eval_defence.md` §6 talking point 1 | "Even human ODC experts disagree 20-30% of the time" | ✅ Replaced with our measured ~77% two-strategy ceiling |
| `docs/Research Paper Roadmap_ Defect Classification.md` | "Chillarege's foundational work … peaks at 70% to 80%" | ✅ Rewritten around the evidence-dependence finding (κ 0.16 → 0.93) |
| `d4j_odc_pipeline/comparison.py` module docstring | "Chillarege et al. (1992) — ODC inter-rater disagreement is expected (~20-30%)" | ✅ Replaced with the real four references |
| `d4j_odc_pipeline/comparison.py` insight text (~line 146) | "Even expert human classifiers disagree on 20-30% of bugs (Chillarege 1992)" — **this string was being written into generated reports** | ✅ Replaced with the Henningsson κ 0.16 finding and the correct confusion pair |
| `docs/classification_engine_plan.md` (stale doc) | "κ vs the ~20–30% human-disagreement ceiling from ODC literature" | ✅ Replaced with the measured ceiling |

Also corrected while in there: the AutoSD citation was "Kang, S., Yoo, S., & Ryu, D. (2023)" in
`eval_defence.md` and `comparison.py` — wrong authors and wrong year. It is **Kang, Chen, Yoo & Lou,
EMSE 2024**.

⚠️ **One instance was deliberately NOT fixed:**
`iut_submissions/presentation/generate_presentation.py:736` cites "Kang et al. (2023)". That
directory is **frozen** (pre-defense deliverables, exactly as submitted) — per `CLAUDE.md` we never
edit anything under it. Recorded here for the record; do not propagate that citation into new work.

---

# Section 7 — ✅ FIXED: the "agreement means correctness" framing

**Status: corrected in `docs/eval_defence.md` on 2026-09-15**, in two places:

| Location | What it said | Now |
| --- | --- | --- |
| §1 Pillar 1 | "Both classifications are *correct from their evidence perspective*" | "Each classification is reasonable given the evidence that produced it", plus a warning box citing Chart_17 / Math_90 |
| §6 talking point 2 | "both are correct, but they may name the condition differently" | "two evidence positions, not two truths" |

The rest of this section is the standing guidance — the two attacks and the wording that survives
them. Both are avoidable by wording, not by dropping the argument.

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
| --- | --- |
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
