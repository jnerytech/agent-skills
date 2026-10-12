# Chapter 27: Reliable Product Launches at Scale
*Authors: Rhandeev Singh and Sebastian Kirsch with Vivek Rau (edited by Betsy Beyer)*

## Core Idea
At a high launch rate (up to 70 launches/week at Google), a dedicated SRE consulting team, **Launch Coordination Engineering (LCE)**, plus a curated **launch checklist** makes launches reproducibly reliable without slowing the pace of change.

## Frameworks Introduced
- **Launch Coordination Engineering (LCE)**: a dedicated SRE consulting team for the technical side of launches.
  - When to use: rapid growth (product developers doubling every 1–2 years), services scaling to hundreds of millions of users, and reliability mattering despite a high rate of change.
  - How (roles): (1) audit products for compliance with reliability standards and give specific improvement actions; (2) liaise between the teams involved; (3) drive the technical side and keep momentum; (4) act as gatekeeper and sign off on "safe" launches; (5) educate developers with docs and training.
  - Why it works: **breadth of experience** (cross-product knowledge transfer), **cross-functional perspective** (a holistic view across SRE, dev, PM, and launches spanning 6+ teams and time zones), and **objectivity** (a nonpartisan mediator between SRE, developers, PMs and marketing). LCEs are SREs, so they are incentivized toward reliability. Failure mode: if the process is too burdensome, engineers sidestep it, especially in crunch mode.
