# Chapter 8: Running Data-Heavy Apps with StatefulSets and Jobs

## Core Idea

Kubernetes is a dynamic environment, but data-heavy applications — databases, message queues, distributed caches — expect stability: known peer addresses, persistent per-instance storage, and periodic maintenance tasks. StatefulSets model that stability by giving Pods predictable names, ordered startup, and individually addressable DNS entries. Jobs and CronJobs handle the batch-processing and maintenance side (backups, reconciliation) by guaranteeing a Pod runs to completion on demand or on a schedule.

---

## Frameworks Introduced

- **StatefulSet Controller**: A Pod controller that enforces a stable, ordered runtime environment.
  - **What**: Creates Pods with predictable names (`<name>-0`, `<name>-1`, …), starts them in strict index order, replaces missing Pods with identical replacements (same name, same PVC binding), and scales down in reverse order.
  - **When**: Clustered apps that need a primary/secondary topology, apps that assume stable network addresses for peers, or any workload that must retain identity across Pod restarts.
  - **How**: Requires a linked headless Service for DNS; supports `volumeClaimTemplates` to give each Pod its own PVC; uses init containers for role-specific initialization logic.
  - **Why / Failure**: Without it, ReplicaSets assign random names and start Pods in parallel — a clustered database can end up with zero primaries or multiple primaries, corrupting the cluster.

- **Job Controller**: Ensures a Pod-based batch process runs to completion.
  - **What**: Creates a Pod from a spec, monitors it, restarts or replaces it on failure, and retains the completed Pod so logs are available. Supports `completions` (total runs) and `parallelism` (concurrent Pods).
  - **When**: Any finite batch process: backups, data transformations, compute-intensive calculations, queue draining.
  - **How**: Set `restartPolicy: Never` (replace Pod on failure) or `OnFailure` (restart container in same Pod). Add init containers to inject per-Pod input without modifying the app image.
  - **Why / Failure**: Long-running containers that never exit will keep the Job open forever. The container entrypoint must be a process that terminates.

- **CronJob Controller**: A Job controller that fires Jobs on a Linux-cron schedule.
  - **What**: Creates a Job (and thus a Pod) on a recurring schedule. Owns Jobs via `ownerReferences`, not label selectors.
  - **When**: Regular maintenance tasks — database backups, log rotation, report generation.
  - **How**: Embed a full Job spec inside `jobTemplate`. Set `concurrencyPolicy: Forbid` to prevent overlapping runs if the previous Job is still running.
  - **Why / Failure**: No automatic cleanup of completed Jobs/Pods (TTL controller is alpha). Manual deletion or a suspend flag is required to stop accumulation.

---

## Key Concepts

1. **Predictable Pod naming**: StatefulSet Pods are named `<statefulset-name>-<index>` (e.g., `todo-db-0`, `todo-db-1`). This is deterministic and stable across replacements — a new Pod 0 has the same name as the one it replaces.

2. **Ordered creation and deletion**: Pods are created sequentially from index 0 upward; Pod N+1 does not start until Pod N is Ready. Scale-down removes from the highest index downward. Replacement of a missing Pod does not re-trigger ordering for existing Pods.

3. **Headless Service**: A Service with `clusterIP: None`. It has no virtual IP. DNS resolution returns one A-record per Pod in the StatefulSet. Each Pod also gets its own DNS entry in the format `<pod-name>.<service-name>.<namespace>.svc.cluster.local`.

4. **Per-Pod DNS addressability**: Because each Pod has a stable name and a headless Service provides individual DNS entries, a secondary Pod can reliably find the primary by looking up `todo-db-0.todo-db.default.svc.cluster.local`.

5. **volumeClaimTemplates**: A field in the StatefulSet spec that acts as a PVC factory. One PVC is created per Pod, named `<template-name>-<pod-name>`. The PVC-to-Pod binding is preserved when a Pod is replaced — new Pod 0 re-attaches to the PVC that old Pod 0 used.

6. **Init containers for role initialization**: Since Pods start in order, an init container in Pod 1 can safely assume Pod 0 is running. Init containers can check pod index (via hostname) to decide: "I am Pod 0 → become primary; I am Pod N → wait for Pod 0, then replicate."

