# Chapter 6: Performance

## Core Idea
Kafka is already tuned for performance by design: an append-only log, sequential I/O, the page cache, zero-copy, and "dumb broker, smart client." Most of your performance wins therefore come from choosing the right partition count up front and tuning the clients: producer batching and compression, consumer fetch sizes. Define performance first (bandwidth vs. end-to-end latency vs. resource use), then **understand, measure, optimize**.

## Frameworks Introduced
- **Partition-count sizing (consumer-bottleneck rule)**: size partitions from the number of parallel consumers you need, not from Kafka's capacity.
  - When to use: creating any topic, especially one with keyed (ordered) data, because the count is hard to change later.
  - How: (1) Find the bottleneck. Is it the consumer, Kafka, or an external system such as a slow DB? (2) Measure per-message processing time, giving consumer throughput = 1 / time. (3) Partitions ≥ peak rate / per-consumer throughput. (4) Add headroom and pick an easily divisible number (ideally divisible by the broker count too). (5) Default to **12** across all use cases. If you need more than 12 parallel consumers in one group, **double** (24, 48…). (6) Check cost and limits: some cloud providers (e.g. Confluent) bill per partition.
  - Why it works / failure mode: a partition is consumed by at most one member of a group, so the partition count caps group parallelism. Too many partitions cost client RAM, broker CPU/memory/file handles, longer recovery after a broker failure (minutes of leader redistribution under ZooKeeper), and harder monitoring. More partitions are pointless if the downstream DB is the bottleneck.
- **Producer batching (`batch.size` + `linger.ms`)**: the producer keeps one batch per topic-partition and sends it when the batch is full **or** the linger time expires.
  - When to use: any producer sending more than about 100 msg/s, or messages larger than the 16 KB default batch.
  - How: raise `batch.size` up to **1 MB** (capped by `max.message.bytes`) and set `linger.ms ≈ 10`. For low-rate producers you can raise `linger.ms` further, at some latency cost. Re-measure after every change.
  - Why it works / failure mode: fewer, larger requests mean less network and broker overhead and better compression. If messages are larger than `batch.size`, no batching happens, messages queue up, and latency gets *worse*. Bigger batches can therefore lower latency as well as raise throughput.
- **Batch-level end-to-end compression (`compression.type`)**: the producer compresses a whole batch once. The leader stores it unchanged and replicates it unchanged, and only the consumer decompresses it.
  - How: set `compression.type` to `zstd` or `lz4` (best throughput/CPU balance). `gzip` compresses better but costs more CPU. Standardize the setting across all producers of a topic.
  - Payoff: reduces network traffic (producer→leader, leader→followers, broker→consumer) and disk usage at the same time. Bigger batches compress better.
- **Consumer fetch tuning (`fetch.min.bytes` + `fetch.max.wait.ms`)**: the broker holds a fetch until at least `fetch.min.bytes` is available or `fetch.max.wait.ms` has elapsed.
  - How: raise `fetch.min.bytes` (e.g. 1 MB) for throughput and keep `fetch.max.wait.ms` at 500 to bound latency. Never set either to 0.
- **Broker/OS tuning checklist**: raise the max open file descriptors, tune vm dirty-page writeback to flush early, minimize swappiness, and tune the network. Set `num.network.threads` 3→6 when using TLS, `num.io.threads` = number of disks, and `queued.max.requests` > 500 to match the number of client connections.
- **Broker-count sizing**: brokers = (daily volume × retention days × replication factor) / disk per broker, then check network and throughput. Start with 3 brokers (RF 3, survives maintenance plus one failure) and grow.

