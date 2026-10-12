# Chapter 5: Virtual clusters with Namespaces

## Core Idea
Namespaces divide a single Kubernetes cluster into multiple **virtual clusters**. They provide **soft isolation** for **soft multi-tenancy** — letting tenants (apps, teams, departments) share one cluster while each gets its own users, RBAC rules, resource quotas, and policies. They are NOT a strong security boundary: a compromised workload in one Namespace can impact workloads in others.

## Frameworks Introduced
- **Soft vs. hard isolation**: Namespaces = soft (shared nodes/control plane, lightweight, cheap). Separate clusters on dedicated hardware = hard (strong isolation, more cost/overhead).
- **Imperative vs. declarative** creation and deployment (both supported because Namespaces are first-class objects in the core v1 API group).
- **Namespaced vs. cluster-scoped objects**: most objects are namespaced; some (Nodes, PersistentVolumes) are cluster-scoped and cannot be isolated.

## Key Concepts
1. **Kubernetes Namespaces ≠ kernel namespaces.** Kernel namespaces partition an OS into containers; Kubernetes Namespaces partition a cluster into virtual clusters. (Capital "N" = Kubernetes object.)
2. **Soft multi-tenancy** — multiple tenants share the cluster; the term "tenant" is loose (app, team, dept, even external customer). Most common: internal tenants in one org.
3. **No hard isolation** — Namespaces cannot stop a compromised workload from escaping; for strong isolation use separate clusters on separate hardware.
4. **default Namespace** — where new objects land if no Namespace is specified.
5. **Resource quotas & policies** — applied per Namespace, independently.
6. **First-class core v1 resource** — stable, long-standing, works imperatively and declaratively.
7. **`ns` shorthand** — substitutable for `namespace` in kubectl.
8. **`-n` / `--namespace`** — scopes a single command; `--all-namespaces` returns objects across all.
9. **kubeconfig context Namespace** — set a default Namespace so you stop typing `-n` on every command.
10. **Deleting a Namespace** cascades — deletes all objects (Pods, Services, ServiceAccounts) inside it.

## Mental Models
- A Namespace is a **virtual cluster boundary for resource and accounting purposes** — not a firewall.
- Think of Namespaces as **org-chart partitions** of a production cluster (e.g. `finance`, `hr`, `corporate-ops`).
- Choose isolation by **trust level**: trusted internal tenants → Namespaces; untrusted/external tenants → separate clusters.

## Anti-patterns
- Using Namespaces for **hard multi-tenancy** or to isolate **external/untrusted** tenants — they only provide soft isolation.
- Placing **mutually hostile workloads** (the book's Shield vs. Hydra) in the same cluster separated only by Namespaces.
- Forgetting to **reset the kubeconfig Namespace** after work — future commands silently run against a deleted/wrong Namespace and return nothing.

## Code Examples

Check which objects are namespaced (NAMESPACED column true/false):
```
$ kubectl api-resources
NAME                     SHORTNAMES   NAMESPACED   KIND
nodes                    no           false        Node
persistentvolumeclaims   pvc          true         PersistentVolumeClaim
persistentvolumes        pv           false        PersistentVolume
pods                     po           true         Pod
resourcequotas           quota        true         ResourceQuota
services                 svc          true         Service
```

List, describe, and scope:
```
$ kubectl get namespaces
$ kubectl describe ns default
$ kubectl get svc --namespace kube-system
$ kubectl get svc -n kube-system
$ kubectl get pods --all-namespaces
```

Create imperatively:
```
$ kubectl create ns hydra
namespace/hydra created
```

Create declaratively (`shield-ns.yml`):
```yaml
kind: Namespace
apiVersion: v1
metadata:
  name: shield
  labels:
    env: marvel
```
```
$ kubectl apply -f shield-ns.yml
namespace/shield created
```

Delete a Namespace (cascades to all contained objects):
```
$ kubectl delete ns hydra
namespace "hydra" deleted
```

Set / reset the default Namespace in kubeconfig:
```
$ kubectl config set-context --current --namespace shield
$ kubectl config set-context --current --namespace default
```

Target objects at a Namespace declaratively (each object sets `metadata.namespace`):
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  namespace: shield      # <<==== Namespace
  name: default
---
apiVersion: v1
kind: Service
metadata:
  namespace: shield      # <<==== Namespace
  name: the-bus
spec:
  type: LoadBalancer
  ports:
  - port: 8080
    targetPort: 8080
  selector:
    env: marvel
---
apiVersion: v1
kind: Pod
metadata:
  namespace: shield      # <<==== Namespace
  name: triskelion
```

## Reference Tables

Pre-created Namespaces on every cluster:

| Namespace         | Purpose                                                                 |
|-------------------|-------------------------------------------------------------------------|
| `default`         | Where new objects go when no Namespace is specified                     |
| `kube-system`     | Control plane components (internal DNS / `kube-dns`, metrics server)    |
| `kube-public`     | Objects that need to be readable by anyone                              |
| `kube-node-lease` | Node heartbeat / node lease management                                  |

## Worked Example
1. Create the `shield` Namespace declaratively: `kubectl apply -f shield-ns.yml`.
2. Verify it exists: `kubectl get ns`.
3. Scope kubectl to it so you skip `-n`: `kubectl config set-context --current --namespace shield`.
4. Deploy a 3-object app (ServiceAccount + Service + Pod), each manifest carrying `namespace: shield`: `kubectl apply -f app.yml`.
5. Verify objects landed there: `kubectl get pods -n shield` and `kubectl get svc -n shield` (Pod `triskelion`, Service `the-bus`).
6. Connect: `curl localhost:8080` (the Service's EXTERNAL-IP on port 8080) — no different from the default Namespace.
7. Clean up: `kubectl delete ns shield` (cascades), then reset `kubectl config set-context --current --namespace default`.

## Key Takeaways
- Namespaces = virtual clusters for **resource and accounting** division, each with its own users, RBAC, and quotas.
- They are **soft isolation only** — not safe for hard multi-tenancy or untrusted tenants.
- Most objects are namespaced; **Nodes and PersistentVolumes are cluster-scoped**.
- Work with Namespaces **imperatively (`kubectl create ns`)** or **declaratively (YAML `kind: Namespace`)**.
- Use `-n` / `--namespace` per command, `--all-namespaces` for cluster-wide views, or set a default via the kubeconfig context.
- Deleting a Namespace deletes everything inside it; always reset your context afterward.

## Connects To
- **Ch. 1–4 (Pods, Deployments, Services)**: those objects are namespaced and get deployed into Namespaces here.
- **Later chapters**: RBAC and security (per-Namespace users/permissions), ResourceQuotas and LimitRanges (per-Namespace limits), and cluster-vs-Namespace scoping.
