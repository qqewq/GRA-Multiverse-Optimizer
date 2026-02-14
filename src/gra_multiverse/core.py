# src/gra_multiverse/core.py

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Callable
import numpy as np


@dataclass
class Level:
    """One abstraction level l in the multiverse."""
    index: int
    name: str


@dataclass
class Goal:
    """Goal G_l for a given level."""
    level: Level
    description: str
    # User can attach arbitrary payload, e.g. constraints, target data, etc.
    payload: Dict[str, Any] | None = None


class MultiverseState:
    """
    Container for Ψ = {Ψ^(a)} over all multi-indices a.
    Internally we represent it as a dict: key = tuple (multi-index), value = np.ndarray.
    """

    def __init__(self, states: Dict[Tuple[int, ...], np.ndarray]):
        self.states = states  # { (a0, a1, ...): vector }

    def copy(self) -> "MultiverseState":
        return MultiverseState({k: v.copy() for k, v in self.states.items()})

    def keys(self):
        return self.states.keys()

    def __getitem__(self, key: Tuple[int, ...]) -> np.ndarray:
        return self.states[key]

    def __setitem__(self, key: Tuple[int, ...], value: np.ndarray) -> None:
        self.states[key] = value


class FoamFunctional:
    """
    Φ^(l)(Ψ^(l), G_l): simple placeholder implementation.
    In your theory it sums |<Ψ^a | P_G | Ψ^b>|^2 over a≠b with dim(a)=dim(b)=l.
    Here we approximate P_G as identity (for prototype).
    """

    def __init__(self, projector: Callable[[np.ndarray], np.ndarray] | None = None):
        # projector(x) ≈ P_G x; default = identity
        self.projector = projector if projector is not None else (lambda x: x)

    def phi_level(
        self,
        state: MultiverseState,
        level: Level,
        index_dim_fn: Callable[[Tuple[int, ...]], int],
    ) -> float:
        """Compute Φ^(l) over all pairs with dim(a)=dim(b)=l."""
        keys = [k for k in state.keys() if index_dim_fn(k) == level.index]
        val = 0.0
        for i in range(len(keys)):
            for j in range(len(keys)):
                if i == j:
                    continue
                a, b = keys[i], keys[j]
                psi_a = state[a]
                psi_b = state[b]
                p_psi_b = self.projector(psi_b)
                inner = float(np.vdot(psi_a, p_psi_b))
                val += abs(inner) ** 2
        return val


class MultiverseFunctional:
    """
    J_multiverse(Ψ) = sum_l Λ_l sum_{dim(a)=l} J^(l)(Ψ^(a)).
    For prototype we implement a simple quadratic J_loc at level 0
    and J^(l) = sum J^(l-1) + Φ^(l) structurally.
    """

    def __init__(
        self,
        levels: List[Level],
        goals: List[Goal],
        lambda0: float = 1.0,
        alpha: float = 0.8,
        index_dim_fn: Callable[[Tuple[int, ...]], int] | None = None,
    ):
        self.levels = levels
        self.goals = goals
        self.lambda0 = lambda0
        self.alpha = alpha
        self.index_dim_fn = index_dim_fn if index_dim_fn is not None else (lambda a: len(a) - 1)
        self.foam = FoamFunctional()

    def lambda_l(self, l: int) -> float:
        return self.lambda0 * (self.alpha ** l)

    # ---- Local J_loc prototype ----
    def J_loc(self, psi: np.ndarray, goal: Goal | None = None) -> float:
        """
        Prototype: J_loc = 0.5 * ||psi||^2.
        You can replace this with task-specific loss later.
        """
        return 0.5 * float(np.vdot(psi, psi).real)

    def J_multiverse(self, state: MultiverseState) -> float:
        """Compute scalar J_multiverse(Ψ) for current state."""
        total = 0.0
        # level-wise
        for level in self.levels:
            lam = self.lambda_l(level.index)
            # local contributions J^(0) ~ J_loc
            if level.index == 0:
                for k in state.keys():
                    if self.index_dim_fn(k) != 0:
                        continue
                    total += lam * self.J_loc(state[k])
            else:
                # For prototype: add Φ^(l) only (no explicit recursion of J^(l-1))
                total += lam * self.foam.phi_level(state, level, self.index_dim_fn)
        return total
