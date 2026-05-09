# Parallel Run Implementation Plan

## 1. Problem Statement

The `study-run` batch command processes bugs **sequentially** — one bug at a time, two evidence modes (prefix + postfix) per bug. For each evidence mode, the pipeline executes:

1. **Collection phase** (slow): D4J checkout → compile → test → parse → export properties → extract code
2. **Classification phase** (fast): Build prompt → LLM API call → parse response → write report

### Current Performance Profile

| Metric                  | Value                                                            |
| ----------------------- | ---------------------------------------------------------------- |
| **Machine**             | AMD Ryzen 5 3600 (6 cores / 12 threads), 32 GB RAM               |
| **GPU**                 | NVIDIA GeForce GT 1030 (2 GB VRAM)                               |
| **OS**                  | Windows 10 Pro, Defects4J runs through WSL                       |
| **Observed throughput** | ~60 runs (30 prefix + 30 postfix) in ~3 hours                    |
| **Per-run average**     | ~3 minutes per collection+classification cycle                   |
| **Bottleneck**          | Collection phase (checkout + compile + test ≈ 90%+ of wall time) |

### Time Breakdown Per Bug (Approximate)

From the user's terminal output for `Lang-29`:

| Step                                 | Time (seconds)         | Category                         |
| ------------------------------------ | ---------------------- | -------------------------------- |
| Query bug metadata                   | ~5s                    | D4J subprocess (WSL)             |
| Fetch bug info                       | ~0.2s                  | D4J subprocess (WSL)             |
| Fetch bug report                     | ~0.9s                  | HTTP (network)                   |
| **Checkout**                         | **~35s**               | **D4J subprocess (WSL) — HEAVY** |
| **Compile**                          | **~27s**               | **D4J subprocess (WSL) — HEAVY** |
| **Run tests**                        | **~31s**               | **D4J subprocess (WSL) — HEAVY** |
| Export properties                    | ~9.5s                  | D4J subprocess (WSL)             |
| Code extraction                      | <1s                    | Local file I/O                   |
| LLM classification                   | ~2-5s                  | HTTP API call                    |
| **Total per evidence mode**          | **~110-120s**          |                                  |
| **Total per bug (prefix + postfix)** | **~220-240s (~4 min)** |                                  |

> **Key insight:** ~85% of wall time is spent in three D4J subprocess calls: `checkout`, `compile`, and `test`. These are CPU-bound Java processes running inside WSL.

---

## 2. Can a GPU (e.g., RTX 5060 Ti) Help?

> [!IMPORTANT]
> **Short answer: No.** A GPU will not speed up the collection phase. Here's why:

### Why GPUs Cannot Help

| Factor                                | Explanation                                                                                                                                                                                                       |
| ------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Java compilation is CPU-bound**     | `javac` performs sequential lexical analysis, AST construction, type checking, and bytecode generation. These are branching-heavy, logic-intensive operations — the exact opposite of what GPUs are designed for. |
| **JUnit test execution is CPU-bound** | Tests run on the JVM, which executes on CPU cores. Tests involve complex object creation, assertion logic, and I/O — none of which can be offloaded to CUDA cores.                                                |
| **Git/SVN checkout is I/O-bound**     | The checkout step copies files from the D4J repository cache to the work directory. This is limited by disk I/O speed, not compute.                                                                               |
| **No CUDA-compatible tooling exists** | Neither `javac`, Maven, Ant, Gradle, nor JUnit have GPU-accelerated variants. There are no CUDA kernels for Java compilation.                                                                                     |

### What GPUs ARE Good For (Not Applicable Here)

- Matrix multiplication (ML training/inference)
- Image/video processing
- Cryptographic hashing at scale
- Physics simulation
- LLM inference (if running models locally — not our case since we use API-based LLMs)

> [!NOTE]
> If you were running a **local LLM** (e.g., `llama.cpp` or `vLLM`) for classification instead of API calls, then a powerful GPU (RTX 4090/5060 Ti) would dramatically speed up the classification phase. But since we use Gemini/Groq/OpenRouter APIs, GPU is irrelevant for our pipeline.

---

## 3. What WILL Help: Viable Strategies

### Strategy Overview

