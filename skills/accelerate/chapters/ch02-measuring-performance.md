# Chapter 2: Measuring Performance
*Authors: Nicole Forsgren, Jez Humble, Gene Kim*

## Core Idea
Measure software delivery performance with four global, outcome-oriented metrics — **delivery lead time, deployment frequency, time to restore service, change fail rate** — which cluster teams into high, medium and low performers and show there is no trade-off between speed and stability; this performance in turn predicts organizational performance.

## Frameworks Introduced
- **Software delivery performance (the four key metrics)**:
  1. **Lead time for changes** (product delivery lead time): time from code committed to code successfully running in production.
  2. **Deployment frequency**: how often the organization deploys code for its primary service/application to production or an app store — a proxy for **batch size** (strictly its reciprocal).
  3. **Time to restore service (MTTR)**: how long it generally takes to restore service after an incident (unplanned outage, service impairment).
  4. **Change fail rate**: percentage of changes to production (releases and infrastructure configuration changes) that result in degraded service or require remediation (hotfix, rollback, fix-forward, patch). In Lean terms, the "percent complete and accurate" of the delivery process.
  - Lead time + deployment frequency = **tempo**; MTTR + change fail rate = **stability**.
  - When to use: benchmarking teams against the industry, setting improvement targets, testing which practices actually move outcomes.
  - How: survey (or instrument) each metric using the ordinal buckets below; locate yourself in Table 2.3; ask teams to set targets for the four measures.
  - Why it works / failure mode: the metrics are global (no team can win alone — dev and ops must collaborate) and outcome-based (busywork doesn't move them). Failure mode: using them as a control tool in a pathological/bureaucratic culture — "whenever there is fear, you get the wrong numbers" (Deming).
- **Two criteria for a successful performance measure**: (1) focus on a **global outcome**, so teams aren't pitted against each other (e.g., rewarding dev for throughput and ops for stability creates the "wall of confusion"); (2) focus on **outcomes, not output** — don't reward busywork.
  - When to use: evaluating any proposed engineering metric.
- **Design vs. delivery split of lead time (Table 2.1)**: separate the high-variability "fuzzy front end" (design/validation, Reinertsen) from the low-variability, measurable delivery part (build, test, deploy). Measure the delivery part.
- **Cluster analysis of performance**: group respondents on the four measures without telling the algorithm what is "good"; it found significantly different high/medium/low clusters every year (2014–2017), with all four measures good classifiers.

## Key Concepts
- **Outputs vs. outcomes**: flawed metrics count activity (lines of code, story points); good ones measure results that matter.
- **Lines of code**: rewards bloat and maintenance cost; minimizing it rewards unreadable code — neither works.
- **Velocity**: an Agile capacity-planning tool; relative and team-dependent, so incommensurable across teams; gamed when used as productivity (inflated estimates, less cross-team collaboration).
- **Utilization**: good only up to a point — queue theory says as utilization approaches 100%, lead times approach infinity; no slack for unplanned work or improvement.
- **Batch size**: central Lean lever (Toyota); smaller batches reduce cycle time and variability, accelerate feedback, reduce risk and overhead, improve efficiency, motivation, cost and schedule growth (Reinertsen).
- **Continuous deployment**: single-piece flow where each commit can be released to production.
- **Organizational performance**: self-rated profitability, market share, productivity (Widener 2007 scale) — highly correlated with ROI and robust to economic cycles.
- **Noncommercial performance**: quantity of goods/services, operating efficiency, customer satisfaction, quality, achieving mission goals (Cavalluzzo & Ittner 2004 scale).
- **Predictive relationship (arrows in figures)**: read as "drives," "predicts," "affects," "impacts" — beyond correlation (inferential prediction, Ch 12).

## Mental Models
- Think of deployment frequency as **the visible proxy for invisible inventory**: software has no warehouse, so deploy cadence stands in for batch size.
- Use "how quickly can we restore?" instead of "how rarely do we fail?" when systems are complex and change rapidly — failure is inevitable.
- Think of utilization as a **queue**: past a threshold, every extra percent of busyness explodes lead time; manage utilization against lead time economically.
- Use the four metrics only in a learning culture; in a fearful one they become a weapon and the data gets distorted.

## Anti-patterns
- **Lines of code as productivity**: rewards bloated, costly software.
- **Velocity as a productivity or cross-team comparison metric**: destroys its planning value and inhibits collaboration.
- **Maximizing utilization**: removes slack, lead times grow exponentially.
- **Local/siloed incentives (dev = throughput, ops = stability)**: the "wall of confusion" — poor code thrown over the wall, painful change management in return.
- **Assuming speed trades off against stability**: refuted by the data; underlies flawed "bimodal IT."
- **Increasing tempo by "working harder"**: low performers in 2017 lost stability without fixing underlying obstacles (re-architecture, process improvement, automation).
- **Change approval boards**: negatively correlated with tempo and stability.
- **Outsourcing strategic software**: delivery performance is a competitive advantage — bring it in-house; buy SaaS for non-strategic software (payroll, office tools) — see Wardley mapping.

## Code Examples
Survey response options (ordinal scales) used to measure the metrics:

```
Lead time for changes (commit -> running in production)   [same options used for time to restore service]
- less than one hour
- less than one day
- between one day and one week
- between one week and one month
- between one month and six months
- more than six months

Deployment frequency (primary service/application)
- on demand (multiple deploys per day)
- between once per hour and once per day
- between once per day and once per week
- between once per week and once per month
- between once per month and once every six months
- fewer than once every six months

Change fail rate
- % of changes that result in degraded service or subsequently require remediation
  (service impairment/outage, hotfix, rollback, fix-forward, patch)
```
What it demonstrates: how to make each metric measurable via self-report buckets that reduce variability and allow cross-organization comparison.

## Reference Tables

**Table 2.1 Design vs. Delivery** (Kim et al. 2016)

| Product Design and Development | Product Delivery (Build, Testing, Deployment) |
|---|---|
| Create new products/services that solve customer problems using hypothesis-driven delivery, modern UX, design thinking | Enable fast flow from development to production and reliable releases by standardizing work and reducing variability and batch sizes |
| Feature design and implementation may require work never performed before | Integration, test, and deployment must be performed continuously as quickly as possible |
| Estimates are highly uncertain | Cycle times should be well-known and predictable |
| Outcomes are highly variable | Outcomes should have low variability |

**Table 2.2 Software Delivery Performance for 2016**

| 2016 | High Performers | Medium Performers | Low Performers |
|---|---|---|---|
| Deployment Frequency | On demand (multiple deploys per day) | Between once per week and once per month | Between once per month and once every six months |
| Lead Time for Changes | Less than one hour | Between one week and one month | Between one month and six months |
| MTTR | Less than one hour | Less than one day | Less than one day* |
| Change Failure Rate | 0–15% | 31–45% | 16–30% |

**Table 2.3 Software Delivery Performance for 2017** (use this to locate yourself)

| 2017 | High Performers | Medium Performers | Low Performers |
|---|---|---|---|
| Deployment Frequency | On demand (multiple deploys per day) | Between once per week and once per month | Between once per week and once per month* |
| Lead Time for Changes | Less than one hour | Between one week and one month | Between one week and one month* |
| MTTR | Less than one hour | Less than one day | Between one day and one week |
| Change Failure Rate | 0–15% | 0–15% | 31–45% |

\* Low performers were lower on average (statistically significant) but share the same median as the medium performers.

**Organizational impact**
- High performers were consistently **twice as likely** to exceed profitability, market share and productivity goals than low performers (multi-year).
- In 2017, high performers were also **twice as likely** to exceed noncommercial objectives (quantity of goods/services, operating efficiency, customer satisfaction, quality, mission goals).
- High-performing cluster is pulling away; low performers held throughput flat 2014–2016, started increasing in 2017, and lost stability.

## Worked Example
**The 2016 "Surprise!" anomaly.** In 2016 medium performers had a *worse* change fail rate (31–45%) than low performers (16–30%) — the first inconsistency across measures in any group. The data don't conclusively explain it; the authors' hypothesis: medium performers are mid-transformation, wrestling with large-scale re-architecture and legacy code bases. Supporting signal: in 2016 medium performers reported more time on new work, and more time on unplanned rework than low performers — suggesting new work came at the expense of critical rework, accumulating technical debt, making systems more fragile and raising change fail rate. Practitioner lesson: during a transformation, a temporary rise in change fail rate is a warning to reserve capacity for rework and debt, not a reason to abandon the transformation.

## Key Takeaways
1. Measure delivery with the four metrics — lead time, deployment frequency, time to restore, change fail rate — and stop using lines of code, velocity or utilization as productivity.
2. Measure delivery lead time from commit to production; don't try to clock the fuzzy front end.
3. Reduce batch size (deploy more often) to get faster feedback and lower risk.
4. Optimize tempo and stability together; high performers win on all four.
5. Benchmark against Table 2.3 and have teams set their own targets for the four measures.
6. Treat strategic software delivery as a core competency; outsource/SaaS only non-strategic systems.
7. Fix culture first — deploy metrics for learning, never for control.

## Connects To
- **Ch 1**: source of the 46x / 440x / 170x / 5x high-vs-low comparison.
- **Ch 3**: culture (Westrum) as precondition for honest measurement; note that only lead time, deployment frequency and time to restore form the valid delivery *construct* — change fail rate is strongly correlated but separate.
- **Ch 4**: continuous delivery practices that drive these metrics and lower change fail rate.
- **Ch 7**: change approval processes (CABs) — negatively correlated with tempo and stability.
- **Ch 8**: Lean product development and the fuzzy front end; small batches enabling A/B testing.
- **Ch 12**: inferential prediction behind the arrows in figures.
- **Appendix B**: cluster analysis details.
- **Reinertsen, *Principles of Product Development Flow***: batch size, queue theory, fuzzy front end.
- **DORA metrics**: the industry name later adopted for these four measures.
- **Wardley mapping**: deciding which software is strategic.
