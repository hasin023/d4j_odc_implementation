# Study Execution Log

Running record of how classifications were actually executed — commands, environment,
results, and gotchas. Append a section per run so agents and teammates can reproduce
or resume without re-deriving anything. Newest at the bottom.

> For current condition semantics (taxonomy × strategy) see the 2026-07-07 amendment near the bottom of this file, or docs/condition_model.md directly.

> ⚠️ **STALE COMMAND NAMES (2026-07-08):** `study-classify` and `study-analyze`, used throughout the historical runs below, are retired (tombstoned — they now print a redirect and exit). Every condition now goes through `study-run` (prefix+postfix, any `--taxonomy`/`--strategy`); the old auto-computed RQ2 coverage metrics are now the explicit `study-escape` command, and the RQ4 ladder now has its own `study-ladder` command. See `docs/condition_model.md` §6. This log's historical command blocks are left as-written for reproducibility of what was actually run — do not "fix" them in place.

## Environment (all runs unless noted)

- Provider/model: `gemini` / `gemini-3.1-flash-lite-preview` (from `.env`; free tier ~1,500 RPD)
- Evidence: pre-collected contexts in `.dist/study/artifacts_full/{prefix,postfix}/<Project>_<bug>_<mode>/context.json`
  (854 prefix + 854 postfix; validated 1707/1708 — see Known Data Issues)
- All study commands take `--artifacts-root .dist/study/artifacts_full` so one context store
  serves every manifest; contexts are reused (never re-collected) — verify via
  `reused_context` counts in the run summaries.

## Known Data Issues

- `Chart_1_postfix/context.json` has an empty `fix_diff` → a postfix run on Chart 1 silently
  behaves like prefix (no error raised). Repair before any study that includes it:
  `collect --project Chart --bug 1 --include-fix-diff` targeting that folder — or exclude
  Chart 1 from postfix-dependent analyses.

---

## 2026-07-06 — Pilot run (manifest_pilot.json, 6 bugs, ~30 LLM calls)

Hand-picked deviation probes: Lang 60 (anchor, clean Checking), Time 25/27
(Checking↔Algorithm boundary), JxPath 20 (Relationship/Interface boundary), Compress 44
(Checking↔Assignment), Closure 143 (design-heavy, Function/Class/Object bias probe).

Commands (in order):

```bash
python -m d4j_odc_pipeline study-run      --manifest manifest_pilot.json --artifacts-root .dist/study/artifacts_full --taxonomy closed --skip-coverage
python -m d4j_odc_pipeline study-classify --manifest manifest_pilot.json --artifacts-root .dist/study/artifacts_full                       # open-scientific (default)
python -m d4j_odc_pipeline study-classify --manifest manifest_pilot.json --artifacts-root .dist/study/artifacts_full --taxonomy closed --reasoning zero
python -m d4j_odc_pipeline study-classify --manifest manifest_pilot.json --artifacts-root .dist/study/artifacts_full --taxonomy free   --reasoning zero
python -m d4j_odc_pipeline study-analyze  --prefix-dir .dist/study/artifacts_full/prefix --postfix-dir .dist/study/artifacts_full/postfix --manifest manifest_pilot.json
```

Outputs: tagged files in the bug folders; `.dist/study/taxonomy_coverage_6.json`;
`.dist/study/analysis_6.{json,md}`; `.dist/study/classify_summary.<tag>.json`;
`.dist/study/summary.json`. All arms reported `reused_context = 6/6`; total wall time
≈ 3 minutes.

### Result matrix (prefix side unless noted)

| bug | closed-scientific | open-scientific | closed-zero | free-zero (own words) | postfix closed-sci |
|---|---|---|---|---|---|
| Lang_60 | Checking | **Algorithm/Method** | Checking | "Incorrect Boundary Check" | Algorithm/Method |
| Time_27 | Algorithm/Method | Algorithm/Method | Algorithm/Method | "Incorrect Parsing Logic" | **Checking** |
| Time_25 | Algorithm/Method | Algorithm/Method | Algorithm/Method | "Incorrect DST transition…" | Algorithm/Method |
| JxPath_20 | Algorithm/Method | Algorithm/Method | Algorithm/Method | "Incorrect relational…" | Algorithm/Method |
| Compress_44 | Checking | Checking | Checking | "Missing Input Validation" | Checking |
| Closure_143 | Algorithm/Method | Algorithm/Method | Algorithm/Method | "input validation logic…" | **Checking** |

### Findings (n=6 — signals, not results)

1. **Shift ranking: evidence mode ≫ run variance > taxonomy > reasoning.**
   Pre→post fix changed 3/6 types (RQ5 signal); taxonomy open-vs-closed shifted 1/6;
   reasoning zero-vs-scientific shifted 0/6.
2. **Coverage 1.0, escape 0/6** — no bug took the "Other" hatch, not even JxPath 20.
   Shift-κ (8-cat) = 0.57 driven entirely by Lang_60.
3. **Lang_60's "taxonomy shift" is probably sampling variance**: two earlier standalone
   open-scientific runs of the same context said Checking; the pilot's open run said
   Algorithm/Method. Same condition, different answers across runs → the RQ2 shift
   metric will absorb temperature noise unless self-consistency voting (Phase 3, k=3)
   lands first. Treat single-run shift-κ as an upper bound on true schema instability.
4. **closed-zero matched closed-scientific 6/6** — zero-shot equaled the full protocol on
   these bugs. If this holds at scale it is an RQ4 headline either way; do not assume the
   protocol wins.
5. **free-zero produced ad-hoc vocabulary** (four distinct label styles in 6 bugs) —
   the RQ4 vocabulary-reduction phenomenon is clearly present.
6. Distribution skews Algorithm/Method + Checking, consistent with known Defects4J
   composition.

### Implications for next steps

- Run Phase 3 self-consistency BEFORE the full RQ2 passes, or shift-κ is confounded.
- Add the daily budget guard before any full-corpus run.
- Keep Lang_60 as the variance canary in future pilots.

---

## 2026-07-06 — Agentic engine smoke test (1 bug, 3 LLM calls)

First live run of `--reasoning agentic` (closed taxonomy) on Time_27 prefix:

```bash
python -m d4j_odc_pipeline classify --context .dist/study/artifacts_full/prefix/Time_27_prefix/context.json --taxonomy closed --reasoning agentic
```

- 3 turns: probed `snippet(PeriodFormatterBuilder)` — the actual buggy class —
  (duplicate request deduped with an "already served" nudge), then concluded.
- Concluded **Checking**, where single-shot closed-scientific said Algorithm/Method
  and the postfix oracle run said Checking — i.e. the agentic prefix answer agreed
  with the oracle where the single-shot did not (n=1 anecdote; the RQ4 agentic arm
  measures this properly).
