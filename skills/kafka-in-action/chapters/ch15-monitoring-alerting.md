# Chapter 15: Kafka Monitoring and Alerting

## Core Idea
Monitor four layers: infrastructure, broker (server, log, network, controller metrics), client (producer, consumer, Connect, Streams) and environment. Alert only on a small set of smoothed, contextualized signals: under-replicated and under-min-ISR partitions, network processor idle below 0.3, consumer `records-lag`/`records-lead`, failed tasks and threads, and disk/network above 60%. Keep everything else on dashboards for root-cause analysis, and avoid alert fatigue.

## Frameworks Introduced
- **Layered monitoring model**: infrastructure → broker → client → deployment environment.
  - When to use: when designing dashboards and alerts for any Kafka platform.
  - How: (1) Infrastructure first. Many "Kafka problems" are really CPU, RAM, disk or network shortages, and checking these first saves hours of searching inside Kafka. (2) Broker metrics by MBean domain (`kafka.server`, `kafka.log`, `kafka.network`, `kafka.controller`). (3) Client metrics by domain (`kafka.producer`, `kafka.consumer`, `kafka.connect`, `kafka.streams`), attributed to clients via the `client-id` label. (4) Environment-specific signals (hypervisor, cloud, Kubernetes, managed-service limits, security).
  - Why it works / failure mode: a single metric snapshot says little. During partition rebalancing, resource use rises temporarily and that is normal. Sustained high usage means organic growth, so scale the cluster.
- **60% headroom rule**: alert when disk or network utilization exceeds 60%.
  - When to use: on every broker host.
  - How: a disk alert above 60% leaves time to order new disks and leaves room for the extra space needed during reassignment. If storage can be expanded within minutes, the threshold can be higher. A network alert above 60% matters because partition moves, adding brokers and broker failures all temporarily spike network traffic.
- **Metrics → alerts pipeline**:
  - How: (1) Visualize each candidate metric. (2) Two-state metrics (good/bad) become alerts directly. (3) Smooth noisy metrics over a longer window: CPU at 100% for seconds is fine, sustained for several minutes is not. (4) Start with conservative thresholds and tune them when false alarms occur. (5) Give self-healing systems (e.g. a Kubernetes restart) time to recover before paging, but review the incident afterwards. (6) Keep non-alertable metrics as context panels. For example, produced records explains whether high consumer lag comes from a slow consumer or from a traffic surge. (7) Distrust auto-generated baseline alerts until they are tuned, and review all thresholds regularly.
  - Why it works / failure mode: oversensitive alerting produces false positives, people start ignoring alerts, and real incidents get missed. This is **alert fatigue**.
- **Alerts → problem solving**: enrich every alert with what the metric means, why it matters, links to dashboards and a **playbook** (step-by-step troubleshooting). Playbooks are living documents: update them after each incident. Where possible, add automatic handlers (restart, scale). The goal is that a non-expert woken at night can act calmly.

## Key Concepts
- **Under-replicated partitions** (`UnderReplicatedPartitions`): partitions with out-of-sync replicas. It must be 0. Persistently above 0 means a broker is offline; a fluctuating value means resource problems.
- **At/Under min ISR partition count**: `AtMinIsrPartitionCount` is a warning, expected for every partition when RF=1. `UnderMinIsrPartitionCount` is critical: producers using `acks=all` cannot write and consumption is delayed.
- **Offline replica count / reassigning partitions**: both should be 0. If they stay above 0 for long, the cluster has serious trouble.
- **Follower lag** (`ReplicaFetcherManager` MaxLag, `FetcherLagMetrics` ConsumerLag): replica lag behind the leader. Keep it near the producer batch size, and watch that it does not grow steadily.
- **NetworkProcessorAvgIdlePercent**: the share of idle network threads. A value consistently below 0.3 means the broker is overloaded or close to it, so scale immediately.
- **Delayed operation purgatory size**: requests parked while waiting. These are either produce requests waiting for follower acks, or fetch requests waiting on `fetch.max.wait.ms` / `fetch.min.bytes`.
- **ActiveController**: exactly one broker reports 1 and all others report 0. Related signals: active and fenced broker counts, offline partitions, and preferred-replica imbalance. Kafka rebalances leaders automatically when imbalance exceeds `leader.imbalance.per.broker.percentage` (default 10%).
- **records-lag vs records-lead**: lag is how far the consumer is behind the newest record. Lead is how far it is ahead of the oldest retained record. Low lead combined with high lag means retention or compaction may delete records before the consumer reads them.
- **time-between-poll / last-poll-seconds-ago**: if poll gaps approach `max.poll.interval.ms`, the consumer is declared dead and the group rebalances.
- **Alert fatigue**: the condition in which repeated false positives lead people to ignore real alerts.

## Mental Models
- Think of **most broker metrics as indicators, not verdicts**: before declaring a broker overloaded, cross-check CPU and network.
- Think of **records-lead as a data-loss early warning**: lag alone means "slow", but low lead plus high lag means "about to lose data". Set thresholds per topic.
- Use **connection-count churn as a rebalance detector**: a consumer's connection count should be stable. Frequent changes mean frequent rebalances, and nothing is consumed during a rebalance.
- Use **non-alerting dashboards as the root-cause toolkit**: an alert says something is wrong, and the context panels say why.

