# Chapter 1: Introduction to Apache Kafka

## Core Idea
Kafka is a persistent, distributed, horizontally scalable log that acts as the "central nervous system" for enterprise data: producers write events to topics, any number of consumers read (and re-read) them independently. Short orientation chapter. It names the ten architectural components and leaves the mechanics to later chapters, so this file is intentionally below the usual budget.

## Frameworks Introduced
- **Kafka as the central nervous system for data**: every significant business event (user interaction, state change, financial transaction) is stored as a record in a Kafka topic. Downstream systems subscribe to it in real time or replay it later.
  - When to use: many services need the same data streams; you want to stop building point-to-point integrations; or you are moving from batch (end-of-day) processing to real-time flows.
  - How: (1) identify the business events; (2) have the owning system publish each one to a topic; (3) let every interested system consume the topic independently; (4) rely on persistence so that new services can backfill from history and failed consumers resume where they left off.
  - Why it works: persistence separates writers from readers in time. Asynchronous communication means one service being down or under maintenance does not stop the others, and teams can evolve their services independently. Failure mode: treating Kafka as the whole solution. Even with a managed service, you still need in-house expertise in topic design, client design and monitoring.
- **Kafka's ten-component architecture (figure 1.2)**: messages/records → producers (choose the partition through a partitioner and send to the partition **leader**) → topics → partitions (replicated across brokers) → consumers → consumer groups → brokers → leaders → followers → coordination cluster (**KRaft**, previously a **ZooKeeper** ensemble).
  - When to use: as the mental map for reasoning about any Kafka data flow or failure.
  - How: follow a record from producer to partition leader, then replication to followers, then the consumer group member that owns the partition.
- **Legacy-to-modern bridge**: Kafka sits between batch-oriented legacy systems and the event-driven/microservices "new world", so legacy systems can feed real-time consumers with minimal changes. It is not strictly required for this; adapters and anti-corruption layers also work.

## Key Concepts
- **Event**: a structured record of a significant business occurrence, such as a transfer, a click or a sensor reading.
- **Message / record**: the payload, sent as a byte array and usually grouped into batches before transmission.
- **Topic**: a named stream that groups messages about one business subject. It is comparable to a database table.
- **Partition**: a subdivision of a topic. Partitions are the unit of parallelism and scaling, and the unit of replication across brokers.
- **Producer**: a client that writes messages. It uses a partitioner to choose the partition and sends to that partition's leader.
- **Consumer / consumer group**: a client that reads from one or more partitions and topics. Within a group, each partition is consumed by exactly one member. If a member fails, the others take over its partitions.
- **Broker**: a Kafka server. Brokers share replicas and leadership evenly, and another broker takes over if one fails.
- **Leader / follower**: the broker that handles reads and writes for a partition, and the brokers that hold its replicas. A follower is promoted if the leader fails.
- **KRaft**: Kafka's built-in Raft-based coordination. It replaces the external ZooKeeper ensemble and simplifies operations and scaling.

## Mental Models
- Think of Kafka as a **persistent distributed log**, not a queue. Data stays for hours, days or months and can be read many times.
- Think of a **topic as a table** and a **partition as a shard** that enables parallel reads and writes.
- Use Kafka when **asynchronous decoupling** is the goal. A producer never waits for, or knows about, its consumers.
- Kafka runs on **commodity hardware** and is built to tolerate the failure of individual components. It does not need fail-safe appliances.

## Anti-patterns
- **A tangled web of point-to-point integrations**: each new consumer adds coupling and fragility. Publish once to a topic instead.
- **Synchronous coupling between microservices**: maintenance or failure in one service spreads to the others. Exchange data asynchronously through Kafka.
- **Assuming a managed service removes the need for Kafka expertise**: operating the infrastructure is only one part of a streaming architecture.

## Code Examples
None. The chapter is conceptual (the first CLI commands are in ch02).

## Reference Tables
| Option | Examples | Authors' stance |
|---|---|---|
| Self-managed | Your own brokers (needs a JRE, since Kafka is written in Scala/Java) | Doable but easy to underestimate |
| Cloud-provider Kafka | Amazon MSK, Azure HDInsight | Viable |
| Kafka specialists | Confluent, Aiven | Recommended (good first-hand experience) |
| Kafka-compatible alternatives | Redpanda, WarpStream | Not enough experience to recommend |

Prerequisites for running Kafka: reliable servers (one broker each), a network with low latency and high bandwidth, deliberate topic and partition design, well-designed producer and consumer applications, and a monitoring and management strategy. Official clients exist for Java and Scala, and clients exist for Python and other languages.

## Worked Example
**Bank fund transfers.** The transfer application is the producer. It emits one message per transfer (source account, destination account, amount, timestamp) to the topic `bank-transfers`. The topic is split into partitions, for example by type or group of transfer, so the work can be processed in parallel. Each partition has a leader broker that handles reads and writes, plus followers that replicate it. If the leader fails, a follower takes over. KRaft coordinates the brokers and the metadata. A consumer group of account-update services divides the partitions, with each partition read by exactly one member, so accounts are updated in parallel, accurately and on time.

## Key Takeaways
1. Use Kafka as the shared event backbone instead of point-to-point integrations. Publish each business event once and let any system subscribe.
2. Persistence sets Kafka apart from classic messaging: consumers can resume after a failure, and new services can replay history.
3. Partitions are the scaling and replication unit. Consumer groups parallelize consumption, with one consumer per partition per group.
4. Kafka scales horizontally by adding brokers, and it reaches fault tolerance on commodity hardware through replication (leader/followers).
5. New clusters use KRaft for coordination instead of ZooKeeper.
6. A managed offering still requires in-house Kafka expertise. The authors recommend Confluent or Aiven.

## Connects To
- **ch02**: first hands-on use of topics, producers and consumers through the CLI.
- **ch03 / ch04**: messages, topics, partitions and the log in depth.
- **ch05**: replication, leaders and followers for reliability.
- **ch07**: the move from ZooKeeper to KRaft.
- **ch09**: consumer groups and partition assignment.
- **ch17 / ch18**: how Kafka compares with other messaging systems and where it fits in enterprise architectures.
- **Microservices / event-driven architecture**: Kafka supplies the asynchronous, decoupled communication they need.
- **Anti-corruption layer (DDD)**: an alternative way to bridge legacy and modern systems.
