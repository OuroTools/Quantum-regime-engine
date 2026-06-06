"""Console entry points for pip-installed commands."""

from __future__ import annotations

import argparse
import logging
import subprocess
import sys
from pathlib import Path

from .pipeline import run_analysis
from .sectors import SECTOR_PRESETS, get_preset
from .visualize import plot_equity_curves, plot_regimes_on_price

logger = logging.getLogger(__name__)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="regime-engine",
        description="Market regime detection with HMM + backtest",
    )
    p.add_argument("--ticker", default=None, help="Primary ticker (overrides preset)")
    p.add_argument("--portfolio", nargs="+", default=None, help="Portfolio tickers")
    p.add_argument(
        "--sector",
        choices=list(SECTOR_PRESETS.keys()),
        default="broad_market",
        help="Sector preset",
    )
    p.add_argument("--period", default="10y", help="History period (yfinance)")
    p.add_argument("--test-years", type=float, default=2.0, help="OOS test years")
    p.add_argument("--states", type=int, default=3, help="HMM latent states")
    p.add_argument("--quantum", action="store_true", help="QAOA per-regime weights")
    p.add_argument("--output", type=Path, default=Path("output"), help="Output directory")
    return p


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = _build_parser().parse_args(argv)

    preset = get_preset(args.sector)
    primary = args.ticker or preset.primary
    portfolio = args.portfolio or list(preset.portfolio)

    logger.info("Sector: %s | Primary: %s | Portfolio: %s", preset.name, primary, portfolio)

    try:
        result = run_analysis(
            primary_ticker=primary,
            portfolio_tickers=portfolio,
            period=args.period,
            test_years=args.test_years,
            n_states=args.states,
            use_quantum=args.quantum,
        )
    except Exception as exc:
        logger.error("Analysis failed: %s", exc)
        return 1

    print(result.report_text)

    args.output.mkdir(parents=True, exist_ok=True)
    plot_regimes_on_price(
        result.prices[primary].loc[result.test_features.index],
        result.test_regimes,
        output_path=args.output / "regimes_oos.png",
        title=f"{primary} - Out-of-Sample Regimes",
    )
    plot_equity_curves(
        [result.buy_hold, result.regime_switch],
        output_path=args.output / "equity_curves.png",
        title="OOS Backtest: Buy & Hold vs Regime Switching",
    )
    (args.output / "report.txt").write_text(result.report_text, encoding="utf-8")
    logger.info("Saved plots and report to %s", args.output.resolve())

    print(f"\nLatest OOS regime ({result.latest_date}): {result.latest_regime.value}")
    print(f"Suggested allocation: {result.current_allocation}")
    return 0


def dashboard_main() -> int:
    app = Path(__file__).resolve().parent / "dashboard_app.py"
    return subprocess.call(
        [sys.executable, "-m", "streamlit", "run", str(app), "--server.headless", "true"]
    )


if __name__ == "__main__":
    raise SystemExit(main())
