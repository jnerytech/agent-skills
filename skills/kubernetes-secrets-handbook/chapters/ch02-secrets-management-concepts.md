# Chapter 2: Walking through Kubernetes Secrets Management Concepts

## Core Idea
Kubernetes has **seven built-in Secret types** that differ only in how the payload is *consumed* (all serialize to base64 in etcd the same way) — and the practical controls over them are `stringData` vs `data`, immutability, RBAC (Role/ClusterRole + bindings), and an audit policy scoped to the `secrets` resource.

## Frameworks Introduced

- **Pick the Secret type by consumer, not by content.** All types store identically; the type declares intent and unlocks declarative consumption.
  - When to use: every time you create a Secret.
  - How: match the consumer to the type — Ingress ⇒ `kubernetes.io/tls`; image pull ⇒ `kubernetes.io/dockercfg` + `imagePullSecrets`; Pod identity ⇒ `kubernetes.io/service-account-token`; node join ⇒ `bootstrap.kubernetes.io/token`; anything else ⇒ `Opaque`.
  - Why it works: typed Secrets get validated key names and are wired into controllers (Ingress TLS termination, kubelet image pull) without glue code.

- **`stringData` vs `data` — the input-format decision.**
  - When to use: `stringData` for human-authored plaintext values; `data` for base64 when the value is a large YAML file, a binary, or already-encoded material.
  - How: `stringData` lets Kubernetes handle encode/decode for you. Either way, **the stored result is always base64** — this is a Kubernetes storage convention, not a security boundary.
  - Failure mode: `kubectl edit secret` always presents the **base64** form. Typing plaintext there fails.

- **RBAC four-object model for Secrets**: `Role` + `RoleBinding` (namespace-scoped) and `ClusterRole` + `ClusterRoleBinding` (cluster-wide).
  - When to use: any time you need to answer "who can read this Secret?"
  - How:
    1. Discover the available verbs: `kubectl api-resources -o wide | grep secrets` → `create delete deletecollection get list patch update watch`.
    2. Write a `Role` with `apiGroups: [""]` (empty = core API group), `resources: ["secrets"]`, and the minimum verbs.
    3. Bind it with a `RoleBinding` whose `roleRef` points to a Role **in the same namespace**; `subjects` may come from other namespaces.
    4. Escalate to `ClusterRole`/`ClusterRoleBinding` only when the permission genuinely spans namespaces.

- **Audit policy scoped to Secrets** — record every Secret access without drowning in unrelated events.
  - When to use: from day one; it's the only way to detect unauthorized reads after the fact.
  - How: write a `Policy` at `level: Metadata` filtered to `resources: ["secrets"]`, `omitStages: ["RequestReceived"]`, pass it to `kube-apiserver --audit-policy-file=…`.

## Key Concepts
- **Opaque** — the default type; arbitrary user-defined key/values, from literals or files.
- **Long-lived access token** — a service account token materialized as a Secret. Pre-v1.27 this was automatic; it is still creatable by making an **empty Secret** of type `kubernetes.io/service-account-token` annotated with `kubernetes.io/service-account.name`.
- **Projected service account token** — the token mounted at `/var/run/secrets/kubernetes.io/serviceaccount/token`; a **JWT**.
- **Immutable Secret** — `immutable: true`. Edits are rejected with `data: Forbidden: field is immutable when 'immutable' is set`. **Permanently** immutable — the only path to change it is delete + re-apply.
- **`--record=true`** — stores the issuing command in the `kubernetes.io/change-cause` annotation.
- **`--save-config=true`** — stores the prior config in `kubectl.kubernetes.io/last-applied-configuration`, i.e. a poor man's backup.
- **Bootstrap token** — bearer-style token used only during cluster init, to join new nodes.
- **SOPS (Mozilla Secrets OPerationS)** — encrypts Secrets so they can live in Git; backs onto cloud KMS or PGP.
- **`apiGroups: [""]`** — the empty string denotes the **core** API group (where `secrets` lives).

## Mental Models
- **Think of a Secret's `type` as a contract with a controller, not a storage mode.** The bytes in etcd are identical; the type tells the Ingress controller / kubelet / apiserver how to use them.
- **Use `immutable: true` as a guardrail, not a lock.** It prevents accidental edits; it does not prevent deletion, and it does not encrypt anything.
- **Treat every environment identically.** "Having different handling of Secrets in different environments can cause issues in the long term, and the team will not be able to fully validate the security implications" — divergent dev/prod handling means you never actually test your production posture.
- **Think of Git-with-encryption as an alternative to a vault, not a fallback.** Git already gives you versioning (commit history), access control (repo rules), and durability (provider SLA); encryption via SOPS+KMS supplies the missing confidentiality.
- **A Secret's life starts before Kubernetes.** It sat in some other system first — secure storage upstream (Vault, GCP Secret Manager, AWS Secrets Manager) is part of the Secret's threat model.

## Code Examples