7. **Job `restartPolicy`**: Must be set explicitly. `Never` creates a fresh Pod on failure (potentially on a different node). `OnFailure` restarts the container inside the same Pod.

8. **Job `completions` and `parallelism`**: `completions` sets how many successful Pod runs are required. `parallelism` sets how many run concurrently. These can be combined — e.g., 6 completions with parallelism 3 runs two waves of 3 Pods.

9. **CronJob `concurrencyPolicy`**: Controls what happens if a new Job fires while the previous one is still running. `Forbid` skips the new run; `Allow` creates it anyway; `Replace` cancels the old Job and starts a new one.

10. **StatefulSets are not easily mutated**: Fundamental changes (e.g., adding `volumeClaimTemplates` to an existing StatefulSet) cannot be applied with `kubectl apply`. The StatefulSet must be deleted and recreated. This is by design — StatefulSets model stable environments and resist disruptive changes.

---

## Mental Models

1. **StatefulSet = Stable identities, not just multiple copies**: Think of a ReplicaSet as a fleet of anonymous, interchangeable soldiers. A StatefulSet is a named squad — Soldier-0 always carries the flag; Soldier-1 is always the radio operator. The cluster enforces those roles even after casualties. Each soldier has their own equipment locker (PVC) that goes with their name, not their person.

2. **Job/CronJob hierarchy mirrors Deployment/ReplicaSet**: A CronJob owns Jobs the way a Deployment owns ReplicaSets. A Job owns Pods the way a ReplicaSet does. The difference is lifecycle: Deployments manage long-running replicas; Jobs manage finite-run Pods. CronJob → Job → Pod is the full ownership chain. Cascading deletes remove everything from the top down.

3. **Headless Service as a DNS directory, not a load balancer**: A normal ClusterIP Service is a receptionist who routes calls. A headless Service is a company directory — it lists everyone's direct number (Pod IP). Callers get all the numbers and decide whom to call. StatefulSet Pods also get personal extensions (`pod-name.service-name`).

4. **Managed cloud services vs. in-cluster StatefulSets**: Running a StatefulSet database in Kubernetes is powerful but complex (replication scripts, init containers, PVCs, backup CronJobs, chaos testing). Managed cloud databases (RDS, Cloud SQL, Azure Database) offload all that to the provider. A pragmatic split: use containerized databases in dev/test (cheap, easy to reset); use managed services in production where data is irreplaceable.

---

## Anti-patterns

- **Running a clustered database in a ReplicaSet/Deployment**: Random Pod names and parallel startup make it impossible to reliably elect a primary. You will get race conditions, split-brain, or zero primaries.

- **Shared PVC for all StatefulSet replicas**: Mounting a single PVC in multiple Pods causes all replicas to write to the same storage. Use `volumeClaimTemplates` to give each Pod independent storage.

- **Job container that never exits**: A process that keeps running will prevent the Job from completing. Jobs are for batch workloads with a defined end state.

- **CronJob without `concurrencyPolicy: Forbid` on slow tasks**: If a backup Job takes longer than the schedule interval, new Jobs pile up. Each spawns its own Pod, exhausting resources and potentially causing concurrent writes to the same backup target.

- **Trying to `kubectl apply` a StatefulSet with changed `volumeClaimTemplates`**: This will be rejected. You must delete the StatefulSet and redeploy. Plan the PVC spec carefully before first deployment.

- **Ignoring CronJob Job accumulation**: Without the TTL controller (alpha), completed Jobs and their Pods are never cleaned up automatically. Over time this clutters the cluster. Use `successfulJobsHistoryLimit` and `failedJobsHistoryLimit` fields, or manually prune.

---

## Code Examples

**StatefulSet with volumeClaimTemplates + headless Service:**

