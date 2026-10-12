# Chapter 12: Empowering Self-Healing Apps

## Core Idea

Kubernetes provides three complementary mechanisms for keeping applications running without manual intervention: **container probes** (readiness and liveness) that test application health and trigger routing changes or restarts, **resource limits** (memory and CPU) that prevent runaway apps from starving nodes, and **Helm atomic upgrades** with pre/post hooks that automatically roll back failed deployments. Together, these shift operational burden from humans to the platform — but they require thoughtful configuration to avoid creating new failure modes.

---

## Frameworks Introduced

- **Readiness Probe**
  - **What:** A periodic healthcheck that determines whether a Pod should receive network traffic.
  - **When:** Always — any Pod container that serves requests should declare one.
  - **How:** `httpGet`, `tcpSocket`, or `exec` test runs on `periodSeconds` cadence; failure removes the Pod from Service endpoints without restarting it.
  - **Why / failure:** Without it, Services send traffic to unhealthy containers returning 5xx errors. Over-reliance without a liveness probe can drain all endpoints, taking the service fully offline.

- **Liveness Probe**
  - **What:** A periodic healthcheck that determines whether the container process is alive enough to keep running.
  - **When:** Any container that can enter a permanently broken state (e.g., deadlock, fatal error) without the process exiting.
  - **How:** Same `httpGet`/`exec`/`tcpSocket` mechanism, but failure causes the container to be killed and replaced (Pod restarts, same IP); `initialDelaySeconds` and `failureThreshold` prevent premature kills during startup.
  - **Why / failure:** Without it, permanently failed apps sit in Pods that never restart; with too-tight settings, healthy slow-starting apps are killed in a restart loop.

- **Resource Limits and Requests**
  - **What:** `resources.limits` caps the maximum CPU/memory a container may use; `resources.requests` declares the minimum needed, guiding the scheduler.
  - **When:** Mandatory before production; pair both on every container spec.
  - **How:** Memory limits are hard — exceeding them triggers `OOMKilled` and a Pod restart. CPU limits are soft throttles — the container slows to the cap but is not killed.
  - **Why / failure:** Without limits, a single container can exhaust node memory or CPU, crashing or starving all other workloads. Limits set too low cause perpetual `OOMKilled`/`CrashLoopBackOff`.

- **Helm Atomic Upgrades and Hooks**
  - **What:** `--atomic` flag makes `helm install`/`helm upgrade` roll back automatically if the rollout fails within the given `--timeout`. `helm.sh/hook` annotations attach Kubernetes Jobs to lifecycle events (`pre-upgrade`, `test`).
  - **When:** Use for any production release pipeline; run `helm test` as a smoke-test after successful upgrades.
  - **How:** Helm watches the Deployment rollout; if readiness probes on new Pods fail before the timeout, Helm reverts to the previous revision. Pre-upgrade Jobs run first and block the upgrade if they fail.
  - **Why / failure:** Without it, a bad update requires manual `kubectl rollout undo`; with it, the app stays on the last good revision automatically.

---

## Key Concepts

1. **Pod readiness vs. running state:** Kubernetes knows a container is *running*, but only a readiness probe tells it the *application* is healthy. Without one, the Service includes unhealthy Pods in its endpoint list.

2. **Service endpoints are dynamic:** A Service's endpoint list is rebuilt from label selectors filtered by the ready state. Pods with failing readiness probes are silently removed from (and re-added to) this list without a restart.

3. **Readiness probe failure does not trigger a restart:** The Deployment and ReplicaSet leave a not-ready Pod alone. If all Pods fail readiness, the Service has zero endpoints and the app goes offline — but no restarts happen automatically.

4. **Liveness probe failure triggers a container restart, not a Pod replacement:** The Pod (and its IP, volumes) remain; only the container is replaced. Init containers and sidecar containers re-execute on restart.

