# Chapter 12: Printing

## Core Idea
Linux, FreeBSD, and macOS all use **CUPS** (Common UNIX Printing System) — a network/security-aware printing system that is, under the hood, a **web server speaking IPP (Internet Printing Protocol, HTTP-based)**. CUPS provides a browser GUI (port 631), legacy `lpr`/`lpq`/`lp` commands, and a filter pipeline that converts documents to each printer's format. Printing is low-priority for admins but high-priority for users — making it "just work" earns easy goodwill.

## Frameworks Introduced
- **The print pipeline**: `lpr` → `cupsd` queue → **filter chain** (reformat/convert/rasterize, guided by the printer's PPD) → **back end** (transmits to printer via USB/socket/IPP/etc.) → printer.
  - CUPS picks the filter chain by lowest total cost: `.types` files identify the doc's MIME type, the PPD says what the printer accepts, `.convs` files give conversion filters + costs.
- **Queue control = two ends**: the *submission* end (`accept`/`reject` — controls whether new jobs may enter) and the *exit/printer* end (`cupsenable`/`cupsdisable` — controls whether queued jobs print).
  - When to use: `reject` for extended downtime (don't accept hopeless jobs); `cupsdisable` for brief, user-invisible interruptions (toner change).
- **Command lineage**: CUPS bundles BSD (`lpr`/`lpq`/`lprm`/`lpc`), System V (`lp`/`lpadmin`/`lpstat`/`cancel`/`accept`/`reject`), and native (`cupsenable`/`lpoptions`/`lpinfo`) commands.

## Key Concepts
- **CUPS = web server**: clients are web clients; admin via browser at `http://printhost:631` (or `https://...:443`). Config files resemble Apache's.
- **PPD (PostScript Printer Description)**: per-printer capabilities file — used even for *non*-PostScript printers.
- **`lpadmin` vs `lpoptions`**: `lpadmin` = system-wide tasks (add/remove printers, quotas, access); `lpoptions` = per-user defaults/printer instances.
- **Printer instances**: one physical printer used multiple ways, e.g. `Phaser_6120/2up` for 2-up draft printing.
- **Network printer browsing**: every machine runs a `cupsd`; servers broadcast their printers every 30s so clients auto-discover. Broadcasts don't cross subnets — use `BrowsePoll`/`BrowseRelay` slave servers.
- **Printer URIs**: `parallel:/dev/lp0`, `socket://192.168.0.12`, `ipp://host/ipp`, `lpd://host/ps`, `usb://...`, `serial:/dev/ttyS0?baud=9600`.

## Mental Models
- **Mnemonic for queue ends**: "if CUPS *rejects* a job, you can't *inject* it" (submission side). Also: accept/reject act on *jobs*; enable/disable act on *printers*.
- **CUPS auto-disables a flaky printer** (dislodged cable). After fixing, `cupsenable` it — `lpstat` reminds you if you forget.
- **Restart `cupsd` after editing `cupsd.conf`** — it reads config only at startup (GUI changes restart it automatically).

## Anti-patterns
- **`lpr --help` / `lp --help`**: emulate legacy tools "too well" — they print errors, not usage. Use man pages.
- **Forgetting to re-`cupsenable` after a fix**: jobs silently stall; check `lpstat`.
- **Editing config without restarting `cupsd`**: changes don't take effect.
- **Relying on a network printer's web console to fix it when it's down**: that console needs the printer up on the network — unavailable exactly when you need it.

## Code Examples
```sh
lpr foo.pdf /tmp/testprint.ps          # submit to default printer
lpq ; lprm <jobid> ; lpstat -t         # queue status / remove job / overall status
export PRINTER=name ; lpoptions -d name   # set default printer (per-user)
lpoptions -p Phaser_6120/2up -o number-up=2 -o job-sheets=standard   # create instance
lpr -P Phaser_6120/2up biglisting.ps

# Add printers (lpadmin: -p name, -E enable, -v device-URI, -m PPD)
sudo lpadmin -p groucho -E -v parallel:/dev/lp0 -m pxlcolor.ppd
sudo lpadmin -p fezmo -E -v socket://192.168.0.12 -m laserjet.ppd
sudo lpadmin -x fezmo                  # remove a printer
lpinfo -v                              # list visible devices + supported URI types

# Queue control (two ends)
sudo cupsdisable groucho               # stop printing (exit end) — brief outage
sudo reject corbet                     # refuse new jobs (submission end) — long outage

# Troubleshooting
systemctl restart org.cups.cupsd.service
/usr/lib/cups/backend/usb              # run a back end directly to verify the connection
telnet printhost 631                   # check the cupsd is reachable
```

## Reference Tables
**Filter-selection files**: `mime.types` (identify input MIME type, e.g. `pdf` if ext `.pdf` or starts with `%PDF`) · `mime.convs` (conversion rules with cost, e.g. `application/pdf application/postscript 33 pdftops`) · PPD `*cupsFilter:` line (final filter to printer-native format). CUPS chooses the lowest-total-cost chain.

**Network-server `cupsd.conf` changes**: add `Allow From <netaddress>` in `<Location />`, set `BrowseAddress 192.168.0.255:631`, restart `cupsd`.

**Logs** (in `/var/log`, locations set in `cupsd.conf`): page log (pages printed), access log, error log — same format as Apache's.

## Worked Example
**Disable a printer for a toner change vs for a week of repair.** The queue has two controllable ends. For a *brief* toner swap that should be invisible to users: `sudo cupsdisable groucho` — new jobs still queue, they just wait; re-enable with `cupsenable groucho` and they flow. For *extended* downtime (printer shipped for repair): `sudo reject groucho` — the queue refuses new submissions so users get immediate feedback instead of jobs piling up with no hope of printing. The rule: `reject` (submission end) for long outages so you don't "accept jobs that have no hope of being printed"; `cupsdisable` (exit end) for short, transparent ones. Remember accept/reject act on *jobs*, enable/disable act on *printers*.

## Key Takeaways
1. CUPS is the universal printing system and is fundamentally a web server speaking IPP — manage it at `:631` or via `lp*` commands.
2. The pipeline is queue → filter chain (PPD + MIME cost-based selection) → back end → printer.
3. Control the queue at two ends: `accept`/`reject` (submissions) and `cupsenable`/`cupsdisable` (printing).
4. `lpadmin` for system-wide config (add/remove/quotas), `lpoptions` for per-user defaults and printer instances.
5. CUPS daemons auto-discover each other's printers via 30s broadcasts; cross subnets with BrowsePoll/BrowseRelay.
6. Restart `cupsd` after config edits; debug by running back ends directly and checking the three CUPS logs.

## Connects To
- **Ch 10**: logging (CUPS access/error/page logs, like Apache).
- **Ch 13**: TCP/IP — network printers need IP/netmask (via DHCP or static console config).
- **Ch 19**: web hosting — CUPS config mirrors Apache's syntax.
- **Ch 21/22**: file/print sharing (SMB printers).
