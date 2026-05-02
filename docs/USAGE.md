# CLI Usage

The D4J ODC Pipeline supports two modes of operation:

1. **Interactive Mode** (recommended) — A REPL shell with `/slash` commands, tab completion, and session persistence
2. **Script Mode** — Traditional CLI commands for scripting, CI, and automation

---

## Interactive Mode (REPL)

### Launching

```bash
# Simply run the module with no arguments
python -m d4j_odc_pipeline
```

This opens the interactive shell:

```bash
╭──────────────────────────────────────────╮
│  🔬 D4J ODC Pipeline — Interactive Mode  │
│                                          │
│  Provider   gemini                       │
│  Model      gemini-3.1-flash-lite-preview│
│  Mode       prefix (realistic)           │
│                                          │
│  Type /help for available commands       │
│  Type /exit or Ctrl+D to quit            │
╰──────────────────────────────────────────╯

odc>
```

### Slash Commands Reference

Type `/help` inside the REPL to see all commands. Here's the full list:

#### 🔧 Pipeline Commands

| Command                                           | Description                                               |
| ------------------------------------------------- | --------------------------------------------------------- |
| `/collect [--project P --bug N] [--postfix]`      | Collect bug evidence (prefix or postfix mode)             |
| `/classify [context_directory_name]`              | Classify an existing context JSON with LLM                |
| `/run [--project P --bug N] [--postfix]`          | End-to-end collect + classify                             |
| `/compare --prefix P --postfix Q`                 | Compare pre-fix and post-fix classifications (NOT USEFUL) |
| `/compare-batch --prefix-dir D1 --postfix-dir D2` | Batch compare (alias: `/cb`) (NOT USEFUL)                 |

#### 📊 Study Commands

| Command                                                  | Description                            |
| -------------------------------------------------------- | -------------------------------------- |
| `/study plan [--target-bugs N]`                          | Generate balanced bug manifest         |
| `/study run [--manifest M]`                              | Execute batch paired runs              |
| `/study analyze [--manifest M] [--require-all-projects]` | Cross-artifact analysis                |
| `/study baseline [--manifest M]`                         | Run baseline (direct) classifications  |
| `/study export [--analysis PATH] [--format FORMAT]`      | Export results as LaTeX tables and CSV |

#### 🐛 Defects4J Proxy

| Command                           | Description                 |
| --------------------------------- | --------------------------- |
| `/d4j pids`                       | List all available projects |
| `/d4j bids [--project P]`         | List bug IDs for a project  |
| `/d4j info [--project P --bug N]` | Show project or bug details |

#### 🔗 Multi-Fault

| Command                             | Description                                    |
| ----------------------------------- | ---------------------------------------------- |
| `/multifault [--project P --bug N]` | Query multi-fault data (alias: `/mf`)          |
| `/enrich [classification_path]`     | Enrich classification with multi-fault context |

#### 🔍 Inspection

| Command                | Description                                 |
| ---------------------- | ------------------------------------------- |
| `/show context`        | Pretty-print the last collected context     |
| `/show classification` | Pretty-print the last classification result |
| `/show report`         | Render the last markdown report in terminal |
| `/show prompt`         | Show the rendered LLM prompt messages       |

#### ⚙️ Session & Config

| Command                    | Description                                                  |
| -------------------------- | ------------------------------------------------------------ |
| `/help`                    | Show all available commands                                  |
| `/status`                  | Show current session state                                   |
| `/config [key] [value]`    | Show or modify config (provider, model, skip-coverage, etc.) |
| `/provider [name]`         | Show or switch LLM provider (session-only)                   |
| `/model [name]`            | Show or switch LLM model                                     |
| `/history [N]`             | Show last N commands                                         |
| `/bugs`                    | List recently worked-on bugs                                 |
| `/clear [screen\|session]` | Clear terminal or reset session                              |
| `/doctor`                  | Check environment health (D4J, API keys, Python)             |
| `/version`                 | Show pipeline version                                        |
| `/exit`                    | Exit (aliases: `/quit`, `/q`)                                |

