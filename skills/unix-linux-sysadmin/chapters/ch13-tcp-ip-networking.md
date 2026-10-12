# Chapter 13: TCP/IP Networking

## Core Idea
TCP/IP is the hardware/OS-independent protocol suite underlying the Internet. Master the layered model (link → IP → transport), addressing (MAC, IP, hostname, port), **subnetting/CIDR arithmetic**, NAT/private addresses, the IPv4↔IPv6 relationship, and routing. The single most important practical skill is reading and computing subnet masks; the everyday tools are `ip` (Linux) / `ifconfig` (FreeBSD), `ip route`/`route`, and `sysctl`.

## Frameworks Introduced
- **The protocol suite**: IP (routing, RFC791), ICMP (errors/control), ARP (IP→MAC), UDP (unreliable one-way), TCP (reliable, flow-controlled, error-corrected). Layered as a stack; higher protocols use lower.
- **Encapsulation**: each layer wraps the one above as its payload — Ethernet frame ⊃ IP packet ⊃ TCP segment ⊃ app data; reversed on receipt. Names by layer: frame (link), packet (IP), segment (TCP).
- **Three addressing schemes used together**: MAC (hardware, 6-byte), IP (software, hardware-independent), hostname (people). **IP addresses identify interfaces, not machines.**
- **Subnetting + CIDR**: a netmask's contiguous leftmost 1s mark the network portion. CIDR (`/N` notation) lets the boundary fall between any bits and aggregates routes (supernetting). Network portion + host portion; all-0 host = network address, all-1 host = broadcast.

## Key Concepts
- **Ports**: 16-bit (1–65535) channel selectors on top of IP; TCP and UDP port spaces are separate. Well-known ports in `/etc/services`. Ports <1024 require root/capability to *bind* (not to connect).
- **MTU**: max link payload (Ethernet 1500). IPv4 routers fragment oversized packets; IPv6 forbids in-flight fragmentation (sender does path-MTU discovery; min 1280). TCP does path-MTU discovery automatically.
- **Address types**: unicast (one interface), multicast (a group, via IGMP), broadcast (all on subnet), anycast (nearest of a group — load balancing at the routing layer).
- **Private addresses (RFC1918)**: `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16` — internal only, never routed on the Internet.
- **NAT/PAT**: border router rewrites private source addresses (and ports) to a public IP, keeping a translation table. Hides interior structure but is *not* a substitute for a firewall.
- **IPv6**: 128-bit addresses, fixed /64 network boundary (no real subnetting), written as 8 hex groups (`::` collapses one run of zero groups). SLAAC = stateless autoconfig (link-local `fe80::/64` + router advertisements + EUI-64 host ID from MAC).
- **Routing**: kernel matches a packet's destination to the *most specific* (longest-mask) route; falls back to the default route (`0.0.0.0/0`); else returns ICMP "network unreachable."

## Mental Models
- **Subnet arithmetic shortcuts**: `last netmask byte = 256 − network size`; a network address's last byte must be evenly divisible by the network size. A `/N` network has `2^(32−N)` addresses, minus 2 (network+broadcast) usable hosts (except `/31`, RFC3021, both usable).
- **You don't choose IPv4 vs IPv6 — you choose IPv4-only vs both.** IPv4 support remains mandatory (major sites still lack AAAA records); IPv6's only real driver is address exhaustion, and managing both eliminates efficiency gains. Support IPv6 if civic-minded or running public services; otherwise no urgency.
- **Autonegotiation is all-or-nothing.** If you manually set speed/duplex on one side, you must manually set both — you can't manually configure one end and let the other auto-adapt. Failed autoneg shows as high large-packet loss.
- **CIDR aggregates routes.** A site's `192.144.0.0/21` is one backbone routing entry regardless of how it's internally split (variable-length subnetting) — all hosts on one network must share the same netmask.

## Anti-patterns
- **Weird broadcast addresses**: inconsistent per-host broadcast addresses cause broadcast storms (packets loop until TTL expires). Block broadcast pings at the border + tell hosts not to respond, instead.
- **Tuning `/proc/sys/net/.../conf/all`**: change-propagation rules are undocumented (AND/OR/MAX vary per variable) — confine changes to individual interfaces or `conf/default`.
- **Tweaking network sysctls on a production box you're SSH'd into**: you can lock yourself out and need console recovery. Test on a desktop first.
- **Editing `/etc/services`**: it's infrastructure — never modify it.
- **MTU mismatch in VPN tunnels**: 1500-byte packets + tunnel header → 1540 → fragmentation. Lower the link MTU to avoid it.

