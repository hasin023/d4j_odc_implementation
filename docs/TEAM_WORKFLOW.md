# Team Workflow — who runs what, where it lands, how it moves

> **Read this before running anything as a team.** It covers the three roles, the exact commands
> each one runs, where files go, how work moves between machines, and how to tell current files
> from dead ones.
>
> This file does not repeat what other docs already say. It links to them:
> - `docs/SETUP.md` — installing Defects4J, Java, Python, `.env`
> - `docs/condition_model.md` §6 — the canonical study command recipes
> - `docs/USAGE.md` — every CLI flag, in tables
> - `AGENTS.md` §11 item 16 — the manifest-vs-artifacts-root rule
> - `docs/study_execution_log.md` — the running record of real runs

---

## 1. The one rule that prevents most confusion

**A manifest is a worklist. `--artifacts-root` is the namespace.**

The manifest decides *which bugs this run touches*. `--artifacts-root` decides *where output goes*.
Two different manifests pointed at the same root write into the same per-bug folders when their
bugs overlap — that is intentional, and it is what lets everyone share one context store.

So: to split work between people, give them **different manifests** and the **same artifacts root**.

---

## 2. Roles

**These are roles, not people.** One person can do both Collector and Classifier — the split above
exists so the Collector doesn't *need* an LLM key, not so they're forbidden from having one.

Current assignment: **Nahiyan collects first — that's the priority, and it's the slow, disk-heavy
part.** If he finishes the six manifests with time left over, he moves on to classifying the same
manifests, following the Classifier section below exactly (same conditions, same
`--artifacts-root`). His `.env`'s LLM key is sent to him directly by the project owner, out of band —
**never through git.** `.env` is gitignored on purpose (see `docs/SETUP.md`); nothing about receiving
a key changes that. If he doesn't get to classification, that's fine — collection alone is the
bottleneck this handoff exists to unblock, and whoever classifies later just needs `docs/TEAM_WORKFLOW.md`
§2 Classifier and the same repo state he already pushed.

### Collector — generates `context.json` (the slow step)

**Needs:** Defects4J installed, **Java 11**. That's it — **no LLM API key**, no `DEFAULT_LLM_PROVIDER`
config, no Impact/condition knowledge. `study-collect` never imports the LLM layer; grep
`collect_bug_context` in `pipeline.py` and it's Defects4J + the bug-report fetcher only. See
`docs/SETUP.md` for installing Defects4J and, on Windows, WSL.

This is the only role that needs Defects4J. It is also the only slow one: about **63 seconds per
context** and roughly **115 MB of disk per bug** while running.

**`study-collect` collects BOTH evidence modes for every bug automatically, with coverage on by
default.** There is no flag to choose one mode — the loop inside it always does prefix then postfix
per bug (`for evidence_mode in ("prefix", "postfix")`, hardcoded). Coverage runs unless you pass
`--skip-coverage`, which you should not do for real collection — coverage is what makes the evidence
usable (see `docs/study_execution_log.md` for why the old, coverage-empty corpus was replaced).

**Smoke-test with one bug, both modes, before launching a full manifest** — this catches a broken
`DEFECTS4J_CMD`, a wrong `DEFECTS4J_PATH_STYLE`, or a silently-failing checkout cleanup in under a
few minutes instead of after two hours:

```bash
source .venv/bin/activate

python -m d4j_odc_pipeline collect --project Lang --bug 1                        # prefix mode
python -m d4j_odc_pipeline collect --project Lang --bug 1 --include-fix-diff     # postfix mode
```

If both produce a `context.json` (`.dist/runs/Lang_1_prefix/` and `.dist/runs/Lang_1_postfix/`) with
a non-empty `coverage` section, Defects4J and coverage work. **That single-bug `collect` command does
NOT test checkout cleanup** — it never deletes its own work dir (only the batch command does). Move
on to the real check below before trusting a long unattended run.

**Verify checkout cleanup actually works on your machine before walking away from a full run.** This
matters specifically because you're on WSL: the automatic deletion (`shutil.rmtree` on a Defects4J
checkout) has real test coverage on native Linux but has never been exercised against a
`/mnt/c/...`-style path, which is what `docs/SETUP.md`'s recommended layout puts your `work-root` on.
If it silently fails there, checkouts pile up instead of being deleted (~115–234 MB each) and your
disk fills over the course of a multi-hour run with no error, just increasingly full.

Start the first real manifest, but check in after the first couple of bugs instead of leaving it
unattended immediately:

```bash
python -m d4j_odc_pipeline study-collect \
  --manifest .dist/study/manifest_chart26.json \
  --artifacts-root .dist/study/artifacts_v2 \
  --work-root .dist/study/work_v2
```

