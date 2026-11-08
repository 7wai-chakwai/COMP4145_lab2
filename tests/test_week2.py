from datetime import date
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

from portfolio_backtest import backtest_portfolio, moving_average_signals


class PortfolioEngineTests(unittest.TestCase):
    def setUp(self):
        self.index = pd.date_range("2025-01-02", periods=9, freq="B")
        self.cycle = pd.Series(
            [5.0, 4.0, 3.0, 4.0, 5.0, 6.0, 5.0, 4.0, 3.0],
            index=self.index,
            name="AAPL",
        )

    def test_no_signal_and_constant_prices(self):
        prices = pd.DataFrame({"AAPL": 100.0}, index=self.index)
        result = backtest_portfolio(prices, self.index[0], 1_000, 2, 3, end_date=self.index[-1])
        self.assertTrue(result.trade_history.empty)
        np.testing.assert_allclose(result.equity_curve["Strategy"], 1_000)
        self.assertEqual(result.metrics["Total Return (%)"], 0)
        self.assertEqual(result.metrics["Annualized Volatility (%)"], 0)

    def test_complete_cycle_executes_next_session(self):
        result = backtest_portfolio(
            self.cycle.to_frame(), self.index[0], 1_000, 2, 3, end_date=self.index[-1]
        )
        trades = result.trade_history
        self.assertEqual(trades["Action"].tolist(), ["Buy", "Sell"])
        self.assertEqual(trades.iloc[0]["SignalDate"], self.index[4])
        self.assertEqual(trades.iloc[0]["TradeDate"], self.index[5])
        self.assertEqual(trades.iloc[1]["SignalDate"], self.index[7])
        self.assertEqual(trades.iloc[1]["TradeDate"], self.index[8])
        self.assertAlmostEqual(trades.iloc[0]["ExecutionPrice"], 6.0)
        self.assertAlmostEqual(trades.iloc[1]["ExecutionPrice"], 3.0)
        self.assertAlmostEqual(result.metrics["Final Portfolio Value"], 500.0)
        self.assertAlmostEqual(result.metrics["Maximum Drawdown (%)"], -50.0)

    def test_transaction_cost_is_charged_once_per_fill(self):
        result = backtest_portfolio(
            self.cycle.to_frame(), self.index[0], 1_000, 2, 3, 100, self.index[-1]
        )
        buy_quantity = 1_000 / (6.0 * 1.01)
        expected_buy_cost = buy_quantity * 6.0 * 0.01
        expected_sell_cost = buy_quantity * 3.0 * 0.01
        expected_final = buy_quantity * 3.0 - expected_sell_cost
        self.assertAlmostEqual(result.trade_history.iloc[0]["Quantity"], buy_quantity)
        self.assertAlmostEqual(result.metrics["Transaction Costs"], expected_buy_cost + expected_sell_cost)
        self.assertAlmostEqual(result.metrics["Final Portfolio Value"], expected_final)

    def test_equal_sleeves_and_multiple_stock_contributions(self):
        prices = pd.DataFrame({
            "AAPL": self.cycle,
            "MSFT": 100.0,
            "NVDA": [10.0, 9.0, 8.0, 9.0, 10.0, 12.0, 11.0, 10.0, 9.0],
        }, index=self.index)
        result = backtest_portfolio(prices, self.index[0], 9_000, 2, 3, end_date=self.index[-1])
        np.testing.assert_allclose(result.contributions["Initial Allocation"], 3_000)
        self.assertAlmostEqual(result.contributions.loc["MSFT", "Strategy Profit/Loss"], 0)
        self.assertAlmostEqual(
            result.metrics["Final Portfolio Value"], result.sleeve_values.iloc[-1].sum()
        )
        self.assertTrue((result.sleeve_values >= -1e-9).all().all())
        self.assertTrue((result.trade_history["Quantity"] > 0).all())

    def test_different_calendars_use_union_and_observed_execution_dates(self):
        prices = pd.DataFrame({"AAPL": self.cycle, "MSFT": self.cycle.values}, index=self.index)
        prices.loc[self.index[[1, 5]], "MSFT"] = np.nan
        result = backtest_portfolio(prices, self.index[0], 2_000, 2, 3, end_date=self.index[-1])
        self.assertEqual(result.equity_curve.index.tolist(), self.index.tolist())
        msft_observed = set(prices["MSFT"].dropna().index)
        msft_trade_dates = set(result.trade_history.loc[result.trade_history["Ticker"] == "MSFT", "TradeDate"])
        self.assertTrue(msft_trade_dates.issubset(msft_observed))
        self.assertFalse(result.equity_curve.isna().any().any())

    def test_insufficient_data_and_invalid_inputs_are_rejected(self):
        short_prices = pd.DataFrame({"AAPL": [1.0, 2.0, 3.0]}, index=self.index[:3])
        with self.assertRaisesRegex(ValueError, "at least 6"):
            backtest_portfolio(short_prices, self.index[0], 1_000, 2, 5, end_date=self.index[2])
        with self.assertRaisesRegex(ValueError, "positive"):
            backtest_portfolio(self.cycle.to_frame(), self.index[0], 0, 2, 3, end_date=self.index[-1])
        with self.assertRaisesRegex(ValueError, "smaller"):
            backtest_portfolio(self.cycle.to_frame(), self.index[0], 1_000, 3, 3, end_date=self.index[-1])
        with self.assertRaisesRegex(ValueError, "basis points"):
            backtest_portfolio(self.cycle.to_frame(), self.index[0], 1_000, 2, 3, -1, self.index[-1])

    def test_final_open_position_is_marked_without_fake_sell(self):
        rising = pd.Series([5.0, 4.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0], index=self.index)
        result = backtest_portfolio(rising.to_frame("AAPL"), self.index[0], 900, 2, 3, end_date=self.index[-1])
        self.assertEqual(result.trade_history["Action"].tolist(), ["Buy"])
        self.assertAlmostEqual(result.metrics["Final Portfolio Value"], 1_350)
        self.assertIn("not forcibly sold", result.assumptions["Terminal Treatment"])

    def test_signal_calculation_does_not_change_input(self):
        original = self.cycle.copy()
        signals = moving_average_signals(self.cycle, 2, 3)
        pd.testing.assert_series_equal(self.cycle, original)
        self.assertEqual(signals.loc[self.index[4]], 1)
        self.assertEqual(signals.loc[self.index[7]], -1)


