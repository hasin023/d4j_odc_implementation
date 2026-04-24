# CLI Usage

Commands are provided in both **PowerShell** (Windows) and **Bash** (Ubuntu/Linux/WSL) variants. Copy from the section that matches your environment.

---

## `collect` — Build pre-fix context

Checks out the buggy version, runs tests, fetches all evidence, and saves `context.json`.

**Smart defaults:**

- `--work-dir` defaults to `work/<project>_<bug>_prefix` (or `_postfix` with `--include-fix-diff`)
- `--output` defaults to `.dist/runs/<project>_<bug>_prefix/context.json` (or `_postfix`)

**PowerShell (Windows):**

```powershell
# Minimal — all paths auto-computed
python -m d4j_odc_pipeline collect `
  --project Lang --bug 1 `
  --skip-coverage

# Post-fix mode
python -m d4j_odc_pipeline collect `
  --project Lang --bug 1 `
  --include-fix-diff --skip-coverage

# With explicit paths (overrides defaults)
python -m d4j_odc_pipeline collect `
  --project Lang --bug 1 `
  --work-dir .\work\Lang_1b `
  --output .\artifacts\Lang_1\context.json `
  --skip-coverage
```

**Bash (Ubuntu/Linux/WSL):**

```bash
# Minimal — all paths auto-computed
python -m d4j_odc_pipeline collect \
  --project Lang --bug 1 \
  --skip-coverage
```

---

## `classify` — Classify an existing context

Sends evidence to the LLM and produces classification + report.

When `--output` and `--report` are omitted, they default to the same directory as `--context`:

- `classification.json` and `report.md` alongside `context.json`

**PowerShell (Windows):**

```powershell
# Minimal (outputs go next to context.json)
python -m d4j_odc_pipeline classify `
  --context .\.dist\runs\Lang_1_prefix\context.json

# With explicit output paths
python -m d4j_odc_pipeline classify `
  --context .\artifacts\Lang_1\context.json `
  --output .\artifacts\Lang_1\classification.json `
  --report .\artifacts\Lang_1\report.md
```

**Bash (Ubuntu/Linux/WSL):**

```bash
# Minimal (outputs go next to context.json)
python -m d4j_odc_pipeline classify \
  --context ./.dist/runs/Lang_1_prefix/context.json
```

---

## `run` — End-to-end collection + classification

Runs both `collect` and `classify` in a single command.

**Smart defaults:**

- `--work-dir` defaults to `work/<project>_<bug>_prefix` (or `_postfix` with `--include-fix-diff`)
- All output paths default to `.dist/runs/<project>_<bug>_prefix/` (or `_postfix`)
- Outputs: `context.json`, `classification.json`, `report.md`

**PowerShell (Windows):**

```powershell
# Minimal — pre-fix (all defaults)
python -m d4j_odc_pipeline run `
  --project Lang --bug 1 `
  --skip-coverage

# Post-fix mode (outputs go to .dist/runs/Lang_1_postfix/)
python -m d4j_odc_pipeline run `
  --project Lang --bug 1 `
  --include-fix-diff --skip-coverage
```

**Bash (Ubuntu/Linux/WSL):**

```bash
# Minimal — pre-fix (all defaults)
python -m d4j_odc_pipeline run \
  --project Lang --bug 1 \
  --skip-coverage
```

---

## Switching LLM provider (with environment variables)

You can switch the default LLM provider at runtime without modifying `.env`.
Each provider has its own model/API-key pair in the environment.

**Example: switch to Groq (O120B model)**

Make sure `GROQ_API_KEY`, `GROQ_BASE_URL`, `GROQ_MODEL` are set in your environment.
Then run:

```bash
# Run with Groq default (no --provider flag needed)
python -m d4j_odc_pipeline run --project Lang --bug 1

# Or explicitly:
python -m d4j_odc_pipeline run \
  --provider groq \
  --project Lang --bug 1
```

When you omit `--model`, the pipeline auto-selects the provider-specific default
(e.g. `GROQ_MODEL`) instead of `DEFAULT_LLM_MODEL` from `.env`.

To switch back to Gemini:

```bash
python -m d4j_odc_pipeline run \
  --provider gemini \
  --project Lang --bug 1
```

