# Claw-Code → D4J ODC Pipeline: Improvement Plan

> **Reference codebase**: `c:\WORK\IUT\Research\claw-code`
> **Target codebase**: `c:\WORK\IUT\Research\implementation`
> **Date**: 2026-04-14

---

## Executive Summary

After deep analysis of the claw-code architecture (9 Rust crates, Python port layer, 75+ ROADMAP items, and its design philosophy), this document identifies **16 concrete improvements** adoptable by our D4J ODC pipeline. Each item is classified by priority, effort, and alignment with our system.

Items are grouped into 5 categories:

1. **Error Handling & Resilience** — Structured failures, retry, recovery
2. **Structured Output & Observability** — Machine-readable state, event logging
3. **LLM Client Architecture** — Provider routing, token tracking, response validation
4. **Pipeline Architecture** — Modular design, session management, batch orchestration
5. **CLI & Developer Experience** — Output formats, diagnostics, configuration

---

## Feature Comparison Table

| #   | Claw-Code Pattern                                                    | Our Current State                             | Adoptable? | Priority | Effort |
| --- | -------------------------------------------------------------------- | --------------------------------------------- | ---------- | -------- | ------ |
| 1   | **Failure taxonomy** (`WorkerFailureKind` enum)                      | Bare exception types, no classification       | ✅ Yes     | P0       | Medium |
| 2   | **Structured result types** (every operation returns a typed result) | Mixed: some dataclasses, some raw dicts       | ✅ Yes     | P0       | Medium |
| 3   | **Provider routing** (model-prefix dispatch, multi-provider)         | Hardcoded provider branches in `llm.py`       | ✅ Yes     | P1       | Medium |
| 4   | **Cost/usage tracking** (`CostTracker`, `UsageSummary`)              | None — no token/cost tracking                 | ✅ Yes     | P1       | Low    |
| 5   | **Session persistence** (`SessionStore`, JSONL transcript)           | None — no run history                         | ✅ Yes     | P2       | Medium |
| 6   | **Structured JSON output mode** (`--output-format json`)             | Rich-only console, `--quiet` flag             | ✅ Yes     | P1       | Medium |
| 7   | **Event/history log** (`HistoryLog`, `LaneEvent` schema)             | Console prints only, no structured log        | ✅ Yes     | P1       | Low    |
| 8   | **Recovery recipes** (auto-retry with strategy per failure type)     | Basic retry in `_urlopen_json` only           | ✅ Yes     | P1       | Medium |
| 9   | **Context window preflight** (size estimation before API call)       | None — sends full payload blind               | ✅ Yes     | P0       | Low    |
| 10  | **Structured task packets** (`TaskPacket` with scope, objective)     | Implicit in function args                     | ⚠️ Partial | P2       | Medium |
| 11  | **Permission/safety enforcement** (`PermissionEnforcer`)             | N/A — pipeline doesn't execute arbitrary code | ❌ No      | —        | —      |
| 12  | **MCP/Plugin lifecycle**                                             | N/A — no plugin system needed                 | ❌ No      | —        | —      |
| 13  | **Worker state machine** (`WorkerStatus` lifecycle)                  | N/A — single-threaded pipeline                | ❌ No      | —        | —      |
| 14  | **Branch/worktree management**                                       | N/A — git not central to pipeline             | ❌ No      | —        | —      |
| 15  | **Batch pipeline run manifest** (structured batch tracking)          | Basic `compare-batch` CLI                     | ✅ Yes     | P1       | Medium |
| 16  | **Doctor/preflight diagnostics** (`claw doctor`)                     | None — fails at runtime                       | ✅ Yes     | P1       | Low    |

**Legend**: P0 = Critical (do first), P1 = High (do soon), P2 = Nice-to-have

---

## Detailed Improvement Proposals

---

### 1. Failure Taxonomy & Error Classification