## Key Concepts
- **Bandwidth vs. latency**: throughput (bytes/s) and end-to-end latency are different goals. High throughput does not imply low latency, and latency usually matters more to users.
- **Resource friendliness**: a third performance dimension. Get the target bandwidth and latency with minimal CPU, RAM, disk and cost.
- **Page cache write / no fsync**: brokers write to the OS page cache and ACK without flushing to disk. Durability comes from replication across brokers, not from fsync.
- **Zero-copy transfer**: because the on-wire format equals the on-disk format, the Linux kernel moves data between socket and page cache by pointer manipulation. It is **lost with TLS**.
- **Fetch-based (pull) consumers**: consumers decide when and how much to fetch, so a correct consumer cannot be overloaded by the broker.
- **Ordering scope**: order is guaranteed only within a partition, from a single producer, and only with `enable.idempotence=true` (otherwise retries can reorder).
- **Key → partition mapping**: `hash(key) mod numPartitions`. Changing the partition count remaps keys.
- **Share groups (Queues for Kafka)**: an upcoming feature that lets more consumers than partitions read cooperatively. It gives queue semantics without strict ordering and does not replace partitioning for ordered, high-throughput cases.
- **Idempotent consumption**: include an event ID so a consumer can detect and skip already-processed events, for example after an offset-translation migration.

## Mental Models
- Think of the **consumer as the usual ceiling**. Size partitions for consumer parallelism and check external systems before adding partitions.
- Think of a **truck full of microSD cards**: enormous bandwidth, terrible latency. Always ask which of the two you are optimizing.
- Use **"understand → measure → optimize"** before touching broker configs. Broker defaults are already good, and most tuning belongs in the clients.
- Think of **partition count as near-immutable** for keyed topics. Increasing it breaks per-key ordering until old data ages out, and decreasing it is impossible.

## Anti-patterns
- **Over-partitioning "just in case"**: wastes client RAM and broker resources, slows failover, raises cloud cost, and often exceeds what downstream DBs can absorb anyway.
- **Increasing partitions on a keyed topic in place**: keys land in new partitions, so per-key order breaks until retention deletes the old data. New partitions also start empty, which skews the distribution.
- **Custom partitioners**: possible, but avoid them in general. The default producer-side partitioning keeps broker coordination low.
- **Leaving `batch.size` at 16 KB with large messages**: no batching happens, and both latency and throughput suffer.
- **`fetch.min.bytes=0` or `fetch.max.wait.ms=0`**: the broker answers immediately and the consumer re-requests immediately, for every partition. That can reach about 10,000 requests/s from a single consumer at 1 ms RTT.
- **Mixed compression settings across producers of one topic**: it works, but throughput and storage efficiency become inconsistent.
- **Trusting one run of a perf test**: JVM warm-up skews early numbers. Repeat runs, and use production-like data and environments (JMeter for end-to-end).

## Code Examples
```bash
# Baseline producer test: 1M records x 10,000 bytes, unthrottled
$ kafka-producer-perf-test.sh \
    --topic performance-test \
    --num-records 1000000 \
    --record-size 10000 \
    --throughput -1 \
    --producer-props bootstrap.servers=localhost:9092

# Same test with bigger batches and linger
$ kafka-producer-perf-test.sh \
    --topic performance-test \
    --num-records 1000000 \
    --record-size 10000 \
    --throughput -1 \
    --producer-props bootstrap.servers=localhost:9092 \
      batch.size=100000 linger.ms=100

# Consumer test; consumer settings must come from a file
$ kafka-consumer-perf-test.sh \
    --topic performance-test \
    --consumer.config ./consumer.properties \
    --messages 1000000 \
    --bootstrap-server localhost:9092

# Clean up (the test writes ~10 GB)
$ kafka-topics.sh --delete --topic performance-test --bootstrap-server localhost:9092
```
```properties
# consumer.properties
fetch.min.bytes: 1000000
fetch.max.wait.ms: 500
```
- **What it demonstrates**: A/B testing client settings with Kafka's built-in perf tools. Producer props go inline via `--producer-props`, while consumer props require `--consumer.config`.

## Reference Tables
**Producer settings (Table 6.1, with chapter defaults/recommendations)**

| Setting | Default | Effect / recommendation |
|---|---|---|
| `acks` | — (see ch05) | `0`: highest throughput, data loss possible. `1`: slightly lower, loss less likely. `-1`/`all`: slightly lower again, highest reliability. Choose by reliability needs, not performance. |
| `enable.idempotence` | — | `false` not recommended. `true` guarantees order and uniqueness and is only compatible with `acks=-1`. |
| `compression.type` | `none` | `gzip`: better ratio, more CPU. `zstd`/`snappy`/`lz4`: can perform better. Prefer `zstd` or `lz4`. |
| `batch.size` | 16384 B (16 KB) | Higher means more throughput and latency. Go up to 1 MB (limited by `max.message.bytes`). |
| `linger.ms` | 0 | Higher means more throughput and latency. About 10 ms is recommended for >100 msg/s. |

