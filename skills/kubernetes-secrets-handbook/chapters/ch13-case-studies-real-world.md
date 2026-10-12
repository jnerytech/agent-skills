# Chapter 13: Case Studies and Real-World Examples

## Core Idea
Production Secrets management is **lifecycle management** — provisioning → storage → distribution → rotation → decommissioning → revocation — not storage; the CI/CD half of that lifecycle is where Secrets most often leak, and **OIDC/Workload Identity Federation replaces the long-lived cloud credential in the pipeline**, which is the single highest-value change most teams can make.

## Frameworks Introduced

- **The four production qualities** — non-negotiable regardless of approach.
  1. **High availability** — etcd survives a node loss; but nodes must span **different data centers**, not one. Beyond that, a whole region can disconnect — which is why DR exists.
  2. **Disaster recovery** — see the etcd options below.
  3. **Encryption** — at rest, covering *both* disk storage and etcd Secret encryption.
  4. **Auditing** — present in every cloud provider, and in Vault and Conjur.

- **Three DR topologies when Secrets live in etcd**:
  - **Cluster created on demand in another region** — via etcd backups or Velero; on a cloud provider (e.g. GCP) "you can duplicate a Kubernetes cluster with the click of a button."
  - **Standby cluster in another region** — CI/CD must push Secrets to **two** clusters, *or* the standby pulls from Git under GitOps (Argo CD), so Secrets are never pushed directly.
  - **Active-active clusters in multiple regions**.
  - With an **external store**, DR is the store's problem: Azure Key Vault and GCP Secret Manager give cross-region *availability*; AWS Secrets Manager and Vault Enterprise give cross-region *replication*.

- **The five CI/CD Secret risks** — and what each looks like.
  - **Leaking Secrets in a pipeline** — GitHub Actions masks a printed secret, "**This is not enough**." Write it to a file and print the file, and the mask is bypassed. Worse, **job history and logs persist** and often cannot be erased. Secrets can also be baked into **build artifacts** downloadable from the CI/CD UI.
  - **Production Secrets in CI/CD** — pipeline operations differ from production ones; a misconfigured pipeline then runs with production privileges and can affect a live system. Blast radius is far larger than with a dedicated CI secret.
  - **Malevolent contributions** — a PR that triggers a pipeline gives its author many ways to exfiltrate the secret. Mitigate with protected branches, segregated pipelines, fine-grained permissions. GitHub Actions helps: **fork workflows get no access to Secrets**, and runs from public forks can require approval.
  - **Untrusted software** — a Jenkins plugin or workflow action that reads pipeline Secrets and ships them elsewhere. Use trusted sources only, verify authenticity (**hash-based verification**), stay patched.
  - **Pipelines with extra privileges** — a *test* job with permissions broad enough to delete **production** Secrets. "A pipeline misconfiguration can lead to data loss or even a production outage."

- **Seven CI/CD best practices**:
  1. Do not commit clear-text Secrets.
  2. If using tokens, **rotate them and make them short-lived**.
  3. **If an OIDC-based integration is possible, use it** — it is more secure.
  4. Moving pipelines to Kubernetes on-premises hardens security.
  5. Follow the principle of least privilege.
  6. Use **dedicated Secrets for testing**.
  7. Never share Secrets between testing and production.

- **Three secret-update/rotation mechanics** — pick per application:
  - **Monitoring and reloading** — watch for changes, update values in application memory.
  - **Keyring mode** — keep multiple versions live to prevent downtime; monitor which version is in use and retire old ones on time.
  - **Restart as reload** — automatically restart Pods on change (a Kubernetes Job or similar detects and triggers), so init containers re-run and fetch the latest.
  - Choose against four criteria: **timely secret consumption**, **graceful secret changes** (no state loss), **downtime avoidance** (multiple replicas + rolling updates), and **monitoring and alerting** on rotations and restarts.

- **The Keywhiz authorization data model** (clients / secrets / groups / users) — a reusable design:
  - **Clients** — services or applications needing Secrets; prove identity with a **client certificate**.
  - **Secrets** — uniquely named and **immutable once set**, though multiple versions may be kept.
  - **Groups** — the join table. Label both clients and Secrets; a client sees a secret when they share a group tag. Square used three group types: **one per service on a specific server**, **one per distinct service**, and **a universal group of all clients**.
  - **Users** — the humans administering Keywhiz, who assign group tags.

