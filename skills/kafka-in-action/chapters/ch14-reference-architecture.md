# Chapter 14: Kafka Reference Architecture

## Core Idea
A production Kafka setup is more than brokers plus a coordination cluster. It also needs clients, Connect, stream processing, schema management, read-only GUIs, GitOps resource management and Cruise Control, all on infrastructure that is robust and run by a team that knows Kafka. Size the hardware RAM-first: the heap stays small and the page cache is sized to how far consumers may lag.

## Frameworks Introduced
- **Reference architecture (figure 14.1)**: brokers + coordination cluster (KRaft/ZooKeeper) are the core. Around them sit producers/consumers, Kafka Connect, stream processing (Kafka Streams/Flink), a schema registry or explicit schema management, a GUI, resource automation, Cruise Control and monitoring.
  - When to use: as a checklist when planning a new Kafka platform.
  - How: (1) Java clients are the reference. Non-Java producers must use the same partitioning algorithm as Java. (2) Use Connect before writing custom integration code. (3) Process data in Kafka with Streams/Flink. (4) Manage schemas explicitly. Whether you use a registry is a secondary decision. (5) Add the operational tools below.
- **GitOps resource management**: a Git repo is the source of truth for topics, users and ACLs. Changes go in through pull/merge requests, get a manual or automated review, and a CD pipeline creates, modifies or deletes them in Kafka. This is a specific form of Infrastructure as Code.
  - When to use: from the preproduction phase onward. Never create topics manually in production, and never through a GUI.
  - How: declare resources in the repo → PR → review/approval (which differs by company) → pipeline reconciles the cluster. Use `kcctl` (inspired by `kubectl`) for Connect connectors: keep the connector JSON in Git and run `kcctl apply -f file.json`.
  - Why it works / failure mode: changes are auditable, reviewable and reproducible across dev/test/prod. There is no off-the-shelf universal tool, so most organisations build their own. Strimzi's Topic/User operators come closest.
- **Cruise Control for Apache Kafka (LinkedIn)**: automated partition/leader rebalancing based on actual resource load, not just partition counts.
  - When to use: monitoring shows uneven load across brokers, a broker is being added (Kafka does nothing automatically for new brokers), or a broker is being decommissioned (its partitions must be drained first).
  - How: a **metrics reporter** JAR on every broker writes load samples to a Kafka topic. The **analyzer** evaluates them against configured **goals** and produces a **proposal**. You review it, then the **executor** applies it via the REST API or the Cruise Control UI. Start manually: monitoring detects imbalance → run the analyzer → review → execute. Later you can enable **automatic anomaly/self-healing detection**, which analyzes and executes on its own when goals are violated.
  - Goals: for each of CPU, RAM, disk and network you set a **capacity goal** (keep usage under a fixed ceiling, e.g. disk) and a **resource distribution goal** (spread usage as evenly as possible).
  - Why it works / failure mode: it replaces the giant spreadsheets once used for manual reassignment. Partition moves cause very high load, so never run them while the cluster is near its limits.
- **Deployment-model decision**: own hardware / VMs / Kubernetes with Strimzi / self-managed in the public cloud / managed KaaS.
  - How: the infrastructure itself matters less than whether it is robust and whether a Kafka-competent team runs it. If either is missing, buy a managed service. A managed service still needs an internal Kafka team for automation, processes and expertise for other teams.

## Key Concepts
- **kcat (formerly kafkacat)**: a CLI producer/consumer based on librdkafka (C). It starts almost instantly, supports headers and has short flags (`-b`, `-t`, `-P`, `-C`).
- **Kafbat Kafka UI**: formerly Provectus Kafka UI. The authors consider it the strongest open-source GUI (topics, Connect, Schema Registry, ACLs, consumer groups). Commercial alternatives: Kpow, Kadeck, Conduktor Console.
- **kcctl**: a kubectl-style CLI for declaratively managing Kafka Connect connectors from JSON files.
- **Strimzi**: a Kubernetes operator that, in the authors' words, "essentially represents our reference architecture". Red Hat's supported distribution is AMQ Streams.
- **Cluster Operator**: Strimzi's core operator. It deploys brokers, coordination nodes, Connect and the other operators.
- **Entity Operator**: the Topic Operator plus the User Operator, which can also be used without the rest of Strimzi. They manage topics, users/ACLs, auth secrets and TLS key pairs declaratively.
- **Tiered storage**: available since Kafka 3.9. It offloads older segments to cheap storage (e.g. cloud object storage), which makes indefinite retention affordable.
- **Rack awareness**: spreading replicas across racks, fire compartments or availability zones so that one physical failure cannot take out several replicas.
- **Page cache sizing**: the OS cache that serves lagging consumers without disk reads. Size it as data produced per broker per hour × the maximum tolerated consumer lag in hours.

