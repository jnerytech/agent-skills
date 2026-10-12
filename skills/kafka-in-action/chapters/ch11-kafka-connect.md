# Chapter 11: Integrating external systems with Kafka Connect

## Core Idea
Don't hand-write producers and consumers to move data between Kafka and databases, files, object stores or other messaging systems. Use Kafka Connect. It is a scalable, fault-tolerant framework that models each external source or sink as a set of *partitioned streams* with offsets. Run it in Distributed Mode, manage connectors only through its REST API (driven by CI/CD), and use CDC (Debezium) rather than JDBC polling when you need every change.

## Frameworks Introduced
- **Partitioned-stream model**: any external system that can be split into independent streams (DB tables, files) with a resumable position (sequential ID, timestamp, line or byte position) fits Kafka Connect. This mirrors Kafka's own partitions and offsets.
  - When to use: deciding whether a connector fits, or whether to write your own connector instead of custom clients.
  - How: (1) find the unit that must not be split (one table, one file) because splitting it breaks ordering; (2) find a monotonic position to store as the source offset; (3) let `tasks.max` spread those streams over tasks.
  - Why it works / failure mode: offsets let a restarted connector resume without re-reading. The position must only ever increase, or new data gets missed. If no connector exists but the data maps to partitioned streams, write a Connect connector instead of rebuilding this logic with producers and consumers.
- **Distributed Mode cluster**: every worker that shares a `group.id` forms one Connect cluster. Workers coordinate through the Kafka rebalance protocol (ch09) and keep their state in three internal topics: config, offset and status.
  - When to use: always in production. Use **Standalone Mode** only on dev machines or when the connector needs local files. Standalone keeps no offsets or config in Kafka and can't scale.
  - How: write `worker.properties`, run `connect-distributed.sh worker.properties`, then POST connector JSON to port 8083. To scale, start more workers with the same `group.id`. If a worker crashes or joins, its tasks are rebalanced.
  - Why it works / failure mode: internal topics want RF 3, so the cluster won't start with fewer than 3 brokers unless you lower `config.storage.replication.factor` (and the equivalents for the other two topics).
- **Two configuration layers**: the *worker config* (properties file, applies to all connectors on that worker) and the *connector config* (JSON sent over REST, stored in the config topic). Connector configs may override client settings through `producer.override.*` or `consumer.override.*`, but only if `connector.client.config.override.policy` allows it.
- **Error-handling ladder**: (1) retries for transient faults: `errors.retry.timeout` (default 0, meaning no retries) and `errors.retry.delay.max.ms`; (2) tolerance: `errors.tolerance=all` skips bad records, where the default `none` fails the connector; (3) visibility: `errors.log.enable=true`, plus `errors.log.include.messages` (off by default because of PII); (4) for sinks only, a DLQ via `errors.deadletterqueue.topic.name`.
  - When to use: on every production connector. Set up an alert whenever records are being skipped.
  - Failure mode: once a connector or task has FAILED, nothing happens until you restart it manually.
- **Single Message Transformations (SMTs)**: a chain of per-record transforms declared under `transforms`. They run in list order. In a source connector they run after the connector and before the converter; in a sink connector, after the converter and before the connector.
  - When to use: light changes such as renaming or dropping fields, masking, or moving a field into the key. Use Kafka Streams (ch12) for anything ETL-like.

