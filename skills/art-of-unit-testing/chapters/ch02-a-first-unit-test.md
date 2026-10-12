# Chapter 2: A first unit test

## Core Idea
A unit testing framework like Jest gives you structure, repeatability, and confidence by acting at once as library, assertion, runner, and reporter — and the real craft is not writing one test but evolving tests that stay readable and maintainable as the system grows.

## Frameworks Introduced
- **Arrange-Act-Assert (AAA)**: structure every test in three parts — arrange the inputs/state, act on the entry point, assert on the exit point.
  - When to use: every unit test; it's the default skeleton.
  - How: (1) Arrange — build inputs, fakes, and bring the system under test to a known state; (2) Act — call the entry point and capture the output; (3) Assert — verify the outcome at an exit point. Separate the three with blank lines.
  - Why it works / failure mode: makes tests instantly scannable ("where's the act?"). Failure mode: multiple unrelated asserts at the end → assertion roulette (a failing first assert hides later ones), pushing people to comment lines out.
- **USE naming**: name a test with **U**nit under test, **S**cenario/inputs, **E**xpectation/exit point.
  - When to use: every test name; the name is often all you see on a failing build.
  - How: `verifyPassword, given a failing rule, returns errors`. With `describe()` nesting, split the three pieces across levels: outer describe = unit, inner describe = scenario, `it()` = expectation.
  - Why it works: a clear name lets a reader diagnose the production bug without reading the test body.

## Key Concepts
- **Anatomy of a framework**: Jest fills four roles — test library, assertion library (`expect`), test runner, test reporter (plus isolation facilities for mocks/stubs/spies).
- **xUnit**: family of frameworks (JUnit, NUnit, CppUnit) descended from SUnit; standardized structure and XML report still consumed by build tools like Jenkins.
- **TAP**: Test Anything Protocol, an alternative reporting standard born in Perl; Jest is neither xUnit- nor TAP-compliant by default (use `jest-xunit` / `jest-tap-reporter`).
- **Assertion roulette**: commenting out asserts to test others; symptom of cramming multiple checks into one test (term from Meszaros' *xUnit Test Patterns*).
- **Scroll fatigue**: having to scroll up/down to find where state was created/declared, caused by `beforeEach()` hoisting setup away from the `it()`.
- **Factory method**: small helper function that builds an object or state and is reused across tests.
- **Parameterized tests**: one test body run over a table of inputs (`test.each` / `it.each`, or a vanilla `for`).
- **Test categories**: Jest has no built-in categories; emulate with `--testPathPattern` or separate `jest.config.js` files with distinct `testRegex`.
- **String comparison maintainability**: assert with `toContain`/`toMatch` (substring/regex) rather than exact equality so edge changes to strings don't break tests.
- **Testing the test**: temporarily inject a bug to confirm the test fails when it should.

## Mental Models
- Use **AAA + USE** as the default skeleton for any new test.
- Use **`toContain`/`toMatch`** instead of `toEqual` when asserting on strings — strings are UI and their edges drift.
- Use the **terse `test()` flavor** when context is simple; use **`describe()`-driven (BDD) nesting** when one scenario has multiple exit points/expectations.
- Use **factory methods over `beforeEach()`** when setup hoisting causes scroll fatigue — keep the *when* and *with what* inside the `it()`.
- Use **parameterized tests only for input variations** of the *same* scenario; split different expected outputs into separate tests.

## Code Examples
```js
describe('PasswordVerifier', () => {
  describe('with a failing rule', () => {
    it('has an error message based on the rule.reason', () => {
      const verifier = makeVerifierWithFailedRule('fake reason');
      const errors = verifier.verify('any input');
      expect(errors[0]).toContain('fake reason');
    });
  });
});
```
- **What it demonstrates**: AAA + USE naming via nested `describe`/`it`, a factory method (`makeVerifierWithFailedRule`) keeping arrange inside the test, and a non-brittle `toContain` assertion.

## Worked Example
The **Password Verifier** starts as `verifyPassword(input, rules)` returning an errors array. First test (`test()`, terse):
```js
test('badly named test', () => {
  const fakeRule = input => ({ passed: false, reason: 'fake reason' }); // arrange
  const errors = verifyPassword('any value', [fakeRule]);               // act
  expect(errors[0]).toMatch('fake reason');                            // assert
});
```
Improvements applied in sequence: (1) **test the test** by commenting out the `errors.push` line to confirm failure; (2) rename with **USE** → `verifyPassword, given a failing rule, returns errors`; (3) swap `toMatch`/`toEqual` for `toContain` for maintainability; (4) wrap in `describe()`, then nest a second `describe()` for the scenario and use `it()` for the expectation. Refactoring `verifyPassword` into a stateful `class PasswordVerifier1` (`addRule` + `verify`) widens the unit of work to two coupled calls; adding a second assert (`errors.length`) creates assertion roulette, so each check becomes its own `it()` — exposing heavy duplication. `beforeEach()` on two levels removes the duplication but introduces scroll fatigue (and risks: forgotten `errors` reset, Jest's parallel runs sharing top-level state). **Factory methods** (`makeVerifierWithFailedRule`, `makePassingRule`) replace `beforeEach()` entirely, restoring readability while keeping state inside each `it()` — and the `describe()` blocks become optional sugar, allowing a return to flat `test()` calls.

## Key Takeaways
1. Jest is one framework doing four jobs (library, assert, runner, reporter); leaning on it lets you focus on patterns, not tooling.
2. AAA structures a test; USE names it — together they make tests self-explanatory on a red build.
3. Prefer `toContain`/`toMatch` over exact equality on strings to reduce brittleness and false positives.
4. One logical assertion per test avoids assertion roulette; split extra checks into separate `it()`s.
5. `beforeEach()` cuts duplication but breeds scroll fatigue and can become a dumping ground; factory methods usually read better.
6. Parameterize only input variations of the same scenario; never mix differing expectations into one `test.each` table.
7. Jest lacks test categories — use `--testPathPattern` or per-category `jest.config.js` files with `testRegex`.

## Connects To
- **Ch 1**: replaces the hand-rolled framework from Ch 1 with a real one; reinforces entry points, exit points, and the unit-of-work definition now exercised through Jest.
- **Ch 3**: the stateful `PasswordVerifier` sets up dependencies and testability problems; Ch 3 introduces fakes, stubs, mocks, and spies to handle them.
