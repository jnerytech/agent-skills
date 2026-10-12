# Chapter 23: Managing Critical State: Distributed Consensus for Reliability
*Authors: Laura Nolan (edited by Tim Harvey)*

## Core Idea
Whenever a system needs leader election, critical shared state, or distributed locking, use a formally proven, thoroughly tested distributed consensus system (Paxos, Raft, Zab, Mencius, usually consumed as a service like Chubby, Zookeeper, Consul, etcd). Ad hoc methods such as heartbeats, timeouts and gossip are "a ticking bomb." After that, the hard part is deployment: how many replicas, where they live, and how they perform under real network latency and disk-logging costs.

## Frameworks Introduced
- **"Everything is distributed consensus" recognition rule**: master election, group membership, distributed locking and leasing, reliable distributed queuing and messaging, and any critical shared state that has to look the same to every process are all versions of the distributed consensus problem.
  - When to use: at design review, whenever you see "leader", "lock", "lease", "membership", "exactly one", or "committed to the queue."
  - How: (1) name the shared decision; (2) refuse heartbeat, STONITH or gossip solutions; (3) delegate it to a proven consensus service (Chubby, Zookeeper, etcd, Consul) rather than an in-app library; (4) build on higher-level primitives (RSM, lock service, queue), not raw Paxos.
  - Why it works / failure mode: leader election is a reformulation of asynchronous consensus, so timeouts cannot solve it correctly. A slow or lossy network (not a clean partition) produces split brain (two masters writing) or mutual STONITH (both down). The informal approach fails exactly when the network is degraded, which is when you need it most.