- Transcript (hypothesis/prediction/probe/observation per turn) persisted in the
  artifact's `turns` field; `llm_calls_used: 3` recorded and counted by the budget guard.

---

## 2026-07-06 — Agentic arm over the pilot manifest (6 bugs, 19 LLM calls)

```bash
python -m d4j_odc_pipeline study-classify --manifest manifest_pilot.json --artifacts-root .dist/study/artifacts_full --taxonomy closed --reasoning agentic
```

Batch path verified live: context reuse 6/6, per-turn budget accounting correct
(summary `llm_calls_made: 19` = 5×3 + 1×4 turns), no forced conclusions, no failures.

| bug | agentic | turns | single-shot (closed-sci) | postfix reference |
|---|---|---|---|---|
| Lang_60 | Checking | 3 | Checking | Algorithm/Method |
| Time_27 | **Checking** | 3 | Algorithm/Method | Checking |
| Time_25 | Algorithm/Method | 3 | Algorithm/Method | Algorithm/Method |
| JxPath_20 | Algorithm/Method | 4 | Algorithm/Method | Algorithm/Method |
| Compress_44 | Checking | 3 | Checking | Checking |
| Closure_143 | **Checking** | 3 | Algorithm/Method | Checking |

### Findings (n=6 — signals, not results)

1. **Agreement with the postfix reference: agentic 5/6 vs single-shot 3/6.**
   On both bugs where the engines disagreed (Time_27, Closure_143), the agentic
   answer matched the oracle-informed reference and the single-shot did not.
   If this holds at scale it is the RQ4 headline for the agentic rung.
