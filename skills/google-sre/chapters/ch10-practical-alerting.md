# Chapter 10: Practical Alerting from Time-Series Data
*Authors: Jamie Wilkinson (edited by Kavita Guliani)*

> "May the queries flow, and the pager stay silent." — Traditional SRE blessing

## Core Idea
Replace per-target check scripts with **mass collection of time-series plus centralized rule evaluation**: export every metric in a common format, scrape it cheaply, and compute charts and alerts with simple arithmetic over labeled vectors. This decouples monitoring cost from service size, so maintenance scales sublinearly.

Monitoring is the bottom layer of the **Service Reliability Hierarchy** (Part III intro: Monitoring → Incident Response → Postmortem/Root-Cause Analysis → Testing → Capacity Planning → Development → Product). Without it "you're flying blind."

## Frameworks Introduced
- **Borgmon time-series alerting model (white-box)**: targets expose metrics over HTTP (`/varz`); Borgmon scrapes them, stores labeled time-series in RAM, evaluates rules that produce new time-series, and sends alerts to Alertmanager. (Open source descendants: **Prometheus**, Riemann, Heka, Bosun.)
  - When to use: any fleet too large to page on single-machine failures; you want to alert on high-level service objectives but keep drill-down granularity.
  - How: (1) instrument every binary with an exported-variable interface (one declaration per metric); (2) discover targets via service discovery (e.g. BNS); (3) scrape at fixed intervals, spread over the interval so targets are not polled in lockstep; (4) record synthetic per-target variables (name resolved? responded to collection? responded to health check? collection finish time); (5) write aggregation rules (sum of rates); (6) write alert rules with a minimum duration; (7) route via Alertmanager.
  - Why it works: a common data exposition format avoids subprocess and connection-setup costs; collection history is reusable for alert computation; rules are abstracted over a common format, so new services arrive "ready" with library templates.
  - Failure mode: schemaless `varz` decouples variable definition from rule use — renaming a variable silently breaks rules. Mitigate with rule generators/validators and change management.
- **Hierarchical / sharded monitoring topology**: Borgmon can scrape other Borgmon via a streaming protocol (cheaper than text varz).
  - When to use: collecting globally from all tasks would be a scaling bottleneck and a single point of failure.
  - How: typical = one Borgmon per datacenter/cluster + two or more global Borgmon (diversity across maintenance zones). Very large services add a scraping-only layer below a DC aggregation (rule-evaluation) layer; global layer may split into rule evaluation and dashboarding. Upper tiers filter what they stream so per-task series don't flood the global arena.
- **Sum of rates, not rate of sums**: compute `rate()` per task, then aggregate with `sum without instance`.
  - Why: defends against counter resets (task restarts) and missing collections.
- **Counters over gauges**: prefer monotonically increasing counters; gauges lose events that happen between samples.
- **Rule naming convention `level:variable:operation`**: e.g. `task:http_requests:rate10m`, `dc:http_errors:ratio_rate10m` — aggregation level, variable name, and the operation that created it.
- **Alert with a "for" duration**: an alert goes *pending* when the rule is true and *fires* only after it stays true for the minimum duration — typically ≥ two rule-evaluation cycles — to suppress flapping and missed-collection false alerts.
- **White-box + black-box pairing (Prober)**: Prober runs protocol checks (validating payloads, exporting latency histograms as time-series) against both the load-balanced frontend and the per-datacenter backends behind it.
  - When to use: always — white-box only shows queries that arrived; DNS failures and crashed-server losses "never make a sound."
  - How: probe both the VIP (e.g. www.google.com) and each DC's servers to tell "traffic still served despite DC failure" vs. "isolate the edge where failure occurs," and to suppress redundant alerts.
- **Separation of rules from targets + templates**: same rule sets apply to many targets; macro-like templates form reusable libraries; unit/regression test rules with synthesized time-series; CI packages and ships config, and each Borgmon validates before accepting.
  - Two library classes emerged: (a) templates codifying the varz schema of a code library (HTTP server, memory allocation, storage client, generic RPC); (b) aggregation templates that model topology from task → job → shard → datacenter → global, following **shared fate**.

