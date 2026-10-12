# Chapter 4: Kafka as a Distributed Log

## Core Idea
Kafka is an append-only, offset-addressed log that is **split** (partitions, for parallelism) and **copied** (replication, for resilience) across commodity brokers. Ordering holds only within a partition, keys decide the partition, and consumer groups scale reads one partition per consumer. Kafka is a data hub for moving data between systems. It is not a database you query.

## Frameworks Introduced
- **The log abstraction (two operations)**: a log is a list of events that supports only (1) *write*, which appends to the end, and (2) *read*, which starts at a chosen position and moves from old to new, usually to the end. Its properties are time ordering (oldest at the start), one write/read direction, and immutability (once written, an entry is not changed).
  - When to use: to reason about what Kafka can and cannot do. If the access pattern isn't "append" or "scan forward from a position", Kafka is the wrong store.
  - How: address data only by **offset**, a consecutive per-partition position with no meaning of its own (like a page number). The broker assigns the offset at write time. Consumers note the next offset to read, poll for new entries and advance. Kafka persists that bookmark in the internal `__consumer_offsets` topic, so progress survives a restart.
  - Why it works / failure mode: logs are among the simplest data structures. They are easy to replicate (copy message by message) and easy to split (use several logs instead of one). They also give you history and "time travel": replay up to any point to rebuild past state. The failure mode is treating Kafka as a key-value store or an ad hoc query engine, which turns every lookup into a scan of the whole log.
- **Kafka as central data hub (not a central database)**: share data through Kafka, and inside each service sink it into the store that fits the use case. Use Elasticsearch for search, PostgreSQL for ad hoc or complex queries, and Redis for fast access to prepared data.
  - When to use: whenever a team wants to "query Kafka" or replace its databases, caches or analytics tools with Kafka.
  - How: Kafka holds the event history. Each consumer materializes its own view in its own technology.
