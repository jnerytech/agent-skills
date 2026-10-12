# Chapter 7: Extending Applications with Multicontainer Pods

## Core Idea

A Pod is a shared virtual environment — shared network and optional shared filesystem — that can host more than one container. Helper containers (sidecars, adapters, ambassadors, init containers) run alongside or before the application container, extending its behaviour without touching its code or image. The result is that even a legacy app that has no concept of Kubernetes can be made to conform to the platform's expectations for configuration ingestion, log emission, health checking, metrics, and controlled network access.

---

## Frameworks Introduced

- **Sidecar pattern**
  - _What_: One or more helper containers that run in parallel with the app container inside the same Pod.
  - _When_: Any time you need to augment a running app — add logging relay, expose a health endpoint, stream metrics.
  - _How_: Define additional entries in `spec.containers[]`; they start together and all must be Ready before the Pod is Ready.
  - _Why / failure_: Every sidecar is a new failure mode. If a sidecar crashes on startup, the whole Pod is not Ready and receives no Service traffic.

- **Adapter pattern** (specialisation of sidecar)
  - _What_: A sidecar that translates app-internal behaviour (e.g., file-based logging) into the form the platform expects (stdout stream).
  - _When_: Legacy apps that write logs to files, use proprietary config formats, or lack health/metrics endpoints.
  - _How_: Mount the same EmptyDir volume in app container (write) and adapter sidecar (read-only); sidecar tails the file and echoes to stdout.
  - _Why / failure_: Introduces a lag between app write and Kubernetes seeing the log. Disk space is consumed until the Pod is replaced.

- **Ambassador pattern** (specialisation of sidecar)
  - _What_: A proxy sidecar that intercepts and controls all outgoing network traffic from the app container.
  - _When_: You want service discovery, address remapping, retries, traffic encryption, or outbound access control without changing app code.
  - _How_: Set `http_proxy=http://localhost:<port>` in the app container; configure the proxy sidecar to map localhost URLs to real cluster addresses and block everything else.
  - _Why / failure_: Complex proxy configuration can silently block legitimate traffic; requires thorough testing of the URI map.

- **Init container pattern**
  - _What_: Containers in `spec.initContainers[]` that run to completion, in sequence, before any app container starts.
  - _When_: Environment preparation — writing config files, fetching secrets, cloning repos, running DB migrations.
  - _How_: Each init container must exit 0 before the next begins; all must succeed before `spec.containers[]` are started.
  - _Why / failure_: A failing init container blocks the entire Pod indefinitely; a misconfigured init container prevents a rolling update from completing while the old ReplicaSet stays up.

---

## Key Concepts

1. **Shared network namespace**: All containers in a Pod share the same IP address. They communicate via `localhost:<port>`. External Services route to the Pod IP; whichever container listens on that port handles the request.

2. **Shared filesystem via volumes**: Volumes are defined at the Pod level (`spec.volumes[]`) and mounted per-container (`volumeMounts`). Different containers can mount the same volume with different access levels (`readOnly: true`).

3. **EmptyDir as scratch pad**: The most common volume type for inter-container communication. Ephemeral — destroyed when the Pod is deleted. Cheap, fast, and zero-config.

4. **Init containers vs sidecar containers**: Init containers are in `spec.initContainers[]`, run sequentially to completion before `spec.containers[]` start. Sidecars are in `spec.containers[]` and run in parallel with the app.

5. **Pod-level readiness**: The Pod is not Ready until every container in `spec.containers[]` reports Ready. Init containers must all exit 0 first.

6. **Environment variables are per-container**: Each container has its own isolated set of env vars. An init container's `APP_ENVIRONMENT=TEST` is invisible to app containers in the same Pod.

7. **Volume mount overwrites the image directory**: When a volume is mounted at a path that already exists in the image, the image content at that path is hidden. Init containers exploit this — they write a config file to an EmptyDir, and the app container mounts that EmptyDir over the directory where the app looks for config, shadowing the baked-in default.

8. **`shareProcessNamespace: true`**: An opt-in Pod setting that lets every container see every other container's processes. Required for sidecars that need to introspect app-process metrics. Use with caution — any container can kill processes in other containers.

9. **Init container restart semantics**: If a Pod is replaced, all init containers run again — init logic must be idempotent. Changing an init container image restarts the Pod and re-runs all init containers. Changing only an app container image replaces only app containers; init containers do not re-run.

10. **Pod is one logical component**: Do not bundle independent app components (e.g., Nginx + WordPress + MySQL) in a single Pod. Each component needs its own Pod so it can be scaled, updated, and managed independently.

---

## Mental Models

1. **The Pod as a shared machine, containers as processes**: Think of the Pod as a lightweight VM. Containers are like processes on that machine — they share the NIC (same IP) and can share parts of the disk (mounted volumes), but each has its own filesystem root and env vars. Init containers are like boot scripts that must complete before the main services start.

