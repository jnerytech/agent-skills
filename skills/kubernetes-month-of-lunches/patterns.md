# Patterns & Techniques

## Declarative Desired-State Apply
**When to use**: Every deployment, update, or scale operation — as the primary workflow for all cluster changes.
**How**: Author a YAML manifest (`apiVersion`, `kind`, `metadata`, `spec`). Run `kubectl apply -f <manifest.yaml>`. Re-applying is a no-op if state already matches (idempotent). Use `kubectl apply -f <url>` to deploy from a remote URL.
**Trade-offs**: Mandates discipline — imperative commands (`kubectl run`, `kubectl create`) bypass audit trails and drift detection. A wrong manifest is faithfully enforced; validate YAML before applying.
**Source**: Ch 1, 2

---

## Deployment Rolling Update + Rollback
**When to use**: Every production Deployment update where zero downtime is required.
**How**: Set `strategy.type: RollingUpdate` with `maxSurge`, `maxUnavailable`, and `minReadySeconds` in the Deployment spec. Monitor with `kubectl rollout status deploy/<name>`. On failure, run `kubectl rollout undo deploy/<name> --to-revision=N`. Old ReplicaSets are retained (default 10) as revision checkpoints.
**Trade-offs**: Default 25%/25% surge/unavailable is aggressive — tune deliberately. `minReadySeconds: 0` risks promoting a fast-crashing image. Kubernetes does NOT auto-rollback; manual `rollout undo` is required.
**Source**: Ch 9

---

## Blue-Green Deployment (Manual)
**When to use**: UX-breaking changes where dual-version coexistence confuses users, or teams new to rolling updates.
**How**: Deploy a second Deployment with a distinct version label. Switch a Service's `selector` to the new label to redirect all traffic. Keep the old Deployment idle for fast fallback; delete it after validation.
**Trade-offs**: Doubles compute cost. No built-in rollout history; requires strict label hygiene. Not suitable for clusters where spare capacity is scarce.
**Source**: Ch 9

---

## Init Container Pattern
**When to use**: Environment preparation that must complete before the app starts — config merging, secret fetching, DB migrations.
**How**: Define containers in `spec.initContainers[]`. Each runs sequentially to completion (exit 0) before `spec.containers[]` start. Write results to a shared `emptyDir` volume for the app to consume. Init logic must be idempotent — it re-runs on every Pod replacement.
**Trade-offs**: A failing init container blocks the entire Pod (and the rolling update) indefinitely — old ReplicaSet stays up but no new Pods become Ready. Watch `kubectl get pods` for pods stuck in `Init` state.
**Source**: Ch 7

---

## Sidecar / Adapter Pattern
**When to use**: Augmenting a running app without modifying its image — log relay, health endpoint, metrics exposure.
**How**: Add extra entries in `spec.containers[]`. All start in parallel; all must be Ready before the Pod is Ready. Share data via `emptyDir` volumes (app writes, sidecar reads `readOnly: true`). Adapter variant: sidecar tails a log file and echoes to stdout so `kubectl logs` captures it.
**Trade-offs**: Every sidecar is a new failure mode and a new resource cost. A crashing sidecar marks the entire Pod not-Ready, removing it from Service endpoints. Multiply cost by replica count.
**Source**: Ch 7

---

## Ambassador (Outbound Proxy Sidecar) Pattern
**When to use**: Controlling outgoing network traffic from the app without code changes — service discovery, address remapping, outbound access control, retries.
**How**: Set `http_proxy=http://localhost:<port>` in the app container env. Configure a proxy sidecar to map localhost URIs to real cluster addresses. Both containers share the Pod's network namespace (same IP); the sidecar intercepts all outbound traffic.
**Trade-offs**: Complex proxy configuration can silently block legitimate traffic. Requires thorough URI-map testing. Mirrors service mesh data-plane (Envoy/Linkerd) behavior at small scale.
**Source**: Ch 7

---

## Readiness vs. Liveness Probes
**When to use**: Always — together on every container that serves requests or can enter a deadlocked state.
**How**:
- **Readiness**: `readinessProbe.httpGet/tcpSocket/exec` — failure removes Pod from Service endpoints without restart. Use `periodSeconds: 5`.
- **Liveness**: `livenessProbe.httpGet/...` — failure kills and replaces the container (Pod stays). Use `initialDelaySeconds` and `failureThreshold` to avoid premature kills.
- Databases: `tcpSocket` for readiness, `exec: pg_isready` for liveness.
**Trade-offs**: Readiness-only means all Pods failing = zero endpoints, app offline, no restarts. Liveness `initialDelaySeconds` too short = premature restart loop. Pair both or accept the stated risk.
**Source**: Ch 12

