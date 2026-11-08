from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd


TRADE_COLUMNS = [
    "Ticker",
    "SignalDate",
    "TradeDate",
    "Action",
    "ExecutionPrice",
    "Quantity",
    "TransactionCost",
    "SleeveValue",
]


@dataclass
class BacktestResult:
    equity_curve: pd.DataFrame
    daily_returns: pd.Series
    sleeve_values: pd.DataFrame
    benchmark_sleeve_values: pd.DataFrame
    contributions: pd.DataFrame
    trade_history: pd.DataFrame
    metrics: dict[str, float]
    benchmark_metrics: dict[str, float]
    assumptions: dict[str, Any]


def moving_average_signals(prices, short_window, long_window):
    """Return causal crossover signals calculated from current and prior closes."""
    short_ma = prices.rolling(short_window, min_periods=short_window).mean()
    long_ma = prices.rolling(long_window, min_periods=long_window).mean()
    buy = (short_ma > long_ma) & (short_ma.shift(1) <= long_ma.shift(1))
    sell = (short_ma < long_ma) & (short_ma.shift(1) >= long_ma.shift(1))
    return pd.Series(np.select([buy, sell], [1, -1], default=0), index=prices.index, dtype="int8")


def _validated_prices(prices, short_window, long_window, start, end):
    if not isinstance(prices, pd.DataFrame) or prices.empty or prices.shape[1] == 0:
        raise ValueError("At least one stock price history is required.")
    if prices.columns.has_duplicates:
        raise ValueError("Portfolio tickers must be unique.")
    if not isinstance(short_window, int) or not isinstance(long_window, int):
        raise ValueError("Moving-average windows must be whole numbers.")
    if short_window < 2 or long_window < 3 or short_window >= long_window:
        raise ValueError("Short MA must be at least 2 and smaller than Long MA.")

    frame = prices.copy()
    index = pd.DatetimeIndex(pd.to_datetime(frame.index))
    if index.hasnans:
        raise ValueError("Market data contains invalid dates.")
    if index.tz is not None:
        index = index.tz_localize(None)
    frame.index = index.normalize()
    frame = frame.sort_index()
    if frame.index.has_duplicates:
        raise ValueError("Market data must have unique dates.")

    cleaned = {}
    for column in frame:
        ticker = str(column).strip().upper()
        series = pd.to_numeric(frame[column], errors="coerce").dropna().astype(float)
        series = series.loc[:end]
        if series.empty or not np.isfinite(series.to_numpy()).all() or (series <= 0).any():
            raise ValueError(f"{ticker} has missing, non-finite, or non-positive usable prices.")
        if len(series) < long_window + 1:
            raise ValueError(
                f"{ticker} needs at least {long_window + 1} observed prices including MA warm-up; "
                f"only {len(series)} are available."
            )
        simulation_prices = series.loc[start:end]
        if len(simulation_prices) < 2:
            raise ValueError(f"{ticker} needs at least 2 observed prices inside the simulation period.")
        cleaned[ticker] = series.rename(ticker)

    if len(set(cleaned)) != len(cleaned):
        raise ValueError("Portfolio tickers must be unique after normalization.")
    return pd.concat(cleaned.values(), axis=1).sort_index()


def _performance_metrics(equity, initial_capital):
    returns = equity.pct_change(fill_method=None).dropna()
    volatility = returns.std(ddof=1) * np.sqrt(252) * 100 if len(returns) >= 2 else 0.0
    drawdown = equity.div(equity.cummax()).sub(1).min() * 100
    final_value = float(equity.iloc[-1])
    return {
        "Initial Capital": float(initial_capital),
        "Final Portfolio Value": final_value,
        "Total Profit/Loss": final_value - float(initial_capital),
        "Total Return (%)": (final_value / float(initial_capital) - 1) * 100,
        "Maximum Drawdown (%)": float(drawdown),
        "Annualized Volatility (%)": float(volatility),
    }


