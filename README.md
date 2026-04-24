# Defects4J ODC Pipeline

A research pipeline that collects pre-fix bug evidence from [Defects4J](https://github.com/rjust/defects4j), classifies it into ODC (**Orthogonal Defect Classification**) defect types using an LLM (Gemini by default, OpenRouter as fallback), and saves machine-readable outputs for evaluation.

The pipeline follows a **Scientific Debugging** methodology — observation → hypothesis → prediction → experiment → conclusion — to classify each bug into one of 7 ODC defect types with grounded, code-level reasoning.

For large-scale evaluation, the CLI also supports batch-study commands: `study-plan`, `study-run`, and `study-analyze`.

For multi-fault analysis, the pipeline integrates with [defects4j-mf](https://github.com/DCallaz/defects4j-mf) data via the `multifault` and `multifault-enrich` commands.

---

## Quick Start

```bash
# 1. Setup (see docs/SETUP.md for full instructions)
pip install -r requirements.txt && pip install -e .

# 2. Run a single bug classification (pre-fix)
python -m d4j_odc_pipeline run --project Lang --bug 1 --skip-coverage

# 3. Run a batch study
python -m d4j_odc_pipeline study-plan --target-bugs 68
python -m d4j_odc_pipeline study-run --manifest manifest_68.json --skip-coverage
python -m d4j_odc_pipeline study-analyze --manifest manifest_68.json
```

---

## Documentation

| Document                                         | Contents                                                                                                                                                                             |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [**docs/SETUP.md**](docs/SETUP.md)               | Installation for Windows+WSL and native Linux, Defects4J setup, Python environment, `.env` configuration, provider options                                                           |
| [**docs/USAGE.md**](docs/USAGE.md)               | All CLI commands with examples (`collect`, `classify`, `run`, `compare`, `study-*`, `multifault`, `d4j`), parameter reference tables, coverage/fix-diff modes, output file reference |
| [**docs/ARCHITECTURE.md**](docs/ARCHITECTURE.md) | Pipeline architecture diagrams, Defects4J evidence flow, ODC taxonomy, `classification.json` schema, project structure, design choices                                               |
| [**AGENTS.md**](AGENTS.md)                       | Agent-facing codebase map: module guide, execution flows, artifact contracts, extension patterns                                                                                     |
| [**docs/eval_defence.md**](docs/eval_defence.md) | Scientific defence for pre-fix/post-fix evaluation methodology                                                                                                                       |

---

## CLI Commands at a Glance

| Command                | Purpose                                              |
| ---------------------- | ---------------------------------------------------- |
| `run`                  | End-to-end: collect evidence + classify (single bug) |
| `collect`              | Build `context.json` from Defects4J evidence only    |
| `classify`             | Classify an existing `context.json` via LLM          |
| `compare`              | Compare a pre-fix/post-fix classification pair       |
| `compare-batch`        | Batch-compare directory of paired classifications    |
| `study-plan`           | Generate a balanced bug manifest for batch studies   |
| `study-run`            | Execute paired prefix/postfix runs from a manifest   |
| `study-analyze`        | Cross-artifact analysis over study outputs           |
| `multifault`           | Query multi-fault co-existence data                  |
| `multifault-enrich`    | Enrich classification with multi-fault context       |
| `d4j pids\|bids\|info` | Defects4J proxy commands                             |

Most parameters have **smart defaults** — see [docs/USAGE.md](docs/USAGE.md) for details.

---

## Output Layout

```bash
.dist/
├── runs/                              # Standalone commands (run, collect, classify)
│   ├── Lang_1_prefix/
│   │   ├── context.json
│   │   ├── classification.json
│   │   └── report.md
│   └── Lang_1_postfix/
│       └── ...
└── study/                             # Batch commands (study-plan, study-run, study-analyze)
    ├── manifest_68.json
    ├── summary.json
    ├── analysis_68.json
    ├── analysis_68.md
    └── artifacts_68/
        ├── prefix/
        ├── postfix/
        └── checkpoint.json
```

---

## Project Structure

```bash
d4j_odc_pipeline/
├── cli.py             # CLI surface and command dispatch
├── pipeline.py        # Core orchestration
├── batch.py           # Batch manifest, execution, analysis
├── defects4j.py       # Defects4J wrapper
├── llm.py             # LLM provider abstraction
├── prompting.py       # Prompt engineering
├── odc.py             # ODC taxonomy
├── models.py          # Data models
├── parsing.py         # Stack trace + JSON parsing
├── comparison.py      # Evaluation metrics
├── multifault.py      # Multi-fault data loader
├── web_fetch.py       # Bug report fetcher
└── console.py         # Rich output helpers
```

---

## Official References

- [Defects4J CLI overview](https://defects4j.org/html_doc/defects4j.html)
- [Defects4J docs index](https://defects4j.org/html_doc/index.html)
- [d4j-checkout](https://defects4j.org/html_doc/d4j/d4j-checkout.html) · [d4j-compile](https://defects4j.org/html_doc/d4j/d4j-compile.html) · [d4j-test](https://defects4j.org/html_doc/d4j/d4j-test.html) · [d4j-coverage](https://defects4j.org/html_doc/d4j/d4j-coverage.html)
- [d4j-export](https://defects4j.org/html_doc/d4j/d4j-export.html) · [d4j-query](https://defects4j.org/html_doc/d4j/d4j-query.html) · [d4j-bids](https://defects4j.org/html_doc/d4j/d4j-bids.html) · [d4j-info](https://defects4j.org/html_doc/d4j/d4j-info.html) · [d4j-pids](https://defects4j.org/html_doc/d4j/d4j-pids.html)
