# Chapter 19: Controlling Workload Placement and Automatic Scaling

## Core Idea

The Kubernetes scheduler decides where Pods run. Chapter 19 gives you control over that decision through four mechanisms that compose: taints/tolerations (exclude unsuitable nodes), node selectors and affinity (require or prefer specific nodes or co-location with other Pods), HorizontalPodAutoscaler (adjust replica count based on load), and priority classes (protect important Pods when nodes are under resource pressure). Together they let you express placement constraints, automate capacity, and define a graceful degradation order for overloaded nodes.

---

## Frameworks Introduced

- **Taints and Tolerations**
  - What: Taints mark a node as unsuitable for general work; tolerations on a Pod spec acknowledge that mark.
  - When: Reserve nodes for special workloads (GPU, compliance boundary, disk type) or protect control-plane nodes from app traffic.
  - How: `kubectl taint nodes <node> key=value:Effect`; add matching `tolerations:` block in Pod spec.
  - Why-or-failure: `NoSchedule` is a hard filter — new Pods without a toleration are blocked. `PreferNoSchedule` is soft (scoring penalty only). Neither guarantees a Pod lands on the tainted node; use nodeSelector/affinity for positive guarantees.

- **Node Affinity / Pod Affinity / Pod Anti-Affinity**
  - What: Rich label-based placement rules supporting `In`/`NotIn`/`Exists` operators, multiple OR/AND clauses, and topology scoping.
  - When: Multi-arch clusters, co-location for latency reduction, spreading replicas across failure domains.
  - How: `affinity:` block in Pod spec under `nodeAffinity`, `podAffinity`, or `podAntiAffinity`; combine `requiredDuringScheduling…` (hard) with `preferredDuringScheduling…` (soft).
  - Why-or-failure: Required rules leave Pods permanently pending if no node satisfies them; always pair with a preferred fallback where possible.

- **HorizontalPodAutoscaler (HPA)**
  - What: A separate Kubernetes object that monitors a scale target (Deployment/StatefulSet) and adjusts replica count to hit a metric target.
  - When: CPU-bound or request-rate-driven apps that need elastic capacity without manual intervention.
  - How: Deploy `metrics-server`, define an HPA object pointing at the Deployment with `minReplicas`, `maxReplicas`, and target metric; v2 spec adds custom metrics and tunable `behavior`.
  - Why-or-failure: Without `metrics-server`, HPA reports `<unknown>` and never acts. Pod spec must include CPU `requests` for percentage-based scaling to be meaningful.

---

## Key Concepts

1. **Scheduler two-phase process**: filtering (exclude unsuitable nodes) then scoring (rank remaining nodes). Taints/nodeSelectors act in filtering; preferred affinity rules act in scoring.
2. **Taint effects**: `NoSchedule` (hard block, filter stage), `PreferNoSchedule` (soft penalty, scoring stage), `NoExecute` (evicts already-running Pods without a toleration).
3. **Tolerations vs. nodeSelector**: tolerations express willingness to run on a node type; nodeSelector asserts a positive requirement. They complement each other and can appear together in one Pod spec.
4. **nodeAffinity syntax nuance**: `requiredDuringSchedulingIgnoredDuringExecution` is a hard rule (filter stage); `preferredDuringSchedulingIgnoredDuringExecution` is a weighted soft rule (scoring stage). The `IgnoredDuringExecution` suffix means existing Pods are not evicted if labels change after scheduling.
5. **Multiple matchExpressions in required rules are AND; multiple nodeSelectorTerms are OR.** In preferred rules, multiple matchExpressions are AND; multiple preference entries are OR.
6. **Topology key**: scopes Pod affinity/anti-affinity to a level of physical layout (hostname = same node, zone = same availability zone, region = same region). `kubernetes.io/hostname` is always present and unique per node.
7. **metrics-server**: Lightweight cluster add-on that scrapes current CPU/memory from kubelets. Not included by default in Docker Desktop or Kind. Required for `kubectl top` and HPA to function.
8. **HPA v1 vs. v2 spec**: v1 has `targetCPUUtilizationPercentage` and fixed scaling behavior (scale-up every 15 s, scale-down after 5 min). v2 (`autoscaling/v2beta2`) exposes a generic `metrics:` section (including Prometheus) and a `behavior:` block to tune stabilization windows and scaling policies.
9. **Pod eviction (preemption)**: When a node's available memory or disk falls below the kubelet's eviction threshold, Kubernetes adds a taint to the node and stops containers of selected Pods, freeing resources. Evicted Pods remain as objects for forensics; controllers create replacements.
10. **Priority classes**: Integer-valued `PriorityClass` objects (`scheduling.k8s.io/v1`) that the kubelet uses to rank Pods for eviction. Higher value = more protected. Pods reference a class via `priorityClassName` in the Pod spec. When multiple Pods are eligible, Kubernetes evicts the worst offenders by memory-over-request ratio among equal-priority Pods.