- **Key-based partitioning**: `partition_number = hash(key) % number_of_partitions`, computed in the producer library.
  - When to use: when the order between related messages matters, for example all price changes of one product. Give them the same key.
  - How: set the same key on related messages so they land in one partition, which gives ordering per key. With no key, the producer spreads messages across partitions. Older producers used plain per-message round-robin. Since Kafka 2.4 the producer is batch-aware: it sticks to one partition until a batch is sent, then switches. This means fewer requests, fuller batches and better compression.
  - Why it works / failure mode: Kafka guarantees order **only within a partition**. Two things break per-key ordering. (1) **Changing the partition count** of a live topic changes the modulo, so keys move to other partitions. (2) **Mixed client libraries**: librdkafka's default hash differs from the Java client's murmur2. Set `partitioner=murmur2_random` in librdkafka producers. **Skewed keys** (a few keys carrying most of the traffic, such as "top members" producing more than 90% of a social network's load) create hot partitions.
- **Consumer groups**: consumers that share the same `group.id` split a topic's partitions among themselves and commit their offsets to Kafka.
  - When to use: to scale one service horizontally (one group per service), and to let independent services read the same topic without affecting each other (a separate group per service).
  - How: within a group, each partition is read by **at most one** consumer, and one consumer may read several partitions. More consumers than partitions leaves some idle. Groups are isolated from each other. Restarting a consumer with the same group resumes from the committed offset.
  - Why it works: one reader per partition preserves order. The pull model means a slow consumer only falls behind and is never overloaded.
- **Warm replication: one leader, several followers**: replication factor (RF) is set per topic. Each partition has one leader and RF−1 followers, and together they are its replicas. All reads and writes go through the leader. Followers fetch from the leader by offset, like consumers do, and append to their own local logs.
  - When to use: always in production. RF cannot exceed the broker count.
  - How: if the leader fails, an in-sync replica (ISR) or an eligible leader replica (ELR) becomes the new leader, and clients switch to it automatically. By default the first broker in the `Replicas` list is the preferred leader. Kafka spreads partition leaders evenly across brokers. Keep that balance in production, because Kafka's performance depends on it.
  - Failure mode: replication is not a backup. Kafka has no *cold* replication, so backups are your responsibility.

## Key Concepts
- **Offset**: a consecutive position of a record within a partition. The broker assigns it on write, and it serves as both the record's address and the consumer's bookmark.
- **`__consumer_offsets`**: an internal topic where Kafka durably stores each consumer group's committed offsets.
- **Partition**: an independent ordered log within a topic. It is the unit of parallelism, distribution and ordering (similar to sharding).
- **Partitioner**: the producer-side logic that picks a partition, using the key hash or batch-aware round-robin when there is no key.
- **Replica / leader / follower**: every broker that stores a partition is a replica. The leader serves all I/O, and the followers pull from it to stay current.
- **ISR (in-sync replicas)**: the replicas that are up to date. If the ISR list is shorter than the Replicas list, a broker is lagging or has failed.
- **ELR (eligible leader replica)**: a replica that may still be elected leader when it isn't in the ISR. It appears as `Elr:` in `--describe` output.
- **Coordination cluster**: KRaft controllers, or formerly a ZooKeeper ensemble. It tracks live brokers, topic metadata, partition-to-broker assignment, leaders and ACLs, and it designates the **controller**, which reassigns partitions and elects leaders when a broker fails.
- **Clients**: every external application that connects to the cluster, including producers, consumers, Kafka Streams (both consumer and producer) and Kafka Connect. Java clients use the Kafka API. Other languages typically use librdkafka.
- **Vertical vs horizontal scaling**: vertical means a bigger machine (more performance, but no gain in reliability). Horizontal means more machines (parallelism and redundancy, at the cost of coordination complexity).

## Mental Models
- **Think of a log as a diary written in ballpoint pen**: pages are filled in order, nothing is left blank, entries are read from old to new, and edits are visible. Offsets are the page numbers and the consumer's bookmark.
- **Think of a partition key as "what must stay ordered together"**: city for a cab exchange, product ID for prices. Order across keys doesn't matter, so those keys can scale out.
- **Use one consumer group per service, and as many consumers in it as partitions (at most)**: the partition count is the ceiling on read parallelism.
- **Think of failure as normal**: commodity disks fail at about 1% per year (Backblaze data). Kafka accepts failure and designs around it with replication and simple structures rather than buying expensive hardware.

## Anti-patterns
- **Using Kafka as a database or key-value store**: the offset is the only address. Ad hoc queries or lookups by key mean scanning the log. Sink the data into a fit-for-purpose store instead.
- **Producing order-sensitive data without keys to a multi-partition topic**: messages are spread across partitions and read back interleaved, which in the shop example produces wrong prices and inconsistent systems.
- **Increasing partitions on a keyed topic in flight**: `hash(key) % N` changes, keys move partitions, and the ordering guarantee is lost.
- **Mixing Java and default librdkafka producers on keyed topics**: different hash functions partition the same key differently, which breaks joins and aggregations (for example in Kafka Streams).
- **Low-cardinality or hot keys**: a few dominant keys overload a few partitions and brokers.
- **Two brokers, or an even-sized coordination cluster**: with two brokers, one in maintenance plus one failure means data loss. An even-sized quorum gains no fault tolerance.
- **Treating replication as a backup**: replication is warm availability. It does not protect against deletion or corruption.

## Code Examples
```bash
# Keyed producer: same key -> same partition -> per-key order preserved
$ kafka-console-producer.sh \
    --topic products.prices.changelog.multi-partitions-keys \
    --property parse.key=true \
    --property key.separator=":" \
    --bootstrap-server localhost:9092
> coffee pads:10
> cola:2
> energy drink:3

# Consumer in a group: offsets committed, load shared with same --group
$ kafka-console-consumer.sh \
    --from-beginning \
    --topic products.prices.changelog.multi-partitions-keys \
    --property print.key=true \
    --property key.separator=":" \
    --group products \
    --bootstrap-server localhost:9092
```
- **What it demonstrates**: keys pin related records to one partition, and `--group` makes consumers share partitions and resume from committed offsets. A second run of the same group prints `Processed a total of 0 messages`.

```bash
$ kafka-topics.sh --create --topic products.prices.replication \
    --partitions 3 --replication-factor 3 --bootstrap-server localhost:9092
$ kafka-topics.sh --describe --topic products.prices.replication \
    --bootstrap-server localhost:9092
Topic: products.prices.replication  Partition: 0  Leader: 2  Replicas: 2,1,3  Isr: 2,1,3  Elr:
Topic: products.prices.replication  Partition: 1  Leader: 3  Replicas: 3,2,1  Isr: 3,2,1  Elr:
Topic: products.prices.replication  Partition: 2  Leader: 1  Replicas: 1,3,2  Isr: 1,3,2  Elr:
```
- **What it demonstrates**: leaders are spread across brokers, the first entry in the Replicas list is the preferred leader, and ISR equals Replicas in a healthy cluster. `--replication-factor 4` on 3 brokers fails with `InvalidReplicationFactorException: ... only 3 broker(s) are registered`.

## Reference Tables

| Partitioning mode | Trigger | Ordering | Notes |
|---|---|---|---|
| Key hash | key set | Per key (within its partition) | `hash(key) % partitions`. Breaks if the partition count changes |
| Batch-aware round-robin (Kafka ≥ 2.4) | no key | None across partitions | Switches partition after each batch: fewer requests, better batching and compression |
| librdkafka default | key set, non-Java client | Inconsistent with Java | Set `partitioner=murmur2_random` |

| Replication type | Example | Recovery time | In Kafka? |
|---|---|---|---|
| Cold | Backups | Slow (restore) | No, do it yourself |
| Warm | Replicas on running brokers | Almost immediate failover | Yes, RF per topic |

| Sizing rule | Value |
|---|---|
| Minimum brokers | 3 |
| Coordination nodes (KRaft or ZooKeeper) | Odd number: 3 for small clusters (tolerates 1 failure), 5 for larger ones (tolerates 2) |
| Max replication factor | ≤ number of brokers |
| Max useful consumers per group | = number of partitions |
| KRaft production-ready | Kafka 3.3+. Combined broker/controller roles are fine for small clusters. Use a dedicated controller cluster for large ones |

| Ecosystem need | Component |
|---|---|
| Integrate DBs and third-party systems | Kafka Connect (ships with Kafka, Apache 2.0) |
| HTTP/REST or mainframe access | REST proxy (Confluent REST Proxy, or Aiven Karapace, which is open source) |
| Stream processing | Kafka Streams, Apache Flink, Akka |
| Schema management | Git repo, Confluent Schema Registry, Karapace registry (Kafka ships none) |
| Multi-DC mirroring | MirrorMaker 2 |
| Operations | Monitoring, automation (no manual setup), compliance enforcement |

## Worked Example
**Ordering lost, then restored with keys.** Create `products.prices.changelog.multi-partitions` with `--partitions 2 --replication-factor 1`. Produce six messages without keys: `coffee pads 10, cola 2, energy drink 3, coffee pads 11, coffee pads 12, coffee pads 10`. Consuming `--from-beginning` returns them interleaved, for example `cola 2, coffee pads 11, coffee pads 10, ...`. The odd-numbered and even-numbered messages went to different partitions, and the consumer drains one partition and then the other. The "current" coffee-pad price is now wrong. You may need to restart the producer or consume several times to see this with so few messages.

Fix it with a new topic, `...-multi-partitions-keys`, produced with `parse.key=true` and `key.separator=":"`, using the product name as the key. The global order still differs from the produce order, but each key's sequence is intact: `coffee pads:10, 11, 12, 10`, `cola:2, 1` and `energy drink:3, 4`. Then start two consumers with `--group products` and produce more `cola` and `energy drink` records. Consumer 1 receives all the `cola` records (2, 5, 2) and Consumer 2 receives all the `energy drink` records (2, 3, 1), so each consumer owns one partition. Had `coffee pads` been used instead of `energy drink`, everything could have gone to one consumer, because both keys hash to the same partition. A third consumer would sit idle.

## Key Takeaways
1. Key every message whose relative order matters, and choose the key as the smallest unit that needs ordering. Order is guaranteed only within a partition.
2. Fix the partition count up front for keyed topics. Changing it remaps keys and voids ordering.
3. In polyglot environments, set `partitioner=murmur2_random` on librdkafka producers so they partition the same way as Java clients.
4. Scale consumption with consumer groups: one `group.id` per service, with at most as many consumers as partitions.
5. Run at least 3 brokers and an odd-sized coordination quorum (3, or 5 for large clusters). Use RF 3, and check that ISR matches Replicas.
6. Don't query Kafka. Stream data out into Elasticsearch, PostgreSQL, Redis and similar stores, and keep Kafka as the hub.
7. Kafka alone isn't a streaming platform. Plan for Connect, schema management, stream processing, MirrorMaker 2 or backups, monitoring, automation and compliance.

## Connects To
- **ch03**: covers message keys and the topic/message structure that partitioning relies on.
- **ch05**: covers ISR/ELR, acks and leader failover in depth (reliability).
- **ch06**: covers partition count, consumer-group scaling and batching performance.
- **ch07**: covers KRaft vs ZooKeeper coordination clusters and controller duties.
- **ch08 / ch09**: cover partitioner and producer internals, and consumer group rebalancing and offset commits.
- **ch10**: covers log compaction by key.
- **ch11 / ch12 / ch13 / ch16 / ch18**: cover Connect, stream processing, schema registry, MirrorMaker 2 and backups, and the enterprise streaming platform.
- **Database commit log / write-ahead log**: Kafka exposes the commit log that databases hide, and its replication is log shipping.
- **Sharding**: partitioning is sharding applied to a log.
