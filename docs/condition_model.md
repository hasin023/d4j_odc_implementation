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
`open-scientific`.**

## 2. Valid conditions (5, not 9)

`zero` is taxonomy-free **by definition** (a zero-shot prompt contains no label
space), and `few`/`scientific` need a label space to classify into. The CLI
enforces this (`odc.validate_condition`):

```
free-zero            the unstructured baseline (retired name: "naive")
closed-few           taxonomy forced-choice, strong static prompt
open-few             taxonomy + escape hatch, strong static prompt
closed-scientific    forced-choice, enforced loop
open-scientific      escape hatch, enforced loop     ← THE DEFAULT
```

Invalid and rejected: `closed-zero`, `open-zero`, `free-few`, `free-scientific`.

## 3. Retired concepts (do not resurrect)

| Retired | Why | Where it went |
|---|---|---|
| `--prompt-style naive\|direct\|scientific` | bundled two variables | tombstoned flag |
| `--reasoning zero\|scientific\|agentic` | "scientific" meant *narrated* single-shot — a level the pilot showed adds nothing (0/6 label changes vs zero-shot with taxonomy) | tombstoned flag; see §4 |
| the **narrated single-shot "scientific"** condition | narration ≠ the method; only *enforcement* changed answers (pilot: 2/6, both toward the oracle) | its full prompt (protocol text + tree + examples) **lives on as the `few` strategy** — it is the strongest static baseline, and the name is now accurate (it literally contains few-shot worked examples) |
| the `direct` cell (taxonomy, no examples) | redundant middle rung; pilot: identical answers to the full static prompt | dropped |
| `study-baseline` / `study-naive` / `study-coverage` | one command per condition doesn't scale | `study-classify --taxonomy X --strategy Y` |

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

- Filenames: `classification.<taxonomy>-<strategy>.json`, `report.<tag>.md`,
  `checkpoint.{pairs|prefix}.<tag>.json` — always explicit, all conditions
  side by side in the bug folder next to the shared read-only `context.json`.
- Result fields: `taxonomy_mode`, `strategy`, plus `turns`/`llm_calls_used`
  (scientific), `consistency_*` (self-consistency), `other_*` (open escapes).

⚠️ **Artifacts written before 2026-07-07 use the OLD tokens** (`reasoning`
field; `*-scientific` files there mean the *narrated single-shot*, and
`*-agentic` files mean the loop). They are pilot-era exploratory data — do not
mix them with new runs; regenerate instead. See `docs/study_execution_log.md`.

## 6. Study recipes

```bash
# The default pipeline: paired prefix+postfix, open-scientific
python -m d4j_odc_pipeline study-run      --manifest m.json --artifacts-root <root>

# RQ2 comparison pass (closed) + auto coverage metrics happen via:
python -m d4j_odc_pipeline study-run      --manifest m.json --artifacts-root <root> --taxonomy closed
python -m d4j_odc_pipeline study-classify --manifest m.json --artifacts-root <root> --taxonomy open   # if closed ran first

# Ablation arms (prefix-only, reuse contexts)
python -m d4j_odc_pipeline study-classify --manifest m.json --artifacts-root <root> --taxonomy free   --strategy zero
python -m d4j_odc_pipeline study-classify --manifest m.json --artifacts-root <root> --taxonomy open   --strategy few

# Analysis defaults to the pipeline default condition (open-scientific)
python -m d4j_odc_pipeline study-analyze  --prefix-dir <root>/prefix --postfix-dir <root>/postfix
```

## 7. RQ mapping (core questions unchanged; operationalization current)

| RQ (core question) | Conditions consumed |
|---|---|
| RQ1 type distribution | `open-scientific` prefix (the honest 8-bin distribution) |
| RQ2 taxonomy coverage | `closed-*` vs `open-*` passes (escape rate, shift-κ, KL, escape audit) |
| RQ3 pre-fix accuracy | prefix vs the `open-scientific` postfix reference |
| RQ4 what does structure contribute | `free-zero` → `open-few` → `open-scientific` ladder |
| RQ5 pre/post divergence | prefix vs postfix under `open-scientific` |
