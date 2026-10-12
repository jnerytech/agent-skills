# Chapter 2: Running Containers in Kubernetes with Pods and Deployments

## Core Idea

Kubernetes never manages containers directly — it wraps them in **Pods**, and wraps Pods in **controllers** like Deployments. This two-layer abstraction is what enables self-healing, desired-state workflows, and node-level resilience.

---

## Frameworks Introduced

- **Desired-State Workflow** (author's term): You declare the end state you want; Kubernetes reconciles the cluster to match it rather than executing imperative steps.
  - When to use: Every time you deploy or change an application. Use `kubectl apply -f` with YAML manifests instead of `kubectl run` / `kubectl create` for anything beyond a throwaway test.
  - How: (1) Write a YAML manifest specifying `apiVersion`, `kind`, `metadata`, and `spec`. (2) Run `kubectl apply -f <file>`. (3) Kubernetes compares current state to desired state and acts only on the delta.
  - Why it works: Idempotent — re-applying the same manifest is a no-op if state already matches. Failure mode: imperative commands (`run`, `create`) bypass this model, making state drift harder to detect.

- **Controller Pattern** (author's term): A controller is a Kubernetes resource that watches the API for its owned resources, compares current vs. desired state, and reconciles.
  - When to use: Whenever you need resilience, scaling, or replacement on failure. Deployments are the standard controller for stateless Pods.
  - How: (1) Create a Deployment with a `selector.matchLabels` field. (2) The Deployment controller polls the API. (3) If Pod count falls below `replicas`, it creates replacements. If it rises above (e.g., after a label re-match), it deletes the excess.
  - Why it works: Loose coupling via labels — the controller never holds direct references to Pods. Failure mode: editing Pod labels severs the controller relationship; the controller creates a new Pod while the original becomes an unmanaged orphan.

- **Label Selector Coupling** (author's term): Controllers identify their managed resources by matching labels, not by storing object IDs.
  - When to use: Understanding why deleting a Pod under a Deployment doesn't permanently remove it; troubleshooting orphaned Pods; intentional Pod adoption/ejection for debugging.
  - How: Set `spec.selector.matchLabels` in the Deployment; Pod template `metadata.labels` must match. Use `kubectl label pods <name> --overwrite <key>=<value>` to move a Pod in or out of controller scope.
  - Why it works: Controllers can discover their resources at any time without stale references. Failure mode: accidental label edits cause the Deployment to spawn extras, leaving orphaned Pods consuming resources.

---

## Key Concepts

- **Pod**: The smallest deployable unit in Kubernetes — one or more containers sharing a virtual IP, network namespace, and localhost. Runs on exactly one node.
- **Container Runtime Interface (CRI)**: The standard API Kubernetes nodes use to communicate with any container runtime (Docker, containerd, etc.). Kubernetes manages Pods; the CRI manages containers.
- **Deployment**: A controller resource (API group `apps/v1`) that manages a set of identical Pods. Handles replacement on node failure and scaling to desired replica count.
- **Label**: A key-value pair attached to any Kubernetes resource. Used by controllers as the coupling mechanism between themselves and their managed Pods.
- **Label Selector**: A query (`matchLabels` or `matchExpressions`) in a controller spec that identifies which Pods it owns.
- **Application Manifest**: A YAML (or JSON) file fully describing one or more Kubernetes resources. Declarative; can be version-controlled; deployed via `kubectl apply`.
- **`kubectl apply`**: The idempotent command for deploying manifests — creates the resource if absent, updates it if changed, no-ops if identical.
- **`kubectl port-forward`**: Tunnels traffic from a local machine port to a Pod or Deployment port. Development/debugging tool only, not for production traffic routing.
- **Pod Template**: The nested Pod specification inside a Deployment's `spec.template`. Defines the Pods the Deployment will create; must include labels matching the selector.
- **Unmanaged Pod**: A Pod with no controller. Created by `kubectl run --restart=Never` or a bare Pod manifest. If deleted, it stays deleted; no controller recreates it.

---

## Mental Models

- **Think of a Pod as a managed container wrapper**: Kubernetes owns the Pod; the CRI owns the container. If the container crashes, the node recreates it inside the still-living Pod. If the Pod is deleted, the container goes with it.
- **Think of a Deployment as a Pod thermostat**: It continuously monitors how many Pods match its label selector. Too few → creates more. Too many → deletes the excess. The desired temperature is `spec.replicas` (default 1).
- **Use `kubectl apply` when you want repeatable deployments; use `kubectl run` only for throwaway tests**: Imperative commands leave no auditable artifact; manifests can be stored in source control and re-applied anywhere.
- **Use label manipulation to eject a Pod from a Deployment for live debugging**: Change one label so the selector no longer matches → the Deployment spawns a healthy replacement while the ejected Pod stays alive for investigation.

---

## Anti-patterns

- **Deleting Pods to remove a Deployment's workload**: The Deployment controller immediately recreates the Pod. You must delete the Deployment (`kubectl delete deploy <name>`) to cascade-delete its Pods.
- **Running production workloads as bare Pods**: A bare Pod is permanently lost if its node goes offline. Deployments reschedule to another node automatically.
- **Editing Pod labels without understanding the selector**: Accidental label changes cause the Deployment to create a new Pod (now two running where one is expected), or adopt an unrelated Pod (controller then deletes one to enforce replica count).
- **Using `kubectl run` / `kubectl create` for complex apps**: These imperative commands cannot express replica counts, resource limits, health checks, or volume mounts. YAML manifests are required for anything beyond a smoke test.

---

## Code Examples

**Run a bare Pod imperatively (test use only):**
```bash
kubectl run hello-kiamol --image=kiamol/ch02-hello-kiamol --restart=Never
```
`--restart=Never` creates only the Pod, no controller.

**Wait for a Pod to be Ready:**
```bash
kubectl wait --for=condition=Ready pod hello-kiamol
```
Blocks until the Pod's Ready condition is true.

**Custom-column output — network details:**
```bash
kubectl get pod hello-kiamol \
  --output custom-columns=NAME:metadata.name,NODE_IP:status.hostIP,POD_IP:status.podIP
```
Demonstrates JSONPath field selection for Pod IP visibility.

**JSONPath output — container runtime ID:**
```bash
kubectl get pod hello-kiamol -o jsonpath='{.status.containerStatuses[0].containerID}'
```
Shows that Kubernetes references the container runtime, not the container directly.

**Port-forward to a Pod:**
```bash
kubectl port-forward pod/hello-kiamol 8080:80
```
Maps local `:8080` → Pod `:80`. Development/debug only.

**Port-forward to a Deployment (selects a Pod automatically):**
```bash
kubectl port-forward deploy/hello-kiamol-2 8080:80
```

**Create a Deployment imperatively:**
```bash
kubectl create deployment hello-kiamol-2 --image=kiamol/ch02-hello-kiamol
```

**Deploy from a local manifest:**
```bash
kubectl apply -f pod.yaml
kubectl apply -f deployment.yaml
```

**Deploy from a remote URL:**
```bash
kubectl apply -f https://raw.githubusercontent.com/sixeyed/kiamol/master/ch02/pod.yaml
```
Kubectl downloads and sends the manifest to the API; no local file needed.

**Query Deployment's Pod label selector:**
```bash
kubectl get deploy hello-kiamol-2 -o jsonpath='{.spec.template.metadata.labels}'
```

**List Pods by label:**
```bash
kubectl get pods -l app=hello-kiamol-2
```

**Overwrite a Pod label (to eject from Deployment):**
```bash
kubectl label pods -l app=hello-kiamol-2 --overwrite app=hello-kiamol-x
```

**Re-attach ejected Pod (Deployment adopts it, then deletes the extra):**
```bash
kubectl label pods -l app=hello-kiamol-x --overwrite app=hello-kiamol-2
```

**Exec into a Pod container (interactive shell):**
```bash
kubectl exec -it hello-kiamol -- sh
```

**Run a command in a Deployment's Pod (non-interactive):**
```bash
kubectl exec deploy/hello-kiamol-4 -- sh -c 'wget -O - http://localhost > /dev/null'
```

**Tail logs from a Pod:**
```bash
kubectl logs --tail=2 hello-kiamol
```

**Tail logs by label selector (all matching Pods):**
```bash
kubectl logs --tail=1 -l app=hello-kiamol-4
```

**Copy a file from a Pod to local:**
```bash
kubectl cp hello-kiamol:/usr/share/nginx/html/index.html /tmp/kiamol/ch02/index.html
```
Bidirectional; uses `tar` internally (requires `tar` in the container image).

**Delete all Pods (controllers will recreate theirs):**
```bash
kubectl delete pods --all
```

**Delete all Deployments (cascades to Pods):**
```bash
kubectl delete deploy --all
```

---

## Reference Tables

### Pod vs Deployment

| Property | Bare Pod | Deployment-managed Pod |
|---|---|---|
| Created by | `kubectl run --restart=Never` or Pod manifest | Deployment controller |
| Pod naming | Exact name from manifest/command | `<deploy-name>-<random-suffix>` |
| Node failure | Pod is lost permanently | Deployment reschedules on another node |
| Delete Pod | Stays deleted | Deployment immediately recreates it |
| Scaling | Manual, error-prone | Set `spec.replicas`; controller manages |
| Delete resource | `kubectl delete pod <name>` | `kubectl delete deploy <name>` (cascades) |

### Minimal YAML Field Requirements

| Resource | Required fields |
|---|---|
| Pod | `apiVersion: v1`, `kind: Pod`, `metadata.name`, `spec.containers[].name`, `spec.containers[].image` |
| Deployment | `apiVersion: apps/v1`, `kind: Deployment`, `metadata.name`, `spec.selector.matchLabels`, `spec.template.metadata.labels` (must match selector), `spec.template.spec.containers[].name`, `spec.template.spec.containers[].image` |

### Common kubectl Commands (Chapter 2)

| Command | Purpose |
|---|---|
| `kubectl get pods` | List all Pods |
| `kubectl describe pod <name>` | Full Pod details including events |
| `kubectl get pods -o custom-columns=...` | Filtered column output |
| `kubectl get pods -o jsonpath='...'` | JSONPath query output |
| `kubectl apply -f <file|URL>` | Declarative deploy/update |
| `kubectl port-forward <resource> <local>:<pod>` | Dev traffic tunnel |
| `kubectl exec -it <pod> -- <cmd>` | Run command in container |
| `kubectl logs [--tail=N] [-l selector]` | View container logs |
| `kubectl cp <pod>:<path> <local>` | Copy files to/from Pod |
| `kubectl label pods -l <sel> --overwrite <k>=<v>` | Change Pod labels |
| `kubectl delete pods --all` | Delete all Pods (controllers recreate) |
| `kubectl delete deploy --all` | Delete Deployments + cascade Pods |

---

## Worked Example

**Goal:** Deploy a web app first as a bare Pod, then as a Deployment-managed Pod using manifests.

**Step 1 — Bare Pod manifest (`pod.yaml`):**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: hello-kiamol-3
spec:
  containers:
    - name: web
      image: kiamol/ch02-hello-kiamol
```
```bash
kubectl apply -f pod.yaml
# Output: pod/hello-kiamol-3 created
kubectl get pods
# NAME              READY   STATUS    RESTARTS   AGE
# hello-kiamol-3   1/1     Running   0          5s
```
Re-applying the same manifest: `pod/hello-kiamol-3 unchanged` — idempotent.

**Step 2 — Deployment manifest (`deployment.yaml`):**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hello-kiamol-4
spec:
  selector:
    matchLabels:
      app: hello-kiamol-4
  template:
    metadata:
      labels:
        app: hello-kiamol-4
    spec:
      containers:
        - name: web
          image: kiamol/ch02-hello-kiamol
```
```bash
kubectl apply -f deployment.yaml
# Output: deployment.apps/hello-kiamol-4 created

kubectl get pods -l app=hello-kiamol-4
# NAME                              READY   STATUS    RESTARTS   AGE
# hello-kiamol-4-7d6b9f8c5-xk2pq   1/1     Running   0          8s
```
The Deployment created the Pod (random suffix). The bare Pod (`hello-kiamol-3`) still exists separately with no controller managing it.

**Step 3 — Verify self-healing:**
```bash
kubectl delete pod hello-kiamol-4-7d6b9f8c5-xk2pq
kubectl get pods -l app=hello-kiamol-4
# A new Pod with a different random suffix appears within seconds
```
The Deployment controller detected 0 Pods matching its selector and created a replacement.

**Step 4 — Clean up correctly:**
```bash
kubectl delete pod hello-kiamol-3        # bare Pod: stays deleted
kubectl delete deploy hello-kiamol-4     # cascades: Deployment + its Pods removed
```

---

## Key Takeaways

1. **Kubernetes manages Pods, not containers.** The CRI is responsible for containers; Kubernetes is responsible for Pod lifecycle. A failed container is repaired inside the running Pod by the node.
2. **Always use Deployments for real workloads.** Bare Pods are lost permanently on node failure. Deployments reschedule automatically.
3. **`kubectl apply` is the production workflow; `kubectl run` / `create` are for quick tests.** Manifests are declarative, idempotent, version-controllable, and URL-deployable.
4. **Controllers couple to Pods through labels, not direct references.** This is flexible but fragile: accidentally changing a Pod's label orphans it and triggers the Deployment to create a replacement.
5. **To truly delete a controlled resource, delete the controller.** Deleting just the Pod creates an instant replacement. `kubectl delete deploy` cascades to Pods.
6. **`kubectl exec`, `kubectl logs`, and `kubectl cp` work on Deployment resources directly.** You do not need to discover the random Pod name to interact with a managed Pod.
7. **Label manipulation is a legitimate debugging technique.** Eject a misbehaving Pod from its Deployment to investigate it live while the Deployment spins up a clean replacement to maintain service.

---

## Connects To

- **Ch 1**: Cluster architecture — nodes, the control plane, and the Kubernetes API that controllers use to watch and reconcile state.
- **Ch 3 (Services and Networking)**: `kubectl port-forward` is a kubectl-only workaround; Services are the production mechanism for routing traffic to Pods by label selector.
- **Ch 6 (Scaling and Controllers)**: Extends the Deployment with `spec.replicas`, HPA, and rolling updates.
- **Ch 9 (Rollouts and Rollbacks)**: Deployment-managed rollouts depend on the Pod template and label selector concepts introduced here.
- **Kubernetes Docs — Pod spec**: https://kubernetes.io/docs/reference/kubernetes-api/workload-resources/pod-v1/
- **Kubernetes Docs — Deployment spec**: https://kubernetes.io/docs/reference/kubernetes-api/workload-resources/deployment-v1/
- **Container Runtime Interface (CRI)**: https://kubernetes.io/docs/concepts/architecture/cri/