## Mental Models
- Think of the **GUI as a read-only window**: use it for data exploration in production and for writing test data in dev. It is never a write path and never a substitute for monitoring.
- Think of **Strimzi as the reference design**: even if you cannot run it, copy its patterns (operator-managed cluster, declarative topics/users, Cruise Control, anti-affinity).
- Use **RAM as the sizing driver**: fix the RAM first (aim for 32–64 GB per broker), then derive the CPU. Prefer more, smaller cores, because Kafka parallelises well.
- Think **regional clusters plus replication, not one global cluster**: inter-broker latency must stay below 30 ms.

## Anti-patterns
- **Producing to production with console scripts or kcat**: writing data is the job of real producers.
- **Changing configs or producing data through a GUI in production**: give GUI users read-only permissions.
- **Creating topics manually in production**: this causes drift and gives you no review or audit trail. Use GitOps.
- **Testing or developing on the production cluster**: always run separate dev/test clusters.
- **RAID 5/6 on brokers**: too slow. RAID is unnecessary anyway, because replication provides redundancy (RAID 0 is the only exception, and only for speed).
- **SAN/NFS/GlusterFS storage**: NFS and GlusterFS are strongly advised against on Kubernetes. Use a SAN only if it is proven fast and reliable, otherwise use local SSDs. Several brokers compacting at once can overwhelm shared storage. Cloud block storage from the big three is fine.
- **Two brokers on the same VM host, K8s node or rack**: a single host or power failure loses several replicas, and because Kafka does not fsync immediately, data can be lost. Use anti-affinity rules in Strimzi.
- **Stretching one cluster across cloud regions**: latency above 30 ms degrades replication, metadata sync and end-to-end latency.
- **Running Cruise Control rebalances at peak load**: partition movement adds heavy network and disk load.
- **Signing up for a managed service without a cost model**: costs climb steeply with volume, and retention or throughput limits may not fit.

## Code Examples
```bash
# Produce with kcat (end with Ctrl-D)
$ kcat -b localhost:9092 -t products.prices.changelog -P
> energy drink 2
> cola 5

# Consume with kcat (end with Ctrl-C); -C can be omitted, kcat guesses the mode
$ kcat -b localhost:9092 -t products.prices.changelog -C
energy drink 2
cola 5
% Reached end of topic products.prices.changelog [0] at offset 6
```
- **What it demonstrates**: kcat's short flags (`-b` bootstrap, `-t` topic, `-P` produce, `-C` consume) and its end-of-partition notice. It is fine for scripts and exploration, not for production writes.

```bash
kcctl apply -f file.json   # declaratively create/update a Connect connector from Git-managed JSON
```
- **What it demonstrates**: GitOps for connectors without calling the REST API by hand.

## Reference Tables

**Deployment environments**

| Environment | Fits when | Watch out for |
|---|---|---|
| Own hardware | Skilled ops team, predictable load, little virtualisation (e.g. web analytics) | Spare parts, capacity planning, rack/fire-compartment separation, multi-DC latency < 30 ms |
| Virtualized (own DC) | An established VM platform already in place | Spread brokers across VM hosts. Avoid SAN unless proven; prefer local SSDs. Shared storage can be overwhelmed by simultaneous compaction |
| Kubernetes + Strimzi | Existing K8s, strong ops team, reliable infrastructure | Use recent K8s versions and performant storage (no NFS/GlusterFS). Anti-affinity so no two brokers share a node |
| Self-managed in public cloud | You need control the managed offerings lack | Instance/storage choice drives throughput and latency. Cloud block storage is OK. Strimzi if already on K8s |
| Managed (MSK, Azure HDInsight, Confluent Cloud, Aiven) | No reliable infrastructure or no ops capacity | Limits on retention and throughput, and cost at volume. Confluent sells capacity rather than cluster sizes. Aiven can run in your own cloud account (useful when regulated). Both offer VNet peering/Private Link |

