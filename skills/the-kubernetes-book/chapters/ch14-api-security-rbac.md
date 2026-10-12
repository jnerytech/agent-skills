# Chapter 14: API security and RBAC

## Core Idea
Kubernetes is API-centric: every action is a CRUD request (create/read/update/delete) to the API server. Every request — from kubectl, Pods, Kubelets, control plane services, and native apps — passes through the same three-stage security pipeline before execution: **authentication -> authorization -> admission control**. The client-to-API-server connection is always secured with TLS.

## Frameworks Introduced (AuthN -> AuthZ -> Admission request pipeline)
A request must pass all three stages, in order, or it is rejected:

1. **Authentication (authN, "auth en")** — Proves *identity*. Verifies the credentials embedded in every request. Fail -> HTTP **401** and request denied. Pluggable; no built-in identity database (forces external IAM, avoids an identity silo).
2. **Authorization (authZ, "auth zee") / RBAC** — Decides whether the authenticated identity *may* perform the action on the resource. Pluggable; multiple modules can run, and as soon as *any* module authorizes, the request proceeds. Fail -> **403 Access Denied**.
3. **Admission control** — Enforces *policy* on requests that modify cluster state. Read requests are not subject to admission control.

Airport analogy: passport = authentication, ticket = authorization, airline policy checks (luggage, etc.) = admission control.

## Key Concepts (5-10)
- **kubeconfig** — File (`~/.kube/config` on Linux/Mac, `C:\Users\<user>\.kube\config` on Windows) read by kubectl. Four top-level sections: `clusters`, `users`, `contexts`, `current-context`. A **context** = a cluster + a user.
- **Credentials** — Often an X.509 client certificate signed by the cluster's CA. Cert encodes the username in the **CN** property and group memberships in the **O** property.
- **RBAC (Role-Based Access Control)** — Most common authZ module. About three things: **users (subjects), actions (verbs), resources**. Which users can perform which actions against which resources.
- **Least privilege / deny-by-default** — Everything is locked down; you write allow rules to open access. Kubernetes RBAC supports **allow rules only — no deny rules** (simpler to implement/troubleshoot).
- **Role** — Defines a set of permissions (the *what*). Namespaced.
- **RoleBinding** — Binds a Role to users (the *who*). Namespaced. The username string must match a successfully authenticated username.
- **Rule fields** — `verbs` (permitted actions), `apiGroups` + `resources` (which objects). `""` (empty quotes) = core API group; all other groups named explicitly.
- **Admission controllers** — Mutating (can modify requests) and Validating (can only accept/reject). Mutating always run first.

## Mental Models (least privilege; Role = what, Binding = who)
- **Role = what, Binding = who.** A Role grants nothing until a Binding attaches it to a subject.
- **Deny-by-default.** No rule = no access. You never remove access, you only choose to grant it.
- **Define once, reuse everywhere.** Use a **ClusterRole** to define a permission set at cluster scope, then attach it per-Namespace with **RoleBindings** (one per Namespace).
- **Group-based admin.** Users authenticate as members of groups (e.g. `system:masters`); a ClusterRoleBinding maps the group to a ClusterRole.

## Anti-patterns (cluster-admin everywhere; wildcards in verbs/resources)
- Granting the built-in **cluster-admin** ClusterRole broadly — it allows all verbs on all resources in all Namespaces (equivalent to root, powerful and dangerous).
- **Wildcards** in rules: `verbs: ["*"]`, `resources: ["*"]`, `apiGroups: ["*"]` grant everything — demo only, do not create in real clusters.
- Relying on out-of-the-box **client certificates** in production instead of integrating an enterprise IAM (AD, cloud IAM).

## Code Examples

**Role** — read-only Deployments in the `shield` Namespace:
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: shield
  name: read-deployments
rules:
- verbs: ["get", "watch", "list"]   # allowed actions
  apiGroups: ["apps"]                # on resources
  resources: ["deployments"]         # of this type
```

**RoleBinding** — bind the Role to user `sky`:
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-deployments
  namespace: shield
subjects:
- kind: User
  name: sky                          # authenticated username
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: read-deployments             # Role to bind
  apiGroup: rbac.authorization.k8s.io
```
Result: `sky` can run `kubectl get deployments -n shield`.

