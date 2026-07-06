# Classification Engine Plan — RQ2 Open Taxonomy + Agentic Scientific Loop

**Status:** agreed design, pre-implementation (2026-07-06)
**Scope:** the classification half of the pipeline only. Evidence collection is done — all 800+ `context.json` files exist and are **reused as-is; no re-collection**.
**Companion docs:** `RQ2_ODC_Coverage_Analysis.md` (RQ2 spec), `details_of_RQ2.md` (design defense), `RQs_JSS.md` (RQ list), `eval_defence.md` (pre/post-fix defense).

---

## 1. Why this work exists

The thesis stands on three pillars: **Defects4J** (the corpus), **ODC** (the taxonomy), and the **LLM-driven scientific approach** (the classifier). The first two are fixed; this plan fixes the third. Two gaps remain in the classifier:

1. **The closed 7-type schema cannot falsify itself** (RQ2). We need the 8-type open mode with a structured "Other" escape category — a *measurement instrument*, not a taxonomy extension.
2. **The "scientific debugging" in the current prompt is rhetorical, not procedural.** The LLM narrates observe→hypothesize→predict→examine→conclude in one forward pass over a fixed evidence dump. Nothing can surprise it; it grades its own homework. AutoSD's actual contribution is the **closed loop**: commit a prediction, run an experiment, receive an exogenous observation, revise. The pipeline currently has no feedback edge. Additionally, `confidence` is a single verbalized number with no operational meaning.

**Hard constraint:** the existing single-shot path (scientific/direct/naive styles) must be preserved untouched — it produced the 34-pair preliminary results and remains the RQ4 baseline arm. Everything below is *additive*.

---

## 2. Methodology invariant: the two orderings of the scientific method

Verified against Zeller (*Why Programs Fail*, Ch. 6) and the AutoSD paper (Kang et al., EMSE 2024, Fig. 1 — DOI 10.1007/s10664-024-10594-x). "Observe" has two senses; never mix them:

| Level | Order | Source | Where used |
|---|---|---|---|
| **Process level** | Observe → Hypothesize → Predict → Experiment/Examine → Conclude | Zeller Ch. 6 (failure observed first; hypotheses must be consistent with prior observations) | Single-shot prompt (`prompting.py::_scientific_debugging_instructions`), overall pipeline framing |
| **Loop-iteration level** | Hypothesis → Prediction → Experiment → Observation (the experiment's *result*) → Conclusion | AutoSD Fig. 1 (the initial failure observation is the *prompt input*) | Each turn of the new agentic engine |

The agentic engine implements **both**: the failure evidence from `context.json` seeds the loop (process-level observe-first), then each turn runs the AutoSD iteration order.

The wrong hybrid to never propagate: "Hypothesize, Observe, Predict, Examine, Conclude" (initial symptom examination placed *after* hypothesizing) — it matches neither source. It exists in the frozen `iut_submissions/` deliverables as a known, preserved historical error; do not copy wording from there.

---

## 3. Phase 1 — Open taxonomy for RQ2 ("Other" mode)

Adds a `taxonomy_mode: closed | open` axis. Implements §2.2 of `RQ2_ODC_Coverage_Analysis.md`.

| File | Change |
|---|---|
| `odc.py` | `Other` as a mode-gated 8th label. `taxonomy_markdown(mode)` renders it only in open mode with anti-lazy-escape instructions ("choose Other only after all 7 diagnostics fail"). |
| `prompting.py` | Thread `taxonomy_mode` through `build_messages`; in open mode extend `_json_contract()` with the mandatory-when-Other fields: `other_justification`, `nearest_type`, `other_confidence`. |
| `llm.py` | `classification_response_schema(mode)` — Gemini's `responseJsonSchema` enforces the enum, so open mode changes the allowed label set at the API level. |
| `models.py` | Add the 3 optional fields + `taxonomy_mode` to `ClassificationResult`. |
| `pipeline.py` | Validation: `odc_type == "Other"` ⇒ the 3 fields are required, else reject. |
| `cli.py` / `batch.py` | `--taxonomy open` on `classify`/`run`; new `study-coverage` command = re-run an existing manifest's prefix artifacts under open mode (pass 2 of the two-pass design; pass 1 closed artifacts come from `study-run`). |
| `analysis.py` / `comparison.py` | Coverage Rate, Escape Rate, per-project Escape Rate, Taxonomy Shift (Cohen's κ between closed and open passes — κ machinery exists in `comparison.py`), KL-divergence of type distributions. False Escape Rate via a manual audit workflow over `other_justification`. |

**Two-pass rationale** (from `details_of_RQ2.md`): pass 1 (closed) is the clean baseline for RQ3–RQ5; pass 2 (open) is the RQ2 coverage measurement. Mixing them would contaminate both. The "Other" type makes RQ2 falsifiable — a closed-schema-only study would be circular.

---

## 4. Phase 2 — Agentic scientific loop (`--engine agentic`)

New module (e.g. `agent.py`); default engine stays `single`.

### 4.1 Loop structure

```
seed:  failure observation served from context.json      (process level: observe first)
turn 1..max_turns (default 6):
  LLM returns ONE structured action (per-turn responseJsonSchema):
    hypothesize      → {hypothesis, prediction}
    request_evidence → {probe, args}            # the experiment
    conclude         → {full classification JSON}
  harness executes the probe and appends the REAL result   (exogenous observation)
at max_turns without conclude → forced conclusion, needs_human_review=true
```

Turns are adaptive — the model may conclude on turn 1. The full turn transcript is persisted into `classification.json` (`turns: [...]`) — this is the explainability artifact.

### 4.2 Probes — served from EXISTING artifacts, zero re-collection

The single-shot prompt truncates `context.json` (5 failures / 15 trace lines / 10 frames / 8+3 snippets / 6 coverage classes — see `prompting.py::_context_payload`). The held-back remainder is the probe corpus:

| Probe (tier 1 — always available) | Served from |
|---|---|
| `more_failures`, `full_stack_trace(test)` | `context.failures` (full traces stored) |
| `more_snippets`, `snippet_content(class)` | `context.code_snippets` (all collected) |
| `full_coverage(class)` | `context.coverage` |
| `full_bug_report` | `context.bug_report_content` |

**Tier 2 (optional, later):** on-demand `defects4j checkout` (seconds–minutes; the week-long cost was test+coverage runs, never repeated) enables `read_region`, `grep_source`, and live `run_test`. Build the probe interface so tier 2 slots in; ship tier 1 first.

### 4.3 Why static probes are legitimate "experiments" (epistemics)

- Zeller's step 4 is explicitly "test the hypothesis by experiments **and further observations**" — examining more code/state is within the method.
- The falsifiability property is **exogeneity, not execution**: the model commits its prediction *before* the probe result returns, and the harness answers with ground truth it cannot fabricate. The current single-shot lacks exactly this property.
- Stack traces, failing-test output, and coverage **are recorded executions** — Defects4J ran the code during collection. AutoSD queries a *live* debugger; we query *recorded* execution evidence (record-and-replay analogy). Paper framing: *"experiments realized as hypothesis-driven probes over recorded execution evidence,"* with live `run_test` as an optional upgrade.

---

## 5. Phase 3 — Confidence and budget

### 5.1 Confidence: three honest signals, no fake blending formula

| Field | What | Cost | Trust |
|---|---|---|---|
| `verbalized_confidence` | Model's own number (kept for comparability with old artifacts) | free | low — known to be miscalibrated |
| `consistency_confidence` | k=3 independent runs, temperature > 0; label = majority vote; confidence = agreement fraction | 3× calls → **evaluation subset only** | high — standard, citable (self-consistency) |
| Loop-derived signals | Hypothesis revision count; probes confirmed vs refuted; forced-conclusion flag | free (from transcript) | high — behavioral |

`needs_human_review` becomes **rule-driven**: label flipped across samples ∨ forced conclusion ∨ final hypothesis refuted by a probe ∨ `Other` chosen. On the evaluation subset, run a **calibration analysis** (accuracy binned by confidence) — the JSS answer to "what does 0.85 mean?".

### 5.2 API budget (Gemini flash-lite free tier, ~1,500 RPD binding)

- **Per-bug cap:** `max_turns` (default 6); realistic average ~2–4 calls/bug (pilot will measure).
- **Global daily guard:** runner tracks calls against `--daily-call-budget` (default ~1,400, headroom under RPD); on hit → clean checkpoint stop, resume next day via existing `checkpoint.json` infra. Never burn into 429s.
- **Corpus math:** single-shot ≈ 800 calls (<1 day). Agentic k=1 ≈ 2,800 calls (~2 days). Self-consistency k=3 only on the manifest subset (e.g. 68 bugs ≈ 750 calls, ~half a day).

---

## 6. RQ4 — ablation ladder (loop vs no-loop)

The `engine` axis joins the existing prompt-style arms; each rung isolates exactly one component. Same manifest, same prefix mode, same model — paired per-bug; existing κ/agreement machinery applies.

```
naive              no ODC, no scientific method        (existing)
    + taxonomy grounding
direct             ODC, zero-shot                      (existing)
    + protocol narration
scientific-single  ODC + protocol in one pass          (existing default)
    + closed feedback loop
scientific-agentic ODC + protocol with real turns      (new)
```

**Confound control (mandatory):** the agentic arm sees more evidence (probes unlock held-back context), so add a cheap fifth arm — **single-shot with the full untruncated evidence payload** (1 call/bug):
- single-shot-capped vs single-shot-full → isolates *evidence quantity*
- single-shot-full vs agentic → isolates *the loop itself*

---

## 7. Defense: loopholes, backing, and the overkill question

### 7.1 The syllogism

```
Zeller:  debugging is diagnosis → formalize as the scientific method    (manual)
AutoSD:  the formalized manual process can be executed by an LLM        (automated)
Ours:    ODC classification is ALSO diagnosis — "what KIND of root-cause
         mechanism produced this failure?" is differential diagnosis over
         7 candidate mechanisms → same formalization, LLM-executed       (this thesis)
```

The load-bearing premise — *ODC classification is a diagnosis task* — holds because ODC types are root-cause categories (why the bug happened), not structural ones (how it looks). The diagnostic-questions prompt is literally a differential. The hypothetico-deductive method is the standard formalization of differential diagnosis; importing it here is fit-for-purpose, not decoration.

### 7.2 Backing inventory

1. **Automating ODC is an established goal:** AutoODC (Huang et al., ASE) and Lopes et al. 2020 (*Automating orthogonal defect classification using machine learning algorithms*, FGCS) automated ODC with pre-LLM ML over bug-report text only. **Action: verify/add both to `citations.bib`.** Our delta: richer evidence (code, traces, coverage) + structured reasoning instead of shallow features.
2. **AutoSD** proves the "LLM executes a formalized manual protocol" pattern (kang2023autosd — already cited).
3. **ODC's own docs** require the classifier to understand the root cause — precisely what the protocol forces the LLM to articulate before labeling.
4. Self-consistency, CoT-for-classification, and LLM-as-annotator literatures back the confidence and prompting choices.

### 7.3 Loopholes and their plugs

| # | Loophole | Plug |
|---|---|---|
| 1 | **No executable oracle for the final label** (the real disanalogy with AutoSD: a patch is verifiable by tests; "this is a Checking defect" is not). The loop can converge confidently to a wrong label. | Validation is *agreement-based*, stated explicitly: pre/post-fix consistency (RQ5), self-consistency, κ vs the ~20–30% human-disagreement ceiling from ODC literature. Claim: *the loop guarantees grounded reasoning, not verified conclusions; conclusions are validated statistically.* Never claim more. |
| 2 | **ODC orthodoxy assigns the type at fix time** (closer attribute); pre-fix classification deviates. | Frame pre-fix as a *prediction of the eventual fix's category*; post-fix agreement is its empirical test. The deviation becomes the built-in evaluation (`eval_defence.md`). |
| 3 | **Confirmation bias in the loop** — the model may probe to confirm, not falsify, making the loop theater. | Prediction committed *before* the probe result (exogeneity, §4.3); log confirm/refute rates per bug; a near-zero refute rate is detectable evidence of degeneration, reported not hidden. |
| 4 | **Overkill — is a loop necessary for 7-way classification?** | Made empirical, not assumed: the RQ4 ladder measures the loop's marginal contribution. If agentic ≈ single-shot, that is a reportable finding about where structured reasoning stops paying off — and the rest of the thesis stands on the single-shot arm regardless. Overkill is only a sin when unmeasured and load-bearing; this is measured and severable. |
| 5 | **Anthropomorphism** — claiming the LLM "does science". | Wording rule for the manuscript: the pipeline *"follows a scientific-method protocol."* Operational claims only; no cognitive claims. |

---

## 8. Execution order and validation

1. **Phase 1** (open taxonomy) — fully spec'd, ~1 day; unblocks the RQ2 study.
2. **Phase 2** (agentic engine, tier-1 probes) — ~3–4 days.
3. **Phase 3** (confidence + budget guard) — ~1 day.
4. **Pilot:** 3–5 Lang/Math smoke bugs, then a 20-bug pilot to measure turns/bug (sets the real RPD math and tunes `max_turns`).
5. Wire `engine`/`taxonomy_mode` axes through `batch.py` study commands; checkpoint entries record engine/mode/**exact model ID** per artifact (reproducibility).
6. Update tests alongside each phase (`tests/test_batch.py`, prompt/schema tests).
7. Manuscript updates (later): loop diagram (Observe-first seeding + AutoSD-order iterations — do **not** reuse the frozen report's `scientific_debug` figure, which shows the wrong order), confidence/calibration section, defense points from §7.

### Settled defaults

- Tier-2 executed probes: interface designed now, shipped later.
- `max_turns = 6`, adaptive; pilot may revise.
- Self-consistency k=3 on the evaluation subset only; k=1 corpus-wide.
- Same-provider key rotation (`GEMINI_API_KEYS` round-robin) deferred; revisit if the daily budget becomes the schedule bottleneck.
