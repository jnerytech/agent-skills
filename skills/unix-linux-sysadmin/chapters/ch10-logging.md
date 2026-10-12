# Chapter 10: Logging

## Core Idea
Daemons, the kernel, and apps emit a torrent of log messages; the admin's job is **log management** — collect from many sources, provide a queryable interface, and manage retention/expiration. Two native systems coexist on Linux: the **systemd journal** (binary, indexed, `journalctl`) and **syslog/rsyslog** (text, facility/severity routing, network forwarding). Logs are the *first* place to look when something breaks.

## Frameworks Introduced
- **Three log-management subtasks**: collect (from varied sources) → query/filter/monitor → retain & expire (per legal/policy rules, with NTP-validated timestamps).
- **syslog facility.severity routing**: every message has a *facility* (source program) and *severity* (importance); selectors `facility.level → action` route them. This is syslog's core model.
- **rsyslog as event-stream processor**: inputs (`im*` modules) → filters/rules → outputs (`om*` modules). Each stage modular and configurable in `/etc/rsyslog.conf` (+`/etc/rsyslog.d/*.conf`, lexicographic order).
- **Centralized logging**: clients forward (`omfwd` over TCP/UDP, optionally TLS) to a central server (`imtcp`/`imudp`) that filters by type and writes site-wide files — required by PCI DSS/COBIT/ISO 27001 and broadly useful.

