# Week 1 Test Results

Executed: 2026-10-26. Assigned verification owner: M5. Environment: macOS,
existing `.venv`, Python 3.13.15; pandas 3.1.0, numpy 2.5.4, yfinance 1.7.0,
Streamlit 1.66.1, Plotly 7.1.0, matplotlib 3.11.2.

## Automated Reproducible Suite

```sh
.venv/bin/python -m unittest discover -s tests -p 'test_week1.py' -v
```

**Actual final executed result: 13 tests, OK.** The first ten calculation/loader/
strategy tests passed before UI integration. First UI attempt had three test-path
setup errors (I01); after fixing `../app.py`, all thirteen passed. Mocked API
responses and simulated failures are test fixtures, not live outages or results.

| Test case | Expected result | Actual result | Pass/Fail | Notes |
|---|---|---|---|---|
| Normalization / cumulative return | First values all 100; last=[90,100,200]; returns=[-10,0,100]% | Assertions matched | Pass | AAPL=[100,120,90], MSFT constant 100, NVDA=[50,75,100] |
| Volatility / drawdown | AAPL sample std([0.2,-0.25])*sqrt(252)*100; drawdown -25%; flat MSFT volatility 0 | Numerical assertions matched | Pass | Drawdown curve [0,0,-0.25] also checked |
| Stock input selection | Uppercase/deduplicate; reject <2, >5, empty/malformed inputs | All assertions matched | Pass | Supports three default stocks and 2-5 scope |
| Date input | Reject reversed dates and future end date | ValueError in both cases | Pass | Independent of API |
| Historical cleaning | Preserve session date, remove timezone, sort; reject NaN/inf/nonpositive/duplicates/empty/short data | All assertions matched | Pass | No filling or input mutation |
| Alignment / insufficient history | Shared observations only; reject <3 common dates or incomplete risk inputs | Assertions matched | Pass | Original missing row remains missing |
| Partial API failure | Two valid series retained; failed ticker reported; end request +1 day; auto_adjust=True | Assertions matched | Pass | Simulated failure, mocked Yahoo |
| All API failures | Empty results + symbol-specific errors, no crash | Assertions matched | Pass | Mocked empty histories |
| Real MA / Golden Cross / target exit | MA values correct, initial MA200 unavailable, one genuine cross, >=15% exit | One trade, Target reached | Pass | Deterministic 380-session down/up fixture |
| Holding limit / no signals | Empty trades with no signal; last available session <=60 calendar days with no target | Zero-return Max holding period exit | Pass | Deterministic 300-session flat fixture |
| Original Streamlit strategy views | Chart, statistics, detailed records, CSV control and outcome filter work | No AppTest exceptions; expected chart/trade/filter assertions | Pass | Data mocked; download control checked, browser file bytes not tested |
| Comparison/risk/changed selection/cache | Three stocks/two charts; NVDA best; AAPL drawdown -25%; focus MSFT changes; navigation cache reused; two-stock selection reloads | Assertions matched; loader called once then twice after change | Pass | Streamlit AppTest, controlled inputs |
| UI invalid input/API errors | Warnings/error states, malformed or one-symbol selection never crashes | Expected messages, zero AppTest exceptions | Pass | Simulated provider errors explicitly identified |

## Live And Environment Checks (Separate From Fixtures)

| Test case | Expected result | Actual result | Pass/Fail | Notes |
|---|---|---|---|---|
| Live AAPL/MSFT/NVDA history, 2024 | Three usable series and common dates | No symbol errors; 252 rows x 3, 2024-01-02 through 2024-12-31 | Pass | Executed with actual Yahoo requests, not fixtures |
| Live Lab 2 MSFT history | Existing loader/signal/strategy runs | 1,255 rows; 4 crosses; 4 trade records | Pass | Five-year moving period; result can change later |
| Live invalid ticker NOTREALPD2XYZ | Invalid-symbol error isolated while AAPL survives | Yahoo 404/no timezone reported; AAPL retained 252 rows; no exception escaped | Pass | Deliberate negative test, not a system outage |
| Baseline preservation | Original strategy and four app functions unchanged | Git diff of strategy empty; AST equality of load_results,price_chart,statistics,detailed_trades passed | Pass | Compare to c40801b |
| Dependencies | Required app imports resolve; no broken package dependencies | App modules importable; pip check: No broken requirements found | Pass | Optional notebook IPython unresolved, notebook not executed |
| Python compile / diagnostics | New source compiles with no reported errors | compileall passed; editor errors empty for four touched Python files; market_data Pylance diagnostics empty | Pass | Not a project-wide strict type audit |
| Streamlit startup / HTTP | Launch task starts; /_stcore/health responds | Local URL http://localhost:8501; HTTP health body ok | Pass | Actual running server, not only AppTest |
| Live browser strategy/comparison | Preserved MSFT plot and three-stock price/normalized charts render | Browser snapshot shows MAs/buy/sell, 4 trades, both comparison plots and ranking | Pass | Desktop viewport 1440x1000, live data |
| Desktop/mobile risk visualization | Live risk cards and nonblank charts; mobile labels fit without document overflow | Desktop screenshot shows cards/bars/drawdown; 390x844 mobile screenshot shows stacked cards; document width=390; both charts present; drawdown screenshot readable | Pass | I03 title/legend spacing corrected and 13-test suite rerun successfully; screenshot is a spot check, not exhaustive accessibility testing |
| Documentation/dependency packaging | Required files/links exist; direct pins match installed versions; time log remains blank | Eleven required Markdown documents verified; all links resolve; six version pins match; CSV has header only | Pass | Structured runtime assertions, no invented time entries |
| Patch consistency | No whitespace errors | git diff --check passed | Pass | Version-control review gate |

Live 2024 metrics observed (percent, rounded; provider adjustments may change):

| Ticker | Cumulative return | Annualized volatility | Maximum drawdown |
|---|---|---|---|
| AAPL | 35.5563 | 22.4197 | -15.3548 |
| MSFT | 14.5016 | 19.9495 | -15.4868 |
| NVDA | 178.8741 | 52.5106 | -27.0468 |

Live values are integration observations, not independently known expected
financial answers. Correctness claims rely on deterministic expected-value tests.
Yahoo/pandas emitted non-blocking deprecation warnings (I02). Bare-mode
Streamlit test warnings did not produce test failures.

## Not Yet Verified

Clean-environment dependency installation, cloud deployment/public URL, portfolio
calculation/execution/accounting, long-running API reliability, notebook execution,
exhaustive browser accessibility and cross-market data completeness. No portfolio
or Week 2 test is marked passed. Team UAT/sign-off remains separate from software
checks. No actual elapsed coding time is certified here.