# Chapter 9: WebAssembly on Kubernetes

## Core Idea
WebAssembly (Wasm) is the third wave of cloud computing (VMs → containers → Wasm), each wave delivering smaller, faster, more portable apps. Wasm is a binary instruction set architecture (ISA) — like ARM, x86, RISC-V — that languages compile to. A Wasm binary runs on any host with a **Wasm runtime**. Kubernetes clusters using **containerd** can run Wasm workloads by swapping `runc` + standard shim for a **Wasm runtime + Wasm shim**, then scheduling with node labels + **RuntimeClass**.

## Frameworks Introduced
- **Wasm / WebAssembly**: write `Wasm` not `WASM`; "Wasm" is short for WebAssembly, not an acronym. Use cases: WebAssembly outside the browser / on the server / in the cloud / at the edge.
- **WASI** (WebAssembly System Interface): lets sandboxed Wasm apps securely access external services (key-value stores, networks, host env). Vital for Wasm outside the browser. WASI Preview 2 in development at time of writing.
- **runwasi** (github.com/containerd/runwasi): the code that interfaces a Wasm shim with containerd. Each shim embeds runwasi + a specific Wasm runtime.
- **Spin** (Fermyon): popular Wasm framework — runtime + build/scaffold tooling (`spin new`, `spin build`).
- Other runtimes/shims seen: Slight, WasmEdge, lunatic, wws.

## Key Concepts (5-10)
1. **Deny-by-default sandbox**: Wasm apps run in a sandbox where everything is denied unless explicitly allowed by the runtime. Containers are allow-by-default (everything wide open, shared kernel).
2. **Battle-hardened isolation**: the Wasm sandbox was hardened running untrusted code on the web.
3. **True portability**: containers are architecture-dependent (one OS+arch per image → image sprawl). Wasm = build once, run anywhere with a runtime, including IoT/edge/exotic architectures.
4. **Sub-second startup**: VMs start in minutes, containers in seconds, Wasm in ~10ms or less (microseconds with optimization). Enables true scale-to-zero and serverless.
5. **Shim architecture**: a Wasm shim is a single binary = shim code (runwasi) + embedded Wasm runtime. Differs from runc's separate shim.
6. **Shim naming convention** (containerd-mandated): `containerd-shim` prefix + runtime name + version. Example: `containerd-shim-spin-v1`.
7. **containerd unchanged**: all Wasm changes sit *below* containerd; one unchanged containerd instance per node. Everything below containerd is hidden from Kubernetes — fully supported config.
8. **RuntimeClass + node labels**: how Kubernetes schedules Wasm Pods to nodes with the correct shim. RuntimeClass has a `scheduling.nodeSelector` (matches node label) and a `handler` (the runtime/shim name).
9. **OCI packaging**: Wasm binary is packaged as an OCI image (`FROM scratch`) so Docker/registries/Kubernetes can handle it. At runtime the app+runtime execute in a minimal container (just namespaces + cgroups, no filesystem).

## Mental Models (Wasm as next-gen lightweight workload vs containers)
- **Compilation target**: instead of compiling to "Linux on ARM", you compile to **Wasm**. The runtime is the portability layer.
- **Third wave**: VMs (isolation, minutes) → containers (density, seconds) → Wasm (sub-second, tiny, sandboxed).
- **Side-by-side**: Linux containers and Wasm containers run together in the same cluster — even the same Pod. Wasm is additive, not a replacement.
- **Minimal container wrapper**: Wasm doesn't *need* a container, but K8s/Docker tooling does, so it gets the thinnest possible wrapper.

## Anti-patterns
- Writing `WASM` (incorrect capitalization) — it's `Wasm`.
- Assuming containers are portable — they are architecture-dependent.
- Using a standard k3d/cluster image and expecting Wasm to work — most distros don't yet bundle Wasm shims; you need an image with shims pre-installed.
- Installing a shim but forgetting to **register** it in containerd's `config.toml` — presence alone isn't enough.
- Choosing Wasm for traditional cloud apps with heavy networking, heavy I/O, or many service connections — containers are still the better fit (at time of writing).
- Forgetting to reset kubectl context after creating the dedicated `wasm` cluster.

## Code Examples

Install Wasm compile target for Rust:
```
$ rustup target add wasm32-wasi
```

RuntimeClass (selects labeled nodes, points handler at the Spin shim):
```
kubectl apply -f - <<EOF
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: rc-spin
scheduling:
  nodeSelector:
    wasm: "yes"
handler: spin
EOF
```

Label a node so the scheduler knows it can run Wasm:
```
$ kubectl label nodes k3d-wasm-agent-1 wasm=yes
```

Pod/Deployment referencing the RuntimeClass:
```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: wasm-spin
spec:
  replicas: 3
  template:
    metadata:
      labels:
        app: wasm
    spec:
      runtimeClassName: rc-spin          # <== references the RuntimeClass
      containers:
      - name: testwasm
        image: nigelpoulton/k8sbook:wasm-0.1   # <== Wasm OCI image
        command: ["/"]
```

Dockerfile to package the Wasm binary as an OCI image:
```
FROM scratch
COPY /target/wasm32-wasi/release/tkb_wasm.wasm .
COPY spin.toml .
```

