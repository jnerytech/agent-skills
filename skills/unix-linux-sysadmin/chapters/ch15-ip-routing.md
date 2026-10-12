# Chapter 15: IP Routing

## Core Idea
IP routing is **next-hop routing**: each system only decides the *next* router toward a destination, not the whole path. Two meanings of "routing": forwarding packets (simple) vs. building the routing table (tricky). For most networks, a single **static default route** is all you need; dynamic routing protocols (RIP/OSPF/EIGRP/BGP) matter only in complex topologies that must adapt to link failures. **Don't use UNIX/Linux boxes as production routers — buy a dedicated router.**

## Frameworks Introduced
- **Longest-match forwarding**: the kernel picks the *most specific* matching route (longest netmask); else the default route (`0.0.0.0/0`); else returns ICMP "network unreachable." Gateways must be exactly one hop away.
- **Two protocol families**: **distance-vector** ("gossipy" — announce how far you are from each network; simple but slow to converge, loop-prone, chatty) vs. **link-state** (share raw "X↔Y link is up" facts; each router builds a full map; fast convergence but more CPU/memory).
- **Cost metric**: a number per link (hops, latency, bandwidth, $); path cost = sum of link costs. Defaults work in 99% of cases — to deprioritize a link for political/financial reasons, artificially boost its cost.
- **Four routing-complexity levels** (selection criteria): no routing → static routes only → mostly static + clients listen to RIP → dynamic routing everywhere.

## Key Concepts
- **Routing daemon inputs**: config files + existing routing table + other daemons' advertisements → compute optimal routes → feed back into the kernel table (and to peers).
- **Autonomous System (AS)**: networks under one administrative entity. **Interior** protocols route within an AS; **exterior** protocols (BGP) route *between* ASes and hide internal topology.
- **RIP** (distance-vector, hop-count metric, ≥15 hops = unreachable): simple, widely supported lowest-common-denominator; chatty (broadcasts every 30s); doesn't scale. RIPv2 adds netmasks/CIDR; RIPng is IPv6-only.
- **OSPF** (the only mainstream link-state protocol): industrial-strength, supports areas + multiple paths; worthwhile only at scale with hierarchical addressing.
- **EIGRP**: Cisco-proprietary, advanced distance-vector (avoids DV loop/convergence problems); ~equal to OSPF functionally but locks you to Cisco.
- **BGP**: the exterior protocol for Internet backbone routing (~660k prefixes); sends full table once then only changes. Needed when connected to *multiple* ISPs.
- **ICMP redirects**: a router tells a host "use this better gateway." Some sites abuse them as a poor man's dynamic routing — *don't*; handling varies (some ignore for security), they clutter tables and add load.

## Mental Models
- **Forwarding ≠ route computation.** Moving a packet is trivial (table lookup + send to next hop); building the table correctly is the hard part — that's what "routing" usually means.
- **A router rewrites the Ethernet header, not the IP header.** When R1 forwards A's packet to B, the IP source still says A; only the link-layer MAC addresses change hop to hop.
- **Skip the "RIP zone."** RIP fits a narrow band — too complex for no protocol, too simple for OSPF. If you expect growth, jump straight past RIP to OSPF/EIGRP. RIP is still fine as a *distribution* mechanism to leaf nodes (passive/`-q` mode).
- **Default strategy for a medium site**: static routes internally (forward unknowns to a default gateway) + dynamic routing only at that gateway / political boundaries.

## Anti-patterns
- **UNIX/Linux as a production router**: dedicated routers are simpler, more reliable, secure, and faster. Use a Linux box only for lightly-populated test/auxiliary subnets.
- **Relying on ICMP redirects as a routing "protocol"**: inconsistent handling, table clutter, extra load, security risk — properly configured networks never show redirects in the routing table.
- **Running a dynamic protocol where one gateway exists**: a single-exit network needs only a static default route — no dynamic updates.
- **Standardizing on EIGRP**: proprietary to Cisco, limits future hardware choices despite Cisco's quality.
- **Link-local addresses for normal traffic**: `fe80::/10` (IPv6) is scoped to the local segment (used by OSPF etc.) — don't route real traffic over it.

