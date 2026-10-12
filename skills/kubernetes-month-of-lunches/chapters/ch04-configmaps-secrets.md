# Chapter 4: Configuring Applications with ConfigMaps and Secrets

## Core Idea

Container images should be identical across all environments (dev, test, prod). Environment-specific behavior is injected at runtime via Kubernetes configuration objects — ConfigMaps for general settings, Secrets for sensitive data. Both surface into Pods either as environment variables or as files in the container filesystem, decoupling the application binary from its runtime configuration.

---

## Frameworks Introduced

- **Configuration Hierarchy**: A layered override model where (1) default settings are baked into the container image as a JSON/YAML file, (2) environment-specific settings are injected via a ConfigMap mounted as a file that the app merges with the defaults, and (3) individual overrides can be applied as inline `env` values in the Pod spec. **When**: Any app with multi-environment deployments. **How**: App reads `/app/appsettings.json` (image), then `/app/config/config.json` (ConfigMap mount), then environment variables. **Failure**: Inline `env` values that duplicate ConfigMap keys take precedence — this is intentional but can surprise you when debugging.

- **Versioned Config Objects**: Instead of mutating an existing ConfigMap, deploy a new ConfigMap with a version suffix (e.g., `todo-web-config-v2`) and update the Deployment to reference it. **When**: Auditability and rollback are priorities, or when live updates are not needed. **How**: Name ConfigMaps with a version scheme; update `configMap.name` in the Pod spec volumes section to point to the new object, triggering a Pod replacement. **Why**: Gives a full audit trail and easy revert; tradeoff is no live updates without a Pod restart.

---

## Key Concepts

1. **ConfigMap**: A Kubernetes resource that stores arbitrary key-value pairs or file contents. Lives independently of Pods; can be shared across many Pods or unused. No encryption. Intended for non-sensitive configuration.

2. **Secret**: Structurally similar to a ConfigMap but managed with additional protections — sent only to nodes that need them, stored in memory (not disk), and supports encryption in transit and at rest. Data is Base64-encoded at rest in the API, but decoded to plain text inside the container.

3. **Inline env variables** (`env` in Pod spec): Statically set per Pod; cannot be changed without replacing the Pod. Highest precedence when duplicate keys exist with `envFrom`.

4. **`envFrom` with ConfigMap**: Loads all key-value pairs from a ConfigMap as environment variables in one block. Keys in `env` override duplicate keys from `envFrom`.

5. **Volume mount of ConfigMap**: The ConfigMap is treated as a directory; each data key becomes a file. Kubernetes creates the directory and populates it. Files are read-only by default.

6. **Selective item mounting**: Use `volumes[].configMap.items` to expose only specific keys from a ConfigMap rather than all keys. Prevents unwanted files from appearing in the mount directory.

7. **ConfigMap directory clobber risk**: If a volume is mounted at a path that already exists in the container image (e.g., `/app`), the mount replaces the entire directory, wiping app binaries. Always mount to a subdirectory (e.g., `/app/config`).

8. **Live config updates**: When a ConfigMap is updated, Kubernetes eventually delivers new file contents to running Pods (takes ~2 minutes due to caching). Whether the app reacts depends on the application — some reload on file-change events, others require a restart.

9. **Base64 in Secrets**: `kubectl describe secret` hides values; `kubectl get secret -o jsonpath` shows Base64-encoded values. Inside a Pod container, Secrets are always decoded to plain text.

10. **`stringData` vs `data` in Secret YAML**: `stringData` accepts plain text (encoded automatically on creation); `data` requires values to be pre-encoded in Base64. `stringData` is more readable in YAML specs but exposes secrets in source control.

---

## Mental Models

1. **ConfigMap as a virtual filesystem directory**: Think of a ConfigMap not as a flat key-value store but as a directory. Each key is a filename; the value is the file content. When mounted, Kubernetes materializes this directory inside the container at the specified `mountPath`. The container image provides other directories; the ConfigMap provides this one. They compose into a unified view, but the mounted directory completely replaces any same-named directory from the image — it does not merge.

