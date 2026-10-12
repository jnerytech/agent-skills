# Appendices A–F: Reference Material
*Appendix B written by Ben Treynor Sloss; all edited by Betsy Beyer*

## Core Idea
These are ready-to-use reference artifacts: downtime math (A), Treynor Sloss's condensed production best practices (B), and a fully worked set of incident artifacts for the fictional "Shakespeare Sonnet++" outage. That set includes the live incident state doc (C), the postmortem (D), the launch checklist (E) and the production meeting minutes (F).

## A. Availability Table
Allowed downtime, assuming no planned downtime:

| Availability | per year | per quarter | per month | per week | per day | per hour |
|---|---|---|---|---|---|---|
| 90% | 36.5 days | 9 days | 3 days | 16.8 h | 2.4 h | 6 min |
| 95% | 18.25 days | 4.5 days | 1.5 days | 8.4 h | 1.2 h | 3 min |
| 99% | 3.65 days | 21.6 h | 7.2 h | 1.68 h | 14.4 min | 36 s |
| 99.5% | 1.83 days | 10.8 h | 3.6 h | 50.4 min | 7.20 min | 18 s |
| 99.9% | 8.76 h | 2.16 h | 43.2 min | 10.1 min | 1.44 min | 3.6 s |
| 99.95% | 4.38 h | 1.08 h | 21.6 min | 5.04 min | 43.2 s | 1.8 s |
| 99.99% | 52.6 min | 12.96 min | 4.32 min | 60.5 s | 8.64 s | 0.36 s |
| 99.999% | 5.26 min | 1.30 min | 25.9 s | 6.05 s | 0.87 s | 0.04 s |

- Use an **aggregate unavailability metric** ("X% of all operations failed") rather than outage length for partially available services (some replicas down) or for load that varies by day or week. See Ch 3, Equations 3-1/3-2.

## B. A Collection of Best Practices for Production Services
- **Fail Sanely**: sanitize and validate config inputs. On implausible input, *keep operating in the previous state* and alert.
  - Incorrect data: validate syntax and semantics, and watch for empty, partial or truncated data (alert if the config is N% smaller than the previous one).
  - Delayed data: alert well before data is expected to expire.
  - Prefer failing permissive or simplistic over failing closed. Wait for human approval before using new, possibly invalid data.
  - *2005*: DNS balancer accepted an empty file and served NXDOMAIN for all Google properties for 6 min. It now sanity-checks (e.g., VIPs for google.com present) and keeps serving the old entries. *2009*: the suspect-URL list was replaced by `/`, which flagged the whole Web as malware. Size-change and plausibility checks would have caught it.
- **Progressive Rollouts**: stage all non-emergency config and binary changes across small fractions of traffic and capacity, and across different geographies (diurnal and traffic-mix effects). Supervise rollouts, preferably with reliable monitoring. **Roll back first, diagnose afterward** to minimize MTTR.
- **Define SLOs Like a User**: measure where users experience the service. Gmail measured at the client, saw lower availability, fixed client and server, and went from about 99.0% to over 99.9%.
- **Error Budgets**: budget = 1 − SLO, usually per month. While budget remains, devs launch freely. Once it is spent, freeze changes except urgent security fixes and fixes for the error cause. For an SLO above 99.99%, reset quarterly. This removes structural tension between SRE and dev.
- **Monitoring**: only three outputs. **Pages** (a human acts now), **Tickets** (a human acts within days), **Logging** (for later analysis). Email alerts are "the moral equivalent of piping them to /dev/null."
- **Postmortems**: blameless. Assume people are intelligent, well intentioned and made the best choices with the information they had. Fix the environment, not the people.
- **Capacity Planning**: **N+2**, meaning peak is served by N instances (possibly degraded) with the largest 2 unavailable (a planned and an unplanned outage at once). Validate forecasts against reality until they match. Use load tests, not tradition, for the resource-to-capacity ratio. Day-one load is not steady-state load.
- **Overloads and Failure**: serve reasonable but suboptimal results under overload (Search uses a smaller index fraction and disables Instant), and test beyond rated capacity. Beyond that, shed load gracefully: well-behaved queues, dynamic timeouts, **tarpitting**, and a consistent subset of clients getting errors. Drop a fraction of traffic (including retries) upstream when load exceeds capacity. Every RPC client must use **exponential backoff with jitter**. Mobile clients are worst because fixes take weeks to roll out.
- **SRE Teams**: no more than **50% ops work**, with overflow sent to dev. Include devs in on-call and tickets, and hold a regular production meeting. Have at least **8 people on-call**, ideally **6 per site** across two well-separated sites. Expect at most **2 events per 12-hour shift**. Practice hypothetical outages (Disaster Role Playing) so rare incidents do not find the team out of practice.

## C. Example Incident State Document
Template structure ("Shakespeare Sonnet++ Overload: 2015-10-21"):
```
<Title: Service + incident name : date>
Incident management info: <link to cheat sheet>
(Communications lead to keep summary updated.)
Summary: <one line: what is broken and why>
Status: active|resolved, incident #NNN
Command Post(s): <IRC/chat channel>
Command Hierarchy (all responders)
  Current Incident Commander: <name>
    Operations lead / Planning lead / Communications lead: <names>
  Next Incident Commander: <name or TBD>
(Update at least every four hours and at handoff of Comms Lead role.)
Detailed Status (last updated at <UTC time> by <name>)
  Exit Criteria: <condition> TODO|DONE   (e.g. within 99.99% availability and 99%ile < 100 ms SLOs for 30+ min)
  TODO list and bugs filed: <task> (Bug N) TODO|DONE
  Incident timeline (most recent first; UTC): <time> <who> - <action/observation>
```
What it demonstrates: a single living document holding roles, explicit exit criteria and a reverse-chronological log (Ch 14).

