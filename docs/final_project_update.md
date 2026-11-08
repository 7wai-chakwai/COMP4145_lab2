# Final Project Update

Prepared: 2026-10-29 for COMP4145 Project Development 2.

## Executive Summary

The existing Lab 2 Streamlit application now provides four integrated sections:
the original single-stock Golden Cross strategy, Multi-Stock Comparison, Risk
Analysis, and Multi-Stock Portfolio Backtesting. The Week 2 engine uses equal
independent cash sleeves and next-session execution. All 23 automated tests pass,
and live-data, local startup, desktop, and mobile checks succeeded. Remote
Streamlit Cloud deployment remains blocked pending explicit authorization.

## Objectives and Delivery Status

| Objective | Planned timing | Actual outcome |
|---|---|---|
| Preserve Lab 2 strategy, charts, statistics and records | Both weeks | Delivered and regression-tested |
| Multi-Stock Comparison | Week 1 | Delivered with shared-date normalization and ranking |
| Risk Analysis Dashboard | Week 1 | Delivered with volatility, drawdown, return and coverage |
| Portfolio Backtesting | Week 2 | Delivered with equal sleeves, costs, benchmark, contributions and trade history |
| Validation and integration | Week 2 | 23 tests pass; live and browser smoke checks completed |
| Streamlit Cloud deployment | Week 2 | Local preparation complete; remote action not authorized |
| Management records and report | Both weeks | Updated; missing real time/team feedback remains explicit |

## Week 1 and Week 2 Progress

Week 1 established validated market data, comparison, risk metrics, navigation,
thirteen tests, and a portfolio feasibility study. Week 2 added a pure simulation
engine, a fourth Streamlit section, ten additional automated tests, live portfolio
evidence, integration records, deployment preparation, the final board, and this
reporting package. A checksum-verified Week 1 archive was created before Week 2
edits because the local Git client was unavailable.

## Testing Results

The 23-test suite includes known-result financial calculations, loader failures,
legacy behavior, all dashboards, portfolio accounting, transaction costs,
calendar differences, invalid input, and partial-universe rejection. Compilation
and `pip check` passed. A new temporary environment installed only the five pinned
runtime requirements, then passed all 23 tests and `pip check`. Live
AAPL/MSFT/NVDA data produced a reconciled portfolio
curve. The browser rendered both the original and portfolio workflows, and the
mobile page had no document-level horizontal overflow.

## Technical Challenges and Decisions

The original per-trade function could not represent shared portfolio capital or
causal fills. The team plan therefore kept it unchanged and placed portfolio
accounting in a new pure module. Next observed adjusted Close was chosen because
the shared loader provides adjusted Close, while same-close execution would use
information unavailable before that close. Independent sleeves eliminated
simultaneous-signal overspending and made equal initial allocation auditable.
Open positions are marked at the end instead of creating a fictional liquidation.

Different calendars are handled on a union valuation calendar. Signals and fills
use each stock's actual observations, while the last observed price is carried
only to value an unchanged holding. A failed selected ticker stops the simulation
so the investment universe does not change silently. Automatic rebalancing,
optimization, leverage, and real-time execution remain outside scope.

The local Git executable failed because Apple Command Line Tools were missing.
Work continued from a separate archive without destructive version-control
commands. yfinance still emits non-blocking pandas deprecation warnings.

## Outcome and Outstanding Issues

The three PD2 feature objectives are functionally delivered and integrated with
Lab 2. T09, T10, and T12 meet their evidence gates. T13 remains blocked because
no remote push or deployment was authorized; therefore no public application URL
is reported. The real coding-time log and individual team feedback are also
missing and cannot be invented.

Future work can add whole-share execution, bid-ask spread and slippage, cash
dividends, FX conversion, delisted-symbol datasets, periodic rebalancing,
benchmarks beyond equal buy-and-hold, and cloud monitoring after deployment.

## Feature 4 Enhancement Addendum

On 2026-11-04, T14 added a shared custom US-stock watchlist without changing the
historical Scrum snapshots. Comparison, risk, and portfolio now use one persistent
selection with a configurable default maximum of 20. Users can type symbols,
remove entries, clear the watchlist, or restore defaults. Provider history still
determines availability, and optional Yahoo metadata rejects known non-equity or
non-USD instruments. The complete suite increased from 23 to 31 passing tests.
