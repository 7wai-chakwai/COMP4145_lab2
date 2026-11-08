# Initial Project Update: Week 1

Stock Trading Analytics Platform | COMP4145 PD2 | Prepared 2026-10-26
Evidence-based implementation checkpoint; team activities and elapsed time are
not invented. Roles below are assigned responsibilities, not attendance records.

## 1. Executive Summary

Week 1 extended the existing Lab 2 application with Multi-Stock Comparison and a
basic Risk Analysis Dashboard while preserving MSFT Golden Cross charts,
statistics and trade records. Thirteen deterministic/integration tests passed;
live Yahoo data and local Streamlit startup were verified. Portfolio backtesting
is assessed, not implemented. Cloud deployment and final reporting remain W2.

## 2. Project Objectives

Help non-professional investors compare historical outcomes and understand risk.
Deliver a manageable two-week enhancement with transparent financial assumptions,
test evidence and project-management decisions suitable for a four-page report.

## 3. Planned Features And Priorities

Comparison and basic risk were prioritized because they provide immediate user
value through existing data/chart libraries with limited architectural change.
Portfolio backtesting is the technically challenging feature: reusable signals
do not solve causal execution, capital constraints, concurrent positions or
cost accounting. Advanced risk and automatic rebalancing are optional, not MVP.

## 4. Team Responsibilities

| Role | Assigned responsibility |
|---|---|
| M1 Project Manager / Business Analyst | Requirements, scope, sprint/risk tracking and stakeholder reporting |
| M2 Frontend Developer | Native Streamlit navigation, UI and comparison |
| M3 Data Analyst | Shared market data, financial assumptions and risk dashboard |
| M4 Backend Developer | Feasibility, execution/capital assumptions and W2 portfolio engine |
| M5 QA / DevOps | Git/environment, integration tests, dependency checks and W2 deployment |

## 5. Week 1 Accomplishments

Requirements, sprint/risk/decision records, UI diagram and preliminary feasibility
assessment are available. New analytics support 2-5 stocks, historical dates,
adjusted prices, normalization and return ranking, volatility and drawdown.
Data validation/caching and failure handling are shared. A recoverable Lab 2
archive was created before edits; original strategy and four application
functions were verified unchanged.

## 6. Current Project Status

T01,T02,T04,T05,T06,T07,T08,T11 meet their stated Week 1 deliverable gates.
T07 means basic metrics; T08 means preliminary assessment; T11 means verified
local environment, not remote push/cloud installation. T09/T12 are To Do;
T03/T10/T13 remain Backlog. Stakeholder review is not presumed complete.

All 13 automated tests passed. Live 2024 AAPL/MSFT/NVDA loading returned 252
shared sessions; MSFT five-year strategy returned four trade records. A deliberate
invalid ticker was isolated without losing valid data. Local browser charts and
HTTP health succeeded. These are observed checks, not long-term reliability guarantees.

## 7. Challenges And Risks

The first UI test run was blocked by a caller-relative AppTest path; this was
corrected and all tests rerun. A screenshot exposed close title/legend spacing
in a new chart; a local layout fix passed the regression suite and mobile
screenshot check. Yahoo's library emits non-blocking pandas
deprecation warnings. API availability, missing sessions, short-history risk
interpretation and clean/cloud dependency compatibility remain risks.
Backtesting has unresolved next-Open versus next-Close execution and terminal
position choices. The less-than-three-hour coding limit cannot be certified from
missing actual time records; a blank log is provided for real entries.

## 8. Management Decisions

The implementation follows conservative scope choices: extend rather than
replace Lab 2; complete two easy feature MVPs before the hard engine; use shared
adjusted-price validation and cache; normalize on common dates but calculate risk
on original observed sessions; use known-value tests rather than plausible live
numbers as proof of correctness. No rebalancing, new framework, unauthorized
push or fabricated cloud URL was introduced. These are documented choices,
not invented team meeting approvals.

## 9. Week 2 Action Plan

M1/M4 first resolve execution, costs and final-position assumptions. M4 implements
equal-initial-weight sleeves and a causal cash/position ledger; M3 reviews data
and calculations. M5 validates hand-calculated cases and reruns W1 regressions;
M2 integrates output. M5 then verifies a clean install and cloud deployment,
adding the real public URL. M1 records actual feedback, progress and reflection,
then compacts the final Word report to four pages. Incomplete gates remain visible
and optional scope is deferred if the real time budget is insufficient.