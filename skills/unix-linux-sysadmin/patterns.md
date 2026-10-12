# Patterns — Sysadmin Techniques & Procedures

Concrete, reusable techniques from ULSAH. Format: **When to use → How → Trade-offs.**

## Add a disk (Linux)
**When**: attach new storage, single volume, default FS.
**How**: `lsblk -o +MODEL,SERIAL` (verify!) → `fdisk /dev/sdX` (`g`,`n`,`w` = GPT+partition) → `mkfs -t ext4 -L label /dev/sdX1` → `mkdir /mnt/x` → `mount LABEL=label /mnt/x` → add `LABEL=label … /etc/fstab`.
**Trade-offs**: reference by LABEL/UUID, never device name (ephemeral). FreeBSD: `gpart create -s GPT`/`gpart add`/`newfs`.

## Build software from source
**When**: no package, or need custom compile options.
**How**: `git clone` → `./configure --help` (`--prefix=` to relocate) → `./configure && make && sudo make install`.
**Trade-offs**: no package tracking — prefer OS packages; check INSTALL/README for prerequisites.

## Safe site-wide sudo
**When**: grant root access with accountability across many hosts.
**How**: one master `/etc/sudoers` (host is a match criterion), edit with `visudo`, validate `visudo -c -f`, distribute via config mgmt or a cron pull (`scp` + validate). 90% is `ADMINS ALL=(ALL) ALL`.
**Trade-offs**: last-matching-line wins (4-tuple); never blacklist commands; a sudoer's account ≈ root.

## Reload a daemon without restart
**When**: apply config changes (rsyslog, sendmail, BIND, nginx).
**How**: `kill -HUP $(cat /var/run/<daemon>.pid)` or `systemctl reload <unit>`.
**Trade-offs**: HUP a file-writing daemon *before* rotating its logs; some daemons need full restart.

## Find what's filling a filesystem
**When**: disk full, runaway output.
**How**: `df -h` (find 100%+ FS) → `du -h <mount>` recursively to the big files.
**Trade-offs**: unlinked-but-open files show in `df` not `du` — use `lsof`/`fuser` to find the holder.

## Trace a stuck/suspicious process
**When**: a process is hung, looping, or suspect.
**How**: `strace -p <pid>` (Linux) / `truss` (FreeBSD); `-f` follows forks, `-e trace=file` shows file ops. Capture *before* killing (preserves evidence).
**Trade-offs**: dense output — focus on syscalls returning errors.

## Subnet arithmetic
**When**: split a network, decode an address.
**How**: usable hosts = `2^(32−N) − 2`; last netmask byte = `256 − network-size`; network's last byte divisible by size. Verify with `ipcalc`.
**Trade-offs**: all hosts on one segment share one netmask; `/31` (RFC3021) has both addresses usable.

## Debug a DNS delegation
**When**: name resolution fails or a zone won't propagate.
**How**: `dig +trace name` follows root→TLD→domain; or query each server `dig @server name SOA`. `aa` flag = authoritative; `NXDOMAIN` = no such name; `SERVFAIL` = server config error. **Always bump the SOA serial after editing a zone.**
**Trade-offs**: external servers nonrecursive; resolver-facing servers must be recursive.

## Resize an LVM filesystem online
**When**: a logical-volume FS is full.
**How (enlarge — volume first)**: confirm free space `vgdisplay` → `lvresize -L +100G vg/lv` → `resize2fs /dev/vg/lv` (XFS: `xfs_growfs`, mounted). **Shrink = filesystem first.**
**Trade-offs**: XFS/UFS grow-only; cloud disks resize at 3 layers (provider/partition/FS).

## Software RAID 5 (mdadm)
**When**: redundancy without a dedicated controller.
**How**: partition disks (type "Linux RAID") → `mdadm --create /dev/md/x --level=5 --raid-devices=3 /dev/sd{f,g,h}1` → `watch cat /proc/mdstat` → `mdadm --detail --scan >> /etc/mdadm.conf`.
**Trade-offs**: RAID 5 ≠ backup, write hole — use ZFS RAID-Z or scrub via cron; designate hot spares.

