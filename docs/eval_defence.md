# Evaluation Defence: Why Pre-fix ≠ Post-fix is Scientifically Expected

This document provides the complete scientific defence for the evaluation methodology
used in the Defects4J ODC Pipeline thesis. It addresses the core question:

> **If our pipeline classifies the same bug differently in pre-fix and post-fix
> modes, does that mean our pipeline is wrong?**

**Answer: No.** Classification divergence between pre-fix and post-fix modes
is _expected_, _explainable_, and fully consistent with the ODC literature.

---

## 1. The Three Pillars of Defence

### Pillar 1: Evidence Asymmetry

Pre-fix and post-fix classifications operate on **fundamentally different evidence bases**.

| Aspect                         | Pre-fix Mode                                                          | Post-fix Mode                                  |
| ------------------------------ | --------------------------------------------------------------------- | ---------------------------------------------- |
| **Evidence available**         | Stack traces, failing tests, error messages, production code snippets | All of the above + the actual buggy→fixed diff |
| **What the LLM sees**          | _Symptoms_ of the bug                                                 | The _actual code change_ that fixes the bug    |
| **Classification perspective** | Effect-oriented: "what went wrong?"                                   | Cause-oriented: "what was changed?"            |
| **Analogous to**               | A doctor diagnosing from symptoms                                     | A pathologist with the biopsy results          |

**Key insight**: A symptom like `NullPointerException` might suggest a **Checking** defect
(missing null guard), but the actual fix might reveal an **Algorithm/Method** defect
(the whole approach to data retrieval was wrong, and the NPE was just one manifestation).
Each classification is _reasonable given the evidence that produced it_.

> ⚠️ **Do not write "both classifications are correct."** We have no ODC ground truth for
> Defects4J, so we cannot certify either one as correct. The post-fix run is a
> **better-informed second rater**, not a validator of truth. Our own 13-bug manual analysis
> has cases where pre-fix and post-fix agree perfectly and are **both wrong** (Chart_17,
> Math_90). The defensible phrasing is "the pre-fix label reproduces / does not reproduce the
> fix-aware reference." See `docs/RQ_standing_assessment.md` Section 7.

**Literature support**: Kang, Chen, Yoo & Lou (AutoSD, EMSE 2024) demonstrated that scientific
debugging produces different hypotheses depending on available evidence. This is not a flaw — it
is the scientific method working as designed.

---

### Pillar 2: ODC Boundary Ambiguity

The ODC taxonomy has **known boundary ambiguity zones** where even expert human classifiers
disagree.

#### Known Ambiguous Type Pairs

| Type A                 | Type B                    | Why they're ambiguous                                                          |
| ---------------------- | ------------------------- | ------------------------------------------------------------------------------ |
| Algorithm/Method       | Checking                  | Is a missing boundary check a "checking" issue or an "algorithmic" flaw?       |
| Algorithm/Method       | Assignment/Initialization | Is a wrong value an "assignment" bug or a flawed "algorithm"?                  |
| Function/Class/Object  | Interface/O-O Messages    | Is a missing capability a "design" gap or a "contract" mismatch?               |
| Interface/O-O Messages | Relationship              | Is a cross-component issue a "message" problem or a "relationship" constraint? |
| Function/Class/Object  | Relationship              | Is a missing association a "design" gap or a "relationship" violation?         |

#### Inter-rater Agreement Benchmarks

**This subsection is the canonical home of our human-agreement evidence.** Other documents
(`docs/RQ_standing_assessment.md` §6, the roadmap, `comparison.py`) point here. Update this first.

##### What we checked, and what we found about the old claim

This table previously read *"Chillarege et al. (1992) | Human inter-rater agreement | ~70-80%"* and
*"Typical ODC studies | Cohen's Kappa | 0.60-0.80."* We went looking for the source, because the
point itself is one we genuinely need. **We could not find one.** Specifically checked:

- Chillarege et al. (1992), IEEE TSE 18(11) — the paper the claim was attributed to.
- The Chillarege Inc. ODC concept article.
- Chillarege's "ODC for Process Measurement, Analysis and Control" paper — it discusses
  classification as "a human process, and subject to the usual problems of human error, confusion"
  but reports **no agreement figure**, only procedural mitigations.
- The IBM ODC v5.2 reference we hold locally (`docs/odc_doc.md`) — no agreement figures.
- The Wikipedia ODC article — the only quantitative claim there is that a trained person can
  classify a defect in under 3 minutes. Nothing about agreement.

