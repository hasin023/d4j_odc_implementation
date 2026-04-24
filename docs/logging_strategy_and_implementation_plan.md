# Logging Strategy and Implementation Plan

## Purpose

This document proposes a logging design for the Defects4J ODC pipeline that fits the current thesis goals and the next-stage product direction:

- reliable large-scale execution over all 800+ Defects4J bugs
- reproducible thesis artifacts and defensible methodology
- future multi-model, multi-run, and human-review studies
- eventual evolution into an interactive CLI tool with first-class UX

The goal is **not** to duplicate `context.json`, `classification.json`, or `report.md`.
The goal is to add a fourth artifact that captures **how** a run happened.

---

## What The Current Code Already Gives Us

The current codebase already has most of the raw signals we need, but they are scattered and mostly ephemeral:

- [`d4j_odc_pipeline/pipeline.py`](../d4j_odc_pipeline/pipeline.py) measures many steps with `spinner_step(...)` and `timed_step(...)`, but those timings are only printed to the console.
- [`d4j_odc_pipeline/defects4j.py`](../d4j_odc_pipeline/defects4j.py) already returns a structured `CommandResult` with `args`, `cwd`, `returncode`, `stdout`, and `stderr`.
- [`d4j_odc_pipeline/web_fetch.py`](../d4j_odc_pipeline/web_fetch.py) already returns a structured `WebFetchResult` with `status_code`, `source_type`, `duration_ms`, `content_length`, and `error`.
- [`d4j_odc_pipeline/llm.py`](../d4j_odc_pipeline/llm.py) already implements retry/backoff logic, but it does not persist request attempts, provider status, response IDs, or usage data.
- [`d4j_odc_pipeline/batch.py`](../d4j_odc_pipeline/batch.py) already persists coarse batch status and checkpoint state, but not per-phase timing or detailed failure causes.
- [`docs/to_improve_the_system.md`](./to_improve_the_system.md) already identified the need for a structured event/pipeline log, token tracking, session persistence, and better failure typing.

This means the logging feature should be implemented as a **structured persistence layer**, not as a brand-new telemetry subsystem from scratch.

---

## Recommendation In One Sentence

Add an append-only, structured, JSONL-style `run.log` file to every bug artifact directory, plus a `study.log` file at the batch root, and treat logs as a **versioned event stream** for observability, provenance, and future CLI UX.

---

## Why This Log Should Exist

Your log file should serve four roles at the same time.

### 1. Operational observability

It should answer:

- Which step failed?
- How long did each step take?
- Was the failure caused by Defects4J, web fetch, prompt size, provider outage, invalid JSON, or a local filesystem problem?
- Which retries happened and why?

### 2. Research provenance and reproducibility

It should answer:

- Which exact code version, model, provider, prompt style, environment, and evidence mode produced this classification?
- Which artifacts were created, with what hashes and sizes?
- Can we prove that a later rerun is the same experiment or a changed experiment?

### 3. Batch-scale analytics

It should answer:

- Which projects are slowest to collect?
- How often does bug-report fetch fail by project?
- How often is coverage empty?
- How often do different models or prompt styles require human review?
- What is the cost and latency profile for scaling to all Defects4J bugs?

### 4. Future interactive CLI/session history

It should eventually answer:

- What command did the user run?
- Was the run interactive or scripted?
- Which step was cancelled, retried, resumed, or confirmed by the user?
- How do we reconstruct a session timeline later?

---

## Recommended File Strategy

### Per-bug file

For every bug artifact directory, create:

- `run.log`

Examples:

- `.dist/runs/Lang_1_prefix/run.log`
- `.dist/runs/Lang_1_postfix/run.log`
- `.dist/study/artifacts_68/prefix/Lang_1_prefix/run.log`

### Batch-root file

For `study-run`, also create:

- `.dist/study/artifacts_<N>/study.log`

This captures manifest loading, checkpoint resume, interrupt handling, per-entry progress, and batch summary events that do not belong to one bug only.

### Append behavior

`run.log` should be **append-only**, not overwrite-only.

