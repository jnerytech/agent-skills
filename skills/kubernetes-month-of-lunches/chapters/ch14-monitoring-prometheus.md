# Chapter 14: Monitoring Applications and Kubernetes with Prometheus

## Core Idea

Prometheus provides a pull-based, centralized monitoring system that integrates natively with Kubernetes through its API-driven service discovery. Every monitoring target exposes metrics at an HTTP endpoint; Prometheus scrapes those endpoints on a schedule and stores the results. Grafana then visualizes the stored data. Together, the three components — Prometheus, exporters/client libraries, and Grafana — form a complete observability stack that spans individual application logic, third-party infrastructure components, and the Kubernetes platform itself.

---

## Frameworks Introduced

- **Pull-based scraping**
  - **What**: Prometheus periodically makes HTTP GET requests to a `/metrics` endpoint on each target rather than having targets push data to a central collector.
  - **When**: Any time you need decoupled, low-overhead metric collection that survives target restarts.
  - **How**: Configure Prometheus with `scrape_configs` that list jobs; each job defines which targets to poll and how often. Direct Pod-IP scraping bypasses Services so each replica is measured independently.
  - **Why / failure**: If a target is missing a container port declaration or serves metrics on a non-standard path and no annotation overrides it, Prometheus either cannot reach it or stores data under the wrong path. Always declare `containerPort` and use `prometheus.io/path` annotations when needed.

- **Exporter pattern (adapter pattern)**
  - **What**: A separate sidecar container that reads internal state from a third-party application (Nginx stub_status page, Postgres system tables) and re-exposes it in Prometheus format on a dedicated port.
  - **When**: The target application has no native Prometheus client library integration.
  - **How**: Add the exporter image as an extra container in the Pod spec; add `prometheus.io/port` annotation so Prometheus knows which port to scrape; both containers share the Pod network namespace so the exporter reaches the main app via `localhost`.
  - **Why / failure**: Exporters are limited to information the target application already surfaces. Nginx's basic exporter cannot break down HTTP status codes if the source data is not available. Pick exporters that match your observability requirements.

- **Convention-driven service discovery with relabeling**
  - **What**: A set of `relabel_configs` in a Prometheus scrape job that automatically filters and maps Kubernetes Pod metadata (namespace, labels, annotations) onto Prometheus metric labels, reducing per-app boilerplate.
  - **When**: Running Prometheus in a shared cluster where many apps are deployed independently.
  - **How**: The pipeline keeps only Pods in a target namespace, copies the Pod `app` label to the Prometheus `job` label, uses the Pod name as the `instance` label, and reads optional annotations to override path or port.
  - **Why / failure**: Tightly coupling the pipeline to a single namespace is intentional for isolation. Forgetting to add the `app` label on a Pod or setting the wrong annotation key silently breaks discovery.

---

## Key Concepts

1. **Scraping**: The act of Prometheus making an HTTP GET to `/metrics` on a target. Prometheus calls this operation "scraping". Frequency is configurable per job (default 30 s in the book examples).

2. **`/metrics` endpoint**: The HTTP path where a component exposes all its current metric values in the Prometheus text exposition format. Every instrumented app or exporter must serve this endpoint (or a custom path declared via annotation).

3. **Prometheus client libraries**: Language-specific libraries (Go, Java, .NET, Node.js, Python, etc.) that application code embeds to define and expose metrics. They also publish run-time metrics automatically (memory, CPU, thread count for the .NET runtime, for example).

4. **Labels**: Key-value pairs attached to every metric sample. Used to identify the source (`instance`, `job`) and to slice/aggregate in queries. Relabeling shapes which labels end up on stored samples.

5. **Relabeling (`relabel_configs`)**: A pipeline applied before metrics are stored. Rules can keep, drop, or transform labels based on regex matches against Pod metadata. Allows one generic Prometheus config to handle many diverse apps.

6. **Annotations as overrides**: Pod manifest annotations prefixed with `prometheus.io/` (`prometheus.io/path`, `prometheus.io/port`) let individual workloads deviate from the default discovery convention without touching the Prometheus config.

7. **Exporters**: Standalone adapter applications (Nginx exporter, Postgres exporter, blackbox exporter) that translate a third-party system's internal metrics into the Prometheus exposition format.