**Conclusion: the ~70-80% figure is not attributable to Chillarege, and the "typical ODC studies:
κ 0.60-0.80" row was never attributed to anyone.** Do not restore either sentence as written.

**But the underlying point is sound, and the real evidence is stronger for us.** The literature
does not support one fixed agreement percentage. It supports something more useful: **agreement on
ODC classification depends almost entirely on how much evidence the rater has.** That is precisely
the variable our pre-fix vs post-fix design manipulates.

##### The evidence, by how much the rater could see

| Study | Raters / items | ODC attribute | Evidence available | Agreement |
| --- | --- | --- | --- | --- |
| **Henningsson & Wohlin (2004)** | 8 raters, 30 faults | Defect Type (ODC-based) | Written fault **descriptions only** | **mean pairwise κ = 0.16** ("poor"). Merging the two most-confused classes reached only 0.24 |
| **Hernández-González et al. (2018)** | 5 annotators; 962 (Compendium) + 675 (Mozilla) defects | **Impact** (13 categories) | Defect report **text only** | Majority (3 of 5) reached on only **481/962** and **394/675**. See caveat below |
| **El Emam & Wieczorek (1998)** | ISSRE 1998 | Code defect classification (ODC/PSP family) | **Code available** at detection time | Scheme "in general repeatable" (κ-based). ⚠️ We have not recovered the individual κ values — do not quote a number |
| **Rahman & Farhana (2020)**, COVID-19 projects | 2 coders | ODC-style bug categories | Full repository context | **72.7% agreement, κ = 0.70** (open coding); **95.1%, κ = 0.93** (closed coding). ⚠️ Taken from a secondary summary — verify against the PDF before citing |
| **NoSQL ODC study (JSS 2020)** | external verifiers | Defect Type | Full code and change context | **κ = 0.93**. ⚠️ This was *verification* of an existing classification, not blind independent labelling |
| **Thung, Lo & Jiang (2012)** | automated | Defect category | Post-fix code + ML | 77.8% accuracy. ⚠️ Not independently re-verified by us |

**Caveat on Hernández-González et al.** The paper itself reports contingency tables and majority
counts, **not** a kappa. A secondary analysis (Derek Jones, *The Shape of Code*, 2026) computed 95%
agreement intervals of **0.26–0.29** (Compendium) and **0.28–0.33** (Mozilla), both "fair to poor".
Cite the majority counts from the paper; cite the intervals as a secondary, non-peer-reviewed
computation, or not at all.

##### Which types get confused

Henningsson & Wohlin's most frequent confusion was **Assignment ↔ Algorithm**, *not* Checking ↔
Algorithm: *"The most frequent mix-up is the interchange between AS and AL, in total, 22 of the 28
pairs mixed these two classes up a number of times."* That 22/28 = 79% counts **rater pairs**, not
classifications. Their Table 6 ranks confusions by occasions: Assignment–Algorithm 184,
Interface–Algorithm 77, **Checking–Algorithm 68 (third)**, Assignment–Interface 59,
Assignment–Checking 49.

> ⚠️ **Never write "experts confuse Algorithm and Checking about 80% of the time."** It gets the
> pair wrong (it is Assignment ↔ Algorithm) and the unit wrong (rater pairs, not bugs). A reviewer
> who opens the cited paper will find both errors immediately.

##### How to state this in the paper — the sentence that is actually defensible

> "Human agreement on ODC classification is strongly evidence-dependent rather than fixed. Raters
> working only from written fault descriptions reach poor agreement — Henningsson and Wohlin (2004)
> measured a mean pairwise Kappa of 0.16 across eight raters, and Hernández-González et al. (2018)
> found five annotators reached a simple majority on barely half of their defects. Where raters had
> the code and the change available, agreement is substantially higher: El Emam and Wieczorek (1998)
> found the same family of scheme 'in general repeatable', and a 2020 JSS study of NoSQL defects
> reports Kappa of 0.93 for Defect Type. Holding an LLM pipeline to 100% pre-fix/post-fix agreement
> is therefore unreasonable — and the pre-fix versus post-fix contrast our design measures is the
> same evidence variable those studies identified."

That version is stronger than the old one for three reasons: it is sourced, it does not depend on a
single disputed percentage, and **the literature's explanation for the disagreement is our
experimental variable**. The old sentence merely excused our error rate; this one predicts it.

---

### Pillar 3: Multi-Fault Reality

Defects4J's "single-fault" assumption is an **artificial construct**.

#### Evidence from defects4j-mf (Callaghan 2024)