That matters because:

- `collect` may run today and `classify` may run tomorrow in the same directory
- reruns should remain auditable
- later analysis can compare multiple attempts for the same bug/mode

Each invocation should therefore get a fresh `run_id`, but reuse the same `run.log`.

---

## Recommended Format

Use a `.log` extension, but store the file as **structured JSON Lines**.

That means:

- one JSON object per line
- stable field names and types
- safe incremental append during long runs
- easy ingestion into Python, pandas, DuckDB, jq, or future dashboards

This is much better than plain text because your next step is not just “read one log by hand”; it is “query logs across 864+ bugs”.

### Why JSONL instead of prose logs

- It is human-tail-able enough.
- It is machine-parseable.
- It survives partial writes better than one giant JSON object.
- It supports event-stream thinking: `run_started`, `phase_finished`, `artifact_written`, `run_finished`.

---

## Recommended Default Policy

The default log should be **metadata-rich but content-light**.

By default, the log should store:

- identifiers
- timestamps
- durations
- statuses
- counts
- hashes
- sanitized command metadata
- retry and failure metadata
- artifact references

By default, the log should **not** duplicate:

- full prompt text
- full raw LLM response
- full Java source snippets
- full bug report body
- full subprocess stdout/stderr

Those already belong in existing artifacts such as `context.json`, `classification.json`, and optional `prompt.json`.

The log should point to those artifacts and store hashes/sizes instead.

---

## What To Log

## Common fields on every event

Every event line should contain at least:

| Field                                | Why                                                 |
| ------------------------------------ | --------------------------------------------------- |
| `schema_version`                     | version the log schema for forward compatibility    |
| `ts`                                 | event timestamp in UTC ISO 8601                     |
| `seq`                                | monotonic sequence number within the invocation     |
| `level`                              | `DEBUG`, `INFO`, `WARN`, `ERROR`                    |
| `event`                              | stable event name                                   |
| `run_id`                             | unique ID for this invocation                       |
| `session_id`                         | reserved for future interactive CLI sessions        |
| `command`                            | `collect`, `classify`, `run`, `study-run`, etc.     |
| `project_id`, `bug_id`, `version_id` | core run identity                                   |
| `evidence_mode`                      | `prefix` / `postfix` or `pre-fix` / `post-fix`      |
| `phase`                              | `collect`, `classify`, `report`, `batch`, etc.      |
| `status`                             | `started`, `ok`, `failed`, `skipped`, `interrupted` |
| `message`                            | short human-readable summary                        |
| `data`                               | structured event-specific payload                   |

## Run envelope

At run start, record:

- `run_id`
- `parent_run_id` for batch child runs
- `batch_id` for `study-run`
- CLI command and sanitized args
- provider, model, prompt style
- package version
- git commit if available
- git dirty flag if available
- Python version
- OS/platform
- hostname
- `DEFECTS4J_CMD`
- `DEFECTS4J_PATH_STYLE`
- working directory

## Collection-phase events

Record:

- metadata query start/end
- queried fields and returned field count
- bug info fetch result
- bug report fetch result with `source_type`, `status_code`, `duration_ms`, `content_length`
- Defects4J subprocess results for `checkout`, `compile`, `test`, `export`, `coverage`
- failure parsing result count
- suspicious frame count
- source directory count
- production snippet count
- test snippet count
- hidden oracle stored yes/no
- coverage outcome:
  - attempted?
  - targeted classes count
  - retry without filter yes/no
  - parsed classes count
- fix diff outcome:
  - requested?
  - collected?
  - char length

## Classification-phase events

Record:

- prompt build start/end and duration
- prompt hash
- prompt size summary:
  - total chars
  - estimated tokens
  - production snippet count included
  - test snippet count included
  - coverage entries included
  - fix diff included yes/no
- LLM request attempts:
  - provider
  - model
  - base URL host only
  - request parameters that matter (`temperature`, `max_tokens` when applicable)
  - retry count
  - HTTP status or network error type
- LLM result summary:
  - response ID if available
  - finish reason if available
  - input/output/total tokens if available
  - latency
