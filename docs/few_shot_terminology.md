# Few-shot terminology: what counts as an "example", and what the sources say

Written 2026-10-04 (§2.5, §2.6 and §5 added the same day). Read this before writing about the `zero`/`few` strategies in the paper, the
slides or any doc. The word "example" was being used for two different things in this project, and
that caused real confusion.

## 1. One name per thing

| Use this name | What it is | Where it lives in our prompt |
|---|---|---|
| **Taxonomy definition** | The meaning of one ODC type, IBM's text word for word | `odc.py::ODC_TYPES[...]["summary"]`, rendered as **Definition** |
| **IBM illustration** | A sentence inside a type's definition that shows what the type means, e.g. "Value greater than 100 is not valid, but the check to make sure that the value was less than 100 was missing." | `odc.py::ODC_TYPES[...]["examples"]`, rendered under the heading **Examples** |
| **Worked example** | One solved bug: the input (bug evidence) + the correct type + a short reason | `prompting.py::_few_shot_examples()` |

**Worked example = positive example (Super-NaturalInstructions) = demonstration (Brown et al., Min et
al.) = shot.** These four words mean the same thing. An IBM illustration is **never** one of them. It
is part of the definition.

Do not write plain "example" in the paper or slides. Say "IBM illustration" or "worked example".

Two more terms that come up:
- **Negative example** (Super-NaturalInstructions): an input shown with a *wrong* output, explained as
  wrong. We do not use these. The "NOT Algorithm/Method: ..." lines inside our worked examples are part
  of the reason, not negative examples.
- **Label space** (Min et al.): the set of possible answers. For us, the 7 ODC types (+ Other in the
  open taxonomy).

## 2. What the sources say

Every quote below was checked against the official published PDF on 2026-10-04.

### 2.1 Brown et al. 2020: defines zero-shot and few-shot

Tom B. Brown et al., "Language Models are Few-Shot Learners", *Advances in Neural Information
Processing Systems 33 (NeurIPS 2020)*. This is the GPT-3 paper, where the terms come from.

- Official page: https://proceedings.neurips.cc/paper/2020/hash/1457c0d6bfcb4967418bfb8ac142f64a-Abstract.html
- Official PDF: https://proceedings.neurips.cc/paper_files/paper/2020/file/1457c0d6bfcb4967418bfb8ac142f64a-Paper.pdf
- arXiv (longer, 75-page version): https://arxiv.org/abs/2005.14165

The NeurIPS version is a 25-page cut of the arXiv one, and the wording differs. Quote the official one:

- Few-shot (NeurIPS p. 3): "few-shot works by giving K examples of context and completion, and then
  one final example of context, with the model expected to provide the completion"
- Zero-shot (NeurIPS p. 3): "Zero-Shot (0S) - similar to few-shot but with a natural language
  description of the task instead of any examples."
- Zero-shot (NeurIPS p. 2): "the zero-shot setting which only uses a natural language description or
  invocation of the task to be performed."
- What makes something a shot (NeurIPS p. 2), about earlier work that called itself zero-shot but put
  examples in the prompt: "Due to the use of what are effectively training examples, these cases are
  better described as "one-shot" or "few-shot" transfer."
- The arXiv version words zero-shot as: "no demonstrations are allowed, and the model is only given a
  natural language instruction describing the task" (arXiv §2, p. 7).

**Finding:** a shot is a solved instance of the task (input + answer). Zero-shot means no shots. It does
**not** mean no task description, and a list of categories is part of describing a classification task.

### 2.2 Wang et al. 2022 (Super-NaturalInstructions): names definition and examples as separate parts

Yizhong Wang, Swaroop Mishra, Pegah Alipoormolabashi et al., "Super-NaturalInstructions: Generalization
via Declarative Instructions on 1600+ NLP Tasks", *Proceedings of EMNLP 2022*, pages 5085–5109.

- Official page (ACL Anthology): https://aclanthology.org/2022.emnlp-main.340/
- Official PDF: https://aclanthology.org/2022.emnlp-main.340.pdf
- DOI: https://doi.org/10.18653/v1/2022.emnlp-main.340
- arXiv: https://arxiv.org/abs/2204.07705

§3 "Instruction schema" (p. 5087):
- "DEFINITION defines a given task in natural language. This is a complete definition of how an input
  text (e.g., a sentence or a document) is expected to be mapped to an output text."
