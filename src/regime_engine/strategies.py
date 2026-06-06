"""Regime-conditional portfolio allocation rules."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from .hmm_detector import RegimeLabel


@dataclass
class RegimeStrategy:
    """
    Map market regimes to portfolio weights across assets.

    Default allocations:
      bull     -> 100% risk asset (e.g. SPY)
      bear     -> 100% defensive (e.g. TLT bonds)
      sideways -> balanced mix
    """

    risk_ticker: str = "SPY"
    defensive_ticker: str = "TLT"
    alt_ticker: str = "GLD"

    weights: dict[RegimeLabel, dict[str, float]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.weights:
            self.weights = {
                RegimeLabel.BULL: {self.risk_ticker: 1.0},
                RegimeLabel.BEAR: {self.defensive_ticker: 1.0},
                RegimeLabel.SIDEWAYS: {
                    self.risk_ticker: 0.5,
                    self.defensive_ticker: 0.3,
                    self.alt_ticker: 0.2,
                },
            }

    def get_weights(self, regime: RegimeLabel | str) -> dict[str, float]:
        if isinstance(regime, str):
            regime = RegimeLabel(regime)
        return self.weights.get(regime, {self.risk_ticker: 1.0})

    def build_allocation_series(
        self,
        regimes: pd.Series,
        tickers: list[str],
    ) -> pd.DataFrame:
        """
        Build daily weight matrix aligned to regime series.
        Uses same-day regime (caller should lag for realistic backtest).
        """
        rows = []
        for date, regime in regimes.items():
            w = self.get_weights(regime)
            row = {t: w.get(t, 0.0) for t in tickers}
            rows.append(row)
        return pd.DataFrame(rows, index=regimes.index)


def optimize_weights_mean_variance(
    returns: pd.DataFrame,
    risk_aversion: float = 2.0,
) -> dict[str, float]:
    """
    Classical mean-variance optimal weights (long-only, sum to 1).
    Used as baseline and QAOA comparison target.
    """
    from scipy.optimize import minimize

    tickers = list(returns.columns)
    mu = returns.mean().values
    cov = returns.cov().values
    n = len(tickers)

    def objective(w: np.ndarray) -> float:
        port_ret = w @ mu
        port_var = w @ cov @ w
        return -(port_ret - 0.5 * risk_aversion * port_var)

    constraints = {"type": "eq", "fun": lambda w: np.sum(w) - 1.0}
    bounds = [(0.0, 1.0)] * n
    x0 = np.ones(n) / n

    result = minimize(objective, x0, method="SLSQP", bounds=bounds, constraints=constraints)
    if not result.success:
        return {t: 1.0 / n for t in tickers}

    weights = result.x / result.x.sum()
    return {t: float(w) for t, w in zip(tickers, weights)}


@dataclass
class QuantumRegimeStrategy(RegimeStrategy):
    """
    Per-regime weights from mean-variance optimization.
    Quantum module can replace the optimizer; falls back to classical.
    """

    use_quantum: bool = False
    min_observations: int = 60

    def fit_regime_weights(
        self,
        price_data: pd.DataFrame,
        regimes: pd.Series,
    ) -> None:
        """Learn optimal weights per regime from in-sample returns."""
        returns = price_data.pct_change().dropna()
        aligned = returns.join(regimes.rename("regime"), how="inner")
        aligned["_regime"] = aligned["regime"].map(
            lambda r: RegimeLabel(r.value) if hasattr(r, "value") else RegimeLabel(str(r))
        )

        for regime in RegimeLabel:
            subset = aligned[aligned["_regime"] == regime]
            if len(subset) < self.min_observations:
                continue

            regime_returns = subset.drop(columns=["regime", "_regime"])
            if self.use_quantum:
                from .quantum_opt import quantum_portfolio_weights

                self.weights[regime] = quantum_portfolio_weights(regime_returns)
            else:
                self.weights[regime] = optimize_weights_mean_variance(regime_returns)
