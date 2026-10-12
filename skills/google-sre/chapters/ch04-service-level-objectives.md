# Chapter 4: Service Level Objectives
*Authors: Chris Jones, John Wilkes, and Niall Murphy with Cody Smith (edited by Betsy Beyer); sidebar by Marc Alvidrez*

## Core Idea
Separate the overloaded "SLA" into **SLI** (what you measure), **SLO** (the target for it), and **SLA** (the contract with consequences); choose a few user-centric indicators as distributions, set simple, defensible targets, and use them as the control loop for action and expectation-setting.

## Frameworks Introduced
- **SLI / SLO / SLA terminology**:
  - **SLI**: a carefully defined quantitative measure of some aspect of the level of service (latency, error rate, throughput, availability/yield, durability).
  - **SLO**: a target value or range for an SLI: `SLI ≤ target` or `lower bound ≤ SLI ≤ upper bound`.
  - **SLA**: an explicit or implicit contract with users including consequences of meeting/missing the SLOs.
  - Test: ask "what happens if the SLOs aren't met?" — no explicit consequence means it's an SLO. "SLA violation" almost always means a missed SLO.
  - Why it works: Untangling the terms lets SRE own SLIs/SLOs while business/legal own SLAs; SRE helps avoid triggering SLA consequences and makes SLIs objectively measurable.
