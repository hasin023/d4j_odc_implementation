# defects4j-mf CLI Tool — Full Integration Plan for d4j_odc_pipeline

> **Status**: Future work — NOT for immediate implementation.
>
> **Purpose**: This document provides a step-by-step blueprint for integrating the
> `defects4j_multi` CLI tool from the [defects4j-mf](https://github.com/DCallaz/defects4j-mf)
> project directly into our `d4j_odc_pipeline` CLI. An LLM agent reading this document
> should be able to fully implement the integration without additional research.

---

## Table of Contents

1. [Current State Assessment](#1-current-state-assessment)
2. [What defects4j-mf Actually Is](#2-what-defects4j-mf-actually-is)
3. [Why We Need CLI Integration](#3-why-we-need-cli-integration)
4. [Prerequisites & Environment Requirements](#4-prerequisites--environment-requirements)
5. [Setup Steps: Installing defects4j-mf](#5-setup-steps-installing-defects4j-mf)
6. [Architecture: How the CLI Tool Works](#6-architecture-how-the-cli-tool-works)
7. [Integration Design](#7-integration-design)
8. [Implementation Steps (Ordered)](#8-implementation-steps-ordered)
9. [CLI Command Specifications](#9-cli-command-specifications)
10. [Environment Configuration](#10-environment-configuration)
11. [WSL Considerations](#11-wsl-considerations)
12. [Testing Strategy](#12-testing-strategy)
13. [Risk Assessment](#13-risk-assessment)
14. [File-by-File Change Map](#14-file-by-file-change-map)

---

## 1. Current State Assessment

### What We Have Now

Our pipeline currently uses a **JSON-only approach** to multi-fault data:

```
implementation/
├── fault_data/             # Copied from defects4j-mf/fault_data/
│   ├── Chart.json          # Version → fault_id → [triggering tests]
│   ├── Chart_backtrack.json # Fault location tracking
│   ├── Closure.json
│   ├── Closure_backtrack.json
│   ├── Lang.json
│   ├── Lang_backtrack.json
│   ├── Math.json
│   ├── Math_backtrack.json
│   ├── Time.json
│   └── Time_backtrack.json
└── d4j_odc_pipeline/
    └── multifault.py       # Pure-Python parser for the above JSONs
```

### What This Gives Us

- Query co-existing fault IDs for any version of the 5 supported projects
- View triggering test names and fault locations
- Enrich existing classification JSONs with multi-fault context
- No external dependencies beyond the JSON files

### What This Does NOT Give Us

- **No multi-fault checkout** — we can't actually check out a version with transplanted tests
- **No multi-fault coverage** — we can't run GZoltar-based coverage with fault identification
- **No project expansion** — we're limited to the 5 projects that have pre-computed JSON data
- **No dynamic fault discovery** — we can't discover multi-fault data for newly added D4J projects

---

## 2. What defects4j-mf Actually Is

### Repository Structure

```
defects4j-mf/
├── README.md                           # Setup + usage docs (well-documented)
├── setup.sh                            # Automated installer
├── defects4j_multi_with_jars.patch     # ~10.8 MB git patch applied to D4J
├── multi_fault_dataset_paper_summary.md # Paper methodology summary
├── projects.txt                        # Supported projects: Chart, Closure, Lang, Math, Time
├── gen_coverage.sh                     # Batch coverage generation
├── single_coverage.sh                  # Per-version coverage
├── docker/
│   └── Dockerfile                      # Ubuntu 20.04 + Java 8 + D4J container
└── fault_data/
    ├── multi.tar.bz2                   # ~65.8 MB compressed fault data archive
    ├── {Project}.json                  # Multi-fault version maps
    └── {Project}_backtrack.json        # Fault location tracking
```

### How It Works (High Level)

1. **Patches Defects4J** — applies `defects4j_multi_with_jars.patch` to a vanilla D4J installation
2. **Adds `defects4j_multi` command** — a bash script at `$D4J_HOME/framework/bin/defects4j_multi`
3. **Adds Python helper scripts** — in `$D4J_HOME/framework/bin/scripts/` (backtrack.py, checkout.py, copy_test.py, etc.)
4. **Adds GZoltar JARs** — for spectrum-based coverage collection
5. **Extracts fault data** — `multi.tar.bz2` → per-version test and location files
6. **Configures fault_data path** — via `config.json` stored alongside scripts

### The `defects4j_multi` CLI Commands

| Command                                       | What It Does                                                                                           | Dependencies                                      |
| --------------------------------------------- | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------- |
| `info -p <project> [-v <version>]`            | Shows co-existing faults per version                                                                   | fault_data JSONs + Python3                        |
| `checkout -p <project> -v <version> -w <dir>` | Checks out version + injects transplanted tests + writes `bug.locations.N` and `tests.trigger.N` files | D4J checkout + Python3 checkout.py + copy_test.py |
| `compile`                                     | Synonym for `defects4j compile`                                                                        | D4J                                               |
| `coverage`                                    | Runs GZoltar for per-test coverage spectrum                                                            | GZoltar JARs + D4J                                |
| `identify -p <project> -v <version> -c <dir>` | Tags coverage spectrum lines with fault IDs                                                            | Python3 find_faults.py + identify_bugs.sh         |
| `configure -f <path>`                         | Sets fault_data directory in config.json                                                               | Python3                                           |

### The Patch Installs These Files

```
$D4J_HOME/framework/bin/
├── defects4j_multi              # Main bash CLI script (case/esac dispatch)
└── scripts/
    ├── backtrack.py             # Fault location tracker
    ├── checkout.py              # Multi-fault checkout + test transplantation
    ├── copy_test.py             # Test file copier
    ├── correct.sh               # Coverage correction
    ├── dump_versions.py         # Version enumerator
    ├── evosuite_clean.sh        # EvoSuite cleanup
    ├── find_faults.py           # Fault finder in coverage
    ├── find_faults.sh           # Shell wrapper for find_faults
    ├── identify_bugs.sh         # Bug identification in coverage spectrum
    ├── config.json              # Configuration (fault_data path)
    └── DiffProcess.jar          # Diff processing for fault tracking
$D4J_HOME/framework/projects/
├── defects4j.export.xml         # Ant build extension
└── lib/
    └── coverage.sh              # GZoltar coverage runner
```

### Specific D4J Version Requirement

**CRITICAL**: The patch is built for a specific D4J commit:

```
git checkout db899aee2347b16fd042e7e62dacac64eba98cae
```

This is pinned in `setup.sh`. The patch may not apply cleanly to newer D4J versions.

---

## 3. Why We Need CLI Integration

### Immediate Benefits

1. **Multi-fault checkout** — get actual source with transplanted tests, enabling richer evidence for classification
2. **Per-bug fault location files** — `bug.locations.N` files give exact line-level fault positions
3. **Per-bug triggering test files** — `tests.trigger.N` files list exactly which tests expose each fault
4. **Coverage spectrum** — GZoltar-based coverage with fault identification

### Research Benefits

1. **Richer evidence** — the pipeline could incorporate transplanted test failures as additional evidence for ODC classification
2. **Fault isolation** — classify individual faults within a multi-fault version separately
3. **Multi-fault-aware prompts** — the LLM could be told "this version has 7 co-existing faults; focus on fault #3"

### Project Expansion

Currently limited to: Chart, Closure, Lang, Math, Time.

With CLI integration, we could **generate multi-fault data for any D4J project** by running the coverage and identification pipeline ourselves. However, this requires:

- A full D4J installation
- Java 8 runtime
- GZoltar JARs (included in the patch)
- Significant compute time per version

---

## 4. Prerequisites & Environment Requirements

### System Requirements

| Requirement          | Version                                     | Notes                                      |
| -------------------- | ------------------------------------------- | ------------------------------------------ |
| **Java**             | JDK 8 (Amazon Corretto 8.0.432 recommended) | Must be Java 8, not 11 or later            |
| **Python**           | ≥ 3.6                                       | For defects4j-mf helper scripts            |
| **Perl**             | ≥ 5.x                                       | For Defects4J itself                       |
| **Git**              | Any recent                                  | For applying patches                       |
| **Maven**            | 3.x                                         | For D4J project compilation                |
| **Subversion (svn)** | Any                                         | Required by D4J for some projects          |
| **cpanm**            | Any                                         | Perl module installer for D4J dependencies |

### Our Environment Specifics

Our pipeline runs on **Windows + WSL (Ubuntu)**:

- D4J is installed inside WSL at a path like `/home/<user>/defects4j/`
- D4J commands are invoked via `wsl perl /home/<user>/defects4j/framework/bin/defects4j`
- Path translation happens via `DEFECTS4J_PATH_STYLE=wsl`

The `defects4j_multi` command is also a **bash script**, so it MUST run inside WSL. This is important for the integration design.

### Docker Alternative

If the WSL setup is too complex, the Dockerfile provides a complete, self-contained environment:

```dockerfile
FROM ubuntu:20.04
# Installs: git curl build-essential wget zip unzip vim subversion perl bc maven cpanminus
# Installs: Java 8 via SDKMAN (8.0.432-amzn)
# Installs: Python3
# Clones defects4j-mf and runs setup.sh
```

---

## 5. Setup Steps: Installing defects4j-mf

### Automatic Setup (Recommended)

Inside WSL:

```bash
# Navigate to defects4j-mf repo
cd /path/to/defects4j-mf

# Run setup with existing D4J installation
./setup.sh /path/to/defects4j

# OR let it install D4J locally
./setup.sh
```

### What `setup.sh` Does (Step by Step)

1. **Checks for existing D4J** — if provided as argument, uses that; otherwise clones D4J
2. **Resets D4J framework/** — `git reset`, `git restore`, `git clean -dfx` the framework directory
3. **Pins D4J to specific commit** — `git checkout db899aee2347b16fd042e7e62dacac64eba98cae`
4. **Runs `./init.sh`** — D4J's own initialization (downloads project repositories)
5. **Exports `D4J_HOME`** — sets environment variable
6. **Applies the patch** — `git apply defects4j_multi_with_jars.patch`
7. **Verifies** — runs `defects4j_multi -h` to check success
8. **Extracts fault data** — `tar -xjf multi.tar.bz2` inside `fault_data/`
9. **Configures fault data path** — `defects4j_multi configure -f /path/to/fault_data`

### Manual Setup

```bash
# 1. Clone Defects4J and pin version
git clone https://github.com/rjust/defects4j.git
cd defects4j
git checkout db899aee2347b16fd042e7e62dacac64eba98cae
cpanm --installdeps .
./init.sh
export D4J_HOME="$(pwd)"
export PATH="$PATH:$D4J_HOME/framework/bin"

# 2. Apply the patch
git apply /path/to/defects4j-mf/defects4j_multi_with_jars.patch

# 3. Verify
defects4j_multi -h

# 4. Extract and configure fault data
cd /path/to/defects4j-mf/fault_data
tar -xjf multi.tar.bz2
defects4j_multi configure -f /path/to/defects4j-mf/fault_data
```

### Post-Setup Verification

```bash
# Should print help text
defects4j_multi -h

# Should show multi-fault info for Lang
defects4j_multi info -p Lang

# Should show version-specific detail
defects4j_multi info -p Lang -v 10
```

---

## 6. Architecture: How the CLI Tool Works

### Command Dispatch

`defects4j_multi` is a bash script that dispatches to sub-commands via `case/esac`:

```
defects4j_multi <command> [args]
    │
    ├── info      → Python3 dump_versions.py + backtrack.py
    ├── checkout  → Python3 checkout.py (calls defects4j checkout internally + copy_test.py)
    ├── compile   → defects4j compile (pass-through)
    ├── coverage  → framework/projects/lib/coverage.sh (uses GZoltar)
    ├── identify  → framework/bin/scripts/identify_bugs.sh → find_faults.py
    └── configure → Python3 inline script → config.json
```

### Data Flow for Multi-Fault Checkout

```
defects4j_multi checkout -p Lang -v 10 -w /tmp/Lang-10
    │
    ├── 1. defects4j checkout -p Lang -v 10b -w /tmp/Lang-10
    │      (standard D4J buggy checkout)
    │
    ├── 2. Read fault_data/{Project}.json
    │      Find version "1-3-4-5-6-7-10" containing bug 10
    │      Extract fault list: [1, 3, 4, 5, 6, 7, 10]
    │
    ├── 3. For each additional fault (reversed order):
    │      - copy_test.py: transplant test files from fault's fixed version
    │      - Write tests.trigger.N with exposing test names
    │
    ├── 4. For each fault:
    │      - backtrack.py: compute fault location in this version
    │      - Write bug.locations.N with file:line mappings
    │
    └── 5. Result in /tmp/Lang-10/:
           ├── src/... (buggy source code)
           ├── test/... (original + transplanted tests)
           ├── bug.locations.1, bug.locations.3, ... bug.locations.10
           └── tests.trigger.1, tests.trigger.3, ... tests.trigger.10
```

### Data Flow for Multi-Fault Coverage

```
defects4j_multi coverage (inside checked-out dir)
    │
    ├── 1. Run GZoltar with all tests (including transplanted)
    │      Produces: sfl/txt/spectra.csv, sfl/txt/matrix.txt, sfl/txt/tests.csv
    │
    └── 2. Result in sfl/txt/:
           ├── spectra.csv   (code elements: class#method:line)
           ├── matrix.txt    (test × element execution matrix)
           └── tests.csv     (test names with pass/fail status)

defects4j_multi identify -p Lang -v 10 -c sfl/txt/
    │
    ├── 1. Read spectra.csv
    ├── 2. For each code element, check if it matches a bug.locations.N
    ├── 3. Annotate spectra.csv entries with fault IDs
    │
    └── 4. Result: spectra.csv elements now tagged as:
           "class#method:line" → "class#method:line:faultId1:faultId2"
```

---

## 7. Integration Design

### Design Principle: Wrapper, Not Embed

We should **wrap** `defects4j_multi` the same way we wrap `defects4j` — through
subprocess calls with path translation, not by embedding the bash/Python scripts.

### Module Architecture

```
d4j_odc_pipeline/
├── multifault.py          # EXISTING: JSON-only query API (keep as-is)
├── multifault_cli.py      # NEW: CLI wrapper for defects4j_multi commands
└── cli.py                 # MODIFY: Add new subcommands
```

### Why a Separate Module (`multifault_cli.py`)

1. **Separation of concerns**: `multifault.py` is pure-Python/JSON-only (no external deps). `multifault_cli.py` requires a working D4J-mf installation.
2. **Graceful degradation**: if D4J-mf is not installed, all JSON-based features still work. Only the CLI-dependent features fail with a clear error.
3. **Testability**: `multifault.py` can be tested without D4J. `multifault_cli.py` tests would be integration tests requiring the full environment.

### Proposed Class: `MultiFaultClient`

Model after the existing `Defects4JClient` in `defects4j.py`:

```python
class MultiFaultClient:
    """Wraps the defects4j_multi CLI tool."""

    def __init__(
        self,
        command: str = "defects4j_multi",
        path_style: str = "native",
        fault_data_dir: str | None = None,
    ):
        self.command = command
        self.path_style = path_style
        self.fault_data_dir = fault_data_dir

    @classmethod
    def from_env(cls) -> "MultiFaultClient":
        """Build from environment variables."""
        ...

    def info(self, project: str, version: int | None = None) -> str:
        """Run defects4j_multi info."""
        ...

    def checkout(self, project: str, version: int, work_dir: Path) -> Path:
        """Check out a multi-fault version with transplanted tests."""
        ...

    def coverage(self, work_dir: Path) -> Path:
        """Run GZoltar coverage in a checked-out multi-fault version."""
        ...

    def identify(self, project: str, version: int, coverage_dir: Path) -> Path:
        """Identify faults in coverage spectrum."""
        ...
```

---

## 8. Implementation Steps (Ordered)

### Phase 1: Environment Setup & Verification

> **Goal**: Ensure defects4j-mf can be installed alongside our existing D4J setup.

1. **Document the D4J version conflict**
   - Our existing D4J may use a different commit than `db899aee`
   - Decide: separate D4J installation for multi-fault, or patch our existing one
   - Recommendation: **use a separate D4J installation** to avoid breaking existing workflow

2. **Create a setup guide**
   - Add instructions for installing defects4j-mf in WSL alongside existing D4J
   - Document the required environment variables

3. **Verify patch application**
   - Clone D4J, pin commit, apply patch inside WSL
   - Verify `defects4j_multi -h` works
   - Verify `defects4j_multi info -p Lang` outputs correctly

### Phase 2: Create `multifault_cli.py`

> **Goal**: Python wrapper for the `defects4j_multi` bash commands.

4. **Create `MultiFaultClient` class**
   - Mirror the `Defects4JClient` pattern from `defects4j.py`
   - Support `from_env()` factory method
   - Handle WSL path translation (reuse existing `_windows_to_wsl_path`)

5. **Implement `info()` method**
   - Run `defects4j_multi info -p <project> [-v <version>]`
   - Parse the table output into structured Python data
   - Return a `MultiFaultInfo` dataclass

6. **Implement `checkout()` method**
   - Run `defects4j_multi checkout -p <project> -v <version> -w <dir>`
   - Verify the checkout produced `bug.locations.N` and `tests.trigger.N` files
   - Return the list of faults found in the checkout

7. **Implement `coverage()` method**
   - Run `defects4j_multi coverage` inside the work dir
   - Parse the resulting `sfl/txt/` data files
   - Return structured coverage data

8. **Implement `identify()` method**
   - Run `defects4j_multi identify -p <project> -v <version> -c <dir>`
   - Parse the annotated spectrum
   - Return fault-to-element mapping

9. **Add availability check**
   - `MultiFaultClient.is_available()` — returns `True` if `defects4j_multi -h` succeeds
   - Used by CLI commands to show helpful errors if not installed

### Phase 3: CLI Integration

> **Goal**: Add new CLI subcommands that use the `MultiFaultClient`.

10. **Add `mf-info` subcommand**

    ```
    python -m d4j_odc_pipeline mf-info --project Lang [--version 10]
    ```

    - Uses `MultiFaultClient.info()`
    - Displays co-existing faults in Rich table format

11. **Add `mf-checkout` subcommand**

    ```
    python -m d4j_odc_pipeline mf-checkout --project Lang --version 10 --work-dir ./work/Lang_10_mf
    ```

    - Uses `MultiFaultClient.checkout()`
    - Displays list of injected faults and test files

12. **Add `mf-coverage` subcommand**

    ```
    python -m d4j_odc_pipeline mf-coverage --work-dir ./work/Lang_10_mf --output ./artifacts/Lang_10/mf_coverage.json
    ```

    - Runs `coverage` + `identify` in sequence
    - Saves structured coverage data

13. **Add `mf-collect` subcommand** (the integrated command)

    ```
    python -m d4j_odc_pipeline mf-collect --project Lang --version 10 \
      --work-dir ./work/Lang_10_mf --output ./artifacts/Lang_10/mf_context.json
    ```

    - Full pipeline: checkout → compile → test → collect evidence → save context
    - The context would include per-fault triggering tests and locations as additional evidence

### Phase 4: Pipeline Enhancement

> **Goal**: Make the classification pipeline aware of multi-fault context.

14. **Extend `BugContext` in `models.py`**
    - Add `multifault_context` field (optional dict)
    - Contains fault count, per-fault tests, per-fault locations

15. **Extend `prompting.py`**
    - When multi-fault data is present, add a section to the prompt:
      ```
      NOTE: This version contains 7 co-existing faults from bugs #1, #3, #4, #5, #6, #7, #10.
      The specific fault under analysis (bug #10) has the following exposing tests:
      - org.apache.commons.lang3.StringUtilsTest::testFoo
      Known fault locations: src/main/java/org/apache/commons/lang3/StringUtils.java:L123
      Focus your classification on THIS specific fault, not the other co-existing faults.
      ```

16. **Extend `comparison.py`**
    - Add multi-fault-aware insights to the evidence asymmetry analysis
    - Use actual fault data (not just "this project is multi-fault") for richer explanations

### Phase 5: Documentation & Testing

17. **Update `.env.example`**

    ```
    # defects4j-mf CLI (optional — only needed for mf-* commands)
    D4J_MULTI_CMD=wsl /home/user/defects4j/framework/bin/defects4j_multi
    D4J_MULTI_HOME=/home/user/defects4j  # same as D4J_HOME if patched in-place
    ```

18. **Add integration tests**
    - `tests/test_multifault_cli.py` — tests requiring D4J-mf (marked as integration)
    - Test `MultiFaultClient.info()` parsing with known output
    - Test checkout verification logic with mocked subprocess

19. **Update AGENTS.md** with new module and command documentation

20. **Update README.md** with setup instructions for D4J-mf CLI mode

---

## 9. CLI Command Specifications

### `mf-info`

```
usage: d4j-odc mf-info [-h] --project PROJECT [--version VERSION]

Query multi-fault info from defects4j_multi CLI.

options:
  --project, -p    Defects4J project ID (e.g., Lang, Math)
  --version, -v    Optional specific version number
```

**Output**: Rich table showing versions and their co-existing faults.

### `mf-checkout`

```
usage: d4j-odc mf-checkout [-h] --project PROJECT --version VERSION --work-dir WORK_DIR

Checkout a multi-fault version with transplanted tests.

options:
  --project, -p    Defects4J project ID
  --version, -v    Version number (bug ID)
  --work-dir, -w   Target directory for checkout
```

**Output**: Rich panel showing checkout results, list of fault files created.

### `mf-coverage`

```
usage: d4j-odc mf-coverage [-h] --work-dir WORK_DIR [--output OUTPUT]

Run GZoltar coverage + fault identification on a multi-fault checkout.

options:
  --work-dir, -w   Checked-out multi-fault version directory
  --output         Path to write coverage JSON
```

**Output**: Coverage spectrum with fault annotations.

### `mf-collect`

```
usage: d4j-odc mf-collect [-h] --project PROJECT --version VERSION --work-dir WORK_DIR --output OUTPUT [--skip-coverage]

Full multi-fault evidence collection pipeline.

options:
  --project, -p        Defects4J project ID
  --version, -v        Version number
  --work-dir, -w       Target directory
  --output             Context JSON output path
  --skip-coverage      Skip GZoltar coverage step
```

**Output**: Context JSON enriched with multi-fault data.

---

## 10. Environment Configuration

### New Environment Variables

| Variable               | Purpose                                  | Default                               | Required |
| ---------------------- | ---------------------------------------- | ------------------------------------- | -------- |
| `D4J_MULTI_CMD`        | Path/command to invoke `defects4j_multi` | Auto-detect from `DEFECTS4J_CMD` path | No       |
| `D4J_MULTI_HOME`       | D4J installation with multi-fault patch  | Same as `D4J_HOME`                    | No       |
| `D4J_MULTI_FAULT_DATA` | Path to extracted multi.tar.bz2 data     | `$D4J_MULTI_HOME/../../fault_data/`   | No       |

### Detection Logic

```python
def _resolve_multi_cmd() -> str:
    # 1. Explicit env var
    cmd = os.environ.get("D4J_MULTI_CMD")
    if cmd:
        return cmd

    # 2. Derive from DEFECTS4J_CMD
    d4j_cmd = os.environ.get("DEFECTS4J_CMD", "")
    if "defects4j" in d4j_cmd:
        # Replace 'defects4j' with 'defects4j_multi' in the command
        # e.g., "wsl perl .../bin/defects4j" → "wsl .../bin/defects4j_multi"
        # NOTE: defects4j_multi is a bash script, not perl
        d4j_bin_dir = d4j_cmd.rsplit("defects4j", 1)[0]
        return d4j_bin_dir + "defects4j_multi"

    # 3. Default
    return "defects4j_multi"
```

### Important: `defects4j_multi` Is Bash, Not Perl

Unlike `defects4j` (which is a Perl script invoked as `wsl perl .../defects4j`),
`defects4j_multi` is a **bash script**. The WSL invocation must be:

```
wsl /home/user/defects4j/framework/bin/defects4j_multi info -p Lang
```

NOT:

```
wsl perl /home/user/defects4j/framework/bin/defects4j_multi info -p Lang
```

This is a critical difference from our existing D4J wrapper.

---

## 11. WSL Considerations

### Path Translation

The same `_windows_to_wsl_path()` from `defects4j.py` applies:

```python
# Windows path: C:\WORK\IUT\Research\work\Lang_10_mf
# WSL path:     /mnt/c/WORK/IUT/Research/work/Lang_10_mf
```

### Command Execution

```python
def _run_multi(self, *args: str) -> subprocess.CompletedProcess:
    if self.path_style == "wsl":
        # defects4j_multi is bash, not perl
        cmd = ["wsl", self.command] + list(args)
    else:
        cmd = [self.command] + list(args)

    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=600,  # multi-fault checkout can be slow
    )
```

### Working Directory Handling

Some `defects4j_multi` commands (like `coverage`) must be run **inside** the checkout directory. In WSL mode:

```python
if self.path_style == "wsl":
    wsl_work_dir = _windows_to_wsl_path(str(work_dir))
    cmd = ["wsl", "bash", "-c", f"cd {wsl_work_dir} && {self.command} coverage"]
```

---

## 12. Testing Strategy

### Unit Tests (No D4J-mf Required)

These test the Python wrapper logic without calling the actual CLI:

```python
class TestMultiFaultClient:
    def test_resolve_multi_cmd_from_d4j_cmd(self):
        """D4J_MULTI_CMD auto-detection from DEFECTS4J_CMD."""
        ...

    def test_parse_info_table_output(self):
        """Parse the tabular output from defects4j_multi info."""
        sample_output = """
        +------------------------------------------------------------------------------+
        | Version | Identified bugs                                                    |
        +------------------------------------------------------------------------------+
        | 1       | 1, 3, 4, 5, 6, 7, 10                                              |
        +------------------------------------------------------------------------------+
        """
        # Test that this parses correctly

    def test_wsl_path_for_multi_cmd(self):
        """Ensure defects4j_multi uses bash, not perl."""
        ...

    def test_checkout_produces_fault_files(self):
        """Verify checkout result parser finds bug.locations.N files."""
        ...
```

### Integration Tests (Requires D4J-mf Installation)

Mark these with `@pytest.mark.integration`:

```python
@pytest.mark.integration
class TestMultiFaultCLIIntegration:
    def test_info_lang(self):
        """Live test: defects4j_multi info -p Lang."""
        ...

    def test_checkout_lang_10(self):
        """Live test: checkout Lang version 10."""
        ...
```

---

## 13. Risk Assessment

### High Risk

| Risk                            | Impact                                                                    | Mitigation                                            |
| ------------------------------- | ------------------------------------------------------------------------- | ----------------------------------------------------- |
| **D4J version conflict**        | Patching existing D4J may break our pipeline                              | Use separate D4J installation for multi-fault         |
| **Patch may not apply cleanly** | Git patch is version-pinned to commit `db899aee`                          | Pin D4J version OR maintain a fork                    |
| **Long execution times**        | Multi-fault checkout + GZoltar coverage can take 5-15 minutes per version | Add timeouts, progress indicators, skip-coverage flag |

### Medium Risk

| Risk                         | Impact                                                | Mitigation                                  |
| ---------------------------- | ----------------------------------------------------- | ------------------------------------------- |
| **GZoltar compatibility**    | GZoltar requires Java 8; newer Java versions may fail | Document Java 8 requirement clearly         |
| **WSL memory**               | GZoltar + Maven builds are memory-intensive           | Document minimum 4GB RAM for WSL            |
| **multi.tar.bz2 extraction** | 65.8 MB compressed → potentially large extracted data | Only extract once; verify extraction status |

### Low Risk

| Risk                   | Impact                                     | Mitigation                             |
| ---------------------- | ------------------------------------------ | -------------------------------------- |
| **Project expansion**  | Not all D4J projects have multi-fault data | Graceful fallback to JSON-only mode    |
| **Network dependency** | `setup.sh` clones D4J from GitHub          | Can work with existing local D4J clone |

---

## 14. File-by-File Change Map

### New Files

| File                                 | Purpose                                             | Lines (est.) |
| ------------------------------------ | --------------------------------------------------- | ------------ |
| `d4j_odc_pipeline/multifault_cli.py` | `MultiFaultClient` class wrapping `defects4j_multi` | ~250         |
| `tests/test_multifault_cli.py`       | Unit + integration tests for `MultiFaultClient`     | ~150         |

### Modified Files

| File                             | Changes                                                                          | Scope            |
| -------------------------------- | -------------------------------------------------------------------------------- | ---------------- |
| `d4j_odc_pipeline/cli.py`        | Add `mf-info`, `mf-checkout`, `mf-coverage`, `mf-collect` subcommands + dispatch | ~100 lines added |
| `d4j_odc_pipeline/models.py`     | Add `multifault_context` field to `BugContext`                                   | ~10 lines        |
| `d4j_odc_pipeline/prompting.py`  | Add multi-fault-aware prompt section                                             | ~30 lines        |
| `d4j_odc_pipeline/comparison.py` | Enhance evidence asymmetry with actual CLI data                                  | ~20 lines        |
| `.env.example`                   | Add `D4J_MULTI_CMD`, `D4J_MULTI_HOME`                                            | ~5 lines         |
| `AGENTS.md`                      | Document `multifault_cli.py`, new commands, env vars                             | ~60 lines        |
| `README.md`                      | Add D4J-mf CLI setup docs, new command usage                                     | ~80 lines        |

### Unchanged Files

| File                             | Reason                                                           |
| -------------------------------- | ---------------------------------------------------------------- |
| `multifault.py`                  | Stays as-is — the JSON-only API remains the lightweight fallback |
| `pipeline.py`                    | No changes until Phase 4 (prompt integration)                    |
| `defects4j.py`                   | No changes — existing D4J wrapper is independent                 |
| `llm.py`, `odc.py`, `parsing.py` | No changes needed                                                |

---

## Appendix A: defects4j-mf Documentation Assessment

### Is the Documentation Sufficient?

**Yes, with caveats.**

| Aspect             | Quality                   | Notes                                                                                        |
| ------------------ | ------------------------- | -------------------------------------------------------------------------------------------- |
| **README.md**      | Good                      | Clear setup, usage examples, command table                                                   |
| **Paper summary**  | Excellent                 | Full methodology documented in `multi_fault_dataset_paper_summary.md`                        |
| **setup.sh**       | Self-documenting          | Each step is clear and sequential                                                            |
| **Dockerfile**     | Complete                  | Shows exact system requirements                                                              |
| **CLI help**       | Basic                     | `defects4j_multi -h` lists commands; per-command help (`defects4j_multi checkout -h`) exists |
| **Python scripts** | Minimal comments          | `checkout.py`, `backtrack.py` etc. are readable but sparsely documented                      |
| **Patch contents** | Not separately documented | Must read the patch diff to understand what files are added/modified                         |

### What's Missing from Their Docs

1. **No API documentation** for the Python scripts (backtrack.py, checkout.py, etc.)
2. **No versioning strategy** — unclear if future D4J versions will be supported
3. **No Windows/WSL instructions** — assumes Linux only
4. **No CI/CD examples** — no GitHub Actions or similar for automated testing
5. **No performance benchmarks** — no estimate of how long checkout/coverage takes per project

### Our Plan Fills These Gaps

This integration plan documents the WSL-specific requirements, provides the wrapper
architecture, and establishes the testing strategy that defects4j-mf's own docs don't cover.

---

## Appendix B: Quick Reference — The 5 Supported Projects

| Project | Total D4J Bugs | Multi-Fault Versions | Avg Faults/Version | JSON Size                 |
| ------- | -------------- | -------------------- | ------------------ | ------------------------- |
| Chart   | 26             | varies               | varies             | 23 KB + 25 KB backtrack   |
| Closure | 133            | varies               | varies             | 306 KB + 589 KB backtrack |
| Lang    | 65             | varies               | varies             | 65 KB + 118 KB backtrack  |
| Math    | 106            | varies               | varies             | 91 KB + 280 KB backtrack  |
| Time    | 27             | varies               | varies             | 56 KB + 32 KB backtrack   |

Note: Mockito has a `_backtrack.json` but no main `.json` file — it's incomplete.

---

## Appendix C: Command Cheat Sheet

```bash
# === Inside WSL ===

# 1. Setup (one-time)
cd /path/to/defects4j-mf
./setup.sh /path/to/defects4j
export D4J_HOME="/path/to/defects4j"
export PATH="$PATH:$D4J_HOME/framework/bin"

# 2. Info queries
defects4j_multi info -p Lang
defects4j_multi info -p Lang -v 10

# 3. Multi-fault checkout
defects4j_multi checkout -p Math -v 4 -w /tmp/Math-4
ls /tmp/Math-4/bug.locations.*
ls /tmp/Math-4/tests.trigger.*

# 4. Compile
cd /tmp/Math-4
defects4j_multi compile

# 5. Coverage (GZoltar)
defects4j_multi coverage

# 6. Identify faults in spectrum
defects4j_multi identify -p Math -v 4 -c sfl/txt/
cat sfl/txt/spectra.csv | head -20

# === From our pipeline (future) ===
python -m d4j_odc_pipeline mf-info --project Lang --version 10
python -m d4j_odc_pipeline mf-checkout --project Math --version 4 --work-dir .\work\Math_4_mf
python -m d4j_odc_pipeline mf-coverage --work-dir .\work\Math_4_mf --output .\artifacts\Math_4\mf_coverage.json
python -m d4j_odc_pipeline mf-collect --project Math --version 4 --work-dir .\work\Math_4_mf --output .\artifacts\Math_4\mf_context.json
```
