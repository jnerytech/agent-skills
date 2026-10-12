# Glossary — The Art of Unit Testing (Osherove, 3rd ed)

**AAA (Arrange-Act-Assert)** — three-part test structure: set up state, invoke the unit of work, assert on its exit point (Ch 2).
**Agent of change** — person who champions and drives unit-testing adoption in an organization (Ch 11).
**Always-green test** — a test that can never fail (no real assert, or asserts on a stub); gives false confidence (Ch 7).
**API test** — test that exercises a backend through its public API, out-of-process, without the UI (Ch 10).
**Assertion message** — human-readable text explaining what an assert expected; the only clue left in a CI log (Ch 9).
**Assertion roulette** — multiple asserts in one test so a failure can't tell you which one broke (Ch 2, Ch 8).
**Characterization test** — test written to pin down the current behavior of legacy code before changing it (Ch 12).
**Component test** — test of a single component/module in memory, may touch several units (Ch 10).
**Constructor injection** — supplying a dependency through a class/object constructor (Ch 3).
**Control over the dependency** — the goal of injection: the test, not production wiring, decides what the dependency does (Ch 3).
**CUT / SUT** — Class/System Under Test: the thing being tested (Ch 1).
**DAMP vs DRY** — Descriptive-And-Meaningful-Phrases vs Don't-Repeat-Yourself; tests favor clarity over deduplication (Ch 8).
**Delivery-blocking test** — a test whose failure stops the release; contrast non-blocking "good-to-know" tests (Ch 10).
**Delivery vs discovery pipeline** — fast pipeline that gates releases vs slower one that surfaces information (Ch 10).
**Dependency** — code the unit of work relies on; incoming (drives it) or outgoing (it calls out) (Ch 3).
**Dummy** — a placeholder value/object passed but never used (Ch 3).
**Duck typing** — substituting any object with the right shape, no shared declared type (Ch 3, Ch 4).
**E2E / system test** — test through the full deployed stack, UI to database (Ch 10).
**Entry point** — the public place a test invokes the unit of work (Ch 1).
**Exit point** — observable result of a unit of work; one of: return value, state change, third-party call (Ch 1).
**Extract and Override (partial mock)** — subclass/override a method to fake part of the SUT, for legacy code (Ch 4).
**Extract Adapter** — wrap an external dependency (e.g. fetch) behind a seam you can fake (Ch 6).
**Extract Entry Point** — pull pure logic out of async/I-O code so it can be tested synchronously (Ch 6).
**Factory function** — test helper that builds the SUT with sensible defaults, replacing `beforeEach()` (Ch 2, Ch 8).
**Fake** — generic term for any stand-in (stub or mock) for a real dependency (Ch 3, Ch 4).
**False failure** — a test that breaks on a change that didn't actually break behavior; the maintainability metric (Ch 8).
**False positive / negative** — test passes when code is broken / fails when code is fine (Ch 7).
**Flaky test** — passes and fails non-deterministically without code changes (Ch 3, Ch 7).
**Functional injection** — passing a dependency as a function argument, incl. via partial application (Ch 3).
**Guerrilla implementation** — bottom-up, ask-forgiveness adoption of testing (Ch 11).
**Happy path** — the expected, no-error scenario for a feature (Ch 10).
**Integration test** — test that uses a real (uncontrolled) dependency; not repeatable/fast like a unit test (Ch 1, Ch 10).
**Isolation framework** — library that dynamically creates stubs/mocks (Jest, Sinon, substitute.js); Osherove avoids "mocking framework" (Ch 5).
**Legacy code** — code without tests (Ch 12).
**Magic value (witchcraft value)** — an unexplained literal in a test that hides intent (Ch 9).
**Maintainability** — second pillar: how rarely tests force unnecessary changes (Ch 8).
**Mock object** — a fake you assert against; stands in for an exit point (third-party call) (Ch 4).
**Modular injection** — replacing a module's exported function via the module seam, then resetting it (Ch 3).
**Monkey-patching** — replacing a function/module member at runtime to fake it; last-resort seam (Appendix).
**Overspecification** — asserting on more than the one relevant behavior, making tests fragile (Ch 4, Ch 8).
**Parameter injection** — passing a dependency (e.g. current time) as a plain argument (Ch 3).
**Parameterized test** — one test body run over many input/expectation pairs (`test.each`) (Ch 2, Ch 8).
**Partial application** — pre-binding some function args to produce a simpler injectable function (Ch 3).
**Reporter** — framework part that formats and outputs test results (Ch 2).
**Runner** — framework part that finds and executes tests (Ch 2).
**Readability** — third pillar: a test that explains itself to the next reader (Ch 9).
**Seam** — a place you can change behavior without editing the code there (Feathers); the hook for faking (Ch 3, Ch 6, Ch 12).
**Spy** — a stub that also records how it was called (Ch 4, Ch 5).
**Stub** — a fake that feeds the SUT canned inputs; you never assert on it (Ch 3).
**TAP** — Test Anything Protocol, a test-output format (Ch 2).
**TDD (Red-Green-Refactor)** — write a failing test, make it pass, refactor; not a substitute for good tests (Ch 1).
**Test categories** — grouping tests (e.g. by speed/level) to run subsets (Ch 2).
**Test double** — umbrella term for stubs, mocks, fakes, spies, dummies (Ch 3).
**Test recipe** — a plan stating which levels test which parts of a feature (Ch 10).
**Test with logic** — a test containing conditionals/loops/computed expected values; untrustworthy (Ch 7).
**Three pillars** — trustworthiness, maintainability, readability: the goals of a good test (Ch 7–9).
**Three core skills of TDD** — write a good test, write it test-first, design (refactor) well (Ch 1).
**Trustworthy test** — one you believe when it's green and when it's red (Ch 7).
**Unit of work** — all code run between an entry point and its resulting exit point(s) (Ch 1).
**Unit test** — fast, in-memory, repeatable, isolated test of a unit of work via one exit point (Ch 1).
**USE naming** — test name states Unit under test, Scenario, Expectation (Ch 2, Ch 9).
**xUnit** — family of test frameworks (JUnit, NUnit, Jest-style) sharing structure (Ch 2).