def backtest_portfolio(
    prices,
    start_date,
    initial_capital=10_000.0,
    short_window=20,
    long_window=50,
    transaction_cost_bps=0.0,
    end_date=None,
):
    """Simulate independent equal-capital sleeves with next-session execution.

    Signals use adjusted closing prices on session t. A signal can only fill at
    that stock's next observed adjusted Close, so no trade uses future data when
    the signal is generated. Open positions are marked, not liquidated, at the
    end of the requested period.
    """
    try:
        capital = float(initial_capital)
        cost_bps = float(transaction_cost_bps)
    except (TypeError, ValueError) as error:
        raise ValueError("Initial capital and transaction cost must be numeric.") from error
    if not np.isfinite(capital) or capital <= 0:
        raise ValueError("Initial capital must be positive and finite.")
    if not np.isfinite(cost_bps) or cost_bps < 0 or cost_bps > 10_000:
        raise ValueError("Transaction cost must be between 0 and 10,000 basis points.")

    start = pd.Timestamp(start_date).tz_localize(None).normalize()
    end = pd.Timestamp(end_date).tz_localize(None).normalize() if end_date is not None else None
    if pd.isna(start) or (end is not None and pd.isna(end)):
        raise ValueError("Simulation dates must be valid.")
    if end is None:
        end = pd.DatetimeIndex(pd.to_datetime(prices.index)).tz_localize(None).max().normalize()
    if start >= end:
        raise ValueError("Simulation start date must be earlier than end date.")

    frame = _validated_prices(prices, short_window, long_window, start, end)
    tickers = list(frame.columns)
    allocation = capital / len(tickers)
    cost_rate = cost_bps / 10_000

    native = {ticker: frame[ticker].dropna().loc[:end] for ticker in tickers}
    simulation = {ticker: series.loc[start:end] for ticker, series in native.items()}
    calendar = simulation[tickers[0]].index
    for ticker in tickers[1:]:
        calendar = calendar.union(simulation[ticker].index)
    calendar = calendar.sort_values()
    if len(calendar) < 3:
        raise ValueError("At least 3 portfolio valuation dates are required.")

    events = {}
    for ticker, series in native.items():
        signals = moving_average_signals(series, short_window, long_window)
        for signal_date, action in signals.items():
            if action == 0 or signal_date < start or signal_date > end:
                continue
            location = series.index.get_loc(signal_date)
            if location + 1 >= len(series):
                continue
            trade_date = series.index[location + 1]
            if trade_date > end:
                continue
            events.setdefault(trade_date, []).append((ticker, int(action), signal_date))

    states = {ticker: {"cash": allocation, "quantity": 0.0} for ticker in tickers}
    benchmark_states = {ticker: {"cash": allocation, "quantity": 0.0} for ticker in tickers}
    benchmark_buy_dates = {ticker: series.index[0] for ticker, series in simulation.items()}
    last_marks = {}
    sleeve_rows = []
    benchmark_rows = []
    equity_rows = []
    trades = []

    for valuation_date in calendar:
        for ticker in tickers:
            if valuation_date in simulation[ticker].index:
                last_marks[ticker] = float(simulation[ticker].loc[valuation_date])

        for ticker in tickers:
            if valuation_date == benchmark_buy_dates[ticker]:
                price = float(simulation[ticker].loc[valuation_date])
                state = benchmark_states[ticker]
                quantity = state["cash"] / (price * (1 + cost_rate))
                cost = quantity * price * cost_rate
                state["quantity"] = quantity
                state["cash"] = max(0.0, state["cash"] - quantity * price - cost)

        for ticker, action, signal_date in sorted(events.get(valuation_date, [])):
            price = float(native[ticker].loc[valuation_date])
            state = states[ticker]
            if action == 1 and state["quantity"] == 0:
                quantity = state["cash"] / (price * (1 + cost_rate))
                notional = quantity * price
                cost = notional * cost_rate
                state["quantity"] = quantity
                state["cash"] = max(0.0, state["cash"] - notional - cost)
                action_name = "Buy"
                traded_quantity = quantity
            elif action == -1 and state["quantity"] > 0:
                traded_quantity = state["quantity"]
                notional = traded_quantity * price
                cost = notional * cost_rate
                state["cash"] += notional - cost
                state["quantity"] = 0.0
                action_name = "Sell"
            else:
                continue
            sleeve_value = state["cash"] + state["quantity"] * price
            trades.append({
                "Ticker": ticker,
                "SignalDate": signal_date,
                "TradeDate": valuation_date,
                "Action": action_name,
                "ExecutionPrice": price,
                "Quantity": traded_quantity,
                "TransactionCost": cost,
                "SleeveValue": sleeve_value,
            })

        for ticker in tickers:
            if states[ticker]["cash"] < -1e-8 or states[ticker]["quantity"] < -1e-12:
                raise RuntimeError(f"Portfolio invariant failed: {ticker} introduced leverage or a short position.")
            if benchmark_states[ticker]["cash"] < -1e-8 or benchmark_states[ticker]["quantity"] < -1e-12:
                raise RuntimeError(f"Benchmark invariant failed: {ticker} introduced leverage or a short position.")

        sleeve_value_row = {}
        benchmark_value_row = {}
        for ticker in tickers:
            mark = last_marks.get(ticker)
            state = states[ticker]
            benchmark_state = benchmark_states[ticker]
            sleeve_value_row[ticker] = state["cash"] + state["quantity"] * mark if mark is not None else state["cash"]
            benchmark_value_row[ticker] = (
                benchmark_state["cash"] + benchmark_state["quantity"] * mark
                if mark is not None else benchmark_state["cash"]
            )
        sleeve_rows.append(pd.Series(sleeve_value_row, name=valuation_date))
        benchmark_rows.append(pd.Series(benchmark_value_row, name=valuation_date))
        equity_rows.append({
            "Date": valuation_date,
            "Strategy": sum(sleeve_value_row.values()),
            "Buy and Hold Benchmark": sum(benchmark_value_row.values()),
        })

    sleeve_values = pd.DataFrame(sleeve_rows)
    benchmark_sleeve_values = pd.DataFrame(benchmark_rows)
    equity_curve = pd.DataFrame(equity_rows).set_index("Date")
    daily_returns = equity_curve["Strategy"].pct_change(fill_method=None).rename("Portfolio return")
    trade_history = pd.DataFrame(trades, columns=TRADE_COLUMNS)

    final_sleeves = sleeve_values.iloc[-1]
    final_benchmark_sleeves = benchmark_sleeve_values.iloc[-1]
    contributions = pd.DataFrame({
        "Initial Allocation": allocation,
        "Final Strategy Sleeve": final_sleeves,
        "Strategy Profit/Loss": final_sleeves - allocation,
        "Contribution to Portfolio Return (%)": (final_sleeves - allocation) / capital * 100,
        "Final Benchmark Sleeve": final_benchmark_sleeves,
    }).rename_axis("Ticker")

    metrics = _performance_metrics(equity_curve["Strategy"], capital)
    metrics["Transaction Costs"] = float(trade_history["TransactionCost"].sum()) if not trade_history.empty else 0.0
    benchmark_metrics = _performance_metrics(equity_curve["Buy and Hold Benchmark"], capital)

    if (sleeve_values < -1e-8).any().any():
        raise RuntimeError("Portfolio invariant failed: a sleeve value became negative.")
    if not np.allclose(equity_curve["Strategy"], sleeve_values.sum(axis=1), rtol=1e-10, atol=1e-8):
        raise RuntimeError("Portfolio invariant failed: equity does not equal the sum of sleeves.")

    return BacktestResult(
        equity_curve=equity_curve,
        daily_returns=daily_returns,
        sleeve_values=sleeve_values,
        benchmark_sleeve_values=benchmark_sleeve_values,
        contributions=contributions,
        trade_history=trade_history,
        metrics=metrics,
        benchmark_metrics=benchmark_metrics,
        assumptions={
            "Tickers": tuple(tickers),
            "Initial Allocation Per Stock": allocation,
            "Short MA": short_window,
            "Long MA": long_window,
            "Transaction Cost (bps)": cost_bps,
            "Execution": "Signal at adjusted Close t; fill at the stock's next observed adjusted Close.",
            "Terminal Treatment": "Open positions are marked to the final observed adjusted Close, not forcibly sold.",
            "Calendar": "Union of observed stock sessions; the last observed price is carried only for valuation.",
        },
    )
