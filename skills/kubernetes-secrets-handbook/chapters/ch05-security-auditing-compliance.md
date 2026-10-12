# Chapter 5: Security, Auditing, and Compliance

## Core Idea
Stop asking "how do we secure this?" and start from the CISO's real question — "what regulations must we comply with?" — because **cyber risk management** (business-driven, per-business-unit, reportable) succeeds where **cybersecurity** (IT-centric, incident-driven, lock-everything-down) produces disabled controls and shadow infrastructure.

## Frameworks Introduced

- **Cybersecurity vs. Cyber risk** — the chapter's central reframe.
  - When to use: whenever a security control is being designed, justified, or resisted.
  - How: run the decision from the business down, not from IT up.

| | **Cybersecurity** (traditional) | **Cyber risk management** |
|---|---|---|
| Owner | A small IT team working in isolation | The board + every business unit |
| Scope | Infrastructure stack only | Whole organization, incl. critical business apps |
| Trigger | Incident-driven / reactive | Continuous, risk-prioritized |
| Posture | "Lock everything down" | Controls proportional to asset criticality |
| Seen as | A **cost** and a constraint | A **business value** with near-real-time reporting |
| Example control | 30-day password rotation + MFA everywhere | OTP for general web apps; MFA + audit **only** for source-code push |

  - Why it works: "Doing (cyber)security for the sake of ticking a box will not provide any benefit… and will frustrate all members of staff, including the IT department, **resulting in security measures being disabled and shadow infrastructure being built**."

- **The four board questions** — how to get executive sponsorship for a security budget.
  - When to use: building governance, justifying investment.
  - How, ask each executive:
    - **CEO**: What would be the brand damage of a security breach?
    - **CFO**: What would be the financial impact of a security breach?
    - **CISO**: Are we prioritizing our investment to improve our security posture?
    - **COO**: Would our customers/partners trust doing business with us?

- **The five CIS Kubernetes Benchmark rules that govern Secrets** (v1.7.0 at time of writing) — the concrete audit checklist.
  - When to use: assessing or proving a cluster's Secrets posture.
  - How:

| Rule | Control | Remediation / chapter |
|---|---|---|
| **1.2.29** | `--encryption-provider-config` is set as appropriate | Enable native encryption (Ch 3) |
| **1.2.30** | Encryption providers configured appropriately — must be `aescbc`, `aesgcm`, or `kms` | Audit the referenced config file's content |
| **3.2.2** | Audit policy covers key security concerns — tracks access/modify/use of `Secret`, `ConfigMap`, `TokenReview` via Pod and Service | Ch 2 audit policy |
| **5.4.1** | **Prefer Secrets as files over Secrets as environment variables** — env vars expose Secrets in node memory and application logs | Switch to volume mounts |
| **5.4.2** | Consider external secret storage instead of embedded etcd | Ch 11 |

- **DevSecOps as four insertion points in the existing DevOps cycle** — not a separate framework.
  - **Planning**: security, governance, compliance requirements in the *initial project scope*. Pitfall: treating them as a final pre-release gate.
  - **Development**: security in coding governance; code analysis tooling catches vulnerabilities **before commit**.
  - **CI/CD**: scan code and container images for vulnerabilities before they reach production.
  - **Continuous monitoring/auditing**: near-real-time detection and response; supports a risk-based posture where some exposures are knowingly accepted but closely watched.

## Key Concepts
- **Security posture** (NIST 800-37) — "The security status of an enterprise's networks, information, and systems based on information assurance resources (for example, people, hardware, software, and policies) and capabilities in place to manage the defense of the enterprise and to react as the situation changes."
- **CIS Benchmarks** — per-platform security-control benchmarks (OS, mobile, server software, cloud, virtualization, container, Kubernetes) that **map onto** HIPAA, PCI-DSS, SWIFT, ISO 27000, SOC 2, and NIST — the key to a unified approach across overlapping regulations.
- **Trivy** (Aqua Security) — container image + cluster scanner with a **Secrets-specific severity check**.
- **kube-bench** (Aqua Security) — runs the CIS Kubernetes Benchmark as a configurable YAML job; supports `Type: "skip"` to disable a control that doesn't fit your governance.
- **Compliance Operator** — operator-based CIS + **OpenSCAP** profile assessment (e.g. ACSC Essential Eight) that also **applies remediations** as YAML, one at a time or in batches.
- **StackRox** — open-source Kubernetes security platform: image vulnerability management, runtime mutation detection, **network-flow visualization with NetworkPolicy mitigation**, regulatory scanning, and API-driven pipeline integration. Risk-ranked dashboard.
- **DRP (Disaster Recovery Plan)** — the analogy the authors use for cyber risk: define the *minimal* set of requirements to keep the business achieving its goals even under attack.

