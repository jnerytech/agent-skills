# Chapter 12: Integrating with Secret Stores

## Core Idea
There are **two consumption paradigms** — convert external Secrets into native Kubernetes Secrets, or fetch them directly at runtime — and roughly eight integration mechanisms; the alignment rule is that **Pod-lifecycle mechanisms (init containers, sidecars, CSI) naturally suit direct fetch, while Kubernetes extensions and API mechanisms (webhooks, CRDs, custom API servers) are inherently suited to conversion**.

## Frameworks Introduced

- **The two secret-consumption paradigms** — the first architectural decision, made before choosing any tool.

| | **Convert to native Kubernetes Secrets** | **Directly fetch from external store** |
|---|---|---|
| Freshness | May lag; needs sync | **Always latest version** |
| Caching | ✓ Fewer external requests | ✗ |
| Failure mode | **Eliminates a critical point of failure** | Direct dependency on the store |
| Latency | Low | Higher (external fetch) |
| Audit trail | Split across two systems | **Cleaner** |
| Cost | Redundancy + synchronization burden | — |

- **The six general configuration steps** — the integration runbook, tool-agnostic.
  1. **Selection of secret store** — weigh security requirements, scalability, compliance standards, and *team familiarity*.
  2. **Initialization and connecting to Kubernetes** — deploy inside the cluster or alongside it.
  3. **Handle authentication and authorization** — IAM roles, tokens, service accounts, or client certificates; plus fine-grained authorization so only entitled services reach designated Secrets.
  4. **Determine secret retrieval and consumption method** — the paradigm choice above.
  5. **Test the configuration** — verify retrieval and consumption *before* production.
  6. **Monitor and audit** — detect unauthorized access attempts and breaches.

- **The eight integration mechanisms**, grouped by layer:
  - *Kubernetes extensions / API mechanisms* (→ conversion): **admission controllers + mutating webhooks**, **CRDs + custom controllers**, **custom API server**.
  - *Pod lifecycle* (→ direct fetch): **init containers**, **sidecars**, **DaemonSets**, **environment controllers**.
  - *Specialized patterns*: **SealedSecrets**, **Secret Store CSI Driver**, **service mesh**, **broker systems**.

- **The SealedSecrets four-phase flow** — one-way encryption for Git.
  1. **Setup** — install the SealedSecrets controller and the `kubeseal` CLI.
  2. **Encrypt** — `kubeseal < secret.yaml > sealed-secret.yaml`, producing a `SealedSecret`.
  3. **Deploy** — `kubectl apply` it like any other resource; safe to commit to Git.
  4. **Decryption** — the in-cluster controller decrypts it into a **standard Kubernetes Secret**.
  - Why it works: "Secrets are encrypted in a way that **only the cluster itself can decrypt**." Developers hold the public key; administrators hold the decryption key.
  - **Important caveat**: once decrypted it *is* an ordinary Kubernetes Secret, subject to every etcd concern from Ch 1.

- **Broker vs. secretless broker** — a distinction the chapter insists on.
  - **Broker mechanism**: request → **validate identity and authorization** → fetch → transmit to the application → **audit and log**. The app is agnostic to storage location and retrieval method.
  - **Secretless broker**: goes one step further — *establishes the connection on the application's behalf* and **never reveals the secret to the application at all**.
  - Why brokers still matter: flexible across many application types, centralized control, granular access, **bridge the gap for legacy systems**, and handle secret *governance and lifecycle*, not just retrieval.

- **Service-mesh secret lifecycle (4 stages)** — for certificates and tokens specifically.
  1. **Dynamic secret creation** — the mesh integrates with an external CA or runs its own; certificates are generated on demand as services join.
  2. **Secret distribution** — delivered through the **sidecar proxies** accompanying each service instance.
  3. **Rotation and renewal** — automatic after a predefined period, old ones invalidated, **no downtime or manual intervention**.
  4. **Revocation** — on compromise, the mesh revokes the associated Secrets quickly.
  - Istio implements this with **Citadel** as the CA (generate, distribute, rotate, revoke), securing mTLS in the mesh, plus authentication, identity provisioning, and policy enforcement.

