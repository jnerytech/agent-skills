# Chapter 9: Managing App Releases with Rollouts and Rollbacks

## Core Idea

Every production Kubernetes workflow involves far more updates than fresh deployments. Containerized apps inherit release cadences from base images — OS patches, runtime upgrades, security fixes — so you need a repeatable, low-risk update process. Kubernetes bakes rollout management into Deployments, DaemonSets, and StatefulSets: a structured mechanism to replace Pods progressively, track revision history, and revert to a known-good state when something breaks. Understanding update strategies and their parameters is the single biggest lever for reducing deployment-caused downtime.

---

## Frameworks Introduced

- **RollingUpdate Strategy (Deployment)**: The default update strategy — gradually scales up a new ReplicaSet while scaling down the old one.
  - **When**: All Deployment updates where you want zero-downtime releases.
  - **How**: Set `strategy.type: RollingUpdate`; tune `maxSurge`, `maxUnavailable`, `minReadySeconds`.
  - **Failure**: Defaults are aggressive (25%/25%). Without tuning, a bad image can break a quarter of your fleet before anyone notices.

- **Recreate Strategy (Deployment)**: Scales old ReplicaSet to zero before creating the new one.
  - **When**: Only when two versions absolutely cannot coexist (e.g., breaking database schema migration).
  - **Failure**: Guarantees downtime if the new image is broken — old Pods are gone before new ones are validated.

- **OnDelete Strategy (DaemonSet / StatefulSet)**: Controller waits for Pods to be deleted externally; only then creates replacements from the new spec.
  - **When**: Hardware-coupled Pods that need explicit teardown before replacement.
  - **How**: Set `updateStrategy.type: OnDelete`; manage deletions externally.

- **Partitioned StatefulSet Update**: Rollout stops at a defined `partition` index; Pods with index ≥ partition are updated, lower indices are left on the old spec.
  - **When**: Clustered stateful apps (databases) where you need to validate secondaries before touching the primary.
  - **How**: Set `updateStrategy.rollingUpdate.partition: N`; verify; then apply with lower/no partition.

- **Blue-Green Deployment (manual)**: Both old and new Deployment objects run simultaneously; a Service label-selector switch activates one version.
  - **When**: UX changes where dual-version coexistence confuses users, or organisations transitioning from big-bang deployments.
  - **Failure**: Compute-intensive (two full copies running); no built-in rollout history; requires careful label hygiene.

---

## Key Concepts

1. **Rollout vs. Replica Change**: Only changes to the Pod spec trigger a rollout (new ReplicaSet). Scaling replicas up/down mutates the existing ReplicaSet with no revision entry in rollout history.

2. **ReplicaSet Retention**: Deployments retain old (empty) ReplicaSets — 10 by default (`revisionHistoryLimit`). Each retained ReplicaSet corresponds to a rollout revision that can be targeted for rollback.

3. **`kubectl rollout` command family**: The primary tool for observing and managing releases.
   - `kubectl rollout status deploy/<name>` — streams progress; exits 0 on completion.
   - `kubectl rollout history deploy/<name>` — lists revisions with optional change-cause annotation.
   - `kubectl rollout undo deploy/<name>` — reverts to the previous revision.
   - `kubectl rollout undo deploy/<name> --to-revision=N` — reverts to a specific revision.
   - `kubectl rollout pause/resume deploy/<name>` — halts or continues an in-flight rollout.

4. **`--record` flag**: Saves the triggering `kubectl` command as the `change-cause` annotation on the revision. Useful when YAML filenames are meaningful; less useful when deploying entire directories.

5. **`maxSurge`**: Maximum number of extra Pods (above `replicas`) that can exist during a rolling update. Accelerates new-ReplicaSet scale-up. Can be an integer or percentage. Cannot both be zero with `maxUnavailable`.

6. **`maxUnavailable`**: Maximum number of Pods that can be unavailable during the update. Accelerates old-ReplicaSet scale-down. Setting to `0` ensures capacity is never reduced (create-first approach).