---

## Resource Requests and Limits
**When to use**: Mandatory before production on every container spec.
**How**: Set `resources.requests` (scheduler hint, soft minimum) and `resources.limits` (hard cap). Memory limit breach → `OOMKilled` restart. CPU limit → throttle, not kill. Use `ResourceQuota` to cap namespace-wide consumption.
**Trade-offs**: Limits too low → `CrashLoopBackOff` under normal load. No limits → one container can exhaust the node, evicting unrelated workloads. Requests without limits → poor scheduling decisions.
**Source**: Ch 12

---

## ConfigMap / Secret Injection — Env vs. Volume
**When to use**: All multi-environment deployments. Use env vars for simple scalars; use volume mounts for structured files (JSON, YAML) or Secrets that benefit from file-permission control.
**How**:
- **Env**: `envFrom.configMapRef` or `env[].valueFrom.configMapKeyRef`. Frozen at Pod start; Pod must restart on change.
- **Volume**: Mount at a subdirectory (`/app/config`, never `/app`). Kubernetes updates mounted files within ~2 min on ConfigMap change (if app watches filesystem).
- **Secret**: Prefer volume mount with `defaultMode: 0400`. Base64 is encoding, not encryption — real security via RBAC + encryption at rest.
- **Versioned ConfigMaps**: Name with suffix (`app-config-v2`), update Deployment reference → Pod replacement → rollback capability.
**Trade-offs**: Volume mounts risk overwriting image directories if `mountPath` matches an existing directory. Env vars offer no live-update path. `stringData` in Secret YAML exposes credentials in source control.
**Source**: Ch 4, 9

---

## PVC + StorageClass for Persistent Storage
**When to use**: Any workload that must retain data across Pod replacements.
**How**: Create a `PersistentVolumeClaim` with `accessModes`, `resources.requests.storage`, and optionally a `storageClassName`. Reference by `volumes[].persistentVolumeClaim.claimName` in the Pod spec. For dynamic provisioning omit `storageClassName` (uses cluster default). For static binding, set `storageClassName: ""` and pre-create a matching PV.
**Trade-offs**: A PVC that cannot bind (no matching PV, no default class) leaves the Pod permanently Pending with no visible Deployment-level error. Always verify `kubectl get pvc` shows `Bound` status. Dynamic provisioning behavior differs across distributions.
**Source**: Ch 5

---

## volumeClaimTemplates for StatefulSet Storage
**When to use**: Stateful apps (databases, message queues) where each Pod replica needs independent, stable persistent storage.
**How**: Add `spec.volumeClaimTemplates` to the StatefulSet. One PVC is created per Pod (`<template-name>-<pod-name>`). PVC binding is preserved on Pod replacement — new `todo-db-0` re-attaches to `data-todo-db-0`. Pair with a headless Service (`clusterIP: None`) for per-Pod DNS (`<pod>.<svc>.<ns>.svc.cluster.local`).
**Trade-offs**: Adding `volumeClaimTemplates` to an existing StatefulSet requires delete-and-recreate. Plan PVC specs before first deployment.
**Source**: Ch 8

---

## Service-Based Load Balancing
**When to use**: Any inter-Pod or external traffic — never use Pod IPs directly.
**How**:
- **ClusterIP**: Internal traffic; DNS name = `<service-name>.<namespace>.svc.cluster.local`.
- **LoadBalancer**: External traffic; same YAML across environments, different platform behavior.
- **ExternalName**: DNS CNAME alias for external TCP systems.
- **Headless** (`clusterIP: None`): Per-Pod DNS for StatefulSets; returns individual A-records.
kube-proxy maintains iptables/IPVS rules; the Service's virtual IP is stable even as Pod IPs change.
**Trade-offs**: NodePort not recommended for production (node-IP dependency, port uniqueness). ExternalName unsuitable for plain HTTP (Host header mismatch).
**Source**: Ch 3

---

## Ingress Host/Path Routing
**When to use**: Multiple HTTP/S apps sharing a single cluster entry point (one LoadBalancer IP).
**How**: Deploy one ingress controller (Nginx/Traefik) with its own LoadBalancer Service. Create `Ingress` objects with `spec.rules[].host` and `spec.rules[].http.paths`. Use `pathType: Exact` to allowlist specific paths (blocks `/metrics`, `/config`). TLS termination: add `spec.tls[].secretName` referencing a TLS Secret.
**Trade-offs**: Advanced features (sticky sessions, caching, rewrites) require controller-specific annotations — not portable across controllers. Switching controllers is a migration project. PathType support varies by controller version.
**Source**: Ch 15

---

