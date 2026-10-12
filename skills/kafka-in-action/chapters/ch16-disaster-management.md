# Chapter 16: Disaster Management

## Core Idea
Classify failures by blast radius (network, compute, storage, data center, human) and buy only as much resilience as the business needs: in-cluster replication (`replication.factor` + `min.insync.replicas` + `acks=all`) covers brokers, a stretched cluster across 3+ nearby DCs covers data-center loss, and MirrorMaker 2 topologies cover distant sites. Kafka has no good backup story, so first decide whether a backup is needed at all.

## Frameworks Introduced
- **Failure taxonomy ("What could possibly go wrong?")**: network failures (client-broker, inter-broker), compute failures (broker down), storage failures (full disk, dead disk, central storage), data-center failures, amplified by human error (misconfiguration, maintenance mistakes, weak procedures).
  - When to use: risk assessment before designing a deployment; prioritising which scenarios get engineering money.
  - How: for each class, ask (1) what Kafka does automatically, (2) what the clients must do, (3) what operators must do, (4) whether the business can simply accept the downtime.
  - Why it works: most network failures self-heal and lose no data (async, persisted log; clients just retry/re-consume), so effort should go to the classes that can actually lose data — full disks and correlated storage failure.

- **Broker-failure tolerance = `replication.factor` vs `min.insync.replicas`** (only effective with producer `acks=all`):
  - When to use: sizing topics/cluster for availability.
  - How: RF=3, `min.insync.replicas=2` → lose 1 broker with zero client impact; lose a 2nd → `acks=all` producers fail, consumers keep reading as long as the leader lives, and all load lands on the one survivor. RF=4, `min.insync.replicas=2` → survive 2 broker losses transparently, a 3rd only affects producers. More brokers than RF spreads the survivor load.
  - Failure mode: higher RF raises cost significantly and only protects against broker failure, not the more likely human mistakes — use a multi-cluster setup for that.

- **Permanent broker replacement by broker ID**: rebuild hardware, install Kafka, configure identically, and reuse the *same broker ID*. The controller recognises the ID, the empty broker re-replicates from partition leaders, catches up into ISR, and resumes preferred leadership.
  - Why it works: Kafka identifies brokers only by ID, not by data or host.

- **Stretched cluster**: one Kafka cluster whose brokers (and controller/ZooKeeper quorum) are spread over multiple data centers, so losing a DC looks like losing brokers.
  - When to use: DC-level fault tolerance where sites are close (cloud availability zones, not regions).
  - How: (1) ≥3 data centers; (2) latency ≤ ~30 ms; (3) set `broker.rack` to the DC/AZ name on every broker so new topics spread replicas across racks; (4) rebalance existing topics with Cruise Control; (5) set `client.rack` on consumers to fetch from the local follower (KIP-392) and cut cross-AZ traffic.
  - Failure mode: with only 2 DCs the quorum majority sits in one DC; losing it kills the coordination cluster and the whole Kafka cluster. Cross-AZ traffic is a major cloud cost driver.

- **MirrorMaker 2 (Kafka Connect-based) mirroring**: continuous, asynchronous copy of topics, ACLs and consumer offsets between clusters over long distances via three connectors — `MirrorSourceConnector` (topics + ACLs), `MirrorCheckpointConnector` (consumer offsets), `MirrorHeartbeatConnector` (connectivity checks). Proprietary alternative: Confluent Replicator.

- **Mirroring topologies**: active-passive, active-active, hub-and-spoke (see Reference Tables).