7. **`minReadySeconds`**: Seconds a new Pod must stay up with no container crashes before being considered Ready for rollout purposes. Default is `0` (instant). Guards against fast-crashing images that briefly appear healthy.

8. **`progressDeadlineSeconds`**: Time limit for the rollout to make forward progress (default 600 s). Exceeding it sets a condition flag on the Deployment but does NOT trigger automatic rollback as of Kubernetes 1.19.

9. **Mutable vs. Immutable ConfigMaps**: If you update a ConfigMap in-place, the Deployment doesn't change, so no rollout is recorded and no rollback is possible. Immutable configs use versioned names (e.g., `app-config-v2`), bundled with a Deployment update — making the config change part of the rollout history.

10. **DaemonSet Rolling Update**: No `maxSurge` — nodes never run two Pods simultaneously. Only `maxUnavailable` controls parallelism. Updates are always delete-then-create, so a single-node cluster briefly loses the DaemonSet Pod.

11. **StatefulSet Rolling Update order**: Proceeds from the highest ordinal index downward to 0. Pod 0 (typically the primary in a cluster) is updated last.

---

## Mental Models

**The Seesaw**: `maxSurge` and `maxUnavailable` work together like a seesaw. Raising `maxSurge` accelerates creating new Pods; raising `maxUnavailable` accelerates removing old ones. They operate simultaneously, which means at peak you could have `replicas + maxSurge` total Pods. Setting both to `0` is invalid. Tuning one high and the other low shifts the strategy toward create-first or remove-first respectively.

**Rollback Confuses Labels, Not Images**: The revision history records the full Pod spec, not just a version label you set. If you mix imperative commands (e.g., `kubectl set image`) with declarative YAML (which sets version labels), a rollback to a specific revision restores the image from that spec — which may not match the version label. This is why all-imperative or all-declarative discipline matters.

**Stuck Update as a Safety Net**: When `maxUnavailable=1` and `maxSurge=1`, a failing image causes the rollout to stall — one broken Pod exists alongside the original Pods (minus one). The app keeps serving traffic at slightly reduced capacity. This is the correct failure mode: it prevents a bad image from propagating further without manual intervention. Kubernetes does NOT auto-rollback; you must run `kubectl rollout undo`.

**Partition as a Staged Gate**: For StatefulSets, `partition` acts like a feature flag for the rollout itself. You can roll out to secondaries, validate, then lower the partition to include the primary. Each successive `apply` with a lower partition value is a deliberate, operator-controlled gate rather than an automatic wave.

---

## Anti-patterns

- **Using Recreate in production without a hard architectural reason**: It guarantees downtime. Even for schema migrations there are better patterns (init containers, schema-compatible migrations).
- **Mixing `kubectl set image` with YAML-managed releases**: The declarative YAML becomes out of sync, and rollback revisions reference state you didn't intend. Always follow up imperative commands with YAML updates.
- **Leaving `minReadySeconds: 0`**: Fast-crashing images may briefly pass readiness checks, causing the rollout to proceed before the failure is apparent.
- **Mutable ConfigMaps for configuration that needs rollback**: A config-only hot reload means there is no Deployment revision to revert to — you lose rollback capability.
- **Relying on `progressDeadlineSeconds` as an automatic rollback trigger**: As of 1.19 it only sets a condition flag. Operator action is still required.
- **Including `version` labels in the Deployment selector**: Selectors are immutable after creation. If `version` is part of `spec.selector.matchLabels`, you can never update the app. Keep selectors minimal (e.g., just `app` name); use version labels on the Pod spec only.

---

## Code Examples

**RollingUpdate strategy block (Deployment):**
```yaml
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 1
  minReadySeconds: 10
  revisionHistoryLimit: 5
  selector:
    matchLabels:
      app: vweb          # selector: stable, minimal labels only
  template:
    metadata:
      labels:
        app: vweb
        version: v2      # version label on Pod spec, not in selector
```

