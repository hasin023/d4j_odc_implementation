# Thesis Pre-Defense: Paper-to-Story Mapping

## "Orthogonal Defect Classification on Defects4J Using an LLM-Driven Scientific Approach"

---

> **How to use this document:** Each story point lists (a) **supporting papers** that defend your claim, (b) **opposing/gap papers** that expose limitations (useful for building toward your gap), and (c) a **recommended slide citation strategy** based on the Pre-Defense Guidelines.

---

## Story Point 1 — Introduction to Defects4J: What it is, its artifacts, and its continued relevance

### Supporting Papers

| #     | Citation                                                                                                                                                                                | Key Claim Supported                                                                                                                                                                                                                                         |
| ----- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SP1-A | **Just, R., Jalali, D., & Ernst, M. D. (2014).** Defects4J: A database of existing faults to enable controlled testing studies for Java programs. _ISSTA 2014_, pp. 437–440.            | Foundational paper. Defects4J contains real Java bugs paired with regression test suites, developer-written patches, and CLI tools — the very artifacts (bug reports, triggering tests, buggy code, fixed code, code diffs) your ODC pipeline will consume. |
| SP1-B | **Rafi, M. N., Chen, A. R., Chen, T.-H. P., & Wang, S. (2024).** Revisiting Defects4J for Fault Localization in Diverse Development Scenarios. _arXiv:2402.13040._                      | Demonstrates the dataset continues to be actively used in 2024 fault localization studies — proving ongoing relevance. Also reveals that Defects4J has grown to **864 artifacts** across multiple Java projects.                                            |
| SP1-C | **Durieux, T., Martinez, M., Monperrus, M., & Wuttke, J. (2018).** Automatic Repair of Real Bugs in Java: A Large-Scale Experiment on the Defects4J Dataset. _arXiv:1811.02429._        | Shows Defects4J being used at scale for APR experiments, cementing its status as the benchmark for empirical Java software engineering research.                                                                                                            |
| SP1-D | **Xuan, J., Monperrus, M., et al. (2017).** Better test cases for better automated program repair: A manual inspection of Defects4J bugs and its implications. _FSE 2017_, pp. 831–841. | Manual inspection study of 50 Defects4J bugs showing that the test-suite artifacts and bug-triggering tests in the dataset carry real diagnostic value — directly relevant to explaining the richness of Defects4J artifacts.                               |

### Opposing / Nuance Papers

| #      | Citation                                                             | Nuance to Acknowledge                                                                                                                                                       |
| ------ | -------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SP1-O1 | **Rafi et al. (2024)** (same as SP1-B)                               | 77% of fault-triggering tests embed post-hoc developer knowledge — meaning the dataset is not a perfect neutral benchmark. Acknowledging this strengthens your credibility. |
| SP1-O2 | Research Dimensions Doc — _Multi-fault variants of Defects4J (2024)_ | Real programs contain an average of 9.2 interacting faults per version; Defects4J's single-fault assumption is artificial.                                                  |

---

## Story Point 2 — Importance of Bug/Defect Categorization in the SDLC

### Supporting Papers

| #     | Citation                                                                                                                                                                                                  | Key Claim Supported                                                                                                                                                                                                                       |
| ----- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SP2-A | **Catolino, G., Palomba, F., Zaidman, A., & Ferrucci, F. (2019).** Not all bugs are the same: Understanding, characterizing, and classifying bug types. _Journal of Systems and Software, 153_, pp. 1–18. | Directly proves that different bug types behave differently and require different resolution strategies — categorization is not cosmetic but operationally necessary for optimizing the debugging process.                                |
| SP2-B | **Andrade, R., Teixeira, C., Laranjeiro, N., & Vieira, M. (2025).** An Empirical Study on the Classification of Bug Reports with Machine Learning. _arXiv:2503.00660._                                    | Recent empirical evidence that automated bug report classification directly improves triage and maintenance efficiency — supporting the claim that categorization optimizes the process.                                                  |
| SP2-C | **Hirsch, T., & Hofer, B. (2022).** Using textual bug reports to predict the fault category of software bugs. _Array, 15_, 100189.                                                                        | Demonstrates the practical value of early fault categorization: predicting the fault category from a bug report helps developers prioritize and allocate resources before even looking at the code.                                       |
| SP2-D | **Chillarege, R., et al. (1992).** Orthogonal Defect Classification — A Concept for In-Process Measurements. _IEEE Transactions on Software Engineering, 18_(11), pp. 943–956.                            | The original ODC paper explicitly argues that structured defect categorization provides actionable, in-process measurement for managers and developers alike — directly supporting the "categorization helps optimize the process" claim. |

### Opposing / Nuance Papers

| #      | Citation                                  | Nuance                                                                                                                                                       |
| ------ | ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| SP2-O1 | **Andrade et al. (2025)** (same as SP2-B) | ML-based classification accuracy remains imperfect; human labeling remains the gold standard but is too expensive at scale. This gap sets up your LLM angle. |

---

## Story Point 3 — Existing Attempts at Classifying Defects4J

### Supporting Papers

| #     | Citation                                                                                                                                                                         | Key Claim Supported                                                                                                                                                                                                                                              |
| ----- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SP3-A | **Van der Spuy, A., & Fischer, B. (2025).** An Anatomy of 488 Faults from Defects4J Based on the Control- and Data-Flow Graph Representations of Programs. _arXiv:2502.02299._   | The most recent and direct CFG-based classification of Defects4J — manually classifies 488 bugs into 6 control-flow and 2 data-flow classes. This is the primary existing classification attempt you need to position against.                                   |
| SP3-B | **Sobreira, V., Durieux, T., Madeiral, F., Monperrus, M., & Maia, M. A. (2018).** Dissection of a Bug Dataset: Anatomy of 395 Patches from Defects4J. _SANER 2018_, pp. 130–140. | First systematic classification of Defects4J patches (v1.2, 395 bugs), manually extracting repair actions and repair patterns (e.g., 43% involve conditional block changes). Provides the only existing human-labelled patch taxonomy — and it only covers v1.2. |
| SP3-C | **Xuan, J., Monperrus, M., et al. (2017).** (same as SP1-D)                                                                                                                      | A manual inspection of 50 randomly selected Defects4J bugs, identifying fixability patterns. A small-sample classification exercise that shows what careful manual analysis reveals.                                                                             |

> **Note for slides:** These three papers collectively represent: (1) a structural/graph-based classification (Van der Spuy 2025), (2) a patch-level classification by repair action (Sobreira 2018), and (3) a small-sample fixability study (Xuan 2017). None of them apply a **semantic, root-cause taxonomy** like ODC to the full dataset.

---

## Story Point 4 — Limitations of Existing Classification Approaches

### Supporting Papers

| #     | Citation                                          | Limitation Exposed                                                                                                                                                                                                                                  |
| ----- | ------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SP4-A | **Sobreira et al. (2018)** (same as SP3-B)        | Only covers 395 bugs from Defects4J **v1.2**. The current dataset has 864+ entries. No complete labeling of the full dataset has ever been performed. The taxonomy is patch-structural, not semantic/root-cause.                                    |
| SP4-B | **Van der Spuy & Fischer (2025)** (same as SP3-A) | Covers 488 bugs across 7 projects — still not the full Defects4J dataset. Taxonomy is grounded in CFG/DFG structure, which captures **how** bugs manifest syntactically, but not **why** they exist semantically (no context-aware classification). |
| SP4-C | **Xuan et al. (2017)** (same as SP1-D)            | Explicitly limited to a random sample of 50 bugs — the paper itself acknowledges this as a significant threat to external validity.                                                                                                                 |
| SP4-D | **Rafi et al. (2024)** (same as SP1-B)            | Reveals systemic bias in existing test artifacts — meaning any automated labeling pipeline that relies on test execution traces alone will inherit this bias, underscoring the need for context-aware, test-independent classification like ODC.    |
| SP4-E | **Andrade et al. (2025)** (same as SP2-B)         | ML-based classification of bug reports relies on labeled training data — which Defects4J lacks in any complete form. Without ground-truth ODC labels, traditional ML pipelines cannot be trained reliably.                                          |

### Key Gap Statement (synthesized from above)

> No study has ever fully labeled all bugs in the Defects4J dataset. Existing studies either cover a small subset (50–488 bugs), use structural-only taxonomies (CFG/DFG), classify repair actions rather than root causes, or require post-fix code that prevents pre-triage use. There exists no context-aware, semantically-grounded, scalable classification of the full Defects4J dataset.

