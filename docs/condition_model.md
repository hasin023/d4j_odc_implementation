# The Condition Model (authoritative)

**This document is the single source of truth for how classifications are
configured.** If any other document (including older specs, logs, or the frozen
`iut_submissions/`) contradicts this file, THIS file wins. Adopted 2026-07-07;
rationale in §4.

## 1. The two variables

Every classification is a coordinate `(taxonomy, strategy)`:

| Variable | Levels | Default |
|---|---|---|
| `--taxonomy` | `free` — no taxonomy; the model answers in its own words · `closed` — the 7 ODC types, forced choice (closed-set) · `open` — 7 + "Other" escape category (open-set) | **`open`** |
| `--strategy` | `zero` — zero-shot: no taxonomy, no worked examples (the unstructured baseline) · `few` — few-shot single call: taxonomy + diagnostic decision tree + 5 worked classification examples (the strong static prompt) · `scientific` — the enforced scientific loop (`agent.py`): hypothesis → prediction → probe → observation turns over held-back `context.json` evidence, max 6 turns, full transcript persisted | **`scientific`** |

**The default pipeline — for BOTH prefix and postfix evidence — is
`scientific-open`.**

## 2. Valid conditions (5, not 9)

`zero` is taxonomy-free **by definition** (a zero-shot prompt contains no label
space), and `few`/`scientific` need a label space to classify into. The CLI
enforces this (`odc.validate_condition`):

```
zero-free            the unstructured baseline (retired name: "naive")
few-closed           taxonomy forced-choice, strong static prompt
few-open             taxonomy + escape hatch, strong static prompt
scientific-closed    forced-choice, enforced loop
scientific-open      escape hatch, enforced loop     ← THE DEFAULT
```

Invalid and rejected: `closed-zero`, `open-zero`, `free-few`, `free-scientific`.

## 3. Retired concepts (do not resurrect)

| Retired | Why | Where it went |
|---|---|---|
| `--prompt-style naive\|direct\|scientific` | bundled two variables | tombstoned flag |
| `--reasoning zero\|scientific\|agentic` | "scientific" meant *narrated* single-shot — a level the pilot showed adds nothing (0/6 label changes vs zero-shot with taxonomy) | tombstoned flag; see §4 |
| the **narrated single-shot "scientific"** condition | narration ≠ the method; only *enforcement* changed answers (pilot: 2/6, both toward the oracle) | its full prompt (protocol text + tree + examples) **lives on as the `few` strategy** — it is the strongest static baseline, and the name is now accurate (it literally contains few-shot worked examples) |
| the `direct` cell (taxonomy, no examples) | redundant middle rung; pilot: identical answers to the full static prompt | dropped |
| `study-baseline` / `study-naive` / `study-coverage` | one command per condition doesn't scale | `study-run --taxonomy X --strategy Y` |
| `study-classify` (2026-07: prefix-only shortcut sibling to `study-run`) | had no remaining purpose once `study-run` was used for every condition (prefix+postfix, "for free" relative to what study-classify did); its RQ2 trigger and the dead RQ4 ladder engine needed real homes anyway | `study-run` for the classification itself; `study-escape` (RQ2) and `study-ladder` (RQ4) for the analyses that used to live inside its CLI handler |

## 4. Rationale (the justifications to cite)

