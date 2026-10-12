# Chapter 12: Stream Processing

## Core Idea
Once data is in Kafka, you can analyze it continuously, one event at a time, instead of waiting for a nightly batch. Do it with an established library (Kafka Streams, Flink, Faust, Goka), not hand-rolled consumers and producers. Get comfortable with eventually consistent intermediate results, streams vs tables, key-based state, time windows, and partition-based parallelism.

## Frameworks Introduced
- **Batch vs event-at-a-time processing**: batch processes large data sets at fixed times (e.g., a 4 a.m. cron job) and produces final results. Stream processing handles each event almost immediately, but every result is only an intermediate state and is **eventually consistent**.
  - When to use: use batch for recurring reports tied to a deadline that need a final number (monthly revenue, inventory). Batch on cloud spot instances overnight is also cheap. Use streaming when the business has to react now (price errors, stock-outs, fraud).
  - How: in batch setups Kafka acts only as the data exchange layer. In streaming setups the processor reads topics, keeps state, and writes results back to Kafka. Consumers or Kafka Connect then deliver those results to other systems.
  - Why it works / failure mode: streaming removes hours of latency. The cost is that you must assume any result can still change. Treating a streaming output as final is a design error.
- **Three programming styles for stream processors**: *imperative* (step-by-step "if this, then that", as with plain consumers and producers), *functional* (chained reusable processors such as `filter`/`map`/`aggregate`, used by Kafka Streams and the Flink DataStream API), and *declarative* (streaming SQL, as in Flink SQL).
- **Processor topology**: a directed graph of source processors (`builder.stream()` / `builder.table()`), stateless processors (`filter`, `map`, `mapValues`, `merge`, `split`), stateful processors (`groupByKey().count()`, `aggregate`, joins), and sinks (`to()`). The graph helps with debugging and lets you understand the logic without reading the code.
- **Stream–table duality (KStream/KTable, DataStream/Table)**: a stream is an unbounded sequence of changes. A table is the latest value per key, derived from that stream. Stream-processing tables are partitioned key-value stores, usually RocksDB, backed by a compacted **changelog topic**. They are not relational tables.
  - How: `builder.table("topic")` reads the topic from the beginning and upserts each key. Go from table to stream with `toStream()`. Go from stream to table with `toTable()`, `count()` or `aggregate()`. Use compacted topics for master data.
  - Why it works / failure mode: Debezium turns a table into a stream, and aggregating a stream gives you a table again. Every table means local state plus a changelog topic, so the cost is storage and restore time.
- **Aggregation = initializer + adder**: the *initializer* is the neutral element used for a key with no previous state (0 for count and sum, 1 for multiplication, an empty list for collections). The *adder* takes `(key, value, agg)` and returns the new state. Aggregations are always per key.
  - How (Kafka Streams): you cannot aggregate a KStream directly. First call `groupByKey()`, or `groupBy((k,v) -> newKey)` if you need a new key. `groupBy` creates a repartition topic.
- **Streaming joins as lookups**: you cannot cross-join infinite streams, so a join looks up the current message's key in a state store. Both inputs must be **co-partitioned**: the same number of partitions and the same key.
  - Stream–table: only a new stream record triggers the join. Table updates do not re-emit results. This is the standard way to enrich events with master data.
  - Table–table: changes on either side trigger the join (a primary-key join).
  - Stream–stream: a general version is impossible. You need a time window (`JoinWindows`), and each record joins every record with the same key on the other side within that window.
- **Time windows**: Tumbling, Sliding, Hopping and Session windows (see Reference Tables), plus a *grace period* (lateness) for out-of-order records.
- **Kafka Streams scaling model**: one **task** per input partition. A task is the smallest unit of work. Tasks are spread across instances and threads using the Kafka rebalance protocol, which is the same mechanism consumer groups and Connect use. Each task has its own state store. Changing a key before a stateful operation adds a `-repartition` topic and splits the topology into **subtopologies**.

