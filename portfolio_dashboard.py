from datetime import date, timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from market_data import load_market_data, validate_dates, validate_tickers
from portfolio_backtest import backtest_portfolio
from stock_selector import render_stock_selector


@st.cache_data(ttl=3600, show_spinner=False)
def load_portfolio_prices(tickers, start, end, long_window):
    warmup_days = max(90, int(long_window * 2.5) + 30)
    warmup_start = start - timedelta(days=warmup_days)
    return load_market_data(tickers, warmup_start, end)


def _portfolio_inputs():
    symbols = render_stock_selector()
    with st.sidebar:
        st.subheader("Portfolio settings")
        start = st.date_input(
            "Simulation start", date.today() - timedelta(days=365), key="portfolio_start"
        )
        end = st.date_input(
            "Simulation end", date.today(), max_value=date.today(), key="portfolio_end"
        )
        initial_capital = st.number_input(
            "Initial capital (USD)", min_value=1.0, value=10_000.0, step=1_000.0,
            key="portfolio_capital",
        )
        short_window = st.number_input(
            "Short moving average", min_value=2, max_value=250, value=20, step=1,
            key="portfolio_short_ma",
        )
        long_window = st.number_input(
            "Long moving average", min_value=3, max_value=400, value=50, step=1,
            key="portfolio_long_ma",
        )
        cost_bps = st.number_input(
            "Transaction cost (basis points per trade)",
            min_value=0.0, max_value=500.0, value=0.0, step=1.0,
            key="portfolio_cost_bps",
        )
        if st.button("Refresh portfolio data", icon=":material/refresh:"):
            load_portfolio_prices.clear()
        st.caption("1 basis point = 0.01%. Prices: Yahoo Finance adjusted daily Close.")

    try:
        tickers = validate_tickers(symbols, min_count=1)
        start, end = validate_dates(start, end)
        if int(short_window) >= int(long_window):
            raise ValueError("Short MA must be smaller than Long MA.")
        if float(initial_capital) <= 0:
            raise ValueError("Initial capital must be positive.")
    except (TypeError, ValueError) as error:
        st.error(str(error))
        return None
    return tickers, start, end, float(initial_capital), int(short_window), int(long_window), float(cost_bps)


def _equity_chart(equity_curve):
    figure = go.Figure()
    colors = {"Strategy": "#146b88", "Buy and Hold Benchmark": "#8a5a14"}
    for column in equity_curve:
        figure.add_trace(go.Scatter(
            x=equity_curve.index,
            y=equity_curve[column],
            name=column,
            mode="lines",
            line=dict(width=2.3, color=colors[column]),
            hovertemplate="%{x|%d %b %Y}<br>$%{y:,.2f}<extra>%{fullData.name}</extra>",
        ))
    figure.update_layout(
        title=dict(text="Portfolio equity and benchmark", y=0.98),
        template="plotly_white",
        height=460,
        hovermode="x unified",
        margin=dict(l=10, r=10, t=90, b=10),
        legend=dict(orientation="h", y=1.02, yanchor="bottom", x=0),
        yaxis=dict(title="Portfolio value (USD)", tickprefix="$", tickformat=",.0f"),
        xaxis=dict(title=None, rangeslider=dict(visible=True, thickness=0.07)),
    )
    return figure


def _contribution_chart(contributions):
    values = contributions["Strategy Profit/Loss"]
    figure = go.Figure(go.Bar(
        x=values.index,
        y=values,
        marker_color=["#18834b" if value >= 0 else "#d04348" for value in values],
        hovertemplate="%{x}<br>$%{y:,.2f}<extra></extra>",
    ))
    figure.update_layout(
        title="Individual stock contribution",
        template="plotly_white",
        height=340,
        margin=dict(l=10, r=10, t=55, b=10),
        yaxis=dict(title="Strategy profit / loss (USD)", tickprefix="$"),
        xaxis_title=None,
    )
    return figure


