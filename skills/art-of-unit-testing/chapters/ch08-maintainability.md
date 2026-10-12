# Chapter 8: Maintainability

## Core Idea
Maintainability is the second of the **three pillars** (readability, maintainability, trustworthiness). A test suite earns its keep over the 4-10 year life of the code only if tests fail **for reasons we truly care about**. The discipline: distinguish **true failures** (test found a production bug) from **false failures** (test broke for any other reason), then drive the false-failure count toward zero. Two governing questions: *which test failures force us to change the test?* and *when do we voluntarily change a test to make it more maintainable?*

## Frameworks Introduced
- **True vs. false failures (maintainability metric)**: formulation — classify every red test as either finding a real bug (true) or breaking for another reason (false). / *When*: during test reviews and over time as the suite ages. / *How*: log the count and reason of false failures across versions; each recurring reason is a maintainability defect to fix. / *Why*: false failures erode trust until developers ignore or delete tests, throwing away the work that created them.
- **Factory & helper functions for setup**: formulation — centralize creation of the unit under test (and its fakes) in named functions instead of inlining `new` in every test. / *When*: any time more than one test instantiates the same object, or a constructor/API is likely to change. / *How*: `makeX(...)` returns a preconfigured instance with sensible defaults and optional overrides; helpers like `addDefaultUser()` encapsulate shared arrange steps. / *Why*: an API change is then absorbed in one place — the tests themselves stay untouched.

## Key Concepts
- **Which failures force a test change**: (1) test is no longer relevant or **conflicts with another test** (delete the stale one — exception: feature toggles); (2) a change in the production code's **API/constructor**; (3) **changes in other tests** leaking through shared state.
- **Constructor-change fragility**: every test that calls `new PasswordVerifier(...)` must change when the constructor gains a parameter or swaps `ILogger` for `IComplicatedLogger`. Factory functions quarantine that blast radius.
- **Avoid testing private/protected methods**: private methods are *internal contracts* that shift on refactor. Test only the public, observable behavior. A private method always sits under a public use case ending in one of three exit points: return value, state change, third-party call.
- **Wanting to test a private method** signals a missing abstraction — make it public, make a stateless one public+static, or extract it into its own class with a real contract.
- **DRY vs. DAMP in tests**: duplication forces multi-edit churn (and tempts deletion), so abstract nonessential arrange/assert into helpers — but don't DRY so hard that you hide the test's intent (readability, Ch 9).
- **Avoid setup methods (`beforeEach`)**: they get abused — can't take parameters, can't return values, can't be factories, run for *all* tests even ones that don't need them. Prefer helper/factory functions; reserve `beforeEach`/`afterEach` for resetting shared resources.
- **Parameterized tests** (`test.each`): collapse identical-shape tests into one, moving duplicated setup *and* assertion into the data table — only when the scenario is truly the same and just input/output vary.
- **Overspecified tests**: assert internal state, use multiple mocks, use stubs as mocks, or demand exact order/exact string when not required.
- **Test isolation / interdependence anti-patterns**: a test must run in its own little world. **Constrained test order** (one test relying on another having run, or not run) breaks because runners don't guarantee order.
- **Magic values & string matching**: strings are a UI — they get embellished. Assert `toMatch(/2 failed/)` (contains) over `toBe("you have 2 failed rules.")` (exact); numbers survive localization, decorative text does not.

## Mental Models
- **The boy who cried wolf**: a test riddled with false failures trains the team to dismiss it ("if it sometimes passes, it passes") — and a real bug slips through. Trust is the asset being spent.
- **Code lives a decade**: assume the design *will* change. Maintainability is insurance bought now (factories, helpers) against a near-certain future API change.
- **Exit points, not call paths**: a good test asserts on what crosses the unit's boundary (return / state / third-party call), never on which internal function got called. Asserting internals couples the test to implementation for no benefit.
- **The test's own little world**: each test sets up everything it needs and resets what it shares — no test is allowed to be another's prerequisite.

## Code Examples
```js
// FRAGILE: constructor inlined in every test; a signature change
// (ILogger -> IComplicatedLogger) forces edits across the whole file.
const verifier = new PasswordVerifier([], { info: jest.fn() });

// MAINTAINABLE: creation centralized; a constructor change is absorbed
// in makePasswordVerifier alone — the tests below never change.
const makeFakeLogger = () => ({ info: jest.fn() });
const makePasswordVerifier = (rules, logger = makeFakeLogger()) =>
  new PasswordVerifier(rules, logger);

it("passes with zero rules", () => {
  const verifier = makePasswordVerifier([]);
  expect(verifier.verify("any input")).toBe(true);
});
```
- **What it demonstrates**: a factory function decouples the *creation* of the unit under test from the tests, converting a many-file API change into a one-line change — the central maintainability move of the chapter.

## Worked Example
**Killing constructor-change fragility.** Start with tests that each call `new PasswordVerifier([failingRule], { info: jest.fn() })` directly. Now the future arrives: the constructor swaps `ILogger` for `IComplicatedLogger` (`PasswordVerifier2`). With inlined construction, *every* test breaks and must be hand-edited — pure false failures.

Refactor before the change lands: extract `makeFakeLogger()` and `makePasswordVerifier(rules, logger = makeFakeLogger())`; rewrite tests to call the factory. When the breaking change hits, edit only two functions — `makeFakeLogger` now returns `Substitute.for<IComplicatedLogger>()` and `makePasswordVerifier` returns `new PasswordVerifier2(...)`. The `it(...)` blocks are byte-for-byte identical. "That's the type of manageable change I can live with in a real project." The same pattern (`addDefaultUser()` + `beforeEach(() => getUserCache().reset())`) cures the constrained-order cache tests without hiding intent.

## Key Takeaways
- Tests must fail **only for reasons you care about**; measure and drive down false failures.
- A conflicting/irrelevant test gets deleted (unless feature toggles); an API-change failure gets mitigated with factory/helper functions, not test edits.
- Never test private/protected methods or assert internal calls — test observable behavior at the exit point (return value, state change, third-party call).
- Eliminate test interdependence: no shared state across tests; reset shared resources in `beforeEach`/`afterEach`; never rely on test order.
- Keep tests DRY with helpers and parameterization, but stop before you hide intent.
- Prefer `toMatch`/`contains` over exact-string and full-collection assertions; treat strings as UI and avoid order/schema overspecification.

## Connects To
- **Ch 7** (trustworthiness): the first pillar supplies the true-vs-false-failure distinction this chapter operationalizes — a maintainable test is one whose failures stay trustworthy as the code ages; both warn against test bugs and overspecification eroding confidence.
- **Ch 9** (readability): the explicit guardrail on this chapter — DRY/factory abstraction must not hide what a test arranges or asserts; readability is where "don't over-DRY" gets its rules (DAMP).
