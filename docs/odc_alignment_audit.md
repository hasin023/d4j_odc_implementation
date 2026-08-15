# ODC v5.2 Alignment Audit — Pipeline, Artifact Mapping, and the Impact Attribute

**Date:** 2026-07-10 · **Audited state:** working tree on `fix_jss` (post two-variable
redesign, pre confirmatory run) · **Evidence corpus inspected:**
`.dist/study/artifacts_full/` (854 prefix + 854 postfix `context.json`) and the n=44
dev-validation classifications · **Reference:** `docs/odc_doc.md` (IBM ODC v5.2 for
Software Design and Code, 2013) — all §refs below are to that document.

This audit answers three questions the team raised, then generalizes into a full
alignment check of the Defects4J→ODC artifact mapping and the classification pipeline:

1. Are we determining the ODC **Impact** attribute the right way?
2. Is the LLM properly aware of the impacts defined by ODC v5.2?
3. Is what we are doing enough — and where are the loopholes?

Companion changes: every "Resolution" noted below was implemented in the same pass as
this document (prompting/agent/odc/llm/models/pipeline/analysis/web_fetch + tests +
`latex/jss/main.tex`), except items listed in §8 (Deferred).

---

## 1. Direct answers

**Q1 — Are we determining impact the right way?** No — but not because it was determined
badly; it was, in practice, **not determined at all**. Before this pass the only impact
machinery was a keyword heuristic (`prompting.py::_build_odc_mapping_hints`) that could
reach just **5 of the 13** v5.2 impact categories and injected its guesses into the LLM's
evidence payload as `odc_opener_hints` (an anchoring bias, not an independent judgment).
The LLM-side field (`inferred_impact`) was an unvalidated *list* of free strings — v5.2
§3.3 asks for a single selection — and in the n=44 dev-validation run under the default
condition (`scientific-open`), only **1 of 44** classifications contained any impact
value, because the scientific loop's system prompt never mentioned opener attributes at
all. No research question or analysis consumed the field; `analysis.py::analyze_impact_vs_type`
was dead code (never called by any study command).

**Q2 — Is the LLM aware of the v5.2 impact definitions?** No. Neither the few-shot
system prompt nor the scientific-loop system prompt contained any impact category names
or definitions. The only impact vocabulary the model ever saw was the heuristic's
candidate list riding inside the evidence JSON. Any impact value the model produced came
from its training-data notion of "impact", not from v5.2.

**Q3 — Is what we are doing enough?** Not before this pass, on two fronts. First, the
impact attribute needed the full treatment it now has (§6). Second — found while auditing
the mapping — the **pre-fix evidence arm was leaking fix-derived information** through two
channels (§4.2, §4.3), which contradicted the paper's own no-leakage claim and softened
the very pre/post contrast that RQ3/RQ5 measure.

---

## 2. Ground rules from ODC v5.2 (what the spec actually requires)

- **Two-phase model (§1, §2):** Activity, Trigger, Impact are **opener** attributes —
  classifiable when the defect is found, from the failure and its circumstances. Target,
  Defect Type, Qualifier, Age, Source are **closer** attributes — classifiable only when
  the fix is known ("Represents the actual correction that was made", §4.2).
- **Consequence for this project:** *Defect Type is fix-defined.* Classifying it pre-fix
  is therefore a **prediction of a closer attribute from opener-time evidence** — that is
  the research contribution, and prefix/postfix drift is partly genuine indeterminacy
  (multiple valid fixes), partly prediction error. *Impact is open-time-defined and
  fix-independent* — which yields the negative-control design in §6.3.
- **Field-reported defects (§3.1.6, §5.3):** most Defects4J bugs come from user-filed
  reports, i.e. they are *field* defects in ODC terms. For those, v5.2 prescribes:
  select the **Trigger** first from what the user was doing; then derive **Activity** as
  the in-process activity that *should have caught* the defect, via the organization's
  activity→trigger mapping (§2.1). Activity is NOT "whatever harness reproduced the bug
  later".
