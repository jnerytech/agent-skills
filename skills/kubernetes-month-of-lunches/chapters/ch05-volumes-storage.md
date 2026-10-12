# Chapter 5: Storing Data with Volumes, Mounts, and Claims

## Core Idea

Container filesystems are ephemeral by default: data written inside a container lives only as long as that container, not the Pod. Kubernetes provides a layered storage model — from Pod-scoped `emptyDir`, to node-scoped `hostPath`, to clusterwide PersistentVolumes — to match different durability and availability requirements. Storage is abstracted through PersistentVolumeClaims so application specs remain decoupled from the underlying infrastructure.

---

## Frameworks Introduced

- **Volume + VolumeMount pattern**: Declare a named volume in the Pod spec, then mount it at a specific path in one or more containers. Every storage type (emptyDir, hostPath, PV) follows the same two-field pattern. Use when any data must outlive a single container restart. Failure mode: omitting the volume declaration means the mount silently falls back to the ephemeral container layer.

- **PV / PVC / StorageClass three-tier abstraction**: PersistentVolumes (PV) represent physical storage; PersistentVolumeClaims (PVC) represent application storage requests; StorageClasses define provisioning policies. The decoupling lets ops teams manage infrastructure while app teams declare requirements. Failure mode: requesting a PVC without a matching PV (static) or without a default class (dynamic) leaves the Pod permanently Pending.

- **Static vs. Dynamic Provisioning**: In static provisioning, an admin creates PVs manually; PVCs bind to them. In dynamic provisioning, a StorageClass provisioner creates the PV on demand when a PVC is created. Dynamic is simpler and is the norm on cloud platforms.

---

## Key Concepts

1. **Container filesystem lifecycle**: Built from image layers plus a per-container writable layer. The writable layer has the lifecycle of the *container*, not the Pod — a Pod restart replaces the container and its writable layer.

2. **emptyDir volume**: An empty directory provisioned at the Pod level. Survives container restarts within the same Pod; destroyed when the Pod itself is replaced. Suitable for caches, temporary sharing between containers, or any non-critical ephemeral state.

3. **hostPath volume**: Maps a directory from the node's filesystem into the container. Data persists beyond Pod replacements — but only if the replacement Pod lands on the same node. Carries a security risk: a mount at `/` exposes the entire node filesystem to the container.

4. **hostPath subPath**: Restricts a volume mount to a specific subdirectory within the hostPath, limiting what the container can read or write on the node.

5. **PersistentVolume (PV)**: A cluster-scoped Kubernetes object representing a pre-provisioned piece of storage (NFS, Azure Disk, local volume, etc.). Defines capacity, access modes, and reclaim policy. One-to-one binding with a PVC.

6. **PersistentVolumeClaim (PVC)**: A namespace-scoped request for storage. Specifies access mode, capacity, and optional storage class. Kubernetes binds it to an available PV that satisfies the requirements.

7. **Access modes**: `ReadWriteOnce` (RWO) — mounted read/write by one node; `ReadOnlyMany` (ROX) — mounted read-only by many nodes; `ReadWriteMany` (RWX) — mounted read/write by many nodes. The PV and PVC must agree on access mode for binding to succeed.

8. **StorageClass**: A cluster resource that defines a provisioner, reclaim policy, and binding mode. PVCs that omit `storageClassName` use the cluster default. Named classes let workloads request specific storage tiers (fast SSD, replicated NFS, etc.) without hard-coding volume details.

9. **Dynamic provisioning**: When a PVC references a StorageClass (or uses the default), the cluster's provisioner creates a matching PV on demand. The PV is destroyed when the PVC is deleted if the reclaim policy is `Delete`.

10. **Stateful apps in Kubernetes**: Technically feasible with PVCs, but adds operational complexity (backups, snapshots, rollbacks). Managed cloud database services are often preferable; container-native databases like TiDB and CockroachDB are designed for this use case.

---

## Mental Models

- **Filesystem as a stack of layers**: Think of the container filesystem as a transparent overlay stack — image layers (read-only) at the bottom, a per-container writable layer in the middle, and mounted volumes injected at specific paths. Volumes punch through the ephemeral layers to durable storage underneath.

- **Storage lifecycle ladder**: Each storage type sits on a rung of the durability ladder:
  1. Container writable layer — dies with the container.
  2. `emptyDir` — lives at the Pod level; survives restarts, not replacements.
  3. `hostPath` — lives at the node level; survives Pod replacements if on the same node.
  4. PV/PVC — lives at the cluster level; survives Pod replacements on any node (if distributed storage is used).

