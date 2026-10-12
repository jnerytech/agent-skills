# Chapter 6: Monitoring Distributed Systems
*Authors: Rob Ewaschuk (ed. Betsy Beyer)*

## Core Idea
Monitoring exists to tell a human, with high signal and very low noise, *what* is broken (symptom) and help find *why* (cause). Page only on urgent, actionable, user-visible symptoms; keep the paging path simple; push everything else to dashboards, tickets, or automation.

## Frameworks Introduced
- **The Four Golden Signals**: latency, traffic, errors, saturation. "If you can only measure four metrics of your user-facing system, focus on these four."
  - When to use: baseline monitoring and dashboards for any user-facing service; the minimal set to page on.
  - How:
    1. **Latency** — time to serve a request. Track successful and failed request latency *separately* (a fast HTTP 500 skews the average; a slow error is worse than a fast one). Don't just filter errors out.
    2. **Traffic** — demand in a high-level, system-specific metric: HTTP req/s (split static vs dynamic), network I/O or concurrent sessions for streaming, transactions/retrievals per second for key-value stores.
    3. **Errors** — rate of failed requests: *explicit* (HTTP 500), *implicit* (200 with wrong content), *by policy* (committed to 1 s, so anything over 1 s is an error). Load-balancer 500s catch total failures; only end-to-end tests catch wrong content.
    4. **Saturation** — how "full" the service is, emphasizing the most constrained resource (memory, I/O). Systems degrade before 100%, so set a utilization target. Supplement with load capacity ("can we take 2x? 10% more?"); latency increase is a leading indicator — watch p99 over a ~1-minute window. Include predictions ("disk full in 4 hours").
    - Page a human when one signal is problematic (or, for saturation, *nearly* problematic) → service "at least decently covered."
  - Why it works: covers both user experience (latency, errors) and headroom (traffic, saturation) with a tiny, simple rule set. Failure mode: computing them as means hides the tail.

- **Symptoms Versus Causes ("what's broken" vs "why")**: the symptom is *what's broken*; the cause is *why* (possibly an intermediate cause). One of the most important distinctions for max signal/min noise.
  - When to use: deciding what to page on vs what to show on debug dashboards.
  - How: page on symptoms; use cause-oriented heuristics as debugging aids; for causes, only alert on "very definite, very imminent" ones. Remember that in layered systems one team's symptom is another's cause (slow DB reads: symptom for DB SRE, cause for frontend SRE).
  - Why it works: symptoms correlate with user pain; causes are numerous and often benign. Failure mode: cause-based paging produces floods of non-actionable pages.

- **Black-Box vs White-Box Monitoring**: combine heavy white-box with modest but critical black-box.
  - Black-box: symptom-oriented, shows *active, not predicted* problems ("the system isn't working correctly, right now"). For paging, forces discipline to only nag a human for ongoing, real symptoms. Useless for imminent problems.
  - White-box: inspects internals (logs, JVM profiling interface, HTTP handlers exposing stats). Detects imminent problems and failures masked by retries; essential for debugging (measure DB latency both as seen by web server and as the DB sees itself, to distinguish slow DB from network).

- **Alert-rule review questions** (for writing/reviewing a new alert, avoiding false positives and pager burnout):
  1. Does this rule detect an otherwise undetected condition that is **urgent, actionable, and actively or imminently user-visible**? (N+0 redundancy and "nearly full" count as imminent.)
  2. Will I ever be able to ignore this alert, knowing it's benign? When/why, and how can I avoid that?
  3. Does it definitely indicate users are negatively affected? Filter out cases like drained traffic or test deployments.
  4. Can I take action? Is it urgent or could it wait until morning? Could the action be safely automated? Long-term fix or short-term workaround?
  5. Are other people getting paged for this issue (making a page redundant)?

- **Philosophy on pages and pagers** (four rules):
  - Every page → react with a sense of urgency; only possible a few times a day before fatigue.
  - Every page should be **actionable**.
  - Every page response should **require intelligence**; a robotic response means it shouldn't be a page.
  - Pages should be about a **novel problem** or an event not seen before.
  - Consequence: if a page satisfies these, white-box vs black-box origin is irrelevant; spend much more effort catching symptoms than causes.

- **As Simple as Possible, No Simpler** (pruning guidelines):
  - Rules catching real incidents most often → simple, predictable, reliable.
  - Data collection/aggregation/alerting config rarely exercised (e.g., < once a quarter) → up for removal.
  - Signals collected but not shown on any prebaked dashboard nor used by any alert → candidates for removal.
  - Keep monitoring standalone; don't blend in profiling, single-process debugging, crash tracking, load testing, log analysis, traffic inspection. Integrate via loosely coupled, stable APIs.

## Key Concepts
- **Monitoring**: collecting, processing, aggregating, displaying real-time quantitative data (query counts/types, error counts/types, processing times, server lifetimes).
- **White-box monitoring**: based on metrics exposed by system internals.
- **Black-box monitoring**: testing externally visible behavior as a user would see it.
- **Dashboard**: prebuilt (usually web) summary view of a service's core metrics; may show ticket queue, high-priority bugs, current on-call, recent pushes.
- **Alert**: human-targeted notification classified as **tickets**, **email alerts** ("alert spam"), or **pages**.
- **Root cause**: a defect in a software or human system that, if repaired, instills confidence the event won't recur the same way; incidents can have multiple root causes, each to be fixed.
- **Push**: any change to a service's running software or its configuration.
- **Tail latency**: the slow fraction of requests (e.g., p99) hidden by means; one backend's p99 can become the frontend's median.
- **Latency-bucketed histogram**: count requests per latency bucket with ~exponential boundaries (factor ~3).
- **Incidents per shift**: page-load metric reviewed quarterly with management.

