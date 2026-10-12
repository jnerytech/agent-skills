# Chapter 17: Testing for Reliability
*Authors: Alex Perry and Max Luebbe (edited by Diane Bates)*

> "If you haven't tried it, assume it's broken." (Unknown)

## Core Idea
An SRE's job is to **quantify confidence** in a system. Monitoring measures past reliability, and testing makes **future** reliability predictable. A test that passes both before and after a change shows equivalence and reduces the uncertainty that a change introduces. More test coverage means you can make more changes before predicted reliability hits the acceptability limit.

## Frameworks Introduced
- **Testing and MTTR/MTBF relationship**: passing tests don't prove reliability, but failing tests generally prove its absence.
  - **Zero MTTR**: when a system-level test applied to a subsystem catches the same problem monitoring would catch, the push is blocked and the bug never reaches production.
  - How: the more bugs you find with zero MTTR, the higher the MTBF your users see. Higher MTBF encourages faster releases, new bugs then push release velocity back down, and the system self-regulates.
  - Why it works: a test is a monitoring signal that fires *before* users are exposed, so the repair is simply blocking the push.
- **Hierarchy of traditional tests** (offline, pre-deployment):
  1. **Unit test**: the smallest test, of a separable unit (class or function). It doubles as a specification and is the entry point to TDD.
  2. **Integration test**: tests an assembled component. **Dependency injection** (for example, Dagger) replaces complex dependencies, such as a stateful DB, with precisely specified mocks.
  3. **System test**: the largest test of an undeployed system, end to end. Variants:
     - **Smoke test** (sanity test): very simple but critical behavior. It short-circuits more expensive testing.
     - **Performance test**: catches incremental degradation, for example memory growing from 8 GB to 32 GB, or latency going 10 ms to 50 ms to 100 ms.
     - **Regression test**: a "gallery of rogue bugs" that historically broke the system, kept at system or integration level.
  - Cost gradient: unit tests take milliseconds on a laptop, while full-server system tests take minutes to hours and dedicated resources.
- **Production tests** (against the live system, similar to black-box monitoring):
  - **Configuration test**: for each config file in version control, check how the binary is *actually* configured in production and report discrepancies. These tests are non-hermetic. The versions that pass show how far production lags behind the goal. Configs get harder to test when they (a) implicitly include binary defaults, (b) pass through a preprocessor such as bash into flags, or (c) specify context for a shared runtime.
  - **Stress test**: find the limits where components fail catastrophically rather than degrading gracefully. For example: how full can a DB get before writes fail, and how many QPS before an app server overloads?
  - **Canary test**: upgrade a subset of servers, let them incubate ("**baking the binary**"), then roll out progressively or revert. It "isn't really a test; rather, it's structured user acceptance."
- **Fault order U (canary math)**: with an exponential rollout, cumulative variance reports follow **C·U = R·K**. Here R is the report rate and K is the period over which traffic grows by a factor of *e* (172%). Estimate the fault order as U = R·K / C ("dividing and correcting for K"):
  - U=1: the request hit code that is simply broken.
  - U=2: the request randomly damages data that a future request may see.
  - U=3: the damaged data is also a valid identifier to a previous request.
  - Most bugs are order 1 and scale linearly with traffic. Turn logs of unusual responses into regression tests. Higher-order bugs must be caught during release, because operational load grows fast. You don't need fairness among traffic fractions as long as each uses the same K.
- **Where to start testing a prototype codebase (most impact, least effort)**:
  1. Can you **stack-rank** components by importance? ("If every task is high priority, none of the tasks are.")
  2. Which functions are **mission- or business-critical**? Billing is the classic case, and it is often cleanly separable.
  3. Which **APIs** do other teams integrate against?
  4. Add **smoke tests for every release**, because shipping obviously broken software is a "cardinal sin."
  5. **Convert every reported bug into a test** that initially fails, to grow a regression suite.
