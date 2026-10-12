# Chapter 9: Common Design Patterns

## Core Idea
A catalog of the patterns that recur in .NET API design: aggregate components (façades), the Task-Based Async Pattern, the Dispose pattern, factories, LINQ support, the Optional Feature pattern, covariance/contravariance, Template Method, timeouts, XAML, and buffer/`Span<T>` operations.

## Frameworks Introduced
- **Aggregate component + Create-Set-Call**: a façade (`HttpClient`, `MessageQueue`, `EventLog`) over lower-level *factored types*. Users: `new`, set properties, call methods — one `new` per simple scenario. "It-Just-Works"; complexity is hidden completely or not at all.
- **Task-Based Async Pattern (TAP)**: the only recommended async pattern (Classic/APM and Event-Based/EAP are legacy). `Async` suffix, returns `Task`/`Task<T>`/`ValueTask<T>`, optional `CancellationToken cancellationToken = default` (last param).
- **Basic Dispose Pattern**: `IDisposable.Dispose()` → `Dispose(true)` + `GC.SuppressFinalize(this)`; all cleanup in `protected virtual void Dispose(bool disposing)`.
- **Template Method**: public non-virtual member validates + calls a `protected virtual XxxCore` — centralizes extensibility to one overridable method.
- **Optional Feature Pattern**: a `bool CanXxx` property + virtual `Xxx()` that throws `NotSupportedException` by default (`Stream.CanSeek`/`Seek`) — avoids interface explosion + dynamic casts.
- **Simulated Covariance Pattern**: an `IFoo<out T>` root interface (contravariant members removed) implemented explicitly, so all `Foo<T>` share a common root.

## Reference Tables

Async return type decision:

| Method | Return |
|---|---|
| No result | `Task` |
| Commonly completes synchronously | `ValueTask<T>` |
| Otherwise | `Task<T>` |

Async pattern status:

| Pattern | Status |
|---|---|
| Task-Based (TAP) | **Use for all new async** |
| Classic (Begin/End, APM) | Legacy |
| Event-Based (EAP) | Legacy |

Factory vs. constructor:

| Prefer | When |
|---|---|
| **Constructor** (default) | Discoverable, IntelliSense-guided, consistent |
| Factory method | Need to return a derived/cached type, a self-explanatory name (`String.Repeat`), or conversions (`Parse`, `Decode`) |
| Factory type (abstract factory) | Runtime selection of the concrete type |

