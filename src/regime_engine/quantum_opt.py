"""
Quantum-inspired portfolio optimization via QAOA.

Formulates long-only mean-variance portfolio selection as a QUBO and solves
with Qiskit's QAOA. Falls back to classical SLSQP if quantum solve fails or
asset count exceeds qubit budget.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

MAX_QAOA_ASSETS = 4  # 4 qubits keeps simulation tractable on CPU


def _mean_variance_qubo(
    mu: np.ndarray,
    cov: np.ndarray,
    risk_aversion: float = 2.0,
    penalty: float = 10.0,
) -> np.ndarray:
    """
    Build QUBO matrix for binary asset selection + weight discretization.

    Simplified: n binary variables = include asset i (equal weight among selected).
    Objective approximates max return - risk_aversion/2 * variance with budget penalty.
    """
    n = len(mu)
    Q = np.zeros((n, n))

    for i in range(n):
        Q[i, i] += -mu[i] + 0.5 * risk_aversion * cov[i, i]
        for j in range(i + 1, n):
            cross = risk_aversion * cov[i, j]
            Q[i, j] += cross
            Q[j, i] += cross

    # Penalty (sum x_i - 1)^2 encourages selecting exactly one asset for n=1 budget
    # For multi-asset: encourage 2-3 selections via diagonal adjustment
    target_k = min(2, n)
    for i in range(n):
        Q[i, i] += penalty * (1 - 2 * target_k)
        for j in range(n):
            if i != j:
                Q[i, j] += penalty

    return Q


def _qubo_to_weights(bitstring: str, tickers: list[str]) -> dict[str, float]:
    """Convert QAOA bitstring to normalized long-only weights."""
    bits = [int(b) for b in bitstring]
    selected = [i for i, b in enumerate(bits) if b == 1]
    n = len(tickers)
    weights = np.zeros(n)
    if not selected:
        weights[:] = 1.0 / n
    else:
        for i in selected:
            weights[i] = 1.0 / len(selected)
    return {t: float(w) for t, w in zip(tickers, weights)}


def quantum_portfolio_weights(
    returns: pd.DataFrame,
    risk_aversion: float = 2.0,
    reps: int = 2,
) -> dict[str, float]:
    """
    Solve portfolio weight selection with QAOA; classical fallback on failure.

    For >4 assets, subsamples top-volatility assets or uses classical opt.
    """
    from .strategies import optimize_weights_mean_variance

    tickers = list(returns.columns)
    if len(tickers) > MAX_QAOA_ASSETS:
        logger.info(
            "Too many assets (%d) for QAOA; using classical optimizer.",
            len(tickers),
        )
        return optimize_weights_mean_variance(returns, risk_aversion)

    mu = returns.mean().values
    cov = returns.cov().values
    Q = _mean_variance_qubo(mu, cov, risk_aversion)

    try:
        from qiskit_algorithms import QAOA
        from qiskit_algorithms.optimizers import COBYLA
        from qiskit_optimization import QuadraticProgram
        from qiskit_optimization.algorithms import MinimumEigenOptimizer
        from qiskit.primitives import StatevectorSampler

        qp = QuadraticProgram()
        for i in range(len(tickers)):
            qp.binary_var(name=f"x{i}")

        linear = {f"x{i}": float(Q[i, i]) for i in range(len(tickers))}
        quadratic = {}
        for i in range(len(tickers)):
            for j in range(i + 1, len(tickers)):
                if Q[i, j] != 0:
                    quadratic[(f"x{i}", f"x{j}")] = float(Q[i, j])

        qp.minimize(linear=linear, quadratic=quadratic)
        sampler = StatevectorSampler()
        qaoa = QAOA(sampler=sampler, optimizer=COBYLA(maxiter=100), reps=reps)
        optimizer = MinimumEigenOptimizer(qaoa)
        result = optimizer.solve(qp)

        x = result.x
        bits = "".join(str(int(v)) for v in x)
        return _qubo_to_weights(bits, tickers)

    except Exception as exc:
        logger.warning("QAOA failed (%s); falling back to classical.", exc)
        return optimize_weights_mean_variance(returns, risk_aversion)
