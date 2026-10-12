# Chapter 21: Running Serverless Functions in Kubernetes

## Core Idea

Serverless on Kubernetes removes the overhead between writing code and having it run in a Pod. Instead of building container images, crafting Deployment YAML, and managing registries, you supply a code file and the platform handles packaging, Pod creation, and triggering. Functions still run as containers in standard Pods and Services — serverless is a deployment and invocation abstraction, not a different runtime model.

The key trade-off vs. cloud serverless (AWS Lambda, Azure Functions): you lose zero-ops auto-scaling but gain portability, unified operations, and integration with your existing cluster tooling (logging, monitoring, RBAC).

---

## Frameworks Introduced

- **Kubeless** — code-first, source-level deployment. You supply a single code file (or zip); Kubeless creates a Function CRD, a Deployment, a Service, and a ConfigMap. An init container compiles the source using the language's native build tools. Triggers are separate CRDs: HTTPTrigger -> Ingress, CronJobTrigger -> CronJob, NATSTrigger -> queue subscription. Best for: rapid iteration with no image build pipeline.

- **Knative** — image-first. You package your function in a Docker image yourself; Knative deploys it. More production-grade, CNCF-adjacent (uses Contour/Envoy ingress), but adds friction in the developer loop. The chapter lab exercises use Knative.

- **Serverless framework** — abstraction layer over a serverless platform. Define functions and triggers in `serverless.yml`; the CLI translates that into Kubeless (or Lambda, or Azure Functions) resources. Adds portability at the cost of an extra YAML spec and Node.js/npm dependency chain. Same Kubeless CRDs are created underneath.

---

## Key Concepts

1. **Function CRD** — Kubeless extends Kubernetes with custom resources for `Function`, `HTTPTrigger`, `CronJobTrigger`, and `NATSTrigger`. The Kubeless controller watches these and creates standard Kubernetes objects.

2. **Init container compilation** — Instead of a pre-built image per function, Kubeless uses an init container with the language's build toolchain (e.g., Java JDK + Maven). The init container reads source from a ConfigMap volume, compiles the output, and writes it to an EmptyDir volume shared with the app container. This removes the need for an image registry with write credentials but increases cold-start time.

3. **ConfigMap as code carrier** — When you deploy a function, Kubeless stores the source code in a ConfigMap mounted into the Pod. This is how the init container accesses the source without an image build.

4. **HTTPTrigger -> Ingress** — Creating an HTTPTrigger CRD causes the Kubeless controller to create an Ingress rule. The function Service is exposed at a path/domain you specify, making it indistinguishable from any other app endpoint at the ingress level.

5. **CronJobTrigger -> CronJob** — A scheduled trigger creates a standard Kubernetes CronJob that calls the function's HTTP endpoint on the specified schedule. Defined as a `CronJobTrigger` custom resource, or by applying YAML directly with `kubectl`.

6. **NATSTrigger -> queue subscription** — A plugin CRD+controller for NATS. The controller subscribes to a topic and calls the function's HTTP endpoint when messages arrive. Enables pub/sub integration: multiple subscribers (existing handlers + new functions) each receive a copy of the message.

7. **Polyglot runtimes** — Kubeless supports Java, Python, Node.js, Go, .NET, PHP, Ballerina, Vert.x, and more. Runtime images vary significantly in size (Go < 60 MB vs. Node.js ~600 MB), which affects scale-out speed and attack surface.

8. **Dependency management** — Specify a language-native dependency file alongside code (`package.json` for Node.js, `requirements.txt` for Python). The init container fetches dependencies using the runtime's package manager.

9. **Function signature** — Every Kubeless function, regardless of language, receives two arguments: `event` (trigger type, data payload) and `context` (runtime metadata, timeout). The return value is sent as the HTTP response for HTTP-triggered calls.

10. **Serverless at run-time is just Kubernetes** — Once deployed, functions are managed like any other workload. `kubectl logs`, `kubectl get pods`, resource limits, liveness probes, and centralized monitoring all apply unchanged.

---

## Mental Models

**"Serverless = build abstraction, not runtime abstraction."**
At runtime, a serverless function is a Pod with a ClusterIP Service. The serverless platform only abstracts the steps between code file and running Pod. Once running, all normal Kubernetes operations apply: scaling, eviction, logging, RBAC.

**"Triggers are thin wrappers over standard Kubernetes resources."**
An HTTP trigger is an Ingress rule. A schedule trigger is a CronJob. A queue trigger is a controller that subscribes and calls the Service's HTTP endpoint. The CRDs exist so you can declare intent at a high level; the controllers translate that into primitives you already understand.

**"Message queues decouple function chains; functions never call each other directly."**
When the todo-api function publishes a NATS message, the audit function does not depend on todo-api. It depends only on the queue topic. Adding a new subscriber (another function) requires no change to existing code, which makes serverless particularly powerful for audit, compliance, and enrichment use cases in event-driven architectures.

---

