# Defects4J ODC Pipeline - Detailed Run Guide

This guide is a command-first companion to [README.md](README.md), using the same workflow and feature set, but with strict step-by-step commands to run and test everything.

It covers:

1. Environment setup checks
2. CLI sanity checks
3. Running and testing each command (`d4j`, `collect`, `classify`, `run`, `compare`, `compare-batch`)
4. A complete pre-fix vs post-fix evaluation flow
5. Troubleshooting commands

## 0. What To Do Now (Quick Start)

Run this exact sequence first.

1. Switch to the no-space path and activate virtual environment:

```powershell
cd C:\d4j_odc_implementation
.\.venv\Scripts\Activate.ps1
```

2. Verify Defects4J bridge works:

```powershell
python -m d4j_odc_pipeline d4j pids
python -m d4j_odc_pipeline d4j info --project Lang --bug 1
```

3. Run one end-to-end pipeline job:

```powershell
python -m d4j_odc_pipeline run `
  --project Lang --bug 1 `
  --work-dir .\work\Lang_1b `
  --context-output .\artifacts\Lang_1\context.json `
  --classification-output .\artifacts\Lang_1\classification.json `
  --report .\artifacts\Lang_1\report.md `
  --skip-coverage
```

4. Confirm output files were created:

```powershell
Get-ChildItem .\artifacts\Lang_1
```

5. Run another bug (example bug 3):

```powershell
python -m d4j_odc_pipeline run `
  --project Lang --bug 3 `
  --work-dir .\work\Lang_3b `
  --context-output .\artifacts\Lang_3\context.json `
  --classification-output .\artifacts\Lang_3\classification.json `
  --report .\artifacts\Lang_3\report.md `
  --skip-coverage
```

If any command fails, run this diagnostic block and inspect the output:

```powershell
python -m d4j_odc_pipeline d4j pids
python -m d4j_odc_pipeline d4j info --project Lang --bug 1
wsl -d Ubuntu -- bash -lc "perl /root/defects4j/framework/bin/defects4j info -p Lang | head -n 20"
```

## 0.1 Large-Scale Study (50-70 Bugs Across All Projects)

Use this workflow when you want guaranteed project coverage, pre-fix/post-fix runs, and final cross-artifact analysis.

### Step 1 - Generate a balanced manifest

This guarantees at least one bug per discovered Defects4J project (typically 17 projects), then fills the rest up to your target.

```powershell
python -m d4j_odc_pipeline study-plan `
  --output .\.dist\study\manifest_68.json `
  --target-bugs 68 `
  --min-per-project 1
```

### Step 2 - Execute prefix and postfix runs from the manifest

This creates paired artifacts under:

- `.dist\study\artifacts\prefix\<Project>_<Bug>_prefix\`
- `.dist\study\artifacts\postfix\<Project>_<Bug>_postfix\`

Each directory includes `context.json`, `classification.json`, and `report.md`.

```powershell
python -m d4j_odc_pipeline study-run `
  --manifest .\.dist\study\manifest_68.json `
  --artifacts-root .\.dist\study\artifacts `
  --work-root .\.dist\study\work `
  --summary-output .\.dist\study\run_summary.json `
  --require-all-projects `
  --skip-coverage
```

#### Stopping a Running Study

If you need to stop an active `study-run` process (e.g., it's taking too long or you need to interrupt), use this PowerShell command to kill the process tree immediately:

```powershell
Get-CimInstance Win32_Process |
  Where-Object { $_.CommandLine -match 'd4j_odc_pipeline study-run' } |
  ForEach-Object { taskkill /PID $_.ProcessId /T /F }
```

Alternatively, in VS Code, you can click the **trash icon** on the terminal tab to kill the session and all child processes.

### Step 3 - Run cross-artifact analysis

This consumes prefix/postfix outputs and produces study-level analytics, including:

1. total bugs analyzed
2. bugs with changed type in postfix vs prefix
3. all alternative-match divergences (where type changed but alternatives overlap)
4. per-project drift and type-transition summaries

```powershell
python -m d4j_odc_pipeline study-analyze `
  --prefix-dir .\.dist\study\artifacts\prefix `
  --postfix-dir .\.dist\study\artifacts\postfix `
  --manifest .\.dist\study\manifest_68.json `
  --require-all-projects `
  --output .\.dist\study\analysis.json `
  --report .\.dist\study\analysis.md
