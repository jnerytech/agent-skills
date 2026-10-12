# Chapter 5: Reliability

## Core Idea
Reliability in Kafka is three properties: durability, availability and consistency. You tune them through the producer's `acks` setting, the topic's `min.insync.replicas`, idempotent producers, transactions and leader-follower replication. The safe baseline is `acks=all` + `min.insync.replicas=2` + replication factor 3 + idempotence on + consumers on `read_committed`. Every deviation from that baseline buys speed or availability with data you can lose or duplicate.

## Frameworks Introduced
- **ACK strategies (`acks`, producer-side)**: `acks=0` (fire-and-forget, like UDP), `acks=1` (the leader confirms on receipt, like TCP), `acks=all` / `acks=-1` (the leader confirms only after every in-sync replica has the message). Since Kafka 3.0 the default is `acks=all`. It was `acks=1` before that.
  - When to use: use `acks=all` for anything business-relevant. Use `acks=0` only when losing data is acceptable, such as a temperature sensor sending a reading every millisecond where only the latest value matters. `acks=1` saves a little latency but loses data if the leader dies before followers replicate.
  - How: set it on the producer, never on the topic (`--producer-property acks=all` in the console producer). It is independent of topic config, but its real effect depends on `min.insync.replicas`.
  - Why it works / failure mode: `acks=all` waits for the ISR, but the ISR can shrink to just the leader. With `min.insync.replicas=1` and one ISR left, `acks=all` silently degrades to `acks=1`.
- **`acks=all` + `min.insync.replicas` (topic-side)**: the leader refuses writes with `NOT_ENOUGH_REPLICAS` when fewer than `min.insync.replicas` replicas are in sync. The producer retries and finally gets `NotEnoughReplicasException`.
  - When to use: on every topic whose data must not be lost.
  - How: replication factor 3 → `min.insync.replicas=2`, which tolerates one broker down while still accepting writes. To lose two brokers and still have one in reserve, use RF 4 and min ISR 2.
  - Why it works / failure mode: it trades write availability for durability. Below min ISR, `acks=all` producers stop, and they stop loudly. `acks=0`/`acks=1` writes are still accepted but are not consumable until the ISR is back to min ISR. In older versions, consuming did not require min ISR.
- **Message delivery guarantees**: *at most once* = `acks=0` (no duplicates, possible loss). *At least once* = `acks=all` + a reasonable `min.insync.replicas` (no loss, possible duplicates when an ACK gets lost and the producer resends). *Exactly once* = idempotence + `acks=all` (no loss, no duplicates, correct order per partition).
- **Idempotent producer (`enable.idempotence=true`)**: the producer stamps each message with a sequence ID. The partition leader sees an already-persisted duplicate and resends only the ACK. When messages arrive out of order it sends a NACK and the producer retries.
  - How: this requires `acks=all`, `max.in.flight.requests.per.connection` ≤ 5 (default 5) and `retries` > 0 (default 2147483647). A delivery timeout stops infinite resending. It is on by default in modern clients; the chapter dates the default change to Kafka 3.0 in one place and 3.3 in another. The performance cost is negligible, so keep it on.
- **Kafka transactions (variant of Two-Phase Commit)**: atomic writes across several partitions, either all committed or none. They are built from (1) idempotent producers, for reliable writes to each partition, and (2) a **transaction coordinator** (a broker) that writes commit or abort markers.
  - How (producer): set a unique `transactional.id`, then `init_transactions()` → `begin_transaction()` → `produce()`… → (optionally `send_offsets_to_transaction()`) → `commit_transaction()` or `abort_transaction()`.
  - How (consume-process-produce): set the consumer to `enable.auto.commit=False` and commit offsets through the producer with `send_offsets_to_transaction()`, so the offset write to `__consumer_offsets` joins the same transaction. Only producers can take part in transactions.
  - How (consumer): set `isolation.level=read_committed`, otherwise consumers read tentative data and the transaction is meaningless.
  - Why it works / failure mode: aborted messages are not deleted. They are marked, and the broker filters them out. An open transaction blocks `read_committed` consumers on that partition, including non-transactional messages written after it, because ordering must hold.
