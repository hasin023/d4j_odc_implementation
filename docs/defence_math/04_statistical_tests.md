# Statistical tests — what each one does, with our numbers

This doc covers every statistical test in Chapter 6: the Monte Carlo χ² test and Cramér's V (RQ1), the
rule of three (RQ2), bootstrap confidence intervals (RQ3), the paired bootstrap on Δκ, McNemar's exact
test and the sign test (RQ4).

Implementation: `scripts/analysis/recompute_rq_statistics.py` (pure Python, fixed seed 20260915). The
pipeline itself provides the metrics (`compare_classifications`, `compute_cohens_kappa`); the resampling
and tests are in this script.

**One idea runs through all of them:** a *p-value* is the probability of seeing a result at least this
extreme **if the "nothing is going on" hypothesis were true**. Small p (conventionally < 0.05) means the
data would be surprising under that hypothesis.

---

## 1. Monte Carlo permutation χ² test (RQ1)

**Question:** does the ODC type distribution depend on the project?

**The table:** 6 projects (rows) × 6 ODC types that occur (columns); each cell is a count of bugs.

**The χ² statistic:** compares each observed cell count O with the count E expected if project and type
were unrelated:

```
E(project, type) = (row total × column total) / n
χ² = Σ over all cells of (O − E)² / E
```

Degrees of freedom: (rows − 1) × (columns − 1) = 5 × 5 = **25**.

**Why not the usual χ² p-value:** the standard p-value assumes every expected count E is at least 5. Ours
are not: Interface/O-O Messages appears once and Function/Class/Object three times, so most of those cells
have E far below 5, and the textbook p-value would be unreliable.

**What we do instead (permutation test):**

1. Compute the real χ² (36.11 for scientific pre-fix).
2. Randomly shuffle the type labels across the 410 bugs. This keeps each project's size and each type's
   total, but destroys any link between project and type.
3. Recompute χ² on the shuffled table.
4. Repeat 10,000 times.
5. p = (number of shuffles with χ² ≥ 36.11, plus 1) / (10,000 + 1).

**Our results:**

| Condition | χ² | dof | Monte Carlo p | Cramér's V |
| --- | --- | --- | --- | --- |
| Scientific pre-fix | 36.11 | 25 | **0.096** | 0.133 |
| Few-shot pre-fix | 49.48 | 25 | **0.010** | 0.155 |
| Scientific, five projects without Closure | 21.35 | 20 | 0.381 | 0.144 |

**How to read it:** under the scientific condition, about 1 random shuffle in 10 produces a table as
uneven as ours, so the project differences are consistent with chance at the 5% level. Under few-shot,
only about 1 in 100 does, so few-shot's distribution does depend on the project.

**How to explain:** "We used a permutation version of the χ² test because several ODC types are rare,
which breaks the normal test's assumptions. Shuffling the labels 10,000 times gives the p-value directly
from the data."

### Cramér's V (effect size)

A p-value says whether an association is detectable, not how strong it is. Cramér's V rescales χ² to
0 (no association) … 1 (perfect association):

```
V = sqrt( χ² / (n × (min(rows, columns) − 1)) )
  = sqrt( 36.11 / (410 × 5) ) = 0.133
```

**Reading:** 0.13 is a weak association. Even where it exists, the project explains little of the type
distribution.

---

## 2. Rule of three (RQ2)

**Question:** we saw **zero** "Other" escapes. How high could the true escape rate still be?

**Why a p-value doesn't work:** with zero events there is nothing to test. What we can give is an
**upper bound**.

**The rule:** if an event occurred 0 times in n independent trials, the 95% upper confidence bound on its
rate is approximately **3 / n**.

**Where it comes from:** if the true rate were p, the chance of seeing zero events is (1 − p)ⁿ. The largest
p for which that chance is still at least 5% solves (1 − p)ⁿ = 0.05, so p = 1 − 0.05^(1/n) ≈ −ln(0.05)/n ≈
3.0 / n.

| n | 3 / n | Exact 1 − 0.05^(1/n) |
| --- | --- | --- |
| 410 (one condition) | 0.73% | 0.73% |
| 1,640 (all classifications) | 0.18% | 0.18% |

The book rounds these to 0.7% and 0.2%.

**How to explain:** "Zero escapes in 1,640 classifications means that, with 95% confidence, fewer than 2 in
1,000 bugs would need the 'Other' category."

**Careful:** the rule assumes independent trials. The 1,640 classifications are four views of 410 bugs,
so they are not fully independent; the per-condition bound (0.7%, n = 410) is the more conservative number.

---

## 3. Bootstrap confidence intervals (RQ3)

**Question:** 70.2% strict match and κ = 0.505 come from one sample of 410 bugs. How much would they
change with a different sample of bugs?

**The method (percentile bootstrap):**

1. From the 410 bugs, draw 410 bugs **with replacement** (some bugs appear twice, some not at all).
2. Recompute strict match (or κ) on that resample.
3. Repeat 2,000 times.
4. Sort the 2,000 values; the 2.5th and 97.5th percentiles are the 95% interval.

**Our results:**

| Metric | Scientific | Few-shot |
| --- | --- | --- |
| Strict match | 70.2% [65.6, 74.9] | 66.6% [62.0, 71.2] |
| Cohen's κ | 0.505 [0.433, 0.574] | 0.389 [0.310, 0.468] |

