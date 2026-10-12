# Chapter 3: Exploring Kafka topics and messages

## Core Idea
A topic is a named, partitioned, replicated channel that you manage with `kafka-topics.sh` (partitions can only grow, never shrink). A message is a byte array made of a timestamp, an optional key, a value and optional headers. Choose the message type (state/delta/event/command), keep one consistent data format, and use keys wherever per-entity ordering matters.

## Frameworks Introduced
- **Topic lifecycle with `kafka-topics.sh`**: one CLI covers `--list`, `--describe`, `--create`, `--alter` and `--delete`, always with `--bootstrap-server` (any broker works, because it does not matter which broker manages the topic).
  - When to use: to inspect a topic someone else created, to provision a new topic, or to scale an existing one.
  - How: (1) `--list` to see which topics exist; (2) `--describe --topic X` to read TopicId, PartitionCount, ReplicationFactor, Configs (empty means all defaults) and one line per partition showing Leader/Replicas/Isr/Elr/LastKnownElr; (3) `--create --partitions N --replication-factor R`; (4) `--alter --partitions M` with M > N to add partitions; (5) `--delete` to drop the topic and its data. Its offsets in `__consumer_offsets` are cleaned up too.
  - Why it works / failure mode: Kafka places leaders and replicas automatically to spread the load across brokers. Deleting and re-creating a topic to resize it loses all its data, so use `--alter` instead. Partitions can never be reduced, because moving data between partitions would break per-partition ordering. Replication factor cannot be changed with `--alter --partitions`. It needs `--replica-assignment` or `kafka-reassign-partitions.sh`, and it can never exceed the broker count.
- **Four message types (states, deltas, events, commands)**: classify every message by the question it answers.
  - When to use: when you design a topic's payload contract. Real systems mix all four. For example, an ERP emits a price-change *event*, a promotions service reacts by sending a *command* to a notification service, and that service is reusable by others.
  - How: **State**: the full current picture of an object ("what does it look like now?"). Pairs with keys plus log compaction to keep only the latest. **Delta**: only the changed fields. It saves volume and makes it obvious what changed, but a single delta is useless without context or a base state. **Event**: what happened, with business context ("what just happened?"). It is often derived from states and deltas in another topic, and logs are a special case of events. **Command**: asks another system to act in the future, which adds coupling because the sender depends on the recipient executing it.
  - Why it works / failure mode: an event's sender does not care who consumes it, so it stays loosely coupled. A command needs action from a specific receiver, so the coupling is tight. Choosing deltas where consumers need full state forces them to rebuild state.
- **Keys for per-entity ordering**: Kafka uses the key to pick the partition, so all messages with the same key land in the same partition and keep their order (for a single producer).
  - When to use: whenever a topic has more than 1 partition and the order per entity matters (prices per product, for example).
  - How: produce with a key (console: `--property parse.key=true --property key.separator=:`). Accept that there is no ordering across different keys. Without a key, the authors say messages are spread round-robin across partitions.
  - Why it works / failure mode: ordering is guaranteed only within a partition. Without keys on a multi-partition topic, `coffee pads:11` can be read before `coffee pads:10`, which shows wrong prices and makes systems inconsistent.

## Key Concepts
- **Topic**: a logical channel that organizes data flow, roughly comparable to a database table. Topics are agnostic of keys, so nothing special is needed at creation time to hold keyed messages.
- **Partition**: a unit of parallelism inside a topic, numbered from 0. It lets producers write, and consumers read, concurrently.
- **Replication factor**: how many brokers store a copy of each partition. RF=1 means no failover, and RF can never exceed the number of brokers.
- **Leader**: the broker with primary responsibility for a partition.
- **ISR (in-sync replicas)**: the brokers whose replicas are up to date for that partition.
- **ELR (eligible leader replicas) / LastKnownElr**: ELR lists the ISR members eligible to become leader if the current leader fails. LastKnownElr lists previously eligible replicas that had an unclean shutdown.
- **`__consumer_offsets`**: an internal topic (50 partitions) that stores each consumer's read position, which works like a bookmark. The double-underscore prefix is reserved for Kafka.
- **Message / record**: a timestamp (always present), an optional key, a value (the main payload) and optional custom headers. To Kafka, all of these are just byte arrays.
- **Headers**: technical metadata such as tracing IDs, similar to HTTP headers. Never put business data in them, and it is fine not to use them at all.
- **Schema**: the blueprint for a data format (Avro or Protobuf schemas, JSON Schema, XSD or DTD). Binary formats cannot be interpreted without one, and optional fields are what make deltas valid.

