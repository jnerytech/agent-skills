# Glossary

**ACC matrix** — Attribute-Component-Capability matrix; columns = quality attributes, rows = components, cells = capabilities. Stable structure for organising and risk-scoring test ideas (Ch 1).

**Activation phenomenon** — Letting people speak at the start of a review raises participation and willingness to flag problems (Gawande) (Ch 1).

**Always/never heuristic** — A short session listing absolute truths ("should always", "should never") to surface key risks and hidden assumptions, then trying to refute them (Ch 1).

**Arrange-Act-Assert** — Unit-testing name for the Given-When-Then structure (Ch 2).

**Atomic external resource** — A resource whose appearance guarantees it is complete and ready for use; prevents partial-read flakiness (Ch 3).

**Below the skin of the application** — Driving test set-up/clean-up via service/HTTP/DB calls instead of the UI (Ch 3).

**Black swan** — An unexpected, unknowable incident no regression test prevents; mitigate by training fast reaction (Ch 1).

**Business time** — A domain clock decoupled from the OS clock, controllable in tests, re-runnable in production (Ch 3).

**Capability** — What a feature lets a user do, or prevents; the right focus for exploratory testing (Ch 1).

**Chaos monkey** — Deliberately breaking critical parts to check the suite catches it; risk-driven manual mutation testing (Ch 4).

**Coherence** — One of the three C's: documentation is logical, understandable on its own, and consistent in style/terminology (Ch 2).

**Completeness** — One of the three C's: acceptance tests cover the feature and its integrations; a force, not an absolute goal (Ch 2).

**Conciseness** — One of the three C's: a specification with no repetition, redundancy or overlap (Ch 2).

**Counter-example** — A case showing when a feature does *not* apply; best when inputs are as close as possible to a positive case but yield a different output (Ch 2).

**Coverage (as negative metric)** — Measures how bad something is, not how good; low coverage is informative, high coverage is not (Ch 4).

**Decouple coverage from purpose** — Treat area of coverage (unit/integration/E2E) and purpose (business/technical) as independent dimensions (Ch 4).

**Describe what, not how** — Keep acceptance criteria on purpose/business decisions, not execution mechanics (Ch 2).

**Equivalence class** — A set of inputs (or outputs) treated as interchangeable; reduce classes for *both* inputs and outputs (Ch 2).

**Given-When-Then** — Structural pattern: parameters in Given, single action in When, outcomes in Then; used in strict sequence (Ch 2).

**Half-life of a test** — A test's stability, measured by rate of change (e.g. check-ins over time) (Ch 4).

**Key example** — A small, simple, concrete scenario at the right abstraction that illustrates a business rule (Ch 2).

**Mob testing** — A group (4–8+) designing or running tests together for diverse, rapid idea generation (Ch 1).

**One test, one topic** — Each test covers one action; multiple When clauses or conjunctions signal lack of focus (Ch 2).

**Optimise for reading** — Favour test readability over ease of writing or DRY, because tests inform at first-pass and at failure (Ch 4).

**Page object pattern** — UI-automation pattern; the three-layer approach is a decoupled superset (Ch 3).

**Precondition-Trigger-Postcondition** — Use-case-era name for Given-When-Then (Ch 2).

**Production metrics testing** — Measuring hard-to-test qualities (perf, usability, task time) in production instead of pre-release (Ch 3).

**Quantify even if you can't measure** — Capture expectations as numbers/intervals for hard-to-test qualities (Ch 1).

**Risk checklist** — A 5–9 item list naming key risks (not test steps) for cross-cutting concerns; "Do-Confirm" not "Read-Do" (Ch 1).

**Sampling** — Periodic polling for a condition; good for positive expectations, poor for proving non-occurrence (Ch 3).

**SHADED FIGS** — Emotional test-design heuristic: Scary, Happy, Angry, Delinquent, Embarrassing, Desolate, Forgetful, Indecisive, Greedy, Stressful (Ch 1).

**Three C's** — Conciseness, Completeness, Coherence — competing forces in BDD artifacts (Ch 2).

**Three-layer automation** — Separate business decisions, workflows and technical interactions into reusable layers (Ch 3).

**Trust boundary** — An explicit, group-agreed statement of how much to trust another team/component, setting where defences are needed (Ch 1).

**Wait for events, not time** — Block on an event (queue message, file appears) rather than sleeping a fixed period (Ch 3).

**Write assertions first** — Write outputs/Then clauses (or right-hand table columns) before inputs (Ch 2).