- **Leader-follower replication**: each partition has one leader. Followers are essentially consumers that pull with a special fetch request and report their offset, which is how the leader knows when to send `acks=all` confirmations. When a leader fails, the controller picks a new leader from the ISR or the ELR set (eligible leader replicas).
- **Preferred vs unclean leader election**: the *preferred leader* is the first broker in the `Replicas` list. After a failed broker re-syncs, leadership returns to it automatically after a few minutes (by default) or manually via `kafka-leader-election.sh --election-type=preferred`. An *unclean* election (`--election-type=unclean` or broker config `unclean.leader.election.enable`) lets an out-of-sync replica lead when no ISR exists. Expect data loss with it.

## Key Concepts
- **Durability**: data, once written, stays stored correctly.
- **Availability**: consumers can read and producers can write at all times, as far as possible.
- **Consistency**: data is persisted exactly as intended, with no loss, duplicates or reordering. This is the hardest of the three to achieve in a distributed system.
- **ISR (in-sync replica)**: a replica that has fetched the leader's current data recently (within the last 30 s, the `replica.lag.time.max.ms` default).
- **ELR (eligible leader replica)**: a replica outside the ISR that is still allowed to become leader. It appears as `Elr:` in `--describe` output; ch08 covers it in depth.
- **Idempotence**: repeating an operation with the same input gives the same result. In Kafka this means a resent message is persisted once.
- **NACK**: the negative acknowledgment a leader sends when an idempotent producer's messages arrive out of sequence. It triggers a resend.
- **`transactional.id`**: a unique, stable ID for a transactional producer. A newer producer with the same ID fences the old one as a *zombie*.
- **Transaction coordinator**: the broker that registers a transaction's partitions and writes commit or abort markers. It keeps the guarantees intact even through broker or producer crashes.
- **Under-replicated partition**: a partition whose ISR is smaller than its replica list. *Under-min-ISR* means the ISR is smaller than `min.insync.replicas`.

## Mental Models
- Think of `acks` as transport protocols: `0` = UDP, `1` = TCP (the receiver got it), `all` = "every in-sync copy got it".
- Think of `min.insync.replicas` as the floor under `acks=all`. Without a floor > 1, `acks=all` is only as strong as `acks=1` once the ISR shrinks.
- Think of a Kafka transaction as booking a trip. Reserve the hotel with a 10-minute cancellation window (tentative writes), book the flight, then confirm or cancel the hotel (commit or abort marker). If you never call back, the reservation expires.
- Use the read-process-write transaction pattern (or Kafka Streams, which packages it) when output topics and consumer offsets must move together. When the sink is a database, use idempotent upserts or store the offsets in the database instead.

## Anti-patterns
- **`acks=all` with `min.insync.replicas=1` (or unset)**: when the ISR shrinks to the leader, it degrades to `acks=1`, so you lose data when the leader fails.
- **Disabling idempotence "for performance"**: the cost is negligible, and real performance problems lie elsewhere.
- **Consumers left on the default isolation level**: they read uncommitted or aborted transactional data. Set `read_committed` everywhere now, even before you adopt transactions, so you never have to touch every consumer later.
- **Committing offsets from the consumer inside a consume-transform-produce app**: the offset commit falls outside the transaction, which brings back loss or duplicates.
- **Two producers sharing a `transactional.id`**: they interfere, and one gets fenced as a zombie.
- **Very short transactions**: the coordinator overhead is per partition, not per message. A 10 ms transaction has about 30% overhead, against about 3% for 100 ms.
- **Unclean leader election as a habit or cluster-wide setting**: it guarantees data loss. Use it only in an extreme emergency (no ISR left, partition unusable), and always scope it with `--topic`, never `--all-topic-partitions`.

