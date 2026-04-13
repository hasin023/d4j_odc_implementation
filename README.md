# Defects4J ODC Pipeline

This repository contains a runnable thesis pipeline that:

1. Collects pre-fix bug evidence from Defects4J.
2. Builds an ODC defect-type classification prompt using a scientific-debugging structure.
3. Calls Gemini by default, with OpenRouter available as a fallback.
4. Saves machine-readable outputs for later evaluation and annotation.

## What the pipeline does

- Checks out a buggy Defects4J version with the official CLI.
- Compiles and tests the buggy version.
- Parses `failing_tests` and stack traces.
- Extracts source snippets around suspicious stack frames.
- Optionally runs `defects4j coverage` on suspicious classes only.
- Builds a structured ODC classification prompt.
- Writes `context.json`, `classification.json`, and a markdown report.

## Recommended Setup

### 1. Windows prerequisites

- Install Python 3.11+ on Windows.
- Install WSL with Ubuntu.
- Keep this research repo on Windows if you want, but keep the Defects4J clone inside WSL on the Linux filesystem.

### 2. WSL prerequisites

Inside Ubuntu/WSL, run:

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

If `info -p Lang` fails with a missing Perl module such as `String::Interpolate`, rerun:

```bash
sudo cpanm String::Interpolate
sudo cpanm --installdeps ~/defects4j
```

### 4. Configure this repo

Create `.env` from `.env.example` and set:

```dotenv
DEFAULT_LLM_PROVIDER=gemini
DEFAULT_LLM_MODEL=gemini-3.1-flash-lite-preview
GEMINI_API_KEY=your_real_key_here
DEFECTS4J_CMD=wsl perl /home/your-linux-user/defects4j/framework/bin/defects4j
DEFECTS4J_PATH_STYLE=wsl
```

The CLI auto-loads `.env`, so you usually do not need to export variables manually.

## Collect and Classify a Bug

### Step 1. Collect pre-fix context

```powershell
cd C:\path\to\your\repo\implementation

python -m d4j_odc_pipeline collect `
  --project Lang `
  --bug 1 `
  --work-dir .\work\Lang_1b `
  --output .\artifacts\Lang_1\context.json `
  --skip-coverage
```

### Step 2. Classify the collected bug

```powershell
python -m d4j_odc_pipeline classify `
  --context .\artifacts\Lang_1\context.json `
  --output .\artifacts\Lang_1\classification.json `
  --report .\artifacts\Lang_1\report.md
```

By default, the CLI uses:

- provider: `gemini`
- model: `gemini-3.1-flash-lite-preview`

You can override them explicitly:

```powershell
python -m d4j_odc_pipeline classify `
  --context .\artifacts\Lang_1\context.json `
  --output .\artifacts\Lang_1\classification.json `
  --report .\artifacts\Lang_1\report.md `
  --provider gemini `
  --model gemini-3.1-flash-lite-preview
```

### Step 3. Run end-to-end in one command

```powershell
python -m d4j_odc_pipeline run `
  --project Lang `
  --bug 1 `
  --work-dir .\work\Lang_1b `
  --context-output .\artifacts\Lang_1\context.json `
  --classification-output .\artifacts\Lang_1\classification.json `
  --report .\artifacts\Lang_1\report.md `
  --skip-coverage
```

## About `--skip-coverage`

Coverage is optional in this pipeline. The main collection flow always performs metadata lookup, checkout, compile, test, failure parsing, suspicious stack-frame selection, and snippet extraction. The `--skip-coverage` flag only controls the extra `defects4j coverage` step.

| Mode                      | What happens                                                                                                                                                 | When to use it                                                                                                      | Trade-off                                                                                         |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| With `--skip-coverage`    | The pipeline does not call `defects4j coverage`. It collects metadata, failures, suspicious frames, exports, and source snippets only.                       | Best for first-run smoke tests, new machine setup, debugging WSL/Defects4J issues, and fast large-batch collection. | Faster and simpler, but `context.json` will not contain runtime coverage evidence.                |
| Without `--skip-coverage` | After test execution, the pipeline tries to instrument suspicious classes and run `defects4j coverage`, then parses coverage XML into the collected context. | Best when you want richer evidence for classification or later analysis.                                            | Slower, more moving parts, and more dependent on Defects4J coverage generation working correctly. |

