# Chapter 10: Packaging and Managing Apps with Helm

## Core Idea

Helm is the package manager for Kubernetes. It solves two gaps that plain Kubernetes leaves open: there is no native concept of an "application" grouping related resources, and there is no standard distribution mechanism for sharing app bundles. Helm introduces a packaging format (charts) that wraps standard Kubernetes YAML in versioned, parameterized archives, a repository model for discovery and distribution, and a release lifecycle (install / upgrade / rollback / uninstall) that tracks history with revision granularity. Helm is client-side only (since Helm 3) and uses the same kubeconfig as kubectl.

---

## Frameworks Introduced

- **Chart / Release / Values triad**
  - **What**: A chart is a versioned package of templated Kubernetes manifests plus metadata. A release is one installed instance of a chart. Values are the parameters users can override at install or upgrade time.
  - **When**: Every time you install an app from Helm, these three concepts interact — the chart provides the template, values supply the inputs, and the release records the resulting deployment state in the cluster.
  - **How**: `helm install <release-name> <chart-ref> --set key=val` or `helm install -f values-file.yaml <release-name> <chart-ref>`.
  - **Why / failure**: Omitting a value during upgrade causes Helm to revert that setting to the chart default, not to whatever was set in the previous release — this is the most common source of botched upgrades.

- **Atomic upgrades with automatic rollback**
  - **What**: The `--atomic` flag makes `helm upgrade` an all-or-nothing operation: if any resource update fails, Helm rolls back every resource to the last successful revision automatically.
  - **When**: Use on production upgrades where partial failures are unacceptable.
  - **How**: `helm upgrade --atomic -f values.yaml <release-name> <chart-ref> --version x.y.z`
  - **Why / failure**: Without `--atomic`, a partial failure leaves resources in a mixed-revision state that must be diagnosed and manually corrected.

- **Conditional dependencies (subcharts)**
  - **What**: Parent charts declare optional child charts (subcharts) in `Chart.yaml` under `dependencies:`, each with a `condition:` key that maps to a boolean value. When the condition evaluates to false, the subchart is skipped entirely.
  - **When**: Use when an app component (database, proxy, sidecar) is needed in some environments but not others.
  - **How**: Set the condition flag at install time — e.g. `--set proxy.enabled=true` — or in a values file; build dependencies first with `helm dependency build <chart-dir>`.
  - **Why / failure**: Subcharts must remain standalone (independently installable). Tightly coupled subcharts that only work when embedded break the modularity model.

---

## Key Concepts

1. **Chart**: A folder (or `.tgz` archive) containing `Chart.yaml`, `values.yaml`, and a `templates/` directory. The folder name must match the chart name.
2. **Chart.yaml**: Metadata file — sets `name`, `version` (semver, immutable per release), `apiVersion`, and optionally `appVersion` and `dependencies`.
3. **values.yaml**: Default parameter values for the chart. Users override these at install/upgrade time via `--set` flags or `-f` files.
4. **Templates**: Kubernetes manifests with Go-template syntax (`{{ }}`). Helm processes templates at install time, substituting values before sending YAML to the API server.
5. **Release**: A named, versioned instance of a chart installed in a cluster. Multiple releases of the same chart can coexist (different names = different isolated deployments).
6. **Repository**: An index-file server listing chart versions. Helm caches the index locally. Any HTTP server can host a repository; ChartMuseum is a popular dedicated option.
7. **`helm upgrade --reuse-values`**: Carry forward custom values from the currently deployed release. Risky when upgrading to a chart version that adds new parameters — new params fall back to chart defaults, not prior release values.
8. **`helm get values <release> -o yaml`**: Export the current release's custom values to a file for safe reuse in upgrades.
9. **`helm history <release>`**: Shows all revisions: chart version, app version, action taken, status, and timestamps. Far richer than `kubectl rollout history`.
10. **`helm rollback <release> <revision>`**: Roll back to any prior numbered revision. The rollback itself is recorded as a new revision.
11. **Dry-run**: `helm install <name> <chart> --dry-run` prints the rendered YAML without deploying — useful for template debugging and pre-deploy review.
12. **`helm lint <chart-dir>`**: Validates chart structure and template syntax locally before packaging.

---

## Mental Models