```yaml
# Headless Service — gives each Pod its own DNS entry
apiVersion: v1
kind: Service
metadata:
  name: todo-db
spec:
  selector:
    app: todo-db
  clusterIP: None        # No virtual IP; DNS returns individual Pod IPs
  ports:
    - port: 5432

---
# StatefulSet with per-Pod PVC
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: todo-db
spec:
  selector:
    matchLabels:
      app: todo-db
  serviceName: todo-db   # Must match the headless Service name
  replicas: 2
  template:
    metadata:
      labels:
        app: todo-db
    spec:
      initContainers:
        - name: wait-service
          image: kiamol/ch03-sleep
          envFrom:
            - configMapRef:
                name: todo-db-env
          command: ['/scripts/wait-service.sh']
          volumeMounts:
            - name: scripts
              mountPath: "/scripts"
      containers:
        - name: db
          image: postgres:13-alpine
          volumeMounts:
            - name: data
              mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:          # Creates one PVC per Pod
    - metadata:
        name: data               # PVC name: data-todo-db-0, data-todo-db-1, etc.
      spec:
        accessModes:
          - ReadWriteOnce
        resources:
          requests:
            storage: 5Mi
```

**Job:**

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: pi-job
spec:
  template:
    spec:
      containers:
        - name: pi
          image: kiamol/ch05-pi
          command: ["dotnet", "Pi.Web.dll", "-m", "console", "-dp", "50"]
      restartPolicy: Never   # Replace Pod on failure rather than restart in place
```

**CronJob:**

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: todo-db-backup
spec:
  schedule: "*/2 * * * *"       # Linux cron syntax; runs every 2 minutes
  concurrencyPolicy: Forbid     # Skip new run if previous Job still running
  jobTemplate:
    spec:
      template:
        spec:
          containers:
            - name: backup
              image: postgres:13-alpine
              command: ["pg_dump", ...]
          restartPolicy: OnFailure
```

---

## Reference Tables

### Deployment vs StatefulSet

| Dimension | Deployment (via ReplicaSet) | StatefulSet |
|---|---|---|
| Pod naming | Random suffix (`todo-db-7f4c8-xkj2p`) | Indexed (`todo-db-0`, `todo-db-1`) |
| Startup order | Parallel | Sequential (0 → 1 → 2 …) |
| Scale-down order | Arbitrary | Reverse index (n → n-1 → … → 0) |
| DNS addressability | Only via Service (load-balanced) | Per-Pod DNS via headless Service |
| Pod replacement | New Pod, new name | New Pod, same name |
| Per-Pod storage | Shared PVC only | `volumeClaimTemplates` (one PVC per Pod) |
| PVC on replacement | N/A | New Pod re-attaches to same PVC |
| Best for | Stateless apps, microservices | Clustered databases, message queues, caches |

### Job vs CronJob

| Dimension | Job | CronJob |
|---|---|---|
| Trigger | Manual (`kubectl apply`) or app-initiated | Schedule (Linux cron expression) |
| Ownership | Owns Pods directly | Owns Jobs, which own Pods |
| Parallelism | Yes (`parallelism` field) | Yes (via Job template) |
| Concurrency control | N/A | `concurrencyPolicy` (Allow/Forbid/Replace) |
| Cleanup | Manual or TTL controller | `successfulJobsHistoryLimit` / `failedJobsHistoryLimit` |
| Suspend | No | Yes (`suspend: true`) |
| Best for | One-off batch tasks, queue processing | Scheduled maintenance, backups, reports |

---

## Worked Example

**Goal**: Deploy a replicated Postgres database using a StatefulSet with stable per-Pod storage, then run a CronJob to take periodic backups.

**Step 1 — Deploy the headless Service and StatefulSet:**

```bash
kubectl apply -f todo-list/db/
kubectl get statefulset todo-db
kubectl get pods -l app=todo-db
```

Observe: Pods appear as `todo-db-0` and `todo-db-1`. Pod 1 does not start until Pod 0 is Ready. Each Pod's hostname matches its name.

**Step 2 — Verify per-Pod DNS:**

```bash
kubectl apply -f sleep/sleep.yaml
kubectl exec deploy/sleep -- sh -c 'nslookup todo-db | grep "^[^*]"'
kubectl exec deploy/sleep -- sh -c \
  'nslookup todo-db-0.todo-db.default.svc.cluster.local | grep "^[^*]"'
```

The headless Service DNS returns two A-records (one per Pod IP). Pod 0 also has its own DNS entry, which the init container in Pod 1 uses to reach the primary before replication begins.

**Step 3 — Validate init container role selection:**

```bash
kubectl logs todo-db-0 --tail 1   # "I am the primary"
kubectl logs todo-db-1 --tail 2   # "Waiting for primary... replication started"
```

