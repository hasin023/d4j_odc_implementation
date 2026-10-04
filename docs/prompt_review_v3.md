# Prompt review for v3 (few + scientific, pre-fix + post-fix)

Written 2026-10-05. **APPROVED by the user on 2026-10-05 (decisions 1–10 below, all "yes"; decision 7
= only the dangling-reference cleanup) and IMPLEMENTED the same day as prompt `v3-2026-10-05`**
(`prompting.PROMPT_VERSION`). Implementation record, tests, rollback and the pilot runbook:
`docs/study_execution_log.md` → "2026-10-05 — Prompt v3-2026-10-05". One wording fix beyond the
decisions: the user message's first line also says "exactly one type from the taxonomy" (same reason as
decision 2). Terminology as in
`docs/few_shot_terminology.md` ("IBM illustration" is our docs-only name for the short cases IBM lists
under "Examples:"; the model never sees that word).

## 1. Aim and rules of the review

- **Fixed anchors:** IBM ODC v5.2's definitions and "Examples:" (verbatim in `odc.py`, guarded by
  `tests/test_odc.py::IbmDefinitionTests`) and the 7 approved worked examples
  (`docs/worked_examples_draft.md`). Both stay in every `few` and `scientific` variant.
- **Every other line** must have a source in the order IBM → peer-reviewed paper → our manual analysis
  → Claude's reasoning approved by the user (research doc Q6.1, decision 9). Lines written before July
  2026 are distrusted by default.
- **Remove** any line that contradicts IBM's text or the worked examples. Change as little as possible
  otherwise.
- **Modular:** the worked-example block must stand alone (no other block refers to it), so a future
  zero-shot variant with IBM's taxonomy only can be built by leaving that block out. That variant is
  not built now.
- Scope: `few` and `scientific`, both evidence modes, closed and open taxonomy (8 variants). `zero` is
  out of scope (separate prompt; `zero-free` pending with the supervisor).

## 2. Where each block appears, and when its current wording was written

| # | Block | Code | few pre | few post | sci pre | sci post | Wording written |
|---|---|---|---|---|---|---|---|
| 1 | Role line | `_build_system_prompt`, `_agent_system_prompt` | ✓ | ✓ | ✓ | ✓ | April 2026 |
| 1b | Pre-fix task line | inline in `_build_system_prompt` | ✓ | – | **–** | – | April 2026 |
| 2 | Post-fix guidance | `_fix_diff_guidance` | – | ✓ | – | ✓ | 2026-04-14 (`9151ae9`), unchanged |
| – | Scientific loop instructions | `_agent_system_prompt` | – | – | ✓ | ✓ | 2026-09-27 (`deb9f29`); not reviewed here |
| 3 | Critical rules | `_critical_rules` | ✓ | ✓ | ✓ | ✓ | substance April; FCO rule re-merged 2026-08-10 (`6878d90`) |
| 4a | Taxonomy: IBM definitions + "Examples:" | `odc.py` `summary`/`examples` | ✓ | ✓ | ✓ | ✓ | 2026-10-04 (IBM verbatim) |
| 4b | Taxonomy: "When to / When NOT to choose" | `odc.py` `indicators`/`distinguish_from` | ✓ | ✓ | ✓ | ✓ | 2026-04-21 (`f79c7b2`) |
| 4c | Taxonomy: Other (open only) | `taxonomy_markdown` | ✓ | ✓ | ✓ | ✓ | 2026-07-06 (`ffe4071`) |
| 5 | JSON output format | `_json_contract` | ✓ | ✓ | turn schema | turn schema | April; Other fields July |
| 6 | Decision process | `_decision_process` | ✓ | ✓ | ✓ | ✓ | substance 2026-04-14; compressed and "first question that fits" added 2026-08-10 (`6878d90`) |
| 7 | Worked examples | `_few_shot_examples` | ✓ | ✓ | ✓ | ✓ | 2026-10-05 (approved) |
| 8 | User-message rules | `_build_user_prompt` | ✓ | ✓ (+ fix-diff rule) | evidence only | evidence only | April; Other rule July |

