# RESEARCH_AGENTS.md

This file is the full research-and-implementation context map for LLMs working
on this repository. It combines the theoretical research framing, JSS paper
strategy, ODC background, research questions, evaluation defence, current
pipeline architecture, artifact contracts, known drift, and planned future work.

Use this file when a future LLM needs to understand not only what the code
currently does, but also why the system exists, what the research is trying to
prove, what the manuscript must defend, and which implementation pieces are
current versus planned.

Important scope rule:

- This file is a research compass and agent briefing.
- The executable implementation remains the authority for behavior.
- When this file conflicts with code, inspect `d4j_odc_pipeline/*.py` first.
- When this file conflicts with older generated artifacts, trust the current
  dataclasses and writers.

## 1. Source Documents Synthesized

The research layer was synthesized from:

- `docs/RQs_JSS.md`
- `docs/RQ2_ODC_Coverage_Analysis.md`
- `docs/details_of_RQ2.md`
- `docs/odc_doc.md`
- `docs/METHODOLOGY.md`
- `docs/eval_defence.md`
- `docs/Research Paper Roadmap_ Defect Classification.md`
- `docs/END_TO_END_RQs.md`

The implementation layer was synthesized from:

- `AGENTS.md`
- `README.md`
- `docs/USAGE.md`
- `docs/ARCHITECTURE.md`
- `pyproject.toml`
- `requirements.txt`
- Current source files under `d4j_odc_pipeline/`

The planned/future-work layer was synthesized from:

- `docs/future_works/logging_strategy_and_implementation_plan.md`
- `docs/future_works/mf_actual_integration_plan.md`
- `docs/future_works/parallel_run_implementation_plan.md`
- `docs/future_works/to_improve_the_system.md`
- `docs/future_works/RCEGen_ODC_Integration_Plan.md`

## 2. Status Legend

Use these status labels when interpreting this document:

- [current]: implemented in the current codebase.
- [partial]: implemented in a limited or heuristic form.
- [planned]: described in research/future docs but not fully implemented.
- [drift]: a known documentation or schema mismatch that future agents must not
  blindly trust.

## 3. Executive Thesis

This project studies whether Large Language Models can perform meaningful,
root-cause-oriented software defect classification over real Defects4J Java
bugs using IBM Orthogonal Defect Classification (ODC), especially the seven
standard ODC Defect Type values for `Target=Design/Code`.

The central claim is not merely that an LLM can attach labels to bug reports.
The stronger claim is that a pipeline combining:

- Defects4J execution evidence,
- failing tests,
- stack traces,
- suspicious production frames,
- source snippets,
- optional coverage,
- optional post-fix diffs,
- ODC taxonomy grounding, and
- a scientific-debugging-style reasoning protocol

can produce defensible, reproducible, machine-readable classifications of Java
bugs into ODC defect types.

The intended venue is the Journal of Systems and Software (JSS). The paper must
therefore be framed as an empirical software engineering study, not as a demo.
The manuscript must defend the theoretical validity of ODC, the methodological
validity of pre-fix versus post-fix comparison, the value added by scientific
debugging prompts, and the limits introduced by Defects4J, LLMs, and taxonomy
ambiguity.

## 4. One-Paragraph Paper Framing

This research bridges the semantic gap between symptom-level bug evidence and
cause-level defect classification by combining Defects4J evidence collection,
ODC v5.2 defect semantics, and LLM-based scientific debugging. Pre-fix mode
classifies from the evidence realistically available before a fix; post-fix
mode additionally exposes the actual buggy-to-fixed diff as oracle evidence.
Rather than treating pre/post disagreement as simple failure, the study measures
agreement through strict match, top-2 overlap, family match, Cohen's kappa,
semantic distance, evidence asymmetry, and per-project reliability. The result
is both an automated ODC classification pipeline and an empirical study of how
stable, exhaustive, and useful the ODC taxonomy is for curated open-source Java
defects.

## 5. Core Research Assumptions

These assumptions explain why the system is designed the way it is.

1. ODC Defect Type is a root-cause-oriented semantic attribute.
   It should describe the actual correction needed in the design/code, not just
   the external symptom.

2. ODC Impact and ODC Defect Type are orthogonal.
   For example, "Performance" is an Impact. The Defect Type behind a
   performance symptom could be `Checking`, `Algorithm/Method`,
   `Timing/Serialization`, or another type.

3. Pre-fix evidence is symptom-oriented.
   Stack traces, failing tests, bug reports, and snippets show how a defect
   appears, but may not reveal exactly what code must change.

4. Post-fix evidence is cause-oriented.
   The actual diff reveals what the developer changed, so it is an
   oracle-assisted perspective.

5. Pre-fix and post-fix classifications are not expected to agree perfectly.
   Disagreement can be caused by evidence asymmetry, ODC boundary ambiguity,
   or co-existing faults in Defects4J versions.

6. A seven-type closed ODC taxonomy is the main classification contract.
   The planned RQ2 coverage experiment may add an `Other` escape label as a
   measurement instrument, not as a permanent ODC category.

7. Scientific debugging prompts should improve reasoning discipline.
   The scientific prompt is expected to reduce shallow symptom-labeling and
   force the LLM to justify hypotheses against evidence.

8. Baselines must isolate variables.
   `scientific`, `direct`, and `naive` prompt styles must see the same evidence
   payload when being compared.

## 6. ODC Background

ODC, introduced by Chillarege et al. at IBM, classifies defects through
orthogonal attributes collected when a defect is opened and when it is closed.
For this repository, the most important closer attribute is `Defect Type` for
`Target=Design/Code`.

### 6.1 ODC Opener and Closer Attributes

ODC v5.2 separates attributes into:

Opener attributes, usually available when the defect is found:

- `Activity`: the activity during which the defect was discovered.
- `Trigger`: the condition that exposed the defect.
- `Impact`: the effect the defect would have, or did have, on the customer.

Closer attributes, usually available after the defect is fixed:

- `Target`: the high-level entity fixed.
- `Defect Type`: the semantic kind of correction.
- `Qualifier`: whether the correction addresses missing, incorrect, or
  extraneous implementation.
- `Age`: whether the defect was base, new, rewritten, or refixed.
- `Source`: whether the fixed code was developed in-house, reused, outsourced,
  or ported.

