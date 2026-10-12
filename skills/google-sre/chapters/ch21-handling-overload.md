# Chapter 21: Handling Overload
*Authors: Alejandro Forero Cuervo (edited by Sarah Chavis)*

## Core Idea
No load balancing policy prevents all overload, so every client and backend must handle resource limits gracefully: redirect when possible, serve degraded results when necessary, and handle resource errors transparently when all else fails. A task provisioned for a rate should keep serving that rate, without crashing, even when offered 2x–10x more.

## Frameworks Introduced
- **Client-Side Throttling via Adaptive Throttling**: clients self-regulate once backends reject too much, failing excess requests locally without touching the network.
  - When to use: when rejecting a request at the backend still costs real resources (e.g., cheap RAM-lookup services where rejecting ≈ serving), so a backend could be overloaded just by rejecting.
  - How:
    1. Each client keeps, over the last **two minutes**: `requests` (attempted by the application layer) and `accepts` (accepted by the backend).
    2. Normally equal. Once `requests` exceeds `K × accepts`, reject new requests locally with probability `max(0, (requests − K × accepts) / (requests + 1))` (Equation 21-1).
    3. Locally rejected requests still count in `requests` — intentional, so drop probability rises as demand outgrows accepts.
    4. Tune K: lower = more aggressive (K=1.1 → backend rejects only 1 per 10 accepted); higher = less aggressive. Google prefers **K = 2**: wastes some backend resources but propagates backend recovery to clients faster.
  - Why it works: purely local information, simple, no extra dependencies or latency; yields stable request rates, and even in large overload backends reject about one request per request they process.
  - Failure mode: clients that send requests only sporadically have too little visibility into backend state.

- **Per-Customer Limits (global quotas)**: provision capacity on negotiated usage and give each customer a quota (in CPU-seconds per second) so that in global overload only misbehaving customers get errors.
  - When to use: shared/internal services with many client teams, where global overload happens "quite frequently."
  - How: aggregate global usage in real time from all backend tasks; push effective limits to individual tasks; quotas may sum to more than total capacity (statistical multiplexing). Limits can be set per criticality.

- **Criticality**: four-level request priority, a first-class RPC concept.
  - `CRITICAL_PLUS` — most critical; serious user-visible impact if it fails.
  - `CRITICAL` — default for production jobs; user-visible impact. Provision for all expected CRITICAL + CRITICAL_PLUS traffic.
  - `SHEDDABLE_PLUS` — partial unavailability expected; default for batch jobs (can retry minutes/hours later).
  - `SHEDDABLE` — frequent partial and occasional full unavailability expected.
  - How it's used: out-of-quota backends reject a criticality only after rejecting all lower ones; overloaded tasks reject lower criticalities sooner; adaptive throttling keeps per-criticality stats. Criticality **propagates automatically** through the RPC tree; set it as close to the browser/mobile client as possible (HTTP frontends) and override only where justified. Criticality is orthogonal to latency/QoS (search-as-you-type suggestions: highly sheddable but latency-sensitive).

- **Utilization Signals / Executor Load Average**: task-level protection based on local utilization; reject by criticality as thresholds are approached (higher thresholds for higher criticality).
  - How: count active threads (running or ready-to-run), smooth with exponential decay, start rejecting when it exceeds available processors. Short fan-out spikes get absorbed; sustained load triggers rejection. Pluggable: memory pressure, or combined signals.