- parse/validation result:
  - JSON extraction success/failure
  - invalid `odc_type` yes/no
  - canonical family overwrite performed
- classification summary:
  - `odc_type`
  - `family`
  - `confidence`
  - `needs_human_review`
  - alternative type count

## Artifact events

For every written artifact, record:

- path
- file size
- SHA-256 digest
- write timestamp

At minimum:

- `context.json`
- `classification.json`
- `report.md`
- `prompt.json` when enabled
- `instrument_classes.txt` when enabled
- `run.log` header/finalization

## Batch/study events

Record:

- manifest path and manifest hash
- total entries
- checkpoint path
- checkpoint resume count
- per-entry index and bug key
- skip-existing events
- interrupt events
- comparison inline result summary when both sides exist
- batch totals at finish

## Future interactive CLI events

Reserve fields now even if v1 does not fully use them:

- `session_id`
- `interaction_id`
- `ui_mode` (`interactive`, `noninteractive`)
- `user_action` (`confirm`, `cancel`, `retry`, `resume`)
- `conversation_id`
- `tool_name`
- `parent_event_id`

These fields will let a future Claude-Code-style interface reuse the same log model without a second redesign.

---

## What Not To Log By Default

Do **not** log the following by default:

- API keys
- auth headers
- access tokens
- `.env` contents
- full prompt text
- full raw LLM output
- full Java code snippets
- full bug report bodies
- full subprocess stdout/stderr
- `classes.modified` hidden oracle value

Default replacements:

- store hashes of prompt/response content
- store content length
- store paths to existing artifacts
- on failure, keep only a truncated stderr tail plus full-length/hash metadata

This keeps logs useful without turning them into a second copy of all artifacts.

---

## Logging Levels And Content Modes

Use two dimensions, not one.

### Event level

- `INFO` for normal lifecycle
- `WARN` for recoverable problems or degraded evidence
- `ERROR` for failed phases
- `DEBUG` for very detailed internals

### Content capture mode

- `default`
  - metadata, timings, counts, hashes, truncated failure tails
- `debug`
  - more subprocess detail, more retry detail, prompt sizing detail
- `content`
  - opt-in capture of prompt/response excerpts or full content references

This is safer than making “verbose logging” mean “log everything”.

---

## Recommended Event Names

Use stable, low-cardinality event names such as:

- `run_started`
- `phase_started`
- `phase_finished`
- `subprocess_started`
- `subprocess_finished`
- `fetch_finished`
- `prompt_built`
- `llm_request_attempt`
- `llm_request_finished`
- `llm_retry_scheduled`
- `classification_validated`
- `artifact_written`
- `checkpoint_written`
- `comparison_computed`
- `run_finished`

For failures, use a separate `error.type` classification such as:

- `d4j_not_found`
- `d4j_checkout_failed`
- `d4j_compile_failed`
- `d4j_test_failed`
- `d4j_coverage_failed`
- `web_fetch_failed`
- `llm_auth`
- `llm_rate_limit`
- `llm_provider_http`
- `llm_network`
- `llm_parse_failed`
- `llm_invalid_odc_type`
- `artifact_write_failed`
- `interrupted`

---

## Example `run.log` Records

