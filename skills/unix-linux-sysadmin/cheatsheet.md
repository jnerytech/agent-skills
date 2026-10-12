# Cheatsheet — Sysadmin Decision Rules & Defaults

The author's judgment, distilled to decisions. Keep beside you while working.

## Decision rules (when X, do Y, because Z)
- **When patching the kernel/OS** → do it promptly and methodically, *because* most exploits target old, widely-known bugs (you're statistically safer updated). Security patches = immediate; routine = monthly.
- **When you need a newer kernel** → install a distro built around it, *not* shoehorn it in, *because* distros avoid kernels for subtle reasons you can't see.
- **When granting root access** → use `sudo` (not su/root login), *because* it logs who-did-what and revokes without changing the root password.
- **When a sudoers line could match multiple ways** → remember **last matching line wins** (4-tuple: user/host/runas/command); put `NOPASSWD` exceptions *after* general rules.
- **When choosing password strategy** → length over complexity (12+ char passphrase, unique per boundary), *because* length scales exponentially and reuse cascades one breach into many.
- **When exposing admin access to the Internet** → require MFA (VPN/SSH/admin UIs), *because* single-factor is unacceptable for privileged access.
- **When mounting NFS** → `hard,intr,bg`, *because* `soft` risks data loss; never serve critical binaries over NFS (a down server hangs every process).
- **When using NFS at all** → use v4 + Kerberos, retire v3, *because* AUTH_SYS is trivially forged.
- **When deploying a daemon in a container** → run it in the foreground, *because* the container dies when PID 1 exits.
- **When you find a resource-hog process** → usually do nothing (renice/ionice/ulimit or reschedule), *because* heavy work is often legitimate; killing destroys evidence.
- **When a build/pipeline breaks** → fixing it is the #1 priority (blame-free), *because* nothing else ships until it's green.
- **When the same artifact must reach prod** → build once, deploy often, *because* only testing *that exact* artifact proves it's prod-ready.
- **When a host is under config management** → never edit it by hand, *because* it instantly becomes an un-reproducible snowflake.
- **When editing a DNS zone** → bump the SOA serial, *because* slaves only pull on a higher serial.
- **When a disk reports a block error in logs** → pull mechanical disks (data already lost); an isolated SSD bad block is OK to reformat-and-reuse.
- **When mirroring data across data centers** → still keep off-line backups, *because* both DCs can be lost (ransomware/hackers).

## Thresholds & defaults
| Thing | Value |
|---|---|
| Real-user UID/GID start | 1000+ |
| Future-proof password length | 12+ chars |
| CPU-bound process | >90% of allocated CPU |
| CPU split (general server) | ~50% user / ~50% sys, idle > 0 |
| Load average (CPU-bound) | < number of cores |
| `umask` defaults | 022 (lenient) / 027 / 077 (strict) |
| Privileged ports | < 1024 (root to bind) |
| Default ports | SSH 22, SMTP 25, DNS 53, HTTP 80/443, MSA 587, NFS 2049, LDAP 389, CUPS 631, Docker TLS 2376 |
| NFS timeout alarm | >3% RPC timeouts = problem |
| Ethernet MTU / jumbo | 1500 / ~9000 |
| Non-overlapping 2.4GHz Wi-Fi channels | 1, 6, 11 |
| RAID 5 min disks / efficiency | 3 / ≥67% |
| Data-center temp (ASHRAE) | 18–27°C, humidity 8–60% |
| Good PUE | ≤1.4 (Google ~1.12) |
| On-site generator fuel | ≥72h |
| Standby-power test interval | ≤6 months |
| Linux swappiness default | 60 (if tempted to tune, buy RAM) |
| Mail loop limit | ~25 hops |
| Container base image | smallest that works (Alpine ~5MB, Ubuntu ~188MB) |

## Tells & smells (recognize the situation)
- **Process in `D` (uninterruptible sleep), unkillable** → NFS server down on a `hard` mount; fix cause or reboot.
- **Zombie/`<defunct>` processes** → negligent parent; check PPID.
- **High large-packet loss on Ethernet** → failed/one-sided autonegotiation.
- **`df` says full but `du` doesn't add up** → unlinked-but-open file; `lsof`/`fuser`.
- **Config-management changes silently not applying** → someone `chattr +i`'d a file (or hand-edited).
- **DNS changes not propagating** → forgot to bump the SOA serial.
- **VM slow but "under quota"** → stolen cycles (`st` in top); restart instance to re-place.
- **Reach host by IP but not by name** → DNS is the culprit.
- **Mysterious local slowness, no runaway** → slow remote server (dead NFS, 2s DNS lookup in `gethostent`).
- **Nonzero SMART scan-error/reallocation/probation count** → disk failure likely within 60 days.
- **Constant page-outs (`so`)** → inadequate RAM; buy more (don't just tweak swappiness).
- **A "vendor" appears to fix the A/C unannounced** → social-engineering attempt; turn away if unverified.

## "Which one?" quick picks
- **CM system**: most sites → Ansible (agentless) or Salt (fast); inherited → Puppet; enterprise scale only → Chef.
- **MTA**: Postfix (simple/secure) > Exim (powerful/complex) > sendmail (legacy).
- **Web server**: NGINX (production) / H2O (HTTP/2) / Apache (reference).
- **Hypervisor**: KVM or Xen (Linux prod), ESXi (enterprise), VirtualBox/Vagrant (dev), bhyve (avoid yet).
- **Linux I/O scheduler**: CFQ (mechanical default), NOOP (SSD/SAN), Deadline (low-latency).
- **Monitoring**: time-series (Prometheus/Graphite) + Grafana over first-gen threshold (Nagios/Icinga).
- **Scripting**: sh (glue ≤50 lines) → Python (default) / Ruby; avoid Perl (new), csh (scripting), PHP (sysadmin).
- **File sharing**: NFS (UNIX-only, fast) vs SMB/Samba (cross-platform, ubiquitous).
- **Container storage driver**: distro default (overlay); don't tune unless expert.
- **Password vault**: 1Password (teams) / KeePass (individual) / CyberArk-Secret Server (enterprise).

## The three security rules (apply everywhere)
1. **Least privilege** — minimum access per entity (firewall/file/user perms).
2. **Defense in depth** — layers; don't be a Tootsie Pop (hard shell, soft center).
3. **Minimize attack surface** — fewer services/packages/exposed systems.

## Golden rules to never forget
- Enterprise needs drive IT, not the reverse.
- Automate anything done >twice; never automate what you don't understand.
- RAID is not a backup; mirroring is not a backup.
- A prompt human reply to a ticket beats an instant fix.
- Verify a disk's identity before touching it; reference by LABEL/UUID.
