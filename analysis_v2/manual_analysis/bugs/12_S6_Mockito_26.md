# 12 · Mockito_26 — Scientific vs Few-shot contrast

| | Scientific-open | Few-open |
|---|---|---|
| **Prefix** | Assignment/Initialization (0.9) ✅ | Algorithm/Method (0.8) ❌ |
| **Postfix** | Assignment/Initialization (1.0) ✅ | Assignment/Initialization (1.0) ✅ |

- **Manual ground truth:** **Assignment/Initialization** (confidence: High)
- **Bug report:** https://code.google.com/archive/p/mockito/issues/352
- **Modified class (Defects4J oracle):** `org.mockito.internal.util.Primitives`
- **Scientific loop:** prefix 5 turns / 4 probes · postfix 2 turns / 1 probes
- **Buggy class present in evidence store:** no · **retrieved by a prefix probe:** no
- **Artifacts:** `.dist/study/artifacts_v2/prefix/Mockito_26_prefix/`, `.dist/study/artifacts_v2/postfix/Mockito_26_postfix/`

## Why this bug was shortlisted
Scientific was correct in BOTH modes; few-shot prefix was wrong (Algorithm/Method). But the scientific win did not come from experiments: 4 prefix probes returned nothing new and the buggy class (Primitives) was never in the evidence store. (Scientific scenario: agree, correct.)

**Presentation talking point:** Scientific beats few-shot, honestly framed: the win came from how the hypothesis was phrased ('returns Integer 0 where Double 0.0 is expected' = a wrong value), not from the probes.

## The bug and the fix
**Fix in one line:** `primitiveValues.put(double.class, 0);` (autoboxes to Integer) -> `primitiveValues.put(double.class, 0D);`

**Failing test(s) (shown to the model in both modes):**
- `org.mockito.internal.progress.HandyReturnValuesTest::should_default_values_for_primitive` — `java.lang.ClassCastException: class java.lang.Integer cannot be cast to class java.lang.Double (java.lang.Integer and java.lang.Double are in module java.base of loader 'bootstrap')`
- `org.mockito.internal.stubbing.defaultanswers.ReturnsEmptyValuesTest::should_return_primitive` — `junit.framework.AssertionFailedError: expected:<0.0> but was:<0>`
- `org.mockito.internal.stubbing.defaultanswers.ReturnsMocksTest::should_return_the_usual_default_values_for_primitives` — `junit.framework.AssertionFailedError: expected:<0.0> but was:<0>`
- `org.mockito.internal.stubbing.defaultanswers.ReturnsSmartNullsTest::should_return_the_usual_default_values_for_primitives` — `junit.framework.AssertionFailedError: expected:<0.0> but was:<0>`

**Developer fix diff (shown to the model ONLY in postfix):**
```diff
--- org.mockito.internal.util.Primitives (buggy)
+++ org.mockito.internal.util.Primitives (fixed)
@@ -63,6 +63,6 @@
         primitiveValues.put(int.class, 0);
         primitiveValues.put(long.class, 0L);
         primitiveValues.put(float.class, 0F);
-        primitiveValues.put(double.class, 0);
+        primitiveValues.put(double.class, 0D);
     }
 }
```

## Ground-truth verdict and rationale
A single map entry is initialized with the wrong literal type. ODC Assignment/Initialization, with no ambiguity.

## Step-by-step manual analysis
**Prefix / scientific (5 turns, 4 probes).**
| Turn | Experiment | What came back |
|---|---|---|
| T1 | `snippet(HandyReturnValues)` | `HandyReturnValuesTest` (test class) |
| T2 | `snippet(HandyReturnValues)` again | blocked duplicate |
| T3 | `snippet(org.mockito.internal.progress.HandyReturnValues)` | `HandyReturnValuesTest` again (substring) |
| T4 | `snippet(HandyReturnValues)` again | blocked duplicate |
| T5 | conclude | **Assignment/Initialization 0.9** |

The evidence store for this bug holds **only three test classes**. The model never named `Primitives` in prefix. Its label comes from the symptoms: `ClassCastException: Integer cannot be cast to Double` and `expected:<0.0> but was:<0>`. The hypothesis "returning an Integer (0) when a Double (0.0) is expected" is phrased as a wrong value, and the label followed. The loop also shows a behavioural weakness: repeating a blocked probe twice.

