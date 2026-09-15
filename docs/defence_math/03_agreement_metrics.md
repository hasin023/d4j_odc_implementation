# Agreement metrics — the four tiers, drift, and the ceiling

This doc explains every *agreement* number in RQ3 and RQ4: what it measures, how it is computed, the
worked value from our data, and how to explain it. Cohen's κ (Tier 4) has its own doc:
[`02_cohens_kappa.md`](02_cohens_kappa.md).

All numbers: 410 bugs, `scientific-open` unless stated. Code: `d4j_odc_pipeline/comparison.py`
(`compare_classifications`) and `scripts/analysis/recompute_rq_statistics.py`.

---

## 1. The setup: two labels per bug

For each bug we have a **pre-fix** label (buggy code, tests, report) and a **post-fix** label (the same
plus the fix diff). The post-fix label is the *fix-informed reference*. Every tier compares these two
labels for the same bug, then averages over bugs.

Each classification also lists **alternative types** — close runner-up types, with a reason each was not
chosen. Tier 2 uses these.

---

## 2. Tier 1 — Strict match

**What:** do the two labels name exactly the same ODC type?

**Formula:** strict match = (number of bugs with pre-fix label = post-fix label) / (number of bugs)

**Our value:** 288 / 410 = **70.2%** (few-shot: 66.6%).

**How to explain:** "For 70% of bugs, the label we assign before any fix exists is exactly the label we
assign once the fix is visible."

**Interval:** 95% bootstrap interval [65.6%, 74.9%] — see `04_statistical_tests.md` §3.

---

## 3. Tier 2 — Top-2 match

**What:** do the two labels match, or does either label appear among the *other* classification's
alternative types?

**Code (`comparison.py`):** `top2 = strict or prefix_type in postfix_alts or postfix_type in prefix_alts`
— symmetric, in either direction.

**Our value:** **97.1%** (few-shot 98.5%).

## 4. Tier 3 — Family match

