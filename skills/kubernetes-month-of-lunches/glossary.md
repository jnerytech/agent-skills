# Glossary

**Adapter Pattern** — A sidecar container that translates app-internal behavior (e.g., file logs to stdout) into the form Kubernetes expects, without modifying the application. (Ch 7, Ch 14)

**Admission Webhook** — An HTTPS server registered via `ValidatingWebhookConfiguration` or `MutatingWebhookConfiguration` that intercepts API write requests to allow, block, or mutate objects before they are stored in etcd. (Ch 16)

**Ambassador Pattern** — A proxy sidecar that intercepts all outgoing network traffic from the app container, enabling service discovery, address remapping, and access control without changing app code. (Ch 7)

**API Server (`kube-apiserver`)** — The HTTPS REST interface that is the sole management entry point for Kubernetes; all tooling including kubectl communicates exclusively through it. (Ch 1, Ch 18)

**Cluster** — A set of servers (nodes) configured with a container runtime and joined into a single logical unit managed by Kubernetes. (Ch 1)

**Cluster Autoscaler** — Cloud-provider tooling that adds or removes nodes when Pods are pending due to insufficient cluster capacity; complements HPA. (Ch 22)

**ClusterIP** — Default Service type that assigns a cluster-internal virtual IP, reachable only from inside the cluster; used for inter-Pod communication. (Ch 3)

**ClusterRole** — An RBAC object that grants permissions cluster-wide, or across any namespace when referenced by a RoleBinding; required for cluster-scoped resources. (Ch 17)

**ClusterRoleBinding** — Binds a ClusterRole to a subject with cluster-wide scope; use only when namespace scope is insufficient. (Ch 17)

**CNI (Container Network Interface)** — A plugin standard that provides the Pod network; required for NetworkPolicy enforcement (Calico, Cilium, Flannel, Weave). (Ch 16, Ch 18)

**ConfigMap** — A Kubernetes resource storing arbitrary key-value pairs or file contents, surfaced into Pods as environment variables or volume-mounted files; intended for non-sensitive configuration. (Ch 4)

**Container Runtime Interface (CRI)** — The standard API Kubernetes nodes use to communicate with any container runtime (Docker, containerd, CRI-O). (Ch 2)

**Controller** — A Kubernetes resource that watches the API for its owned resources, compares current vs. desired state, and reconciles; examples include Deployment, ReplicaSet, DaemonSet, StatefulSet. (Ch 2, Ch 6)

**CRD (CustomResourceDefinition)** — A Kubernetes object that registers a new resource type with its own group, version, scope, and JSONSchema, making it manageable via kubectl like any built-in resource. (Ch 20)

**CronJob** — A controller that creates Jobs on a Linux cron schedule; supports `concurrencyPolicy` to prevent overlapping runs and `successfulJobsHistoryLimit` for cleanup. (Ch 8)

**DaemonSet** — A controller that runs exactly one Pod per node (or per labeled node subset); used for infrastructure agents, log collectors, and node-local reverse proxies. (Ch 6, Ch 13)

**Deployment** — A controller that manages a set of identical Pods via ReplicaSets, providing desired-replica enforcement, rolling updates, and rollback history. (Ch 2, Ch 6, Ch 9)

**Desired State** — The specification of what should be running, declared in a YAML manifest; Kubernetes continuously reconciles actual state to match it. (Ch 1, Ch 2)

**EFK Stack** — Elasticsearch + Fluentd/Fluent Bit + Kibana; the canonical open-source centralized logging architecture for Kubernetes clusters. (Ch 13)

**emptyDir** — A Pod-scoped ephemeral volume that survives container restarts within the same Pod but is destroyed when the Pod is replaced; the standard mechanism for inter-container data sharing. (Ch 5, Ch 7)

**Endpoints** — A Kubernetes resource (auto-managed by the Service controller) holding the live list of Pod IPs matching a Service's selector; updated immediately on Pod changes. (Ch 3)