## Mental Models
- **Add compliance rings to the onion.** Ch 3's etcd onion gains outer layers of *continuous discovery, assessment, analysis, and mitigation execution* — the posture is a loop, not a state.
- **Regulations overlap; benchmarks exploit the overlap.** A US healthcare-AI SaaS may owe HIPAA + GDPR + PCI-DSS + EU AI Act + Cyber Resilience Act + Data Act + NIS2 + export controls simultaneously. Don't implement eight programs — implement CIS controls and map them.
- **Think "surgical vs. generic tools."** Your org may already own an enterprise security suite; `kube-bench` still earns its place because it speaks Kubernetes.
- **Security is not a finite state.** "There is no single and simple recipe"; the goal is a continuously shrinking gap, not a pass.
- **Tailored security removes the feeling of constraint.** When controls match the risk of the asset, stakeholders participate instead of routing around them.

## Code Examples

Secrets-targeted vulnerability scan of a whole cluster:

```bash
trivy k8s --severity-checks=secret --report=summary cluster
```
- **What it demonstrates**: Trivy has a secret-specific check class; you don't have to sift a general CVE report.

A kube-bench control definition — note it carries **audit command, test, and remediation** in one object:

```yaml
controls:
  id: 1
  text: "Master Node Security Configuration"
  type: "master"
  groups:
  - id: 1.1
    text: API Server
    checks:
    - id: 1.1.1
      text: "Ensure that the --allow-privileged argument is set (Scored)"
      audit: "ps -ef | grep kube-apiserver | grep -v grep"
      tests:
        bin_op: or
        test_items:
        - flag: "--allow-privileged"
          set: true
      remediation: "Edit /etc/kubernetes/config on the master node and set
                    KUBE_ALLOW_PRIV to '--allow-privileged=false'"
      scored: true
```

Disabling a control that doesn't apply to your governance:

```yaml
    - id: 1.1.1
      text: "Ensure that the --allow-privileged argument is set (Scored)"
      Type: "skip"
      scored: true
```
- **What it demonstrates**: benchmarks are *tailorable*. Skipping is a documented governance decision, not cheating — as long as it's deliberate.

The compliance-grade audit policy (Secrets **and** ConfigMaps):

```yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
- level: Metadata
  resources:
  - group: ""
    resources: ["secrets", "configmaps"]
```

## Reference Tables

| Regulation | Domain | Why it touches Kubernetes Secrets |
|---|---|---|
| **HIPAA** (US) | Patient records | Encryption at rest + access audit |
| **GDPR** (EU) | Personal data of third parties | Storage, processing, breach notification |
| **PCI-DSS** | Payment card transactions | Key management, segregation, audit trail |
| **EU AI Act** | Use of AI | Model/credential governance |
| **Cyber Resilience Act** | Secure software supply chain | Image scanning, provenance |
| **Data Act** | Cross-cloud data portability | Multi-cloud secret strategy |
| **NIS2** | Critical infrastructure | Incident management best practice |
| **Export controls** (US Dept. of Commerce) | Sanctioned countries | Distribution restrictions |

| Tool | Assesses | Remediates | Note |
|---|---|---|---|
| **Trivy** | Image CVEs + secret exposures | ✗ | `--severity-checks=secret` |
| **kube-bench** | CIS Kubernetes Benchmark | ✗ (gives remediation text) | **Needs elevated privileges** |
| **Compliance Operator** | CIS + OpenSCAP profiles | ✓ (YAML, batched or single) | **Needs elevated privileges**; operator-capable distros |
| **StackRox** | Images, runtime, network flows, regulatory profiles | ✓ (NetworkPolicy paths) | Risk-ranked UI; API-driven for pipelines |
| **Kubernetes audit logging** | All object interactions | ✗ | The audit trail of record |

## Worked Example

**Building the security-posture blueprint for a multi-regulation organization.** The authors walk the "reversed approach" — start at the last question, not the first:

