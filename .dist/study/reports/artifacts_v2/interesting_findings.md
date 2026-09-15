# Interesting findings, per project — worth mentioning to supervisor

Running notes, written as each project's `scientific-open` + `few-open` classification
finishes. Numbers are computed straight from `classification.<tag>.json` under
`.dist/study/artifacts_v2/`, both evidence modes. See `per_project/<Project>_<date>.xlsx`
for the full tables this is drawn from.

---

## Lang (61 bugs)

1. **Dominant, directional strategy confusion:** when Scientific and Few disagree, it's
   almost always Scientific→**Checking**, Few→**Algorithm/Method** — 15/19 prefix
   disagreements, 8/13 postfix disagreements. Not scattered noise; one specific,
   systematic, one-directional bias between two strategies on two categories.
2. **Agreement asymmetry:** strategies agree more with oracle info than without —
   Postfix 79% (48/61) vs Prefix 69% (42/61). Consistent with the Scientific loop's
   extra work actually diverging from a plain Few-shot call specifically when the
   answer is hard to find, and converging once both have the fix diff. Ambiguous
   whether this means Scientific is *more correct* under hard conditions, or just
   *more different* — no independent ground truth to check against. See discussion
   below.
3. Same Checking↔Algorithm/Method pair also dominates pre→post **type drift** (9 of 16
   drift cases) — unstable across both the strategy axis and the evidence-mode axis,
   suggesting a genuine ambiguity in how Lang bugs split between these two ODC types,
   not an artifact of one particular comparison.
4. **"Other" never predicted** — 0 of 122 classifications. Ties into the still-open
   RQ2 question: does the open taxonomy's escape category ever fire for Lang, even
   with richer coverage evidence?
5. Zero classifications flagged low-confidence or needs-human-review, across all 122.
   Worth a skeptical read rather than taking at face value.

**On point 2 (is the agreement asymmetry good or bad for the research goal):**
double-edged, not a clean answer.
- *Favorable reading:* the strategy variable clearly has a causal effect — if
  Scientific and Few behaved identically everywhere, that would be a null result for
  the entire premise of building the enforced loop. Diverging exactly where more
  evidence-gathering should matter (prefix) and converging where it doesn't need to
  (postfix, oracle already available) is the shape you'd want if the loop does real
  work.
- *Unfavorable reading:* divergence alone doesn't prove Scientific is *more correct* —
  it could mean the longer reasoning chain gives more chances to drift to a wrong
  answer, not fewer. Without ground-truth ODC labels, "more disagreement under harder
  conditions" is also consistent with "the task is inherently more ambiguous here for
  both, and each lands on a different side of that ambiguity somewhat arbitrarily."
- The fact that the disagreement concentrates on ONE directional pair (not spread
  across many categories) leans slightly toward a prompt-bias explanation (each
  strategy has its own systematic pull toward a label) rather than diffuse genuine
  uncertainty.
- **Concrete next step, not yet done:** read the `reasoning_summary` (and for
  Scientific, the probe transcript) for 3-4 Checking-vs-Algorithm/Method disagreement
  bugs side by side. If Scientific cites evidence Few never had access to, that's the
  favorable story. If both look at the same evidence and just land differently,
  that's the prompt-bias story.

---

## Chart (26 bugs)

1. **Same overall shape as Lang, different dominant pair.** Strategy disagreement here
   leans on **Assignment/Initialization ↔ Algorithm/Method** (4/9 prefix
   disagreements) rather than Lang's Checking↔Algorithm/Method — but **Algorithm/
   Method is on one side of nearly every top confusion pair in both projects**
   (drift pairs, prefix strategy pairs, and postfix strategy pairs all feature it).
   Worth checking whether this generalizes further once Time/Mockito/Math are in —
   if Algorithm/Method keeps showing up as the "attractor" category project after
   project, that's a taxonomy-level finding (this category may be under-specified or
   overly broad relative to how models actually use it), not a per-project quirk.