Important behavior in this implementation:

- Coverage is targeted, not global. The pipeline instruments only suspicious source classes derived from parsed stack frames.
- If failing tests were parsed, the pipeline runs coverage using the first failing test as the focused test.
- If no suspicious non-test frames are found, coverage is skipped automatically even if you do not pass `--skip-coverage`.
- When coverage runs, the collector writes an `instrument_classes.txt` file next to the output artifact directory to tell Defects4J which classes to instrument.
- If coverage runs but no parseable XML report is produced, collection still completes and adds a note to `context.json`.

Practical recommendation:

- Use `--skip-coverage` for your first run on a new machine.
- Remove `--skip-coverage` once checkout, compile, test, and classification are already working.

## Pipeline CLI Reference

### Top-level command summary

| Command    | Purpose                                                                                            | Typical use                                                                         |
| ---------- | -------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| `collect`  | Build pre-fix bug context from Defects4J and write `context.json`.                                 | Use when you want to inspect or reuse the collected evidence before classification. |
| `classify` | Read an existing `context.json`, build the prompt, call the LLM, and write classification outputs. | Use when you already collected context or want to rerun only the model step.        |
| `run`      | Perform collection and classification in one command.                                              | Use for end-to-end execution once your local setup is stable.                       |

### `collect` parameters

| Parameter          | Required | Description                                                                                                        | When to use                                                                     |
| ------------------ | -------- | ------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------- |
| `--project`        | Yes      | Defects4J project id such as `Lang`, `Math`, or `Chart`.                                                           | Always required for a collection run.                                           |
| `--bug`            | Yes      | Numeric Defects4J bug id such as `1` or `17`. The collector automatically turns it into buggy version id `<bug>b`. | Always required for a collection run.                                           |
| `--work-dir`       | Yes      | Checkout directory for the buggy revision.                                                                         | Use a dedicated directory like `.\work\Lang_1b`.                                |
| `--output`         | Yes      | Path for the produced `context.json`.                                                                              | Use a stable artifact path you can reuse for classification.                    |
| `--defects4j-cmd`  | No       | Overrides `DEFECTS4J_CMD` for this run only.                                                                       | Use if you want a temporary alternate Defects4J installation or command prefix. |
| `--snippet-radius` | No       | Number of source lines to include before and after a suspicious line. Default: `12`.                               | Increase it if your debugging prompt needs more code context.                   |
| `--skip-coverage`  | No       | Disables the coverage collection step.                                                                             | Use for faster, more robust smoke tests or when coverage is failing.            |

Example:

```powershell
python -m d4j_odc_pipeline collect `
  --project Math `
  --bug 17 `
  --work-dir .\work\Math_17b `
  --output .\artifacts\Math_17\context.json `
  --snippet-radius 20 `
  --skip-coverage
```

### `classify` parameters

