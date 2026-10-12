# Chapter 6: Unit testing asynchronous code

## Core Idea
Async code is hard to test not because it's async, but because the async I/O is *tangled with* the pure logic that processes its results. The fix is **separating async from logic**: pull the inherently asynchronous piece (a fetch, a timer) out of the way so the decision-making becomes a synchronous, value-based unit of work. You keep one or two integration tests for orchestration, and cover every other scenario with fast, deterministic unit tests.

## Frameworks Introduced
- **Extract Entry Point**: formulation — split an async unit of work into the async part (left intact) and the result-handling logic, which you externalize as new functions. / **When**: the async orchestration is fine but the branching logic inside `.then`/`catch` (or after `await`) needs many test cases. / **How**: move success-handling and error-handling code into `processFetchSuccess(text)` / `processFetchError(err)`; export them; the original `isWebsiteAlive` just wires them together. / **Why**: the new entry points run synchronously with simulated inputs — no network, no waiting, no flakiness. Prefer returning values over invoking callbacks.
- **Extract Adapter (seam for fetch)**: formulation — treat the async dependency like any other dependency; wrap it behind a narrow adapter you can fake. / **When**: you want to keep the original entry point but control the I/O. / **How**: a `network-adapter` module is the *only* place importing `node-fetch`, exposing a simplified `fetchUrlText(url)` returning `{ok, text}`; inject it (modular via `jest.mock`, functional via a parameter, or OO via constructor + interface). / **Why**: the seam isolates the unmanaged dependency and applies interface segregation — the consumer sees only what it needs.

## Key Concepts
- **Async unit of work**: has entry and exit points like any unit of work, but the exit may be a callback, a resolved promise, or an emitted event (see fig 6.1).
- **Waiting for the act**: with callback exit points the test must explicitly wait; Jest's `done()` signals "don't finish until I call this," timing out (default 5s) otherwise.
- **`async`/`await` in tests**: since await is sugar over promises, an `async` test function with `const r = await fn()` restores plain Arrange-Act-Assert readability vs. `.then(done)` chains.
- **Integration vs unit for async**: an awaited call is still async underneath, so it's still an integration test — slow, flaky, tests irrelevant code/environment, harder to simulate failures, harder to trust.
- **`done()` even when synchronous**: extracted callback entry points run linearly, but `done()` still guards against a callback that never fires (a passing-by-silence false positive).
- **Three injection styles for the adapter**: modular (`jest.mock` the file), functional (pass adapter as a parameter, build fakes with a `makeStubNetworkWithResult` helper), object-oriented (constructor injection against an `INetworkAdapter` interface, faked with substitute.js).
- **Naming the fake `stubSyncNetwork`**: makes the synchronous nature of the test obvious, since `await` alone hides whether code runs linearly or asynchronously.
- **Fake timers**: `jest.useFakeTimers` stubs `setTimeout`/`setInterval`; `jest.advanceTimersToNextTimer` triggers pending callbacks step by step (essential for recursive timers).
- **Monkey-patching timers**: save the original `setTimeout`, replace it with `(cb) => cb()` for synchronous execution, restore in `afterEach` — works but is boilerplate-heavy and error-prone.
- **Events tested by end result**: verify the observable state change (an emitted value, a changed DOM element), not merely that an event fired.

## Mental Models
- **The async is the dependency**: a fetch or timer is just an unmanaged dependency you want under control — extract a seam and the problem reduces to ones from Ch 3.
- **Logic is synchronous; only the plumbing is async**: once you carve the decision-making away from the I/O, "testing async code" collapses into ordinary value-based testing.
- **Test pyramid for async**: a thin layer of one-or-two integration tests proves orchestration; the broad base of fast unit tests proves every branch. Don't pay integration cost for logic coverage.
- **Test the exit point users care about**: for UI/events, the meaningful exit point is the visible state change, not the event firing — couple tests to observable behavior, not internal wiring.

## Code Examples
```js
// Extracted entry point + adapter, tested synchronously with await
jest.mock("./network-adapter");
const stubSyncNetwork = require("./network-adapter");
const webverifier = require("./website-verifier");

describe("website verifier", () => {
  beforeEach(jest.resetAllMocks);
  test("good content returns true", async () => {
    stubSyncNetwork.fetchUrlText.mockReturnValue({ ok: true, text: "illustrative" });
    const result = await webverifier.isWebsiteAlive();
    expect(result.success).toBe(true);
    expect(result.status).toBe("ok");
  });
});
```
- **What it demonstrates**: `await` keeps AAA readability while the faked adapter makes the call run linearly — "async-friendly signature, synchronous execution." The fake's name flags that nothing truly waits.

## Worked Example
Start with `isWebsiteAlive()` that fetches `example.com`, checks the body for `"illustrative"`, and returns `{success, status}` — all tangled in one async function. The only obvious test is a NETWORK-REQUIRED integration test: slow, flaky, can't simulate "text missing" or "site down" without real conditions.

**Extract the seam.** Apply Extract Adapter: create a `network-adapter` module — the sole importer of `node-fetch` — exposing `fetchUrlText(url)` that returns `{ok, text}`. `isWebsiteAlive` now `await`s the adapter and delegates branching to extracted entry points `processFetchSuccess(text)` / `processFetchError(err)`.

**Test synchronously.** Inject a `stubSyncNetwork` returning `{ok: true, text: "illustrative"}` → expect `success: true`; return bad content → expect `"missing text"`; reject → expect failure. Every scenario is now a fast unit test. Keep exactly one integration test to confirm the real fetch wiring works. Result: confidence without sacrificing speed or stability.

## Key Takeaways
- Testing async code directly yields slow, flaky tests; the cure is structural, not a framework trick.
- **Extract Entry Point** when the logic needs coverage; **Extract Adapter** when you want to control the I/O — both turn async problems into synchronous value-based tests.
- Prefer returning values over callbacks; with `async`/`await` your tests read like ordinary AAA.
- Keep integration tests few — just enough to verify orchestration — and push scenario coverage down to unit tests.
- Control timers with `jest.useFakeTimers` + `advanceTimersToNextTimer` rather than waiting real time; monkey-patching works but costs boilerplate.
- Test events and UI by asserting the observable end result, not that an event fired — this keeps tests decoupled from implementation.

## Connects To
- **Ch 3**: the adapter is a seam and the injection styles (modular/functional/OO constructor) are the same dependency-breaking and stub/mock techniques applied to an async dependency.
- **Ch 7**: integration-test flakiness, trust in failing tests, and the broader strategy of balancing test levels are picked up where this chapter's caveats leave off.