## Key Concepts
- **Workload Identity Federation** — the OIDC trust between a CI/CD provider and a cloud, exchanging the job's auto-generated OIDC token for **short-lived** cloud credentials. Replaces "attaching the credentials of the cloud provider on the CI/CD job" — static credentials that, if compromised without proper logging or audit, "could be used for an extended period, creating a **silent breach**."
- **GitOps / Argo CD** — a Kubernetes controller that watches a Git repo and reconciles running infrastructure toward the declared state. Compatibility: **SealedSecrets works with no extra effort**; **external secret stores are unaffected** (data lives elsewhere); **Helm Secrets support depends on the tool** — Argo CD can support it but requires modifications for encryption/decryption of chart-distributed Secrets.
- **Tekton** — open-source framework for building CI/CD systems inside Kubernetes.
- **Authorization sprawl** — RBAC set too broadly, usually unintentionally, so users or services hold more privilege than needed.
- **Masking** — obscuring secret values in logs and UIs via pattern recognition, checksums, or explicitly marked sensitive fields in logging config.
- **AES-GCM** — the mode Keywhiz used to encrypt Secrets before database storage, recommended by **NIST SP 800-38D**.
- **HKDF** — HMAC-based key derivation function giving each Keywhiz secret **its own unique key**, "so that even if one key is discovered, the others remain safe." Derivation keys lived in **HSMs**.
- **certstrap** — the certificate management tool Square used to run its own CAs, avoiding OpenSSL's complexity, issuing X.509 identities for **mTLS**.
- **Keysync** — the Keywhiz client: connects over mTLS, downloads Secrets into **tmpfs**, and **keeps working from its cache if the Keywhiz server is down** — only a full server reboot forces a re-fetch.
- **SIEM** — integrating audit logs with security information and event management systems to correlate events and identify patterns.

## Mental Models
- **Manual secret persistence is disqualified before the discussion starts.** Four reasons: you lose track of deployment needs, dependencies are invisible, there's no clear depiction of what's applied, and it's incompatible with infrastructure as code.
- **Masking is a speed bump, not a control.** The mask covers `echo $SECRET`; writing to a file and printing the file walks straight past it — and the logs are retained.
- **Run the pipeline where the secrets already are.** If Vault sits in a private network, integrating an external CI/CD provider means **exposing Vault publicly**. Running the pipeline inside Kubernetes removes that requirement entirely.
- **A Secrets management system is an ecosystem, not a system.** Keywhiz's effectiveness "relies heavily on its integration with the company's existing workflows, policies, and organizational culture" — directory services for role-based access, compliance-driven audit trails, and so on.
- **Ease of use is a security property.** Square designed Keywhiz to be easy "If it wasn't, people might try to take shortcuts, which could be less safe." (The Ch 7 shadow-IT risk again.)
- **Separate key rotation from software deployment.** Keywhiz decoupled them so security could be updated without changing the whole system — "safer and more flexible."
- **Enforce specific Secret types to get free validation.** Mandating `kubernetes.io/dockerconfigjson` for registry credentials means Kubernetes validates the structure, and the type makes the secret **self-descriptive** for auditors and developers alike.

## Code Examples

**GCP Workload Identity Federation for GitHub Actions** — the pattern that removes the static service-account key:

```bash
# 1. Create the identity pool
gcloud iam workload-identity-pools create "ga-ksm-pool" \
  --project="${GCP_PROJECT_ID}" --location="global" \
  --display-name="GitHub actions Pool"

# 2. Register GitHub as an OIDC provider
gcloud iam workload-identity-pools providers create-oidc "github" \
  --project="${GCP_PROJECT_ID}" --location="global" \
  --workload-identity-pool="ga-ksm-pool" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com"

# 3. Bind a GCP service account to ONE GitHub repository
gcloud iam service-accounts add-iam-policy-binding \
  "github-service-account@${GCP_PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/${project_number}/locations/global/workloadIdentityPools/ga-ksm-pool/attribute.repository/${github_org}/${github_repo}"
```

```yaml
jobs:
  run:
    permissions:
      id-token: write        # ← required to mint the OIDC token
      contents: read
    steps:
    - id: 'auth'
      uses: 'google-github-actions/auth@v1'
      with:
        workload_identity_provider: 'projects/{project-id}/locations/global/workloadIdentityPools/ga-ksm-pool/providers/github'
        service_account: 'github-service-account@${GCP_PROJECT_ID}.iam.gserviceaccount.com'
    - id: fetch
      run: |
        curl -H 'Bearer: ${{ steps.auth.outputs.access_token }}' \
          https://secretmanager.googleapis.com/v1/projects/project-name/secrets/secret-name/versions/latest:access
```
- **What it demonstrates**: the `attribute.repository` binding scopes the trust to **one repo**. No key material lives in GitHub.
- **The authors' own warning**: "the preceding steps print the secret **on purpose** since they serve as an example… **You should not print any retrieved Secrets on the CI/CD console.**"

**The authorization-sprawl anti-pattern**, exactly as the book presents it:

```yaml
kind: Role
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: myapp-role
rules:
- apiGroups: [""]
  resources: ["pods", "secrets"]                                     # ← two resource kinds
  verbs: ["get","watch","list","create","update","delete"]           # ← every verb
```
- **What it demonstrates**: `myapp-sa` ends up with full CRUD over **all** Secrets in the namespace when it probably needed `get` on one. Fix by naming the minimum verbs, splitting the Role, and reviewing RBAC on a schedule.

**Rotation job that triggers Pod restarts** (the "restart as reload" method):

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: secret-rotator
spec:
  template:
    spec:
      containers:
      - name: secret-rotator
        image: user-implemented-rotator-image
        env:
        - name: VAULT_ADDR
          value: "http://vault:8200"
        - name: SECRET_PATH
          value: "secret/my-app"
```
- **What it demonstrates**: the job watches Vault for rotations and restarts affected Pods so their **init containers run again** and fetch the new version.

**Argo CD in a few commands**:

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/v2.5.8/manifests/install.yaml
kubectl port-forward svc/argocd-server -n argocd 8080:443
argocd admin initial-password -n argocd
argocd app create guestbook --repo https://github.com/argoproj/argocd-example-apps.git \
  --path guestbook --dest-server https://kubernetes.default.svc --dest-namespace default
```

## Reference Tables

| Secrets approach | DR mechanism | Notes |
|---|---|---|
| **etcd — on-demand cluster** | etcd backups / Velero | Cloud providers can clone a cluster |
| **etcd — standby cluster** | CI/CD pushes to both, **or** GitOps pull | GitOps avoids pushing Secrets to clusters |
| **etcd — active-active** | Both clusters live | Highest cost |
| **Azure Key Vault / GCP Secret Manager** | Cross-region **availability** | Automatic |
| **AWS Secrets Manager / Vault Enterprise** | Cross-region **replication** | Configured |

| GitOps compatibility | Works? | Caveat |
|---|---|---|
| **SealedSecrets** | ✓ No extra effort | Controller applies Secrets from Git |
| **External secret store** | ✓ Unaffected | Secret data lives elsewhere |
| **Helm Secrets** | ⚠ Depends on the tool | Argo CD **requires modifications** for encrypt/decrypt |

| Rotation method | Downtime | Complexity | Best for |
|---|---|---|---|
| **Monitoring and reloading** | None | App must support live reload | Apps that can re-read config |
| **Keyring mode** | None | Must track version in use | Multiple valid versions accepted |
| **Restart as reload** | Managed by rolling update | Lowest app-side effort | Init-container-based Secret delivery |

| Keywhiz lesson | Why it generalizes |
|---|---|
| **Centralized management with Kubernetes is hard** | K8s workloads are ephemeral and decentralized; needs dynamic create/delete, RBAC integration, multi-cluster/namespace support |
| **It's an ecosystem, not a system** | Value depends on integration with directory services, compliance regimes, and culture |
| **Lack of auditing as a story** | Client-side tmpfs delivery is **invisible to the server** — no record of who used it, when, how, or from where |

## Worked Example

**Keywhiz at Square — a complete secrets system, and why it was deprecated.**

*The design.*
- **Business justification**: Secrets should be hard to reach — never on a developer's machine or the internet. Services fetch them **directly**, without intermediate steps. Centralizing them prevented scattering, enabled health checks (are keys strong enough? due for rotation?), and — crucially — **produced a detailed record of every access**, "something you can't do if you just drop the Secrets onto servers as files."
- **Encryption**: each secret was wrapped in **AES-GCM** (NIST SP 800-38D) *before* hitting the database, with a **unique per-secret key derived via HKDF**, and derivation keys held in **HSMs**. One compromised key does not unravel the rest.
- **Authentication via PKI**: **mTLS with X.509** certificates as service identity, with **certstrap** running Square's own CAs — a chain of trust where every service's identity is verified.
- **Authorization**: the clients / secrets / **groups** / users model above. Groups are tags on both sides; matching tags grant access.
- **Distribution via Keysync**: connects over mTLS, pulls the Secrets it needs, and stores them in **tmpfs** — "a temporary space that doesn't save anything once the server is turned off," so a power cut or reboot leaves nothing behind. Keysync also **survives Keywhiz outages** by serving from what it already downloaded; only a full reboot forces a re-fetch. Admins used a CLI to add/remove/change Secrets and check system health.
- **Decoupling**: key rotation was deliberately separated from software deployment.