## Key Concepts
- **`min.insync.replicas`**: minimum ISR count for an `acks=all` write to succeed; defines how many broker losses producers tolerate.
- **Broker ID**: the only identity Kafka uses for a broker; reusing it makes an empty broker take over the old one's replicas and leaderships.
- **Multiple log directories (JBOD)**: several `log.dirs` without RAID; a failed directory is reported to the controller while the others keep serving, then the replaced disk re-replicates from leaders.
- **`broker.rack`**: broker location label (rack, AZ or DC) used for rack-aware replica placement.
- **`client.rack`**: consumer-side location label enabling fetch-from-follower (KIP-392).
- **2.5 data center setup**: two full DCs plus a "light" third site hosting only one coordination node — tolerated, not recommended.
- **Remote topic**: MirrorMaker 2 topic prefixed with the source cluster name; never re-mirrored (prevents loops) and made read-only via ACLs.
- **REGEX subscription**: consumer subscribes to all topics matching a pattern, used to read local + remote topics together.
- **Kannika**: commercial Kafka backup/restore and cluster-cloning tool (with data masking for test environments).

## Mental Models
- Think of a stretched cluster as turning "a data center died" into "some brokers died" — the same replication math applies.
- Think of producers, not consumers, as the decision point during network outages: consumers just wait; producers must choose to block, buffer, drop, or crash and surface unavailability.
- Use MirrorMaker when distance exceeds ~30 ms or you need independent clusters; use a stretched cluster when sites are nearby AZs.
- Ask "Can the data be re-imported from the source system?" before designing any Kafka backup — if yes (or if data lives seconds), skip backups.

## Anti-patterns
- **Letting a volume fill up**: Linux handles full volumes badly and Kafka relies on the OS page cache to flush; unflushed data can be lost, permanently if all identically configured brokers fill at once. Stop Kafka before the disk fills; keep a spare ~10 GB file to delete in an emergency.
- **Stretched cluster over 2 DCs**: the quorum majority lives in one DC; that DC failing takes down the cluster.
- **Stretching across cloud regions**: exceeds the ~30 ms latency Kafka is tuned for — mirror instead.
- **Raising RF as the reliability answer**: costly, and doesn't protect against human error.
- **Filesystem snapshots as a real backup**: redundant data (replicas), lose everything after the snapshot, and non-simultaneous snapshots plus partition moves can miss partitions entirely.
- **Kafka Connect → S3 as "backup"**: restores data but not consumer offsets, so consumers can't resume exactly.
- **Tiered storage as backup**: doesn't cover compacted topics or `__consumer_offsets`, and segment offload timing is unpredictable.
- **Running a consume-and-produce service in both DCs of an active-active pair without dedup**: each order is processed twice (e.g., double payment).
- **Building DC-failure protection reflexively**: stretched/mirrored clusters dramatically increase complexity and cost; Kafka is rarely the biggest problem when a DC is gone.

## Code Examples
The chapter has no listings; the settings it relies on, collected (illustrative):
```properties
# Broker (each DC/AZ gets its own label)
broker.rack=dc-a
log.dirs=/data/disk1,/data/disk2,/data/disk3

# Topic
replication.factor=3
min.insync.replicas=2

# Producer
acks=all

# Consumer (KIP-392 fetch-from-follower)
client.rack=dc-a
```
- **What it demonstrates**: the full set of keys that make a stretched, rack-aware, durable cluster — replica spread, broker-loss tolerance, and local-replica reads.

## Reference Tables

**Broker-loss tolerance (RF = number of brokers, producers use `acks=all`)**

| RF | `min.insync.replicas` | Transparent broker losses | Next loss affects | Consumers still work while |
|---|---|---|---|---|
| 3 | 2 | 1 | Producers blocked at 2nd loss | Leader replica alive (up to 2 losses) |
| 4 | 2 | 2 | Producers blocked at 3rd loss | Leader replica alive (up to 3 losses) |

**Failure classes and responses**