5. **`initialDelaySeconds` and `failureThreshold` prevent false positives:** Give slow-starting apps a grace period before the first probe fires, and require multiple consecutive failures before action is taken.

6. **Three probe action types:** `httpGet` (status 200–399 = success), `tcpSocket` (port open = success), `exec` (exit code 0 = success). Non-HTTP components like databases use `tcpSocket` for readiness and `exec` for liveness.

7. **Memory limits are enforced with `OOMKilled`:** When a container exceeds its memory limit, the kernel kills it and the Pod enters a restart cycle, eventually reaching `CrashLoopBackOff`.

8. **CPU limits throttle, not kill:** A container at its CPU limit simply runs slower; it is never killed for CPU overuse. CPU is specified in cores or millicores (`250m` = 0.25 core).

9. **`ResourceQuota` objects govern an entire namespace:** They set aggregate CPU/memory caps; a Pod spec that would push the namespace over quota is rejected at creation time — proactive, not reactive.

10. **`CrashLoopBackOff` signals a systemic problem:** Kubernetes applies exponential backoff to restart intervals for repeatedly failing Pods. This state usually means manual intervention is required; self-healing alone cannot recover it.

---

## Mental Models

- **Readiness = routing gate, Liveness = restart trigger:** Think of them as operating at different layers. Readiness controls the network path (L4/L7 traffic); liveness controls the compute lifecycle (container replacement). A well-configured Pod uses both in concert: readiness keeps traffic away from a broken container while liveness arranges for it to be replaced.

- **Resource limits as circuit breakers:** Just as an electrical circuit breaker isolates a fault before it spreads, memory and CPU limits contain a misbehaving container within its Pod. Without them, one bad actor can trip the entire node, taking down unrelated workloads.

- **Helm upgrade as a transactional deployment:** `helm upgrade --atomic` behaves like a database transaction — it commits (finishes the rollout) or rolls back entirely. The timeout is the transaction window. Pre-upgrade hooks are like pre-condition checks that abort before the transaction even starts.

- **Self-healing has a ceiling:** Kubernetes heals *transient* failures by rerouting or restarting. It does not heal *permanent* failures (misconfigured specs, fatal bugs, missing dependencies). Understanding which category a failure belongs to determines whether more configuration helps or human intervention is needed.

---

## Anti-patterns

- **Missing readiness probes:** The Service includes Pods regardless of application health, routing traffic to containers returning errors. The symptom is intermittent 5xx errors proportional to the unhealthy replica fraction.

- **Readiness-only configuration (no liveness probe):** Once all replicas fail the readiness probe, the Service has zero endpoints. The app is completely offline, and since no restarts are triggered, it stays that way until manual intervention. The random-number API example demonstrates this exact failure mode.

- **Liveness probe `initialDelaySeconds` too short:** Slow-starting containers are killed before they finish initializing, creating a permanent restart loop that was never caused by a real failure.

- **No resource limits in production:** Memory-hungry containers can exhaust an entire node's RAM, causing the node's `kubelet` to start evicting other Pods (OOM at the OS level). CPU-intensive containers can starve neighbours during traffic spikes.

- **Resource limits set too tightly:** Correct but conservative limits cause `OOMKilled` crashes as soon as normal load spikes, producing `CrashLoopBackOff` and reducing effective capacity — the opposite of self-healing.

- **`CrashLoopBackOff` misdiagnosis:** Operators sometimes add more liveness probes or widen limits when the real issue is a fatal application bug or misconfigured Pod spec (e.g., a container `command` override left from debugging). Self-healing tooling amplifies the restart loop rather than fixing it.

- **Helm upgrades without `--atomic` or `--timeout`:** A failed rollout leaves the Deployment in a mixed-ReplicaSet state indefinitely. The old ReplicaSet stays at partial scale, hoping the rollout eventually completes; the old pods remain but the Deployment never stabilizes.

---

## Code Examples

**Readiness probe — HTTP GET:**
```yaml
readinessProbe:
  httpGet:
    path: /healthz
    port: 80
  periodSeconds: 5
```