**Consumer settings**

| Setting | Default | Meaning |
|---|---|---|
| `fetch.min.bytes` | 1 | Minimum bytes the broker waits for before responding. Never 0. |
| `fetch.max.wait.ms` | 500 | Maximum wait before responding even if `fetch.min.bytes` is not reached. Never 0. |

**Broker tuning**

| Setting | Default | Guidance |
|---|---|---|
| `num.network.threads` | 3 | 6 when using TLS |
| `num.io.threads` | — | = number of data disks |
| `queued.max.requests` | 500 | Raise to roughly the number of client connections |

**Partition limits**: ZooKeeper-mode guidance is ≤ 4,000 partitions per broker and ≤ 200,000 per cluster. KRaft allows significantly more.

**Measured results (local, 1 partition, RF 1, 1M × 10 KB)**

| Test | Throughput | Avg latency |
|---|---|---|
| Producer defaults | 117.47 MB/s (~12.3k rec/s) | 165 ms (p99 287 ms) |
| Producer `batch.size=100000 linger.ms=100` | 437.55 MB/s (~45.9k rec/s) | 64.6 ms (p99 126 ms) |
| Consumer defaults | 547 MB/s, 17 s | — |
| Consumer `fetch.min.bytes=1000000` | 734 MB/s, 13 s | — |

## Worked Example
**Sizing partitions and brokers for a slow sink.** A consumer writes each message to a slow data store and needs about 100 ms per message, so it handles 10 msg/s. Peak load is 100 msg/s, so you need at least 10 consumers, which means at least 10 partitions. Round up to the default **12**: it gives headroom and divides cleanly by 2, 3, 4 and 6 consumers and by 3 brokers. Before going further, check whether the data store tolerates 12 concurrent writers. If it doesn't, more partitions buy nothing.

For storage, assume 1 TB/day, 7-day retention and 2 TB disks. That is 7 TB of data, so at least 4 brokers. With replication factor 3 the total is 21 TB, so **11 brokers**. Then validate the expected data rate against the NICs.

**Producer fix.** With 10 KB messages and the 16 KB default `batch.size`, batching barely happens. Raising `batch.size` to 100000 and `linger.ms` to 100 took throughput from 117 to 437 MB/s **and** cut average latency from 165 to 65 ms.

## Key Takeaways
1. Decide whether you are optimizing bandwidth, latency, or resource use before you tune anything.
2. Default to 12 partitions and double only when one group needs more than 12 parallel consumers. Weigh RAM, recovery time and per-partition pricing.
3. Treat the partition count as fixed for keyed topics. To change it, create a new topic and migrate: drain it during a maintenance window, switch producers and let consumers drain the old topic, or copy the data with Kafka Streams and translate offsets.
4. Set `batch.size` up to 1 MB, `linger.ms` ≈ 10 and `compression.type=zstd|lz4` on producers. These are the biggest, cheapest wins.
5. Leave broker defaults mostly alone. Tune the OS instead (file descriptors, swappiness, dirty-page writeback, network), and remember that TLS disables zero-copy.
6. Raise `fetch.min.bytes` for consumer throughput, never set it or `fetch.max.wait.ms` to 0, and scale consumers through consumer groups.

## Connects To
- **ch04**: partitions, consumer groups and ordering semantics that drive the partition-count decision.
- **ch05**: `acks`, `enable.idempotence` and replication as the reliability side of the trade-off.
- **ch08**: producer internals behind batching, compression and persistence.
- **ch09**: consumer fetch mechanics and group scaling.
- **ch10**: retention determines how long disorder lasts after repartitioning.
- **ch12**: joins require co-partitioned topics (same partition count), and Kafka Streams can be used to copy topics.
- **ch13**: TLS costs zero-copy and needs more network threads.
- **ch15**: monitor limits you can't tune, e.g. on Kubernetes.
- **Apache JMeter**: end-to-end performance testing beyond the perf-test scripts.
