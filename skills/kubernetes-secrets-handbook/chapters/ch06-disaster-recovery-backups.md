# Chapter 6: Disaster Recovery and Backups

## Core Idea
Secrets are **tier-0 services** — lose them and every dependent application stops, and many cannot simply be regenerated — so the backup itself must be encrypted, access-controlled, immutable, and *rehearsed*; an unencrypted backup of a well-managed secret store is a breach waiting to happen.

## Frameworks Introduced

- **Four reasons Secrets DR is not optional** — the justification structure.
  - **Service availability**: apps need Secrets to reach databases, internal/external services, and third-party APIs. Lose them and operations halt entirely until restored. *(Caveat the authors add: if an external store syncs into native Kubernetes Secret resources, a store outage does not immediately break running services.)*
  - **Recreation challenges**: third-party vendor Secrets need formalities and security checks to reissue; some are bound to specific hardware or timed information and **cannot be recreated at all**.
  - **Security implications**: after a compromise you need to *revert to a known-good state* or rotate on a short TTL — that requires a trusted backup.
  - **Regulatory requirements**: recoverability is a legal obligation in many industries; non-compliance means fines plus reputational damage.

- **Three backup strategies, chosen by RPO and budget.**
  - **Geo-replication / cross-region** — *active-active* (simultaneous multi-region writes; high availability, fastest recovery, minimal loss, most expensive) vs *active-DR* (one active, one standby; cheaper, higher data loss depending on sync frequency). Benefits: geographic redundancy, latency. Challenges: cross-region complexity and cost.
  - **Point-in-time snapshots to immutable storage** — full / incremental / differential (see table). Benefits: immutability defeats tampering and accidental deletion; restore to any past point. Challenges: **recovery point limited to the latest snapshot**, and snapshot sprawl costs.
  - **Writing to multiple places during transit** — encrypt the secret, write it to an **event stream** (Kafka / Pub-Sub), then batch-persist to immutable storage. Benefits: redundancy plus genuinely *event-driven* backup (every change is instantly captured). Challenges: stream+batch operational complexity and data duplication cost.

