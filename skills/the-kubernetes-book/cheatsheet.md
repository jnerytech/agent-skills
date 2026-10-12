# Cheatsheet — The Kubernetes Book (Poulton, 2024)

A decision aid. For terms see glossary; for explanations see chapters. Every line helps you decide.

## Pick a workload controller
- Need to run an app? -> stateless (web, API, no per-Pod identity/data) -> **Deployment**
  - -> stateful (DB, KV, session store; needs same name/DNS/volume after restart) -> **StatefulSet**
  - -> one Pod per node (logging/monitoring agent, CNI) -> **DaemonSet**
  - -> run-to-completion / batch -> **Job / CronJob**

| | Deployment | StatefulSet | DaemonSet |
|---|---|---|---|
| Use for | stateless | stateful, sticky ID | node-level agent |
| Pod identity | random, interchangeable | sticky `<name>-N`, ordinal | one per node |
| Startup/scale | parallel | one at a time, ordered, ready-gated | follows nodes |
| Scale-down | any Pod | highest ordinal first | follows nodes |
| Storage | shared/none | per-Pod PVC, stays bound | per-node |
| Needs Headless Svc | no | yes (DNS per Pod) | no |

**Rule:** if the app must reconnect to *the same* identity + data after a restart -> StatefulSet. Otherwise Deployment. StatefulSet is only a framework — the app must be coded to find peers via DNS.

## Expose an app (Service type)
- Reachable only inside cluster (other Pods)? -> **ClusterIP** (default)
  - -> external, dev/test or no cloud LB -> **NodePort** (high port 30000–32767 on every node)
  - -> external, single L4 app, prod -> **LoadBalancer** (1 Svc = 1 cloud LB)
  - -> many HTTP apps behind one LB, host/path routing (L7) -> **Ingress** (fronts ClusterIP Svcs)
  - -> direct per-Pod DNS, no load-balancing (StatefulSet peers) -> **Headless** (`clusterIP: None`)

| Type | Scope | When |
|---|---|---|
| ClusterIP | internal | inter-app traffic; default |
| NodePort | external | dev/test, no cloud LB |
| LoadBalancer | external | prod, one L4 app per LB (costly at scale) |
| Ingress | external L7 | many web apps, one LB, host+path routing |

**Rule:** never connect to Pods directly (ephemeral). Always front with a Service for stable DNS/IP/port. 25 internet apps via LoadBalancer = 25 LBs -> use Ingress instead. If running a service mesh, you may not need Ingress.

## Config: ConfigMap vs Secret
- Non-sensitive config (URLs, flags, files)? -> **ConfigMap**; sensitive (passwords, tokens, certs)? -> **Secret**.
- **base64 ≠ encryption.** Secrets are only base64-encoded in the cluster store — anyone can `base64 -d` without a key. Not encrypted at rest, in flight, or in the container (always surfaces as plaintext, via in-memory tmpfs on the node).
- Real protection = EncryptionConfiguration (at-rest) + service mesh (in-flight) + RBAC + Vault. Never bake config into the image (anti-pattern).

## Storage access mode
| Mode | Abbr | Meaning |
|---|---|---|
| ReadWriteOnce | RWO | one node read/write (block storage) |
| ReadWriteMany | RWX | many read/write (file/object; **block usually can't**) |
| ReadOnlyMany | ROX | many read-only |

- PV/PVC stuck **Pending** + StorageClass uses `WaitForFirstConsumer` -> normal: no volume until a Pod claims it. Don't expect block storage to give RWX.

## RBAC scope (least privilege, deny-by-default)
- Permission needed in one Namespace? -> **Role**; across all Namespaces / cluster-scoped resource? -> **ClusterRole**.
- Same perms in many Namespaces -> define one **ClusterRole**, attach per-NS with **RoleBindings**.
- **Role/ClusterRole = what (verbs+resources); RoleBinding/ClusterRoleBinding = who (subjects).** A Role grants nothing until bound. Binding's subject name must match an authenticated username.
- Avoid binding **cluster-admin** broadly (= root: all verbs, all resources, all NS).

## Defaults the author commits to
- New objects with no NS -> `default` Namespace. Namespaces = soft isolation only, NOT a security boundary.
- Rolling update: `maxSurge` = Pods above desired, `maxUnavailable` = Pods below (e.g. 10 replicas, surge 1/unavail 1 -> 9–11 during rollout).
- StatefulSet wiring: Pod name -> PVC `<template>-<sts>-<ordinal>` -> DNS hostname; everything keys off the ordinal.

## Tells & smells
| Symptom | Likely cause |
|---|---|
| Pod `Pending` | scheduler can't place it: resources, node selector, or PVC unbound |
| PVC `Pending` | no matching PV / `WaitForFirstConsumer` (waits for Pod) |
| `Init:0/1` stuck | init container's dependency (e.g. Service) not ready |
| `CrashLoopBackOff` | app crashes on start or failing liveness probe |
| `ImagePullBackOff` | bad image name/tag or registry auth |
| `READY 9/10` mid-rollout | expected: `maxUnavailable` |
| 11 Pods in describe | expected: `maxSurge` |

## Essential kubectl
| Verb | Command |
|---|---|
| apply | `kubectl apply -f <file>` |
| list | `kubectl get pods\|deploy\|svc\|rs\|pvc\|pv` |
| inspect | `kubectl describe pod\|deploy\|svc <name>` |
| logs | `kubectl logs <pod>` |
| shell | `kubectl exec -it <pod> -- sh` |
| scale | `kubectl scale deploy <name> --replicas=N` |
| rollout status | `kubectl rollout status deploy <name>` |
| rollback | `kubectl rollout undo deploy <name>` |
| history | `kubectl rollout history deploy <name>` |
| pause/resume | `kubectl rollout pause\|resume deploy <name>` |
| expose | `kubectl expose deployment <name> --type=NodePort` |
| port-forward | `kubectl port-forward <pod> 8080:80` |
| delete | `kubectl delete -f <file>` |
| set default NS | `kubectl config set-context --current --namespace=<ns>` |