2. **Same agreement asymmetry direction as Lang, smaller gap:** Postfix 73.1% (19/26)
   vs Prefix 65.4% (17/26) — an 8-point gap here vs Lang's 10-point gap. Same
   qualitative pattern, consistent effect direction across two projects now.
3. Pre→post type drift: 5/26 (19%) — lower than Lang's 26%, but small-N (26 bugs),
   so not a strong claim yet.
4. **"Other" never predicted** here either — 0/52. Second project in a row.
5. One flag: `Chart_26` prefix marked `needs_human_review: True` **despite** a stated
   confidence of 0.9 and a confident-sounding reasoning summary ("fits the 'Checking'
   ODC type perfectly"). Worth noting that `needs_human_review` doesn't reliably
   track with low confidence — the two signals can disagree with each other, which
   matters if the plan was to use either one alone as a filter for what to spot-check.

---

## Time (26 bugs)

1. **Same exact dominant pair as Lang, and even more concentrated:** Scientific→
   Checking, Few→Algorithm/Method is 9 of 12 prefix disagreements (75%) and 4 of 5
   postfix disagreements (80%). Third project in a row where Algorithm/Method sits on
   one side of the dominant confusion pair — and the second (of two) where the exact
   Checking↔Algorithm/Method pair is the one driving it. This is no longer a
   coincidence worth a footnote — it's a pattern that's held across Lang and Time
   with the same direction, and Chart shares the same attractor category even with a
   different partner category (Assignment/Initialization).
2. **Largest agreement-rate gap so far:** Prefix 53.8% (14/26) vs Postfix 80.8%
   (21/26) — a 27-point gap, well past Lang's 10 points and Chart's 8. Time's
   strategies are the *most* alike once oracle info is available and the *most*
   unalike without it, of the three projects done so far.
3. Pre→post type drift: 8/26 (31%) — highest of the three projects so far (Lang 26%,
   Chart 19%), and again dominated by the same pair (6 of 8 drift cases are
   Checking↔Algorithm/Method in either direction).
4. **"Other" never predicted** — third project in a row, 0/52.
5. Two `needs_human_review` flags this time (`Time_15`, `Time_22`, both prefix) —
   more than Chart's one, none in Lang. Worth checking whether these cluster with the
   Checking/Algorithm-Method disagreement cases or are unrelated.

**Running cross-project observation (3/6 projects done):** the Checking↔Algorithm/
Method boundary looks like a real, recurring soft spot in how the model applies the
open taxonomy — not a per-project artifact. Worth pulling actual code+reasoning for a
handful of these bugs (across projects, not just Lang) before writing this up as a
finding, per the concrete-next-step note under Lang above.

---

## Mockito (38 bugs)

1. **The pattern breaks here, and that's itself informative.** Checking↔Algorithm/
   Method still appears (4/12 prefix disagreements, 3/13 drift cases) but is no
   longer dominant — disagreement spreads across several pairs instead:
   Algorithm/Method↔Function/Class/Object (3), Assignment/Initialization↔Algorithm/
   Method (2/2 pre/post), Relationship↔Checking (2, postfix). **Interface/O-O
   Messages** shows up for the first time in any project's top pairs, plausibly
   because Mockito (a mocking framework) has a much heavier interface/object-
   oriented surface than Lang/Time/Chart's data-and-algorithm-heavy codebases.
   Algorithm/Method is still on one side of most top pairs, so the "attractor
   category" observation holds — but which category it gets confused *with* looks
   domain-dependent, not fixed.
2. **Agreement asymmetry still holds, mid-sized gap:** Prefix 68.4% (26/38) vs
   Postfix 76.3% (29/38) — 8 points, same direction as all three prior projects,
   closer to Chart's gap than Time's.
3. Pre→post type drift: 13/38 (34%) — highest rate of the four projects so far.
4. **"Other" never predicted** — fourth project in a row, 0/76.
5. Two `needs_human_review` flags (`Mockito_12`, `Mockito_15`, both prefix).

**Running cross-project observation (4/6 projects done):** the agreement-rate
asymmetry (postfix > prefix) has now held in all four projects — that part looks
solid. The *specific* dominant confusion pair does not generalize as cleanly as
Lang+Time suggested; Chart and Mockito each have their own dominant partner category
for Algorithm/Method. Read as: Algorithm/Method is a genuine attractor category
project-independently, but which category it gets pulled from depends on what kinds
of bugs the project actually has — worth stating both parts together, not just the
punchier "same pair every time" version that looked true after 2 projects.

---

## Math (106 bugs — largest project at the time this section was written, most statistically robust; see Closure below for the current largest)

1. **Checking→Algorithm/Method is dominant again, and at the largest sample size
   yet.** 14/30 prefix disagreements (47%) and 9/26 postfix disagreements (35%) are
   exactly this pair, same direction as Lang and Time. With Math's 106 bugs, this is
   now the pattern's strongest single piece of evidence — three of five projects
   (Lang, Time, Math — the three largest by bug count) share the identical dominant
   pair and direction. Chart and Mockito remain the exceptions, not the rule.
2. **Smallest agreement gap of all five projects:** Prefix 71.7% (76/106) vs Postfix
   75.5% (80/106) — only 3.8 points, versus Time's 27, Lang's 10, Chart's/Mockito's 8.
   Direction still holds (postfix higher), but the *magnitude* varies enormously by
   project (3.8 to 27 points) — worth being careful not to quote one number as "the"
   effect size; it's project-dependent.
3. Pre→post type drift: 26/106 (25%) — right in line with Lang's 26%.
4. **"Other" never predicted** — fifth project in a row, 0/212. Across all five
   projects collected so far: 0 of 514 classifications used "Other."
5. Only one `needs_human_review` flag (`Math_106`, prefix) despite being the largest
   project — consistent with the pattern that this flag fires rarely everywhere (6
   total across 514 classifications, all five projects combined).

---

## Closure (152 of 174 active bugs — largest project by far; 22 pending collection)

Teammate-collected via a separate WSL/Windows lane and merged 2026-09-15. 22 active
bugs (`1`, `49`-`69` except `63`, `143`) are not yet in this corpus: `1` and `143` were
collected but quarantined as defective (bad fix diff), the rest of the `49`-`69` range
was simply not collected yet. `63` and `93` are the two Defects4J-deprecated ids and
were correctly excluded from the start. All 152 included bugs passed
`scripts/check_contexts.py`'s freshness gate (collected on/after 2026-08-10, i.e. after
the frame-selection-gap fix) — no stale contexts mixed in.

