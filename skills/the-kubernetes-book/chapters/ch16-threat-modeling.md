# Chapter 16: Threat modeling Kubernetes

## Core Idea
Threat modeling is the process of identifying vulnerabilities so you can put measures in place to prevent and mitigate them. This chapter applies the **STRIDE** model to Kubernetes, walking each of its six threat categories and surveying ways each applies to a cluster. No model guarantees full coverage; the goal is to seed ideas. Recurring themes: defense in depth, least privilege, and the fact that one threat often enables another.

## Frameworks Introduced
**STRIDE** — six potential threat categories:
- **Spoofing** — pretending to be somebody else to gain extra privileges. K8s counter: mTLS between components, ServiceAccount identity for Pods, trusted CAs.
- **Tampering** — maliciously changing something to cause denial of service or elevation of privilege. K8s counter: TLS integrity in transit, restricted/audited access at rest, read-only filesystems.
- **Repudiation** — creating doubt about an action; non-repudiation proves who/what/when/where/why/how. K8s counter: API server audit logs + node/runtime audit daemons, centralized secure log store.
- **Information disclosure** — leaking sensitive data. K8s counter: protect the cluster store (etcd), encrypt Secrets, store KEKs externally (HSM/KMS).
- **Denial of service** — making something unavailable. K8s counter: HA control plane across AZs, resource limits, ResourceQuota, podPidsLimit, NetworkPolicies.
- **Elevation of privilege** — gaining higher access than granted. K8s counter: RBAC/Node/Webhook authorizers, non-root, capability dropping, seccomp, allowPrivilegeEscalation=false, PSS/PSA.

