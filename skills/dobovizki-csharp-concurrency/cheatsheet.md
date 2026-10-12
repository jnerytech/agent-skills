# Cheatsheet — C# Concurrency (Dobovizki)

## Which run-in-background primitive?
| Situation | Use |
|---|---|
| Long-running / need thread properties (locale, COM, background) | `Thread` + `Thread.Start`, wait with `Join` |
| Short task, legacy | `ThreadPool.QueueUserWorkItem` |
| Short task or async code | `Task.Run`, wait with `await Task.WhenAll` |
| I/O-bound parallel work | async I/O (`...Async` + `await`), NOT `Task.Run` blocking |

## Where does code after `await` run? (real rules, in order)
1. Task already complete → **same thread** (`ConfigureAwait(false)` has no effect).
2. Thread has a `SynchronizationContext` (UI, ASP.NET Classic) + no `ConfigureAwait(false)` → **that context** (UI→UI).
3. Task has a `TaskScheduler` + no `ConfigureAwait(false)` → **that scheduler**.
4. Else / `ConfigureAwait(false)` → **thread pool**.

## async/await decision list (earlier wins)
1. Many connections → use async. 2. async-only API → use async. 3. UI freezing → async the slow bit. 4. Thread-per-request + heavy I/O → consider. 5. Codebase already async → use. 6. Codebase not async → avoid. 7. One-thing-at-a-time → don't. 8. Else → weigh trade-offs.

## The lock rules (and the conflict)
- Lock **all** shared access (reads too) — memory reordering/caching.
- Same **lock order** everywhere (lock hierarchy).
- Never call **foreign code** (events/delegates/virtuals) while holding a lock.
- Hold for the **whole operation** — composing thread-safe ops ISN'T thread-safe.
- …but hold as **briefly** as possible (else synchronization/starvation).
- Conflict of last two → **prefer longer** (race conditions > synchronization in badness).
- Lock a **private `object`** (never `lock(this)`); `.NET 9+`: `System.Threading.Lock`.

## Never do
`Thread.Abort/Suspend/Resume` · set thread **priority** or **processor affinity** · `volatile` as a fix · `await` inside `lock` · `.Result`/`.Wait()` on an incomplete task on a context thread (deadlock) · throw from `async void` · plain `Dictionary` as a concurrent/async cache.

## ConfigureAwait(false)
- Application/UI code → **avoid**.
- Library code, context-agnostic → on **every** `await`.
- To leave a context on purpose → `Task.Run`, NOT `ConfigureAwait(false)` (no-op on completed tasks).
- Myth: it does not mean "same vs other thread"; no-op if task already complete.

## Collection picker
| Need | Type |
|---|---|
| Concurrent read+write map/queue/stack | `ConcurrentDictionary` / `ConcurrentQueue` / `ConcurrentStack` |
| Same threads add & take, order N/A | `ConcurrentBag<T>` |
| Producer/consumer, block when empty | `BlockingCollection<T>` (own threads) |
| Producer/consumer, **async** | `Channel<T>` |
| Functional / undo / pass to untrusted code | immutable collections |
| Read-only sequential, thread-safe | `ImmutableArray<T>` |
| (Almost) never changes, read-hot | `FrozenDictionary` / `FrozenSet` |
| Already hold a lock for own logic | plain generic collection (simpler/faster) |

## Concurrent-dictionary idioms
- Cache: `d.GetOrAdd(key, factory)` (factory may run >once; same object returned).
- Increment: `while(true){ var p=d[k]; if(d.TryUpdate(k,p+1,p)) break; }`.
- No `Add`/`Remove` → `TryAdd`/`TryRemove` (already-present is normal, not an error).

## Task / TaskCompletionSource
- `Task` = future event; `Task<T>` = future value; completed = RanToCompletion | Canceled | Faulted.
- Prefer `TrySet*` over `Set*` (Set throws on already-complete → race).
- Completing under a lock → construct with `TaskCreationOptions.RunContinuationsAsynchronously`.
- Return `ValueTask<T>` from often-synchronous hot methods.

## Cancellation
- `cts.Token` in; worker calls `token.ThrowIfCancellationRequested()` (cooperative — check inside long loops).
- Timeout: `cts.CancelAfter(TimeSpan.FromSeconds(30))`. Combine reasons: `CreateLinkedTokenSource(...)`.
- Legacy API: `token.Register(callback)` (runs on the canceling thread). No-cancel API: `CancellationToken.None`.

## Exceptions in async
- Pre-first-`await` throw → normal exception; post-`await` throw → stashed in the Task (`Faulted`).
- `await` throws only the **first** inner of `AggregateException`; multi-failure → read `Task.Exception`.
- **Forgotten `await` = lost exception** (code silently stops → suspect a missing `await`).
- `async void` → catch everything inside; never let one escape.

## Partial-update gotchas (need a lock)
`decimal` (128-bit) · `long` on 32-bit · any `struct` assignment · `++n` (read-modify-write).

## Async iterators
- `async IAsyncEnumerable<T>` + `await` + `yield return` (yield **outside** `try`); consume `await foreach`.
- Cancel: `.WithCancellation(token)` + `[EnumeratorCancellation]` on the generator param.
- `Channel<T>` → wrap in `GetAsyncConsumingEnumerable()` for clean loops. Async LINQ: `System.Linq.Async` NuGet.
