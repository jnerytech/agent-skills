# Chapter 3: Access Control and Rootly Powers

## Core Idea
Access control = the *mechanical* rules the kernel and filesystem use to grant or deny operations (distinct from "security," Ch 27). The traditional UNIX model — owners, groups, and an all-powerful `root` (UID 0) — is simple, predictable, and still the default; modern systems layer on `sudo`, PAM, capabilities, namespaces, and MAC (SELinux/AppArmor) to patch its weaknesses.

## Frameworks Introduced
- **Standard UNIX access control rules**: decisions key on the acting user (or group membership); objects have owners; you own what you create; `root` can act as any owner; only `root` does certain sensitive ops. The kernel checks the **effective UID**; UID 0 = superuser.
- **`sudo` as the primary path to root**: run a single command as root (or another user) per `/etc/sudoers`, with per-user/per-host/per-command rules and full logging.
  - When to use: essentially always — replaces both direct root login and `su`.
  - How: edit with `visudo` (locks + syntax-checks); 90% of files are just `User_Alias ADMINS = alice,bob` + `ADMINS ALL = (ALL) ALL`.
- **Principle of least privilege**: grant access only when necessary — the design goal behind capabilities, MAC, and well-scoped sudoers.
- **Setuid/setgid execution**: a marked executable runs with the *file owner's* UID/GID (often root), promoting privilege for that one command (e.g. `passwd` editing `/etc/shadow`).

## Key Concepts
- **UID/GID**: numeric identities; names in `/etc/passwd` (UID) and `/etc/group` (GID) exist only for humans.
- **real / effective / saved UID**: effective = used for permission checks; saved = parking spot to re-enter privilege; real ≈ accounting (vestigial). Linux adds a filesystem UID (NFS detail).
- **PAM (Pluggable Authentication Modules)**: a *framework* answering "is this really user X?" — programs call PAM instead of hard-coding password checks. Enables biometrics, 2FA, network identity.
- **Kerberos**: a specific authentication *method* (trusted third-party server issues crypto credentials); PAM wraps it. Basis of Windows Active Directory auth.
- **Linux capabilities**: split root's powers into ~30 units (e.g. `CAP_NET_BIND_SERVICE` for ports <1024); inheritable, file-attached. In practice an *enabling* tech for AppArmor/Docker, rarely used alone.
- **Linux namespaces**: partition a process's view of files/ports/processes — preemptive access control; foundation of containers/Docker. Confinement is irreversible, so root-in-a-namespace is safe.
- **DAC vs MAC**: standard model is *discretionary* (owners set perms). *Mandatory* access control = admin/vendor policies that override discretionary perms (SELinux, AppArmor, TrustedBSD MAC).
- **RBAC**: assign permissions to *roles*, roles to users; roles can be hierarchical. Built into several MAC systems; no native Linux/FreeBSD RBAC.
- **LSM (Linux Security Modules)**: kernel API letting access-control systems load as modules (SELinux, AppArmor, Smack, TOMOYO, Yama). Effectively one active at a time.

## Mental Models
- **Treat root as a single point of failure.** Compromise = unlimited damage. Minimize its use (sudo), minimize setuid programs, and consider disabling its password entirely.
- **`sudo` precedence = last matching line wins**, matched on the full 4-tuple (user, host, target user, command). Put `NOPASSWD` exceptions *after* their general counterparts.
- **"Allow all commands except X" is doomed** — `cp /bin/sh /tmp/sh; sudo /tmp/sh` defeats a shell blacklist. Use it only as a *reminder*, not real control.
- **sudo's risk: a sudoer's account ≈ the root account.** The attack surface expands to every admin's personal account.

