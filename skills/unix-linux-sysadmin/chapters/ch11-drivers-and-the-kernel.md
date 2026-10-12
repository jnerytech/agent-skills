# Chapter 11: Drivers and the Kernel

## Core Idea
The kernel is the "central government" — it abstracts hardware behind a clean interface and provides five core services: device management/abstraction, processes/threads, memory management, I/O facilities (filesystems/network), and housekeeping. Admins rarely touch kernel C code; the common chores are **tuning parameters (`sysctl`), adding device drivers, loading modules, and occasionally building a custom kernel**. Be conservative — kernel changes destabilize easily; always keep a known-good fallback.

## Frameworks Introduced
- **Three ways to configure a kernel** (Linux and FreeBSD both): (1) tune dynamic parameters at runtime — easiest, most common; (2) load/unload drivers as modules on the fly; (3) build from source — hardest, least often needed.
- **Device driver abstraction**: a driver translates between hardware commands and a stylized kernel interface, keeping the rest of the kernel device-independent (like the VFS layer making disk and network filesystems look identical).
- **Device files + major/minor numbers**: `/dev` entries map operations to drivers. **Major** = which driver (device type); **minor** = which instance/unit (driver interprets freely).
- **Automatic device management**: kernel emits device add/remove events → user-space daemon acts. Linux: **udev/udevd** + sysfs + rules. FreeBSD: **devfs** (kernel) + **devd** daemon.

## Key Concepts
- **Block vs character device**: block = read/written in ~512-byte blocks (`b` in `ls -l`); character = one byte at a time (`c`). Linux treats dual-mode devices (disks) as block; FreeBSD as character.
- **Pseudo-devices**: drivers controlling no real hardware — PTYs (network logins look like serial ports), `/dev/null`, `/dev/zero`, `/dev/urandom`.
- **sysfs (`/sys`)**: in-memory kernel filesystem; one file = one device attribute; organized successor to the chaotic `/proc`. udevd reads device data from it.
- **`/proc/sys` & `sysctl`**: tunable parameters. Write to `/proc/sys/...` for a runtime change (not persistent); use `sysctl` (and `/etc/sysctl.conf`) for persistence. Variable name = the `/proc/sys` path with slashes → dots.
- **udev rules**: `match_clause, ... assign_clause, ...` in `/etc/udev/rules.d/NN-*.rules` (lower NN first). Match keys: `ACTION`, `ATTR{}`/`ATTRS{}`, `KERNEL`, `SUBSYSTEM`, `DRIVER`, `PROGRAM`. Assign keys: `NAME`, `SYMLINK`, `RUN`. Build them from `udevadm info -a`.
- **Loadable kernel modules (LKMs)**: link drivers in/out of a running kernel — no rebuild, smaller kernel. Risk: loading/unloading can panic the system.

## Mental Models
- **Don't build a kernel just to get a newer one — install a distro built around it.** Distros pick kernel versions for reasons (subtle concerns you can't see). Shoehorning a new kernel into an old distro invites instability.
- **"If it ain't broke, don't fix it."** Upgrade/patch the kernel only when expected reliability/performance gains exceed the effort and risk. *Exception: security patches go in promptly.*
- **Change IPv4 and IPv6 parameters together.** Easy to tune `net.ipv4.*` and forget `net.ipv6.*`, then debug "strange network behavior" months later.
- **Drivers are OS- and kernel-version-specific.** Windows drivers don't work; check other sites' experience before buying hardware.

## Anti-patterns
- **Editing `.config` by hand**: options are interdependent — use `make xconfig`/`gconfig`/`menuconfig` (avoid bare `make config`).
- **Skipping `make clean`**: many build problems trace back to a dirty build environment.
- **Testing an untested module on a machine you can't crash**: load/unload risks a kernel panic.
- **Editing default udev rules in `/lib/udev/rules.d`**: never edit them — override by creating a same-named file in `/etc/udev/rules.d`.
- **Forgetting `udevadm control --reload-rules`**: and note typos are *silently ignored* on reload — double-check syntax.