## Mental Models
- Think of a topic as a **database table without a query engine**: Kafka stores bytes and never interprets them, and that is a key reason it is fast.
- Use **keys** when you need per-entity ordering on a topic with more than one partition. Think of the key as a partition router, not a primary key, because old messages with the same key are not deleted (unless you use compaction).
- Think of Kafka as built for **many small messages** (LinkedIn handled about 7 trillion a day across about 100 clusters in 2019), not for moving large files. Keep messages at or below the 1 MB default.
- Use **events** to decouple producers from consumers. Use **commands** only when you truly need a specific system to act, and accept the coupling that comes with it.

## Anti-patterns
- **Naming your own topics with `__`**: the prefix is reserved for internal topics. It causes conflicts, future compatibility breakage and admin confusion.
- **Deleting and re-creating a topic to resize it**: you lose all its data. Use `--alter` or a reassignment instead.
- **Trying to reduce the partition count**: this is not possible, and it would cause data loss and break ordering.
- **Raising the 1 MB message limit to ship big files**: performance and resource usage suffer badly. Use another transport for large files.
- **A different data format per topic**: the cost grows as the cluster grows and ages. Pick one consistent format, document it, and back it with schemas.
- **Business data in headers**: headers are for technical metadata only.
- **Keyless messages on multi-partition topics where order matters**: per-entity order is lost.

## Code Examples
```bash
# Inspect, create, grow, delete
kafka-topics.sh --list --bootstrap-server localhost:9092
kafka-topics.sh --describe --topic products.prices.changelog --bootstrap-server localhost:9092
kafka-topics.sh --create --topic products.prices.changelog \
  --replication-factor 2 --partitions 2 --bootstrap-server localhost:9092
kafka-topics.sh --alter --topic products.prices.changelog \
  --partitions 3 --bootstrap-server localhost:9092
kafka-topics.sh --delete --topic products.prices.changelog --bootstrap-server localhost:9092
```
- **What it demonstrates**: the full topic lifecycle with one tool. `--alter` adds partitions without moving existing leaders or replicas.

```bash
# Produce and consume with keys (key properties are client-side, not broker/topic settings)
kafka-console-producer.sh --topic products.prices.changelog.keys \
  --property parse.key=true --property key.separator=: \
  --bootstrap-server localhost:9092
> coffee pads:10
> cola:2

kafka-console-consumer.sh --from-beginning --topic products.prices.changelog.keys \
  --property print.key=true --property key.separator=":" \
  --bootstrap-server localhost:9092
```
- **What it demonstrates**: the consumer hides keys unless you set `print.key=true`. `--from-beginning` reads from the earliest offset, while the default is to read only new messages from the end.

```json
// state     {"id": 123, "name": "coffee pad", "price": "10", "stock": 101010}
// delta     {"id": 345, "stock": 60, "price": 3}
// event     {"id": 234, "event": "promotion_start", "payload": {"price": 1.99}}
// command   {"command": "notify_customer", "customer_id": 123456, "message": "The promotion for Coke Zero started. It's now 1.99"}
```
- **What it demonstrates**: how the same product domain looks when written as each of the four message types.

## Reference Tables

**`kafka-topics.sh --describe` fields**

| Field | Meaning |
|---|---|
| TopicId | A unique ID that Kafka generates automatically. It changes when the topic is re-created. |
| PartitionCount | Number of partitions (`--partitions`) |
| ReplicationFactor | Copies per partition (`--replication-factor`) |
| Configs | Topic-level overrides. Empty means defaults. |
| Leader | ID of the broker primarily responsible for the partition |
| Replicas | IDs of the brokers that hold the partition |
| Isr | Replicas that are currently in sync |
| Elr / LastKnownElr | ISR members eligible as next leader / previously eligible replicas that had an unclean shutdown |

