# Chapter 2: First steps with Kafka

## Core Idea
Three bundled scripts, `kafka-topics.sh`, `kafka-console-producer.sh` and `kafka-console-consumer.sh`, are enough to create a topic, write to it and read from it. Even this small demo shows the defining property of Kafka: many independent producers and consumers share one persistent topic that can be replayed. Short hands-on chapter, so this file is intentionally below the usual budget.

## Frameworks Introduced
- **The create → produce → consume CLI loop**: the minimal end-to-end check of a Kafka cluster.
  - When to use: smoke-testing a new cluster, learning, or debugging whether data actually reaches a topic.
  - How: (1) create the topic with `kafka-topics.sh --create`, setting `--partitions`, `--replication-factor` and `--bootstrap-server`; (2) produce with `kafka-console-producer.sh`, which sends one message per input line; (3) consume with `kafka-console-consumer.sh`, adding `--from-beginning` to see data that already exists.
  - Why it works / failure mode: `kafka-topics.sh --create` usually fails for one of two reasons: the brokers are not running or reachable, or the topic already exists. The console producer prints **no confirmation** on success. The console consumer starts at the **end** of the topic by default, so without `--from-beginning` it shows nothing old ("Processed a total of 0 messages").
- **Fan-out and fan-in on one topic**: several producers (for example, departments responsible for different product categories) write to the same topic. Several consumers (an inventory system, a sales-analysis tool) each read all of it independently, without coordinating with one another.
  - When to use: one data stream feeds several separate systems, or one stream has several sources.
  - How: point every producer and every consumer at the same `--topic`. A consumer that needs history starts with `--from-beginning`. A live view starts without it.

## Key Concepts
- **`kafka-topics.sh`**: the bundled script for topic administration (create, and more).
- **`kafka-console-producer.sh`**: reads stdin and sends each line as a message. Stop it with Ctrl-D (EOF).
- **`kafka-console-consumer.sh`**: prints messages from a topic and runs until you press Ctrl-C.
- **`--bootstrap-server`**: the address the client uses to reach the cluster. A local broker listens on `localhost:9092` by default.
- **`--from-beginning`**: makes the console consumer start at the earliest retained message instead of the end of the topic.
- **Topic naming convention**: lowercase components separated by dots, for example `products.prices.changelog`.
- **Default retention**: Kafka keeps data for **7 days** by default. It can be set to never delete.
- **Kafka GUIs**: Kafbat UI (open source) and Kadeck (proprietary) show topics, partitions, consumer groups and individual messages (key, value, timestamp).

## Mental Models
- Think of reading a topic as **non-destructive**. Unlike a classic queue, reading leaves the data in place, so any number of consumers can re-read it at any time.
- Use `--from-beginning` when you need **history**. Leave it off when you only want **live** updates.
- Think of Kafka as a **system-to-system** interface. Humans only touch production data as administrators in emergencies.

## Anti-patterns
- **Writing data or changing configuration through a GUI in production**: it leads to inconsistencies, weak error handling and poor scalability. Use GUIs only to view and monitor.
- **Expecting the console consumer to show old messages by default**: it starts at the end of the topic, so add `--from-beginning`.
- **Using `--partitions 1 --replication-factor 1` beyond a demo**: it gives no parallelism and no redundancy (see ch05 and ch06).
- **Native Windows `.bat` scripts**: prefer WSL. Confluent's distribution drops the `.sh` suffix.

## Code Examples
```bash
# Create the topic (demo values: 1 partition, no replication)
$ kafka-topics.sh \
    --create \
    --topic products.prices.changelog \
    --partitions 1 \
    --replication-factor 1 \
    --bootstrap-server localhost:9092
Created topic products.prices.changelog.

# Produce one message non-interactively (no confirmation is printed)
$ echo "coffee pads 10" | kafka-console-producer.sh \
    --topic products.prices.changelog \
    --bootstrap-server localhost:9092

# Read everything already in the topic (Ctrl-C to stop)
$ kafka-console-consumer.sh \
    --topic products.prices.changelog \
    --from-beginning \
    --bootstrap-server localhost:9092
coffee pads 10
Processed a total of 1 messages
```
- **What it demonstrates**: the full create/produce/consume loop, and that the console consumer needs `--from-beginning` to see existing data.

## Reference Tables
| Tool / flag | Purpose | Default / note |
|---|---|---|
| `kafka-topics.sh --create --topic <t>` | Create a topic | Errors if the topic exists or Kafka is unreachable |
| `--partitions N` | Partition count | 1 in the demo |
| `--replication-factor N` | Copies of each partition | 1 in the demo (no replication) |
| `--bootstrap-server host:port` | Cluster entry point | `localhost:9092` for a local cluster |
| `kafka-console-producer.sh` | One message per stdin line | Silent on success; Ctrl-D stops it |
| `kafka-console-consumer.sh` | Print messages | Starts at the end of the topic; Ctrl-C stops it |
| `--from-beginning` | Read from the oldest retained message | Off by default |
| Retention | How long data is kept | 7 days by default; can be unlimited |

## Worked Example
**Price changelog for an e-commerce platform** (this use case runs through the whole book, alongside user management, orders and payments). Product management records every price update in `products.prices.changelog`.
1. Create the topic and produce `coffee pads 10`. A plain consumer prints 0 messages. Adding `--from-beginning` shows `coffee pads 10`.
2. Consumer 1 (inventory management, live view, no flag) waits for new data. Producer 1 types `coffee pads 11`, `coffee pads 12` and `coffee pads 10`, and each line appears in Consumer 1 right away.
3. Consumer 2 (sales analysis) starts with `--from-beginning` and prints all four messages, so `coffee pads 10` appears twice, because it was also the first message.
4. Producer 2 (another department) sends `pillow 30` and `blanket 40`. Both consumers receive them in the order they were produced.
The result: several producers and several consumers share one topic, and the consumers never need to coordinate. The same model scales to tens of GB/s in real deployments.

## Key Takeaways
1. Use the bundled CLI scripts to smoke-test any cluster: create a topic, produce to it, then consume it with `--from-beginning`.
2. Name topics in lowercase with dot-separated parts that describe the domain, for example `products.prices.changelog`.
3. The console consumer starts at the end of the topic by default. Use `--from-beginning` for history and leave it off for live updates.
4. Any number of independent consumers can read the same topic, as often as they like. Retention (7 days by default) sets how far back they can go.
5. Several producers can write to the same topic at the same time.
6. Use Kafka GUIs (Kafbat UI, Kadeck) for inspection and troubleshooting, never for producing data or changing config in production.

## Connects To
- **ch01**: the components (topic, producer, consumer, broker) exercised here.
- **ch03**: message structure (key, value, timestamp) and how topics are organized.
- **ch05 / ch06**: why the demo's single partition and replication factor of 1 are not suitable for production.
- **ch09**: consumer offsets and why the default start position is the end of the topic.
- **ch10**: retention settings (7-day default, unlimited retention, compaction).
- **ch15**: monitoring, where GUIs complement metrics.
- **ch19**: setting up the multi-broker test environment used in the examples.