```

#### Understanding the Analysis Metrics

The `analysis.md` header shows these key metrics:

- **Total pairs**: Number of bug pairs analyzed
- **Projects covered**: Number of unique projects represented
- **Type changed**: Bugs where pre-fix and post-fix classifications differ
- **Type unchanged**: Bugs with identical pre-fix and post-fix classifications
- **No alternative overlap**: Type-changed bugs where the pre-fix and post-fix types have no overlapping alternative types. These represent the hardest classification disagreements
- **No family match**: Type-changed bugs where the pre-fix and post-fix types belong to different defect families (Control and Data Flow vs Structural)
- **Family match**: Type-changed bugs where both classifications share the same defect family, even if the specific type differs

The **Type Transitions** section lists all type changes and marks them with:
- `(no alt overlap)` — pre-fix and post-fix types have no shared alternatives
- `(no family match)` — types are from completely different defect families
- Both markers if both conditions apply

### Step 4 - Optional compatibility comparison output

You can still generate the existing comparison metrics output for backward compatibility:

```powershell
python -m d4j_odc_pipeline compare-batch `
  --prefix-dir .\.dist\study\artifacts\prefix `
  --postfix-dir .\.dist\study\artifacts\postfix `
  --output .\.dist\study\batch_comparison.json `
  --report .\.dist\study\batch_comparison.md
```

## 1. Before You Start

Use a Windows path without spaces when running commands (recommended):

```powershell
C:\d4j_odc_implementation
```

Why: Defects4J checkout can fail when WSL receives space-containing paths.

If you get errors like ModuleNotFoundError: No module named rich, your terminal is using system Python instead of the project virtual environment. In that case, either activate .venv first, or run commands with .\\.venv\\Scripts\\python explicitly.

## 2. One-Time Setup Verification

From PowerShell:

```powershell
cd C:\d4j_odc_implementation
.\.venv\Scripts\Activate.ps1
python --version
```

Check WSL and Defects4J availability:

```powershell
wsl -l -v
wsl -d Ubuntu -- bash -lc "perl /root/defects4j/framework/bin/defects4j info -p Lang | head -n 20"
```

Verify environment variables in [.env](.env):

```dotenv
DEFAULT_LLM_PROVIDER=gemini
DEFAULT_LLM_MODEL=gemini-3.1-flash-lite-preview
GEMINI_API_KEY=your_real_key
DEFECTS4J_CMD=wsl perl /root/defects4j/framework/bin/defects4j
DEFECTS4J_PATH_STYLE=wsl
```

## 3. Quick Health Checks

Run these before any experiment:

```powershell
python -m pytest -q
python -m d4j_odc_pipeline d4j pids
python -m d4j_odc_pipeline d4j info --project Lang --bug 1
```

Expected:

1. Tests pass.
2. `d4j pids` prints project IDs.
3. `d4j info` prints Lang-1 metadata.

## 4. Feature-by-Feature Commands

### 4.1 `d4j` - Defects4J helper/proxy commands

Purpose:

1. Inspect projects and bugs without leaving pipeline CLI.

Commands:

```powershell
python -m d4j_odc_pipeline d4j pids
python -m d4j_odc_pipeline d4j bids --project Lang
python -m d4j_odc_pipeline d4j bids --project Lang --all
python -m d4j_odc_pipeline d4j info --project Lang --bug 1
```

### 4.2 `collect` - Build pre-fix evidence context

Purpose:

1. Checkout buggy revision
2. Compile
3. Run tests
4. Parse failures and stack traces
5. Extract code evidence
6. Write `context.json`

Minimal fast run:

```powershell
python -m d4j_odc_pipeline collect `
  --project Lang --bug 1 `
  --work-dir .\.dist\work\Lang_1b `
  --output .\.dist\artifacts\Lang_1\context.json `
  --skip-coverage
```

Coverage-enabled run:

```powershell
python -m d4j_odc_pipeline collect `
  --project Lang --bug 1 `
  --work-dir .\.dist\work\Lang_1b_cov `
  --output .\.dist\artifacts\Lang_1_cov\context.json
```

Include fix diff oracle:

```powershell
python -m d4j_odc_pipeline collect `
  --project Lang --bug 1 `
  --work-dir .\.dist\work\Lang_1b_fix `
  --output .\.dist\artifacts\Lang_1f\context.json `
  --skip-coverage --include-fix-diff
```

### 4.3 `classify` - Classify existing context with LLM

Purpose:

1. Build prompt from context
2. Call selected LLM provider
3. Validate JSON output
4. Write `classification.json`
5. Optionally write markdown report and prompt dump

Dry-run (no API call):

```powershell
python -m d4j_odc_pipeline classify `
  --context .\.dist\artifacts\Lang_1\context.json `
  --output .\.dist\artifacts\Lang_1\classification.json `
  --report .\.dist\artifacts\Lang_1\report.md `
  --prompt-output .\.dist\artifacts\Lang_1\prompt.json `
  --dry-run
```

Real run (Gemini):

```powershell
python -m d4j_odc_pipeline classify `
  --context .\.dist\artifacts\Lang_1\context.json `
  --output .\.dist\artifacts\Lang_1\classification.json `
  --report .\.dist\artifacts\Lang_1\report.md `
  --prompt-output .\.dist\artifacts\Lang_1\prompt.json
```

OpenRouter example:

```powershell
python -m d4j_odc_pipeline classify `
  --context .\.dist\artifacts\Lang_1\context.json `
  --output .\.dist\artifacts\Lang_1_openrouter\classification.json `
  --report .\.dist\artifacts\Lang_1_openrouter\report.md `
  --provider openrouter `
  --model openai/gpt-5.2
```