## Code Examples
```bash
# Topic that refuses acks=all writes unless 2 replicas are in sync
kafka-topics.sh --create \
  --topic products.prices.changelog.min-isr-2 \
  --replication-factor 3 --partitions 3 \
  --config min.insync.replicas=2 \
  --bootstrap-server localhost:9092

# Reliable producer: acks=all + idempotence
kafka-console-producer.sh \
  --topic products.prices.changelog.min-isr-2 \
  --bootstrap-server localhost:9092 \
  --producer-property acks=all \
  --producer-property enable.idempotence=true
```
- **What it demonstrates**: the producer setting and the topic setting combine to give at-least-once durability, and adding idempotence gives exactly-once writes.

```python
from confluent_kafka import Producer

producer = Producer({
    'bootstrap.servers': 'localhost:9092',
    'acks': 'all',                    # recommended reliable-producer settings
    'enable.idempotence': True,
    'partitioner': 'murmur2_random',  # compatible with Java producers' partitioning
    'transactional.id': 'transaction-1',
})
producer.init_transactions()
producer.begin_transaction()
producer.produce("customer.balance", key="bob", value="-10")
producer.produce("customer.balance", key="alice", value="+10")
producer.commit_transaction()       # or producer.abort_transaction()
```
- **What it demonstrates**: an atomic Bob→Alice transfer. Both balance changes become visible together, or neither does.

```sql
-- Exactly-once into a DB, option 1: idempotent upsert, commit Kafka offset after
INSERT INTO products_price_changelog (id, timestamp, name, price)
VALUES (…) ON CONFLICT DO NOTHING;

-- Option 2: store offsets in the DB, atomically with the data
BEGIN TRANSACTION;
INSERT INTO products_price_changelog (id, timestamp, name, price) VALUES (…);
INSERT INTO offsets (topic, partition, offset) VALUES ('products_price_changelog', 0, 123);
COMMIT;
```
- **What it demonstrates**: the two ways to get exactly-once semantics when the sink is not Kafka.

```bash
kafka-topics.sh --describe --bootstrap-server localhost:9092 --under-replicated-partitions
kafka-topics.sh --describe --bootstrap-server localhost:9092 --under-min-isr-partitions
kafka-leader-election.sh --election-type=preferred --all-topic-partitions \
  --bootstrap-server localhost:9092
```
- **What it demonstrates**: commands that check replication health across the whole cluster, and a manual rebalance back to the preferred leaders.

## Reference Tables

| `acks` | ACK sent when | Guarantee | Loss risk | Duplicates | Analogy |
|---|---|---|---|---|---|
| `0` | never | at most once | yes | no | UDP |
| `1` | leader persisted | at least once (only with retries) | yes, if the leader dies before replicating | yes | TCP |
| `all` / `-1` (default since 3.0) | all ISRs persisted (≥ `min.insync.replicas`) | at least once; exactly once with idempotence | no, if min ISR ≥ 2 | only without idempotence | — |

| Guarantee | Required config |
|---|---|
| At most once | `acks=0` |
| At least once | `acks=all` + `min.insync.replicas` ≥ 2 |
| Exactly once (per partition) | `acks=all` + `enable.idempotence=true` |
| Exactly once (multi-partition / read-process-write) | the above + `transactional.id` + transactions + `send_offsets_to_transaction()` + `enable.auto.commit=False` + consumers `isolation.level=read_committed` |

| Setting | Scope | Default / recommendation |
|---|---|---|
| `acks` | producer | `all` (since 3.0; `1` before) |
| `min.insync.replicas` | topic (`--config`) | recommend 2 with RF 3; RF 4 + 2 to survive losing 2 brokers |
| `enable.idempotence` | producer | keep `true` |
| `max.in.flight.requests.per.connection` | producer | 5; must be ≤ 5 for idempotence |
| `retries` | producer | 2147483647; must be > 0 for idempotence (a delivery timeout caps it) |
| `transactional.id` | producer | unique per producer instance |
| `isolation.level` | consumer | set `read_committed` on all consumers |
| `enable.auto.commit` | consumer | `False` in transactional consume-produce apps |
| `unclean.leader.election.enable` | broker | leave off |
| ISR lag window | broker | in sync if fetched within 30 s |