## Anti-patterns
- **Alerting on every metric**: this is labor-intensive and noisy, and it causes alert fatigue.
- **Alerting on raw, unsmoothed spikes**: brief CPU spikes to 100% should not page anyone at night.
- **Paging before self-healing has had a chance**, and conversely **ignoring incidents that self-healed**: allow recovery time, but always review afterwards.
- **Hunting inside Kafka without infrastructure monitoring**: this wastes hours on what is really a host resource problem.
- **Using a GUI as monitoring**: GUIs cover only part of what monitoring needs (see ch14).
- **Ignoring producer-side rejections**: brokers count records rejected for a missing key on a compacted topic, a bad CRC or out-of-sequence offsets. Producers see the errors, but weak application monitoring hides them, so tell the developers.
- **Very long Connect retry intervals without status monitoring**: retries absorb temporary third-party outages, but they also delay the transition to FAILED, which hides real failures.

## Code Examples
```text
# Broker: full MBean form vs Prometheus-style name
kafka.server:type=ReplicaManager,name=PartitionCount   ->  kafka_server_replicamanager_partitioncount

# Critical broker alerts
kafka.server:type=ReplicaManager,name=UnderReplicatedPartitions        == 0
kafka.server:type=ReplicaManager,name=UnderMinIsrPartitionCount        == 0
kafka.network:type=SocketServer,name=NetworkProcessorAvgIdlePercent    > 0.3

# Critical client alerts
kafka.consumer:type=consumer-fetch-manager-metrics,partition="{partition}",topic="{topic}",client-id="{client-id}",name=records-lag
kafka.connect:type=connect-worker-metrics,connector="{connector}",name=connector-failed-task-count   == 0
kafka.streams:type=stream-metrics,client-id=([-.\w]+),name=failed-stream-threads                    == 0
```
- **What it demonstrates**: the MBean naming convention (domain → type → name, plus labels such as `client-id`, `topic` and `partition`; Prometheus drops the type for client metrics) and the handful of metrics worth alerting on.

## Reference Tables

**Infrastructure thresholds**

| Resource | Threshold / guidance |
|---|---|
| Disk usage | Alert above 60% (leaves time to buy disks and room for rebalancing). Can be higher if expansion takes minutes |
| Network utilization | Keep below 60% (partition moves, new brokers and broker failures spike traffic) |
| Memory | Keep headroom. Kafka runs with less RAM, but a smaller page cache means slower performance |
| CPU | Short spikes reduce performance; sustained saturation stops request processing |

**Most important broker metrics (table 15.1)**

| MBean | Meaning | Alert rule |
|---|---|---|
| `kafka.server:type=ReplicaManager,name=UnderReplicatedPartitions` | Partitions with out-of-sync replicas | Must be 0. Persistently above 0 means a broker is offline |
| `kafka.server:type=ReplicaManager,name=AtMinIsrPartitionCount` | ISR exactly at `min.insync.replicas` | Warning (expected when RF=1) |
| `kafka.server:type=ReplicaManager,name=UnderMinIsrPartitionCount` | ISR below min | Critical: `acks=all` producers are blocked and consumption is delayed |
| `kafka.server:type=FetcherLagMetrics,name=ConsumerLag,clientId=…,topic=…,partition=…` | Follower lag per topic/partition | A brief lag is OK. Growing or constant lag threatens the ISR |
| `kafka.network:type=SocketServer,name=NetworkProcessorAvgIdlePercent` | Idle network processors | Should be above 0.3. Below that means overload risk |

Other broker signals: PartitionCount and LeaderCount (should be balanced across brokers, otherwise reassign), ProducerIdCount, OfflineReplicaCount, ReassigningPartitions, BrokerTopicMetrics (MessagesIn, BytesIn/Out, ReplicationBytesIn/Out, ReassignmentBytesIn/Out), log flush time and rate (high values mean a storage problem), `OfflineLogDirectoryCount` (must be 0; a nonzero value means a disk failure), Log Size/NumLogSegments/LogStartOffset/LogEndOffset (for trends), LogCleaner, RequestMetrics, ActiveControllerCount, ActiveBrokerCount, FencedBrokerCount, PreferredReplicaImbalanceCount.

**Client metrics (tables 15.2–15.5)**