Namespace-scoped read-only access to Secrets — the least-privilege starting point:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: secret-viewer
rules:
- apiGroups: [""]          # "" = core API group
  resources: ["secrets"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: secret-viewer-binding
  namespace: default
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: secret-viewer        # must live in this namespace
subjects:
- kind: ServiceAccount
  name: secret-viewer
  namespace: default         # subjects MAY come from other namespaces
```
- **What it demonstrates**: the Role names the *action + target*; the RoleBinding names the *actor*. Both are needed.

Audit only Secret access, and only metadata (no payloads in your logs):

```yaml
apiVersion: audit.k8s.io/v1
kind: Policy
omitStages:
- "RequestReceived"
rules:
- level: Metadata
  resources:
  - group: ""
    resources: ["secrets"]
```
```bash
kube-apiserver --audit-policy-file=/path/to/audit-policy.yaml
# minikube:
minikube start \
  --extra-config=apiserver.audit-policy-file=/etc/ssl/certs/audit-policy.yaml \
  --extra-config=apiserver.audit-log-path=-
```
- **What it demonstrates**: `level: Metadata` records who/what/when without echoing the secret value into the audit log.

Long-lived service-account token, created deliberately:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: service-account-secret
  annotations:
    kubernetes.io/service-account.name: example-service-account
type: kubernetes.io/service-account-token
```
- **What it demonstrates**: an *empty* Secret plus one annotation; the controller fills in `ca.crt`, `namespace`, and `token`.

## Reference Tables

| Secret type | Purpose | Consumed by |
|---|---|---|
| `Opaque` | Default; arbitrary key/values or files | Env vars, volume mounts |
| `kubernetes.io/service-account-token` | Long-lived SA token (pre-v1.27 automatic) | Pods calling the K8s API |
| `kubernetes.io/dockercfg` / `dockerconfigjson` | Registry credentials | `imagePullSecrets` on a Pod |
| `kubernetes.io/basic-auth` | `username` + `password` keys | Apps, Ingress basic-auth |
| `kubernetes.io/ssh-auth` | SSH private key | Git/SSH clients |
| `kubernetes.io/tls` | `tls.crt` + `tls.key` | `Ingress.spec.tls[].secretName` |
| `bootstrap.kubernetes.io/token` | Cluster bootstrap / node join | kubeadm |

| Field | Input format | Stored as | Use when |
|---|---|---|---|
| `stringData` | plaintext UTF-8 | base64 | Human-authored simple values |
| `data` | base64 | base64 | Binaries, large files, pre-encoded material |

| Scope | Permission object | Binding object | `namespace` field |
|---|---|---|---|
| One namespace | `Role` | `RoleBinding` | Required on both |
| Cluster-wide | `ClusterRole` | `ClusterRoleBinding` | Absent |

## Worked Example

**Proving RBAC actually constrains a Pod — the admin/viewer pair.** The authors don't test RBAC with `kubectl auth can-i`; they run a Pod as the service account and read the logs:

1. `kubectl create sa secret-admin` and apply a `ClusterRole` with `resources: ["secrets"], verbs: ["*"]`, bound cluster-wide.
2. Run a Pod whose container is `bitnami/kubectl:latest` with `args: [create, secret, generic, test, --from-literal=literal1=text-for-literal-1]` and `serviceAccountName: secret-admin`.
3. `kubectl logs` on that Pod prints `secret/test created` — the Pod's *identity*, not the operator's kubeconfig, carried the permission.
4. Repeat with `kubectl create sa secret-viewer`, the namespaced `secret-viewer` Role, and a Pod running `get secret secret-to-view`. A viewer can read but a `create` would be rejected.
5. Turn on auditing and issue `kubectl get secret`; tail `kubectl logs -f kube-apiserver-minikube -n kube-system | grep audit.k8s.io/v1` to see the event land:

```json
{"kind":"Event","verb":"list","user":{"username":"minikube-user",
 "groups":["system:masters","system:authenticated"]},
 "sourceIPs":["192.168.49.1"],"responseStatus":{"code":200}}
```

The pattern generalizes: **exercise the permission from inside a Pod with the service account attached**, then confirm the audit trail recorded it.

## Anti-patterns
- **Editing a Secret and typing plaintext** — `kubectl edit` requires base64; the edit silently fails to mean what you intended.
- **Reaching for `ClusterRole` by default** — cluster-wide Secret admin is the widest possible blast radius; prefer namespaced `Role`.
- **Enabling audit at `level: Request`/`RequestResponse` for Secrets** — you would write secret payloads into the audit log. `Metadata` is the right level.
- **Divergent Secret handling per environment** — breaks automation and leaves production posture untested.
- **Storing Secrets in Git unencrypted** — Git's versioning and access control are real benefits, but only with SOPS/PGP/KMS encryption on top.
- **Expecting `immutable: true` to be reversible** — it is permanent for that object; plan for delete-and-recreate.
- **Deleting a Secret without a backup** — recovery requires an etcd restore or a prior `kubectl get secret -o yaml` dump.

## Key Takeaways
1. Every Secret type serializes to base64 in etcd; the `type` field changes **consumption**, not storage or protection.
2. Use `stringData` for authoring, `data` for binaries/large payloads — the stored form is base64 either way.
3. `apiGroups: [""]` (empty string) is the core group where `secrets` lives — a common RBAC gotcha.
4. Discover verbs with `kubectl api-resources -o wide | grep secrets` before writing a Role; grant the minimum.
5. `--record=true` and `--save-config=true` give you a change-cause trail and a last-known-good config on `kubectl edit`.
6. `immutable: true` is a permanent accidental-edit guard, not encryption.
7. Enable a Secrets-scoped audit policy at `level: Metadata` — auditing is how unauthorized access becomes detectable.
8. Secure the Secret *before* it reaches Kubernetes: upstream storage (Vault / AWS / GCP Secret Manager) is part of the same chain.

## Connects To
- **Ch 1**: base64 is encoding, not encryption — the reason RBAC + audit matter so much here.
- **Ch 3**: encryption at rest closes the gap RBAC cannot (etcd file, backups).
- **Ch 5**: audit policy becomes the compliance evidence trail.
- **Ch 12**: SOPS and Sealed Secrets are the "encrypted in Git" pattern developed fully.
- **Ch 13**: CI/CD jobs and Argo CD / GitOps secret injection.
- **Principle of least privilege / RBAC (NIST)** — the standard this chapter operationalizes.
