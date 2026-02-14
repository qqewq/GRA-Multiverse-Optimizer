# tests/test_llm_module.py

from src.gra_multiverse.llm_module import optimize_answers


def test_optimize_answers_basic():
    answers = [
        "Paris is the capital of France.",
        "The capital of France is Marseille.",
        "France is a country in Europe. Its capital is Paris.",
    ]

    result = optimize_answers(
        answers=answers,
        meta_goal="max_consistency",
        max_steps=10,
    )

    # Должен вернуться один из исходных ответов
    assert result["index"] in range(len(answers))
    assert result["chosen"] == answers[result["index"]]
    assert "best_cosine_similarity" in result["debug"]


def test_optimize_answers_empty():
    result = optimize_answers(
        answers=[],
        meta_goal="max_consistency",
        max_steps=5,
    )
    assert result["index"] == -1
    assert result["chosen"] == ""


def test_optimize_answers_prefers_consistent_fact():
    # Два ответа согласуются (Париж), один – нет (Марсель)
    answers = [
        "Paris is the capital of France.",
        "Marseille is the capital of France.",
        "The capital of France is Paris.",
    ]

    result = optimize_answers(
        answers=answers,
        meta_goal="max_consistency",
        max_steps=10,
    )

    # Ожидаем, что выбран будет один из "парижских" ответов (0 или 2)
    assert result["index"] in (0, 2)
