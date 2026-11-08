# Feature 4 Custom US Stock Selection and Watchlist

Implemented: 2026-11-04. Scrum task: **T14**. Assigned owner: **M2** with **M3**
support. Priority: **Medium**. Scope: **Week 2 enhancement**. This record does not
change the three earlier Scrum snapshots.

## Outcome

T14 is **Done for implemented and tested scope**. One Streamlit session-state
watchlist now supplies Multi-Stock Comparison, Risk Analysis, and Portfolio
Backtesting. The suggestion list is not an allowlist. Users can enter other
symbols, remove chips, clear the selection, or restore AAPL/MSFT/NVDA defaults.

The default limit is 20 and is configured centrally through
`PD2_MAX_SELECTED_STOCKS`. Comparison needs at least two usable stocks; risk and
portfolio support one or more. Portfolio capital remains equal-weight at `1/N`.
Selections above 10 display a rate-limit/performance warning. Existing one-hour
caches remain in place; portfolio still requests additional MA warm-up history.

## Validation and Provider Policy

Symbols are uppercased, deduplicated and checked against a US-stock format before
download. A syntactically valid symbol must still return usable Yahoo history.
When Yahoo provides instrument metadata, non-equities and non-USD instruments
are rejected. Metadata can be incomplete, so the application cannot independently
certify every listing as US-based. Comparison/risk can continue with successfully
loaded symbols while showing per-symbol warnings. Portfolio keeps its stricter
policy and stops if any selected symbol fails, preserving the intended universe.

## Executed Tests

The final suite contains **31 tests, all passing**. Eight T14 tests cover custom
valid symbols, lowercase normalization, duplicate removal, unavailable symbols,
provider instrument/currency rejection in both validation and loading, empty and malformed input, the configured
20-stock boundary, add/remove/clear/restore behavior, six-stock shared state across
all three features, and exact six-stock `1/N` portfolio allocation. The original
23 tests also passed without changes to the Lab 2 strategy behavior.

A live smoke check loaded 61 adjusted-price rows for JPM and rejected SPY with
Yahoo's `ETF` classification. The recurring yfinance/pandas deprecation warning
remained non-blocking.

## Remaining Limitations

Yahoo availability and metadata quality are external. Up to 20 sequential
symbol requests can be slower or rate-limited, especially on a cold cache.
Suggestions cover common US companies but are not a complete exchange directory.
The watchlist persists within the current Streamlit session, not across browsers,
devices, server restarts or authenticated user accounts.
