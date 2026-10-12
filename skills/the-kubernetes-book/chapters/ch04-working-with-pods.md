# Chapter 4: Working with Pods

## Core Idea
Every app on Kubernetes runs inside a **Pod** — deploy, terminate, scale, and update all operate on Pods. Pods are the atomic unit of scheduling: they wrap one or more containers (also VMs, serverless functions, Wasm), provide a shared execution environment, and augment workloads with scheduling, health probes, restart policies, and more. You define Pods in declarative YAML but usually deploy them via higher-level workload controllers.

## Frameworks Introduced
- **Pod as abstraction layer**: Pods abstract the workload type / use when running heterogeneous workloads (containers, VMs via KubeVirt, serverless via Knative, Wasm) side-by-side / Kubernetes manages Pods without caring what's inside; VMs run in a `VirtualMachineInstance` (VMI) variant.
- **Init container pattern**: Prepare/initialize the environment before the main app / use for one-time setup (wait for a remote API, clone a repo) / defined under `spec.initContainers`; guaranteed to run once and complete before `spec.containers` start.
- **Sidecar pattern**: Augment an app without modifying it / use for log scraping, content sync, service-mesh proxying / regular container under `spec.containers` running the full Pod lifecycle (no formal API support yet — alpha in 1.28).

## Key Concepts
- **Abstraction layer** — Pods hide workload-type details so Kubernetes deploys/manages them uniformly.
- **Shared execution environment** — all containers in a Pod share filesystem/volumes (mnt), network stack (net), memory (IPC), process tree (pid), and hostname (uts).
- **pod network** — flat Layer-2 overlay spanning all nodes; every Pod talks to every other Pod directly. Implemented by a CNI plugin (e.g., Cilium) chosen at build time.
- **pause container** — (implied infra container) holds the Pod's namespaces so containers can share them.
- **Mortal** — a Pod runs, terminates, and is deleted; it is never restarted (replaced instead).
- **Immutable** — you cannot modify a running Pod; change = create new + delete old. Applies at object level (Pod config) and app level (container filesystem — your responsibility).
- **static Pods** — deployed directly from a manifest, managed only by the local kubelet; cannot self-heal across nodes, scale, or roll updates.
- **Atomic deployment** — a Pod only serves requests once *all* its containers are up.
- **Resource requests vs limits** — requests = minimums (for scheduling, reserved/guaranteed); limits = maximums (capped by kubelet/runtime).

## Mental Models
- "Restart the Pod" always means **replace it with a new one** (new UID, new IP, no state) — happens on node failure, eviction, scaling, updates, rollbacks.
- Kubernetes never restarts Pods, but the kubelet *can* restart individual **containers** on the same node (governed by `spec.restartPolicy`).
- Put containers in the same Pod only if they must share resources (memory, volume, network); if you only need co-scheduling, use separate Pods + affinity rules.
- YAML manifests are "empathy as code" — self-documenting app requirements (ports, CPU/memory) for dev and ops.

## Anti-patterns
- Making changes to a live Pod (e.g., `apk add curl` inside an exec session) — violates immutability; OK only for demos.
- Omitting resource requests/limits — scheduler can't size the node and may overload it.
- Cramming unrelated workloads into one Pod just to land them on the same node.
- Relying on static Pods for production apps (no self-healing/scaling/rollouts).

## Code Examples
Single-container Pod manifest (`pod.yml`):
```yaml
kind: Pod
apiVersion: v1
metadata:
  name: hello-pod
  labels:
    zone: prod
    version: v1
spec:
  containers:
  - name: hello-ctr
    image: nigelpoulton/k8sbook:1.0
    ports:
    - containerPort: 8080
    resources:
      limits:
        memory: 128Mi
        cpu: 0.5
```
Four top-level fields: `kind`, `apiVersion`, `metadata`, `spec`. If you specify only `limits`, Kubernetes auto-sets `requests` to match.

Core kubectl workflow:
```bash
kubectl apply -f pod.yml                 # pod/hello-pod created
kubectl get pods                         # NAME READY STATUS RESTARTS AGE
kubectl get pods -o wide                 # extra columns
kubectl get pods hello-pod -o yaml       # full spec (desired) + status (observed)
kubectl describe pod hello-pod           # formatted overview + lifecycle Events
kubectl logs hello-pod                   # logs from first container
kubectl logs logtest --container syncer  # logs from a named container
kubectl exec hello-pod -- ps             # remote command execution
kubectl exec -it hello-pod -- sh         # interactive exec session
kubectl edit pod hello-pod               # immutable fields rejected on save
kubectl delete pod hello-pod initpod git-sync
```
**What it demonstrates**: full Pod lifecycle from the CLI — deploy, inspect desired vs observed state, read logs, run/shell into containers, and delete. `-o yaml` reveals defaults Kubernetes fills in plus the live `status` block.

