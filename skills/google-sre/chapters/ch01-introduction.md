# Chapter 1: Introduction
*Authors: Benjamin Treynor Sloss (edited by Betsy Beyer)*

## Core Idea
SRE is "what happens when you ask a software engineer to design an operations team": run production with engineers who automate away manual work, cap ops load at 50%, and replace the dev/ops conflict over change with an explicit, shared **error budget**.

## Frameworks Introduced
- **The 50% cap on ops work**: Aggregate "ops" work (tickets, on-call, manual tasks) for SREs is capped at 50%; the remaining 50%+ must be development/engineering.
  - When to use: Always, as the structural guarantee that an SRE team does not devolve into a linearly-scaling ops team.
  - How: (1) Measure how SRE time is actually spent. (2) If a team consistently spends <50% on development, redirect excess ops work back to the product dev team — reassign bugs/tickets to dev managers, (re)integrate developers into the pager rotation — or add staff without adding operational responsibilities. (3) Stop redirection when ops load drops back to <=50%.
  - Why it works: It is a "safety valve" and a feedback mechanism — developers who feel the overflow are pushed to build systems that need no manual intervention. Goal is systems that are *automatic*, not just *automated*.
  - Failure mode: Works only if the whole org (SRE and dev) understands why the valve exists; otherwise overflow redirection looks like SRE refusing work.
- **Error budget**: Error budget = 1 − availability target. A 99.99% target leaves a 0.01% budget that can be spent on anything (launches, experiments) as long as it isn't overspent.
  - When to use: To resolve the structural conflict between innovation velocity (dev) and stability (ops).
  - How: (1) The business/product sets the availability target (a product question, not a technical one). (2) Compute the budget. (3) Spend it on risky launches; use phased rollouts and 1% experiments to spend it efficiently. (4) If depleted, stop releases (e.g., for the rest of the quarter) — this needs management backing.
  - Why it works: SRE's goal is no longer "zero outages"; both teams aim to spend the budget for maximum feature velocity, so an outage becomes an expected, managed cost of innovation rather than a failure to fear.
- **Questions for choosing the reliability target**: (1) What availability will users be happy with, given how they use the product? (2) What alternatives exist for dissatisfied users? (3) What happens to usage at different availability levels?
- **Three kinds of valid monitoring output**: Alerts (human must act *now*), Tickets (human must act, but within days), Logging (no one reads unless prompted; diagnostic/forensic).
  - How: Software interprets; humans are notified only when they must act. Never rely on email alerts a human must read and judge.
- **Change-management trio (automated)**: progressive rollouts; quickly and accurately detecting problems; rolling back safely when problems arise.
- **Mandatory capacity-planning steps**: (1) accurate organic demand forecast extending beyond capacity acquisition lead time; (2) accurate incorporation of inorganic demand sources; (3) regular load testing to correlate raw capacity (servers, disks) to service capacity.
- **On-call load target**: max two events per 8–12-hour on-call shift; fewer than one per shift consistently wastes the engineer.

## Key Concepts
- **Sysadmin model**: Assemble off-the-shelf components, run them with an ops team that grows with load; easy to staff but costly.
- **Direct costs (dev/ops split)**: Manual change management and event handling make team size scale with system load.
- **Indirect costs (dev/ops split)**: Different backgrounds, vocabulary, risk assumptions and incentives erode communication, trust and respect — "a pathology".
- **SRE hiring mix**: 50–60% standard Google SWEs; 40–50% near-SWE (85–99% of the skill set) plus rare skills, most often UNIX internals and networking (Layer 1–3); no performance difference observed.
- **Blameless postmortem culture**: Write postmortems for all significant incidents, paging or not; expose faults and engineer fixes rather than avoid them.
- **MTTF / MTTR**: Reliability is a function of mean time to failure and mean time to repair; MTTR is the key emergency-response metric.
- **Playbook**: Pre-recorded best practices yielding roughly 3x MTTR improvement vs. "winging it".
- **Wheel of Misfortune**: Disaster role-playing exercise to prepare on-call engineers.
- **Organic vs. inorganic growth**: Natural adoption vs. demand from launches, marketing campaigns, business changes.
- **Provisioning**: Combines change management and capacity planning; riskier than load shifting, so done carefully, quickly and only when needed.

## Mental Models
- Think of SRE as ops work done by people who get bored doing things by hand and can write the software to replace it.
- Use the error budget when dev and ops argue about launch speed: convert the argument into budget arithmetic.
- Think of slowness as lost capacity: a slowing system eventually stops serving ("infinite slowness"); SREs provision to a capacity target *at a specific response speed*.
- Use "a team that manages a service needs to code or it will drown" when deciding whether to accept more manual work.

## Anti-patterns
- **Launch gates that check every past outage cause**: Arbitrarily long, unequal-value lists; devs route around them with "flag flips", "incremental updates", "cherrypicks" and sharding to dodge review.
- **100% reliability target**: Users can't distinguish 100% from 99.999% because laptop, WiFi, ISP and power grid are far less reliable; the last 0.001% costs enormously for no benefit (exceptions: pacemakers, anti-lock brakes).
- **Email-based alerting requiring human interpretation**: Fundamentally flawed; software should interpret.
- **Hero jack-of-all-trades on-call**: Works, but a practiced engineer with a playbook works much better.
- **Ops team that scales linearly with traffic**: Hiring more people to do the same tasks over and over.
- **Pager fatigue (>2 events/shift)**: Problems can't be investigated; engineers can't learn; won't improve with scale.

## Reference Tables
| Item | Number |
|---|---|
| Cap on ops work | 50% (upper bound; target is far lower) |
| SRE composition | 50–60% SWE / 40–50% near-SWE + rare skills |
| Max on-call events | 2 per 8–12h shift (min useful ~1) |
| Playbook effect | ~3x MTTR improvement |
| Outages caused by changes | ~70% |
| DevOps term emerged | late 2008 |

## Worked Example
**Error budget in practice**: A service's product owner sets 99.99% availability. Error budget = 0.01% unavailability. Dev wants to launch features fast; rather than SRE blocking, both teams agree to spend the 0.01% on launches, using phased rollouts and 1% experiments so each risk consumes little budget. If outages deplete the budget, releases stop for the rest of the quarter — a decision that product teams accept only when management mandates it, which is why SRE requires strong management support.

## Key Takeaways
1. Measure SRE time; enforce the 50% ops cap by pushing overflow back to developers (tickets, pager).
2. Set reliability targets as a product decision using the three user-centric questions; never 100%.
3. Derive the error budget (1 − target) and use it to gate release velocity.
4. Make monitoring emit only alerts, tickets, or logs — no human-interpreted emails.
5. Write playbooks and run Wheel of Misfortune drills to cut MTTR.
6. Automate progressive rollouts, detection and rollback, since ~70% of outages come from changes.
7. SRE owns capacity planning and therefore provisioning and efficiency.

## Connects To
- **Ch 3**: Full treatment of risk tolerance and error budgets.
- **Ch 4**: SLOs that define the availability target behind the budget.
- **Ch 5**: Toil and the 50% rule in detail.
- **Ch 6 / Ch 10**: Monitoring philosophy (alerts/tickets/logs) and Borgmon.
- **Ch 8**: Release engineering and progressive rollouts.
- **Ch 11 / Ch 28**: On-call load and Wheel of Misfortune ("Disaster Role Playing").
- **Ch 15**: Blameless postmortem culture.
- **Ch 31**: Production meetings for dev/SRE collaboration on performance.
- **DevOps**: SRE can be seen as a specific implementation of DevOps with idiosyncratic extensions.
