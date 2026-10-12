# Chapter 13: Centralizing Logs with Fluentd and Elasticsearch (EFK)

## Core Idea

Kubernetes stores container logs as raw files on each node — useful for quick inspection but unworkable at scale across many Pods and namespaces. The collect-and-forward model solves this: a log collector reads node-level log files, enriches them with Kubernetes metadata, and ships them to a central store that supports indexing, filtering, and search. The canonical open-source stack for this is EFK: Elasticsearch (storage), Fluentd/Fluent Bit (collection and processing), and Kibana (search UI). The pipeline is independent of applications, so changes to log routing, parsing, and filtering do not require application restarts.

---

## Frameworks Introduced

- **EFK Stack (Elasticsearch + Fluentd/Fluent Bit + Kibana)**
  - What: A three-component logging architecture where Fluent Bit collects and processes logs, Elasticsearch indexes and stores them as documents, and Kibana provides a query UI.
  - When: Any multi-Pod, multi-namespace cluster where `kubectl logs` is insufficient for operational troubleshooting.
  - How: Deploy Fluent Bit as a DaemonSet with a HostPath volume mount to `/var/log/containers`; configure the pipeline via ConfigMap; ship output to Elasticsearch's REST API; visualize in Kibana.
  - Why-or-failure: Without a centralized log collector, logs are siloed per-namespace, logs lose Pod identity when you query across labels, and log files are subject to node-level rotation that destroys history.

- **Fluent Bit Data Pipeline (Input → Parser → Filter → Output)**
  - What: A staged processing model where each stage is a plugin. Tags applied at input route entries through the pipeline.
  - When: Any time you need to enrich, transform, route, or filter log entries before storage.
  - How: Configure each stage in a ConfigMap; use tag patterns in `Match` rules to route entries to specific output plugins.
  - Why-or-failure: Skipping the Kubernetes filter means losing Pod labels, image tag, and host metadata that are critical for production troubleshooting.

---

## Key Concepts

1. **Node-level log storage**: Kubernetes writes container stdout/stderr to files on the node in `/var/log/containers/`. Filename format: `pod-name_namespace_container-name-container-id.log`. Content is raw JSON from the container runtime.

2. **Log files survive Pod restarts** but are subject to node-level log rotation (managed outside Kubernetes) to prevent disk exhaustion.

3. **DaemonSet deployment for Fluent Bit**: Exactly one collector Pod runs per node, accessed via a HostPath volume mount to the node's log directory. The DaemonSet ensures complete cluster coverage with no manual placement.

4. **Tags for routing**: Fluent Bit assigns a tag to each log entry at the input stage (typically derived from the log filename). Tags drive `Match` rules in filter and output stages. A custom tagging scheme using the format `kube.namespace.container_name.pod_name` enables fine-grained routing.

5. **Kubernetes filter**: A Fluent Bit plugin that queries the Kubernetes API server to enrich each log entry with Pod metadata — labels, image tag, image hash, host node, namespace. This adds ~14 additional fields per entry.

6. **Parser plugins**: Convert unstructured text log lines into structured fields using regex. Applied per-Pod via the annotation `fluentbit.io/parser: <parser-name>`. Structured fields become searchable and filterable in Kibana without full-text queries.

7. **grep filter**: Includes or excludes log entries based on a regex match against a named field. Used to drop low-priority log entries before they reach Elasticsearch, reducing storage without removing entries from the raw node log files.

8. **Elasticsearch indexes**: Logs are stored as documents in named indexes. Different namespaces or applications can be routed to different indexes using multiple output stages. Each document can have its own field set (schema-less), which suits heterogeneous log sources.

9. **Kibana index patterns**: Before searching, Kibana requires an index pattern (e.g., `test`) and a time filter field (`@timestamp`). Once configured, all enriched Fluent Bit fields appear as filterable columns in the Discover view.

10. **Pipeline independence from applications**: Log level filtering and routing live in the Fluent Bit ConfigMap, not in application code. Changing the pipeline requires only a Fluent Bit DaemonSet rollout restart, not an application Pod restart.

---

## Mental Models

**Log files are the source of truth, not kubectl**: `kubectl logs` reads from the same node log files that Fluent Bit reads. Filtering in the pipeline drops entries from Elasticsearch but never from the node files. In a troubleshooting flow, Kibana identifies the Pod; `kubectl logs` is then used for full fidelity on that Pod.

