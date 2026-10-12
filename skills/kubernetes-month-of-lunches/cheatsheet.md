# Cheatsheet

## Controller Decision Tree

**Which controller do I need?**
- Stateless app, scale for load, rolling updates → **Deployment**
- Need stable per-Pod identity, ordered start, per-Pod PVC → **StatefulSet** (not Deployment)
- One Pod per node (log agent, metrics, HA proxy) → **DaemonSet**
- Finite batch process that must run to completion → **Job**
- Recurring maintenance (backups, reports) → **CronJob** (owns Jobs)
- Never create a bare **ReplicaSet** directly — Deployments manage them for you

## Service Type Decision Tree

**How is this service reached?**
- Inter-Pod only, never external → **ClusterIP** (default; omit `type`)
- Dev/test external access via node IP:port → **NodePort** (avoid in production — IP fragility)
- External traffic, production → **LoadBalancer** (one cloud LB, same YAML everywhere)
- Alias for an external domain (TCP, not HTTP) → **ExternalName** (returns CNAME; breaks HTTP Host header)
- Route by hostname/path, many apps, one IP → **Ingress** in front of ClusterIP Services
- Need per-Pod DNS (clustered DB, primary/secondary) → **headless Service** (`clusterIP: None`) + StatefulSet

## Volume / Storage Decision Tree

**How long must data live?**
- Only while container runs → container writable layer (default, no config needed)
- Survives container restart, not Pod replacement; inter-container share → **emptyDir**
- Survives Pod replacement, single-node only → **hostPath** (never in multi-node production)
- Survives Pod replacement on any node → **PersistentVolume + PVC**
  - Admin pre-creates PV → static provisioning (`storageClassName: ""`)
  - PVC auto-creates PV via StorageClass → dynamic provisioning (cloud norm)
  - Per-replica independent PVC (StatefulSet) → **volumeClaimTemplates**

## Probe Decision Rules

- **Readiness probe** → controls routing (removes/adds Pod from Service endpoints); failure does NOT restart
- **Liveness probe** → controls restarts (kills container, Pod IP preserved); use for deadlock / permanent failure
- Always combine both: readiness alone → all Pods fail → zero endpoints → app offline
- Never make liveness probe depend on downstream services (DB, external API) → transient dep failure kills healthy Pod
- Set `initialDelaySeconds` to slow-start grace; set `failureThreshold ≥ 2` to avoid flapping
- Non-HTTP workloads: use `tcpSocket` for readiness, `exec` for liveness

### Readiness vs. Liveness

| Dimension | Readiness | Liveness |
|---|---|---|
| Failure action | Remove from Service endpoints | Kill + restart container |
| Pod replaced? | No | No (container only) |
| IP preserved? | Yes | Yes |
| Probe too aggressive | All endpoints drain → outage | Healthy slow-starts killed in loop |

## Update Strategy Trade-offs

| Strategy | Downtime | Dual-version | When |
|---|---|---|---|
| RollingUpdate (default) | None (tunable) | Yes — old+new run together | Most cases; production default |
| Recreate | Guaranteed | No — clean cutover | Hard schema migrations (rare) |
| Blue-Green (manual) | None | Yes | UX-breaking changes; doubles compute |
| OnDelete (DS/STS) | Per-Pod | No | Hardware-coupled teardown |

### maxSurge / maxUnavailable Effects

| Config | Effect |
|---|---|
| `surge:0, unavail:1` | Remove-first; brief reduced capacity; no extra nodes |
| `surge:1, unavail:0` | Create-first; full capacity maintained; needs spare node |
| `surge:1, unavail:1` | Parallel (fastest); ±1 capacity swing |
| Both `25%` (defaults) | Aggressive — bad image breaks 25% of fleet before detection |
| Both `0` | Rejected by API |

**Decision rules:**
- Zero-downtime with no spare capacity → `maxSurge:0, maxUnavailable:1`
- Guarantee full capacity during rollout → `maxSurge:1, maxUnavailable:0`
- Always set `minReadySeconds > 0` (catches fast-crash images that briefly look healthy)
- Kubernetes does NOT auto-rollback — run `kubectl rollout undo` manually

## ConfigMap vs. Secret vs. Delivery Method

| Dimension | ConfigMap | Secret |
|---|---|---|
| For | Non-sensitive config | Passwords, tokens, certs |
| Storage | Plain text in etcd | Base64-encoded; encrypt-at-rest optional |
| `kubectl describe` | Shows values | Hides values |
| Real security | RBAC | RBAC + encryption at rest |

| Delivery | Live update? | Precedence | Best for |
|---|---|---|---|
| `env` / `envFrom` | No — Pod must restart | `env` > `envFrom` | Simple scalar settings |
| Volume mount (file) | Yes (~2 min) | App-defined merge | Structured config (JSON/YAML/TOML) |

**Rule:** Mount Secrets as files (`defaultMode: 0400`), not env vars — env vars appear in crash dumps and are readable by all processes.

## RBAC Decision Rules

- Need namespace-scoped access → **Role + RoleBinding** (not ClusterRole + ClusterRoleBinding)
- Need cluster-scoped resources (Nodes, PVs, Namespaces) → **ClusterRole**
- Reuse same permission set across many namespaces → ClusterRole referenced by namespaced **RoleBinding** (scopes it down)
- Start from built-ins: `view` (read-only) → `edit` → `admin` → `cluster-admin` (last resort)
- Create a dedicated **ServiceAccount** per app; never accumulate roles on `default`
- `cluster-admin` handed to any workload/user = RBAC smell; rotate and narrow immediately