| Strategy                                               | Speedup Potential                    | Complexity      | Risk   |
| ------------------------------------------------------ | ------------------------------------ | --------------- | ------ |
| **A. Parallel collection (ThreadPoolExecutor)**        | 3-5×                                 | Medium          | Low    |
| **B. WSL filesystem optimization**                     | 1.5-2×                               | Low             | None   |
| **C. Docker-native execution**                         | 2-3× (+ eliminates WSL overhead)     | High (one-time) | Medium |
| **D. Two-phase pipeline (collect-all → classify-all)** | 1.2× + better rate-limit utilization | Medium          | Low    |
| **E. Docker + GNU Parallel**                           | 4-8×                                 | High (one-time) | Medium |
| **F. Pre-built checkout cache**                        | 1.5-2× (eliminates checkout time)    | Low             | None   |

---

### Strategy A: Parallel Collection with `ThreadPoolExecutor` (Recommended First Step)

#### Concept

Since each bug's collection is independent (separate work directories, separate D4J subprocess calls), we can run N collections simultaneously using Python's `concurrent.futures.ThreadPoolExecutor`.

`ThreadPoolExecutor` is ideal here because:

- The Python code is just waiting for `subprocess.run()` to finish (I/O-bound from Python's perspective)
- The actual work happens in external OS processes (WSL → Java), so the GIL is irrelevant
- Each thread manages one independent subprocess pipeline

#### Architecture

```
Main Thread (batch.py)
│
├─ ThreadPoolExecutor(max_workers=N)
│   ├─ Worker 1: collect_bug_context(Lang_1, work_dir_1)
│   ├─ Worker 2: collect_bug_context(Math_5, work_dir_2)
│   ├─ Worker 3: collect_bug_context(Chart_8, work_dir_3)
│   └─ ... (up to N concurrent collections)
│
├─ Results Queue (thread-safe)
│   └─ As each collection completes → classify sequentially (rate-limited)
│
└─ Checkpoint Writer (after each complete bug pair)
```

#### Choosing `max_workers`

Your machine: **6 cores / 12 threads, 32 GB RAM**

Each D4J collection spawns Java processes (JVM, javac, JUnit runner) that are CPU-intensive:

- Each JVM instance uses ~1-2 CPU cores during compilation/testing
- Each JVM instance uses ~512 MB - 2 GB RAM (depending on project)
- WSL itself consumes some overhead per subprocess

**Recommended settings:**

| `max_workers` | Expected Behavior                      | RAM Usage (est.) |
| ------------- | -------------------------------------- | ---------------- |
| 2             | Safe, ~2× speedup                      | ~8-12 GB         |
| 3             | Good balance, ~2.5-3× speedup          | ~12-16 GB        |
| 4             | Aggressive, ~3-4× speedup              | ~16-22 GB        |
| 5-6           | Risk of thrashing, diminishing returns | ~20-28 GB        |

> [!WARNING]
> With 32 GB RAM and a 6-core CPU, **`max_workers=3`** is the recommended starting point. Going above 4 risks memory pressure and CPU context-switching overhead that can actually slow things down. Large projects like `Closure` can consume 4+ GB per JVM.

#### Implementation Sketch

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Rate-limit LLM calls to 1 at a time (free tier)
_llm_lock = threading.Lock()

def _collect_single(entry, defects4j, work_root, artifacts_root, ...):
    """Run collection for one bug + one evidence mode. Thread-safe."""
    context = collect_bug_context(
        defects4j=defects4j,
        project_id=entry["project_id"],
        bug_id=entry["bug_id"],
        work_dir=work_root / f"{entry['project_id']}_{entry['bug_id']}b",
        output_path=artifacts_root / "context.json",
        ...
    )
    return context

def run_batch_parallel(entries, max_workers=3, ...):
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        # Submit all collection tasks
        future_to_entry = {}
        for entry in entries:
            future = pool.submit(_collect_single, entry, ...)
            future_to_entry[future] = entry

        # Process results as they complete
        for future in as_completed(future_to_entry):
            entry = future_to_entry[future]
            context = future.result()

            # Classify sequentially (rate-limited)
            with _llm_lock:
                classification = classify_bug_context(context=context, ...)

            # Write checkpoint
            _write_checkpoint(...)
```

#### Key Design Decisions

1. **Collection = parallel, Classification = sequential**: The LLM API has rate limits (free tier). Collecting in parallel fills a queue of ready-to-classify contexts, and a single thread drains that queue respecting rate limits.

2. **Graceful shutdown**: The existing `_shutdown_requested` event still works — check it before submitting new tasks and use `pool.shutdown(wait=True, cancel_futures=True)` on interrupt.

3. **Progress tracking**: Use `rich.Progress` with `as_completed()` to show real-time progress.

4. **Checkpoint safety**: Each completed (collected + classified) bug writes a checkpoint. Partially collected bugs are not checkpointed.

5. **Console output**: With parallel workers, console output from `collect_bug_context` will interleave. Options:
   - Suppress per-bug console output in parallel mode (use progress bar only)
   - Capture output per-worker and display on completion
   - Use `rich.Live` with a table showing all active workers

---

### Strategy B: WSL Filesystem Optimization (Quick Win)

#### The 9P Problem

Your current setup:

```
Windows (Python) → subprocess.run("wsl perl defects4j ...") → WSL → Java
```

When D4J's work directory (`-w`) points to a Windows path (e.g., `C:\WORK\...`), WSL accesses it via the **9P protocol** (`/mnt/c/...`). This protocol has **significant overhead** for the thousands of small file I/O operations that Java compilation involves.

#### Fix: Use WSL-Native Filesystem for Work Directories

```
# SLOW (current): Work dir on Windows filesystem
defects4j checkout -p Lang -v 29b -w /mnt/c/WORK/IUT/Research/implementation/work/Lang_29b

# FAST (optimized): Work dir on WSL-native ext4 filesystem
defects4j checkout -p Lang -v 29b -w /home/hasin/d4j_work/Lang_29b
```

**Implementation:**

- Add a new env var: `D4J_WORK_ROOT_WSL=/home/hasin/d4j_work`
- The pipeline uses this WSL-native path for checkout/compile/test
- After collection, the context JSON (small file) is written back to the Windows filesystem
- The WSL work directory can be cleaned up after each bug

> [!TIP]
> This single change can provide **1.5-2× speedup** on I/O-heavy projects (like Closure) with zero code changes to the pipeline. The ext4 filesystem inside WSL2 is dramatically faster than the 9P bridge.

#### How to Verify the Impact

```bash
# Inside WSL:
# Test write speed on Windows filesystem
dd if=/dev/zero of=/mnt/c/WORK/test_write bs=1M count=100

# Test write speed on WSL-native filesystem
dd if=/dev/zero of=/home/hasin/test_write bs=1M count=100
```

You should see a **3-10× difference** in write throughput.

---

### Strategy C: Docker-Native Execution (Eliminates WSL Overhead Entirely)

#### Concept

Instead of running `Windows Python → WSL → D4J`, run the entire pipeline inside a Docker container with D4J pre-installed.

#### Architecture

```
Windows Host
│
├── Docker Desktop (uses WSL2 backend, but with native Linux kernel)
│   └── Container: d4j-odc-pipeline
│       ├── Python 3.13 + pipeline code (mounted volume)
│       ├── Defects4J (pre-installed, /defects4j)
│       ├── OpenJDK 8 (required by D4J)
│       └── Work directories on ext4 (native, no 9P)
│
└── Shared volume: ./implementation → /app (for code)
    Shared volume: ./.dist → /output (for results)
```

#### Dockerfile

```dockerfile
FROM openjdk:8-jdk-slim

# System dependencies
RUN apt-get update && apt-get install -y \
    git subversion build-essential curl \
    python3 python3-pip python3-venv \
    perl cpanminus \
    && rm -rf /var/lib/apt/lists/*

# Install Defects4J
RUN git clone https://github.com/rjust/defects4j.git /defects4j
WORKDIR /defects4j
RUN cpanm --installdeps . && ./init.sh
ENV PATH="/defects4j/framework/bin:${PATH}"
ENV TZ="America/Los_Angeles"

# Install pipeline
WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY . .

# D4J work directory on native ext4 (fast!)
RUN mkdir -p /d4j_work /output

ENTRYPOINT ["python3", "-m", "d4j_odc_pipeline"]
```

#### docker-compose.yml (Parallel Workers)

```yaml
version: "3.8"

services:
  pipeline:
    build: .
    volumes:
      - ./implementation:/app # Pipeline code
      - ./.dist:/output # Results
      - d4j_work:/d4j_work # Fast ext4 workspace
    environment:
      - DEFECTS4J_CMD=defects4j # Direct, no WSL wrapper
      - DEFECTS4J_PATH_STYLE=native # No path conversion needed
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - GROQ_API_KEY=${GROQ_API_KEY}

volumes:
  d4j_work: # Docker-managed volume (native ext4)
```

#### Benefits

| Benefit                       | Impact                                                           |
| ----------------------------- | ---------------------------------------------------------------- |
| No WSL subprocess overhead    | Eliminates `wsl perl ...` wrapper latency                        |
| No 9P filesystem penalty      | All D4J file I/O on native ext4                                  |
| No path conversion            | Removes `windows_to_wsl_path()` entirely                         |
| Reproducible environment      | Same JDK, same Perl, same D4J version everywhere                 |
| Easy to deploy on any machine | Teammates can `docker compose up` and go                         |
| Combine with Strategy A       | ThreadPoolExecutor inside the container for parallel collections |

#### Trade-offs

| Cost                                                     | Mitigation                                     |
| -------------------------------------------------------- | ---------------------------------------------- |
| One-time Docker image build (~20-30 min for D4J init)    | Build once, reuse forever                      |
| Docker Desktop license (if commercial use)               | Use Podman or Rancher Desktop as alternatives  |
| JDK 8 inside container (some D4J bugs need specific JDK) | Use multi-stage build or install multiple JDKs |
| Larger image size (~2-4 GB with D4J initialized)         | Acceptable for a research tool                 |

---

### Strategy D: Two-Phase Pipeline (Collect-All → Classify-All)

#### Concept

Currently, the batch loop does: `collect(bug) → classify(bug) → next bug`. This means the LLM rate limit pauses between bugs, and collection cannot start for the next bug until classification finishes.

**Proposed:** Split into two phases:

1. **Phase 1 (Collect-All):** Run all collections in parallel (Strategy A), writing `context.json` files. No LLM calls.
2. **Phase 2 (Classify-All):** Iterate over all collected contexts sequentially, calling the LLM for each. This can be rate-limited without blocking collection.

#### Benefits

- Collection is never blocked by LLM rate limits
- If the LLM API is down, you still have all contexts collected
- You can switch LLM providers between phases (e.g., collect with no API key, classify with Groq)
- The `--dry-run` flag already supports this (collect without classifying)

#### Implementation

This is essentially adding a `--collect-only` flag to `study-run` and then using `study-run --context-dir` to classify pre-collected contexts. The existing `classify` command already works on individual contexts — this would be a batch version.

---

### Strategy E: Docker + GNU Parallel (Maximum Throughput)

#### Concept

For maximum throughput on multi-core machines, use GNU Parallel inside the Docker container to run D4J commands at the shell level:

```bash
# Generate collection commands for all manifest entries
python3 -m d4j_odc_pipeline study-generate-jobs \
  --manifest manifest_100.json \
  --output jobs.txt

# Run 4 collections in parallel using GNU Parallel
cat jobs.txt | parallel -j4 --joblog parallel.log
```

This is how the Defects4J maintainers themselves run large-scale experiments.

#### When to Use This

- Processing 200+ bugs
- Running on a dedicated server / CI machine with 16+ cores
- When you need maximum utilization of all CPU cores

---

### Strategy F: Pre-Built Checkout Cache (Eliminates Checkout Time)

#### Concept

The `checkout` step (~35s per bug) clones the repository and checks out the specific version. For a study of 100 bugs, that's **~58 minutes** of checkout time alone (100 bugs × 2 modes × 35s).

If you pre-checkout all bugs once and cache the directories, subsequent runs skip the checkout entirely.

#### Implementation

```bash
# Pre-checkout all bugs in the manifest (one-time)
python -m d4j_odc_pipeline study-checkout \
  --manifest manifest_100.json \
  --cache-dir /d4j_cache

# Run study with cached checkouts (skips checkout step)
python -m d4j_odc_pipeline study-run \
  --manifest manifest_100.json \
  --checkout-cache /d4j_cache
```

Each cached checkout is a pristine copy of the repository at the buggy version. Before compile/test, the pipeline copies (or symlinks) the cached checkout to the work directory.

> [!NOTE]
> This strategy pairs extremely well with Docker (Strategy C) since the cache can live on a Docker volume with fast ext4 I/O.

---

## 4. Recommended Implementation Order

Given your current setup (Windows + WSL, Ryzen 5 3600, 32 GB RAM), here is the recommended order:

### Phase 1: Quick Wins (1-2 hours of work)

1. **Strategy B** — WSL filesystem optimization
   - Change work directory to WSL-native path
   - Expected: **1.5-2× speedup** with almost no code changes

2. **Strategy D** — Add `--collect-only` mode to `study-run`
   - Decouple collection from classification
   - Allows parallel collection without worrying about rate limits

### Phase 2: Parallel Collection (4-6 hours of work)

3. **Strategy A** — `ThreadPoolExecutor` in `batch.py`
   - Add `--parallel N` flag to `study-run`
   - Default: `N=1` (current behavior), recommended: `N=3`
   - Combined with Phase 1: **3-5× total speedup**

### Phase 3: Docker Native (1-day project)

4. **Strategy C** — Dockerize the entire pipeline
   - Eliminates WSL overhead entirely
   - Makes the tool portable and reproducible
   - Combined with Strategy A: **4-6× total speedup**

### Phase 4: Heavy-Duty (Optional)

5. **Strategy E + F** — GNU Parallel + checkout cache
   - Only needed for 200+ bug studies or dedicated research servers

---

## 5. Expected Performance After Optimization

| Scenario                | Current   | After Phase 1 | After Phase 2 | After Phase 3 |
| ----------------------- | --------- | ------------- | ------------- | ------------- |
| **100 bugs (200 runs)** | ~10 hours | ~5-6 hours    | ~2-3 hours    | ~1.5-2 hours  |
| **200 bugs (400 runs)** | ~20 hours | ~10-12 hours  | ~4-6 hours    | ~3-4 hours    |
| **Time per bug pair**   | ~6 min    | ~3-4 min      | ~1.5-2 min    | ~1-1.5 min    |

> [!IMPORTANT]
> These estimates assume average bug complexity. Large projects like **Closure** can take 3-5× longer per bug than small ones like **Lang** or **Time**. The manifest's round-robin selection helps balance the load.

---

## 6. Summary: What Helps and What Doesn't

| Approach                   | Helps?          | Why                                                              |
| -------------------------- | --------------- | ---------------------------------------------------------------- |
| **GPU (any)**              | ❌ No           | Java compilation/testing is CPU-bound, not GPU-parallelizable    |
| **More CPU cores**         | ✅ Yes          | More parallel D4J subprocesses                                   |
| **Faster single-core CPU** | ✅ Yes          | Each compilation/test run finishes faster                        |
| **More RAM**               | ✅ Yes          | Enables more parallel JVM instances                              |
| **NVMe SSD**               | ✅ Somewhat     | Faster checkout/file I/O (diminishing returns if already on SSD) |
| **WSL ext4 filesystem**    | ✅ Yes (1.5-2×) | Eliminates 9P protocol overhead                                  |
| **Docker-native**          | ✅ Yes (2-3×)   | Eliminates WSL subprocess wrapper + 9P overhead                  |
| **ThreadPoolExecutor**     | ✅ Yes (3-5×)   | Parallel collection, sequential classification                   |
| **GNU Parallel**           | ✅ Yes (4-8×)   | Shell-level parallelism, maximum CPU utilization                 |
| **Checkout cache**         | ✅ Yes (1.5-2×) | Eliminates ~35s checkout step per run                            |

---

## 7. References

- [Defects4J GitHub — Parallel Test Scripts](https://github.com/rjust/defects4j/tree/master/framework/test) — The D4J team uses `GNU parallel -j20` for bulk experiments
- [Python `concurrent.futures` Documentation](https://docs.python.org/3/library/concurrent.futures.html) — `ThreadPoolExecutor` API reference
- [WSL2 Filesystem Performance](https://learn.microsoft.com/en-us/windows/wsl/compare-versions) — Microsoft's documentation on 9P overhead vs. native ext4
- [Docker Compose Scaling](https://docs.docker.com/compose/compose-file/deploy/) — `deploy.replicas` for worker scaling