## Mental Models
- Think of a **page as an expensive interrupt** on a human's work, personal time, or sleep; too many and people second-guess, skim, or ignore real ones.
- Use **symptom-based black-box alerts for paging** and **white-box cause data for debugging**.
- Think of **"one person's symptom is another person's cause"** when monitoring multilayer stacks; monitor symptoms further "up" the stack, but subsystem saturation directly on the subsystem.
- Use a **controlled short-term availability hit** when it buys long-term stability (Bigtable SLO relaxation); every page today steals time from improving the system tomorrow.

## Anti-patterns
- **Alerting because "something seems a bit weird"**: not actionable; only acceptable for narrow security auditing.
- **"Magic" systems that learn thresholds or detect causality**: fragile and opaque; Google avoids them (exception: simple rules for unexpected end-user request-rate changes).
- **Complex dependency hierarchies in alerting** ("if DB slow alert DB, else alert website"): break under constant refactoring; only for very stable parts (e.g., "if datacenter drained, don't alert on its latency").
- **Designing around means**: CPU, DB fullness, latency are imbalanced; mean hides a 5-second 1%.
- **Staring at a screen to watch for problems**: SRE teams avoid any such role.
- **Email alerts**: very limited value, overrun with noise; use a dashboard of ongoing subcritical problems (optionally paired with a log) instead.
- **Pages with rote, algorithmic responses**: red flag; team unwillingness to automate them signals lack of confidence in cleaning tech debt — escalate.
- **Over-fine resolution**: per-second CPU or probing a 99.9% service more than once or twice a minute is costly and unnecessary.

## Code Examples
CPU hotspot capture without high-resolution collection cost (procedure):
```
1. Record the current CPU utilization each second.
2. Using buckets of 5% granularity, increment the appropriate CPU utilization bucket each second.
3. Aggregate those values every minute.
```
What it demonstrates: internal sampling on the server + external aggregation gives high resolution of brief spikes without per-second collection/retention cost.

Latency histogram buckets (≈ factor 3): `0–10 ms, 10–30 ms, 30–100 ms, 100–300 ms, …`
What it demonstrates: bucketed counts expose the tail; exponential boundaries visualize distribution easily.

## Reference Tables
Table 6-1. Example symptoms and causes

| Symptom | Cause |
|---|---|
| Serving HTTP 500s or 404s | Database servers refusing connections |
| Responses are slow | CPUs overloaded by a bogosort, or crimped Ethernet cable → partial packet loss |
| Users in Antarctica not receiving animated cat GIFs | CDN blacklisted some client IPs |
| Private content is world-readable | New software push caused ACLs to be forgotten, allowing all requests |

Key numbers:
| Item | Value |
|---|---|
| Monitoring staffing | 1–2 members of a 10–12-person SRE team ("monitoring person") |
| Tail example | 100 ms avg at 1,000 QPS; 1% may take 5 s |
| 1% at 10x mean | rest are ~2x faster than mean |
| 99.9% annual uptime | ~9 hours downtime/year → probe 200s ≤ once or twice/min; disk fullness every 1–2 min |
| Removal threshold | config exercised < once a quarter |
| Saturation leading indicator | p99 latency over ~1-minute window |

## Worked Example
**Bigtable SRE: A Tale of Over-Alerting.** Bigtable's SLO was based on a synthetic well-behaved client's *mean* performance. Storage-stack problems made the worst 5% of requests much slower, driving the mean. Email alerts fired as the SLO approached; pages fired when exceeded. Both fired voluminously; the team spent its time triaging to find the few actionable ones and often missed real user-affecting problems. Many pages were non-urgent, with rote or no response.
Three-pronged fix: (1) major effort to improve Bigtable performance; (2) temporarily dial back the SLO target to **75th percentile** request latency; (3) disable email alerts entirely. Result: breathing room to fix long-term problems in Bigtable and lower storage layers rather than tactical ones; on-call could do project work. Temporarily backing off alerts produced faster progress to a better service.

Second case — **Gmail/Workqueue**: alerts fired per task "de-scheduled" by Workqueue (thousands of tasks, each a fraction of a percent of users) — unmaintainable. SRE built a tool to "poke" the scheduler; debate on fully automating the loop vs fear the hack delays a real fix. Lesson: managers/tech leads must prioritize long-term fixes even after paging pain subsides; refusal to automate rote pages signals lack of confidence in paying tech debt.

## Key Takeaways
1. Instrument the four golden signals for every user-facing system and page on them (saturation: when *nearly* problematic).
2. Page on symptoms; keep causes for dashboards and debugging, alerting only on definite, imminent causes.
3. Run every new alert through the five review questions; every page must be urgent, actionable, need intelligence, and be novel.
4. Measure distributions (latency buckets, percentiles), never just means; choose resolution to match the SLO.
5. Delete rules/signals unused in a quarter or not on any dashboard/alert; keep the paging path simple and understandable by everyone.
6. Replace email alerts with a dashboard of subcritical issues.
7. Track page load (incidents per shift) quarterly with management; accept short-term availability hits for long-term health.

## Connects To
- **Ch 4**: SLOs define what symptoms matter and what to page on (Bigtable SLO percentile change).
- **Ch 3**: error budgets justify a controlled short-term availability hit.
- **Ch 5**: rote, scriptable pages are toil — automate or fix root cause.
- **Ch 10**: Borgmon implements these principles (time-series alerting rules).
- **Ch 11 / Ch 29 / Ch 30**: pager load, on-call health, operational overload.
- **Ch 12**: white-box data feeds troubleshooting.
- **Ch 9**: simplicity applied to monitoring config.
- **Alarm fatigue (healthcare cardiac alarm management)**: same alert-fatigue dynamics.
- **N+1 redundancy**: N+0 counts as imminent user-visible risk.