- **Impact (§3.3):** one of 13 fixed categories, judged from the customer/user
  perspective — for field defects, "the impact the failure had on the customer".
  **Capability** is the explicit fallback ("where the customer is not impacted in any of
  the previous categories"), and §5.1 permits **Unknown** at open time when information
  is missing.
- **Age (§4.2.4):** the developmental history of the code the defect was *in* —
  Base/New/Rewritten/ReFixed describe where the defect was **injected**, not how big the
  fix is.
- **Qualifier (§4.2.2):** Missing = omission; Incorrect = commission; Extraneous = code
  or text that should not exist at all (not "the fix deleted lines").

---

## 3. The corrected Defects4J-artifact → ODC-attribute mapping

This replaces the mapping narrative previously used (paper §"ODC and Defects4J Artefact
Mapping"; earlier: `iut_submissions` report — frozen history). One row per attribute.
"Status" values: **Claimed** (we determine and report it) · **Predicted-closer** (the
research task itself) · **Constant-by-construction** (fixed by how D4J is built; stated,
not inferred) · **Not reliably determinable** (documented limitation, not claimed).

| ODC attribute | Phase | v5.2 rule | D4J evidence actually available | Status in this pipeline | What was wrong before |
|---|---|---|---|---|---|
| **Impact** | Opener | §3.3: single category, customer perspective; field defects → impact the failure had; Capability fallback; Unknown allowed (§5.1) | Bug report title/description (832/854 bugs) + failing-test behaviour (all bugs) | **Claimed** — the one opener attribute we determine (it is the behaviour/failure-side dimension). Single-select from 13 + Unknown, definitions in prompt, enum-validated | No definitions in prompt; 5/13-category keyword heuristic anchored the model; unvalidated list field; emitted 1/44 |
| **Trigger** | Opener | §3.2, §5.3.2a: the condition/catalyst, chosen from the *usage scenario* for field defects | Usage scenario only inside bug reports, of very uneven quality; the D4J triggering test is a retrospective reproduction — quantified in §9.1: 33/40 sampled trigger tests postdate the buggy revision, corroborated by Rafi et al. 2025 (55%/77%, MSR) | **Not reliably determinable** — documented; keyword heuristic removed | "expected"/"after"-style keyword matches fired on nearly every JUnit assertion; candidates violated the §2.1 activity→trigger table |
| **Activity** | Opener | §3.1.6: for field defects, the in-process activity that should have caught it, derived *from* the trigger | Nothing independent — the harness always reruns JUnit regardless of how the defect actually surfaced | **Not reliably determinable / constant-by-construction** — documented | "Tests → Activity" treated the harness's reproduction as the discovery activity; hardcoded "Unit Test" default |
| **Target** | Closer | §4.1: entity fixed (Requirements/Design/Code/Build/Info-Dev/NLS) | D4J minimized patches touch source code only, by benchmark construction. A design-originated defect still lands as Code here — Design (§4.1.2) requires a design *specification document* to change, and D4J never has one; the design-magnitude distinction ODC does track sits one level down, in Defect Type (§9.3) | **Constant-by-construction:** Design/Code — stated as a scoping assumption | Presented as if inferred from modified classes |
| **Defect Type** | Closer | §4.2: defined by the actual correction | Postfix arm: the real buggy→fixed diff. Prefix arm: symptoms only | Postfix = ODC-canonical reference; prefix = **Predicted-closer** (the study's core task) | Sound — this framing is the contribution; now stated explicitly in the paper |
| **Qualifier** | Closer | §4.2.2: Missing/Incorrect/Extraneous | The fix diff (postfix arm) | LLM-determined in postfix from the diff; optional | Diff-shape heuristic mapped remove-only→"Extraneous" (wrong: deleting a wrong line = Incorrect); heuristic removed |
| **Age** | Closer | §4.2.4: injection history of the defective code | Would require VCS archaeology (SZZ-style: when were the defective lines introduced) — not in `context.json`, but recoverable in principle: `active-bugs.csv` gives the exact buggy-revision commit hash and `project_repos/` has full history; demonstrated by hand on Lang-1 (§9.2) | **Not reliably determinable** — heuristic removed; SZZ integration is future work (§8), now with a citation trail (§9.2) | Diff-size heuristic (≥120 changed lines → "Rewritten") conflated fix size with injection history |
| **Source** | Closer | §4.2.3: in-house/reused/outsourced/ported | All 17 D4J projects are single-organization OSS | **Constant-by-construction:** ≈ Developed In-House — stated, not claimed as a finding | Left dangling (never populated, never explained) |

The one-line story for the paper: **of the three opener attributes, only Impact is
supported by Defects4J's artifacts** (bug report + failure behaviour = exactly the
customer-perspective evidence §3.3 asks for); Activity and Trigger require discovery-time
process context that a retrospective benchmark cannot supply. On the closer side, Type
and Qualifier are supported (by the diff, postfix), Target and Source are constants of
the benchmark, and Age is out of evidence reach.

---

## 4. Findings

### 4.1 Impact was vestigial (severity: high for any impact claim)

Details in §1/Q1–Q2. Code locations (pre-change): `prompting.py::_build_odc_mapping_hints`
(keyword heuristic, 5/13 categories reachable, `"message"`→Documentation fired on error
messages); `llm.py::classification_response_schema` (`inferred_impact`: unconstrained
string array); `pipeline.py::_validate_classification_payload` (no vocabulary check);
`agent.py::_agent_system_prompt` (no opener attributes at all). Resolution: §6.

### 4.2 `bug_info` leaked the modified-classes oracle into the pre-fix arm (severity: high)

`collect` stores the raw stdout of `defects4j info -p P -b N` as `context.bug_info`, and
the payload builder passed it to the LLM verbatim. That text ends with:

```
List of modified sources:
 - org.jfree.chart.imagemap.StandardToolTipTagFragmentGenerator
```

— the classes changed by the **developer's fix commit** (D4J derives this from the
buggy→fixed diff; it is the same information as `classes.modified`). The pipeline
explicitly treats `classes.modified` as a hidden oracle (`pipeline.py` stores it under
`hidden_oracles` with the note "excluded from the LLM prompt") and the paper claimed
this prevented leakage — but the identical fact rode in through `bug_info`.
**852/854 prefix contexts** contain the section (the other 2 lack the info block).
`bug_info` also carries "Revision ID/date (fixed version)" — post-fix facts by
definition.

Why it matters: it hands the model near-perfect fault localization derived from the fix,
which (a) no pre-triage user would have, (b) partially explains the pilot observation
"probed the actually-buggy class first in 6/6 bugs" (`condition_model.md` §4.2) that
motivated the enforced loop, and (c) inflates prefix accuracy / deflates the pre-post
drift that RQ3 and RQ5 measure.

**Resolution:** classify-time sanitization of the **pre-fix arm only** —
`_sanitize_bug_info` strips the "List of modified sources" and "Revision ID/date (fixed
version)" sections before the payload is built. The post-fix arm legitimately knows the
fix and keeps `bug_info` untouched. `context.json` files are never modified.

