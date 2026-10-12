# Chapter 11: GC Flavors and Settings

## Core Idea
.NET exposes two orthogonal GC mode axes — **Workstation vs. Server** and **Non-concurrent vs. Concurrent (Background)** — giving four flavors, plus dynamically-settable **latency modes**; the defaults are almost always right, but you must know the alternatives and how to benchmark them before changing anything.

## Frameworks Introduced
- **Two orthogonal mode axes → four flavors**: {Workstation | Server} × {Non-concurrent | Background}.
  - When to use: pick the axis that matches app shape (interactive/desktop → Workstation; request-processing/server → Server), then decide concurrency.
  - How: set `System.GC.Server` (true/false) and `System.GC.Concurrent` (true/false). Microsoft chose an **application-centric** approach (few knobs) vs. the JVM's **GC-centric** fine-grained tuning.
  - Failure mode: on a single-logical-CPU machine, Workstation GC is always forced regardless of `gcServer`.

- **Concurrent Marking (Background GC mark)**: discover reachability while user threads run.
  - How: (1) marking recorded in a separate **mark array** (1 bit per 16-byte heap region on 64-bit, 8-byte on 32-bit; bits only set, never cleared during concurrent mark) instead of flipping the MethodTable bit; (2) **write barriers** record every modification of an already-visited object into a **write watch list** (OS WriteWatch pre-.NET 5 / software write watch on non-Windows and Windows since .NET 5, page-granular = 4 kB); (3) modified objects are **revisited** as extra roots.
  - Why it works: solves the **"lost object" problem** (a visited object gains a reference to an otherwise-unreachable object). Cost: produces **floating garbage** (already-marked dead objects survive one cycle).

- **Background GC phase model (A–D)**: (A) initial stop-the-world (scan stacks + finalization queues into work list, often a piggybacked ephemeral GC); (B) concurrent mark (handles + work list + write watch list; emits `BGCDrainMark`, `BGCRevisit`); (C) final mark stop-the-world ("final truth", incremental catch-up, weak/dependent handles); (D) concurrent sweep. **Foreground GCs** (regular non-concurrent ephemeral collections) may fire during B and D.

- **Latency modes (`GCSettings.LatencyMode`)**: dynamically dial GC intrusiveness — Batch, Interactive, LowLatency, SustainedLowLatency, NoGCRegion.

## Key Concepts
- **Foreground GC**: a regular non-concurrent ephemeral GC that runs during a background GC (background GC is temporarily suspended); may be compacting and expand the heap.
- **Full-blocking GC**: a full (gen 2) GC done non-concurrently; the most costly pause.
- **Mark stealing**: Server GC threads steal batches of objects to visit from each other to balance unequal heaps.
- **Server GC threads / Background GC threads**: Server Non-concurrent = 1 GC thread per heap (= per logical core); Background Server = 2 threads per heap (server + background) → 32 threads on 16 cores.
- **Floating garbage**: dead objects that survive a cycle because concurrent marking already marked them; trades aggressiveness for concurrency.
- **DATAS (Dynamically Adapting to Application Sizes)**: dynamically adjusts gen 0 budget and the number of server heaps based on last-3-GC metrics; built on conservative mode.
- **Configuration knobs**: runtime settings via `DOTNET_xxx` (or legacy `COMPlus_xxx`) env vars; numeric values in hex without `0x` prefix.

## Mental Models
- **Think of Workstation vs. Server as two config bundles, not literal machine types** — Server GC in a desktop app or Workstation GC in a web app is legitimate; it's about throughput+memory vs. responsiveness+low footprint.
- **Server mode trades memory for shorter total suspension**: fewer, parallel GCs → higher working set (more hanging garbage) but lower cumulative pause time.
- **Use latency modes for short bursts, then revert** — the stronger the mode, the shorter you should hold it; expect an intensive GC afterward (trigger it yourself at a controlled moment).
- **`% Time in GC` must be read relative to the mode**: in Server mode it looks small because work is parallel across heaps/cores — be more tolerant of high values in Workstation than in Server.

