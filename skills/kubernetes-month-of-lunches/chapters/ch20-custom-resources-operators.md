# Chapter 20: Extending Kubernetes with Custom Resources and Operators

## Core Idea

Kubernetes is built on a highly available database (etcd) and a REST API that handles resources uniformly. That same architecture is extensible: you can define your own resource types via CustomResourceDefinitions (CRDs) and pair them with custom controllers that act on those resources. The Operator pattern takes this further by using CRDs and controllers together to automate full application life cycle management — deployment, upgrades, backups, and cleanup — for stateful or operationally complex applications.

---

## Frameworks Introduced

- **CustomResourceDefinition (CRD)**
  - What: A Kubernetes object (`kind: CustomResourceDefinition`) that registers a new resource type — its group, version, scope, names, and JSONSchema — in the API server.
  - When: Whenever you want to store domain-specific objects in Kubernetes and interact with them via `kubectl` like any native resource.
  - How: Define `apiVersion: apiextensions.k8s.io/v1`, set `spec.group`, `spec.names`, `spec.scope`, and a `schema.openAPIV3Schema` block. Deploy with `kubectl apply`.
  - Why-or-failure: Deleting a CRD cascades to all its instances — secure CRD-level RBAC tightly.

- **Custom Controller / Reconcile Loop**
  - What: An application (usually a Pod) that connects to the Kubernetes API, watches a resource type, and reconciles actual cluster state with the desired state declared in the resource.
  - When: Once CRDs alone are insufficient — you need side effects (create Namespaces, ServiceAccounts, Deployments, etc.) when objects are created, updated, or deleted.
  - How: The controller uses a watch (an endless event loop) that is notified of create/update/delete events. For each event it checks what exists and drives toward desired state — idempotently.
  - Why-or-failure: A controller that does not handle cleanup leaves orphaned Secrets, Namespaces, and PVCs that admins don't expect; design the delete workflow as carefully as the create workflow.

- **Operator Pattern**
  - What: A higher-level convention where one or more CRDs plus one or more custom controllers together encode the operational knowledge for a complex application — handling upgrades, backups, high-availability clustering, and teardown.
  - When: Third-party stateful applications (databases, message queues) or your own apps with complex, non-trivial upgrade or operational sequences that cannot be expressed in standard Kubernetes objects.
  - How: Deploy the Operator (usually a Deployment with RBAC), which itself installs CRDs via an init container and runs controller containers. Users then create simple custom resources (`NatsCluster`, `MysqlCluster`, `WebPinger`) and the Operator does the rest.
  - Why-or-failure: An Operator is a large dependency; if the upstream project stalls you may need to reverse-engineer it. Evaluate contributor activity, release cadence, and maturity before adopting.

---

## Key Concepts

1. **CRD scope** — A CRD can be `Namespaced` (resources live in a namespace) or `Cluster` (clusterwide). Scope is declared in `spec.scope`.

2. **API group and version** — Custom resources use a group (e.g., `ch20.kiamol.net`) and a version (e.g., `v1`). The `apiVersion` field in a custom resource YAML is `<group>/<version>`.

3. **JSONSchema validation** — CRDs embed an `openAPIV3Schema` block that Kubernetes uses to validate custom resource fields before storing them, the same way built-in resources are validated.

4. **Multiple versions** — A CRD can declare multiple versions under `spec.versions`. Each version has its own `schema`, `served` flag (whether it is exposed in the API), and `storage` flag (which version is persisted in etcd).

5. **Printer columns** — CRDs support `additionalPrinterColumns` that control what `kubectl get` displays. These are additive and do not affect stored resources.

6. **Cascade deletion** — Deleting a CRD deletes every instance of that custom resource. The Kubernetes API will refuse requests for the resource type once the CRD is gone.

7. **Control loop semantics** — A controller must be idempotent. Whether it is handling a brand-new resource or reacting to a restart, it must check what exists and create/update/delete only what is needed to reach desired state. It must never assume a clean slate.

