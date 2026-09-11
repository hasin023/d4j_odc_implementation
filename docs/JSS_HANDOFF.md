# JSS Paper Handoff — Pipeline, Analysis, RQs, Results

> **Read this file first.** It is the single entry point for drafting the JSS
> paper: what the pipeline does, how each RQ is computed, the exact RQ
> wording, and the results produced so far. Everything below is current as of
> 2026-07-10. Where a claim needs more depth than fits here, it points to the
> specific doc that has it — you should not need to go doc-hunting.

**`docs/odc_alignment_audit.md` (new, 2026-07-10, addendum 2026-08-16) is the
ODC v5.2 alignment audit** — the corrected Defects4J-artifact→ODC-attribute
mapping, the Impact opener attribute (now first-class and v5.2-grounded), and
the pre-fix evidence-leak fixes described in the status flag below. Read it
before writing the paper's mapping/Impact/threats-to-validity sections;
`latex/jss/main.tex` already reflects it. Its §9 addendum (2026-08-16)
quantifies the Trigger retrospective-reproduction claim (33/40 sampled
trigger tests postdate the buggy revision, corroborated by a peer-reviewed
MSR 2025 paper) and reframes Age from "not in the evidence set" to "not
currently extracted, but recoverable via git blame/SZZ" — this is the
grounding evidence behind the JSS paper's §2.3 draft.

**`docs/related_work_literature_leads.md` (new, 2026-08-15) holds pending
related-work fixes and citation candidates** — a citation misattribution in
the current SVM/Naive-Bayes sentence, a wrong ODC Source value in the new
`tab:odc-attributes` table, and ~15 new candidate citations (the LSTM ODC
paper, memorization-advantage rebuttal, agentic-loop analogues, etc.) from a
two-agent literature survey. Not yet acted on — read before resuming work on
`latex/jss/sections/03_related_work.tex`.

## Status flag (read before citing any number below)

**Uncommitted.** All code and doc changes described here exist only in the
local working tree — nothing has been pushed or committed yet.

**No result below is final.** Both runs described in §4 are development/
validation runs (n=6 and n=44), used to confirm the pipeline and its
analysis layer produce *correct* numbers — not to produce numbers for the
paper. The RQ2/RQ4 escape-rate and vocabulary-reduction findings in
particular are directional signals at this scale, not defensible estimates.
A confirmatory run (recommended 68-100+ bugs, see §4) is still needed before
any number here goes into a manuscript table.

**§4's numbers additionally predate the 2026-07-10 audit fixes** and must not
be reused even directionally without rerunning: the pre-fix arm leaked the
modified-sources oracle (852/854 bugs) and, for JIRA-tracked projects,
fix-era report discussion (~98% of JIRA reports); the system prompt asserted
an expected type distribution that RQ1 then measured; and Impact was an
unvalidated, ODC-blind heuristic (present in 1/44 classifications) rather than
today's v5.2-taught single-select. All four are fixed in the pipeline; §4 is
kept only as a record that the analysis *layer* itself produced well-formed
output. See `docs/odc_alignment_audit.md` §5 for the full list of what these
numbers taint and why. The confirmatory run should use the current code.

**Both the 6-bug pilot and the 44-bug dev-validation set have since been
rerun on the post-audit code** (all 4 conditions, both arms) — see
`docs/study_execution_log.md`'s "2026-07-10/11 — Pilot rerun..." and
"2026-07-11 — 40-bug dev-validation rerun..." entries for the full before/
after numbers. **§4 below still shows the old, pre-audit numbers** — the
reruns updated `analysis_40.json`/`taxonomy_coverage_40.json`/
`taxonomy_grounding_40.json` and the pilot's artifacts in place, but §4's
prose/tables have not yet been rewritten to match; do not quote §4 without
cross-checking the execution log's before/after tables first. Headline from
the 44-bug rerun: Impact is now fully populated (176/176) and its
prefix↔postfix agreement (97.7%, κ=0.920) is far higher than Type's (72.7%,
κ=0.601) — confirming the negative-control design. Type prefix↔postfix
agreement **dropped** 9.1 points (81.8%→72.7%) post-fix — the direction the
audit predicted (leaked fix knowledge was inflating agreement), not a
regression. RQ2's zero-escape-rate and RQ4's vocabulary-reduction findings
were unchanged, as expected (neither was leak-dependent). Lang-specific
numbers were unreliable at n=3 (per-project κ swung 1.0→−0.5 on 2 bug flips).