1. **Same dominant strategy-confusion pair as Lang/Time/Math, but at its sharpest
   concentration yet.** Scientific→**Checking**, Few→**Algorithm/Method** accounts for
   37 of 49 prefix disagreements (**75.5%**) and 24 of 29 postfix disagreements
   (**82.8%**) — higher concentration than Lang (79%/62%), and on more than double
   Lang's sample size. With Closure added, 4 of 6 projects (the four largest: Lang,
   Time, Math, Closure) now share this identical dominant pair/direction; Chart and
   Mockito remain the only exceptions.
2. **Agreement-rate gap holds direction, 6/6 projects now:** prefix sci-vs-few
   agreement 67.8% (103/152) vs postfix 75.7% (115/152) — a 7.9-point gap, landing
   between Math's 3.8 and Time's 27. Postfix beating prefix is now exception-free
   across every project collected so far.
3. **Pre→post type drift is identical in count but not in which bugs drift:**
   Scientific 53/152 (34.9%) and Few 53/152 (34.9%) — the exact same number is a
   coincidence, not shared mechanism: only 26 bugs drift under *both* strategies, 27
   drift under Scientific only, 27 under Few only, and 72 drift under neither. Worth
   citing the breakdown, not just the matching top-line rate — it would be easy to
   misread "53 = 53" as the two strategies drifting on the same bugs.