## Key Concepts
- **Source connector / sink connector**: a source reads an external system and produces to Kafka; a sink consumes from Kafka and writes out. MirrorMaker is the exception, copying Kafka to Kafka.
- **Worker**: one Connect JVM process in a cluster. It runs connectors and their tasks.
- **Task**: the unit of parallel work, such as a subset of tables or partitions. The real task count is capped by the connector and the data (source tables, topic partitions), whatever `tasks.max` says.
- **`group.id` (worker)**: the *Connect cluster identity*, not a consumer group. The authors say `connect.id` would have been a better name.
- **Internal topics**: `config.storage.topic` (connector configs), `offset.storage.topic` (source offsets such as the last DB ID) and `status.storage.topic` (connector and task state).
- **Converter**: serializes between Connect's internal record format and bytes in Kafka. Options include `StringConverter`, `JsonConverter`, `AvroConverter`, Protobuf, JSON Schema and ByteArray. Avro, Protobuf and JSON Schema need a Schema Registry.
- **Sink consumer group**: by default `connect-<connector name>`. You can override it with `consumer.group.id` if the worker allows overrides.
- **Config providers**: externalize secrets and variables (`config.providers`, `config.providers.<name>.class`, `config.providers.<name>.param.<param>`).
- **CDC (change data capture)**: captures *changes* rather than snapshots of data, for example by reading the database transaction log (PostgreSQL WAL with `wal_level=logical`).
- **Debezium envelope**: each change message carries `before`, `after`, `source`, `op` (`c` create, `u` update, `d` delete, `r` snapshot read), `ts_ms` and `transaction`.

## Mental Models
- Think of a Connect cluster as a consumer group of workers: tasks are the partitions that get rebalanced.
- Think of a JDBC source in `incrementing` mode as running `SELECT * FROM t WHERE id > <last offset>`. It sees inserts only. It never sees updates, deletes or reused IDs.
- Use JDBC polling when the table is append-only or "eventually most changes" is good enough. Use Debezium CDC when every insert, update and delete must reach Kafka.
- Treat the connector `name` as the only metadata you get. It appears in REST paths and in the sink group ID, so give it a real naming scheme.

## Anti-patterns
- **Hand-rolled producer and consumer integration code**: it takes a long time to write, breaks easily, scales badly and misses edge cases that Connect already handles.
- **FileStreamSource or FileStreamSink in production**: these are proof-of-concept connectors with poor error handling, and they only see appended lines, not edits. Use FilePulse instead.
- **Relying on worker-default converters**: set `key.converter` and `value.converter` explicitly in each connector config. Use JSON or Avro as the worker default value converter, not String.
- **`JsonConverter` with `schemas.enable=true` at scale**: every message embeds its schema, which makes messages very verbose. Use a Schema Registry converter such as `io.confluent.connect.avro.AvroConverter`.
- **Humans calling the REST API in production**: the API has no authn/authz, and Basic auth gives everyone full power. Let CI/CD own all connector changes.
- **Timestamp mode as a completeness guarantee**: rows that share a timestamp can be skipped, and the chance shrinks with timestamp precision but never reaches zero. `bulk` mode is complete but reloads the whole table every poll, which the authors strongly advise against.
- **Overusing SMTs**: Connect is not an ETL tool.
- **`request.timeout.ms` set too low**: on a slow network or loaded brokers, requests are retried over and over and may never succeed, so the connector stalls.
- **Leaving `topic.creation.enable` on when topics are managed as IaC**: Connect will create topics on its own. Disable it if you want full control.

## Code Examples
```properties
# worker.properties (Distributed Mode)
bootstrap.servers=localhost:9092
group.id=connect
config.storage.topic=connect-config
offset.storage.topic=connect-offset
status.storage.topic=connect-status
key.converter=org.apache.kafka.connect.storage.StringConverter
value.converter=org.apache.kafka.connect.storage.StringConverter
plugin.path=<PATH-TO-YOUR-USER-DIRECTORY>/kafka/libs/
```
```bash
$ connect-distributed.sh worker.properties
$ curl -X POST -H "Content-Type: application/json" \
    --data @source-connector.json http://localhost:8083/connectors
$ curl http://localhost:8083/connectors/customers-source/status | jq
$ curl -X PUT  http://localhost:8083/connectors/customers-source/pause
$ curl -X PUT  http://localhost:8083/connectors/customers-source/resume
$ curl -X POST "http://localhost:8083/connectors/customers-source/restart?includeTasks=true&onlyFailed=true"
```
- **What it demonstrates**: bootstrapping a Distributed-Mode worker and the core connector lifecycle (create, inspect, pause, resume, restart failed tasks).