- **Criteria for a good launch process**: **Lightweight** (easy on developers), **Robust** (catches obvious errors), **Thorough** (addresses important details consistently and reproducibly), **Scalable** (many simple launches and fewer complex ones), **Adaptable** (common launch types and new ones like Chrome or Fiber). These conflict, especially lightweight vs. thorough.
  - Tactics to balance them: **Simplicity** (get the basics right, don't plan for every eventuality); **A high touch approach** (experienced engineers customize the process per launch); **Fast common paths** (simplified process for recurring launch classes, e.g., launching in a new country).
- **The Launch Checklist**: question, then action item, then pointer (e.g., "Are you storing persistent data?" → "Implement backups; here are instructions"). Full version in Appendix E.
  - Curation rules: every question's importance must be substantiated, ideally by a previous launch disaster; every instruction must be concrete, practical and reasonable for developers. At one point adding a question required VP approval. Make small continuous updates plus a full review once or twice a year.
  - Why it works: like aviation and surgical checklists, it gives consistency and completeness. It also drives **convergence** on common infrastructure: whole sections collapse to "Implement rate limiting using system X."
- **Checklist themes** (how to structure your own): Architecture and Dependencies; Integration; Capacity Planning; Failure Modes; Client Behavior; Processes and Automation; Development Process; External Dependencies; Rollout Planning.
- **Launching the Unexpected**: for a new vertical (e.g., Android, where client code can't be hot-fixed), go back to abstract first principles of a safe launch, structure around broad themes (reliability, failure modes, processes) with domain experts, then re-specialize into concrete items. Keep each question's *intent* in mind so you don't apply items mindlessly.
- **Feature flag frameworks**: requirements are (1) roll out many changes in parallel, each to a few servers/users/entities/datacenters; (2) grow to a larger but limited group, usually 1–10%; (3) route traffic by user, session, object or location; (4) handle failure of new code paths automatically without affecting users; (5) revert each change independently and immediately; (6) measure each change's UX improvement. There are two classes: UI-focused ones (stateless: an HTTP payload rewriter keyed on cookie hash mod range, whitelists/blacklists) and server-side/business-logic ones (stateful: scoped to logged-in user IDs or entity IDs, proxying/rerouting to different servers).
- **Low-risk launch fast path**: no new server executables and traffic increase under 10% means an almost trivial checklist. By 2008, 30% of reviews were low-risk.

## Key Concepts
- **Launch**: any new code that introduces an externally visible change to an application.
- **Canary**: the first stage of a gradual rollout. New software is observed under real traffic and automatically rolled back if it fails the validation period.
- **Gradual and staged rollouts**: a few machines in one datacenter, then all of that datacenter, then global, with observation in between. Also applies to Android app percentages and invite systems.
- **Kill switches** ("Make-children-cry switches" for NORAD Tracks Santa): protective toggles that disable a feature to save services.
- **Server-side client control**: the client periodically downloads config that sets sync/retry rates and toggles features.
- **Dormant functionality**: ship code in the client before activating it. Launches can be aborted by switching it off, and you avoid a combinatorial explosion of release tracks.
- **Exponential backoff with jitter**: increasing, randomized retry delays. Don't retry 4xx errors, but network errors are usually fine to retry.
- **Production Reviews / Launch Reviews**: the formalized LCE consulting sessions, days to weeks before launch.
- **Churn reduction policy**: infrastructure teams may not ship backward-incompatible features until they automate their clients' migration.

## Mental Models
- Use **launch-specific expertise** when a team excels at day-to-day ops but launches rarely. Launch challenges differ from steady-state operation.
- Think of the **checklist as a convergence lever**: every recommended shared system replaces a page of requirements.
- Think of **overload as nonlinear**: services can be slower when idle (cold caches), linear in a middle window, then degrade or lock up. Errors that trigger expensive debug logging, or GC thrashing, can cause a total halt. You can't predict this from first principles, so load test.
- Use **randomness** in every periodic or automated client action (jittered retries, random daily update times) to avoid a thundering herd.

## Anti-patterns
- **Burdensome launch process**: engineers route around it.
- **Unbounded checklist growth**: unmanageable burden. Require evidence (a past disaster) for each item.
- **"Push-button" global launches**: no chance to observe and roll back. "Never change a running system" without staging.
- **Synchronized client behavior**: 2 a.m. updates for all phones, or fixed 1-2-4s retry backoff without jitter, cause spikes that repeat.
- **Misjudged update rates**: a 60s sync instead of 600s means 10x load.
- **Retrying into an overloaded service**: amplifies the overload.
- **Reimplementing common infrastructure** (e.g., your own rate limiter) when hardened shared systems exist.
- **Undocumented manual processes**: a human becomes a single point of failure. Document them so any team member can execute them.
- **Overly cautious, change-averse SREs**: this slows launch velocity, which is one reason LCE was created.

## Reference Tables
| Theme | Example question | Example action item |
|---|---|---|
| Architecture & Dependencies | Request flow user→frontend→backend? Different latency classes? | Isolate user-facing from non-user-facing requests. Validate request volume (one page view → many requests) |
| Integration | — | Set up DNS name, load balancers, monitoring |
| Capacity Planning | Tied to press/ads/blog? Expected traffic and growth? Compute obtained? | Launch region-by-region. Plan N+1/N+2 (3 needed → keep 4–5 deployments) |
| Failure Modes | Single points of failure? How do you mitigate dependency unavailability? | Request deadlines. Load shedding early under overload |
| Client Behavior | Auto-save/auto-complete/heartbeat? | Exponential backoff on failure. Jitter automatic requests |
| Processes & Automation | Manual processes needed to keep running? | Document manual processes and datacenter moves. Automate build/release |
| Development Process | — | Check all code and config into version control. Cut each release on a new release branch |
| External Dependencies | Third-party code/data/services/events? Partners to notify? Missed hard deadline? | Filtering/rewriting proxies, transcoding pipelines, caches |
| Rollout Planning | — | Launch plan with an owner per item. Contingency per risky step (e.g., backup slide deck: "will be launching") |

| Number | Value |
|---|---|
| Launches per week at Google | up to 70 |
| Keyhole on Christmas Eve 2011 | 25x normal peak, >1M req/s |
| Launch spikes vs. estimates | up to 15x higher |
| One LCE over 3.5 years | 350 launches. Team of ~5 means >1,500 launches |
| New LCE training | ~6 months |
| Full-time LCE team founded | 2004 |
| Low-risk share of reviews (2008) | 30% |
| Ops work cap | 50% (Ch 5) |

## Worked Example
**NORAD Tracks Santa (Christmas Eve 2011)**: a whimsical site with every trait of a risky launch: a hard deadline (Santa won't come a week later), heavy publicity, an audience of millions, and a steep ramp. The "virtual fly-over" used Keyhole satellite imagery, which normally serves thousands of images/s and jumped to 25x peak (>1M req/s). LCE coordinated the engineering groups and anticipated failure modes. Kill switches ("Make-children-cry switches") were built in so features could be disabled to protect core services, and capacity was provisioned ahead of a predictable but extreme spike.

## Key Takeaways
1. Define "launch" broadly (any externally visible change) and give frequent launch classes a fast path, e.g., no new binaries and <10% traffic.
2. Curate a launch checklist of question → concrete action → link. Admit items only with disaster-backed justification, and review it yearly.
3. Use the checklist to steer teams onto shared, hardened infrastructure (rate limiting, quotas, data push, release tooling).
4. Roll out gradually: canaries with automatic rollback, percentage rollouts, invites, and feature flags reversible per change.
5. Make clients well-behaved: exponential backoff with jitter, no retry on 4xx, randomized schedules, server-controlled config, and dormant features you can toggle.
6. Load test every significant launch, because overload behavior is nonlinear and unpredictable. Add deadlines and load shedding.
7. Know what LCE can't fix (scalability rearchitecture, growing ops load, infrastructure churn) and handle those with platforms, automation and churn-reduction policy.

## Connects To
- **Ch 8**: release engineering. Release branches, version control of config, automated builds.
- **Ch 21 / Ch 22**: handling overload and cascading failures. Load shedding, deadlines, retries with backoff and jitter.
- **Ch 24 / Ch 25**: thundering herds from synchronized jobs.
- **Ch 5**: the 50% cap on ops work, part of "growing operational load".
- **Ch 26**: the "Are you storing persistent data? → implement backups" checklist item.
- **Ch 32**: the evolving SRE engagement model. PRRs and frameworks address what LCE couldn't.
- **Appendix E (Ch 35)**: the full Launch Coordination Checklist. **Appendix B**: safe-rollout patterns.
- **External**: Gawande's *The Checklist Manifesto*, canary releases, feature toggles, A/B testing.
