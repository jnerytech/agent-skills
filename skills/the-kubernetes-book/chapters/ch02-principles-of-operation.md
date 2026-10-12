# Chapter 2: Kubernetes principles of operation

## Core Idea
Kubernetes is two things at once: a **cluster** (one or more nodes providing CPU/memory/resources) and an **orchestrator** (a system that intelligently deploys and manages apps — placing them across nodes/failure zones, self-healing, scaling, and doing zero-downtime rolling updates). All workloads (containers, VMs, Wasm) must be wrapped in **Pods** to run, and the system is driven by the **declarative model**: you describe desired state in YAML, post it to the API server, and controllers continuously reconcile observed state toward it.

## Key Concepts
- **Cluster**: One or more nodes (physical, VM, or cloud; ARM or AMD64/x86-64) supplying resources to apps; two node types — control plane and worker.
- **Control plane node**: Runs every control plane service (API server, scheduler, controllers, cluster store); implements the "brains." Must be Linux. Run 1 for labs, 3 or 5 for HA.
- **Worker node**: Runs user applications. Linux or Windows. A single cluster can mix both.
- **Desired state**: What you want (declared in YAML manifest); recorded as a "record of intent" in the cluster store.
- **Observed state**: What you actually have right now (a.k.a. actual/current state).
- **Reconciliation**: Background process controllers run to keep observed state matching desired state.
- **Pod**: Atomic unit of scheduling in Kubernetes; a thin wrapper/shared execution environment for one or more containers.
- **Sidecar**: Helper container in the same Pod as the main app container (e.g., service mesh providing encryption + telemetry).
- **Deployment**: Higher-level controller wrapping a Pod; adds self-healing, scaling, rolling updates, and versioned rollbacks for stateless apps.
- **Service**: API object providing a stable name/IP/port (front end) that load balances across a dynamic set of healthy Pods (back end, selected by labels).

## Frameworks Introduced
- **Declarative model (vs. imperative)**: Describe an end-state, not the steps to reach it.
  - When to use: Kubernetes supports both but prefers declarative — it's platform-agnostic, integrates with version control/GitOps, and enables self-healing, autoscaling, and rolling updates.
  - How (6 steps): 1) Describe desired state in a YAML manifest; 2) post it to the API server (usually via `kubectl`); 3) it's persisted to the cluster store as a record of intent; 4) a controller notices observed ≠ desired; 5) the controller reconciles the difference; 6) the controller keeps running in the background to reconcile future drift.
  - Contrast: imperative model requires complex platform-specific scripts to reach an end-state; declarative is a simple platform-agnostic description of the end state.
- **Object nesting (packaging)**: Each wrapping layer adds value.
  - How: container wraps the app + dependencies → Pod wraps the container so it can run on Kubernetes → Deployment wraps the Pod and adds self-healing, scaling, etc. Post the Deployment YAML to the API server as desired state.

## Mental Models
- **Courier analogy**: Kubernetes is like a shipping courier. You package and label goods (wrap your app in a Pod); the courier handles logistics — which planes/trucks (which nodes), hand-offs (networking), delivery (volumes/scheduling). Add-on services (insurance, proof of delivery) map to controllers that add value (health, autoscaling).
- **Pods are mortal**: Created, live, die. A replacement Pod always has a NEW ID and NEW IP — never the same one resurrected. Forces loosely-coupled, failure-immune app design.
- **Pods are immutable**: Never log on and change a running Pod. "Updating a Pod" always means delete-and-replace. Fits GitOps workflows.
- **Pod as unit of scaling**: Scale up = add more Pods; scale down = delete Pods. You NEVER scale by adding containers to an existing Pod.
- **Single responsibility via multi-container Pods**: Keep the main app simple; push cross-cutting concerns (encryption, telemetry, log scraping) into sidecars in the same Pod.

## Anti-patterns
- Running user apps on control plane nodes in production (allowed, but force them onto worker nodes so the control plane focuses on cluster ops).
- Using an even number of etcd replicas — etcd prefers an ODD number to avoid split-brain (no quorum/majority). On split-brain, etcd goes read-only; apps keep running but cluster updates are blocked.
- Treating a highly-available cluster store as a substitute for backup/recovery — you still need real backups of etcd.
- Logging into a running Pod to modify it (violates immutability) — replace instead.
- Adding containers to a Pod to scale (wrong unit of scaling).
- Connecting clients directly to individual Pod IPs — IP churn from rollouts/scaling/failures makes them unreliable; use a Service.

