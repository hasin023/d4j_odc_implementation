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