2. **Probe behavior is on-target**: every bug's first probe was `snippet(<the
   suspicious class>)` — the loop reads the code it hypothesizes about. Typical
   pattern: probe → (dedup nudge on a repeat request) → conclude in 3 turns.
3. Average ~3.2 calls/bug → full-corpus agentic pass ≈ 2,700 calls (~2 budget-days).
4. Lang_60 stayed Checking here (variance canary: its earlier open-pass flip
   remains the only observed run-to-run instability).

---

## 2026-07-07 — PROTOCOL AMENDMENT: the condition model (taxonomy × strategy)

The condition variables were redesigned; **`docs/condition_model.md` is now the
single authoritative spec.** Summary:

- `--strategy zero|few|scientific` replaces `--reasoning zero|scientific|agentic`.
- `zero` = zero-shot, taxonomy-free by definition (invalid with closed/open).
- `few` = the strong static prompt (taxonomy + tree + worked examples) — the
  full content of the old narrated "scientific" single-shot, accurately renamed.
- `scientific` now means the enforced loop (old "agentic"). The narrated
  single-shot condition is retired: the pilot showed narration changed 0/6
  labels while enforcement changed 2/6, both toward the oracle.
- Valid conditions: free-zero, closed-few, open-few, closed-scientific,
  open-scientific. **Default everywhere (incl. postfix): open-scientific** —
  per the supervisor's position that bugs must never be force-fitted into a
  fixed schema; escapes are data, and a significant escape mass is future
  taxonomy-adaptation scope.

⚠️ **All artifacts and log entries ABOVE this entry use the old tokens**: their
`reasoning` field and `*-scientific` filenames mean the narrated single-shot;
`*-agentic` files mean the loop. They are exploratory pilot data — do not mix
with new runs. To clean stale pilot classifications from the context store:

```bash
find .dist/study/artifacts_full -name "classification.*.json" -delete
find .dist/study/artifacts_full -name "report.*.md" -delete   # context.json untouched
```

---

## 2026-07-08 — Batch/study CLI redesign: `study-classify` retired, `study-escape`/`study-ladder` added

`study-classify` (the prefix-only cost-saving shortcut) was killed — tombstoned,
redirects to `study-run`. `study-analyze` renamed to `study-drift` (tombstoned
old name). Two new commands take over what used to be side effects of
`study-classify`: `study-escape` (RQ2 coverage/escape-rate, closed vs open for
one strategy) and `study-ladder` (RQ4 ablation ladder, generalized from a
hardcoded 3-tier `naive/direct/scientific` comparison to an arbitrary ordered
list of condition tags). Full rationale and command surface: `docs/condition_model.md`
§6, `AGENTS.md`. Also cleaned 66 stale pre-tag-flip files (old
`<taxonomy>-<strategy>` naming) out of the 6 pilot bug folders in
`artifacts_full` — `context.json` untouched.

Re-ran the pilot (`manifest_pilot.json`, 6 bugs) under the new command surface
to smoke-test end-to-end: `study-run` (scientific-open) → `study-drift`,
`study-run` (scientific-closed) → `study-escape`, `study-run` (zero-free,
few-open) → `study-ladder`. All four commands produced correctly-tagged,
non-empty output. See `docs/JSS_HANDOFF.md` §4 for the actual numbers (pilot
row of each RQ table).

## 2026-07-09 — `study-drift` wiring fix + 40-bug dev-validation run

**Fix:** `analyze_batch_artifacts` (the engine behind `study-drift`) was
silently producing empty or wrong tables for RQ1 (type distribution), part of
RQ3 (per-type P/R/F1, overall Cohen's κ, confusion matrix), and RQ5
(per-project κ) — the functions existed in `analysis.py`/`comparison.py` and
were unit-tested, but were never called from this path. Confirmed by direct
inspection: `accuracy.tex` generated from real pilot data read "Strict Match:
0/6" when the true value was 5/6. Fixed by wiring `compute_type_distribution`,
`compute_per_type_metrics`, `compute_per_project_kappa`, `compute_cohens_kappa`,
and a confusion-matrix build into `analyze_batch_artifacts`'s existing loop
(uses data it already collects — no new I/O, no change to `study-run`/
`study-escape`/`study-ladder`). Predates this session's `study-classify`
redesign; not caused by it. Regression coverage added to
`tests/test_batch.py`.

**Run:** `study-plan --target-bugs 40 --min-per-project 2 --seed 42` → all 17
projects covered, 2-3 bugs each. Ran the 4 conditions the 5 RQs require
(`zero-free`, `few-open`, `scientific-open`, `scientific-closed`; `few-closed`
skipped, not needed by any current RQ) against `--artifacts-root
.dist/study/artifacts_full`, then `study-drift`/`study-escape`/`study-ladder`.
Because these three scan the whole shared prefix/postfix tree rather than
filtering by manifest (manifest = worklist, not namespace), 4 leftover pilot
bugs not in `manifest_40.json` were picked up too → **effective n=44**, not 40.

Cost: ~14.4 real LLM calls/bug across the 4 conditions (measured, not
assumed — scientific strategy averaged 2.5-2.7 calls/classification, well
under the 6-turn ceiling). Total ≈ 620 calls, ~21 minutes wall-clock, zero
Defects4J re-collection (context.json already existed for all 44 bugs from
the pre-collected 854-bug corpus).

Full results table: `docs/JSS_HANDOFF.md` §4. Headline: RQ4's taxonomy-
grounding effect is now clearly visible (43 unique free-form labels for 44
bugs collapsing to 4-5 under any taxonomy-constrained condition); RQ5's
per-project κ is now computable for all 17 projects (was "insufficient data"
for 4/5 projects at the pilot's n=6). **These are development-validation
numbers, not final results** — see `docs/JSS_HANDOFF.md`'s status flag before
citing anything from this run in the manuscript.

---

## 2026-07-10/11 — Pilot rerun after the ODC alignment audit (manifest_pilot.json, 6 bugs, all 4 conditions)

Context: `docs/odc_alignment_audit.md` (same session) fixed pre-fix evidence
leaks (modified-sources oracle, tracker fix-era content), added the Impact
opener attribute (previously vestigial — 0 populated), removed the
`odc_opener_hints`/`odc_closer_hints` keyword heuristics, and removed the
instrument-prior lines ("most Defects4J bugs are Checking/Algorithm/Method/
Assignment") from the `few`/`scientific` system prompts. Before overwriting,
the pilot's existing artifacts (all 4 conditions × 2 arms × 6 bugs = 96 files)
were copied to `.dist/study/pilot_snapshot_pre_audit_2026-07-10/` — kept
as a permanent before/after reference, not scratch.

**Provider/model/keys unchanged**: `gemini` / `gemini-3.1-flash-lite-preview`,
now via 7 `GEMINI_API_KEYS` on separate Google Cloud projects (rotation
untouched by this session — verified via `git diff` before rerunning).

```bash
python -m d4j_odc_pipeline study-run --manifest .dist/study/manifest_pilot.json --artifacts-root .dist/study/artifacts_full --no-skip-existing --summary-output .dist/study/pilot_rerun_summary.scientific-open.json
python -m d4j_odc_pipeline study-run --manifest .dist/study/manifest_pilot.json --artifacts-root .dist/study/artifacts_full --taxonomy closed --no-skip-existing --summary-output .dist/study/pilot_rerun_summary.scientific-closed.json
python -m d4j_odc_pipeline study-run --manifest .dist/study/manifest_pilot.json --artifacts-root .dist/study/artifacts_full --taxonomy free --strategy zero --no-skip-existing --summary-output .dist/study/pilot_rerun_summary.zero-free.json
python -m d4j_odc_pipeline study-run --manifest .dist/study/manifest_pilot.json --artifacts-root .dist/study/artifacts_full --taxonomy open --strategy few --no-skip-existing --summary-output .dist/study/pilot_rerun_summary.few-open.json
```

`--no-skip-existing` was required (files already existed from the original
pilot run). The checkpoint-based skip did **not** need bypassing separately —
`checkpoint.pairs.<tag>.json` under this artifacts-root had last been written
by the 40-bug dev-validation manifest, so its stored `manifest_hash` mismatched
`manifest_pilot.json`'s hash and the loader correctly treated it as stale
("Checkpoint manifest hash mismatch — starting fresh"), confirmed by comparing
the stored hash (`ab5cf61d2db91486`, 40 completed_keys) against a freshly
computed pilot-manifest hash (`7dab9804f3ee2333`) before running anything.
All 4 runs completed 6/6, no interruptions: ~1m6s / ~1m4s / ~21s / ~33s.

### Findings (n=6 — signals, not results; see caveat below)

1. **Impact went from 0/48 populated to 36/36 populated** in every
   taxonomy-constrained classification (few-open, scientific-open,
   scientific-closed × 6 bugs × 2 arms); correctly absent in all 12
   `zero-free` rows (must stay ODC-vocabulary-free). Distribution: 31
   Capability, 5 Reliability. Impact-stability negative control on
   `scientific-open`: 6/6 prefix↔postfix agreement — but flagged
   degenerate (all six landed on Capability within that one condition, so
   κ=1.0 is not yet a meaningful noise-floor read; Compress_44 does show
   Reliability elsewhere in the table, so the field isn't a rubber stamp
   in general, just within this n=6/this condition slice).
2. **`zero-free` "changes" (12/16 of all label diffs) are re-phrasings of
   the same underlying free-text judgment**, not audit-attributable shifts
   — expected non-determinism in an unstructured baseline, not signal.
3. **Real label shifts: 7/36 taxonomy-constrained comparisons (~19%)** —
   Lang_60 (few-open prefix, scientific-open postfix), Time_27 (few-open
   prefix, scientific-closed both arms, scientific-open postfix),
   Closure_143 (few-open prefix). Notably some are **postfix-arm** shifts,
   which the leak-sanitization fix does *not* touch (postfix payloads are
   unchanged) — attributable instead to the instrument-prior removal and/or
   `odc_opener_hints` removal, which apply to both arms.
4. **Prefix↔postfix strict-match rate**: `few-open` improved 4/6→5/6
   (66.7%→83.3%, Time_27 and Closure_143 newly agree). `scientific-open` and
   `scientific-closed` held at 5/6 (83.3%) but the *specific* disagreeing bug
   changed — Time_27 flipped into agreement, Lang_60 flipped into
   disagreement. Compress_44 (Checking/Checking) was unchanged across every
   condition, before and after — a stable anchor bug.
5. **Net read: mixed, not uniformly "improved."** One bug flip is a
   16.7-point swing at this n — not remotely citable, and not meant to be.
   The directional signal (few-open genuinely improved; scientific-*
   held flat in aggregate but the underlying agreement is not identical) is
   worth watching in the confirmatory run, nothing more.

Full per-row before/after table (all 48 bug×mode×condition rows, generated
from `pilot_snapshot_pre_audit_2026-07-10/` vs the post-rerun state):

| Bug | Mode | Condition | Before | After | Changed |
|---|---|---|---|---|---|
| Lang_60 | prefix | zero-free | Incorrect Boundary Condition (conf 1.0) | Off-by-one boundary condition error (conf 1.0, impact None) | CHANGED |
| Lang_60 | prefix | few-open | Algorithm/Method (conf 0.9) | Checking (conf 0.9, impact Capability) | CHANGED |
| Lang_60 | prefix | scientific-open | Checking (conf 1.0) | Checking (conf 1.0, impact Capability) | |
| Lang_60 | prefix | scientific-closed | Checking (conf 1.0) | Checking (conf 1.0, impact Capability) | |
| Lang_60 | postfix | zero-free | incorrect boundary condition (conf 1.0) | Off-by-one boundary error (conf 1.0, impact None) | CHANGED |
| Lang_60 | postfix | few-open | Algorithm/Method (conf 1.0) | Algorithm/Method (conf 1.0, impact Capability) | |
| Lang_60 | postfix | scientific-open | Checking (conf 1.0) | Algorithm/Method (conf 1.0, impact Capability) | CHANGED |
| Lang_60 | postfix | scientific-closed | Algorithm/Method (conf 1.0) | Algorithm/Method (conf 1.0, impact Capability) | |
| Time_27 | prefix | zero-free | Incorrect Parsing Logic (conf 0.9) | Incorrect parsing logic for ISO period formats (conf 0.9, impact None) | CHANGED |
| Time_27 | prefix | few-open | Algorithm/Method (conf 0.85) | Checking (conf 0.9, impact Reliability) | CHANGED |
| Time_27 | prefix | scientific-open | Algorithm/Method (conf 0.9) | Algorithm/Method (conf 0.9, impact Capability) | |
| Time_27 | prefix | scientific-closed | Checking (conf 0.9) | Algorithm/Method (conf 0.9, impact Capability) | CHANGED |
| Time_27 | postfix | zero-free | Incorrect logic in composite formatter construction (conf 0.95) | Incorrect logic in composite formatter construction (conf 0.95, impact None) | |
| Time_27 | postfix | few-open | Checking (conf 0.9) | Checking (conf 0.9, impact Reliability) | |
| Time_27 | postfix | scientific-open | Checking (conf 0.95) | Algorithm/Method (conf 1.0, impact Capability) | CHANGED |
| Time_27 | postfix | scientific-closed | Checking (conf 1.0) | Algorithm/Method (conf 1.0, impact Capability) | CHANGED |
| Time_25 | prefix | zero-free | Incorrect DST transition handling (conf 1.0) | Incorrect Daylight Saving Time (DST) transition handling (conf 0.95, impact None) | CHANGED |
| Time_25 | prefix | few-open | Algorithm/Method (conf 0.9) | Algorithm/Method (conf 0.9, impact Capability) | |
| Time_25 | prefix | scientific-open | Algorithm/Method (conf 0.9) | Algorithm/Method (conf 0.9, impact Capability) | |
| Time_25 | prefix | scientific-closed | Algorithm/Method (conf 0.95) | Algorithm/Method (conf 0.9, impact Capability) | |
| Time_25 | postfix | zero-free | incorrect logic for DST transition handling (conf 1.0) | incorrect DST transition handling (conf 1.0, impact None) | CHANGED |
| Time_25 | postfix | few-open | Algorithm/Method (conf 0.9) | Algorithm/Method (conf 0.9, impact Capability) | |
| Time_25 | postfix | scientific-open | Algorithm/Method (conf 0.9) | Algorithm/Method (conf 1.0, impact Capability) | |
| Time_25 | postfix | scientific-closed | Algorithm/Method (conf 1.0) | Algorithm/Method (conf 0.9, impact Capability) | |
| JxPath_20 | prefix | zero-free | Incorrect relational operator logic (conf 0.95) | Incorrect operator precedence or evaluation logic for relational expressions (conf 0.85, impact None) | CHANGED |
| JxPath_20 | prefix | few-open | Algorithm/Method (conf 0.9) | Algorithm/Method (conf 0.8, impact Capability) | |
| JxPath_20 | prefix | scientific-open | Algorithm/Method (conf 0.9) | Algorithm/Method (conf 0.9, impact Capability) | |
| JxPath_20 | prefix | scientific-closed | Algorithm/Method (conf 0.9) | Algorithm/Method (conf 0.9, impact Capability) | |
| JxPath_20 | postfix | zero-free | Incorrect Argument Order in Method Call (conf 1.0) | Incorrect argument order in method call (conf 1.0, impact None) | CHANGED |
| JxPath_20 | postfix | few-open | Algorithm/Method (conf 0.9) | Algorithm/Method (conf 1.0, impact Capability) | |
| JxPath_20 | postfix | scientific-open | Algorithm/Method (conf 1.0) | Algorithm/Method (conf 1.0, impact Capability) | |
| JxPath_20 | postfix | scientific-closed | Algorithm/Method (conf 1.0) | Algorithm/Method (conf 1.0, impact Capability) | |
| Compress_44 | prefix | zero-free | Missing Input Validation (conf 1.0) | Missing Input Validation (conf 0.95, impact None) | |
| Compress_44 | prefix | few-open | Checking (conf 1.0) | Checking (conf 0.9, impact Reliability) | |
| Compress_44 | prefix | scientific-open | Checking (conf 1.0) | Checking (conf 1.0, impact Capability) | |
| Compress_44 | prefix | scientific-closed | Checking (conf 1.0) | Checking (conf 1.0, impact Capability) | |
| Compress_44 | postfix | zero-free | Missing Input Validation (conf 1.0) | Missing Input Validation (conf 1.0, impact None) | |
| Compress_44 | postfix | few-open | Checking (conf 1.0) | Checking (conf 1.0, impact Reliability) | |
| Compress_44 | postfix | scientific-open | Checking (conf 1.0) | Checking (conf 1.0, impact Capability) | |
| Compress_44 | postfix | scientific-closed | Checking (conf 1.0) | Checking (conf 1.0, impact Reliability) | |
| Closure_143 | prefix | zero-free | input validation logic error (conf 0.95) | Input validation logic error (conf 0.95, impact None) | CHANGED |
| Closure_143 | prefix | few-open | Algorithm/Method (conf 0.9) | Checking (conf 0.9, impact Capability) | CHANGED |
| Closure_143 | prefix | scientific-open | Checking (conf 1.0) | Checking (conf 1.0, impact Capability) | |
| Closure_143 | prefix | scientific-closed | Checking (conf 0.95) | Checking (conf 1.0, impact Capability) | |
| Closure_143 | postfix | zero-free | incomplete input validation and logic error (conf 0.95) | input validation and logic error (conf 1.0, impact None) | CHANGED |
| Closure_143 | postfix | few-open | Checking (conf 0.9) | Checking (conf 0.9, impact Capability) | |
| Closure_143 | postfix | scientific-open | Checking (conf 1.0) | Checking (conf 1.0, impact Capability) | |
| Closure_143 | postfix | scientific-closed | Checking (conf 1.0) | Checking (conf 1.0, impact Capability) | |

**Do not cite any of this in the manuscript** — n=6, same status as every
other pilot number in `docs/JSS_HANDOFF.md`. Value here is methodological:
confirms the audit fixes are live and measurably change output (so they
weren't silently inert), and gives a first, honest (not cherry-picked) look
at direction and magnitude before spending the confirmatory run's budget.

---

## 2026-07-11 — 40-bug dev-validation rerun after the ODC alignment audit (manifest_40.json, all 4 conditions)

Context: same audit as the pilot rerun above, now applied to the larger
(effective n=44) dev-validation set — `manifest_40.json` (40 bugs) plus the
4 pilot bugs `study-drift`/`study-escape`/`study-ladder` sweep in from the
shared artifact tree (see the 2026-07-09 entry for why). Before overwriting,
all 40 bugs' existing artifacts (2 arms × 4 conditions × 2 files = 640 files)
were copied to `.dist/study/manifest40_snapshot_pre_rerun_2026-07-11/`,
along with the pre-rerun `analysis_40.json`/`taxonomy_coverage_40.json`/
`taxonomy_grounding_40.json` (also recoverable from git history, since those
three are tracked — see `CLAUDE.md`'s artifact-tracking policy — but copied
alongside for a single before/after location).

```bash
python -m d4j_odc_pipeline study-run --manifest .dist/study/manifest_40.json --artifacts-root .dist/study/artifacts_full --no-skip-existing --summary-output .dist/study/manifest40_rerun_summary.scientific-open.json
python -m d4j_odc_pipeline study-run --manifest .dist/study/manifest_40.json --artifacts-root .dist/study/artifacts_full --taxonomy closed --no-skip-existing --summary-output .dist/study/manifest40_rerun_summary.scientific-closed.json
python -m d4j_odc_pipeline study-run --manifest .dist/study/manifest_40.json --artifacts-root .dist/study/artifacts_full --taxonomy free --strategy zero --no-skip-existing --summary-output .dist/study/manifest40_rerun_summary.zero-free.json
python -m d4j_odc_pipeline study-run --manifest .dist/study/manifest_40.json --artifacts-root .dist/study/artifacts_full --taxonomy open --strategy few --no-skip-existing --summary-output .dist/study/manifest40_rerun_summary.few-open.json

