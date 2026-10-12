# Chapter 10: Cleaning Up Messages

## Core Idea
Kafka removes data with two segment-based policies: **log retention** (`delete`), which drops whole segments by age or size, and **log compaction** (`compact`), which keeps only the latest record per key. Neither runs on the active segment, so the real deletion time depends on segment rolling. Retention guarantees must therefore be computed from `segment.ms` + `retention.ms` + check interval, not from `retention.ms` alone.

## Frameworks Introduced
- **Choosing a cleanup policy** (`cleanup.policy` per topic, `log.cleanup.policy` cluster default = `delete`; `delete,compact` combines both):
  - When to use: `delete` for time-bounded data such as privacy/compliance deletion, sensor data that goes stale, application logs, or pure messaging. `compact` for "current state per key" data such as customer addresses or price tables, where old values are obsolete but the latest must never expire by age.
  - How: decide whether records are *events that expire* (delete) or *state updates keyed by entity* (compact). Compaction requires keys: brokers reject keyless records with `InvalidRecordException: Compacted topic cannot accept message without key`.
  - Trade-off: retention is cheap (age check only) but blind, so it deletes important data just because it's old. Compaction is precise but expensive, because it must scan the whole partition.
- **Log retention timing (segment-level deletion)**: a segment is deleted only when its *newest* message is older than `retention.ms` (default 7 days), or, if `retention.bytes` is set, when the partition exceeds that size (oldest segment goes first). The check runs every `log.retention.check.interval.ms` (default 5 min). The active segment can't be deleted while it keeps receiving writes.
  - When to use: any hard maximum-retention requirement (e.g., "keep at most 7 days").
  - How: force regular rolls with `segment.ms`, then pick `retention.ms` so that `segment.ms + retention.ms + log.retention.check.interval.ms ≤ legal maximum`. Rolling more often gives finer-grained deletion and lets you set a higher `retention.ms`.
  - Why it works / failure mode: setting only `retention.ms = 7d` on a continuously written topic lets the open segment hold messages far older than 7 days, which breaks compliance.
- **Log compaction eligibility**: the log cleaner wakes every `log.cleaner.backoff.ms` (15 s). A partition is eligible if *(uncompacted messages older than `max.compaction.lag.ms`)* **OR** *(dirty ratio ≥ `min.cleanable.dirty.ratio` **AND** uncompacted messages older than `min.compaction.lag.ms`)*. The dirty ratio also prioritizes which eligible partition is compacted first. The active segment is always excluded.
  - How: lower `min.cleanable.dirty.ratio` to reduce wasted space, at a CPU/IO cost. Set `max.compaction.lag.ms` to force compaction on low-throughput topics; it also forces a segment roll on the next produce. Set `min.compaction.lag.ms` to guarantee consumers see every update for a minimum time.
  - Why it works / failure mode: a ratio near 0 would keep brokers busy compacting continuously, since every pass reads the full partition.
- **Log cleaner algorithm**: (1) scan dirty segments and record the latest offset per key; (2) read from the oldest message, skip superseded keys, write survivors into a new segment; (3) swap the clean segment in for the old ones (old files get a `.deleted` suffix, then are removed). Needs at most one extra segment of disk. Offsets and order are preserved, and gaps are fine because a fetch for a missing offset returns the next available message.
- **Tombstones**: a record with a key and a `null` payload. Compaction deletes earlier values for that key, and the tombstone itself is removed after `delete.retention.ms` (topic) / `log.cleaner.delete.retention.ms` (cluster), default 1 day. The delay gives consumers time to see and act on the deletion. Removing the tombstone keeps logs from filling with markers for dead keys.

## Key Concepts
- **Log retention**: deletion of whole segments by age (`retention.ms`) or partition size (`retention.bytes`).
- **Log compaction**: deletion of records superseded by a newer record with the same key; guarantees at least the latest value per key survives.
- **Log cleaner**: broker background component that performs retention and compaction, always segment by segment.
- **Active (current) segment**: the segment currently being written; never deleted by retention while it's still being written, and never compacted.
- **Dirty segment**: a segment that has never been compacted. **Dirty ratio** = dirty log / total log.
- **Tombstone**: keyed record with `null` value that marks a key for deletion under compaction.
- **Offset retention**: expiry of committed offsets of *inactive* consumer groups via `offsets.retention.minutes` (default 7 days).
- **Offset gap**: missing offsets after cleanup; consumers transparently receive the next existing offset.

## Mental Models
- Think of retention as **"drop the oldest box when its newest item expires"**. Granularity equals segment size/age, never single messages.
- Think of a compacted topic as **a key-value table persisted as a changelog**: latest value per key, plus a recent tail that may still contain duplicates.
- Use `min.cleanable.dirty.ratio` as a **space-vs-CPU dial**: ratio r means the outdated data in the log is at most r/(1−r) of the needed size (0.5 → up to 2× storage; 0.2 → ≤ 25% overhead).
- Use `max.compaction.lag.ms` when **a low-traffic compacted topic must actually get compacted**. Otherwise the 0.5 ratio may never be reached.

## Anti-patterns
- **Relying on `retention.ms` alone for a legal maximum**: the active segment isn't deleted while it keeps receiving writes, so data outlives the limit. Also cap `segment.ms` and subtract the 5-minute check interval.
- **Producing keyless records to a compacted topic**: rejected by the broker (`InvalidRecordException`).
- **Setting `min.cleanable.dirty.ratio` to ~0**: brokers spend all their resources rewriting partitions.
- **Purging a topic by temporarily setting `retention.ms=0`**: an old trick; use the Admin API (delete records) instead.
- **Shortening `offsets.retention.minutes`**: a group paused for a bug fix longer than the window loses its offsets. Offsets are tiny, so increasing the value is safer than decreasing it.
- **Expecting compaction to dedupe immediately**: the newest segment can hold any number of records per key until it rolls and the cleaner runs.

