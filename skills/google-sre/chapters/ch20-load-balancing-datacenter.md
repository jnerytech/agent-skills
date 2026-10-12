# Chapter 20: Load Balancing in the Datacenter
*Authors: Alejandro Forero Cuervo (edited by Sarah Chavis)*

## Core Idea
Inside a datacenter, client tasks choose which backend task serves each request. Good balancing means (1) detecting unhealthy backends (**lame duck state**), (2) limiting connections with **deterministic subsetting**, and (3) choosing a backend per request with a policy that uses backend-reported load (**Weighted Round Robin**) — because poor balancing turns reserved capacity into wasted capacity.

## Frameworks Introduced
- **The Ideal Case / Wasted Capacity**: you can only send traffic to a datacenter until the *most loaded* task hits capacity; every other task's idle headroom is wasted.
  - When to use: to quantify the cost of imbalance.
  - How: with task 0 the most loaded, waste = Σᵢ (CPU[0] − CPU[i]). "Wasted" = reserved but unused. E.g., reserving 1,000 CPUs but only able to use ~700.
  - Why it works: makes the spread between least- and most-loaded tasks the target metric, not average utilization.

- **Lame Duck State**: a backend can be *Healthy*, *Refusing connections*, or *Lame duck* (still listening and able to serve, but explicitly asking clients to stop sending requests).
  - When to use: clean shutdowns, code pushes, maintenance, restarts; also slow initialization (connect early, signal readiness explicitly).
  - How (clean shutdown):
    1. Job scheduler sends SIGTERM.
    2. Backend enters lame duck (RPC API call in the SIGTERM handler) and asks clients to send new requests elsewhere.
    3. Requests started before (or before clients noticed) finish normally.
    4. Active requests drain to zero.
    5. After a configured interval (rule of thumb **10s–150s**), the task exits or is killed.
  - Propagation: active clients are told directly; inactive clients still send periodic UDP health checks, so lame duck reaches all clients in **1–2 RTT**.
  - Why it works: no errors served to the "unlucky" in-flight requests during shutdown. Contrast with simple **flow control** (mark backend unhealthy at **100** active requests per client), which only protects against extreme overload and can backfire with long-lived requests, making all backends unreachable.

- **Subsetting**: limit the pool of backends each client connects to.
  - When to use: whenever clients × backends would create too many long-lived connections (memory + CPU for health checks on both ends).
  - How: choose a **subset size** (typically **20–100** backends) and a selection algorithm. Use a larger subset when (a) clients are far fewer than backends (else some backends get no traffic), or (b) client load is bursty/imbalanced (e.g., large fan-out "read all followers" requests).
  - Selection algorithm requirements: assign backends uniformly (10% overload on one backend ⇒ overprovision all by 10%); minimize churn on restarts/failures; handle resizes without knowing counts in advance.

