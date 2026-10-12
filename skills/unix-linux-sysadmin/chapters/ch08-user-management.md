# Chapter 8: User Management

## Core Idea
A user is fundamentally just a **32-bit UID**; everything else maps to/from it. Account hygiene is a security front line (stale accounts and weak passwords are prime targets). Know the flat files (`/etc/passwd`, `/etc/shadow` or FreeBSD `/etc/master.passwd`, `/etc/group`) that everything ultimately emulates — then use the higher-level tools (`useradd`/`adduser`/`usermod`, `pw`) and centralize with LDAP at scale.

## Frameworks Introduced
- **The `/etc/passwd` 7 fields**: login name : password placeholder (`x`/`*`) : UID : default GID : GECOS (full name/office/phone) : home directory : login shell.
- **The `/etc/shadow` 9 fields** (Linux, root-only): login : encrypted password : last-change : min-days : max-days : warn-days : inactive-days : expiration : reserved. Dates are *days* since Jan 1 1970 (not seconds).
- **The manual add-user procedure** (what the tools automate): edit passwd+shadow (or master.passwd) → add to `/etc/group` → set password → create+chown+chmod home → copy startup files from `/etc/skel` → configure roles → sign policy agreement → verify → document.
- **Personal groups**: each user gets a private group named after them (GID = UID), so default file sharing is restrictive; create explicit shared groups for collaboration.

## Key Concepts
- **UID rules**: root = 0; pseudo-users (bin/daemon) get low UIDs + `/bin/false` shell; real users start at **1000+**. Never recycle UIDs (backups identify by UID); keep UIDs unique org-wide (NFS security depends on it).
- **GID**: GID 0 = root/wheel/system. Default GID matters only for *new file creation* (files get your effective group). setgid bit (02000) on a dir or `grpid` mount → new files inherit the dir's group.
- **Password hashing**: default SHA-512 (`$6$`); `$1$`=MD5, `$2$`=Blowfish, `$5$`=SHA-256. Salted so identical passwords → different hashes. Hash length fixed regardless of password length.
- **Placeholder `*`/`x`** in the password field disables login until a real password is set (`passwd`).
- **GECOS field**: comma-separated full name/office/phone; users edit via `chfn`.
- **Startup files**: dot-`rc` files copied from `/etc/skel`; system-wide ones (`/etc/profile`, `/etc/profile.d/*`) run before the user's own.
- **FreeBSD specifics**: real file is `/etc/master.passwd` (3 extra fields: login class, password-change time, expiration); `/etc/login.conf` sets per-class resource limits/env (compile with `cap_mkdb`); manage with the `pw` command.

## Mental Models
- **The flat-file model is the lingua franca.** LDAP/AD and `nsswitch.conf` layer over `getpwnam()`/`getpwuid()` — login does a `getpwnam()` and validates the password regardless of the actual backing store. Learn the files to understand everything above them.
- **Prefer length over complexity** for passwords — 12 chars minimum for future-proofing (longer than any default). Defer to org-wide standards if they exist.
- **Consistency is the primary goal; UID uniqueness is second.** Same login name + same UID on every machine the user touches; central directory server enforces it best.

## Anti-patterns
- **Hand-editing passwd/group without `vipw`/`vigr`**: error-prone and unlocked. `vipw` locks the file, invokes `$EDITOR`, and on FreeBSD regenerates the derived `passwd` + hashed dbs (`pwd_mkdb`); `vipw -s` edits shadow; `vigr` edits group.
- **`chown -R newuser ~newuser/.*`**: the `.*` glob matches `..` → you chown the parent dir and other users' homes. Use `chown -R newuser:newgroup ~newuser`.
- **Auto-create accounts with no initial password (set on first login)**: "a giant security hole" — anyone who guesses the login name hijacks the account first. Set a password (or a short-lived transitional/random one).
- **Recycling UIDs / inconsistent UIDs across machines**: backup confusion and NFS security holes.
- **Distributing passwords by email**: insecure; prefer in-person/phone/SMS, and expire unused passwords in a couple days.
- **Releasing an account before the policy agreement is signed**: get the signature while you still have leverage (before account creation).

