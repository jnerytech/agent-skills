# Glossary — The Kubernetes Book (2024), Nigel Poulton

**Admission control** — The third request-pipeline stage that enforces policy on state-changing requests via mutating (modify) and validating (accept/reject) controllers (Ch 14).
**Affinity / anti-affinity** — Scheduling rules that attract or repel Pods to/from nodes or other Pods during the filtering phase (Ch 2).
**Alpha** — Earliest API maturity level; experimental, may be dropped without warning, often disabled by default (Ch 15).
**API group (core)** — Mature early resources (Pods, Nodes, Services, Secrets) served under `/api/v1`, shown as `""`; frozen to new resources (Ch 15).
**API group (named)** — Sub-groups under `/apis/{group}/{version}` (e.g. `apps`, `networking.k8s.io`) holding all new resources (Ch 15).
**API server** — The front end of Kubernetes; a RESTful HTTPS service all clients pass through for authN/authZ before persistence (Ch 2, Ch 15).
**Authentication (authN)** — First pipeline stage proving identity by verifying request credentials; failure returns HTTP 401 (Ch 14).
**Authorization (authZ)** — Second pipeline stage deciding if an identity may act on a resource; failure returns 403 (Ch 14).
**AutoPilot** — A GKE cluster mode that does not support all book examples; use Standard instead (Ch 3).
**Beta** — Pre-release API maturity level; enabled by default but small changes still expected before GA (Ch 15).
**BGP** — A non-encapsulating CNI networking model, simpler for firewalls than overlay/VXLAN (Ch 17).
**Borg / Omega** — Google's in-house orchestrators sharing heritage with Kubernetes but not its source (Ch 1).
**Capabilities** — The ~30+ granular privileges making up root; drop all and add back only what the app needs (Ch 16).
**ClusterIP** — Default Service type giving a virtual internal-only IP plus DNS name, reachable only inside the cluster (Ch 7, Ch 10).
**ClusterRole** — Cluster-scoped RBAC object defining a reusable permission set across all Namespaces (Ch 14).
**ClusterRoleBinding** — Cluster-scoped object binding a ClusterRole to subjects across all Namespaces (Ch 14).
**Cloud-native** — An app with auto-scaling, self-healing, and automated update/rollback behaviors — not merely an app running in the cloud (Ch 1).
**Cluster** — One or more nodes (control plane + workers) supplying CPU/memory/resources to apps (Ch 2).
**Cluster store (etcd)** — The only stateful control-plane component; a distributed DB (odd replicas, RAFT) holding desired state as the record of intent (Ch 2, Ch 16).
**CNCF** — Cloud Native Computing Foundation; owns Kubernetes under Apache 2.0 (Ch 1).
**CNI plugin** — Implements the flat pod network connecting all Pods (e.g. Cilium); chosen at cluster build time (Ch 4, Ch 17).
**ConfigMap (CM)** — Core `v1` object storing non-sensitive config as key-value pairs (max 1MiB), injected into Pods at run time (Ch 12).
**containerd** — The default K8s-optimized container runtime ("container dee") in most new clusters (Ch 1, Ch 2).
**Containerization** — Packaging an app plus dependencies as an image and running it as a container (Ch 1).
**Container Runtime Interface (CRI)** — The pluggable interface decoupling Kubernetes from any specific low-level runtime (Ch 1).
**Context (kubectl)** — A named bundle of cluster + user credentials telling kubectl which cluster to target and how to authenticate (Ch 3).
**Control plane node** — Linux node running all control-plane services (API server, scheduler, controllers, store); 1 for labs, 3/5 for HA (Ch 2).
**Controller** — A background watch loop that reconciles observed state toward desired state, delivering self-healing/scaling/rollouts (Ch 2).
**CoreDNS** — The cluster DNS implementation serving as the service registry, running as a `coredns` Deployment in `kube-system` (Ch 10).
**CSI (Container Storage Interface)** — Industry-standard interface letting providers ship out-of-tree storage drivers usable by any orchestrator (Ch 11).
**CustomResourceDefinition (CRD)** — Extends the API with custom resources that look native, paired with a custom controller to act on them (Ch 15).
**Declarative model** — Describing desired end-state in YAML and letting controllers reconcile it; preferred over the imperative model (Ch 2).
**Default backend** — Where an Ingress controller routes traffic that matches no host/path rule (Ch 8).
**Deployment** — `apps/v1` controller wrapping Pods for stateless apps, adding self-healing, scaling, rolling updates, and rollbacks (Ch 6).
**Desired state** — What you want, declared in YAML and stored as the record of intent (Ch 2, Ch 6).
**EndpointSlice** — Object auto-created per Service tracking the IP:port of healthy matching Pods; scales better than legacy Endpoints (Ch 7, Ch 10).
**FQDN** — Fully qualified DNS name `<object>.<namespace>.svc.cluster.local` resolving a Service in any Namespace (Ch 10).
**GA (stable)** — Production-ready API maturity level with a firm deprecation policy (≥12 months / 3 releases) (Ch 15).
**Governing Service** — The headless Service named in a StatefulSet's `spec.serviceName` owning the per-Pod DNS subdomain (Ch 13).
**GVR** — Group, Version, Resource; the structure of Kubernetes REST paths (Ch 15).
**Headless Service** — A Service with `clusterIP: None` that creates per-Pod DNS records for direct connections, no load balancing (Ch 13).
**Horizontal Pod Autoscaler (HPA)** — Default autoscaler that adds/removes Pods based on load (Ch 6).
**Host-based routing** — Ingress routing on the HTTP hostname (e.g. `shield.mcu.com` → svc-shield) (Ch 8).
**Hosted Kubernetes** — A cloud-managed cluster (GKE, EKS, AKS) with managed/hidden control plane and itemized billing (Ch 3).
**Imperative model** — Issuing step-by-step commands without a stored desired state; lacks self-healing (Ch 2, Ch 6).
**Immutability** — Running Pods cannot be modified; every update is a delete-and-replace (Ch 2, Ch 4).
**Ingress** — `networking.k8s.io/v1` object exposing many ClusterIP Services through one cloud load balancer via L7 host/path routing (Ch 8).
**Ingress controller** — The component (e.g. NGINX) that watches Ingress objects and enforces their rules; not built in (Ch 8).
**IngressClass** — Object binding Ingress objects to a specific controller via `spec.ingressClassName`, enabling multiple controllers (Ch 8).
**Init container** — A container under `spec.initContainers` guaranteed to run once and complete before the main containers start (Ch 4).
**K8s** — Common shorthand for Kubernetes; the 8 replaces the eight letters between K and s (Ch 1).
**KEK / DEK** — Key Encryption Key / Data Encryption Key; store KEKs externally (HSM/KMS) since the DEK lives on the node (Ch 16).
**kubeconfig** — The `~/.kube/config` file holding clusters, users, contexts, and current-context that kubectl reads (Ch 3, Ch 14).
**kubectl** — The CLI that converts user commands into REST requests to the API server (Ch 3).
**kubelet** — The main worker-node agent that watches the API server and instructs the runtime to execute tasks (Ch 2).
**kube-proxy** — Per-node component writing kernel rules that trap virtual ClusterIP traffic and redirect it to healthy Pod IPs (Ch 2, Ch 10).
**Label selector** — The mechanism Deployments and Services use to loosely couple to Pods by matching labels (Ch 6, Ch 7).
**Least privilege / deny-by-default** — Lock everything down and grant only required access; K8s RBAC is allow-only (Ch 14, Ch 16).
**LoadBalancer** — Service type provisioning a cloud load balancer (auto-creating NodePort + ClusterIP) for internet-facing access (Ch 7).
**maxSurge / maxUnavailable** — Rolling-update fields capping Pods above/below desired count during a rollout (Ch 6).
**Microservices** — An app built from many small, independent, separately deployed services (Ch 1).
**mTLS** — Mutual TLS authenticating components with rotated, CA-signed certs (Ch 16).
**Mortal (Pod)** — A Pod is never restarted; it is replaced by a new Pod with a new ID and IP (Ch 2, Ch 4).
**Namespace** — A virtual cluster providing soft isolation for soft multi-tenancy; not a security boundary (Ch 5, Ch 17).
**NetworkPolicy** — `networking.k8s.io/v1` object scoping Pod ingress/egress for default-deny, least-privilege networking (Ch 16, Ch 17).
**NodePort** — Service type exposing a port (30000–32767) on every node that forwards to a ClusterIP (Ch 7).
**Observed state** — What you actually have right now (a.k.a. actual/current state) (Ch 2, Ch 6).
**OCI** — Open Container Initiative; image/container standards Docker, containerd, and K8s all implement (Ch 1, Ch 9).
**Orchestrator** — A platform that deploys apps and dynamically reacts to change (scale, self-heal, rollout) with minimal human input (Ch 1).
**Ordinal index** — The zero-based integer in a StatefulSet Pod name driving ordered startup, scaling, and PVC binding (Ch 13).
**Overlay (VXLAN)** — A CNI model encapsulating packets, hiding src/dst IPs and complicating firewall inspection (Ch 17).
**Path-based routing** — Ingress routing on the URL path (e.g. `mcu.com/shield` → svc-shield) (Ch 8).
**pause container** — The infra container holding a Pod's namespaces so its containers can share them (Ch 4).
**PersistentVolume (PV)** — Object representing/mapping to an external storage volume on Kubernetes (Ch 11).
**PersistentVolumeClaim (PVC)** — A request granting an app access to a PV (Ch 11).
**Pod** — The atomic unit of scheduling; a shared execution environment wrapping one or more containers (Ch 2, Ch 4).
**pod-template-hash** — System label hashing the Pod template, wiring Deployment→ReplicaSet→Pods; never modify it (Ch 6).
**podPidsLimit** — Caps a Pod's process count to defend against fork bombs (Ch 16).
**Pod Security Admission (PSA)** — Namespace-level validating admission controller applying PSS in warn/audit/enforce modes (Ch 16).
**Pod Security Standards (PSS)** — Three fixed community policies: Privileged, Baseline, Restricted (Ch 16).
**Protobuf** — A faster/smaller serialization format used internally; JSON serves external clients (Ch 15).
**RBAC** — Role-Based Access Control; the common authZ module about users (subjects), verbs, and resources (Ch 14).
**Reclaim policy** — PV data-safety setting: `Delete` (default, destructive) or `Retain` (keeps volume, manual cleanup) (Ch 11).
**Reconciliation** — The controller loop driving observed state back to desired state (Ch 2, Ch 6).
**ReplicaSet** — The controller a Deployment manages that actually creates, counts, and terminates Pods (Ch 6).
**Resource requests vs limits** — Requests are scheduling minimums (reserved); limits are maximums (capped by kubelet) (Ch 4).
**ResourceQuota** — Per-Namespace object capping object counts/resource usage to blunt DoS (Ch 16).
**REST** — REpresentational State Transfer; a request is a verb (HTTP method) plus a path to a resource (Ch 15).
**Role** — Namespaced RBAC object defining a permission set (the *what*) (Ch 14).
**RoleBinding** — Namespaced RBAC object binding a Role/ClusterRole to subjects (the *who*) (Ch 14).
**Rolling update** — Zero-downtime strategy creating a new ReplicaSet and incrementally swapping Pods per `maxSurge`/`maxUnavailable` (Ch 6).
**Rollback** — An update whose "new" image is an older revision, using the kept old ReplicaSet (Ch 6).
**runwasi** — The code interfacing a Wasm shim with containerd; embedded in each Wasm shim (Ch 9).
**RuntimeClass** — `node.k8s.io/v1` object selecting labeled nodes via `nodeSelector` and naming a `handler` (e.g. a Wasm shim) (Ch 9, Ch 17).
**Scheduler** — Control-plane service that filters then ranks nodes to assign new tasks; unschedulable tasks go Pending (Ch 2).
**seccomp** — Syscall filtering (GA 1.19); use a custom least-privilege profile (Ch 16).
**Secret** — Core `v1` object like a ConfigMap but for sensitive data; only base64-encoded (not encrypted) in the store (Ch 12, Ch 16).
**securityContext** — Pod/container field setting non-root user, capability drops, `allowPrivilegeEscalation`, read-only FS, seccomp (Ch 16, Ch 17).
**Service** — API object giving a stable name/IP/port that load balances over a label-selected set of healthy Pods (Ch 2, Ch 7).
**Service discovery** — The automatic name-to-ClusterIP machinery: registration into and resolution out of the cluster DNS (Ch 10).
**ServiceAccount** — Non-human identity auto-mounted into Pods as a token; disable with `automountServiceAccountToken: false` when unused (Ch 14, Ch 16).
**Session Affinity** — `None` (default) or `ClientIP` stickiness on a Service; ClientIP is an anti-pattern for microservices (Ch 7).
**Sidecar** — A helper container in the same Pod augmenting the main app (e.g. log scraping, service-mesh proxy) (Ch 2, Ch 4).
**Soft vs hard multi-tenancy** — Soft = trusted tenants sharing infra (Namespaces fine); hard = untrusted, requiring separate clusters (Ch 5, Ch 17).
**Spin** — Fermyon's popular Wasm framework providing a runtime plus build/scaffold tooling (Ch 9).
**Static Pod** — A Pod deployed directly from a manifest and managed only by the local kubelet; no self-healing/scaling (Ch 4).
**StatefulSet** — `apps/v1` controller for stateful apps giving each Pod a sticky ID: stable name, DNS hostname, and volume (Ch 13).
**Sticky ID** — A StatefulSet Pod's persistent name + DNS hostname + volume binding that survive failure and rescheduling (Ch 13).
**StorageClass (SC)** — Object defining a storage tier; makes provisioning dynamic and automatic; immutable once created (Ch 11).
**STRIDE** — Threat model with six categories: Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege (Ch 16).
**Supply chain security** — Securing the delivery path: registries, approved base images, scanning, signing, IaC review (Ch 17).
**tmpfs** — In-memory filesystem Secret volumes mount, base64-decoded and never written to node disk (Ch 12).
**Vertical Pod Autoscaler (VPA)** — Resizes Pod CPU/memory; not installed by default and disruptive (Ch 6).
**VolumeBindingMode** — `WaitForFirstConsumer` (defers volume creation to a consuming Pod for locality) or `Immediate` (Ch 11).
**volumeClaimTemplates** — StatefulSet field generating one unique per-Pod PVC named `<template>-<sts>-<ordinal>` (Ch 13).
**WASI** — WebAssembly System Interface letting sandboxed Wasm apps securely access external services (Ch 9).
**Wasm (WebAssembly)** — A binary ISA apps compile to, run by a Wasm runtime; deny-by-default, sub-second, truly portable (Ch 9).
**Wasm shim** — A single binary (runwasi + embedded runtime) named `containerd-shim-<runtime>-v<n>`, registered in containerd (Ch 9).
**Worker node** — Linux or Windows node running user applications (Ch 2).
