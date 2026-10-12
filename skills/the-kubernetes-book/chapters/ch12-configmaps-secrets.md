# Chapter 12: ConfigMaps and Secrets

## Core Idea
Most business apps have two parts: the application binary and its configuration. Packaging both into one image is an anti-pattern. Modern apps **decouple config from the image**, storing config as separate Kubernetes objects (ConfigMaps for non-sensitive data, Secrets for sensitive data) and injecting it at run time. Decoupling buys: **reuse**, **simpler dev/testing**, and **simpler, less-disruptive changes**.

Example: one hardened NGINX image used across dev/test/prod, with three separate configs applied at run time — vs. building/storing/deploying three separate images and rebuilding all three for a single typo fix.

## Frameworks Introduced (3 ways to inject config into a container)
Stored config is injected at run time by any of:
1. **Environment variables** — map CM keys to env vars in the Pod template.
2. **Arguments to the container's startup command** — reference env vars (themselves from a CM) in the startup command.
3. **Files in a volume** — mount CM entries as files inside the container.

All three work with existing apps unchanged. **Volume is the most flexible; startup command is the least.** Only the volume method propagates live updates to running containers.

## Key Concepts (5-10)
- **ConfigMap (CM)** — core API group, `v1` (stable, long-standing). Stores config outside Pods, injected at run time. Transparent to apps (no app changes needed).
- **Map of key-value pairs** — keys: alphanumerics, dashes, dots, underscores; values: anything including full multi-line config files; separated by colon `key:value`. Limited to **1MiB (1,048,576 bytes)**.
- **No state** — CMs/Secrets have a `data` block, not `spec`/`status`, because they have no concept of desired vs. actual state.
- **Pipe `|` in YAML** — tells Kubernetes to treat everything after it as a single literal value (used for embedding whole config files).
- **`--from-literal` / `--from-file`** — two imperative data sources; with `--from-file` the key name = the input filename, value = the file contents.
- **Env vars are static** — CM updates do NOT appear in containers that consumed via env vars or startup command. Main reason to avoid them.
- **Volume updates are live** — CM edits propagate into mounted files in running containers (may take ~1 minute).
- **Secret** — almost identical to a CM but for sensitive data (passwords, certificates, OAuth tokens).
- **base64 is encoding, NOT encryption** — Secrets are only base64-encoded in the cluster store; anyone can decode without a key.
- **Kubernetes-native apps** — can read CM data directly via the API server (no env/volume needed), at the cost of Kubernetes lock-in.

## Mental Models
- **CM/Secret = config stored separately, bolted on at run time.** One image, many configs.
- **Secrets workflow:** create (stored *un-encrypted* in cluster store) → schedule Pod → transferred *un-encrypted* over network to node → kubelet starts Pod → container runtime mounts via in-memory **tmpfs** and decodes base64 → app consumes as plain text → Pod delete removes node copy (cluster-store copy stays). tmpfs means Secrets are never written to node disk.
- **Always plain text in the end:** even with encryption-at-rest and a service mesh encrypting in-flight, Kubernetes always surfaces the Secret as plain text in the container so the app needn't decode/decrypt.

## Anti-patterns
- **Baking config into the image** — forces N images/repos/deploys per environment; every config typo means rebuild+retest+restore+redeploy all environments. Harder to isolate issues.
- **Treating Secrets as encrypted** — they are NOT. base64 is not security. Not encrypted at rest, in flight, or in the container.
- **Storing sensitive data in a ConfigMap** — Kubernetes makes no effort to protect CM contents.
- **Using env vars / startup commands when you need live config updates** — those are static; use a volume.

## Code Examples

ConfigMap (declarative, simple entries — `multimap.yml`):
```yaml
kind: ConfigMap
apiVersion: v1
metadata:
  name: multimap
data:
  given: Nigel
  family: Poulton
```

ConfigMap with an embedded config file (`singlemap.yml`, single entry via `|`):
```yaml
kind: ConfigMap
apiVersion: v1
metadata:
  name: test-config
data:
  test.conf: |
    env = plex-test
    endpoint = 0.0.0.0:31001
    char = utf8
    vault = PLEX/test
    log-size = 512M
```

Inject via **environment variables** (`envpod.yml` maps CM `given`/`family` → `FIRSTNAME`/`LASTNAME`):
```yaml
# in containers[].env:
#   FIRSTNAME -> configMapKeyRef multimap key "given"
#   LASTNAME  -> configMapKeyRef multimap key "family"
$ kubectl exec envpod -- env | grep NAME
HOSTNAME=envpod
FIRSTNAME=Nigel
LASTNAME=Poulton
```

Inject via **volume** (`cmpod.yml`, Pod `cmvol`):
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: cmvol
spec:
  volumes:
  - name: volmap            # create a volume called "volmap"
    configMap:              # based on a ConfigMap
      name: multimap        # called "multimap"
  containers:
  - name: ctr
    image: nginx
    volumeMounts:
    - name: volmap          # mount the "volmap" volume
      mountPath: /etc/name  # into the container at "/etc/name"