```json
{"schema_version":1,"ts":"2026-04-24T12:00:00Z","seq":1,"level":"INFO","event":"run_started","run_id":"6a1d4c78-2d9f-4d0a-9b9e-4e7b4b1d2e91","command":"run","project_id":"Lang","bug_id":1,"version_id":"1b","evidence_mode":"prefix","phase":"run","status":"started","message":"Run started","data":{"provider":"gemini","model":"gemini-3.1-flash-lite-preview","prompt_style":"scientific","service_version":"0.2.0"}}
{"schema_version":1,"ts":"2026-04-24T12:00:42Z","seq":8,"level":"INFO","event":"subprocess_finished","run_id":"6a1d4c78-2d9f-4d0a-9b9e-4e7b4b1d2e91","command":"run","project_id":"Lang","bug_id":1,"version_id":"1b","evidence_mode":"prefix","phase":"collect","status":"ok","message":"defects4j test finished","data":{"subcommand":"test","returncode":1,"duration_ms":18321,"stdout_bytes":912,"stderr_bytes":0,"failure_count":1}}
{"schema_version":1,"ts":"2026-04-24T12:00:51Z","seq":15,"level":"INFO","event":"llm_request_finished","run_id":"6a1d4c78-2d9f-4d0a-9b9e-4e7b4b1d2e91","command":"run","project_id":"Lang","bug_id":1,"version_id":"1b","evidence_mode":"prefix","phase":"classify","status":"ok","message":"LLM response received","data":{"provider":"gemini","model":"gemini-3.1-flash-lite-preview","duration_ms":6210,"input_tokens":8412,"output_tokens":683,"response_id":"candidate-1","finish_reasons":["stop"]}}
{"schema_version":1,"ts":"2026-04-24T12:00:52Z","seq":18,"level":"INFO","event":"artifact_written","run_id":"6a1d4c78-2d9f-4d0a-9b9e-4e7b4b1d2e91","command":"run","project_id":"Lang","bug_id":1,"version_id":"1b","evidence_mode":"prefix","phase":"report","status":"ok","message":"classification.json written","data":{"path":".dist/runs/Lang_1_prefix/classification.json","bytes":5823,"sha256":"..."}}
{"schema_version":1,"ts":"2026-04-24T12:00:52Z","seq":19,"level":"INFO","event":"run_finished","run_id":"6a1d4c78-2d9f-4d0a-9b9e-4e7b4b1d2e91","command":"run","project_id":"Lang","bug_id":1,"version_id":"1b","evidence_mode":"prefix","phase":"run","status":"ok","message":"Run complete","data":{"duration_ms":52114,"odc_type":"Checking","needs_human_review":false}}
```

---

## Research Questions These Logs Will Unlock

Once present across all bugs, these logs will let you answer questions that the current 3 artifacts cannot answer cleanly:

- Which evidence source is missing most often by project?
- Does missing bug-report content reduce confidence?
- What is the average latency contribution of checkout vs test vs coverage vs LLM?
- Which provider/model is cheapest per successful classification?
- Which bugs repeatedly fail because of infrastructure rather than methodology?
- Which prompt changes increased token cost without improving confidence?
- Which projects most often trigger post-fix divergence?
- Which runs were produced before vs after a taxonomy or prompt change?

That makes the log a thesis asset, not just an engineering convenience.

---

## Recommended Implementation Plan

## Phase 1: Safe v1 logging foundation

Goal: add logs without re-architecting the whole app.

Create a new module, preferably `d4j_odc_pipeline/events.py` or `d4j_odc_pipeline/logging_utils.py`, containing:

- `LogEvent` dataclass
- `RunLogger` class
- `NullRunLogger`
- helpers for:
  - UTC timestamps
  - JSONL append
  - SHA-256 hashing
  - path normalization
  - redaction/sanitization

Important design choice:

- keep `console.py` as-is in v1
- emit logs **alongside** current console calls
- do not convert console rendering into an event bus yet

This keeps risk low.

## Phase 2: Instrument the core pipeline

Modify:

- `cli.py`
  - create the logger at command entry
  - derive default `run.log` path from artifact directory
  - append for separate `collect` and `classify`
- `pipeline.py`
  - emit phase start/end, counts, artifact writes, final summary
- `defects4j.py`
  - add `duration_ms` to `CommandResult`, or log around `run(...)`
  - log sanitized command args, exit codes, truncated tails
- `web_fetch.py`
  - no schema redesign needed; log the existing `WebFetchResult`
- `batch.py`
  - create one per-bug logger and one batch-root logger
  - log checkpoint resume/write and signal interrupts

## Phase 3: Improve LLM telemetry

Refactor `llm.py` to return a structured response object instead of raw text only.

Recommended new type:

```python
@dataclass
class LLMResponse:
    text: str
    response_id: str | None = None
    finish_reasons: list[str] = field(default_factory=list)
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    duration_ms: int | None = None
    provider_status: int | None = None
```

