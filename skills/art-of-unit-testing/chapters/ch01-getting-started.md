# Chapter 1: Getting started

## Core Idea
A unit test invokes a **unit of work** through one **entry point** and verifies exactly one **exit point** (return value, state change, or third-party call); good unit tests are fast, isolated, in-memory, readable, maintainable, and trustworthy — everything else is integration testing.

## Frameworks Introduced
- **Unit of work / entry point / exit point**: A unit of work is all actions between the invocation of an entry point and a noticeable end result through one or more exit points.
  - When to use: Every time you decide what to test and how to scope a test.
  - How: Identify the entry point (the function signature/declaration you trigger from outside — parameters are context, not the entry point). Identify each exit point (publicly noticeable result). Write at least one separate, readably-named test per exit point. Scope can span one function, multiple functions, or multiple modules.
  - Why it works: Mapping triggers to verifiable results makes test scope explicit and keeps each test focused on one outcome, so failures pinpoint one requirement. Failure mode: bundling exit points into one test makes failures ambiguous and tests fragile.
- **The unit test checklist (good-test criteria as yes/no questions)**: A diagnostic to separate true unit tests from integration tests.
  - When to use: Auditing any existing test you're unsure about.
  - How: Ask — Can I (and any teammate) run it months later? All tests in a few minutes? At the push of a button? Write a basic test in minutes? Does it pass despite bugs in another team's code? Same result across machines? Does it break without DB/network/deployment? Are tests independent of each other? Any "no" → it's likely integration, not unit.
- **TDD (test-first development)**: Red-Green-Refactor.
  - When to use: When deciding *when* to write tests; to gain trust by testing the test itself.
  - How: (1) Write a failing test as if production code worked. (2) Make it pass with the simplest production code — don't touch the test. (3) Refactor production + test code in tiny steps, rerunning all tests after each.

## Key Concepts
- **SUT**: Subject/system/suite under test — the thing you're testing (also CUT: component/class/code under test).
- **Entry point**: The function declaration/signature you trigger from outside; where the test invokes the unit of work. A unit can have multiple entry points used by different tests.
- **Exit point**: An externally visible end result — return value, state change, or third-party call. Maps to Meszaros' direct/indirect outputs.
- **Dependency**: Something you don't fully/easily control in a test (file logger, network, other teams' code, slow/DB/thread work). Rule of thumb: fully controllable + in-memory + fast = not a dependency.
- **Integration test**: A test that fails one or more good-unit-test criteria — uses a real dependency (network, time, filesystem, DB) outside the execution process.
- **Regression**: Previously working functionality (a unit of work) that now breaks.
- **Control flow code**: Code containing logic (if, loop, calculation, decision). Logic-free getters/setters need no direct test until logic is added.
- **Refactoring**: Changing code without changing its functionality (rename, split method) for readability/maintainability.

## Mental Models
- **Use "different exit point → different test → different technique"**: return-value tests are easiest (call, check); state-based tests need a second call to inspect; third-party tests force mock objects. Keep mock-based tests under ~5%.
- **Think of query vs command actions** (Command Query Separation): queries return without changing state; commands change state without returning. Separating them improves testability.
- **Use the car-engine analogy for integration tests**: many subsystems must work together, so a failure has many possible sources — hard to localize. Unit tests isolate one subsystem.
- **Think of the three test pillars as Readability, Maintainability, Trust**: lose any one and you revert to manual testing or debugging, erasing the time benefit.

## Code Examples
```js
const assertEquals = (expected, actual) => {
  if (actual !== expected) {
    throw new Error(`Expected ${expected} but was ${actual}`);
  }
};
const check = (name, implementation) => {
  try {
    implementation();
    console.log(`${name} passed`);
  } catch (e) {
    console.error(`${name} FAILED`, e.stack);
  }
};
check('sum with 2 numbers should sum them up', () => {
  const result = sum('1,2');
  assertEquals(3, result);
});
```
- **What it demonstrates**: A test framework is just helper functions — `assert` (throws on mismatch) + a runner (`check`) that names, catches, and reports. Jest just generalizes this.

## Worked Example
The `sum(numbers)` function evolves to show all three exit-point types. v1: `sum` splits a "1,2" string and returns `a+b` — here the entry point *is* the exit point (result returned where it's triggered). v2 adds `total += result` plus a `totalSoFar()` reader — now two exit points (return value AND observable state change), warranting two tests; `totalSoFar` can itself be an entry point in a separate test proving it returns 0 before any sum. v3 adds `logger.info(...)` — a third exit point: calling a third party (a dependency you can't control), which later requires mocks. The author then tests v1 from scratch with no framework: a `parserTest` that calls `sum('1,2')`, throws if `result !== 3`, catches exceptions, and is wired via `npm test` → `node` a JS file in package.json.

## Key Takeaways
1. Write one readably-named test per exit point — don't bundle outcomes into one test.
2. The entry point is the function signature, not its parameters; parameters are input/context.
3. Classify each exit point (return / state / third party) because each needs a different technique; avoid third-party (mock) tests where possible (<5%).
4. Run the unit-test checklist to honestly classify a test; any "no" means it's integration, not unit — and integration tests must be kept separate to preserve a "safe green zone."
5. Good unit tests run quickly, in memory, fully isolated, fully controlled, and as synchronous/linear as possible.
6. TDD's underappreciated payoff: seeing a test fail then pass (without editing it) tests the test itself, building trust and reducing debugging.
7. TDD ≠ good tests — they're separate skills (good testing, test-first, design); learn them one at a time.

## Connects To
- **Ch 2**: Replaces the hand-rolled `assertEquals`/`check` with Jest's API, naming, and continuous execution.
- **Ch 3 (stubs/isolation) & later mocks**: "Full control of code under test" and replacing dependencies with stubs/mocks foreshadowed here.
- **Khorikov, *Unit Testing Principles, Practices, and Patterns***: cited for the deeper treatment of observable behavior.
- **Meszaros, *XUnit Test Patterns***: entry/exit points map to direct/indirect inputs and outputs ("front door").
- **Feathers, *Working Effectively with Legacy Code***: "code that has no tests" as the legacy-code definition.
- **Beck, *TDD By Example* / Fowler, Command Query Separation**: recommended for test-first and design skills.
