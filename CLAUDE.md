# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

A research pipeline that collects pre-fix bug evidence from [Defects4J](https://github.com/rjust/defects4j), classifies bugs into [ODC (Orthogonal Defect Classification)](https://www.research.ibm.com/haifa/projects/odc/index.shtml) defect types using an LLM, and saves machine-readable outputs for evaluation. The goal is to answer 4 research questions about pre-fix ODC classification accuracy.

A second sub-thesis ("Can an LLM Write the Missing Test?") extends the pipeline to automatically generate JUnit 4 regression tests from pre-fix `context.json` artifacts and evaluate them against the Defects4J ground-truth trigger tests.

## Commands

```bash
# Install
pip install -r requirements.txt
pip install -e .

# Launch interactive REPL (primary interface)
d4j-odc

# Script mode — ODC classification pipeline
python -m d4j_odc_pipeline run --project Lang --bug 1
python -m d4j_odc_pipeline study-plan --target-bugs 68
python -m d4j_odc_pipeline study-run --manifest manifest_68.json
python -m d4j_odc_pipeline study-analyze --manifest manifest_68.json

# Script mode — Test generation sub-thesis
# 0. Collect fixed (postfix) version — needed for oracle evaluation
python -m d4j_odc_pipeline collect --project Lang --bug 1 --postfix --skip-coverage

# 1. Generate a test from a single prefix context.json (work_dirs must be on disk)
python -m d4j_odc_pipeline test-gen \
  --prefix-context .dist/runs/Lang_1_prefix/context.json \
  --postfix-context .dist/runs/Lang_1_postfix/context.json \
  --prompt-style full

# 1a. With self-correction loop (up to 3 refinement iterations)
python -m d4j_odc_pipeline test-gen \
  --prefix-context .dist/runs/Lang_1_prefix/context.json \
  --postfix-context .dist/runs/Lang_1_postfix/context.json \
  --prompt-style full --refine --max-refine-iterations 3

# 1b. Dry-run — render prompt only, no LLM call (saves prompt.json)
python -m d4j_odc_pipeline test-gen \
  --prefix-context .dist/runs/Lang_1_prefix/context.json \
  --prompt-style full --dry-run

# 2. Batch generate over an entire study artifacts directory
python -m d4j_odc_pipeline test-gen-batch \
  --artifacts-dir .dist/study/artifacts_68/ \
  --prompt-style full --refine

# 3. Aggregate metrics and export report + CSV
python -m d4j_odc_pipeline test-gen-analyze \
  --results-dir .dist/test_gen/baseline/ \
  --export-csv

# Defects4J raw commands (used internally; useful for debugging / manual steps)
# Re-checkout buggy version if work_dir was cleaned up:
#   defects4j checkout -p Lang -v 1b -w work/Lang_1_prefix
# Re-checkout fixed version:
#   defects4j checkout -p Lang -v 1f -w work/Lang_1_postfix
# Inspect trigger tests for a checked-out bug:
#   defects4j export -p tests.trigger  (run inside work_dir)
# Run only the developer-written trigger tests:
#   defects4j test -r  (run inside work_dir)

# Tests
pytest tests/
pytest tests/test_batch.py          # single module
pytest tests/ -k test_name          # single test
```

## Configuration

Copy `.env.example` to `.env` and set:
- `GEMINI_API_KEY` or `OPENROUTER_API_KEY`
- `DEFECTS4J_CMD` — typically `wsl perl /path/to/defects4j/framework/bin/defects4j` on Windows+WSL
- `D4J_WORK_DIR` — temp checkout directory (defaults to `./work`)
- `D4J_OUTPUT_DIR` — results root (defaults to `./.dist`)

## Architecture

The pipeline has three phases, each producing a JSON artifact:

1. **Collection** (`collect`) — checks out the buggy revision, runs tests, extracts stack traces and code snippets. Produces `context.json`.
2. **Classification** (`classify`) — sends evidence to an LLM using one of three prompt strategies (scientific / direct / naive). Produces `classification.json`.
3. **Evaluation** (`compare`, `study-*`) — compares pre-fix and post-fix classifications using 4-tier accuracy metrics (strict match → top-2 → family → Cohen's Kappa). Produces `analysis_*.json` and LaTeX/CSV exports.

### Sub-thesis: Test Generation

4. **Test Generation** (`test-gen`, `test-gen-batch`, `test-gen-analyze`) — takes a pre-fix `context.json` (LLM sees only buggy evidence), generates a JUnit 4 test via LLM, then validates it against both the buggy and fixed checkouts using `defects4j compile` + `defects4j test`. Compares to the Defects4J ground-truth trigger test (read from the checked-out work_dir). Produces `test_gen_result.json`.

**Critical dependency**: `test-gen` requires the `work_dir` embedded in `context.json` to still exist on disk. If it has been deleted, re-checkout both versions first:
```bash
defects4j checkout -p <Project> -v <bug>b -w <prefix_work_dir>
defects4j checkout -p <Project> -v <bug>f -w <postfix_work_dir>
```

**Accuracy metrics** produced by the test-gen pipeline:
- `compilation_rate` — fraction of generated tests that compile
- `fault_detection_rate` — of compiled tests, fraction that fail on the buggy version
- `oracle_pass_rate` — fraction that fail on buggy AND pass on fixed (the "oracle" criterion)
- `method_name_match_rate` — generated method name overlaps the actual trigger test method name
- `class_targeting_rate` — generated test references the modified class
- `refinement_used_rate` — fraction of bugs where `--refine` triggered at least one iteration
- `refined_fault_kept_rate` — of refined bugs, fraction that still fail on buggy after refinement (no regression)
- `refined_oracle_match_rate` — of refined bugs, fraction that achieved oracle_match through refinement

**Refinement failure modes** handled by `--refine`:
1. `compile_failed` — compilation error; LLM receives the compiler message and is asked to fix it
2. `passed_on_buggy` — test passes on buggy version; LLM is asked to probe the defect more precisely
3. `oracle_fail` — test fails on both buggy and fixed; LLM is asked to correct the expected value (requires `--postfix-context`)

## Key Modules

| File | Responsibility |
|------|---------------|
| `cli.py` | Command dispatcher — routes both interactive and script invocations |
| `pipeline.py` | Orchestrates collection and classification for a single bug |
| `batch.py` | Batch workflows: manifest generation, checkpoint/resume, study-run |
| `defects4j.py` | Wraps the Defects4J CLI; handles WSL path translation on Windows |
| `llm.py` | Single `LLMClient` supporting Gemini, OpenRouter, OpenAI-compatible APIs |
| `prompting.py` | Prompt construction — scientific protocol, few-shots, evidence normalization |
| `odc.py` | ODC taxonomy source-of-truth (7 types, families, decision tree) |
| `comparison.py` | Pre/post-fix comparison and semantic distance metrics |
| `analysis.py` | Statistical analysis for RQ1–RQ4 (chi-squared, per-type precision/recall) |
| `interactive/` | REPL shell with slash commands, tab completion, session persistence |
| `test_gen.py` | Sub-thesis: oracle-clean prompt construction, `_strip_trigger_methods`, `_run_postfix_attempt`, self-correction loop (`refine_test_generation`) with `compile_failed`/`passed_on_buggy`/`oracle_fail` modes |
| `test_gen_analysis.py` | Sub-thesis: batch metrics aggregation (compilation, fault detection, oracle, refinement), per-project/per-style breakdown, markdown report, CSV export |

## Design Invariants

- **File-oriented, synchronous**: no database or async orchestration; state lives in JSON checkpoints.
- **Hidden oracle**: `classes.modified` and other post-fix identifiers are stored in `context.json` but excluded from LLM prompts (guarded by `hidden: true` in the payload builder in `prompting.py`).
- **Evidence parity**: all three prompt strategies receive the same evidence payload so only the prompting methodology varies.
- **Suspicious frame filtering**: stack frames from JDK/framework/test-runner packages are excluded; source frames are capped at 12, prioritizing project source packages.

## Output Layout

```
.dist/
├── runs/                    # Standalone run outputs
│   ├── Lang_1_prefix/
│   │   ├── context.json     # includes test_class_sources (trigger class raw Java, bodies stripped at prompt time)
│   │   ├── classification.json
│   │   └── report.md
│   └── Lang_1_postfix/      # fixed version; collected with: collect --postfix
├── study/                   # Batch study outputs
│   ├── manifest_68.json
│   ├── analysis_68.json / analysis_68.md
│   ├── artifacts_68/        # per-bug prefix+postfix pairs
│   ├── baseline_68/         # direct-prompt baseline results
│   └── latex/ + csv/        # export for paper tables
└── test_gen/                # Sub-thesis: test generation outputs
    ├── baseline/            # --prompt-style full, no --refine
    │   ├── Lang_1/
    │   │   ├── test_gen_result.json
    │   │   ├── generated_test.java
    │   │   └── test_gen_report.md
    │   └── aggregate/
    └── refined/             # --prompt-style full --refine
        ├── Lang_1/
        │   ├── test_gen_result.json   # includes refine_iterations + refine_history
        │   ├── generated_test.java
        │   └── test_gen_report.md
        └── aggregate/
            ├── test_gen_analysis.json
            ├── test_gen_summary.md
            └── test_gen_results.csv
```

## Additional Documentation

- `AGENTS.md` — module-by-module codebase map and execution flows (authoritative)
- `RESEARCH_AGENTS.md` — research methodology deep-dive, RQ definitions, evaluation framework
- `docs/ARCHITECTURE.md` — pipeline flows, ODC taxonomy, JSON schemas
- `docs/USAGE.md` — full CLI reference with parameter tables
- `docs/METHODOLOGY.md` — research questions and evaluation criteria