**Postfix / scientific (2 turns, 1 probe).** `snippet(org.mockito.internal.util.Primitives)` → error (not in store). It concluded Assignment/Initialization 1.0 from the diff.

**Few-shot.** **Prefix Algorithm/Method 0.8**: *"the logic that maps types to their default values"*, explicitly rejecting Assignment/Initialization ("not just an incorrect constant value"). Postfix Assignment/Initialization 1.0.

**Discussion points.** Present this next to Math_104: the scientific-vs-few advantage flips between bugs, and in both cases the decisive factor is the framing of the hypothesis/reasoning, not new evidence gathered by probes.

## Checklist for the human reviewers
- [ ] Read the diff above and decide the ODC type independently **before** reading the model output.
- [ ] Do you agree with the ground truth **Assignment/Initialization**? If not, record your type and the reason.
- [ ] For each scientific turn: was the hypothesis consistent with what had been observed so far?
- [ ] Did any probe return **production** code, or only test classes / errors?
- [ ] Grade separately: *label correct?* and *mechanism/reasoning correct?*

---

## Appendix A — Bug report text given to the model (excerpt)
```text
Google Code Archive - Long-term storage for Google Code Project Hosting. Code Archive Skip to content Google About Google Privacy Terms
```

## Appendix B — Verbatim model outputs (extracted from the artifacts)

### prefix · scientific-open → **Assignment/Initialization** ✅  (confidence 0.9)
Files: `.dist/study/artifacts_v2/prefix/Mockito_26_prefix/classification.scientific-open.json`, `.dist/study/artifacts_v2/prefix/Mockito_26_prefix/report.scientific-open.md`, `.dist/study/artifacts_v2/prefix/Mockito_26_prefix/prompt.scientific-open.json`

Loop: 5 turn(s), 4 probe(s), termination `concluded`, 2 probe miss(es), 5 LLM call(s).

**Model reasoning summary:** The tests fail because the system returns 0 (Integer) when 0.0 (Double) is expected. This is a direct result of incorrect initialization or assignment logic within the default value provider.

- *Rejected alternative* **Algorithm/Method** — The issue is not the algorithm itself, but the specific value being returned for a given input type.

#### Turn 1 — `request_evidence`
- **Hypothesis:** The code responsible for returning default values for primitives (likely in HandyReturnValues or ReturnsEmptyValues) is incorrectly returning an Integer (0) when a Double (0.0) is expected, causing a type mismatch or assertion failure.
- **Prediction:** I expect to find a method that returns a default value for a given class type, where the logic for handling 'double.class' or 'Double.TYPE' is either missing or incorrectly returning an Integer instead of a Double.
- **Experiment (probe):** `snippet(HandyReturnValues)`
- **Observation returned:** snippets: HandyReturnValuesTest (TEST)

#### Turn 2 — `request_evidence`
- **Hypothesis:** The HandyReturnValues class is missing or has an incorrect implementation for returning the default value for double.class, causing it to return an Integer (0) instead of a Double (0.0).
- **Prediction:** I expect to see the implementation of HandyReturnValues.returnFor(Class) and find that it lacks a specific case for double.class or returns a default value that is not a double.
- **Experiment (probe):** `snippet(HandyReturnValues)`
- **Observation returned:** ERROR: probe already served this exact request — use a different probe or conclude

#### Turn 3 — `request_evidence`
- **Hypothesis:** The HandyReturnValues class is missing or has an incorrect implementation for returning the default value for double.class, causing it to return an Integer (0) instead of a Double (0.0).
- **Prediction:** I expect to find the implementation of HandyReturnValues.returnFor(Class) and see that it lacks a specific case for double.class or returns a default value that is not a double.
- **Experiment (probe):** `snippet(org.mockito.internal.progress.HandyReturnValues)`
- **Observation returned:** snippets: HandyReturnValuesTest (TEST)

#### Turn 4 — `request_evidence`
- **Hypothesis:** The HandyReturnValues class is missing the implementation for returning the default value for double.class, causing it to return an Integer (0) instead of a Double (0.0).
- **Prediction:** I expect to find the source code for HandyReturnValues and see that it lacks a specific case for double.class or returns a default value that is not a double.
- **Experiment (probe):** `snippet(HandyReturnValues)`
- **Observation returned:** ERROR: probe already served this exact request — use a different probe or conclude

