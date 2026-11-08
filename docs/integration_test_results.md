# Week 2 Integration Test Results T12

Executed: 2026-10-29 to 2026-10-30 in the existing Python 3.13.15 virtual
environment and a separate temporary clean Python 3.13 environment.

## Automated Suite

Command: `.venv/bin/python -m unittest discover -s tests -p 'test_*.py' -v`

Actual result: **23 tests passed, 0 failed** in 1.531 seconds.

| Area | Evidence | Result |
|---|---|---|
| Original Lab 2 strategy | Golden Cross fixture, target and holding exits, chart/statistics/records/filter/download AppTest | Pass |
| Multi-Stock Comparison | Controlled prices, two charts, ranking, ticker changes, cache behavior, invalid ticker and API failure handling | Pass |
| Risk Analysis | Known cumulative return, sample volatility, drawdown, focus-stock cards, coverage table | Pass |
| Portfolio engine | Eight expected-value tests and runtime accounting invariants | Pass |
| Portfolio UI | Navigation, five metrics, equity/benchmark and contribution charts, results tables, three-stock validation | Pass |
| Portfolio data failure | Partial universe rejected with a ticker warning; selected universe not silently reduced | Pass |
| Python compilation | Application and test modules compiled without error | Pass |
| Dependency consistency | `pip check` returned no broken requirements | Pass |
| Clean installation | Five pinned runtime dependencies installed in a new temporary environment; all 23 tests and `pip check` passed there | Pass |
| Editor diagnostics | No errors reported for changed Python files | Pass |

## Live and Browser Smoke Tests

The current Streamlit application loaded through a real browser at
`http://localhost:8501`. The original MSFT page showed the close, MA50, MA200,
buy and sell traces and four current live trades. Navigation to Portfolio
Backtesting loaded AAPL, MSFT, and NVDA and displayed five metrics, two charts,
individual contributions, trade history, download control, and the assumptions
panel. The Streamlit health URL returned `ok`.

At a 390 x 844 viewport, the portfolio page reported a 390-pixel document width,
two Plotly charts, and no document-level horizontal overflow. This is a targeted
responsive smoke test, not an exhaustive accessibility audit.

## Errors and Resolutions

| ID | Observed error | Cause | Resolution | Status |
|---|---|---|---|---|
| I04 | Git commands fail with `invalid active developer path` | Local Apple Command Line Tools installation is unavailable | Created and checksum-verified a separate W1 archive; did not reset or discard files | Open environment issue |
| I05 | VS Code task output referenced an earlier run and port 8501 was already held | Existing Streamlit process and stale task output | Checked the listener, opened the current app directly, verified current navigation and health | Resolved for local QA |
| I06 | Portfolio caption treated dollar signs as markup in the rendered accessibility tree | Dollar-delimited text can be interpreted as math markup | Changed caption amounts to explicit `USD` text | Resolved |

The recurring yfinance Pandas4 deprecation warnings remain non-blocking issue
I02. No synthetic failure is represented as a production incident.

## Deployment Boundary

Local startup, health, browser rendering, source-secret search, clean dependency
installation, all tests, and package consistency passed. A remote GitHub push and
Streamlit Community Cloud deployment were not authorized, so no public URL or
cloud smoke result is claimed.
