# Chapter 10: Exploring Cloud Secret Store on GCP

## Core Idea
GCP splits the roles like AWS (**Secret Manager** for storage, **Cloud KMS** for encryption) but binds them to GKE through **Workload Identity** — a Kubernetes ServiceAccount annotated with `iam.gke.io/gcp-service-account` so it acts on behalf of a GCP service account — with two GCP-specific gotchas: Secret Manager is **multi-region by default** (you constrain it for data residency, not to enable DR), and the GKE control plane's service account **lives outside your project**, so the KMS IAM binding must target `container-engine-robot`.

## Frameworks Introduced

- **The three-tier IAM scope model** — GCP's permission granularity, coarsest to finest.
  1. **Organizational level** — manage an organization's resources.
  2. **Project-wide** — permissions targeting specific resource *types* across a GCP project.
  3. **Resource-based** (most granular) — permissions on one specific resource.
  - Identities are **users, Google Groups, or service accounts**. Grant at the finest tier that works — here, `google_secret_manager_secret_iam_binding` on a single secret.

- **Workload Identity on GKE** — map a Kubernetes SA onto a GCP SA.
  - When to use: any Pod needing a Google Cloud API.
  - How:
    1. Enable it on the cluster: `workload_identity_config { workload_pool = "<project>.svc.id.goog" }`.
    2. Create a GCP service account (`google_service_account`).
    3. Grant it the minimum role — `roles/secretmanager.secretAccessor` — **bound to the specific secret**.
    4. Create the Kubernetes ServiceAccount and **annotate** it: `iam.gke.io/gcp-service-account=<gsa-email>`.
    5. Set `serviceAccountName` on the Pod.
  - Why it works: "the service account of Kubernetes will act on behalf of the service account we created previously." No key file in the cluster.

- **Two audit queries, two systems** — GCP separates *application* logs from *audit* logs, and reading audit logs requires the **Private Logs Viewer** permission.
  - Kubernetes-side Secret operations:
    ```
    protoPayload.methodName="io.k8s.core.v1.secrets.create"
    protoPayload.@type="type.googleapis.com/google.cloud.audit.AuditLog"
    resource.type="k8s_cluster"
    ```
  - Secret Manager–side access:
    ```
    resource.type="audited_resource" AND
    resource.labels.service="secretmanager.googleapis.com"
    ```

- **GKE security posture dashboard** — GCP's built-in equivalent of the Ch 5 tool chain, in two parts:
  - **Kubernetes security posture** — scans clusters and workloads, surfaces discovered vulnerabilities with the affected clusters/workloads, and gives "opinionated, actionable recommendations."
  - **Workload vulnerability scanning** — scans container images *and* the **programming-language packages** inside them.
  - Findings integrate with Cloud Logging/Monitoring, so alerts and automated response are available.

## Key Concepts
- **GCP Secret Manager** — a *service*, not a provisioned resource: "to use Secret Manager on GCP, we do not need to create a resource. Instead, we create the Secrets that will be hosted on Secret Manager."
- **Secret vs. secret version** — `google_secret_manager_secret` holds the container and replication policy; `google_secret_manager_secret_version` holds the actual data.
- **`user_managed { replicas { location } }`** — pin which regions hold the secret. Used to *restrict* for **data residency**, since the default is already multi-region.
- **`roles/secretmanager.secretAccessor`** — the read role for a secret.
- **`iam.gke.io/gcp-service-account`** — the annotation binding a KSA to a GSA.
- **`container-engine-robot`** — the Google-managed service account of the GKE control plane, of the form `service-<project-number>@container-engine-robot.iam.gserviceaccount.com`. It lives **outside your project** but must hold the KMS encrypt/decrypt role.
- **`roles/cloudkms.cryptoKeyEncrypterDecrypter`** — the KMS role needed for etcd encryption.
- **`database_encryption { state = "ENCRYPTED" }`** — the GKE setting that switches etcd Secret encryption to your **customer-managed key (CMK)**.
- **Key ring** — Cloud KMS groups crypto keys into a regional `google_kms_key_ring`.
- **GKE Autopilot** — the managed GKE variant; **the CSI plugin is installed by default** there, unlike standard GKE.

## Mental Models
- **On GCP, network is global and subnets are regional.** `google_compute_network` takes no region; `google_compute_subnetwork` does. This is the inverse of the AWS mental model.
- **Secret Manager is globally accessible and replicated by default.** "The Secrets can be accessed globally from different regions… replicated in multiple regions **unless specified otherwise**." You specify regions to *comply*, not to *protect*.
- **GKE encrypts at rest already — CMK is about control, not about turning encryption on.** "By default, GKE will encrypt data at rest, and the encryption is managed by GCP." Supplying a CMK moves the key into your project and your audit trail.
- **The control plane is not yours.** GKE's master runs on Google's side with Google's service account. Any IAM grant the *control plane* needs must be made to an external principal — a real trap when writing least-privilege policy.
- **Delete the default node pool.** GKE forces an initial node pool at creation; `remove_default_node_pool = true` plus a purpose-built `google_container_node_pool` keeps one pool running and the cost down.