The defects4j-mf project (Mining Bug Repositories for Multi-Fault Programs) definitively
proved that Defects4J bug versions are **not** single-fault programs. Key findings:

- **Average co-existing faults per version: ~9.2**
- All 5 major D4J projects have multi-fault versions (Chart, Closure, Lang, Math, Time)
- Some versions contain 15+ co-existing faults from different bug IDs
- Faults from different bugs can overlap in the same source files

#### Why This Matters for Classification Divergence

When a bug version contains 9+ co-existing faults:

1. **Pre-fix mode** sees symptoms from _all_ co-existing faults mixed together.
   The LLM might classify based on the most prominent symptom, which could
   come from a _different_ fault than the one being officially fixed.

2. **Post-fix mode** sees the specific diff for _one_ fault fix. It classifies
   based on what that specific fix changed, ignoring the other 8+ faults.

3. **Result**: Pre-fix and post-fix are literally classifying _different facets_
   of the same multi-fault landscape. Divergence is not error — it is
   the pipeline correctly identifying different defect perspectives.

#### How to Query Multi-Fault Data

The pipeline can query multi-fault data for any supported project:

```powershell
python -m d4j_odc_pipeline multifault --project Lang --bug 1
python -m d4j_odc_pipeline multifault-enrich \
  --classification ./artifacts/Lang_1b/prefix/classification.json \
  --output ./artifacts/Lang_1b/prefix/classification_enriched.json
```

---

## 2. The Multi-Tier Accuracy Framework

Our evaluation framework does **not** rely on strict match alone. It uses a multi-tier approach.

> ⚠️ **Corrected 2026-09-15.** The "expected rate" figures that used to appear under each tier
> (40-60%, 60-80%, 70-90%, κ 0.50-0.80) were never sourced. They are replaced below with the
> **measured** results from the 257-bug `artifacts_v2` corpus.

Measured on 257 bugs, `scientific-open` vs its post-fix counterpart (few-shot in brackets):

### Tier 1: Strict Match (Exact Agreement)

The pre-fix and post-fix classifications assign the **same primary ODC type**.

- **Interpretation**: Highest confidence — both evidence modes converge on the same type.
- **Measured**: **73.5%** (95% CI 68.1-79.0). Few-shot: 67.7%.

### Tier 2: Top-2 Match (Alternative Type Overlap)

The pre-fix primary type appears in the post-fix `alternative_types`, or vice versa.

- **Interpretation**: The LLM recognized both types as plausible but ranked them
  differently given different evidence.
- **Measured**: 96.1% (few-shot 97.7%).

### Tier 3: Family Match (Structural vs Control and Data Flow)

Both classifications assign types from the **same ODC family**.

- **Interpretation**: Even when granular types differ, the LLM identified the
  correct _category_ of defect.
- **Measured**: 93.0% (few-shot 94.2%).

### ⚠️ How to report Tiers 2 and 3 — read them conditionally, not unconditionally

96.1% and 93.0% sound impressive but are close to the ceiling: **shuffle the labels at random and
you still get 90.6% and 92.4%**. Quoted on their own they carry almost no information, and a
reviewer will say so.

Tiers 2 and 3 are not independent accuracy tests — they describe **how severe the disagreement is
on the bugs where Tier 1 already failed**. Report them over the disagreeing bugs only:

| Among bugs where pre-fix ≠ post-fix               | Scientific (68 bugs) | Few-shot (83 bugs) |
| ------------------------------------------------- | -------------------- | ------------------ |
| Post-fix label was already shortlisted ("near miss") | 85.3%                | 92.8%              |
| Same ODC family                                   | 73.5%                | 81.9%              |
| **Genuinely unrelated** (neither shortlisted nor same family) | **9 bugs = 3.5% of the corpus** | 2 bugs = 0.8%      |

That last row is the number worth publishing: **only 3.5% of bugs get a pre-fix label unrelated to
the fix-aware one.**

### Tier 4: Cohen's Kappa (Statistical Agreement)

Measures agreement between pre-fix and post-fix as two "raters" classifying the same bugs,
corrected for agreement that would occur by chance.

- **Interpretation**: κ 0.41-0.60 is "moderate", κ 0.61-0.80 "substantial" (Landis & Koch 1977).
- **Measured**: **0.577** (95% CI 0.498-0.655), few-shot 0.437 (CI 0.344-0.527).
- **Be honest about this:** 0.577 is *moderate*, and falls just **below** the substantial band.
  Do not round it up or quietly drop the comparison — state it, then give the ceiling below.

