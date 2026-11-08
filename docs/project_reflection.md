# Project Reflection

The feature priorities were appropriate. Comparison and risk reused the original
data and charting stack, so Week 1 could deliver visible value while exposing the
data-quality assumptions needed for Week 2. Deferring the portfolio engine until
after a feasibility study prevented the existing independent-trade output from
being mislabeled as portfolio performance.

The two-week plan worked best when acceptance gates were concrete. Known-value
fixtures, explicit price units, and preserved snapshots made progress measurable.
The hard feature was more complex than a moving-average loop because execution
timing, simultaneous signals, cash limits, costs, missing sessions, terminal
positions, and benchmark fairness interact. Treating each stock as an independent
cash sleeve kept the MVP understandable and prevented leverage. This scope choice
also deferred automatic rebalancing, which would add orders and costs that are not
required by the user story.

Some work did not proceed as expected. The local Git client became unavailable
through a missing Apple Command Line Tools path, so a separate checksum-verified
archive replaced the intended Week 2 Git baseline. The VS Code task surfaced
stale output from an earlier run, and the active server had to be verified through
the listener, browser, and health page. These issues did not change application
behavior, but they show why environment readiness and evidence sources should be
checked at each sprint boundary.

Risk management was effective where mitigations were executable: provider
failures are isolated, invalid data is rejected, prices are never fabricated,
portfolio invariants run during simulation, and all original views remain in the
regression suite. Remaining exposure is clear. Yahoo availability and adjustment
history can change; adjusted Close is not a broker quote; cloud compatibility is
not proven; and no public URL exists without authorized deployment.

AI assistance accelerated module scaffolding, test construction, UI integration,
and documentation updates. Its output still required human-oriented validation:
the accounting rules had to be chosen explicitly, expected results were calculated
independently, live values were separated from correctness proof, and rendered
interfaces and documents were inspected. Future planning should reserve time for
environment repair, stakeholder review, and deployment authorization instead of
assuming those external dependencies will be available at the end.

Individual team experiences and actual development hours remain for the team to
add. The blank time log does not prove compliance with the course's 180-minute
limit, so this reflection makes no claim about that limit.