> Beyond coverage limitations, current classification paradigms fail to provide actionable insights for real-world software development. Structural and patch-based taxonomies describe _how_ a bug manifests in code, but do not explain _why_ it occurred or _how it should be addressed_. As a result:
>
> - Developers cannot easily infer the underlying cause of a defect or determine an appropriate fix strategy.
> - The classifications do not map to development lifecycle activities (design, coding, testing), limiting their usefulness for process improvement.
> - Labels are often too low-level (syntactic patterns) or too inconsistent (ad hoc ML categories) to support decision-making in triage, debugging, or quality assurance workflows.
>
> In essence, existing approaches produce _descriptive_ rather than _diagnostic_ classifications. They capture surface-level characteristics of defects but fail to encode the semantic, process-oriented insights required in practice. This gap motivates the need for a principled, context-aware taxonomy—such as Orthogonal Defect Classification (ODC)—that aligns defect categorization with real-world development and management needs.

---

## Story Point 5 — Why LLM-Based Defect Categorization Is a Viable Path

### Supporting Papers

| #     | Citation                                                                                                                                                                                                    | Key Claim Supported                                                                                                                                                                                                                                     |
| ----- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SP5-A | **Colavito, G., Lanubile, F., Novielli, N., & Quaranta, L. (2024).** Large Language Models for Issue Report Classification. _Ital-IA 2024, CEUR Workshop Proceedings._                                      | Direct evidence that LLMs can classify issue reports (closely related to bug reports) effectively, validating the LLM-for-defect-classification hypothesis.                                                                                             |
| SP5-B | **Koyuncu, A. (2025).** Exploring fine-grained bug report categorization with large language models and prompt engineering: An empirical study. _ACM Transactions on Software Engineering and Methodology._ | Directly uses LLMs with prompt engineering (including few-shot prompting) to achieve **fine-grained** bug report categorization — the most directly relevant prior work to your approach.                                                               |
| SP5-C | **Nong, Y., et al. (2024).** Chain-of-Thought Prompting of Large Language Models for Discovering and Fixing Software Vulnerabilities. _arXiv:2402.17230._                                                   | Although focused on vulnerability analysis rather than bug categorization, it demonstrates that **CoT prompting** of LLMs improves classification accuracy by over 500% on structured tasks — validating CoT as a prompting strategy for your pipeline. |
| SP5-D | Research Dimensions Doc — _RCEGen: A Generative Approach for Automated Root Cause Analysis (2024)_                                                                                                          | Demonstrates that LLMs can generate structured, ODC-aligned root cause explanations from bug reports and stack traces — directly showing that LLMs can reason about semantic defect categories.                                                         |

### Opposing / Nuance Papers

| #      | Citation                                                             | Challenge to Acknowledge                                                                                                                                                       |
| ------ | -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| SP5-O1 | Research Dimensions Doc — _AutoODC (2011)_ and _Thung et al. (2012)_ | Earlier automated approaches using SVM/Naïve Bayes achieved only ~77–82% accuracy, struggled with sparse text. LLMs overcome these exact limitations — use this as motivation. |
| SP5-O2 | **Hirsch & Hofer (2022)** (same as SP2-C)                            | Text-based ML models for bug category prediction have fundamental limits without code context. LLMs are code-aware — this distinction is your key advantage.                   |

---

## Story Point 6 — Limitations of LLM-Driven Approach: The Taxonomy Problem

### Supporting Papers

| #     | Citation                                        | Limitation Exposed                                                                                                                                                                                                          |
| ----- | ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SP6-A | Research Dimensions Doc — _RCEGen (2024)_       | Explicitly notes that **LLMs hallucinate heavily** when deprived of concrete stack traces or a guiding structured taxonomy — motivating the need for ODC as a classification framework to constrain LLM outputs.            |
| SP6-B | **Koyuncu (2025)** (same as SP5-B)              | Even with prompt engineering, fine-grained classification without a rigorous taxonomy produces inconsistent categories — different LLM runs produce different category labels for the same bug.                             |
| SP6-C | Research Dimensions Doc — _Thung et al. (2012)_ | Without a standardized taxonomy, automated defect categorization collapses into either vague super-categories (control/data flow, structural, non-functional) or inconsistent labels that can't be compared across studies. |
| SP6-D | **Andrade et al. (2025)** (same as SP2-B)       | Machine learning bug classification studies suffer from a proliferation of incompatible taxonomies — proving that ad hoc classification without a principled framework (like ODC) yields unactionable results.              |

> **Transition to ODC:** A well-established, mathematically rigorous taxonomy is needed to constrain and guide the LLM. That taxonomy is ODC. This is your bridge to Story Point 7.

---

## Story Point 7 — What is ODC? Its Importance and Insights

### Supporting Papers

| #     | Citation                                                                                                                                                                                                           | Key Claim Supported                                                                                                                                                                                                                                                                                                                                         |
| ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SP7-A | **Chillarege, R., Bhandari, I. S., Chaar, J. K., Halliday, M. J., Moebus, D. S., Ray, B. K., & Wong, M.-Y. (1992).** Orthogonal Defect Classification — A Concept for In-Process Measurements. _IEEE TSE, 18_(11). | The foundational ODC paper. Defines the 8 orthogonal attributes (Type, Trigger, Impact, Target, Qualifier, Source, Age, Activity). Explains how tracking Defect Type provides a measurement of the development process model, while tracking Trigger measures testing effectiveness — directly addresses the "insights to management and developers" claim. |
| SP7-B | Research Dimensions Doc — _AutoODC (2011)_                                                                                                                                                                         | Validates ODC's industrial adoption and relevance 20 years after its inception — it was important enough that IBM Research invested in automating it.                                                                                                                                                                                                       |
| SP7-C | Research Dimensions Doc — _Ni et al. / Pan et al. (2024): Understanding Defects in Generated Codes by LLMs_                                                                                                        | Proves ODC remains viable even for AI-generated code in 2024 — the taxonomy is not obsolete; it generalizes beyond human-written software.                                                                                                                                                                                                                  |
| SP7-D | Research Dimensions Doc — _RCEGen (2024)_                                                                                                                                                                          | Shows that ODC attributes enable LLMs to generate structured root cause explanations (not just labels), demonstrating the framework's depth and utility for developers.                                                                                                                                                                                     |

---

## Story Point 8 — Why ODC is Suitable for Defects4J and How Artifacts Map to ODC

### Supporting Papers

| #     | Citation                                           | Key Claim Supported                                                                                                                                                                                                                                                                            |
| ----- | -------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SP8-A | **Just et al. (2014)** (same as SP1-A)             | Defects4J's per-bug artifacts — bug reports, triggering tests, buggy code, fixed code, and code diffs — provide exactly the multi-modal context that ODC attributes require for classification (Trigger from test, Type from code diff, Target from modified classes, Impact from bug report). |
| SP8-B | **Sobreira et al. (2018)** (same as SP3-B)         | The Defects4J Dissection project demonstrates that code diffs can be systematically analyzed for structural patterns — proving that automated extraction of ODC-relevant features from Defects4J artifacts is tractable.                                                                       |
| SP8-C | Research Dimensions Doc — _Chillarege (1992)_      | ODC's Defect Type (Assignment, Checking, Algorithm, Interface, etc.) and Defect Trigger (Unit Test, Function Test, etc.) map naturally to what Defects4J provides: the trigger is literally encoded in the failing test, and the type is inferable from the code diff.                         |
| SP8-D | Research Dimensions Doc — _Collector-Sahab (2023)_ | Demonstrates that augmenting static code diffs with runtime context improves diagnostic value — your pipeline can similarly combine static artifacts (diffs) with dynamic ones (test execution logs from Defects4J CLI) for richer ODC classification.                                         |

---

## Story Point 9 — Challenges: Evaluating the ODC Pipeline Without Ground-Truth Labels

### Supporting Papers

| #     | Citation                                                        | Challenge / Evaluation Strategy                                                                                                                                                                                                                                                           |
| ----- | --------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SP9-A | **Van der Spuy & Fischer (2025)** (same as SP3-A)               | Their CFG/DFG classification of 488 bugs can serve as a **partial ground-truth proxy** for evaluating your ODC pipeline — you can cross-validate ODC "Type" labels (especially control-flow vs. data-flow bugs) against their independently derived structural labels.                    |
| SP9-B | **Sobreira et al. (2018)** (same as SP3-B)                      | Their 395 manually labelled repair patterns for Defects4J v1.2 provide a second partial validation set. ODC's Defect Type should correlate with repair patterns (e.g., ODC "Checking" type bugs should map to Sobreira's "conditional block" repair patterns).                            |
| SP9-C | Research Dimensions Doc — _RCEGen (2024)_                       | Evaluates LLM-based root cause classification on Correctness, Clarity, and Depth of Reasoning metrics via human expert review — this rubric can be adapted for evaluating your ODC label quality when no ground truth exists.                                                             |
| SP9-D | Research Dimensions Doc — _AutoODC (2011), Thung et al. (2012)_ | These papers used small, industry-labeled ODC datasets as gold standards for training/evaluation. You can similarly perform a small-scale human annotation of a stratified sample (~50–100 bugs) as an evaluation subset.                                                                 |
| SP9-E | Research Dimensions Doc — _"Revisiting Defects4J" (2024)_       | Points to the data contamination problem — LLMs may have memorized some Defects4J solutions. Your evaluation must account for this by testing classification consistency across bugs from the less-common projects (Closure, JFreeChart) that are less likely to be in pre-training data. |

