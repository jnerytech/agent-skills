# Chapter 9: Consuming Messages

## Core Idea
Kafka consumers *pull* (fetch) data and own their reading position; consumer groups turn that position into a durable, shared offset stored in `__consumer_offsets` and use the broker-assisted Kafka Rebalance Protocol to split partitions among members. Because every rebalance pauses work, the practical skill is picking the right assignor and cutting unnecessary rebalances (Cooperative Sticky Assignor, static membership).

## Frameworks Introduced
- **Fetch model + request purgatory (consumer side)**: the consumer sends a fetch request (partition + start offset) to the partition leader; the broker's network threads queue it, I/O threads *read* batches (ideally straight from the page cache), and the request waits in purgatory for *more data*, not for other brokers.
  - When to use: reasoning about consumer latency vs. throughput.
  - How: broker answers as soon as `fetch.min.bytes` (default `1`) bytes are available, or after `fetch.max.wait.ms` (default `500` ms) if not. Raise `fetch.min.bytes` for throughput (bigger batches); keep defaults for low latency. Both are consumer-side settings, so each consumer chooses its own trade-off.
- **Fetch from the closest replica (KIP-392)**: brokers declare `broker.rack`; consumers declare `client.rack`; the consumer may then fetch from a follower in its own rack/AZ. Producers still always write to the leader.
  - When to use: multi-AZ clusters where cross-zone traffic costs money or adds latency.
- **Offset storage options**: (1) don't store (rebuildable in-memory cache), (2) local disk of the service (local DB/cache), (3) external system written in the *same transaction* as the data (exactly-once for the consumer; the approach many Kafka Connect sinks use), (4) Kafka itself via consumer groups → compacted topic `__consumer_offsets`.
  - When to use: default to (4); use (3) when you need exactly-once into a database; (2) breaks statelessness and horizontal scaling.
- **Kafka Rebalance Protocol**: generic broker-assisted protocol for distributing resources (partitions, Kafka Streams tasks, Connect tasks) among group members; Kafka doesn't care what is distributed.
  - How: (0) `FindCoordinator` to any broker → group coordinator (chosen by hashing group ID across brokers); (1) each member sends `JoinGroup`, a synchronization point: existing members are pulled out and must rejoin, and nobody consumes meanwhile; (2) first member to join becomes **group leader**; (3) leader computes the assignment with `partition.assignment.strategy` and sends it via `SyncGroup`; (4) coordinator distributes assignments; (5) members send `Heartbeat`s every `heartbeat.interval.ms`; missing ~3 intervals (`session.timeout.ms`) gets a member evicted.
  - Why it works / failure mode: reuses the brokers' fault tolerance instead of running a separate coordination cluster per group. The cost is that classic rebalances *stop the world*. Triggers: member joins, member leaves (intentionally or by crash/timeout), partition count of a consumed topic changes. A rolling restart of 3 consumers causes 6 rebalances.
- **Partition assignors** (`partition.assignment.strategy`, all members MUST use the same one):
  - **Range Assignor** (default): partition *n* of every subscribed topic goes to the same consumer, which enables co-partitioned stream joins but can leave consumers idle.
  - **Round Robin Assignor**: spreads all partitions of all topics evenly; reshuffles everything on rebalance.
  - **Sticky Assignor**: even like Round Robin but minimizes movement; still stop-the-world.
  - **Cooperative Sticky Assignor** (Kafka 3.0): incremental. Rebalance #1 revokes only partitions that must move, everyone else keeps consuming; rebalance #2 assigns the now-dangling partitions.
  - Why it works / failure mode: only moved partitions pause. Authors' recommendation: use Cooperative Sticky until the next-gen protocol (KIP-848, Kafka 4.0) is available, then switch to KIP-848.
- **Static membership** (Kafka 2.3): give each consumer a stable `group.instance.id` and raise `session.timeout.ms` to minutes, so an auto-restarted instance rejoins under the same identity without a rebalance.
  - How: derive the ID from something stable across restarts (Kubernetes StatefulSet pod name, constant cloud hostname). Rebalances then happen only on new members, a member silent for minutes, or partition-count changes.

