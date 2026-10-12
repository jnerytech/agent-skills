# Chapter 15: Managing Incoming Traffic with Ingress

## Core Idea

Ingress solves the problem of routing external HTTP/S traffic to multiple internal applications through a single cluster entry point. Instead of allocating a separate LoadBalancer Service (and thus a separate public IP) per application, you deploy one ingress controller — a reverse proxy running in a Pod — and define routing rules as Kubernetes Ingress objects. The controller watches for Ingress resource changes and translates them into proxy configuration, routing traffic by domain name and path to the appropriate ClusterIP Service.

---

## Frameworks Introduced

- **Ingress resource vs. ingress controller**: The Ingress object is a generic Kubernetes resource that stores routing rules (host, path, TLS). The ingress controller is the pluggable reverse proxy (Nginx, Traefik, HAProxy, Contour, etc.) that reads those rules and acts on them.
  - *When*: Always used together; the Ingress object is meaningless without a running controller.
  - *How*: Deploy the controller first (receives a LoadBalancer Service), then create Ingress objects with rules; the controller reconciles its proxy config automatically.
  - *Why-or-failure*: If you create Ingress objects before deploying a controller, the rules exist in etcd but nothing acts on them — traffic is never routed.

- **Ingress classes**: A labeling mechanism that tells a specific controller which Ingress objects to process. Required when multiple controllers run in the same cluster.
  - *When*: Any environment running more than one ingress controller implementation.
  - *How*: Set `kubernetes.io/ingress.class: <name>` annotation (or `spec.ingressClassName`) on each Ingress object.
  - *Why-or-failure*: Without ingress classes, all controllers may fight over the same Ingress objects, causing unpredictable routing.

---

## Key Concepts

1. **Single entry point**: One LoadBalancer Service for the ingress controller handles all inbound traffic; internal apps use ClusterIP Services only.

2. **Host-based routing**: Ingress rules can restrict scope to a specific domain name (`host: hello.kiamol.local`). Requests for other domains return 404 unless a matching rule exists.

3. **Path-based routing**: Multiple paths within a domain can route to different backend Services (`path: /v1` → `vweb-v1`, `path: /` → `vweb-v2`).

4. **PathType field**: Introduced in Kubernetes 1.18. `Exact` matches only the specified path; `Prefix` matches any path starting with the value. Controllers that predate this field may ignore it.

5. **URL rewrite via annotation**: When a path like `/v1` is stripped before forwarding to a backend that only understands `/`, the controller must rewrite the URL. Expressed through controller-specific annotations (e.g., `nginx.ingress.kubernetes.io/rewrite-target: /`), not the Ingress spec itself.

6. **Annotations for extended features**: The Ingress spec covers only basic routing and TLS. Everything else — caching, sticky sessions, rate limiting, URL rewrites — is configured via annotations specific to the chosen controller. These annotations are not portable across controllers.

7. **Sticky sessions**: The ingress controller pins a client's requests to the same Pod, necessary for stateful apps with anti-forgery checks. Nginx configures this via annotations on the Ingress object; Traefik configures it at the Service level.

8. **TLS / HTTPS termination**: The controller loads a TLS certificate from a Kubernetes TLS Secret and terminates encryption. Applications receive plain HTTP internally. This centralizes certificate management away from individual app teams.