2. **Env vars are sealed at Pod start; files can be live-updated**: Environment variables are frozen when the container starts. No update to a ConfigMap changes them — the Pod must be replaced. Volume-mounted files, however, can be updated in place by Kubernetes when the backing ConfigMap changes. The gap (up to ~2 minutes) is a Kubernetes caching artifact. Design your app's config model around this if live updates matter.

3. **Secrets offer obscurity, not security**: Base64 is encoding, not encryption. Anyone with `kubectl get secret` access can read all values. The real security controls are RBAC (who can read Secrets) and encryption at rest (cluster-level config). Loading Secrets as files rather than env vars adds a layer because file permissions (e.g., 0400) limit which processes inside the container can read the value.

4. **Pod replacement as the deployment primitive**: Configuration changes — even a single env var value — that require touching the Pod spec trigger a full Pod replacement via the Deployment controller. This is intentional; Kubernetes applies the same rolling update logic as a code change. Design apps to start and stop cleanly to make this frictionless.

---

## Anti-patterns

- **Mounting a ConfigMap at an existing image directory** (`mountPath: "/app"` instead of `"/app/config"`): Overwrites all binaries in that directory; the new Pod crashes immediately. The old Pod stays running (Kubernetes keeps it until the replacement is healthy), so the app appears to keep working — but the new spec is silently not applied.

- **Storing sensitive data in ConfigMaps**: ConfigMaps have no security semantics. Use Secrets for passwords, tokens, API keys, and certificates.

- **Loading Secrets as environment variables when files are an option**: Env vars are readable by every process in the container and may appear in crash dumps or platform logs. Prefer mounting Secrets as files and controlling access with file permissions (e.g., `defaultMode: 0400`).

- **Committing plain-text Secrets in YAML to source control**: Using `stringData` in a YAML file is convenient but exposes secrets. Use placeholder values in YAML and inject real values from a secure store (Azure KeyVault, GitHub Secrets, Vault) during the CI/CD pipeline before `kubectl apply`.

- **Assuming `kubectl apply` failure means the app is broken**: A bad Deployment update that crashes the new Pod still reports a successful `apply`. The old Pod continues serving traffic. Check `kubectl get pods` to see if a new Pod is in `CrashLoopBackOff` while the old one is still `Running`.

---

## Code Examples

```yaml
# Inline env variable in Pod spec
env:
  - name: KIAMOL_CHAPTER
    value: "04"
```

```yaml
# Env variable sourced from a ConfigMap key
env:
  - name: KIAMOL_SECTION
    valueFrom:
      configMapKeyRef:
        name: sleep-config-literal   # ConfigMap name
        key: kiamol.section          # Key within the ConfigMap
```

```yaml
# Load all ConfigMap keys as env vars (envFrom)
envFrom:
  - configMapRef:
      name: sleep-config-env-file
```

```yaml
# Env variable sourced from a Secret key
env:
  - name: KIAMOL_SECRET
    valueFrom:
      secretKeyRef:
        name: sleep-secret-literal
        key: secret
```

```yaml
# ConfigMap YAML with a JSON file as a data value
apiVersion: v1
kind: ConfigMap
metadata:
  name: todo-web-config-dev
data:
  config.json: |-
    {
      "ConfigController": {
        "Enabled": true
      }
    }
```

```yaml
# Secret YAML using stringData (plain text, auto-encoded)
apiVersion: v1
kind: Secret
metadata:
  name: todo-db-secret-test
type: Opaque
stringData:
  POSTGRES_PASSWORD: "kiamol-2*2*"
```

```yaml
# Volume mount: ConfigMap surfaced as a directory
spec:
  containers:
    - name: web
      image: kiamol/ch04-todo-list
      volumeMounts:
        - name: config
          mountPath: "/app/config"
          readOnly: true
  volumes:
    - name: config
      configMap:
        name: todo-web-config-dev
```

