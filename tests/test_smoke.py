"""Smoke tests — require network for yfinance."""

from __future__ import annotations

import pytest

from regime_engine.backtest import Backtester
from regime_engine.data import compute_features, fetch_prices, train_test_split_by_date
from regime_engine.hmm_detector import RegimeDetector, RegimeLabel
from regime_engine.pipeline import run_analysis
from regime_engine.sectors import SECTOR_PRESETS, get_preset
from regime_engine.strategies import RegimeStrategy


@pytest.fixture(scope="module")
def sample_prices():
    return fetch_prices(["SPY", "TLT", "GLD"], period="2y")


def test_fetch_prices(sample_prices):
    assert not sample_prices.empty
    assert "SPY" in sample_prices.columns


def test_features(sample_prices):
    feat = compute_features(sample_prices["SPY"])
    assert {"log_return", "volatility"}.issubset(feat.columns)
    assert len(feat) > 100


def test_hmm_fit_and_predict(sample_prices):
    feat = compute_features(sample_prices["SPY"])
    train, test = train_test_split_by_date(feat, test_years=0.5)
    det = RegimeDetector(n_states=3)
    det.fit(train)
    regimes = det.predict_regimes(test)
    assert len(regimes) == len(test)
    assert regimes.iloc[-1] in RegimeLabel


def test_backtest(sample_prices):
    feat = compute_features(sample_prices["SPY"])
    train, test = train_test_split_by_date(feat, test_years=0.5)
    det = RegimeDetector(n_states=3)
    det.fit(train)
    regimes = det.predict_regimes(test)
    prices = sample_prices.loc[test.index]
    bt = Backtester(prices, regimes, RegimeStrategy())
    metrics = bt.compare()
    assert len(metrics) == 2
    assert "sharpe" in metrics.columns


def test_pipeline_run():
    result = run_analysis(period="3y", test_years=0.5)
    assert result.latest_regime.value in {"bull", "bear", "sideways"}
    assert len(result.metrics) == 2


def test_sector_presets():
    assert len(SECTOR_PRESETS) >= 8
    p = get_preset("technology")
    assert p.primary == "XLK"