## EFK Logging Pipeline
**When to use**: Multi-Pod, multi-namespace clusters where `kubectl logs` is insufficient for cross-cutting troubleshooting.
**How**: Deploy Fluent Bit as a DaemonSet with a HostPath volume mount to `/var/log/containers`. Configure an INPUT (tail), FILTER (kubernetes enrichment), and OUTPUT (Elasticsearch) in a ConfigMap. Apply `fluentbit.io/parser: <name>` annotation on Pods needing structured parsing. Use `grep` filters to drop low-priority entries centrally. Restart after ConfigMap changes with `kubectl rollout restart ds/fluent-bit`.
**Trade-offs**: Skipping the Kubernetes filter means no Pod labels or image metadata on log entries, making filtering by deployment difficult. Elasticsearch must be sized for log volume; run as StatefulSet in production.
**Source**: Ch 13

---

## Prometheus Pull / Exporter Pattern
**When to use**: Application and infrastructure observability across all cluster tiers.
**How**:
- **App with library**: Embed Prometheus client; expose `/metrics` at a declared `containerPort`. Prometheus auto-discovers via `kubernetes_sd_configs` (role: pod) + `relabel_configs` filtering by namespace.
- **Third-party app**: Add exporter sidecar (e.g., `nginx-prometheus-exporter`); annotate with `prometheus.io/port: "9113"`. Sidecar reaches main app via `localhost` (shared Pod network).
- **Platform layer**: Deploy `kube-state-metrics` (Deployment) and `cAdvisor` (DaemonSet); add as static or discovery-based scrape targets.
**Trade-offs**: Scrape Pod IPs directly, not Services — per-replica visibility is the entire point. Missing `containerPort` declaration = silent scrape failure.
**Source**: Ch 14

---

## RBAC Least-Privilege
**When to use**: Every role and binding, for both human users and in-cluster service accounts.
**How**: Create a dedicated `ServiceAccount` per app. Define a `Role` (namespace-scoped) or `ClusterRole` (cluster-wide or cross-namespace reuse) with explicit `resources` + `verbs`. Bind via `RoleBinding` (preferred) or `ClusterRoleBinding` (only when truly cluster-wide). Verify with `kubectl auth can-i <verb> <resource> --as system:serviceaccount:<ns>:<name>`.
**Trade-offs**: Using `ClusterRoleBinding` when `RoleBinding` suffices silently grants access to every namespace including `kube-system`. Accumulating roles on the `default` service account infects every Pod in the namespace.
**Source**: Ch 17

---

## SecurityContext + NetworkPolicy Defense-in-Depth
**When to use**: Every production workload — apply incrementally, tighten incrementally.
**How**:
- **NetworkPolicy**: Start with deny-all, carve explicit ingress/egress `podSelector` allow rules. Requires a compatible CNI (Calico/Cilium). Test enforcement with a live curl from a sleep Pod.
- **SecurityContext**: `automountServiceAccountToken: false`, `runAsNonRoot: true` (or `runAsUser: 65534`), `allowPrivilegeEscalation: false`, `capabilities.drop: [all]`, `readOnlyRootFilesystem: true` (use `emptyDir` for writable scratch).
- **Admission enforcement**: Use OPA Gatekeeper (`ConstraintTemplate` + `Constraint`) to enforce these settings cluster-wide as code-reviewed YAML policies.
**Trade-offs**: NetworkPolicy is inert without a compatible CNI — must be verified with live test. `readOnlyRootFilesystem` breaks apps that write to their own image directory; add `emptyDir` mounts for `/tmp` etc. Mutating webhooks can silently break root-only images.
**Source**: Ch 16

---

## Taints/Tolerations + Affinity for Workload Placement
**When to use**: Multi-arch clusters, compliance isolation, spreading replicas across failure domains, co-locating latency-sensitive services.
**How**:
- **Taints** (negative/node): `kubectl taint nodes <node> key=value:NoSchedule`. Add matching `tolerations:` block in Pod spec.
- **NodeAffinity** (positive/node): Use `requiredDuringSchedulingIgnoredDuringExecution` (hard, filter stage) or `preferredDuringSchedulingIgnoredDuringExecution` (soft, scoring stage).
- **PodAntiAffinity** (spread): `topologyKey: kubernetes.io/hostname` spreads replicas across nodes; `topology.kubernetes.io/zone` spreads across AZs.
**Trade-offs**: Toleration without nodeAffinity allows a Pod on the tainted node but doesn't force it there — combine both for strict compliance isolation. Required anti-affinity caps effective scale to the matching node count.
**Source**: Ch 19

---