**The full 61-bug Lang-only run (supervisor's specific interest) is now
done** — see `docs/study_execution_log.md`'s "Full Lang project run, all 5
conditions" and "Cross-condition drift/impact/ladder synthesis" entries.
Lang's Type strict match is 86.9% (κ=0.766, scientific-open) — far more
usable than the n=3 figure above. Impact prefix↔postfix agreement beat Type
agreement in every one of the 8 condition/dataset combinations measured (not
just scientific-open), the strongest evidence yet for the negative-control
design. One real pipeline bug was found and fixed while running this
(`parsing.py::extract_json_object` rejected LLM output containing an
unescaped control character inside a JSON string — deterministic at
temperature=0, so it could never self-resolve via retry without the fix);
regression test added, not corpus-specific, applies to any future run.

---

## 1. Pipeline

A research pipeline that collects pre-fix bug evidence from Defects4J and
classifies it into ODC (Orthogonal Defect Classification) defect types via
an LLM, producing machine-readable artifacts for evaluation.

**Two evidence modes:**
- **pre-fix** (default) — realistic classification from buggy code + failing
  tests only. As of 2026-07-10, `bug_info`/bug-report content are sanitized
  in this arm only (fix-derived sections stripped at payload-build time,
  `context.json` untouched) so the arm contains no fix knowledge — see
  `docs/odc_alignment_audit.md` §7 for the invariant this establishes.
- **post-fix** (`--include-fix-diff`) — injects the real buggy→fixed diff as
  oracle information; used as the reference arm for RQ3/RQ5. `bug_info`/report
  are left untouched here, since this arm legitimately knows the fix.

**`docs/suspicious_frame_selection.md` (new, 2026-08-10)** covers a
different axis than the audit above: how `suspicious_frames`/`coverage` are
selected (stack-trace frames + trigger-test coverage union, not stack trace
alone — fixes a case where the buggy class never appears in any stack
trace), why bug-report JSON parsing was cleaned up (decoded entities,
dropped opaque tracker-comment ids), and the full list of what
`_context_payload` trims from `context.json` before it reaches the LLM
prompt. Read it before describing evidence-selection methodology in the
paper.

**`docs/llm_prompting_architecture.md` (new, 2026-08-10)** is the exact,
field-by-field inventory of what's sent to the LLM per strategy
(`zero`/`few`/`scientific`, including the agentic loop's 5 probes) plus the
literature-and-code-grounded justification for the system/user message
split (Instruction Hierarchy paper, ChatML, prompt caching, and how our own
Gemini/Groq/OpenRouter integrations structurally enforce it). Read it before
writing the prompting-methodology section of the paper.

**`docs/llm_model_selection.md` (new, 2026-08-10)** is the free-tier model
tier list and per-strategy model pairing research — read it before choosing
which model(s) back a study-run, and before writing a "models used" section
in the paper. Also covers the model axis added to the artifact scheme
(`docs/condition_model.md` §5): running a strategy under 2 models for the
same condition is now collision-free.

**Impact (ODC opener attribute) was REMOVED from the pipeline on 2026-09-10.**
It is no longer taught in any prompt, no longer in the response schema, no
longer written to `classification.*.json`, and the three `study-drift` Impact
analyses (distribution, impact×type cross-tab, stability) are gone along with
the three Impact tabs in `scripts/reports/generate_combined_report.py`.

Reason: the attribute was not sufficiently justified, and **no RQ depended on
it** — all five RQs are Defect Type only. Impact had been a descriptive
companion to RQ1 and an optional noise-floor reading for RQ5's drift, wired
into `study-drift`'s output with no RQ of its own. The only thing lost is that
optional RQ5 discussion point; if a reviewer later wants a noise baseline,
repeated same-evidence-mode runs answer it better than a fix-independent attribute does.

⚠️ `docs/odc_alignment_audit.md` §6 still describes Impact as first-class and
is now stale on that point — the rest of that document (the attribute mapping,
the pre-fix leak fixes, the §9 Trigger/Age addendum) is unaffected. Artifacts
written before 2026-09-10 still carry `impact`/`inferred_impact`; every reader
uses raw `.get()`, so they load unchanged.

**Every classification is a coordinate of two independent condition
variables** (full spec: `docs/condition_model.md`, authoritative — read it
before describing the experimental design in the paper):
- `--taxonomy free|closed|open` — free = the model's own words; closed = the
  7 canonical ODC types forced; open = 7 + an "Other" escape category with
  mandatory justification. **Default: open.**
- `--strategy zero|few|scientific` — zero = zero-shot, no taxonomy, no
  examples; few = few-shot single call (taxonomy + diagnostic tree + worked
  examples); scientific = the enforced hypothesis→prediction→probe→
  observation loop (AutoSD-inspired), up to 6 turns. **Default: scientific.**

Only 5 combinations are valid (CLI-enforced):
`zero-free`, `few-closed`, `few-open`, `scientific-closed`, `scientific-open`.
Filenames are always condition-tagged: `classification.<strategy>-<taxonomy>.json`.

**Batch/study CLI** (as of the 2026-07-08 redesign — full reference:
`docs/USAGE.md`):
- `study-plan` — generate a balanced bug manifest (target bug count,
  minimum bugs per project).
- `study-run` — classify prefix+postfix for a manifest, ONE condition at a
  time (any of the 5 above). Evidence (`context.json`) is collected once per
  bug and reused across every condition sharing an `--artifacts-root`.
- `study-drift` — cross-artifact prefix/postfix drift analysis for ONE
  condition (backs RQ1, RQ3, RQ5). Renamed from `study-analyze`.
- `study-escape` — RQ2: taxonomy-coverage/escape-rate between the closed and
  open passes of one strategy.
- `study-ladder` — RQ4: ablation-ladder metrics across an ordered list of
  condition tags (default `zero-free,few-open,scientific-open`).
- `study-export` — LaTeX tables + CSV for the above.

`study-classify`/`study-analyze` (old names) are retired — tombstoned,
redirect to `study-run`/`study-drift`. If you see either name in an older
doc, treat it as historical, not current.

**Data already collected:** `.dist/study/artifacts_full/` holds
**854 prefix + 854 postfix `context.json`** files — essentially the full
non-deprecated Defects4J benchmark (17 projects) — pre-collected and
git-tracked. Any new study manifest drawn from Defects4J is very likely
already covered, so re-running classification under a new/changed prompt
costs **zero** Defects4J checkout/test time — only LLM call time.

---

## 2. Analysis (how each RQ's numbers are actually computed)

Engines live in `d4j_odc_pipeline/analysis.py` and `comparison.py`. The
authoritative RQ→command→engine mapping is `docs/condition_model.md` §7;
summarized here:

| RQ | Command | Engine function(s) | What it needs |
|---|---|---|---|
| RQ1 | `study-drift` | `compute_type_distribution` | `scientific-open` prefix classifications |
| RQ2 | `study-escape` | `compute_coverage_metrics` | closed + open passes, same strategy |
| RQ3 | `study-drift` | `compute_per_type_metrics`, `compute_cohens_kappa` | `scientific-open` prefix vs postfix pairs |
| RQ4 | `study-ladder` | `compute_taxonomy_grounding_metrics` | prefix-only, N ordered condition tags |
| RQ5 | `study-drift` | drift/transition logic + `compute_per_project_kappa` | `scientific-open` prefix vs postfix pairs |

**Important provenance note for whoever writes the methods section:** RQ1,
the per-type precision/recall/F1 half of RQ3, and RQ5's per-project kappa
were **not actually wired into `study-drift`'s output until 2026-07-08/09**
— the functions existed and were unit-tested, but `study-drift`'s engine
(`analyze_batch_artifacts`) never called them, so earlier exports of these
three would have been silently empty or wrong (confirmed by direct
inspection, not theoretical). This is now fixed and covered by regression
tests (`tests/test_batch.py`). If any *earlier* exported table for type
distribution, per-type F1, or per-project kappa exists anywhere, discard it
and regenerate — it predates the fix.

Citable methodology/defense prose (statistical choices, literature backing,
threats to validity):
- `docs/eval_defence.md` — the 3-pillar defense for pre/post-fix divergence,
  4-tier accuracy framework, literature references.
- `docs/details_of_RQ2.md` and `docs/RQ2_ODC_Coverage_Analysis.md` — full
  methodological argument for the closed/open two-pass RQ2 design, why
  Cohen's κ, academic backing and counter-evidence. The two overlap;
  `details_of_RQ2.md` is the tighter version, `RQ2_ODC_Coverage_Analysis.md`
  has more depth if you need it.
- `docs/odc_doc.md` — the full IBM ODC v5.2 taxonomy reference, for
  background/related-work sections.
- `docs/Research Paper Roadmap_ Defect Classification.md` — related-work
  narrative and manuscript-structuring guidance (no RQ numbering
  dependency, safe to use as-is).

**Do not pull methodology from:** `docs/METHODOLOGY.md`,
`docs/END_TO_END_RQs.md`, `docs/classification_engine_plan.md`,
`docs/two_variable_refactor_spec.md` — all four are explicitly banner-marked
stale/superseded in their own text (old RQ numbering RQ1.1/RQ2.1/etc., old
command names, or fully superseded design docs). `docs/ARCHITECTURE.md` is
partially stale (self-flagged) — its classification-flow diagram/prompt-style
content is the still-stale part; its evidence-collection and ODC-mapping
sections were updated 2026-08-10 to reflect the coverage-augmented frame
selection (see `docs/suspicious_frame_selection.md` for the fuller
methodology writeup) and are current again.
`docs/study_execution_log.md` and `RESEARCH_AGENTS.md` are useful for
provenance/context but are working documents, not methods sources — see
their own staleness banners for which sections are still current.

---

## 3. Research Questions

Verbatim from `docs/RQs_JSS.md` (canonical, do not paraphrase differently
elsewhere without updating that file first):

- **RQ1 — Bug Type Distribution Across Projects.** What is the distribution
  of ODC defect types across the Defects4J benchmark, and does this
  distribution vary significantly across projects?
- **RQ2 — Bug Type Coverage of the ODC Taxonomy.** Do the seven standard
  ODC bug types cover all the bugs in Defects4J — or do some bugs actually
  fall outside those seven types?
- **RQ3 — Overall Pipeline Classification Accuracy.** How well does the
  LLM-based pipeline, using the scientific debugging loop and ODC taxonomy,
  classify Defects4J bugs into the correct defect types under a four-level
  accuracy evaluation?
- **RQ4 — Contribution of Each Pipeline Component.** How much do the
  scientific debugging loop and explicit ODC taxonomy grounding each
  improve classification accuracy, label consistency, and vocabulary
  reduction compared to an unstructured LLM baseline?
- **RQ5 — Does Seeing the Fix Change How a Bug Gets Classified?** What is
  the magnitude and pattern of semantic divergence between pre-fix and
  post-fix ODC classifications, and how does per-project classification
  reliability vary across Defects4J projects?

---

## 4. RQ Results So Far (development-validation runs — not final)

Two runs exist, both against the shared `artifacts_full` evidence store, no
Defects4J re-collection needed for either:

- **Pilot** (2026-07-08): 6 hand-picked bugs, `manifest_pilot.json`.
- **Dev-validation** (2026-07-09): 40-bug balanced manifest
  (`manifest_40.json`, `min_per_project=2`, seed 42, all 17 projects
  covered) — but because `study-drift`/`study-escape`/`study-ladder` scan
  the whole shared prefix/postfix tree rather than filtering by manifest (a
  manifest is a worklist, not a namespace — see `AGENTS.md`'s gotcha
  section), 4 leftover pilot bugs not in `manifest_40.json` were picked up
  too, for an **effective n=44**. Outputs: `.dist/study/analysis_40.json`,
  `taxonomy_coverage_40.json`, `taxonomy_grounding_40.json`.

Conditions run for the dev-validation pass: `zero-free`, `few-open`,
`scientific-open`, `scientific-closed` (the 4 conditions the 5 RQs actually
require — `few-closed` was not run, it isn't needed by any current RQ).

### RQ1 — type distribution (prefix, `scientific-open`)

| Type | Pilot (n=6) | Dev-validation (n=44) |
|---|---|---|
| Checking | 3 (50.0%) | 20 (45.5%) |
| Algorithm/Method | 3 (50.0%) | 15 (34.1%) |
| Assignment/Initialization | 0 | 6 (13.6%) |
| Function/Class/Object | 0 | 3 (6.8%) |
| (other 3 types) | 0 | 0 |

Only 4 of 7 ODC types appeared in either run — plausibly a real skew in
this sample, or an artifact of small n; needs the confirmatory run to
distinguish. Per-project chi-squared association (the second half of RQ1)
was not computed in either run — many projects still have only 1-3 bugs, far
below the ≥5-expected-count-per-cell threshold a chi-squared test needs; not
meaningful before the confirmatory run.

### RQ2 — taxonomy coverage (`scientific-closed` vs `scientific-open`)

| Metric | Pilot (n=6) | Dev-validation (n=44) |
|---|---|---|
| Escape rate | 0.0% | 0.0% |
| Coverage rate | 100% | 100% |
| Closed↔open shift κ | 0.667 | 0.709 |
| Bugs shifted type | 1/6 (16.7%) | 8/44 (18.2%) |

Zero escapes to "Other" in either run. That's a real result, but at n=44 a
true escape rate anywhere below ~7-8% would still very plausibly show 0
escapes by chance — needs the confirmatory run before claiming the taxonomy
is exhaustive.

### RQ3 — accuracy (prefix vs postfix, `scientific-open`)

| Metric | Pilot (n=6) | Dev-validation (n=44) |
|---|---|---|
| Strict match | 5/6 (83.3%) | 36/44 (81.8%) |
| Top-2 match | 100% | 97.7% |
| Family match | 100% | 97.7% |
| Cohen's κ (overall) | 0.667 | 0.726 (substantial) |
| Per-type F1 | not meaningful at n=6 | 0.80–0.86 across the 4 observed types |

### RQ4 — ablation ladder (`zero-free → few-open → scientific-open`, prefix-only)

| Tier | Pilot: unique labels / entropy / ODC coverage | Dev-validation: unique labels / entropy / ODC coverage |
|---|---|---|
| zero-free | 6 / 2.585 / 2 of 7 | 43 / 5.414 / 5 of 7 |
| few-open | 2 / 0.650 / 2 of 7 | 5 / 1.649 / 4 of 7 |
| scientific-open | 2 / 1.000 / 2 of 7 | 4 / 1.703 / 3 of 7 |
| Vocabulary reduction ratio | 0.0 (baseline ≤ 7, formula doesn't trigger) | **0.837** |

The dev-validation run shows the taxonomy-grounding effect clearly: 43
distinct free-form labels for 44 bugs (near one-per-bug) collapse to 4-5
once a taxonomy is imposed. This is the strongest, most reproducible signal
across both runs — worth flagging as a likely genuine effect vs. a small-n
artifact.

### RQ5 — pre/post drift + per-project reliability (`scientific-open`)

Global drift numbers are the same rows as RQ3 (strict/top-2/family match,
overall κ) — this table is the per-project κ half specifically:

| Project | Pilot κ (n=1-2/project) | Dev-validation κ (n=2-3/project) |
|---|---|---|
| Chart | insufficient data | 0.0 |
| Cli | insufficient data | 1.0 |
| Closure | insufficient data | 0.5 |
| Codec | insufficient data | 0.5 |
| Collections | insufficient data | 0.5 |
| Compress | insufficient data | 1.0 |
| Csv | insufficient data | 1.0 |
| Gson | insufficient data | 1.0 |
| JacksonCore | insufficient data | 1.0 |
| JacksonDatabind | insufficient data | 1.0 |
| JacksonXml | insufficient data | 0.333 |
| Jsoup | insufficient data | 0.0 |
| JxPath | insufficient data | 1.0 |
| Lang | insufficient data | 1.0 |
| Math | insufficient data | 1.0 |
| Mockito | insufficient data | 1.0 |
| Time | 0.0 (n=2) | 0.5 |

At the pilot's n=6 (1-2 bugs/project), per-project κ was undefined for all
but one project (Cohen's κ needs ≥2 bugs/project — this is a hard
mathematical floor, not a pipeline gap). At n=44 (2-3 bugs/project) it's
computable everywhere but still noisy per-project (e.g. Chart/Jsoup at 0.0
with only 2-3 bugs each) — worth a closer per-project look once the
confirmatory run gives more bugs per project, rather than reading these as
final per-project reliability figures.

### Recommended next step

A confirmatory run at 68-100 bugs (already `study-plan`'s existing
default range, `min_per_project` ≥4-5 to get meaningfully non-degenerate
per-project κ everywhere) before any of the above goes into a manuscript
table. See the chat history / `docs/study_execution_log.md` for the
rate-limit and timing math behind that recommendation — at the measured
~14.4 LLM calls/bug across the 4 required conditions, a 100-bug run is
~1,440 calls, comfortably within a single day even on one API key.