- **PVC as a storage ticket**: A PVC is like a purchase order: you describe what you need (size, access mode, class); Kubernetes finds (static) or creates (dynamic) a matching PV to fulfill it. The Pod holds only the ticket reference, not the storage details.

---

## Anti-patterns

- **Writing to the container writable layer for persistent data**: Any data written directly inside the container (not in a volume mount) is lost on container restart. Apps that "seem to work" this way will silently lose data under failure.

- **Using hostPath for clusterwide persistence**: hostPath data is node-local. On multi-node clusters, Pod replacements may land on different nodes, making stored data unreachable. Treat hostPath as a single-node or debugging tool only.

- **Mounting hostPath at `/` without subPath restriction**: Grants the container (often running as root) full read/write access to the node filesystem, including Kubernetes control plane files. Exposing host PID namespaces or credentials this way is a common container escape vector.

- **Deploying a PVC with no matching PV and no StorageClass**: The PVC remains Pending indefinitely. Any Pod referencing it also stays Pending with no error surfaced at the Deployment level — the app silently never starts.

- **Assuming dynamic provisioning on all clusters**: Behavior of a PVC without `storageClassName` differs across platforms (Docker Desktop creates a HostPath PV immediately; K3s waits until a Pod uses the PVC; some clusters have no default class at all). Always verify cluster capabilities before relying on dynamic provisioning.

---

## Code Examples

```yaml
# emptyDir volume — data survives container restart, not Pod replacement
volumes:
  - name: data
    emptyDir: {}
```

```yaml
# hostPath volume — maps node directory into container
volumes:
  - name: cache-volume
    hostPath:
      path: /volumes/nginx/cache
      type: DirectoryOrCreate    # creates path if absent
```

```yaml
# hostPath with subPath — restrict container access to specific subdirectories
volumeMounts:
  - name: node-root
    mountPath: /pod-logs
    subPath: var/log/pods
  - name: node-root
    mountPath: /container-logs
    subPath: var/log/containers
volumes:
  - name: node-root
    hostPath:
      path: /
      type: Directory
```

```yaml
# PersistentVolume (static, local storage pinned to a labeled node)
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv01
spec:
  capacity:
    storage: 50Mi
  accessModes:
    - ReadWriteOnce
  local:
    path: /volumes/pv01
  nodeAffinity:
    required:
      nodeSelectorTerms:
        - matchExpressions:
            - key: kiamol
              operator: In
              values: ["ch05"]
```

```yaml
# PersistentVolumeClaim (static — requires existing PV)
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 40Mi
  storageClassName: ""    # blank = require existing PV, skip dynamic provisioning
```

```yaml
# PersistentVolumeClaim (dynamic — uses cluster default StorageClass)
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc-dynamic
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 100Mi
  # no storageClassName field → uses default class
```

```yaml
# PersistentVolumeClaim (named StorageClass)
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: kiamol
  resources:
    requests:
      storage: 100Mi
```

```yaml
# Pod referencing a PVC (database example)
volumes:
  - name: data
    persistentVolumeClaim:
      claimName: postgres-pvc
containers:
  - name: db
    image: postgres:11.6-alpine
    volumeMounts:
      - name: data
        mountPath: /var/lib/postgresql/data
```

```bash
# Label a node so a local PV can pin to it
kubectl label node $(kubectl get nodes -o jsonpath='{.items[0].metadata.name}') kiamol=ch05

# Apply a PV
kubectl apply -f todo-list/persistentVolume.yaml

# Check PVs and PVCs
kubectl get pv
kubectl get pvc

# Deploy a PVC and observe binding
kubectl apply -f todo-list/postgres-persistentVolumeClaim.yaml

# List StorageClasses
kubectl get storageclass

# Delete a PVC (triggers volume reclaim policy)
kubectl delete pvc postgres-pvc-dynamic
```

---

## Reference Tables

### Volume Types Comparison

| Type | Lifecycle | Scope | Use Case | Risk |
|---|---|---|---|---|
| Container writable layer | Container | Container | Default writes | Data lost on restart |
| `emptyDir` | Pod | Pod | Temp cache, inter-container share | Lost on Pod replacement |
| `hostPath` | Node disk | Node | Single-node state, node log access | Node-local; security risk |
| PV (local) | Independent | Node (pinned) | Lab/static single-node persistence | Node-local |
| PV (distributed: NFS, Azure Files, EBS) | Independent | Cluster | Production stateful apps | Cost; platform-specific config |

### PV / PVC / StorageClass Roles

| Resource | Scope | Owner | Defines |
|---|---|---|---|
| PersistentVolume (PV) | Cluster | Ops/Admin | Physical storage details, capacity, access modes |
| PersistentVolumeClaim (PVC) | Namespace | App team | Storage requirements (size, mode, class) |
| StorageClass | Cluster | Ops/Admin | Provisioner, reclaim policy, binding mode |