| Failure | Data loss risk | Mitigation |
|---|---|---|
| Client↔broker network | Low (retry/re-consume) | Monitoring, producer policy: block/buffer/drop/crash |
| Inter-broker network | Low; spurious leader elections, under-replication | Wait for restore; redundant network |
| Broker down (temporary) | None with RF/ISR set correctly | Restart broker |
| Broker lost (permanent) | None | New host, same config, same broker ID → re-replicates |
| Disk full | High, possibly permanent if all brokers hit it together | Alert early, stop Kafka first, grow volume (VM/K8s), 10 GB spare file |
| Single disk dead | None with multiple `log.dirs` | Replace disk; broker refills from leaders |
| Central storage dead | Likely | Fix and restart; little Kafka can do |
| Whole DC | Total in single-DC cluster | Off-site backup and rebuild, stretched cluster, or mirroring |

**MirrorMaker 2 topologies**

| Topology | Shape | Failover behaviour | Best for | Drawback |
|---|---|---|---|---|
| Active-passive | One cluster serves clients, mirrored to idle twin | Clients switch to passive | Two distant DCs; DC/cloud migrations | After failover the old active is out of sync; must delete and recreate a new passive every time |
| Active-active | Two equal clusters mirror each other via remote topics | Survivor keeps running; unconsumed messages read from remote topics; little or no action | Recommended for resilience | Duplicate processing risk in consume-produce services; needs idempotence/dedup |
| Hub-and-spoke | Central hub aggregates spoke clusters; hub can push topics (e.g., commands/prices) back | Spokes run autonomously when disconnected; sync both ways on reconnect | Retail chains, cruise ships, government ops, HQ analytics | Spokes may run on stale data (old prices) |

## Worked Example
**Active-active payments with remote topics.** DC1 and DC2 each run a cluster and a MirrorMaker that mirrors the other's topics in as remote topics (e.g., `dc1.orders` appears in DC2), read-only via ACLs and never mirrored back. Producers write only to their local `orders`. Consumers use a REGEX subscription to read `orders` plus the remote `dc1.orders`. Trap: a payment service consumes orders and writes to `payment-status`; deployed in both DCs and reading local + remote topics, each order gets charged twice. Fix: make processing idempotent and deduplicate on a transaction ID so each payment executes exactly once across DCs. Payoff: when DC1 dies, DC2's producers and consumers keep going, and DC2 drains the not-yet-consumed DC1 messages from the remote topic; when DC1 is back, operations resume as before. Caveat: MirrorMaker is asynchronous, so the newest messages not yet mirrored can be lost.

## Key Takeaways
1. Pair `acks=all` with `min.insync.replicas` = RF−1 (RF=3/minISR=2 baseline); add brokers beyond RF so a survivor isn't swamped.
2. Never let Kafka run out of disk — alert early and stop Kafka before it fills, because correlated full disks can cause permanent loss.
3. Replace dead brokers by reusing the broker ID; use multiple `log.dirs` so one dead disk doesn't kill the broker.
4. Stretch only across ≥3 nearby sites (≤30 ms), set `broker.rack` everywhere and `client.rack` on consumers to contain cross-AZ cost.
5. Decide whether you need backups at all; if Kafka is the source of truth, none of snapshots, Connect→S3 or tiered storage is complete (offsets and compacted topics get missed).
6. Prefer active-active MirrorMaker 2 over active-passive, and build idempotence/dedup into services that run in both sites.
7. Treat mirroring as asynchronous: expect a small loss window equal to mirroring lag.

## Connects To
- **ch05**: replication, ISR, `acks` and `min.insync.replicas` are the durability base for broker-failure tolerance.
- **ch07**: KRaft/ZooKeeper quorum majority is why stretched clusters need 3 sites.
- **ch10**: tiered storage limits (compacted topics, offsets) explain why it isn't a backup.
- **ch11**: MirrorMaker 2 and S3 sink "backups" are Kafka Connect connectors.
- **ch14**: Cruise Control for rebalancing replicas across racks; operational procedures.
- **ch15**: disk usage, under-replicated partitions and network alerts detect these failures early.
- **ch08 / ch09**: idempotent producers, transactional IDs and REGEX subscriptions used in active-active.
- **KIP-392**: fetch-from-follower via `client.rack`.
- **RPO/RTO planning**: the topologies trade cost against recovery time and loss window.