## Key Concepts
- **Factored types**: the richer types behind an aggregate component; no modes, clear lifetime, often `IDisposable`, exposed via a property (`SerialPort.BaseStream`).
- **`CancellationToken`**: applies to async AND long-running/blocking *synchronous* methods (`BlockingCollection<T>.Add`). Throw `OperationCanceledException` (or `token.ThrowIfCancellationRequested()`) — an early `return` wrongly marks the Task `RanToCompletion`.
- **`ConfigureAwait(false)`**: use when awaiting, except in UI app models that need the synchronization context — avoids tying up the UI thread and deadlocks. It wraps the Task; no effect unless awaited.
- **Covariance (`out`) / Contravariance (`in`)**: `out` for output-only type params, `in` for input-only; "declare variance whenever the compiler lets you" (both are breaking to remove). `List<string>` → `List<object>` is illegal because `T` is both in and out.
- **`Span<T>`/`ReadOnlySpan<T>`**: `ref struct` over contiguous memory (array/`stackalloc`/pointer/string); O(1) slicing, no copy. Callers slice themselves → no offset/count overloads needed. `Memory<T>`/`ReadOnlyMemory<T>` for storage and async (spans can't be fields or cross an await).
- **Dependency property**: value stored in a property store; regular CLR property + `public static readonly DependencyProperty XxxProperty`; validation/change-notification/coercion go in metadata callbacks, never in the accessor.

## Mental Models
- **`ValueTask` is easy to misuse**: only ever `await` or `return` it once — never store, re-await, or read `.Result` twice. "Never have a `ValueTask` local" (call `.AsTask()` first if you need to).
- **Throw usage-error exceptions synchronously from an async method** — put them in a public method that validates then defers to a private `async ...Core`, so the exception isn't buried in the Task and the call stack is clear.
- **Never return `null`/`Created`-state Task**; use `Task.CompletedTask`/`Task.FromResult`.
- **Never `Task.Wait()`/`.Result` inside async** — blocking wait → deadlock; `await` instead; call async variants from async code.
- **Dispose must be idempotent, must not throw when `disposing == false`** (finalizer context → process termination); throw `ObjectDisposedException` from members used after dispose; don't rehydrate public types.
- **Don't make public types finalizable** — wrap unmanaged resources in a `SafeHandle`; a finalizer taxes every allocation even if never called.
- **Scoped operations return a disposable** (`writer.OpenScope()`, `lock.GetReadLock()`) so `using` pairs begin/end in a finally block — critical for locks.
- **Don't return a `Span` over your own field** — it over-exposes internals and breaks when you grow the buffer; accept a destination `Span<T>` and copy instead.

## Code Examples
Basic Dispose Pattern:
```csharp
public void Dispose() { Dispose(true); GC.SuppressFinalize(this); }
protected virtual void Dispose(bool disposing) {
    if (disposing) { _resource?.Dispose(); }   // managed resources only when disposing
}
```
Template Method — validate in public, override in Core:
```csharp
public void SetBounds(int l, int r) {
    if (l < MinLeft || l >= r) throw new ArgumentOutOfRangeException(nameof(l));
    if (_disposed) throw new ObjectDisposedException(...);
    SetBoundsCore(l, r);
}
protected virtual void SetBoundsCore(int l, int r) { /* derived-specific work */ }
```
Optional Feature Pattern:
```csharp
public virtual bool CanSeek => false;
public virtual void Seek(int position) => throw new NotSupportedException();
```
`ReadOnlySpan<byte>` for fixed data (compiler emits no allocation):
```csharp
public static ReadOnlySpan<byte> LocalFile => new byte[] { 0x50, 0x4b, 0x03, 0x04 };
```

## Anti-patterns
- **Returning `Task` for a long-running *synchronous* method** (no async yield) or wrapping a sync method in `Task.Run` just to look async.
- **`ref`/`out`/`in` on async methods** — `out` param → the method becomes a blocking sync-over-async fake (deadlock risk). Convert to a return type or `Task<TResult struct>`.
- **Aggregate component requiring inheritance / interface implementation / config files** — rely on properties + composition; use events, not virtuals/delegates.
- **Factored types with modes**; **Create-Call-Get** (login then read properties) — return a result object instead.
- **Validation/change/coercion in a dependency-property accessor** — bypassed by XAML/styling; put logic in metadata callbacks.
- **Covariant interface returning `T[]`** — writes can throw `ArrayTypeMismatchException`; use a collection interface.
- **Public virtual members** — use Template Method (`Core` suffix) instead.
- **Integer timeouts** with ambiguous units — prefer `TimeSpan`; throw `TimeoutException`, never return an error code.

## Key Takeaways
1. Provide aggregate components for common feature areas (Create-Set-Call, one `new`, events over delegates); expose factored types for advanced use.
2. Use TAP for all new async: `Async` suffix, `Task`/`ValueTask<T>`, trailing default `CancellationToken`, `ConfigureAwait(false)` off the UI, throw `OperationCanceledException` on cancel.
3. Implement the Basic Dispose Pattern (idempotent, `ObjectDisposedException`, no-throw in finalizer path); keep public types non-finalizable via `SafeHandle`; `IAsyncDisposable` = both async + dispose guidance.
4. Prefer constructors; use factories for derived/cached returns, self-explanatory names, and conversions (`Create<Type>` / `<Type>Factory` naming).
5. Support LINQ via `IEnumerable<T>` (basic), `IQueryable<T>` (remote/expression-inspecting, measure perf), or the Query Pattern; defer execution; put query extensions in a `.Linq` subnamespace.
6. Use the Optional Feature Pattern (`CanXxx` + throwing virtual) over interface explosion; declare `in`/`out` variance whenever the compiler allows.
7. Use Template Method (`Core` suffix) for controlled extensibility; validate common args in the public member, derived-specific args in Core.
8. Timeouts: `TimeSpan` params, `TimeoutException`; XAML: default constructor (or markup extension for immutables), `[ContentProperty]`; buffers: `Span<T>`/`ReadOnlySpan<T>` (prefer read-only), `Memory<T>` for storage/async, don't return spans over fields.

## Connects To
- **Ch 2**: layered architecture (high-level aggregate vs. low-level factored); low barrier to entry.
- **Ch 5**: constructors vs. factory methods (§5.3), `Func`/`Action` callbacks, the Try pattern (`out` in factories).
- **Ch 6**: Template Method is the tool for scoped virtual extensibility; abstractions and base classes.
- **Ch 7**: `OperationCanceledException`/`TimeoutException`; async exception handling; `using`/finally.
- **Ch 8**: collection abstractions returned by LINQ; `IDisposable`; `Span`/`Memory` vs. arrays.
- **App. B**: legacy Classic/Event-Based async and older Dispose guidance.
