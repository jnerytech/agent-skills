# Chapter 17: Single Sign-On

## Core Idea
Single sign-on (SSO) = one set of credentials works on every system. It rests on two concepts — **identity** (who you are: username, UID, attributes) and **authentication** (proving you own that identity). The modern UNIX/Linux stack: an **LDAP** directory (or Active Directory) holds identities, **Kerberos** or LDAP authenticates, **sssd** aggregates both, **nsswitch.conf** routes identity lookups, and **PAM** plugs authentication into login.

## Frameworks Introduced
- **The four SSO elements**: (1) a centralized directory store (LDAP / Active Directory); (2) a management tool (phpLDAPadmin, Apache Directory Studio, AD Users & Computers); (3) an authentication mechanism (LDAP bind or Kerberos); (4) directory-aware C library lookups (`getpwent` et al.) configured via `nsswitch.conf`.
- **The login-integration chain**: directory → `sssd` (talks to LDAP/AD/Kerberos) → `nsswitch.conf` (lookup source = `sss`) → PAM (authenticates via `pam_sss`). NTP + DNS are critical when Kerberos is involved (tickets are timestamped).
- **PAM stack model**: each config line = `module-type control-flag module-path [args]`; modules of one type form a *stack* processed in order, combined per control flags into one result.
- **LDAP data model**: entries = property lists of named multi-valued attributes, organized by **distinguished name (dn)** into a hierarchy (most-significant component on the right, like DNS). Schema via `objectClass`.

