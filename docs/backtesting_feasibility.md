# Portfolio Backtesting: Preliminary Feasibility (T08)

Prepared: 2026-10-26. Assigned owner: M4. **Assessment only**: no portfolio engine
or portfolio test result is claimed. Week 1 gates covered the two easy features.

## Existing Evidence And Reuse

`trading_strategy.py` computes 50/200-session moving averages and Golden Cross
from current/prior values. These calculations can run separately for each stock.
The preserved regression fixture produces one crossover and a target exit; the
live MSFT run produced four trade records. This is evidence for reusable signal
generation, not validated multi-stock capital accounting.

Do **not** combine `implement_strategy()` trade means into portfolio return. It
uses same-close entry, creates independent potentially overlapping trades, skips
the first 200 rows, and closes on the last available price even if the 60-day
window is incomplete. It has no shared cash, quantity, cost or equity ledger.
These are inspected legacy assumptions, not deliberately introduced defects.

## Proposed Architecture

```text
market_data: validated price history + sufficient pre-start warm-up
        -> existing moving averages and Golden Cross per symbol
        -> new Week 2 daily order/position/cash ledger
        -> equity curve + fill records + reconciliation checks
        -> existing Streamlit navigation/chart libraries
```

Keep the simulator independent from Streamlit and the legacy trade function.
Reuse market-data validation and visualizations where their assumptions match.
No simulator module is created until Week 2.

## Design Questions And Technical Assumptions

| Question | Recommended MVP approach / unresolved point |
|---|---|
| Reuse existing strategy? | Reuse MA/crossover functions, not independent-trade return aggregation. Review initial 200-row slicing explicitly. |
| Align trading dates? | Restrict MVP to same-currency US equities. Calculate MAs on each symbol's original sessions with >=200 pre-start observations. Use shared eligible execution dates; warn/reject incompatible histories. Never backfill prices. |
| Allocate capital? | Split initial capital equally into N sleeves, each with its own cash/position; portfolio weights drift after trades. Equal initial allocation is not daily equal weighting. Fractional shares proposed for MVP, subject to approval. |
| Track cash/positions? | One long position per sleeve; cash never negative; mark equity = sum(cash + quantity x observed valuation price). No interest or leverage. Ledger records orders, fills, costs and realized/unrealized values. |
| Multiple signals? | Evaluate all signals using information available at that day's close. Ignore a new buy when its sleeve is already invested; no cross-sleeve capital borrowing. Deterministic ordering, exits then entries, no same-day round-trip. |
| Valid simulation? | Signal at close t -> earliest next session execution, not a retrospectively chosen close t. First executable signal needs warm-up. Execution at next Open requires preserving adjusted Open and documenting its basis; next Close is a simpler alternative with a full session delay. This choice is unresolved. |
| Exits? | Evaluate 15% target on observed close relative to executed basis; submit next-session exit. Time exit after 60 calendar days, execute on next eligible session. Weekend handling explicit. No intraday target fill assumed from closing-only data. |
| End of range? | Recommend mark open positions to final Close and report unrealized value separately, not fake a matured time exit. Forced liquidation, if selected instead, must be explicit and charged costs. |
| Trading costs? | Configurable nonnegative transaction-cost basis points plus optional slippage; reduce buying capacity and cash proceeds per actual fill. Use zero-cost and nonzero-cost fixtures; no unsupported broker precision claims. |
| Rebalancing feasible? | Automatic rebalancing adds order scheduling, extra costs and strategy conflicts. Defer it. Equal initial sleeves deliver the MVP without pretending weights remain equal. |

## Dependencies

T06 validated histories, approved T01 scope, T11 tested environment and T10 QA.
Data needs additional pre-start history and, for next-Open fills, actual adjusted
Open columns rather than inventing an `Adj Close` field. The current analytics
loader returns Close only; a narrow, tested loader extension will be needed.
Stay with pandas/numpy/yfinance/Plotly/Streamlit; no new backtesting framework
unless it demonstrably reduces work within the real remaining time budget.

## Major Risks And Expected Challenges

Look-ahead from same-bar execution; dividend/split basis mismatch; false daily
equal weighting; costs charged twice or omitted; simultaneous order cash
overspend; overlapping positions; incorrectly timed 60-day exits; omitted MA
warm-up; survivorship bias of chosen current tickers; missing or differing market
sessions; incorrect annualization; equity return confused with mean trade return.
Adjusted prices are a provider-adjusted analytical simulation, not a broker cash
dividend ledger. Report that limitation and do not double-credit dividends.

## MVP And Optional Improvements

MVP: 2-5 same-currency stocks, initial capital, equal initial sleeves, causal
Golden Cross orders, one long position per sleeve, cash, costs, daily equity,
completed and open trade records, explicit terminal policy and accounting tests.
Optional: rebalancing, benchmark, cash dividends, FX, whole-share rounding,
portfolio risk, optimizer and alternative strategy controls.

## Week 2 Strategy And Validation Gates

1. M1/M4 confirm price/fill basis, terminal treatment and cost units before coding.
2. M4 build a small deterministic ledger before UI work. M3 supplies data/warm-up
   checks and reviews calculation units.
3. M5 test all-cash/no-signal, one-stock, simultaneous two-stock, target/time exit,
   weekend, insufficient warm-up, nonzero costs and final open-position cases.
4. Assert cash >= 0, quantities >= 0, equity reconciliation each date, each cost
   exactly once, and no fill before its signal is known. Compare to hand values.
5. M2 integrate the validated curve/records; M5 rerun all W1 regressions before
   deployment. M1 remove optional scope if the real time budget is insufficient.

No duration estimate is presented as actual time. MVP appears technically
plausible from inspected signal logic, but execution/accounting correctness,
provider Open availability for chosen tickers and runtime cost remain unverified.