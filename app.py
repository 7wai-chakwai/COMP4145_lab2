import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from trading_strategy import (
    calculate_moving_averages,
    get_stock_data,
    identify_golden_cross,
    implement_strategy,
)


st.set_page_config(page_title="MSFT | Golden Cross", page_icon=":chart_with_upwards_trend:", layout="wide")


@st.cache_data(ttl=3600, show_spinner=False)
def load_results():
    prices = get_stock_data("MSFT", period="5y")
    if prices.empty:
        raise ValueError("No Microsoft price data was returned by Yahoo Finance.")
    prices = identify_golden_cross(calculate_moving_averages(prices))
    return prices, implement_strategy(prices)


def price_chart(prices, trades):
    figure = go.Figure()
    for column, label, color, width in [
        ("Close", "MSFT close", "#146b88", 2),
        ("MA50", "50-day MA", "#b87813", 1.5),
        ("MA200", "200-day MA", "#8955a1", 1.5),
    ]:
        figure.add_trace(go.Scatter(
            x=prices.index, y=prices[column], name=label,
            mode="lines", line=dict(color=color, width=width),
            hovertemplate="%{x|%d %b %Y}<br>$%{y:.2f}<extra>%{fullData.name}</extra>",
        ))
    if not trades.empty:
        for prefix, label, color in [("Buy", "Buy", "#18834b"), ("Sell", "Sell", "#d04348")]:
            figure.add_trace(go.Scatter(
                x=trades[f"{prefix}Date"], y=trades[f"{prefix}Price"],
                name=label, mode="markers",
                marker=dict(size=11, color=color, symbol="circle", line=dict(color="white", width=1.5)),
                hovertemplate="%{x|%d %b %Y}<br>$%{y:.2f}<extra>" + label + "</extra>",
            ))
    figure.update_layout(
        height=560, margin=dict(l=10, r=10, t=20, b=10),
        template="plotly_white", hovermode="x unified",
        legend=dict(orientation="h", y=1.12, x=0),
        yaxis=dict(title="Price (USD)", tickprefix="$"),
        xaxis=dict(title=None, rangeslider=dict(visible=True, thickness=0.08)),
    )
    return figure


def statistics(trades):
    st.subheader("Overall trade statistics")
    if trades.empty:
        st.info("No completed trades in this period.")
        return
    profits = trades["ProfitPct"]
    winners = profits > 0
    columns = st.columns(4)
    columns[0].metric("Total trades", len(trades))
    columns[1].metric("Win rate", f"{winners.mean() * 100:.1f}%")
    columns[2].metric("Average return / trade", f"{profits.mean():.2f}%")
    columns[3].metric("Average holding period", f"{trades['HoldingDays'].mean():.1f} days")
    st.divider()
    columns = st.columns(4)
    columns[0].metric("Winning trades", int(winners.sum()))
    columns[1].metric("Non-winning trades", int((~winners).sum()))
    columns[2].metric("Best trade", f"{profits.max():.2f}%")
    columns[3].metric("Worst trade", f"{profits.min():.2f}%")
    st.divider()
    left, right = st.columns(2)
    with left:
        figure = go.Figure(go.Bar(
            x=[f"Trade {number}" for number in range(1, len(trades) + 1)],
            y=profits, marker_color=["#18834b" if value > 0 else "#d04348" for value in profits],
            hovertemplate="%{x}<br>%{y:.2f}%<extra></extra>",
        ))
        figure.update_layout(title="Return per trade", template="plotly_white", yaxis_title="Return (%)", height=340)
        st.plotly_chart(figure, width="stretch")
    with right:
        reasons = trades["SellReason"].value_counts().rename_axis("Exit reason").reset_index(name="Trades")
        st.subheader("Exit breakdown")
        st.dataframe(reasons, hide_index=True, width="stretch")
        st.caption("Returns are per trade, not a portfolio return. Fees and slippage are excluded. Holding periods are calendar days.")


def detailed_trades(trades):
    st.subheader("Detailed trades")
    if trades.empty:
        st.info("No completed trades in this period.")
        return
    selected = st.segmented_control("Outcome", ["All", "Winning", "Non-winning"], default="All")
    filtered = trades.copy()
    if selected == "Winning":
        filtered = filtered[filtered["ProfitPct"] > 0]
    elif selected == "Non-winning":
        filtered = filtered[filtered["ProfitPct"] <= 0]
    st.download_button("Download CSV", filtered.to_csv(index=False), "msft_trades.csv", "text/csv", icon=":material/download:")
    display = filtered.copy()
    for column in ["BuyDate", "SellDate"]:
        display[column] = pd.to_datetime(display[column]).dt.strftime("%Y-%m-%d")
    st.dataframe(display, hide_index=True, width="stretch", column_config={
        "BuyDate": "Buy date", "SellDate": "Sell date",
        "BuyPrice": st.column_config.NumberColumn("Buy price", format="$%.2f"),
        "SellPrice": st.column_config.NumberColumn("Sell price", format="$%.2f"),
        "ProfitPct": st.column_config.NumberColumn("Return", format="%.2f%%"),
        "HoldingDays": "Holding days", "SellReason": "Exit reason",
    })
    st.caption(f"{len(filtered)} of {len(trades)} trades")


st.title("Microsoft / MSFT")
st.caption("Golden Cross  |  50 / 200 trading-day averages  |  15% target  |  60-day holding limit")
page = st.segmented_control(
    "View", ["Price chart", "Trade statistics", "Detailed trades"],
    default="Price chart", label_visibility="collapsed",
)
try:
    with st.spinner("Loading Microsoft prices..."):
        prices, trades = load_results()
except Exception as error:
    st.error(f"Unable to load market data: {error}")
    if st.button("Retry", icon=":material/refresh:"):
        load_results.clear()
        st.rerun()
    st.stop()

st.caption(f"{prices.index.min():%d %b %Y} - {prices.index.max():%d %b %Y}  |  {len(prices):,} trading sessions")
if page == "Trade statistics":
    statistics(trades)
elif page == "Detailed trades":
    detailed_trades(trades)
else:
    st.plotly_chart(price_chart(prices, trades), width="stretch", config={"displaylogo": False})
    st.caption(f"{len(trades)} trades  |  Green: buy  |  Red: sell")