- **Secrets versioning strategy** — a distinct decision from the backup mechanism.
  - **All versions**: complete historical record, best for audit/compliance. Storage overhead — but "Secrets are usually small in size," so this is often negligible.
  - **Latest only**: cheapest and simplest; loses all change history in a loss event.
  - **Hybrid / selective versioning** (the authors' recommendation): keep multiple versions for important Secrets, latest-only for the rest, plus **retention policies** that archive or delete after a period or a version count.
  - **Always back up metadata and annotations** — they carry tracking, auditing, and usage-analysis context needed *during* recovery.

- **The DRP's four elements** — what a Kubernetes Secrets DRP must contain.
  1. **Clear roles and responsibilities** — a named recovery team with explicit tasks.
  2. **Defined communication strategy** — internal (recovery team) *and* external (stakeholders).
  3. **Prepared incident response** — protocols to minimize downtime and limit damage.
  4. **Recovery procedures** — scenario-specific, per source (etcd vs external store), and **frequently tested**.
  - Plus: recovery restricted to authorized personnel, and their actions **auditable**.

- **Six backup security guidelines** (the control set that would have prevented Case Study 2):
  1. **Isolated environment with access control** — IP whitelisting, differentiated user/admin roles, VPN-gated access, zero-trust (nothing trusted by default, inside or outside).
  2. **At-rest encryption with rotatable keys** — modern standards, regular rotation, secure key management.
  3. **In-transit security** — HTTPS/TLS, VPNs or dedicated lines.
  4. **Auditing and alerting** — log all access and modification attempts; alert on unusual patterns.
  5. **Immediate breach response** — assess impact, then **rotate and change all keys and credentials to prevent decryption**.
  6. **Immutable storage** — AWS S3 Object Lock or WORM; balance protection duration against cost.

## Key Concepts
- **Tier-0 service** — a service whose failure halts everything downstream. Secrets qualify: API keys, passwords, tokens, certificates "act as the linchpin for service interactions."
- **Backups ≠ audit logs** — backups preserve the *value* of the data; audit logs record *who accessed what, when*, for accountability and traceability. Do not conflate them.
- **Gameday** — a simulated real-world failure exercise. Scenarios to cover: total cluster failure (etcd-stored Secrets), catastrophic loss at the external store, and **failure of the backup system itself**.
- **Velero** — open-source Kubernetes backup/restore and migration, covering objects and persistent volumes; can handle etcd data.
- **etcdctl** — the etcd CLI; `snapshot save` is the raw etcd backup path.
- **Vault raft snapshot** — `vault operator raft snapshot save`. OSS Vault requires a **sidecar** plus a hand-rolled periodic upload; **Vault Enterprise** has built-in auto-snapshots to S3/GCS on a configurable interval.
- **`Backup-AzKeyVaultSecret`** — Azure cmdlet that downloads a secret to a file; **includes all versions**.
- **AWS Secrets Manager multi-region replication** — since 2021-03-03, replicate a secret and access it from the recovery region.
- **Kubestr** — validates the effectiveness of a backup/recovery strategy.
- **Kasten K10** — comprehensive Kubernetes application data management platform.

## Mental Models
- **Small data, enormous value.** "A large transportation company might only manage less than a gigabyte of Secrets data." Storage cost is almost never the real constraint — which is why *all-versions* backups are usually affordable.
- **Zero data loss is not the goal; minimizing it is.** "Achieving zero data loss can be challenging, and mitigating strategies should aim to reduce data loss to the barest minimum."
- **Your backup strategy is dictated by where the Secrets live.** etcd ⇒ Kubernetes-oriented (Velero, etcd snapshots). External store ⇒ use *that product's* native backup, and if it's a cloud service, prefer the same provider's backup service for integration and support.
- **An untested DRP is a document, not a plan.** Recovery procedures "need to be tested frequently to confirm their effectiveness during actual disasters."
- **Treat the backup store as a primary attack surface.** A robust backup strategy with unencrypted backups is worse than none — it centralizes every secret in one poorly-guarded place.

## Code Examples

Velero backup storage location:

```yaml
apiVersion: velero.io/v1
kind: BackupStorageLocation
metadata:
  name: aws
  namespace: velero
spec:
  provider: aws
  objectStorage:
    bucket: myBucket
  config:
    region: us-west-2
```

Raw etcd snapshot — the lowest-level, highest-caution option:

```bash
ETCDCTL_API=3 etcdctl snapshot save snapshot.db
```
- **What it demonstrates**: one command captures every Secret in the cluster. It also "requires more technical expertise and caution, given its potential effects on the entire Kubernetes cluster."

HashiCorp Vault raft snapshot (OSS path):

```bash
vault operator raft snapshot save snapshot.hcl
```
- **What it demonstrates**: OSS Vault gives you the primitive but not the automation — you must add a **backup sidecar container** that snapshots and uploads to S3, plus your own scheduling. Vault Enterprise configures a destination and interval and handles upload itself. Either way, **monitor backup metrics and alert on failure**.

## Reference Tables

| Snapshot type | Captures | Restore needs | Storage | Restore complexity |
|---|---|---|---|---|
| **Full** | Entire dataset every time | Just the latest full | Highest | Simplest |
| **Incremental** | Changes since the **previous backup** | Latest full + **all** subsequent incrementals | Lowest | Most intricate |
| **Differential** | Changes since the **last full** | Latest full + latest differential | Middle (grows over time) | Simple |

| Where Secrets live | Backup approach | Tools |
|---|---|---|
| **etcd** | Full cluster backup, or etcd snapshot | Velero, `etcdctl snapshot save` |
| **HashiCorp Vault** | Raft snapshot (sidecar OSS / auto Enterprise) | `vault operator raft snapshot` |
| **AWS Secrets Manager** | Multi-region secret replication | AWS native |
| **Azure Key Vault** | `Backup-AzKeyVaultSecret` (all versions) | Azure PowerShell |

| Decision factor | Question to answer |
|---|---|
| **Granularity** | Can I restore *one* Secret without touching the others? |
| **Encryption** | Is the backup encrypted at rest and in transit? |
| **Access control** | Is access limited to a specific admin group? |
| **Regulatory compliance** | Do GDPR/HIPAA dictate specific backup procedures here? |
| **Storage overhead** | Full (comprehensive, costly) vs incremental/differential (cheap, complex restore)? |
| **Data retention** | Am I pruning beyond regulatory/business need? Compression? Dedup? |
| **Long-term cost** | Every 10 min × 13 months adds up — tier older backups, drop stale versions |

## Worked Example

**Two case studies that define the failure modes, and one recovery that worked.**

*Case study 1 — service disruption from missing Secret backups.* A fast-growing e-commerce company runs on Kubernetes. A system failure crashes its clusters. It restores most services from backups — then discovers the Secrets stored in Kubernetes (payment-gateway API keys, database credentials) **were never backed up separately**. The platform goes offline, thousands of transactions halt, and it takes **several days** to regenerate Secrets, reconfigure them, and come back up. Result: lost sales and a decline in customer trust.
→ *Lesson:* "we backed up the cluster" is not "we backed up the Secrets." Verify granularity and coverage explicitly.

*Case study 2 — breach from unsecured backups.* A global SaaS company used a centralized Secrets management system and had **a robust backup strategy in place**. But the backups themselves were neither encrypted nor access-controlled. In 2022 criminals breached the backup store, read the Secrets in the clear, and used them for data theft and to inject malicious code into the company's services.
→ *Lesson:* "the lack of access control, and the non-existing encryption and security measures for the backups themselves, resulted in a severe incident." The backup is a copy of every secret you own — secure it like the original.

*The recovery that worked — OrgX.* Four things made it succeed:
1. **DRP existed and was rehearsed** — periodic **gamedays** validated it before it was needed.
2. **Cross-functional team activation** — the plan was executed across departments, not by one on-call engineer.
3. **Protected Secrets** — encrypted backups pulled from an **AWS S3 bucket**; decryption and restoration performed by **authorized personnel using secure procedures**; Secrets restored into a secret store with integrity preserved.
4. **Service continuity** — the rehearsed response restored Secrets swiftly, minimizing disruption, and applications came back on the **latest** secret values.

## Anti-patterns
- **Backing up the cluster but not the Secrets** — Case Study 1 exactly.
- **Unencrypted or unrestricted backup storage** — Case Study 2; turns your DR asset into your worst breach.
- **Conflating backups with audit logs** — they answer different questions and neither substitutes for the other.
- **A DRP that is never rehearsed** — gamedays are the only proof the procedures work.
- **Never testing failure of the backup system itself** — a scenario the authors explicitly call out.
- **Latest-version-only backups when audit history matters** — you lose the change trail exactly when you need it.
- **Dropping metadata and annotations from the backup** — recovery loses its context.
- **Unbounded retention** — 10-minute backups held 13 months accumulate real cost; tier and prune deliberately.
- **Relying on OSS Vault snapshots without automation or alerting** — the primitive exists; the schedule, upload, and failure alert do not.

## Key Takeaways
1. Secrets are **tier-0**; treat their DR with the same seriousness as the cluster's.
2. Some Secrets **cannot be regenerated** (vendor-issued, hardware-bound, time-bound) — backup is the only path.
3. Choose the strategy from where the Secrets live: etcd ⇒ Velero/etcd snapshot; external store ⇒ that product's native backup, ideally same-cloud.
4. Encrypt backups at rest with **rotatable** keys, encrypt in transit, restrict access (IP allowlist, RBAC, VPN, zero trust), and make storage **immutable** (S3 Object Lock / WORM).
5. Prefer **hybrid versioning**: all versions for critical Secrets, latest-only for the rest, with retention policies — and always include metadata/annotations.
6. Understand your snapshot type's restore chain: incremental needs the full **plus every** subsequent increment.
7. A DRP needs roles, communication, incident response, and tested recovery procedures — with recovery restricted to authorized, **audited** personnel.
8. Run **gamedays** covering cluster loss, external-store loss, and backup-system loss; involve DevOps, security, and IT together.
9. On backup compromise: assess impact, then **rotate every key and credential** so the stolen backup cannot be decrypted.

## Connects To
- **Ch 1**: backups were exposure #5 — this chapter is its mitigation, and Case Study 2 is that exposure realized.
- **Ch 3**: encryption at rest determines whether a stolen etcd snapshot is readable; losing the KEK loses the restore.
- **Ch 5**: the DRP is the direct analogy the authors use for cyber risk management; gamedays are the "fire drills" Ch 5 says teams lack.
- **Ch 7**: hybrid/multi-cloud risk compounds cross-region replication decisions.
- **Ch 8/9/10**: AWS Secrets Manager replication, Azure Key Vault backup cmdlet, GCP equivalents.
- **Ch 11**: Vault's raft snapshots, seal/unseal, and HA design.
- **RPO/RTO, WORM storage, zero-trust architecture** — external concepts this chapter operationalizes.
