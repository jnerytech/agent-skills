# Patterns — Kubernetes Secrets Handbook

Techniques, integration patterns, and named anti-patterns with their canonical fixes.

---

## Envelope Encryption (DEK / KEK)
**When to use**: any compliance regime requiring external key management; any environment where control-plane disk access is a credible threat.
**How**: a **DEK** encrypts the payload and is generated locally by kube-apiserver; a **KEK** encrypts the DEK and is generated and hosted **remotely on the KMS**. Only the encrypted DEK reaches etcd. Configure via the `kms` provider in `EncryptionConfiguration` plus a KMS provider plugin (e.g. Trousseau) over a local UNIX socket.
**Trade-offs**: strongest option and the only one that keeps the key off the node — but adds configuration complexity and an external dependency. Use **one KEK per cluster**; a shared KEK is a single point of failure. KMSv2 caches the DEK in memory (fast, partition-tolerant); KMSv1 calls the KMS per transaction and is deprecated in 1.28. (Ch 3)

## Provider-List Migration (encryption at rest without downtime)
**When to use**: turning encryption on, changing providers, or rotating keys.
**How**: put the **new provider first** and keep the old one below it. New writes use provider #1; reads are header-driven so old objects still decrypt. Then **rewrite every Secret** to a new revision. Only after that, remove the old provider. Verify by dumping entries directly from etcd.
**Trade-offs**: non-disruptive, but changes only apply to objects you rewrite. Removing the old provider early makes unrewritten Secrets **permanently unreadable**. (Ch 3, Ch 7)

## Onion-Layer Defense for etcd
**When to use**: designing production etcd posture, especially self-managed/on-prem/edge.
**How**, outermost to innermost: **Transport (TLS everywhere, internal too)** → **Linux hardening (SCAP/CIS/NIST profiles, OpenSCAP scanning)** → **Disk encryption (FDE/SED)** → **Filesystem encryption (dm-crypt / LUKS / NBDE)** → **Kubernetes native encryption**.
**Trade-offs**: each ring stops a different attacker; none substitutes for another. TLS does nothing against a stolen disk; native encryption does nothing against a wire tap. (Ch 3)

## Filesystem Encryption Selection
**When to use**: choosing how to protect the etcd data file on disk.
**How**: **plain dm-crypt** for deniable, header-less, disaster-resilient block encryption; **LUKS** when you need key derivation, rotation, and multiple passphrases (composable with LVM/RAID); **NBDE/Tang** when you need transparent reboot without a passphrase and without operating a highly-available vault.
**Trade-offs**: dm-crypt has no KDF, no rotation, and TRIM leaks the encryption pattern. LUKS exposes a header (LVM-on-LUKS protects the layout but uses one key; LUKS-on-LVM is flexible but exposes the layout). TPM auto-unlock removes the passphrase prompt but travels with a stolen server. (Ch 3)

## RBAC Least-Privilege for Secrets
**When to use**: any time you must answer "who can read this Secret?"
**How**: discover verbs with `kubectl api-resources -o wide | grep secrets`; write a `Role` with `apiGroups: [""]` (core group), `resources: ["secrets"]`, and the **minimum** verbs; bind with a `RoleBinding` whose `roleRef` is same-namespace. Escalate to `ClusterRole`/`ClusterRoleBinding` only for genuinely cluster-spanning needs.
**Trade-offs**: namespaced roles need duplication across namespaces; cluster roles are one object with the widest blast radius. Verify by running a Pod with the ServiceAccount, not by reading the manifest. (Ch 2, Ch 13)

## Secrets-Scoped Audit Policy
**When to use**: from day one on every cluster.
**How**: `audit.k8s.io/v1` `Policy` at `level: Metadata`, `omitStages: ["RequestReceived"]`, filtered to `resources: ["secrets", "configmaps"]`; pass with `kube-apiserver --audit-policy-file=`.
**Trade-offs**: `Metadata` records who/what/when without payloads. `RequestResponse` captures the values — only use it with a secured log sink and a specific reason. Satisfies CIS 3.2.2. (Ch 2, Ch 5, Ch 7)

