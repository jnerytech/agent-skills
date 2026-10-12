# Chapter 7: The Evolution of Automation at Google
*Authors: Niall Murphy with John Looney and Michael Kacirek (ed. Betsy Beyer)*

## Core Idea
Automation is "a force multiplier, not a panacea": software automation beats manual operation in most cases, but better than both is an **autonomous system** designed to need neither. Its value comes from what it does *and* its judicious application — thoughtless automation multiplies errors at scale.

## Frameworks Introduced
- **The Value of Automation** (five values):
  1. **Consistency** — humans doing a task hundreds of times won't do it the same way; for well-scoped, known procedures, consistency is the *primary* value.
  2. **A Platform** — extensible, reusable, can be spun out; **centralizes mistakes** (fix a bug once and forever); runs more often/at inconvenient times; exports metrics about the process. No automation = "a tax levied on the operation of a system."
  3. **Faster Repairs** — automation resolving common faults reduces **MTTR**; problems caught early are cheaper to fix.
  4. **Faster Action** — machines react faster than humans for well-defined failover/traffic switching; don't make humans press "Allow system to continue to run."
  5. **Time Saving** — most-cited but least calculable; key insight: **decoupling operator from operation** — anyone can run encapsulated automation.
  - When to use: justifying automation beyond a naive time-spent vs time-saved calculation.