Pod 0's startup script checks its hostname: `todo-db-0` → primary. Pod 1 checks its hostname: `todo-db-1` → secondary, then runs `pg_basebackup` against `todo-db-0.todo-db…`.

**Step 4 — Add volumeClaimTemplates for persistent storage (requires StatefulSet delete/recreate):**

```bash
kubectl delete statefulset todo-db
kubectl apply -f todo-list/db/replicated/update/todo-db-pvc.yaml
kubectl get pvc -l app=todo-db
```

Two PVCs are created: `data-todo-db-0` and `data-todo-db-1`. Each Pod mounts only its own PVC. If you delete `todo-db-0` and it is replaced, the new `todo-db-0` re-attaches to `data-todo-db-0` and has access to all previous data.

**Step 5 — Scale to three replicas:**

```bash
kubectl scale --replicas=3 statefulset/todo-db
kubectl wait --for=condition=Ready pod -l app=todo-db
kubectl logs todo-db-2 --tail 2   # Confirms Pod 2 initialized as secondary
```

A third PVC (`data-todo-db-2`) is created and a third secondary is added.

**Step 6 — Deploy the backup CronJob:**

```bash
kubectl apply -f todo-list/db/backup/
sleep 150   # Wait for first scheduled run (every 2 minutes)
kubectl get cronjob todo-db-backup
kubectl apply -f sleep/sleep-with-db-backup-mount.yaml
kubectl exec deploy/sleep -- ls -l /backup
```

The CronJob fires, creates a Job, which creates a Pod running `pg_dump` against the read-only secondary. The backup `.tar` file is written to the shared PVC. The Pod exits successfully, and the Job status shows one completion.

**Step 7 — Suspend the CronJob to stop further runs:**

```bash
kubectl apply -f todo-list/db/backup/update/todo-db-backup-cronjob-suspend.yaml
kubectl get cronjob todo-db-backup   # suspended: true
```

The spec is preserved, previous Jobs remain, but no new Jobs are created until the CronJob is re-activated.

---

## Key Takeaways

1. StatefulSets give Pods a stable identity — predictable names, ordered lifecycle, and individual DNS entries via a headless Service — making them the correct controller for clustered, primary/secondary applications.

2. `volumeClaimTemplates` solve the per-Pod storage problem: each Pod gets its own dynamically provisioned PVC, and that PVC binding survives Pod replacement, preserving state across restarts and rolling updates.

3. Init containers and ordered Pod startup compose naturally: because Pod N+1 does not start until Pod N is Ready, an init container in Pod 1 can safely assume Pod 0 (the primary) is reachable before attempting replication.

4. Jobs abstract all scheduling, retry, and monitoring logic for batch workloads. The container only needs to do one thing and exit; Kubernetes handles everything else.

5. CronJobs extend Jobs with a schedule, `concurrencyPolicy` to prevent overlap, and a suspend mechanism — making them the right tool for recurring maintenance tasks like database backups.

6. StatefulSets are intentionally inflexible: adding `volumeClaimTemplates` to an existing StatefulSet requires a delete-and-recreate cycle. Design storage requirements up front.

7. Running databases in Kubernetes is powerful but complex. For production data in the cloud, managed database services (RDS, Cloud SQL, etc.) are often the pragmatic choice. The in-cluster StatefulSet pattern is most valuable for on-premises clusters and non-production environments.

---

## Connects To

- **Chapter 5 — Volumes and Storage**: PersistentVolumes, PersistentVolumeClaims, and StorageClasses are the building blocks that `volumeClaimTemplates` automate.
- **Chapter 7 — Multi-container Pods**: Init containers, EmptyDir shared volumes, and sidecar patterns are all used inside StatefulSet Pod templates to handle complex initialization and log shipping.
- **Chapter 6 — Scaling and Controllers**: ReplicaSets and DaemonSets provide the contrast that motivates StatefulSets — understanding what they can't do explains why StatefulSets exist.
- **Chapter 3 — Services and Networking**: ClusterIP Services vs. headless Services; DNS resolution patterns that underpin per-Pod addressability.
- **Chapter 9 — Rollouts and Rollbacks**: StatefulSets support rolling updates but with stricter ordering guarantees than Deployments; the rollout model differs meaningfully for stateful workloads.