8. **Blackbox exporter**: A special exporter that performs external probing (TCP or HTTP) against an application container and reports whether it is reachable, without requiring the app to expose any native metrics. Useful for legacy or opaque services.

9. **kube-state-metrics**: A Kubernetes-native component that queries the Kubernetes API and exposes object-level metrics (Deployment replicas, Pod status, node conditions). Runs as a Deployment; Prometheus reaches it via a static DNS target.

10. **cAdvisor**: A Google open source project that reports container-level resource usage (CPU, memory) by reading from the container runtime on each node. Runs as a DaemonSet; one Pod per node. Prometheus discovers DaemonSet Pods via Kubernetes service discovery.

11. **Grafana**: An open source visualization tool that runs queries against Prometheus (using PromQL) and renders the results as dashboards. Dashboards are stored as JSON and can be loaded via ConfigMaps, enabling GitOps-style management.

---

## Mental Models

**Metrics as an HTTP API**: Think of every Pod's `/metrics` URL as a read-only REST endpoint that returns the current internal state in a standardized text format. Prometheus is just a periodic client that calls those endpoints and saves the responses. This makes instrumentation independent of Prometheus itself — you can `curl` a `/metrics` endpoint in a debugging session without any Prometheus dependency.

**Layered monitoring targets**: There are three distinct layers, each requiring a different integration approach:
- *Application layer*: custom business metrics + runtime stats via a client library embedded in the app code.
- *Infrastructure component layer*: third-party apps (databases, proxies) covered via sidecar exporters.
- *Platform layer*: Kubernetes objects and container resources covered by kube-state-metrics and cAdvisor, which are cluster-wide components scraped by separate Prometheus jobs.

The three layers are independent; you can have full application metrics without any cluster-level metrics, and vice versa.

**Pod-level scraping, not Service-level**: Prometheus targets individual Pod IP addresses, not Services. This is deliberate: each replica records its own metric values, and scraping at the Service level would load-balance across replicas, making it impossible to compare individual instance behaviour. Aggregation happens at query time in PromQL, not at collection time.

---

## Anti-patterns

- **Scraping a Service instead of Pods**: Funneling scrapes through a Service load-balancer merges per-replica data. When one replica is slow or erroring, the Service-level metrics hide it.

- **Omitting the container port declaration**: Prometheus relies on the `containerPort` field in the Pod spec to know which port to target. Leaving it out is a silent failure; Prometheus cannot discover the correct port.

- **Excluding components without an annotation**: If a component has no Prometheus support and no explicit `prometheus.io/scrape: "false"` annotation (or equivalent relabel exclusion), Prometheus continually tries to scrape it, producing persistent scrape errors in the Targets view. Always annotate non-Prometheus-ready components to opt them out.

- **Overloaded dashboards**: More than a dozen or so visualizations on a single Grafana dashboard becomes cognitively overwhelming. If a panel does not convey useful information at a glance, it is not adding value. Keep dashboards focused on key indicators.

- **Using platform metrics as a substitute for app metrics**: cAdvisor and kube-state-metrics tell you about container resource consumption, not user-facing behaviour. Heavy disk usage is interesting; a high percentage of users abandoning a slow checkout page is actionable. Platform metrics complement, not replace, application-level instrumentation.

---

## Code Examples

**Pod spec annotated for Prometheus scraping (custom path)**
```yaml
# prometheus.io/path annotation overrides default /metrics path
template:
  metadata:
    labels:
      app: apod-api
    annotations:
      prometheus.io/path: "/actuator/prometheus"
```

**Prometheus relabel rule that activates the path annotation**
```yaml
- source_labels:
  - __meta_kubernetes_pod_annotationpresent_prometheus_io_path
  - __meta_kubernetes_pod_annotation_prometheus_io_path
  regex: true;(.*)
  target_label: __metrics_path__
```

**Prometheus scrape job using Kubernetes service discovery (namespace filter)**
```yaml
scrape_configs:
  - job_name: 'test-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_namespace]
        action: keep
        regex: kiamol-ch14-test
```