### Tab Completion

Press **Tab** at any point to get suggestions:

- Type `/` + Tab → see all available commands
- Type `/ru` + Tab → autocompletes to `/run`
- Type `/d4j ` + Tab → shows subcommands (`pids`, `bids`, `info`)
- Type `/provider ` + Tab → shows available providers
- Type `/clear ` + Tab → shows `screen` and `session` options

### Interactive File Pickers

When you run `/classify` or `/study run` without specifying a file path, a **dropdown selection dialog** appears showing all available files:

```
odc> /classify

  ┌── Select context.json ────────────────┐
  │ Use ↑↓ arrow keys, Enter to select:   │
  │                                        │
  │ ● .dist/runs/Lang_1_prefix/context.json│
  │ ○ .dist/runs/Lang_1_postfix/context.json│
  │ ○ .dist/runs/Math_3_prefix/context.json│
  └────────────────────────────────────────┘
```

This works for:

- `/classify` — picks from discovered `context.json` files
- `/enrich` — picks from discovered `classification.json` files
- `/study run` — picks from discovered `manifest*.json` files
- `/study analyze` — picks from discovered `manifest*.json` files

### Session Persistence

Sessions **auto-resume** by default. When you relaunch the REPL, it remembers:

- Active project and bug (set by `/run`, `/collect`, `/d4j info`)
- Provider and model (session-only — resets to `.env` defaults on fresh launch)
- Last context, classification, and report paths
- Recent bugs worked on (up to 20)
- Command history (up to 100 entries, also used for ↑↓ arrow recall)

Session data is stored at `.dist/.odc_session.json`.

To start completely fresh:

```
odc> /clear session
```

### Bare Input Shorthand

You can type a project and bug number directly without a slash command:

```bash
odc> Lang 1
  💡 Tip: Interpreted as: /run --project Lang --bug 1
          Next time, use /run directly for explicit control.
  Collecting Lang-1 (prefix)...
```

This is a shorthand for `/run --project Lang --bug 1`. The REPL shows a tip so you learn the proper slash command for next time.

### Postfix (Oracle) Mode

To switch between pre-fix (realistic) and post-fix (oracle) modes:

```
odc> /config include-fix-diff true     # Switch to postfix mode
odc> /run --project Lang --bug 1       # Now runs in postfix mode

odc> /config include-fix-diff false    # Switch back to prefix mode
```

Or use the `--postfix` flag per-command:

```
odc> /collect --project Lang --bug 1 --postfix
odc> /run --project Lang --bug 1 --postfix
```

### Example Workflow

```
odc> /doctor                              # Check environment health
odc> /d4j pids                            # See available projects
odc> /d4j bids --project Lang             # See bug IDs for Lang
odc> /run --project Lang --bug 1          # Collect + classify
odc> /show classification                 # View result
odc> /show report                         # View markdown report
odc> /run --project Lang --bug 1 --postfix  # Run postfix for comparison
odc> /compare --prefix .dist/runs/Lang_1_prefix/classification.json \
               --postfix .dist/runs/Lang_1_postfix/classification.json
odc> /bugs                                # See recent bugs
odc> /status                              # Check session state
odc> /exit                                # Save and quit
```

### Keyboard Shortcuts

| Key        | Action                   |
| ---------- | ------------------------ |
| **Tab**    | Autocomplete commands    |
| **↑ / ↓**  | Navigate command history |
| **Ctrl+C** | Cancel current input     |
| **Ctrl+D** | Exit the REPL            |

---

## Script Mode (Traditional CLI)

All original CLI commands remain fully functional when arguments are provided. Use this mode for scripting, CI pipelines, and automation.

```bash
python -m d4j_odc_pipeline --help    # Show all script-mode commands
```

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

---

## `study-baseline` — Baseline (Direct Prompt) Comparison