```json
"transforms": "moveKey,extractKey",
"transforms.moveKey.type": "org.apache.kafka.connect.transforms.ValueToKey",
"transforms.moveKey.fields": "product_id",
"transforms.extractKey.type": "org.apache.kafka.connect.transforms.ExtractField$Key",
"transforms.extractKey.field": "product_id"
```
- **What it demonstrates**: SMT chaining. `ValueToKey` alone produces the struct key `{product_id: ...}`; adding `ExtractField$Key` turns it into a plain scalar key. Other built-ins: `ReplaceField$Value` (`exclude`, `renames: "foo:bar"`) and `MaskField` (sets fields to null).

## Reference Tables
**Worker configuration**
| Key | Default | Meaning / guidance |
|---|---|---|
| `group.id` | — | Connect cluster identity |
| `config/offset/status.storage.topic` | — | Internal state topics; RF 3 recommended (`*.replication.factor` to lower) |
| `key.converter` / `value.converter` | — | Still required on the worker even if connectors override them |
| `plugin.path` | — | Comma-separated dirs for connectors, converters and SMTs |
| `topic.creation.enable` | true | Auto-create topics; disable for IaC-managed topics |
| `exactly.once.source.support` | disabled | EOS for source connectors; on an existing cluster go `preparing` → `enabled` |
| `session.timeout.ms` | — | Lower means faster failover but more needless rebalances |
| `request.timeout.ms` | — | Too low causes endless retries on slow or busy brokers |
| `offset.flush.interval.ms` / `offset.flush.timeout.ms` | — | Many small msgs: flush more often or raise the timeout (symptom: "Failed to flush, timed out while waiting for producer to flush outstanding x messages") |
| `connector.client.config.override.policy` | — | Allows `producer.override.*` / `consumer.override.*` in connector configs |
| `config.providers` | — | Variable and secret substitution |
| `listeners` | HTTP :8083 | REST API host, port and protocol |

**Connector configuration**
| Key | Default | Meaning |
|---|---|---|
| `name` | — | Only metadata; appears in REST paths |
| `connector.class` | — | e.g. `JdbcSourceConnector`, `io.debezium.connector.postgresql.PostgresConnector`, `MirrorSourceConnector` |
| `tasks.max` | — | Upper bound on parallelism |
| `topics` / `topic.regex` | — | Sink input topics (regex needs topic naming conventions) |
| `consumer.group.id` | `connect-<name>` | Sink group override |
| `exactly.once.support` | `requested` | `required` makes the connector fail if the worker lacks EOS |
| `errors.tolerance` | `none` | `all` skips bad records |
| `errors.log.enable` | false | Log tolerated errors too |
| `errors.log.include.messages` | false | Include the record (PII risk) |
| `errors.deadletterqueue.topic.name` | — | Sink-only DLQ |
| `errors.retry.timeout` | 0 (no retry) | Max total retry time (ms) |
| `errors.retry.delay.max.ms` | — | Max delay between retries |
| JDBC `connection.attempts` / `connection.backoff.ms` | 3 / 10 s (~30 s total) | Raise these to survive DB maintenance |
| JDBC sink `max.retries` / `retry.backoff.ms` | 10 / 3 s | Retries on locked rows and similar |

**REST API**
| Call | Purpose |
|---|---|
| `GET /` | Version, commit, Kafka cluster ID |
| `GET /connector-plugins` | Verify plugins loaded |
| `GET /connectors[?expand=info\|status]` | List connectors (optionally with details) |
| `GET /connectors/<c>` · `/config` · `/status` · `/tasks` · `/tasks/<id>/status` | Inspect a connector |
| `GET /connectors/<c>/topics` · `PUT …/topics/reset` | Topics actually used; reset has no operational effect |
| `POST /connectors` | Create (error if the name already exists) |
| `PUT /connectors/<c>/config` | Update config (body = config only) |
| `PUT …/pause` · `PUT …/resume` | Pause during third-party maintenance |
| `POST …/restart?includeTasks=true&onlyFailed=true` · `POST …/tasks/<id>/restart` | Recover failed connectors or tasks |
| `DELETE /connectors/<c>` | 204 if deleted, 404 if it doesn't exist |

