# Chapter 17b: The Confident O(n²): Performance as a Contract

## Core Idea
Some AI defects arrive with a fully green suite: the code is correct by every check you have, but its cost curve is invisible at fixture scale (twelve rows) and unaffordable at production scale — "the defect is not in the answer; it is in the invoice." The fix is the book's standard move: write the cost expectation down once as a committed **performance contract**, then let machines enforce it — deterministic operation counts in the inner loop (QuickPerf), time and load budgets in the nightly ring (JMH, k6/Gatling) — and treat cost as an attack surface.

## Frameworks Introduced
- **Performance as a Contract**: the budget is a committed, versioned artifact, not advice.
  - When to use: hot paths, endpoints with SLAs, algorithms that *are* the product, any repository/ORM access in a loop.
  - How: declare intent in source with `@AIPerformance(constraint = "...")` (guidance the generator reads), then enforce it with a committed contract: "this use case issues one query," "this endpoint answers < 200 ms at p95 at the declared load," "this parser allocates ≤ X per document." Same move as freezing the payload with a committed `openapi.yaml` (Ch 18).
- **Count Operations in the Inner Loop; Measure Time in the Outer One**: choose the enforcement point by determinism.
  - When to use: deciding where each performance assertion lives.
  - How: never assert wall-clock time on shared CI runners (40 ms on a laptop, 140 ms beside a noisy neighbor — flaky by design, violating Ch 5b's zero-flakiness law). In the 30-second inner loop assert the **cost model**: query counts (`@ExpectSelect`), heap allocation (`@ExpectMaxHeapAllocation`). In the nightly ring, on pinned hardware against a committed baseline: JMH microbenchmarks for hot algorithms, k6/Gatling thresholds for endpoints, wired as Ch 21 branch gates for release.
- **The Confident-but-Quadratic Zoo**: five recognizable specimens to spot on sight (see table).
  - When to use: reviewing any AI-generated data access, loop, cache or regex.
  - How: map each specimen to its instrument — query counts catch N+1 and chatty loops; allocation budgets catch memory vacuums; benchmarks catch quadratic accumulators; adversarial input catches backtracking regexes.
- **The Complexity Bomb (cost as attack surface)**: an attacker can make your endpoint expensive on demand without it being wrong.
  - When to use: endpoints taking attacker-controlled input — regexes, hash keys, compressed payloads.
  - How: give the Ch 20 Attacker Agent a second objective function: "the p95 contract says 200ms; find the input that makes it miss by the widest margin." Freeze each blow-up found as a committed red test with the hostile input.

## Key Concepts
- **Demo-scale lie**: fixtures have twelve rows, where O(n²) and O(n log n) are indistinguishable; production is a different regime no functional test crosses.
- **Three reasons the generator writes slow code**: tutorial-shaped training data (naive = idiomatic at 10 items); it never feels latency (no feedback path to a p95 chart); fluency hides cost (the efficient version carries the batching/pagination/join that makes cost visible, so it looks uglier).
- **Cost model assertion**: a deterministic count (queries, allocations) instead of elapsed time.
- **QuickPerf**: open-source JUnit extension (quickperf.io) that asserts SQL and allocation counts on existing tests.
- **Committed baseline**: a JMH result in the repo that turns "it got slower" into a diffable fact outside the model's writable scope.
- **Load threshold**: k6/Gatling encoding of the declared traffic shape plus p95/error-rate budgets, versioned with code.
- **Algorithmic complexity attack**: crafted non-matching strings (backtracking regex), colliding hash keys, decompression bombs.
- **Internal pair**: Ch 17 hides in timing; Ch 17b hides in scale — both pass every functional test.

## Mental Models
- Think of a functional test as asserting *what* comes back, never *what it cost*.
- Use deterministic counts where noise is fatal (inner loop) and milliseconds where noise is tolerable (nightly, pinned hardware).
- Think of the budget as outside the model's writable scope: it may propose any implementation, not a new number.
- Treat the failure message as the prompt: "QuickPerf: expected 1 SELECT, got 51. Fix the query with a fetch join; do not change the assertion."

## Anti-patterns
- **N+1 query**: lazy relation touched inside the loop; the ORM makes each query look like field access.
- **Chatty loop**: one HTTP call/cache lookup/SELECT per item where a batch endpoint or `IN` clause exists — self-inflicted distributed DoS at 10,000 items.
- **Quadratic accumulator**: `list.contains` inside a loop over the same list; line-by-line string concatenation; nested scans a `Set` or join would linearize.
- **Memory vacuum**: `findAll()` into a `List` then filtered in Java; unbounded in-memory cache "for performance" = slow-motion `OutOfMemoryError`.
- **Backtracking regex**: nested quantifiers like `(a+)+`, exponential on crafted non-matches (Stack Overflow down 34 minutes in 2016; Cloudflare edge offline July 2019).
- **Wall-clock assertions in unit tests**: flaky by construction.
- **Performance budgets in a dashboard nobody opens**: advice, not a gate.
- **Letting the AI "fix" the failing budget by changing the assertion**: fix the query, not the test.

## Code Examples
```java
@QuickPerfTest
class OrderHistoryServiceTest {

    @ExpectSelect(1)   // the performance contract: one query, not N+1
    @Test
    void loads_order_history_in_a_single_query() {
        List<OrderView> history = orderHistoryService.forCustomer(CUST_42);
        assertThat(history).hasSize(50);
    }
}
```
- **What it demonstrates**: a deterministic cost-model assertion that fails with "expected 1 SELECT but got 51" plus the offending statements — the ArchUnit experience pointed at cost.

```javascript
export const options = {
  thresholds: {
    // the endpoint's performance contract, versioned with the code
    http_req_duration: ['p(95)<200'],
    http_req_failed:   ['rate<0.01'],
  },
};
```
- **What it demonstrates**: an endpoint budget that fails the nightly run as a release branch gate.

## Reference Tables
| Ring | Instrument | Asserts | Determinism |
|---|---|---|---|
| Inner loop (≈30 s) | QuickPerf `@ExpectSelect`, `@ExpectMaxHeapAllocation` | Query and allocation counts | Deterministic |
| Nightly | JMH + committed baseline | Algorithm throughput within declared tolerance | Pinned hardware |
| Nightly / release gate | k6 or Gatling thresholds | Endpoint p95 latency, error rate at declared load | Pinned env |
| Adversarial | Attacker Agent (Ch 20) | Worst-case input vs budget | Frozen as red test |

| Specimen | Shape | Caught by |
|---|---|---|
| N+1 query | Lazy load per element | `@ExpectSelect` |
| Chatty loop | Remote/cache/SQL call per item | Query/call counts |
| Quadratic accumulator | `contains` in loop, string concat, nested scan | JMH baseline |
| Memory vacuum | `findAll()` + in-Java filter, unbounded cache | `@ExpectMaxHeapAllocation` |
| Backtracking regex | Nested quantifiers `(a+)+` | Attacker Agent + frozen hostile input |

## Worked Example
Request: order history with product thumbnails. The assistant ships in ninety seconds — repository call, mapping loop, DTO, green behavioral test asserting fifty rows. `mvn test` fails `loads_order_history_in_a_single_query`: **expected 1 SELECT but got 151**. The loop touched `order.getItems()` per order and each item touched `product.getThumbnailUrl()` — two nested lazy loads, 50 orders → 151 queries, at fixture scale, on a laptop, before any human read the diff. The failure text goes back verbatim plus "fix the query, not the test." The assistant returns a fetch join and a two-level `@BatchSize`; one query; behavioral test still green. Human contribution: writing `@ExpectSelect(1)` once months ago and pasting one failure message. No profiler opened. The test stays forever, so a future session repeating the mistake hits the same wall.

## Why It Works / Failure Mode
- **Works** because it forces an invisible property (cost) into a deterministic, local, pasteable signal — a query count for the curve, as a barrier was for the race in Ch 17 — and because the budget lives where the generator cannot rewrite it. It also answers the half of the Inquisitor's "does it scale?" question that static review cannot ("I can see an O(n²) join in `OrderReconciler`; I cannot tell you whether your load ever makes that matter").
- **Breaks** at the boundary of human imagination: a performance contract catches regressions against declared budgets and traffic shapes; it does not discover traffic patterns you failed to imagine, size capacity, or replace production profiling. The k6 load model is a hypothesis; "the world gets a vote." What it guarantees: the cost curve changes only when a human decides, never as a silent side effect of a fluent completion.

## Key Takeaways
1. Green functional tests say nothing about cost; assert cost explicitly.
2. In the inner loop, assert deterministic operation counts (queries, allocations), never milliseconds.
3. Put timing budgets in the nightly ring — JMH baselines and k6/Gatling thresholds on pinned hardware — as release gates.
4. Learn the zoo: N+1, chatty loop, quadratic accumulator, memory vacuum, backtracking regex.
5. Paste budget failures back verbatim and forbid changing the assertion.
6. Treat cost as an attack surface: aim the Attacker Agent at your budgets and freeze its findings as tests.

## Connects To
- **Ch 2**: AI code looks most trustworthy where it deserves most scrutiny.
- **Ch 4**: `@AIPerformance` as the in-source declaration slot.
- **Ch 5 / 5b**: ArchUnit-style enforcement; zero-flakiness law and the 30-second inner loop.
- **Ch 17**: the sibling internal failure hiding in timing.
- **Ch 18**: committed `openapi.yaml` — the same freeze-the-contract move; next, the external contracts.
- **Ch 20**: Attacker Agent with a cost objective.
- **Ch 21**: load ring as a branch gate. **Ch 22**: completes the Inquisitor's scaling answer.
- **ReDoS / algorithmic complexity attacks**: Stack Overflow 2016, Cloudflare 2019.
