# Chapter 7: Trustworthy tests

## Core Idea
A test is worth nothing unless you can trust it, maintain it, and read it — the **three pillars** of a good test. **Trustworthiness** comes first: if you don't trust a test, there's no point running, fixing, or maintaining it. You trust a test when its failure genuinely worries you (you don't move on assuming the test is wrong) and its passing lets you relax (you don't feel the need to manually debug "just in case"). This chapter is a review checklist for spotting tests that lie — both failing tests that shouldn't, and quiet green tests that pass for the wrong reasons.

## Frameworks Introduced
- **Why tests fail (root-cause triage)**: formulation — a test can fail for exactly one *good* reason (a real production bug) and several *bad* ones (buggy test/false failure, out-of-date test, conflict with another test, flakiness). / When — every time a test goes red. / How — eliminate the bad reasons before trusting the red signal; debug production first, then suspect the test. / Why — only the first reason justifies acting on the failure; the others are the test telling you not to trust it.
- **Fix, convert, or kill (flaky-test game)**: formulation — quarantine each flaky test, then choose one of three fates. / When — after defining "flaky" (e.g. inconsistent across 10 runs with no code change) and pulling flaky tests out of the delivery build. / How — **Fix** by controlling the dependency (seed the DB the test needs); **Convert** to a lower-level test by stubbing a real dependency; **Kill** if the value no longer justifies the maintenance cost. / Why — flaky tests are costly and erode trust in the whole suite; aim for zero. Beware the sunk-cost fallacy when deciding to kill.

## Key Concepts
- **The three pillars**: trustworthiness, maintainability, readability. Drop one and the others collapse — you can't trust a test you can't read.
- **False positive / false negative**: a false positive is a test that fails when nothing is broken; a false negative is a test that passes while a real bug exists. Both destroy trust.
- **Testing the test (introduce a bug)**: after fixing a suspected buggy test, plant an obvious bug in production (flip a Boolean) and confirm the test fails; then revert and confirm it passes. You've now seen it fail-when-it-should and pass-when-it-should.
- **Avoid logic in tests**: `if/switch/else`, `for/foreach/while`, concatenation (`+`), `try/catch` inside a test add bugs and reduce readability. Logic also hides in helpers, handwritten fakes, and utilities — test those if you must keep them.
- **Dynamic expected values**: computing the expected result in the assert often repeats the production algorithm, so the test inherits the same bug. Use **hardcoded** expected values; make inputs trivial enough to make this easy.
- **Test one concern (exit point)**: an exit point is a single end result — return value, state change, or third-party call. One test per concern.
- **Multiple asserts ≠ multiple concerns**: asserting `name` and `age` of one built object is fine (one concern); asserting a return value *and* a callback is two concerns → two tests.
- **Always-green / no-assert tests**: a test with no assert verifies nothing. The exception is a deliberate "does not throw" check — name it accordingly (`expect(fn).not.toThrow()`).
- **Safe green zone**: keep fast, non-flaky unit tests separate from flaky integration tests so a red test is genuinely alarming and can't be hand-waved as "just network."
- **Code coverage is a guide, not a goal**: coverage targets breed meaningless tests. Measure escaped bugs and time-to-fix instead.

## Mental Models
- **Trust is behavioral, not theoretical**: you measure trust by what you *do* on red/green — worry or shrug, relax or re-debug. If you still test manually after green, you don't trust the suite.
- **The test contains the same bug as the code**: any logic duplicated from production into the assert means the test agrees with the bug instead of catching it. Trust trumps DRY.
- **Asserts are symptoms of a disease**: a thrown assert exception stops the test, so later asserts never run. Splitting concerns into separate tests reveals *all* symptoms at once, making the underlying defect easier to diagnose.
- **Flakiness scales with real dependencies**: the higher the test level, the more moving parts (DB, network, config) and the more flakiness — higher confidence, lower determinism. Unit tests should be fully deterministic; flakiness there means a hidden dependency (clock, machine name, filesystem) crept in.

## Code Examples
```js
// Untrustworthy: logic repeated from production — test inherits the bug
expect(result).toBe("hello" + name);   // prod: return "hello" + name;

// Trustworthy: hardcoded expected value, trivial input
const result = makeGreeting("abc");
expect(result).toBe("hello abc");
```

## Worked Example
**Spotting a test with logic that can't be trusted.** A teammate submits this for review and it's green:
```js
const namesToTest = ["firstOnly", "first second", ""];
it("works", () => {
  namesToTest.forEach((name) => {
    const result = isName(name);          // prod: input.split(" ").length === 2
    if (name.includes(" ")) expect(result).toBe(true);
    else expect(result).toBe(false);
  });
});
```
Red flags: (1) a `forEach` loop — loops have bugs; (2) an `if/else` that *re-derives* the production rule ("has a space → is a name"), so the test encodes the same logic it's meant to verify; (3) the name `"works"` is generic because the test does several things at once. To prove it lies, plant a production bug (`=== 3`) — the loop/branch may still happen to agree. **Fix:** split into separate hardcoded tests, each one concern, each named:
```js
it("returns true for two words", () => expect(isName("first second")).toBe(true));
it("returns false for one word",  () => expect(isName("firstOnly")).toBe(false));
```
No logic, no leaked algorithm, self-documenting names, and each case fails independently.

## Key Takeaways
- Trust is the first pillar; a test you don't trust is wasted effort no matter how clever.
- Only a real production bug is a *good* reason to fail. Buggy test, out-of-date, conflict, and flakiness all mean "don't trust me yet."
- When you fix a suspected buggy test, **test the test**: introduce an obvious production bug and confirm it fails, then revert and confirm it passes.
- Strip logic from tests — no loops, branches, concatenation, or dynamic expected values. Prefer hardcoded values; trust beats DRY.
- One concern per test; multiple asserts are fine only when they verify the same exit point. Split when the next assert still matters after the first fails.
- Be suspicious of green tests too: no asserts, unreadable, mixed with flaky integration tests, or constantly changing.
- Quarantine flaky tests and play **fix, convert, or kill**. Coverage is a guide, never the goal — measure escaped bugs.

## Connects To
- **Ch 8**: Maintainability, the second pillar — out-of-date and constantly-changing tests are a maintainability problem; reducing how often production changes force test changes keeps the suite trustworthy over time.
- **Ch 9**: Readability, the third pillar — "I can't understand the test" is a trust killer; good names and clear structure (foreshadowed in the exit-point and `"works"` discussions) are detailed here.
