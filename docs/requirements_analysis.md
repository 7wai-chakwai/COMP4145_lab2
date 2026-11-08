# Requirements Analysis (T01)

Prepared: 2026-10-26. Owner: M1. Deliverable for stakeholder review, not a claim
that a stakeholder workshop or approval has taken place.

## 1. Project Background

Stock Trading Analytics Platform, COMP4145 PD2: two weeks, five members. The Lab 2
prototype is a working MSFT Golden Cross app with price charts, statistics and
detailed trade records. PD2 extends that app rather than replacing it.

## 2. Problem Statement

A single-stock, per-trade view does not help a non-professional investor compare
alternatives or judge historical losses. Portfolio results also cannot be inferred
by averaging independent trade returns without cash and position accounting.

## 3. Project Objectives

Deliver accessible, reproducible historical stock comparisons and core risk
metrics in Week 1; investigate and then build a constrained portfolio backtest in
Week 2. Preserve Lab 2 behavior, demonstrate risk-informed scope decisions and
provide evidence for a four-page final management report.

## 4. Target Users

Non-professional investors comparing historical performance and risk; academic
business/technical stakeholders evaluating requirements, delivery and management.
No professional execution or personalized suitability assessment is promised.

## 5. Functional Requirements

| ID | Requirement | Acceptance reference |
|---|---|---|
| FR01 | Preserve MSFT loader, Golden Cross, price/MA/buy/sell chart, statistics, trade filters and CSV | AC-LAB |
| FR02 | Navigate among strategy, comparison and risk in one application | AC-UI |
| FR03 | Select custom US stock symbols from one shared watchlist, default AAPL/MSFT/NVDA, and historical dates | AC-COMP, AC-WATCH |
| FR04 | Retrieve, validate and cache provider-adjusted daily prices; isolate ticker failures | AC-DATA |
| FR05 | Show interactive price and normalized charts, cumulative return and historical ranking | AC-COMP |
| FR06 | Show volatility, drawdown and return cards, comparative chart and drawdown chart | AC-RISK |
| FR07 | Document preliminary equal-weight portfolio feasibility without a Week 1 simulator | AC-FEAS |
| FR08 | Add/remove, clear, restore, normalize and persist up to the configured stock limit across comparison, risk and portfolio | AC-WATCH |

### Feature Selection

| Feature / priority | Business value, user requirement and expected outcome | Difficulty and risks | MVP / optional |
|---|---|---|---|
| Multi-Stock Comparison / Must, Week 1 | Compare alternatives on a fair shared historical window; identify historical relative performance, not future winners | Easy; API failure, unequal calendars, currency confusion | MVP: 2-5 stocks, dates, prices, index=100, endpoint return, ranking, errors/cache. Optional: benchmark, FX conversion, larger universe |
| Risk Analysis / Must, Week 1 | Understand fluctuations and peak-to-trough loss before judging returns; display three defined metrics and historical drawdown | Easy basic version; incorrect units, insufficient observations, irregular sessions | MVP: sample annualized volatility, maximum drawdown, cumulative return, charts/cards and known-result tests. Optional: Sharpe, VaR, portfolio risk |
| Portfolio Backtesting / Must MVP, Week 2 | Evaluate combined strategy outcomes with capital constraints rather than averaging trades | Hard; execution timing, cash ledger, calendar alignment, costs and bias | Week 1: feasibility only. Week 2 MVP: equal initial sleeves, cash/positions, causal orders, costs, equity/trades. Optional: automatic rebalancing, optimization |
| Custom Stock Selection and Watchlist / Medium, Week 2 enhancement | Let users analyze preferred US-listed equities without maintaining three inconsistent lists | Medium; provider existence/classification, rate limits, state synchronization and variable-count performance | MVP: shared state, manual symbols, add/remove/clear/restore, configurable default limit 20, provider errors and regression tests |

The two easy features reuse the existing provider and chart libraries and deliver
visible user value early. The hard feature was selected for a meaningful
simulation challenge and technical evaluation, not to manufacture failure.

## 6. Non-Functional Requirements

| ID | Requirement / verification |
|---|---|
| NFR01 | Modular Python/Streamlit, reuse existing components, no new frontend/database/auth framework |
| NFR02 | Deterministic financial tests; metrics in percent with definitions and coverage |
| NFR03 | Invalid input/API failure must show actionable messages without uncaught UI errors |
| NFR04 | One-hour cached analytics requests; navigating with unchanged inputs reuses the cache |
| NFR05 | No credentials in source; ignore virtualenv, local backup and secrets |
| NFR06 | Local Python environment/dependencies/startup verified; cloud verification deferred |
| NFR07 | Less than 180 minutes total vibe coding, recorded using real times, not estimates presented as actuals |
| NFR08 | Native responsive charts/controls, readable labels, no misleading prediction claims |
| NFR09 | One shared ticker state; default configurable maximum 20; warn above 10; reuse one-hour cached loaders |

## 7. Feature Prioritization

Must: Lab 2 regression safety, data validation, comparison, basic risk, planning
evidence. Must Week 2: portfolio MVP and validation. Should: deployment and final
stakeholder update. Could: advanced metrics and rebalancing only after core gates.
T03 stakeholder sign-off is a separate team-owned follow-up, not implicit approval.
T14 is a Medium-priority Week 2 enhancement and does not alter historical board snapshots.

## 8. Acceptance Criteria

- **AC-LAB:** moving averages and real Golden Cross tested; 15% exit and holding
  limit preserved; all three existing UI views and CSV control accessible.
- **AC-UI:** four sections in one entry point; one stock watchlist is reused by
  comparison/risk/portfolio; charts, metric labels, spinner and error states available.
- **AC-DATA:** real AAPL/MSFT/NVDA histories load; date indexes sorted and
  timezone-free; adjusted Close explicitly defined; missing/invalid values,
  duplicates and short history rejected; no future-price filling; ticker errors isolated.
- **AC-COMP:** three valid stocks display; first shared values equal 100;
  cumulative return equals last/first minus one; ranking uses the same window;
  changing tickers refreshes results; invalid inputs do not crash.
- **AC-RISK:** daily-return sample standard deviation x sqrt(252), peak-based
  maximum drawdown and endpoint return match deterministic expected values;
  selection updates cards/data; short history produces an error.
- **AC-FEAS:** architecture, alignment, allocation, cash, signals, costs, biases,
  rebalancing decision, dependencies and unresolved questions documented.
- **AC-PORT (Week 2, unverified):** no negative cash or duplicate sleeve position;
  signal available before fill; equity=cash+marked positions; costs deducted
  once per fill; all-cash/one-stock/two-stock fixtures reconcile; reported return
  derives from equity, not mean trade returns.
- **AC-WATCH:** manual symbols normalize to uppercase and deduplicate; empty,
  malformed, unavailable, unsupported and over-limit selections show clear
  messages; add/remove/clear/restore persist across reruns; more than five and
  limit-sized selections validate; all three analytical pages use the same state.

## 9. Project Scope

Week 1 includes two functional easy features, shared data functions, Lab 2
regression tests, a preliminary feasibility study and management records. Week 2
adds a minimal portfolio engine, integration/validation, deployment and reporting.
Done indicates observed artifact/test evidence, not stakeholder sign-off.

## 10. Out-Of-Scope Features

Real-time trading, brokerage integration, account authentication, databases,
investment recommendations, predictive AI, optimization, short selling,
leverage and automatic rebalancing. Cloud delivery and portfolio implementation
are not Week 1 accomplishments.
