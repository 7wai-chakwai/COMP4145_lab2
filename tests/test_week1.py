from datetime import date
import unittest
from unittest.mock import patch, MagicMock

import numpy as np
import pandas as pd

from market_data import (
    align_prices, clean_close, drawdowns, load_market_data,
    normalized_performance, risk_metrics, validate_dates, validate_tickers,
)
from trading_strategy import calculate_moving_averages, identify_golden_cross, implement_strategy


class AnalyticsTests(unittest.TestCase):
    def setUp(self):
        self.prices = pd.DataFrame(
            {"AAPL": [100.0, 120.0, 90.0], "MSFT": [100.0, 100.0, 100.0], "NVDA": [50.0, 75.0, 100.0]},
            index=pd.date_range("2024-01-02", periods=3, freq="B"),
        )

    def test_normalized_and_cumulative_return(self):
        normalized = normalized_performance(self.prices)
        np.testing.assert_allclose(normalized.iloc[0], [100, 100, 100])
        np.testing.assert_allclose(normalized.iloc[-1], [90, 100, 200])
        np.testing.assert_allclose(risk_metrics(self.prices)["Cumulative return (%)"], [-10, 0, 100])

    def test_volatility_and_drawdown(self):
        metrics = risk_metrics(self.prices)
        expected = np.std([0.2, -0.25], ddof=1) * np.sqrt(252) * 100
        self.assertAlmostEqual(metrics.loc["AAPL", "Annualized volatility (%)"], expected)
        self.assertEqual(metrics.loc["MSFT", "Annualized volatility (%)"], 0)
        self.assertAlmostEqual(metrics.loc["AAPL", "Maximum drawdown (%)"], -25)
        np.testing.assert_allclose(drawdowns(self.prices)["AAPL"], [0, 0, -0.25])

    def test_ticker_selection(self):
        self.assertEqual(validate_tickers("aapl, MSFT nvda AAPL"), ("AAPL", "MSFT", "NVDA"))
        self.assertEqual(validate_tickers("AAPL,AAPL"), ("AAPL",))
        self.assertEqual(validate_tickers("A B C D E F"), ("A", "B", "C", "D", "E", "F"))
        self.assertEqual(len(validate_tickers([f"T{number:02d}" for number in range(20)])), 20)
        with self.assertRaisesRegex(ValueError, "at least 2"):
            validate_tickers("AAPL", min_count=2)
        for symbols in ["AAPL,???", "", [f"T{number:02d}" for number in range(21)]]:
            with self.subTest(symbols=symbols), self.assertRaises(ValueError):
                validate_tickers(symbols)

    def test_date_validation(self):
        for start, end in [("2024-01-03", "2024-01-02"), (date.today(), "2099-01-01")]:
            with self.assertRaises(ValueError):
                validate_dates(start, end)

    def test_cleaning_timezone_sorting_and_no_fill(self):
        history = pd.DataFrame({"Close": [90, 120, 100]}, index=pd.to_datetime(
            ["2024-01-04", "2024-01-03", "2024-01-02"]).tz_localize("America/New_York"))
        cleaned = clean_close(history, "AAPL")
        self.assertIsNone(cleaned.index.tz)
        self.assertEqual(cleaned.tolist(), [100, 120, 90])
        for values in [[100, np.nan, 90], [100, 0, 90], [100, np.inf, 90], [100, -1, 90]]:
            with self.assertRaises(ValueError):
                clean_close(pd.DataFrame({"Close": values}, index=self.prices.index), "AAPL")
        with self.assertRaises(ValueError):
            clean_close(pd.DataFrame(), "AAPL")
        with self.assertRaises(ValueError):
            clean_close(history.iloc[:2], "AAPL")
        with self.assertRaises(ValueError):
            clean_close(pd.concat([history, history.iloc[:1]]), "AAPL")

    def test_alignment_and_insufficient_data(self):
        prices = self.prices.reindex(pd.date_range("2024-01-02", periods=4, freq="B"))
        pd.testing.assert_frame_equal(align_prices(prices), self.prices)
        self.assertTrue(prices.iloc[-1].isna().all())
        with self.assertRaises(ValueError):
            align_prices(self.prices.iloc[:2])
        with self.assertRaises(ValueError):
            risk_metrics(self.prices.iloc[:2])
        with self.assertRaises(ValueError):
            risk_metrics(prices)

    @patch("market_data.yf.Ticker")
    def test_data_loading_and_partial_api_failure(self, ticker_factory):
        good = MagicMock()
        good.history.return_value = self.prices[["AAPL"]].rename(columns={"AAPL": "Close"})
        bad = MagicMock()
        bad.history.side_effect = RuntimeError("Simulated API restriction")
        ticker_factory.side_effect = [good, good, bad]
        prices, errors = load_market_data(("AAPL", "MSFT", "NVDA"), "2024-01-02", "2024-01-04")
        self.assertEqual(list(prices.columns), ["AAPL", "MSFT"])
        self.assertEqual(errors, {"NVDA": "Simulated API restriction"})
        self.assertEqual(good.history.call_args.kwargs["end"], "2024-01-05")
        self.assertTrue(good.history.call_args.kwargs["auto_adjust"])

    @patch("market_data.yf.Ticker")
    def test_all_data_loading_failures(self, ticker_factory):
        ticker_factory.return_value.history.return_value = pd.DataFrame()
        prices, errors = load_market_data(("AAPL", "MSFT"), "2024-01-02", "2024-01-04")
        self.assertTrue(prices.empty)
        self.assertEqual(set(errors), {"AAPL", "MSFT"})


