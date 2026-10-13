# Chapter 20c: The Simulation Harness: Fitness Functions for Emergent Behavior

## Core Idea
Some properties (balance, economic snowballs, death spirals) exist only when the whole system runs against itself, over time, at volume. They live in no single component, so no unit, contract or architecture test can see them. Drive the whole system headless many times and turn the aggregate outcome into a fitness function. Read it with variance literacy, keep its blind spots in view, and pair it with mechanism tests.

## Frameworks Introduced
- **Simulation Harness (fitness function over emergent behavior)**: run the real system headless, unattended, many times, log structured outcomes, and assert a healthy band on an aggregate metric. This is Ch 2b's fitness function aimed at behavior instead of structure.
  - When to use: the property you care about comes from many independent agents interacting under a shared ruleset (game balance, market or economy dynamics, retry/cache/load-balancer interplay, multi-agent workflows).
  - How: (1) build an observation surface into the product: a deterministic debug hook exposing live entities, per-type aggregate stats and a force-end call. (2) Run the actual system headless, with no renderer, no human and no wallclock waits, across the full scenario roster (every map). (3) At the end of each run, dump a structured record: who died, who killed them, spend, duration, winner. (4) Derive one load-bearing aggregate metric (e.g. kill-value-per-dollar). (5) Assert a healthy band (0.5–1.5) and flag only types that land *consistently* outside it across enough runs. (6) Fail the build on violation, so the design intent that used to live in a spreadsheet becomes a gate.
- **Variance Literacy (common-cause vs special-cause)**: treat run-to-run noise as the ordinary output of a stable stochastic process (Shewhart/Deming), not as signal.
  - When to use: every time you read harness output, a dashboard or any stochastic metric.
  - How: never judge one run. Judge aggregates, then judge trends across several aggregates, before you conclude anything. A single match is a data point. A 100-match average is a measurement. Rerun an identical build before acting on an outlier.
- **Metric Blind-Spot Check**: before you "fix" what a metric reports, work out what it structurally cannot see.
  - When to use: an entity reads zero or extreme on a metric that may not match its job.
  - How: list each entity's actual job. Mark the readings that are structural non-signal (support units at 0.00). Check attribution paths (a carrier's delivered squad credits kills to the squad, not the carrier). Encode that knowledge into how you interpret the fitness function.
- **Assert the Mechanism, Not Just the Score**: pair statistical many-run fitness functions with scripted scenario tests that verify specific, nameable mechanisms.
  - When to use: always, alongside any aggregate harness.
  - How: write scripted end-to-end scenarios that drive a specific setup to a mechanistically verifiable outcome ("a plane is actually shot down by AA over a defended picket line", not "AA kill count > 0"). Keep both layers: the aggregate harness finds emergent defects, and the mechanism tests prove that named intent actually fires.

## Key Concepts
- **Emergent property**: a property present in no component, only in the composition running together over time.
- **Kill-value-per-dollar**: the total cost of the units a unit type killed, divided by that type's own cost. Healthy band 0.5–1.5.
- **Healthy band**: the asserted range an aggregate metric must stay in. It is the fitness-function threshold for emergent behavior.
- **Common-cause variation**: noise inherent to a stable process. Reacting to it as signal causes false fixes.
- **Special-cause variation**: a genuine signal that something changed.
- **Positive-feedback loop / snowball**: territory → income → units → territory, compounding until the loser cannot break out.
- **Rubber-band counterweight**: a mechanic that softens the reward curve as one side's advantage grows.
- **Observation surface**: a debug/telemetry hook shipped as product surface (not bolted-on scaffolding) that makes headless assertion possible.
- **Telemetry needs tests**: harness accounting is itself a test instrument and must be checked against an independent count.