Repository scope:

- [current] `Defect Type` is mandatory.
- [current] `Target` effectively defaults to `Design/Code`.
- [partial] `Qualifier`, `Age`, and `Source` are optional persisted fields.
- [partial] `Activity`, `Triggers`, and `Impact` are inferred/candidate fields,
  not authoritative ODC opener labels.
- [partial] The pipeline operationalizes an additive ODC mapping layer, but it
  does not implement the full IBM opener/closer workflow as a validated schema.

### 6.2 Canonical ODC Defect Types

The current implementation uses exactly these seven canonical labels from
`d4j_odc_pipeline/odc.py`:

| ODC Type | Family | Core Meaning |
| --- | --- | --- |
| `Algorithm/Method` | Control and Data Flow | The local procedure, algorithm, computational strategy, or data-structure logic is wrong. |
| `Assignment/Initialization` | Control and Data Flow | A value or object state is assigned incorrectly, not assigned, reset incorrectly, or initialized incorrectly. |
| `Checking` | Control and Data Flow | A validation, guard, predicate, boundary condition, loop condition, or data check is missing or wrong. |
| `Timing/Serialization` | Control and Data Flow | Correctness depends on ordering, locking, serialization, concurrency, or coordinated access to shared resources. |
| `Function/Class/Object` | Structural | A significant capability, class, object, global structure, or design-level function is missing or incorrectly specified. |
| `Interface/O-O Messages` | Structural | The defect is in communication across boundaries: calls, signatures, parameters, messages, API contracts, or object services. |
| `Relationship` | Structural | Correctness depends on associations among procedures, data structures, classes, objects, inheritance, or cross-entity constraints. |

Important boundary rules:

- Do not classify a crash as `Checking` just because an exception occurred.
  Ask what correction is semantically required.
- Do not classify a bug as `Function/Class/Object` merely because a method or
  class is involved. Use it for design-level capability/object/function gaps.
- Use `Algorithm/Method` for local procedural logic defects that are not simply
  missing/incorrect guards or assignments.
- Use `Interface/O-O Messages` when the bug is primarily a mismatch between
  communicating components, services, parameters, messages, or API contracts.
- Use `Relationship` when the failure is due to inconsistent assumptions or
  constraints across related entities.

### 6.3 Impact Versus Defect Type

This distinction is essential for the paper.

Impact is the symptom or user-visible effect:

- `Reliability`: crash, unplanned interruption, failure.
- `Performance`: slow, hang, degradation.
- `Capability`: intended behavior missing or incorrect.
- `Integrity/Security`: unauthorized alteration/disclosure or corruption.
- `Usability`, `Maintenance`, `Serviceability`, `Migration`, etc.

Defect Type is the semantic correction:

- A reliability failure may be a `Checking` defect if a null guard was missing.
- A performance failure may be `Timing/Serialization` if locking is wrong.
- A capability failure may be `Algorithm/Method` if the method computes the
  wrong result.
- A security impact may still be `Interface/O-O Messages` if the issue is an
  incorrect boundary contract.

One of the paper's methodological contributions is showing that the pipeline
does not collapse symptom labels into root-cause labels.

## 7. Defects4J Research Setting

Defects4J is used because it provides real Java bugs with reproducible buggy
and fixed versions, triggering tests, metadata, and project histories. It is a
standard empirical benchmark for software testing, fault localization, and
automated program repair.

Why Defects4J fits the ODC Design/Code scope:

- It consists of functional Java defects.
- It centers on source-code changes.
- Documentation, build, and configuration issues are generally not the primary
  corpus target.
- Defects are reproducible through tests.

Key caveats:

- Defects4J's single-fault framing is an experimental simplification.
- `defects4j-mf` evidence suggests versions can contain many co-existing
  faults, with an average around 9.2 in supported projects.
- Triggering tests may include developer knowledge written after the bug was
  understood, so "pre-fix" evidence is realistic but not perfectly raw
  pre-triage evidence.
- Folder names in `work/` and `.dist/` are not reliable truth. Trust
  `context.json`, `classification.json`, and Defects4J config/properties.

## 8. Prompting and LLM Methodology

### 8.1 Scientific Debugging Protocol

The main prompt strategy is inspired by Zeller-style scientific debugging:

1. Observe the failure evidence.
2. Form a hypothesis about the root-cause mechanism.
3. Predict what code/evidence should look like if the hypothesis is true.
4. Examine the available evidence against that prediction.
5. Conclude with one ODC defect type and alternatives.

The manuscript positions this as an LLM adaptation of structured debugging,
aligned with research such as AutoSD. The purpose is not to make the LLM run a
real debugger today; the purpose is to force disciplined, evidence-grounded,
traceable reasoning.

### 8.2 Prompt Styles

[current] The implementation supports three prompt styles:

| Prompt Style | ODC Taxonomy | Scientific Protocol | Few-Shot Examples | Purpose |
| --- | --- | --- | --- | --- |
| `scientific` | Yes | Yes | Yes | Main method. Full taxonomy, anti-bias rules, diagnostic protocol, decision tree, and examples. |
| `direct` | Yes | No | No | Zero-shot ODC baseline. Isolates contribution of scientific prompt engineering. |
| `naive` | No | No | No | Taxonomy-free baseline. Measures whether explicit ODC grounding reduces vocabulary scatter and improves actionability. |

Controlled comparison rule:

- All three styles should receive the same evidence payload and snippet budget.
- The difference should be the system prompt, not evidence availability.
- `naive` omits ODC-specific hints and taxonomy names.

### 8.3 Evidence Modes

| Mode | Evidence Available | Research Role |
| --- | --- | --- |
| `pre-fix` | Bug report, `defects4j info`, failing tests, stack traces, suspicious frames, production snippets, test snippets, optional coverage. | Realistic diagnosis before seeing the fix. |
| `post-fix` | All pre-fix evidence plus the actual buggy-to-fixed diff. | Oracle-assisted cause perspective. |

Important:

- `--include-fix-diff` creates post-fix mode.
- Post-fix mode is useful for evaluation, not for realistic deployment.
- The fix diff is explicitly labeled as oracle information in the prompt.
- `classes.modified` is a hidden oracle and should not enter the pre-fix prompt.

