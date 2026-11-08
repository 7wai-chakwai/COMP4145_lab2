# End Of Week 1 Scrum Board (Actual Implementation Checkpoint)

Evidence checkpoint: 2026-10-26, based on current artifacts and executed checks.
This is not a claim that a calendar week elapsed or that members signed off.
Done scope is the Week 1 deliverable, not the entire project or optional features.

| Backlog | To Do | In Progress | Blocked | Done |
|---|---|---|---|---|
| T03 M1: Stakeholder review | T09 M4: Portfolio MVP | None | None currently | T01 M1: Requirements |
| T10 M5: Validation/integration | T12 M5: Deployment | | | T02 M1: Sprint/risk records |
| T13 M1: Final report/reflection | | | | T04 M2: UI/navigation |
| | | | | T05 M2: Comparison |
| | | | | T06 M3: Data processing |
| | | | | T07 M3: Basic risk MVP |
| | | | | T08 M4: Preliminary feasibility |
| | | | | T11 M5: Git/local environment |

## Completion Evidence

| Task | Actual status | Evidence / boundary |
|---|---|---|
| T01 | Done | requirements_analysis.md, ten sections and feature acceptance criteria; external approval not claimed |
| T02 | Done | sprint_plan.md, risk_register.md, issues_and_decisions.md with owners/dependencies and real issues |
| T04 | Done | Same app, three navigation sections; architecture/UI diagram; original UI regressions pass |
| T05 | Done | Three live stock histories, two comparison charts, known-result normalization/returns, selection/cache/error tests |
| T06 | Done | market_data.py, date/ticker/index/price validation and partial/all failure tests; no filling |
| T07 | Done (basic W1 scope) | Volatility/drawdown/return cards/charts; deterministic formulas and focus-selection tests; advanced risk deferred |
| T08 | Done (preliminary study only) | backtesting_feasibility.md addresses allocation/calendar/cash/signals/costs/bias/rebalancing; no portfolio implementation claimed |
| T11 | Done (local scope) | Existing Git origin inspected; recovery archive; reviewed/pinned dependencies; pip check; launch/health; no push/clean/cloud install claimed |

## Week 1 Progress Summary

- Planned: eight tasks T01,T02,T04,T05,T06,T07,T08,T11. Completed: all eight
  within their stated Week 1 scope; 13 reproducible tests passed and live checks
  succeeded. This does not assert actual team work durations.
- Incomplete project work: T03 stakeholder review, T09 portfolio engine, T10
  portfolio validation/broader integration, T12 cloud deployment, T13 final
  update/board/reflection/Word report. These are planned later work, not hidden failures.
- Blockers: none for the verified W1 functionality. Actual time-budget
  compliance cannot be verified until the team supplies real log entries.
- Issues: I01 test-path setup and I03 chart-title spacing fixed and suite rerun;
  I02 library deprecations remain a non-blocking maintenance concern.
- Risks: Yahoo availability, provider missing sessions, short histories,
  portfolio accounting/execution bias, time budget and cloud compatibility.
- Actions/decisions: preserved baseline, easy MVPs first, strict adjusted-price
  assumptions, shared cache, expected-value tests, W2 ledger/rebalancing scope split.

No Scrum PNG exporter existed, so Markdown is the board artifact. Retain this
snapshot and the planned baseline unchanged; record actual W2 progress in the
separate W2 submission template, rather than rewriting history.