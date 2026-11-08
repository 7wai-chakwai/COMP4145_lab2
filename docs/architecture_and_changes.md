# Lab 2 Baseline, Compatibility And PD2 Architecture

Inspection and baseline date: 2026-10-26. No existing Scrum board, tests, docs
directory or screenshot-export workflow was found. Existing ignored environment
and caches were inspected as infrastructure, not rewritten.

## Existing Structure And Reusable Components

| Component | Observed role | Reuse / preservation |
|---|---|---|
| app.py | Streamlit entry point; load_results, price_chart, statistics, detailed_trades | All four functions structurally identical to commit c40801b; only page title/navigation wiring extended |
| trading_strategy.py | Yahoo period-based history; rolling MA50/MA200; GoldenCross; independent target/time exits; console analysis/main | Byte-for-byte unchanged; existing strategy reused |
| requirements.txt | pandas, numpy, yfinance, matplotlib, Streamlit >=1.49, Plotly >=6 | Same dependency set, pinned to installed tested versions; matplotlib retained for original work |
| README.md | Single Lab 2 heading | Extended with execution, features, structure and honest limitations |
| Original notebook | Single-stock and independent multi-stock trade examples | Preserved without execution; not a portfolio ledger |
| stock_data.csv | Date,Symbol,Open,High,Low,Close,Adj Close,Volume sample columns | Preserved; not silently substituted for live Yahoo data |
| Lab 1/Lab 2 Word files | Existing course materials | Preserved; no overwrite |
| .git / .venv | Git origin remote; Python 3.13.15 with required app packages | Reused, no commit/branch/push; no new Python packages |

## Recoverable Baseline

Tracked baseline commit: `c40801b` (`feat: add Streamlit trading strategy dashboard`).
The initial tracked worktree was clean; student notebook, CSV and Word documents
were untracked. Before code edits, a local archive preserved all original source,
README, requirements, CSV, notebook and both Word files:

` .baseline/lab2-before-pd2.tar.gz `

SHA-256: `fc4223549806b39cde8146eade1fce838ffdce0d018704fb474c2f6423ab4427`.
The archive is ignored, not committed. To inspect/recover **without overwriting
current work**, extract to a separate directory:

```sh
mkdir -p ../lab2-recovery
tar -xzf .baseline/lab2-before-pd2.tar.gz -C ../lab2-recovery
git show c40801b:app.py
```

Review differences before any deliberate restore. No reset, checkout, deletion
or unauthorized overwrite was performed.

## Compatibility Risks Identified Before Changes

Legacy same-close/independent-trade assumptions must not change in a Week 1 UI
extension. Its history API accepts periods, not dates. Shared analytics must not
mutate legacy frames or rely on notebook output. Installed Streamlit supports
new-option multiselects; lower/unpinned versions might not. Provider adjusted
columns, timezone handling, missing data and calendar differences affect metrics.
Existing untracked student files must stay untouched.

Smallest safe extension: keep legacy modules/functions, add one pure data/metrics
module and one UI module, then change top-level navigation only. Baseline AST
comparison and deterministic strategy/UI regressions verified preservation.

## Current Architecture And UI Structure

```text
app.py (Streamlit entry point)
  Sidebar: Stock Trading Strategy
    -> load_results (legacy one-hour cache) -> trading_strategy.py -> Yahoo
    -> Price chart | Trade statistics | Detailed trades / CSV
  Sidebar: Multi-Stock Comparison
    -> shared ticker/date controls -> load_analytics (one-hour cache)
    -> market_data.py -> Yahoo adjusted daily Close
    -> historical chart | shared-date index=100 | return ranking
  Sidebar: Risk Analysis Dashboard
    -> same controls/cache/data -> per-stock risk_metrics / drawdowns
    -> focus-stock cards | comparative bars | drawdown chart | coverage table
```

`pd2_dashboard.py` owns new controls/charts; `market_data.py` is UI-independent
and directly unit-testable. Two modules avoid separate loaders/processors/metric
classes with unnecessary indirection. No database/auth/frontend service was added.

## Week 2 Extension

```text
app.py
  Sidebar: Portfolio Backtesting
    -> portfolio_dashboard.py inputs/cache/presentation
    -> market_data.py adjusted Close histories plus MA warm-up
    -> portfolio_backtest.py causal signals and independent sleeve ledger
       -> strategy and equal buy-and-hold equity curves
       -> metrics, contributions and trade records
```

`portfolio_backtest.py` is Streamlit-independent. It calculates moving-average
signals from each stock's native observations and delays every fill until the
next observed session. Each sleeve holds cash or one long fractional position.
Portfolio equity is checked against the sum of sleeve values at every date.

Before Week 2 edits, `.baseline/week1-before-week2-20261029.tar.gz` preserved the
workspace except Git, virtualenv, caches and the baseline folder. SHA-256:
`2f6cd40987c99894e86107c950a170f2d097675355a1152bd7df03641ba0ba0c`.
Git itself could not provide a new baseline because the local Apple Command Line
Tools path was unavailable. The original Lab 2 archive remains unchanged.

## Data And Calculation Assumptions

- Use provider `history(interval='1d', auto_adjust=True, actions=False)` and its
  actual Close field. Start and end are inclusive in the UI; provider end is
  exclusive, so the request adds one day and then clips returned observations.
- Preserve local exchange session date when removing timezone, normalize and
  sort. Duplicate dates and missing/nonfinite/nonpositive Close are rejected;
  no forward fill, backfill or future-value interpolation.
- Outer alignment retains differing observed calendars for raw charts; common
  complete dates support fair normalization/ranking. Risk operates on each
  validated stock's original observations, not the shared-date subset.
- Returns = P(last)/P(first)-1; index=100*P/P(first); drawdown=P/running_peak-1;
  volatility=sample std(daily percentage returns)*sqrt(252). Stored fractions
  become percent only for metrics/charts. At least three prices are needed.
- Missing provider **rows** cannot be reliably distinguished from exchange
  holidays in this MVP. Short/irregular histories limit risk interpretation.
- No FX conversion; normalized results are local-currency percentage performance.
  Adjusted-price returns are not a modeled dividend/cost/cash ledger.

## Changes And Verification Boundary

Added shared data/risk processing, new comparison/risk UI, deterministic/AppTest
tests, launch task, ignore rules and management docs. Original charts, statistics,
trade records, download and strategy logic remain. Direct dependency pins reflect
the local environment, not a claimed clean/cloud install. See the test report for
actual commands, values and limitations; all portfolio implementation remains W2.