- **Testing infrastructure foundation**: versioned source control, then a **continuous build** that notifies on breakage. Everyone drops everything to fix a broken build. Use dependency-aware builds (**Bazel**) so only the tests for changed code run.
- **Barrier defenses against risky software** (for tools that bypass the tested API, for example by turning off DB transactions for batch maintenance):
  1. Use a separate tool to place a **barrier** in the replication config so the replica fails its health check and isn't released to users.
  2. Make the risky software **check for the barrier at startup** and only touch unhealthy replicas.
  3. Use the black-box replica health-validation tool to **remove** the barrier.
- **Offline disaster-recovery tool design**: (1) compute a checkpoint equal to a clean stop, (2) push the checkpoint so it is loadable by existing non-disaster validation tools, (3) support the usual release barrier tools that trigger the clean start. Breaking any constraint (offline, checkpoint, loadable, barrier, clean start) sharply lowers confidence that the tool will work.
- **Config file classification rule**: put each config file in exactly one category: (a) it exists for low MTTR and is edited only during failures, or (b) it changes more often than app releases (holds release state) and must be treated **as a release**. Enforce this with: enough test coverage for routine edits, edits briefly delayed for release testing before releases, and a **noisy break-glass** that files a bug.
- **Break-glass with tests still running**: don't disable the tests. Associate the early push with the pending test run, back-annotate broken tests onto the push as soon as possible, and automatically boost the priority of those tests so they preempt routine work.
- **Production probes (three request sets)**: known bad requests, known good requests replayable against production, and known good requests that are not replayable. Use each as an integration test, a release test, *and* a monitoring probe. The probe's production configuration (real load balancer, real persistent backend, independent release cycles) is one that was never tested before.

## Key Concepts
- **MTTR**: Mean Time to Repair, how long ops takes to fix a bug by rollback or another action.
- **MTBF**: Mean Time Between Failures, as experienced by users.
- **Hermetic test**: runs in a sandboxed, fully controlled environment. Production is not hermetic.
- **Rollouts entangle tests**: production mixes binary and config versions, so a test may pair the latest config with an older binary. A result can be "valid hermetically, but not operationally."
- **Statistical tests**: Lemon (fuzzing), Chaos Monkey, and Jepsen. They aren't repeatable, but log the RNG seed, replay several times, and the non-failure rate tells you how hard it will be to confirm a fix.
- **Batch test vs. interactive test**: the test deadline is the engineer's next context switch. Batch failures tell the *reviewer* "not ready for review."
- **Flakiness budget**: the tolerable rate of patches wrongly rejected because of environmental flakiness.
- **Fake backend versions**: the peer team should cut a fake backend release alongside the real one. Monitoring tracks every release-version combination across an interface, and rollout automation should block on bad combinations.
- **Defense in depth for tools**: every anticipated misbehavior should be *reported* by some test or by another tool's validator, even if that tool can't fix it.

## Mental Models
- Think of **testing as demonstrating equivalence across a change**. Each test that passes both before and after removes uncertainty from your reliability prediction.
- Think of **reliability as a budget that changes spend**. Too many changes too fast pushes predicted reliability toward the limit, so pause and let monitoring data accumulate.
- Use **stability-drives-agility** when arguing for build hygiene: a predictably green build lets developers iterate faster and makes emergency releases (for example, after a security disclosure) feasible.
- Use **shorter feedback cycles**: testing intermediate versions maps each failure unambiguously to its cause, so the shipped release is better even with the same tests. Segment the reliability budget by team, giving feature teams and SRE separate uncertainty limits and release rates.

## Anti-patterns
- **Trying to unit-test everything first in a low-coverage codebase**: it is overwhelming. Start with the highest-impact, lowest-effort tests.
- **"We need more tests" as a refrain**: set explicit coverage goals and deadlines instead, and treat it as an engineering project.
- **Equal test rigor for all software**: life- or revenue-critical systems need far more than a short-lived script.
- **Segregating test infrastructure from production config**: it duplicates tools, creates commit races, and in SRE prevents architecture changes because migration risk can't be eliminated.
- **Disabling tests on break-glass**: mistakes surface only once users are affected.
- **Configs in an embedded interpreted language** (such as Python): loading means executing code, with no upper bound on runtime. Prefer YAML with a heavily tested parser (`safe_load`), or better, **protocol buffers**, which give a predefined schema, load-time checks, and bounded runtime. If you must use an interpreted config, enforce deadlines on integration tests.
- **Auto-remediating tools**: the home-directory tool that notices a half-parsed `/etc/passwd` should *report* the discrepancy, not delete users' data.
- **Assuming automation won't affect itself**: a container-shuffling tool may move itself, and a fleet upgrader and a rebalancer may change each other's environment. Restart semantics and test coverage are required.

