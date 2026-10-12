# Chapter 26: Data Integrity: What You Read Is What You Wrote
*Authors: Raymond Blum and Rhandeev Singh (edited by Betsy Beyer)*

## Core Idea
Users can't tell data loss, corruption and extended unavailability apart, so data integrity really means data *availability*: the data has to be accessible and correct when users want it. You get there through defense in depth (soft deletion, tiered backups, early out-of-band detection), and you prove it by running restores continuously, not by taking backups.

## Frameworks Introduced
- **Data integrity is the means; data availability is the goal**: "data integrity without expected and regular data availability is effectively the same as having no data at all."
  - When to use: framing any backup/storage investment, or setting SLOs for data.
  - How: define **SLOs for data availability** across failure modes, then practice and demonstrate that you meet them. Don't make teams "practice backups".
  - Why it works: the payoff (restore) is visible, while "backups are a tax" paid for the service of guaranteed data availability. Failure mode: a provider who kept the data but couldn't serve it for ~10 days still lost its users.
- **"No one really wants to make backups; what people really want are restores"** / Delivering a Recovery System, Rather Than a Backup System: recovery requirements drive backup decisions, never the reverse.
  - How: let your recovery scenarios dictate (1) which backup and recovery methods to use, (2) how often you set restore points (full/incremental), (3) where you store backups, (4) how long you keep them. Ask two questions: *how much recent data can you afford to lose?* and *how quickly do you need to recover?*
- **The 24 Combinations of Data Integrity Failure Modes**: 3 factors in any combination.
  - **Root cause** (6): user action, operator error, application bugs, infrastructure defects, faulty hardware, site catastrophes.
  - **Scope** (2): widespread vs. narrow/directed.
  - **Rate** (2): big bang (1M rows → 10 rows in a minute) vs. creeping (10 rows/min for weeks).
  - When to use: designing a data integrity program. A strategy against a creeping bug won't help when your datacenter burns, and vice versa.
- **Defense in depth (three layers + overarching replication)**: each layer protects against progressively rarer loss scenarios.
  - Layer 1, **Soft deletion** (and **lazy deletion** in developer/cloud offerings).
  - Layer 2, **Backups and their related recovery methods** (tiered).
  - Layer 3, **Early detection** (out-of-band data validation).
  - Overarching: **Replication**, occasionally useful for recovery, but plans must not rely on it.
  - Why it works: each protection mechanism is assumed to fail like everything else, so you need uncoupled practices that each protect well on their own.
- **First-layer roles (sum-up)**:
  - Trash folder = primary defense against user error.
  - Soft deletion = primary defense against developer error, secondary against user error.
  - Lazy deletion = primary defense against internal developer error, secondary against external developer error.
  - Revision history counts as a form of trash only if deletion doesn't wipe history. Apply soft/lazy deletion to revision history too.
- **Tiered backup strategy**:
  - Tier 1: many frequent, quick-restore backups close to the live datastore (same or similar storage tech). Retained hours to single-digit days, restore in minutes. Covers most software bugs and developer error.
  - Tier 2: fewer backups on random-access distributed filesystems local to the site. Retained single to low-double-digit days, restore in hours. Covers storage-technology mishaps and bugs detected too late for tier 1. If you release twice a week, keep these at least 1–2 weeks.
  - Subsequent tiers: nearline/offline (tape libraries, offsite media). Taken less often, kept longer, protect against site-level failure. They don't contend with live storage growth.
- **Trust points + incremental + sharded backup (1T vs 1E)**: at exabyte scale, verify data once it's immutable ("trust points"), back up only what changed since, and shard copy/verify work across N independent tasks (balanced, independent shards, no contention among sibling tasks).
- **Out-of-band data validation**: pipelines (MapReduce/Hadoop) that check invariants within and between datastores.
  - How: validate only "invariants that cause devastation to users". Too strict and engineers abandon it, too loose and corruption slips through. Run it at least daily. As scale grows, use tiered validation: cheap daily checks catch the most disastrous cases within 24h, and more rigorous checks run less often.
  - Requirements: validation job management; monitoring, alerts and dashboards; rate-limiting features; troubleshooting tools; production playbooks; data validation APIs that make validators easy to add and refactor.
  - Org model: a central infrastructure team owns the validation framework, and product teams own the custom business-logic validators.