### Access Modes

| Mode | Abbreviation | Meaning |
|---|---|---|
| ReadWriteOnce | RWO | One node can mount read/write |
| ReadOnlyMany | ROX | Many nodes can mount read-only |
| ReadWriteMany | RWX | Many nodes can mount read/write |

PV and PVC access modes must be compatible for binding. Most block storage (Azure Disk, EBS) supports only RWO. File-based storage (NFS, Azure Files) typically supports RWX.

---

## Worked Example

**Goal**: Deploy a Postgres database whose data survives Pod replacement using a PVC backed by a local PV.

**Step 1 — Label a node** so a local PV can pin to it:
```bash
kubectl label node $(kubectl get nodes -o jsonpath='{.items[0].metadata.name}') kiamol=ch05
```

**Step 2 — Create the PV** referencing the labeled node and a local path (`/volumes/pv01`):
```bash
kubectl apply -f todo-list/persistentVolume.yaml
kubectl get pv   # status: Available
```

**Step 3 — Create the directory on the node** (using a sleep Pod with a hostPath mount, since direct node access is not available in most environments):
```bash
kubectl apply -f sleep/sleep-with-hostPath.yaml
kubectl exec deploy/sleep -- mkdir -p /node-root/volumes/pv01
```

**Step 4 — Create the PVC** requesting 40Mi with `ReadWriteOnce` and `storageClassName: ""` (forcing static binding):
```bash
kubectl apply -f todo-list/postgres-persistentVolumeClaim.yaml
kubectl get pvc   # status: Bound
kubectl get pv    # status: Bound
```
The PV and PVC are now in a one-to-one binding.

**Step 5 — Deploy Postgres** referencing the PVC in the Pod spec under `persistentVolumeClaim.claimName: postgres-pvc`. Postgres initializes its data files into the mounted volume at `/var/lib/postgresql/data`:
```bash
kubectl apply -f todo-list/postgres/
sleep 30
kubectl logs -l app=todo-db --tail 1   # "database system is ready to accept connections"
```

**Step 6 — Verify data survives Pod replacement**:
```bash
# Add data via the web app, then delete the database Pod
kubectl delete pod -l app=todo-db
# Deployment controller starts a replacement Pod
# Replacement mounts the same PVC → same PV → same local path
kubectl exec deploy/sleep -- ls -l /node-root/volumes/pv01/pg_wal   # WAL files present
# Refresh the web app — data is still there
```

The Pod was replaced, but the PVC remained bound to the same PV. The new container mounted the existing volume and found all previously written data intact.

**Key insight**: The only change needed to move from a lab local volume to production distributed storage is replacing the `local` volume spec inside the PV with the appropriate distributed volume type (NFS, Azure Files, EBS). The PVC and Pod specs remain unchanged.

---

## Key Takeaways

1. Container writable layers are ephemeral — any data written inside a container (not in a volume mount) is lost when the container restarts.
2. `emptyDir` volumes share the Pod's lifecycle: they survive container restarts but not Pod replacements. Ideal for caches and inter-container sharing.
3. `hostPath` volumes persist across Pod replacements but only on the same node. Multi-node clusters make this unreliable. Always restrict access with `subPath` to limit the security surface.
4. The PV/PVC abstraction decouples application specs from storage infrastructure. App teams write PVCs; ops teams provision PVs or configure StorageClasses.
5. Dynamic provisioning (StorageClass without explicit PV creation) is the production norm on cloud platforms. Behavior differs by cluster — verify what your platform provides before relying on a default class.
6. A PVC that cannot bind to a PV leaves any referencing Pod in Pending state indefinitely. Always check `kubectl get pvc` to confirm `Bound` status before troubleshooting Pod scheduling.
7. Running stateful apps in Kubernetes is technically viable but operationally complex. Evaluate managed database services before containerizing relational databases.

---

## Connects To

- **Chapter 4 (ConfigMaps and Secrets)**: ConfigMaps and Secrets are mounted using the same volume/volumeMount mechanism introduced here. Understanding the general volume pattern makes those specific read-only volume types easier to reason about.
- **Chapter 6 (Scaling and Controllers)**: StatefulSets (covered later) pair each Pod replica with its own PVC via `volumeClaimTemplates`, enabling stable storage identities for stateful workloads like databases.
- **Chapter 8 (StatefulSets and Jobs)**: StatefulSets build directly on PVCs and StorageClasses to give each Pod a stable, unique persistent volume across rescheduling events.
