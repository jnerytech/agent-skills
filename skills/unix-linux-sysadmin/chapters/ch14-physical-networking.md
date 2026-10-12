# Chapter 14: Physical Networking

## Core Idea
The link layer beneath IP is dominated by **Ethernet** (>95% of LANs) — wired (UTP/fiber) and wireless (Wi-Fi). Build good networks on four pillars: reasonable design, quality hardware, proper installation + documentation, and competent ongoing operations. Even in a virtualized/SDN world, virtual networks emulate physical ones, so this knowledge stays essential.

## Frameworks Introduced
- **CSMA/CD**: Ethernet's original "polite dinner party" access model — Carrier Sense (listen first), Multiple Access (everyone may talk), Collision Detection (back off a random time on collision). Switches made it nearly moot by reducing collision domains to two devices.
- **Connection devices by cost/intelligence**: hub (layer 1, repeater — obsolete) < switch (layer 2, learns MAC→port, forwards selectively) < router/"layer-3 switch" (layer 3, routes by IP, filters/prioritizes).
- **Two golden rules of autonegotiation**: (1) *required* on all ≥1 Gb/s interfaces; (2) on ≤100 Mb/s, either autoneg on *both* ends or manually set speed+duplex on *both* — never one side each (causes a mismatch and poor performance).
- **Broadcast domain = one logical segment.** Switches forward broadcasts to all ports in a segment; isolate broadcast traffic with routers (or VLANs) to prevent broadcast storms when a segment exceeds ~100 hosts.

## Key Concepts
- **Logical vs physical segment**: with switches, one logical segment spans many physical segments (each = one switch port + one host). Broadcast goes to all; unicast/multicast only where needed.
- **UTP categories**: Cat5 (100 Mb/s, baseline), Cat5e/6/6a (1 Gb/s — 6a preferred for new installs, interference-resistant), Cat7/7a (10 Gb/s), Cat8 (40 Gb/s). All limited to 100 m. Faster standards need more pairs.
- **Fiber**: multimode (in-building/campus, thicker, cheap LED optics) vs single-mode (long-haul, precision optics). Everything must match (type/size/connectors) or face hard-to-isolate problems.
- **VLAN**: software-partitioned switch ports forming separate logical segments; inter-VLAN traffic goes through a router. 802.1Q trunking spans VLANs across switches. *VLANs alone give little security — you must filter between them.*
- **PoE (802.3af)**: power + data over one UTP cable (VoIP phones, WAPs). Budget power closet wattage accordingly.
- **Jumbo frames**: MTU >1500 (commonly 9000) — ~10% throughput gain for large TCP transfers (NFS/SMB). All equipment on the subnet must support them.
- **Wi-Fi**: 802.11g (2.4GHz, 54Mb/s), 802.11n (2.4/5GHz, ~400Mb/s real), 802.11ac (~1Gb/s). WAPs advertise SSIDs (map to VLANs); non-overlapping 2.4GHz channels = 1, 6, 11.
- **SDN**: separates control plane (manages) from data plane (forwards packets); data plane programmable for dynamic, API-driven topology.

## Mental Models
- **Switch first, never hub.** Hubs blindly repeat to all ports; switches learn MAC locations and forward selectively, multiplying effective bandwidth. Hubs are obsolete even at home.
- **A network is a chain — only as good as its weakest link.** Ethernet performance degrades *nonlinearly* under load; isolate local traffic with subnets/routers; keep file-sharing (NFS/SMB) off the backbone.
- **Backplane speed is the number that counts.** A well-designed switch's backplane exceeds the sum of all port speeds. Trust independent evaluations, not vendor marketing.
- **Wireless: WEP is broken, use WPA2.** Mnemonic: WEP = "Wired Equivalent Privacy" = as protected as plugging a stranger into your wired net (i.e., none). Never use WEP even at home; no WPA2 → never inside the firewall.
- **Do building wiring right the first time** — cost is mostly labor, not materials. Pull 3–4× the pairs you need and run both multi/single-mode fiber to hard-to-reach places. "The kind you need in the future is always the kind you didn't install."