| Object | Scope | Can reference |
|---|---|---|
| Role | One namespace | — |
| ClusterRole | Cluster-wide | — |
| RoleBinding | One namespace | Role or ClusterRole (scoped to binding's namespace) |
| ClusterRoleBinding | All namespaces | ClusterRole only |

## Placement Decision Rules

- Reserve specialist nodes (GPU, compliance) → **taint node** + toleration on Pod (toleration = permission, not guarantee)
- Guarantee Pod lands on specific node type → **nodeSelector** or required **nodeAffinity** (AND with toleration)
- Spread replicas across failure zones → **preferred podAntiAffinity** with `topologyKey: topology.kubernetes.io/zone`
- Required anti-affinity on a 1-node cluster → Pods stay Pending forever (cap = node count)
- CPU-based elastic capacity → **HPA** (requires `metrics-server` + CPU `requests` on every Pod)
- HPA creates Pods; affinity rules still apply → anti-affinity caps `maxReplicas` to matching node count

### Taint Effects

| Effect | Behavior |
|---|---|
| `NoSchedule` | Hard filter — new Pods without toleration blocked |
| `PreferNoSchedule` | Soft scoring penalty only |
| `NoExecute` | Evicts already-running Pods without toleration |

## QoS Classes & Eviction Order (evicted first → last)

| Class | Condition | Evicted |
|---|---|---|
| BestEffort | No `requests` or `limits` set | First |
| Burstable | `requests` set but `requests < limits` | Second (by memory overage ratio) |
| Guaranteed | `requests == limits` for all resources | Last |

**Rule:** Set both `requests` and `limits` on every production container. Memory limit breach → `OOMKilled`; CPU limit breach → throttle (not killed).

## Tells & Smells (Fast Diagnostics)

| Symptom | Likely Cause | Fix |
|---|---|---|
| `CrashLoopBackOff` | Liveness probe too tight, OOMKill, or fatal app bug | Check `kubectl describe pod` events; widen `initialDelaySeconds` or memory limit; look for bug |
| `Pending` Pod | No node satisfies resources/affinity/taint | `kubectl describe pod` → "0/N nodes are available"; check taint/nodeSelector/HPA + affinity cap |
| Intermittent 5xx | Missing readiness probe → unhealthy Pod in Service endpoints | Add `readinessProbe` |
| App offline (no endpoints) | All replicas fail readiness, no liveness → no restarts | Add `livenessProbe` alongside readiness |
| Rollout stalls | Bad image; `maxUnavailable` limits propagation | `kubectl rollout status`; if stuck → `kubectl rollout undo` |
| `<unknown>` in HPA | `metrics-server` not installed or Pod has no CPU `requests` | Install metrics-server; add `resources.requests.cpu` |
| PVC stuck `Pending` | No matching PV and no default StorageClass | `kubectl get pvc` + `kubectl describe pvc` → check `storageClassName` |
| `cluster-admin` on workload SA | RBAC over-permission | Audit with `kubectl auth can-i "*" "*" --as <sa>` |

## StatefulSet vs. Deployment at a Glance

| Dimension | Deployment | StatefulSet |
|---|---|---|
| Pod names | Random suffix | Indexed (`db-0`, `db-1`) |
| Startup order | Parallel | Sequential 0→N |
| Scale-down order | Arbitrary | Reverse (N→0) |
| Per-Pod DNS | No (only via Service LB) | Yes via headless Service |
| Per-Pod PVC | Shared only | `volumeClaimTemplates` (own PVC per Pod) |
| Changing `volumeClaimTemplates` | N/A | Delete + recreate StatefulSet |

## kubectl Quick Reference

| Command | Purpose |
|---|---|
| `kubectl apply -f <file|dir|URL>` | Declarative deploy/update (idempotent) |
| `kubectl get <type> [-l sel] [-n ns] [-o wide\|yaml\|json]` | List resources |
| `kubectl describe <type> <name>` | Full details + events (primary debug tool) |
| `kubectl logs <pod> [--tail=N] [-l sel] [-c container]` | Container logs |
| `kubectl exec -it <pod> -- <cmd>` | Interactive shell in container |
| `kubectl scale deploy/<name> --replicas=N` | Imperative scale (update YAML too) |
| `kubectl rollout status deploy/<name>` | Stream rollout progress |
| `kubectl rollout history deploy/<name>` | List revisions |
| `kubectl rollout undo deploy/<name> [--to-revision=N]` | Rollback |
| `kubectl rollout pause/resume deploy/<name>` | Halt or resume in-flight rollout |
| `kubectl auth can-i <verb> <resource> [--as <user>] [-n ns]` | Check permissions |
| `kubectl config use-context <name>` | Switch cluster context |
| `kubectl config get-contexts` | List available contexts |
| `kubectl get events --sort-by='.lastTimestamp'` | Cluster-wide event stream |
| `kubectl top pods [-l sel]` | Live CPU/memory (requires metrics-server) |
| `kubectl label nodes <node> <key>=<val>` | Add node label (affinity/nodeSelector) |
| `kubectl taint nodes <node> <key>=<val>:<Effect>` | Taint node |
| `kubectl delete <type> <name> [--cascade=false]` | Delete; `--cascade=false` orphans children |