## Key Concepts
- **varz**: plain-text HTTP page of space-separated key/value exported variables; one fetch collects all metrics from a target.
- **Map-valued variable**: a variable with labels exporting a table/histogram, e.g. `http_responses map:code 200:25 404:0 500:12`.
- **Time-series arena**: fixed-size in-memory block with GC expiring oldest entries; periodically checkpointed and archived to the **TSDB** (slower, cheaper, larger).
- **Horizon**: span between newest and oldest entries in the arena; ~12 hours for DC/global Borgmon (a "magic number": enough to debug an incident in RAM).
- **Labelset / variable expression**: a time-series name is a set of `key=value` labels; required: `var`, `job`, `service`, `zone` (plus `instance` per target).
- **Vector**: result of a labelset query — a slice/cross-section of the multidimensional matrix; add `[10m]` for a time range.
- **Synthetic variables**: Borgmon-generated per-target health signals; collection failure itself becomes an alertable signal.
- **Alertmanager**: central service receiving Alert RPCs; inhibits alerts when others are active, deduplicates across Borgmon with identical labelsets, fans in/out by labelset.
- **Label uses**: breakdowns of data (HTTP code), source of data (instance/job), locality/aggregation (zone, shard).
- **Alert routing**: page-worthy → on-call; important-but-subcritical → ticket queue; everything else → informational dashboards.

## Mental Models
- Think of Borgmon as "really just a programmable calculator, with some syntactic sugar that enables it to generate alerts"; collection and storage are necessary evils.
- Think of a time-series as a 1-D matrix of numbers over time that becomes multidimensional as labels are added; queries slice it along the **time axis** (history) and the **space axis** (label subsets).
- Use collection failure as a signal rather than designing for SNMP-style robustness: the system is already robust to network/machine failure, so a failed scrape is just another input.
- Ensure monitoring maintenance cost scales **sublinearly** with service size — the recurring SRE theme for all sustaining work.

## Anti-patterns
- **Alerting on single-machine failures at scale**: too noisy to be actionable; design for robustness and aggregate/prune outliers instead.
- **Custom check scripts forked per target**: subprocess and connection overhead, duplicated config, alerting divorced from trend visualization.
- **Rate of sums**: breaks on counter resets and missed collections.
- **Gauges for event counts**: miss activity between samples.
- **Aggregating without dropping `instance`**: Borgmon cannot sum rows that still differ by instance label.
- **Collecting everything globally in one Borgmon**: scaling bottleneck + SPOF.
- **White-box only**: you can only alert on failures you expected; you miss what users see.
- **Untested rule logic**: high-level config languages invite complexity; test with synthesized series.

## Code Examples
```
% curl http://webserver:80/varz
http_requests 37
errors_total 12
```
What it demonstrates: the varz exposition format — one HTTP fetch returns all metrics.

```
{var=http_requests,job=webserver,instance=host0:80,service=web,zone=us-west}
{var=http_requests,job=webserver,service=web,zone=us-west}[10m]
```
What it demonstrates: a fully specified variable expression; dropping `instance` returns a vector of all matching tasks; `[10m]` returns 10 minutes of history (10 points at 1-minute collection).

```
rules <<<
  # Compute the rate of requests for each task from the count of requests
  {var=task:http_requests:rate10m,job=webserver} =
    rate({var=http_requests,job=webserver}[10m]);

  # Sum the rates to get the aggregate rate of queries for the cluster;
  # 'without instance' instructs Borgmon to remove the instance label
  # from the right hand side.
  {var=dc:http_requests:rate10m,job=webserver} =
    sum without instance({var=task:http_requests:rate10m,job=webserver})
>>>
```
What it demonstrates: per-task `rate()` (total delta / total time between earliest and latest values) then cluster aggregation; rules can depend on earlier rules.

```
rules <<<
  # Compute a rate pertask and per 'code' label
  {var=task:http_responses:rate10m,job=webserver} =
    rate by code({var=http_responses,job=webserver}[10m]);

  # Compute a cluster level response rate per 'code' label
  {var=dc:http_responses:rate10m,job=webserver} =
    sum without instance({var=task:http_responses:rate10m,job=webserver});

  # Compute a new cluster level rate summing all non 200 codes
  {var=dc:http_errors:rate10m,job=webserver} = sum without code(
    {var=dc:http_responses:rate10m,jobwebserver,code=!/200/};

  # Compute the ratio of the rate of errors to the rate of requests
  {var=dc:http_errors:ratio_rate10m,job=webserver} =
    {var=dc:http_errors:rate10m,job=webserver}
      /
    {var=dc:http_requests:rate10m,job=webserver};
>>>
```
What it demonstrates: error-ratio pipeline — rate per code → sum across instances → sum non-200 codes (regex label match `code=!/200/`) → divide by request rate; output compared to the SLO. (Typos `jobwebserver` are in the source.)

