# Chapter 14: Conclusion and the Future of Kubernetes Secrets Management

## Core Idea
There is **no single tool that addresses all needs** — the answer is always a composition of native and external solutions covering both platform and application Secrets — and the way to change what's missing is concrete: file a **KEP/GitHub issue** with a clear *what*, *why*, and ideally *how*, exactly as issue **#111532** did to eliminate the API-server restart on `EncryptionConfiguration` changes.

## Frameworks Introduced

- **The five DevSecOps continuous-improvement principles** — the book's closing method.
  1. **Skill acquisition** — "Most security exposures are linked to a lack of knowledge or awareness." Cross-team collaboration, training, webinars, meetups; contribute to open source and bring the knowledge back.
  2. **Start early, fail fast, and iterate** — waterfall infrastructure delays produce suboptimal outcomes or failure. Worse, "the adoption of Kubernetes is often done with the **relics of legacy patterns**." Start early with all stakeholders and learn alongside the project — a hybrid model fitting both waterfall planning and agile delivery.
  3. **Automation as a strategy / Everything as Code (EaC)** — "Most security breaches are related to a **lack of automation**." Teams fix systems, write a ticket, and stop. Instead: codify every action, review it through source control, automate it, and add **constant drift detection** so all systems get retrofitted with the latest remediations. EaC spans infrastructure, application, governance, compliance, security, and the BCP — all in CI/CD, "the gatekeeper against deploying critical applications on unsafe platforms."
  4. **Threat modeling** — identify threats and vulnerabilities *early*, with the security team embedded in each domain's core team, producing a proactive posture.
  5. **Incident response** — not a documented process but a **regularly and randomly triggered exercise**, gamified like NATO CCDCOE's **Locked Shields**, to upskill teams under real cyberattack conditions.

- **The five requested enhancements** — the authors' own wish list, and a useful lens on what's still weak.
  1. **Native encryption** — `aesgcm`/`aescbc` "come with a set of challenges that relatively complexify the implementation, exposing their encryption keys," and there's no commercial KMS plugin with enterprise support. Should also cover **any API object payload**, not just Secrets: "A deployment definition… can provide enough valuable information about the platform and applications to be exploited."
  2. **Dynamic secret** — updating Secrets on specific triggers, required by most regulations. KEP-3299 prioritizes automated *encryption-key* rotation; CSI Secrets Store triggers an update when the external source changes. **Still missing**: auditing the actual *usage* and *uniqueness* of a secret payload, to reduce the sprawl of one payload across many platforms — which turns one compromise into large-scale exposure.
  3. **Offload all API object data to an external vault** — replace etcd as the store, via the KMS plugin provider, removing the operational burden of securing etcd.
  4. **NBDE for etcd** — at least three instances bound to a network segment, each holding part of the encryption key, combined with a **TPM**. Would make `aesgcm`/`aescbc` "safer than they are today with limited external services to be deployed."
  5. **Enrich logging capabilities** — deeper **SIEM** integration so enterprises can correlate events and audit impacted systems fast during incident response, especially across multi-platform/multi-cloud object sprawl.

- **How to influence a project's roadmap** — the concrete escalation path.
  - **Proprietary solutions**: contact the vendor, ask for a ticket, hope it reaches engineering. "The evolution of such a request is about the same as following the activity of a black hole."
  - **Open source (including Kubernetes)**:
    1. Discuss with the appropriate **SIG** on Slack or at meetups — discover whether a workstream already exists to contribute to.
    2. Open an issue on the Kubernetes repository.
    3. Template: **a clear explanation of the *what* and the *why*, with clear examples, and if you can, the *how* with code.**

## Key Concepts
- **KEP (Kubernetes Enhancement Proposal)** — how the project documents design changes and the releases targeted for alpha, beta, and **GA**.
- **KEP-3299, "KMSv2 Improvements"** — the governing proposal. At the time of writing: **KMSv1 deprecated in 1.28** in favour of KMSv2, with **KMSv2 GA targeted for 1.29**; plus the **`KMSv2KDF` feature gate** enabling a new DEK per encryption, for regulations where KMSv2's default single-DEK-at-startup behaviour is unacceptable.
- **The four KMS themes since 1.25** — seamless key rotation; health checks for reliability; performance without compromising resilience and security; end-to-end observability between API server, KMS plugin, and KMS with auditing.
- **CSI Secrets Store as a *native* solution** — despite depending on an external vault, it is (a) built on the **native CSI architecture**, (b) carried by a Kubernetes **SIG**, and (c) uses native API objects with **no agent, sidecar, or non-native pattern**. Now fully integrated into enterprise distributions such as **Red Hat OpenShift 4.14**.
- **Sync Secret capability** — CSI Secrets Store can synchronize external Secrets **into native Kubernetes Secret objects** — which then *requires* encryption at rest, since those objects land in etcd.
- **Vault Radar** (HashiCorp) — scanners that identify Secrets **leaked or hardcoded in application code**, with remediation paths **ranked by risk**.
- **Locked Shields** — the international cyber-defence exercise (CCDCOE) cited as the model for gamified incident-response drills.

