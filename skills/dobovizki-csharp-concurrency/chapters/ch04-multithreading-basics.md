# Chapter 4: Multithreading Basics

## Core Idea
Three ways to run on another thread (`Thread`, `ThreadPool`, `Task.Run`) fit different jobs; and the moment two threads touch shared mutable data, non-atomic operations corrupt it — which locks fix, at the cost of a new failure mode: deadlock.

## Frameworks Introduced
- **Three ways to run on another thread** — pick by workload:
  - **`Thread` + `Thread.Start`**: oldest, most flexible; the *only* fully-owned thread. Use for **long-running** code or when you must change thread properties (locale, background, COM apartment). Do NOT use for async or short tasks. Wait with `Join()`.
  - **`ThreadPool.QueueUserWorkItem`**: borrows a pre-created thread — no create/destroy cost. Use for **short tasks**. Old/clunky API, predates Task, no built-in wait, can't change thread props. Don't use for long tasks or async.
  - **`Task.Run`**: runs on the thread pool but returns a `Task` and plays well with async/await. Use for **short tasks and async code**. Don't use for non-async long-running work.
- **Atomic operation**: an operation that can't be interrupted (single hardware-level op). `++n` is NOT atomic — it's read-modify-write (3 steps); interleaving corrupts it.
  - When to use: deciding if shared access needs protection.
  - How: if it's not a single hardware op and the data is shared → protect it.
- **Four responses to shared data** (in order of preference): (1) **no shared data** — each thread owns its variables; (2) **immutable shared data** — never modified, safe to read in parallel (functional style; Ch 13 has immutable collections); (3) **`lock`/`Mutex`** — synchronize access; (4) `Interlocked` — only when profiled and needed.
- **`lock` statement**: `.NET`'s internal mutex, faster than `Mutex` (no syscall). Auto-releases on block exit *and* on exception.
  - When to use: the default, simplest, safest synchronization.
  - How: `lock(privateObj) { …mutate shared state… }`. Lock on a **private** object used only for locking (Object in ≤.NET 8, `System.Threading.Lock` in .NET 9+).

## Key Concepts
- **Main thread**: the initial thread running `Main`.
- **Thread pool**: system-managed set of reused threads, tuned for short tasks; grows between min/max.
- **`Task.WhenAll`**: awaits many tasks asynchronously — elegant replacement for a `Join` loop.
- **Deadlock**: threads stuck forever waiting on each other (A holds mutex1 waits mutex2; B holds mutex2 waits mutex1).
- **`ManualResetEventSlim`**: a gate — `Wait()` blocks while unset (closed); `Set()` opens, `Reset()` closes. For signaling between threads that keep running (when `Join` won't do).
- **`Interlocked`**: lock-free atomic Increment/Decrement/Add/And/Or/Exchange/CompareExchange — protects the *operation, not the variable*; a single call only.
- **UI thread**: only thread allowed to touch UI controls (WinForms/WPF/UWP); marshal work back via `Invoke`/`BeginInvoke`.
- **`IsBackground`**: background threads don't keep the app alive; app exits when all non-background threads exit. Set before `Start`.

## Mental Models
- Think "borrowing a thread pool thread = visiting someone's house — don't rearrange the furniture (thread properties)."
- Awaiting `Task.Run` defeats its purpose — it serializes you back to sequential while paying task overhead.
- Deadlock is the tax on locks; the private-lock-object rule keeps both sides of every lock under your control so you *can* prevent it.

## Anti-patterns
- **`Thread.Suspend`/`Resume`/`Abort`**: never use — Suspend can freeze a thread mid-lock (e.g. inside the memory manager) → instant deadlock.
- **Setting thread priority**: risks priority-inversion deadlocks/perf loss; don't in normal apps.
- **`await Task.Run(...)`**: usually wrong — makes it sequential (exception: offloading from the UI thread). Use `_ = Task.Run(...)` to silence the warning if fire-and-forget.
- **Start-then-immediately-Join in one loop**: serializes execution with threading overhead — start all, *then* join all.
- **Capturing the loop variable in a task lambda**: all tasks see the final value; copy to a loop-scoped `var icopy = i;`.
- **Reaching for `Mutex`/`Interlocked`/exotic primitives first**: prefer `lock`; escalate only after profiling proves a bottleneck.

## Worked Example
The race and its fix — two threads each increment 5,000,000 times:

```csharp
// BROKEN: prints ~6,000,000, not 10,000,000 — ++theValue is read-modify-write
int theValue = 0;
var threads = new Thread[2];
for (int i = 0; i < 2; ++i) {
    threads[i] = new Thread(() => { for (int j = 0; j < 5000000; ++j) ++theValue; });
    threads[i].Start();
}
foreach (var t in threads) t.Join();
Console.WriteLine(theValue);   // wrong, varies every run

// FIXED: lock on a private object serializes the mutation
int theValue = 0;
object theLock = new Object();
// ... inside thread body:
for (int j = 0; j < 5000000; ++j) { lock (theLock) { ++theValue; } }   // prints 10,000,000
```

Waiting for many `Task.Run` jobs cleanly:

```csharp
var tasks = new Task[10];
for (int i = 0; i < 10; ++i) tasks[i] = Task.Run(RunInPool);
await Task.WhenAll(tasks);      // async wait, no Join loop
```

**What it demonstrates**: non-atomic shared writes silently lose updates; `lock` restores correctness; `Task.WhenAll` waits asynchronously where `Thread.Join` would block.

## Key Takeaways
1. `Thread` = long/owned; `ThreadPool.QueueUserWorkItem` = short/legacy; `Task.Run` = short + async-friendly.
2. `++n` isn't atomic; any shared mutable data needs protection.
3. Prefer, in order: no sharing → immutability → `lock` → `Interlocked` (profiled only).
4. `lock` on a private object; it auto-releases on exit/exception.
5. Reading shared data unsynchronized is also unsafe (stale/partial values).
6. Never `Suspend`/`Resume`/`Abort` or tweak priority; never block the UI thread.
7. `Task.WhenAll` beats a `Join` loop; don't `await Task.Run` unless offloading the UI thread.

## Connects To
- **Ch 5**: where the `await` continuation runs — connects threads to async/await.
- **Ch 7**: deadlocks, synchronization pitfalls, "composing thread-safe ops isn't thread-safe."
- **Ch 13**: immutable + concurrent collections, `Interlocked` patterns.
- **Ch 11**: UI thread, synchronization contexts, `Invoke`/`BeginInvoke`.