## Code Examples
```sh
# Linux
useradd hilbert              # create (account DISABLED until password set)
useradd -D -s /bin/bash      # set default shell (writes /etc/default/useradd)
passwd hilbert               # set initial password
usermod -e 2026-12-31 user   # set account expiration (yyyy-mm-dd)
userdel user ; groupadd/groupmod/groupdel
vipw ; vipw -s ; vigr        # safely edit passwd / shadow / group
pwconv                       # reconcile shadow with passwd
chown -R newuser:newgroup ~newuser   # fix home ownership (NOT ~newuser/.*)

# FreeBSD
pw groupmod staff -m dan ; pw groupshow staff   # add to group, verify
pw usermod raphael -w random                    # generate+set random password
cap_mkdb /etc/login.conf                         # compile login.conf after edits
```
```
# /etc/passwd entry
whitney:x:1003:1003:Whitney Sather,AMATH 3-27,x7919,:/home/staff/whitney:/bin/sh
# /etc/shadow entry (millert, changed 2017-06-19, must change within 180d, 14d warning)
millert:$6$iTEFbMTM$CXmx...YwOl/:17336:0:180:14:::
# /etc/group entry: name : passwd : GID : members(comma, no spaces)
staff:*:20:dan,ben,trent
```

## Reference Tables
**Per-distro tools/config**: All Linux → `useradd`/`usermod`/`userdel`, config in `/etc/login.defs` (hand-edit: aging, hash algo, UID/GID ranges) + `/etc/default/useradd` (set via `useradd -D`). Debian/Ubuntu → friendlier `adduser`/`deluser` (`/etc/adduser.conf`). FreeBSD → `adduser`/`rmuser`/`pw` (`/etc/login.conf`).

**Password-quality defaults**: RHEL/CentOS 8+ chars, complexity (`/etc/security/pwquality.conf`, `/etc/pam.d/system-auth`) · Debian/Ubuntu 6+ chars (`/etc/pam.d/common-password`) · FreeBSD none (`/etc/login.conf`).

**Common startup files**: `.profile` (sh), `.bashrc`/`.bash_profile` (bash), `.login`/`.cshrc` (csh), `.vimrc`, `.gitconfig`. Samples in `/etc/skel`. Recommended new-user `umask`: 077 / 027 / 022 by site friendliness.

## Worked Example
**Add user "whitney" by hand, safely.** (1) `vipw` → add `whitney:*:1003:1003::/home/staff/whitney:/bin/sh` — note the `*` so the account can't be used yet; on Linux it reminds you to `vipw -s` for shadow. (2) `vigr` → create her personal group and add her to any shared groups; skip `vigr -s` (gshadow) unless setting a group password. (3) `passwd whitney` to set a real password (or a short-lived transitional one). (4) `mkdir /home/staff/whitney`, copy `/etc/skel/.*` startup files in, then `chown -R whitney:whitney ~whitney` (never `~whitney/.*`), set umask in the startup files. (5) Have her sign the policy agreement *before* release, verify by logging in and running `pwd`/`ls -la`, and record her contact info. The placeholder `*` is what keeps the half-built account from being hijacked between steps 1 and 3.

## Key Takeaways
1. A user is a UID; the flat files (`passwd`/`shadow`/`group`, FreeBSD `master.passwd`/`login.conf`) are the model everything else emulates.
2. Real users start at UID/GID 1000+; never recycle; keep unique and consistent org-wide.
3. Always edit with `vipw`/`vigr` (locking + derived-file regeneration); never the raw files.
4. Default GID/personal groups exist to keep file sharing *restrictive by default*; create explicit groups to share.
5. Set an initial password (placeholder `*`/`x` disables until then); prefer length over complexity; expire unused passwords fast.
6. Use `useradd`/`adduser`/`pw` daily; customize via `/etc/login.defs`+`/etc/default/useradd` (Linux) or `/etc/login.conf` (FreeBSD); centralize with LDAP at scale.

## Connects To
- **Ch 3**: setuid/setgid, sudo (group → sudoers), RBAC.
- **Ch 5**: home-directory permissions, umask, setgid directories.
- **Ch 17**: PAM, LDAP, Active Directory, `nsswitch.conf` — centralized account management.
- **Ch 27**: password vaults, password aging, cracking.
- **Ch 31**: user policy agreements; SOX/HIPAA/GLBA compliance.