- "POSITIVE EXAMPLES are samples of inputs and their correct outputs, along with a short explanation
  for each."

They then compare "Def" (definition only) with "Def + Pos (k)" (definition plus k positive examples):
the same contrast as our `zero` vs `few`.

**Finding:** this is the clearest source for our distinction. Our IBM definitions and illustrations are
the **Definition** part. Our worked examples are **Positive Examples**: input, correct output and a
short explanation each.

Caveat: SuperNI does not discuss illustrations placed inside a definition. Putting IBM's illustrations
under "Definition" is our reading. It holds because they are not samples of the task's input with an
output, but say so when presenting it.

### 2.3 Min et al. 2022: what a worked example teaches

Sewon Min, Xinxi Lyu, Ari Holtzman, Mikel Artetxe, Mike Lewis, Hannaneh Hajishirzi, Luke Zettlemoyer,
"Rethinking the Role of Demonstrations: What Makes In-Context Learning Work?", *Proceedings of EMNLP
2022*, pages 11048–11064.

- Official page (ACL Anthology): https://aclanthology.org/2022.emnlp-main.759/
- Official PDF: https://aclanthology.org/2022.emnlp-main.759.pdf
- DOI: https://doi.org/10.18653/v1/2022.emnlp-main.759
- arXiv: https://arxiv.org/abs/2202.12837

- Abstract (p. 1): demonstrations are "a few input-label pairs (demonstrations)".
- Figure 7 (p. 5): "Four different aspects in the demonstrations: the input-label mapping, the
  distribution of the input text, the label space, and the use of input-label pairing as the format
  of the demonstrations."
- Abstract (p. 1): "ground truth demonstrations are in fact not required -- randomly replacing labels in
  the demonstrations barely hurts performance". What matters instead: "(1) the label space, (2) the
  distribution of the input text, and (3) the overall format of the sequence."
- §5 tests the parts separately, including labels without inputs ("demonstrations with labels only",
  p. 7).
- How many worked examples (p. 5): "model performance does not increase much as k increases when
  k ≥ 8, both with gold labels and with random labels."

The four aspects in our terms:

| Min's term | Plain meaning | For us |
|---|---|---|
| Label space | The set of possible answers | The 7 ODC types (+ Other) |
| Input distribution | What the inputs look like | Real bug evidence: bug reports and Java code |
| Format | The input → answer structure | evidence → type + reason |
| Input-label mapping | Whether each input has the right answer | "this bug → Checking" is actually correct |

**Finding:** the label space, the look of the inputs and the format matter most; whether every label
is right matters least. Their experiments are on short classification and multiple-choice tasks, so the
sizes of the effects do not carry over to ODC typing directly. The direction does.

### 2.4 Anthropic's prompting guide (practitioner source)

https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#use-examples-effectively

- "A few well-crafted examples (known as few-shot or multishot prompting) improve accuracy and
  consistency."
- Examples should be "Relevant: Mirror your actual use case closely."

More from the same page, checked 2026-10-05 (used by `docs/prompt_review_v3.md`):
- "Structured: Wrap examples in `<example>` tags (multiple examples in `<examples>` tags) so Claude can
  distinguish them from instructions." (why the worked examples sit in `<worked_examples>` tags)