## Key Concepts
- **LDAP** ("lightweight" but isn't): the standard directory protocol (TCP 389). Assumptions: small objects, widely replicated/cached, attribute-based, read-often/write-rarely, search-heavy. OpenLDAP (`slapd`) and 389 Directory Server are the open-source servers; Active Directory is the most common LDAP instantiation.
- **LDIF**: the text interchange format for LDAP entries (`dn:`, `objectClass:`, attributes) — easy plain-text conversion is key to LDAP's success.
- **Kerberos**: ticket-based authentication using symmetric-key crypto; a trusted KDC issues a ticket-granting ticket (TGT). Backbone of AD authentication. `kinit` gets a ticket, `klist` shows it, `kdestroy` invalidates it.
- **sssd (System Security Services Daemon)**: one-stop daemon for identity + authentication + account mapping; caches credentials offline (great for laptops); requires TLS for LDAP auth.
- **nsswitch.conf**: per-lookup source order, e.g. `passwd: files sss` (local files first, then sssd → directory). Test with `getent passwd`.
- **PAM module types**: `auth` (verify identity, grant groups), `account` (restrictions: time, ports, expiry), `session` (setup/teardown: mount home, set umask, log), `password` (change passwords).

## Mental Models
- **PAM control flags are subtle — most modules run regardless of siblings' results** (to hide which module failed from attackers): `required` (failure dooms the stack but keeps running), `requisite` (failure stops *immediately*), `sufficient` (success aborts the stack early — but can't override an earlier `required` failure), `optional` (matters only if it's the lone module).
- **Order matters in PAM and nsswitch.** A password-prompt module must precede the password-check module; local `files` should be consulted before the directory so you can still log in if the directory is down.
- **Kerberos lives and dies by the clock.** Tickets have limited validity; `krb5.conf` allows a small `clockskew` (e.g. 300s) as NTP insurance — but run NTP and ensure DNS/FQDN are correct.
- **Pick LDAP-auth or Kerberos-auth and commit.** "The road of life is paved with flat squirrels that couldn't decide."

## Anti-patterns
- **NIS for new deployments**: 1980s tech (`yp*` commands); migrate existing to LDAP, never start new.
- **`rsync`-ing `/etc/passwd`/`/etc/shadow` from a master**: quick hack but requires passwordless `sshd` and applying *all* changes (incl. password changes) on the master — significant security implications; use a directory or config management instead.
- **sssd LDAP auth over plaintext**: disallowed — requires LDAPS/TLS; set `tls_reqcert = demand` to validate the server cert.
- **Active Directory as an external/Internet-facing DNS or identity server**: internal use only.
- **slapd.conf world-readable**: contains the `rootpw` hash — must be root-owned, mode 600.
- **Forgetting NTP/DNS with Kerberos**: clock skew or name-mismatch breaks ticket validation.

## Code Examples
```sh
# Query LDAP (LDIF output) — great for AD debugging
ldapsearch -h atlantic.atrust.com -p 389 -x \
  -D "cn=trent,cn=users,dc=boulder,dc=atrust,dc=com" -W \
  -b "cn=users,dc=boulder,dc=atrust,dc=com" "cn=ned*"
# -x simple auth, -D bind DN, -W prompt password, -b baseDN, last arg = filter

# Join a Linux box to Active Directory (realmd does Kerberos+sssd in one step)
sudo realm join --user=trent ULSAH.COM
realm list

# Kerberos (FreeBSD / manual)
kinit administrator@ULSAH.COM     # request TGT
klist                             # show tickets + expiry
kdestroy                          # invalidate

# Verify identity sources after configuring nsswitch
getent passwd                     # lists accounts from files + sss
```
```ini
# /etc/sssd/sssd.conf  (Active Directory)
[sssd]
services = nss, pam
domains = ULSAH.COM
[domain/ULSAH.COM]
id_provider = ad
access_provider = ad

# /etc/nsswitch.conf
passwd: files sss
group:  files sss
shadow: files sss

# /etc/pam.d/login (excerpt) — module-type control-flag module
auth      sufficient  pam_unix2.so
auth      sufficient  pam_sss.so use_first_pass     # try directory if local fails
account   required    pam_unix2.so
password  requisite   pam_pwcheck.so cracklib       # strength check
session   required    pam_limits.so                 # apply ulimits
```

## Reference Tables
**LDAP attributes**: `dn` (distinguished name, unique path), `o` (organization), `ou` (org unit), `cn` (common name), `dc` (domain component — DNS-style), `uid`, `objectClass` (schema). `posixAccount`/`shadowAccount` object classes hold UNIX account data (RFC2307 maps passwd/group → LDAP).

**PAM control flags**: `required` (fail→stack fails, keep running), `requisite` (fail→stop now), `sufficient` (success→stop, unless earlier `required` failed), `optional`, `include`.

**Auth choices**: directory (OpenLDAP / 389-DS / Active Directory), auth method (LDAP bind vs Kerberos), aggregator (sssd), legacy (NIS — deprecated).

## Worked Example
**Read an `/etc/login` PAM auth stack.** `auth requisite pam_nologin.so` — if `/etc/nologin` exists, abort immediately (unless root). `auth required pam_securetty.so` — root may log in only on terminals in `/etc/securetty`; a failure dooms the stack but later modules still run (so an attacker can't tell *which* check failed). `auth required pam_env.so` sets env vars. `auth sufficient pam_unix2.so` — standard UNIX password check; **success here aborts the stack successfully** *only because* no earlier `required` module failed. `auth sufficient pam_sss.so use_first_pass` — if the user has no local account, try the directory via sssd, reusing the already-typed password. The lesson: `sufficient` short-circuits on success but cannot rescue a prior `required` failure, and modules deliberately keep running past failures to obscure the failing step.

## Key Takeaways
1. SSO = identity (LDAP/AD) + authentication (Kerberos or LDAP bind), glued by sssd → nsswitch → PAM.
2. LDAP is an attribute-based, hierarchical, read-mostly directory; entries are dn-keyed property lists exchanged as LDIF.
3. Kerberos is ticket-based and clock-sensitive — always run NTP and fix DNS/FQDN; `realm join` automates AD enrollment on Linux.
4. sssd unifies identity/auth and caches offline; require TLS for LDAP auth.
5. nsswitch order = local `files` then `sss`; PAM control flags (`required`/`requisite`/`sufficient`) have subtle, order-dependent semantics — understand them before editing.
6. NIS and rsync'd password files are legacy — use a directory + config management.

## Connects To
- **Ch 8**: user management (the accounts being centralized; `/etc/passwd`/`shadow`/`group`).
- **Ch 3**: PAM as authentication framework, root login restrictions (`securetty`).
- **Ch 16**: DNS (required for Kerberos hostname mapping).
- **Ch 13**: NTP (time sync for Kerberos tickets).
- **Ch 23**: configuration management (distributing identity config / files).