1. **Ask the CISO question first**: "What are my CISO team requirements?" The answer comes back as another question — *"What are the regulations that my organization has to comply with?"* This is a legal question, not a technical one.
2. **Enumerate the obligations.** For the worked case — a US software company using AI in healthcare, selling SaaS and on-prem to medical practices globally — that is HIPAA + GDPR + PCI-DSS + EU AI Act + Cyber Resilience Act + Data Act + NIS2 + sanctions compliance.
3. **Collapse the overlap.** Rather than eight programs, adopt the **CIS Benchmarks** and use the published mappings (e.g. *CIS Controls v8 → NIST 800-53 Rev 5*) as the evidence bridge to each regulator.
4. **Narrow to the Kubernetes Secrets controls** — rules 1.2.29, 1.2.30, 3.2.2, 5.4.1, 5.4.2 (table above). This is now a five-item, testable checklist.
5. **Measure with `kube-bench`** on a **test environment mirroring production** (both kube-bench and Compliance Operator require elevated privileges unsuitable for prod). Tailor the YAML: `Type: "skip"` for controls your governance has consciously excluded.
6. **Close the gaps**: enable `--encryption-provider-config` with `aesgcm`/`kms` (1.2.29/1.2.30); apply the `secrets`+`configmaps` audit policy (3.2.2); convert env-var Secret injection to **file mounts** (5.4.1); plan the external store (5.4.2).
7. **Make it continuous**: wire Trivy into CI/CD, StackRox for runtime and network flows, and ship audit logs. The posture is now a repeating discover → assess → analyze → execute loop, with reporting the board can read.

## Anti-patterns
- **Security as a box-tick** — controls get disabled and shadow infrastructure appears.
- **Security owned by an isolated IT team** — limited scope (infra only), no knowledge of the business continuity plan, and no real incident-response capability.
- **One-size-fits-all policy** — 30-day rotation + heavy MFA fits engineers, breaks the business team on short-timeout web apps; people route around it.
- **Injecting Secrets as environment variables** — CIS 5.4.1: exposed in node memory and application logs. Prefer file mounts.
- **Treating compliance as a pre-release gate** — the Planning-stage pitfall; requirements must enter at project scoping.
- **Running kube-bench / Compliance Operator directly in production** — they need elevated privileges; validate on a production-like test environment first.
- **Treating DevSecOps as a separate framework** — it is complementary to DevOps, woven into each existing step.
- **No fire drills** — teams have monitoring and processes but never rehearse, exactly as with an untested DRP.

## Key Takeaways
1. Start from **regulation**, not from technology. The CISO's requirement is a legal question in disguise.
2. **Cyber risk management** produces controls people actually keep; **cybersecurity-as-lockdown** produces workarounds.
3. Use **CIS Benchmarks** as the unifying layer across overlapping regulations, then use published mappings as regulator-facing evidence.
4. Five CIS rules define Kubernetes Secrets compliance: 1.2.29, 1.2.30, 3.2.2, 5.4.1, 5.4.2 — memorize these.
5. **CIS 5.4.1 is a direct design instruction**: mount Secrets as files, not environment variables.
6. Tool chain: **Trivy** (images + secret exposures) → **kube-bench** (CIS) → **Compliance Operator** (SCAP + remediation) → **StackRox** (runtime/network/regulatory) → **audit logging** (evidence).
7. Both kube-bench and Compliance Operator need privileges; run them on a production-mirroring test cluster.
8. Security posture (NIST 800-37) is a *status that changes*; the deliverable is a continuous improvement loop with board-readable reporting.

## Connects To
- **Ch 3**: rules 1.2.29/1.2.30 are literally the `EncryptionConfiguration` work; the onion diagram gains compliance layers here.
- **Ch 2**: rule 3.2.2 is the audit policy introduced there, extended to ConfigMaps and TokenReview.
- **Ch 6**: DRP is the explicit analogy for cyber risk management — minimal requirements to keep the business running.
- **Ch 11**: rule 5.4.2 — external secret storage.
- **Ch 12**: rule 5.4.1 — the integration patterns (CSI driver, sidecar) that deliver Secrets as files.
- **NIST 800-37 / 800-53, CIS Controls v8, OpenSCAP, ENISA supply-chain guidance** — the external standards referenced.
