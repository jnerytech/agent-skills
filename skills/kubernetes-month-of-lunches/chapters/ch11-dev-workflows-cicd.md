# Chapter 11: App Development—Developer Workflows and CI/CD

## Core Idea

Kubernetes changes how software is built and delivered. The chapter examines two ends of a spectrum: a **Docker-centric workflow** where containers are present in every environment including the developer's local machine, and a **Kubernetes-as-a-Service (KaaS) / PaaS workflow** where containers are pushed entirely to the CI/CD outer loop and developers never touch Docker. Understanding where your organization sits on that spectrum—and the trade-offs of each—is the central decision the chapter equips you to make.

---

## Frameworks Introduced

### Docker Developer Workflow

**What:** Developers use Docker (and Docker Compose) locally to build images, then deploy those images to a local Kubernetes cluster using kubectl. Container artifacts (Dockerfile, Compose file, Kubernetes manifests) are part of every project.

**When:** Teams willing to invest in container literacy at every level; projects that need fine-grained control over image construction and size.

**How:**
1. Clone the repo.
2. `docker-compose build` to build the image.
3. `kubectl apply` to deploy to local cluster.
4. Rebuild and delete the Pod manually when iterating on changes (because Kubernetes does not re-pull an unchanged image name/tag).

**Why it can fail:** Developers hit subtle friction points—imagePullPolicy defaults, mutable image tags not triggering Pod replacements, need to manually delete Pods—that are not intuitive and frustrate those unfamiliar with container internals.

---

### Kubernetes-as-a-Service (PaaS) Workflow

**What:** Container tooling lives entirely in the CI/CD pipeline. Developers push source code to Git; a pipeline (Jenkins + BuildKit + Buildpacks) builds the image, pushes it to a registry, and deploys to a test namespace. Developers never run Docker or kubectl.

**When:** Organizations that want to centralize container expertise in a platform team; polyglot environments; clusters using non-Docker runtimes.

**How:**
1. Developer commits and pushes source code to Git.
2. Jenkins detects the push, calls BuildKit (Docker-free image builder) using Buildpacks as the build frontend.
3. BuildKit pushes the resulting image to a private registry.
4. Jenkins runs `helm upgrade --install` targeting the test namespace.

**Why it can fail:** Complexity shifts from developers to the platform team. The toolchain (BuildKit + Buildpacks bridge) is less mature than Docker; images produced by Buildpacks are much larger (1 GB vs 95 MB for a tuned Docker image). Debugging pipeline failures requires deep knowledge of multiple moving parts. Bespoke pipelines are harder to maintain than standard Dockerfiles.

---

## Key Concepts

1. **Inner loop vs outer loop** — The inner loop is the developer's local workflow (code → build → run locally). The outer loop is the CI/CD pipeline (push → build → test → deploy). The Docker workflow puts containers in both loops; PaaS pushes them only to the outer loop.

2. **imagePullPolicy** — Controls when Kubernetes pulls an image from the registry. `Always` forces a pull every time a Pod starts (useful for `:latest`). `IfNotPresent` uses the local image cache if available (required for Docker-workflow local development). Default behavior: if the tag is `:latest` or absent, Kubernetes always tries to pull; otherwise it uses the cached image.

3. **Mutable image tags** — Replacing an image in the registry under the same name and tag does not trigger a Pod replacement in Kubernetes, because the Pod spec has not changed. The workaround is to delete the Pod manually (forcing the Deployment controller to recreate it) or use unique build-numbered tags in CI.

4. **BuildKit** — An open-source image builder from the Docker team that can run as a standalone server inside the cluster. It builds container images from Dockerfiles or via Buildpacks without requiring a Docker Engine or daemon. Accepts build requests over TCP.

5. **Buildpacks (CNCF)** — A technology pioneered by Heroku that detects the application language, compiles the app inside a build container, and packages the output on top of a runtime base image—no Dockerfile required. Uses the same concept as multi-stage Dockerfiles but with zero explicit Dockerfile authoring.

6. **Private image registry + pull Secret** — In multi-node clusters, every node must be able to pull the application image. For private registries (Docker Hub private repos, ACR, ECR), Kubernetes needs credentials stored as a `docker-registry` type Secret. The Secret is referenced in the Pod spec or mounted into the build Pod.