---

## Mental Models

1. **Negative vs. positive scheduling signals**: Taints + tolerations express something negative about the node ("this node has spinning disks; avoid it unless you can cope"). Affinity + nodeSelector express something positive ("I need an Intel node in the EU zone"). Both can coexist in one Pod spec, and they operate at different scheduler stages. Mixing them provides the tightest placement control.

2. **HPA as a control loop**: The HPA measures average metric across all current Pods, compares against a target, and nudges the replica count up or down every 15 seconds. It is deliberately conservative: it waits (default 5 min for scale-down) before acting to avoid flapping. The v2 `behavior:` block exposes those waits as first-class parameters, letting you shape the control loop for bursty vs. steady workloads.

3. **Eviction as a safety valve, not a feature**: Preemption is the cluster's last resort. Proper sizing (resource `requests`/`limits`), HPA, and cluster autoscaler should prevent it. Priority classes shift which Pods are sacrificed first, not whether eviction happens. A continuous eviction/creation loop signals a fundamentally under-resourced cluster.

4. **Affinity rules and HPA interact**: HPA adds replicas, but those replicas must satisfy every placement rule in the Pod spec. A required anti-affinity that demands unique nodes caps effective scale to the number of nodes in the cluster, regardless of `maxReplicas`.

---

## Anti-patterns

- **Tolerations without nodeSelector for compliance isolation**: A toleration allows a Pod to run on a tainted node but does not prevent it from running elsewhere. For strict PCI or data-sovereignty isolation you must combine a taint on the target nodes with a `nodeSelector` (or required `nodeAffinity`) on the Pod spec.
- **Required anti-affinity on a single-node cluster**: Pods waiting to replace an existing Pod can never schedule because the existing Pod already occupies the only node. The Deployment ends up managing two ReplicaSets simultaneously, and rollouts stall.
- **Missing CPU `requests` with HPA**: HPA expresses utilization as a percentage of requested CPU. A Pod with no `requests` makes the percentage undefined; HPA may scale erratically or not at all.
- **Ignoring affinity when setting `maxReplicas`**: Setting `maxReplicas: 10` on a Deployment with required node anti-affinity across a 3-node cluster means at most 3 Pods can ever run. The excess replicas stay pending forever, masking the real constraint.
- **Deploying metrics-server in production clusters that already have it**: Some distributions (K3s) include it; others (Docker Desktop, Kind) do not. Deploying a second instance causes conflicts. Always check with `kubectl top nodes` first.
- **No priority classes in mixed-criticality clusters**: Without priority classes, eviction order is determined solely by memory-over-request ratio, which may sacrifice critical workloads before low-importance batch jobs.

---

## Code Examples

**nodeSelector combined with toleration (listing 19.2)**
```yaml
spec:
  containers:
    - name: sleep
      image: kiamol/ch03-sleep
  tolerations:
    - key: "kiamol-disk"
      operator: "Equal"
      value: "hdd"
      effect: "NoSchedule"
  nodeSelector:
    kubernetes.io/arch: amd64
```

**Taint a node (CLI)**
```bash
kubectl taint nodes --all kiamol-disk=hdd:NoSchedule
```

