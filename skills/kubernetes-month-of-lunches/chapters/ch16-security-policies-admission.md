# Chapter 16: Securing Applications with Policies, Contexts, and Admission Control

## Core Idea

Kubernetes is not secure by default. Containers share the host OS kernel, run as root unless told otherwise, and in a default cluster every Pod can reach every other Pod. Hardening requires multiple independent layers: network policies to control traffic, security contexts to constrain what processes can do inside a container, and admission control to enforce those constraints cluster-wide — so nothing reaches production without them.

---

## Frameworks Introduced

- **NetworkPolicy** — firewall-rule objects that restrict ingress and egress traffic between Pods at the port level using label selectors.
  - **What**: A `networking.k8s.io/v1` resource with `podSelector`, `ingress`, and `egress` stanzas.
  - **When**: Any time Pods should not be reachable by every other Pod (i.e., always).
  - **How**: Deploy deny-all defaults, then carve out explicit allow rules per component.
  - **Why-or-failure**: Policies are silently unenforced if the cluster's network plugin does not support them (Docker Desktop default, basic K3s, EKS without a replacement CNI). You must test enforcement explicitly.

- **SecurityContext** — Pod- and container-level fields that control the Linux user, group, kernel capabilities, privilege escalation, and filesystem mutability.
  - **What**: `securityContext` blocks at `spec` (Pod-wide) and `spec.containers[].securityContext` (per-container).
  - **When**: Every workload; start with `runAsNonRoot`, then tighten with `capabilities` and `readOnlyRootFilesystem`.
  - **How**: Add incrementally; run tests after each tightening step because some apps need root or specific capabilities.
  - **Why-or-failure**: A container running as root inside the cluster gives an attacker host-level access if exploited; the Kubernetes API token is mounted by default and can authenticate API calls even for non-root processes.

- **Admission Webhooks (ValidatingAdmissionWebhook / MutatingAdmissionWebhook)** — cluster-level hooks that intercept object creation and update events, calling out to a custom HTTPS server to allow, block, or modify the object.
  - **What**: `ValidatingWebhookConfiguration` / `MutatingWebhookConfiguration` objects that point at a webhook service URL.
  - **When**: When you need cluster-wide enforcement of rules that Kubernetes does not natively support.
  - **How**: Deploy a TLS-secured server (inside or outside the cluster), register a configuration object referencing it with a CA bundle, set `rules` for the object types and operations to intercept.
  - **Why-or-failure**: Mutating webhooks can silently transform specs in ways that break apps and are invisible in user-submitted YAML; validating webhooks applied at the Pod level do not block Deployments, only the Pods the controllers try to create.

- **OPA Gatekeeper** — a CNCF project that runs a generic validating webhook and lets you define admission policies as Kubernetes objects (constraint templates + constraints) written in the Rego policy language, without custom webhook code.
  - **What**: A Gatekeeper deployment installs its own webhook server and `ValidatingWebhookConfiguration`; you create `ConstraintTemplate` CRDs with Rego logic, then `Constraint` objects that activate those templates.
  - **When**: Preferred over hand-rolled webhooks when you want discoverable, version-controlled, human-readable policies.
  - **How**: `kubectl apply -f gatekeeper.yaml` → apply template → apply constraint.
  - **Why-or-failure**: Gatekeeper does not have mutation capabilities; constraint failures on controller-created Pods appear in the ReplicaSet description, not at the Deployment level, which can confuse users.

---

## Key Concepts

1. **Flat networking model**: Every Pod can reach every other Pod by IP by default; Services are cluster-wide. NetworkPolicy is the only native mechanism to restrict this.

2. **Network plugin dependency**: NetworkPolicy objects are just data; the CNI plugin enforces them. Calico, Cilium, and Weave enforce policy. Docker Desktop's default network and basic cloud defaults often do not. Test enforcement explicitly.

3. **Ingress vs. egress rules in NetworkPolicy**: `ingress` restricts incoming traffic to the selected Pods; `egress` restricts outgoing traffic. Both support `podSelector` and `namespaceSelector`. A deny-all policy is implicit when any rule is present; only traffic matching a rule is allowed.