**Tags are the pipeline's routing layer**: Think of a tag like a mail routing label. Applied once at input, a tag determines which filters and outputs see the entry. The richer the tag (namespace + Pod name + container), the more precise the downstream routing rules can be — without requiring changes to the source application.

**Parsers are opt-in and Pod-scoped**: Parsers are registered globally in the ConfigMap but activated per-Pod via annotation. An unrecognized or unannotated Pod continues to pass through the pipeline with the raw log message intact; adding a parser annotation to a Deployment spec is a zero-downtime enrichment.

**Fluent Bit restart ≠ application restart**: Because Fluent Bit tracks its position in each log file, restarting the DaemonSet (e.g., after a ConfigMap update) does not lose log entries. This makes pipeline configuration changes safe to apply in production without affecting the applications being monitored.

---

## Anti-patterns

- **Filtering at the input stage instead of using tags**: Reading only specific log files (e.g., by filename pattern) at input is tempting but brittle. It bypasses the routing flexibility of tags and means the Kubernetes filter cannot enrich excluded entries. Read all inputs; route with tags.

- **Writing logs directly from application code to Elasticsearch**: Ties every application to a specific storage backend, breaks for legacy apps writing to OS logs, and duplicates collection logic across every service. The DaemonSet collector is operationally simpler and handles all workloads uniformly.

- **Running Elasticsearch as a single-Pod Deployment in production**: Elasticsearch supports clustering via StatefulSet with persistent storage, or a managed cloud service. A single-Pod deployment is a single point of failure with no data durability guarantees.

- **Skipping Kibana index pattern setup**: Kibana cannot search any index until an index pattern and time filter field (`@timestamp`) are configured. This is a manual step; forgetting it leaves Elasticsearch populated but unsearchable.

- **Relying on kubectl for cross-namespace log analysis at scale**: `kubectl logs` requires one namespace at a time, cannot join log streams from multiple Pods by correlation ID, and provides no time-range indexing. It is a debugging tool, not a log management system.

---

## Code Examples

```yaml
# Fluent Bit DaemonSet — runs collector on every node
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluent-bit
  namespace: kiamol-ch13-logging
spec:
  selector:
    matchLabels:
      app: fluent-bit
  template:
    spec:
      containers:
      - name: fluent-bit
        image: fluent/fluent-bit
        volumeMounts:
        - name: varlog
          mountPath: /var/log
      volumes:
      - name: varlog
        hostPath:
          path: /var/log
```

```ini
# Fluent Bit pipeline ConfigMap — input, parse, kubernetes filter, output
[INPUT]
    Name              tail
    Tag               kube.*
    Path              /var/log/containers/*.log
    Parser            docker

[FILTER]
    Name              kubernetes
    Match             kube.*
    Merge_Log         On

[OUTPUT]
    Name              es
    Match             kube.kiamol-ch13-test.*
    Host              elasticsearch
    Port              9200
    Index             test
    Type              _doc
```

```ini
# Custom parser registered in ConfigMap — regex splits priority from message
[PARSER]
    Name      dotnet-syslog
    Format    regex
    Regex     ^\<(?<priority>[0-9]+)\>*(?<message>.*)$
```

```yaml
# Pod spec annotation — activates named parser for this Pod's logs
template:
  metadata:
    annotations:
      fluentbit.io/parser: dotnet-syslog
```

```ini
# grep filter — drop low-priority API log entries before Elasticsearch
[FILTER]
    Name     grep
    Match    kube.kiamol-ch13-test.api.numbers-api*
    Regex    priority [234]
```

```bash
# Deploy Fluent Bit DaemonSet and ConfigMap
kubectl apply -f fluentbit/

# Restart DaemonSet after ConfigMap update (safe — no log loss)
kubectl rollout restart ds/fluent-bit -n kiamol-ch13-logging

# Verify collector is running and reading logs
kubectl logs -l app=fluent-bit -n kiamol-ch13-logging --tail 2
```

---

## Reference Tables

### EFK Component Roles

