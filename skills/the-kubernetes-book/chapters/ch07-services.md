# Chapter 7: Kubernetes Services

## Core Idea
Pods are ephemeral and unreliable — they're deleted on scale-down, rolling updates, rollbacks, and failures. Never connect to Pods directly. A **Service** is an API object that sits in front of one or more identical Pods and exposes them via a **stable network identity**: a DNS name, IP address, and port that Kubernetes guarantees will never change for the life of the Service. Manage Services declaratively via version-controlled YAML.

## Frameworks Introduced
- **Service front end / back end split**: Front end = stable DNS name + IP + port (immutable). Back end = a **label selector** that load-balances traffic over a dynamic set of healthy matching Pods.
- **Service stacking**: LoadBalancer builds on NodePort builds on ClusterIP. Each higher type auto-creates the constructs below it.

## Key Concepts (5-10)
- **Stable network identity**: front-end IP/DNS/port never change even as Pods come and go.
- **Label selector + loose coupling**: Services find Pods via labels — the *same* mechanism that couples Deployments to Pods. A Pod must carry *all* selector labels to receive traffic (extra labels are fine).
- **EndpointSlice**: created automatically per Service by the EndpointSlice controller; tracks healthy Pods (IP:port) matching the selector. Added/removed as Pods appear/disappear. >100 matching Pods → multiple EndpointSlices. Dual-stack clusters get one per address family (IPv4 + IPv6).
- **Endpoints (legacy)**: older functionally-identical object; EndpointSlices scale better on large/busy clusters.
- **kube-proxy / cluster DNS**: containers are pre-programmed to use cluster DNS to resolve the Service name → ClusterIP; traffic is then forwarded to a Pod from the EndpointSlice.
- **Round-robin load balancing**: Service picks among healthy Pods; consecutive requests likely hit different Pods.
- **Session Affinity**: `None` (default) or `ClientIP` for stickiness. ClientIP is an anti-pattern for microservices.
- **External Traffic Policy**: `Cluster` (default, balances across all nodes but obscures source IP) vs `Local` (only local-node Pods, preserves source IP).

## Mental Models
- **Service as a stable front-end**: clients target the unchanging name/IP; the churn of Pods behind it is invisible.
- **Labels as loose coupling**: no hard wiring between Service and Pods — match by label, so scaling, updates, rollbacks, and failures never break the connection.

## Anti-patterns
- Connecting to Pods directly instead of through a Service.
- Relying on `Session Affinity: ClientIP` for state — microservices should be designed for process disposability so any instance can serve any client.
- Using NodePort for general external access (clients must know node names/IPs and node health) — prefer LoadBalancer.

## Code Examples

ClusterIP (default — internal only):
```yaml
apiVersion: v1
kind: Service
metadata:
  name: skippy
spec:
  ports:
  - port: 8080
  selector:
    project: tkb
    zone: prod
```

NodePort (external via a port on every node):
```yaml
apiVersion: v1
kind: Service
metadata:
  name: skippy
spec:
  type: NodePort
  ports:
  - port: 8080        # ClusterIP port
    targetPort: 9000  # app port in container
    nodePort: 30050   # external port on every node (30000-32767)
  selector:
    app: hello-world
```

LoadBalancer (cloud LB, low port, public DNS — auto-creates NodePort + ClusterIP):
```yaml
kind: Service
apiVersion: v1
metadata:
  name: cloud-lb
spec:
  type: LoadBalancer
  ports:
  - port: 9000        # load balancer (front-end) port
    targetPort: 8080  # app port inside container
  selector:
    chapter: services
```

Imperative + inspection (exact):
```bash
kubectl expose deployment svc-test --type=LoadBalancer
kubectl get svc -o wide
kubectl describe svc svc-test          # shows Endpoints, Session Affinity, External Traffic Policy
kubectl apply -f lb.yml
kubectl get endpointslices
kubectl describe endpointslice <name>  # block per healthy Pod: Addresses, Ready, TargetRef, NodeName
kubectl delete svc svc-test
```
Note: `core/v1` API group is special — `apiVersion: v1` omits the group name.

## Reference Tables

| Type | Reachable from | Mechanism | When to use |
|------|----------------|-----------|-------------|
| ClusterIP | Inside cluster only | Internal IP + DNS name (not externally routable) | Default; app-to-app comms within the cluster |
| NodePort | External | Dedicated high port (30000-32767) on *every* node → ClusterIP | Basic external access; dev/testing; no cloud LB available |
| LoadBalancer | External (internet) | Cloud LB (friendly DNS, low port) → NodePort → ClusterIP | Production internet-facing access; simplest external entry |

| `kubectl get svc` column | Meaning |
|--------------------------|---------|
| CLUSTER-IP | Internal-only IP |
| EXTERNAL-IP | Cloud LB IP/DNS (or `localhost` locally; `<pending>` while provisioning) |
| PORT(S) | `lbPort:nodePort/TCP` e.g. `8080:31755/TCP` |
| SELECTOR | Labels matched on Pods |

## Worked Example
1. `kubectl apply -f deploy.yml` — Deployment `svc-test`: 10 Pods, web app on port 8080, label `chapter=services`.
2. `kubectl expose deployment svc-test --type=LoadBalancer` — inspects the Deployment and auto-builds correct port mappings + selector, plus the ClusterIP and NodePort constructs underneath.
3. `kubectl get svc -o wide` — wait for EXTERNAL-IP (e.g. `212.2.245.220`); PORT(S) shows `8080:31755/TCP`; SELECTOR `chapter=services`.
4. `kubectl describe svc svc-test` — `Endpoints: 10.1.0.200:8080,10.1.0.201:8080,...` — the healthy Pod IPs from the EndpointSlice map exactly to the running Pods.
5. Browse `EXTERNAL-IP:8080` → traffic flows LB(8080) → NodePort(31755) → ClusterIP(8080) → Pod(8080).
6. Cleanup: `kubectl delete -f deploy.yml -f lb.yml` — deleting a Service auto-deletes its Endpoints/EndpointSlices.

## Key Takeaways
- Always reach Pods through a Service, never directly.
- Front end = stable IP/DNS/port; back end = label-selected, always-current set of healthy Pods.
- ClusterIP = internal, NodePort = port on every node, LoadBalancer = cloud LB; the types stack.
- EndpointSlices (or legacy Endpoints) keep the healthy-Pod list current automatically.
- Manage Services declaratively as version-controlled YAML.

## Connects To
- **Ch 5/6 (Pods/Deployments)**: same label-selector loose-coupling links Deployments→Pods and Services→Pods.
- **Service Discovery chapter**: cluster DNS registration and name resolution detail.
- **Ingress / Gateway**: higher-level L7 routing built atop Services.