## Code Examples
```bash
# Shorten retention to 60 s on an existing topic
kafka-configs.sh --alter \
  --topic products.prices-retention \
  --add-config retention.ms=60000 \
  --bootstrap-server localhost:9092

# Create a compacted topic
kafka-topics.sh --create \
  --topic products.prices-compaction \
  --partitions 3 \
  --replication-factor 3 \
  --config cleanup.policy=compact \
  --bootstrap-server localhost:9092

# Keyed produce (required for compaction)
kafka-console-producer.sh \
  --topic products.prices-compaction \
  --property parse.key=true \
  --property key.separator=: \
  --bootstrap-server localhost:9092

# Force segment roll / bounded compaction delay
kafka-configs.sh --alter \
  --topic products.prices-compaction \
  --add-config max.compaction.lag.ms=60000 \
  --bootstrap-server localhost:9092

# Inspect keys/values inside a segment file
kafka-dump-log.sh --print-data-log \
  --files ~/kafka/data/kafka1/products.prices-compaction-0/00000000000000000000.log
```
- **What it demonstrates**: switching a topic's cleanup behavior at runtime and verifying the result directly on segment files.

## Reference Tables
| Topic config | Broker/cluster default key | Default | Meaning |
|---|---|---|---|
| `cleanup.policy` | `log.cleanup.policy` | `delete` | `delete`, `compact`, or both |
| `retention.ms` | `log.retention.ms` | 7 days | Delete segment when its newest message is older than this |
| `retention.bytes` | `log.retention.bytes` | `-1` (off) | Delete oldest segment when partition exceeds this size |
| — | `log.retention.check.interval.ms` | 5 min | How often retention is evaluated |
| `segment.ms` | — | (see ch08) | Time-based segment roll; bounds retention precision |
| `min.cleanable.dirty.ratio` | `log.cleaner.min.cleanable.dirty.ratio` | `0.5` | Dirty/total threshold for compaction |
| `min.compaction.lag.ms` | `log.cleaner.min.compaction.lag.ms` | `0` | Minimum age before a record may be compacted |
| `max.compaction.lag.ms` | `log.cleaner.max.compaction.lag.ms` | `9223372036854775807` (~300 million years) | Maximum time a record may stay uncompacted; also forces roll |
| `delete.retention.ms` | `log.cleaner.delete.retention.ms` | 1 day | How long tombstones are kept |
| — | `log.cleaner.backoff.ms` | 15 s | Cleaner polling interval |
| — | `offsets.retention.minutes` | 7 days | Expiry of inactive groups' committed offsets |

| Aspect | Log retention (`delete`) | Log compaction (`compact`) |
|---|---|---|
| Criterion | Age / partition size | Newer record with same key |
| Keys required | No | Yes (keyless rejected) |
| Broker overhead | Low | High (full partition scan) |
| Guarantee | Data gone after bound (if segments roll) | Latest value per key always kept |
| Typical use | Compliance deletion, sensors, logs, messaging | Entity state (addresses, prices), `__consumer_offsets` |

## Worked Example
**Sizing retention for a 7-day legal maximum.** Budget = 7 days − 5 min (`log.retention.check.interval.ms`) and split it between `segment.ms` and `retention.ms`:
- `segment.ms` = 6 days, so `retention.ms` ≤ 23 h 55 min. Messages are 1–7 days old when deleted, which means a lot of data is lost early.
- `segment.ms` = 1 day, so `retention.ms` = 5 days 23 h 55 min. Messages are 6–7 days old when deleted.
More frequent rolls give finer deletion and a longer usable `retention.ms`.

**Compaction walkthrough.** On compacted `products.prices-compaction`, key `energy drink` lands in partition 0 (values 5, then 3). Both stay because they sit in the active segment. Set `max.compaction.lag.ms=60000` and produce `energy drink:6`: the segment rolls (`…0004.log` appears), the cleaner rewrites segment 0 so it keeps only offset 3, and the old file briefly shows `.deleted`. Produce 5 and 6 quickly: another roll (`…0005.log`). The new active segment holds both 5 and 6 uncompacted, while the cleaned older segment holds exactly one record for the key (offset 4, value 6). Offsets never shift. A fetch for deleted offset 0 returns the next existing record.

## Key Takeaways
1. Pick `delete` for expiring events and `compact` for latest-state-per-key data; combine them when you need both.
2. For a hard retention limit, enforce `segment.ms + retention.ms + log.retention.check.interval.ms ≤ limit`.
3. The active segment is never compacted, and retention can't delete it while it keeps receiving writes. Segment rolling drives cleanup timing.
4. On low-volume compacted topics, set `max.compaction.lag.ms`. Use `min.compaction.lag.ms` to give consumers a guaranteed window to see every update.
5. Delete a key in a compacted topic with a tombstone (`null` value). Keep `delete.retention.ms` long enough for all consumers to observe it (default 1 day).
6. Don't lower `offsets.retention.minutes`; consider raising it.
7. Purge topics via the Admin API, not by toggling `retention.ms`.

## Connects To
- **ch03**: keys and partitioning, which compaction depends on.
- **ch08**: segment files (`.log`, `.index`, `.timeindex`), `segment.ms`/`segment.bytes` rolling, `kafka-dump-log.sh`.
- **ch09**: `__consumer_offsets` is compacted; offset gaps are transparent to consumers.
- **ch11 / ch12**: Connect internal topics and Kafka Streams changelogs/KTables rely on compaction and tombstones.
- **ch13**: data-protection requirements (deletion deadlines, right to be forgotten via tombstones).
- **GDPR / data-retention regulation**: drives the retention sizing calculation.
