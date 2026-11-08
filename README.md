# Stock Trading Analytics Platform

COMP4145 PD2 two-week enhancement of the existing Lab 2 Streamlit application.
Two-week project, five assigned roles (M1-M5). Educational historical analytics,
not investment advice or a prediction service.

## Implemented Features

- **Stock Trading Strategy:** original five-year MSFT Golden Cross strategy,
	50/200-session averages, buy/sell chart markers, 15% target, 60-calendar-day
	holding limit, trade statistics, filtered detailed records and CSV download.
- **Multi-Stock Comparison:** select 2-5 symbols (AAPL, MSFT, NVDA by default),
	inclusive date range, interactive adjusted-price and baseline-100 charts,
	common-period cumulative returns and best historical performer.
- **Risk Analysis Dashboard:** annualized daily-return volatility, maximum
	drawdown, cumulative return, selected-stock cards, comparative bars,
	drawdown chart and data-coverage table.
- **Portfolio Backtesting:** select 1-20 stocks by default, dates, initial capital, short and
	long moving averages, and per-trade costs. The engine simulates equal initial
	cash sleeves, next-session Golden Cross fills, portfolio/benchmark equity,
	risk/return metrics, stock contributions, and downloadable trade history.
- **Custom US Stock Selection and Watchlist:** one shared, session-persistent
	watchlist feeds comparison, risk, and portfolio pages. Users can type US stock
	symbols, add/remove chips, clear the list, or restore AAPL/MSFT/NVDA defaults.
	The ten displayed companies are suggestions rather than an allowed-only list.
- Shared analytics controls, one-hour data caching, refresh, loading and error
	states. Failed portfolio symbols stop the run rather than silently changing
	the selected investment universe.

Comparison requires at least two usable stocks. Risk analysis and portfolio
backtesting support one or more. The default maximum is 20 selected stocks and
can be changed before startup with `PD2_MAX_SELECTED_STOCKS`. Selecting more than
10 shows a performance/rate-limit warning.

## Installation And Execution

Validated locally with Python 3.13.15. Use Python 3.13 for the tested baseline.
The existing environment is `.venv`; no packages were added during Week 1.
Direct application dependencies are pinned to the installed, tested versions.
The unused matplotlib runtime dependency was removed; the preserved notebook
can install its own optional plotting dependency if it is executed separately.