Runs prefix-only classifications using the `direct` prompt style for RQ2.2 controlled comparison. When `--scientific-artifacts-root` is provided, the baseline reuses `context.json` from the scientific run — ensuring both conditions see identical evidence.

**PowerShell (Windows):**

```powershell
# Run baseline using same manifest as the scientific study
python -m d4j_odc_pipeline study-baseline `
  --manifest manifest_68.json `
  --skip-coverage

# Reuse context from the scientific run (recommended for fair comparison)
python -m d4j_odc_pipeline study-baseline `
  --manifest manifest_68.json `
  --scientific-artifacts-root .\.dist\study\artifacts_68
```

**Bash (Ubuntu/Linux/WSL):**

```bash
# Run baseline with context reuse
python -m d4j_odc_pipeline study-baseline \
  --manifest manifest_68.json \
  --scientific-artifacts-root ./.dist/study/artifacts_68
```

---

## `study-export` — LaTeX and CSV Export

Exports analysis results as publication-ready LaTeX tables and CSV files for secondary statistical analysis (R/SPSS).

**PowerShell (Windows):**

```powershell
# Export both LaTeX and CSV (default)
python -m d4j_odc_pipeline study-export `
  --analysis .\.dist\study\analysis_68.json

# Export LaTeX only
python -m d4j_odc_pipeline study-export `
  --analysis .\.dist\study\analysis_68.json `
  --format latex

# Export to a custom directory
python -m d4j_odc_pipeline study-export `
  --analysis .\.dist\study\analysis_68.json `
  --output-dir .\manuscript\tables
```

**Bash (Ubuntu/Linux/WSL):**

```bash
python -m d4j_odc_pipeline study-export \
  --analysis ./.dist/study/analysis_68.json
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
├── baseline_68/                  # Generated by study-baseline
│   ├── Lang_1_prefix/
│   │   ├── classification.json
│   │   └── report.md
│   └── checkpoint.json
├── latex/                        # Generated by study-export
│   ├── type_distribution.tex
│   ├── accuracy.tex
│   ├── confusion_matrix.tex
│   └── per_project_kappa.tex
├── csv/                          # Generated by study-export
│   ├── per_bug_comparison.csv
│   └── type_distribution.csv
└── work/
    ├── prefix/
    └── postfix/
```

---

## End-to-End Study Workflow (All RQs)

This section walks through every step needed to run a complete study from scratch and produce all analysis + manuscript-ready outputs. The example uses **100 bugs**, but you can substitute any number.

> **Time estimate**: Steps 1–3 are the bulk of the work. Each bug takes ~2–5 minutes (checkout + compile + test + LLM call). For 100 bugs × 2 modes (prefix + postfix) + 100 baseline runs = ~300 runs total. Budget **8–20 hours** depending on network, LLM, and hardware.

### Prerequisites

- Defects4J installed and working (verify with `/doctor` or `python -m d4j_odc_pipeline d4j pids`)
- LLM provider configured in `.env` (Gemini API key, or OpenRouter, etc.)
- Python environment activated with `pip install -e .`

---

### Step 1: Generate a Study Manifest

Create a balanced bug selection across all Defects4J projects.

```powershell
# PowerShell
python -m d4j_odc_pipeline study-plan `
  --target-bugs 100 `
  --seed 42
```

```bash
# Bash
python -m d4j_odc_pipeline study-plan \
  --target-bugs 100 \
  --seed 42
```

**Output**: `.dist/study/manifest_100.json` — a JSON file listing the selected bugs with balanced per-project sampling.

**RQs served**: All — this manifest drives every subsequent step.

---

### Step 2: Run Scientific (Full Protocol) Classifications

Execute paired prefix + postfix runs for every bug using the `scientific` prompt style. This is the main experimental group.

```powershell
# PowerShell
python -m d4j_odc_pipeline study-run `
  --manifest manifest_100.json `
  --skip-coverage
