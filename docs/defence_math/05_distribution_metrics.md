# Distribution and vocabulary metrics — shares, TVD, entropy, vocabulary reduction

This doc covers the numbers that describe *label distributions* rather than per-bug agreement: type shares
(RQ1), total variation distance (RQ1, RQ3), Shannon entropy and the vocabulary reduction ratio (RQ4a).

---

## 1. Type shares (RQ1)

**Formula:** share of a type = (bugs with that label) / (all bugs).

**Scientific pre-fix, 410 bugs:**

| Type | Count | Share |
| --- | --- | --- |
| Checking | 198 | 48.3% |
| Algorithm/Method | 175 | 42.7% |
| Assignment/Initialization | 28 | 6.8% |
| Relationship | 5 | 1.2% |
| Function/Class/Object | 3 | 0.7% |
| Interface/O-O Messages | 1 | 0.2% |
| Timing/Serialization, Other | 0 | 0% |

"Three types cover 97.8%" = (198 + 175 + 28) / 410 = 401 / 410.

"Closure has almost no Assignment/Initialization" = 2 / 153 = 1.3%, against 26 / 257 = 10.1% in the other five
projects.

**Careful:** these are the pipeline's labels under one stated condition, not a configuration-independent
distribution of Defects4J. The book says this explicitly, and TVD (next section) is how it quantifies it.

---

## 2. Total variation distance (TVD)

**Question:** how different are two label distributions, as a single number?

**Formula:** for distributions P and Q over the same set of types,

```
TVD(P, Q) = ½ × Σ over types |P(type) − Q(type)|
```

It ranges from 0 (identical) to 1 (no overlap). A handy reading: **TVD is the smallest share of labels you
would have to move to turn one distribution into the other.**

### Worked example 1 — scientific pre-fix vs post-fix (RQ3): 0.051

| Type | Pre-fix | Post-fix | Difference |
| --- | --- | --- | --- |
| Checking | 198 | 192 | 6 |
| Algorithm/Method | 175 | 160 | 15 |
| Assignment/Initialization | 28 | 37 | 9 |
| Relationship | 5 | 12 | 7 |
| Function/Class/Object | 3 | 4 | 1 |
| Interface/O-O Messages | 1 | 5 | 4 |
| **Sum of differences** | | | **42** |

TVD = 42 / (2 × 410) = **0.051**. About 5% of labels would need to move to turn the pre-fix distribution into
the post-fix one.

### Worked example 2 — scientific vs few-shot, both pre-fix (RQ1): 0.23

| Type | Scientific | Few-shot | Difference |
| --- | --- | --- | --- |
| Checking | 198 | 119 | 79 |
| Algorithm/Method | 175 | 265 | 90 |
| Assignment/Initialization | 28 | 11 | 17 |
| Relationship | 5 | 5 | 0 |
| Function/Class/Object | 3 | 8 | 5 |
| Interface/O-O Messages | 1 | 2 | 1 |
| **Sum** | | | **192** |

TVD = 192 / 820 = **0.234**.

**The point the book makes with these two numbers:** changing the prompting strategy moves the distribution
(0.23) about four times as much as showing the fix does (0.05). So RQ1's distribution is reported for a
stated condition.

### An important subtlety: TVD versus drift

29.8% of *individual* labels change between pre-fix and post-fix, yet TVD is only 0.051. How?

Because changes cancel out in aggregate: 38 bugs move Algorithm/Method → Checking while 37 move Checking →
Algorithm/Method. Those 75 individual changes shift the Checking and Algorithm/Method *totals* by only one bug.
Drift measures per-bug change; TVD measures the change in the overall distribution. ODC is designed to be used
on distributions, which is why the book stresses the small TVD.

---

## 3. Shannon entropy (RQ4a)

**Question:** how spread out is a set of labels?

**Formula:** for label shares p₁, p₂, …,

```
H = − Σ pᵢ × log₂(pᵢ)      (in bits)
```

**Intuition:** H is the average number of yes/no questions needed to identify a bug's label.

- All bugs share one label → H = 0.
- Labels spread evenly over k labels → H = log₂(k), the maximum.

**Our values (pre-fix, 410 bugs):**

| Condition | Distinct labels | Entropy | Maximum possible for that many labels |
| --- | --- | --- | --- |
| zero-free (no taxonomy) | 366 | **8.376 bits** | log₂(366) = 8.52 |
| few-open | 6 | 1.291 bits | log₂(6) = 2.58 |
| scientific-open | 6 | 1.446 bits | log₂(6) = 2.58 |

**How to read it:**
- zero-free's 8.376 is close to its maximum of 8.52: the free-form labels are spread almost as evenly as
  possible — nearly one label per bug.
- The taxonomy conditions sit around 1.3–1.4 bits: most bugs fall into two or three types.
- few-open (1.291) is lower than scientific-open (1.446) because few-shot concentrates labels on
  Algorithm/Method (265 of 410).

**Careful:** lower entropy is not "better". It measures concentration, not correctness. The book uses it only
to show how strongly the taxonomy constrains the labels.

---

## 4. Vocabulary reduction ratio (RQ4a)

**Formula (defined in the book, Chapter 5; code: `analysis.py`):**

```
vocabulary reduction ratio = 1 − k / u
```

- k = 7, the number of ODC types
- u = the number of distinct labels produced without a taxonomy

**Our value:** 1 − 7 / 366 = **0.981**. (Five projects without Closure: 1 − 7 / 228 = 0.969.)

**Reading:** the taxonomy reduces the label vocabulary by about 98%.

**Careful:**
- It uses k = 7 (the size of the taxonomy), not the 6 types actually used.
- Like entropy, it measures constraint, not quality: many free-form labels are sensible descriptions. The
  problem RQ4a shows is that they cannot be counted or compared.

---

## 5. Free-form label statistics (RQ4a)

| Statistic | Value | Meaning |
| --- | --- | --- |
| Distinct free-form labels | 366 for 410 bugs | almost one label per bug |
| Used exactly once | 342 of 366 | 93% of labels are unique |
| Most frequent | "Null Pointer Dereference", 15 bugs | even the commonest label covers under 4% of bugs |
| Same label in both modes | 15.1% (Closure 9.2%) | exact string comparison — see `03_agreement_metrics.md` §9 |
