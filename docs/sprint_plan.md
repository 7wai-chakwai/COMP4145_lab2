# Sprint Plan (T02)

Prepared: 2026-10-26. Two one-week sprints; owners are assigned responsibilities,
not claims about who performed work. Priorities: P1 core, P2 follow-up, P3 optional.

| Task | Deliverable | Owner | Sprint / priority | Dependencies | Acceptance / gate |
|---|---|---|---|---|---|
| T01 | Requirements and acceptance criteria | M1 | W1 / P1 | Lab 2 inspection | Ten required analysis sections; testable MVP scope |
| T02 | Sprint, risk, issue and decision records | M1 | W1 / P1 | T01 | Owners, priorities, dependencies, R01-R07 and factual logs |
| T03 | Final project update and reflection | M1 | W2 / P2 | T01,T02,T09,T10,T12 | Evidence-based final update, reflection and report; missing feedback/time remains explicit |
| T04 | UI structure and navigation | M2 | W1 / P1 | T01 | Diagram and three sections; original views preserved |
| T05 | Multi-Stock Comparison | M2 | W1 / P1 | T04,T06,T11 | AC-COMP, three live stocks, normalization and UI tests |
| T06 | Market-data processing | M3 | W1 / P1 | T01,T11 | AC-DATA, explicit prices, validated indexes and isolated failures |
| T07 | Basic Risk Analysis Dashboard | M3 | W1 / P1 | T04,T06 | AC-RISK, known-result calculation and UI tests |
| T08 | Preliminary backtesting feasibility | M4 | W1 / P1 | Lab 2 logic,T01,T06 | AC-FEAS; assumptions/uncertainties, no full simulator |
| T09 | Portfolio backtesting MVP | M4 | W2 / P1 | T08,T06,T11 | AC-PORT; causal signals, equal sleeves, ledger/costs/equity |
| T10 | Backtesting validation and limitations | M4 | W2 / P1 | T09,T06 | Hand-calculated fixtures, accounting invariants and documented limitations |
| T11 | Git and local environment setup | M5 | W1 / P1 | Existing repository | Recovery baseline, reviewed requirements, pip check, local startup/tests |
| T12 | Integration testing and bug tracking | M5 | W2 / P1 | T05,T07,T09,T10 | Full regression, startup/browser checks and factual issue resolutions |
| T13 | Streamlit Cloud deployment | M5 | W2 / P2 | T09,T10,T12 | Local readiness plus authorized cloud smoke test and actual public URL |
| T14 | Custom Stock Selection and Watchlist | M2, support M3 | W2 enhancement / Medium | T05,T06,T07,T09 | Shared custom selector, configurable limit, provider validation, persistence and regression tests |

## Week 1 Delivery Sequence

Inspect/recover Lab 2 -> establish requirements/local environment -> data
functions and deterministic tests -> navigation/comparison/risk -> regression
and live-data checks -> feasibility and evidence-based project update.
M2 and M3 own the easier feature surfaces; M4 focuses on simulation risks;
M1 maintains scope/progress and M5 owns verification/deployment readiness.

## Week 2 Delivery Sequence

M1/M4 resolve execution price, terminal-position treatment and cost assumptions
before T09. M4 adds an isolated daily ledger reusing the crossover concept, not
the independent-trade aggregator. M4 validates known results and limitations;
M5 runs integration and bug tracking while M2 supports presentation and M3
reviews returns and price basis. Deployment remains conditional on authorization;
M1 compacts actual management evidence into the final report.

## Definition Of Done And Scope Control

An artifact exists, its stated acceptance checks were executed (where applicable),
and limitations are recorded. Documentation completion is not external approval.
No planned target is treated as actual completion. Blocked tasks retain their
status and named next action. Week 1 T07 means the **basic** metric scope only.

No actual duration or team meeting is recorded. Use the blank real-time log and
keep total vibe coding strictly below 180 minutes. If the real remaining budget
is insufficient, remove optional features first and disclose any unmet MVP gate;
do not weaken financial correctness to make a task appear Done.

## Week 2 Mapping Correction

The detailed Week 2 brief assigns T03 to final updates and reflection, T10 to
backtesting validation, T12 to integration, and T13 to cloud deployment. The
Week 1 snapshots are preserved as written even though their provisional labels
used a different T12/T13 mapping. The End of Week 2 board uses the authoritative
Week 2 ownership list rather than rewriting historical snapshots.

## Post Snapshot Enhancement T14

T14 was added after the recorded End of Week 2 checkpoint. It is tracked in a
separate implementation record so the Before Week 1, End of Week 1, and End of
Week 2 snapshots remain historical evidence rather than being rewritten.
