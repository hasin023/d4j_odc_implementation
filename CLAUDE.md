# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A research pipeline that collects pre-fix bug evidence from Defects4J, classifies it into one of 7 ODC (Orthogonal Defect Classification) defect types via an LLM, and writes machine-readable outputs for large-scale evaluation. It backs a thesis; much of the repo is generated experiment state, not source.

**`AGENTS.md` is the authoritative, detailed working map** (module guide, execution flows, artifact schemas, extension patterns). Read it before non-trivial changes. This file is the quick orientation; `AGENTS.md` and `docs/` are the depth.

**`docs/study_execution_log.md` is the running record of actual classification runs** (commands, environment, result matrices, findings). Read it before running or analyzing any study; append a section after every run.

Source-of-truth order when docs conflict: `d4j_odc_pipeline/*.py` → `tests/*.py` → `AGENTS.md` → `README.md` → `docs/`. Files under `artifacts/` span multiple schema generations and are **not** the current contract.

## Commands

Activate the venv once per shell (`source .venv/bin/activate`); then `python`/`pytest` resolve normally. (Without it they're not on PATH — use `.venv/bin/python` for a one-off command.)

```bash
# Install (editable)
pip install -r requirements.txt && pip install -e .

# Run the CLI — no args launches the interactive `odc>` REPL; any command = script mode
d4j-odc                              # or: python -m d4j_odc_pipeline
python -m d4j_odc_pipeline run --project Lang --bug 1 --skip-coverage

# Tests
pytest                               # all
pytest tests/test_batch.py           # one file
pytest tests/test_batch.py::test_name # one test
pytest -k pattern                    # by name pattern
```

There is no configured linter/formatter/type-checker; `pyproject.toml` only defines the `d4j-odc` script and pytest's `testpaths`. Requires Python >= 3.11.

Note: the two `tests/test_defects4j.py` path-conversion tests assert Windows→WSL behavior and only pass on a Windows+WSL host; they fail on native Linux and are not a regression.

## Environment

Runtime config comes from `.env` (copy `.env.example`). Two things must be set for real runs:
- **`DEFECTS4J_CMD`** — how to invoke the Defects4J binary (e.g. `wsl perl /home/user/defects4j/framework/bin/defects4j`). `DEFECTS4J_PATH_STYLE=wsl` when the clone lives inside WSL.
- **An LLM provider key** — `DEFAULT_LLM_PROVIDER` selects `gemini | openrouter | groq | openai-compatible`; each provider has its own `*_API_KEY` / `*_BASE_URL` / `*_MODEL` block.

Use `/doctor` in the REPL to validate Defects4J, keys, and Python before running.

## Architecture (big picture)

The system is **file-oriented and synchronous** — no database, queue, or async. The filesystem *is* the contract between stages; each stage reads/writes JSON artifacts.

Core evidence flow (see `pipeline.py`):
```
collect:  Defects4J checkout/test/coverage  ->  context.json
classify: context.json -> prompt -> LLM     ->  classification.json (+ report.md)
run:      collect + classify in one shot
```

Two evidence modes matter methodologically:
- **pre-fix** (default) — realistic classification from buggy code + failing tests only.
- **post-fix** — only when `--include-fix-diff` is passed; injects the real buggy→fixed diff as oracle info. The prefix/postfix pairing is the basis of the evaluation.

Every classification is a coordinate of **two condition variables** (constructed in `prompting.py`, constants in `odc.py`):
- `--taxonomy free|closed|open` (default **open**): free = answer in own words (no taxonomy); closed = the 7 ODC types forced; open = 7 + "Other" escape category (RQ2 instrument).
- `--reasoning zero|scientific` (default **scientific**; `agentic` reserved for Phase 2): enforcement depth of the scientific method — absent → narrated (protocol + diagnostic tree + few-shot examples).

Retired preset names map as: naive = free×zero, direct = closed×zero, scientific = closed×scientific. `--prompt-style` and the `study-baseline`/`study-naive`/`study-coverage` commands are tombstoned (they print the new invocation and exit). Filenames are always condition-tagged — `classification.<taxonomy>-<reasoning>.json`, `report.<tag>.md` — written into the same bug folder beside the shared, read-only `context.json`.

## Methodology invariants (do not violate)

- **Scientific debugging has TWO valid orderings — never mix them.** "Observe" is ambiguous between them; be explicit about which level you mean:
  - **Process level** (Zeller, *Why Programs Fail*, Ch. 6; used by the single-shot prompt): **Observe → Hypothesize → Predict → Experiment/Examine → Conclude**. The failure is observed FIRST; hypotheses must be consistent with prior observations. `prompting.py::_scientific_debugging_instructions` is the reference implementation.
  - **Loop-iteration level** (AutoSD, Kang et al. EMSE 2024, Fig. 1): the initial failure observation (failing test + error message + code) is the *prompt input*; each iteration then runs **Hypothesis → Prediction → Experiment → Observation (experiment result) → Conclusion**.
  - The historical error to avoid: "Hypothesize, Observe, Predict, Examine, Conclude" — where "Observe" means examining failure symptoms *after* hypothesizing. That matches **neither** source and must not be propagated.
- **`iut_submissions/` is FROZEN** — it holds the pre-defense deliverables exactly as submitted. Never edit, reformat, or "fix" anything under it. Known issue kept for the record: `report/main.tex` lines ~332 and ~351-352 contain the wrong hybrid ordering (initial failure-symptom examination placed *after* hypothesizing — see the two-orderings rule above; this is NOT the same as AutoSD's loop-level hypothesize-first, which is valid). Do not propagate that ordering into new documents or code; do not fix it in place.

The batch/study layer (`batch.py`) scales this to a manifest of bugs with checkpoint/resume and graceful Ctrl+C: `study-plan` (balanced manifest) → `study-run` (paired prefix/postfix runs of one condition) → `study-classify` (any single condition, prefix-only, reusing existing contexts; auto-computes RQ2 coverage metrics `taxonomy_coverage_<N>.json` when running open with a closed pass present) → `study-analyze` (cross-artifact stats, `analysis.py`; defaults to closed-scientific, the paired baseline condition) → `study-export` (LaTeX + CSV, `results_export.py`). Checkpoints are per condition (`checkpoint.pairs.<tag>.json` / `checkpoint.prefix.<tag>.json`). `comparison.py` computes agreement metrics incl. per-project Cohen's Kappa.

Module map:
- `cli.py` — argparse dispatch for script mode; entrypoint.
- `interactive/` — the `odc>` REPL: `handlers.py` (command logic), `commands.py` (registry), `completer.py`, `session.py` (persisted session state). Slash commands (`/run`) mirror script commands (`run`).
- `defects4j.py` — Defects4J wrapper: query/export, coverage parsing, WSL path translation.
- `llm.py` — provider abstraction (Gemini / OpenRouter / Groq / OpenAI-compatible).
- `odc.py` — canonical 7-type taxonomy + family mapping. `models.py` — dataclasses for persisted artifacts. `parsing.py` — stack-trace + JSON parsing. `multifault.py` — defects4j-mf co-existence data. `web_fetch.py` — bug-report fetcher. `console.py` — Rich output.

## Output layout

- `.dist/runs/<Project>_<bug>_<prefix|postfix>/` — standalone `run`/`collect`/`classify` outputs.
- `.dist/study/` — batch outputs: `manifest_<N>.json`, `artifacts_<N>/{prefix,postfix}/`, `baseline_<N>/`, `naive_<N>/`, `checkpoint.json`, `latex/`, `csv/` (N = target bug count).
- `work/` — standalone Defects4J checkouts; `.dist/study/work/` — batch checkouts.

`work/`, root `artifacts/`, `logs/`, and `.env` are gitignored. **`.dist/` is NOT uniformly gitignored** — two areas are deliberately committed:
- `.dist/runs/` — standalone outputs; several bug folders are tracked in git.
- **`.dist/study/artifacts/` (unnumbered) is the committed preliminary dataset** (~35 prefix bugs, old untagged filenames) backing the pre-defense results (73.5% strict match etc.), kept via a `.gitignore` negation. Treat it like `iut_submissions/`: historical record — never delete, never rerun into it, never "migrate" it to the tagged naming.

Regenerable/ignored: `.dist/study/artifacts_<N>/` (per-manifest study trees), `.dist/test_tmp_batch/` (pytest debris, delete freely), `work/` checkouts.
