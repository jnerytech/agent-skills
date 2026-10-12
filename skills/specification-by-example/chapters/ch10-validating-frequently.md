# Chapter 10: Validating frequently

## Core Idea
Once the right product is built, executable specifications must be validated frequently — like Botts' Dots that rumble when you drift — so the system stays right and small problems get caught while they're still cheap. On brownfield systems this adds three challenges over ordinary CI: environmental unreliability, slow feedback, and managing tests you can't fix immediately.

## Frameworks Introduced

### Theme 1 — Reducing unreliability

- **Find the most annoying thing, fix it, and repeat**: incrementally remove sources of instability rather than one big rewrite.
  - When: Working on a system with bad automated test support.
  - How: Pick the single worst flake, fix it; the next worst surfaces; repeat. Legacy systems won't become testable overnight, and big simultaneous changes destabilize an already-untested system. (McLennan: timeouts → DB perf → stale-data messaging → cookie-expiry → business time.)

- **Identify unstable tests using CI test history**: let the build server's test-result tracking tell you where to start.
  - When: Retrofitting automated testing into a legacy system.
  - How: Plug specs into the continuous-build system; read the run history to find which tests/groups fail most often; fix those first. (Useless on greenfield where tests almost always pass — only pays off on flaky retrofits.)

- **Set up a dedicated continuous validation environment**: secure machines used only for continuous validation.
  - How: Don't share one environment across demos, manual testing, and continuous validation — that causes data-consistency issues. A dedicated environment eliminates unplanned changes and tells you a failure is a real bug, not someone poking the box.

- **Employ fully automated deployment**: deploy in a single reproducible on-demand procedure with zero manual steps.
  - How: One standard upgrade procedure, identical layout on dev and test environments. Fully automated means *fully* — no admin-console clicking, no half-automated scripts, and crucially no manual database scripts afterward. (On-demand executable; not necessarily auto-triggered.)

- **Create simpler test doubles for external systems**: replace flaky external dependencies with a fake you control.
  - When: Working with external reference data sources.
  - How: A separate fake reads reference data from a version-controlled file (e.g. XML) instead of calling the real service. Gives availability, full control of data (no expiry surprises), speed, and version-matched test data. Periodically check the double still matches the real system. (Park's auto-policy server.)

- **Selectively isolate external systems**: turn off only the external services irrelevant to a given spec's goal.
  - When: External systems participate in work (provide more than reference data).
  - How: Don't fully fake systems whose real functionality matters. Per spec, disable the minimal set so each test still exercises the minimum real externals. Faster, and a failure clearly implicates the one remaining dependency. (Cooper, Beazley.)

- **Try multistage validation**: each team validates locally first, then pushes to a shared central environment.
  - When: Large/multisite groups.
  - How: Each team has its own continuous-validation environment; integrate intra-team changes there first, then push to central where all teams integrate. Stops one team's breakage from blocking everyone; teams keep working when central is broken. Run full pack in both, or a smoke subset in one for speed.

- **Execute tests in transactions**: run each test in a DB transaction and roll back at the end.
  - When: Executable specifications modify reference data.
  - How: Rollback keeps test runs independent (e.g. avoids unique-constraint failures on re-run) and isolates concurrent processes. Keep transaction control in the automation layer, not in the spec. Caveats: deferred constraint checks / nested autonomous transactions may not work.

- **Run quick checks for reference data**: a separate fast pack that verifies reference data is still as expected.
  - When: Data-driven systems.
  - How: Run it before the executable specs; if it fails, skip the rest. Pinpoints reference-data/config problems fast instead of mysterious spec failures.

- **Wait for events, not for elapsed time**: block on a message/poll instead of `Wait 10 seconds`.
  - How: Fixed sleeps fail under load, become environment-dependent, and inflate feedback time (50s wasted × 20 tests = 15+ min). Block on a queue or poll a DB/service in the background until the process actually finishes.

- **Make asynchronous processing optional**: configure the system to run processes synchronously under test.
  - When: Greenfield projects.
  - How: Toggle between queueing and direct execution; run continuous validation synchronously for reliable, fast specs. Trade-off: it no longer tests end-to-end, so add short focused technical tests that async wiring works.

- **Don't use executable specifications as end-to-end validations**: stop overloading one big spec with business logic + integration + wiring.
  - When: Brownfield projects.
  - How: (1) Separate business logic from infrastructure code; (2) spec/test business logic per step in isolation, synchronously, no real DB/queue; (3) add simple technical integration tests for infrastructure; (4) keep one end-to-end test that proves all components talk (touches everything, blocks on queue / polls DB). Moving down the list: fewer tests, slower each.

### Theme 2 — Getting feedback faster

- **Introduce business time**: a configurable replacement for the system clock.
  - When: Working with temporal constraints.
  - How: System asks the "business clock" for now, so tests time-travel instantly (no waiting for midnight jobs, cache windows, or contract expiry). Quick-and-dirty: change the test-box clock (beware time caching / confusing reports). Robust: build it into production code. Watch for sync issues with external systems — apply doubles/isolation.

- **Break long test packs into smaller modules**: split one giant pack into several smaller ones by functional area.
  - How: Prefer 12 packs ≤30 min over one 6-hour pack. Rerun just the relevant area; spot a 10-min regression that's invisible across 6 hours but obvious across 30 min. (Author cut a client's area from ~1 hour to 9 min.)

