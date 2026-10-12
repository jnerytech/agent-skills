# Chapter 13: StatefulSets

## Core Idea
StatefulSets deploy and manage **stateful applications** — apps that create and save valuable data (databases, key-value stores, session stores). Like Deployments, they are API resources following the standard controller architecture (control loops reconciling observed state with desired state) and provide self-healing, scaling, and rollouts. Unlike Deployments, they guarantee each Pod a **sticky ID**: a stable, predictable name, DNS hostname, and volume binding that survive failures, scaling, and rescheduling.

## Frameworks Introduced
- **The three StatefulSet guarantees (sticky ID / state):**
  1. Predictable and persistent **Pod names**
  2. Predictable and persistent **DNS hostnames**
  3. Predictable and persistent **volume bindings**
- A failed Pod is replaced by a new Pod with the *exact same* name, DNS hostname, and volumes — even on a different node.

## Key Concepts (5-10)
- **Ordinal index** — zero-based integer in Pod name; core to startup, self-heal, scale, delete, and volume attachment.
- **Pod naming format** — `<StatefulSetName>-<Integer>` (e.g. `tkb-sts-0`, `tkb-sts-1`, `tkb-sts-2`). Must be valid DNS names.
- **Ordered startup/scaling** — controller creates one Pod at a time, waiting for *running and ready* before starting the next. Scale-down terminates highest ordinal first, one at a time.
- **Headless Service** — a Service with `spec.clusterIP: None` (no ClusterIP). Creates DNS SRV + A records for every matching Pod so clients query DNS and connect directly to individual Pods (no round-robin load balancing).
- **Governing Service** — the headless Service named in the StatefulSet's `spec.serviceName`; owns the DNS subdomain for the StatefulSet's Pods.
- **volumeClaimTemplates** — generates a unique PVC per Pod; names link Pods and PVCs together.
- **Per-Pod persistent volume** — volumes are decoupled from Pods via the PVC system with independent lifecycles, so they survive Pod failure/termination/rescheduling.
- **podManagementPolicy** — `OrderedReady` (default, one at a time) vs `Parallel` (acts like a Deployment for scaling only; naming rules still enforced; does not affect rollouts/rollbacks).
- **terminationGracePeriodSeconds** — commonly ≥10s so apps flush buffers and commit in-flight writes.
- **Self-healing** — StatefulSet controller does its own self-healing and scaling (Deployments delegate to a ReplicaSet controller).

## Mental Models (StatefulSet for apps needing stable identity + storage)
- **Sticky ID = name + DNS + volume.** If an app needs to reconnect to *the same* identity and data after a restart, it needs a StatefulSet.
- **Names are the wiring.** Pod name → PVC name (`<template>-<sts>-<ordinal>`) → DNS hostname. Everything keys off the ordinal.
- **Service has a head and a tail.** Head = stable ClusterIP; tail = backend Pods. Headless = no head, so clients reach individual Pods by DNS.
- **Volumes outlive Pods.** Scale-down deletes Pods but keeps PVCs; scale-up reattaches the surviving PVC. A safety net if you delete the last replica.
- **StatefulSets are only a framework.** The application must be *coded* to query DNS for peers and exploit stable identity.

## Anti-patterns
- **Deleting a StatefulSet directly** when order matters — deletion does *not* terminate Pods in order. Scale to 0 first.
- Expecting **parallel startup** like a Deployment — startup is serialized; a stuck Pod blocks the rest.
- Assuming **scaling down deletes storage** — PVCs (and PVs/backend storage) remain; clean them up explicitly to avoid cloud costs.
- **Node-failure auto-recovery** assumptions on older clusters — replacing a "failed" node's Pods can cause two identical Pods writing the same volume → data corruption. Newer K8s handles this better.
- Relying on the **Service to load-balance to a specific Pod** — use the headless Service + per-Pod DNS instead.

## Code Examples

### StatefulSet with volumeClaimTemplates (sts.yml)
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: tkb-sts
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  serviceName: "dullahan"        # governing (headless) Service
  template:
    metadata:
      labels:
        app: web
    spec:
      terminationGracePeriodSeconds: 10
      containers:
      - name: ctr-web
        image: nginx:latest
        ports:
        - containerPort: 80
          name: web
        volumeMounts:
        - name: webroot
          mountPath: /usr/share/nginx/html
  volumeClaimTemplates:          # one unique PVC per Pod
  - metadata:
      name: webroot
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: "flash"
      resources:
        requests:
          storage: 10Gi
```

### Governing headless Service (headless-svc.yml)
```yaml
apiVersion: v1
kind: Service
metadata:
  name: dullahan
  labels:
    app: web
spec:
  ports:
  - port: 80
    name: web
  clusterIP: None                # makes it headless
  selector:
    app: web