## Mental Models
- **Composition, not selection.** "There is not one software to address all needs. It often involves combining multiple projects and composing a solution toward our end goal while managing Secrets for **both the Kubernetes platform and applications running on it**." — the Ch 1 platform/application split, restated as the book's final word.
- **The Sync Secret feature is a trapdoor back into etcd.** Using CSI to *sync* rather than *mount* re-creates the native Secret object and every exposure that comes with it, so encryption at rest becomes mandatory again.
- **Secrets aren't the only sensitive API objects.** A Deployment manifest alone tells an attacker a great deal about the platform and its applications.
- **Payload uniqueness matters as much as payload secrecy.** The same secret value replicated across many platforms means one compromise becomes "large-scale exposure." Auditing *uniqueness* is a capability nobody currently offers.
- **Filing an issue works.** Issue #111532 was picked up by SIG Auth and implemented as #111919. "While it might seem rather intimidating to introduce an issue for such a large project, the open source communities around Kubernetes have been building a safe space for anyone to share their ideas."
- **Technology is easy; organizational change is not.** The book's closing line: "Technology is easy and should not be a substitute for organizational change."

## Code Examples

**The `EncryptionConfiguration` change that motivated issue #111532** — reordering providers to activate a KMS plugin:

```yaml
# Before — identity first, so nothing is encrypted on write
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
- resources:
  - secrets
  providers:
  - identity: {}
  - kms:
      name: myKmsPlugin
      endpoint: unix:///tmp/myKmsPlugin.sock
      cachesize: 100
```
```yaml
# After — kms first; previously this required an API-server RESTART
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
- resources:
  - secrets
  providers:
  - kms:
      name: myKmsPlugin
      endpoint: unix:///tmp/myKmsPlugin.sock
      cachesize: 100
  - identity: {}
```
- **What it demonstrates**: the provider list is **order-based** (Ch 3), and before this fix the API server had to be restarted to acknowledge a new order.

## Reference Tables

| Issue #111532 — the enhancement template in practice | |
|---|---|
| **What** | Make `EncryptionConfiguration` provider-order changes take effect without an API-server restart |
| **Why** | Current behaviour causes **service disruption**, requires an **elevated-privilege user**, and **blocks KMS plugin use on managed offerings** (no control-plane node access) |
| **Improves** | Day-2 operations (make it a regular CRUD API object); resilience and service continuity; KMS plugin usability on managed Kubernetes |
| **Outcome** | SIG Auth implemented it via **#111919** — config now reloads without restarting the API server |

| KMSv2 status at time of writing | |
|---|---|
| Kubernetes 1.25 | KEP themes begin: rotation, health checks, performance, observability |
| Kubernetes 1.28 | **KMSv1 deprecated**; KMSv2 still **beta**; `KMSv2KDF` feature gate for per-encryption DEK |
| Kubernetes 1.29 | **KMSv2 GA targeted** |

| CSI Secrets Store — why it counts as native | Detail |
|---|---|
| Architecture | Built on **CSI**, a native Kubernetes interface |
| Governance | Carried by a Kubernetes **SIG** |
| Pattern | Native API objects; **no agent, sidecar, or non-native pattern** |
| DevSecOps fit | Native CSI connectivity for the platform team; **self-service** via native API objects for app teams; metrics, logging, and **secret auto-rotation**; public roadmap and implementation status |

| Requested enhancement | Gap it closes |
|---|---|
| **Native encryption** (all API objects) | Key exposure in `aesgcm`/`aescbc`; unencrypted non-Secret payloads |
| **Dynamic secret** + usage/uniqueness auditing | Regulatory rotation requirements; payload sprawl |
| **Offload API object data to external vault** | Operational burden of securing etcd |
| **NBDE for etcd** (3+ instances + TPM) | Makes local AES providers safe without heavy external dependencies |
| **Enriched logging / SIEM** | Cross-cloud incident correlation and audit |

## Worked Example

**From frustration to merged code — the #111532 story, as a template you can reuse.**