**How to explain:** "If we repeated the study on another set of bugs of this kind, strict match would
typically land between about 66% and 75%."

**Careful:**
- Bootstrap intervals are Monte Carlo estimates: re-running with another seed moves the endpoints slightly
  (about ±0.01 here, more for small samples such as Time's 26 bugs).
- Overlapping intervals for two conditions do **not** by themselves test the difference between them — that
  needs the paired bootstrap below.

---

## 4. Paired bootstrap on the κ difference (RQ4b — the main test)

**Question:** is scientific's κ (0.505) really higher than few-shot's (0.389), or could the gap be chance?

**Why "paired":** both conditions were run on the **same** 410 bugs. Hard bugs are hard for both. Resampling
bugs once and computing both κ values on the same resample keeps that pairing, which makes the comparison
much more precise than comparing two separate intervals.

**The method:**

1. Draw 410 bugs with replacement.
2. On that resample, compute κ for scientific and κ for few-shot, and take Δκ = κ_sci − κ_few.
3. Repeat 5,000 times.
4. 95% interval = 2.5th and 97.5th percentiles of Δκ.
5. Two-sided p ≈ 2 × min(share of resamples with Δκ ≤ 0, share with Δκ ≥ 0).

**Our result:** **Δκ = 0.115, 95% CI [0.026, 0.208], p ≈ 0.012.**

**How to read it:** the interval does not include 0, so the improvement is statistically significant at the
5% level. Because p is two-sided (2 × the smaller tail), p ≈ 0.012 means that in only about 0.6% of resamples was few-shot's κ equal to or higher than scientific's.

**Same test on Closure alone:** Δκ = 0.065, CI [−0.108, 0.237]. The interval includes 0, so the loop's gain on
Closure is not distinguishable from zero.

**How to explain:** "We resampled bugs 5,000 times and recomputed both strategies' κ on each resample. The
difference stayed above zero in more than 99% of resamples."

---

## 5. McNemar's exact test (RQ4a, RQ4b)

**Question:** for paired yes/no outcomes, does one condition succeed more often than the other?

**The idea:** for each bug, record whether its pre-fix and post-fix labels match under condition A and under
condition B. Bugs where both match or both fail say nothing about which condition is better. Only the
**discordant** bugs matter:

- b = bugs consistent under A only
- c = bugs consistent under B only

If A and B were equally good, each discordant bug would be equally likely to fall on either side, like a fair
coin. The exact test asks how unusual the split b vs c is for a fair coin:

```
p = 2 × Σ_{i=0}^{min(b,c)} C(b+c, i) / 2^(b+c)     (capped at 1)
```

**Our results:**

| Comparison | b | c | p |
| --- | --- | --- | --- |
| RQ4a: scientific-open vs zero-free | 223 | 18 | 3.8 × 10⁻⁴⁶ |
| RQ4a: few-open vs zero-free | 204 | 14 | 2.1 × 10⁻⁴⁴ |
| RQ4b: scientific vs few-shot, raw agreement | 73 | 58 | **0.221** |
| RQ4b: scientific vs few-shot, match with post-fix consensus (313 bugs) | 43 | 33 | 0.302 |

**Why RQ4b's McNemar is not significant while the κ test is:** McNemar counts raw matches. Few-shot labels
265 of 410 bugs as Algorithm/Method, so its two labels match often just because they are usually the same
dominant type. κ subtracts that chance agreement; McNemar does not. The book reports both and explains the
difference — see `02_cohens_kappa.md` §5.

**About the tiny RQ4a p-values:** with 223 vs 18, a fair coin would essentially never produce such a split.
The result is expected (fixed labels are more consistent than free text), so present it as confirming a
precondition, not as a striking discovery.

---

## 6. Sign test (RQ4b)

**Question:** across projects, does scientific consistently beat few-shot, regardless of by how much?

**The idea:** in each project, record only *who wins* on κ. If the strategies were equally good, each project
would be a coin flip. Scientific won in **6 of 6** projects.

```
one-sided p = P(6 or more wins out of 6 | fair coin) = (1/2)^6 = 1/64 = 0.016
```

(A two-sided version would be 2/64 = 0.031.)

**How to explain:** "If the two strategies were equally good, winning all six projects would happen by chance
about once in 64 tries."

**Careful:** the test ignores the size of each win, and six projects is a small number, so it is supporting
evidence alongside the paired bootstrap, not the main test.

---

## 7. Why so many different tests?

Each answers a different question, and the book states which test belongs to which RQ:

| Question | Test | RQ |
| --- | --- | --- |
| Does the type mix depend on project? | Permutation χ² + Cramér's V | RQ1 |
| How high could a never-observed rate be? | Rule of three | RQ2 |
| How precise is a single rate or κ? | Bootstrap CI | RQ3 |
| Is one condition's κ higher than another's? | Paired bootstrap on Δκ | RQ4b |
| Does one condition succeed more often per bug? | McNemar exact | RQ4a, RQ4b |
| Does one condition win consistently across projects? | Sign test | RQ4b |

**Likely challenge — "multiple testing":** we run several tests, which raises the chance of a false positive.
Answer: the primary claim for RQ4b is a single comparison (Δκ), made on κ because κ is Tier 4 of the evaluation framework defined in the methodology; McNemar and the sign test are
reported as supporting and contrasting evidence, and the non-significant results are reported openly.
