# Chapter 10: Service discovery deep dive

## Core Idea
Apps on Kubernetes talk to each other via the **Service** in front of each app, never the Pods directly. Two things are needed: (1) knowing the other app's Service **name** (developer's job), and (2) converting that name into an **IP address** (Kubernetes' job). Service discovery is the name-to-IP machinery, and on Kubernetes it is **automatic** — implemented by the **cluster DNS (CoreDNS)** acting as the cluster's **service registry**.

## Frameworks Introduced (registration vs resolution — the two halves)
Service discovery has two automatic halves:

1. **Service registration** — putting names+IPs *into* the registry.
   - Steps: (1) assign Service a name [developer], (2) assign Service a ClusterIP [K8s], (3) register name+IP in cluster DNS [K8s].
   - Cluster DNS watches the API server for new Services; on each new one it registers DNS **A records** and **SRV records**. Apps need *zero* registration logic.
2. **Service resolution / discovery** — getting IPs *out* of the registry.
   - Every container's `/etc/resolv.conf` is auto-configured (by the kubelet) with the cluster DNS Service IP and search domains.
   - App sends short name → container queries cluster DNS → DNS returns ClusterIP → traffic routed to a Pod.

## Key Concepts
- **Service registry** = the built-in **cluster DNS**. Maintains list of Service names ↔ ClusterIPs.
- **CoreDNS / kube-dns**: cluster DNS runs as a **Deployment** (`coredns`, or `kube-dns` on GKE) of 2+ Pods, fronted by a Service **always named `kube-dns`**, in the `kube-system` Namespace, labeled `k8s-app=kube-dns`, listening on **port 53 TCP/UDP** (image: `registry.k8s.io/coredns/coredns`).
- **Service registration is automatic** — cluster DNS observes new Service objects via the API server.
- **EndpointSlice** objects hold the list of healthy Pod IPs matching a Service's label selector.
- **`/etc/resolv.conf`**: auto-configured per container with `nameserver <cluster-DNS-IP>` (commonly `10.96.0.10`), search domains, and `options ndots:5`.
- **FQDN**: `<object-name>.<namespace>.svc.cluster.local`. Short/**unqualified names** get search domains appended to become FQDNs.
- **Cluster domain**: the cluster's DNS address space, usually `cluster.local`. Object names must be unique within it (per Namespace).
- **ClusterIP routing**: ClusterIPs are virtual IPs on the **service network**, which has **no routes**. Traffic goes to the default gateway → node → node kernel, where **kube-proxy** rules trap it and redirect to a healthy Pod IP.
- **kube-proxy**: runs on every node, watches Services + EndpointSlices, writes kernel rules intercepting ClusterIP traffic and forwarding to Pod IPs.

## Mental Models
- The cluster DNS is a **phone book**: registration writes entries; discovery looks them up. Both automatic.
- A **ClusterIP is virtual** — it exists only as a kube-proxy kernel rule, not a routable address. The "no route → default gateway → kernel trap" path is the magic that turns a virtual IP into a real Pod.
- **Short name = local Namespace; FQDN = any Namespace.** `ndots:5` + search domains is why a short name silently resolves locally.

## Anti-patterns
- Assuming a short name reaches another Namespace — short names resolve only in the **local** Namespace; cross-Namespace requires the FQDN.
- Expecting apps to need registration code — registration is automatic; never build custom registration logic.
- Mismatched DNS IP: if `kube-dns` Service ClusterIP ≠ the `nameserver` in containers' `/etc/resolv.conf`, DNS queries go to the wrong place and resolution breaks.

## Code Examples
Find the cluster DNS components (all labeled `k8s-app=kube-dns` in `kube-system`):
```
$ kubectl get pods   -n kube-system -l k8s-app=kube-dns
$ kubectl get deploy -n kube-system -l k8s-app=kube-dns
$ kubectl get svc    -n kube-system -l k8s-app=kube-dns
# kube-dns  ClusterIP  10.96.0.10  53/UDP,53/TCP,9153/TCP
```

A container's `/etc/resolv.conf` (auto-configured):
```
search default.svc.cluster.local svc.cluster.local cluster.local
nameserver 10.96.0.10        # ClusterIP of internal cluster DNS
options ndots:5
```

Exec into a Pod and resolve names:
```
$ kubectl exec -it jump --namespace dev -- bash
# curl ent:8080                         # short name → LOCAL (dev) Namespace
# curl ent.prod.svc.cluster.local:8080  # FQDN → REMOTE (prod) Namespace
```

DNS sanity test with `nslookup` (use a dnsutils Pod):
```
$ kubectl run -it dnsutils --image registry.k8s.io/e2e-test-images/jessie-dnsutils:1.7
# nslookup kubernetes
Server:   10.96.0.10
Address:  10.96.0.10#53
Name:     kubernetes.default.svc.cluster.local
Address:  10.96.0.1
```
Error `nslookup: can't resolve kubernetes` ⇒ DNS broken.

## Reference Tables

**DNS name forms / resolution scope**

| Form used by app | Example | Resolves to |
|------------------|---------|-------------|
| Short / unqualified name | `ent` | Service in the **local** Namespace |
| FQDN | `ent.prod.svc.cluster.local` | Service in the **named** (remote) Namespace |
| FQDN pattern | `<object>.<namespace>.svc.cluster.local` | Any Service, fully qualified |

**Cluster DNS components (kube-system, label `k8s-app=kube-dns`)**

| Component | Name | Notes |
|-----------|------|-------|
| Deployment | `coredns` (or `kube-dns`) | manages 2+ DNS Pods |
| Pods | `coredns-*` | image `registry.k8s.io/coredns/coredns` |
| Service | `kube-dns` (always) | ClusterIP, port 53 TCP/UDP (+ 9153) |
| EndpointSlice | `kube-dns-*` | holds DNS Pod IPs on port 53 |

## Worked Example: tracing a name → ClusterIP → Pod
The `enterprise` app (behind Service `ent`) needs to reach the `cerritos` app (behind Service `cer`).

1. Developer configured `enterprise` with the name `cer`; it issues a request to `cer`.
2. The container's resolver appends a search domain (e.g. `cer` → `cer.<ns>.svc.cluster.local`) per `ndots:5` and sends the query to the **cluster DNS** at the `nameserver` IP in `/etc/resolv.conf` (`10.96.0.10`).
3. Cluster DNS returns `cer`'s **ClusterIP** (e.g. `192.168.200.217`).
4. App sends traffic to that ClusterIP. But the **service network has no routes**, so the container forwards to its **default gateway** → the node.
5. The node also has no route, forwards to its own default gateway, causing the **node kernel** to process the packet.
6. **kube-proxy**'s kernel rules trap the ClusterIP traffic and redirect it to the **IP of a healthy Pod** matching `cer`'s label selector.

Namespace proof (from the `sd-example.yml` example with identical `ent` Services in `dev` and `prod`): from the `jump` Pod in `dev`, `curl ent:8080` → "Hello from the DEV Namespace"; `curl ent.prod.svc.cluster.local:8080` → "Hello from the PROD Namespace".

## Key Takeaways
- Apps connect through **Services**; service discovery converts Service **names → ClusterIPs**.
- The built-in **cluster DNS (CoreDNS)** is the **service registry**; both registration and discovery are **automatic**.
- Containers query DNS because the kubelet auto-writes the DNS IP + search domains + `ndots:5` into `/etc/resolv.conf`.
- **Short names resolve in the local Namespace; cross-Namespace needs the FQDN** `<svc>.<ns>.svc.cluster.local`.
- ClusterIPs are virtual (no routes); **kube-proxy** kernel rules redirect ClusterIP traffic to real Pod IPs.
- Troubleshoot in order: verify `coredns` Deployment/Pods up → check CoreDNS logs → verify `kube-dns` Service IP matches `resolv.conf` → check EndpointSlice → `nslookup kubernetes`; last resort, delete `coredns` Pods to force recreation.

## Connects To
- **Ch 7 (Services)**: ClusterIP, label selectors, EndpointSlices — prerequisite knowledge.
- **kube-proxy / Pod network**: the data-plane half that completes ClusterIP → Pod routing.
- **Namespaces**: partition the cluster address space, enabling parallel `dev`/`prod` configs with identical Service names.