```

### StorageClass for dynamic volumes (gcp-sc.yml — GKE)
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: flash                    # referenced by the PVC
provisioner: pd.csi.storage.gke.io
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
parameters:
  type: pd-ssd
```

## Reference Tables

### StatefulSet vs Deployment
| Property | StatefulSet | Deployment |
|---|---|---|
| Pod names | Stable, predictable: `<sts>-<ordinal>` | Random suffix |
| DNS hostname | Stable per-Pod (via headless Service) | Not per-Pod stable |
| Startup/scale-up | One at a time, in order (0,1,2…); waits for running+ready | All at once (ReplicaSet); race conditions possible |
| Scale-down | Highest ordinal first, one at a time | Parallel |
| Storage | Per-Pod PVC via volumeClaimTemplates; survives Pod loss | Typically shared/none |
| Self-heal/scale controller | StatefulSet controller itself | ReplicaSet controller |
| Replacement Pod | Same name + DNS + volume | New identity |

### PVC naming (volumeClaimTemplate → Pod → PVC)
| volumeClaimTemplate | Pod | PVC |
|---|---|---|
| webroot | tkb-sts-0 | webroot-tkb-sts-0 |
| webroot | tkb-sts-1 | webroot-tkb-sts-1 |
| webroot | tkb-sts-2 | webroot-tkb-sts-2 |

### Per-Pod DNS (default Namespace, governing Service `dullahan`)
Format: `<object>.<service>.<namespace>.svc.cluster.local`
- `tkb-sts-0.dullahan.default.svc.cluster.local`
- `tkb-sts-1.dullahan.default.svc.cluster.local`
- `tkb-sts-2.dullahan.default.svc.cluster.local`

## Worked Example
Deploy a 3-replica StatefulSet (StorageClass → headless Service → StatefulSet):
```bash
kubectl apply -f gcp-sc.yml         # or dd-sc.yml on Docker Desktop
kubectl apply -f headless-svc.yml
kubectl apply -f sts.yml
kubectl get sts --watch             # 0/3 → 1/3 → 2/3 → 3/3 (~30s each, in order)
```
Stable names + per-Pod PVCs appear:
```bash
kubectl get pvc
# webroot-tkb-sts-0  Bound  10Gi  RWO  flash
# webroot-tkb-sts-1  Bound  10Gi  RWO  flash
# webroot-tkb-sts-2  Bound  10Gi  RWO  flash
```
Peer discovery via headless Service (from a jump Pod with `dig`):
```bash
kubectl exec -it jump-pod -- bash
dig SRV dullahan.default.svc.cluster.local   # SRV → Pod names, A → Pod IPs
```
Scale down 3→2 deletes only `tkb-sts-2` (highest ordinal); all 3 PVCs remain `Bound` (`webroot-tkb-sts-2` shows `Used by: <none>`). Scale back 2→3 creates a new Pod that reattaches the surviving PVC:
```bash
kubectl describe pod tkb-sts-2 | grep ClaimName   # ClaimName: webroot-tkb-sts-2
```
Test failure — delete `tkb-sts-0`; controller recreates it with the same name and reconnects `webroot-tkb-sts-0`.
Delete safely:
```bash
kubectl scale sts tkb-sts --replicas=0      # ordered shutdown before delete
kubectl delete sts tkb-sts
kubectl delete svc dullahan
kubectl delete pvc webroot-tkb-sts-0 webroot-tkb-sts-1 webroot-tkb-sts-2  # deletes PVs/backend storage
kubectl delete sc flash
```

## Key Takeaways (3-7)
- StatefulSets give Pods a persistent **sticky ID** (name + DNS hostname + volume) that survives failures, restarts, scaling, and rescheduling.
- Pods are named `<sts>-<ordinal>`; the ordinal drives **ordered** creation, scaling, rollouts, and PVC binding.
- `volumeClaimTemplates` creates one **per-Pod PVC**; volumes have independent lifecycles and survive Pod deletion (scale-down keeps PVCs).
- A **headless Service** (`clusterIP: None`) set as `spec.serviceName` is the governing Service, producing stable per-Pod DNS for direct peer connections.
- Scale to 0 before deleting a StatefulSet (deletion is not ordered); set `terminationGracePeriodSeconds` for clean shutdown.
- Rollouts go highest→lowest ordinal, one at a time; **rollbacks need manual attention**. The app must be designed to exploit the framework.

## Connects To
- **Ch 12 (Deployments)** — contrast: random names, parallel startup, ReplicaSet-driven; StatefulSets add identity + ordering.
- **Ch (Storage / PVCs & StorageClasses)** — `volumeClaimTemplates`, dynamic provisioning, `WaitForFirstConsumer`, RWO access modes.
- **Ch (Services & networking)** — headless Services, DNS SRV/A records, the cluster DNS service registry.
- **Ch (Pods)** — running-and-ready readiness gates the ordered behavior.
