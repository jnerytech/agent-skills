# Chapter 6: Software Installation and Management

## Core Idea
Installing, patching, and provisioning software is most of the job. The win is **automation + packaging**: PXE/kickstart/preseed for hands-free OS installs, and dual-layer package managers (low-level `rpm`/`dpkg` + high-level `yum`/`apt`) that handle dependencies, atomic install/rollback, and repository-based updates. "Localization" = adapting a stock distro to your conventions.

## Frameworks Introduced
- **Network/unattended installation pipeline**: DHCP → TFTP → PXE boot loader → fetch OS files (HTTP/NFS/FTP) → answer-file driven install. Worth it for >~10 systems.
  - Red Hat: **kickstart** (`ks.cfg`, scripts Anaconda). Debian/Ubuntu: **preseed** (`preseed.cfg`, drives `debconf`). FreeBSD: **bsdinstall** + `installerconfig`.
  - **Cobbler** wraps PXE+DHCP+DNS+TFTP and adds templates/snippets to share config across host profiles.
- **Two-layer package management**: low-level installer (`rpm`, `dpkg`) operates on a single package file; high-level metapackage manager (`yum`/DNF, `apt`) finds, downloads, resolves dependencies, and updates from repositories.
- **Repository structure**: *release* (snapshot target to update toward) → *component* (main/universe/multiverse/restricted) → *architecture* (x86_64…) → *package* (versioned independently).

## Key Concepts
- **PXE (Preboot eXecution Environment)**: NIC-ROM mini-OS that netboots via a standard BIOS API — hardware-independent. PXELINUX (SYSLINUX) is the common boot system; iPXE adds wireless.
- **Package**: precompiled binaries + dependency info + config templates; install is as-atomic-as-possible (backable-out); won't clobber local config (backs it up or ships `.rpmnew`/example).
- **Dependency hell**: can't update a package due to version conflicts among its dependencies — the motivation for `apt`/`yum`.
- **Package version ≠ software version** — maintainers backport and renumber (e.g. `docker-engine-1.13.0` package ships docker 1.13.1).
- **`apt update` vs `yum update` trap**: `apt update` refreshes the package *cache*; `yum update` *upgrades every package* (= `apt upgrade`). `yum -C` skips cache validation.

## Mental Models
- **Don't reinvent installs — drive the vendor installer with an answer file.** kickstart/preseed are scripting interfaces to the *same* installer humans use; generate the answer files programmatically (pykickstart, debconf dumps) from a master config.
- **Day-to-day = high-level tools; occasionally drop to low-level.** Use `apt`/`yum` for everything routine; reach for `rpm`/`dpkg` only to inspect or force-handle a single file.
- **Build your own packages for localization.** Package your configs/local apps with `fpm`; use the dependency mechanism to create meta-packages ("install X pulls in everything") and to auto-upgrade fleets.

## Anti-patterns
- **`rpm -U --force`** to bypass dependency errors: "nothing like a broken SSH on a remote system to ruin a sysadmin's morning." Fetch the dependent packages too; `rpm -q --whatrequires` *before* upgrading.
- **Cleartext `rootpw` in kickstart / plaintext passwords in preseed**: answer files live on HTTP servers and get discovered. Use `--iscrypted` / hashed values (`openssl passwd -1`); better, change the password post-boot so the fleet doesn't share one.
- **Editing the system file tree by hand instead of repackaging**: accept default file locations; package your changes.
- **Unattended `apt upgrade -y` straight from a distro mirror**: "playing with fire"; do automated upgrades only against *your own* tested repo, and randomize cron times across the fleet.
- **`dselect`**: ignore it; stick with `apt`.

