# Chapter 22: Addressing Cascading Failures
*Authors: Mike Ulrich*

> "If at first you don't succeed, back off exponentially." — Dan Sandler
> "Why do people always forget that you need to add a little jitter?" — Ade Oshineye

## Core Idea
A **cascading failure** is a failure that grows over time through positive feedback: one part fails, raising the probability that other parts fail (e.g., one overloaded replica dies, pushing its load onto the rest). Prevent it by load testing to and past the breaking point, rejecting/degrading early and cheaply, bounding retries and deadlines, and — once it starts — fixing the trigger and drastically cutting load until the system stabilizes.

## Frameworks Introduced
- **Preventing Server Overload (in rough priority order)**:
  1. **Load test the server's capacity limits, and test the failure mode for overload** — the most important step; you can't predict which resource exhausts first without realistic testing.
  2. **Serve degraded results** — cheaper, lower-quality answers.
  3. **Instrument the server to reject requests when overloaded** — fail early and cheaply.
  4. **Instrument higher-level systems to reject requests** — rate limit at reverse proxies (per IP, vs DoS/abuse), at load balancers (indiscriminate or selective, e.g., drop background sync but keep interactive sessions), at individual tasks.
  5. **Perform capacity planning** — couple with performance testing; plan N+2. Necessary but not sufficient.
  - Why it works: each layer lowers the chance overload turns into crashes; crashes are what create the positive feedback loop.

- **Load Shedding and Graceful Degradation**: load shedding drops a proportion of traffic as the server nears overload; graceful degradation reduces the work per request.
  - When to use: as the built-in response to unexpected load shifts or capacity-planning failures.
  - How: per-task throttling on CPU, memory, or queue length (e.g., HTTP **503** when in-flight requests exceed a limit); switch FIFO to **LIFO** or **CoDel** to drop requests unlikely to be worth serving; prioritize/select by client. Degrade by searching an in-memory subset or using a cheaper ranking algorithm.
  - Decide: which metrics trigger it, what actions in degraded mode, at which layer (every layer or one choke point).
  - Keep in mind: it should trigger rarely; "the code path you never use is the code path that (often) doesn't work" — exercise it by running a small subset of servers near overload; alert when too many servers enter it; build a fast off-switch (e.g., config in Chubby, aware of synchronized-failure risk).
  - Failure mode: complex degradation logic can trip unintentionally or create feedback cycles.

- **Retry Discipline**:
  - Always use **randomized exponential backoff** (jitter), else retry ripples synchronize and amplify.
  - Limit retries per request.
  - Consider a **server-wide retry budget** (e.g., **60 retries/minute** per process; beyond that, fail).
  - Retry at one level only — retries multiply across layers (4 attempts at each of 3 layers = 4³ = **64** attempts on the DB).
  - Use clear response codes: separate retriable vs nonretriable; never retry permanent errors or malformed requests; return a specific "overloaded" status so callers back off.

- **Deadlines and Deadline Propagation**:
  - Always set a deadline; none or very high deadlines let past problems keep consuming resources.
  - Check remaining deadline before each stage (parse, backend call, process) — "you don't get credit for late assignments with RPCs."
  - **Deadline propagation**: set an absolute deadline high in the stack; every downstream RPC inherits the remainder (minus a few hundred ms for transit/post-processing). Consider an upper bound for noncritical backends.
  - **Cancellation propagation**: cancel downstream work when the upstream request dies, avoiding RPC leakage.
  - Exception: long checkpointed catch-up work may check the deadline only after writing a checkpoint.

