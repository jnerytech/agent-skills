# Cheatsheet — Khorikov, Unit Testing (decisions, not definitions)

## The four pillars (multiply — any ~0 ⇒ worthless test)
| Pillar | Maximize? | Note |
|---|---|---|
| Protection against regressions | trade vs speed | richer code paths catch more bugs |
| Resistance to refactoring | **always — non-negotiable** | zero false positives; binary |
| Fast feedback | trade vs protection | |
| Maintainability | **always** | small + simple deps |
> You can max only 3 of 4. Lock resistance + maintainability; slide between protection and speed.

## What to mock — decision rule
- **Shared in-process dependency** → isolate / mock (classical).
- **Managed out-of-process** (app-only DB) → **use the real thing**, assert final state.
- **Unmanaged out-of-process** (bus, SMTP, other apps see it) → **mock**, verify the contract.
- **Domain class / value / private dep** → **never mock** — brittle.

## Pick the test style
- Can the SUT return a value with no side effects? → **output-based** (best).
- Else does it change observable state? → **state-based**.
- Else only side effect is an unmanaged dependency? → **communication-based** (mock) — last resort.

## Types-of-code quadrant → test strategy
| | Few collaborators | Many collaborators |
|---|---|---|
| **High complexity / domain** | Domain model → **unit test hard** | Overcomplicated → **refactor (Humble Object), don't test as-is** |
| **Low complexity** | Trivial → **don't test** | Controllers → **integration test** |
> Goal: empty the overcomplicated corner — split into domain + controller.

## Coverage metrics
- Low coverage = real problem. High coverage ≠ good tests. **Negative indicator only — never a target.**

## Test smells / tells
- Test fails after a refactor with no behavior change → **brittle / false positive → kill or fix**.
- Asserting on a stub, or on calls to your own classes → **overspecification**.
- Test mirrors production code line-for-line → **tautology / leaking domain knowledge**.
- Production code has test-only branches/flags → **code pollution**.
- `if` or loop inside a test → split it.
- Mocking a concrete class → missing abstraction; split the class.
- Reading `DateTime.Now` / static singleton in SUT → **Ambient Context**; inject it.

## AAA quick rules
- One Act line. Multiple AAA blocks → multiple tests. No conditionals.
- Large Arrange → private factory / Object Mother, not shared fields.
- Name tests in plain English describing behavior, not method names.

## Test Pyramid
- Many unit (domain) · fewer integration (controllers, managed DB) · fewest E2E.
- Exception: simple CRUD/API apps flatten toward more integration tests.

## Database tests
- Migration-based delivery, immutable committed migrations, reference data in schema.
- Clean at **start** of test (not end). Sequential runs. Same DBMS as prod. No in-memory substitute.