**ClusterRole** — same permissions at cluster scope (no `metadata.namespace`, `kind: ClusterRole`); attach per-Namespace via RoleBindings:
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: read-deployments
rules:
- verbs: ["get", "watch", "list"]
  apiGroups: ["apps"]
  resources: ["deployments"]
```

Discover resources and their supported verbs (useful when writing rules):
```bash
kubectl api-resources --sort-by name -o wide
```

## Reference Tables

**RBAC object scope:**

| Object | Scope | Purpose |
|--------|-------|---------|
| Role | Namespaced | Define permissions in one Namespace |
| RoleBinding | Namespaced | Bind a Role (or ClusterRole) to subjects in one Namespace |
| ClusterRole | Cluster-wide | Define permissions across all Namespaces / cluster-scoped resources |
| ClusterRoleBinding | Cluster-wide | Bind a ClusterRole to subjects across all Namespaces |

All four share the `rbac.authorization.k8s.io` API sub-group; YAML structures are nearly identical.

**Verbs -> HTTP method -> response:**

| Kubernetes verb(s) | HTTP method | Common responses |
|--------------------|-------------|------------------|
| create | POST | 201 Created, 403 Access Denied |
| get, list, watch | GET | 200 OK, 403 Access Denied |
| update | PUT | 200 OK, 403 Access Denied |
| patch | PATCH | 200 OK, 403 Access Denied |
| delete | DELETE | 200 OK, 403 Access Denied |

**apiGroup / resource -> API path:**

| apiGroup | resource | API path |
|----------|----------|----------|
| `""` (core) | pods | /api/v1/namespaces/{ns}/pods |
| `""` (core) | secrets | /api/v1/namespaces/{ns}/secrets |
| `storage.k8s.io` | storageclass | /apis/storage.k8s.io/v1/storageclasses |
| `apps` | deployments | /apis/apps/v1/namespaces/{ns}/deployments |

## Worked Example
**Goal:** grant a subject read-only access to Pods in a single Namespace (`shield`).

Pods are in the **core API group**, so `apiGroups: [""]`.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: shield
  name: read-pods
rules:
- verbs: ["get", "watch", "list"]
  apiGroups: [""]            # core group for Pods
  resources: ["pods"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: shield
subjects:
- kind: User
  name: sky
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: read-pods
  apiGroup: rbac.authorization.k8s.io
```
Apply both -> `sky` can `kubectl get pods -n shield` but nothing else. (For a ServiceAccount subject, set `kind: ServiceAccount` and include its `namespace`.)

**Inspecting the built-in admin path (Docker Desktop):** the kubeconfig client cert identifies user `docker-for-desktop` in group `system:masters`; the `cluster-admin` ClusterRoleBinding maps `system:masters` to the `cluster-admin` ClusterRole (all verbs on all resources in all Namespaces).
```bash
kubectl describe clusterrole cluster-admin
kubectl describe clusterrolebindings cluster-admin
```

## Key Takeaways (3-7)
- Every API request passes TLS, then **authN -> authZ -> admission control**, in that order.
- RBAC is **deny-by-default, allow-only, least-privilege**; four objects: Role, RoleBinding, ClusterRole, ClusterRoleBinding.
- **Role/ClusterRole = permissions (what); RoleBinding/ClusterRoleBinding = grants to subjects (who).** A Role does nothing until bound.
- Rules combine `verbs` + `apiGroups` + `resources`; `""` = core group; avoid `*` wildcards and broad `cluster-admin`.
- Admission controllers enforce policy on state-changing requests only: **mutating** can modify, **validating** can only accept/reject; all must approve.

## Connects To
- **Ch15** — In-depth look at the Kubernetes API and API server.
- **Ch3** — Building the Docker Desktop cluster used in the cluster-admin example.
- **ServiceAccounts / Secrets** — non-human identities (Pods) authenticating to the API server.
- **External IAM** (AD, cloud IAM) — production-grade authentication replacing client certs.