- **Deterministic Subsetting** (Google's solution): group clients into rounds; each round shares one shuffled backend list (seeded by round number); each client in a round takes a distinct contiguous slice.
  - When to use: instead of random subsetting, which is very uneven.
  - How: see code below. Shuffle so a client's subset isn't consecutive tasks (which may all be updated together); use a different seed per round so a failed backend's load spreads over *all* remaining backends, not just its subset-mates.
  - Result: backend connection counts differ by at most 1.

- **Load Balancing Policies** (how a client picks a backend within its subset):
  1. **Simple Round Robin** — rotate among connectable, non-lame-duck backends. Up to **2x** CPU spread, due to: small subsetting, varying query costs, machine diversity, unpredictable performance factors.
  2. **Least-Loaded Round Robin** — round robin among backends with the fewest active requests *from this client*. Must count recent errors as active requests to avoid sinkholing. Still ~2x spread in large services.
  3. **Weighted Round Robin** — each backend reports QPS, errors/s, and utilization (CPU) in every response, including health checks; clients keep a "capability" score per backend and weight distribution by it; failed requests incur a penalty. Drastically reduced spread in practice.

## Key Concepts
- **Backend task / client task**: server processes handling queries vs processes holding connections and choosing backends; services typically 100–1,000 processes (min 3, max >10,000).
- **GFE (Google Frontend)**: HTTP reverse proxy that applies these algorithms plus Ch 19's.
- **Flow control**: client marks a backend unhealthy when its active-request count hits a limit (e.g., 100).
- **Lame duck**: backend serving but asking clients to stop sending new requests.
- **Subset size**: number of backends each client connects to (typically 20–100).
- **Churn**: replacement-backend selection causing new TCP connections and negotiation overhead.
- **Inactive connection mode**: idle connections drop TCP for UDP with less frequent health checks.
- **Sinkholing**: an unhealthy task returns fast errors, looks lightly loaded, and attracts more traffic.
- **GCU (Google Compute Unit)**: virtual CPU unit normalizing CPU rates across architectures.
- **Antagonistic neighbors**: unrelated co-located processes degrading performance (up to 20%).

## Mental Models
- Think of datacenter capacity as **limited by the hottest task**, not the average — every point of spread is wasted reservation.
- Use **lame duck for planned exits** and health checks for unplanned ones: let backends say "please go elsewhere" before they disappear.
- Think of **client-local signals as a partial, stale view**: a client's active-request count ignores other clients and network wait time; backend-reported utilization (Weighted RR) closes the gap.
- Use **fast errors as a warning sign**, not a sign of spare capacity — count errors as load.

## Anti-patterns
- **Random subsetting**: needs subset sizes near 75% for even load; at 10% subset, least loaded gets 50% of average, most loaded 150%.
- **Unshuffled or same-seed subsets**: consecutive tasks fail together during rolling updates; a failed backend's load only lands on its subset-mates, compounding as more fail.
- **Flow-control-only health detection**: can't distinguish unhealthy from slow; a too-low limit has made all backends unreachable.
- **Least-Loaded RR without counting errors**: sinkholes traffic into a task serving 100% errors.
- **Unbounded per-request cost**: expensive requests (1000x+ the cheapest) make some tasks unlucky; cap work per request (e.g., pagination), though it adds consistency complications.
- **Assuming homogeneous machines/performance**: CPU differences, neighbors, and post-restart warmup (e.g., Java JIT) all skew load.

## Code Examples
```python
def Subset(backends, client_id, subset_size):
  subset_count = len(backends) / subset_size

  # Group clients into rounds; each round uses the same shuffled list:
  round = client_id / subset_count
  random.seed(round)
  random.shuffle(backends)

  # The subset id corresponding to the current client:
  subset_id = client_id % subset_count

  start = subset_id * subset_size
  return backends[start:start + subset_size]
```
What it demonstrates: deterministic subsetting — clients within a round get disjoint slices of the same shuffled list; different rounds use different shuffles, so connection load is uniform and failure load spreads widely.

Wasted-capacity formula: `waste = Σ_i (CPU[0] − CPU[i])`, task 0 = most loaded.

## Reference Tables
**Random subsetting (300 clients, 300 backends)**
| Subset size | Backends/client | Least loaded | Most loaded |
|---|---|---|---|
| 30% | 90 | 63% of avg (57 conns) | 121% (109 conns) |
| 10% | 30 | 50% (15 conns) | 150% (45 conns) |
| ~75% | 225 | needed for roughly even load — impractical | |
| Deterministic, 10 of 300 | 10 | every backend identical | |

**Policy comparison**
| Policy | Uses backend info? | Observed spread | Main pitfall |
|---|---|---|---|
| Simple Round Robin | No | Up to 2x CPU | Ignores cost/machine variance |
| Least-Loaded RR | Client-local active requests | ~2x in large services | Sinkholing; active count ≠ capability; ignores other clients |
| Weighted RR | Yes: QPS, errors, utilization | Drastically reduced | Needs backend reporting |

Other numbers: flow-control limit **100** active requests; lame-duck drain **10–150s**; lame duck propagates in **1–2 RTT**; antagonistic neighbor impact **up to 20%**; one Java backend averages **15 ms** CPU/query but some queries take **10 s**; example GCU equivalence: 2 CPU on slow machine X = 0.8 CPU on fast machine Y.

## Worked Example
**Deterministic subsetting with 12 backends, subset size 3, 10 clients.** subset_count = 12/3 = 4, so each round has 4 clients. Round 0 shuffles to [0, 6, 3, 5, 1, 7, 11, 9, 2, 4, 8, 10]; round 1 to [8, 11, 4, 0, ...]; round 2 to [8, 3, 7, 2, ...]. Within a round: subset[0] = shuffled[0..2], subset[1] = [3..5], subset[2] = [6..8], subset[3] = [9..11]. Client i uses subset[i % 4]: clients 0, 4, 8 → subset 0; 1, 5, 9 → subset 1; etc. Each round assigns every backend to exactly one client, so with 10 clients (last round partial) every backend gets 2 or 3 clients. If backend 6 fails, its clients in round 0 are spread differently from those in rounds 1–2, so its load lands on many backends instead of only its two subset-mates.

**Least-Loaded RR sinkhole.** A task goes bad and returns "I'm unhealthy!" errors instantly. Its active-request count stays near zero, so every client picks it first — it absorbs a large share of traffic and fails it. Fix: count recent errors as active requests.

## Key Takeaways
1. Measure imbalance as the gap from the most loaded task — that gap is reserved-but-unusable capacity.
2. Implement lame duck state in the SIGTERM handler and drain for 10–150s so shutdowns and pushes serve no errors.
3. Use deterministic subsetting (shuffled, per-round seeds) with subset sizes of ~20–100; enlarge when clients are few or bursty.
4. Don't stop at Round Robin; feed backend-reported utilization into a Weighted Round Robin policy.
5. Treat errors as load in any least-loaded policy to prevent sinkholing.
6. Normalize heterogeneous hardware (GCU-style units) and prewarm restarted tasks in lame duck before serving.
7. Cap per-request work where feasible; large cost variance defeats any balancing policy.

## Connects To
- **Ch 19**: the upstream layer (DNS + VIP) that delivers traffic to the datacenter.
- **Ch 21**: overload handling, client-side throttling, and criticality when balancing isn't enough.
- **Ch 22**: lame duck, health checks, and error-avoiding policies can amplify cascading failures.
- **Ch 2**: Borg scheduling, GFE, and RPC (Stubby) infrastructure.
- **Ch 8**: rolling pushes are why churn-minimizing subsetting and lame duck matter.
- **Power of two choices / least-connections** (external): related load balancing heuristics.
