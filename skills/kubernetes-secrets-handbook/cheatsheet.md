# Cheatsheet — Kubernetes Secrets Handbook

Decision rules, thresholds, and tells. Keep beside you while working.

## Core decision rules

- **If the Secret is consumed by a Kubernetes component or add-on → keep it in etcd.** Offloading platform Secrets to an external vault means a vault partition collapses the cluster.
- **If the Secret is consumed by your application → offload it** to a cloud store or Vault, and mount it via CSI. Application Secrets are the only safe offload candidates.
- **If you have a KMS available → use the `kms` provider, not `aesgcm`.** Local AES keys sit base64 in a YAML file on the control-plane disk; a disk breach yields both ciphertext and key.
- **If you must use `aesgcm` → you have committed to automated key rotation.** Without it you're exposed to padding-oracle, birthday, and key-guessing attacks.
- **If you're changing encryption providers → new provider first, old one below, then rewrite every Secret.** Never remove the old provider before the rewrite; unrewritten Secrets become unreadable.
- **If a Secret can be a file, don't make it an env var** (CIS 5.4.1) — env vars leak via node memory and application logs.
- **If you're debugging a Secret → hash it, never print it.** `echo $V | md5sum`. Printing ships it to CloudWatch/Datadog/Cloud Monitoring and forces rotation.
- **If a resource reports healthy but behaves wrong → read the controller's logs, not the resource's.** An Ingress with a bad cert serves a Kubernetes-generated cert and looks fine.
- **If a value already looks like hex or base64 → use `stringData:`, not `data:`.** Otherwise it's decoded once too many and arrives as binary.
- **If access is temporary → grant JIT, never "add them to the admin group for now."** Temporary admins become permanent admins.
- **If a CI/CD job needs cloud access → use OIDC / Workload Identity Federation.** A stored cloud key is a silent breach waiting to happen.
- **If the pipeline needs something in a private network → run the pipeline in Kubernetes.** Don't expose Vault publicly to reach an external CI/CD provider.
- **If security is becoming too complicated → simplify it.** Complexity produces shadow IT, which is worse than the control you were adding.

## Choosing an encryption provider

| Have a KMS? | Regulated? | Choose |
|---|---|---|
| Yes | Yes | **`kms` (KMSv2)** + one KEK per cluster; `KMSv2KDF` if a per-encryption DEK is required |
| Yes | No | **`kms` (KMSv2)** |
| No | No | **`aesgcm`** + automated rotation + hardened disk/filesystem |
| No | — | Never `aescbc` for new work — "weak but fast" |
| — | — | `identity` only to revert to plaintext deliberately |

## Choosing an integration mechanism

- Need the Secret **before the app starts**? → **init container**
- Need it to **refresh without a restart**? → **sidecar** (or Vault Agent Injector)
- Need it **per node** (logging agent, etc.)? → **DaemonSet**
- Want a **uniform interface across many stores**, as files? → **Secrets Store CSI Driver** (accepts root-on-every-node)
- Want developers to write **a label, not a Secret**? → **mutating webhook**
- Want Secrets **in Git**? → **SealedSecrets** (+ encryption at rest, since it decrypts into a real Secret)
- Only need **certs and tokens**, and a mesh exists? → **service mesh** (Istio/Citadel)
- Need to **decouple legacy apps** from store specifics? → **broker**; if the app should never see the value, **secretless broker**

## Convert vs. direct fetch

| Choose **convert to native Secrets** when | Choose **direct fetch** when |
|---|---|
| You want caching and fewer external calls | You need the freshest version always |
| You must survive external-store downtime | You want one clean audit trail |
| Kubernetes-native tooling is the consumer | Latency is acceptable |
| *Cost*: redundancy + sync burden | *Cost*: hard dependency on the store |

**Alignment rule**: Pod-lifecycle mechanisms → direct fetch. API extensions → conversion.

## Thresholds and defaults

| Thing | Number |
|---|---|
| Production control-plane nodes | **≥ 3** (with dedicated worker nodes) |
| Vault/Conjur Raft cluster | **≥ 3**; tolerates `(n-1)/2` failures |
| AES encryption key | **32 bytes or more**, random, base64 |
| Vault KV-2 retained versions | **10** by default (configurable) |
| Conjur retained versions | **20** |
| Secret rotation interval | **30 / 60 / 90 days** (NIST SP 800-57) |
| KEKs per cluster | **1** — never share across clusters |
| Audit policy level for Secrets | **`Metadata`** (never `RequestResponse` without a secured sink) |
| Kubernetes version notes | KMSv1 **deprecated 1.28**; KMSv2 **GA 1.29**; auto-reload flag **1.26+**; SA token Secrets automatic **before 1.27** |