**Example: switch to OpenRouter (e.g. DeepSeek)**

```bash
python -m d4j_odc_pipeline run \
  --provider openrouter \
  --project Lang --bug 1
```

This uses `OPENROUTER_API_KEY`, `OPENROUTER_BASE_URL`, `OPENROUTER_MODEL`.

**Supported providers** (via `--provider` flag and per-provider env vars):

- `gemini` (global default in `.env`)
- `groq`
- `openrouter`
- `openai-compatible`

---

## `d4j` — Defects4J proxy commands

Convenience wrappers around common Defects4J operations with formatted output:

```bash
python -m d4j_odc_pipeline d4j pids                         # List all projects
python -m d4j_odc_pipeline d4j bids --project Lang           # List bug IDs
python -m d4j_odc_pipeline d4j bids --project Lang --all     # Include deprecated IDs
python -m d4j_odc_pipeline d4j info --project Lang --bug 1   # Show bug details
```

---

## `compare` and `compare-batch` — Accuracy Evaluation

Compare pre-fix and post-fix classification results using multi-tier accuracy metrics.

**PowerShell (Windows):**

```powershell
# Compare a single bug pair
python -m d4j_odc_pipeline compare `
  --prefix .\artifacts\Lang_1\classification.json `
  --postfix .\artifacts\Lang_1f\classification.json `
  --output .\artifacts\Lang_1\comparison.json `
  --report .\artifacts\Lang_1\comparison.md

# Batch compare a directory of pairs
python -m d4j_odc_pipeline compare-batch `
  --prefix-dir .\artifacts\prefix_runs `
  --postfix-dir .\artifacts\postfix_runs `
  --output .\artifacts\batch_comparison.json `
  --report .\artifacts\accuracy_report.md
```

**Bash (Ubuntu/Linux/WSL):**

```bash
# Compare a single bug pair
python -m d4j_odc_pipeline compare \
  --prefix ./artifacts/Lang_1/classification.json \
  --postfix ./artifacts/Lang_1f/classification.json \
  --output ./artifacts/Lang_1/comparison.json \
  --report ./artifacts/Lang_1/comparison.md

# Batch compare a directory of pairs
python -m d4j_odc_pipeline compare-batch \
  --prefix-dir ./artifacts/prefix_runs \
  --postfix-dir ./artifacts/postfix_runs \
  --output ./artifacts/batch_comparison.json \
  --report ./artifacts/accuracy_report.md
```

**Batch naming convention**: directories must be named `<Project>_<Bug>_prefix/` and `<Project>_<Bug>_postfix/`, each containing a `classification.json`.

---

## `multifault` and `multifault-enrich` — Multi-Fault Analysis