## Anti-patterns
- **Leaving default Workstation GC on a data-crunching Windows Service**: it behaves like a server workload; Server mode can massively improve throughput.
- **Trusting the config file for actual GC settings**: env vars/registry override it, and `COMPlus_/DOTNET_` override JSON. Only the runtime itself (via the Rundown event) tells the truth.
- **Judging modes by averages**: averages hide tail behavior — use **percentiles** for pause times and response times.
- **Setting LowLatency (or NoGCRegion) without a guaranteed revert**: on .NET Framework use a **Constrained Execution Region (CER)**; heap can balloon since gen 2 GCs are disabled.
- **Forgetting `GC.EndNoGCRegion()`**: every `TryStartNoGCRegion` needs a matching `End`, or the next `TryStartNoGCRegion` throws `InvalidOperationException` ("already in progress").

## Code Examples
```csharp
GCLatencyMode oldMode = GCSettings.LatencyMode;
RuntimeHelpers.PrepareConstrainedRegions();
try
{
    GCSettings.LatencyMode = GCLatencyMode.LowLatency;
    // Perform time-sensitive, short work here
}
finally
{
    GCSettings.LatencyMode = oldMode;
}
```
- **What it demonstrates**: safely setting a low-latency window with a CER so the `finally` revert is guaranteed (CERs deprecated on .NET Core, which already guarantees `finally`).

```csharp
// in case previous finally block didn't run
if (GCSettings.LatencyMode == GCLatencyMode.NoGCRegion)
    GC.EndNoGCRegion();
if (GC.TryStartNoGCRegion(1024, true)) {
    try { /* Do some work. */ }
    finally {
        try { GC.EndNoGCRegion(); }
        catch (InvalidOperationException ex) { /* Log message */ }
    }
}
```
- **What it demonstrates**: defensive NoGCRegion usage — pre-check for a leaked region, and swallow the "exceeds specified memory" exception on End.

```json
// SomeApplication.runtimeconfig.json (.NET Core)
"configProperties": {
    "System.GC.Server": true,
    "System.GC.Concurrent": true
}
```
- **What it demonstrates**: JSON GC configuration (overridable by `DOTNET_gcServer` / `DOTNET_gcConcurrent`, expected in hex).

## Reference Tables

**Four flavors (Table 11-1 condensed):**
| | WKS Non-concurrent | WKS Background | SVR Non-concurrent | SVR Background |
|---|---|---|---|---|
| GC threads | none (runs on triggering user thread) | 1 | = visible logical cores | = 2× logical cores |
| Batch | Yes (default) | Yes (disables BGC) | Yes (default) | Yes (disables BGC) |
| Interactive | Yes (enables BGC) | Yes (default) | Yes (enables BGC) | Yes (default) |
| LowLatency | Yes | Yes | No | No |
| SustainedLowLatency | No | Yes | No | Yes |
| GCHeapCount | No | No | Yes | Yes |
| Typical use | many lightweight apps tolerating longer pauses | interactive/UI, strict responsiveness | rare; compromise vs. Background Server | most request-processing apps (IIS web, services) — **default since 4.5** |

**Latency modes (`GCLatencyMode`):**
| Mode (value) | Effect | Availability |
|---|---|---|
| Batch (0) | ignore pause length; **default for non-concurrent**; disables BGC dynamically | all |
| Interactive (1) | minimize pauses; enables BGC; **default for concurrent** (= .NET default) | all |
| LowLatency (2) | disables ALL gen 2 GCs (concurrent + non-concurrent); full GC only on low-mem notif or explicit `GC.Collect` | Workstation only |
| SustainedLowLatency (3) | disables only **non-concurrent** full GCs (ephemeral + BGC allowed); needs concurrent enabled at startup | WKS + SVR |
| NoGCRegion (4) | disallow GC during a critical path if enough memory pre-reserved; set via `GC.TryStartNoGCRegion`, not the field | all |

**Server thread/heap knobs:** `GCHeapCount` (heaps+threads, < available logical CPUs), `GCNoAffinitize`, `GCHeapAffinitizeMask`/`GCHeapAffinitizeRanges`, `GCCpuGroup` (Windows CPU groups).

**Memory/footprint knobs:** `GCHeapHardLimit` / `GCHeapHardLimitPercent` (default container limit 75%), per-heap `GCHeapHardLimitSOH/LOH/POH` (+`...Percent`), `GCHighMemPercent` (aggressive-collect threshold, default ~90%), `GCConserveMemory` (0–9; fragmentation cap = (10−value)/10), `GCDynamicAdaptationMode` (DATAS; auto-sets ConserveMemory=5), `GCLargePages` (needs hard limit; else `0x8013200E`).

