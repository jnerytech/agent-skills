# Chapter 18: Deploying Kubernetes — Multinode and Multiarchitecture Clusters

## Core Idea

Running your own Kubernetes cluster from scratch exposes every component normally abstracted by managed cloud platforms. kubeadm is the primary tool for initializing a control plane, joining worker nodes, and managing the cluster lifecycle. A single cluster can host nodes with different operating systems (Linux, Windows) and CPU architectures (Intel x86-64, Arm, IBM), enabling hybrid workloads that span legacy Windows apps and modern Linux microservices — managed through a unified YAML manifest model with only minor tweaks (node selectors) to distinguish architecture targets.

---

## Frameworks Introduced

- **Control Plane vs. Worker Node Split**
  - **What**: Two logical tiers — control plane nodes running management components (api-server, scheduler, controller-manager, etcd) and worker nodes running only application Pods plus kubelet, kube-proxy, and container runtime.
  - **When**: Any self-managed cluster deployment.
  - **How**: kubeadm bootstraps the control plane on the first VM; all other VMs join as workers via `kubeadm join`. Control plane nodes are tainted by default to prevent application workloads.
  - **Why / Failure**: Without this separation, application workloads can starve the API server and scheduler of CPU, making the cluster unmanageable.

- **HA Control Plane Topology**
  - **What**: Multiple control plane nodes each running their own copy of every control-plane component; the API server is load-balanced; etcd is replicated across instances.
  - **When**: Production deployments where loss of the control plane must not halt management.
  - **How**: Use an odd number of control plane nodes so a quorum can elect a new manager after node failure. Optionally run etcd external to the cluster for additional redundancy or split its storage for events vs. cluster state for performance.
  - **Why / Failure**: A single control plane node is a single point of failure — apps keep running on workers, but kubectl stops working and self-healing is lost.

- **Multiarchitecture Node Selection**
  - **What**: Adding nodes with different OS/CPU combinations (Linux/Intel, Linux/Arm, Windows/Intel) to the same cluster and directing Pods to the correct node type via `nodeSelector`.
  - **When**: Organizations with mixed workloads — legacy Windows apps, modern Linux services, cost-optimized Arm nodes.
  - **How**: Each node carries built-in labels (`kubernetes.io/os`, `kubernetes.io/arch`). Pod specs declare `nodeSelector` to constrain scheduling. All containers in a Pod must share the same architecture.
  - **Why / Failure**: Omitting node selectors in a multiarchitecture cluster risks scheduling Linux images onto Windows nodes (or vice versa), causing immediate container startup failures.

---

## Key Concepts

1. **kubeadm**: The Kubernetes administration CLI for bootstrapping clusters. Handles `init`, `join`, `token create`, and version upgrades. Requires Docker/containerd, kubelet, and supporting kernel settings installed on the host first.

2. **Control Plane Components**:
   - `kube-apiserver` — HTTPS REST interface; the only management entry point; horizontally scalable.
   - `kube-scheduler` — watches for unscheduled Pods and selects nodes; pluggable.
   - `kube-controller-manager` — runs node-availability, endpoint, and other internal controllers.
   - `etcd` — distributed key-value store for all cluster state; must be replicated for HA.

3. **Node Components** (every node, including control plane nodes):
   - `kubelet` — runs as a host process (not in a Pod); manages Pod lifecycle; sends heartbeats to the API server.
   - `kube-proxy` — DaemonSet Pod; routes inter-Pod and ingress traffic per node.
   - Container runtime — pluggable via CRI (Docker, containerd, CRI-O).

4. **Pod Network Plugin**: Kubernetes does not ship a built-in Pod network. A CNI plugin (flannel, Calico, etc.) must be applied after `kubeadm init`. Without it, the node stays `NotReady` and DNS Pods will not start. Flannel is preferred for multiarchitecture clusters due to its mature cross-platform DaemonSet images.

5. **kubeadm Join Token**: A short-lived token plus a CA certificate hash generated at `kubeadm init` time. Any server with network access to the control plane and possession of the token can join. Treat the token as a secret; regenerate with `kubeadm token create --print-join-command` if expired.

6. **NodePort Service**: A Service type that opens a specific port on every node in the cluster (must be >= 30000). Traffic arriving on any node's IP at that port is routed to the correct Pod regardless of which node it runs on. Suitable for on-premises clusters without a cloud load balancer.

7. **Master Taint**: Control plane nodes carry the `node-role.kubernetes.io/master` taint by default, preventing application Pods from being scheduled there. Removable for lab environments (`kubectl taint nodes --all node-role.kubernetes.io/master-`); should remain in production.

