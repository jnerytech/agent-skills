---
name: unix-linux-sysadmin
description: "Knowledge base from \"UNIX and Linux System Administration Handbook, 5th ed (2017)\" by Nemeth, Snyder, Hein, Whaley & Mackin. Use when applying the authors' frameworks for system administration — boot/systemd, access control, filesystems, networking (TCP/IP, DNS, routing), storage/RAID, NFS/SMB, config management, virtualization, containers, CI/CD, security, monitoring, performance, data centers, and IT methodology — studying the book, or referencing its concepts."
---

<!-- argument-hint: [topic, framework name, or chapter number, e.g. "systemd", "RAID", "ch16"] -->

# UNIX and Linux System Administration Handbook (5th Edition)
**Authors**: Evi Nemeth, Garth Snyder, Trent R. Hein, Ben Whaley, Dan Mackin | **Pages**: ~1226 | **Chapters**: 31 | **Generated**: 2026-06-26

## How to Use This Skill

- **Without arguments** — load the core frameworks below for reference.
- **With a topic** — ask about `systemd`, `RAID`, `sudo`, `DNS`, `containers`, etc.; I find and read the relevant chapter.
- **With a chapter** — ask for `ch20`; I load that specific chapter.
- **Browse** — ask "what chapters do you have?" to see the full index.

When you ask about a topic not in the Core Frameworks below, I read the relevant chapter file before answering.

---

## Core Frameworks & Mental Models

**The role.** Enterprise needs drive IT activities, not the reverse. The sysadmin's job is the *essential duties* (Ch 1): access control, hardware, automation, backups, software, monitoring, troubleshooting, documentation, security, performance, policy, vendors, fire-fighting. Treat every install as attack surface; minimize it.

**systemd (Ch 2).** Linux PID 1. Everything is a *unit* (service/socket/target/timer) defined by an `.ini`-style unit file. Stock units in `/usr/lib/systemd/system` (never edit); overrides in `/etc/systemd/system` (wins). `systemctl enable --now`, `status -l`, `isolate target`. *Which* units activate (`Wants`/`Requires`) is separate from *ordering* (`Before`/`After`) — systemd parallelizes by default.

**Access control (Ch 3).** Traditional model: owner/group/root, kernel checks the **effective UID** (0 = root). Use **sudo** as the path to root (last-matching-line wins on the 4-tuple; never blacklist commands). PAM = auth *framework*, Kerberos = auth *method*. Capabilities/namespaces underlie containers; MAC (SELinux/AppArmor) overrides discretionary perms.

**Processes (Ch 4).** fork+exec; PID 1 reaps orphans. Signals: HUP=reload, TERM=graceful (default), KILL=forceful last resort, STOP/CONT=suspend. `ps aux`/`top`/`pgrep`. `D`-state = unkillable (NFS hard mount down). cron for scheduling (mind the non-login-shell environment).

**Filesystem (Ch 5).** One tree from `/`; "everything is a file." 7 file types (read off `ls -l`). Hard link = same inode (same-FS, counted); symlink = named pointer. Deleting needs perm on the *directory*. 12 mode bits = 9 perms + setuid/setgid/sticky; execute = "search" on dirs. `umask` removes default perms.

**Software (Ch 6).** Two-layer packaging: low-level (`rpm`/`dpkg`, one file) + high-level (`yum`/`apt`, repos + dependencies). `apt update`=refresh cache, `apt upgrade`=install; `yum update`=upgrade everything. PXE + kickstart/preseed for unattended installs. Never `rpm -U --force`.

**Scripting (Ch 7).** Master one shell (bash), editor (vim), language (Python). Pipes/redirection/filters compose; build pipelines interactively, preview, then run. `sh` for glue ≤50 lines; Python beyond. Regex is the universal pattern language.

**Networking (Ch 13–16).** TCP/IP is layered + encapsulated; IP addresses identify *interfaces*. Master subnetting/CIDR (usable hosts = `2^(32−N)−2`). NAT + RFC1918 + CIDR deferred IPv4 exhaustion. Routing = next-hop, longest-match; static default route reaches anywhere — dynamic protocols (OSPF/BGP) only for complex/adaptive topologies. DNS = delegated/cached hierarchy; **always bump the SOA serial**; `dig +trace` to debug. SSO = LDAP/AD identity + Kerberos auth, glued by sssd→nsswitch→PAM.