| Component | Role | Deployment Model | Notes |
|---|---|---|---|
| Fluent Bit | Collect, parse, filter, route, ship logs | DaemonSet (one Pod per node) | Lightweight; CNCF project; subset of Fluentd with 1,000+ plugins in parent |
| Fluentd | Alternative collector with larger plugin ecosystem | DaemonSet | Use when Fluent Bit lacks a required output plugin (e.g., MongoDB, AWS S3) |
| Elasticsearch | Document store and indexing engine for log data | Single Pod (dev) or StatefulSet (prod) | Schema-less; REST API; organizes data into named indexes |
| Kibana | Web UI for querying and visualizing Elasticsearch data | Deployment (stateless; scale freely) | Requires manual index pattern setup per index; port 5601 |

### Log Pipeline Stages

| Stage | Fluent Bit Plugin Type | Purpose | Key Config |
|---|---|---|---|
| Collect | INPUT (tail) | Read log files from node HostPath mount | `Path`, `Tag`, `Parser` |
| Parse | PARSER | Decode JSON runtime wrapper; optionally apply custom regex parser | `Format`, `Regex` |
| Enrich | FILTER (kubernetes) | Add Pod labels, image tag, image hash, namespace via API server query | `Match`, `Merge_Log` |
| Route | Tag matching in FILTER/OUTPUT | Direct log entries to correct output based on namespace or Pod name | `Match kube.<namespace>.*` |
| Filter | FILTER (grep) | Include or exclude entries by field value regex | `Regex <field> <pattern>` |
| Ship | OUTPUT (es, stdout, counter) | Send processed entries to target system | `Host`, `Port`, `Index` |
| Store | Elasticsearch index | Persist documents; make fields searchable | Index pattern in Kibana |

### Node Log File Naming Convention

| Component | Value in Filename |
|---|---|
| Pod name | `timecheck-abc123` |
| Namespace | `kiamol-ch13-dev` |
| Container name | `logger` |
| Container ID | `a1b2c3d4...` |
| Full filename | `timecheck-abc123_kiamol-ch13-dev_logger-a1b2c3d4.log` |

---

## Worked Example

**Goal**: Deploy Fluent Bit to collect container logs from all nodes, enrich them with Kubernetes metadata, apply a custom parser for the numbers-API, and ship structured logs to Elasticsearch for search in Kibana.

**Step 1 — Deploy the timecheck app to generate logs in two namespaces**

```bash
kubectl apply -f timecheck/
kubectl wait --for=condition=ContainersReady pod -l app=timecheck -n kiamol-ch13-dev
kubectl wait --for=condition=ContainersReady pod -l app=timecheck -n kiamol-ch13-test
```

Observe via `kubectl logs` that cross-namespace querying is cumbersome and loses Pod identity.

**Step 2 — Deploy Fluent Bit as a DaemonSet**

```bash
kubectl apply -f fluentbit/
kubectl wait --for=condition=ContainersReady pod -l app=fluent-bit -n kiamol-ch13-logging
kubectl logs -l app=fluent-bit -n kiamol-ch13-logging --tail 2
```

Fluent Bit reads all log files under `/var/log/containers/` via HostPath mount and writes them to stdout. Entries appear as raw JSON plus a precise timestamp added by Fluent Bit.

**Step 3 — Enable the Kubernetes filter and namespace-based routing**

```bash
kubectl apply -f fluentbit/update/fluentbit-config-match.yaml
kubectl rollout restart ds/fluent-bit -n kiamol-ch13-logging
kubectl wait --for=condition=ContainersReady pod -l app=fluent-bit -n kiamol-ch13-logging
kubectl logs -l app=fluent-bit -n kiamol-ch13-logging --tail 1
```

Each log entry now carries ~14 additional metadata fields from the API server, including Pod name, labels, container image tag, and image hash. The `Match` rule restricts stdout output to the `test` namespace only.

**Step 4 — Deploy Elasticsearch and Kibana**

```bash
kubectl apply -f elasticsearch/
kubectl wait --for=condition=ContainersReady pod -l app=elasticsearch -n kiamol-ch13-logging
kubectl apply -f kibana/
kubectl wait --for=condition=ContainersReady pod -l app=kibana -n kiamol-ch13-logging
kubectl get svc kibana -o jsonpath='http://{.status.loadBalancer.ingress[0].*}:5601' -n kiamol-ch13-logging
```

