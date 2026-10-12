# Chapter 22: SMB

## Core Idea
**SMB** (Server Message Block) is the file-sharing protocol native to Windows and macOS. **Samba** brings it to UNIX/Linux — one server-side package, no special Windows-side software, giving "just like local" access between UNIX and Windows. Use it when you need cross-platform file sharing; for homogeneous UNIX/Linux, prefer NFS. (Note: CIFS was a deprecated 1996 marketing variant — only SMB lives on, now at v2/v3.)

## Frameworks Introduced
- **Samba architecture**: two user-space daemons — `smbd` (file/print service + auth, forks a per-user instance running *as that user*) and `nmbd` (name resolution + service announcement/browsing). No kernel module needed (unlike NFS).
- **Two authentication paths**: (1) **local accounts** — `security = user`, a *separate* SMB password hash per user via `smbpasswd` (UNIX account must pre-exist); (2) **Active Directory** — `security = ads`, piggybacks on the user's domain login via sssd/Kerberos (the modern choice).
- **Share configuration**: each `[stanza]` in `smb.conf` is a share; the stanza name is the advertised share name. Special `[homes]` stanza auto-exposes each user's home directory.
- **Group project shares via setgid**: restrict mounting to a UNIX group (`valid users = @eng`), `force group` + setgid directory bit so all created files inherit the group — collaboration without a pseudo-user owner.

## Key Concepts
- **Share**: a directory made available over the network (Windows term). Accessed as `\\server\sharename`.
- **`smbd` runs as the requesting user** after auth, so normal UNIX file/group permissions apply automatically; the only extra is Windows-style file locking.
- **SMB mounts belong to a *user*, not the system**: `mount -t cifs -o username=joe //host/share /mnt`. All files appear owned by the mounting user (tweak with `uid`/`gid`/`fmask`/`dmask`). Windows servers don't handle multiple UNIX users sharing one mount.
- **`smb.conf` auto-reloads** every few seconds — no restart needed after edits. `testparm -v` lists effective config (yours + defaults).
- **Encryption**: Samba encrypts *only password authentication*, not data transport — block external access at the firewall (UDP 137-139, TCP 137/139/445).
- **Tools**: `smbclient` (FTP-like browse/transfer without mounting), `smbstatus` (active connections + locked files), `smbcontrol` (change debug level on a running server).

## Mental Models
- **Use SMB for ubiquity, NFS for integration/performance.** Almost every OS speaks SMB; NFS is a more natural UNIX fit with better performance (kernel server). SMB = user-space, per-user processes, OS-based access control, mounted by individual users.
- **Samba leans on UNIX permissions — so home-directory exposure surprises Windows users.** If home dirs are world-readable on UNIX, Windows users see each other's files too. Use `valid users = %S` to restrict `[homes]` to the owner.
- **Don't overreach with Samba.** It *can* be an AD controller or print server, but leave AD to Windows and printing to CUPS — Samba's sweet spot is file sharing.
- **Trust Windows lock warnings.** When Windows says a file is locked by another app, it usually is — fix it client-side (close the app), don't brute-force locks on the server.

## Anti-patterns
- **Mounting an SMB share as root**: all files then belong to root and normal users can't write — mount as the appropriate user with `username=`/`uid=`.
- **Exposing Samba to the Internet**: data transport is unencrypted — users could download files in plaintext across the Internet. Firewall ports 137-139/445.
- **Using ACLs for group shares**: "too complex for most users" — use a dedicated group share + setgid directory bit instead.
- **Wrong filename charset from the start**: improperly encoded names (accented chars) accumulate and are "surprisingly complex" to fix later — set `unix charset` to match the server locale (UTF-8 recommended) up front.
- **Maintaining a separate `smbpasswd` database when AD exists**: archaic — integrate with Active Directory/LDAP via sssd.

