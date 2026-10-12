# Cheatsheet — Apache Kafka in Action

## Durability decision (acks × RF × min ISR)
| Need | Setting | Survives |
|---|---|---|
| Loss acceptable, max speed (sensor readings) | `acks=0` | nothing guaranteed |
| Default for real data | `acks=all`, RF 3, `min.insync.replicas=2`, idempotence on | 1 broker loss, no client impact |
| Higher tolerance | RF 4, min ISR 2 | 2 broker losses |
| Trap | `acks=all` + min ISR 1 | behaves like `acks=1` → loss |
2nd loss at RF 3/min ISR 2 → producers blocked, HWM frozen; consumers read only up to HWM.

## Delivery guarantee
- Loss OK → at-most-once (`acks=0`).
- No loss, duplicates OK → at-least-once (`acks=all`, retries).
- Exactly once inside Kafka → idempotence + transactions + `read_committed`.
- Exactly once into a DB → UPSERT, or offset in the same DB transaction.
- Set `isolation.level=read_committed` everywhere now — adopting transactions later needs no consumer change.

## Partitions
- Default **12**; double only when one group needs >12 consumers. Never decreases.
- Keyed topic: changing the count breaks per-key order → migrate to a new topic.
- Consumers > partitions in one group → idle consumers.
- ZooKeeper era: ≤4,000/broker, ≤200,000/cluster (KRaft: much more).

## Producer / consumer tuning
| Key | Default | Use |
|---|---|---|
| `batch.size` | 16 KB | up to 1 MB |
| `linger.ms` | 0 | ≈10 above 100 msg/s |
| `compression.type` | none | zstd / lz4 |
| `delivery.timeout.ms` | 2 min | then circuit breaker, no blind resend |
| `fetch.min.bytes` / `fetch.max.wait.ms` | 1 / 500 | never 0 (→ ~10k req/s) |
| `auto.offset.reset` | latest | `earliest` for new groups needing history |
| `replica.lag.time.max.ms` | 30 s | don't lower to ~2 s (ISR churn) |

## Retention & compaction
- Hard limit: `segment.ms + retention.ms + 5 min ≤ legal max`.
- `min.cleanable.dirty.ratio` r → up to r/(1−r) overhead: 0.5 = 2× storage, 0.2 = 25%. Never ≈0.
- Low-traffic compacted topic never compacts → set `max.compaction.lag.ms`.
- Delete key → tombstone (null value), kept `delete.retention.ms` = 1 day.
- Don't shorten `offsets.retention.minutes` (7 d). Purge with delete-records, not `retention.ms=0`.

## Cluster sizing
- ≥3 brokers; controllers 3 (tolerate 1) or 5 (tolerate 2); 4 adds nothing. Prod: dedicated controllers.
- Brokers = daily volume × retention days × RF ÷ disk/broker (1 TB × 7 × 3 ÷ 2 TB ≈ 11).
- RAM: heap 1–6 GB; page cache = ingest/broker/hour × tolerated lag hours; 32–64 GB/broker, then add brokers.
- Several small SSDs, no RAID 5/6; ≥1 Gbit/s; inter-broker latency < 30 ms (AZs yes, regions no).
- TLS → `num.network.threads` 3→6; `num.io.threads` = disks.

## Resilience choice
- Broker loss → replication (above). Lost broker → new host, **same broker ID**.
- DC loss, ≤30 ms → stretched cluster over **≥3** DCs + `broker.rack`/`client.rack`.
- Farther → MirrorMaker 2; prefer active-active (idempotent consumers, regex over local+remote topics).
- Backup only if Kafka is the source of truth (offsets and compacted topics are hard to back up).
- Never let disks fill — keep a ~10 GB spare file to delete.

## Alert thresholds
| Signal | Alert when |
|---|---|
| UnderReplicated / UnderMinIsr / Offline partitions | > 0 (UnderMinIsr blocks `acks=all`) |
| ActiveControllerCount | ≠ 1 across cluster |
| NetworkProcessorAvgIdlePercent | < 0.3 sustained |
| Disk / network utilization | > 60% |
| records-lag ↑ with records-lead ↓ | data about to be lost |
| failed Connect tasks / Streams threads / record-error-rate | > 0 |
| CPU 100% | only if sustained minutes |

## Schema evolution
| Level | Can read | Update first | Safe change |
|---|---|---|---|
| Backward | old data with new schema | consumers | delete fields |
| Forward | new data with old schema | producers | add fields |
| Full | both | either | add/remove optional (default) fields |
Renames break everything → new topic + migration.

## Is Kafka the right tool?
- < 1,000 msg/h, no growth in a year, one team → no (Postgres table as log), unless Kafka already exists.
- Need an immediate answer (UI, trading) → synchronous REST; Kafka for decoupled flows.
- Querying current state → DB / materialized view, never Kafka.
- Files/PDFs → object storage + pointer (1 MB default limit).
- One central cluster by default; split only for isolation, security/GDPR, geography, extreme scale.

## Smells
- Console consumer shows nothing → missing `--from-beginning`.
- Two apps "stealing" messages → shared `group.id`.
- Keys landing in different partitions across services → librdkafka vs Java hash (`murmur2_random`).
- Rebalance on every deploy → no static membership / eager assignor.
- Humans writing via GUI or creating topics in prod → missing GitOps.