4. **Root in containers = root on the host**: Linux containers share the host kernel. If a container runs as UID 0 and an attacker escapes the container namespace, they own the node. `runAsNonRoot: true` and `runAsUser: <non-zero>` mitigate this.

5. **Kubernetes API token auto-mount**: By default, every Pod receives a service account token at `/run/secrets/kubernetes.io/serviceaccount/token` that can authenticate to the Kubernetes API. `automountServiceAccountToken: false` removes this attack surface for apps that do not need it.

6. **Linux capabilities**: The `capabilities` field under a container `securityContext` allows fine-grained control of kernel features beyond the root/non-root split. Dropping all capabilities (`drop: [all]`) then adding back only what is needed is the most restrictive safe posture.

7. **readOnlyRootFilesystem**: Prevents the container process from writing anywhere in the container filesystem. Blocks attackers from downloading scripts or binaries, but many apps need at least a writable `/tmp`; use `emptyDir` volume mounts to supply writable scratch space.

8. **allowPrivilegeEscalation: false**: Blocks `setuid` binaries and `sudo`-style escalation within the container, even if the process starts as a non-root user.

9. **Admission control pipeline**: Every Kubernetes API write (CREATE, UPDATE) passes through built-in admission controllers, then through any registered mutating webhooks (in parallel), then through validating webhooks (in parallel). Any single validating webhook can block the request. Mutating webhooks run first.

10. **OPA Rego policy language**: Rego evaluates structured data against logical rules. A `violation` rule in a constraint template receives `input.review.object` (the incoming spec) and `input.parameters` (values from the constraint); any non-empty `violation` set blocks the object.

---

## Mental Models

**Defense-in-depth rings**: Think of Kubernetes security as concentric rings, not a single wall. The outermost ring is image scanning (known CVEs before the image runs). The next ring is network policy (traffic between Pods). The next is the security context (what the process can do on the OS). The innermost ring is admission control (enforcing the previous two rings cannot be bypassed). Compromise at any one ring is contained by the others.

**SecurityContext is a shrinking privilege envelope**: Start with the widest envelope (everything allowed, root, writable filesystem, all capabilities, API token mounted). Each security context field shrinks the envelope. The goal is to make the envelope exactly large enough for the application to function and no larger. Test after each reduction.

**Admission control as a policy gateway**: Every object create/update goes through a gateway before it lands in etcd. Validating webhooks are bouncers (allow or deny). Mutating webhooks are editors (transform the spec before it is stored). Because mutation happens first, a mutating webhook can bring a spec into compliance; a validating webhook then confirms it is compliant. OPA Gatekeeper is a structured way to configure what the bouncer checks, without writing custom bouncer code.

---

## Anti-patterns

- **Running containers as root**: Default for most base images. Root inside a container is root on the host kernel if the container is escaped. Always set `runAsNonRoot: true` or an explicit `runAsUser` with a non-zero UID.

- **No NetworkPolicy = open cluster network**: Without policies, every Pod can reach every other Pod, the Kubernetes API server, and any service in the cluster. A compromised web front-end can directly query the database, scrape secrets from other namespaces, or call the Kubernetes API with the mounted service account token.

- **Deploying NetworkPolicy on a cluster without a compatible CNI**: The objects are stored and visible in `kubectl get networkpolicy` but have zero effect. Teams believe they are secured when they are not. Always verify enforcement with a live test (curl from a sleep Pod after the policy is applied).

- **Mutating webhooks applied too broadly**: A mutation that sets `runAsNonRoot: true` on every Pod will silently break images built on root-only base images (e.g., official Nginx). Users see a container that never starts and no obvious reason in their own YAML.

- **Validating webhooks applied only at the Pod level**: Deployments and ReplicaSets are created successfully; only when the controller tries to create the Pod does the webhook fire. The user sees a healthy Deployment and ReplicaSet with zero Pods and must `kubectl describe rs` to find the admission error.