## D. Example Postmortem
Section skeleton: **Title (incident #) / Date / Authors / Status / Summary / Impact / Root Causes / Trigger / Resolution / Detection / Action Items (table: item, type, owner, bug) / Lessons Learned (What went well / What went wrong / Where we got lucky) / Timeline / Supporting information**.

Key facts (Shakespeare Sonnet++, #465):
- **Summary**: Shakespeare Search was down for **66 minutes** during a surge of interest in a newly discovered sonnet. **Impact**: about **1.21B queries lost**, no revenue impact.
- **Root cause**: cascading failure from exceptionally high load combined with a **file-descriptor leak** on searches for terms not in the corpus. The new sonnet's never-before-seen word was what users searched for. **Trigger**: a latent bug triggered by a traffic spike (**88x**). **Detection**: Borgmon paged on HTTP 500s.
- **Resolution**: send all traffic to a **sacrificial cluster** (USA-2), raise capacity (a 2x attempt failed because of an order-of-magnitude whiteboard error, then 10x total), push the updated index, and ramp traffic back 1%→10%→30%→50%→100%. Outage 14:54–16:00. The incident ended at 16:30 after **30 minutes of nominal performance** (exit criterion).
- **Action item types**: mitigate / prevent / process / other. Examples: update the playbook for cascading failure, plug the FD leak, add load shedding, add regression tests for queries of death, schedule a cascading-failure test in the next DiRT, and a production freeze until 2015-11-20 for **error budget exhaustion**.
- **Notes**: Root Causes can use the **5 Whys**. Rescope "knee-jerk" action items, because unit tests often beat bespoke alerts. "Where we got lucky" records **near misses**. The timeline is a "screenplay" seeded from the incident doc.

## E. Launch Coordination Checklist (Google, c. 2005, condensed)
- **Architecture**: architecture sketch, server types, client request types, programmatic clients.
- **Machines and datacenters**: machines, bandwidth, DCs, **N+2**, network QoS, new domains, DNS load balancing.
- **Volume, capacity, performance**: traffic and bandwidth estimates, launch spike, traffic mix, 6 months out; load and end-to-end tests; per-DC capacity at max latency; impact on key services; storage.
- **Reliability and failover**: machine, rack or cluster loss; inter-DC network failure. Per backend: detecting death and responding, restarting without user impact, load balancing, rate limits, timeouts, retries and error handling. Backup/restore and DR.
- **Monitoring and server management**: internal and end-to-end monitoring, alert management, monitoring the monitoring, financially important alerts and logs. Don't crash mail servers by emailing alerts to yourself.
- **Security**: design review, code audit, spam, authentication, SSL, prelaunch access control, blacklists.
- **Automation and manual tasks**: change control for servers, data and configs; release process, repeatable builds, canaries, staged rollouts.
- **Growth**: spare capacity, 10x growth, growth alerts, bottlenecks, linear scaling, caching, sharding/resharding.
- **External dependencies**: third parties, launch spikes, graceful degradation, not overrunning partners or internal services.
- **Schedule and rollout**: hard deadlines, external events, Mondays/Fridays, SOPs.

## F. Example Production Meeting Minutes
Agenda skeleton (2015-10-23):
```
Date / Attendees
Announcements                      (e.g. major outage #465, blew error budget)
Previous Action Item Review
Outage Review                      (cause, fixes deployed, prevention bugs, budget/freeze status)
Paging Events                      (e.g. alert paged 5x; raise threshold to cut unactionable pages)
Nonpaging Events
Monitoring Changes and/or Silences (e.g. threshold 60s -> 180s, bug link, TODO owner)
Planned Production Changes         (e.g. cluster maintenance window; no response required)
Resources                          (borrowed capacity to return; CPU/RAM/disk utilization trend)
Key Service Metrics                (OK/BAD vs SLO, trailing 30 days: 99ile 88 ms < 100 ms OK; availability 86.95% < 99.99% BAD)
Discussion / Project Updates
New Action Items                   (TODO(owner): ...)
```

## Key Takeaways
1. Translate SLOs into concrete downtime with Table A-1 before committing to a target. Each extra nine cuts downtime 10x.
2. Validate inputs and keep the last good state. Roll out progressively, and roll back before diagnosing.
3. Route all monitoring output to page, ticket or log, and nowhere else.
4. Provision N+2. Implement exponential backoff with jitter and graceful degradation.
5. Staff on-call with at least 8 people (6 per site for two sites), at most 2 events per shift, and at most 50% ops.
6. Reuse the C/D/F templates as-is: incident doc → postmortem → production meeting form one paper trail.

## Connects To
- **Ch 3 Embracing Risk / Ch 4 SLOs**: availability math and error budgets.
- **Ch 14 Managing Incidents**: Appendix C's roles and state document.
- **Ch 15 Postmortem Culture**: Appendix D.
- **Ch 21–22 Overload / Cascading Failures**: the Sonnet++ failure mode and load shedding.
- **Ch 27 Reliable Product Launches**: the full LCE checklist that Appendix E condenses.
- **Ch 31 Communication and Collaboration**: the production meeting in Appendix F.
