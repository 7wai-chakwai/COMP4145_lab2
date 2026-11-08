# Issues And Decisions (T02)

Evidence date: 2026-10-26. Responsible Member means assigned follow-up owner;
it does not assert that the member performed the action or attended a meeting.

## Observed Issues

| Issue ID | Date | Description | Impact | Root Cause | Responsible Member | Action Taken | Management Decision | Resolution Status |
|---|---|---|---|---|---|---|---|---|
| I01 | 2026-10-26 | First UI suite: three AppTest setup errors looking for tests/app.py | UI validation initially blocked, not a production failure | Streamlit resolves relative file paths from the caller test file | M5 | Changed AppTest path to ../app.py; reran identical suite | Correct test harness and retain full regression gate | Resolved; all 13 tests passed |
| I02 | 2026-10-26 | yfinance emits pandas inplace deprecation warnings during real downloads | Non-blocking maintenance risk; future dependency upgrades may break | Installed yfinance uses pandas operations scheduled for removal | M5 | Observed successful downloads, recorded warnings, pinned tested direct dependencies | Avoid unrelated dependency rewrites; review compatibility in W2 clean install | Open; no runtime failure observed |
| I03 | 2026-10-26 | Desktop screenshot showed drawdown title too close to the legend | Reduced chart readability | New line-chart title and legend occupied adjacent top-margin space | M2 | Increased top margin and assigned separate title/legend positions; reran all 13 tests and inspected mobile chart screenshot | Keep the correction local to new charts; preserve legacy chart styling | Resolved; readable title/legend and all tests passed |

Yahoo 404 for a deliberately invalid symbol and simulated timeout fixtures were
expected test inputs, not fabricated project outages. The notebook's optional
IPython dependency is unresolved; notebook execution is outside the running app.
No API reliability incident or cloud failure was observed or claimed.

## Decisions Applied In This Implementation

These record implementation choices, not invented team approvals.

| Decision | Date | Assigned owner | Choice and rationale | Follow-up |
|---|---|---|---|---|
| D01 | 2026-10-26 | M1/M2 | Extend the same entry point; preserve strategy and four original UI functions to minimize regression risk | Keep baseline and original tests during W2 |
| D02 | 2026-10-26 | M3 | Add a date-aware loader using existing Yahoo provider because legacy period-only loader lacks requested dates; explicitly use adjusted Close | Retain strict validation; review provider coverage assumptions |
| D03 | 2026-10-26 | M3 | Normalize/rank on common observed dates; risk uses each stock's own sessions so calendar intersection does not create multi-session daily-return samples | Show coverage and document differences/no FX conversion |
| D04 | 2026-10-26 | M1/M4 | Deliver easy-feature MVPs first; portfolio work is assessment only in W1, no rebalancing or advanced risk scope | Resolve execution/accounting assumptions before T09 |
| D05 | 2026-10-26 | M5 | Preserve original dependencies; pin tested installed direct versions without adding packages | Clean installation and cloud verification in T12 |
| D06 | 2026-10-26 | M1 | Base Done statuses on actual artifacts/tests; leave time log/public deployment URL unfilled | Obtain real time records and real W2 evidence |

## New Issue Template

| Issue ID | Date | Description | Impact | Root Cause | Responsible Member | Action Taken | Management Decision | Resolution Status |
|---|---|---|---|---|---|---|---|---|
| TBD | Actual date | Observed evidence only | Actual impact | Unknown until investigated | M1-M5 | Actual action or pending | Actual decision or pending | Open / In Progress / Blocked / Resolved |

Do not copy risks into this table as if they have occurred. Record real evidence,
separate root-cause hypotheses from verified facts, and attach the retest result.

## Week 2 Observed Issues

| Issue ID | Date | Description | Impact | Root Cause | Responsible Member | Action Taken | Management Decision | Resolution Status |
|---|---|---|---|---|---|---|---|---|
| I04 | 2026-10-29 | Git commands fail with `invalid active developer path` | Current Git status/commit unavailable | Local Apple Command Line Tools path is missing | M5 | Created checksum-verified Week 1 archive before edits; avoided destructive Git commands | Continue local implementation and disclose version-control limitation | Open environment issue |
| I05 | 2026-10-29 | VS Code task returned earlier output while port 8501 was already occupied | Initial startup evidence was ambiguous | Existing Streamlit listener and retained task output | M5 | Inspected listener; verified current app and health through browser | Use live browser state as startup evidence | Resolved for QA |
| I06 | 2026-10-29 | Dollar signs in portfolio caption were treated as markup | Accessibility tree lost clear currency text | Dollar-delimited Streamlit markdown parsing | M2 | Replaced caption symbols with explicit USD labels | Keep currency text unambiguous | Resolved |

## Week 2 Decisions

| Decision | Date | Assigned owner | Choice and rationale | Result |
|---|---|---|---|---|
| D07 | 2026-10-29 | M4 | Use independent equal-capital sleeves; unused cash stays with its stock | Simultaneous signals cannot overspend shared cash; no leverage or silent redistribution |
| D08 | 2026-10-29 | M4 | Signal on adjusted Close t and fill at the next observed adjusted Close | Prevents same-close look-ahead with the available price field |
| D09 | 2026-10-29 | M3/M4 | Use union session calendar and carry the last price only for valuation | Different calendars produce a continuous portfolio value without fabricated trade signals |
| D10 | 2026-10-29 | M4 | Mark terminal positions instead of forcing liquidation | Avoids invented sell trades and costs at the reporting boundary |
| D11 | 2026-10-29 | M1/M5 | Stop a simulation if any selected ticker fails; block remote deployment without authorization | Preserves the intended universe and keeps deployment reporting factual |
