# Chapter 5: The Filesystem

## Core Idea
The filesystem is a single unified hierarchy rooted at `/` that represents not just files but devices, kernel state, sockets, and IPC — everything is mapped into the namespace. It has four parts: **namespace** (naming/hierarchy), **API** (syscalls), **security model** (permission bits/ACLs), and **implementation** (ext4/XFS/UFS/ZFS/Btrfs). Master pathnames, mounting, the 7 file types, links, and the 12 mode bits.

## Frameworks Introduced
- **The 7 file types** — everything must look like one of: regular file, directory, character device, block device, local domain (UNIX) socket, named pipe (FIFO), symbolic link. Identify with `file` or the first char of `ls -l`.
- **The 12 mode bits** = 9 permission bits (owner/group/other × read/write/execute) + setuid (4000) + setgid (2000) + sticky (1000). File-type bits are fixed at creation; mode bits change with `chmod`.
  - When to use: every permission decision.
  - How: octal (absolute) or mnemonic `u/g/o/a` + `+/-/=` + `rwx`.
- **Mounting**: `mount` grafts a filesystem onto a *mount point* directory; `/etc/fstab` declares what mounts at boot (and documents disk layout).

## Key Concepts
- **Pathname**: absolute (`/tmp/foo`) or relative (to each process's current directory). Component ≤255 chars; full path ≤4095 (Linux)/1024 (BSD).
- **Hard link**: an additional directory entry pointing to the *same* inode; all equal; filesystem frees data only when link count hits 0. Can't cross filesystems or (sanely) link directories. `ln old new` (mirrors `cp`).
- **Symbolic (soft) link**: points to a *name*; can cross filesystems, dangle, or loop. `ln -s target linkname`. Its `lrwxrwxrwx` perms are dummies — access governed by the target's perms + containing dir. The first arg is a literal string, *not* resolved relative to cwd.
- **Inode**: integer identifying a file's contents; hard links share it. `ls -li` shows it.
- **Device files**: major number → which driver; minor → which unit. `/dev` is now a kernel-maintained virtual filesystem.
- **ctime**: attribute-*change* time (NOT creation time); mtime = content-modification; atime = access.
- **ACL / ACE**: access control list = ordered list of access control entries; each names a user/group + permissions. Two flavors: POSIX-draft and NFSv4 (Windows-style).

## Mental Models
- **Permission triplet bit values**: owner 400/200/100, group 40/20/10, other 4/2/1 — high=read, mid=write, low=execute. Most-specific category wins (owner perms apply to the owner even if group perms are broader).
- **Execute bit means different things on dirs**: on a dir it's "search/scan" (traverse/enter); read+execute = list contents; write+execute = create/delete/rename within.
- **Deleting a file is a directory permission, not a file permission.** Write on the *parent directory* lets you remove/rename a file regardless of the file's own perms — which is why the sticky bit on `/tmp` exists (only owner/dir-owner/root may delete).
- **setgid on a directory** ≠ setgid on an executable: it makes new files inherit the directory's group — handy for shared project dirs.
- **`umask` = permissions to *remove*.** Default 022 (deny group/world write); 027 also denies all "other" access. Users can override their own; set defaults in startup files, or use MAC (SELinux) to enforce.

## Anti-patterns
- **Reorganizing the standard file tree**: hidden dependencies break things — accept default locations unless you have a compelling reason. Consult the FHS / `man hier`.
- **`chmod -R a-x`**: blind to dir-vs-file execute semantics; strips the search bit off directories. Use `find mydir -type f -exec chmod a-x {} ';'` instead. Prefer mnemonic syntax with `-R` to preserve unset bits.
- **`chown -R matt ~matt/.*`**: the `.*` glob matches `..` and walks up into the parent/other users' homes.
- **`chattr +i` to block config management**: makes Ansible/Salt silently fail and confuses everyone later — fix it *in* the config system instead. Immutable/append flags are "more often used by hackers than against them."
- **`umount -f` / `umount -l` on local journaled FS (XFS/ext4)**: usually a bad idea; instead use `fuser`/`lsof` to find who's holding the mount.

## Code Examples
```sh
mount /dev/sda4 /users          # graft filesystem onto mount point
mount                           # list all mounted filesystems
fuser -cv /usr                  # who is using this filesystem (PID + command)
lsof                            # richer alternative to fuser
file /bin/sh                    # report file type / format
ls -ld /usr/include             # -d: the dir itself, not its contents
ls -li                          # show inode numbers + link counts (trace hard links)
rm -- -f                        # delete a file literally named "-f"
rm -i foo*                      # confirm each (safe with glob/control-char names)
ln old new                      # hard link;  ln -s target link  # symlink
chmod 711 myprog                # octal: rwx owner, --x others
chmod -R g+w mydir              # mnemonic + recursive: preserve execute bits
chmod ug=srx,o= file            # setuid+setgid, rx owner/group, nothing for other
chown -R matt:staff ~matt/restore
find mnt -xdev -inum <inode> -print    # find all hard links to an inode
```

## Reference Tables
**`ls -l` first char**: `-` regular · `d` dir · `c` char device · `b` block device · `s` socket · `p` named pipe · `l` symlink.

**Mode-char overloads in `ls`**: owner execute shows `s` (setuid), group execute `s` (setgid), other execute `t` (sticky). Capital `S`/`T` = special bit set but execute bit *off*. Trailing `.` = no ACL; `+` = ACL present.

**Linux bonus flags** (`lsattr`/`chattr`): `a` append-only, `i` immutable (root-only), `A` no-atime, `d` skip-backup (advisory), `S`/`j`/`D` sync/journal (databases). Check `lsattr` when a file "behaves strangely."

## Worked Example
**Decode `ls -l /usr/bin/gzip` → `-rwxr-xr-x 4 root wheel 37432 Nov 11 2016`**: `-` = regular file; `rwx`=owner all, `r-x`=group read/exec, `r-x`=other read/exec; link count `4` (gzip/gunzip/gzcat/zcat are hard links to one inode); owner `root`, group `wheel`; size 37432 bytes; mtime Nov 11 2016. For a device file `crw--w---- 1 root tty 4, 0 /dev/tty0`, the size field is replaced by **major,minor** = `4, 0` → terminal driver, first virtual console.

## Key Takeaways
1. One unified tree from `/`; "everything is a file," including devices, sockets, and `/proc`/`/sys` kernel interfaces.
2. Know the 7 file types and read them off `ls -l`'s first character.
3. Hard link = same inode (counted, same-FS); symlink = a named pointer (can dangle/cross FS). Deleting requires permission on the *directory*, not the file.
4. 12 mode bits: 9 perms + setuid/setgid/sticky; octal bit values 4/2/1 per triplet; execute = "search" on directories.
5. `chmod`/`chown`/`chgrp` (mind `-R` execute semantics and `.*` globs); `umask` removes default perms.
6. ACLs extend the 9-bit model when owner/group/other isn't enough; the deeper storage/partition topics live in Ch 20.

## Connects To
- **Ch 3**: setuid/setgid, permission semantics, ACLs, SELinux overrides.
- **Ch 11**: device files, drivers, `/dev` management.
- **Ch 20**: storage — partitioning, ZFS/Btrfs, fsck, the technical filesystem internals.
- **Ch 21/22**: NFS and SMB (network filesystems plugged into the same tree).