- **Knowing That Data Recovery Will Work**: continuously test the recovery process as part of normal operations, and alert when a recovery process fails to provide a heartbeat of success. "You only know that you can recover your recent state if you actually do so." Automate full end-to-end tests.
- **General Principles of SRE as Applied to Data Integrity**: Beginner's Mind, Trust but Verify, Hope Is Not a Strategy, Defense in Depth, Revisit and Reexamine.

## Key Concepts
- **Data integrity**: accuracy and consistency of data over its lifetime. From the user's view it means services stay accessible and that access stays "in perfect shape".
- **Soft deletion**: deleted data is immediately marked as such and usable only by administrative code paths (legal discovery, hijacked-account recovery, support), then destroyed after a delay.
- **Lazy deletion**: behind-the-scenes purging controlled by the storage system. Data is inaccessible to the app but kept by the provider for up to a few weeks.
- **Point-in-time recovery** ("**time-travel**" inside Google): restoring each affected artifact to its own unique point in time, which creeping corruption requires.
- **Backup vs. archive**: backups can be loaded back into the application within service uptime needs. Archives serve auditing, discovery and compliance, and slow retrieval is fine for them.
- **Replication is not recoverability**: replicas faithfully propagate corrupt rows and errant deletes.
- **Media/layer diversity**: protecting against a failure at layer X requires storing data on diverse components at that layer (tape vs. disk driver bugs; "clay tablets").
- **Retention**: how long you keep copies. Creeping losses need older snapshots, and merging those with live state is hard.
- **Trust points**: portions of data verified after becoming immutable (usually through the passage of time), which enables incremental backup.
- **ACID vs. BASE**: transactional vs. "Basically Available, Soft state, Eventual consistency". Mixed, uncoordinated backups across both complicate restores and referential integrity.

## Mental Models
- Think of **backups as a tax** that funds the municipal service of data availability. Sell the service (restore), not the tax.
- Think of **uptime and integrity as independent SLOs**: 99.99% uptime is about an hour a year, but 99.99% good bytes in a 2 GB file is ~200 KB garbled, which is catastrophic.
- Use **proactive detection plus rapid repair** when you want near-100% integrity. If corruption is found and fixed in 30 minutes before users see it, the object is 99.99% available and effectively 100% intact.
- Think of a **latent broken restore as a light bulb** that already failed: you only notice when you flick the switch in the dark. Test continuously.

## Anti-patterns
- **"We have something better than backups: replication"**: replication copies corruption and deletes to every replica before you can isolate the problem.
- **Exports onto the same filesystem as the database**: a low-level zero-day or driver bug takes out both copies.
- **Treating backup as neglected, deferred sysadmin work**: low risk but high impact, and it can make or break the company.
- **Relying on an infrequently used redundancy scheme**: its only "tests" are your rare recoveries. Pick a scheme in common, continual use.
- **Manual, staged recovery tests**: they turn into drudgery done neither deeply nor often enough. Automate them and run them continuously.
- **Over-strict validators**: legitimate changes fail them, so engineers abandon validation altogether.
- **Trusting a consistent-storage API (e.g., Paxos-backed Megastore) to guarantee integrity**: "perfect algorithms may not have perfect implementations". Trust storage systems, but verify.
- **Per-user deletion-rate alerts**: they're noisy. Alert on the *global* deletion rate crossing an extreme threshold (e.g., 10x the observed 95th percentile).
- **Lazy deletion where privacy guarantees require timely destruction**, or long lazy deletion periods for short-lived data (too costly).

## Reference Tables
| Item | Number |
|---|---|
| "Too long" unavailable threshold for Google Apps | 24 hours (starting point) |
| Gmail 2011 incident duration | 4 days, "perhaps too long" |
| Common soft-deletion delays | 15, 30, 45 or 60 days (most issues surface within 60, so beyond 60 is hard to justify) |
| Gmail trash retention | 30 days |
| Google backup reach for many services | 30–90 days |
| Copy-time scaling example | DB replication: seconds. Export snapshot to FS: ~40 min. Full FS backup: hours |
| 700 PB at 300 MB/s (SATA 2.0), single task | ~8 decades to iterate/verify |
| 3-yr full + daily incrementals | Restore chains >1,000 interdependent backups |
| Gmail validator detection window | within 24 hours. Largest validator split into 10–14 shards, one per day |
| Gmail validator refactoring | cut disk-spindle contention 60% |
| Google study of 19 recovery efforts | most common: deletion or loss of referential integrity from software bugs. Hardest: low-grade corruption found weeks to months later |

