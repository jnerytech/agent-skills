# Chapter 11: Being On-Call
*Authors: Andrea Spadaccini (edited by Kavita Guliani)*

## Core Idea
On-call is sustainable only when it is balanced in **quantity** (≤25% of an SRE's time) and **quality** (≤2 incidents per 12-hour shift), backed by safety nets (escalation paths, incident procedures, blameless postmortems) so engineers reason deliberately instead of reacting on stress-driven heuristics.

## Frameworks Introduced
- **Balanced On-Call (quantity × quality)**: managers keep on-call workload sustainable along two axes — *quantity* = percent of time on on-call duties; *quality* = number of incidents per shift.
  - When to use: sizing teams, designing rotations, deciding whether a service is overloading the team.
  - How:
    1. Enforce ≥50% engineering; of the remaining ≤50%, **no more than 25% on-call**, up to another 25% other ops work.
    2. Derive team size: with primary + secondary always on-call and week-long shifts, a **single-site team needs ≥8 engineers** (each on-call one week per month); **dual-site: ≥6 per site**.
    3. Budget **~6 hours per incident** (root-cause analysis, remediation, postmortem, bug fixes) → **max 2 incidents per 12-hour shift**.
    4. Aim for a very flat page distribution with **median 0 incidents/shift**; a component paging daily (median > 1) signals something else will break too.
    5. If limits are exceeded (e.g. for a quarter), put corrective objectives into quarterly planning.
  - Why it works: caps protect the "E" in SRE and leave time for follow-up work (postmortems, fixes) that prevents repeat pages.
  - Failure mode: exceeding the incident budget means follow-ups get skipped, which breeds more incidents — a self-reinforcing spiral.
- **Multi-site "follow the sun" rotation**: prefer creating a multi-site team over growing a single-site one.
  - Why: avoids night shifts (harmful to health) and caps rotation size so engineers stay in touch with production.
  - Trade-off: communication and coordination overhead; decide by importance of the system and workload.
- **Primary/secondary rotation patterns**: secondary as fall-through for missed pages, *or* primary takes pages while secondary handles non-urgent production work; two related teams can act as each other's secondary.
- **Feeling Safe (deliberate vs intuitive thinking)**: stress hormones (cortisol, CRH) push people from rational, focused, deliberate cognition to intuitive, automatic, rapid action and heuristic abuse (e.g. confirmation bias: "4th page this week, must be the same external cause").
  - How to counteract — provide the three key on-call resources:
    1. **Clear escalation paths** (developer teams usually run 24/7 rotations to escalate to).
    2. **Well-defined incident-management procedures** (Ch 14 protocol, supported by a tool automating role handoff and status updates).
    3. **A blameless postmortem culture**.
  - Ideal: act at the desired pace once enough data supports a reasonable decision, while critically examining assumptions.
- **Operational overload remediation**:
  - Quantify symptoms (e.g. **daily tickets < 5, paging events per shift < 2**).
  - Fix misconfigured monitoring: pages must map to symptoms threatening SLOs and be **actionable**.
  - Group related alerts; silence duplicates during an incident; tune toward a **1:1 alert/incident ratio**.
  - Set shared goals with developers when their changes add noise.
  - Loan an experienced SRE to the overloaded team (Ch 30).
  - Extreme case: **"give back the pager"** — route some or all pages to the developer on-call until the service meets SRE standards; temporary, then re-onboard.
- **Operational underload countermeasures**: size teams so every engineer is on-call **at least once or twice a quarter**; run **Wheel of Misfortune** exercises (Ch 28); participate in **DiRT** (Disaster Recovery Training), Google's annual multiday company-wide drill.

## Key Concepts
- **Paging response time**: agreed time to be hands-on — typically **5 minutes** for user-facing/time-critical services, **30 minutes** for less time-sensitive systems.
- **Incident (on-call definition)**: sequence of events and alerts with the same root cause, discussed in the same postmortem.
- **Primary / secondary on-call**: two concurrent roles with team-specific division of duties.
- **Operational overload**: ops work exceeding the 50% cap; must be measured and fixed via planning.
- **Operational underload**: too little production exposure, causing over- or under-confidence and knowledge gaps discovered only during incidents.
- **Giving back the pager**: SRE asks developers to be exclusively on-call until the system meets SRE standards.
- **Compensation**: time-off-in-lieu or cash, **capped at a proportion of salary** — the cap implicitly limits per-person on-call load and prevents burnout.
- **Nonpaging events**: lower-priority alerts, releases; handled during business hours, below pages in priority.
- **DiRT**: annual Disaster Recovery Training combining theoretical and practical drills.

## Mental Models
- Think of response time as derived from the SLO: 99.99% quarterly ≈ 13 minutes downtime, so reaction must be within minutes; relaxed SLOs allow tens of minutes.
- Think of incident load as a time budget: 12 hours / 6 hours per incident = 2.
- Use the deliberate (System 2) mindset for complex outages; treat a strong "I know what this is" feeling as a hypothesis, not a conclusion.
- Think of "give back the pager" as evidence of a balance of powers between SRE and dev, resolving the reliability vs feature-velocity tension.

## Anti-patterns
- **Unbounded on-call time**: erodes engineering, causes burnout.
- **Night shifts in a single-site team**: health damage; prefer follow-the-sun.
- **Noisy, non-actionable, low-priority pages** (hourly or more): fatigue makes serious alerts get less attention.
- **Alert fan-out per incident**: on-call triages duplicates instead of the incident.
- **Confirmation bias / habitual responses**: blaming the previous cause; quick reactions are unconsidered and can be disastrous.
- **Rotation too large / too quiet**: engineers lose touch with production.
- **Blaming individuals in postmortems**: focus on events and systems; automate away error opportunities.

## Reference Tables
| Parameter | Value |
|---|---|
| Engineering time minimum | 50% |
| On-call time maximum | 25% |
| Other ops work | up to 25% |
| Min team size, single-site 24/7 (primary + secondary, weekly shifts) | 8 |
| Min team size per site, dual-site | 6 |
| Time per incident (RCA + remediation + postmortem + bugs) | ~6 h |
| Max incidents per 12-h shift | 2 |
| Target median incidents/shift | 0 |
| Response time, user-facing | 5 min |
| Response time, less time-sensitive | 30 min |
| Overload targets example | tickets/day < 5; pages/shift < 2 |
| Minimum on-call exposure | 1–2 times per quarter |
| 99.99% quarterly downtime | ~13 min |

## Worked Example
**Sizing a rotation.** A service needs 24/7 coverage with primary and secondary. Each engineer may spend ≤25% on-call. Two people on-call at all times with week-long shifts: in a 4-week month that's 8 person-weeks of duty; at 1 week per engineer per month (25%), you need **8 engineers** on a single site. With two sites splitting the day (follow-the-sun, no night shifts), each site needs about **6** to honor the 25% rule and keep critical mass. Then check quality: if the service averages more than 2 incidents per 12-hour shift for a quarter, put overload objectives (alert tuning to 1:1, reliability fixes with devs, an SRE loan, or partial pager hand-back) into the next quarter's plan.

## Key Takeaways
1. Cap on-call at 25% of time and size teams accordingly (8 single-site, 6 per site dual-site).
2. Budget ~6 hours per incident; keep ≤2 incidents per 12-hour shift and a median of 0.
3. Make every page actionable and SLO-symptom-based; drive toward one alert per incident.
4. Give on-callers clear escalation paths, a formal incident procedure, and blameless postmortems so they can think deliberately.
5. Measure overload with concrete targets and fix it through quarterly planning, dev collaboration, or giving back the pager.
6. Prevent underload: on-call at least once or twice a quarter, plus Wheel of Misfortune and DiRT.
7. Compensate out-of-hours work with a cap that also limits individual on-call load.

## Connects To
- **Ch 1**: 50% cap on ops work; SRE vs dev tension.
- **Ch 3/4**: SLOs determine response times and what deserves a page.
- **Ch 10 / Ch 6**: actionable, symptom-based alerting.
- **Ch 14**: incident-management protocol on-callers rely on.
- **Ch 15**: blameless postmortems.
- **Ch 28**: Wheel of Misfortune, onboarding to on-call.
- **Ch 29**: interrupts and nonpaging operational load.
- **Ch 30**: embedding an SRE to relieve operational overload.
- **Kahneman's System 1/System 2**: intuitive vs deliberate cognition under stress.
