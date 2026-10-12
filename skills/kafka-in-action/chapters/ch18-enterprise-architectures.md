# Chapter 18: Kafka's role in modern enterprise architectures

## Core Idea
Kafka is the backbone for decoupled, asynchronous data exchange *between* services and teams (data mesh, core-system liberation, big data transport, IIoT) — but it is not a relational database, not a request/response channel, not a file store, and not worth introducing for small single-team workloads. Use databases for service-internal state and Kafka for exchange.

## Frameworks Introduced
- **Data mesh (Zhamak Dehghani, 2019) on Kafka**: four principles — *domain ownership*, *data as a product*, *self-service data infrastructure*, *decentralized governance*.
  - When to use: a central data-engineering team is drowning in broken ETL pipelines because source teams change schemas (CRM fields renamed, ERP exports incomplete) without telling anyone, and the data lake has degraded into a *data swamp*.
  - How: (1) producing business units (data owners) publish agreed-upon, documented data products to the central Kafka platform, own the data life cycle, honor schema contracts, and decide who gets access via ACLs; (2) consuming units request access through the platform and keep their software compliant with schema contracts and data-protection rules; (3) the data platform team provides the domain-agnostic infrastructure, self-service processes, governance (access control, quotas, compliance), templates for producers/consumers, and helps with hard schema evolutions — becoming a center of excellence instead of a pipeline fire brigade.
  - Why it works: responsibility for data quality moves to the people with domain knowledge; Kafka adds near-real-time publishing/consumption, schema enforcement, governance integration (ch13), and cheap long retention via tiered storage. Failure mode: without self-service, every change still routes through the platform team and the bottleneck returns.
- **Liberating data from core systems**: decouple monolithic, DB-centric core systems (core banking, SAP inventory) from new agile services without overloading them or building costly custom integrations.
  - When to use: new customer-facing apps (mobile banking, online shop) need core-system data in near real time, but the core system must keep handling core processes and cannot take direct load.
  - How: CDC the core DB to Kafka with **Debezium** → never let other departments consume the raw, normalized, expert-only format → build new consolidated data structures. Options ranked: (a) core system emits an event stream natively (rare); (b) a Kafka Streams app joins raw topics into a consolidated format (many joins + state stores → complex to operate); (c) CDC into a *second* relational database (even a different DBMS), do the heavy joins in SQL, write results to **outbox tables**, CDC those to Kafka.
  - Why it works / failure mode: SQL is the right tool for massive joins; "a thousand-line join across 200 tables in Kafka Streams" is best avoided altogether.
- **Multiple-cluster decision**: default to **one centralized Kafka cluster**; split only for performance isolation (fraud detection vs. batch reporting), data security (HR/GDPR isolation), geographical distribution (data sovereignty, latency), or scalability/fault tolerance at very large scale (transactional vs. inventory vs. analytics). A raw-data cluster plus a processing cluster for teams is a legitimate pattern.

## Key Concepts
- **Data lake**: centralized repository of raw structured/unstructured data for flexible analysis.
- **Data swamp**: a data lake ingested without governance — incomplete metadata, poor docs, inconsistent ingestion — so data can't be found or trusted.
- **Data product**: a department's data, published with documentation, schema and quality guarantees, treated like any service product with customers.
- **Core system**: large, decades-old monolith on a central database that runs the company's essential processes and is hard to adapt.
- **Change data capture (CDC)**: streaming row changes from a database's log into Kafka (Debezium).
- **Outbox table/pattern**: write denormalized, consumer-ready records to a dedicated table in the same DB transaction, then CDC them to Kafka.
- **Tiered storage**: keep hot data on brokers and offload older segments to cheap storage, making long/historical retention in Kafka affordable.
- **MQTT**: lightweight device protocol; devices talk to an MQTT broker that forwards to Kafka.
- **Kafka proxy (Kroxylicious)**: intermediary layer enabling finer-grained control than Kafka's topic-level ACLs.
- **Denormalization**: flattening related rows (customers + orders) into one self-contained message so consumers don't join.

## Mental Models
- Think of relational databases as the store of **current state** and Kafka as the store of **history** from which each service rebuilds its own state.
- Use Kafka when data crosses team/service boundaries or volume is large; use a database (or PostgreSQL-as-a-log) when one team owns small data inside a monolith.
- Think of every Kafka message as a **self-contained event**: if it needs a join or a 50 MB attachment to be meaningful, the boundary is wrong.
- Think of the LinkedIn origin (every click into Hadoop) as the baseline use case: moving huge valuable data A→B, buffering spikes in the log so a downstream outage loses nothing — architecturally "almost mundane."

