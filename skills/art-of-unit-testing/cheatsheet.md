# Cheatsheet — The Art of Unit Testing (Osherove)

## Decision rules
- **When the result is a return value** → assert the value (value-based test). No fakes needed.
- **When the result is a state change** → call the SUT, then query state through another entry point and assert (state-based).
- **When the result is a call to a third party you don't control** → inject a **mock** and assert on the call (interaction test). Only here.
- **When a dependency only feeds the SUT inputs** → use a **stub**; never assert on it.
- **When you wrote a green test** → break the production code once; if it stays green, the test is worthless. Fix it.
- **When a test has an `if`/`for`/computed expected value** → remove the logic; hardcode the expected. Logic in tests hides bugs.
- **When a test is flaky** → fix root cause → else convert to integration → else quarantine/delete. Never leave it in the green build.
- **When setup grows / `beforeEach` causes scroll fatigue** → replace with a `makeSUT()` factory function.
- **When you're tempted to test a private method** → test it through a public entry point, or extract it into its own unit.

## One mock per test
- Many **stubs** per test = fine. More than **one mock** = you're testing too much; split.
- Interaction (mock) tests should be ~**2–5%** of your suite. Default to value/state tests.

## Trust / fragility tells (smells)
| You see… | Probably… | Do |
|---|---|---|
| Test never goes red | always-green / no real assert | break prod to verify; add real exit-point assert |
| Test breaks on unrelated refactor | overspecification | assert only the relevant exit point |
| Asserts on a stub's return | testing the test setup, not the SUT | drop the assert |
| Exact full-string / order / schema assert | brittle | assert on the part that matters (`toContain`, key fields) |
| Random pass/fail | flaky (time, async, shared state) | inject time, await properly, isolate state |
| Test depends on another test running first | constrained order | make each test self-contained |

## USE naming (test name = three facts)
`unitOfWork_scenario_expectedBehavior` → `verifyPassword_withNoNumbers_returnsFalse`
The name is the **only** clue in a failed CI log. Spend on it.

## Injection technique → pick by code style
| Situation | Technique |
|---|---|
| Simple value (time, config) | Parameter injection |
| Functional / JS | Inject a function; partial application |
| Module-level function, no param reach | Modular injection + reset (fragile) |
| Class with collaborators | Constructor injection (object / extracted interface) |
| Large/fat interface | Extract a common interface, fake that |
| No seam, can't change signature | Monkey-patch + restore (last resort) |

## Test levels — prefer fast & low
| Level | Speed | Confidence | Use sparingly? |
|---|---|---|---|
| Unit | fastest | per-unit | no — most of suite |
| Component (in-mem) | fast | module | moderate |
| Integration | slow | real deps | targeted |
| API (out-of-proc) | slow | backend contract | targeted |
| E2E / UI (system) | slowest | full stack | very few |
Rule of thumb: ~**1** higher-level test per **~5** lower-level. E2E hits diminishing returns fast.

## Three pillars — the goal of every test
1. **Trustworthy** (Ch 7) — green means works, red means broken. No logic, no flakiness, real asserts.
2. **Maintainable** (Ch 8) — fails only when behavior actually changes. Metric: count false failures.
3. **Readable** (Ch 9) — explains itself: USE name, AAA, no magic values, clear assert message.

## TDD loop
Red (failing test) → Green (simplest pass) → Refactor (clean both prod & test). TDD ≠ a substitute for writing *good* tests.

## Legacy: where to start
Score components on **logic complexity × dependencies × priority**. Inexperienced team → **easy-first** (build confidence). Experienced team → **hard-first** (unblock the system). Wrap in integration tests *before* refactoring to break dependencies.
