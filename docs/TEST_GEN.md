# Test Generation Sub-Thesis Pipeline

Reference for the "Can an LLM Write the Missing Test?" sub-thesis commands, artifacts, and metrics.

---

## Commands

### 1. Collect (buggy + fixed versions)

```bash
# Collect buggy (prefix) version — stores test class source for oracle-clean prompting
python -m d4j_odc_pipeline collect --project <Project> --bug <N> --skip-coverage

# Collect fixed (postfix) version — required for oracle (passes_on_fixed) evaluation
python -m d4j_odc_pipeline collect --project <Project> --bug <N> --postfix --skip-coverage
```

Outputs:
- `.dist/runs/<Project>_<N>_prefix/context.json`
- `.dist/runs/<Project>_<N>_postfix/context.json`

---

### 2. Generate a single test

```bash
# Baseline (no refinement)
python -m d4j_odc_pipeline test-gen \
  --prefix-context .dist/runs/<Project>_<N>_prefix/context.json \
  --postfix-context .dist/runs/<Project>_<N>_postfix/context.json \
  --prompt-style full

# With self-correction loop (up to 3 iterations)
python -m d4j_odc_pipeline test-gen \
  --prefix-context .dist/runs/<Project>_<N>_prefix/context.json \
  --postfix-context .dist/runs/<Project>_<N>_postfix/context.json \
  --prompt-style full --refine --max-refine-iterations 3

# Dry-run — inspect prompt without calling the LLM
python -m d4j_odc_pipeline test-gen \
  --prefix-context .dist/runs/<Project>_<N>_prefix/context.json \
  --prompt-style full --dry-run
```

| Flag | Default | Description |
|------|---------|-------------|
| `--prefix-context` | required | Pre-fix `context.json` (LLM input) |
| `--postfix-context` | optional | Fixed-version `context.json` (oracle evaluation) |
| `--prompt-style` | `full` | `full` · `report_only` · `snippets_only` |
| `--refine` | off | Enable self-correction loop |
| `--max-refine-iterations` | `3` | Max LLM correction turns |
| `--dry-run` | off | Render prompt to `prompt.json`, skip LLM |

---

### 3. Batch generate

```bash
python -m d4j_odc_pipeline test-gen-batch \
  --artifacts-dir .dist/study/artifacts_68/ \
  --prompt-style full --refine
```

---

### 4. Aggregate and analyze

```bash
# Analyze a results directory (baseline or refined)
python -m d4j_odc_pipeline test-gen-analyze \
  --results-dir .dist/test_gen/baseline/ \
  --export-csv

python -m d4j_odc_pipeline test-gen-analyze \
  --results-dir .dist/test_gen/refined/ \
  --export-csv
```

Outputs to `<results-dir>/aggregate/`:
- `test_gen_analysis.json` — all metrics
- `test_gen_summary.md` — markdown report
- `test_gen_results.csv` — flat CSV for statistical analysis

---

## New field in `context.json` — `test_class_sources`

Added to `BugContext` to enable oracle-clean prompting.

| Field | Type | Description |
|-------|------|-------------|
| `test_class_sources` | `dict[str, str]` | Map of FQN → full raw Java source of each trigger test class. Collected at checkout time from `dir.src.tests`. Empty `{}` on old context files (backwards-compatible). |

**How it is used in prompts:**
- Trigger test method bodies are stripped via `_strip_trigger_methods` (brace-counting parser)
- Stripped source is shown under `=== TEST CLASS INFRASTRUCTURE (trigger test bodies omitted) ===`
- Helper methods and constants (e.g. `ZONE_MOSCOW`, `doTest_*`) are visible to the LLM
- Trigger method bodies are replaced with `// [trigger test '<name>' — body omitted]`
- This gives the LLM test infrastructure context without leaking the ground-truth test assertions

---

## `test_gen_result.json` fields