Query multi-fault co-existence data from the [defects4j-mf](https://github.com/DCallaz/defects4j-mf) dataset. Supported projects: Chart, Closure, Lang, Math, Time.

**PowerShell (Windows):**

```powershell
# Query multi-fault data for a specific bug
python -m d4j_odc_pipeline multifault --project Lang --bug 1

# Query with JSON output
python -m d4j_odc_pipeline multifault --project Lang --bug 1 `
  --output .\artifacts\Lang_1\multifault.json

# Enrich an existing classification (output defaults alongside input)
python -m d4j_odc_pipeline multifault-enrich `
  --classification .\artifacts\Lang_1\classification.json
```

**Bash (Ubuntu/Linux/WSL):**

```bash
# Query multi-fault data for a specific bug
python -m d4j_odc_pipeline multifault --project Lang --bug 1

# Enrich an existing classification (output defaults alongside input)
python -m d4j_odc_pipeline multifault-enrich \
  --classification ./artifacts/Lang_1/classification.json
```

The multi-fault data directory is resolved in order: `--fault-data-dir` CLI argument → `MULTIFAULT_DATA_DIR` env var → `./fault_data/` relative to the implementation root.

---

## `study-plan`, `study-run`, and `study-analyze` — Large-Scale Batch Workflow

These commands support large studies (for example, 50-70 bugs) with paired pre-fix/post-fix runs and built-in cross-artifact analysis.

**Key features:**

- **Graceful Ctrl+C** — Press Ctrl+C once to finish the current bug and stop cleanly. Press twice to force-quit.
- **Checkpoint/Resume** — A `checkpoint.json` is written after each bug completes. Re-running the same command resumes from where it left off.
- **Progress bar** — Real-time progress display showing current bug and completion count.
- **Smart defaults** — Almost all paths are auto-computed from the manifest's `target_bugs` value.

**PowerShell (Windows):**

```powershell
# Step 1: Build a balanced manifest (output defaults to .dist/study/manifest_68.json)
python -m d4j_odc_pipeline study-plan --target-bugs 68

# Step 2: Execute prefix + postfix runs
# Artifacts go to .dist/study/artifacts_68/ — only --manifest is required
python -m d4j_odc_pipeline study-run `
  --manifest manifest_68.json `
  --skip-coverage

# To resume after interruption, just re-run the same command:
python -m d4j_odc_pipeline study-run `
  --manifest manifest_68.json `
  --skip-coverage

# Step 3: Analyze (all paths auto-derived from manifest)
python -m d4j_odc_pipeline study-analyze `
  --manifest manifest_68.json `
  --require-all-projects
```

**Bash (Ubuntu/Linux/WSL):**

```bash
# Step 1: Build a balanced manifest
python -m d4j_odc_pipeline study-plan --target-bugs 68

# Step 2: Execute prefix + postfix runs
python -m d4j_odc_pipeline study-run \
  --manifest manifest_68.json \
  --skip-coverage

# Step 3: Analyze
python -m d4j_odc_pipeline study-analyze \
  --manifest manifest_68.json \
  --require-all-projects
```

**Output layout (for `--target-bugs 68`):**

```bash
.dist/study/
├── manifest_68.json              # Generated by study-plan
├── summary.json                  # Generated by study-run
├── analysis_68.json              # Generated by study-analyze
├── analysis_68.md                # Generated by study-analyze
├── artifacts_68/                 # Generated by study-run
│   ├── prefix/
│   │   ├── Lang_1_prefix/
│   │   │   ├── context.json
│   │   │   ├── classification.json
│   │   │   └── report.md
│   │   └── ...
│   ├── postfix/
│   │   ├── Lang_1_postfix/
│   │   │   ├── context.json
│   │   │   ├── classification.json
│   │   │   └── report.md
│   │   └── ...
│   └── checkpoint.json
└── work/
    ├── prefix/
    └── postfix/
```

---

## CLI Parameters

### Common parameters (used by `collect`, `run`)

| Parameter            | Required | Description                                                                                  |
| -------------------- | :------: | -------------------------------------------------------------------------------------------- |
| `--project`          |   Yes    | Defects4J project id (`Lang`, `Math`, `Chart`, etc.)                                         |
| `--bug`              |   Yes    | Numeric bug id. Automatically suffixed to `<bug>b`.                                          |
| `--work-dir`         |    No    | Checkout directory. Defaults to `work/<project>_<bug>_prefix` (or `_postfix` with fix-diff). |
| `--defects4j-cmd`    |    No    | Override `DEFECTS4J_CMD` for this run.                                                       |
| `--snippet-radius`   |    No    | Source lines around suspicious frames. Default: `12`.                                        |
| `--skip-coverage`    |    No    | Skip the `defects4j coverage` step.                                                          |
| `--include-fix-diff` |    No    | Include buggy→fixed diff as post-fix oracle (see below).                                     |

### LLM parameters (used by `classify`, `run`)

| Parameter                              | Required | Description                                          |
| -------------------------------------- | :------: | ---------------------------------------------------- |
| `--context`                            |  Yes\*   | Path to existing `context.json`. (_`classify` only_) |
| `--output` / `--classification-output` |    No    | Path for classification JSON. Auto-derived.          |
| `--report`                             |    No    | Markdown report path. Auto-derived.                  |
| `--prompt-output`                      |    No    | Save rendered prompt messages as JSON.               |
| `--prompt-style`                       |    No    | `direct` or `scientific` (default: `scientific`).    |
| `--provider`                           |    No    | `gemini`, `openrouter`, or `openai-compatible`.      |
| `--model`                              |    No    | Model name for the selected provider.                |
| `--api-key-env`                        |    No    | Custom env var name for the API key.                 |
| `--base-url`                           |    No    | Override API base URL.                               |
| `--dry-run`                            |    No    | Build prompt only, skip LLM call.                    |

### Comparison parameters (used by `compare`, `compare-batch`)

| Parameter       | Required | Description                                         |
| --------------- | :------: | --------------------------------------------------- |
| `--prefix`      |  Yes\*   | Path to pre-fix JSON. (_`compare` only_)            |
| `--postfix`     |  Yes\*   | Path to post-fix JSON. (_`compare` only_)           |
| `--prefix-dir`  |   Yes†   | Directory of pre-fix runs. (†`compare-batch` only)  |
| `--postfix-dir` |   Yes†   | Directory of post-fix runs. (†`compare-batch` only) |
| `--output`      |   Yes    | Path for comparison JSON output.                    |
| `--report`      |    No    | Path for human-readable markdown report.            |

### Study parameters (used by `study-plan`, `study-run`, `study-analyze`)

| Parameter                          | Required | Description                                                                                          |
| ---------------------------------- | :------: | ---------------------------------------------------------------------------------------------------- |
| `--manifest`                       |  Yes\*   | Study manifest JSON path. Bare filenames resolve under `.dist/study/`.                               |
| `--output`                         |    No    | Manifest/analysis output path. Defaults include `_<target_bugs>` suffix.                             |
| `--target-bugs`                    |    No    | Desired study size for `study-plan` (default: `68`).                                                 |
| `--min-per-project`                |    No    | Minimum selected bugs per project in `study-plan` (default: `1`).                                    |
| `--seed`                           |    No    | Reproducible sampling seed for `study-plan` (default: `42`).                                         |
| `--projects`                       |    No    | Optional project subset for `study-plan`; omit to include all discovered projects.                   |
| `--allow-partial-project-coverage` |    No    | Allow incomplete project coverage during `study-plan`.                                               |
| `--artifacts-root`                 |    No    | Root output directory for paired batch artifacts. Defaults to `.dist/study/artifacts_<target_bugs>`. |
| `--work-root`                      |    No    | Root checkout directory for batch runs. Defaults to `.dist/study/work`.                              |
| `--summary-output`                 |    No    | Batch execution summary JSON path. Defaults to `.dist/study/summary.json`.                           |
| `--no-skip-existing`               |    No    | Re-run entries even when artifacts already exist (`study-run`).                                      |
| `--prompt-output`                  |    No    | Save prompt payloads for each entry (`study-run`).                                                   |
| `--prefix-dir`                     |    No    | Prefix artifact directory for analysis. Defaults to `.dist/study/artifacts_<N>/prefix`.              |
| `--postfix-dir`                    |    No    | Postfix artifact directory for analysis. Defaults to `.dist/study/artifacts_<N>/postfix`.            |
| `--report`                         |    No    | Analysis report path. Defaults to `.dist/study/analysis_<N>.md`.                                     |
| `--expected-projects`              |    No    | Explicit expected project list for `study-analyze`.                                                  |
| `--require-all-projects`           |    No    | Enforce full project coverage in `study-run` and `study-analyze`.                                    |

### Global flags

| Flag             | Description                                          |
| ---------------- | ---------------------------------------------------- |
| `-q` / `--quiet` | Suppress all rich console output (for scripting/CI). |

---

## Coverage Mode

Coverage is optional and adds line/branch-level evidence to the context.

- **With `--skip-coverage`**: Faster, simpler. Best for first runs, setup debugging, or fast batch collection.
- **Without `--skip-coverage`**: Instruments suspicious classes (`-i instrument_classes.txt`), runs coverage with the first failing test, and parses Cobertura XML. If the first attempt fails (e.g., instrumentation crash), the pipeline **automatically retries without the instrument file**. If there are no suspicious source frames, coverage is skipped automatically.

**Recommendation**: Use `--skip-coverage` until checkout/compile/test/classify are working, then remove it.

---

## Fix Diff Mode (Post-Fix Oracle)

By default, the pipeline only uses **pre-fix evidence** — the LLM never sees the actual fix. This simulates real-world bug triage.

With `--include-fix-diff`, the pipeline also:

1. Checks out the **fixed version** (`<bug>f`) in a temporary sibling directory
2. Exports source directories for the fixed checkout
3. Diffs `classes.modified` between buggy and fixed versions using unified diff
4. Includes the diff in the LLM evidence as `fix_diff_oracle` (labeled as post-fix)
5. Cleans up the fixed checkout automatically

### Comparing Pre-fix vs Post-fix Accuracy

For thesis evaluation, you can compare classification accuracy by running each bug **twice**:

**PowerShell (Windows):**

```powershell
# Step 1: Collect pre-fix context (no diff)
python -m d4j_odc_pipeline collect `
  --project Lang --bug 1 `
  --skip-coverage

# Step 2: Collect post-fix context (with diff)
python -m d4j_odc_pipeline collect `
  --project Lang --bug 1 `
  --include-fix-diff --skip-coverage

# Step 3: Classify both (reuse existing context — instant, no checkout needed)
python -m d4j_odc_pipeline classify `
  --context .\.dist\runs\Lang_1_prefix\context.json

python -m d4j_odc_pipeline classify `
  --context .\.dist\runs\Lang_1_postfix\context.json
```

**Bash (Ubuntu/Linux/WSL):**

```bash
# Step 1: Collect pre-fix context (no diff)
python -m d4j_odc_pipeline collect \
  --project Lang --bug 1 \
  --skip-coverage

# Step 2: Collect post-fix context (with diff)
python -m d4j_odc_pipeline collect \
  --project Lang --bug 1 \
  --include-fix-diff --skip-coverage

# Step 3: Classify both (reuse existing context - instant, no checkout needed)
python -m d4j_odc_pipeline classify \
  --context ./.dist/runs/Lang_1_prefix/context.json

python -m d4j_odc_pipeline classify \
  --context ./.dist/runs/Lang_1_postfix/context.json

# Step 4: Compare
python -m d4j_odc_pipeline compare \
  --prefix ./.dist/runs/Lang_1_prefix/classification.json \
  --postfix ./.dist/runs/Lang_1_postfix/classification.json \
  --output ./.dist/runs/Lang_1_prefix/comparison.json \
  --report ./.dist/runs/Lang_1_prefix/comparison.md
```

Both `classification.json` and `report.md` include an **`evidence_mode`** field (`"pre-fix"` or `"post-fix"`) so you can programmatically compare results.

> **Note**: The fix diff is clearly labeled in the prompt as "POST-FIX oracle information" so the LLM knows it wouldn't normally be available. The `classes.modified` field remains hidden from the prompt regardless.

---

## Output Files

### Default Output Directories

| Command scope | Default root   | Example path                                                        |
| ------------- | -------------- | ------------------------------------------------------------------- |
| Standalone    | `.dist/runs/`  | `.dist/runs/Lang_1_prefix/classification.json`                      |
| Batch study   | `.dist/study/` | `.dist/study/artifacts_68/prefix/Lang_1_prefix/classification.json` |

### File Reference

| File                     | Produced by        | Contents                                                                          |
| ------------------------ | ------------------ | --------------------------------------------------------------------------------- |
| `context.json`           | `collect` / `run`  | All pre-fix evidence: code snippets, metadata, failures, coverage, bug report     |
| `classification.json`    | `classify` / `run` | ODC type + family + confidence + reasoning chain + optional ODC attribute mapping |
| `report.md`              | `classify` / `run` | Human-readable bug + classification summary                                       |
| `comparison.json`        | `compare`          | Single-pair strict/top2/family match result                                       |
| `batch_comparison.json`  | `compare-batch`    | Aggregate metrics + confusion matrix + per-bug detail                             |
| `manifest_*.json`        | `study-plan`       | Balanced bug manifest with all selected project/bug entries                       |
| `summary.json`           | `study-run`        | Per-entry execution status for prefix/postfix runs                                |
| `checkpoint.json`        | `study-run`        | Resume checkpoint: tracks completed bugs for interrupted batch runs               |
| `analysis.json`          | `study-analyze`    | Cross-artifact study analytics and top-3 divergence buckets                       |
| `analysis.md`            | `study-analyze`    | Human-readable batch analysis report                                              |
| `prompt.json`            | `--prompt-output`  | Rendered prompt messages sent to the LLM (system + user)                          |
| `instrument_classes.txt` | Coverage step      | Classes instrumented for targeted coverage                                        |
