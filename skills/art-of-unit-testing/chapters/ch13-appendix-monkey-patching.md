# Appendix: Monkey-patching functions and modules

## Core Idea
Sometimes you can't inject a dependency: the code isn't yours to change, a module exports only functions (no object to swap), or it runs immediately on import. **Monkey-patching** — changing the behavior of a running program at run time — lets you replace a global function or a whole module so your tests can control it. Osherove's stance is blunt: this is a **last resort**. Patching works *around* the design instead of building **seams** *into* it, so the tests it produces are more fragile, harder to read, and prone to leaking dirty global state into other tests. Prefer parameterization and dependency injection; reach for patching only when there is genuinely no other way, and minimize how much you do it.

## Frameworks Introduced
- **CFRA (Clear–Fake–Require–Act)**: the pattern for faking a *module's* data per-test. **When** the code under test destructures a function off a `require`d module (`const { getAllMachines } = require('./mod')`), so normal property patching can't reach it. **How** — (1) **Clear** cached/required modules from runner memory; (2) **Fake** the module so a re-require returns your stub; (3) **Require** the code under test mid-test (not at file top); (4) **Act** — call the entry point. **Why** the module is cached on first import, so without clearing and re-requiring you get the real implementation every time. Skip a step or misorder it and faking silently fails — or worse, *sometimes* works.
- **Jest spyOn + mockImplementation**: **When** patching a global/exported function the Jest way. **How** `jest.spyOn(scope, 'name').mockImplementation(fn)` wraps then replaces it; `jest.restoreAllMocks()` in `afterEach` restores. **Why** `spyOn` alone only *tracks* (it calls the real code); `mockImplementation` is what actually stubs.

## Key Concepts
- **Monkey-patching**: replacing a function's behavior at run time, for a given scope, affecting all code (production and test) from that point on.
- **Seams via patching vs. injected seams**: patching adds a seam implicitly around the code; injection builds it into the code — the latter is cleaner and less brittle.
- **Replacing module exports**: faking a module = faking a global object loaded once on first `import`/`require`.
- **Restoring originals**: always put the original back (`afterEach`, `restoreAllMocks`) or you poison global state for other tests.
- **Why monkey-patching is a last resort**: extra code, extra maintenance, test fragility, parallelism hazards, and cross-test contamination.
- **spy**: an invisible tracking layer on a unit's entry/exit points that records inputs/outputs *without* changing behavior — it still calls the real implementation.
- **`mockImplementation` is mis-named**: it builds stubs *or* mocks; Osherove would call it `fakeImplementation`. Jest overuses "mock."
- **`jest.mock('path')`**: the safest technique here — ignores a whole module wholesale without touching its internals.
- **Module caching**: `require.cache` (vanilla/Jasmine) vs. Jest's own internal cache — Jest ignores `require.cache`.
- **Parallelism risk**: global fakes can collide across parallel test files; `jest --runInBand` forces serial execution.

## Code Examples
```js
describe('findRecentlyRebooted with jest spyOn', () => {
  afterEach(() => jest.restoreAllMocks());      // restore originals

  test('1 of 2 machines under threshold is found', () => {
    const fromDate = new Date(2000, 0, 3);
    Date.now = jest.spyOn(Date, 'now')
                   .mockImplementation(() => fromDate.getTime()); // patch + stub
    const machines = [
      { lastBootTime: new Date(2000, 0, 1), name: 'ignored' },
      { lastBootTime: fromDate,             name: 'found' }];
    const result = findRecentlyRebooted(machines, 1, fromDate);
    expect(result[0].name).toContain('found');
  });
});
```
- **What it demonstrates**: patching the global `Date.now` via `spyOn`+`mockImplementation` to control time, with `restoreAllMocks` guaranteeing the original is restored even if asserts throw.

## Worked Example
Goal: stub `getAllMachines` from a module so `findRecentlyRebooted` sees fake data, then restore. With Jest, lean on CFRA: require the module, declare `jest.mock` above the suite, fake per-test, and clear in `beforeEach`.

```js
const dataModule = require('../my-data-module');
const { findRecentlyRebooted } = require('../machine-scanner');
const fakeData = data => dataModule.getAllMachines.mockImplementation(() => data);

jest.mock('../my-data-module');                 // Fake (whole module)

describe('findRecentlyRebooted', () => {
  beforeEach(jest.resetAllMocks);               // Clear — cleanest reset

  test('given no machines, returns empty', () => {
    fakeData([]);                               // Fake per-test data
    expect(findRecentlyRebooted(0, new Date(2000,0,1)).length).toBe(0);
  }); // Require + Act happen normally at top / in the test
});
```
Note `resetAllMocks` leaves the module *faked* — only the implementation resets, so each test must re-supply its return value or you get strange errors. The vanilla equivalent (`delete require.cache[path]` then re-`require` mid-test) shows the same four steps without a framework.

## Anti-patterns
- **Restoring inside the test body**: if an assert throws, the restore line never runs and the global stays dirty for later tests. Use `afterEach`/`restoreAllMocks`.
- **Faking globals/singletons when a parameter would do**: invites fragility and cross-test coupling; pass the value or a seam instead.
- **Jest manual mocks (`__mocks__` folder)**: hardcoded fake modules in separate files raise scroll fatigue and maintenance cost; control fake data in the test.
- **Relying on `require.cache` under Jest**: Jest ignores it and uses its own cache — the patch silently does nothing.
- **`mockImplementationOnce` for stubs**: caring about call count turns a stub into a mock and makes tests brittle.

## Key Takeaways
- Monkey-patching is a necessary evil — use it only for code you can't change, function-only modules, or immediately-executing code.
- Always restore originals via `afterEach`/`restoreAllMocks`, never inline after the asserts.
- Faking a destructured module function requires CFRA: Clear, Fake, Require (mid-test), Act.
- `jest.mock('path')` to ignore a whole module is the safest patching technique.
- `spyOn` tracks; `mockImplementation` fakes — you need both to stub a global.
- Global fakes endanger parallel runs; there is almost always a cleaner injected-seam alternative.

## Connects To
- **Ch 3**: parameter/constructor injection (cleaner alternatives) — design seams into the code instead of patching around it.
- **Ch 5**: jest.mock as a structured form of patching — and the mocks-vs-stubs distinction `mockImplementation` blurs.
