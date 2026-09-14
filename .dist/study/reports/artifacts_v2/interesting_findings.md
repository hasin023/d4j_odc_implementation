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

## Math (106 bugs — largest project, most statistically robust)

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

## Cross-project summary (5 of 6 target projects — Chart, Time, Mockito, Lang, Math; Closure pending)

What holds everywhere, no exceptions:
- **Agreement rate is always higher on postfix than prefix.** 5/5 projects, no
  exceptions, though the gap ranges from 3.8 points (Math) to 27 points (Time) — the
  direction is a real, repeatable effect; the size is not a fixed constant.
- **"Other" was never predicted once** — 0 of 514 classifications across all five
  projects. The open taxonomy's escape category looks structurally unused at this
  point, not just rare — worth treating as a real RQ2 finding rather than an
  early-data quirk.
- **`needs_human_review` and low-confidence flags are both rare everywhere** (6 and 0
  occurrences respectively, out of 514) — the model reports near-uniform high
  confidence regardless of project, which is itself worth a skeptical mention rather
  than being read as "the model is always right here."

What's real but project-dependent, not universal:
- **Algorithm/Method is an attractor category in every project**, but *which*
  category it gets confused with is not fixed: Checking (Lang, Time, Math — the three
  largest), Assignment/Initialization (Chart), and a genuinely diffuse spread
  including a new category, Interface/O-O Messages (Mockito). Reads as: Algorithm/
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