Note 1b: the code says `few` and `scientific` "differ ONLY by the loop" (comment above the shared blocks
in `prompting.py`), but the pre-fix task line exists only in `few`. Probably missed when `scientific`
started sharing `few`'s guidance (`deb9f29`).

## 3. Conflict test: what each guidance block would say about the 7 worked examples

✗ = points to a different type than the approved one; ? = a real risk that it does; ✓ = agrees.

| Rule | Ex1 Checking 11239 | Ex2 Assign. 12976 | Ex3 Algorithm 7508 | Ex4 Interface 13119 | Ex5 FCO 6378 | Ex6 Relationship 9055 | Ex7 Timing 4255 |
|---|---|---|---|---|---|---|---|
| 6. Decision process, "first question that fits" | ✓ Q1 | ✓ Q2 | **✗** Q1 fires first: the fix edits an `if` ("if-conditions") | ? Q2 "wrong value" (a literal `true`) before Q4 | ? Q4 "API interaction" (signature changed) before Q7 | **✗** Q1 lists "exception handling"; the symptom is an exception-handling log | ? Q3 "data-structure operation" before Q5 |
| 2. "If the diff CHANGES method signatures or API contracts → Interface" | – | – | – | – | **✗** the fix changes a signature; approved type FCO | ? the exception hierarchy as an "API contract" | – |
| 2. "If the diff ADDS a missing null/bounds check → Checking" (misses IBM's "incorrect" checks) | ✓ | – | – | – | – | – | – |
| 2. "CHANGES a value … → Assignment" (misses IBM's multiple-assignment caveat) | – | ✓ | ? the diff initializes `haveVnodes = false` | – | – | – | – |
| 3. "Do NOT default to FCO … not merely wrong behaviour in existing code" | – | – | – | – | ? existing `createThriftClient` does fail | – | – |
| 8. "If code snippets show existing logic producing wrong results, this is usually NOT FCO" | – | – | – | – | **✗** existing logic fails, yet the type is FCO | – | – |
| 4b. Checking "When to": "predicate logic …" | ✓ | – | ? the fix changes a predicate | – | – | – | – |
| 4b. Algorithm "When NOT": "If the fix is primarily a missing/incorrect guard, use Checking" | – | – | ? the changed `if` reads as an "incorrect guard" | – | – | – | – |
| 4b. Interface "When to": "… or parameter signature …" | – | – | – | ✓ | ? signature changed | – | – |
| 4b. Timing "When to": "operation order …" (not in IBM) | – | – | – | – | – | – | ✓ |

Source of each judgment: the approved worked examples' own Type and Why-not lines, which rest on IBM.

## 4. Evaluation block by block

### 1 / 1b. Role and task line
- Role: Anthropic's guide recommends a role; Zheng et al., Findings of EMNLP 2024, pp. 15126–15154
  (https://aclanthology.org/2024.findings-emnlp.888/) found personas "do not improve model performance"
  and their effect "can be largely random". **Keep unchanged** (no gain expected from removing it, and
  it is not a technique we rely on).
- Task line: says "exactly one ODC defect type", which is wrong in open mode ("Other" is not an ODC
  type), and exists only in `few`. **Change** and share it with `scientific` (pre-fix only), carrying
  IBM §4.2's rule so the prompt states it in IBM's words (tier 1):
  > Your job is to classify one bug into exactly one type from the taxonomy below, using ONLY the
  > provided pre-fix evidence. In ODC, a defect type describes "the actual correction that was made"
  > (IBM ODC v5.2), so judge what kind of correction the evidence shows the bug needs.

### 2. Post-fix guidance
- Keep: the first two lines and the "IMPORTANT: The diff is the GROUND TRUTH …" line (IBM §4.2).
- **Drop the 7 "If the diff … → type" lines.** One contradicts IBM (signatures are under IBM's
  *Algorithm* illustration (3), "The number and/or types of parameters of a method or an operation are
  incorrectly specified") and worked example 5; two are incomplete against IBM; one is wider than IBM.
  As surface rules they match the failure our manual analysis saw in post-fix runs (finding 7: "the
  diff's surface form … suggested another type").
- Add the same IBM sentence as 1b, worded for the diff: "In ODC, a defect type describes "the actual
  correction that was made" (IBM ODC v5.2), so classify the nature of this change."

### 3. Critical rules
- "Do NOT default to 'Function/Class/Object' — …": **drop.** IBM's FCO definition ("should require a
  formal design change") and worked example 5's "Why not Algorithm" now teach this boundary with IBM's
  words; the rule's "not merely wrong behaviour in existing code" puts example 5 at risk (§3). Warning:
  v2's 97.8% for three types cannot show the rule is unnecessary (the rule may be why FCO was rare), so
  removing it may shift RQ1's type distribution; log it.
- "Read the code snippets carefully. The type of fix needed determines the ODC type.": **drop as a
  duplicate**; 1b and 2 now carry this in IBM's words.
- "Do not use benchmark familiarity, project reputation, or hidden fix knowledge.": **keep.** Not an ODC
  rule; it guards against memorization (threat 4 in `docs/RQ_standing_assessment.md` §9).

### 4. Taxonomy
- 4a IBM text: unchanged, including IBM's own heading "Examples".
- 4b "When to / When NOT to choose" (April, no recorded source, one sentence traces to IBM): a third
  paraphrase of each type next to IBM's own text, with drift (Timing's "operation order", Interface's
  "parameter signature") and four risks against the worked examples (§3). **Proposed: stop rendering
  both fields**, so each type shows IBM's Definition and IBM's Examples only. This reverses the earlier
  decision to keep our guidance fields, so it is a separate decision. The fields can stay in `odc.py`
  unrendered, for history.
- The header line "Read the definitions carefully — each type has specific indicators and boundaries."
  becomes "Read the definitions carefully." if 4b goes.
- 4c Other: **only** remove the dangling reference "ONLY after you have explicitly worked through all 7
  diagnostic questions" if block 6 goes, keeping "can state, for EACH of the 7 types, a concrete
  evidence-based reason why it does not apply". Its "LAST RESORT" wording affects RQ2 and the deferred
  leave-one-type-out check (`docs/other_category.md` §5), so it is a supervisor question, not changed.
- Wrap the taxonomy in `<odc_taxonomy>` tags (see block 7).
- The "Family" in each type header is not IBM (Thung et al. 2012 families); the analysis uses it
  (`comparison.py`). Out of scope; unchanged.

### 5. JSON output format
Unchanged. Its `alternative_types[{type, why_not_primary}]` and "explaining WHY this ODC type was chosen
over alternatives" already match the worked examples' "Why not" lines.

### 6. Decision process
**Drop.** It is a fourth paraphrase of the types, it drifts from IBM ("exception handling" under
Checking; "lifecycle ordering" under Timing; "must stay aligned" under Relationship), and its ranking
rule "Choose the BEST matching type from the first question that fits" (added 2026-08-10, no source)
contradicts IBM's Assignment caveat ("a fix involving multiple assignment corrections may be of type
Algorithm") and sends worked examples 3 and 6 to Checking (§3). Checking ↔ Algorithm is our least stable
boundary (manual analysis finding 9), and the ranking puts Checking first. What it was for, a way of
reasoning, is now shown by the worked examples; Anthropic's guide (checked 2026-10-05): "Present each
example as a problem, the method to apply, and the expected answer."
- Optional replacement (Claude's text, tier 4, not recommended): a three-step procedure "identify the
  correction; pick the type whose IBM definition describes it; name the closest rival and why not".
  Not recommended because the JSON already asks for the rival and the worked examples show the method.

### 7. Worked examples
Content approved. Wrap in `<worked_examples>` with one `<example>` per bug (Anthropic's guide: "Wrap
examples in `<example>` tags (multiple examples in `<examples>` tags) so Claude can distinguish them
from instructions"; a practitioner source written for Claude, our model is Gemini). Headings "##
Worked examples", "### Worked example N: <type>". Intro:
> The short examples inside each definition above are IBM's. The worked examples below are real bugs
> from other projects (Apache Cassandra and HBase), each labeled by ODC researchers, with the evidence,
> the real fix, the type the fix points to, and, for most, why a close type does not fit. They show how
> to reason; they are not related to the bug you are classifying.
Position unchanged: last in `few`'s system prompt (recency, Zhao et al.; decision 6); in `scientific`
followed only by the turn-schema line, as today. Prose, not JSON: one block feeds two answer formats
(classification JSON in `few`, turn JSON in `scientific`); the cost is Min et al.'s format point.

### 8. User-message rules (`few`)
- Drop "If code snippets show existing logic producing wrong results, this is usually NOT
  'Function/Class/Object'." (duplicate of the dropped FCO rule; contradicts example 5, §3).
- Change "Examine code snippets line-by-line to determine the root cause mechanism, working through the
  system prompt's Classification Decision Process." to end after "mechanism." if block 6 goes.
- Keep the rest ("Use ONLY the evidence", needs_human_review, allowed types, Other, the post-fix
  "CAREFULLY examine the fix_diff_oracle … The nature of the change determines the ODC type.").
- Not now: Anthropic's "Put longform data at the top … Queries at the end" would reorder the message
  (evidence first). Practitioner, Claude-specific, and a pure reorder; leave for later.

## 5. Resulting order of the system prompt

`few`: role → task line (pre-fix) or post-fix guidance → rule (no memorization) → `<odc_taxonomy>` (IBM
Definition + Examples per type; Other in open mode) → JSON output format → `<worked_examples>`.

`scientific`: role (+ "working as a scientific-debugging agent") → task line (pre-fix) or post-fix
guidance → loop instructions → rule → `<odc_taxonomy>` → `<worked_examples>` → turn-schema line.

Future IBM-only zero-shot variant: the same minus `<worked_examples>`.

## 6. Tests and records affected

- `tests/test_prompting.py`: lines 74–75 (`few` must contain "Classification Decision Process" and
  "Classification Examples"), the `### Example {i}:` loop just before line 500, and
  `test_decision_tree_still_covers_all_seven_boundaries` (503–508) → rewritten or removed. Lines 112
  and 120–121 are `zero` "must NOT contain" checks and stay valid; new tests for the worked-example block (7, approved order, one per type, no
  Other, same in both modes, absent from `zero`), the shared task line, and "nothing references the
  worked-example block".
- `tests/test_agent.py` 598–605: drop the `_decision_process` assertion; keep the `GROUND TRUTH` checks.
- `tests/test_open_taxonomy.py` 80, 99: `LAST RESORT` stays.
- All changes ship as **one tagged prompt version**, recorded in every classification artifact and in
  one `docs/study_execution_log.md` entry. With several changes at once, the 13-bug pilot
  (`manifest_alvee13.json`) matters more, and v3 results are not attributable change-by-change against
  v2 (v2 also predates the loop-v2 changes).

## 7. The decisions as approved (2026-10-05)

1. Role line unchanged. 2. Shared pre-fix task line with IBM's "actual correction" sentence.
3. Post-fix guidance: drop the 7 mapping lines, add the IBM sentence. 4. Critical rules: only "no
benchmark familiarity". 5. Stop rendering "When to / When NOT to choose" (reverses the earlier
decision to keep our guidance fields). 6. Drop the decision process, no replacement. 7. Other: only
remove the reference to the decision process. 8. User message: drop the FCO line and the
decision-process reference. 9. Tags around the taxonomy and the worked examples, new intro and
headings. 10. One tagged prompt version, one log entry, the 13-bug pilot first; full run or rollback
decided by the user on the pilot.

On the FCO rule the user asked whether IBM's definition and the worked example cover it: yes — IBM's
"should require a formal design change …" sets the bar and example 5's "Why not Algorithm" applies it;
the only open point is that v3's FCO rate may differ from v2's, which is logged, not fixed by
reordering blocks.
