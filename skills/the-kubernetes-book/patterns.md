# Patterns — The Kubernetes Book (2024), Nigel Poulton

Concrete techniques, design patterns, and operational methods.

## Declarative Manifest + Apply
**When to use**: All workload/object management; default for everything.
**How**: Describe desired state in YAML (apiVersion, kind, metadata, spec) → version-control it → `kubectl apply -f`. Re-apply edited files to update. Avoid imperative `create/run` except for quick tests.
**Trade-offs**: Auditable, repeatable, Git-friendly; small upfront verbosity vs imperative one-liners.

## Desired-State Reconciliation (Control Loops)
**When to use**: Any time you want the cluster to self-maintain.
**How**: Post desired state to API server → store in cluster store → a controller watches and continuously compares observed vs desired, taking action to converge. You declare *what*, not *how*.
**Trade-offs**: Resilient and hands-off; convergence is eventual/async, not instant.

## Rolling Update + Versioned Rollback
**When to use**: Zero-downtime updates of stateless apps (Deployments).
**How**: Edit image/tag in manifest → `apply`. Deployment creates a new ReplicaSet, scales it up while scaling old down per `maxSurge`/`maxUnavailable`. Each rollout is versioned; `kubectl rollout undo` reverts to prior ReplicaSet. Keep old ReplicaSets for history.
**Trade-offs**: Smooth, reversible; needs backward-compatible app versions and readiness probes to gate traffic.

## Self-Healing via Controllers
**When to use**: Survive Pod/node failures automatically.
**How**: Run Pods through a controller (Deployment/StatefulSet), not bare. Controller watches replica count; on failure it reschedules to restore desired count. Pod restartPolicy + probes handle in-Pod failures.
**Trade-offs**: Recovers replacements, not the same Pod — state must live elsewhere; bare Pods get no healing.

## Label-Selector Loose Coupling
**When to use**: Connect Services↔Pods, Deployments↔Pods, NetworkPolicies↔targets without hardcoding identities.
**How**: Tag Pods with `metadata.labels` → match via `selector` (Service) or `matchLabels` (controllers). Coupling is by label match, fully dynamic as Pods come/go.
**Trade-offs**: Flexible, ephemeral-friendly; mismatched/typo'd labels silently break wiring — verify endpoints.

## Service Type Selection
**When to use**: Exposing a set of Pods at a stable address.
**How**: **ClusterIP** = internal-only stable VIP+DNS (default, mesh/east-west). **NodePort** = ClusterIP + port on every node (dev/legacy external). **LoadBalancer** = NodePort + cloud LB (internet-facing single app). Service gives a name/IP/port that never changes; EndpointSlices track healthy Pods.
**Trade-offs**: LoadBalancer = 1 cloud LB per Service (cost, quotas) → prefer Ingress for many web apps.

## Ingress Host/Path Routing (L7)
**When to use**: Expose many HTTP apps behind one cloud load balancer.
**How**: Deploy an ingress controller → write Ingress rules mapping `host`/`path` → backend ClusterIP Service. One LB fans out by inspecting HTTP host header and path.
**Trade-offs**: Big LB cost savings; HTTP/HTTPS only, controller is a shared dependency. Service mesh may make it redundant.

## ConfigMap / Secret Injection
**When to use**: Decouple config from image (12-factor).
**How**: Store non-sensitive config in ConfigMap, sensitive in Secret. Inject as: env vars (`valueFrom`), container args, or mounted volume (best — supports live updates). Same image, env-specific config.
**Trade-offs**: Reuse + cleaner changes; Secrets are only base64-encoded (not encrypted) at rest by default — add encryption/external KMS.

## StatefulSet Sticky Identity + volumeClaimTemplates
**When to use**: Stateful apps needing stable name/network/storage (DBs, KV stores).
**How**: StatefulSet gives ordered, predictable Pod names (`app-0,1,2`), stable DNS via a headless Service, and per-Pod PVCs from `volumeClaimTemplates`. Pods created/scaled/deleted in order; a rescheduled Pod reattaches its same volume.
**Trade-offs**: Strong identity guarantees; slower ordered ops, more complex than Deployments — use only when state demands it.

## Dynamic Volume Provisioning (StorageClass + PVC)
**When to use**: On-demand persistent storage without manual PV creation.
**How**: Admin defines StorageClass (CSI provisioner + params + reclaimPolicy). App submits a PVC referencing the class with size + accessMode → PV auto-created and bound. Pod mounts the PVC.
**Trade-offs**: Self-service, no pre-provisioning; reclaimPolicy (Delete vs Retain) governs data safety on PVC deletion — pick deliberately.

## RBAC Least-Privilege
**When to use**: Scope what users/Pods can do on the API.
**How**: Create a ServiceAccount (for Pods) → define a Role (namespaced) or ClusterRole listing allowed verbs on resources → bind with RoleBinding/ClusterRoleBinding. Grant minimum verbs; deny by default.
**Trade-offs**: Tight blast-radius control; rule sprawl and over-broad ClusterRoles are common pitfalls — audit bindings.

## CRD API Extension
**When to use**: Add custom object types / operator patterns to the API.
**How**: Register a CustomResourceDefinition → custom resources become first-class API objects (kubectl, RBAC, watch). Pair with a custom controller to reconcile them.
**Trade-offs**: Extends K8s natively without forking; you own the controller lifecycle and versioning.

## STRIDE Threat Modeling
**When to use**: Systematically surface cluster vulnerabilities.
**How**: Walk six categories — **S**poofing, **T**ampering, **R**epudiation, **I**nformation disclosure, **D**enial of service, **E**levation of privilege — mapping each to cluster surfaces (API server, etcd, kubelet, network). Add controls per finding; remember one threat enables another.
**Trade-offs**: Structured coverage; no model is exhaustive — seeds ideas, not guarantees.

## Defense-in-Depth Security (Build/Deploy/Runtime)
**When to use**: Whole-lifecycle hardening.
**How**: Layer controls across supply chain (signed/scanned images, SBOM), deploy (admission control, policy, RBAC), and runtime (workload isolation, monitoring/audit). Assume breach; stack independent controls.
**Trade-offs**: No single control suffices; more controls = more operational overhead.

## NetworkPolicy Isolation
**When to use**: Restrict Pod-to-Pod traffic (Namespaces are NOT a network boundary).
**How**: Default-deny, then allow specific ingress/egress by Pod/Namespace label selectors and ports. Requires a CNI that enforces policy.
**Trade-offs**: Real network segmentation; ineffective if CNI doesn't enforce — verify support.

## RuntimeClass for Wasm
**When to use**: Run Wasm workloads alongside containers.
**How**: On containerd nodes, install a Wasm runtime + shim → label those nodes → define a RuntimeClass → reference it via `spec.runtimeClassName` in the Pod and schedule onto labeled nodes (nodeSelector/affinity).
**Trade-offs**: Tiny, fast, portable workloads; needs node-level runtime setup and scheduling discipline.
