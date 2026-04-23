# Defects4J ODC Pipeline

A research pipeline that collects pre-fix bug evidence from [Defects4J](https://github.com/rjust/defects4j), classifies it into ODC (**Orthogonal Defect Classification**) defect types using an LLM (Gemini by default, OpenRouter as fallback), and saves machine-readable outputs for evaluation.

The pipeline follows a **Scientific Debugging** methodology — observation → hypothesis → prediction → experiment → conclusion — to classify each bug into one of 7 ODC defect types with grounded, code-level reasoning.

For large-scale evaluation, the CLI also supports batch-study commands: `study-plan`, `study-run`, and `study-analyze`.

For multi-fault analysis, the pipeline integrates with [defects4j-mf](https://github.com/DCallaz/defects4j-mf) data via the `multifault` and `multifault-enrich` commands.

---

## Pipeline Architecture

### Evidence Collection Flow (`collect`)

```mermaid
flowchart TD
    A[Start: project ID + bug ID] --> B[d4j query: bug metadata]
    B --> |"bug.id, report.id, report.url,\nrevision.buggy, revision.fixed,\nclasses.modified, classes.relevant,\ntests.trigger, tests.relevant"| C[d4j info: bug root cause text]
    C --> D{report.url exists?}
    D -->|Yes| E[Fetch Bug Report Page\nGitHub API / JIRA API / generic HTML]
    D -->|No| F[Skip fetch]
    E --> |"title, type, priority, description,\ncomments → bug_report_content"| G[d4j checkout buggy version]
    F --> G
    G --> |"d4j checkout -p X -v Yb\n→ buggy source on disk"| H[d4j compile]
    H --> |"d4j compile -w <work_dir>"| I[d4j test]
    I --> |"d4j test -w <work_dir>"| J[Parse Failing Tests]
    J --> |"failing_tests file + stderr\n→ test_name, headline, stack_trace, frames"| K[d4j export properties]
    K --> |"dir.src.classes, dir.bin.classes,\ndir.src.tests, dir.bin.tests,\ncp.compile, cp.test,\ntests.trigger, tests.relevant"| L[Select Suspicious Frames]
    L --> |"Filter framework classes\n→ prioritize project source\n→ max 12 source frames"| M[Discover Source Dirs]
    M --> N[Extract Production Code Snippets]
    N --> |"Source around each suspicious frame\n±12 lines, with focus-line marker"| O[Extract Test Source Code]
    O --> |"Failing test method source\n±18 lines, shows expected behavior"| P{Coverage enabled?}
    P -->|Yes| Q[d4j coverage on suspicious classes]
    P -->|No| R[Build BugContext]
    Q --> |"Cobertura XML → line_rate,\nbranch_rate, covered_lines"| R
    R --> S{--include-fix-diff?}
    S -->|Yes| T[Checkout fixed version\nDiff modified classes → fix_diff]
    S -->|No| U[Write context.json]
    T --> U
    U --> V["✅ context.json saved"]
```

### Classification Flow (`classify`)

```mermaid
flowchart TD
    A[Load context.json] --> B[Build System Prompt]
    B --> |"ODC taxonomy with indicators\n+ 7-question diagnostic tree\n+ 5 few-shot examples\n+ scientific debugging protocol\n+ JSON contract schema"| C[Build User Prompt]
    C --> |"Evidence payload:\n• project/bug/version identity\n• d4j metadata fields\n• bug_info text from d4j info\n• bug_report_description\n• failing_tests + stack traces\n• suspicious_frames\n• production_code_snippets\n• test_code_snippets\n• coverage_summary\n• odc_opener_hints / odc_closer_hints\n• fix_diff_oracle (if post-fix)"| D[Call LLM API]
    D --> E[Parse & Extract JSON]
    E --> F{Valid odc_type?}
    F -->|No| G[Retry up to 2 times]
    G --> D
    F -->|Yes| H[Enforce Canonical Family]
    H --> |"odc.family_for(odc_type)\nnever trust LLM family mapping"| I[Write classification.json]
    I --> J[Generate Markdown Report]
    J --> K["✅ classification.json\n+ report.md saved"]
```

### Accuracy Evaluation Flow (`compare` / `compare-batch`)

```mermaid
flowchart TD
    A["Pre-fix classification.json"] --> C[compare_classifications]
    B["Post-fix classification.json"] --> C
    C --> D[Tier 1: Strict Match\nodc_type exact agreement]
    D --> E[Tier 2: Top-2 Match\nprimary or alternative_types overlap]
    E --> F[Tier 3: Family Match\nsame Control and Data Flow / Structural]
    F --> G[Cohen's Kappa\ninter-rater agreement]
    G --> H1[Layer A: Semantic Distance\n0.0-1.0 type proximity]
    H1 --> H2[Layer B: Evidence Asymmetry\nwhy pre-fix ≠ post-fix]
    H2 --> H3[Layer C: Attribute Concordance\ntarget/qualifier/age/source]
    H3 --> H4[Layer D: Divergence Pattern\nexact/soft/moderate/hard]
    H4 --> H5[Layer E: Insights\nhuman-readable analysis]
    H5 --> H["comparison.json + comparison.md"]

    I["Multiple pre-fix/ dirs"] --> J[compare-batch\nAuto-discover pairs]
    K["Multiple postfix/ dirs"] --> J
    J --> L[Aggregate metrics\n+ confusion matrix\n+ divergence patterns\n+ per-bug detail]
    L --> M["batch_comparison.json\n+ batch_report.md"]
```

---

## Defects4J Artifacts & Metadata Used as LLM Input

This section describes every data item that originates from the Defects4J dataset (its CLI tools, property files, and checked-out source) and how it flows into the LLM context.

### From `defects4j query` (via `query_bug_metadata`)

The pipeline queries the following fields for every bug using `defects4j query -p <project> -q <fields>`:

| Field              | D4J CLI field name | Role in LLM input                                                                   |
| ------------------ | ------------------ | ----------------------------------------------------------------------------------- |
| Bug ID             | `bug.id`           | Identity metadata sent in `project_id` / `bug_id` / `version_id`                    |
| Report tracking ID | `report.id`        | Included in `metadata` payload (e.g. `LANG-747`)                                    |
| Bug report URL     | `report.url`       | Used to fetch `bug_report_content` from JIRA/GitHub; URL itself kept in `metadata`  |
| Buggy commit hash  | `revision.buggy`   | Stored in `metadata`; identifies which version was checked out                      |
| Fixed commit hash  | `revision.fixed`   | Stored in `metadata`; used only when `--include-fix-diff` is set                    |
| Modified classes   | `classes.modified` | **Hidden oracle** — stored in `hidden_oracles`, excluded from LLM prompt by default |
| Relevant classes   | `classes.relevant` | Stored in `metadata` for reference                                                  |
| Triggering tests   | `tests.trigger`    | Stored in `metadata`; cross-referenced with parsed failures                         |
| Relevant tests     | `tests.relevant`   | Stored in `metadata`                                                                |

> **Note**: `classes.modified` is the ground-truth oracle. It is never sent to the LLM in pre-fix mode to avoid data leakage.

---

### From `defects4j info` (via `client.info`)

The pipeline runs `defects4j info -p <project> -b <id>` and captures its full stdout as `bug_info`. This text contains:

- Project summary (script dir, base dir, repo, etc.)
- Number of bugs in the project
- Fixed revision ID and date
- Bug report ID and URL
- **Root cause in triggering tests** (the exception + test name mapping)
- List of modified source files

This `bug_info` text is sent verbatim as `bug_info` in the user prompt evidence payload.

---

### From `defects4j checkout` + `defects4j compile` + `defects4j test`

| Operation | D4J command                                   | What it produces                                                  |
| --------- | --------------------------------------------- | ----------------------------------------------------------------- |
| Checkout  | `defects4j checkout -p X -v Yb -w <work_dir>` | Buggy source tree on disk; `work_dir` recorded in context         |
| Compile   | `defects4j compile -w <work_dir>`             | Validates the buggy version compiles; exit code stored in `notes` |
| Test      | `defects4j test -w <work_dir>`                | Generates `failing_tests` file; creates test failure output       |

**From `defects4j test` output** (parsed by `read_failures` + `parse_failing_tests`):

- `test_name` — fully qualified test method (e.g. `org.foo.BarTest::testMethod`)
- `test_class` / `test_method` — split from test name
- `headline` — exception class + message from the first line of the failure block
- `stack_trace` — raw stack trace lines (first 15 lines sent to LLM per failure)
- `frames` — parsed structured frames: `class_name`, `method_name`, `file_name`, `line_number`

The **suspicious frames** are selected from these parsed frames by filtering out framework/JDK/build-tool classes (`org.junit.*`, `java.*`, `org.apache.tools.ant.*`, etc.) and preferring project source frames (up to 12).

---

### From `defects4j export` (via `export_properties`)

After checkout, the pipeline runs `defects4j export -p <property> -w <work_dir>` for each of:

| Export property   | Usage                                                              |
| ----------------- | ------------------------------------------------------------------ |
| `dir.src.classes` | Locates production Java source root(s) for code snippet extraction |
| `dir.bin.classes` | Stored in `exports` for reference                                  |
| `dir.src.tests`   | Locates test Java source root(s) for test snippet extraction       |
| `dir.bin.tests`   | Stored in `exports` for reference                                  |
| `cp.compile`      | Stored in `exports` for reference                                  |
| `cp.test`         | Stored in `exports` for reference                                  |
| `tests.trigger`   | Cross-referenced with failing test output                          |
| `tests.relevant`  | Stored in `exports` for reference                                  |

`dir.src.classes` and `dir.src.tests` are the most critical — they are used to resolve Java source files from stack frame class names, enabling production and test code snippet extraction.

---

### From the Checked-Out Source Tree

Using the directory paths from `defects4j export`, the pipeline reads Java source files directly:

| Artifact                     | How collected                                                                              | Sent to LLM as               |
| ---------------------------- | ------------------------------------------------------------------------------------------ | ---------------------------- |
| **Production code snippets** | Source file around each suspicious frame (±12 lines), focus-line marked with `>>`          | `production_code_snippets[]` |
| **Test source code**         | The failing test method body from the test source file (±18 lines, or exact method bounds) | `test_code_snippets[]`       |

Each code snippet carries:

- `class_name`, `file_path`, `start_line`, `end_line`, `focus_line`
- `reason` — why this snippet was selected (e.g. "Stack frame from Foo.bar" or "Test source: BarTest::testFoo")
- `content` — the actual lines with line numbers

---

### From `defects4j coverage` (optional, `--skip-coverage` to disable)

When coverage is enabled, the pipeline runs `defects4j coverage -w <work_dir> [-t <test>] [-i <instrument_file>]`. It parses the resulting Cobertura XML reports (`coverage*.xml`, `cobertura*.xml`) to extract per-class coverage data:

| Coverage field  | Sent to LLM as                                     |
| --------------- | -------------------------------------------------- |
| `class_name`    | Identifier in `coverage_summary[]`                 |
| `line_rate`     | Fraction of executed lines (0.0–1.0)               |
| `branch_rate`   | Fraction of executed branches (0.0–1.0)            |
| `covered_lines` | Top-10 hit lines per class (`line_number`, `hits`) |

Coverage is focused on the **suspicious classes** (those appearing in selected stack frames) to avoid noisy irrelevant data.

---

### From JIRA / GitHub (via `web_fetch`)

Bug report URLs (from `report.url`) are fetched and the content extracted:

| Source type   | Extraction method                                         | Fields extracted                                                                              |
| ------------- | --------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| Apache JIRA   | JIRA REST API (`/rest/api/2/issue/{key}`)                 | `summary`, `description`, `issuetype`, `priority`, `status`, `resolution`, up to 5 `comments` |
| GitHub Issues | GitHub REST API (`/repos/{owner}/{repo}/issues/{number}`) | `title`, `state`, `labels`, `body`, up to 5 `comments`                                        |
| Generic HTML  | HTML → text stripping pipeline                            | Full page text, whitespace-collapsed                                                          |

The result is truncated to **12,000 characters** (`max_chars`) and sent as `bug_report_description` in the user prompt.

---

### From the Fixed Version Checkout (optional, `--include-fix-diff`)

When `--include-fix-diff` is set, the pipeline additionally:

1. Checks out `<bug>f` (fixed version) in a sibling directory
2. Exports `dir.src.classes` for the fixed checkout
3. Diffs each class in `classes.modified` (buggy vs fixed) using `difflib.unified_diff`
4. Sends the diff as `fix_diff_oracle` (labeled clearly as **POST-FIX oracle information**) in the user prompt

This post-fix oracle dramatically improves classification accuracy but breaks the pre-fix-only methodology. Cleaned up automatically after collection.

---

### ODC Opener/Closer Alignment Hints

In addition to raw evidence, the pipeline synthesizes heuristic metadata aligned to ODC opener and closer attributes. These are sent as `odc_opener_hints` and `odc_closer_hints` in every prompt:

**Opener hints** (inferred from combined text of bug report, bug info, failure headlines):

| Hint field            | Values                                                                                                       | Derivation                                                          |
| --------------------- | ------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------- |
| `activity_candidates` | `Unit Test`, `Function Test`, `System Test`                                                                  | Keyword matching (`integration`, `workload`, `stress`)              |
| `trigger_candidates`  | `Test Variation`, `Test Sequencing`, `Test Interaction`, `Recovery/Exception`, `Workload/Stress`, `Coverage` | Keyword matching on exception types, ordering, interaction keywords |
| `impact_candidates`   | `Reliability`, `Performance`, `Integrity/Security`, `Documentation`, `Capability`                            | Keyword matching on crash/slow/security/documentation tokens        |

**Closer hints** (partially inferred from fix diff shape when available):

| Hint field       | Values                               | Derivation                                                                              |
| ---------------- | ------------------------------------ | --------------------------------------------------------------------------------------- |
| `target`         | `Design/Code` (always)               | Fixed for this pipeline scope                                                           |
| `qualifier_hint` | `Missing`, `Incorrect`, `Extraneous` | From fix diff: lines added-only → Missing; removed-only → Extraneous; mixed → Incorrect |
| `age_hint`       | `New`, `Base`, `Rewritten`           | From fix diff size: `>=120` delta → Rewritten; large new block → New; else → Base       |
| `source_hint`    | `null`                               | Not currently inferred                                                                  |

These hints are **additive and optional** — the LLM is free to accept or reject them based on evidence.

---

## What the Pipeline Does (Step by Step)

1. **Queries bug metadata** via `defects4j query` — retrieves `report.url`, `revision.buggy/fixed`, `tests.trigger`, `classes.modified` (hidden oracle), and related fields.
2. **Fetches bug info** via `defects4j info` — captures plain-text root cause summary and triggering test list.
3. **Fetches bug report page** — downloads and parses JIRA/GitHub content (title, description, comments) via structured API or HTML fallback.
4. **Checks out the buggy version** via `defects4j checkout -v <bug>b`.
5. **Compiles the buggy version** via `defects4j compile`.
6. **Runs tests** via `defects4j test` — always fails on the buggy version; generates `failing_tests` file.
7. **Parses test failures** — reads `failing_tests`, extracts structured stack frames (`class_name`, `method_name`, `file_name`, `line_number`).
8. **Exports Defects4J properties** via `defects4j export` — obtains source directory paths and classpaths.
9. **Filters suspicious frames** — removes JUnit, Ant, JDK, Hamcrest, Mockito, and 20+ other framework prefixes; keeps up to 12 project source frames.
10. **Extracts production code snippets** — reads Java source ±12 lines around each suspicious frame with focus-line marker.
11. **Extracts test source code** — reads the failing test method body (±18 lines or exact method bounds) from the test source tree.
12. **Optionally runs coverage** via `defects4j coverage` — instruments suspicious classes, parses Cobertura XML for line/branch rates. Retries without instrument file if first attempt fails.
13. **Optionally collects fix diff** (`--include-fix-diff`) — checks out `<bug>f`, diffs modified classes, stores as post-fix oracle.
14. **Writes `context.json`** — serialised `BugContext` with all of the above.
15. **Classifies using LLM** — sends structured evidence to Gemini/OpenRouter with a scientific debugging prompt containing:
    - Contrastive ODC taxonomy (7 types with indicators, boundaries, and examples)
    - 5 canonical few-shot examples with explicit `NOT X` reasoning
    - 7-question diagnostic decision tree
    - Anti-bias rules preventing default-to-Function behavior
16. **Adds ODC mapping hints** (optional) — Includes heuristic opener/closer-aligned metadata in prompt evidence (`odc_opener_hints`, `odc_closer_hints`) to improve traceability to ODC concepts.
17. **Writes outputs** — `context.json`, `classification.json`, and a markdown report.

### Optional ODC Opener/Closer Metadata

The core pipeline output remains the same (`odc_type`, `family`, confidence, reasoning).

In addition, `classification.json` may include optional ODC-aligned fields when inferable:

- Opener-oriented (inferred): `inferred_activity`, `inferred_triggers`, `inferred_impact`
- Closer-oriented (optional): `target` (defaults to `Design/Code`), `qualifier`, `age`, `source`

These fields are additive and optional-first for backward compatibility.

---

## ODC Defect Types

The pipeline classifies into 7 ODC **Defect Type** categories:

| ODC Defect Type               | Family                | Description                                                                                                                                                                                          |
| ----------------------------- | --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Algorithm/Method**          | Control and Data Flow | Efficiency or correctness problems that affect the task and can be fixed by (re)implementing an algorithm or local data structure without the need for requesting a design change...                 |
| **Assignment/Initialization** | Control and Data Flow | Value(s) assigned incorrectly or not assigned at all...                                                                                                                                              |
| **Checking**                  | Control and Data Flow | Errors caused by missing or incorrect validation of parameters or data in conditional statements...                                                                                                  |
| **Timing/Serialization**      | Control and Data Flow | Necessary serialization of shared resource was missing, the wrong resource was serialized, or the wrong serialization technique was employed...                                                      |
| **Function/Class/Object**     | Structural            | The error should require a formal design change, as it affects significant capability, end-user interfaces, product interfaces, interface with hardware architecture, or global data structure(s)... |
| **Interface/O-O Messages**    | Structural            | Communication problems between modules, components, device drivers, objects, or functions...                                                                                                         |
| **Relationship**              | Structural            | Problems related to associations among procedures, data structures and objects. Such associations may be conditional...                                                                              |

---

## Setup

This project supports two installation modes:

- **Mode A: Windows + WSL (Ubuntu)**
- **Mode B: Native Ubuntu/Linux**

Use path placeholders below so the commands stay valid regardless of where you keep your repos.

| Placeholder    | Meaning                                               |
| -------------- | ----------------------------------------------------- |
| `<IMPL_DIR>`   | Absolute path to this repo (`d4j_odc_implementation`) |
| `<D4J_HOME>`   | Absolute path to your Defects4J clone                 |
| `<LINUX_USER>` | Your Linux username                                   |

Example: `<IMPL_DIR>` might be `C:\dev\thesis\d4j_odc_implementation` on Windows, or `/home/alex/dev/d4j_odc_implementation` on Ubuntu.

`<D4J_HOME>` is defined by where you clone Defects4J. If you use the default clone command below, it will usually be the absolute path of a `defects4j` directory.

### Mode A - Windows + WSL (Ubuntu)

#### 1) Prerequisites

- Windows: Python 3.11+
- WSL: Ubuntu installed and working
- Recommended layout: keep `<IMPL_DIR>` on Windows, keep `<D4J_HOME>` inside WSL Linux filesystem

#### 2) Install Defects4J dependencies in WSL

```bash
sudo apt update
sudo apt install -y openjdk-11-jdk git subversion perl cpanminus curl unzip
git config --global core.autocrlf input
```

#### 3) Clone and initialize Defects4J in WSL

```bash
cd /home/<LINUX_USER>
git clone https://github.com/rjust/defects4j.git
cd defects4j
export D4J_HOME="$(pwd)"
sudo cpanm --installdeps .
./init.sh
perl framework/bin/defects4j info -p Lang
```

If `info -p Lang` fails with missing Perl modules (for example `String::Interpolate`):

```bash
sudo cpanm String::Interpolate
sudo cpanm --installdeps <D4J_HOME>
```

#### 4) Create Python environment in Windows repo

```powershell
cd <IMPL_DIR>

python -m venv .venv
.venv\Scripts\Activate.ps1          # PowerShell
# or: .venv\Scripts\activate.bat    # CMD

pip install -r requirements.txt
pip install -e .
```

#### 5) Configure `.env` (WSL mode)

```dotenv
DEFAULT_LLM_PROVIDER=gemini
DEFAULT_LLM_MODEL=gemini-3.1-flash-lite-preview
GEMINI_API_KEY=your_real_key_here
DEFECTS4J_CMD=wsl perl <D4J_HOME>/framework/bin/defects4j
DEFECTS4J_PATH_STYLE=wsl
```

### Mode B - Native Ubuntu/Linux

#### 1) Prerequisites

```bash
sudo apt update
sudo apt install -y openjdk-11-jdk git subversion perl cpanminus curl unzip
```

#### 2) Clone and initialize Defects4J

```bash
git clone https://github.com/rjust/defects4j.git
cd defects4j
export D4J_HOME="$(pwd)"
sudo cpanm --installdeps .
./init.sh
perl framework/bin/defects4j info -p Lang
```

If `info -p Lang` fails with missing Perl modules:

```bash
sudo cpanm String::Interpolate
sudo cpanm --installdeps <D4J_HOME>
```

#### 3) Create Python environment in implementation repo

```bash
cd <IMPL_DIR>
python3 -m venv .venv

# If venv creation fails with "ensurepip is not available":
# sudo apt install -y python3-venv
# (or version-specific package, e.g. python3.12-venv)

source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

#### 4) Configure `.env` (native Linux mode)

```dotenv
DEFAULT_LLM_PROVIDER=gemini
DEFAULT_LLM_MODEL=gemini-3.1-flash-lite-preview
GEMINI_API_KEY=your_real_key_here
DEFECTS4J_CMD=perl <D4J_HOME>/framework/bin/defects4j
DEFECTS4J_PATH_STYLE=native
```

#### 5) Quick validation (both modes)

```bash
python -m d4j_odc_pipeline d4j pids
python -m d4j_odc_pipeline d4j info --project Lang --bug 1
```

If validation fails with `Can't open perl script .../framework/bin/defects4j`, verify that `<D4J_HOME>` in `DEFECTS4J_CMD` matches your actual clone location exactly.

---

## Usage

Commands are provided in both **PowerShell** (Windows) and **Bash** (Ubuntu/Linux/WSL) variants. Copy from the section that matches your environment.

### `collect` — Build pre-fix context

Checks out the buggy version, runs tests, fetches all evidence, and saves `context.json`.

Output defaults to `.dist/runs/<project>_<bug>_prefix/context.json` (or `_postfix` with `--include-fix-diff`) when `--output` is omitted.

**PowerShell (Windows):**

```powershell
# With explicit output path
python -m d4j_odc_pipeline collect `
  --project Lang --bug 1 `
  --work-dir .\work\Lang_1b `
  --output .\artifacts\Lang_1\context.json `
  --skip-coverage

# With default output (.dist/runs/Lang_1_prefix/context.json)
python -m d4j_odc_pipeline collect `
  --project Lang --bug 1 `
  --work-dir .\work\Lang_1b `
  --skip-coverage

# Post-fix mode (.dist/runs/Lang_1_postfix/context.json)
python -m d4j_odc_pipeline collect `
  --project Lang --bug 1 `
  --work-dir .\work\Lang_1b `
  --include-fix-diff --skip-coverage
```

**Bash (Ubuntu/Linux/WSL):**

```bash
python -m d4j_odc_pipeline collect \
  --project Lang --bug 1 \
  --work-dir ./work/Lang_1b \
  --skip-coverage
```

### `classify` — Classify an existing context

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

### `run` — End-to-end collection + classification

Runs both `collect` and `classify` in a single command.

All output paths default to `.dist/runs/<project>_<bug>_prefix/` (or `_postfix` with `--include-fix-diff`) when omitted:

- `context.json`, `classification.json`, `report.md`

**PowerShell (Windows):**

```powershell
# Minimal — pre-fix (all outputs go to .dist/runs/Lang_1_prefix/)
python -m d4j_odc_pipeline run `
  --project Lang --bug 1 `
  --work-dir .\work\Lang_1b `
  --skip-coverage

# Post-fix mode (outputs go to .dist/runs/Lang_1_postfix/)
python -m d4j_odc_pipeline run `
  --project Lang --bug 1 `
  --work-dir .\work\Lang_1b `
  --include-fix-diff --skip-coverage
```

**Bash (Ubuntu/Linux/WSL):**

```bash
# Minimal — pre-fix (all outputs go to .dist/runs/Lang_1_prefix/)
python -m d4j_odc_pipeline run \
  --project Lang --bug 1 \
  --work-dir ./work/Lang_1b \
  --skip-coverage
```

### Switching LLM provider (with environment variables)

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

### `d4j` — Defects4J proxy commands

Convenience wrappers around common Defects4J operations with formatted output:

```bash
python -m d4j_odc_pipeline d4j pids                         # List all projects
python -m d4j_odc_pipeline d4j bids --project Lang           # List bug IDs
python -m d4j_odc_pipeline d4j bids --project Lang --all     # Include deprecated IDs
python -m d4j_odc_pipeline d4j info --project Lang --bug 1   # Show bug details
```

### `compare` and `compare-batch` — Accuracy Evaluation

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

### `multifault` and `multifault-enrich` — Multi-Fault Analysis

Query multi-fault co-existence data from the [defects4j-mf](https://github.com/DCallaz/defects4j-mf) dataset. Supported projects: Chart, Closure, Lang, Math, Time.

**PowerShell (Windows):**

```powershell
# Query multi-fault data for a specific bug
python -m d4j_odc_pipeline multifault --project Lang --bug 1

# Query with JSON output
python -m d4j_odc_pipeline multifault --project Lang --bug 1 `
  --output .\artifacts\Lang_1\multifault.json

# Enrich an existing classification with multi-fault context
python -m d4j_odc_pipeline multifault-enrich `
  --classification .\artifacts\Lang_1\classification.json `
  --output .\artifacts\Lang_1\classification_enriched.json
```

**Bash (Ubuntu/Linux/WSL):**

```bash
# Query multi-fault data for a specific bug
python -m d4j_odc_pipeline multifault --project Lang --bug 1

# Enrich an existing classification with multi-fault context
python -m d4j_odc_pipeline multifault-enrich \
  --classification ./artifacts/Lang_1/classification.json \
  --output ./artifacts/Lang_1/classification_enriched.json
```

The multi-fault data directory is resolved in order: `--fault-data-dir` CLI argument → `MULTIFAULT_DATA_DIR` env var → `./fault_data/` relative to the implementation root.

### `study-plan`, `study-run`, and `study-analyze` — Large-Scale Batch Workflow

These commands support large studies (for example, 50-70 bugs) with paired pre-fix/post-fix runs and built-in cross-artifact analysis.

**Key features:**

- **Graceful Ctrl+C** — Press Ctrl+C once to finish the current bug and stop cleanly. Press twice to force-quit.
- **Checkpoint/Resume** — A `checkpoint.json` is written after each bug completes. Re-running the same command resumes from where it left off.
- **Progress bar** — Real-time progress display showing current bug and completion count.
- **Default paths** — `--artifacts-root`, `--work-root`, and `--summary-output` default to `.dist/study/` when omitted.

**PowerShell (Windows):**

```powershell
# Step 1: Build a balanced manifest across all discovered projects
python -m d4j_odc_pipeline study-plan `
  --output .\.dist\study\manifest_68.json `
  --target-bugs 68 `
  --min-per-project 1

# Step 2: Execute prefix + postfix runs for every manifest entry
# All paths default to .dist/study/ — only --manifest is required
python -m d4j_odc_pipeline study-run `
  --manifest .\.dist\study\manifest_68.json `
  --skip-coverage

# To resume after interruption, just re-run the same command:
python -m d4j_odc_pipeline study-run `
  --manifest .\.dist\study\manifest_68.json `
  --skip-coverage

# Step 3: Analyze classification.json + context.json + report.md together
python -m d4j_odc_pipeline study-analyze `
  --prefix-dir .\.dist\study\artifacts\prefix `
  --postfix-dir .\.dist\study\artifacts\postfix `
  --manifest .\.dist\study\manifest_68.json `
  --require-all-projects `
  --output .\.dist\study\analysis.json `
  --report .\.dist\study\analysis.md
```

**Bash (Ubuntu/Linux/WSL):**

```bash
# Step 1: Build a balanced manifest across all discovered projects
python -m d4j_odc_pipeline study-plan \
  --output ./.dist/study/manifest_68.json \
  --target-bugs 68 \
  --min-per-project 1

# Step 2: Execute prefix + postfix runs (defaults to .dist/study/)
python -m d4j_odc_pipeline study-run \
  --manifest ./.dist/study/manifest_68.json \
  --skip-coverage

# Step 3: Analyze
python -m d4j_odc_pipeline study-analyze \
  --prefix-dir ./.dist/study/artifacts/prefix \
  --postfix-dir ./.dist/study/artifacts/postfix \
  --manifest ./.dist/study/manifest_68.json \
  --require-all-projects \
  --output ./.dist/study/analysis.json \
  --report ./.dist/study/analysis.md
```

---

## CLI Parameters

### Common parameters (used by `collect`, `run`)

| Parameter            | Required | Description                                              |
| -------------------- | :------: | -------------------------------------------------------- |
| `--project`          |   Yes    | Defects4J project id (`Lang`, `Math`, `Chart`, etc.)     |
| `--bug`              |   Yes    | Numeric bug id. Automatically suffixed to `<bug>b`.      |
| `--work-dir`         |   Yes    | Checkout directory for the buggy revision.               |
| `--defects4j-cmd`    |    No    | Override `DEFECTS4J_CMD` for this run.                   |
| `--snippet-radius`   |    No    | Source lines around suspicious frames. Default: `12`.    |
| `--skip-coverage`    |    No    | Skip the `defects4j coverage` step.                      |
| `--include-fix-diff` |    No    | Include buggy→fixed diff as post-fix oracle (see below). |

### LLM parameters (used by `classify`, `run`)

| Parameter                              | Required | Description                                          |
| -------------------------------------- | :------: | ---------------------------------------------------- |
| `--context`                            |  Yes\*   | Path to existing `context.json`. (_`classify` only_) |
| `--output` / `--classification-output` |   Yes    | Path for classification JSON.                        |
| `--report`                             |   No†    | Markdown report path. (†Required in `run`.)          |
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

| Parameter                          | Required | Description                                                                            |
| ---------------------------------- | :------: | -------------------------------------------------------------------------------------- |
| `--manifest`                       |  Yes\*   | Study manifest JSON path. (\*Required in `study-run` and optional in `study-analyze`.) |
| `--target-bugs`                    |    No    | Desired study size for `study-plan` (default: `68`).                                   |
| `--min-per-project`                |    No    | Minimum selected bugs per project in `study-plan` (default: `1`).                      |
| `--seed`                           |    No    | Reproducible sampling seed for `study-plan` (default: `42`).                           |
| `--projects`                       |    No    | Optional project subset for `study-plan`; omit to include all discovered projects.     |
| `--allow-partial-project-coverage` |    No    | Allow incomplete project coverage during `study-plan`.                                 |
| `--artifacts-root`                 |    No    | Root output directory for paired batch artifacts. Defaults to `.dist/study/artifacts`. |
| `--work-root`                      |    No    | Root checkout directory for batch runs. Defaults to `.dist/study/work`.                |
| `--summary-output`                 |    No    | Batch execution summary JSON path. Defaults to `.dist/study/summary.json`.             |
| `--no-skip-existing`               |    No    | Re-run entries even when artifacts already exist (`study-run`).                        |
| `--prompt-output`                  |    No    | Save prompt payloads for each entry (`study-run`).                                     |
| `--prefix-dir`                     |   Yes‡   | Prefix artifact directory for analysis. (‡`study-analyze` only)                        |
| `--postfix-dir`                    |   Yes‡   | Postfix artifact directory for analysis. (‡`study-analyze` only)                       |
| `--expected-projects`              |    No    | Explicit expected project list for `study-analyze`.                                    |
| `--require-all-projects`           |    No    | Enforce full project coverage in `study-run` and `study-analyze`.                      |

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
  --work-dir .\work\Lang_1b `
  --output .\artifacts\Lang_1\context.json `
  --skip-coverage

# Step 2: Collect post-fix context (with diff)
python -m d4j_odc_pipeline collect `
  --project Lang --bug 1 `
  --work-dir .\work\Lang_1b_fix `
  --output .\artifacts\Lang_1f\context.json `
  --skip-coverage --include-fix-diff

# Step 3: Classify both (reuse existing context — instant, no checkout needed)
python -m d4j_odc_pipeline classify `
  --context .\artifacts\Lang_1\context.json `
  --output .\artifacts\Lang_1\classification.json `
  --report .\artifacts\Lang_1\report.md

python -m d4j_odc_pipeline classify `
  --context .\artifacts\Lang_1f\context.json `
  --output .\artifacts\Lang_1f\classification.json `
  --report .\artifacts\Lang_1f\report.md
```

**Bash (Ubuntu/Linux/WSL):**

```bash
# Step 1: Collect pre-fix context (no diff)
python -m d4j_odc_pipeline collect \
  --project Lang --bug 1 \
  --work-dir ./work/Lang_1b \
  --output ./artifacts/Lang_1/context.json \
  --skip-coverage

# Step 2: Collect post-fix context (with diff)
python -m d4j_odc_pipeline collect \
  --project Lang --bug 1 \
  --work-dir ./work/Lang_1b_fix \
  --output ./artifacts/Lang_1f/context.json \
  --skip-coverage --include-fix-diff

# Step 3: Classify both (reuse existing context - instant, no checkout needed)
python -m d4j_odc_pipeline classify \
  --context ./artifacts/Lang_1/context.json \
  --output ./artifacts/Lang_1/classification.json \
  --report ./artifacts/Lang_1/report.md

python -m d4j_odc_pipeline classify \
  --context ./artifacts/Lang_1f/context.json \
  --output ./artifacts/Lang_1f/classification.json \
  --report ./artifacts/Lang_1f/report.md

# Step 4: Compare
python -m d4j_odc_pipeline compare \
  --prefix ./artifacts/Lang_1/classification.json \
  --postfix ./artifacts/Lang_1f/classification.json \
  --output ./artifacts/Lang_1/comparison.json \
  --report ./artifacts/Lang_1/comparison.md
```

Both `classification.json` and `report.md` include an **`evidence_mode`** field (`"pre-fix"` or `"post-fix"`) so you can programmatically compare results.

> **Note**: The fix diff is clearly labeled in the prompt as "POST-FIX oracle information" so the LLM knows it wouldn't normally be available. The `classes.modified` field remains hidden from the prompt regardless.

---

## Output Files

### Default Output Directories

| Command scope | Default root   | Example path                                                     |
| ------------- | -------------- | ---------------------------------------------------------------- |
| Standalone    | `.dist/runs/`  | `.dist/runs/Lang_1_prefix/classification.json`                   |
| Batch study   | `.dist/study/` | `.dist/study/artifacts/prefix/Lang_1_prefix/classification.json` |

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

### `classification.json` Schema

| Field                  | Description                                                  |
| ---------------------- | ------------------------------------------------------------ |
| `odc_type`             | One of the 7 ODC defect type names                           |
| `family`               | Canonical family: `Control and Data Flow` or `Structural`    |
| `confidence`           | Float 0.0–1.0                                                |
| `needs_human_review`   | Boolean                                                      |
| `evidence_mode`        | `"pre-fix"` or `"post-fix"`                                  |
| `observation_summary`  | Failure symptoms observed                                    |
| `hypothesis`           | Specific root-cause mechanism                                |
| `prediction`           | What code would look like if hypothesis is correct           |
| `experiment_rationale` | How evidence confirms or refutes the hypothesis              |
| `reasoning_summary`    | Why this ODC type was chosen over alternatives               |
| `evidence_used`        | Specific evidence items cited                                |
| `evidence_gaps`        | Missing evidence or ambiguity                                |
| `alternative_types`    | Runner-up ODC types with explicit `why_not_primary`          |
| `target`               | ODC closer: `Design/Code` (default)                          |
| `qualifier`            | ODC closer: `Missing`, `Incorrect`, `Extraneous` (optional)  |
| `age`                  | ODC closer: `Base`, `New`, `Rewritten`, `ReFixed` (optional) |
| `source`               | ODC closer: `Developed In-House`, etc. (optional)            |
| `inferred_activity`    | ODC opener: inferred testing activity (optional)             |
| `inferred_triggers`    | ODC opener: inferred trigger candidates (optional)           |
| `inferred_impact`      | ODC opener: inferred impact candidates (optional)            |

---

## Provider Options

| Provider            | Default key env var  | Default base URL                                   |
| ------------------- | -------------------- | -------------------------------------------------- |
| `gemini`            | `GEMINI_API_KEY`     | `https://generativelanguage.googleapis.com/v1beta` |
| `openrouter`        | `OPENROUTER_API_KEY` | `https://openrouter.ai/api/v1`                     |
| `openai-compatible` | `OPENAI_API_KEY`     | `https://api.openai.com/v1`                        |

OpenRouter example:

```dotenv
DEFAULT_LLM_PROVIDER=openrouter
DEFAULT_LLM_MODEL=openai/gpt-5.2
OPENROUTER_API_KEY=your_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_HTTP_REFERER=https://your-site.example
OPENROUTER_APP_TITLE=Defects4J ODC Pipeline
```

---

## Project Structure

```bash
d4j_odc_pipeline/
├── __init__.py        # Package init
├── __main__.py        # Entry point (delegates to cli.main)
├── cli.py             # Argparse CLI: collect, classify, run, compare, compare-batch, multifault, multifault-enrich, study-*, d4j
├── pipeline.py        # Core orchestration: collect_bug_context, classify_bug_context, write_markdown_report
├── batch.py           # Batch manifest generation, batch execution, and cross-artifact analysis
├── defects4j.py       # Defects4J client (checkout, compile, test, coverage, query, export, info, pids, bids)
├── web_fetch.py       # Bug report fetcher: GitHub API, JIRA API, generic HTML → text pipeline
├── llm.py             # LLM API client (Gemini, OpenRouter, OpenAI-compatible)
├── prompting.py       # Prompt engineering: system prompt, user prompt, ODC hints, few-shot examples
├── odc.py             # ODC type definitions with indicators, boundaries, examples, and family mapping
├── models.py          # Data models: BugContext, ClassificationResult, CodeSnippet, StackFrame, Failure, CoverageClass
├── parsing.py         # Stack trace parser, JSON extraction from LLM output
├── comparison.py      # Enhanced comparison: strict/top2/family, semantic distance, evidence asymmetry, divergence patterns, insights
├── multifault.py      # Multi-fault data loader for defects4j-mf: co-existing faults, locations, enrichment
└── console.py         # Rich terminal output helpers (spinner, panels, tables)
```

---

## Design Choices

- The LLM sees **pre-fix evidence only** by default.
- `classes.modified` is stored as a `hidden_oracle` for offline analysis but excluded from the LLM prompt.
- The default prompt style is `scientific`, following observation → hypothesis → prediction → experiment → conclusion.
- The ODC target is the 7-class **Defect Type** attribute. ODC opener/closer attributes are inferred as additive optional metadata.
- Evidence is separated into `production_code_snippets` and `test_code_snippets` so the LLM distinguishes "where the bug is" from "what behavior is expected."
- Framework classes (JUnit, Ant, JDK, Hamcrest, Mockito, etc.) are aggressively filtered to keep only project source frames.
- Bug report content is fetched from JIRA/GitHub and truncated to 12,000 chars to avoid prompt explosion.
- ODC family is **always** derived from the canonical `odc.family_for()` mapping — the LLM's `family` field is overwritten to prevent drift.
- Comparison uses a 4-tier hierarchy: Strict Match > Top-2 Match > Family Match > Cohen's Kappa, giving partial credit for near-misses.
- Defects4J supports both WSL mode (`DEFECTS4J_PATH_STYLE=wsl`) and native Linux mode (`DEFECTS4J_PATH_STYLE=native`).
- **Batch runs are resumable** — `checkpoint.json` tracks completed entries; re-running `study-run` skips bugs that finished previously.
- **Graceful shutdown** — Ctrl+C during `study-run` finishes the current bug, saves checkpoint, and exits cleanly. A second Ctrl+C force-quits.
- **Standardized output layout** — standalone commands default to `.dist/runs/`, batch studies default to `.dist/study/`.

---

## Official References

- [Defects4J CLI overview](https://defects4j.org/html_doc/defects4j.html)
- [Defects4J docs index](https://defects4j.org/html_doc/index.html)
- [d4j-checkout](https://defects4j.org/html_doc/d4j/d4j-checkout.html) · [d4j-compile](https://defects4j.org/html_doc/d4j/d4j-compile.html) · [d4j-test](https://defects4j.org/html_doc/d4j/d4j-test.html) · [d4j-coverage](https://defects4j.org/html_doc/d4j/d4j-coverage.html)
- [d4j-export](https://defects4j.org/html_doc/d4j/d4j-export.html) · [d4j-query](https://defects4j.org/html_doc/d4j/d4j-query.html) · [d4j-bids](https://defects4j.org/html_doc/d4j/d4j-bids.html) · [d4j-info](https://defects4j.org/html_doc/d4j/d4j-info.html) · [d4j-pids](https://defects4j.org/html_doc/d4j/d4j-pids.html)