## Code Examples

Secret + version + a resource-scoped IAM binding — the whole least-privilege chain:

```hcl
resource "google_secret_manager_secret" "my_secret" {
  secret_id = "my-secret"
  user_managed {
    replicas { location = var.location }
    replicas { location = "us-east1" }     # explicit residency control
  }
}

resource "google_secret_manager_secret_version" "my_secret_version" {
  secret      = google_secret_manager_secret.my_secret.id
  secret_data = "secret-data"
}

resource "google_service_account" "my_service_account" {
  account_id = "read-secrets-service-account"
}

resource "google_secret_manager_secret_iam_binding" "my_secret_reader" {
  role      = "roles/secretmanager.secretAccessor"
  secret_id = google_secret_manager_secret.my_secret.id   # ← bound to ONE secret
  members   = ["serviceAccount:${google_service_account.my_service_account.email}"]
}
```

GKE cluster with Workload Identity, a discarded default node pool, and CMK etcd encryption:

```hcl
resource "google_container_cluster" "gke_cluster" {
  name       = "secrets-cluster"
  location   = var.region
  network    = google_compute_network.vpc.name
  subnetwork = google_compute_subnetwork.subnet.name

  remove_default_node_pool = true      # cost control
  initial_node_count       = 1

  workload_identity_config {
    workload_pool = "kube-secrets-book.svc.id.goog"
  }

  database_encryption {
    key_name = google_kms_crypto_key.ksm_secret_key.id
    state    = "ENCRYPTED"
  }
}
```

**The out-of-project IAM binding** — the chapter's sharpest gotcha:

```hcl
data "google_project" "project" {}

resource "google_kms_crypto_key_iam_binding" "ksm_secret_key_encdec" {
  crypto_key_id = google_kms_crypto_key.ksm_secret_key.id
  role          = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
  members = [
    "serviceAccount:service-${data.google_project.project.number}@container-engine-robot.iam.gserviceaccount.com"
  ]
}
```
- **What it demonstrates**: "on GKE, the master is managed by GCP, and the service account that the master nodes use is **not** a service account residing on our Google Cloud project, thus we need to assign permission to a service account that is not part of our project."

CSI plugin install (standard GKE — **not** needed on Autopilot):

```bash
helm repo add secrets-store-csi-driver \
  https://kubernetes-sigs.github.io/secrets-store-csi-driver/charts
helm install csi-secrets-store secrets-store-csi-driver/secrets-store-csi-driver \
  --namespace kube-system
kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/\
secrets-store-csi-driver-provider-gcp/main/deploy/provider-gcp-plugin.yaml
```

Binding the Kubernetes SA to the GCP SA:

```bash
kubectl create serviceaccount read-secret --namespace=default
kubectl annotate serviceaccount read-secret --namespace=default \
  iam.gke.io/gcp-service-account=read-secrets-service-account@test-gcp-project.iam.gserviceaccount.com
```

`SecretProviderClass` — GCP addresses the secret by **full resource name including the version**:

```yaml
apiVersion: secrets-store.csi.x-k8s.io/v1
kind: SecretProviderClass
metadata:
  name: app-secrets
spec:
  provider: gcp
  parameters:
    secrets: |
      - resourceName: "projects/project-i/secrets/my-secret/versions/latest"
        path: "good1.txt"
```
- **What it demonstrates**: `path` names the file the secret lands in inside the mount — the secret arrives as a **file**, satisfying CIS 5.4.1.

## Reference Tables

| Concern | AWS (Ch 8) | Azure (Ch 9) | **GCP (this chapter)** |
|---|---|---|---|
| Secret store | Secrets Manager | Key Vault | **Secret Manager** |
| KMS | AWS KMS | Key Vault (same service) | **Cloud KMS** (key ring + crypto key) |
| Workload identity | IRSA (IAM role + OIDC) | Workload Identity (federated credential) | **Workload Identity** (`workload_pool`) |
| Binding mechanism | SA annotation `eks.amazonaws.com/role-arn` | SA annotation + label | SA annotation `iam.gke.io/gcp-service-account` |
| CSI driver install | Helm | **Built-in add-on** | Helm (standard GKE) / **built-in on Autopilot** |
| Officially supported? | Yes (AWS repo) | Yes | **"not officially supported by Google"** |
| Multi-region | Opt-in (`replica`) | Automatic secondary region | **Automatic multi-region; opt *out* for residency** |
| Audit | CloudTrail | Diagnostic settings | Cloud Logging (needs **Private Logs Viewer**) |
| Posture tooling | — | — | **GKE security posture dashboard** |

| GCP resource | Scope |
|---|---|
| `google_compute_network` (VPC) | **Global** — no region |
| `google_compute_subnetwork` | **Regional** |
| `google_kms_key_ring` | Regional |
| Secret Manager secret | Global, multi-region replicated |

| Query target | Log filter |
|---|---|
| Kubernetes Secret create | `protoPayload.methodName="io.k8s.core.v1.secrets.create"` + `resource.type="k8s_cluster"` |
| Secret Manager access | `resource.type="audited_resource" AND resource.labels.service="secretmanager.googleapis.com"` |