| Parameter         | Required | Description                                                                                                                             | When to use                                                                                      |
| ----------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| `--context`       | Yes      | Path to an existing `context.json`.                                                                                                     | Always required for classification.                                                              |
| `--output`        | Yes      | Path for the produced `classification.json`.                                                                                            | Always required for classification.                                                              |
| `--report`        | No       | Markdown summary output path.                                                                                                           | Use when you want a quick human-readable summary alongside JSON.                                 |
| `--prompt-output` | No       | Path to save the fully rendered prompt messages as JSON.                                                                                | Useful for debugging prompts, auditing evidence, or thesis appendices.                           |
| `--prompt-style`  | No       | Prompt template style. Choices: `direct`, `scientific`. Default: `scientific`.                                                          | Use `scientific` for your main thesis pipeline; use `direct` for ablations or simpler baselines. |
| `--provider`      | No       | LLM backend. Choices: `gemini`, `openrouter`, `openai-compatible`. Default comes from `DEFAULT_LLM_PROVIDER` or falls back to `gemini`. | Use when you want to override the default backend per run.                                       |
| `--model`         | No       | Model name sent to the selected provider. Default comes from `DEFAULT_LLM_MODEL` or falls back to `gemini-3.1-flash-lite-preview`.      | Use when comparing models or switching providers.                                                |
| `--api-key-env`   | No       | Environment variable name that stores the API key. If omitted, the code uses the provider default.                                      | Use only when your key is stored in a non-standard env var.                                      |
| `--base-url`      | No       | Override API base URL for the provider.                                                                                                 | Use for custom gateways, alternate regions, proxies, or provider-compatible endpoints.           |
| `--dry-run`       | No       | Builds and optionally saves the prompt, but skips the LLM request and does not write classification JSON.                               | Use when validating prompt construction without spending API credits.                            |

Provider-specific API key defaults:

| Provider            | Default key env var  | Default base URL                                   |
| ------------------- | -------------------- | -------------------------------------------------- |
| `gemini`            | `GEMINI_API_KEY`     | `https://generativelanguage.googleapis.com/v1beta` |
| `openrouter`        | `OPENROUTER_API_KEY` | `https://openrouter.ai/api/v1`                     |
| `openai-compatible` | `OPENAI_API_KEY`     | `https://api.openai.com/v1`                        |

Example:

```powershell
python -m d4j_odc_pipeline classify `
  --context .\artifacts\Lang_1\context.json `
  --output .\artifacts\Lang_1\classification.json `
  --report .\artifacts\Lang_1\report.md `
  --prompt-output .\artifacts\Lang_1\prompt.json `
  --provider gemini `
  --model gemini-3.1-flash-lite-preview
```

### `run` parameters

`run` combines `collect` and `classify`, so it accepts the bug-selection parameters from `collect` plus the LLM parameters from `classify`.

| Parameter                 | Required | Description                                                                    | When to use                                                                  |
| ------------------------- | -------- | ------------------------------------------------------------------------------ | ---------------------------------------------------------------------------- |
| `--project`               | Yes      | Defects4J project id.                                                          | Always required.                                                             |
| `--bug`                   | Yes      | Numeric Defects4J bug id.                                                      | Always required.                                                             |
| `--work-dir`              | Yes      | Checkout directory for the buggy revision.                                     | Use a dedicated workspace such as `.\work\Lang_1b`.                          |
| `--context-output`        | Yes      | Path for the intermediate collected context JSON.                              | Always required in end-to-end mode.                                          |
| `--classification-output` | Yes      | Path for the final classification JSON.                                        | Always required in end-to-end mode.                                          |
| `--report`                | Yes      | Path for the markdown report.                                                  | Required in `run` because it is the main human-readable output.              |
| `--defects4j-cmd`         | No       | Overrides `DEFECTS4J_CMD` for this run only.                                   | Use for temporary Defects4J command changes.                                 |
| `--prompt-output`         | No       | Saves the final rendered prompt messages.                                      | Useful for debugging and experiment logging.                                 |
| `--snippet-radius`        | No       | Number of source lines around suspicious frames. Default: `12`.                | Increase if your prompt needs wider code context.                            |
| `--skip-coverage`         | No       | Skip the coverage collection step.                                             | Recommended for the first successful end-to-end smoke test.                  |
| `--prompt-style`          | No       | Prompt template style. Choices: `direct`, `scientific`. Default: `scientific`. | Use `scientific` for your main thesis workflow.                              |
| `--provider`              | No       | LLM provider. Choices: `gemini`, `openrouter`, `openai-compatible`.            | Use when overriding the repo default.                                        |
| `--model`                 | No       | Model name for the selected provider.                                          | Use for model comparisons and experiments.                                   |
| `--api-key-env`           | No       | Custom env var name for the API key.                                           | Use only when your key is not stored in the provider default variable.       |
| `--base-url`              | No       | Override API base URL.                                                         | Use for custom provider-compatible endpoints.                                |
| `--dry-run`               | No       | Perform collection and prompt generation, but skip the LLM request.            | Useful when you want a full collection plus prompt audit without model cost. |

