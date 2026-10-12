# Chapter 22: Never the End

## Core Idea

Wrap-up and next-steps chapter. Not a technical chapter in the traditional sense — it surveys topics the book intentionally skipped, gives guidance on choosing a Kubernetes platform, explains how the Kubernetes project itself is governed, and points to community resources. Content is deliberately light; no new labs or hands-on exercises.

---

## Key Concepts

### Quality of Service (QoS) Classes

Skipped from Chapter 12. Kubernetes assigns every Pod one of three QoS classes based on how its resource requests and limits are specified. These classes determine eviction priority when a node is under memory pressure.

| Class | Condition | Eviction Priority |
|---|---|---|
| **BestEffort** | No requests or limits set on any container | Evicted first |
| **Burstable** | Requests set but limits differ from requests (or only one is set) | Evicted second |
| **Guaranteed** | Requests == limits for every container (CPU and memory) | Evicted last |

### Other Skipped Concepts (brief definitions)

- **Kustomize** — tool for layering YAML overrides across environments without full Helm templating; produces environment-specific manifests from a base + overlays.
- **Service Topology** — extension to Service routing that prefers Pods on the same node or region as the caller, reducing network latency.
- **Projected Volumes** — merge multiple ConfigMaps and Secrets into a single directory mount inside a container.
- **Ephemeral Containers** — temporary containers injected into a running Pod for live debugging, sharing the Pod's network and optionally its volumes/processes.
- **Pod Disruption Budgets (PDBs)** — separate objects that guarantee a minimum number of Pods remain available during voluntary disruptions (e.g., node drain); PDBs block drain if honoring it would violate the budget.
- **GitOps** — operations model where the cluster watches Git repos and auto-deploys new releases; Argo CD is the CNCF project implementing this.
- **Prometheus Operator** — production-grade Prometheus deployment that adds CRDs for Prometheus instances, Alertmanager, scrape targets, and alerting rules.
- **PodSecurityPolicy** — admission controller resource that enforces security rules Pods must satisfy before the cluster will schedule them (note: deprecated in later Kubernetes versions).
- **Service Account Projection** — allows Pod specs to request scoped JWT tokens with custom expiration and audience, useful for limiting token lifetime in init containers.
- **VerticalPodAutoscaler (VPA)** — add-on that adjusts resource requests/limits based on actual usage, complementing the HPA.
- **Cluster Autoscaler** — monitors the scheduler for pending Pods; adds or removes nodes to match demand, typically provided by cloud platforms.
- **API Aggregation** — alternative to CRDs; plugs entirely new API capabilities into the Kubernetes API server via the aggregation layer.
- **KEDA (Kubernetes Event-Driven Autoscaling)** — CNCF project that scales workloads to zero (and back) based on event sources like message queues or Prometheus metrics.
- **Kubernetes Dashboard** — web UI for viewing workloads and their health, and for deploying or editing resources; requires careful RBAC scoping.
- **Special Interest Groups (SIGs)** — public working groups that own different areas of the Kubernetes project; open meetings, dedicated Slack channels, decisions documented on GitHub.

---

## Mental Models

### The "Certified Platform" Filter

When evaluating a Kubernetes distribution or hosted service, start with the CNCF landscape certified list (https://landscape.cncf.io/). A certified platform guarantees conformance with the Kubernetes API. Then assess the four baseline features every production platform should provide: LoadBalancer integration, multiple storage classes, encrypted Secret storage, and cluster autoscaling.

### Managed vs. Self-Managed Trade-off

- **Hosted (cloud)**: Fast setup, native integration, managed nodes and control plane, but customizations via annotations reduce portability.
- **Wrapped on-premises (e.g., OpenShift)**: Additional tooling and abstractions on top of Kubernetes; may add features but reduces portability between platforms.
- **Open source self-hosted**: Maximum control; requires full-time Kubernetes administrators, CKA-level knowledge, and active tracking of the quarterly release cadence.

### Quarterly Release Cadence

Kubernetes publishes a minor version every three months. The three most recent minor versions are supported. Breaking changes occur as alpha/beta API versions are deprecated. Upgrade at least twice a year. Always read the change log before upgrading — API version changes in specs (e.g., `apps/v1beta2` → `apps/v1`) can break existing manifests.

---

## Key Takeaways

1. The official Kubernetes documentation (https://kubernetes.io) and API Reference are the only external resources permitted during CKA/CKAD certification exams — get comfortable with them.
2. Understand QoS classes (BestEffort / Burstable / Guaranteed) and Pod Disruption Budgets before running production workloads — they directly affect eviction behavior and rolling update safety.
3. For CI/CD pipelines, investigate GitOps (Argo CD) as an alternative to push-based deployment — the cluster pulls releases automatically from Git.
4. For platform selection, start from the CNCF certified list, prefer a hosted cloud service unless there are strong on-premises requirements, and be cautious of wrapped distributions that reduce portability.
5. Track the quarterly Kubernetes release schedule; audit change logs for deprecated API versions before upgrading a cluster.
6. Engage with the community via kubernetes.slack.com, SIG meetings on GitHub, and regional meetups or KubeCon/CloudNativeCon — SIGs are open to anyone.
7. If self-hosting a cluster, budget for full-time Kubernetes administrators and consider the CKA exam as a baseline competency bar for the ops team.

---

## Connects To

- **Ch 2**: Kustomize as a lighter alternative to the raw YAML approach introduced there.
- **Ch 3**: Service Topology extends Service load-balancing behavior.
- **Ch 4**: Projected Volumes extend ConfigMap/Secret mounting patterns.
- **Ch 5**: Platform-specific volume types build on PVC/StorageClass concepts.
- **Ch 6**: Affinity/anti-affinity rules (from Ch 19) complement Deployment scaling.
- **Ch 7**: Ephemeral Containers extend the multicontainer Pod model for debugging.
- **Ch 8**: Pod management policy extends StatefulSet behavior.
- **Ch 9**: Pod Disruption Budgets complement rollout/rollback safety.
- **Ch 10**: Advanced Helm templating (conditionals, loops, named templates) extends the Helm introduction.
- **Ch 11**: GitOps / Argo CD extends CI/CD patterns.
- **Ch 12**: QoS classes extend resource limits and self-healing behavior.
- **Ch 13**: kubelet and container runtime log collection extends centralized logging.
- **Ch 14**: Prometheus Operator extends the Prometheus deployment.
- **Ch 15**: Contour/Envoy as an additional ingress controller option.
- **Ch 16**: PodSecurityPolicy extends the security options.
- **Ch 17**: Service account projection and audit2rbac extend RBAC.
- **Ch 18**: RKE and Azure Arc extend multinode cluster management.
- **Ch 19**: VerticalPodAutoscaler and cluster autoscaler extend HPA/scaling.
- **Ch 20**: API aggregation as an alternative to CRDs for extending the API.
- **Ch 21**: KEDA extends serverless/event-driven scaling patterns.