## Code Examples
```sh
# Inspect interfaces / addresses / routes (Linux ip; FreeBSD ifconfig/route)
ip link show ; ip address show          # interfaces; bound addresses
ip address add 192.168.1.13/26 broadcast 192.168.1.63 dev enp0s5
ip route show ; netstat -nr             # routing table (numeric)
ip route add 192.168.45.128/25 via zulu-gw.atrust.net   # add route
ip route add default via 192.168.0.1    # default route (= 0.0.0.0/0)
ip route del ... ; ip route flush

# Hardware media options (Linux)
ethtool eth0                            # query speed/duplex/autoneg
ethtool -s eth0 speed 100 duplex full   # lock (transient — put in iface config)

# Kernel network tuning
sysctl net.ipv4.icmp_echo_ignore_broadcasts=1   # Smurf-attack defense
sysctl net.ipv4.ip_forward=0                     # disable routing
# persist in /etc/sysctl.conf

# Subnet math helper
ipcalc 24.8.175.69/28
```
```ini
# Debian/Ubuntu  /etc/network/interfaces
auto lo enp0s5
iface lo inet loopback
iface enp0s5 inet static
  address 192.168.1.102
  netmask 255.255.255.0
  gateway 192.168.1.254
# iface enp0s5 inet dhcp    # DHCP alternative

# Red Hat/CentOS  /etc/sysconfig/network-scripts/ifcfg-eth0
DEVICE=eth0
IPADDR=192.168.1.13
NETMASK=255.255.255.0
ONBOOT=yes
# BOOTPROTO=dhcp            # DHCP alternative

# DNS client  /etc/resolv.conf
search cs.colorado.edu colorado.edu
nameserver 128.138.242.1
nameserver 128.138.243.151
```

## Reference Tables
**Subnet decode** (IP 128.138.243.100): `/16` → net 128.138.0.0, bcast 128.138.255.255 · `/24` → net 128.138.243.0, bcast .243.255 · `/26` (mask 255.255.255.192) → net 128.138.243.64, bcast .243.127, 62 hosts.

**Private ranges (RFC1918)**: `10.0.0.0/8` (A), `172.16.0.0/12` (B), `192.168.0.0/16` (C). Loopback `127.0.0.1` = localhost. IPv6 loopback `::1`, link-local `fe80::/64`.

**Config file map**: hostname → `/etc/hostname` (Deb) / `/etc/sysconfig/network` (RH). Interfaces → `/etc/network/interfaces` (Deb) / `/etc/sysconfig/network-scripts/ifcfg-*` (RH). DNS client → `/etc/resolv.conf` (both). Net tunables → `/proc/sys/net/ipv4|ipv6` via `sysctl`.

## Worked Example
**Split a `/24` into four `/26` networks.** Given `128.138.243.0/24`, borrow 2 bits for the network → `/26`, mask `255.255.255.192`. The two borrowed bits take values 00/01/10/11 → networks `.0`, `.64`, `.128`, `.192` (each last byte divisible by the size 64 — the shortcut). Each `/26` has `2^6 = 64` addresses but only **62 usable hosts** (subtract the all-0 network address and all-1 broadcast). For `.64/26`: network = .64, broadcast = .127, hosts .65–.126. Verify with the mask shortcut: `256 − 64 = 192` = the last netmask byte. `ipcalc 128.138.243.100/26` confirms it. All hosts on one of these networks must use the identical `/26` mask — you can't mix `/26` and `/25` on the same wire.

## Key Takeaways
1. TCP/IP is layered and hardware-independent; encapsulation nests each layer's data inside the next.
2. IP addresses identify interfaces; combine MAC (hardware), IP (software), hostname (people), and port (process).
3. Subnetting/CIDR is the core arithmetic — netmask 1s = network bits, usable hosts = `2^(32−N) − 2`; memorize the `256 − size` and divisibility shortcuts.
4. NAT + RFC1918 private addresses + CIDR are what deferred the IPv4 exhaustion crisis; NAT ≠ firewall.
5. IPv6 = bigger addresses, fixed /64 boundary, SLAAC autoconfig — but you must run it *alongside* IPv4, so adopt at your own pace (mandatory for public services).
6. Configure with `ip`/`ifconfig` + distro files (`interfaces` / `ifcfg-*`); tune the stack via `/proc/sys/net` and `sysctl` (per-interface, tested first).

## Connects To
- **Ch 11**: kernel network tunables in `/proc/sys/net`, `sysctl`.
- **Ch 14**: physical networking (Ethernet, switches, the link layer below IP).
- **Ch 15**: IP routing protocols (building the routing table).
- **Ch 16**: DNS (hostname↔IP resolution, `/etc/resolv.conf`).
- **Ch 9**: cloud networking (virtual networks, security groups) builds on these concepts.
