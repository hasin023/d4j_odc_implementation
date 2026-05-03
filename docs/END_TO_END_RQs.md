# End-to-End Study Workflow (All RQs)

This section walks through every step needed to run a complete study from scratch and produce all analysis + manuscript-ready outputs. The example uses **100 bugs**, but you can substitute any number.

> **Time estimate**: Steps 1–3 are the bulk of the work. Each bug takes ~2–5 minutes (checkout + compile + test + LLM call). For 100 bugs × 2 modes (prefix + postfix) + 100 baseline runs = ~300 runs total. Budget **8–20 hours** depending on network, LLM, and hardware.

## Prerequisites

- Defects4J installed and working (verify with `/doctor` or `python -m d4j_odc_pipeline d4j pids`)
- LLM provider configured in `.env` (Gemini API key, or OpenRouter, etc.)
- Python environment activated with `pip install -e .`

## Step 1: Generate a Study Manifest

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

## Step 2: Run Scientific (Full Protocol) Classifications

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
| RQ1.1 | Prefix classifications → type distribution                             |
| RQ1.2 | Prefix classifications with `inferred_impact` → Impact vs Type         |
| RQ2.1 | Prefix vs Postfix pairs → strict/top2/family accuracy + per-type P/RF1 |
| RQ3.1 | Prefix vs Postfix pairs → semantic gap metrics                         |
| RQ4.1 | All pairs → per-project Cohen's Kappa                                  |

---

## Step 3: Run Baseline (Direct/Zero-Shot) Classifications

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

| RQ    | What this step provides                                                     |
| ----- | --------------------------------------------------------------------------- |
| RQ2.3 | Taxonomy-free labels → vocabulary size, entropy, ODC coverage after mapping |

---

## Step 4: Cross-Artifact Analysis

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

## Step 5: Export Manuscript Tables

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

| File                                        | Content                                          | Manuscript target |
| ------------------------------------------- | ------------------------------------------------ | ----------------- |
| `.dist/study/latex/type_distribution.tex`   | ODC type frequency + family breakdown            | Table 1 (RQ1.1)   |
| `.dist/study/latex/accuracy.tex`            | Strict/Top-2/Family match rates + Kappa          | Table 2 (RQ2.1)   |
| `.dist/study/latex/confusion_matrix.tex`    | 7×7 prefix→postfix type transition matrix        | Table 3 (RQ2.1)   |
| `.dist/study/latex/per_project_kappa.tex`   | Per-project Cohen's Kappa + interpretation       | Table 4 (RQ4.1)   |
| `.dist/study/latex/baseline_comparison.tex` | Scientific vs Direct improvement deltas          | Table 5 (RQ2.2)   |
| `.dist/study/csv/*.csv`                     | All metrics in CSV for R/SPSS secondary analysis | Supplementary     |

---

## Step 6: Verify and Review

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

| Step | Command          | RQ1.1 | RQ1.2 | RQ2.1 | RQ2.2 | RQ2.3 | RQ3.1 | RQ4.1 |
| ---- | ---------------- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1    | `study-plan`     |       |       |       |       |       |       |       |
| 2    | `study-run`      |  ✅   |  ✅   |  ✅   |       |       |  ✅   |  ✅   |
| 3    | `study-baseline` |       |       |       |  ✅   |       |       |       |
| 3b   | `study-naive`    |       |       |       |       |  ✅   |       |       |
| 4    | `study-analyze`  |  ✅   |       |  ✅   |       |       |  ✅   |  ✅   |
| 5    | `study-export`   |  ✅   |  ✅   |  ✅   |  ✅   |  ✅   |  ✅   |  ✅   |

> **Note**: RQ1.2 (Impact vs Type), RQ2.2 (Baseline comparison), and RQ2.3 (Taxonomy grounding) analysis is computed during export from the raw classification data. All other RQs are computed during `study-analyze`.
