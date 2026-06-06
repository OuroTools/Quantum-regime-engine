"""Plotting utilities for regime detection results."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from .backtest import BacktestResult
from .hmm_detector import RegimeLabel


REGIME_COLORS = {
    RegimeLabel.BULL.value: "#22c55e",
    RegimeLabel.BEAR.value: "#ef4444",
    RegimeLabel.SIDEWAYS.value: "#eab308",
}


def _regime_strings(regimes: pd.Series) -> pd.Series:
    return regimes.map(lambda r: r.value if hasattr(r, "value") else str(r))


def make_regime_figure(
    prices: pd.Series,
    regimes: pd.Series,
    title: str = "Price with Detected Regimes",
):
    """Build matplotlib figure for price + regime shading (for web/notebook)."""
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(prices.index, prices.values, color="#1e293b", linewidth=1.2, label="Price")

    regime_str = _regime_strings(regimes)
    y_min, y_max = float(prices.min()) * 0.95, float(prices.max()) * 1.05
    for regime_val, color in REGIME_COLORS.items():
        mask = regime_str == regime_val
        if mask.any():
            ax.fill_between(
                prices.index,
                y_min,
                y_max,
                where=mask.reindex(prices.index, fill_value=False),
                alpha=0.15,
                color=color,
                label=regime_val,
            )

    ax.set_title(title)
    ax.set_ylabel("Price")
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig


def make_equity_figure(
    results: list[BacktestResult],
    title: str = "Strategy Comparison",
):
    """Build matplotlib figure comparing equity curves."""
    fig, ax = plt.subplots(figsize=(14, 6))
    for r in results:
        ax.plot(r.equity_curve.index, r.equity_curve.values, label=r.name, linewidth=1.5)

    ax.set_title(title)
    ax.set_ylabel("Growth of $1")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig


def plot_regimes_on_price(
    prices: pd.Series,
    regimes: pd.Series,
    output_path: Path | None = None,
    title: str = "Price with Detected Regimes",
) -> None:
    fig = make_regime_figure(prices, regimes, title=title)
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=150)
        plt.close(fig)
    else:
        plt.show()


def plot_equity_curves(
    results: list[BacktestResult],
    output_path: Path | None = None,
    title: str = "Strategy Comparison",
) -> None:
    fig = make_equity_figure(results, title=title)
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=150)
        plt.close(fig)
    else:
        plt.show()


def print_report(
    regime_summary: pd.DataFrame,
    transition_matrix: pd.DataFrame,
    backtest_metrics: pd.DataFrame,
) -> str:
    lines = [
        "=" * 60,
        "REGIME DETECTION ENGINE - REPORT",
        "=" * 60,
        "",
        "Regime Statistics (in-sample):",
        regime_summary.to_string(),
        "",
        "Transition Matrix (probability of moving between regimes):",
        transition_matrix.round(3).to_string(),
        "",
        "Backtest Comparison (out-of-sample):",
        backtest_metrics.round(4).to_string(),
        "",
        "=" * 60,
    ]
    return "\n".join(lines)