4. **Closure has the lowest Cohen's κ of all 6 projects under scientific-open: 0.367**
   — "fair" agreement (Landis & Koch), the only project to fall below the >0.4
   "moderate" floor that Chart/Lang/Math/Mockito/Time all clear (range was
   0.480-0.672 before Closure; now 0.367-0.672). It still beats its own few-open κ
   (0.301), so the RQ5 pattern "Scientific's κ beats Few's in every project" now
   holds 6/6, not 5/5 — but Closure is pulling the overall-κ average down more than
   any other single project.
5. **"Other" never predicted** — 0 of 608 classifications, sixth project in a row.
   Running total across all six projects: **0 of 1,122 classifications ever used
   "Other."** RQ2's escape-rate finding (0%) is now confirmed on the full corpus,
   not just 5/6 of it.
6. **`needs_human_review` flags concentrate on prefix, never postfix:** 5 flags, all
   on the oracle-free prefix side (`Closure_46`, `Closure_112`, `Closure_148` under
   scientific-open; `Closure_165`, `Closure_171` under few-open) — zero on postfix.
   Proportionally more than the other five projects combined (6 flags across their
   514 classifications). All five are stated at confidence 0.8, above the 0.7
   "low-confidence" cutoff used elsewhere in this doc — the review flag and the
   numeric confidence score are evidently not the same signal; a flagged bug can
   still self-report moderate-high confidence.
7. **RQ1's cross-project chi-squared test changes once Closure is included.**
   Recomputed on the full 409-bug, 6-project prefix distribution:
   scientific-open χ²=36.01, dof=25, p=0.071 (still not significant, but a sharp drop
   from the 5-project p=0.38); **few-open χ²=49.21, dof=25, p=0.0027 — now
   significant** (was borderline non-significant at p=0.056 with 5 projects). Adding
   Closure — the largest project, and the one built around compiler internals rather
   than a general-purpose library — is enough to tip few-open's cross-project type
   distribution into a statistically real difference. Scientific-open's distribution
   is comparatively more stable across projects even with Closure included.

---

## Cross-project summary (all 6 target projects — Chart, Time, Mockito, Lang, Math, Closure)

What holds everywhere, no exceptions:
- **Agreement rate is always higher on postfix than prefix.** 6/6 projects, no
  exceptions, though the gap ranges from 3.8 points (Math) to 27 points (Time) —
  Closure's 7.9-point gap lands mid-pack. The direction is a real, repeatable effect;
  the size is not a fixed constant.
- **"Other" was never predicted once** — 0 of 1,122 classifications across all six
  projects. The open taxonomy's escape category looks structurally unused, not just
  rare — a real, final RQ2 finding now confirmed on the complete target set, not an
  early-data quirk.
- **`needs_human_review` is rare everywhere but not evenly so, and low-confidence
  flags never fire at all** (11 and 0 occurrences respectively, out of 1,122).
  Closure alone accounts for 5 of the 11 review flags despite being ~half the
  corpus by bug count — proportionally elevated, and concentrated entirely on the
  oracle-free prefix side. The model reports near-uniform high confidence
  regardless of project either way, which is itself worth a skeptical mention
  rather than being read as "the model is always right here."

What's real but project-dependent, not universal:
- **Algorithm/Method is an attractor category in every project**, but *which*
  category it gets confused with is not fixed: Checking (Lang, Time, Math, Closure —
  the four largest), Assignment/Initialization (Chart), and a genuinely diffuse
  spread including a new category, Interface/O-O Messages (Mockito). Closure shows
  this pattern at its sharpest concentration of any project (75-83% of
  disagreements are exactly this one pair). Reads as: Algorithm/
  Method's boundary is generally soft, and what it bleeds into depends on what kinds
  of bugs a given project actually has (Mockito's mocking/interface-heavy code being
  the clearest case of domain shaping the confusion pattern).