**Claw-code pattern**: `WorkerFailureKind` enum with variants like `TrustGate`, `PromptDelivery`, `Protocol`, `Provider`. Each failure type has a structured recovery recipe. ROADMAP items #8, #5 show the full taxonomy: `prompt_delivery`, `trust_gate`, `branch_divergence`, `compile`, `test`, `infra`, etc.

**Our current state**: We have `LLMError(RuntimeError)` and `Defects4JError(RuntimeError)` — two flat exception classes with no sub-classification. When a failure occurs, the CLI catches broad exception types and shows a generic panel.

**Proposed changes**:

#### [NEW] `d4j_odc_pipeline/errors.py`

```python
from enum import Enum
from dataclasses import dataclass

class FailureKind(Enum):
    """Typed failure classes for pipeline operations."""
    LLM_AUTH        = "llm_auth"           # Missing/invalid API key
    LLM_RATE_LIMIT  = "llm_rate_limit"     # 429 / quota exceeded
    LLM_PROVIDER    = "llm_provider"       # 500/502/503 from provider
    LLM_RESPONSE    = "llm_response"       # Unparseable/invalid response
    LLM_CONTEXT     = "llm_context"        # Prompt exceeds context window
    D4J_NOT_FOUND   = "d4j_not_found"      # Defects4J binary not on PATH
    D4J_CHECKOUT    = "d4j_checkout"       # Checkout failed
    D4J_COMPILE     = "d4j_compile"        # Compilation failed
    D4J_TEST        = "d4j_test"           # Test execution failed
    D4J_TIMEOUT     = "d4j_timeout"        # Subprocess timeout
    NETWORK         = "network"            # HTTP/connection errors
    FILE_IO         = "file_io"            # Read/write failures
    VALIDATION      = "validation"         # Data validation failures

@dataclass(frozen=True)
class PipelineFailure:
    kind: FailureKind
    message: str
    recoverable: bool
    hint: str | None = None
    detail: str | None = None
```

**Why**: This directly mirrors claw-code's `FailureScenario::from_worker_failure_kind()` bridge. With typed failures, the CLI can show targeted hints, the batch runner can decide whether to retry, and structured JSON output can include machine-readable failure classes.

---

### 2. Structured Result Types for All Operations

**Claw-code pattern**: Every operation returns a typed result — `TurnResult`, `WebFetchResult`, `BashCommandOutput`, `WorkerReadySnapshot`. Nothing returns raw strings or raises on expected conditions.

**Our current state**: `collect_bug_context` returns `BugContext`, `classify_bug_context` returns `ClassificationResult | None`. But web_fetch already follows this pattern (thanks to our earlier work). However, `defects4j.py` commands raise on non-zero exit codes rather than returning structured results.

**Proposed changes**:

#### [MODIFY] `d4j_odc_pipeline/pipeline.py`

Add a `PipelineRunResult` dataclass wrapping the full pipeline outcome:

```python
@dataclass
class PipelineRunResult:
    context: BugContext
    classification: ClassificationResult | None
    events: list[PipelineEvent]       # See item #7
    usage: UsageRecord | None         # See item #4
    duration_ms: int
    failure: PipelineFailure | None   # See item #1
    output_paths: dict[str, str]      # {"context": "...", "classification": "..."}
```

**Why**: The batch runner and any future automation needs a single object to inspect — not just the classification, but _how_ the run went (timing, token usage, failures, events).

---

### 3. Provider Routing via Model-Name Prefix