```

```bash
# Bash
python -m d4j_odc_pipeline study-run \
  --manifest manifest_100.json \
  --skip-coverage
```

**Features**:

- **Resumable**: If interrupted (Ctrl+C, crash, network error), re-run the exact same command to pick up where you left off. Progress is saved in `checkpoint.json`.
- **Graceful shutdown**: Press Ctrl+C once to finish the current bug cleanly, twice to force-quit.
- **Skip existing**: Bugs with all 3 output files (context, classification, report) are automatically skipped.

**Output**: `.dist/study/artifacts_100/prefix/` and `.dist/study/artifacts_100/postfix/` — each bug gets a subdirectory with `context.json`, `classification.json`, and `report.md`.

**RQs served**:

| RQ    | What this step provides                                                |
| ----- | ---------------------------------------------------------------------- |
| RQ1.1 | Prefix classifications → type distribution                            |
| RQ1.2 | Prefix classifications with `inferred_impact` → Impact vs Type        |
| RQ2.1 | Prefix vs Postfix pairs → strict/top2/family accuracy + per-type P/RF1 |
| RQ3.1 | Prefix vs Postfix pairs → semantic gap metrics                        |
| RQ4.1 | All pairs → per-project Cohen's Kappa                                 |

---

### Step 3: Run Baseline (Direct/Zero-Shot) Classifications

Run the same bugs through the `direct` prompt style (no scientific protocol, no few-shots, no diagnostic tree). This is the controlled baseline for RQ2.2.

```powershell
# PowerShell — reuse context from scientific run for fair comparison
python -m d4j_odc_pipeline study-baseline `
  --manifest manifest_100.json `
  --scientific-artifacts-root .\.dist\study\artifacts_100
```

```bash
# Bash
python -m d4j_odc_pipeline study-baseline \
  --manifest manifest_100.json \
  --scientific-artifacts-root ./.dist/study/artifacts_100
```

> **Important**: The `--scientific-artifacts-root` flag reuses `context.json` from the scientific run. This ensures both prompt styles see **identical evidence** — the only difference is the system prompt. Without this flag, evidence would be re-collected (same result, but slower and risks minor variance from network-fetched bug reports).

**Output**: `.dist/study/baseline_100/` — each bug gets `classification.json` and `report.md` (context is reused, not duplicated).

**RQs served**:

| RQ    | What this step provides                                                    |
| ----- | -------------------------------------------------------------------------- |
| RQ2.2 | Baseline classifications → compared against scientific + postfix for delta |

---

### Step 3b: Run Naive (Taxonomy-Free) Classifications

Run the same bugs through the `naive` prompt style (no ODC taxonomy at all — the LLM classifies in its own words). This is the controlled baseline for RQ2.3.

```powershell
# PowerShell — reuse context from scientific run for fair comparison
python -m d4j_odc_pipeline study-naive `
  --manifest manifest_100.json `
  --scientific-artifacts-root .\.dist\study\artifacts_100
```

```bash
# Bash
python -m d4j_odc_pipeline study-naive \
  --manifest manifest_100.json \
  --scientific-artifacts-root ./.dist/study/artifacts_100
```

> **Important**: Like `study-baseline`, the `--scientific-artifacts-root` flag reuses `context.json` from the scientific run to guarantee identical evidence across all three prompt tiers.

**Output**: `.dist/study/naive_100/` — each bug gets `classification.json` with free-form `defect_type` labels instead of ODC types.

**RQs served**:

| RQ    | What this step provides                                                        |
| ----- | ------------------------------------------------------------------------------ |
| RQ2.3 | Taxonomy-free labels → vocabulary size, entropy, ODC coverage after mapping    |

---

### Step 4: Cross-Artifact Analysis

Aggregate all prefix/postfix pairs into a single analysis JSON with metrics for every RQ.

```powershell
# PowerShell
python -m d4j_odc_pipeline study-analyze `
  --manifest manifest_100.json `
  --require-all-projects