7. **Namespaces** — A grouping mechanism that creates virtual clusters within a real cluster. Every Kubernetes object belongs to a namespace. Common patterns: one namespace per environment (dev/test/uat/prod), one namespace per developer on a shared dev cluster, one namespace per product. Deleting a namespace deletes all its resources. Networking is flat (Pods across namespaces can communicate through Services), but controllers only watch resources in their own namespace.

8. **Contexts** — A kubectl configuration concept that bundles a cluster endpoint, authentication credentials, and a default namespace into a named profile. Switching contexts changes both the cluster target and the default namespace. Stored in `~/.kube/config`. Managed Kubernetes services typically provide a command to merge a new context into your local config.

9. **Helm in pipelines** — `helm upgrade --install --atomic` combines install and upgrade into a single idempotent command. `--atomic` rolls back automatically if the deployment fails. Image-specific values (registry server, user, build number) are injected at deploy time via `--set`, so the Helm chart itself stays generic.

10. **Gogs** — A lightweight, self-hosted Git server that can run as a Kubernetes Deployment. Useful for creating a reproducible, offline-capable CI/CD demo environment inside the cluster.

---

## Mental Models

### The Complexity Budget

Every workflow has a fixed amount of complexity—the Docker approach distributes it across all development teams (everyone must understand Dockerfiles, Compose, kubectl, and image tagging quirks). The PaaS approach centralizes it in the platform/ops team and the CI/CD pipeline toolchain. Neither eliminates complexity; each chooses where it lives. Centralizing complexity reduces cognitive load for feature teams but creates a bottleneck and a single point of failure in the platform team.

### Outer Loop as the Trust Boundary

In the PaaS model, the pipeline is the only place where container knowledge is exercised. This means: (a) developers can be more productive in their native tooling, but (b) feedback cycles are longer because changes must be pushed and built before the developer sees them running in a container. The Docker workflow tightens the feedback loop at the cost of requiring every developer to understand containers. Choose based on how fast you need that loop to close and how much container expertise your teams realistically have.

### Image Identity in Kubernetes

Kubernetes tracks desired state via the Pod spec. If the image field in a Pod spec does not change (same name and tag), Kubernetes considers the workload up-to-date and takes no action—even if the registry image has been silently replaced. Always use unique, build-numbered image tags in CI/CD (e.g., `bulletin-board:42-kiamol`) to guarantee that each build produces a new Pod spec that Kubernetes will act on.

---

## Anti-patterns

- **Using `:latest` tags in manifests** — Kubernetes may always pull from the registry (`imagePullPolicy: Always` is implied for `:latest`), which conflicts with local Docker workflow where you want the cached local image. Use explicit versioned tags and set `imagePullPolicy: IfNotPresent` for local dev.

- **Rebuilding an image and re-running `kubectl apply` without changing the tag** — The Pod spec is unchanged; Kubernetes does nothing. Developers waste time wondering why their changes aren't visible. Fix: delete the Pod manually, or (in CI) use a unique build-numbered tag.

- **Deploying to a shared cluster without namespaces** — Name collisions between teams and environments, accidental overwrites, and inability to apply per-environment resource limits. Always assign workloads to a dedicated namespace.

- **Centralizing all container expertise in one team without investing in shared knowledge** — Creates resentment toward the platform team and a culture where most engineers cannot debug their own deployments. Consider a hybrid approach: encourage container literacy while centralizing the hardest parts.

- **Trusting immature bridge tooling in production** — The BuildKit-Buildpacks bridge used in the chapter is described as a "proof of concept." Using experimental glue components in production pipelines introduces risk. Prefer proven tools (Jenkins X, GitLab CI) if going Docker-free.

---

## Code Examples