2. **The relay chain for legacy apps**: Visualise a three-stage chain: (a) init container reads from ConfigMaps/Secrets/env vars and writes a single merged config file to an EmptyDir; (b) app container starts, reads the config file from the EmptyDir as if it were its own; (c) sidecar adapter tails the app's log file from the same (or another) EmptyDir and relays lines to stdout. The app never changes; the platform wraps it.

3. **Sidecars as transparent middleware**: The ambassador sidecar makes the app think it is talking to `localhost`. The app does not know a proxy exists. This is analogous to an HTTP intercepting proxy or a service mesh data-plane — it sits in the network path invisibly and can enforce policy, remap addresses, and log traffic.

4. **Failure blast radius is the Pod**: Adding more containers multiplies failure modes. An init container failure blocks a rolling update in place (old ReplicaSet stays; new one never becomes Ready). A crashing sidecar marks the Pod not-Ready, removing it from Service endpoints. Design for failure at each container boundary.

---

## Anti-patterns

- **Multiple independent apps in one Pod**: Running a web server and an API server in the same Pod prevents independent scaling and updates. A Pod is one logical component.
- **Non-idempotent init containers**: Init containers run again on every Pod restart or replacement. Writing data that conflicts with a previous run will break the Pod.
- **Sidecars that share env vars with the app**: Environment variables are container-scoped. Do not assume a value set in one container is visible to another — pass shared data through volumes instead.
- **Mounting init-container-prepared files over broad directories**: If the app stores binaries and config in the same directory, mounting an EmptyDir over it will hide the binaries. Ensure the config path is isolated.
- **Ignoring sidecar resource costs**: Even a `tail -f` sidecar consumes memory and CPU. Multiply by the number of Pods across a cluster and the overhead becomes significant.
- **No failure-scenario testing for multicontainer Pods**: Deployment checks that only verify the Deployment object (`kubectl get deploy`) can show a successful rollout when the underlying new Pods are stuck in init-container failure loops.

---

## Code Examples

### EmptyDir shared volume between two sidecars (read-write / read-only)

```yaml
spec:
  containers:
    - name: sleep
      image: kiamol/ch03-sleep
      volumeMounts:
        - name: data
          mountPath: /data-rw          # writable mount
    - name: file-reader
      image: kiamol/ch03-sleep
      volumeMounts:
        - name: data
          mountPath: /data-ro
          readOnly: true               # read-only mount of same volume
  volumes:
    - name: data
      emptyDir: {}
```

### Init container writing a config file; app container reading it

```yaml
spec:
  initContainers:
    - name: init-config
      image: kiamol/ch03-sleep        # image has jq
      command:
        - sh
        - -c
        - "cat /config-in/appsettings.json | jq --arg APP_ENV \"$APP_ENVIRONMENT\" '.Application.Environment=$APP_ENV' > /config-out/appsettings.json"
      env:
        - name: APP_ENVIRONMENT
          value: TEST
      volumeMounts:
        - name: config-map
          mountPath: /config-in       # ConfigMap volume (read)
        - name: config-dir
          mountPath: /config-out      # EmptyDir volume (write)
  containers:
    - name: timecheck
      image: kiamol/ch07-timecheck
      volumeMounts:
        - name: config-dir
          mountPath: /config          # same EmptyDir, shadows image default
  volumes:
    - name: config-map
      configMap:
        name: timecheck-config
    - name: config-dir
      emptyDir: {}
```

### Adapter sidecar tailing a log file to stdout

```yaml
- name: logger
  image: kiamol/ch03-sleep
  command: ['sh', '-c', 'tail -f /logs-ro/timecheck.log']
  volumeMounts:
    - name: logs-dir
      mountPath: /logs-ro
      readOnly: true
```

### Ambassador sidecar — app routes all traffic through localhost proxy

```yaml
- name: web
  image: kiamol/ch03-numbers-web
  env:
    - name: http_proxy
      value: http://localhost:1080    # all outbound goes through ambassador
    - name: RngApi__Url
      value: http://localhost/api     # app uses localhost address

- name: proxy
  image: kiamol/ch07-simple-proxy
  env:
    - name: Proxy__Port
      value: "1080"
    - name: Proxy__Request__UriMap__Source
      value: http://localhost/api
    - name: Proxy__Request__UriMap__Target
      value: http://numbers-api/sixeyed/kiamol/master/ch03/numbers/rng
```

### Shared process namespace

```yaml
spec:
  shareProcessNamespace: true         # all containers see all processes
  containers: [...]
```

### kubectl: targeting a specific container in a multicontainer Pod

```bash
kubectl exec deploy/sleep -c sleep -- sh -c 'echo ${HOSTNAME} > /data-rw/hostname.txt'
kubectl exec deploy/sleep -c file-reader -- cat /data-ro/hostname.txt
kubectl logs -l app=timecheck -c logger
kubectl get pod -l app=sleep -o jsonpath='{.items[0].status.containerStatuses[*].name}'
kubectl get pod -l app=sleep -o jsonpath='{.items[0].status.initContainerStatuses[*].name}'
```

---

## Reference Tables

### Init containers vs sidecar containers

