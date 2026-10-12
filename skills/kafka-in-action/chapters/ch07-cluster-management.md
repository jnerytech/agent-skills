# Chapter 7: Cluster management

## Core Idea
Cluster management in Kafka means solving distributed consensus: which node is the controller, who leads which partition, which brokers are alive, and where the configuration lives. KRaft (Raft-based, metadata held in the `__cluster_metadata` log) replaces ZooKeeper. It is faster, scales to more partitions, and means operating one system instead of two. Plan a zero-downtime migration off ZooKeeper now. This is a short chapter, so this file sits below the normal length budget.

## Frameworks Introduced
- **KRaft process roles (`process.roles`)**: every Kafka node runs as a `controller`, a `broker`, or both (combined mode).
  - When to use: every new cluster. KRaft is production-ready since 3.3.0, ZooKeeper is deprecated since 3.5.0, and ZooKeeper support is removed in 4.0.
  - How: (1) Run an **odd** number of controllers: 1 for dev (no failover), 3 to tolerate 1 failure, 5 to tolerate 2. Four buys nothing over three. (2) The controller quorum elects one **active controller**. It watches brokers, assigns partitions and leaders, and reassigns them on failure. The others are **standby controllers** that take over immediately. (3) Run at least 3 normal brokers that serve clients, store data and replicate. (4) In production, keep controllers and brokers **separate**, which makes scaling brokers and operations simpler. In non-production you can use combined controller-brokers to save resources, and in local dev a single JVM can run both roles.
  - Why it works / failure mode: Kafka is already excellent at logs, so storing metadata as a replicated Kafka topic removes ZooKeeper's extra abstraction and the lag between ZooKeeper and the brokers. Failover is near-instant. Under ZooKeeper, a controller failure could cause problems for minutes on large clusters.
- **ZooKeeper-to-KRaft migration (zero downtime)**: Upgrade → Migrate → Upgrade.
  - When to use: any cluster still on ZooKeeper. Migrate as soon as possible.
  - How:
    1. Upgrade to the latest Kafka version that still supports ZooKeeper, using the normal upgrade procedure.
    2. Provision 3 or 5 **new dedicated** KRaft controllers with the **same cluster ID** as the ZooKeeper cluster, `zookeeper.metadata.migration.enable=true`, and `zookeeper.connect=<Zookeeper address>`.
    3. On the existing brokers, set `zookeeper.metadata.migration.enable=true` and add the connection info for the new controllers. The controllers copy the metadata from ZooKeeper. Wait for the log line `Completed migration of metadata from ZooKeeper to KRaft`. You can still roll back at this point.
    4. Switch the normal brokers to KRaft: remove the migration flag and `zookeeper.connect`, and set `process.roles=broker`. Run in this state for **1–2 weeks**. Rollback is still possible.
    5. **Point of no return**: on the controllers, disable migration mode, remove `zookeeper.connect`, and do a rolling restart.
    6. Upgrade to the latest Kafka version.
  - Failure mode / constraint: migration only supports a **dedicated** controller cluster, not combined mode, so the machine count stays the same as with ZooKeeper. Follow the official docs for the exact steps.
- **Bootstrap → metadata request → direct connection**: how a client finds partition leaders.
  - How: (1) The client contacts any address in `--bootstrap-server`/`bootstrap.servers`. (2) It sends a **metadata request** for the topics it needs. The response lists all brokers and the leader of each partition. (3) It connects directly to each partition leader. (4) It refreshes metadata only when something fails, for example when a leader is unavailable. The controller has meanwhile detected the failure and elected a new leader from the replicas. The client sees a brief delay, then resumes.
  - Why it works: any broker can answer a metadata request, because every broker caches the metadata. Since Kafka 0.10.0 clients ask brokers, not ZooKeeper.

## Key Concepts
- **Consensus**: getting all nodes of a distributed system to agree on one state, here the controller, partition leaders, ISR, configs and ACLs.
- **Raft**: the consensus algorithm KRaft is built on, from Ongaro & Ousterhout's 2014 paper "In Search of an Understandable Consensus Algorithm".
- **Active controller / standby controllers**: in KRaft, the elected quorum member that manages the cluster, and the hot spares that take over immediately.
- **`__cluster_metadata`**: an internal topic holding all cluster metadata that previously lived in ZooKeeper. It is replicated to every node regardless of role.
- **ZNode**: a node in ZooKeeper's hierarchical key-value store. Kafka elects its controller by having brokers race to write their ID to the controller ZNode, and the first write wins.
- **ZAB (ZooKeeper Atomic Broadcast)**: ZooKeeper's Paxos-variant consensus protocol, which commits a value once a majority agrees.
- **ZooKeeper-mode controller**: an ordinary broker that also does management. In KRaft, by contrast, the active controller is always a member of the controller quorum.
- **Metadata request**: a client call to any broker that returns cluster brokers and partition leaders for the requested topics.
- **Bootstrap servers**: the initial contact list a client uses only to fetch metadata.

