# Chapter 6: Scaling Applications Across Multiple Pods with Controllers

## Core Idea

Kubernetes scaling is fundamentally about running more Pods. Because networking and storage are abstracted away from the compute layer, you can run many identical Pod replicas and connect them to the same Services and volumes. The platform scales up or down in seconds. Three controller types handle different scaling scenarios: Deployments (most common, stateless scale-for-load), DaemonSets (one Pod per node, scale-for-HA), and StatefulSets (covered in chapter 8). Controllers track their Pods via label selectors; Services use the same label selectors to load-balance across all matching Pods automatically.

---

## Frameworks Introduced

- **Deployment → ReplicaSet → Pod hierarchy**: A Deployment manages one or more ReplicaSets; each ReplicaSet manages Pods. When you change only the `replicas` count, the Deployment updates the existing ReplicaSet in place. When you change the Pod spec, the Deployment creates a new ReplicaSet and scales the old one to zero, enabling controlled rollouts. **Use when**: running stateless workloads that need scale-for-load or rolling updates. **Failure mode**: manually scaling with `kubectl scale` then running `kubectl apply` will revert to the YAML-declared replica count — declarative YAML always wins.

- **DaemonSet**: Runs exactly one Pod replica per node (or per subset of nodes selected by a `nodeSelector`). The control loop watches both Pod status and node membership. **Use when**: you need a Pod on every node (log collectors, metrics agents, reverse proxies for HA without heavy replication). **Failure mode**: converting from Deployment to DaemonSet without planning the order causes downtime — create the DaemonSet first so Pods are available, then delete the Deployment.

- **Object ownership and cascading deletes**: Every controller-managed object stores its owner in `metadata.ownerReferences`. Kubernetes garbage-collects orphans automatically. `kubectl delete --cascade=false` breaks the link without deleting dependents, allowing another controller to adopt them via label matching.

---

## Key Concepts

1. **Replicas**: The declared number of identical Pod copies a ReplicaSet or Deployment should maintain. The control loop continuously reconciles actual vs. desired count.

2. **ReplicaSet**: The actual scale mechanism. Owns Pods via a label selector and a Pod template. You rarely create ReplicaSets directly — Deployments do it for you.

3. **Pod template hash**: Kubernetes hashes the Pod spec template and stores the result as a label (`pod-template-hash`) on the ReplicaSet and its Pods. This lets Deployments detect whether a scaled-down ReplicaSet matches a new desired spec and reuse it instead of creating a fresh one.

4. **Service load balancing**: A Service with the same `matchLabels` selector as a ReplicaSet automatically registers an endpoint for every Pod. Scaling the ReplicaSet changes the endpoint list, and Kubernetes distributes traffic across all healthy Pods — for both external LoadBalancer traffic and internal ClusterIP traffic.

5. **`kubectl scale`**: Imperative shortcut to change replica count immediately. Fast for emergencies, but a subsequent `kubectl apply` of the YAML file will override it. Always update the YAML too.

6. **DaemonSet node targeting with `nodeSelector`**: Adding a `nodeSelector` in the Pod spec of a DaemonSet restricts it to nodes carrying that label. The DaemonSet scales to zero if no nodes match, and scales up as matching nodes appear.

7. **EmptyDir vs. HostPath at scale**: EmptyDir volumes are unique per Pod — safe for concurrent replicas but no shared state. HostPath volumes are shared by Pods on the same node — enables a shared proxy cache but only works for apps tolerant of concurrent file access (Nginx is; most apps are not).

8. **Scale speed is bounded by image pull time**: On a single node with a cached image, scaling is near-instant. On a production cluster, new Pods scheduled to nodes without the image must pull it first. Lean images matter.

9. **Cascading deletes**: Default behavior when deleting a controller — all managed Pods are also deleted. Use `--cascade=false` to leave Pods running (orphaned). A matching controller created afterward adopts them.

10. **Controller adoption**: If an orphaned Pod's labels match a new controller's `selector`, the controller adopts it, sets the `ownerReferences` metadata, and manages its lifecycle going forward.

---

## Mental Models

**"Same label selector = shared fate"**: The ReplicaSet finds its Pods, and the Service finds its backends, through the exact same label mechanism. When you scale, the Pod list grows; the Service endpoint list grows automatically. There is no explicit wiring — the labels do the coupling.

**"Deployment is a deployment manager, not a scale manager"**: The ReplicaSet is what actually holds `replicas`. The Deployment adds a higher-level orchestration layer: it creates, tracks, and scales ReplicaSets across updates. Changing `replicas` alone touches the ReplicaSet in place; changing the Pod spec creates a new ReplicaSet and retires the old one to zero. This distinction explains both rolling updates (chapter 9) and why `kubectl scale` on a Deployment is overridden by the next `kubectl apply`.

**"DaemonSet = infrastructure topology controller"**: Unlike a Deployment, a DaemonSet doesn't ask "how many Pods do I need?" — it asks "which nodes exist (and match my selector)?" It maintains exactly one Pod per qualifying node, watching node join/leave events. Think of it as a per-node process manager, not a replica manager.