- **Leaving `automountServiceAccountToken` at its default (true)**: Every Pod gets an API credential it almost certainly does not need. Explicitly set `automountServiceAccountToken: false` in every Pod spec that does not call the Kubernetes API.

---

## Code Examples

**Pod-level SecurityContext (non-root user, no API token):**
```yaml
spec:
  automountServiceAccountToken: false
  securityContext:
    runAsUser: 65534
    runAsGroup: 3000
```

**Container-level SecurityContext (no privilege escalation, drop all capabilities):**
```yaml
containers:
  - name: app
    securityContext:
      allowPrivilegeEscalation: false
      capabilities:
        drop:
          - all
      readOnlyRootFilesystem: true
```

**NetworkPolicy — restrict ingress to a single labeled Pod source on a named port:**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: apod-api
spec:
  podSelector:
    matchLabels:
      app: apod-api
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: apod-web
      ports:
        - port: api
```

**ValidatingWebhookConfiguration (abridged):**
```yaml
apiVersion: admissionregistration.k8s.io/v1beta1
kind: ValidatingWebhookConfiguration
metadata:
  name: servicetokenpolicy
webhooks:
  - name: servicetokenpolicy.kiamol.net
    rules:
      - operations: ["CREATE", "UPDATE"]
        apiGroups: [""]
        apiVersions: ["v1"]
        resources: ["pods"]
    clientConfig:
      service:
        name: admission-webhook
        namespace: default
        path: "/validate"
      caBundle: <base64-encoded-CA-cert>
```

**OPA Gatekeeper constraint template (Rego — required labels):**
```yaml
violation[{"msg": msg, "details": {"missing_labels": missing}}] {
  provided := {label | input.review.object.metadata.labels[label]}
  required := {label | label := input.parameters.labels[_]}
  missing := required - provided
  count(missing) > 0
  msg := sprintf("you must provide labels: %v", [missing])
}
```

**OPA Gatekeeper constraint (activate the template for Pods):**
```yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: RequiredLabels
metadata:
  name: requiredlabels-app
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Pod"]
  parameters:
    labels: ["app", "version"]
```

---

## Reference Tables

| Layer | Mechanism | Scope | Enforced by | Failure mode if skipped |
|---|---|---|---|---|
| Network traffic | NetworkPolicy | Pod-to-Pod, Pod-to-API | CNI plugin | Any Pod can reach any other Pod or API |
| Process identity | `securityContext.runAsUser` / `runAsNonRoot` | Pod or container | kubelet | Container runs as root; full node risk on escape |
| Kernel capabilities | `securityContext.capabilities` | Container | Linux kernel | Container can perform privileged syscalls |
| Filesystem writes | `readOnlyRootFilesystem` | Container | Linux kernel | Attacker can write scripts/binaries inside container |
| API credential | `automountServiceAccountToken: false` | Pod | API server | Mounted token allows unauthenticated Kubernetes API calls |
| Admission gate (custom code) | ValidatingAdmissionWebhook | Any object type/operation | Webhook server | Non-compliant specs reach the cluster |
| Admission gate (mutation) | MutatingAdmissionWebhook | Any object type/operation | Webhook server | Specs missing required fields are not corrected at gate |
| Admission gate (policy as code) | OPA Gatekeeper (ConstraintTemplate + Constraint) | Any object type/operation | Gatekeeper ValidatingWebhook | Policies not enforced; also requires testing Pod-vs-Deployment level |

---

## Worked Example

**Scenario**: Harden the APOD (Astronomy Picture of the Day) application — a multi-component app with a web frontend, API backend, and access-log component — so that lateral movement is blocked, container privileges are minimized, and cluster-wide admission policies prevent future regressions.

### Step 1 — Diagnose the defaults

Deploy the app without any hardening and probe from a sleep Pod:

```bash
kubectl exec deploy/sleep -- curl -s http://apod-api/image      # succeeds — open network
kubectl exec deploy/apod-web -- whoami                           # root
kubectl exec deploy/apod-web -- cat /run/secrets/kubernetes.io/serviceaccount/token  # token present
```

Every component is accessible from every Pod. The web container runs as root with a mounted API credential.

### Step 2 — Lock the network with NetworkPolicy

Apply a policy so only the web Pod can reach the API Pod on the `api` named port:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: apod-api
spec:
  podSelector:
    matchLabels:
      app: apod-api
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: apod-web
      ports:
        - port: api
```