## Code Examples
```sh
# Inspect routing tables
netstat -rn          # numeric routing table (FreeBSD + Linux net-tools)
ip route             # Linux preferred (net-tools deprecated)
# Example default route entry:
#   0.0.0.0  199.165.145.24  0.0.0.0  UG  ...  eth0   (UG = up, gateway)

# Quagga (mainstream multi-protocol routing daemon): core zebra + ripd/ospfd/bgpd
vtysh                # Cisco-IOS-like CLI
#   enable            -> privileged mode
#   config term       -> enter config
#   write             -> save to config file

# routed -q : passive RIP — listen for routes, advertise nothing
```
```
# Cisco IOS basics
ssh acme-gw.acme.com        # user mode (prompt ends in >)
  enable                    # privileged mode (prompt ends in #) — careful!
  show running              # current running config
  show interfaces
  config term               # edit config
    interface Ethernet0
    ip address 192.225.40.253 255.255.255.0
  <Ctrl-Z>
  write mem                 # save to NVRAM
```

## Reference Tables
**Protocols**: RIP/RIPng (distance-vector, hop count, internal LANs) · EIGRP (Cisco DV, WAN/corporate) · OSPF (link-state, large topologies) · BGP (exterior, Internet backbone).

**Routing-protocol multicast addresses**: all routers `224.0.0.2`/`ff02::2`, OSPF `224.0.0.5`/`ff02::5`, RIP `224.0.0.9`/`ff02::9`, EIGRP `224.0.0.10`/`ff02::10`.

**UNIX/Linux routing software**: `routed` (obsolete, RIP only, useful for `-q` passive mode) · **Quagga** (RIP/OSPF/BGP, `zebra` core + per-protocol daemons, `vtysh` CLI) · XORP (full router-in-a-box, even a live CD). No UNIX EIGRP implementation exists.

## Worked Example
**Why host B needs an extra route (dual-router network).** B sits on net 199.165.146 with two routers: R1 (to internal net 199.165.145) and R2 (to the Internet). With only a default route to R2, a packet B→A (on 199.165.145) goes to R2, which forwards it to R1 *and* sends B an ICMP redirect; B then installs a host route `199.165.145.17 via R1`. This "works" but: it relies on redirects (inconsistent, cluttering, one host route per destination — other hosts on A's net each need their own redirect). The correct config gives B an *explicit* static route for the whole `199.165.145.0/24` net via R1, plus the default via R2 — no redirects, no clutter. The lesson: in a properly configured network, redirects should never appear in the routing table.

## Key Takeaways
1. Routing = next-hop; forwarding is trivial, table-building is the hard part (and the usual meaning of "routing").
2. A static default route reaches anywhere — adopt dynamic protocols only for complex/adaptive topologies or at administrative boundaries.
3. Distance-vector (RIP/EIGRP/BGP) gossips distances; link-state (OSPF) shares a full map and converges faster.
4. Match protocol to scale: static/default for simple nets, OSPF/EIGRP for large ones, BGP only for multi-ISP/backbone; skip the RIP zone if you expect growth.
5. Never abuse ICMP redirects as dynamic routing; use explicit static routes.
6. Don't run production routing on UNIX/Linux — use dedicated routers (Cisco IOS basics: `enable` → `config term` → `write mem`); back up configs (RANCID).

## Connects To
- **Ch 13**: routing tables, default routes, CIDR/netmasks, `ip route`/`route`.
- **Ch 14**: routers as layer-3 devices; switches vs routers.
- **Ch 16**: DNS (OSPF/link-local discovery; resolving gateway names).
- **Ch 27**: access lists / router security, securing VTYs.
