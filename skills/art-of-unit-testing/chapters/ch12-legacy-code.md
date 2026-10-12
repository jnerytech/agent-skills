# Chapter 12: Working with legacy code

## Core Idea
Legacy code is code without tests. You can't safely refactor it (no tests to catch regressions), and you can't easily test it (no seams to break dependencies) — a chicken-and-egg trap. This chapter is deliberately short and practical: it answers the **two problems of legacy** — *where to start adding tests* and *how to break dependencies safely* — by prioritizing components on logic-complexity vs dependency level, choosing an easy-first or hard-first strategy based on team experience, and using integration tests as a safety net around refactoring. It does not re-teach dependency-breaking mechanics; it points you to Feathers for that.

## Frameworks Introduced
- **Test-feasibility table (component prioritization)**: formulation — score each component on *logical complexity* (cyclomatic: nested ifs, switches, recursion), *dependency level* (how many deps to break to get it under test), and *priority* (importance in the project), each 1–10. When — before writing a single legacy test, to build a ranked work list instead of flailing. How — fill the table, plot logic (value) vs dependencies, and drop anything below a logic threshold of ~2–3 (data-holders aren't worth testing). Why — focuses effort where tests deliver value, and makes the easy-vs-hard tradeoff explicit and visible to the team.
- **Integration tests as a refactoring safety net**: formulation — wrap untested production behavior in coarse integration tests (no mocks/stubs) *before* you touch the code. When — refactoring legacy for testability, or adding a feature to code you can't yet unit-test (e.g. C++ with no isolation tooling). How — (1) write integration tests proving the system currently works, (2) add a failing test for the new feature, (3) change in small chunks, running the integration tests constantly. Why — they pin existing behavior cheaply without needing to understand internal structure or injection points; later, replace most with smaller unit tests.

## Key Concepts
1. **Legacy code = code without tests.** Age and language don't define it — absence of a test harness does.
2. **The two problems of legacy.** Where to start adding tests (prioritization) + how to break dependencies safely (mechanics/seams). This chapter owns the first; Feathers owns the second.
3. **Seams.** Places in code where you can substitute or extend a component without editing it in place. Legacy code is hard precisely because it was written without seams.
4. **Logical complexity (cyclomatic complexity).** Amount of branching logic. High logic = high value to test (more ways to be wrong). Tools can measure it automatically.
5. **Dependency level.** Number of dependencies you must break to get a class into a test harness — calls to email components, static log methods, file/disk access, etc. High deps = hard to test.
6. **Test-feasibility table.** The scoring artifact (logic × deps × priority) that turns "where do I start?" into a sortable list.
7. **Logic threshold.** Ignore components below ~2–3 logic — data holders (`Person`) and thin config wrappers give little testing value regardless of deps.
8. **Easy-first strategy.** Start with low-dependency components. Fast early wins, but the hardest components pile up at the end of the cycle when everyone is stressed.
9. **Hard-first strategy.** Start with the most-coupled components. Slow first (a day for the simplest test), but refactoring a high-dep component often fixes testability for its dependencies too — so total effort *declines* over time.
10. **Tooling matters.** Lack of isolation tooling (e.g. C++) can force integration tests over unit tests; cyclomatic-complexity analyzers and tools like CodeScene surface hidden technical debt.

## Mental Models
- **Value lives in the top-left, pain lives in the top-right.** Plot logic (value) on one axis, dependencies (difficulty) on the other. Top-left = high logic, low deps = test first, always. Top-right = high logic, high deps = the real decision point. Bottom = low logic = ignore.
- **The cost curves cross.** Easy-first: per-test cost slowly *rises* over the project (you save the monsters for last). Hard-first: per-test cost sharply *falls* (each tamed monster unlocks its dependencies). Pick the curve your team can survive.
- **Match strategy to team experience, not to ambition.** Hard-first only works if the team already knows isolation/mocking techniques. A green team that starts hard-first will stall.
- **Grow the system where you're already working.** Don't try to test everything. Add tests to the parts you must change; leave other bridges for when you reach them.

## Reference Tables

Component-prioritization (test-feasibility) matrix — score 1 (low) to 10 (high). Ignore rows below the logic threshold (~2–3).

| Component | Logical complexity | Dependency level | Priority | Decision |
|---|---|---|---|---|
| Utils | 6 | 1 | 5 | **Test first** — high logic, low deps. Easy + high value (top-left). |
| Person | 2 | 1 | 1 | **Ignore** — data holder, almost no logic. Little value. |
| TextParser | 8 | 4 | 6 | **High value, hard** — lots of logic + deps + high project priority (top-right). The real decision. |
| ConfigManager | 1 | 6 | 1 | **Ignore** — thin logic, reads files from disk. High cost, low value. |

After filtering, only `Utils` (easy/valuable) and `TextParser` (hard/valuable) survive — the strategy choice is between exactly those two.

## Worked Example
You inherit a billing module with four classes and no tests. You build the test-feasibility table above. First filter: drop everything under logic 3 — `Person` (data holder) and `ConfigManager` (thin config wrapper) fall out despite ConfigManager's six dependencies; testing them buys almost nothing. Two candidates remain:

- **`Utils`** — logic 6, deps 1. Top-left: easy to test, lots of value.
- **`TextParser`** — logic 8, deps 4, priority 6. Top-right: high value but expensive (4 dependencies to break).

Your team is new to unit testing. **Decision: easy-first.** Start with `Utils` — quick wins build confidence and technique, and you cap yourself at components with ≤4 dependencies for now, deferring `TextParser`. Had the team been experienced, hard-first on `TextParser` would pay off: breaking its 4 dependencies likely makes its collaborators testable too, collapsing future cost.

When you do reach `TextParser`, you can't unit-test it yet. So you wrap its current save/load behavior in integration tests (real system, no mocks) to lock in working behavior, add a failing test for the new attribute you must support, then change in small chunks running the integration suite constantly. Green across the board = nothing broken. Over months, replace those integration tests with maintainable unit tests as seams appear.

## Key Takeaways
1. **Map before you test.** Score every component on logic, dependencies, and priority — don't start tests by gut feel.
2. **Drop low-logic components.** Data holders and thin wrappers aren't worth testing even when heavily depended-on.
3. **Easy-first for green teams; hard-first for experienced ones.** The strategy must match the team's isolation skills.
4. **Hard-first's payoff is the declining cost curve** — taming a high-dep component often frees its dependencies too.
5. **Integration tests are the refactoring seatbelt.** Pin existing behavior with coarse tests before touching code, run them often, then migrate to unit tests later.
6. **Test only what you're changing.** Grow the tested region around the work you actually have to do.
7. **Don't reinvent dependency-breaking — read Feathers.** This chapter sends you there for seams and characterization tests.

## Connects To
- **Ch 3 (Mocks & stubs / breaking dependencies)**: the isolation techniques you need to execute the hard-first strategy and turn integration tests into unit tests.
- **Working Effectively with Legacy Code (Feathers)**: the deep treatment of seams & characterization tests — the "how to break dependencies safely" half of the two problems this chapter intentionally delegates.
- **Ch 11 (Design & testability)**: legacy pain is the absence of testable design (no seams); this chapter is what you do when you inherit code that ignored Ch 11. Khorikov ch. 7 is cited for an in-depth refactoring example.
