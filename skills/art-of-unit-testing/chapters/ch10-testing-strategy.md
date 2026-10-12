# Chapter 10: Developing a testing strategy

## Core Idea
A **testing strategy** answers the organizational questions that individual tests can't: at what *level* do we test each feature, who writes which tests, and how do we keep feedback fast without sacrificing trust? Osherove's answer is to stop arguing "unit vs. E2E" and instead deliberately spread each feature's scenarios across **test levels** — driven by a lightweight **test recipe** — then split execution into **delivery vs. discovery pipelines** so slow, non-binary tests never block a release. Higher levels use more real dependencies, buying confidence at the cost of speed and flakiness; the craft is positioning each scenario where it pays best.

## Frameworks Introduced
- **Test recipe strategy**: an informal 5–20 line plan, written *just before coding* a feature, listing each scenario (happy path + edge cases) and the level it will be tested at. **When**: at the start of a feature/story, ideally by a dev + tester pair (two viewpoints check implicit assumptions). **How**: list scenarios, assign each the lowest level that still gives confidence, store it as a comment in the Jira story/TODO — not a formal artifact. **Why**: most tests land low (fast feedback) while a few high-level tests guarantee confidence; placing variations *below* the main scenario kills cross-level duplication and opens a dev↔QA communication channel. It becomes part of the feature's definition of "done."
- **Delivery vs. discovery pipelines**: two parallel pipelines split by test purpose. **When**: as soon as you have non-binary/long-running tests (load, perf, complexity scans). **How**: delivery pipeline runs delivery-blocking tests and gives a fast green/red go-no-go (and can auto-deploy); discovery pipeline runs good-to-know tests continuously, never blocks a release, and ends in dashboard numbers that become future work items. **Why**: keeps slow, advisory feedback off the critical release path.