## The five CIS Kubernetes rules for Secrets

| Rule | Requirement |
|---|---|
| **1.2.29** | `--encryption-provider-config` is set |
| **1.2.30** | Provider is `aescbc`, `aesgcm`, or `kms` |
| **3.2.2** | Audit policy covers `Secret`, `ConfigMap`, `TokenReview` |
| **5.4.1** | **Prefer Secrets as files over environment variables** |
| **5.4.2** | Consider external secret storage |

## Cloud provider quick comparison

| | AWS | Azure | GCP |
|---|---|---|---|
| Store | Secrets Manager | **Key Vault (also the KMS)** | Secret Manager |
| KMS | AWS KMS | Key Vault | Cloud KMS |
| Identity binding | `eks.amazonaws.com/role-arn` | annotation **+ `use: "true"` label** | `iam.gke.io/gcp-service-account` |
| Scoping field | IAM `Condition` → `<oidc>:sub` | federated credential `subject` | — |
| CSI driver | Helm install | **Built-in add-on** | Helm (built-in on Autopilot); **unsupported by Google** |
| Cross-region | Opt-in `replica` block | **Automatic** | **Automatic** (restrict for residency) |
| Audit reads | CloudTrail `GetSecretValue` | `operationName: KeyGet` | `secretmanager.googleapis.com` filter |
| Audit decrypts | CloudTrail `Decrypt` | `operationName: KeyDecrypt` | Cloud KMS logs |
| Gotcha | Trust policy without `sub` = any SA | Needs **both** `oidc_issuer_enabled` and `workload_identity_enabled` | KMS role goes to **`container-engine-robot`, outside your project** |

## Tells and smells

| If you see… | You're probably in… |
|---|---|
| One master key protecting everything | **Secret zero** — split it (Shamir/HSM) |
| An admin group with subgroups and 400 members | **Secret access ballooning** — JIT + membership scans |
| CI fetching all Secrets to the host filesystem | **Secret valet parking** — dynamic short-TTL Secrets |
| The same credential in source, wiki, and Dropbox | **Secret sprawl** — centralize |
| Jenkins Secrets + AWS Secrets + no shared policy | **Secret island** — integrate via APIs |
| `verbs: ["*"]` on `["pods","secrets"]` | **Authorization sprawl** — name the minimum verbs |
| Pod stuck in `ContainerCreating` | Missing Secret mounted as a **volume** — `describe pod` → `FailedMount` |
| `CreateContainerConfigError` | Missing Secret referenced via **`envFrom`** |
| Ingress healthy, browser shows a Kubernetes cert | Invalid `kubernetes.io/tls` Secret — read the **controller** logs |
| MD5 mismatch between source and container | **Double-base64** — move to `stringData:` |
| "We backed up the cluster" | Ask whether **Secrets** were backed up separately |
| A robust backup strategy with unencrypted backups | The Case Study 2 breach — encrypt and access-control the backup |
| Vault unsealed and initialized on startup | **Dev mode** — not a deployment |
| `-key-shares=1 -key-threshold=1` | Shamir defeated — demo config in production |
| A ServiceAccount created but Vault auth fails | Missing **`system:auth-delegator`** ClusterRoleBinding |
| Test pipeline can delete production Secrets | Over-privileged pipeline — scope to the environment |

## The five exposures (Ch 1) — verify all five before declaring "secured"

1. **kube-apiserver** — RBAC
2. **etcd API** — TLS, network policy
3. **etcd database file** — encryption at rest + filesystem encryption
4. **Node filesystem** — OS hardening, disk encryption, non-root Pods
5. **Backups** — encrypted, access-controlled, immutable storage

*Bonus (Ch 7)*: **kubelet impersonation** — Kubernetes has **no need-to-know distribution**, so node root reads every Secret. Set `runAsNonRoot: true`, `allowPrivilegeEscalation: false`, `readOnlyRootFilesystem: true`.

## Secret lifecycle checklist (Ch 13)

**Provision** (traceable, standardized, typed) → **Store** (encrypted, RBAC, namespaced) → **Distribute** (TLS, trust chain, least privilege) → **Rotate** (monitor-reload / keyring / restart-as-reload) → **Decommission** (wired into service retirement) → **Revoke** (proactive on schedule, reactive on compromise).
