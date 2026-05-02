# **Software Defect Classification: Bridging the Semantic Gap with Large Language Models and Scientific Debugging**

The integration of Orthogonal Defect Classification (ODC) with the Defects4J benchmark—mediated by an LLM-driven approach inspired by Andreas Zeller’s scientific debugging methodology—represents a profound advancement in automated defect analysis. Transitioning this framework from an exploratory academic thesis into a manuscript suitable for a premier, peer-reviewed Q1 venue such as the _Journal of Systems and Software_ (JSS) requires rigorous external validation. It demands a deep theoretical understanding of the taxonomy's historical evolution, the empirical validation of the pipeline's core claims against the broader software engineering literature, an analysis of JSS publication patterns, and the formulation of high-impact research questions. This report provides an exhaustive, multi-dimensional analysis of the theoretical underpinnings of the proposed pipeline, validates its architectural claims, analyzes opposing viewpoints present in the literature, and proposes an extensive roadmap and pool of research questions to guide the development of a gold-standard academic manuscript.

## **The Evolution of Orthogonal Defect Classification (1992–2026)**

To effectively position a manuscript for a premier software engineering journal, it is imperative to trace the historical evolution of the core taxonomy utilized in the research. Orthogonal Defect Classification (ODC) was introduced by Ram Chillarege and colleagues at IBM Research in 1992 as a transformative mechanism to extract in-process measurements directly from the software development life cycle. Unlike previous structural metrics that merely tracked the physical location of a fault (e.g., file or module), ODC was fundamentally designed to capture the semantic meaning of a defect—specifically, determining what was logically necessary to fix the problem from a programming perspective. The evolution of ODC over the past three and a half decades provides critical context for its modern application via LLMs.

### **Foundational Architecture and the IBM v5.2 Standard**

The original ODC framework categorized defects using highly structured attributes divided into "openers" (the conditions and activities present when the defect is discovered) and "closers" (the conditions surrounding the actual resolution and patching of the defect). The core defect types established early in the framework's history included Algorithm/Method, Assignment/Initialization, Checking, Timing/Serialization, Function/Class/Object, Interface/O-O Messages, and Relationship.

By 2013, IBM had formalized the ODC v5.2 standard, which refined these attributes to better suit the complexities of modern object-oriented software design. A pivotal enhancement in the v5.2 standard was the rigorous distinction between the "Impact" of a bug and its underlying "Type". The Impact attribute describes the observable effect the defect has on the customer or system environment, encompassing categories such as Capability, Usability, Reliability, Security, and crucially, Performance. Conversely, the Defect Type describes the actual semantic coding error that required modification.

This distinction addresses a frequent point of confusion in automated triage. For example, a bug report may describe a system freezing or degrading in response time, leading developers to intuitively label it a "performance bug." Under the ODC taxonomy, however, "Performance" is merely the Impact. The actual Defect Type might be an infinite loop caused by a missing conditional guard (categorized as Checking) or a concurrency deadlock (categorized as Timing/Serialization). An LLM trained to respect this ODC dichotomy is prevented from making superficial, symptom-based classifications, forcing it instead to parse the underlying semantic structure of the code.

### **The Transition to Automated and AI-Adapted Classification**

Conducting ODC classification manually requires deep domain expertise and is highly time-consuming, prompting early efforts to automate the process using traditional machine learning algorithms. Between 2011 and 2015, approaches such as AutoODC (Huang et al., 2011\) and the works of Thung et al. (2012) utilized Support Vector Machines (SVM) and Naive Bayes classifiers, achieving accuracies ranging from 75% to 82% on highly constrained datasets. However, these early ML techniques relied heavily on sparse textual data and term frequencies (TF-IDF), often struggling with the semantic nuances required to accurately map a complex Java patch to a single ODC category.

As the software engineering landscape evolved into the era of artificial intelligence, the ODC framework has been continuously adapted. By 2026, researchers have begun extending ODC to accommodate the specific defects inherent in AI and machine learning systems. Frameworks such as AIODC have introduced entirely new attributes—such as Data, Learning, and Thinking—to account for the unique failure modes of neural networks, proving the taxonomy's enduring flexibility. Understanding this evolution from a manual IBM mainframe protocol to an automated, AI-assisted taxonomy demonstrates that applying state-of-the-art LLMs to ODC is the logical, empirically sound next step in a decades-long methodological progression.

## **Architectural and Methodological Validation**

The proposed research pipeline utilizes a multi-modal approach to extract pre-fix and post-fix evidence from the Defects4J dataset, subsequently feeding this structured data into an LLM guided by a scientific debugging prompt. To justify this methodology for a top-tier peer-reviewed journal, the fundamental claims underlying the pipeline architecture must be corroborated by external literature, while opposing viewpoints must be rigorously analyzed and integrated into the validity threats of the study.