**JDBC source `mode`**
| Mode | Detects | Gap |
|---|---|---|
| `incrementing` (`incrementing.column.name`) | New rows | Updates, deletes, reused or smaller IDs |
| `timestamp` (`timestamp.column.name`) | Inserts and updates | Deletes; same-timestamp rows can be missed; needs a timestamp column |
| `timestamp+incrementing` | Both | Columns must increase monotonically |
| `bulk` | Everything | Full reload every poll (strongly discouraged) |

## Worked Example
**Customers table: JDBC polling vs Debezium CDC.** SQLite `customers` holds rows 1 and 2. A `JdbcSourceConnector` runs with `table.whitelist=customers`, `topic.prefix=sqlite_`, `mode=incrementing`, `incrementing.column.name=id`, `JsonConverter` with `schemas.enable=false` and `table.types=TABLE` set explicitly. Both rows land in `sqlite_customers` as flat JSON. The topic prefix also stops the connector from writing into an existing topic that happens to share a table name. Inserting id 3 (with a wrong birthdate) shows up within seconds. The `UPDATE ... SET birthdate=... WHERE id=3` correction never arrives, because the connector only runs `SELECT * FROM customers WHERE id > 3`.

Repeat on PostgreSQL:
- Set `wal_level = logical` and restart.
- Create the role `customers_user REPLICATION LOGIN` and make it owner of the `customers` DB.
- Register `PostgresConnector` with `plugin.name=pgoutput`, `publication.autocreate.mode=filtered`, `topic.prefix=debezium` and `table.include.list=public.customers`.

The topic is `debezium.public.customers`. The initial rows arrive with `op:"r"` (snapshot). The insert arrives as `op:"c"` and the birthdate fix as `op:"u"`. The update is captured this time because Debezium reads the transaction log instead of polling. To get only the row state rather than the full envelope, add the `ExtractNewRecordState` SMT.

## Key Takeaways
1. Use an existing connector first. Write a custom Connect connector, not raw clients, when the data maps to partitioned streams.
2. Run Distributed Mode with RF-3 internal topics, and scale by adding workers with the same `group.id`. Remember that `tasks.max` can't go beyond the data's natural parallelism.
3. Set converters explicitly per connector, and prefer Avro or a Schema Registry over schema-embedded JSON.
4. Lock down the REST API: no human access in production, CI/CD only. Pause connectors during third-party maintenance.
5. Configure errors on purpose: add retries (default 0), set `errors.tolerance=all` only together with `errors.log.enable=true` and alerting, and give sinks a DLQ. Raise JDBC connection retries above the default ~30 s.
6. JDBC polling misses updates and deletes, and in timestamp mode it can miss same-timestamp rows. Use Debezium CDC (with `ExtractNewRecordState`) when every change matters.
7. Keep SMTs to small per-record edits. Move real transformation to Kafka Streams.

## Connects To
- **ch05**: exactly-once semantics behind `exactly.once.source.support` and `exactly.once.support`.
- **ch09**: Connect workers use the same rebalance protocol as consumer groups, and sinks are consumer groups (`connect-<name>`).
- **ch12**: Kafka Streams is where transformations go once they outgrow SMTs.
- **ch13**: Schema Registry for Avro, Protobuf and JSON Schema converters; authn/authz for Connect; config providers for secrets.
- **ch15**: monitoring Connect connectors and tasks; alerting on skipped records.
- **ch16**: MirrorMaker (`MirrorSourceConnector`) runs on Connect for cross-cluster replication.
- **Change data capture / Debezium**: log-based CDC (PostgreSQL logical decoding, `pgoutput`) as the complete alternative to query-based polling.