### Key Challenge Statement

> Since Defects4J has no complete ODC ground-truth labels, pipeline accuracy cannot be evaluated using traditional precision/recall metrics. Your strategy should involve: (1) partial validation against Sobreira 2018 and Van der Spuy 2025, (2) inter-rater human validation of a sample, and (3) qualitative evaluation of LLM reasoning depth à la RCEGen.

---

## Story Point 10 — The Inspiration: LLM-Driven Scientific Debugging as the Architectural Model

### Supporting Papers

| #      | Citation                                                                                                                                                        | Key Claim Supported                                                                                                                                                                                                                                                                          |
| ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SP10-A | **Kang, S., Chen, B., Yoo, S., & Lou, J.-G. (2023).** Explainable Automated Debugging via Large Language Model-driven Scientific Debugging. _arXiv:2304.02195._ | The direct inspiration paper. AutoSD automates Zeller's Hypothesize → Observe → Conclude cycle into an agentic LLM pipeline with live debugger feedback loops. You propose to similarly automate ODC classification into a structured, repeatable LLM pipeline rather than ad hoc prompting. |
| SP10-B | **Zeller, A. (2009).** _Why Programs Fail: A Guide to Systematic Debugging_ (2nd ed.). Morgan Kaufmann.                                                         | The original "Scientific Debugging" methodology that AutoSD formalizes. Citing this root source demonstrates depth of study and positions your pipeline as principled rather than heuristic.                                                                                                 |
| SP10-C | Research Dimensions Doc — _HAFixAgent (2025)_                                                                                                                   | Demonstrates that LLM agents interacting with Defects4J's compile/test CLI tools significantly outperform static inference — supporting an agent-based ODC pipeline that dynamically validates classifications through code execution.                                                       |
| SP10-D | Research Dimensions Doc — _Ni et al. (2024): Taxonomy on Software Defects for LLM Generation_                                                                   | Shows that feeding LLMs a structured taxonomy (ODC) and asking them to reason through defect classification step-by-step yields interpretable, evaluable outputs — aligning with the scientific methodology principle.                                                                       |

### How to Frame the Analogy on Slides

> Just as Kang et al. (2023) took Zeller's human scientific debugging workflow (hypothesize → observe → conclude) and encoded it into an LLM pipeline, **our approach takes Chillarege's ODC workflow** (identify trigger → classify type → assess impact) and encodes it into an LLM classification pipeline with structured prompting. The parallel is direct and defensible.

---

## Story Point 11 — Methodology: Pipeline Architecture and Implementation

> This is where the presentation transitions from **"why"** to **"how"**. Story Point 11 is multi-part and should be presented as a walkthrough of the pipeline with actual prompt/code screenshots.

---

### Story Point 11A — Evidence Collection Flow: Building `context.json`

#### What to Show on Slides

Show the **Evidence Collection Flow** diagram from `README.md`. Walk through each step and explain what data is collected, why it is necessary, and how it maps to ODC classification.

#### The `context.json` Structure — What We Collect and Why

| Evidence Field                                                                                      | Source                                          | Why It's Necessary for ODC Classification                                                                                                                         |
| --------------------------------------------------------------------------------------------------- | ----------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `project_id`, `bug_id`, `version_id`                                                                | `defects4j query`                               | Identity metadata — associates classification results to specific Defects4J bugs for reproducibility                                                              |
| `metadata` (report.id, report.url, revision.buggy, tests.trigger, tests.relevant, classes.relevant) | `defects4j query`                               | Rich contextual metadata — report.url enables bug report fetching; tests.trigger cross-references with parsed failures                                            |
| `hidden_oracles` (classes.modified)                                                                 | `defects4j query`                               | **Deliberately excluded** from LLM prompt — this is ground-truth oracle data. Sending it would cause data leakage and invalidate the pre-fix methodology          |
| `bug_info`                                                                                          | `defects4j info`                                | Root cause summary text from Defects4J — provides developer-written description of what the failing tests expose                                                  |
| `bug_report_content`                                                                                | JIRA / GitHub API / HTML fetch                  | The original bug report (title, description, priority, comments) — this is the **opener-side evidence** in ODC terms: what the reporter observed                  |
| `failures` (test_name, headline, stack_trace, frames)                                               | `defects4j test` → `failing_tests` parsing      | The **trigger evidence** — stack traces reveal WHERE the bug manifests, headlines reveal WHAT exception occurred                                                  |
| `suspicious_frames`                                                                                 | Filtered from `failures.frames`                 | Prioritized project source frames (framework/JDK/build-tool filtered out) — these are the **most diagnostic** stack locations                                     |
| `code_snippets` (production)                                                                        | Source files ±12 lines around suspicious frames | The actual **buggy code** — the LLM examines this to determine the root cause mechanism (wrong check? wrong value? wrong algorithm?)                              |
| `code_snippets` (test)                                                                              | Failing test method body ±18 lines              | Shows **expected behavior** — what the developer intended vs what happened. Critical for ODC Type inference                                                       |
| `coverage` (optional)                                                                               | `defects4j coverage` → Cobertura XML            | Line/branch execution rates for suspicious classes — helps identify which code paths are exercised by failing tests                                               |
| `exports` (dir.src.classes, dir.src.tests, cp.compile, cp.test)                                     | `defects4j export`                              | Source directory paths enabling code snippet extraction; classpaths stored for reference                                                                          |
| `fix_diff` (post-fix only)                                                                          | `difflib.unified_diff` of buggy→fixed classes   | **Post-fix oracle** — the actual code change. Only included when `--include-fix-diff` is set. Dramatically improves classification but breaks pre-fix methodology |
| `notes`                                                                                             | Pipeline runtime                                | Compilation/test exit codes, hidden oracle storage notes — contextual pipeline metadata                                                                           |

#### Pre-fix vs Post-fix Evidence Modes

| Aspect                         | Pre-fix Mode (default)                                                                           | Post-fix Mode (`--include-fix-diff`)                        |
| ------------------------------ | ------------------------------------------------------------------------------------------------ | ----------------------------------------------------------- |
| **Evidence available**         | Stack traces, failing tests, error messages, production/test code snippets, bug report, coverage | All of the above + the actual buggy→fixed diff              |
| **What the LLM sees**          | _Symptoms_ of the bug                                                                            | The _actual code change_ that fixes the bug                 |
| **Classification perspective** | Effect-oriented: "what went wrong?"                                                              | Cause-oriented: "what was changed?"                         |
| **Analogous to**               | A doctor diagnosing from symptoms                                                                | A pathologist with biopsy results                           |
| **ODC mapping**                | Opener-side reasoning (trigger, activity, impact)                                                | Closer-side reasoning (defect type, qualifier, age, source) |

#### Supporting Papers

| #       | Citation                          | Key Claim Supported                                                                                                                                                                                |
| ------- | --------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SP11A-A | **Just et al. (2014)** [1]        | Defects4J's per-bug artifacts (bug reports, triggering tests, buggy code, fixed code, diffs) provide exactly the multi-modal context that our pipeline consumes                                    |
| SP11A-B | **Sobreira et al. (2018)** [2]    | Demonstrates that Defects4J code diffs can be systematically analyzed for structural patterns — proving automated extraction of ODC-relevant features is tractable                                 |
| SP11A-C | **Rafi et al. (2024)** [3]        | 77% of fault-triggering tests embed post-hoc developer knowledge — our pipeline explicitly separates pre-fix evidence from post-fix oracle to acknowledge this                                     |
| SP11A-D | **Chillarege et al. (1992)** [12] | ODC's opener/closer model requires evidence from both "when the defect is opened" (symptoms) and "when the defect is fixed" (code change) — our dual-mode pipeline directly mirrors this structure |

> **Slide recommendation**: Show side-by-side screenshots of a real `context.json` (e.g., Cli-38) highlighting each evidence section. Use color-coding to show which parts map to ODC opener vs closer evidence.

---

### Story Point 11B — ODC Taxonomy Integration and System Prompt Design

#### What to Show on Slides

Show the **actual system prompt** text on slides. The audience should be able to read the ODC taxonomy, the few-shot examples, and the diagnostic questions directly.

#### The 7 ODC Defect Types (from `odc.py`)

Our pipeline encodes the full ODC defect type taxonomy from Chillarege (1992) as a structured Python dictionary, which is rendered into the system prompt at runtime:

| ODC Defect Type               | Family                | Summary                                                                     | Key Indicator                                            |
| ----------------------------- | --------------------- | --------------------------------------------------------------------------- | -------------------------------------------------------- |
| **Algorithm/Method**          | Control and Data Flow | Efficiency or correctness problems fixable by (re)implementing an algorithm | Wrong iteration, search logic, computational strategy    |
| **Assignment/Initialization** | Control and Data Flow | Values assigned incorrectly or not assigned at all                          | Wrong default, constant, or initialization               |
| **Checking**                  | Control and Data Flow | Missing or incorrect validation in conditional statements                   | Missing null check, wrong boundary, incorrect predicate  |
| **Timing/Serialization**      | Control and Data Flow | Missing/wrong serialization of shared resources                             | Race condition, wrong lock order, concurrency issues     |
| **Function/Class/Object**     | Structural            | Requires formal design-level capability correction                          | Major capability absent, significant design gap          |
| **Interface/O-O Messages**    | Structural            | Communication problems between modules/components                           | Wrong parameter order, type mismatch, contract violation |
| **Relationship**              | Structural            | Problems in associations among procedures/data/objects                      | Broken cross-entity consistency assumptions              |

Each type entry in our prompt includes:

- **Definition** (`summary`) — what the type means
- **When to choose** (`indicators`) — positive selection criteria
- **When NOT to choose** (`distinguish_from`) — contrastive boundary guidance
- **Examples** (`examples`) — concrete instances from ODC literature

> This contrastive design is critical — without "distinguish_from" guidance, LLMs tend to default to `Function/Class/Object` for any bug, as documented in our anti-bias rules.

#### ODC Opener/Closer Alignment Hints

Beyond the primary defect type, our prompt includes **heuristic ODC attribute hints** inferred from the evidence:

**Opener hints** (inferred from bug report text, failure headlines, stack trace keywords):

| Hint Field            | Possible Values                                                                                  | Derivation                                       |
| --------------------- | ------------------------------------------------------------------------------------------------ | ------------------------------------------------ |
| `activity_candidates` | Unit Test, Function Test, System Test                                                            | Keyword matching (integration, workload, stress) |
| `trigger_candidates`  | Test Variation, Test Sequencing, Test Interaction, Recovery/Exception, Workload/Stress, Coverage | Exception types, ordering keywords               |
| `impact_candidates`   | Reliability, Performance, Integrity/Security, Documentation, Capability                          | Crash/slow/security/doc tokens                   |

**Closer hints** (partially inferred from fix-diff shape when available):

| Hint Field       | Possible Values                | Derivation                                                                     |
| ---------------- | ------------------------------ | ------------------------------------------------------------------------------ |
| `target`         | Design/Code (always)           | Fixed for pipeline scope                                                       |
| `qualifier_hint` | Missing, Incorrect, Extraneous | Diff shape: added-only → Missing; removed-only → Extraneous; mixed → Incorrect |
| `age_hint`       | New, Base, Rewritten           | Diff size: ≥120 delta → Rewritten; large new block → New; else → Base          |

#### 5 Few-Shot Classification Examples (from `odc_doc.md`)

Our prompt includes 5 canonical few-shot examples derived from ODC literature patterns, each showing:

1. **Symptom** — what the test/error shows
2. **Code snippet** — what the buggy code looks like
3. **Classification** — the correct ODC type with reasoning
4. **NOT X** — explicit contrastive reasoning ("Why it is NOT Function/Class/Object")

| Example # | ODC Type                      | Symptom Pattern                              | Key Distinction                                                         |
| --------- | ----------------------------- | -------------------------------------------- | ----------------------------------------------------------------------- |
| 1         | **Checking**                  | NullPointerException, no null guard          | NOT Function/Class/Object — method exists, just lacks validation        |
| 2         | **Assignment/Initialization** | assertEquals fails, wrong initial value      | NOT Checking — no condition is wrong, the value itself is wrong         |
| 3         | **Algorithm/Method**          | Wrong numerical result, wrong array index    | NOT Assignment — not a wrong constant, it's wrong indexing logic        |
| 4         | **Interface/O-O Messages**    | Swapped fields after serialization           | NOT Algorithm — each component correct internally, mismatch at boundary |
| 5         | **Function/Class/Object**     | UnsupportedOperationException, unimplemented | NOT Algorithm — no wrong computation exists, capability is absent       |

#### Supporting Papers

| #       | Citation                          | Key Claim Supported                                                                                                                                               |
| ------- | --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SP11B-A | **Chillarege et al. (1992)** [12] | The foundational ODC paper — our 7 defect types, opener/closer structure, and attribute definitions are directly sourced from this work                           |
| SP11B-B | **Koyuncu (2025)** [11]           | Demonstrates that LLMs with prompt engineering (including few-shot) achieve fine-grained bug categorization — validates our few-shot approach                     |
| SP11B-C | **Nong et al. (2024)** [19]       | Chain-of-thought prompting improves LLM classification accuracy by >500% — our contrastive "NOT X" reasoning in examples serves the same purpose                  |
| SP11B-D | **Pan et al. (2024)** [17]        | Proves ODC taxonomy remains viable for LLM-driven classification in 2024 — the taxonomy generalizes beyond human-written software                                 |
| SP11B-E | **IBM ODC v5.2 (2013)** [20]      | The official ODC specification document that defines all 8 attributes, activity-trigger mappings, and closer categories — direct source for our taxonomy encoding |

> **Slide recommendation**: Show the actual rendered prompt text — the taxonomy section, one few-shot example, and the opener/closer hints. Use a monospace font block so the audience can read the exact prompt the LLM receives.

---

### Story Point 11C — Scientific Debugging Protocol: Strengthening ODC Classification

#### What to Show on Slides

Show the **Scientific Debugging Protocol** and the **7-Question Diagnostic Decision Tree** from the system prompt.

#### The Scientific Debugging Protocol (from `prompting.py`)

Our pipeline encodes Zeller's (2009) scientific debugging methodology into the LLM's system prompt as a 5-step structured reasoning process:

```
Step 1 — OBSERVE: Examine failure symptoms
  → What does the error message say?
  → What does the stack trace reveal about WHERE?
  → What does the test name tell you about WHAT?

Step 2 — HYPOTHESIZE: Form a specific root-cause hypothesis
  → Be specific about the MECHANISM (wrong condition? wrong value? wrong computation?)

Step 3 — PREDICT: What would we expect in code if hypothesis is correct?
  → Checking bug → missing/wrong if-condition or guard
  → Algorithm/Method bug → wrong iteration, formula, or procedure
  → Assignment/Initialization bug → wrong value or initialization

Step 4 — EXAMINE EVIDENCE: Look at code snippets
  → Do the snippets confirm or refute the hypothesis?
  → What specific lines support the classification?

Step 5 — CONCLUDE: Choose the ODC type matching the ROOT CAUSE mechanism
```

#### The 7-Question Diagnostic Decision Tree

After the scientific debugging protocol, the prompt includes a **structured diagnostic checklist** that the LLM must work through before classifying:

| Question # | Diagnostic Question                                                  | If YES → Consider             |
| ---------- | -------------------------------------------------------------------- | ----------------------------- |
| 1          | Is a condition/guard/validation missing or wrong?                    | **Checking**                  |
| 2          | Is a specific value, constant, or initialization wrong?              | **Assignment/Initialization** |
| 3          | Is the computational logic or procedure itself wrong?                | **Algorithm/Method**          |
| 4          | Is the problem at a component boundary or API interaction?           | **Interface/O-O Messages**    |
| 5          | Does the problem depend on execution order or timing?                | **Timing/Serialization**      |
| 6          | Is the issue centered on associations among related entities?        | **Relationship**              |
| 7          | Does the defect require a formal design-level capability correction? | **Function/Class/Object**     |

> **Key design choice**: Question 7 (Function/Class/Object) is deliberately placed **last** — this forces the LLM to consider all simpler explanations before defaulting to the "design gap" type. Our anti-bias rules in the system prompt explicitly warn: _"Do NOT default to Function/Class/Object. Most Defects4J bugs are in existing code that produces wrong results."_

#### The JSON Contract Schema

The LLM is required to return a structured JSON response containing:

| Field                                                       | Purpose                                      | Requirement                                                      |
| ----------------------------------------------------------- | -------------------------------------------- | ---------------------------------------------------------------- |
| `odc_type`                                                  | Primary classification                       | **Required** — must be one of 7 canonical names                  |
| `family`                                                    | Control and Data Flow or Structural          | Required (but canonicalized server-side, never trusted from LLM) |
| `confidence`                                                | 0.0–1.0 self-assessed confidence             | Required                                                         |
| `needs_human_review`                                        | Boolean flag for uncertain classifications   | Required                                                         |
| `observation_summary`                                       | Failure symptom description                  | Required — Step 1 output                                         |
| `hypothesis`                                                | Specific root-cause mechanism                | Required — Step 2 output                                         |
| `prediction`                                                | Expected code pattern                        | Required — Step 3 output                                         |
| `experiment_rationale`                                      | How evidence confirms/weakens hypothesis     | Required — Step 4 output                                         |
| `reasoning_summary`                                         | Why this type over alternatives              | Required — Step 5 output                                         |
| `evidence_used`                                             | Specific evidence items cited                | Required                                                         |
| `evidence_gaps`                                             | Missing or ambiguous evidence                | Required                                                         |
| `alternative_types`                                         | Other plausible types with rejection reasons | Required                                                         |
| `target`, `qualifier`, `age`, `source`                      | ODC closer attributes                        | Optional                                                         |
| `inferred_activity`, `inferred_triggers`, `inferred_impact` | ODC opener attributes                        | Optional                                                         |

