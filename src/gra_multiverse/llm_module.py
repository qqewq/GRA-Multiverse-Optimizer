# src/gra_multiverse/llm_module.py

"""
EN:
LLM / agent helper module for GRA-Multiverse-Optimizer.

This module provides a high-level function `optimize_answers` that:
- takes several textual answers from different models/agents,
- embeds them into a simple vector space,
- builds a tiny two-level multiverse state (level 0: local answers, level 1: meta-consistency),
- runs MultiverseOptimizer over J_multiverse,
- selects the answer closest to the optimized multiverse state.

RU:
Модуль-помощник для LLM / агентов в GRA-Multiverse-Optimizer.

Функция `optimize_answers`:
- принимает несколько текстовых ответов от моделей/агентов,
- отображает их в простое векторное пространство,
- строит маленькое двухуровневое состояние мультиверса (уровень 0: локальные ответы, уровень 1: мета-согласование),
- запускает MultiverseOptimizer по J_multiverse,
- выбирает ответ, наиболее близкий к оптимизированному состоянию мультиверса.
"""

from typing import List, Callable, Tuple, Dict
import numpy as np

from .core import Level, Goal, MultiverseState, MultiverseFunctional
from .optimizer import MultiverseOptimizer


# --- Простая текстовая "эмбеддер-функция" по умолчанию --- #

def default_embed(text: str) -> np.ndarray:
    """
    EN: Very simple bag-of-chars embedding (placeholder).
    RU: Очень простое bag-of-chars представление (заглушка).
    Замените на нормальные эмбеддинги (sentence-transformers и т.п.).
    """
    # Fixed alphabet for toy example
    alphabet = "abcdefghijklmnopqrstuvwxyzабвгдеёжзийклмнопрстуфхцчшщъыьэюя"
    vec = np.zeros(len(alphabet), dtype=np.float32)
    text = text.lower()
    for ch in text:
        if ch in alphabet:
            idx = alphabet.index(ch)
            vec[idx] += 1.0
    # Normalize
    norm = np.linalg.norm(vec) + 1e-9
    return (vec / norm).astype(np.complex128)


# --- Вспомогательная функция для длины мультииндекса --- #

def default_index_dim_fn(a: Tuple[int, ...]) -> int:
    """
    EN: Dimension = last index value (for this simple LLM case).
    RU: Размерность = последнее значение индекса (для простого LLM случая).
    Мы будем использовать кортежи (i, 0) для уровня 0 и (0, 1) для уровня 1.
    """
    return a[-1]


# --- Основная функция оптимизации ответов --- #

def optimize_answers(
    answers: List[str],
    meta_goal: str = "max_consistency",
    embed_fn: Callable[[str], np.ndarray] = default_embed,
    lambda0: float = 1.0,
    alpha: float = 0.8,
    step_size: float = 1e-2,
    max_steps: int = 50,
) -> Dict[str, str]:
    """
    EN:
    Optimize a set of LLM/agent answers via multiverse GRA functional
    and return a "consensus" answer (chosen from originals).

    RU:
    Оптимизирует набор ответов LLM/агентов через мультиверсный функционал GRA
    и возвращает "консенсусный" ответ (выбранный из исходных).

    Parameters / Параметры:
        answers: list of raw text answers.
        meta_goal: currently unused string, placeholder for future goal logic.
        embed_fn: function text -> np.ndarray embedding.
        lambda0, alpha: hyperparameters Λ_l.
        step_size, max_steps: параметры оптимизатора.

    Returns / Возвращает:
        dict c ключами:
            "chosen"  – выбранный ответ,
            "index"   – его индекс,
            "debug"   – текстовое описание / служебная информация.
    """
    if len(answers) == 0:
        return {"chosen": "", "index": -1, "debug": "no answers provided"}

    # 1. Define levels and goals
    level0 = Level(index=0, name="local_answers")
    level1 = Level(index=1, name="meta_consistency")

    goal0 = Goal(level=level0, description="local plausibility")
    goal1 = Goal(level=level1, description=f"meta goal: {meta_goal}")

    levels = [level0, level1]
    goals = [goal0, goal1]

    # 2. Build initial MultiverseState
    # Use indices (i, 0) for individual answers at level 0,
    # and a single meta-node (0, 1) for level 1.
    states: Dict[Tuple[int, ...], np.ndarray] = {}

    embeds = [embed_fn(a) for a in answers]
    for i, e in enumerate(embeds):
        states[(i, 0)] = e.copy()

    # Meta node: average of all embeddings as initial "consensus"
    meta_vec = np.mean(np.stack(embeds, axis=0), axis=0)
    states[(0, 1)] = meta_vec.astype(np.complex128)

    psi = MultiverseState(states)

    # 3. Create functional and optimizer
    functional = MultiverseFunctional(
        levels=levels,
        goals=goals,
        lambda0=lambda0,
        alpha=alpha,
        index_dim_fn=default_index_dim_fn,
    )

    optimizer = MultiverseOptimizer(
        functional=functional,
        step_size=step_size,
    )

    # 4. Run optimization
    psi_opt = optimizer.run_to_convergence(
        state=psi,
        max_steps=max_steps,
        tol=1e-6,
        callback=None,
    )

    # 5. Choose answer closest to optimized meta-node
    meta_opt = psi_opt[(0, 1)]
    best_idx = 0
    best_sim = -1.0

    for i, e in enumerate(embeds):
        # cosine similarity
        num = float(np.real(np.vdot(e, meta_opt)))
        denom = (np.linalg.norm(e) * np.linalg.norm(meta_opt) + 1e-9)
        sim = num / denom
        if sim > best_sim:
            best_sim = sim
            best_idx = i

    return {
        "chosen": answers[best_idx],
        "index": best_idx,
        "debug": f"best_cosine_similarity={best_sim:.4f}, n_answers={len(answers)}",
    }