How `read_committed` consumers see a partition:

| Partition state | What the consumer receives |
|---|---|
| Open (uncommitted) transaction | Nothing past the transaction's first message, including unrelated non-transactional messages |
| Transaction committed | Everything up to the commit marker is released, in order |
| Transaction aborted | Aborted messages are skipped; non-transactional ones are delivered |
| Another transaction open before the marker | Only up to that transaction's first message, until it also finishes |

## Worked Example
**Write behavior below min ISR.** Create `products.prices.changelog.min-isr-2` with RF 3, 3 partitions and `min.insync.replicas=2`. `--describe` shows `Isr: 1,2,3` for every partition. Stop brokers 3 and 2 with `kafka-broker-stop.sh`. Broker 1 now leads all three partitions with `Isr: 1`. If broker 2 was the active controller, briefly restart one broker so that a quorum can elect a new one.

Start a console consumer `--from-beginning`, then produce:
- `cola 0` with `acks=0`. No error, but nothing reaches the consumer, and you cannot know whether it was persisted.
- `cola 1` with `acks=1`. No error, and it is persisted on the leader, but it still is not consumable because consuming requires min ISR.
- `cola all` with `acks=all`. Warnings show `NOT_ENOUGH_REPLICAS, retrying (2…1…0 attempts left)`, then `NotEnoughReplicasException: Messages are rejected since there are fewer in-sync replicas than required.`

Restart brokers 2 and 3 (`kafka-server-start.sh -daemon …kafka2.properties` and `…kafka3.properties`). They catch up, the ISR is back to 3, and `cola 0` and `cola 1` now appear on the consumer. With only one broker stopped (ISR 2 ≥ 2), `acks=all` would have kept working.

**Leader failover and preferred-leader return.** On `replication-3` (leaders 2/3/1 for partitions 0/1/2), stopping broker 3 makes broker 1 the leader of partition 1, and broker 3 drops out of the ISR. `--under-replicated-partitions` lists all three partitions. `--under-min-isr-partitions` lists none, because ISR 2 = min ISR. After restarting broker 3, it rejoins the ISR as a follower. `kafka-leader-election.sh --election-type=preferred` (or waiting a few minutes) makes it the leader of partition 1 again, since it is first in `Replicas: 3,1,2`.

## Key Takeaways
1. The default reliable setup is `acks=all`, `enable.idempotence=true`, RF 3, `min.insync.replicas=2`. Size RF and min ISR from how many broker failures you must survive.
2. `acks=all` without `min.insync.replicas` ≥ 2 is a false sense of safety, because it collapses to `acks=1` when the ISR shrinks.
3. Idempotence gives exactly-once, in-order writes per partition at negligible cost. Transactions extend this to atomic writes across partitions, including consumer offsets.
4. In read-process-write apps, disable auto-commit and commit offsets through `send_offsets_to_transaction()`. Set every consumer to `read_committed`.
5. Keep transactions long enough (about 100 ms or more) to amortize the per-partition marker overhead, and never let one stay open for long, because it stalls `read_committed` consumers.
6. Monitor `--under-replicated-partitions` and `--under-min-isr-partitions`. Reserve unclean leader election for emergencies, and only for a specific topic.

## Connects To
- **ch04**: replication, partition leaders and the log underpin everything here.
- **ch06**: the performance side of `acks`, idempotence and transaction overhead.
- **ch07**: controller and quorum behavior during broker failures (the active-controller caveat in the demo).
- **ch08**: producer internals, retries, ISR/ELR membership rules and leader eligibility in depth.
- **ch09**: consumer offset commits and `isolation.level` in practice.
- **ch12**: Kafka Streams packages read-process-write exactly-once.
- **ch15**: alerting on under-replicated and under-min-ISR partitions.
- **ch16**: unclean leader election and data-loss trade-offs in disasters.
- **Two-Phase Commit**: Kafka transactions are a variant of it, coordinated by the transaction coordinator.
- **TCP/UDP ACK semantics**: the analogy for `acks=1` vs `acks=0`.