### The ceiling that puts Tier 1 and Tier 4 in context

Give **both** strategies the fix diff, and they still disagree with each other on 23.3% of bugs
(76.7% match, κ = 0.633). Two runs of the same model, both holding the answer, cannot exceed ~77%
agreement on this task. Against that ceiling, a pre-fix result of 73.5% is close to the practical
maximum — not close to chance. This is a stronger and more honest frame than comparing against an
invented human baseline.

---

## 3. Defending Specific Bug Examples

> ⚠️ The Cli-38 example that used to sit here came from a pre-2026-07 dataset that is no longer
> current, and Cli is not one of the five projects in `artifacts_v2`. It has been replaced with
> two live examples from the 257-bug corpus.

### Example: Chart_18 — a within-family drift (the common case)

- **Pre-fix**: `Algorithm/Method` (Control and Data Flow)
- **Post-fix**: `Checking` (Control and Data Flow)

**Defence**: Both types belong to the `Control and Data Flow` family, and this is the single most
common drift pair in our data — Checking ↔ Algorithm/Method accounts for **32 of 68** scientific
drifts. The pre-fix run read the failure as flawed method logic; the fix-aware run saw that the
actual change added a guard. This is exactly the boundary Henningsson & Wohlin's raters also
struggled with. Treat it as **evidence-dependent labelling of a genuinely ambiguous boundary**,
not as a pipeline error.

### Example: Chart_23 — a cross-family drift (the rare case, and we count them)

- **Pre-fix**: `Checking` (Control and Data Flow)
- **Post-fix**: `Function/Class/Object` (Structural)

**Defence**: Do not defend this one away. Cross-family drift is the severe case, and we report it
as such: **9 of 257 bugs (3.5%)** drift to a label that is neither shortlisted nor in the same
family. Naming that number ourselves is stronger than being asked for it.

---

## 4. Summary: What Constitutes "Pipeline Accuracy"?