This is the single most important internal refactor for making logs genuinely useful at scale.

## Phase 4: Add content-capture controls

Add CLI flags such as:

- `--log-level info|debug`
- `--log-content none|hash|excerpt`
- `--log-file <path>` for overrides

Default should remain safe and compact.

## Phase 5: Add log query UX

After v1 is stable, add user-facing commands such as:

- `d4j-odc logs tail --run-dir ...`
- `d4j-odc logs summarize --study-root ...`
- `d4j-odc logs failures --study-root ...`

This matters for the future interactive CLI direction.

---

## File-By-File Change Map

### New files

- `d4j_odc_pipeline/events.py` or `d4j_odc_pipeline/logging_utils.py`
- `tests/test_logging.py`

### Modified files

- `d4j_odc_pipeline/cli.py`
- `d4j_odc_pipeline/pipeline.py`
- `d4j_odc_pipeline/defects4j.py`
- `d4j_odc_pipeline/llm.py`
- `d4j_odc_pipeline/batch.py`
- optionally `d4j_odc_pipeline/web_fetch.py`
- `README.md`
- `docs/USAGE.md`
- `docs/ARCHITECTURE.md`
- `AGENTS.md`

### Prefer not to change in v1

- `models.py`

Reason:

- you do not need to change `context.json` or `classification.json` schemas just to add `run.log`
- avoid unnecessary backward-compatibility churn in the first logging rollout

Optional phase-2 enhancement:

- add `run_id` fields to persisted artifacts later if you want explicit cross-links

---

## Test Plan

Add unit tests that verify:

- `run.log` is created in default artifact directories
- separate `collect` and `classify` append to the same `run.log`
- failed runs still emit `run_finished` with `status="failed"`
- interruption emits `interrupted` status and persists partial data
- sanitized command logging never includes secrets
- success cases log hashes and sizes for artifacts
- retry paths in `llm.py` emit attempt events
- checkpoint resume emits batch events correctly

Do **not** make logging tests depend on live network access.

---

## Acceptance Criteria

The feature is ready when:

- every bug artifact directory contains `run.log`
- `run.log` remains useful in `--quiet` mode
- logs are structured and schema-stable
- logs can be aggregated across all bugs without regex scraping
- no secrets or hidden oracles are leaked by default
- per-phase timings are persisted, not just printed
- LLM retries and provider failures are visible after the run
- batch root has a `study.log`

---

## Recommended Scope Decision

For the first implementation, I recommend:

- **yes** to per-bug `run.log`
- **yes** to batch-root `study.log`
- **yes** to JSONL structured logs
- **yes** to artifact hashes and per-phase timings
- **yes** to LLM usage/latency fields when available
- **no** to full prompt/response logging by default
- **no** to artifact schema changes in v1
- **no** to a full console/event-bus rewrite in v1

That gives you a strong, thesis-grade logging layer quickly, while keeping implementation risk contained.

---

## External Standards That Informed This Proposal

- OpenTelemetry recommends **structured logs with a stable schema** and explicit log/trace correlation.
- OpenTelemetry GenAI conventions recommend logging model/provider/request settings, token usage, duration, response IDs, and evaluation results.
- OpenTelemetry GenAI guidance also recommends **not recording full prompts/outputs by default** and using external references when content is large or sensitive.
- OpenTelemetry CLI conventions recommend capturing process exit codes and sanitized command arguments.
- MLflow’s run model shows the value of treating executions as first-class objects with parameters, metrics, start/end times, and artifacts.
- MLflow dataset tracking shows the usefulness of artifact digests, source lineage, schema, and profile metadata.
- OWASP logging guidance supports recording “when, where, who, what” and explicitly warns against logging secrets, source code, or unsafe identifiers without sanitization.
- W3C PROV-O and Workflow Run RO-Crate show a good provenance model: **activity** (run), **agent** (who/what executed it), **instrument** (tool/model), **object** (inputs), and **result** (artifacts).

These standards are not being adopted wholesale, but they strongly support the design above.
