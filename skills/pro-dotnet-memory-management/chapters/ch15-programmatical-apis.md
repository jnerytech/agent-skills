# Chapter 15: Programmatical APIs

## Core Idea
The GC can be controlled and measured from code at three levels of flexibility: the static `GC`/`GCSettings` classes for configuration, statistics, notifications and limits; the ClrMD and TraceEvent libraries for building diagnostic/monitoring tools; and — at the extreme — a pluggable custom (Local/Standalone) GC that replaces the built-in one entirely.

## Frameworks Introduced
- **GC API (static `GC` + `GCSettings` classes)**: thin managed wrapper over `InternalCall` runtime methods, grouped by function: statistics, notifications, unmanaged pressure, explicit collection, No-GC regions, finalization, memory limits.
  - When to use: in-process configuration, logging, diagnostics, and controlled explicit collection.
  - How: call `GC.GetGCMemoryInfo`, `GC.GetTotalAllocatedBytes`, `GC.CollectionCount`, `GCSettings.*`, etc. Methods are `[MethodImpl(InternalCall)]`, mapped in `ecalllist.h` → `comutilnative.cpp` → `gc.cpp`.
- **ClrMD (`Microsoft.Diagnostics.Runtime`)**: managed API to introspect live processes / dumps, SOS-equivalent from C#.
  - When to use: build custom diagnostic tools / dump analysis (also self-monitoring, cautiously).
  - How: get a `DataTarget` via `AttachToProcess(pid, suspend:true)` or `LoadDump`; from `ClrRuntime` reach `Heap` (`ClrHeap`), `SubHeaps`, `Segments`, `EnumerateObjects`, `EnumerateHandles`, `EnumerateRoots`. Uses the DAC (Data Access Component) to read CLR structures.
  - Why/failure mode: attaching without suspending is undefined behavior; for self-inspection prefer delegating to a child process.
- **TraceEvent (`Microsoft.Diagnostics.Tracing.TraceEvent`)**: collect/process CLR events via ETW (Framework) or EventPipe (.NET Core+).
  - When to use: low-overhead deep self-monitoring or offline ETL analysis of GC behavior.
  - How: `TraceEventSession` + `session.Source.Clr.GCStart/GCStop/GCHeapStats` handlers on Windows; on other OSes create an `EventPipeSession` via `DiagnosticsClient(pid)` and wrap in `EventPipeEventSource`. `Source.Process()` blocks until disposed.
- **Custom GC (Local/Standalone GC)**: replace the whole GC with your own DLL.
  - When to use: research/experiment; the .NET team itself ships `clrgc.dll` (old segment GC) and `clrgcexp.dll` (experimental).
  - How: set `DOTNET_GCName=Your.dll` (same folder as coreclr.dll) or `DOTNET_GCPath` (absolute, .NET 9+). Export `GC_Initialize` and `GC_VersionInfo`; implement `IGCHeap` (80+ methods) and `IGCHandleManager`.

## Key Concepts
- **`GC.GetGCMemoryInfo(GCKind)`**: returns a `GCMemoryInfo` struct with per-GC stats (promoted/fragmented/committed bytes, pause durations, per-generation size before/after); preferred way to assess GC efficiency since .NET Core 3.0.
- **`GC.GetTotalAllocatedBytes(precise)`**: ever-growing sum of bytes allocated across all heaps since process start; `precise:true` suspends threads for accuracy.
- **`GC.GetAllocatedBytesForCurrentThread()`**: cumulative per-thread allocations — fast, isolated; ideal for unit tests measuring allocations.
- **`GC.GetTotalMemory(forceFullCollection)`**: total size of live+dead managed objects, excluding fragmentation; can trigger up to 20 blocking GCs when `true`.
- **GC Notifications**: `RegisterForFullGCNotification` / `WaitForFullGCApproach` / `WaitForFullGCComplete` — predict approaching full blocking GC (only blocking GCs notify, not background).
- **No-GC Region**: `GC.TryStartNoGCRegion(totalSize...)` / `EndNoGCRegion` — reserve a budget within which GC is disallowed.
- **Unmanaged memory pressure**: `GC.AddMemoryPressure`/`RemoveMemoryPressure` — net pressure vs a budget (starts at 4 MB) can trigger a GC.
- **`MemoryFailPoint`**: disposable best-effort check that enough memory is available before critical work; throws `InsufficientMemoryException`; **Windows-only** implementation.
- **Memory Limits (runtime-adjustable, .NET 8+)**: set `GCHeapHardLimit*` via `AppContext.SetData` then call `GC.RefreshMemoryLimit()`.
- **Frozen Segment / NonGC Heap (NGCH)**: `GC._RegisterFrozenSegment`/`_UnregisterFrozenSegment` register native memory as never-scanned, never-collected heap for huge static data.

