# 08 · Chart_11 — Drift: Prefix WRONG, Postfix CORRECT (oracle helped)

| | Scientific-open | Few-open |
|---|---|---|
| **Prefix** | Algorithm/Method (1.0) ❌ | Algorithm/Method (0.9) ❌ |
| **Postfix** | Assignment/Initialization (1.0) ✅ | Assignment/Initialization (1.0) ✅ |

- **Manual ground truth:** **Assignment/Initialization** (confidence: High)
- **Bug report:** https://sourceforge.net/p/jfreechart/bugs/868
- **Modified class (Defects4J oracle):** `org.jfree.chart.util.ShapeUtilities`
- **Scientific loop:** prefix 5 turns / 4 probes · postfix 2 turns / 1 probes
- **Buggy class present in evidence store:** no · **retrieved by a prefix probe:** no
- **Artifacts:** `.dist/study/artifacts_v2/prefix/Chart_11_prefix/`, `.dist/study/artifacts_v2/postfix/Chart_11_postfix/`

## Why this bug was shortlisted
Most visual one-token bug. The prefix loop spent 5 turns and 4 probes without ever reaching the buggy class (it isn't in context.json), still concluded with confidence 1.0 (Algorithm/Method). Postfix corrected to Assignment/Initialization.

**Presentation talking point:** Evidence starvation: failed experiments did not lower the model's confidence. The loop's value depends entirely on what context.json contains.

## The bug and the fix
**Fix in one line:** Copy-paste typo: `PathIterator iterator2 = p1.getPathIterator(null);` -> `p2.getPathIterator(null);`.

**Failing test(s) (shown to the model in both modes):**
- `org.jfree.chart.util.junit.ShapeUtilitiesTests::testEqualGeneralPaths` — `junit.framework.AssertionFailedError`

**Developer fix diff (shown to the model ONLY in postfix):**
```diff
--- org.jfree.chart.util.ShapeUtilities (buggy)
+++ org.jfree.chart.util.ShapeUtilities (fixed)
@@ -272,7 +272,7 @@
             return false;
         }
         PathIterator iterator1 = p1.getPathIterator(null);
-        PathIterator iterator2 = p1.getPathIterator(null);
+        PathIterator iterator2 = p2.getPathIterator(null);
         double[] d1 = new double[6];
         double[] d2 = new double[6];
         boolean done = iterator1.isDone() && iterator2.isDone();
```

## Ground-truth verdict and rationale
A local variable is initialized from the wrong object (`p1` instead of `p2`). The comparison algorithm itself is correct once `iterator2` holds the right value. ODC Assignment/Initialization: *"an internal variable … had an incorrect value"*.

## Step-by-step manual analysis
**Prefix / scientific (5 turns, 4 probes). The loop is visible but gains nothing.**
| Turn | Experiment | What came back |
|---|---|---|
| T1 | `snippet(org.jfree.chart.util.ShapeUtilities)` | error: no snippet matches (+ list of available classes: only "most-executed" interfaces) |
| T2 | `snippet(ShapeUtilities)` | `ShapeUtilitiesTests` (**test** class, substring match) |
| T3 | `list_evidence` | inventory confirming there is no production snippet for ShapeUtilities |
| T4 | repeat of T1 | blocked: "probe already served this exact request" |
| T5 | conclude | **Algorithm/Method, confidence 1.0** |

The hypotheses were close to the truth ("uses the same PathIterator for both paths / fails to create independent iterators") but framed as an *iteration-logic* error. After T3 showed the evidence doesn't exist, the correct scientific move would have been to lower confidence or flag `needs_human_review`; instead confidence stayed at 1.0.

**Postfix / scientific (2 turns, 1 probe).** T1 stated the exact mechanism (iterator2 initialized from p1). The probe failed the same way. T2 concluded Assignment/Initialization 1.0 "given … the fix diff provided in the initial information".

**Few-shot.** Algorithm/Method → Assignment/Initialization, the same flip.

**Discussion points.**
- The pipeline's collection step only snapshots stack-frame classes and "most-executed" classes. For assertion failures where the buggy method is not on the stack, the probes cannot reach it (the buggy class was available in only 105/257 contexts).
- Calibration: `confidence` is not reduced by failed experiments, so it should not be read as evidence quality.

## Checklist for the human reviewers
- [ ] Read the diff above and decide the ODC type independently **before** reading the model output.
- [ ] Do you agree with the ground truth **Assignment/Initialization**? If not, record your type and the reason.
- [ ] For each scientific turn: was the hypothesis consistent with what had been observed so far?
- [ ] Did any probe return **production** code, or only test classes / errors?
- [ ] Grade separately: *label correct?* and *mechanism/reasoning correct?*

---

## Appendix A — Bug report text given to the model (excerpt)
```text
JFreeChart / Bugs / #868 JCommon 1.0.12 ShapeUtilities.equal(path1,path2) Join/Login Business Software Open Source Software For Vendors Blog About More Articles Create SourceForge Podcast Site Documentation Subscribe to our Newsletter Support Request JCommon 1.0.12 ShapeUtilities.equal(path1,path2) Brought to you by: mungady , taqua This project can now be found here. Summary Files Reviews Support Mailing Lists Tickets ▾ Patches Bugs Feature Requests News Code Cvs Menu ▾ ▴ Create Ticket View Stats Group 1.0.x Searches Changes Closed Tickets Open Tickets Help Formatting Help #868 JCommon 1.0.12 ShapeUtilities.equal(path1,path2) Status: closed-fixed Owner: David Gilbert Labels: jcommon (9) Priority: 5 Updated: 2008-06-02 Created: 2008-05-29 Creator: Peter Kolb Private: No The comparison of two GeneralPath objects uses the same PathIterator for both objects. equal(GeneralPath path1, GeneralPath path2) will thus return true for any pair of non-null GeneralPath instances having the same windingRule. Discussion David Gilbert - 2008-06-01 assigned_to : nobody --> mungady If you would like to refer to this comment somewhere else in this project, copy and paste the following link: David Gilbert - 2008-06-01 Logged In: YES user_id=112975 Originator: NO Thanks for the report. I fixed the bug, which then (when rerunning the JUnit tests) uncovered a bug in the serialization for GeneralPath. I'll commit the fixes to CVS shortly. Regards, Dave Gilbert JFreeChart Project Leader If you would  …
```

## Appendix B — Verbatim model outputs (extracted from the artifacts)

### prefix · scientific-open → **Algorithm/Method** ❌  (confidence 1.0)
Files: `.dist/study/artifacts_v2/prefix/Chart_11_prefix/classification.scientific-open.json`, `.dist/study/artifacts_v2/prefix/Chart_11_prefix/report.scientific-open.md`, `.dist/study/artifacts_v2/prefix/Chart_11_prefix/prompt.scientific-open.json`

Loop: 5 turn(s), 4 probe(s), termination `concluded`, 2 probe miss(es), 5 LLM call(s).

**Model reasoning summary:** The bug is a classic algorithmic error where the implementation of a comparison method fails to correctly iterate over the data structures it is comparing, leading to incorrect results. This is a procedural logic error within the method itself.

- *Rejected alternative* **Checking** — The issue is not a missing guard or validation, but an incorrect implementation of the comparison algorithm itself.

#### Turn 1 — `request_evidence`
- **Hypothesis:** The ShapeUtilities.equal(GeneralPath, GeneralPath) method incorrectly compares two GeneralPath objects by using the same PathIterator instance for both, which causes the iterator to advance incorrectly or share state, leading to false positives (returning true when paths are different).
- **Prediction:** The implementation of ShapeUtilities.equal will show that it retrieves a PathIterator from one path and uses it to iterate through both paths, or fails to create independent iterators for each path, resulting in incorrect equality checks.
- **Experiment (probe):** `snippet(org.jfree.chart.util.ShapeUtilities)`
- **Observation returned:** ERROR: no snippet matches 'org.jfree.chart.util.ShapeUtilities'

#### Turn 2 — `request_evidence`
- **Hypothesis:** The ShapeUtilities class is likely located in a different package or the snippet request failed due to a naming mismatch. Given the test class is org.jfree.chart.util.junit.ShapeUtilitiesTests, the class under test is almost certainly org.jfree.chart.util.ShapeUtilities.
- **Prediction:** Requesting the snippet for 'ShapeUtilities' will return the source code for the class, confirming the flawed implementation of the equal method.
- **Experiment (probe):** `snippet(ShapeUtilities)`
- **Observation returned:** snippets: ShapeUtilitiesTests (TEST)

#### Turn 3 — `request_evidence`
- **Hypothesis:** The ShapeUtilities.equal method is failing to correctly compare two GeneralPath objects because it likely uses a single PathIterator or fails to iterate through both paths independently, leading to incorrect equality results.
- **Prediction:** The source code for ShapeUtilities.equal will reveal that it either uses one iterator for both paths or has a logic error in the iteration loop that prevents it from detecting differences in the path segments.
- **Experiment (probe):** `list_evidence()`
- **Observation returned:** evidence inventory _(payload 27587 chars, truncated)_

#### Turn 4 — `request_evidence`
- **Hypothesis:** The ShapeUtilities.equal(GeneralPath, GeneralPath) method is flawed because it uses a single PathIterator instance to iterate over both paths simultaneously, or fails to properly reset/compare the segments of both paths, leading to incorrect equality results when the paths differ.
- **Prediction:** The source code for ShapeUtilities.equal will show that it retrieves a PathIterator from one path and uses it to compare against the other, or otherwise fails to maintain independent iteration state for both paths.
- **Experiment (probe):** `snippet(org.jfree.chart.util.ShapeUtilities)`
- **Observation returned:** ERROR: probe already served this exact request — use a different probe or conclude

#### Turn 5 — `conclude`
- **Hypothesis:** The ShapeUtilities.equal method is flawed because it uses a single PathIterator instance to iterate over both paths simultaneously, or fails to properly reset/compare the segments of both paths, leading to incorrect equality results when the paths differ.
- **Prediction:** The source code for ShapeUtilities.equal will show that it retrieves a PathIterator from one path and uses it to compare against the other, or otherwise fails to maintain independent iteration state for both paths.
- **Conclusion ODC type:** **Algorithm/Method**


### prefix · few-open → **Algorithm/Method** ❌  (confidence 0.9)
Files: `.dist/study/artifacts_v2/prefix/Chart_11_prefix/classification.few-open.json`, `.dist/study/artifacts_v2/prefix/Chart_11_prefix/report.few-open.md`, `.dist/study/artifacts_v2/prefix/Chart_11_prefix/prompt.few-open.json`

**Model reasoning summary:** The bug is a failure in the computational logic used to compare two objects. The method uses a PathIterator incorrectly, leading to an incorrect result (always true for same winding rule). This is a procedural error in the implementation of the equality algorithm, not a missing guard (Checking), a wrong constant (Assignment), or a design-level capability gap (Function/Class/Object).

- *Rejected alternative* **Checking** — The issue is not a missing guard or condition, but an incorrect implementation of the comparison logic itself.
- *Rejected alternative* **Function/Class/Object** — The capability (equality check) exists, but the implementation of the algorithm is flawed.


### postfix · scientific-open → **Assignment/Initialization** ✅  (confidence 1.0)
Files: `.dist/study/artifacts_v2/postfix/Chart_11_postfix/classification.scientific-open.json`, `.dist/study/artifacts_v2/postfix/Chart_11_postfix/report.scientific-open.md`, `.dist/study/artifacts_v2/postfix/Chart_11_postfix/prompt.scientific-open.json`

Loop: 2 turn(s), 1 probe(s), termination `concluded`, 1 probe miss(es), 2 LLM call(s).

**Model reasoning summary:** The bug is a classic case of incorrect variable usage during initialization. The code intended to initialize an iterator for the second path (p2) but instead initialized it using the first path (p1). This is a direct assignment/initialization error.

- *Rejected alternative* **Algorithm/Method** — While it affects the method's logic, the root cause is a simple incorrect assignment of a variable, not a flaw in the algorithmic strategy itself.

#### Turn 1 — `request_evidence`
- **Hypothesis:** The bug is caused by an incorrect implementation of the ShapeUtilities.equal(GeneralPath, GeneralPath) method, where the second path iterator is incorrectly initialized using the first path (p1) instead of the second path (p2). This leads to the method always comparing a path against itself, resulting in incorrect equality checks.
- **Prediction:** The snippet of org.jfree.chart.util.ShapeUtilities will show that the PathIterator for the second path is initialized using p1 instead of p2.
- **Experiment (probe):** `snippet(org.jfree.chart.util.ShapeUtilities)`
- **Observation returned:** ERROR: no snippet matches 'org.jfree.chart.util.ShapeUtilities'

#### Turn 2 — `conclude`
- **Hypothesis:** The class name provided in the previous probe was slightly incorrect or the file is located in a different package structure than expected. Given the bug report and the fix diff provided in the initial information, the error is clearly an incorrect variable assignment in the ShapeUtilities class where p1 is used instead of p2 when initializing the second iterator.
- **Prediction:** The bug is an Assignment/Initialization error because the code incorrectly assigns the path iterator of p1 to the variable intended for p2, failing to correctly initialize the comparison state for the second object.
- **Conclusion ODC type:** **Assignment/Initialization**


### postfix · few-open → **Assignment/Initialization** ✅  (confidence 1.0)
Files: `.dist/study/artifacts_v2/postfix/Chart_11_postfix/classification.few-open.json`, `.dist/study/artifacts_v2/postfix/Chart_11_postfix/report.few-open.md`, `.dist/study/artifacts_v2/postfix/Chart_11_postfix/prompt.few-open.json`

**Model reasoning summary:** The fix involved changing the initialization of the second iterator (iterator2) from using p1 to using p2. This is a classic case of an incorrect variable assignment during initialization, where the wrong object was referenced, rather than a flaw in the algorithmic logic itself or a missing guard.

- *Rejected alternative* **Algorithm/Method** — While the logic is part of a method, the root cause is specifically the incorrect assignment of the source object for the second iterator, not a flaw in the computational steps or iteration strategy.

