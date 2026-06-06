"""Market regime detection via HMM with optional quantum portfolio optimization."""

__version__ = "0.1.0"

from .data import fetch_prices, compute_features, train_test_split_by_date
from .hmm_detector import RegimeDetector, RegimeLabel
from .backtest import Backtester, BacktestResult
from .strategies import RegimeStrategy
from .pipeline import run_analysis, AnalysisResult
from .sectors import SECTOR_PRESETS, get_preset

__all__ = [
    "fetch_prices",
    "compute_features",
    "train_test_split_by_date",
    "RegimeDetector",
    "RegimeLabel",
    "Backtester",
    "BacktestResult",
    "RegimeStrategy",
    "run_analysis",
    "AnalysisResult",
    "SECTOR_PRESETS",
    "get_preset",
]
