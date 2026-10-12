# Chapter 1: Before You Begin (Fast-Track Setup)

## Core Idea

Kubernetes is a container platform that implements a **desired-state model**: you declare what you want in YAML manifests, send them to the cluster API, and Kubernetes continuously reconciles actual state to match — restarting unhealthy containers, rescheduling on failed nodes, and scaling under load. This chapter is lighter on exercises than all others; its sole job is to orient you conceptually and get a verified cluster running before Chapter 2.

---

## Frameworks Introduced

- **Desired-State / Declarative API** (Stoneman's foundational framing): You describe the target state in a YAML manifest and post it to the Kubernetes API. The control plane diffs current state against desired state and takes corrective action.
  - When to use: Every time you deploy, update, or scale an application — always express intent, never issue imperative step-by-step commands.
  - How:
    1. Author a YAML manifest describing the resource (Pod, Deployment, Service, etc.).
    2. `kubectl apply -f <manifest.yaml>` — sends the manifest to the API.
    3. Kubernetes schedules, starts, and monitors containers to match the spec.
    4. When reality drifts (node failure, crashed container), Kubernetes self-heals without operator intervention.
  - Why it works: State is stored in etcd and continuously reconciled by controllers — the cluster is always driving toward your declared intent. Failure mode: if the manifest is wrong, Kubernetes faithfully enforces the wrong state; validate YAML before applying.

- **"Immediately Effective" Learning Pattern** (Month of Lunches series principle): Each chapter follows introduce → try-it-now exercises → recap → hands-on lab. Theory is minimal; practice is primary.
  - When to use: Structuring your study sessions — read the intro, run the exercises in your live cluster, read the recap, then attempt the unguided lab.
  - How: Clone the `kiamol` repo, `cd` to the chapter folder, follow try-it-now blocks, check the lab answer only after attempting it yourself.
  - Why it works: Kinesthetic repetition in a real cluster builds muscle memory that reading alone cannot. Failure mode: skipping exercises leaves you with conceptual knowledge but no operational confidence.

---

## Key Concepts

- **Cluster**: A set of servers (nodes) configured with a container runtime and joined into a single logical unit managed by Kubernetes.
- **Node**: An individual server inside the cluster; managed by cluster administrators (or hidden behind a managed service like AKS/EKS).
- **API**: The central interface to Kubernetes — all tooling, including `kubectl`, communicates exclusively through it.
- **Manifest**: A YAML file that declares the desired state of one or more Kubernetes resources; also called an application manifest.
- **Resource**: Any object Kubernetes can manage — Pod, Deployment, Service, ConfigMap, Secret, PersistentVolume, etc.
- **Pod**: The smallest deployable unit in Kubernetes; wraps one or more containers (introduced by name here, detailed in Ch 2).
- **Deployment**: A resource that manages a replicated set of Pods with rolling-update capability (introduced by name here, detailed in Ch 2).
- **kubectl**: The Kubernetes CLI (pronounced "cube-cuttle"); connects to the cluster API and is the primary operator interface.
- **K3s**: A minimal but fully certified Kubernetes distribution for Linux; roughly half the binary size of full Kubernetes, suitable for local labs and edge environments.
- **Desired State**: The specification of what should be running, as declared in a manifest; Kubernetes continuously works to make actual state match it.

---

## Mental Models

- Think of the Kubernetes cluster as a **single compute surface**, not a collection of servers — nodes are an operational detail you rarely interact with directly.
- Think of YAML manifests as **infrastructure contracts**: you state what you want; Kubernetes signs the contract and enforces it indefinitely.
- Use Docker Desktop (Windows/macOS) when you want the fastest zero-friction path to a local cluster with a built-in Reset button; use K3s when you are on Linux or in a VM and want a lightweight but fully featured setup.
- Think of `kubectl get nodes` as your **cluster health handshake** — if it returns a node in `Ready` state, your entire control-plane-to-CLI chain is verified.

---

## Anti-patterns

- **Running Kubernetes on Windows without a Linux VM**: Kubernetes control-plane components are Linux containers; Windows cannot host them natively. Docker Desktop handles this transparently, but attempting bare-metal Windows installs will fail.
- **Using the classic Windows Command Prompt for exercises**: The try-it-now exercises are written for Linux/macOS shells and PowerShell. `cmd.exe` will break on quoting, path separators, and multi-line commands from the first chapter onward. Use PowerShell.
- **Installing a third-party Kubernetes distribution on top of Docker Desktop**: Other distributions (minikube, Kind, etc.) do not integrate with Docker Desktop's network configuration and will cause exercise failures. Use Docker Desktop's own built-in Kubernetes option.
- **Skipping exercises to read ahead**: Chapters often build on resources created in earlier try-it-now blocks. Skipping exercises will produce errors in later steps — which Stoneman notes is a learning opportunity, but only if you understand why, not if you are lost.

---

## Code Examples

Clone the book's source repository (required before any chapter exercise):

```bash
git clone https://github.com/sixeyed/kiamol
```

Install Docker and K3s on Linux in two commands:

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh

# Install K3s (with Docker runtime, Traefik disabled, kubeconfig world-readable)
curl -sfL https://get.k3s.io | sh -s - --docker --disable=traefik --write-kubeconfig-mode=644
```

Install `kubectl` on Linux manually (use when neither Docker Desktop nor K3s is your chosen path):

```bash
curl -Lo ./kubectl https://storage.googleapis.com/kubernetes-release/release/v1.18.8/bin/linux/amd64/kubectl
chmod +x ./kubectl
sudo mv ./kubectl /usr/local/bin/kubectl
```

Verify the cluster is up and all nodes are in Ready state:

```bash
kubectl get nodes
```

Create a single-node AKS cluster via Azure CLI and configure local `kubectl` access:

```bash
az group create --name kiamol --location eastus
az aks create --resource-group kiamol --name kiamol-aks --node-count 1 \
  --node-vm-size Standard_DS2_v2 --kubernetes-version 1.18.8 --generate-ssh-keys
az aks get-credentials --resource-group kiamol --name kiamol-aks
```

Create a single-node EKS cluster via `eksctl`:

```bash
eksctl create cluster --name=kiamol --nodes=1 --node-type=t3.large
```

---

## Worked Example

**Lab install + cluster verification sequence (Docker Desktop path)**

1. Download and run the Docker Desktop installer from `https://www.docker.com/products/docker-desktop`. Accept all defaults; reboot if prompted (Windows only).
2. Click the whale icon in the system tray → **Settings** → **Kubernetes** → check **Enable Kubernetes** → Apply & Restart.
3. Docker Desktop downloads Kubernetes runtime images and starts the single-node cluster. Wait for two green status dots in the Settings window.
4. Open a terminal (PowerShell on Windows, Terminal on macOS). Run:

```bash
kubectl get nodes
```

Expected output:

```
NAME             STATUS   ROLES    AGE   VERSION
docker-desktop   Ready    master   2m    v1.18.x
```

5. Clone the kiamol repository so you have all exercise files ready:

```bash
git clone https://github.com/sixeyed/kiamol
cd kiamol/ch02   # ready for Chapter 2
```

A single `Ready` node and a successful clone means the environment is fully operational.

---

## Key Takeaways

1. Kubernetes is a **declarative, desired-state platform** — you declare intent in YAML; the cluster enforces it continuously, including self-healing.
2. The **cluster abstracts away individual nodes** — treat it as a single compute entity, not a collection of servers.
3. Kubernetes manages far more than containers: networking (Services, Ingress), configuration (ConfigMaps, Secrets), storage (PersistentVolumes), and traffic routing are all first-class resources.
4. The **same YAML API** describes every workload type — legacy monoliths, microservices, Linux, and Windows apps all use identical tooling and workflow.
5. **Docker Desktop** is the lowest-friction local option (Windows 10/macOS); **K3s** is the right choice on Linux; AKS/EKS work if you need a cloud-hosted lab.
6. `kubectl get nodes` showing `Ready` is the canonical verification that your full stack (cluster → API → CLI) is working.
7. The `kiamol` GitHub repo (`https://github.com/sixeyed/kiamol`) is the single source of truth for all exercise files and lab sample answers — clone it before starting Chapter 2.

---

## Connects To

- **Ch 2 (Pods and Deployments)**: Chapter 1 is pure setup; Chapter 2 is where the first `kubectl apply` commands and YAML manifests appear, building directly on the running cluster created here.
- **Ch 3 (Services and Networking)**: The Services resource mentioned in figure 1.3/1.4 is covered in depth; understanding the cluster abstraction from Ch 1 is a prerequisite.
- **Kubernetes official docs**: `https://kubernetes.io/docs/home/` — architecture, tutorials, and contribution guides.
- **Kubernetes API reference (v1.20)**: `https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20` — full object specifications; bookmark it.
- **CKAD certification**: This book covers approximately 80% of the Certified Kubernetes Application Developer curriculum — Ch 1 sets the conceptual baseline.
- **Learn Docker in a Month of Lunches** (Stoneman, Manning 2020): Recommended prerequisite for readers unfamiliar with images, containers, and registries.
