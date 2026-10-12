# Chapter 17: Comparison with Other Technologies

## Core Idea
Pick technology by data role: keep "data on the inside" (service-private, strongly consistent, current state) in databases, and move "data on the outside" (service-agnostic, immutable, shared history) through Kafka. Kafka is a dumb pipe with smart endpoints, and is best seen as the core of a streaming platform, not a drop-in replacement for ESBs, REST or relational databases. A conceptual chapter: no code, so it runs shorter than the technical chapters.

## Frameworks Introduced
- **Data on the Inside vs. Data on the Outside (Pat Helland, CIDR 2005)**:
  - Inside: service-internal, stored in whatever format suits the service, tightly coupled to its code, needs synchronous reads/writes and strong consistency (read-your-writes so users don't retry).
  - Outside: crosses service boundaries, service-agnostic schema, ideally immutable (assume someone already consumed it), loosely coupled so inside and outside models evolve independently; the system carrying it must be resilient and fast, because if it fails, data exchange across the company stops.
  - When to use: deciding where a dataset lives and which technology carries it.
  - How: classify each dataset → inside goes to a database/specialised store; outside goes to Kafka; never expose inside data directly as the integration contract.
  - Why it works: isolates internal schema churn from consumers. Failure mode: a shared database or a REST API over internal data turns inside data into a de facto outside contract.

- **Smart pipes, dumb endpoints (ESB) vs. dumb pipe, smart endpoints (Kafka)**: ESBs route, transform formats, apply backpressure and enforce compliance centrally; Kafka only persists logs and lets producers/consumers decide what to read/write.
  - Kafka's four kinds of decoupling: **platform agnostic**, **data format agnostic** (JSON/Avro/Protobuf), **programming language agnostic** (Java, Python, Go...), **consumer agnostic** (the producer doesn't know whether consumers exist, are online, or are overloaded).

- **Pull + retention instead of push + delete-on-consume**: classic brokers delete messages once read, must track consumers, push to them, and use backpressure (slow down producers), which re-couples consumers to producers. Kafka retains data, so slow consumers fall behind and catch up, failed consumers restart and re-read, and new services can bootstrap from history.
  - Failure mode for classic systems: misconfiguration or slow consumers can overload the broker and cause large outages.

- **"What is?" vs. "What was?"**: relational databases answer "What is the current state of my world?"; Kafka answers "How did I arrive at the current state?" — the history, from which any service can rebuild the state it needs.

- **Turning the database inside out (Martin Kleppmann) / central nervous system for data**: databases are internally commit logs plus derived tables, indexes and materialized views. Make Kafka topics the shared log and let each service build its own local materialized views in the best-fit technology (Elasticsearch/OpenSearch for search, Redis for caching, PostgreSQL for ad hoc queries, or Kafka Streams/Flink state instead of a separate DB).

- **Streaming platform components**: Kafka (central log) + Kafka Connect (integrate existing systems) + stream processing (Kafka Streams/Apache Flink) + management/automation (topic creation, naming conventions, users and rights, credential distribution, schema and connector config), preferably Git-based with automated checks plus human review for production.

## Key Concepts
- **Data on the inside**: service-private data, tightly coupled to its service and requiring strong consistency.
- **Data on the outside**: immutable, service-agnostic data exchanged between services.
- **ESB (enterprise service bus)**: central integration middleware (SAP PI, Seeburger BIS, Microsoft BizTalk) handling routing, transformation, backpressure and compliance.
- **Backpressure**: messaging system asking producers to slow down for slow consumers, which re-couples them.
- **Temporal/physical coupling**: synchronous calls require the callee to be up and reachable right now; causes cascading (domino) failures.
- **Data at rest vs. data in motion**: REST transmits data only when requested; Kafka streams each event as it happens, triggering workflows.
- **Local materialized view**: a service-owned, format-specific projection built from a Kafka topic.
- **Streaming platform**: Kafka plus Connect, stream processing and automated governance, acting as the organisation's central nervous system for data.
- **Old World / New World**: classic messaging connects core systems (SAP ERP to production control); Kafka powers new products, with bridges between them.

## Mental Models
- Think of the database as the answer to "What is?" and Kafka as the answer to "What was?" — use both.
- Use REST/synchronous calls when you need an immediate answer (real-time gaming, trading, frontend↔backend); use Kafka when throughput, scalability and decoupling between services matter.
- Think of a shared multi-service database as a house of cards: the slightest change can bring it down, so nobody dares touch it.
- Use Kafka alongside IBM MQ or MQTT (IoT) rather than forcing a winner — coexistence is the norm.