## Mental Models
- Use `GC.GetAllocatedBytesForCurrentThread` (not `GetTotalMemory`) when measuring allocations in tests — thread isolation gives clean, reproducible results.
- Think of `GC.GetTotalMemory` as a leak detector, not a process-memory gauge — it ignores fragmentation and segment overhead; pair with `Process.PrivateMemorySize64`/`WorkingSet64`.
- Use `GC.MaxGeneration` instead of hard-coding `2` when iterating generations.
- Think of a Custom GC as "the only limit is your imagination": `GarbageCollect` can be one line (`return NOERROR`) — a Zero GC that allocates and never reclaims.

## Anti-patterns
- **Using `GC.GetTotalMemory` for request throttling / memory limiting**: it excludes fragmentation and segment commit overhead, so it understates real memory pressure.
- **Attaching ClrMD to a non-suspended process**: officially unsupported, undefined behavior; self-attach in Release/production is risky.
- **Using frozen-segment APIs casually**: no runtime facility for arbitrary-location allocation — you manually write method-table pointers and manage lifetime; strongly discouraged.
- **Guessing wrong `RegisterForFullGCNotification` thresholds**: too high → false positives; too low → missed GCs. Requires per-workload experimentation.
- **Passing an invalid/stack object to `GC.GetGeneration`**: result is undefined (current .NET returns `int.MaxValue`).

## Code Examples
```csharp
GC.Collect(2, GCCollectionMode.Aggressive);
GCMemoryInfo info = GC.GetGCMemoryInfo(GCKind.Any);
if (info.Index != 0) {
    Console.Write($"#{info.Index} is gen{info.Generation}");
    if (info.Compacted)  Console.Write(" compacting");
    if (info.Concurrent) Console.Write(" concurrent");
    Console.WriteLine($"Promoted bytes   = {info.PromotedBytes}");
    Console.WriteLine($"Fragmented bytes = {info.FragmentedBytes}");
    Console.WriteLine($"Committed bytes  = {info.TotalCommittedBytes}");
    foreach (var pause in info.PauseDurations)      // always 2 entries
        if (pause.TotalNanoseconds > 0)             // ignore pause-less phase
            Console.WriteLine($"  {pause.TotalMicroseconds} us");
    // GenerationInfo index: 0=gen0 1=gen1 2=gen2 3=LOH 4=POH
}
```
- **What it demonstrates**: reading per-GC efficiency stats — the preferred replacement for PerfView's GCStats view, in-process.

```csharp
// Runtime-adjustable memory limit (.NET 8+): value MUST be ulong
AppContext.SetData("GCHeapHardLimitPercent", 50UL);
GC.RefreshMemoryLimit();   // suspends runtime; throws InvalidOperationException if too low
```
- **What it demonstrates**: adjusting `GCHeapHardLimit*` at runtime; non-`ulong` values are silently ignored.

## Reference Tables

Allocation-measurement APIs:

| API | Scope | Notes |
|-----|-------|-------|
| `GC.GetAllocatedBytesForCurrentThread()` | current thread | fast, cumulative; best for tests (Core 2.1+, Framework 4.8) |
| `GC.GetTotalAllocatedBytes(precise)` | all heaps | ever-growing; `precise` suspends threads (Core 3.0+) |
| `GC.GetTotalMemory(force)` | live+dead objects | excludes fragmentation; `force` may trigger ~20 GCs |
| `AppDomain.MonitoringTotalAllocatedMemorySize` | AppDomain | Framework only; alloc-context granularity |
| `AppDomain.MonitoringSurvivedMemorySize` | AppDomain | survivors; accurate after full GC |