python -m d4j_odc_pipeline study-drift  --prefix-dir .dist/study/artifacts_full/prefix --postfix-dir .dist/study/artifacts_full/postfix --manifest .dist/study/manifest_40.json
python -m d4j_odc_pipeline study-escape --prefix-dir .dist/study/artifacts_full/prefix --manifest .dist/study/manifest_40.json
python -m d4j_odc_pipeline study-ladder --prefix-dir .dist/study/artifacts_full/prefix --manifest .dist/study/manifest_40.json
```

**Cost:** 186 + 185 (177 + 2 retry attempts, see gotcha below) + 80 + 80 = 531
LLM calls, ~24 minutes wall-clock across the 4 `study-run` invocations. Well
inside a single key's ~1,500 RPD, let alone the 7-key rotation.

**Gotcha — transient per-bug LLM failure, not a pipeline bug:**
`scientific-closed`'s first pass completed 39/40 (`prefix_ok: 39`); `Jsoup_12`'s
prefix arm failed with `Could not parse a JSON object from the LLM response.`
(`parsing.py::extract_json_object` — the model's final turn didn't contain a
parseable JSON object). Its classification file was left at its pre-rerun
(stale) content rather than overwritten, since the write only happens on
success. A same-bug retry (`study-run` against a hand-built one-entry manifest,
`.dist/study/manifest_jsoup12_retry.json`, `--no-skip-existing`) failed
**again** with the identical error; a third attempt succeeded cleanly,
confirming this was LLM output flakiness for that one bug/condition, not a
structural problem with its evidence. Verified all 80/80 files (40 bugs × 2
arms) for `scientific-closed` carry a `created_at` timestamp from this run
before treating the condition as complete. Two operational lessons for future
reruns: (1) `study-run`'s per-bug failure handling degrades gracefully — one
bad bug doesn't abort the batch or corrupt the summary counts, but it also
silently leaves stale content in place, so **check `prefix_ok`/`postfix_ok`
against `total_entries` in the summary JSON, don't just check the process
exit code**; (2) there's no CLI flag to retarget a single bug from an
existing manifest — build a one-entry manifest by extracting the entry from
the original.

### Findings (effective n=44 — development-validation scale, still not final)

Comparing `analysis_40.json` / `taxonomy_coverage_40.json` /
`taxonomy_grounding_40.json` before (git `HEAD`, the 2026-07-09 run) vs. after
(this rerun):

| Metric (condition) | Before | After | Δ |
|---|---|---|---|
| Impact populated (few/scientific × both arms) | 0/176 | 176/176 | fixed is live |
| Impact distribution (prefix, all taxonomy-constrained) | n/a | Capability 84.1% (37/44), Reliability 15.9% (7/44) | only 2/13 categories used |
| **Impact** prefix↔postfix agreement (negative control) | n/a | 97.7% raw (43/44), κ=0.920 | new — see below |
| Type strict match (scientific-open, RQ3) | 81.8% (36/44) | 72.7% (32/44) | **−9.1 pts** |
| Type top-2 match | 97.7% (43/44) | 95.5% (42/44) | −2.3 pts |
| Type family match | 97.7% (43/44) | 93.2% (41/44) | −4.5 pts |
| Type Cohen's κ (scientific-open) | 0.726 | 0.601 | −0.125 |
| Type changed / drift rate | 18.2% (8/44) | 27.3% (12/44) | +9.1 pts |
| RQ2 escape rate (closed→open) | 0.0% | 0.0% | unchanged |
| RQ2 coverage rate | 100% | 100% | unchanged |
| RQ2 closed↔open shift κ (8-cat) | 0.709 | 0.668 | −0.041 |
| RQ2 shifted count | 8/44 | 9/44 | +1 |
| RQ4 vocabulary reduction ratio | 0.837 | 0.841 | ~unchanged |
| RQ4 `zero-free` unique labels | 43/44 | 44/44 | slightly more varied |

1. **Impact is fully populated and behaves exactly as the negative-control
   design predicted**: 97.7% prefix↔postfix agreement (κ=0.920) vs. Type's
   72.7% (κ=0.601) — Impact (opener, fix-independent per v5.2) stays stable
   across arms while Type (closer, fix-choice-dependent) genuinely drifts.
   This is the cleanest result of the rerun and directly supports the
   negative-control argument in `latex/jss/main.tex`. Impact is skewed hard
   toward Capability/Reliability (2 of 13 categories) — an honest limitation
   already flagged in the audit's Threats-to-Validity additions, not a
   surprise.
2. **Type prefix↔postfix agreement dropped, not improved — and this is the
   direction the audit predicted, not a regression.** The audit's finding 2
   was that leaked fix knowledge (modified-sources list, fix-era report text)
   was "softening RQ3/RQ5 prefix-vs-postfix contrast" — i.e. artificially
   inflating agreement by handing the prefix arm partial fix knowledge.
   Removing that leak should make the prefix arm a genuinely blind predictor
   again, and agreement dropping toward the true difficulty of blind
   prediction is exactly what happened, at a much more reliable n=44 (vs. the
   pilot's inconclusive n=6). **Do not read this as "the pipeline regressed"
   — read it as evidence the leak fix had a real, measurable effect.**
3. **The drop is not uniform** — 9 bugs flipped match→mismatch (`Cli_17`,
   `Cli_32`, `Compress_15`, `JacksonCore_24`, `JxPath_22`, `Lang_43`,
   `Lang_60`, `Math_34`, `Mockito_26`), 5 flipped mismatch→match (`Chart_10`,
   `Codec_3`, `Collections_21`, `Jsoup_12`, `Time_27`), netting 36→32. In most
   flips the **prefix** classification is what moved (postfix stayed put or
   moved less) — consistent with the sanitization change being prefix-arm-only
   by design. This has not been individually traced to confirm each flip's
   prefix payload actually contained a removed leak; it's the plausible
   mechanism given where the code changed, not a proven causal chain per bug.
4. **RQ2's headline (zero escapes to "Other") is untouched by the leak
   fix** — still 0/44 both before and after. That result was never
   leak-dependent, and this rerun corroborates it wasn't an artifact either.
5. **RQ4's taxonomy-grounding effect is untouched** (vocabulary reduction
   0.837→0.841, essentially flat) — collapsing free-form labels under a
   taxonomy is robust to the prior-removal, as expected (that fix targeted
   the instrument's *distributional* prior, not its vocabulary-narrowing
   mechanism).
6. **Lang-specific numbers are not reliable at this scale.** Only 3 Lang bugs
   exist in the effective 44 (`Lang_27`, `Lang_43`, `Lang_60`). Per-project
   Type κ for Lang swung **1.0 → −0.5** — driven by 2 of the 3 bugs
   (`Lang_43`, `Lang_60`) flipping from match to mismatch; with n=3, one or
   two flips produce wild kappa swings and this number should not be
   interpreted as "Lang got worse." This is the concrete argument for running
   the full 61-bug Lang corpus separately (already collected in
   `artifacts_full`, no re-collection needed) before drawing any Lang-specific
   conclusion for the supervisor.

**Do not cite any of this in the manuscript** — development-validation scale,
same status as every other number in `docs/JSS_HANDOFF.md`. Value here is
confirmatory: the audit fixes are live, they move the numbers in the
predicted direction at a much less noisy n=44, and the parts of the pipeline
that shouldn't have been leak-sensitive (RQ2 escape rate, RQ4 vocabulary
reduction) indeed didn't move.

---

## 2026-07-11 — Full Lang project run, all 5 valid conditions (manifest_lang61.json, 61 bugs)

Context: supervisor's specific interest is the Lang project; the 44-bug
dev-validation set above only contains 3 Lang bugs (too few for a reliable
per-project statistic — its own entry above shows Lang's κ swinging 1.0→−0.5
off 2 bug flips). Defects4J's Lang project has 61 non-deprecated bugs, all
already collected in `artifacts_full` (both arms) — no re-collection needed,
classification-only cost.

**Manifest built directly from the corpus, not via `study-plan`:**
`.dist/study/manifest_lang61.json` was hand-built by listing
`artifacts_full/prefix/Lang_*_prefix` (61 matches) and verifying `context.json`
exists in both arms for every one, rather than invoking `study-plan` (which
would call live Defects4J and risks a bug-list mismatch against what's
actually pre-collected, forcing an unplanned real collection). All 61 had
context already — zero collection calls.

**All 5 valid conditions run** (`docs/condition_model.md`'s full set — the
first time `few-closed` has ever been run in this study; the other 4 already
had 3 bugs — `Lang_27`, `Lang_43`, `Lang_60` — freshly classified from the
40-bug rerun above, which `--no-skip-existing`-less `study-run` correctly
auto-skipped rather than re-billed):

```bash
python -m d4j_odc_pipeline study-run --manifest .dist/study/manifest_lang61.json --artifacts-root .dist/study/artifacts_full --summary-output .dist/study/lang61_run_summary.scientific-open.json
python -m d4j_odc_pipeline study-run --manifest .dist/study/manifest_lang61.json --artifacts-root .dist/study/artifacts_full --taxonomy open   --strategy few        --summary-output .dist/study/lang61_run_summary.few-open.json
python -m d4j_odc_pipeline study-run --manifest .dist/study/manifest_lang61.json --artifacts-root .dist/study/artifacts_full --taxonomy free   --strategy zero       --summary-output .dist/study/lang61_run_summary.zero-free.json
python -m d4j_odc_pipeline study-run --manifest .dist/study/manifest_lang61.json --artifacts-root .dist/study/artifacts_full --taxonomy closed --strategy scientific --summary-output .dist/study/lang61_run_summary.scientific-closed.json
python -m d4j_odc_pipeline study-run --manifest .dist/study/manifest_lang61.json --artifacts-root .dist/study/artifacts_full --taxonomy closed --strategy few        --summary-output .dist/study/lang61_run_summary.few-closed.json
```

**Real pipeline bug found and fixed: `parsing.py::extract_json_object`
rejected valid-content LLM output that contained a literal unescaped
newline inside a JSON string value.** `Lang_41`'s prefix arm under
`zero-free` failed 3/3 times with the identical
`Could not parse a JSON object from the LLM response.` error — identical,
not just similar, because `zero-free`/single-sample calls run at
`temperature=0.0` (`pipeline.py::classify_bug_context`), so the model's
output is deterministic and blind retries can never succeed if the output
itself is malformed. Reproduced standalone (`load_context` +
`build_messages` + `LLMClient.complete` against the real context/prompt) and
found the model had embedded a raw `\n` byte inside its `"symptom"` string
field instead of escaping it — invalid per strict JSON (RFC 8259) but
recoverable. Fix: `json.JSONDecoder(strict=False)` in `extract_json_object`
(one line) — tolerates control characters inside string values without
weakening structural parsing. Verified against `tests/test_parsing.py` (2/2
pass) and the full suite (143/145, only the 2 pre-existing Windows/WSL-only
failures), then verified end-to-end: `Lang_41` classified cleanly on the next
attempt. **This bug is not Lang-specific or manifest-specific** — any bug in
the 854-corpus could trigger it in any future run (it depends on what the
model happens to write in a prose field, not on the bug's evidence content);
today's earlier runs (the pilot rerun, the 40-bug rerun) were checked and had
zero silently-swallowed failures of this kind before the fix landed — the
one real failure hit before this fix (`Jsoup_12`, `scientific-closed`) was
in the multi-turn agentic loop, where turn-to-turn API-level variation let a
retry eventually produce different (parseable) output; that mechanism
doesn't exist for single-shot conditions, which is exactly why `Lang_41`
couldn't self-resolve without the fix.

**Cost:** 249 (scientific-open, 58 new + 3 skipped) + 116 (few-open) + 116 + 3
(zero-free, incl. 2 failed + 1 successful `Lang_41` retry) + 244
(scientific-closed) + 122 (few-closed, all 61 new) = 850 calls for this run;
**1,381 calls total today** across both reruns. Still comfortably inside a
single key's ~1,500 RPD, and ~13% of the 7-key ~10,500/day aggregate.

### Results (n=61, Lang project only — most reliable project-level numbers produced so far)

Computed via `study-drift`/`study-escape`/`study-ladder` pointed at a
**symlink view** (`.dist/study/lang61_{prefix,postfix}_view/`, one symlink
per Lang bug folder back into `artifacts_full`) rather than
`artifacts_full/prefix` directly — `_discover_pairs` scans whichever
directory it's given non-recursively, and `artifacts_full` now holds
classifications for non-Lang bugs under the same tags (from the 40-bug
rerun), so scanning it directly would have mixed projects. No data was
copied, only symlinked; `--manifest` does not filter analysis scope in this
codebase (documented gotcha — worklist, not namespace), so this view trick is
the correct way to get a project-only cut of a shared artifact tree without
touching it.

```bash
python -m d4j_odc_pipeline study-drift  --prefix-dir .dist/study/lang61_prefix_view --postfix-dir .dist/study/lang61_postfix_view --manifest .dist/study/manifest_lang61.json --output .dist/study/analysis_lang61.json --report .dist/study/analysis_lang61.md
python -m d4j_odc_pipeline study-escape --prefix-dir .dist/study/lang61_prefix_view --manifest .dist/study/manifest_lang61.json --output .dist/study/taxonomy_coverage_lang61.json
python -m d4j_odc_pipeline study-ladder --prefix-dir .dist/study/lang61_prefix_view --manifest .dist/study/manifest_lang61.json --tags "zero-free,few-open,scientific-open,few-closed,scientific-closed" --output .dist/study/taxonomy_grounding_lang61.json
```

| Metric (scientific-open unless noted) | Value |
|---|---|
| Type strict match | 86.9% (53/61) |
| Type top-2 match | 100% (61/61) |
| Type family match | 100% (61/61) |
| Type Cohen's κ | 0.766 |
| Type changed / drift rate | 13.1% (8/61) |
| Type distribution (prefix) | Algorithm/Method 49.2%, Checking 45.9%, Assignment/Init 3.3%, Relationship 1.6% |
| Impact distribution (prefix) | Capability 70.5%, Reliability 27.9%, Serviceability 1.6% |
| Impact prefix↔postfix agreement | 95.1% (58/61), κ=0.890 |
| RQ2 coverage / escape rate (closed→open) | 100% / 0% |
| RQ2 shift κ (closed vs open, 8-cat) | 0.767 |
| RQ4 vocabulary reduction (5-tag ladder) | 0.870 |

1. **Lang's Type profile is narrower than the general corpus**: only 4 of 7
   ODC types appear at all, and Algorithm/Method + Checking alone account for
   95.1% (58/61). Whether that's a real property of Lang's bug population or
   an artifact of this instrument is not something a single project can
   answer — worth a cross-project comparison once other projects have n>30.
2. **The negative-control pattern holds at project scale, not just in
   aggregate**: Impact agreement (95.1%, κ=0.890) is well above Type
   agreement (86.9%, κ=0.766) — same direction as the 44-bug set, now on a
   cleaner single-project sample.
3. **n=61 makes Lang's numbers far more usable than the 44-set's n=3** — this
   was the actual point of the exercise. 86.9% strict match / κ=0.766 is a
   real, citable-scale project-level result (still development-validation
   status pending the confirmatory run, but no longer a small-n artifact).
4. `few-closed` ran for the first time anywhere in this study — no prior
   baseline to compare against, so no drift/before-after numbers for it here,
   only its contribution to the RQ4 ladder above.

**Do not cite any of this in the manuscript yet** — same development-
validation status as every other number in this log. The Lang-specific
numbers are more statistically usable than anything produced so far
project-scoped, but still pre-confirmatory-run.

---

## 2026-07-11 — Cross-condition drift/impact/ladder synthesis (44-set + Lang-61, all conditions)

Context: the runs above only ever computed `study-drift` for the *default*
condition (`scientific-open`) for each dataset. This pass fills in the other
conditions — `zero-free`, `few-open`, `scientific-closed` for both datasets,
plus `few-closed` for Lang-61 — so drift/impact can be compared across the
full condition space, not just one condition. Pure local computation, zero
LLM calls.

**Contamination guard:** by this point `artifacts_full` holds classifications
for the 44-set AND the 61 Lang bugs under the same tags (`zero-free`,
`few-open`, `scientific-open`, `scientific-closed`), since both reruns wrote
into the same shared tree. `study-drift`/`_discover_pairs` scans whichever
directory it's given non-recursively with no manifest-based filtering (the
`--manifest` flag only derives `expected_projects` — confirmed by reading
`analyze_batch_artifacts`'s signature directly, it takes no manifest/entries
parameter). Pointing it at `artifacts_full/prefix` directly for, say,
`zero-free` would now silently mix in the 58 new Lang bugs and produce a
102-bug analysis, not a clean 44-bug one. Fix: built a matching **44-set
symlink view** (`.dist/study/manifest44_{prefix,postfix}_view/`, 44 symlinks
each, union of `manifest_40.json` ∪ `manifest_pilot.json`) the same way the
Lang-61 view was built earlier, and ran every condition against the
appropriate view. Sanity-checked: `scientific-open` recomputed through the
44-set view reproduces `analysis_40.json` exactly (`type_changed: 12`,
matching the existing stored file) — confirms the view approach doesn't
alter results, only scope.

```bash
V44=.dist/study/manifest44_prefix_view; VP44=.dist/study/manifest44_postfix_view
VL=.dist/study/lang61_prefix_view; VPL=.dist/study/lang61_postfix_view