## Key Concepts
- **In-memory vs. out-of-process**: unit, component, integration tests instantiate production code directly in memory; API, E2E, system tests add a network and a deployment.
- **Unit vs. component test**: distinction is *abstraction scope*, not dependencies — both control everything (no files/DB/network). A component test just spans more functions/classes between entry and exit points.
- **Integration test**: looks like a unit test but leaves some dependencies *real* (config, DB, filesystem); still invoked in-memory.
- **Generic test scorecard**: judge any test on five criteria — complexity, flakiness, confidence-when-passes, maintainability, execution speed (each 1–5).
- **Diminishing returns from E2E**: the first E2E test buys huge confidence (exercises all the glue); the second is usually a variation costing the same to run/debug but adding a fraction of the confidence.
- **Build whisperer**: the burnout-prone QA gatekeeper who manually interprets a chronically-red flaky build to declare "it's actually green." A symptom of the E2E-only antipattern; cured by robust automated pipelines that statistically judge builds.
- **"Throw it over the wall" mentality**: QA owns the high-level tests, devs don't see or care about their results — structurally turns devs and QA into enemies.
- **Delivery-blocking vs. good-to-know (non-blocking) tests**: blocking = binary go/no-go (unit, E2E, system, security); good-to-know = discovery/monitoring of KPIs (complexity scans, load/perf), non-binary, failures spawn backlog items not release blocks.
- **Test parallelization**: run different test layers — and even individual tests within a stage — in parallel, using dynamically created/destroyed environments. Cheaper than more manual testers or idle waiting.
- **DRY across features and layers**: if a scenario is already covered (by another feature's E2E, or at a higher level), don't repeat it; lower levels test only *variations*.

## Mental Models
- **The confidence/speed trade-off ladder**: climbing test levels trades maintainability + speed for confidence + realism. No level is "best"; each feature picks rungs.
- **The 1:5 (to 1:10) ratio**: for every high-level test, expect ~5+ lower-level tests. Bottom-up: 100 unit → ~10 integration → 1 E2E. A rule of thumb for balance, not a quota.
- **The test pyramid — Osherove's take**: he endorses the *shape* (many fast low-level tests, few slow high-level) but reframes it: don't fill levels for their own sake; let the per-feature recipe decide. Some features need only unit tests, others only API/E2E. Confidence, not pyramid symmetry, is the goal.
- **Pragmatism over coverage at all levels**: "if all these tests passed, I'd feel pretty good about this feature" is the completion test — shuffle scenarios between levels until that's true.

## Reference Tables

| Level | What's real | Speed | Confidence | Complexity | Flakiness | Maintainability | Pros | Cons | Who writes |
|---|---|---|---|---|---|---|---|---|---|
| Unit | nothing (all controlled, in-mem) | 5/5 | 1/5 | 1/5 | 1/5 | 5/5 | fastest, cheapest, least flaky | only proves a small piece works | developer |
| Component | nothing (more code in scope) | 5/5 | ~1–2/5 | 1–2/5 | 1/5 | 5/5 | broader scope, still fully controlled | still low system confidence | developer |
| Integration | some deps real (DB, config, FS) | 3–4/5 | 2–3/5 | 2/5 | 2–3/5 | 3–4/5 | verifies uncontrolled deps | slower, flakier per real dep | developer |
| API | deployed service + network | 2–3/5 | 3–4/5 | 3/5 | 3–4/5 | 2–3/5 | proves callers can trust deployed API | network flakiness, schema setup | dev / QA |
| E2E/UI isolated | own app real, deps faked | 1–2/5 | 4/5 | 4/5 | 4/5 | 1–2/5 | user-flow confidence, no 3rd-party risk | slow, flaky, multi-step | QA / dev |
| E2E/UI system | everything real | 1/5 | 5/5 | 5/5 | 5/5 | 1/5 | highest confidence, near-prod | minutes–hours, fails 1000 ways | QA |

**Antipatterns**: *E2E-only* (slow, flaky, diminishing returns, build whisperers); *low-level-only* (fast but never confident — forces manual testing before release); *disconnected low/high-level* (two non-communicating groups, duplicated scenarios, worst of both worlds).

## Worked Example
Feature: **User profile update.** Two people (dev + tester) spend ~10 minutes before coding listing scenarios and applying the recipe rules (*prefer lower levels; don't repeat across layers; stop when confident*):

```
User profile feature testing recipe
E2E   - Login, go to profile, update email, log out, log in with new email, verify updated
API   - Call UpdateProfile API with more complicated data
Unit  - Profile update logic with bad email
Unit  - Profile update logic with same email
Unit  - Profile serialization/deserialization
```

Reasoning: the *one* happy-path E2E proves the full glue works end to end (highest-value, run once). Richer data variations drop to **API** — no need to re-pay the E2E tax once the glue is proven. All edge cases (bad/same email, serialization) go to **unit** level: fast, deterministic, no duplication of the E2E path. Result ≈ 1 E2E : 1 API : 3 unit — honoring the 1:5-ish ratio while keeping feedback fast. Dev writes the unit tests, QA writes the E2E, both work in parallel while the feature is coded.

## Key Takeaways
1. Pick the test *level* per scenario, not per project — lowest level that still gives confidence.
2. Use a **test recipe**: 5–20 informal lines, written just-in-time, by a pair, stored as a comment — part of "done."
3. Aim for a ~1:5 (to 1:10) ratio of high- to low-level tests; never duplicate a scenario across levels.
4. Don't avoid E2E tests — *minimize* them; their marginal value drops fast while cost stays flat.
5. Avoid all three antipatterns; the disconnected one is a tell that QA and dev don't talk.
6. Split into **delivery** (blocking, fast, can auto-deploy) and **discovery** (non-blocking, slow, dashboard) pipelines.
7. **Parallelize** layers, stages, and individual tests; run after every commit, never nightly.

## Connects To
- **Ch 1**: defines what makes a *good unit test* (fast, trustworthy, maintainable, in-memory, controls its dependencies) — the scorecard's top-left corner and the foundation the strategy spreads upward from.
- **Ch 11**: turning this strategy into an *organizational* reality — leading the change, breaking the dev/QA wall, getting buy-in for pipelines and dynamic environments so build whisperers become unnecessary.