class PortfolioDashboardTests(unittest.TestCase):
    def setUp(self):
        import streamlit as st
        from streamlit.testing.v1 import AppTest

        st.cache_data.clear()
        self.app = AppTest.from_file("../app.py", default_timeout=20)
        self.strategy_history = pd.DataFrame(
            {"Close": np.concatenate([np.linspace(200, 100, 220), np.linspace(100, 300, 160)])},
            index=pd.date_range("2023-01-01", periods=380, freq="B"),
        )
        portfolio_index = pd.bdate_range(end=pd.Timestamp(date.today()), periods=110)
        cycle = np.concatenate([np.linspace(140, 80, 55), np.linspace(80, 180, 55)])
        self.portfolio_prices = pd.DataFrame({
            "AAPL": cycle,
            "MSFT": cycle * 1.1,
            "NVDA": cycle * 0.7,
        }, index=portfolio_index)

    @patch("portfolio_dashboard.load_market_data")
    @patch("trading_strategy.get_stock_data")
    def test_portfolio_workflow_and_validation(self, strategy_loader, portfolio_loader):
        strategy_loader.return_value = self.strategy_history
        portfolio_loader.return_value = (self.portfolio_prices, {})
        self.app.run()
        self.app.sidebar.radio[0].set_value("Portfolio Backtesting").run()
        self.assertEqual(len(self.app.exception), 0)
        self.assertEqual(len(self.app.metric), 5)
        self.assertEqual(len(self.app.get("plotly_chart")), 2)
        self.assertGreaterEqual(len(self.app.dataframe), 2)
        self.assertGreater(len(self.app.dataframe[1].value), 0)
        self.assertEqual(portfolio_loader.call_count, 1)

        portfolio_loader.return_value = (self.portfolio_prices[["AAPL", "MSFT"]], {})
        self.app.sidebar.multiselect[0].set_value(["AAPL", "MSFT"]).run()
        self.assertEqual(len(self.app.error), 0)
        self.assertEqual(len(self.app.dataframe[0].value), 2)
        self.assertEqual(len(self.app.exception), 0)

    @patch("portfolio_dashboard.load_market_data")
    @patch("trading_strategy.get_stock_data")
    def test_portfolio_data_failure_preserves_universe(self, strategy_loader, portfolio_loader):
        strategy_loader.return_value = self.strategy_history
        portfolio_loader.return_value = (
            self.portfolio_prices[["AAPL", "MSFT"]],
            {"NVDA": "Simulated missing history"},
        )
        self.app.run()
        self.app.sidebar.radio[0].set_value("Portfolio Backtesting").run()
        self.assertEqual(len(self.app.exception), 0)
        self.assertEqual(len(self.app.warning), 1)
        self.assertIn("universe was not changed", self.app.error[0].value)


if __name__ == "__main__":
    unittest.main()