## Code Examples
```ini
# /etc/samba/smb.conf — local-account auth
[global]
  workgroup = ulsah
  security = user
  netbios name = freebsd-book

# Active Directory auth (via sssd)
[global]
  workgroup = ulsah
  realm = ulsah.example.com
  security = ads
  dedicated keytab file = FILE:/etc/samba/samba.keytab
  kerberos method = dedicated keytab

# A simple share -> \\server\bookshare
[bookshare]
  path = /storage/bookshare
  read only = no

# Auto-share home dirs, owner-only
[homes]
  browseable = no
  valid users = %S          # restrict to the home dir's owner
  read only = no

# Group project share (setgid for shared ownership)
[eng]
  valid users = @eng
  path = /home/eng
  force group = eng
  create mask = 0660
  directory mask = 2770
  force directory mode = 2000
```
```sh
sudo smbpasswd -a tobi          # add Samba password (UNIX account must exist)
# group share dir setup:
sudo chown root:eng /home/eng ; sudo chmod u=rwx,g=rwxs,o= /home/eng   # setgid bit

# Client mount
sudo mount -t cifs -o username=joe //redmond/joes /home/joe/mnt   # Linux
sudo mount -t smbfs //joe@redmond/joes /home/joe/mnt             # FreeBSD

# Browse / debug
smbclient -L //hoarder -U dan   # list shares without mounting
smbclient //hoarder/Docs -U dan # interactive FTP-like session
sudo smbstatus                  # connections + locked files
sudo smbcontrol smbd debug "4 auth:10"   # raise debug level live
```

## Reference Tables
**SMB vs NFS**: SMB = user-space servers, per-user processes, uses OS access control, mounted by individual users, "pretty good" performance, cross-platform. NFS = kernel server (threads), one server for all clients, own access control, mounted by the system, best performance, UNIX-native.

**Samba security checklist**: `hosts allow` (explicit clients; `hosts deny` takes priority on conflict), firewall UDP 137-139 + TCP 137/139/445 from outside, current Samba version (many updates are security fixes).

**Debug sources**: `smbstatus` (state/locks), per-client logs `/var/log/samba.log.%m` with `max log size`, `smbcontrol ... debug` (live level; >100 leaks passwords).

## Worked Example
**Set up a collaborative engineering share.** Goal: members of UNIX group `eng` mount one work area, and every file created there is group-owned by `eng` so teammates can edit it — without a shared pseudo-user. (1) `smb.conf` stanza `[eng]` with `valid users = @eng` (Samba checks group membership before allowing the mount), `force group = eng` (coerce each mounter's effective GID), and `directory mask = 2770` + `force directory mode = 2000` (ensure new *subdirectories* get the setgid bit too). (2) On disk, make the share root group-`eng` and setgid: `chown root:eng /home/eng; chmod g=rwxs /home/eng`. The setgid bit makes new files inherit the directory's group (`eng`) rather than the creator's primary group — so collaboration "just works." Users still mount under their own accounts (SMB mounts are per-user), but the files land in the shared group. ACLs would also achieve this but are too complex for most users.

## Key Takeaways
1. Samba = SMB server for UNIX/Linux (one package, no Windows-side install); use for cross-platform sharing, NFS for UNIX-only.
2. `smbd` runs as the authenticated user, so UNIX permissions apply directly; `nmbd` does name resolution/browsing.
3. Authenticate via local accounts (`smbpasswd`, separate hash) or — preferably — Active Directory (`security = ads` + sssd/Kerberos).
4. SMB mounts belong to a user, not the system — never mount as root for normal-user access; tune with `uid`/`gid`/masks.
5. Samba encrypts only auth, not data — firewall ports 137-139/445 from the Internet; set `hosts allow` and the right filename charset up front.
6. Debug with `smbstatus` (locks/connections), per-client logs, and live `smbcontrol` debug levels; use setgid group shares over ACLs.

## Connects To
- **Ch 21**: NFS (the UNIX-native alternative; SMB vs NFS tradeoffs).
- **Ch 17**: single sign-on (AD/Kerberos/sssd integration for share auth).
- **Ch 5**: setgid directories, UNIX file permissions that Samba enforces.
- **Ch 12**: printing (CUPS, the recommended print server over Samba).
- **Ch 27**: security (unencrypted transport, firewalling SMB ports).