## Worked Example

**GKE Pod reads a Secret Manager secret, with both audit trails proving it.**

1. **Terraform provider** points at the credentials file, project, and region. Omit `credentials` and Terraform falls back to the identity from `gcloud auth login` — convenient locally, wrong for CI; specify a service account file there.
2. **Network**: `google_compute_network` with `auto_create_subnetworks = "false"` (global), plus one regional `google_compute_subnetwork` at `10.10.0.0/24` for the nodes.
3. **Secret**: create the secret with two explicit replica locations, then a version carrying the data. Create a GCP service account and bind `roles/secretmanager.secretAccessor` **to that one secret** — not to the project.
4. **Cluster**: `google_container_cluster` with `workload_identity_config`, `remove_default_node_pool = true`, `initial_node_count = 1`. Then a real `google_container_node_pool` on the STABLE release channel, `n1-standard-1`, `disk_size_gb = 10`, `disable-legacy-endpoints = "true"`, and OAuth scopes limited to `logging.write` and `monitoring`. Terraform deletes the throwaway pool afterwards.
5. **Connect**: `gcloud container clusters get-credentials secrets-cluster --region us-central1 --project kube-secrets-book`, then `kubectl get node`.
6. **Install** the CSI driver via Helm plus the GCP provider plugin manifest.
7. **Bind** the Kubernetes SA to the GCP SA with `kubectl annotate`.
8. **Apply** the `SecretProviderClass` and a Pod that mounts it read-only at `/var/secrets`.
9. **Verify both audit paths.** Create a probe secret — `kubectl create secret generic empty-secret` — and query Cloud Logging with the `k8s_cluster` filter to see the Kubernetes-side event. Then query the `secretmanager.googleapis.com` filter to see the Secret Manager–side reads performed by the CSI provider.
10. **Add CMK etcd encryption**: create the key ring and crypto key, grant `cryptoKeyEncrypterDecrypter` to `service-<project-number>@container-engine-robot.iam.gserviceaccount.com`, then set `database_encryption { state = "ENCRYPTED" }` on the cluster. Now GKE encrypts etcd Secrets with *your* key, and every use shows up in your Cloud KMS audit log.

## Anti-patterns
- **Granting `secretAccessor` at the project level** — bind it to the individual secret; GCP's resource-tier IAM exists for exactly this.
- **Granting the KMS role to a service account inside your project** — the GKE control plane uses `container-engine-robot`, outside your project. The binding silently fails to help otherwise.
- **Leaving the default node pool running** — you pay for two pools; set `remove_default_node_pool = true`.
- **Assuming a region must be set on the VPC** — it's a global resource; only the subnetwork is regional.
- **Assuming you must configure replication for DR** — Secret Manager is multi-region by default; explicit `replicas` are for **data residency compliance**.
- **Assuming GKE at-rest encryption means you control the key** — the default key is Google-managed; a CMK is a separate, deliberate step.
- **Expecting Google support for the CSI plugin** — "the CSI plugin is not officially supported by Google."
- **Trying to read audit logs without Private Logs Viewer** — audit logs are permission-gated separately from application logs.
- **Installing the CSI plugin on Autopilot** — it's already there.

## Key Takeaways
1. GCP splits storage (**Secret Manager**) from encryption (**Cloud KMS**), like AWS and unlike Azure.
2. Secret Manager is a **service, not a resource** — you create secrets, never the manager.
3. Secrets are **globally accessible and multi-region replicated by default**; specify `replicas` to *restrict* for data residency.
4. Workload Identity = `workload_pool` on the cluster + `iam.gke.io/gcp-service-account` annotation on the KSA. No key files.
5. Bind IAM at the **resource tier** (`secretAccessor` on one secret), not project-wide.
6. **The GKE control plane's service account is outside your project** — grant `cryptoKeyEncrypterDecrypter` to `container-engine-robot`.
7. GKE encrypts etcd by default with a Google-managed key; `database_encryption` with your key ring switches it to a **CMK**.
8. Two separate audit queries: `resource.type="k8s_cluster"` for Kubernetes, `secretmanager.googleapis.com` for the store. **Private Logs Viewer** is required.
9. The CSI plugin needs manual install on standard GKE (and is **not officially supported by Google**); Autopilot ships it.
10. Use the **GKE security posture dashboard** for cluster posture and image/package vulnerability scanning, wired into Logging and Monitoring for alerts.

## Connects To
- **Ch 3**: `database_encryption` is the `kms` provider path; the CMK is the KEK.
- **Ch 5**: the GKE security posture dashboard plays the role Trivy/kube-bench/StackRox play elsewhere; CIS 5.4.1 and 5.4.2 are both satisfied.
- **Ch 6**: default multi-region replication is GCP's DR answer.
- **Ch 7**: resource-tier IAM is the structural defence against **secret access ballooning**.
- **Ch 8/9**: same two-lever pattern — see the comparison table.
- **Ch 12**: CSI driver as one of several integration approaches.