**Storage (Ch 20–22).** Stack: device → partition → RAID → LVM → filesystem. **RAID is not a backup.** Know RAID levels + the RAID 5 write hole (ZFS RAID-Z immune). LVM = online resize/snapshots (enlarge volume-first, shrink FS-first). Reference disks by LABEL/UUID. NFSv4 + Kerberos (retire v3, `hard,intr,bg`); SMB/Samba for cross-platform.

**Modern infra (Ch 23–26).** Config management captures desired state as code, killing the snowflake model — never hand-edit a managed host. Virtualization (hypervisor, VMs) vs containers (shared kernel, ephemeral, image+CoW layers, foreground process, log to STDOUT). CI/CD: build once → test in layers → deploy (blue/green/canary); a broken pipeline is the #1 priority.

**Operations (Ch 27–31).** Security = CIA triad + 3 rules (least privilege, defense in depth, minimize attack surface); humans are the weakest link; patch promptly; MFA for all privileged access. Monitor everything before it goes live (data → evaluate → react); all monitoring data is time-series. Performance: four resources (CPU/memory/storage I/O/network I/O) — CPU is usually *least* important, disk/memory dominate. **DevOps = CLAMS** (Culture, Lean, Automation, Measurement, Sharing): merge Dev+Ops to drive change.

---

## Chapter Index

| # | Title | Key Frameworks |
|---|-------|----------------|
| [ch01](chapters/ch01-where-to-start.md) | Where to Start | essential duties, distro choice, attack surface |
| [ch02](chapters/ch02-booting-and-systemd.md) | Booting & systemd | boot stages, units, targets, GRUB |
| [ch03](chapters/ch03-access-control-rootly-powers.md) | Access Control | sudo, PAM, capabilities, MAC, least privilege |
| [ch04](chapters/ch04-process-control.md) | Process Control | fork/exec, signals, ps/top, nice, cron |
| [ch05](chapters/ch05-the-filesystem.md) | The Filesystem | 7 file types, links, mode bits, umask |
| [ch06](chapters/ch06-software-installation.md) | Software Installation | rpm/dpkg, yum/apt, PXE, kickstart/preseed |
| [ch07](chapters/ch07-scripting-and-the-shell.md) | Scripting & the Shell | pipes/filters, sh, regex, Python, Ruby |
| [ch08](chapters/ch08-user-management.md) | User Management | passwd/shadow/group, UID/GID, useradd |
| [ch09](chapters/ch09-cloud-computing.md) | Cloud Computing | cattle-not-pets, IaaS/PaaS/SaaS, regions/zones |
| [ch10](chapters/ch10-logging.md) | Logging | systemd journal, rsyslog, facility/severity |
| [ch11](chapters/ch11-drivers-and-the-kernel.md) | Drivers & the Kernel | device files, udev/devfs, sysctl, LKMs |
| [ch12](chapters/ch12-printing.md) | Printing | CUPS, IPP, filter pipeline, queue control |
| [ch13](chapters/ch13-tcp-ip-networking.md) | TCP/IP Networking | layering, subnetting/CIDR, NAT, IPv6, ip/sysctl |
| [ch14](chapters/ch14-physical-networking.md) | Physical Networking | Ethernet, switches, VLANs, Wi-Fi/WPA2, fiber |
| [ch15](chapters/ch15-ip-routing.md) | IP Routing | next-hop, distance-vector vs link-state, OSPF/BGP |
| [ch16](chapters/ch16-dns.md) | DNS | zones, SOA/NS/A/PTR, delegation, caching, dig |
| [ch17](chapters/ch17-single-sign-on.md) | Single Sign-On | LDAP, Kerberos, sssd, nsswitch, PAM stacks |
| [ch18](chapters/ch18-electronic-mail.md) | Electronic Mail | MTA/MSA/MUA, SMTP, headers, SPF/DKIM, aliases |
| [ch19](chapters/ch19-web-hosting.md) | Web Hosting | HTTP, virtual hosts/SNI, load balancers, caches/CDN |
| [ch20](chapters/ch20-storage.md) | Storage | stack, RAID levels/write hole, LVM, SMART, SSD |
| [ch21](chapters/ch21-network-file-system.md) | NFS | stateful/stateless, exports, mounts, idmap |
| [ch22](chapters/ch22-smb.md) | SMB | Samba, shares, AD auth, setgid group shares |
| [ch23](chapters/ch23-configuration-management.md) | Configuration Management | declarative/idempotent, Ansible/Salt/Puppet/Chef |
| [ch24](chapters/ch24-virtualization.md) | Virtualization | hypervisors, Xen/KVM, live migration, Packer |
| [ch25](chapters/ch25-containers.md) | Containers | namespaces/cgroups, images/union FS, Docker |
| [ch26](chapters/ch26-continuous-integration-delivery.md) | CI/CD | pipeline, test pyramid, blue/green/canary, Jenkins |
| [ch27](chapters/ch27-security.md) | Security | CIA triad, 3 rules, MFA, nmap/OSSEC, rootkits |
| [ch28](chapters/ch28-monitoring.md) | Monitoring | pipeline, time-series, StatsD/collectd, dashboards |
| [ch29](chapters/ch29-performance-analysis.md) | Performance Analysis | four resources, vmstat/iostat/sar, stolen cycles |
| [ch30](chapters/ch30-data-center-basics.md) | Data Center Basics | power/UPS/generators, hot/cold aisle, PUE, tiers |
| [ch31](chapters/ch31-methodology-policy-politics.md) | Methodology/Policy/Politics | DevOps/CLAMS, ticketing, SLAs, disaster recovery |

