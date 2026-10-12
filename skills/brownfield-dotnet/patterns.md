# Patterns & Techniques — Brownfield Application Development in .NET

## The Check-In Dance
**When to use**: Every commit, especially on a team without CI discipline.
**How**: Get latest → merge/resolve → full local build → run tests → only then commit. With CI (Ch 3), the build server re-runs the same steps to confirm.
**Trade-offs**: Adds seconds per commit; eliminates "works on my machine" and broken-build churn.

## Time-Boxed Technical Debt Paydown
**When to use**: Whenever an app carries a technical-debt backlog (always, in brownfield).
**How**: Allocate fixed time (e.g. ½ day/week, one person) each cycle to debt. Limited by *time*, not by task count — stop when time's up.
**Trade-offs**: Slow but steady; avoids the risky "big push" that halts feature work.

## Proof-of-Concept / Time-Boxed Trial
**When to use**: Selling a risky change (new ORM, IoC, layering) to skeptical management.
**How**: Isolate a small, controlled slice. Prove value with concrete results in cash/risk terms. Stay objective — be willing to conclude it failed.
**Trade-offs**: Limited scope may not surface integration issues; but contains downside.

## Continuous Integration Pipeline
**When to use**: Any team with more than one developer.
**How**: VCS trigger → automated build (NAnt/MSBuild) → run unit tests (NUnit) → report. Split fast (unit) from slow (integration) builds. Broken build = top priority, stop and fix.
**Trade-offs**: Setup cost; pays back via short feedback loop and the "metronome" rhythm.

## Test-Before-Fix (Characterization)
**When to use**: Fixing a defect in untested legacy code.
**How**: Write a failing test that reproduces the defect first, then fix until green. Leaves a regression guard behind.
**Trade-offs**: Slower per fix; builds a safety net and proves the fix.

## Interface-Based Design + Seams
**When to use**: Breaking dependencies to isolate layers or get code under test.
**How**: Extract an interface at the dependency boundary (a seam); depend on the abstraction; substitute real/fake implementations.
**Trade-offs**: More types; enables testing, layering, and IoC.

## Dependency Inversion → Injection → Container (incremental)
**When to use**: Taming a tightly-coupled brownfield codebase, one step at a time.
**How**: (1) extract interfaces, (2) invert dependencies (depend on abstractions), (3) inject via constructor (poor man's DI first), (4) introduce an IoC container once injection is pervasive.
**Trade-offs**: Each step is independently shippable; avoid big-bang container adoption.

## Anti-Corruption Layer (Adapter/Façade)
**When to use**: Integrating a legacy module, third-party API, or external service (web service, Excel interop).
**How**: Wrap the foreign interface behind your own interface (Adapter/Façade); translate its model into yours (DTOs). Call only your wrapper from the rest of the code.
**Trade-offs**: Extra indirection; isolates you from external change and keeps the foreign model out of your domain.

## Layering by Whittling (one screen at a time)
**When to use**: Re-layering a tangled app without a stop-the-world rewrite.
**How**: Pick one screen/feature; pull its logic out of the UI into domain/data layers behind interfaces; repeat. Use tests to lock behavior.
**Trade-offs**: Incremental, low-risk; app stays shippable throughout.

## Presenter Extraction (MVP)
**When to use**: ASP.NET/WinForms code-behind stuffed with logic.
**How**: Define a view interface, move logic into a Presenter that talks to the interface. Passive View (dumb view) for max testability; Supervising Controller when simple binding is fine.
**Trade-offs**: More classes; makes UI logic unit-testable and decoupled.

## Repository over Data Access
**When to use**: Replacing scattered hand-rolled SQL/ADO.NET.
**How**: Define `IRepository<T>`/specific repository interfaces; back them with an ORM (NHibernate) or generated/hand-rolled implementation. Inject repositories.
**Trade-offs**: Abstraction cost; testable, swappable, SQL-injection-resistant data access.

## Metric-Driven Hotspot Finding
**When to use**: Deciding where to refactor first in a large unfamiliar codebase.
**How**: Run coverage + cyclomatic complexity + class coupling (the "Three CC's"). Track *deltas* over time, not absolute targets. High-complexity + low-coverage = top refactor candidate.
**Trade-offs**: Metrics mislead if treated as goals; use as a compass, never a quota or build-failer.

## Zero Defect Count
**When to use**: A team drowning in a defect backlog.
**How**: Clear the backlog, then fix new defects immediately so the open count stays ~0. Make it a cultural norm. Write defects with the 5 C's: Concise, Clear, Complete, Constructive, Closed.
**Trade-offs**: Upfront effort to drain backlog; high quality becomes self-sustaining.