```
rules <<<
  {var=dc:http_errors:ratio_rate10m,job=webserver} > 0.01
    and by job, error
  {var=dc:http_errors:rate10m,job=webserver} > 1
    for 2m
    => ErrorRatioTooHigh
      details "webserver error ratio at [[trigger_value]]"
      labels { severity=page };
>>>
```
What it demonstrates: an alert requiring error ratio > 1% AND absolute error rate > 1, held true for 2 minutes, with a templated message and a `severity=page` routing label.

## Reference Tables
| Item | Value |
|---|---|
| Borg created / Borgmon built | 2003, shortly after |
| Arena horizon (DC/global Borgmon) | ~12 hours (much less for lowest-level shards) |
| Memory per data point | ~24 bytes |
| Capacity example | 1M unique series × 12 h × 1-min interval < 17 GB RAM |
| Typical deployment | 1 Borgmon per cluster + pair (≥2) global |
| Alert `for` duration | ≥ 2 rule-evaluation cycles |
| Required labels | `var`, `job`, `service`, `zone` |

| Counter | Gauge |
|---|---|
| Only increases (km driven) | Any value (fuel left, speed) |
| Keeps meaning across sample gaps | Misses events between samples |
| Preferred for Borgmon-style data | Use for current state only |

## Worked Example
**Web server error-ratio alert.** Five tasks (host0–host4) export `http_requests` and `http_responses` by code. Over 10 minutes, `task:http_requests:rate10m` yields ~1, 0.9, 1.1, 0, 1 → `dc:http_requests:rate10m` = **4** (instance label dropped so rows can be summed). Response rates per code sum to 200: 3.4, 500: 0.6 → `dc:http_errors:rate10m` = **0.6** → `dc:http_errors:ratio_rate10m` = 0.6/4 = **0.15**. The alert threshold is 0.01, so the ratio clause is true; but the absolute error rate (0.6) is not > 1, so the alert stays inactive. Once errors exceed 1/s, the alert goes **pending** for 2 minutes and only then **fires**, sending an Alert RPC (filled with `[[trigger_value]]`) to Alertmanager, which routes it to the pager because of `severity=page`. All intermediate results are themselves time-series, so on-call can query them ad hoc and promote useful queries to console graphs.

## Key Takeaways
1. Standardize metric exposition (one HTTP fetch per target) and instrument every library by default so new services ship with metrics and templates.
2. Alert on aggregated, service-level symptoms compared to SLOs, not individual machines; keep labels so you can drill down.
3. Always compute `sum(rate(counter))`, use counters, and follow the `level:var:operation` naming convention.
4. Require alerts to hold for ≥ two evaluation cycles and combine ratio + absolute thresholds to avoid paging on tiny volumes.
5. Pair white-box metrics with black-box probers at both the frontend and behind the load balancer.
6. Shard monitoring hierarchically (scrape → DC aggregate → ≥2 global) and filter what flows upward.
7. Treat rules as code: separate rules from targets, template them, unit-test with synthetic series, ship via CI.

## Connects To
- **Ch 4**: alerts compare error ratios to SLOs; alert design guidance.
- **Ch 6**: symptoms vs causes, white-box vs black-box, simplicity, four golden signals.
- **Ch 2**: Borg and BNS (target discovery).
- **Ch 11**: actionable paging, 1:1 alert/incident ratio, overload from misconfigured monitoring.
- **Ch 12**: exported variables and Borgmon rule tracing as troubleshooting telemetry.
- **Ch 29**: page vs ticket vs dashboard routing.
- **Prometheus / PromQL**: direct open-source analog (recording rules, `rate()`, `sum without`, `for:`, Alertmanager inhibition/dedup/grouping).