## Key Concepts
- **Stream processor**: a component that applies one transformation to messages in a stream. Processors are chained into topologies.
- **Stateless vs stateful processor**: stateless processors (`filter`, `map`, `mapValues`, `merge`, `split`) look at one message in isolation. Stateful processors (`count`, `aggregate`, joins, windows) need a state store.
- **KStream / KTable**: the Kafka Streams names for a data stream and a key-value table. Flink calls them DataStream and Table.
- **State store**: a local key-value store, usually RocksDB, that holds a task's intermediate state. Kafka Streams creates one per stateful processor per task.
- **Changelog topic**: an internal, usually compacted topic that records every state-store change, so the store can be rebuilt after a crash.
- **Repartition topic**: an internal topic ending in `-repartition`. Re-keyed data is written to it and read back, so that each key reaches the right task before a join or aggregation.
- **Subtopology**: one piece of a topology that is split at a repartition topic. One subtopology writes to `-repartition` and the next one reads from it.
- **Co-partitioning**: both join inputs have the same partition count and the same key, so matching keys land in the same task.
- **Event time / CreateTime / LogAppendTime / stream time**: when the event happened (a payload field), when the producer called `send()`, when the broker appended the record, and when the processor handles it.
- **Grace period (lateness)**: how long a window stays open for late records. Without one, out-of-order records are silently dropped.
- **Headless mode (Flink SQL)**: SQL queries deployed to run continuously, with results written back to Kafka or to another sink.

## Mental Models
- Think of a **table as a materialized aggregation of a stream**, and of a stream as the changelog of a table. Pick the view that fits each topic: transactional data (price changes) is a stream, and master data (customers, products) is a table on a compacted topic.
- Think of a **streaming join as a lookup, not a set operation**. Ask which side's change triggers the join. That answer determines whether a stream–table, table–table or windowed stream–stream join is correct.
- Think of a **streaming SQL query as a subscription**. It never returns and keeps emitting changes, so its performance cost is ongoing. Review queries before you deploy them.
- Use **parallelism = number of input partitions**. Adding instances or threads beyond the task count gives you no extra throughput.

## Anti-patterns
- **Building stream processing yourself with raw consumers and producers**: you end up re-implementing state, fault tolerance, windowing and rebalancing badly. Use Kafka Streams, Flink, Faust or Goka.
- **Using `map()` or `selectKey()` when `mapValues()` would do**: any key change marks the stream for repartitioning. That adds an internal topic and roughly doubles network and storage traffic before the next stateful operation.
- **Chains of `filter()` calls to route records**: it is easy to leave gaps or produce overlapping (duplicate) branches. `split()` evaluates its branches from top to bottom and has a `defaultBranch`.
- **Overwriting the Kafka record timestamp manually to mean "event time"**: add an explicit event-time field to the payload instead, and tell the framework to use it through a `TimestampExtractor`.
- **Joining topics that are not co-partitioned**: the join silently misses matches. Re-key one side first, and accept the repartition cost.
- **Expecting a stream–table join to fire when master data changes**: it fires only on new stream records. Use a table–table join if updates on both sides should produce output.
- **Running streaming SQL in production without reviewing it**: the query plan and its state cost are often not obvious.

## Code Examples
```java
// split(): routes each record to the first branch whose predicate matches (top to bottom)
prices.split()
    .branch((key, value) -> value.price < 10,
        Branched.withConsumer((stream) -> stream.to("prices-cheap")))
    .branch((key, value) -> value.price < 100,
        Branched.withConsumer((stream) -> stream.to("prices-midrange")))
    .defaultBranch(Branched.withConsumer(
        (stream) -> stream.to("prices-expensive")));
```
- **What it demonstrates**: routing without gaps or duplicates. The second branch does not need a `>= 10` check because the first branch already took those records.

```java
// Topology with two sources, merge, sink, plus a stateful count
salesDataNorth = builder.stream("salesData.north");
salesDataSouth = builder.stream("salesData.south");
salesData_aggregated = salesDataNorth.merge(salesDataSouth);
salesData_aggregated.to("salesData.aggregated");
salesData_aggregated.groupByKey()
    .count()                 // result is a KTable
    .toStream()              // convert back before writing
    .to("salesData.count");
```
- **What it demonstrates**: `merge` behaves like SQL `UNION`, one stream can feed two branches, and `count()` returns a KTable that you must convert with `toStream()` before calling `to()`.

