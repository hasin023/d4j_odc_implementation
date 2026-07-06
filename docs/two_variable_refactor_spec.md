# Two-Variable Refactor Spec (agreed 2026-07-06)

**Status: EXECUTED 2026-07-06.** All items below are implemented and tested
(87 passed; only the 2 known WSL-path tests fail on native Linux). Kept as the
decision record. Do NOT re-litigate the decisions below. Phase 1
(open taxonomy, RQ2) is already implemented and tested on top of the OLD naming
(`--prompt-style` + `--taxonomy`, `study-coverage`); this refactor converts that working
state to the final two-variable design. All 87 tests pass pre-refactor (2 known
WSL-path failures on native Linux are unrelated).

## Decisions (user-confirmed, final)

1. **Two explicit variables replace `--prompt-style`:**
   - `--taxonomy  free | closed | open`   — **default `open`** (user's explicit choice; do not argue closed)
   - `--reasoning zero | scientific`      — default `scientific`; `agentic` reserved for Phase 2
   - Old preset mapping: naive = free×zero, direct = closed×zero, scientific = closed×scientific.
   - Level names are literature-aligned: closed-set = forced 7; open-set = 7 + "Other";
     free = no taxonomy. Reasoning axis = enforcement depth of the scientific method:
     absent (zero) → narrated (scientific) → enforced (agentic). Do NOT call scientific "few".
2. **Filenames always explicit** (no untagged default file):
   - `classification.<taxonomy>-<reasoning>.json`, `report.<taxonomy>-<reasoning>.md`
   - e.g. `classification.open-scientific.json`, `classification.closed-zero.json`
3. **Bug-centric layout** — all conditions live in the SAME bug folder next to context.json:
   - standalone: `.dist/runs/<Project>_<bug>_<prefix|postfix>/`
   - batch: `.dist/study/artifacts_<N>/{prefix,postfix}/<Project>_<bug>_<prefix|postfix>/`
   - `context.json` is written ONLY by collect; every classification condition reads it.
   - Parallel roots `baseline_<N>/`, `naive_<N>/`, `coverage_<N>/` are RETIRED.
   - Checkpoints per condition: `artifacts_<N>/checkpoint.<taxonomy>-<reasoning>.json`
     (prefix-only arms) — study-run keeps its paired checkpoint but tag-suffixed too.
4. **Commands:**
   - `study-classify --manifest m.json --taxonomy X --reasoning Y` — NEW generalized
     prefix-only condition runner (replaces study-baseline / study-naive / study-coverage;
     they were all `run_baseline_from_manifest` with hardcoded conditions).
   - `study-run` keeps collect+classify pairs; gains both variable flags.
   - `study-coverage`, `study-baseline`, `study-naive`, `--prompt-style` → **tombstones**:
     registered names that print the new equivalent invocation and exit(2). Never execute.
     Example: "'study-baseline' was removed. Use: study-classify --manifest ... --taxonomy closed --reasoning zero"
   - RQ2 metrics file renamed `taxonomy_coverage_<N>.json` (avoid collision with code
     coverage); auto-computed after the open pass when the closed pass exists (same logic
     as current `_cmd_study_coverage`).
5. **The RQ condition map** (for help text/docs):
   - RQ1/3/5 + RQ2 side A: `study-run --taxonomy closed` (closed-scientific pairs)
   - RQ2 side B: `study-classify --taxonomy open` (open-scientific, prefix)
   - RQ4 arms: `study-classify --taxonomy closed --reasoning zero` and `--taxonomy free --reasoning zero`
6. **`free × scientific`** (protocol without taxonomy) becomes implementable via the
   factorial interface: scientific instructions minus the ODC diagnostic tree/labels;
   answer in own words. Implement the prompt branch (drop tree + taxonomy + JSON odc
   fields; keep Observe→Hypothesize→Predict→Examine→Conclude). Low priority but do it —
   it completes the grid and is the interaction-effect control.

## Per-file change list

- `odc.py`: add `TAXONOMY_FREE = "free"`; `REASONING_ZERO/SCIENTIFIC/AGENTIC`;
  `condition_tag(taxonomy, reasoning) -> "open-scientific"` helper + parser.
- `prompting.py`: `build_messages(context, taxonomy, reasoning)`; route:
  free×zero → old naive prompt; (closed|open)×zero → old direct (taxonomy_mode passed);
  (closed|open)×scientific → old scientific; free×scientific → new branch (see §6).
- `pipeline.py`: `classify_bug_context(..., taxonomy, reasoning)`; validation:
  free → no label validation (free-form label stored in odc_type, family None — reuse
  old naive branch); closed/open → current validation incl. Other rules. Output paths
  derived from condition_tag. `ClassificationResult` gains `reasoning`; keep
  `prompt_style` field populated (legacy readers) via mapping.
- `models.py`: add `reasoning: str = "scientific"`; keep existing fields.
- `batch.py`: `run_batch_from_manifest` + `run_baseline_from_manifest` →
  parameterize by (taxonomy, reasoning); write tagged files into shared bug folders;
  per-condition checkpoint names; summary records both variables.
- `cli.py`: new flags on run/classify/study-run; new `study-classify`; tombstone stubs;
  update `_cmd_study_coverage` logic into `study-classify` post-run metrics hook
  (metrics when taxonomy==open and closed-scientific files exist for same bugs).
- `analysis.py`: `compute_coverage_metrics` discovery: read
  `classification.closed-scientific.json` vs `classification.open-scientific.json`
  within the SAME folder tree (no more two roots); keep two-root support only if trivial.
- `comparison.py`: `compare-batch`/`_discover_pairs` in batch.py: prefix/postfix pairing
  unchanged, but classification filename now tagged — pick tag via new `--taxonomy/--reasoning`
  flags on study-analyze/compare-batch (default open-scientific per CLI default? NO —
  analyze must compare like-for-like; give it explicit flags defaulting to closed-scientific
  for RQ5 analysis, since that is the paired-pass condition. Note this exception in help.)
  ^ NOTE: study-run default taxonomy follows CLI default (open) unless user overrides;
  keep flags explicit in all documented RQ recipes to avoid surprises.
- tests: update `test_prompting.py`, `test_batch.py`, `test_open_taxonomy.py` call sites;
  add tests: condition_tag, tagged filenames, tombstone exit codes, free×scientific prompt.
- docs: README command tables + Output Layout section; AGENTS.md §§4/7/8 (layout,
  artifact contracts, runtime dirs) + command list; CLAUDE.md architecture lines
  (prompt styles → two variables); `docs/classification_engine_plan.md` §6 variable table.

## Context that motivated this (for the paper, do not lose)

- The old names conflated two variables; user explicitly rejected preset bundles.
- "open/closed" follow open-set/closed-set classification literature; user initially
  proposed inverted names — resolved; "free" = no taxonomy.
- Naive arm is required by RQ4 only (unstructured baseline anchor + vocabulary reduction).
- Reasoning-model swap (o1/thinking models) considered and rejected as a substitute for the
  agentic loop: doesn't lift the evidence ceiling, no exogeneity, hides the trace;
  acceptable later as a robustness arm on the eval subset.
- Default=open caveat for the manuscript: one sentence defending the default against
  "you extended ODC" (Other = measurement instrument; RQ2 §details_of_RQ2.md Q1).

## After this refactor

Phase 2 (agentic engine per `docs/classification_engine_plan.md`) builds on
`--reasoning agentic`; llm.py already has the `response_schema` seam on `complete()`.
