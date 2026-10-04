# Few-shot worked examples: what "few-shot" means, and where real ODC-labeled examples could come from

> Terminology and the sources for what counts as few-shot (IBM illustration vs worked example,
> Brown / Super-NaturalInstructions / Min, official links): `docs/few_shot_terminology.md` (2026-10-04).
> Follow-up dataset check and fix verdicts: Q5 at the end of this file.

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

---

## Q5. Follow-up check of the Coimbra dataset (2026-10-04)

I downloaded `2019-jss.zip` again (HTTP 200, 116,862,853 bytes) and checked the claims above against the files. The zip and its contents stay outside the repo: the readme states no license, so redistribution is still unresolved. This section cites ids, labels and file paths only.

### 5.1 What holds

- The Defect Type distribution in 2.1 is exact (3,846 typed records).
- All 14 records in the Q3 table exist in `<DB> after.csv` with the labels listed there.
- Agreement with the final label: researcher2 matches `after.csv` on 387/410 (94%), researcher3 on 356/400 (89%). These fit the papers' 0.94 and 0.90-0.91.
- `after.csv` is the right file. `before.csv` is the label before internal verification. Example: MongoDB 3641 was Function/Class/Object / Missing before and Algorithm/Method / Incorrect after.

### 5.2 Corrections

- **The dataset ships the bug report text.** 2.1 says `Bug report` is the id only, with no text. That is true of the CSV, but the zip also has `odc classification/bug report data/<DB>/<DB> - <id>.txt`: 4,102 files with title, JIRA link, dates, components, description and all comments. All 14 Q3 records have one. The comments often name the fix commit (git hash, GitHub link or SVN revision), which is the way to get the diff. So step 1 of "How to finish each row" is half done offline: the report text is already local; only the fix commit has to be fetched.
- **The id mapping is settled.** The verification sheets carry the URL templates: `SERVER-<id>` (jira.mongodb.org), `CASSANDRA-<id>` and `HBASE-<id>` (issues.apache.org). The MongoDB 19615 text file opens with `[SERVER-19615]`.
- **Only 3 of the 14 Q3 picks were double-labeled:** Cassandra 9055 (researcher2 agrees), Cassandra 6965 (researcher3 agrees), HBase 7002 (researcher2 agrees). The other 11 were labeled by researcher1 alone. Under the Q3 rule "prefer double-labeled, agreed records", those 11 should be replaced from the pool in 5.3 where the pool allows it.

### 5.3 Candidate pool: double-labeled records whose verifier agreed

How it was built: a record is in the pool if researcher2 (sheet `Henrique` in `verificacao-researcher2-410.xlsm`) or researcher3 (column 14 of sheet `Planilha1` in `verificacao-researcher3-410.xlsm`) gave the same Defect Type as `after.csv`. This is agreement between one external verifier and the final label. It is **not** agreement between the two external verifiers: their sets overlap on only 5 records.

"Commit ref" means a regex found a git hash, GitHub commit link, "committed as/in <hash>" or SVN revision in the report text. I did not open any of these commits.

| Defect Type | Agreed (all DBs) | Agreed, Java (Cassandra + HBase) | Java with commit ref |
|---|---|---|---|
| Relationship | 2 | 2 | **1** |
| Timing/Serialization | 9 | 4 | 2 |
| Assignment/Initialization | 34 | 14 | 5 |
| Interface/O-O Messages | 49 | 31 | 17 |
| Checking | 80 | 50 | 19 |
| Function/Class/Object | 98 | 58 | 29 |
| Algorithm/Method | 466 | 311 | 139 |

These are candidates, not finished examples. Each one still needs the five steps in Q3: fetch the fix, quote the symptom and the fix hunk, write our own rationale, drop it if the fix does not support the label, and relabel it against `odc.py`.

Candidates for the thin types (Java, agreed):
- **Relationship:** Cassandra 9055 (commit ref), HBase 2458 (no ref).
- **Timing/Serialization:** HBase 7421 (SVN ref), HBase 16701 (git ref), Cassandra 4255, HBase 9723 (no ref).
- **Assignment/Initialization, with commit ref:** Cassandra 7149, Cassandra 12481, HBase 12976, HBase 13085, HBase 13647.

### 5.4 Things to watch when the fixes are read