## Anti-patterns

- **Hundreds of function Pods without resource limits** — Kubeless does not apply resource requests or limits by default. A large number of fine-grained function Pods, each loading a language runtime, will collectively apply significant memory pressure to nodes. The eviction scenarios described in chapter 19 become more likely. Mitigation: set resource blocks in the Function custom resource YAML (must be done manually, not via the CLI).

- **Choosing a heavy runtime for latency-sensitive functions** — Node.js images are ~10x the size of Go images. Larger images slow scale-out and present a larger security surface. Evaluate runtime image sizes before committing to a language for high-throughput functions.

- **Tightly coupling function code to a specific platform API** — Knative and Kubeless invoke functions differently; AWS Lambda differs further. If you write platform-specific init/handler boilerplate without an abstraction layer (Serverless framework), migrating between platforms requires rewriting function code, not just configuration.

---

## Code Examples

Deploy a Java function (single file, no dependencies):
```
kubeless function deploy hello-kiamol --runtime java11 --handler Kiamol.hello --from-file functions/hello-kiamol/hello-kiamol.java
```

Deploy a Node.js function with a dependency file:
```
kubeless function deploy todo-api --runtime nodejs12 --handler server.handler --from-file functions/todo-api/server.js --dependencies functions/todo-api/package.json
```

Deploy a Python function:
```
kubeless function deploy todo-audit --runtime python3.7 --handler audit.handler --from-file functions/todo-audit/audit.py
```

Call a function via the CLI:
```
kubeless function call todo-api --data 'Finish KIAMOL ch21'
```

Call a function via kubectl proxy:
```
curl http://localhost:8080/api/v1/namespaces/default/services/hello-kiamol:http-function-port/proxy/
```

Create a NATS trigger for a function:
```
kubeless trigger nats create todo-audit --function-selector function=todo-audit --trigger-topic events.todo.newitem
```

Python audit function body (listing 21.3 — the entire function):
```python
def handler(event, context):
    print(f"AUDIT @ {event['data']['Item']['DateAdded']}: {event['data']['Item']['Item']}")
```

Node.js API function core (listing 21.2 — key lines):
```javascript
function handler(event, context) {
    var newItemEvent = { Item: { Item: event.data, DateAdded: new Date().toISOString() } }
    nc.publish('events.todo.newitem', newItemEvent)
}
```

Serverless framework spec (`serverless.yml`, listing 21.4):
```yaml
service: todo-api
provider:
  name: kubeless
  runtime: nodejs12
  hostname: api.todo.kiamol.local
plugins:
  - serverless-kubeless
functions:
  todo-api:
    description: 'ToDo list - create item API'
    handler: server.handler
    events:
      - http:
          path: /todos
```

Deploy with Serverless framework (run inside function project folder):
```
npm install
serverless deploy
```

Apply a Function and CronJobTrigger directly via kubectl (no CLI needed):
```
kubectl apply -f functions/todo-mutating-handler/
```

List schedule triggers and the resulting CronJobs:
```
kubectl get cronjobtriggers
kubectl get cronjobs
```

---

## Reference Tables

### Platform Comparison

| Feature | Kubeless | Knative | Serverless Framework |
|---|---|---|---|
| Workflow | Code-first | Image-first | Spec-first (wraps a platform) |
| Build step | Init container (no registry needed) | Must build & push Docker image | Delegates to underlying platform |
| Spec format | Kubeless CLI or Function CRD YAML | Knative Service CRD YAML | `serverless.yml` |
| Trigger types | HTTP, Schedule, NATS, Kafka | HTTP (Knative Serving) | HTTP, queue (via provider plugins) |
| CNCF status (2021) | No | Adjacent (uses CNCF tools) | No |
| Portability | Kubernetes only | Kubernetes only | Multi-cloud (Lambda, Azure, Kubeless, …) |
| Dependency management | Language-native file (package.json, etc.) | Baked into Docker image | Language-native file |

### Trigger to Kubernetes Resource Mapping

| Trigger Type | Kubeless CRD | Kubernetes Resource Created |
|---|---|---|
| HTTP | `HTTPTrigger` | `Ingress` rule |
| Schedule | `CronJobTrigger` | `CronJob` |
| NATS queue | `NATSTrigger` (plugin) | Controller subscribes to topic, calls function Service |
| Kafka queue | `KafkaTrigger` (built-in) | Controller subscribes to topic, calls function Service |
| None (manual) | `Function` only | ClusterIP `Service` (callable via CLI or kubectl proxy) |

---

## Worked Example

### Deploy a to-do API function exposed over HTTP with auditing via NATS

**Goal:** Add a REST API to an existing to-do app without modifying the app. The API publishes to the same NATS queue the app uses internally. A second function audits every new item.

**Step 1 — Install Kubeless CRDs and controllers.**
```
kubectl apply -f kubeless/
kubectl wait --for=condition=ContainersReady pod -l kubeless=controller -n kubeless
```
Verify CRDs exist: `kubectl get crd` shows `functions.kubeless.io`, `httptriggers.kubeless.io`, `cronjobtriggers.kubeless.io`.

