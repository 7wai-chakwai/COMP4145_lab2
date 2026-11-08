from datetime import date, timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from market_data import (
    align_prices, drawdowns, load_market_data, normalized_performance,
    risk_metrics, validate_dates, validate_tickers,
)
from stock_selector import render_stock_selector


@st.cache_data(ttl=3600, show_spinner=False)
def load_analytics(tickers, start, end):
    return load_market_data(tickers, start, end)


def analytics_inputs(min_required=2):
    symbols = render_stock_selector()
    with st.sidebar:
        st.subheader("Analysis period")
        start = st.date_input("Start date", date.today() - timedelta(days=365), key="analytics_start")
        end = st.date_input("End date", date.today(), max_value=date.today(), key="analytics_end")
        if st.button("Refresh market data", icon=":material/refresh:"):
            load_analytics.clear()
        st.caption("Source: Yahoo Finance. Daily adjusted Close in each stock's quoted currency.")
    try:
        tickers = validate_tickers(symbols, min_count=min_required)
        start, end = validate_dates(start, end)
    except (ValueError, TypeError) as error:
        st.error(str(error))
        return None
    try:
        with st.spinner("Loading historical stock prices..."):
            prices, errors = load_analytics(tickers, start, end)
    except Exception as error:
        st.error(f"Unable to retrieve market data: {error}")
        return None
    for ticker, message in errors.items():
        st.warning(f"{ticker}: {message}")
    if prices.shape[1] < min_required:
        noun = "stock" if min_required == 1 else "stocks"
        st.error(
            f"At least {min_required} {noun} with usable data are needed. "
            "Check tickers or widen the date range."
        )
        return None
    return prices


def line_chart(prices, title, y_label, suffix=""):
    figure = go.Figure()
    for ticker in prices:
        figure.add_trace(go.Scatter(
            x=prices.index, y=prices[ticker], name=ticker, mode="lines", connectgaps=False,
            hovertemplate="%{x|%d %b %Y}<br>%{y:.2f}" + suffix + "<extra>" + ticker + "</extra>",
        ))
    figure.update_layout(
        title=dict(text=title, y=0.98), template="plotly_white", height=420, hovermode="x unified",
        margin=dict(l=10, r=10, t=95, b=10), yaxis_title=y_label,
        legend=dict(orientation="h", y=1.02, yanchor="bottom", x=0),
    )
    return figure


def comparison_dashboard(prices):
    st.plotly_chart(line_chart(prices, "Historical adjusted prices", "Adjusted Close (quoted currency)"),
                    width="stretch", config={"displaylogo": False})
    st.caption("Raw prices are not directly comparable across currencies or share denominations; no FX conversion is applied.")
    try:
        aligned = align_prices(prices)
    except ValueError as error:
        st.error(str(error))
        return
    normalized = normalized_performance(aligned)
    returns = (normalized.iloc[-1] - 100).sort_values(ascending=False)
    best = returns[returns == returns.max()].index.tolist()
    st.metric("Best historical performer" if len(best) == 1 else "Joint best historical performers",
              ", ".join(best), f"{returns.max():+.2f}%", delta_color="off")
    st.plotly_chart(line_chart(normalized, "Normalized historical performance", "Index (start = 100)"),
                    width="stretch", config={"displaylogo": False})
    st.dataframe(returns.rename("Cumulative return (%)").rename_axis("Ticker").reset_index(),
                 hide_index=True, width="stretch",
                 column_config={"Cumulative return (%)": st.column_config.NumberColumn(format="%.2f%%")})
    st.caption(f"Common observed dates: {aligned.index.min():%Y-%m-%d} to {aligned.index.max():%Y-%m-%d}; "
               f"{len(aligned)} shared sessions. No missing prices are filled. Baseline is the first shared date.")


def risk_dashboard(prices):
    metrics = pd.concat([risk_metrics(prices[[ticker]].dropna()) for ticker in prices])
    selected = st.selectbox("Risk metric cards for", list(prices.columns), key="risk_focus")
    columns = st.columns(3)
    for column, metric in zip(columns, metrics.columns):
        column.metric(metric, f"{metrics.loc[selected, metric]:.2f}%")
    st.caption("Annualized volatility: sample standard deviation of daily returns x sqrt(252). "
               "Maximum drawdown: worst decline from a prior peak. Cumulative return: last / first adjusted Close minus 1.")
    figure = go.Figure()
    for metric, color in [("Annualized volatility (%)", "#146b88"), ("Maximum drawdown (%)", "#d04348")]:
        figure.add_trace(go.Bar(x=metrics.index, y=metrics[metric], name=metric, marker_color=color))
    figure.update_layout(title="Historical risk comparison", template="plotly_white", height=360,
                         yaxis_title="Percent", barmode="group", legend=dict(orientation="h", y=1.15))
    st.plotly_chart(figure, width="stretch", config={"displaylogo": False})
    declines = pd.concat([drawdowns(prices[[ticker]].dropna()) for ticker in prices], axis=1)
    st.plotly_chart(line_chart(declines * 100, "Historical drawdown", "Drawdown (%)", "%"),
                    width="stretch", config={"displaylogo": False})
    coverage = metrics.copy()
    coverage["First date"] = [prices[ticker].dropna().index.min().date() for ticker in coverage.index]
    coverage["Last date"] = [prices[ticker].dropna().index.max().date() for ticker in coverage.index]
    coverage["Observations"] = prices.count()
    st.dataframe(coverage.reset_index(), hide_index=True, width="stretch", column_config={
        metric: st.column_config.NumberColumn(format="%.2f%%") for metric in metrics.columns})
    st.caption("Risk uses each stock's own observed sessions, not the comparison's shared-date subset. "
               "252 sessions/year assumes a typical equity market calendar. Short histories are unstable; "
               "missing provider sessions or different calendars can distort annualization. Drawdown is shown as a negative return.")