**Recreate strategy block:**
```yaml
spec:
  replicas: 3
  strategy:
    type: Recreate       # scales old RS to 0 before creating new RS
```

**StatefulSet partitioned rolling update:**
```yaml
spec:
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      partition: 1       # only Pods with index >= 1 are updated
```

**DaemonSet rolling update:**
```yaml
spec:
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1  # update one node at a time
```

**DaemonSet OnDelete strategy:**
```yaml
spec:
  updateStrategy:
    type: OnDelete       # controller waits for external Pod deletion
```

**Imperative image update (use sparingly; sync YAML afterward):**
```
kubectl set image deployment/vweb web=kiamol/ch09-vweb:v2
```

**Rollout commands:**
```
kubectl rollout status deploy/vweb
kubectl rollout history deploy/vweb
kubectl rollout undo deploy/vweb
kubectl rollout undo deploy/vweb --to-revision=2
kubectl rollout pause deploy/vweb
kubectl rollout resume deploy/vweb
kubectl apply -f vweb-v2.yaml --record
```

**Watch Pods during rollout:**
```
kubectl get po -l app=vweb --watch
```

**Map ReplicaSets to revisions (custom columns):**
```
kubectl get rs -l app=vweb -o=custom-columns=NAME:.metadata.name,REPLICAS:.status.replicas,REVISION:.metadata.annotations.deployment\.kubernetes\.io/revision
```

**Dry-run a rollback:**
```
kubectl rollout undo deploy/vweb --dry-run
```

---

## Reference Tables

### RollingUpdate vs. Recreate

| Dimension | RollingUpdate | Recreate |
|---|---|---|
| Downtime risk | Low (tunable) | Guaranteed during update |
| Multi-version coexistence | Yes — old and new Pods run simultaneously | No — clean cutover |
| Rollback speed | Scale up old RS (seconds–minutes) | Same as a new deploy |
| Use case | General-purpose; production default | Strict single-version requirement (rare) |
| Config required | `maxSurge`, `maxUnavailable`, `minReadySeconds` | None (single `type: Recreate` field) |

### maxSurge vs. maxUnavailable Effects

| Setting | Value | Effect |
|---|---|---|
| `maxSurge: 0, maxUnavailable: 1` | Remove-first | Old Pod deleted before new one created; brief reduced capacity; no extra nodes needed |
| `maxSurge: 1, maxUnavailable: 0` | Create-first | New Pod created and ready before old one is removed; full capacity maintained; extra node capacity needed |
| `maxSurge: 1, maxUnavailable: 1` | Parallel | One old Pod removed and one new Pod created simultaneously; fastest; brief ±1 capacity swing |
| Both `0` | Invalid | Kubernetes rejects the spec |
| Both `25%` (defaults) | Balanced | Up to 25% extra Pods created, up to 25% removed at once |

### Controller Update Strategy Comparison

| Controller | Default Strategy | Surge Option | Unavailable Option | Ordered? |
|---|---|---|---|---|
| Deployment | RollingUpdate | `maxSurge` | `maxUnavailable` | No |
| DaemonSet | RollingUpdate | None (no surge) | `maxUnavailable` | No |
| StatefulSet | RollingUpdate | None | None (always 1 at a time) | Yes, descending index |

---

## Worked Example

**Scenario**: Deploy a web app, roll out a broken image, observe the stuck update, then roll back.

**Step 1 — Initial deploy:**
```
kubectl apply -f vweb/vweb-v1.yaml
kubectl get rs -l app=vweb          # one RS, 3 replicas
kubectl rollout history deploy/vweb # revision 1 only
```

**Step 2 — Apply a rolling update with safety settings:**
```yaml
# vweb-rollingUpdate-v2.yaml
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 1
  minReadySeconds: 10
  template:
    spec:
      containers:
      - name: web
        image: kiamol/ch09-vweb:v2
```
```
kubectl apply -f vweb-rollingUpdate-v2.yaml --record
kubectl rollout status deploy/vweb   # streams Pod readiness
```
Rollout completes: new RS at 3 replicas, old RS at 0. `rollout history` shows revision 2.