8. **Windows Node Support**: Requires Windows Server 2019+, Docker as the container runtime, Windows-specific flannel and kube-proxy DaemonSets deployed on the control plane, and a Windows-specific `PrepareNode.ps1` setup script on the node itself. The control plane is always Linux; kubelet and kube-proxy run on both OS families.

9. **Multiarchitecture Images**: Container images are OS + CPU-architecture-specific. A Linux/Intel image cannot run on a Windows node or an Arm node. Image tags alone do not convey architecture — manifest lists (multi-arch manifests) allow a single image name to serve the correct binary per platform.

10. **Cluster Scale Limits**: Kubernetes officially supports up to 5,000 nodes and 150,000 Pods per cluster. Practical limits arise earlier (around 500 nodes) due to etcd and network plugin performance. Beyond that, control plane components may need independent horizontal scaling, or the workload split across multiple clusters.

---

## Mental Models

- **The Two-Tier Separation Analogy**: Think of the control plane as the "air traffic control tower" and worker nodes as "runways." The tower schedules and directs; runways run the planes. Overloading a runway with control functions grounds the whole airport.

- **Architecture as a Node Label, Not an Image Property**: Kubernetes does not introspect image manifests to determine compatibility. The node carries an OS/arch label; the Pod spec carries a selector. Matching is explicit and declarative — the scheduler is just doing label filtering. If either side omits the label/selector, the match is accidental and fragile.

- **etcd as the Source of Truth**: Every object in the cluster — Pods, Services, Secrets, ConfigMaps — exists first as a record in etcd. If etcd is lost without backup, the cluster's declarative state is gone even though running containers may still be alive on nodes. This is why replicating etcd and taking backups is the most critical HA concern.

- **kubeadm as a Bootstrap Tool, Not an Operator**: kubeadm gets the cluster started; it does not manage day-2 operations such as certificate rotation, etcd backups, or node repair. After `kubeadm init`, the operator is responsible for those concerns.

---

## Anti-patterns

- **Single control plane node in production**: If the control plane VM is lost, the cluster is unmanageable. Existing Pods keep running, but there is no self-healing, no new scheduling, and no kubectl access. A minimum of three control plane nodes (odd quorum) is required for HA.

- **No node selector in multiarchitecture clusters**: Deploying manifests without `nodeSelector` when the cluster has both Linux and Windows (or Intel and Arm) nodes will cause Pods to be scheduled on incompatible nodes, failing immediately with image pull or runtime errors.

- **Exposing the kubeadm join token insecurely**: The token is a credential. Anyone on the network who obtains the token and CA hash can join rogue nodes to the cluster, gaining access to cluster secrets and Pod network traffic.

- **Running application workloads on control plane nodes in production**: Removing the master taint in production risks CPU/memory starvation of the API server, scheduler, and controller-manager, leading to cluster instability under load.

- **Ignoring image size for scale**: Each node maintains its own local image cache. Large images (the Windows flannel image is ~5 GB) cause slow Pod starts on new nodes and slow horizontal scale-up. Optimizing Dockerfiles and using smaller base images directly affects time-to-scale.

---

## Code Examples

```bash
# Initialize a control plane node with fixed pod and service CIDRs
sudo kubeadm init --pod-network-cidr="10.244.0.0/16" --service-cidr="10.96.0.0/12" --apiserver-advertise-address=$(cat /tmp/ip.txt)

# Copy the admin kubeconfig so kubectl can authenticate
mkdir ~/.kube && sudo cp /etc/kubernetes/admin.conf ~/.kube/config && sudo chmod +r ~/.kube/config

# Deploy the flannel CNI plugin to make the node Ready
kubectl apply -f flannel.yaml

# Wait for DNS Pods (they won't start until flannel is up)
kubectl -n kube-system wait --for=condition=ContainersReady pod -l k8s-app=kube-dns

# Join a Linux worker node (values come from kubeadm init output)
sudo kubeadm join 172.21.125.229:6443 --token 3sqpc7.a19sx21toelnar5i --discovery-token-ca-cert-hash sha256:ed01ef0e33f7ecd56f1d39b5db0fbaa56811ac055f43adb37688a2a2d9cc86b9

# Regenerate a join command if the token has expired
kubeadm token create --print-join-command

# Remove the master taint so control plane node can run app Pods (lab only)
kubectl taint nodes --all node-role.kubernetes.io/master-

# Label / nodeSelector for a Windows Pod
# In the Pod spec:
#   nodeSelector:
#     kubernetes.io/os: windows

# Deploy Windows-specific kube-proxy and flannel DaemonSets
kubectl apply -f /vagrant/setup/kube-proxy.yml
kubectl apply -f /vagrant/setup/flannel-overlay.yml

# Join a Windows node (same kubeadm join syntax)
kubeadm join 172.21.120.227:6443 --token 5wbq7j.bew48gsfy0maa2bo --discovery-token-ca-cert-hash sha256:2c520ea15a99bd68b74d04f40056996dff5b6ed1e76dfaeb0211c6db18ba0393

# NodePort Service excerpt (port >= 30000)
# spec.type: NodePort
# spec.ports[0].nodePort: 30000

# List Pods on a specific node
kubectl get pods --all-namespaces --field-selector spec.nodeName=kiamol-node
```

