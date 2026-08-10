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
- Secondary: the ODC opener `Impact` attribute (v5.2 §3.3) — single-select from the 13 official categories + `Unknown`, taught to the LLM and strictly validated (`ClassificationResult.impact`); the one opener attribute the pipeline claims (see `docs/odc_alignment_audit.md`)
- Tertiary, optional/heuristic: closer-aligned metadata `target`, `qualifier`, `age`, `source`. The legacy `inferred_activity`, `inferred_triggers`, `inferred_impact` fields remain on `ClassificationResult` for reading old artifacts but are no longer populated by prompts (Activity/Trigger are not reliably determinable from Defects4J evidence — see the audit doc)

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
- `study-run`: execute prefix + postfix runs for every bug in a study manifest, for ONE condition (`--taxonomy` x `--strategy`, any of the 5 valid combos — with checkpoint/resume and graceful Ctrl+C). Replaces the tombstoned `study-baseline`/`study-naive`/`study-coverage`/`study-classify`.
- `study-drift`: cross-artifact prefix/postfix drift analysis over study outputs for ONE condition (RQ1/RQ3/RQ5). Renamed from `study-analyze` (tombstoned).
- `study-escape`: RQ2 taxonomy-coverage/escape-rate metrics between the closed and open passes of one `--strategy`, writing `taxonomy_coverage_<N>.json`. Needs both passes already produced by `study-run`.
- `study-ladder`: RQ4 ablation-ladder metrics (vocabulary size / entropy / ODC coverage) across an ordered `--tags` list of condition tags, prefix-only, writing `taxonomy_grounding_<N>.json`.
- `study-export`: export analysis results as LaTeX tables and CSV files
- `multifault`: query multi-fault co-existence data from defects4j-mf
- `multifault-enrich`: enrich an existing classification JSON with multi-fault context
- `d4j pids|bids|info`: convenience proxy commands over Defects4J

The filesystem is the main contract:

- `.dist/runs/` contains outputs from standalone commands (`collect`, `run`, `classify`)
- `.dist/study/` contains outputs from batch commands (`study-run`, `study-drift`, `study-escape`, `study-ladder`)
- `.dist/study/artifacts_<N>/` has `prefix/` and `postfix/` subdirectories for paired runs (N = target_bugs)
- All classification conditions write into the SAME bug folders under `artifacts_<N>/{prefix,postfix}/` as condition-tagged files (`classification.<strategy>-<taxonomy>.json`); the old `baseline_<N>/`, `naive_<N>/`, `coverage_<N>/` parallel roots are retired
- `.dist/study/artifacts_<N>/checkpoint.pairs.<tag>.json` (study-run) tracks progress for resumable batch runs, one per condition — the old `checkpoint.prefix.<tag>.json` scheme (study-classify) is gone along with the command
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
- `d4j_odc_pipeline/analysis.py`: cross-study statistical analysis: type distribution (RQ1), coverage/escape-rate metrics (RQ2, `compute_coverage_metrics`), per-type P/R/F1 (RQ3, `compute_per_type_metrics`), taxonomy-grounding ablation ladder (RQ4, `compute_taxonomy_grounding_metrics`, generic over N tiers as of 2026-07-08)
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
- **`docs/JSS_HANDOFF.md`: start here for anything paper-drafting or research-results related** — Pipeline/Analysis/RQs/RQ-results in one place, current as of 2026-07-09, with explicit pointers to which of the docs below are current vs stale
- `docs/eval_defence.md`: complete scientific defence for pre-fix/post-fix evaluation methodology (current)
- `docs/odc_doc.md`: IBM ODC reference material (current)
- `docs/RQs_JSS.md`: canonical RQ1-RQ5 wording (current — do not use `docs/METHODOLOGY.md`'s RQ1.1/RQ2.1-style numbering, it's stale/self-flagged)
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
9. Select suspicious stack frames from parsed failures (`_select_suspicious_frames`).
10. Discover Java source roots.
11. Run coverage (once per trigger test, over ALL production classes — see below) and augment `suspicious_frames` with coverage-only classes (`_augment_frames_with_coverage`).
12. Extract production snippets around the (now possibly coverage-augmented) suspicious frames.
13. Extract failing test source snippets to show expected behavior (skips a class/line already covered by a production snippet — see below).
14. Optionally collect buggy-to-fixed diff as post-fix oracle information.
15. Serialize `BugContext` to JSON.

