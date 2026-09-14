# 13 · Chart_7 — Scientific vs Few-shot contrast

| | Scientific-open | Few-open |
|---|---|---|
| **Prefix** | Assignment/Initialization (0.9) ✅ | Algorithm/Method (0.8) ❌ |
| **Postfix** | Algorithm/Method (1.0) ❌ | Assignment/Initialization (1.0) ✅ |

- **Manual ground truth:** **Assignment/Initialization** (confidence: Medium-High)
- **Bug report:** UNKNOWN
- **Modified class (Defects4J oracle):** `org.jfree.data.time.TimePeriodValues`
- **Scientific loop:** prefix 5 turns / 4 probes · postfix 2 turns / 1 probes
- **Buggy class present in evidence store:** no · **retrieved by a prefix probe:** no
- **Artifacts:** `.dist/study/artifacts_v2/prefix/Chart_7_prefix/`, `.dist/study/artifacts_v2/postfix/Chart_7_postfix/`

## Why this bug was shortlisted
Crossed drift: scientific went Assignment/Initialization -> Algorithm/Method while few-shot went Algorithm/Method -> Assignment/Initialization on the same evidence. Scientific prefix got the right label for a WRONG mechanism ('stale cached index'). There is no bug report at all.

**Presentation talking point:** 'Right for the wrong reason': a label-only metric scores scientific prefix as correct, but reading the turns shows the reasoning was invented. This is the strongest argument for manual turn-level analysis.

## The bug and the fix
**Fix in one line:** Copy-paste bug in `TimePeriodValues.updateBounds`: the max-middle block computes `s`/`e` from `getDataItem(this.minMiddleIndex)`; the fix uses `this.maxMiddleIndex`.

**Failing test(s) (shown to the model in both modes):**
- `org.jfree.data.time.junit.TimePeriodValuesTests::testGetMaxMiddleIndex` — `junit.framework.AssertionFailedError: expected:<1> but was:<3>`

**Developer fix diff (shown to the model ONLY in postfix):**
```diff
--- org.jfree.data.time.TimePeriodValues (buggy)
+++ org.jfree.data.time.TimePeriodValues (fixed)
@@ -297,9 +297,9 @@
         }
         
         if (this.maxMiddleIndex >= 0) {
-            long s = getDataItem(this.minMiddleIndex).getPeriod().getStart()
+            long s = getDataItem(this.maxMiddleIndex).getPeriod().getStart()
                 .getTime();
-            long e = getDataItem(this.minMiddleIndex).getPeriod().getEnd()
+            long e = getDataItem(this.maxMiddleIndex).getPeriod().getEnd()
                 .getTime();
             long maxMiddle = s + (e - s) / 2;
             if (middle > maxMiddle) {
```

## Ground-truth verdict and rationale
Two local variables (`s`, `e`) are initialized from the wrong field (`minMiddleIndex` instead of `maxMiddleIndex`). This is the same kind as Chart_11 (wrong object in an initializer), so for consistency: Assignment/Initialization. **Why Medium-High:** "wrong variable used in a computation" is exactly where models (and some human raters) split between Assignment/Initialization and Algorithm/Method.

## Step-by-step manual analysis
**Prefix / scientific (5 turns, 4 probes). No bug report is available (empty report).**
| Turn | Experiment | What came back |
|---|---|---|
| T1 | `snippet(org.jfree.data.time.TimePeriodValues)` | error: not in evidence store |
| T2 | `snippet(TimePeriodValues)` | `TimePeriodValuesTests` (test class, substring) |
| T3 | `list_evidence` | inventory: no production snippet for TimePeriodValues |
| T4 | repeat of T1 | blocked duplicate |
| T5 | conclude | **Assignment/Initialization 0.9** |

The concluding hypothesis: *"updates the cached index only when a new maximum is found, but does not handle cases where … indices shift when the list grows"*. That mechanism is **not** the bug (the bug is reading `minMiddleIndex` where `maxMiddleIndex` was meant). The label is right; the reasoning is fabricated from a single assertion (`expected:<1> but was:<3>` in `testGetMaxMiddleIndex`).

**Postfix / scientific (2 turns, 1 probe).** T1 stated the exact mechanism (*"uses the wrong index (minMiddleIndex instead of maxMiddleIndex)"*). The probe failed, and T2 concluded **Algorithm/Method 1.0**: *"the wrong variable was used in a comparison … a procedural error"*.

**Few-shot.** Prefix Algorithm/Method 0.8 (vague "procedural logic"). **Postfix Assignment/Initialization 1.0**: *"a classic case of using the wrong variable (an assignment/initialization error)"*.