- **CAP theorem (applied)**: you can't have Consistency, Availability and Partition tolerance all at once. Partitions will happen, so the real design question is how consistency and availability trade off *for your application*.
  - When to use: choosing between ACID/consensus-backed storage and BASE/eventually consistent storage.
  - How: for critical state, take consistency (correctness can't be sacrificed for performance, e.g. financial data). Keep BASE and multimaster "latest timestamp wins" for data that tolerates staleness, and remember that clock drift makes timestamps unreliable.
- **Safety vs. liveness under FLP**: the FLP impossibility result says no asynchronous consensus algorithm can guarantee progress over an unreliable network. In practice, the protocol guarantees *safety*, and enough redundancy, network connectivity and **randomized backoff** encourage *liveness*.
  - How: provision enough healthy replicas and use randomized delays on retries and leader election, so you avoid cascades and dueling proposers.
- **Replicated State Machine (RSM) pattern**: the same operations are executed in the same order on several processes. Consensus orders the operations, and the RSM executes them. Any deterministic program can be made highly available as an RSM.
  - Builds: replicated datastores and config stores (consensus sits in the critical path, so throughput matters), leader-election services (consensus is off the critical path), barriers, locks, and queues (atomic broadcast is equivalent to consensus).
  - Lagging members catch up through a sliding-window protocol.
- **Highly Available Processing Using Leader Election**: write the service as a simple single-process program, replicate it, and use leader election so that only one leader works at a time (coarse mutual exclusion). Used by GFS and Bigtable masters.
- **Leases, not locks**: use renewable leases with timeouts instead of indefinite locks, and lease queue tasks instead of removing them outright, so a crashed holder can't block forever. Most applications should use a higher-level system with distributed transactions rather than raw locks.
- **Replica-count trade-off**: decide the number of replicas by weighing *reliability need, frequency of planned maintenance, risk, performance, cost*.
  - How: use majority quorums of 2f+1 to tolerate f failures (3f+1 for Byzantine). Three replicas is the minimum. Use five so the system survives one replica down for maintenance *plus* one unplanned failure. With 4/5 alive no action is needed; with 3/5 left, add replicas.
- **Replica-location trade-off**: balance the *failure domains* you need to survive against *latency*. Optimize for client-perceived RTT, and don't widen the failure domain beyond your clients' (if every client is in New York, surviving a New York outage buys nothing). Keep snapshot backups elsewhere anyway: you can never escape software bugs or human error.
- **Hierarchical quorums**: when member RTTs differ a lot, deploy 9 replicas as 3 groups of 3. A quorum is a majority of groups, and each group needs a majority of its members. Losing one replica in the central group then barely affects latency.

## Key Concepts
- **Asynchronous distributed consensus**: agreement among processes over a network with unbounded message delays. This is the variant that applies to real software systems.
- **Crash-recover vs. crash-fail**: crash-recover algorithms let nodes return after transient faults and are the useful kind in practice.
- **Byzantine failure**: a process sends incorrect messages because of a bug or malice. It costs more to tolerate (3f+1 replicas).
- **Paxos**: a sequence of numbered proposals. A proposer gets a majority of acceptors to promise (they promise only if they haven't seen a higher number), then commits a value. Any two majorities overlap, and acceptors journal to disk before agreeing.
- **Multi-Paxos / strong leader**: a stable leader skips Phase 1 (Prepare/Promise) within a view (leader term), so one round trip to a quorum reaches consensus.
- **Dueling proposers**: a livelock in which competing proposers keep preempting each other. Fix it with a single elected proposer or rotating slots, plus randomized timeouts.
- **Quorum leases**: a quorum of replicas gets a time-bounded read lease on a subset of state, which allows strongly consistent local reads. Writes must then be acknowledged by every lease holder.
- **Pipelining**: several batched proposals are in flight at once ("keep the pipe full", like a TCP sliding window), still globally ordered by view and transaction number.
- **Failure domain**: the set of components a single failure can take out (machine, rack/PDU, network switch, datacenter/fiber, region/hurricane).
- **Atomic broadcast**: every participant receives messages reliably and in the same order. It is equivalent to consensus.

## Mental Models
- Think of **a slow network as worse than a dead one**. A partition you can see is simpler to handle than slowness, partial packet loss, or one-way throttling, and those are what break heartbeat-based failover.
- Use **raw consensus algorithms like assembly language**: they agree on one value once. Put RSMs, datastores, lock services and queues on top, consumed as a service.
- Think of **a leader as a bandwidth hot spot**: its Accept messages carry the full payload while followers send only small ACKs. Spread shard leaders across datacenters, or a single datacenter becomes the outgoing-bandwidth bottleneck and failover sends a traffic surge across the remaining links.
- Use **"human escalation is not a fallback"**: if the network is too damaged for consensus to elect a master, an overloaded on-call human is no better placed to do it.

## Anti-patterns
- **STONITH plus heartbeats for leader election**: on a lossy network both nodes can shoot each other (unavailable), or both can take mastership (corruption).
- **Gossip-based group membership with local master election**: after a partition, each side elects its own master and accepts writes, causing split brain and data corruption.
- **Escalating failover to a human**: there is no data loss, but availability suffers, operational load rises, and humans scale poorly in the large incidents where this case actually comes up.
- **Leaving consistency to application developers (BASE everywhere)**: developers end up spending a large share of their time on complex, error-prone code to cope with stale data.
- **Assuming consensus is too slow**: with batching, pipelining, stable leaders, proxies and log co-location it runs at the core of Google's critical systems.
- **Assuming Fast Paxos is always faster**: if clients are far from acceptors that are close to each other, N parallel slow-link messages lose to one slow message plus N fast ones (latency tail effect). Client proposers also make batching harder.
- **Adding a 6th replica to a 5-replica group**: the quorum becomes 4, so tolerance drops from 40% to 33% unavailable. If the extra replica is co-located with another, a datacenter outage takes both spares at once.
- **Automatic leader placement that clusters leaders** (nearest-to-clients, fastest machines, longest-running process): leaders end up correlated with one datacenter, and its failure causes a dramatic traffic shift.
- **Routing reads purely to the nearest replica**: a regional spike overloads the nearest replica, then the next, and so on in a cascade (Ch 22). Batch jobs starting together often trigger it.

## Code Examples
Latency formula for one Multi-Paxos operation (Phase 2):
```
latency = 1 disk write (proposer)
        + parallel messages to acceptors
        + parallel disk writes at acceptors
        + return messages
```
What it demonstrates: network RTT and synchronous disk logging are the two physical limits. A variant that disk-bound systems can use has the proposer log in parallel with the acceptors and send an explicit Accept, so latency is about two messages plus one parallel quorum disk write. The book's number: about 10 ms per small random write gives roughly 100 consensus ops "per minute" (as printed; the arithmetic gives ~100/s).

## Reference Tables
| Item | Value |
|---|---|
| Replicas to tolerate f non-Byzantine failures | 2f + 1 |
| Replicas to tolerate f Byzantine failures | 3f + 1 |
| Minimum practical replicas | 3 (tolerates 1) |
| Recommended for critical consensus (Chubby/Zookeeper) | 5 (tolerates 2; quorum 3; 40% can be down) |
| 6 replicas | quorum 4; only 33% can be down |
| RTT within a datacenter | ~1 ms |
| RTT within the US | ~45 ms |
| RTT New York to London | ~70 ms |
| Disk log write | 1 to several ms |
| Initial TCP window | 4–15 KB |

**Strongly consistent reads need one of:** a read-only consensus operation; a read from the guaranteed most up-to-date replica (the stable leader); or quorum leases.

**Monitoring checklist for consensus systems:** members running and health per group; persistently lagging replicas; whether a leader exists (no leader means totally unavailable); number of leader changes (rapid changes mean flapping, and a *decreasing* view number means a serious bug); consensus transaction number (must keep increasing); proposals seen vs. agreed; throughput and latency. For performance work, also watch proposal-acceptance latency distributions, inter-site network latency distributions, time acceptors spend on durable logging, and bytes accepted per second.

## Worked Example
**Transatlantic quorum composition.** Place five replicas: two in the central US, one on the US east coast, two in Europe. Usually North America reaches quorum without waiting for Europe, and Europe reaches quorum by talking only to the east-coast replica, which acts as the linchpin where the two quorums overlap. If the east-coast replica is lost, every quorum must cross the EU-to-central-US link, and its RTT is about 50% higher than EU-to-east-coast, so latency jumps for everyone. Fix: a **hierarchical quorum** of 9 replicas in 3 groups of 3, where the quorum is a majority of groups and each group needs a majority of members. Losing one central replica leaves that group able to vote with 2 of 3. To offset the extra cost in a sharded, read-heavy system, run fewer consensus groups so the total process count stays the same.

## Key Takeaways
1. Treat any leader, lock, lease, membership or "exactly once" requirement as a consensus problem, and use a proven service for it, never heartbeats or gossip.
2. Run 5 replicas for critical consensus (3 at minimum) across distinct failure domains. Never add an even-numbered extra replica casually.
3. Get performance from a stable leader, batching plus pipelining, regional proxies for client connections, and one combined consensus/RSM log. Use quorum leases or replica reads for read-heavy loads when stale reads are safe.
4. Tune leader election with randomized backoff to avoid dueling proposers, and spread shard leaders across datacenters.
5. Size failure domains to match where your clients are, and still back up snapshots outside the consensus group (software bugs and human error are inescapable).
6. Monitor leader existence, leader-change rate, transaction-number progress and lagging replicas.

## Connects To
- **Ch 24**: distributed cron is built directly on Paxos (a Fast Paxos leader acts as cron leader).
- **Ch 25**: Workflow uses Chubby to elect the Task Master writer and Spanner journals.
- **Ch 22**: routing reads to the nearest replica can cascade under regional spikes.
- **Ch 26**: snapshot backups protect against software bugs and human error that replication can't.
- **Ch 2**: Chubby lock service in Google's production environment.
- **Raft / Zookeeper / etcd**: open-source equivalents of the consensus-as-a-service pattern.
- **FLP impossibility, CAP theorem, Jepsen (Kingsbury)**: theoretical and empirical background.
