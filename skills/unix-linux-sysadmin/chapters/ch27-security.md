# Chapter 27: Security

## Core Idea
Security is a **process, not a product**, framed by the **CIA triad** — Confidentiality (privacy/access control/encryption), Integrity (data is authentic/unaltered, trusted sources), Availability (accessible when needed). Defend with three rules of thumb: **least privilege**, **defense in depth** (layers — don't be a Tootsie Pop: hard shell, soft center), and **minimize attack surface**. The highest-value chore is keeping systems patched; the weakest link is almost always humans.

## Frameworks Introduced
- **CIA triad**: every control serves confidentiality, integrity, or availability — keep all three in mind designing/maintaining systems.
- **The three security rules of thumb**: least privilege (minimum access for each entity — firewall rules, file perms, user perms), defense in depth (layered controls, never rely on one), minimize attack surface (fewer services/packages/exposed systems = fewer vulnerabilities).
- **How security is compromised** (the threat taxonomy): social engineering/phishing (the weakest link — humans), software vulnerabilities (buffer overflows / input-validation bugs), DDoS (botnets flood you), insider abuse (trusted agents — hardest to detect), configuration errors (the easiest to find and fix).
- **Defense layers**: patch promptly + disable unnecessary services + remote/central logging + tested off-site backups + packet filtering (network + host) + MFA + intrusion detection + vigilance.

## Key Concepts
- **Least-privilege for apps**: run processes as unprivileged users (not root) so a vulnerability does limited damage; reinforce with MAC (SELinux) and capability-limited containers.
- **Passwords**: length beats complexity — use a long, memorable, *unique* passphrase ("six guests drank Evi's poisoned wine"); never reuse a password across administrative boundaries (one breach compromises all reuses). Verify every account has a password; pseudo-users get `*`/`!` in shadow.
- **MFA (multifactor authentication)**: something you know + something you have — an "absolute minimum" for *any* Internet-facing privileged access (VPN, SSH, admin web UIs). Google Authenticator, Duo.
- **Password aging caveat**: forced changes lead to weak/incremented passwords; focus on *quality* over frequency. Change root passwords every ~6 months, when staff leave, or on suspected compromise.
- **Remote/central logging**: forward syslog to a secure aggregator so attackers can't erase their tracks on compromised hosts.
- **Root kits**: hide attacker activity (from hacked `ls`/`ps` to kernel modules); detect with OSSEC, AIDE, chkrootkit — but a compromised system is best wiped and restored, not cleaned.
- **Packet filtering**: firewall between systems and the Internet, passing only wanted services; double up with host filters (`iptables`/`ufw`, `ipfw`); cloud = security groups (be granular, add outbound rules too).

## Mental Models
- **Humans are the weakest link.** No technology stops social engineering — train users, communicate regularly, and tell them admins will *never* ask for their password (report anyone who does). Test your own resistance only with explicit written management approval.
- **Configuration errors are the easiest wins — for both sides.** Hackers exploit convenient defaults (no passwords, lax firewall rules, unprotected databases). The single most important hardening step is "don't put out a welcome mat" — scan yourself before they do.
- **Patch promptly even though patches carry risk.** Most exploits target *old, widely-known* vulnerabilities — statistically you're far safer regularly updated. Do it methodically (schedule, change plan with rollback, accurate inventory, security mailing lists).
- **A compromised system, not its rootkit, is the problem.** Time spent cleaning advanced rootkits is better spent saving data and wiping — the best ones subvert removal tools.
- **Security is only as strong as the weakest link.** A hardened network with an app that leaks data without a password = battle won, war lost. Pen-test apps (OWASP methodology, third party).

## Anti-patterns
- **Installing back doors "for your own use"**: too easily misused/exploited by others — never.
- **Allowing remote root login**: set `PermitRootLogin No` in `sshd_config`; with sudo you rarely need root login at all. Watch for extra UID-0 entries planted in `/etc/passwd` (who/w show utmp names, not UIDs).
- **Group/shared logins** (`guest`, `demo`): hacker homesteading, illegal under HIPAA — prohibit; education is the only real enforcement.
- **Reusing passwords across boundaries**: one breach cascades.
- **Single-factor auth for admin interfaces**: MFA is the minimum.
- **Running unnecessary network daemons**: each is attack surface — disable and de-boot them.
- **Scanning networks you don't own**: get permission — admins (rightly) resent unsolicited nmap, and it's suspicious without a mandate.

## Code Examples
```sh
# Find what's listening / who owns a port (disable unneeded services)
netstat -an | grep LISTEN          # (Linux moving to ss)
sudo lsof -i:22                    # which process holds the port

# Port-scan yourself the way an attacker sees you
nmap -sT host                      # TCP connect scan
sudo nmap -sV -O host              # service versions + OS fingerprint
# STATE: open / closed / filtered (blocked by firewall)

# Password hygiene
sudo ./john /etc/shadow            # John the Ripper — crack to find weak passwords
sudo chage -m 2 -M 90 -E 2017-07-31 -W 14 ben   # Linux password aging
sudo pw user mod trent -p 2017-09-25 -e 90      # FreeBSD aging

# Harden SSH: /etc/ssh/sshd_config
#   PermitRootLogin No
```
```xml
<!-- OSSEC: ignore a noisy file in integrity checks (/var/ossec/etc/ossec.conf) -->
<syscheck>
  <ignore>/var/log/customapp.log</ignore>
</syscheck>
```

## Reference Tables
**Security power tools**: `nmap` (port scanner / OS+service fingerprint), Nessus (vulnerability scanner, 31k+ plugins), Metasploit (penetration testing / exploit framework), Lynis (on-box hardening audit), John the Ripper (password cracker), Bro (programmable NIDS — monitors *flows*, who-talks-to-whom), Snort (signature NIDS — simpler "starter"), OSSEC (host IDS — rootkit/integrity/log analysis), Fail2Ban (bans IPs after failed logins).

**Patching process**: regular schedule (monthly + critical ASAP) · change plan with rollback + testing · subscribe to vendor security lists/Bugtraq · accurate app/OS inventory.

**Threat categories**: social engineering/phishing · software vulnerabilities (buffer overflow / input validation) · DDoS (botnets) · insider abuse · config errors.

## Worked Example
**Audit a host the way an attacker would, then harden it.** Run `nmap -sT host`: it reveals `25/smtp`, `80/http`, `111/rpcbind`, `139/netbios-ssn`, `445/microsoft-ds`, `3306/mysql` open. Several of these (portmap/rpcbind, an exposed SMTP server, a public MySQL) are "likely unused and historically associated with security problems" — exactly what an attacker probes next. To harden: (1) on the host, `netstat -an | grep LISTEN` + `lsof -i:<port>` + `ps` to identify each listening daemon; (2) stop and de-boot the unneeded ones (shrink attack surface); (3) put a packet filter in front so only intended ports (say 25, 80) are reachable — re-scan and confirm the others show `filtered`. Layer on: `PermitRootLogin No` + MFA for SSH, central syslog so logs can't be erased, OSSEC for file-integrity/rootkit alerts, Fail2Ban to ban brute-forcers, and run `john /etc/shadow` (with management approval) to force-fix weak passwords. The lesson: the secure server's scan showed only the two ports it *intends* to expose — everything else firewalled.

## Key Takeaways
1. Security is a process governed by CIA (confidentiality/integrity/availability) and three rules: least privilege, defense in depth, minimize attack surface.
2. Humans (social engineering/phishing) are the weakest link — train them; config errors are the easiest holes — scan yourself before attackers do.
3. Patch promptly and methodically (most exploits hit old known bugs); disable unnecessary services; centralize logs; keep tested off-site backups.
4. Passwords: long unique passphrases over forced-rotation complexity; MFA is mandatory for all Internet-facing privileged access; no shared/group logins; no remote root.
5. Run apps with least privilege (unprivileged users, MAC, capability-limited containers) to contain vulnerabilities.
6. Use the toolkit — nmap/Nessus/Lynis to find holes, Snort/Bro/OSSEC/Fail2Ban to detect and respond — and wipe-and-restore compromised systems rather than clean them.

## Connects To
- **Ch 3**: access control, least privilege, sudo, SELinux/capabilities.
- **Ch 8**: password files, account hygiene, password aging (`chage`/`pw`).
- **Ch 10**: logging (central/remote log aggregation, tamper-evidence).
- **Ch 13/14**: packet filtering, firewalls, security groups, network IDS.
- **Ch 22.x (SSH/TLS/firewalls)**: the chapter continues into cryptography, SSH, TLS, firewalls, and VPNs (covered as their own topics).