## Workload Identity (credential-free cloud access)
**When to use**: any Pod or CI/CD job that must call a cloud API.
**How**, by platform:
- **AWS (IRSA)**: IAM role trusting the cluster's OIDC provider via `sts:AssumeRoleWithWebIdentity`, with a `Condition` on `<oidc>:sub = system:serviceaccount:<ns>:<sa>`; annotate the SA with `eks.amazonaws.com/role-arn`.
- **Azure**: cluster with `oidc_issuer_enabled` **and** `workload_identity_enabled`; user-assigned managed identity; role assignment; **federated identity credential** with `subject = system:serviceaccount:<ns>:<sa>`; SA gets the `azure.workload.identity/client-id` annotation **and** the `use: "true"` label.
- **GCP**: `workload_identity_config { workload_pool }`; annotate the SA with `iam.gke.io/gcp-service-account`.
- **CI/CD**: Workload Identity Federation — an identity pool + OIDC provider, bound to one repository via `attribute.repository`.
**Trade-offs**: eliminates static credentials entirely. The scoping field (`sub` / `subject` / `attribute.repository`) **is** the security control — omit or loosen it and any workload can assume the identity. (Ch 8, Ch 9, Ch 10, Ch 13)

## Secrets Store CSI Driver
**When to use**: delivering external-store Secrets to Pods as files, keeping them out of etcd.
**How**: install the driver (Helm on EKS/GKE; built-in add-on on AKS and GKE Autopilot); declare a `SecretProviderClass` naming the provider and objects; mount it as a `csi` volume with `readOnly: true`. Architecture is **CRD (behavior) + DaemonSet (per-node presence)**, mounting into **tmpfs**.
**Trade-offs**: unified interface across stores; Secrets never persist to node disk; dynamic updates where the store supports them. But setup is complex (dual architecture), it **requires root on every node**, and features vary by provider. The **Sync Secret** option re-creates native Secrets in etcd — then encryption at rest is mandatory again. (Ch 8, Ch 12, Ch 14)

## Vault Kubernetes Auth (inverted trust)
**When to use**: integrating Vault without storing any Vault credential in the cluster.
**How**: configure a Vault service account able to call `TokenReview`; create a Vault role bound to a Kubernetes SA (`bound_service_account_names` / `_namespaces`) with a policy and TTL; grant the app's SA `system:auth-delegator`; the Pod's SA JWT is presented to Vault, which asks Kubernetes to validate it, then returns the secret.
**Trade-offs**: nothing sensitive lands in etcd — the strongest property of the pattern. Many moving parts; enable `vault audit enable file` early for debugging. (Ch 11)

## Vault Agent Injector (annotation-driven injection)
**When to use**: injecting Vault Secrets with no application or manifest changes beyond three annotations.
**How**: `vault.hashicorp.com/agent-inject: 'true'`, `/role: '<vault-role>'`, `/agent-inject-secret-<file>: '<path>'`. A **mutating admission webhook** rewrites the Pod spec to add agent containers rendering Secrets into a **shared memory volume** at `/vault/secrets/`; a sidecar updates them when Vault changes.
**Trade-offs**: cleanest developer experience; memory-only delivery. Requires the injector deployment and its webhook to be healthy — it is in the Pod-creation path. (Ch 11)

## Seal / Unseal with Shamir's Secret Sharing
**When to use**: initializing any production Vault.
**How**: `vault operator init` generates a root key, encrypts it, and stores it. The unseal key is split into **shares** requiring a **threshold** to reconstruct. Unsealing loads the decrypted root key into memory only. **Sealing** during an intrusion purges it and halts Vault.
**Trade-offs**: stolen shares below the threshold are worthless. `-key-shares=1 -key-threshold=1` (used in demos) defeats the entire mechanism. Losing enough shares loses the data. (Ch 7, Ch 11)