### 4.3 Bug reports carried fix-era content into the pre-fix arm (severity: high, tracker-dependent)

`web_fetch.py` requested JIRA `status`/`resolution` fields and appended up to 5 comments
(JIRA + GitHub); SourceForge/Google-Code pages were flattened whole-page text including
comment threads. Resolved-issue reports therefore contain "Resolution: Fixed",
"Fixed in CVS for the upcoming 1.0.13 release", "status: open → closed-fixed", and in at
least one case the report *is* a patch ticket ("Fix for MultiplePiePlot … I committed
your change"). Corpus measurements (strict markers: `Fixed in`/`closed-fixed`/
`closed-accepted`/`Resolution: Fixed`/`committed`/`status : open`):

| | reports present | with fix-era markers |
|---|---|---|
| All 854 bugs | 832 (97.4%) | 360/832 (43%; 53% under a looser marker set) |
| JIRA projects (Lang, Math, Cli, Codec, Collections, Compress, Csv, JxPath) | 336/337 | **328/336 (~98%)** — the JIRA API embeds Status/Resolution on every resolved issue |
| GitHub projects (Gson, JacksonCore/Databind/Xml, Jsoup, Mockito) | 288/291 | 10/288 (~3%) |
| Chart (SourceForge) | 8/26 | 7/8 |
| Closure (Google Code archive) | 174/174 | 9/174 |

Two implications beyond the leak itself: contamination is **systematically unequal by
project** (a per-project confound for RQ1/RQ5 had it stayed), and report *availability*
is also uneven (Chart 31% vs ~100% elsewhere) — the latter is now a stated
threat-to-validity for the impact attribute, whose primary evidence is the report.