**Step 2 — Deploy the to-do app (web + NATS + DB + save-handler).**
```
kubectl apply -f todo-list/config/ -f todo-list/db/ -f todo-list/msgq/ -f todo-list/web/ -f todo-list/save-handler/
kubectl wait --for=condition=ContainersReady pod -l app=todo-list
```

**Step 3 — Deploy the Node.js API function with dependencies.**

The function (`server.js`) uses the `nats` npm package to publish messages. The dependency is declared in `package.json`.
```
kubectl exec -it kubeless-cli -- sh
cd /kiamol/ch21
kubeless function deploy todo-api \
  --runtime nodejs12 \
  --handler server.handler \
  --from-file functions/todo-api/server.js \
  --dependencies functions/todo-api/package.json
kubectl wait --for=condition=ContainersReady pod -l function=todo-api
```

What Kubeless created: a `Function` CRD, a `Deployment` (one Pod), a `ConfigMap` with the source code, and a `ClusterIP` Service.

**Step 4 — Test the function directly via CLI.**
```
kubeless function call todo-api --data 'Test item'
```
Check that the save-handler received the message: `kubectl logs -l component=save-handler --tail 1`.

**Step 5 — Expose via HTTP trigger and Ingress.**
```
exit
kubectl apply -f ingress-nginx/
kubectl apply -f todo-list/web/ingress/ -f functions/todo-api/ingress/
```

Kubeless creates an `Ingress` rule pointing the path `/todos` on `api.todo.kiamol.local` to the `todo-api` Service. After updating `/etc/hosts`:
```
curl --data 'New task' http://api.todo.kiamol.local/todos
```

Browse `http://todo.kiamol.local/list` — the new item appears, added by the function, invisible to the app.

**Step 6 — Add a NATS audit trigger.**
```
kubectl apply -f kubeless/nats-trigger/
kubectl wait --for=condition=ContainersReady pod -l kubeless=natstrigger-controller -n kubeless
kubectl exec -it kubeless-cli -- sh
kubeless function deploy todo-audit \
  --runtime python3.7 \
  --handler audit.handler \
  --from-file functions/todo-audit/audit.py
kubectl wait --for=condition=ContainersReady pod -l function=todo-audit
kubeless trigger nats create todo-audit \
  --function-selector function=todo-audit \
  --trigger-topic events.todo.newitem
exit
```

**Step 7 — End-to-end verification.**
```
curl --data 'Verify audit chain' http://api.todo.kiamol.local/todos
kubectl logs -l function=todo-audit | grep AUDIT
```

Expected log: `AUDIT @ <timestamp>: Verify audit chain`

The flow: curl -> Ingress -> todo-api Service -> todo-api Pod (publishes NATS message) -> NATS controller invokes todo-audit Pod -> audit log written. The existing save-handler also receives the same NATS message and persists the item.

---

## Key Takeaways

1. Serverless on Kubernetes is a deployment abstraction: functions still run as Pods with Services, managed by the same tools as any other workload.

2. Kubeless uses init containers to compile source code at Pod startup, eliminating the need for a container image build pipeline or registry write access.

3. HTTP triggers create Ingress rules; schedule triggers create CronJobs; queue triggers use a controller that subscribes and calls the function's Service. All triggers map to standard Kubernetes resources.

4. Event-driven architectures make serverless functions naturally additive: new functions subscribe to existing queues without any change to existing components.

5. Running many function Pods without resource limits risks node memory pressure and eviction; plan resource requests when deploying large numbers of functions.

6. The Serverless framework decouples function definitions from the underlying platform, enabling potential migration between Kubeless, Knative, Lambda, and Azure Functions with minimal code changes.

7. At runtime, serverless functions integrate with existing cluster infrastructure (logging, monitoring, RBAC, ingress) identically to any other application.

---

## Connects To

- **Chapter 15 (Ingress)** — HTTP triggers generate Ingress rules; understanding ingress controllers is required to expose functions externally.
- **Chapter 19 (Resource management and eviction)** — Memory pressure from many function Pods without resource limits triggers the eviction scenarios covered there.
- **Chapter 20 (CRDs and Operators)** — Kubeless itself is built on the CRD + controller pattern from chapter 20; `Function`, `HTTPTrigger`, and `CronJobTrigger` are custom resources managed by Kubeless controllers.
- **Chapter 20 (NATS messaging)** — The to-do app messaging architecture introduced in chapter 20 is the integration point for queue-triggered functions in this chapter.
- **Chapter 8 (CronJobs)** — Schedule triggers produce standard `CronJob` objects; the CronJob mechanics are the same.
- **Chapter 7 (Init containers and EmptyDir volumes)** — Kubeless's compile-at-startup pattern relies on init containers writing compiled output to an EmptyDir volume shared with the app container.