Runtime-adjustable memory limits (.NET 8+): `GCHeapHardLimit`, `GCHeapHardLimitPercent`, and per-heap `GCHeapHardLimit{SOH,LOH,POH}` (+`...Percent`).

Custom-GC exports & interfaces: `GC_Initialize`, `GC_VersionInfo`; interfaces `IGCHeap`, `IGCHandleManager`; CLR callbacks via `IGCToCLR` (`SuspendEE`/`RestartEE`, `GcScanRoots`, `GcStartWork`/`GcDone`).

## Worked Example
**Listing NonGC string literals with ClrMD.** Attach and walk heaps to find literal strings that C# stores in the NonGC heap (a.k.a. Frozen segment):

```csharp
using DataTarget target = DataTarget.AttachToProcess(pid, suspend: true);
ClrRuntime runtime = target.ClrVersions[0].CreateRuntime();
ClrHeap heap = runtime.Heap;
if (!heap.CanWalkHeap) return;                       // must check before walking
foreach (ClrSubHeap subHeap in heap.SubHeaps)        // 1 (Workstation) or N=cores (Server)
    foreach (var segment in subHeap.Segments.OrderBy(s => s.Start))
        if (segment.Kind == GCSegmentKind.Frozen)    // NGCH / "Frozen"
            foreach (var obj in segment.EnumerateObjects())
                if (obj.IsValid && obj.Type?.IsString == true)
                    Console.WriteLine($"{obj.Address:x} \"{obj.AsString()}\"");
```
Key points the author walks through: check `CanWalkHeap`; a segment's `Kind` distinguishes SOH/`Large`(LOH)/`Pinned`(POH)/`Frozen`(NGCH); always test `IsValid` because the iterator may yield an object with address 0 or unknown type. To also see *unused* literals you must parse the assembly's `#US` stream via `System.Reflection.Metadata` (`PEReader.GetMetadataReader().GetUserString`).

## Key Takeaways
1. `GetGCMemoryInfo` (Core 3.0+) is the in-process way to judge GC efficiency; `.NET 8` adds `GC.GetTotalPauseDuration`.
2. Measure allocations with the thread-isolated `GetAllocatedBytesForCurrentThread`; measure leaks with `GetTotalMemory`; measure process pressure with `Process` properties.
3. GC notifications only fire for blocking GCs and are inherently predictive — tune thresholds per workload.
4. Since .NET 8 you can adjust `GCHeapHardLimit*` at runtime via `AppContext.SetData` + `GC.RefreshMemoryLimit` (values must be `ulong`).
5. ClrMD (introspection via DAC) and TraceEvent (ETW/EventPipe events) are the two library pillars for building diagnostic and self-monitoring tools with low overhead.
6. The GC is pluggable (Local/Standalone GC since .NET Core 2.1): a DLL exporting `GC_Initialize`/`GC_VersionInfo` and implementing `IGCHeap` can replace the built-in GC — the Zero GC never reclaims memory.
7. Frozen-segment/NGCH APIs let you store objects in unmanaged, never-scanned memory for gigabyte-scale static data — powerful but manual and discouraged.

## Connects To
- **Ch 5**: allocation context — basis of `GetAllocatedBytesForCurrentThread`'s implementation.
- **Ch 7**: explicit `GC.Collect` overloads and unmanaged memory pressure scenarios.
- **Ch 11**: `GCSettings.LatencyMode`, `IsServerGC`, No-GC regions, memory limits.
- **Ch 12**: `Gen2GcCallback`, finalization management, `PinnableBufferCache`.
- **Ch 4/9**: NonGC heap / string literals; pinned-object diagnostics.
- **DATAS / Server vs Workstation GC**: `GCDynamicAdaptationMode`, `HeapCount`, `ClrHeap.IsServer`.
- **CLR internals**: DAC, ETW/EventPipe, `IGCHeap`/`IGCToCLR` runtime contracts.
