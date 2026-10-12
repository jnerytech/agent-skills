# Patterns & Techniques

## Prefer struct over class
**When to use**: small, short-lived, method-local data; array elements read in bulk.
**How**: declare `struct`; store in arrays for contiguous cache-friendly layout (array-of-structs is packed; array-of-classes is scattered references). Pass large structs by `ref`/`in` to avoid copies.
**Trade-offs**: zero heap alloc + data locality, but copy cost grows with size and hidden boxing can bite; no identity/inheritance. Min heap object is 24 B (64-bit) — structs have no such overhead.

## Avoid boxing
**When to use**: value types used as `object`/interface, in `params object[]`, non-overridden `GetHashCode`/`ToString`, `foreach` over `IEnumerable<T>` (boxes struct enumerator).
**How**: use generics, override virtual methods on structs, use concrete collection types, cache boxed values.
**Trade-offs**: each box = one heap alloc + copy + GC pressure; eliminating it is nearly free.

## stackalloc + Span<T> for temp buffers
**When to use**: small (<1 kB) short-lived buffers on a hot path.
**How**: `Span<T> buf = n < 100 ? stackalloc T[n] : new T[n];` — guard size to avoid uncatchable `StackOverflowException`. Memory is implicitly pinned, zero heap alloc.
**Trade-offs**: eliminates allocation entirely; risky if size unbounded.

## ArrayPool<T> / object pooling
**When to use**: buffers reused repeatedly or large enough to hit LOH (≥85,000 B); to solve mid-life crisis and LOH fragmentation.
**How**: `ArrayPool<T>.Shared.Rent(n)` / `.Return(arr)`; `ObjectPool<T>`; `RecyclableMemoryStream`; `MemoryPool<T>.Shared`. Trimmed via `Gen2GcCallback`.
**Trade-offs**: avoids repeated zeroing (multi-MB zeroing costs tens of ms) and gen2 churn; you must return buffers and not retain references.

## Avoid mid-life crisis
**When to use**: objects that live just long enough to be promoted to gen2, then die — worst case for GC.
**How**: either make them truly short-lived (die in gen0) or pool them so they're long-lived and stable. Watch gen2 sawtooth trend.
**Trade-offs**: keeps gen2/full GCs rare; requires understanding object lifetimes.

## Reduce LOH allocations / fragmentation
**When to use**: large arrays, big JSON/images, `double[]≥1000` on 32-bit.
**How**: pool large buffers; prefer one large LOH array sliced with `Span<T>` over many small ones; avoid slightly-growing large allocations (poor hole reuse).
**Trade-offs**: LOH is sweep-only (no auto-compact) → fragments; pooling is the real fix.

## LOH compaction (last resort)
**When to use**: measured LOH fragmentation you can't fix by pooling.
**How**: `GCSettings.LargeObjectHeapCompactionMode = CompactOnce;` then `GC.Collect()` (background GC ignores the setting). Auto under hard memory limits.
**Trade-offs**: blocking; 100–200 ms per few-hundred MB, >1 s for GBs. Prefer pooling.

## Efficient string building
**When to use**: concatenation, especially in loops.
**How**: avoid `+=` (hidden `String.Concat` temporaries). Use interpolation, `StringBuilder`, `string.Format`, or `String.Create`/`ValueStringBuilder` (fastest, stackalloc→ArrayPool).
**Trade-offs**: interpolation/`String.Create` allocate ~6× less than concat.

## String interning
**When to use**: many long-lived duplicated strings.
**How**: `string.Intern`; literals interned by default (live in NonGC/Frozen heap).
**Trade-offs**: dedups memory but interned strings are immortal — harmful for temporary bursts.

## Hunt hidden allocations
**When to use**: hot paths with high alloc-rate (measure with `dotnet-trace --profile gc-verbose`, PerfView Alloc stacks, `GetAllocatedBytesForCurrentThread`).
**How**: eliminate closures (`<>c__DisplayClass`), non-cached delegates, `params` arrays, LINQ iterators (~48 B each), `yield`/async state machines, boxing. Cache non-capturing lambdas.
**Trade-offs**: 2–4× speedups, often 0 B; only optimize proven hot paths.

