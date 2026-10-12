# Chapter 15: The Kubernetes API

## Core Idea
Kubernetes is **API-centric**: every resource is defined in the API, and all communication (clients, kubelets, control plane services) flows through the **API server**, which acts as the **front-end to the cluster**. Master the API and you master Kubernetes. The API server exposes a large, modular **RESTful** interface; clients issue CRUD requests that are authenticated, authorized, then executed and persisted.

## Frameworks Introduced
- **API server as front-end** — the single entry point ("Grand Central station"); everything talks to everything via REST calls to it.
- **RESTful CRUD-over-HTTP** — Create/Read/Update/Delete map to POST/GET/PUT/PATCH/DELETE.
- **API groups** — core group vs named groups, dividing a once-monolithic API.
- **API versioning** — alpha → beta → stable (GA) maturity pipeline.
- **Extending the API** — Custom Resource Definitions (CRDs) + custom controllers.

## Key Concepts
- **Resources vs objects** — *resource* = the API definition; *object* = a running instance on the cluster. Used interchangeably; most resources are objects (some are lists or operations).
- **JSON serialization** — objects serialized to JSON strings for network transit (HTTP) and storage in the cluster store; reverse is deserialization. **Protobuf** also supported (faster/smaller, used internally); JSON used for external clients. Clients advertise schema via `Content-Type` header.
- **API server** — control plane service (sometimes Pods in `kube-system`); uses TLS, authN + authZ; must be highly available and performant. Commonly on port **443 or 6443**.
- **REST** = REpresentational State Transfer. A request = a **verb** (action / HTTP method) + a **path** (URI to the resource).
- **Core API group** — mature early resources (Pods, Nodes, Services, Secrets, ServiceAccounts) under `/api/v1`; sometimes shown as empty quotes `''`. No new resources added here.
- **Named API groups** (sub-groups) — all new resources; under `/apis/{group}/{version}/`. E.g. `apps` (Deployments, StatefulSets, DaemonSets), `networking.k8s.io` (Ingress, NetworkPolicy), `storage.k8s.io`, `batch`.
- **GVR** = Group, Version, Resource — the structure of REST paths.
- **Namespaced vs cluster-scoped** — namespaced objects have longer paths (`.../namespaces/{namespace}/...`).
- **watch** — a GET-based verb to observe object changes (e.g. kubelets watch the API server for tasks).
- **CustomResourceDefinition (CRD)** — lets you add resources that look/feel native, with their own REST paths.

## Mental Models
- **Everything is an object served by one RESTful API.** If a resource isn't in the API, you can't deploy it.
- **Amazon analogy** — Stuff = Resources/objects; Warehouse = API; Browser = kubectl; Amazon website = API server. You order (create), track (watch), receive (deployed), and return (delete) all through the website (API server).
- **POSTing to the API server** — creating an object = HTTP POST of its YAML/JSON manifest.
- The API is becoming the **de facto cloud API**, with vendors extending it (e.g. storage snapshot scheduling via custom resources alongside CSI/StorageClasses).

## Anti-patterns
- Using **alpha** resources in production (experimental, "hairy and scary", may be dropped without warning; often disabled by default).
- Treating **beta** as production-safe by default — pre-release, small changes still expected at GA; decide per-cluster.
- Expecting new resources in the **core group** — they only go to named groups.
- Ignoring **deprecation warnings** (e.g. `extensions/v1beta1` Ingress) instead of migrating.
- Running a poorly-resourced or non-HA control plane — slow API responses or total loss of API access.

## Code Examples

```bash
# Cluster address/port
$ kubectl cluster-info
# Kubernetes control plane is running at https://kubernetes.docker.internal:6443

# kubectl command -> REST request
$ kubectl get pods --namespace shield     # GET /api/v1/namespaces/shield/pods

# Proxy the API to localhost (handles auth)
$ kubectl proxy --port 9000 &

# Raw REST calls via the proxy
$ curl -X GET http://localhost:9000/api/v1/namespaces/shield/pods
$ curl http://localhost:9000/api            # core group versions -> {"kind":"APIVersions","versions":["v1"]...}
$ curl http://localhost:9000/apis           # named groups list (APIGroupList)

# POST (create) a Namespace from JSON
$ curl -X POST -H "Content-Type: application/json" \
    --data-binary @ns.json http://localhost:9000/api/v1/namespaces

# DELETE
$ curl -X DELETE -H "Content-Type: application/json" \
    http://localhost:9000/api/v1/namespaces/shield
```

```bash
# Inspect the API
$ kubectl api-resources     # all resources+groups, shortnames, NAMESPACED, KIND
$ kubectl api-versions      # all served group/versions (spot alpha/beta/v1/v2)
$ kubectl get --raw /apis/apps/v1   # raw GET of a REST path
```

