# Chapter 10: Await Your Own Events

## Core Idea
`TaskCompletionSource` lets you create and *manually control* a `Task` — completing it with a result, exception, or cancellation whenever you choose. It's how you make your own events, initialization, legacy APIs, and data structures awaitable.

## Frameworks Introduced
- **`TaskCompletionSource` / `TaskCompletionSource<T>`**: owns one `Task`/`Task<T>` (via its `.Task` property, initially `WaitingForActivation`) and completes it on demand.
  - When to use: adapting non-Task async APIs, awaiting app events, building async data structures, background initialization.
  - How — three completion methods, each in `Set`/`Try` form:
    - `TrySetResult(v)` → `RanToCompletion` (sets `Result` for `Task<T>`).
    - `TrySetException(ex)` → `Faulted`; `await` throws (wrapped `AggregateException`).
    - `TrySetCanceled()` → `Canceled`; `await` throws `TaskCanceledException` (note `IsFaulted` stays false, `Exception` null).
- **`Set` vs `Try`**: `SetXxx` throws if the task is already complete; `TrySetXxx` returns false instead. **Prefer `Try`** — `Set` causes a race when two threads (e.g. worker + cancellation) may both complete it.
- **`RunContinuationsAsynchronously`**: by default the continuation (code after `await`) can run *synchronously inside* your `TrySetResult` call — so calling it while holding a lock risks deadlock (foreign continuation code takes another lock).
  - When to use: whenever you complete a task while holding a lock, or want predictable `TrySet…` timing.
  - How: `new TaskCompletionSource<T>(TaskCreationOptions.RunContinuationsAsynchronously)` — decided at construction, not per-call. Alternative: copy the locked value to a local and call `TrySetResult` *outside* the lock.
- **`Task.Factory.FromAsync`**: wraps a legacy `BeginXxx`/`EndXxx` (`IAsyncResult`) pair into a `Task`.

## Key Concepts
- **Continuation**: the code after `await` (or the `ContinueWith` callback).
- **Background initialization pattern**: constructor kicks off `Task.Run`, stores the `tcs.Task` in a field; every method `await`s that field — combines "is it ready?", "get the value", and "did init fail?" into one await.
- **Adapting event-style APIs**: subscribe to the completion event, call `tcs.TrySetResult` in the handler, return `tcs.Task`.
- **`Task.FromResult(v)`**: an already-completed task — deliver a value with no waiting.

## Mental Models
- Think of `TaskCompletionSource` as the "write end" of a Task and `await` as the "read end" — you control exactly when the reader wakes.
- A `TaskCompletionSource` is the general form of the `setResult`/`setException` callbacks from Ch 3's manual async transform.
- `RunContinuationsAsynchronously` = "don't run the reader's code on my thread" — the safety valve for completing under a lock.

## Worked Example
Background initialization — await a value that may still be computing:

```csharp
public class RequiresInit {
    private Task<int> _value;
    public RequiresInit() {
        var tcs = new TaskCompletionSource<int>();
        _value = tcs.Task;                        // assign BEFORE leaving constructor
        Task.Run(() => {
            try { Thread.Sleep(1000); tcs.TrySetResult(7); }   // long init
            catch (Exception ex) { tcs.TrySetException(ex); }  // propagate failure
        });
    }
    public async Task<int> Add1() => await _value + 1;   // waits only if not ready; throws if init failed
}
```

Async data structure — a queue whose `Dequeue` awaits until an item exists (note the lock-safe flag):

```csharp
public Task<T> Dequeue(CancellationToken ct) {
    lock (_lock) {
        if (_dataWaitingForProcessors.Count > 0)
            return Task.FromResult(_dataWaitingForProcessors.Dequeue());   // immediate
        var tcs = new TaskCompletionSource<T>(TaskCreationOptions.RunContinuationsAsynchronously);
        _processorsWaitingForData.Enqueue(tcs);
        if (ct.CanBeCanceled) ct.Register(() => tcs.TrySetCanceled(ct));
        return tcs.Task;                                                   // completes when Enqueue matches it
    }
}
```
**What it demonstrates**: `TaskCompletionSource` turns "notify me later" into an awaitable; `RunContinuationsAsynchronously` makes it safe to `TrySetResult` while holding `_lock`; `TrySetResult`'s bool return distinguishes delivered vs. already-canceled processors.

## Anti-patterns
- **`SetResult`/`SetException`/`SetCanceled` where two threads may complete the task**: throws on the loser → race. Use `TrySet…`.
- **Completing a task inside a `lock` without `RunContinuationsAsynchronously`**: the continuation may run synchronously under your lock → deadlock. Flag it, or complete outside the lock.
- **Forgetting to assign `tcs.Task` before the constructor returns**: callers can't await it.
- **Hand-writing `TaskCompletionSource` plumbing for `BeginXxx`/`EndXxx`**: use `Task.Factory.FromAsync`.

## Key Takeaways
1. `TaskCompletionSource` creates a Task you complete manually (`TrySetResult`/`TrySetException`/`TrySetCanceled`).
2. Prefer the `Try` variants — `Set` throws (race) when already complete.
3. Canceled tasks throw `TaskCanceledException` on await but have `IsFaulted == false`, `Exception == null`.
4. Continuations may run *synchronously* inside `TrySet…`; use `RunContinuationsAsynchronously` (or complete outside the lock) to stay deadlock-safe.
5. Use it for awaitable events, background init, and async collections; `Task.FromResult` for the already-have-it fast path.
6. `Task.Factory.FromAsync` adapts legacy `BeginXxx`/`EndXxx`.

## Connects To
- **Ch 3**: the `setResult`/`setException` manual transform this generalizes; `AggregateException`.
- **Ch 8**: builds the *async* work queue promised there (vs blocking `BlockingCollection`).
- **Ch 9**: `CancellationToken.Register`, `CanBeCanceled`, `CancellationToken.None`.
- **Ch 5/11**: where continuations run; deadlock from running foreign code under a lock.
