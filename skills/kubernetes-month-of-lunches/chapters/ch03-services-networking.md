# Chapter 3: Connecting Pods over the Network with Services

## Core Idea

Pods communicate using IP addresses, but those addresses change whenever a Pod is replaced. Kubernetes solves this with **Services** — stable virtual resources that provide a fixed DNS name and IP address, routing traffic to the right Pods via label selectors. Services are the network glue for every traffic pattern in a cluster: Pod-to-Pod, external-to-Pod, and Pod-to-external.

---

## Frameworks Introduced

- **Service + Label Selector routing**: A Service defines a `selector` that matches Pod labels. Kubernetes maintains a live `Endpoints` list of matching Pod IPs and routes traffic through the Service's stable virtual IP. Use this whenever two components need to communicate — never hard-code Pod IPs.
  - *How*: Deploy a `Service` manifest with a `selector` matching the target Pod's label. Kubernetes DNS registers the Service name; consumers use that name as a host.
  - *Why it fails without it*: Pod IPs are ephemeral. Replacement Pods get new IPs. Without a Service, DNS has nothing to resolve and callers break silently after the first Pod replacement.

- **kube-proxy + virtual IP**: The ClusterIP is not a real network address — it exists only in `kube-proxy`'s packet-filter rules (iptables/IPVS). DNS returns the virtual IP; kube-proxy rewrites packets to the actual endpoint IP. This means clients can cache the DNS response forever and never break across Pod churn.

---

## Key Concepts

- **ClusterIP**: Default Service type. Assigns a cluster-internal virtual IP. Only reachable from inside the cluster. Used for inter-Pod communication. Omitting `type` in the spec defaults to ClusterIP.

- **NodePort**: Exposes a Service on a static port on every node's IP. External clients connect to `<NodeIP>:<nodePort>`. Less flexible than LoadBalancer; requires publicly accessible nodes and unique ports per Service.

- **LoadBalancer**: Extends NodePort. Provisions an external load balancer from the platform (cloud provider, K3s, Docker Desktop). Clients reach the Service via the external IP. The recommended type for external traffic in production — same YAML across all environments, different platform behavior.

- **ExternalName**: An alias Service. DNS returns a CNAME pointing to an external domain name. No proxy, no virtual IP. Used to give internal Pods a local cluster name for external systems. Does **not** rewrite HTTP `Host` headers — best suited to TCP (databases, non-HTTP).

- **Headless Service**: A ClusterIP Service with no `selector`. Paired with a manual `Endpoints` resource listing explicit IP addresses. Used to route to external systems by IP rather than domain name.

- **Endpoints**: A Kubernetes resource (auto-managed by the Service controller) that holds the live list of Pod IPs matching a Service's selector. Updated immediately when Pods are added, replaced, or removed.

- **kube-proxy**: A per-node component that watches Services and Endpoints and programs iptables/IPVS rules to forward traffic from the virtual ClusterIP to a real endpoint.

- **Namespace**: A logical partition of the cluster. Every resource lives in a namespace (default: `default`). The full DNS name of a Service is `<name>.<namespace>.svc.cluster.local`; within the same namespace, short names resolve.

- **Fully Qualified Domain Name (FQDN)**: `<service-name>.<namespace>.svc.cluster.local`. Short name (`<service-name>`) works within the same namespace via DNS search suffix.

- **CNAME (ExternalName resolution)**: When a Pod resolves an ExternalName Service, the cluster DNS server returns a CNAME record pointing to the external host. The OS then resolves that via the node's upstream DNS.

---

## Mental Models

- Use **ClusterIP** when the component is internal-only (API, cache, database sidecar) and should never be reachable from outside the cluster.
- Use **LoadBalancer** when external traffic needs to reach a Pod — works consistently from local dev (Docker Desktop/K3s) to cloud (AKS/EKS), with the same YAML.
- Use **ExternalName** when a Pod needs a local cluster name for an external system (e.g., a managed cloud database), and the protocol is TCP (not plain HTTP, due to Host header mismatch).
- Use a **headless Service + Endpoints** when you need to route to an external system by IP address rather than domain name, or when you want full control over endpoint resolution.

---

## Anti-patterns

- **Using Pod IP addresses directly**: Pod IPs change on replacement. Any caller that cached a Pod IP will break silently on the next Pod churn. Always use a Service.
- **Skipping Services for internal components**: Without a ClusterIP Service, a component has no DNS name, so other Pods cannot find it. The app will fail as soon as it tries a DNS lookup (returns no result, not an error you expect).
- **Using NodePort in production**: Requires publicly accessible node IPs, ties you to specific ports, and behaves inconsistently across distributions (notably broken in Kind). Use LoadBalancer for external traffic to keep manifests consistent across environments.
- **Using ExternalName for HTTP services**: The HTTP client sends the local cluster name in the `Host` header. The remote server sees the wrong hostname and typically rejects or misroutes the request. ExternalName is for TCP-level protocols.
- **`kubectl delete svc --all` in a live cluster**: This deletes the `kubernetes` API Service too. Kubernetes has a controller that recreates it (in `kube-system`), but the command is dangerous in production. Delete Services by name.
- **Caching DNS responses in app code** (misguided optimization): Actually safe with Kubernetes because the ClusterIP is virtual and stable — but misleading in other contexts. The Service controller keeps kube-proxy endpoints current regardless of DNS cache.