```yaml
# crd.yml — minimal CRD (cluster-scoped "books" in nigelpoulton.com group, v1)
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: books.nigelpoulton.com      # must be plural.group
spec:
  group: nigelpoulton.com           # named API group
  scope: Cluster                    # or Namespaced
  names:
    plural: books
    singular: book                  # used on CLI/output
    kind: Book                      # used in YAML files
    shortNames: ["bk"]
  versions:
    - name: v1
      served: true                  # false = not served
      storage: true                 # store instances as this version
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              properties: {}         # define resource properties here
```

```yaml
# kcna.yml — an instance of the custom resource
apiVersion: nigelpoulton.com/v1
kind: Book
metadata:
  name: kcna
spec:
  bookTitle: "The KCNA Book"
  topic: Certifications
  edition: 1
```

## Reference Tables

CRUD verb ↔ HTTP method ↔ kubectl:

| K8s CRUD verb | HTTP method | kubectl example |
|---------------|-------------|-----------------|
| create        | POST        | `kubectl create -f <file>` |
| get, list, watch | GET      | `kubectl get pods` |
| update        | PUT / PATCH | `kubectl edit deployment <name>` |
| delete        | DELETE      | `kubectl delete ingress <name>` |

(Names don't always align: `kubectl edit` = update verb = HTTP PATCH.)

API maturity levels:

| Level | Path example | Stability guarantee |
|-------|--------------|---------------------|
| **alpha** | `/apis/apps/v1alpha1/xyz` | Experimental; bugs, features dropped without warning; often disabled by default |
| **beta** | `/apis/apps/v1beta1/xyz` | Pre-release; small changes expected at GA; enabled by default; **9-month** window to release new beta or graduate |
| **stable / GA** | `/apis/apps/v1/xyz`, `/apis/autoscaling/v2/...` | Production-ready; strong long-term commitment; deprecation support **12 months or 3 releases, whichever is longest** |

Core vs named group paths:

| Type | Path prefix | Notes |
|------|-------------|-------|
| Core | `/api/v1/...` | Singular `api`, no group name; e.g. `/api/v1/namespaces/{ns}/pods/` |
| Named | `/apis/{group}/{version}/...` | Plural `apis` + group; e.g. `/apis/networking.k8s.io/v1/.../ingresses/` |

## Worked Example: extend the API with a CRD
1. **Inspect** existing groups/versions: `kubectl api-resources`, `kubectl api-versions`, or `curl .../apis` via `kubectl proxy`.
2. **Create the resource**: `kubectl apply -f crd.yml` → CRD registered; served at `apis/nigelpoulton.com/v1/books/`.
3. **Verify in API**: `kubectl api-resources | grep books`, `kubectl explain book` (→ `KIND: Book  VERSION: nigelpoulton.com/v1`).
4. **Create an instance**: `kubectl apply -f kcna.yml` → `book.nigelpoulton.com/kcna created`.
5. **Use native tooling**: `kubectl get bk` (shortname works); `curl http://localhost:9000/apis/nigelpoulton.com/v1/` shows the resource with verbs incl. `watch`.
6. **Custom resources are inert** until you write a **custom controller** to act on them.
7. **Clean up**: `kubectl delete book kcna`; `kubectl delete crd books.nigelpoulton.com`; kill the proxy.

## Key Takeaways
- Kubernetes is API-driven; the **API server is the front-end to the cluster** and the single point all clients (internal + external) pass through for authN/authZ.
- The API is a **modern resource-based RESTful API** doing CRUD via POST/GET/PUT/PATCH/DELETE.
- It's split into the **core group** (`/api/v1`, mature resources, frozen) and **named groups** (`/apis/...`, all new resources) for scalability and extensibility.
- Resources mature **alpha → beta → GA(stable)**; GA carries a firm deprecation policy (≥12 months / 3 releases).
- **CRDs** make custom resources first-class; pair with a **custom controller** to make them do something.
- A healthy, **highly-available, performant control plane** is essential — the API server is the bottleneck for the whole cluster.

## Connects To
- **Ch on API security / RBAC** — verbs, authN/authZ on every request; ClusterRole lives in `rbac.authorization.k8s.io`.
- **Ch on Pods / Deployments / StatefulSets / DaemonSets** — the `apps` named group resources.
- **Ch on Services / Ingress / NetworkPolicy** — `networking.k8s.io`.
- **Ch on Storage** — StorageClass (`storage.k8s.io`), CSI drivers + custom resources for advanced features.
- **Ch on cluster store (etcd) & control plane** — where serialized objects are persisted and the API server runs.