*Why it ended.* **Keywhiz was deprecated on September 18, 2023** and is no longer maintained; the recommended migration is to HashiCorp Vault. Three lessons the authors draw:
1. **Centralized management doesn't fit Kubernetes cleanly.** Kubernetes needs dynamic secret creation and deletion matching ephemeral Pods, tight RBAC integration, and efficient multi-cluster/multi-namespace handling. Keywhiz's centralized strength was a poor match; Vault's dynamic Secrets, service-account auth, and fine-grained policies fit better.
2. **A secrets system is an ecosystem.** A healthcare org adopting Keywhiz would need it synced with employee directory services for role/department-based access and aligned with compliance standards where its audit trails and encryption become the evidence. Technical capability alone doesn't determine efficacy.
3. **The tmpfs delivery model created an audit blind spot.** Because Keysync downloads Secrets client-side, the server cannot see whether an application actually *used* them. Four things go unrecorded: **which user or service accessed a secret**, **the precise timestamp**, **the nature of the access** (read vs. modify), and **the IP or machine it came from**. The result is "potential gaps in the auditing process" that break the continuous lifecycle trail.

That third lesson is the sharpest: **the same tmpfs mechanism that makes distribution secure makes usage unobservable.** Any architecture that hands Secrets to the client permanently trades some auditability for some confidentiality.

## Anti-patterns
- **Manual secret persistence to Kubernetes** — four disqualifying reasons; incompatible with IaC.
- **Storing long-lived cloud credentials in CI/CD job variables** — static credentials enable a **silent breach**; use OIDC/Workload Identity Federation.
- **Trusting CI/CD secret masking** — write to a file, print the file, mask defeated. And the logs persist.
- **Emitting Secrets into build artifacts** — downloadable from the CI/CD UI.
- **Using production Secrets in CI/CD** — vastly larger blast radius; use dedicated test Secrets.
- **Unprotected branches on repos whose pipelines touch Secrets** — a PR becomes an exfiltration vector.
- **Unverified or outdated pipeline plugins/actions** — the classic supply-chain path.
- **Over-broad pipeline permissions** — a test job that can delete production Secrets.
- **RBAC Roles listing every verb on `["pods","secrets"]`** — authorization sprawl; the book's own example.
- **Distributing Secrets in plain text at rest** on the host filesystem or in a container environment.
- **Rotation exemptions without documentation** — if a secret can't be rotated, **mark it, document it, and have an incident-response path to rotate it fast**.
- **Exposing a private Vault publicly** just to reach an external CI/CD provider — run the pipeline in-cluster instead.

## Key Takeaways
1. Production Secrets management needs four qualities: **HA (across data centers), DR (across regions), encryption, and auditing**.
2. **OIDC / Workload Identity Federation is the CI/CD fix** — short-lived tokens instead of stored cloud keys. Scope the binding to a single repository.
3. **CI/CD masking is not a control.** Assume anything the pipeline can read can be exfiltrated by a determined PR author.
4. **Never share Secrets between test and production**; scope pipeline permissions to the environment they touch.
5. Running pipelines **inside Kubernetes** (e.g. Tekton) avoids exposing private infrastructure to an external CI/CD provider.
6. Under **GitOps**, SealedSecrets and external stores work cleanly; **Helm Secrets needs Argo CD modifications**.
7. Manage the whole lifecycle: **provision → store → distribute → rotate → decommission → revoke**. Decommissioning must be wired into service-retirement workflows.
8. Pick a rotation mechanic per app: **monitor-and-reload**, **keyring mode**, or **restart-as-reload**.
9. **Enforce specific Secret types** (e.g. `kubernetes.io/dockerconfigjson`) to gain built-in validation and self-describing, auditable Secrets.
10. **Tag, label, and mask**: metadata for granular access and audit trails; masking so logs and UIs never carry values.
11. Assign **explicit responsibility and on-call ownership** for both distribution and store management, and run **ongoing penetration testing** across the whole lifecycle, feeding results into risk evaluation.
12. Keywhiz's warning: client-side tmpfs delivery is secure but **unobservable** — you cannot audit what the server never sees.

## Connects To
- **Ch 3**: encryption at rest is one of the four production qualities.
- **Ch 5**: auditing, compliance, and the DevSecOps CI/CD insertion point.
- **Ch 6**: DR topologies, backups, and the emergency recovery plan referenced directly.
- **Ch 7**: **authorization sprawl** is *secret access ballooning*; the ease-of-use argument is the shadow-IT risk; Keywhiz's centralization answers *sprawl*.
- **Ch 10**: the GCP Workload Identity work this chapter extends to GitHub Actions.
- **Ch 11**: Vault's Kubernetes auth is the same JWT/OIDC pattern; Vault is Keywhiz's recommended successor.
- **Ch 12**: SealedSecrets, init containers, and sidecars as the delivery mechanisms being operated here.
- **NIST SP 800-38D (AES-GCM), HKDF, mTLS/X.509, HSM, Prometheus/Grafana, SIEM** — external standards and tools referenced.
