# Using GRA-Multiverse-Optimizer for LLM Anti-Hallucination

This document describes how to use **GRA-Multiverse-Optimizer** as an **Anti‑Hallucination Core** on top of large language models (LLMs).

We focus on the practical side: how to feed multiple answers into the multiverse, how the “foam” functionals \(\Phi^{(l)}\) are used, and how to integrate this into a real LLM pipeline.

---

## 1. Concept / Концепция

We interpret multiple LLM answers (or multiple samples from one LLM) as a **multiverse of hypotheses**:

- **Level 0**: individual answers \(\Psi^{(0,a)}\) from one or several LLMs.  
- **Level 1**: agreement between answers (pairwise consistency).  
- **Level 2**: agreement with external context (RAG documents, knowledge base, tools).

At each level \(l\) we define a “foam” functional \(\Phi^{(l)}\) that measures inconsistency:

- \(\Phi^{(0)}\): internal contradictions within a single answer (e.g., conflicting numbers, entities).  
- \(\Phi^{(1)}\): disagreements between different answers (semantic distance, entity mismatch).  
- \(\Phi^{(2)}\): disagreement with external context (documents, trusted sources).

The multiverse functional

\[
J_{\text{multiverse}}(\mathbf{\Psi}) =
\sum_{l=0}^K \Lambda_l \sum_{\dim(\mathbf{a})=l} J^{(l)}(\Psi^{(\mathbf{a})})
\]

is minimized by a **cognitive vacuum** state: an answer (or ensemble of answers) with minimal foam and maximal cross‑level consistency.

---

## 2. Basic API: `optimize_answers`

The main high‑level entry point for LLM usage is:

```python
from gra_multiverse.llm_anti_hallucination import optimize_answers