8. **Controller ownership of cleanup** — When a custom resource is deleted, the controller is responsible for removing every Kubernetes resource it created. It should also watch those child resources so it can recreate them if an admin deletes them out-of-band.

9. **Operator deployment models** — Operators can be distributed via raw YAML manifests, Helm charts, or the Operator Lifecycle Manager (OLM) / OperatorHub catalog. Maturity varies widely; always assess the project's contributor count and release history.

10. **Operator residue on uninstall** — Operators often leave CRDs, ConfigMaps, Secrets, and PVCs behind when removed, because those may contain data. Manual cleanup of leftover resources is commonly required; use dedicated namespaces to make cleanup tractable.

---

## Mental Models

- **Kubernetes as a generic desired-state engine** — The API server is essentially a typed, watched key-value store. Every resource kind — built-in or custom — participates in the same watch-notify-reconcile loop. Custom resources get all standard verbs (create, get, list, watch, delete) for free; you only need to supply the controller logic that reacts to them.

- **CRD as a schema contract** — A CRD is the agreement between the resource author and the Kubernetes API about what fields a resource may contain. The API enforces the schema at admission time; controllers consume those fields at runtime. Changing the schema requires versioning (`v1`, `v1alpha1`, `v2beta2`) — the same discipline used by built-in resources.

- **Operator as encoded operational knowledge** — An Operator externalizes the runbook. Instead of a human following a checklist to upgrade a database (put into read-only, snapshot, upgrade, verify), the Operator controller watches for a version change in the custom resource and executes those steps automatically. The simpler the custom resource spec, the more knowledge the Operator is encoding.

- **Controllers build on controllers** — Operators do not reinvent Kubernetes. They create standard resources (Deployments, StatefulSets, Services, Secrets) that are then managed by Kubernetes' own built-in controllers. Deleting a custom resource triggers the Operator controller, which deletes a Deployment, which triggers the ReplicaSet controller, which deletes Pods.

---

## Anti-patterns

- **Using CRDs as a general-purpose database** — Storing domain objects that have no relationship to Kubernetes operations (e.g., to-do list items with no cluster side-effects) wastes the extension mechanism and couples unrelated data to cluster lifecycle. CRDs add value when the resources integrate with or extend what the cluster manages.

- **Skipping the delete workflow** — Controllers that handle create but not delete leave orphaned Namespaces, Secrets, and PVCs. Sensitive data (tokens, credentials) persists indefinitely. The delete handler must be as complete as the create handler.

- **Not watching child resources** — A controller that creates a Namespace and ServiceAccount but does not watch them cannot heal when an admin manually deletes them. Production controllers should watch all resources they own.

- **Building an Operator for simple apps** — Writing an Operator to wrap a single Deployment + ConfigMap + Service is overkill. Use admission controllers to enforce specification compliance instead. Reserve Operators for genuinely complex operational sequences.

- **Adopting an immature Operator for critical components** — An alpha-tagged Operator maintained by a single person is a risky dependency for a production database. Evaluate contributor count, release cadence, and backing organization before adopting.

- **Deploying CRD and resources in one shot** — CRDs take several seconds to register in the API server. Deploying a directory that contains both a CRD and its instances simultaneously often fails because the CRD is not yet available. Deploy the CRD first; deploy instances after.

---

## Code Examples

```yaml
# Listing 20.1 — todo-crd.yaml: CustomResourceDefinition
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: todos.ch20.kiamol.net       # must match <plural>.<group>
spec:
  group: ch20.kiamol.net
  scope: Namespaced
  names:
    plural: todos
    singular: todo
    kind: ToDo
  versions:
    - name: v1
      served: true
      storage: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              properties:
                item:
                  type: string
```

```yaml
# Listing 20.2 — todo-ch20.yaml: a custom resource instance
apiVersion: "ch20.kiamol.net/v1"
kind: ToDo
metadata:
  name: ch20
spec:
  item: "Finish KIAMOL Ch20"
```

