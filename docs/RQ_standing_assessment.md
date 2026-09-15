# RQ Standing Assessment: can we defend each RQ with `artifacts_v2`?

> **Date:** 2026-09-15
> **Data:** `.dist/study/artifacts_v2/` only. The five projects are Chart (26), Lang (61), Math (106), Mockito (38) and Time (26), for **257 bugs**. Closure is excluded.
> **Conditions present:** `scientific-open` and `few-open`, each run in prefix and postfix, giving 1,028 classifications.
> **Model:** gemini-3.1-flash-lite-preview.
> **RQ wording:** `docs/RQs_JSS.md`.
> **Related:** `analysis_v2/*.xlsx` (per-project workbooks) and `analysis_v2/manual_analysis/` (the 13-bug manual shortlist).
>
> The numbers below were recomputed directly from the artifacts using the pipeline's own `compare_classifications` and `compute_cohens_kappa` (`d4j_odc_pipeline/comparison.py`). The Excel labels match the artifact labels exactly (0 mismatches).

## Verdict in one line

**Not doomed, but not every RQ is defensible as currently worded.**
- **RQ1** and **RQ5** are defensible now.
- **RQ2** is weak but honest.
- **RQ3** is not defensible as worded, because we have no ground truth.
- **RQ4** is mostly unanswerable from v2, because its baseline condition was never run.

Two of the arguments we planned to use (the "80% expert confusion" claim, and "prefix = postfix means prefix is enough for triage") need correcting before a reviewer or faculty member finds the problem.

| RQ | Standing | Short reason |
|---|---|---|
| RQ1: type distribution across projects | ✅ Defensible (descriptive) | Distribution is clear; no significant difference between projects |
| RQ2: taxonomy coverage | 🟡 Weak but honest | 0 "Other" escapes, but no closed run to compare against |
| RQ3: accuracy (4-level framework) | ❌ Not defensible as worded | No human ground truth; two of the four levels are near chance |
| RQ4: component contribution | ❌ Mostly not answerable | No `zero-free` baseline in v2; scientific vs few-shot not significant |
| RQ5: prefix/postfix divergence | ✅ Strongest RQ | Magnitude and pattern are clear and match the human-confusion literature |

---

## RQ1: Bug type distribution across projects

**Standing: ✅ defensible, as a descriptive result.**

### Overall distribution

| Type | Sci prefix | Few prefix | Sci postfix | Few postfix |
|---|---|---|---|---|
| Checking | 121 (47.1%) | 79 | 113 | 93 |
| Algorithm/Method | 106 (41.2%) | 156 | 96 | 132 |
| Assignment/Initialization | 26 (10.1%) | 9 | 32 | 24 |
| Function/Class/Object | 1 | 6 | 3 | 0 |
| Interface/O-O Messages | 1 | 2 | 5 | 4 |
| Relationship | 2 | 5 | 8 | 4 |
| Timing/Serialization | 0 | 0 | 0 | 0 |
| Other | 0 | 0 | 0 | 0 |

### Variation across projects

We ran a χ² test on the Algorithm/Method, Checking and Assignment/Initialization columns, with every other type pooled into one "Rest" column.

| Run | χ² | dof | p | Cramér's V | Cells with expected count < 5 |
|---|---|---|---|---|---|
| Sci prefix | 15.29 | 12 | 0.226 | 0.141 | 8 / 20 |
| Sci postfix | 17.72 | 12 | 0.125 | 0.152 | 7 / 20 |
| Few postfix | 22.93 | 12 | 0.028 | 0.172 | 8 / 20 |

Per-project counts (sci prefix: Algorithm / Checking / Assignment / Rest):
- Chart: 5 / 15 / 6 / 0
- Lang: 22 / 33 / 5 / 1
- Math: 53 / 42 / 9 / 2
- Mockito: 17 / 16 / 4 / 1
- Time: 9 / 15 / 2 / 0

### What we can claim
- Three Control-and-Data-Flow types account for about 98% of Defects4J bugs in these five projects.
- Under the scientific condition the distribution does **not** differ significantly across projects, so it is stable.