### **The Semantic Gap and Evidence Asymmetry**

A cornerstone of the proposed evaluation methodology is the comparative analysis of bug classification using "pre-fix" evidence (the symptoms and context available at the time of initial triage) versus "post-fix" evidence (the actual code changes implemented by a developer). The pipeline's architecture posits that a divergence in classification between these two temporal modes is not indicative of an algorithmic failure, but rather a reflection of inherent "evidence asymmetry".

This assertion is heavily validated by existing software engineering literature, which frequently discusses the "semantic gap" between bug reports and source code fixes. Bug reports, stack traces, and failing tests are inherently effect-oriented; they describe how a system deviated from its expected state at runtime. Conversely, a code commit is cause-oriented; it represents the precise syntactic restructuring required to eliminate the root defect. The literature on Traceability Link Recovery (TLR) emphasizes that bridging this semantic gap between high-level issue descriptions and low-level source code remains one of the most persistent challenges in software maintenance.

When an LLM evaluates a NullPointerException (NPE) in a pre-fix state, the absence of a null guard strongly points to an ODC "Checking" defect. However, post-fix analysis of the developer's diff might reveal that the variable was null because an entire data retrieval algorithm was flawed, categorizing the true root cause as an "Algorithm/Method" defect. By actively isolating pre-fix and post-fix evidence and acknowledging their distinct diagnostic value, the proposed methodology empirically measures the width of this semantic gap rather than collapsing it.

### **The Multi-Fault Reality of the Defects4J Benchmark**

Defects4J is universally recognized as the gold-standard benchmark for empirical software engineering, fault localization, and automated program repair (APR) studies. Traditionally, experimental designs utilizing Defects4J have operated under the simplifying assumption that each program version isolates a single, independent fault. However, the proposed pipeline challenges this by incorporating the understanding that these programs are actual, complex multi-fault environments.

This claim is strongly supported by recent empirical investigations. The introduction of datasets and analysis tools like `defects4j-mf` (Callaghan, 2024) has explicitly demonstrated that real-world software repositories rarely contain isolated defects, citing an average of 9.2 co-existing faults per version across major projects like Closure, Lang, and Math. The presence of multiple latent faults dictates that the symptoms observed during a system failure may be an amalgamation of interactions between several discrete bugs. Acknowledging this multi-fault reality is a significant methodological strength. It scientifically justifies why a purely symptom-based pre-fix classification might struggle to pinpoint the exact root cause of a specific patch, as the symptoms presented to the LLM are inherently contaminated by the noise of co-existing defects.

### **Addressing Opposing Views: Developer Knowledge in Triggering Tests**

While the methodology is sound, a submission to JSS must address opposing empirical findings that challenge the integrity of the dataset. A critical vulnerability in the pre-fix versus post-fix comparison lies in the nature of the triggering tests provided by the Defects4J benchmark.

Recent research has uncovered that Defects4J frequently includes test cases that were added _post-bug report_, specifically written by developers who already understood the root cause of the fault. Studies evaluating fault localization techniques have shown that 77% of fault-triggering tests in Defects4J contain embedded "developer knowledge" of the bug. This implies that the triggering tests analyzed in the "pre-fix" mode of the proposed pipeline are not truly representative of a raw, pre-triage state; they are artificially precise.

This opposing evidence must be integrated into the JSS manuscript, likely within the "Threats to Validity" section. It introduces a construct validity threat: the pre-fix classification may achieve artificially high accuracy because the triggering tests implicitly guide the LLM toward the correct code segment. Acknowledging this limitation—and discussing how the pipeline's aggressive filtering of framework classes attempts to mitigate it—demonstrates the rigorous academic maturity expected by Q1 journal reviewers.

### **The Multi-Tier Evaluation Framework and Inter-Rater Reliability**

Traditional machine learning classification tasks rely on strict accuracy metrics. However, the proposed research correctly argues that a binary "Strict Match" evaluation is fundamentally insufficient for ODC classification due to boundary ambiguities within the taxonomy. To resolve this, the pipeline implements a 4-tier evaluation strategy: Strict Match, Top-2 Match, Family Match, and Cohen’s Kappa, supplemented by Semantic Distance calculations.