```java
// Stream-table join (enrichment) and windowed stream-stream join
KStream salesData = builder.stream("salesData");
KTable masterData = builder.table("products");
ValueJoiner enricher = (sale, product) -> {
    sale.manufacturer = product.manufacturer;
    return sale;
};
KStream salesData_enriched = salesData.join(masterData, enricher);

JoinWindows joinWindow = JoinWindows.ofTimeDifferenceWithNoGrace(Duration.ofMinutes(1));
KStream correlated = priceChanges.join(salesData, joiner, joinWindow);
```
- **What it demonstrates**: a stream–table join needs no window. A stream–stream join must be bounded by `JoinWindows`.

```sql
-- Flink SQL: a "table" is only a connector definition; data stays in Kafka
CREATE TABLE productprices (
  product_id INT, product_name STRING, price FLOAT, oldPrice FLOAT
) WITH (
  'connector' = 'kafka',
  'topic' = 'products.prices.changelog',
  'properties.bootstrap.servers' = 'localhost:9092',
  'format' = 'json',
  'key.format' = 'json',
  'key.fields' = 'product_id',
  'value.fields-include' = 'EXCEPT_KEY'
);
SELECT product_id, COUNT(*) AS num_price_changes FROM productprices GROUP BY product_id;
```
- **What it demonstrates**: Flink SQL has no separate stream type, only tables bound to topics. The record key is declared through `key.fields`. The query emits continuous updates and never returns a single final result.

## Reference Tables

**Table 12.1: Aggregations as initializer + adder**

| Aggregation | Aggregate type | Initial state | Adder | Example (input → state) |
|---|---|---|---|---|
| `count()` | Number | 0 | `(agg, value) -> agg + 1` | (K1,2)→K1:1; (K2,1)→K2:1; (K2,2)→K2:2 |
| `sum()` | Number | 0 | `(agg, value) -> agg + value` | (K1,2)→K1:2; (K2,1)→K2:1; (K2,2)→K2:3 |
| `toTable()` | Value type | null | `(agg, value) -> value` | (K1,2)→K1:2; (K2,1)→K2:1; (K2,2)→K2:2 |
| `average()` | Number | (sum, count, avg) | `(agg, value) -> (agg.sum+value, agg.count+1, newSum/newCount)` | (K2,1)→(1,1,1); (K2,2)→(3,2,1.5) |

For `average()`, add a `mapValues()` over the resulting table so it exposes only the average and not the internal sum and count.

**Table 12.2: Which side triggers a streaming join**

| Left | Right | Join executes on changes to |
|---|---|---|
| Table | Table | Both left and right |
| Data stream | Table | Data stream only |
| Data stream | Data stream (windowed) | Both left and right |

**Table 12.3: Times in streaming**

| Time | Set by | Meaning | How it is configured |
|---|---|---|---|
| Event time | Your code | When the event actually happened | A field in the payload |
| Create time | Producer | When `send()` was called | Default: `log.message.timestamp.type=CreateTime` |
| Log append time | Broker | When the broker wrote the record to the log | `LogAppendTime` via broker `log.message.timestamp.type` or topic `message.timestamp.type`. Timestamps then increase within a partition. |
| Stream time | Stream processor | When the record is processed | Chosen through a `TimestampExtractor` |

**Window types**

| Window | Parameters | Overlap | Use for |
|---|---|---|---|
| Tumbling | length | None. Each record falls in exactly one window. | Billing, periodic consumption readings |
| Sliding | length | Continuous | "X over the last Y minutes" (count of card transactions in the last 5 min). Better than hopping for closely spaced intervals. |
| Hopping | length + advance (e.g., 7 days / 1 day) | Yes, opened at fixed intervals even when no data arrives | Periodic reports over overlapping periods (daily 7-day average revenue) |
| Session | inactivity gap | None. A window closes after a gap with no records. | User-session analysis |

**Kafka Streams scaling knobs**

| Setting | Meaning |
|---|---|
| `num.stream.threads` (the book calls it `num.threads`) | Threads per instance. Tasks are spread across threads, and each thread has its own consumer and producer. |
| `num.standby.replicas` (≥1) | Keeps a warm copy of each state store on another instance, so failover does not need to rebuild the store from the changelog topic. |

