# Chapter 17: Real-world Kubernetes security

## Core Idea
Real-world Kubernetes security is a layered, defense-in-depth practice seen from a security architect's high-level view (not cookbook solutions). It spans four domains: securing the software delivery pipeline (supply chain), workload isolation, identity and access management (IAM), and security monitoring and auditing. The recurring theme: no single control is enough, and no system is 100% secure — plan for breaches and stack controls across the lifecycle.

## Frameworks Introduced

### The four-pillar security model
1. **Security in the software delivery pipeline** — supply chain: registries, base images, scanning, signing, config-as-code, image promotion.
2. **Workload isolation** — cluster → node → runtime → network layers.
3. **Identity and access management (IAM)** — RBAC, SSH control, MFA.
4. **Security monitoring and auditing** — recognize breaches + build a non-repudiable timeline.

### Workload isolation layers (strongest to weakest)
- **Cluster** (separate clusters = only true hard boundary)
- **Node** (ring-fenced node subsets)
- **Runtime** (VMs, namespaced containers, runtime classes, Wasm)
- **Network** (CNI, firewalls, NetworkPolicy)

## Key Concepts
1. **Supply chain security** — secure the path from developer laptop to production: registries, approved base images, scanning, signing, IaC review.
2. **Image registries/repositories** — prefer private registries inside your firewall; official images > community images; only host approved/vetted images.
3. **Approved base images** — small set of hardened, vetted bases (e.g., custom Alpine). Benefits: known patches, standardized audit, less sprawl, simpler testing/updates/troubleshooting.
4. **Image scanning (vulnerability scanning)** — scan at binary level against CVE databases; integrate into CI/CD; auto-fail/quarantine builds on critical CVEs; good tools allow false-positive customization.
5. **Configuration as code / policy as code** — scan Dockerfiles, YAML, Helm charts (IBM embedded-TLS-key incident). Less adopted than app-code scanning but critical.
6. **Image signing (provenance/integrity)** — devs cryptographically sign; consumers verify on pull/run. Implemented by the container runtime. Enforce enterprise-wide signing policies, not per-user.
7. **Soft vs hard multi-tenancy** — soft = trusted workloads sharing infra (Namespaces fine); hard = untrusted/hostile workloads (NOT possible in Kubernetes — need separate clusters).
8. **Runtime isolation classes** — namespaced containers (shared kernel, weak) vs VMs (dedicated kernel, strong) vs gVisor/Kata via RuntimeClasses vs Wasm (deny-by-default host).
9. **CNI networking — overlay vs BGP** — overlay (VXLAN) encapsulates packets, hiding src/dst IPs from firewalls; BGP doesn't encapsulate, simpler for firewalls.
10. **IP churn** — Pod IPs are dynamic/recycled; associate with Pod IDs / Service aliases / container IDs for packet capture and forensics.

## Mental Models
- **Defense in depth** — stack controls (scanning + no-root + SELinux) so one missed control isn't fatal. CVE-2019-5736 would have been stopped by any one of three layers.
- **Shift-left** — push security into the pipeline: scan and sign before production, fail builds early, quarantine bad images.
- **Namespaces are organizational, not security boundaries** — use them for limits/quotas/RBAC grouping, never to isolate hostile workloads.
- **VMs always win on isolation** — when strong isolation is required, hardware-enforced kernel separation beats kernel-shared containers.
- **Plan for breach** — assume compromise; invest in auditing to recognize it and build a non-repudiable timeline (what/how/when/who).
- **Crawl, walk, run migration** — don't change an app's security posture during migration; improve it only afterward to avoid misdiagnosing issues.

## Anti-patterns
- Trusting images pulled from public registries without due diligence.
- Running hostile/untrusted workloads on the same cluster (relying on Namespaces as a security boundary).
- Treating namespaced containers as a strong isolation boundary.
- Skipping scanning of config files (Dockerfiles/YAML/Helm) while scanning app code.
- Leaving image signing to individual users instead of enforced policy.
- Running container processes as root / disabling SELinux.
- Granting broad SSH access to control plane nodes without MFA and logging.
- Choosing an overlay (encapsulating) pod network when your firewalls can't inspect encapsulated packets.
- Going live in production without auditing and monitoring.

## Reference Tables

