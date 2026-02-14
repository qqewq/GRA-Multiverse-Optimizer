# tests/test_optimizer.py

import numpy as np

from src.gra_multiverse import (
    Level,
    Goal,
    MultiverseState,
    MultiverseFunctional,
    MultiverseOptimizer,
)


def test_optimizer_decreases_J():
    # Уровень 0 с двумя векторами
    level0 = Level(index=0, name="level0")
    goal0 = Goal(level=level0, description="test goal")

    psi0 = np.array([1.0 + 0j, 0.0 + 0j])
    psi1 = np.array([0.5 + 0j, 0.5 + 0j])

    state = MultiverseState({
        (0,): psi0,
        (1,): psi1,
    })

    functional = MultiverseFunctional(
        levels=[level0],
        goals=[goal0],
        lambda0=1.0,
        alpha=0.8,
        index_dim_fn=lambda a: 0,  # всё считаем уровнем 0
    )

    optimizer = MultiverseOptimizer(
        functional=functional,
        step_size=1e-2,
        fd_eps=1e-4,
    )

    J_before = functional.J_multiverse(state)
    state_after = optimizer.run_to_convergence(
        state=state,
        max_steps=20,
        tol=1e-6,
        callback=None,
    )
    J_after = functional.J_multiverse(state_after)

    # Ожидаем, что функционал уменьшится или останется тем же
    assert J_after <= J_before + 1e-6


def test_optimizer_single_step_runs():
    # Простейший тест, что step() не падает
    level0 = Level(index=0, name="level0")
    goal0 = Goal(level=level0, description="test goal")

    psi0 = np.array([1.0 + 0j, -1.0 + 0j])

    state = MultiverseState({
        (0,): psi0,
    })

    functional = MultiverseFunctional(
        levels=[level0],
        goals=[goal0],
        lambda0=1.0,
        alpha=0.8,
        index_dim_fn=lambda a: 0,
    )

    optimizer = MultiverseOptimizer(
        functional=functional,
        step_size=1e-2,
        fd_eps=1e-4,
    )

    new_state = optimizer.step(state)
    assert (0,) in new_state.keys()
    assert new_state[(0,)].shape == psi0.shape