1. **Open by default (supervisor's position):** bugs from arbitrary domains
   must not be force-fitted into a fixed 7-type schema. A forced choice
   manufactures false certainty; the "Other" escape (with mandatory
   `other_justification`, `nearest_type`, `other_confidence`) keeps every
   classification honest and makes the taxonomy's coverage *measurable*
   (escape rate). If a significant share of bugs escapes, that is a finding —
   and the seed of a future taxonomy-adaptation study (cf. the space-systems
   ODC study that found ~32% unclassifiable and proposed adaptations).
   The closed taxonomy remains available for the RQ2 comparison pass and for
   comparability with prior 7-type ODC literature.
2. **Scientific = the loop (pilot evidence, 2026-07-06):** the narrated
   protocol changed 0/6 labels vs zero-structure prompting, while the enforced
   loop changed 2/6 — both times agreeing with the oracle-informed postfix
   reference where the static prompt did not, and probing the actually-buggy
   class first in 6/6 bugs. The scientific method is something the model must
   *do* (commit prediction → receive exogenous observation), not *recite*.
   Hence "scientific strategy" now means the loop, and only the loop.
3. **`few` keeps the strongest static prompt:** the loop must outperform the
   best single-call prompt (taxonomy + tree + worked examples), not a
   handicapped one — otherwise the comparison is rigged in the loop's favor.
4. **Postfix defaults to the same condition:** the reference arm should be the
   best-informed configuration of the same instrument. (A reference-sensitivity
   check — few vs scientific on postfix, eval subset — is queued to confirm
   the reference is robust to this choice.)

## 5. Artifacts

- Filenames: `classification.<strategy>-<taxonomy>.json`, `report.<tag>.md`,
  `checkpoint.{pairs|prefix}.<tag>.json` — always explicit, all conditions
  side by side in the bug folder next to the shared read-only `context.json`.
- Result fields: `taxonomy_mode`, `strategy`, plus `turns`/`llm_calls_used`/
  `termination_reason`/`loop_duration_seconds`/`probe_misses` (scientific),
  `consistency_*` (self-consistency), `other_*` (open escapes).
  ⚠️ The `impact` field (ODC opener attribute) was REMOVED from the pipeline on
  2026-09-10 — no RQ depended on it and the attribute was not sufficiently
  justified. Artifacts written before that date still carry `impact` and
  `inferred_impact`; readers use raw `.get()` so they load unchanged.

**Model is a third, orthogonal axis (added 2026-08-10), never part of the
5-combo `(taxonomy, strategy)` validation above.** Running the same
condition under a second `--provider`/`--model` against the same
`--artifacts-root` does not overwrite or collide with the first model's
files: `odc.resolve_effective_tag` (used by `study-run`, and by
`study-drift`/`study-escape` when given the same `--provider`/`--model`)
checks the bare tag's `checkpoint.pairs.<tag>.json` — no checkpoint, or one
with no `model`/`provider` keys (every checkpoint written before this
existed, including the whole committed corpus), keeps the bare filenames
forever; a *different* recorded `(provider, model)` gets a suffixed tag
instead: `classification.<tag>.<provider>-<model-slug>.json`. First-model
runs, resumes with the same model, and every pre-existing artifact are
therefore byte-for-byte unaffected by this mechanism — it only activates
when a second distinct model actually shows up. See `odc.py`'s
`model_slug`/`resolve_effective_tag`/`resolve_effective_tag_from_root`
docstrings for the exact rules. Resuming a model-scoped run must pass the *same*
`--provider`/`--model` string each time — a reformatted/typo'd model string
now starts a new suffixed run instead of resuming, unlike before this axis
existed.

⚠️ **Artifacts written before 2026-07-07 use the OLD tokens** (`reasoning`
field; `*-scientific` files there mean the *narrated single-shot*, and
`*-agentic` files mean the loop). They are pilot-era exploratory data — do not
mix them with new runs; regenerate instead. See `docs/study_execution_log.md`.

⚠️ **Artifacts written before 2026-07-10 predate the ODC alignment audit**:
their pre-fix payload was not sanitized (the modified-sources oracle and, for
JIRA-tracked projects, fix-era report content leaked into the prefix arm), the
system prompt asserted an expected type distribution, and `impact` is absent
or came from the old unvalidated keyword heuristic (`inferred_impact`, a
list). Do not mix with post-audit runs; regenerate instead. See
`docs/odc_alignment_audit.md` §5 and §7.

## 6. Study recipes

`study-classify` was retired 2026-07 (tombstoned, redirects to `study-run`).
Every condition — including the RQ4 ablation arms — now goes through
`study-run` (prefix+postfix, any of the 5 valid conditions via
`--taxonomy`/`--strategy`), reusing the same `--artifacts-root` so evidence
(`context.json`) is shared across conditions. RQ2 and RQ4's cross-condition
analyses are their own commands, `study-escape` and `study-ladder`, rather
than a side effect of a classification command.

```bash
# The default pipeline: paired prefix+postfix, scientific-open
python -m d4j_odc_pipeline study-run      --manifest m.json --artifacts-root <root>

# RQ2 comparison pass: run the closed pass too, then compare closed vs open
python -m d4j_odc_pipeline study-run      --manifest m.json --artifacts-root <root> --taxonomy closed
python -m d4j_odc_pipeline study-escape   --prefix-dir <root>/prefix --strategy scientific

# RQ4 ablation ladder: run each rung (prefix+postfix; only prefix is used by
# the ladder, but running both means the same data also feeds RQ1/RQ3/RQ5)
python -m d4j_odc_pipeline study-run      --manifest m.json --artifacts-root <root> --taxonomy free --strategy zero
python -m d4j_odc_pipeline study-run      --manifest m.json --artifacts-root <root> --taxonomy open --strategy few
python -m d4j_odc_pipeline study-ladder   --prefix-dir <root>/prefix --tags zero-free,few-open,scientific-open

# Drift analysis defaults to the pipeline default condition (scientific-open)
python -m d4j_odc_pipeline study-drift    --prefix-dir <root>/prefix --postfix-dir <root>/postfix
```

## 7. RQ mapping (core questions unchanged; operationalization current)

| RQ (core question) | Conditions consumed | Command |
|---|---|---|
| RQ1 type distribution | `scientific-open` prefix (the honest 8-bin distribution) | `study-drift` (or `study-run`'s inline stats) |
| RQ2 taxonomy coverage | `closed-*` vs `open-*` passes, same strategy (escape rate, shift-κ, KL, escape audit) | `study-escape` |
| RQ3 pre-fix accuracy | prefix vs the `scientific-open` postfix reference | `study-drift` |
| RQ4 what does structure contribute | `zero-free` → `few-open` → `scientific-open` ladder (or any tag sequence) | `study-ladder` |
| RQ5 pre/post divergence | prefix vs postfix under `scientific-open` (or any condition) | `study-drift` |
