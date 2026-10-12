# Chapter 3: Embracing Risk
*Authors: Marc Alvidrez (edited by Kavita Guliani); "Motivation for Error Budgets" by Mark Roth (edited by Carmela Quinito)*

## Core Idea
Past a certain point more reliability is worse for a service and its users: cost grows nonlinearly while users can't perceive the gain. Make a service "reliable enough, but no more reliable than it needs to be", and manage the remaining unreliability with a jointly owned, data-driven **error budget**.

## Frameworks Introduced
- **Error budget (forming and using it)**: A quarterly, objective measure of how unreliable the service is allowed to be, derived from the SLO.
  - When to use: To settle dev-vs-SRE disputes about testing, push frequency, canary size, fault tolerance — without politics, fear or hope ("Hope is not a strategy").
  - How: (1) Product Management defines an SLO (expected uptime per quarter). (2) A neutral third party — the monitoring system — measures actual uptime. (3) The difference is the remaining "budget" of unreliability. (4) As long as measured uptime is above the SLO, new releases can be pushed. (5) When the budget is spent, halt releases and invest in testing/resilience; subtler options include slowing or rolling back releases as the budget nears exhaustion (beyond "bang/bang" control).
  - Why it works: Creates a common incentive; product development becomes *self-policing* — with a large budget they take risks; near exhaustion they themselves ask for more testing or slower pushes. Infrastructure outages (network, datacenter) also consume the budget, so everyone shares uptime responsibility. If launches are chronically blocked, the team can choose to loosen the SLO.
  - Failure mode: Relies on SRE having the authority to actually stop launches when the SLO is broken.
- **Availability target as both minimum and maximum**: Exceed the target, but not by much — surplus reliability wastes opportunities for features, tech-debt cleanup, or cost reduction.
- **Risk-tolerance factors for consumer services**: (1) What availability is required? (2) Do different failure types have different effects? (3) How can service cost locate the service on the risk continuum? (4) What other metrics (e.g., latency) matter?
  - Target-availability questions: What level do users expect? Tied directly to revenue (ours or customers')? Paid or free? What do competitors provide? Consumers or enterprises?
- **Cost/benefit of one more nine**: Value of improved availability = revenue × availability increase; invest only if the cost to get there is lower.
  - When no revenue mapping exists: compare with the background ISP error rate (0.01%–1%); errors below it are lost in the noise of the user's connection.
- **Explicitly delineated levels of service (infrastructure)**: Partition infrastructure into independent service tiers (e.g., low-latency vs throughput Bigtable clusters) so clients choose the cheapest level that meets their needs, externalizing the cost difference.
  - How: vary resource quantity, redundancy, geographic provisioning constraints and — critically — software configuration on identical hardware/software.

## Key Concepts
- **Risk continuum**: Reliability is a nonlinear continuum; each increment may cost 100x the previous.
- **Cost of redundant compute**: Spare equipment for maintenance, parity blocks for durability.
- **Opportunity cost**: Engineers building risk reduction instead of user-visible features.
- **Unplanned downtime**: The tractable proxy for service risk, expressed in "nines".
- **Time-based availability**: uptime / (uptime + downtime).
- **Aggregate (yield-based) availability**: successful requests / total requests over a rolling window; Google's preferred metric because globally distributed services are rarely fully "down".
- **Planned downtime**: Scheduled maintenance windows not counted against unplanned downtime (old Ads Frontend).
- **Canarying**: Testing a release on a small subset of real workload; its duration and size are an error-budget trade-off.
- **Information asymmetry**: Devs see effort to ship code; SREs see production reliability — amplifying the incentive conflict.
- **Bang/bang control**: Simple on/off release halting when budget is exhausted.

## Mental Models
- Use "a user on a 99% reliable smartphone cannot tell 99.99% from 99.999%" whenever someone asks for another nine.
- Think of the error budget as a control loop for release velocity, measured by a neutral monitor.
- Use failure *shape*, not just count: a constant low error rate and an occasional full outage can have equal error totals but very different business impact.
- Think of infrastructure success as client-relative: for Bigtable, empty queues are success for latency users and failure for throughput users.

## Anti-patterns
- **Engineering every infrastructure service to be ultra-reliable**: Far too expensive at infrastructure scale; tier it instead.
- **Negotiating risk by politics or negotiating skill**: The informal balance is unprovable; use an agreed objective metric.
- **Treating 100% as the target**: Impossible, unnoticed by users, and kills velocity.
- **Overshooting the target by a lot**: Wastes budget that could buy features, debt paydown or lower cost.
- **Keeping a service up while it leaks private data**: For a privacy failure (contacts shown to another user), taking the service down entirely is appropriate.

## Code Examples
```
Equation 3-1 (time-based):   availability = uptime / (uptime + downtime)
Equation 3-2 (aggregate):    availability = successful requests / total requests
```
What it demonstrates: the two availability definitions; yield-based applies also to batch/pipeline/storage systems via successful vs unsuccessful units of work (e.g., records processed by an ETL job).

## Reference Tables
| Metric | Value |
|---|---|
| 99.99% over a year (time-based) | up to 52.56 min downtime |
| 2.5M requests/day at 99.99% | up to 250 errors/day |
| Typical ISP background error rate | 0.01%–1% |
| Google Apps for Work external target | 99.9% quarterly (stronger internal target + contract penalties) |
| Throughput Bigtable cluster cost | ~10–50% of a low-latency cluster |
| SLO 99.999% → budget | 0.001%; a 0.0002% failure spends 20% of the quarter's budget |

| Service | Risk-tolerance decision |
|---|---|
| Google Apps for Work | High target (enterprise customers' outage = their outage) |
| YouTube (2006) | Lower target; rapid feature development more important |
| Ads Frontend (years ago) | Scheduled maintenance windows acceptable (business hours use) |
| AdWords | Must not slow search; latency is an invariant |
| AdSense | Hundreds of ms slower acceptable → consolidated into fewer locations |
| Frontend infrastructure (GFE, LB) | Extremely high reliability; lost request never reaches app |

## Worked Example
**Is one more nine worth it?** Proposed: 99.9% → 99.99%, an increase of 0.09%. Service revenue $1M (each request equal value). Value = $1M × 0.0009 = $900. If reaching 99.99% costs less than $900, invest; if more, costs exceed the projected revenue gain. Pair this with the error-budget loop: e.g., an SLO of 99.999% gives a 0.001% budget; an incident failing 0.0002% of quarterly queries consumes 20% of it, which shapes how many risky pushes remain that quarter.

## Key Takeaways
1. Treat reliability as a cost/benefit decision on a nonlinear continuum; never target 100%.
2. Prefer request-success-rate availability over uptime for distributed and batch systems.
3. Derive targets with product owners from user expectations, revenue linkage, paid/free, competitors and consumer vs enterprise.
4. Weigh failure types and secondary metrics (latency) — they give degrees of freedom for cheaper provisioning.
5. Offer infrastructure in explicit service tiers so clients pay only for what they need.
6. Run releases off an error budget measured by monitoring, and give SRE authority to stop launches when it's spent.

## Connects To
- **Ch 1**: Error budget introduced as an SRE tenet.
- **Ch 4**: SLOs that error budgets are built on.
- **Ch 8**: Push frequency, canarying and release velocity.
- **Ch 2 / Ch 26**: Bigtable vs Spanner tiering and storage trade-offs.
- **Ch 19 / Ch 20**: Frontend infrastructure reliability.
- **Appendix A (Ch 35)**: Availability table (nines → downtime).
- **Control theory**: Bang-bang control as the simplest release-gating loop.
