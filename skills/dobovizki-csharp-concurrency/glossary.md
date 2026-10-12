# Glossary — C# Concurrency

**Acquire semantics** — an operation ("don't move reads earlier than this"); acquiring a lock has it, giving up-to-date memory values (Ch 7).

**AggregateException** — wraps one or more exceptions; always what `Task.Exception` holds. `await` throws only its first inner exception (Ch 3, Ch 12).

**async (keyword)** — a compiler flag enabling `await` support + wrapping the return in a Task; does NOT make code run in the background (Ch 3).

**async void** — async method with no Task; legal only for event handlers; must self-handle all exceptions (Ch 3, Ch 12).

**Atomic operation** — an operation that can't be interrupted (single hardware op). `++n` is not atomic (Ch 4).

**await (keyword)** — ends the current chunk and returns to the caller, resuming the continuation when the awaited task completes; does not block (Ch 3).

**await foreach** — `foreach` with an `await` at each iteration, over `IAsyncEnumerable<T>` (Ch 14).

**Awaiter** — the internal object `await` actually uses (conceptually `ContinueWith`) (Ch 3).

**BlockingCollection<T>** — producer/consumer wrapper adding waiting + bounded capacity over a concurrent collection; blocking, not async-friendly (Ch 8, Ch 13).

**Blocked state** — OS parks a thread doing a blocking op; gives it no CPU until complete (Ch 1).

**Blocking operation** — file/network/anything outside CPU+memory, or waiting on another thread (Ch 1).

**Bounded capacity** — `BlockingCollection`/`Channel` max size, throttling the producer (Ch 13).

**CancelAfter** — `CancellationTokenSource` method implementing a timeout (Ch 9).

**CancellationToken** — the standard cooperative cancellation flag; only checks (Ch 9).

**CancellationTokenSource** — creates/controls tokens; `Cancel()`, `CancelAfter`, `CreateLinkedTokenSource` (Ch 9).

**Channel<T>** — async multi-producer/consumer queue; the async substitute for `BlockingCollection` (Ch 13, Ch 14).

**ConcurrentDictionary<K,V>** — thread-safe dictionary; `TryAdd`, `GetOrAdd`, `TryUpdate` fuse check-and-act (Ch 13).

**ConfigureAwait(false)** — makes `await` ignore the current `SynchronizationContext`/`TaskScheduler` → thread pool; libraries only (Ch 11).

**Context switch** — CPU saving one thread's state and loading another's; overhead (Ch 1).

**Continuation** — code after `await` (or the `ContinueWith` callback) (Ch 5, Ch 10).

**ContinueWith** — Task's callback mechanism; runs on the thread pool; rarely used directly (Ch 3).

**Coroutine** — code that can suspend/resume/return multiple values; C# iterator (`yield`) and async methods (Ch 2).

**Dead letter queue** — where poison/unprocessed messages are parked for inspection (Ch 8).

**Deadlock** — threads stuck forever waiting on each other (Ch 4, Ch 7, Ch 11).

**EnumeratorCancellation (attribute)** — marks the generator parameter that receives the iteration's cancellation token (Ch 14).

**Exactly-once delivery** — process each item once; generally impossible (Ch 8).

**Frozen collection** — read-optimized, build-once, unmodifiable (`FrozenDictionary`, `FrozenSet`) (Ch 13).

**GetConsumingEnumerable** — `BlockingCollection` method; `foreach` blocks when empty, exits on `CompleteAdding` (Ch 8, Ch 13).

**GetOrAdd** — `ConcurrentDictionary` atomic get-or-create; the one-line thread-safe cache (Ch 13).

**IAsyncEnumerable<T>** — async `IEnumerable<T>`; `GetAsyncEnumerator` → `MoveNextAsync` returns `ValueTask<bool>` (Ch 14).

**Immutable collection** — thread-safe by never changing; each "change" returns a new sharing-most-nodes copy (Ch 13).

**ImmutableArray<T>** — array-backed immutable collection; slow write, fast read; treat like frozen (Ch 13).

**ImmutableInterlocked** — lock-free swaps of a variable holding an immutable collection; all-or-nothing (Ch 13).

**Interlocked** — lock-free atomic ops (Increment/Add/Exchange/CompareExchange); protects the operation, not the variable (Ch 4).

