# Chapter 8: Processing a Sequence of Items in the Background

## Core Idea
For a batch of items, choose between processing them **in parallel** (finish fast, but bound the concurrency) or **sequentially in the background** (free the caller now, don't care how long it takes) — and pick the primitive (`Thread`, thread pool, `Parallel`, work queue, persistent queue) to match load and durability needs.

## Frameworks Introduced
- **Parallel vs sequential-background**: parallel = wait for all, wall-clock = slowest item, but risks unbounded threads / thread-pool saturation. Sequential-background = move the whole loop off the caller's thread, return immediately, gentle on downstream services.
- **The Parallel class**: `Parallel.Invoke` / `For` / `ForEach` (sync, block till done) / `ForEachAsync` (async body, returns a Task). Cleaner than hand-rolled loops.
  - When to use: `ForEach` for short collections of CPU/blocking work; be wary on large ones.
  - How: `Parallel.ForEach(items, (item, _) => {...}).Wait();` — the `_` is a cancellation token (Ch 9).
  - **Pitfall**: `MaxDegreeOfParallelism` defaults are unreliable — `ForEach` *does* cap parallelism despite docs saying otherwise (limiting thread-pool self-tuning); `ForEachAsync` treats the default (core count) as *items processed at once*, so 1,000 async 1-second waits on 12 cores take ~84s. Set `MaxDegreeOfParallelism` explicitly.
- **Work queue pattern (`BlockingCollection<T>`)**: one (or few) long-lived thread(s) drain a shared queue. Bounds load — no per-item thread explosion.
  - When to use: servers/multi-user where you must cap sustained load.
  - How: `Add` enqueues; `CompleteAdding` signals done; `foreach (var x in queue.GetConsumingEnumerable())` blocks when empty, exits after `CompleteAdding`. Use `Thread` (not pool) for the long-lived consumer.
- **Persistent (durable) queues**: queue on disk/DB/broker (RabbitMQ, SQS, Azure Storage Queues) so items survive crashes.
  - When to use: losing pending items is unacceptable.
  - How: reading and removing are separate ops → choose **at-least-once** (remove after processing; risk duplicates) or **at-most-once** (remove before; risk loss). *Exactly-once is generally impossible.*

## Key Concepts
- **Thread-pool saturation**: dumping many long/blocking work items ties up the pool; other users (ASP.NET) stall. `ThreadPool.SetMinThreads(n, …)` pre-warms it.
- **Thread-pool self-tuning**: the pool grows threads gradually — early bursts are slow, later runs faster.
- **`MaxDegreeOfParallelism`**: the cap on concurrent items in `Parallel*`.
- **Poison message**: an item that always crashes processing → infinite retry loop under at-least-once. Catch failures, and after repeated fails move it to a **dead letter queue**.
- **`IsBackground`**: set on a background thread so the app can exit without waiting for it.

## Mental Models
- Think "blocking parallel work saturates the pool; async parallel work barely touches it" — the 1,000-item test: blocking ~20–70s, async ~1.0s.
- Think of a work queue as a rate-limiter: fixed consumers = bounded downstream pressure.
- "Losing data is usually worse than doing it twice" → default to at-least-once + poison handling.

## Worked Example
Same mail-merge, four ways — watch the one-line deltas and their cost (1,000 × 1s items):

```csharp
// Thread-per-item: works, ~1.2s for 1,000; but unbounded threads (10 users × 100 = 1,000)
new Thread(() => Send(msg)).Start();   // + Join loop

// Thread pool via Task.Run: bounded threads, but blocking saturates pool → 20–70s, self-tunes
Task.Run(() => Send(msg));             // + Task.WaitAll

// Async in the pool: holds no thread while waiting → ~1.0s, near-zero overhead
Task.Run(async () => await sender.SendMailAsync(msg));

// Parallel class: closest to the original foreach
Parallel.ForEach(recipients, (r, _) => Send(r)).Wait();
Parallel.ForEachAsync(recipients,
    new ParallelOptions { MaxDegreeOfParallelism = recipients.Length },   // don't trust the default
    async (r, _) => await sender.SendMailAsync(BuildMessage(r))).Wait();
```

Work queue (bounded, long-lived consumer):

```csharp
BlockingCollection<MailInfo> _queue = new();
public void Start() => new Thread(BackgroundProc).Start();
public void Stop()  => _queue.CompleteAdding();
public void Enqueue(MailInfo m) => _queue.Add(m);
private void BackgroundProc() {
    var sender = new SmtpClient("smtp.example.com");
    foreach (var m in _queue.GetConsumingEnumerable())   // blocks when empty, exits on CompleteAdding
        try { sender.Send(Build(m)); } catch { LogFailure(m.email); }
}
```
**What it demonstrates**: identical logic, but async-in-pool erases thread-pool overhead, and the work queue caps concurrency to protect a shared server. Prepare each queue item fully so one failure affects one message.

## Anti-patterns
- **Unbounded thread/task creation per item on a server**: N users × M items = thread explosion.
- **Blocking work items flooding the thread pool**: stalls ASP.NET and everything else sharing it.
- **Trusting `Parallel.ForEach`/`ForEachAsync` default parallelism**: measure and set `MaxDegreeOfParallelism`.
- **Relying on behavior that contradicts the docs**: a future fix breaks you; code to satisfy both, or accept the risk.
- **Using the thread pool for a permanently-running consumer**: wastes a pool thread you'll never return.
- **At-least-once without poison-message handling**: one bad item → infinite crash loop.
- **Sending email in a loop without provider clearance**: gets you blocked; use a transactional email service.

## Key Takeaways
1. Parallel = finish fast (bound it); sequential-background = free the caller (durability optional).
2. Async work items barely touch the thread pool; blocking ones saturate it.
3. Pre-warm the pool with `SetMinThreads` when you know you need many threads.
4. Always set `MaxDegreeOfParallelism` on `Parallel*` for large collections.
5. Use `BlockingCollection<T>` + a dedicated `Thread` for the work-queue pattern.
6. Persistent queues survive crashes; choose at-least-once (default) and handle poison messages via a dead-letter queue.

## Connects To
- **Ch 9**: cancelling this background work with `CancellationToken`.
- **Ch 10**: building an *async* work queue (`BlockingCollection` has no non-blocking async form).
- **Ch 4/5**: `Thread` vs pool vs `Task.Run`, async I/O.
- **Ch 13**: `BlockingCollection` and other concurrent collections in depth.
