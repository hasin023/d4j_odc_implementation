# Manual analysis shortlist: 13 bugs from `analysis_v2`

**Scope:** Chart, Lang, Math, Mockito and Time (257 bugs). Closure is excluded.
**Model:** gemini-3.1-flash-lite-preview.
**Conditions compared:** `scientific-open` (the enforced hypothesis → prediction → probe → observation loop) and `few-open` (single call). Each condition was run in both **prefix** (buggy code plus failing tests) and **postfix** (the same evidence plus the developer's fix diff) modes.

## Files

| File | What it is |
|---|---|
| `shortlist.csv` | One row per bug: scenario, all 4 labels and confidences, loop statistics, manual ground truth, a per-condition verdict, why it was chosen, the presentation talking point, and paths to the report and artifacts. |
| `bugs/NN_Sx_<Bug>.md` | The full manual analysis for one bug: the fix, the ground-truth rationale, a step-by-step reading of every scientific turn, and a reviewer checklist. Appendix B holds the verbatim model outputs (hypotheses, predictions, probes, what each probe returned, and the reasoning plus rejected alternatives), extracted directly from the artifacts. |

## How the ground truth was decided

Defects4J provides no ODC labels. Each bug's "ground truth" here is **one careful reading** of the developer's fix diff, the failing tests and the bug report, judged against the **pipeline's own ODC definitions** (`d4j_odc_pipeline/odc.py`). ODC types describe the **nature of the fix**, so the diff decides, not where the exception was thrown. Every bug carries a confidence (High / Medium-High / Medium) and, where relevant, the strongest counter-argument. **These are proposals for the human reviewers to confirm or overrule**, not final labels. Time_27, Lang_20 and Math_17 were deliberately kept debatable so they can be discussed in front of the faculty.

## Shortlist

| # | Bug | Scenario | Sci pre → post | Few pre → post | Ground truth |
|---|---|---|---|---|---|
| 1 | Chart_9 | S1 agree, correct | CHK → CHK ✅✅ | CHK → CHK ✅✅ | Checking |
| 2 | Lang_40 | S1 agree, correct | ALG → ALG ✅✅ | ALG → ALG ✅✅ | Algorithm/Method |
| 3 | Chart_17 | S2 agree, wrong | CHK → CHK ❌❌ | CHK → ALG ❌✅ | Algorithm/Method |
| 4 | Math_90 | S2 agree, wrong | CHK → CHK ❌❌ | CHK → INT ❌✅ | Interface/O-O Messages |
| 5 | Math_23 | S3 drift, prefix right | ALG → ASN ✅❌ | ALG → ALG ✅✅ | Algorithm/Method |
| 6 | Math_17 | S3 drift, prefix right | CHK → ALG ✅❌ | FCO → ALG ❌❌ | Checking |
| 7 | Time_3 | S4 drift, postfix right | ALG → CHK ❌✅ | ALG → CHK ❌✅ | Checking |
| 8 | Chart_11 | S4 drift, postfix right | ALG → ASN ❌✅ | ALG → ASN ❌✅ | Assignment/Initialization |
| 9 | Time_27 | S5 drift, neither | ALG → REL ❌❌ | ALG → CHK ❌✅ | Checking |
| 10 | Lang_20 | S5 drift, neither | CHK → ALG ❌❌ | CHK → ALG ❌❌ | Assignment/Initialization |
| 11 | Math_104 | S6 few beats sci | ALG → ASN ❌✅ | ASN → ASN ✅✅ | Assignment/Initialization |
| 12 | Mockito_26 | S6 sci beats few | ASN → ASN ✅✅ | ALG → ASN ❌✅ | Assignment/Initialization |
| 13 | Chart_7 | S6 crossed drift | ASN → ALG ✅❌ | ALG → ASN ❌✅ | Assignment/Initialization |

Abbreviations: CHK = Checking, ALG = Algorithm/Method, ASN = Assignment/Initialization, INT = Interface/O-O Messages, REL = Relationship, FCO = Function/Class/Object.

The S6 bugs also belong to one of S1–S5 under the scientific condition (Math_104 → S4, Mockito_26 → S1, Chart_7 → S3). They were chosen to contrast the two strategies.

## How the candidates were found

1. All 5 workbooks were merged (257 rows). The `Defect Types` tab equals the `Scientific` columns of `Ablation Study` in every row, so the main prefix/postfix analysis uses **scientific-open**. All 4 labels per bug were cross-checked against the `classification.*.json` artifacts: **0 mismatches**.
2. Scientific prefix = postfix for **189** bugs; **68** drift.
3. The fix diff of every drifting bug was screened, plus all 140 agreeing bugs with short diffs. Candidates were rendered with full evidence: diff, failing tests, bug report, all 4 classifications, and every turn with its probe result.
4. Scenarios were confirmed by reading the turns. Picks favour bugs that are easy to explain on a slide, cover several ODC types and projects, and each show a distinct pipeline behaviour.

## Cross-cutting findings (useful for the presentation)

These came out of reading the turns and are backed by counts over all 257 bugs.

1. **The snippet probe matches by substring.** `snippet(org.apache.commons.math3.dfp.Dfp)` returns `DfpTest`, and `snippet(Gamma)` returns `GammaTest`. The model then reasons as if it had seen production code (Math_17, Math_104, Time_3, Math_23). See `execute_probe` in `d4j_odc_pipeline/agent.py`: `argument in s.class_name`.
2. **The buggy class is often not in the evidence store at all.** The class that Defects4J marks as modified appears among `context.json` snippets for only **105 / 257** bugs, and a prefix probe actually retrieved it for **55 / 257**. Collection captures stack-frame classes and "most-executed" classes, and for assertion failures the buggy method is often neither (Chart_11, Chart_7, Mockito_26).
3. **The loop often isn't used.** **31** prefix and **82** postfix scientific runs concluded at turn 1 with **zero probes**. Two of the agree-but-wrong bugs (Chart_17, Math_90) never ran an experiment, even though one probe of the failing test would have falsified the hypothesis in Math_90.
4. **Confidence does not respond to failed experiments.** Chart_11 made 4 probes, none reaching the code, and still concluded with confidence 1.0.
5. **Right mechanism, wrong label.** In Time_3 and Math_104 the prefix run *predicted the exact fix* but labeled by the context (DST side effects, convergence algorithm) instead of the kind of change.
6. **Right label, wrong reason.** Chart_7 (scientific prefix) and Math_17 (prefix) have correct types with invented or inaccurate mechanisms. A label-only accuracy metric cannot see this, which is the strongest argument for this manual analysis. Suggested rubric: grade *type correct?* and *mechanism correct?* separately.
7. **The oracle can hurt as well as help.** In Math_23 and Math_17, postfix runs moved away from the definition-consistent label because the diff's surface form (a new variable; an added branch) suggested another type. In Chart_17 and Math_90 the diff was in the prompt and scientific ignored it, while few-shot used it.
8. **Bug-report anchoring.** When the report proposes a fix (Math_90: "could be fixed by checking that the object is Comparable"), that proposal tends to become the label.
9. **The least stable boundaries** are Checking ↔ Algorithm/Method (17 + 15 drifts) and Algorithm/Method ↔ Assignment/Initialization (9 + 2), matching the `Type Drift` tabs. Chart_7, Lang_20 and Math_23 show why.

## Suggested reading order for the manual session

Chart_9 (how the loop should work) → Chart_11 (the loop starved of evidence) → Time_3 (right mechanism, wrong label) → Chart_17 / Math_90 (confident, consistent, wrong) → Math_23 (the oracle hurts) → Chart_7 (right for the wrong reason) → Math_104 / Mockito_26 (strategy contrast) → Time_27 / Lang_20 / Math_17 (debatable ground truth).
