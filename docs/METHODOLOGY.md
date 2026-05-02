# Methodology

This document describes the research methodology used in the Defects4J ODC pipeline, structured around the JSS research questions.

## Study Design

The study evaluates automated ODC defect type classification using two evidence modes (pre-fix and post-fix) and three prompt strategies (scientific, direct baseline, and naive baseline).

### Evidence Modes

| Mode         | Evidence Available                                                      | Purpose                                                                |
| ------------ | ----------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| **Pre-fix**  | Failing tests, stack traces, buggy code snippets, coverage, bug reports | Realistic classification — mirrors what a developer sees before fixing |
| **Post-fix** | All pre-fix evidence + the actual buggy→fixed diff                      | Oracle-assisted classification — uses ground truth fix as reference    |

### Prompt Strategies

| Strategy              | ODC Taxonomy | Scientific Protocol | Few-Shot | Purpose                                                              |
| --------------------- | :----------: | :-----------------: | :------: | -------------------------------------------------------------------- |
| **Scientific**        |      ✅      |         ✅          |    ✅    | Full methodology — the main pipeline approach                        |
| **Direct (Baseline)** |      ✅      |         ❌          |    ❌    | Zero-shot baseline — isolates the contribution of prompt engineering |
| **Naive (Baseline)**  |      ❌      |         ❌          |    ❌    | Taxonomy-free baseline — isolates the contribution of ODC grounding  |

**Controlled variable**: All three strategies receive the **exact same evidence payload** (identical snippet budget, same bug context). The only difference is the system prompt.

## Research Questions

### RQ1.1: ODC Type Distribution

_How are ODC defect types distributed across Defects4J projects?_

- **Method**: Compute type and family frequency distributions from prefix classifications.
- **Statistical test**: Chi-squared test of independence (project × type contingency table).
- **Output**: Distribution tables, per-project breakdowns.

### RQ1.2: Impact vs Type Separation

_Does the pipeline correctly separate ODC Impact (symptom) from ODC Type (root cause)?_

- **Method**: Track `inferred_impact` labels against `odc_type` to demonstrate that the pipeline does not conflate symptoms with root causes.
- **Validation**: Compare naive symptom→type mapping accuracy against the pipeline's actual classifications.
- **Grounding**: IBM ODC v5.2 — Impact and Type are orthogonal attributes.

### RQ2.1: Overall Pipeline Efficacy

_How accurately does the pipeline classify ODC defect types?_

- **Metrics**: 4-tier evaluation framework:
  1. **Strict Match**: Exact type agreement (pre-fix = post-fix)
  2. **Top-2 Match**: Primary type or alternative types overlap
  3. **Family Match**: Same ODC family (Control and Data Flow / Structural)
  4. **Cohen's Kappa**: Inter-rater reliability statistic
- **Per-type metrics**: Precision, recall, and F1 for each ODC type (post-fix as reference).
- **Confusion matrix**: Full 7×7 type transition matrix.

### RQ2.2: Scientific Protocol Efficacy

_Does the scientific debugging protocol improve classification accuracy over a zero-shot baseline?_

- **Method**: Run the same bug set through both `scientific` and `direct` prompt styles, then compare against post-fix classifications.
- **Metrics**: Improvement deltas on strict/top2/family match rates and mean confidence.
- **Isolation**: Same evidence, same model, same bugs — only the system prompt differs.

### RQ2.3: Taxonomy Grounding Effect

_Does explicit ODC taxonomy grounding improve classification consistency and actionability over unconstrained LLM classification?_

- **Method**: Run the same bug set through the `naive` prompt style (no ODC taxonomy, no labels, no framework guidance) and compare against `direct` and `scientific` results.
- **Metrics**:
  - **Vocabulary size**: Number of unique free-form labels vs. fixed 7-type taxonomy.
  - **Label entropy**: Shannon entropy of the label distribution (higher = more scattered).
  - **ODC coverage**: How many of the 7 canonical ODC types are naturally discovered by the naive classifier.
  - **Vocabulary reduction ratio**: Percentage reduction in label space from naive → taxonomy-grounded.
