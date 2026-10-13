# Chapter 6b: The Log Is a Feedback Loop

## Core Idea
An agent running your code gets back one bit (exit code) unless the runtime narrates itself; a structured, decision-level log is the cheap, permanent channel that tells the agent *what the system did*, and it doubles as a verification and bug-hunting instrument. Log quality is no longer hygiene — it is a performance parameter of your agent tooling.

## Frameworks Introduced
- **Two Telemetry Channels**: Ch 6's living diagram answers "what does my system look like now?" on every build; the log answers "what did my system just do?" on every run. Both are pure telemetry, neither prevents anything.
  - When to use: deciding what feedback an agent loop is missing.
  - How: give the agent both structure (diagram) and behavior (log). One run produces two returns — the exit code (did it work? one bit) and the log (branch taken, deciding values, timing). Put a filter step between them: log to a file, agent greps it; never flood the context window.
- **The Log Has to Tell a Story (three rules)**: a reader who was not present can reconstruct what happened and why.
  - When to use: writing or reviewing any log statement; instructing an agent on logging.
  - How: (1) **Log decisions, not positions** — "chose rule VOLUME_TIER_2 because subtotal crossed 200," not "entering method"; the branch not taken leaves no trace otherwise. (2) **Carry identity on every line** — a correlation ID (e.g. `orderId`) turns interleaved output into a filterable narrative. (3) **Prefer structured fields to prose** — `orderId=A-1187 discount=12.45` is queryable; a sentence must be parsed. Selection standard (stolen from Log20): a log line earns its place by how many possible executions it rules out.
- **Levels Are a Budget, Not a Vocabulary**: each level has an audience and a spending limit; enforce the asymmetry — in production spend INFO like money, in a debug run spend words freely.
  - When to use: setting a level policy; resolving INFO-vs-DEBUG disputes (developers agree only ~0.75–0.81 AUC).
  - How: apply the budget table below; keep DEBUG on in dev, CI and the agent's run profile; write the policy into the context file/spec, not tribal memory.
- **The Log as Verification**: tests assert outcomes; log assertions assert the *path* taken.
  - When to use: load-bearing behavior a green test can't prove — cache, retry, fallback, authorization, tenant scoping, idempotency key reuse.
  - How: emit a named event at the contract point; capture output in a test (`OutputCaptureExtension`, pytest `caplog`, Logback `ListAppender`, Go captured `slog` handler) and assert the sequence. Treat asserted event names/fields as an interface — renaming is a breaking API change. Lighter variant: after a change, have the agent run the scenario at DEBUG and read the narrative back as prose ("confirm from the log the request took the new validation branch").
- **The Log as a Bug Hunt**: two disciplines — **Instrument before you theorize** and **Ship the missing log line with the fix**.
  - When to use: any nontrivial bug the agent is asked to fix.
  - How: before proposing a fix, the agent adds log lines that distinguish its hypothesis from alternatives, runs the repro, pastes real output. The fix is complete only when the diff contains the line that would have made the cause obvious in one read — and that line stays. Over time the log becomes dense exactly where the system is fragile.

## Key Concepts
- **Blind-between-runs contract**: the default agent condition — change any file, run anything, but only told "worked/broke."
- **Confident narrative**: a model deprived of evidence generates the most plausible explanation from code shape and training data, then edits working code to fit it.
- **Past-tense artifact**: the log is the only repo artifact reporting what *did* happen; source, types, tests, diagrams describe what *should*.
- **Correlation identifier**: a per-request ID on every line, making one story grep-able out of ten thousand interleaved requests.
- **Load-bearing log event**: a log event asserted in tests — effectively a spec clause written in the logging framework.
- **Debug run profile**: one agent-owned command that runs the app/scenario at DEBUG with output to a known path.
- **Failure-only default output**: green run prints one line; red run prints the captured narrative for the failing case only.
- **Log the trigger, link the detail**: log an identifier for a large payload and write the payload beside it.