**Nginx exporter sidecar container in a Pod spec**
```yaml
- name: exporter
  image: nginx/nginx-prometheus-exporter:0.8.0
  ports:
    - name: metrics
      containerPort: 9113
  args:
    - -nginx.scrape-uri=http://localhost/stub_status
```

**kube-state-metrics as a static Prometheus scrape target**
```yaml
- job_name: 'kube-state-metrics'
  static_configs:
    - targets:
      - kube-state-metrics.kube-system.svc.cluster.local:8080
      - kube-state-metrics.kube-system.svc.cluster.local:8081
```

**cAdvisor discovered via Kubernetes service discovery (DaemonSet Pods)**
```yaml
- job_name: 'cadvisor'
  kubernetes_sd_configs:
    - role: pod
  relabel_configs:
    - source_labels:
        [__meta_kubernetes_namespace, __meta_kubernetes_pod_labelpresent_app, __meta_kubernetes_pod_label_app]
      action: keep
      regex: kube-system;true;cadvisor
```

**Scrape-exclusion annotation (opt a Pod out of scraping)**
```yaml
annotations:
  prometheus.io/scrape: "false"
```

---

## Reference Tables

### Monitoring target types and integration methods

| Target type | Example | Integration method | Prometheus job config | Grafana data source |
|---|---|---|---|---|
| Application with client library | .NET timecheck, Java APOD API, Node.js APOD web | Embed Prometheus client lib; expose `/metrics` (or custom path) in app code | Kubernetes service discovery (`role: pod`), relabel by namespace | PromQL query on stored app + runtime metrics |
| Third-party app with exporter | Nginx proxy, Postgres database | Add exporter sidecar container; set `prometheus.io/port` annotation | Same discovery job; exporter container port targeted via annotation | PromQL query on exporter-produced metrics |
| App with no metrics (blackbox) | Random-number API | Add blackbox exporter sidecar; configure HTTP/TCP probe target | Same discovery job; path/port annotations pointing to blackbox exporter | Simple up/down status panel |
| Kubernetes objects | Deployments, Pods, Nodes | kube-state-metrics Deployment in `kube-system` | Static target using full DNS name of kube-state-metrics Service | PromQL filtered by namespace/workload label |
| Container resources | CPU, memory per container | cAdvisor DaemonSet in `kube-system` | Kubernetes service discovery for cAdvisor DaemonSet Pods | PromQL aggregated or per-container |
| Cluster nodes (not covered in depth) | Linux/Windows nodes | Node Exporter / Windows Exporter on each node | Node service discovery or static targets | Node-level disk, network, CPU panels |

---

## Worked Example

**Scenario**: Instrument the timecheck app with a Prometheus client library, discover it automatically, and visualize its counter in Grafana.

**Step 1 — Deploy Prometheus in a dedicated namespace**

```bash
kubectl apply -f prometheus/        # Deployment + ConfigMap with scrape_configs
kubectl wait --for=condition=ContainersReady pod -l app=prometheus \
  -n kiamol-ch14-monitoring
```

The ConfigMap defines a `test-pods` job that uses `kubernetes_sd_configs` with `role: pod`. The relabel pipeline keeps only Pods in the `kiamol-ch14-test` namespace and copies the `app` label to the Prometheus `job` label. At this point the Targets page shows the `test-pods` category with zero targets because the test namespace does not exist yet.

**Step 2 — Deploy the instrumented app**

```bash
kubectl apply -f timecheck/
kubectl wait --for=condition=ContainersReady pod -l app=timecheck \
  -n kiamol-ch14-test
```

The timecheck app is a .NET background process. It embeds the Prometheus .NET client library, which registers the application-specific counter `timecheck_total` (how many time checks have been logged) alongside automatic runtime metrics (`dotnet_total_memory_bytes`, thread counts, etc.). The Pod spec declares `containerPort: 80` so Prometheus can find the right port.

Within one scrape interval (30 s) Prometheus detects the new Pod via the Kubernetes API, applies the relabel rules, confirms the Pod is in the correct namespace, and begins polling `http://<pod-ip>:80/metrics`.

**Step 3 — Query metrics in Prometheus**

Browse to the Prometheus web UI `/graph` page. Select `timecheck_total` from the metric dropdown and click Execute. The result shows the current counter value for the single Pod.