python -m d4j_odc_pipeline study-drift --prefix-dir $V44 --postfix-dir $VP44 --manifest .dist/study/manifest_40.json --taxonomy free   --strategy zero       --output .dist/study/analysis_44_zero-free.json         --report .dist/study/analysis_44_zero-free.md
python -m d4j_odc_pipeline study-drift --prefix-dir $V44 --postfix-dir $VP44 --manifest .dist/study/manifest_40.json --taxonomy open   --strategy few        --output .dist/study/analysis_44_few-open.json          --report .dist/study/analysis_44_few-open.md
python -m d4j_odc_pipeline study-drift --prefix-dir $V44 --postfix-dir $VP44 --manifest .dist/study/manifest_40.json --taxonomy closed --strategy scientific --output .dist/study/analysis_44_scientific-closed.json  --report .dist/study/analysis_44_scientific-closed.md

python -m d4j_odc_pipeline study-drift --prefix-dir $VL  --postfix-dir $VPL  --manifest .dist/study/manifest_lang61.json --taxonomy free   --strategy zero       --output .dist/study/analysis_lang61_zero-free.json        --report .dist/study/analysis_lang61_zero-free.md
python -m d4j_odc_pipeline study-drift --prefix-dir $VL  --postfix-dir $VPL  --manifest .dist/study/manifest_lang61.json --taxonomy open   --strategy few        --output .dist/study/analysis_lang61_few-open.json         --report .dist/study/analysis_lang61_few-open.md
python -m d4j_odc_pipeline study-drift --prefix-dir $VL  --postfix-dir $VPL  --manifest .dist/study/manifest_lang61.json --taxonomy closed --strategy scientific --output .dist/study/analysis_lang61_scientific-closed.json --report .dist/study/analysis_lang61_scientific-closed.md
python -m d4j_odc_pipeline study-drift --prefix-dir $VL  --postfix-dir $VPL  --manifest .dist/study/manifest_lang61.json --taxonomy closed --strategy few        --output .dist/study/analysis_lang61_few-closed.json       --report .dist/study/analysis_lang61_few-closed.md

