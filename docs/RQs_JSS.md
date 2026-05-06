# Research Questions for JSS

## **RQ1 — Bug Type Distribution Across Projects**

**Question:** What is the distribution of ODC defect types across the Defects4J benchmark, and does this distribution vary significantly across projects?

---

## **RQ2 — Separating Bug Symptoms from Bug Causes**

**Question:** Does explicitly separating the ODC defect Impact (the observable symptom, such as a crash or performance degradation) from the ODC defect Type (the root cause, such as a missing guard or incorrect algorithm) lead to more accurate automated triage compared to symptom-only labeling?

---

## **RQ3 — Overall Pipeline Classification Accuracy**

**Question:** How well does the LLM-based pipeline, using the scientific debugging loop and ODC taxonomy, classify Defects4J bugs into the correct defect types under a four-level accuracy evaluation?

---

## **RQ4 — Contribution of Each Pipeline Component**

**Question:** How much do the scientific debugging loop and explicit ODC taxonomy grounding each improve classification accuracy, label consistency, and vocabulary reduction compared to an unstructured LLM baseline?

---

## **RQ5 — Does Seeing the Fix Change How a Bug Gets Classified?**

**Question:** What is the magnitude and pattern of semantic divergence between pre-fix and post-fix ODC classifications, and how does per-project classification reliability vary across Defects4J projects?