#### Supporting Papers

| #       | Citation                        | Key Claim Supported                                                                                                                                                        |
| ------- | ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SP11C-A | **Kang et al. (2023)** [15]     | Direct inspiration — AutoSD automates Zeller's Hypothesize → Observe → Conclude cycle into an LLM pipeline. We encode the same structured reasoning for ODC classification |
| SP11C-B | **Zeller (2009)** [16]          | The original Scientific Debugging methodology — our 5-step protocol directly implements Zeller's observe → hypothesize → predict → experiment → conclude cycle             |
| SP11C-C | **Nong et al. (2024)** [19]     | CoT prompting improves classification accuracy by >500% on structured tasks — our diagnostic decision tree serves as a domain-specific chain-of-thought                    |
| SP11C-D | **RCEGen (2024)** [18]          | Demonstrates that LLMs generate structured, ODC-aligned root cause explanations when guided by a taxonomy — validates our structured prompt approach                       |
| SP11C-E | **Colavito et al. (2024)** [10] | LLMs can classify issue reports effectively — our scientific debugging protocol adds the structured reasoning layer that generic prompting lacks                           |

> **Analogy for slides**: "Just as Kang et al. (2023) took Zeller's human scientific debugging workflow and encoded it into an LLM pipeline for fault localization, **our approach takes Chillarege's ODC workflow** (identify trigger → classify type → assess impact) and encodes it into an LLM classification pipeline with structured prompting."

---

### Story Point 11D — Classification Flow: LLM Integration and Validation

#### What to Show on Slides

Show the **Classification Flow** diagram from `README.md`. Walk through the LLM call, response parsing, validation, and canonical enforcement.

#### Multi-Provider LLM Architecture (`llm.py`)

Our pipeline supports three LLM providers through a unified abstraction:

| Provider              | API Transport                         | Authentication          | Key Feature                                                                                            |
| --------------------- | ------------------------------------- | ----------------------- | ------------------------------------------------------------------------------------------------------ |
| **Gemini** (default)  | `generateContent` REST API            | `x-goog-api-key` header | **Response JSON Schema** — Gemini natively enforces our classification schema, reducing parsing errors |
| **OpenRouter**        | OpenAI-compatible `/chat/completions` | Bearer token            | Access to 100+ models (Claude, GPT-4, Llama, etc.) via a single API                                    |
| **OpenAI-compatible** | Standard `/chat/completions`          | Bearer token            | Any OpenAI-compatible endpoint (local models, Azure, etc.)                                             |

#### Classification Pipeline Steps

```
1. Load context.json → BugContext object
2. Build system prompt:
   ├── ODC taxonomy with contrastive guidance
   ├── Anti-bias rules
   ├── Scientific debugging protocol (if style=scientific)
   ├── 7-question diagnostic tree (if style=scientific)
   ├── JSON contract schema
   └── 5 few-shot examples
3. Build user prompt:
   ├── Evidence mode declaration (pre-fix only / post-fix with diff)
   ├── Analysis rules
   └── Evidence payload (JSON):
       ├── project/bug/version identity
       ├── filtered metadata (classes.modified excluded)
       ├── bug_info text
       ├── bug_report_description
       ├── failing_tests + stack trace excerpts
       ├── suspicious_frames
       ├── production_code_snippets (up to 8)
       ├── test_code_snippets (up to 3)
       ├── coverage_summary
       ├── odc_opener_hints / odc_closer_hints
       └── fix_diff_oracle (if post-fix)
4. Call LLM API (with exponential backoff retry on 429/500/502/503)
5. Extract JSON from raw response (handles fenced code blocks, extra text)
6. Validate odc_type against 7 canonical names
7. Canonicalize family (NEVER trust LLM's family mapping)
8. Normalize optional ODC fields (trim, coerce lists)
9. Write classification.json + report.md
```

#### Key Design Decisions

| Decision                               | Rationale                                                                                                                  | Paper Support                                                            |
| -------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| **Temperature = 0.0**                  | Deterministic, reproducible classifications for scientific evaluation                                                      | Standard practice in structured classification tasks                     |
| **Schema-enforced responses (Gemini)** | Eliminates malformed JSON — the API guarantees schema compliance                                                           | Reduces post-hoc parsing errors compared to free-text extraction         |
| **Family canonicalized server-side**   | LLMs occasionally hallucinate family membership. We ALWAYS overwrite with `odc.family_for(odc_type)`                       | Ensures taxonomic consistency regardless of model behavior               |
| **Hidden oracle exclusion**            | `classes.modified` is ground-truth — including it in the prompt would let the LLM "cheat" by knowing which class was fixed | Maintains pre-fix methodology integrity [3]                              |
| **Retry on transient HTTP only**       | 429/500/502/503 are retried with exponential backoff + jitter; invalid JSON or invalid `odc_type` are NOT retried          | Distinguishes infrastructure failures from classification quality issues |
| **Two prompt styles**                  | `direct` (minimal + taxonomy) vs `scientific` (full debugging protocol) — allows experimental comparison                   | `scientific` is default; produces richer reasoning traces                |

#### Supporting Papers

| #       | Citation                        | Key Claim Supported                                                                                                                                                             |
| ------- | ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SP11D-A | **Koyuncu (2025)** [11]         | Demonstrates that prompt engineering (including structured schemas and few-shot examples) enables fine-grained LLM bug categorization                                           |
| SP11D-B | **Colavito et al. (2024)** [10] | Validates that LLMs can classify issue reports effectively across multiple categories                                                                                           |
| SP11D-C | **RCEGen (2024)** [18]          | LLMs hallucinate when deprived of structured taxonomy guidance — our schema enforcement and canonical validation prevent this                                                   |
| SP11D-D | **AutoODC (2011)** [13]         | Earlier automated ODC used SVM/Naïve Bayes achieving ~77-82% accuracy. LLMs with structured prompting overcome the sparse-text limitations that hindered those approaches       |
| SP11D-E | **Thung et al. (2012)** [14]    | Achieved 77.8% automatic defect categorization accuracy with post-fix code and ML — our LLM approach aims to match or exceed this with richer evidence and structured reasoning |

> **Slide recommendation**: Show the actual classification flow diagram. Highlight the anti-bias rules and canonical family enforcement as key quality assurance mechanisms.

---

## Story Point 12 — Analysis and Results

> **STATUS: PLACEHOLDER — Requires experimental data from study runs**

### Planned Content

#### 12A — Classification Distribution Analysis

- [ ] Distribution of ODC types across all classified bugs (histogram)
- [ ] Family-level distribution (Control and Data Flow vs Structural)
- [ ] Confidence distribution (high vs low confidence classifications)
- [ ] `needs_human_review` rate analysis

#### 12B — Pre-fix Classification Results

- [ ] Per-project ODC type distribution
- [ ] Most common type per project (e.g., does Math skew toward Algorithm/Method?)
- [ ] Confidence analysis by type (are some types harder to classify?)
- [ ] Evidence gaps analysis (what evidence is most commonly missing?)

#### 12C — Post-fix Classification Results

- [ ] Per-project ODC type distribution with fix-diff evidence
- [ ] Confidence improvement from pre-fix → post-fix
- [ ] Types that shift most frequently between modes

#### 12D — Pre-fix vs Post-fix Comparison Results

- [ ] Strict match rate (exact agreement)
- [ ] Top-2 match rate (alternative type overlap)
- [ ] Family match rate
- [ ] Cohen's Kappa
- [ ] Semantic distance distribution
- [ ] Divergence pattern breakdown (exact/soft/moderate/hard)
- [ ] Type confusion matrix
- [ ] Per-project comparison metrics

#### 12E — Qualitative Analysis

- [ ] Example walkthrough of 3-5 interesting bug classifications
- [ ] Show the LLM's reasoning chain (observation → hypothesis → prediction → conclusion)
- [ ] Highlight cases where scientific debugging protocol improved classification quality

> **Note**: These slides will be populated after completing the study runs (`study-plan` → `study-run` → `study-analyze`). The analysis framework is fully implemented — only the data needs to be generated.

---

## Story Point 13 — Evaluation Defence: Why Pre-fix ≠ Post-fix is Scientifically Expected

### What to Present

This story point directly draws from the `Eval Defence.md` document. The core question to address:

> **"If our pipeline classifies the same bug differently in pre-fix and post-fix modes, does that mean our pipeline is wrong?"**
>
> **Answer: No.** Classification divergence is _expected_, _explainable_, and fully consistent with ODC literature.

### The Three Pillars of Defence

#### Pillar 1: Evidence Asymmetry

