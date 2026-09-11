# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A research pipeline that collects pre-fix bug evidence from Defects4J, classifies it into one of 7 ODC (Orthogonal Defect Classification) defect types via an LLM, and writes machine-readable outputs for large-scale evaluation. It backs a thesis; much of the repo is generated experiment state, not source.

**`AGENTS.md` is the authoritative, detailed working map** (module guide, execution flows, artifact schemas, extension patterns). Read it before non-trivial changes. This file is the quick orientation; `AGENTS.md` and `docs/` are the depth.

**Drafting the JSS paper or need the RQ results? Start at `docs/JSS_HANDOFF.md`, not here.** It's the single current entry point for Pipeline / Analysis / RQs / RQ results, with explicit pointers to which other docs are current vs stale — read it before opening anything else under `docs/`.

**Running this as a team, or handing work to a teammate? Read `docs/TEAM_WORKFLOW.md`.** It has the
three roles (collect / classify / report), the exact commands each runs, how `context.json` moves
between machines, and an ACTIVE/STALE verdict on every directory under `.dist/`.

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
- **An LLM provider key** — `DEFAULT_LLM_PROVIDER` selects `gemini | openrouter | groq | openai-compatible`; each provider has its own `*_API_KEY` / `*_BASE_URL` / `*_MODEL` block. Optional: `*_API_KEYS` (plural, comma-separated, e.g. `GEMINI_API_KEYS`) rotates across multiple keys per-request to spread RPM/RPD load — see `llm.py`'s `_resolve_api_keys`/`_get_key_cycle`.

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
- `--strategy zero|few|scientific` (default **scientific**): zero = zero-shot, taxonomy-free by definition (only valid with free); few = few-shot single call (taxonomy + diagnostic tree + worked examples — the strong static prompt); scientific = the ENFORCED loop (`agent.py`: hypothesis→prediction→probe→observation over held-back context.json evidence, max 6 turns, transcript in the artifact incl. each probe's actual return payload, truncated to 2000 chars).

Only 5 conditions are valid: zero-free, few-closed, few-open, scientific-closed, scientific-open (CLI-enforced). The old narrated single-shot "scientific" condition was retired 2026-07-07 (pilot: narration changed 0/6 labels; enforcement 2/6, both toward the oracle) — its prompt content lives on as `few`. Tombstoned (print redirect + exit): `--prompt-style`, `--reasoning`, `study-baseline`/`study-naive`/`study-coverage`. Filenames are always condition-tagged — `classification.<strategy>-<taxonomy>.json` — beside the shared read-only `context.json`. ⚠️ Artifacts written before 2026-07-07 use old `reasoning` tokens with different semantics; do not mix (see study_execution_log.md).

**Model is a third axis, orthogonal to the 5-combo validation above (added 2026-08-10).** `study-run`/`study-drift`/`study-escape` accept `--provider`/`--model`; running a second distinct model against the same `--artifacts-root`+condition auto-suffixes filenames (`classification.<tag>.<provider>-<model-slug>.json`) instead of colliding with or overwriting the first model's — see `docs/condition_model.md` §5 and `odc.py::resolve_effective_tag` for the exact resolution rules. First-model runs and every pre-2026-08-10 artifact are unaffected (no `model`/`provider` in an old checkpoint always resolves to the bare, untagged filename).

## Methodology invariants (do not violate)

- **Scientific debugging has TWO valid orderings — never mix them.** "Observe" is ambiguous between them; be explicit about which level you mean:
  - **Process level** (Zeller, *Why Programs Fail*, Ch. 6): **Observe → Hypothesize → Predict → Experiment/Examine → Conclude**. The failure is observed FIRST; hypotheses must be consistent with prior observations. No standalone function implements this anymore — the `few` prompt's narrated version (`_scientific_debugging_instructions`) was removed 2026-08-10 (pilot: 0/6 label changes vs plain structured prompting); it survives only as the conceptual ordering this invariant describes.
  - **Loop-iteration level** (AutoSD, Kang et al. EMSE 2024, Fig. 1): the initial failure observation (failing test + error message + code) is the *prompt input*; each iteration then runs **Hypothesis → Prediction → Experiment → Observation (experiment result) → Conclusion**.
  - The historical error to avoid: "Hypothesize, Observe, Predict, Examine, Conclude" — where "Observe" means examining failure symptoms *after* hypothesizing. That matches **neither** source and must not be propagated.
- **`iut_submissions/` is FROZEN** — it holds the pre-defense deliverables exactly as submitted. Never edit, reformat, or "fix" anything under it. Known issue kept for the record: `report/main.tex` lines ~332 and ~351-352 contain the wrong hybrid ordering (initial failure-symptom examination placed *after* hypothesizing — see the two-orderings rule above; this is NOT the same as AutoSD's loop-level hypothesize-first, which is valid). Do not propagate that ordering into new documents or code; do not fix it in place.

The batch/study layer (`batch.py`) scales this to a manifest of bugs with checkpoint/resume and graceful Ctrl+C: `study-plan` (balanced manifest) → `study-run` (paired prefix/postfix runs of ANY one condition, reusing existing contexts) → `study-drift` (cross-artifact prefix/postfix drift stats for one condition — RQ1/RQ3/RQ5, `analysis.py`; renamed from `study-analyze`; defaults to the pipeline default condition, scientific-open) → `study-escape` (RQ2 coverage metrics `taxonomy_coverage_<N>.json`, comparing the closed and open passes of one strategy) → `study-ladder` (RQ4 ablation-ladder metrics `taxonomy_grounding_<N>.json`, comparing an arbitrary ordered list of condition tags) → `study-export` (LaTeX + CSV, `results_export.py`). `study-classify` (the old prefix-only shortcut that used to host the RQ2 trigger and dead RQ4 engine) is retired 2026-07-08 — tombstoned, redirects to `study-run`. Checkpoints are per condition (`checkpoint.pairs.<tag>.json` only now — the old `checkpoint.prefix.<tag>.json` scheme died with `study-classify`). `comparison.py` computes agreement metrics incl. per-project Cohen's Kappa.

Module map:
- `cli.py` — argparse dispatch for script mode; entrypoint.
- `interactive/` — the `odc>` REPL: `handlers.py` (command logic), `commands.py` (registry), `completer.py`, `session.py` (persisted session state). Slash commands (`/run`) mirror script commands (`run`).
- `defects4j.py` — Defects4J wrapper: query/export, coverage parsing, WSL path translation.
- `llm.py` — provider abstraction (Gemini / OpenRouter / Groq / OpenAI-compatible).
- `odc.py` — canonical 7-type taxonomy + family mapping. `models.py` — dataclasses for persisted artifacts. `parsing.py` — stack-trace + JSON parsing. `multifault.py` — defects4j-mf co-existence data. `web_fetch.py` — bug-report fetcher. `console.py` — Rich output.

## Output layout

- `.dist/runs/<Project>_<bug>_<prefix|postfix>/` — standalone `run`/`collect`/`classify` outputs.
- `.dist/study/` — batch outputs: `manifest_<N>.json` (or hand-authored, e.g. `manifest_pilot.json`), `artifacts_<N>/{prefix,postfix}/` (all conditions live as tagged files in the SAME bug folders, beside one shared `context.json`), `checkpoint.pairs.<tag>.json`, `summary.json` (study-run — see gotcha below), `taxonomy_coverage_<N>.json` (study-escape, RQ2), `taxonomy_grounding_<N>.json` (study-ladder, RQ4), `analysis_<N>.{json,md}` (study-drift), `latex/`, `csv/` (N = target bug count).
- **`.dist/study/artifacts_full/`** — a manually-named `--artifacts-root` override, NOT the `artifacts_<N>` auto-naming convention. Holds the pre-collected 854 prefix + 854 postfix `context.json` corpus (added 2026-07-06, ~1 week to collect). Every study command should point `--artifacts-root` here so any manifest/condition reuses one context store instead of re-collecting.
- `work/` — standalone Defects4J checkouts; `.dist/study/work/` — batch checkouts.

`work/`, root `artifacts/`, `logs/`, and `.env` are gitignored. **`.dist/` is NOT uniformly gitignored, and the gitignore rule is narrower than the folder names suggest**: `artifacts/` (`.gitignore:41`) matches only a directory literally named `artifacts` — it does NOT match `artifacts_200` or `artifacts_full`.
- `.dist/runs/` — standalone outputs; several bug folders are tracked in git.
- **`.dist/study/artifacts/` (unnumbered) is the committed preliminary dataset** (~35 prefix bugs, old untagged filenames) backing the pre-defense results (73.5% strict match etc.), kept via a `.gitignore` negation. Treat it like `iut_submissions/`: historical record — never delete, never rerun into it, never "migrate" it to the tagged naming.
- **`.dist/study/artifacts_full/` is fully git-tracked too** (1,772 files, ~114MB) — the bare `artifacts/` rule never matches it, so nothing inside it is actually ignored. This is a deliberate, standing policy, not an oversight to silently patch: `context.json` is tracked everywhere because it's the pipeline's biggest bottleneck to regenerate — **and so are the results**: `git ls-files` shows 1,708 `context.json`, 3,074 `classification.<tag>.json`, 3,074 `report.<tag>.md` and 5 checkpoints tracked inside it (corrected 2026-09-11; this paragraph previously claimed classifications were NOT tracked, which was wrong and would have misled anyone planning a handoff). Changing what's tracked here is a judgment call for the team, not an autonomous `.gitignore` fix. ⚠️ Never widen the `artifacts/` rule to `artifacts*/` — it looks like a bug but widening it silently ignores all ~7,900 of those tracked files. See `docs/TEAM_WORKFLOW.md`.
- `.dist/study/artifacts_200/` — an abandoned early smoke test (`manifest_200.json`, 2 bugs, pre-redesign untagged naming) — legacy, not part of any active study.

Actually regenerable/ignored: `.dist/test_tmp_batch/` (pytest debris, delete freely), `work/` checkouts (both `work/` and `.dist/study/work/`).

**Gotcha — a manifest is a worklist, not a namespace.** `--artifacts-root` decides *where* output goes; `--manifest` only decides *which bugs this run touches*. Two manifests pointed at the same `--artifacts-root` under the same condition read/write the exact same per-bug files if their bug keys overlap — intentional, since it's what lets every manifest reuse one shared context store. The one place manifest identity matters: `checkpoint.pairs.<tag>.json` is keyed by `(artifacts_root, tag)` only, **not** by manifest name, so switching manifests under the same root+tag resets resume state ("checkpoint manifest hash mismatch — starting fresh"). This does not reprocess or destroy already-written classification files — those are separately protected by a file-existence skip-check.

**Gotcha — `summary.json` (from `study-run`) is the only study artifact that isn't condition-tagged.** Everything else (`checkpoint.pairs.<tag>.json`, `classification.<tag>.json`, `taxonomy_coverage_<N>.json` naming aside — that one is per-strategy not per-full-tag) carries its condition in the filename; a second `study-run` under a different condition silently overwrites the first run's `summary.json`.

<!-- rtk-instructions v2 -->
# RTK (Rust Token Killer) - Token-Optimized Commands

## Golden Rule

**Always prefix commands with `rtk`**. If RTK has a dedicated filter, it uses it. If not, it passes through unchanged. This means RTK is always safe to use.

**Important**: Even in command chains with `&&`, use `rtk`:
```bash
# ❌ Wrong
git add . && git commit -m "msg" && git push

# ✅ Correct
rtk git add . && rtk git commit -m "msg" && rtk git push
```

## RTK Commands by Workflow

### Build & Compile (80-90% savings)
```bash
rtk cargo build         # Cargo build output
rtk cargo check         # Cargo check output
rtk cargo clippy        # Clippy warnings grouped by file (80%)
rtk tsc                 # TypeScript errors grouped by file/code (83%)
rtk lint                # ESLint/Biome violations grouped (84%)
rtk prettier --check    # Files needing format only (70%)
rtk next build          # Next.js build with route metrics (87%)
```

### Test (60-99% savings)
```bash
rtk cargo test          # Cargo test failures only (90%)
rtk go test             # Go test failures only (90%)
rtk jest                # Jest failures only (99.5%)
rtk vitest              # Vitest failures only (99.5%)
rtk playwright test     # Playwright failures only (94%)
rtk pytest              # Python test failures only (90%)
rtk rake test           # Ruby test failures only (90%)
rtk rspec               # RSpec test failures only (60%)
rtk test <cmd>          # Generic test wrapper - failures only
```

### Git (59-80% savings)
```bash
rtk git status          # Compact status
rtk git log             # Compact log (works with all git flags)
rtk git diff            # Compact diff (80%)
rtk git show            # Compact show (80%)
rtk git add             # Ultra-compact confirmations (59%)
rtk git commit          # Ultra-compact confirmations (59%)
rtk git push            # Ultra-compact confirmations
rtk git pull            # Ultra-compact confirmations
rtk git branch          # Compact branch list
rtk git fetch           # Compact fetch
rtk git stash           # Compact stash
rtk git worktree        # Compact worktree
```

Note: Git passthrough works for ALL subcommands, even those not explicitly listed.

### GitHub (26-87% savings)
```bash
rtk gh pr view <num>    # Compact PR view (87%)
rtk gh pr checks        # Compact PR checks (79%)
rtk gh run list         # Compact workflow runs (82%)
rtk gh issue list       # Compact issue list (80%)
rtk gh api              # Compact API responses (26%)
```

### JavaScript/TypeScript Tooling (70-90% savings)
```bash
rtk pnpm list           # Compact dependency tree (70%)
rtk pnpm outdated       # Compact outdated packages (80%)
rtk pnpm install        # Compact install output (90%)
rtk npm run <script>    # Compact npm script output
rtk npx <cmd>           # Compact npx command output
rtk prisma              # Prisma without ASCII art (88%)
rtk uv run <cmd>        # Compact uv project command output
```

### Files & Search (60-75% savings)
```bash
rtk ls <path>           # Tree format, compact (65%)
rtk read <file>         # Code reading with filtering (60%)
rtk grep <pattern>      # Search grouped by file (75%). Format flags (-c, -l, -L, -o, -Z) run raw.
rtk find <pattern>      # Find grouped by directory (70%)
```

### Analysis & Debug (70-90% savings)
```bash
rtk err <cmd>           # Filter errors only from any command
rtk log <file>          # Deduplicated logs with counts
rtk json <file>         # JSON structure without values
rtk deps                # Dependency overview
rtk env                 # Environment variables compact
rtk summary <cmd>       # Smart summary of command output
rtk diff                # Ultra-compact diffs
```

### Infrastructure (85% savings)
```bash
rtk docker ps           # Compact container list
rtk docker images       # Compact image list
rtk docker logs <c>     # Deduplicated logs
rtk kubectl get         # Compact resource list
rtk kubectl logs        # Deduplicated pod logs
```

### Network (65-70% savings)
```bash
rtk curl <url>          # Compact HTTP responses (70%)
rtk wget <url>          # Compact download output (65%)
```

### Meta Commands
```bash
rtk gain                # View token savings statistics
rtk gain --history      # View command history with savings
rtk discover            # Analyze Claude Code sessions for missed RTK usage
rtk proxy <cmd>         # Run command without filtering (for debugging)
rtk init                # Add RTK instructions to CLAUDE.md
rtk init --global       # Add RTK to ~/.claude/CLAUDE.md
```

## Token Savings Overview

| Category | Commands | Typical Savings |
|----------|----------|-----------------|
| Tests | vitest, playwright, cargo test | 90-99% |
| Build | next, tsc, lint, prettier | 70-87% |
| Git | status, log, diff, add, commit | 59-80% |
| GitHub | gh pr, gh run, gh issue | 26-87% |
| Package Managers | pnpm, npm, npx | 70-90% |
| Files | ls, read, grep, find | 60-75% |
| Infrastructure | docker, kubectl | 85% |
| Network | curl, wget | 65-70% |

Overall average: **60-90% token reduction** on common development operations.
<!-- /rtk-instructions -->