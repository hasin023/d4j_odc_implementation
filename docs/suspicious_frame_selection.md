# Suspicious-frame selection & context.json evidence noise

> Written 2026-08-10. Companion to `docs/odc_alignment_audit.md` (which covers
> the fix-leak sanitization invariant) — this doc covers a *different* axis:
> how `suspicious_frames`/`coverage` are selected, and why several
> `context.json` fields are trimmed before they reach the LLM prompt.
> Read `docs/JSS_HANDOFF.md` first for the pipeline's overall shape.

## 1. How suspicious frames are selected

### The problem this fixes

`collect_bug_context` (`pipeline.py`) used to select `suspicious_frames`
purely from the failing test's raw stack trace, in trace order, after
dropping JUnit/Ant/JDK frames (`_is_framework_class`) and preferring
non-test frames over test frames (`_select_suspicious_frames`). That
heuristic has a hard failure mode: **many Defects4J bugs never throw through
the buggy class at all.** The failure is an `assertTrue`/`assertEquals`
inside the *test* method itself, comparing an already-wrong value that was
computed earlier, silently, inside the buggy production code. `Closure-150`
is a worked example: `TypedScopeCreator` (the actually modified class) does
not appear anywhere in the stack trace — the trace is 100% test/JUnit/Ant/
JDK-reflection frames. `_select_suspicious_frames` then falls back to test
frames only, and the LLM never sees a single line of the real buggy class.