```bash
# Build app image with Docker Compose (Docker workflow inner loop)
docker-compose -f bulletin-board/docker-compose.yml build

# Deploy to local Kubernetes
kubectl apply -f bulletin-board/kubernetes/

# Force a Pod replacement to pick up a new local image
kubectl delete pod -l app=bulletin-board

# Create a dedicated namespace
kubectl create namespace kiamol-ch11-test

# Deploy into a specific namespace via flag
kubectl apply -f sleep.yaml --namespace kiamol-ch11-test

# List resources across all namespaces
kubectl get deploy -l app=sleep --all-namespaces

# Set the default namespace for the current context
kubectl config set-context --current --namespace=kiamol-ch11-test

# Reset default namespace to cluster default
kubectl config set-context --current --namespace=

# List and inspect configured contexts
kubectl config get-contexts
kubectl config view

# Create a docker-registry Secret for private registry pull
kubectl create secret docker-registry registry-creds \
  --docker-server=$REGISTRY_SERVER \
  --docker-username=$REGISTRY_USER \
  --docker-password=$REGISTRY_PASSWORD

# Build image using BuildKit + Buildpacks (no Docker, no Dockerfile)
buildctl build \
  --frontend=gateway.v0 \
  --opt source=kiamol/buildkit-buildpacks \
  --local context=src \
  --output type=image,name=kiamol/ch11-bulletin-board:buildkit

# CI build stage: build and push with build-numbered tag (build.sh in pipeline)
buildctl --addr tcp://buildkitd:1234 build \
  --frontend=gateway.v0 \
  --opt source=kiamol/buildkit-buildpacks \
  --local context=src \
  --output type=image,name=${REGISTRY_SERVER}/${REGISTRY_USER}/bulletin-board:${BUILD_NUMBER}-kiamol,push=true

# CI deploy stage: Helm upgrade/install into test namespace (run.sh in pipeline)
helm upgrade --install --atomic \
  --set registryServer=${REGISTRY_SERVER},registryUser=${REGISTRY_USER},imageBuildNumber=${BUILD_NUMBER} \
  --namespace kiamol-ch11-test \
  bulletin-board helm/bulletin-board

# Check which image is running in test namespace Pods
kubectl get pods -n kiamol-ch11-test -l app.kubernetes.io/name=bulletin-board \
  -o=custom-columns=NAME:.metadata.name,IMAGE:.spec.containers[0].image
```

**Pod spec snippet — explicit imagePullPolicy for local development:**
```yaml
spec:
  containers:
  - name: bulletin-board
    image: kiamol/ch11-bulletin-board:dev
    imagePullPolicy: IfNotPresent   # Use local cache; do not pull from registry
```

**Namespace spec in YAML:**
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: kiamol-ch11-uat
```

**Deployment targeting a named namespace:**
```yaml
metadata:
  name: sleep
  namespace: kiamol-ch11-uat   # Namespace must exist before apply
```

---

## Reference Tables

### Docker Developer Workflow vs Kubernetes-as-a-Service (PaaS) Workflow

| Dimension | Docker Workflow | KaaS / PaaS Workflow |
|---|---|---|
| Container tools on dev machine | Docker, Docker Compose, kubectl required | None required |
| Where containers enter the process | Inner loop (local build and run) | Outer loop (CI/CD pipeline only) |
| Build artifact | Dockerfile + Compose file + K8s manifest | Source code only; pipeline handles rest |
| Image builder | Docker Engine (mature, widely used) | BuildKit + Buildpacks (less mature) |
| Image size | Fine-tunable (e.g., 95 MB with multi-stage) | Buildpacks baseline can be 1 GB+ |
| Feedback loop speed | Fast (local rebuild + delete Pod) | Slower (requires push → pipeline → deploy) |
| Container knowledge required | All team members | Centralized in platform/ops team |
| Portability of skills | High (Docker/K8s skills are universal) | Lower (bespoke pipeline knowledge) |
| Flexibility | High (any Dockerfile customization) | Lower (Buildpacks are more prescriptive) |
| Complexity location | Distributed across all teams | Centralized in pipeline toolchain |
| Debugging ownership | Any developer can investigate | Requires platform team involvement |
| Docker-free clusters | Not straightforward | Fully supported |

---

## Worked Example

**Scenario: A code change is pushed through the full PaaS pipeline and deployed to the test namespace.**

**Infrastructure already in place:**
- Gogs Git server running in the cluster (deployed via `kubectl apply -f infrastructure/gogs.yaml`)
- BuildKit server running as a Deployment (`buildkitd`) in the cluster
- Registry credentials stored as a `docker-registry` Secret named `registry-creds`
- Jenkins Deployment running with `kubectl` and BuildKit CLI installed, authenticated to the cluster via the in-Pod service account token and the registry Secret mounted at `/root/.docker`

**Step 1: Developer makes a code change and pushes to Git.**
```bash
git add bulletin-board/src/backend/events.js
git commit -m 'Add event descriptions'
git push gogs
```
Jenkins polls Gogs and detects the new commit within one minute, triggering the pipeline.

**Step 2: Jenkins pipeline — build stage (`build.sh`).**
The Jenkins Pod runs `buildctl` targeting the BuildKit server over TCP:
```bash
buildctl --addr tcp://buildkitd:1234 build \
  --frontend=gateway.v0 \
  --opt source=kiamol/buildkit-buildpacks \
  --local context=src \
  --output type=image,name=${REGISTRY_SERVER}/${REGISTRY_USER}/bulletin-board:${BUILD_NUMBER}-kiamol,push=true
