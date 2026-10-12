# Chapter 1: Understanding Kubernetes Secrets Management

## Core Idea
Kubernetes ships a Secrets *framework*, not a Secrets *vault* — `Secret` data is base64-encoded (not encrypted) and lands in etcd in plaintext, so security must be layered on deliberately across five exposure points: kube-apiserver, etcd's API, etcd's database file, the node filesystem, and backups.

## Frameworks Introduced

- **The five security exposures of a Kubernetes Secret**: enumerate every place the plaintext can leak, not just the API.
  - When to use: threat-modelling any cluster before choosing a Secrets strategy; also the checklist for "did my mitigation actually close the hole?"
  - How:
    1. `kube-apiserver` — the primary entry point; anyone who can `get secret` reads the value.
    2. `etcd` API service — API-driven, so any access or network trace exposes data.
    3. `etcd` database file — a plain binary file with **no encryption capability of its own**; `grep`-able.
    4. Kubernetes nodes — the etcd Pod's volume is attached to a node; node access ⇒ data access.
    5. Backups — cluster backups contain the etcd file; breaching the *backup system* yields every Secret.
  - Why it works: mitigations tend to target only #1 (RBAC). #3–#5 survive perfect RBAC, which is why encryption-at-rest (Ch 3) and backup strategy (Ch 6) are separate chapters.

- **Platform Secrets vs. Application Secrets** (the split that decides what may be offloaded).
  - When to use: deciding whether a given Secret belongs in etcd or in an external vault.
  - How: classify the Secret by who consumes it.
    - **Platform** — Secrets that internal Kubernetes components and third-party add-ons (storage, networking, controllers) need to talk to each other. **Keep these in Kubernetes.**
    - **Application** — credentials for external services (database, S3 bucket). **These are candidates for offload** to Vault/Conjur/Key Vault.
  - Why it works / failure mode: if platform Secrets are offloaded and the external vault partitions away, "the Kubernetes cluster will start collapsing, along with all the workloads." Offloading is a resilience trade, not a pure security win.

- **Declarative desired-state as the security surface**: every infrastructure requirement is a YAML manifest reconciled by controllers into etcd.
  - When to use: reasoning about *why* etcd is the crown jewel.
  - How: manifest → kube-apiserver → etcd record → controllers converge. etcd is continuously updated during creation, producing an audit-trail-like record — and a single plaintext store of everything.

## Key Concepts
- **Secret** — a Kubernetes API object whose `data` field holds key–value pairs with **base64-encoded** values.
- **base64 in Secrets** — an *encoding* for safe transport of special characters through the CLI, the wire, and kube-apiserver. It is **not** encryption and provides zero confidentiality.
- **ConfigMap** — sibling object whose `data` field expects **UTF-8 strings** (no encoding). Designed for env vars and app arguments, but widely abused for sensitive config — treat it with the same care as a Secret.
- **Opaque** — the default Secret `type`, meaning "I define the shape of `data` myself."
- **etcd** — the key-value store serving as Kubernetes' asset management service. "A corrupted etcd results in a full disaster scenario."
- **kubelet** — the node agent that **decodes the base64 payload** when injecting a Secret into a container.
- **CustomResourceDefinition (CRD)** — the standard extension object vendors use to add their own API objects, guaranteeing a common integration standard.
- **Reconciliation loop** — a controller that tracks the drift between desired and current state and adjusts the latter.
- **GitOps** — the practice that emerges organically from YAML manifests living in Git: one central point of config management with authorization, peer review, and organization built in.

## Mental Models
- **Think of base64 as an envelope, not a lock.** It survives the mail system; it does not stop the mailman reading it.
- **Think of Kubernetes as a service broker, not a security product.** "By design, Kubernetes will not become a storage system or an encrypted Vault." It provides the framework to interconnect third-party solutions that each own a domain.
- **Use the container/VM/bare-metal ladder to explain trade-offs**: bare metal = native performance, terrible utilization; VMs = isolation at the cost of OS sprawl; containers = near-native performance, no guest OS, but a new security paradigm most IT orgs haven't absorbed.
- **Assume the attacker got the backup.** If your mitigation only holds when nobody touches the node or the backup tarball, it is a control-plane control, not a data control.

## Code Examples

Minimal `Secret` — note the values are base64, and that is *all* the protection present:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: mysecret
type: Opaque
data:
  username: YWRtaW4K
  password: UGFja3QxMjMhCg==
```
- **What it demonstrates**: `YWRtaW4K` decodes to `admin` on any machine, any OS, any online decoder. Nothing in this manifest is confidential.

The `ConfigMap` counterpart — the one structural difference is the absence of encoding:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-environment
data:
  appversion1: dev
```
- **What it demonstrates**: `ConfigMap.data` takes raw UTF-8 strings. Developers drift sensitive config (license keys, connection strings) into here precisely because it's easier — a hacker reading it can pivot to other workloads or to the cluster itself.

