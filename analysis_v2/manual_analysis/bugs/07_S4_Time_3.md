# 07 · Time_3 — Drift: Prefix WRONG, Postfix CORRECT (oracle helped)

| | Scientific-open | Few-open |
|---|---|---|
| **Prefix** | Algorithm/Method (0.9) ❌ | Algorithm/Method (0.9) ❌ |
| **Postfix** | Checking (1.0) ✅ | Checking (1.0) ✅ |

- **Manual ground truth:** **Checking** (confidence: High (see caveat))
- **Bug report:** https://github.com/JodaOrg/joda-time/issues/77
- **Modified class (Defects4J oracle):** `org.joda.time.MutableDateTime`
- **Scientific loop:** prefix 2 turns / 1 probes · postfix 1 turns / 0 probes
- **Buggy class present in evidence store:** no · **retrieved by a prefix probe:** no
- **Artifacts:** `.dist/study/artifacts_v2/prefix/Time_3_prefix/`, `.dist/study/artifacts_v2/postfix/Time_3_postfix/`

## Why this bug was shortlisted
Suggested by the team. Prefix scientific PREDICTED THE EXACT FIX ('do not contain an if (amount == 0) return; guard') yet labeled Algorithm/Method; postfix corrected to Checking. Few-shot drifted identically.

**Presentation talking point:** 'Right mechanism, wrong label': in prefix the model classifies by its idea of the root cause (DST side effects) instead of the nature of the fix. Both strategies drift the same way, so the drift is evidence-driven, not strategy-driven.

## The bug and the fix
**Fix in one line:** Adds `if (amount != 0) { ... }` guards around `setMillis(...)` in `add(DurationFieldType,int)` and in all 10 `addYears/Months/Weeks/Days/Hours/Minutes/Seconds/Millis/Weekyears` methods. Nothing else changes.

**Failing test(s) (shown to the model in both modes):**
- `org.joda.time.TestMutableDateTime_Adds::testAddYears_int_dstOverlapWinter_addZero` — `junit.framework.ComparisonFailure: expected:<...10-30T02:30:00.000+0[1]:00> but was:<...10-30T02:30:00.000+0[2]:00>`
- `org.joda.time.TestMutableDateTime_Adds::testAddDays_int_dstOverlapWinter_addZero` — `junit.framework.ComparisonFailure: expected:<...10-30T02:30:00.000+0[1]:00> but was:<...10-30T02:30:00.000+0[2]:00>`
- `org.joda.time.TestMutableDateTime_Adds::testAddWeeks_int_dstOverlapWinter_addZero` — `junit.framework.ComparisonFailure: expected:<...10-30T02:30:00.000+0[1]:00> but was:<...10-30T02:30:00.000+0[2]:00>`
- `org.joda.time.TestMutableDateTime_Adds::testAdd_DurationFieldType_int_dstOverlapWinter_addZero` — `junit.framework.ComparisonFailure: expected:<...10-30T02:30:00.000+0[1]:00> but was:<...10-30T02:30:00.000+0[2]:00>`
- `org.joda.time.TestMutableDateTime_Adds::testAddMonths_int_dstOverlapWinter_addZero` — `junit.framework.ComparisonFailure: expected:<...10-30T02:30:00.000+0[1]:00> but was:<...10-30T02:30:00.000+0[2]:00>`