**Hardware guidelines**

| Resource | Recommendation |
|---|---|
| Broker count | Start with at least 3, then add gradually |
| Disk | Fast, reliable SSDs. Several small disks beat a few large ones (large clusters: 12 × 1 TB SSD). No RAID 5/6. Start small and grow. Use tiered storage (3.9+) for old data |
| JVM heap | At least 1 GB. Rarely more than 6 GB even for very large clusters |
| RAM total | Heap + page cache (lag-based). Aim for 32–64 GB per broker. Below that makes little sense; above it, add brokers instead |
| Network | At least 1 Gbit/s Ethernet, no upper limit. Use a dedicated storage network if storage is networked |
| CPU | Secondary and derived from RAM. More, smaller cores. Memory-optimised instances |
| Placement | Different hosts, racks and AZs (rack awareness). Inter-broker latency < 30 ms. One cluster per region, connected with MirrorMaker only when needed |
| Coordination (KRaft/ZK) | Small: 4–8 GB RAM, but a low-latency network (ZK is very latency-sensitive). Odd node count: 3 nodes tolerate 1 failure, 5 tolerate 2 |

## Worked Example
**Page-cache sizing for a 3-broker cluster.** The cluster ingests 30 GB/hour, and consumers may lag up to 2 hours without having to read from disk.
1. Per broker, assuming even distribution: 30 GB / 3 = 10 GB/hour.
2. Page cache needed: 10 GB/h × 2 h = 20 GB.
3. Add the heap: 6 GB (the practical ceiling) + 20 GB = about 26 GB.
4. Choose 32 GB RAM per broker. This leaves headroom and sits at the bottom of the 32–64 GB per-broker band the authors recommend. If the lag tolerance or the volume grows past what 64 GB covers, add brokers rather than RAM.

## Key Takeaways
1. Treat topics, users, ACLs and connectors as code. Git is the source of truth, changes arrive as PRs and a pipeline applies them. Never make manual or GUI changes in production.
2. Give GUIs read-only production access. They are for exploration, not monitoring or writing.
3. Use Cruise Control for load balancing, broker addition and broker decommissioning. Start in review-then-execute mode, and avoid rebalancing at peak load.
4. Pick the deployment model based on infrastructure robustness and team competence. On Kubernetes, use Strimzi with anti-affinity. Without ops capacity, buy managed, but keep an internal Kafka team.
5. Size brokers RAM-first: heap of 1–6 GB plus page cache equal to per-broker ingest × lag tolerance, landing at 32–64 GB per broker.
6. Physically separate brokers (hosts, racks, AZs), keep inter-broker latency under 30 ms, and run separate regional clusters linked by MirrorMaker instead of one global cluster.
7. Run coordination on 3 or 5 small nodes with a low-latency network.

## Connects To
- **ch06**: the page cache and batching explain why RAM, not CPU, is the sizing driver.
- **ch07**: KRaft/ZooKeeper quorum sizing (odd counts, 3 or 5) and the coordination cluster's role.
- **ch04 / ch05**: replication and rack awareness are the reasons RAID is unnecessary and physical separation is mandatory.
- **ch10**: tiered storage and retention. Compaction load can overwhelm shared storage.
- **ch11**: Kafka Connect and kcctl. **ch12**: Streams/Flink in the architecture. **ch13**: schema management, ACLs, quotas.
- **ch15**: monitoring detects the imbalance that Cruise Control fixes. A GUI is not a substitute for monitoring.
- **ch16**: MirrorMaker and multi-region clusters for disaster scenarios.
- **GitOps / Infrastructure as Code**: the general practice applied here to Kafka resources.
- **Kubernetes operator pattern**: the basis of Strimzi's Cluster, Topic and User operators.
