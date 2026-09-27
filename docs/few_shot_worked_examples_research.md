# Few-shot worked examples: what "few-shot" means, and where real ODC-labeled examples could come from

Research note, 2026-09-27. Scope: the `few` strategy's `_few_shot_examples()` in `d4j_odc_pipeline/prompting.py` (also used by `scientific`). Status: **partial.** Q1 and Q2 are verified against primary sources. Q3 found real per-bug ODC labels for all 7 types, but I ran out of session budget before I could fetch the bug text or fix code for any record, so no example is ready to paste in yet (see Q3).

## TL;DR

1. Our `few` strategy **is few-shot in Brown et al.'s sense**: K demonstrations of context+completion at inference, no weight updates. Brown does not require the demonstrations to be ground truth, manually verified, or 10-15 in number. Brown's own K was "typically 10 to 100", limited only by the 2048-token context window.
2. Label correctness matters less than people expect. Min et al. 2022 found random labels cost only 0–5% absolute. Format and **in-distribution inputs** matter more (OOD inputs cost 3–16%). Yoo et al. 2022 found the label effect varies with the setup. Selection (Liu 2022) and order (Lu 2022, Zhao 2021) can swing results from near chance to near SOTA.
3. The real weakness of our 5 examples is **distribution and format mismatch**, not "they aren't 10-15 ground-truth items". They are invented one-liners and look nothing like the real `_context_payload` input. They cover 5 of 7 types and never show Timing/Serialization or Relationship.
4. The best public per-bug ODC dataset is the **Coimbra NoSQL dataset** (Agnelo/Laranjeiro/Bernardino, JSS 2020; reused by Lopes et al., FGCS 2020). It has 4,096 JIRA bugs from MongoDB, Cassandra and HBase with 6 ODC attributes, Defect Type κ≈0.88–0.93, and a public download. It contains labels and issue ids only: no rationale, no code, no diffs, no tests. Labelers read the report text plus comments, and "source code changes" per the JSS paper.
5. I sourced 14 real labeled records covering all 7 types (2 each). **0 of them are finished examples**: none has a verified bug description, fix excerpt, or rationale yet. They must be fetched from JIRA and the fix commits before use.

---

## Q1. What "few-shot" means, and whether our `few` qualifies

### 1.1 The origin: Brown et al. 2020, "Language Models are Few-Shot Learners" ([arXiv:2005.14165](https://arxiv.org/abs/2005.14165), §2 "Approach" and §2.4 "Evaluation")

- Definition (§2): "Few-Shot (FS) is the term we will use in this work to refer to the setting where the model is given a few demonstrations of the task at inference time as conditioning [RWC+19], but no weight updates are allowed. … few-shot works by giving K examples of context and completion, and then one final example of context, with the model expected to provide the completion. We typically set K in the range of 10 to 100 as this is how many examples can fit in the model's context window (n_ctx = 2048)."
- One-shot: "the same as few-shot except that only one demonstration is allowed, in addition to a natural language description of the task". Zero-shot: "no demonstrations are allowed, and the model is only given a natural language instruction describing the task."
- §2.4: "we evaluate each example in the evaluation set by randomly drawing K examples from that task's training set as conditioning". Also: "K can be any value from 0 to the maximum amount allowed by the model's context window … Larger values of K are usually but not always better".
- The Introduction describes few-shot as allowing "as many demonstrations as will fit into the model's context window (typically 10 to 100)".

What this means for us:
- **K has no lower bound other than K>1.** "10 to 100" describes what fit in GPT-3's window. It is not a definitional minimum. By Brown's terms, 5 demonstrations plus an instruction is few-shot.
- **Brown drew demonstrations from the task's labeled training set, at random, for each test item.** That is the one way we differ from Brown's protocol. Our demonstrations are hand-written, fixed across all items, and not drawn from the task distribution. Brown's definition does not require ground truth, but the demonstrations Brown actually used were real task data.

### 1.2 Do the demonstrations need correct labels? Min et al. 2022, "Rethinking the Role of Demonstrations" ([arXiv:2202.12837](https://arxiv.org/abs/2202.12837), EMNLP 2022)