### Caveats to state in the paper
1. **Test validity.** 8 of 20 cells have expected counts below 5, so use Fisher's exact test (or a Monte Carlo χ²) instead of asymptotic χ².
2. **Model labels, not ground truth.** The distribution **depends on the prompting strategy**. Few-shot prefix gives Algorithm/Method 156 where scientific gives 106. The total variation distance between the sci prefix and few prefix distributions is **0.23**, which is *larger* than the prefix-to-postfix shift within scientific (**0.07**). Report RQ1 as conditional on the pipeline configuration.

---

## RQ2: Bug type coverage of the ODC taxonomy

**Standing: 🟡 weak but honest.**

### What we have
- **0 "Other" primary labels** across all 1,028 classifications.
- "Other" was offered as an alternative type exactly once (sci prefix).
- By the rule of three, the true escape rate is at most **≈1.2% per condition** (3/257) at 95% confidence.
- `needs_human_review` was set 6 times (sci prefix) and 5 times (few prefix), and never in postfix.
- In the 13-bug manual reading, every bug fit one of the seven standard types.

### What is missing
- The planned design compares **closed vs open** runs of the same strategy (closed↔open shift κ). v2 contains **no closed runs**, so that half of RQ2 cannot be computed.
- We cannot separate "the taxonomy covers every bug" from "the model avoids choosing Other". A reviewer will raise this.
- Four of the seven types are almost never used. That is coverage in the sense of "nothing escaped", not in the sense of "every type is exercised".

### To strengthen it
Run `scientific-closed` (and ideally `few-closed`) on the same 257 bugs into `artifacts_v2`, then report closed↔open agreement next to the escape-rate upper bound.

---

## RQ3: Overall pipeline classification accuracy

**Standing: ❌ not defensible as worded.**

### Why
RQ3 asks how well the pipeline classifies bugs into the *correct* types. There is **no human-verified ground truth**. Postfix is a second opinion that happens to have more evidence; it is not a correct answer. In the 13-bug manual shortlist, scientific postfix was wrong on 7 of 13. That sample was deliberately chosen to show failure modes, so it cannot be generalised, but it shows postfix is not a valid reference.

### The 4-level framework, with chance baselines

The chance baseline shuffles postfix labels across bugs (300 permutations) and recomputes each level.

| Level | Sci prefix vs postfix | Chance | Few prefix vs postfix | Chance |
|---|---|---|---|---|
| Strict match | **73.5%** (95% CI 68.1–79.0%) | 37.5% | 67.7% (CI 62.3–73.2%) | 42.7% |
| Cohen's κ | **0.577** (CI 0.498–0.655), "moderate" | — | 0.437 (CI 0.344–0.527) | — |
| Top-2 match | 96.1% | **90.6%** | 97.7% | 92.4% |
| Family match | 93.0% | **92.4%** | 94.2% | 92.1% |

**Top-2 and family match are uninformative.**
- 253 of 257 sci prefix labels fall in the "Control and Data Flow" family, so family agreement is nearly automatic.
- 224 of 257 sci prefix classifications list Checking or Algorithm/Method among their alternatives, so Top-2 is nearly automatic too.
- Only **strict match and κ** carry real signal. Also note that κ = 0.577 falls **below** the "substantial (0.6–0.8)" target in `docs/eval_defence.md`.

### Two ways to fix RQ3
1. **Reframe it** as prefix/postfix classification *consistency*. Report strict match and κ only, and drop Top-2 and family as evidence of accuracy.
2. **Add real ground truth** (strongly recommended).
   - Draw a **random** sample of about 60–80 bugs.
   - Two of us label each bug independently from the fix diff, without seeing any model output, and adjudicate disagreements.
   - Report our own κ, then score prefix and postfix against the adjudicated labels.

Option 2 is the single change that would most strengthen the paper.

---

## RQ4: Contribution of each pipeline component

**Standing: ❌ mostly not answerable from v2.**