---

## Code Examples

```yaml
# Listing 3.1 — Minimal ClusterIP Service (sleep2-service.yaml)
# Demonstrates: Service name becomes DNS hostname; selector links to Pod labels
apiVersion: v1
kind: Service
metadata:
  name: sleep-2          # DNS name other Pods use to reach this Service
spec:
  selector:
    app: sleep-2         # Routes to Pods with label app=sleep-2
  ports:
    - port: 80           # Service port (and target port, same value)
```

```yaml
# Listing 3.2 — Explicit ClusterIP Service (api-service.yaml)
# Demonstrates: type: ClusterIP stated explicitly for clarity; internal-only
apiVersion: v1
kind: Service
metadata:
  name: numbers-api
spec:
  ports:
    - port: 80
  selector:
    app: numbers-api
  type: ClusterIP
```

```yaml
# Listing 3.3 — LoadBalancer Service (web-service.yaml)
# Demonstrates: port/targetPort split; external traffic entry point
apiVersion: v1
kind: Service
metadata:
  name: numbers-web
spec:
  ports:
    - port: 8080         # Port external clients connect to
      targetPort: 80     # Port the container listens on
  selector:
    app: numbers-web
  type: LoadBalancer
```

```yaml
# Listing 3.4 — NodePort Service (web-service-nodePort.yaml)
# Demonstrates: three-port model (port, targetPort, nodePort)
apiVersion: v1
kind: Service
metadata:
  name: numbers-web-node
spec:
  ports:
    - port: 8080         # ClusterIP port (Pod-to-Pod)
      targetPort: 80     # Container port
      nodePort: 30080    # External port on every node IP
  selector:
    app: numbers-web
  type: NodePort
```

```yaml
# Listing 3.5 — ExternalName Service (api-service-externalName.yaml)
# Demonstrates: CNAME alias from cluster name to external FQDN
apiVersion: v1
kind: Service
metadata:
  name: numbers-api
spec:
  type: ExternalName
  externalName: raw.githubusercontent.com   # DNS CNAME target
```

```yaml
# Listing 3.6 — Headless Service + Endpoints (api-service-headless.yaml)
# Demonstrates: ClusterIP with no selector; manual Endpoints resource with static IP
apiVersion: v1
kind: Service
metadata:
  name: numbers-api
spec:
  type: ClusterIP        # No selector — headless
  ports:
    - port: 80
---
kind: Endpoints
apiVersion: v1
metadata:
  name: numbers-api      # Must match Service name
subsets:
  - addresses:
      - ip: 192.168.123.234   # Static external IP
    ports:
      - port: 80
```

```bash
# Deploy two Deployments and check Pod IPs
kubectl apply -f sleep/sleep1.yaml -f sleep/sleep2.yaml
kubectl wait --for=condition=Ready pod -l app=sleep-2
kubectl get pod -l app=sleep-2 --output jsonpath='{.items[0].status.podIP}'

# Ping Pod by IP from another Pod (works but fragile — IP changes on replacement)
kubectl exec deploy/sleep-1 -- ping -c 2 $(kubectl get pod -l app=sleep-2 --output jsonpath='{.items[0].status.podIP}')

# Deploy a Service and verify DNS resolution
kubectl apply -f sleep/sleep2-service.yaml
kubectl get svc sleep-2
kubectl exec deploy/sleep-1 -- ping -c 1 sleep-2   # ping fails (ICMP not supported); DNS resolves

# Deploy ClusterIP Service for API, then test app
kubectl apply -f numbers/api-service.yaml
kubectl get svc numbers-api
kubectl port-forward deploy/numbers-web 8080:80

# Deploy LoadBalancer Service and retrieve external address
kubectl apply -f numbers/web-service.yaml
kubectl get svc numbers-web
kubectl get svc numbers-web -o jsonpath='http://{.status.loadBalancer.ingress[0].*}:8080'

# DNS lookup inside a Pod — short name vs FQDN
kubectl exec deploy/sleep-1 -- sh -c 'nslookup numbers-api | tail -n 5'
kubectl exec deploy/sleep-1 -- sh -c 'nslookup numbers-api.default.svc.cluster.local | grep "^[^*]"'
kubectl exec deploy/sleep-1 -- sh -c 'nslookup kube-dns.kube-system.svc.cluster.local | grep "^[^*]"'

# Inspect endpoints and watch them update on Pod replacement
kubectl get endpoints sleep-2
kubectl delete pods -l app=sleep-2
kubectl get endpoints sleep-2   # New Pod IP appears immediately

# View resources across namespaces
kubectl get svc --namespace default
kubectl get svc -n kube-system

# Cleanup — delete by type, not --all for safety
kubectl delete deploy --all
kubectl delete svc --all
```

---

## Reference Tables

