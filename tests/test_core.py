# tests/test_core.py

import numpy as np

from src.gra_multiverse import (
    Level,
    Goal,
    MultiverseState,
    MultiverseFunctional,
)


def test_multiverse_state_basic():
    # Two simple states at level 0: indices (0,) and (1,)
    psi0 = np.array([1.0 + 0j, 0.0 + 0j])
    psi1 = np.array([0.0 + 0j, 1.0 + 0j])

    state = MultiverseState({
        (0,): psi0,
        (1,): psi1,
    })

    assert (0,) in state.keys()
    assert (1,) in state.keys()
    assert np.allclose(state[(0,)], psi0)
    assert np.allclose(state[(1,)], psi1)


def test_J_multiverse_level0_only():
    # Single level (l=0), simple local functional J_loc = 0.5 * ||psi||^2
    level0 = Level(index=0, name="level0")
    goal0 = Goal(level=level0, description="test goal")

    psi0 = np.array([1.0 + 0j, 0.0 + 0j])
    psi1 = np.array([0.0 + 0j, 2.0 + 0j])

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

    J = functional.J_multiverse(state)

    # J_loc(psi0) = 0.5 * (1^2 + 0^2) = 0.5
    # J_loc(psi1) = 0.5 * (0^2 + 2^2) = 2.0
    # J = λ0 * (0.5 + 2.0) = 2.5
    assert np.isclose(J, 2.5)


def test_J_multiverse_two_levels():
    # Level 0: two states; Level 1: one state. Check that code runs and J>0.
    level0 = Level(index=0, name="local")
    level1 = Level(index=1, name="meta")

    goal0 = Goal(level=level0, description="local goal")
    goal1 = Goal(level=level1, description="meta goal")

    psi0 = np.array([1.0 + 0j, 0.0 + 0j])
    psi1 = np.array([0.0 + 0j, 1.0 + 0j])
    psi_meta = np.array([1.0 + 0j, 1.0 + 0j])

    state = MultiverseState({
        (0, 0): psi0,      # level 0
        (1, 0): psi1,      # level 0
        (0, 1): psi_meta,  # level 1
    })

    def index_dim(a: tuple[int, ...]) -> int:
        # last index is level
        return a[-1]

    functional = MultiverseFunctional(
        levels=[level0, level1],
        goals=[goal0, goal1],
        lambda0=1.0,
        alpha=0.8,
        index_dim_fn=index_dim,
    )

    J = functional.J_multiverse(state)
    assert J > 0.0
