# Thesis Methodology Guidance

**I'm reviewing your PDF against the current literature to turn your three dimensions into a concrete, defensible bachelor-thesis methodology, while identifying weak points, risky scope, and the exact next-week supervisor update plus a realistic 3-week pre-defense plan.**

I've pinned down the strongest framing: an explainable, evidence-grounded ODC defect-type classification pipeline on a curated Defects4J subset, under a constrained, reproducible protocol.

You do have enough for a solid pre-defense if you keep that scope disciplined. I'm now turning it into a concrete methodology, a next-week supervisor plan, and a realistic 3-week countdown.

**Thought for 32m 34s**

You are closer than you think.

After reading your PDF, the missing piece is not a brand-new topic; it is a narrower, defensible claim. The strongest synthesis already in your document is this: **Defects4J gives the reproducible execution environment, ODC gives the bug taxonomy, and Scientific Debugging gives the explainable LLM workflow.** That is a legitimate thesis direction, and it aligns with the current literature: Defects4J still exposes scriptable checkout, compile, test, and coverage workflows; ODC is still the classic IBM defect taxonomy; and AutoSD showed that LLMs can be structured around a hypothesis–experiment–conclusion loop instead of acting like opaque patch generators.

## The reason your methodology has felt unstable

The reason your methodology has felt unstable is that “classify Defects4J with LLMs” is too broad. Recent work shows two major confounds you must explicitly handle: developer knowledge inside Defects4J fault-triggering tests can inflate evaluation, and some LLMs can partially memorize bug benchmarks. Newer datasets such as GitBug-Java were created partly to reduce that contamination risk. So your idea is still valid, but your methodology must include safeguards.

One more important point: **do not claim “first-ever defect classification of Defects4J.”** Recent work has already manually classified hundreds of Defects4J faults with a different flow/data-flow taxonomy. Your contribution should instead be framed as an ODC-based, explainable, execution-aware LLM methodology using pre-fix evidence.

## What your thesis should become

A strong, realistic version of your thesis is:

> **An explainable, execution-aware methodology for LLM-based ODC defect-type classification on a controlled subset of Defects4J using only pre-fix evidence.**

That is much better than “we classify all Defects4J bugs with LLMs,” because it is:

- scoped,
- method-driven,
- explainable,
- and easier to defend academically.

## How to interpret your three dimensions

Your PDF’s three dimensions are useful, but each one should play a specific role:

1. **Defects4J is your execution bed, not your novelty.**  
   Use it because it is reproducible and tool-supported. But acknowledge its limitations: benchmark bias, memorization risk, and unrealistic single-fault assumptions.

2. **ODC is your taxonomy, not your entire target space.**  
   ODC is accepted and meaningful, but full multi-attribute ODC is expensive to annotate. For a bachelor’s thesis, that means you should start with a smaller, cleaner target. ODC’s long history and its more recent use in LLM-era root-cause analysis support this move.

3. **Scientific Debugging is your reasoning protocol, not a promise to build full APR.**  
   AutoSD matters here not because you must reproduce full automated repair, but because it gives you a defensible structure: observe, hypothesize, predict, experiment, conclude. You can adapt that structure for classification.

## The methodology I recommend

### 1) Freeze the scope immediately

Do not try to automate all ODC attributes in 3 weeks.

Use:

- **Primary target**: ODC Defect Type
- **Optional secondary target**: one simpler secondary field, such as Trigger, or a collapsed coarse category

Your fallback plan should be:

- report 7-class ODC Type if annotation agreement is acceptable
- otherwise also report a collapsed coarse grouping for robustness

That makes the methodology much safer. Your thesis then becomes about whether LLMs can produce grounded ODC-type classifications and explanations, not about solving all of defect analytics.

### 2) Build a small gold-standard dataset yourselves

This is the step that fixes your earlier “taxonomy weakness.”

Use a small, high-quality subset, not the whole benchmark:

- around 30–50 bugs
- from 3 projects
- chosen to cover some diversity

For each bug:

- manually inspect the bug using all evidence needed for **human annotation**
- assign the **gold ODC defect type**
- write a 2–4 sentence rationale for the label

**Use two annotators if you are two students:**

- both label the same pilot set of 8–10 bugs
- compare disagreements
- refine your annotation guide
- then annotate the full subset
- compute Cohen’s kappa or at least report agreement percentage

**Very important:**  
For the gold label, humans may inspect the fix diff if needed.  
**For the model input, do not give the fix diff.**

That distinction is crucial. It solves the old “post-fix feature paradox” while keeping the oracle reliable.

### 3) Restrict model input to pre-fix evidence

This is one of the most important design choices.

At inference time, your LLM should only see evidence a developer could plausibly access **before the fix**:

- failing test output
- stack trace
- failing test name
- suspicious methods or lines from coverage/localization
- buggy code snippet around the suspicious region

Use Defects4J as the source of that evidence through its normal CLI workflow: compile, test, coverage, and related metadata. Defects4J’s documentation also notes that reproducible execution depends on details like timezone settings, so your environment description should mention that.

**Do not use as model input:**

- fixed patch
- modified-class oracle from the fix
- bug ID in a way that invites memorized retrieval
- benchmark answer text

That is how you defend against the strongest criticism.

### 4) Adapt Scientific Debugging into a classification pipeline

This is where your thesis becomes modern and explainable.

Do not implement a full autonomous debugger if time is short.  
Implement a lightweight AutoSD-inspired prompting pipeline:

**Stage A — Observe**  
Provide:

- failing test output
- stack trace
- suspicious code snippet
- short failure summary  

Ask the model to summarize what is failing.

**Stage B — Hypothesize**  
Ask:

- what likely root cause category is involved?
- what kind of defect behavior is suggested?

**Stage C — Predict**  
Ask:

- what behavior would we expect if this hypothesis were true?
- which code region or condition would likely be implicated?

**Stage D — Experiment**  
Instead of full live debugger automation, use a lightweight evidence refresh:

- coverage-based suspicious lines
- one more focused code snippet
- maybe a narrowed test output or stack frame

**Stage E — Conclude**  
Force structured output:

- `odc_type`
- `confidence`
- `evidence_used`
- `reasoning_summary`
- `needs_human_review` (yes/no)

This is faithful to the Scientific Debugging idea while remaining feasible for a bachelor’s thesis.

### 5) Compare against simple baselines

Your evaluation becomes much stronger if you compare the proposed method against simpler alternatives.

Use these baselines:

1. **Baseline 0**: majority-class baseline
2. **Baseline 1**: direct single-shot LLM classification from minimal text
3. **Baseline 2**: LLM with text + buggy code only
4. **Proposed method**: execution-aware, scientific-debugging prompt

**Optional (only if you have time):**  
5. **Historical baseline**: simple TF-IDF + SVM or Naive Bayes on bug text / failure text

That optional classical baseline is nice because it connects directly to the ODC automation history from SVM-era methods to LSTM/LLM-era methods.

### 6) Evaluate three things, not one

Do not evaluate only “accuracy.”  
Use three evaluation layers:

**A. Classification performance**

- accuracy
- macro-F1
- per-class F1

**B. Annotation reliability**

- Cohen’s kappa or agreement percentage between annotators

**C. Explanation quality**

- correctness
- grounding in evidence
- clarity
- usefulness to a human reviewer

You can rate explanations on a small 1–5 rubric yourselves, or ask one more peer to blind-rate a subset.

That gives your pre-defense methodology real shape. It shows you care not only about labels, but about explainability.

### 7) Add validity safeguards explicitly

This section will impress your supervisor because it shows maturity.

Include these threats and mitigations:

- **Benchmark memorization threat**  
  Mitigation: no fix patch in prompts, no explicit bug IDs, pre-fix evidence only, discussion of contamination risk.

- **Developer-knowledge bias in tests**  
  Mitigation: state the threat explicitly and avoid overstating generality; optionally distinguish bugs with cleaner evidence from those with obvious post-hoc test influence.

- **Small sample size**  
  Mitigation: frame the work as a methodology study / feasibility study

- **Annotation subjectivity**  
  Mitigation: dual annotation + consensus process

- **Prompt sensitivity**  
  Mitigation: fixed prompt template and ablation study

### 8) Add one optional extension for credibility

If time permits, do a tiny external validation:

- take 5–10 bugs from GitBug-Java
- run only the final prompt configuration
- report it as a small transfer check, not a full second benchmark

This is powerful because GitBug-Java was explicitly built from recent bugs to reduce the benchmark-staleness problem.

## The research questions I would put in the proposal

Use something like this:

**RQ1.** How accurately can LLMs classify Defects4J bugs into ODC defect types using only pre-fix evidence?  

**RQ2.** Does execution-aware Scientific-Debugging prompting improve ODC classification compared with direct single-shot prompting?  

**RQ3.** Are the generated ODC explanations sufficiently grounded and clear to support human understanding of the defect?

That is clean, modern, and defendable.

## What you should send your supervisor by Thursday, April 2, 2026

With today being Thursday, March 26, 2026, your next-week target should be a **methodology note**, not a finished system.

Send these 4 things:

1. **A 1–2 page methodology summary**  
   - problem statement  
   - research questions  
   - dataset scope  
   - pipeline  
   - evaluation

2. **A one-figure workflow diagram**  
   - Defects4J evidence extraction  
   - Scientific Debugging prompt stages  
   - ODC label + explanation output

3. **A pilot annotation sheet**  
   - even 8–10 manually labeled bugs is enough to show progress

4. **A risk/mitigation section**  
   - leakage  
   - annotation subjectivity  
   - limited scope

## A message you can send your supervisor

You can adapt this:

> We reviewed the literature and refined our direction. Instead of proposing generic LLM-based bug classification on Defects4J, we now propose an explainable methodology for ODC defect-type classification on a controlled subset of Defects4J.  
>
> The method uses only pre-fix evidence from Defects4J, such as failing tests, stack traces, coverage-based suspicious regions, and buggy code snippets. We adapt the Scientific Debugging workflow to structure LLM reasoning into observation, hypothesis, prediction, experiment, and conclusion, and the final output is an ODC label with explanation and confidence.  
>
> To address earlier weaknesses, we will create a small manually annotated gold set, compare direct prompting with execution-aware prompting, and explicitly discuss threats such as benchmark leakage and developer-knowledge bias.  
>
> We would appreciate your feedback on this methodology before we finalize the pre-defense proposal.

## Your 3-week plan

**Week 1: March 26 – April 2**

- freeze title, RQs, scope
- create annotation guide
- manually label 8–10 pilot bugs
- draft methodology note
- contact supervisor

**Week 2: April 3 – April 9**

- finish full annotated subset
- implement evidence extraction
- implement 3 prompt settings
- run first experiments

**Week 3: April 10 – April 16**

- analyze results
- prepare threats to validity
- build pre-defense slides
- rehearse the story: problem → gap → method → safeguards → expected contribution

## The one sentence that should guide all your decisions

**You are not proposing a new bug taxonomy and you are not promising full automated program repair; you are proposing an explainable, execution-aware LLM methodology for ODC classification of Defects4J bugs using pre-fix evidence.**

That is a solid bachelor’s thesis direction.

If you want, I can turn this into a supervisor-ready 1–2 page methodology note in polished academic language.

---

**Sources**  
All citations appear inline throughout the document (e.g., [arXiv], [Springer], [Defects4J], [IBM Research], etc.).
