# Related-work literature leads (2026-08-15 research pass)

Findings from a two-agent literature survey run while drafting
`latex/jss/sections/03_related_work.tex` subsection 2.2. Not yet acted on —
this is a holding pen for when related-work writing resumes. Read this
before touching subsection 2.1, 2.3 ("mapping"), or 2.4 again.

## Citation error to fix

`latex/jss/sections/03_related_work.tex` (subsection 2.3/"LLM-based Defect
Classification" area, the SVM/Naive-Bayes sentence) currently attributes
"77–82% accuracy" to **both** `\citep{huang2011autoodc,thung2012automatic}`.
Those numbers belong to **AutoODC (`huang2011autoodc`) alone**
(82.9%/80.7% NB/SVM industrial, 77.5%/75.2% on FileZilla). Thung et al.
2012 reported a different result: 77.8% average accuracy with multiclass
SVM on **three ODC super-categories** (control-and-data-flow, structural,
non-functional), using bug-report text **plus code features from bug
fixes** — not the same setup, not the same number. Needs a rewrite of that
sentence to attribute correctly.

## Also pending (found earlier same session, not a literature-search item)

Subsection 2.2's new ODC attribute table (`tab:odc-attributes`,
`latex/jss/sections/03_related_work.tex`) has a wrong **Source** value: it
currently says "in-house, outsourced, ported, or open-source." Per the
actual v5.2 spec (`docs/odc_doc.md`), the real values are **Developed
In-House, Reused From Library, Outsourced, Ported** — "open-source" is not
a real ODC Source category. Fix alongside the citation error above.

## New citation candidates

### High-value — directly comparable to this pipeline

- **Kumar, Sharma, Muttoo & Singh (2022), "Autoclassify Software Defects
  Using Orthogonal Defect Classification."** ICCSA 2022, LNCS 13381,
  pp. 313–322. DOI: 10.1007/978-3-031-10548-7_23. **The LSTM paper** —
  LSTM/RNN/CNN/MLP over BoW/TF-IDF/word2vec, classifying into **ODC Impact
  categories** specifically. LSTM wins, ~70% accuracy on Redmine. Directly
  relevant since Impact is now first-class in this pipeline
  ([[odc-alignment-audit]] memory) — cite as a text-only-ceiling comparator
  against the evidence-grounded (code+test) approach here.
- **Djiré, Kaboré, Samhi, Barr, Klein, Bissyandé, "Learned or Memorized?
  Quantifying Memorization Advantage in Code LLMs."** ICSE 2026.
  arXiv:2604.13997. Defects4J's memorization advantage is <0.1, the
  *lowest* of 19 benchmarks measured — rebuts the "the model already
  memorized this bug" objection to pre-fix classification. Strong
  threats-to-validity citation.
- **Cotroneo, Improta, Liguori, ISSRE 2025.** arXiv:2508.21634. ODC applied
  at 500k-sample scale to human vs. LLM-generated code — natural successor
  citation to the already-cited `pan2024understanding`.

### Fills the "keyword-based → deep learning → LLM" chronology gap

- **Lopes, Agnelo, Teixeira, Laranjeiro, Bernardino (2020).** FGCS
  102:932–947. DOI: 10.1016/j.future.2019.09.009. Benchmarks
  kNN/SVM/NB/Nearest-Centroid/RF **and RNNs** across *all* ODC attributes on
  4,096 real bug reports. Headline finding — some ODC attributes are hard
  to recover from bug-report text alone — is close to a direct motivation
  statement for using code+test evidence instead of report text.
- **Liu, Zhao, Yang, Lu, Zhou, Xu (2015), "An AST-Based Approach to
  Classifying Defects."** IEEE QRS-C 2015. DOI: 10.1109/QRS-C.2015.15.
  Classifies defects from **AST features of source code**, not bug-report
  text. Closest methodological ancestor to a code-evidence ODC pipeline.
- **Patil & Ravindran (2020).** EMSE 25:1341–1378. DOI:
  10.1007/s10664-019-09779-6. Zero-shot ODC defect-type classification via
  concept-based Explicit Semantic Analysis — no labelled training data.
  Precursor to a zero-shot/LLM framing.
- **Kumar, Muttoo, Singh (2022).** IJOSSP 13(1):1–16. DOI:
  10.4018/IJOSSP.300749. Same group as the LSTM paper; classical ML with
  chi-square feature selection, reports **per-ODC-attribute** numbers
  (activity, impact, target, type, qualifier) — useful if a per-attribute
  accuracy comparison table gets built later.

### Structural analogues to the enforced reasoning loop

- **AgentSZZ (2026).** arXiv:2604.02665. ReAct-style observe-reason-act
  agent, capped at 15 turns, for bug-inducing-commit identification (not
  defect types). Corroborates "agentic loop beats single-shot on
  evidence-grounded SE labelling," different label space than this work.
- **"When Agents Fail" (2026).** arXiv:2601.15232. BugReAct, a ReAct agent
  annotating bugs against a hand-built taxonomy, with human-agreement and
  cost reporting. No standardized industrial taxonomy, no open-set escape
  category — both are differentiators for this pipeline vs. that one.

### Scoping / survey references

- **Alannsary (2025/2026), "AI-ODC."** e-Informatica Software Engineering
  Journal 20(1):260102. arXiv:2508.17900. Extends the ODC *schema* itself
  for AI-based systems — evidence ODC is still actively evolving; contrast
  with this pipeline's approach of leaving v5.2's schema unmodified and
  using an open "Other" escape category instead of proposing new types.
- **"From Bugs to Benchmarks" survey.** arXiv:2504.17977 (rev. Feb 2026).
  151 defect datasets surveyed — scoping reference for why Defects4J.
- **Chen et al., LLM-for-defect-detection SLR.** Frontiers of Computer
  Science 20:2006202, 2026. DOI: 10.1007/s11704-025-40672-2. Covers
  *detection*, not classification — citable as a stated gap this work
  fills.
- **Colavito et al., extended issue-classification study (2025).**
  arXiv:2506.00128. Supersedes the already-cited `colavito2024llm` —
  consider swapping or adding.

## Open question — not resolved by the search

The "keyword-based approach" you recalled finding before the LSTM paper did
**not** turn up as a real ODC paper. No purely keyword/rule-based ODC
classification paper exists in the peer-reviewed literature that either
agent could find. Closest matches: Otoom, Al-jdaeh & Hammad (2019, ICICM,
DOI: 10.1145/3357419.3357424) — keyword-based, but classifies
corrective-vs-perfective, not ODC — or a non-citable US patent
(9,047,402, "Automatic calculation of ODC fields"). Best guess: the memory
is Thung et al. 2012's code-feature engineering, mentally filed as
"keyword-based." Worth a gut-check before assuming a paper is missing.

## Bottom line from both research agents

Neither agent found any published work that classifies Defects4J bugs into
ODC types using an LLM, or that compares pre-fix vs. post-fix evidence for
classification — the core contribution here remains unclaimed as of this
search date.
