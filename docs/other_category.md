# The "Other" category: what it means, why it has no worked example, and how to check it

Written 2026-10-04. Covers the open taxonomy's escape category `Other` (`odc.py::OTHER_TYPE_NAME`,
rendered by `taxonomy_markdown("open")`). Terminology ("worked example", "IBM illustration") as in
`docs/few_shot_terminology.md`.

## Decisions (2026-10-04)

1. **"Other" means a code fix whose nature fits none of the 7 ODC defect types.** It never means a
   configuration, build or documentation bug.
2. **Keep "Other"** (the supervisor's position, `condition_model.md` §4.1).
3. **No worked example for "Other".** Worked examples are given for the 7 types only; "Other" is
   defined in words.
4. **"0 of 410 bugs in Other" is reported as "the model never chose Other"**, not as proof that every
   Defects4J bug fits ODC, until the check in §5 is run.
5. **The leave-one-type-out check (§5) is deferred**: run it after the first v3 pass with the new worked
   examples, and agree it with the supervisor first. If it shows the model never uses "Other", revisit
   decision 3.

## 1. What "Other" means

**Non-code bugs are not "Other" in ODC. They sit outside the defect types entirely.** IBM ODC v5.2
(`docs/odc_doc.md` §4.1) has a separate attribute, *Target*, for what had to change to fix the bug:
Requirements, Design, Code, Build/Package, Information Development (documentation), National Language
Support. The 7 defect types are defined only for Target = Design/Code (§4.2.1 is titled "Defect Type
for Target=Design/Code"). A configuration, build or documentation fix has a different Target and no
defect type. The Coimbra dataset follows this: its non-code records have Defect Type `NULL`.

**Defects4J has no non-code bugs by its own rules** (Defects4J `README.md`, "Each bug has the following
properties"): "Fixed by modifying the source code (as opposed to configuration files, documentation, or
test files)." So if "Other" meant non-code, no Defects4J bug could ever be Other and RQ2 would measure
nothing.

**Our prompt already defines "Other" at the code level** (`odc.py`, open taxonomy block): "The defect's
root-cause mechanism genuinely does not fit ANY of the 7 ODC types above, even approximately."

An earlier answer given at the thesis defence ("Other = no-code/configuration bugs") is therefore wrong
for this study. Do not repeat it.

## 2. Why keep "Other"

- **ODC gaps happen in practice.** Silva & Vieira applied ODC to space-system bugs and, as reported by
  Agnelo et al. (JSS 2020, §related work), found "difficulties in classifying about 32% of the bugs
  analyzed due to context specificities", which led them to adapt the taxonomy. The paper itself is
  paywalled and was not read (§8), so what those bugs were (code or not) is unknown.
- **Offering the option costs nothing when it is wrong.** Tam et al. 2025 added "None of the above" as a
  *wrong* option to multiple-choice questions: "When NA serves as a distractor, performance aligns with
  baseline rankings (Pearson's r=0.98), suggesting models treat NA distractors similarly to standard
  options." So "Other" should not hurt the classification of bugs that do fit the 7 types.

## 3. What "0 of 410 in Other" can and cannot mean

Tam et al. 2025 also made "None of the above" the *correct* answer (the right option removed): accuracy
fell "from approximately 63.2% under standard conditions down to 28.5% when the correct answers are
replaced by NAs", "a consistent 30-50% performance drop across models regardless of scale". Models pick
the most plausible remaining option instead, even when they know the facts (their Figure 1). The drop
was 14.6% for math but 48.1% for judgment-heavy subjects such as business ethics.

So "0 of 410" has two readings: ODC v5.2 covers Defects4J, or the model never picks "Other". Until §5 is
run we cannot tell which, so we report it as "the model never chose Other". ODC typing is a judgment
task, so it is probably on the high-drop side; that is our extrapolation, not their result.

Caveats on Tam et al.: an arXiv preprint (no peer-reviewed version found on 2026-10-04); 4-option
multiple choice with one exact answer, not 8-way classification; zero-shot chain-of-thought prompting.
The direction carries over, the numbers do not. Our "Other" also demands `other_justification`,
`nearest_type` and `other_confidence`, which may make the model choose it even less.

## 4. Why "Other" has no worked example

1. **A worked example of "Other" would push the model toward "Other"** (the strongest reason, and from
   LLM in-context prompting). Zhao et al. 2021 tested GPT-3 and GPT-2 with worked examples in the prompt:
   "LMs are biased towards outputting answers that are (1) frequent in the prompt (majority label bias)".
   They even saw accuracy drop from 0 to 1 example, "due to the model frequently repeating the class of
   the one training example". How often the model picks "Other" is exactly what RQ2 measures, so an
   Other example would measure our own example, not ODC's coverage.
2. **"Other" has no single shape to show.** It is defined by what it is not. One example shows one kind
   of "outside", and the model would likely treat it as an 8th type with that shape. Supporting evidence
   from pre-LLM few-shot models: FewRel 2.0 (Gao et al. 2019) tried giving examples of its
   none-of-the-above class ("sample instances outside the N relations as the supporting data of NOTA,
   and perform the (N + 1)-way K-shot learning") and found it "does not bring much improvements, since
   the supporting data for NOTA actually belong to several different relations and are scattered in the
   feature space". FewRel 2.0 tested trained neural models (CNN- and BERT-based), not prompted LLMs, so
   cite it as "in pre-LLM few-shot models". Its benchmark's own support set holds examples of the given
   classes only ("S is the supporting set containing K instances for each relation").
3. **No real example exists.** The Coimbra dataset has no "Other" label, and worked examples must be real
   (`docs/few_shot_worked_examples_research.md` Q6), so one would have to be invented.
4. **It would break the closed vs open comparison.** The closed prompt cannot show an Other example, so
   the two prompts would differ in their worked examples as well as their taxonomy. RQ2 compares exactly
   those two.

**The counterpoint (Tam et al.):** models under-choose none-of-the-above even when it is right, and with
no example our model may under-use "Other". That is the cost of this decision, and why §5 exists.

Note: Zhao et al. tested 2020–21 models. Instruction-tuned models may show these biases less strongly.

## 5. The deferred check: leave-one-type-out

**Method:**
1. Take bugs whose type we trust (e.g. the same type in both the pre-fix and post-fix runs, or the
   13 manually analysed bugs).
2. Run them with that type removed from the taxonomy and its worked example removed, keeping "Other".
3. Those bugs now fit none of the listed types; the right answer is "Other".
4. Repeat for each of the 7 types. Cheap on `few-open` (1 call per bug).

**Precedent:**
- Tam et al. 2025 "NA-as-answer": "the original correct answer is replaced with 'None of the Above'.
  This forces the model to choose from the remaining options". The same design.
- Shu, Xu & Liu 2017 (DOC): "For openworld evaluation, we hold out some classes (as unseen) in training
  and mix them back during testing."
- Gao et al. 2019 (FewRel 2.0): "The NOTA queries are sampled from those relations outside the given N
  relations", reported at several "NOTA rates".

**How to report the outcome:**
- The model sends them to "Other" → "0 of 410" is a real RQ2 finding: ODC v5.2 covered Defects4J.
- The model forces them into another type → "0 of 410" is a lower bound, explained by a known LLM
  weakness (Tam et al.). Then revisit decision 3, e.g. test an Other worked example separately.

## 6. What to say when asked "what is an example of Other?"

"Other means a code fix whose nature none of the 7 ODC types describes. Configuration or documentation
bugs aren't Other: in ODC they have a different Target and no defect type, and Defects4J excludes them.
Defects4J produced no Other. Research shows offering a none-of-the-above option doesn't hurt accuracy
when it isn't the answer, but LLMs under-choose it when it is, so our zero means the model never chose
Other, and we check that with a leave-one-type-out test."

Before §5 is run, drop the last clause or say "we plan to check".

## 7. Sources

All quotes checked against the PDFs on 2026-10-04.

- **Tam, Wu, Lin, Chen**, "None of the Above, Less of the Right: Parallel Patterns between Humans and LLMs
  on Multi-Choice Questions Answering", 2025. arXiv preprint: https://arxiv.org/abs/2503.01550
  (PDF https://arxiv.org/pdf/2503.01550). No peer-reviewed version found.
- **Zhao, Wallace, Feng, Klein, Singh**, "Calibrate Before Use: Improving Few-Shot Performance of Language
  Models", ICML 2021, PMLR 139, pp. 12697–12706. Official: https://proceedings.mlr.press/v139/zhao21c.html
  · PDF: https://proceedings.mlr.press/v139/zhao21c/zhao21c.pdf · arXiv: https://arxiv.org/abs/2102.09690.
  What the whole paper is about: few-shot prompting is unstable (format, choice and order of examples swing
  accuracy "from near chance to near state-of-the-art"), caused by majority label, recency and common token
  bias; their fix, contextual calibration, needs per-answer probabilities, which our JSON output does not
  give, so we use only the diagnosis.
- **Gao, Han, Zhu, Liu, Li, Sun, Zhou**, "FewRel 2.0: Towards More Challenging Few-Shot Relation
  Classification", EMNLP-IJCNLP 2019, pp. 6250–6255. Official: https://aclanthology.org/D19-1649/ ·
  PDF: https://aclanthology.org/D19-1649.pdf · DOI: https://doi.org/10.18653/v1/D19-1649 ·
  arXiv: https://arxiv.org/abs/1910.07124. Pre-LLM (trained CNN/BERT models).
- **Shu, Xu, Liu**, "DOC: Deep Open Classification of Text Documents", EMNLP 2017, pp. 2911–2916.
  Official: https://aclanthology.org/D17-1314/ · PDF: https://aclanthology.org/D17-1314.pdf ·
  DOI: https://doi.org/10.18653/v1/D17-1314 · arXiv: https://arxiv.org/abs/1709.08716. Pre-LLM.
- **Agnelo, Laranjeiro, Bernardino**, "Using Orthogonal Defect Classification to characterize NoSQL
  database defects", JSS 159 (2020) 110451. https://doi.org/10.1016/j.jss.2019.110451 · free author copy:
  https://eden.dei.uc.pt/~cnl/papers/2020-jss-odc-joao-v64-submitted.pdf (source of the 32% quote).
- **IBM ODC v5.2** (`docs/odc_doc.md`) §4.1 Target, §4.2.1; **Defects4J** `README.md` bug properties.

## 8. Paywalled: ask the supervisor or library

1. **Silva & Vieira**, "Adapting the Orthogonal Defect Classification Taxonomy to the Space Domain",
   SAFECOMP 2016, Springer LNCS. https://doi.org/10.1007/978-3-319-45477-1_23. Needed to learn whether its
   32% hard-to-classify bugs were code fixes, and what it added to ODC: the closest thing in the literature
   to a real code-level "Other". Get this one first.
2. **Silva, Cunha & Vieira**, "A field study on root cause analysis of defects in space software",
   Reliability Engineering & System Safety, Feb 2017. https://doi.org/10.1016/j.ress.2016.08.016. The
   follow-up applying the adapted ODC to 1,070 defects.
