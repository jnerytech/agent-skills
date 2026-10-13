# Chapter 17: The Asynchronous Trap

## Core Idea
AI assistants are structurally — not temporarily — bad at concurrency: correctness depends on Java Memory Model properties (happens-before, visibility, atomicity) that are invisible in source text and appear only under rare interleavings, so code that *looks* correct and code that *is* correct are almost disjoint sets. Sequential tests (including the ones the AI writes) give false confidence; the only reliable signal is a stress harness that **forces the collision** deterministically, with detectors that turn a hang into a named diagnosis the AI can fix.

## Frameworks Introduced
- **Forced-Collision Testing (async-test-lib)**: invert "hope the OS scheduler exposes the race" into "manufacture the worst-case interleaving on purpose."
  - When to use: any code touching shared mutable state — caches, counters, lazy singletons, thread pools, `@Async` methods, anything called "thread-safe."
  - How: annotate with `@AsyncTest(threads = N, invocations = M)`; the JUnit 5 extension parks all threads at a `CyclicBarrier` one instruction before your code, releases them simultaneously, repeats; assert the post-condition in `@AfterEach`; enable the relevant detector per test.
- **Treat Concurrency as Adversarial (the four-step workflow)**: a standing rule, because the AI will not volunteer it.
  - When to use: whenever the assistant produces concurrent code.
  - How: (1) do not accept the AI's own concurrency test as evidence — it will be sequential and pass; (2) demand an `@AsyncTest`: "Write an async-test with at least 20 threads and 100 invocations that asserts the post-condition after concurrent access, with the relevant detector enabled"; (3) run it and **expect red**; (4) paste the detector's diagnosis back: "async-test-lib reports a visibility violation on `cache`. Fix it and keep the test."
- **Annotation + Async-Test Closure**: the annotation states the invariant; the async-test proves it.
  - When to use: any class meant to be concurrent.
  - How: mark it `@AIThreadSafe(strategy = LOCK_FREE, note = "...")` so every assistant's generated config carries the guarantee; off Java/VibeTags, use a CLAUDE.md note plus `// thread-safe: lock-free, do not introduce locks`.
- **Structurally Bounded Concurrency**: "if you spawn threads, they must be structurally bounded."
  - When to use: Java 21+ virtual threads, fan-out/fan-in, partial-result aggregation.
  - How: require `StructuredTaskScope` over ad-hoc `Thread.startVirtualThread()`; for quorum/partial results, subclass it and `shutdown()` in `handleComplete` once the quorum is met; name this idiom in CLAUDE.md/AGENTS.md because it is too new to be in the model's muscle memory. Still force collisions — scopes bound lifecycle, not state.

## Key Concepts
- **Java Memory Model (JSR 133, Java 5, 2004)**: the happens-before/visibility/atomicity rules that determine concurrent correctness and are invisible in source.
- **Read-modify-write**: `counter++` is three steps, not atomic — the canonical atomicity violation (check-then-act/TOCTOU family).
- **Loop-Invariant Code Motion**: C2 may hoist a non-volatile flag read out of a loop, turning a poll into an infinite loop — legal per the JLS.
- **`volatile`**: forbids the hoist, inserts barriers, establishes the happens-before edge.
- **Total Store Order (x86-64) vs weak ordering (ARM)**: racy code often passes on Intel/AMD and corrupts on Apple Silicon, Graviton, Ampere.
- **Heisenbug / thread-starvation illusion**: races that surface only under load or GC pauses; threads rarely switch exactly at the race on multicore machines.
- **Detectors**: opt-in, zero-overhead-when-off diagnostics — deadlock with lock-chain analysis, visibility, ABA and broken double-checked locking, race tracking, atomicity, recursive `computeIfAbsent`.
- **AsyncAssert**: polls a condition with timeout for eventual side effects, replacing the AI's default `Thread.sleep`.
- **Virtual Thread Illusion**: virtual threads solve throughput, not concurrency, and make racy code look more sequential and correct.
- **Eight Fallacies of Distributed Computing (Deutsch, 1994)**: tutorial-trained AI assumes the network is reliable, latency zero, etc. — calls remotes like local methods, never retries or times out.