## Anti-patterns
- **Kafka as a relational database**: no transactional isolation, no strong consistency across partitions, only asynchronous access, and expensive joins — never query current state from it.
- **Simulated synchrony**: button click → produce → wait for another system to reply via Kafka; users wait indefinitely. Persist the action synchronously and confirm receipt instead.
- **Exchanging PDFs/files via Kafka**: messages are optimized for many small, machine-readable records (1 MB default limit). Send structured data or a pointer to object storage.
- **Huge SOAP envelopes as one message**: split semantically into one message per contained event.
- **Exposing normalized/raw CDC topics to regular consumers**: forces every consumer to re-join and couples them to core-system internals.
- **Writing denormalized Kafka data 1:1 into a relational DB**: normalize in the consumer first.
- **Kafka for tiny single-team apps**: adds operational complexity with no decoupling benefit.
- **Kafka as a substitute for architecture**: swapping messaging platforms without understanding requirements, NFRs, cost and scale fixes nothing — garbage in, garbage out; Kafka doesn't care what it transports.
- **Granting end users/consumer devices read rights on whole topics**: ACLs are topic-level; handle per-customer rights in backend logic or a proxy.

## Code Examples
No code in this chapter; the key architecture flows:
```text
# Core-system liberation (heavy joins)
Core DB --CDC(Debezium)--> raw topics --CDC--> 2nd relational DB (SQL joins)
       --> outbox tables --CDC--> consolidated topics --> new services

# Async UI instead of request/response over Kafka
UI --sync--> backend --> relational DB ("received!") --outbox+CDC--> Kafka
   --> 3rd system processes --> status event via Kafka --> backend notifies UI

# Large files
producer --> object storage (PDF) ; producer --> Kafka {"pdf": "<address>"}
consumer <-- Kafka notification --> fetch PDF from object storage

# IIoT ingestion
devices --MQTT--> MQTT broker --> Kafka --> connectors (JDBC, analytics) / Kafka Streams
```
- **What it demonstrates**: the four reference flows the authors recommend instead of misusing Kafka.

## Reference Tables
| Kafka is NOT… | Why | Do instead |
|---|---|---|
| A relational DB | No full ACID (lacks isolation, cross-partition strong consistency), async only, costly joins | DB for service-internal state; Kafka for exchange |
| A sync interface | Request/response over async log makes users wait | Sync write to DB, confirm, process async via outbox + CDC; or sync REST → backend produces → confirm on successful produce |
| A file exchange | Optimized for small machine-readable messages (≤1 MB default) | JSON payload + PDF generation service, or object storage + pointer message |
| For small apps | No coupling/volume benefit | PostgreSQL tables as a log; monolith is fine |
| A substitute for architecture | Same gaps persist after migration | Think, plan, then execute |

| Reason for multiple clusters | Example |
|---|---|
| Performance isolation | Low-latency fraud detection vs. batch historical reporting |
| Data security | HR cluster isolated for GDPR |
| Geographical distribution | North America vs. Europe for sovereignty/latency |
| Scalability & fault tolerance | Global retailer: transactional / inventory / analytics clusters |

IIoT use cases: predictive maintenance, factory automation, supply chain optimization, energy management, real-time production analytics.

**Small-app threshold**: < 1,000 messages/hour, no expected significant growth within a year, and only one team using the data → advise against Kafka (unless Kafka already exists in the enterprise architecture).

## Worked Example
**Asynchronous order submission.** A user clicks "submit" in a web UI. Wrong: backend produces to Kafka and blocks until a third system processes it and replies over Kafka — the user stares at a spinner. Right: the backend writes the action to its relational database synchronously and immediately tells the user "we received your input." An outbox row is CDC'd to Kafka; the third system consumes and processes it asynchronously, then emits a status event back via Kafka; the backend consumes it and updates the user on progress. If the backend has no database, the frontend may call the backend via synchronous REST, the backend produces to Kafka, and confirms "action triggered" once the produce succeeds.

## Key Takeaways
1. Run Kafka as the self-service platform of a data mesh: domains own and document data products, the platform team owns infrastructure and governance.
2. Liberate core-system data via CDC, but never expose raw normalized topics — publish consolidated structures, doing big joins in a secondary SQL database plus outbox.
3. Keep messages self-contained and denormalized; denormalize in the DB before producing, normalize in the consumer before writing to a DB.
4. Default to one central cluster; justify each extra cluster by isolation, security, geography or scale.
5. For IIoT, front untrusted/weak devices with MQTT, use tiered storage for affordable history (someone will ask for training data), and offer self-service access from day one.
6. Skip Kafka for < 1,000 msgs/hour single-team apps; use PostgreSQL as a log.

## Connects To
- **ch11**: Kafka Connect / Debezium CDC and JDBC connectors power core-system liberation and sinks.
- **ch12**: Kafka Streams joins and state stores — and why huge joins there are a trap.
- **ch13**: governance (schemas, ACLs, quotas) underpins decentralized data-mesh governance.
- **ch10**: retention and tiered storage for historical IIoT data.
- **ch16**: multi-cluster/geo-distribution trade-offs.
- **ch17**: comparison with other technologies — when another tool fits better.
- **Outbox Pattern / CDC**: the standard bridge from transactional DBs to Kafka.
- **Data mesh (Dehghani)**: the organizational model Kafka implements technically.
