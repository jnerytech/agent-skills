# Glossary — Unit Testing Principles, Practices, and Patterns

**AAA (Arrange, Act, Assert)** — the three-section structure of a unit test: set up the SUT and dependencies, invoke the behavior, verify the outcome (Ch 3).

**Ambient Context** — anti-pattern of accessing a dependency (e.g. current time) via a static/global instead of an explicit parameter; hurts testability (Ch 11).

**Black-box testing** — testing through the public API without knowledge of internals; the default for writing tests (Ch 4).

**Branch coverage** — coverage metric counting exercised control-flow branches; better than code coverage but still a poor target/goal (Ch 1).

**Brittle test** — a test that fails on refactoring without a real bug; a false positive; low resistance to refactoring (Ch 4, Ch 5).

**Classical (Detroit) school** — school of unit testing that isolates *tests* from each other (not classes), uses real collaborators, mocks only shared dependencies (Ch 2).

**Code coverage** — ratio of executed lines to total; a *negative* indicator only — low is bad, high proves nothing (Ch 1).

**Code pollution** — anti-pattern of adding production code (e.g. test-only flags) that exists only to support testing (Ch 11).

**Collaborator** — a dependency that is either shared or mutable (out-of-process); distinct from a value (Ch 2, Ch 6).

**Command Query Separation (CQS)** — methods are either commands (side effects, return void) or queries (return value, no side effects); never both (Ch 5).

**Communication-based testing** — verifying interactions (mocks) between the SUT and collaborators (Ch 6).

**Controller** — code that orchestrates between domain model and out-of-process dependencies; one corner of the types-of-code quadrant (Ch 7).

**Domain model and algorithms** — high-complexity, low-collaborator code; the prime target for unit testing; the most valuable quadrant (Ch 7).

**End-to-end test** — test running the full system including all out-of-process dependencies; a subset of integration tests (Ch 2, Ch 8).

**Fail fast principle** — surface errors immediately (exceptions, preconditions) rather than testing edge cases that crash on their own (Ch 8).

**False negative** — a test that stays green despite a real bug; weak protection against regressions (Ch 4).

**False positive** — a test that fails without a real bug; a false alarm; the enemy of resistance to refactoring (Ch 4).

**Fast feedback** — pillar: the speed at which a test runs and reports (Ch 4).

**Functional architecture** — "functional core, mutable shell": isolate side-effect-free business logic from a thin shell that talks to the world (Ch 6).

**Hexagonal architecture** — domain surrounded by application services; distinguishes internal vs external communications (Ch 5).

**Humble Object pattern** — extract testable logic out of a hard-to-test class (UI, DB, async), leaving a thin humble wrapper (Ch 7, Ch 11).

**Implementation detail** — internal mechanics not part of observable behavior; asserting on them causes brittleness (Ch 5).

**Integration test** — test that touches an out-of-process dependency or fails the unit-test definition (not isolated, slow) (Ch 2, Ch 8).

**Isolation issue** — what each school isolates: classical isolates tests; London isolates the SUT class via mocks (Ch 2).

**London (mockist) school** — isolates the SUT from all collaborators with mocks; one-class-per-test granularity (Ch 2).

**Maintainability** — pillar: how hard a test is to read and run (test size + dependency complexity) (Ch 4).

**Managed dependency** — out-of-process dependency only your app accesses (e.g. application database); use the real thing in integration tests (Ch 8).

**Migration-based database delivery** — version the DB schema as ordered, immutable migration scripts; preferred over state-based (Ch 10).

**Mock** — test double that verifies outgoing interactions (commands); also the broad term for any test double in casual use (Ch 2, Ch 5).

**Observable behavior** — operations and state meaningful to a client (public API contract); the only thing tests should assert on (Ch 5).

**Out-of-process dependency** — runs outside the process (DB, message bus, SMTP, filesystem); managed or unmanaged (Ch 2, Ch 8).

**Output-based testing** — feed input, assert on the returned value; the most robust style; requires functional code (Ch 6).

**Overspecification** — asserting on more than observable behavior (e.g. interactions with stubs); a brittleness source (Ch 5).

**Private dependency** — a dependency used by a single test/SUT; the classical school uses real ones (Ch 2).

**Protection against regressions** — pillar: a test's ability to catch real bugs (Ch 1, Ch 4).

**Reference data** — data the app needs to function (lookup tables); part of the schema, kept in source control (Ch 10).

**Resistance to refactoring** — pillar: not failing when behavior is unchanged; the non-negotiable pillar (Ch 4).

**Shared dependency** — dependency shared between tests, enabling them to affect each other (static, DB, filesystem); mock or isolate (Ch 2).

**Spy** — handwritten mock; preferred at the system edge for fluent, reusable verification (Ch 5, Ch 9).

**State-based testing** — assert on the SUT/collaborator state after the act (Ch 6).

**State-based database delivery** — keep the whole DB state in source control and diff to deploy; inferior to migration-based (Ch 10).

**Stub** — test double that provides canned inputs (queries); never assert on a stub (Ch 5).

**Sustainable growth** — the goal of unit testing: enabling a project to keep growing without slowing down (Ch 1).

**SUT (System Under Test)** — the unit of behavior a test exercises; aka MUT (method under test) (Ch 3).

**Test accuracy** — signal-to-noise: true-positive rate vs false-positive rate; maximized by killing brittleness (Ch 4).

**Test data life cycle** — clean leftover data at the *start* of each integration test, not the end; no shared in-memory state (Ch 10).

**Test double** — umbrella term for any stand-in: stub, mock, spy, dummy, fake (Ch 2, Ch 5).

**Test fixture** — object reused as a known starting state across tests; prefer private factory methods over shared mutable fields (Ch 3).

**Test Pyramid** — many fast unit tests, fewer integration, fewest E2E (Ch 4, Ch 8).

**Trivial code** — low complexity, low collaborators (getters/setters); not worth testing (Ch 7).

**Types-of-code quadrant** — complexity/domain-significance × number of collaborators → domain model, trivial, controllers, overcomplicated (Ch 7).

**Unit of behavior** — what a unit test verifies; a behavior, not a class or method (Ch 2, Ch 3).

**Unmanaged dependency** — out-of-process dependency visible to other apps (message bus, SMTP); mock it to preserve the contract (Ch 8).

**Value object** — immutable object with no identity, compared by value; safe to use as a real collaborator (Ch 2, Ch 6).

**White-box testing** — testing with knowledge of internals; use to *analyze* coverage, never to *write* tests (Ch 4).
