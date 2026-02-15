"""
Basic foam / risk metrics for LLM answers.

This is a simple, heuristic implementation intended as a research prototype.
"""

from typing import List, Dict, Any


def foam_level0(answer: str) -> float:
    """
    Local foam: very simple heuristic based on length and presence of obvious uncertainty markers.
    """
    text = answer.lower()
    base = len(answer) * 0.001  # длина как лёгкий штраф

    uncertainty_markers = ["maybe", "perhaps", "i guess", "возможно", "кажется"]
    penalty_uncertainty = any(m in text for m in uncertainty_markers)

    return base + (0.5 if penalty_uncertainty else 0.0)


def foam_level1(answers: List[str]) -> List[float]:
    """
    Cross-answer foam: simple pairwise disagreement heuristic.

    For now: for each answer we count how many others are 'very different' in a naive way
    (string inequality), which is obviously simplistic but enough for a toy prototype.
    """
    n = len(answers)
    scores = [0.0] * n
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            if answers[i].strip().lower() != answers[j].strip().lower():
                scores[i] += 1.0
    return scores


def foam_level2(answers: List[str], context_documents: List[str]) -> List[float]:
    """
    Context foam: penalty if answer does not share tokens with context.

    Very naive implementation: we check unigram overlap with concatenated context.
    """
    if not context_documents:
        return [0.0] * len(answers)

    ctx = " ".join(context_documents).lower().split()
    ctx_set = set(ctx)

    scores = []
    for ans in answers:
        tokens = ans.lower().split()
        overlap = sum(1 for t in tokens if t in ctx_set)
        # чем меньше overlap, тем больше пена
        score = 1.0 / (1.0 + overlap)
        scores.append(score)
    return scores


def aggregate_scores(
    answers: List[str],
    context_documents: List[str] | None,
    lambda_levels: Dict[int, float],
) -> Dict[str, Any]:
    """
    Compute per-level foam and total scores for each answer.

    Returns:
        {
          "phi0": [..],
          "phi1": [..],
          "phi2": [..],
          "total": [..],
        }
    """
    context_documents = context_documents or []

    phi0 = [foam_level0(a) for a in answers]
    phi1 = foam_level1(answers)
    phi2 = foam_level2(answers, context_documents)

    lam0 = lambda_levels.get(0, 0.0)
    lam1 = lambda_levels.get(1, 0.0)
    lam2 = lambda_levels.get(2, 0.0)

    total = [
        lam0 * phi0[i] + lam1 * phi1[i] + lam2 * phi2[i]
        for i in range(len(answers))
    ]

    return {
        "phi0": phi0,
        "phi1": phi1,
        "phi2": phi2,
        "total": total,
    }
