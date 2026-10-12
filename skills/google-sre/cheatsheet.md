# Cheatsheet — Site Reliability Engineering

## Decision rules
- **Budget left?** Ship. **Budget spent?** Freeze feature launches, spend on reliability. Chronically blocked → renegotiate the SLO, don't ignore it. (Ch 3)
- **Asked for another nine?** Value = revenue × Δavailability; invest only if cost < value. If users' ISP error rate (0.01–1%) dwarfs yours, the nine is invisible. (Ch 3)
- **Far above SLO for months?** Users now depend on it — inject planned downtime (global Chubby). (Ch 4)
- **Should this page?** Only if urgent + actionable + needs human judgment + novel + user-visible. Otherwise ticket or log. (Ch 6)
- **Ops > 50% of team time?** Redirect tickets/pages to dev ("give back the pager") until fixed. (Ch 1, 11)
- **Incident?** Declare if: a second team is needed, OR customer-visible, OR unsolved after 1 h. (Ch 14)
- **Mid-outage?** Stop the bleeding first (roll back, drain, shed) — root cause later. (Ch 12)
- **Debugging where to look first?** What changed last. Horses, not zebras. (Ch 12)
- **Overloaded?** Return "overloaded; don't retry" and shed lowest criticality first. (Ch 21)
- **Data or availability?** Data integrity wins; take service down if it leaks private data. (Ch 3, 26)
- **Cron: skip or double-run?** Skip (fail closed). (Ch 24)
- **Need strong consistency across sites?** Use proven consensus; never hand-rolled heartbeats/STONITH. (Ch 23)

## Thresholds & defaults
| Item | Value |
|---|---|
| Ops/toil cap | ≤50% of SRE time |
| On-call time | ≤25% → ≥8 people (1 site) / 6 per site (2 sites) |
| Incidents per 12 h shift | ≤2 (each ≈ 6 h incl. postmortem) |
| Page response | ~5 min user-facing; ~30 min otherwise |
| Capacity | N + 2 |
| Retries | ≤3 per request; retries <10% of client requests; jittered exponential backoff |
| Adaptive throttling | K = 2, 2-min window |
| Backend subset per client | 20–100 |
| Consensus replicas | 2f+1; 5 typical (tolerates 2 failures, 1 in maintenance) |
| Soft-delete window | 15–60 days |
| Canary stages | 0.1% → 1% → 10% → 100% |
| Playbooks | ~3× better MTTR |

## Availability ↔ downtime (per year / per quarter)
| SLO | Year | Quarter |
|---|---|---|
| 99% | 3.65 d | 21.6 h |
| 99.9% | 8.76 h | 2.16 h |
| 99.95% | 4.38 h | 1.08 h |
| 99.99% | 52.6 min | 12.96 min |
| 99.999% | 5.26 min | 1.3 min |

## Overload / cascading-failure emergency moves (Ch 22)
1. Add resources (if not a QoD/bug) → 2. Stop health-check kills → 3. Restart servers (GC death spiral, deadlocks) → 4. Drop traffic, recover gradually → 5. Degraded mode → 6. Kill batch load → 7. Block bad traffic (query of death).

## Monitoring output → action
| Output | Response time | Example |
|---|---|---|
| Page | Minutes | SLO burn, user-visible errors |
| Ticket | Days | Disk filling in 4 days |
| Log | Never unless debugging | Diagnostics |

## Tells & smells
- Alerts per incident ≫ 1 → dedupe/aggregate (target 1:1). (Ch 11)
- Average latency looks fine but users complain → check p99. (Ch 4, 6)
- Unhealthy task gets *more* traffic → sinkholing via fast errors. (Ch 20)
- Latency bimodal, threads exhausted → missing deadlines/propagation. (Ch 22)
- Empty input to automation touched everything → "zero means all". (Ch 7, 13)
- Replicas all corrupted together → replication ≠ backup. (Ch 26)
- Same person fielding interrupts and projects → polarize time. (Ch 29)
- New hires learning by "trial by fire" → use checklists, shadowing, Wheel of Misfortune. (Ch 28)
- Postmortem names a person → rewrite blameless. (Ch 15)