Verify: `kubectl exec deploy/sleep -- curl http://apod-api/image` now times out (on a Calico or equivalent CNI). The web Pod can still reach the API.

### Step 3 — Harden the Pod with securityContext

Update the web Deployment spec:

```yaml
spec:
  automountServiceAccountToken: false
  securityContext:
    runAsUser: 65534
    runAsGroup: 3000
  containers:
    - name: web
      securityContext:
        allowPrivilegeEscalation: false
        capabilities:
          drop:
            - all
        readOnlyRootFilesystem: true
```

Note: the app must switch its listening port from 80 (requires root) to 5001 via an environment variable. The Service port mapping hides this from consumers. Verify the app still serves traffic and `whoami` returns a non-root username.

### Step 4 — Enforce via OPA Gatekeeper

Deploy Gatekeeper, then apply constraint templates and constraints that mandate:
- `app` and `version` labels on all Pods
- Container images from an approved repository only
- Resource `limits` set on all containers
- Readiness and liveness probes defined

Attempt to deploy a non-compliant spec: Gatekeeper blocks all violations in a single response from the Rego policy, listing every missing field. Update the spec to include all required fields and redeploy — Gatekeeper permits it and the Pod starts.

Result: The network is segmented, the container runs with minimal OS privilege, the API token is absent, and no future deployment can bypass these controls without meeting the Gatekeeper constraints.

---

## Key Takeaways

1. Kubernetes has no meaningful security enabled by default; every hardening feature must be explicitly configured.
2. NetworkPolicy objects are inert without a CNI that enforces them; always test with a real curl from a sleep Pod after applying a policy.
3. `runAsNonRoot` and `automountServiceAccountToken: false` are the two highest-value, lowest-effort security context settings to apply to every workload.
4. Admission webhooks (validating and mutating) enforce rules cluster-wide but carry risk: mutating webhooks can silently break apps, and both types target Pods, not Deployments, creating confusing failure UX.
5. OPA Gatekeeper makes admission policies discoverable and maintainable as YAML objects; Rego policies are readable compared to embedded webhook logic, and the full violation list is returned in a single response.
6. Security in depth means multiple independent layers: image scanning → network policy → security context → admission control → RBAC (chapter 17) → runtime monitoring (Falco). No single layer is sufficient.
7. Adopt security incrementally: start with security contexts, add network policies once your CNI supports enforcement, then introduce admission control once your policy rules are stable.

---

## Connects To

- **Chapter 15** — Ingress controls external HTTP traffic; NetworkPolicy controls internal Pod-to-Pod traffic. Both are needed.
- **Chapter 12** — ResourceQuota is a built-in admission controller; this chapter extends that model to custom validating and mutating webhooks.
- **Chapter 17** — RBAC (Role-Based Access Control) is the next security layer: restricting what Kubernetes API operations users and service accounts are permitted to perform, which complements the run-time controls here.
- **Chapter 20** — OPA Gatekeeper uses CustomResourceDefinitions (CRDs) to register ConstraintTemplate and Constraint as native Kubernetes object types; CRDs are covered in depth there.
- **Calico / Cilium / Weave** — Third-party CNI plugins required for NetworkPolicy enforcement; selection and installation is a cluster-setup decision that must be made before policies are deployed.
- **OPA Gatekeeper policy library** — Community-maintained Rego policies covering the controls introduced in this chapter: https://github.com/open-policy-agent/gatekeeper-library
- **Network policy recipes** — Ahmet Alp Balkan's collection of ready-to-use NetworkPolicy patterns: https://github.com/ahmetb/kubernetes-network-policy-recipes
