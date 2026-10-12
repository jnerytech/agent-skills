# Chapter 8: Exploring Cloud Secret Store on AWS

## Core Idea
Cloud Secrets integration rests on **two separate pieces of infrastructure — Secret Storage and KMS** — and on AWS that means **Secrets Store CSI Driver + IRSA** (a Kubernetes ServiceAccount annotated with an IAM role, assumed via the cluster's OIDC provider) to *read* Secrets from AWS Secrets Manager without them ever entering etcd, plus **AWS KMS as the `kms` encryption provider** for the Secrets that do.

## Frameworks Introduced

- **The two-lever cloud Secrets pattern** — applies identically on AWS, Azure, and GCP.
  - **Lever 1 — external store via CSI**: mount Secrets straight from the cloud store into the Pod filesystem. Secrets never touch etcd.
  - **Lever 2 — KMS as encryption provider**: for Secrets that *do* live in etcd, encrypt them with a cloud-managed KEK.
  - When to use: both, together. They cover different Secrets (application vs. platform — see Ch 1).

- **Workload identity via IRSA (IAM Roles for Service Accounts)** — how a Pod gets AWS permissions with no static credentials.
  - When to use: any Pod that needs to call an AWS API.
  - How:
    1. Create an IAM role whose trust policy has `Principal.Federated` = the cluster's **OIDC provider ARN** and action `sts:AssumeRoleWithWebIdentity`.
    2. Constrain it with a `Condition` on `<oidc>:aud = sts.amazonaws.com` and `<oidc>:sub = system:serviceaccount:<namespace>:<serviceaccount-name>`.
    3. Attach a **least-privilege policy** (read *this* secret, nothing else).
    4. Annotate the Kubernetes ServiceAccount with `eks.amazonaws.com/role-arn`.
    5. Set `serviceAccountName` on the Pod.
  - Why it works: the role is "a workload identity mapped to a role in the Kubernetes cluster… limited in what it can do. We cannot use the role to perform operations on other AWS resources." No long-lived AWS keys anywhere in the cluster.

- **Secrets Store CSI Driver architecture** — a `DaemonSet` (one per node) of three components:
  - **`node-driver-registrar`** — registers the CSI driver with the kubelet; creates a registration socket exposed via hostPath in the kubelet plugin registry.
  - **`secrets-store`** — mounts secret volumes on Pod creation and unmounts on deletion; gRPC implementation of the CSI **node service**.
  - **`liveness-probe`** — monitors driver health and restarts the Pod on failure.
  - Flow: Pod created/started/restarted → CSI Driver → CSI *provider* → cloud secret store → credentials mounted as a volume at the specified directory.

- **Terraform's four-verb lifecycle** (the IaC substrate for all three cloud chapters): `init` (initialize, download state) → `plan` (dry run — "similar to the dry-run command from kubectl") → `apply` (execute) → `destroy`. Plus `-target=<resource>` for surgical operations and `terraform import <resource> <id>` to adopt existing infrastructure. Layout: `main.tf` (entry point), `variables.tf` (dynamic inputs), `outputs.tf` (extracted values). **State belongs in S3, not on your filesystem**, for anything production-bound.

## Key Concepts
- **AWS Secrets Manager** — AWS's managed secret store: database credentials, application credentials, secure tokens.
- **Envelope encryption in Secrets Manager** — values are encrypted with an **AES-256 data key**, which is itself encrypted by **AWS KMS**. A **new data key is generated on every value change**. A custom KMS key can be configured.
- **Encryption in transit** — calls go through secure private endpoints and each must be signed with X.509 certificates or a Secrets Manager secret access key.
- **Versioning** — every create/update produces a version; reads return the latest; old versions remain retrievable until a scheduled deletion date. Recovering a pending-deletion version requires removing it from pending deletion first.
- **Rotation** — a scheduled **AWS Lambda** runs custom rotation code (templates at `aws-samples/aws-secrets-manager-rotation-lambdas`). The new version is **tested during rotation**; on failure the rotation is retried.
- **`recovery_window_in_days`** — how long a deleted secret can still be recovered.
- **`replica { region = … }`** — cross-region secret replication for DR.
- **CloudWatch** — real-time logs and metrics; **Logs Insights** for querying; supports alarms on suspicious access.
- **CloudTrail** — the audit service. `GetSecretValue` and `Decrypt` are the two event names that matter here.
- **CSI (Container Storage Interface)** — the standardized Kubernetes storage interface; `SecretProviderClass` is the object that maps a cloud secret to a mountable volume.

## Mental Models
- **"A secret is a concept that exists outside the realm of Kubernetes."** etcd is merely Kubernetes' *default* secret store, not the only one.
- **Think of the CSI driver as replacing etcd, not supplementing it.** "Instead of consuming Secrets from etcd… we can consume the Secrets from various external sources."
- **The ServiceAccount is the identity bridge.** Kubernetes RBAC controls who can use the ServiceAccount; AWS IAM controls what that ServiceAccount can reach. Two systems, one annotation.
- **Audit in two places, not one.** *Kubernetes* Secret access lands in CloudWatch (via the audit policy from Ch 2); *Secrets Manager* access lands in CloudTrail. You need both queries to see the whole picture.
- **Region-HA is free, cross-region DR is a decision.** Secrets Manager spans an AWS region's three AZs automatically; surviving the loss of a whole region requires an explicit `replica` block.

## Code Examples

The **SecretProviderClass** — maps an AWS Secrets Manager ARN to a mountable object:

```yaml
apiVersion: secrets-store.csi.x-k8s.io/v1
kind: SecretProviderClass
metadata:
  name: service-token
spec:
  provider: aws
  parameters:
    objects: |
      - objectName: "arn:aws:secretsmanager:eu-west-1:1111111:secret:service_token-IJ2VLg"
```

The **ServiceAccount → IAM role** annotation, the heart of IRSA:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: service-token-reader
  namespace: default
  annotations:
    eks.amazonaws.com/role-arn: "arn:aws:iam::11111:role/eks-secret-reader"
```

The **Pod** consuming it — note `readOnly: true` on both the mount and the CSI volume:

```yaml
kind: Pod
apiVersion: v1
metadata:
  name: nginx
spec:
  serviceAccountName: service-token-reader
  containers:
  - image: nginx
    name: nginx
    volumeMounts:
    - name: secret-from-asm
      mountPath: "/mnt/secrets-store"
      readOnly: true
  volumes:
  - name: secret-from-asm
    csi:
      driver: secrets-store.csi.k8s.io
      readOnly: true
      volumeAttributes:
        secretProviderClass: "service-token"
```
- **What it demonstrates**: the secret arrives as a **file** on the Pod filesystem — satisfying CIS 5.4.1 (Ch 5) — and never enters etcd.

The IAM trust policy that scopes the role to **exactly one** ServiceAccount:

```hcl
assume_role_policy = jsonencode({
  Version = "2012-10-17",
  Statement = [{
    Effect = "Allow",
    Principal = { Federated = "arn:aws:iam::${account_id}:oidc-provider/${oidc_provider}" },
    Action    = "sts:AssumeRoleWithWebIdentity",
    Condition = { StringEquals = {
      "${oidc_provider}:aud" = "sts.amazonaws.com",
      "${oidc_provider}:sub" = "system:serviceaccount:default:service-token-reader"
    }}
  }]
})
```
- **What it demonstrates**: the `sub` condition is the security control. Without it, *any* ServiceAccount in the cluster could assume the role.

KMS as the etcd encryption provider for EKS:

```hcl
resource "aws_kms_key" "ksm_kms_key" {
  description             = "ksm_kms_key"
  deletion_window_in_days = 30
  enable_key_rotation     = true      # ← always
}

module "ksm_eks" {
  create_kms_key = false
  cluster_encryption_config = {
    resources        = ["secrets"]
    provider_key_arn = aws_kms_key.ksm_kms_key.arn
  }
}
```

Installing the driver and the AWS provider (the driver is **not** available as an EKS add-on):

```bash
helm repo add secrets-store-csi-driver \
  https://kubernetes-sigs.github.io/secrets-store-csi-driver/charts
helm install -n kube-system csi-secrets-store \
  secrets-store-csi-driver/secrets-store-csi-driver
helm repo add aws-secrets-manager \
  https://aws.github.io/secrets-store-csi-driver-provider-aws
helm install -n kube-system secrets-provider-aws \
  aws-secrets-manager/secrets-store-csi-driver-provider-aws
```

## Reference Tables

| Concern | AWS service | How to verify |
|---|---|---|
| Secret storage | AWS Secrets Manager | `aws secretsmanager create-secret` |
| Encryption of etcd | AWS KMS as `kms` provider | CloudTrail `Decrypt` events |
| Workload identity | IAM role + OIDC (IRSA) | ServiceAccount annotation |
| Monitoring / logs | **CloudWatch** (+ Logs Insights, alarms) | Kubernetes audit events |
| Auditing | **CloudTrail** | `GetSecretValue` events |
| Regional HA | 3 AZs, automatic | — |
| Cross-region DR | `replica { region = … }` | — |

| Audit question | Where to look | Event / query |
|---|---|---|
| Who read a Kubernetes Secret? | CloudWatch Logs Insights | `filter @message like 'audit-test'` |
| Who read a Secrets Manager secret? | CloudTrail | `EventName=GetSecretValue` |
| Who decrypted with the KMS key? | CloudTrail | `EventName=Decrypt` |

| Terraform verb | Purpose | kubectl analogue |
|---|---|---|
| `init` | Initialize project, download state | — |
| `plan` | Show what would change | `--dry-run` |
| `apply` | Make the change | `apply` |
| `destroy` | Tear down | `delete` |

## Worked Example

**End-to-end: EKS Pod reads a Secrets Manager secret with no static credentials.**

1. **Network** — a VPC spanning **three availability zones** via `terraform-aws-modules/vpc`: three private subnets (`10.0.1-3.0/24`) for the workloads, three public subnets (`10.0.4-6.0/24`) for ingress, `enable_nat_gateway = true` so private nodes can reach the internet outbound. This is the authors' recommended middle ground between a fully private cluster and a public one.
2. **Cluster** — `terraform-aws-modules/eks` with `subnet_ids = private_subnets`, `create_cloudwatch_log_group = true`, and a managed node group. `cluster_endpoint_public_access = true` for convenience; the authors note it "can be fine-tuned [to] a restricted number of IPs."
3. **Authenticate** — `aws eks --region eu-west-1 update-kubeconfig --name eks-ksm-cluster`, then `kubectl get nodes` to confirm.
4. **Create the secret** with a cross-region replica and a recovery window:
   ```hcl
   resource "aws_secretsmanager_secret" "ksm_service_token" {
     name = "service-token"
     replica { region = "eu-central-1" }     # ← DR
   }
   resource "aws_secretsmanager_secret_version" "first" {
     secret_id     = aws_secretsmanager_secret.ksm_service_token.id
     secret_string = "a-service-token"
   }
   ```
   (CLI equivalent: `aws secretsmanager create-secret --name service-token --secret-string a-service-token --add-replica-regions Region=eu-central-1`.)
5. **Create the IAM role** with the OIDC trust policy scoped to `system:serviceaccount:default:service-token-reader`, and attach a read-only policy for **that one secret**.
6. **Install** the CSI driver and the AWS provider via Helm. Verify with `kubectl get daemonset -n kube-system`.
7. **Wire it up**: `SecretProviderClass` → annotated `ServiceAccount` → Pod with the CSI volume.
8. **Prove it**: `kubectl exec -it nginx cat /mnt/secrets-store/<objectName>`.
9. **Audit it**: CloudTrail shows the read performed by the *assumed role*, not a user —
   ```json
   {"userIdentity": {"type": "AssumedRole",
     "principalId": "id:secrets-store-csi-driver-provider-aws",
     "arn": "arn:aws:sts::1111111:assumed-role/eks-secret-reader/secrets-store-csi-driver-provider-aws"},
    "eventSource": "secretsmanager.amazonaws.com", "eventName": "GetSecretValue",
    "requestParameters": {"secretId": "arn:aws:secretsmanager:eu-west-1:…:secret:service_token-93z7he"}}
   ```
   That `AssumedRole` identity is the proof IRSA worked: no key, no user, a traceable per-workload identity.

## Anti-patterns
- **Storing Terraform state on the local filesystem** — "not a viable option for infrastructure as code targeting a production environment." Use an S3 backend.
- **An IAM trust policy without the `sub` condition** — any ServiceAccount in the cluster could then assume the role.
- **A broad IAM policy on the workload role** — the point of IRSA is that the role "cannot… perform operations on other AWS resources."
- **Auditing only CloudWatch or only CloudTrail** — Kubernetes-side and Secrets-Manager-side access are recorded separately.
- **Assuming region-level HA covers regional loss** — it doesn't; add a `replica` block.
- **`enable_key_rotation = false` on the KMS key** — rotation is a one-line setting.
- **Expecting the CSI driver as an EKS add-on** — it isn't; install via Helm.
- **Mounting the CSI volume writable** — set `readOnly: true` on both the volume and the mount.

## Key Takeaways
1. Cloud Secrets management needs **two** components: a secret store and a KMS. Use both.
2. **Secrets Store CSI Driver** mounts external Secrets as **files** — Secrets never enter etcd, and it satisfies CIS 5.4.1.
3. The driver is a per-node **DaemonSet** of `node-driver-registrar` + `secrets-store` + `liveness-probe`.
4. **IRSA** is the credential-free identity bridge: OIDC federation → IAM role → annotated ServiceAccount → Pod. Always scope the trust policy's `sub` to the exact ServiceAccount.
5. Secrets Manager gives envelope encryption (fresh AES-256 data key per value change), versioning with pending-deletion recovery, and **Lambda-driven rotation that tests before committing**.
6. **CloudWatch** for Kubernetes-side audit and alarms; **CloudTrail** for `GetSecretValue` and `Decrypt`.
7. Secrets Manager is regionally HA across three AZs by default; cross-region DR needs an explicit `replica` block.
8. Terraform state in S3; `plan` is your `--dry-run`; `-target` and `import` handle surgical and brownfield cases.

## Connects To
- **Ch 1**: platform vs. application Secrets — the CSI path is for *application* Secrets.
- **Ch 3**: `kms` provider and envelope encryption — AWS KMS is the KEK host here.
- **Ch 5**: CIS 5.4.1 (Secrets as files) and 5.4.2 (external store) are both satisfied by this pattern.
- **Ch 6**: `replica` blocks and Secrets Manager multi-region replication are the DR mechanism.
- **Ch 7**: cloud IAM is why **secret zero** largely disappears here.
- **Ch 9 / Ch 10**: the same two-lever pattern with Azure Key Vault and GCP Secret Manager.
- **Ch 12**: CSI driver as one of several integration approaches (vs. init container, sidecar, operator, sealed Secrets).
