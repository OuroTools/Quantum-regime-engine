#!/usr/bin/env python3
"""Run a quick health check on the full tool."""

from __future__ import annotations

import sys


def check(name: str, fn) -> bool:
    try:
        fn()
        print(f"  OK  {name}")
        return True
    except Exception as exc:
        print(f"  FAIL {name}: {exc}")
        return False


def main() -> int:
    print("Regime Detection Engine — verification\n")

    ok = True

    def imports():
        import regime_engine  # noqa: F401
        from regime_engine import dashboard_app  # noqa: F401

    ok &= check("imports", imports)

    def pipeline():
        from regime_engine.pipeline import run_analysis

        r = run_analysis(period="3y", test_years=1.0)
        assert r.latest_regime.value in ("bull", "bear", "sideways")

    ok &= check("pipeline (live data)", pipeline)

    def charts():
        from regime_engine.interactive_charts import allocation_pie

        fig = allocation_pie({"SPY": 0.6, "TLT": 0.4})
        assert fig is not None

    ok &= check("plotly charts", charts)

    def quantum_optional():
        try:
            from regime_engine.quantum_opt import quantum_portfolio_weights
            import pandas as pd

            rets = pd.DataFrame({"SPY": [0.01, -0.02, 0.005] * 30, "TLT": [0.002, 0.001, -0.001] * 30})
            w = quantum_portfolio_weights(rets)
            assert abs(sum(w.values()) - 1.0) < 0.01
        except ImportError:
            print("  SKIP quantum (install with: pip install -e \".[quantum]\")")

    quantum_optional()

    print()
    if ok:
        print("All required checks passed. Tool is ready.")
        print("\nNext steps:")
        print("  regime-engine              # CLI")
        print("  regime-dashboard           # Web UI")
        print("  streamlit run dashboard.py # Web UI (dev)")
        return 0
    print("Some checks failed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
