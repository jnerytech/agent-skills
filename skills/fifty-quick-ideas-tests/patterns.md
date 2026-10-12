# Patterns & Techniques

## Big-Picture Quality Pyramid
**When to use**: Milestone kick-off; aligning developers/testers/analysts/business on what "quality" means.
**How**: Draw 5 levels — (1) works at all, (2) works well, (3) usable, (4) useful, (5) successful. Add expectations on sticky notes per level, then quantify each.
**Trade-offs**: Higher levels often not testable pre-release, but guide design and exploratory testing.

## Explore Capabilities, Not Features
**When to use**: Designing exploratory sessions.
**How**: Brainstorm what a feature allows/prevents; use impact-map actor impacts or story-map spine. Focus on the "in order to" (value), not "I want" (feature).
**Trade-offs**: Wider scope than a feature, but still focused enough to avoid losing direction.

## Always/Never + Refutation
**How**: 10-min silent brainstorm of absolutes per group; merge; then attack each statement with counter-examples. Survivors → keep challenge scenarios as tests; refuted ones → critical test cases.

## SHADED FIGS Emotional Heuristic
**How**: Start at the happy path, then walk the other 8 paths (scary/angry/delinquent/embarrassing/desolate/forgetful/indecisive/greedy/stressful) looking for risks. Best in a multi-person workshop.

## ACC Matrix
**How**: Columns = quality attributes, rows = components, cells = capabilities (user-facing actions, testable, not full test cases). Risk-score each capability with stakeholders. Use change-impact links to decide what to retest.
**Trade-offs**: Capabilities are the hard part to identify; attributes/components stay stable.

## Risk Checklists (Cross-Cutting Concerns)
**How**: Name key *risks* (not scenarios), 5–9 per list, one list per concern. Use as "Do-Confirm" (work, then review), never "Read-Do".

## Focus on Key Examples
**How (4 complexity strategies)**: 1. Find missing concepts; 2. Group by commonality, show only variations; 3. Split validation from processing; 4. Summarise & explore boundaries. Aim for ~5 examples per rule group.
**Trade-offs**: Don't try to replace all testing with examples — aim for shared understanding.

## Contrast With Counter-Examples
**How**: Write simplest positive as a table row; for each output, reach a different value via the smallest input change; repeat until every output value has a row. Counter-examples should sit close to positives.

## Given-When-Then (Strict Sequence)
**How**: Parameters → Given (past tense, passive); single action → When (present, active); outcomes → Then (future, passive). One When per scenario.
**Trade-offs**: A sharp tool — misuse creates long unmaintainable tests.

## Flip Equivalence Classes (Inputs ↔ Outputs)
**How**: Split into two groups — one designs input classes, one output classes. Heuristic: input equivalence for valid cases, output equivalence (every error message) for invalid cases. Cover secondary outputs: validation, audit trails, alerts, post-processing.

## Write Assertions First
**How**: Write Then clauses / right-hand table columns first, then explain how to reach them. Iterate between outputs and inputs; never a single top-down pass.

## Treat Boundaries as a Modelling Problem
**How**: Design test cases before coding; if a small set of key examples can't describe the model, try 3–4 alternative models and pick the one with fewest scenarios / clearest structure. Look for hidden domain concepts.

## Split Technical & Business Checks
**How**: For each test ask "who resolves a failure?" — programmer → technical group; business → business group; both → split. Keep business tests human-readable, technical tests in code.

## Wrap Synchronous DB Tests in Transactions
**How**: Globally wrap the runner to begin a transaction and roll back at the end. Synchronous, single-process only.
**Trade-offs**: One uncontrolled test corrupts many — must be global, not per-test.

## Set Up Before Async Tests, Don't Clean Up After
**How**: Make set-up defensive (check state, alert on inconsistency). Use version checks/checksums to skip expensive truncation. Clean-up only for optimistic resource de-allocation.

## Introduce Business Time
**How**: Application-clock component; tests move it instantly. Fallback: set test-machine system clock (single box, time-tolerant third parties only).

## Provide Atomic External Resources
**How (preference order)**: temp-name-then-rename → create/move across folders → marker file/queue message → exclusive write lock → existence + growth check.

## Wait for Events, Not Time
**How**: Use completion notifications; make remote processes emit events/logs; else sample every ~100ms. Sampling can't prove non-occurrence — use "ask what happens instead?".

## Three-Layer Automation
**When to use**: UI is the only way to drive the test.
**How**: business decisions → reuse workflow components → reuse technical-interaction components. Localises change to one layer.
**Trade-offs**: Don't push all layers into plain-text spec tools — you lose refactoring/compilation support.

## Minimise UI Interactions
**How**: Rephrase UI examples as business-domain concepts; pull set-up/clean-up below the skin (HTTP/DB); add a test-only control interface (TCP/web service) for app state. Keep UI actions only for UI-specific risk.

## Use Production Metrics for Expensive Tests
**How**: State expectations as usual, but verify in production (e.g. Google Analytics, custom monitoring). Design software upfront to emit the metrics. Don't call a story done until verified.

## Make Developers Responsible for Checking
**How**: Whole team decides *what* to test; developers automate; experts only teach tools; pair testers+developers to de-risk.

## Decouple Coverage From Purpose
**How**: Decide purpose first (drives format/tool), then choose the minimal coverage area. Allows business-oriented unit tests and technical end-to-end checks. Split tests into libraries so groups run in isolation.

## Coverage as Diagnostic, Not Target
**How**: Use coverage to find gaps; don't publish it. If forced, use multiple dimensions (Copeland's 7 levels). Combine with human judgement (e.g. exploratory sessions scoped by risk/capability).

## Measure Test Half-Life
**How**: Store tests in VCS; count check-ins/interval; heat-map change & failures by feature. Diagnose: volatile area vs weak/buggy area vs fragile tests.

## Chaos Monkey (Risk-Driven)
**How**: Schedule, time-box, agree key risks (reuse ACC routes); break critical parts and run tests; silence ⇒ write more tests; blameless post-mortem. Drive mutations from risk, not technical code analysis.

## Organise Tests by Business Activity
**How**: Structure by user activities / workflows / transaction types, not work items. Move tests out of the task tracker once a story is accepted; link with tags, avoid duplication.

## Version Control Tests With Software
**How**: Keep tests in the same VCS as code. If a tool uses a binary DB, sync via text export/import on the build server.

## Gallery of Automation Patterns
**How**: Separate, searchable hierarchy of example tests that demonstrate how to automate things (they test nothing). Prevents divergent duplicate approaches; promotes common domain language.

## Split Just-in-Case Tests From Key Examples
**How**: Separate document/hierarchy for extra technical edge cases, cross-linked, **reusing the same automation**. Run key examples in the primary CI job, extras as secondary/overnight jobs.