python -m d4j_odc_pipeline study-ladder --prefix-dir $V44 --manifest .dist/study/manifest_40.json --tags "zero-free,few-open,scientific-open,scientific-closed" --output .dist/study/taxonomy_grounding_44_extended.json
```

### Findings

| Condition | 44-set strict / κ | Lang-61 strict / κ | 44-set impact κ | Lang-61 impact κ |
|---|---|---|---|---|
| zero-free | 11.4% / 0.111 | 24.6% / 0.240 | n/a (not prompted) | n/a |
| few-open | 79.5% / 0.651 | 78.7% / 0.608 | 0.835 | 0.836 |
| scientific-open | 72.7% / 0.601 | 86.9% / 0.766 | 0.920 | 0.890 |
| scientific-closed | 68.2% / 0.516 | 82.0% / 0.687 | 0.808 | 0.886 |
| few-closed | not run | 75.4% / 0.543 | not run | 0.762 |

1. **No single condition is "best" across both datasets** — `few-open` has
   the highest Type agreement on the 44-set (79.5%); `scientific-open` is
   clearly highest on Lang-61 (86.9%). Condition ranking is corpus-dependent;
   resist picking a universal "winner" from one dataset's ordering.
2. **Open taxonomy beats its Closed counterpart on Type agreement, 3/3 times
   it's directly comparable**: `few-open`>`few-closed` (Lang: 78.7% vs
   75.4%), `scientific-open`>`scientific-closed` (44-set: 72.7% vs 68.2%;
   Lang: 86.9% vs 82.0%). Forcing the closed 7-type taxonomy under two
   different evidence sets (prefix vs postfix) more often yields two
   *different* forced choices than leaving an "Other" escape open.
3. **Impact's κ beats Type's κ in all 8 measured condition/dataset cells**,
   not just the `scientific-open` cell reported earlier — this is now the
   best-supported finding of the whole audit follow-up. `few-closed` has the
   *weakest* Impact reliability of the four impact-bearing conditions
   (κ=0.762, Lang) — plausibly the least-grounded prompt combination (no
   open-taxonomy escape, no scientific-loop evidence probing), not
   independently verified further.
4. **`zero-free`'s numbers are not comparable to the others** — `family_match`
   reads as 100% in the raw output for both datasets, but that's a
   computation artifact: free-text labels have no ODC family, so
   `prefix_family=None`/`postfix_family=None` and the comparator counts
   `None == None` as a match. Ignore `zero-free` family/top-2 columns; its
   strict-match numbers alone are usable, and even those mostly measure
   text-rephrasing noise, not conceptual disagreement.
5. **Vocabulary reduction is condition-agnostic**: 0.841 (44-set, 3- or 4-tag
   ladder — identical either way) vs 0.870 (Lang-61, 5-tag,
   `taxonomy_grounding_lang61.json`, computed in the previous entry). Doesn't
   matter which taxonomy-constrained condition is compared against
   `zero-free` — the collapse from near-one-label-per-bug down to 4-5 total
   labels is essentially the same size regardless.

**scientific-open Type distribution, prefix vs postfix** (the condition drilled
into in chat afterward):

44-set (n=44): Checking 43.2%→31.8%, Algorithm/Method 40.9%→38.6%,
Function/Class/Object 9.1%→13.6%, Assignment/Initialization 6.8%→13.6%,
Interface/O-O Messages 0%→2.3%. 12 bugs drifted; 8 of the 12 started as
Checking in prefix (`Cli_32`, `Closure_140`, `JacksonCore_24`, `JacksonXml_3`,
`Jsoup_28`, `JxPath_22`, `Lang_60`, `Math_34`), matching the aggregate drop.

Lang-61 (n=61): Algorithm/Method 49.2%→45.9%, Checking 45.9%→45.9%
(unchanged count), Assignment/Initialization 3.3%→6.6%, Relationship
1.6%→1.6%. 8 bugs drifted (`Lang_21`, `Lang_26`, `Lang_29`, `Lang_34`,
`Lang_43`, `Lang_53`, `Lang_60`, `Lang_61`) — split evenly 3-and-3 between
Checking↔Algorithm/Method in both directions, plus `Lang_26`/`Lang_29` both
independently make the identical Algorithm/Method→Assignment/Initialization
move (not investigated further — worth a manual look if there's a shared fix
pattern).

**scientific-open Impact distribution, prefix vs postfix**: 44-set Capability
84.1%→81.8%, Reliability 15.9%→18.2%, 1 disagreement (`Gson_7`,
Capability→Reliability). Lang-61 Capability 70.5%→65.6%, Reliability
27.9%→32.8%, Serviceability 1.6%→1.6% (unchanged), 3 disagreements (`Lang_35`,
`Lang_56`, `Lang_65`, all Capability→Reliability). **Every Impact
disagreement in both datasets moves the same direction (Capability→
Reliability) — never the reverse, never involving Serviceability.** Part of
why Impact's κ is so much higher than Type's: not just fewer disagreements,
but the ones that exist are clustered on one transition instead of scattered.

**Also from this session**: found and fixed a real, non-corpus-specific
pipeline bug while running the Lang-61 conditions —
`parsing.py::extract_json_object` used strict-mode `json.JSONDecoder()`,
which rejects LLM output containing a literal unescaped control character
(e.g. a raw newline) inside a JSON string value. `Lang_41`'s prefix arm under
`zero-free` failed identically 3/3 times (deterministic at temperature=0, so
retries alone could never fix it). Fixed with `JSONDecoder(strict=False)`;
regression test added (`tests/test_parsing.py::test_extract_json_object_tolerates_unescaped_control_character`).
Full write-up in the "Full Lang project run" entry above.

**Do not cite any of this in the manuscript** — same development-validation
status as everything else in this log.