## Worked Example
**Fraud detection on login attempts.** All authentication attempts go to `auth_requests`, keyed by user ID. A Fraud Detection Service counts attempts per user in 1-minute tumbling windows. When a user crosses the threshold, it writes a record to `possible_frauds`, and a downstream system then requires a second factor such as a push notification or phone call.

```java
KStream<String, String> authRequests = builder.stream("auth_requests");
KTable<Windowed<String>, Long> windowedCounts = authRequests
    .groupByKey()
    .windowedBy(TimeWindows.ofSizeWithNoGrace(Duration.ofMinutes(1)))
    .count();
KStream<String, Long> possibleFrauds = windowedCounts
    .toStream()
    .filter((windowedKey, count) -> count > 3)
    .map((windowedKey, count) -> KeyValue.pair(windowedKey.key(), count)); // unwrap Windowed key
possibleFrauds.to("possible_frauds");
```
Flink SQL version: `INSERT INTO possible_frauds SELECT user_id, COUNT(*) AS request_count, TUMBLE_START(request_time, INTERVAL '1' MINUTE) AS window_start, TUMBLE_END(...) AS window_end FROM auth_requests GROUP BY user_id, TUMBLE(request_time, INTERVAL '1' MINUTE) HAVING COUNT(*) > 3;`

The prose says "at least three attempts", but both code versions use `> 3`. Pick `>=` or `>` deliberately. `ofSizeWithNoGrace` drops late records, so add a grace period if producers can deliver late.

A second example is notifications. `user-devices` is aggregated with initializer `List.of()` and an adder that inserts active devices and removes inactive ones. The result is a `KTable<userId, List<DeviceInfo>>`, which is stream–table joined with `notifications` (key = user ID) and written to `device-notifications`. In Flink SQL, the same logic is a view built with `LISTAGG(... JSON_OBJECT(...)) GROUP BY user_id` and joined on `user_id`.

**Scaling walkthrough.** A topic with 12 partitions gives 12 tasks. One instance runs all 12, and six instances run about 2 each. With 9 tasks spread over instance A (2 threads) and instance B (3 threads), most threads get 2 tasks and one thread gets 1. If an instance dies, the rebalance protocol moves its tasks elsewhere, and their state stores are restored from the changelog topics, unless standby replicas exist. A `selectKey()` followed by `count()` produces two subtopologies joined by a `-repartition` topic.

## Key Takeaways
1. Choose Kafka Streams when you want a Kafka-native Java library: Kafka coordinates the instances and Spring Boot supports it. Choose Flink when you need richer features, a Python API or Flink SQL, and you can run its separate cluster and coordination layer (there is a Kubernetes operator). For Python consider Faust, and for Go consider Goka.
2. Prefer `mapValues()` to `map()`/`selectKey()`, and prefer `split()` to multiple `filter()` calls. Changing the key causes repartitioning, which costs extra network traffic, storage and an internal topic.
3. Model master data as tables on compacted topics, and model transactional data as streams. Enrich streams with stream–table joins, and make sure the inputs are co-partitioned first.
4. Every stateful operation creates RocksDB state and a changelog topic per task. Set `num.standby.replicas>=1` if fast failover matters.
5. Decide explicitly which time a window uses. Record event time in the payload instead of overwriting the record timestamp, and configure a grace period for late records.
6. Parallelism is capped by the partition count. Plan partitions for your downstream stream-processing needs, not only for the producers.
7. Streaming results are intermediate and eventually consistent. Write them back to Kafka and let consumers or Kafka Connect deliver them onward.

## Connects To
- **ch02**: the `products.prices.changelog` topic introduced there is the running example in this chapter.
- **ch04**: partitions, keys and ordering guarantees drive tasks, co-partitioning and repartitioning.
- **ch09**: Kafka Streams instances balance tasks with the consumer-group rebalance protocol.
- **ch10**: changelog topics and master-data topics depend on log compaction.
- **ch11**: Debezium CDC turns database tables into streams (stream–table duality), and Connect delivers stream-processing results to other systems.
- **ch13**: schemas and data contracts keep processor inputs and outputs compatible.
- **ch17**: the comparison of Kafka with batch and big-data systems.
- **Apache Flink / Flink SQL, RocksDB**: an external engine and the default state-store backend.
- **Lambda/Kappa architectures, CQRS**: the stream–table duality and materialized views are the same idea.
