# Chapter 28: Monitoring

## Core Idea
A commitment to monitoring is **the** distinguishing mark of a professional sysadmin — every system goes onto the monitoring platform *before* it goes live. The universal pipeline: **harvest data → evaluate against rules → react** (notify/act/store). Modern monitoring recognizes that *all monitoring data is time-series data*, so the field has shifted from first-gen threshold-alerters (Nagios) to time-series stores (Graphite/Prometheus). Good monitoring catches small problems before they snowball and lets you fix things at your convenience, not at 3 a.m.

## Frameworks Introduced
- **The monitoring pipeline**: (1) instrumentation/data collection, (2) intake & processing (apply rules), (3) reaction — notifications, dashboards, automated actions, storage. Even a 5-line Perl cron script (`uptime` → if load>5 → mail) embodies all three: data, evaluation, reaction.
- **Three data types**: **real-time metrics** (numbers/booleans tested against thresholds → alerts), **events** (log entries / push notifications — state changes), **aggregated historic trends** (time-series for analysis and baselines).
- **The monitoring culture tenets**: if someone depends on it, monitor it; monitor all HA constructs (don't learn the primary failed only when the backup also fails); monitoring is not optional; everyone responds to alerts (not just ops); **fix alerts, don't suppress them**.
- **Time-series rollup**: keep recent data at fine resolution and summarize as it ages (e.g. 10s for 12h, 1min for 7d, 10min for 1y) — controls storage growth while preserving baselines.

## Key Concepts
- **Notifications must be actionable** — every recipient must *potentially do something*. Purely-informational notifications train people to ignore the system. Escalate beyond email: SMS for critical, ChatOps for less-critical.
- **Dashboards**: selective (most important metrics), context cues (red = problem, grouping = relationships), charts for at-a-glance assessment. Most collected data never reaches a dashboard.
- **Platform categories**: real-time/threshold (Nagios, **Icinga 2** preferred, Sensu — first-gen, losing favor) vs **time-series** (Graphite, **Prometheus** [authors' favorite], InfluxDB, Munin) vs charting (**Grafana** — DB-agnostic, 30+ backends, prettier).
- **Data collection front ends**: **StatsD** (UDP, ingests/calculates arbitrary stats, modular backends), **collectd** (system-stats daemon, 100+ plugins, feeds Graphite/Icinga), **sysdig**/**dtrace** ("Wireshark for the kernel" — deep syscall/process tracing; sysdig is container-aware).
- **SNMP**: standard but baroque protocol for *network-device* monitoring; data in MIBs as OIDs (e.g. `sysUpTime` = `1.3.6.1.2.1.1.3`); ops are get/get-next/set/trap; "community string" = obfuscated password (use SNMPv3). Treat it as a low-level last resort for dumb devices — get data out fast into a real platform; don't run an SNMP agent on UNIX servers anymore (use collectd).
- **Security monitoring**: FIM (file integrity — checksum vs known-good baseline: Tripwire/OSSEC/mtree) + IDS (HIDS like OSSEC, NIDS like Snort).

## Mental Models
- **Monitoring outage > service outage** for some shops — "without monitoring they'd have no idea what was happening anyway." Treat the telemetry system as critical infrastructure.
- **The hard part of collection is knowing what to ignore.** Over-collection loads the system and drowns important signals in noise — collect only data with a clear, actionable purpose, and continually re-evaluate.
- **If you can get it from the command line, you can monitor it.** A few lines of parsing glue (Perl one-liner on `uptime`, etc.) turns any command output into a metric — but prefer reading values directly from the kernel (`/proc`, `sysctl`) when possible.
- **A ping proves the network path + kernel are up, nothing about higher-level software.** Pings are cheap (every ~10s), but a busy gateway may drop them — collect as binary got-through/didn't events and roll up into % packet loss; don't alarm on the first miss.
- **FIM/HIDS alerts are only as useful as the attention paid.** Don't "set and forget" — auto-open trouble tickets for HIDS alerts and monitor for unresolved ones.

## Anti-patterns
- **Leaving systems unmonitored** until an angry user calls — or **disabling after-hours notifications** because they're bothersome: fire-fighting + bad reputation.
- **Purely informational notifications**: train staff to ignore the system — make every notification actionable.
- **Suppressing noisy/false-positive alerts instead of tuning them**: spurious alerts make everyone ignore monitoring — fix the alert.
- **Over-collecting data with no actionable purpose**: noise that obscures real signals and burdens systems.
- **Running an SNMP agent on a modern UNIX server**: "all smoke and no fire" — use collectd; reserve SNMP for network gear.
- **Building your own monitoring stack** when an outsourced/SaaS option fits: usually cheaper and more reliable for common app/server sets.

## Code Examples
```sh
# Simplest possible monitor: data -> evaluate -> react
loadavg=$(uptime | perl -anF'[\s,]+' -e 'print $F[10]')   # parse 1-min load
[ "$(echo "$loadavg > 5.0" | bc)" = 1 ] && mail -s "Load high" dan@admin.com </dev/null

# Submit a metric to StatsD (UDP, port 8125): name:value|type (c=count, g=gauge)
echo "sample.count:1|c" | nc -u -w0 statsd.admin.com 8125

# Read values directly from the kernel (preferred over parsing commands)
cat /proc/loadavg                 # Linux
sysctl -n vm.loadavg              # FreeBSD

# System monitoring commands
sar -n DEV 2 30                   # network interface stats every 2s, 30 times
df / du / free / iostat / lsof / mpstat / vmstat   # disk/mem/io/cpu

# SNMP (network devices only): sysUpTime OID
# 1.3.6.1.2.1.1.3 = iso.org.dod.internet.mgmt.mib-2.system.sysUpTime
```
```ini
# collectd: continuous system-stats daemon  (/etc/collectd/collectd.conf)
Hostname client1.admin.com
Interval 30
LoadPlugin cpu
LoadPlugin df
LoadPlugin interface
LoadPlugin load
LoadPlugin memory
LoadPlugin rrdtool
<Plugin rrdtool>
  DataDir "/var/lib/collectd/rrd"
</Plugin>
```

## Reference Tables
**Platform choices**: real-time (Nagios / **Icinga 2** / Sensu — threshold alerting) · time-series (Graphite / **Prometheus** / InfluxDB / Munin) · charting (**Grafana** — DB-agnostic) · commercial (Datadog, SignalFx, Sysdig Cloud, SolarWinds) · hosted (StatusCake — external view of public services).

**Collection tools**: StatsD (generic UDP submission `name:value|type`), collectd (system daemon, 100+ plugins), sysdig/dtrace (kernel+process tracing), per-command parsing glue.

**Monitoring commands**: `df`/`du` (disk), `free` (memory), `iostat` (disk perf), `lsof` (files/ports), `mpstat` (per-CPU), `vmstat` (process/cpu/mem), `sar` (everything, portable).

**Security monitoring**: FIM = Tripwire / OSSEC / mtree (checksum vs baseline). IDS = OSSEC (HIDS, broad) / Snort (NIDS) / AIDE (Linux FIM).

## Worked Example
**Turn any command into a monitored metric, end to end.** You want the 1-minute load average in Grafana. (1) **Extract**: `uptime` prints `... load average: 1.20, 1.41, 1.88`; a Perl one-liner splits on spaces/commas and prints field 10 → `1.20`. (2) **Submit**: wrap it in a script that uses a StatsD client library (preferred over hand-rolling `nc`, since libraries are less brittle and clarify intent): `Net::Statsd::gauge(hostname.'.loadAverage' => $loadavg)`. (3) **Store/roll-up**: configure Carbon (`storage-schemas.conf`) to keep `^stats.*` at 10s for 12h, 1min for 7d, 10min for 1y, and `storage-aggregation.conf` to summarize correctly — *sum* for counts/errors, *average* for load/utilization (getting the aggregation method wrong gives misleading rollups). (4) **Visualize**: point Grafana at Graphite. Better still, read load directly from `/proc/loadavg` instead of parsing `uptime` — same result, less brittle. The whole point: monitoring is just data → evaluate → react, and *anything* on the command line can feed it.

## Key Takeaways
1. Monitor everything anyone depends on, *before* it goes live; treat the monitoring system as critical infrastructure.
2. The pipeline is harvest → evaluate against rules → react; all monitoring data is time-series — prefer time-series platforms (Prometheus/Graphite) + Grafana.
3. Make every notification actionable, escalate appropriately (SMS/ChatOps), and tune (don't suppress) noisy alerts.
4. Collect only data with a clear actionable purpose; the hard part is knowing what to ignore.
5. Anything on the command line is monitorable (parse output or read `/proc`/`sysctl`); use StatsD/collectd to feed metrics in at scale.
6. Layer in security monitoring (FIM + HIDS/NIDS) and feed its alerts into tickets/dashboards; reserve SNMP for dumb network devices.

## Connects To
- **Ch 29**: performance analysis (the metrics monitoring collects — load, CPU, memory, I/O).
- **Ch 10**: logging (log monitoring, aggregation, OSSEC log analysis).
- **Ch 27**: security (FIM, HIDS/NIDS, OSSEC, intrusion detection).
- **Ch 26/31**: CI/CD & DevOps (application/APM monitoring, ChatOps, everyone responds).
- **Ch 13**: networking (ping, SNMP, network status monitoring).