Example:

```powershell
python -m d4j_odc_pipeline run `
  --project Lang `
  --bug 1 `
  --work-dir .\work\Lang_1b `
  --context-output .\artifacts\Lang_1\context.json `
  --classification-output .\artifacts\Lang_1\classification.json `
  --report .\artifacts\Lang_1\report.md `
  --prompt-output .\artifacts\Lang_1\prompt.json `
  --skip-coverage
```

## Defects4J CLI Reference

Your pipeline calls Defects4J through the official CLI. Since your working installation is inside WSL, the safest pattern is:

```bash
perl ~/defects4j/framework/bin/defects4j <command> [args]
```

If you want, you can create a shell alias in WSL:

```bash
alias defects4j='perl ~/defects4j/framework/bin/defects4j'
```

Then you can use `defects4j <command>` directly in examples.

### Main command list

| Command        | What it does                                                      | Key parameters                                      | Typical use                                                                       |
| -------------- | ----------------------------------------------------------------- | --------------------------------------------------- | --------------------------------------------------------------------------------- |
| `pids`         | Lists all available project ids.                                  | None                                                | Discover valid project names such as `Lang`, `Math`, `Chart`, or `Closure`.       |
| `bids`         | Lists bug ids for a specific project.                             | `-p`, optionally `-D` or `-A`                       | Find valid bug numbers before calling the pipeline.                               |
| `info`         | Shows project information, optionally for a single bug.           | `-p`, optionally `-b`                               | Inspect a project or specific bug before collection.                              |
| `query`        | Returns project metadata in CSV form.                             | `-p`, optionally `-q`, `-H`, `-D`, `-A`, `-o`       | Best for scripting, bug metadata retrieval, and building automation.              |
| `checkout`     | Checks out a buggy or fixed version into a working directory.     | `-p`, `-v`, `-w`                                    | Required before compile/test/coverage on a bug.                                   |
| `compile`      | Compiles the checked-out version.                                 | `-w`                                                | Verify buildability or reproduce compile errors.                                  |
| `test`         | Runs tests on a checked-out version.                              | `-w`, optionally `-r`, `-t`, `-s`                   | Reproduce failing tests or run targeted tests.                                    |
| `coverage`     | Measures code coverage on a checked-out version.                  | `-w`, optionally `-r`, `-t`, `-s`, `-i`             | Collect execution evidence for suspicious classes.                                |
| `mutation`     | Runs mutation analysis.                                           | `-w`, optionally `-r`, `-t`, `-s`, `-i`, `-e`, `-m` | Use for deeper test-adequacy experiments, not needed for the core pipeline.       |
| `export`       | Exports one version-specific property from a checked-out version. | `-p`, optionally `-o`, `-w`                         | Inspect source dirs, classpaths, triggering tests, and related checkout metadata. |
| `env`          | Prints environment information.                                   | None                                                | Use when debugging the WSL Defects4J installation.                                |
| `monitor.test` | Monitors class loading for a single test.                         | Single-test focused command; see the main CLI docs. | Advanced analysis when you need loaded source/test class information.             |

### Commonly used Defects4J commands and parameters