**etcd** — The distributed key-value store that holds all cluster state; must be replicated for HA; source of truth for every Kubernetes object. (Ch 18)

**ExternalName** — A Service type that returns a CNAME DNS record pointing to an external domain; suitable for TCP services but not HTTP due to Host header mismatch. (Ch 3)

**Headless Service** — A Service with `clusterIP: None`; DNS returns individual Pod IPs rather than a virtual IP; required by StatefulSets for per-Pod DNS addressability. (Ch 3, Ch 8)

**Helm Chart** — A versioned, parameterized package of Kubernetes YAML templates plus metadata (`Chart.yaml`) and default values (`values.yaml`). (Ch 10)

**Helm Release** — A named, versioned instance of a Helm chart installed in a cluster; multiple releases of the same chart can coexist. (Ch 10)

**Helm Repository** — An index-file HTTP server listing chart versions; queried via `helm search repo` after `helm repo add`. (Ch 10)

**HorizontalPodAutoscaler (HPA)** — A separate Kubernetes object that monitors a scale target and adjusts its replica count to hit a CPU (or custom) metric target; requires metrics-server. (Ch 19)

**hostPath** — A volume type that maps a node filesystem directory into the container; data persists across Pod replacements only if the replacement Pod lands on the same node. (Ch 5, Ch 13)

**imagePullPolicy** — A Pod spec field controlling when Kubernetes pulls an image: `Always`, `IfNotPresent`, or `Never`; defaults to `Always` for `:latest` tags. (Ch 11)

**Ingress** — A Kubernetes resource storing HTTP/S routing rules (host, path, TLS); acted on by an ingress controller to route external traffic to ClusterIP Services. (Ch 15)

**Ingress Class** — A labeling mechanism (`kubernetes.io/ingress.class` annotation or `spec.ingressClassName`) that tells a specific ingress controller which Ingress objects to process. (Ch 15)

**Ingress Controller** — A reverse proxy (Nginx, Traefik, HAProxy, Contour) that watches Ingress resources and routes external HTTP/S traffic; exposed via a single LoadBalancer Service. (Ch 15)

**Init Container** — A container in `spec.initContainers[]` that runs to completion in sequence before any app container starts; used for config preparation, migrations, and secret fetching. (Ch 7, Ch 8)

**Job** — A controller that runs a Pod to completion, with retry logic; supports `completions` (total runs) and `parallelism` (concurrent Pods). (Ch 8)

**K3s** — A minimal, fully certified Kubernetes distribution for Linux; suitable for local labs and edge environments. (Ch 1)

**KEDA** — Kubernetes Event-Driven Autoscaling; CNCF project that scales workloads to zero and back based on event sources such as message queues or Prometheus metrics. (Ch 22)

**kubectl** — The Kubernetes CLI; connects to the cluster API and is the primary operator interface for all resource management operations. (Ch 1)

**kubeadm** — The Kubernetes administration CLI for bootstrapping control planes and joining worker nodes; handles `init`, `join`, and version upgrades. (Ch 18)

**kube-proxy** — A per-node DaemonSet component that watches Services and Endpoints and programs iptables/IPVS rules to forward virtual ClusterIP traffic to real endpoint IPs. (Ch 3, Ch 18)

**kubelet** — A host process (not a Pod) on every node that manages Pod lifecycle and sends heartbeats to the API server. (Ch 18)

**Kustomize** — A tool for layering YAML overrides across environments using a base + overlays model, without Helm's templating. (Ch 22)

**Label** — A key-value pair attached to any Kubernetes resource; the primary coupling mechanism between controllers and their managed Pods, and between Services and their backends. (Ch 2)

**Label Selector** — A query (`matchLabels` or `matchExpressions`) in a controller or Service spec that identifies which Pods it owns or routes to. (Ch 2, Ch 3)

**LimitRange** — A namespace object that sets default resource requests/limits and min/max constraints for containers, enforced at Pod creation time. (Ch 19)

**Liveness Probe** — A periodic healthcheck that determines whether a container is alive; failure kills the container and triggers a restart without replacing the Pod. (Ch 12)