Build the OCI image with the Wasm platform:
```
$ docker build --platform wasi/wasm --provenance=false \
    -t nigelpoulton/k8sbook:wasm-0.1 .
```

Verify shims and registration on a node:
```
$ ls /bin | grep shim
containerd-shim-lunatic-v1
containerd-shim-runc-v2          # default for Linux containers
containerd-shim-slight-v1
containerd-shim-spin-v1          # the Spin Wasm shim
containerd-shim-wws-v1

$ containerd --config /var/lib/rancher/k3s/agent/etc/containerd/config.toml \
    config dump | grep spin
```

kubectl commands:
```
$ kubectl get runtimeclass        # NAME=rc-spin HANDLER=spin
$ kubectl get pods -o wide        # confirm all replicas land on the labeled node
$ curl http://localhost:5005/tkb  # -> The Kubernetes Book loves Wasm!
```

## Reference Tables

Wasm vs Containers:
| Attribute   | Wasm                          | Linux Containers                  |
|-------------|-------------------------------|-----------------------------------|
| Size        | Tiny (~620kB example image)   | Several MB+ for hello world       |
| Speed       | Sub-second (~10ms, even µs)   | Seconds to start                  |
| Isolation   | Deny-by-default sandbox       | Allow-by-default, shared kernel   |
| Portability | True build-once-run-anywhere  | Architecture-dependent (one OS+arch per image) |
| Best for    | Event handlers, serverless, IoT/edge, plugins/extensions, scale-to-zero | Traditional apps w/ heavy networking, I/O, many service deps |

The three waves:
| Wave | Tech       | Start time | Trait                         |
|------|------------|------------|-------------------------------|
| 1    | VMs        | Minutes    | Strong isolation              |
| 2    | Containers | Seconds    | Density, easy to copy         |
| 3    | Wasm       | Sub-second | Tiny, portable, sandboxed     |

Deploy workflow (containerd cluster):
| Step | Action |
|------|--------|
| 1 | Write app, compile to Wasm binary |
| 2 | Package Wasm binary as OCI image, push to registry |
| 3 | Install a Wasm shim on ≥1 node |
| 4 | Create a RuntimeClass specifying the Wasm shim |
| 5 | Create a Pod using the Wasm image |
| 6 | Reference the RuntimeClass in the Pod |
| 7 | Deploy to Kubernetes |

## Worked Example
Deploy a Wasm workload to a Wasm-enabled node:
1. Scaffold and build: `spin new tkb-wasm -t http-rust` (path `/tkb`), edit `src/lib.rs` to return text, `spin build` → produces `tkb_wasm.wasm` in `target/wasm32-wasi/release/`.
2. Strip leading path in `spin.toml`: `source = "tkb_wasm.wasm"` (was the release path), so the runtime finds it at `/` inside the container.
3. `docker build --platform wasi/wasm --provenance=false -t .../k8sbook:wasm-0.1 .` then `docker push`.
4. Build Wasm cluster: `k3d cluster create wasm --image ghcr.io/deislabs/containerd-wasm-shims/examples/k3d:v0.10.0 -p "5005:80@loadbalancer" --agents 2` (special image with shims pre-installed).
5. Confirm on a worker: containerd running (`ps | grep containerd`), shims present (`ls /bin | grep shim`), shims registered in `config.toml`.
6. `kubectl label nodes k3d-wasm-agent-1 wasm=yes`, then apply the `rc-spin` RuntimeClass.
7. `kubectl apply -f .../wasm/app.yml` (Deployment w/ `runtimeClassName: rc-spin` + Service + Ingress). All 3 replicas schedule to the labeled `agent-1` node.
8. Test: `curl http://localhost:5005/tkb` → `The Kubernetes Book loves Wasm!`
9. Clean up: `k3d cluster delete wasm`, `kubectl delete runtimeclass rc-spin`, `docker rmi`, reset kubectl context.

## Key Takeaways (3-7)
1. Wasm is a compile target/ISA — compile once to a Wasm binary, run anywhere there's a Wasm runtime.
2. Wasm apps are smaller, faster, more portable, and more secure (deny-by-default) than Linux containers — but can't yet do everything containers can.
3. On containerd-based Kubernetes, Wasm runtimes are implemented as **containerd shims** (single binary = runwasi + embedded runtime), named `containerd-shim-<runtime>-v<n>`.
4. To run Wasm: install + register a shim on a node, label the node, and create a **RuntimeClass** whose `nodeSelector` matches the label and whose `handler` names the shim. Pods reference it via `runtimeClassName`.
5. Wasm binaries are packaged as OCI images (`FROM scratch`, `--platform wasi/wasm`) so existing Docker/registry/Kubernetes tooling applies.
6. Alternatives exist: `crun` instead of containerd; the **Kwasm** project adds Wasm support to existing clusters.

## Connects To
- **Ch 3** (installing Docker Desktop & k3d — prerequisite tooling).
- **containerd / runc / shim architecture** (the CRI layer Kubernetes delegates low-level container work to).
- **Pods & Deployments** — Wasm Pods are scheduled like regular containers but carry `runtimeClassName`.
- **Scheduling** — node labels + nodeSelector drive placement of Wasm workloads.
- **Services & Ingress** — the sample app fronts the Wasm Deployment with a ClusterIP Service + Ingress.
