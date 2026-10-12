# Chapter 19: Load Balancing at the Frontend
*Authors: Piotr Lewandowski (edited by Sarah Chavis)*

## Core Idea
No single machine, however powerful, can serve global traffic: physics (speed of light) and the single-point-of-failure risk forbid it. Frontend load balancing is layered: **DNS load balancing** picks a datacenter before the connection starts, then **VIP load balancing** (network load balancers + consistent hashing + GRE encapsulation) picks a machine inside it.

## Frameworks Introduced
- **"Optimal" depends on context**: optimal distribution depends on (1) the hierarchical level (global vs local), (2) the technical level (hardware vs software), and (3) the nature of the traffic.
  - When to use: before choosing any routing policy.
  - How: classify the request by its dominant variable. Latency-sensitive (search) → nearest datacenter by RTT. Throughput-sensitive (video upload) → possibly an underutilized link, trading latency for throughput. Inside a datacenter → assume equal distance; optimize resource utilization and protect individual servers from overload. Other considerations: route slightly farther to keep caches warm; send noninteractive traffic to another region to avoid congestion.

- **DNS Load Balancing (first layer)**: return addresses in the DNS reply so the client is steered before the connection even starts.
  - When to use: always as the first, coarse layer; the "simplest and most effective way to balance load before the user's connection even starts" — but never sufficient alone.
  - How:
    1. Naive: return multiple A/AAAA records; client picks randomly (little control, roughly equal traffic per record; SRV weights not adopted for HTTP).
    2. Serve authoritative nameservers on an **anycast** address so queries reach the closest server, which returns the closest datacenter.
    3. Better: maintain a map of networks → approximate physical locations and answer per mapping (costs a complex DNS server + a pipeline to keep the map fresh).
    4. Use **EDNS0** client-subnet info so the answer is optimal for the user, not the recursive resolver.
    5. Track known resolvers with the approximate user base and geographic distribution behind each, to estimate the impact of each reply.
    6. Integrate the authoritative DNS server with global control systems tracking traffic, capacity, and infrastructure health — "best location" = close AND has capacity AND is healthy.
    7. Keep TTL relatively low (you can't flush resolver caches) and replies within the **512-byte RFC 1035 limit**.
  - Failure mode: the **DNS middleman** (recursive resolver) causes three problems — recursive resolution of IP addresses (you see the resolver's IP, not the user's), nondeterministic reply paths (one ISP resolver can serve a whole continent), and additional caching complications (one reply may reach 1 or thousands of users; TTL bounds how fast changes propagate, and not all resolvers respect TTL).

- **VIP Load Balancing with a Network Load Balancer (second layer)**: a virtual IP shared across many devices, fronted by a balancer that forwards each packet to a backend.
  - When to use: after DNS, to spread load across machines while hiding pool size and enabling invisible maintenance.
  - How (backend selection):
    1. "Least loaded backend" is intuitive but breaks for stateful protocols — the balancer must track every connection.
    2. Stateless alternative: `id(packet) mod N` — but removing one backend changes N and remaps almost every connection, resetting them.
    3. Use **consistent hashing** (1997): mapping stays stable as backends are added/removed. Google's practice: simple connection tracking normally, fall back to consistent hashing under pressure (e.g., DoS attack).
  - How (packet forwarding), in evolution order:
    1. **NAT** — requires a tracking-table entry per connection; precludes a stateless fallback.
    2. **Layer-2 rewrite / Direct Server Response (DSR)** — change destination MAC; backend replies directly to the user. Huge savings when requests are small and replies large; stateless. But all balancers and backends must share one broadcast domain — Google outgrew it.
    3. **Packet encapsulation with GRE** (current, Maglev [Eis16]) — wrap the packet in another IP packet addressed to the backend; backend strips the outer IP+GRE. Balancer and backend can be on different continents.
  - Failure mode: GRE adds **24 bytes** (IPv4+GRE) overhead, risking MTU overflow and fragmentation; mitigated with a larger in-datacenter MTU (requires network support for large PDUs).

## Key Concepts
- **Single point of failure**: the reason "power isn't the answer" — even a perfect supercomputer is a bad design.
- **RTT (round-trip time)**: metric for "nearest" datacenter for latency-sensitive traffic.
- **Recursive DNS resolver**: middleman between users and authoritative nameservers that proxies and caches answers.
- **EDNS0 client subnet**: DNS extension that passes the client's subnet to the authoritative server.
- **Anycast**: one address announced from many places; packets flow to the nearest.
- **TTL**: caching lifetime of a DNS record; sets the lower bound on how fast DNS changes propagate.
- **VIP (Virtual IP)**: an IP not bound to one interface, shared across many devices, appearing to users as a single regular IP.
- **Network load balancer**: the device that receives VIP packets and forwards them to a backend.
- **Consistent hashing**: mapping that minimally disrupts existing connections when the backend pool changes.
- **DSR (Direct Server Response)**: backend replies to the client directly, bypassing the balancer.
- **GRE (Generic Routing Encapsulation)**: IP-in-IP encapsulation used by Google's VIP balancers.
- **MTU**: max transmission unit; encapsulation overhead can exceed it and cause fragmentation.

## Mental Models
- Think of frontend load balancing as **two funnels**: DNS is a coarse, slow-to-change, cache-polluted funnel to a datacenter; VIP balancing is a fine, fast funnel to a machine.
- Use **consistent hashing when pool membership changes** (failures, scaling, attack) and per-connection state is unaffordable — `mod N` is fine only for a frozen pool.
- Think of a **DNS reply as a broadcast of unknown size**: one answer may steer one user or a whole ISP for the TTL duration — weigh it by the resolver's estimated user base.
- Use **DSR / encapsulation when replies dwarf requests** (HTTP): keep the heavy return path off the balancer.

## Anti-patterns
- **Relying on "a bigger box"**: still a single point of failure and still bound by the speed of light.
- **Plain multi-A-record round robin as the whole strategy**: random client choice, equal traffic per record, no proximity, no capacity awareness.
- **Optimizing for the resolver's location**: users behind a centralized ISP resolver get sent to the resolver's best datacenter, not theirs.
- **High DNS TTLs**: you can't flush resolver caches, so changes (e.g., draining a datacenter) take too long.
- **`id(packet) mod N` without consistent hashing**: losing one backend resets nearly all connections.
- **NAT-based forwarding at scale**: requires full per-connection state; no stateless fallback.
- **Layer-2 DSR across a growing fleet**: forces everything into one broadcast domain.

## Code Examples
```
id(packet) mod N
```
What it demonstrates: stateless connection-to-backend mapping; all packets of a connection go to the same backend — until N changes to N-1 and almost every packet remaps (motivating consistent hashing).

## Reference Tables
| Forwarding method | Balancer state | Reply path | Limitation |
|---|---|---|---|
| NAT | Entry per connection | Through balancer | No stateless fallback |
| L2 MAC rewrite (DSR) | None | Direct backend → user | All machines in one broadcast domain |
| GRE encapsulation | None needed | Direct backend → user | +24 bytes (IPv4+GRE) → MTU/fragmentation |

| Traffic type | Dominant variable | Global routing choice |
|---|---|---|
| Search request | Latency | Nearest datacenter by RTT |
| Video upload | Throughput (succeed first time) | Possibly underutilized link, accepting extra latency |

Key numbers: DNS reply limit **512 bytes** (RFC 1035; otherwise the user needs TCP just to get IPs); GRE overhead **24 bytes**; consistent hashing proposed **1997** [Kar97].

## Worked Example
**Search vs. video upload.** A user's search query hits DNS; the authoritative server (reached via anycast, informed by EDNS0 client subnet and resolver-size estimates) returns an IP for the nearest healthy datacenter with spare capacity. The packet reaches a VIP; the network load balancer picks a backend via connection tracking (or consistent hashing if under attack), wraps the packet in GRE to that backend, and the backend replies directly to the user. A video upload from the same user may instead be routed over an underutilized link to maximize throughput, since users tolerate upload time but expect first-time success. If a backend dies mid-stream, consistent hashing ensures only its connections remap rather than nearly all (as `mod N` would).

## Key Takeaways
1. Never design around one big machine; distribute across links, datacenters, and machines.
2. Classify traffic by its key variable (latency vs throughput) before choosing a routing target.
3. Use DNS as the first layer, but make it location-, capacity-, and health-aware (anycast, network map, EDNS0, resolver tracking) and keep TTLs low.
4. Always follow DNS with a VIP layer — DNS alone can't address enough servers (512-byte limit) or react fast enough.
5. Use consistent hashing so backend churn doesn't reset every connection; fall back to it under load/attack.
6. Prefer encapsulation (GRE) over L2 DSR at scale, and plan for MTU/fragmentation overhead.

## Connects To
- **Ch 2**: GFE, GSLB, and datacenter topology that this layer routes into.
- **Ch 20**: the next zoom level — load balancing within the datacenter (subsetting, Weighted Round Robin).
- **Ch 21**: overload handling when balancing can't prevent hotspots.
- **Ch 22**: load balancer behavior can spread overload across clusters (cascading failures).
- **Ch 3/4**: latency and availability targets that drive "optimal" routing.
- **Maglev [Eis16]**: Google's software network load balancer using GRE + consistent hashing.
- **Consistent hashing (Karger et al. 1997)**: foundational for stable distributed mapping.