### What is missing
There is no `zero-free` (unstructured LLM) baseline in v2. So **vocabulary reduction** and the **contribution of taxonomy grounding compared to an unstructured baseline** cannot be measured.

### What v2 can say (scientific loop vs few-shot)

| Metric | Scientific | Few-shot |
|---|---|---|
| Prefix↔postfix strict match | 73.5% | 67.7% |
| Prefix↔postfix κ | 0.577 | 0.437 |
| Prefix vs postfix-consensus (the 197 bugs where both postfix runs agree) | 79.2% | 75.6% |

Scientific looks better, but:
- **Not significant per bug.** A McNemar test on per-bug prefix=postfix agreement gives: scientific-only agree 46, few-only agree 31, exact **p = 0.110**. The κ confidence intervals overlap.
- **The loop is not clearly the cause.**
  - 31 sci prefix runs (and 82 postfix runs) concluded at turn 1 **with zero probes**.
  - The buggy (modified) class is present in the evidence store for only **105 / 257** bugs, and a prefix probe actually retrieved it for **55 / 257**.
  - Prefix/postfix agreement by number of probes: 0 probes → 87.1% (n=31); 1 → 66.7% (n=84); 2 → 71.9% (n=57); 3+ → 76.5% (n=85). Probe count most likely tracks bug difficulty rather than causing better agreement.

### To make RQ4 answerable
- Run `zero-free` on the same 257 bugs into `artifacts_v2` (≈514 LLM calls).
- Otherwise, narrow RQ4 to "scientific loop vs few-shot" and report the non-significant result honestly.

---

## RQ5: Does seeing the fix change the classification?

**Standing: ✅ strongest RQ.**

### Magnitude
- Scientific: labels changed for **68 / 257 (26.5%)**, κ = 0.577.
- Few-shot: labels changed for **83 / 257 (32.3%)**, κ = 0.437.
- The type mix barely moves at distribution level. Total variation distance prefix vs postfix is 0.07 (scientific) and 0.12 (few-shot).

### Pattern (scientific drifts)
- Checking ↔ Algorithm/Method: **32** (17 one way, 15 the other)
- Algorithm/Method ↔ Assignment/Initialization: **11** (9 + 2)
- Checking ↔ Assignment/Initialization: **7** (5 + 2)
- **50 / 68 drifts (74%) stay within those three types**, which are the same pairs human raters are documented to confuse (see the literature section).

### A useful ceiling
Even **with** the fix visible, scientific and few-shot disagree on 23.3% of bugs (strict 76.7%, κ = 0.633). Two strategies of the same model, both given the oracle, still differ; that bounds how much prefix/postfix agreement is realistically achievable.

### Per-project reliability

| Project | n | Sci strict | Sci κ | Few strict | Few κ |
|---|---|---|---|---|---|
| Chart | 26 | 80.8% | 0.672 | 57.7% | 0.349 |
| Lang | 61 | 73.8% | 0.546 | 73.8% | 0.497 |
| Math | 106 | 75.5% | 0.603 | 74.5% | 0.537 |
| Mockito | 38 | 65.8% | 0.499 | 52.6% | 0.272 |
| Time | 26 | 69.2% | 0.480 | 57.7% | 0.212 |

With n = 26 for Chart and Time, report bootstrap confidence intervals for per-project κ.

### Qualitative drift mechanisms
The 13-bug manual analysis documents both directions of drift:
- The oracle **helps**: Time_3, Chart_11.
- The oracle **hurts**: Math_23, Math_17. The postfix run relabels based on surface syntax of the patch.
- The oracle is **ignored**: Chart_17, Math_90.

That gives RQ5 a qualitative "why" alongside the numbers.

---

## Checking the claim "experts confuse Algorithm and Checking ~80% of the time"

**As stated, the claim is not accurate. It traces to a real result, and the corrected version is more useful to us.**