**Discussion points.**
- The same diff, read by two prompting strategies, produced opposite labels. The "wrong variable" boundary between Assignment/Initialization and Algorithm/Method is the least stable boundary in the study.
- Grade reasoning separately from label. A two-column rubric (type correct? mechanism correct?) would score scientific prefix as ✓/✗ and postfix as ✗/✓.

## Checklist for the human reviewers
- [ ] Read the diff above and decide the ODC type independently **before** reading the model output.
- [ ] Do you agree with the ground truth **Assignment/Initialization**? If not, record your type and the reason.
- [ ] For each scientific turn: was the hypothesis consistent with what had been observed so far?
- [ ] Did any probe return **production** code, or only test classes / errors?
- [ ] Grade separately: *label correct?* and *mechanism/reasoning correct?*

---

## Appendix A — Bug report text given to the model (excerpt)
```text
(no bug report content)
```

## Appendix B — Verbatim model outputs (extracted from the artifacts)

### prefix · scientific-open → **Assignment/Initialization** ✅  (confidence 0.9)
Files: `.dist/study/artifacts_v2/prefix/Chart_7_prefix/classification.scientific-open.json`, `.dist/study/artifacts_v2/prefix/Chart_7_prefix/report.scientific-open.md`, `.dist/study/artifacts_v2/prefix/Chart_7_prefix/prompt.scientific-open.json`

Loop: 5 turn(s), 4 probe(s), termination `concluded`, 2 probe miss(es), 5 LLM call(s).

**Model reasoning summary:** The bug is an incorrect state update (Assignment/Initialization) where the cached index of the maximum value is not correctly maintained during additions to the collection.

- *Rejected alternative* **Algorithm/Method** — The issue is not the algorithm for finding the maximum, but the failure to correctly initialize/update the state variable holding the index.

#### Turn 1 — `request_evidence`
- **Hypothesis:** The method getMaxMiddleIndex() in TimePeriodValues is incorrectly tracking the index of the maximum middle value, likely due to an incorrect update logic when a new value is added that is not the new maximum, or failing to update when the maximum index changes due to additions.
- **Prediction:** The implementation of getMaxMiddleIndex() will show that it either caches the index incorrectly or fails to re-evaluate the index when the data set changes, leading to the observed stale index value of 3 instead of 1.
- **Experiment (probe):** `snippet(org.jfree.data.time.TimePeriodValues)`
- **Observation returned:** ERROR: no snippet matches 'org.jfree.data.time.TimePeriodValues'

#### Turn 2 — `request_evidence`
- **Hypothesis:** The class TimePeriodValues is likely in the package org.jfree.data.time, but the snippet probe failed because I used the wrong class name or it is not indexed under that exact string. I will try to list the files or use a broader search if possible, but since I cannot list files, I will try to infer the class name from the test class package.
- **Prediction:** The class is actually named TimePeriodValues and resides in org.jfree.data.time. I will try to request the snippet for 'TimePeriodValues' directly.
- **Experiment (probe):** `snippet(TimePeriodValues)`
- **Observation returned:** snippets: TimePeriodValuesTests (TEST)

#### Turn 3 — `request_evidence`
- **Hypothesis:** The class TimePeriodValues is not appearing in the snippet search, likely because it is not in the source directory or the search is restricted. I need to find the actual implementation of TimePeriodValues to see how it manages the index of the maximum middle value.
- **Prediction:** I will find the source code for TimePeriodValues by searching for the class name again, perhaps by checking the available classes more carefully or assuming it exists in the source tree.
- **Experiment (probe):** `list_evidence()`
- **Observation returned:** evidence inventory _(payload 27590 chars, truncated)_

#### Turn 4 — `request_evidence`
- **Hypothesis:** The class org.jfree.data.time.TimePeriodValues contains the logic for getMaxMiddleIndex(). The failure in the test case suggests that the internal state tracking the index of the maximum middle value is not being updated correctly when new data points are added, specifically when the new data point does not become the new maximum, or when the index needs to be recalculated.
- **Prediction:** The snippet for org.jfree.data.time.TimePeriodValues will reveal an incorrect update mechanism (e.g., a simple comparison that fails to account for index shifts or a stale cache) in the add() method or the getMaxMiddleIndex() method itself.
- **Experiment (probe):** `snippet(org.jfree.data.time.TimePeriodValues)`
- **Observation returned:** ERROR: probe already served this exact request — use a different probe or conclude

