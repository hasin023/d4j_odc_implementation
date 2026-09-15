# Research Questions for JSS

> **Revised 2026-09-15.** RQ3 and RQ4 were reworded to match what our data actually supports, and
> rewritten in plain language. RQ1, RQ2 and RQ5 keep their original wording.
> The reasoning and the numbers behind each: `docs/RQ_standing_assessment.md`.
> The old RQ3/RQ4 wording is kept at the bottom for provenance — do not cite it.

**Words used below:**
- **pre-fix** — what the pipeline sees at triage time: the buggy code and the failing tests. No fix.
- **post-fix** — the same bug, plus the developer's real fix diff.
- **ODC** — the seven-type Orthogonal Defect Classification taxonomy.

---

## **RQ1 — Bug Type Distribution Across Projects**

**Question:** What is the distribution of ODC defect types across the Defects4J benchmark, and does this distribution vary significantly across projects?

*In short: which types of bugs are these, and do Math bugs look different from Mockito bugs?*

---

## **RQ2 — Bug Type Coverage of the ODC Taxonomy**

**Question:** Do the seven standard ODC bug types cover all the bugs in Defects4J — or do some bugs actually fall outside those seven types?

*In short: we offered the model an "Other" escape category. Did any bug need it?*

---

## **RQ3 — Does a Classification Made Before the Fix Survive Seeing the Fix?**

**Question:** Defects4J has no ODC labels, so there is no answer key. We therefore classify each bug twice — once pre-fix and once post-fix — and treat the post-fix classification as our reference, because an ODC defect type describes the nature of the fix, so the run that sees the fix is the better-informed one. **How often does the pre-fix classification produce the same defect type as the post-fix one, and when it does not, how far apart are the two labels?**

*In short: at triage time nobody has written the fix yet. Does the label we assign then still hold once the fix exists?*

The "how far apart" part is graded on four levels: same type, same type after correcting for chance
(Cohen's κ), the other label was already shortlisted, and same ODC family.

---

## **RQ4 — What Does Each Part of the Pipeline Actually Contribute?**

Our pipeline adds two things on top of simply asking an LLM: we force it to use the ODC taxonomy, and
we force it to run a scientific-debugging loop. These two have very different effect sizes, so we ask
about them separately.

**RQ4a — Question:** What does forcing the ODC taxonomy buy us, compared to letting the model describe the bug in its own words? We compare label vocabulary size, label spread (entropy), and whether the label is reproducible across two views of the same bug.

*In short: is imposing ODC better than just asking "what kind of bug is this?"*

**RQ4b — Question:** What does the enforced hypothesis → prediction → probe → observation loop add on top of a strong single-call few-shot prompt, when both use the same taxonomy? We compare agreement with the post-fix reference, overall and per project.

*In short: does making the model investigate before answering beat just giving it good instructions?*

---

## **RQ5 — Does Seeing the Fix Change How a Bug Gets Classified?**

**Question:** What is the magnitude and pattern of semantic divergence between pre-fix and post-fix ODC classifications, and how does per-project classification reliability vary across Defects4J projects?

*In short: how many labels change when the fix becomes visible, which types swap with which, and is the pipeline equally reliable on every project?*

---

## How RQ3 and RQ5 differ

They use the same pre-fix/post-fix comparison but ask opposite questions about it.

- **RQ3** asks **how much agreement there is** — can we trust a pre-fix label? It reports the match
  rate and how severe the misses are.
- **RQ5** asks **what the disagreement is made of** — which types swap with which, in which projects,
  and why. It reports the pattern and the mechanisms.

---

## Superseded wording (pre-2026-09-15 — kept for provenance, do not cite)

- **RQ3 (old):** "How well does the LLM-based pipeline, using the scientific debugging loop and ODC
  taxonomy, classify Defects4J bugs into the correct defect types under a four-level accuracy
  evaluation?" — retired because the word "correct" asserts a ground truth Defects4J does not provide.
- **RQ4 (old):** "How much do the scientific debugging loop and explicit ODC taxonomy grounding each
  improve classification accuracy, label consistency, and vocabulary reduction compared to an
  unstructured LLM baseline?" — retired because it bundled two ablations with very different effect
  sizes into one question. Split into RQ4a and RQ4b.
