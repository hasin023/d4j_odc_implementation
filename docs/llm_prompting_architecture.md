# LLM prompting architecture: what we send, and why system/user are separate

> Written 2026-08-10. Covers two things for the thesis methodology section:
> (1) the exact, field-by-field inventory of everything sent to the LLM for
> each of the 3 strategies (`zero`/`few`/`scientific`) — grounded in the
> current code, re-verify against `prompting.py`/`agent.py` if either
> changes; (2) why this pipeline uses separate system/user messages instead
> of one combined prompt, with literature backing and evidence from our own
> provider integrations. Companion to `docs/suspicious_frame_selection.md`
> (what's IN the evidence) and `docs/condition_model.md` (the 2-variable
> condition model this prompting layer implements).

---

## Part 1 — Exact artifact inventory per strategy

Every strategy's **evidence** comes from the same function,
`prompting.py::_context_payload(context)` — this is deliberate: "Both
styles get the same evidence budget to avoid confounds in RQ2.2. The only
difference between scientific and direct is the system prompt"
(`prompting.py:503-504`). What differs across strategies is (a) how much of
that evidence reaches the model up front vs. behind on-demand probes, and
(b) the instructional prose wrapped around it.

### 1.1 The shared evidence object — `_context_payload`

Every strategy's user-facing evidence is built from exactly these fields,
in this order, each capped as shown (`prompting.py:412-572`):

| Field | Source (`context.json`) | Cap | Notes |
|---|---|---|---|
| `project_id`, `bug_id`, `version_id` | verbatim | — | |
| `metadata` | `context.metadata`, minus `classes.modified` | — | `tests.relevant` collapsed to a count string, not the full class list (`prompting.py:447-450`); `tests.trigger` kept verbatim |
| `bug_info` | `context.bug_info` (raw `defects4j info` text) | — | fix-revealing sections (`List of modified sources`, `Revision ID/date (fixed version)`) stripped in the **pre-fix arm only**; local-machine-path/corpus-size lines (`Script dir`, `Base dir`, etc.) stripped in **both** arms |
| `bug_report_description` | `context.bug_report_content` (cleaned bug-tracker text, see `docs/suspicious_frame_selection.md` §2) | — | comment-thread/status/resolution sanitized in the **pre-fix arm only** (`sanitize_bug_report`) |
| `failing_tests` | `context.failures` | first **5** failures; each `stack_trace_excerpt` capped at **15** lines, filtered through the same JUnit/JDK/Ant framework blocklist as frame selection | test_name, headline, stack_trace_excerpt |
| `suspicious_frames` | `context.suspicious_frames` | first **10** | class_name, method_name, file_name, line_number, `origin` (`"stack_trace"` or `"coverage"` — tells the model whether this class crashed or was merely touched by the trigger test) |
| `production_code_snippets` | `context.code_snippets` where `reason` doesn't start with `"Test source:"` | first **8** | class_name, reason, file_path, start_line, end_line, focus_line, content (line-numbered text, `>>` marks the focus line) |
| `test_code_snippets` | `context.code_snippets` where `reason` starts with `"Test source:"` | first **3** | same shape as above |
| `coverage_summary` | `context.coverage` | first **6** classes, each capped at top **10** covered lines | class_name, line_rate, branch_rate, top_covered_lines (line_number + hits) |
| `fix_diff_oracle` | `context.fix_diff` | **only present in the post-fix arm** | note explaining it's oracle information + the unified diff (capped at collection time to 8000 chars) |

**Deliberately excluded from every strategy's payload:**
- `hidden_oracles.classes.modified` — the fix-location oracle, collection-time-only, never serialized into any prompt.
- `notes` — collection-run bookkeeping (compile/test/coverage exit codes, raw Ant build stderr) — zero classification signal, stripped from the payload entirely as of 2026-08-10 (still in `context.json` for debugging).
- `exports` (classpath strings, source directory paths) — never included in the payload at all.
- `work_dir`, `defects4j_command`, `created_at` — never included.

### 1.2 `zero` strategy