## Key Concepts
- **Fetch request**: consumer request to a partition leader (or nearest replica) naming partition and start offset.
- **`auto.offset.reset`**: where to start when the group has no committed offset: `latest` (default) or `earliest`; the CLI equivalent of `earliest` is `--from-beginning`.
- **Offset**: per-partition, monotonically increasing message position, never renumbered; gaps can appear after cleanup and consumers just get the next available message.
- **`__consumer_offsets`**: internal compacted topic where Kafka stores committed offsets per consumer group.
- **Consumer group**: all consumers sharing a `group.id`; unit of offset ownership and of partition distribution. Different groups read the same topic independently.
- **Consumer lag**: Log End Offset minus the group's current (committed) offset, per partition; the single most important consumer metric (0 = fully caught up).
- **Group coordinator**: broker responsible for one group (membership, heartbeats, assignment hand-off).
- **Group leader**: the first consumer to join; computes the partition assignment client-side.
- **`client.id`**: consumer-configured name surfaced in logs, metrics, and `kafka-consumer-groups.sh` output.

## Mental Models
- Think of a consumer as a **bookmark holder**: the broker doesn't push or track deliveries; the consumer (via its group) owns the bookmark.
- Think of offsets as **just data**: Kafka stores them in a Kafka topic, which is why consumer groups are worth using even with a single consumer.
- Use **Range Assignor when** you co-partition topics by key and must see partition *n* of every topic together. Otherwise use Round Robin/Sticky, and in practice Cooperative Sticky.
- Think of every rebalance as a **pause button for the whole group** (classic protocol). Design deployments so restarts don't press it.

## Anti-patterns
- **Reusing or copy-pasting the wrong `group.id`**: two applications share and overwrite offsets, "stealing" messages from each other, which can mean data loss or inconsistent processing in production.
- **Mixing assignment strategies within one group**: unpredictable assignments during rebalances, processing inconsistencies.
- **Hand-rolling joins in a plain consumer on top of Range Assignor**: possible but fragile; use Kafka Streams for joins.
- **Storing offsets on the service's local disk for stateless/scaled services**: new instances don't know where to start, and you lose horizontal scalability.
- **Rolling restarts with dynamic membership and default timeouts**: two rebalances per instance, with repeated stop-the-world pauses.
- **Not clearing local state/committing before a rebalance**: after reassignment, the consumer may own entirely different partitions.

## Code Examples
```bash
# Read a specific partition from an explicit offset (no group)
kafka-console-consumer.sh \
  --topic products.prices.changelog \
  --offset 0 \
  --partition 0 \
  --bootstrap-server localhost:9092

# Consume as a named group (offsets get committed to __consumer_offsets)
kafka-console-consumer.sh \
  --topic products.prices-offsets \
  --bootstrap-server localhost:9092 \
  --group products.prices.monitoring \
  --from-beginning \
  --property print.key=true \
  --property key.separator=":"

# Inspect group offsets, LEO and lag per partition
kafka-consumer-groups.sh \
  --group products.prices.monitoring \
  --describe \
  --bootstrap-server localhost:9092
```
- **What it demonstrates**: manual partition/offset reads vs. group-managed offsets, and how to check lag.

```properties
# Consumer settings discussed in the chapter
group.id=products.prices.monitoring
auto.offset.reset=earliest            # default: latest
fetch.min.bytes=1                     # default
fetch.max.wait.ms=500                 # default
client.rack=eu-central-1a             # pair with broker.rack (KIP-392)
partition.assignment.strategy=org.apache.kafka.clients.consumer.CooperativeStickyAssignor
group.instance.id=consumer-0          # static membership; stable across restarts
session.timeout.ms=300000             # "several minutes" with static membership
```
- **What it demonstrates**: the consumer knobs for start position, fetch batching, rack-aware fetching, assignment strategy, and static membership. The values for `client.rack`, `group.instance.id`, and `session.timeout.ms` are illustrative.