**nodeAffinity — required rule covering dual label namespace (listing 19.3)**
```yaml
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
        - matchExpressions:
            - key: kubernetes.io/arch
              operator: In
              values:
                - amd64
        - matchExpressions:
            - key: beta.kubernetes.io/arch
              operator: In
              values:
                - amd64
```

**podAffinity — collocate web with API (listing 19.5)**
```yaml
affinity:
  podAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      - labelSelector:
          matchExpressions:
            - key: app
              operator: In
              values:
                - numbers
            - key: component
              operator: In
              values:
                - api
        topologyKey: "kubernetes.io/hostname"
```

**HPA v1 — CPU-based autoscaling (listing 19.6)**
```yaml
apiVersion: autoscaling/v1
kind: HorizontalPodAutoscaler
metadata:
  name: pi-cpu
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: pi-web
  minReplicas: 1
  maxReplicas: 5
  targetCPUUtilizationPercentage: 75
```

**HPA v2 — tunable scale-down behavior (listing 19.7)**
```yaml
metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 75
behavior:
  scaleDown:
    stabilizationWindowSeconds: 30
    policies:
      - type: Percent
        value: 50
        periodSeconds: 15
```

**PriorityClass — low-priority eviction candidate (listing 19.8)**
```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: kiamol-low
value: 100
globalDefault: true
description: "Low priority-OK to be evicted"
```

---

## Reference Tables

### nodeSelector vs. Affinity

| Feature | nodeSelector | nodeAffinity |
|---|---|---|
| Matching | Equality only | `In`, `NotIn`, `Exists`, `DoesNotExist`, `Gt`, `Lt` |
| Multiple criteria | AND of all key-value pairs | AND within `matchExpressions`, OR across `nodeSelectorTerms` |
| Hard vs. soft | Hard only | Hard (`required…`) or soft (`preferred…`) with weights |
| Label namespace portability | No — one key per entry | Yes — multiple selector terms cover old and new prefixes |
| Verbosity | Low | High |

### Taints/Tolerations vs. Affinity

| Dimension | Taints + Tolerations | Affinity / Anti-affinity |
|---|---|---|
| Signal direction | Negative (node repels Pods) | Positive (Pod attracted to / repelled from nodes or Pods) |
| Guarantee type | Exclusion (toleration required to enter) | Inclusion or preference |
| Pod-to-Pod relationship | No | Yes (`podAffinity`, `podAntiAffinity`) |
| Scheduler phase | Filtering (NoSchedule) or Scoring (PreferNoSchedule) | Filtering (required) or Scoring (preferred) |
| Good for | Reserving specialist nodes | Colocation, spreading, architecture selection |

### HPA v1 vs. Cluster Autoscaler

| Dimension | HPA (Pod autoscaler) | Cluster Autoscaler |
|---|---|---|
| What scales | Replica count (Pods) | Node count |
| Scope | In-cluster; works anywhere | Cloud-provider specific |
| Metrics source | metrics-server (or custom) | Pending Pod queue |
| Config object | `HorizontalPodAutoscaler` | Provider-specific tooling |
| Complementary | Yes — HPA creates pending Pods; cluster autoscaler adds nodes to absorb them | Yes — both work together in cloud environments |

---

## Worked Example

**Scenario: Spread API replicas across zones, then autoscale under load**

1. Label nodes with zone information (or confirm cloud labels exist):
   ```bash
   kubectl label node node-1 topology.kubernetes.io/zone=eu-west-1a
   kubectl label node node-2 topology.kubernetes.io/zone=eu-west-1b
   ```

2. Add a taint to reserve GPU nodes for the model-serving workload:
   ```bash
   kubectl taint nodes gpu-node workload=gpu:NoSchedule
   ```