| Command    | Parameters                     | Meaning                                                         | Example                                                                                            |
| ---------- | ------------------------------ | --------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| `pids`     | None                           | Print all project IDs.                                          | `perl ~/defects4j/framework/bin/defects4j pids`                                                    |
| `bids`     | `-p <project_id>`              | Print active bug ids for one project.                           | `perl ~/defects4j/framework/bin/defects4j bids -p Lang`                                            |
| `bids`     | `-D`                           | Print only deprecated bug ids.                                  | `perl ~/defects4j/framework/bin/defects4j bids -p Lang -D`                                         |
| `bids`     | `-A`                           | Print active and deprecated bug ids together.                   | `perl ~/defects4j/framework/bin/defects4j bids -p Lang -A`                                         |
| `info`     | `-p <project_id>`              | Print project-level info.                                       | `perl ~/defects4j/framework/bin/defects4j info -p Lang`                                            |
| `info`     | `-b <bug_id>`                  | Add details for one specific bug.                               | `perl ~/defects4j/framework/bin/defects4j info -p Lang -b 1`                                       |
| `query`    | `-p <project_id>`              | Query metadata for one project.                                 | `perl ~/defects4j/framework/bin/defects4j query -p Lang`                                           |
| `query`    | `-H`                           | List all available metadata fields.                             | `perl ~/defects4j/framework/bin/defects4j query -p Lang -H`                                        |
| `query`    | `-q "<field1,field2,...>"`     | Return selected metadata columns as CSV.                        | `perl ~/defects4j/framework/bin/defects4j query -p Lang -q "bug.id,report.url,classes.modified"`   |
| `query`    | `-o <output_file>`             | Save CSV query output to a file.                                | `perl ~/defects4j/framework/bin/defects4j query -p Lang -q "bug.id,report.url" -o lang.csv`        |
| `query`    | `-D`                           | Query deprecated bugs only.                                     | `perl ~/defects4j/framework/bin/defects4j query -p Lang -q "bug.id" -D`                            |
| `query`    | `-A`                           | Query both active and deprecated bugs.                          | `perl ~/defects4j/framework/bin/defects4j query -p Lang -q "bug.id,deprecated.reason" -A`          |
| `checkout` | `-p <project_id>`              | Select the project.                                             | `perl ~/defects4j/framework/bin/defects4j checkout -p Lang -v 1b -w ~/tmp/Lang_1b`                 |
| `checkout` | `-v <version_id>`              | Select the version, for example `1b` or `1f`.                   | `perl ~/defects4j/framework/bin/defects4j checkout -p Lang -v 1f -w ~/tmp/Lang_1f`                 |
| `checkout` | `-w <work_dir>`                | Target working directory.                                       | `perl ~/defects4j/framework/bin/defects4j checkout -p Math -v 17b -w ~/tmp/Math_17b`               |
| `compile`  | `-w <work_dir>`                | Compile a checked-out project.                                  | `perl ~/defects4j/framework/bin/defects4j compile -w ~/tmp/Lang_1b`                                |
| `test`     | `-w <work_dir>`                | Run tests in a checked-out project.                             | `perl ~/defects4j/framework/bin/defects4j test -w ~/tmp/Lang_1b`                                   |
| `test`     | `-r`                           | Run only relevant developer-written tests.                      | `perl ~/defects4j/framework/bin/defects4j test -w ~/tmp/Lang_1b -r`                                |
| `test`     | `-t <class>::<method>`         | Run one test method only.                                       | `perl ~/defects4j/framework/bin/defects4j test -w ~/tmp/Lang_1b -t org.example.Test::testCase`     |
| `test`     | `-s <suite.tar.bz2>`           | Run an external archived test suite.                            | `perl ~/defects4j/framework/bin/defects4j test -w ~/tmp/Lang_1b -s Lang-11f-randoop.1.tar.bz2`     |
| `coverage` | `-w <work_dir>`                | Run coverage in a checked-out project.                          | `perl ~/defects4j/framework/bin/defects4j coverage -w ~/tmp/Lang_1b`                               |
| `coverage` | `-r`                           | Use relevant developer-written tests only.                      | `perl ~/defects4j/framework/bin/defects4j coverage -w ~/tmp/Lang_1b -r`                            |
| `coverage` | `-t <class>::<method>`         | Run coverage for one test method only.                          | `perl ~/defects4j/framework/bin/defects4j coverage -w ~/tmp/Lang_1b -t org.example.Test::testCase` |
| `coverage` | `-s <suite.tar.bz2>`           | Run coverage for an external test suite.                        | `perl ~/defects4j/framework/bin/defects4j coverage -w ~/tmp/Lang_1b -s Lang-11f-randoop.1.tar.bz2` |
| `coverage` | `-i <instrument_classes_file>` | Restrict instrumentation to classes listed in a file.           | `perl ~/defects4j/framework/bin/defects4j coverage -w ~/tmp/Lang_1b -i instrument_classes.txt`     |
| `export`   | `-p <property_name>`           | Export one version-specific property.                           | `perl ~/defects4j/framework/bin/defects4j export -p dir.src.classes -w ~/tmp/Lang_1b`              |
| `export`   | `-o <output_file>`             | Save the exported property to a file.                           | `perl ~/defects4j/framework/bin/defects4j export -p tests.trigger -w ~/tmp/Lang_1b -o trigger.txt` |
| `export`   | `-w <work_dir>`                | Read properties from the checked-out version in that directory. | `perl ~/defects4j/framework/bin/defects4j export -p cp.test -w ~/tmp/Lang_1b`                      |
| `mutation` | `-w <work_dir>`                | Run mutation analysis in a checked-out project.                 | `perl ~/defects4j/framework/bin/defects4j mutation -w ~/tmp/Lang_1b`                               |
| `mutation` | `-i <instrument_classes_file>` | Mutate only selected classes.                                   | `perl ~/defects4j/framework/bin/defects4j mutation -w ~/tmp/Lang_1b -i instrument_classes.txt`     |
| `mutation` | `-e <exclude_file>`            | Exclude listed mutant ids.                                      | `perl ~/defects4j/framework/bin/defects4j mutation -w ~/tmp/Lang_1b -e excluded.txt`               |
| `mutation` | `-m <mutation_operators_file>` | Limit mutation operators.                                       | `perl ~/defects4j/framework/bin/defects4j mutation -w ~/tmp/Lang_1b -m operators.txt`              |
| `env`      | None                           | Print environment/debug info for this Defects4J install.        | `perl ~/defects4j/framework/bin/defects4j env`                                                     |

