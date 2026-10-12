# Chapter 5: Eliminating Toil
*Authors: Vivek Rau (edited by Betsy Beyer)*

## Core Idea
**Toil** — manual, repetitive, automatable, tactical, no-enduring-value work that scales O(n) with the service — must be kept below 50% of each SRE's time, because unchecked it expands to fill 100%; engineering away toil is the "Engineering" in SRE.

## Frameworks Introduced
- **The six attributes of toil**: Work tied to running a production service that is:
  1. **Manual** — includes hands-on time running a script (not elapsed time).
  2. **Repetitive** — done over and over; first or second time, or novel problems, are not toil.
  3. **Automatable** — a machine could do it as well, or the need could be designed away; essential human judgment suggests not toil.
  4. **Tactical** — interrupt-driven and reactive (e.g., handling pager alerts).
  5. **No enduring value** — the service is in the same state after the task.
  6. **O(n) with service growth** — scales linearly with service size, traffic, or users.
  - When to use: To classify any operational task and decide what to automate.
  - How: The more attributes a task matches, the more likely it is toil; not all are required.
  - Why it works / failure mode: Distinguishes toil from mere dislike or grunge. Beware "needs human judgment" as an excuse: a service paging several times daily with complex judgment-heavy responses is poorly designed; until redesigned, that judgment work *is* toil.
- **50% toil cap (engineering ≥ 50%)**: Keep toil below 50% of each SRE's time; at least 50% on engineering projects that reduce future toil or add service features — averaged over a few quarters or a year (toil is spiky).
  - Why it works: Lets SRE scale sublinearly with service size and keeps the hiring promise that SRE is not an Ops team.
  - How: If project time averages significantly below 50% over the long haul, the team must step back and find what's wrong; for individual outliers, managers spread toil more evenly and steer them to engineering projects.
- **Four categories of SRE activity**:
  - **Software engineering**: writing/modifying code plus design and docs (automation scripts, tools, frameworks, scalability/reliability features, hardening infra code).
  - **Systems engineering**: configuring production or documenting with lasting improvement from one-time effort (monitoring setup, load balancing config, server config, OS tuning; consulting on architecture/productionization).
  - **Toil**: work directly tied to running a service that is repetitive, manual, etc.
  - **Overhead**: administrative work not tied to running a service (hiring, HR paperwork, meetings, bug queue hygiene, snippets, peer reviews, training).
- **Definition of engineering work**: Novel, intrinsically requires human judgment, produces permanent improvement, guided by a strategy, often creative and design-driven — the more generalized the better; lets the same staff handle larger or more services.

## Key Concepts
- **Toil**: Mundane, repetitive operational work with no enduring value that scales linearly with service growth.
- **Overhead**: Necessary admin work not tied to running production (OKRs, snippets, meetings) — not toil.
- **Grungy work**: Unpleasant work that may still have long-term value (e.g., cleaning up alerting config) — not toil.
- **Interrupts**: Non-urgent service-related messages/emails — top source of SRE toil.
- **On-call floor on toil**: Primary + secondary on-call weeks set a minimum toil fraction per rotation size.
- **Sublinear scaling**: Service grows ≥ one order of magnitude with zero additional work beyond one-time resource additions.
- **Snippets**: Googlers' short weekly free-form work summaries (overhead).
- **OKRs**: Objectives and Key Results goal system (Andy Grove, Intel) — overhead.

## Mental Models
- Use "if a human operator needs to touch your system during normal operations, you have a bug" (Carla Geisser) when deciding what to automate — and remember "normal" changes as systems grow.
- Think of toil as a gas: left unchecked it expands to fill 100% of everyone's time.
- Use "did the service end up in a better permanent state?" to separate engineering from toil.
- Think of toil as fine in small doses (calming, quick wins, low stress) but toxic in large quantities.

## Anti-patterns
- **Calling a judgment-heavy alert response "not toil"**: The system is poorly designed and needs simplification or automation.
- **Counting script runs as automation**: The human hands-on time to run it is still toil.
- **Being too willing to absorb toil** ("Sets precedent"): Dev teams get incentives to shift operational work that belongs to them onto SRE.
- **Letting a team devolve into Ops**: Breaks the hiring promise.
- **Consequences of excessive toil** — individual: *career stagnation* ("you can't make a career out of grunge"), *low morale* (burnout, boredom, discontent); organizational: *creates confusion* about SRE's engineering role, *slows progress* (feature velocity drops), *sets precedent*, *promotes attrition* (best engineers leave), *causes breach of faith* (new hires promised project work feel cheated).

## Reference Tables
| On-call rotation size | Weeks on-call per cycle (primary + secondary) | Toil floor |
|---|---|---|
| 6 people | 2 of 6 | 2/6 = 33% |
| 8 people | 2 of 8 | 2/8 = 25% |

| Toil measurement | Value |
|---|---|
| Advertised cap | < 50% toil per SRE |
| Average reported (quarterly surveys) | ~33% |
| Outliers | 0% (pure dev, no on-call) to 80% |
| Top sources (in order) | interrupts → on-call (urgent) response → releases and pushes |

## Worked Example
**Calculating an SRE's toil floor**: A team runs a 6-person on-call rotation, each person doing one week primary and one week secondary per cycle. At least 2 of every 6 weeks go to on-call and interrupt handling, so each SRE's minimum toil is 33% before any tickets, pushes or manual tasks — leaving only 17 points of headroom under the 50% cap. Growing the rotation to 8 drops the floor to 25%. Survey data confirm the pattern: average toil ~33%, dominated by interrupts, then urgent on-call, then releases/pushes — so automating release and push processes is a clear target even where partial automation exists.

## Key Takeaways
1. Classify work with the six toil attributes; don't confuse toil with overhead or valuable grungy work.
2. Enforce ≤ 50% toil per SRE, averaged over quarters; investigate teams persistently below 50% engineering.
3. Measure toil (e.g., quarterly surveys) and rebalance outliers across the team.
4. Compute the on-call toil floor from rotation size; larger rotations lower it.
5. Target the biggest sources first: interrupts, urgent on-call response, releases/pushes.
6. Push back on toil that belongs to developers to avoid setting precedent.
7. Eliminate a bit of toil each week with good engineering — "invent more, and toil less."

## Connects To
- **Ch 1**: The 50% cap on ops work as a core SRE tenet.
- **Ch 7**: Automation as the primary toil-elimination tool.
- **Ch 8**: Release engineering — releases/pushes are a top toil source.
- **Ch 11**: Primary vs secondary on-call and on-call load.
- **Ch 29**: Dealing with interrupts, the top toil source.
- **Ch 30**: Operational overload and recovering teams drowning in toil.
- **Ch 32**: Engagement model — handing operational work back to dev.
- **OKRs (Andy Grove)**: Goal-setting overhead referenced in the toil definition.