## SealedSecrets (Secrets in Git)
**When to use**: keeping application config and Secrets together under version control, especially with GitOps.
**How**: install the controller and `kubeseal`; `kubeseal < secret.yaml > sealed-secret.yaml`; commit and `kubectl apply`; the in-cluster controller decrypts it into a standard Secret.
**Trade-offs**: only the cluster can decrypt, so Git storage is safe. But the **decrypted result is an ordinary Kubernetes Secret** with all the etcd exposures. Works with Argo CD out of the box. (Ch 12, Ch 13)

## Init Container / Sidecar / DaemonSet Injection
**When to use**: **init container** when a config file must exist before the app starts; **sidecar** when Secrets must refresh without restarting the app; **DaemonSet** for node-level agents needing node-scoped Secrets.
**How**: share an `emptyDir` volume between the fetching container and the app container. With Workload Identity plus the provider's client libraries, you can build this yourself for stores with no official injector (e.g. GCP Secret Manager).
**Trade-offs**: all three are direct-fetch (no conversion, freshest values, cleaner audit) at the cost of latency and a hard dependency on the store. (Ch 11, Ch 12)

## Broker / Secretless Broker
**When to use**: decoupling applications from store specifics, and bridging legacy systems.
**How**: **broker** — request → validate identity and authorization → fetch → transmit → **audit and log**. **Secretless broker** — the same, except it opens the connection on the app's behalf and never reveals the secret.
**Trade-offs**: brokers centralize governance and work with almost any application; secretless brokers eliminate exfiltration from the app entirely but must understand the protocol they broker. Brokers and sidecars are themselves attack vectors — harden and monitor them. (Ch 12)

## Service Mesh Certificate Lifecycle
**When to use**: **certificates and tokens only**, when a mesh is already present.
**How**: dynamic creation (mesh CA or external CA) → distribution via sidecar proxies → automatic rotation and invalidation → revocation on compromise. Istio's **Citadel** implements this; enable with `PeerAuthentication` `mtls.mode: STRICT`.
**Trade-offs**: fully automated, no downtime, uniform policy. But sidecar proxies add latency and monitoring burden, and a mesh is **not** a general Secrets manager. (Ch 12)

## Backup Strategy Selection
**When to use**: designing Secrets DR.
**How**: **geo-replication** (active-active = fastest recovery, highest cost; active-DR = cheaper, more loss); **point-in-time snapshots to immutable storage** (full / incremental / differential); **write-to-multiple-places-in-transit** (encrypt → event stream → batch to immutable storage).
**Trade-offs**: incremental restores need the full backup **plus every** subsequent increment; differential needs only the full plus the latest differential. Snapshot recovery point is limited to the latest snapshot. Event streaming gives instant event-driven backup at the cost of complexity and duplication. Secrets data is tiny (often <1 GB), so storage cost rarely constrains the choice. (Ch 6)

## Secrets Versioning Strategy
**When to use**: deciding what to retain.
**How**: **all versions** (best audit trail, negligible cost given small payloads), **latest only** (cheapest, loses history), or **hybrid/selective** — multiple versions for critical Secrets, latest-only for the rest, plus retention policies by age or version count. **Always include metadata and annotations** — they carry the context recovery needs.
**Trade-offs**: hybrid is the authors' recommendation. Versioning is what makes rotation safe to attempt. (Ch 6)

## Secret Rotation Mechanics
**When to use**: implementing periodic rotation (commonly 30/60/90 days; see NIST SP 800-57).
**How**: **monitoring and reloading** (watch for change, update in application memory); **keyring mode** (multiple versions live, track which is in use, retire old ones); **restart as reload** (a Job detects rotation and restarts Pods so init containers re-fetch).
**Trade-offs**: choose per application against timely consumption, graceful change, downtime avoidance (replicas + rolling updates), and monitoring/alerting. Secrets exempt from rotation must be **documented and marked**, with an incident-response path to rotate them fast. (Ch 13)

