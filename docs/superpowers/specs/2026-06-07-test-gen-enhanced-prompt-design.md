# Design Spec: Enhanced Test-Gen Prompt + Self-Correction Loop

**Date:** 2026-06-07  
**Branch:** icsea  
**Status:** Approved — ready for implementation

---

## Problem Statement

The initial test-gen pipeline (Time-25 trial run) revealed three distinct failures:

1. **Trigger method body leaked via `_extract_class_header` fallback.**  
   When a code snippet is a line-windowed excerpt (e.g. lines 910–918 of a class), it has no `package` declaration. The fallback `java_source[:500]` dumps the first 500 characters — which is the body of a trigger test method — directly into the LLM prompt. This is oracle leakage.

2. **Failure headlines expose the correct expected value.**  
   JUnit assertion failure messages take the form `expected:<+04:00> but was:<+03:00>`. The `expected:<X>` part is precisely what the fixed code must return. We are handing the answer to the LLM.

3. **Test class infrastructure is hidden but needed.**  
   The LLM only receives the class header (imports + `class {`). Constants like `ZONE_MOSCOW` and helpers like `doTest_getOffsetFromLocal` are invisible, forcing the LLM to invent timezone and assertion patterns from scratch. For Time-25 it invented Los Angeles 2009 from the bug reporter's example code in the bug report, then tested a non-buggy code path.

---

## Oracle Taxonomy

Invariant: anything that reveals what the *fixed* code must return is forbidden from the LLM prompt.

| Evidence | Verdict | Reason |
|---|---|---|
| Bug report text | ✅ Allowed | Public, pre-fix |
| Stack trace — exception type + frame locations | ✅ Allowed | Pre-fix observable |
| Failure headline — `was:<Y>` (buggy output) | ✅ Allowed | Describes the defect, not the fix |
| Production code snippets (buggy version) | ✅ Allowed | Pre-fix |
| Test class — package, imports, field/constant declarations | ✅ Allowed | Infrastructure, no oracle |
| Test class — non-trigger helper method bodies | ✅ Allowed | Infrastructure, no oracle |
| Test class — non-trigger `@Test` method bodies | ✅ Allowed | Patterns, no oracle |
| Failure headline — `expected:<X>` | ❌ Strip | Reveals the correct post-fix value |
| Trigger test method bodies | ❌ Strip | This IS the ground truth |
| `tests.trigger` method names in prompt | ❌ Strip | Tells LLM which methods to mimic |
| `classes.modified` | ❌ Already hidden | Post-fix oracle |

---

## Design: Option C — Collect raw, strip at prompt time

Collection stores the full unmodified test class source. Prompt building strips oracle content dynamically. This gives a complete archival record in `context.json` while guaranteeing a clean LLM input.

---

## File Changes

### 1. `models.py` — New field on `BugContext`

```python
test_class_sources: dict[str, str] = field(default_factory=dict)
# key   = fully-qualified class name ("org.joda.time.TestDateTimeZoneCutover")
# value = full raw Java source as read from work_dir at collect time
```

`from_dict` reads: `test_class_sources=dict(data.get("test_class_sources", {}))`.

Backwards-compatible: old `context.json` files without this field get an empty dict.

---

### 2. `pipeline.py` — New helper, called once in `collect_bug_context`

```python
def _collect_test_class_sources(exports: dict[str, str], work_dir: Path) -> dict[str, str]:
```

Logic:
1. Split `exports["tests.trigger"]` on commas/newlines → list of `Class::method` strings
2. Deduplicate class FQNs
3. For each FQN: resolve `work_dir / exports["dir.src.tests"] / fqn_to_path.java`
4. If file exists: store `{fqn: source}`; silently skip missing files
5. Return dict

Called in `collect_bug_context` after `export_properties` resolves, before constructing `BugContext`.

---

### 3. `test_gen.py` — Four targeted changes

#### 3a. Fix `_extract_class_header` — remove leaking fallback

```python
# Before (buggy):
return "\n".join(header_lines) if header_lines else java_source[:500]

# After (fixed):
return "\n".join(header_lines)  # returns "" for snippets with no package line
```

Callers already skip empty strings.

#### 3b. New `_clean_failure_headline(headline: str) -> str`

Strips `expected:<…> but ` from JUnit assertion messages.
Keeps `was:<…>` (what the buggy code produced — legitimate pre-fix evidence).

```python
_EXPECTED_RE = re.compile(r"expected:<[^>]*>\s+but\s+", re.IGNORECASE)

def _clean_failure_headline(headline: str) -> str:
    return _EXPECTED_RE.sub("", headline).strip()
```

Used in `build_test_gen_prompt` for the `=== OBSERVED FAILURES ===` section.

#### 3c. New `_strip_trigger_methods` + `_build_test_class_section`

`_strip_trigger_methods(source, trigger_names)`:  
Walks source line-by-line with brace-depth counting. When a method whose name is in `trigger_names` is detected, replaces its full body (from declaration to closing `}`) with a single stub comment:

