# Chapter 1: Where to Start

## Core Idea
This book is an orientation guide + quick-reference handbook focused on **serious, professional administration of enterprise servers and networks** — not single-machine setup. It teaches the major administrative subsystems, their tradeoffs, and rules of thumb that scale as complexity and heterogeneity grow.

## Frameworks Introduced
- **The essential duties of a sysadmin**: the recurring job description used to frame the whole book.
  - When to use: deciding what to learn, staff, or automate; writing a sysadmin job spec.
  - How: cover all of — controlling access, adding hardware, automating tasks, overseeing backups, installing/upgrading software, monitoring, troubleshooting, maintaining local documentation, vigilantly monitoring security, tuning performance, developing site policies, working with vendors, and fire fighting. At least one person must understand *all* components even when work is split across a team.
- **"Additional software = additional attack surface"**: the security lens applied to every install decision.
  - When to use: every package install, especially on general-purpose distros.
  - How: install only what's necessary; minimalist distros (CoreOS, Alpine) reduce footprint.
- **Vendor/distribution due-diligence questions**: choosing a distro is choosing a vendor relationship.
  - How: ask — alive in 5 years? stays on top of security patches? active community + docs? will the vendor talk to me and at what cost?

## Key Concepts
- **Linux distribution**: the Linux kernel + packages making up all runnable commands. All share kernel lineage; differ in package format/type/count, focus, support, popularity.
- **Man page sections**: numbered categories (1 user cmds, 2 syscalls, 3 library, 4 drivers/protocols, 5 file formats, 6 games, 7 misc, 8 sysadmin cmds, 9 kernel internals).
- **Continuous delivery**: automatically releasing software to users at a regular cadence as it's developed.
- **IEC binary units**: kibi/mebi/gibi (Ki/Mi/Gi) = powers of 2; metric kilo/mega/giga = powers of 10. RAM is power-of-2; network bandwidth is power-of-10.
- **Reference implementation**: software "implemented by a trusted source according to the RFC specification."

## Mental Models
- **Think of the command line as non-negotiable** — GUI admin tools on UNIX/Linux remain rudimentary vs. the underlying software. Master `vim` (run `vimtutor`); it's the single best productivity gain. Use `nano` discreetly.
- **Be a polyglot programmer** — the dev/admin line is blurring. Default scripting picks: Bash (duct tape), Python (readable, big community), Ruby (equivalent to Python — preference call). Learn `expect` for driving interactive programs.
- **Google first** — unless looking up an exact command/file format, search the web before asking a forum.

## Anti-patterns
- **`curl https://… | sudo sh`**: prototypical rookie blunder — root shell runs even if curl delivers a *partial* script on a network glitch. Fix: save script to a temp file, verify download succeeded, then run as a separate step.
- **Insecure (HTTP) install URLs**: trivially hijacked; you'll run attacker code as root. Always prefer `https:`; an HTTP→HTTPS *redirect* is no safer than plain HTTP (initial exchange is interceptable) — but try substituting `https` for `http` yourself, it often just works.
- **Cluttered general-purpose distros**: unused packages = vulnerabilities + admin anguish.

## Code Examples
```sh
which gcc          # is a binary in my PATH? -> /usr/bin/gcc
whereis name       # broader system dirs, PATH-independent
locate signal.h    # query prebuilt filesystem index (updatedb refreshes it via cron)
rpm -q python      # Red Hat: is package installed + version
rpm -qf /etc/httpd # Red Hat: which package owns this file
dpkg-query -S /etc/apache2   # Debian/Ubuntu: which package owns this file
pkg which /usr/local/sbin/httpd   # FreeBSD: which package owns this file
man -k translate   # == apropos: search man one-liners by keyword
```
- **What it demonstrates**: the cross-distro "is X installed / who owns this file" toolkit.

```sh
# Build from source — universal C project sequence
git clone https://github.com/the-tcpdump-group/tcpdump.git && cd tcpdump
git checkout tags/tcpdump-4.7.4 -b tcpdump-4.7.4
./configure --help        # discover options; --prefix=DIR changes install root (default /usr/local)
./configure && make && sudo make install
```
- **What it demonstrates**: the `configure / make / make install` pattern common to all UNIX/Linux C software.

## Reference Tables
**Example systems used throughout the book** (your mental "test matrix"):

| Family | Systems | Package tool |
|---|---|---|
| Debian lineage | Debian 9 "Stretch", Ubuntu 17.04 | APT (`apt-get`), `dpkg` |
| Red Hat lineage | RHEL 7.1, CentOS 7.1 | `yum`, `rpm` |
| BSD | FreeBSD 11.0 (complete OS, not just kernel) | `pkg` |

Install `tcpdump`: `apt-get install tcpdump` (Deb/Ubuntu) · `yum install tcpdump` (RHEL/CentOS) · `pkg install -y tcpdump` (FreeBSD).

## Worked Example
**Adding new software you can't name yet.** The skill is translating intent → canonical package name. "I want `locate`" → install the **mlocate** package. "I need `named`" → install **BIND**. Procedure: (1) `which <cmd>` to check if already present; (2) if not, Google "`<cmd>` command" or the OS package index to find the package name; (3) install with the OS package manager; (4) prefer the OS package over a web installer because packages are trackable, upgradable, removable — accepting that OS packages often trail the upstream version by a release or two.

## Key Takeaways
1. The book's scope is *enterprise* administration that scales under load, partitions, and attacks — optimize for recovery and growth, not first-boot.
2. Memorize the duties list; it's the contract for the whole role and the rest of the book.
3. Command line + `vim` + a scripting language (Bash/Python/Ruby) are table stakes.
4. Treat every install as attack surface; minimize it.
5. Choosing a distro is a multi-year vendor bet — judge longevity, patch cadence, community, support cost.
6. Never pipe an unverified web script into a root shell; never trust HTTP install URLs.
7. Know the cross-distro "who owns this file / is it installed" commands by heart.

## Connects To
- **Ch 6**: software installation & package management (the deep version of §1.10).
- **Ch 7**: scripting & the shell (the automation duty).
- **Ch 9 / Ch 25**: cloud (recommended default host) and containers (minimalist-distro trend).
- **Ch 27 / Ch 29**: security and performance duties.
- **Ch 31**: site policy and politics (the "developing site policies" duty).
