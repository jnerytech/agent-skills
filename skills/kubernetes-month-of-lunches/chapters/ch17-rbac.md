# Chapter 17: Securing Resources with Role-Based Access Control

## Core Idea

Kubernetes RBAC is an additive, grant-only permission model that controls what subjects (users, groups, service accounts) can do to which resources. Permissions are never denied explicitly — the absence of a grant is a deny. Every production cluster must treat least-privilege as non-negotiable: attackers who compromise an over-privileged account inherit everything that account can do.

---

## Frameworks Introduced

- **Least-Privilege**
  - **What:** Grant subjects only the exact permissions required for their job, restricted to the narrowest namespace scope possible.
  - **When:** Every role and binding you create, for both end users and service accounts.
  - **How:** Start from zero (no roles), add only what is needed, prefer named resources (`resourceNames`) when possible, create a dedicated service account per app that uses the API.
  - **Why-or-failure:** Shared service accounts accumulate permissions over time; a compromised app in the same namespace inherits all of them.

- **Role vs ClusterRole (scope boundary)**
  - **What:** Role applies within one namespace; ClusterRole applies cluster-wide (or can be referenced by a namespaced RoleBinding to scope it down).
  - **When:** Use Role + RoleBinding for namespace-scoped resources. Use ClusterRole when the resource is cluster-scoped (Namespaces, PersistentVolumes, Nodes) or when the same permission pattern should be reused across many namespaces.
  - **How:** A RoleBinding referencing a ClusterRole grants that ClusterRole's permissions only inside the binding's namespace — a powerful pattern for sharing role definitions without granting cluster-wide access.
  - **Why-or-failure:** Using ClusterRoleBinding instead of RoleBinding when namespace scope is sufficient silently grants access to every namespace, including `kube-system`.

- **Binding Subjects: User / Group / ServiceAccount**
  - **What:** A subject is the identity that receives the role.
  - **When:** Users and groups are for external (human) callers; ServiceAccounts are for in-cluster workloads.
  - **How:** Manage group membership in the external auth system; let Kubernetes RBAC reference the group name. For service accounts, use the canonical prefix `system:serviceaccount:<namespace>:<name>`.
  - **Why-or-failure:** Omitting the namespace from a service-account group subject accidentally targets every account in the cluster, which can elevate every Pod to cluster-admin (a real Docker Desktop bug).

---

## Key Concepts

1. **RBAC objects:** Role, ClusterRole, RoleBinding, ClusterRoleBinding — all in API group `rbac.authorization.k8s.io/v1`.
2. **Verbs:** The actions Kubernetes permits — `get`, `list`, `watch`, `create`, `update`, `patch`, `delete`, `approve`. `"*"` means all.
3. **apiGroups:** Core resources (Pods, Services, Namespaces) use `""`. Other resources use their group, e.g., `certificates.k8s.io`.
4. **Subresources:** Some resources require explicit subresource permissions, e.g., `pods/log` must be listed separately from `pods`.
5. **resourceNames:** Roles can restrict access to a specific named resource instance, not just the type — useful for single-ConfigMap or single-Namespace access.
6. **Predefined cluster roles:** `cluster-admin` (all verbs, all resources), `admin` (all within namespace), `edit` (create/update/delete within namespace), `view` (read-only). Start here before building custom roles.
7. **User authentication:** Kubernetes does not authenticate end users directly; it trusts external providers (AD, LDAP, OIDC). For lab clusters, client certificates issued by Kubernetes can serve as identity. The certificate's `CN` field becomes the username; `O` fields become groups.
8. **Service account tokens:** JWT tokens mounted automatically at `/var/run/secrets/kubernetes.io/serviceaccount/token`. Creating a Secret of type `kubernetes.io/service-account-token` causes the cluster to populate it. Tokens can be revoked by deleting the Secret.
9. **kubectl impersonation:** `--as <user>` and `--as system:serviceaccount:<ns>:<name>` let you test RBAC without switching contexts.
10. **kubectl auth can-i:** The canonical command for permission checking. Can be combined with `--as`, `-n`, and `--all-namespaces`.

---

## Mental Models

**RBAC as a graph, not a list**
Think of permissions as edges in a graph: Subject → RoleBinding → Role → Rule (resource + verb). There is no "deny" edge; the union of all matched edges determines what a subject can do. Auditing requires traversing the full graph, not just looking at one binding.

**Namespace as security boundary**
A namespace is not just a naming scope; it is the permission boundary. A Role in `kube-system` applies only there. A RoleBinding in `default` pointing to a ClusterRole grants that role only in `default`. Keeping unrelated workloads in separate namespaces limits blast radius when permissions are misconfigured.

