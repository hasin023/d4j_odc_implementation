# RCEGen × ODC Thesis: Complete Integration Plan

> **Document purpose:** Full analysis of the RCEGen paper (Mollik et al., 2025) — its
> workflow, prompts, evaluation methodology, and results — followed by a precise,
> file-by-file plan for incorporating its best parts into the existing
> `d4j_odc_pipeline` thesis implementation.
>
> **Audience:** The thesis authors and any future agents working in this repository.
>
> **Source files analysed:** `software-04-00029-v2.pdf` (RCEGen paper), `README.md`,
> `AGENTS.md` (ODC pipeline).

---

## Table of Contents

1. [RCEGen Paper — Complete Analysis](#1-rcegen-paper--complete-analysis)
   - 1.1 [Problem Statement & Motivation](#11-problem-statement--motivation)
   - 1.2 [Research Questions](#12-research-questions)
   - 1.3 [Key Contributions](#13-key-contributions)
   - 1.4 [Framework Architecture — All Four Phases](#14-framework-architecture--all-four-phases)
   - 1.5 [Phase 1 — Pre-Processing](#15-phase-1--pre-processing)
   - 1.6 [Phase 2 — RCE Generation (5 LLMs)](#16-phase-2--rce-generation-5-llms)
   - 1.7 [Phase 3 — Judge Prompt Construction](#17-phase-3--judge-prompt-construction)
   - 1.8 [Phase 4 — RCE Evaluation & Selection](#18-phase-4--rce-evaluation--selection)
   - 1.9 [Exact Prompts Used](#19-exact-prompts-used)
   - 1.10 [Dataset](#110-dataset)
   - 1.11 [Experimental Setup](#111-experimental-setup)
   - 1.12 [Results — All Tables & Findings](#112-results--all-tables--findings)
   - 1.13 [Discussion & Key Takeaways](#113-discussion--key-takeaways)
   - 1.14 [Threats to Validity & Limitations](#114-threats-to-validity--limitations)
2. [ODC Thesis Pipeline — Current State](#2-odc-thesis-pipeline--current-state)
   - 2.1 [Architecture Overview](#21-architecture-overview)
   - 2.2 [What the Pipeline Already Produces](#22-what-the-pipeline-already-produces)
   - 2.3 [What Your System Does Better Than RCEGen](#23-what-your-system-does-better-than-rcegen)
   - 2.4 [What Is Currently Missing](#24-what-is-currently-missing)
3. [Head-to-Head Comparison](#3-head-to-head-comparison)
4. [Integration Plan — Complete Implementation](#4-integration-plan--complete-implementation)
   - 4.1 [Overview of Changes](#41-overview-of-changes)
   - 4.2 [Step 1 — `models.py`: Schema Extension](#42-step-1--modelspy-schema-extension)
   - 4.3 [Step 2 — `prompting.py`: Inline RCE Generation](#43-step-2--promptingpy-inline-rce-generation)
   - 4.4 [Step 3 — `pipeline.py`: Extract and Store `rce_text`](#44-step-3--pipelinepy-extract-and-store-rce_text)
   - 4.5 [Step 4 — New `judge.py`: LLM-as-Judge Module](#45-step-4--new-judgepy-llm-as-judge-module)
   - 4.6 [Step 5 — New `evaluation.py`: Batch Metrics](#46-step-5--new-evaluationpy-batch-metrics)
   - 4.7 [Step 6 — `cli.py`: New Commands](#47-step-6--clipy-new-commands)
   - 4.8 [Step 7 — `reporting.py` / `pipeline.py`: RCE in Reports](#48-step-7--reportingpy--pipelinepy-rce-in-reports)
   - 4.9 [Step 8 — Human Reference Dataset Construction](#49-step-8--human-reference-dataset-construction)
   - 4.10 [Step 9 — Multi-LLM Comparative Study](#410-step-9--multi-llm-comparative-study)
   - 4.11 [Step 10 — Information Ablation Study (Unique Contribution)](#411-step-10--information-ablation-study-unique-contribution)
5. [New Output File Structure](#5-new-output-file-structure)
6. [Updated `AGENTS.md` Additions](#6-updated-agentsmd-additions)
7. [Research Contribution Statement](#7-research-contribution-statement)
8. [Quick Reference Checklist](#8-quick-reference-checklist)

---

## 1. RCEGen Paper — Complete Analysis

### 1.1 Problem Statement & Motivation

Root Cause Analysis (RCA) is the process of identifying the underlying cause of a
software defect from a bug report. Traditionally, developers perform RCA manually
before fixing a bug — it is a prerequisite to the fix itself.

**The core problem RCEGen addresses:**

Prior automated RCA work framed the task as a **classification problem** — predicting
a coarse category (e.g., "Null Check Not Performed", "Exception Not Thrown", "Algorithm
Error"). These category-based outputs have two fundamental weaknesses:

1. **Ambiguity:** The same category label maps to many different specific causes.
   A developer receiving "Algorithm Error" still has to perform manual inspection.
2. **Insufficient granularity:** Bug root causes vary enormously. Coarse categories
   cannot capture the diversity of real-world defects. As Catolino et al. (2019)
   argue: "not all bugs are the same."

**The reframing RCEGen proposes:**

Treat RCA as a **generative task** instead of a classification task. Instead of
predicting a label, have an LLM generate a natural language explanation of what
specifically caused the bug. This produces per-report, fine-grained, actionable
output that a developer can immediately act on.

**What makes manual RCA hard:**

- Bug reports are written by end-users who lack technical expertise. They describe
  symptoms, not causes.
- Developers own only specific components and have varying expertise levels.
- The volume of bugs in large-scale systems makes manual triage impractical.
- Manual RCA is slow and introduces delay in the maintenance cycle.

---

### 1.2 Research Questions

RCEGen investigates four research questions:

| RQ | Question | Purpose |
|----|----------|---------|
| **RQ1** | To what extent is RCEGen effective at producing correct, clear, and actionable root causes, and which LLM performs best? | Measure per-model performance across three quality dimensions |
| **RQ2** | To what extent are independent LLM judges reliable when scoring RCE quality? | Validate the automated evaluation pipeline via inter-rater agreement |
| **RQ3** | To what extent do RCEGen's explanations align with developer-authored root-cause analyses? | Validate practical utility against ground-truth human explanations |
| **RQ4** | To what extent does the quality of a bug report's title and description impact RCEGen's accuracy? | Understand input sensitivity and identify failure modes |

---

### 1.3 Key Contributions

The paper claims three primary contributions:

1. **RCEGen framework** — A novel LLM-based pipeline for generating
   evidence-grounded root cause explanations directly from bug reports.

2. **Comparative LLM evaluation** — A systematic comparison of five
   state-of-the-art open-source code LLMs under unified zero-shot prompting.

3. **LLM-as-Judge evaluation framework** — A ranking-based scoring system
   assessing RCE quality on three dimensions (Correctness, Clarity, Depth of
   Reasoning), validated through inter-rater agreement analysis.

---

### 1.4 Framework Architecture — All Four Phases

RCEGen is a four-phase pipeline. Every bug report passes through all four phases
sequentially.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          RCEGen Pipeline                                │
│                                                                         │
│  Bug Report ──► [1. Pre-Processing] ──► Final Prompt                   │
│                                              │                          │
│                                              ▼                          │
│                                    [2. RCE Generation]                  │
│                              ┌───────────────────────────┐             │
│                              │  Qwen2.5-Coder-32B        │             │
│                              │  DeepSeek-Coder-33B        │             │
│                              │  Codestral-22B             │             │
│                              │  CodeLlama-34B             │             │
│                              │  OpenCoder-8B              │             │
│                              └───────────────────────────┘             │
│                                    5× RCEs produced                     │
│                                              │                          │
│                                              ▼                          │
│                              [3. Judge Prompt Construction]             │
│                        Bug Report + Generated RCE ──► Judge Prompt     │
│                                              │                          │
│                                              ▼                          │
│                              [4. RCE Evaluation & Selection]            │
│                              ┌────────────────────────────┐            │
│                              │  Judge: GPT-4o             │            │
│                              │  Judge: DeepSeek-V3        │            │
│                              └────────────────────────────┘            │
│                    Score on: Correctness · Clarity · Depth             │
│                                              │                          │
│                              Best RCE selected ──► Developer           │
└─────────────────────────────────────────────────────────────────────────┘
```

**Automation level:** Fully automated end-to-end. Human developers were only
involved for a validation subset of 75 bug reports (RQ3).

---

### 1.5 Phase 1 — Pre-Processing

**Input:** A bug report (title + description + any embedded stack trace).

**Steps:**

1. Extract key metadata from each bug report:
   - `bug_report_title`
   - `bug_report_body` (description, comments, embedded traces)

2. Build an initial prompt using a fixed zero-shot template (see Section 1.9).
   The template frames the task as a software engineering problem with a role
   assignment ("You are a software engineer").

3. **Token-length filtering:** Filter out bug reports whose concatenated
   title + body exceeds a conservative token budget.
   - The most constrained model (OpenCoder-8B) has an 8,192-token context window.
   - RCEGen targets inputs where `title + body ≤ 3,000 tokens`.
   - Very long bug reports (dominated by large stack traces or verbose logs)
     are **excluded entirely** from the dataset.
   - Rationale: Small-capacity models hallucinate on very long inputs.

4. The resulting clean prompt is the "Final Prompt" fed to all five generator LLMs.

**Important design choice:** RCEGen uses **only the bug report text** — no code,
no execution, no test results. This is the single greatest weakness of the paper
relative to your ODC thesis.

---

### 1.6 Phase 2 — RCE Generation (5 LLMs)

Five open-source code LLMs were selected based on the EvalPlus leaderboard
(HumanEval benchmark rankings). Selection criteria:

- High HumanEval ranking
- Parameter size ≤ 35B (hardware constraint: NVIDIA RTX A6000, 48 GB VRAM)
- Instruction-tuned variants
- Avoid redundant model families

| Model | Params | Developer | Context Window | Selection Reason |
|-------|--------|-----------|----------------|-----------------|
| **Qwen2.5-Coder-32B-Instruct** | 32B | Alibaba | 128K | Top-ranked, broad language support, GPT-4o competitive |
| **DeepSeek-Coder-33B-Instruct** | 33B | DeepSeek | 16K | Strong code completion, fill-in-the-blank training |
| **Codestral-22B-v0.1** | 22B | Mistral AI | 32K | Open-source, 80+ languages, strong infilling |
| **CodeLlama-34B-Instruct** | 34B | Meta | 16K | Popular baseline, strong Python, HumanEval-proven |
| **OpenCoder-8B-Instruct** | 8B | Infly | 8K | Smallest model; tests whether scale matters |

**What each model produces:** A raw text response containing a root cause
explanation (RCE) of up to three sentences. The same prompt is sent to all five
models with no model-specific tuning.

**Prompting strategy:** Zero-shot only. No few-shot examples, no chain-of-thought,
no retrieval, no external tools. The authors deliberately avoided these to isolate
each model's intrinsic reasoning ability.

---

### 1.7 Phase 3 — Judge Prompt Construction

For each generated RCE, a "judge prompt" is constructed by combining:

1. The **original bug report** (title + description)
2. The **generated RCE** from one of the five models

This creates a "peer review" setup where a second, more powerful LLM reads both
the original evidence and the proposed explanation, then scores its quality.

**Two judge models are used simultaneously:**

| Judge Model | Why Selected |
|-------------|-------------|
| **GPT-4o** | Strong alignment with human judgments in LLM-as-judge benchmarks; 128K context; proven code evaluation quality |
| **DeepSeek-V3** | 671B MoE model; superior SWE-benchmark performance; provides independent second opinion; architecturally distinct from GPT-4o |

**Rationale for two judges:** Using two architecturally different judge models
reduces single-model bias. Agreement between them (measured by Cohen's κ)
validates the reliability of the evaluation. The authors explicitly chose models
that are unlikely to share training data pathways.

---

### 1.8 Phase 4 — RCE Evaluation & Selection

**Scoring dimensions:** Each RCE is scored on three dimensions (1–5 Likert scale):

| Dimension | Definition |
|-----------|-----------|
| **Correctness** | Does the explanation accurately and precisely identify the underlying root cause? |
| **Clarity** | Is the explanation easy to understand and coherent with the context of the bug report? |
| **Depth of Reasoning** | Does the explanation logically connect the symptoms to the root cause and provide sufficient justification or evidence? |

**Scoring formula:**

```
Q_overall = w_c × C + w_l × L + w_d × D

where w_c = w_l = w_d = 1/3  (equal weights, no arbitrary bias)

Scores normalized to [0, 1] via min-max normalization.
```

After discovering low inter-rater agreement on Clarity (Cohen's κ < 0.25 for
most models), the authors revised to:

```
Q_overall_revised = 0.5 × C + 0.5 × D  (Clarity excluded)
```

**Selection:** The RCE with the highest mean Q_overall across both judges is
selected as the final output for that bug report. Ties are broken by GPT-4o's
score (which shows slightly stronger correlation with human judgments).

**Semantic similarity evaluation (RQ3):**

- **CodeBERTScore** (embedding-based, range [0,1]): measures semantic fidelity
  between LLM-generated RCE and developer-written reference.
- **ROUGE-L** (lexical, range [0,1]): measures longest common subsequence overlap.
- Human references were collected from 2 senior developers for a stratified
  sample of 75 bug reports (Yamane's formula: n ≈ 75 from N=298, 95% CI, ±10%).

---

### 1.9 Exact Prompts Used

#### Generator Prompt (Zero-Shot Instruction Prompt for RCE Generation)

```
You are a software engineer. You can use your expertise and analyze the root
cause of the bug using bug report's title and description.

Now, I'll give you a bug title and description, you will give me the root
cause in up to three sentences. Please don't write more than three sentences.

Bug report: "
Bug Report Title: {bug_report_title}
Bug Report Body: {bug_report_body}"

Output:
Root Cause:
```

**Design decisions in this prompt:**

- Role assignment: `"You are a software engineer"` — frames the task from a
  developer's perspective.
- Hard length limit: "up to three sentences" — ensures concise, comparable output.
- No few-shot examples — tests intrinsic model ability.
- No chain-of-thought instructions — keeps outputs comparable.
- Simple placeholder injection: `{bug_report_title}` and `{bug_report_body}`.

#### Judge/Evaluation Prompt

```
You are a judge evaluating the quality of a root cause explanation for
a given bug report. Your task is to assess the explanation using three
evaluation metrics: Correctness, Clarity, and Depth of Reasoning. Each metric
should be scored independently on a scale from 1 (poor) to 5 (excellent).

Evaluation Criteria:
- Correctness: Does the explanation accurately and precisely identify the
  underlying root cause?
- Clarity: Is the explanation easy to understand and coherent with the context
  of the bug report?
- Depth of Reasoning: Does the explanation logically connect the symptoms to
  the root cause and provide sufficient justification or evidence?

Bug Report:
title: {bug_report_title}
description: {bug_report_body}

Root Cause:
{root_cause_provided_by_llm}

Please provide your scores using the format below, followed by a very short
justification for each score:

Final Scores:
- Correctness:
- Clarity:
- Depth of Reasoning:
```

**Design decisions in the judge prompt:**

- The judge sees the original bug report AND the RCE together — enabling
  fact-checking of the explanation against the source evidence.
- Each dimension is defined explicitly to reduce judge interpretation variance.
- Justification is requested ("very short") — enables qualitative analysis.
- Free-text response format (not JSON) — the scores are parsed from the output.

---

### 1.10 Dataset

| Property | Value |
|----------|-------|
| **Source** | Hirsch et al. (2022) — 361 training bug reports from Java open-source GitHub projects |
| **Final size after filtering** | **298 bug reports** |
| **Filtering reason** | Token-length exceeded model context limits |
| **Original purpose** | Classification task (Hirsch et al. used ground-truth labels) |
| **RCEGen's use** | Generative — labels were **not used**; only title + description |
| **Bug types** | Memory, concurrency, and semantic bugs (Java open-source only) |
| **Validation subset** | 75 bugs with human-written reference RCEs |

**Important dataset limitation:** The dataset is biased toward memory, concurrency,
and semantic issues. UI, configuration, and documentation bugs are
underrepresented. Results may not generalize beyond these categories.

---

### 1.11 Experimental Setup

| Resource | Specification |
|----------|--------------|
| **GPU** | NVIDIA RTX A6000 (48 GB GDDR6) |
| **Model format** | Locally deployed open-source models |
| **Max model size** | 35B parameters (hardware limit) |
| **Input token budget** | ≤ 3,000 tokens per bug report |
| **Output token limit** | 3 sentences (enforced by prompt) |
| **Judge models** | GPT-4o (API) + DeepSeek-V3 (API) |
| **Evaluation metric** | Weighted Cohen's κ for inter-rater agreement |
| **Semantic metric** | CodeBERTScore (microsoft/codebert-base) |
| **Lexical metric** | ROUGE-L |
| **Human validators** | 2 senior developers for 75-bug reference set |

---

### 1.12 Results — All Tables & Findings

#### Table 1: Per-Model Quality Scores (Mean ± SD, both judges)

| Judge | Model | Correctness μ(σ) | Clarity μ(σ) | Depth μ(σ) | Overall μ(σ) |
|-------|-------|-----------------|-------------|-----------|-------------|
| DeepSeek-V3 | **Qwen2.5-Coder-32B** | **0.879 (0.155)** | 0.879 (0.133) | **0.636 (0.151)** | **0.798 (0.112)** |
| DeepSeek-V3 | Codestral-22B | 0.836 (0.176) | **0.883 (0.132)** | 0.616 (0.159) | 0.778 (0.120) |
| DeepSeek-V3 | DeepSeek-Coder-33B | 0.743 (0.219) | 0.837 (0.145) | 0.537 (0.190) | 0.706 (0.156) |
| DeepSeek-V3 | CodeLlama-34B | 0.757 (0.217) | 0.813 (0.156) | 0.493 (0.187) | 0.688 (0.158) |
| DeepSeek-V3 | OpenCoder-8B | 0.756 (0.227) | 0.677 (0.251) | 0.519 (0.208) | 0.651 (0.181) |
| GPT-4o | **Qwen2.5-Coder-32B** | **0.890 (0.133)** | 0.821 (0.115) | **0.648 (0.138)** | **0.786 (0.105)** |
| GPT-4o | Codestral-22B | 0.873 (0.157) | 0.824 (0.121) | 0.656 (0.149) | 0.784 (0.121) |
| GPT-4o | DeepSeek-Coder-33B | 0.781 (0.199) | 0.778 (0.132) | 0.562 (0.179) | 0.707 (0.150) |
| GPT-4o | CodeLlama-34B | 0.810 (0.186) | 0.769 (0.122) | 0.550 (0.165) | 0.710 (0.137) |
| GPT-4o | OpenCoder-8B | 0.731 (0.220) | 0.575 (0.254) | 0.506 (0.222) | 0.604 (0.199) |

**Findings from Table 1:**

- Qwen2.5-Coder-32B is the best model overall (correctness ≈ 0.89, overall ≈ 0.79).
- Codestral-22B is second-best, closely following Qwen.
- Depth of Reasoning is the weakest dimension across ALL models (max ≈ 0.65).
- OpenCoder-8B (smallest) performs worst — scale matters for this task.
- DeepSeek fluently writes clear text but is less factually accurate.

#### Table 2: Inter-Rater Agreement (Weighted Cohen's κ)

| Model | Correctness κ | Clarity κ | Depth κ |
|-------|--------------|-----------|---------|
| DeepSeek-Coder-33B | **0.709** | 0.255 | **0.650** |
| Codestral-22B | 0.704 | 0.146 | 0.546 |
| CodeLlama-34B | 0.670 | 0.236 | 0.608 |
| Qwen2.5-Coder-32B | 0.662 | 0.216 | 0.532 |
| OpenCoder-8B | 0.639 | **0.631** | 0.555 |

**Findings from Table 2:**

- **Correctness** has substantial agreement (κ ≈ 0.64–0.71) — reliable.
- **Depth of Reasoning** has moderate agreement (κ ≈ 0.53–0.65) — acceptable.
- **Clarity** has very low agreement (κ < 0.26 for 4 of 5 models) — **unreliable**.
  - Exception: OpenCoder-8B had high clarity κ = 0.631, but only because both
    judges consistently agreed it was *unclear*.
- Conclusion: Clarity is too subjective for LLM-based evaluation. It was
  excluded from the revised scoring formula.

#### Table 3: Overall Scores With and Without Clarity

| Judge | Model | Overall (with Clarity) | Overall (without Clarity) |
|-------|-------|----------------------|--------------------------|
| DeepSeek-V3 | Qwen2.5-Coder-32B | 0.798 (0.112) | 0.758 (0.143) |
| DeepSeek-V3 | Codestral-22B | 0.778 (0.120) | 0.726 (0.158) |
| GPT-4o | Qwen2.5-Coder-32B | 0.786 (0.105) | 0.786 (0.105) |
| GPT-4o | Codestral-22B | 0.784 (0.121) | 0.784 (0.121) |

**Finding:** Rankings are preserved; top-2 models remain unchanged. Including
Clarity inflated some scores without adding reliability.

#### Table 4: Similarity to Human-Written Reference RCEs

| Model | CodeBERTScore | ROUGE-L |
|-------|--------------|---------|
| **Qwen2.5-Coder-32B** | **0.989 ± 0.005** | 0.134 ± 0.057 |
| Codestral-22B | 0.987 ± 0.006 | 0.165 ± 0.079 |
| CodeLlama-34B | 0.987 ± 0.006 | **0.183 ± 0.086** |
| DeepSeek-Coder-33B | 0.978 ± 0.009 | 0.153 ± 0.063 |
| OpenCoder-8B | 0.947 ± 0.013 | 0.017 ± 0.027 |

**Critical finding:** CodeBERTScore ≈ 0.98 across top models, while ROUGE-L < 0.20.
This proves that **high semantic fidelity does not require lexical similarity**.
LLMs paraphrase faithfully rather than copy. Evaluation pipelines using only
ROUGE-L will systematically undervalue LLM-generated explanations.
CodeBERTScore must be used.

#### RQ4 Findings: Bug Report Quality Impact

**Low-scoring reports shared these deficiencies:**

- Vague or very short titles (e.g., "Crash in RateLimiter delete")
- Missing reproduction steps
- No error messages, logs, or stack traces in the description
- Result: speculative, weakly-supported hypotheses

**High-scoring reports shared these properties:**

- Specific error message pinpointing the failure mode
- A minimal reproduction snippet with concrete execution context
- Clear statement of expected vs. actual behavior
- Result: LLMs correctly identified the fault AND articulated the causal chain

**Pattern identified (3 failure anti-patterns):**

1. **Under-specification:** Short title + no reproduction cues → generic interpretation
2. **Missing cross-checks:** Stack trace present but no expected/actual text → symptom chasing
3. **Ambiguous scope:** Multi-component bug + no module boundaries → hallucinated wrong subsystem

---

### 1.13 Discussion & Key Takeaways

1. **Generative RCA surpasses classification-based approaches.** Fixed categories
   (Algorithm, Checking, etc.) cannot capture the per-report specificity that
   developers need. Generating fine-grained natural language explanations directly
   addresses the granularity gap.

2. **Correctness is strong; reasoning depth is the ceiling.** Models achieve
   correctness ≈ 0.89 but depth ≈ 0.65. When reports lack grounding signals (logs,
   traces, reproduction steps), models resort to plausible but shallow hypotheses.

3. **Semantic alignment with developers is high; lexical overlap is low.** Use
   CodeBERTScore, not ROUGE-L, as the primary evaluation metric for explanation
   quality. ROUGE-L underestimates quality by ≈ 40%.

4. **Evaluator LLMs are reliable for correctness and depth, not clarity.**
   Implement the κ < 0.25 filter — exclude unstable dimensions from ranking.

5. **Bug report quality is a prerequisite for LLM-based RCA.** The analogy to
   human debugging holds: LLMs, like developers, need structured evidence to reason
   deeply. Vague reports produce vague explanations regardless of model capability.

6. **Future direction: retrieval + reflection.** Replace zero-shot with a
   retrieve-and-reflect loop (similar bugs, diffs, traces) and allow the model to
   cite specific evidence in its explanation.

---

### 1.14 Threats to Validity & Limitations

| Category | Threat | Mitigation in Paper |
|----------|--------|-------------------|
| Internal | Subjectivity of human RCA assessment | Multiple reviewers + structured criteria |
| Internal | Dataset bias (memory/concurrency/semantic bugs) | Stratified sampling where possible |
| Internal | Training data overlap between generator and judge LLMs | Architecturally distinct judges + κ analysis |
| Internal | LLM-as-Judge loop without full human evaluation | Partial mitigation via 75-bug human subset |
| External | Java open-source GitHub only | Acknowledged; closed-source and other languages excluded |
| External | Long reports excluded by token limit | Acknowledged; industrial verbose tickets underrepresented |
| Design | Zero-shot, 3-sentence cap may underestimate model potential | Acknowledged; ensures comparability |
| Design | Skewed bug type distribution | Acknowledged; may bias away from UI/config bugs |

---

## 2. ODC Thesis Pipeline — Current State

### 2.1 Architecture Overview

The thesis pipeline has three primary modes:

```
collect  ──►  context.json
classify ──►  classification.json + report.md
compare  ──►  comparison.json  (pre-fix vs post-fix)
```

**Full evidence collection flow:**

```
Bug Report URL ─────────────────────────────────────────────────────────┐
d4j info (root cause text) ─────────────────────────────────────────────┤
                                                                         ▼
d4j checkout (buggy version) ──► d4j compile ──► d4j test               │
                                                      │                  │
                              Parse failing_tests ◄───┘                  │
                                      │                                  │
                         Filter suspicious frames                        │
                         (remove JUnit/JDK/Hamcrest/Mockito/etc.)       │
                                      │                                  │
                         Extract production snippets (±12 lines)         │
                         Extract failing test source                     │
                         Optional: d4j coverage (Cobertura XML)         │
                         Optional: fixed-version diff (post-fix oracle) │
                                      │                                  │
                              context.json ◄──────────────────────────────┘
```

**Classification flow:**

```
context.json
    │
    ▼
Build system prompt:
  - ODC taxonomy (7 types, contrastive definitions, boundary rules)
  - 7-question diagnostic decision tree
  - 5 canonical few-shot examples
  - Scientific debugging protocol (observation→hypothesis→prediction→experiment→conclusion)
  - Anti-bias rules (prevent default-to-Function)
    │
Build user prompt (evidence payload):
  - production_code_snippets
  - test_code_snippets
  - bug_info + bug_report_content
  - stack traces (filtered, project-only)
  - coverage data (optional)
  - metadata (report URL, revisions)
  - fix_diff (optional, oracle-labelled)
    │
    ▼
Call LLM (Gemini / OpenRouter / OpenAI-compatible)
    │
    ▼
Parse JSON response
    │
    ▼
Validate odc_type → Canonicalize family from odc.py
    │
    ▼
classification.json + report.md
```

---

### 2.2 What the Pipeline Already Produces

The `classification.json` already contains these reasoning fields — all of which
are more structured than anything RCEGen produces:

| Field | Description | RCEGen equivalent |
|-------|-------------|-------------------|
| `odc_type` | One of 7 canonical ODC types | Not present (no structured taxonomy) |
| `family` | Control and Data Flow / Structural | Not present |
| `confidence` | Float [0, 1] | Not present |
| `needs_human_review` | Boolean flag | Not present |
| `observation_summary` | What the failing test and stack trace show | Source of "Correctness" judgment |
| `hypothesis` | Proposed causal mechanism | Source of "Depth of Reasoning" |
| `prediction` | What the fix would do | Unique to ODC pipeline |
| `experiment_rationale` | Why this evidence supports the hypothesis | Unique to ODC pipeline |
| `reasoning_summary` | Full chain in prose | Closest to RCEGen's RCE |
| `evidence_used` | List of specific evidence items cited | Unique to ODC pipeline |
| `evidence_gaps` | What's missing or uncertain | Unique to ODC pipeline |
| `alternative_types` | Other ODC types considered | Unique to ODC pipeline |
| `evidence_mode` | "pre-fix" or "post-fix" | Unique to ODC pipeline |

**In summary:** Your system already produces 14 structured fields per bug. RCEGen
produces one unstructured text blob of 3 sentences. The depth gap is **in your
favour**.

---

### 2.3 What Your System Does Better Than RCEGen

| Dimension | RCEGen | Your ODC Pipeline |
|-----------|--------|-------------------|
| **Input signals** | Bug report text only | Bug report + failing tests + stack traces + production code + test source + optional coverage + optional fix diff |
| **Dataset quality** | Text-only bug reports, no execution ground truth | Defects4J — real, reproducible Java bugs with ground-truth patches and failing test suites |
| **Reasoning structure** | One unstructured 3-sentence blob | 9 structured reasoning fields with explicit scientific debugging stages |
| **Prompting sophistication** | Zero-shot, no examples, no chain-of-thought | Scientific debugging protocol + 5 few-shot examples + 7-question diagnostic decision tree + anti-bias rules |
| **Structured output** | None — free text | JSON with 14 typed fields including confidence and alternative_types |
| **ODC taxonomy** | None — no structured defect taxonomy | Full 7-type ODC taxonomy with contrastive boundary rules |
| **Pre/post-fix comparison** | Not possible | First-class: compare-batch with Cohen's κ |
| **Hidden oracle discipline** | Not applicable | classes.modified deliberately excluded from prompt |
| **Evaluation metric** | F1 not applicable — generative | Cohen's κ on exact type / top-2 / family match |

---

### 2.4 What Is Currently Missing

These are the gaps your system has **relative to** what RCEGen contributed:

| Gap | Description | Impact |
|----|-------------|--------|
| **G1: No condensed RCE** | The `reasoning_summary` is rich but long. There is no concise 2–3 sentence developer-facing summary that synthesizes the ODC type + evidence into an immediately readable output. | Developers prefer a one-paragraph briefing over a full structured JSON |
| **G2: No LLM-as-judge evaluation** | Classification accuracy (F1) measures label correctness but not reasoning quality, clarity, or depth. | Cannot claim the reasoning chain is good — only that the label is right |
| **G3: No inter-rater reliability on explanations** | Cohen's κ is computed for ODC label agreement (pre-fix vs post-fix) but not for explanation quality across evaluators. | Evaluation of reasoning is unvalidated |
| **G4: No CodeBERTScore / semantic similarity** | No measurement of how semantically close LLM-generated explanations are to expert-written references. | Cannot counter "ROUGE-L is low therefore outputs are wrong" objection |
| **G5: No multi-LLM comparative study** | Single LLM provider evaluated. | No model ranking; weaker comparative contribution |
| **G6: No human reference RCE dataset** | No expert-written reference explanations to validate against. | Cannot run RQ3-style semantic validation |
| **G7: No bug report quality analysis** | No study of how input richness (quality of bug report + signals) affects output quality. | Cannot characterize failure modes systematically |

---

## 3. Head-to-Head Comparison

```
┌──────────────────────┬────────────────────────────┬────────────────────────────┐
│ Dimension            │ RCEGen                     │ Your ODC Thesis            │
├──────────────────────┼────────────────────────────┼────────────────────────────┤
│ Task framing         │ Generative (free text)     │ Classificatory + Generative│
│ Input                │ Bug report text only        │ Execution-aware, 7 signals │
│ Dataset              │ 298 text-only reports       │ Defects4J (real execution) │
│ Structured taxonomy  │ None                       │ 7-type ODC taxonomy        │
│ Reasoning structure  │ Unstructured 3 sentences   │ 9 structured fields        │
│ Prompting            │ Zero-shot, minimal          │ Scientific debugging, rich │
│ Output               │ Free-text RCE               │ JSON + structured reasoning│
│ Evaluation           │ LLM-as-judge + κ            │ Label F1 + pre/post κ      │
│ Semantic validation  │ CodeBERTScore + ROUGE-L     │ Not yet implemented        │
│ Human validation     │ 75-bug reference set        │ Not yet implemented        │
│ Multi-LLM comparison │ 5 models compared           │ Not yet implemented        │
│ Pre/post-fix study   │ Not applicable              │ First-class feature        │
│ RCE quality scoring  │ Yes (Correctness/Clarity/D) │ Not yet implemented        │
│ Inter-rater κ (expln)│ Yes                        │ Not yet implemented        │
└──────────────────────┴────────────────────────────┴────────────────────────────┘
```

**Bottom line:** RCEGen has a stronger **evaluation methodology** for explanation
quality. Your thesis has a fundamentally stronger **input pipeline and reasoning
structure**. The integration goal is to add RCEGen's evaluation methodology on
top of your superior evidential foundation.

---

## 4. Integration Plan — Complete Implementation

### 4.1 Overview of Changes

The integration requires **7 file modifications** and **2 new files**:

| File | Change Type | What Changes |
|------|-------------|-------------|
| `models.py` | Modify | Add `rce_text` to `ClassificationResult`; add `JudgeScore`, `RCEEvaluation` dataclasses |
| `prompting.py` | Modify | Add RCE instruction block + `rce_text` to JSON schema spec |
| `pipeline.py` | Modify | Extract `rce_text` from LLM response; pass to `ClassificationResult` |
| `judge.py` | **New file** | LLM-as-judge scoring module |
| `evaluation.py` | **New file** | Batch aggregation, Cohen's κ, CodeBERTScore, ROUGE-L |
| `cli.py` | Modify | Add `judge` and `evaluate-batch` commands |
| `reporting.py` | Modify | Include RCE section in markdown reports |
| `comparison.py` | Modify | Include RCE mean scores in batch comparison output |
| `odc.py` | No change | Already correct |
| `defects4j.py` | No change | Already correct |
| `llm.py` | No change | Already correct |

**Zero extra API calls are required for RCE generation.** The `rce_text` field is
produced by the same LLM call that produces the ODC classification. The judge
calls are a separate, optional evaluation step run after classification.

---

### 4.2 Step 1 — `models.py`: Schema Extension

Add `rce_text` to the existing `ClassificationResult` dataclass and add two new
dataclasses for judge evaluation.

```python
# ── In ClassificationResult (add after reasoning_summary) ──────────────────

rce_text: str = ""
# A condensed 2-3 sentence natural language root cause explanation synthesized
# from observation_summary + hypothesis + reasoning_summary.
# Produced by the classifier LLM at classification time — not a separate call.
# This is the developer-facing output, equivalent to RCEGen's RCE.
# Unlike RCEGen, this explanation is constrained by the formal ODC type prior
# and grounded in actual execution evidence (stack trace, test source, code snippets).


# ── New dataclasses (add at end of models.py) ───────────────────────────────

@dataclass
class JudgeScore:
    """Quality score for one RCE from one judge model."""
    judge_model: str
    correctness: float           # normalized [0, 1], originally 1-5 Likert
    clarity: float               # normalized [0, 1]
    depth_of_reasoning: float    # normalized [0, 1]
    overall: float               # (correctness + clarity + depth) / 3
    overall_no_clarity: float    # (correctness + depth) / 2  [more reliable]
    correctness_note: str = ""
    clarity_note: str = ""
    depth_note: str = ""
    created_at: str = ""


@dataclass
class RCEEvaluation:
    """Per-bug aggregate of all judge scores for one RCE."""
    project_id: str
    bug_id: int
    rce_text: str
    odc_type: str
    judge_scores: list           # list[JudgeScore]
    mean_overall: float          # mean across judges
    mean_correctness: float
    mean_depth: float
    # Populated only in batch evaluation:
    codebertscoreore: float = 0.0
    rouge_l: float = 0.0
    human_reference_rce: str = ""
    created_at: str = ""
```

**Schema change policy:** When updating `ClassificationResult`, follow the
AGENTS.md schema change protocol:

1. Update `models.py`
2. Update writers/readers in `pipeline.py`
3. Update backward compatibility in `comparison.py`
4. Update prompt contract in `prompting.py`
5. Update README and AGENTS.md

The `rce_text = ""` default ensures backward compatibility with older
`classification.json` artifacts that do not include this field.

---

### 4.3 Step 2 — `prompting.py`: Inline RCE Generation

This is the most important change. Modify the existing classification prompt to
also request `rce_text` as a JSON output field. No extra API call is needed.

#### 4.3.1 Add the RCE instruction block to the system prompt

In `build_messages()` (or equivalent), add this block to the system prompt
**after** the ODC classification instructions:

```python
RCE_INSTRUCTION_BLOCK = """
## Root Cause Explanation (rce_text field)

After completing your ODC classification, synthesize a concise Root Cause
Explanation (RCE) and write it in the `rce_text` JSON field.

The RCE must be exactly 2-3 sentences. Write it as if briefing a senior
developer who has not read the bug report and will immediately start
investigating the fix.

Rules for rce_text:
1. Anchor every claim to specific, observable evidence: class name, method
   name, test assertion, exception type, or line-level behavior.
2. State the defect mechanism in the first sentence — do not hedge or
   use "it appears that" or "based on the evidence."
3. Name the ODC defect type naturally in the explanation (e.g., "an
   algorithm error in X" not "this is classified as Algorithm/Method").
4. Do not reproduce the bug report title verbatim.
5. Connect symptoms (what the test sees) to cause (what the code does)
   within the 2-3 sentences.

Good rce_text example:
  "The StringUtils.repeat() method computes the output array size using a
  signed integer multiplication that silently overflows to a negative value
  for large repeat counts, triggering a NegativeArraySizeException before
  any guard condition is evaluated. The failing test confirms this by calling
  repeat('a', Integer.MAX_VALUE) and expecting an IllegalArgumentException,
  but the JVM throws NegativeArraySizeException during array allocation — a
  path that bypasses the method's own input validation entirely."

Bad rce_text example (do NOT do this):
  "Based on the evidence, it appears the bug may be related to an algorithm
  issue. The classification is Algorithm/Method. More investigation needed."
"""
```

#### 4.3.2 Add `rce_text` to the JSON output schema specification

In the section of the prompt that specifies the required JSON output format,
add `rce_text`:

```python
JSON_OUTPUT_SCHEMA_EXTENSION = {
    # ... all existing fields remain unchanged ...
    "rce_text": (
        "string — 2-3 sentences, evidence-anchored natural language root cause "
        "explanation suitable for immediate developer consumption. Must cite "
        "specific class/method names and connect symptoms to cause."
    )
}
```

#### 4.3.3 Add to Gemini structured output schema

If using Gemini's `response_schema` feature for structured JSON output, add:

```python
"rce_text": {"type": "STRING"}
```

to the schema properties alongside the existing fields.

#### 4.3.4 Prompt quality note

Because your prompt already uses scientific debugging structure, the LLM has
already reasoned through observation → hypothesis → prediction before it writes
the RCE. The `rce_text` will therefore be a synthesis of already-completed
structured reasoning — making it far more grounded than RCEGen's free-form
zero-shot RCEs.

---

### 4.4 Step 3 — `pipeline.py`: Extract and Store `rce_text`

In `classify_bug_context()`, after parsing the JSON response and extracting
existing fields, add:

```python
# After existing field extraction (odc_type, confidence, hypothesis, etc.):

result.rce_text = parsed.get("rce_text", "").strip()

# Validate that rce_text is not empty and not too long
if not result.rce_text:
    result.notes = (result.notes or "") + " [WARNING: rce_text missing from LLM response]"
elif len(result.rce_text.split()) > 120:
    # 3 sentences should be ~60-90 words; truncate if grossly oversized
    result.notes = (result.notes or "") + " [WARNING: rce_text unexpectedly long]"
```

No other changes are needed in `pipeline.py` for the core classification flow.
The `rce_text` will be automatically serialized as part of `ClassificationResult`
when `classification.json` is written.

---

### 4.5 Step 4 — New `judge.py`: LLM-as-Judge Module

Create `d4j_odc_pipeline/judge.py`. This implements RCEGen's evaluation Phase 3
and Phase 4, adapted to your richer context.

```python
"""
judge.py — LLM-as-judge evaluation of RCE quality.

Adapted from RCEGen (Mollik et al., 2025) for the d4j_odc_pipeline.

Scores a ClassificationResult's rce_text on three dimensions:
  - Correctness (1-5): Does the RCE accurately identify the root cause?
  - Clarity (1-5):     Is it readable and grounded in the bug context?
  - Depth (1-5):       Does it link symptoms to cause with specific evidence?

Unlike RCEGen, the judge also sees the ODC type label, confidence, and
execution-level evidence — providing richer grounding for the correctness
judgment.

Usage:
    from d4j_odc_pipeline.judge import judge_classification
    scores = judge_classification(ctx, result, [(client, "gpt-4o"), (client2, "deepseek-v3")])
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from .models import BugContext, ClassificationResult, JudgeScore


# ── System prompt for judge ────────────────────────────────────────────────

JUDGE_SYSTEM_PROMPT = """You are an expert software engineering evaluator.

You will assess the quality of a Root Cause Explanation (RCE) for a Java bug
from the Defects4J benchmark. You are given:
  1. Bug evidence: failing test, stack trace top frames, production code snippet.
  2. The ODC defect type and confidence assigned by a classifier.
  3. The RCE text to evaluate.

Score EACH dimension INDEPENDENTLY on a 1-5 scale:
  1 = Poor   2 = Fair   3 = Adequate   4 = Good   5 = Excellent

CORRECTNESS (most important):
  Does the RCE accurately identify the underlying root cause as evidenced by
  the stack trace and production code? Does it correctly reflect the assigned
  ODC defect type? A score of 5 requires specific, verifiable claims — not
  general statements like "there is a logic error."

CLARITY:
  Is the explanation precise, concise, and free of vague hedging ("it appears
  that", "may be related to")? Would a developer unfamiliar with this bug
  understand exactly what is wrong after reading it?

DEPTH OF REASONING:
  Does the RCE connect observable symptoms (test failure, exception message)
  to the specific code-level cause (wrong condition, missing null check,
  overflow in computation) with concrete evidence (class names, method names,
  specific values)?

Respond with ONLY a JSON object. No preamble, no markdown, no extra text.
{
  "correctness": <integer 1-5>,
  "correctness_note": "<one sentence justification, max 20 words>",
  "clarity": <integer 1-5>,
  "clarity_note": "<one sentence justification, max 20 words>",
  "depth_of_reasoning": <integer 1-5>,
  "depth_note": "<one sentence justification, max 20 words>"
}"""


# ── User prompt builder ────────────────────────────────────────────────────

def build_judge_user_prompt(ctx: BugContext, result: ClassificationResult) -> str:
    """
    Build a concise judge user prompt from BugContext + ClassificationResult.

    Deliberately uses a compressed evidence subset — not the full classify prompt —
    to avoid pushing the judge past its context window. The judge needs enough
    to verify the RCE; it does not need to re-derive the classification.
    """
    parts = []

    # ── Bug identity ────────────────────────────────────────────────────────
    parts.append(f"## Bug: {ctx.project_id}-{ctx.bug_id}")

    # ── Failing test (first failure only) ───────────────────────────────────
    if ctx.failures:
        f = ctx.failures[0]
        parts.append(f"\n### Failing test\n`{f.test_class}#{f.test_method}`")

        if f.stack_frames:
            parts.append("\nTop stack frames (project source only):")
            for fr in f.stack_frames[:4]:
                parts.append(
                    f"  {fr.class_name}.{fr.method_name}"
                    f"({fr.file_name}:{fr.line_number})"
                )

        if hasattr(f, "error_message") and f.error_message:
            parts.append(f"\nException: `{f.error_message[:200]}`")

    # ── Production code snippet (first suspicious frame, truncated) ─────────
    if ctx.code_snippets:
        s = ctx.code_snippets[0]
        parts.append(f"\n### Production code ({s.class_name})")
        # Cap at 600 chars — judge needs context, not the full method
        parts.append("```java\n" + s.source[:600] + "\n```")

    # ── Failing test source (if available) ──────────────────────────────────
    if ctx.test_code_snippets:
        ts = ctx.test_code_snippets[0]
        parts.append(f"\n### Failing test source ({ts.class_name})")
        parts.append("```java\n" + ts.source[:400] + "\n```")

    # ── Bug report summary (truncated) ──────────────────────────────────────
    if ctx.bug_info:
        parts.append(f"\n### d4j bug info\n{ctx.bug_info[:300]}")

    # ── Classification result ────────────────────────────────────────────────
    parts.append(f"\n### ODC classification\n**Type:** {result.odc_type}")
    parts.append(f"**Confidence:** {result.confidence:.2f}")
    if result.alternative_types:
        parts.append(f"**Alternatives considered:** {', '.join(result.alternative_types)}")

    # ── The RCE to evaluate ──────────────────────────────────────────────────
    parts.append(f"\n### Root Cause Explanation to evaluate\n{result.rce_text}")

    return "\n".join(parts)


# ── Core scoring function ──────────────────────────────────────────────────

def _parse_judge_response(raw: str) -> dict:
    """Extract JSON scores from judge model raw response."""
    # Strip markdown fences if present
    raw = re.sub(r"```(?:json)?", "", raw).strip().strip("`").strip()
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError(f"Judge returned no valid JSON. Raw: {raw[:300]}")
    return json.loads(match.group())


def _normalize(v: int | float, scale: int = 5) -> float:
    """Map a 1-to-scale Likert value to [0, 1]."""
    return round((float(v) - 1) / (scale - 1), 4)


def score_rce(
    ctx: BugContext,
    result: ClassificationResult,
    judge_client,          # LLMClient instance
    judge_model: str,
) -> JudgeScore:
    """
    Call one judge LLM and return a JudgeScore.

    Args:
        ctx:          BugContext for this bug.
        result:       ClassificationResult containing the rce_text to judge.
        judge_client: An initialized LLMClient instance.
        judge_model:  Model name to pass to the client.

    Returns:
        A populated JudgeScore with normalized [0,1] values.
    """
    if not result.rce_text:
        raise ValueError("ClassificationResult.rce_text is empty — cannot judge.")

    user_prompt = build_judge_user_prompt(ctx, result)
    messages = [
        {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
        {"role": "user",   "content": user_prompt},
    ]

    raw = judge_client.complete(messages, model=judge_model)
    parsed = _parse_judge_response(raw)

    c = _normalize(parsed.get("correctness", 3))
    l = _normalize(parsed.get("clarity", 3))
    d = _normalize(parsed.get("depth_of_reasoning", 3))

    return JudgeScore(
        judge_model=judge_model,
        correctness=c,
        clarity=l,
        depth_of_reasoning=d,
        overall=round((c + l + d) / 3, 4),
        overall_no_clarity=round((c + d) / 2, 4),    # RCEGen revised formula
        correctness_note=parsed.get("correctness_note", ""),
        clarity_note=parsed.get("clarity_note", ""),
        depth_note=parsed.get("depth_note", ""),
        created_at=datetime.now(timezone.utc).isoformat(),
    )


def judge_classification(
    ctx: BugContext,
    result: ClassificationResult,
    judge_clients: list[tuple],   # [(LLMClient, model_name_str), ...]
) -> list[JudgeScore]:
    """
    Score an RCE with all configured judge models.

    Best practice: pass two architecturally distinct judge models
    (e.g., GPT-4o + Gemini-1.5-Pro, or GPT-4o + DeepSeek-V3) so that
    inter-rater agreement can be computed.

    Returns a list of JudgeScore, one per judge. Failed judges are skipped
    with a warning rather than raising — partial results are preserved.
    """
    scores = []
    for client, model in judge_clients:
        try:
            score = score_rce(ctx, result, client, model)
            scores.append(score)
            print(f"[judge] {model}: correctness={score.correctness:.3f}  "
                  f"depth={score.depth_of_reasoning:.3f}  "
                  f"overall={score.overall:.3f}")
        except Exception as exc:
            print(f"[judge] WARNING: {model} failed — {exc}")
    return scores
```

---

### 4.6 Step 5 — New `evaluation.py`: Batch Metrics

Create `d4j_odc_pipeline/evaluation.py`. This provides:

- Weighted Cohen's κ (exact match to RCEGen's method)
- ROUGE-L (self-contained, no external dependency)
- CodeBERTScore (optional; requires `evaluate` + `transformers`)
- Aggregate statistics matching RCEGen Table 1 and Table 2 format

```python
"""
evaluation.py — Batch RCE evaluation metrics.

Implements:
  - Weighted Cohen's kappa (inter-rater agreement, RCEGen Table 2 equivalent)
  - ROUGE-L (lexical overlap baseline, no external dependency)
  - CodeBERTScore (semantic similarity vs human references, optional dep)
  - Aggregate statistics (RCEGen Table 1 equivalent)

All metric implementations are self-contained except CodeBERTScore, which
requires: pip install evaluate transformers torch
"""

from __future__ import annotations

import json
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Optional

from .models import JudgeScore, RCEEvaluation


# ════════════════════════════════════════════════════════════════════════════
# Cohen's weighted kappa
# ════════════════════════════════════════════════════════════════════════════

def _to_likert(normalized: float, k: int = 5) -> int:
    """Convert normalized [0,1] score back to 1-k Likert scale."""
    return min(k, max(1, round(normalized * (k - 1) + 1)))


def weighted_kappa(
    ratings_a: list[int],
    ratings_b: list[int],
    k: int = 5,
) -> float:
    """
    Compute weighted Cohen's kappa for two raters using linear weights.

    w_ij = 1 - |i - j| / (k - 1)

    Matches the methodology in RCEGen Table 2.

    Args:
        ratings_a: Rater A's integer ratings in [1, k].
        ratings_b: Rater B's integer ratings in [1, k].
        k:         Number of scale points (default 5 for 1-5 Likert).

    Returns:
        Weighted Cohen's kappa, range [-1, 1].
    """
    n = len(ratings_a)
    assert n == len(ratings_b), "Rating lists must be equal length"
    assert n > 0, "Cannot compute kappa on empty lists"

    # Linear weight matrix
    W = [
        [1.0 - abs(i - j) / (k - 1) for j in range(k)]
        for i in range(k)
    ]

    # Observed agreement matrix (frequencies, not proportions)
    observed = [[0.0] * k for _ in range(k)]
    for a, b in zip(ratings_a, ratings_b):
        observed[a - 1][b - 1] += 1.0

    # Marginals as proportions
    row_p = [sum(observed[i]) / n for i in range(k)]
    col_p = [sum(observed[i][j] for i in range(k)) / n for j in range(k)]

    # Expected agreement under independence
    Po = sum(W[i][j] * observed[i][j] / n for i in range(k) for j in range(k))
    Pe = sum(W[i][j] * row_p[i] * col_p[j] for i in range(k) for j in range(k))

    if abs(1.0 - Pe) < 1e-10:
        return 1.0  # Perfect agreement edge case
    return round((Po - Pe) / (1.0 - Pe), 4)


def compute_kappa_for_dimension(
    evals: list[RCEEvaluation],
    dimension: str,    # "correctness" | "clarity" | "depth_of_reasoning"
    k: int = 5,
) -> float:
    """
    Compute weighted kappa between the first two judges across all bugs
    for a given scoring dimension.

    Requires at least 2 judges per evaluation and at least 2 evaluations.
    """
    a_ratings, b_ratings = [], []
    for ev in evals:
        if len(ev.judge_scores) >= 2:
            score_a = getattr(ev.judge_scores[0], dimension)
            score_b = getattr(ev.judge_scores[1], dimension)
            a_ratings.append(_to_likert(score_a, k))
            b_ratings.append(_to_likert(score_b, k))

    if len(a_ratings) < 2:
        return 0.0
    return weighted_kappa(a_ratings, b_ratings, k)


# ════════════════════════════════════════════════════════════════════════════
# ROUGE-L
# ════════════════════════════════════════════════════════════════════════════

def _lcs_length(tokens_a: list[str], tokens_b: list[str]) -> int:
    """Compute length of longest common subsequence."""
    m, n = len(tokens_a), len(tokens_b)
    # Space-optimized DP: O(min(m,n)) space
    if m < n:
        tokens_a, tokens_b = tokens_b, tokens_a
        m, n = n, m
    prev = [0] * (n + 1)
    curr = [0] * (n + 1)
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if tokens_a[i - 1] == tokens_b[j - 1]:
                curr[j] = prev[j - 1] + 1
            else:
                curr[j] = max(prev[j], curr[j - 1])
        prev, curr = curr, [0] * (n + 1)
    return prev[n]


def rouge_l(hypothesis: str, reference: str) -> float:
    """
    Compute ROUGE-L F1 score (sentence-level).

    Uses F1 = (2 * P * R) / (P + R) where:
      P = LCS / len(hypothesis tokens)
      R = LCS / len(reference tokens)

    Matches RCEGen Table 4 methodology.
    """
    if not hypothesis or not reference:
        return 0.0
    h_toks = hypothesis.lower().split()
    r_toks = reference.lower().split()
    if not h_toks or not r_toks:
        return 0.0
    lcs = _lcs_length(h_toks, r_toks)
    precision = lcs / len(h_toks)
    recall    = lcs / len(r_toks)
    if precision + recall < 1e-10:
        return 0.0
    return round(2.0 * precision * recall / (precision + recall), 4)


# ════════════════════════════════════════════════════════════════════════════
# CodeBERTScore
# ════════════════════════════════════════════════════════════════════════════

def codebertscoreore(hypothesis: str, reference: str) -> float:
    """
    Compute CodeBERTScore F1 between hypothesis and reference strings.

    Requires: pip install evaluate transformers torch

    Falls back gracefully to 0.0 if the library is unavailable, so the
    rest of the evaluation pipeline continues to function.

    Uses microsoft/codebert-base as the encoder, matching RCEGen Table 4.
    """
    if not hypothesis or not reference:
        return 0.0
    try:
        import evaluate
        scorer = evaluate.load("bertscore")
        result = scorer.compute(
            predictions=[hypothesis],
            references=[reference],
            lang="en",
            model_type="microsoft/codebert-base",
        )
        return round(float(result["f1"][0]), 4)
    except ImportError:
        print("[evaluation] CodeBERTScore unavailable — "
              "run: pip install evaluate transformers torch")
        return 0.0
    except Exception as exc:
        print(f"[evaluation] CodeBERTScore error: {exc}")
        return 0.0


# ════════════════════════════════════════════════════════════════════════════
# Aggregation — RCEGen Table 1 + Table 2 equivalent
# ════════════════════════════════════════════════════════════════════════════

def aggregate_judge_stats(evals: list[RCEEvaluation]) -> dict:
    """
    Compute mean ± SD statistics per judge model (Table 1 equivalent)
    and inter-rater kappa per dimension (Table 2 equivalent).

    Args:
        evals: List of RCEEvaluation objects, one per bug.

    Returns:
        Dict with keys:
          "per_judge_stats": {model_name: {dimension: {mean, sd}}}
          "inter_rater_kappa": {dimension: kappa}
          "summary": overall averages
    """
    per_judge: dict[str, dict[str, list[float]]] = defaultdict(
        lambda: {"correctness": [], "clarity": [], "depth_of_reasoning": [],
                 "overall": [], "overall_no_clarity": []}
    )

    for ev in evals:
        for score in ev.judge_scores:
            m = score.judge_model
            per_judge[m]["correctness"].append(score.correctness)
            per_judge[m]["clarity"].append(score.clarity)
            per_judge[m]["depth_of_reasoning"].append(score.depth_of_reasoning)
            per_judge[m]["overall"].append(score.overall)
            per_judge[m]["overall_no_clarity"].append(score.overall_no_clarity)

    stats: dict[str, dict] = {}
    for model, dims in per_judge.items():
        stats[model] = {}
        for dim, vals in dims.items():
            if len(vals) > 1:
                stats[model][dim] = {
                    "mean": round(statistics.mean(vals), 4),
                    "sd":   round(statistics.stdev(vals), 4),
                    "n":    len(vals),
                }
            elif len(vals) == 1:
                stats[model][dim] = {"mean": round(vals[0], 4), "sd": 0.0, "n": 1}

    kappas = {
        "correctness":       compute_kappa_for_dimension(evals, "correctness"),
        "clarity":           compute_kappa_for_dimension(evals, "clarity"),
        "depth_of_reasoning":compute_kappa_for_dimension(evals, "depth_of_reasoning"),
    }

    return {
        "per_judge_stats": stats,
        "inter_rater_kappa": kappas,
        "n_bugs_evaluated": len(evals),
        "note": (
            "Clarity kappa < 0.25 for most models in RCEGen — "
            "consider using overall_no_clarity as primary metric if this holds."
        ),
    }


def run_semantic_evaluation(
    evals: list[RCEEvaluation],
    references: dict[str, str],    # {"Project-BugID": "human RCE text"}
) -> list[RCEEvaluation]:
    """
    Compute CodeBERTScore and ROUGE-L for each evaluation against human references.

    Modifies evals in place, adding codebertscoreore, rouge_l, and
    human_reference_rce to each RCEEvaluation that has a matching reference.

    Args:
        evals:      List of RCEEvaluation objects.
        references: Dict mapping "{project_id}-{bug_id}" to human RCE string.

    Returns:
        The same list of evals, with semantic scores filled in where available.
    """
    n_matched = 0
    for ev in evals:
        key = f"{ev.project_id}-{ev.bug_id}"
        if key in references:
            ref = references[key]
            ev.human_reference_rce = ref
            ev.codebertscoreore = codebertscoreore(ev.rce_text, ref)
            ev.rouge_l = rouge_l(ev.rce_text, ref)
            n_matched += 1

    print(f"[evaluation] Semantic scores computed for {n_matched}/{len(evals)} bugs.")
    return evals
```

---

### 4.7 Step 6 — `cli.py`: New Commands

Add two new subcommands to the existing CLI:

#### `judge` command

```python
# In the argparse subparser setup, add:

judge_p = subparsers.add_parser(
    "judge",
    help="Score the rce_text in a classification.json using LLM judges"
)
judge_p.add_argument(
    "--context", required=True,
    help="Path to context.json (provides evidence for the judge)"
)
judge_p.add_argument(
    "--classification", required=True,
    help="Path to classification.json (contains rce_text to score)"
)
judge_p.add_argument(
    "--output", required=True,
    help="Output path for judge_scores.json"
)
judge_p.add_argument(
    "--judge-model", action="append", dest="judge_models", metavar="MODEL",
    help=(
        "Judge model name (repeat for multiple judges). "
        "Example: --judge-model gpt-4o --judge-model deepseek/deepseek-v3. "
        "Uses DEFAULT_LLM_MODEL if not specified."
    )
)
judge_p.add_argument(
    "--judge-provider", default=None,
    help="LLM provider for judge calls. Defaults to DEFAULT_LLM_PROVIDER."
)
```

Dispatch handler:

```python
elif args.command == "judge":
    import json
    from dataclasses import asdict
    from .judge import judge_classification
    from .llm import LLMClient
    from .models import BugContext, ClassificationResult, RCEEvaluation
    from datetime import datetime, timezone

    ctx_data = json.loads(Path(args.context).read_text())
    cls_data = json.loads(Path(args.classification).read_text())

    ctx = BugContext(**ctx_data)
    result = ClassificationResult(**cls_data)

    if not result.rce_text:
        print("[judge] ERROR: classification.json has no rce_text field. "
              "Re-run classify with the updated prompting.py first.")
        raise SystemExit(1)

    models = args.judge_models or [os.environ.get("DEFAULT_LLM_MODEL", "")]
    models = [m for m in models if m]
    if not models:
        print("[judge] ERROR: No judge model specified. "
              "Use --judge-model or set DEFAULT_LLM_MODEL.")
        raise SystemExit(1)

    # Use same provider for all judges unless overridden
    provider = args.judge_provider or os.environ.get("DEFAULT_LLM_PROVIDER", "gemini")
    client = LLMClient.from_env(provider=provider)
    judge_clients = [(client, m) for m in models]

    scores = judge_classification(ctx, result, judge_clients)

    if not scores:
        print("[judge] ERROR: All judges failed.")
        raise SystemExit(1)

    mean_overall = sum(s.overall for s in scores) / len(scores)
    mean_corr    = sum(s.correctness for s in scores) / len(scores)
    mean_depth   = sum(s.depth_of_reasoning for s in scores) / len(scores)

    output = {
        "project_id":   ctx.project_id,
        "bug_id":       ctx.bug_id,
        "odc_type":     result.odc_type,
        "rce_text":     result.rce_text,
        "mean_overall": round(mean_overall, 4),
        "mean_correctness": round(mean_corr, 4),
        "mean_depth":   round(mean_depth, 4),
        "judge_scores": [asdict(s) for s in scores],
        "created_at":   datetime.now(timezone.utc).isoformat(),
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(output, indent=2))
    print(f"[judge] Saved → {args.output}")
    print(f"[judge] Mean overall: {mean_overall:.4f} | "
          f"Correctness: {mean_corr:.4f} | Depth: {mean_depth:.4f}")
```

#### `evaluate-batch` command

```python
eval_p = subparsers.add_parser(
    "evaluate-batch",
    help=(
        "Aggregate RCE quality statistics across all judged bugs. "
        "Produces Table 1 and Table 2 equivalent outputs."
    )
)
eval_p.add_argument(
    "--artifacts-dir", required=True,
    help="Directory tree containing judge_scores.json files (searched recursively)"
)
eval_p.add_argument(
    "--references", default=None,
    help=(
        "Optional JSON file mapping 'Project-BugID' to human-written RCE strings. "
        "Required for CodeBERTScore and ROUGE-L computation."
    )
)
eval_p.add_argument(
    "--output", required=True,
    help="Output path for evaluation_summary.json"
)
eval_p.add_argument(
    "--report", default=None,
    help="Optional path for human-readable markdown evaluation report"
)
```

Dispatch handler:

```python
elif args.command == "evaluate-batch":
    import json
    from pathlib import Path
    from .evaluation import aggregate_judge_stats, run_semantic_evaluation
    from .models import RCEEvaluation, JudgeScore

    artifacts_dir = Path(args.artifacts_dir)
    judge_files = list(artifacts_dir.rglob("judge_scores.json"))

    if not judge_files:
        print(f"[evaluate-batch] No judge_scores.json found under {artifacts_dir}")
        raise SystemExit(1)

    print(f"[evaluate-batch] Found {len(judge_files)} judge score files.")

    evals = []
    for jf in judge_files:
        data = json.loads(jf.read_text())
        scores = [JudgeScore(**s) for s in data.get("judge_scores", [])]
        ev = RCEEvaluation(
            project_id=data["project_id"],
            bug_id=data["bug_id"],
            rce_text=data["rce_text"],
            odc_type=data["odc_type"],
            judge_scores=scores,
            mean_overall=data.get("mean_overall", 0.0),
            mean_correctness=data.get("mean_correctness", 0.0),
            mean_depth=data.get("mean_depth", 0.0),
        )
        evals.append(ev)

    # Compute aggregate stats
    summary = aggregate_judge_stats(evals)

    # Optionally compute semantic similarity vs human references
    if args.references:
        references = json.loads(Path(args.references).read_text())
        evals = run_semantic_evaluation(evals, references)
        cbs_scores = [e.codebertscoreore for e in evals if e.codebertscoreore > 0]
        rl_scores  = [e.rouge_l for e in evals if e.rouge_l > 0]
        if cbs_scores:
            import statistics
            summary["semantic_similarity"] = {
                "codebertscoreore_mean": round(statistics.mean(cbs_scores), 4),
                "codebertscoreore_sd":   round(statistics.stdev(cbs_scores) if len(cbs_scores) > 1 else 0.0, 4),
                "rouge_l_mean":   round(statistics.mean(rl_scores), 4),
                "rouge_l_sd":     round(statistics.stdev(rl_scores) if len(rl_scores) > 1 else 0.0, 4),
                "n_compared":     len(cbs_scores),
            }

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(summary, indent=2))
    print(f"[evaluate-batch] Summary saved → {args.output}")
```

---

### 4.8 Step 7 — `reporting.py` / `pipeline.py`: RCE in Reports

In the markdown report generation (currently in `pipeline.py`), add an RCE
section prominently near the top — between the classification summary badge
and the full reasoning chain:

```python
# After the ODC type / confidence / family block:
# Before the full observation_summary / hypothesis section:

if result.rce_text:
    lines.append("\n---\n")
    lines.append("## Root Cause Explanation\n")
    lines.append(f"> {result.rce_text}\n")
    lines.append(
        "*Condensed from execution evidence. Grounded in stack trace, "
        "failing test, and production code snippets.*\n"
    )
    lines.append("---\n")
```

If `judge_scores.json` exists in the same directory, optionally append a
quality score block to the report:

```python
judge_path = Path(output_path).parent / "judge_scores.json"
if judge_path.exists():
    scores_data = json.loads(judge_path.read_text())
    lines.append("\n## RCE Quality Scores (LLM-as-Judge)\n")
    lines.append(f"| Judge Model | Correctness | Depth | Overall |")
    lines.append(f"|-------------|-------------|-------|---------|")
    for s in scores_data.get("judge_scores", []):
        lines.append(
            f"| {s['judge_model']} "
            f"| {s['correctness']:.3f} "
            f"| {s['depth_of_reasoning']:.3f} "
            f"| {s['overall']:.3f} |"
        )
    lines.append(f"\n**Mean overall:** {scores_data.get('mean_overall', 0):.4f}\n")
```

---

### 4.9 Step 8 — Human Reference Dataset Construction

This is the equivalent of RCEGen's RQ3. It requires human effort but produces
the ground truth needed for CodeBERTScore validation.

#### Sampling strategy

Use Yamane's formula to justify your sample size:

```
n = N / (1 + N × e²)

For N = 298 bugs, e = 0.10 (±10% precision), 95% confidence:
n ≈ 75

For a 7-type ODC taxonomy, stratified by type:
~10-11 bugs per ODC type × 7 types = 75-77 bugs
```

Run stratified sampling programmatically:

```python
import json
from pathlib import Path
from collections import defaultdict
import random

artifacts = Path("artifacts")
by_type = defaultdict(list)

for f in artifacts.rglob("classification.json"):
    data = json.loads(f.read_text())
    if data.get("rce_text"):
        by_type[data["odc_type"]].append({
            "key": f"{data['project_id']}-{data['bug_id']}",
            "rce_text": data["rce_text"],
            "odc_type": data["odc_type"],
            "path": str(f),
        })

# Sample ~11 per type
sample = []
for odc_type, bugs in by_type.items():
    n = min(11, len(bugs))
    sample.extend(random.sample(bugs, n))

# Write to a human annotation worksheet
with open("human_annotation_worksheet.json", "w") as fh:
    json.dump(sample, fh, indent=2)

print(f"Sampled {len(sample)} bugs across {len(by_type)} ODC types.")
```

#### Annotation procedure

1. Two annotators (e.g., thesis author + supervisor) independently write
   a 2–3 sentence RCE for each sampled bug using only the `report.md` as input.
   Access to the full `context.json` is allowed but the `fix_diff` must not
   be consulted (to match the pre-fix scenario).

2. Record annotations in a spreadsheet with columns:
   `key | annotator_a_rce | annotator_b_rce | agreed_rce | notes`

3. Compute inter-annotator agreement on the reference texts themselves
   (ROUGE-L between annotator A and B) to validate annotation quality.
   Aim for ROUGE-L ≥ 0.25 between human annotators.

4. Resolve disagreements through discussion into a single `agreed_rce` per bug.

5. Save the final reference file:

```json
{
  "Lang-1":   "The StringUtils.repeat() method...",
  "Lang-3":   "The NumberUtils.createNumber() method...",
  "Math-5":   "The FastMath.atan2() function..."
}
```

1. Pass this file to `evaluate-batch --references human_references.json`.

---

### 4.10 Step 9 — Multi-LLM Comparative Study

RCEGen's biggest standalone contribution is a comparative study of 5 models.
You can replicate this at the `classify` level (for ODC accuracy) and at the
`judge` level (for RCE quality).

#### Classify-level comparison

Run `classify` with different models using the `--model` flag:

```bash
# Run classification with 4 models on the same context.json files
for model in "gemini-1.5-pro" "deepseek/deepseek-coder-33b" \
             "openai/gpt-4o-mini" "meta-llama/codellama-34b-instruct"; do
    python -m d4j_odc_pipeline classify \
        --context artifacts/Lang_1/context.json \
        --output  artifacts/Lang_1/classification_${model//\//_}.json \
        --model   "$model"
done
```

Use `compare-batch` to compute accuracy metrics per model.

#### RCE-quality comparison

After classifying with each model, run `judge` to score each model's `rce_text`:

```bash
for model in "gemini-1.5-pro" "deepseek/deepseek-coder-33b" ...; do
    python -m d4j_odc_pipeline judge \
        --context        artifacts/Lang_1/context.json \
        --classification artifacts/Lang_1/classification_${model//\//_}.json \
        --output         artifacts/Lang_1/judge_scores_${model//\//_}.json \
        --judge-model    gpt-4o \
        --judge-model    deepseek/deepseek-v3
done
```

Use `evaluate-batch` to aggregate across bugs and produce per-model statistics.

#### Expected output table (fills in as you run experiments)

| Model | ODC Acc (exact) | ODC Acc (family) | RCE Correctness | RCE Depth | RCE Overall |
|-------|-----------------|-----------------|-----------------|-----------|-------------|
| Gemini-1.5-Pro | TBD | TBD | TBD | TBD | TBD |
| GPT-4o-mini | TBD | TBD | TBD | TBD | TBD |
| DeepSeek-Coder-33B | TBD | TBD | TBD | TBD | TBD |
| CodeLlama-34B | TBD | TBD | TBD | TBD | TBD |

This table is your thesis's Table 1 equivalent — a direct, publishable contribution.

---

### 4.11 Step 10 — Information Ablation Study (Unique Contribution)

This is something **RCEGen could not do** because it only had text inputs.
Your pipeline has 7 distinct evidence signals. By systematically removing them,
you can quantify each signal's independent contribution to ODC accuracy and RCE
quality.

#### Ablation design

Create variants of `context.json` by zeroing out evidence fields:

```python
# ablation.py — generate ablated context variants

import json
import copy
from pathlib import Path

ABLATION_CONFIGS = {
    "full":              {},   # baseline — all signals
    "no_coverage":       {"coverage": []},
    "no_fix_diff":       {"fix_diff": None},
    "no_test_source":    {"test_code_snippets": []},
    "no_code_snippets":  {"code_snippets": []},
    "no_stack_trace":    {"failures": []},  # removes frames too
    "no_bug_report":     {"bug_report_content": ""},
    "text_only":         {  # closest to RCEGen baseline
        "code_snippets": [],
        "test_code_snippets": [],
        "failures": [],
        "coverage": [],
        "fix_diff": None,
    },
}

def ablate(context_path: Path, config_name: str, config: dict) -> Path:
    data = json.loads(context_path.read_text())
    ablated = copy.deepcopy(data)
    for field, value in config.items():
        ablated[field] = value

    out = context_path.parent / f"context_{config_name}.json"
    out.write_text(json.dumps(ablated, indent=2))
    return out
```

Run the full classify + judge pipeline on each ablated context:

```bash
for config in full no_coverage no_fix_diff no_test_source \
              no_code_snippets no_stack_trace no_bug_report text_only; do
    python -m d4j_odc_pipeline classify \
        --context  artifacts/Lang_1/context_${config}.json \
        --output   artifacts/Lang_1/classification_${config}.json

    python -m d4j_odc_pipeline judge \
        --context        artifacts/Lang_1/context_${config}.json \
        --classification artifacts/Lang_1/classification_${config}.json \
        --output         artifacts/Lang_1/judge_${config}.json \
        --judge-model    gpt-4o
done
```

Expected finding (based on RCEGen RQ4 and literature): stack traces and
production code snippets will have the highest individual contribution; bug
report text alone (the `text_only` config) will produce the weakest results.
This directly validates your design choice to collect execution evidence.

---

## 5. New Output File Structure

After all integrations, a complete run produces:

```
artifacts/
└── Lang_1/
    ├── context.json               # unchanged — all pre-fix evidence
    ├── classification.json        # UPDATED: adds rce_text field
    ├── report.md                  # UPDATED: adds RCE section at top
    ├── judge_scores.json          # NEW: LLM-as-judge quality scores
    ├── prompt.json                # unchanged (--prompt-output flag)
    │
    ├── context_full.json          # Ablation variants (optional)
    ├── context_text_only.json
    ├── ...
    ├── classification_full.json   # Per-ablation classification
    ├── classification_text_only.json
    ├── judge_full.json            # Per-ablation judge scores
    └── judge_text_only.json

artifacts/
└── evaluation_summary.json        # Batch aggregate (Table 1 + Table 2 equiv.)
```

### `classification.json` — updated schema

```json
{
  "project_id": "Lang",
  "bug_id": 1,
  "version_id": "1b",
  "prompt_style": "scientific",
  "model": "gemini-1.5-pro",
  "provider": "gemini",
  "created_at": "2025-...",
  "odc_type": "Algorithm/Method",
  "family": "Control and Data Flow",
  "confidence": 0.91,
  "needs_human_review": false,
  "observation_summary": "...",
  "hypothesis": "...",
  "prediction": "...",
  "experiment_rationale": "...",
  "reasoning_summary": "...",
  "rce_text": "The StringUtils.repeat() method computes...",   ← NEW
  "evidence_used": ["..."],
  "evidence_gaps": ["..."],
  "alternative_types": ["Checking"],
  "evidence_mode": "pre-fix",
  "raw_response": "..."
}
```

### `judge_scores.json` — new schema

```json
{
  "project_id": "Lang",
  "bug_id": 1,
  "odc_type": "Algorithm/Method",
  "rce_text": "The StringUtils.repeat() method...",
  "mean_overall": 0.7917,
  "mean_correctness": 0.875,
  "mean_depth": 0.75,
  "judge_scores": [
    {
      "judge_model": "gpt-4o",
      "correctness": 0.875,
      "clarity": 0.75,
      "depth_of_reasoning": 0.75,
      "overall": 0.7917,
      "overall_no_clarity": 0.8125,
      "correctness_note": "Correctly identifies overflow as the root cause.",
      "clarity_note": "Clear and specific but slightly dense.",
      "depth_note": "Links overflow to array allocation, misses guard bypass path.",
      "created_at": "2025-..."
    },
    {
      "judge_model": "deepseek/deepseek-v3",
      "correctness": 0.875,
      "clarity": 0.875,
      "depth_of_reasoning": 0.75,
      "overall": 0.8333,
      "overall_no_clarity": 0.8125,
      ...
    }
  ],
  "created_at": "2025-..."
}
```

### `evaluation_summary.json` — new schema (mirrors RCEGen Tables 1 & 2)

```json
{
  "n_bugs_evaluated": 75,
  "per_judge_stats": {
    "gpt-4o": {
      "correctness":         {"mean": 0.8720, "sd": 0.142, "n": 75},
      "clarity":             {"mean": 0.8010, "sd": 0.138, "n": 75},
      "depth_of_reasoning":  {"mean": 0.6830, "sd": 0.189, "n": 75},
      "overall":             {"mean": 0.7853, "sd": 0.121, "n": 75},
      "overall_no_clarity":  {"mean": 0.7775, "sd": 0.148, "n": 75}
    },
    "deepseek/deepseek-v3": { "..." }
  },
  "inter_rater_kappa": {
    "correctness":        0.681,
    "clarity":            0.198,
    "depth_of_reasoning": 0.542
  },
  "semantic_similarity": {
    "codebertscoreore_mean": 0.983,
    "codebertscoreore_sd":   0.008,
    "rouge_l_mean":   0.147,
    "rouge_l_sd":     0.062,
    "n_compared":     75
  }
}
```

---

## 6. Updated `AGENTS.md` Additions

Append the following sections to `AGENTS.md`:

```markdown
## 16. RCE Integration (Added from RCEGen paper)

The pipeline now produces a `rce_text` field in `classification.json`.

This is a 2-3 sentence natural language root cause explanation synthesized
at classification time — not a separate API call. It is generated by the same
LLM that produces the ODC classification, using the ODC type as a structured
prior.

Key files:
- `models.py`: `ClassificationResult.rce_text` (str, default "")
- `prompting.py`: RCE_INSTRUCTION_BLOCK added to system prompt
- `pipeline.py`: `result.rce_text = parsed.get("rce_text", "").strip()`

## 17. LLM-as-Judge Evaluation (New module: judge.py)

`judge.py` implements RCE quality scoring adapted from RCEGen (Mollik et al., 2025).

Usage:
    python -m d4j_odc_pipeline judge \
        --context classification.json --classification classification.json \
        --output judge_scores.json \
        --judge-model gpt-4o --judge-model deepseek/deepseek-v3

Output: judge_scores.json with per-judge Correctness/Clarity/Depth scores.

Two judges should always be used for inter-rater reliability analysis.

## 18. Batch Evaluation (New module: evaluation.py)

`evaluation.py` aggregates judge scores across all bugs.

Usage:
    python -m d4j_odc_pipeline evaluate-batch \
        --artifacts-dir artifacts/ \
        --references human_references.json \
        --output evaluation_summary.json

Produces Table 1 equivalent (per-judge mean ± SD) and Table 2 equivalent
(inter-rater Cohen's κ per dimension).

Note: CodeBERTScore requires `pip install evaluate transformers torch`.
ROUGE-L has no extra dependencies.

## 19. Human Reference Dataset

A JSON file mapping "Project-BugID" → "human RCE string" is required for
CodeBERTScore computation. See Section 4.9 of RCEGen_ODC_Integration_Plan.md
for the annotation procedure.

Target size: ~75 bugs (stratified by ODC type, ~11 per type).
```

---

## 7. Research Contribution Statement

After implementing all steps in Section 4, the thesis can make the following
contribution claims — each backed by a concrete implementation:

---

### Primary Contribution

**Claim:** We present the first pipeline that combines structured ODC defect-type
classification with execution-evidence-grounded natural language root cause
explanations on the Defects4J benchmark, evaluated using a dual LLM-as-judge
framework with inter-rater reliability analysis and CodeBERT-based semantic
similarity validation.

**Supported by:**

- ODC classification: existing `classify` pipeline with 7-type taxonomy
- RCE generation: `rce_text` field in `classification.json` (Step 2)
- Execution grounding: failing tests + stack traces + code snippets (existing)
- Dual LLM-as-judge: `judge.py` (Step 4)
- Inter-rater κ: `evaluation.py` `weighted_kappa()` (Step 5)
- CodeBERTScore: `evaluation.py` `codebertscoreore()` (Step 5)

---

### Secondary Contribution: Input Signal Ablation

**Claim:** We quantify the marginal contribution of each evidence signal (bug
report text, failing tests, stack traces, production code snippets, test source,
coverage) to both ODC classification accuracy and RCE quality — demonstrating
that execution-level signals are necessary for deep reasoning, not merely helpful.

**Supported by:** Ablation study (Step 10). This is a contribution RCEGen
explicitly could not make because it only had text-only bug report input.

---

### Tertiary Contribution: Pre-Fix vs Post-Fix RCE Quality

**Claim:** We characterise how access to the fix diff (post-fix oracle) changes
both ODC classification accuracy and RCE quality, providing practitioners with
an empirical bound on what can be determined from pre-fix evidence alone.

**Supported by:** Existing `compare-batch` + new `judge` applied to both
`classification.json` and `classification_postfix.json` artifacts.

---

### Positioning Against RCEGen

Your thesis directly extends RCEGen in three provable ways:

| RCEGen limitation | Your extension |
|-------------------|---------------|
| Text-only input | Execution-aware: stack traces, code snippets, failing tests, coverage |
| No structured taxonomy | Full 7-type ODC taxonomy with contrastive boundary rules and formal definitions |
| Free-text RCE with no structured prior | ODC-type-constrained RCE: the classification result guides the explanation space, reducing hallucination |
| Zero-shot prompting only | Scientific debugging protocol with few-shot examples and 7-question diagnostic decision tree |
| No pre/post-fix analysis | First-class pre/post-fix study with oracle labelling |
| No input sensitivity study | Information ablation study quantifying per-signal contribution |

---

## 8. Quick Reference Checklist

Use this checklist to track implementation progress:

### Schema & Model Layer

- [ ] Add `rce_text: str = ""` to `ClassificationResult` in `models.py`
- [ ] Add `JudgeScore` dataclass to `models.py`
- [ ] Add `RCEEvaluation` dataclass to `models.py`

### Prompt Layer

- [ ] Add `RCE_INSTRUCTION_BLOCK` to system prompt in `prompting.py`
- [ ] Add `rce_text` to JSON output schema specification in `prompting.py`
- [ ] Add `rce_text: {type: STRING}` to Gemini response schema in `prompting.py`

### Pipeline Layer

- [ ] Extract `rce_text` from parsed JSON in `pipeline.py`
- [ ] Add `rce_text` validation warning in `pipeline.py`

### New Modules

- [ ] Create `d4j_odc_pipeline/judge.py` (Section 4.5)
- [ ] Create `d4j_odc_pipeline/evaluation.py` (Section 4.6)

### CLI Layer

- [ ] Add `judge` command to `cli.py` (Section 4.7)
- [ ] Add `evaluate-batch` command to `cli.py` (Section 4.7)

### Reporting Layer

- [ ] Add RCE section to `report.md` generation in `pipeline.py` (Section 4.8)
- [ ] Add judge score table to `report.md` if `judge_scores.json` present

### Experimental Work

- [ ] Run ablation script to generate `context_*.json` variants (Section 4.11)
- [ ] Run multi-LLM classification comparative study (Section 4.10)
- [ ] Collect stratified sample of ~75 bugs for human annotation (Section 4.9)
- [ ] Complete human annotation worksheet with 2 annotators
- [ ] Build `human_references.json` file
- [ ] Run `evaluate-batch` with `--references human_references.json`
- [ ] Install `evaluate transformers torch` for CodeBERTScore

### Documentation

- [ ] Append Sections 16–19 to `AGENTS.md`
- [ ] Update `README.md` with new commands (`judge`, `evaluate-batch`)
- [ ] Update `README.md` output files table with `judge_scores.json`
- [ ] Update `README.md` project structure with `judge.py`, `evaluation.py`

### Backward Compatibility

- [ ] Verify `comparison.py` still works with old artifacts (no `rce_text`)
- [ ] Verify `pipeline.py` still runs if `rce_text` is absent from LLM response

---

*Document prepared: April 2026*
*Based on: RCEGen (Mollik et al., Software 2025, 4, 29) and d4j_odc_pipeline README + AGENTS.md*