**Liveness probe — HTTP GET with delay and threshold:**
```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 80
  periodSeconds: 10
  initialDelaySeconds: 10
  failureThreshold: 2
```

**Readiness probe — TCP socket (database port check):**
```yaml
readinessProbe:
  tcpSocket:
    port: 5432
  periodSeconds: 5
```

**Liveness probe — exec command (Postgres readiness tool):**
```yaml
livenessProbe:
  exec:
    command: ["pg_isready", "-h", "localhost"]
  periodSeconds: 10
  initialDelaySeconds: 10
```

**Resource limits — memory only:**
```yaml
resources:
  limits:
    memory: 50Mi
```

**Resource limits — CPU only (millicores):**
```yaml
resources:
  limits:
    cpu: 250m
```

**Resource limits — both CPU and memory with requests:**
```yaml
resources:
  requests:
    memory: 32Mi
    cpu: 100m
  limits:
    memory: 50Mi
    cpu: 250m
```

**ResourceQuota for a namespace:**
```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: memory-quota
  namespace: kiamol-ch12-memory
spec:
  hard:
    limits.memory: 150Mi
```

**Helm atomic upgrade with timeout:**
```bash
helm upgrade --atomic --timeout 30s todo-list todo-list/helm/v3/todo-list/
```

**Helm pre-upgrade hook annotation on a Job:**
```yaml
annotations:
  "helm.sh/hook": pre-upgrade
  "helm.sh/hook-weight": "10"
```

**Helm test hook annotation on a Job:**
```yaml
annotations:
  "helm.sh/hook": test
```

---

## Reference Tables

### Readiness vs. Liveness Probe

| Dimension | Readiness Probe | Liveness Probe |
|---|---|---|
| **Failure action** | Remove Pod from Service endpoints | Kill container; Pod restarts |
| **Pod replaced?** | No | No (container replaced, Pod stays) |
| **IP address preserved?** | Yes | Yes |
| **Use case** | Temporary overload, slow startup, rolling updates | Deadlocked/permanently broken app process |
| **Action layer** | Network (L4/L7 routing) | Compute (container lifecycle) |
| **Deployment reaction** | None — Deployment does not replace not-ready Pods | None — Deployment does not replace restarted Pods |
| **Key risk** | All Pods failing = zero endpoints, app offline | Probe too aggressive = premature kills |

### Resource Requests vs. Limits

| Dimension | `resources.requests` | `resources.limits` |
|---|---|---|
| **Purpose** | Scheduler hint — minimum guaranteed | Hard cap on consumption |
| **Memory enforcement** | Soft — used for scheduling only | Hard — `OOMKilled` on breach |
| **CPU enforcement** | Soft — used for scheduling only | Throttle — container slows, not killed |
| **Namespace quota interaction** | Quota may track requests | Quota may track limits (see `limits.memory`) |
| **When Pod spec lacks this** | Scheduler has no placement guidance | Container can consume all node resources |

---

## Worked Example

**Scenario:** The random-number API Deployment runs two replicas. The app enters a permanent failure state after a certain number of requests, returning HTTP 500. The goal is to configure probes so that unhealthy replicas are removed from the Service and then restarted.

**Step 1 — Baseline (no probes).**
Deploy the API with two replicas and no container probes. After calling `/rng` to trigger failure, `kubectl get endpoints numbers-api` shows both Pod IPs still present. Traffic continues to route to the broken Pod, which returns 500 errors. Kubernetes sees a running container and takes no action.

**Step 2 — Add readiness probe only.**

```yaml
spec:
  containers:
  - image: kiamol/ch03-numbers-api
    readinessProbe:
      httpGet:
        path: /healthz
        port: 80
      periodSeconds: 5
```