**Claw-code pattern**: `detect_provider_kind()` uses model-name prefixes (`openai/`, `gpt-`, `grok`, `qwen/`) to route to the correct API client. Prefix wins over env-var presence. This was a major pain point they solved (ROADMAP #29, #30, #61).

**Our current state**: `LLMClient.from_env()` takes an explicit `provider` string. The user must manually specify `--provider gemini` or `--provider openrouter`. There is no auto-detection from the model name.

**Proposed changes**:

#### [MODIFY] `d4j_odc_pipeline/llm.py`

```python
def detect_provider(model: str, explicit_provider: str | None = None) -> str:
    """Auto-detect provider from model name prefix, falling back to explicit."""
    if explicit_provider:
        return explicit_provider.strip().lower()
    model_lower = model.strip().lower()
    if model_lower.startswith("gemini") or model_lower.startswith("models/gemini"):
        return "gemini"
    if model_lower.startswith("openai/") or model_lower.startswith("gpt-"):
        return "openai-compatible"
    if model_lower.startswith("claude"):
        return "anthropic"
    if model_lower.startswith("deepseek"):
        return "openai-compatible"
    # Check env vars as fallback
    if os.environ.get("GEMINI_API_KEY"):
        return "gemini"
    if os.environ.get("OPENROUTER_API_KEY"):
        return "openrouter"
    return "openai-compatible"
```

**Why**: Directly from claw-code's lesson — ROADMAP #29 shows users hitting `missing Anthropic credentials` when they had `OPENAI_API_KEY` set because the router didn't check model prefixes. Our pipeline users will benefit from the same convenience.

---

### 4. Token/Cost Usage Tracking

**Claw-code pattern**: `UsageSummary` tracks `input_tokens` and `output_tokens` per turn. `CostTracker` records events with unit costs. The query engine accumulates totals across turns.

**Our current state**: Zero tracking. We call the LLM and discard everything except the response text.

**Proposed changes**:

#### [NEW] `d4j_odc_pipeline/usage.py`

```python
@dataclass
class UsageRecord:
    provider: str
    model: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    prompt_chars: int = 0
    response_chars: int = 0
    estimated_cost_usd: float | None = None
    duration_ms: int = 0
```

#### [MODIFY] `d4j_odc_pipeline/llm.py`

Parse token usage from the API response:

- OpenAI-compatible: `data["usage"]["prompt_tokens"]`, `data["usage"]["completion_tokens"]`
- Gemini: `data["usageMetadata"]["promptTokenCount"]`, `data["usageMetadata"]["candidatesTokenCount"]`

Return `(response_text, UsageRecord)` tuple from `complete()`.

**Why**: Essential for research — knowing how many tokens each classification uses helps optimize prompts, estimate batch costs, and compare provider efficiency.

---

### 5. Session Persistence / Run History

**Claw-code pattern**: `SessionStore` saves/loads session state to `.port_sessions/`. Sessions carry `session_id`, messages, token counts. Can resume from a saved session.

**Our current state**: Each run is fire-and-forget. No way to see "what did I run 3 days ago?" or resume a failed batch.

**Proposed changes**:

#### [NEW] `d4j_odc_pipeline/run_log.py`

```python
@dataclass
class RunLogEntry:
    run_id: str                  # UUID
    timestamp: str               # ISO 8601
    command: str                 # "collect" | "classify" | "run"
    project_id: str
    bug_id: int
    provider: str | None
    model: str | None
    status: str                  # "success" | "failed" | "partial"
    failure_kind: str | None     # From FailureKind enum
    duration_ms: int
    usage: dict | None           # Token usage
    output_paths: dict[str, str] # Files written
```

Store as JSONL in `.d4j_pipeline/run_history.jsonl`. Add a `history` CLI subcommand to list/search past runs.

**Why**: Research pipelines need reproducibility. This mirrors claw-code's `SessionStore` philosophy — every run is a first-class record, not just console output that disappears.

---

### 6. Structured JSON Output Mode (`--output-format json`)

**Claw-code pattern**: Every CLI command supports `--output-format json` emitting structured payloads. ROADMAP items #42, #49, #56, #57 show how they systematically ensured all paths — including error paths — emit JSON when requested.

**Our current state**: `--quiet` suppresses Rich output, but there's no machine-readable output mode. Errors go to stderr as prose.

**Proposed changes**:

#### [MODIFY] `d4j_odc_pipeline/cli.py`

Add `--output-format` flag (`text` | `json`). When `json`:

- All console output is suppressed
- On success, emit `{"status": "success", "result": {...}}` to stdout
- On failure, emit `{"status": "error", "kind": "...", "message": "...", "hint": "..."}` to stderr
- Batch results emit streaming JSONL (one object per bug)

**Why**: Essential for CI/CD integration, programmatic consumption, and future batch orchestration. Claw-code learned this the hard way across 6+ ROADMAP items.

---

### 7. Structured Event/Pipeline Log

**Claw-code pattern**: `HistoryLog` records typed `HistoryEvent(title, detail)` entries. The Rust layer has `LaneEvent` with variants `Started`, `Blocked`, `Failed`, `Finished` — each carrying structured metadata.

**Our current state**: `console.py` prints to Rich console — no structured event trail. After a run, we can't programmatically inspect what happened.

**Proposed changes**:

#### [NEW] `d4j_odc_pipeline/events.py`

```python
from enum import Enum
from dataclasses import dataclass, field

class EventKind(Enum):
    PHASE_START   = "phase_start"
    PHASE_DONE    = "phase_done"
    STEP          = "step"
    WARNING       = "warning"
    ERROR         = "error"
    LLM_CALL      = "llm_call"
    FETCH         = "fetch"
    D4J_COMMAND   = "d4j_command"

@dataclass
class PipelineEvent:
    kind: EventKind
    message: str
    timestamp: str
    detail: str | None = None
    duration_ms: int | None = None

@dataclass
class EventLog:
    events: list[PipelineEvent] = field(default_factory=list)

    def record(self, kind: EventKind, message: str, **kwargs) -> None: ...
    def to_json(self) -> list[dict]: ...
    def summary(self) -> str: ...
```

Thread the `EventLog` through `collect_bug_context` and `classify_bug_context`. Console output becomes a _rendering_ of events (like claw-code's principle: "Events over scraped prose").

**Why**: Separates event generation from event rendering. The same events can drive Rich console, JSON output, run history, and future dashboards.

---

### 8. Recovery Recipes per Failure Type

**Claw-code pattern**: ROADMAP #8 encodes known automatic recoveries: trust prompt → auto-resolve, stale branch → rebase, compile failure → retry after merge. Each recovery is itself emitted as a structured event.

**Our current state**: `_urlopen_json` has basic retry with exponential backoff for HTTP errors. Coverage has a single retry (without instrument file). No other recovery logic.

**Proposed changes**:

```python
RECOVERY_RECIPES: dict[FailureKind, RecoveryAction] = {
    FailureKind.LLM_RATE_LIMIT: RecoveryAction(
        strategy="exponential_backoff",
        max_retries=5,
        escalation="abort with cost warning",
    ),
    FailureKind.LLM_RESPONSE: RecoveryAction(
        strategy="retry_with_modified_prompt",
        max_retries=2,
        modification="append 'Return ONLY valid JSON, no markdown.'",
    ),
    FailureKind.LLM_CONTEXT: RecoveryAction(
        strategy="reduce_context",
        steps=["drop coverage", "reduce snippets to 3", "drop test snippets"],
    ),
    FailureKind.D4J_COMPILE: RecoveryAction(
        strategy="retry_once",
        max_retries=1,
        escalation="skip to classification with partial context",
    ),
}
```

**Why**: The pipeline should be resilient enough to run unattended over 100+ bugs. Each failure type has a known best-effort recovery before giving up.

---

### 9. Context Window Preflight Check

**Claw-code pattern**: ROADMAP #18 — "provider request sizing now emits `context_window_blocked` before oversized requests leave the process." They added a model-context registry to check sizes upfront.

**Our current state**: We build the prompt, send it, and hope it fits. If the prompt exceeds the model's context window, we get an opaque error from the API.

**Proposed changes**:

#### [MODIFY] `d4j_odc_pipeline/prompting.py` or new `d4j_odc_pipeline/preflight.py`

```python
MODEL_CONTEXT_LIMITS: dict[str, int] = {
    "gemini-2.5-flash": 1_000_000,
    "gemini-2.5-pro": 1_000_000,
    "gpt-4o": 128_000,
    "gpt-4o-mini": 128_000,
    "deepseek-chat": 64_000,
    # ... etc
}

def estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 chars per token for English/code."""
    return len(text) // 4

def preflight_check(messages: list[dict], model: str) -> PreflightResult:
    total_chars = sum(len(m["content"]) for m in messages)
    estimated_tokens = estimate_tokens(json.dumps(messages))
    limit = MODEL_CONTEXT_LIMITS.get(model)
    if limit and estimated_tokens > int(limit * 0.9):
        return PreflightResult(ok=False, estimated_tokens=estimated_tokens,
                               limit=limit, suggestion="reduce snippets or coverage")
    return PreflightResult(ok=True, estimated_tokens=estimated_tokens, limit=limit)
```

**Why**: Failing before the API call saves time, money, and gives actionable feedback. Especially important in batch mode.

---

### 10. Doctor/Preflight Diagnostics Command

**Claw-code pattern**: `claw doctor` runs a structured health check: binary availability, env vars, config validation, workspace state. Outputs both text and JSON.

**Our current state**: If something is misconfigured (missing env var, wrong D4J path), the user discovers it mid-pipeline run.

**Proposed changes**:

#### [MODIFY] `d4j_odc_pipeline/cli.py` — add `doctor` subcommand

```python
def _cmd_doctor(args) -> int:
    checks = [
        ("Defects4J binary", _check_d4j_available),
        ("LLM API key", _check_api_key),
        ("Work directory writable", _check_work_dir),
        ("Python version", _check_python_version),
        ("WSL availability (Windows)", _check_wsl),
        (".env file", _check_dotenv),
    ]
    # Run each check, report pass/fail/warn with structured output
```

**Why**: Claw-code's ROADMAP #5 emphasizes this: "Surface doctor/preflight diagnostics in onboarding docs and help." A `doctor` command prevents 90% of first-run failures.

---

### 11. Batch Pipeline Run Manifest

**Claw-code pattern**: `TaskPacket` carries objective, scope, acceptance tests, commit policy, escalation policy. Lane events track per-task state.

**Our current state**: `compare-batch` discovers file pairs by convention. No structured manifest for batch runs.

**Proposed changes**:

#### [NEW] `d4j_odc_pipeline/batch.py`

```python
@dataclass
class BatchManifest:
    bugs: list[BugSpec]           # [{project: "Lang", bug_id: 1}, ...]
    provider: str
    model: str
    prompt_style: str
    output_dir: Path
    concurrency: int = 1         # Future: parallel execution
    retry_policy: str = "auto"   # "none" | "auto" | "aggressive"

@dataclass
class BatchRunState:
    manifest: BatchManifest
    started_at: str
    completed: list[str]          # "Lang-1", "Lang-2"
    failed: dict[str, str]        # "Lang-3" -> "LLM_RATE_LIMIT"
    pending: list[str]

    def save(self, path: Path) -> None: ...

    @classmethod
    def load(cls, path: Path) -> "BatchRunState": ...
```

Add CLI command: `batch-run --manifest manifest.json` with resume support.

**Why**: Running 100+ bugs needs structured tracking: what succeeded, what failed, what to retry. Claw-code's lane board is the scaled version of this exact need.

---

### 12. Prompt Context Reduction Strategy

**Claw-code pattern**: `compress_summary_text()` in the Rust `summary_compression` module. The `compact_after_turns` config auto-trims old context. The recovery recipe for context overflow is "reduce context."

**Our current state**: We include everything: 8 production snippets, 3 test snippets, 6 coverage items, full bug report text. No strategy for when this is too much.

**Proposed changes**:

#### [MODIFY] `d4j_odc_pipeline/prompting.py`

Add tiered context reduction:

```python
def build_messages_with_budget(context, prompt_style, max_tokens=None):
    """Build messages with automatic context reduction if over budget."""
    messages = build_messages(context, prompt_style)
    if max_tokens and estimate_tokens(messages) > max_tokens * 0.85:
        # Tier 1: Reduce coverage to 3 classes
        # Tier 2: Reduce snippets to 4
        # Tier 3: Drop test snippets
        # Tier 4: Truncate bug report to 2000 chars
        # Tier 5: Drop bug report entirely
        messages = _reduce_context(context, prompt_style, max_tokens)
    return messages
```

**Why**: Some Defects4J bugs produce enormous stack traces or source files. Graceful degradation > hard failure.

---

### 13. LLM Response Validation with Retry

**Claw-code pattern**: `structured_retry_limit` in `QueryEngineConfig` — if structured output fails to render, retry with a simpler payload up to N times. ROADMAP #38 shows "dead-session" recovery where compaction is detected and the tool surface is probed.

**Our current state**: `extract_json_object()` tries multiple parsing strategies (raw, code blocks, brace-find) but if all fail, we crash. No retry with prompt modification.

**Proposed changes**:

#### [MODIFY] `d4j_odc_pipeline/pipeline.py` — in `classify_bug_context`

```python
MAX_CLASSIFICATION_RETRIES = 2

for attempt in range(MAX_CLASSIFICATION_RETRIES + 1):
    raw_response = client.complete(messages)
    try:
        payload = extract_json_object(raw_response)
        result = _validate_classification_payload(payload, ...)
        break
    except ValueError as exc:
        if attempt < MAX_CLASSIFICATION_RETRIES:
            events.record(EventKind.WARNING,
                f"LLM response parse failed (attempt {attempt+1}), retrying with repair prompt")
            messages.append({"role": "assistant", "content": raw_response})
            messages.append({"role": "user", "content": REPAIR_PROMPT})
        else:
            raise
```

Where `REPAIR_PROMPT` = "Your previous response was not valid JSON. Please return ONLY the JSON object with no markdown formatting or extra text."

**Why**: LLMs occasionally wrap JSON in markdown or add preamble. A single retry with a repair prompt recovers most of these silently.

---

### 14. Structured Web Fetch Diagnostics

**Claw-code pattern**: `WebFetchResult` carries `source_type`, `status_code`, `duration_ms`, `content_length`, `error`. MCP degraded-startup reporting (#10) provides per-source failure details.

**Our current state**: Already implemented via `web_fetch.py` (our earlier work). ✅ **Done.**

---

### 15. Auth Error Hint System

**Claw-code pattern**: ROADMAP #28 — when Anthropic auth fails but `OPENAI_API_KEY` is in the environment, the error message says "I see OPENAI_API_KEY set; if you meant to use that provider, prefix your model name with openai/". When a bearer token starts with `sk-ant-*`, the error says "Move it to ANTHROPIC_API_KEY."

**Our current state**: `LLMError("Missing API key in environment variable OPENAI_API_KEY.")` — no hint about alternative env vars or common misconfigurations.

**Proposed changes**:

#### [MODIFY] `d4j_odc_pipeline/llm.py`

```python
def _auth_error_with_hints(provider: str, expected_env: str) -> str:
    msg = f"Missing API key: {expected_env} is not set."
    # Check for common misconfiguration
    alt_keys = {
        "GEMINI_API_KEY": "gemini",
        "OPENROUTER_API_KEY": "openrouter",
        "OPENAI_API_KEY": "openai-compatible",
    }
    found = [k for k, v in alt_keys.items() if os.environ.get(k) and v != provider]
    if found:
        msg += f"\n  Hint: Found {', '.join(found)} in environment. "
        msg += "Did you mean to use a different --provider?"
    return msg
```

**Why**: Directly from claw-code's user pain — ROADMAP #28 documents real users confused by auth. Our pipeline users will hit the same issue.

---

### 16. Configuration File Support

**Claw-code pattern**: `ConfigLoader` reads settings from multiple sources (CLI flags → env vars → config files → defaults). `settings.json` or `.claw/settings.json` provides persistent config.

**Our current state**: CLI flags + `.env` file + env vars. No persistent config file for pipeline preferences.

**Proposed changes**:

#### [NEW] Support `.d4j_pipeline.toml` or `d4j_pipeline.json`

```toml
[llm]
provider = "gemini"
model = "gemini-2.5-flash"
temperature = 0.0

[pipeline]
snippet_radius = 12
skip_coverage = false
prompt_style = "scientific"

[batch]
retry_policy = "auto"
max_retries = 2
```

The CLI already reads `.env` for secrets. A config file handles non-secret preferences.

**Why**: Avoids repeating `--provider gemini --model gemini-2.5-flash --prompt-style scientific` on every invocation.

---

## Implementation Priority Roadmap

### Phase 1 — Foundation (Do First)

| Item | Description              | Files                               | Est. LOC |
| ---- | ------------------------ | ----------------------------------- | -------- |
| #1   | Failure taxonomy         | `errors.py` (new)                   | ~60      |
| #9   | Context window preflight | `preflight.py` (new)                | ~50      |
| #4   | Token/cost tracking      | `usage.py` (new), `llm.py` (modify) | ~80      |
| #10  | Doctor command           | `cli.py` (modify)                   | ~80      |

### Phase 2 — Observability (Do Soon)

| Item | Description         | Files                                     | Est. LOC |
| ---- | ------------------- | ----------------------------------------- | -------- |
| #7   | Event/pipeline log  | `events.py` (new), `pipeline.py` (modify) | ~100     |
| #6   | JSON output mode    | `cli.py` (modify)                         | ~100     |
| #15  | Auth error hints    | `llm.py` (modify)                         | ~30      |
| #2   | Pipeline run result | `pipeline.py` (modify)                    | ~40      |

### Phase 3 — Resilience (Improves Batch Reliability)

| Item | Description           | Files                                       | Est. LOC |
| ---- | --------------------- | ------------------------------------------- | -------- |
| #8   | Recovery recipes      | `recovery.py` (new), `pipeline.py` (modify) | ~120     |
| #13  | LLM response retry    | `pipeline.py` (modify)                      | ~40      |
| #12  | Context reduction     | `prompting.py` (modify)                     | ~60      |
| #3   | Provider auto-routing | `llm.py` (modify)                           | ~50      |

### Phase 4 — Scale (Enables Large Batches)

| Item | Description               | Files                                 | Est. LOC |
| ---- | ------------------------- | ------------------------------------- | -------- |
| #11  | Batch manifest + resume   | `batch.py` (new), `cli.py` (modify)   | ~200     |
| #5   | Run history / session log | `run_log.py` (new), `cli.py` (modify) | ~100     |
| #16  | Config file support       | `config.py` (new), `cli.py` (modify)  | ~80      |

---

## Patterns We Explicitly Do NOT Adopt

| Claw-Code Pattern                   | Why Not                                          |
| ----------------------------------- | ------------------------------------------------ |
| Multi-agent coordination (OmO, OmX) | Our pipeline is single-agent, single-LLM-call    |
| Worker state machine                | Single-threaded pipeline, no background workers  |
| MCP/Plugin lifecycle                | No extensibility layer needed                    |
| Git worktree management             | Not a coding agent                               |
| Lane event schema                   | Too heavyweight; our simpler `EventLog` suffices |
| Discord notification routing        | No external notification surface                 |
| Trust prompt resolution             | No interactive permission model                  |
| Prompt delivery verification        | We control the prompt directly                   |

---

## Key Design Principles Adopted from Claw-Code

1. **"Events over scraped prose"** — Separate event generation from rendering. Console output should be derived from typed events, not be the primary record.

2. **"Every operation returns a typed result, never raises on expected conditions"** — Errors are values, not exceptions. Expected failures (missing coverage, unparseable response) are data, not crashes.

3. **"Recovery before escalation"** — Known failure modes should auto-heal once before asking for help. One retry attempt per known failure type.

4. **"State machine first"** — Pipeline phases should have explicit states. Each phase transitions cleanly with structured handoffs.

5. **"Terminal is transport, not truth"** — The Rich console is a rendering layer. The source of truth is the event log and structured results.

6. **"Model-name prefix wins over env-var presence"** — Provider routing should be deterministic from the model name, not dependent on which env vars happen to be set.