Init container example (`initpod.yml`):
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: initpod
  labels:
    app: initializer
spec:
  initContainers:
  - name: init-ctr
    image: busybox:1.28.4
    command: ['sh', '-c', 'until nslookup k8sbook; do echo waiting for k8sbook service; sleep 1; done; echo Service found!']
  containers:
  - name: web-ctr
    image: nigelpoulton/web-app:1.0
    ports:
    - containerPort: 8080
```
**What it demonstrates**: `web-ctr` cannot start until `init-ctr` finds the `k8sbook` Service. Status shows `Init:0/1` (Pod `Pending`) → `PodInitializing` → `Running 1/1` once the Service exists; the init container ends in `terminated` (exit 0).

Sidecar example (`sidecarpod.yml`, abridged):
```yaml
spec:
  containers:
  - name: ctr-web          # main app (NGINX serving from shared volume)
    image: nginx
    volumeMounts:
    - name: html
      mountPath: /usr/share/nginx/
  - name: ctr-sync         # sidecar: git-sync into shared volume
    image: k8s.gcr.io/git-sync:v3.1.6
    volumeMounts:
    - name: html
      mountPath: /tmp/git
    env:
    - name: GIT_SYNC_REPO
      value: https://github.com/nigelpoulton/ps-sidecar.git
  volumes:
  - name: html
    emptyDir: {}
```
**What it demonstrates**: sidecar syncs a Git repo into an `emptyDir` shared volume; the main container serves the updated content — separation of concerns within one Pod.

## Reference Tables
Restart policies (`spec.restartPolicy`, Pod-wide, excludes init containers):

| Policy | Behavior | Typical use |
|--------|----------|-------------|
| `Always` (default) | Always restart the container | Long-living apps (web servers, datastores, queues) |
| `OnFailure` | Restart only on failure, not on success | Short-living batch jobs you want retried |
| `Never` | Never restart | Batch jobs where failure doesn't warrant retry |

Pod lifecycle phases:

| Phase | Meaning |
|-------|---------|
| Pending | Posted to API server; scheduler finding a node / pulling images / init containers running |
| Running | Scheduled, all containers started; stays here for long-lived Pods |
| Succeeded | All containers completed successfully (short-lived/batch) |
| Failed | Containers terminated with failure |

## Worked Example
1. Define `pod.yml` (above) with `name: hello-pod`, image `nigelpoulton/k8sbook:1.0`, port 8080, limits.
2. Deploy: `kubectl apply -f pod.yml`.
3. Watch readiness: `kubectl get pods` → `0/1 ContainerCreating` → `1/1 Running`.
4. Inspect: `kubectl describe pod hello-pod` (Events: Scheduled → Pulling → Pulled → Created → Started).
5. Exec in: `kubectl exec -it hello-pod -- sh`, then `env | grep HOSTNAME` → `HOSTNAME=hello-pod` (Pod name = container hostname; must be a valid DNS name).
6. Confirm immutability: `kubectl edit pod hello-pod`, change name/port/resources → save → rejected as forbidden.
7. `exit`, then `kubectl delete pod hello-pod`.

## Key Takeaways
1. Pods are the atomic unit of scheduling and an abstraction over any workload type.
2. All containers in a Pod share network, volumes, memory, PID, and hostname; they're guaranteed to co-schedule on one node.
3. Pods are mortal and immutable — never restarted, only replaced; store state in volumes.
4. `restartPolicy` (Always/OnFailure/Never) restarts *containers* via the kubelet, not Pods.
5. Init containers run-once before the app; sidecars run alongside it for the Pod's full life.
6. Always set resource requests (minimums, scheduling) and limits (maximums, capping).
7. Prefer workload controllers over static Pods for self-healing, scaling, and rollouts.

## Connects To
- **Chapter 2**: builds on the Kubernetes API, declarative model, and core architecture.
- **Chapter 6**: workload resources and controllers (Deployments, Jobs, DaemonSets) that manage Pods.
- **Services chapter**: labels (`zone`, `version`) connect Pods to Services; init container waits on the `k8sbook` Service.
- **Storage/volumes chapter**: `emptyDir` and persistent volumes for stateful and shared-data patterns.
- **Networking/security**: the pod network, CNI plugins (Cilium), and Network Policies.