**IsBackground** — background threads don't keep the app alive (Ch 4, Ch 9).

**Lock hierarchy** — always acquiring locks in the same order to prevent deadlock (Ch 7).

**lock statement** — .NET's fast internal mutex; auto-releases on block exit/exception; lock a private object (Ch 4, Ch 7).

**ManualResetEventSlim** — a gate; `Wait()` blocks while unset, `Set()` opens (Ch 4).

**Memory access reordering** — compiler/CPU reorder/eliminate memory ops preserving single-threaded results; breaks unlocked flags (Ch 7).

**Memory barrier** — blocks compiler/CPU from moving reads and writes across it (Ch 7).

**Memory model** — the rules for how memory access may be reordered (Ch 7).

**MoveNextAsync** — `IAsyncEnumerator` method returning `ValueTask<bool>` (Ch 14).

**Multicore CPU** — N cores → N truly-simultaneous threads; cuts processing time, not waiting time (Ch 1).

**Nonblocking operation** — queues work with the OS/device and returns immediately, freeing the thread (Ch 1).

**OperationCanceledException** — thrown by `ThrowIfCancellationRequested()` (Ch 9).

**Parallel class** — `Invoke`/`For`/`ForEach`/`ForEachAsync`; set `MaxDegreeOfParallelism` (Ch 8).

**Partial update** — another thread sees a half-written value; happens even on single `decimal`/`long`(32-bit)/struct assignments (Ch 7).

**Poison message** — an item that always crashes processing → infinite retry under at-least-once (Ch 8).

**Polling ("Are we there yet?")** — looping on `IsCompleted` with real work between checks (Ch 3).

**Race condition** — result depends on uncontrollable timing (Ch 7).

**Recursive lock** — same thread may re-acquire (`lock`/`Mutex`); `Semaphore`/exclusive files can't (Ch 7).

**Release semantics** — "don't move writes later than this"; releasing a lock has it, flushing changes (Ch 7).

**RunContinuationsAsynchronously** — `TaskCompletionSource` option running continuations off the completing thread; makes completing under a lock safe (Ch 10).

**Starvation** — one thread/group monopolizes a resource, starving others (Ch 7).

**SynchronizationContext** — .NET's "run code on that thread" abstraction (`Post`/`Send`); UI/ASP.NET Classic install one (Ch 11).

**Synchronization** — parallel work forced sequential (sometimes desired, e.g. banking) (Ch 7).

**Task** — represents a future event/completion; not a thread or background op (Ch 3).

**Task<T>** — represents a future value (Ch 3).

**TaskCompletionSource** — creates and manually completes a Task (`TrySetResult`/`Exception`/`Canceled`) (Ch 10).

**Task.Run** — runs code on the thread pool; returns a Task; async-friendly (Ch 4).

**TaskScheduler** — async infra deciding which thread runs continuations; `.Default` = thread pool (Ch 11).

**Task.WhenAll** — awaits many tasks asynchronously (vs blocking `WaitAll`) (Ch 4).

**Task.Yield** — async `DoEvents`; queues continuation at end of input queue to stay responsive (Ch 11).

**Thread** — one parallel sequence of operations; has memory + management overhead (Ch 1, Ch 4).

**Thread affinity** — pinning a thread to a core; almost always a mistake (Ch 1).

**Thread pool** — system-managed reused threads, tuned for short tasks (Ch 4).

**ThrowIfCancellationRequested** — throws `OperationCanceledException` if canceled (Ch 9).

**TryUpdate** — `ConcurrentDictionary` compare-and-swap (new, expected) for lock-free optimistic updates (Ch 13).

**ValueTask / ValueTask<T>** — struct holding a value directly when synchronous, else a Task; avoids allocation on the fast path (Ch 3).

**volatile** — does NOT guarantee latest value; don't use it (Ch 7).

**WithCancellation** — extension routing a token into `await foreach`'s hidden `GetAsyncEnumerator` (Ch 14).

**Work queue pattern** — few long-lived threads draining a shared queue to bound load (Ch 8).

**Work stealing** — `ConcurrentBag` taking from another thread's queue when its own is empty (Ch 13).

**yield return** — lazily produces a sequence via a compiler-generated iterator state machine (Ch 2, Ch 14).