## Hash-Compare Debugging
**When to use**: verifying a Secret's value reached a container correctly, without leaking it.
**How**: mount the Secret into a minimal container and `echo $VALUE | md5sum`; compare against the source hash. Rule out consumption problems by testing both env-var and file mounts in a simple container before touching the real deployment.
**Trade-offs**: proves equality without ever printing the value. Printing sends it to stdout → the org's logging platform → mandatory rotation. (Ch 4)

---

# Anti-patterns and their canonical fixes

## Secret Zero
**Tell**: one master key unlocks everything, and that key itself has to live somewhere.
**Fix**: MFA on master-key access; **key splitting** (shards stored separately); **HSMs** for the key or its shards; **Shamir's Secret Sharing** requiring a quorum; continuous monitoring and access-log audits.
**Note**: largely non-existent on AWS/Azure/GCP thanks to cloud IAM; **persists on-prem and in private clouds**. API key + CPU ID + IP does **not** solve it — keys get stolen, IPs get spoofed. (Ch 7)

## Secret Access Ballooning
**Tell**: an LDAP group of 10 has become 400 with nested subgroups; external engineers are still admins.
**Fix**: strict group policies (**no subgroups inside admin groups**); scan memberships every few weeks; **RBAC**; **JIT access**; **step-up authentication**; and **track access growth as a metric** against a baseline — the early-warning signal. (Ch 7, Ch 13)

## Secret Valet Parking
**Tell**: CI fetches every secret it might need onto the host filesystem, and trusts the subsystem to delete them.
**Fix**: **dynamic, short-TTL Secrets** invalidated after use; a monitoring system that **verifies deletion**; fetch **per workload, when required** to shrink the blast radius; regular process audits. (Ch 7)

## Secret Sprawl
**Tell**: the same credential lives in source, a config file, Git, a wiki, and Dropbox.
**Fix**: **centralization** into one tightly-controlled store (Vault, CyberArk) with restricted access and detailed audit logs. Scan for leaked/hardcoded Secrets (e.g. Vault Radar). (Ch 7, Ch 14)

## Secret Island
**Tell**: Jenkins has its Secrets, AWS has its own, nothing shares policy; scaling adds teams and clouds until someone bypasses the process (**shadow IT**).
**Fix**: centralized management with consistent policy; **standardized protocols mandated across all islands**; integration tools and APIs so islands interoperate; regular audits and continuous monitoring; deliberate cross-team communication. (Ch 7)

## Double-Base64
**Tell**: a value that is already hex or base64-shaped is placed directly in `data:`; it applies cleanly but arrives in the container as binary.
**Fix**: use `stringData:` for plaintext, or base64-encode properly for `data:`. Detect with a hash comparison inside a test Pod. (Ch 4)

## Type-Trusting
**Tell**: assuming Kubernetes validates a typed Secret's contents.
**Fix**: only `dockercfg` is validated. Invalid TLS certs and malformed basic-auth Secrets apply successfully and fail later — an Ingress with a bad cert even **serves a Kubernetes-generated certificate** and looks healthy. Escalate to the **controller's** logs. (Ch 4)

## Authorization Sprawl (RBAC)
**Tell**: `resources: ["pods","secrets"]` with `verbs: ["get","watch","list","create","update","delete"]`.
**Fix**: fine-grained roles naming the minimum verbs; scheduled RBAC reviews; enforce compliance, monitor and revoke violations promptly, and audit policy changes for impact. (Ch 13)

## CI/CD Secret Leakage
**Tell**: relying on the pipeline's secret masking; production Secrets in test pipelines; unverified plugins.
**Fix**: OIDC/Workload Identity Federation instead of stored credentials; **dedicated test Secrets**; protected branches and segregated pipelines; fork workflows get no Secrets and public-fork runs require approval; trusted, hash-verified, patched tooling; least-privilege scoping. Remember masking is defeated by writing to a file and printing it — and job logs persist. (Ch 13)
