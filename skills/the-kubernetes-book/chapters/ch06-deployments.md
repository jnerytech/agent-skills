# Chapter 6: Kubernetes Deployments

## Core Idea
Deployments are the most popular way to run **stateless** apps on Kubernetes. They add four cloud-native features: **self-healing**, **scaling**, **rolling updates**, and **versioned rollbacks**. You wrap a Pod in a Deployment; the Deployment controller (control plane) watches it and reconciles **observed state** with **desired state**.

## Frameworks Introduced

### Deployment > ReplicaSet > Pods hierarchy
```
Deployment   (manages rollouts/rollbacks, governs ReplicaSet config)
  └─ ReplicaSet   (does self-healing + scaling via reconciliation loop)
       └─ Pods    (identical replicas, immutable)
            └─ Containers
```
- One Deployment manages one or more **identical** Pods. One microservice = one Deployment (e.g. web Deployment + cart Deployment).
- The Pod spec is embedded as a `template` inside the Deployment YAML.
- Always manage via the Deployment — never edit the ReplicaSet or Pods directly.
- Deployment resource lives in the **apps/v1** API.

### Rolling update strategy
On a Pod-template change, the Deployment controller creates a **new ReplicaSet** running the new version, then incrementally scales the new RS up while scaling the old RS down — zero downtime. Old ReplicaSets are wound to 0 but kept (config intact) for rollback.

## Key Concepts
- **Desired state** = what you want; **observed state** (a.k.a. actual/current state) = what you have. Goal: they always match.
- **Reconciliation** — a controller loop that drives observed state back to desired state (adds Pods if too few, kills if too many). Powers self-healing, scaling, rollouts, rollbacks alike.
- **Declarative model** — you declare the end goal in YAML; Kubernetes decides *how*. Strongly preferred over the **imperative model** (long command lists, no desired state, no self-healing).
- **Immutability** — Pods are immutable. Every "update" is a **replacement** (delete old, create new). You cannot change a Deployment's `selector`/labels after creation.
- **Labels & selectors** — Deployment `spec.selector.matchLabels` must match the Pod template's labels (`app=hello-world`). This is how controllers find Pods they own.
- **pod-template-hash** — system-generated label added by controllers (a hash of the Pod template). Connects Deployment→ReplicaSet→Pods and stops controllers from seizing pre-existing static Pods with matching labels. ReplicaSet selectors include it; Deployment selectors don't. Never modify it.
- **Autoscalers** — HPA (adds/removes Pods, installed by default), CA (adds/removes nodes, installed by default), VPA (resizes Pod CPU/mem, not default, disruptive). Combining them = *multi-dimensional autoscaling*.

## Mental Models
- **Chocolate cake analogy** — Declarative: "Give me a cake for ten people." Imperative: "Drive to store, buy eggs, preheat oven, if fan-assisted bake 30 min else 40..." Declarative leaves the *how* to Kubernetes.
- **Car API analogy** — A microservice exposes a stable API (steering wheel + pedals). You can re-map the engine / swap the exhaust (rollout) without the driver (client) learning anything new — provided releases stay **backward and forward compatible**.
- A rollback is just an update where the "new" image is an older one — same strategy rules apply.

## Anti-patterns
- Scaling imperatively (`kubectl scale`) then leaving the YAML out of sync — a later `kubectl apply` resets replicas to the manifest's value. Keep manifests in sync with the live cluster; change things declaratively.
- Managing ReplicaSets or Pods directly instead of via the Deployment.
- Using `kubectl rollout undo` (imperative) without then updating source YAML to match.
- Too-low `minReadySeconds` — risks replacing all replicas with broken ones before failures surface.
- Excessive `revisionHistoryLimit` — bloats the object on large/busy clusters.

## Code Examples

### Deployment YAML (`deploy.yml`)
```yaml
kind: Deployment
apiVersion: apps/v1
metadata:
  name: hello-deploy            # must be a valid DNS name
spec:
  replicas: 10                  # desired Pod count
  selector:
    matchLabels:
      app: hello-world          # must match template labels
  revisionHistoryLimit: 5       # keep last 5 ReplicaSets for rollback
  progressDeadlineSeconds: 300  # 5-min window per replica before "stalled"
  minReadySeconds: 10           # wait 10s between replica swaps
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  template:                     # Pod spec below
    metadata:
      labels:
        app: hello-world
    spec:
      containers:
      - name: hello-pod
        image: nigelpoulton/k8sbook:1.0
        ports:
        - containerPort: 8080
```