**LoadBalancer** — A Service type that provisions an external load balancer from the platform; the recommended type for external traffic in production. (Ch 3)

**Manifest** — A YAML file declaring the desired state of one or more Kubernetes resources; deployed via `kubectl apply`. (Ch 1)

**metrics-server** — A lightweight cluster add-on that scrapes current CPU/memory from kubelets; required for `kubectl top` and HPA to function. (Ch 19)

**MutatingAdmissionWebhook** — An admission webhook that can modify (mutate) object specs before they are stored; runs before validating webhooks. (Ch 16)

**Namespace** — A logical partition of the cluster; every resource lives in a namespace; the permission and DNS isolation boundary. (Ch 3, Ch 11)

**NetworkPolicy** — A `networking.k8s.io/v1` resource with `podSelector`, `ingress`, and `egress` stanzas that restricts Pod-to-Pod traffic; enforced only by compatible CNI plugins. (Ch 16)

**Node** — An individual server inside the cluster running a container runtime, kubelet, and kube-proxy; managed by the control plane. (Ch 1, Ch 18)

**Node Affinity** — A Pod spec field (`affinity.nodeAffinity`) with rich label-based placement rules supporting required (hard) and preferred (soft) scheduling constraints. (Ch 19)

**nodeSelector** — A simple map in the Pod spec that constrains scheduling to nodes carrying matching labels; the lightweight alternative to node affinity. (Ch 6, Ch 18, Ch 19)

**OOMKilled** — The exit reason when a container exceeds its memory limit; the kernel kills the container and the Pod enters a restart cycle. (Ch 12)

**Operator** — A higher-level pattern combining one or more CRDs and custom controllers to encode full application lifecycle management (deployment, upgrades, backups, HA) into the cluster. (Ch 20)

**OPA Gatekeeper** — A CNCF project that runs a generic validating webhook and lets you define admission policies as `ConstraintTemplate` + `Constraint` CRD objects written in Rego. (Ch 16)

**PersistentVolume (PV)** — A cluster-scoped object representing pre-provisioned storage with capacity, access modes, and reclaim policy; binds one-to-one with a PVC. (Ch 5)

**PersistentVolumeClaim (PVC)** — A namespace-scoped request for storage specifying access mode, capacity, and optional StorageClass; Kubernetes binds it to a matching PV. (Ch 5, Ch 8)

**Pod** — The smallest deployable unit in Kubernetes; wraps one or more containers sharing a virtual IP, network namespace, and localhost. (Ch 1, Ch 2)

**Pod Affinity / Anti-Affinity** — Placement rules that attract or repel Pods relative to other Pods using label selectors and a topology key scoping the constraint to node, zone, or region. (Ch 19)

**Pod Disruption Budget (PDB)** — A separate object that guarantees a minimum number of Pods remain available during voluntary disruptions such as node drains. (Ch 22)

**Pod Template** — The nested Pod specification inside a controller's `spec.template`; defines the Pods the controller will create and must include labels matching the selector. (Ch 2)

**pod-template-hash** — A label Kubernetes adds to ReplicaSets and their Pods by hashing the Pod spec template; lets Deployments detect whether a retained ReplicaSet matches a new desired spec. (Ch 6)

**PriorityClass** — An integer-valued `scheduling.k8s.io/v1` object referenced by Pods via `priorityClassName`; determines eviction order when nodes are under memory pressure. (Ch 19)

**Projected Volume** — A volume type that merges multiple ConfigMaps and Secrets into a single directory mount inside a container. (Ch 22)

**Prometheus** — A pull-based monitoring system that scrapes `/metrics` HTTP endpoints on a schedule; integrates natively with Kubernetes via service discovery and relabeling. (Ch 14)

**QoS Class** — A Pod classification (BestEffort, Burstable, Guaranteed) Kubernetes assigns based on resource requests/limits; determines eviction priority under node memory pressure. (Ch 22)

**Readiness Probe** — A periodic healthcheck that determines whether a Pod should receive network traffic; failure removes the Pod from Service endpoints without restarting it. (Ch 12)