---

## Reference Tables

### Control Plane Components and Their Roles

| Component | Pod Name | Role | HA Behavior |
|---|---|---|---|
| API Server | `kube-apiserver` | HTTPS REST management interface; entry point for kubectl and internal Pods | Horizontally scalable; load-balanced across control plane nodes |
| Scheduler | `kube-scheduler` | Watches for unscheduled Pods; selects a node based on resource and policy constraints | Pluggable; one active leader at a time (leader election) |
| Controller Manager | `kube-controller-manager` | Runs node-availability controller, endpoint controller, and other internal controllers | One active leader; others in standby |
| etcd | `etcd` | Distributed key-value store; holds all cluster state | Replicated across all control plane nodes; external etcd also supported for extra redundancy |

### Node-Level Components (All Nodes)

| Component | Runs As | Role |
|---|---|---|
| kubelet | Host process (not a Pod) | Creates and monitors Pods; sends heartbeats to API server |
| kube-proxy | DaemonSet Pod | Routes traffic between Pods and from external sources |
| Container runtime | Host daemon | Manages container lifecycle via CRI (Docker, containerd, CRI-O) |

### Linux vs. Windows Node Considerations

| Concern | Linux Node | Windows Node |
|---|---|---|
| Minimum OS | Ubuntu 20.04 (or similar) | Windows Server 2019+ |
| Container runtime | Docker, containerd, or CRI-O | Docker only (containerd in progress at book time) |
| Setup script | `linux-setup.sh` | `windows-setup.ps1` + `PrepareNode.ps1` |
| Control plane DaemonSets needed | Yes (flannel, kube-proxy — standard) | Additional Windows-specific DaemonSets must be deployed on control plane before node joins |
| Flannel image size | Small (~tens of MB) | ~5 GB — slow first-start |
| nodeSelector | `kubernetes.io/os: linux` | `kubernetes.io/os: windows` |
| Control plane role | Can be control plane or worker | Worker only (control plane is always Linux) |

---

## Worked Example

### Scenario: Initialize a cluster, join a Linux worker, join a Windows worker, and run a hybrid app

**Step 1 — Prepare and initialize the control plane VM**

Provision an Ubuntu 20.04 VM (e.g., via Vagrant: `vagrant up kiamol-control && vagrant ssh kiamol-control`). Run the setup script to install Docker, kubelet, kubeadm, and kubectl:

```bash
sudo chmod +x /vagrant/setup/linux-setup.sh && sudo /vagrant/setup/linux-setup.sh
```

Initialize the cluster. The `--pod-network-cidr` must match what the chosen CNI plugin (flannel) expects:

```bash
sudo kubeadm init --pod-network-cidr="10.244.0.0/16" --service-cidr="10.96.0.0/12" \
  --apiserver-advertise-address=$(cat /tmp/ip.txt)
```

Copy the output's `kubeadm join` command to a text file — you will need it for worker nodes. Configure kubectl:

```bash
mkdir ~/.kube
sudo cp /etc/kubernetes/admin.conf ~/.kube/config
sudo chmod +r ~/.kube/config
```

At this point `kubectl get nodes` shows the control plane node in `NotReady` status — the Pod network is missing.

**Step 2 — Install the flannel CNI plugin**

```bash
kubectl apply -f flannel.yaml
kubectl -n kube-system wait --for=condition=ContainersReady pod -l k8s-app=kube-dns
kubectl get nodes
```

The node transitions to `Ready`. DNS Pods start because flannel is now running.

**Step 3 — Join a Linux worker node**

Provision a second Ubuntu VM: `vagrant up kiamol-node && vagrant ssh kiamol-node`. Run the same setup script, then execute the join command saved earlier:

```bash
sudo /vagrant/setup/linux-setup.sh
sudo kubeadm join 172.21.125.229:6443 \
  --token 3sqpc7.a19sx21toelnar5i \
  --discovery-token-ca-cert-hash sha256:ed01ef0e33f7ecd56f1d39b5db0fbaa56811ac055f43adb37688a2a2d9cc86b9
```

Back on the control plane: `kubectl get nodes` now shows two nodes. The new worker automatically receives flannel and kube-proxy Pods via DaemonSets.