```
// [trigger test 'test_DateTime_constructor_Moscow_Autumn' — body omitted]
```

Everything else (imports, constants, helpers, non-trigger tests) is kept verbatim.

`_build_test_class_section(test_class_sources, trigger_raw)`:  
Derives `trigger_names` from the `tests.trigger` string, calls `_strip_trigger_methods` for each stored class, returns a formatted string for the prompt section:

```
=== TEST CLASS INFRASTRUCTURE (trigger test bodies omitted) ===
// Test infrastructure: org.joda.time.TestDateTimeZoneCutover
package org.joda.time;
...
static final DateTimeZone ZONE_MOSCOW = ...;
private void doTest_getOffsetFromLocal(...) { ... }
// [trigger test 'test_DateTime_constructor_Moscow_Autumn' — body omitted]
...
```

`build_test_gen_prompt` uses this as the primary test-class section when `context.test_class_sources` is non-empty; falls back to the old header-only path for legacy context files.

#### 3d. New `refine_test_generation` + `_build_refine_feedback`

New fields on `TestGenResult`:
```python
refine_iterations: int = 0          # 0 = not used; 1–N = extra LLM calls made
refine_history: list[dict] = field(default_factory=list)
# each entry: {iteration, reason, java_source, compilation_success, fails_on_buggy}
```

`refine_test_generation(initial_result, context_prefix, client, d4j, max_iterations=3)`:

```
if result.fails_on_buggy is True: return immediately (already good)

original_messages = build_test_gen_prompt(context_prefix, result.prompt_style)

for iteration in 1..max_iterations:
    if result.fails_on_buggy is True: break

    reason = "compile_failed" | "passed_on_buggy"
    feedback = _build_refine_feedback(result, reason, context_prefix)

    messages = original_messages
             + [assistant: result.raw_llm_response]
             + [user: feedback]

    raw_response = client.complete_text(messages)
    java_source  = extract_java_code(raw_response)

    write → compile → run on buggy → cleanup
    append to history
    update result (carry original ground-truth fields)

return final result
```

`_build_refine_feedback`:
- **compile_failed**: Shows the compile error, asks to fix only the syntax. No oracle content.
- **passed_on_buggy**: Explains the test passed when it must fail; asks the LLM to reconsider inputs/assertions. Never mentions `expected:<X>` values or trigger method names.

---

### 4. `test_gen_analysis.py` — Refinement metrics

Added to `compute_aggregate_metrics`:

| Metric | Definition |
|---|---|
| `refinement_used_count` | bugs where `refine_iterations > 0` |
| `refinement_used_rate` | `refinement_used_count / total` |
| `refined_success_count` | bugs where refinement was used AND `fails_on_buggy=True` at end |
| `refined_success_rate` | `refined_success_count / refinement_used_count` |
| `avg_refine_iterations` | mean of `refine_iterations` across bugs that used refinement |

`_result_from_dict` updated to read `refine_iterations` and `refine_history`.

---

### 5. `cli.py` — New flags on test-gen and test-gen-batch

```
--refine                       Enable self-correction loop (default: off)
--max-refine-iterations N      Max feedback iterations (default: 3)
```

`_cmd_test_gen`: after `run_test_generation`, if `args.refine` and `not result.fails_on_buggy`, call `refine_test_generation`.

Result panel adds: `Refine iterations` row.

`_cmd_test_gen_batch`: passes `refine` and `max_refine_iterations` through to each bug's generation call.

---

## What Does NOT Change

- ODC classification pipeline (`classify`, `run`, `study-*`) — untouched
- `oracle_match`, `fails_on_buggy`, `passes_on_fixed` semantics — unchanged
- `context.json` schema is backwards-compatible — old files without `test_class_sources` get `{}`
- The ground-truth comparison fields (`trigger_test_source`, `trigger_methods`, `method_name_match`, `trigger_class_targeted`) are unchanged — they are post-LLM metrics, never sent to the LLM

---

## Usage After Implementation

```bash
# Single bug — enhanced prompt only (baseline)
python -m d4j_odc_pipeline test-gen \
  --prefix-context .dist/runs/Lang_1_prefix/context.json \
  --prompt-style full

# Single bug — enhanced prompt + self-correction loop
python -m d4j_odc_pipeline test-gen \
  --prefix-context .dist/runs/Lang_1_prefix/context.json \
  --prompt-style full \
  --refine --max-refine-iterations 3

# Batch — with refine
python -m d4j_odc_pipeline test-gen-batch \
  --artifacts-dir .dist/study/artifacts_68/ \
  --prompt-style full \
  --refine

# Analyze (now includes refinement metrics)
python -m d4j_odc_pipeline test-gen-analyze \
  --results-dir .dist/test_gen/ \
  --export-csv
```

**Important:** re-run `collect` for any bug before running `test-gen` to populate `test_class_sources`. Old `context.json` files will fall back to the header-only path automatically.
