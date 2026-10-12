# Chapter 11: Kubernetes storage

## Core Idea
Kubernetes has a pluggable persistent volume subsystem that lets apps consume enterprise-grade external storage (block, file, object; cloud or on-prem) in a uniform, declarative way. External storage systems connect via a CSI plugin; a standardized set of API objects (PV, PVC, StorageClass) lets apps request and mount storage — dynamically and automatically.

## Frameworks Introduced

### Three-layer architecture
1. **Storage providers / provisioners** (left) — external systems: EMC, NetApp, AWS EBS, GCE PD, Filestore, etc.
2. **Plugin layer** (middle) — the **Container Storage Interface (CSI)** connects external systems to Kubernetes.
3. **Persistent volume subsystem** (right) — API objects apps use to consume storage.

### The storage trinity (PV + PVC + StorageClass)
- **PersistentVolume (PV)** — represents/maps to an external volume on Kubernetes.
- **PersistentVolumeClaim (PVC)** — grants an application access to a PV.
- **StorageClass (SC)** — defines a tier of storage; makes provisioning automatic and dynamic.
- One-liner: *PVs map to external volumes, PVCs grant access to PVs, SCs make it all automatic and dynamic.*

### CSI (Container Storage Interface)
Open-source industry-standard interface so any orchestrator can use external storage uniformly. Lets developers write **out-of-tree** plugins (vs legacy **in-tree**, which forced open-sourcing and tied updates to the Kubernetes release cycle). Each provider ships its own CSI plugin (a.k.a. driver) via Helm chart or YAML installer; it runs as Pods in the `kube-system` Namespace. Driver list: https://kubernetes-csi.github.io/docs/drivers.html

## Key Concepts
- **Dynamic provisioning** — SC controller watches the API server for new PVCs referencing it, then creates the external volume + PV on demand.
- **1:1 mapping** — a single external volume maps to exactly one PV (cannot split a 50GB volume into 2×25GB PVs).
- **No double-writes** — Kubernetes prevents multiple Pods from writing the same PV.
- **StorageClass immutability** — once deployed, an SC cannot be modified.
- **`parameters` block** — plugin-specific values; different for every plugin.
- **Default StorageClass** — used by PVCs that don't name an SC; fine for dev, but always specify an SC explicitly in production.
- **VolumeBindingMode** — `WaitForFirstConsumer` delays volume creation until a Pod mounts it (guarantees same region/zone as Pod); `Immediate` pre-creates volumes (no locality guarantee).
- **AllowVolumeExpansion** — SC property controlling whether volumes can grow.
- **Locality restrictions** — Pods usually must be in the same region/zone as the storage backend; cannot use AWS EBS on an Azure cluster.
- Terms **provisioner**, **plugin**, and **driver** are used interchangeably.

## Mental Models
- **PVC is a request, PV is the fulfillment.** App authors write PVCs (what they want); SC + CSI produce the PV (what they get) behind the scenes.
- **StorageClass = menu of storage tiers.** Define one SC per (storage type × locality × feature) combination — e.g. `fast-local`, `fast-replicated`, `slow-local`, `slow-replicated`.
- **The volume provisioning workflow (Fig 11.2):** Pod → PVC → SC → CSI plugin → backend creates device → reports back → SC creates PV mapped to device → Pod mounts PV.

## Anti-patterns
- Relying on the **default SC in production** — always specify an appropriate SC.
- Using the **legacy in-tree** plugin (e.g. `kubernetes.io/gce-pd`) — prefer CSI drivers.
- Trusting the default **`Delete` reclaim policy** for data you care about — deleting the PVC deletes the PV and external storage. Use with caution.
- Forgetting that with **`Retain`**, deleting the PVC leaves the PV and backend disk alive — failing to manually clean up incurs unwanted cloud charges.
- Expecting **block storage to support `ReadWriteMany`** — usually only file/object storage does.

## Code Examples

### StorageClass YAML (AWS EBS, encrypted SSD, Ireland)
```yaml
kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
  name: fast-local
provisioner: ebs.csi.aws.com        # AWS EBS CSI plugin
parameters:
  encrypted: "true"                 # create encrypted volumes
  type: io1                         # AWS SSD drives
  iopsPerGB: "10"                   # performance requirement
allowedTopologies:                  # where to provision volumes/replicas
  - matchLabelExpressions:
      - key: topology.ebs.csi.aws.com/zone
        values:
          - eu-west-1a              # Ireland AWS region
```

