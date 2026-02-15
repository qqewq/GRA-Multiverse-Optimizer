# tests/test_llm_anti_hallucination.py

from gra_multiverse.llm_module import optimize_answers


def test_optimize_answers_prefers_consistent_fact():
    answers = [
        "Paris is the capital of France.",
        "Paris is a large city in Germany.",
        "The capital of France is Paris.",
    ]

    context_documents = [
        "France is a country in Europe. Its capital is Paris."
    ]

    result = optimize_answers(
        answers=answers,
        context_documents=context_documents,
        lambda_levels={0: 0.5, 1: 1.0, 2: 2.0},
    )

    # Должен вернуть строку и индекс
    assert isinstance(result["answer"], str)
    assert isinstance(result["chosen_index"], int)

    # Ожидаем, что выбран будет один из «парижских» ответов (0 или 2)
    assert result["chosen_index"] in (0, 2)


def test_optimize_answers_returns_scores_dict():
    answers = [
        "GRA-Multiverse-Optimizer is a prototype backend for multilevel GRA Meta-Obnulyonka.",
        "GRA-Multiverse-Optimizer is a video game engine.",
    ]

    context_documents = [
        "GRA-Multiverse-Optimizer is a prototype backend for multilevel GRA Meta-Obnulyonka."
    ]

    result = optimize_answers(
        answers=answers,
        context_documents=context_documents,
        lambda_levels={0: 0.3, 1: 0.7, 2: 1.5},
    )

    # Проверяем наличие scores и базовую структуру
    assert "scores" in result
    scores = result["scores"]
    assert isinstance(scores, dict)
    # ожидаем, что хотя бы один уровень присутствует
    assert len(scores) >= 1