## Key Concepts
1. **mTLS between components** — all components authenticate via cryptographically signed certs; K8s auto-rotates them. Security is only as strong as the issuing CA.
2. **CA hygiene** — auto-generated self-signed CA is "better than nothing" but not production-grade alone. Use two trusted key pairs: internal CA for cluster components, trusted 3rd-party CA(s) for external systems. Never trust the internal CA outside the cluster.
3. **ServiceAccount tokens** — auto-mounted into every Pod as a Secret, grants API server access. Most Pods don't need it, so set `automountServiceAccountToken: false`. When needed, scope with `expirationSeconds` and `audience` via a projected volume.
4. **In transit vs at rest** — tampering happens on the network (mitigate with TLS integrity) or in memory/disk (mitigate with access restriction, SHA-2 checksum verification, SSH-only bootstrap, audit daemons).
5. **Read-only filesystems** — `readOnlyRootFilesystem: true` and `allowedHostPaths` enforce filesystem immutability for running Pods.
6. **Cluster store as prime target** — etcd holds network/storage config, passwords, the cluster CA. Encrypt Secrets (since 1.7, not default); the DEK lives on the same node, so node access bypasses it — store KEKs externally (HSM/KMS, beta since 1.11).
7. **DoS resource controls** — Memory/CPU/Storage limits, `ResourceQuota` (cap object counts per Namespace), `podPidsLimit` (defends against fork bombs by capping a Pod's processes).
8. **Authorization modes** — run multiple authorizers simultaneously; RBAC + Node is common. Webhook offloads to an external policy engine but creates a single point of failure.
9. **Capabilities** — root's power is a set of 30+ granular privileges (e.g. SYS_TIME, NET_ADMIN). Drop all, then add back the minimum the app needs (`securityContext.capabilities.add`).
10. **Seccomp** — filters syscalls (GA in 1.19). Profiles: Non-blocking (records for building a profile), Blocking (denies all), Runtime Default, Custom (least privilege, preferred).

## Mental Models
- **Defense in depth** — combine NetworkPolicies, mTLS, token auth, app-layer least-privilege authorization; an attacker must defeat all layers.
- **Don't lock the house and leave the keys in the door** — encrypting Secrets/Volumes/ConfigMaps is worthless if the decryption keys are stored insecurely.
- **One threat begets another** — tampering can cause DoS or elevation of privilege; spoofing can drive DoS by overloading the API server.
- **Tamper-evidence over tamper-prevention** — when you can't stop tampering, make it obvious (like tamper-proof drug seals → audit logging).
- **Least privilege everywhere** — capabilities, syscalls, RBAC, ServiceAccount tokens: grant only the exact set required.

## Anti-patterns
- Running application processes as root (UID 0) — container root can sometimes equal host root.
- Sharing the same `runAsUser` UID across unrelated Pods — shared security context risks data corruption and cross-tampering.
- Letting child processes claim more privileges than their parent (set `allowPrivilegeEscalation: false`).
- Trusting the internal K8s CA outside the cluster.
- Leaving any Namespace with no Pod Security configuration.
- Running etcd co-located with the control plane for large production clusters (etcd is the common choking point).
- Relying solely on container-runtime default capabilities/seccomp profiles in production.

## Code Examples
- Disable token automount: `automountServiceAccountToken: false` in Pod spec.
- Scoped token: projected volume `serviceAccountToken` with `expirationSeconds: 3600` and `audience: vault`.
- Audit a binary (auditd): `auditctl -w /usr/bin/docker -p wxa -k audit-docker`.
- Read-only FS: `securityContext.readOnlyRootFilesystem: true` + `allowedHostPaths` with `pathPrefix` / `readOnly: true`.
- Non-root: `securityContext.runAsUser: 1000` (Pod-level), overridable per container.
- Add capabilities: `securityContext.capabilities.add: ["NET_ADMIN", "CHOWN"]`.
- ResourceQuota: `kind: ResourceQuota` with `spec.hard.pods: "100"`.
- PSA label: `pod-security.kubernetes.io/enforce=baseline` (format `<prefix>/<mode>: <policy>`).
- Dry-run a policy: `kubectl label --dry-run=server --overwrite ns ... pod-security.kubernetes.io/enforce=restricted`.

## Reference Tables

| STRIDE category | Kubernetes example threat | Mitigation |
|---|---|---|
| **Spoofing** | One component or Pod impersonates another to gain privileges; spoofed API server identity | mTLS with rotated certs; secure & isolated CA; two trusted key pairs (internal CA + 3rd-party CA); ServiceAccount tokens, `automountServiceAccountToken: false` when unneeded |
| **Tampering** | Modifying etcd, config files, runtime/K8s binaries, container images; tampering a running Pod | TLS integrity in transit; restrict/audit access at rest; SHA-2 checksums; SSH-only bootstrap; `readOnlyRootFilesystem: true`; auditd watches on binaries |
| **Repudiation** | No proof of who changed a cluster resource or started a container | Enable API server audit logging; collect runtime/kubelet/app/firewall logs; DaemonSet log shipper to a secure central store; auditd for file writes |
| **Information disclosure** | etcd leaks passwords/CA; Secrets exposed via node access | Limit/audit cluster-store node access; encrypt Secrets; store KEKs in HSM/KMS; use Secrets for decryption keys (not env/plain text) |
| **Denial of service** | Overloading the API server; fork bomb in a Pod; etcd overload | HA control plane across AZs; Memory/CPU/Storage limits; `ResourceQuota`; `podPidsLimit`; NetworkPolicies; HA 3/5-node isolated etcd; monitoring/alerting on sane thresholds; firewalls |
| **Elevation of privilege** | Container escalates to host root; child process gains extra privileges | RBAC + Node (+ Webhook) authorizers; `runAsUser` non-root; drop capabilities; seccomp custom profile; `allowPrivilegeEscalation: false`; PSS/PSA |

### Pod Security Standards (PSS) — three community-maintained policies
| Policy | Description |
|---|---|
| **Privileged** | Wide-open, allow-all |
| **Baseline** | Sensible defaults; more secure than privileged, less than restricted |
| **Restricted** | Gold standard, current best practices; many Pods fail its strict requirements |

You cannot modify, import, or create your own PSS policies.

### Pod Security Admission (PSA) — Namespace-level validating admission controller, three modes
| Mode | Behavior |
|---|---|
| **Warn** | Allows violating Pods, issues user-facing warning |
| **Audit** | Allows violating Pods, logs an audit event |
| **Enforce** | Rejects violating Pods at creation |

PSA cannot modify Pods and cannot affect already-running Pods.

## Worked Example: PSA enforcing the baseline policy (Elevation of privilege)
1. Create Namespace: `kubectl create ns psa-test`.
2. Enforce baseline: `kubectl label --overwrite ns psa-test pod-security.kubernetes.io/enforce=baseline`; verify with `kubectl describe ns psa-test`.
3. Deploy a Pod with `securityContext.privileged: true` → rejected: `Error from server (Forbidden): ... violates PodSecurity "baseline:latest": privileged ... must not set securityContext.privileged=true`.
4. Set `privileged: false`, re-apply → `pod/psa-pod created`.
5. Dry-run the stricter policy: `kubectl label --dry-run=server --overwrite ns psa-test pod-security.kubernetes.io/enforce=restricted` → warns the existing Pod fails 4 checks: `allowPrivilegeEscalation != false`, unrestricted capabilities, `runAsNonRoot != true`, fails `seccompProfile`.
6. Apply restricted for real → same warnings, but the **already-running Pod keeps running** (`STATUS Running`) because PSA only acts on Pod creation/modification.
7. Layer modes: enforce baseline while warning + auditing restricted to prepare for migration:
   `pod-security.kubernetes.io/enforce=baseline`, `.../warn=restricted`, `.../audit=restricted`.

This demonstrates PSA's gradual-rollout pattern: start with warn/audit on every Namespace, then promote to enforce.

## Key Takeaways
1. Apply STRIDE systematically — Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege — to find and mitigate cluster threats.
2. mTLS and audit logging are foundational; their value collapses if the CA or the central log store is compromised.
3. The cluster store (etcd) is the highest-value target — isolate, encrypt, and store key encryption keys (KEKs) externally.
4. Enforce least privilege at every layer: non-root users, dropped capabilities, seccomp custom profiles, `allowPrivilegeEscalation: false`, scoped ServiceAccount tokens, tight RBAC.
5. Use resource controls (limits, ResourceQuota, podPidsLimit) and HA across AZs to blunt DoS.
6. PSS + PSA are the preferred built-in way to standardize Pod security; roll out via warn/audit before enforce. For more flexibility use OPA Gatekeeper, Kubewarden, or Kyverno.
7. Defense in depth wins — one mitigation is rarely enough, and one threat often enables another.

## Connects To
- **Ch15 (RBAC and API security)** — authentication, authorization, mTLS foundations referenced throughout.
- **Ch17 (Real-world Kubernetes security / best practices)** — production lessons and hardening.
- **Secrets, ConfigMaps, Persistent Volumes** chapters — data-at-rest protection.
- **Networking** — NetworkPolicies for DoS and lateral-movement defense.
- External: Cloud Native Security Whitepaper (CNCF), NCC Group K8s 1.24 security audit (2023), confidential computing for data-in-use.