```yaml
# Selective item mount: only expose one key from ConfigMap
volumes:
  - name: config
    configMap:
      name: todo-web-config-dev
      items:
        - key: config.json
          path: config.json
```

```yaml
# Secret volume mount with restricted file permissions
volumeMounts:
  - name: db-password
    mountPath: "/secrets"
    readOnly: true
volumes:
  - name: db-password
    secret:
      secretName: todo-db-secret-test
      defaultMode: 0400
```

```bash
# Create ConfigMap from a literal value
kubectl create configmap sleep-config-literal --from-literal=kiamol.section='4.1'

# Create ConfigMap from an env file
kubectl create configmap sleep-config-env-file --from-env-file=sleep/ch04.env

# Create Secret from a literal value
kubectl create secret generic sleep-secret-literal --from-literal=secret=shh...

# Apply a ConfigMap defined in YAML
kubectl apply -f todo-list/configMaps/todo-web-config-dev.yaml

# Inspect a ConfigMap (shows values)
kubectl describe cm sleep-config-literal

# Inspect a Secret (hides values, shows keys only)
kubectl describe secret sleep-secret-literal

# Read a Secret value (Base64 encoded)
kubectl get secret sleep-secret-literal -o jsonpath='{.data.secret}'

# Decode a Secret value
kubectl get secret sleep-secret-literal -o jsonpath='{.data.secret}' | base64 -d

# Verify env vars inside a running Pod
kubectl exec deploy/sleep -- printenv HOSTNAME KIAMOL_CHAPTER

# Check files in a volume-mounted directory
kubectl exec deploy/todo-web -- sh -c 'ls -l /app/config/*.json'

# Delete all resources across multiple directories
kubectl delete -f sleep/
kubectl delete -f todo-list/
kubectl delete -f todo-list/configMaps/
kubectl delete -f todo-list/secrets/
```

---

## Reference Tables

### Environment Variable vs Config File as Volume Mount

| Dimension | Env Variable | Volume Mount (file) |
|---|---|---|
| Data format | Key-value pairs only | Any text or binary format |
| Live update without Pod restart | No | Yes (app must watch filesystem) |
| Precedence | `env` > `envFrom` > image | App-defined merge logic |
| Security (for Secrets) | Readable by all processes; may appear in logs | File permissions (e.g., 0400) limit access |
| Suitable for | Simple scalar settings | Structured config files (JSON, YAML, TOML, INI) |

### ConfigMap vs Secret

| Dimension | ConfigMap | Secret |
|---|---|---|
| Intended for | Non-sensitive configuration | Passwords, tokens, certs, keys |
| Storage at rest | Plain text in etcd | Base64-encoded; encryption at rest optional (cluster config) |
| `kubectl describe` output | Shows values | Shows key names only, hides values |
| Node delivery | All nodes that schedule the Pod | Only nodes that need them |
| In-memory storage on node | No | Yes |
| YAML field for plain text | `data` | `stringData` (auto-encodes) or `data` (pre-encoded Base64) |
| Resource type keyword | `ConfigMap` | `Secret` with `type: Opaque` |

---

## Worked Example

**Goal**: Deploy a to-do web app that reads its configuration from a ConfigMap mounted as a file, enabling a /config diagnostic page that is disabled by default.

**Step 1 — Create the ConfigMap from YAML.**

```yaml
# todo-web-config-dev.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: todo-web-config-dev
data:
  config.json: |-
    {
      "ConfigController": {
        "Enabled": true
      }
    }
```

```bash
kubectl apply -f todo-list/configMaps/todo-web-config-dev.yaml
kubectl get cm todo-web-config-dev
```

**Step 2 — Deploy the app with the ConfigMap volume mount.**

The Pod spec references the ConfigMap as a volume and mounts it at `/app/config`. The app is configured to read `/app/config/config.json` and merge it with the default `/app/appsettings.json` baked into the image.