## HPA Autoscaling
**When to use**: CPU-bound or traffic-driven stateless apps that need elastic capacity without manual intervention.
**How**: Deploy `metrics-server`. Create a `HorizontalPodAutoscaler` referencing a Deployment with `minReplicas`, `maxReplicas`, and `targetCPUUtilizationPercentage` (v1) or a `metrics:` + `behavior:` block (v2). Pod spec must declare `resources.requests.cpu` for percentage-based scaling.
**Trade-offs**: `maxReplicas` bounded by affinity/anti-affinity constraints — setting 10 replicas with unique-node anti-affinity on a 3-node cluster leaves 7 Pods Pending. Default 5-minute scale-down delay prevents flapping; tune via `behavior.scaleDown.stabilizationWindowSeconds`.
**Source**: Ch 19

---

## CRD + Operator / Reconcile Loop
**When to use**: Complex stateful applications (databases, message queues) or operational workflows too complex for standard Kubernetes objects.
**How**: Define a `CustomResourceDefinition` (APIExtensions group, with `openAPIV3Schema`). Write a controller that watches the CRD via Kubernetes API, checks existing state, and creates/deletes standard Kubernetes resources (Deployments, Services, Secrets) to match declared spec. Deploy CRD first; deploy instances after (CRD registration takes seconds). Controller must be idempotent and handle delete events to avoid orphaned resources.
**Trade-offs**: Deleting a CRD cascades to all instances — secure with RBAC. Operators are large dependencies; evaluate contributor activity before adopting for critical workloads. Build your own Operator only when operational complexity justifies it; admission controllers suffice for simpler policy enforcement.
**Source**: Ch 20

---

## Serverless Functions (Kubeless)
**When to use**: Rapid iteration where eliminating image build pipelines is more valuable than control; event-driven augmentation of existing apps without modifying them.
**How**: `kubeless function deploy <name> --runtime <lang> --handler <file.handler> --from-file <code>`. An init container compiles source (stored in a ConfigMap) into an EmptyDir shared with the app container. Create triggers: `HTTPTrigger` → Ingress, `CronJobTrigger` → CronJob, `NATSTrigger` → queue subscription. Functions subscribe to existing queues to add behavior without modifying producers.
**Trade-offs**: No resource limits by default — many function Pods risk node memory pressure and eviction. Init container compilation increases cold-start time vs. pre-built images. Platform-specific handler signatures make cross-platform migration harder without an abstraction layer (Serverless framework).
**Source**: Ch 21

---

## Helm Chart Packaging
**When to use**: Distributing, versioning, or parameterizing multi-resource applications for reuse across environments.
**How**: Structure a chart directory (`Chart.yaml`, `values.yaml`, `templates/`). Use Go-template syntax (`{{ .Values.key }}`, `{{ .Release.Name }}`) in manifests. Install: `helm install <release> <chart> --set key=val`. Upgrade safely: `helm get values <release> -o yaml > vals.yaml && helm upgrade -f vals.yaml --atomic <release> <chart> --version x.y.z`. Rollback: `helm rollback <release> <revision>`.
**Trade-offs**: `--atomic` automatically rolls back if any resource fails within `--timeout`. Omitting `--atomic` leaves resources in a mixed-revision state. Upgrade without re-specifying all custom values silently reverts settings to chart defaults — always export values first.
**Source**: Ch 10

---

## DaemonSet for Infrastructure Agents
**When to use**: Log collectors, metrics agents, node-local reverse proxies — any workload that must run exactly once per node.
**How**: Use `kind: DaemonSet` (no `replicas` field). The controller watches nodes joining/leaving and schedules one Pod per matching node. Use `nodeSelector` in the Pod spec to restrict to labeled node subsets. Control Pod updates via `updateStrategy.type: RollingUpdate` with `maxUnavailable`.
**Trade-offs**: Creating a DaemonSet before deleting a Deployment replacement avoids traffic gaps. Using HostPath shared volumes for apps that assume exclusive file access risks data corruption. `--cascade=false` orphans Pods for zero-downtime controller replacement.
**Source**: Ch 6, 13

---

## StatefulSet Ordered Rollout (Partitioned)
**When to use**: Clustered stateful apps (databases) where secondaries must be validated before touching the primary.
**How**: Set `updateStrategy.rollingUpdate.partition: N` in the StatefulSet spec. Only Pods with index ≥ N are updated. Validate secondaries, then lower partition to 0 via a second `kubectl apply` to update the primary. StatefulSet rollouts always proceed from highest index downward (primary is index 0, updated last by default).
**Trade-offs**: Requires explicit operator gate between each partition value change — no automatic propagation. `volumeClaimTemplates` changes require StatefulSet delete-and-recreate; plan storage schema before first deploy.
**Source**: Ch 8, 9