### Likely origin: Henningsson & Wohlin (2004)
- **Setup:** 8 people classified 30 faults using an ODC-based scheme, working from written fault descriptions only.
- **Agreement:** average pairwise κ was **0.16** ("poor"). Merging the two most-confused classes only raised it to 0.24.
- **Most frequent confusion:** **Assignment ↔ Algorithm**. Quote: *"The most frequent mix-up is the interchange between AS and AL, in total, 22 of the 28 pairs mixed these two classes up a number of times."* That is 22/28 = **79%** of rater pairs, the likely source of "80%".
- **Top confusions** (Table 6, occasions):

  | Pair | Occasions |
  |---|---|
  | Assignment–Algorithm | 184 |
  | Interface–Algorithm | 77 |
  | **Checking–Algorithm** | **68 (third)** |
  | Assignment–Interface | 59 |
  | Assignment–Checking | 49 |

- **Their conclusion:** the fault description was the likely cause of low agreement. They recommend giving raters source code and change information.
- **Correct phrasing:** 79% of rater *pairs* confused **Assignment and Algorithm**. Checking–Algorithm was third.

### Counter-evidence we must also cite
- **El Emam & Wieczorek (1998):** the ODC-derived scheme was "in general repeatable" (κ-based). Raters classified inspection defects at detection time, with code available.
- **ODC study of NoSQL defects (JSS 2020):** the external verification step reports **κ = 0.93** for Defect Type (one verifier reached accuracy 0.94, another 0.91 / κ 0.90). This was a *verification* of an existing classification, so it is not strictly a blind independent labelling.

### How to use this honestly
Human agreement on ODC type **depends on how much information the rater has**: poor from descriptions alone, high with full code and change context. That mirrors our prefix (limited evidence) vs postfix (fix visible) design, and it explains why prefix/postfix drift concentrates in Assignment/Algorithm/Checking.

### Claims in our own docs to remove or source
- `docs/eval_defence.md` and `docs/Research Paper Roadmap_ Defect Classification.md` state *"Chillarege et al. (1992): human inter-rater agreement ~70–80%"*.
  - Not found in the repo's ODC v5.2 doc (`docs/odc_doc.md`).
  - Not found in Chillarege's own ODC concept article, which reports no agreement figures.
  - **Remove unless a page-level citation is found.**
- `docs/eval_defence.md`: *"Typical ODC studies: κ 0.60–0.80"* has no source. Replace it with the concrete studies above.

---

## Checking the argument "prefix = postfix means prefix alone is enough for triage"

**As stated, this will be attacked, for two reasons.**
1. **Agreement is not correctness.** Chart_17 and Math_90 agree across prefix and postfix and are both wrong. Postfix is a better-informed second rater, not a validator of truth.
2. **ODC Defect Type is not a developer-assignment scheme.** ODC was designed to give process feedback from **distributions** of defect types, not per-bug routing. "Correct type → correct developer" would need its own evidence, which we don't have.