**"Cascade is the default, orphan is the exception"**: Kubernetes assumes you want to clean up all owned objects when a controller is removed. The `--cascade=false` escape hatch exists for maintenance windows (e.g., take down a DaemonSet for node work without killing the Pods, then recreate it to re-adopt them).

---

## Anti-patterns

- **Scaling imperatively without updating YAML**: Running `kubectl scale --replicas=4 deploy/my-app` gives instant capacity, but the next `kubectl apply` of the Deployment YAML will revert the replica count to whatever the file says. Always update the spec file and commit it.

- **Deleting a Deployment before creating its DaemonSet replacement**: This creates a gap where no Pods serve traffic. Create the DaemonSet first (it gets added to Service endpoints), verify Pods are running, then delete the Deployment.

- **Using HostPath volumes for apps that assume exclusive file access**: Most stateful apps (databases, message queues) will corrupt data or crash if two instances write to the same directory. HostPath shared volumes work only for apps explicitly designed for concurrent access (like Nginx's proxy cache).

- **Manually editing labels on Pods managed by a controller**: Changing a Pod's label so it no longer matches the controller's selector orphans it from management. The controller will then create a new Pod to meet the replica count, leaving a zombie Pod running with no owner.

- **Creating standalone ReplicaSets instead of Deployments**: ReplicaSets lack rollout management. Use Deployments, which give you rolling updates, rollback, and change history through multiple ReplicaSets.

---

## Code Examples

```yaml
# Minimal ReplicaSet (listing 6.1 — whoami.yaml)
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: whoami-web
spec:
  replicas: 1
  selector:
    matchLabels:
      app: whoami-web
  template:
    # Pod spec follows
```

```yaml
# Deployment with explicit replicas (listing 6.2 — web.yaml)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pi-web
spec:
  replicas: 2          # defaults to 1 if omitted
  selector:
    matchLabels:
      app: pi-web
  template:
    # Pod spec follows
```

```yaml
# DaemonSet (listing 6.3 — nginx-ds.yaml)
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: pi-proxy
spec:
  selector:
    matchLabels:
      app: pi-proxy    # same label mechanism as ReplicaSet
  template:
    metadata:
      labels:
        app: pi-proxy  # must match selector
    spec:
      # Pod spec follows — no replicas field
```

```yaml
# DaemonSet with node selector (listing 6.4 — nginx-ds-nodeSelector.yaml)
spec:
  containers: # ...
  volumes: # ...
  nodeSelector:
    kiamol: ch06       # only runs on nodes labeled kiamol=ch06
```

```bash
# Deploy ReplicaSet and Service
kubectl apply -f whoami/

# Check ReplicaSet status
kubectl get replicaset whoami-web

# Scale up by applying updated spec
kubectl apply -f whoami/update/whoami-replicas-3.yaml

# Imperative scale (use sparingly)
kubectl scale --replicas=4 deploy/pi-web

# List ReplicaSets with labels (shows pod-template-hash)
kubectl get rs -l app=pi-web --show-labels

# List Pods with labels
kubectl get po -l app=pi-web --show-labels

# Check object ownership metadata
kubectl get po -o custom-columns=NAME:'{.metadata.name}',OWNER:'{.metadata.ownerReferences[0].name}',OWNER_KIND:'{.metadata.ownerReferences[0].kind}'

# Delete controller without deleting its Pods
kubectl delete ds pi-proxy --cascade=false

# Label a node to match a DaemonSet nodeSelector
kubectl label node $(kubectl get nodes -o jsonpath='{.items[0].metadata.name}') kiamol=ch06 --overwrite

# Fetch logs from all Pods matching a label
kubectl logs -l app=pi-proxy --tail 1

# Bulk cleanup using label
kubectl delete all -l kiamol=ch06
```

---

## Reference Tables

### Controller Role Comparison

| Controller | Manages | Replica Logic | Primary Use |
|---|---|---|---|
| ReplicaSet | Pods | Fixed desired count; control loop reconciles | Internal — used by Deployments |
| Deployment | ReplicaSets | Manages multiple ReplicaSets across versions | Stateless apps, rolling updates |
| DaemonSet | Pods | One per node (or per labeled node subset) | Infrastructure agents, node-local HA |
| StatefulSet | Pods | Stable identity, ordered rollout | Stateful apps (covered in ch08) |

### Scaling for Load vs. Scaling for High Availability

| Dimension | Scale for Load | Scale for HA |
|---|---|---|
| Goal | Handle more concurrent requests | Survive node/Pod failure |
| Controller | Deployment (many replicas on any nodes) | DaemonSet (one replica per node) |
| Replica count | Driven by traffic; can be high | One per node; bounded by node count |
| Storage | Stateless preferred; shared cache with caution | Each Pod may have independent storage (HostPath) |
| Scale mechanism | Update `replicas` field or `kubectl scale` | Add/remove nodes; use `nodeSelector` to restrict |
| Load balancing | Service distributes across all replicas | Service distributes to whichever node serves the request |

### Label Selector Relationships

| Resource | Uses Selector To |
|---|---|
| ReplicaSet | Find and own Pods |
| Deployment | Find and own ReplicaSets (via pod-template-hash) |
| DaemonSet | Find and own Pods; also matches against node labels |
| Service | Find backend Pods for endpoint registration |

---

## Worked Example

**Scenario**: Scale a Deployment up from 1 to 3 replicas, observe load balancing behind a Service, then use `kubectl scale` as an emergency measure and understand what happens at the next apply.

**Step 1 — Deploy the Pi web app with 2 replicas:**
```bash
kubectl apply -f pi/web/
kubectl get rs -l app=pi-web
```
The Deployment creates one ReplicaSet (`pi-web-<hash>`) with `DESIRED=2`, `READY=2`.

**Step 2 — Verify the Service distributes traffic:**
```bash
kubectl apply -f sleep.yaml
kubectl exec deploy/sleep -- sh -c 'for i in 1 2 3; do curl -w \\n -s http://pi-web:8080; done;'
```
Responses come from different Pod hostnames, confirming load balancing via the shared ClusterIP.

**Step 3 — Scale up declaratively to 3 replicas:**
```bash
kubectl apply -f pi/web/update/web-replicas-3.yaml
kubectl get rs -l app=pi-web
```
The Deployment updates the existing ReplicaSet's desired count to 3. No new ReplicaSet is created because the Pod spec is unchanged. A third Pod starts in seconds (image already on node).

**Step 4 — Change the Pod spec (add enhanced logging):**
```bash
kubectl apply -f pi/web/update/web-logging-level.yaml
kubectl get rs -l app=pi-web
```
Now two ReplicaSets appear. The original (`DESIRED=0`, `READY=0`) is retained but scaled to zero. A new ReplicaSet (`DESIRED=3`, `READY=3`) runs the updated Pod spec. Deployment waits for new Pods to be ready before scaling down old ones.

**Step 5 — Emergency imperative scale to 4:**
```bash
kubectl scale --replicas=4 deploy/pi-web
kubectl get rs -l app=pi-web   # new RS now shows DESIRED=4
```

**Step 6 — Apply YAML with replicas=3 (reverts the manual scale):**
```bash
kubectl apply -f pi/web/update/web-replicas-3.yaml
kubectl get rs -l app=pi-web   # DESIRED drops back to 3
kubectl get pods -l app=pi-web  # only 3 pods remain
```
The Deployment detects the spec matches the old ReplicaSet's pod-template-hash, scales the new RS to 0, and scales the old RS back to 3. Three new Pods run the original logging spec. The manual scale is gone — YAML is truth.

**Key observations from this walkthrough:**
- Changing `replicas` only → same ReplicaSet updated in place
- Changing Pod spec → new ReplicaSet created, old one scaled to zero
- `kubectl scale` → overridden by next `kubectl apply`
- Service automatically tracks all Pods via label selector throughout

---

## Key Takeaways

1. Controllers (Deployments, DaemonSets, ReplicaSets) own Pods via label selectors. A control loop continuously reconciles desired vs. actual Pod count.

2. Deployments manage ReplicaSets; ReplicaSets manage Pods. Always use Deployments in production — the extra abstraction enables rolling updates and rollbacks.

3. Services use the same label selector mechanism as controllers. Scaling a Deployment automatically extends the Service's endpoint list — zero extra configuration required.

4. The pod-template-hash label lets Deployments efficiently reuse scaled-down ReplicaSets when a spec reverts to a previous state, rather than creating new objects.

5. `kubectl scale` is an imperative escape hatch. It works immediately but will be overridden by the next `kubectl apply`. Always update the YAML file to match.

6. DaemonSets provide node-topology-aware HA: one Pod per node (or per labeled node subset). Their control loop watches nodes joining/leaving and node label changes, not just Pod counts.

7. Object ownership metadata (`ownerReferences`) and cascading deletes mean removing a controller removes its Pods by default. Use `--cascade=false` to orphan Pods and allow adoption by a new controller.

---

## Connects To

- **Chapter 2**: Pods and Deployments — foundational understanding of Pod templates and why you don't run Pods directly.
- **Chapter 3**: Services and networking — ClusterIP, LoadBalancer, and label selectors as the glue between compute and network.
- **Chapter 5**: Volumes and storage — EmptyDir and HostPath behavior at scale; why shared writable volumes are tricky with multiple replicas.
- **Chapter 8**: StatefulSets — the controller for stateful workloads that need stable network identity and synchronized persistent storage (the complement to DaemonSets for HA with data).
- **Chapter 9**: Rollouts and rollbacks — the full story of how Deployments manage multiple ReplicaSets during updates and how to roll back by scaling a previous ReplicaSet.
- **Chapter 10**: Helm — packaging multi-component apps (like the Pi proxy + web setup) with configurable replica counts.