#### Turn 5 — `conclude`
- **Hypothesis:** The class TimePeriodValues maintains a cached index for the maximum middle value. When a new item is added, the code updates this cache only if the new item's middle value is greater than the current maximum. However, it fails to account for the fact that adding an item might shift the indices of existing items, or that the cached index itself might become invalid if the underlying data structure changes in a way that the cached index no longer points to the correct element.
- **Prediction:** The implementation of the add method in TimePeriodValues will show that it updates the cached index only when a new maximum is found, but does not handle cases where the maximum index might need to be re-evaluated or adjusted when the list grows.
- **Conclusion ODC type:** **Assignment/Initialization**


### prefix · few-open → **Algorithm/Method** ❌  (confidence 0.8)
Files: `.dist/study/artifacts_v2/prefix/Chart_7_prefix/classification.few-open.json`, `.dist/study/artifacts_v2/prefix/Chart_7_prefix/report.few-open.md`, `.dist/study/artifacts_v2/prefix/Chart_7_prefix/prompt.few-open.json`

**Model reasoning summary:** The failure indicates that the internal logic for tracking the index of the maximum middle value is incorrect. Since the method is responsible for maintaining and calculating this index based on the data added, the error lies in the procedural logic of the algorithm used to update or retrieve this index, rather than a simple missing guard or a static initialization error.

- *Rejected alternative* **Assignment/Initialization** — While the index value is wrong, the error is likely in the logic that updates the index during the 'add' operation, which is an algorithmic process rather than a simple initialization error.
- *Rejected alternative* **Checking** — There is no evidence of a missing guard or condition; the failure is in the result of a calculation.


### postfix · scientific-open → **Algorithm/Method** ❌  (confidence 1.0)
Files: `.dist/study/artifacts_v2/postfix/Chart_7_postfix/classification.scientific-open.json`, `.dist/study/artifacts_v2/postfix/Chart_7_postfix/report.scientific-open.md`, `.dist/study/artifacts_v2/postfix/Chart_7_postfix/prompt.scientific-open.json`

Loop: 2 turn(s), 1 probe(s), termination `concluded`, 1 probe miss(es), 2 LLM call(s).

**Model reasoning summary:** The bug is a classic implementation error where the wrong variable was used in a comparison, affecting the outcome of the algorithm. This fits the definition of Algorithm/Method as it is a procedural error in the implementation of the calculation.

- *Rejected alternative* **Assignment/Initialization** — The error is not in the initialization of the variable, but in the logic used to update it during the execution of the method.
- *Rejected alternative* **Checking** — The error is not a missing or incorrect guard, but an incorrect variable reference in a calculation.

#### Turn 1 — `request_evidence`
- **Hypothesis:** The method getMaxMiddleIndex in TimePeriodValues uses the wrong index (minMiddleIndex instead of maxMiddleIndex) when calculating the middle point of the time period to compare against the current maximum middle index, leading to incorrect updates of the maxMiddleIndex field.
- **Prediction:** The source code for org.jfree.data.time.TimePeriodValues will show that the logic for updating maxMiddleIndex incorrectly references minMiddleIndex in the comparison calculation.
- **Experiment (probe):** `snippet(org.jfree.data.time.TimePeriodValues)`
- **Observation returned:** ERROR: no snippet matches 'org.jfree.data.time.TimePeriodValues'

#### Turn 2 — `conclude`
- **Hypothesis:** The class org.jfree.data.time.TimePeriodValues is the correct class containing the bug, but the snippet probe failed because the class name was not in the provided list. I will assume the logic error is within the method that calculates the max middle index, which is an algorithmic error in the procedure.
- **Prediction:** The logic for updating the maxMiddleIndex uses the wrong index variable (minMiddleIndex instead of maxMiddleIndex) during the comparison, which is a procedural error.
- **Conclusion ODC type:** **Algorithm/Method**


### postfix · few-open → **Assignment/Initialization** ✅  (confidence 1.0)
Files: `.dist/study/artifacts_v2/postfix/Chart_7_postfix/classification.few-open.json`, `.dist/study/artifacts_v2/postfix/Chart_7_postfix/report.few-open.md`, `.dist/study/artifacts_v2/postfix/Chart_7_postfix/prompt.few-open.json`

**Model reasoning summary:** The fix involved changing the variable used in the calculation from `minMiddleIndex` to `maxMiddleIndex`. This is a classic case of using the wrong variable (an assignment/initialization error) rather than a flaw in the algorithmic logic itself or a missing guard.

- *Rejected alternative* **Algorithm/Method** — While the calculation is part of a method, the root cause is specifically the use of the wrong variable (a state/assignment error) rather than a flaw in the computational strategy itself.