3. Deploy the API Deployment with required node affinity (EU region) and preferred Pod anti-affinity (spread across zones):
   ```yaml
   affinity:
     nodeAffinity:
       requiredDuringSchedulingIgnoredDuringExecution:
         nodeSelectorTerms:
           - matchExpressions:
               - key: topology.kubernetes.io/region
                 operator: In
                 values:
                   - eu-west-1
     podAntiAffinity:
       preferredDuringSchedulingIgnoredDuringExecution:
         - weight: 100
           podAffinityTerm:
             labelSelector:
               matchExpressions:
                 - key: app
                   operator: In
                   values:
                     - numbers-api
             topologyKey: topology.kubernetes.io/zone
   ```
   The required nodeAffinity ensures all Pods land in the EU region. The preferred podAntiAffinity nudges the scheduler to spread replicas across zones without blocking scheduling if only one zone is available.

4. Deploy metrics-server if not present, then create the HPA:
   ```yaml
   apiVersion: autoscaling/v1
   kind: HorizontalPodAutoscaler
   metadata:
     name: numbers-api
   spec:
     scaleTargetRef:
       apiVersion: apps/v1
       kind: Deployment
       name: numbers-api
     minReplicas: 2
     maxReplicas: 5
     targetCPUUtilizationPercentage: 50
   ```

5. Verify placement and scaling under load:
   ```bash
   kubectl get pods -l app=numbers-api -o wide   # confirm zone spread
   kubectl get hpa numbers-api                   # watch replica count
   kubectl top pods -l app=numbers-api           # confirm CPU metrics
   ```

6. When load spikes above 50% average CPU, the HPA adds replicas every 15 seconds (up to 5). The new Pods must also satisfy the EU region affinity; if the maximum zone-count is 3 but `maxReplicas` is 5, two replicas will share a zone (preferred rule, not required). Scale-down waits 5 minutes by default before reducing replicas.

---

## Key Takeaways

1. Taints filter out nodes for Pods that don't tolerate them; tolerations grant permission but not priority. Combine with nodeSelector or nodeAffinity for a positive guarantee of placement.
2. `requiredDuringScheduling…` rules block scheduling if unmet; `preferredDuringScheduling…` rules penalize but never block. Default to preferred unless the constraint is a hard operational requirement (compliance, architecture mismatch).
3. Pod affinity/anti-affinity uses the same syntax as node affinity but matches on labels of running Pods, not node labels. The topology key determines the scope (node, zone, region).
4. The HPA is a separate object that watches a Deployment via metrics-server; it scales the replica count, not the Pod spec. All placement rules in the Pod spec still apply to every new replica.
5. HPA v2 unlocks custom metric sources (Prometheus) and tunable `behavior` for scale-up and scale-down rates — important for bursty workloads where the default 5-minute scale-down delay is too slow.
6. Eviction is a safety mechanism, not a design feature. Priority classes protect critical workloads during pressure events; resource `requests` in every Pod spec ensure the kubelet can rank eviction candidates rationally.
7. These features interact: HPA-driven replicas must satisfy affinity rules; anti-affinity caps effective scale to the number of matching nodes; eviction order depends on priority class and resource overage. Model your cluster capacity with all constraints active before setting `maxReplicas` or required affinity.

---

## Connects To

- **Chapter 17** — Node labels and CPU architecture selectors; control-plane taint that isolates master nodes from workloads. Chapter 19 builds directly on those concepts.
- **Chapter 16** — NetworkPolicy objects (separate object, decoupled from Pod spec) — the same architectural pattern used by HPA.
- **Chapter 14** — Prometheus metrics collection and cluster dashboards; HPA v2 can use Prometheus as a custom metric source; node memory pressure indicators were added to the dashboard in ch14.
- **Chapter 8** — StatefulSets with multiple replicas; the chapter notes that without anti-affinity all replicas may land on the same node, defeating the purpose of replication.
- **Resource Quotas / LimitRanges** (referenced in scheduling context) — namespace-level constraints that feed into the scheduler's filtering stage alongside affinity rules.
- **Cluster Autoscaler** — Cloud-provider tooling that provisions new nodes when Pods are pending due to insufficient cluster capacity; complements HPA (HPA creates pending Pods; cluster autoscaler adds nodes to schedule them).