```yaml
# Listing 20.5 — todo-list-queue.yaml: NatsCluster custom resource (NATS Operator)
apiVersion: nats.io/v1alpha2
kind: NatsCluster
metadata:
  name: todo-list-queue
spec:
  size: 3          # number of NATS Pods in the HA cluster
  version: "1.3.0"
```

```yaml
# Listing 20.6 — todo-list-db.yaml: MysqlCluster custom resource (Presslabs Operator)
apiVersion: mysql.presslabs.org/v1alpha1
kind: MysqlCluster
metadata:
  name: todo-db
spec:
  mysqlVersion: "5.7.24"
  replicas: 2
  secretName: todo-db-secret
  podSpec:
    resources:
      limits:
        memory: 200Mi
        cpu: 200m
```

```yaml
# Listing 20.8 — webpinger-blog.yaml: WebPinger custom resource (web-ping Operator)
apiVersion: "ch20.kiamol.net/v1"
kind: WebPinger
metadata:
  name: blog-sixeyed-com
spec:
  target: blog.sixeyed.com
  method: HEAD
  interval: "7s"
```

```yaml
# Listing 20.7 — Operator Pod spec pattern: init container installs CRDs, app containers are controllers
spec:
  serviceAccountName: web-ping-operator
  automountServiceAccountToken: true
  initContainers:
    - name: installer
      image: kiamol/ch20-wpo-installer          # creates CRDs
  containers:
    - name: pinger-controller
      image: kiamol/ch20-wpo-pinger-controller  # watches WebPinger resources
    - name: archive-controller
      image: kiamol/ch20-wpo-archive-controller # watches WebPingerArchive resources
```

---

## Reference Tables

### Built-in Resource vs. Custom Resource

| Dimension | Built-in resource (e.g., Pod, Deployment) | Custom resource |
|-----------|-------------------------------------------|-----------------|
| Definition | Baked into API server binary | Registered via CRD object |
| Schema | Versioned by Kubernetes release | Defined by author in `openAPIV3Schema` |
| kubectl support | Automatic | Automatic once CRD is applied |
| Verbs supported | get, list, watch, create, update, delete, patch | Same — all verbs automatic |
| Validation | Kubernetes enforces | JSONSchema defined in CRD |
| Cascade on delete | Owned resources via ownerReferences | Custom resource deleted when CRD is deleted |

### Controller vs. Operator

| Dimension | Custom Controller | Operator |
|-----------|-------------------|----------|
| Scope | Typically one CRD | One or more CRDs + multiple controllers |
| Goal | Automate a single workflow | Encode full application life cycle |
| Complexity | Low-to-medium | Medium-to-high |
| Typical targets | Internal tooling, user provisioning | Stateful third-party apps (databases, queues) |
| Distribution | YAML manifests | YAML, Helm, or OLM/OperatorHub |
| Operational knowledge encoded | Limited | Full (upgrades, backups, HA, teardown) |

---

## Worked Example

### Scenario: User Provisioning System (Section 20.2)

**Problem:** Smaller organizations use Kubernetes Service Accounts as end-user accounts. Creating a user requires creating a Namespace (for the group), a ServiceAccount, and a token — tedious to do manually and error-prone at scale.

**Step 1 — Define the CRD.** A `user-crd.yaml` registers a `User` kind in the `ch20.kiamol.net` group, namespaced scope, with fields for the user's name and group.

**Step 2 — Deploy CRD first, then users.**
```bash
kubectl apply -f users/crd/        # register the User type
kubectl apply -f users/            # create User instances
kubectl get users                  # lists users like any native resource
```
At this point, `User` objects are stored in etcd. No side effects yet — there is no controller.

