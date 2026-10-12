# Chapter 4: Interaction testing using mock objects

## Core Idea
Some units of work don't end in a return value or a state change — they end by *calling something you don't control* (a logger, an emailer, a third-party module). Third-party functions don't expose APIs to ask "were you called correctly?", so the only way to test that exit point is to substitute a fake you *can* interrogate. **Interaction testing** verifies how your unit of work sends messages (calls functions, with which arguments) to a dependency beyond its control. The tool for that is the **mock object**: a fake that records the call so you can assert on it. If you never assert on it, it isn't a mock.

## Frameworks Introduced
- **Mock object (handwritten)**: a fake module/object/function that records the arguments of an outgoing call so the test can assert the call happened correctly. Represents an **exit point** — the requirement "it calls X."
  - *When to use*: the unit's outcome is invoking a dependency you don't control. *How*: replace the real dependency with a fake that saves its received args to a variable; assert on that variable last. *Why*: proves the exit point was exercised without coupling to the real dependency's internals.
- **Four injection styles** (same techniques used for stubs): Standard (introduce parameter), Functional (currying / factory higher-order function), Modular (abstract+override module deps via `injectDependencies`/`resetDependencies`), Object-oriented (untyped object or TypeScript interface in the constructor).
  - *When to use*: pick the seam that matches your codebase's paradigm; the mock pattern is identical across all four.
- **Partial mock (Extract and Override)**: instantiate a *real* object, then override just one function (or subclass and override) so part is fake, part is real.
  - *When to use*: legacy code where full injection isn't feasible. *Why beware*: brittle, mixes real logic with fake.

## Key Concepts
- **Interaction testing**: checking what calls a unit of work makes to its outgoing dependencies, and with which arguments.
- **Mock vs stub distinction**: a **mock** breaks an *outgoing* dependency and you *assert* on it; a **stub** breaks an *incoming* dependency, feeds data/behavior in, and you *never* assert on it. Same refactoring, opposite direction of information flow.
- **Exit point types**: a unit of work ends in exactly one of three ways — (1) return value, (2) state change, (3) call to a third party. Interaction testing covers type 3.
- **"Mock = exit point you assert on"**: an object is only a mock by virtue of being asserted against; the same `FakeLogger` can act as a stub in one test and a mock in another.
- **Fake / test double**: umbrella term for anything that isn't real. Name it `Fake`/`Testable` when reusable across roles; name it `mockXxx` in a test to signal "an assertion is coming."
- **Overspecification**: asserting more than the single requirement under test — multiple mocks per test, or asserting against stubs. Couples tests to implementation details and reduces value.
- **One-mock-per-test**: more than one mock means more than one requirement in one test → assertion roulette.
- **Assertion roulette** (Meszaros): when the first mock assertion fails, frameworks stop, so later mocks are never verified — you see only part of the failure.
- **Duck typing**: a fake need only implement the part of the interface the unit actually uses (`info`, not `debug`).
- **Interface Segregation Principle (ISP)**: don't fake fat third-party interfaces directly; wrap them in a small adapter interface you own and shape to your needs.

## Mental Models
- **The doctor seeing 30% of symptoms**: multiple mocks per test = a doctor who can't see the hidden failures behind the first one, and treats the wrong thing.
- **Waypoint vs destination**: stubs are stops *on the way* to the outcome (don't assert); mocks are the *destination* (assert). Direction of data flow tells you which.
- **Assert on behavior, not on the query**: don't mock-assert "we queried the DB"; stub the DB return and assert the resulting behavior change. Querying is an incoming detail.
- **Control + adapt your fakes**: only fake interfaces you (a) control and (b) have trimmed to your unit's needs.

## Code Examples
```js
// Standard style: introduce the logger as a parameter, inject a handwritten mock
const verifyPassword2 = (input, rules, logger) => {
  const failed = rules.map(r => r(input)).filter(r => r === false);
  if (failed.length === 0) { logger.info('PASSED'); return true; }
  logger.info('FAIL'); return false;
};

it('calls the logger with PASSED', () => {
  let written = '';
  const mockLog = { info: (text) => { written = text; } }; // records the arg
  verifyPassword2('anything', [], mockLog);
  expect(written).toMatch(/PASSED/); // assert => this is a mock
});
```
- **What it demonstrates**: the canonical interaction test — inject a fake at the seam, let it capture the outgoing argument, assert on the captured value. The `mockXxx` name warns the reader an assertion is coming; one mock, one requirement.

## Worked Example
Requirement: `verifyPassword` must call the logger with `PASSED` when all rules pass. The real logger writes to files/console — no API to ask "were you called?" So we make the call observable.

1. **Create a seam**: add `logger` as a constructor parameter (OO style).
   ```js
   class PasswordVerifier {
     constructor(rules, logger) { this._rules = rules; this._logger = logger; }
     verify(input) {
       const failed = this._rules.map(r => r(input)).filter(r => r === false);
       if (failed.length === 0) { this._logger.info('PASSED'); return true; }
       this._logger.info('FAIL'); return false;
     }
   }
   ```
2. **Build a recording fake** (duck-typed — only `info`):
   ```js
   class FakeLogger { logged = ''; info(text) { this.logged = text; } }
   ```
3. **Inject, exercise, assert on the recorded argument**:
   ```js
   test('passing scenario calls logger with PASSED', () => {
     const mockLog = new FakeLogger();
     const verifier = new PasswordVerifier([], mockLog);
     verifier.verify('any input');
     expect(mockLog.logged).toMatch(/PASSED/); // the assertion makes it a mock
   });
   ```
`FakeLogger` is just a fake; the *assertion* on `mockLog.logged` is what turns it into a mock for this test. One outgoing call, one assertion, one requirement.

## Key Takeaways
1. Use a mock only for the third exit-point type — a call to a dependency you don't control; for return values and state changes, stay with value/state-based testing.
2. A fake becomes a *mock* the moment you assert on it and a *stub* when you only feed data in; name them (`mockXxx` vs `stubXxx`) so readers know an assertion is (or isn't) coming.
3. Keep at most one mock per test, but allow many stubs — extra mocks mean extra requirements and trigger assertion roulette.
4. Never assert against a stub; verifying an incoming interaction (e.g., "we queried the DB") is overspecification that couples the test to implementation.
5. The injection technique (standard / functional / modular / OO-interface) is a paradigm choice; the recording-and-asserting mock pattern is identical underneath.
6. Don't fake fat third-party interfaces directly — apply ISP and fake a small adapter you own and control, so interface churn touches one file, not every test.
7. Reach for partial mocks (Extract and Override) only for legacy code; mixing real and fake behavior makes tests more brittle.

## Connects To
- **Ch 3**: introduced stubs (incoming dependencies) and the same seam/injection refactorings; Ch 4 reuses them in the opposite direction — outgoing dependencies you assert on. The mock/stub naming discipline started there pays off here.
- **Ch 5**: handwritten mocks become long, repetitive boilerplate for fat interfaces (`IComplicatedLogger`); isolation frameworks (Jest, substitute.js) generate dynamic stubs and mocks at runtime to remove that boilerplate, and show the adapter/ISP solution in practice.
