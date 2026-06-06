"""Backtest regime-switching vs buy-and-hold."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .strategies import RegimeStrategy


@dataclass
class BacktestResult:
    name: str
    equity_curve: pd.Series
    daily_returns: pd.Series
    metrics: dict[str, float]


def _compute_metrics(returns: pd.Series, name: str) -> dict[str, float]:
    returns = returns.dropna()
    if returns.empty:
        return {
            "strategy": name,
            "total_return": 0.0,
            "ann_return": 0.0,
            "ann_vol": 0.0,
            "sharpe": 0.0,
            "max_drawdown": 0.0,
        }

    equity = (1 + returns).cumprod()
    total_return = float(equity.iloc[-1] - 1)
    ann_factor = 252
    ann_return = float((1 + returns.mean()) ** ann_factor - 1)
    ann_vol = float(returns.std() * np.sqrt(ann_factor))
    sharpe = ann_return / ann_vol if ann_vol > 0 else 0.0

    rolling_max = equity.cummax()
    drawdown = equity / rolling_max - 1
    max_dd = float(drawdown.min())

    return {
        "strategy": name,
        "total_return": total_return,
        "ann_return": ann_return,
        "ann_vol": ann_vol,
        "sharpe": sharpe,
        "max_drawdown": max_dd,
    }


class Backtester:
    """Compare buy-and-hold against regime-switching allocation."""

    def __init__(
        self,
        prices: pd.DataFrame,
        regimes: pd.Series,
        strategy: RegimeStrategy,
        rebalance_cost_bps: float = 5.0,
    ):
        self.prices = prices
        self.regimes = regimes
        self.strategy = strategy
        self.rebalance_cost_bps = rebalance_cost_bps

    def _portfolio_returns(
        self,
        weights: pd.DataFrame,
        asset_returns: pd.DataFrame,
    ) -> pd.Series:
        """Compute daily portfolio return with lagged weights (no lookahead)."""
        w_lagged = weights.shift(1).ffill()
        aligned = w_lagged.join(asset_returns, how="inner", rsuffix="_ret")

        tickers = list(asset_returns.columns)
        port_ret = pd.Series(0.0, index=aligned.index)
        for t in tickers:
            port_ret += aligned[t].fillna(0) * aligned[f"{t}_ret"].fillna(0)

        # Transaction costs on weight changes
        weight_change = w_lagged.diff().abs().sum(axis=1)
        cost = weight_change * (self.rebalance_cost_bps / 10_000)
        port_ret = port_ret - cost.fillna(0)

        return port_ret

    def run_buy_and_hold(self, ticker: str | None = None) -> BacktestResult:
        ticker = ticker or self.strategy.risk_ticker
        asset_returns = self.prices.pct_change().dropna()
        if ticker not in asset_returns.columns:
            raise ValueError(f"Ticker {ticker} not in price data.")

        returns = asset_returns[ticker]
        equity = (1 + returns).cumprod()
        metrics = _compute_metrics(returns, f"Buy & Hold ({ticker})")
        return BacktestResult(
            name=metrics["strategy"],
            equity_curve=equity,
            daily_returns=returns,
            metrics=metrics,
        )

    def run_regime_switching(self) -> BacktestResult:
        asset_returns = self.prices.pct_change().dropna()
        common_idx = self.regimes.index.intersection(asset_returns.index)
        regimes = self.regimes.loc[common_idx]
        asset_returns = asset_returns.loc[common_idx]

        tickers = list(asset_returns.columns)
        weights = self.strategy.build_allocation_series(regimes, tickers)
        returns = self._portfolio_returns(weights, asset_returns)
        equity = (1 + returns).cumprod()

        metrics = _compute_metrics(returns, "Regime Switching")
        return BacktestResult(
            name=metrics["strategy"],
            equity_curve=equity,
            daily_returns=returns,
            metrics=metrics,
        )

    def compare(self) -> pd.DataFrame:
        """Run both strategies and return metrics side by side."""
        bh = self.run_buy_and_hold()
        rs = self.run_regime_switching()
        return pd.DataFrame([bh.metrics, rs.metrics]).set_index("strategy")
