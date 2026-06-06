"""Plotly charts for the web dashboard."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .backtest import BacktestResult
from .hmm_detector import RegimeLabel

REGIME_COLORS = {
    RegimeLabel.BULL.value: "rgba(34, 197, 94, 0.2)",
    RegimeLabel.BEAR.value: "rgba(239, 68, 68, 0.2)",
    RegimeLabel.SIDEWAYS.value: "rgba(234, 179, 8, 0.2)",
}
REGIME_LINE_COLORS = {
    RegimeLabel.BULL.value: "#22c55e",
    RegimeLabel.BEAR.value: "#ef4444",
    RegimeLabel.SIDEWAYS.value: "#eab308",
}


def _regime_strings(regimes: pd.Series) -> pd.Series:
    return regimes.map(lambda r: r.value if hasattr(r, "value") else str(r))


def _regime_segments(regimes: pd.Series) -> list[tuple[str, pd.Timestamp, pd.Timestamp]]:
    """Contiguous date ranges per regime label."""
    s = _regime_strings(regimes)
    if s.empty:
        return []
    segments: list[tuple[str, pd.Timestamp, pd.Timestamp]] = []
    current = s.iloc[0]
    start = s.index[0]
    for date, label in s.iloc[1:].items():
        if label != current:
            segments.append((current, start, s.index[s.index.get_loc(date) - 1]))
            current, start = label, date
    segments.append((current, start, s.index[-1]))
    return segments


def regime_price_chart(prices: pd.Series, regimes: pd.Series, title: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=prices.index,
            y=prices.values,
            mode="lines",
            name=prices.name or "Price",
            line=dict(color="#0f172a", width=2),
        )
    )
    for label, start, end in _regime_segments(regimes):
        fig.add_vrect(
            x0=start,
            x1=end,
            fillcolor=REGIME_COLORS.get(label, "rgba(148,163,184,0.15)"),
            line_width=0,
            layer="below",
        )
    for label, color in REGIME_LINE_COLORS.items():
        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode="markers",
                marker=dict(size=10, color=color),
                name=label,
            )
        )
    fig.update_layout(
        title=title,
        template="plotly_white",
        height=420,
        margin=dict(l=40, r=20, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
    )
    fig.update_yaxes(title_text="Price ($)")
    return fig


def equity_curve_chart(results: list[BacktestResult], title: str) -> go.Figure:
    fig = go.Figure()
    palette = ["#2563eb", "#7c3aed", "#059669"]
    for i, r in enumerate(results):
        fig.add_trace(
            go.Scatter(
                x=r.equity_curve.index,
                y=r.equity_curve.values,
                mode="lines",
                name=r.name,
                line=dict(width=2.5, color=palette[i % len(palette)]),
            )
        )
    fig.update_layout(
        title=title,
        template="plotly_white",
        height=420,
        margin=dict(l=40, r=20, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
    )
    fig.update_yaxes(title_text="Growth of $1")
    return fig


def allocation_pie(weights: dict[str, float], title: str = "Suggested allocation") -> go.Figure:
    labels = list(weights.keys())
    values = [weights[k] * 100 for k in labels]
    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.45,
                textinfo="label+percent",
                marker=dict(colors=["#2563eb", "#64748b", "#eab308", "#22c55e", "#ef4444"]),
            )
        ]
    )
    fig.update_layout(title=title, height=360, margin=dict(l=20, r=20, t=50, b=20))
    return fig


def transition_heatmap(matrix: pd.DataFrame, title: str = "Regime transitions") -> go.Figure:
    fig = go.Figure(
        data=go.Heatmap(
            z=matrix.values,
            x=list(matrix.columns),
            y=list(matrix.index),
            colorscale="Blues",
            text=matrix.round(2).values,
            texttemplate="%{text}",
            textfont={"size": 12},
            hovertemplate="From %{y} to %{x}: %{z:.1%}<extra></extra>",
        )
    )
    fig.update_layout(
        title=title,
        template="plotly_white",
        height=320,
        margin=dict(l=60, r=20, t=50, b=40),
    )
    return fig


def regime_timeline(regimes: pd.Series, title: str = "Regime timeline (test period)") -> go.Figure:
    s = _regime_strings(regimes)
    mapping = {RegimeLabel.BULL.value: 2, RegimeLabel.SIDEWAYS.value: 1, RegimeLabel.BEAR.value: 0}
    y = s.map(mapping)
    colors = [REGIME_LINE_COLORS.get(v, "#94a3b8") for v in s]

    fig = go.Figure(
        data=go.Bar(
            x=s.index,
            y=[1] * len(s),
            marker=dict(color=colors),
            hovertext=s.values,
            hovertemplate="%{x}<br>%{hovertext}<extra></extra>",
        )
    )
    fig.update_layout(
        title=title,
        template="plotly_white",
        height=120,
        showlegend=False,
        margin=dict(l=20, r=20, t=40, b=20),
        yaxis=dict(visible=False),
    )
    return fig