9. **Self-signed vs. trusted certificates**: Traefik can generate its own self-signed certificate for dev/test (annotation-driven). For production, use certificates from a trusted CA (Let's Encrypt via cert-manager, or organizational CA) stored as TLS Secrets.

10. **Multiple controllers in one cluster**: Kubernetes supports running Nginx and Traefik simultaneously. Each serves a different set of Ingress objects selected by ingress class. Risk: incompatible feature sets and annotation dialects require separate Ingress rule models per controller.

---

## Mental Models

**The central post room**: Think of the ingress controller as a post room for the building (cluster). All mail (HTTP requests) arrives at one address (one IP/port). The post room reads the label (host + path) and delivers to the right internal office (ClusterIP Service). Individual offices don't need their own street address (no LoadBalancer per app).

**Ingress as a policy layer**: Ingress rules are not just routing — they are access control. By specifying only exact paths you want public, you implicitly block all others. The metrics endpoint (`/metrics`), config dump (`/config`), and diagnostics pages remain inside the cluster even when the app itself is public.

**Annotation dialect lock-in**: Every ingress controller speaks its own annotation language. Nginx annotations (`nginx.ingress.kubernetes.io/*`) are unintelligible to Traefik, and vice versa. Switching controllers is a migration project, not a config swap.

**Controller complexity is hidden, not absent**: Traefik has no human-readable config file; Nginx generates one with 1,700+ lines of Lua-embedded config. Both are complex — Traefik hides complexity in its dashboard and API; Nginx exposes it in an auto-generated file. Know which you prefer to debug.

---

## Anti-patterns

- **One LoadBalancer per app**: Defeats the purpose of Ingress; creates IP sprawl and DNS management overhead.
- **No ingress class in a multi-controller cluster**: Controllers process each other's Ingress objects, causing routing conflicts and unpredictable behavior.
- **Relying on PathType for access control when using mixed controllers**: Traefik (as of the book) ignores `PathType: Exact`, so what looks like an allowlist becomes open access. Always verify feature support per controller.
- **Packaging TLS certificates inside container images**: Certificates expire and rotate; baking them into images means rebuilding for every renewal. Always load from Secrets.
- **Running multiple ingress controllers with different annotation models without strict team discipline**: Leads to misconfigured Ingress objects referencing the wrong controller, silently routing (or blocking) traffic incorrectly.
- **Expecting Ingress to handle non-HTTP traffic**: Ingress is HTTP/S only. TCP/UDP routing requires other mechanisms (e.g., a raw LoadBalancer Service or a gateway API implementation).

---

## Code Examples

**Minimal Ingress — catch-all rule (beta API):**
```yaml
apiVersion: networking.k8s.io/v1beta1
kind: Ingress
metadata:
  name: hello-kiamol
spec:
  rules:
  - http:
      paths:
      - path: /
        backend:
          serviceName: hello-kiamol
          servicePort: 80
```

**Host-scoped Ingress rule:**
```yaml
spec:
  rules:
  - host: hello.kiamol.local
    http:
      paths:
      - path: /
        backend:
          serviceName: hello-kiamol
          servicePort: 80
```

**Multi-path routing with URL rewrite annotation (Nginx):**
```yaml
apiVersion: networking.k8s.io/v1beta1
kind: Ingress
metadata:
  name: vweb
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: vweb.kiamol.local
    http:
      paths:
      - path: /
        backend:
          serviceName: vweb-v2
          servicePort: 80
      - path: /v1
        backend:
          serviceName: vweb-v1
          servicePort: 80
```

**Exact and Prefix path matching (Kubernetes >= 1.18):**
```yaml
rules:
- host: todo.kiamol.local
  http:
    paths:
    - pathType: Exact
      path: /new
      backend:
        serviceName: todo-web
        servicePort: 80
    - pathType: Prefix
      path: /static
      backend:
        serviceName: todo-web
        servicePort: 80
```

**Nginx proxy cache annotation:**
```yaml
metadata:
  name: pi
  annotations:
    nginx.ingress.kubernetes.io/proxy-buffering: "on"
    nginx.ingress.kubernetes.io/configuration-snippet: |
      proxy_cache static-cache;
      proxy_cache_valid 10m;
```

**TLS block referencing a Secret:**
```yaml
spec:
  rules:
  - host: todo2.kiamol.local
    http:
      paths:
      - path: /new
        backend:
          serviceName: todo-web-sticky
          servicePort: 80
  tls:
  - secretName: kiamol-cert
```

**Traefik ingress class + exact path (annotation-driven):**
```yaml
metadata:
  name: todo2-new
  annotations:
    kubernetes.io/ingress.class: traefik
    traefik.ingress.kubernetes.io/router.pathmatcher: Path
```

**Create TLS Secret from PEM files:**
```bash
kubectl create secret tls kiamol-cert --key=tls.key --cert=tls.crt
```

**Deploy Nginx ingress controller:**
```bash
kubectl apply -f ingress-nginx/
kubectl get svc -n kiamol-ingress-nginx
```

**Deploy Traefik ingress controller:**
```bash
kubectl apply -f ingress-traefik/
kubectl get svc ingress-traefik-controller -o jsonpath='http://{.status.loadBalancer.ingress[0].*}:8080' -n kiamol-ingress-traefik
```

---

## Reference Tables

### Ingress vs. LoadBalancer Service

| Dimension | LoadBalancer Service | Ingress |
|---|---|---|
| IP addresses | One per Service | One for the entire cluster |
| Protocol | Any TCP/UDP | HTTP and HTTPS only |
| Routing granularity | Port-level | Host + path |
| TLS termination | Must be handled by the app | Handled by the ingress controller |
| DNS management | One record per Service | One record per domain, shared entry point |
| Cost | Higher (cloud LB per app) | Lower (one cloud LB for all apps) |

### Common Ingress Controller Options

| Controller | Category | Key strengths | Notable annotation prefix |
|---|---|---|---|
| Nginx (Kubernetes project) | Traditional reverse proxy | Battle-tested, caching, WAF support, sticky sessions | `nginx.ingress.kubernetes.io/` |
| Traefik | Modern/platform-aware | Admin dashboard, Let's Encrypt native, no config file, auto-discovery | `traefik.ingress.kubernetes.io/` |
| HAProxy | Traditional reverse proxy | High performance, established ops tooling | `haproxy.org/` |
| Contour | Modern/platform-aware | CNCF project, Envoy-based, HTTPProxy CRD | `projectcontour.io/` |

---

## Worked Example

**Scenario**: Deploy the to-do list app accessible at `todo.kiamol.local` with HTTPS and sticky sessions for the `/new` path, using the Nginx ingress controller.

**Step 1 — Deploy the Nginx ingress controller:**
```bash
kubectl apply -f ingress-nginx/
kubectl get svc ingress-nginx-controller -n kiamol-ingress-nginx
# Note the external IP; it listens on port 80 (HTTP) and 443 (HTTPS)
```
At this point, browsing to the controller IP returns a 404 — no Ingress rules exist yet.

**Step 2 — Deploy the app with a ClusterIP Service:**
```yaml
# todo-web Deployment + ClusterIP Service (no external IP)
```
```bash
kubectl apply -f todo-list/
kubectl get svc todo-web   # CLUSTER-IP only, no EXTERNAL-IP
```

**Step 3 — Register the local domain:**
```bash
./add-to-hosts.sh todo.kiamol.local ingress-nginx
# Maps todo.kiamol.local → ingress controller IP in /etc/hosts
```

**Step 4 — Deploy initial Ingress rule (all paths open):**
```yaml
apiVersion: networking.k8s.io/v1beta1
kind: Ingress
metadata:
  name: todo
spec:
  rules:
  - host: todo.kiamol.local
    http:
      paths:
      - path: /
        backend:
          serviceName: todo-web
          servicePort: 80
```
```bash
kubectl apply -f todo-list/ingress.yaml
kubectl get ingress   # shows host, address, and port
# Browse to http://todo.kiamol.local — app is live
```

**Step 5 — Restrict access to exact paths (block /metrics, /config):**
```bash
kubectl apply -f todo-list/update/ingress-exact.yaml
# Now only /new, /list, /static, and / are reachable externally
# /metrics and /config return 404 from the ingress controller
```

**Step 6 — Scale up and add sticky sessions for /new:**
```bash
kubectl scale deploy/todo-web --replicas 3
# Anti-forgery errors appear on POST to /new (load-balanced to wrong Pod)
kubectl apply -f todo-list/update/ingress-sticky.yaml
# /new path now uses Nginx sticky session cookie; other paths load-balance normally
```

**Step 7 — Generate and deploy TLS certificate:**
```bash
kubectl apply -f cert-generator.yaml
kubectl exec -it deploy/cert-generator -- sh
# Inside Pod:
mv server-cert.pem tls.crt
mv server-key.pem tls.key
kubectl create secret tls kiamol-cert --key=tls.key --cert=tls.crt
exit
```

**Step 8 — Update Ingress to enable HTTPS:**
```yaml
spec:
  rules:
  - host: todo.kiamol.local
    http:
      paths:
      - path: /new
        backend:
          serviceName: todo-web
          servicePort: 80
      # ... other paths ...
  tls:
  - secretName: kiamol-cert
```
```bash
kubectl apply -f todo-list/update/ingress-https.yaml
# Browse https://todo.kiamol.local — HTTPS active
# curl http://todo.kiamol.local → 308 redirect to HTTPS (Nginx automatic)
```

**Result**: Single ingress controller handles all routing. The app is publicly available only at explicitly listed paths. TLS terminates at the controller. Sticky sessions prevent anti-forgery failures under scale. The app's internal ClusterIP Service is never directly exposed.

---

## Key Takeaways

1. Ingress replaces per-app LoadBalancer Services with a single entry point, reducing IP sprawl and centralizing routing, TLS, and access control.
2. The Ingress object is controller-agnostic for core features (host/path routing, TLS Secret reference); advanced features require controller-specific annotations that are not portable.
3. TLS termination at the ingress layer centralizes certificate management — applications receive plain HTTP internally, removing the need to handle certificates per app.
4. PathType (`Exact`, `Prefix`) enables Ingress objects to act as an access allowlist, blocking sensitive endpoints (metrics, diagnostics) without any application changes.
5. Ingress classes are mandatory in multi-controller clusters; without them, controllers fight over Ingress objects and routing becomes unpredictable.
6. Switching ingress controllers is a migration project: annotation dialects, feature availability (e.g., PathType support), and routing models (sticky at Ingress level vs. Service level) all differ between implementations.
7. The Kubernetes community recognized Ingress limitations and began developing the Gateway API as a long-term replacement; Ingress remains the production standard in the near term.

---

## Connects To

- **Chapter 6** — Nginx used as a caching reverse proxy per-app; Chapter 15 elevates this to cluster-wide ingress caching via annotations.
- **Chapter 9** — Versioned web app (`vweb-v1`, `vweb-v2`) reused to demonstrate multi-path Ingress routing.
- **Chapter 13** — randomnumber API used a per-app reverse proxy; Ingress centralizes that pattern.
- **Chapter 14 (Services)** — ClusterIP Services are the backends for Ingress rules; LoadBalancer Services are what the ingress controller itself exposes.
- **ConfigMaps and Secrets (Chapter 4)** — TLS certificates are stored as TLS Secrets (`kubectl create secret tls`), the same Secret subsystem used for application configuration.
- **StorageClass (Chapter 5)** — IngressClass is a parallel concept: a named class selects which controller handles a resource, just as StorageClass selects which provisioner handles a PVC.
- **Scaling and controllers (Chapter 6)** — Ingress sticky sessions are the remedy for stateful anti-forgery failures when Deployments are scaled beyond one replica.
- **Gateway API** — The forthcoming replacement for Ingress, addressing annotation portability and feature standardization limitations described in section 15.5.
