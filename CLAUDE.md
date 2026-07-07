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

**`docs/condition_model.md` is the single authoritative spec for classification conditions** — read it before touching prompting/CLI/batch. Summary: every classification is a coordinate of two variables:
- `--taxonomy free|closed|open` (default **open**): free = own words; closed = the 7 ODC types forced; open = 7 + "Other" escape category. Open is the default per the supervisor's position: never force-fit bugs into a fixed schema; escapes are data.
- `--strategy zero|few|scientific` (default **scientific**): zero = zero-shot, taxonomy-free by definition (only valid with free); few = few-shot single call (taxonomy + diagnostic tree + worked examples — the strong static prompt); scientific = the ENFORCED loop (`agent.py`: hypothesis→prediction→probe→observation over held-back context.json evidence, max 6 turns, transcript in the artifact).

Only 5 conditions are valid: free-zero, closed-few, open-few, closed-scientific, open-scientific (CLI-enforced). The old narrated single-shot "scientific" condition was retired 2026-07-07 (pilot: narration changed 0/6 labels; enforcement 2/6, both toward the oracle) — its prompt content lives on as `few`. Tombstoned (print redirect + exit): `--prompt-style`, `--reasoning`, `study-baseline`/`study-naive`/`study-coverage`. Filenames are always condition-tagged — `classification.<taxonomy>-<strategy>.json` — beside the shared read-only `context.json`. ⚠️ Artifacts written before 2026-07-07 use old `reasoning` tokens with different semantics; do not mix (see study_execution_log.md).

## Methodology invariants (do not violate)

- **Scientific debugging has TWO valid orderings — never mix them.** "Observe" is ambiguous between them; be explicit about which level you mean:
  - **Process level** (Zeller, *Why Programs Fail*, Ch. 6; used by the single-shot prompt): **Observe → Hypothesize → Predict → Experiment/Examine → Conclude**. The failure is observed FIRST; hypotheses must be consistent with prior observations. `prompting.py::_scientific_debugging_instructions` is the reference implementation.
  - **Loop-iteration level** (AutoSD, Kang et al. EMSE 2024, Fig. 1): the initial failure observation (failing test + error message + code) is the *prompt input*; each iteration then runs **Hypothesis → Prediction → Experiment → Observation (experiment result) → Conclusion**.
  - The historical error to avoid: "Hypothesize, Observe, Predict, Examine, Conclude" — where "Observe" means examining failure symptoms *after* hypothesizing. That matches **neither** source and must not be propagated.