**Message types**

| Type | Answers | Pros | Cons |
|---|---|---|---|
| State | What does the object look like now (or historically)? | Self-contained, and compactable with keys | Repeats unchanged fields |
| Delta | What changed? | Small, and makes changes easy to spot | Useless alone, needs context or a base state |
| Event | What just happened? | Business context, loosely coupled | Often has to be derived from states and deltas |
| Command | What should be done next? | Directs a specific action | Couples the sender to the receiver |

**Data formats**

| Format | Human-readable | Size | Schema |
|---|---|---|---|
| JSON | Yes | Inflated, and compression helps only a little | JSON Schema |
| XML | Yes | Inflated | XSD / DTD |
| Avro (common in the Kafka community) / Protobuf | No (harder for humans, and almost every topic gets read by a human at some point) | Compact | Mandatory |

**Limits and defaults**: max message size 1 MB (adjustable, but avoid changing it). `__consumer_offsets` has 50 partitions. RF must be ≤ the number of brokers. The partition count can only increase.

## Worked Example
**Re-create and scale `products.prices.changelog` on 3 brokers.**
1. Start with `--describe` on the original topic: PartitionCount 1 and RF 1, with `Leader: 3 Replicas: 3 Isr: 3`. The partition lives only on broker 3, so there is no failover.
2. Run `--delete`. A following `--list` shows only `__consumer_offsets`, whose offsets for the deleted topic were also removed.
3. Run `--create --partitions 2 --replication-factor 2`. `--describe` now shows partition 0 with `Leader: 3 Replicas: 3,2` and partition 1 with `Leader: 1 Replicas: 1,3`. Kafka balances the placement: no single broker ever leads both partitions, and the 4 replicas never sit on only 2 of the 3 brokers. Re-creating the topic only changes which broker gets which role.
4. Performance is no longer enough, so run `--alter --partitions 3`. Partitions 0 and 1 keep their leaders and replicas. The new partition 2 gets `Leader: 2 Replicas: 2,3`. The placement takes `__consumer_offsets` into account: its 50 partition leaders were split 17/16/16, so new leaders went to the brokers that led fewer partitions. Adding 3 partitions instead (to 5 total) would have given each broker exactly one more leader, which is perfectly even.
5. To change RF later, use `--replica-assignment` (fine for a single topic) or `kafka-reassign-partitions.sh`, which handles complex multi-topic reassignments and can redistribute assignments automatically.

## Key Takeaways
1. Run `kafka-topics.sh --describe` before you use someone else's topic. It shows partitions, RF, overrides and the leader/ISR health of every partition.
2. Size partitions with some headroom from the start. You can add them with `--alter` but never remove them, and adding them changes key-to-partition placement.
3. Use RF ≥ 2 for any data you care about (RF=1 means no failover), and remember that RF ≤ the broker count.
4. Key every message whose per-entity order matters. Order exists only within a partition, and that is usually enough.
5. Decide the message type deliberately: state for "current picture", delta for compact changes, event for decoupled facts, command only when you need a specific system to act.
6. Standardize on one data format across the cluster, back it with schemas, and document it. Consistency matters more than which format you pick.
7. Keep messages small (≤ 1 MB), put only technical metadata in headers, and never prefix your own topics with `__`.

## Connects To
- **ch02**: introduced `kafka-console-producer.sh`/`-consumer.sh` and the original `products.prices.changelog` topic.
- **ch04**: partitions and replication as a distributed log, which explains why order is per partition only.
- **ch05**: ISR/ELR, leader failover and how replication factor affects reliability.
- **ch06**: partitioning strategy, choosing partition counts, and why partitions cannot shrink.
- **ch08**: how producers pick partitions from keys, and ISR/ELR details.
- **ch09**: consumer offsets stored in `__consumer_offsets` and `--from-beginning` semantics.
- **ch10**: log compaction with keys, so state topics keep only the latest value.
- **ch13**: schema management for Avro, Protobuf and JSON Schema.
- **ch07**: the KRaft coordination cluster that manages brokers.
- **Event-driven architecture (events vs commands)**: the coupling trade-off maps onto EIP's Event Message vs Command Message.
