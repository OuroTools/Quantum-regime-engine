"""Fetch and prepare market price data."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Sequence

import numpy as np
import pandas as pd
import yfinance as yf


def fetch_prices(
    tickers: Sequence[str],
    start: str | None = None,
    end: str | None = None,
    period: str = "10y",
) -> pd.DataFrame:
    """
    Download adjusted close prices for one or more tickers.

    Returns a DataFrame indexed by date with one column per ticker.
  """
    if end is None:
        end = datetime.now().strftime("%Y-%m-%d")
    if start is None and period == "":
        start = (datetime.now() - timedelta(days=365 * 10)).strftime("%Y-%m-%d")

    raw = yf.download(
        list(tickers),
        start=start if start else None,
        end=end,
        period=period if not start else None,
        auto_adjust=True,
        progress=False,
        threads=True,
    )

    if raw.empty:
        raise ValueError(f"No data returned for tickers: {tickers}")

    if isinstance(raw.columns, pd.MultiIndex):
        prices = raw["Close"]
    else:
        prices = raw[["Close"]].rename(columns={"Close": tickers[0]})

    if isinstance(prices, pd.Series):
        prices = prices.to_frame()

    prices = prices.dropna(how="all").ffill().dropna()
    return prices


def compute_features(prices: pd.Series, vol_window: int = 21) -> pd.DataFrame:
    """
    Build HMM observation features from a single price series.

    Features: log return, rolling volatility (annualized).
    """
    log_ret = np.log(prices / prices.shift(1))
    vol = log_ret.rolling(vol_window).std() * np.sqrt(252)

    features = pd.DataFrame(
        {"log_return": log_ret, "volatility": vol},
        index=prices.index,
    ).dropna()

    return features


def train_test_split_by_date(
    df: pd.DataFrame,
    test_years: float = 2.0,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split features chronologically; last `test_years` go to test set."""
    if float(test_years).is_integer():
        cutoff = df.index.max() - pd.DateOffset(years=int(test_years))
    else:
        cutoff = df.index.max() - pd.Timedelta(days=int(float(test_years) * 365.25))
    train = df[df.index <= cutoff]
    test = df[df.index > cutoff]
    if train.empty or test.empty:
        raise ValueError("Train or test set is empty after split. Use more history.")
    return train, test