### Pod + PVC + StorageClass in one file (GKE pd-ssd)
```yaml
apiVersion: v1
kind: Pod                                   # 1. Pod
metadata:
  name: mypod
spec:
  volumes:
    - name: data
      persistentVolumeClaim:
        claimName: mypvc                    # 2. request volume via "mypvc" PVC
  containers:
    - name: ctr
      # ...<SNIP>
      volumeMounts:
        - name: data
          mountPath: /data
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mypvc                               # 3. the "mypvc" PVC
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 50Gi                         # 4. provision a 50Gi volume...
  storageClassName: fast                    # 5. ...based on "fast" SC
---
kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
  name: fast                                # 6. the "fast" StorageClass
provisioner: pd.csi.storage.gke.io          # 7. use this CSI plugin
parameters:
  type: pd-ssd                              # 8. provision pd-ssd storage
```

### Replicated SC with Retain policy (GKE regional PD)
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: sc-fast-repl
provisioner: pd.csi.storage.gke.io
parameters:
  type: pd-ssd
  replication-type: regional-pd
volumeBindingMode: WaitForFirstConsumer
reclaimPolicy: Retain
```

## Reference Tables

### Access modes
| Mode | Short | Meaning |
|------|-------|---------|
| ReadWriteOnce | RWO | Single PVC binds in read/write; further binds fail |
| ReadWriteMany | RWM | Multiple PVCs bind read/write (file/object storage; usually not block) |
| ReadOnlyMany | ROM | Multiple PVCs bind read-only |

A PV can be opened in **only one mode** at a time.

### Reclaim policies
| Policy | Behavior | Notes |
|--------|----------|-------|
| Delete | Deletes PV + external storage when PVC is released | **Default** for dynamic SC-created PVs; dangerous |
| Retain | Keeps PV + external storage after PVC deleted | Safer; manual cleanup required |

### GKE `kubectl get sc` (trimmed)
| NAME | PROVISIONER | RECLAIM | VOLUMEBINDINGMODE |
|------|-------------|---------|-------------------|
| premium-rwo | pd.csi.storage.gke.io | Delete | WaitForFirstConsumer |
| standard-rwo (def) | pd.csi.storage.gke.io | Delete | WaitForFirstConsumer |
| premium-rwx | filestore.csi.storage.gke.io | Delete | WaitForFirstConsumer |
| standard | kubernetes.io/gce-pd (legacy in-tree, avoid) | Delete | Immediate |

## Worked Example
Dynamically provision a volume via a PVC and mount it (GKE, built-in `premium-rwo` SC):

1. **Create PVC** — `pvc-prem`, 10Gi, `ReadWriteOnce`, `storageClassName: premium-rwo`.
   ```bash
   kubectl apply -f pvc-gke-premium.yml
   kubectl get pvc   # STATUS: Pending  (no PV yet)
   kubectl get pv    # No resources found
   ```
   Stays **Pending** because `premium-rwo` uses `WaitForFirstConsumer` — no volume until a Pod claims it.
2. **Create Pod** that mounts the PVC (`claimName: pvc-prem`, `mountPath: /data`):
   ```bash
   kubectl apply -f prempod.yml
   kubectl get pvc   # STATUS: Bound, VOLUME pvc-796af..., 10Gi, RWO, premium-rwo
   kubectl get pv    # pvc-796af... 10Gi RWO Delete Bound default/pvc-prem
   ```
   A matching persistent disk now exists on the GCP backend.
3. **Clean up** — `Delete` reclaim policy means removing the PVC removes PV + backend disk:
   ```bash
   kubectl delete pod volpod
   kubectl delete pvc pvc-prem
   kubectl get pv    # No resources found
   ```
   With a **`Retain`** SC instead (e.g. `sc-fast-repl`), the PV and backend disk survive PVC deletion — you must `kubectl delete pv <name>` and delete the cloud disk manually to avoid charges.

## Key Takeaways
- The trinity: **PVs map to external volumes, PVCs grant access, StorageClasses automate dynamic provisioning.**
- Each external storage system needs its **own CSI plugin**; modern plugins are out-of-tree and run as Pods in `kube-system`.
- **Dynamic provisioning** = SC controller watches for PVCs and creates volumes + PVs on demand via CSI.
- Choose **access mode** (RWO/RWM/ROM) per workload; block storage rarely supports RWM.
- **Reclaim policy** is a data-safety decision: `Delete` (default, destructive) vs `Retain` (safe, manual cleanup).
- `WaitForFirstConsumer` binding ensures volume locality matches the consuming Pod.
- StorageClasses are **immutable** — recreate to change.

## Connects To
- **Ch 10 (StatefulSets)** — stable per-Pod storage via PVC templates relies on this subsystem.
- **Ch 3** — Regional GKE cluster used for the hands-on demos.
- **ConfigMaps/Secrets** — other ways Pods consume non-persistent data via volumes.
- Cloud provider CSI drivers: `ebs.csi.aws.com`, `pd.csi.storage.gke.io`, `filestore.csi.storage.gke.io`.