```

Secret (declarative, `tkb-secret.yml`):
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: tkb-secret
  labels:
    chapter: configmaps
type: Opaque
data:                       # use "stringData" for plain-text input
  username: bmlnZWxwb3VsdG9u
  password: UGFzc3dvcmQxMjM=
```

Inject Secret via **volume** (`secretpod.yml`, mounted read-only):
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secret-pod
spec:
  volumes:
  - name: secret-vol        # volume name
    secret:                 # volume type
      secretName: tkb-secret  # populate from this Secret
  containers:
  - name: secret-ctr
    image: nginx
    volumeMounts:
    - name: secret-vol
      mountPath: "/etc/tkb"
```

## Reference Tables

Injection methods:

| Method | Live updates? | Flexibility | Notes |
|--------|---------------|-------------|-------|
| Environment variables | No (static) | Medium | Simplest; map CM key → env var; updates never reach running container |
| Startup command args | No (static) | **Least** | Extension of env vars; references env vars in the command; same static limitation |
| Volume (files) | **Yes** (~1 min) | **Most** | Can hold whole config files; CM edits surface as updated files; Secret volumes mounted **read-only** |

Imperative create sources:

| Flag | Source | Behavior |
|------|--------|----------|
| `--from-literal k=v` | command-line literal | one entry per flag |
| `--from-file f.txt` | a file | key = filename, value = file contents |

ConfigMap vs. Secret:

| | ConfigMap | Secret |
|--|-----------|--------|
| Purpose | non-sensitive config (env vars, config files, hostnames, ports, account names) | sensitive data (passwords, certs, OAuth tokens) |
| Storage in cluster store | plain | base64-encoded (NOT encrypted) |
| In container | plain text files/env | plain text (tmpfs, base64-decoded) |
| API | core, `v1`, `data` block | core, `v1`, `data`/`stringData` block |

## Worked Example
Create a ConfigMap and inject it two ways:
```bash
# 1. Imperative create from literals
$ kubectl create configmap testmap1 \
    --from-literal shortname=AOS \
    --from-literal longname="Agents of Shield"
$ kubectl describe cm testmap1          # shows key:value map
$ kubectl get cm testmap1 -o yaml       # full object, "data" block, no spec/status

# 2. Declarative
$ kubectl apply -f multimap.yml         # given=Nigel, family=Poulton

# Inject as ENV VARS, verify
$ kubectl apply -f envpod.yml
$ kubectl exec envpod -- env | grep NAME
FIRSTNAME=Nigel
LASTNAME=Poulton

# Inject as VOLUME, verify files appear
$ kubectl apply -f cmpod.yml
$ kubectl exec cmvol -- ls /etc/name
family
given

# Prove live updates (volume only)
$ kubectl edit cm multimap              # change values (e.g. City/Country)
$ kubectl exec cmvol -- ls /etc/name    # new keys appear (~1 min)
City
Country
$ kubectl exec cmvol -- cat /etc/name/Country
UK
```
Secret check (proving base64 ≠ encryption):
```bash
$ kubectl create secret generic creds \
    --from-literal user=nigelpoulton --from-literal pwd=Password123
$ kubectl get secret creds -o yaml      # pwd: UGFzc3dvcmQxMjM= (base64)
$ echo UGFzc3dvcmQxMjM= | base64 -d     # decodes with no key
Password123
$ kubectl apply -f secretpod.yml
$ kubectl exec secret-pod -- cat /etc/tkb/password
Password123                              # surfaced as plain text
```
Clean up: `kubectl get`/`kubectl delete` the Pods, ConfigMaps, and Secrets.

## Key Takeaways (3-7)
1. **Decouple config from the image** — one image, many run-time configs; enables reuse and independent, non-disruptive config changes.
2. CMs and Secrets are first-class `v1` core API objects; create imperatively or declaratively; inspect with `kubectl`. They use a `data` block (no state).
3. Three injection methods: **env vars, startup command args, volumes**. Volumes are preferred — most flexible and the only method with **live updates** in running containers.
4. **Secrets are NOT secure** — base64 is encoding, not encryption; not encrypted at rest, in flight, or in the container. A complete solution needs EncryptionConfiguration (at-rest), a service mesh (in-flight), and/or 3rd-party tools like HashiCorp Vault.
5. Secret volumes are mounted **read-only** via in-memory **tmpfs**, decoded to plain text, never persisted to node disk.

## Connects To
- **Pods (Ch 5)** — config injected via the Pod template (`env`, `command`, `volumes`/`volumeMounts`).
- **Storage / volumes** — ConfigMap and Secret volumes are special volume types.
- **Security** — EncryptionConfiguration (encryption-at-rest), service meshes (in-flight encryption), RBAC for restricting Secret access, Vault for full secrets management.
- **Deployments / multi-environment workflows** — the dev/test/prod single-image-many-configs pattern.