**Concrete next step, still not done:** pull `reasoning_summary` (and Scientific's
probe transcript) for a handful of Checking-vs-Algorithm/Method disagreement bugs
across Lang, Time, and Math specifically, side by side, to determine whether
Scientific's extra evidence-gathering is finding something Few misses, or whether
both strategies see the same evidence and just land differently. This is the one
finding here that would benefit most from a qualitative read before it goes in front
of the supervisor as more than a pattern observation.

---

## Which RQs this dataset actually answers

Computed via `study-drift` (scientific-open, few-open) and `study-ladder`
(few-open → scientific-open) against `artifacts_v2`'s 409 bugs, all 6 target
projects (Chart, Closure, Lang, Math, Mockito, Time — Closure at 152 of 174
active bugs; see its section above for the 22 not yet collected), plus one
direct `analysis.py` call for the RQ1 chi-squared test. Recomputed
2026-09-15 after Closure was added; prior numbers below (257 bugs, 5
projects, through 2026-09-14) are struck through inline for traceability.
`zero-free` and any `-closed` taxonomy pass were still never run for this
corpus — noted per RQ below where that matters.

**RQ1 (type distribution across projects) — DONE, and the finding changed
with Closure added.** Chi-squared cross-project test on the full 409-bug
prefix distribution: scientific-open χ²=36.01, dof=25, p=0.071 (still not
significant, was χ²=21.35/dof=20/p=0.38 at 5 projects — noticeably closer to
the 0.05 line); **few-open χ²=49.21, dof=25, p=0.0027 — now significant**
(was χ²=30.95/dof=20/p=0.056, borderline-not-significant, at 5 projects).
Adding Closure — the largest project, and the only one built around compiler
internals rather than a general-purpose library — is enough to tip
few-open's cross-project type distribution into a statistically real
difference; scientific-open's is comparatively more stable even with Closure
included. The "Checking and Algorithm/Method dominate everywhere" read still
holds directionally, but "distribution doesn't differ significantly by
project" is no longer true for few-open specifically.

**RQ2 (taxonomy coverage / escape rate) — PARTIALLY DONE, rest deliberately
not pursued.** The escape-rate half of this RQ is fully answered from the
open-pass data alone, no closed-taxonomy run needed: **0 of 1,122
classifications ever used "Other"** (was 0/514 at 5 projects), across both
strategies and now all 6 target projects. That is a solid, final 0% escape
rate, now confirmed on the complete target set. The other half of RQ2's
design (`compute_coverage_metrics`'s closed-vs-open shift kappa and KL
divergence — does removing the escape *option* itself change ordinary labels,
independent of whether escapes occur) still needs a `scientific-closed`/
`few-closed` pass that does not exist for this corpus. Deliberately not run:
given the escape rate is already 0%, the expected result (labels barely
move) is low-value relative to its cost. Recorded as a conscious scoping
decision, not a gap.

**RQ3 (four-level accuracy: strict/top-2/family/κ) — DONE, both strategies,
all 6 projects.**

| Metric | Scientific-open | Few-open |
|---|---|---|
| Strict match | 70.4% (was 73.5%) | 66.7% (was 67.7%) |
| Top-2 match | 97.1% (was 96.1%) | 98.5% (was 97.7%) |
| Family match | 94.1% (was 93.0%) | 95.6% (was 94.2%) |
| Cohen's κ (overall) | 0.508 moderate (was 0.577) | 0.392 fair (was 0.437) |

Adding Closure pulls both strict-match and overall κ down slightly for both
strategies — expected, since Closure's own strict-match (65.1%/scientific,
65.1%/few — identical rate, see its section above) and κ (0.367, the lowest
of any project) sit below the 5-project averages. Few-open's overall κ also
crosses from "moderate" into "fair" territory (Landis & Koch) once Closure
is folded in. Direction of every comparison (Scientific > Few on strict/κ,
Few > Scientific on top-2/family) is unchanged.