- **Avoid using in-memory databases for testing**: keep the real DB instead of swapping in an in-memory engine.
  - When: Data-driven systems.
  - How: A DB-backed spec is also an integration test — SQL-dialect differences make in-memory results misleading and force maintaining two SQL/data sets. Slow tests on realistic data warn of slow production. Prefer transactions for isolation; if mixing test types, use the real DB and speed it up (indexes). (Iowa Student Loan dropped Hypersonic: saved 2 of 45 min, more maintenance.) In-memory is fine for DB-agnostic checks.

- **Separate quick and slow tests**: group specs by execution speed; run the quick ones often.
  - When: A small number of tests take most of the time to execute.
  - How: e.g. RainStor — functional pack <1h after each build, customer scenarios overnight, long-running suites every weekend. Less than full validation each time, but quick feedback with much lower risk.

- **Keep overnight packs stable**: only add tests to overnight packs once they're unlikely to fail.
  - When: Slow tests run only overnight.
  - How: A flaky overnight failure masks other problems and burns a full day per fix cycle. Move failing tests to a known-regression pack; promote a spec into the overnight pack only after it's passed reliably for a while (use run history). Run unstable ones manually/on-demand until stable. (Knight, RainStor.)

- **Create a current iteration pack**: a separate pack of specs affected by the current development phase.
  - How: Fast feedback on the most volatile, most important area. Can include specs for planned-but-unimplemented features to track progress and know when you're done; this pack failing as a whole doesn't break the main regression pack. Variant: a current-release pack. Tools allow parallel hierarchies so a spec lives in multiple packs.

- **Parallelize test runs**: split packs across multiple environments running simultaneously.
  - When: You can get more than one test environment.
  - How: After splitting big packs, run them in parallel; isolate non-parallelizable tests into their own pack. (LMAX: 3-min commit build → sequential boxes → 23 VMs in parallel → perf test; Songkick on EC2: 3h → 20 min.) TeamCity/Sauce Labs/EC2 ease cloud parallelization if security/regulation permits.

- **Try disabling less risky tests**: drop low-value acceptance tests from the regression pack after the feature ships.
  - When: Test feedback is very slow.
  - How: Tests great for *driving* development (e.g. delayed emails) may cost more to maintain than they're worth as regression. Keep them in source control, just not running. (uSwitch — controversial; author disagrees, prefers cheaper automation below the UI per ch.9. uSwitch can afford it because production user-experience monitoring backstops them.)

### Theme 3 — Managing failing tests

- **Create a known regression failures pack**: a dedicated pack holding tests expected to fail.
  - How: When you choose not to fix a regression immediately, move it here so it fails without breaking the main set. Track the count; still run them periodically (a "trailing zeros" failure may mask a wrong result the next day — Knight). Use only as a temporary holding space for issues needing clarification; cap the number (Cucumber can enforce limits) so it doesn't become a "get out of jail free" card. A long-resident test argues for dropping that functionality.