> ⚠️ **Corrected 2026-09-15.** This section previously set pass/fail thresholds ("strict match
> ≥ 40% — comparable to human inter-rater agreement baselines") that rested on the unsourced
> 70-80% figure removed in §1. Thresholds invented before the experiment are not a defence; they
> look like a moving goalpost. Report the measured numbers against a measured ceiling instead.

**First, say what "accuracy" can and cannot mean here.** Defects4J has no ODC labels, so there is
no answer key. We therefore do not claim absolute accuracy. We claim **reproduction of a
better-informed reference**: the post-fix run sees the developer's actual fix, and an ODC defect
type describes the nature of the fix, so the fix-aware run is the better-grounded rater. The
question we can answer is: *does a label assigned before any fix exists survive the fix appearing?*

**Second, report against the measured ceiling, not an invented floor.**

| Measure                                        | Our result (scientific) | Context                                                       |
| ---------------------------------------------- | ----------------------- | ------------------------------------------------------------- |
| Strict match with the fix-aware reference       | **73.5%**               | Ceiling is ~76.7% — two strategies that both hold the fix      |
| Cohen's κ                                       | **0.577** (moderate)    | Below the 0.61 "substantial" band; say so                      |
| Bugs whose pre-fix label is *unrelated* to the reference | **3.5%** (9 of 257) | The severity number worth leading with                        |
| Matches the post-fix consensus (197 bugs where both strategies agree) | **79.2%** | A cleaner reference than either strategy alone                 |
| All four runs agree                             | **50.6%** (130 of 257)  | Offer as a high-confidence tier for triage                     |

**Third, name what this does not license.** Agreement is not correctness — Chart_17 and Math_90
agree across both arms and are both wrong. And ODC defect type was designed for process feedback
from **distributions**, not for routing individual bugs to individual developers; do not claim
"right type → right developer" without separate evidence. The aggregate-level claim is the safe and
genuinely useful one: pre-fix classifications produce almost the same type distribution as
fix-aware ones (total variation distance **0.07**), so early ODC analytics are viable for exactly
the purpose ODC exists to serve.

---

## 5. Literature References

| #   | Reference                                                                                                                                             | Relevance                                                                                 |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| 1   | Chillarege, R., Bhandari, I., Chaar, J., et al. (1992). "Orthogonal Defect Classification — A Concept for In-Process Measurements." IEEE TSE, 18(11). | Original ODC paper; defines the taxonomy and its in-process purpose. ⚠️ Reports **no** inter-rater agreement figures — do not cite it for one |
| 1a  | Henningsson, K. & Wohlin, C. (2004). "Assuring Fault Classification Agreement: An Empirical Evaluation." ISESE 2004, pp. 95-104.                      | 8 raters, descriptions only, mean pairwise κ 0.16; most-confused pair Assignment ↔ Algorithm. The real source of our agreement discussion |
| 1b  | El Emam, K. & Wieczorek, I. (1998). "The Repeatability of Code Defect Classifications." ISSRE 1998, pp. 322-333.                                      | Same scheme family, "in general repeatable" **with code available** — the counterweight to 1a |
| 1c  | "Using Orthogonal Defect Classification to Characterize NoSQL Database Defects." JSS, 2020.                                                           | κ 0.93 for Defect Type with full code and change context (a verification step, not blind labelling) |
| 1d  | Hernández-González, J., Rodriguez, D., Inza, I., Harrison, R., & Lozano, J.A. (2018). "Learning to classify software defects from crowds: A novel approach." Applied Soft Computing. Datasets: "Two datasets of defect reports labeled by a crowd of annotators of unknown reliability," Data in Brief, 2018. | 5 annotators, ODC **Impact**, 962 + 675 defects from report text only. Majority of 5 reached on just 481/962 and 394/675. ⚠️ The paper reports contingency tables, **not** a κ |
| 1e  | Rahman, A. & Farhana, E. (2020). "An Exploratory Characterization of Bugs in COVID-19 Software Projects." arXiv:2006.00586.                            | 72.7% agreement / κ 0.70 (open coding) and 95.1% / κ 0.93 (closed coding) on ODC-style categories with full repository context. ⚠️ Taken from a secondary summary — verify against the PDF before citing |
| 2   | Thung, F., Lo, D., & Jiang, L. (2012). "Automatic Defect Categorization." WCRE 2012.                                                                  | 77.8% accuracy with ML + post-fix code. ⚠️ We have not independently re-verified this figure |
| 3   | Callaghan, D. (2024). "Mining Bug Repositories for Multi-Fault Programs." Defects4J-MF.                                                               | Proves ~9.2 co-existing faults per D4J version; invalidates "single-fault" assumption     |
| 4   | Kang, S., Chen, B., Yoo, S., & Lou, J.-G. (EMSE 2024). "Explainable Automated Debugging via LLM-driven Scientific Debugging" (AutoSD).                | Evidence-dependent hypothesis generation; source of our loop-iteration ordering. ⚠️ Earlier drafts of this file cited this as "Kang, Yoo & Ryu (2023)" — wrong authors and year |
| 5   | Ni, M., et al. (2024). "ODC Taxonomy for LLM-Generated Code."                                                                                         | Extends ODC taxonomy validity to automated/LLM-driven classification                      |
| 6   | Landis, J.R. & Koch, G.G. (1977). "The Measurement of Observer Agreement for Categorical Data." Biometrics.                                           | Standard interpretation scale for Cohen's Kappa                                           |
| 7   | Zeller, A. (2009). "Why Programs Fail: A Guide to Systematic Debugging."                                                                              | Scientific debugging methodology: observe → hypothesize → predict → experiment → conclude |

---

## 6. Thesis Defence Talking Points

When presenting these results, emphasize:

1. **"We don't expect 100% agreement, and here is the measured ceiling."** Give both of our
   strategies the fix diff and they still disagree with each other on 23.3% of bugs. So ~77% is the
   practical maximum on this task. Our pre-fix run reaches 73.5%.
   ⚠️ **Do not say "human ODC experts disagree 20-30% of the time."** That number is unsourced and
   has been removed from this document. If you want the human comparison, use the real one: human
   agreement ranges from κ 0.16 (descriptions only) to κ 0.93 (full code and change context), which
   is the same evidence-dependence our design measures.

2. **"Pre-fix and post-fix are two evidence positions, not two truths."** Like a symptom-based
   diagnosis versus a biopsy-informed one — the second is better informed, and we treat it as the
   reference. ⚠️ **Do not say "both are correct."** We have no ground truth, and we have cases
   (Chart_17, Math_90) where both arms agree and are both wrong.

3. **"Multi-fault reality makes single-bug accuracy misleading."** When a version contains
   9+ faults, the pre-fix classifier is seeing a _different defect landscape_ than the
   post-fix classifier.

4. **"The alternative types prove the LLM understands the ambiguity."** When the LLM's
   alternative types in pre-fix include the post-fix primary (or vice versa), it demonstrates
   the model correctly identified the type boundary but ranked differently given different evidence.