Pre-fix and post-fix operate on **fundamentally different evidence bases**.

| Aspect          | Pre-fix (Symptoms)                          | Post-fix (Cause)               |
| --------------- | ------------------------------------------- | ------------------------------ |
| Evidence        | Stack traces, failing tests, error messages | All of above + actual fix diff |
| LLM perspective | "What went wrong?"                          | "What was changed?"            |
| ODC alignment   | Opener-side reasoning                       | Closer-side reasoning          |

**Example**: A `NullPointerException` might suggest **Checking** (missing null guard) from symptoms, but the fix reveals the entire data retrieval approach was wrong → **Algorithm/Method**. Both are _correct from their evidence perspective_.

#### Pillar 2: ODC Boundary Ambiguity

Even human ODC experts disagree 20-30% of the time (Chillarege 1992). Known ambiguous type pairs include:

| Type A                | Type B                    | Ambiguity                                                       |
| --------------------- | ------------------------- | --------------------------------------------------------------- |
| Algorithm/Method      | Checking                  | Missing boundary check: "checking" issue or "algorithmic" flaw? |
| Algorithm/Method      | Assignment/Initialization | Wrong value: "assignment" bug or flawed "algorithm"?            |
| Function/Class/Object | Interface/O-O Messages    | Missing capability: "design" gap or "contract" mismatch?        |

**Literature benchmark**: Thung et al. (2012) achieved 77.8% with post-fix code + ML. Expecting 100% agreement would be **scientifically unreasonable**.

#### Pillar 3: Multi-Fault Reality

Defects4J's "single-fault" assumption is artificial. Callaghan (2024) proved:

- **Average co-existing faults per version: ~9.2**
- Pre-fix sees symptoms from ALL co-existing faults mixed together
- Post-fix sees the diff for ONE specific fault fix
- Result: they classify _different facets_ of the same multi-fault landscape

### The Multi-Tier Accuracy Framework

| Tier | Metric            | Interpretation                       | Expected Rate                      |
| ---- | ----------------- | ------------------------------------ | ---------------------------------- |
| 1    | **Strict Match**  | Exact odc_type agreement             | 40-60%                             |
| 2    | **Top-2 Match**   | Primary or alternative_types overlap | 60-80% cumulative                  |
| 3    | **Family Match**  | Same ODC family (C&DF / Structural)  | 70-90% cumulative                  |
| 4    | **Cohen's Kappa** | Statistical inter-rater agreement    | κ ≥ 0.50 (moderate to substantial) |

### Extended Analysis Layers

| Layer | Metric                          | What It Measures                                                            |
| ----- | ------------------------------- | --------------------------------------------------------------------------- |
| A     | **Semantic Distance** (0.0–1.0) | Quantitative distance between ODC types in taxonomy structure               |
| B     | **Evidence Asymmetry Analysis** | Structured explanation of WHY pre-fix ≠ post-fix with literature references |
| C     | **Attribute Concordance**       | Agreement on target/qualifier/age/source beyond primary type                |
| D     | **Divergence Pattern**          | Categorizes as exact-match / soft / moderate / hard divergence              |
| E     | **Insight Generation**          | Human-readable analysis strings per comparison                              |

### Current Evaluation Approaches and Their Limitations

| Approach                                    | Papers                                    | Limitation                                                                        | How We Address It                                                                              |
| ------------------------------------------- | ----------------------------------------- | --------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| **Traditional accuracy (precision/recall)** | Thung 2012 [14], AutoODC 2011 [13]        | Requires complete ground-truth labels — Defects4J has none                        | Multi-tier framework that doesn't require ground truth                                         |
| **Human expert labeling**                   | Chillarege 1992 [12], Sobreira 2018 [2]   | Expensive, limited to small samples (50-488 bugs), inherent disagreement (20-30%) | LLM pipeline scales to full dataset; our evaluation acknowledges the same disagreement ceiling |
| **Patch-structural classification**         | Van der Spuy 2025 [4], Sobreira 2018 [2]  | Captures HOW bugs manifest syntactically, not WHY they exist semantically         | ODC captures root-cause semantics, not just structural patterns                                |
| **ML-based classification**                 | Andrade 2025 [8], Hirsch & Hofer 2022 [9] | Requires labeled training data (Defects4J lacks complete ODC labels)              | Zero-shot/few-shot LLM approach requires no training data                                      |
| **Single-metric evaluation**                | Most prior work                           | Binary match/no-match loses nuance                                                | Semantic distance + divergence patterns + attribute concordance                                |

### Supporting Papers

| #      | Citation                              | Key Claim Supported                                                                                                                                                                     |
| ------ | ------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SP13-A | **Chillarege et al. (1992)** [12]     | ODC was designed for statistical patterns, not per-bug ground truth. Human inter-rater agreement is ~70-80% — our multi-tier framework respects this ceiling                            |
| SP13-B | **Thung et al. (2012)** [14]          | Achieved 77.8% accuracy with ML + post-fix code — establishes the accuracy ceiling for automated ODC. Our semantic distance metric is calibrated from this work                         |
| SP13-C | **Callaghan (2024)** [21]             | defects4j-mf proves ~9.2 co-existing faults per D4J version — invalidates "single-fault" assumption and scientifically explains multi-fault contamination of pre-fix evidence           |
| SP13-D | **Kang et al. (2023)** [15]           | AutoSD demonstrated that scientific debugging produces different hypotheses depending on available evidence — validates that evidence asymmetry produces expected divergence, not error |
| SP13-E | **Landis & Koch (1977)** [22]         | Standard interpretation scale for Cohen's Kappa: κ ≥ 0.61 is "substantial agreement" — the accepted threshold in defect classification research                                         |
| SP13-F | **Van der Spuy & Fischer (2025)** [4] | Their CFG/DFG classification provides a partial ground-truth proxy — we can cross-validate ODC labels against independently derived structural labels                                   |
| SP13-G | **Sobreira et al. (2018)** [2]        | Their 395 repair pattern labels for D4J v1.2 provide a second partial validation set — ODC types should correlate with repair patterns                                                  |

> **Slide recommendation**: Present the "Three Pillars of Defence" as a visual diagram. Show the multi-tier accuracy framework as a stacked bar chart. Include the Cli-38 example from Eval Defence.md as a concrete walkthrough.

### Thesis Defence Talking Points

1. **"We don't expect 100% agreement."** Even human ODC experts disagree 20-30% of the time.
2. **"Pre-fix and post-fix are two valid perspectives."** Like symptom-based vs biopsy-confirmed diagnosis.
3. **"Multi-fault reality makes single-bug accuracy misleading."** When a version has 9+ faults, pre-fix and post-fix see different defect landscapes.
4. **"Our framework measures what matters."** Semantic distance and divergence patterns tell a richer story than binary match/no-match.
5. **"The alternative types prove the LLM understands ambiguity."** When alternative types in pre-fix include the post-fix primary, the model correctly identified the type boundary.

---

## Story Point 14 — Limitations

### What to Present

Honest acknowledgment of limitations strengthens the thesis — it shows scientific maturity.

#### Limitation 1: No Complete Ground-Truth ODC Labels for Defects4J

- Defects4J has **never** been fully labeled with ODC categories by human experts
- Our evaluation relies on pre-fix vs post-fix comparison (self-consistency), not against an independent gold standard
- Partial cross-validation is possible via Van der Spuy 2025 (488 bugs, structural) and Sobreira 2018 (395 bugs, patch-level), but these use different taxonomies
- **Mitigation**: Our multi-tier accuracy framework (strict → top-2 → family → kappa) with extended analysis layers (semantic distance, divergence patterns) reduces dependence on ground truth and provides richer evaluation than binary accuracy

#### Limitation 2: LLM Sensitivity and Reproducibility