## Anti-patterns
- **One-side-only autonegotiation** on ≤100 Mb/s links: the manual side won't learn the auto side's settings → mismatch, high large-packet loss.
- **>~100 hosts in one switched logical segment**: broadcast storms; split with routers/VLANs.
- **Relying on VLANs for security without inter-VLAN filtering**: provides essentially no protection.
- **Mixing jumbo and non-jumbo equipment on a subnet**: must be uniform; devices may *accept* but not *generate* jumbo frames — enable explicitly.
- **Mismatched fiber types/sizes** (e.g., OM1 vs OM2, both orange): endless hard-to-isolate problems — check the size imprint.
- **PVC cable in return-air plenums**: toxic fumes if it burns — use Teflon (and respect fire codes / firewall penetrations).
- **Public/hallway ports on the internal network**: put them on a guest VLAN or use 802.1x.

## Code Examples
```sh
# Wireless client (FreeBSD/Linux)
iwlist scan                 # list available access points
iwconfig wlan0 essid "Net"  # configure connection params
wpa_supplicant ...          # authenticate (WPA2 / 802.1x)
ifconfig wlan0 ...          # bring up the interface

# Jumbo frames = raise the MTU (see Ch13 ip/ifconfig)
ip link set dev eth0 mtu 9000

# Debugging: capture and inspect packets (link layer)
wireshark                   # free packet sniffer of choice
```

## Reference Tables
**Ethernet speeds**: 10BASE-T (Cat3) → 100BASE-TX (Cat5, 2 pairs) → 1000BASE-T "gigabit" (Cat5e/6, 4 pairs) → 10GBASE-T (Cat6a/7) → 40/100/200/400 Gb/s (fiber). All copper limited to 100 m.

**Connection devices**: hub (L1, repeat-all, obsolete) · switch (L2, MAC-learning, selective forward, industry standard) · VLAN switch (software-partitioned segments) · router (L3, IP routing + filtering, fixed or modular).

**Debug tools**: hand-held cable analyzer (TDR — length, breaks, miswiring; e.g. Fluke LanMeter) for electrical/cabling; packet sniffer (Wireshark) for link-layer protocol errors — can't diagnose cabling.

## Worked Example
**Diagnose a flaky link: cabling or protocol?** The two tool classes answer different questions. If a host has intermittent connectivity, first check switch "idiot lights" (link status / traffic) against your wiring documentation — this is why labeling pays off. Suspect the *physical* layer? Use a cable analyzer with **time-domain reflectometry**: it measures the cable's length and pinpoints breaks or miswiring electrically. Suspect *protocol/config* (duplex mismatch, bad MTU, misconfigured host)? A cable analyzer is blind to these — use **Wireshark**, which operates at the link layer and disassembles packets to expose protocol errors, but can't see cabling/electrical faults. A classic culprit the sniffer reveals: high large-packet loss from one-sided autonegotiation — fix by setting *both* ends consistently (auto/auto or manual/manual).

## Key Takeaways
1. Ethernet dominates the link layer; switches (L2 MAC-learning) replaced hubs and shrank collision domains — always switch, never hub.
2. Autonegotiation must match on both ends; ≥1 Gb/s requires it, ≤100 Mb/s needs both-auto or both-manual.
3. Keep logical segments under ~100 hosts; isolate broadcast traffic and file-sharing with routers/subnets/VLANs (filter between VLANs for security).
4. Cat6a + fiber for new wiring; do it right the first time, over-provision pairs, label everything, document obsessively.
5. Wireless: WPA2 always, WEP never; map SSIDs to VLANs; non-overlapping 2.4GHz channels 1/6/11.
6. Debug by isolating components: cable analyzer (TDR) for physical faults, Wireshark for protocol faults.

## Connects To
- **Ch 13**: the IP layer above (MTU/jumbo frames, autonegotiation set via `ip`/`ifconfig`, broadcast/subnet).
- **Ch 15**: IP routing (routers as layer-3 devices).
- **Ch 27**: security (802.1x port auth, guest VLANs, WPA2).
- **Ch 30**: data center basics (cabling, power/PoE, cooling).