| Field | Type | Description |
|-------|------|-------------|
| `project_id` | `str` | Defects4J project (e.g. `"Time"`) |
| `bug_id` | `int` | Bug number |
| `prefix_work_dir` | `str` | Buggy checkout path |
| `postfix_work_dir` | `str` | Fixed checkout path (`""` if not provided) |
| `model` | `str` | LLM model used |
| `provider` | `str` | LLM provider |
| `prompt_style` | `str` | Prompt strategy used |
| `generated_class_name` | `str` | Java class name extracted from LLM output |
| `generated_method_name` | `str` | `@Test` method name extracted |
| `generated_test_code` | `str` | Full Java source of generated test |
| `compilation_success` | `bool` | Whether the test compiled |
| `compilation_error` | `str\|null` | Compiler output on failure |
| `fails_on_buggy` | `bool\|null` | Test fails on buggy version (fault detection) |
| `passes_on_fixed` | `bool\|null` | Test passes on fixed version (`null` if no postfix) |
| `oracle_match` | `bool\|null` | `fails_on_buggy AND passes_on_fixed` |
| `trigger_methods` | `list[str]` | Ground-truth trigger test FQNs (never sent to LLM) |
| `trigger_test_source` | `str` | Ground-truth trigger test source (never sent to LLM) |
| `method_name_match` | `bool` | Generated method name matches a trigger method name |
| `trigger_class_targeted` | `bool` | Generated test references the modified class |
| `modified_class` | `str\|null` | The class the bug fix touches (`classes.modified`) |
| `buggy_stdout/stderr` | `str` | Test runner output on buggy version |
| `fixed_stdout/stderr` | `str` | Test runner output on fixed version |
| `notes` | `list[str]` | Pipeline notes (skipped steps, warnings) |
| `refine_iterations` | `int` | Number of refinement turns used (`0` = no refinement) |
| `refine_history` | `list[dict]` | Per-iteration: `reason`, `compilation_success`, `fails_on_buggy`, `passes_on_fixed` |

---

## Self-correction loop (`--refine`)

The loop triggers when `oracle_match is not True` (with postfix) or `fails_on_buggy is not True` (without postfix).

| Failure mode | Trigger condition | Feedback to LLM |
|--------------|------------------|-----------------|
| `compile_failed` | `compilation_success = False` | Compiler error text; asked to fix |
| `passed_on_buggy` | `fails_on_buggy = False` | "Test passed on buggy version; probe the defect differently" |
| `oracle_fail` | `fails_on_buggy = True` AND `passes_on_fixed = False` | "Test fails on fixed version too; correct the expected value" |

**Oracle integrity**: feedback messages never contain `expected:<X>` values, trigger method names, or post-fix source code.

The loop stops as soon as `oracle_match = True` or `max_refine_iterations` is exhausted.

---

## Aggregate metrics reference

| Metric | Definition |
|--------|-----------|
| `compilation_rate` | compiled / total |
| `fault_detection_rate` | fails_on_buggy / compiled |
| `oracle_pass_rate` | oracle_match / compiled |
| `method_name_match_rate` | method_name_match / total |
| `class_targeting_rate` | trigger_class_targeted / total |
| `refinement_used_rate` | bugs with refine_iterations > 0 / total |
| `refined_fault_kept_rate` | of refined: still fails_on_buggy after refine |
| `refined_oracle_match_rate` | of refined: achieved oracle_match through refine |
| `avg_refine_iterations` | mean iterations across bugs that used refinement |

---

## Output layout

```
.dist/test_gen/
├── baseline/                  # --prompt-style full, no --refine
│   ├── <Project>_<N>/
│   │   ├── test_gen_result.json
│   │   ├── generated_test.java
│   │   └── test_gen_report.md
│   └── aggregate/
│       ├── test_gen_analysis.json
│       ├── test_gen_summary.md
│       └── test_gen_results.csv
└── refined/                   # --prompt-style full --refine
    ├── <Project>_<N>/
    │   ├── test_gen_result.json   # refine_iterations > 0
    │   ├── generated_test.java
    │   └── test_gen_report.md
    └── aggregate/
        ├── test_gen_analysis.json
        ├── test_gen_summary.md
        └── test_gen_results.csv
```

> **Note**: `prompt.json` (written by `--dry-run`) is gitignored — regenerate on demand.