## 9. High-Level JSS Research Questions

The current JSS-facing RQs are:

### RQ1: Bug Type Distribution Across Projects

Question:

What is the distribution of ODC defect types across the Defects4J benchmark,
and does this distribution vary significantly across projects?

Core purpose:

- Establish the empirical defect-type landscape of Defects4J.
- Show whether projects have different root-cause profiles.
- Support process-insight claims, not only classifier-accuracy claims.

### RQ2: Bug Type Coverage of the ODC Taxonomy

Question:

Do the seven standard ODC bug types cover all bugs in Defects4J, or do some
bugs genuinely fall outside those seven types?

Core purpose:

- Make the ODC sufficiency claim falsifiable.
- Measure whether Defects4J defects are exhausted by the canonical seven
  Design/Code defect types.
- Use `Other` only as a measurement instrument, not as a permanent taxonomy
  category.

### RQ3: Overall Pipeline Classification Accuracy

Question:

How well does the LLM-based pipeline, using the scientific debugging loop and
ODC taxonomy, classify Defects4J bugs into correct defect types under a
four-level accuracy evaluation?

Core purpose:

- Evaluate the main pipeline against post-fix oracle-assisted classifications.
- Avoid over-reliance on exact match by using partial-agreement tiers.

### RQ4: Contribution of Each Pipeline Component

Question:

How much do the scientific debugging loop and explicit ODC taxonomy grounding
each improve classification accuracy, label consistency, and vocabulary
reduction compared to unstructured LLM baselines?

Core purpose:

- Isolate the contribution of scientific prompting.
- Isolate the contribution of ODC taxonomy grounding.
- Show that the method is more than generic LLM labeling.

### RQ5: Does Seeing the Fix Change How a Bug Gets Classified?

Question:

What is the magnitude and pattern of semantic divergence between pre-fix and
post-fix ODC classifications, and how does per-project classification
reliability vary across Defects4J projects?

Core purpose:

- Treat pre/post disagreement as a measurable semantic gap.
- Identify divergence patterns and project-level reliability variation.
- Defend why divergence is scientifically expected, not automatic failure.

## 10. Internal RQ Mapping Used by Current Code

Some implementation and methodology docs use an older/internal numbering. Map
it to the JSS-facing RQs like this:

| JSS RQ | Internal/Code Analysis Area | Current Code Support |
| --- | --- | --- |
| RQ1: Distribution | RQ1.1 type distribution, RQ1.2 impact-vs-type separation | `analysis.compute_type_distribution`, `analysis.compute_project_type_correlation`, `analysis.analyze_impact_vs_type` |
| RQ2: ODC coverage | Planned open-schema seven-plus-Other coverage study | [planned] Not fully implemented as a dedicated prompt/schema mode. |
| RQ3: Accuracy | Internal RQ2.1 overall efficacy, per-type P/R/F1 | `comparison.py`, `analysis.compute_per_type_metrics` |
| RQ4: Component contribution | Internal RQ2.2 scientific vs direct; RQ2.3 naive taxonomy grounding | `study-baseline`, `study-naive`, `analysis.compare_baseline_vs_scientific`, `analysis.compute_taxonomy_grounding_metrics` |
| RQ5: Fix visibility and divergence | Internal RQ3.1 semantic gap, RQ4.1 per-project kappa | `comparison.semantic_distance`, `comparison.compute_per_project_kappa`, `batch.analyze_batch_artifacts` |

Future agents must not confuse the planned RQ2 coverage experiment with the
currently implemented `naive` taxonomy-grounding experiment. They are related
but not identical.

## 11. RQ1: Distribution Across Projects

Goal:

- Quantify how the seven ODC types are distributed across Defects4J.
- Determine whether the distribution varies by project.
- Separate root-cause type from symptom/impact.

Primary data:

- Prefix/scientific `classification.json` outputs.
- `odc_type`, `family`, `inferred_impact`, `project_id`.

Metrics:

- Corpus-level type counts.
- Corpus-level family counts.
- Per-project type distribution.
- Chi-squared test of project-by-type independence when `scipy` is available.
- Impact-vs-Type comparison to show that symptoms are not simply relabeled as
  defect types.

Expected paper contribution:

- A Defects4J ODC type distribution map.
- Evidence that different projects may have different defect profiles.
- A demonstration that ODC provides deeper semantic categories than labels such
  as "crash", "performance", or "wrong output".

Implementation:

- `analysis.compute_type_distribution(classifications)`
- `analysis.compute_project_type_correlation(classifications)`
- `analysis.analyze_impact_vs_type(classifications)`
- `results_export.export_type_distribution_latex(analysis)`

## 12. RQ2: ODC Taxonomy Coverage

Status:

- [planned] The full seven-plus-Other coverage mode is described in the
  research docs but is not yet a first-class implemented CLI mode.
- [current] The pipeline does implement the seven-type closed taxonomy.
- [current] The pipeline implements a `naive` taxonomy-free baseline, but this
  is for taxonomy-grounding analysis, not the same as the planned `Other`
  coverage experiment.

### 12.1 RQ2 Formal Claim

RQ2 asks:

To what extent do the seven canonical ODC Defect Types constitute an exhaustive
taxonomy for functional code defects in Defects4J?

This is a taxonomic validity question. It asks whether the study can safely use
the closed seven-type schema for the main accuracy, divergence, and component
studies.

### 12.2 Why `Other` Is Methodologically Necessary

A closed seven-type run cannot prove coverage by itself. If the LLM is forced
to choose one of seven types, every bug will be assigned one of seven types by
construction. That would be circular.

The planned RQ2 experiment therefore adds an eighth label, `Other`, as a release
valve. This makes the sufficiency claim falsifiable.

Important nuance:

- `Other` is not a proposed eighth ODC category.
- `Other` is a measurement instrument.
- The official taxonomy remains the seven ODC Design/Code Defect Types.
- A low `Other` rate supports the closed seven-type design used elsewhere.

### 12.3 Planned Open-Schema Output Contract

When RQ2 coverage mode is implemented, use canonical current labels plus
`Other`:

```json
{
  "odc_type": "Algorithm/Method | Assignment/Initialization | Checking | Timing/Serialization | Function/Class/Object | Interface/O-O Messages | Relationship | Other",
  "other_justification": "required only when odc_type is Other",
  "nearest_type": "closest canonical ODC type when odc_type is Other",
  "other_confidence": "low | medium | high"
}
```

The `Other` branch should be hard to choose. The LLM must explain why none of
the seven types apply, name the nearest forced-fit type, and assign confidence.

### 12.4 Planned Two-Pass Design

The RQ2 design requires two runs:

1. Closed seven-type run.
   This is the normal pipeline mode and the baseline used by RQ1/RQ3/RQ4/RQ5.

2. Open eight-type run.
   This repeats the same bugs with seven canonical labels plus `Other`.

Why both are needed:

- The closed run preserves the production-mode classification baseline.
- The open run measures taxonomy coverage.
- Comparing the two measures whether adding `Other` destabilizes ordinary
  seven-type classification.

### 12.5 Planned RQ2 Metrics

| Metric | Meaning |
| --- | --- |
| Coverage Rate | Fraction of bugs assigned to one of the seven ODC types in the open run. |
| Escape Rate | `1 - Coverage Rate`, the fraction assigned `Other`. |
| Per-project Escape Rate | Escape rate computed separately for each Defects4J project. |
| False Escape Rate | Fraction of `Other` labels that manual inspection judges to be LLM errors rather than true taxonomy gaps. |
| Taxonomy Shift Rate | Chance-corrected agreement between closed and open runs, using Cohen's kappa. |
| Type Distribution Stability | Population-level distribution shift, planned with KL-divergence or a similar distribution metric. |

Expected interpretation:

- Escape Rate < 5%: strong evidence that the seven ODC types cover Defects4J.
- Escape Rate 5-15%: moderate gap or model uncertainty; requires careful manual
  inspection.
- Escape Rate > 15%: significant finding that may imply taxonomy limitations
  for open-source Java bugs.

### 12.6 Literature Argument for Coverage

The coverage hypothesis is defensible because:

- Chillarege et al. derived ODC from industrial defect streams and treated the
  types as empirically saturated for Design/Code defect analysis.
- IBM ODC v5.2 specifies the seven Design/Code defect types and the related
  closer attributes.
- ODC has been applied across multiple domains, including industrial systems,
  NoSQL databases, infrastructure-as-code, open-source projects, and ML-based
  defect classification datasets.
- Defects4J itself is curated around functional Java source-code bugs, which
  aligns with the ODC Design/Code target.

Honest limitations:

- ODC extensions exist for AI/ML-specific, cloud, space/satellite, and
  internationalization/NLS contexts.
- Those domains are outside the core Defects4J functional Java scope.
- The paper should frame RQ2 as an empirical test, not as an assumption.

## 13. RQ3: Overall Pipeline Accuracy

RQ3 evaluates how well the full scientific pipeline classifies bugs into ODC
Defect Types.

The evaluation should not rely only on exact agreement because:

- ODC has known boundary ambiguity.
- Human inter-rater agreement is not perfect.
- Pre-fix and post-fix modes see different evidence.
- Alternative ODC types may be defensible even when primary labels differ.

### 13.1 Four-Tier Accuracy Framework

| Tier | Metric | Meaning |
| --- | --- | --- |
| Tier 1 | Strict Match | Prefix and postfix primary `odc_type` are identical. |
| Tier 2 | Top-2 Match | One side's primary type appears in the other side's `alternative_types`. |
| Tier 3 | Family Match | Both types fall in the same family: `Control and Data Flow` or `Structural`. |
| Tier 4 | Cohen's Kappa | Chance-corrected agreement over all pairs. |

Additional current metrics:

- Per-type precision, recall, and F1 using post-fix as oracle-assisted
  reference.
- 7-by-7 type confusion/transition matrix.
- Semantic distance.
- Divergence pattern counts.
- Attribute concordance for optional ODC fields.

### 13.2 Expected Accuracy Interpretation

The evaluation defence uses these rough thresholds as defensible targets:

- Strict match around 40-60% can be meaningful given ODC ambiguity.
- Top-2 match around 60-80% indicates the model found the right type
  neighborhood.
- Family match around 70-90% indicates useful high-level root-cause grouping.
- Cohen's kappa around 0.50-0.80 indicates moderate to substantial agreement.

These are not hard acceptance criteria, but they are literature-informed
expectations for discussing results.

Implementation:

- `comparison.compare_classifications(prefix, postfix)`
- `comparison.batch_compare(pairs)`
- `comparison.compute_cohens_kappa(pairs)`
- `analysis.compute_per_type_metrics(pairs)`
- `results_export.export_accuracy_table_latex(analysis)`
- `results_export.export_confusion_matrix_latex(analysis)`

## 14. RQ4: Component Contribution

RQ4 asks whether the pipeline's design choices actually matter.

The two major components to isolate are:

1. Scientific debugging protocol.
2. Explicit ODC taxonomy grounding.

### 14.1 Scientific Protocol Efficacy

Compare:

- `scientific`: taxonomy + scientific protocol + few-shot examples.
- `direct`: taxonomy + JSON contract + anti-bias rules, but no protocol, no
  diagnostic tree, and no few-shots.

Controlled condition:

- Same bugs.
- Same evidence payload.
- Same model/provider configuration.
- Same snippet budget.

Metrics:

- Strict/top-2/family match deltas against post-fix.
- Confidence differences.
- Evidence-gap patterns.
- Error categories where scientific protocol helps or fails.

Implementation:

- `study-baseline`
- `batch.run_baseline_from_manifest`
- `analysis.compare_baseline_vs_scientific`
- `results_export.export_baseline_comparison_latex`

### 14.2 Taxonomy Grounding Effect

Compare:

- `naive`: no ODC taxonomy, no ODC labels, free-form defect labels.
- `direct`: ODC taxonomy but no scientific protocol.
- `scientific`: ODC taxonomy plus full scientific protocol.

Metrics:

- Vocabulary size.
- Label entropy.
- Number of canonical ODC types recovered after heuristic mapping.
- Vocabulary reduction from naive to taxonomy-grounded conditions.
- Whether taxonomy grounding produces more consistent and actionable labels.

Implementation:

- `study-naive`
- `prompt_style="naive"`
- `analysis.map_naive_to_odc`
- `analysis.analyze_naive_labels`
- `analysis.compute_taxonomy_grounding_metrics`
- `results_export.export_taxonomy_grounding_latex`

## 15. RQ5: Fix Visibility, Semantic Divergence, and Project Reliability

RQ5 asks what changes when the model sees the real fix.

This is not just an accuracy question. It measures the semantic gap between:

- symptom-based classification before the fix, and
- cause-based classification after the fix.

### 15.1 Three-Pillar Defence for Pre/Post Divergence

Pillar 1: Evidence asymmetry.

- Pre-fix mode sees symptoms.
- Post-fix mode sees the correction.
- A null pointer symptom may suggest `Checking`, while the real fix may reveal
  `Algorithm/Method`.

Pillar 2: ODC boundary ambiguity.

- `Algorithm/Method` versus `Checking`
- `Algorithm/Method` versus `Assignment/Initialization`
- `Function/Class/Object` versus `Interface/O-O Messages`
- `Interface/O-O Messages` versus `Relationship`
- `Function/Class/Object` versus `Relationship`

Pillar 3: Multi-fault reality.

- Defects4J versions may contain many co-existing faults.
- Pre-fix symptoms can be contaminated by other latent faults.
- Post-fix diff isolates one official fault.

Therefore, pre/post disagreement can be scientifically meaningful rather than
simply wrong.

### 15.2 Semantic Gap Metrics

Implemented layers:

- Layer A: semantic distance, a 0.0-1.0 proximity score grounded in type/family
  boundaries.
- Layer B: evidence asymmetry explanation.
- Layer C: attribute concordance on `target`, `qualifier`, `age`, and `source`.
- Layer D: divergence pattern category:
  - `exact-match`
  - `soft-divergence`
  - `moderate-divergence`
  - `hard-divergence`
- Layer E: human-readable comparison insights.

Implementation:

- `comparison.semantic_distance`
- `comparison.classify_divergence_pattern`
- `comparison.analyze_evidence_asymmetry`
- `comparison.compute_attribute_concordance`
- `comparison.generate_comparison_insights`
- `comparison.compute_per_project_kappa`
- `analysis.compute_semantic_gap_metrics`
- `results_export.export_per_project_kappa_latex`

## 16. Threats to Validity

Internal validity:

- LLM nondeterminism may change outputs between runs.
- API/provider behavior can change over time.
- Invalid JSON or invalid labels are not always retried.
- Coverage is best-effort and may be empty.
- Bug report fetching may vary with network/API availability.

Construct validity:

- ODC classification is semantically subjective.
- Post-fix is an oracle-assisted reference, not perfect human ground truth.
- Pre-fix evidence may include developer-written tests that encode knowledge of
  the bug.
- The `inferred_activity`, `inferred_triggers`, and `inferred_impact` fields
  are heuristic and not authoritative ODC opener annotations.

External validity:

- Defects4J is Java-focused.
- Results may not generalize to AI/ML systems, cloud infrastructure,
  internationalization defects, embedded safety-critical software, or
  non-source-code defects.
- Defects4J projects differ in style, test quality, and age.

Conclusion validity:

- Strict match alone underestimates useful performance.
- Family match alone may overstate detailed correctness.
- Cohen's kappa requires enough samples and label variation to be meaningful.
- Manual inspection is required for any planned `Other` claims in RQ2.

## 17. Current Pipeline Overview

[current] The repository implements a synchronous, file-oriented research
pipeline. There is no database, queue, service layer, or async orchestrator.

Primary package:

- `d4j_odc_pipeline/`

Primary generated roots:

- `.dist/runs/` for standalone command outputs.
- `.dist/study/` for batch study outputs.
- `work/` for standalone Defects4J checkouts.
- `.dist/study/work/` for batch Defects4J checkouts.

### 17.1 Primary CLI Modes

[current] Script-mode commands:

- `collect`
- `classify`
- `run`
- `compare`
- `compare-batch`
- `study-plan`
- `study-run`
- `study-analyze`
- `study-baseline`
- `study-naive`
- `study-export`
- `multifault`
- `multifault-enrich`
- `d4j pids`
- `d4j bids`
- `d4j info`

[current] Interactive REPL:

- Launch with `d4j-odc` or `python -m d4j_odc_pipeline` with no arguments.
- Provides slash commands such as `/run`, `/collect`, `/classify`,
  `/study plan`, `/study run`, `/study analyze`, `/study baseline`,
  `/study naive`, `/study export`, `/multifault`, `/enrich`, `/doctor`,
  `/show classification`, and `/status`.
- Session state is stored in `.dist/.odc_session.json`.

## 18. Evidence Collection Flow

Primary function:

- `pipeline.collect_bug_context(...)`

Sequence:

1. Query bug metadata with `Defects4JClient.query_bug_metadata()`.
2. Fetch bug text via `defects4j info`.
3. Fetch bug report content from `report.url` through `web_fetch.fetch_bug_report()`.
4. Checkout buggy version `<bug_id>b`.
5. Compile the buggy version.
6. Run tests.
7. Parse failures from `failing_tests` and raw output.
8. Export Defects4J properties.
9. Select suspicious stack frames from parsed failures.
10. Discover Java source roots.
11. Extract production snippets around suspicious frames.
12. Extract failing test source snippets to show expected behavior.
13. Optionally run coverage and parse Cobertura XML.
14. Optionally collect the buggy-to-fixed diff as post-fix oracle evidence.
15. Serialize `BugContext` to `context.json`.

Important behavior:

- `classes.modified` is stored in `hidden_oracles` and excluded from the prompt.
- Suspicious production frames are preferred over test frames.
- Framework/JDK/build/test-runner frames are filtered aggressively.
- Test source extraction is capped to the first three failures.
- Coverage is targeted to suspicious classes first.
- If coverage fails with instrumentation, it retries without the instrumentation
  filter.
- If filtered coverage parsing is empty, parsing retries unfiltered.
- `fix_diff` is collected only when `--include-fix-diff` is set.

## 19. Classification Flow

Primary function:

- `pipeline.classify_bug_context(...)`

Sequence:

1. Load `context.json`.
2. Build prompt messages with `prompting.build_messages()`.
3. Optionally save rendered prompt JSON.
4. Call the configured LLM provider.
5. Extract a JSON object from raw response.
6. For `scientific` and `direct`, validate `odc_type`.
7. Canonicalize `family` from `odc.family_for(odc_type)`.
8. Normalize optional ODC mapping fields.
9. Write `classification.json`.
10. Optionally write `report.md`.

Important behavior:

- `build_messages()` returns exactly two messages: `system` and `user`.
- `scientific` includes taxonomy, JSON contract, anti-bias rules, protocol,
  diagnostic tree, and few-shot examples.
- `direct` includes taxonomy, JSON contract, and anti-bias rules only.
- `naive` includes no ODC taxonomy and writes free-form classification fields.
- `family` is always overwritten from the canonical mapping.
- `target` defaults to `Design/Code` when omitted.
- `dry_run=True` builds prompt messages and skips the LLM call.

Known drift:

- Some docs mention retrying invalid classifications. Current source only
  retries transient HTTP/network errors; invalid ODC labels raise `LLMError`.

## 20. Comparison and Analysis Flow

Primary functions/modules:

- `comparison.compare_classifications(...)`
- `comparison.batch_compare(...)`
- `batch.analyze_batch_artifacts(...)`
- `analysis.py`
- `results_export.py`

Comparison evaluates:

- Strict type match.
- Top-2 alternative overlap.
- Family match.
- Cohen's kappa.
- Semantic distance.
- Evidence asymmetry.
- Attribute concordance.
- Divergence pattern.
- Per-project kappa.
- Type confusion matrix.

Analysis evaluates:

- Type/family distribution.
- Project-type correlation.
- Impact-vs-Type separation.
- Per-type precision/recall/F1.
- Scientific-vs-direct baseline comparison.
- Naive label analysis and taxonomy grounding.
- Semantic gap metrics.

Export writes:

- LaTeX tables using `booktabs` style.
- CSV files for R/SPSS or supplementary analysis.

## 21. Module Map

Use this map when changing implementation.

| Module | Role |
| --- | --- |
| `d4j_odc_pipeline/__main__.py` | Package entrypoint. |
| `d4j_odc_pipeline/__init__.py` | Version export (`0.2.0`). |
| `d4j_odc_pipeline/cli.py` | Argparse CLI and command dispatch. Launches REPL when no args are given. |
| `d4j_odc_pipeline/interactive/` | REPL shell, slash commands, completion, session state, rendering. |
| `d4j_odc_pipeline/pipeline.py` | Main orchestration for collection, classification, validation, and report writing. |
| `d4j_odc_pipeline/defects4j.py` | Defects4J wrapper, query/export helpers, coverage parsing, WSL path handling. |
| `d4j_odc_pipeline/llm.py` | Provider abstraction for Gemini, OpenRouter, Groq, and generic OpenAI-compatible APIs. |
| `d4j_odc_pipeline/prompting.py` | Prompt construction, evidence payload shaping, ODC mapping hints. |
| `d4j_odc_pipeline/odc.py` | Canonical seven-type ODC taxonomy and family mapping. |
| `d4j_odc_pipeline/models.py` | Dataclasses for persisted artifacts. |
| `d4j_odc_pipeline/parsing.py` | Failing test parsing, stack frame parsing, JSON extraction. |
| `d4j_odc_pipeline/comparison.py` | Pre/post comparison and extended semantic divergence layers. |
| `d4j_odc_pipeline/analysis.py` | Cross-study statistical analysis aligned to RQs. |
| `d4j_odc_pipeline/results_export.py` | LaTeX and CSV export. |
| `d4j_odc_pipeline/batch.py` | Study manifests, batch execution, checkpoints, baselines, analysis. |
| `d4j_odc_pipeline/multifault.py` | Pure-Python defects4j-mf data loader/enricher. |
| `d4j_odc_pipeline/web_fetch.py` | Bug report retrieval from GitHub, JIRA, or generic pages. |
| `d4j_odc_pipeline/console.py` | Rich console helpers. |

## 22. Artifact Contracts

### 22.1 `context.json`

Serialized from `BugContext`.

Important fields:

- `project_id`
- `bug_id`
- `version_id`
- `work_dir`
- `created_at`
- `defects4j_command`
- `metadata`
- `exports`
- `failures`
- `suspicious_frames`
- `code_snippets`
- `coverage`
- `hidden_oracles`
- `notes`
- `bug_info`
- `bug_report_content`
- `fix_diff`

Notes:

- `code_snippets` contains production and test snippets together.
- `prompting.py` splits snippets into production/test payloads by reason.
- `fix_diff` is a string and is usually `""` when absent.

### 22.2 `classification.json`

Serialized from `ClassificationResult`.

Important fields:

- `project_id`
- `bug_id`
- `version_id`
- `prompt_style`
- `model`
- `provider`
- `created_at`
- `odc_type`
- `family`
- `confidence`
- `needs_human_review`
- `observation_summary`
- `hypothesis`
- `prediction`
- `experiment_rationale`
- `reasoning_summary`
- `evidence_used`
- `evidence_gaps`
- `alternative_types`
- `target`
- `qualifier`
- `age`
- `source`
- `inferred_activity`
- `inferred_triggers`
- `inferred_impact`
- `evidence_mode`
- `raw_response`

For `naive` prompt style:

- `odc_type` may store the free-form `defect_type`.
- `family` is `None`.
- ODC validation is intentionally not applied.

### 22.3 Comparison Outputs

Single comparison includes:

- prefix/postfix ODC type and family.
- strict/top2/family match booleans.
- match detail.
- optional closer fields from both sides.
- evidence modes.
- semantic distance and divergence pattern.
- evidence asymmetry and insights.

Batch comparison includes:

- counts and rates.
- global Cohen's kappa.
- per-project kappa.
- per-bug results.
- type confusion matrix.
- average semantic distance.
- divergence pattern counts.
- average attribute concordance.

## 23. Output Layout

Standalone commands:

```text
.dist/runs/
  Lang_1_prefix/
    context.json
    classification.json
    report.md
  Lang_1_postfix/
    context.json
    classification.json
    report.md
```

Batch study:

```text
.dist/study/
  manifest_<N>.json
  summary.json
  analysis_<N>.json
  analysis_<N>.md
  artifacts_<N>/
    prefix/
      <Project>_<Bug>_prefix/
        context.json
        classification.json
        report.md
    postfix/
      <Project>_<Bug>_postfix/
        context.json
        classification.json
        report.md
    checkpoint.json
  baseline_<N>/
    <Project>_<Bug>_prefix/
      classification.json
      report.md
    checkpoint.json
  naive_<N>/
    <Project>_<Bug>_prefix/
      classification.json
      report.md
    checkpoint.json
  latex/
  csv/
  work/
```

## 24. End-to-End Study Workflow

The normal full study flow is:

1. Generate balanced manifest.
2. Run scientific prefix/postfix classifications.
3. Run direct baseline classifications.
4. Run naive taxonomy-free classifications.
5. Analyze batch artifacts.
6. Export manuscript tables and CSV files.

Script-mode example:

```powershell
python -m d4j_odc_pipeline study-plan --target-bugs 100 --seed 42
python -m d4j_odc_pipeline study-run --manifest manifest_100.json --skip-coverage
python -m d4j_odc_pipeline study-baseline --manifest manifest_100.json --scientific-artifacts-root .\.dist\study\artifacts_100
python -m d4j_odc_pipeline study-naive --manifest manifest_100.json --scientific-artifacts-root .\.dist\study\artifacts_100
python -m d4j_odc_pipeline study-analyze --manifest manifest_100.json --require-all-projects
python -m d4j_odc_pipeline study-export --analysis .\.dist\study\analysis_100.json
```

Interactive equivalent:

```text
odc> /study plan --target-bugs 100 --seed 42
odc> /study run --manifest manifest_100.json
odc> /study baseline --manifest manifest_100.json --scientific-artifacts-root .dist/study/artifacts_100
odc> /study naive --manifest manifest_100.json --scientific-artifacts-root .dist/study/artifacts_100
odc> /study analyze --manifest manifest_100.json --require-all-projects
odc> /study export --analysis .dist/study/analysis_100.json
```

RQ2 coverage-mode workflow is planned separately:

1. Run closed seven-type classifications.
2. Run open seven-plus-Other classifications on the same bugs and evidence.
3. Measure coverage, escape rate, false escapes, taxonomy shift, and
   distribution stability.
4. Manually inspect every `Other` case.

## 25. Environment and Providers

Runtime:

- Python `>=3.11`
- `rich`
- `requests`
- `prompt_toolkit`
- `scipy` optional for chi-squared testing

Package:

- Project name: `d4j-odc-pipeline`
- Console script: `d4j-odc`
- Current version: `0.2.0`

Important environment variables:

- `DEFAULT_LLM_PROVIDER`
- `DEFAULT_LLM_MODEL`
- `GEMINI_API_KEY`
- `GEMINI_BASE_URL`
- `OPENROUTER_API_KEY`
- `OPENROUTER_BASE_URL`
- `OPENROUTER_HTTP_REFERER`
- `OPENROUTER_APP_TITLE`
- `GROQ_API_KEY`
- `GROQ_BASE_URL`
- `GROQ_MODEL`
- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `DEFECTS4J_CMD`
- `DEFECTS4J_PATH_STYLE`
- `MULTIFAULT_DATA_DIR`

Provider support:

- [current] `gemini`
- [current] `openrouter`
- [current] `groq`
- [current] `openai-compatible`

Defects4J path style:

- `wsl`: convert relevant Windows paths to `/mnt/<drive>/...`.
- `native`: leave paths unchanged.

## 26. Known Drift and Caveats

Future agents should watch these carefully:

1. Some docs say invalid classifications are retried. Current code retries
   transient HTTP/network failures only; invalid ODC labels raise an error.
2. Older docs may omit `groq`, but current code includes it as a provider.
3. Older artifacts may use `coarse_group` instead of `family`.
4. Older artifacts may omit `evidence_mode`, `fix_diff`, or optional
   opener/closer fields.
5. Only `odc_type` is strictly validated for ODC modes.
6. Optional fields are normalized lightly, not validated against the full IBM
   ODC schema.
7. `source_hint` is currently always `null`.
8. `tests/test_url_fetch.py` is a live network integration script, not a normal
   unit test.
9. Full `pytest` may trigger `tests/test_url_fetch.py`; use a targeted unit
   test list unless live network testing is intended.
10. `compare-batch` relies on matching directory names after stripping
    `_prefix` and `_postfix`.
11. Existing generated outputs in `artifacts/` and `.dist/` may span multiple
    schema generations.
12. RQ2 seven-plus-Other coverage mode is not yet fully implemented even though
    the methodology is documented.

## 27. Safe Extension Rules

If changing evidence schema:

1. Update `models.py`.
2. Update collection/writing in `pipeline.py`.
3. Update prompt payload shaping in `prompting.py`.
4. Update tests.
5. Update docs and this file.

If changing ODC label names or boundaries:

1. Update `odc.py`.
2. Update taxonomy prompt text and examples in `prompting.py`.
3. Update validation in `pipeline.py`.
4. Update comparison/report wording.
5. Preserve old-artifact compatibility where possible.

If changing opener/closer metadata:

1. Update `_build_odc_mapping_hints()` in `prompting.py`.
2. Update JSON schema in `llm.py`.
3. Update `ClassificationResult` in `models.py`.
4. Update extraction/normalization in `pipeline.py`.
5. Update `comparison.py` if the fields affect comparison.
6. Update tests and docs.

If changing batch study behavior:

1. Update `batch.py`.
2. Preserve checkpoint compatibility or explicitly migrate it.
3. Update CLI and REPL handlers.
4. Update `docs/USAGE.md`, `docs/END_TO_END_RQs.md`, and this file.

## 28. Future Implementation Roadmap

These are planned directions from `docs/future_works/`.

### 28.1 RQ2 Open-Schema Coverage Mode

Need to implement:

- A dedicated prompt style or flag for seven-plus-Other classification.
- Output fields `other_justification`, `nearest_type`, and `other_confidence`.
- Validation rules that require those fields only for `Other`.
- Analysis functions for coverage rate, escape rate, false escape rate,
  taxonomy shift, and distribution stability.
- Export tables for RQ2 coverage.
- Manual-inspection workflow for `Other` cases.