## Topic Index

- **Active Directory** → ch17, ch22
- **Ansible / Salt / Puppet / Chef** → ch23
- **backups** → ch20, ch27, ch31
- **boot loader / GRUB** → ch02
- **CIDR / subnetting** → ch13
- **cloud** → ch09, ch19, ch24
- **containers / Docker** → ch25
- **cron** → ch04
- **DevOps / CLAMS** → ch31, ch23, ch26
- **DNS / dig / BIND** → ch16, ch13
- **Ethernet / switches / VLAN** → ch14
- **firewall / packet filter** → ch27, ch13
- **Kerberos** → ch17, ch03, ch21
- **LDAP / sssd** → ch17
- **load balancer** → ch19, ch29
- **LVM** → ch20
- **mail / SMTP / SPF** → ch18
- **MFA / passwords** → ch27, ch08
- **monitoring / Prometheus / Grafana** → ch28
- **NFS** → ch21
- **nmap / OSSEC / pen-testing** → ch27
- **PAM** → ch03, ch17
- **performance / vmstat / sar** → ch29
- **PXE / kickstart / preseed** → ch06
- **RAID** → ch20
- **regex** → ch07
- **routing / OSPF / BGP** → ch15
- **rsyslog / journal** → ch10
- **Samba / SMB** → ch22
- **SELinux / MAC** → ch03
- **signals** → ch04
- **SSH hardening** → ch27
- **sudo** → ch03
- **systemd / units / targets** → ch02
- **TLS / HTTPS / SNI** → ch19
- **udev / device files** → ch11
- **user management / UID** → ch08
- **virtualization / Xen / KVM** → ch24
- **ZFS / Btrfs** → ch20

## Supporting Files

- [glossary.md](glossary.md) — key terms with definitions (chapter-referenced)
- [patterns.md](patterns.md) — concrete techniques & procedures (when/how/trade-offs)
- [cheatsheet.md](cheatsheet.md) — decision rules, thresholds, tells & smells, quick picks

---

## Scope & Limits

This skill covers the book's content (the 2017 5th edition, four primary example systems: Debian/Ubuntu, RHEL/CentOS, FreeBSD). Specific software versions and cloud-provider details have evolved since publication — verify current syntax against live docs. For hands-on work in your codebase, combine with project-specific tools.