| Metric (name=) | Client | Meaning / rule |
|---|---|---|
| `connection-count` | all | Should be stable. Frequent changes signal consumer rebalances |
| `failed-authentication-total` | all | Wrong credentials or a broken auth system. Investigate promptly |
| `request-rate`, `outgoing-byte-rate` (and incoming) | all | App-specific. Use for anomaly detection. A `node-` prefix gives per-broker values |
| `record-error-rate` | producer | Should be about 0. Causes: batch size above the broker's max message size, no key on a compacted topic, network trouble, broker offline |
| `produce-throttle-time-avg` / max | producer | Throttling from quotas or overload |
| `request-latency-avg`, `record-send-rate` | producer | Key performance signals. A sudden latency rise means cluster trouble |
| requests in flight | producer | Pending unacknowledged requests, which grow with `acks=all` |
| `time-between-poll` (avg/max), `last-poll-seconds-ago` | consumer | A rising value means a scalability problem. Reaching `max.poll.interval.ms` triggers a rebalance |
| `rebalance-rate`, rebalance-total, failed-rebalance-total, rebalance-latency-max/total | consumer | Some is normal (especially on K8s). Persistently high values or failures signal group problems |
| `commit-latency-max`, commit-total | consumer | Anomaly detection |
| assigned-partitions | consumer | Should be even. A consumer holding 0 partitions for a long time may hide an error |
| `records-lag` | consumer | The most important consumer metric. Should be about 0. Permanently high means a bottleneck |
| `records-lead` | consumer | Use only together with lag. Low lead plus high lag means a risk of data loss to retention or compaction |
| `connector-failed-task-count` | Connect | Above 0 means no processing. Either a temporary dependency issue (restart the task) or a processing error |
| task-error metrics (errors, DLQ writes) | Connect | Error counts and dead-letter-queue writes |
| `failed-stream-threads` | Streams | Above 0 means processing has stopped |
| `process-rate` | Streams | Anomaly detection |
| `dropped-records-rate` / dropped-records-total | Streams | Critical: records were not processed correctly |

**Environment-specific monitoring focus**

| Environment | Also watch |
|---|---|
| Own hardware | Disk health, CPU, memory, network bandwidth. Redundancy, backups and a DR plan are all your responsibility |
| VMs | CPU steal time, disk I/O latency, memory swapping (hypervisor contention) |
| Public cloud | Network latency, throughput, autoscaling, instance health, storage performance, inter-region traffic |
| Kubernetes | JMX → Prometheus scraping → Grafana. Pod health, node resources, cluster contention |
| Managed service | Partition distribution, throughput, consumer lag, latency, provider limits and quotas (instance size, bandwidth), SLAs |
| All | Failed authentications, unauthorized access, encryption overhead |

## Worked Example
**Diagnosing a consumer-lag alert.** The `records-lag` alert fires for a consumer group.
1. Check the context panel for produced records and topic `MessagesIn`. If production spiked, the consumers are simply working through a surge, and the lag should drain. That is not a defect.
2. If production is normal, check `time-between-poll` and `last-poll-seconds-ago`. A rising trend means processing per batch is slowing down, for example because a downstream database grows slower. If it nears `max.poll.interval.ms`, the consumer is evicted and the group rebalances, which pauses consumption and worsens the lag.
3. Check `rebalance-rate`, `connection-count` churn and `assigned-partitions` to confirm a rebalance storm or an idle consumer.
4. Check `records-lead`. If it is low while lag is high, retention or compaction may delete records before they are read, so escalate.
5. Remedies: short term, raise `max.poll.interval.ms` or add hardware. Use `CooperativeStickyAssignor` so that the rest of the group keeps consuming during rebalances. Long term, re-architect for scalability. Afterwards, update the playbook.

## Key Takeaways
1. Monitor infrastructure first, and alert when disk or network exceeds 60% so that rebalancing and failures have headroom.
2. Hard broker alerts: `UnderReplicatedPartitions` > 0, `UnderMinIsrPartitionCount` > 0, `OfflineLogDirectoryCount` > 0, offline replicas, ActiveController ≠ exactly one, `NetworkProcessorAvgIdlePercent` < 0.3.
3. On the client side, alert on `records-lag` (paired with `records-lead`), `record-error-rate`, `failed-authentication-total`, `connector-failed-task-count`, `failed-stream-threads` and `dropped-records-rate`.
4. Watch `time-between-poll` and rebalance metrics to catch consumer-group trouble before `max.poll.interval.ms` evicts members.
5. Smooth noisy metrics, start with conservative thresholds, tune them on false alarms, and let self-healing work before you page anyone.
6. Every alert needs context: what it means, links to dashboards and a playbook that is updated after each incident.
7. A managed service does not remove monitoring duties. Lag, throughput, partition distribution and provider quotas remain yours.

## Connects To
- **ch05**: ISR, `min.insync.replicas` and `acks=all`, which explain why under-min-ISR blocks producers.
- **ch06**: page cache and network threads. These explain the network processor idle metric and the memory headroom.
- **ch09**: consumer groups, rebalancing, `max.poll.interval.ms`, `CooperativeStickyAssignor`, lag.
- **ch10**: retention and compaction, which drive the `records-lead` data-loss risk. Covers the log cleaner metrics.
- **ch11 / ch12**: Connect task status, DLQ and retries. Streams threads, tasks and state stores.
- **ch13**: quotas, which show up as throttle-time metrics, and authentication failures.
- **ch14**: deployment environments, Cruise Control (acts on the imbalance monitoring detects), and why a GUI is not monitoring.
- **ch20 (Appendix B)**: a hands-on Prometheus and Grafana setup for these metrics.
- **SRE alerting practice (Google SRE)**: symptom-based alerts, playbooks and alert fatigue.
