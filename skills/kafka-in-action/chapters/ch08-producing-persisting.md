# Chapter 8: Producing and Persisting Messages

## Core Idea
A produced message goes through this path: client (serialize → partition → buffer → batch → send → ACK/retry) → broker (network thread → request queue → I/O thread → page cache → purgatory → response) → on-disk partition directory of segments, indexes and checkpoints. Durability comes from replication, measured by the ISR and High Watermark, not from fsync.

## Frameworks Introduced
- **Producer pipeline (10 steps)**: `produce()`/`send()` → serializer → partitioner → per-partition buffer → batch sent to the partition leader → wait for ACK → on success, the delivery callback runs → if no ACK arrives, the library retries for a while → when it gives up, it raises an exception.
  - When to use: to reason about producer latency, throughput, ordering and error handling.
  - How: use the official Java client or a client built on `librdkafka`, and avoid other libraries, which lack features and optimizations. Kafka only sees bytes, so the producer serializes the data (String, JSON, Protobuf, Avro or a custom serializer). The partitioner hashes the key. With no key, it spreads messages round-robin or by batch. Do not pin a partition by hand unless you have a strong reason. Each partition gets a buffer inside `buffer.memory` (32 MiB). Batches hold up to `batch.size` (16 KiB). The producer sends one batch per broker that groups the partition batches for the partitions that broker leads. It does not wait for batches to fill (`linger.ms=0`), so batching only happens when you produce faster than you can send.
  - Why it works / failure mode: when Java and librdkafka producers write to the same topic, set `partitioner: murmur2_random` in librdkafka. librdkafka uses a different hash by default, so the same key can land in different partitions and per-key ordering is lost.
- **Producer timeout chain**: `max.block.ms` (60 s) limits how long `produce()` blocks when the buffer is full. `linger.ms` (0 ms) is the batch wait. `request.timeout.ms` (30 s) is the wait for one response. `retry.backoff.ms` (100 ms) is the pause between retries. `delivery.timeout.ms` (2 min) is the overall deadline before the library throws an exception.
  - When to use: tuning how long a producer tolerates a degraded cluster.
  - How: let the library handle retries. With `enable.idempotence`, it keeps message order across retries. When the final exception comes, do not resend blindly, because the cluster is probably unhealthy. Catch the failure with a circuit breaker or a similar pattern.
  - Why it works / failure mode: resending at application level duplicates messages and breaks ordering. It also adds load to a cluster that is already struggling.
- **Broker produce path**: network threads receive the request and check authorization → the request goes on the request queue → I/O threads append it to the active log segment in the **page cache** → the response waits in **purgatory** until all in-sync followers have fetched the message → the response goes on the response queue → a network thread sends the ACK.
  - When to use: diagnosing broker-side latency, such as overloaded I/O threads or slow followers that hold responses in purgatory.
  - How: let the OS flush the page cache asynchronously. Kafka does not fsync. `flush.ms` and `flush.messages` force fsync, and both default to Long.MAX (about 300 million years for `flush.ms`). Leave them alone.
  - Why it works / failure mode: skipping fsync is fast, but the data is only safe if the replicas live on independent hardware. Spread brokers across hosts and racks and use rack awareness. If all replicas of a partition sit on one VM host and that host crashes, the data is lost.
- **ISR / LEO / HWM replication model**: followers pull from the leader. Each fetch request carries the follower's LEO, so the leader knows what each follower has. HWM = the smallest LEO among the ISRs. A message is *committed* only when HWM ≥ its offset, regardless of the `acks` setting. Consumers can only read up to the HWM. The leader sends the HWM to followers in fetch responses.
  - When to use: explaining why consumers stall, why `acks=all` fails, and what "committed" means.
  - How: a follower stays in sync if it reached the leader's LEO within `replica.lag.time.max.ms` (30 s). It fetches every `replica.fetch.wait.max.ms` (500 ms). The leader is always in sync. A replica that misses heartbeats leaves the ISR right away.
  - Why it works / failure mode: a slow in-sync follower holds the HWM back, so **all consumers stall** until it drops out of the ISR (up to 30 s). Then the HWM jumps forward. If the ISR count falls below `min.insync.replicas`, producers using `acks=all` are rejected, and the HWM stops advancing, so consumers stall even if producers use `acks=0` or `acks=1`.
- **Leader epoch fencing**: the leader epoch is a counter that goes up with every leader change. It is stored in `leader-epoch-checkpoint` as `<epoch> <start offset>` pairs. Replication messages carry the epoch, and brokers ignore messages with an old epoch. This stops a broker from acting as leader after it has lost that role ("zombie" leader).

