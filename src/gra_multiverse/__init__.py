# src/gra_multiverse/__init__.py
"""
GRA-Multiverse-Optimizer

EN:
Core interfaces for the multilevel GRA Meta-Obnulyonka "multiverse optimizer".
This package provides:
- Level, Goal: abstraction levels and goals G_l
- MultiverseState: container for Ψ = {Ψ^(a)}
- MultiverseFunctional: J_multiverse(Ψ) and foam Φ^(l)
- MultiverseOptimizer: simple gradient-based optimizer over Ψ

RU:
Базовые интерфейсы для многоуровневого оптимизатора GRA Мета-обнулёнки.
Пакет предоставляет:
- Level, Goal: абстрактные уровни и цели G_l
- MultiverseState: контейнер для Ψ = {Ψ^(a)}
- MultiverseFunctional: функционал J_multiverse(Ψ) и пена Φ^(l)
- MultiverseOptimizer: простой градиентный оптимизатор по Ψ
"""

from .core import (
    Level,
    Goal,
    MultiverseState,
    MultiverseFunctional,
)

from .optimizer import (
    MultiverseOptimizer,
)

__all__ = [
    "Level",
    "Goal",
    "MultiverseState",
    "MultiverseFunctional",
    "MultiverseOptimizer",
]
