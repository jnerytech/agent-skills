# Chapter 16: Tracking Outages
*Authors: Gabe Krabbe (edited by Lisa Carey)*

## Core Idea
You can only improve reliability over time if you start from a known baseline and track progress. Postmortems cover only large incidents, so you also need a system that passively captures **every** alert and lets you annotate, group, tag, and analyze them. That system reveals frequent, small, or cross-cutting problems. Google's version is **Outalator**, built on top of **Escalator**.

## Frameworks Introduced
- **Escalator (notification escalation)**: a central replicated system that tracks whether a human acknowledged an alert. If nobody acknowledges within a configured interval, it escalates to the next destination (for example, from primary on-call to secondary).
  - When to use: any paging setup where a missed page must not die silently.
  - How: it receives copies of emails sent to on-call aliases and stays largely transparent, so neither user behavior nor the monitoring systems had to change.
  - Why it works: it adds value to existing infrastructure without forcing anyone to change their workflow, so adoption is effortless.
- **Outalator (outage tracker)**: the next layer of abstraction above Escalator. It deals with **outages**, not individual notifications.
  - When to use: to learn systematically from all alerts, not only the ones that get a postmortem.
  - How (features):
    1. A **time-interleaved queue view** across multiple queues, useful because one SRE team often fronts services that have different secondary escalation targets (usually dev teams).
    2. It stores the original notification and silently saves **email replies** as annotations. Annotations can be marked **"important"**, which collapses the rest of the thread.
    3. **Aggregation**: it combines multiple alerts into a single **incident**, which enables "incidents per day" versus "alerts per day" analysis.
    4. **Tagging**: free-form metadata at any level, with colon-separated hierarchical namespaces.
    5. **Analysis** and **reporting** (shift handoff emails, "report mode").
  - Why it works / failure mode: postmortems miss issues that are individually small but frequent and widespread, and fixes with poor cost/benefit for one service but large **horizontal impact**. An outage tracker catches both.
- **Free-form hierarchical tagging**: tags are mostly single words, and colons act as semantic separators.
  - How: the suggested prefixes are mainly `cause:` and `action:`. The suggestion list is team-specific and generated from historical usage. Granularity varies by team (`cause:network` versus `cause:network:switch` / `cause:network:cable`), and some tags become links (`bug:76543` links to the bug tracker). `bogus` is the widely used tag for false positives.
  - Principle: avoid a predetermined list. Letting teams find their own standards gives a more useful tool and better data, even with typos (`cause:netwrok`) and unhelpful tags (`problem-went-away`). It is "probably one of the Outalator's most useful unique features."
- **Layers of outage analysis**:
  1. **Counting and basic aggregate statistics**: incidents per week/month/quarter, alerts per incident.
  2. **Comparison across teams/services and over time**: is this alert load "normal"? "That's the third time this week" means nothing until you know whether it used to happen five times per day or five times per month.
  3. **Semantic analysis of wider issues**: for example, which infrastructure component causes the most incidents, or a shared root cause (network congestion leading to DB replication delay) behind different service-specific alerts ("stale data," "high latency").

## Key Concepts
- **Alert vs. incident**: an alert is one escalating notification. An incident is a group of alerts with the same underlying cause, or a grouping of auditable or spurious events.
- **Outalation**: an Outalator entry or incident. Several can be selected and emailed as a handoff.
- **"Important" annotation**: a flagged reply that cuts clutter from noisy threads, such as reply-alls that only add cc recipients.
- **Horizontal impact**: a fix with little effect on any single outage that pays off across many events (for example, a Bigtable change).
- **Report mode**: expands important annotations inline to give a quick overview of "lowlights" for weekly production reviews.
- **Shift handoff email**: a selection of outalations with their subjects, tags, and important annotations, sent to the next on-call.
- **Dummy escalator configuration**: a queue no human receives, used as a "system of record" for audit-style logging.
- **Over-performing service**: one that runs well above its SLO, so users' expectations drift upward. The remedy may be injecting artificial failures (see Ch 4, Chubby).