**Step 4 — Scale up and observe per-replica metrics**

```bash
kubectl scale deploy/timecheck --replicas 2 -n kiamol-ch14-test
```

Prometheus detects the second Pod automatically and begins scraping it. The same `timecheck_total` query now returns two rows, each labelled with a different Pod name in the `instance` label. One Pod has processed significantly more iterations than the other because it started earlier. This per-replica visibility is why Prometheus scrapes Pod IPs directly, not the Service.

**Step 5 — Deploy Grafana with a pre-built dashboard**

```bash
kubectl apply -f grafana/
kubectl wait --for=condition=ContainersReady pod -l app=grafana \
  -n kiamol-ch14-monitoring
```

Grafana is deployed with two ConfigMaps: one that sets the Prometheus data source URL, and one that embeds a dashboard JSON definition for the timecheck (and later APOD and to-do) apps. Each visualization panel in the dashboard is backed by a PromQL expression. The dashboard shows CPU usage, memory usage, HTTP request rates, and the application-specific counter — all sourced from the metrics Prometheus has already been collecting.

**Key outcome**: No manual Prometheus configuration was required when the timecheck Pod was deployed. The combination of the relabeling pipeline and the Pod metadata (namespace, `app` label, declared container port) was sufficient for automatic discovery. Adding replicas also required no configuration change. The only development effort was the dozen-or-so lines to initialize the Prometheus client library inside the application.

---

## Key Takeaways

1. **Prometheus uses a pull model**: targets expose an HTTP `/metrics` endpoint, and Prometheus collects from them on a schedule. You do not need to configure anything in Prometheus when a new app is deployed if it follows the discovery conventions.

2. **Per-Pod scraping is essential**: targeting Pod IPs (not Services) ensures every replica is measured independently, enabling per-instance drilldown and detection of outlier behaviour.

3. **Three integration paths cover all cases**: Prometheus client libraries for apps you own, exporters (as sidecars) for third-party components, and the blackbox exporter for anything else. No application needs to be left out of monitoring.

4. **Kubernetes annotations are the extension point**: `prometheus.io/path` and `prometheus.io/port` annotations let individual Pods override discovery defaults without modifying the shared Prometheus configuration.

5. **Platform metrics require dedicated components**: cAdvisor (DaemonSet) captures container resource usage; kube-state-metrics (Deployment) captures Kubernetes object status. Both are separate from application-level monitoring and must be explicitly deployed and added as Prometheus scrape targets.

6. **Grafana dashboards are configuration, not state**: storing dashboard JSON in ConfigMaps means dashboards are versioned, reproducible, and can be deployed alongside the applications they monitor — the same pattern used for everything else in Kubernetes.

7. **Start simple and iterate**: Even a Grafana panel that shows only "up" or "down" is more useful than nothing. Instrument the four golden signals (latency, traffic, errors, saturation) first, then add application-specific metrics as operational needs become clearer.

---

## Connects To

- **Chapter 7 (Multi-container Pods / Adapter pattern)**: Exporters as sidecars are a direct application of the adapter pattern introduced there. The exporter adapts a non-Prometheus interface to the Prometheus exposition format.
- **Chapter 13 (Logging with Fluentd/Fluent Bit)**: Monitoring (Prometheus) and logging (Fluent Bit) are complementary. Monitoring tells you *something is wrong*; logs give you the details. The relabeling pipeline in Prometheus is conceptually similar to Fluent Bit's data pipeline.
- **Chapter 12 (Self-healing and Probes)**: The blackbox exporter provides observability for workloads that are not good candidates for Kubernetes liveness/readiness probes. Platform metrics (node pressure from kube-state-metrics) give early warning before Kubernetes starts evicting Pods.
- **Chapter 9 (Rollouts and Rollbacks)**: Grafana dashboards that include application version labels (from Pod labels) enable correlating a metric degradation with a specific release, supporting data-driven rollback decisions.
- **Appendix B (ebook)**: Full walkthrough of adding Prometheus instrumentation (four golden signals) to a multi-language application (APOD: Java, Go, Node.js), including the client library setup omitted from this chapter.