- **Automatically check which tests are turned off**: monitor disabled tests so they don't get forgotten.
  - When: Failing tests are disabled, not moved to a separate pack.
  - How: An automated test lists disabled tests and must match a declared turned-off list (the list itself acts as a test). Attach a tracking ticket (JIRA) per disabled test; follow up each iteration to delete or fix. (Iowa Student Loan, FitNesse.)

## Key Concepts
- **Continuous validation**: a build server frequently checks all executable specifications against a real, deployed system — the "Botts' Dots" that keep the right product right.
- **Environmental unreliability**: specs failing due to network/DB/deploy/timing rather than wrong code.
- **Business time**: a configurable clock the system queries instead of the OS clock.
- **Test double**: a controlled fake (often file-backed, version-controlled) standing in for an external system.
- **Living documentation**: the continuously validated spec set that documents what the system does.

## Mental Models
- Use **iterative "most annoying thing"** instability removal when retrofitting tests onto legacy code — never a single big destabilizing change.
- Use **CI test history** when you don't know which flake to attack first.
- Use **event-waiting** when async timing causes flakes; use **sleeps** never.
- Use **a dedicated, fully-automated-deploy environment** when "but it works on my machine" keeps appearing.
- Use **split/parallel packs + current-iteration pack** when full-run feedback is too slow to support the development flow.
- Use **known-regression pack over silent disabling** when you genuinely can't fix a failure now.

## Anti-patterns
- **`Wait N seconds` steps**: fail under load, couple tests to hardware, and silently inflate total feedback time.
- **One giant end-to-end executable spec**: too many moving parts, any one breaks it; can't validate a case without running the whole flow.
- **Shared environment for demos + manual + continuous validation**: data-consistency failures you can't attribute.
- **Half-automated deployment**: claiming automation while someone still runs DB scripts by hand.
- **In-memory DB for data-driven systems**: dialect drift makes results misleading and doubles SQL maintenance.
- **Silently disabling failing tests**: easy to forget; rots the living documentation and defeats continuous validation.

## Worked Example
Clare McLennan's team had a chicken-and-egg problem: developers ignored the executable specs because they were unstable, but stabilizing them required developer knowledge to change the system design. Rather than a big-bang fix, she applied "find the most annoying thing, fix it, and repeat." First symptom: slow test-data processing caused timeouts. The DBA tuned database performance — which exposed the next problem: some tests started before the updated test data finished processing, so the system served stale data and produced false negatives. They added messages signaling when the latest DB data was being served, then reliably started tests after that signal (an event, not a sleep). With that source of entropy gone, the next annoyance surfaced: HTTP cookie expiry was failing tests. They introduced **business time** — a configurable replacement for the system clock — so the system could be told what time it "is," eliminating expiry-driven flakes. Each fix revealed the next; iterating without halting the delivery flow turned an untrusted suite into a stable, useful validation system — and earned developer buy-in along the way.

## Key Takeaways
1. Validate executable specs frequently so the right product stays right; on brownfield systems this is harder than unit-test CI in three specific ways: reliability, speed, and failure management.
2. Reliability is earned iteratively — fix the worst flake, repeat — backed by CI test history, a dedicated environment, and fully automated (including DB) deployment.
3. Tame externals and async: file-backed doubles, selective isolation, transactions, and *waiting for events* rather than elapsed time.
4. Don't overload one spec as functional + integration + end-to-end; separate business logic from infrastructure and keep just one thin end-to-end wiring test.
5. Get faster feedback by introducing business time, splitting packs by area/speed, running in parallel, and maintaining a current-iteration pack.
6. Avoid in-memory DBs for data-driven systems — dialect drift misleads and slow realistic tests are a real production-perf warning.
7. When you can't fix a failure now, move it to a monitored, capped known-regression pack — never silently disable, and if you must disable, automatically track what's off.

## Connects To
- **Ch 5**: high-level examples ("don't look only at the lowest level") are the good candidates for the single end-to-end wiring test.
- **Ch 9**: "automate below the skin of the application" is the cheaper alternative to expensive UI-driven tests that pushes back on disabling specs.
- **Ch 11**: continuously validated specs become the living documentation system the next chapter shows how to evolve.
- **Ch 1**: Weyerhaeuser's 30,000+ checks ("higher product quality") motivate why some failing tests must be managed rather than instantly fixed.