## Mental Models
- Think of a passing run of a racy program as proof only that the breaking interleaving didn't happen *that time*.
- Think of the compiler as an adversary: the defect may live in an optimization the language allows, not in the silicon.
- Use your laptop's green as weak evidence — x86 TSO hides reorderings ARM exposes; run async-tests on ARM in CI.
- Make the AI build the gun aimed at its own code: a named detector diagnosis is the high-signal input that lets it fix instead of guess.

## Anti-patterns
- **Accepting the AI's single-threaded "thread-safe" test**: green forever, tests nothing about the property that is wrong.
- **Non-volatile stop flags**: C2 hoists the read; the spinning thread never sees the write.
- **Broken double-checked locking**: AI "optimizes" a lazy initializer without a `volatile` field.
- **Inconsistent lock ordering**: two methods acquiring the same two locks in opposite order → deadlock.
- **Recursive `computeIfAbsent` on the same `ConcurrentHashMap`**: violates the "mapping function must not modify the map" contract; deadlocks in Java 8 when keys share a bin, throws `IllegalStateException` or stalls later.
- **`Thread.sleep` in async tests**: trades a race for a flaky test.
- **Unbounded virtual-thread executor + list of Futures + manual `get(timeout)` for fan-out**: leaks remaining tasks on early return, holds connections open, blows the SLA when a slow vendor times out at 30s.
- **Virtual threads mutating a shared `HashMap`/`ThreadLocal`**: still a race, now looking deceptively sequential.

## Code Examples
```java
import se.deversity.asynctest.AsyncTest;
import org.junit.jupiter.api.AfterEach;
import static org.junit.jupiter.api.Assertions.assertEquals;

class CounterTest {
    private int counter = 0;

    @AsyncTest(threads = 50, invocations = 100)
    void incrementsAreLost() {
        counter++;                       // 50 threads collide here, 100 times
    }

    @AfterEach
    void verify() {
        assertEquals(5000, counter);     // fails: counter < 5000, reproducibly
    }
}
```
- **What it demonstrates**: a once-in-a-million production race becomes a deterministic red test in CI.

```java
@AsyncTest(threads = 2, detectDeadlocks = true, timeoutMs = 2000)
void transferDoesNotDeadlock() {
    bank.transfer(accountA, accountB, 100);
    bank.transfer(accountB, accountA, 100);   // opposite lock order
}
```
- **What it demonstrates**: an opaque hang becomes a report naming the circular lock dependency and threads.

```java
public class QuorumTaskScope<T> extends StructuredTaskScope<T> {
    private final int requiredSuccesses;
    private final ConcurrentLinkedQueue<T> results = new ConcurrentLinkedQueue<>();

    public QuorumTaskScope(int quorum) {
        super("quorum-scope", Thread.ofVirtual().factory());
        this.requiredSuccesses = quorum;
    }

    @Override
    protected void handleComplete(Subtask<? extends T> subtask) {
        if (subtask.state() == Subtask.State.SUCCESS) {
            results.add(subtask.get());
            if (results.size() >= requiredSuccesses) {
                this.shutdown();   // cancels remaining virtual threads
            }
        }
    }
    public Collection<T> results() { return results; }
}
```
- **What it demonstrates**: first-3-of-5 vendor quotes within a 200 ms SLA with no leaked tasks or orphaned sockets.

```java
// AI version: C2 may hoist to `if (!stop) while (true) doWork();`
boolean stop = false;
void spin() { while (!stop) { doWork(); } }
// Fix:
volatile boolean stop;
```
- **What it demonstrates**: a one-keyword visibility fix for a compiler-legal infinite loop.