```

```bash
# Bash
python -m d4j_odc_pipeline study-analyze \
  --manifest manifest_100.json \
  --require-all-projects
```

**Output**:

- `.dist/study/analysis_100.json` — machine-readable analysis (type distribution, confusion matrix, kappa, per-project metrics, divergence patterns)
- `.dist/study/analysis_100.md` — human-readable report with tables and summaries

**RQs served**: Produces the raw data for RQ1.1, RQ2.1, RQ3.1, RQ4.1. RQ1.2 and RQ2.2 are computed in the next step via `analysis.py`.

---

### Step 5: Export Manuscript Tables

Generate publication-ready LaTeX tables and CSV files from the analysis.

```powershell
# PowerShell
python -m d4j_odc_pipeline study-export `
  --analysis .\.dist\study\analysis_100.json
```

```bash
# Bash
python -m d4j_odc_pipeline study-export \
  --analysis ./.dist/study/analysis_100.json
```

**Output**:

| File                                       | Content                                      | Manuscript target |
| ------------------------------------------ | -------------------------------------------- | ----------------- |
| `.dist/study/latex/type_distribution.tex`  | ODC type frequency + family breakdown         | Table 1 (RQ1.1)   |
| `.dist/study/latex/accuracy.tex`           | Strict/Top-2/Family match rates + Kappa       | Table 2 (RQ2.1)   |
| `.dist/study/latex/confusion_matrix.tex`   | 7×7 prefix→postfix type transition matrix     | Table 3 (RQ2.1)   |
| `.dist/study/latex/per_project_kappa.tex`  | Per-project Cohen's Kappa + interpretation    | Table 4 (RQ4.1)   |
| `.dist/study/latex/baseline_comparison.tex`| Scientific vs Direct improvement deltas       | Table 5 (RQ2.2)   |
| `.dist/study/csv/*.csv`                    | All metrics in CSV for R/SPSS secondary analysis | Supplementary  |

---

### Step 6: Verify and Review

```powershell
# Quick sanity check — how many pairs were analyzed?
python -c "import json; d=json.load(open('.dist/study/analysis_100.json')); print(f'Pairs: {d[\"total_pairs\"]}, Kappa: {d.get(\"cohens_kappa\",\"N/A\")}')"

# Open the human-readable report
cat .dist/study/analysis_100.md
```

Review the generated `.tex` files in your LaTeX editor. The tables use `booktabs` conventions and can be directly `\input{}`-ed into a manuscript.

---

### Quick Reference: Complete Command Sequence

For copy-paste convenience, here is the full sequence in **PowerShell**:

```powershell
# 1. Plan (select 100 bugs)
python -m d4j_odc_pipeline study-plan --target-bugs 100 --seed 42

# 2. Scientific runs (prefix + postfix)
python -m d4j_odc_pipeline study-run --manifest manifest_100.json --skip-coverage

# 3. Baseline runs (direct prompt, reuse context)
python -m d4j_odc_pipeline study-baseline `
  --manifest manifest_100.json `
  --scientific-artifacts-root .\.dist\study\artifacts_100

# 4. Analyze
python -m d4j_odc_pipeline study-analyze `
  --manifest manifest_100.json `
  --require-all-projects

# 5. Export tables
python -m d4j_odc_pipeline study-export `
  --analysis .\.dist\study\analysis_100.json
```

And in **Bash**:

```bash
# 1. Plan
python -m d4j_odc_pipeline study-plan --target-bugs 100 --seed 42

# 2. Scientific runs
python -m d4j_odc_pipeline study-run \
  --manifest manifest_100.json --skip-coverage

# 3. Baseline runs
python -m d4j_odc_pipeline study-baseline \
  --manifest manifest_100.json \
  --scientific-artifacts-root ./.dist/study/artifacts_100