## Code Examples
```
C · U = R · K      =>   U = (R · K) / C
```
What it demonstrates: cumulative user-visible variances C under exponential rollout, from report rate R, growth period K, and fault order U.

```
K = 86400 / ln(0.1 / 0.01) = 37523 seconds  (~10 h 25 min)
```
What it demonstrates: the growth period K for a 24-hour exponential ramp from 1% to 10% of traffic.

```
0.99 ^ (1/42000) ≈ 0.99999976   →  each test must pass > 99.9999% of the time
```
What it demonstrates: with 21,000 tests run before and after a patch (42,000 results) and at most 1 in 100 perfect patches falsely rejected, each individual test must be extremely non-flaky ("Hmm.").

## Reference Tables

| Canary rollout rule of thumb | Traffic |
|---|---|
| Day 1 | 0.1% |
| Day 2 | 1% |
| Day 3 | 10% |
| Day 4 | 100% |
(Scale by orders of magnitude every 24 h while varying the geographic location of upgraded servers.)

| Test type | Hermetic? | Scope / purpose |
|---|---|---|
| Unit | Yes | A class or function, as a specification |
| Integration | Yes | An assembled component with DI mocks |
| System (smoke/perf/regression) | Yes | End to end on an undeployed system |
| Configuration | No | Checked-in config vs. actual production |
| Stress | No | Find catastrophic limits |
| Canary | No | Structured user acceptance on live traffic |

| False-rejection rate of perfect patches | User reaction |
|---|---|
| 1 in 10 | Vehement complaints |
| 1 in 100 | Likely goes without comment |

## Worked Example
**Probe-gated rollout:** a production updater gradually replaces both the application and its probes, so all four combinations of old/new probe and old/new app run continuously. Each new instance is expected to be briefly unhealthy at startup. If the probes are part of the **readiness check** and a combination errors, the update "safely fails indefinitely." No user traffic ever reaches the new version, and the update stays paused until engineers diagnose the problem and trigger a clean rollback. If a probe fails, either the frontend API (from the load balancer) or the backend API (to the persistent store) is not equivalent between production and release, and unless you know why, "the site is likely broken." This covers the case where a new version talks to an old peer through a deprecated API, or an old version uses an API that "didn't work properly yet."

## Key Takeaways
1. Treat test coverage as a way to reduce uncertainty. Pause changes when predicted reliability nears the limit.
2. Aim for zero-MTTR bugs by running system-level tests that block pushes before users see the bug.
3. In a new or prototype codebase, start with smoke tests, critical paths (billing), and public APIs, and convert every bug into a test.
4. Build on source control plus continuous build. A broken build gets fixed before anything else.
5. Use canaries with exponential ramps (0.1%, 1%, 10%, 100%) and estimate the fault order. Higher-order bugs must be caught at release.
6. Treat frequently changing config as releases. Use bounded-runtime, schema-checked formats (protobuf), and a noisy break-glass that keeps tests running.
7. Reuse known-good and known-bad request sets as integration tests, release tests, and production probes, and gate rollouts on probe readiness.

## Connects To
- **Ch 4 (Service Level Objectives)**: the acceptability limit that reliability predictions are compared against.
- **Ch 6 (Monitoring Distributed Systems)**: production tests resemble black-box monitoring.
- **Ch 8 (Release Engineering)**: hermetic builds, canary rollouts, and push-on-green.
- **Ch 3 (Embracing Risk)**: the error budget is the counterpart of segmenting the reliability budget by team.
- **Ch 21–22 (Handling Overload / Cascading Failures)**: stress tests find catastrophic limits.
- **Ch 26 (Data Integrity)**: offline checkpoint and recovery tooling.
- **Ch 27 (Reliable Product Launches)**: gradual and staged rollouts.
- **Chaos engineering (Chaos Monkey, Jepsen)**: statistical fault-injection testing.