## ValueTask<T> over Task<T>
**When to use**: async methods that usually complete synchronously.
**How**: return `ValueTask<T>` (struct union: result | Task | IValueTaskSource); `Task.FromResult` caches bool/small ints.
**Trade-offs**: avoids Task alloc on sync completion; don't use as blanket Task replacement (single-await, no blocking).

## ref returns / ref locals / in params
**When to use**: expose collection elements or pass large value types without copying.
**How**: `ref T` returns/locals; `in` for read-only by-ref. Mark structs `readonly` to avoid defensive copies.
**Trade-offs**: type-safe, zero-copy; managed pointers can't live on heap; interior pointer can root its container.

## Span<T> / Memory<T>
**When to use**: `Span<T>` for synchronous zero-alloc slicing over array/stackalloc/native/string; `Memory<T>` when buffer must survive `await` or be a field.
**How**: `.Slice()`, `str.AsSpan()`, `.Span`; take `ReadOnlySpan<T>` params to accept both. Pair pooled/native memory with `IMemoryOwner<T>` + `Dispose`.
**Trade-offs**: `Span<T>` (ref struct) banned from heap/boxing/fields/async; "fast span" beats raw array.

## Pinning: use sparingly
**When to use**: passing managed buffers to native code.
**How**: prefer POH (`GC.AllocateArray(pinned:true)`); keep `fixed` scopes short OR reuse one long-lived pinned buffer. Diagnose via `PinObjectAtGCTime` ETW / `!GCHandles`.
**Trade-offs**: pinning forces zero relocation, pre/post-plug copying, fragmentation, plug extension — the source of most Plan-phase overhead.

## IDisposable + Dispose pattern
**When to use**: type owns unmanaged resources or IDisposable fields.
**How**: shared `Cleanup(bool fromFinalizer)` guarded by `_isReleased`; always free unmanaged; dispose managed fields only when not from finalizer; `Dispose()` calls cleanup + `GC.SuppressFinalize(this)`; throw `ObjectDisposedException` after release. Consume via `using`.
**Trade-offs**: deterministic resource release; frees resources not memory.

## Prefer SafeHandle over finalizers
**When to use**: wrapping any unmanaged handle (`IntPtr`).
**How**: derive from `SafeHandleZeroOrMinusOneIsInvalid`; override `IsInvalid` + `ReleaseHandle`. Owning class holds the field, needs no finalizer.
**Trade-offs**: critically finalizable, ref-counted around P/Invoke (no `GC.KeepAlive` needed), blocks handle-recycling attacks.

## Avoid finalizers
**When to use**: almost always — use only as a safety net for forgotten cleanup.
**How**: keep bodies tiny/fast; wrap in try-catch (escaping exception kills process); never touch other finalizable objects (order undefined). Prefer explicit Dispose/SafeHandle.
**Trade-offs**: ~40× slower allocation, extra generation survival, single finalizer thread can back up (fReachable leak).

## GC.KeepAlive for lifetime-critical objects
**When to use**: `Timer`/`Mutex`/handles held in a local not used after creation — eager root collection can collect them mid-use in Release.
**How**: `GC.KeepAlive(obj)` at the end of the region; or `Dispose`/`using`.
**Trade-offs**: setting locals to `null` is pointless (JIT already tracks real last-use).

## Weak references
**When to use**: observe reachability without owning it — weak events, time-based caches, "is it still alive?".
**How**: `WeakReference<T>.TryGetTarget` (atomic, type-safe); short handle zeroes before finalizers, long (`WeakTrackResurrection`) tracks resurrection.
**Trade-offs**: no lifetime extension; target may vanish anytime.

## ConditionalWeakTable / dependent handles
**When to use**: attach runtime "fields" to objects keyed by object lifetime; weak-event patterns.
**How**: `ConditionalWeakTable<TKey,TValue>` (weak keys, ReferenceEquals). Dispose/Clear.
**Trade-offs**: not aged (scanned every gen0), multipass Mark for chains — use sparingly.