## Anti-patterns
- **Microservices wired with synchronous REST for data exchange**: recreates monolith entanglement with distributed-system failure modes; one failing service dominoes through the chain.
- **Local caches fed by polling** to escape synchronous coupling: without change notifications there is no simple way to keep them fresh — subscribe to events instead.
- **Many services sharing one database without data ownership**: strong coupling, changes become impossible.
- **Replacing databases with Kafka**: Kafka has no central queryable store; ad hoc SQL is awkward (Flink SQL exists but is less mature), so export to data lakes/warehouses for analytics.
- **Centralised transformation teams**: ESB-style change processes take weeks or months; Kafka decentralises format mapping to teams.
- **Ignoring Kafka management/automation until multiple teams pile in**: naming, ACLs, credentials and schemas sprawl.
- **Adopting Kafka for a tiny system**: operating Kafka and maintaining two APIs (internal and external) may cost more than it returns for small teams.

## Code Examples
The chapter contains no code or configuration. The practical hook is that Kafka Connect links databases to Kafka "with relatively little configuration effort" (see ch11), and Kafka Streams/Flink stateful operations can replace a separate view database (see ch12).
- **What it demonstrates**: n/a — architectural chapter.

## Reference Tables

**Table 17.1 — Classic messaging systems vs. Kafka**

| Characteristic | Classic messaging systems | Kafka |
|---|---|---|
| Integration with legacy systems | Often connect legacy systems (e.g., SAP ERP) | Ideal for modern cloud-native apps and microservices |
| Message processing model | Typically synchronous, tight producer/consumer coupling | Asynchronous, temporal decoupling |
| Data persistence | Limited; messages may be deleted after delivery | Persists messages; long-term storage and replay |
| Scalability | Often hard to scale in large distributed environments | Horizontal scaling to massive volumes |
| Flexibility | Rigid; needs customisation/middleware for format conversion | Format-agnostic (JSON, Avro, ...) |
| Latency | Higher due to synchronous processing | Low latency, high throughput |
| Consumer independence | Consumers tightly coupled to producers | Consumers read at own pace, even after being offline |
| Use case flexibility | Established core business apps | Real-time streaming, EDA, new applications |

**Technology fit by question**

| Technology | Core question / strength | Coupling | Best for | Weakness |
|---|---|---|---|---|
| Relational DB | "What is?" — current state, powerful SQL | Tight to app | Data on the inside | Shared DB becomes a house of cards |
| HTTP-REST | Easy, ubiquitous, reusable API | Temporal + physical | Request/response, real-time answers | Cascading failures, caches hard to refresh |
| Classic MQ/ESB | Smart routing, transformation, backpressure | Producers↔consumers via backpressure; central team | Connecting core legacy systems | Delete-on-consume, no replay, slow central change |
| Kafka | "What was?" — history, data in motion | Loose | Data on the outside, event-driven microservices | No central queryable store; ops expertise; dual APIs |

## Worked Example
**From shared database to inside-out architecture.** Several services read and write one central database with no ownership boundaries; a schema change risks breaking everyone, so the system freezes. Refactor: each service keeps its own database for inside data. State changes are published as immutable events to Kafka topics (directly, or by Kafka Connect capturing the database). Consumers build local materialized views suited to their job: a search service indexes into OpenSearch, the high-traffic website keeps a Redis cache warm, a reporting service loads PostgreSQL for ad hoc queries, and another uses Kafka Streams state stores with no extra database. A new service bootstraps by replaying the topic history instead of asking the producer for a resend. The payoff grows with the number of interacting services; for a two-service system the operational overhead may not be worth it.

## Key Takeaways
1. Classify data as inside vs. outside first; use databases for inside data and Kafka for exchange.
2. Keep outside data immutable and service-agnostic so internal models can change freely.
3. Avoid synchronous REST chains for inter-service data; publish events and precompute views so requests are answered locally.
4. Rely on retention and consumer-pulled reads instead of backpressure; new consumers can replay history.
5. Don't treat Kafka as a database: export to lakes/warehouses for ad hoc analytics.
6. Treat Kafka as the core of a streaming platform: add Connect, stream processing and Git-based automation of topics, ACLs, credentials, schemas and connectors.
7. Weigh cost against scale: Kafka pays off with many teams/services, less so for small projects.

## Connects To
- **ch01**: why Kafka exists and the event-streaming motivation this chapter justifies.
- **ch04 / ch10**: log abstraction and retention enable replay vs. delete-on-consume.
- **ch11**: Kafka Connect integrates databases and legacy messaging.
- **ch12**: Kafka Streams/Flink stateful processing as materialized views.
- **ch13 / ch14**: governance, schemas, naming and Git-based topic/ACL processes.
- **ch18**: Kafka within enterprise architectures (data mesh, etc.).
- **Pat Helland, "Data on the Outside vs. Data on the Inside"**: the framing paper.
- **Martin Kleppmann, "Turning the database inside out"**: log-centric architecture.
- **CQRS / event sourcing**: local materialized views built from a shared event log.