### 4.4 `run` - End-to-end collect + classify

Purpose:

1. Execute `collect`
2. Execute `classify`
3. Generate report in one command

```powershell
python -m d4j_odc_pipeline run `
  --project Lang --bug 1 `
  --work-dir .\.dist\work\Lang_1b_run `
  --context-output .\.dist\artifacts\Lang_1_run\context.json `
  --classification-output .\.dist\artifacts\Lang_1_run\classification.json `
  --report .\.dist\artifacts\Lang_1_run\report.md `
  --skip-coverage
```

### 4.5 `compare` - Compare one pre-fix/post-fix pair

Purpose:

1. Compare label agreement and accuracy-related fields
2. Write comparison JSON
3. Optionally write comparison report

```powershell
python -m d4j_odc_pipeline compare `
  --prefix .\.dist\artifacts\Lang_1\classification.json `
  --postfix .\.dist\artifacts\Lang_1f\classification.json `
  --output .\.dist\artifacts\Lang_1\comparison.json `
  --report .\.dist\artifacts\Lang_1\comparison_report.md
```

### 4.6 `compare-batch` - Compare many bug pairs

Purpose:

1. Evaluate many prefix/postfix results in one run
2. Generate aggregate metrics report

```powershell
python -m d4j_odc_pipeline compare-batch `
  --prefix-dir .\.dist\artifacts\prefix_runs `
  --postfix-dir .\.dist\artifacts\postfix_runs `
  --output .\.dist\artifacts\batch_comparison.json `
  --report .\.dist\artifacts\accuracy_report.md
```

## 5. Full End-to-End Test Plan (Single Bug)

Run in this exact order:

1. Environment + sanity checks
2. `collect` pre-fix context
3. `collect` post-fix context (`--include-fix-diff`)
4. `classify` pre-fix
5. `classify` post-fix
6. `compare`

Commands:

```powershell
cd C:\d4j_odc_implementation
.\.venv\Scripts\Activate.ps1

python -m d4j_odc_pipeline d4j pids
python -m d4j_odc_pipeline d4j info --project Lang --bug 1

python -m d4j_odc_pipeline collect `
  --project Lang --bug 1 `
  --work-dir .\.dist\work\Lang_1b `
  --output .\.dist\artifacts\Lang_1\context.json `
  --skip-coverage

python -m d4j_odc_pipeline collect `
  --project Lang --bug 1 `
  --work-dir .\.dist\work\Lang_1b_fix `
  --output .\.dist\artifacts\Lang_1f\context.json `
  --skip-coverage --include-fix-diff

python -m d4j_odc_pipeline classify `
  --context .\.dist\artifacts\Lang_1\context.json `
  --output .\.dist\artifacts\Lang_1\classification.json `
  --report .\.dist\artifacts\Lang_1\report.md

python -m d4j_odc_pipeline classify `
  --context .\.dist\artifacts\Lang_1f\context.json `
  --output .\.dist\artifacts\Lang_1f\classification.json `
  --report .\.dist\artifacts\Lang_1f\report.md

python -m d4j_odc_pipeline compare `
  --prefix .\.dist\artifacts\Lang_1\classification.json `
  --postfix .\.dist\artifacts\Lang_1f\classification.json `
  --output .\.dist\artifacts\Lang_1\comparison.json `
  --report .\.dist\artifacts\Lang_1\comparison_report.md
```

## 6. Where Outputs Go

Common output files:

1. `.dist/artifacts/<bug>/context.json`
2. `.dist/artifacts/<bug>/classification.json`
3. `.dist/artifacts/<bug>/report.md`
4. `.dist/artifacts/<bug>/prompt.json` (if `--prompt-output` is used)
5. `.dist/artifacts/<bug>/comparison.json` (for `compare`)

## 7. Troubleshooting Commands

If a command fails, run these diagnostics:

```powershell
cd C:\d4j_odc_implementation
.\.venv\Scripts\Activate.ps1
python -m d4j_odc_pipeline d4j pids
python -m d4j_odc_pipeline d4j info --project Lang --bug 1
wsl -d Ubuntu -- bash -lc "git config --global --get core.autocrlf"
wsl -d Ubuntu -- bash -lc "perl /root/defects4j/framework/bin/defects4j info -p Lang | head -n 20"
```

If the Defects4J path differs from `/root/defects4j`, update [\.env](.env) accordingly:

```dotenv
DEFECTS4J_CMD=wsl perl <actual_d4j_home>/framework/bin/defects4j
```

## 8. Notes on Original README Alignment

This guide follows the same feature set and semantics as [README.md](README.md):

1. Same setup models (Windows+WSL, native Linux)
2. Same command groups (`d4j`, `collect`, `classify`, `run`, `compare`, `compare-batch`)
3. Same optional modes (`--skip-coverage`, `--include-fix-diff`, `--dry-run`)
4. Same expected outputs (`context.json`, `classification.json`, `report.md`)