- **Relationship is the bottleneck.** There are 2 agreed Java records and only 1 has a commit ref. *(Resolved 2026-10-04, see Q6: the doubt below came from the old paraphrased `odc.py` text, which lacked IBM's inheritance example. With IBM's text restored, CASSANDRA-9055 fits directly.)* The one usable record is also borderline under our definition: CASSANDRA-9055's proposed fix is to make `FunctionExecutionException` extend `RequestExecutionException`. Under `odc.py` that could read as Interface/O-O Messages or Function/Class/Object rather than "associations among procedures, data structures and objects". One verified Relationship example per type may not be achievable from this dataset.
- **Some Timing/Serialization labels are test-timeout fixes.** Three of the four Java candidates are about tests timing out or being flaky (HBASE-7421 "has an aggressive timeout", HBASE-9723, HBASE-16701). If the fix only raises a timeout in a test, it does not match our definition (missing or wrong serialization of a shared resource). Check each fix before using it.
- **The format gap stays.** These are JIRA reports about distributed databases. Most have no failing unit test, stack trace or coverage data. An example built from them can show real report text and a real fix hunk, but it cannot fully copy `_context_payload` without inventing evidence, which must not be done.

### 5.5 Open decision: Relationship — DECIDED 2026-10-04: option 2, CASSANDRA-9055 (see Q6)

Choose one:
1. Use a single-labeled Relationship record (HBase 5172 from Q3, or another single-labeled one) and say so in the paper.
2. Use Cassandra 9055 only if our own relabel agrees it is Relationship.
3. Leave Relationship out of the examples and say why: 8 of 3,846 records in the source dataset.

### 5.6 Fix check of the checked candidates (2026-10-04)

All candidates below are checked records (a second labeler agreed with the final label, see 5.3). For each one I fetched the fix commit from GitHub (`apache/cassandra` or `apache/hbase`) and confirmed the commit names the JIRA key. Finding a commit by a hash in the report text is not safe on its own: for HBASE-12976, HBASE-13647, CASSANDRA-5752 and CASSANDRA-6604 the hash in the comments pointed to a different bug's commit. Search GitHub by JIRA key and check the commit message.

The verdict judges whether the production code change (tests and CHANGES.txt ignored) fits the type under our `odc.py` definitions.

