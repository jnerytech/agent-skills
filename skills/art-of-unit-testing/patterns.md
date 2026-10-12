# Patterns & Techniques — The Art of Unit Testing (Osherove)

## Arrange-Act-Assert (AAA)
**When**: every test.
**How**: Arrange inputs/SUT → Act on one entry point → Assert on one exit point. Blank-line-separate the three blocks.
**Trade-offs**: more than one Act or multiple unrelated Asserts → split the test.

## USE Naming
**When**: naming every test.
**How**: encode three facts — `Unit under test`, `Scenario`, `Expectation` (e.g. `verifyPassword_withNoNumbers_returnsError`).
**Trade-offs**: longer names; pays off because the name is all you get in a failed CI log.

## Factory function instead of beforeEach()
**When**: shared setup causes scroll fatigue or hidden state.
**How**: write `makeSUT(overrides)` that returns a freshly built SUT; each test calls it and sees its own inputs.
**Trade-offs**: slight repetition, but each test is self-contained and readable; avoids order-coupling.

## Parameterized tests
**When**: same behavior across many input/expectation pairs.
**How**: `test.each([...])` over a table.
**Trade-offs**: a failing row must still be identifiable — keep a descriptive name template.

## Parameter injection (stub a value)
**When**: SUT depends on a simple, hard-to-control input (time, random, config).
**How**: pass it as a plain argument with a production default; tests pass a fixed value.
**Trade-offs**: cleanest seam; only works when you control the signature.

## Functional injection / partial application
**When**: JS/functional code; want to inject behavior, not data.
**How**: pass a function as a dependency, or pre-bind args with partial application to produce a simpler injectable.
**Trade-offs**: no classes needed; can proliferate function params if overused.

## Constructor / object injection (OO)
**When**: stateful collaborators in class-based code.
**How**: take the dependency in the constructor; inject a stub/mock object (duck-typed or via an extracted interface).
**Trade-offs**: explicit and testable; adds wiring. Extract a common interface to fake fat dependencies.

## Modular injection (+ reset seam)
**When**: code calls a module-level function you can't reach via a parameter.
**How**: replace the module's export, run the test, reset it afterward.
**Trade-offs**: fragile, global, parallel-unsafe — prefer real injection when possible.

## Mock object (interaction test)
**When**: the exit point is a call to a third party (logger, email, network) with no return to assert on.
**How**: inject a fake that records the call; assert it was called with the expected args.
**Trade-offs**: one mock per test; over-mocking → overspecified, brittle tests.

## Isolation framework (dynamic fakes)
**When**: handwriting fakes is tedious or the interface is large.
**How**: Jest — `jest.fn()`, `jest.spyOn()`, `jest.mock()`, `mockReturnValue`/`mockImplementation`; verify with `toHaveBeenCalledWith`. Typed: substitute.js `Substitute.for<T>()`.
**Trade-offs**: powerful but easy to overspecify; keep interaction asserts to ~2–5% of tests.

## Extract Entry Point / Extract Adapter (async)
**When**: testing code that fetches data or uses timers.
**How**: pull pure logic into a synchronous function (entry point); wrap the I/O behind an adapter seam you can stub. Use fake timers for `setTimeout`/`setInterval`.
**Trade-offs**: a little indirection buys fast, deterministic tests; otherwise tests become flaky integration tests.

## Testing the test
**When**: you wrote a new test and it's green.
**How**: deliberately break the production code; confirm the test goes red. If it stays green, the test is worthless.
**Trade-offs**: one extra step; catches always-green tests.

## Fix–convert–kill (flaky tests)
**When**: a test fails non-deterministically.
**How**: fix the root cause if cheap; convert to an integration test if the flakiness is environmental; quarantine/kill if it can't be trusted. Never leave flaky tests in the green build.
**Trade-offs**: deleting tests feels wrong but a distrusted suite is worse.

## Test recipe strategy
**When**: deciding how to test a new feature.
**How**: write a recipe listing which levels (unit/component/integration/API/E2E) cover which parts; prefer many fast unit tests, few slow E2E. Aim roughly 1 high-level test per ~5 lower-level.
**Trade-offs**: avoids both E2E-only and unit-only antipatterns; needs upkeep.

## Delivery vs discovery pipelines
**When**: CI is slow or noisy.
**How**: split a fast delivery-blocking pipeline (must pass to release) from a slower discovery pipeline (good-to-know). Parallelize layers/stages.
**Trade-offs**: more pipeline config; keeps fast feedback honest.

## Legacy: test-feasibility table
**When**: adding tests to untested code.
**How**: score components on logic complexity × dependency level × business priority; pick easy-first (inexperienced team) or hard-first (experienced team). Wrap in integration tests before refactoring to break dependencies.
**Trade-offs**: prioritization beats random coverage; integration safety net is slower but catches regressions during refactor.

## Monkey-patching (last resort)
**When**: no injection seam exists and you can't change the signature.
**How**: replace the function/module member at runtime; restore it afterward (`jest.spyOn` + `restoreAllMocks`).
**Trade-offs**: global, fragile, parallel-hostile — refactor toward injection when you can.
