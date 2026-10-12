# Patterns & Techniques — Khorikov, Unit Testing

## AAA (Arrange, Act, Assert)
**When to use**: structuring every unit test.
**How**: one Arrange (set up SUT + deps), one single-line Act (invoke the behavior), one Assert (verify observable outcome). Avoid multiple AAA blocks (split into separate tests) and `if` statements in tests.
**Trade-offs**: large Arrange sections move to private factory methods / Object Mother, not shared mutable fixtures.

## Score every test on the four pillars
**When to use**: deciding whether a test is worth keeping.
**How**: rate protection-against-regressions, resistance-to-refactoring, fast-feedback, maintainability; **multiply** (any near-zero ⇒ worthless). Resistance to refactoring is binary and non-negotiable; trade only between protection and speed.
**Trade-offs**: max only 3 of 4 — you slide between protection (richer) and speed (faster).

## Functional core, mutable shell (functional architecture)
**When to use**: making domain logic output-based-testable.
**How**: push side-effect-free decisions into a pure core that returns instructions; a thin mutable shell gathers inputs up front and applies the instructions. Test core with fast output-based tests, shell with few integration tests.
**Trade-offs**: more classes; can increase up-front data reads.

## Humble Object pattern
**When to use**: logic trapped behind a hard-to-test boundary (UI, DB, async, controller).
**How**: extract the logic into a separately testable component; leave a thin humble wrapper that only delegates. Moves code out of the "overcomplicated" quadrant.
**Trade-offs**: extra indirection.

## CanExecute / Execute pattern
**When to use**: validation/precondition logic in a controller you want in the domain.
**How**: domain class exposes `CanExecute()` (returns decision) consumed by the controller before `Execute()`; keeps conditional logic out of orchestration.
**Trade-offs**: couples controller to call ordering (mitigate with a guard inside Execute).

## Output-based over state-based over communication-based
**When to use**: choosing how to assert.
**How**: prefer asserting on a return value; fall back to state; use communication (mocks) only for unmanaged out-of-process dependencies.
**Trade-offs**: output-based needs functional code; communication-based is the most brittle.

## Mock only unmanaged dependencies, at the system edge
**When to use**: deciding what to mock.
**How**: use real **managed** deps (application DB) and verify final state; **mock unmanaged** deps (bus, SMTP) to protect their observable contract. Mock the *last* type before the unmanaged dependency, and only types you own (wrap third-party libs in an adapter).
**Trade-offs**: requires owning an abstraction layer.

## Spy at the edge over framework mock
**When to use**: verifying interactions with an unmanaged dependency.
**How**: handwrite a reusable spy with a fluent assertion API instead of inline framework `Verify`. Verify both existence and absence of calls (`VerifyNoOtherCalls`, `Times.Once`).
**Trade-offs**: a bit more code, far better readability/reuse.

## Migration-based database delivery
**When to use**: keeping DB schema testable + deployable.
**How**: ordered, immutable migration scripts in source control; never edit a committed migration; reference data is part of the schema. Each developer gets a separate DB instance.
**Trade-offs**: more migrations to manage vs single state snapshot.

## Integration-test data life cycle
**When to use**: keeping DB integration tests independent.
**How**: clean leftover data at the **start** of each test (base-class hook, FK-ordered deletes preserving reference data); run tests sequentially; use the same DBMS vendor as production; wrap arrange/act/assert each in its own transaction. Don't use in-memory DBs as substitutes.
**Trade-offs**: slower than in-memory, but accurate.

## Object Mother (and Test Data Builder)
**When to use**: building arrange-phase entities for integration tests.
**How**: a factory that returns ready-made domain objects; prefer Object Mother for brevity, Test Data Builder when many variations are needed.
**Trade-offs**: Mother grows many methods; Builder is verbose.

## Fail fast over edge-case tests
**When to use**: code that crashes immediately on bad input.
**How**: add preconditions/guard clauses and let it throw; skip tests for situations that self-evidently fail at once.
**Trade-offs**: relies on discipline around precondition coverage.

## Time as an explicit dependency
**When to use**: code reading the current time.
**How**: inject time as a value or `IDateTimeProvider` parameter; never via Ambient Context (static/global).
**Trade-offs**: threads a parameter through call sites.