## Mental Models
- Think of **KRaft as "Kafka eating its own dog food"**: cluster state is just another replicated log, so the system that is good at logs manages itself.
- Think of **controller quorum size like ZooKeeper ensemble size**: a majority must survive, so you tolerate ⌊(n−1)/2⌋ failures. Use odd numbers only.
- Use **a load balancer, DNS name or virtual IP for bootstrap** when listing every broker gets cumbersome. Each broker must still be individually reachable by its own IP or DNS name, because clients talk to leaders directly.
- Think of **ZooKeeper's weakness as stale caches**: brokers cached metadata to avoid slow ZooKeeper reads. The controller polled ZooKeeper periodically, and some operations went to ZooKeeper directly, bypassing the controller. The result was decisions made on outdated state, such as assigning leadership to a dead broker.

## Anti-patterns
- **Running an even number of controllers (e.g. 4)**: costs more and still tolerates only one failure.
- **Pointing clients at a single bootstrap broker in production**: clients fail to start if that broker is down. List all brokers, or use DNS or a load balancer.
- **Putting a load balancer in front of brokers without per-broker addresses**: bootstrap works, but clients can't reach partition leaders directly.
- **Staying on ZooKeeper**: you operate two distributed systems, partition scalability is limited, controller failover is slow, and ZooKeeper must be secured separately because it holds ACLs. There is no path to Kafka 4.0.
- **Rushing the final migration step**: disabling migration mode on the controllers is irreversible. Soak for 1–2 weeks first.

## Code Examples
```bash
# Bootstrap via a single broker (OK for dev only)
$ kafka-topics.sh \
    --list \
    --bootstrap-server localhost:9092

# Production: list all brokers so startup survives one being down
$ kafka-topics.sh \
    --list \
    --bootstrap-server \
    localhost:9092,localhost:9093,localhost:9094
```
```properties
# New KRaft controllers during migration (same cluster ID as the ZK cluster)
zookeeper.metadata.migration.enable=true
zookeeper.connect=<Zookeeper address>

# Normal brokers after switching to KRaft (migration flag + zookeeper.connect removed)
process.roles=broker
```
- **What it demonstrates**: resilient bootstrapping, and the configuration flips that drive each phase of the ZooKeeper-to-KRaft migration.

## Reference Tables
**KRaft vs. ZooKeeper cluster management**

| Aspect | ZooKeeper mode | KRaft mode |
|---|---|---|
| Systems to operate | Kafka + ZooKeeper ensemble | Kafka only |
| Consensus protocol | ZAB (Paxos variant) | Raft |
| Metadata store | ZNodes in ZooKeeper | `__cluster_metadata` topic |
| Controller | One regular broker, elected via ZNode race | Active controller elected from the controller quorum. Standbys are hot. |
| Controller failover | Can take minutes on large clusters | Immediate takeover by a standby |
| Partition limits | ≤ 4,000 per broker, ≤ 200,000 per cluster | Significantly higher |
| Consistency | Cached and polled metadata can go stale | Every node replicates the same metadata log |
| Status | Deprecated in 3.5.0, removed in 4.0 | Production-ready since 3.3.0 |

**Controller quorum sizing**

| Controllers | Tolerated failures | Use |
|---|---|---|
| 1 | 0 | Local dev (can be combined with a broker in one JVM) |
| 3 | 1 | Production minimum |
| 4 | 1 | No benefit over 3 |
| 5 | 2 | Higher reliability |

**Recommended minimal production cluster**: 3 or 5 dedicated controllers plus at least 3 brokers.

## Worked Example
**A consumer survives a leader failure.** A consumer wants `products.prices.changelog`. It sends a metadata request to any bootstrap address. Because every broker caches the metadata, it doesn't matter which one answers. The response lists all brokers and the leader of each partition, and the consumer opens direct fetch connections to those leaders. It doesn't poll for metadata changes. Later, the broker leading partition 1 crashes. The active controller detects the failure and elects a new leader from the in-sync replicas, and the cluster metadata is updated. The consumer's next fetch to the dead leader fails, so it sends a fresh metadata request to any bootstrap broker, learns the new leader, reconnects and resumes. The only visible effect is a short delay during the election.

## Key Takeaways
1. Build new clusters on KRaft with 3 or 5 dedicated controllers and at least 3 brokers. Use combined mode only outside production.
2. Always use an odd controller count: 3 tolerates 1 failure, 5 tolerates 2.
3. Migrate ZooKeeper clusters without downtime: upgrade → dual-write migration → brokers to KRaft → soak 1–2 weeks → finalize controllers (irreversible) → upgrade.
4. Give clients several bootstrap addresses, or a DNS name or load balancer, but keep every broker individually addressable.
5. Clients refresh metadata lazily, on errors. Leader failover shows up only as a brief fetch delay.

## Connects To
- **ch04**: partition leaders and followers, which the controller assigns.
- **ch05**: ISR, preferred leader and unclean leader election, which the controller executes on failure.
- **ch06**: partition-count limits per broker and cluster depend on the coordination mode.
- **ch09**: the group coordinator and consumer-group rebalancing, the other coordination layer.
- **ch13**: ACLs live in cluster metadata, so ZooKeeper had to be secured separately.
- **ch16**: controller quorum sizing for disaster scenarios.
- **ch19**: the test environment and its `localhost:9092-9094` brokers.
- **Raft / Paxos (ZAB)**: the external consensus algorithms behind KRaft and ZooKeeper.