| Dimension | Init containers (`initContainers[]`) | Sidecar containers (`containers[]`) |
|---|---|---|
| Execution timing | Before any app container starts | In parallel with app containers |
| Execution order | Sequential (one at a time) | Parallel (all start together) |
| Completion requirement | Must exit 0; failure blocks Pod | Must stay running; crash marks Pod not-Ready |
| Re-run on Pod restart | Yes — always | Container is recreated if it exits |
| Re-run on app image update | No | Yes (app containers replaced) |
| Re-run on init image update | Yes (all init containers re-run) | No (init containers not re-run) |
| Visible in `containerStatuses` | No — use `initContainerStatuses` | Yes |
| Typical use | Config prep, migrations, secret fetch | Logging relay, health API, metrics API, proxy |

### Container communication patterns inside a Pod

| Pattern | Mechanism | Direction | Example |
|---|---|---|---|
| Shared volume | EmptyDir (or any volume) mounted by both | Bidirectional or one-way (readOnly) | Init writes config; app reads it |
| Localhost network | Both listen on different ports; address is `localhost` | Bidirectional | App calls ambassador on `localhost:1080` |
| stdout relay | Sidecar tails a file written by app and echoes to stdout | App → sidecar → Kubernetes log stream | Logger sidecar with `tail -f` |
| Process inspection | `shareProcessNamespace: true` | Any container to any process | Metrics sidecar reading app process stats |

---

## Worked Example

**Goal**: Give a legacy app (`timecheck`) that writes to a log file and reads a single config file all the features of a good Kubernetes citizen — without changing its code or image.

**Pod structure**:
1. Init container (`init-config`) — reads a ConfigMap and an env var, merges them with `jq`, writes `/config-out/appsettings.json` to an EmptyDir.
2. App container (`timecheck`) — mounts the same EmptyDir at `/config`; the merged file shadows the image's built-in config. Writes timestamped log lines to `/logs/timecheck.log` on a second EmptyDir.
3. Adapter sidecar (`logger`) — mounts the logs EmptyDir read-only at `/logs-ro`; runs `tail -f /logs-ro/timecheck.log` so every new log line is echoed to stdout and is visible via `kubectl logs`.
4. Health sidecar (`healthz`) — serves a static `{"status":"OK"}` JSON response on port 8080 via a netcat loop; documented in the Pod spec with `containerPort: 8080`.
5. Metrics sidecar (`metrics`) — serves Prometheus-format text on port 8081.

**Startup sequence**:
- `init-config` runs; reads `/config-in/appsettings.json` (from ConfigMap volume) and `$APP_ENVIRONMENT` env var; writes merged JSON to EmptyDir.
- `init-config` exits 0.
- `timecheck`, `logger`, `healthz`, and `metrics` start in parallel.
- Pod is Ready only when all four report Ready.

**Key observations from the exercise**:
- `kubectl get pod -o jsonpath='{...containerStatuses[*].name}'` shows only the running containers; init containers appear in `initContainerStatuses`.
- `kubectl logs -l app=timecheck -c logger` now exposes the app's log stream even though `kubectl logs` on the raw app container would show nothing (it writes to a file, not stdout).
- The health and metrics endpoints are reachable from other Pods in the cluster via a ClusterIP Service that publishes both ports.
- The app container was never modified. The same `kiamol/ch07-timecheck` image is used in every variant.
- A broken init container (e.g., wrong jq expression) causes the new Pod to stay in init state indefinitely; the Deployment never scales down the old ReplicaSet, so traffic continues going to the previous version — a safe, if confusing, failure mode.

---

## Key Takeaways

1. All containers in a Pod share the same IP address and communicate over `localhost`; they share the filesystem only through explicitly mounted volumes.
2. Init containers are guaranteed to complete before any app container starts — use them for config preparation, migrations, or any setup that must finish first.
3. Sidecar containers extend the app's behaviour at runtime without modifying the app image — adapter, ambassador, health, and metrics patterns all follow this model.
4. The Pod is Ready only when every container in `spec.containers[]` is Ready; adding containers multiplies failure modes and increases deployment/termination time.
5. Environment variables are per-container; use volumes (typically EmptyDir) to pass data between containers at runtime.
6. Init container logic must be idempotent — it re-runs on every Pod replacement.
7. `shareProcessNamespace: true` is an escape hatch for sidecars that need cross-container process visibility; use with care.

---

## Connects To

- **Chapter 2** — First introduction to Pod spec and the fact that `containers` is an array; this chapter makes that real.
- **Chapter 3** — EmptyDir volumes (the workhorse of inter-container data sharing) introduced there.
- **Chapter 4** — ConfigMaps and Secrets as volume mounts; init containers can read them and merge values the app container cannot directly consume.
- **Chapter 5** — PersistentVolumeClaims can be mounted by multiple containers in a Pod, not just EmptyDirs.
- **Chapter 12** — Self-healing and probes; sidecar health endpoints (`healthz` on port 8080) are the precursor to proper liveness/readiness probes covered there.
- **Service mesh (Linkerd, Istio)** — Mentioned as a large-scale production manifestation of the ambassador/proxy sidecar pattern.