**System message** (`_build_zero_system_prompt`, `prompting.py:605-644`, ≈124 words):
- Role line ("You are a software defect analyst").
- One sentence stating the task (classify into a defect type).
- If post-fix: 2 sentences noting the fix diff is available.
- The **simplified JSON contract** (`_naive_json_contract`, `prompting.py:647-657`): `defect_type` (free text, the model's own words), `confidence`, `reasoning_summary`, `root_cause`, `symptom`.
- **Contains zero ODC vocabulary** — no type names, no taxonomy, no decision tree, no worked examples, no Impact attribute. Verified by `tests/test_prompting.py::test_naive_excludes_*`.

**User message** (`_build_user_prompt`, zero branch, `prompting.py:212-236`):
- 4-5 generic instruction bullets ("use only the evidence", "examine code snippets carefully", etc.) — no ODC references.
- `"\n\nEvidence:\n" + json.dumps(_context_payload(context), indent=2)` — the full evidence object from §1.1.

### 1.3 `few` strategy

**System message** (`_build_system_prompt`, `prompting.py:51-121`, ≈2,000-2,220 words as of the 2026-08-10 conciseness pass):
1. Role line + fix-diff-aware preamble (if post-fix: a 7-line mapping from diff-shape to ODC type).
2. CRITICAL RULES (2 bullets: don't default to Function/Class/Object; don't use benchmark familiarity/hidden fix knowledge).
3. `taxonomy_markdown(taxonomy_mode)` (`odc.py:350-386`) — full definitions of all 7 ODC types (or 7+Other in open mode): summary, when-to-choose, when-NOT-to-choose (`distinguish_from`), worked mini-examples, per type.
4. `impact_markdown()` (`odc.py:236-266`) — all 13 v5.2 Impact categories + Unknown, with guidance.
5. The full JSON response contract (`_json_contract`, `prompting.py:575-602`): `odc_type`, `family`, `impact`, `target`, `qualifier`, `confidence`, `needs_human_review`, `observation_summary`, `reasoning_summary`, `evidence_used`, `evidence_gaps`, `alternative_types` (+ `other_*` fields in open mode). `hypothesis`/`prediction`/`experiment_rationale` are NOT part of `few`'s contract — `classification_response_schema(strategy=...)` in `llm.py` only requires them for `scientific`, where the turn loop earns them through real commit-before-observe ordering.
6. **Classification Decision Process** — 7 diagnostic questions, one per ODC type, each a one-line "signal → type" mapping (tightened 2026-08-10; previously verbose, same 7 questions/type coverage).
7. **Classification Examples** — 5 fully worked examples (`_few_shot_examples`, `prompting.py:150-186`), each with a symptom, a code snippet, the classification, and explicit "NOT type X because Y" reasoning for 1-2 alternative types.

**User message** (`_build_user_prompt`, few branch, `prompting.py:238-260`):
- Evidence mode line (pre-fix vs post-fix).
- IMPORTANT ANALYSIS RULES: 6-7 bullets pointing back at the decision process, the allowed type list, the Impact instruction, and (open mode only) the "Other is a last resort" rule.
- `"\n\nEvidence:\n" + json.dumps(_context_payload(context), indent=2)`.

### 1.4 `scientific` strategy — the multi-turn agentic loop

Unlike `zero`/`few` (one system + one user message, one API call), `scientific` (`agent.py::run_agentic_classification`) is a **conversation that grows every turn**, up to `AGENT_MAX_TURNS = 6`.

**System message** (`_agent_system_prompt`, `agent.py:176-220`, ≈1,565-1,746 words — sent **once**, not repeated per turn):
- Role line + loop-protocol explanation: every turn the model must emit `hypothesis`, `prediction`, then either `action: "request_evidence"` (with a `probe`) or `action: "conclude"` (with the full classification).
- The 5 available probes, each with what argument they take (see below).
- RULES (5 bullets): commit prediction before seeing the result; don't re-request served evidence; conclude as soon as evidence supports one type; don't default to Function/Class/Object; the final `odc_type` must be valid.
- `taxonomy_markdown(taxonomy)` and `impact_markdown()` — **the same shared functions `few` uses** (so tightening them benefits both strategies).
- The turn JSON schema description (sent as a real JSON Schema via `response_schema` on every API call, not repeated in prose).

**Turn 1 user message** (the seed, `agent.py:251-260`):
- One sentence ("Initial failure observation — truncated evidence summary, use probes for anything held back") + `json.dumps(_context_payload(context), indent=2)` — **identical evidence object to `few`'s**, per the RQ2.2 confound-control invariant in §1.1.

**Every subsequent turn** (`agent.py:267-313`), two messages get appended to the running conversation:
- `{"role": "assistant", "content": <the model's own previous turn JSON, verbatim>}` — its hypothesis/prediction/action from last turn.
- `{"role": "user", "content": "Observation (probe '<name>'):\n" + json.dumps(<probe result>)}` — the harness-executed, non-fabricatable result of whatever probe it requested. On the second-to-last turn this gets a forced-conclude notice appended.

**No taxonomy, Impact text, or protocol prose is ever re-sent** — those live once, in the system message, at conversation start (`agent.py` docstring, confirmed by trace: the loop only ever appends the model's own prior turn + the probe observation).

**The 5 probes** (`execute_probe`, `agent.py:78-169`) — all run against the SAME already-collected `context.json`, no new Defects4J execution, no filesystem access, "Tier-1... serve ONLY held-back parts of the already-collected context.json" (`agent.py:13-15`):

| Probe | Argument | Returns |
|---|---|---|
| `list_evidence` | none | Inventory: failing test names, production/test snippet class names, coverage class names, whether a bug report exists — lets the model see what's available before asking for it |
| `full_stack_trace` | test-name substring | The **full, untruncated** stack trace for a matching failure (vs. the seed's 15-line-capped, framework-filtered excerpt) |
| `snippet` | class-name substring | The **full** code snippet(s) for a matching class (same content the seed already capped to 8+3; a class beyond that cap can still be reached here) |
| `coverage` | class-name substring | The **full** covered-line list for a matching class (vs. the seed's top-10-by-hits cap) |
| `bug_report` | none | The full bug report text (sanitized the same way as the seed, in the pre-fix arm) |

This means `scientific` can, over its turn budget, see strictly **more** evidence than `few`/`zero` ever do (anything beyond the seed's caps) — but only the evidence it actually asks for, and only after committing a falsifiable prediction first. That asymmetry (bounded-but-extensible evidence, gated behind a prediction) is the methodological core of why `scientific` is expected to outperform a single fixed-evidence-budget call — not a bigger prompt, but a different information-acquisition process. (See `docs/condition_model.md` §4.2 for the citation to Kang et al., EMSE 2024 / AutoSD.)

---

## Part 2 — Why system and user prompts are separate messages, not one combined prompt

Your supervisor's challenge — "I've seen nothing like system prompt in
existing literature" — is worth answering precisely, because the honest
answer is: **the system/user split is not a paper-specific methodological
invention we made up; it's how every LLM API we actually call is built**,
and there is a growing body of ML-safety/systems literature studying what
that separation *does* to model behavior. Below is the grounding, tied to
our own code and our own three provider integrations (Gemini, Groq,
OpenRouter — all live in `llm.py` and `.env`), not a generic claim.

### 2.1 It is not our design choice — it is the wire format of the APIs we call

`llm.py` talks to two structurally different API shapes, and **both
enforce a system/non-system split at the schema level**, not just as a
naming convention we adopted:

- **OpenAI-compatible providers (Groq, OpenRouter, and any future
  `openai-compatible` provider — SambaNova, etc., per
  `docs/llm_model_selection.md`)**: `_complete_openai_compatible`
  (`llm.py:196-221`) sends `{"model": ..., "messages": [...]}` to
  `/chat/completions`, where `messages` is a list of `{"role": "system" |
  "user" | "assistant", "content": ...}` objects — the **ChatML** format
  OpenAI introduced with the ChatGPT/Whisper API in March 2023 and which
  became the de facto standard adopted across essentially every subsequent
  chat-completion API and open-weight chat template. The `role` field is
  not decorative — providers train and serve these roles with different
  positional/attention treatment.
- **Gemini** (our default provider, `GEMINI_API_KEY` already configured):
  `_complete_gemini` (`llm.py:223-265`) does something stronger than just
  tagging a role — it puts the system content in a **structurally separate
  top-level API field**, `system_instruction` (`llm.py:237-241`), entirely
  outside the `contents` array that carries the user/model turns.
  `_gemini_system_instruction`/`_gemini_contents` (`llm.py:387-403`)
  explicitly filter `role == "system"` messages OUT of `contents` and INTO
  this separate field — Gemini's API does not merely label system content
  differently, it does not accept it in the same channel as conversation
  content at all.

So for this pipeline specifically: dropping the system/user distinction
and sending one combined prompt would require either (a) synthesizing a
fake role split ourselves before every call (defeating the point), or (b)
stuffing everything into Gemini's `contents` array with no
`system_instruction`, which the code deliberately avoids — the split isn't
a stylistic preference layered on top of the API, it *is* the API contract
for the model we actually classify most bugs with.

### 2.2 What the literature says the split is *for*

- **Wallace, Xiao, Leike, Weng, Heidecke, Beutel (OpenAI), "The Instruction
  Hierarchy: Training LLMs to Prioritize Privileged Instructions,"
  arXiv:2404.13208 (April 2024).** Formalizes exactly this distinction as a
  privilege hierarchy: system-level instructions (from the application
  developer) are trained to take priority over user-level content, and
  user-level content over third-party/tool content. The paper's stated
  motivation is that *without* this separation, models treat
  developer-authored task instructions and arbitrary input content as
  equally authoritative — which is precisely the risk in our pipeline if
  the ODC taxonomy/decision-tree instructions (system, developer-authored,
  stable) were flattened together with `bug_report_description` (user
  content, scraped from a public bug tracker, i.e. *external, unreviewed
  text*). Keeping the taxonomy/rules in the system role and the scraped
  bug-report text in the user role's `Evidence:` JSON block is the
  practical application of that hierarchy: instructional content stays
  privileged, external data stays data.
- **Ouyang et al. (OpenAI), "Training language models to follow
  instructions with human feedback" (InstructGPT), NeurIPS 2022.** The
  foundational RLHF paper establishing that models can be trained to
  reliably distinguish and follow structured instruction framings over raw
  next-token continuation — the underlying capability that makes a
  system-role instruction set (taxonomy + rules + JSON contract) something
  a model can be expected to hold *consistently across turns* while the
  user content varies. This is the capability our `scientific` strategy
  leans on hardest: the taxonomy/protocol is stated once, in the system
  message, and must still govern behavior 6 turns and several
  tool-observation messages later.
- **ChatML origin (OpenAI, March 2023)** — not an academic paper, an
  engineering specification, but the direct ancestor of the role-tagged
  format every provider we use now implements. Its stated design goals
  (per OpenAI's own documentation and secondary analysis) were exactly:
  (a) let the model reliably distinguish *who* said what — developer vs.
  end-user vs. the model's own prior turns — and (b) mitigate prompt
  injection by making instruction content structurally distinguishable
  from arbitrary input content. Both goals map directly onto why a bug
  report's raw text (which could, in principle, contain arbitrary strings —
  we don't control what got typed into a public tracker years ago) sits in
  a JSON evidence block inside the user message rather than being
  interpolated into the system prompt's instruction prose.

### 2.3 The practical engineering reason: caching and cost, quantified for our own study

Every production LLM API we could realistically use for this pipeline
implements **prompt caching keyed on a stable prefix** — and our
system/user split is exactly what makes that prefix stable:

- Anthropic: up to ~90% cost reduction, ~85% latency reduction on cached
  prefixes (explicit `cache_control` breakpoints).
- OpenAI: automatic caching above 1024 tokens, ~50% cost reduction, no
  extra API surface needed.
- Gemini: explicit context caching (32K-token minimum block) or the
  provider's own implicit caching depending on tier.

Within one condition (fixed `taxonomy` + `strategy`), our system message is
**byte-identical across every bug** — it's built from static functions
(`taxonomy_markdown`, `impact_markdown`, the decision tree, the worked
examples) with no per-bug interpolation at all (`_build_system_prompt`,
`_agent_system_prompt` take no `context` argument). Only the user
message's `Evidence:` JSON block changes per bug. That is precisely the
shape prompt caching is built around: a large, static, reusable prefix
(our ~2,000-2,200-word `few` system prompt, or the ~1,565-1,750-word
`scientific` one) plus a small, unique suffix per call. For a full-corpus
run — 854 bugs × 2 arms × up to 6 turns for `scientific` — that system
prompt is sent thousands of times; keeping it as a separate, unchanging
message is what lets a caching-aware provider (or a caching-aware
retry/rotation layer we might add later) avoid re-billing/re-processing it
every time. Merging system and user into one prompt per call would still
work functionally, but would throw away this entire cost/latency
optimization path on every provider we use.

### 2.4 Summary for the methodology section

State it as three independent, converging justifications, not one:

1. **It's the literal wire format.** Two of our three provider
   integrations (`llm.py`) require it — Gemini structurally, via a
   separate `system_instruction` field; the OpenAI-compatible providers
   (Groq, OpenRouter, and any `openai-compatible` addition) via the
   ChatML `role` convention nearly every model provider and open-weight
   chat template has converged on since March 2023.
2. **It encodes a privilege/trust distinction with direct literature
   backing** (Wallace et al. 2024's instruction hierarchy; the RLHF
   role-following capability from Ouyang et al. 2022) — stable,
   developer-authored task instructions (taxonomy, decision tree, JSON
   contract) in the system role; per-bug, externally-sourced evidence
   (much of it scraped from public bug trackers) in the user role as
   structured data, not instruction prose.
3. **It is the precondition for prompt caching**, which is directly
   relevant at our study's scale (854 bugs, up to 6 turns each for the
   flagship `scientific` condition) — a combined single-message prompt
   would forfeit this on every provider evaluated.