## Reference Tables

### Control plane vs. worker node components
| Component | Plane | Role |
|---|---|---|
| API server | Control plane | Front end of Kubernetes; RESTful API over HTTPS; all create/query requests (even internal) pass through it; handles authN/authZ. |
| Cluster store (etcd) | Control plane | Only stateful component; holds desired state of all apps/components; etcd distributed DB, odd replicas, RAFT consensus for write consistency. |
| Controllers + controller manager | Control plane | Background watch loops reconciling observed→desired (Deployment, StatefulSet, ReplicaSet controllers). Controller manager spawns/manages individual controllers. |
| Scheduler | Control plane | Watches API server for new tasks, identifies capable nodes, assigns tasks. |
| Cloud controller manager | Control plane | (Cloud only) Integrates cluster with cloud services — instances, load balancers, storage. |
| Kubelet | Worker | Main node agent; watches API server for tasks, instructs runtime to execute them, reports task status back. |
| Runtime (containerd) | Worker | Executes tasks: pulls images, starts/stops containers. containerd is default; CRI-O on OpenShift; Docker no longer supported. |
| kube-proxy | Worker | Implements cluster networking; load balances traffic to tasks on the node. |

### Scheduler node selection (3 steps + criteria)
1. Watch API server for new tasks. 2. Identify capable nodes. 3. Assign tasks to nodes.
- Filtering = predicate checks: taints, affinity/anti-affinity rules, network port availability, available CPU/memory (incapable nodes ignored).
- Ranking = points-based: has the image already, available CPU/memory, current task count; highest-scoring nodes win.
- No suitable node → task marked **pending**; if node autoscaling is enabled, a pending task triggers a cluster autoscaling event that adds a node.

## Worked Example
**Desired-state reconciliation — node failure:** Deploy an app from YAML requesting **10 replicas**. A node running 2 replicas fails → observed state drops to **8** ≠ desired **10**. A controller notices the diff and schedules **2 new** replicas to return to 10. No human action.

**Declarative app update:** Edit one line of YAML to point at an updated image; post to Kubernetes. The relevant controller notices observed ≠ desired and replaces old-version replicas with new-version replicas (rolling update). Imperatively this would need complex scripts to manage/monitor/health-check; declaratively it's a single YAML line.

**Deploy/update request path (API server):** 1) Describe requirements in YAML; 2) POST to API server; 3) authenticate + authorize; 4) persist to cluster store; 5) schedule to the cluster.

**Multi-container Pod networking:** Both containers share the Pod's IP (e.g., main app on `10.0.10.15:8080`, sidecar on `10.0.10.15:5005`); container-to-container traffic inside the Pod uses `localhost`. All containers in a Pod schedule to the same node; Pod start is atomic (marked running only when ALL containers start).

## Key Takeaways
1. Kubernetes = cluster + orchestrator; control plane (Linux, 3 or 5 for HA) holds the brains, workers (Linux/Windows) run user apps.
2. The API server is the single front door — everything, including internal services, communicates through it; etcd is the only stateful piece.
3. Everything runs inside Pods (the atomic scheduling unit); Pods are mortal, immutable, and the unit of scaling.
4. Controllers are background watch loops that continuously reconcile observed state toward desired state — this is what delivers self-healing, autoscaling, and rollouts.
5. Prefer the declarative model: change YAML, post it, let Kubernetes do the rest — GitOps-friendly and platform-agnostic.
6. Wrap Pods in Deployments for self-healing/scaling/rollouts, and front them with Services for a stable name/IP/port that load balances across healthy Pods despite IP churn.

## Connects To
- **Ch. 3+ (hands-on)**: Building/installing clusters; using `kubectl` to post manifests.
- **Pods chapter**: Deeper Pod anatomy, multi-container patterns, lifecycle.
- **Deployments chapter**: ReplicaSets, rolling updates, versioned rollbacks.
- **Services chapter**: ServiceTypes, label selectors, internal vs. external networking, load balancing.
- **Wasm chapter**: Alternative runtimes beyond containerd.
- **GitOps/configuration management**: Declarative model + immutable Pods underpin version-controlled, reconciliation-driven workflows.