## Reference Tables

| Component | Plane | Role | Secrets-relevant risk |
|---|---|---|---|
| `kube-apiserver` | Control | Exposes the API, performs CRUD against etcd | Primary breach entry point |
| `etcd` | Control | Key-value asset store | Plaintext at rest; API + file + volume exposure |
| `kube-scheduler` | Control | Binds Pods to healthy nodes | — |
| `kube-controller-manager` | Control | Runs reconciliation loops (nodes, jobs, endpoints, service accounts) | Manages service-account tokens |
| `cloud-controller-manager` | Control (optional) | Cloud provider abstractions | Holds cloud credentials |
| `kubelet` | Node + control | Reconciles Pod desired state | **Decodes base64** to inject Secrets |
| `kube-proxy` | Node | Network plumbing / rules | — |
| `container runtime` | Node | Runs containers | Privileged containers see node Secrets |

| | `Secret.data` | `ConfigMap.data` |
|---|---|---|
| Value encoding | base64 | raw UTF-8 string |
| Encrypted at rest by default | No | No |
| Intended for | credentials, tokens, certs, keys | env vars, app arguments |
| Actual risk | High | High (misused for sensitive data) |

## Worked Example

**Example 02 — proving a Secret is not secret, in seven steps.** The authors walk an attacker's path end-to-end:

1. `kubectl apply` a `Secret` manifest, then check its status.
2. `kubectl get secret -o yaml` to **recover the full definition back out** — including the payload. *Lesson: anyone who reaches kube-apiserver can exfiltrate some or all Secrets.*
3. Author a new Secret from scratch: base64-encode the pairs by hand, write the YAML, push it via CLI.
4. Reference the Secret from a `Pod` as an environment variable, using a `busybox` container, and `echo` it — **the value now appears in container logs**.
5. Observe that `kubelet` is the component that decoded the base64 on the way in.
6. Query the **etcd API directly**: the retrieved data is *neither encrypted nor base64-encoded*. A hacker who breaches the etcd Pod owns cluster asset management — and, in a cloud deployment, potentially the cloud account.
7. Extract the **etcd database file to the local filesystem** and read the Secret out of it. This is the step that generalizes to filesystem access and to cluster backups: even a well-hardened cluster leaks every Secret if the storage or backup system is breached.

The takeaway the authors draw: injecting a Secret adds almost nothing to the Pod-creation transaction cost — the cost is entirely in the security debt you inherit.

## Anti-patterns
- **Hardcoding Secrets into container images** — every stakeholder with registry access gets them; push to a public registry and the audience is the internet.
- **Treating base64 as protection** — the single most common misreading of the Secret spec.
- **Putting sensitive data in ConfigMaps** — no encoding, same lack of encryption, less scrutiny.
- **Running containers with `privileged: true`** — such a container "will have access to all Secrets from the node on which it runs," collapsing per-Pod isolation.
- **Offloading platform Secrets to an external vault** — introduces a partition-tolerance failure that takes the whole cluster down.
- **Assuming a vault solves it** — a vault "would only secure the application side," leaving ConfigMaps, multi-cluster mTLS certs, and platform Secrets exposed.
- **Single-node control plane in production** — production wants ≥3 control planes with dedicated worker nodes for resilience and separation of concerns.

## Key Takeaways
1. Kubernetes Secrets are **encoded, not encrypted** — assume plaintext everywhere until you explicitly add encryption at rest (Ch 3).
2. Enumerate all five exposures — apiserver, etcd API, etcd file, node filesystem, backups — before declaring a Secret "secured."
3. Classify every Secret as **platform** or **application**; only application Secrets are safe offload candidates.
4. `ConfigMap` deserves `Secret`-grade handling because developers put secrets in it.
5. `privileged: true` is a Secrets vulnerability, not just a workload-isolation one.
6. Backups are a first-class attack surface — they contain the unencrypted etcd file.
7. Security in Kubernetes Secrets management is "not as simple as ticking a box"; it's a layered design decision spanning platform, application, storage, and backup.

## Connects To
- **Ch 2**: Secret types, RBAC, and Pod Security Standards — the access-control layer over exposure #1.
- **Ch 3**: Encryption in transit and at rest in etcd — the direct mitigation for exposures #2–#3.
- **Ch 6**: Disaster recovery and backups — mitigation for exposure #5.
- **Ch 11–12**: HashiCorp Vault / CyberArk Conjur and integration patterns — the "application Secrets offload" path.
- **OCI (Open Container Initiative)** — the container standard underpinning portability.
- **CIA triad / defense in depth** — the security framing the chapter implicitly applies.