## Centralized logging
**When**: compliance, correlation, tamper-resistance.
**How**: clients `*.* @@logserver` (TCP) + `imfile` for app logs; server `imtcp` port 514, filter by `$programname`, write site-wide files. TLS via `gtls` driver on 6514.
**Trade-offs**: TCP can still drop (use RELP for guarantees); set `Storage=persistent` for the journal.

## Patch OS packages with dependencies
**When**: security update affecting dependent packages.
**How (RHEL)**: `rpm -q --whatrequires <pkg>` first → fetch all dependents → `rpm -U pkg-*` (sorts by dependency). Or just let `yum`/`apt` resolve it.
**Trade-offs**: never `rpm -U --force`; restart the service afterward (rpm doesn't).

## Unattended OS install
**When**: >~10 machines.
**How**: PXE (DHCP→TFTP→boot loader) + answer file: kickstart `ks.cfg` (RHEL), preseed `preseed.cfg` (Debian). Generate programmatically; hash all passwords.
**Trade-offs**: never store cleartext passwords in answer files; Cobbler wraps PXE/DHCP/DNS/TFTP.

## Zero-downtime deployment
**When**: outages unacceptable.
**How**: **blue/green** (stage standby, test, switch LB), **rolling** (one node at a time through LB), **canary** (small % first + telemetry).
**Trade-offs**: rolling needs version coexistence; canary needs precise monitoring; immutable = new servers per release.

## Build an image as code (Packer)
**When**: reproducible VM/AMI images.
**How**: template with **builders** (platform/API) + **provisioners** (shell/Chef/Ansible); `packer build template.json`. Commit to version control.
**Trade-offs**: secrets via variables/credential store, never embedded; `-debug` to pause per step.

## Persistent USB device naming (udev)
**When**: stable `/dev` name + automount for removable media.
**How**: find name (`dmesg`/`lsusb`) → `udevadm info -a -p /block/sdX1` for stable match keys (model/serial, not size) → rule in `/etc/udev/rules.d/10-local.rules` (`SYMLINK+=`, `ACTION=="add"` + `RUN+=`) → `udevadm control --reload-rules`.
**Trade-offs**: reload silently ignores typos; never edit `/lib/udev` defaults — override in `/etc`.

## Group project share (Samba/UNIX)
**When**: a team needs a collaborative dir where files inherit the group.
**How**: `valid users = @group`, `force group`, setgid bit on the dir (`chmod g=rwxs`), `directory mask = 2770`.
**Trade-offs**: setgid makes new files inherit the dir's group — avoids a pseudo-user owner; simpler than ACLs.

## Triage a suddenly-slow server
**When**: transient performance crisis.
**How**: `ps auxww`/`top` (>50% CPU = suspect) → `uptime` load avg → `vmstat` (paging? disk?) → `kill -STOP` to test a theory. Found a hog? Usually do nothing; `renice` (CPU) / `ionice -c 3` (disk) / `ulimit` (mem), or reschedule.
**Trade-offs**: check network/DNS/NFS for ripple-effect slowness; on VMs watch stolen cycles (`st`).

## Harden a new system
**When**: before production.
**How**: patch → disable unneeded services (`netstat -an|grep LISTEN`, `lsof -i:port`, stop+de-boot) → packet filter (only needed ports) → MFA + `PermitRootLogin No` → central logging → FIM/HIDS (OSSEC) → Fail2Ban → scan yourself (`nmap -sV -O`).
**Trade-offs**: least privilege + defense in depth + minimize attack surface; automate it for repeatability.

## Self-document with infrastructure as code
**When**: keep docs from going stale.
**How**: store config as Puppet modules / Ansible playbooks in Git; rebuild & compare environments regularly.
**Trade-offs**: docs and environment always match; complement with short one-page human docs and config-file comments.