## Code Examples
```sh
ls -l /dev/sda        # brw-rw---- ... 8, 0  -> block device, major 8 minor 0
mknod name b 8 1      # manually create device file (rare; type b/c, major, minor)

# Tunable parameters
cat /proc/sys/fs/file-max ; echo 32768 > /proc/sys/fs/file-max   # runtime, not persistent
sysctl net.ipv4.ip_forward=0          # set now; /etc/sysctl.conf for boot-time persistence
sysctl -a                             # list all (FreeBSD & Linux)

# Linux device exploration & modules
lsusb ; dmesg ; journalctl            # how did the kernel name the new device?
udevadm info -a -n sdb                # all attributes (feed into rules)
udevadm control --reload-rules        # apply rule changes (needs root)
lsmod ; modprobe snd-usb-audio        # list / load a module
```
```
# udev rule: persist a USB flash drive's name + automount  (/etc/udev/rules.d/10-local.rules)
ATTRS{model}=="USB2FlashStorage", KERNEL=="sd[a-z]1", SYMLINK+="ate-flash%n"
ACTION=="add", ATTRS{model}=="USB2FlashStorage", KERNEL=="sd[a-z]1", \
  PROGRAM=="/lib/udev/vol_id -t %N", RESULT=="vfat", RUN+="/bin/mount -t vfat /dev/%k /mnt/ate-flash%n"
```

## Reference Tables
**Auto device management components**: Linux → `udev`/`devtmpfs` filesystem, `udevd` daemon, config `/etc/udev/udev.conf` + rules `/etc/udev/rules.d`. FreeBSD → `devfs` filesystem (`/etc/devfs.conf` static, `/etc/devfs.rules` removable), `devd` daemon (`/etc/devd.conf`: `attach`/`detach`/`nomatch`/`notify`).

**Common tunable params**: `fs/file-max` (max open files), `net/ipv4/ip_forward` (routing), `net/ipv4/tcp_syncookies` (SYN-flood defense), `kernel/panic` (reboot delay after panic), `vm/overcommit_memory`. FreeBSD: `kern.maxfiles`, `net.inet.ip.forwarding`, `kern.ipc.nmbclusters`, `kern.maxvnodes`.

**Build steps** — Linux: `cd src` → `make {x,g,menu}config` → `make clean` → `make` → `make modules_install` → `make install`. FreeBSD: `cd /usr/src/sys/arch/conf` → `cp GENERIC MYCUSTOM` → edit → `cd /usr/src` → `make buildkernel KERNCONF=MYCUSTOM` → `make installkernel KERNCONF=MYCUSTOM`.

## Worked Example
**Persistent name + automount for a USB flash drive (udev).** (1) Insert it; find the kernel's name via `lsusb` or `dmesg`/`journalctl` → it's `sdb`/`sdb1`. (2) `udevadm info -a -p /block/sdb/sdb1` dumps match opportunities — pick stable ones: `KERNEL=="sd[a-z]1"` + `ATTRS{model}=="USB2FlashStorage"` (or the serial number; *avoid* size, which changes). (3) Write rules to `/etc/udev/rules.d/10-local.rules`: a `SYMLINK+="ate-flash%n"` rule for a stable `/dev` name; an `ACTION=="add"` rule with `RUN+="/bin/mkdir -p /mnt/ate-flash%n"` then a `PROGRAM`/`RESULT=="vfat"` guard + `RUN+="/bin/mount ..."`; and `ACTION=="remove"` rules to umount/rmdir. (4) `sudo udevadm control --reload-rules`. Now insertion creates `/dev/ate-flash1` → `sdb1` and mounts it at `/mnt/ate-flash1`. Note `PROGRAM` (match-phase) vs `RUN` (action-phase) — and that reload silently ignores typos.

## Key Takeaways
1. The kernel abstracts hardware; admins tune it, add drivers, load modules, and rarely rebuild — conservatively, with a fallback.
2. Device files map to drivers by major (type) + minor (instance) number; block (`b`) vs character (`c`).
3. udev/udevd + sysfs (Linux) and devfs + devd (FreeBSD) auto-manage `/dev`; write udev rules for persistent names/automount.
4. `sysctl`/`/proc/sys` tune runtime parameters — persist in `/etc/sysctl.conf`; change IPv4 and IPv6 together.
5. Prefer installing a distro built around the kernel you need over building one yourself; patch only when gains beat risk (security patches excepted).
6. LKMs add/remove drivers without a rebuild but can panic the kernel — don't test untested modules on machines you can't crash.

## Connects To
- **Ch 2**: GRUB/boot loader, kernel boot parameters, side-by-side kernels.
- **Ch 4**: `/proc` filesystem and process internals.
- **Ch 5**: device files, block/character devices, the VFS abstraction.
- **Ch 13**: network tunables (`ip_forward`, `tcp_syncookies`) live in `/proc/sys/net`.
- **Ch 29**: performance tuning via kernel parameters (vnodes, file-max, memory).