**Resolution:** pre-fix-arm-only sanitization — `sanitize_bug_report` keeps
title/metadata/description, drops the `Comments:` block and `Status:`/`Resolution:`
tokens (API-format reports), and truncates flattened generic pages at the first
comment-thread marker. Defense-in-depth for future collections: `web_fetch.py` no longer
requests `status`/`resolution` and no longer appends comments.

The first implementation pass truncated at *per-comment* boilerplate (e.g. SourceForge's
"If you would like to refer to this comment…" link, which is appended *after* each
comment) — that missed fix disclosures living inside the *first* comment itself, textually
*before* that link (`Chart_1`: "Good spot… I've committed the fix. If you would like to
refer…"). It also missed Google Code/Closure's raw-JSON report shape
(`{"status":"Fixed","comments":[{"id":0,...},{"id":1,...}]}`), where `"status":"Fixed"`
uses JSON's unquoted-colon syntax (not matched by the plain-text `Status: X` pattern) and
comment objects after the first routinely disclose the fix ("thanks for the report, the fix
will get committed on monday" — `Closure_90`). Both were found by re-running the sanitizer
over the **full 854-bug prefix corpus** (not just spot-checked samples) and grepping the
rendered LLM payload for leak markers — the fix now (a) truncates at SourceForge's
`Discussion` section header, which precedes *every* comment including the first, and (b)
truncates a raw-JSON `comments[]` array after its first element regardless of the second
element's `"id"` value. **Verified: 0/854 prefix payloads contain any modified-sources,
fixed-revision, or fix-era-comment marker** (broadened marker set, re-run after the fix).
Both new patterns are pinned by regression tests
(`test_sanitize_bug_report_sourceforge_first_comment_leak`,
`test_sanitize_bug_report_json_status_and_second_comment` in `tests/test_prompting.py`).

### 4.4 The zero-shot baseline saw ODC vocabulary (severity: medium — RQ4 confound)

`_context_payload` appended `odc_opener_hints`/`odc_closer_hints` (containing
"Capability", "Test Variation", "Design/Code", …) to **every** payload — including the
`zero-free` condition whose definition is "no ODC concepts anywhere". The RQ4 ladder's
baseline rung was therefore not clean (conservatively: the contamination could only have
*reduced* the measured vocabulary-collapse effect, since the baseline still produced 43
unique labels despite the hints — but the cell must be clean regardless).
**Resolution:** `_build_odc_mapping_hints` and both payload keys removed entirely.

### 4.5 Instrument prior steered the RQ1 distribution (severity: medium)

Both system prompts asserted *"Most Defects4J bugs are … Checking, Algorithm/Method, or
Assignment/Initialization."* For RQ1 — which *measures* the type distribution — the
instrument embedded its own expected answer (the dev-validation run indeed returned
Checking 45%, Algorithm/Method 34%, Assignment 14%). **Resolution:** replaced with a
neutral anti-default rule (don't default to Function/Class/Object; it needs design-level
evidence) that names no expected distribution. All runs before this change (pilot n=6,
dev-validation n=44) embedded the old prior — one more reason those numbers are
non-final, alongside the leaks.

### 4.6 Family grouping is not an IBM construct (severity: low, presentation)

The "Control and Data Flow" / "Structural" two-family split used by RQ3's Tier-3 family
match does **not** appear in v5.2. It is a coarse grouping this project defines (it
echoes groupings used in the automated-ODC literature, e.g. Thung et al.'s
control-flow/data/structural super-categories, but is not identical to any of them).
**Resolution:** paper and `odc.py` now present it as our defined grouping with its
Tier-3 purpose; if the team prefers a cited grouping, swap in the source explicitly.

### 4.7 `odc.py` definition nuances (severity: low)

Two v5.2 subtleties were missing and both matter for common Defects4J fixes:
- **Checking** (§4.2.1.2): if the missing/incorrect check is the critical error, the
  type stays Checking **even when the fix also adds consequence code** (a loop/branch/
  early-return) — the classic "add guard + return" patch.
- **Assignment/Initialization** (§4.2.1.1): a fix consisting of *multiple* assignment
  corrections may be of type **Algorithm/Method**.
**Resolution:** both nuances added to the type descriptions.

### 4.8 Dead/misleading analysis code (severity: low)

`analysis.py::analyze_impact_vs_type` was never called by any study command, and its
`_NAIVE_MAP` ("Performance→Timing/Serialization, Documentation→Function/Class/Object",
…) was an invented mapping with no literature basis, feeding a "symptom_label_accuracy"
metric that would not survive review. **Resolution:** reworked — the impact×type
cross-tab stays (it is the empirical orthogonality check, §6.2); the naive map and its
metric are deleted; the function is now wired into `study-drift`.

---

## 5. What the findings taint (read before citing old numbers)

- **Pilot (n=6) and dev-validation (n=44) prefix classifications** were produced with
  (i) the modified-sources oracle visible, (ii) fix-era report content visible for
  JIRA-tracked bugs, and (iii) the distribution prior in the prompt. They were already
  flagged non-final in `docs/JSS_HANDOFF.md`; they must now additionally be considered
  *optimistically biased* on prefix accuracy and *understated* on pre/post drift.
  The user will rerun them after this pass; the confirmatory run starts clean.
- **The "probed the actually-buggy class first in 6/6 bugs" pilot observation**
  (`condition_model.md` §4.2) is partially explained by the leak and must not be cited
  as evidence of scientific-loop localization behaviour until reproduced on sanitized
  payloads. (The other pilot evidence for the loop — 2/6 label changes toward the
  oracle vs 0/6 for narration — concerns label agreement, not localization, and is less
  affected, but reruns will tell.)
- **RQ4 ladder numbers** (43→4-5 label collapse) — directionally robust (contamination
  worked against the effect) but regenerate anyway.

---

## 6. The Impact attribute, done right (design implemented in this pass)

### 6.1 Determination

- **Vocabulary:** the 13 v5.2 §3.3 categories, verbatim-faithful definitions, plus
  **Unknown** (§5.1). Lives in `odc.py::ODC_IMPACTS` / `impact_markdown()` /
  `allowed_impact_names()`.
- **Single-select** (`impact: string|null`), enum-constrained in the response schema and
  strictly validated in `pipeline.py` (same policy as `odc_type`). The legacy
  `inferred_impact` list remains readable in old artifacts but is no longer requested.
- **Prompted in `few` and `scientific`** (system-prompt section "ODC Impact — opener
  attribute"): judge from the customer/user perspective using the bug report and the
  failure behaviour; the fix does not define impact; Capability is the §3.3 fallback;
  Unknown when the evidence does not support a judgment. **Not** added to `zero-free`
  (that cell must stay ODC-free).
- **No heuristic candidates** in the payload — the LLM's impact judgment is now
  unanchored; the old keyword heuristic is gone.
- Evidence basis is opener-side by construction in the prefix arm (sanitized report +
  failures). The postfix arm also emits impact — not as a better estimate (ODC says the
  fix adds nothing to impact) but to enable §6.3.

### 6.2 Analysis (wired into `study-drift`)

- `compute_impact_distribution` — counts/shares over prefix classifications + how many
  had a bug report available (coverage caveat travels with the number).
- `analyze_impact_vs_type` — impact×type cross-tab: the empirical check of ODC's
  orthogonality claim (impact = behavioural dimension; type = code-mechanism dimension).
  The literature's "performance bugs / GUI bugs / network bugs" are impact-like labels;
  this table is where that discussion becomes data.
- **Expect a skewed distribution:** failing-unit-test benchmarks should concentrate in
  Reliability (crashes/exceptions) and Capability (wrong results). That is a property of
  the benchmark, not an instrument failure; report the distribution with entropy, do not
  promise discriminative power.

### 6.3 Impact as a negative control for drift (the methodological payoff)

Per v5.2, Defect Type is fix-defined (prefix→postfix drift mixes genuine fix-choice
indeterminacy with instrument noise), while Impact is open-time-defined and
**fix-independent** (drift on impact *should be zero*). Therefore prefix↔postfix impact
disagreement, measured on the same pairs as type drift, estimates **pure instrument
noise** — a baseline that contextualizes type drift. `analyze_batch_artifacts` now emits
`impact_stability` (raw agreement; κ where the marginal distribution is non-degenerate,
with a degeneracy caveat) alongside the type-drift block. Interpretation rule: type
drift meaningfully above impact drift = evidence of genuine fix-dependence in type, not
just LLM instability.

### 6.4 What impact still cannot claim (honest limits)

- **No oracle exists.** D4J has no customer-impact labels, and postfix is not a
  reference for an opener attribute. Impact accuracy is not measurable the way type
  accuracy is; only distribution, stability, and (future) human spot-validation are.
- **Report availability is uneven** (Chart 31%): bugs without reports rest on failure
  behaviour alone; Unknown is the honest answer when that is insufficient.
- Impact enters the paper as a **descriptive companion to RQ1** and the **negative
  control inside RQ5** — no new RQ, no accuracy claim.

---

## 7. Invariant established by this pass

> **The pre-fix payload contains no fix-derived information.** Every difference between
> the prefix and postfix payloads is fix knowledge: the diff (`fix_diff_oracle`), the
> unsanitized `bug_info` (modified sources, fixed-revision ids), and unsanitized report
> content. `context.json` artifacts are never modified by sanitization — it is applied
> at payload-build time, so the 854-bug evidence store required no re-collection.

Regression tests pin this: prefix payloads must contain no "List of modified sources" /
fix-era markers / `odc_opener_hints`; postfix payloads keep `bug_info` and report text
untouched; the `zero-free` prompt+payload contain no ODC vocabulary. Beyond unit-test
fixtures, the invariant was checked empirically against every bug in the evidence store:
rendering the `few`/`closed` prompt for all **854** prefix `context.json` files and
grepping for the leak markers of §4.2/§4.3 (modified-sources, fixed-revision,
status/resolution tokens in both plain-text and JSON syntax, per-comment and thread-level
tracker boilerplate) returns **zero matches**.

## 8. Deferred (explicitly out of this pass)

- **Rerun of pilot + n=44 dev-validation** on sanitized payloads — user will run later;
  required before any of §5's tainted numbers are replaced.
- **Age via SZZ/VCS archaeology** (map defective lines to their introducing commits) —
  the only sound path to §4.2.4 Age on D4J; future work. Confirmed feasible in
  principle (§9.2): `active-bugs.csv` has exact buggy-revision hashes, `project_repos/`
  has full history, demonstrated by hand on Lang-1. Citation trail: mechanism precedent
  (IBM patent US8214798B2, continuation US9047402B2) and D4J-specific BIC feasibility
  (Wen et al. ESEC/FSE 2019; An & Yoo ESEC/FSE 2019/2021, 91 D4J bugs; An, Hong & Yoo's
  Fonte, ICSE 2023).
- **Human-validated impact subset** (e.g. 2 raters × 30–50 bugs, κ) — the standard move
  if impact is ever to carry stronger claims than distribution + stability.
- **Full v5.2 field-defect Trigger/Activity procedure** (trigger from usage scenario,
  activity via §2.1 mapping) — possible only for bugs with high-quality reports; not
  claimed in the current design.
- **Reference-sensitivity check** (few vs scientific on postfix) — already queued
  before this audit; unchanged.

---

## 9. Follow-up grounding pass (2026-08-16) — Trigger provenance and Age recoverability

Verification pass for JSS paper §2.3 (Defects4J↔ODC attribute mapping, related work),
independent of the 2026-07-10 pass above. Quantifies the Trigger line in §3's table with
fresh evidence and corrects the framing of the Age line from "not in the evidence set" to
"not currently extracted, but recoverable."

### 9.1 Trigger: the retrospective-reproduction claim, quantified

Sampled 40 bugs across 12 projects (Lang, Math, Closure, Jsoup, Cli, Codec, Collections,
Compress, Csv, Gson, JacksonCore, JacksonDatabind, JxPath) using the local Defects4J
clone (`~/Thesis/defects4j`, full git history in `project_repos/`). For each bug, read
the `tests.trigger` metadata name and diffed the actual test file between
`revision.id.buggy` and `revision.id.fixed` (from `active-bugs.csv`).

**Result: 33/40 (82.5%) trigger-test methods did not exist at the buggy revision** — they
were added in the same commit as the fix. Example: Lang-1's trigger test
`NumberUtilsTest::TestLang747` is a pure addition in fix commit `d1a45e97`, absent at
buggy revision `396afc3e`. Defects4J's own bug-mining process
(`framework/bug-mining/README.md` step 4) confirms this is expected: curation only
requires "a test that fails on pre-fix and passes on post-fix," never that the test
predate the fix.

**Independent peer-reviewed corroboration:** Rafi, Chen, Chen & Wang, "Revisiting
Defects4J for Fault Localization in Diverse Development Scenarios," MSR 2025
(arXiv:2310.19139) — 55% of Defects4J's fault-triggering tests were newly added to
reproduce the bug or as a regression test; 77% show some form of post-report "developer
knowledge" (added or modified after the bug report date). Their number is a lower bound
relative to the 82.5% above because they anchor on bug-report date rather than
presence-at-buggy-commit.

**Structural confirmation from the source paper:** Just, Jalali & Ernst, ISSTA 2014 —
Defects4J constructs `V_bug` by re-applying the isolated patch to `V_fix` ("Vbug is
obtained by re-introducing the bug... applying the patch of the isolated bug to Vfix").
Since `V_bug` derives from `V_fix`, it inherits `V_fix`'s test suite by construction,
including any test the fix commit added. The paper does not flag this as a limitation.

### 9.2 Age: recoverable in principle, not a documentation gap

`active-bugs.csv` (one per project, `framework/projects/<P>/active-bugs.csv`) stores
exact `revision.id.buggy` and `revision.id.fixed` commit hashes for every bug, and the
local `project_repos/` are full git clones. Demonstrated on Lang-1: `git blame` on the
pre-fix lines of `NumberUtils.java` at the buggy revision traces them to a commit from
2012-09-12 (Sebastian Bazley), about ten months before the July 2013 fix, itself
modifying code from 2003 (Stephen Colebourne). Age is not evidence D4J withholds — it is
evidence this pipeline does not currently extract.

No peer-reviewed paper connects SZZ/blame analysis to ODC's Age attribute specifically.
Closest precedents:
- **Mechanism precedent:** IBM patent US8214798B2 (continuation US9047402B2), Bellucci &
  Portaluri, "Automatic calculation of orthogonal defect classification (ODC) fields" —
  automates ODC's Age/Source-History field from version control by diffing against a
  baseline code level. Not peer-reviewed, but the same mechanism used by hand above.
- **Feasibility on Defects4J specifically:** Wen et al., "Exploring and Exploiting the
  Correlations between Bug-Inducing and Bug-Fixing Commits," ESEC/FSE 2019 (manually
  validated BIC dataset for D4J bugs); An & Yoo, "Reducing the Search Space of Bug
  Inducing Commits using Failure Coverage," ESEC/FSE 2019/2021 (91 D4J bugs, blame +
  bisection); An, Hong & Yoo, "Fonte: Finding Bug Inducing Commits from Failures," ICSE
  2023.

No prior work combines the two. Age-via-SZZ-on-Defects4J is a citable, unexploited
extension, not an unsupported claim.

### 9.3 Target: the design-originated-defect edge case

Question: does a defect whose root cause was a design decision, not a local code
mistake, count as Target=Design if its fix happens to touch multiple files? No — v5.2
§4.1.2 defines Design strictly as "it was necessary to change the design **specification
document**"; Target classifies the artifact touched, not the defect's conceptual origin.
D4J never has a design-spec artifact distinct from source, so Target=Code holds whether
the fix was a local tweak or a structural rethink. ODC's design-magnitude distinction
lives one level down, in Defect Type: Function/Class/Object (§4.2.1.4) is defined for
errors that "should require a formal design change... affects significant capability...
or global data structure(s)," while Algorithm/Method (§4.2.1.3) is explicitly fixable
"without the need for requesting a design change." A multi-file fix reflecting a design
rethink lands as Function/Class/Object or Relationship; the same-fix-applied-in-several-
places case lands as Algorithm/Method or Assignment/Initialization. Target stays Code
either way.

### 9.4 Citation correction

`docs/related_work_literature_leads.md`'s "AgentSZZ" candidate (cited there as
`arXiv:2604.02665`) does not resolve to a paper connecting SZZ to ODC or Defects4J — that
ID surfaces an unrelated paper (AgenticSZZ, arXiv:2602.02934, Shi/Li/Adams/Hassan, no
ODC/Age/D4J content). That entry needs correcting or removing; the SZZ-on-D4J citations
to use instead are the three feasibility papers in §9.2.
