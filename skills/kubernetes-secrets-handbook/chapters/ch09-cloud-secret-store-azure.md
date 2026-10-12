# Chapter 9: Exploring Cloud Secret Store on Azure

## Core Idea
Azure collapses the AWS two-service split into **one service** — Azure Key Vault is *both* the secret store *and* the KMS — and binds it to AKS with **Workload Identity**: a user-assigned managed identity plus a **federated identity credential** whose `subject` is `system:serviceaccount:<ns>:<sa>`, letting a Pod's ServiceAccount impersonate the identity through the cluster's OIDC issuer.

## Frameworks Introduced

- **Workload Identity on AKS** — the credential-free identity bridge (Azure's IRSA).
  - When to use: any Kubernetes workload that must reach an Azure resource.
  - How:
    1. Create the cluster with **`oidc_issuer_enabled = true`** *and* **`workload_identity_enabled = true`**. (Both are required; neither works alone.)
    2. Create an `azurerm_user_assigned_identity` — a **managed identity**, not a service principal with credentials.
    3. `azurerm_role_assignment` scoped to the Key Vault, e.g. role `Key Vault Reader`.
    4. Create an `azurerm_federated_identity_credential` with `issuer = <cluster oidc_issuer_url>`, `audience = ["api://AzureADTokenExchange"]`, and **`subject = "system:serviceaccount:default:service-token-reader"`**.
    5. Annotate the ServiceAccount with `azure.workload.identity/client-id` **and** label it `azure.workload.identity/use: "true"`.
  - Why it works: "The federated credential… establishes a trust relationship with the identity provider of our AKS cluster and Active Directory. We allow the `service-token-reader` service account to impersonate `ksm-reader-identity`." The Pod requests a token from Azure AD and uses it against the resource — no stored credential.

- **Azure RBAC over access policies** — the authorization decision.
  - When to use: always, for new Key Vaults.
  - How: set `enable_rbac_authorization = true` on the vault, then grant with **role assignments** against a **security principal** (user, group, or computer account).
  - Why: access policies are "the legacy way"; Azure RBAC is "the recommended way" and is what the rest of the chapter builds on.

- **Diagnostic settings as the audit pipeline** — Azure's audit is opt-in and route-able.
  - When to use: the moment a Key Vault exists.
  - How: `azurerm_monitor_diagnostic_setting` targeting the vault, with `log { category = "AuditEvent" }`, streamed to one of three sinks: **Azure storage account** (default), **Log Analytics workspace**, or **Azure Event Hub**.
  - Result: a container named **`insights-logs-auditevent`** holding JSON records.

## Key Concepts
- **Azure Key Vault** — "a versatile service": secret storage, cryptographic key storage, *and* encryption/decryption operations. This is why Azure needs no separate KMS service.
- **Security principal** — an entity with an Azure identity: user account, group account, or computer account.
- **Access policy** — the legacy permission model on Key Vault; superseded by Azure RBAC.
- **Managed identity / Workload Identity** — "machine identities representing software workloads that require identities to interact with Azure resources," avoiding manually attached credentials.
- **Federated identity credential** — the trust link between the AKS OIDC issuer and Azure AD, scoped by `subject`.
- **`SecretProviderClass`** — a Kubernetes **custom resource** (CRD — an extension of the Kubernetes API) carrying driver config and provider-specific parameters to the CSI driver.
- **`soft_delete_retention_days`** — how long a deleted vault/secret remains recoverable.
- **`enforce_private_link_endpoint_network_policies`** — subnet setting letting workloads reach Azure components over the **internal** network.
- **`key_management_service` block** — the AKS setting that makes a Key Vault key the etcd encryption KEK.
- **`KeyGet` / `KeyDecrypt`** — the audit `operationName` values for a secret/key read and for etcd decryption respectively.

## Mental Models
- **Key Vault is Secrets Manager *and* KMS in one resource.** On AWS you provision two services; on Azure you provision one vault and use it for both roles. That also means one blast radius — scope RBAC carefully.
- **HA and DR are automatic here, not configured.** Key Vault replicates within its region **and** to a secondary region; on regional failure "requests… will be routed to the secondary region… automatically; there is no need to provision any extra Azure Key Vault resources." Contrast with AWS, where cross-region replication is an explicit `replica` block (Ch 8).
- **AKS ships the CSI driver as an add-on.** Unlike EKS, no Helm install: `--enable-addons azure-keyvault-secrets-provider` (or the Terraform equivalent) puts `aks-secrets-store-csi-driver` and `aks-secrets-store-provider-azure` in `kube-system` for you.
- **Resource groups are the blast-radius boundary.** "It is crucial to provision the resources for this chapter under one resource group" — logical separation from everything else in the subscription.
- **Two identities appear in the audit log, and they mean different things.** `xms_mirid` pointing at `userAssignedIdentities/keyvault-reader` = a workload read a secret. `xms_az_rid` pointing at `managedClusters/ksm-aks` = the cluster itself decrypted etcd.

## Code Examples

The AKS cluster with **both** identity switches plus the KMS binding:

```hcl
resource "azurerm_kubernetes_cluster" "ksm_aks" {
  name                              = "ksm-aks"
  dns_prefix                        = "private-aks-cluster"
  private_cluster_enabled           = false
  oidc_issuer_enabled               = true    # ← required for Workload Identity
  workload_identity_enabled         = true    # ← required for Workload Identity
  role_based_access_control_enabled = true

  key_management_service {                     # ← etcd encryption via Key Vault
    key_vault_key_id         = azurerm_key_vault_key.ksm_encryption_key.id
    key_vault_network_access = "Public"
  }

  default_node_pool {
    name           = "default"
    node_count     = 1
    vm_size        = "Standard_A2_v2"
    vnet_subnet_id = azurerm_subnet.ksm_subnet.id   # nodes on the private subnet
  }
}
```

The federated identity credential — **`subject` is the security control**:

```hcl
resource "azurerm_federated_identity_credential" "cred" {
  name      = "ksm-reader-identity"
  issuer    = azurerm_kubernetes_cluster.ksm_aks.oidc_issuer_url
  audience  = ["api://AzureADTokenExchange"]
  parent_id = azurerm_user_assigned_identity.keyvault_reader.id
  subject   = "system:serviceaccount:default:service-token-reader"
}
```

The `SecretProviderClass` — Azure's version can fetch **both secrets and keys**:

```yaml
apiVersion: secrets-store.csi.x-k8s.io/v1
kind: SecretProviderClass
metadata:
  name: keyvault-secrets
spec:
  provider: azure
  parameters:
    usePodIdentity: "false"        # Workload Identity, not the deprecated Pod Identity
    clientID: <managed identity client id>
    keyvaultName: <vault name>
    tenantId: <tenant id>
    objects: |
      array:
        - |
          objectName: secret1
          objectType: secret
        - |
          objectName: key1
          objectType: key
```

The ServiceAccount — note it needs **both** the annotation and the label:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: service-token-reader
  namespace: default
  annotations:
    azure.workload.identity/client-id: <identity with Key Vault access>
  labels:
    azure.workload.identity/use: "true"
```

A Key Vault key with an **automatic rotation policy** — the piece AWS handles with `enable_key_rotation`:

```hcl
resource "azurerm_key_vault_key" "ksm_encryption_key" {
  name         = "ksm-encryption-key"
  key_vault_id = azurerm_key_vault.ksm_key_vault.id
  key_type     = "RSA"
  key_size     = 2048
  key_opts     = ["decrypt","encrypt","sign","unwrapKey","verify","wrapKey"]

  rotation_policy {
    automatic { time_before_expiry = "P30D" }
    expire_after         = "P90D"
    notify_before_expiry = "P29D"
  }
}
```

CLI shortcut for the whole cluster setup:

```bash
az aks create -n ksm-aks -g ksm-resource-group \
  --enable-addons azure-keyvault-secrets-provider \
  --enable-oidc-issuer --enable-workload-identity

az aks get-credentials --name ksm-aks --resource-group ksm-resource-group \
  --subscription $subscription --admin
```

## Reference Tables

| Concern | AWS (Ch 8) | Azure (this chapter) |
|---|---|---|
| Secret store | Secrets Manager | **Azure Key Vault** |
| KMS | AWS KMS (separate service) | **Azure Key Vault** (same service) |
| Workload identity | IRSA (IAM role + OIDC) | **Workload Identity** (managed identity + federated credential) |
| Trust scoping field | IAM `Condition` → `<oidc>:sub` | `azurerm_federated_identity_credential.subject` |
| CSI driver install | Helm (not an add-on) | **Built-in add-on** (`azure-keyvault-secrets-provider`) |
| Cross-region DR | Explicit `replica` block | **Automatic** to a secondary region |
| Audit sink | CloudTrail | Diagnostic settings → storage / Log Analytics / Event Hub |
| Monitoring | CloudWatch | Azure Monitor |

| Audit `operationName` | Meaning | Identity claim to check |
|---|---|---|
| `KeyGet` | A workload read a key/secret from the vault | `xms_mirid` → `userAssignedIdentities/keyvault-reader` |
| `KeyDecrypt` | AKS decrypted an etcd Secret | `xms_az_rid` → `managedClusters/ksm-aks` |

| Key Vault setting | Purpose |
|---|---|
| `enable_rbac_authorization = true` | Use Azure RBAC instead of legacy access policies |
| `soft_delete_retention_days` | Recovery window after deletion |
| `sku_name` | `standard` vs `premium` (HSM-backed) |

## Worked Example

**Provisioning the whole AKS + Key Vault path, and then proving it from the audit log.**

1. **Terraform state** in an `azurerm` backend (resource group + storage account + container `tfstate`), never local.
2. **One resource group** (`ksm-resource-group`) for everything, plus a **storage account** (`ksmlogs`) that will receive the diagnostic logs.
3. **Network**: virtual network `10.1.0.0/16`, private subnet `10.1.0.0/24` with `enforce_private_link_endpoint_network_policies = true` so workloads reach Azure services internally.
4. **Cluster**: public control plane, nodes on the private subnet, OIDC issuer + Workload Identity + RBAC all enabled. (A fully private cluster is available via `private_cluster_enabled` plus a bastion host — the repo has `ch09/bastion.tf`.)
5. **Vault**: `enable_rbac_authorization = true`, `soft_delete_retention_days = 7`.
6. **Identity chain**: user-assigned identity `keyvault-reader` → role assignment `Key Vault Reader` scoped to the vault → federated credential with `subject = system:serviceaccount:default:service-token-reader`.
7. **Verify the driver is already there** (no install step on AKS):
   ```bash
   $ kubectl get pods -n kube-system \
       -l 'app in (secrets-store-csi-driver,secrets-store-provider-azure)'
   aks-secrets-store-csi-driver-t6n7h       3/3   Running
   aks-secrets-store-provider-azure-htmqk   1/1   Running
   ```
8. **Wire it**: `SecretProviderClass` → labelled+annotated `ServiceAccount` → Pod with the CSI volume at `/mnt/secrets-store`.
9. **Turn on auditing** with `azurerm_monitor_diagnostic_setting` (`category = "AuditEvent"`) targeting the storage account.
10. **Read the evidence** in `insights-logs-auditevent`:
    ```json
    {"time":"2023-08-30T09:07:19Z","category":"AuditEvent",
     "operationName":"KeyGet","resultType":"Success",
     "identity":{"claim":{"xms_mirid":"/subscriptions/.../userAssignedIdentities/keyvault-reader"}},
     "properties":{"id":"https://ksm-key-vault.vault.azure.net/keys/key1",
                   "isRbacAuthorized":true}}
    ```
    `isRbacAuthorized: true` confirms the RBAC path (not a legacy access policy) actually granted it, and the identity is exactly the one bound to the ServiceAccount.
11. **Confirm etcd encryption** separately — the `key_management_service` block produces `KeyDecrypt` events attributed to the *cluster*:
    ```json
    {"operationName":"KeyDecrypt","resultType":"Success",
     "identity":{"claim":{"xms_az_rid":"/subscriptions/.../managedClusters/ksm-aks"}},
     "properties":{"algorithm":"RSA-OAEP-256",
                   "clientInfo":"k8s-kms-keyvault/v0.5.0 (linux/amd64)",
                   "tlsVersion":"TLS1_2"}}
    ```
    The `k8s-kms-keyvault` client string is the KMS plugin (Ch 3) doing its job.

## Anti-patterns
- **Enabling only one of `oidc_issuer_enabled` / `workload_identity_enabled`** — Workload Identity needs both.
- **Omitting the `azure.workload.identity/use: "true"` label** — the annotation alone doesn't activate the webhook.
- **Creating the Key Vault with access policies instead of `enable_rbac_authorization = true`** — the legacy model, explicitly not recommended.
- **A federated credential with a loose `subject`** — same failure as an unscoped IRSA trust policy: any ServiceAccount could impersonate the identity.
- **Relying on Diagnostic Settings storage retention** — the authors flag it as **being deprecated**; configure retention through **Azure Storage Lifecycle Management** instead.
- **Local Terraform state** — use the `azurerm` backend.
- **Scattering resources across resource groups** — loses the logical isolation boundary.
- **Creating a KMS key with no `rotation_policy`** — rotation is declarative here; use it.

## Key Takeaways
1. **One service, two jobs**: Azure Key Vault is the secret store *and* the KMS for etcd encryption.
2. Workload Identity requires **`oidc_issuer_enabled` + `workload_identity_enabled`**, a user-assigned managed identity, a **role assignment**, and a **federated credential whose `subject` is the exact ServiceAccount**.
3. The ServiceAccount needs **both** the `client-id` annotation and the `use: "true"` label.
4. Use **Azure RBAC**, not access policies; verify with `isRbacAuthorized: true` in the audit log.
5. AKS ships the CSI driver as an **add-on** — no Helm install, unlike EKS.
6. Key Vault is **regionally HA and cross-region DR by default** — no replica configuration needed.
7. Auditing is opt-in via **Diagnostic settings**; route to storage, Log Analytics, or Event Hub. Manage retention with Storage Lifecycle Management, not the deprecated diagnostic retention.
8. Read `operationName` to tell the two flows apart: **`KeyGet`** = workload read; **`KeyDecrypt`** = etcd decryption by the cluster.
9. Attach a **`rotation_policy`** to the KMS key (e.g. expire after 90 days, rotate 30 days before expiry).

## Connects To
- **Ch 3**: `key_management_service` is the `kms` provider; `k8s-kms-keyvault` in the audit log is the KMS plugin.
- **Ch 5**: Secrets arrive as files (CIS 5.4.1) from an external store (CIS 5.4.2).
- **Ch 6**: automatic secondary-region replication is Azure's DR answer; `soft_delete_retention_days` is the recovery window.
- **Ch 7**: Azure AD identity is why secret zero largely disappears; the `subject` scoping prevents access ballooning.
- **Ch 8**: same two-lever pattern, different topology — compare the table above.
- **Ch 10**: GCP Secret Manager + Cloud KMS complete the trio.
- **Ch 12**: CSI driver as one integration approach among several.