### Defects4J properties and metadata fields most relevant to this pipeline

The pipeline uses both `query` and `export`.

`query` is used before checkout to retrieve bug metadata. The current code prefers these fields when they are available:

| Field              | Why it matters                                                                                           |
| ------------------ | -------------------------------------------------------------------------------------------------------- |
| `bug.id`           | Identifies the bug row to extract from the CSV output.                                                   |
| `report.id`        | Useful for linking to issue tracker records.                                                             |
| `report.url`       | Useful as bug-report context and traceability.                                                           |
| `classes.modified` | Stored as a hidden oracle for offline evaluation, but intentionally excluded from the prompt by default. |
| `classes.relevant` | Helpful bug-level context if present in the project metadata.                                            |
| `tests.trigger`    | Helps identify triggering developer tests.                                                               |
| `tests.relevant`   | Helps identify the bug-relevant developer-written test set.                                              |

`export` is used after checkout to inspect the checked-out version. The collector currently exports these properties:

| Property          | Why it matters                                                |
| ----------------- | ------------------------------------------------------------- |
| `dir.src.classes` | Helps locate production source files for snippet extraction.  |
| `dir.bin.classes` | Useful for checked-out build layout inspection.               |
| `dir.src.tests`   | Helps resolve test-source directories.                        |
| `dir.bin.tests`   | Useful for checked-out test build layout inspection.          |
| `cp.compile`      | Compile classpath for the checked-out version.                |
| `cp.test`         | Test classpath for the checked-out version.                   |
| `tests.trigger`   | Triggering tests known to Defects4J for that checked-out bug. |
| `tests.relevant`  | Relevant developer-written tests for that checked-out bug.    |

## Choosing Bugs

List projects in WSL:

```bash
perl ~/defects4j/framework/bin/defects4j pids
```

List active bug IDs for a project:

```bash
perl ~/defects4j/framework/bin/defects4j bids -p Math
```