**Developer fix diff (shown to the model ONLY in postfix):**
```diff
--- org.joda.time.MutableDateTime (buggy)
+++ org.joda.time.MutableDateTime (fixed)
@@ -636,7 +636,9 @@
         if (type == null) {
             throw new IllegalArgumentException("Field must not be null");
         }
+        if (amount != 0) {
             setMillis(type.getField(getChronology()).add(getMillis(), amount));
+        }
     }
 
     //-----------------------------------------------------------------------
@@ -657,7 +659,9 @@
      * @throws IllegalArgumentException if the value is invalid
      */
     public void addYears(final int years) {
+        if (years != 0) {
             setMillis(getChronology().years().add(getMillis(), years));
+        }
     }
 
     //-----------------------------------------------------------------------
@@ -678,7 +682,9 @@
      * @throws IllegalArgumentException if the value is invalid
      */
     public void addWeekyears(final int weekyears) {
+        if (weekyears != 0) {
             setMillis(getChronology().weekyears().add(getMillis(), weekyears));
+        }
     }
 
     //-----------------------------------------------------------------------
@@ -699,7 +705,9 @@
      * @throws IllegalArgumentException if the value is invalid
      */
     public void addMonths(final int months) {
+        if (months != 0) {
             setMillis(getChronology().months().add(getMillis(), months));
+        }
     }
 
     //-----------------------------------------------------------------------
@@ -720,7 +728,9 @@
      * @throws IllegalArgumentException if the value is invalid
      */
     public void addWeeks(final int weeks) {
+        if (weeks != 0) {
             setMillis(getChronology().weeks().add(getMillis(), weeks));
+        }
     }
 
     //-----------------------------------------------------------------------
@@ -761,7 +771,9 @@
      * @throws IllegalArgumentException if the value is invalid
      */
     public void addDays(final int days) {
+        if (days != 0) {
             setMillis(getChronology().days().add(getMillis(), days));
+        }
     }
 
     //-----------------------------------------------------------------------
@@ -782,7 +794,9 @@
      * @throws IllegalArgumentException if the value is invalid
      */
     public void addHours(final int hours) {
+        if (hours != 0) {
             setMillis(getChronology().hours().add(getMillis(), hours));
+        }
     }
     
     //-----------------------------------------------------------------------
@@ -813,7 +827,9 @@
      * @throws IllegalArgumentException if the value is invalid
      */
     public void addMinutes(final int minutes) {
+        if (minutes != 0) {
             setMillis(getChronology().minutes().add(getMillis(), minutes));
+        }
     }
 
     //-----------------------------------------------------------------------
@@ -844,7 +860,9 @@
      * @throws IllegalArgumentException if the value is invalid
      */
     public void addSeconds(final int seconds) {
+        if (seconds != 0) {
             setMillis(getChronology().seconds().add(getMillis(), seconds));
+        }
     }
 
     //-----------------------------------------------------------------------
@@ -877,7 +895,9 @@
      * @throws IllegalArgumentException if the value is invalid
      */
     public void addMillis(final int millis) {
+        if (millis != 0) {
             setMillis(getChronology().millis().add(getMillis(), millis));
+        }
     }
 
     //-----------------------------------------------------------------------
```

## Ground-truth verdict and rationale
Every hunk of the fix is the same missing guard: skip the mutation when the amount is zero. ODC Checking: *"missing or incorrect validation of parameters or data in conditional statements"*. **Caveat:** one can argue the deeper root cause is the chronology's DST-overlap arithmetic (adding 0 should not change the offset) and the guard is a workaround. ODC classifies by the fix that was made, hence Checking.

## Step-by-step manual analysis
**Prefix / scientific (2 turns, 1 probe).**
1. *T1 hypothesis* — the add methods for larger units perform a recalculation during the DST overlap even when the amount is 0, while smaller units short-circuit. Built from the failing tests (`testAddYears_int_dstOverlapWinter_addZero`, `…AddDays…`) and the report ("addDays(0) changes value of MutableDateTime").
2. *T1 experiment* — `snippet(MutableDateTime)` returned only `TestMutableDateTime_Adds` (substring match; `MutableDateTime` production source is not in the store). The test snippet confirms the expected `+01:00` vs actual `+02:00`, but reveals nothing about the implementation.
3. *T2 conclusion* — the prediction is *"`addDays`, `addMonths`, and `addYears` … do not contain an `if (amount == 0) return;` guard"*, which **is the fix**. Yet the label is **Algorithm/Method 0.9**, reasoning that "the code performs unnecessary calculations that trigger side effects", with Checking listed as the rejected alternative.

**Postfix / scientific (1 turn, 0 probes).** It saw `if (amount != 0)` repeated across the diff and concluded Checking 1.0: *"a classic example of a missing guard condition"*.

**Few-shot.** Exactly the same flip (Algorithm/Method 0.9 → Checking 1.0). The few-shot prefix run even wrote *"adding a check for 'if (amount == 0) return;' would fix the symptom, [but] the root cause is … the underlying calculation"*.