# 3b. Naive (taxonomy-free) runs
python -m d4j_odc_pipeline study-naive \
  --manifest manifest_100.json \
  --scientific-artifacts-root ./.dist/study/artifacts_100

# 4. Analyze
python -m d4j_odc_pipeline study-analyze \
  --manifest manifest_100.json --require-all-projects

# 5. Export
python -m d4j_odc_pipeline study-export \
  --analysis ./.dist/study/analysis_100.json
```

### Interactive Mode Equivalent

The same workflow in the REPL:

```text
odc> /study plan --target-bugs 100 --seed 42
odc> /study run --manifest manifest_100.json
odc> /study baseline --manifest manifest_100.json --scientific-artifacts-root .dist/study/artifacts_100
odc> /study naive --manifest manifest_100.json --scientific-artifacts-root .dist/study/artifacts_100
odc> /study analyze --manifest manifest_100.json --require-all-projects
odc> /study export --analysis .dist/study/analysis_100.json
```

---

### RQ Coverage Matrix

| Step | Command           | RQ1.1 | RQ1.2 | RQ2.1 | RQ2.2 | RQ2.3 | RQ3.1 | RQ4.1 |
| ---- | ----------------- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1    | `study-plan`      |       |       |       |       |       |       |       |
| 2    | `study-run`       | ✅    | ✅    | ✅    |       |       | ✅    | ✅    |
| 3    | `study-baseline`  |       |       |       | ✅    |       |       |       |
| 3b   | `study-naive`     |       |       |       |       | ✅    |       |       |
| 4    | `study-analyze`   | ✅    |       | ✅    |       |       | ✅    | ✅    |
| 5    | `study-export`    | ✅    | ✅    | ✅    | ✅    | ✅    | ✅    | ✅    |

> **Note**: RQ1.2 (Impact vs Type), RQ2.2 (Baseline comparison), and RQ2.3 (Taxonomy grounding) analysis is computed during export from the raw classification data. All other RQs are computed during `study-analyze`.

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

### Baseline parameters (used by `study-baseline`)

| Parameter                     | Required | Description                                                                           |
| ----------------------------- | :------: | ------------------------------------------------------------------------------------- |
| `--manifest`                  |   Yes    | Study manifest JSON path.                                                             |
| `--baseline-root`             |    No    | Root output directory for baseline artifacts. Defaults to `.dist/study/baseline_<N>`. |
| `--work-root`                 |    No    | Root checkout directory. Defaults to `.dist/study/work`.                              |
| `--scientific-artifacts-root` |    No    | Root of scientific artifacts to reuse context.json from (ensures identical evidence). |
| `--summary-output`            |    No    | Baseline summary JSON path. Defaults to `.dist/study/baseline_summary.json`.          |
| `--prompt-style`              |    No    | Prompt style override: `direct` (default) or `scientific`.                            |
| `--no-skip-existing`          |    No    | Re-run entries even when artifacts exist.                                             |
| `--prompt-output`             |    No    | Save prompt payloads.                                                                 |

### Export parameters (used by `study-export`)

| Parameter      | Required | Description                                                             |
| -------------- | :------: | ----------------------------------------------------------------------- |
| `--analysis`   |   Yes    | Path to analysis JSON.                                                  |
| `--format`     |    No    | `latex`, `csv`, or `both` (default: `both`).                            |
| `--output-dir` |    No    | Output directory for export files. Defaults to same directory as input. |

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
| `baseline_summary.json`  | `study-baseline`   | Per-entry execution status for baseline runs                                      |
| `*.tex`                  | `study-export`     | LaTeX tables (type distribution, accuracy, confusion matrix, per-project kappa)   |
| `*.csv`                  | `study-export`     | CSV files for R/SPSS statistical analysis                                         |
| `prompt.json`            | `--prompt-output`  | Rendered prompt messages sent to the LLM (system + user)                          |
| `instrument_classes.txt` | Coverage step      | Classes instrumented for targeted coverage                                        |