## Key Concepts
- **Admission controller** — control-plane component intercepting API requests **after authentication and authorization but before persistence**; can reject or modify the object.
- **Mutating webhook** — custom code run on resource create/modify; the way to inject secret references so "developers only specify a label or annotation."
- **CRD + custom controller** — the CRD adds the type; **the controller supplies the behavior**. "Just defining and creating the CRD doesn't give it functionality."
- **`ExternalSecret`** — the canonical CRD shape: `spec.backendType`, `spec.data[].key` (name in the store) and `.name` (name presented to Pods), `spec.region`.
- **Environment controller** — unlike CRDs, does **not** extend the API; it manipulates environment variables directly in the Pod's context, avoiding extra CRD/controller infrastructure.
- **Init container** — runs *before* application containers; fetches Secrets, populates a config file, writes to a shared volume (`emptyDir`).
- **Sidecar** — runs *alongside*; refreshes Secrets during the Pod's lifetime **without restarting the application**.
- **DaemonSet** — one Pod per node; right for **node-level** Secrets (e.g. a logging agent's credentials).
- **`tmpfs`** — the in-memory filesystem the CSI driver mounts into, so "Secrets aren't written to node disks."
- **Service mesh** — "a configurable infrastructure layer for microservice applications… implemented through lightweight network proxies deployed alongside application code **without the application needing to be aware**."

## Mental Models
- **Match the mechanism to the paradigm.** "Pod lifecycle-based methods, such as init containers and sidecars, naturally align with **direct fetch** methodologies… Kubernetes extensions and API mechanisms, although versatile, are inherently more suited for **conversion** to Kubernetes resources."
- **A CRD is a noun; the controller is the verb.** Applying an `ExternalSecret` does nothing until something is watching for it.
- **Init container = one-shot at start; sidecar = continuous refresh; DaemonSet = per-node.** Choose by *when* the secret must change.
- **A service-mesh proxy is a broker in disguise** — but its primary focus is secure service-to-service communication, not Secrets management. It is "not a one-size-fits-all solution for all secret types" and "shouldn't be seen as a complete replacement for comprehensive Secrets management."
- **Usability is the other side of the security coin.** "A system that's too cumbersome might lead to workarounds or shortcuts, negating the security benefits" — the shadow-IT risk from Ch 7, restated as a design constraint.
- **Think about blast radius explicitly.** "What happens if a node or an entire cluster is compromised?" Compartmentalize and isolate Secrets to bound the answer.

## Code Examples

Mutating webhook that intercepts Pod creation for secret injection:

```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: MutatingWebhookConfiguration
metadata:
  name: secret-injector-webhook
webhooks:
- name: secret-injector.example.com
  clientConfig:
    service:
      name: secret-injector-service
      namespace: default
      path: "/mutate"
    caBundle: [CA_BUNDLE]
  rules:
  - operations: ["CREATE"]
    apiGroups: [""]
    apiVersions: ["v1"]
    resources: ["pods"]
```
- **What it demonstrates**: developers write a label or annotation; the webhook injects the secret reference. Direct interaction with Secrets is abstracted away entirely.

The `ExternalSecret` CRD instance — note `key` vs `name`:

```yaml
apiVersion: k8s.example.com/v1
kind: ExternalSecret
metadata:
  name: my-database-password       # name in Kubernetes — need NOT match the store
spec:
  backendType: awsSecretsManager
  data:
  - key: database-password         # identifier in AWS Secrets Manager
    name: dbPassword               # name presented to Pods
  region: us-west-1
```
On apply, the controller: detects the resource → reads the backend and region → authenticates → retrieves `database-password` → presents it as `dbPassword` (as a native Secret, an env var, or a **tmpfs volume**, depending on the controller's design).

Init container populating a shared volume before the app starts:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-with-init-container
spec:
  initContainers:
  - name: fetch-secrets
    image: secret-fetcher:latest
    volumeMounts:
    - name: config-volume
      mountPath: /config
  containers:
  - name: main-app
    image: my-app:latest
    volumeMounts:
    - name: config-volume
      mountPath: /config
  volumes:
  - name: config-volume
    emptyDir: {}
```

Sidecar refreshing Secrets without an app restart — same shape, but **both containers under `containers:`**:

```yaml
spec:
  containers:
  - name: main-app
    image: my-app:latest
    volumeMounts: [{name: config-volume, mountPath: /config}]
  - name: secret-refresher
    image: secret-refresher:latest
    volumeMounts: [{name: config-volume, mountPath: /config}]
  volumes:
  - name: config-volume
    emptyDir: {}
```

SealedSecrets end to end:

```bash
kubeseal < secret.yaml > sealed-secret.yaml
```
```yaml
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: my-secret
  namespace: default
spec:
  encryptedData:
    password: [encrypted_value]     # safe to commit to Git
```
Applying it makes the controller emit a normal `Secret` named `my-secret`, consumed as usual via `secretKeyRef`.

Istio strict mTLS for a namespace:

```yaml
apiVersion: "security.istio.io/v1beta1"
kind: "PeerAuthentication"
metadata:
  name: "default"
  namespace: "foo"
spec:
  mtls:
    mode: STRICT
```

## Reference Tables

| Mechanism | Layer | Paradigm fit | Best for |
|---|---|---|---|
| **Mutating webhook** | API extension | Conversion | Abstracting Secrets away from developers' manifests |
| **CRD + controller** | API extension | Conversion | Kubernetes-native declarative access to an external store |
| **Custom API server** | API extension | Conversion | Teams fluent in `kubectl` but not the store's CLI |
| **Init container** | Pod lifecycle | Direct fetch | Config file must exist *before* the app starts |
| **Sidecar** | Pod lifecycle | Direct fetch | Periodic refresh **without restarting** the app |
| **DaemonSet** | Pod lifecycle | Direct fetch | Node-level agents needing node-scoped Secrets |
| **Environment controller** | Pod lifecycle | Direct fetch | Apps reading Secrets from env vars, without storing them in K8s |
| **SealedSecrets** | Specialized | Conversion | Secrets under version control in Git / CI-CD |
| **CSI Driver** | Specialized | Direct fetch | Unified file-mount access to many enterprise stores |
| **Service mesh** | Specialized | Direct fetch | **Certificates and tokens only** |
| **Broker** | Specialized | Either | Legacy systems, centralized governance |

**Secret Store CSI Driver — architecture and trade-offs**

| Aspect | Detail |
|---|---|
| Driver name | `secrets-store.csi.k8s.io` |
| **Dual architecture** | **CRD** drives behavior + external-store interaction; **DaemonSet** puts a copy on every node |
| Mounting | **Direct to `tmpfs` in-memory FS** — never written to node disks |
| Privileges | **Requires root on every host** (node-level CSI interface) |
| ✓ Unified access | One standard interface across many enterprise stores |
| ✓ Enhanced security | tmpfs; no disk persistence |
| ✓ Dynamic updates | If the external store supports it |
| ✗ Complex setup | The CRD + DaemonSet duality |
| ✗ Node-level access | Root on every node is a security concern in some environments |
| ✗ Provider dependencies | Feature availability varies by store |

| Security implication | Best practice response |
|---|---|
| **Dependency on external systems** — downtime or compromise hits the cluster | Back up the external store; plan contingencies |
| **Data transit exposure** | Encrypted channels (TLS), **both ends authenticate each other** |
| **Privilege escalation through brokers/sidecars** | Harden intermediaries; least privilege; monitor them |
| **Configurations and overly permissive access policies** | Fine-grained access control in the store |
| **Versioning / rotation sync mismatches** | Rotate periodically **and** have a propagation mechanism |
| (all of the above) | Use the store's **auditing**; watch for anomalous access patterns |

## Worked Example

**The broker request cycle, made concrete.** Service `foo` needs database credentials:

1. **Request** — `foo` sends "I need credentials for DB1" to the broker. It does **not** know where the secret lives or how to retrieve it.
2. **Validation** — the broker checks whether `foo` has the right permissions for DB1, verifying the sender's identity and authorization.
3. **Fetch and transmit** — on confirmation, the broker retrieves the secret from the store and securely hands it over.
4. **Audit and log** — every transaction, request and fetch alike, is logged.

The design payoff: "applications sidestep the intricacies of directly engaging with different secret stores; they merely need to interface with the broker." Swap AWS Secrets Manager for Vault and `foo` never changes.

**Then contrast with the secretless variant.** A secretless broker would take `foo`'s request and **open the database connection itself**, handing back a live connection rather than credentials. `foo` never sees the secret at all — so a compromise of `foo` yields nothing to exfiltrate. The trade-off is that the broker must understand the protocol it is brokering, which is why traditional brokers remain "invaluable… flexible, work with a vast array of applications… and often bridge the gap for legacy systems."

**Where this lands you architecturally**: the broker is a conversion-free, direct-fetch mechanism with centralized governance — sitting between the raw CSI mount (simplest, node-root required) and the service mesh (automatic, but certificates and tokens only).

## Anti-patterns
- **Creating a CRD without a controller** — the resource applies cleanly and does nothing.
- **Treating SealedSecrets as end-to-end encryption** — after decryption it is an ordinary Kubernetes Secret in etcd, with all of Ch 1's exposures.
- **Using a service mesh as a general Secrets manager** — it excels at certificates and tokens; it is "not a one-size-fits-all solution for all secret types."
- **Running a custom API server casually** — "running and maintaining a custom API server isn't trivial"; you own its security, scaling, and failover.
- **Extending the API and stopping there** — "just extending the API does not complete the loop"; agents or controllers must still deliver Secrets to Pods.
- **Unencrypted or unauthenticated transit** from store to cluster — both ends must authenticate.
- **Unhardened brokers and sidecars** — they become the attack vector that siphons the whole store.
- **Rotating in the store with no propagation mechanism** — produces stale Secrets in the cluster.
- **Never backing up the external store** — a compromise or failure then has no recovery path.
- **Vendor lock-in** — "favor those designed with open standards" to preserve ease of transition.
- **Designing for security at the expense of usability** — cumbersome systems produce workarounds that negate the benefit.

## Key Takeaways
1. Decide the **paradigm first** — convert to native Secrets (caching, no external SPOF, sync burden) or fetch directly (freshest, cleaner audit, latency + dependency).
2. **Align mechanism to paradigm**: Pod-lifecycle mechanisms → direct fetch; API extensions → conversion.
3. Run the **six configuration steps** in order, and don't skip step 5 (test before production).
4. **Mutating webhooks** let developers name a label instead of a secret — the cleanest developer-experience win in the chapter.
5. A **CRD needs a controller**; the `ExternalSecret` pattern separates the store-side `key` from the Pod-facing `name`.
6. **Init container** = populate before start; **sidecar** = refresh without restart; **DaemonSet** = node-level; **environment controller** = env vars without extending the API.
7. **SealedSecrets** makes Git-stored Secrets safe (only the cluster can decrypt) — but the decrypted result is a normal Kubernetes Secret.
8. The **CSI Driver** mounts into **`tmpfs`** so Secrets never hit node disks — at the cost of setup complexity and **root on every node**.
9. **Service meshes** (Istio + Citadel) automate create → distribute → rotate → revoke for **certificates and tokens**, with no downtime.
10. **Brokers** validate then deliver; **secretless brokers** connect on the app's behalf and never reveal the secret. Brokers remain the practical bridge for legacy systems.
11. Balance across **scalability, auditability, interoperability, blast radius, failure/recovery, cost, geographic redundancy, ease of transition, and compliance** (ISO 27001, PCI-DSS, HIPAA).

## Connects To
- **Ch 1**: SealedSecrets decrypt into ordinary Secrets — the etcd exposures still apply.
- **Ch 3**: transit encryption (TLS) and at-rest encryption remain necessary underneath any integration.
- **Ch 5**: CIS 5.4.1 (files over env vars) favours CSI/init-container mounts; CIS 5.4.2 is this whole chapter.
- **Ch 6**: "back up the external store" is the DR requirement restated.
- **Ch 7**: hardening brokers/sidecars addresses **secret valet parking**; centralized brokers address **sprawl** and **islands**; the usability warning is the **shadow IT** risk.
- **Ch 8/9/10**: the CSI driver and cloud providers as concrete instances.
- **Ch 11**: the Vault Agent Injector *is* a mutating webhook; the Conjur Kubernetes Authenticator Client *is* a sidecar.
- **Ch 13**: CI/CD pipeline secret management and the end-to-end production story.
- **Istio/Citadel, mTLS, Bitnami SealedSecrets, `kubeseal`, tmpfs** — external tools and primitives referenced.