**Helm vs kubectl are complementary, not interchangeable.** Helm manages the lifecycle of a release (install, upgrade, rollback, uninstall) and tracks application-level history. kubectl manages individual Kubernetes resources. Once a release is installed, kubectl is the right tool for real-time inspection (`kubectl get`, `kubectl describe`, `kubectl logs`). Helm is the right tool when you want to change release-level configuration or roll back. Do not mix `kubectl apply` on template files (they contain unprocessed `{{ }}` syntax that kubectl will reject).

**Values flow: defaults overridden by user input.** At install time, Helm merges: (1) chart defaults from `values.yaml`, (2) user `-f` file overrides, (3) individual `--set` overrides — in that precedence order. At upgrade time, the base is the chart defaults again (not the previous release's values) unless `--reuse-values` or an explicit values export is used. This means upgrade commands must re-specify every non-default setting or they silently revert.

**Charts are immutable artifacts; treat versions as immutable.** Once a chart version is published to a repository, it should never be changed in place. Modifications must bump the version number. This parallels container image tagging discipline — always pin chart versions in production, never rely on "latest."

**Subcharts to parent charts via prefixed values.** A subchart's value named `upstreamToProxy` is set from a parent chart's values file as `proxy.upstreamToProxy`. This namespace prefix is the dependency name declared in `Chart.yaml`. Subchart values can even reference parent release metadata via Go-template expressions like `{{ .Release.Name }}`.

---

## Anti-patterns

- **Upgrading without re-specifying all custom values.** If a `--set servicePort=8010` was used on install but omitted on upgrade, the port reverts to the chart default. Always save values to a file (`helm get values -o yaml`) and use `-f` on upgrade.
- **Pinning to "latest" chart version.** Omitting `--version` installs the latest chart, a moving target. Pin explicit versions in scripts and CI to guarantee reproducibility.
- **Mixing kubectl apply with Helm templates.** Templates with `{{ }}` syntax are not valid YAML; applying them with kubectl fails. Teams must commit to one workflow per environment.
- **Mutating a published chart version.** Publishing changes under an existing version number breaks dependency locks in parent charts that bundled that version.
- **Using `--reuse-values` when upgrading to a chart with new parameters.** New parameters not present in the previous release default to chart defaults, not blank — this can silently misconfigure the new resources (e.g. a new `serviceType` field defaulting to `ClusterIP` clashes with an existing `LoadBalancer` Service).
- **Tightly coupling subcharts to their parent.** If a subchart cannot be installed standalone, it is not reusable and harder to test. Design subcharts to be generic with templated connection points.

---

## Code Examples

**Minimal chart directory structure:**
```
web-ping/
  Chart.yaml
  values.yaml
  templates/
    deployment.yaml
    service.yaml
```

**Chart.yaml — with optional dependencies:**
```yaml
apiVersion: v2
name: pi
version: 0.1.0
dependencies:
  - name: proxy
    version: 0.1.0
    repository: file://../proxy
    condition: proxy.enabled
  - name: vweb
    version: 2.0.0
    repository: https://kiamol.net
    condition: vweb.enabled
```

**values.yaml — parent chart defaults including subchart namespace:**
```yaml
replicaCount: 2
serviceType: LoadBalancer
proxy:
  enabled: false
  upstreamToProxy: "{{ .Release.Name }}-web"
  servicePort: 8030
  replicaCount: 2
```

**Templated Deployment manifest (templates/deployment.yaml):**
```yaml
metadata:
  name: {{ .Release.Name }}-web
  labels:
    app.kubernetes.io/instance: {{ .Release.Name }}
    kiamolChapter: {{ .Values.kiamolChapter }}
spec:
  replicas: {{ .Values.replicaCount }}
  template:
    spec:
      containers:
        - name: app
          image: kiamol/ch10-web-ping
          env:
            - name: TARGET
              value: {{ .Values.targetUrl }}
            - name: INTERVAL
              value: {{ .Values.pingIntervalMilliseconds | quote }}
```

**Repository setup:**
```bash
helm repo add kiamol https://kiamol.net
helm repo update
helm search repo vweb --versions
```

**Inspect default values before installing:**
```bash
helm show values kiamol/vweb --version 1.0.0
```

**Install a release with custom values:**
```bash
helm install --set servicePort=8010 --set replicaCount=1 ch10-vweb kiamol/vweb --version 1.0.0
```

**Install from local chart folder:**
```bash
helm lint web-ping
helm install wp1 web-ping/
```

**Install with a values file:**
```bash
helm install -f web-ping-values.yaml wp3 local/web-ping
```

**Install a second release of the same chart (different name, different target):**
```bash
helm install --set targetUrl=kiamol.net wp2 web-ping/
```

**Upgrade a release:**
```bash
helm upgrade --set servicePort=8010 --set replicaCount=3 ch10-vweb kiamol/vweb --version 1.0.0
```

**Safe upgrade — export current values, then upgrade atomically:**
```bash
helm get values ch10-vweb -o yaml > vweb-values.yaml
helm upgrade -f vweb-values.yaml --atomic ch10-vweb kiamol/vweb --version 2.0.0
```

**Rollback to a specific revision:**
```bash
helm history ch10-vweb
helm get values ch10-vweb --revision 2
helm rollback ch10-vweb 2
helm history ch10-vweb --max 2 -o yaml
```

**Dry-run to preview rendered YAML:**
```bash
helm install pi1 ./pi --dry-run
```

**Build subchart dependencies:**
```bash
helm dependency build pi
ls ./pi/charts
```

**Package and publish a chart:**
```bash
helm package web-ping
curl --data-binary "@web-ping-0.1.0.tgz" http://<chartmuseum-url>/api/charts
helm repo update
helm search repo web-ping
```

**List and uninstall all releases:**
```bash
helm ls
helm ls -q
helm uninstall $(helm ls -q)
```

---

## Reference Tables

### Helm CLI Commands

| Command | Purpose |
|---|---|
| `helm repo add <name> <url>` | Register a chart repository |
| `helm repo update` | Sync local index cache from all repositories |
| `helm search repo <term> --versions` | Search cached repository index |
| `helm show values <chart> --version x.y.z` | Display chart default values |
| `helm install <release> <chart>` | Install a new release |
| `helm upgrade <release> <chart>` | Update an existing release |
| `helm upgrade --atomic` | Upgrade with automatic rollback on failure |
| `helm upgrade --reuse-values` | Carry forward prior custom values (use carefully) |
| `helm rollback <release> <revision>` | Roll back to a numbered revision |
| `helm history <release>` | Show full revision history of a release |
| `helm get values <release> -o yaml` | Export current custom values |
| `helm get values <release> --revision N` | Export custom values from a specific revision |
| `helm ls` | List all installed releases |
| `helm uninstall <release>` | Remove a release and its resources |
| `helm lint <chart-dir>` | Validate chart structure and templates |
| `helm package <chart-dir>` | Create a `.tgz` archive for distribution |
| `helm dependency build <chart-dir>` | Download and bundle subchart dependencies |
| `helm install --dry-run` | Render templates without deploying |

### Chart.yaml vs values.yaml Roles

| File | Role | Key Fields |
|---|---|---|
| `Chart.yaml` | Chart identity and dependency declarations | `name`, `version`, `apiVersion`, `appVersion`, `dependencies` |
| `values.yaml` | Default parameter values for templates | Any key-value pairs; referenced in templates as `{{ .Values.<key> }}` |

### Template Objects

| Object | Source | Example use |
|---|---|---|
| `{{ .Release.Name }}` | Set by Helm at install | Resource names scoped to the release |
| `{{ .Values.<key> }}` | Merged from values.yaml + user overrides | `{{ .Values.replicaCount }}` |
| `{{ .Chart.<field> }}` | From Chart.yaml | `{{ .Chart.Version }}` |
| `{{ .Values.<key> \| quote }}` | Pipe to function | Wrap numeric env var values in quotes |

---

## Worked Example

**Scenario**: Deploy the `vweb` app, scale it up, perform a failed upgrade, inspect history, and roll back to a known-good revision.

**Step 1 — Add repository and install v1:**
```bash
helm repo add kiamol https://kiamol.net
helm repo update
helm show values kiamol/vweb --version 1.0.0
helm install --set servicePort=8010 --set replicaCount=1 ch10-vweb kiamol/vweb --version 1.0.0
helm ls
```
This creates revision 1 of release `ch10-vweb` with one replica behind port 8010.

**Step 2 — Scale up (upgrade, re-specify all values):**
```bash
helm upgrade --set servicePort=8010 --set replicaCount=3 ch10-vweb kiamol/vweb --version 1.0.0
```
Note: `servicePort` must be repeated — Helm does not carry forward prior custom values unless told to. This creates revision 2.

**Step 3 — Test new chart version in isolation before upgrading production:**
```bash
helm install --set servicePort=8020 --set replicaCount=1 --set serviceType=ClusterIP ch10-vweb-v2 kiamol/vweb --version 2.0.0
kubectl port-forward svc/ch10-vweb-v2 8020:8020
# Smoke-test, then:
helm uninstall ch10-vweb-v2
```

**Step 4 — Attempted upgrade using --reuse-values (fails):**
```bash
helm upgrade --reuse-values ch10-vweb kiamol/vweb --version 2.0.0
```
v2.0.0 introduced a new `serviceType` parameter. `--reuse-values` does not pull in chart defaults for new parameters — `serviceType` resolves to blank, Kubernetes rejects the Service update. Helm records this as a failed revision 3 and (if `--atomic` was set) auto-rolls back to revision 2.

**Step 5 — Inspect history:**
```bash
helm history ch10-vweb
```
Output shows: revision 1 (install), revision 2 (upgrade, deployed), revision 3 (upgrade, failed/superseded if --atomic), revision 4 (rollback).

**Step 6 — Safe upgrade — export and reuse values:**
```bash
helm get values ch10-vweb -o yaml > vweb-values.yaml
helm upgrade -f vweb-values.yaml --atomic ch10-vweb kiamol/vweb --version 2.0.0
kubectl get svc,rs -l app.kubernetes.io/instance=ch10-vweb
```
The values file includes `servicePort: 8010` and `replicaCount: 3`. The chart default fills in the new `serviceType: LoadBalancer`. Upgrade succeeds (new revision).

**Step 7 — Roll back to revision 2:**
```bash
helm get values ch10-vweb --revision 2    # confirm what was set
helm rollback ch10-vweb 2
helm history ch10-vweb --max 2 -o yaml   # rollback is a new revision
```

**Cleanup:**
```bash
helm uninstall $(helm ls -q)
```

---

## Key Takeaways

1. **Charts, releases, and values are the three pillars.** A chart is the template artifact, a release is a named deployment instance, and values are the runtime parameters. Mastering how they interact (especially at upgrade time) is the critical skill.
2. **Always re-specify or export custom values on upgrade.** Helm defaults back to chart defaults for any value not explicitly provided; `helm get values -o yaml` + `-f` is the safe pattern.
3. **Pin chart versions.** Never rely on "latest" in automation or production; treat chart versions as immutable artifacts.
4. **Multiple releases of one chart enable parallel testing.** Install the new version as a separate ClusterIP release alongside the running production release, smoke-test it, then upgrade the production release. Helm's parameterized names make this natural.
5. **`--atomic` makes upgrades safe by default.** It rolls back every affected resource if any single resource update fails, leaving the cluster in the last good state rather than a mixed-revision limbo.
6. **Subcharts model optional dependencies.** Use `condition:` in `Chart.yaml` to make components opt-in; keep subcharts standalone and generically useful.
7. **Helm and kubectl are complementary.** Helm owns the application lifecycle; kubectl owns resource-level observation and debugging. Do not use `kubectl apply` directly on chart template files.

---

## Connects To

- **Chapter 9 (Rollouts and Rollbacks)**: Helm's upgrade/rollback lifecycle builds on Kubernetes Deployment rollout mechanics. `--atomic` and `helm rollback` complement (and improve on) `kubectl rollout undo` by tracking application-level history across all resource types, not just Deployments.
- **Chapter 8 (StatefulSets and Jobs)**: Complex apps (database + app + proxy) are the prime use case for conditional subchart dependencies, letting the same chart deploy differently across dev/test/prod.
- **Chapter 4 (ConfigMaps and Secrets)**: Chart templates generate ConfigMaps; advanced Helm usage hashes ConfigMap content as a Deployment label to trigger Pod rollouts automatically when configuration changes.
- **Chapter 6 (Scaling and Controllers)**: `replicaCount` is a canonical chart parameter, making replica management a first-class concern of chart values rather than post-deploy patching.
- **Chapter 5 (Volumes and Storage)**: The Pi app used throughout this chapter has been the scaling demo since Chapter 5 — here it becomes the vehicle for demonstrating subchart dependencies.
