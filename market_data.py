from collections.abc import Mapping
from datetime import date, timedelta
import os
import re

import numpy as np
import pandas as pd
import yfinance as yf


DEFAULT_MAX_SELECTED_STOCKS = 20


def _configured_stock_limit():
    try:
        value = int(os.getenv("PD2_MAX_SELECTED_STOCKS", DEFAULT_MAX_SELECTED_STOCKS))
    except (TypeError, ValueError):
        return DEFAULT_MAX_SELECTED_STOCKS
    return value if value > 0 else DEFAULT_MAX_SELECTED_STOCKS


MAX_SELECTED_STOCKS = _configured_stock_limit()


def normalize_tickers(symbols):
    if symbols is None:
        symbols = []
    if isinstance(symbols, str):
        symbols = re.split(r"[,\s]+", symbols.strip())
    tickers = []
    for symbol in symbols:
        ticker = str(symbol).strip().upper()
        if ticker and ticker not in tickers:
            tickers.append(ticker)
    return tuple(tickers)


def validate_tickers(symbols, min_count=1, max_count=None):
    tickers = normalize_tickers(symbols)
    maximum = MAX_SELECTED_STOCKS if max_count is None else int(max_count)
    if min_count < 0 or maximum < min_count:
        raise ValueError("Ticker count limits are invalid.")
    for ticker in tickers:
        if not re.fullmatch(r"[A-Z][A-Z0-9.\-]{0,14}", ticker):
            raise ValueError(f"Invalid US stock ticker format: {ticker!r}.")
    if len(tickers) < min_count:
        noun = "ticker" if min_count == 1 else "tickers"
        raise ValueError(f"Select at least {min_count} distinct stock {noun}.")
    if len(tickers) > maximum:
        raise ValueError(f"Select no more than {maximum} distinct stock tickers.")
    return tickers


def validate_us_equity_metadata(metadata, ticker):
    if not isinstance(metadata, Mapping):
        return
    instrument_type = metadata.get("instrumentType") or metadata.get("quoteType")
    if instrument_type and str(instrument_type).upper() != "EQUITY":
        raise ValueError(
            f"Unsupported instrument type for {ticker}: {instrument_type}. "
            "This feature supports US-listed equities."
        )
    currency = metadata.get("currency")
    if currency and str(currency).upper() != "USD":
        raise ValueError(
            f"Unsupported quoted currency for {ticker}: {currency}. "
            "This feature currently supports USD-listed equities."
        )


def validate_dates(start, end):
    start = pd.Timestamp(start).date()
    end = pd.Timestamp(end).date()
    if start >= end:
        raise ValueError("Start date must be earlier than end date.")
    if end > date.today():
        raise ValueError("End date cannot be in the future.")
    return start, end


def clean_close(history, ticker):
    if history.empty or "Close" not in history.columns:
        raise ValueError("No Close prices returned; check the ticker and date range.")
    prices = pd.to_numeric(history["Close"], errors="coerce").copy()
    if not np.isfinite(prices).all() or (prices <= 0).any():
        raise ValueError("Missing or invalid Close prices; no prices were filled or fabricated.")
    index = pd.DatetimeIndex(pd.to_datetime(prices.index))
    if index.hasnans:
        raise ValueError("Invalid market dates returned.")
    if index.tz is not None:
        index = index.tz_localize(None)
    prices.index = index.normalize()
    prices = prices.sort_index()
    if prices.index.has_duplicates:
        raise ValueError("Duplicate trading dates returned.")
    if len(prices) < 3:
        raise ValueError("At least 3 historical prices are needed for risk analysis.")
    return prices.rename(ticker)


def load_market_data(tickers, start, end):
    tickers = validate_tickers(tickers)
    start, end = validate_dates(start, end)
    series = []
    errors = {}
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            history = stock.history(
                start=start.isoformat(), end=(end + timedelta(days=1)).isoformat(),
                interval="1d", auto_adjust=True, actions=False,
                raise_errors=True, timeout=15,
            )
            metadata_getter = getattr(stock, "get_history_metadata", None)
            metadata = metadata_getter() if callable(metadata_getter) else None
            if not isinstance(metadata, Mapping):
                metadata = getattr(stock, "history_metadata", None)
            validate_us_equity_metadata(metadata, ticker)
            prices = clean_close(history, ticker)
            prices = prices.loc[start.isoformat():end.isoformat()]
            if len(prices) < 3:
                raise ValueError("Fewer than 3 prices inside the requested date range.")
            series.append(prices)
        except Exception as error:
            errors[ticker] = str(error)
    if not series:
        return pd.DataFrame(), errors
    return pd.concat(series, axis=1).sort_index(), errors


def align_prices(prices):
    if prices.shape[1] < 2:
        raise ValueError("At least 2 successfully loaded stocks are required.")
    aligned = prices.dropna(how="any").copy()
    if len(aligned) < 3:
        raise ValueError("At least 3 shared trading dates are required; widen the date range.")
    if not np.isfinite(aligned.to_numpy()).all() or (aligned <= 0).any().any():
        raise ValueError("Prices must be finite and positive.")
    if not aligned.index.is_monotonic_increasing or aligned.index.has_duplicates:
        raise ValueError("Prices must have unique, ascending trading dates.")
    return aligned


def normalized_performance(prices):
    return prices.div(prices.iloc[0]).mul(100)


def drawdowns(prices):
    return prices.div(prices.cummax()).sub(1)


def risk_metrics(prices):
    if len(prices) < 3 or prices.empty:
        raise ValueError("At least 3 historical prices are required.")
    if prices.isna().any().any() or not np.isfinite(prices.to_numpy()).all() or (prices <= 0).any().any():
        raise ValueError("Risk calculations require finite, positive, complete prices.")
    returns = prices.pct_change(fill_method=None).iloc[1:]
    return pd.DataFrame({
        "Cumulative return (%)": (prices.iloc[-1] / prices.iloc[0] - 1) * 100,
        "Annualized volatility (%)": returns.std(ddof=1) * np.sqrt(252) * 100,
        "Maximum drawdown (%)": drawdowns(prices).min() * 100,
    }).rename_axis("Ticker")