1. **The friction.** In Ch 3 you learned the `EncryptionConfiguration` provider list is evaluated in order, and that migrating providers means reordering the list. What the chapter didn't dwell on: before this fix, **the API server had to be restarted** for a new order to take effect.
2. **Why that mattered, stated as impact — not as complaint.** Three concrete consequences: (a) it is "the source of **disruption from a service perspective**"; (b) it "**requires a user with elevated privileges**"; (c) it "does not allow the KMS provider's plugin capabilities to be leveraged within the context of the **managed Kubernetes offering** (no access to the control plane nodes)." That third point is the killer — it made the feature unusable on EKS/AKS/GKE.
3. **What improvement was requested, framed as outcomes**: move `EncryptionConfiguration` to "a regular CRUD API object" for day-2 operations; gain resilience and service continuity by avoiding the restart; unlock the KMS provider plugin on managed offerings.
4. **The submission format** — "a clear explanation of the **what** and the **why** with clear example(s) and, if you can, the **how** with the code to illustrate the change." The issue included the two YAML manifests above, before and after, plus a pointer to the enabling proposal **#111405**.
5. **Before filing** — discuss with the relevant SIG on Slack or at a meetup, to find an existing workstream to join rather than duplicating it.
6. **The outcome.** **SIG Auth**, which owns the KMSv2 implementation, picked up #111532 and implemented the change as **#111919**. The result is exactly what Ch 3 documents as current behaviour: `--encryption-provider-config-automatic-reload=true`, config reloaded **without restarting the API server**.

The generalizable point: the flag you now take for granted exists because someone wrote down what annoyed them, why it mattered in business terms, and what "fixed" would look like.

## Anti-patterns
- **Assuming one product solves Secrets management** — the whole book argues for composition across platform and application Secrets.
- **Using CSI Sync Secret without enabling encryption at rest** — syncing recreates native Secret objects in etcd.
- **Encrypting only `secrets`** — other API objects (a Deployment definition, for example) leak exploitable information about the platform.
- **Reusing the same secret payload across platforms and applications** — one compromise becomes large-scale exposure, and no tool currently audits payload uniqueness.
- **Waterfall infrastructure projects** — waiting until the end produces delays, suboptimal outcomes, or failure, and imports legacy patterns into a cloud-native platform.
- **Fixing security by hand and closing the ticket** — "Most security breaches are related to a lack of automation." Codify, review, automate, and add drift detection.
- **Treating the incident response plan as a document** — it must be a randomly triggered, gamified exercise.
- **Treating the handbook's practices as a one-time implementation** — "all these will not make much sense if they're considered as an endgame."
- **Expecting a vendor ticket to move a proprietary roadmap** — "about the same as following the activity of a black hole."

## Key Takeaways
1. **Compose, don't choose**: native Kubernetes constructs *plus* external vaults, covering platform and application Secrets both.
2. Track **KEP-3299**: KMSv1 deprecated in 1.28, KMSv2 GA targeted for 1.29, `KMSv2KDF` for per-encryption DEKs where regulation demands it.
3. **CSI Secrets Store is effectively native** — CSI-based, SIG-governed, no sidecars — and is the direction of travel (already in OpenShift 4.14).
4. **Sync Secret re-introduces etcd exposure** — enable encryption at rest whenever you use it.
5. The remaining gaps worth watching: encryption for **all** API objects, true **dynamic Secrets**, **usage/uniqueness auditing**, **etcd offload**, **NBDE+TPM for etcd**, and deeper **SIEM** integration.
6. **Scan for leaked and hardcoded Secrets** (e.g. Vault Radar) — sprawl detection is critical in multi-cloud.
7. To change open source: **talk to the SIG first**, then file an issue with *what*, *why*, and ideally *how* with code. #111532 → #111919 proves it works.
8. Five closing principles: **skill acquisition, start early/fail fast/iterate, automation and Everything as Code, threat modeling, and rehearsed incident response**.
9. Automate everything and add **drift detection** — a security fix applied by hand and documented in a ticket is not a fix.
10. **"Technology is easy and should not be a substitute for organizational change."** DevSecOps is a cultural shift toward shared responsibility, not a toolchain.

## Connects To
- **Ch 1**: the platform vs. application Secrets split, restated as the composition principle.
- **Ch 3**: `EncryptionConfiguration`, provider precedence, KMSv1/v2, and NBDE — this chapter is their roadmap.
- **Ch 5**: DevSecOps as continuous improvement; threat modeling and incident response extend it.
- **Ch 7**: **secret sprawl** is what Vault Radar scans for; payload uniqueness auditing is the missing control.
- **Ch 8/9/10**: managed Kubernetes offerings are exactly why #111532 mattered.
- **Ch 12**: CSI Secrets Store and its Sync Secret capability.
- **Ch 13**: SIEM integration and rehearsed incident response as production practices.
- **KEP process, Kubernetes SIGs, Locked Shields (CCDCOE), TPM, SIEM** — external references.