## Reference Tables
| Setting | Default | Meaning |
|---|---|---|
| `auto.offset.reset` | `latest` | Start position when group has no committed offset (`earliest` / `latest`) |
| `fetch.min.bytes` | `1` | Broker responds once this much data is available |
| `fetch.max.wait.ms` | `500` | Max time broker holds a fetch in purgatory if `fetch.min.bytes` not met |
| `heartbeat.interval.ms` | (client default) | Heartbeat cadence to group coordinator |
| `session.timeout.ms` | (client default) | No heartbeat for this long (≈3 intervals), member is evicted and the group rebalances; raise to minutes for static membership |
| `partition.assignment.strategy` | Range Assignor | How the group leader assigns partitions |
| `group.instance.id` | unset | Enables static membership |
| `broker.rack` / `client.rack` | unset | Rack awareness; enables fetch-from-closest-replica |

| Assignor | Distribution | On rebalance | Use when |
|---|---|---|---|
| Range (default) | Same partition number of all topics → same consumer | Stop-the-world, recompute | Co-partitioned joins (better: Kafka Streams) |
| Round Robin | Even across all partitions | Stop-the-world, full reshuffle | Independent topics, no key correlation |
| Sticky | Even, minimal movement | Stop-the-world, few moves | Stateful consumers, legacy clients |
| Cooperative Sticky (3.0+) | Even, minimal movement | Incremental, two rounds; unmoved partitions keep flowing | Default recommendation pre-KIP-848 |

| `kafka-consumer-groups.sh --describe` column | Meaning |
|---|---|
| Current Offset | Next offset the group will read (committed position) |
| Log End Offset | Offset the next produced message will get |
| Lag | LEO − Current Offset |
| Consumer ID / Host / Client ID | Auto-generated member ID, consumer IP, configured `client.id` |

## Worked Example
Topic `products.prices-offsets` (2 partitions, RF 3). Produce keyed messages `coffee pads:10, cola:2, energy drink:4, coffee pads:11, coffee pads:12, energy drink:4`. Consume with `--group products.prices.monitoring --from-beginning`: output order differs from produce order because the `energy drink` keys hash to one partition and `cola`/`coffee pads` to the other, and the console consumer drains one partition before the other. Ctrl-C and restart: nothing is re-read, which proves the offsets were committed. `--describe` shows P0 current=2/LEO=2/lag 0 and P1 current=4/LEO=4/lag 0 (one consumer owns both). Stop the consumer, produce more: P0 LEO 4 (lag 2), P1 LEO 7 (lag 3). Restart, the group resumes from the committed offsets, and lag returns to 0.

## Key Takeaways
1. Always set a deliberate, unique `group.id` per application. Even single-instance consumers benefit from group-managed offsets.
2. Monitor consumer lag per partition. It is the primary health signal for consumers.
3. Set `auto.offset.reset=earliest` when a new group must process history; the default `latest` silently skips existing data.
4. Use the Cooperative Sticky Assignor today and migrate to the KIP-848 next-gen protocol (Kafka 4.0) when available.
5. On Kubernetes/cloud with auto-restart, enable static membership (`group.instance.id` + `session.timeout.ms` in minutes) to stop rolling restarts from triggering rebalance storms.
6. In multi-AZ deployments, set `broker.rack` and `client.rack` so consumers read from the local replica.
7. For exactly-once into a database, commit offsets in the same DB transaction as the data.

## Connects To
- **ch04**: coordination as a hard distributed-systems problem; the brokers serve as the coordination layer.
- **ch06**: tuning `fetch.min.bytes` / `fetch.max.wait.ms` for consumer performance.
- **ch08**: broker request path (network threads, I/O threads, purgatory), mirrored here for fetch; LEO/HWM limit what consumers can read.
- **ch10**: `__consumer_offsets` is a compacted topic; `offsets.retention.minutes` expires inactive groups' offsets.
- **ch11 / ch12**: Kafka Connect and Kafka Streams use the same rebalance protocol; Streams does co-partitioned joins properly.
- **ch15**: consumer lag as a key alerting metric.
- **Kubernetes StatefulSets**: stable pod identities feed `group.instance.id`.
- **KIP-392 / KIP-848**: closest-replica fetching; next-generation consumer rebalance protocol.