**What:** do the two types belong to the same family? The book uses two families (this study's own
grouping, not part of IBM's specification):

- **Control and Data Flow:** Algorithm/Method, Assignment/Initialization, Checking, Timing/Serialization
- **Structural:** Function/Class/Object, Interface/O-O Messages, Relationship

**Our value:** **94.1%** (few-shot 95.6%).

---

## 5. Why Tiers 2 and 3 cannot be read on their own

**The problem:** three types (Checking, Algorithm/Method, Assignment/Initialization) cover 97.8% of
labels, and all three are in the same family. So almost any two labels are in the same family, and the
reference type is very often on the alternative list anyway.

**How we measured the chance level (shuffle baseline):** keep every pre-fix classification fixed, randomly
reassign the post-fix classifications to *different* bugs, recompute Tiers 2 and 3, and repeat 200 times.
Matching a bug with someone else's reference can only agree by chance.

| Tier | Real | Random shuffle |
| --- | --- | --- |
| Top-2 match | 97.1% | **92.5%** |
| Family match | 94.1% | **92.9%** |

The real values are only a few points above chance, so on their own they prove little.

**What we do instead — read them conditionally:** look only at the 122 bugs where Tier 1 failed and ask how
far apart the labels are.

| Among the 122 disagreeing bugs (scientific) | Count | Share |
| --- | --- | --- |
| One label is on the other classification's alternative list ("near miss") | 110 | 90.2% |
| Both types in the same family | 98 | 80.3% |
| **Unrelated**: neither an alternative nor the same family | **10** | 8.2% of drifts, **2.4% of all 410 bugs** |

**Direction matters.** The pipeline's top-2 match is symmetric: it counts a near miss if the post-fix
label is among the pre-fix alternatives **or** the pre-fix label is among the post-fix alternatives. If you
count only "the reference label was already on the pre-fix shortlist", the share is **94 of 122 = 77.0%**
(few-shot 80.3%; Closure 88.9% instead of 96.3%). The book now uses the symmetric wording (Issue #8, fixed).

**Derived sentence in the book:** "For a further 27.3%, the labels differ but the reference was already an
alternative or in the same family" = (410 − 288 strict − 10 unrelated) / 410 = 112 / 410.

**How to explain:** "Tiers 2 and 3 look high partly because the benchmark is dominated by three related
types, so we don't use them as accuracy. We use them to grade the misses: of the 30% that disagree, in 90%
one label was already the other's runner-up, and only 2.4% of all bugs get an unrelated label."

---

## 6. Drift

**Definition:** a bug *drifts* when its pre-fix and post-fix labels differ. Drift rate = 1 − strict match.

**Our values:** 122 of 410 = **29.8%** (few-shot 137 = 33.4%). Five projects without Closure: 26.5%;
Closure alone: 35.3% (54 of 153).

**Drift pairs (Table "most frequent drift pairs"):** count each drifting bug under its unordered pair of
types, and split by direction.

| Pair | Drifts | A → B | B → A |
| --- | --- | --- | --- |
| Algorithm/Method – Checking | 75 | 38 | 37 |
| Algorithm/Method – Assignment/Initialization | 12 | 10 | 2 |
| Checking – Assignment/Initialization | 11 | 8 | 3 |

- Within the three types: 75 + 12 + 11 = **98 of 122 = 80.3%**.
- Algorithm/Method–Checking alone: 75 / 122 = **61%**.
- The near-even split 38 / 37 means the fix does not push labels systematically one way — the boundary is
  genuinely ambiguous.

---

## 7. The agreement ceiling

**Question it answers:** is 70.2% low because the pre-fix run lacks the fix, or because the task itself is
ambiguous?

**How:** compare the two *strategies* with each other on the same bugs.

| Comparison | Agreement | κ |
| --- | --- | --- |
| scientific vs few-shot, **both see the fix** (post-fix) | **76.3%** | 0.614 |
| scientific vs few-shot, neither sees the fix (pre-fix) | 68.0% | 0.451 |

Even with the fix visible to both, two classifications disagree on 23.7% of bugs ("nearly a quarter").
Our pre-fix strict match, 70.2%, is only about 6 points (76.3 − 70.2 = 6.1) below this. Post-fix agreement
is higher than pre-fix agreement in all six projects.

**How to explain:** "Even two fix-aware classifications only agree 76% of the time, so a large part of the
remaining disagreement comes from the ambiguity of the ODC boundaries, not from missing the fix."

**Careful:** this is not a hard mathematical ceiling — it is an empirical reference point. Say "reference
level", not "maximum possible".

---

## 8. Post-fix consensus (RQ4b)

**Definition:** the bugs where the scientific and few-shot **post-fix** labels agree — 313 bugs. On these,
the reference is not dependent on which strategy produced it.

**Our values:** scientific pre-fix matches the consensus on **74.8%**, few-shot pre-fix on 71.6%.

**Why it exists:** it answers "is your reference just an artefact of using `scientific-open` for the
post-fix side?" — against a reference that both strategies agree on, the scientific pre-fix result is
slightly higher, not lower.

---

## 9. "Reproducible" (RQ4a)

**Definition:** the share of bugs for which the model produced the *identical label string* in both
evidence modes. For the taxonomy conditions this equals strict match; for `zero-free` it compares
free-form text exactly.

| Condition | Reproducible |
| --- | --- |
| zero-free | 15.1% (Closure only: 9.2%) |
| few-open | 66.6% |
| scientific-open | 70.2% |

**Careful:** for `zero-free`, "Improper input validation logic" vs "Incorrect boundary condition logic"
counts as a mismatch even though the meaning is close. That is exactly RQ4a's point — free-form labels
cannot be aggregated — so call it "string-level" if asked.

---

## 10. Manual-reading agreement (thirteen bugs)

**Definition:** the number of the thirteen manually analysed bugs whose model label equals the manual
reading. Reported as counts (6 / 13), never as a rate or accuracy, because the bugs were chosen to cover
specific scenarios and the reading is one rater's judgement.

| Condition | Gemini | gpt-5-mini |
| --- | --- | --- |
| Scientific pre-fix | 6 | 6 |
| Few-shot pre-fix | 4 | 4 |
| Scientific post-fix | 6 | 11 |
| Few-shot post-fix | 11 | 12 |

---

## Questions to be ready for

1. **"Agreement isn't accuracy."** Agreed — the book says so. Chart_17 and Math_90 agree across modes and
   are both wrong. The claim is reproduction of a better-informed reference.
2. **"Why not report top-2 and family as accuracy?"** Because the random-shuffle baseline is above 92%;
   they only become informative conditional on disagreement.
3. **"Isn't the reference biased toward the scientific condition?"** Section 8: against the 313-bug
   consensus of both strategies, scientific still matches more often.