Elasticsearch exposes a REST API on port 9200; Kibana connects to it and serves the UI on port 5601.

**Step 5 — Route logs to Elasticsearch**

```bash
kubectl apply -f fluentbit/update/fluentbit-config-elasticsearch.yaml
kubectl rollout restart ds/fluent-bit -n kiamol-ch13-logging
kubectl wait --for=condition=ContainersReady pod -l app=fluent-bit -n kiamol-ch13-logging
```

The updated ConfigMap adds an `es` output plugin targeting `Host: elasticsearch`, `Index: test` for the test namespace and a `kube-system` index for Kubernetes system Pods. Logs from the dev namespace match no output rule and are discarded.

**Step 6 — Set up Kibana index pattern**

In the Kibana UI: Discover → Create index pattern → enter `test` → select `@timestamp` as time filter → Create. The Discover tab then shows indexed log documents with all enriched fields available as filters.

**Step 7 — Add a custom parser and grep filter**

Register the `dotnet-syslog` parser in the ConfigMap, apply the `fluentbit.io/parser: dotnet-syslog` annotation to the numbers-API Deployment, and apply a grep filter to retain only priority `[234]` entries:

```bash
kubectl apply -f fluentbit/update/fluentbit-config-parser.yaml
kubectl apply -f fluentbit/update/fluentbit-config-grep.yaml
kubectl rollout restart ds/fluent-bit -n kiamol-ch13-logging
kubectl apply -f numbers/update/
```

In Kibana, the `priority` field now appears as a discrete column. Filter to `priority: 4` to see warnings only. Low-priority (level 6) startup entries are absent from Elasticsearch but still visible via `kubectl logs`.

**Step 8 — End-to-end troubleshooting flow**

1. User reports an error with a failure ID from the numbers-API response.
2. In Kibana Discover, enter: `kubernetes.labels.app:numbers-api AND log:<failure-ID>`.
3. Single matching document returned with Pod name, image hash, timestamp.
4. Use `kubectl logs -n kiamol-ch13-test -l app=numbers-api` for full context around the failure.

---

## Key Takeaways

1. Kubernetes writes container stdout/stderr to node-local files using a standard naming convention that encodes namespace, Pod, and container — no application change is required to make logs collectable.
2. Fluent Bit deployed as a DaemonSet with a HostPath volume is the standard pattern for cluster-wide log collection; every node gets exactly one collector Pod.
3. The Kubernetes filter is essential in production: it enriches every log entry with Pod labels, image tags, and host metadata that are critical for filtering and root-cause analysis.
4. Tags applied at input stage drive all routing decisions downstream — investing in a good tagging scheme (namespace + Pod + container) pays off in simple, declarative Match rules.
5. Custom parsers activated via Pod annotations convert opaque text logs into structured fields that Elasticsearch indexes and Kibana can filter without full-text search.
6. Pipeline-level grep filters allow log verbosity to be managed centrally without touching application Pods; raw entries remain accessible via `kubectl logs`.
7. The EFK stack is entirely open source and can run identically in development, staging, and production — shared tooling across environments improves the quality and utility of application logging.

---

## Connects To

- **Chapter 7 (Multi-container Pods / Sidecars)**: Logging sidecars that relay app log files to stdout are the prerequisite for node-level log collection. Logs must appear on stdout for Kubernetes to write them to node files.
- **Chapter 4 (ConfigMaps and Secrets)**: Fluent Bit's entire pipeline is defined in a ConfigMap; the pattern of rolling restart after ConfigMap update is the standard mechanism for applying pipeline changes.
- **Chapter 6 (Scaling and Controllers)**: The DaemonSet controller is what ensures one Fluent Bit Pod per node as the cluster scales. Understanding DaemonSet scheduling is necessary to reason about log collection coverage.
- **Chapter 8 (StatefulSets)**: Elasticsearch in production is modeled as a StatefulSet with persistent storage for durability and high availability.
- **Chapter 9 (Rollouts and Rollbacks)**: `kubectl rollout restart ds/fluent-bit` is used repeatedly to apply pipeline config changes safely; understanding rollout mechanics explains why this is non-destructive.
- **Chapter 12 (Self-healing / Probes)**: Liveness and readiness probes on Elasticsearch and Kibana Pods ensure the logging infrastructure remains available without manual intervention.
