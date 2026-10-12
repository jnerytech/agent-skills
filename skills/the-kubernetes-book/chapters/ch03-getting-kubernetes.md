# Chapter 3: Getting Kubernetes

## Core Idea
You need a working Kubernetes cluster to follow the book's hands-on examples. Two recommended paths: a free single-node cluster on your laptop via **Docker Desktop** (best for most readers), or a paid production-grade hosted cluster via **Google Kubernetes Engine (GKE)**. Both ship/install **kubectl**, the universal command-line tool you'll use everywhere.

## Key Concepts
- **kubectl**: Kubernetes command-line utility; converts user-friendly commands into HTTP REST requests sent to the API server. Required for every example.
- **kubectl context**: A named bundle of (cluster + user credentials) telling kubectl which cluster to target and how to authenticate.
- **kubeconfig file**: File named `config` in `~/.kube/`. Holds three blocks: clusters, users, contexts.
- **Cluster (in kubeconfig)**: Definition with a friendly name, certificate info, and API server endpoint. One kubectl can manage many clusters.
- **User (in kubeconfig)**: Named set of credentials (e.g., dev vs. ops). With X.509 certs, the username/group is embedded in the certificate.
- **Hosted Kubernetes**: Cloud provider builds and manages the cluster — HA, performance, updates, managed control plane, itemized billing.
- **Control plane (hidden in GKE)**: GKE manages control-plane nodes and hides them; you only see worker nodes (ROLES shows `<none>`).
- **AutoPilot vs. Standard cluster**: AutoPilot does NOT work with all book examples — always choose Standard.

## Mental Models
- **kubectl version skew**: kubectl must be within one minor version of the cluster. Cluster 1.29.x → kubectl 1.28.x–1.30.x.
- **Context = cluster + user**: Switching context redirects all commands; e.g., an `ops-prod` context sends to the prod cluster as the ops user.
- **Delete cloud clusters when idle**: A hosted cluster costs money continuously. Author deletes nightly and recreates on demand.

## Anti-patterns
- Creating an **AutoPilot** GKE cluster (breaks examples) — use Standard.
- Creating a **Zonal** GKE cluster — some later examples need a **Regional** cluster.
- Changing default cluster settings beyond what's instructed (may break later examples).
- Leaving a GKE cluster running after use (unwanted costs).
- Running kubectl with a version more than one minor off the cluster.

## Code Examples

```
$ docker --version
Docker version 25.0.2, build 29cf629

$ kubectl version --client=true -o yaml
clientVersion:
  compiler: gc
  gitVersion: v1.29.1
  major: "1"
  minor: "29"
  platform: darwin/arm64
```
What it demonstrates: verifying Docker and kubectl are installed after Docker Desktop setup.

```
$ kubectl get nodes
NAME             STATUS   ROLES           AGE   VERSION
docker-desktop   Ready    control-plane   93d   v1.29.1
```
What it demonstrates: confirming the Docker Desktop single-node cluster is up and the context is set.

```
$ gcloud container clusters get-credentials gke-tkb --region...
Fetching cluster endpoint and auth data.
kubeconfig entry generated for gke-tkb.
```
What it demonstrates: the Connect command (copied from GKE console) that configures kubectl to talk to the cloud cluster.

```
$ kubectl get nodes
NAME                    STATUS   ROLES    VERSION
gke-gke-tkb-default...h2gp   Ready   <none>   v1.29.0-gke.1381000
gke-gke-tkb-default...l29b   Ready   <none>   v1.29.0-gke.1381000
gke-gke-tkb-default...qzv6   Ready   <none>   v1.29.0-gke.1381000
```
What it demonstrates: GKE worker nodes only; `<none>` roles because the control plane is managed/hidden.

```
$ kubectl config current-context
docker-desktop

$ kubectl config use-context hpa-test
Switched to context "hpa-test".

$ kubectl config current-context
hpa-test
```
What it demonstrates: viewing and switching the active context.

```
$ kubectl config view
```
What it demonstrates: prints the kubeconfig with sensitive data redacted.

### Minimal kubeconfig (cluster `shield`, user `coulson`, context `director`)
```yaml
apiVersion: v1
kind: Config
clusters:
- name: shield
  cluster:
    server: https://192.168.1.77:8443
    certificate-authority-data: LS0tLS1CRUdJTiBDRVJ...
users:
- name: coulson
  user:
    client-certificate-data: LS0tLS1CRUdJTiBDRV...
    client-key-data: LS0tLS1CRUdJTiBFQyB...
contexts:
- context:
    name: director
    cluster: shield
    user: coulson
current-context: director
```
What it demonstrates: how clusters, users, and contexts wire together; `current-context` is the default kubectl uses.

## Reference Tables

| | Docker Desktop (laptop) | GKE (hosted cloud) |
|---|---|---|
| Cost | Free (personal/edu; license if 250+ employees or $10M+ revenue) | Costs money |
| Nodes | Single node | Multi-node (Regional, 1 node/zone in book) |
| Control plane | Visible (`control-plane` role) | Managed/hidden (`<none>` roles) |
| kubectl | Installed by Docker Desktop | Installed by gcloud CLI |
| Recommended for | Most readers / most examples | Only if okay spending money |
| Limitations | Some advanced storage examples need GKE; WASM chapter uses different cluster | Same WASM caveat |

Other hosted services: AWS **EKS**, Azure **AKS**, Civo Cloud Kubernetes, DigitalOcean **DOKS**, Google **GKE**, Linode **LKE**.
Other local options: **k3d**, **KinD**, **minikube** (k3d & KinD build multi-node clusters on top of Docker Desktop).

## Worked Example

Laptop cluster, end to end:
1. Install Docker Desktop (download installer; Windows: install WSL 2 when prompted).
2. Click the Docker whale icon → Settings → Kubernetes → check **Enable Kubernetes** → **Apply & restart**. Wait until the Kubernetes icon turns green.
3. Verify:
```
$ kubectl get nodes
NAME             STATUS   ROLES           AGE   VERSION
docker-desktop   Ready    control-plane   93d   v1.29.1
```

GKE cluster, end to end:
1. Install the **gcloud CLI** (https://cloud.google.com/sdk/); it auto-installs kubectl and prompts `gcloud auth login`.
2. Console → Kubernetes Engine > Clusters → Create → **SWITCH TO STANDARD CLUSTER**.
3. Name `gke-tkb`; Location type = **Regional**; pick a Region; Release channel = latest from **Rapid**; default-pool → Number of nodes (per zone) = 1; **Create**.
4. Cluster's three-dots → **Connect**, copy the `gcloud container clusters get-credentials` command, run it, then `kubectl get nodes`.
5. **Delete the cluster when done** to avoid costs.

## Key Takeaways
1. Docker Desktop is the free, recommended path for most examples; GKE is the paid production-grade path.
2. Always create a **Standard, Regional** GKE cluster — not AutoPilot, not Zonal.
3. kubectl talks to the API server via the `~/.kube/config` kubeconfig (clusters + users + contexts).
4. A context binds a cluster to a user; `use-context` switches targets, and Docker Desktop's whale menu offers a GUI switch.
5. Keep kubectl within one minor version of the cluster.
6. Delete hosted clusters when idle to avoid charges.

## Connects To
- Ch 2 (Kubernetes principles): the cluster you build here is the control plane + nodes described there.
- Later storage examples and the WebAssembly chapter require different/cloud clusters.
- All subsequent hands-on chapters depend on a working cluster and kubectl context set up here.