### Defensible reframing
- **Aggregate level (ODC's intended use).** Prefix-only classifications give almost the same type distribution as fix-aware classifications (TVD 0.07 under scientific). Early, pre-fix ODC analytics are therefore viable.
- **Nature of disagreements.** 74% of prefix/postfix disagreements are within the ambiguous type pairs where humans also disagree, so drift is a known property of ODC rather than random noise.
- **Confidence tiering for triage.** All four runs agree on **130 / 257 (50.6%)** bugs, which can be offered as a high-confidence tier. Prefix matches the postfix consensus on 79.2% of the 197 bugs where both postfix runs agree.
- **Role of postfix.** Present it as a *consistency reference* (a second rater with more evidence), not as a validator.

---

## Is the 13-bug manual analysis the right approach?

**For explaining the pipeline to faculty, and for RQ5's qualitative drift mechanisms: yes, very good.** It shows:
- the loop working as designed (Chart_9);
- the loop starved of evidence (Chart_11);
- right mechanism, wrong label (Time_3, Math_104);
- confident, consistent and wrong (Chart_17, Math_90);
- the oracle hurting (Math_23);
- right label for the wrong reason (Chart_7).

That is an honest demonstration that the classifications are useful but imperfect.

**As evidence of accuracy: no.** The 13 bugs were deliberately chosen to show failure modes, and the proposed ground truth comes from a single rater. Presented as proof of correctness, it will be challenged.

### To make it count
1. At least two team members label each bug **from the diff, before reading the model output** (the per-bug checklist already asks for this), and we report their κ.
2. Present it as a qualitative study of mechanisms, not a quantitative accuracy estimate.
3. Pair it with the random-sample human labelling proposed under RQ3 for any accuracy claim.
4. Grade the **label** and the **reasoning/mechanism** separately. Chart_7 and Math_17 show the two can diverge.

---

## Threats to fix or disclose

1. **Probe bug.** `execute_probe`'s snippet probe matches by substring (`argument in s.class_name`, `d4j_odc_pipeline/agent.py`), so `snippet(...dfp.Dfp)` returns `DfpTest` and `snippet(Gamma)` returns `GammaTest`. The model then reasons as if it had seen production code. This is a real pipeline bug that weakens claims about the loop. **Fix before any rerun.**
2. **Evidence coverage.** The modified class is missing from `context.json` snippets for 152 of 257 bugs, so probes cannot reach the buggy code in most assertion-failure bugs.
3. **Single model.** All results use gemini-3.1-flash-lite-preview.
4. **Possible memorization.** Defects4J bugs and fixes are public, so the model may already know them.
5. **Bug-report anchoring.** Reports that propose a fix (e.g., Math_90) steer the label.
6. **Statistics.** Sparse χ² cells (RQ1), small per-project n (RQ5), and near-chance Top-2 and family levels (RQ3).

---

## Recommended next steps (by impact per effort)

1. **Fix the substring match** in the snippet probe.
2. **Random-sample human ground truth** (60–80 bugs, 2 blind raters, κ, adjudication). This rescues RQ3 and strengthens RQ5.
3. **Run `zero-free`** on the 257 bugs into `artifacts_v2` (≈514 LLM calls). This makes RQ4 answerable.
4. **Run `scientific-closed`** (optionally `few-closed`) on the 257 bugs. This completes RQ2.
5. **Rewrite the accuracy framing:** drop Top-2 and family as accuracy evidence, report strict match and κ with confidence intervals, and use Fisher/Monte Carlo tests for RQ1.
6. **Correct the literature claims** in `docs/eval_defence.md` and the roadmap doc, as described above.

None of this requires re-collecting Defects4J evidence; only additional LLM runs and a few days of careful human labelling.

---

## Sources

- K. Henningsson and C. Wohlin, "Assuring Fault Classification Agreement: An Empirical Evaluation," ISESE 2004, pp. 95–104. [PDF](https://www.wohlin.eu/isese04.pdf) · [IEEE Xplore](https://ieeexplore.ieee.org/document/1334897)
- K. El Emam and I. Wieczorek, "The Repeatability of Code Defect Classifications," ISSRE 1998, pp. 322–333. [IEEE Xplore](https://ieeexplore.ieee.org/document/730897/) · [ResearchGate](https://www.researchgate.net/publication/3780730_The_Repeatability_of_Code_Defect_Classifications)
- "Using Orthogonal Defect Classification to Characterize NoSQL Database Defects," Journal of Systems and Software, 2020. [Preprint PDF](https://eden.dei.uc.pt/~cnl/papers/2020-jss-odc-joao-v64-submitted.pdf) · [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0164121219302250)
- R. Chillarege et al., "Orthogonal Defect Classification: A Concept for In-Process Measurements," IEEE TSE 18(11), 1992. [ACM DL](https://dl.acm.org/doi/10.1109/32.177364)
- Chillarege Inc., ODC concept article. [Link](https://www.chillarege.com/articles/odc-concept.html)
- F. Thung, D. Lo and L. Jiang, "Automatic Defect Categorization," WCRE 2012. [ACM DL](https://dl.acm.org/doi/10.1109/WCRE.2012.30) (the 77.8% figure cited in our docs was not re-verified in this assessment)