After the first 1–2 bugs finish (or Ctrl+C once they do — it's safe, it checkpoints), run this in
another terminal or after stopping:

```bash
du -sh .dist/study/work_v2
```

This should be a few KB, not hundreds of MB — the checkout for each finished bug should already be
gone. **If it's not near-zero, stop. Do not let the run continue unattended.** That means cleanup is
silently failing on this machine and every bug is going to leave a checkout behind — report it rather
than deleting the directory yourself or patching the pipeline (see the note below on why). Re-run the
same `study-collect` command to resume once whatever's blocking it is fixed.

Once you've confirmed `du -sh` stays small after a couple of bugs, resume the same command and let it
run the rest of the manifest — but it's still worth an occasional `du -sh .dist/study/work_v2` check
during a long overnight run rather than trusting it blindly the whole way through.

**The six projects, in the order to run them** — cheapest first, so an interrupted session still
leaves whole projects finished rather than six half-finished ones. Every manifest listed here already
exists in the repo at the given path; nothing needs generating.

| Order | Project | Bugs | Manifest |
|---|---|---|---|
| 1 | Chart | 26 | `.dist/study/manifest_chart26.json` |
| 2 | Time | 26 | `.dist/study/manifest_time26.json` |
| 3 | Mockito | 38 | `.dist/study/manifest_mockito38.json` |
| 4 | Lang | 61 | `.dist/study/manifest_lang61.json` (9/61 bugs already collected — see below) |
| 5 | Math | 106 | `.dist/study/manifest_math106.json` |
| 6 | Closure | 174 | `.dist/study/manifest_closure174.json` |

Run the same `study-collect` command for each, only changing `--manifest`. **Lang already has 9 bugs
collected and committed** (`Lang_1,3,4,5,6,7,8,9,10`, both modes) from a prior session — `study-collect`
skips those automatically (`skip_existing`, on by default) and resumes the rest.

Notes:
- **Checkouts are deleted automatically** once each `context.json` is written, so peak disk is one
  checkout (~234 MB worst case, Closure) instead of ~29 GB. Watch for the `Work dir discarded` log
  line after each bug — if it never appears, checkouts are piling up and you should stop and report
  it rather than patch around it (see below). Pass `--keep-work` only when debugging a collection
  failure.
- No `--daily-call-budget`, no `--taxonomy`/`--strategy` — collection has neither an LLM call nor a
  condition, so `study-collect` doesn't take those flags at all.
- Ctrl+C is safe. It writes a checkpoint (`checkpoint.collect.json`) and stops cleanly. Re-running
  the same command resumes.
- If Defects4J fails with `Java 11 is required!`, your default JDK is too new. Point `JAVA_HOME` at
  a Java 11 JDK **and** put its `bin/` first on `PATH` — Defects4J checks the `java` on `PATH`, so
  `JAVA_HOME` alone does nothing. This is a per-machine environment fix, never a repo/code change.
- **If `study-collect` fails or misbehaves, stop and report it — don't hand-patch the pipeline.**
  The single-bug `collect` command used to be the only collect option and never cleaned up its own
  checkout; that gap is exactly what led to a locally-patched copy and a Drive handoff before. The
  batch command now has the same tested cleanup `study-run` uses. If it's still wrong, that's a real
  bug worth fixing once, centrally — not a reason to route around git again.
- Contexts land as ordinary files under `--artifacts-root`. Once your manifest finishes, commit them
  (§5, Path A) or zip and send them (§5, Path B) — both are fully supported; there's no need to route
  around the repo.

### Classifier — turns contexts into labels

**Needs:** an LLM API key. **Nothing else.** No Defects4J, no Java, no checkouts. If you're picking
this up after collecting, the key was sent to you directly (Slack/email/etc.), not through git — put
it in your local `.env` (copy `.env.example`) and never commit that file, gitignored or not.

That is a real guarantee, not a hope: `classify` has no `--defects4j-cmd` at all, and `study-run`
skips collection entirely when `context.json` already exists, so it never calls Defects4J.

**Always run the readiness gate first:**

```bash
python scripts/check_contexts.py .dist/study/manifest_lang61.json .dist/study/artifacts_v2
```

It exits non-zero if anything is missing or was collected with the old evidence code. If even one
context is missing, that bug falls through to collection inside `study-run` and fails on a machine
without Defects4J — which is exactly the confusing failure this gate exists to prevent.

Then classify — a genuinely different command from the Collector's `study-collect`, not the same one
with a flag dropped:

```bash
python -m d4j_odc_pipeline study-run \
  --manifest .dist/study/manifest_lang61.json \
  --artifacts-root .dist/study/artifacts_v2 \
  --taxonomy open --strategy scientific \
  --daily-call-budget 2000 --prompt-output
```

Since every context already exists (checked by the gate above), `study-run` reuses each one instead
of collecting — this pass is a pure classify run in practice, even though the command has no
`--collect-only` counterpart of its own.

Change `--strategy` to run another condition. Each condition writes its own filenames, so
conditions never overwrite each other.

Do **not** pass `--require-all-projects` — it is the one flag that calls Defects4J.

### Reporter — builds the spreadsheets and paper tables

**Needs:** `pip install -r requirements.txt` (includes `openpyxl`).

```bash
# Cross-project Excel workbook for the supervisor
python scripts/reports/generate_combined_report.py

# Per-condition drift analysis (RQ1/RQ3/RQ5), then LaTeX + CSV for the paper
python -m d4j_odc_pipeline study-drift  --manifest .dist/study/manifest_lang61.json \
                                        --artifacts-root .dist/study/artifacts_v2 \
                                        --taxonomy open --strategy scientific
python -m d4j_odc_pipeline study-export --analysis .dist/study/analysis_lang61_scientific-open.json
```

See §6 for the important caveat about the combined report.

---

## 3. Conditions

Five are valid; the CLI rejects the rest.

| `--strategy` | `--taxonomy` | Tag on every filename | Cost |
|---|---|---|---|
| `zero` | `free` | `zero-free` | 1 call |
| `few` | `closed` / `open` | `few-closed` / `few-open` | 1 call |
| `scientific` | `closed` / `open` | `scientific-closed` / `scientific-open` | ~2.5 calls (loop) |

Current priority: **`scientific-open` and `few-open`**, both evidence modes, all projects.
`zero-free` is the bottom rung of RQ4's ablation ladder and is cheap — worth adding once the two
priority conditions finish.

---

## 4. Where files go

```
.dist/study/
  manifest_<scope>.json                     the worklist (hand-authored or via study-plan)
  artifacts_v2/                             ← the shared namespace
    prefix/<Project>_<bug>_prefix/
      context.json                          shared by ALL conditions — collected once
      classification.<tag>.json             one per condition
      report.<tag>.md                       one per condition, human-readable
      prompt.<tag>.json                     only with --prompt-output
    postfix/<Project>_<bug>_postfix/        same, plus the fix diff as oracle
    checkpoint.collect.json                 resume state for study-collect (no condition — bug set only)
    checkpoint.pairs.<tag>.json             resume state for study-run, per condition
    runs.jsonl                              append-only ledger: one line per run
  summary.<tag>.json                        per-run summary
  analysis_<scope>_<tag>.{json,md}          study-drift output
```

**`context.json` is shared and read-only after collection.** Every condition reads the same file.
Never regenerate it just to run a new condition.

**`runs.jsonl`** is the answer to "did results get better or worse". Each line records run id,
timestamps, git SHA, condition, provider/model, call count and bug counts. Read it to know what
produced what.

---

## 5. Moving work between machines

Both paths are fine. Use whichever you trust on the day.

### Path A — git branch (preferred)

Work on your own branch. Nothing you do can damage `main` or `fix_jss`; the worst case is deleting
your branch.

```bash
git checkout -b contexts/<yourname>

# add ONLY your artifacts root — never `git add -A` or `git add .`
git add .dist/study/artifacts_v2
git commit -m "contexts: Chart + Time (52 contexts)"
git push -u origin contexts/<yourname>
```

On the receiving machine:

```bash
git fetch origin && git checkout contexts/<yourname>
python scripts/check_contexts.py .dist/study/manifest_chart26.json .dist/study/artifacts_v2
```

**Never use `git add -A` or `git add .` in this repo.** There are unrelated modified files in the
working tree; `-A` sweeps them into your commit. Naming the path explicitly is the whole safety
mechanism.

Size is not a problem: the largest context is 0.4 MB and a full 6-project corpus is roughly 159 MB,
well inside GitHub's limits. No Git LFS needed.

### Path B — zip and share (equally valid)

```bash
zip -r artifacts_v2_chart_time.zip .dist/study/artifacts_v2
```

Receiver unzips at the repo root so the path stays `.dist/study/artifacts_v2/...`, then runs the
readiness gate. Use this whenever the git path feels risky — the result is identical.

---

## 6. The Excel reports

### Cross-project workbook

```bash
python scripts/reports/generate_combined_report.py [output.xlsx]
```

Reads `classification.scientific-open.json` for all six project manifests directly from
`ARTIFACTS_ROOT` (hardcoded near the top of the script — **edit it to point at `artifacts_v2`**).
Builds three sheets: **Defect Types** (per bug, pre vs post, changed rows highlighted),
**Type Distribution** (pooled then per project), **Type Drift** (pre×post confusion matrix).

It hard-asserts that every expected bug has both classifications and dies on the first gap, so run
the readiness gate first.

⚠️ **It will overwrite the committed workbook with fewer sheets.** The committed
`combined_report.scientific-open.xlsx` (2026-07-26) has six sheets, three of which were Impact
tables. Impact was removed from the pipeline on 2026-09-10, so the script now produces three. Write
to a new filename if you want to keep the old one.

⚠️ Relative output paths resolve against the **repo root**, not your current directory.

### Per-project workbooks

The six `*_report.xlsx` files in `.dist/study/` were produced by a script that no longer exists. The
4-tab spec is recorded in `docs/xlsx_report_spec.md` — rebuild from there if they are ever needed
again.

---

## 7. Telling current files from dead ones

`.dist/` holds several years of experiment generations side by side. Three mechanical tests, no
judgement needed.

**By date:**

| When | Meaning |
|---|---|
| 2026-09-10 or later | Current work |
| 2026-07-08 → 2026-08-04 | Reference results; authority is `artifacts_full` |
| before 2026-07-07 | Dead |

**By filename** — these names are pre-2026-07-07 and always dead:
`classification.json`, `report.md`, `analysis.json`, `summary.json`, `checkpoint.json` (all
untagged). Anything current carries a condition tag, e.g. `classification.scientific-open.json`.

**By content, per file:**
- `context.json` with `created_at` before **2026-08-10** → collected with the old evidence code
  (`6878d90`). Coverage empty, buggy class often missing entirely. `scripts/check_contexts.py`
  applies this test for you.
  *Do not test for a missing `origin` key instead* — a bug with no stack frames has no frame to
  carry it and passes incorrectly.
- `classification.*.json` containing an `impact` key → produced before the 2026-09-10 Impact
  removal.

### Workspace map

| Path | Status | What it is |
|---|---|---|
| `artifacts_v2/` | **ACTIVE** | The new corpus. Everything current goes here. |
| `artifacts_pilot_v2/` | **ACTIVE** | 6-bug pilot, 2026-09-10, validating the current code |
| `artifacts_full/` | REFERENCE | 854 bugs collected Jun–Jul with the **old** evidence code. 458 classified. Do not add new results here. |
| `lang61_snapshot_pre_fewshot_simplify_2026-08-04/` | ARCHIVE | The pre-change copy of 61 Lang `few-open` results. Tracked since `6aa80ac` (2026-09-11). |
| `manifest40_snapshot_pre_rerun_2026-07-11/` | ARCHIVE | Keep. Frozen record. |
| `pilot_snapshot_pre_audit_2026-07-10/` | ARCHIVE | Keep. Frozen record. |
| `artifacts/` (unnumbered) | DEAD | Abandoned 35/68 run from April, untagged names |
| `artifacts_200/` | DEAD | Abandoned 3/200 run from May |
| `.dist/runs/` | DEAD | Single-bug scratch area, superseded |
| `.dist/test_tmp_batch/` | DISPOSABLE | pytest leftovers, delete freely |
| `*_view/` (10 dirs) | DERIVED | Symlinks into `artifacts_full`, used to scope analysis to one project |
| `work/`, `work_v2/`, `work_*/` | DISPOSABLE | Defects4J checkouts, gitignored, deleted automatically |

Two names that look like conventions but are not: the **"44" scope** (`analysis_44_*`,
`manifest44_*_view/`) has no manifest file — it is `manifest_40` plus the 4 pilot bugs not already
in it. And `taxonomy_grounding_44_extended.json` uses an `_extended` suffix that appears nowhere
else.

⚠️ **Never widen `.gitignore`'s `artifacts/` rule to `artifacts*/`.** It looks like a bug. It is not.
Widening it silently ignores ~7,900 deliberately tracked files.

---

## 8. After every run

Append an entry to `docs/study_execution_log.md`, following the format already used there:

1. What was run and why
2. Bug counts, verified against the local Defects4J clone
3. The **exact commands**, copy-pasteable
4. Any failures and how they were resolved
5. Cost and wall-clock table
6. Verification — actual file counts on disk
7. What is still outstanding

This is how the next person avoids re-deriving what you already know. The log is currently about six
weeks behind; catching it up is worth doing before the next big run.