**Discussion points.**
- ODC is a *fix-based* taxonomy. Without the fix, the model has to choose between "what would fix it" and "what caused it", and here it chose the cause. This is the conceptual ceiling of pre-fix classification.
- Because few-shot and scientific agree in both modes, the loop neither helped nor hurt; the evidence mode alone decided the label.

## Checklist for the human reviewers
- [ ] Read the diff above and decide the ODC type independently **before** reading the model output.
- [ ] Do you agree with the ground truth **Checking**? If not, record your type and the reason.
- [ ] For each scientific turn: was the hypothesis consistent with what had been observed so far?
- [ ] Did any probe return **production** code, or only test classes / errors?
- [ ] Grade separately: *label correct?* and *mechanism/reasoning correct?*

---

## Appendix A — Bug report text given to the model (excerpt)
```text
Title: addDays(0) changes value of MutableDateTime
Labels: Bug, Fixed

Description:
Upon DST transition from summer to winter time zone, adding the amount of zero days to a mutable date time object changes the value of the object.

The code

``` java
final MutableDateTime mdt = new MutableDateTime(2011, 10, 30, 3, 0, 0, 0, DateTimeZone.forID("Europe/Berlin"));
System.out.println("Start date:   " + mdt + " (" + mdt.toInstant().getMillis() + ")");
mdt.addHours(-1);
System.out.println("addHours(-1): " + mdt + " (" + mdt.toInstant().getMillis() + ")");
mdt.addHours(0);
System.out.println("addHours(0):  " + mdt + " (" + mdt.toInstant().getMillis() + ")");
mdt.addDays(0);
System.out.println("addDays(0):   " + mdt + " (" + mdt.toInstant().getMillis() + ")");
```

prints

```
Start date:   2011-10-30T03:00:00.000+01:00 (1319940000000)    //OK
addHours(-1): 2011-10-30T02:00:00.000+01:00 (1319936400000)    //OK
addHours(0):  2011-10-30T02:00:00.000+01:00 (1319936400000)    //OK, no change in time
addDays(0):   2011-10-30T02:00:00.000+02:00 (1319932800000)    //error, time has changed by 1 hour
```

The methods addMonths and addYears show the same problem; addSeconds, addMinutes and addHours are ok.

I have tested with version 2.3. However, if I repeat the test with Joda 1.5.2, the invocation of addDays(0) does not change the date's value.
```

## Appendix B — Verbatim model outputs (extracted from the artifacts)

### prefix · scientific-open → **Algorithm/Method** ❌  (confidence 0.9)
Files: `.dist/study/artifacts_v2/prefix/Time_3_prefix/classification.scientific-open.json`, `.dist/study/artifacts_v2/prefix/Time_3_prefix/report.scientific-open.md`, `.dist/study/artifacts_v2/prefix/Time_3_prefix/prompt.scientific-open.json`

Loop: 2 turn(s), 1 probe(s), termination `concluded`, 0 probe miss(es), 2 LLM call(s).

**Model reasoning summary:** The bug is a failure to handle the identity case (adding 0) in the `add` methods for larger time units. This is an algorithmic/procedural defect because the code performs unnecessary calculations that trigger side effects (offset re-normalization) during DST transitions. It is not a design-level capability gap (Function/Class/Object) nor a simple initialization error (Assignment/Initialization).

- *Rejected alternative* **Checking** — While adding a check (if amount == 0) is a form of checking, the root cause is the execution of an unnecessary algorithm that causes state corruption, making it an algorithmic/procedural issue.

#### Turn 1 — `request_evidence`
- **Hypothesis:** The `add` methods for larger time units (days, months, years) in `MutableDateTime` (or its underlying field implementation) perform an unnecessary or incorrect recalculation of the local time during DST transitions even when the added amount is zero, whereas smaller units (hours, minutes, seconds) correctly short-circuit or handle the zero-addition case without triggering a re-normalization of the offset.
- **Prediction:** I expect to find that the `add` methods for days, months, and years in `MutableDateTime` or the corresponding `DateTimeField` implementations do not check if the amount to add is zero before proceeding with the full field-based calculation, which triggers a re-evaluation of the DST offset.
- **Experiment (probe):** `snippet(MutableDateTime)`
- **Observation returned:** snippets: TestMutableDateTime_Adds (PRODUCTION) _(payload 9670 chars, truncated)_

