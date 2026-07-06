# Study Execution Log

Running record of how classifications were actually executed — commands, environment,
results, and gotchas. Append a section per run so agents and teammates can reproduce
or resume without re-deriving anything. Newest at the bottom.

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
