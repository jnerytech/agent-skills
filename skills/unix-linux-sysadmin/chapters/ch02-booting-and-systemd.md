# Chapter 2: Booting and System Management Daemons

## Core Idea
Booting proceeds through fixed stages — firmware → boot loader → kernel → the PID 1 system-management daemon that starts services and manages state. On modern Linux that daemon is **systemd** (dependency-driven, parallel); on FreeBSD it's simple BSD `init` + `rc.d`. Admins don't drive boot interactively; they edit config files and boot-loader/kernel arguments.

## Frameworks Introduced
- **The four boot tasks**: (1) find/load/run bootstrap code, (2) find/load/run the kernel, (3) run startup scripts & daemons, (4) maintain process hygiene + manage state transitions. Task 4 never ends, so "boot" blurs into normal operation.
- **systemd unit model**: everything systemd manages is a *unit* (service, socket, device, mount, target, timer, slice…), each defined by a `.ini`-syntax **unit file**.
  - When to use: any service start/stop/enable/status work on a modern Linux box.
  - How: `systemctl <subcommand> <unit>`; stock units in `/usr/lib/systemd/system` (or `/lib/...`) — never edit; local overrides in `/etc/systemd/system` (highest priority); transient in `/run/systemd/system`.
- **Targets replace run levels**: a `.target` unit is just a well-known dependency marker for an operating mode. `multi-user.target` (CLI), `graphical.target` (GUI), `rescue.target` (single-user).

## Key Concepts
- **UEFI vs legacy BIOS**: UEFI uses GPT + a FAT **EFI System Partition (ESP)**; firmware reads a target `.efi` file directly — no mystery boot blocks, no loader strictly required. BIOS uses the 512-byte **MBR** boot block → second-stage loader.
- **GRUB**: default Linux boot loader (GRUB 2); reads `grub.cfg` from a regular filesystem at boot.
- **Boot loader job**: identify and load a kernel, present a menu, and marshal kernel arguments (e.g. `single`/`-s` → single-user mode).
- **Spontaneous processes**: kernel-started processes with low PIDs and `[bracketed]` names in `ps`; not configurable, no admin attention.
- **`init`/systemd = PID 1**: keeps the running service complement matched to the current mode.
- **Unit statuses**: `enabled` (autostart), `disabled` (autostart path off, still manually startable), `static` (no install section; only starts on demand or as a dependency), `masked` (administratively blocked), `linked`, `bad`.

## Mental Models
- **`Requires`/`Wants` ≠ ordering.** *Which* units activate is separate from *what order*. Ordering comes only from `Before`/`After`; absent those, units run in parallel (the whole point of systemd). Prefer `Wants` (loosest) over `Requires`.
- **"Enabled" really means "installed."** Enabling executes the unit's `[Install]` section (`WantedBy`/`RequiredBy`), wiring activation symlinks. If a service won't autostart, check it's enabled/symlinked.
- **Kernels install side-by-side, not in place.** A bad kernel patch → pick the previous kernel from the GRUB menu to recover.

## Anti-patterns
- **`rm -rf /` on a systemd UEFI box**: can destroy the system *at the firmware level* — UEFI vars are mounted read/write via `/sys` and get removed too.
- **Handcrafting `grub.cfg`**: distros regenerate it after updates and clobber your edits. Edit `/etc/default/grub` (+ `/etc/grub.d/40_custom`), then run `update-grub` / `grub2-mkconfig`.
- **Running MBR-specific tools on a GPT disk**: they misread the layout and corrupt it.
- **`systemctl mask` vs `disable`**: use `disable` for `enabled`/`linked` units; reserve `mask` for `static` units you must hard-block.

## Code Examples
```sh
# systemd day-to-day
systemctl list-units --type=service        # active services
systemctl list-unit-files --type=service   # all installed units + state
systemctl status -l cups                   # status + recent logs (-l = full lines)
systemctl enable --now cups                # wire autostart AND start now
systemctl disable cups; systemctl mask cups
systemctl isolate multi-user.target        # switch mode (activate target, deactivate others)
systemctl get-default; systemctl set-default multi-user.target   # boot mode (servers: no GUI)
systemctl add-wants multi-user.target my.local.service
systemctl daemon-reload                    # after editing unit files
```
```ini
# Minimal service unit (rsync.service)
[Unit]
Description=fast remote file copy program daemon
ConditionPathExists=/etc/rsyncd.conf
[Service]
ExecStart=/usr/bin/rsync --daemon --no-detach
[Install]
WantedBy=multi-user.target
```
- **What it demonstrates**: the three-section unit-file anatomy — `[Unit]` (metadata/deps), `[Service]` (how to run), `[Install]` (autostart wiring).

```sh
efibootmgr -v                  # inspect UEFI boot entries
sudo efibootmgr -o 0004,0002   # set boot order (drive then network)
gpart show                     # FreeBSD: inspect GPT partitions / find ESP
```

## Reference Tables
**`forking` service directives** (from `nginx.service`): `Type=forking` + `PIDFile` (daemon backgrounds itself, records PID); `ExecStartPre` (validate config / clear stale PID), `ExecStart`, `ExecReload=/bin/kill -s HUP $MAINPID`, `KillSignal=SIGQUIT`, `TimeoutStopSec` (then TERM then uncatchable KILL), `PrivateTmp=true` (isolated `/tmp` for security).

**Dependency directives** (`[Unit]`): `Wants` (soft, preferred) · `Requires` (strict; prereq failure kills service) · `Requisite` (must already be active) · `BindsTo`/`PartOf` (tighter) · `Conflicts` (negative).

## Worked Example
**Boot to multi-user, re-enable a disabled service.** A server is booting to `graphical.target` and CUPS is disabled. (1) `systemctl get-default` → `graphical.target`; fix with `systemctl set-default multi-user.target`. (2) `systemctl status -l cups` shows `Loaded: ... disabled; vendor preset: enabled` and `Active: inactive (dead)`. (3) `systemctl enable cups` creates the `multi-user.target.wants` symlink (and socket/path symlinks); `systemctl start cups` runs it now — or do both at once with `enable --now`. The status line's three facts to read: **Loaded** (enabled/disabled + vendor preset), **Active** (running/dead + when), and the tail **log entries**.

## Key Takeaways
1. Boot = firmware → loader → kernel → PID-1 daemon; you influence it via config files and kernel args, not interactively.
2. On Linux, learn systemd: units, unit files, `systemctl`, and targets — it standardizes what used to differ per distro.
3. Stock units live under `/usr/lib`; put your overrides in `/etc/systemd/system` (wins conflicts).
4. Activation set (`Wants`/`Requires`) is independent of ordering (`Before`/`After`); systemd parallelizes by default.
5. Edit `/etc/default/grub`, never `grub.cfg` directly; regenerate with `update-grub`/`grub2-mkconfig`.
6. UEFI/ESP/GPT is the modern path; keep BIOS/MBR knowledge for legacy and virtualized systems.
7. Recover a broken update by selecting the prior side-by-side kernel at the GRUB menu.

## Connects To
- **Ch 4**: process control & signals (KillSignal, MAINPID, single-user root shell).
- **Ch 5**: filesystem & mounting (why `/boot` holds only simple files).
- **Ch 6**: package management (packages ship their own unit files).
- **Ch 10**: logging (systemd's `journald`).
- **Ch 11**: kernel & drivers (kernel boot parameters).