## Reference Tables
| Detector | AI mistake it catches |
|---|---|
| Deadlock (lock-chain analysis) | Two locks acquired in inconsistent order across methods |
| Visibility monitoring | Missing `volatile`/synchronization — "works on my machine" |
| ABA / broken DCL | Lazy initializer "optimized" without volatile |
| Race-condition tracking | Cross-thread access to unsynchronized fields |
| Atomicity violations | Check-then-act / TOCTOU (`counter++`) |
| Recursive `computeIfAbsent` | Memoized graph walker / DP cache recursing into the same map |

| Why random scheduling fails | Forced-collision answer |
|---|---|
| Thread starvation illusion (threads rarely switch at the race) | `CyclicBarrier` releases all workers in lockstep |
| Heisenbug (only under CPU load / GC pause) | Repeated barrage of invocations |

Setup: test-scoped Maven dependency `se.deversity.async-test-lib:async-test-lib` or Gradle `testImplementation("se.deversity.async-test-lib:async-test-lib:1.7.0-RC3")`. Licensing: PolyForm Noncommercial — free for personal/hobby, commercial use needs a license (a procurement check, easy to miss).

## Worked Example
Recursive `computeIfAbsent`, before and after:
```java
// AI-generated: silent deadlock in Java 8, undefined in later JDKs
graph.computeIfAbsent("A", k -> {
    Node child = graph.computeIfAbsent("B", k2 -> new Node(k2)); // same map, same bin possible
    return new Node(k, child);
});
// Fix: lift the recursion out of the mapping function
Node child = graph.computeIfAbsent("B", k2 -> new Node(k2));
graph.computeIfAbsent("A", k -> new Node(k, child));
```
The inner call modifies the map under a bin-level lock the caller already holds. The deadlock detector converts the production hang into a named lock-chain diagnosis in CI before merge; that diagnosis is pasted back to the AI, which lifts the recursion and keeps the test.

## Why It Works / Failure Mode
- **Forced collision works** because it replaces probability with construction: parking every thread one instruction before the target and releasing them together makes the bad interleaving the common case, and detectors name the class of bug, giving the AI a precise fix target. It fails on the state you did not think to stress — an async-test forces interleavings only where pointed.
- **The general ceiling**: every guardrail shortens the distance between defect introduction and automated signal; none makes it zero. The defect that slips through is, by definition, the one no guardrail was aimed at. Therac-25 (1985–87; ≥3 deaths from a race between operator-interface and treatment-setup tasks, studied by Leveson & Turner, 1993) needed years of engineering to ship a fatal race; an AI can produce one in a single prompt, with a test that won't catch it.

## Key Takeaways
1. Never accept an agent's own concurrency test as evidence its concurrency code is correct.
2. For any shared mutable state, demand an `@AsyncTest` (≥20 threads, ≥100 invocations) with the relevant detector — and expect red first.
3. Feed named detector diagnoses back to the AI; they are what lets it fix rather than guess.
4. Use `volatile`, `VarHandle` acquire/release or `java.util.concurrent` primitives; run async-tests on ARM, not just x86.
5. Virtual threads solve throughput, not concurrency; bound them with `StructuredTaskScope` and name the quorum idiom in your context file.
6. Declare concurrency invariants with `@AIThreadSafe` (or an equivalent comment + CLAUDE.md note) so future edits preserve them.

## Connects To
- **Ch 2**: the "beautifully deceptive" AI failure mode, at its worst here.
- **Ch 2b**: the Eight Fallacies of Distributed Computing.
- **Ch 3**: context file as the place to name required idioms (StructuredTaskScope).
- **Ch 4 / §4.8**: `@AIThreadSafe` and its hand-written equivalent.
- **Ch 17b**: the second invisible internal failure — scale instead of timing.
- **Therac-25 (Leveson & Turner, IEEE Computer 1993)**: canonical race-condition safety failure.
- **JSR 133 / JMM (Pugh, Lea et al.)**: the formal model the AI cannot see.
