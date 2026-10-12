# Chapter 12: Object Lifetime

## Core Idea
.NET separates *object lifetime* (GC's job) from *resource lifetime* (your job): three mechanisms bridge them — non-deterministic **finalization**, deterministic **IDisposable/Disposable pattern**, and **weak references** — and the recurring lesson is to prefer explicit cleanup and `SafeHandle` over hand-written finalizers.

## Frameworks Introduced

- **Disposable pattern (IDisposable + finalizer safety net)**: combine explicit `Dispose()` with an optional finalizer that calls the same cleanup path.
  - When to use: a type owns unmanaged resources (or IDisposable fields) that must be released deterministically.
  - How: a single `protected virtual Cleanup(bool fromFinalizer)` (author renames the confusing `Dispose(bool disposing)` → `Release(bool fromFinalizer)`); guard with an `_isReleased` flag; always free unmanaged resources; only dispose managed IDisposable fields when NOT from the finalizer; `Dispose()` calls cleanup then `GC.SuppressFinalize(this)`; public methods throw `ObjectDisposedException` if released.
  - Why it works: `Dispose()` gives deterministic release; the finalizer is a last-resort net if a developer forgets. `SuppressFinalize` removes the finalization overhead once disposed (sets one header bit).

- **SafeHandle (critically finalizable handle wrapper)**: derive from `SafeHandle` (which derives from `CriticalFinalizerObject` and implements Disposable) instead of writing finalizers.
  - When to use: wrapping any unmanaged handle representable as `IntPtr` (files, pipes, crypto keys, registry, wait handles).
  - How: inherit from `SafeHandleZeroOrMinusOneIsInvalid` (or `SafeHandleMinusOneIsInvalid`); override only `IsInvalid` and `ReleaseHandle`; store the handle via `SetHandle`. The owning class then holds a SafeHandle field and no longer needs its own finalizer.
  - Why it works: CLR gives special P/Invoke treatment — increments/decrements a lock-free ref count around the call, keeping the handle alive (no `GC.KeepAlive` needed) and preventing the **handle-recycling attack**. Cleanup is deferred until ref count hits zero.

- **Weak references (weak handles)**: hold a reference the GC does NOT treat as a root.
  - When to use: observers/listeners (weak events) and time-based caches — reference an object without extending its lifetime.
  - How: `GCHandle.Alloc(obj, GCHandleType.Weak)` (short) or `GCHandleType.WeakTrackResurrection` (long); prefer `WeakReference<T>` with `TryGetTarget` (atomic, type-safe) over `WeakReference.IsAlive`/`Target`.

## Key Concepts
- **Non-deterministic finalization**: implicit cleanup via a finalizer (`~Type()`); runs "at some time" after the object becomes unreachable, on a dedicated thread.
- **Finalizer**: C# `~Type()` syntax compiled into an override of `System.Object.Finalize` — a contract with the GC marking the object *finalizable*.
- **finalization queue**: array of addresses of all live finalizable objects, kept generation-aware (groups for gen0/1/2, LOH, POH) via **fill pointers**.
- **fReachable queue**: objects found dead at end of Mark phase but still needing their finalizer to run — now reachable only because of finalization; split into Critical and Normal groups.
- **Critical finalizer**: finalizer in a `CriticalFinalizerObject`-derived type; CLR guarantees it runs (JITted in advance) even during rude AppDomain unload / thread abort; runs *after* all normal finalizers.
- **Resurrection**: a finalizer reassigns `this` to a live root, making a dead object reachable again; needs `GC.ReRegisterForFinalize(this)` to be re-finalized (else finalizer runs only once).
- **Suppressing finalization**: `GC.SuppressFinalize` sets `BIT_SBLK_FINALIZER_RUN` header bit so the finalizer thread skips it (no array manipulation — cheap).
- **Short vs long weak handle**: short is zeroed *before* finalizers run (ignores resurrection); long stays valid through resurrection (tracks resurrection).

## Mental Models
- Think of `Dispose` as **RAII replacement**, not memory reclamation — it frees *resources*, never the object's managed memory. The GC alone reclaims memory.
- Use a finalizer only as a **"safety net"** for forgotten explicit cleanup — never as a normal control-flow hook (e.g. logging, pooling).
- Think of the finalizer thread as an async worker: the GC can't call user finalizers inline or a `Thread.Sleep(1h)` finalizer would freeze/deadlock the whole GC.
- Use weak references when you want to **observe reachability without owning it** — the only easy way to test "is this object still alive?"

## Anti-patterns
- **Referencing other finalizable objects inside a finalizer**: finalizer order is undefined — the "owned" object may already be finalized (e.g. an injected `ILogger`).
- **Calling managed instance methods in a finalizer / relying on `this` after last use**: eager root collection can finalize the object mid-method (`ObjectDisposedException: Cannot access a closed file`). Fix with `GC.KeepAlive(this)`, `HandleRef`, or better, `SafeHandle`.
- **Throwing from a finalizer**: by default kills the whole process — always wrap in try-catch.
- **Adding a finalizer to a hot-path type**: allocation is ~40× slower and the object survives an extra GC generation.
- **`EvilPool` (resurrection-based object pool)**: once objects reach gen2, finalizers (and thus returns) may not run for hours. Use explicit pools like `ArrayPool<T>`.
- **Forgetting to unsubscribe events (`-=`)**: the delegate's `_target` field roots the listener; a long-lived/static source leaks all listeners.
- **Using `HandleRef` / `HandleCollector`**: legacy, don't prevent handle-recycling attacks — use SafeHandle.

## Code Examples

```csharp
class FileWrapper : IDisposable {
    private bool _isReleased = false;
    private IntPtr handle;

    protected virtual void Cleanup(bool fromFinalizer) {
        if (_isReleased) return;          // idempotent
        _isReleased = true;
        if (handle != IntPtr.Zero) {      // ALWAYS free unmanaged
            Unmanaged.CloseHandle(handle);
            handle = IntPtr.Zero;
        }
        if (fromFinalizer) return;        // skip managed cleanup from finalizer
        // call Dispose() on IDisposable fields here
    }
    ~FileWrapper() { Cleanup(true); }
    public void Dispose() { Cleanup(false); GC.SuppressFinalize(this); }
    public int UseMe() {
        if (_isReleased) throw new ObjectDisposedException(GetType().Name);
        // ObjectDisposedException.ThrowIf(_isReleased); // newer .NET
        ...
    }
}
```
- **What it demonstrates**: the author's cleaner Disposable pattern — `Cleanup(bool fromFinalizer)` shared by finalizer and `Dispose`, guarded by `_isReleased`, with `SuppressFinalize`.

```csharp
GC.Collect();
GC.WaitForPendingFinalizers();
GC.Collect();
```
- **What it demonstrates**: "the-ultimate-explicit-GC" — 1st GC finds fReachable objects, wait runs their finalizers (making them truly unreachable), 2nd GC reclaims them.

## Reference Tables

Finalizable vs non-finalizable allocation (BenchmarkDotNet, Listing 12-12):

| Method | N | Mean | Gen 0 | Gen 1 | Allocated |
|---|---|---|---|---|---|
| ConsumeNonFinalizableClass | 1 | 2.78 ns | 0.0076 | - | 32 B |
| ConsumeFinalizableClass | 1 | 132.14 ns | 0.0074 | 0.0036 | 32 B |
| ConsumeNonFinalizableClass | 1000 | 3,244 ns | 7.63 | - | 32000 B |
| ConsumeFinalizableClass | 1000 | 131,725 ns | 7.57 | 3.66 | 32000 B |

~40× slower; finalizable objects trigger gen1 GCs (extra promotion). Same allocated bytes.

Finalization-related CLR ETW events (`Microsoft-Windows-DotNETRuntime/GC`):

| Event | Meaning |
|---|---|
| FinalizersStart | Finalizer thread wakes after a GC |
| FinalizeObject | Emitted per finalizable object processed |
| FinalizersStop | Whole fReachable batch finished (missing = never catching up) |

Diagnostic performance counters:

| Counter | Meaning |
|---|---|
| `.NET CLR Memory\Finalization Survivors` | # objects moved finalization→fReachable in last GC |
| `.NET CLR Memory\Promoted Finalization-Memory from Gen 0` | total size promoted due to finalization (all gens, despite name) |

Note: **no counter exists for finalization rate or fReachable queue size** — the actual leak indicator.

## Worked Example
**Scenario 12-1 — Finalization memory leak.** An app's `Gen 2 heap size` and `Bytes in all Heaps` climb steadily. Cause: allocation rate of finalizable objects exceeds finalization rate, so the single finalizer thread can't drain the fReachable queue (here each `~EvilFinalizableClass()` does `Thread.Sleep(10000)`).

Diagnosis path:
1. **Perf counters mislead** — `Finalization Survivors` and `Promoted Finalization-Memory` stay flat (only one object promoted per GC); nothing alarming.
2. **PerfView ETW events** reveal the truth: a 10-second gap between each `FinalizeObject` and no `FinalizersStop` — the finalizer thread never catches up.
3. **SOS `!finalizequeue`** in WinDbg/dotnet-dump shows `Ready for finalization 5175 objects` — the fReachable backlog. `!finalizequeue -allReady` isolates the not-rooted fReachable instances (5,175 `EvilFinalizableClass`). SOSEX `!finq`/`!frq` give nicer output. Capturing successive dumps and watching this number grow confirms the leak.

Fix: avoid finalizers; if unavoidable, keep them tiny and fast.

## Key Takeaways
1. `Dispose`/finalizers manage *resources*, never reclaim managed memory — the GC does that.
2. Prefer explicit cleanup (`IDisposable` + `using` → try/finally); use a finalizer only as a safety net and call `GC.SuppressFinalize` in `Dispose`.
3. Prefer `SafeHandle` over custom finalizers — critically finalizable, ref-counted, P/Invoke-protected, blocks handle-recycling attacks.
4. Finalization has real cost: ~40× slower allocation, an extra generation of survival (worsens midlife crisis), a lock on the generational finalization queue, and a single finalizer thread that can back up.
5. Never touch `this`/managed methods late in a method or in finalizers — eager root collection can finalize you early; wrap finalizer bodies in try-catch (an escaping exception kills the process).
6. Events leak: the delegate roots the listener via `_target`; unsubscribe with `-=`, or use the WPF-style weak event pattern (`WeakEventManager`) when source outlives listeners.
7. Weak references (`WeakReference<T>.TryGetTarget`) enable weak caches and weak events without extending lifetime — short handles zero before finalizers, long handles track resurrection.

## Connects To
- **Ch 6**: object creation — finalizable types use the slow allocation path (`CORINFO_HELP_NEWFAST`, `RegisterForFinalization`).
- **Ch 7**: reference counting via IDisposable/`using` (Listing 7-3); `ArrayPool<T>` as the right pooling approach vs resurrection pools.
- **Ch 8**: eager (early) root collection JIT optimization — the root cause of "resource released too early."
- **Mark phase**: `GcShortWeakPtrScan`/`GcWeakPtrScan` null out weak targets; `ScanForFinalization` promotes to fReachable.
- **CriticalFinalizerObject / CER (Constrained Execution Region)**: guarantees for critical finalizers.
- **Rules 25 & 26**: "Avoid Finalizers" and "Prefer Explicit Cleanup."