```yaml
# Relevant excerpt from todo-web-dev.yaml
spec:
  containers:
    - name: web
      image: kiamol/ch04-todo-list
      volumeMounts:
        - name: config
          mountPath: "/app/config"
          readOnly: true
  volumes:
    - name: config
      configMap:
        name: todo-web-config-dev
```

```bash
kubectl apply -f todo-list/todo-web-dev.yaml
kubectl wait --for=condition=Ready pod -l app=todo-web
```

**Step 3 — Verify the config file is present and read-only.**

```bash
kubectl exec deploy/todo-web -- sh -c 'ls -l /app/config/*.json'
# Expected: config.json present, read-only (-r--------) 
kubectl exec deploy/todo-web -- sh -c 'echo test >> /app/config/config.json'
# Expected: permission denied — Kubernetes enforces readOnly: true
```

**Step 4 — Browse to /config.**
The page is now visible because the ConfigMap's JSON set `ConfigController.Enabled: true`, overriding the default (disabled).

**Step 5 — Live update the ConfigMap (add logging settings).**

```bash
kubectl apply -f todo-list/configMaps/todo-web-config-dev-with-logging.yaml
# Wait ~2 minutes for Kubernetes to push the update to the Pod
kubectl exec deploy/todo-web -- sh -c 'ls -l /app/config/*.json'
# Now two files: config.json and logging.json
kubectl logs -l app=todo-web
# Log entries now include Debug-level messages from the app
```

The Pod was never restarted; Kubernetes updated the mounted files in place, and the app detected the change and reloaded its configuration.

---

## Key Takeaways

1. ConfigMaps and Secrets are independent Kubernetes resources — they exist before the Pod and can be reused across many Pods. They must exist before any Pod that references them is deployed.

2. Inline `env` values in the Pod spec take precedence over `envFrom` values from ConfigMaps. Use this deliberately for per-environment overrides, not accidentally.

3. Volume mounts surface a ConfigMap as a directory. Each key becomes a file. If the `mountPath` already exists in the image, the mount replaces the directory entirely — it does not merge. Always mount into a dedicated subdirectory.

4. Secrets are not encrypted by default — Base64 is obfuscation. Real security comes from RBAC on the Secret resource and cluster-level encryption at rest. Treat anything in a Secret as potentially readable by anyone with cluster access.

5. Live configuration updates (no Pod restart) require volume-mounted files, not environment variables, and an application that watches for file changes. Kubernetes propagates ConfigMap updates to mounted files within ~2 minutes.

6. When a Deployment update fails (e.g., bad volume mount wipes app binaries), the original Pod keeps running. `kubectl apply` succeeds and the app stays up, but `kubectl get pods` will show the new Pod in `CrashLoopBackOff`. Always verify with `kubectl get pods` after applying changes.

7. For Secrets in source control, use `stringData` with placeholder values and replace them from a secure store (Azure KeyVault, GitHub Secrets, HashiCorp Vault) in the CI/CD pipeline before `kubectl apply`. Never commit real credential values.

---

## Connects To

- **Chapter 3 (Services and Networking)**: Services expose Pods; ConfigMaps configure which backend a Pod connects to (e.g., database hostname), enabling environment-specific service discovery without image changes.
- **Chapter 2 (Pods and Deployments)**: Pod spec is where `env`, `envFrom`, `volumeMounts`, and `volumes` are defined. Configuration changes to these fields trigger a Deployment rollout (Pod replacement).
- **Chapter 9 (Rollouts and Rollbacks)**: Versioned ConfigMap naming strategy (new object per release) integrates with Deployment rollout history, enabling configuration rollbacks alongside code rollbacks.
- **Chapter 11 (Dev Workflows and CI/CD)**: Secret injection patterns (placeholder YAML + pipeline substitution from secure stores) are a core CI/CD concern when automating `kubectl apply`.
- **RBAC (later chapters)**: Access to `Secret` objects should be controlled by RBAC policies — the main security control on top of Base64 encoding.