- "Present each example as a problem, the method to apply, and the expected answer." (the worked
  examples' shape; why the decision process could go)
- "Setting a role in the system prompt focuses Claude's behavior and tone for your use case."
- "Put longform data at the top: Place your long documents and inputs near the top of your prompt,
  above your query, instructions, and examples." (not applied yet; see prompt review block 8)

A living web page written for Claude (our classifier is Gemini), so use it to convince the team, not as
a paper citation.

### 2.4b Zheng et al. 2024: roles in system prompts (peer-reviewed counterpoint)

Mingqian Zheng, Jiaxin Pei, Lajanugen Logeswaran, Moontae Lee, David Jurgens, "When "A Helpful
Assistant" Is Not Really Helpful: Personas in System Prompts Do Not Improve Performances of Large
Language Models", *Findings of EMNLP 2024*, pp. 15126–15154.
Official: https://aclanthology.org/2024.findings-emnlp.888/ · arXiv: https://arxiv.org/abs/2311.10054

- 162 roles, 4 model families, 2,410 factual questions: "adding personas in system prompts does not
  improve model performance across a range of questions compared to the control setting where no
  persona is added"; "the effect of each persona can be largely random".

**Use:** our role line ("You are an expert software defect analyst …") is kept as convention, not as a
technique we rely on (prompt review block 1).

### 2.5 Zhao et al. 2021: the last worked example pulls the answer

Tony Z. Zhao, Eric Wallace, Shi Feng, Dan Klein, Sameer Singh, "Calibrate Before Use: Improving
Few-Shot Performance of Language Models", *Proceedings of the 38th International Conference on Machine
Learning (ICML 2021)*, PMLR 139, pages 12697–12706.

- Official page (PMLR): https://proceedings.mlr.press/v139/zhao21c.html
- Official PDF: https://proceedings.mlr.press/v139/zhao21c/zhao21c.pdf
- arXiv: https://arxiv.org/abs/2102.09690

Abstract:
- "the order of the training examples can cause accuracy to vary from near chance to near
  state-of-the-art"
- "bias of language models towards predicting certain answers, e.g., those that are placed near the
  end of the prompt or are common in the pre-training data."

**Finding:** the type of the last worked example is the one the model leans toward (recency bias). This
is not the "lost in the middle" effect, which is about finding information in long inputs.

### 2.6 Lu et al. 2022: order matters, and a good order does not carry over between models

Yao Lu, Max Bartolo, Alastair Moore, Sebastian Riedel, Pontus Stenetorp, "Fantastically Ordered Prompts
and Where to Find Them: Overcoming Few-Shot Prompt Order Sensitivity", *Proceedings of ACL 2022
(Volume 1: Long Papers)*, pages 8086–8098.

- Official page (ACL Anthology): https://aclanthology.org/2022.acl-long.556/
- Official PDF: https://aclanthology.org/2022.acl-long.556.pdf
- DOI: https://doi.org/10.18653/v1/2022.acl-long.556
- arXiv: https://arxiv.org/abs/2104.08786

Abstract:
- "the order in which the samples are provided can make the difference between near state-of-the-art
  and random guess performance"
- "a given good permutation for one model is not transferable to another"

**Finding:** the order of worked examples has to be checked, and checked again for each model (we run
more than one model, see `condition_model.md` §5).

### 2.7 Not used here

Wei et al. 2022, chain-of-thought (https://arxiv.org/abs/2201.11903), is often cited as precedent for
hand-written worked examples. Its abstract confirms "a few chain of thought demonstrations are provided
as exemplars in prompting", but the claim that the exemplars were written by hand was not checked
against the paper. Verify it before citing it for that.

## 3. Applied to our prompts

| Prompt content | Few-shot? | Why |
|---|---|---|
| Taxonomy definitions + IBM illustrations only | **No: zero-shot** | Describes the task; no solved bug is shown (Brown p. 3, SuperNI "Def") |
| The above + the 5 worked examples in `_few_shot_examples()` (the current `few`) | **Yes** | The worked examples are input + correct output + reason (Brown's "context and completion", SuperNI's "Positive Examples") |
| `zero-free` (v2) | Zero-shot | No worked examples. It also has no taxonomy, which zero-shot does not require (see §4) |

What each part of the prompt provides, in Min's terms:

| | Label space | Input distribution | Format | Mapping |
|---|---|---|---|---|
| IBM definitions + illustrations | yes | no | no | no |
| Current 5 invented worked examples | partly: 5 of 7 types, no Timing/Serialization or Relationship | **no**: made-up one-liners, unlike real evidence | yes | yes |
| Planned worked examples from the Coimbra dataset ([few_shot_worked_examples_research.md](few_shot_worked_examples_research.md) Q5) | yes, all 7 | mostly: real bug reports and Java code, but no stack traces or coverage | yes | yes, checked by two labelers |

## 4. What this means for the project

**What the sources support:**
- Our current `few` strategy **is** few-shot by Brown's definition. Its worked examples are invented, not
  wrong in kind.
- They are weak exactly where Min says it counts: they miss 2 of the 7 types and look nothing like real
  bug evidence. That is the case for real worked examples from an externally labeled dataset.
- `docs/condition_model.md` §2 says `zero` is "taxonomy-free **by definition** (a zero-shot prompt
  contains no label space)". Brown's definition does not say that: zero-shot only removes worked
  examples, and a task description may include the categories. So `zero-free` removed two things at
  once (worked examples and the taxonomy) and cannot show what either one adds.

**What not to claim:** that our few-shot "was not really few-shot". By Brown's definition it was. Saying
otherwise is easy to disprove and weakens the two points above that are correct.

**Open, pending the team and supervisor (2026-10-04):** whether to keep `zero-free`, add
`zero-open`/`zero-closed` (taxonomy, no worked examples), or replace it. Note that a taxonomy-but-no-
worked-examples condition existed before as the `direct` cell and was dropped after a 6-bug pilot
(condition_model.md §3); that pilot used the invented worked examples. Until decided,
`condition_model.md` stays the operative spec.


## 5. Decisions and the papers behind them

Each decision taken on 2026-10-04 for the new worked examples, with the paper that supports it. The full
list of decisions, including the ones with no paper behind them, is in
`docs/few_shot_worked_examples_research.md` Q6.

| Decision | Paper | What the paper says | Where |
|---|---|---|---|
| A worked example (input + type + reason) is what makes a prompt few-shot; IBM illustrations do not | Brown et al. 2020 (§2.1) | a shot is "effectively training examples"; few-shot gives "K examples of context and completion" | NeurIPS pp. 2–3 |
| Same decision, with the two parts named | Wang et al. 2022, SuperNI (§2.2) | "DEFINITION" vs "POSITIVE EXAMPLES ... samples of inputs and their correct outputs" | EMNLP p. 5087 |
| Zero-shot does not require removing the taxonomy (pending with supervisor) | Brown et al. 2020 (§2.1) | zero-shot uses "a natural language description of the task instead of any examples" | NeurIPS p. 3 |
| Use real bugs as worked examples, not invented ones | Min et al. 2022 (§2.3) | what drives performance is "(1) the label space, (2) the distribution of the input text, and (3) the overall format" | EMNLP p. 1 |
| Cover all 7 types (the old set skipped 2) | Min et al. 2022 (§2.3) | the label space is one of the three main drivers | EMNLP p. 1, §5.2 |
| Each worked example includes the fix and a short reason | SuperNI (§2.2); Brown et al. (§2.1) | positive examples come "along with a short explanation for each"; a shot has a "context and a desired completion" | EMNLP p. 5087; NeurIPS p. 3 |
| 7 worked examples is enough; no need to pad to 10–15 | Min et al. 2022 (§2.3) | performance "does not increase much as k increases when k ≥ 8" | EMNLP p. 5 |
| End on a rare type, not on Function/Class/Object or Algorithm/Method | Zhao et al. 2021 (§2.5) | models lean towards answers "placed near the end of the prompt" | ICML abstract |
| No worked example for "Other" | Zhao et al. 2021 (§2.5); Gao et al. 2019, FewRel 2.0 (pre-LLM) | labels "frequent in the prompt" get predicted more (majority label bias); none-of-the-above examples "do not bring much improvements" because they are "scattered" | full rationale: `docs/other_category.md` §4 |
| Run the pilot with 2–3 different orders, per model | Lu et al. 2022 (§2.6); Zhao et al. 2021 (§2.5) | order can swing results "between near state-of-the-art and random guess"; a good order "is not transferable to another" model | ACL abstract; ICML abstract |

**Decisions with no paper behind them (our own reasoning), so do not cite a paper for these:**
- One set of worked examples, the same in the pre-fix and post-fix arms. Reason: keeps the two arms'
  prompts identical except for the target bug's evidence (methodology, not literature). Its one cost
  *is* paper-based: Min et al. say format should match the real input, and the pre-fix input has no fix.
- The "Why not <closest type>" line inside each worked example, and which rival it names. Each rival
  must have a source in this order: IBM ODC v5.2, then a peer-reviewed paper (e.g. Henningsson &
  Wohlin 2004's confusion table), then our manual analysis, then Claude's reasoning approved by the
  user (research doc Q6.1, decision 9). (A "first reading vs. the fix" step was drafted and dropped
  on 2026-10-05; see research doc Q6.1, decision 5.)
- Quoting only the important lines, word for word.
- Preferring checked labels (single-labeled ones are valid). Min et al. found random labels "barely hurt", so this is not what drives
  performance; we do it because the paper has to defend where its labels came from.