## Code Examples
```sh
# Low-level: single package files
rpm -i pkg.rpm ; rpm -U pkg.rpm ; rpm -e pkg ; rpm -qa          # install/upgrade/erase/query-all
rpm -q --whatrequires openssh         # who depends on this before upgrading
rpm -U openssh-*                      # rpm sorts multiple files by dependency
dpkg --install ./nvi_*.deb ; dpkg -l | grep -i http            # install / list (ii = installed)

# High-level: repositories + dependency resolution
apt update && apt install sudo        # refresh cache, then install/upgrade (can upgrade in-use pkgs)
apt upgrade                           # = apt-get dist-upgrade --with-new-pkgs
apt-get autoclean                     # prune /var/cache/apt
yum install foo ; yum update 'lib*'   # install; update glob (quote it!) — yum update = upgrade ALL

# FreeBSD
pkg install -y tcpdump                # prefer binary packages over ports
uname -r                              # 11.0-RELEASE  (which branch)
freebsd-update fetch install          # update base system (RELEASE branch only)
```
```
# kickstart ks.cfg (Red Hat) — 3 sections: commands / %packages / %pre+%post
text
url --url http://installserver/redhat
rootpw --iscrypted $6$NaCl$...        # NEVER cleartext
clearpart --all --initlabel
part / --fstype ext3 --size 4096
part /var --fstype ext3 --size 1 --grow
%packages
@ GNOME
mylocalpackage
```

## Reference Tables
**Choosing the installer by distro**: Red Hat/CentOS → kickstart (`ks.cfg`, Anaconda; supports LVM, firewall). Debian/Ubuntu → preseed (`preseed.cfg`, debconf; recipes: `atomic`/`home`/`multi`). Ubuntu also accepts kickstart but missing LVM/firewall — prefer the Debian installer. FreeBSD → `installerconfig`.

**`/etc/apt/sources.list` line** = `type uri distribution [components]`, e.g. `deb http://archive.ubuntu.com/ubuntu xenial main restricted universe multiverse`. Always include `security.ubuntu.com`. Run `apt update` after edits.

**FreeBSD software tiers**: base system (one unit, `freebsd-update`) · binary packages (`pkg`, preferred) · ports (source build, for custom compile options). Add-ons install under `/usr/local`. Branches: CURRENT (dev) / STABLE (next release, adventurous) / RELEASE (production, security+serious-bug fixes only).

## Worked Example
**Patch OpenSSH on RHEL without breaking it.** `sudo rpm -U openssh-6.6.1p1-33.el7_2.x86_64.rpm` fails: "openssh = 6.6.1p1-23 is needed by openssh-clients / openssh-server." The right move is *not* `--force`. (1) Discover the dependents up front: `rpm -q --whatrequires openssh` → openssh-server, openssh-clients. (2) Fetch updated versions of all of them. (3) `sudo rpm -U openssh-*` — rpm topologically sorts the files by dependency and installs them together. (4) Verify `rpm -q openssh`. Note rpm does *not* restart sshd — `systemctl restart sshd` to finish. (In real life you'd just let `yum`/`apt` resolve this automatically — that's the whole point of the high-level tools.)

## Key Takeaways
1. Automate OS installs with PXE + kickstart/preseed/bsdinstall once you pass ~10 machines; generate answer files programmatically; never store plaintext passwords in them.
2. Cobbler ties PXE/DHCP/DNS/TFTP together with reusable templates and snippets.
3. Packages give atomic, dependency-aware, rollback-capable installs that respect local config.
4. Low-level (`rpm`/`dpkg`) handles one file; high-level (`yum`/`apt`) handles repos + dependencies — use high-level daily.
5. Mind the verbs: `apt update`=refresh cache, `apt upgrade`=install updates; `yum update`=upgrade everything.
6. Build your own packages (`fpm`) and meta-packages to distribute localizations and drive fleet upgrades; do auto-updates only from your own tested repo with randomized timing.

## Connects To
- **Ch 2**: PXE boot loaders and the boot process.
- **Ch 23**: configuration management (the scaled-up successor to localization scripts/packages).
- **Ch 25/26**: containers and CI/CD (image-based provisioning beyond package managers).
- **Ch 27**: security (timely patching is a core duty; trust of update sources).