**Service accounts are not users, but can play the role**
In clusters without an external identity provider, service accounts with JWT tokens distributed to humans can act as user accounts. Namespaces serve as "groups" (the `system:serviceaccounts:<ns>` group). This is a pragmatic escape hatch, not a long-term solution — migrate to OIDC when scale demands it.

**RBAC is evaluation at request time**
Permissions are not cached in the Pod or the service account object. When you add or remove a RoleBinding, the change takes effect on the very next API call — no Pod restart required.

---

## Anti-patterns

- **Handing out `cluster-admin`:** Giving the `cluster-admin` ClusterRole to any workload, user, or group that doesn't strictly need it. A compromised account with this role can delete all workloads, read every Secret in every namespace, and reconfigure the cluster. The `rbac-tools` service account in this chapter's own exercises was given `cluster-admin` for convenience — the book explicitly calls this out as lazy and wrong.
- **Binding roles to the default service account:** Any Pod that does not specify a `serviceAccountName` uses the default. If the default account accumulates roles from multiple apps, every new Pod in that namespace inherits the union of those permissions.
- **Using ClusterRoleBinding when RoleBinding suffices:** Grants access across all namespaces unintentionally.
- **Omitting the namespace from a service-account group subject:** `system:serviceaccounts` (no namespace) targets every service account in the cluster. Always specify: `system:serviceaccounts:<namespace>`.
- **Storing kubectl config files with embedded certificates insecurely:** The config file then contains everything needed to authenticate to the cluster.
- **Not managing file apply order when roles depend on resources:** RBAC rules that reference named resources (a specific Namespace, a specific ConfigMap) must be created after those resources exist. Use filename prefixes (`01-`, `02-`) to control `kubectl apply -f <folder>` order.

---

## Code Examples

```yaml
# Role: read Pods in one namespace
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: default
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
```

```yaml
# RoleBinding: bind Role to a ServiceAccount
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: pod-reader-binding
  namespace: default
subjects:
- kind: ServiceAccount
  name: my-app
  namespace: default
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: pod-reader
```

```yaml
# ServiceAccount
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app
  namespace: default
```

```yaml
# ClusterRole: access cluster-scoped resource (Namespaces), named resource
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: ch17-reader
rules:
- apiGroups: [""]
  resources: ["namespaces"]
  resourceNames: ["kiamol-ch17"]
  verbs: ["get"]
```

```yaml
# ClusterRole: certificates (multi-rule, multiple apiGroups)
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: create-approve-csr
rules:
- apiGroups: ["certificates.k8s.io"]
  resources: ["certificatesigningrequests"]
  verbs: ["create", "get", "list", "watch"]
- apiGroups: ["certificates.k8s.io"]
  resources: ["certificatesigningrequests/approval"]
  verbs: ["update"]
- apiGroups: ["certificates.k8s.io"]
  resources: ["signers"]
  resourceNames: ["kubernetes.io/kube-apiserver-client"]
  verbs: ["approve"]
```

```yaml
# RoleBinding: bind predefined ClusterRole "view" to a User, scoped to default namespace
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: reader-view
  namespace: default
subjects:
- kind: User
  name: reader@kiamol.net
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: view
  apiGroup: rbac.authorization.k8s.io
```

```yaml
# RoleBinding: subject in a different namespace than the binding
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: kube-explorer-system
  namespace: kube-system
subjects:
- kind: ServiceAccount
  name: kube-explorer
  namespace: default          # subject lives in a different namespace
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: system-pod-reader
```

```yaml
# ClusterRole + subresource: Pod logs
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: logs-reader
rules:
- apiGroups: [""]
  resources: ["pods", "pods/log"]
  verbs: ["get"]
```

```bash
# Check your own permissions
kubectl auth can-i "*" "*"

# Check another user's permissions (impersonation)
kubectl get pods --as reader@kiamol.net

# Check a service account's permissions
kubectl auth can-i "*" "*" --as system:serviceaccount:kiamol-ch17:default

# Check a specific verb/resource for a service account, in a namespace
kubectl auth can-i get pods -n kiamol-ch17 --as system:serviceaccount:kiamol-ch17:default

# Check all namespaces
kubectl auth can-i create csr -A --as system:serviceaccount:default:user-cert-generator

# Describe the cluster-admin ClusterRole
kubectl describe clusterrole cluster-admin

# Verify RBAC is enabled
kubectl api-versions | grep rbac
```

---

## Reference Tables

### Role vs ClusterRole

| Dimension | Role | ClusterRole |
|---|---|---|
| Scope of permissions | One namespace (where the Role lives) | Cluster-wide, or any namespace when referenced by a RoleBinding |
| Cluster-scoped resources (Nodes, PVs, Namespaces) | Cannot grant | Can grant |
| Typical use | App-level or team-level namespace access | Shared permission templates, cluster infra components, cross-namespace reuse |