Inspect one bug before collecting it:

```bash
perl ~/defects4j/framework/bin/defects4j info -p Math -b 17
perl ~/defects4j/framework/bin/defects4j query -p Math -q "bug.id,report.url,classes.modified"
```

Then use those values in the pipeline:

```powershell
python -m d4j_odc_pipeline collect `
  --project Math `
  --bug 17 `
  --work-dir .\work\Math_17b `
  --output .\artifacts\Math_17\context.json
```

## Output Files

| File                     | Produced by                                | Contents                                                            |
| ------------------------ | ------------------------------------------ | ------------------------------------------------------------------- |
| `context.json`           | `collect` or `run`                         | Collected Defects4J evidence before LLM classification.             |
| `classification.json`    | `classify` or `run`                        | Structured ODC classification output from the model.                |
| `report.md`              | `classify` with `--report`, or `run`       | Human-readable summary of the bug and classification.               |
| `prompt.json`            | `classify` or `run` with `--prompt-output` | The exact rendered prompt messages sent to the LLM layer.           |
| `instrument_classes.txt` | `collect` or `run` when coverage executes  | The class list used to restrict Defects4J coverage instrumentation. |

## Provider Options

### Gemini default

- Provider name: `gemini`
- Default model: `gemini-3.1-flash-lite-preview`
- Env var: `GEMINI_API_KEY`

### OpenRouter fallback

If you want to use OpenRouter instead:

```dotenv
DEFAULT_LLM_PROVIDER=openrouter
DEFAULT_LLM_MODEL=openai/gpt-5.2
OPENROUTER_API_KEY=your_real_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_HTTP_REFERER=https://your-site.example
OPENROUTER_APP_TITLE=Defects4J ODC Pipeline
```

Or pass it per command:

```powershell
python -m d4j_odc_pipeline classify `
  --context .\artifacts\Lang_1\context.json `
  --output .\artifacts\Lang_1\classification.json `
  --report .\artifacts\Lang_1\report.md `
  --provider openrouter `
  --model openai/gpt-5.2
```

## Design Choices

- The LLM sees pre-fix evidence only by default.
- `classes.modified` is stored as a hidden oracle for offline analysis, but excluded from the prompt.
- The default prompt style is `scientific`, following observation, hypothesis, prediction, experiment, and conclusion.
- The ODC target is the 7-class `Defect Type` attribute.
- Defects4J is executed through WSL and Windows paths are converted automatically when `DEFECTS4J_PATH_STYLE=wsl`.

## Official References

- Defects4J CLI overview: [defects4j](https://defects4j.org/html_doc/defects4j.html)
- Defects4J docs index: [Defects4J Documentation](https://defects4j.org/html_doc/index.html)
- Defects4J checkout: [d4j-checkout](https://defects4j.org/html_doc/d4j/d4j-checkout.html)
- Defects4J compile: [d4j-compile](https://defects4j.org/html_doc/d4j/d4j-compile.html)
- Defects4J test: [d4j-test](https://defects4j.org/html_doc/d4j/d4j-test.html)
- Defects4J coverage: [d4j-coverage](https://defects4j.org/html_doc/d4j/d4j-coverage.html)
- Defects4J export: [d4j-export](https://defects4j.org/html_doc/d4j/d4j-export.html)
- Defects4J query: [d4j-query](https://defects4j.org/html_doc/d4j/d4j-query.html)
- Defects4J bids: [d4j-bids](https://defects4j.org/html_doc/d4j/d4j-bids.html)
- Defects4J info: [d4j-info](https://defects4j.org/html_doc/d4j/d4j-info.html)
- Defects4J pids: [d4j-pids](https://defects4j.org/html_doc/d4j/d4j-pids.html)
- Defects4J env: [d4j-env](https://defects4j.org/html_doc/d4j/d4j-env.html)
- Defects4J mutation: [d4j-mutation](https://defects4j.org/html_doc/d4j/d4j-mutation.html)