def portfolio_dashboard():
    inputs = _portfolio_inputs()
    if inputs is None:
        return
    tickers, start, end, capital, short_window, long_window, cost_bps = inputs

    try:
        with st.spinner("Loading portfolio history and MA warm-up data..."):
            prices, errors = load_portfolio_prices(tickers, start, end, long_window)
    except Exception as error:
        st.error(f"Unable to retrieve portfolio data: {error}")
        return

    if errors or tuple(prices.columns) != tickers:
        for ticker in tickers:
            if ticker in errors:
                st.warning(f"{ticker}: {errors[ticker]}")
        st.error(
            "Portfolio simulation stopped because every selected ticker must have usable data. "
            "The initial investment universe was not changed."
        )
        return

    try:
        result = backtest_portfolio(
            prices,
            start_date=start,
            end_date=end,
            initial_capital=capital,
            short_window=short_window,
            long_window=long_window,
            transaction_cost_bps=cost_bps,
        )
    except (TypeError, ValueError, RuntimeError) as error:
        st.error(f"Backtest could not run: {error}")
        return

    st.subheader("Portfolio summary")
    metrics = result.metrics
    columns = st.columns(5)
    columns[0].metric("Initial capital", f"${metrics['Initial Capital']:,.2f}")
    columns[1].metric(
        "Final value", f"${metrics['Final Portfolio Value']:,.2f}",
        f"${metrics['Total Profit/Loss']:+,.2f}", delta_color="off",
    )
    columns[2].metric("Total return", f"{metrics['Total Return (%)']:+.2f}%")
    columns[3].metric("Maximum drawdown", f"{metrics['Maximum Drawdown (%)']:.2f}%")
    columns[4].metric("Annualized volatility", f"{metrics['Annualized Volatility (%)']:.2f}%")
    st.caption(
        f"{len(tickers)} equal initial sleeves of USD {result.assumptions['Initial Allocation Per Stock']:,.2f} | "
        f"{len(result.trade_history)} executed trades | USD {metrics['Transaction Costs']:,.2f} strategy costs"
    )

    st.plotly_chart(_equity_chart(result.equity_curve), width="stretch", config={"displaylogo": False})
    benchmark_return = result.benchmark_metrics["Total Return (%)"]
    st.caption(
        f"Buy-and-hold benchmark return: {benchmark_return:+.2f}%. It uses the same tickers, equal starting "
        "sleeves, adjusted Close prices, and transaction-cost rate."
    )

    st.subheader("Individual stock performance")
    left, right = st.columns([1, 1.4])
    with left:
        st.plotly_chart(_contribution_chart(result.contributions), width="stretch", config={"displaylogo": False})
    with right:
        contribution_display = result.contributions.reset_index()
        st.dataframe(contribution_display, hide_index=True, width="stretch", column_config={
            "Initial Allocation": st.column_config.NumberColumn(format="$%.2f"),
            "Final Strategy Sleeve": st.column_config.NumberColumn(format="$%.2f"),
            "Strategy Profit/Loss": st.column_config.NumberColumn(format="$%.2f"),
            "Contribution to Portfolio Return (%)": st.column_config.NumberColumn(format="%.2f%%"),
            "Final Benchmark Sleeve": st.column_config.NumberColumn(format="$%.2f"),
        })

    st.subheader("Trade history")
    if result.trade_history.empty:
        st.info("No Golden Cross buy signals were executed during the selected simulation period.")
    else:
        display = result.trade_history.copy()
        for column in ["SignalDate", "TradeDate"]:
            display[column] = pd.to_datetime(display[column]).dt.strftime("%Y-%m-%d")
        st.download_button(
            "Download portfolio trades",
            display.to_csv(index=False),
            "portfolio_backtest_trades.csv",
            "text/csv",
            icon=":material/download:",
        )
        st.dataframe(display, hide_index=True, width="stretch", column_config={
            "ExecutionPrice": st.column_config.NumberColumn(format="$%.4f"),
            "Quantity": st.column_config.NumberColumn(format="%.6f"),
            "TransactionCost": st.column_config.NumberColumn(format="$%.4f"),
            "SleeveValue": st.column_config.NumberColumn(format="$%.2f"),
        })

    with st.expander("Strategy assumptions and limitations", expanded=False):
        st.markdown(
            f"""
- **Signals:** {short_window}-session MA crossing above/below the {long_window}-session MA using adjusted Close.
- **Execution:** A signal calculated after session *t* closes executes at that stock's next observed adjusted Close. This introduces a full-session delay and prevents same-close look-ahead.
- **Allocation:** ${capital:,.2f} is split equally once across {len(tickers)} independent sleeves. Cash is not moved between stocks and weights are not rebalanced.
- **Costs:** {cost_bps:.2f} basis points on each buy or sell notional. Fractional shares are allowed; interest, tax, slippage, bid-ask spread, leverage, and short selling are excluded.
- **Calendars:** Signals use each stock's observed sessions. Portfolio valuation uses the union of sessions; a last observed price is carried only to value an unchanged holding when another stock trades.
- **End date:** Open positions are marked to the final observed adjusted Close and remain open. No artificial liquidation trade or cost is added.
- **Data:** Yahoo adjusted prices may change and do not model a broker cash-dividend ledger. Results have survivorship, provider, currency, and execution-model limitations and are historical, not investment advice.
            """
        )