- Abstract: "we show that ground truth demonstrations are in fact not required -- randomly replacing labels in the demonstrations barely hurts performance … Instead, we find that other aspects of the demonstrations are the key drivers of end task performance, including the fact that they provide a few examples of (1) the label space, (2) the distribution of the input text, and (3) the overall format of the sequence."
- §4: "replacing gold labels with random labels only marginally hurts performance … models see performance drop in the range of 0–5% absolute."
- On K (§4.2): "model performance does not increase much as k increases when k ≥ 8, both with gold labels and with random labels." The main experiments use k = 16.
- On input distribution (§5.1): "using out-of-distribution inputs instead of the inputs from the training data significantly drops the performance … by 3–16% in absolute … in-distribution inputs in the demonstrations substantially contribute to performance gains."
- On format (§5.3): "keeping the format of the input-label pairs is key."

Counterpoint: Yoo et al. 2022, "Ground-Truth Labels Matter: A Deeper Look into Input-Label Demonstrations" ([arXiv:2205.12685](https://arxiv.org/abs/2205.12685)), abstract: "the correct input-label mappings can have varying impacts on the downstream in-context learning performances, depending on the experimental configuration." Their controlling factors include "the verbosity of prompt templates and the language model size". So correct labels are not irrelevant. The literature does not say they are *required*, though, and it does not say they matter most.

Caveat for us: Min and Yoo study short-label classification and multiple choice (sentiment, NLI and similar) with the models of their time. ODC typing is a long-input, reasoning-heavy task, so these magnitudes do not transfer directly. What does transfer is the direction: format and input distribution are first-order factors.

### 1.3 Selection and order

- Liu et al. 2022, "What Makes Good In-Context Examples for GPT-3?" ([arXiv:2101.06804](https://arxiv.org/abs/2101.06804), DeeLIO 2022): "the empirical results of GPT-3 depend heavily on the choice of in-context examples." The paper proposes retrieving examples that are semantically similar to the test input, and this beats random selection.
- Lu et al. 2022, "Fantastically Ordered Prompts…" ([arXiv:2104.08786](https://arxiv.org/abs/2104.08786), ACL 2022): "the order in which the samples are provided can make the difference between near state-of-the-art and random guess performance … a given good permutation for one model is not transferable to another."
- Zhao et al. 2021, "Calibrate Before Use" ([arXiv:2102.09690](https://arxiv.org/abs/2102.09690), ICML 2021): "the choice of prompt format, training examples, and even the order of the training examples can cause accuracy to vary from near chance to near state-of-the-art … this instability arises from the bias of language models towards predicting certain answers, e.g., those that are placed near the end of the prompt".
- UNVERIFIED (not re-fetched this session): Wei et al. 2022, chain-of-thought ([arXiv:2201.11903](https://arxiv.org/abs/2201.11903)). It used a small set of **manually composed** exemplars with rationales (8 for most arithmetic tasks). This is precedent that author-written demonstrations with rationales are an accepted few-shot design, so being invented is not disqualifying in itself.

### 1.4 Verdict

- **Is `few` few-shot by Brown's definition?** Yes. It gives K=5 demonstrations (symptom + snippet → type + reasoning) in the prompt, plus an instruction and the taxonomy, with no weight updates. It departs from Brown's *protocol*, not the definition: the demonstrations are hand-written and fixed rather than randomly drawn from labeled task data.
- **Does few-shot require ground-truth, manually verified, or 10–15 examples?** No source says so. Brown's "10 to 100" is a context-window statement. Min shows diminishing returns past k≈8 and small losses even from wrong labels. Correct labels are still good practice (Yoo), and a JSS reviewer will expect real labeled examples, but that is a methodological-quality argument, not a definitional one.
- **Real weaknesses of the current 5, judged against this literature:**
  1. *Input distribution mismatch* (Min §5.1, the largest effect measured there). The real input is a JSON-ish evidence bundle: failing tests, headline error, truncated stack trace, suspicious frames, ±12-line snippets, coverage summary, bug_info, and sanitized report text, plus a diff in the post-fix arm. The demonstrations are one-line prose symptoms with one-line code.
  2. *Format mismatch* (Min §5.3). The demonstrations do not use the input→output structure the model sees at test time, and they do not show the JSON output schema the model must emit.
  3. *Label-space coverage* (Min's point (1)). 2 of 7 types (Timing/Serialization, Relationship) are never demonstrated, and "Other" (open mode) is never demonstrated either. This works against the taxonomy-escape questions (RQ2).
  4. *Invented, not drawn from any distribution* (Brown §2.4). They are toys designed to be unambiguous, while real bugs are ambiguous: the NoSQL labelers note multi-correction bugs often collapse to Algorithm/Method (see 2.1). Ex. 1 is also internally odd: it names a "null locale parameter" and then shows a null `input`.
  5. *Fixed order, and a single type in the final slot* (Lu; Zhao recency bias). Example 5 (Function/Class/Object) always sits last, next to the test input. The system prompt already warns against defaulting to Function/Class/Object, so this ordering is worth controlling for.
  6. *Leak-style cue.* The demonstrations state "The fix is …". Fine as a rationale, but in the pre-fix arm the model never sees a fix, so the examples model reasoning from information that is not available.

## Q2. Published ODC datasets with per-bug labels

Ranked by similarity to our Defects4J evidence. "Closest" means code, fix diff and failing test or stack trace; "furthest" means report text only.

### 2.1 Coimbra NoSQL ODC dataset: best available, verified and downloaded

- **Papers:** Agnelo, Laranjeiro, Bernardino, "Using Orthogonal Defect Classification to characterize NoSQL database defects", JSS 2020 ([author PDF](https://eden.dei.uc.pt/~cnl/papers/2020-jss-odc-joao-v64-submitted.pdf)). Lopes, Agnelo, Teixeira, Laranjeiro, Bernardino, "Automating orthogonal defect classification using machine learning algorithms", FGCS 102 (2020) 932–947 ([doi:10.1016/j.future.2019.09.009](https://doi.org/10.1016/j.future.2019.09.009), [author PDF](https://eden.dei.uc.pt/~cnl/selected-research/2020-fgcs-odc.pdf)).
- **Download:** [https://eden.dei.uc.pt/~cnl/papers/2019-jss.zip](https://eden.dei.uc.pt/~cnl/papers/2019-jss.zip). This is JSS ref. [17]: "NoSQL ODC Dataset, Results, and Support Code," Mar-2019. I downloaded it on 2026-09-27 (HTTP 200, 116 MB). The FGCS paper also names `http://odc.dei.uc.pt`, but that host refused connections on 2026-09-27.
- **Size and language:** 4,096 closed/resolved JIRA bugs (MongoDB 1,618, Cassandra 1,095, HBase 1,383), per the zip `readme.txt`. The systems are C++ (MongoDB) and Java (Cassandra, HBase). Of these, 3,846 have Target=Code and so carry a Defect Type.
- **Attributes:** Activity, Trigger, Impact, Target, Defect Type, Qualifier. Age and Source are excluded (FGCS §3.1).
- **Record format:** `odc classification/<DB> after.csv`, with columns `Bug report, Activity, Trigger, Impact, Target, Defect Type, Qualifier`. `Bug report` is the numeric JIRA id **only**: no text, no rationale, no code. The zip also has `verification/verificacao-researcher{1,2,3}-*.xls[xm]` (the double-labeled subsets, not inspected) and scripts.
- **What the labelers used:** FGCS §3.1: "The bug reports used are composed of a title, a description of the detected defect and several comments that end up describing what has been made to correct the defect." The JSS paper's steps include "iii. Analysis and interpretation of the source code changes". So the label reflects the fix, though no diff ships with the data.
- **Who labeled, and agreement:** one trained researcher labeled everything after 300 discarded training bugs. They internally re-checked 20% (820). Two external researchers each re-labeled 410 non-overlapping bugs.
  - JSS Table III (researcher2): Defect Type accuracy 0.94, κ 0.93. Researcher3 on Defect Type: accuracy 0.91, κ 0.90.
  - The FGCS version reports researcher3 at "accuracy of 0.90 which corresponds to a Kappa value of 0.88". The two papers differ slightly, so cite whichever version you use.
- **Defect Type distribution (computed from the CSVs):**
  - Algorithm/Method 2,365
  - Function/Class/Object 543
  - Checking 407
  - Interface/O-O 312
  - Assignment/Initialization 169
  - Timing/Serialization 42
  - Relationship 8
- **Labeling convention to know about** (JSS §IV.A): "a defect that consists of multiple 'Assignment/Initialization' corrections, may correspond to an 'Algorithm/Method' defect type … cases which contained corrections of both 'Assignment/Initialization' and 'Checking' types were often classified as 'Algorithm/Method'". Also, "Function/Class/Object … refers to large changes in the design".
- **License:** none stated in the readme. UNVERIFIED; ask the authors before redistributing.
- **Similarity to our evidence:** medium. Each record has a real bug and a real fix reachable through JIRA and the linked commit, but ships as a label only. Building a demonstration in our format means fetching the report, the fix commit and ideally the failing test by hand.
- **Reuse:** Kumar, Muttoo & Singh 2022 reuse the same 4,096-bug data ([ResearchGate](https://www.researchgate.net/publication/360833622_Classification_of_Software_Defects_Using_Orthogonal_Defect_Classification)).

### 2.2 Other leads (not verified at record level this session)

| Rank | Source | What is known | Verified? |
|---|---|---|---|
| 2 | Thung, Lo, Jiang, "Automatic Defect Categorization", WCRE 2012 | 500 defects from Java projects (Mahout, Lucene, OpenNLP per my recollection), with fix commits. Labeled into **3 ODC-derived families** (control/data flow, structural, non-functional), not the 7 types. The family summary is confirmed by the [IRMA summary](https://www.irma-international.org/viewtitle/300749/?isxn=9781683180975): "categorizes the defect broadly in three categories … 500 defect reports". | Family scheme and 500 count verified second-hand. Projects and dataset link UNVERIFIED. |
| 3 | Durães & Madeira, "Emulation of Software Faults: A Field Data Study and a Practical Approach", IEEE TSE 32(11), 2006 | ODC-typed field faults from open-source C programs, with fault-type patterns (e.g., missing if-construct) mapped to ODC types. Useful for *code-level patterns per type*; not a per-bug labeled Java set. | UNVERIFIED this session. |
| 4 | Huang et al., "AutoODC", Automated Software Engineering 22(1), 2015 ([doi:10.1007/s10515-014-0155-1](https://doi.org/10.1007/s10515-014-0155-1)) | ODC classification of defect reports (text). | Existence verified via citation. Dataset UNVERIFIED. |
| 5 | Hernández-González et al., "Two datasets of defect reports labeled by a crowd of annotators of unknown reliability", Data in Brief 2018 ([UdG portal](https://recerca.udg.edu/en/publications/two-datasets-of-defect-reports-labeled-by-a-crowd-of-annotators-o/)) | Portal: "categorized … according to their **impact** from IBM's orthogonal defect classification taxonomy". The labels are **Impact, not Defect Type**, so this is **not usable** for us. Text only. | Verified (abstract). |
| 6 | Aldekaim et al., "Automating Bug Report Classification with Few Shot Learning", INL 2025 ([OSTI 3395075](https://www.osti.gov/biblio/3395075)) | ODC defect types from bug reports (nuclear DI&C), F1≈0.6. A student expo presentation. Dataset availability unknown. | Abstract verified. Data UNVERIFIED. |
| 7 | Rahman & Farhana 2020 (COVID-19 software ODC); Christmansson & Chillarege 1996 | Not checked this session. | UNVERIFIED. |
| n/a | IBM ODC v5.2 (`docs/odc_doc.md`) | Has "Examples:" blocks for Activity and Trigger. Defect Type values have definitions, not per-bug worked examples. | Grepped locally. |

**Defects4J warning:** no source checked this session labels Defects4J bugs with ODC. Any source found later that does must be kept out of the candidate set: it would leak into our evaluation.

## Q3. Candidate worked examples

**Honest status:** the 14 records below are real, labeled, and cover all 7 types. For **none** of them did I retrieve the bug text, fix diff, or failing test. The dataset contains **no published per-bug rationale**, so every rationale column is "no published rationale". Nothing below is invented. The descriptions are deliberately left blank until the JIRA issue and fix commit are read.

**UNVERIFIED id mapping:** the CSV stores bare numbers. I assume the keys are `CASSANDRA-<n>`, `HBASE-<n>` and MongoDB `SERVER-<n>`. The MongoDB project key in particular must be confirmed before use.

Source for all rows: `odc classification/<DB> after.csv` in [2019-jss.zip](https://eden.dei.uc.pt/~cnl/papers/2019-jss.zip). Confidence for all rows: single labeler (researcher1). Whether a row falls in the 20–40% double-checked subset is unknown until the `verification/*.xls*` files are checked, and double-checked rows should be preferred.

| # | ODC type (labeler) | Record | Activity / Trigger / Impact / Qualifier | Bug + fix excerpt | Rationale |
|---|---|---|---|---|---|
| 1 | Timing/Serialization | Cassandra 9380 | Unit Test / Simple Path / Capability / Missing | not yet retrieved | no published rationale |
| 2 | Timing/Serialization | HBase 12170 | System Test / Blocked Test / Reliability / Incorrect | not yet retrieved | no published rationale |
| 3 | Timing/Serialization | MongoDB 19615 | Code Inspection / **Concurrency** / Capability / Incorrect | not yet retrieved | no published rationale |
| 4 | Relationship | Cassandra 9055 | Code Inspection / Side Effects / Capability / Incorrect | not yet retrieved | no published rationale |
| 5 | Relationship | HBase 5172 | Code Inspection / Logic/Flow / Capability / Incorrect | not yet retrieved | no published rationale |
| 6 | Function/Class/Object | Cassandra 5234 | System Test / Blocked Test / Reliability / Incorrect | not yet retrieved | no published rationale |
| 7 | Function/Class/Object | HBase 3121 | Code Inspection / Side Effects / Capability / Extraneous | not yet retrieved | no published rationale |
| 8 | Interface/O-O Messages | Cassandra 7603 | Unit Test / Simple Path / Capability / Incorrect | not yet retrieved | no published rationale |
| 9 | Interface/O-O Messages | HBase 9415 | Code Inspection / Logic/Flow / Capability / Incorrect | not yet retrieved | no published rationale |
| 10 | Checking | Cassandra 6965 | Unit Test / Simple Path / Reliability / Missing | not yet retrieved | no published rationale |
| 11 | Checking | HBase 8540 | Unit Test / Simple Path / Serviceability / Missing | not yet retrieved | no published rationale |
| 12 | Assignment/Initialization | Cassandra 9503 | Code Inspection / Logic/Flow / Capability / Incorrect | not yet retrieved | no published rationale |
| 13 | Algorithm/Method | Cassandra 471 | Function Test / Test Coverage / Reliability / Incorrect | not yet retrieved | no published rationale |
| 14 | Algorithm/Method | HBase 7002 | Code Inspection / Logic/Flow / Performance / Incorrect | not yet retrieved | no published rationale |

Picks were the first records of each type in file order (Java projects preferred), not a curated selection. Relationship has only 8 records in the whole dataset, so choice there is thin.

How to finish each row before use:
1. Open the JIRA issue and the linked fix commit.
2. Quote the failing symptom or stack trace and a ≤10-line fix hunk verbatim.
3. Write a paraphrased rationale **clearly marked as ours**, derived from the fix.
4. Drop any row where the fix does not plainly support the label.
5. Prefer rows that appear in the researcher2/3 verification files with agreement.

## Q4. Recommendation

- **How many:** about 7–8 (one per type, plus optionally one "Other" for open mode). Min et al. find gains flatten at k ≥ 8. Brown's 10–100 was a context-window ceiling, not a target. Real evidence-format demonstrations are long, so 7–8 is also the practical budget. Do not pad to 15 for its own sake.
- **Format:** mirror `_context_payload`: failing test and headline error, trimmed stack frames, ±N-line buggy snippet, and (post-fix arm only) the fix hunk. Then the label, a one-line "why", and "why not <nearest rival type>", in the same JSON output schema the model must emit. Min §5.1 and §5.3 support in-distribution, same-format demonstrations. Keep one pre-fix variant of each demonstration (no fix shown), so pre-fix prompts do not model reasoning from unseen information.
- **Selection:** real, non-Defects4J, preferably Java bugs (Cassandra, HBase), preferring the double-labeled, agreed records. Relabel them yourselves against `odc.py` definitions and report your own agreement. The Coimbra conventions (e.g., multi-correction bugs → Algorithm/Method) may differ from ours.
- **Order:** fixed, documented, and balanced. Do not put Function/Class/Object or Algorithm/Method last (Zhao recency bias). A robustness check across 2–3 permutations on the pilot is cheap and answers Lu et al.
- **Paper caveat:**
  - Changing `_few_shot_examples()` changes the `few` prompt, so **few-open (and few-closed) must be rerun**.
  - `scientific` builds on the same function, so **scientific arms change too**. Both move together and remain comparable with each other, but not with any artifacts produced under the old examples.
  - Record the example set (hash or version) in the artifacts and in `docs/study_execution_log.md`.
  - Per the existing v3 decision, this belongs in `artifacts_v3`, never `artifacts_v2`.
  - Say plainly in the paper that the demonstrations are drawn from an external ODC-labeled corpus (Agnelo et al. 2020) and adapted to our evidence format.
