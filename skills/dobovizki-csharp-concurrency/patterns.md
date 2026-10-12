# Patterns & Techniques — C# Concurrency

## Async I/O over threaded blocking I/O
**When**: I/O-bound parallel work (files, network).
**How**: replace blocking calls with `...Async` + `await`; make the caller `async` and use `await Task.WhenAll(tasks)`.
**Trade-offs**: holds no thread while waiting (server benchmark: 27 threads vs 106); adds compiler state-machine overhead vs single-threaded.

## Offload the UI thread (`await Task.Run`)
**When**: long CPU work freezing a WinForms/WPF UI.
**How**: `await Task.Run(() => { result = LongCalculation(); }); label.Text = result;` — `await` on the UI thread resumes on the UI thread.
**Trade-offs**: the *only* place `await Task.Run` is right; elsewhere it just serializes.

## Lock around an await (rearrange, don't nest)
**When**: shared state guarded by `lock` in an async method.
**How**: `lock` only the state access before and after the `await`; never `await` inside `lock`.
**Trade-offs**: releases the lock across the await → two callers may both do the expensive work (acceptable if idempotent).

## The lock rules (deadlock-safe multithreading)
**When**: any shared mutable state.
**How**: (1) lock all access incl. reads; (2) same lock order everywhere (lock hierarchy); (3) never call foreign code while holding a lock; (4) hold for the whole operation; (5) but as briefly as possible; (6) no priority/affinity changes.
**Trade-offs**: rules 4 & 5 conflict — favor longer locks (race conditions beat synchronization).

## Cooperative cancellation (CancellationToken)
**When**: stopping background work.
**How**: pass `cts.Token`; in the worker call `token.ThrowIfCancellationRequested()` (or poll `IsCancellationRequested`), checking inside long inner loops.
**Trade-offs**: cooperative — long uninterrupted work delays cancellation; no forced stop.

## Timeout + linked cancellation
**When**: cancel on timeout and/or user, given only a token.
**How**: `using var cts = CancellationTokenSource.CreateLinkedTokenSource(userToken); cts.CancelAfter(TimeSpan.FromSeconds(30)); ...pass cts.Token`.
**Trade-offs**: dispose the linked source.

## Work queue (bounded background processing)
**When**: server must cap sustained load from many items.
**How**: `BlockingCollection<T>` (or `Channel<T>` for async) + a dedicated long-lived `Thread`/`Task`; producers `Add`, consumer `foreach (GetConsumingEnumerable())`, `CompleteAdding` to stop.
**Trade-offs**: in-memory → lost on crash; use a persistent queue (DB/RabbitMQ/SQS) with at-least-once + dead-letter for durability.

## Race-free cache (GetOrAdd)
**When**: memoize expensive per-key initialization across threads.
**How**: `dictionary.GetOrAdd(key, factory)` on `ConcurrentDictionary`.
**Trade-offs**: factory may run in several threads, but all get the same returned object.

## Lock-free optimistic update (TryUpdate loop)
**When**: read-modify-write a concurrent/immutable value without locks.
**How**: `while (true) { var prev = d[key]; if (d.TryUpdate(key, prev+1, prev)) break; }` (or `ImmutableInterlocked.TryUpdate(ref var, ...)`).
**Trade-offs**: retries under contention; single-collection only.

## Manual Task control (TaskCompletionSource)
**When**: make an event/legacy API/data structure awaitable, or background init.
**How**: create `tcs`, return `tcs.Task`, call `TrySetResult/Exception/Canceled` when done; use `RunContinuationsAsynchronously` if completing under a lock.
**Trade-offs**: prefer `Try*` (no race); `Task.Factory.FromAsync` for `BeginXxx`/`EndXxx`.

## Custom SynchronizationContext (single-thread affinity)
**When**: force `await` continuations onto one specific thread (like a UI thread).
**How**: derive `SynchronizationContext`, implement `Post` to enqueue work to a `BlockingCollection` loop; `SetSynchronizationContext` on the thread.
**Trade-offs**: only `Post` is needed for `await`.

## Fix the async/blocking deadlock
**When**: UI/ASP.NET-Classic thread blocks on `.Result`/`.Wait()` while a continuation needs that thread.
**How** (best→worst): use `await` instead of `.Result`; `ConfigureAwait(false)` inside the library method; `Application.DoEvents` loop (100% CPU).
**Trade-offs**: blanket `ConfigureAwait(false)` breaks UI updates — libraries only.

## Async iterator (IAsyncEnumerable + await foreach)
**When**: produce/consume asynchronously-generated sequences (streams, channels).
**How**: `async IAsyncEnumerable<T>` with `await` + `yield return` (yield *outside* any `try`); consume with `await foreach`; cancel via `.WithCancellation(token)` + `[EnumeratorCancellation]`.
**Trade-offs**: no built-in LINQ (use `System.Linq.Async`); `ToBlockingEnumerable` bridges to sync but can deadlock.

## Bound Parallel-class concurrency
**When**: `Parallel.ForEach`/`ForEachAsync` over large collections.
**How**: always set `new ParallelOptions { MaxDegreeOfParallelism = N }`.
**Trade-offs**: defaults contradict docs; `ForEachAsync` default = core count treated as items-at-once (slow for I/O).
