# Defects4J ODC Pipeline

A thesis pipeline that collects pre-fix bug evidence from Defects4J, classifies it into ODC defect types using an LLM (Gemini by default, OpenRouter as fallback), and saves machine-readable outputs for evaluation.

## What the pipeline does

- Checks out a buggy Defects4J version via the official CLI.
- Compiles and tests the buggy version.
- Parses `failing_tests` and stack traces.
- Extracts source snippets around suspicious stack frames.
- Optionally runs targeted `defects4j coverage` on suspicious classes only.
- Builds a structured ODC classification prompt (direct or scientific-debugging style).
- Writes `context.json`, `classification.json`, and a markdown report.

## Setup

### 1. Windows prerequisites

- Python 3.11+
- WSL with Ubuntu
- Keep this repo on Windows; keep the Defects4J clone inside WSL on the Linux filesystem.

### 2. WSL prerequisites

```bash
sudo apt update
sudo apt install -y openjdk-11-jdk git subversion perl cpanminus curl unzip
git config --global core.autocrlf input
```

### 3. Clone and initialize Defects4J inside WSL

```bash
cd ~
git clone https://github.com/rjust/defects4j.git
cd defects4j
sudo cpanm --installdeps .
./init.sh
perl framework/bin/defects4j info -p Lang
```

If `info -p Lang` fails with a missing Perl module such as `String::Interpolate`:

```bash
sudo cpanm String::Interpolate
sudo cpanm --installdeps ~/defects4j
```

### 5. Create a Python virtual environment and install dependencies

```powershell
cd C:\path\to\your\repo\implementation

python -m venv .venv
.venv\Scripts\Activate.ps1          # PowerShell
# or: .venv\Scripts\activate.bat    # CMD

pip install -r requirements.txt
```

Or install as an editable package (adds the `d4j-odc` shortcut command):

```powershell
pip install -e .
```

### 6. Configure `.env`

Copy `.env.example` to `.env` and set your values:

```dotenv
DEFAULT_LLM_PROVIDER=gemini
DEFAULT_LLM_MODEL=gemini-3.1-flash-lite-preview
GEMINI_API_KEY=your_real_key_here
DEFECTS4J_CMD=wsl perl /home/your-linux-user/defects4j/framework/bin/defects4j
DEFECTS4J_PATH_STYLE=wsl
```

## Usage

### `collect` — Build pre-fix context

```powershell
python -m d4j_odc_pipeline collect `
  --project Lang --bug 1 `
  --work-dir .\work\Lang_1b `
  --output .\artifacts\Lang_1\context.json `
  --skip-coverage
```

### `classify` — Classify an existing context

```powershell
python -m d4j_odc_pipeline classify `
  --context .\artifacts\Lang_1\context.json `
  --output .\artifacts\Lang_1\classification.json `
  --report .\artifacts\Lang_1\report.md
```

### `run` — End-to-end collection + classification

```powershell
python -m d4j_odc_pipeline run `
  --project Lang --bug 1 `
  --work-dir .\work\Lang_1b `
  --context-output .\artifacts\Lang_1\context.json `
  --classification-output .\artifacts\Lang_1\classification.json `
  --report .\artifacts\Lang_1\report.md `
  --skip-coverage
```

### `d4j` — Defects4J proxy commands

Convenience wrappers around common Defects4J operations with formatted output:

```powershell
python -m d4j_odc_pipeline d4j pids                         # List all projects
python -m d4j_odc_pipeline d4j bids --project Lang           # List bug IDs
python -m d4j_odc_pipeline d4j info --project Lang --bug 1   # Show bug details
```

## CLI Parameters

### Common parameters (used by `collect`, `run`)

| Parameter          | Required | Description                                           |
| ------------------ | :------: | ----------------------------------------------------- |
| `--project`        |   Yes    | Defects4J project id (`Lang`, `Math`, `Chart`, etc.)  |
| `--bug`            |   Yes    | Numeric bug id. Automatically suffixed to `<bug>b`.   |
| `--work-dir`       |   Yes    | Checkout directory for the buggy revision.            |
| `--defects4j-cmd`  |    No    | Override `DEFECTS4J_CMD` for this run.                |
| `--snippet-radius` |    No    | Source lines around suspicious frames. Default: `12`. |
| `--skip-coverage`  |    No    | Skip the `defects4j coverage` step.                   |

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

### Global flags

| Flag             | Description                                          |
| ---------------- | ---------------------------------------------------- |
| `-q` / `--quiet` | Suppress all rich console output (for scripting/CI). |

## Coverage Mode

Coverage is optional. The main collection always performs metadata lookup, checkout, compile, test, failure parsing, and snippet extraction. The `--skip-coverage` flag only controls the extra `defects4j coverage` step.

- **With `--skip-coverage`**: Faster, simpler. Best for first runs, setup debugging, or fast batch collection. No runtime coverage evidence in `context.json`.
- **Without `--skip-coverage`**: Instruments only suspicious classes, runs coverage with the first failing test, and parses coverage XML. Slower but richer evidence. If no suspicious source frames exist, coverage is skipped automatically.

**Recommendation**: Use `--skip-coverage` until checkout/compile/test/classify are working, then remove it.

## Output Files

| File                     | Produced by        | Contents                                     |
| ------------------------ | ------------------ | -------------------------------------------- |
| `context.json`           | `collect` / `run`  | Pre-fix Defects4J evidence.                  |
| `classification.json`    | `classify` / `run` | ODC classification from the LLM.             |
| `report.md`              | `classify` / `run` | Human-readable bug + classification summary. |
| `prompt.json`            | `--prompt-output`  | Rendered prompt messages sent to the LLM.    |
| `instrument_classes.txt` | Coverage step      | Classes instrumented for coverage.           |

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

## Design Choices

- The LLM sees **pre-fix evidence only** by default.
- `classes.modified` is stored as a hidden oracle for offline analysis but excluded from the prompt.
- The default prompt style is `scientific`, following observation → hypothesis → prediction → experiment → conclusion.
- The ODC target is the 7-class **Defect Type** attribute (`Function`, `Interface`, `Checking`, `Assignment`, `Timing/Serialization`, `Build/Package/Merge`, `Algorithm`).
- Defects4J runs through WSL; Windows paths are converted automatically when `DEFECTS4J_PATH_STYLE=wsl`.

## Official References

- [Defects4J CLI overview](https://defects4j.org/html_doc/defects4j.html)
- [Defects4J docs index](https://defects4j.org/html_doc/index.html)
- [d4j-checkout](https://defects4j.org/html_doc/d4j/d4j-checkout.html) · [d4j-compile](https://defects4j.org/html_doc/d4j/d4j-compile.html) · [d4j-test](https://defects4j.org/html_doc/d4j/d4j-test.html) · [d4j-coverage](https://defects4j.org/html_doc/d4j/d4j-coverage.html)
- [d4j-export](https://defects4j.org/html_doc/d4j/d4j-export.html) · [d4j-query](https://defects4j.org/html_doc/d4j/d4j-query.html) · [d4j-bids](https://defects4j.org/html_doc/d4j/d4j-bids.html) · [d4j-info](https://defects4j.org/html_doc/d4j/d4j-info.html) · [d4j-pids](https://defects4j.org/html_doc/d4j/d4j-pids.html)
