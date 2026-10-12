# Chapter 8: Ingress

## Core Idea
Ingress exposes **multiple** web applications (ClusterIP Services) through a **single** cloud load balancer, using **host-based** and **path-based** HTTP routing. It solves the LoadBalancer Service problem: one LoadBalancer Service = one cloud load balancer, so 25 internet-facing apps would need 25 (costly, often quota-limited) cloud load balancers. Ingress operates at **Layer 7** (application layer / OSI), inspecting HTTP headers to route on hostname and path. GA since Kubernetes 1.19 (after 15+ beta releases). Note: service meshes now overlap with Ingress — if running a mesh, you may not need Ingress.

## Frameworks Introduced
- **Two-construct pattern**: a **resource** (defines routing rules) + a **controller** (implements them). Unlike Deployments/Services, Kubernetes has **no built-in Ingress controller** — you must install one (e.g., NGINX), though some cloud platforms ship one.

## Key Concepts (5-10)
- **Ingress**: API object in `networking.k8s.io/v1` holding routing rules. Capitalized as it's an API resource.
- **Ingress controller**: watches Ingress resources + the load balancer, routes requests per rules. Must be installed; many options exist.
- **IngressClass**: lets you run **multiple Ingress controllers** on one cluster. Each controller is assigned to a class; each Ingress object is assigned to a class via `spec.ingressClassName`. NGINX install creates a class named `nginx`. No shortname for ingressclass objects.
- **Host-based routing**: route on the hostname in the HTTP header (e.g., `shield.mcu.com` → svc-shield).
- **Path-based routing**: route on the URL path (e.g., `mcu.com/shield` → svc-shield).
- **Backend**: usually a ClusterIP Service (referenced by name + port) that forwards to Pods.
- **Default backend**: where the controller sends traffic for an unmatched host/path. Not all controllers implement one (GKE returns `response 404 (backend NotFound)`).
- **LoadBalancer vs load balancer**: `LoadBalancer` = K8s Service of `type=LoadBalancer`; `load balancer` = the cloud's internet-facing load balancer it provisions.
- **TLS / ports**: Ingress only supports HTTP and HTTPS — ports **80** or **443**. (TLS termination handled at the load balancer / controller on 443.)
- **rewrite-target annotation**: NGINX-specific (`nginx.ingress.kubernetes.io/rewrite-target: /`) — best-effort rewrites incoming paths to `/`. Controller-specific; comment out for other controllers.

## Mental Models
- **Ingress = a Layer-7 HTTP router (reverse proxy) sitting in front of many ClusterIP Services**, fronted by one shared cloud load balancer. DNS maps many hostnames → one load balancer IP; the controller reads HTTP headers and fans out to the right Service.
- **fan-out**: one entry point (load balancer + Ingress) splits traffic to many backend Services by host/path.

## Anti-patterns
- One LoadBalancer Service per app (cost + cloud quota limits) — the problem Ingress fixes.
- Assuming a built-in controller exists — Ingress rules do nothing until a controller is installed.
- Relying on `rewrite-target` for every app — path rewrites don't work for all apps (e.g., asset/image paths break).
- Forgetting `spec.ingressClassName` when multiple controllers run — rules go unhandled.

## Code Examples

Install NGINX Ingress controller (single line; provisions Namespace, ServiceAccounts, ConfigMap, Roles, RoleBindings, controller Pod):
```bash
$ kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.9.4/deploy/static/provider/cloud/deploy.yaml
# verify
$ kubectl get pods -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx
$ kubectl get ingressclass    # -> nginx  k8s.io/ingress-nginx
```

Ingress object `mcu-all` (`ig-all.yml`) — host + path rules:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: mcu-all
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - host: shield.mcu.com          # host rule -> shield
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: svc-shield
            port:
              number: 8080
  - host: hydra.mcu.com           # host rule -> hydra
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: svc-hydra
            port:
              number: 8080
  - host: mcu.com
    http:
      paths:
      - path: /shield             # path rule -> shield
        pathType: Prefix
        backend:
          service:
            name: svc-shield
            port:
              number: 8080
      - path: /hydra              # path rule -> hydra
        pathType: Prefix
        backend:
          service:
            name: svc-hydra
            port:
              number: 8080
```

Deploy + inspect:
```bash
$ kubectl apply -f ig-all.yml
$ kubectl get ing            # NAME CLASS HOSTS ADDRESS PORTS  (ADDRESS may take ~1 min on cloud)
$ kubectl describe ing mcu-all
```

## Reference Tables

Host-based vs path-based routing:
| Host-based example | Path-based example | Backend K8s Service |
|--------------------|--------------------|---------------------|
| shield.mcu.com     | mcu.com/shield     | svc-shield          |
| hydra.mcu.com      | mcu.com/hydra      | svc-hydra           |

`kubectl get ing` fields:
| Field | Meaning |
|-------|---------|
| CLASS | IngressClass handling the rules (`<None>` if no class configured) |
| HOSTS | hostnames the Ingress handles |
| ADDRESS | load balancer endpoint (public IP/DNS on cloud; `localhost` locally) |
| PORTS | 80 or 443 (HTTP/HTTPS only) |

## Worked Example
Route two hostnames + two paths to two Services through one Ingress:
1. Deploy app `shield` (port 8080) fronted by ClusterIP `svc-shield`, and app `hydra` (port 8080) fronted by `svc-hydra` (`kubectl apply -f app.yml`).
2. Deploy `mcu-all` Ingress: host rules `shield.mcu.com`→svc-shield, `hydra.mcu.com`→svc-hydra; path rules `mcu.com/shield`→svc-shield, `mcu.com/hydra`→svc-hydra.
3. Configure DNS — point `shield.mcu.com`, `hydra.mcu.com`, `mcu.com` at the load balancer IP. Locally: add `<LB-IP> shield.mcu.com` etc. to `/etc/hosts` (Linux/Mac, root) or `C:\Windows\System32\drivers\etc\hosts` (Windows, admin); use `127.0.0.1` if ADDRESS is `localhost`.
4. Traffic flow: client → DNS → load balancer (port 80) → Ingress controller reads HTTP header (host/path) → matching rule → ClusterIP backend Service → Pod.
5. Result: bare `mcu.com` (no rule) hits the **default backend** (404). Path-based hits use `rewrite-target` (images may not render since rewrite doesn't suit all apps).

## Key Takeaways
- Ingress exposes many ClusterIP Services through one cloud load balancer — fewer load balancers, lower cost.
- It's L7: routes HTTP/HTTPS by hostname (host-based) and path (path-based); ports 80/443 only.
- Resource (rules) + controller (enforcement); the controller is usually **not** built-in — install one.
- IngressClass + `spec.ingressClassName` let multiple controllers coexist and bind rules to a controller.
- Annotations (e.g., NGINX `rewrite-target`) add controller-specific behavior and are not portable.
- Unmatched traffic falls to the default backend (if the controller implements one).
- Service meshes overlap with Ingress — you may not need both.

## Connects To
- **Ch7 (Services)**: backends are ClusterIP Services; Ingress replaces the per-app LoadBalancer/NodePort pattern.
- **Service meshes**: overlapping L7 routing/traffic management — possible alternative.
- **Gateway API**: the evolving successor to Ingress for richer L7 routing (not detailed in this chapter).
- **DNS / cloud load balancers**: external name resolution and the provisioned cloud LB sit in front of Ingress.
