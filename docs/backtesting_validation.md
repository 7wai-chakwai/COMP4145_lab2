# Portfolio Backtesting Validation T10

Executed: 2026-10-29. Deterministic expected-value tests are the correctness
evidence. Live Yahoo results are reported separately because provider values can
change and are not independently known answers.

## Model Under Test

The engine splits initial capital into equal independent sleeves. A crossover
calculated from adjusted Close on session t executes at that stock's next
observed adjusted Close. Fractional shares are allowed. Costs are charged once
on each buy or sell notional. Cash is not shared, borrowed, or automatically
rebalanced. Open positions are marked at the final observed Close.

## Deterministic Results

Command: `.venv/bin/python -m unittest tests.test_week2.PortfolioEngineTests -v`

Actual result: **8 tests passed, 0 failed**.

| Test case | Expected result | Actual result | Result |
|---|---|---|---|
| No buy signal | Constant prices leave the sleeve in cash; return and volatility are zero | No trades; equity remained USD 1,000 | Pass |
| One buy and sell cycle | Prices 5,4,3,4,5,6,5,4,3 produce a buy signal at day 5, fill at 6 next session, sell signal at day 8, fill at 3 next session | Two fills on exact delayed dates; final value USD 500 | Pass |
| Multiple stocks | USD 9,000 becomes three USD 3,000 sleeves; total equity equals sleeve sum | Allocations and reconciliation matched | Pass |
| Constant stock in portfolio | Constant sleeve has no trade and no profit or loss | MSFT sleeve remained USD 3,000 | Pass |
| Different calendars and missing rows | Valuation uses union of observed sessions; fills occur only on the stock's own observed dates | Full union curve, no missing equity, no fabricated MSFT fill date | Pass |
| Insufficient MA history | Long MA 5 requires at least 6 observations | Three-row history rejected with an explicit error | Pass |
| Transaction costs | 100 bps buy and sell costs equal independently calculated notional x 1% amounts | Quantity, both costs, total costs, and final cash matched | Pass |
| Allocation and cash consistency | No negative sleeve, quantity, borrowing, or equity mismatch | Invariants and positive quantities passed | Pass |
| Look-ahead prevention | Each fill date is strictly after its signal date | Buy and sell both filled on the next observed session | Pass |
| Maximum drawdown | USD 1,000 falling to USD 500 after entry has a -50% maximum drawdown | Reported -50.00% | Pass |
| Final open position | One buy without later sell remains open and is marked at final price | One buy only; final marked value USD 1,350 | Pass |
| Input validation | Reject nonpositive capital, short MA >= long MA, and negative costs | Each invalid input raised the expected error | Pass |

## Accounting Invariants

The engine checks each valuation date. Strategy equity must equal the sum of all
sleeves. Cash and quantity cannot become negative beyond floating-point
tolerance. Buy quantity includes the buy cost in its affordability calculation,
so a fill cannot spend more than sleeve cash. Costs are recorded once per fill.
Signals dated before the requested start are not queued into the simulation.

## Live Observation

AAPL, MSFT, and NVDA returned 315 adjusted-price rows from 2023-10-02 through
2024-12-31 with no symbol errors. A 2024 simulation using USD 10,000, 20/50 MAs,
and 10 basis points produced 16 trades, final value USD 11,270.74, 12.7074%
return, -17.4533% maximum drawdown, 17.0628% annualized volatility, and a
76.1345% buy-and-hold return. Equity reconciliation passed. These values are a
live smoke test and may change with provider adjustments.

## Limitations

Adjusted Close is an analytical provider series, not a broker execution quote.
Next-Close execution avoids same-close look-ahead but assumes that closing price
is achievable. Missing provider rows cannot be distinguished reliably from
exchange holidays. Last observed prices are carried only to value unchanged
holdings on another market's session. The model omits spread, slippage, taxes,
interest, whole-share constraints, dividends as cash, FX conversion, delisted
stocks, and survivorship effects. Annualization uses 252 sessions. No forced
terminal sale is added.
