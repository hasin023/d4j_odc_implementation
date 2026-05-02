# AGENTS.md

This file is the working map for future agentic LLMs operating in this repository.

## 1. What This Repository Is

This repo implements a research pipeline that:

1. Collects bug evidence from a Defects4J Java bug.
2. Builds a structured `context.json`.
3. Prompts an LLM to classify the bug into exactly one of 7 ODC defect types.
4. Optionally attaches additive ODC opener/closer-aligned metadata to the classification.
5. Writes machine-readable and markdown outputs.
6. Optionally compares pre-fix and post-fix classifications for evaluation.

The code lives in `d4j_odc_pipeline/`. The rest of the repo is tests, documentation, and generated experiment state.

The current implementation has two ODC layers:

- Primary, required: one of the 7 ODC `Defect Type` values for `Target=Design/Code`
- Secondary, optional: heuristic opener/closer-aligned metadata such as `target`, `qualifier`, `age`, `source`, `inferred_activity`, `inferred_triggers`, and `inferred_impact`

Important scope note:

- The pipeline does **not** implement the full IBM ODC opener/closer workflow as a fully validated schema.
- It **does** now operationalize an additive ODC mapping layer around the main 7-way defect type classification.
- `target` is effectively fixed to `Design/Code` for this repo's scope.

## 2. Source-of-Truth Order

When information conflicts, use this order:

1. `d4j_odc_pipeline/*.py`
2. `tests/*.py`
3. `AGENTS.md`
4. `README.md`
5. `odc_doc.md`
6. Existing files under `artifacts/`
7. `thesis_plan.md`

Notes:

- `odc_doc.md` is the reference source for generic ODC terminology, not the executable contract.
- `README.md` is a lightweight index page linking to focused docs under `docs/`.
- `docs/SETUP.md` contains installation and environment setup instructions.
- `docs/USAGE.md` contains CLI usage examples and parameter reference.
- `docs/ARCHITECTURE.md` contains technical architecture, ODC taxonomy, and schema documentation.
- Existing experiment outputs in `artifacts/` span multiple schema generations and should not be treated as the current contract.

## 3. High-Level Mental Model

The system is file-oriented and synchronous. There is no database, queue, service layer, or async orchestration.

Primary CLI modes:

- `collect`: Defects4J checkout/test/evidence gathering -> `context.json`
- `classify`: `context.json` -> prompt -> LLM -> `classification.json` (+ optional `report.md`)
- `run`: `collect` + `classify` in one command
- `compare`: compare one pre-fix classification with one post-fix classification
- `compare-batch`: compare many pre-fix/post-fix pairs
- `study-plan`: generate a balanced bug manifest for large-scale batch studies
- `study-run`: execute prefix + postfix runs for every bug in a study manifest (with checkpoint/resume and graceful Ctrl+C)
- `study-analyze`: cross-artifact analysis over prefix/postfix study outputs
- `study-baseline`: run baseline (direct prompt) classifications for RQ2.2 comparison
- `study-naive`: run naive (taxonomy-free) classifications for RQ2.3 comparison
- `study-export`: export analysis results as LaTeX tables and CSV files
- `multifault`: query multi-fault co-existence data from defects4j-mf
- `multifault-enrich`: enrich an existing classification JSON with multi-fault context
- `d4j pids|bids|info`: convenience proxy commands over Defects4J

The filesystem is the main contract:

- `.dist/runs/` contains outputs from standalone commands (`collect`, `run`, `classify`)
- `.dist/study/` contains outputs from batch commands (`study-run`, `study-analyze`)
- `.dist/study/artifacts_<N>/` has `prefix/` and `postfix/` subdirectories for paired runs (N = target_bugs)
- `.dist/study/baseline_<N>/` has `<bug>_prefix/` subdirectories for baseline (direct prompt) classifications
- `.dist/study/naive_<N>/` has `<bug>_prefix/` subdirectories for naive (taxonomy-free) classifications
- `.dist/study/checkpoint.json` tracks progress for resumable batch runs
- `.dist/study/latex/` and `.dist/study/csv/` contain exported tables from `study-export`
- `work/` contains checked-out Defects4J projects (for standalone runs, named `<project>_<bug>_prefix` or `_postfix`)
- `.dist/study/work/` contains checkouts for batch runs

Methodologically, the pipeline has two evidence modes:

- `pre-fix`: default and preferred for realistic classification
- `post-fix`: enabled only when `--include-fix-diff` is used; this adds the real buggy-to-fixed diff as oracle information

## 4. Repo Layout

Tracked authored files:

- `d4j_odc_pipeline/__main__.py`: package entrypoint
- `d4j_odc_pipeline/__init__.py`: package version export
- `d4j_odc_pipeline/cli.py`: argparse CLI and command dispatch
- `d4j_odc_pipeline/pipeline.py`: main orchestration for collection, classification, validation, and report writing
- `d4j_odc_pipeline/defects4j.py`: Defects4J wrapper, query/export helpers, coverage parsing, WSL path handling
- `d4j_odc_pipeline/llm.py`: provider abstraction for Gemini, OpenRouter, and generic OpenAI-compatible APIs
- `d4j_odc_pipeline/prompting.py`: prompt construction, evidence payload shaping, ODC mapping hints
- `d4j_odc_pipeline/odc.py`: canonical 7-type ODC taxonomy and family mapping
- `d4j_odc_pipeline/models.py`: dataclasses for persisted artifacts
- `d4j_odc_pipeline/parsing.py`: failing test parsing, stack frame parsing, JSON extraction from LLM output
- `d4j_odc_pipeline/comparison.py`: pre-fix/post-fix evaluation logic with extended analysis layers (semantic distance, evidence asymmetry, attribute concordance, divergence patterns, insight generation)
- `d4j_odc_pipeline/multifault.py`: pure-Python loader/querier for defects4j-mf multi-fault JSON data
- `d4j_odc_pipeline/batch.py`: batch manifest generation, batch execution with checkpoint/resume, baseline runner, signal handling, progress bar, and cross-artifact analysis
- `d4j_odc_pipeline/web_fetch.py`: bug report retrieval from GitHub, JIRA, or generic pages
- `d4j_odc_pipeline/analysis.py`: cross-study statistical analysis: type distribution (RQ1.1), Impact vs Type (RQ1.2), baseline comparison (RQ2.2), semantic gap (RQ3.1), per-type P/R/F1 (RQ2.1)
- `d4j_odc_pipeline/results_export.py`: LaTeX table and CSV export for manuscript/R/SPSS
- `d4j_odc_pipeline/console.py`: Rich-based console helpers
- `tests/test_batch.py`: batch manifest generation, analysis, signal handling, and checkpoint persistence tests
- `tests/test_comparison.py`: comparison compatibility tests
- `tests/test_defects4j.py`: WSL path normalization tests
- `tests/test_llm.py`: provider/env/schema tests
- `tests/test_parsing.py`: failure parsing and JSON extraction tests
- `tests/test_prompting.py`: prompt payload tests — hidden-oracle exclusion, direct/scientific style isolation, evidence parity
- `tests/test_analysis.py`: analysis module tests — type distribution, chi-squared, Impact vs Type, per-type metrics, baseline comparison, semantic gap
- `tests/test_url_fetch.py`: live integration script with top-level network calls
- `README.md`: usage and setup doc
- `Eval Defence.md`: complete scientific defence for pre-fix/post-fix evaluation methodology
- `odc_doc.md`: IBM ODC reference material
- `thesis_plan.md`: research/background context
- `docs/METHODOLOGY.md`: research methodology, RQ structure, evaluation framework, statistical tests
- `pyproject.toml`: packaging and pytest config
- `requirements.txt`: runtime dependencies
- `.env.example`: sample environment configuration

Generated or local-only areas:

- `.venv/`: local Python environment, not implementation
- `work/`: checked-out Defects4J project snapshots, effectively third-party source trees
- `artifacts/`: generated outputs from experiments
- `fault_data/`: multi-fault JSON data copied from defects4j-mf (Chart, Closure, Lang, Math, Time)
- `.env`: local secrets/config, do not copy into outputs

## 5. Core Execution Flow

### 5.1 `collect`

Primary function: `pipeline.collect_bug_context(...)`

Sequence:

1. Query bug metadata with `Defects4JClient.query_bug_metadata()`.
2. Fetch bug text via `defects4j info`.
3. Fetch bug report content from `report.url` using `web_fetch.fetch_bug_report()`.
4. Checkout buggy version `<bug_id>b`.
5. Compile buggy version.
6. Run tests.
7. Parse failures from `failing_tests` or raw test output.
8. Export relevant Defects4J properties.
9. Select suspicious stack frames from parsed failures.
10. Discover Java source roots.
11. Extract production snippets around suspicious frames.
12. Extract failing test source snippets to show expected behavior.
13. Optionally run coverage and parse Cobertura-style XML.
14. Optionally collect buggy-to-fixed diff as post-fix oracle information.
15. Serialize `BugContext` to JSON.

Important behavior:

- `classes.modified` is stored in `hidden_oracles` and deliberately excluded from the LLM prompt.
- Suspicious production frames are preferred over test frames.
- Framework, JDK, build-tool, and test-runner frames are aggressively filtered out before source snippet extraction.
- Test source extraction is capped to the first 3 failures.
- Coverage is targeted at suspicious classes first, then retried without the instrumentation filter if the first coverage command fails.
- If coverage XML cannot be parsed with the class filter, parsing is retried without the filter as a last resort.
- `fix_diff` is collected only when `--include-fix-diff` is requested, but the `fix_diff` field still exists on `BugContext` as a string and is usually `""` when absent.

### 5.2 `classify`

Primary function: `pipeline.classify_bug_context(...)`

Sequence:

1. Build prompt messages from `BugContext`.
2. Optionally save rendered prompt JSON.
3. Call the configured LLM provider.
4. Extract a JSON object from the raw response.
5. Validate `odc_type`.
6. Canonicalize `family` from `odc.py` instead of trusting the model.
7. Normalize optional ODC mapping fields.
8. Write `classification.json`.
9. Optionally write `report.md`.

Important behavior:

- `build_messages()` always returns exactly two messages: one `system`, one `user`.
- There are three prompt styles: `scientific`, `direct` (zero-shot baseline), and `naive` (taxonomy-free baseline).
- `scientific` includes: taxonomy guidance, JSON contract text, anti-bias rules, scientific debugging protocol, 7-question diagnostic tree, and 5 few-shot examples.
- `direct` includes: taxonomy guidance, JSON contract text, and anti-bias rules only. No protocol, no diagnostic tree, no few-shots. This is the controlled baseline for RQ2.2.
- `naive` includes: no ODC taxonomy, no type names, no anti-bias rules. The LLM classifies in its own words using a simplified JSON schema (`defect_type`, `confidence`, `reasoning_summary`). This is the baseline for RQ2.3.
- All three styles receive identical user evidence payloads (same snippet budget of 8) to avoid confounding comparisons. The naive user payload omits ODC-specific hints.
- The user payload separates `production_code_snippets` and `test_code_snippets`.
- For `scientific` and `direct`, the payload includes `odc_opener_hints` and `odc_closer_hints`. The `naive` payload omits these.
- If `context.fix_diff` is present, the payload also includes `fix_diff_oracle` and the evidence mode becomes `post-fix`.
- Gemini uses a response JSON schema. OpenRouter and `openai-compatible` use chat completions plus post-hoc parsing.
- `dry_run=True` skips the LLM call and returns `None`.
- Only `odc_type` is strictly validated against canonical names.
- `target` defaults to `Design/Code` if the model omits it.
- `family` is always overwritten with `family_for(odc_type)`.

### 5.3 `compare`

Primary functions:

- `comparison.compare_classifications(...)`
- `comparison.batch_compare(...)`

Metrics:

- Strict match: exact `odc_type`
- Top-2 match: primary vs `alternative_types`
- Family match: same high-level family
- Cohen's kappa: batch only

Important behavior:

- Comparison carries forward optional closer fields like `target`, `qualifier`, `age`, and `source`.
- Comparison reads `family` when available, but falls back to legacy `coarse_group` for backward compatibility.
- `compare-batch` auto-discovers pairs by directory name, typically using `_prefix` and `_postfix` suffixes.

## 6. Module-by-Module Guide

### `cli.py`

Owns the CLI surface:

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
- `d4j pids|bids|info`

Important details:

- Reads `DEFAULT_LLM_PROVIDER` and `DEFAULT_LLM_MODEL` at parser build time.
- Includes a lightweight `.env` loader that only fills variables not already present in `os.environ`.
- `classify --report` is optional.
- `--work-dir` is optional for `collect` and `run` — defaults to `work/<project>_<bug>_prefix` (or `_postfix` with `--include-fix-diff`).
- `run` outputs default to `.dist/runs/<project>_<bug>_<mode>/` when `--context-output`, `--classification-output`, and `--report` are omitted.
- `collect --output` defaults to `.dist/runs/<project>_<bug>_<mode>/context.json` when omitted.
- `study-plan --output` defaults to `.dist/study/manifest_<target_bugs>.json`.
- `study-run` reads `target_bugs` from the manifest and defaults `--artifacts-root` to `.dist/study/artifacts_<target_bugs>/`.
- `study-run --manifest` and `study-analyze --manifest` resolve bare filenames under `.dist/study/`.
- `study-analyze` defaults `--prefix-dir`, `--postfix-dir`, `--output`, `--report` using the manifest's `target_bugs`.
- `study-baseline` defaults `--baseline-root` to `.dist/study/baseline_<target_bugs>/`.
- `study-baseline --scientific-artifacts-root` reuses `context.json` from scientific runs for evidence parity.
- `study-naive` defaults `--naive-root` to `.dist/study/naive_<target_bugs>/`.
- `study-naive --scientific-artifacts-root` reuses `context.json` from scientific runs for evidence parity.
- `study-export` writes LaTeX tables to `<output-dir>/latex/` and CSV files to `<output-dir>/csv/`.
- `multifault-enrich --output` defaults to `classification_enriched.json` alongside the input file.
- `study-run` installs SIGINT/SIGBREAK signal handlers for graceful Ctrl+C shutdown.
- `d4j bids` supports `--all` to include deprecated bug IDs.