class Lab2RegressionTests(unittest.TestCase):
    def test_actual_moving_averages_and_golden_cross(self):
        data = pd.DataFrame({"Close": np.concatenate([np.linspace(200, 100, 220), np.linspace(100, 300, 160)])},
                            index=pd.date_range("2023-01-01", periods=380, freq="B"))
        result = identify_golden_cross(calculate_moving_averages(data.copy()))
        self.assertAlmostEqual(result["MA50"].iloc[49], data["Close"].iloc[:50].mean())
        self.assertAlmostEqual(result["MA200"].iloc[199], data["Close"].iloc[:200].mean())
        self.assertTrue(result["MA200"].iloc[:199].isna().all())
        self.assertEqual(int(result["GoldenCross"].sum()), 1)
        trades = implement_strategy(result)
        self.assertEqual(len(trades), 1)
        self.assertEqual(trades.iloc[0]["SellReason"], "Target reached")
        self.assertGreaterEqual(trades.iloc[0]["ProfitPct"], 15)

    def test_holding_limit_and_no_signals(self):
        data = pd.DataFrame({"Close": np.full(300, 100.0), "GoldenCross": False},
                            index=pd.date_range("2023-01-01", periods=300, freq="B"))
        self.assertTrue(implement_strategy(data).empty)
        data.loc[data.index[210], "GoldenCross"] = True
        trades = implement_strategy(data)
        self.assertEqual(len(trades), 1)
        self.assertEqual(trades.iloc[0]["SellReason"], "Max holding period")
        self.assertLessEqual(trades.iloc[0]["HoldingDays"], 60)
        self.assertEqual(trades.iloc[0]["ProfitPct"], 0)


class DashboardTests(unittest.TestCase):
    def setUp(self):
        import streamlit as st
        from streamlit.testing.v1 import AppTest
        st.cache_data.clear()
        self.app = AppTest.from_file("../app.py", default_timeout=20)
        self.history = pd.DataFrame(
            {"Close": np.concatenate([np.linspace(200, 100, 220), np.linspace(100, 300, 160)])},
            index=pd.date_range("2023-01-01", periods=380, freq="B"),
        )
        self.prices = pd.DataFrame({"AAPL": [100.0, 120.0, 90.0], "MSFT": [100.0, 100.0, 100.0],
                                    "NVDA": [50.0, 75.0, 100.0]},
                                   index=pd.date_range("2024-01-02", periods=3, freq="B"))

    @patch("trading_strategy.get_stock_data")
    def test_preserved_strategy_views(self, loader):
        loader.return_value = self.history
        self.app.run()
        self.assertEqual(len(self.app.exception), 0)
        self.assertEqual(len(self.app.get("plotly_chart")), 1)
        self.app.segmented_control[0].set_value("Trade statistics").run()
        self.assertEqual(len(self.app.exception), 0)
        self.assertEqual(self.app.metric[0].value, "1")
        self.app.segmented_control[0].set_value("Detailed trades").run()
        self.assertEqual(len(self.app.exception), 0)
        self.assertEqual(len(self.app.dataframe[0].value), 1)
        self.assertEqual(len(self.app.get("download_button")), 1)
        self.app.segmented_control[1].set_value("Non-winning").run()
        self.assertEqual(len(self.app.dataframe[0].value), 0)
        self.assertEqual(len(self.app.exception), 0)

    @patch("pd2_dashboard.load_market_data")
    @patch("trading_strategy.get_stock_data")
    def test_comparison_risk_and_cached_selection(self, strategy_loader, analytics_loader):
        strategy_loader.return_value = self.history
        analytics_loader.return_value = (self.prices, {})
        self.app.run()
        self.app.sidebar.radio[0].set_value("Multi-Stock Comparison").run()
        self.assertEqual(len(self.app.exception), 0)
        self.assertEqual(self.app.metric[0].value, "NVDA")
        self.assertEqual(len(self.app.get("plotly_chart")), 2)
        self.assertEqual(len(self.app.dataframe[0].value), 3)
        self.app.sidebar.radio[0].set_value("Risk Analysis Dashboard").run()
        self.assertEqual(len(self.app.exception), 0)
        self.assertEqual(self.app.metric[2].value, "-25.00%")
        self.app.selectbox[0].set_value("MSFT").run()
        self.assertEqual(self.app.metric[0].value, "0.00%")
        self.assertEqual(analytics_loader.call_count, 1)
        analytics_loader.return_value = (self.prices[["AAPL", "MSFT"]], {})
        self.app.sidebar.multiselect[0].set_value(["AAPL", "MSFT"]).run()
        self.assertEqual(analytics_loader.call_count, 2)
        self.assertEqual(len(self.app.dataframe[0].value), 2)
        self.assertEqual(len(self.app.exception), 0)

    @patch("pd2_dashboard.load_market_data")
    @patch("trading_strategy.get_stock_data")
    def test_ui_invalid_tickers_and_api_errors(self, strategy_loader, analytics_loader):
        strategy_loader.return_value = self.history
        analytics_loader.return_value = (pd.DataFrame(), {"AAPL": "Simulated timeout", "MSFT": "No data"})
        self.app.run()
        self.app.sidebar.radio[0].set_value("Multi-Stock Comparison").run()
        self.assertEqual(len(self.app.exception), 0)
        self.assertEqual(len(self.app.warning), 2)
        self.assertEqual(len(self.app.error), 1)
        self.app.sidebar.multiselect[0].set_value(["AAPL"]).run()
        self.assertIn("at least 2", self.app.error[0].value)
        self.assertEqual(len(self.app.exception), 0)
        self.app.sidebar.multiselect[0].set_value(["AAPL", "???"]).run()
        self.assertIn("Invalid US stock ticker", self.app.error[0].value)
        self.assertEqual(len(self.app.exception), 0)


if __name__ == "__main__":
    unittest.main()