## Unsubscribe events
**When to use**: any `+=` where source outlives listener.
**How**: `-=` in Dispose, or use `WeakEventManager`.
**Trade-offs**: delegate's `_target` roots the listener → leak whole graph otherwise.

## Server vs Workstation GC
**When to use**: Server for throughput/request-processing (default since 4.5); Workstation for responsiveness/small footprint/UI.
**How**: `System.GC.Server` true/false; single logical CPU forces Workstation.
**Trade-offs**: Server = parallel heap-per-core, fewer longer GCs, more CPU+memory; benchmark on near-prod using percentiles.

## Background (concurrent) GC
**When to use**: default; minimize pauses via concurrent gen2 marking.
**How**: `System.GC.Concurrent=true`; uses mark array + write watch + revisit.
**Trade-offs**: never compacts (floating garbage, occasional blocking full GC to fight fragmentation).

## Latency modes
**When to use**: short critical bursts, then revert.
**How**: `GCSettings.LatencyMode` = `SustainedLowLatency` (disables blocking full GCs; used by Roslyn/trading) or `LowLatency` (WKS-only, disables gen2). Guarantee revert (try/finally/CER).
**Trade-offs**: heap can balloon; expect an intense GC after — trigger it yourself.

## TryStartNoGCRegion
**When to use**: a critical path that must not be interrupted by GC.
**How**: `GC.TryStartNoGCRegion(totalSize)` (pre-reserves memory) → work → matching `GC.EndNoGCRegion()` in finally; defensively pre-check for a leaked region.
**Trade-offs**: no matching End → next call throws; segment GC requires size ≤ ephemeral segment.

## Avoid explicit GC.Collect
**When to use**: rarely — known batch churn, cache pre-warming, pre-benchmark cleanup, WeakReference tests.
**How**: if unavoidable use `GC.Collect(2, GCCollectionMode.Aggressive)`; ultimate cleanup = `Collect(); WaitForPendingFinalizers(); Collect();`.
**Trade-offs**: GC won't run if unproductive; `Collect(1)` prematurely promotes to gen2; cyclic calls mask real leaks.

## DATAS / hard memory limits
**When to use**: containers/dynamic load; cap heap.
**How**: `GCDynamicAdaptationMode` (adapts gen0 budget + server heap count); `GCHeapHardLimit`/`Percent` (container default 75%), runtime-adjustable via `AppContext.SetData(...,ulong)` + `GC.RefreshMemoryLimit()`; `GCConserveMemory` (0–9).
**Trade-offs**: less memory, more frequent GC; hard limit can auto-trigger LOH compaction.

## Avoid unnecessary cross-generational references
**When to use**: hot paths with complex reference graphs.
**How**: minimize older→younger references (each fires the write barrier → dirties card table); prefer fewer, flatter objects; the more reference fields, the more Mark/Relocate work.
**Trade-offs**: cheaper young GCs; may complicate design.

## Data-oriented design (AoS→SoA)
**When to use**: throughput-critical apps (trading, big data, games, ML).
**How**: fit hot fields in first cache line; Structure-of-Arrays (one array per field) for sequential prefetcher-friendly access; ECS for extreme cases. Iterate sequentially (row-major), avoid pointer-chasing.
**Trade-offs**: big cache-locality wins (avoids up to 7× false-sharing/miss costs); keep in Infrastructure layer, don't over-engineer.

## Escape analysis / stack allocation
**When to use**: let JIT allocate non-escaping reference types on the stack.
**How**: `DOTNET_JitObjectStackAllocation=1` (partial, off by default in .NET 8); helped by inlining, small non-array types, no loop allocation.
**Trade-offs**: free alloc elimination when it applies; blocked by arrays/strings/boxing/large types.

## Measure GC early
**When to use**: always, before optimizing.
**How**: track process memory growth + GC frequency/duration in CI/CD; `dotnet-counters` (gen2 trend, `% Time in GC`, alloc-rate), PerfView GCStats, `GC.GetGCMemoryInfo`, BenchmarkDotNet `[MemoryDiagnoser]`. Use percentiles/histograms, not averages.
**Trade-offs**: avoids premature optimization; only attack allocations on hot paths.