```sh
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open http://localhost:8501. VS Code also includes a **Run PD2 Streamlit** task.
Use another port with `--server.port=8502` if 8501 is occupied.

```sh
python -m unittest discover -s tests -p 'test_*.py' -v
python -m pip check
```

The standard-library test suite does not require pytest or a live API. All
**31 tests pass**: the original 23 tests plus eight custom-selection, provider,
shared-state, limit, and variable-allocation checks. Separate live-data
and browser observations are recorded in the Week 1 and Week 2 test reports. A
new temporary Python 3.13 environment installed the five pinned requirements and
passed the same 23 tests plus `pip check`.

## Project Structure

```text
app.py                  Existing entry point and preserved Lab 2 chart/statistics/records
trading_strategy.py     Unchanged Lab 2 loader, moving averages, signals and trade rules
market_data.py          Date-aware Yahoo loading, validation, alignment and analytics
pd2_dashboard.py        New Streamlit inputs, caching and comparison/risk views
portfolio_backtest.py   Pure causal signal, sleeve accounting, benchmark and metrics engine
portfolio_dashboard.py  Portfolio controls, caching, charts, metrics and trade table
stock_selector.py       Shared custom US stock watchlist and session-state controls
tests/test_week1.py     Deterministic calculations, failure handling and UI regressions
tests/test_week2.py     Portfolio expected-value, invariant and Streamlit tests
tests/test_stock_selection.py  Ticker validation, shared watchlist and variable-count tests
docs/                   Requirements, sprint/risk logs, feasibility and progress evidence
.vscode/tasks.json      Local Streamlit launch task
requirements.txt        Five tested direct application dependency versions
stock_data.csv          Original sample data; not an automatic live-data fallback
COMP1016_Mini_Project_B_Trading_Strategy.ipynb  Original notebook, preserved
.baseline/              Ignored local recovery archive; not a deployment artifact
```

Original Lab 1/Lab 2 Word files are preserved. The notebook's optional `IPython`
import is unresolved in this environment; notebook execution was not required or
validated. The running application does not depend on it.

## Assumptions And Limitations

New analytics explicitly use Yahoo's `auto_adjust=True` daily **Close**, not an
assumed `Adj Close` column. Adjusted returns reflect provider adjustment factors,
not a cash-dividend ledger or a realizable portfolio result. Raw prices are in
each symbol's quoted currency; there is no FX conversion.

Ticker text is normalized to uppercase and deduplicated before loading. A valid
format does not prove that a symbol exists: each selection must return at least
three usable prices. When Yahoo supplies instrument metadata, non-equities and
non-USD instruments are rejected. Missing metadata cannot independently prove a
US listing, so provider availability and classification remain limitations.

Comparison uses common observed dates and never fills prices. Risk uses each
stock's own observed sessions and shows its coverage. Missing/invalid Close
values, duplicate dates and fewer than three observations are rejected. Holidays
and absent provider rows are not reconstructed. Volatility uses sample standard
deviation (`ddof=1`) and 252 sessions/year; short or irregular histories may be
misleading. API errors are reported, not replaced with fabricated prices.

The Lab 2 strategy is intentionally unchanged: it assumes same-close entry,
allows independent trades and may close a trade at the dataset boundary before
60 days. It excludes fees, slippage and portfolio cash accounting. Do not use
its per-trade mean as portfolio return. See
[the feasibility assessment](docs/backtesting_feasibility.md) before Week 2.

The portfolio engine uses equal independent cash sleeves. Crossovers observed at
adjusted Close t execute at the stock's next observed adjusted Close. It permits
fractional shares, applies the configured basis-point cost once per fill, and
marks open positions at the end. It uses a union valuation calendar and carries
the last observed price only to value an unchanged holding. It excludes spread,
slippage, taxes, interest, whole-share limits, cash dividends, FX, leverage,
shorting, optimization and automatic rebalancing.

Yahoo library pandas deprecation warnings were observed but did not block tests.
Network access is required for live data; caching cannot guarantee API uptime.
Cross-market completeness, broker execution and long-term API reliability remain
limitations. Live values can change when Yahoo revises adjusted history.

## Project Management Records

- [Requirements and acceptance criteria](docs/requirements_analysis.md)
- [Sprint plan](docs/sprint_plan.md), [risks](docs/risk_register.md),
	[issues and decisions](docs/issues_and_decisions.md)
- [Lab 2 baseline and architecture](docs/architecture_and_changes.md)
- [Before Week 1 planned board](docs/scrum_before_week1.md)
- [Week 1 actual board and progress](docs/scrum_end_week1.md)
- [Week 2 actual board](docs/scrum_end_week2.md)
- [Initial project update](docs/initial_project_update.md)
- [Backtesting validation](docs/backtesting_validation.md) and
	[integration test results](docs/integration_test_results.md)
- [Final project update](docs/final_project_update.md) and
	[project reflection](docs/project_reflection.md)
- [Feature 4 implementation and test results](docs/feature4_update.md)
- [Real coding-time log](docs/coding_time_log.csv)
- [Week 2 submission status](docs/week2_submission.md)

Baseline commit: `c40801b`. Recovery instructions and both archive checksums are
in the architecture record. The current Git client is unavailable because the
local Apple Command Line Tools path is missing; no reset, commit, push or remote
deployment was performed. Repair the toolchain before staging project files.

## Deployment Status

Local compilation, clean installation, package consistency, Streamlit health,
desktop/mobile browser flows, requirements review and source-secret search passed. Streamlit Community
Cloud remains pending because remote actions require explicit authorization.
After authorization: repair Git, review/stage the intended files, push to the
existing repository, select `app.py` as the Streamlit entry point with Python
3.13, deploy, then repeat the four-page navigation and invalid-input smoke tests
on the public URL. Do not add a secrets file; the application uses no credentials.

**Public deployed application URL:** pending authorization and verification.
Localhost is not a public deployment.

No elapsed coding time is claimed. Team members must fill actual start/end times
and enforce the assignment's **less than 180 minutes total** vibe-coding limit.
