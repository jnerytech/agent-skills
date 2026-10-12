# Chapter 21: The Network File System (NFS)

## Core Idea
NFS shares filesystems transparently across UNIX/Linux systems — applications use the same syscalls as for local files. The big version divide: **v2/v3 are stateless** (server forgets clients; survives crashes via cookies, but can't manage locks/concurrency, AUTH_SYS security is broken) while **v4 is stateful** (folds in locking, requires TCP/port 2049, single pseudo-filesystem, mandatory strong security via RPCSEC_GSS/Kerberos, NAT/firewall-friendly). **Use v4 whenever both sides support it; discontinue v3.**

## Frameworks Introduced
- **Stateful vs stateless** design tradeoff: stateless (v2/v3) = painless server crashes/reboots (each request independent, cookies survive) but no concurrency control; stateful (v4) = robust locking/read-write management but needs crash-recovery negotiation (grace period for clients to report pre-crash state).
- **Server exports → client mounts**: server lists shared directories in `/etc/exports`; clients `mount host:/path`. In v3 each export is independent; in v4 the server presents one **pseudo-filesystem** (its namespace skeletonized to just exported dirs) that the client mounts at the root and browses.
- **NFSv4 identity mapping**: users represented as `user@nfs-domain` strings; an idmap daemon translates UID/GID↔string on each side. **Mapping applies only to file-attribute operations (stat/chown/`ls -l`), NOT to access control** — access still uses raw UIDs via RPC.
- **Security flavors**: AUTH_NONE (none), AUTH_SYS (UNIX UID/GID — trivially subvertible), RPCSEC_GSS (Kerberos — the only real choice).

## Key Concepts
- **Root squashing**: server maps incoming UID 0 to the `nobody` account (UID 65534) so remote root can't run rampant — but a client root can `su` to any UID, so it only protects root-owned, non-world-accessible files.
- **`hard` vs `soft` mounts**: `hard` (default) = operations block until the server returns (no data loss); `soft` = operations fail with an error (risks data loss — "an abomination"). Recommended combo: **`hard,intr,bg`** (`intr` lets users interrupt blocked ops; `bg` retries failed mounts in background).
- **`/etc/exports`** (Linux): `dir host(options) host(options)` — directory, then space-separated clients each with parenthesized options. **A stray space changes meaning catastrophically** (`dir host (rw)` exports rw to *everyone* and ro to host). Least-privileged rule wins on overlap.
- **Daemons**: v4 needs only `nfsd` (file service) on port 2049. v3 also needs `mountd` (mount protocol), `lockd`+`statd` (locking), and `portmap` (port 111). Activate export changes: `exportfs -a` (Linux) / `service nfsd restart` (FreeBSD).
- **AUTH_SYS depends on consistent passwd/UID across all hosts** — otherwise users access each other's files; any rogue host can forge identities.

## Mental Models
- **Stateless was a feature, not a bug — for v2/v3.** Server crashes are painless because nothing is remembered; the client just waits and resubmits. v4 trades this simplicity for real locking and security.
- **AUTH_SYS "security" is a fig leaf.** The client self-reports its UID; a malicious host (or root via `su`) can claim any identity. Use Kerberos + RPCSEC_GSS — "the only reasonable choice."
- **Identity mapping ≠ authorization.** `ls -l` can show john as owner (idmap translated the UID for display) while ben can still *write* the file (raw UID sent for access control matched john's server UID). Apparent permissions can contradict enforced permissions — keep passwd/UIDs consistent.
- **Don't serve critical system binaries over NFS.** A down server hangs every process touching a `hard`-mounted filesystem — including daemons.

## Anti-patterns
- **NFSv3 in production / over WANs**: long history of RPC bugs + broken AUTH_SYS — discontinue v3; if stuck, packet-filter ports 2049 + 111.
- **Stray space in `/etc/exports`**: silently opens read/write to the whole world — "Oops."
- **Export without a host list**: usually mountable by *all* machines — a sizable security hole.
- **`soft` mounts**: processes get errors and lose data when the server blips; prefer `hard,intr,bg`.
- **`no_root_squash`**: dangerous — lets remote root act as local root.
- **FreeBSD: designating `/` as the V4 root**: exposes the *entire* server filesystem regardless of export status (FreeBSD doesn't implement the RFC pseudo-filesystem).
- **`async` export option**: replies before disk write — slight speedup but data corruption if the server restarts mid-write.

## Code Examples
```sh
# Server: /etc/exports (Linux) — NO space between host and (options)!
/home   *.users.admin.com(rw)   172.17.0.0/24(ro)
sudo exportfs -a            # activate after editing (Linux)
sudo exportfs -v           # show current exports (only local view in v4)

# FreeBSD /etc/exports — different format; V4: line designates the pseudo-root
/var/www -ro,alldirs www*.admin.com
V4: /exports -sec=krb5p,krb5i,krb5,sys -network *.admin.com

# Client: verify exports (v3 only) then mount
showmount -e monk                       # list server's v3 exports (useless for v4)
sudo mount -o rw,hard,intr,bg server:/home/ben /nfs/ben   # v3
sudo mount -o rw,hard,intr,bg server:/ /nfs/ben           # v4 (mount the pseudo-root)
sudo mount -t nfs -o nfsv4 server:/ /mnt                  # FreeBSD v4

# /etc/fstab for boot-time mount
# monk:/home  /nfs/home  nfs  rw,bg,intr,hard,nodev,nosuid  0  0
sudo mount -a -t nfs       # apply fstab NFS mounts now

# Diagnostics
nfsstat -c                 # client stats: >3% timeouts = problem
# badxid~0 + timeouts -> packets lost (lower rsize/wsize)
# badxid~timeouts      -> server too slow (raise timeo, or replace server)
```

## Reference Tables
**Key export options (Linux)**: `ro`/`rw`, `root_squash` (default)/`no_root_squash` (dangerous)/`all_squash`, `anonuid`/`anongid`, `sync` (default)/`async`, `subtree_check`, `sec=flavor`, `insecure` (allow unprivileged source ports).

**Mount flags (Linux)**: `rw`/`ro`, `hard`/`soft`, `intr`/`nointr`, `bg`, `rsize=`/`wsize=` (1KiB–1MiB, negotiated), `timeo=`, `retrans=`, `nfsvers=`, `proto=` (must be tcp for v4), `sec=`.

**Daemons by version**: v4 → `nfsd` only (TCP 2049). v3 → + `mountd`, `lockd`, `statd`, `portmap` (111). Identity map: `rpc.idmapd` (`/etc/idmapd.conf`, Linux) / `nfsuserd` (FreeBSD).

## Worked Example
**Why `ls -l` lies on an NFSv4 client.** ben (client UID 1000) lists a directory `ben` that `ls -l` shows as `drwxr-xr-x ... john` — owned by john, no write permission for others. Yet `touch ben/file` *succeeds*. How? On the *server*, john has UID 1000. The idmap daemon translated the server's UID 1000 → `john@domain` → the client's john (UID 1010) for *display*, so the directory appears john-owned. But for the actual write, ben's raw UID 1000 is sent over RPC and matched directly against the server, where 1000 *is* john — so access is granted. The displayed owner (idmap, attribute layer) and the enforced owner (RPC, access layer) diverge. The fix isn't to trust the display — it's to keep UIDs consistent across hosts (or use Kerberos), because identity mapping never participates in authorization.

## Key Takeaways
1. Use NFSv4 (stateful, TCP/2049, pseudo-filesystem, mandatory strong security); retire v3 and never run v2/v3 over WANs.
2. Server exports in `/etc/exports`, activated with `exportfs -a`; mind the catastrophic stray-space bug and always list specific hosts.
3. Mount with `hard,intr,bg`; avoid `soft` and don't serve critical binaries over NFS.
4. AUTH_SYS is broken — use Kerberos + RPCSEC_GSS; otherwise keep passwd/UIDs perfectly consistent.
5. Identity mapping affects only file-attribute display, not access control — apparent and enforced permissions can disagree.
6. Diagnose with `showmount` (v3), `exportfs -v`, and `nfsstat` (>3% timeouts = trouble; read badxid to localize network vs slow-server).

## Connects To
- **Ch 20**: storage (filesystems being exported; SAN/distributed FS alternatives).
- **Ch 22**: SMB/Samba (the cross-platform file-sharing alternative).
- **Ch 17**: Kerberos/RPCSEC_GSS authentication, LDAP for consistent UIDs.
- **Ch 8**: UID/GID consistency, the `nobody` account.
- **Ch 27**: security (firewalling ports 2049/111, privileged ports).
