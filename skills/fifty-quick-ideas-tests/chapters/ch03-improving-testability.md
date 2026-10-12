# Chapter 3: Improving Testability

## Core Idea
Architectural and modelling tricks that make software easier to *observe* and *control*, so automated tests become reliable and cheap. Most flakiness comes from time, asynchrony, shared data and the UI — design those problems away rather than papering over them with sleeps and retries.

## Frameworks Introduced

- **Wrap synchronous database tests in transactions**: start a transaction, run the test, roll back.
  - When to use: activity under test is synchronous and single-process.
  - How: do it *globally* in the test framework (a wrapper around the runner), not per-test — one uncontrolled test can corrupt thousands.
  - Why it works: DB isolates transactions → parallel runs; rollback = instant clean-up, instant repeatability (no leftover users/funds).

- **Set up before asynchronous data tests, don't clean up after**: ensure consistent state in *set-up*, not teardown.
  - Why it works: clean-up is written for the passing path and is skipped on failure/interruption; set-up that's defensive isolates failures (investigate 1 test, not 500) and preserves failure evidence.
  - How: set-up checks state, alerts on inconsistency rather than running on bad state; use version checks/checksums to short-circuit expensive truncation; use clean-up only for optimistic resource de-allocation.

- **Introduce business time**: an application-clock component all code uses instead of the OS clock.
  - When to use: animations/timeouts, overnight jobs, expiry rules, "yesterday"/"last month" reports.
  - How: components read the app clock; tests move it forward/back instantly (299ms → check disabled, +1ms → check enabled). Fallback if stack isn't fully yours: set the test machine's system clock (only if whole stack runs on one box and third parties survive time going backwards).

- **Provide atomic external resources**: a resource's *appearance* must mean it's *ready*.
  - When to use: files/resources created asynchronously or transferred over networks.
  - How (in order of preference): 1. write under temp name, rename on close (rename is atomic); 2. create in one folder, move to another; 3. separate marker file / queue message signalling completion; 4. exclusive write-lock; 5. (last resort) check existence then watch if file is still growing.

- **Wait for events, not time**: block on an event (message on queue, file appears) instead of sleeping N seconds.
  - Why it works: any fixed wait is too short (flicker) or too long (slow feedback); events adapt to slow networks/busy machines. Saves hours across large suites.
  - How: use completion notifications; if remote process isn't yours, make it emit an event/log you can watch; else *sample* (poll every 100ms) — but sampling can't prove something *didn't* happen (use "what happens instead?").

- **Three-layer automation**: separate **business decisions / workflows / technical interactions** into layers.
  - When to use: UI is the only way to drive a test (legacy logic in UI, opaque third-party component).
  - How: business-decision tests reuse workflow components, which reuse technical-interaction components. A button→hyperlink change touches only one technical activity; a workflow step change touches only the workflow. Superset of the page-object pattern (decouples workflow change too).

## Key Concepts
- **Atomic resource**: one whose visibility guarantees completeness.
- **Sampling / periodic checking**: polling for a condition; good for "expect X", poor for "expect not-X".
- **Business time**: domain clock decoupled from OS clock, controllable in tests and re-runnable in production.
- **Below the skin of the application**: driving set-up via HTTP/service/DB calls instead of the UI.
- **Split data generators from tests**: build generators as separate libraries/processes; the test just says "100,000 trades".

## Mental Models
- **Time-based waiting = waiting in the rain for a pizza** that already arrived by another road — wait *for the delivery* (event), not a fixed time.
- **In-memory DB ≠ production DB**: HSQLDB-vs-Oracle SQL syntax differences make such tests "worse than no automation" (misleading green).
- **Minimise UI interactions**: rephrase UI examples as business-domain concepts; keep UI actions only for UI-specific risks. UI is slowest, most brittle, full-stack-constrained, and needs a human eye anyway.
- **Use production metrics for expensive tests**: when something is hard to test pre-release, measure it in production (perf, usability, task time) — only ~⅓ of shipped ideas actually improve their target metric.

## Anti-patterns
- **`Thread.sleep(300)` / fixed waits**: non-deterministic, environment-dependent, accumulates to hours across the suite.
- **Magic time constants** (`ONE_MONTH_AGO`): hide leap-year/DST/timezone assumptions (what *is* one month ago on 30 March?).
- **Per-test clean-up you depend on**: skipped on failure → cascading false alarms; destroys failure evidence.
- **Checking only that a file exists**: partial-transfer reads → "works on my machine" non-reproducible bugs.
- **Run-it-5-times-and-pass-if-any**: masks real defects, multiplies feedback time, doesn't guarantee accuracy.
- **Record-and-replay UI scripts**: brittle, unmaintainable, force tiny test subsets.
- **Generators welded into each test**: duplicated everywhere → maintenance pain.

## Worked Example
**Killing a 90-second set-up.** A client's tests each began by launching an admin app, registering a user, approving the account, registering and approving a payment card, then transferring money — ~90 seconds per test — purely to get *a valid customer account with $100*. The delivery team replaced the whole UI dance with one step, **"Given a valid customer account with 100 USD"**, executed directly against the database. Account creation dropped from 90 seconds to milliseconds, with no loss of risk coverage and *more* reliable tests. The UI risk wasn't being tested by that set-up, so the UI didn't belong in it.

## Key Takeaways
1. Isolate DB tests with transaction rollback (set globally) for parallelism and free clean-up.
2. For async/distributed data, clean up in *set-up*, never depend on teardown.
3. Decouple from the OS clock with a business-time component; control time instantly in tests.
4. Make async resources atomic — appearance ⇒ readiness — to kill partial-read flakiness.
5. Wait for events, not fixed time; fall back to sampling only for positive expectations.
6. Pull set-up/clean-up "below the skin", keep the UI only for UI-specific risk; use the three-layer pattern when UI driving is unavoidable.
7. Some valuable tests are only feasible in production — extend the test strategy to production metrics.

## Connects To
- **Ch 2**: "minimise UI interactions" applies "describe what, not how"; "wait for events" pairs with "ask what happens instead?" ([[ch02-designing-good-checks]]).
- **Ch 1**: production metrics map to the top of the quality pyramid ([[ch01-generating-test-ideas]]).
- **Ch 4**: three-layer automation supports the "gallery of automation patterns" ([[ch04-managing-large-test-suites]]).
- **Page Object pattern**: three-layer automation is a decoupled superset.
- **Netflix Chaos Monkey**: production-resilience inspiration (revisited in Ch 4).