External literature thoroughly validates this necessity. Chillarege's foundational work on ODC explicitly notes that human inter-rater agreement for defect classification generally peaks at 70% to 80% due to the subjective nature of interpreting developer intent. When senior software engineers cannot achieve perfect consensus on whether a complex patch represents an "Algorithm" flaw or an "Assignment" error, holding an LLM to a 100% strict match standard is empirically unsound. Furthermore, modern studies on automated defect categorization report maximum accuracies of around 77.8% even when fully utilizing post-fix data.

The use of Cohen’s Kappa is the academic standard for measuring inter-rater reliability, as it explicitly accounts for agreements that occur by chance. Achieving a 0.6+ denotes substantial agreement, providing a robust statistical foundation for the study's claims. Additionally, the concept of "Semantic Distance"—measuring how taxonomically related a misclassification is (e.g., confusing two types within the "Control and Data Flow" family versus confusing a structural design flaw with a timing error)—adds a sophisticated layer of qualitative analysis that distinguishes this research from standard automated classification studies.

## **Emulating Scientific Debugging through Large Language Models**

To prevent the LLM from hallucinating or generating transient, inconsistent ODC labels, the proposed pipeline employs a strict prompting strategy based on Andreas Zeller's scientific debugging methodology. Introduced in his seminal 2009 text _Why Programs Fail_, scientific debugging formalizes the inherently chaotic debugging process into a rigorous, verifiable loop: Hypothesize, Observe, Predict, Examine, and Conclude.

### **The AutoSD Framework and Cognitive Emulation**

The transition of this human-centric methodology into an LLM-driven architecture is highly supported by cutting-edge research, most notably the "AutoSD" (Automated Scientific Debugging) framework proposed by Kang et al. (2023–2025). The AutoSD framework successfully demonstrates that LLMs can emulate the cognitive processes of human developers. Rather than treating debugging as a purely statistical pattern-matching exercise, AutoSD prompts the LLM to generate explicit hypotheses about buggy code, formulate scripts to test those hypotheses, observe execution results, and arrive at logical conclusions prior to generating a patch.

The literature confirms that standard automated program repair (APR) techniques often rely on search-based heuristics or raw token probabilities that fail to identify true root causes, leading to patch overfitting and a lack of explainability. By contrast, prompting an LLM to follow a scientific deduction trace forces the model to ground its outputs in empirical evidence, bridging the gap between automated execution and human-readable rationales.

By adopting this scientific debugging protocol, the proposed ODC pipeline ensures that the LLM's classification logic is traceable. If the LLM misclassifies a bug, the researcher can examine the generated scientific trace to pinpoint exactly where the logical deduction failed—whether the model generated an incorrect hypothesis based on the stack trace, or whether it failed to predict the correct structural manifestation in the source code. This addresses the journal community's growing demand for Explainable AI (XAI) in software engineering tasks.

### **Toward Agentic Debugging Frameworks**

The user query notes that the current implementation utilizes a single hypothesize-observe loop, with aspirations to evolve into a fully agentic framework. This trajectory is perfectly aligned with the vanguard of 2025–2026 software engineering research.

Recent publications have introduced systems like InspectCoder and ChatDBG, which transition from static prompting into dynamic, multi-agent frameworks. InspectCoder, for example, utilizes a dual-agent architecture consisting of a "Program Inspector" that interactively probes the runtime environment, and a "Patch Coder" that synthesizes fixes based on the inspector's dynamic findings. Similarly, the Debug2Fix framework introduces a specialized debugging subagent that orchestrates actual debugger tools (like JDB) to gather complex runtime states. Highlighting this agentic future in the manuscript's "Future Work" section will demonstrate that the proposed ODC pipeline is situated at the forefront of the autonomous software engineering revolution.

## **Strategic Roadmap for JSS Manuscript Preparation**

Transitioning from a successful undergraduate pre-defense to a Q1 journal submission requires a strategic shift in narrative framing, empirical rigor, and structural formatting. JSS reviewers are looking for maturity, reproducibility, and actionable insights. The following roadmap is designed to guide the exploration of this research domain while maintaining strict alignment with JSS publication standards.

### **Phase 1: Solidifying the Theoretical Framework and Scope**

Before executing the core analysis, the theoretical grounding of the manuscript must be impenetrable. The paper must explicitly differentiate between standard superficial bug triage (e.g., "Is this a bug or a feature request?") and deep semantic root-cause analysis (e.g., "Is this an algorithmic flaw or an initialization error?").

**Actionable Steps:**

- Conduct a focused literature review on the limitations of purely structural classification methods (like Control-Flow Graph analysis) to highlight why the semantic ODC approach is necessary.
- Ensure that the distinction between a bug's _Impact_ (e.g., performance, crash) and its _Type_ (the root code issue) is explicitly defined in the introduction, citing the IBM v5.2 manual.
- Acknowledge the multi-fault reality of modern codebases early in the text to set expectations regarding classification accuracy limits.