## Anti-patterns
- **Direct root login**: no record of *who* did *what*; disable everywhere but the console. Ubuntu locks root by default.
- **`NOPASSWD: ALL`** (e.g. for Ansible/cron): dangerous; at minimum restrict to specific commands, or use forwarded SSH-agent auth via `pam_ssh_agent_auth`.
- **`.` in `$PATH`** (especially root's): lets a planted fake command run. Also: type the full path `/bin/su` to avoid trojaned `su`.
- **Extra UID-0 accounts / renaming root**: breeds security holes and confusion.
- **SELinux when you don't need it**: notoriously hard to administer; authors judge it "capable of delivering more harm than benefit" outside strong-requirement environments (gov/finance/health). Red Hat/CentOS enable it by default; Ubuntu favors AppArmor.

## Code Examples
```sh
ls -l ~garth/todo     # -rw-r----- 1 garth staff ... -> owner garth, group staff
sudo -u operator /usr/sbin/dump 0u /dev/sda1   # run as a non-root target user
visudo                # safely edit /etc/sudoers (lock + validate)
visudo -c -f newsudoers           # validate a sudoers file before installing
sudo EDITOR=emacs vipw            # pass one env var through sudo's sanitized env
passwd -l root        # lock root (prepend ! to hash); sudo passwd -u root unlocks
mount -o nosuid ...   # disable setuid on untrusted / home-dir filesystems
```
```
# /etc/sudoers essentials
Host_Alias  CS = tigger, anchor, piper
Cmnd_Alias  DUMP = /sbin/dump, /sbin/restore
User_Alias  ADMINS = alice, bob, charles
ADMINS ALL = (ALL) ALL
herb   CS = /usr/sbin/tcpdump : PHYSICS = (operator) DUMP
%wheel ALL, !PHYSICS = NOPASSWD: WATCHDOG
Defaults env_keep += "SSH_AUTH_SOCK"
Defaults !requiretty      # commonly needs disabling for cron/remote sudo
```
- **What it demonstrates**: aliases + the per-line 4-tuple (users / hosts = (run-as) commands); full command paths prevent running look-alikes.

## Reference Tables
**Restricted (root-only) operations**: create device files · set system clock · raise resource limits & process priorities · set hostname · configure network interfaces · open ports <1024 · shut down the system.

**sudo log entry** records: command line, host, user, working directory, timestamp → forward via syslog to a secure central host.

## Worked Example
**Site-wide single sudoers file.** Because each line matches on host, one master `/etc/sudoers` serves an entire administrative domain. Benefits: one authoritative record of who-can-do-what-where; when an admin leaves, edit one file instead of hunting every host. Distribute via configuration management (Ch 23), or a cron "pull" script: `scp` the file from a central repo (scp checks the host key, preventing spoofing), validate with `visudo -c -f`, then install. Prefer enumerating *user accounts* over `%wheel` so the file is self-documenting; match cloud hosts via globbing on a security-classification naming scheme or by IP. Keep the file under file-integrity monitoring.

## Key Takeaways
1. The traditional model (owner/group/root, effective UID checks) is the default everywhere — master it before the extensions.
2. Standardize on `sudo` for root access: accountability via logging, fine-grained per-command grants, revocable without changing the root password.
3. `visudo` always; sudoers precedence is "last match wins" on the 4-tuple; never trust command blacklists.
4. Minimize setuid programs and root's footprint; consider locking the root password (keep it on *physical* machines for rescue).
5. PAM = auth *framework*, Kerberos = auth *method*; both answer "who are you," not "what may you do."
6. Capabilities/namespaces are the plumbing under containers; MAC (SELinux/AppArmor) adds admin policies that override discretionary perms — deploy only when you'll maintain them.

## Connects To
- **Ch 8**: user management (`/etc/passwd`, `/etc/shadow`, pseudo-users).
- **Ch 5**: filesystem permissions & ACLs (the bit-level detail).
- **Ch 17**: single sign-on (PAM, Kerberos, LDAP groups).
- **Ch 25**: containers (namespaces + capabilities in practice).
- **Ch 27**: security (the policy-level companion to this mechanical chapter).