## Key Concepts
- **Log segment**: a file triple of `.log`, `.index` and `.timeindex` (plus `.snapshot`). The file name is the segment's first offset, zero-padded to 20 digits.
- **`.index`**: maps offsets to byte positions in the log. It is sparse: one entry every `index.interval.bytes` (4096 B).
- **`.timeindex`**: maps timestamps to offsets. It lets you reset consumers to a point in time, such as the start of the day.
- **`.snapshot`**: producer-state snapshot used for idempotent producers.
- **Purgatory**: the broker area where pending responses wait for follower confirmation.
- **Log End Offset (LEO)**: the offset just after the last message a replica holds.
- **High Watermark (HWM)**: the smallest LEO across the ISRs. It is the committed boundary and the limit of what consumers can read.
- **Last Committed Offset (LCO)**: the fetch offset the leader records for each follower.
- **Eligible Leader Replicas (ELR)**: a new feature. When the ISR count is below `min.insync.replicas`, replicas that are out of sync but have caught up to the HWM can still be elected leader. No message that consumers already read is lost. Messages produced with `acks=0` or `acks=1` can still be lost.
- **Checkpoint files**: `replication-offset-checkpoint`, `recovery-point-offset-checkpoint`, `log-start-offset-checkpoint` and `cleaner-offset-checkpoint`. Format: line 1 = version, line 2 = entry count, then `<topic> <partition> <offset>`.

## Mental Models
- Think of the HWM as the slowest ISR member's position. One lagging in-sync follower sets the visible end of the log for every consumer.
- Think of Kafka durability as "in memory on N machines", not "on disk on one machine". Replication across failure domains replaces fsync.
- Use the producer library's built-in retries for transient failures, and use a circuit breaker for the final exception. Application-level resends are the wrong layer.
- Think of a partition as a folder of rolling segments, with the base offset as the file name. Roll and cleanup work on whole segments.

## Anti-patterns
- **Third-party or non-librdkafka client libraries**: they often lack features and optimizations.
- **Mixing Java and librdkafka producers with default partitioners**: the same key goes to different partitions, and the ordering guarantee is lost.
- **Blindly resending after a producer exception**: it adds load to a failing cluster and can break ordering and idempotence.
- **Setting `flush.ms`/`flush.messages` for durability**: forced fsync costs a lot of performance. Use replication instead.
- **Placing all replicas on one VM host**: a single host crash loses data that was only in the page cache.
- **Cutting `replica.lag.time.max.ms` to about 2 s**: normal async lag causes ISR churn (shrink and expand), controller overhead and risk of dropping below `min.insync.replicas`.
- **Lowering `min.insync.replicas` for performance**: if the only ISR is the leader and it crashes, consumers may already have read data that was never persisted.

## Code Examples
```python
from confluent_kafka import Producer
producer = Producer({
    'bootstrap.servers': 'localhost:9092',
    'acks': -1,                      # = all; recommended reliable config
    'enable.idempotence': True,
    'partitioner': 'murmur2_random', # match the Java client's hashing
})

def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed for record {msg.key()}: {err}")
        return
    print(f"Record {msg.key()} successfully produced to {msg.topic()}
        [{msg.partition()}] at offset {msg.offset()}")

producer.produce(
    "products.prices.changelog",
    key="cola",
    value="2",
    on_delivery=delivery_report)
```
- **What it demonstrates**: a reliable producer config with an asynchronous delivery callback. The callback fires on ACK or on final failure.

```bash
# Inspect batches in a segment (add --print-data-log for payloads)
kafka-dump-log.sh --files ~/kafka/data/kafka1/products.prices.changelog.file-structure-0/00000000000000000000.log
# Force faster segment rolls on one topic
kafka-configs.sh --alter --topic products.prices.changelog.file-structure \
  --add-config segment.ms=60000 --bootstrap-server localhost:9092
# Restore preferred leaders now instead of waiting up to 5 min
kafka-leader-election.sh --election-type=preferred --all-topic-partitions \
  --bootstrap-server localhost:9092
```
- **What it demonstrates**: tools for inspecting segments, rolling them, and electing leaders. The dump shows `baseOffset`, `lastOffset`, `count`, `position`, `CreateTime`, `size` and `crc` for each batch. Each batch has about 60 B of metadata, which is why batching matters for small messages.

## Reference Tables
**Producer settings**

| Setting | Default | Meaning |
|---|---|---|
| `buffer.memory` | 32 MiB | Total send buffer across partitions |
| `batch.size` | 16 KiB | Max batch per partition |
| `linger.ms` | 0 ms | Wait for more messages before sending a batch |
| `max.block.ms` | 60 s | Max block in `produce()`/`send()` when the buffer is full |
| `request.timeout.ms` | 30 s | Wait for a broker response before retrying |
| `retry.backoff.ms` | 100 ms | Pause between retries |
| `delivery.timeout.ms` | 2 min | Total deadline; after it, the library throws an exception |

**Broker / topic settings**