### `batch.py`

Manages large-scale batch workflows.

Key responsibilities:

- Manifest generation with balanced per-project sampling (`generate_study_manifest`)
- Batch execution with paired prefix/postfix runs (`run_batch_from_manifest`)
- Baseline execution with prefix-only direct-prompt runs (`run_baseline_from_manifest`)
- Signal handling: SIGINT sets a shutdown flag; checked at every loop iteration and between collect/classify steps
- Checkpoint persistence: `checkpoint.json` written after each entry; loaded on restart to skip completed entries
- Manifest hash: SHA-256 of sorted entry keys detects stale checkpoints from different manifests
- Progress bar: Rich progress bar showing current bug and completion count
- Cross-artifact analysis (`analyze_batch_artifacts`): discovers prefix/postfix pairs, computes transition matrices, identifies divergence patterns

Important behavior:

- First Ctrl+C sets a flag and prints a warning; the current bug finishes, then the loop exits.
- Second Ctrl+C raises `SystemExit(130)` for immediate termination.
- `checkpoint.json` uses a manifest hash to detect when the manifest has changed; stale checkpoints are ignored.
- `skip_existing=True` (default) skips entries where all 3 output files exist, independent of checkpoint.

### `pipeline.py`

This is the real orchestrator and the best first file to read for behavioral changes.

Key responsibilities:

- orchestration of evidence collection
- prompt render / classification lifecycle
- report writing
- suspicious-frame selection
- Java source resolution
- fix diff collection
- test source extraction
- payload validation and normalization

If you change artifact structure, evidence collection, optional ODC mapping fields, or markdown report content, this file will probably need edits.

### `defects4j.py`

Wraps the external Defects4J CLI.

Important details:

- Reads `DEFECTS4J_CMD` or takes an override.
- Supports WSL path conversion via `DEFECTS4J_PATH_STYLE=wsl`.
- Normalizes `-w`, `-i`, and `-o` path arguments when WSL mode is active.
- Forces subprocess timezone to `America/Los_Angeles`.
- Treats `test` and `coverage` as allowed-to-fail because failing tests are expected.
- Calls `query -H` first and only requests query fields actually available for the current Defects4J project.
- Parses coverage XML from the checked-out project tree.

### `llm.py`

Minimal provider abstraction.

Supported provider strings:

- `gemini`
- `openrouter`
- `openai-compatible`

Important details:

- default API key env vars are provider-specific
- OpenRouter can attach `HTTP-Referer` and `X-OpenRouter-Title`
- OpenRouter currently uses the same `/chat/completions` transport path as the generic OpenAI-compatible client
- Gemini uses `generateContent` plus `responseJsonSchema`
- transient 429/500/502/503 and network errors are retried with exponential backoff
- invalid JSON payloads and invalid `odc_type` values are **not** retried

### `prompting.py`

Encodes most of the research methodology.

Contains:

- ODC instructions
- scientific debugging protocol
- 5 few-shot examples
- evidence payload shaping
- additive opener/closer alignment hints

Important details:

- Hidden oracle metadata is filtered out before prompt construction.
- `odc_opener_hints` are inferred heuristically from bug report text, `bug_info`, failure headlines, and stack trace excerpts.
- `odc_closer_hints` always set `target=Design/Code`, and may add heuristic `qualifier_hint` and `age_hint` when `fix_diff` is available.
- `source_hint` currently remains `null`.
- Both `scientific` and `direct` prompt styles use the same production snippet budget of 8 (no confound between evidence and prompt engineering).

### `odc.py`

Canonical taxonomy source in code.

The seven supported types are:

- `Algorithm/Method`
- `Assignment/Initialization`
- `Checking`
- `Timing/Serialization`
- `Function/Class/Object`
- `Interface/O-O Messages`
- `Relationship`

Families:

- `Control and Data Flow`
- `Structural`

Also contains:

- type summaries
- indicators
- contrastive "distinguish from" guidance
- a backward-compatible `coarse_group_for()` alias

### `models.py`

Defines the persisted dataclasses:

- `StackFrame`
- `Failure`
- `CodeSnippet`
- `CoverageLine`
- `CoverageClass`
- `BugContext`
- `ClassificationResult`

Current schema additions you must know:

- `BugContext.fix_diff`
- `ClassificationResult.target`
- `ClassificationResult.qualifier`
- `ClassificationResult.age`
- `ClassificationResult.source`
- `ClassificationResult.inferred_activity`
- `ClassificationResult.inferred_triggers`
- `ClassificationResult.inferred_impact`
- `ClassificationResult.evidence_mode`

### `parsing.py`

Parses:

- Defects4J `failing_tests` style blocks
- Java stack frames
- JSON objects embedded in raw LLM output

Important details:

- JSON extraction can recover from fenced code blocks and from responses that contain extra text before the first `{`.

### `comparison.py`

Comparison/reporting logic for evaluation experiments with extended analysis layers.

Important details:

- preserves backward compatibility for old `coarse_group` artifacts
- preserves optional closer fields in comparison records
- computes Cohen's kappa in batch mode (global and per-project)
- `compute_per_project_kappa()` returns per-project kappa values for RQ4.1
- writes markdown reports for both single and batch comparisons
- batch reports include a per-project kappa table with Landis & Koch interpretation

Extended analysis layers (added for thesis defense):

- **Semantic Distance** (Layer A): 0.0–1.0 ODC type proximity score based on family and type boundaries. Calibrated from Thung 2012 and Chillarege 1992.
- **Evidence Asymmetry** (Layer B): structured explanation of WHY pre-fix ≠ post-fix, with 3 rules (symptom/cause asymmetry, ODC boundary ambiguity, multi-fault contamination) and literature references.
- **Attribute Concordance** (Layer C): tracks agreement on target/qualifier/age/source beyond the primary type.
- **Divergence Pattern** (Layer D): categorizes each comparison as `exact-match`, `soft-divergence`, `moderate-divergence`, or `hard-divergence`.
- **Insights** (Layer E): generates human-readable insight strings for each comparison.

New public functions:

- `semantic_distance(type_a, type_b)` → float
- `classify_divergence_pattern(strict, top2, family, distance)` → str
- `analyze_evidence_asymmetry(prefix_data, postfix_data, pattern)` → dict
- `compute_attribute_concordance(prefix_data, postfix_data)` → dict
- `generate_comparison_insights(prefix_data, postfix_data, result, ...)` → list[str]
- `compute_per_project_kappa(results)` → dict[str, float | None]

### `analysis.py`

Cross-study statistical analysis engine aligned to research questions.

Key functions:

- `compute_type_distribution(classifications)` → type/family frequency, per-project breakdown (RQ1.1)
- `compute_project_type_correlation(classifications)` → chi-squared test of independence (RQ1.1)
- `analyze_impact_vs_type(classifications)` → Impact vs Type separation analysis (RQ1.2)
- `compute_per_type_metrics(pairs)` → precision/recall/F1 per ODC type (RQ2.1)
- `compare_baseline_vs_scientific(scientific, baseline, postfix)` → improvement deltas (RQ2.2)
- `compute_semantic_gap_metrics(pairs)` → mean/median/max distance, per-project breakdown (RQ3.1)
- `map_naive_to_odc(naive_label)` → keyword heuristic mapping from free-form label to closest ODC type (RQ2.3)
- `analyze_naive_labels(naive_classifications)` → vocabulary size, entropy, ODC coverage, mapped distribution (RQ2.3)
- `compute_taxonomy_grounding_metrics(naive, direct, scientific)` → 3-tier prompt comparison metrics (RQ2.3)

Important details:

- Chi-squared test requires `scipy`; gracefully returns None if not installed.
- Only classifications with valid canonical ODC type names are counted.
- Impact vs Type analysis uses a naive symptom→type mapping to demonstrate that the pipeline improves over naive classification.

### `results_export.py`

LaTeX table and CSV export for manuscript submission.

Export functions:

- `export_type_distribution_latex(analysis)` → LaTeX table (Table 1)
- `export_accuracy_table_latex(analysis)` → LaTeX table (Table 2)
- `export_confusion_matrix_latex(analysis)` → LaTeX table (Table 3)
- `export_per_project_kappa_latex(analysis)` → LaTeX table (Table 4)
- `export_baseline_comparison_latex(analysis)` → LaTeX table (Table 5)
- `export_taxonomy_grounding_latex(analysis)` → LaTeX table (Table 6) — naive vs direct vs scientific
- `export_all_csv(analysis, output_dir)` → list of CSV file paths

Important details:

- All LaTeX uses `booktabs` package conventions (`\toprule`, `\midrule`, `\bottomrule`).
- CSV exports use standard Python `csv.writer` with UTF-8 encoding.
- Export functions accept the same analysis dict produced by `analysis.py` functions.

### `multifault.py`

Pure-Python loader for defects4j-mf multi-fault data.

Supported projects: Chart, Closure, Lang, Math, Time.

Data sources:

- `{Project}.json`: version → fault_id → [triggering_test_names]
- `{Project}_backtrack.json`: fault location tracking through history

Key functions:

- `get_multifault_summary(project, bug_id)` → `MultiFaultSummary`
- `get_coexisting_fault_ids(fault_data_dir, project, bug_id)` → list[int]
- `get_fault_tests(fault_data_dir, project, bug_id, fault_id)` → list[str]
- `get_fault_locations(fault_data_dir, project, bug_id, fault_id)` → list[FaultLocation]
- `enrich_classification(classification, fault_data_dir)` → dict

Path resolution order:

1. Explicit `fault_data_dir` parameter
2. `MULTIFAULT_DATA_DIR` environment variable
3. `implementation/fault_data/` (sibling of `d4j_odc_pipeline/`)

### `web_fetch.py`

Fetches bug report text.

Routing:

- GitHub issue API first
- JIRA API first
- generic HTML/text/JSON fallback always available

Design choices:

- returns `WebFetchResult` instead of raising
- normalizes `http` to `https` unless localhost
- truncates fetched content with `max_chars=12000` by default
- the generic extractor is the real backbone path

### `console.py`

Pure UX layer for CLI output.

Safe to ignore for algorithmic changes unless you are changing CLI presentation or quiet-mode behavior.

## 7. Artifact Contracts

### Current `context.json`

Serialized from `BugContext`. Important top-level fields:

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

Important notes:

- `code_snippets` stores both production and test snippets in one list.
- The prompt layer splits them into `production_code_snippets` and `test_code_snippets` based on `snippet.reason`.
- `fix_diff` is a string field in the current schema even when empty.

### Current `classification.json`

Serialized from `ClassificationResult`. Important top-level fields:

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

Important notes:

- `family` is canonicalized from `odc.py`, not trusted from the model.
- `target` is defaulted to `Design/Code` if omitted.
- `qualifier`, `age`, `source`, and inferred opener fields are optional and may be `null`, empty, or omitted by older artifacts.
- `alternative_types` is a list of objects with `type` and `why_not_primary`.

### Current comparison outputs

Single-bug comparison fields include:

- `prefix_odc_type`
- `postfix_odc_type`
- `prefix_family`
- `postfix_family`
- `strict_match`
- `top2_match`
- `family_match`
- `match_detail`
- `prefix_target`
- `postfix_target`
- `prefix_qualifier`
- `postfix_qualifier`
- `prefix_age`
- `postfix_age`
- `prefix_source`
- `postfix_source`
- `prefix_evidence_mode`
- `postfix_evidence_mode`

Batch comparison includes:

- counts
- rates
- `cohens_kappa`
- `per_project_kappa`
- `per_bug`
- `type_confusion_matrix`
- `avg_semantic_distance`
- `divergence_pattern_counts`
- `avg_attribute_concordance`

### Historical schema drift you must know

Existing saved artifacts under `artifacts/` may reflect older output versions:

- `classification.json` may use `coarse_group` instead of `family`
- `classification.json` may omit `evidence_mode`
- older `classification.json` files may omit the additive opener/closer fields entirely
- older `context.json` files may omit `fix_diff`
- older comparison outputs may use `prefix_coarse_group`, `postfix_coarse_group`, and `coarse_group_match`

Do not assume sample artifacts match the current code exactly.

## 8. Runtime Directories

### `work/`

This is generated experiment state, not implementation source.

Each work directory is a user-chosen checkout location. Do not trust the folder name alone to infer whether it represents buggy or fixed code. The actual source of truth is:

- `.defects4j.config`
- `defects4j.build.properties`
- the `version_id` saved in the corresponding `context.json`

Many directories happen to end in `b`, but that is a convention, not an enforced rule. Contents usually include:

- `.defects4j.config`
- `defects4j.build.properties`
- `failing_tests`
- project build files
- full Java source tree
- possible coverage outputs like `coverage.xml`

Treat these as disposable checkouts unless the user explicitly wants to inspect a specific bug instance.

Directories like `${work_dir.name}_fixed` are temporary fixed-version checkouts used by fix-diff collection. Cleanup is attempted automatically, but stale directories may remain.

### `artifacts/`

This is generated experiment output.

Common per-run files are:

- `context.json`
- `classification.json`
- `report.md`
- `prompt.json` when `--prompt-output` is used
- `instrument_classes.txt` when coverage was run
- optional comparison files

Comparison batch conventions:

- `compare-batch` expects matching directories under a prefix root and postfix root
- the intended naming pattern is `<Project>_<Bug>_prefix/` and `<Project>_<Bug>_postfix/`
- each matching directory should contain `classification.json`

Subdirectory names are experiment-specific and not fully standardized beyond the file names inside them. Trust saved JSON fields over folder names.

## 9. Environment and Setup

Python/runtime requirements:

- Python `>=3.11`
- `rich`
- `requests`
- `scipy` (optional — used for chi-squared test in `analysis.py`; graceful fallback if missing)

Package metadata:

- package name: `d4j-odc-pipeline`
- console entrypoint: `d4j-odc`
- current package version in code: `0.2.0`

Core configuration variables:

- `DEFAULT_LLM_PROVIDER`
- `DEFAULT_LLM_MODEL`
- `GEMINI_API_KEY`
- `GEMINI_BASE_URL`
- `OPENROUTER_API_KEY`
- `OPENROUTER_BASE_URL`
- `OPENROUTER_HTTP_REFERER`
- `OPENROUTER_APP_TITLE`
- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `DEFECTS4J_CMD`
- `DEFECTS4J_PATH_STYLE`
- `MULTIFAULT_DATA_DIR` — path to `fault_data/` directory from defects4j-mf; defaults to `./fault_data/` relative to implementation root

Defects4J path style:

- `wsl`: convert `-w`, `-i`, and `-o` path arguments to `/mnt/<drive>/...`
- `native`: leave paths untouched

## 10. Research Intent

The repo is built around a few methodological choices:

- pre-fix evidence is the default
- post-fix diff is optional and explicitly treated as oracle information
- hidden leakage via `classes.modified` should not enter the prompt
- classification should use scientific-debugging-style reasoning by default
- the mandatory label is still the 7-class ODC `Defect Type`
- opener/closer-aligned metadata is additive, optional, and partly heuristic
- evaluation distinguishes exact type vs alternative-type overlap vs family-level agreement

`odc_doc.md` is the underlying ODC reference.

What the implementation currently does with ODC attributes:

- `Defect Type`: mandatory
- `Target`: effectively fixed to `Design/Code`
- `Qualifier`: optional, mainly hinted from fix-diff shape
- `Age`: optional, mainly hinted from fix-diff size/shape; the prompt/schema allow values like `ReFixed`, but the current hint builder only suggests `Base`, `New`, or `Rewritten`
- `Source`: optional field in outputs, but not currently inferred in the hint builder
- `Activity`, `Triggers`, `Impact`: represented as inferred or candidate metadata, not authoritative opener labels

`thesis_plan.md` is background context, not executable policy.

## 11. Known Drift, Caveats, and Traps

These are the main places future agents get misled:

1. `README.md` still describes retrying invalid classifications, but the code only retries transient HTTP/network failures in `llm._urlopen_json()`.
2. `cli.main()` catches `Defects4JError`, `FileNotFoundError`, and `ValueError`, but it does **not** catch `LLMError`, so auth/network/provider failures may currently bubble out as uncaught exceptions.
3. `family` in `classification.json` is not trusted from the model; it is always overwritten with `odc.family_for(odc_type)`.
4. Only `odc_type` is validated against canonical labels. Optional ODC fields like `qualifier`, `age`, `source`, and the inferred opener fields are stored with only minimal trimming/list coercion.
5. `odc_opener_hints` and `odc_closer_hints` are heuristic prompt aids, not ground truth ODC labels.
6. `source_hint` in `odc_closer_hints` is currently always `null`.
7. `fix_diff` is a string field on `BugContext`; when not requested or unavailable it is usually `""`, not absent.
8. `tests/test_url_fetch.py` is not a normal unit test file. It is a live integration script with top-level network calls and print statements.
9. Full `pytest` runs may import `tests/test_url_fetch.py` and trigger network access. In restricted or offline environments, avoid that unless you explicitly want it.
10. `compare-batch` only finds pairs when directory names line up after stripping optional `_prefix` and `_postfix` suffixes.
11. Folder names in `work/` and `artifacts/` are not reliable indicators of buggy/fixed or pre-fix/post-fix status. Trust JSON fields and Defects4J config files instead.
12. Coverage parsing is best-effort. Even after a coverage command runs, parsed coverage may still be empty.

## 12. Safe Working Conventions for Future Agents

Do this:

- read `pipeline.py` first for behavioral work
- treat `d4j_odc_pipeline/` as the authoritative implementation
- update tests when changing prompts, schemas, parsing behavior, or ODC mapping fields
- keep backward compatibility in comparison logic when possible
- document schema changes in `README.md` and `AGENTS.md`
- keep secrets out of commits and summaries

Do not do this unless explicitly asked:

- edit `.env`
- mass-edit `work/` checkouts
- treat `artifacts/` as canonical source code
- assume old reports reflect current field names

If you change evidence schema:

1. update `models.py`
2. update writers/readers in `pipeline.py`
3. update prompt payload shaping in `prompting.py`
4. update tests
5. update `README.md` and this file

If you change ODC label names or taxonomy boundaries:

1. update `odc.py`
2. update prompt rules/examples in `prompting.py`
3. update validation in `pipeline.py`
4. update comparison/report wording
5. check compatibility with old artifacts

If you change the additive ODC opener/closer mapping layer:

1. update the hint builder in `prompting.py`
2. update the JSON schema in `llm.py`
3. update `ClassificationResult` in `models.py`
4. update payload normalization and report writing in `pipeline.py`
5. update comparison persistence in `comparison.py` if the new fields matter there
6. update tests and docs

## 13. Recommended Commands

Useful commands (simplified with smart defaults):

```powershell
python -m d4j_odc_pipeline d4j pids
python -m d4j_odc_pipeline d4j bids --project Lang
python -m d4j_odc_pipeline d4j info --project Lang --bug 1
python -m d4j_odc_pipeline collect --project Lang --bug 1 --skip-coverage
python -m d4j_odc_pipeline classify --context .\.dist\runs\Lang_1_prefix\context.json
python -m d4j_odc_pipeline run --project Lang --bug 1 --skip-coverage
python -m d4j_odc_pipeline run --project Lang --bug 1 --include-fix-diff --skip-coverage
python -m d4j_odc_pipeline compare --prefix .\artifacts\Lang_1\classification.json --postfix .\artifacts\Lang_1f\classification.json --output .\artifacts\Lang_1\comparison.json
python -m d4j_odc_pipeline compare-batch --prefix-dir .\artifacts\prefix_runs --postfix-dir .\artifacts\postfix_runs --output .\artifacts\batch_comparison.json
python -m d4j_odc_pipeline multifault --project Lang --bug 1
python -m d4j_odc_pipeline multifault-enrich --classification .\artifacts\Lang_1\classification.json
python -m d4j_odc_pipeline study-plan --target-bugs 68
python -m d4j_odc_pipeline study-run --manifest manifest_68.json --skip-coverage
python -m d4j_odc_pipeline study-analyze --manifest manifest_68.json
python -m d4j_odc_pipeline study-baseline --manifest manifest_68.json --scientific-artifacts-root .\.dist\study\artifacts_68
python -m d4j_odc_pipeline study-export --analysis .\.dist\study\analysis_68.json
```

Safer unit test command:

```powershell
python -m pytest tests/test_comparison.py tests/test_defects4j.py tests/test_llm.py tests/test_parsing.py tests/test_prompting.py tests/test_analysis.py
```

Only run `tests/test_url_fetch.py` intentionally, because it is a live integration script.

## 14. If You Need To Extend the System

To add new evidence fields:

- extend `BugContext`
- collect data in `pipeline.collect_bug_context()`
- expose it in `prompting._context_payload()`
- update tests and docs

To add a new LLM provider:

- add settings resolution in `LLMClient.from_env()`
- add transport logic in `LLMClient.complete()`
- update CLI provider choices
- document required env vars

To improve ODC opener/closer mapping:

- start in `prompting._build_odc_mapping_hints()`
- decide whether the new signal is just a prompt hint or a persisted output field
- if persisted, thread it through `llm.py`, `models.py`, `pipeline.py`, `comparison.py`, tests, and docs

To improve evaluation:

- start in `comparison.py`
- preserve compatibility with old `coarse_group` outputs unless you intentionally migrate stored artifacts

## 15. Bottom Line

For implementation work, start with `pipeline.py`, then follow the call chain into `prompting.py`, `models.py`, `llm.py`, `defects4j.py`, and `comparison.py`.

For methodology questions, use `odc.py`, `odc_doc.md`, `docs/METHODOLOGY.md`, and the scientific-debugging instructions plus ODC mapping hints in `prompting.py`.

For filesystem/output questions, trust current dataclasses and writers over historical artifact examples.

For any work touching the new ODC opener/closer architecture, trace the full path:

`prompting.py` -> `llm.py` -> `pipeline.py` -> `models.py` -> `comparison.py` -> `tests/`

For analysis/export work, trace: `analysis.py` -> `results_export.py` -> `cli.py` -> `interactive/handlers.py`
