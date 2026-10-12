# Patterns — Apache Kafka in Action

## Keyed Messages for Per-Entity Ordering
**When to use**: Order matters per entity (customer, order, device) and the topic has >1 partition.
**How**: Give related messages the same key; `hash(key) % partitions` routes them to one partition. Mixed Java + librdkafka producers: set `partitioner=murmur2_random` on librdkafka.
**Trade-offs**: No ordering across keys; hot keys skew partitions; adding partitions remaps keys and breaks order. (Ch 3, 4, 8)

## Reliable Producer Baseline
**When to use**: Any business-relevant data.
**How**: `acks=all`, `enable.idempotence=true`, topic RF 3 + `min.insync.replicas=2`; let the client retry until `delivery.timeout.ms` (2 min), then trip a circuit breaker instead of resending.
**Trade-offs**: Writes stop when ISR < 2 (durability over availability); slightly higher latency. (Ch 5, 8)

## Transactional Read-Process-Write (Exactly-Once)
**When to use**: Consume → transform → produce with no duplicates or loss.
**How**: Unique `transactional.id`; `init/begin_transaction` → produce → `send_offsets_to_transaction` → `commit_transaction`; `enable.auto.commit=false`; downstream `isolation.level=read_committed`.
**Trade-offs**: ~3% overhead at 100 ms transactions, ~30% at 10 ms; an open transaction stalls `read_committed` consumers. (Ch 5)

## Exactly-Once Into a Database
**When to use**: The sink is an RDBMS.
**How**: Idempotent UPSERT (`ON CONFLICT DO NOTHING`) then commit the offset — or store data and offset in one DB transaction and resume from the stored offset.
**Trade-offs**: Needs a natural key, or you own offset management. (Ch 5, 9)

## Consumer-Driven Partition Sizing
**When to use**: Creating any topic.
**How**: partitions ≥ peak msg/s ÷ per-consumer msg/s; default 12; double (24, 48) only when one group needs more parallelism.
**Trade-offs**: More partitions cost client RAM, broker CPU/file handles, slower failover, cloud per-partition fees; can never shrink. (Ch 6)

## Repartition via a New Topic
**When to use**: You must change partition count of a keyed topic, or reduce it.
**How**: Drain during maintenance and recreate; or move producers to a new topic and let consumers drain the old one; or copy with Kafka Streams + offset translation.
**Trade-offs**: Error-prone (duplicates, offset mapping) — use idempotent consumers; good moment to fix naming/format. (Ch 6)

## Producer Throughput Tuning
**When to use**: >100 msg/s or messages near/above 16 KB.
**How**: `batch.size` up to 1 MB, `linger.ms≈10`, `compression.type=zstd|lz4`; measure with `kafka-producer-perf-test.sh`.
**Trade-offs**: Higher linger adds latency at low rates. (Ch 6)

## Static Membership + Cooperative Sticky
**When to use**: Auto-restarting consumers (Kubernetes) where rolling restarts trigger rebalance storms.
**How**: Unique `group.instance.id` per instance (StatefulSet pod name), `session.timeout.ms` in minutes, `CooperativeStickyAssignor`.
**Trade-offs**: A truly dead consumer is detected only after the long timeout. (Ch 9)

## Compliance-Bounded Retention
**When to use**: Legal max retention (e.g., 7 days).
**How**: Enforce `segment.ms + retention.ms + log.retention.check.interval.ms (5 min) ≤ limit` — a segment is deleted only when its newest record expires.
**Trade-offs**: Frequent rolls → more segment files. (Ch 10)

## Compacted State Topic With Tombstones
**When to use**: Latest-state-per-key data (prices, addresses, master data).
**How**: `cleanup.policy=compact`, always keyed; delete via null-value tombstone; set `max.compaction.lag.ms` on low-traffic topics. `delete,compact` to also expire by age.
**Trade-offs**: CPU/IO heavy; the active segment always holds duplicates. (Ch 10)

## Log-Based CDC With Debezium
**When to use**: Every insert/update/delete must reach Kafka.
**How**: PostgreSQL `wal_level=logical`, REPLICATION role, `PostgresConnector` + `plugin.name=pgoutput`, then `ExtractNewRecordState` SMT to emit only `after`.
**Trade-offs**: Needs DB config/privileges; avoid JDBC `incrementing`/`timestamp` polling, which miss updates/deletes. (Ch 11)

## Tolerant Connector With DLQ
**When to use**: Bad records must not halt a pipeline.
**How**: `errors.tolerance=all` + `errors.log.enable=true` + `errors.deadletterqueue.topic.name` (sinks only) + alerting.
**Trade-offs**: Silent skipping unless monitored; logging messages can leak PII. (Ch 11)

## Stream–Table Enrichment Join
**When to use**: Enrich events with master data.
**How**: `builder.stream()` events, `builder.table()` the compacted master topic, `stream.join(table, ValueJoiner)` on co-partitioned keys. Prefer `mapValues()` over `map()` to avoid repartition topics.
**Trade-offs**: Only stream records trigger output; master updates don't re-emit. (Ch 12)

## Windowed Count (Fraud Detection)
**When to use**: Flag N events per key within a time span.
**How**: `groupByKey().windowedBy(TimeWindows…).count().toStream().filter(...)`; add a grace period for late data; sliding windows catch bursts across boundaries.
**Trade-offs**: No grace → late records dropped. (Ch 12)

## Schema Registry via CI/CD
**When to use**: Several teams share evolving topics.
**How**: Document compatibility level + upgrade order per topic; register schemas from the pipeline; disable producer auto-registration; Karapace/Apicurio for OSS.
**Trade-offs**: Extra critical dependency; Kafka itself validates nothing. (Ch 13)

## Zero-Downtime Security Migration
**When to use**: An unsecured PoC cluster becomes production.
**How**: Add TLS+auth listener → move inter-broker traffic → migrate clients → disable old listener → create and enforce all ACLs at once after testing.
**Trade-offs**: Heavy coordination; `allow.everyone.if.no.acl.found=true` tends to linger. (Ch 13)

## GitOps for Kafka Resources
**When to use**: More than one team, from preproduction onward.
**How**: Topics, users, ACLs, schemas, connectors declared in Git → PR + review → pipeline reconciles (kcctl for connectors).
**Trade-offs**: No universal tool; most teams build their own. (Ch 14, 17)

## Stretched Cluster vs. MirrorMaker 2
**When to use**: DC-level resilience.
**How**: ≤30 ms apart → one cluster over ≥3 DCs with `broker.rack`; farther → separate clusters + MirrorMaker 2, preferably active-active with remote topics and idempotent consumers.
**Trade-offs**: Cross-AZ cost vs. async loss window and duplicate processing. (Ch 16)

## Core-System Liberation (CDC → Second DB → Outbox)
**When to use**: New services need core-system data in near real time.
**How**: Debezium CDC into a secondary DB, consolidate with SQL joins, write denormalized outbox tables, CDC those to Kafka. Never expose raw normalized topics.
**Trade-offs**: Extra DB and pipelines, but avoids unmaintainable Streams join apps. (Ch 18)

## Metrics → Alerts With Playbooks
**When to use**: Building Kafka alerting.
**How**: Smooth noisy metrics over minutes, start conservative and tune, alert on few two-state signals, keep the rest as context panels, attach a playbook to every alert.
**Trade-offs**: Too sensitive → alert fatigue; too lax → late detection. (Ch 15)