## Mental Models
- Think of the log as **part of the interface between the agent and your system** — design it like one (concise, informative, not raw dumps, per SWE-agent).
- Think of a debugger as a **human-latency tool**; the agent loop is a batch loop (generate, build, run, read, adjust ×100/day) — a debugger reinserts a human, a log does not. Use a debugger only when you have a reliable repro and need exact state at one line.
- Use the log as a **queryable artifact, not a message**: file + filter, never pasted whole into the prompt (Ch 3's context budget).
- Structure without behavior is **a map with no traffic report**.

## Anti-patterns
- **Entry/exit logging ("processOrder called", "ok", "done")**: every line true, whole thing worthless — no subject, branch, quantity or outcome; identical text for different inputs.
- **Values without identity / outcomes without inputs**: concurrency shreds the story into confetti (Ch 17's failure mode in the diagnostic layer).
- **Pasting a verbose debug run into the prompt**: more tokens in 30s than the whole codebase; buries the key detail in the middle (Ch 3).
- **Trusting a green retry test**: the stubbed gateway succeeds first try, so the retry branch never executes; the diff is correct and the bug invisible.
- **INFO inside loops**: INFO rate must be O(requests), never O(loop iterations).
- **Logging that slows the system**: someone will turn it off under load, and a disabled control is not a control.
- **Log-asserting commentary lines**: couples tests to strings that aren't contracts — brittle (Ch 20b).

## Code Examples
```java
@ExtendWith(OutputCaptureExtension.class)
class PricingCacheTest {
  @Test
  void secondLookupIsServedFromCache(CapturedOutput output) {
    pricingService.priceFor("SKU-9");
    pricingService.priceFor("SKU-9");
    assertThat(output).contains("cache.miss sku=SKU-9");
    assertThat(output).contains("cache.fill sku=SKU-9");
    assertThat(output).containsOnlyOnce("cache.miss sku=SKU-9");
    assertThat(output).contains("cache.hit sku=SKU-9");
  }
}
```
- **What it demonstrates**: asserting the path, not just the outcome — fails if an agent "optimizes" the cache into a passthrough while refactoring.

```markdown
## Logging
- Structured key-value events: `domain.event key=value`, one event per line.
- Every line inside a request carries `correlationId`.
- INFO: state transitions an operator would ask about. Bounded per request. Never inside a loop.
- DEBUG: the decision narrative. Log the branch taken and the values that decided it. Be generous.
- ERROR only when a human must act. Log the cause, not just the symptom.
- When you fix a bug, add the DEBUG line that would have made it obvious, and keep it.
- Log events asserted in tests are contracts. Renaming one is a breaking change.
```
- **What it demonstrates**: the level policy written into the context file so the agent follows it on every new file.

## Reference Tables
| Level | Audience | Budget | Test for inclusion |
|---|---|---|---|
| ERROR | On-call human | Rare; every line is a claim | Someone must do something. If nobody acts, it is not an error |
| WARN | On-call human, later | Rare | Degraded but handled: retry succeeded, fallback used, quota near limit |
| INFO | Operator, in production | Scarce, bounded per unit of work | A state transition an operator would ask about; rate O(requests), never O(loop iterations) |
| DEBUG | Developer and agent | Generous, spend freely | The story: decisions, branches, the values that decided them |
| TRACE | Developer, briefly | Unbounded, short-lived | Payloads, dumps, wire-level detail nobody keeps enabled |

**Evidence base**: Yuan et al. — 84% of 198 production failures (Cassandra, HBase, HDFS, MapReduce, Redis) had every triggering event already in the log, median 824 messages per failure. Errlog — >50% of 250 failures not diagnosable from existing logs; auto-inserting log points at generic error conditions cut diagnosis time 60.7% at 1.4% overhead. LDB — feeding intermediate values per basic block improved LLM debugging accuracy by up to 9.8 points. SWE-agent — concise, informative environment feedback beats raw output.

## Worked Example
**Nothing-log vs. narrative log for the same execution.**

Before:
```
INFO  OrderService - processOrder called
DEBUG OrderService - validating
DEBUG OrderService - ok
INFO  OrderService - done
```
After:
```
INFO  order.received    orderId=A-1187 customerId=C-42 items=3 total=249.00 currency=EUR
DEBUG order.pricing     orderId=A-1187 rule=VOLUME_TIER_2 discount=12.45 basis=subtotal
DEBUG inventory.reserve orderId=A-1187 sku=SKU-9 requested=2 available=2 result=RESERVED
WARN  payment.retry     orderId=A-1187 attempt=2 reason=GATEWAY_TIMEOUT backoffMs=400
INFO  order.confirmed   orderId=A-1187 paymentRef=PAY-77 elapsedMs=612
```
Five lines answer unasked questions: which pricing rule fired and on what basis; reservation was tight (2 of 2); payment succeeded *on retry*, so the gateway is flaky and success is not evidence of health; total latency 612 ms. `grep orderId=A-1187` extracts this story from a file of ten thousand interleaved requests.

## Why It Works / Failure Mode
- **Log as verification** works because a test can only see outcomes, and caches/retries/fallbacks produce correct outcomes even when broken; a contract event makes the path observable and assertable. It breaks when teams assert on commentary lines (brittle string coupling) or rename asserted events without treating it as an API change.
- **Instrument before you theorize** works because the model's default is fluent, ungrounded narrative; forcing a distinguishing log line plus a real run converts a "guess with good grammar" into a tested hypothesis (same mechanism LDB measured). It breaks when output is dumped whole into context instead of filtered from a file — the signal drowns.

## Key Takeaways
1. A test tells you whether it worked; the log tells you what happened — the second is what makes an agent useful instead of merely fast.
2. Log decisions with identity and structured fields; positions are recoverable from stack traces, decisions are not.
3. Levels are budgets: INFO scarce and bounded per request, DEBUG generous and always on in dev, CI and the agent's run profile.
4. Assert on contract log events (cache hit, retry fired, tenant filter applied) to verify paths green tests can't see.
5. Every bug fix ships with the log line that would have made the bug obvious.
6. Feed logs back as files to filter, with failure-only default output — never as pasted walls.
7. Wiring takes under a day: agent-owned debug profile, CI log artifacts on failure, level policy in the context file, a read-the-story habit at loop end.

## Connects To
- **Ch 6**: the living diagram — the structure channel; this is the behavior channel.
- **Ch 6c**: the third channel, documentation, where the logging policy is written down.
- **Ch 3**: context window as budget; logs are the easiest way to blow it.
- **Ch 5b**: the batch agent loop that a debugger would break.
- **Ch 7**: conventions belong in the spec; load-bearing log events are spec clauses.
- **Ch 17**: concurrency shredding narratives without correlation IDs.
- **Ch 20b**: green suites over wrong implementations; brittle assertions.
- **Observability (Majors et al.)**: structured, high-cardinality events.
- **Kernighan & Pike, *The Practice of Programming***: judicious print statements over stepping a debugger.
- **Humble & Farley "if it hurts, do it more often"**: remove the blind spot while standing in it.