**Step 3 — Deploy a broken image (v3):**
```
kubectl apply -f vweb-rollingUpdate-v3.yaml --record
kubectl get po -l app=vweb
# Output: 2 running (old), 1 in CrashLoopBackOff (new)
kubectl rollout status deploy/vweb
# Hangs — rollout stalled; app still serves at reduced capacity
```
With `maxUnavailable=1`, only one old Pod was removed. With `maxSurge=1`, one new (broken) Pod was created. The Deployment cannot progress further: old RS stays at 2, new RS stays at 1 with failing Pods. App is degraded but not down.

**Step 4 — Identify which revision to restore:**
```
kubectl rollout history deploy/vweb
# REVISION  CHANGE-CAUSE
# 1         ...
# 2         kubectl apply -f vweb-rollingUpdate-v2.yaml --record
# 3         kubectl apply -f vweb-rollingUpdate-v3.yaml --record

kubectl get rs -l app=vweb -o=custom-columns=NAME:.metadata.name,REPLICAS:.status.replicas,REVISION:.metadata.annotations.deployment\.kubernetes\.io/revision
```

**Step 5 — Roll back to revision 2:**
```
kubectl rollout undo deploy/vweb --dry-run   # see what will happen
kubectl rollout undo deploy/vweb --to-revision=2
kubectl rollout status deploy/vweb           # completes quickly — old RS already exists
curl $(cat url.txt)                          # v2 response confirmed
```
The revision 2 ReplicaSet was retained (empty, at 0 replicas). Kubernetes simply scales it back up to 3 and scales the broken RS down to 0 — much faster than a fresh deploy.

---

## Key Takeaways

1. **Pod spec changes trigger rollouts; replica count changes do not.** Know which YAML fields cause a new revision before applying updates.
2. **Tune `maxSurge` and `maxUnavailable` deliberately.** Defaults (25%/25%) are aggressive. Use `maxUnavailable: 0` to guarantee no capacity reduction; use `maxSurge: 0` to avoid needing spare compute.
3. **`minReadySeconds` is your crash-detection buffer.** Set it in every production Deployment to catch images that fail after a brief healthy period.
4. **Kubernetes does NOT auto-rollback.** A failed rollout stalls; it does not revert. You must run `kubectl rollout undo` manually. Build this into your CI/CD runbooks.
5. **Choose mutable vs. immutable ConfigMaps consciously.** Mutable enables hot reload but sacrifices rollback; immutable versioned names preserve full rollout history.
6. **Blue-green deployment is a valid stepping-stone**, especially for UX-breaking changes or teams new to Kubernetes — but it doubles compute cost and lacks automatic rollout history.
7. **StatefulSet partitions enable safe staged rollouts for clustered data.** Validate secondaries first, then lower the partition to include the primary in a final apply.

---

## Connects To

- **Chapter 4 (ConfigMaps and Secrets)**: Mutable vs. immutable config strategies directly determine whether configuration changes appear in rollout history.
- **Chapter 6 (Scaling and Controllers)**: ReplicaSets are the underlying object that rollouts manage; understanding desired vs. current replica counts is prerequisite knowledge.
- **Chapter 7 (Multi-container Pods)**: Init containers can replace some Recreate-strategy use cases (e.g., schema migrations) allowing RollingUpdate to be used instead.
- **Chapter 8 (StatefulSets and Jobs)**: StatefulSet ordered semantics (Pod 0 = primary) explain why rollouts proceed from highest index downward.
- **Chapter 12 (Self-healing and Probes)**: Readiness and liveness probes interact with rollout health checks; `minReadySeconds` waits for a probe-passing Pod to remain stable.
- **Chapter 15 (Network Ingress)**: Advanced traffic routing (sticky sessions, canary weights) builds on rolling update concepts to solve the dual-version UX problem.