**Step 4 — Prepare the control plane for Windows nodes**

Before joining any Windows node, deploy the Windows-specific DaemonSets on the control plane:

```bash
kubectl apply -f /vagrant/setup/kube-proxy.yml
kubectl apply -f /vagrant/setup/flannel-overlay.yml
kubectl get ds -n kube-system   # Windows DaemonSets show desired=0 until the node joins
```

**Step 5 — Join a Windows worker node**

Provision a Windows Server 2019 VM (`vagrant up kiamol-node-win`), connect via `vagrant ssh kiamol-node-win`, switch to PowerShell, and run the two-phase setup:

```powershell
# Phase 1: enable Windows containers feature and install Docker
.\windows-setup.ps1   # VM reboots

# Phase 2: install kubeadm, set up flannel/kubelet on Windows
.\PrepareNode.ps1

# Join (same syntax as Linux)
kubeadm join 172.21.120.227:6443 --token 5wbq7j.bew48gsfy0maa2bo `
  --discovery-token-ca-cert-hash sha256:2c520ea15a99bd68b74d04f40056996dff5b6ed1e76dfaeb0211c6db18ba0393
```

The Windows node downloads the flannel image (~5 GB) and starts. On the control plane, `kubectl get nodes` now shows three nodes across two OS families.

**Step 6 — Deploy a hybrid Linux + Windows application**

The random-number app has a Linux web frontend and a Windows API backend. The only difference from a pure-Linux manifest is the `nodeSelector` per component:

```yaml
# Linux web component
spec:
  nodeSelector:
    kubernetes.io/os: linux

# Windows API component
spec:
  nodeSelector:
    kubernetes.io/os: windows
  containers:
  - name: api
    image: kiamol/ch03-numbers-api:windows
```

Deploy and wait:

```bash
kubectl apply -f /vagrant/numbers/
kubectl -n kube-system wait --for=condition=Ready node --all
kubectl get pods -o wide -l app=numbers
```

The web Pod schedules on the Linux worker; the API Pod schedules on the Windows node. A ClusterIP Service connects them transparently — the Linux web container calls the Windows API Pod over the Pod network as if they were on the same machine. Browse to port 30001 on any node IP to verify the app works end-to-end.

---

## Key Takeaways

1. **kubeadm reduces cluster bootstrap to a single command** — but it requires Docker, kubelet, and kernel settings pre-installed, and you must deploy a CNI plugin separately before the cluster becomes functional.

2. **The control plane is multiple independent components** (api-server, scheduler, controller-manager, etcd), each running as a Pod. Losing the control plane does not kill running workloads but eliminates all management and self-healing.

3. **HA control plane requires multiple nodes in odd numbers** to support quorum-based leader election after node failure. etcd can also be externalized for additional redundancy or performance tuning.

4. **Worker nodes add capacity automatically** — DaemonSets (flannel, kube-proxy) provision system Pods the moment a node joins; no manual per-node configuration of network components is needed.

5. **Multiarchitecture support is a first-class Kubernetes feature** — Linux, Windows, Arm, and IBM nodes can coexist in one cluster. The only manifest change required is `nodeSelector`; Services, ConfigMaps, Secrets, and all other abstractions work identically across architectures.

6. **Control plane nodes are tainted by default** to prevent resource starvation by application workloads. Never remove the taint in production.

7. **Self-managed clusters carry significant operational burden** — certificate management, etcd backups, version upgrades, storage provisioning (no dynamic PVC without a provisioner), and load balancer integration (no cloud LB; use NodePort + MetalLB on-prem) must all be handled manually.

---

## Connects To

- **Chapter 6 (Volumes and Storage)**: Dynamic PersistentVolumeClaims require a storage class and provisioner, which are absent in a bare kubeadm cluster. On-prem alternatives include NFS volumes and HostPath.
- **Chapter 16 (Network Policy / Calico)**: Flannel is chosen here over Calico for multiarchitecture support; both are CNI plugins that solve the same Pod-network gap left by kubeadm.
- **Chapter 19 (Taints and Scheduling)**: The master taint introduced here is fully explained in the next chapter, along with tolerations and advanced scheduling constraints.
- **Chapter 1 (Kubernetes Fundamentals)**: The promise that "Kubernetes doesn't care what your application is" is validated in this chapter by running a 2008 .NET Windows Pet Shop app unmodified on the latest Kubernetes version.
- **Managed Kubernetes (AKS, EKS, GKE)**: The entire control plane complexity described here is the reason managed platforms are attractive — cloud providers absorb control plane management, certificate rotation, etcd backups, and load balancer integration, leaving only worker node concerns to the operator.
