"""Regime Detection Engine — Streamlit web dashboard."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from .interactive_charts import (
    allocation_pie,
    equity_curve_chart,
    regime_price_chart,
    regime_timeline,
    transition_heatmap,
)
from .pipeline import run_analysis
from .sectors import SECTOR_PRESETS

st.set_page_config(
    page_title="Regime Detection Engine",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

REGIME_META = {
    "bull": {"emoji": "🐂", "color": "#22c55e", "hint": "Prices have been rising more than usual."},
    "bear": {"emoji": "🐻", "color": "#ef4444", "hint": "Prices have been falling or very volatile."},
    "sideways": {"emoji": "↔️", "color": "#eab308", "hint": "Choppy market — no clear up or down trend."},
}


def inject_css() -> None:
    st.markdown(
        """
        <style>
        .regime-banner {
            padding: 1.25rem 1.5rem;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
            margin-bottom: 1rem;
        }
        .regime-title { font-size: 1.75rem; font-weight: 700; margin: 0; }
        .regime-sub { color: #64748b; margin-top: 0.35rem; }
        div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            padding: 0.75rem 1rem;
            border-radius: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def cached_analysis(
    primary: str,
    portfolio: tuple[str, ...],
    period: str,
    test_years: float,
    n_states: int,
    use_quantum: bool,
):
    return run_analysis(
        primary_ticker=primary,
        portfolio_tickers=list(portfolio),
        period=period,
        test_years=test_years,
        n_states=n_states,
        use_quantum=use_quantum,
    )


def render_sidebar() -> tuple[str, tuple[str, ...], str, float, int, bool, bool]:
    with st.sidebar:
        st.markdown("## 📈 Settings")
        st.caption("Configure tickers and model, then run.")

        preset_options = {p.name: key for key, p in SECTOR_PRESETS.items()}
        chosen_name = st.selectbox("Sector preset", list(preset_options.keys()))
        preset = SECTOR_PRESETS[preset_options[chosen_name]]
        st.info(preset.description)

        use_custom = st.checkbox("Custom tickers")
        if use_custom:
            primary = st.text_input("Primary (regime detection)", "SPY").strip().upper()
            raw = st.text_input("Portfolio (comma-separated)", "SPY, TLT, GLD")
            portfolio = tuple(t.strip().upper() for t in raw.split(",") if t.strip())
        else:
            primary = preset.primary
            portfolio = preset.portfolio
            st.markdown(f"**Primary:** `{primary}`")
            st.markdown(f"**Portfolio:** {', '.join(f'`{t}`' for t in portfolio)}")

        st.divider()
        period = st.selectbox("Price history", ["5y", "10y", "15y", "max"], index=1)
        test_years = st.slider("Out-of-sample test (years)", 1.0, 5.0, 2.0, 0.5)
        n_states = st.slider("HMM states", 2, 4, 3)
        use_quantum = st.checkbox("Quantum optimizer (QAOA)", help="Slower; uses Qiskit per-regime.")

        st.divider()
        run_btn = st.button("Run analysis", type="primary", use_container_width=True)
        auto_run = st.checkbox("Auto-run on load", value=True)
        st.session_state["auto_run_enabled"] = auto_run

        with st.expander("How to use"):
            st.markdown(
                """
                1. Pick a **sector** or enter tickers.
                2. Click **Run analysis**.
                3. Read the **current regime** and allocation.
                4. Compare strategies in the **Backtest** tab.

                Not financial advice. Research tool only.
                """
            )

    return primary, portfolio, period, test_years, n_states, use_quantum, run_btn


def render_regime_banner(regime: str, date: str, primary: str) -> None:
    meta = REGIME_META.get(regime, {"emoji": "❓", "color": "#64748b", "hint": ""})
    st.markdown(
        f"""
        <div class="regime-banner" style="border-left: 6px solid {meta['color']};">
            <p class="regime-title">{meta['emoji']} Current regime: {regime.upper()}</p>
            <p class="regime-sub">{primary} as of {date} — {meta['hint']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpis(result) -> None:
    bh = result.buy_hold.metrics
    rs = result.regime_switch.metrics
    sharpe_delta = rs["sharpe"] - bh["sharpe"]
    dd_delta = rs["max_drawdown"] - bh["max_drawdown"]

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Buy & hold return", f"{bh['ann_return']:.1%}", help="Annualized return, test period")
    c2.metric("Regime switch return", f"{rs['ann_return']:.1%}")
    c3.metric("Sharpe (regime)", f"{rs['sharpe']:.2f}", delta=f"{sharpe_delta:+.2f} vs B&H")
    c4.metric("Max drawdown (regime)", f"{rs['max_drawdown']:.1%}", delta=f"{dd_delta:+.1%} vs B&H")
    c5.metric("Train / test days", f"{len(result.train_features)} / {len(result.test_features)}")


def render_overview(result) -> None:
    regime = result.latest_regime.value
    render_regime_banner(regime, result.latest_date, result.primary_ticker)
    render_kpis(result)

    left, right = st.columns([1, 1])
    with left:
        st.plotly_chart(
            allocation_pie(result.current_allocation, "Today's suggested allocation"),
            use_container_width=True,
        )
        alloc = pd.DataFrame(
            {"Ticker": list(result.current_allocation), "Weight": list(result.current_allocation.values())}
        )
        alloc["Weight"] = alloc["Weight"].map(lambda x: f"{x:.1%}")
        st.dataframe(alloc, hide_index=True, use_container_width=True)

    with right:
        rules = result.strategy.weights
        rows = []
        for mood, w in rules.items():
            label = mood.value if hasattr(mood, "value") else str(mood)
            rows.append({"Regime": label, "Allocation": ", ".join(f"{k} {v:.0%}" for k, v in w.items())})
        st.markdown("**Strategy rulebook**")
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)


def render_charts(result) -> None:
    test_prices = result.prices[result.primary_ticker].loc[result.test_features.index]
    st.plotly_chart(
        regime_price_chart(
            test_prices,
            result.test_regimes,
            f"{result.primary_ticker} price with regimes (out-of-sample)",
        ),
        use_container_width=True,
    )
    st.plotly_chart(regime_timeline(result.test_regimes), use_container_width=True)
    st.plotly_chart(
        equity_curve_chart(
            [result.buy_hold, result.regime_switch],
            "Buy & hold vs regime switching",
        ),
        use_container_width=True,
    )


def render_backtest(result) -> None:
    display = result.metrics.copy()
    for col in ["total_return", "ann_return", "ann_vol", "max_drawdown"]:
        if col in display.columns:
            display[col] = display[col].map(lambda x: f"{x:.2%}")
    if "sharpe" in display.columns:
        display["sharpe"] = display["sharpe"].map(lambda x: f"{x:.2f}")
    st.dataframe(display, use_container_width=True)
    st.markdown(
        """
        | Metric | Meaning |
        |--------|---------|
        | **Sharpe** | Return per unit of risk — higher is better |
        | **Max drawdown** | Worst peak-to-trough drop — closer to 0% is better |
        | **Ann. vol** | How bumpy the ride was |
        """
    )
    winner = (
        "Regime switching"
        if result.regime_switch.metrics["sharpe"] > result.buy_hold.metrics["sharpe"]
        else "Buy & hold"
    )
    st.success(f"Higher risk-adjusted return (Sharpe) on test data: **{winner}**")


def render_regime_stats(result) -> None:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**In-sample regime statistics**")
        st.dataframe(result.regime_summary, use_container_width=True)
    with c2:
        st.plotly_chart(transition_heatmap(result.transition_matrix), use_container_width=True)
    st.caption("Transition matrix: probability of moving from row regime to column regime the next day.")


def render_report(result) -> None:
    st.code(result.report_text, language=None)
    st.download_button(
        "Download report (.txt)",
        data=result.report_text,
        file_name=f"regime_report_{result.primary_ticker}.txt",
        mime="text/plain",
    )
    metrics_csv = result.metrics.to_csv()
    st.download_button(
        "Download metrics (.csv)",
        data=metrics_csv,
        file_name=f"backtest_metrics_{result.primary_ticker}.csv",
        mime="text/csv",
    )


def main() -> None:
    inject_css()
    st.title("Regime Detection Engine")
    st.caption("Detect bull / bear / sideways markets with an HMM and backtest regime-switching strategies.")

    primary, portfolio, period, test_years, n_states, use_quantum, run_clicked = render_sidebar()

    params = (primary, portfolio, period, test_years, n_states, use_quantum)
    prev_params = st.session_state.get("params")
    auto_run = st.session_state.get("auto_run_enabled", True)

    needs_run = (
        run_clicked
        or (auto_run and prev_params != params)
        or ("result" not in st.session_state and auto_run)
    )

    if needs_run:
        with st.spinner("Downloading prices, training HMM, running backtest..."):
            try:
                st.session_state["result"] = cached_analysis(
                    primary, portfolio, period, test_years, n_states, use_quantum
                )
                st.session_state["params"] = params
            except Exception as exc:
                st.error(f"Analysis failed: {exc}")
                st.stop()
    elif prev_params != params:
        st.info("Settings changed — click **Run analysis** or enable **Auto-run on load**.")
        st.stop()

    result = st.session_state.get("result")
    if result is None:
        st.info("Choose settings in the sidebar and click **Run analysis**.")
        st.stop()

    tab_overview, tab_charts, tab_backtest, tab_regimes, tab_report = st.tabs(
        ["Overview", "Charts", "Backtest", "Regime model", "Report"]
    )
    with tab_overview:
        render_overview(result)
    with tab_charts:
        render_charts(result)
    with tab_backtest:
        render_backtest(result)
    with tab_regimes:
        render_regime_stats(result)
    with tab_report:
        render_report(result)


if __name__ == "__main__":
    main()
