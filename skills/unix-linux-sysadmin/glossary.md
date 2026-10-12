# Glossary — UNIX & Linux System Administration Handbook

**ACL (Access Control List)** — per-file/dir list of access control entries (ACEs) extending the 9-bit owner/group/other model (Ch 5).
**AFR (Annual Failure Rate)** — inverse of MTBF in steady state; real disks run ~6–8% after 2 years (Ch 20).
**Advanced Format** — 4KiB physical disk sectors; 512e emulates 512B (alignment-sensitive) (Ch 20).
**anycast** — one IP shared by several hosts; packet goes to the nearest (Ch 13).
**ARP** — Address Resolution Protocol; maps IP→MAC on a LAN (Ch 13).
**AUTH_SYS** — NFS UNIX-UID-based auth; trivially subvertible — prefer Kerberos/RPCSEC_GSS (Ch 21).
**autonegotiation** — Ethernet speed/duplex auto-config; must match (auto/auto or manual/manual) on both ends (Ch 14).
**BGP** — Border Gateway Protocol; the Internet-backbone exterior routing protocol (Ch 15).
**bhyve** — FreeBSD's (immature) hypervisor (Ch 24).
**bind mount** — mount a host dir into a container; host contents win (Ch 25).
**blue/green deployment** — stage new on standby, switch load-balancer traffic (Ch 26).
**bundle** — reusable collection of CM operations (role/formula/module/cookbook) (Ch 23).
**capability (Linux)** — one of ~30 split root privileges (e.g. `CAP_NET_BIND_SERVICE`) (Ch 3).
**cgroups** — kernel resource limits; foundation of containers (Ch 11, 25).
**CIA triad** — Confidentiality, Integrity, Availability (Ch 27).
**CIDR** — Classless Inter-Domain Routing; `/N` netmask notation, supernetting (Ch 13).
**collectd** — system-stats collection daemon, 100+ plugins (Ch 28).
**copy-on-write** — write to new blocks, keep old (LVM/ZFS/Btrfs snapshots, container layers) (Ch 20, 25).
**CSMA/CD** — Ethernet's collision-handling access scheme (Ch 14).
**CUPS** — Common UNIX Printing System; IPP-over-HTTP, port 631 (Ch 12).
**DAC / MAC** — discretionary (owner-set) vs mandatory (admin-policy) access control (Ch 3).
**dom0 / domU** — Xen privileged management domain vs unprivileged guests (Ch 24).
**DKIM** — DomainKeys Identified Mail; crypto signature published in DNS (Ch 18).
**DSN** — Delivery Status Notification; structured SMTP error code (Ch 18).
**effective UID** — the UID used for permission checks (vs real/saved) (Ch 3, 4).
**EUI-64** — derives an IPv6 host ID from a 48-bit MAC (Ch 13).
**export (NFS)** — a directory a server shares; listed in `/etc/exports` (Ch 21).
**fact (CM)** — auto-discovered system attribute (IP, OS) usable as a variable (Ch 23).
**FIM** — File Integrity Monitoring; checksum vs known-good baseline (Ch 27, 28).
**FQDN** — Fully Qualified Domain Name; in DNS, ends with a dot (Ch 13, 16).
**GECOS** — passwd field for full name/office/phone (Ch 8).
**GPT** — GUID Partition Table; modern replacement for MBR (Ch 2, 20).
**GRUB** — the standard Linux boot loader (Ch 2).
**handler (CM)** — operation triggered by a change event (e.g. restart on config change) (Ch 23).
**hard link** — extra directory entry to the same inode (same FS, counted) (Ch 5).
**HIDS / NIDS** — host- / network-based intrusion detection (OSSEC / Snort) (Ch 27, 28).
**hot/cold aisle** — data-center layout: racks draw cold-aisle air, exhaust to hot aisle (Ch 30).
**hypervisor** — software mediating between VMs and hardware (Type 1 bare-metal / Type 2 hosted) (Ch 24).
**idempotence** — an operation safely re-applicable; CM operations are idempotent (Ch 23).
**identity mapping (NFSv4)** — translates UID/GID↔`user@domain`; affects display, *not* access control (Ch 21).
**inode** — integer identifying a file's contents; hard links share it (Ch 5).
**IPP** — Internet Printing Protocol; HTTP-based, used by CUPS (Ch 12).
**JBOD** — "just a bunch of disks"; concatenation, no redundancy (Ch 20).
**Kerberos** — ticket-based authentication method; basis of AD auth (Ch 3, 17).
**KVM** — Kernel-based Virtual Machine; turns the Linux kernel into a hypervisor (Ch 24).
**LDAP** — Lightweight Directory Access Protocol; central identity store (Ch 8, 17).
**LDIF** — LDAP Data Interchange Format (text) (Ch 17).
**least privilege** — grant only the minimum access needed (Ch 3, 27).
**LKM** — Loadable Kernel Module; add/remove drivers without rebuild (Ch 11).
**live migration** — move a running VM between hosts with no downtime (Ch 24).
**LVM** — Logical Volume Manager; pools (volume groups) → logical volumes; online resize/snapshot (Ch 20).
**MAC address** — 6-byte hardware link-layer address (Ch 13).
**MBR** — Master Boot Record; legacy BIOS partition/boot scheme (Ch 2).
**MFA** — Multifactor Authentication; something you know + have (Ch 27).
**MIB / OID** — SNMP schema / dotted object identifier (Ch 28).
**MTA / MSA / MUA / MDA** — mail transport / submission / user / delivery agent (Ch 18).
**MTU** — Maximum Transfer Unit; Ethernet payload 1500B (jumbo ~9000) (Ch 13, 14).
**namespace (Linux)** — isolates a process's view of FS/PIDs/network; container foundation (Ch 3, 25).
**NAT / PAT** — Network/Port Address Translation; private IPs behind one public IP (Ch 13).
**niceness** — CPU scheduling hint (−20..+19); only root lowers it (Ch 4).
**NOOP scheduler** — FIFO Linux I/O scheduler; best for SSDs (Ch 29).
**operation (CM)** — small idempotent action (task/state/resource/recipe) (Ch 23).
**PAM** — Pluggable Authentication Modules; auth framework (Ch 3, 17).
**paging** — moving memory pages between RAM and swap (Ch 29).
**paravirtualization** — modified guest cooperates with the hypervisor (Ch 24).
**PUE** — Power Usage Effectiveness; total ÷ IT power (good ≤1.4) (Ch 30).
**PXE** — Preboot eXecution Environment; netboot (Ch 6).
**RAID** — striping (0)/mirroring (1)/parity (5/6) across disks (Ch 20).
**RAID 5 write hole** — crash mid-write desyncs data/parity; ZFS RAID-Z immune (Ch 20).
**root squashing** — NFS maps remote UID 0 to `nobody` (Ch 21).
**RPCSEC_GSS** — strong (Kerberos) NFS security flavor (Ch 21).
**SAN** — Storage Area Network; serves raw blocks, not filesystems (Ch 21).
**SLAAC** — Stateless Address Autoconfiguration (IPv6) (Ch 13).
**SLA** — Service Level Agreement (Ch 31).
**SMART** — disk self-monitoring; 4 parameters highly predictive of failure (Ch 20).
**SMB / Samba** — Windows file-sharing protocol / its UNIX server (Ch 22).
**SNI** — Server Name Indication; sends TLS hostname so the server picks the cert (Ch 19).
**snowflake** — an un-reproducible hand-tuned system; CM's enemy (Ch 23).
**SOA record** — Start of Authority; DNS zone metadata + timers (serial!) (Ch 16).
**SPF** — Sender Policy Framework; DNS list of a domain's mail servers (Ch 18).
**stateful / stateless** — server tracks (NFSv4) vs forgets (NFSv3) client state (Ch 21).
**stolen cycles (`st`)** — VM CPU diverted by the hypervisor (Ch 29).
**sudo** — run a command as another user per `/etc/sudoers` (last-match-wins) (Ch 3).
**swappiness** — Linux RAM-vs-swap reclaim balance (default 60) (Ch 29).
**symbolic link** — named pointer to a path; can dangle/cross FS (Ch 5).
**systemd** — Linux PID-1 init: units, targets, `systemctl`, journald (Ch 2).
**TLS** — Transport Layer Security; encrypts between TCP and the app (Ch 19, 27).
**TRIM** — tells an SSD a block is free so it can pre-erase (Ch 20).
**TTL** — Time To Live; DNS cache lifetime (Ch 16).
**udev** — Linux user-space device-file manager (rules + sysfs) (Ch 11).
**UID / GID** — numeric user/group identity (root = 0; real users 1000+) (Ch 8).
**union filesystem** — overlay layers into one hierarchy; container images (Ch 25).
**unit (systemd)** — managed entity (service/socket/target/timer) defined by a unit file (Ch 2).
**UPS** — Uninterruptible Power Supply; battery bridge to generators (Ch 30).
**VLAN** — software-partitioned switch ports = isolated logical segment (Ch 14).
**volume (Docker)** — persistent writable dir outside the union filesystem (Ch 25).
**zone (DNS)** — a domain minus its subdomains; one SOA, master + slaves (Ch 16).
**ZFS** — CoW filesystem + volume manager + RAID-Z (Ch 20).