#### Turn 2 — `conclude`
- **Hypothesis:** The `MutableDateTime` class (or its base class `BaseDateTime`/`AbstractDateTime`) lacks a short-circuit check for zero-value additions in its `addDays`, `addMonths`, and `addYears` methods. When these methods are called with an argument of 0, they proceed to perform a full field-based calculation. During a DST transition, this calculation re-normalizes the time against the current time zone, which can lead to an incorrect offset selection if the internal state is already at a specific point in the transition overlap.
- **Prediction:** I expect to see that the `addDays`, `addMonths`, and `addYears` methods in `MutableDateTime` do not contain an `if (amount == 0) return;` guard, causing them to invoke the underlying field's `add` method unnecessarily.
- **Conclusion ODC type:** **Algorithm/Method**


### prefix · few-open → **Algorithm/Method** ❌  (confidence 0.9)
Files: `.dist/study/artifacts_v2/prefix/Time_3_prefix/classification.few-open.json`, `.dist/study/artifacts_v2/prefix/Time_3_prefix/report.few-open.md`, `.dist/study/artifacts_v2/prefix/Time_3_prefix/prompt.few-open.json`

**Model reasoning summary:** The bug is a procedural error in the calculation logic for adding time fields. When adding zero, the method should ideally return early or perform no calculation, but instead, it triggers a recalculation of the date-time that incorrectly shifts the offset during a DST overlap. This is a flaw in the computational procedure (the algorithm) used to handle time field additions, not a missing guard (Checking) or a simple wrong constant (Assignment).

- *Rejected alternative* **Checking** — While adding a check for 'if (amount == 0) return;' would fix the symptom, the root cause is that the underlying calculation algorithm incorrectly handles the state transition during DST, which is a procedural logic error.
- *Rejected alternative* **Assignment/Initialization** — The issue is not an incorrect initial value or constant, but an incorrect procedural calculation when performing an addition operation.


### postfix · scientific-open → **Checking** ✅  (confidence 1.0)
Files: `.dist/study/artifacts_v2/postfix/Time_3_postfix/classification.scientific-open.json`, `.dist/study/artifacts_v2/postfix/Time_3_postfix/report.scientific-open.md`, `.dist/study/artifacts_v2/postfix/Time_3_postfix/prompt.scientific-open.json`

Loop: 1 turn(s), 0 probe(s), termination `concluded`, 0 probe miss(es), 1 LLM call(s).

**Model reasoning summary:** The bug is a classic example of a missing guard condition. The code performs a calculation even when the input is zero, which, due to the complexity of DST transitions in the underlying chronology, results in an incorrect state change. Adding the check 'if (amount != 0)' prevents this unnecessary and incorrect calculation.

- *Rejected alternative* **Algorithm/Method** — While the calculation itself might be considered part of the algorithm, the root cause is the lack of a guard to skip the operation when it is a no-op, which is the definition of a Checking defect.

#### Turn 1 — `conclude`
- **Hypothesis:** The bug is caused by the absence of a guard condition (amount != 0) in the add methods of MutableDateTime. When adding zero, the underlying chronology calculation incorrectly re-evaluates the time in the context of a DST transition, leading to an unexpected shift in the time zone offset.
- **Prediction:** I expect to see that the add methods in MutableDateTime perform the calculation regardless of whether the input amount is zero, and that adding a zero amount triggers a recalculation that is sensitive to DST transitions.
- **Conclusion ODC type:** **Checking**


### postfix · few-open → **Checking** ✅  (confidence 1.0)
Files: `.dist/study/artifacts_v2/postfix/Time_3_postfix/classification.few-open.json`, `.dist/study/artifacts_v2/postfix/Time_3_postfix/report.few-open.md`, `.dist/study/artifacts_v2/postfix/Time_3_postfix/prompt.few-open.json`

**Model reasoning summary:** The fix involves adding a conditional check (if amount != 0) to prevent unnecessary and incorrect recalculations of the internal millisecond state when the addition amount is zero. This is a classic case of a missing guard/validation check to prevent side effects in a state-mutating operation.

- *Rejected alternative* **Algorithm/Method** — While the underlying calculation might be complex, the root cause is the lack of a guard to skip the calculation entirely when the input is zero, which is a Checking issue.