This is not a Defects4J-specific quirk — it's the general limitation of
stack-trace-only fault localization for assertion-style failures, and it's
directly addressed in fault-localization literature: Kim et al., *SBEST:
Spectrum-Based Fault Localization Without Fault-Triggering Tests* (2024,
[arXiv:2405.00565](https://arxiv.org/pdf/2405.00565)), report stack-trace-
only localization ranks the true fault in the Top-5 for 34/60 bugs, spectrum-
based (Ochiai) alone for only 2/60 — but combining the two signals beats
either alone. The old pipeline used neither combination.

### What changed

Coverage used to make this *worse*, not better: `interesting_classes` (the
set of classes GZoltar/Cobertura instruments) was `{frame.class_name for
frame in suspicious_frames}` — i.e. coverage only ever looked at classes
the (possibly wrong) stack-trace guess had already flagged. A bug whose
stack trace missed the real class could never be rescued by coverage,
because coverage was scoped by that same miss. Worse, the fallback path
that ran `defects4j coverage` with no instrument file at all relies on
Defects4J's own default, which instruments **only `classes.modified`** —
i.e. the fix oracle. Using that as evidence-selection scope would silently
guarantee the correct answer's class is always present in a "coverage" pass,
which is a leak even if the class name itself is withheld from the LLM (the
mere presence/absence of the right class as evidence is oracle-informed).

The fix, in `pipeline.py`:

1. **`_discover_production_classes`** enumerates every `.java` file under
   `dir.src.classes` (the project's own source, not test code) — independent
   of both the stack-trace guess and `classes.modified`.
2. Coverage runs once per **trigger test** (not just the first one), each
   scoped to that full production-class instrument file, and results are
   unioned by `_merge_coverage` (max line/branch rate, union of covered
   lines) into one per-class coverage picture.
3. **`_augment_frames_with_coverage`** extends `suspicious_frames` (still
   capped at 12) with non-test, non-framework classes the coverage run
   touched but the stack trace never mentioned, ranked by `line_rate`
   descending. These synthetic frames carry `origin="coverage"` and no line
   number (code-snippet extraction falls back to the top of the file for
   them); stack-trace frames keep `origin="stack_trace"` and priority — they
   remain the higher-precision signal per SBEST's own findings.

This costs no more Defects4J invocations than before per bug (still one
`defects4j coverage` call per trigger test, which is 1-3 for nearly all D4J
bugs) — it only widens *what* each run instruments and stops using the frame
guess (or the oracle) to scope it. Running coverage against the full
*relevant* (passing) test suite for a true per-line Ochiai suspiciousness
score was considered and explicitly **not** done — it would need running the
full relevant-test suite per bug, which is not affordable at 854-bug scale;
the trigger-test-only union is the cost/benefit point chosen for this pass.

## 2. Bug-report parsing: same information, less noise

GitHub (`web_fetch.py::_fetch_github_issue`) and JIRA
(`_fetch_jira_issue`) extractors already kept only title/labels/summary/
description/priority — no comment thread, minimal. The generic/JSON
fallback path (used for trackers like the Google Code archive, e.g.
Closure's `storage.googleapis.com/.../issue-NN.json`) did not: it either
flattened the whole JSON object into dotted `key: value` lines, or — when
`response.json()` failed to parse cleanly for whatever reason — fell all the
way back to the **raw response text**, which for Google-Code-style reports
means literal `<`-escaped HTML tags surviving JSON decoding as literal
`<b>...</b>` markup, opaque `commenterId` integers, Unix epoch `timestamp`s,
and empty `"attachments":[]` arrays per comment — none of which carry any
classification signal, all of which are pure token bulk. That kind of
irrelevant-context bulk is exactly what degrades LLM reasoning quality, not
just via position (Liu et al., *Lost in the Middle*, 2024) but via raw
volume independent of position (`arXiv:2510.10276`).

`_format_tracker_json` now detects the Google-Code comment-array shape and
renders it as `Comment N (YYYY-MM-DD): <text>` lines — every comment's
actual text survives, `commenterId`/`attachments` don't, epoch timestamps
become dates. `_flatten_json_for_display` (the generic fallback for any
other JSON shape) now runs `html_to_text` on every leaf value (strips stray
tags, decodes entities) and drops the same noise-key set
(`commenterId`/`userId`/`attachments`) by name wherever it appears. No
scraping logic changed — this is purely how already-fetched content gets
turned into text.

`sanitize_bug_report`/`sanitize_bug_info` (`prompting.py`, unchanged by this
work) still do their job downstream: fix-metadata and comment-thread
stripping, applied only to the pre-fix arm (see §3).

## 3. Fix-diff vs. full fixed source (post-fix arm)

`d4j-checkout <bug_id>f` does check out the **complete** fixed source, not
just a diff — `_collect_fix_diff` (`pipeline.py`) already does exactly this
into a temporary sibling checkout, diffs it against the buggy checkout with
`difflib.unified_diff`, and deletes the fixed checkout afterward. So "give
the LLM the full fixed source instead of a diff" is technically possible.

It's deliberately not done: the buggy version of the same class is already
shown via `code_snippets`, so a full fixed file would be ~90% duplicate text
of what's already in the prompt — more noise, not less. A unified diff is
strictly more information-dense for exactly the judgment ODC needs (the
`qualifier` attribute — Missing/Incorrect/Extraneous — reads directly off
`+`/`-` lines). **Diff-only stays the design for the post-fix arm.**

## 4. Where sanitization happens (context.json stays raw)

All of the above (bug-report formatting aside, which happens once at
collection time in `web_fetch.py`) follows the existing project convention:
**`context.json` is never trimmed.** It stores the full evidence — every
stack-trace frame, every code snippet, the untouched `bug_info`/
`bug_report_content` text — because it's the expensive artifact to
regenerate (see root `CLAUDE.md`) and because different prompt strategies
need different views of the same evidence.

Trimming happens only in `prompting.py::_context_payload`, at prompt-build
time, per LLM call:

- `bug_info`: fix-revealing sections (`List of modified sources`, `Revision
  ID/date (fixed version)`) strip in the **pre-fix arm only**
  (`sanitize_bug_info`); local-machine-path/corpus-size lines (`Script dir`,
  `Base dir`, `Major root`, `Repo dir`, `Commit db`, `Number of bugs`) strip
  in **both arms** (`_strip_bug_info_noise`) — they're noise regardless of
  which arm is running, never fix-derived.
- `bug_report_description`: comment-thread/status/resolution sanitization
  in the pre-fix arm only (`sanitize_bug_report`, unchanged).
- `stack_trace_excerpt`: filtered through the same framework-prefix
  blocklist as `suspicious_frames` before capping to 15 lines
  (`_filter_stack_trace_noise`) — the raw first-15-lines excerpt used to be
  dominated by JDK-reflection/Ant boilerplate for assertion-style failures
  (10 of 15 lines, for Closure-150).
- `metadata.tests.relevant`: collapsed to a count (`"N relevant test
  classes (list omitted)"`) instead of the full semicolon-separated class
  list — it has no bearing on ODC type/impact and was pure token bulk (23
  entries for a typical Closure bug). `tests.trigger` (the actually failing
  test) is kept verbatim.
- `code_snippets`: `_extract_test_source` now skips emitting a `"Test
  source: ..."` entry when a `"Stack frame from ..."` entry already covers
  the same `(class_name, focus_line)` — this happened whenever
  `_select_suspicious_frames` fell back to test frames, producing two
  near-identical snippets of the same method under different `reason`
  labels.
- `hidden_oracles` (`classes.modified`) is still never included in the
  payload at all — collection-time-only, excluded by construction.

None of this changes what's written to `context.json` on disk; it only
changes what `build_messages`/`_context_payload` send to the LLM.