| Feature | ClusterIP | NodePort | LoadBalancer | ExternalName |
|---|---|---|---|---|
| **Scope** | Cluster-internal only | External via node IP | External via platform LB | External via DNS CNAME |
| **Virtual IP** | Yes (cluster-internal) | Yes (+ node port) | Yes (+ external IP) | No (CNAME only) |
| **Use case** | Inter-Pod communication | Dev/test external access | Production external traffic | Alias for external domain |
| **Port uniqueness** | No constraint | Must be unique per cluster | Gets dedicated IP (cloud) | N/A |
| **HTTP safe** | Yes | Yes | Yes | No (Host header mismatch) |
| **Platform-dependent behavior** | No | Partially (Kind issues) | Yes (IP source varies) | No |
| **Requires external infra** | No | No | Yes (cloud LB or k3s/DD) | No |

---

## Worked Example

**Goal**: Deploy a two-tier app (web + API) so the web Pod reaches the API by DNS name, and external users reach the web Pod.

**Step 1 — Deploy both components (no Services yet):**
```bash
kubectl apply -f numbers/api.yaml -f numbers/web.yaml
kubectl wait --for=condition=Ready pod -l app=numbers-web
```
The web Pod starts but fails when it tries to call `http://numbers-api` — the DNS name has no Service behind it, so resolution fails.

**Step 2 — Create a ClusterIP Service for the API:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: numbers-api          # Pod uses this as the hostname: http://numbers-api
spec:
  ports:
    - port: 80
  selector:
    app: numbers-api         # Routes to Pods with this label
  type: ClusterIP
```
```bash
kubectl apply -f numbers/api-service.yaml
kubectl get svc numbers-api
# NAME          TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)   AGE
# numbers-api   ClusterIP   10.96.45.201   <none>        80/TCP    5s
```
The web Pod can now resolve `numbers-api` → `10.96.45.201`. kube-proxy forwards that to the API Pod's real IP. App works.

**Step 3 — Create a LoadBalancer Service for external access to the web:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: numbers-web
spec:
  ports:
    - port: 8080
      targetPort: 80
  selector:
    app: numbers-web
  type: LoadBalancer
```
```bash
kubectl apply -f numbers/web-service.yaml
kubectl get svc numbers-web -o jsonpath='http://{.status.loadBalancer.ingress[0].*}:8080'
# http://localhost:8080  (Docker Desktop)
# http://172.28.132.127:8080  (K3s)
```

**Step 4 — Verify resilience through Pod replacement:**
```bash
kubectl get pod -l app=numbers-api -o custom-columns=NAME:metadata.name,POD_IP:status.podIP
kubectl delete pod -l app=numbers-api
kubectl get pod -l app=numbers-api -o custom-columns=NAME:metadata.name,POD_IP:status.podIP
# New Pod, new IP — but numbers-api Service still routes correctly
kubectl get endpoints numbers-api
# Endpoint list updates immediately to the new Pod IP
```

The app continues working because the web Pod always calls `numbers-api` (the Service), not the Pod IP directly. The Service's virtual ClusterIP never changes; kube-proxy updates the endpoint routing table as Pods come and go.

---

## Key Takeaways

1. Every Pod has an IP address, but Pod IPs are ephemeral — always use a Service for inter-Pod communication.
2. A Service provides a stable virtual IP and a DNS name (the Service's `metadata.name`) that resolve consistently across Pod replacements.
3. The link between a Service and its Pods is a **label selector** — the same loose-coupling mechanism used by Deployments.
4. ClusterIP is the default and most common type; LoadBalancer is the preferred type for external traffic (same YAML, different platform behavior).
5. kube-proxy, not the DNS server, does the actual packet routing — DNS returns the virtual ClusterIP; kube-proxy rewrites traffic to the real endpoint using iptables/IPVS.
6. The `Endpoints` resource (auto-managed) holds the live list of matching Pod IPs and is updated immediately on Pod changes.
7. ExternalName Services create DNS CNAMEs to external hosts — useful for TCP services, but incompatible with plain HTTP due to the `Host` header.
8. Every resource lives in a namespace; the full DNS form is `<service>.<namespace>.svc.cluster.local`, but within the same namespace the short name resolves.

---

## Connects To

- **Ch 2 (Pods and Deployments)**: Services are the networking complement to Deployments. A Deployment controls Pod lifecycle; a Service controls network identity. Both use label selectors for loose coupling.
- **Ch 11 (Namespaces and RBAC)**: Namespaces introduced here for DNS context become central to cluster partitioning and security policy.
- **Ingress (later chapters)**: LoadBalancer Services handle L4 traffic. For L7 HTTP routing (host/path-based), Ingress builds on top of Services, referencing them as backends.
- **DNS / CNAME (external concept)**: ExternalName Services rely on standard DNS CNAME semantics — understanding CNAME resolution explains why HTTP `Host` headers break and why TCP-only services work fine.
- **iptables/IPVS (external concept)**: kube-proxy uses OS-level packet filters to implement virtual IPs — knowledge of Linux networking helps diagnose Service routing issues.
