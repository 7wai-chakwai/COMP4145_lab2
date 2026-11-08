from datetime import date
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

from market_data import (
    MAX_SELECTED_STOCKS,
    load_market_data,
    normalize_tickers,
    validate_tickers,
    validate_us_equity_metadata,
)
from portfolio_backtest import backtest_portfolio
from stock_selector import DEFAULT_SELECTED_TICKERS, SHARED_SELECTION_KEY


class StockSelectionValidationTests(unittest.TestCase):
    def test_custom_symbols_are_normalized_and_deduplicated(self):
        self.assertEqual(
            normalize_tickers("aapl, msft AMD aapl brk.b"),
            ("AAPL", "MSFT", "AMD", "BRK.B"),
        )
        self.assertEqual(validate_tickers(["jpm", "KO", "dis"]), ("JPM", "KO", "DIS"))

    def test_empty_invalid_and_limit_validation(self):
        with self.assertRaisesRegex(ValueError, "at least 1"):
            validate_tickers([])
        with self.assertRaisesRegex(ValueError, "Invalid US stock ticker"):
            validate_tickers(["AAPL", "^GSPC"])
        at_limit = [f"T{number:02d}" for number in range(MAX_SELECTED_STOCKS)]
        self.assertEqual(len(validate_tickers(at_limit)), MAX_SELECTED_STOCKS)
        with self.assertRaisesRegex(ValueError, f"no more than {MAX_SELECTED_STOCKS}"):
            validate_tickers(at_limit + ["OVER"])

    def test_provider_metadata_rejects_non_equity_or_non_usd_instruments(self):
        validate_us_equity_metadata({"instrumentType": "EQUITY", "currency": "USD"}, "AAPL")
        with self.assertRaisesRegex(ValueError, "Unsupported instrument type"):
            validate_us_equity_metadata({"instrumentType": "ETF", "currency": "USD"}, "SPY")
        with self.assertRaisesRegex(ValueError, "Unsupported quoted currency"):
            validate_us_equity_metadata({"instrumentType": "EQUITY", "currency": "HKD"}, "0005.HK")

    def test_equal_weight_allocation_supports_variable_stock_counts(self):
        index = pd.date_range("2025-01-02", periods=9, freq="B")
        prices = pd.DataFrame(
            {ticker: 100.0 for ticker in ("AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "AMD")},
            index=index,
        )
        result = backtest_portfolio(prices, index[0], 12_000, 2, 3, end_date=index[-1])
        np.testing.assert_allclose(result.contributions["Initial Allocation"], 2_000)
        np.testing.assert_allclose(result.sleeve_values.iloc[-1], 2_000)

    @patch("market_data.yf.Ticker")
    def test_syntactically_valid_but_unavailable_ticker_is_reported(self, ticker_factory):
        ticker_factory.return_value.history.return_value = pd.DataFrame()
        prices, errors = load_market_data(("NOTREAL",), "2024-01-02", "2024-01-04")
        self.assertTrue(prices.empty)
        self.assertIn("NOTREAL", errors)
        self.assertIn("No Close prices", errors["NOTREAL"])

    @patch("market_data.yf.Ticker")
    def test_loader_rejects_provider_classified_non_equity(self, ticker_factory):
        index = pd.date_range("2024-01-02", periods=3, freq="B")
        ticker_factory.return_value.history.return_value = pd.DataFrame(
            {"Close": [100.0, 101.0, 102.0]}, index=index
        )
        ticker_factory.return_value.get_history_metadata.return_value = {
            "instrumentType": "ETF", "currency": "USD"
        }
        prices, errors = load_market_data(("SPY",), "2024-01-02", "2024-01-04")
        self.assertTrue(prices.empty)
        self.assertIn("Unsupported instrument type", errors["SPY"])


class SharedWatchlistDashboardTests(unittest.TestCase):
    def setUp(self):
        import streamlit as st
        from streamlit.testing.v1 import AppTest

        st.cache_data.clear()
        self.app = AppTest.from_file("../app.py", default_timeout=25)
        self.strategy_history = pd.DataFrame(
            {"Close": np.concatenate([np.linspace(200, 100, 220), np.linspace(100, 300, 160)])},
            index=pd.date_range("2023-01-01", periods=380, freq="B"),
        )
        self.tickers = ("AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "AMD")
        index = pd.bdate_range(end=pd.Timestamp(date.today()), periods=110)
        cycle = np.concatenate([np.linspace(140, 80, 55), np.linspace(80, 180, 55)])
        self.prices = pd.DataFrame(
            {ticker: cycle * (1 + position / 20) for position, ticker in enumerate(self.tickers)},
            index=index,
        )

    @patch("portfolio_dashboard.load_market_data")
    @patch("pd2_dashboard.load_market_data")
    @patch("trading_strategy.get_stock_data")
    def test_more_than_five_stocks_are_shared_by_all_three_features(
        self, strategy_loader, analytics_loader, portfolio_loader
    ):
        strategy_loader.return_value = self.strategy_history
        analytics_loader.return_value = (self.prices, {})
        portfolio_loader.return_value = (self.prices, {})

        self.app.run()
        self.app.sidebar.radio[0].set_value("Multi-Stock Comparison").run()
        self.app.sidebar.multiselect[0].set_value(list(self.tickers)).run()
        self.assertEqual(tuple(analytics_loader.call_args.args[0]), self.tickers)
        self.assertEqual(len(self.app.dataframe[0].value), 6)

        self.app.sidebar.radio[0].set_value("Risk Analysis Dashboard").run()
        self.assertEqual(tuple(self.app.session_state[SHARED_SELECTION_KEY]), self.tickers)
        self.assertEqual(len(self.app.dataframe[0].value), 6)

        self.app.sidebar.radio[0].set_value("Portfolio Backtesting").run()
        self.assertEqual(tuple(portfolio_loader.call_args.args[0]), self.tickers)
        self.assertEqual(len(self.app.dataframe[0].value), 6)
        self.assertEqual(len(self.app.exception), 0)

    @patch("pd2_dashboard.load_market_data")
    @patch("trading_strategy.get_stock_data")
    def test_add_remove_invalid_empty_clear_and_restore(self, strategy_loader, analytics_loader):
        strategy_loader.return_value = self.strategy_history
        analytics_loader.return_value = (self.prices, {})
        self.app.run()
        self.app.sidebar.radio[0].set_value("Risk Analysis Dashboard").run()

        self.app.sidebar.multiselect[0].set_value(["aapl", "MSFT", "amd", "AAPL"]).run()
        self.assertEqual(tuple(self.app.session_state[SHARED_SELECTION_KEY]), ("AAPL", "MSFT", "AMD"))

        analytics_loader.return_value = (self.prices[["AAPL", "AMD"]], {})
        self.app.sidebar.multiselect[0].set_value(["AAPL", "AMD"]).run()
        self.assertEqual(tuple(self.app.session_state[SHARED_SELECTION_KEY]), ("AAPL", "AMD"))

        analytics_loader.return_value = (
            self.prices[["AAPL"]], {"NOTREAL": "No Close prices returned; check the ticker and date range."}
        )
        self.app.sidebar.multiselect[0].set_value(["AAPL", "NOTREAL"]).run()
        self.assertIn("NOTREAL", self.app.warning[0].value)

        self.app.sidebar.multiselect[0].set_value([]).run()
        self.assertIn("at least 1", self.app.error[0].value)

        self.app.button(key="restore_shared_stock_selection").click().run()
        self.assertEqual(tuple(self.app.session_state[SHARED_SELECTION_KEY]), DEFAULT_SELECTED_TICKERS)
        self.app.button(key="clear_shared_stock_selection").click().run()
        self.assertEqual(tuple(self.app.session_state[SHARED_SELECTION_KEY]), ())
        self.assertIn("at least 1", self.app.error[0].value)
        self.assertEqual(len(self.app.exception), 0)


if __name__ == "__main__":
    unittest.main()