```
- BuildKit fetches the Buildpacks integration component.
- Buildpacks detects the Node.js app, compiles it in a build container, and packages the output on a Node.js runtime base image.
- The resulting image is pushed directly from BuildKit to the private registry with a unique build-numbered tag (e.g., `sixeyed/bulletin-board:2-kiamol`).
- No Dockerfile is used. No Docker daemon is required on any node.

**Step 3: Jenkins pipeline — deploy stage (`run.sh`).**
```bash
helm upgrade --install --atomic \
  --set registryServer=${REGISTRY_SERVER},registryUser=${REGISTRY_USER},imageBuildNumber=${BUILD_NUMBER} \
  --namespace kiamol-ch11-test \
  bulletin-board helm/bulletin-board
```
- Helm renders the chart with the new build-numbered image tag.
- The Pod spec changes (new image name), so Kubernetes terminates the old Pod and starts a new one.
- The new Pod pulls the image from the private registry using the `registry-creds` Secret.
- `--atomic` ensures that if the new Pod fails to become Ready, Helm automatically rolls back.

**Step 4: Verification.**
```bash
kubectl get pods -n kiamol-ch11-test -l app.kubernetes.io/name=bulletin-board \
  -o=custom-columns=NAME:.metadata.name,IMAGE:.spec.containers[0].image
```
The IMAGE column shows the build-2 tag, confirming the new version is running. The developer browses to the test URL and sees the updated events list—without ever having run Docker, kubectl, or Helm locally.

---

## Key Takeaways

1. The inner loop (local dev) and outer loop (CI/CD) are distinct; your workflow choice determines which loop containers enter.
2. `imagePullPolicy: IfNotPresent` is essential in local Docker workflows to prevent Kubernetes from bypassing your locally built image.
3. Mutable image tags are a Kubernetes footgun: a re-pushed image under the same tag does not update running Pods. Use unique, build-numbered tags in pipelines.
4. Namespaces are the primary isolation primitive for sharing a cluster across environments and teams; they are also resource and security boundaries.
5. Contexts bundle cluster endpoint + credentials + default namespace—use them to switch between environments without error-prone namespace flags on every command.
6. The PaaS/KaaS approach reduces developer friction but trades Dockerfile simplicity and image size control for a more complex, less mature pipeline toolchain.
7. The right workflow is a culture decision as much as a technology decision: centralized expertise vs. distributed container literacy each carry organizational trade-offs.

---

## Connects To

- **Chapter 3** — Namespaces and fully qualified DNS names for Services (the first introduction of namespaces).
- **Chapter 10 (Helm)** — `helm upgrade --install --atomic` is the deploy mechanism in the CI/CD pipeline; Helm charts parameterize the image tag for pipeline injection.
- **Chapter 12 (Self-healing and probes)** — Liveness and readiness probes interact with `--atomic` rollbacks in Helm; a failing probe triggers the automatic rollback.
- **Chapter 8 (StatefulSets/Jobs)** — Pipeline build steps in Jenkins are themselves workloads that could be modeled as Jobs.
- **Appendix A (Learn Docker in a Month of Lunches)** — Referenced for multi-stage Dockerfile patterns and Docker Compose basics underpinning the Docker workflow.
