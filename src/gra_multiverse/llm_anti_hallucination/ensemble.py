"""
High-level ensemble / anti-hallucination API for LLM answers.
"""

from typing import List, Dict, Any, Optional

from .metrics import aggregate_scores


def optimize_answers(
    answers: List[str],
    context_documents: Optional[List[str]] = None,
    lambda_levels: Optional[Dict[int, float]] = None,
    return_all_scores: bool = True,
) -> Dict[str, Any]:
    """
    Select a more consistent answer from a list of LLM outputs.

    Args:
        answers: list of candidate answers.
        context_documents: optional list of context documents (RAG, KB, etc.).
        lambda_levels: dict[level -> weight], e.g. {0: 0.5, 1: 1.0, 2: 2.0}.
        return_all_scores: if True, include per-level foam scores.

    Returns:
        {
          "answer": str,
          "chosen_index": int,
          "scores": {..}  # if return_all_scores
        }
    """
    if not answers:
        raise ValueError("answers list must not be empty")

    lambda_levels = lambda_levels or {0: 0.5, 1: 1.0, 2: 2.0}

    scores = aggregate_scores(answers, context_documents, lambda_levels)
    total = scores["total"]

    # выбираем индекс с минимальным total
    chosen_index = min(range(len(total)), key=lambda i: total[i])
    chosen_answer = answers[chosen_index]

    result: Dict[str, Any] = {
        "answer": chosen_answer,
        "chosen_index": chosen_index,
    }

    if return_all_scores:
        result["scores"] = scores

    return result