- **SLI categories by system type**:
  - User-facing serving: availability, latency, throughput.
  - Storage: latency, availability, durability.
  - Big data / pipelines: throughput, end-to-end latency (sometimes per-stage).
  - All systems: correctness (often a data property, usually not SRE's to meet).
- **SLI standardization templates**: Define defaults once — aggregation interval ("averaged over 1 minute"), aggregation region ("all tasks in a cluster"), measurement frequency ("every 10 seconds"), included requests ("HTTP GETs from black-box monitoring jobs"), acquisition ("through our monitoring, measured at the server"), data-access latency ("time to last byte"). Anything matching the template can be omitted from individual SLIs.
- **Lessons for choosing targets**: (1) Don't pick a target based on current performance; (2) Keep it simple; (3) Avoid absolutes; (4) Have as few SLOs as possible — defend each; if you can't win a priority conversation by quoting it, drop it; (5) Perfection can wait — start loose, tighten later.
  - Why it works / failure mode: An SLO is a "massive lever" and legitimate forcing function; too aggressive wastes heroic effort, too lax yields a bad product.
- **Control loop (control measures)**: (1) Monitor and measure SLIs; (2) compare SLIs to SLOs and decide if action is needed; (3) if needed, figure out what must happen to meet the target; (4) take that action.
- **Expectation-setting tactics**: *Keep a safety margin* (tighter internal SLO than the advertised one) and *Don't overachieve* (users depend on actual, not stated, performance — use planned outages, throttling, or no-faster-under-light-load design).
- **Work backward from objectives**: Start from what users care about, not what is easy to measure; derive indicators from desired objectives.

## Key Concepts
- **Yield**: Fraction of well-formed requests that succeed — the usual availability SLI.
- **Durability**: Likelihood data is retained over a long period; key SLI for storage.
- **Nines**: 99% = "2 nines", 99.999% = "5 nines"; Google Compute Engine target = "three and a half nines" (99.95%).
- **Proxy SLI**: Server-side latency used when the user-relevant client-side latency is hard to measure.
- **Client-side collection**: Needed when user-visible problems (e.g., slow JavaScript) don't show in server metrics.
- **Percentiles vs mean**: 99th/99.9th show plausible worst case; 50th (median) shows typical case.
- **Tail latency**: Long tail of slow requests hidden by averages; worsened by queuing at high load.
- **Error budget as SLO**: "An error budget is just an SLO for meeting other SLOs" — a tolerated rate of SLO misses.
- **Performance cliff**: Beyond some load, latency jumps; QPS and latency SLIs are coupled.
- **Planned outage (Chubby)**: Synthetic downtime to keep a service from exceeding its SLO.

## Mental Models
- Think of every metric as a distribution, not an average.
- Use "what happens if it isn't met?" to classify any reliability commitment as SLO vs SLA.
- Use the SLO as the trigger for action: without it, you can't know whether or when to act.
- Think of users as building on the reality you deliver, not on what you promise — so actively cap delivered reliability near the SLO.

## Anti-patterns
- **Using every monitored metric as an SLI**: Dilutes attention; a handful of representative indicators suffice.
- **Starting from what's easy to measure**: Produces less useful SLOs.
- **Averaging latency or rates over windows**: 200 req/s on even seconds and 0 on odd has the same average as constant 100 req/s but twice the instantaneous load; averages hide tails.
- **Assuming normal distributions / mean ≈ median**: Computing data is skewed (≥0 ms, timeouts cap values); outlier-driven actions fire too often or too rarely.
- **Setting SLOs on what users control (e.g., incoming QPS)**: You can't choose that value.
- **Insisting SLOs are met 100% of the time**: Slows innovation and forces expensive, conservative designs.
- **Advertising aggressive SLAs broadly**: The wider the constituency, the harder an unwise SLA is to change — be conservative.
- **No published SLO**: Users invent their own beliefs → over-reliance or under-reliance.

## Code Examples
```
SLI ≤ target
lower bound ≤ SLI ≤ upper bound
```
```
99% (averaged over 1 minute) of Get RPC calls will complete in less than 100 ms
    (measured across all the backend servers).
99% of Get RPC calls will complete in less than 100 ms.   # same, relying on SLI defaults

90% of Get RPC calls will complete in less than 1 ms.
99% of Get RPC calls will complete in less than 10 ms.
99.9% of Get RPC calls will complete in less than 100 ms.

95% of throughput clients' Set RPC calls will complete in < 1 s.
99% of latency clients' Set RPC calls with payloads < 1 kB will complete in < 10 ms.
```
What it demonstrates: well-formed SLO statements — explicit measurement conditions, multi-percentile targets for curve shape, and per-workload-class objectives.

## Reference Tables
| Term | Owner | Consequence |
|---|---|---|
| SLI | SRE (defines/measures) | none — it is a measure |
| SLO | SRE + product | internal action (error budget, release decisions) |
| SLA | business/legal (SRE advises) | financial or other penalty |

| Tracking cadence | Audience |
|---|---|
| Daily/weekly SLO and violation tracking | Team (trends, early warning) |
| Monthly/quarterly assessment | Upper management |

## Worked Example
**Global Chubby planned outage**: Global Chubby replicas sit in different regions, so true outages were very rare. Service owners therefore added hard dependencies assuming it would never go down — and when it did, their services failed in user-visible ways. Fix: SRE ensures global Chubby *meets but does not significantly exceed* its SLO. In any quarter where real failures haven't dropped availability below target, SRE synthesizes a controlled outage by intentionally taking the system down, flushing out unreasonable dependencies soon after they're added and forcing owners to face distributed-systems reality early.

Also: a Shakespeare latency SLO (average search latency < 100 ms) would miss users' real experience if JavaScript makes pages slow — so measure time-until-page-usable in the browser.

## Key Takeaways
1. Pick a handful of SLIs by system type (serving, storage, pipeline) plus correctness.
2. Measure SLIs as percentiles; check distributions before applying normal-distribution intuitions.
3. Standardize SLI definitions with reusable templates.
4. Write SLOs with explicit measurement conditions; few, simple, defensible, and initially loose.
5. Keep an internal SLO tighter than the external one, and don't let delivered reliability far exceed the SLO.
6. Feed SLO-miss rate vs error budget into release decisions.
7. Leave SLAs to business/legal, keep them conservative, and make sure their SLIs are objectively measurable.

## Connects To
- **Ch 3**: Error budgets built on SLOs; availability definitions.
- **Ch 2**: Shakespeare sample service and Chubby.
- **Ch 6 / Ch 10**: Monitoring, four golden signals, Borgmon/Prometheus collection.
- **Ch 23**: Chubby and consensus.
- **Ch 26**: Storage SLIs (durability) and data integrity.
- **Ch 21 / Ch 22**: Performance cliffs, overload and cascading failures.
- **Failure injection**: Different purpose but also sets expectations.