**RQ4 (component contribution / ablation ladder) — PARTIALLY DONE, headline
metric out of scope by choice.** The vocabulary-reduction-ratio headline
number is still only meaningful with `zero-free` as the ladder's baseline
tier; without it the formula is undefined and returns 0.0 — not a finding, a
non-result. `zero-free` was not run for this corpus and this ratio remains
consciously waived. What *is* computable between the two taxonomy-constrained
tiers (few-open → scientific-open), recomputed on all 409 bugs: both
strategies still land on exactly the same 5 of 7 ODC types (Function/Class/
Object and Timing/Serialization never fire in either — unchanged by adding
Closure); label entropy is still marginally higher under Scientific (1.447
vs 1.292, was 1.490 vs 1.421 at 5 projects) — same small signal that the
enforced loop spreads labels slightly more evenly across those 5 types
rather than piling onto Checking/Algorithm-Method, consistent with the drift
data above. Worth reporting as a secondary observation, not as the RQ4
headline result.

**RQ5 (pre/post drift + per-project reliability) — DONE, both strategies, all
6 projects.**

| Project | Scientific-open κ | Few-open κ |
|---|---|---|
| Chart | 0.672 | 0.349 |
| Closure | 0.367 | 0.301 |
| Lang | 0.546 | 0.497 |
| Math | 0.603 | 0.537 |
| Mockito | 0.499 | 0.272 |
| Time | 0.480 | 0.212 |

Scientific's κ beats Few's in every one of the 6 projects — a consistent,
non-cherry-picked signal that now extends to the full target set, largest in
relative terms where the raw agreement-rate gap was also largest (Time).
Closure is the new low point on both columns — the least reliable project
for either strategy — but the direction (Scientific > Few) holds there too.
(Not compared against the old n=44 dev-validation table here — that table
used a different, much smaller manifest and is not a valid baseline for this
corpus; see the section below for the actual old-vs-new comparison, run
against the real prior 431-bug corpus.)

**Bottom line:** RQ1, RQ3, and RQ5 are now fully answered on the complete
6-project, 409-bug target corpus with no further data collection needed —
RQ1's few-open finding actually *changed* (borderline → significant) once
Closure was added, which is itself worth flagging to the supervisor as a
"more data changed a borderline conclusion" example. RQ2's core finding (0%
escape rate) is also final on the full set; its secondary closed-vs-open
shift metric remains scoped out on purpose. RQ4's secondary metrics are
answered on the full set; its headline vocabulary-reduction number is still
the one place in the whole study where `zero-free` data would add something,
and that gap remains accepted, not accidental. Only the 22 not-yet-collected
Closure bugs (`1`, `49`-`69` except `63`, `143`) stand between this and the
full 174-bug Closure / 431-bug six-project corpus.

---

## What changed since the last reported run (old reports vs this rerun)