- LLM outputs can vary between models, API versions, and even identical re-runs due to non-deterministic decoding
- Temperature = 0.0 reduces but does not fully eliminate variability (provider-side batching, model updates)
- Different providers (Gemini vs OpenRouter) may classify the same bug differently due to architectural differences
- **Mitigation**: Deterministic temperature setting, canonical family enforcement (never trust LLM's family mapping), structured JSON schema enforcement via Gemini's `responseJsonSchema`

#### Limitation 3: Data Contamination Risk

- LLMs may have encountered Defects4J bugs, patches, and associated discussion in their pre-training corpora
- Particularly high risk for popular benchmark projects (Lang, Math) that appear in hundreds of APR/FL papers
- The LLM could "recognize" a bug from training data rather than genuinely classifying from the provided evidence
- **Mitigation**: Our pipeline uses pre-fix evidence only by default (no fix diff), lowering the signal overlap with training data; cross-project consistency checks can detect model-specific overfitting

#### Limitation 4: Heuristic Opener/Closer Hints

- ODC opener hints (activity, trigger, impact) are keyword-based heuristics derived from bug report text and failure headlines — they are not validated ODC classifications performed by trained human assessors
- Closer hints (qualifier, age) are inferred from diff shape (line counts, added-vs-removed ratio) — a rough structural proxy for what should be a semantic judgment
- The `source` hint is not currently inferred at all due to lack of reliable heuristic signals
- **Mitigation**: All hints are explicitly labeled as "heuristic candidates" in the prompt, and the LLM is instructed to accept, modify, or reject them based on its own analysis

#### Limitation 5: Evidence Quality Variance Across Projects

- Not all Defects4J projects provide equally rich evidence — some have sparse bug reports, missing issue tracker URLs, or minimal test failure messages
- Stack trace depth and diagnostic value varies significantly (e.g., Closure's deeply nested compiler stack traces vs Lang's shallow utility class traces)
- Coverage collection can fail or produce incomplete data depending on project build configuration
- **Mitigation**: The pipeline gracefully handles missing evidence (empty fields default to `""` or `[]`), and the `evidence_gaps` field in classification output explicitly records what evidence was unavailable

#### Limitation 6: Scope Limited to Java and Defects4J

- Our pipeline is tightly coupled to Defects4J's Java project ecosystem — it cannot currently classify bugs from other languages or bug datasets
- The ODC taxonomy itself is language-agnostic, but our evidence collection (Java source parsing, stack frame filtering, JUnit test extraction) is Java-specific
- **Mitigation**: The classification logic (prompting, LLM call, validation) is language-independent — only the evidence collection layer would need adaptation for other ecosystems

#### Supporting Papers

| #      | Citation                      | Limitation Addressed                                                                                                       |
| ------ | ----------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| SP14-A | **Rafi et al. (2024)** [3]    | Data contamination risk — 77% of D4J fault-triggering tests embed post-hoc developer knowledge; LLMs may have seen these   |
| SP14-B | **Koyuncu (2025)** [11]       | LLM sensitivity — even with prompt engineering, fine-grained classification produces variability across runs and models     |
| SP14-C | **Andrade et al. (2025)** [8] | Ground truth gap — ML-based classification relies on labeled data that Defects4J lacks for ODC categories                   |
| SP14-D | **Chillarege et al. (1992)** [12] | Heuristic hints limitation — the original ODC standard requires trained human assessors for opener/closer classification; our heuristics approximate this |

---

## Story Point 15 — Future Work

### What to Present

These are specific, actionable extensions of **this thesis work** — not general research directions.

#### Future Work 1: Scale Classification to the Full Defects4J Dataset

- This thesis demonstrates the pipeline on a subset of Defects4J bugs. The natural next step is to run classification across **all 864+ active bugs** across all 17 projects
- This would produce the first complete ODC-labeled Defects4J dataset — a community resource currently nonexistent
- The pipeline infrastructure (batch `run`, `compare-batch`) is already built to support this scale
- **Validation requirement**: A stratified sample (e.g., 50 bugs across projects) would need human expert ODC annotation to calibrate agreement rates

#### Future Work 2: Multi-Model Consensus to Reduce LLM Sensitivity

- A direct extension of our pipeline's multi-provider architecture: classify each bug with **3+ models** (e.g., Gemini, GPT-4, Claude) and use majority voting or confidence-weighted ensemble
- This directly addresses **Limitation 2** (LLM sensitivity) identified in this thesis
- The pipeline already supports provider switching via `--provider` and `--model` flags — the infrastructure gap is only the consensus aggregation logic
- Prior work: Colavito et al. (2024) documented model-dependent classification variance that consensus could smooth

#### Future Work 3: Validated ODC Opener Classification

- This thesis focuses on the **closer-side** Defect Type classification with heuristic opener hints
- A natural extension is to implement validated Activity → Trigger mapping using Defects4J's test metadata (unit test vs integration test, test coverage patterns, trigger keywords)
- This would complete the full ODC workflow that Chillarege (1992) originally defined, enabling ODC-style process analysis (e.g., "which testing activity catches which defect type most effectively?")
- Addresses **Limitation 4** by replacing keyword heuristics with structured test metadata analysis

#### Future Work 4: ODC-Guided Automated Program Repair (APR) Strategy Selection

- The ODC type classification could directly inform APR tool selection: **Checking** bugs → conditional repair templates; **Assignment/Initialization** → value replacement patches; **Algorithm/Method** → more complex synthesis
- Defects4J is already the standard APR benchmark (Durieux 2018) — integrating our ODC labels could improve per-bug repair strategy selection rather than running all tools blindly
- This bridges our classification thesis with the APR community's need for bug-type-aware repair

#### Future Work 5: Extend Pipeline to Other Bug Datasets and Languages

- Validate whether the ODC classification approach generalizes beyond Defects4J by adapting the evidence collection layer for other Java datasets (Bears, BugSwarm, Bugs.jar) and potentially non-Java datasets
- The classification core (prompting, LLM call, ODC validation) is already language-independent — only `defects4j.py` and the stack frame parsing need adaptation
- This addresses **Limitation 6** and strengthens the external validity of the methodology

#### Supporting Papers

| #      | Citation                          | Future Direction Supported                                                                                                          |
| ------ | --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| SP15-A | **Colavito et al. (2024)** [10]   | Multi-model consensus — documented model-dependent classification variance that our consensus mechanism would address               |
| SP15-B | **Chillarege et al. (1992)** [12] | Validated opener classification — original ODC paper defines the complete Activity → Trigger process model our thesis could fulfill |
| SP15-C | **Durieux et al. (2018)** [5]     | APR integration — D4J is the standard APR benchmark; our ODC labels could guide per-bug repair strategy selection                    |
| SP15-D | **Hirsch & Hofer (2022)** [9]     | Full-scale labeling — early fault categorization improves developer prioritization; a complete D4J ODC dataset enables this          |
| SP15-E | **Catolino et al. (2019)** [7]    | Cross-dataset generalization — different bug types need different strategies; validating across datasets strengthens our claims      |

---

## Story Point 16 — Conclusion

### Key Messages for Final Slide

1. **Research Gap Addressed**: No prior study has applied ODC taxonomy to Defects4J bugs using LLM-driven classification with a scientific debugging protocol — our thesis fills this gap
2. **Pipeline Contribution**: A fully automated, end-to-end pipeline that collects multi-modal evidence from Defects4J, constructs structured ODC-constrained prompts, and produces interpretable, machine-readable classifications
3. **Methodological Innovation**: Encoding Chillarege's ODC opener/closer workflow into Zeller's scientific debugging protocol creates a principled, explainable classification approach — each classification includes a full reasoning trace (observation → hypothesis → prediction → experiment → conclusion)
4. **Evaluation Framework**: Multi-tier accuracy evaluation (strict → top-2 → family → kappa) with extended analysis layers (semantic distance, evidence asymmetry, divergence patterns, multi-fault context) provides scientifically grounded assessment that respects the inherent ~20-30% human disagreement ceiling in ODC
5. **Practical Impact**: The pipeline demonstrates that pre-fix ODC classification — without seeing the fix — is feasible, acknowledging multi-fault reality and evidence asymmetry rather than treating divergence as failure

### Closing Statement

> "Our work demonstrates that LLM-driven scientific debugging, constrained by the ODC taxonomy, can produce interpretable and defensible bug classifications from pre-fix evidence alone. The divergence between pre-fix and post-fix classifications is not a flaw — it is a scientifically expected consequence of evidence asymmetry, ODC boundary ambiguity, and multi-fault reality. Our multi-tier evaluation framework measures what matters: not whether two evidence perspectives agree perfectly, but whether the classifications are taxonomically consistent and diagnostically useful."

---

## Complete Reference List (Slide-Ready Format)

> Use these in your Reference slide(s). Numbered for in-text citation [1], [2], etc.

**[1]** Just, R., Jalali, D., & Ernst, M. D. (2014). Defects4J: A database of existing faults to enable controlled testing studies for Java programs. _ISSTA 2014_, ACM, pp. 437–440.

**[2]** Sobreira, V., Durieux, T., Madeiral, F., Monperrus, M., & Maia, M. A. (2018). Dissection of a Bug Dataset: Anatomy of 395 Patches from Defects4J. _IEEE SANER 2018_, pp. 130–140.

**[3]** Rafi, M. N., Chen, A. R., Chen, T.-H. P., & Wang, S. (2024). Revisiting Defects4J for Fault Localization in Diverse Development Scenarios. _arXiv:2402.13040_.

**[4]** Van der Spuy, A., & Fischer, B. (2025). An Anatomy of 488 Faults from Defects4J Based on the Control- and Data-Flow Graph Representations of Programs. _arXiv:2502.02299_.

**[5]** Durieux, T., Martinez, M., Monperrus, M., & Wuttke, J. (2018). Automatic Repair of Real Bugs in Java: A Large-Scale Experiment on the Defects4J Dataset. _arXiv:1811.02429_.

**[6]** Xuan, J., Monperrus, M., et al. (2017). Better test cases for better automated program repair: A manual inspection of Defects4J bugs and its implications. _FSE 2017_, ACM, pp. 831–841.

**[7]** Catolino, G., Palomba, F., Zaidman, A., & Ferrucci, F. (2019). Not all bugs are the same: Understanding, characterizing, and classifying bug types. _Journal of Systems and Software, 153_, pp. 1–18.

**[8]** Andrade, R., Teixeira, C., Laranjeiro, N., & Vieira, M. (2025). An Empirical Study on the Classification of Bug Reports with Machine Learning. _arXiv:2503.00660_.

**[9]** Hirsch, T., & Hofer, B. (2022). Using textual bug reports to predict the fault category of software bugs. _Array, 15_, 100189.

**[10]** Colavito, G., Lanubile, F., Novielli, N., & Quaranta, L. (2024). Large Language Models for Issue Report Classification. _Ital-IA 2024_, CEUR Workshop Proceedings.

**[11]** Koyuncu, A. (2025). Exploring fine-grained bug report categorization with large language models and prompt engineering: An empirical study. _ACM Transactions on Software Engineering and Methodology_.

**[12]** Chillarege, R., et al. (1992). Orthogonal Defect Classification — A Concept for In-Process Measurements. _IEEE Transactions on Software Engineering, 18_(11), pp. 943–956.

**[13]** Huang, B., & Ng, V., et al. (2011). AutoODC: Automated generation of Orthogonal Defect Classifications. _ASE 2011_.

**[14]** Thung, F., Lo, D., et al. (2012). Automatic Defect Categorization. _WCRE 2012_. (ink.library.smu.edu.sg/sis_research/1681/)

**[15]** Kang, S., Chen, B., Yoo, S., & Lou, J.-G. (2023). Explainable Automated Debugging via Large Language Model-driven Scientific Debugging. _arXiv:2304.02195_.

**[16]** Zeller, A. (2009). _Why Programs Fail: A Guide to Systematic Debugging_ (2nd ed.). Morgan Kaufmann.

**[17]** Pan, X., et al. (2024). Understanding Defects in Generated Codes by Language Models. _CASCON 2024_. (arXiv:2408.13372)

**[18]** Gao, X., et al. (2024). RCEGen: A Generative Approach for Automated Root Cause Analysis. _MDPI Computers, 4_(4), 29.

**[19]** Nong, Y., et al. (2024). Chain-of-Thought Prompting of Large Language Models for Discovering and Fixing Software Vulnerabilities. _arXiv:2402.17230_.

**[20]** IBM. (2013). Orthogonal Defect Classification v 5.2 for Software Design and Code. _IBM Research._

**[21]** Callaghan, D. (2024). Mining Bug Repositories for Multi-Fault Programs. _defects4j-mf, GitHub._

**[22]** Landis, J. R. & Koch, G. G. (1977). The Measurement of Observer Agreement for Categorical Data. _Biometrics, 33_(1), pp. 159–174.

---

## Quick Cross-Reference: Which Papers Support Which Story Points

| Paper                   | SP1 | SP2 | SP3 | SP4 | SP5 | SP6 | SP7 | SP8 | SP9 | SP10 | SP11 | SP12 | SP13 | SP14 | SP15 | SP16 |
| ----------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---- | ---- | ---- | ---- | ---- | ---- | ---- |
| Just 2014 [1]           | ✅  |     |     |     |     |     |     | ✅  |     |      | ✅   |      |      |      |      |      |
| Sobreira 2018 [2]       |     |     | ✅  | ✅  |     |     |     | ✅  | ✅  |      | ✅   |      | ✅   |      |      |      |
| Rafi 2024 [3]           | ✅  |     |     | ✅  |     |     |     |     | ✅  |      | ✅   |      |      | ✅   |      |      |
| Van der Spuy 2025 [4]   |     |     | ✅  | ✅  |     |     |     |     | ✅  |      |      |      | ✅   |      |      |      |
| Durieux 2018 [5]        | ✅  |     |     |     |     |     |     |     |     |      |      |      |      |      | ✅   |      |
| Xuan 2017 [6]           | ✅  |     | ✅  | ✅  |     |     |     |     |     |      |      |      |      |      |      |      |
| Catolino 2019 [7]       |     | ✅  |     |     |     |     |     |     |     |      |      |      |      |      | ✅   |      |
| Andrade 2025 [8]        |     | ✅  |     | ✅  |     | ✅  |     |     |     |      |      |      |      | ✅   |      |      |
| Hirsch & Hofer 2022 [9] |     | ✅  |     |     | ✅  |     |     |     |     |      |      |      |      |      | ✅   |      |
| Colavito 2024 [10]      |     |     |     |     | ✅  |     |     |     |     |      | ✅   |      |      |      | ✅   |      |
| Koyuncu 2025 [11]       |     |     |     |     | ✅  | ✅  |     |     |     |      | ✅   |      |      | ✅   |      |      |
| Chillarege 1992 [12]    |     | ✅  |     |     |     |     | ✅  | ✅  | ✅  |      | ✅   |      | ✅   | ✅   | ✅   | ✅   |
| AutoODC 2011 [13]       |     |     |     |     |     | ✅  | ✅  |     | ✅  |      | ✅   |      |      |      |      |      |
| Thung 2012 [14]         |     |     |     |     |     | ✅  |     |     | ✅  |      | ✅   |      | ✅   |      |      |      |
| Kang 2023 [15]          |     |     |     |     |     |     |     |     |     | ✅   | ✅   |      | ✅   |      |      |      |
| Zeller 2009 [16]        |     |     |     |     |     |     |     |     |     | ✅   | ✅   |      |      |      |      |      |
| Pan 2024 [17]           |     |     |     |     |     |     | ✅  |     |     | ✅   | ✅   |      |      |      |      |      |
| RCEGen 2024 [18]        |     |     |     |     | ✅  | ✅  | ✅  |     | ✅  |      | ✅   |      |      |      |      |      |
| Nong 2024 [19]          |     |     |     |     | ✅  |     |     |     |     |      | ✅   |      |      |      |      |      |
| IBM ODC v5.2 [20]       |     |     |     |     |     |     |     |     |     |      | ✅   |      |      |      |      |      |
| Callaghan 2024 [21]     |     |     |     |     |     |     |     |     |     |      |      |      | ✅   |      |      |      |
| Landis & Koch 1977 [22] |     |     |     |     |     |     |     |     |     |      |      |      | ✅   |      |      |      |


---

## Story Point Flow Summary

| SP#    | Title                                    | Key Message                                                                     | Primary Papers                        |
| ------ | ---------------------------------------- | ------------------------------------------------------------------------------- | ------------------------------------- |
| 1      | Introduction to Defects4J                | What it is, its artifacts, and continued relevance                              | [1], [3], [5], [6]                    |
| 2      | Importance of Bug Categorization         | Why categorization matters in SDLC                                              | [7], [8], [9], [12]                   |
| 3      | Existing Classification Attempts         | What has been done (structural, patch-level)                                    | [2], [4], [6]                         |
| 4      | Limitations of Existing Approaches       | Coverage gaps, structural-only, no root-cause                                   | [2], [4], [6], [8]                    |
| 5      | LLM-Based Classification is Viable       | LLMs can classify bugs with prompt engineering                                  | [10], [11], [19]                      |
| 6      | The Taxonomy Problem                     | LLMs need structured taxonomy to avoid hallucination                            | [11], [13], [14], [18]                |
| 7      | What is ODC?                             | 8 orthogonal attributes, scientifically grounded                                | [12], [17], [18]                      |
| 8      | ODC + Defects4J Mapping                  | D4J artifacts map naturally to ODC attributes                                   | [1], [2], [12]                        |
| 9      | Evaluation Challenges                    | No ground truth, need multi-modal validation                                    | [4], [12], [14], [18]                 |
| 10     | Scientific Debugging Inspiration         | AutoSD → ODC pipeline analogy                                                   | [15], [16]                            |
| **11** | **Methodology: Pipeline Implementation** | **Evidence collection, ODC prompts, scientific debugging, classification flow** | **[1], [11], [12], [15], [16], [19]** |
| **12** | **Analysis and Results**                 | **Classification distributions, comparison metrics**                            | **(placeholder — data needed)**       |
| **13** | **Evaluation Defence**                   | **Why divergence is expected, 3 pillars, multi-tier framework**                 | **[12], [14], [15], [21], [22]**      |
| **14** | **Limitations**                          | **No ground truth, LLM sensitivity, data contamination, heuristic hints, scope** | **[3], [8], [11], [12]**              |
| **15** | **Future Work**                          | **Full-scale labeling, multi-model consensus, opener validation, APR, cross-dataset** | **[5], [7], [9], [10], [12]**         |
| **16** | **Conclusion**                           | **Gap addressed, pipeline contribution, closing statement**                     | **[12], [15], [16]**                  |

---

_Generated for Network and Data Analysis Group (NDAG) Lab Thesis Pre-Defense 2026_