### **Phase 2: Formalizing the Experimental Baselines**

Reviewers at JSS will inherently look for baselines against which to compare the proposed LLM pipeline. A solitary claim that "the LLM performs well" is insufficient without a comparative standard.

**Actionable Steps:**

- Establish a baseline using a traditional machine learning algorithm (e.g., a Support Vector Machine trained via TF-IDF on the Defects4J bug reports) or a zero-shot LLM prompt that lacks the scientific debugging framework.
- By comparing the sophisticated "Hypothesize-Observe-Conclude" pipeline against these rudimentary baselines, the manuscript will quantitatively prove the value of the prompting architecture, demonstrating that the scientific methodology reduces hallucinations.

### **Phase 3: Executing the 4-Tier Evaluation and Statistical Testing**

The 4-tier evaluation framework (Strict Match, Top-2 Match, Family Match, and Cohen's Kappa) is the strongest methodological contribution of the thesis. It must be executed with absolute transparency.

**Actionable Steps:**

- Do not shy away from instances where the pipeline completely fails (Hard Divergence). JSS values papers that rigorously analyze their own failures.
- Dedicate a specific subsection to "Error Analysis" or "Limits of the LLM," detailing cases where the LLM hallucinated despite the scientific prompt, or where the ODC taxonomy was fundamentally inadequate for a highly specific, idiosyncratic Java defect.
- Address the construct validity threat regarding developer knowledge embedded in Defects4J tests.24 Acknowledge that the "pre-fix" state is a simulated environment and discuss how framework filtering attempts to mitigate this bias.

### **Phase 4: Structuring the JSS Manuscript**

A highly structured narrative is crucial for Q1 journals. The manuscript should strictly follow the standard empirical software engineering flow:

| Manuscript Section                 | Content Focus and Narrative Goal                                                                                                                                                                  |
| :--------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **1\. Introduction**               | Contextualize the triage bottleneck, introduce ODC and the power of LLMs, outline the semantic gap, and clearly state the 3–4 selected Research Questions.                                        |
| **2\. Background & Related Work**  | Detail the 1992–2026 evolution of ODC, the history of the Defects4J benchmark, and the emergence of AutoSD and scientific debugging. Discuss the semantic gap.17                                  |
| **3\. Study Design & Methodology** | Outline the multi-modal evidence collection pipeline, the prompt engineering protocol (Zeller's method), and the mathematical formulations for the 4-tier evaluation metrics.                     |
| **4\. Results**                    | Present findings systematically per RQ. Use extensive Markdown tables to display Strict, Top-2, and Family match percentages, alongside Cohen's Kappa scores and Semantic Distances.              |
| **5\. Discussion & Implications**  | Interpret the results. Articulate the defense of "Evidence Asymmetry" and "Multi-Fault Reality." Discuss how achieving a Family Match validates the operational utility of early, pre-fix triage. |
| **6\. Threats to Validity**        | Categorize threats into Internal (data leakage, LLM non-determinism), External (generalizability beyond Java/Defects4J), and Construct (subjectivity of ODC mapping, test suite bias).            |
| **7\. Conclusion & Future Work**   | Summarize the operational value of the pipeline and outline the transition toward fully agentic frameworks (e.g., dual-agent InspectCoder models).                                                |

## **Synthesized Conclusions**

The endeavor to classify the Defects4J benchmark using Orthogonal Defect Classification via an LLM-driven scientific approach represents a highly ambitious, deeply empirical, and publishable piece of software engineering research. The methodology expertly identifies a critical gap in current literature: the stark distinction between syntactic patch analysis and deep semantic root-cause understanding.

By grounding the LLM's cognitive process in Andreas Zeller's scientific debugging framework (emulating the AutoSD paradigm), the research effectively mitigates the hallucination risks typically associated with generative AI in precise technical tasks. Furthermore, the decision to evaluate the pipeline through the dual lenses of pre-fix (symptomatic) and post-fix (causal) evidence—evaluated via a nuanced 4-tier accuracy framework—provides a profound exploration of the semantic gap inherent in software maintenance.

Rather than viewing classification divergence as a system failure, framing it as an expected manifestation of evidence asymmetry and multi-fault contamination elevates the research from a simple automation tool to a deep empirical study of software defect behavior. By selecting targeted research questions from the proposed pool, establishing rigorous comparative baselines, and meticulously adhering to the structural expectations of the _Journal of Systems and Software_, this research possesses the theoretical depth, empirical rigor, and practical applicability required to make a substantial impact in the field of automated software engineering.
