# Cheatsheet — Decision Rules

## Core decision rules (When X → do Y, because Z)
- Object ≥ **85,000 B** → lands in LOH (gen3, sweep-only, rides with gen2) → **pool it (`ArrayPool`) or split it**, because LOH fragments and forces Full GCs.
- **32-bit + `double[]` ≥ 1000** → forced to LOH (~8 KB) → pool it; the 85K rule doesn't apply.
- Rising **gen2 size despite compacting gen2 GCs** → real leak → snapshot-diff to find the holding root; gen0/gen1 stay small always.
- **`% Time in GC` > 10–20%** (Workstation) → allocation churn → cut allocations / pool; in Server mode tolerate higher (work is parallel).
- **Latency spikes + frequent Full GCs** → try Server GC + Background, lower gen2 frequency, kill LOH pressure.
- **Objects promoted to gen2 then die fast (mid-life crisis)** → pool them so they never promote; never `GC.Collect` it away.
- **High alloc-rate but flat heap size** → temporary-object churn (constant gen0 GCs) → hunt hidden allocations.
- **OOM with free RAM (32-bit)** → VM fragmentation → recompile to 64-bit. `GC.Collect` won't help (GC already ran before OOM).
- **`Timer`/`Mutex`/handle in a local, collected mid-use in Release** → eager root collection → `GC.KeepAlive` or `Dispose`/`using`.
- Never `GC.Collect` to "help" — it disrupts self-tuning budgets. Legit uses only: batch-churn cleanup, cache pre-warm, pre-benchmark, LOH `CompactOnce`.

## Decision trees
- **Which GC flavor?** (`System.GC.Server` × `System.GC.Concurrent`)
  - Interactive/UI/desktop, low footprint → **Workstation + Background** (responsiveness).
  - Request-processing/web/service → **Server + Background** (default 4.5+; throughput, parallel heaps).
  - Data-crunching Windows service → switch default WKS → **Server**.
  - Single logical CPU → forced Workstation regardless.
  - Always benchmark all four on near-prod using **percentiles, not averages**.
- **struct vs class?**
  - Small, short-lived, local, rarely copied, no identity → **struct** (0 alloc, locality); pass large ones by `ref`/`in`.
  - Needs identity, sharing, inheritance → **class**.
  - Watch hidden boxing (object/interface cast, `params object[]`, foreach over `IEnumerable<T>`).
- **Resource cleanup?**
  - Unmanaged handle → **SafeHandle** (ref-counted, P/Invoke-safe, blocks recycling attack). Never hand-write a finalizer.
  - Owns IDisposable/unmanaged → **IDisposable + `using`**; finalizer only as last-resort net + `GC.SuppressFinalize` in `Dispose`.
  - Bare finalizer → avoid: ~40× slower alloc, extra generation survival, single drain thread backs up.
- **Buffer strategy?** temp <1 KB → `stackalloc`+`Span<T>`; reused/large → `ArrayPool`/`ObjectPool`/`RecyclableMemoryStream`; survives `await` or stored in field → `Memory<T>`+`IMemoryOwner<T>`.
- **Break a leak:** confirm (grows despite compacting gen2 GC) → diff two `.gcdump`/heap snapshots in PerfView → `!gcroot` the growing type → fix the root (event `-=`, cache key, static).

## Trade-off matrices
| | Workstation | Server |
|---|---|---|
| Latency | lower per-pause | short total suspension |
| Throughput | lower | higher |
| Memory | small footprint | larger (hanging garbage) |
| CPU | low | high (1–2 threads/core) |

| Cleanup | Determinism | Cost | Use |
|---|---|---|---|
| Finalizer | none | ~40×, +1 gen | last resort net |
| IDisposable | deterministic | cheap | owns resources |
| SafeHandle | deterministic | cheap | unmanaged handles |

Fewer, larger objects win: Mark/Compact scale with survivors + references (cache-hostile). One LOH array sliced by `Span<T>` > many small arrays.

## Thresholds & defaults
- LOH threshold **85,000 B** (not 85·1024); shallow size; `LOHThreshold` raises only.
- Min object **12 B** (32-bit) / **24 B** (64-bit, = plug-info size).
- Cache line **64 B** — false sharing costs up to ~7×; pad per-thread data past object header.
- SOH alloc quantum 8 KB; SOH commits ~64 KB (16 pages) at a time.
- Card table 64-bit: 1 bit=256 B, 1 byte=2048 B; card bundle bit=256 KB.
- Gen0 min budget 8/10 MB (WKS/SVR), scales with LLC; gen0 max up to 200 MB.
- Regions (.NET 7+, 64-bit): basic 4 MB, large (LOH/POH) 8×.
- Card efficiency < 30% (`DOTNET_GCLowSkipRatio`) → condemn gen1 not gen0.
- Fragmentation → compact when size **and** ratio both exceed: gen2 200,000 B & 25–50%.
- Container default `GCHeapHardLimit` = 75%; `GCHighMemPercent` ~90% triggers aggressive collect; set hard limit for `GCLargePages`.
- LOH compaction: **100–200 ms** per few-hundred-MB survivors, **>1 s** for GB — blocking; prefer pooling.

## Tells & smells (fast diagnostics)
- Rising **gen2 sawtooth ceiling** = leak (not gen0's "heap size" counter — that's the allocation budget).
- Reserved ≫ committed = normal (esp. 64-bit Server); read **committed bytes** for real usage.
- **fReachable queue growing** = finalizer thread can't keep up (no counter — use `!finalizequeue` / `FinalizersStop` missing).
- Growing region tells the tool: managed heap→gen2 leak; native Heap→malloc; Virtual/Unusable→bad `VirtualAlloc`; Loader→dynamic assemblies (`XmlSerializer` wrong ctor).
- High **pinned count** fragments heap → prefer POH / short `fixed` scopes / long-lived reused pinned buffers.
- Strings are always most numerous — investigate them **last**.
- Distrust averages — demand percentiles/histograms; counters are frozen between GC events (watch deltas).