**Step 3 — Deploy the custom controller.**
```bash
kubectl apply -f user-controller/
kubectl wait --for=condition=ContainersReady pod -l app=user-controller
kubectl logs -l app=user-controller
```
The controller Pod starts, connects to the Kubernetes API, and lists all existing `User` objects. For each user it:
1. Checks whether a Namespace for the group exists; creates it if not.
2. Checks whether a ServiceAccount for the user exists in that Namespace; creates it if not.
3. Creates a token Secret for the user.

The controller uses the same API verbs as `kubectl` but through a client library (Go or .NET), making the code feel natural but verbose.

**Step 4 — Add a new user.**
```bash
kubectl apply -f users/update/
kubectl logs -l app=user-controller --tail 4
kubectl get secret sre4-token -n kiamol-ch20-authn-sre -o jsonpath='{.data.token}' | base64 -d
```
The controller's watch receives a create event. It runs the same idempotent workflow: the group Namespace already exists so nothing is created there; it creates the ServiceAccount and token.

**Step 5 — Delete a user.**
```bash
kubectl delete user tester3
kubectl logs -l app=user-controller --tail 3
kubectl get ns -l kiamol=ch20
```
The controller receives a delete event. It removes the ServiceAccount and token. It then checks whether any other users remain in the group; finding none, it deletes the Namespace. The token Secret is deleted automatically by Kubernetes when the ServiceAccount is removed.

**Key insight:** The controller never assumes clean state. It checks for existence before creating and checks for remaining users before deleting the Namespace. This idempotent, check-first approach is the defining property of a well-built controller.

---

## Key Takeaways

1. A `CustomResourceDefinition` registers a new resource type in the Kubernetes API. Once deployed, all standard `kubectl` commands (get, describe, delete, watch) work on instances of that type automatically.

2. Custom resources alone have no behavior; a custom controller is required to react to create, update, and delete events and reconcile actual cluster state with the declared desired state.

3. Controllers must be idempotent — check what exists before creating or deleting. They must also implement the delete workflow as carefully as the create workflow to avoid orphaned resources.

4. Deleting a CRD deletes all instances of that custom resource. Secure CRD RBAC rules tightly in production.

5. The Operator pattern combines one or more CRDs with one or more controllers to encode full operational knowledge — HA clustering, upgrades, backups, teardown — into the cluster itself. Two lines of YAML can deploy a production-grade distributed message queue or replicated database.

6. Third-party Operators vary enormously in maturity. Evaluate contributor activity, backing organization, and release cadence; a single-maintainer alpha Operator is a risky dependency for a core database.

7. Build your own Operator only when operational complexity genuinely justifies it — non-trivial upgrade sequences, routine operational tasks that must be automated. For simple apps, admission controllers are a better fit.

---

## Connects To

- **Chapter 17 (RBAC and Authentication):** The user-provisioning controller in this chapter automates the manual steps from section 17.3. CRD-level RBAC must be configured to prevent unauthorized deletion of CRDs (which cascades to all instances).

- **Chapter 8 (StatefulSets):** Operators like the MySQL Operator generate StatefulSets under the hood. Understanding StatefulSet semantics clarifies what an Operator is managing on your behalf.

- **Chapter 14 (Monitoring):** The MySQL Presslabs Operator automatically includes a Prometheus exporter sidecar and Prometheus annotations on database Pods, integrating with the cluster monitoring stack from chapter 14 without extra configuration.

- **Chapter 10 (Helm):** The MySQL Operator is distributed and installed via Helm. The web-ping Operator custom resources provide the same "fill in two fields and get an app" experience that Helm chart values provide, but with the addition of ongoing reconciliation.

- **Chapter 9 / Admission Controllers:** For apps that don't need full Operator complexity, admission controllers are the right tool to enforce correct resource specifications — an alternative to building a controller just to validate or default fields.

- **cert-manager (CNCF project):** Cited as a production-grade example of CRDs and custom controllers. Manages TLS certificates as Kubernetes resources and automatically requests and applies them to web applications.