### RoleBinding vs ClusterRoleBinding

| Dimension | RoleBinding | ClusterRoleBinding |
|---|---|---|
| Namespace scope | Permissions apply only in the binding's namespace | Permissions apply in every namespace (or cluster-scoped resources) |
| Can reference | Role or ClusterRole | ClusterRole only |
| Best for | Most use cases — least privilege default | Cluster-wide admin, monitoring agents, cluster infra |

### Subject Kinds

| Kind | `name` value | `namespace` field | Notes |
|---|---|---|---|
| `User` | String matching the authenticated identity (e.g., CN in cert) | Not used | Kubernetes does not store users; name must match what the auth system presents |
| `Group` | Group name (e.g., `O` field in cert, or OIDC claim) | Not used | For service account groups use `system:serviceaccounts:<ns>` |
| `ServiceAccount` | Name of the ServiceAccount object | Required — the namespace the SA lives in | Kubernetes manages auth (JWT token) natively |

### Service Account Group Names (built-in)

| Group | Who belongs |
|---|---|
| `system:serviceaccounts` | Every service account in the cluster (danger: cluster-wide) |
| `system:serviceaccounts:<namespace>` | Every service account in that namespace |

---

## Worked Example

**Goal:** Allow an app's service account to list and get Pods in the `default` namespace only, then verify it cannot do anything else.

**Step 1 — Create a dedicated ServiceAccount**

```bash
kubectl apply -f - <<EOF
apiVersion: v1
kind: ServiceAccount
metadata:
  name: kube-explorer
  namespace: default
EOF
```

**Step 2 — Create a Role with minimal verbs**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: default
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list"]
```

**Step 3 — Bind the Role to the ServiceAccount**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: kube-explorer-pod-reader
  namespace: default
subjects:
- kind: ServiceAccount
  name: kube-explorer
  namespace: default
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: pod-reader
```

**Step 4 — Verify with `kubectl auth can-i`**

```bash
# Should return "yes"
kubectl auth can-i list pods -n default \
  --as system:serviceaccount:default:kube-explorer

# Should return "no"
kubectl auth can-i delete pods -n default \
  --as system:serviceaccount:default:kube-explorer

# Should return "no" (different namespace)
kubectl auth can-i list pods -n kube-system \
  --as system:serviceaccount:default:kube-explorer
```

The RoleBinding is scoped to `default`, so the service account has no access to `kube-system` even though the same Pod type exists there. The account cannot delete Pods because `delete` was not listed in the Role's verbs. No changes to the app or Pod are needed when you add or remove the binding — RBAC evaluation happens at request time.

---

## Key Takeaways

1. RBAC is additive and grant-only. Zero permissions is the secure default; every role binding is an explicit grant.
2. Prefer namespace-scoped Role + RoleBinding over ClusterRole + ClusterRoleBinding whenever namespace scope is sufficient.
3. Use predefined cluster roles (`view`, `edit`, `admin`) as starting points before writing custom roles.
4. Create a dedicated ServiceAccount for every app that calls the Kubernetes API. Never accumulate roles on the `default` service account.
5. `kubectl auth can-i` combined with `--as` is the primary tool for verifying permissions without side effects. Supplement with Krew plugins (`who-can`, `access-matrix`, `rbac-lookup`) for auditing at scale.
6. Guard `cluster-admin` aggressively — reserve it for automated platform processes, not human users or application service accounts.
7. Namespace scope in a Role's `metadata.namespace` is not just where the object lives; it is the scope where the permissions apply. A RoleBinding must be in the same namespace as the Role it references, but its subject can be in a different namespace.

---

## Connects To

- **Chapter 16 (Security Context / Pod security):** RBAC secures the API plane; Security Contexts secure the runtime plane. Both are required for defense-in-depth.
- **Chapter 2 (Pods) / Chapter 3 (Services):** RBAC does not control Pod-to-Pod network access — that is the domain of NetworkPolicy.
- **Chapter 4 (ConfigMaps and Secrets):** Secrets are RBAC-secured resources; a subject with `get` on Secrets in any namespace can extract credentials and service account JWT tokens, potentially escalating privilege.
- **Chapter 10 (Helm):** Helm releases often create ServiceAccounts and RBAC objects. Review generated manifests to confirm they follow least-privilege before applying to production.
- **Chapter 12 (Self-healing / Probes):** Controllers and operators require RBAC to watch and patch resources; their service accounts are high-value targets.
- **Admission controllers / OPA Gatekeeper (beyond this book):** RBAC controls who can call the API; admission controllers enforce what manifests are allowed through it — the next layer of the security stack.
