# Chapter 5: Isolation frameworks

## Core Idea
An **isolation framework** is a set of programmable APIs for the *dynamic* creation, configuration, and verification of mocks and stubs — in object or function form — replacing repetitive handwritten fakes with shorter, more readable code. Osherove deliberately calls them *isolation* frameworks, not "mocking" frameworks, because they isolate a unit of work from its dependencies and serve *both* stubs (incoming) and mocks (outgoing). Used well, they make tests last years; abused, they produce tests you can't read or trust.

## Frameworks Introduced
- **Jest (loose / loosely typed)**: vanilla-JS-friendly, function-oriented isolation framework. *When*: faking modules (`require`/`import`) and single/higher-order functions; functional-style code. *How*: `jest.mock()`, `jest.fn()`, `jest.spyOn()`, plus simulation APIs `mockReturnValue`/`mockImplementation`. *Why*: least ceremony, fits Arrange-Act-Assert, readable. Caveat: uses the word "mock" everywhere even when stubbing; `jest.mock` calls must sit at top of file due to hoisting.
- **substitute.js (typed / strongly typed)**: TypeScript/OO-friendly. *When*: faking whole classes, interfaces, object hierarchies. *How*: `Substitute.for<T>()` generates the fake; `.returns()` stubs, `.received()` verifies, `Arg.is(...)` matches args. *Why*: signature changes don't force test edits — you only care about the one function tested.

## Key Concepts
- **Isolation vs. mocking framework**: same tools handle stubs (simulate incoming values) and mocks (verify outgoing calls); "isolation" names the goal, not one technique.
- **Loose vs. typed flavor**: choose by *what you fake* — modules/functions → Jest/Sinon; full objects/interfaces → substitute.js.
- **Dynamic vs. handwritten fakes**: frameworks generate fakes at runtime, eliminating boilerplate that handwritten fakes accumulate per method.
- **Module mocking ("fake it at the seam")**: `jest.mock("./module")` swaps an entire imported module — vital for legacy/uncontrolled deps.
- **`jest.fn()`**: returns an auto-tracked function; query later via `toHaveBeenCalledWith()`. Best for single-function mocks/stubs.
- **Matchers**: utility functions asserting on a passed argument's value (`stringMatching(/PASS/)`, substitute's `Arg.is`).
- **Stubbing behavior**: `mockReturnValue` (permanent — preferred), `mockReturnValueOnce` (sequenced), `mockImplementation`/`Once` for errors/complex logic.
- **Abstract away direct dependencies**: don't mock code you control; hide third-party APIs behind a ports-and-adapters seam so an upstream breaking change touches one adapter, not thousands of tests.
- **You rarely need mocks**: only the "call a third-party dependency" exit point warrants a mock; return-value/state exit points don't. ~2–5% of tests; ~0 in functional designs.
- **Overspecification antipattern**: too many `.received()`/expectations → fragile tests; never verify a stub was called.

## Mental Models
- **Three exit points, one mock-able**: return value, state change, third-party call. Reach for a mock *only* for the third; otherwise assert a return or observable state change from the outside.
- **Stubs everywhere, mocks sparingly**: stubs feed values in (safe to scatter); each mock adds verification noise — one mock/concern per test.
- **The framework is a sharp knife**: it makes faking *anything* trivial, which tempts you to fake things you shouldn't. Convenience is the trap.
- **AAA, not Record-Replay**: modern frameworks let you arrange a fake, act, then assert — readable, unlike the old record/replay ceremony.

## Code Examples
```js
// Module mocking — fake an entire imported module at the seam
jest.mock("./complicated-logger");
jest.mock("./configuration-service");
const { verifyPassword } = require("./password-verifier");
const mockLoggerModule = require("./complicated-logger");
const stubConfigModule = require("./configuration-service");

afterEach(jest.resetAllMocks);

test("info level, no rules → logs PASSED", () => {
  stubConfigModule.getLogLevel.mockReturnValue("info"); // stub incoming
  verifyPassword("anything", []);
  expect(mockLoggerModule.info)                          // mock outgoing
    .toHaveBeenCalledWith(expect.stringMatching(/PASS/));
});
```
- **What it demonstrates**: one framework call replaces a whole module; the *same* fake supplies a stubbed query (`getLogLevel`) and a verified command (`info`). `jest.mock` sits at top (hoisting); `resetAllMocks` clears state between tests.

## Worked Example
Goal: verify the verifier logs `PASSED` without a handwritten `FakeLogger`.

Handwritten pain — a custom var captures the value, then you assert on it:
```js
let logged = "";
const mockLog = { info: (t) => (logged = t) };
// ...verify... expect(logged).toMatch(/PASSED/);
```
With `jest.fn()` the tracking is automatic:
```js
test("passing scenario calls logger with PASSED", () => {
  const mockLog = { info: jest.fn() };          // auto-tracked fn
  const verify = makeVerifier([], mockLog);
  verify("any input");
  expect(mockLog.info)
    .toHaveBeenCalledWith(expect.stringMatching(/PASS/)); // matcher
});
```
For a full multi-method interface, attach `jest.fn()` per method (`{ info: jest.fn(), warn: jest.fn(), ... }`), or in TypeScript use `Substitute.for<IComplicatedLogger>()` + `mockLog.received().info(Arg.is(x => x.includes("PASSED")), "verify")` so signature changes don't break the test.

## Key Takeaways
- Frameworks dynamically create/configure/verify stubs *and* mocks — hence "isolation," not "mocking."
- Match flavor to target: loose (Jest/Sinon) for modules/functions, typed (substitute.js) for classes/interfaces.
- `jest.fn()` = single-function fake; `jest.mock()` = whole-module fake; `jest.spyOn()` wraps an existing method.
- Stub with `mockReturnValue` (preferred) / `mockReturnValueOnce`; simulate errors with `mockImplementation`.
- Prefer faking *abstractions you control* over directly mocking third-party module APIs.
- Lean on return-value/state tests; keep mocks to one-per-test and ~5% of the suite.
- Never verify a stub or an internal-to-internal call — that's overspecification and fragile.

## Connects To
- **Ch 4** (interaction testing / handwritten fakes): replaces the manual stubs and mocks built by hand there with dynamic equivalents; the stub-incoming / mock-outgoing distinction carries straight over.
- **Ch 6** (async): same `jest.fn()`/`jest.mock()` tools extend to faking and controlling asynchronous dependencies, timers, and entry/adapter seams.