### kubectl commands
```bash
kubectl apply -f deploy.yml                 # create / update Deployment
kubectl get deploy hello-deploy             # READY UP-TO-DATE AVAILABLE
kubectl describe deploy hello-deploy
kubectl get rs                              # ReplicaSets (name = deploy + hash)
kubectl describe rs hello-deploy-54f5d46964

# Scale (imperative — declarative preferred: edit YAML + re-apply)
kubectl scale deploy hello-deploy --replicas 5

# Rollout
kubectl rollout status   deployment hello-deploy
kubectl rollout pause    deploy hello-deploy
kubectl rollout resume   deploy hello-deploy
kubectl rollout history  deployment hello-deploy

# Rollback (imperative; remember to sync YAML afterward)
kubectl rollout undo deployment hello-deploy --to-revision=1

kubectl get pods --show-labels              # shows pod-template-hash
kubectl delete -f deploy.yml                # clean up
```

## Reference Tables

### Rolling update parameters
| Field | Meaning | Effect with `replicas: 10` |
|---|---|---|
| `strategy.type` | `RollingUpdate` (default) or `Recreate` | — |
| `maxSurge: 1` | Max Pods **above** desired during rollout | up to 11 |
| `maxUnavailable: 1` | Max Pods **below** desired during rollout | down to 9 |
| (net effect) | surge − unavailable window | **2 Pods updated at a time** |
| `minReadySeconds: 10` | Throttle between replica swaps | 10s wait each |
| `progressDeadlineSeconds: 300` | Per-replica start window before "stalled" | 5 min each |
| `revisionHistoryLimit: 5` | Old ReplicaSets kept for rollback | last 5 revisions |

### Inspection output cues
| Output | Tells you |
|---|---|
| `READY 9/10` mid-rollout | result of `maxUnavailable: 1` |
| `11 total` in describe | result of `maxSurge: 1` |
| `deployment.kubernetes.io/revision: 2` | current revision number |
| `Progressing ... DeploymentPaused` | rollout paused |
| RS name hash | crypto-hash of the Pod template |

## Worked Example
1. **Deploy**: `kubectl apply -f deploy.yml` → Deployment + 1 ReplicaSet + 10 Pods (image `1.0`). Expose with a LoadBalancer Service (`lb.yml`) on port 8080.
2. **Scale down (imperative)**: `kubectl scale deploy hello-deploy --replicas 5` → 5/5. Now YAML (10) is out of sync.
3. **Re-sync (declarative)**: `kubectl apply -f deploy.yml` → back to 10/10. (Scaling is near-instant; rollouts are not.)
4. **Rolling update**: edit image to `nigelpoulton/k8sbook:2.0`, `kubectl apply -f deploy.yml`. Controller creates a 2nd ReplicaSet, replaces 2 Pods at a time with 10s gaps. Watch with `kubectl rollout status`. Optionally `pause`/`resume`. App page changes "Kubernetes rocks!" → "WebAssembly is coming!"
5. **Rollback**: `kubectl rollout history` shows revisions 1 & 2. Old RS still references `1.0`. `kubectl rollout undo deployment hello-deploy --to-revision=1` winds the old RS back up using the same rolling rules.
6. **Clean up**: `kubectl delete -f deploy.yml -f lb.yml`.

## Key Takeaways
- Deployments = stateless apps + self-healing + scaling + rollouts + rollbacks; defined in **apps/v1**, run by a reconciliation-loop controller.
- It's the **ReplicaSet** (not the Deployment) that actually creates/terminates/counts Pods — but you only ever configure it through the Deployment.
- Always work **declaratively**; keep manifests in sync with the cluster.
- Rollouts and rollbacks are both controlled **replacements** governed by `strategy` (`maxSurge`/`maxUnavailable`), `minReadySeconds`, and `progressDeadlineSeconds`.
- Old ReplicaSets are kept at 0 replicas (per `revisionHistoryLimit`) so rollbacks are instant to configure (though not instant to execute).
- Design apps loosely coupled via APIs and backward/forward compatible for true zero-downtime updates.

## Connects To
- **Ch 5 (Pods)** — the unit a Deployment wraps and templates.
- **Ch 7 (Services)** — needed to expose Deployment Pods; selector labels tie them together.
- **HPA / CA / VPA** — automated scaling layered on top of Deployments.
- Cluster store as the **record of intent**; control-plane controllers as the reconciliation engine.