## Worked Example
**Google Music, March 2012: Runaway Deletion Detection**
1. *Detect (Mar 6–7)*: a user reports skipped tracks. The engineer finds the track metadata missing its audio reference and digs for the root cause rather than patching it. A privacy deletion pipeline, refactored and first run on Feb 6, had removed the references.
2. *Stop the bleeding*: the issue is escalated to top priority and the pipeline is disabled. A hasty MapReduce sizes the damage on Mar 8: ~600,000 audio references, 21,000 users.
3. *Split teams*: developers hunt the root cause (and chase one red herring, a supposedly buggy upstream storage service). The most experienced SREs run the recovery in parallel.
4. *First wave*: only 436,223 tracks were on tape, and ~161,000 had been deleted before backup. The tape stack couldn't handle one huge restore, so SRE programmatically issued **5,475 restore jobs** (by hand it would have been 3+ days of typing). That produced 5,337 tapes recalled by truck, 1.5 PB. Technicians loaded tapes by hand, which DiRT had shown to be hundreds of times faster than vendor robots. Problems: a vendor omitted 1,862 tapes and 17 tapes were bad, so redundancy tapes were recalled thanks to redundant encoding. By Mar 11 restores were at >99.95%. An unrelated outage paused work for 2 days, and all 436,223 tracks were back on Mar 13: ~7 days total, 5 of them actual recovery.
5. *Second wave*: store-bought and promo tracks were reinstated from the store copies. User-uploaded tracks were re-requested from clients, which took more than a week.
6. *Root cause*: a race condition between pipeline stages that assumed strict timing between short-lived secondary copies. As data grew and optimizations accumulated, its probability rose, and the refactor made it common. Fix: redesign the pipeline and add monitoring for runaway global deletion.
- Success factor: annual **DiRT** testing weeks earlier had exercised the tape tools.

(Contrast: **Gmail, Feb 2011, restore from GTape**. Many simulations beforehand let the team estimate restore time, finish within hours of the estimate, and recover 99%+ of data before it.)

## Key Takeaways
1. Set SLOs for data *availability* per failure mode and practice meeting them. Measure restores, not backups.
2. Layer defenses: trash, then soft deletion (~30–60 days), then lazy deletion, then tiered backups (minutes, hours, offsite), then daily out-of-band validation.
3. Build soft-delete and undelete into platform APIs *and enable it by default*. The worst deletions come from developers unfamiliar with deletion code in batch pipelines.
4. Validate only user-devastating invariants, run validators daily, and give on-call playbooks, investigation tools and dashboards for validation failures.
5. Automate end-to-end recovery tests continuously, with heartbeat alerts. Check that backups are non-empty, resources suffice, wall time is reasonable, progress is observable, and there are no off-hours external dependencies.
6. Revisit data-integrity assumptions when features change. Shakespeare's index was re-creatable, but user annotations aren't, so add a tested backup/restore validated by DiRT.
7. Shrink time-to-recover N toward 0, then shift from planning recovery to planning prevention.

## Connects To
- **Ch 3 / Ch 4**: uptime vs. integrity as separate SLOs. Data-availability SLOs.
- **Ch 23**: Paxos/Megastore. Consistent algorithms still need verification.
- **Ch 25**: data processing pipelines. The deletion-pipeline race condition and validation pipelines are built on them.
- **Ch 17**: testing for reliability. Restore testing works like unit tests that give developers "courage" to move fast.
- **Ch 13 / Ch 33**: DiRT and emergency preparedness enabled both case-study recoveries.
- **Ch 15**: root-cause culture (fix at root, not the symptom).
- **Ch 2**: the Shakespeare service example.
- **External**: ACID/BASE, Reed-Solomon erasure codes, GFS replication, RPO/RTO (recovery point/time objectives).
