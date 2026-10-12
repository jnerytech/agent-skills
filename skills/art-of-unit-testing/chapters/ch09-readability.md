# Chapter 9: Readability

## Core Idea
Readability is the third pillar of good tests (after trustworthiness and maintainability) and the one that connects the test's author to the developer who reads it months or years later. A test is a story you tell the next programmer: it should reveal what the application does and why, without forcing the reader to open and decode the test body. The chapter is short and practical — four concrete habits make tests self-explanatory: name tests with three mandatory facts, kill magic values, separate asserts from actions, and avoid generic setup. The unifying goal: release the next developer from the burden of reading test code to understand what is being tested.

## Frameworks Introduced
- **USE naming (Unit under test, Scenario, Expectation)**: every test name (or its surrounding structure) must carry three facts — the entry point / unit of work, the scenario it runs under, and the expected behavior at the exit point. *When*: naming any test. *How*: encode all three in the function name (`verifyPassword_withFailingRule_returnsErrorBasedOnRuleReason`), or split across nested `describe`/`it` strings — layout is free, the three facts are not. *Why*: drop any one and the reader must read the code to recover it; also, the name is often the only thing shown in a failed CI log, so a good name can diagnose a failure without debugging.

## Key Concepts
- **The three name parts**: entry point first (enables navigation and IDE autocomplete), then the scenario ("with..."), then the expected exit behavior in plain English.
- **Missing-information smell**: names like `'with a failing rule'` or `'verifyPassword'` alone answer only one of the three questions and force a code dive.
- **Magic values ("witchcraft values")**: hardcoded, undocumented constants (`0`, `[]`, `'jhGGu78!'`) that work but whose meaning is opaque to a reader.
- **Magic values propagate**: a too-specific-looking input gets copied into other tests "just to be safe," spreading confusion.
- **Naming variables explains what NOT to care about**: a value like `"anything"` signals the input is irrelevant; `SUNDAY`/`NO_RULES` signal what is relevant.
- **Separate asserts from actions**: never nest the method call inside the assertion; assign the result to a named variable first.
- **Setup abuse**: `beforeEach` that creates mocks/stubs hides collaborators from the test and becomes a dumping ground of mixed state.
- **Tests as executable documentation**: a newcomer should learn how a component behaves by reading its tests alone — if they can't, that's a readability red flag.

## Mental Models
- **Test as a story for the next generation**: you're writing for a stranger who inherits the code; optimize for their comprehension, not your keystrokes.
- **The name is the only survivor**: in a failed build log, comments and code vanish — only the test name remains, so it must stand alone as a diagnosis.
- **Helper over setup**: prefer per-test helper functions (`makeMockLogger()`) to a shared `beforeEach`; you keep everything visible in the test while still removing duplication.
- **Locality of understanding**: everything needed to understand a test should sit within the test body, near the reader's eyes — not scrolled away at the top of the file.

## Code Examples
```js
// BAD — what is under test? when? expected what? (one fact at best)
test('with a failing rule', () => { /* ... */ });
test('verifyPassword, returns error based on rule.reason', () => { /* ... */ });

// GOOD — USE: unit + scenario + expectation
test('verifyPassword, with a failing rule, returns error based on rule.reason',
  () => { /* ... */ });

// Or split the three facts across nested structure:
describe('verifyPassword', () => {
  describe('with a failing rule', () => {
    it('returns error based on the rule.reason', () => { /* ... */ });
  });
});
```
- **What it demonstrates**: the same three facts can live in a flat name or a nested `describe`/`it` tree; what matters is that unit, scenario, and expectation are all present so the reader never has to open the body.

## Worked Example
Start with a test riddled with magic values, a fused assert, and hidden setup:

```js
describe('password verifier', () => {
  let mockLog;
  beforeEach(() => { mockLog = Substitute.for<IComplicatedLogger>(); }); // hidden
  test('on weekends, throws', () => {
    expect(() => verifyPassword('jhGGu78!', [], 0)) // 3 magic values
      .toThrowError("It's the weekend!");
  });
});
```

Rewritten for readability — USE name, named values, visible mock, separated act/assert:

```js
describe('verifyPassword', () => {
  test('on weekends, with any password, throws a weekend error', () => {
    const SUNDAY = 0;
    const NO_RULES = [];
    const act = () => verifyPassword('anything', NO_RULES, SUNDAY);
    expect(act).toThrowError("It's the weekend!");
  });
});
```

`SUNDAY` and `NO_RULES` explain what matters; `'anything'` declares the password is irrelevant; the mock (if needed) is created inside the test or via a helper, not `beforeEach`; and the call is pulled into `act` so the assertion reads cleanly and is easy to debug.

## Key Takeaways
- Name every test with all three USE facts: unit of work, scenario, expected behavior — drop one and you force a code dive.
- A great test name lets you diagnose a CI failure straight from the log, no debugging required.
- Replace magic values with meaningfully named constants, or bake the meaning into a string value (`"anything"`).
- Variable names communicate both what is important and what the reader should ignore.
- Pull the act out of the assertion — one statement for the call, one for the expectation.
- Avoid `beforeEach` for mocks/stubs; create them in the test or via a per-test helper to keep collaborators visible.
- Treat tests as living documentation: a newcomer should understand the component from the tests alone.

## Connects To
- **Ch 8**: maintainability — helper functions over shared `beforeEach` serve both pillars; readable, DRY arrange code resists rot.
- **Ch 2**: the entry-point / exit-point vocabulary of the unit of work, here reused as the backbone of test naming.