| Type (Coimbra label) | Record | Fix (production code) | Verdict |
|---|---|---|---|
| Timing/Serialization | CASSANDRA-4255 | `getEstimatedTasks()` made `synchronized` (fix for a ConcurrentModificationException) | **Use.** Clean, one line. |
| Timing/Serialization | HBASE-9723, HBASE-7421 | test files only | Drop: test fix. |
| Timing/Serialization | all 16 Java Timing records reviewed 2026-10-05 (single-labeled allowed) | HBASE-16701 (checked) and 6 single-labeled ones change tests only. Production fixes fetched: HBASE-5535 (2 methods made `synchronized`, same pattern as 4255, single-labeled); HBASE-4294 (`finish()` now sets the flag inside `synchronized (dataAvailable)` and calls `notifyAll()`; symptom is a 1-second delay); CASSANDRA-5244 (removes `synchronized` from `reportSeverity`, which shared the instance lock held by `initServer` during bootstrap, and uses an `AtomicDouble`: IBM's "wrong resource was serialized" clause, but the fix also rewrites the computation, so Algorithm is a real competing reading; single-labeled). CASSANDRA-9380 is labeled Timing/Serialization but is about a field missing from `write`/`readFields`, i.e. data serialization, not IBM's access serialization. | None beats CASSANDRA-4255 (checked, one-line, fits the first clause of IBM's definition exactly). CASSANDRA-5244 is the runner-up. |
| Checking | CASSANDRA-11239 | null guard added around `options.getDataCenters().addAll(dataCenters)` | **Use.** Missing check. |
| Checking | CASSANDRA-6965 | null guard added before `getLocalDataCenter().equals(...)` | **Use** (alternative). Missing check. |
| Checking | CASSANDRA-10343 | condition `deletionInfo().isLive()` → `deletionInfo().getPartitionDeletion().isLive()` | Use if a wrong (not missing) check is wanted. |
| Assignment/Initialization | HBASE-12976 | default constant `Long.MAX_VALUE` → `2 * 1024 * 1024` | **Use.** One constant. |
| Assignment/Initialization | HBASE-13647 | default constant `Integer.MAX_VALUE` → `60000` | Use (alternative). |
| Assignment/Initialization | CASSANDRA-7149 | `unit.convert(time, MILLISECONDS)` → `MILLISECONDS.convert(time, unit)` | Weak: reads as a wrong API call (Interface). |
| Interface/O-O Messages | CASSANDRA-13119 | call `parseOptionalKeyspace(args, probe)` → `parseOptionalKeyspace(args, probe, true)` | **Use.** Wrong parameter list in a call. |
| Interface/O-O Messages | CASSANDRA-12759 | `printf("JMX Port: %d", nativePort)` → `jmxPort` | Use (alternative). Wrong argument passed. |
| Interface/O-O Messages | CASSANDRA-12776, -13393, -13151 | wrong method called (`onHeap()`/`offHeap()`, `size()`/`memUsed()`), missing charset argument | Possible alternatives. |
| Interface/O-O Messages | CASSANDRA-5602 | logger created with the wrong class | Drop: reads as Assignment. |
| Interface/O-O Messages | CASSANDRA-8862 | `pending.incrementAndGet()` → `pending.get()` | Drop: unclear type. |
| Interface/O-O Messages | CASSANDRA-6604 | no fix commit found | Drop. |
| Function/Class/Object | CASSANDRA-5752 | adds a missing capability: Thrift-table support in `CqlPagingRecordReader` (new method) | ~~Use~~ **Rejected 2026-10-04 while drafting:** the Algorithm rival is strong (IBM Algorithm illustration (1): "The algorithm … was missing"; Coimbra's own rule that FCO means "large changes in the design"), so "formal design change" was only Claude's reading; the fix (72 lines, 2 classes) was also hard to excerpt. |
| Function/Class/Object | CASSANDRA-6378 | new class `SSLTransportFactory` (commit `4a6f8a6610`, added after `1b2a190379` forgot it) + 10 new command-line options; the hard-coded plain `TSocket`/`TFramedTransport` connection becomes pluggable | **Use (replaces 5752, 2026-10-04).** Fits IBM "significant capability, end-user interfaces"; checked by researcher 3 (agreed). Found by reading the title and description of all 58 checked Java FCO records (fixes fetched for 8); also rejected: HBASE-7482 (security in CopyTable, 14 files), HBASE-13477 (feature request, no failure), HBASE-8293 (pure file move, 0 lines), HBASE-14936 (missing overrides, reads as Relationship/Algorithm), CASSANDRA-8178 (16 files), HBASE-4277 (fix commit not found on GitHub). |
| Function/Class/Object | CASSANDRA-8502 | redesign of `DataRange.Paging` across 5 files | Drop: too large to excerpt. |
| Algorithm/Method | CASSANDRA-7508 | vnode detection changed from a config value (`DatabaseDescriptor.getNumTokens() > 1`) to a loop over the actual token map (`haveVnodes |= endpointsToTokens.containsKey(...)`); the config import is removed | **Use.** Full fix read 2026-10-04: one method, no signature change, the procedure for deciding "vnodes enabled" is reimplemented. **Use the original 2.1 commit `721afaead6` (`NodeTool.java`)**, not the 2.0 backport `74f3204c66` (`NodeCmd.java`) first fetched: same change, but only 2.1 matches the report's stack trace (`NodeTool.java:464` = the removed `if`, checked 2026-10-04). |
| Algorithm/Method | HBASE-7002 (Q3 pick) | FindBugs clean-up: `new Integer` → `Integer.valueOf`, `static final`, `entrySet()` loop | Drop: cosmetic, teaches nothing about the type. |
| Algorithm/Method | CASSANDRA-9906, -12781 | multi-line logic changes | Possible alternatives. |
| Relationship | CASSANDRA-9055 | `FunctionExecutionException extends CassandraException` → `extends RequestExecutionException` | **Use** (decided 2026-10-04). Matches IBM §4.2.1.7 example 2 ("The inheritance relationship between two classes is missing or incorrectly specified"), now verbatim in `odc.py`. Only checked Relationship record with a fix commit: no checked backup. |
| Relationship | HBASE-2458 | every method of `SoftValueSortedMap` made `synchronized` | Drop as a worked example (re-checked 2026-10-05 under IBM's exact text). Two researchers (main labeler + researcher 3) gave Relationship, most likely from the diagnosis in comment #12857819 (the caller assumed `getCachedLocation` was read-only, but the map's reads mutate it), which fits IBM Relationship illustration (1). But IBM §4.2 defines Defect Type as "the actual correction that was made", and the correction is serialization of a shared resource: IBM Timing definition and illustration (1). By the source order (Q6.1 decision 9), IBM's text outranks the published label. A defensible label, a poor example: its fix teaches Timing. |
| Relationship | 6 single-labeled records (validated 2026-10-05) | CASSANDRA-1259: wrong package names in contrib classes (packaging/compile, no behaviour; fix commit not found). HBASE-5172: `interface HTableInterface extends Closeable` (matches IBM illustration 2 exactly, but the report has no symptom, only "Ioan Eugen Stan found this issue."). HBASE-13409: test categories only. SERVER-1511, -1498, -14671: C++ header compile errors. | None beats CASSANDRA-9055: only HBASE-5172 fits by its correction, and it has no evidence to show pre-fix and no second labeler. |

All 7 types now have a checked example (Relationship decided 2026-10-04).


## Q6. Decisions for the new worked examples (2026-10-04)

The papers behind these decisions, with quotes and links: `docs/few_shot_terminology.md` §5.
Terminology as in `docs/few_shot_terminology.md`: a *worked example* is a solved bug (input + type +
reason); an *IBM illustration* is part of a type's definition. Nothing below is implemented yet:
`_few_shot_examples()` still holds the 5 invented worked examples.

### 6.1 Decided

1. **Source:** real bugs from the Coimbra dataset (Agnelo, Laranjeiro, Bernardino, JSS 159, 2020,
   https://doi.org/10.1016/j.jss.2019.110451), which uses IBM ODC v5.2 unchanged, the same version as
   `docs/odc_doc.md`. **Prefer checked records** (a second researcher re-labeled the bug and agreed,
   5.3); **a single-labeled record is valid** when no checked one fits as well (the user's decision,
   2026-10-05, replacing the stricter "only checked records" of 2026-10-04). Every label in the dataset
   is human: one trained researcher labeled all 4,096 bugs by hand (JSS 2020); no label comes from a
   model. In all cases, only where we read the real fix and it fits IBM's exact text (5.6).
   Examples 1-5 (all checked) are unaffected by the change.
2. **The 7 bugs, one per type:**

   | Type | Bug | Fix in one line |
   |---|---|---|
   | Checking | CASSANDRA-11239 | null guard added around `options.getDataCenters().addAll(dataCenters)` |
   | Assignment/Initialization | HBASE-12976 | default constant `Long.MAX_VALUE` → `2 * 1024 * 1024` |
   | Algorithm/Method | CASSANDRA-7508 | "vnodes enabled" now computed from the token map instead of read from config |
   | Interface/O-O Messages | CASSANDRA-13119 | call `parseOptionalKeyspace(args, probe)` → `parseOptionalKeyspace(args, probe, true)` |
   | Function/Class/Object | CASSANDRA-6378 | missing capability added: client encryption for sstableloader (new class `SSLTransportFactory`, 10 new user options). **Replaced CASSANDRA-5752 on 2026-10-04**, see 5.6 |
   | Relationship | CASSANDRA-9055 | `extends CassandraException` → `extends RequestExecutionException` |
   | Timing/Serialization | CASSANDRA-4255 | `getEstimatedTasks()` made `synchronized` |

3. **Only the important parts, copied exactly.** Each worked example quotes the few lines of bug report
   and code that matter, word for word. Nothing is reworded or condensed, and nothing is invented: no
   made-up stack trace, test or coverage.
4. **One set, the same in both arms.** The pre-fix and post-fix prompts show the same 7 full worked
   examples, including each example's fix.
   - No leak: the pre-fix rule is about the bug being classified. The worked examples are other bugs
     (Cassandra/HBase, not Defects4J), so their fixes say nothing about the target's fix.
   - It teaches what ODC is: IBM types a defect by the nature of its fix.
   - It keeps the arms comparable: the two prompts then differ only in the target bug's evidence, so a
     pre-fix/post-fix difference (RQ3, RQ5) can only come from seeing the fix.
   - Cost: in the pre-fix arm the examples contain a fix section that the real input lacks, a partial
     format mismatch (Min et al. 2022). Judged worth it.
   - This replaces the earlier idea of separate pre-fix and post-fix versions (14 examples).
5. **Shape of each worked example** (final, 2026-10-05): Bug report → Buggy code → Fix → Type →
   Why not. Report and code lines are copied word for word, `[…]` marks every cut, and each code block
   opens with a `//` file label (ours). The Type line quotes IBM's exact definition or illustration
   and then states what the code and diff show. Each "Why not" names a rival type that has a source
   (decision 9) and is a real trap for the reader; an example may have 0 to 3 of them (Example 6,
   CASSANDRA-9055, has none: its report states the cause too clearly for any rival to match).
   - **Dropped 2026-10-05: the "first reading" step** (what the symptom and code suggest before the
     fix). It was a guess written by Claude after seeing the fix, staged to be wrong in 3 examples,
     and the reporter's real framing is already in the Bug report line. The lesson it aimed at (look
     past the symptom to the likely fix) is carried by the "Why not" lines instead.
   - Full text, provenance and every approval: `docs/worked_examples_draft.md`.
6. **Order:** Checking, Assignment/Initialization, Algorithm/Method, Interface/O-O Messages,
   Function/Class/Object, Relationship, Timing/Serialization. Reason: recency bias. Zhao et al.,
   "Calibrate Before Use: Improving Few-Shot Performance of Language Models", ICML 2021
   (https://arxiv.org/abs/2102.09690): "the order of the training examples can cause accuracy to vary
   from near chance to near state-of-the-art", and models are biased "towards predicting certain
   answers, e.g., those that are placed near the end of the prompt". The old set ended on
   Function/Class/Object, the type the prompt warns against overusing. Ending on a rare type limits the
   harm. (This is not the "lost in the middle" effect, which is about long inputs.)
7. **Order check:** run the 13-bug pilot with 2–3 different orders and confirm the labels do not change.
8. **Paper wording:** "worked examples come from an external ODC-labeled dataset (Agnelo et al. 2020)
   and include their fixes; the classified bug's own fix is never shown in pre-fix mode." Also state
   that the post-fix prompt already differed from the pre-fix one by the diff-guidance block.

9. **Order of sources for every reason we write** (the user's rule, 2026-10-04). Applies to the
   "Type" and "Why not" lines of the worked examples, and to any other classification guidance:
   1. IBM ODC v5.2 (`docs/odc_doc.md`).
   2. An author of a peer-reviewed paper (e.g. Henningsson & Wohlin 2004 on which types raters
      confuse; Agnelo et al. JSS 2020 on their labeling conventions).
   3. What our own manual analysis found (`analysis_v2/manual_analysis/`, 13 bugs, one rater).
   4. Claude's own reasoning, only after the user approves it.

   Guidance written before July 2026 is **not trusted by default**, because the coding agents of that
   time reasoned poorly. This covers `odc.py`'s `indicators` and `distinguish_from` fields (Hasin
   `f2dd56b`, 2026-04-14; rewritten `f79c7b2`, 2026-04-21; no source recorded; only one sentence,
   "multiple … assignment corrections may be of type Algorithm/Method", traces to IBM). Do not take
   a worked example's rival type or reasoning from them.

### 6.2 Still open

- ~~An "Other" worked example~~ **DECIDED 2026-10-04: none.** Rationale, sources and the deferred
  leave-one-type-out check: `docs/other_category.md`.
- **Permission to quote** the dataset: the readme states no license. Ask the authors before
  publishing anything that prints the excerpts. Deferred until publication.
- **`zero-free`** (pending with the supervisor, `docs/few_shot_terminology.md` §4) does not affect the
  worked examples; it only decides which conditions v3 runs.

### 6.3 Next steps

1. Draft the 7 worked examples as text for review (no code). **Done: all 7 approved 2026-10-05
   (`docs/worked_examples_draft.md`); CASSANDRA-6378 replaced 5752 for FCO.**
2. **Done 2026-10-05:** implemented as prompt `v3-2026-10-05` together with the prompt review
   (`docs/prompt_review_v3.md`); record and pilot runbook in `docs/study_execution_log.md`.
3. (Former step 2, now done: `_few_shot_examples()` replaced, tests, `condition_model.md`,
   `llm_prompting_architecture.md` §1.3 and the log updated.)
4. Next: the 13-bug pilot (runbook in the log), then the user decides full run or rollback; the order
   check (decision 7) after that.