- **Immediate Steps to Address Cascading Failures** (use incident management, Ch 14):
  1. **Increase resources** (may not suffice in a death spiral).
  2. **Stop health check failures/deaths** — temporarily disable health-check-driven restarts; distinguish *process health checking* (scheduler: "is this binary responding at all?") from *service health checking* (load balancer: "can it serve this class of requests now?").
  3. **Restart servers** — for GC death spirals, deadline-less in-flight requests, deadlocks; identify the cause first, canary slowly (restarts empty cold caches).
  4. **Drop traffic** — fix the trigger, cut load until crashing stops (even to **1%**), let most servers become healthy, ramp up gradually.
  5. **Enter degraded modes**.
  6. **Eliminate batch load** (index updates, data copies, stats gathering).
  7. **Eliminate bad traffic** (queries of death).

## Key Concepts
- **Cascading failure**: failure that grows via positive feedback across replicas, clusters, or layers.
- **Resource exhaustion**: running out of CPU, memory, threads, or file descriptors; effects feed each other and mask the root cause.
- **GC death spiral**: less CPU → slower requests → more RAM → more GC → even less CPU.
- **Watchdog**: thread that kills a server judged not to be making progress.
- **Queue management**: keep queues small relative to thread pool (≤50%) for steady traffic; Gmail often uses queueless servers.
- **Bimodal latency**: a small fraction of requests hang until the deadline and exhaust threads for everyone.
- **Latency cache vs capacity cache**: a latency cache can be lost and load still sustained; a capacity cache cannot — it's a hidden hard dependency.
- **Intra-layer communication**: backends talking to backends; risks distributed deadlock and load-amplifying proxying.
- **Query of Death**: an RPC whose contents crash the process.
- **Slack CPU**: overcommitted spare CPU in a cell; a dangerous safety net.

## Mental Models
- Think of a cascading failure as **hysteresis**: recovery requires dropping far below the load that triggered it (healthy at 10,000 QPS, cascade at 11,000; with 10% servers healthy you need ~1,000 QPS, not 9,000).
- Use **"always go downward in the stack"**: dependencies flow one way; fixing the lowest broken layer repairs the rest. Make clients redirect instead of backends proxying sideways.
- Think of **every resilience feature as a potential amplifier**: retries, shifting load off unhealthy servers, killing unhealthy servers, adding caches — each improves the normal case but can trade one outage for a bigger one.
- Use **distribution, not mean, latency** when diagnosing: bimodal latency hides in averages.

## Anti-patterns
- **Naive retries** (no backoff, many attempts, every layer): turns 100 QPS of overload into growing retry storms.
- **No deadline or deadlines orders of magnitude above mean latency**: thread exhaustion from a few hung requests.
- **Hardcoded downstream deadlines instead of propagation**: downstream servers work on requests already abandoned.
- **Load balancers that avoid any server that served errors**: removes capacity, increases load on the rest, snowballs.
- **Capacity caches posing as performance caches**: cold cache after turnup/restart/maintenance → outage.
- **Backends proxying to each other in the request path**: distributed deadlock; proxy traffic spikes exactly under overload.
- **Depending on slack CPU** or load testing beyond committed resource limits.
- **Pushing updates to many tasks at once or at peak**: process updates trigger cascades.
- **Restarting servers without understanding the cause**: shifts load or empties caches, amplifying the cascade.
- **Health checks that conflate process liveness with serving ability**: the scheduler kills overloaded tasks, shrinking capacity further.

## Code Examples
Naive retry loop (gRPC in Go):
```go
func exampleRpcCall(client pb.ExampleClient, request pb.Request) *pb.Response {
  // Set RPC timeout to 5 seconds.
  opts := grpc.WithTimeout(5 * time.Second)

  // Try up to 20 times to make the RPC call.
  attempts := 20
  for attempts > 0 {
    conn, err := grpc.Dial(*serverAddr, opts...)
    if err != nil {
      // Something went wrong in setting up the connection. Try again.
      attempts--
      continue
    }
    defer conn.Close()

    // Create a client stub and make the RPC call.
    client := pb.NewBackendClient(conn)
    response, err := client.MakeRequest(context.Background, request)
    if err != nil {
      // Something went wrong in making the call. Try again.
      attempts--
      continue
    }

    return response
  }

  grpclog.Fatalf("ran out of attempts")
}
```
What it demonstrates: the anti-pattern — immediate retries with no backoff/jitter, a high attempt cap, no retry budget, and no distinction between retriable and overload errors; it feeds the retry cascade below.