| Topic setting | Broker default key | Default | Meaning |
|---|---|---|---|
| `flush.ms` / `flush.messages` | `log.flush.*` | Long.MAX | Forced fsync (do not use) |
| `index.interval.bytes` | `log.index.interval.bytes` | 4096 B | Bytes between sparse index entries |
| `segment.bytes` | `log.segment.bytes` | 1 GiB | Roll the segment at this size |
| `segment.ms` | `log.roll.ms` | 7 days | Roll the segment at this age |
| `file.delete.delay.ms` | `log.segment.delete.delay.ms` | 1 min | Delay before `-delete` dirs are removed |
| — | `replica.lag.time.max.ms` | 30 s | Max lag before a replica leaves the ISR |
| — | `replica.fetch.wait.max.ms` | 500 ms | Follower fetch interval |
| — | `leader.imbalance.check.interval.seconds` | 300 s | Preferred-leader rebalance check |

**Broker data directory (`~/kafka/data/kafka<ID>/`)**

| File | Content |
|---|---|
| `meta.properties` | broker ID, cluster ID, directory ID, metadata version |
| `bootstrap.checkpoint`, `__cluster_metadata-0/` | KRaft metadata |
| `replication-offset-checkpoint` | offset per partition up to which replication is done (HWM) |
| `recovery-point-offset-checkpoint` | offset up to which data has been flushed to disk |
| `log-start-offset-checkpoint` | first offset still in the log (not necessarily 0) |
| `cleaner-offset-checkpoint` | offset up to which the log cleaner has compacted |
| `<topic>-<p>/partition.metadata` | version + `topic_id` |
| `<topic>-<p>/leader-epoch-checkpoint` | leader epoch + start offset |

## Worked Example
**Following the leader epoch through a broker failure.** Topic `products.prices.changelog.file-structure` has 3 partitions and RF 3. Brokers 1, 2 and 3 lead partitions 0, 1 and 2. Every `leader-epoch-checkpoint` starts at `0 1 0 0`, meaning version 0, one entry, epoch 0, start offset 0. Stop broker 3 with `kafka-broker-stop.sh 3`. A new leader is elected for partition 2, and the epoch file now reads `0 1 1 0` (epoch 1). Restart broker 3 with `kafka-server-start.sh -daemon .../kafka3.properties`. If it still believes it leads partition 2 with epoch 0, the other brokers reject its replication messages because the current epoch is 1. Broker 3 soon learns the current leader and epoch. It becomes the preferred leader again either within 5 minutes (`leader.imbalance.check.interval.seconds`) or right away via `kafka-leader-election.sh --election-type=preferred`. Its partition-2 checkpoint then shows epoch 2. Next, produce keyless messages: `replication-offset-checkpoint` shows uneven offsets of 8/2/2, because batching puts several messages in one partition. Setting `segment.ms=60000` and producing again creates `00000000000000000003.{log,index,timeindex,snapshot}`, and the new file names show the segment's base offset. Deleting the topic renames the folders to `<topic>-<p>.<UniqueID>-delete`. They are removed after 1 minute, and until then the data can still be recovered.

## Key Takeaways
1. Use reliable producer defaults: `acks=all` (-1), `enable.idempotence=true`, and `partitioner=murmur2_random` when librdkafka clients share topics with Java clients.
2. Leave retries to the library and stay within `delivery.timeout.ms` (2 min). When the final exception arrives, trip a circuit breaker instead of resending.
3. Kafka writes to the page cache and never fsyncs by default. Get durability from RF 3, `min.insync.replicas=2` and replicas spread across hosts and racks.
4. Consumers only see data up to the HWM. One lagging in-sync follower stalls every consumer for up to `replica.lag.time.max.ms` (30 s). Do not shrink that value aggressively.
5. If the ISR count drops below `min.insync.replicas`, `acks=all` produces fail and consumption also stops, whatever `acks` the producers use.
6. Segments roll at 1 GiB or 7 days. The sparse index has an entry every 4 KiB. The time index enables "replay from the start of the day" resets.
7. A deleted topic stays recoverable for `file.delete.delay.ms` (1 min) as `-delete` directories.

## Connects To
- **ch04**: partitions, leaders/followers and the log abstraction that this chapter shows on disk.
- **ch05**: `acks`, idempotence, `min.insync.replicas` and preferred leader election, applied here at the byte level.
- **ch06**: batching, `linger.ms` and page-cache performance.
- **ch07**: bootstrap/metadata discovery of leaders, and KRaft `__cluster_metadata`.
- **ch09**: consumers read up to the HWM, offset resets via `.timeindex`, and rack awareness.
- **ch10**: retention and compaction work on whole segments, `log-start-offset` and `cleaner-offset-checkpoint`.
- **ch13**: serializers (JSON, Protobuf, Avro) and schema management.
- **ch15**: ISR shrink/expand and under-replicated partitions as alert signals.
- **Circuit Breaker (Fowler)**: the pattern for handling final producer exceptions.