## Key Concepts
- **systemd journal**: `systemd-journald` collects from `/dev/log`, `/dev/kmsg`, stdout socket, journal API, and auditd; stores indexed binary. Default `Storage=auto` means **logs are lost on reboot** unless `/var/log/journal` exists — set `Storage=persistent`.
- **`journalctl`**: query the journal — `-u <unit>`, `-f` (follow, like `tail -f`), `-b 0` (current boot), `--since`/`--until`, `-n N`, `--disk-usage`, `--list-boots`.
- **Forward Secure Sealing (FSS)**: `Seal` option + `journalctl --setup-keys` makes journal entries cryptographically tamper-evident.
- **Facilities** (Table 10.2): `auth`/`authpriv` (sensitive — sudo uses authpriv), `cron`, `daemon`, `kern`, `mail`, `lpr`, `local0-7` (your programs), `user` (default).
- **Severities** (descending): `emerg` > `alert` > `crit` > `err` > `warning` > `notice` > `info` > `debug`. A level matches that level *and higher*; `=` = this only, `!` = except this and higher.
- **rsyslog config syntaxes**: sysklogd (traditional `selector action` — use for simple filters), legacy `$directives` (modules/daemon options), RainerScript (expressive filtering — recommended for rules).
- **Binary logs (don't manage)**: `wtmp` (logins/reboots — read with `last`), `lastlog` (last login per UID — read with `lastlog`), database transaction logs.

## Mental Models
- **Look at the logs first.** A crashing/refusing daemon or boot-time error almost always leaves hints in `/var/log` or the journal — check before deep debugging.
- **journal vs syslog: both run, for now.** The journal indexes/searches well but lacks rsyslog's input/output flexibility and mature network forwarding. Use rsyslog for routing/centralization; the journal for fast local queries. (Check `ForwardToSyslog` in journald.conf.)
- **Severity sets a floor.** Routing `auth.info` to a file also captures `auth.warning`, `auth.err`, etc. — everything at that level *and above*.
- **Make `/var/log` its own partition.** A runaway log can fill the disk and halt the system — true for cloud/VM instances too.

## Anti-patterns
- **Default journal `Storage=auto` with no `/var/log/journal`**: silently discards logs on reboot — "a real handicap." Create the dir or set `persistent`.
- **Rotating/compressing a log rsyslog has open**: "not healthy, unpredictable results." Send `HUP` first (rsyslogd closes/reopens files) — or use `logrotate`.
- **Legacy `$directives` for message-processing rules**: even rsyslog docs call it "extremely hard to get right" — use sysklogd or RainerScript for filtering.
- **Apps writing ad-hoc log files bypassing syslog**: the historical mess that makes log locations inconsistent across distros — funnel through syslog/journal where possible.
- **Forgetting NTP**: accurate timestamps are essential for correlating logs across hosts (and for compliance).

## Code Examples
```sh
# systemd journal
journalctl -u ssh                 # logs for a unit
journalctl -f                     # follow (live tail)
journalctl -b 0 -u ssh            # current boot, ssh only
journalctl --since=yesterday --until=now
journalctl -n 100 /usr/sbin/sshd  # last 100 from a binary
journalctl --disk-usage ; journalctl --list-boots
# persistent storage:
echo -e "[Journal]\nStorage=persistent" > /etc/systemd/journald.conf.d/storage.conf
systemctl restart systemd-journald

# rsyslog: reload after editing config
kill -HUP $(cat /var/run/syslogd.pid)
```
```
# sysklogd syntax (traditional): selector  action
kern.*                         -/var/log/kern.log     # dash = no fsync (faster)
auth,authpriv.*                /var/log/auth.log
*.*;auth,authpriv,cron,kern.none  -/var/log/syslog
*.*                            @@logs.admin.com       # @@ = TCP forward, @ = UDP

# RainerScript: filter on message properties
if $syslogfacility-text == 'auth' then {
  action(type="omfile" file="/var/log/auth.log")
}
module(load="ommail")
if $syslogseverity-text == 'crit' and $syslogfacility-text == 'kern' then {
  action(type="omfile" file="/var/log/kern-crit.log")
  action(type="ommail" server="smtp.admin.com" mailto="ben@admin.com"
         action.execonlyonceeveryinterval="3600")
}
```

## Reference Tables
**Key rsyslog modules**: `imuxsock` (local `/dev/log`), `imklog` (kernel), `imjournal` (journal integration), `imfile` (tail a text file into syslog — inotify mode), `imtcp`/`imudp` (network input), `immark` (periodic timestamps); `omfile` (write file — default), `omfwd` (forward to remote), `ommysql`/`omelasticsearch`/`omkafka` (DB/ELK/Kafka).

**Common log files** (`/var/log`): `messages`/`syslog` (main), `auth.log`/`secure` (authorization), `kern.log`, `cron`, `mail*`, `boot.log`, `dmesg` (kernel buffer), `dpkg.log`/`yum.log` (packages), `wtmp`/`lastlog`/`faillog` (binary, special tools).

**Forward actions**: `@host` = UDP:514, `@@host` = TCP:514, TLS via `gtls` netstream driver on port 6514.

## Worked Example
**Centralized logging: client forwards, server sorts.** *Client* (RainerScript): forward everything with sysklogd one-liner `*.* @@logs.admin.com`; pull Apache's text logs in via `imfile` (inotify mode, resumes after restart), tag them `apache-access`/`apache-error`, then `if $programname contains 'apache' then action(type="omfwd" Target="logs.admin.com" Port="514" Protocol="tcp")`. *Server*: `module(load="imtcp" MaxSessions="500") input(type="imtcp" port="514")`, then branch — `if $programname == 'apache-access' then action(type="omfile" file=".../access.log") else if ... 'apache-error' ... else action(type="omfile" file=".../syslog")`. TCP is more reliable than UDP but can still drop; use RELP for guaranteed delivery, and the `gtls` driver on port 6514 for TLS-authenticated transport (`authMode="x509/name"` validates the client cert's DNS subject). Site-wide files carry two timestamps: rsyslogd's receive time and Apache's original log time.

## Key Takeaways
1. Logs are the first debugging resource — for crashes, failed starts, boot errors, and security incidents.
2. Two native systems: the systemd journal (binary/indexed, `journalctl`) and rsyslog (text, facility/severity routing, network); both run, used for different strengths.
3. Set `Storage=persistent` so the journal survives reboots.
4. syslog routing = `facility.severity → action`; severity matches that level and higher; sudo uses `authpriv`.
5. rsyslog = inputs→filters→outputs via modules; use RainerScript for rules, sysklogd for simple filters, never legacy directives for filtering.
6. Centralize logs (TCP/TLS forwarding) for compliance and correlation; `HUP` rsyslog (or use logrotate) before rotating files; give `/var/log` its own partition; enable NTP.

## Connects To
- **Ch 2**: systemd/journald as part of the systemd suite.
- **Ch 3**: auth/authpriv logs from sudo, PAM.
- **Ch 4**: signals (HUP to reload rsyslog), tail -f vs journalctl -f.
- **Ch 28**: monitoring (logs feed alerting and the ELK stack).
- **Ch 27**: security (tamper-evident logs, retention, FSS).
