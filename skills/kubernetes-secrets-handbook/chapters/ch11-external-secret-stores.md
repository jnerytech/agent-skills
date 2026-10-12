# Chapter 11: Exploring External Secret Stores

## Core Idea
HashiCorp Vault and CyberArk Conjur reach Kubernetes without ever putting a credential in etcd, by inverting the trust: the **Kubernetes auth method** has Vault call back to the API server with a `TokenReview` to validate the Pod's ServiceAccount JWT — and any external store worth adopting must exhibit **seven qualities**: high availability, encryption of data, secure access, versioning, RBAC, Kubernetes integration, and auditing.

## Frameworks Introduced

- **The seven qualities of a secret manager** — the evaluation checklist for any external store.
  1. **High availability** — Raft consensus, multi-node clusters spanning data centers, failure-tolerant data distribution.
  2. **Encryption of data** — and *the encryption keys must themselves be encrypted* (Shamir's secret sharing, or a master key wrapping the DEKs).
  3. **Secure access** — proper authentication plus least privilege, expressed as **policies**.
  4. **Versioning** — prevents accidental deletion and makes rotation "robust and resilient."
  5. **RBAC**.
  6. **Integration with Kubernetes** — via ServiceAccounts, with **no sensitive keys in etcd** — not even the credentials needed to talk to the store.
  7. **Auditing** — a record of activity for breach identification, remediation, and debugging.

- **The Vault Kubernetes auth flow** — the eight-step handshake that eliminates stored credentials.
  1. A **service account is configured on Vault** with permission to call the Kubernetes API and execute `TokenReview` requests.
  2. A **Vault role** is created granting access to a secret and **bound to a Kubernetes service account** (`bound_service_account_names` / `bound_service_account_namespaces`).
  3. A Pod is created with that service account; the **Vault Injector** requests the secret using the SA's **JWT**.
  4. Vault issues a **`TokenReview`** request to the Kubernetes API to validate the JWT.
  5. Kubernetes validates the token.
  6. Vault checks whether the SA mapped to the token holds a role with access to the requested secret.
  7. Vault responds with the secret value.
  8. The Vault Injector injects it into the Pod.
  - Why it works: the Pod proves its identity with a token Kubernetes already issued; Vault verifies it *with Kubernetes*. Nothing Vault-specific is stored in the cluster.

- **Three ways to get Vault Secrets into a Pod** — pick by operational preference, not security (all three preserve the same properties):
  - **Vault Agent Injector** — a **mutating admission webhook** rewrites the Pod spec to add agent containers that render Secrets into a **shared memory volume**; a sidecar updates them when the Vault value changes.
  - **Secrets Store CSI Driver** with `provider: vault` — mounts Secrets as files, same as the cloud providers.
  - **Vault hosted on Kubernetes** — run the cluster itself in-cluster (StatefulSet + Raft).

- **Vault seal / unseal and Shamir's secret sharing** — the initialization model.
  - On `vault operator init`: a **root key** is generated, encrypted, and stored in the storage backend. Because it's encrypted it cannot be used — an **unseal key** is required to decrypt it.
  - The unseal key is **never distributed whole**. Shamir's algorithm splits it into **shares** spread across the cluster; reconstructing it requires reaching the **threshold**. "Supposing an attacker steals some shares. It will not be possible to reconstruct the unseal key if the shares stolen are less than the threshold."
  - Unsealing loads the decrypted root key into Vault's **memory**, which then decrypts the encryption key used for stored data.
  - **Sealing** (available during an intrusion) purges the root key from memory: Vault can no longer decrypt its storage and all operations stop.

- **Raft node tolerance formula**: `(n-1)/2` nodes may fail. Minimum viable cluster is **3** (tolerates 1); 5 tolerates 2. Writes go to the **leader**, which replicates to followers; a write attempted on a follower gets a **redirect to the leader address**.

## Key Concepts
- **Vault Agent Injector** — deployment + `vault-agent-injector-clusterrole`, whose only permissions are `get/list/watch/patch` on `mutatingwebhookconfigurations`. It intercepts Pod creation when Vault annotations are present.
- **`system:auth-delegator`** — the built-in ClusterRole allowing delegated authentication/authorization checks. The app's ServiceAccount needs it so Vault can `TokenReview` its JWT.
- **KV-2 vs KV-1** — KV-2 versions Secrets, retaining **10 versions by default** (configurable). Deleting only *marks* a version deleted (undeletable); **`destroy`** forces physical deletion. KV-1 has no versioning and lower storage cost.
- **Integrated storage (Raft)** vs **external storage** (Cassandra, DynamoDB, …). Integrated is HashiCorp-maintained and **collocated with the host** — no network hops, less operational complexity, no external-storage expertise needed. External storage inherits that system's backups/HA/auditing.
- **Performance standby nodes** — serve read requests, giving horizontal read scalability.
- **Vault policy** — a path + `capabilities` list, e.g. `path "secret/data/webapp/admin" { capabilities = ["read"] }`.
- **CyberArk Conjur architecture** — three components: **reverse Nginx proxy** (TLS termination), the **Conjur application** (Ruby), and a **PostgreSQL database**.
- **Conjur server keys** — a data key, a UI key, and SSL keys, generated in **plaintext** at initialization and then encrypted with a **master key**; once unlocked they live in the **Linux keyring and a memory-based filesystem**. The master key can be backed by **AWS KMS or an HSM**.
- **Conjur versioning** — keeps the **last 20 versions**.
- **Kubernetes Authenticator Client (Conjur)** — a **sidecar** that authenticates with the ServiceAccount, receives a **temporary token**, and uses it to fetch Secrets.

## Mental Models
- **You don't need an official binary to inject Secrets.** GCP Secret Manager has no injector — but with Workload Identity plus the GCP client libraries in an **init container**, you can mount Secrets locally yourself. "This recipe can be applied to any other form of storage. The key element to note is the usage of Workload Identity."
- **Trust flows backwards, and that's the point.** Rather than giving Kubernetes a Vault credential, Vault asks Kubernetes to vouch for the Pod. That's why nothing sensitive lands in etcd.
- **Even a breached Conjur database leaks names, not values.** `SELECT * FROM secrets` returns encrypted blobs: "the names of the Secrets would be leaked but not the actual value… since the decryption key is needed."
- **Dev mode is a demo, not a deployment.** Dev mode is unsealed, initialized, single-unseal-key, in-memory, and non-HA — every property production inverts.
- **Versioning is the rotation enabler.** Rotation is mandatory for Secrets; versioning is what makes rotation safe to attempt.

## Code Examples

Vault policy + role binding to a Kubernetes ServiceAccount — the least-privilege core:

```bash
# Store the secret
vault kv put secret/webapp/admin username='john.doe' password='strong-password'

# Read-only policy on exactly that path
vault policy write webapp_admin_r - <<EOF
path "secret/data/webapp/admin" {
  capabilities = ["read"]
}
EOF

# Bind the policy to a Kubernetes service account, with a TTL
vault write auth/kubernetes/role/webapp_admin_r \
  bound_service_account_names=simple-app \
  bound_service_account_namespaces=default \
  policies=webapp_admin_r \
  ttl=24h
```

Enabling the Kubernetes auth method on Vault:

```bash
TOKEN_REVIEW_JWT=$(kubectl get secret $VAULT_HELM_SECRET_NAME \
  --output='go-template={{ .data.token }}' | base64 --decode)
KUBE_CA_CERT=$(kubectl config view --raw --minify --flatten \
  -o jsonpath='{.clusters[].cluster.certificate-authority-data}' | base64 --decode)
KUBE_HOST=$(kubectl config view --raw --minify --flatten \
  -o jsonpath='{.clusters[].cluster.server}')

vault auth enable kubernetes
vault write auth/kubernetes/config \
  token_reviewer_jwt="$TOKEN_REVIEW_JWT" \
  kubernetes_host="$KUBE_HOST" \
  kubernetes_ca_cert="$KUBE_CA_CERT" \
  issuer="https://kubernetes.default.svc.cluster.local"
```

The `auth-delegator` binding the app's ServiceAccount needs (easy to forget — provisioning the SA alone is **not** sufficient):

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: role-tokenreview-binding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: system:auth-delegator
subjects:
- kind: ServiceAccount
  name: simple-app
  namespace: default
```

Three annotations are the entire Agent Injector interface:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: webapp
  annotations:
    vault.hashicorp.com/agent-inject: 'true'
    vault.hashicorp.com/role: 'webapp_admin_r'
    vault.hashicorp.com/agent-inject-secret-credentials.txt: 'secret/data/webapp/admin'
spec:
  serviceAccountName: simple-app
  containers:
  - name: app
    image: nginx
```
```bash
$ kubectl exec -it webapp -c app -- cat /vault/secrets/credentials.txt
data: map[password:strong-password username:john.doe]
metadata: map[created_time:2023-10-08T19:23:50Z destroyed:false version:1]
```
- **What it demonstrates**: the app manifest names *no* Vault credential. The webhook rewrote the Pod; the agent authenticated as the SA.

Vault via the CSI Driver — same Vault, file-mount delivery:

```yaml
apiVersion: secrets-store.csi.x-k8s.io/v1alpha1
kind: SecretProviderClass
metadata:
  name: vault-up-creds
spec:
  provider: vault
  parameters:
    roleName: 'devweb-app'
    objects: |
      - objectName: "username"
        secretPath: "secret/data/devwebapp/config"
        secretKey: "username"
      - objectName: "password"
        secretPath: "secret/data/devwebapp/config"
        secretKey: "password"
```

Conjur policy — declarative, role-and-resource shaped:

```yaml
- !policy
  id: ExamplePolicy
  body:
    - !host webApp
    - !variable secretVar
    - !permit
      role: !host webApp
      privileges: [read, execute]
      resource: !variable secretVar
```
- **What it demonstrates**: `!host` is a **non-human identity**. The policy grants `webApp` read+execute on `secretVar` and nothing else.

## Reference Tables

| | **Dev mode** | **Production mode** |
|---|---|---|
| High availability | ✗ | ✓ (Raft cluster) |
| Sealed state | **Unsealed by default** | Sealed until manually unsealed |
| Unseal key | Single | Shamir shares + threshold |
| Initialization | Automatic | **Manual** (`vault operator init`) |
| Data storage | **In memory** | Persistent backend |

| | **HashiCorp Vault** | **CyberArk Conjur** |
|---|---|---|
| Components | Vault binary + storage backend | Nginx reverse proxy + Ruby app + **PostgreSQL** |
| HA mechanism | Raft, leader + followers | Raft, **leader–follower**; follower promoted on master failure |
| Key protection | Root key encrypted; unseal key split by **Shamir** | Data/UI/SSL keys encrypted by a **master key** (AWS KMS or HSM) |
| Versioning | KV-2, **10 versions** default | **20 versions** |
| Kubernetes integration | Agent Injector (webhook) **or** CSI Driver | **Kubernetes Authenticator Client** sidecar |
| Policy form | HCL path + capabilities | YAML `!policy` / `!permit` |

| Vault integration method | Delivery | Mechanism |
|---|---|---|
| **Agent Injector** | Shared **memory volume** at `/vault/secrets/` | Mutating admission webhook rewrites Pod spec |
| **CSI Driver** | File mount at the volume path | `SecretProviderClass` with `provider: vault` |
| **Init container (DIY)** | Local file in the Pod | Workload Identity + provider client libraries |

| Raft cluster size | Failures tolerated `(n-1)/2` |
|---|---|
| 3 | 1 |
| 5 | 2 |
| 7 | 3 |

## Worked Example

**Standing up an HA Vault inside Kubernetes and proving replication.**

1. **Values file** — on minikube there is only one node, so affinity must be disabled:
   ```yaml
   server:
     affinity: ""          # single-node minikube; do NOT do this in production
     ha:
       enabled: true
       replicas: 3
       raft:
         enabled: true
   ```
   ```bash
   helm repo add hashicorp https://helm.releases.hashicorp.com
   helm install vault hashicorp/vault --values helm-vault-raft-values.yml
   ```
   Vault installs as a **StatefulSet**, 3 nodes by default.
2. **It comes up sealed and uninitialized** — this is correct, not a failure:
   ```
   $ kubectl logs -f vault-0
   [INFO] core: security barrier not initialized
   ```
3. **Initialize** (the example uses 1 share/1 threshold *for demonstration only* — production wants multiple shares held by different people):
   ```bash
   kubectl exec vault-0 -- vault operator init \
     -key-shares=1 -key-threshold=1 -format=json > cluster-keys.json
   ```
   The JSON carries `unseal_keys_b64`, `unseal_shares`, `unseal_threshold`, and `root_token`.
4. **Unseal the leader**, then **join** the followers, then **unseal each follower**:
   ```bash
   VAULT_UNSEAL_KEY=$(jq -r ".unseal_keys_b64[]" cluster-keys.json)
   kubectl exec vault-0 -- vault operator unseal $VAULT_UNSEAL_KEY
   kubectl exec -ti vault-1 -- vault operator raft join http://vault-0.vault-internal:8200
   kubectl exec -ti vault-2 -- vault operator raft join http://vault-0.vault-internal:8200
   kubectl exec vault-1 -- vault operator unseal $VAULT_UNSEAL_KEY
   kubectl exec vault-2 -- vault operator unseal $VAULT_UNSEAL_KEY
   ```
   Joining triggers **leader election**.
5. **Write through the leader**:
   ```bash
   kubectl port-forward vault-0 8200:8200
   export VAULT_ADDR=http://0.0.0.0:8200
   vault login $(jq -r ".root_token" cluster-keys.json)
   vault secrets enable -path=secret kv-v2
   vault kv put secret/webapp/config username="static-user" password="static-password"
   ```
6. **Prove replication by reading from a different node** — port-forward to `vault-1` instead and read:
   ```bash
   kubectl port-forward vault-1 8200:8200
   $ vault kv get secret/webapp/config
   password    static-password
   username    static-user
   ```
   The data reached the follower via Raft. That single read is the whole HA demonstration.

**Debugging tip from the same walkthrough**: the Kubernetes auth flow has many moving parts, so enable Vault's own audit device early —
```bash
vault audit enable file file_path=/tmp/vault_audit.log
docker exec -it vault_node_1 tail -f /tmp/vault_audit.log
```

## Anti-patterns
- **Running Vault in dev mode anywhere real** — unsealed, in-memory, single key, no HA. "This is not a secure way to run Vault."
- **`-key-shares=1 -key-threshold=1` in production** — defeats the entire point of Shamir's secret sharing.
- **Creating the app ServiceAccount and stopping there** — "Provisioning the service account alone is not sufficient"; the `system:auth-delegator` ClusterRoleBinding is required for `TokenReview`.
- **A two-node Raft cluster** — `(n-1)/2` = 0; the minimum is 3.
- **Attempting writes against a follower** — Vault redirects, but plan for leader-directed writes.
- **Assuming `vault kv delete` removed the data** — it marks the version deleted and undeletable; use **`vault kv destroy`** for physical removal.
- **Ignoring the storage cost of KV-2** — 10 retained versions by default; tune it or use KV-1 where history isn't needed.
- **Leaving `cluster-keys.json` on disk** — it contains every unseal share *and* the root token.
- **Disabling affinity outside a single-node lab** — the minikube workaround puts all replicas on one node, eliminating the fault tolerance you configured.

## Key Takeaways
1. Evaluate any external store against the **seven qualities**; each of Vault and Conjur satisfies all seven by different means.
2. The **Kubernetes auth method** inverts trust — Vault calls `TokenReview` against the API server — so **no Vault credential ever lands in etcd**.
3. Three Vault delivery methods: **Agent Injector** (webhook → memory volume), **CSI Driver** (file mount), and self-built **init container** with Workload Identity.
4. The Agent Injector is a **mutating admission webhook** driven by three Pod annotations.
5. `system:auth-delegator` on the app's ServiceAccount is a mandatory, easily-missed step.
6. **Seal/unseal**: the root key is encrypted at rest and only exists decrypted in memory; Shamir shares + threshold mean partial theft is useless; sealing during an intrusion purges the key and halts Vault.
7. Raft tolerates `(n-1)/2` failures — **3 nodes minimum**; writes go to the leader, followers redirect.
8. **KV-2** versions Secrets (10 by default); `delete` is reversible, **`destroy`** is not.
9. Prefer **integrated storage** unless you specifically want an external backend's features — fewer network hops, less operational complexity.
10. Conjur stores encrypted values in **PostgreSQL**, so a database breach leaks **secret names, not values**; its master key can be held in **AWS KMS or an HSM**.

## Connects To
- **Ch 1**: platform vs. application Secrets — the warning about offloading *platform* Secrets applies directly to Vault.
- **Ch 2**: creating a long-lived `kubernetes.io/service-account-token` Secret for the `vault` SA is exactly the Ch 2 pattern.
- **Ch 3**: Vault as the KMS behind Trousseau; `kv-v2` as the KEK/DEK analogue.
- **Ch 6**: `vault operator raft snapshot`, seal/unseal, and Vault Enterprise auto-snapshots.
- **Ch 7**: **dynamic Secrets** solve *secret valet parking*; centralization solves *sprawl*; Shamir addresses *secret zero*.
- **Ch 8/9/10**: the cloud stores are the other five providers on the same list.
- **Ch 12**: init containers, sidecars, CSI drivers, operators, and sealed Secrets as a full taxonomy.
- **Shamir's Secret Sharing, Raft consensus, mutating admission webhooks, HSM** — external concepts this chapter applies.
