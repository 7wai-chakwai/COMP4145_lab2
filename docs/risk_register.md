# Risk Register (T02)

Prepared: 2026-10-26. Likelihood/impact are qualitative planning assessments,
not measured probabilities. A risk is not an issue unless actually observed.

| Risk ID | Description | Likelihood | Impact | Owner | Mitigation | Current Status |
|---|---|---|---|---|---|---|
| R01 | Yahoo Finance reliability, rate limits or network outages | Medium | High | M3 | One-hour cache, explicit refresh, per-symbol timeout/error isolation; tests use fixtures | Open; live valid requests passed; future availability not guaranteed |
| R02 | Missing/inconsistent historical data, unequal dates or short histories | High | High | M3 | Explicit adjusted Close, sort/validate indexes, reject corrupt values/duplicates, common-date comparison, show per-stock risk coverage; never fill future prices | Mitigated for W1; provider session completeness remains an assumption |
| R03 | Incorrect risk calculations/units or irregular-return annualization | Medium | High | M3 | Known-result tests, ddof=1, 252 convention, percent labels, no pct_change filling | Core formulas tested; market-calendar and short-history limitations remain |
| R04 | Portfolio calculation complexity: cash, simultaneous signals, execution and terminal handling | High | High | M4 | Separate ledger, equal initial sleeves, causal fills, accounting invariants and hand fixtures; no automatic rebalancing MVP | Open; preliminary assessment complete, engine unimplemented |
| R05 | Limited development time, including <3-hour vibe-coding rule | High | High | M1 | Real start/end log, easy features first, optional scope deferred; gate additional work on actual remaining budget | Open; actual elapsed time not supplied or certified |
| R06 | New UI/data changes regress working Lab 2 features | Medium | High | M2 | Recovery archive, unchanged strategy and original four UI functions, deterministic/AppTest regressions | W1 mitigated; broader W2 integration testing pending |
| R07 | Deployment dependencies/environment differ from local environment | Medium | High | M5 | Pin tested direct versions, pip check, correct app entry point, clean install/cloud smoke test in W2 | Local checks passed; fresh/cloud install unverified |
| R08 | Provider dependency deprecations become breaking changes | Medium | Medium | M5 | Record observed yfinance/pandas warnings, retain tested pins, assess updates with regression tests | Open non-blocking warning, issue I02 |
| R09 | Same-close execution, overlapping trades and truncated exits misrepresented as valid portfolio results | High | High | M4 | Preserve legacy for compatibility, label per-trade results, use next-session execution and explicit ledger in W2 | Identified by code inspection; portfolio design decision required |

Review owners and statuses at the next actual team checkpoint. Reassess after
T09 fixtures and cloud installation; do not mark risks closed based on one live call.

## End of Week 2 Review

| Risk | Week 2 status and actual impact | Mitigation performed | Remaining exposure |
|---|---|---|---|
| R01 Financial API reliability | No outage occurred; live calls passed and warnings recurred | Cache, refresh, per-symbol error reporting, fixtures independent of Yahoo | Provider availability and revisions remain external |
| R02 Missing or inconsistent data | Synthetic missing sessions and failed tickers were exercised | Native-session signals, union valuation calendar, no silent universe reduction | Provider omissions cannot always be separated from holidays |
| R03 Calculation accuracy | No deterministic mismatch occurred | Known-value tests for return, volatility, drawdown, costs and reconciliation | 252-session annualization and adjusted-price basis remain assumptions |
| R04 Backtesting complexity | Material design impact; original trade aggregator was unsuitable | Separate ledger, equal sleeves, causal fills, runtime invariants and terminal mark policy | More realistic execution and dividend models are future scope |
| R05 Limited time | Actual elapsed time remains unknown because the log is blank | MVP kept focused; rebalancing, optimization and advanced execution deferred | Compliance with the 180-minute limit requires team records |
| R06 Integration regression | No regression found in 23-test suite or browser smoke checks | Original views retained in automated suite; engine/UI kept modular | Future provider/library upgrades can regress behavior |
| R07 Cloud deployment | Clean local preparation passed; remote deployment not attempted | Requirements reviewed, unused runtime dependency removed, clean install plus 23 tests, secrets scan and local health/browser checks | Blocked on authorization; no public URL or cloud runtime evidence |
| R08 Provider deprecations | Warning occurred again during live downloads | Tested pins retained and warning documented | Future pandas/yfinance compatibility remains open |
| R09 Execution bias | Addressed for portfolio MVP | Signal at close t fills at next observed Close; open positions are marked | Closing-price attainability, spread and slippage are unmodeled |

R04 produced real design work but no failed accounting test. R07 is a blocked
external step rather than a claimed cloud failure.