#### Turn 5 — `conclude`
- **Hypothesis:** The HandyReturnValues class is missing or has an incorrect implementation for returning the default value for double.class, causing it to return an Integer (0) instead of a Double (0.0).
- **Prediction:** The implementation of HandyReturnValues.returnFor(Class) will show that it lacks a specific case for double.class or returns a default value that is not a double.
- **Conclusion ODC type:** **Assignment/Initialization**


### prefix · few-open → **Algorithm/Method** ❌  (confidence 0.8)
Files: `.dist/study/artifacts_v2/prefix/Mockito_26_prefix/classification.few-open.json`, `.dist/study/artifacts_v2/prefix/Mockito_26_prefix/report.few-open.md`, `.dist/study/artifacts_v2/prefix/Mockito_26_prefix/prompt.few-open.json`

**Model reasoning summary:** The failure occurs because the logic responsible for returning default values for primitives is incorrectly mapping or handling the primitive type conversion. This is a procedural error in the method responsible for determining the default return value, which is a classic Algorithm/Method defect. It is not a missing guard (Checking) or a simple initialization error (Assignment/Initialization), but rather an incorrect implementation of the logic that maps types to their default values.

- *Rejected alternative* **Assignment/Initialization** — The issue is not just an incorrect constant value, but a failure in the logic that determines which value to return based on the requested type.
- *Rejected alternative* **Interface/O-O Messages** — While it involves type handling, the core issue is the internal logic of the default value provider, not a mismatch in the interface contract between two components.


### postfix · scientific-open → **Assignment/Initialization** ✅  (confidence 1.0)
Files: `.dist/study/artifacts_v2/postfix/Mockito_26_postfix/classification.scientific-open.json`, `.dist/study/artifacts_v2/postfix/Mockito_26_postfix/report.scientific-open.md`, `.dist/study/artifacts_v2/postfix/Mockito_26_postfix/prompt.scientific-open.json`

Loop: 2 turn(s), 1 probe(s), termination `concluded`, 1 probe miss(es), 2 LLM call(s).

**Model reasoning summary:** The defect is a simple incorrect value assignment (0 instead of 0D) in a static initialization map. This fits the definition of Assignment/Initialization perfectly as it involves setting a value incorrectly rather than a procedural or structural logic error.

- *Rejected alternative* **Algorithm/Method** — The fix is a simple value correction, not a change to the algorithm or method logic.
- *Rejected alternative* **Checking** — There is no missing guard or conditional logic; the issue is the data being returned.

#### Turn 1 — `request_evidence`
- **Hypothesis:** The bug is caused by an incorrect initialization of the 'double.class' entry in the 'primitiveValues' map within the 'org.mockito.internal.util.Primitives' class. Specifically, it is being initialized with an integer '0' instead of a double '0D', leading to a ClassCastException or type mismatch when the framework attempts to return the default value for a double-returning method.
- **Prediction:** The 'org.mockito.internal.util.Primitives' class will contain a map initialization where 'double.class' is associated with the integer value '0'.
- **Experiment (probe):** `snippet(org.mockito.internal.util.Primitives)`
- **Observation returned:** ERROR: no snippet matches 'org.mockito.internal.util.Primitives'

#### Turn 2 — `conclude`
- **Hypothesis:** The class 'org.mockito.internal.util.Primitives' exists but was not found by the snippet probe due to a naming or path mismatch in the environment. The bug is an incorrect initialization of the default value for 'double.class' in a static map, which is a classic Assignment/Initialization defect.
- **Prediction:** The class 'org.mockito.internal.util.Primitives' will contain a static block or constructor that initializes 'primitiveValues.put(double.class, 0)' instead of '0D'.
- **Conclusion ODC type:** **Assignment/Initialization**


### postfix · few-open → **Assignment/Initialization** ✅  (confidence 1.0)
Files: `.dist/study/artifacts_v2/postfix/Mockito_26_postfix/classification.few-open.json`, `.dist/study/artifacts_v2/postfix/Mockito_26_postfix/report.few-open.md`, `.dist/study/artifacts_v2/postfix/Mockito_26_postfix/prompt.few-open.json`

**Model reasoning summary:** The fix involved changing the value assigned to the 'double.class' key in the 'primitiveValues' map from '0' (an integer) to '0D' (a double). This is a classic case of an incorrect initialization value for a specific type in a lookup table.

- *Rejected alternative* **Algorithm/Method** — The fix is not a change to the procedural logic or algorithm, but a correction of a single incorrect constant value in an initialization map.