Apply with `kubectl apply`. After triggering failure and waiting 10 seconds (`sleep 10`), `kubectl get endpoints numbers-api` shows only one IP — the unhealthy Pod's IP is removed. Traffic stops going to the broken Pod. However, the Pod is still running, just not receiving traffic.

**The edge case:** Trigger the second Pod's failure. Both Pods now fail the readiness probe. `kubectl get endpoints numbers-api` shows no IPs. The Service has zero endpoints; the app is offline. A reset call to the admin URL fails because there are no Pods to receive it. The Deployment does not replace the Pods because they are running — just not ready.

**Step 3 — Add liveness probe alongside readiness probe.**

```yaml
spec:
  containers:
  - image: kiamol/ch03-numbers-api
    readinessProbe:
      httpGet:
        path: /healthz
        port: 80
      periodSeconds: 5
    livenessProbe:
      httpGet:
        path: /healthz
        port: 80
      periodSeconds: 10
      initialDelaySeconds: 10
      failureThreshold: 2
```

Apply the updated spec. New replacement Pods start healthy. When one Pod's application fails:
1. The **readiness probe** fires within 5 seconds and removes the Pod from the Service endpoint list — traffic stops going to it.
2. The **liveness probe** fires after 10 seconds and requires 2 consecutive failures before acting — after ~20 seconds, it kills the container and the Pod restarts.
3. The new container starts healthy, passes the readiness probe, and is re-added to the Service endpoint list.

After `sleep 20` and `kubectl get pods -l app=numbers-api`, one Pod shows a restart count of 1 but both are in `Running` and `Ready` state. Both IPs are back in `kubectl get endpoints numbers-api`. The application healed itself without any manual intervention.

**Observed Kubernetes behavior summary:**
- Readiness probe failure: endpoint list shrinks, Deployment untouched.
- Liveness probe failure: container replaced, Pod IP preserved, endpoint re-added after recovery.
- Both probes failing on all replicas: app goes offline until liveness probe fires and restarts containers.

---

## Key Takeaways

1. Kubernetes knows a container is *running* but not whether the application inside is *healthy* — container probes bridge that gap.
2. Readiness and liveness probes serve distinct purposes and should almost always be used together: readiness manages traffic routing; liveness manages container restarts.
3. All three probe action types (`httpGet`, `tcpSocket`, `exec`) support both readiness and liveness, making probes applicable to any workload including databases.
4. Resource limits (`limits`) cap consumption reactively (OOMKill or throttle); resource quotas cap namespace-level consumption proactively (Pod creation blocked).
5. `helm upgrade --atomic` converts a probe-guarded rollout into an automatic rollback system — if probes never pass within the timeout, Helm reverts to the last good revision.
6. `CrashLoopBackOff` is Kubernetes protecting the cluster from wasted compute on a permanently failing container; it is a signal for human intervention, not more configuration.
7. Self-healing handles *transient* failures well; *permanent* failures (bad specs, fatal bugs) require code or configuration fixes that no amount of probes or limits can substitute.

---

## Connects To

- **Ch 7 — Multicontainer Pods:** Pod restarts triggered by liveness probes re-execute init containers and replace sidecar containers; multicontainer designs must tolerate mid-life restarts.
- **Ch 8 — Jobs and StatefulSets:** Helm test suites and pre-upgrade hooks use Kubernetes Jobs; Job `completions` and `backoffLimit` fields determine Helm's pass/fail evaluation.
- **Ch 9 — Rollouts and Rollbacks:** Readiness probes pause rolling updates until new Pods are healthy; the mixed-ReplicaSet state that appears during a failed rollout is the same state Helm's `--atomic` automatically resolves.
- **Ch 10 — Helm:** Helm lifecycle hooks (`pre-upgrade`, `test`) and the `--atomic` flag build on chart fundamentals introduced in that chapter.
- **Ch 18 — Scheduling:** `resources.requests` is the primary input the Kubernetes scheduler uses to select which node runs a Pod; under-specified requests lead to suboptimal placement and potential node overcommit.