**NoGCRegion overloads:** `TryStartNoGCRegion(totalSize)`, `(totalSize, disallowFullBlockingGC)`, `(totalSize, lohSize)`, `(totalSize, lohSize, disallowFullBlockingGC)` — returns true if enough memory reserved; segment-based GC requires size ≤ ephemeral segment size or throws `ArgumentOutOfRangeException`.

## Worked Example
**Scenario 11-1 — Verify actual GC settings in production.** Config files can't be trusted (env vars/registry/typos override them), so ask the running process. Start and stop a short ETW/EventPipe session — the CLR emits `Microsoft-Windows-DotNETRuntimeRundown/Runtime/Start` whenever a session starts/ends. Inspect its `StartupFlags`:
- `dotnet trace collect --providers Microsoft-Windows-DotNETRuntimeRundown:0x80000000001:5 -p <pid>` (or PerfView for Framework, or Sasha Goldshtein's `etrace`).
- Flags: `CONCURRENT_GC` (0x1), `SERVER_GC` (0x1000), `HOARD_GC_VM` (0x2000). Combine them: Background Server = both `CONCURRENT_GC` + `SERVER_GC`; Non-concurrent Workstation = none listed. A raw value of `1` = concurrent Workstation; an IIS ASP.NET app showed `208919` (0x33017).

**Scenario 11-2 — Benchmark all four flavors (nopCommerce, dockerized).** Measure comprehensively, never on a dev box:
- GC overhead: `CPU Usage (%)` + `% Time in GC since last GC (%)` via `dotnet-counters` → CSV.
- Memory: `GC Heap Size (MB)` (same session).
- Pauses: `PauseMSec` via `dotnet-trace` `gc-collect` profile (low overhead) → PerfView GCStats → CSV.
- Client latency: JMeter Summary Report → CSV.
Findings (this app only): Server modes drive **much higher CPU** and **bigger heaps**; ephemeral pauses are fast in every mode, but **full-GC pauses** separate them — Non-concurrent Workstation is the clear loser (single blocking thread; severe >99th-percentile degradation), Background Server the best on pause percentiles. Response times were better on Server modes; long non-concurrent pauses barely showed in max response time because request processing dwarfed them (they matter most when requests finish in tens of ms). Conclusion: prefer a Server flavor here — at the cost of CPU/memory. **Always use percentiles, beware averages.**

## Key Takeaways
1. Four flavors = `System.GC.Server` × `System.GC.Concurrent`; single-core machines force Workstation regardless.
2. "Concurrent GC" was renamed **Background GC** (Workstation in 4.0, Server in 4.5) and is the modern default; Background never compacts, so a blocking full GC still fires occasionally to fight fragmentation.
3. Background GC stays correct via a **mark array** + **write barriers/write watch** + **revisiting**, accepting floating garbage as the price of concurrency.
4. Latency modes are **code-settable and dynamic**: LowLatency (WKS-only, disables gen 2), SustainedLowLatency (disables only blocking full GCs — used by Roslyn on keystrokes and by trading apps), NoGCRegion (reserve memory, disable GC for a critical path).
5. Server = throughput + parallel heaps + more CPU/memory; Workstation = responsiveness + small footprint. Tune Server load with `GCHeapCount`, affinity knobs, or DATAS.
6. Trust the runtime, not the config file — read `StartupFlags` from the Rundown event to confirm real settings.
7. There's no universal best mode: **measure your own app on a near-production environment using percentiles** (Rule 23, Rule 24).

## Connects To
- **Ch 7 (High-Level View, Static Data, Collection Tuning)**: mode overview origin; gen0 budget & **latency optimization goals/levels** (levels 0–1 supported; `GCLatencyLevel` knob) that will supersede latency modes.
- **Ch 5**: card tables / WriteWatch mechanism reused by concurrent marking; VM hoarding (`HOARD_GC_VM`).
- **Ch 8–10**: mark bit in MethodTable, Plan & Sweep phases — the non-concurrent baseline that foreground/blocking GCs use.
- **Ch 4**: single shared GC (`gc.cpp`) compiled twice into `WKS::`/`SVR::` namespaces (`SERVER_GC` → `MULTIPLE_HEAPS`); Background code under `#if BACKGROUND_GC`.
- **Ch 15**: `GC.GetConfigurationVariables()`, `GC.RefreshMemoryLimit()` (.NET 8).
- **DATAS / containers**: GC memory-limit auto-detection (75% default) and dynamic heap-count adaptation.
