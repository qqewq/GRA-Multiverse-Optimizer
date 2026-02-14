# src/gra_multiverse/optimizer.py

from typing import Callable, Dict, Tuple
import numpy as np

from .core import MultiverseState, MultiverseFunctional, Level


class MultiverseOptimizer:
    """
    Simple gradient-descent optimizer over MultiverseState for J_multiverse.
    Gradients are approximated by finite differences (prototype).
    """

    def __init__(
        self,
        functional: MultiverseFunctional,
        step_size: float = 1e-2,
        fd_eps: float = 1e-4,
    ):
        self.functional = functional
        self.step_size = step_size
        self.fd_eps = fd_eps

    def _finite_diff_grad(self, state: MultiverseState) -> Dict[Tuple[int, ...], np.ndarray]:
        """
        Naive finite-difference gradient:
        ∂J/∂ψ ≈ (J(ψ+εe_i) - J(ψ-εe_i)) / (2ε).
        """
        grads: Dict[Tuple[int, ...], np.ndarray] = {}
        base_val = self.functional.J_multiverse(state)
        for k in state.keys():
            psi = state[k]
            grad = np.zeros_like(psi, dtype=np.complex128)
            for i in range(psi.size):
                e = np.zeros_like(psi, dtype=np.complex128)
                e.flat[i] = self.fd_eps
                # plus
                state_plus = state.copy()
                state_plus[k] = psi + e
                jp = self.functional.J_multiverse(state_plus)
                # minus
                state_minus = state.copy()
                state_minus[k] = psi - e
                jm = self.functional.J_multiverse(state_minus)
                grad.flat[i] = (jp - jm) / (2.0 * self.fd_eps)
            grads[k] = grad
        return grads

    def step(self, state: MultiverseState) -> MultiverseState:
        """One gradient-descent step: Ψ <- Ψ - η ∇J."""
        grads = self._finite_diff_grad(state)
        new_state = state.copy()
        for k, g in grads.items():
            new_state[k] = state[k] - self.step_size * g
        return new_state

    def run_to_convergence(
        self,
        state: MultiverseState,
        max_steps: int = 100,
        tol: float = 1e-6,
        callback: Callable[[int, float], None] | None = None,
    ) -> MultiverseState:
        """
        Run gradient descent until ||ΔΨ|| < tol or max_steps reached.
        """
        prev_val = self.functional.J_multiverse(state)
        for t in range(max_steps):
            new_state = self.step(state)
            val = self.functional.J_multiverse(new_state)
            if callback is not None:
                callback(t, val)
            # simple stopping criterion
            if abs(val - prev_val) < tol:
                return new_state
            state = new_state
            prev_val = val
        return state