## Mental Models
- Think of the harness as Ch 5's ArchUnit rule translated from "does this import cross a forbidden edge" to "does this unit's value cluster where the design intended."
- Think of load testing (Ch 17b's `p(95)<200`) as a one-dimensional special case of the harness: many agents, one endpoint. The harness generalizes it to many interacting agents against a whole ruleset.
- Use whole-system simulation when every component is individually correct and you still fear the composition (cache + retry + load balancer → thundering-herd spiral).
- Treat a zero-error dashboard the way you treat a 0.00 medic: it might be healthy, or the metric might be blind (log-and-swallow upstream of the counter).

## Anti-patterns
- **Judging one short run**: a 4-game run read a unit at 0.22 (a "crisis"). A longer run of the identical build read 0.66 (healthy). A redesign nearly shipped against noise, and it would have eaten attention a real defect needed.
- **"Fixing" a unit the metric cannot see**: transport, medic and smoke units score 0.00 by design. "Balancing" them turns support enablers into dead weight.
- **Trusting headline telemetry unverified**: airdropped units bypassed spawn accounting, so the victory screen showed more losses than units built. The most-glanced number was silently wrong.
- **Aggregate-only verification**: a 285–4 score says one side dominated, not that the intended mechanic fired. An outcome assertion can be satisfied by the wrong mechanism (Ch 20b).
- **Mechanism-only verification**: every named mechanic works in isolation while every emergent interaction between them goes unchecked.
- **Test scaffolding bolted on around the product**: without a shipped observation surface, headless assertion is impossible.

## Reference Tables
| Discipline | Relation to the harness | What it adds / limits |
|---|---|---|
| Chaos engineering (Netflix, Basiri et al. 2016) | Closest production cousin | Define steady state → inject real event → observe aggregate |
| Formal methods (TLA+ at AWS, Newcombe et al. 2015) | Deductive sibling | Proves absence of bad interleavings; harness only finds ones that occur under realistic load, but cheaply |
| Self-play (AlphaGo, Silver et al. 2016) | Same emergence, opposite direction | Strategy surfaces from repetition, not any single game |
| Load testing (k6/Gatling, Ch 17b) | 1-D special case | Many requests, one endpoint, aggregate threshold |
| Fuzzing (OSS-Fuzz) | Simulation over input space | Aggregate signal: crash rate, coverage plateau, new paths |

| Fitness function | Property class | Chapter |
|---|---|---|
| Architectural tests | Structure | 5 |
| Performance budgets | Cost | 17b |
| Attacker agent | Single-request contract | 20 |
| Simulation harness | Emergent whole-system behavior | 20c |

## Worked Example
**The income snowball (browser RTS, CPU-vs-CPU spectate mode).**
- *Setup*: CPU strategy deliberately biased toward capturing and holding territory-control (income) points, run across every map.
- *Finding*: a triple-hold produced a compounding loop (more territory → more income → more units → more territory) that closed faster than the losing side could escape. Result: **285 kills to 4 on every map**.
- *Diagnosis*: the capture mechanic, income formula and purchase logic were each correct on their own. The defect existed only in their composition under a rational exploiter over a long enough match. No unit test, single playtest or code review could find it.
- *Fix*: a rubber-band economic counterweight that softens income as the territorial lead grows.
- *Standing rule produced*: every new positive-feedback income source ships with its own counterweight, verified in simulation, before release.
- *Canonical parallel*: WoW's Corrupted Blood (2005). Raid curse + pet dismiss/resummon + teleport network, each correct on its own, composed into a server-wide epidemic. The durable fix was structural (the curse cannot leave the dungeon). Lofgren & Fefferman analyzed it in *Lancet Infectious Diseases* (2007).

**Variance scale on identical code**: aggregate kills swung 293 vs 7 in one run, then 54 vs 174 the other way on a rerun. The winner of a given map flipped with no code change.

## Why It Works / Failure Mode
- **Why it works**: emergent defects have no single point of origin, so the only instrument that can see them is one that runs the composition at volume and aggregates. A healthy band turns design intent into an executable, repeatable verdict, the same payoff as a structural fitness function.
- **Failure mode 1, scenario coverage**: the harness finds only what its scenario space explores (maps run, strategies the CPU can execute, the metric chosen). A loop that compounds only under a strategy your agents never try stays invisible, just as Ch 20's attacker only attacks the surface it is pointed at.
- **Failure mode 2, misreading**: without variance literacy it manufactures false alarms that erode trust in the instrument. Without blind-spot awareness it "fixes" non-problems. With unverified telemetry its headline number lies.

## Key Takeaways
1. Emergent properties exist only in composition. Build a headless whole-system harness and assert a healthy band on an aggregate metric.
2. Never judge one run: aggregates and trends across aggregates, or you will fix noise and ship the real bug.
3. Know what each metric structurally cannot see before acting on its zeros or outliers.
4. Ship the observation surface (telemetry hook, force-end) as product, and test the telemetry itself against an independent count.
5. Pair statistical fitness functions with scripted mechanism tests. Neither substitutes for the other.
6. Every positive-feedback loop needs a counterweight checked in simulation before shipping.

## Connects To
- **Ch 2b**: defines the fitness function this chapter re-aims at behavior.
- **Ch 5**: ArchUnit structural fitness functions, the template for the band assertion.
- **Ch 17b**: performance budgets and load testing as the 1-D special case.
- **Ch 20**: attacker agent, the single-request fitness function. It shares the "only tests what it's pointed at" ceiling.
- **Ch 20b**: test-suite audit. Telemetry needs tests, and outcome assertions can pass for the wrong reason.
- **Ch 21**: makes all four fitness functions branch-level law run by the pipeline.
- **Fitness functions (Ford/Parsons/Kua, *Building Evolutionary Architectures*)**: shared vocabulary.
- **Shewhart/Deming statistical process control**: common- vs special-cause variation.
- **Chaos engineering, TLA+, fuzzing, self-play**: sibling disciplines with the same steady-state, volume and aggregate structure.
