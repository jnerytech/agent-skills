# Chapter 13: Governance

## Core Idea
A shared Kafka cluster needs three guardrails: **schema governance** (the schema is the producer–consumer contract, with an explicit compatibility level), **security** (TLS, authentication, least-privilege ACLs, with encryption beyond that handled outside Kafka), and **quotas** (per-broker throttling so one misbehaving client can't take the cluster down). Kafka has native support for only some of this. Schema enforcement, encryption at rest and end-to-end encryption all need extra components or client code.

## Frameworks Introduced
- **Compatibility levels (consumer perspective)**: *none*, *backward*, *forward*, *full*, each with or without a *transitive* variant.
  - When to use: decide the level per topic before the first schema change. Record it in a central schema catalog (wiki, Git repo or registry), together with what it means for update order.
  - How: **Backward** means a consumer on the new schema can read old data. Update consumers first, then producers. Allows deleting required fields but not adding them. Useful when a new service must replay history. **Forward** means old consumers can read new data. Update producers first and let consumers catch up. Allows adding fields; this is the most common change and the easiest level when retention is short and teams are separate. **Full** means both directions, so update order doesn't matter, but you may only add or delete *optional* fields (fields with defaults). **None** works only when one team owns both sides and retention is short. **Transitive** extends the guarantee to *all* past and future versions, not just the adjacent one. Full transitive is the "holy grail."
  - Why it works / failure mode: Kafka can't migrate stored data atomically the way an RDBMS can. Old records stay in the topic, and several producers may write different versions at once, so consumers must handle mixed versions. Renaming fields breaks every level. A truly breaking change needs a new topic: migrate the data, then move producers and consumers over (the same procedure as changing the partition count, ch06).
- **Schema registry**: a central service that stores and versions schemas, checks compatibility when a new version is registered, and serves schemas to serializers and deserializers.
  - When to use: whenever you need enforcement and not only documentation. Kafka sees only byte arrays and enforces nothing itself.
  - How: producers embed a schema ID instead of the full schema. Register schema versions **through the deployment pipeline**. Do not let producers auto-register in production. Choose an implementation: **Confluent Schema Registry** if you already run the Confluent platform (avoid it for open-source Kafka because of its licence), **Karapace** (Aiven, API-compatible with Confluent, fewer features but enough for most uses), or **Apicurio** (also covers OpenAPI and AsyncAPI, and has a design studio and documentation features).
  - Why it works / failure mode: it adds a component every client depends on. If it's down, producers and consumers are affected. Multi-cluster setups get complex. Schema IDs are sequential and carry no meaning, so restoring a registry from corrupted data is hard, and an export/import between registries can renumber IDs. Validation is client-side only, so a faulty or malicious producer can still write non-conforming bytes.
- **Closing the client-side-validation gap**: (1) the **Single Producer Pattern**: only the owning team gets Write on the topic (secure but restrictive); (2) **broker-side validation**, available only in Confluent Server or Confluent Cloud, not in Apache Kafka; (3) a **validating Kafka proxy** such as Conduktor (commercial) or Kroxylicious (open source, backed by Red Hat, also offers at-rest encryption).
- **Security layers**: authentication (once, at connection setup), then authorization (ACLs), then transport encryption and signing (TLS), then encryption at rest (disk), then end-to-end encryption (client side, for highly sensitive data). Everything below end-to-end leaves data readable by Kafka and server admins, so classify data in Kafka as "internal/confidential" at most.
- **ACL evaluation order**: is the principal a super user? Allow. Otherwise, does any matching **Deny** rule exist? Reject. Otherwise, does a matching **Allow** rule exist? Allow. With no ACL, the request is denied unless `allow.everyone.if.no.acl.found=true`.
- **Zero-downtime security migration** (unsecured cluster to secured): add a TLS+auth listener with a rolling restart, move inter-broker traffic to it with another rolling restart, migrate clients while listing every user, disable the old listener, then enforce ACLs.
- **Quotas**: a byte-rate quota (`producer_byte_rate`, `consumer_byte_rate`) and a CPU quota (`request_percentage`). You set a default and override it per user principal or client ID. Quotas are enforced **per broker**.
  - Why it works / failure mode: the broker computes a throttle delay over 1-second windows, delays its response and mutes the connection. Quotas that are too tight make the producer's `send()` block once its buffer fills, which leads to timeouts and then cascading failures.

## Key Concepts
- **Schema as contract**: data always has a schema, whether documented or not. Making it explicit defines which changes need agreement between producer (data owner) and consumer.
- **Optional field**: a field with a default (Avro: union with `null`, `"default": null`). Adding or removing it never breaks compatibility.
- **Avro**: a binary format whose schema is written in JSON. It is self-describing, but embedding the schema bloats messages, so the registry stores it and the message carries only an ID.
- **Principal**: the `<type:name>` identity used by ACLs, e.g. `User:alice`. Unauthenticated clients are `User:ANONYMOUS`.
- **mTLS principal mapping**: by default the principal is the full certificate DN. `listener.name.<listener>.ssl.principal.mapping.rules` uses regular expressions to shorten it, typically to the CN.
- **SASL mechanisms**: GSSAPI (Kerberos), OAUTHBEARER (OpenID Connect), PLAIN (username/password checked by a callback you write yourself), and SCRAM (challenge–response, with credentials stored in ZooKeeper or KRaft, so no external system).
- **Encryption at rest**: there is no native Kafka support, so you rely on OS, storage or cloud disk encryption. It is cheap and protects against stolen disks, but not against admins.
- **Encryption proxy**: Kroxylicious or Conduktor encrypts on produce and decrypts on consume. This hides data from the cloud provider or data-centre admins, but the proxy itself sees plaintext, so it is **not** end-to-end encryption.
- **Throttle-time metrics**: per-client broker metrics in three forms: **Produce** and **Fetch** (bandwidth) and **Request** (CPU). They should be 0. A value above 0 means a client or user is being throttled.
- **CPU quota capacity**: `request_percentage` is per thread, so the total is `((num.io.threads + num.network.threads) * 100)%`.

## Mental Models
- Think of compatibility from the **consumer's chair**: "which schema versions can *this* consumer read?" Backward means it can read the past. Forward means it can read the future.
- Use **forward** compatibility when producers own the schema and evolve it first, and retention is short. Use **backward** when new services must replay history. Pay for **full** when teams can't coordinate upgrade order.
- Think of quotas as **circuit protection, not billing**. Being per-broker, they don't guarantee a total rate (a client connected to more brokers can exceed its nominal quota), and they exist to stop accidents.
- Think of authentication as **session-scoped**. Deleting a compromised user doesn't kill its live session. Revoke all of its ACLs.

## Anti-patterns
- **Renaming fields in place**: breaks every compatibility level. Use a new topic and migrate instead.
- **Auto-registering schemas from producers in production**: leads to untracked, accidental incompatible versions. Register schemas through CI/CD.
- **Shared schema library across teams**: gives compile-time types but tightly couples the teams and forces coordinated deployments.
- **Manually exporting and importing schemas between registries**: IDs may change, so the migration can't be clean.
- **Rolling out ACLs with `allow.everyone.if.no.acl.found=true` "temporarily"**: the flag gets forgotten and teams delay because things still work. Create all ACLs, test them on a test cluster, and enforce them at once.
- **Calling proxy encryption "end-to-end"**: the legs from producer to proxy and from proxy to consumer are plaintext to the proxy.
- **Compressing after encrypting**: well-encrypted bytes look random and won't compress.
- **Introducing quotas without monitoring**: throttling you can't see causes outages and hurts Kafka adoption.
- **Quotas by client ID on an unauthenticated cluster**: clients can set any `client.id`, so the quota is easy to evade. Prefer quotas on the user principal.

## Code Examples
```properties
# Broker: plaintext + TLS listeners side by side (transition period)
listeners=PLAINTEXT://$IP:9092,SSL://$IP:9093
listener.security.protocol.map=\
    PLAINTEXT:PLAINTEXT,SSL:SSL
ssl.keystore.location=/home/user/certs/broker.ks.p12
ssl.keystore.type=PKCS12
ssl.keystore.password=keystore-pw
ssl.key.password=keystore-pw
ssl.truststore.location=\
    /home/user/certs/ca.truststore.p12
ssl.truststore.password=truststore-pw
ssl.truststore.type=PKCS12

# mTLS: map DN "CN=alice,OU=...,C=..." to principal "alice" (lowercased by /L)
listener.name.ssl.ssl.principal.mapping.rules= \
    RULE:^CN=([^,]*).*$/$1/L ,\
    DEFAULT
```
- **What it demonstrates**: running two listeners lets you add TLS without downtime. The keystore holds the broker's private key and the truststore holds the CA certificate. The mapping rule turns certificate DNs into short principals for ACLs. (Not shown in the chapter: brokers also need `ssl.client.auth=required` before they demand client certificates for mTLS.)

```bash
# Default for all clients: 1 MiB/s produce, 2 MiB/s consume, 100% request share
kafka-configs.sh --bootstrap-server localhost:9092 --alter \
  --entity-type clients --entity-default \
  --add-config 'producer_byte_rate=1048576,consumer_byte_rate=2097152,request_percentage=100'

# Tighter quota for a bursty producer (client ID)
kafka-configs.sh --bootstrap-server localhost:9092 --alter \
  --entity-type clients --entity-name newsletter \
  --add-config 'producer_byte_rate=524288,request_percentage=50'

# Generous quota for a critical consumer (user principal)
kafka-configs.sh --bootstrap-server localhost:9092 --alter \
  --entity-type users --entity-name warehouse \
  --add-config 'consumer_byte_rate=5242880,request_percentage=200'
```
- **What it demonstrates**: a conservative default plus explicit overrides. `--entity-default` sets the baseline and `--entity-type clients|users` with `--entity-name` sets an override.

## Reference Tables
**Table 13.1: Field operations per compatibility level** (corrected, see note)

| Field operation | No compat. | Backward | Forward | Full |
|---|---|---|---|---|
| Delete required field | Yes | Yes | No | No |
| Delete optional field | Yes | Yes | Yes | Yes |
| Add required field | Yes | No | Yes | No |
| **Add optional field** [corrected] | Yes | Yes | Yes | Yes |

**Correction:** both the printed book and the PDF label the 4th row "Remove required field" with Yes in every column. That label is wrong: it duplicates row 1 and contradicts it under Forward and Full. The surrounding text says "optional fields can always be added or removed" and "for full compatibility we can only add or delete optional fields", so the intended row is **Add optional field**, Yes in every column. Rows 1–3 are correct as printed, and the whole table matches Avro / Confluent Schema Registry semantics: BACKWARD means the new reader can read old data (a new field without a default fails), and FORWARD means the old reader can read new data (deleting a field the old reader needs, with no default, fails).

**Table 13.2: Kafka ACL structure.** Read each ACL as: "Principal P is Allowed/Denied Operation O on Resource R (literal name or prefix) from Host H."

| Component | Options | Example |
|---|---|---|
| Principal | `<type:name>` | `User:PriceAnalyticsService`, `Group:AnalyticsServices` |
| Resource type | Cluster, Topic, Group, TransactionalId, DelegationToken | Topic |
| Pattern type | Literal, Prefixed | Literal |
| Resource name | — | Literal `products.prices.changelog`; Prefixed `products.prices` |
| Operation | Describe, Create, Delete, Alter, Read, Write, DescribeConfigs, AlterConfigs, ClusterAction, IdempotentWrite | Read |
| Permission type | Allow, Deny | Allow |
| Host | `<IP>`, `*` | `*` |

**Minimum permissions by role**

| Role | ACLs needed |
|---|---|
| Broker | `Cluster:ClusterAction` |
| Producer | `Topic:Write`, plus `Cluster:IdempotentWrite` if idempotent, plus `TransactionalId:Write` if transactional |
| Consumer | `Topic:Read`, plus `Group:Read` on its group ID |
| Kafka Streams app | `Topic:Create` (and full rights) on the application-ID prefix, plus Read on its input topics |
| CI/CD pipeline (topics, users) | Topics: Create, Delete, Alter, AlterConfigs, Describe, DescribeConfigs. Cluster: Alter and Describe (ACLs), plus AlterConfigs and DescribeConfigs (quotas) |

**Quota keys**

| Key | Unit | Scope |
|---|---|---|
| `producer_byte_rate` | bytes/s | per broker |
| `consumer_byte_rate` | bytes/s | per broker |
| `request_percentage` | % of one thread; maximum is `(num.io.threads + num.network.threads) * 100` | per broker |

Version notes (not in the chapter): the chapter's `AclAuthorizer` is the ZooKeeper-era class. KRaft clusters use `StandardAuthorizer`, and `AclAuthorizer` was removed in Kafka 4.0. The chapter's "`max.inflight.requests`" corresponds to the client config `max.in.flight.requests.per.connection`.

## Worked Example
**Least-privilege ACLs for the online shop's checkout flow:**
- `checkout` service: Allow Write on Topic `checkout.changelog` (Literal). Add `Cluster:IdempotentWrite` if the producer is idempotent, which is the default in modern clients.
- `payment-processing` service: Allow Read on Topic `checkout.changelog` and Allow Read on Group `payment-processor`.
- `checkout-analytics` (Kafka Streams): Allow all operations on Topic, **Prefixed** `checkout.analytics.`, because Streams creates its own internal changelog and repartition topics there. Add Allow Read on `checkout.changelog`.

Each check runs super-user, then Deny, then Allow, so an explicit Deny (for example on one host) beats any Allow. Suppose the analytics service is compromised. Deleting its SCRAM user doesn't end its current authenticated session, so you also remove its ACLs, which blocks the next request.

**Avro size check:** the product record's binary payload is 35 bytes, while its JSON schema is 292 bytes. Sending the schema inline makes every message more than 10× larger than needed. Registering the schema once and sending only its ID fixes that and still traces each record to its exact schema version.

## Key Takeaways
1. Choose and document a compatibility level per topic, including which side must upgrade first. Default to forward for producer-owned data with short retention, and to full where teams can't coordinate.
2. Add fields as optional (with a default) whenever possible. This is the only kind of change that is safe at every level.
3. Run a schema registry (Karapace or Apicurio for open-source Kafka), register schemas from CI/CD, and remember that it validates only on the client side.
4. TLS, authentication (mTLS or SASL-SCRAM/OAUTHBEARER/GSSAPI) and least-privilege ACLs are mandatory. Disk encryption is cheap, so turn it on. Truly sensitive data needs encryption in your own serializer/deserializer, with keys in Vault or similar.
5. You can secure an existing cluster without downtime: run a parallel listener, do rolling restarts, cut the old listener over on a weekday, then enforce all ACLs at once after testing.
6. Introduce quotas once several teams share the cluster, and only after monitoring is in place. Use a conservative default, generous per-user overrides, and alert when throttle time is above 0.

## Connects To
- **ch03**: data formats (JSON, Avro, Protobuf) and message types that schemas formalize.
- **ch06**: the new-topic migration procedure used for breaking schema changes, and TLS's CPU/performance cost.
- **ch07**: ZooKeeper vs KRaft. ZooKeeper TLS has been supported since Kafka 2.5, and SCRAM credentials live in ZooKeeper or KRaft.
- **ch08**: idempotent and transactional producers, which need `IdempotentWrite` and `TransactionalId` ACLs. `send()` blocks under a producer quota.
- **ch09**: consumer groups need `Group:Read`.
- **ch12**: Kafka Streams internal topics, which need prefixed ACLs on the application ID.
- **ch15**: throttle-time metrics and monitoring as a prerequisite for quotas.
- **Avro / Confluent Schema Registry semantics**: BACKWARD, FORWARD and FULL (plus `_TRANSITIVE`) modes match this chapter's consumer-centric definitions.
- **Least privilege / Zero Trust**: why the chapter assumes internal networks are hostile and TLS is mandatory.