Important behavior:

- `classes.modified` is stored in `hidden_oracles` and deliberately excluded from the LLM prompt.
- `context.json` itself is never sanitized — the pre-fix payload's `bug_info`/`bug_report_content` are stripped of fix-derived sections (`prompting.sanitize_bug_info`/`sanitize_bug_report`) at *payload-build time* only, in `_context_payload` and `agent.execute_probe`'s `bug_report` probe. `_context_payload` additionally strips local-machine-path/corpus-size noise from `bug_info` in BOTH arms, filters `stack_trace_excerpt` through the framework blocklist, caps `metadata.tests.relevant` to a count, and never forwards `notes` (collection bookkeeping) to the LLM at all — none of this touches `context.json` on disk. See §5.2, `docs/odc_alignment_audit.md` §7, and `docs/suspicious_frame_selection.md`.
- Suspicious frames come from TWO sources, tagged via `StackFrame.origin`: `"stack_trace"` (project frames from the parsed failure, preferred, kept in trace order, capped 12) and `"coverage"` (classes the trigger test(s) actually touched but that never appear in any stack trace — e.g. an assertion failure inside the test itself never throws through the buggy class — ranked by coverage line_rate, filling remaining slots up to the same cap of 12, focused on the class's most-executed covered line). See `docs/suspicious_frame_selection.md` for why (SBEST, Kim et al. 2024) and the worked Closure-150 example.
- Framework, JDK, build-tool, and test-runner frames are aggressively filtered out before source snippet extraction.
- Test source extraction is capped to the first 3 failures, and skips a test whose `(class, assertion line)` is already covered by a production snippet (this happens whenever frame selection fell back to test frames) to avoid emitting two near-identical snippets of the same method.
- Coverage instruments ALL production classes discovered under `dir.src.classes` (`_discover_production_classes`) — **not** the suspicious-frame guess and **not** `classes.modified` (Defects4J's own no-instrument-file default would use the fix oracle, which would leak evidence-selection scope) — deliberately decoupled to fix the old circular dependency where coverage could never rescue a bug the frame guess already missed. Runs once per trigger test, merging results (`_merge_coverage`); each run retries without the instrument file if the first attempt fails.
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
- **`docs/condition_model.md` is the single authoritative condition spec.** Two variables: `taxonomy` (free | closed | open; default open) and `strategy` (zero = zero-shot, taxonomy-free by definition | few = static prompt with taxonomy + tree + worked examples | scientific = the enforced loop in agent.py; default scientific). Only 5 valid conditions (validate_condition in odc.py). `--prompt-style` and `--reasoning` are tombstoned. Artifacts written before 2026-07-07 carry old `reasoning` tokens with DIFFERENT semantics ("scientific" meant the narrated single-shot, now retired; "agentic" meant the loop, now called scientific) — never mix old and new artifacts.
- `build_messages()` only handles the two static strategies: `few` (`prompting.py::_build_system_prompt`) includes taxonomy guidance, ODC Impact guidance, JSON contract text, anti-bias rules, a 7-question diagnostic tree, and 5 few-shot examples. The vestigial "Scientific Debugging Protocol" narration block (a leftover of the retired narrated single-shot condition, pilot-proven to change 0/6 labels) was removed 2026-08-10 — `few` is now exactly the 3 components `docs/condition_model.md` §4.3 defines it as (taxonomy + tree + worked examples), ~13% shorter, same content coverage (see `docs/llm_prompting_architecture.md` §1.3 for the full breakdown). `zero` (taxonomy-free by definition; only valid with `--taxonomy free`) includes no ODC taxonomy, no type names, no anti-bias rules — the LLM classifies in its own words using a simplified JSON schema (`defect_type`, `confidence`, `reasoning_summary`).
- `scientific` never calls `build_messages` — it's the enforced loop in `agent.py` (see §5.4/§6 below), with its own system prompt and per-turn schema.
- `zero` and `few` receive identical user evidence payloads (same snippet budget of 8) to avoid confounding comparisons. The `zero` user payload omits ODC-specific hints.
- The user payload separates `production_code_snippets` and `test_code_snippets`.
- The old `odc_opener_hints`/`odc_closer_hints` keyword-heuristic payload keys are REMOVED (they anchored the LLM's opener judgments and leaked ODC vocabulary into `zero-free`; see `docs/odc_alignment_audit.md` §4.4). `few`/`scientific` system prompts instead teach the ODC Impact vocabulary directly (`odc.impact_markdown()`); `zero` still gets none of it.
- When `context.fix_diff` is absent (pre-fix arm only), `bug_info` and `bug_report_description` in the payload are sanitized (`prompting.sanitize_bug_info`/`sanitize_bug_report`) to strip fix-derived content; the post-fix arm gets them untouched. `context.json` on disk is never modified.
- If `context.fix_diff` is present, the payload also includes `fix_diff_oracle` and the evidence mode becomes `post-fix`.
- Gemini uses a response JSON schema. OpenRouter and `openai-compatible` use chat completions plus post-hoc parsing.
- `dry_run=True` skips the LLM call and returns `None`.
- `odc_type` and `impact` (when present) are strictly validated against canonical names — `impact` tolerates absence (`None`) for providers that don't enforce the response schema, but rejects an out-of-vocabulary value. `few`/`scientific` require it in the schema; `zero`/`zero-free` never ask for it.
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
- `study-drift`
- `study-escape`
- `study-ladder`
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
- `study-run --manifest` and `study-drift --manifest` resolve bare filenames under `.dist/study/`.
- `study-drift` defaults `--prefix-dir`, `--postfix-dir`, `--output`, `--report` using the manifest's `target_bugs`.
- `study-escape`/`study-ladder` default `--prefix-dir` to `.dist/study/artifacts_<target_bugs>/prefix` (via `--manifest`) and read the SAME bug folders `study-run` wrote into (bug-centric layout: all conditions beside one shared `context.json`).
- Classification/report filenames are ALWAYS condition-tagged: `classification.<strategy>-<taxonomy>.json`, `report.<strategy>-<taxonomy>.md`. Checkpoints are per condition: `checkpoint.pairs.<tag>.json` (study-run) — keyed by `(artifacts_root, tag)`, NOT by manifest name (see the manifest/artifacts-root gotcha in §7). **Model is a third, orthogonal axis (added 2026-08-10):** `study-run`'s existing `--provider`/`--model` (and the same flags newly added to `study-drift`/`study-escape`) feed `odc.resolve_effective_tag` — a SECOND distinct model against the same artifacts-root+condition gets a suffixed tag (`classification.<tag>.<provider>-<model-slug>.json`, `checkpoint.pairs.<tag>.<provider>-<model-slug>.json`) instead of colliding with the first model's files; the first model, same-model resumes, and every pre-2026-08-10 checkpoint (no `model`/`provider` keys) keep the bare, untagged filenames. See `docs/condition_model.md` §5.
- `study-drift` and `compare-batch` default to the pipeline default condition (scientific-open) — pass `--taxonomy/--strategy` to analyze another condition.
- `--strategy scientific` (agent.py) runs the enforced scientific loop: each turn commits hypothesis+prediction, then either requests one evidence probe (list_evidence / full_stack_trace / snippet / coverage / bug_report — served from the FULL context.json held-back evidence; no Defects4J, no filesystem) or concludes. Max 6 turns; forced conclusion sets needs_human_review; full transcript persisted in classification.json `turns`; artifacts record `llm_calls_used` and budget accounting uses it.
- `study-run` has a budget guard: `--daily-call-budget` (default 1400; 0 disables) stops the run cleanly with a checkpoint before hitting provider daily rate limits (Gemini free ~1,500 RPD); re-running the same command resumes. Summaries record `llm_calls_made` / `budget_reached`.
- Taxonomy modes: `classify`/`run` accept `--taxonomy free|closed|open` (default `open`; `free` is only valid paired with `--strategy zero`). Open mode adds the "Other" escape label; when chosen, `classification.<tag>.json` carries mandatory `other_justification`, `nearest_type`, `other_confidence`, plus `taxonomy_mode`, and `needs_human_review` is forced true. "Other" has no family (`family_for` returns None).
- `study-export` writes LaTeX tables to `<output-dir>/latex/` and CSV files to `<output-dir>/csv/`.
- `multifault-enrich --output` defaults to `classification_enriched.json` alongside the input file.
- `study-run` installs SIGINT/SIGBREAK signal handlers for graceful Ctrl+C shutdown.
- `d4j bids` supports `--all` to include deprecated bug IDs.

### `batch.py`

Manages large-scale batch workflows.

Key responsibilities:

- Manifest generation with balanced per-project sampling (`generate_study_manifest`)
- Batch execution with paired prefix/postfix runs, one condition (`run_batch_from_manifest`) — backs `study-run`, any of the 5 valid conditions. Resolves the model-scoped `effective_tag` once at the top (`odc.resolve_effective_tag_from_root`) and uses it for every checkpoint/classification/report/prompt path — see §5.1's model-axis note.
- Signal handling: SIGINT sets a shutdown flag; checked at every loop iteration and between collect/classify steps
- Checkpoint persistence: `checkpoint.pairs.<tag>.json` (or `.<tag>.<provider>-<model-slug>.json` for a second model) written after each entry, now including `provider`/`model` fields; loaded on restart to skip completed entries
- Manifest hash: SHA-256 of sorted entry keys detects stale checkpoints from different manifests
- Progress bar: Rich progress bar showing current bug and completion count
- Cross-artifact drift analysis (`analyze_batch_artifacts`, optional `provider`/`model` params — omitted reads the bare tag, unchanged from before 2026-08-10): discovers prefix/postfix pairs, computes transition matrices, identifies divergence patterns, plus RQ1 (`type_distribution_prefix`, via `compute_type_distribution`), RQ3 (`strict_match_count/rate`, `cohens_kappa`, `per_type_metrics`, `type_confusion_matrix`), and RQ5 (`per_project_kappa`) — backs `study-drift`. These three were previously computed by standalone functions in `analysis.py`/`comparison.py` that existed and were tested but were never called from this path — `study-drift` + `study-export` silently produced empty/wrong tables (confirmed 2026-07-08 against real pilot data) until wired in here.
- Ladder discovery (`discover_ladder`): collects `classification.<tag>.json` across bug folders for an arbitrary list of condition tags in ONE prefix dir (vs `_discover_pairs`' one tag across two dirs) — feeds `compute_taxonomy_grounding_metrics` (analysis.py), backs `study-ladder`

Important behavior:

- First Ctrl+C sets a flag and prints a warning; the current bug finishes, then the loop exits.
- Second Ctrl+C raises `SystemExit(130)` for immediate termination.
- Checkpoint files use a manifest hash to detect when the manifest has changed; stale checkpoints are ignored.
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
- **API key rotation**: `<PROVIDER>_API_KEYS` (e.g. `GEMINI_API_KEYS`, comma-separated) rotates across multiple keys, taking priority over the singular `<PROVIDER>_API_KEY`. Resolved **per-request**, not per-`LLMClient` construction — a module-level `itertools.cycle`, cached by env var name (`_key_rotation_cycles`), is shared across every `LLMClient` built against that env var, so rotation advances continuously across the whole process (not per-bug, not per-turn — a single bug's `--strategy scientific` loop turns and separate bugs' single calls all draw from the same rotating pool). Only actually multiplies quota if the keys belong to separate provider accounts/projects, not multiple keys under one account.
- OpenRouter can attach `HTTP-Referer` and `X-OpenRouter-Title`
- OpenRouter currently uses the same `/chat/completions` transport path as the generic OpenAI-compatible client
- Gemini uses `generateContent` plus `responseJsonSchema`
- transient 429/500/502/503 and network errors are retried with exponential backoff — this is the ONLY rate-limit handling; there is no proactive RPM/TPM pacing (only the daily `--daily-call-budget` guard in `batch.py`)
- invalid JSON payloads and invalid `odc_type` values are **not** retried

### `prompting.py`

Encodes most of the research methodology.

Contains:

- ODC defect-type taxonomy instructions
- ODC Impact attribute instructions (`odc.impact_markdown()`; few/scientific only, never `zero`)
- 7-question diagnostic decision tree (`few` only)
- 5 few-shot examples
- evidence payload shaping, incl. pre-fix-only sanitization (`sanitize_bug_info`, `sanitize_bug_report`) and always-on noise trimming (both arms)

Important details:

- Hidden oracle metadata (`classes.modified`) is filtered out before prompt construction, for both arms.
- The pre-fix arm additionally has `bug_info`/`bug_report_description` sanitized to remove fix-derived sections (modified-sources list, fixed-revision id/date, tracker comments/status/resolution) — post-fix keeps them untouched.
- Independent of the arm: `bug_info`'s local-machine-path/corpus-size lines are stripped in both arms, `stack_trace_excerpt` is filtered through the framework blocklist, `metadata.tests.relevant` is collapsed to a count, and `notes` is never forwarded to the LLM at all (added 2026-08-10, see `docs/suspicious_frame_selection.md`).
- The old `odc_opener_hints`/`odc_closer_hints` keyword heuristics (Activity/Trigger/Impact candidates, `qualifier_hint`, `age_hint`, `source_hint` always `null`) are REMOVED — see `docs/odc_alignment_audit.md` §4.4 for why (anchoring bias, unsound heuristics, ODC-vocabulary leak into `zero-free`).
- All strategies (`zero`/`few`/`scientific`) use the same production snippet budget of 8 (no confound between evidence and prompt engineering).

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

These two families are this project's own coarse grouping for the Tier-3
family-match agreement level (`comparison.py`) — NOT a named attribute of the
IBM v5.2 document, which defines the seven types individually. Say so in any
write-up (`docs/odc_alignment_audit.md` §4.6).

Also contains:

- type summaries
- indicators
- contrastive "distinguish from" guidance
- a backward-compatible `coarse_group_for()` alias
- `ODC_IMPACTS` — the 13 v5.2 §3.3 Impact categories with verbatim-faithful definitions, plus `IMPACT_UNKNOWN` ("Unknown", per §5.1); `allowed_impact_names()`, `impact_markdown()` (the prompt section for `few`/`scientific`)
- `model_slug(provider, model)`, `resolve_effective_tag(tag, provider, model, existing_checkpoint)`, `resolve_effective_tag_from_root(artifacts_root, tag, provider, model)` — added 2026-08-10, the model-axis mechanism (see `cli.py` note above and `docs/condition_model.md` §5). Pure functions; `_from_root` is the convenience wrapper that reads the bare tag's checkpoint file for `batch.py`/`analysis.py`/`cli.py` callers.

### `models.py`

Defines the persisted dataclasses:

- `StackFrame` — `origin: str = "stack_trace"` (added 2026-08-10; `"coverage"` for frames added by `_augment_frames_with_coverage`, see `pipeline.py`/§5.1 above)
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
- `ClassificationResult.impact` — v5.2 §3.3 opener attribute, single-select, validated (see §10); current source of truth, populated by `few`/`scientific` prompts
- `ClassificationResult.inferred_activity`, `.inferred_triggers`, `.inferred_impact` — LEGACY (list-valued); populated only by pre-2026-07-10 artifacts, no longer written by prompts
- `ClassificationResult.evidence_mode`

### `parsing.py`

Parses:

- Defects4J `failing_tests` style blocks
- Java stack frames
- JSON objects embedded in raw LLM output

Important details:

- JSON extraction can recover from fenced code blocks and from responses that contain extra text before the first `{`.
- JSON extraction uses `JSONDecoder(strict=False)` (since 2026-07-11) — tolerates literal unescaped control characters (e.g. a raw newline) inside string values, which some LLM responses contain instead of properly escaping. Structural parsing (braces/commas/etc.) is unaffected. Found via a real deterministic failure (`temperature=0.0` + malformed output = identical failure on every retry, never self-resolving); regression test in `tests/test_parsing.py`.

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
- JSON parsing is attempted regardless of the declared Content-Type header (added 2026-08-10) — static-file-hosted trackers (e.g. Google Cloud Storage-served archive dumps like Closure's) routinely serve valid JSON under a generic label (`application/octet-stream`); gating strictly on `"json" in content_type` silently skipped cleanup for exactly that case
- `_format_tracker_json`/`_format_tracker_comments` (added 2026-08-10) detect the Google-Code-archive `comments[]` shape and render it as `Comment N (date): text` lines instead of the generic dotted-key flatten — decodes HTML entities/tags, drops opaque `commenterId`/`attachments` noise, keeps every comment's text. See `docs/suspicious_frame_selection.md` §2.

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
- `taxonomy_mode` — current source of truth for the taxonomy axis (`free`/`closed`/`open`)
- `strategy` — current source of truth for the strategy axis (`zero`/`few`/`scientific`)
- `prompt_style` — legacy computed alias (`odc.legacy_prompt_style`) kept for old readers; derive from `taxonomy_mode`/`strategy`, not the other way round
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
- `impact` — v5.2 §3.3 opener attribute; current source of truth (see §5.2, §10)
- `inferred_activity`, `inferred_triggers`, `inferred_impact` — legacy, pre-2026-07-10 artifacts only
- `evidence_mode`
- `raw_response`
- `other_justification`, `nearest_type`, `other_confidence` — present when `odc_type == "Other"` (`--taxonomy open` escape; see §5.2/§11)
- `consistency_k`, `consistency_confidence`, `sample_labels` — present when `--self-consistency k>1` (majority-vote metadata; see §5.2)
- `turns`, `llm_calls_used` — present for `--strategy scientific`: `turns` is the full hypothesis/prediction/probe/observation transcript, `llm_calls_used` is the call count the budget guard accounts against

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
- fix knowledge (the modified-sources oracle, tracker fix-era content) should not enter the pre-fix prompt through ANY channel — not just `classes.modified` (see `docs/odc_alignment_audit.md`)
- classification should use scientific-debugging-style reasoning by default
- the mandatory label is still the 7-class ODC `Defect Type`
- `Impact` (v5.2 §3.3) is the one opener attribute claimed and validated; Activity/Trigger are documented as not reliably determinable from Defects4J evidence rather than guessed at
- evaluation distinguishes exact type vs alternative-type overlap vs family-level agreement, plus an Impact-based drift negative control (fix-independent, so its prefix/postfix disagreement estimates pure instrument noise)

`odc_doc.md` is the underlying ODC reference; `docs/odc_alignment_audit.md` is the alignment audit against it — read before touching anything ODC-attribute-related.

What the implementation currently does with ODC attributes:

- `Defect Type`: mandatory; predicted pre-fix, read from the fix diff post-fix
- `Impact`: claimed opener attribute — single-select from 13 v5.2 categories + `Unknown`, taught in-prompt (`few`/`scientific`), strictly validated
- `Target`: effectively fixed to `Design/Code` (stated scoping assumption, not inferred)
- `Qualifier`: optional, determined from the fix diff (post-fix)
- `Age`, `Source`: not claimed — Age needs VCS archaeology outside current evidence; Source is ≈constant (all projects single-org OSS). See `docs/odc_alignment_audit.md` §3 for the full attribute-by-attribute rationale.
- `Activity`, `Trigger`: not claimed — Defects4J's evidence doesn't match what ODC's field-defect procedure requires (§3.1.6); the old keyword heuristics that guessed at them are removed

`thesis_plan.md` is background context, not executable policy.

## 11. Known Drift, Caveats, and Traps

These are the main places future agents get misled:

1. `README.md` still describes retrying invalid classifications, but the code only retries transient HTTP/network failures in `llm._urlopen_json()`.
2. `cli.main()` catches `Defects4JError`, `FileNotFoundError`, and `ValueError`, but it does **not** catch `LLMError`, so auth/network/provider failures may currently bubble out as uncaught exceptions.
3. `family` in `classification.json` is not trusted from the model; it is always overwritten with `odc.family_for(odc_type)`.
4. `odc_type` and `impact` are validated against canonical labels (`impact` tolerates absence but not an out-of-vocabulary value). Other optional ODC fields like `qualifier`, `age`, `source` are stored with only minimal trimming; the legacy `inferred_*` opener fields are read-only compatibility fields, no longer written.
5. The `odc_opener_hints`/`odc_closer_hints` keyword-heuristic payload keys described in older docs/artifacts no longer exist — they were removed (`docs/odc_alignment_audit.md` §4.4). If you see them in an artifact, it predates 2026-07-10.
6. Pre-fix sanitization (`sanitize_bug_info`/`sanitize_bug_report`) is applied only when `context.fix_diff` is falsy — it runs identically for `zero`/`few`/`scientific` (including the agent's `bug_report` probe), so don't assume it's a `few`/`scientific`-only concern when editing `agent.py`.
7. `fix_diff` is a string field on `BugContext`; when not requested or unavailable it is usually `""`, not absent.
8. `tests/test_url_fetch.py` is not a normal unit test file. It is a live integration script with top-level network calls and print statements.
9. Full `pytest` runs may import `tests/test_url_fetch.py` and trigger network access. In restricted or offline environments, avoid that unless you explicitly want it.
10. `compare-batch` only finds pairs when directory names line up after stripping optional `_prefix` and `_postfix` suffixes.
11. Folder names in `work/` and `artifacts/` are not reliable indicators of buggy/fixed or pre-fix/post-fix status. Trust JSON fields and Defects4J config files instead.
12. Coverage parsing is best-effort. Even after a coverage command runs, parsed coverage may still be empty.
13. **Scientific debugging has two valid orderings — do not mix them.** Process level (Zeller, *Why Programs Fail*, Ch. 6; the single-shot prompt): Observe → Hypothesize → Predict → Experiment/Examine → Conclude — the failure is observed first, and `prompting.py::_scientific_debugging_instructions` is the reference. Loop-iteration level (AutoSD, Kang et al. EMSE 2024, Fig. 1): the failure observation is the *prompt input*, and each iteration runs Hypothesis → Prediction → Experiment → Observation (the experiment's result) → Conclusion. The historical error to avoid propagating: "Hypothesize, Observe, Predict, Examine, Conclude" (initial symptom examination placed *after* hypothesizing) — that matches neither source.
14. **`iut_submissions/` is FROZEN** — pre-defense deliverables exactly as submitted. Never edit anything under it. Its `report/main.tex` (~lines 332, 351-352) contains the wrong step order described above; this is a known, deliberately preserved historical error. Do not fix it in place and do not copy wording from it into new material.
15. **`.dist/` is NOT uniformly gitignored, and the gitignore rule is narrower than the folder names suggest.** `artifacts/` (`.gitignore:41`) matches only a directory literally named `artifacts` — it does NOT match `artifacts_200` or `artifacts_full`. `.dist/study/artifacts/` (unnumbered) is the **committed preliminary dataset** — ~35 prefix bug folders with old untagged filenames, kept via a `.gitignore` negation (`!.dist/study/artifacts/**`); it backs the pre-defense results (73.5% strict / 94.1% top-2 / 97.1% family on 34 pairs). Treat like `iut_submissions/`: never delete, never rerun into it, never rename its files to the tagged scheme. `.dist/study/artifacts_full/` (854+854 pre-collected `context.json`, ~114MB) is ALSO fully git-tracked — deliberately, since `context.json` is the pipeline's biggest bottleneck to regenerate — but its classification/report/checkpoint/summary artifacts are NOT tracked yet by policy (cheap to regenerate; revisit once a full-scale study run exists, not just the 6-bug pilot). Changing what's tracked there is a team judgment call, not an autonomous `.gitignore` fix. `.dist/study/artifacts_200/` is an abandoned early smoke test, legacy. Several `.dist/runs/` bug folders are also git-tracked. Actually regenerable/ignored: `.dist/test_tmp_batch/` (pytest debris — delete anytime), `work/` and `.dist/study/work/` checkouts.
16. **A manifest is a worklist, not a namespace.** `--artifacts-root` decides *where* output goes; `--manifest` only decides *which bugs this run touches*. Two manifests pointed at the same `--artifacts-root` under the same condition read/write the exact same per-bug files when their bug keys overlap — intentional, since it's what lets every manifest reuse one shared context store (e.g. `manifest_pilot.json`'s 6 bugs are a subset of `artifacts_full`'s 854). The one place manifest identity matters: `checkpoint.{pairs|prefix}.<tag>.json` is keyed by `(artifacts_root, tag)` only, NOT by manifest name — switching manifests under the same root+tag resets resume state ("checkpoint manifest hash mismatch — starting fresh"), though it does not reprocess or destroy already-written classification files (those are separately protected by a file-existence skip-check). Also: `study-run`'s `summary.json` is the only study artifact that is NOT condition-tagged (unlike `classify_summary.<tag>.json`/`checkpoint.*.<tag>.json`/`classification.<tag>.json`) — a second `study-run` under a different condition silently overwrites it.

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
python -m d4j_odc_pipeline study-drift --manifest manifest_68.json
python -m d4j_odc_pipeline study-run --manifest manifest_68.json --taxonomy free --strategy zero --skip-coverage
python -m d4j_odc_pipeline study-escape --manifest manifest_68.json --strategy scientific
python -m d4j_odc_pipeline study-ladder --manifest manifest_68.json --tags zero-free,few-open,scientific-open
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

- read `docs/odc_alignment_audit.md` first — it has the current per-attribute determinability rationale (what's claimed, constant, or not determinable, and why); don't reintroduce a keyword-heuristic "candidates" payload key (that pattern was removed for anchoring the LLM's judgment)
- for a new/changed claimed attribute (like `impact`): teach its vocabulary in-prompt (`odc.py` markdown builder, e.g. `impact_markdown()`), add it to `few`/`scientific` prompts only (never `zero`), thread it through `llm.py` (schema), `models.py` (field), `pipeline.py` (`_validate_classification_payload`), `analysis.py`/`comparison.py` if it feeds an RQ, tests, and docs
- decide whether the new signal is opener (fix-independent — a candidate for the impact-style drift negative control) or closer (fix-defined — a candidate for pre-fix prediction like Defect Type)

To improve evaluation:

- start in `comparison.py`
- preserve compatibility with old `coarse_group` outputs unless you intentionally migrate stored artifacts

## 15. Bottom Line

For implementation work, start with `pipeline.py`, then follow the call chain into `prompting.py`, `models.py`, `llm.py`, `defects4j.py`, and `comparison.py`.

For methodology or RQ questions, start at `docs/JSS_HANDOFF.md` — it points to the current methodology docs and explicitly flags which ones (including `docs/METHODOLOGY.md`) are stale and why. Otherwise: `odc.py`, `docs/odc_doc.md`, `docs/odc_alignment_audit.md`, and the scientific-debugging instructions in `prompting.py`.

For filesystem/output questions, trust current dataclasses and writers over historical artifact examples.

For any work touching the new ODC opener/closer architecture, trace the full path:

`prompting.py` -> `llm.py` -> `pipeline.py` -> `models.py` -> `comparison.py` -> `tests/`

For analysis/export work, trace: `analysis.py` -> `results_export.py` -> `cli.py` -> `interactive/handlers.py`