### Pipeline controls (build → deploy → runtime)
| Lifecycle stage | Controls |
|---|---|
| Build | Approved base images; scan app code; scan Dockerfiles/IaC (policy-as-code); sign images; restrict push to build nodes/automation only |
| Deploy/Promote | Vulnerability scan gate (fail/quarantine on critical CVE); verify signatures (enforced policy); RBAC on repos; promote across dev→test→prod |
| Runtime | RuntimeClasses (gVisor/Kata); SELinux/AppArmor/seccomp/capabilities/user-namespaces; no-root policies; NetworkPolicy/firewalls; runtime monitoring |

### Image promotion workflow checklist
1. Policies forcing signed images
2. Network rules restricting push/pull nodes
3. RBAC protecting repositories
4. Approved base images
5. Vulnerability scanning
6. Promote/quarantine based on scan results
7. Review/scan IaC config files

### Workload isolation options
| Option | Isolation | Trade-off |
|---|---|---|
| Virtual machines | Excellent (dedicated kernel) | Slow, resource-heavy |
| Namespaced containers | Weak (shared kernel) | Fast/light; needs hardening |
| Container-per-VM | Strong | Loses container appeal; unpopular |
| RuntimeClasses (gVisor/Kata) | Strong for targeted workloads | Run all as containers, target sensitive ones |
| Wasm containers | Strong (deny-by-default host) | OCI packaging, Wasm runtime |

### Network: overlay vs BGP
| | Overlay (VXLAN) | BGP |
|---|---|---|
| Encapsulation | Yes — hides src/dst IPs | No |
| Firewall friendliness | Hard (needs deep packet inspection) | Easy |

### Security alert triggers
| Event | Why significant |
|---|---|
| Privileged Pod created by a human | Usually automation-only; can gain node root |
| Exec session by a human | Shell access; investigate non-troubleshooting use |
| Control plane access attempt from internet | Should be blocked; success = misconfiguration |

## Worked Example: Harden one workload
**Goal:** deploy a `payments` service with a signed image, restricted Pod security, and a NetworkPolicy.

1. **Signed + scanned image** — build on an approved Alpine base, scan in CI (fail on critical CVE), cryptographically sign, and enforce signature verification via admission policy on pull.
2. **Restricted Pod security** — drop root and capabilities, target a stronger RuntimeClass if isolation demands it:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: payments
spec:
  runtimeClassName: gvisor          # stronger runtime isolation
  securityContext:
    runAsNonRoot: true
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: app
    image: registry.internal/payments@sha256:<digest>   # signed, immutable digest
    securityContext:
      allowPrivilegeEscalation: false
      capabilities:
        drop: ["ALL"]
```
3. **NetworkPolicy** — default-deny posture, then allow only required flows:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: payments-allow
  namespace: prod
spec:
  podSelector:
    matchLabels:
      app: payments
  policyTypes: ["Ingress", "Egress"]
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: web-frontend
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: db
    ports:
    - protocol: TCP
      port: 5432
```
Result: a least-privilege workload — verified provenance, non-root restricted runtime, and explicitly scoped network reachability.

## Key Takeaways
1. Secure the supply chain end-to-end: approved base images, vulnerability scanning, config/IaC scanning, and enforced image signing/verification.
2. Kubernetes has no secure multi-tenancy — Namespaces are not security boundaries; hostile/strongly-isolated workloads need separate clusters.
3. Choose isolation per workload: VMs and RuntimeClasses (gVisor/Kata) for strong isolation; harden namespaced containers with SELinux/seccomp/AppArmor.
4. Pick a CNI (overlay vs BGP) that your firewalls can actually inspect; combine physical and host-based firewalls.
5. Reuse existing IAM via RBAC; lock down and MFA-protect SSH to nodes/control plane; log all SSH activity.
6. Assume breach — robust auditing/monitoring (kube-bench/CIS baseline, lifecycle events, app logs, alerting) is mandatory before production.
7. Migrate apps crawl→walk→run; never change security posture during the migration itself.

## Connects To
- **Ch16 (Threat modeling / STRIDE)** — this chapter operationalizes the threats STRIDE surfaces.
- **Ch9 (Wasm)** — Wasm containers as an isolation/runtime class.
- **RBAC & API server auth** — admission controllers (validate/mutate, e.g. OPA/Gatekeeper, Kyverno) run after authn/authz to enforce policy (signing, no-root, Pod Security Standards).
- **CNI / Services / Ingress** — NetworkPolicy and pod-network choice build on the cluster networking model.
- **Secrets** — store sensitive data outside images, injected at runtime; protect with least privilege.