Formulas:
- Retry amplification across layers: attempts at bottom = Π(attempts per layer), e.g., 4³ = 64.
- Threads busy = QPS × latency (1,000 QPS × 0.1 s = 100 threads).

## Reference Tables
**Bimodal latency example** (10 frontends × 100 threads = 1,000 threads; normal 1,000 QPS at 100 ms)
| Scenario | Threads needed | Outcome |
|---|---|---|
| Normal | 100 | fine |
| 5% hang, 100 s deadline | 5,000 (50 QPS × 100 s) + 95 | only 19.6% served → **80.4% error rate** |

**Queue sizing**: queue 10x threads, 100 ms per request → a full queue means **1.1 s** per request. Steady traffic: queue ≤ 50% of thread pool.

**Deadline propagation example**
| Hop | Elapsed | Deadline passed downstream |
|---|---|---|
| A sets 30 s | 7 s processing | A→B: 23 s |
| B | 4 s processing | B→C: 19 s |

**Capacity planning**: breaking point 5,000 QPS/cluster, peak 19,000 QPS → ~6 clusters for **N+2**.

**Triggering conditions**: process death (Query of Death, cluster issues, assertion failures); process updates; new rollouts (check recent changes; revert); organic growth; planned changes, drains, or turndowns; request profile changes; resource limits (slack CPU vanishes).

## Worked Example
**Retry cascade.** A backend task is capped at 10,000 QPS (rejects beyond, as graceful degradation). The frontend sends 10,100 QPS; 100 QPS are rejected and retried a second later, so the backend sees 10,200 QPS with 200 failing, then 300, and so on — fewer requests succeed on first try, and file descriptors, memory, and CPU burn on retries until the task crashes and its load spreads to other tasks. Even if client demand drops to 9,000 QPS, the outage may persist if rejection is expensive or servers are unstable; you must drastically cut load until retries stop.

**Shakespeare cascade.** A Japanese documentary sends traffic to the Asian datacenter beyond capacity, while a major update runs there. Safeguards from the Production Readiness Review help — graceful degradation drops pictures and maps; timed-out RPCs are either not retried (pictures) or retried with randomized exponential backoff — but tasks still fail one by one and Borg restarts drive working capacity lower. SRE is paged and adds tasks, restoring service. Postmortem actions: GSLB redirects overload to neighboring datacenters; autoscaling is enabled.

## Key Takeaways
1. Load test each component until it breaks and beyond — gradual and impulse loads — and verify it recovers without human help.
2. Make servers reject early and cheaply (503s, small queues, LIFO/CoDel) and design degraded modes you actually exercise.
3. Retry with randomized exponential backoff, per-request limits, a server-wide retry budget, and at one layer only.
4. Always set deadlines, propagate them (and cancellations), and check remaining time before each stage.
5. Know whether your caches are latency or capacity caches; ramp load slowly onto cold clusters.
6. Avoid intra-layer calls; always go downward in the stack.
7. In a cascade: fix the trigger, separate process from service health checks, drop load aggressively, then ramp up.

## Connects To
- **Ch 21**: overload handling — client throttling, criticality, retry budgets — the per-task foundation.
- **Ch 20**: lame duck, health checks, and error-avoiding load balancing can fuel the snowball.
- **Ch 19**: GSLB/DNS shifting traffic between clusters can spread overload globally.
- **Ch 14**: use incident management when a cascade is underway.
- **Ch 15**: Shakespeare postmortem and action items.
- **Ch 17**: load and failure testing to find breaking points.
- **Ch 2**: Shakespeare sample service, Borg health checking, Chubby.
- **Ch 27**: launch readiness and capacity planning.
- **CoDel / exponential backoff and jitter (AWS)** (external): queue and retry techniques cited.
