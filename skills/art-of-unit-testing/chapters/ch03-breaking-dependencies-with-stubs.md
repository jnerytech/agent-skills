# Chapter 3: Breaking dependencies with stubs

## Core Idea
A **stub** is a fake dependency you control that feeds **incoming** (indirect input) data or behavior into your unit of work, so tests become consistent and non-flaky. To insert one, you redesign code to expose a **seam** and **inject** the dependency from the outside instead of letting the code create it internally.

## Frameworks Introduced

- **Two types of dependencies**: Classify every dependency before faking it.
  - When to use: Whenever code touches something outside itself (time, network, filesystem, DB, logger).
  - How: Ask "is this a verb flowing outward (calling/sending/notifying) or passive data flowing inward?" Outgoing = exit point. Incoming = indirect input.
  - Why it works / failure mode: Determines the tool — outgoing dependencies need **mocks** (ch 4); incoming need **stubs**. Mislabeling leads to asserting against stubs (wrong) or having multiple exit points per test.

- **Stub vs mock (test-double vocabulary)**: Stubs break incoming dependencies; mocks break outgoing ones.
  - When to use: Pick the term/role per dependency per test.
  - How: Stubs provide fake data/behavior — you **never assert against them**, and you may have many per test. Mocks represent an exit point — you assert they were called, **at most one per test**.
  - Why it works / failure mode: Calling everything a "mock" creates confusion ("mock database"). When unsure, say **test double** or **fake**. The same fake can act as a stub in one test and a mock in another.

- **Inversion of Control via injection**: Remove a dependency-creation responsibility from the code and externalize it.
  - When to use: When the unit of work itself constructs/chooses an uncontrollable dependency.
  - How: Move creation out to the caller through an **injection point** (a seam): parameter, function, module loader, constructor, or interface.
  - Why it works / failure mode: Whoever creates the dependency has **control** over it; injection hands that control to the test. Failure mode: choosing a seam too tightly coupled to a third-party API (see module injection).

## Key Concepts
- **Dependency**: Something you can't control from a test — time, filesystem, network, randomness.
- **Control**: The ability to instruct a dependency how to behave before the code uses it.
- **Seam**: A place where two pieces of software meet and behavior can be altered without editing that spot (Feathers). Parameters, functions, module loaders, constructors, interfaces.
- **Injection point**: The specific seam through which a dependency is sent in.
- **Dummy**: A bare piece of data with no behavior (e.g., a day integer) — still counts as a stub if it's under your control.
- **Flaky test**: A test that fails only sometimes with no code change (time, network); a prime reason to stub.
- **Duck typing**: If a fake implements the same functions, JS accepts it in place of the real object.
- **Pure function**: No side effects; all dependencies injected — inherently easy to test.

## Mental Models
- **"It just has to be under our control"**: A stub need not be complex. A hardcoded `SUNDAY` integer is a legitimate stub because it removes variability.
- **The pattern is constant; the vocabulary changes**: Parameter, function, factory, constructor, object, interface — all the same injection idea translated into functional or OO style and language features.
- **Factory-as-arrange**: A factory/higher-order function becomes the *arrange* step; calling its returned function becomes the *act* step.
- **Push creation into one place**: A test-side factory function hides how the SUT is constructed, so a constructor-signature change breaks one location, not hundreds of tests.

## Code Examples
```js
// Parameter injection — give the caller (test) control over time
const verifyPassword2 = (input, rules, currentDay) => {
  if ([SATURDAY, SUNDAY].includes(currentDay)) {
    throw Error("It's the weekend!");
  }
  return []; // ...more rules
};

test('on weekends, throws', () => {
  expect(() => verifyPassword2('anything', [], SUNDAY))
    .toThrow("It's the weekend!");
});
```
- **What it demonstrates**: The simplest seam. The function is now pure; the test hardcodes the day, gaining consistency. `currentDay` is a "dummy" we treat as a stub.

## Worked Example
*Constructor injection of a stub object.* Production code declares a `TimeProvider` role and injects it:
```js
class PasswordVerifier {
  constructor(rules, timeProvider) {
    this.rules = rules;
    this.timeProvider = timeProvider;
  }
  verify(input) {
    if ([SATURDAY, SUNDAY].includes(this.timeProvider.getDay())) {
      throw new Error("It's the weekend!");
    }
    return [];
  }
}
// Real wiring lives in a factory, not in the SUT:
const passwordVerifierFactory = (rules) =>
  new PasswordVerifier(rules, new RealTimeProvider());
```
In the test we hand-write a fake with the same signature (**injecting an object instead of a function**) and rely on duck typing:
```js
function FakeTimeProvider(fakeDay) {
  this.getDay = () => fakeDay;
}
test('class constructor: on weekends, throws', () => {
  const verifier = new PasswordVerifier([], new FakeTimeProvider(SUNDAY));
  expect(() => verifier.verify('anything')).toThrow("It's the weekend!");
});
```
With TypeScript we **extract a common interface** (`TimeProviderInterface { getDay(): number }`) so both `RealTimeProvider` and `FakeTimeProvider` `implements` it — now signatures are compiler-checked, not just verified at runtime.

## Key Takeaways
1. Stubs break **incoming** dependencies and are never asserted against; you can have many. Mocks break **outgoing** ones — at most one per test (ch 4).
2. You can't fake a **direct** dependency — you must redesign to create a **seam** first.
3. **Parameter injection** is the cheapest seam; **functional injection** (function-as-parameter, **partial application / factory functions**, **constructor functions**) and **OO injection** (**constructor injection**, **object vs function**, **common interface**) are escalating variants of the same pattern.
4. **Modular injection** (swapping a `require`'d module via an `inject`/`reset` seam) works but is **fragile** — it couples tests to a third-party API. Prefer an interim abstraction you own (Ports & Adapters / Hexagonal) or another injection style.
5. Prefer a **test-side factory function** over IoC containers — readable, and it isolates constructor changes to one place.
6. The "best" style (functional vs OO) is contextual; injection ability is what lets you simulate the otherwise-impossible (errors, weekends).

## Connects To
- **Ch 4**: Mocks and interaction testing — the outgoing-dependency counterpart to stubs; how a fake becomes a mock and what a "fake" is.
- **Ch 5**: Isolation/mocking frameworks (Jest, Sinon, Jasmine) that automate the handwritten stubs and mocks built here.