- **Keyword mapping**: Free-form labels are mapped to the closest ODC type using keyword heuristics from `odc.py` indicators.
- **Isolation**: Same evidence, same model, same bugs — the naive prompt has no ODC concepts at all.

### RQ3.1: Semantic Gap Quantification

_What is the magnitude of the semantic gap between pre-fix and post-fix classifications?_

- **Method**: Compute ODC semantic distance (0.0–1.0) for each bug pair using a calibrated distance matrix.
- **Metrics**: Mean/median/max distance, per-project breakdown, divergence pattern distribution.
- **Patterns**: Each bug is classified as `exact-match`, `soft-divergence`, `moderate-divergence`, or `hard-divergence`.

### RQ4.1: Per-Project Reliability

_How does classification reliability vary across different Defects4J projects?_

- **Method**: Compute Cohen's Kappa separately for each project.
- **Interpretation**: Landis & Koch scale (slight → almost perfect).
- **Insight**: Identifies which projects are harder/easier for automated ODC classification.

## Evaluation Framework

### 4-Tier Accuracy Assessment

```
Tier 1: Strict Match    → pre-fix type == post-fix type
Tier 2: Top-2 Match     → primary or alternative types overlap
Tier 3: Family Match    → same ODC family
Tier 4: Cohen's Kappa   → chance-corrected agreement
```

### Extended Analysis Layers

| Layer | Name                  | Description                                                     |
| ----- | --------------------- | --------------------------------------------------------------- |
| A     | Semantic Distance     | 0.0–1.0 ODC type proximity score (Thung 2012, Chillarege 1992)  |
| B     | Evidence Asymmetry    | Structured explanation of WHY pre-fix ≠ post-fix                |
| C     | Attribute Concordance | Agreement on target/qualifier/age/source beyond primary type    |
| D     | Divergence Pattern    | Categorization: exact-match / soft / moderate / hard divergence |
| E     | Insights              | Human-readable interpretive text for each comparison            |

### Statistical Tests

| Test            | Usage                                            | Implementation                                |
| --------------- | ------------------------------------------------ | --------------------------------------------- |
| Cohen's Kappa   | Inter-rater reliability (global and per-project) | `comparison.compute_cohens_kappa()`           |
| Chi-squared     | Project × type independence                      | `analysis.compute_project_type_correlation()` |
| Per-type P/R/F1 | Classification accuracy per ODC type             | `analysis.compute_per_type_metrics()`         |

## Artifact Layout

```
.dist/study/
├── manifest_<N>.json              # Bug selection manifest
├── artifacts_<N>/
│   ├── prefix/<bug>_prefix/       # Pre-fix classifications (scientific)
│   └── postfix/<bug>_postfix/     # Post-fix classifications (scientific)
├── baseline_<N>/
│   └── <bug>_prefix/              # Pre-fix classifications (direct baseline)
├── analysis_<N>.json              # Cross-study analysis results
├── analysis_<N>.md                # Human-readable analysis report
├── latex/                         # LaTeX table exports
│   ├── type_distribution.tex
│   ├── accuracy.tex
│   ├── confusion_matrix.tex
│   ├── per_project_kappa.tex
│   └── baseline_comparison.tex
└── csv/                           # CSV exports for R/SPSS
    ├── per_bug_comparison.csv
    ├── type_distribution.csv
    ├── per_project_kappa.csv
    ├── semantic_gap_per_bug.csv
    └── per_type_metrics.csv
```

## References

- Chillarege, R. et al. (1992). _Orthogonal Defect Classification — A Concept for In-Process Measurements_. IEEE TSE.
- Thung, F. et al. (2012). _To what extent could we detect field defects?_ ISSRE.
- Kang, S. et al. (2023). _Automated Software Defect Type Prediction_. IST.
- Landis, J. R. & Koch, G. G. (1977). _The Measurement of Observer Agreement for Categorical Data_. Biometrics.
