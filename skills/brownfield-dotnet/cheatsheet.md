# Cheatsheet — Brownfield Application Development in .NET

## Decision rules

| When… | Do… | Because… |
|---|---|---|
| Inheriting a project | Confirm 3 components: existing code, actively worked, salvageable | If not actively worked → it's *legacy*, treat differently |
| Someone asks "should we rewrite?" | Default **No**; decide on business value, not emotion | Refactoring usually beats rewrite (Spolsky); rewrite only if architecture is fundamentally wrong (e.g. sync vs async) |
| You hit the same boilerplate 3× | Trigger "hack alert" → extract/abstract it | Repetition signals a pain point or design flaw |
| Selling change to management | Frame in **cash dollars + risk**, propose a time-boxed PoC | Managers buy value/insurance, not "clean code" |
| Facing technical debt | Time-box paydown each cycle | "Big push" halts features and rarely finishes |
| Tempted to refactor many things | Pick **one**, finish it | Half-done refactorings add debt + inconsistency |
| Fixing a bug in untested code | Write failing characterization test first | Locks behavior, proves the fix, leaves a guard |
| Build breaks under CI | Stop everything, fix the build first | A red build blocks the whole team's feedback loop |
| Integrating external/legacy system | Wrap behind an Anti-Corruption Layer | Keeps their model out of your domain; isolates change |
| Code-behind has logic | Extract a Presenter (MVP) | Makes UI logic unit-testable |
| Choosing where to refactor first | High cyclomatic complexity ∩ low coverage | Highest defect risk, highest payoff |

## Brownfield vs Greenfield vs Legacy
- **Greenfield**: no history, all code active, review always.
- **Brownfield**: mixed new+old, both new dev and maintenance, review on big changes, salvageable. ← *this book*
- **Legacy**: maintenance only, rarely reviewed, "dealt with". (Feathers: code without tests.)

## The Scale (replaces Iron Triangle)
Left (keep low): **time & resources** — Right (keep high): **quality & features**. Must stay balanced. Add a feature → add time/resources, or cut quality/scope. Dev team influences all **except cost**.

## Order of attack (book's sequence)
**Part 1 — Ecosystem first**: VC (2) → CI (3) → Automated tests (4) → Metrics (5) → Defect tracking (6).
**Part 2 — Then the code**: OO/SOLID (7) → Re-layer (8) → IoC/DI (9) → UI/MVP (10) → Data access/ORM (11) → External integration (12) → Sustain (13).
Adapt the order to *your* biggest pain points — the sequence is a default, not a mandate.

## SOLID / OO principles (Ch 7)
- **SRP** — one reason to change.
- **OCP** — open for extension, closed for modification.
- **DIP** — depend on abstractions.
- **LoD** — talk only to immediate friends.
- Prefer **composition over inheritance**. Keep it **KISS / YAGNI / DRY**.

## IoC vocabulary (keep distinct — Ch 9)
IoC (principle) ⊃ DIP (the means) ⊃ DI (the implementation) → IoC container (the tool). Service locator ≠ DI (usually avoid). Incremental path: interfaces → invert → poor man's DI → container.

## MVC vs MVP (Ch 10)
| | Entry point | View | Best for |
|---|---|---|---|
| MVC | Controller | renders model | web request/response |
| MVP — Passive View | View | fully dumb | max testability |
| MVP — Supervising Controller | View | does simple binding | less ceremony |

## Data access choices (Ch 11)
| | Effort | Flexibility | Risk |
|---|---|---|---|
| Hand-rolled | High | Full control | SQL injection, boilerplate |
| Generated | Low | Medium | tied to generator |
| ORM (NHibernate) | Medium setup | High | learning curve |
Always front with a **Repository** + inject it.

## Metrics: thresholds the authors commit to (Ch 5)
- Coverage: aim high but **75%–100% is a diagnostic, not a target**; don't fail builds on it.
- Cyclomatic complexity: prefer ~3–4; ~7+ is a smell.
- Instability I = Ce/(Ca+Ce), 0=stable…1=unstable; Abstractness 0–1. Watch the **delta over time**, not the absolute.
- DIT (depth of inheritance): deeper = more complex.

## Defect tracking (Ch 6)
**Zero Defect Count** — clear backlog, fix new defects immediately. Write defects with the **5 C's**: Concise, Clear, Complete, Constructive, Closed. Defect-vs-feature dispute → let the business prioritize it against everything else.

## Recommended .NET tooling (Ch 13 appendix)
- **Tests**: NUnit, MbUnit, RhinoMocks, Moq, SQLite
- **CI/build**: CruiseControl.NET, TeamCity, NAnt (+ NAnt Contrib)
- **Metrics**: NCover, NDepend, Simian
- **Data**: NHibernate, Fluent NHibernate, NH Prof, AutoMapper
- **IoC**: Castle Windsor, StructureMap, Autofac
- **UI**: Castle MonoRail, ASP.NET MVC

## Tells & smells
- People say "I/my" not "we/our" → fractured team ownership (HPS risk).
- One dev pulling heroic hours → discourage; reward the team.
- "Shelf life is short" / "it's simple" → don't buy it; apps outlive estimates and grow complex.
- Long build, flaky web-service-in-tests → friction; automate or isolate.
- New `SomeClass()` scattered inline → coupling; candidate for DI.