- **`iut_submissions/` is FROZEN** — it holds the pre-defense deliverables exactly as submitted. Never edit, reformat, or "fix" anything under it. Known issue kept for the record: `report/main.tex` lines ~332 and ~351-352 contain the wrong hybrid ordering (initial failure-symptom examination placed *after* hypothesizing — see the two-orderings rule above; this is NOT the same as AutoSD's loop-level hypothesize-first, which is valid). Do not propagate that ordering into new documents or code; do not fix it in place.

The batch/study layer (`batch.py`) scales this to a manifest of bugs with checkpoint/resume and graceful Ctrl+C: `study-plan` (balanced manifest) → `study-run` (paired prefix/postfix runs of one condition) → `study-classify` (any single condition, prefix-only, reusing existing contexts; auto-computes RQ2 coverage metrics `taxonomy_coverage_<N>.json` when running open with a closed pass present) → `study-analyze` (cross-artifact stats, `analysis.py`; defaults to the pipeline default condition, open-scientific) → `study-export` (LaTeX + CSV, `results_export.py`). Checkpoints are per condition (`checkpoint.pairs.<tag>.json` / `checkpoint.prefix.<tag>.json`). `comparison.py` computes agreement metrics incl. per-project Cohen's Kappa.

Module map:
- `cli.py` — argparse dispatch for script mode; entrypoint.
- `interactive/` — the `odc>` REPL: `handlers.py` (command logic), `commands.py` (registry), `completer.py`, `session.py` (persisted session state). Slash commands (`/run`) mirror script commands (`run`).
- `defects4j.py` — Defects4J wrapper: query/export, coverage parsing, WSL path translation.
- `llm.py` — provider abstraction (Gemini / OpenRouter / Groq / OpenAI-compatible).
- `odc.py` — canonical 7-type taxonomy + family mapping. `models.py` — dataclasses for persisted artifacts. `parsing.py` — stack-trace + JSON parsing. `multifault.py` — defects4j-mf co-existence data. `web_fetch.py` — bug-report fetcher. `console.py` — Rich output.

## Output layout

- `.dist/runs/<Project>_<bug>_<prefix|postfix>/` — standalone `run`/`collect`/`classify` outputs.
- `.dist/study/` — batch outputs: `manifest_<N>.json` (or hand-authored, e.g. `manifest_pilot.json`), `artifacts_<N>/{prefix,postfix}/` (all conditions live as tagged files in the SAME bug folders, beside one shared `context.json`), `checkpoint.{pairs|prefix}.<tag>.json`, `summary.json` (study-run — see gotcha below), `classify_summary.<tag>.json` (study-classify), `taxonomy_coverage_<N>.json` (auto RQ2), `analysis_<N>.{json,md}`, `latex/`, `csv/` (N = target bug count).
- **`.dist/study/artifacts_full/`** — a manually-named `--artifacts-root` override, NOT the `artifacts_<N>` auto-naming convention. Holds the pre-collected 854 prefix + 854 postfix `context.json` corpus (added 2026-07-06, ~1 week to collect). Every study command should point `--artifacts-root` here so any manifest/condition reuses one context store instead of re-collecting.
- `work/` — standalone Defects4J checkouts; `.dist/study/work/` — batch checkouts.

`work/`, root `artifacts/`, `logs/`, and `.env` are gitignored. **`.dist/` is NOT uniformly gitignored, and the gitignore rule is narrower than the folder names suggest**: `artifacts/` (`.gitignore:41`) matches only a directory literally named `artifacts` — it does NOT match `artifacts_200` or `artifacts_full`.
- `.dist/runs/` — standalone outputs; several bug folders are tracked in git.
- **`.dist/study/artifacts/` (unnumbered) is the committed preliminary dataset** (~35 prefix bugs, old untagged filenames) backing the pre-defense results (73.5% strict match etc.), kept via a `.gitignore` negation. Treat it like `iut_submissions/`: historical record — never delete, never rerun into it, never "migrate" it to the tagged naming.
- **`.dist/study/artifacts_full/` is fully git-tracked too** (1,772 files, ~114MB) — the bare `artifacts/` rule never matches it, so nothing inside it is actually ignored. This is a deliberate, standing policy, not an oversight to silently patch: `context.json` is tracked everywhere because it's the pipeline's biggest bottleneck to regenerate; `classification.*.json`/`report.*.md`/checkpoints/summaries inside it are NOT tracked yet (cheap to regenerate; the line will be revisited once a full-scale study run — not just the 6-bug pilot — exists). Changing what's tracked here is a judgment call for the team, not an autonomous `.gitignore` fix.
- `.dist/study/artifacts_200/` — an abandoned early smoke test (`manifest_200.json`, 2 bugs, pre-redesign untagged naming) — legacy, not part of any active study.

Actually regenerable/ignored: `.dist/test_tmp_batch/` (pytest debris, delete freely), `work/` checkouts (both `work/` and `.dist/study/work/`).

**Gotcha — a manifest is a worklist, not a namespace.** `--artifacts-root` decides *where* output goes; `--manifest` only decides *which bugs this run touches*. Two manifests pointed at the same `--artifacts-root` under the same condition read/write the exact same per-bug files if their bug keys overlap — intentional, since it's what lets every manifest reuse one shared context store. The one place manifest identity matters: `checkpoint.{pairs|prefix}.<tag>.json` is keyed by `(artifacts_root, tag)` only, **not** by manifest name, so switching manifests under the same root+tag resets resume state ("checkpoint manifest hash mismatch — starting fresh"). This does not reprocess or destroy already-written classification files — those are separately protected by a file-existence skip-check.

**Gotcha — `summary.json` (from `study-run`) is the only study artifact that isn't condition-tagged.** Everything else (`classify_summary.<tag>.json`, `checkpoint.*.<tag>.json`, `classification.<tag>.json`) carries its condition in the filename; a second `study-run` under a different condition silently overwrites the first run's `summary.json`.
