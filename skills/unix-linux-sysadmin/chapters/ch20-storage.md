# Chapter 20: Storage

## Core Idea
Storage is a **layered stack of Lego blocks** between raw devices and the filesystem users see: device → partition → RAID array → logical volume → filesystem (each "can be built on" the layer below). Master the hardware tradeoffs (HDD capacity vs SSD random-access speed), the device-naming pitfalls, RAID levels, logical volume management (resize/snapshot on the fly), and next-gen all-in-one filesystems (ZFS/Btrfs). **Drives fail often — design assuming failure; RAID is not a backup.**

## Frameworks Introduced
- **The storage stack layers**: *storage device* (anything block-addressable) → *partition* (fixed subsection) → *RAID array* (combine devices for performance/redundancy) → *volume group/logical volume* (LVM: flexible pools, resize, snapshots) → *filesystem*. Stack modules to connect each device to its application.
- **"Add a disk" recipe**: identify the device (verify by model/serial!) → write a GPT partition table → `mkfs`/`newfs` a filesystem (with a label) → make a mount point → mount → add to `/etc/fstab` by **label/UUID, not device name**.
- **RAID levels**: 0 (stripe — speed, *worse* reliability), 1 (mirror — redundancy, read speed), 1+0/0+1 (both, ≥4 disks), 5 (striped data+parity, survives 1 failure, ≥3 disks, ≥67% efficient), 6 (two parity, survives 2 failures, ≥4 disks). JBOD/linear = concatenation, no redundancy.
- **HDD vs SSD tradeoff**: HDD = cheap capacity, slow random access (seek + rotational latency); SSD = fast random access (parallel flash), pricier, limited rewrites + sneaky isolated-bad-block failures.

## Key Concepts
- **Ephemeral device names**: `/dev/sda` etc. are assigned at enumeration — adding a disk or rebooting can rename existing disks. **Never name a raw device in config files** (`/etc/fstab`); use labels or UUIDs (`/dev/disk/by-*`).
- **GPT** (GUID Partition Table) replaces MBR; tools: `fdisk`/`parted`/`gparted` (Linux), `gpart` (FreeBSD).
- **LVM** (Linux LVM2): physical volumes (`pvcreate`) → volume groups (`vgcreate`) → logical volumes (`lvcreate`). Resize/move/snapshot online; commands prefixed `pv`/`vg`/`lv`.
- **TRIM**: lets the filesystem tell an SSD a block is free so it can pre-erase pages (erasing is slow and done in big clusters). Without it, write performance degrades.
- **Advanced Format / 4KiB blocks**: modern drives use 4KiB sectors. **512e** (emulates 512B) is alignment-sensitive — partition on a large power-of-2 boundary (modern tools do this automatically). 4Kn is the future.
- **SMART**: drives expose ~50 health parameters. Four are highly predictive (scan errors, reallocation count, off-line reallocation, sectors on probation — all should be 0); a nonzero value raises 60-day failure odds 14–39×. Monitor with `smartmontools` (`smartd`/`smartctl`).
- **Secure erase**: `rm -rf` leaves data recoverable; ATA secure erase (`hdparm`/`camcontrol`) overwrites securely and resets an SSD to fully-erased.

