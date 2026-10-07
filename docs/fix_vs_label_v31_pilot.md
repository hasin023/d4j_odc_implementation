# Predicted fix vs ODC label — v3.1 scientific pilot (13 bugs)

**Question.** When the model gets the fix right, does it also get the ODC type right?

**Data.** `scientific-open`, prompt `v3.1-2026-10-07`, model `gemini-3.1-flash-lite`, the 13 bugs of
`manifest_alvee13.json`, run 2026-10-07 into `.dist/study/artifacts_v3/` (a repeat run into
`artifacts_v3_repeat1/` gave identical output). For each run: `predicted_fix` from
`classification.scientific-open.json`, compared with the real patch (`fix_diff` in the post-fix
`context.json`, never shown to the pre-fix run). Manual labels: `analysis_v2/manual_analysis/shortlist.csv`
(one rater).

**How the fix was judged.** By reading, not by a script — these are judgments for the team to check.
- **right**: the same change in substance as the patch (same place, same effect), even if written differently
- **same place, different change**: the right method or line, but a change the patch does not make
- **wrong**: a different place and change

## Pre-fix (the model never saw the patch)

| Bug | Predicted fix | Real patch | Fix | Model label | Manual label |
|---|---|---|---|---|---|
| Chart_9 | add `if (endIndex < startIndex) emptyRange = true` (written as a rewrite of the index block) | `if ((endIndex < 0) \|\| (endIndex < startIndex))` | right | Algorithm/Method | Checking |
| Math_17 | handle any `x` with the general multiplication instead of failing the range check | `if (x >= 0 && x < RADIX)` fast path, else `multiply(newInstance(x))` | right | Algorithm/Method | Checking |
| Time_3 | `if (amount != 0) { setMillis(...) }` | `if (x != 0)` guard around `setMillis` in every `add*` method | right (one method of many) | Algorithm/Method | Checking |
| Chart_11 | line 275: `p1.getPathIterator` → `p2.getPathIterator` | the same | right (exact) | Algorithm/Method | Assignment/Initialization |
| Chart_7 | lines 300/302: `minMiddleIndex` → `maxMiddleIndex` | the same | right (exact) | Algorithm/Method | Assignment/Initialization |
| Math_23 | track a `best` point from the start, update it each iteration, return it | the same | right | Algorithm/Method ✓ | Algorithm/Method |
| Math_104 | `DEFAULT_EPSILON` 1.0e-9 → 1.0e-15 | `DEFAULT_EPSILON` 10e-9 → 10e-15 | right constant and direction; values written off by 10× | Assignment/Initialization ✓ | Assignment/Initialization |
| Mockito_26 | `primitiveValues.put(double.class, 0D)` | the same | right (exact) | Assignment/Initialization ✓ | Assignment/Initialization |
| Lang_40 | `toUpperCase(Locale.ENGLISH)` on both strings | replace the `toUpperCase` comparison by a `regionMatches(true, …)` loop | same place, different change | Algorithm/Method ✓ | Algorithm/Method |
| Chart_17 | in `clone()`, check `getItemCount() > 0` before `createCopy` | `clone()` uses `super.clone()` + deep copy of `data` | same place, different change | Checking | Algorithm/Method |
| Math_90 | throw `IllegalArgumentException` if `v` is not `Comparable` | new overload `addValue(Comparable<?>)`, old one delegates | same place, different change | Checking | Interface/O-O Messages |
| Lang_20 | handle a null `toString()` in the capacity expression | capacity `noOfItems * 16`, no `toString()` call | same place, different change | Checking | Assignment/Initialization |
| Time_27 | use `Long.parseLong` for large numbers | add `if (sep.iAfterParser == null && sep.iAfterPrinter == null)` in `toFormatter` | wrong | Algorithm/Method | Checking |

**Pre-fix totals (13):** right fix 8 (label also right: 3; **right fix, wrong label: 5**) · same place,
different change 4 · wrong 1. Labels right: 4.

## Post-fix (the patch was in the first message)

All 13 predicted fixes restate the patch (right). Labels right: 8. **Right fix, wrong label: 5**:

| Bug | Model label | Manual label |
|---|---|---|
| Math_17 | Algorithm/Method | Checking |
| Chart_11 | Algorithm/Method | Assignment/Initialization |
| Time_27 | Algorithm/Method | Checking |
| Lang_20 | Algorithm/Method | Assignment/Initialization |
| Math_90 | Checking | Interface/O-O Messages |

## Findings

1. **Finding the fix is not the main weakness.** Without the patch the model found the right fix for 8 of
   13 bugs; with the patch in hand it still labelled 5 of 13 differently from the manual labels.
2. **The label misses lean one way.** Of the 10 right-fix-wrong-label cases (pre + post), 9 are labelled
   **Algorithm/Method**. The manual labels are Checking (an added condition — IBM: *"Errors caused by
   missing or incorrect validation of parameters or data in conditional statements … If the missing or
   incorrect check is the critical error, checking would still be the type chosen"*) or
   Assignment/Initialization (a wrong variable or value).
3. **Wording sensitivity.** Chart_9 pre-fix found the same fix under prompt v3 and v3.1 but was labelled
   Checking under v3 and Algorithm/Method under v3.1 (`docs/study_execution_log.md`, 2026-10-07). The
   naming step, not the investigation, is where labels move.

## Caveats

- 13 bugs, picked to show failure modes; one rater for the manual labels; one reader (Claude) for the fix
  judgments. A signal, not a measurement.
- The manual labels carry the rater's own confidence (`ground_truth_confidence` in `shortlist.csv`): High
  for most, Medium-High for Math_90, Math_17 and Chart_7, **Medium for Time_27 and Lang_20**, and "High (see
  caveat)" for Time_3. Of the 10 right-fix-wrong-label cases, 2 are on Medium labels (Time_27 post, Lang_20
  post) and 4 on Medium-High labels (Math_17 pre and post, Chart_7 pre, Math_90 post).
- Some disagreements are arguable: "wrong variable used" (Chart_11 `p1`→`p2`, Chart_7 `min`→`max`) can be
  read as Assignment or Algorithm. The added-condition cases (Chart_9, Time_3, Math_17) fit IBM's Checking
  text most directly.
- Post-fix "right fix" is expected (the patch is given); its value here is isolating the labelling step.

## For the full run

This can become a measured analysis: compare each pre-fix `predicted_fix` with the real patch (automatic
location match — same class and changed lines — plus a manual check of a sample), and report
fix-correct vs label-correct as two separate numbers.