### 28.2 Structured Logging and Provenance

Planned logging system:

- JSONL event logs per bug and per batch.
- Run envelope events for start/end/failure.
- Collection-phase events for checkout, compile, test, exports, coverage.
- Classification-phase events for prompt build, LLM request, parsing,
  validation, output.
- Artifact events for created files.
- Batch events for checkpoint/resume.
- Content capture modes to avoid logging secrets or huge payloads by default.

Research value:

- Reproducibility.
- Operational debugging.
- Failure-rate analysis.
- Latency and cost analysis.
- Prompt/schema-change provenance.

### 28.3 Multi-Fault CLI Integration

Current multi-fault support:

- Pure-Python loading of copied `fault_data/`.
- Query co-existing fault IDs, tests, and locations.
- Enrich classification JSON with multi-fault context.

Planned deeper integration:

- Wrap the `defects4j-mf` CLI rather than embedding it.
- Add a `MultiFaultClient`.
- Support multi-fault checkout, GZoltar coverage, and fault identification.
- Add CLI commands such as `mf-info`, `mf-checkout`, `mf-coverage`,
  and `mf-collect`.
- Treat WSL path translation carefully.

### 28.4 Parallel and Scalable Execution

Planned scale improvements:

- Two-phase pipeline: collect all contexts first, classify all contexts second.
- Parallel collection using `ThreadPoolExecutor`.
- Rate-limit LLM calls separately from local Defects4J work.
- Move work directories to WSL-native ext4 when using WSL for major speedups.
- Consider Docker-native execution for repeatable large studies.
- Consider checkout caching to reduce repeated Defects4J checkout time.

Important insight:

- A local GPU does not materially accelerate the current pipeline because the
  bottlenecks are Defects4J subprocesses, filesystem I/O, and remote LLM calls.

### 28.5 Reliability and Error Handling

Planned improvements:

- Typed failure taxonomy.
- Structured result types instead of raising for expected failures.
- Recovery recipes per failure type.
- Context-window preflight checks.
- Token/cost usage tracking.
- Auth error hints.
- `--output-format json` for machine-readable CLI results.
- Configuration file support such as `.d4j_pipeline.toml`.
- Prompt context reduction strategy when inputs get too large.

### 28.6 RCEGen-Style Root Cause Explanation Integration

Planned research expansion:

- Add an `rce_text` field: a concise natural-language root cause explanation.
- Constrain RCE generation by ODC type and evidence.
- Add an LLM-as-judge module for explanation quality.
- Add batch evaluation metrics inspired by RCEGen, including agreement between
  judges and similarity to human references.
- Build a human reference dataset stratified by ODC type.
- Run information ablation studies to quantify the value of stack traces,
  test source, production snippets, coverage, and fix diffs.

Positioning:

- RCEGen uses LLMs to generate root cause explanations.
- This pipeline can offer a stronger evidence-grounded and taxonomy-grounded
  RCE by tying explanations to ODC labels and execution evidence.

## 29. Recommended Commands

Environment checks:

```powershell
python -m d4j_odc_pipeline d4j pids
python -m d4j_odc_pipeline d4j bids --project Lang
python -m d4j_odc_pipeline d4j info --project Lang --bug 1
```

Single-bug runs:

```powershell
python -m d4j_odc_pipeline collect --project Lang --bug 1 --skip-coverage
python -m d4j_odc_pipeline classify --context .\.dist\runs\Lang_1_prefix\context.json
python -m d4j_odc_pipeline run --project Lang --bug 1 --skip-coverage
python -m d4j_odc_pipeline run --project Lang --bug 1 --include-fix-diff --skip-coverage
```

Study runs:

```powershell
python -m d4j_odc_pipeline study-plan --target-bugs 68
python -m d4j_odc_pipeline study-run --manifest manifest_68.json --skip-coverage
python -m d4j_odc_pipeline study-analyze --manifest manifest_68.json
python -m d4j_odc_pipeline study-baseline --manifest manifest_68.json --scientific-artifacts-root .\.dist\study\artifacts_68
python -m d4j_odc_pipeline study-naive --manifest manifest_68.json --scientific-artifacts-root .\.dist\study\artifacts_68
python -m d4j_odc_pipeline study-export --analysis .\.dist\study\analysis_68.json
```

Multi-fault:

```powershell
python -m d4j_odc_pipeline multifault --project Lang --bug 1
python -m d4j_odc_pipeline multifault-enrich --classification .\.dist\runs\Lang_1_prefix\classification.json
```

Safer unit test command:

```powershell
python -m pytest tests/test_comparison.py tests/test_defects4j.py tests/test_llm.py tests/test_parsing.py tests/test_prompting.py tests/test_analysis.py tests/test_batch.py
```

Avoid running `tests/test_url_fetch.py` unless live network integration testing
is intentional.

## 30. Bottom Line for Future LLMs

For research reasoning:

- Start with this file, then read `docs/RQs_JSS.md`, `docs/METHODOLOGY.md`,
  `docs/eval_defence.md`, and `docs/odc_doc.md`.
- Remember that JSS reviewers need theory, reproducibility, baselines,
  statistical analysis, honest threats to validity, and clear scope.

For implementation work:

- Start with `d4j_odc_pipeline/pipeline.py`.
- Then trace into `prompting.py`, `models.py`, `llm.py`, `defects4j.py`,
  `comparison.py`, `analysis.py`, `results_export.py`, and `batch.py`.
- Use `odc.py` as the canonical label source.

For RQ2 work:

- Do not confuse naive taxonomy-free classification with open-schema
  seven-plus-Other coverage.
- Implement `Other` as a falsifiability instrument, not a permanent ODC class.
- Require structured justification for every `Other`.

For evaluation:

- Do not call pre/post divergence a failure by default.
- Explain divergence through evidence asymmetry, ODC boundary ambiguity, and
  multi-fault reality.
- Report strict match, top-2 match, family match, kappa, semantic distance, and
  per-project reliability together.

For manuscript positioning:

- The contribution is not "LLM labels bugs."
- The contribution is an evidence-grounded, ODC-grounded, scientifically
  prompted, empirically evaluated defect-classification framework for
  Defects4J, with explicit analysis of taxonomy coverage, component
  contribution, semantic divergence, and project-level reliability.