- **Retry Rules for Overload Errors**: distinguish "a large subset of the datacenter is overloaded" (don't retry; bubble the error up) from "a small subset is overloaded" (retry immediately — likely lands on another task).
  - How:
    1. **Per-request retry budget**: up to **three attempts**, then fail to the caller.
    2. **Per-client retry budget**: retry only while retries are under **10%** of requests (worst case growth drops from ~3x to ~1.1x).
    3. **Attempt counter in request metadata**: backends keep histograms; if many incoming requests are retries, answer "overloaded; don't retry" instead of "task overloaded."
    4. **Retry only at the layer immediately above** the rejecting layer; above that, return "overloaded; don't retry" or a degraded response to avoid combinatorial retry explosion.
    5. Treat retries like new requests in balancing — retries become organic load balancing.

## Key Concepts
- **Degraded responses**: less accurate or less complete but cheaper answers (search a fraction of the corpus; use a stale local copy).
- **QPS pitfall**: query cost varies by client code, time of day, software version — QPS is a moving target.
- **Request cost**: normalized CPU time consumed, across CPU architectures.
- **CPU as provisioning signal**: works because GC turns memory pressure into CPU and other resources can be overprovisioned.
- **Adaptive throttling**: client-side self-regulation from requests/accepts ratio.
- **Criticality**: CRITICAL_PLUS / CRITICAL / SHEDDABLE_PLUS / SHEDDABLE.
- **Executor load average**: smoothed count of active threads vs processors.
- **"Overloaded; don't retry"**: distinct error that stops retries propagating upward.
- **Batch proxy**: intermediary tasks that shield backends from huge batch jobs, acting "like a fuse."
- **Load from connections**: CPU/memory cost of connection pools, health checks, and connection churn.

## Mental Models
- Think of **capacity in resources, not queries**: 500 cores and 1 TB, not "N QPS."
- Use **client-side throttling when rejection isn't free** — stop the request before it reaches the network.
- Think of **criticality as a contract that travels**: set once at the edge, honored at every depth.
- Use **"retry at one layer only"**: the layer above the failure retries; everyone else gets a definitive answer.
- Think of a **well-behaved overloaded backend** as one that keeps accepting what it can process and rejects the rest gracefully — not one that stops accepting everything.

## Anti-patterns
- **Modeling capacity as QPS or static request features** ("keys read"): ratios drift, sometimes drastically after a release.
- **Assuming rejection is cheap**: backends can burn most CPU just rejecting.
- **Ad hoc, service-specific priority schemes**: incompatible across services; standardize and propagate.
- **Retrying at every layer**: combinatorial explosion.
- **Unbounded retries**: request volume grows toward 3x (or more) during overload.
- **Ignoring connection load**: health checks for many low-rate clients can cost more than serving; connection bursts from large batch jobs can overload backends.
- **Turning an overloaded backend off entirely**: counter to robust load balancing.

## Code Examples
Equation 21-1 (client request rejection probability):
```
max(0, (requests − K × accepts) / (requests + 1))
```
What it demonstrates: probability of locally rejecting a new request; zero until requests exceed K × accepts, then rising with excess demand. K=2 is the preferred default; K=1.1 is aggressive.

## Reference Tables
**Example per-customer limits (backend with 10,000 CPUs worldwide)**
| Customer | Limit (CPU-seconds/second) |
|---|---|
| Gmail | 4,000 |
| Calendar | 4,000 |
| Android | 3,000 |
| Google+ | 2,000 |
| Every other user | 500 |
(Sum exceeds 10,000 — relies on customers not peaking together.)

**Retry growth under severe overload**
| Mechanism | Request growth |
|---|---|
| No limits | unbounded |
| Per-request budget (3 attempts) | just below 3X |
| + Per-client budget (10% retry ratio) | ~1.1X |

**Throttle multiplier K**
| K | Behavior |
|---|---|
| 2 (preferred) | backend rejects ~1 per request processed; faster recovery propagation |
| 1.1 | backend rejects ~1 per 10 accepted; more aggressive |

Other numbers: datacenter cap example 100 tasks × 500 RPS = **50,000 QPS**; throttle history window **2 minutes**; tasks should withstand **2x–10x** their provisioned rate without falling over.

## Worked Example
**Retry layering in a dependency stack (Frontend → Backend A → Backend B → DB Frontend).** The DB Frontend is overloaded and rejects a request with "task overloaded." Backend B (the layer immediately above) retries — up to three attempts total, and only while its retry ratio is under 10%. If all three land on overloaded tasks (or the DB Frontend's attempt histograms show many retries and it returns "overloaded; don't retry"), Backend B stops and returns to Backend A either "overloaded; don't retry" or a degraded response. Backend A does not retry; it makes the same choice toward the Frontend. Result: one user action produces at most ~3 attempts on the DB, not 3^depth.

**Batch connection burst.** A giant batch job spins up thousands of worker clients at once, flooding backends with connection negotiation. Mitigation: require batch clients to go through a **batch proxy** (batch client → batch proxy → backend); only the proxy suffers, it uses fewer connections and larger subsets, and higher-priority clients are shielded.

## Key Takeaways
1. Measure capacity and request cost in normalized CPU (and other resources if needed), not QPS.
2. Enforce per-customer quotas so global overload only hurts the customer exceeding its share.
3. Implement adaptive client-side throttling (K=2 default) so rejections don't overload backends.
4. Tag every request with one of four criticalities at the edge, propagate it, and shed lowest first.
5. Protect each task with a local utilization signal (executor load average) and criticality-based thresholds.
6. Cap retries at three per request and 10% per client, retry only one layer up, and use "overloaded; don't retry."
7. Account for connection load; route big batch jobs through a batch proxy.

## Connects To
- **Ch 20**: subsetting and Weighted Round Robin that this chapter complements.
- **Ch 22**: what happens when overload isn't handled — cascading failures; retries, deadlines, load shedding.
- **Ch 19**: cross-datacenter balancing as the first line of overload defense.
- **Ch 4**: SLOs determine which traffic is CRITICAL vs SHEDDABLE.
- **Ch 3**: error budgets frame acceptable degraded responses.
- **Doorman** (external): Google's cooperative distributed client-side rate limiting system.
- **Backpressure / admission control** (external): general concepts behind task-level rejection.
