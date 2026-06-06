"""Shared analysis pipeline used by CLI, dashboard, and notebook."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import pandas as pd

from .backtest import Backtester, BacktestResult
from .data import compute_features, fetch_prices, train_test_split_by_date
from .hmm_detector import RegimeDetector, RegimeLabel
from .strategies import QuantumRegimeStrategy, RegimeStrategy
from .visualize import print_report


@dataclass
class AnalysisResult:
    primary_ticker: str
    portfolio_tickers: list[str]
    prices: pd.DataFrame
    train_features: pd.DataFrame
    test_features: pd.DataFrame
    detector: RegimeDetector
    train_regimes: pd.Series
    test_regimes: pd.Series
    regime_summary: pd.DataFrame
    transition_matrix: pd.DataFrame
    strategy: RegimeStrategy
    buy_hold: BacktestResult
    regime_switch: BacktestResult
    metrics: pd.DataFrame
    report_text: str

    @property
    def latest_regime(self) -> RegimeLabel:
        r = self.test_regimes.iloc[-1]
        if isinstance(r, RegimeLabel):
            return r
        return RegimeLabel(str(r))

    @property
    def latest_date(self) -> str:
        return self.test_regimes.index[-1].strftime("%Y-%m-%d")

    @property
    def current_allocation(self) -> dict[str, float]:
        return self.strategy.get_weights(self.latest_regime)


def run_analysis(
    primary_ticker: str = "SPY",
    portfolio_tickers: Sequence[str] | None = None,
    period: str = "10y",
    test_years: float = 2.0,
    n_states: int = 3,
    use_quantum: bool = False,
) -> AnalysisResult:
    """
    End-to-end: fetch data, train HMM, backtest strategies, return results.
    """
    portfolio = list(portfolio_tickers or ["SPY", "TLT", "GLD"])
    tickers = list(dict.fromkeys([primary_ticker, *portfolio]))

    prices = fetch_prices(tickers, period=period)
    if primary_ticker not in prices.columns:
        raise ValueError(f"Ticker {primary_ticker} not found in downloaded data.")

    features = compute_features(prices[primary_ticker])
    train_feat, test_feat = train_test_split_by_date(features, test_years=test_years)

    detector = RegimeDetector(n_states=n_states)
    detector.fit(train_feat)

    train_regimes = detector.predict_regimes(train_feat)
    test_regimes = detector.predict_regimes(test_feat)
    regime_summary = detector.regime_summary(train_feat, train_regimes)
    transition_matrix = detector.transition_matrix()

    risk = primary_ticker
    defensive = "TLT" if "TLT" in portfolio else (portfolio[1] if len(portfolio) > 1 else "TLT")
    alt = "GLD" if "GLD" in portfolio else (portfolio[-1] if len(portfolio) > 2 else "GLD")

    if use_quantum:
        strategy: RegimeStrategy = QuantumRegimeStrategy(
            risk_ticker=risk,
            defensive_ticker=defensive,
            alt_ticker=alt,
            use_quantum=True,
        )
        strategy.fit_regime_weights(prices.loc[train_feat.index], train_regimes)
    else:
        strategy = RegimeStrategy(
            risk_ticker=risk,
            defensive_ticker=defensive,
            alt_ticker=alt,
        )

    test_prices = prices.loc[test_feat.index]
    backtester = Backtester(test_prices, test_regimes, strategy)
    bh = backtester.run_buy_and_hold(primary_ticker)
    rs = backtester.run_regime_switching()
    metrics = backtester.compare()
    report = print_report(regime_summary, transition_matrix, metrics)

    return AnalysisResult(
        primary_ticker=primary_ticker,
        portfolio_tickers=portfolio,
        prices=prices,
        train_features=train_feat,
        test_features=test_feat,
        detector=detector,
        train_regimes=train_regimes,
        test_regimes=test_regimes,
        regime_summary=regime_summary,
        transition_matrix=transition_matrix,
        strategy=strategy,
        buy_hold=bh,
        regime_switch=rs,
        metrics=metrics,
        report_text=report,
    )