**Correct baseline, stated plainly:** the prior comparable run is the
431-bug, 6-project run from 2026-07-26 (`lang61_report.xlsx`,
`chart26_report.xlsx`, `time26_report.xlsx`, `mockito38_report.xlsx`,
`math106_report.xlsx`, plus Closure — Closure excluded below since this
rerun doesn't have it yet), stored on disk as `.dist/study/artifacts_full`.
This is a well-powered baseline (same per-project bug counts as this rerun:
Chart 26, Lang 61, Math 106, Mockito 38, Time 26 = 257 bugs, identical
manifests both sides) — **not** the tiny n=44 dev-validation table used
elsewhere in this doc for the RQ1-RQ5 walkthrough. Those are two different
prior corpora; don't conflate them.

**The headline aggregate number barely moved — and for one condition it got
worse:**

| Condition | OLD agreement (pre==post) | NEW agreement | Change |
|---|---|---|---|
| scientific-open | 191/257 = 74.3% | 189/257 = 73.5% | -0.8pt |
| few-open | 182/257 = 70.8% | 174/257 = 67.7% | -3.1pt |
| "Other" used (either) | 0/257 | 0/257 | unchanged |

**But underneath that flat/declining topline, a third of the individual
labels changed anyway: 86 of 257 bugs (33.5%) got a different ODC type**
(scientific-open, prefix or postfix), per project:

| Project | Bugs changed | Rate |
|---|---|---|
| Time | 12/26 | 46.2% |
| Mockito | 14/38 | 36.8% |
| Lang | 19/61 | 31.1% |
| Math | 33/106 | 31.1% |
| Chart | 8/26 | 30.8% |

**That combination — flat/declining aggregate accuracy plus 33.5% individual
churn — is label instability, not improvement.** If the pipeline fixes had
genuinely made classification better, the aggregate agreement rate should
have moved up, not sat flat (scientific-open) or dropped (few-open, -3.1pt).

**The two dominant categories traded rank, and the two strategies moved in
opposite directions.** Pre-fix type counts, scientific-open:

| Type | OLD | NEW |
|---|---|---|
| Algorithm/Method | 120 | 106 |
| Checking | 113 | 121 |

Algorithm/Method led old, Checking leads new — same 257 bugs, same
condition, ranks flipped. Few-open moved the **opposite** direction over the
same period:

| Type | OLD | NEW |
|---|---|---|
| Algorithm/Method | 148 | 156 |
| Checking | 93 | 79 |

Scientific-open drifted toward Checking; Few-open drifted further toward
Algorithm/Method, on the identical bug set and time window. That is not
consistent with one shared cause pushing every classification the same way —
it's consistent with each prompt template independently interacting with
whatever changed.

**Pooling every individual pre/post label change, 51 of 93 transitions (55%)
cross the Algorithm/Method↔Checking boundary specifically** (33
Algorithm/Method→Checking, 18 Checking→Algorithm/Method) — the same boundary
that dominates the Scientific-vs-Few strategy-disagreement pattern documented
above. One clean, uncounfounded axis (strategy disagreement, both computed
within `artifacts_v2`) plus this old-vs-new axis both point at the same soft
boundary — worth stating as "Algorithm/Method vs Checking is a genuinely
unstable line in this taxonomy," not as a taxonomy-coverage improvement.

**The "new types appeared for Lang" finding does not generalize to a
taxonomy-coverage improvement.** Pooled Function/Class/Object counts across
all 5 projects actually *dropped* for scientific-open (3 → 1) while
*increasing* for few-open (2 → 6) over the same period — opposite
directions again, and all single-digit counts. The specific Lang_23/Lang_29
bugs examined in detail are still worth citing (the new label matches the
ODC definition better than the old one, verified against the actual fix
diff) — but "the taxonomy is being used more fully now" is not a claim the
pooled numbers support.

**Leading candidate cause, not yet proven:** both classification tags in
this comparison were called via the exact same model string,
`gemini-3.1-flash-lite-preview`, but two months apart (old run: 2026-07-10;
new run: 2026-09-13). That is a rolling "-preview" alias, not a pinned
snapshot — the hosting provider can update the underlying weights behind
that name without any visible version change on our side. The taxonomy
prompt text itself is confirmed unchanged (`git diff` on `odc.py`'s
`ODC_TYPES` dict between the two runs' commits is empty). Given the
aggregate accuracy didn't improve, the most defensible explanation for 33.5%
label churn concentrated on one boundary is that model drift, not the
evidence-collection fix, is doing most of the work here. **Action for the
next run: pin an exact dated model snapshot, not a "-preview" alias**, so
this confound can't recur.

**What this is not:** evidence that the pipeline fixes (evidence-collection
`6878d90`, data-leakage `bb9d176`) improved classification results. They may
still be correct, necessary fixes for other reasons (e.g. closing a real
oracle-leak risk, per `coverage-fallback-oracle-leak`) — but this comparison
does not show them producing better labels, only different ones.

---