## Mental Models
- Think of **postmortems as depth and outage tracking as breadth**. You need both to see deep single failures and also the death by a thousand cuts.
- Use the question **"what did we do last time?"** as the starting point during an incident. History is more valuable still for finding systemic, periodic problems.
- Think of **raw counts as meaningless without a baseline**. Always compare against your own history and against peer services.
- Use cross-team visibility as an alarm in its own right: if a dependency is visibly failing for you but its owning team hasn't been alerted, page them manually.

## Anti-patterns
- **Relying only on postmortems**: high-frequency, low-impact problems and horizontally valuable fixes are never seen.
- **One email per duplicate alert** ("this is the same as that other thing"): it doesn't scale within a team, between teams, or over time. Use grouping.
- **A predetermined, rigid tag taxonomy**: it suppresses organic, team-appropriate data.
- **Treating "most incidents caused" as the whole truth**: it may be an artifact of over-sensitive monitoring or of misbehaving clients running outside the agreed service level, and the count says nothing about how hard the problem is to fix or how severe it is ("on the gripping hand").
- **Forcing users to change their workflow for a new tool**: Escalator and Outalator succeeded by hooking transparently into existing email flows.

## Reference Tables

| Analysis question | Value |
|---|---|
| Alerts per on-call shift? | Measures on-call load (see Ch 11) |
| Ratio of actionable to nonactionable alerts last quarter? | Measures alert quality (see Ch 6) |
| Which service creates the most toil? | Prioritizes toil work (see Ch 5) |
| Incidents/week, alerts/incident | Layer 1 of the analysis |
| Comparison vs. own history and peer teams | Layer 2: establishes "normal" |
| Most-incident-causing component | Layer 3: semantic, cross-team analysis |

## Worked Example
**Network failure fan-out:** a network failure causes timeouts and unreachable backends for everyone. Every affected team gets its own alerts, the backend owners get alerts too, and the network operations center's "klaxons" ring as well. In Outalator, these alerts are grouped into a single incident and tagged `cause:network`. Across teams, the tags show that "stale data" in one service and "high latency" in another share the same network-congestion and replication-delay cause. One systemic fix then replaces many local ones. Separately, a service owner sees an apparent Bigtable problem but no matching Bigtable SRE alert in Outalator, so they page the Bigtable team manually, which speeds mitigation.

**Unexpected uses:** dummy escalator queues log and audit the use of privileged or role accounts (technical audits, not legal ones). They also record and auto-annotate runs of non-idempotent periodic jobs, such as automatic schema changes pushed from version control to databases.

## Key Takeaways
1. Capture **all** alerts passively in a tracker, not just the ones that warrant a postmortem.
2. Group duplicate alerts into incidents, so you can measure both incidents per day and alerts per day.
3. Allow free-form, colon-namespaced tags (`cause:`, `action:`, `bug:`, `bogus`), and let each team evolve its own vocabulary.
4. Analyze in layers: counts, then comparison with baselines and peers, then semantic cross-team root causes.
5. Use the tracker for shift handoffs and weekly production reviews (report mode).
6. Build new tooling by hooking into existing flows (email, Slack, IRC) rather than forcing behavior change.

## Connects To
- **Ch 4 (Service Level Objectives)**: over-performing services and artificial failures.
- **Ch 5 (Eliminating Toil)**: finding which service creates the most toil.
- **Ch 6 (Monitoring Distributed Systems)**: actionable versus nonactionable alerts, and the trade-off between false positives and false negatives.
- **Ch 11 (Being On-Call)**: escalation from primary to secondary, alerts per shift, and handoffs.
- **Ch 15 (Postmortem Culture)**: postmortems give depth for big incidents, and outage tracking gives breadth.
- **Ch 29 (Dealing with Interrupts)**: alert load as interrupt load.
- **ChatOps / incident platforms (Slack, PagerDuty)**: modern equivalents for building your own Outalator.
