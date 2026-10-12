# Chapter 1: Kubernetes primer

## Core Idea
Kubernetes is an orchestrator of containerized, cloud-native microservices apps — it deploys and manages applications packaged as containers so they can scale, self-heal, and update automatically, while abstracting the underlying cloud/datacenter infrastructure.

## Frameworks Introduced
- **Decoding "Kubernetes is an orchestrator of containerized cloud-native microservices apps"**: Translate the jargon term-by-term to understand the value proposition.
  - When to use: Explaining Kubernetes to newcomers or scoping what it actually does.
  - How: Orchestrator (deploys + reacts to change) → Containerized (packaged as image, run as container) → Cloud-native (auto-scale, self-heal, auto-update/rollback) → Microservices (independent small parts). Result: "Kubernetes deploys and manages applications packaged as containers that can easily scale, self-heal, and be updated."

- **OS-of-the-cloud analogy**: Map Kubernetes onto how a server OS works.
  - When to use: Justifying hybrid-cloud, multi-cloud, and migration strategies.
  - How: Linux/Windows abstract server resources (CPU, memory, storage, network) and schedule processes; Kubernetes abstracts cloud resources and schedules application microservices. Developers no longer care which CPU core / DIMM / flash chip; with K8s they no longer care which compute node, failure zone, or storage volume.

## Key Concepts
- **Orchestrator**: A platform that deploys applications and dynamically responds to change (scaling, self-healing, rolling updates/rollbacks) with minimal human involvement after initial config.
- **Containerization**: Packaging an app plus dependencies as an image, then running it as a container; smaller/faster/more portable than VMs but does not fully replace them.
- **Cloud-native**: An app possessing cloud-like features (auto-scaling, self-healing, automated updates, rollbacks) — merely running in the public cloud does NOT make an app cloud-native.
- **Microservices**: An app built from many small, specialized, independent parts, each typically deployed as its own container with its own team and release cycle.
- **CRI (Container Runtime Interface)**: The Kubernetes interface that makes the low-level container runtime pluggable, so you can swap runtimes for isolation vs. performance.
- **containerd**: Default runtime ("container dee") in most new clusters; a stripped-down, K8s-optimized version of Docker that runs Docker-built images.
- **OCI (Open Container Initiative)**: Standards for images and containers that Docker, containerd, and Kubernetes all implement, ensuring interoperability.
- **CNCF (Cloud Native Computing Foundation)**: The body that owns Kubernetes (open-sourced 2014, Apache 2.0 license); https://www.cncf.io.
- **Borg & Omega**: Google's in-house container orchestrators; Kubernetes shares "DNA"/family history with them but is NOT an open-source port of either.
- **K8s**: Common shorthand ("kates") — the 8 replaces the eight letters between "K" and "s".

## Mental Models
- Think of containers as the next generation of VMs — but expect both to run side-by-side; containers are first choice for *new* apps, not a wholesale VM replacement.
- Use the OS analogy when deciding cloud strategy: if Linux frees you from caring about hardware, Kubernetes frees you from caring about which cloud — enabling deploy-on-AWS-today, migrate-tomorrow.
- Treat each microservice as an independently scalable, deployable unit: scaling = adding/removing containers, not rebuilding the monolith.

## Anti-patterns
- **Calling a lift-and-shift app "cloud-native"**: Running a regular app in the public cloud gives it none of the auto-scaling/self-healing/rollback traits that define cloud-native.
- **Assuming containers replace VMs**: They coexist in most cloud-native environments; treating them as a full replacement misreads real-world deployments.
- **Treating Kubernetes as "open-source Borg"**: It only shares heritage with Borg/Omega — assuming feature parity or identical design is wrong.

## Reference Tables

Industry jargon decoded:

| Term | Meaning |
|------|---------|
| Orchestrator | Deploys apps + dynamically reacts (scale, self-heal, rolling update/rollback) |
| Containerized | App+deps packaged as image, run as container |
| Cloud-native | Has auto-scale, self-heal, automated update/rollback |
| Microservices | App = many small, independent, separately-deployed services |

Runtime / orchestrator history:

| Item | Status |
|------|--------|
| Docker as K8s runtime | Removed in Kubernetes **1.24** (bloated/overkill) |
| containerd | Default runtime in most new clusters |
| Docker Swarm / Mesosphere DCOS / Kubernetes | Competed 2016–2017; **Kubernetes won**; Swarm still active for small/simple setups |
| K8s v1.0 | Shipped July 2015; ~v1.29 at time of writing; ~3 releases/year |

## Worked Example
The author walks through an **e-commerce app** with six features: web front-end, catalog, shopping cart, authentication, logging, store. To make it a microservices app you design, develop, deploy, and manage each feature as its own small app — yielding six microservices. The common pattern is one (or more) container per microservice: multiple web front-end containers, multiple catalog containers, etc. This gives each part its own dev team and release cycle, and scaling any part is simply adding or removing that microservice's containers. He also illustrates a **four-node cluster running multiple container runtimes** (some nodes with more than one runtime, fully supported via CRI) — the same kind of config used later to run a WebAssembly/Wasm app in Chapter 14.

## Key Takeaways
1. Kubernetes does two enduring jobs: (1) abstracts infrastructure like AWS, and (2) simplifies moving apps between clouds — the core reasons it matters.
2. The runtime layer is pluggable via CRI; pick runtimes for isolation vs. performance, and don't expect Docker itself to be the runtime (removed in 1.24).
3. Interoperability rests on OCI — Docker, containerd, and K8s all consume OCI images/containers.
4. "Cloud-native" is a set of behaviors (auto-scale, self-heal, auto-update/rollback), not a location.
5. Adopt microservices for independent scaling, releasing, and team ownership — one container per service is the default pattern.
6. Kubernetes is CNCF-owned, Apache 2.0, born from Google's hyper-scale container experience (Borg/Omega lineage, not a clone).

## Connects To
- **Ch 14**: Multi-runtime node configuration is used to deploy a WebAssembly (Wasm) app.
- **OCI standard**: External spec for image/container interoperability across Docker, containerd, Kubernetes.
- **CRI**: Kubernetes interface decoupling the orchestrator from any specific runtime.
- **CNCF / Apache 2.0**: Governance and licensing context for the whole platform.