**ReplicaSet** — The actual scale mechanism owned by a Deployment; maintains a desired count of Pods matching a label selector; rarely created directly by users. (Ch 6, Ch 9)

**Resource Limits** — `resources.limits` in a container spec caps maximum CPU/memory; memory violations trigger OOMKilled, CPU violations throttle the container. (Ch 12)

**Resource Requests** — `resources.requests` in a container spec declares minimum guaranteed resources used by the scheduler for node placement and by HPA for utilization calculations. (Ch 12, Ch 19)

**ResourceQuota** — A namespace object that sets aggregate CPU/memory caps; a Pod spec that would push the namespace over quota is rejected at creation time. (Ch 12)

**Role** — An RBAC object granting named permissions within a single namespace; combined with a RoleBinding to bind the permissions to a subject. (Ch 17)

**RoleBinding** — Binds a Role (or ClusterRole) to a subject within a specific namespace; the default choice for least-privilege access. (Ch 17)

**Rolling Update** — The default Deployment update strategy; gradually scales up a new ReplicaSet while scaling down the old one; tuned via `maxSurge`, `maxUnavailable`, and `minReadySeconds`. (Ch 9)

**Secret** — A Kubernetes resource structurally similar to a ConfigMap but with additional protections (node-only delivery, in-memory storage, optional encryption at rest); data is Base64-encoded in the API and decoded inside containers. (Ch 4)

**securityContext** — Pod- and container-level fields controlling Linux user/group, kernel capabilities, privilege escalation, and filesystem mutability. (Ch 16)

**Service** — A stable virtual resource providing a fixed DNS name and IP, routing traffic to Pods via a label selector; types include ClusterIP, NodePort, LoadBalancer, and ExternalName. (Ch 3)

**ServiceAccount** — A Kubernetes identity for in-cluster workloads; receives a JWT token mounted at a known path; should be created per-app and granted least-privilege RBAC. (Ch 17)

**Sidecar Pattern** — One or more helper containers running in parallel with the app container inside the same Pod, sharing its network namespace and optional volumes. (Ch 7)

**StatefulSet** — A Pod controller that enforces stable, ordered runtimes: predictable Pod names (`<name>-0`, `<name>-1`), sequential startup, per-Pod PVCs via `volumeClaimTemplates`, and individual DNS entries via a headless Service. (Ch 8)

**StorageClass** — A cluster resource defining a provisioner, reclaim policy, and binding mode; PVCs reference a class to trigger dynamic provisioning without pre-created PVs. (Ch 5)

**Taint** — A node-level mark (`key=value:Effect`) that repels Pods without a matching toleration; effects are `NoSchedule` (hard), `PreferNoSchedule` (soft), or `NoExecute` (evicts running Pods). (Ch 18, Ch 19)

**TLS Secret** — A Secret of type `kubernetes.io/tls` storing a certificate and key; referenced by Ingress objects to enable HTTPS termination at the ingress controller. (Ch 15)

**Toleration** — A Pod spec field acknowledging a node taint, granting permission to be scheduled there without guaranteeing placement. (Ch 19)

**ValidatingAdmissionWebhook** — An admission webhook that can allow or deny object creation/update requests; runs after mutating webhooks and any single webhook can block the request. (Ch 16)

**VerticalPodAutoscaler (VPA)** — An add-on that adjusts container resource requests/limits based on actual usage; complements the HPA. (Ch 22)

**Volume** — A storage abstraction declared at the Pod level and mounted per-container; types range from ephemeral (emptyDir) to node-scoped (hostPath) to cluster-scoped (PV/PVC). (Ch 5)

**volumeClaimTemplates** — A StatefulSet spec field that acts as a PVC factory, creating one PVC per Pod named `<template-name>-<pod-name>`; the binding survives Pod replacement. (Ch 8)

**volumeMount** — A container spec field that attaches a named volume to a specific path inside the container filesystem. (Ch 4, Ch 5)