- **A Hierarchy of Automation Classes** (evolution path, illustrated with DB failover):
  1. **No automation** — DB master failed over manually between locations.
  2. **Externally maintained system-specific automation** — an SRE has a failover script in their home directory.
  3. **Externally maintained generic automation** — SRE adds DB support to a "generic failover" script everyone uses.
  4. **Internally maintained system-specific automation** — the database ships with its own failover script.
  5. **Systems that don't need any automation** — the DB notices problems and fails over without human intervention.
  - When to use: assessing where a process sits and what the next step is; aim to remove glue logic by handling "first-order" manipulations (adding accounts, turnup) inside the application.
  - Why it works: externally maintained automation suffers **bit rot** (doesn't change when the system changes) and infrequently run automation (e.g., failover every few months) is fragile due to long feedback cycles. Internalizing it keeps it in sync and exercised. Failure mode: stopping at level 2–3 leaves automation owned by people who don't run the system.

- **Automation process dimensions**: **Competence** (accuracy), **Latency** (how quickly all steps execute once initiated), **Relevance** (proportion of real-world process covered).
  - How: evaluate any automation on all three; the turnup story moved from competent/high-latency/relevant → fast but decaying → "worst of all worlds" → low-latency, competent, accurate via service-owned APIs.

- **Service-Oriented Cluster-Turnup (SOA turnup)**: service owners own an **Admin Server** handling turnup/turndown RPCs; each team provides the **contract (API)** turnup automation needs while freely changing implementation; at "network-ready," automation sends an RPC to each participating Admin Server.
  - Why it works: puts maintenance with the domain experts while keeping a uniform interface; scaled as teams, services, and change rate doubled yearly.

- **Prodtest + idempotent fixes**: extend a unit-test framework to test real services in a named cluster; tests chained by dependency, failure aborts the chain; pair each test with an **idempotent fix**, runnable every 15 minutes; if a fix fails multiple times, stop and notify the user.

## Key Concepts
- **Automation as "metasoftware"**: software to act on software.
- **Autonomous vs automated**: autonomous systems self-repair intrinsically; automated ones replace manual actions with external glue.
- **Glue logic**: external code manipulating a system; ideal systems need none.
- **Bit rot**: separately maintained automation diverging from the system it manages.
- **Leaky abstraction**: e.g., assuming binary push is atomic, when it can be staged-not-pushed, pushed-not-restarted, restarted-not-verifiable; causes systemic, repeated, inconsistent failure. Good automation halts and asks for intervention; bad automation doesn't.
- **Decider**: Ads SRE's automated MySQL failover daemon (2009); <30 s failover 95% of the time.
- **MoB (MySQL on Borg)**: MySQL run on Borg, enabled by Decider.
- **Prodtest (Production Test)**: Python unit-test framework extended to validate real-world services per cluster, with a dependency graph of test states.
- **Admin Servers / Local Admin Daemon**: authenticated, ACL-driven, RPC-based replacement for sshd; logs requestor, parameters, results; changes gated on code review.
- **Borg / warehouse-scale computer**: cluster as a "managed sea of resources" with API calls to a central coordinator; rescheduling as intrinsic, like a process moving between CPUs.
- **Diskerase**: decommission step overwriting all disks, verified independently.

## Mental Models
- Think of **automation as a force multiplier**: it amplifies whatever direction it's pointed — including mistakes ("Enabling Failure at Scale").
- Use **"the most functional tools are written by those who use them"** when assigning automation ownership; keep it with service owners.
- Think of the **cluster as one computer**: cluster turnup = adding RAM/disk; rescheduling = process migration; the global computer must self-repair past a certain size because failures are statistically guaranteed every second — so self-introspection is required.
- Use **design-phase leverage**: autonomy is hard to retrofit; decoupled subsystems, APIs, and minimized side effects make it possible. "Reliability is the fundamental feature."

## Anti-patterns
- **Relying on implicit "safety" signals**: automation assumed an unused first disk meant no storage configured → wiped a multi-petabyte Bigtable cluster.
- **Special values for empty sets**: Diskerase's empty set interpreted as "everything" → erased the whole CDN.
- **Free-form SSH scripts**: "a cholesterol of technical debt"; also insecure (root on many machines).
- **Separating automation runners from service owners**: creates bad incentives — turnup team has no incentive to reduce owners' tech debt; non-running teams don't build automatable systems; PMs unaffected by bad automation prioritize features.
- **Non-idempotent fixes with flaky test-fix-test latency**: can leave the system inconsistent.
- **Automation that removes operators from practice**: humans lose fluency and accurate mental models; manual fallbacks quietly cease to exist (Air France 447 analogy). Expose internals and run drills.
- **Judging automation only by time saved**: undervalues consistency, platform, MTTR, speed.

## Reference Tables
| Item | Number |
|---|---|
| Ads DB managed state | 2005–2008 on MySQL |
| Borg task movement | once or twice per week |
| Manual master failover | 30–90 min per instance → best case 99% uptime |
| Required failover downtime | < 30 s to meet error budget |
| Decider | < 30 s failover 95% of the time (2009) |
| Ops time after MoB | mundane ops tasks −95%; total DB maintenance cost −~95% |
| Hardware freed | ~60% |
| Cluster turnup before Prodtest automation | 6+ weeks from network-ready to serving |
| "One Week Turnup" mission | 5 clusters network-ready same day in 3 months; turn up in one week |
| Fix-script cadence | every 15 minutes (idempotent) |
| Changes to affected systems | > 1,000/day |

## Worked Example
**Automate Yourself Out of a Job (Ads MySQL → MoB).** Ads SRE ran a mature MySQL setup and aimed to migrate onto Borg to (a) eliminate machine/replica maintenance and (b) bin-pack instances. The PoC (late 2008) hit a problem: Borg moves tasks 1–2×/week, fine for replicas, unacceptable for masters. Manual failover took 30–90 min; with shared-machine kernel reboots plus normal failures across many shards, manual failover meant ≤99% availability and huge toil, while the error budget required <30 s downtime per failover — impossible for a human. So they built **Decider** (2009): planned and unplanned failovers in <30 s, 95% of the time. Cost: all apps needed more failure handling (e.g., customizing JDBC), since MySQL norms assume the DB is the most stable component. Payoff: mundane ops −95%; single-task outages no longer paged; freed time cascaded into automating schema changes (total maintenance −~95%); bin-packing freed ~60% of hardware. Shift in mindset: from optimizing for a lack of failover to "failure is inevitable — recover quickly through automation." Lesson: go the extra mile to deliver a **platform** rather than just replacing manual procedures.

## Key Takeaways
1. Justify automation by consistency, platform, MTTR, and speed — not only hours saved.
2. Locate each process on the 5-level hierarchy and push toward internal, then autonomous, behavior.
3. Keep automation ownership with the teams that run the service; expose it via service APIs (Admin Servers) rather than central scripts.
4. Make fixes idempotent, add sanity checks and rate limiting, and never treat empty/absent signals as permission to destroy.
5. Replace SSH-as-root with ACL'd, audited, code-reviewed RPC admin interfaces.
6. Design for autonomy early: decoupled subsystems, APIs, minimal side effects.
7. Keep humans in practice (drills, exposed internals) so they can operate when automation fails.

## Connects To
- **Ch 5**: automation as the primary tool against toil.
- **Ch 2**: Borg, Chubby, Bigtable, uniform production environment.
- **Ch 3 / Ch 4**: error budget forced <30 s failover.
- **Ch 8**: rollout automation (Rapid, Sisyphus) and idempotent, gated changes.
- **Ch 17**: Prodtest as production testing; later discovery = more costly.
- **Ch 28**: "Disaster Role Playing" drills to keep operator skills.
- **Ch 23**: automated failover relates to consensus-based leader election.
- **Pets vs cattle**: Google's scale precludes per-machine hand-holding.
- **Ironies of Automation (Bainbridge) / Air France 447**: operator deskilling.