## Mental Models
- **RAID is not a backup.** RAID 5 protects against *one disk failure* — not accidental deletion, controller failure, fire, hackers, or two simultaneous failures. Keep off-line backups regardless.
- **Drives fail constantly (~6–8% AFR after 2 years).** Even the best are failure-prone; ~150 disks in service ≈ one failure/month. MTBF is a cherry-picked upper bound — divide by ~7.5 for realistic 5-year rates. Be aggressive retiring suspect drives (odd noises, block errors in temp files).
- **Resize order: reductions filesystem-first, enlargements volume-first.** Don't memorize — reason from what's happening (don't shrink the volume out from under the filesystem's data).
- **Prefer software RAID / ZFS / Btrfs over cheap "RAID cards."** Many PC RAID cards/motherboard RAID have no nonvolatile cache — just software RAID in disguise. A hardware controller failure can destroy *all* mirrored disks at once (authors' war story).

## Anti-patterns
- **Formatting/partitioning without verifying the device** (model/serial/size): a newly added drive isn't always the highest-numbered, and names shift — "formatting the wrong device file is a rapid route to disaster."
- **Naming devices in `/etc/fstab`**: use `LABEL=`/`UUID=` — device names are ephemeral.
- **Treating RAID 5 as durable storage**: the **write hole** — a crash mid-write can desync data and parity invisibly; only surfaces (as garbage) when a disk fails and is rebuilt. ZFS RAID-Z (variable-width stripes) is immune; otherwise enable periodic **scrubbing** via cron/timer.
- **Reformatting new drives "as a matter of course"**: factory low-level formatting is as good as any; avoid unless required.
- **Long-lived LVM2 snapshots**: fixed-size; if a snapshot runs out of allocated space it becomes corrupt/inactive — keep them short-lived or as large as the source (unlike ZFS/Btrfs cheap snapshots).
- **SSDs for archival**: errors accumulate regardless of duty cycle — but an isolated bad block ≠ end of life (reformat and reuse).

## Code Examples
```sh
# Add a disk (Linux): identify -> partition (GPT) -> filesystem -> mount
lsblk -o +MODEL,SERIAL          # identify the new drive (verify!)
sudo fdisk /dev/sdb             # g (new GPT), n (new partition), w (write)
sudo mkfs -t ext4 -L spare /dev/sdb1
sudo mkdir /spare && sudo mount LABEL=spare /spare
# /etc/fstab:  LABEL=spare  /spare  ext4  errors=remount-ro  0  0

# Add a disk (FreeBSD)
geom disk list
sudo gpart create -s GPT ada1
sudo gpart add -l spare -t freebsd-ufs -a 1M ada1
sudo newfs -L spare /dev/ada1p1

# LVM2: pv -> vg -> lv, then resize
sudo pvcreate /dev/sdb1
sudo vgcreate DEMO /dev/sdb1 ; sudo vgdisplay DEMO
sudo lvcreate -L 100G -n web1 DEMO
sudo lvcreate -L 100G -s -n web1-snap DEMO/web1     # snapshot
sudo lvresize -L +100G DEMO/web1 ; sudo resize2fs /dev/DEMO/web1   # enlarge: volume then FS

# Software RAID 5
sudo mdadm --create /dev/md/extra --level=5 --raid-devices=3 /dev/sdf1 /dev/sdg1 /dev/sdh1
watch cat /proc/mdstat           # monitor sync/recovery
sudo mdadm --detail --scan       # generate /etc/mdadm.conf ARRAY line

# Health & erase
smartctl -a /dev/sda             # SMART data
sudo hdparm --user-master u --security-erase pass /dev/sdX   # ATA secure erase
```

## Reference Tables
**HDD vs SSD**: HDD ~8ms random access, 200MB/s seq, 150 IOPS, $0.03/GB, ≤16TB. SSD ~0.25ms, 450MB/s, 100k IOPS, $0.26/GB, ≤2TB, limited writes.

**RAID levels**: 0 stripe (speed, no redundancy) · 1 mirror (≤50% efficient) · 1+0/0+1 (≥4 disks) · 5 (≥3 disks, ≥67% efficient, 1-disk tolerance, write hole) · 6 (≥4 disks, 2-disk tolerance). Use `md`/mdadm or LVM2 (RAID 5/6 needs `md`); or ZFS RAID-Z / Btrfs.

**Interfaces**: SATA (6 Gb/s, mass-market, optional hot-swap), SAS (12 Gb/s, enterprise, deep queues, expanders, tunnels SATA), PCIe/NVMe (≫20× SATA for top SSDs), M.2/U.2 (combined connectors), USB 3.x (external, avoid USB 2.0).

## Worked Example
**Grow a full LVM filesystem online.** `/mnt/web1` (a 100GB logical volume) is full and needs +100GB. (1) Confirm free space in the volume group: `vgdisplay DEMO` shows 800GB free. (2) *Enlarge volume first* (enlargements are volume-first): `lvresize -L +100G DEMO/web1` — now 200GB. (3) Grow the filesystem to fill it: `resize2fs /dev/DEMO/web1` (it reads the new size from the volume; ext4 grows mounted). For XFS use `xfs_growfs` (must be mounted), UFS `growfs` — both can only grow, never shrink. The *reason* enlargement is volume-first: the filesystem can't extend into space the volume doesn't yet have; conversely a *shrink* must be filesystem-first so you don't cut off blocks the filesystem is still using. In the cloud, the virtual disk is itself a logical volume — resize at three layers (provider → partition → filesystem).

## Key Takeaways
1. Storage is a stack: device → partition → RAID → LVM → filesystem; compose the layers you need.
2. Verify a disk's identity before touching it, and reference disks by label/UUID (names are ephemeral).
3. Drives fail often — RAID adds redundancy/performance but is **not a backup**; keep off-line backups and use SMART monitoring + hot spares.
4. Know the RAID levels and the RAID 5 write hole (use ZFS RAID-Z or scrub regularly); prefer software RAID/ZFS/Btrfs over cheap RAID cards.
5. LVM gives online resize/move/snapshots — enlarge volume-first, shrink filesystem-first; LVM2 snapshots are fixed-size and fragile (unlike ZFS/Btrfs).
6. HDD = cheap capacity, SSD = fast random I/O (mind TRIM, 4KiB alignment, and sneaky isolated-block failures).

## Connects To
- **Ch 5**: the filesystem layer (file types, permissions) atop this storage.
- **Ch 11**: device files, `/dev`, block vs character devices, major/minor numbers.
- **Ch 21/22**: network filesystems (NFS, SMB) sharing this storage.
- **Ch 9**: cloud block storage / object stores as virtual logical volumes.
- **Ch 28**: monitoring (SMART, disk failure surveillance).
