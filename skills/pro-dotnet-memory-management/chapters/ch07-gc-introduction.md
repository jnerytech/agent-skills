# Chapter 7: Garbage Collection - Introduction

## Core Idea
The .NET GC runs against a **condemned generation** (collecting it and everything younger), choosing per-collection between **Sweep** and **Compact**; its timing and generation selection are driven entirely by self-tuning **static** and **dynamic** data (chiefly the per-generation **allocation budget**), so explicit intervention is almost always harmful.

## Frameworks Introduced
- **Condemned generation model**: a GC always targets one generation and collects it plus all younger ones. LOH/POH are logically part of gen2.
  - When to use: reasoning about GC cost — gen0/gen1 collections stay inside one ephemeral segment (cheap, CPU-cached); gen2 = **Full GC** marks all of gen0/1/2/LOH/POH (orders of magnitude costlier).
  - How: gen0 condemned → only gen0 collected; gen1 → gen0+gen1; gen2 → everything (Full GC). Older generations are still *scanned* (via **card tables**) for cross-generational references even when not condemned.
  - Why it works / failure mode: generational hypothesis — most objects die young, so collecting only young generations reclaims most garbage cheaply. Failure mode: unnecessary Full GCs from long-lived roots.
- **Allocation budget (a.k.a. `desired_allocation`)**: per-generation limit on allocations before that generation's next GC.
  - When to use: understanding *why* a GC triggered and which generation was condemned.
  - How: each generation's `new_allocation` (remaining budget) is decremented as allocation contexts are handed out; when it goes negative, a GC of that generation is due. Promotion into an older generation consumes *its* budget (hence budgets tracked for gen1/gen2 too, though user code only allocates in gen0/LOH/POH). At end of GC, new budget is computed from the generation's **survival rate** (high survival → aggressively grow budget toward max; low → near minimum), clamped by static `limit`/`max_limit`.
- **GC step-by-step pipeline**: Trigger → Suspend managed threads (EE suspension) → run GC on triggering thread → Select condemned generation → **Mark** → **Plan** → **Sweep or Compact** (Relocate first if compacting) → Resume threads.
- **Collection Tuning heuristics**: an ordered list of condemned-reason checks; each may only *raise* the condemned generation (with few exceptions). See Reference Tables.

## Key Concepts
- **Workstation vs Server GC**: Workstation minimizes pause latency (single heap, frequent small GCs); Server maximizes throughput (one heap per logical core, infrequent longer GCs, higher memory use).
- **Non-concurrent vs Concurrent**: non-concurrent = full "stop the world"; concurrent = some GC work overlaps running managed threads. Chapters 7–10 assume non-concurrent Workstation.
- **Full GC**: gen2 condemned — marks all generations + LOH + POH. Avoid whenever possible.
- **Survival rate**: survived bytes ÷ total bytes in a generation; the main driver of the new allocation budget.
- **Remaining budget (`new_allocation`)**: space left in current budget; negative value triggers a GC. Reduced only when allocation contexts are created/grown, not per-object.
- **Induced GC**: any explicitly requested collection (`GC.Collect`, internal runtime calls).
- **EE suspension**: Execution Engine suspending all managed threads ("stop the world") at **safe points**.
- **Cooperative vs Preemptive mode**: cooperative = thread may be touching GC references (must be brought to a safe point); preemptive = running non-managed code, safe to ignore. EE suspension = force all threads preemptive.
- **Sweep vs Compact**: Sweep leaves survivors in place, reclaims dead space as free-list (fast, fragments); Compact moves survivors together (no fragmentation, but must Relocate = update all references).
- **Provisional mode**: transient auto-mode that, under high memory load + fragmented gen2, converts an expensive Full GC into a compacting **Gen1 GC** to fill gen2 gaps.

## Mental Models
- Think of the **allocation budget as a spending limit, not a size**: generations have no "default size" — they start empty and grow as budgets (derived from survival rate) allow. Gen0's budget often oscillates between two boundary values (e.g., 4 MB / 6 MB) because gen0 reacts so sensitively to survival rate.
- Use **survival rate to predict budget**: high survival → GC grows the budget (delaying next GC, hoping for a better dead:live ratio later); low survival → shrinks toward minimum.
- **Fewer objects is always better**: Plan cost scales with total object count (but linear/cache-friendly); Mark and Compact cost scale with *surviving* objects and inter-object references (non-linear, cache-hostile). Prefer one large LOH array sliced with `Span<T>` over many small arrays.
- Treat **`GC.Collect` as an anti-tool**: the GC won't run if it isn't productive; "reminding" it just disrupts its heuristics.

## Anti-patterns
- **Calling `GC.Collect` to "help" the GC**: a GC isn't triggered unless productive; if an object isn't collected, something still references it — forcing a GC won't free it and disturbs self-tuning heuristics.
- **Cyclic/routine `GC.Collect`**: sweeps the real problem (midlife crisis, ever-holding roots) under the rug instead of fixing lifetimes.
- **`GC.Collect(1)` to force ephemeral cleanup**: promotes still-reachable gen1 objects prematurely into gen2 (the ever-old generation) — the opposite of what you want.
- **Allocating many short-lived objects**: 12 GB allocated with stable heap sizes = massive temporary-object churn → constant AllocSmall GCs (Scenario 7-1 showed ~25 GCs/sec, ~24% time in GC).
- **`SuppressGCTransition` on non-trivial P/Invoke**: keeps the thread cooperative during the native call, freezing the whole app if a GC is triggered; only safe on methods guaranteed to return in a few ns (never I/O or synchronization).

## Code Examples
```csharp
// Method to calculate a generation size (from .NET Core source)
size_t gc_heap::current_generation_size (int gen_number) {
    dynamic_data* dd = dynamic_data_of (gen_number);
    size_t gen_size = (dd_current_size (dd)
                       + dd_desired_allocation (dd)   // allocation budget
                       - dd_new_allocation (dd));      // remaining budget
    return gen_size;
}
```
- **What it demonstrates**: approximate generation data size = current size + (budget − remaining budget); i.e., allocations since the last GC are the gap between budget and remaining budget.

```csharp
// Sample program driving Scenario 7-2 (allocation-budget walkthrough)
GC.Collect();
const int LEN = 1_000_000;
byte[][] list = new byte[LEN][];
for (int i = 0; i < LEN; ++i) {
    list[i] = new byte[25000];          // each ~25,024 bytes, kept reachable
    if (i % 100 == 0) {
        if (GC.CollectionCount(0) >= 20) break;
    }
}
```
- **What it demonstrates**: constant memory churn with ~100% survival — drives gen0 budget to its 128 MB max and repeatedly forces Full GCs until budgets stabilize.

## Reference Tables

**Static GC Data — 'Balanced' Mode (default; assuming 16 MB LLC cache)**

|      | Min alloc budget | Max alloc budget | Frag limit | Frag burden limit | limit | max_limit | time_clock | gc_clock |
|------|------------------|------------------|-----------:|------------------:|------:|----------:|------------|---------:|
| Gen0 | 8/10 MB (WKS/SVR)| 8–200 MB         | 40,000     | 0.5               | 9.0   | 20.0      | 1,000 ms   | 1        |
| Gen1 | 160 kB           | ≥ 6 MB           | 80,000     | 0.5               | 2.0   | 7.0       | 10,000 ms  | 10       |
| Gen2 | 256 kB           | SSIZE_T_MAX      | 200,000    | 0.25              | 1.2   | 1.8       | 100,000 ms | 100      |
| LOH  | 3 MB             | SSIZE_T_MAX      | 0          | 0.0               | 1.25  | 4.5       | 0 ms       | 0        |
| POH  | 3 MB             | SSIZE_T_MAX      | 0          | 0.0               | 1.25  | 4.5       | 0 ms       | 0        |

- Gen0 min budget scales with CPU cache; ephemeral (gen0/1) max budgets scale with ephemeral segment size. Override with `GCGen0MaxBudget`/`GCGen1MaxBudget`. Gen2/LOH max = SSIZE_T_MAX (logically unlimited). "Memory Footprint" latency mode uses similar values but smaller generation sizes.

**Fragmentation thresholds (Table 7-3)**

|      | Fragmentation Limit | Fragmentation Ratio |
|------|--------------------:|--------------------:|
| Gen0 | 40,000              | 75%                 |
| Gen1 | 80,000              | 75%                 |
| Gen2 | 200,000             | 50%                 |

- A generation is "too fragmented" when unusable-fragmentation size exceeds the Limit **and** exceeds the Ratio of total generation size (e.g., gen2 > 200,000 bytes and > 50%).

**GC type codes (PerfView "Gen" column)**: `N` = non-concurrent blocking · `B` = Background · `F` = Foreground (blocking ephemeral during BGC) · `I` = Induced blocking · `i` = Induced non-blocking.

**Condemned-generation heuristics (ordered; PerfView "Condemned reasons" names)**:
Generation Budget Exceeded · Time Tuning (WKS only; gen1 after 10 s+10 GCs, gen2 after 100 s+100 GCs — the "1:10:100 Golden Rule", now considered dated) · Internal Tuning (low card-table efficiency → gen1) · Ephemeral Low / Low Ephemeral Fragmented Gen2 · Fragmented Ephemeral · Expand Heap (segments only) · Compacting Full GC (last resort before OOM) · High Memory · Max Generation Budget · Fragmented Gen2 · Small Heap · Avoid Unproductive Full GC · Provisional Mode (×3) · HardLimit reasons (×3) · Ephemeral Before BGC.

## Worked Example
**Scenario 7-2 — first GCs of the byte-array loop (allocation-budget tuning):**
- **GC #1** (`2NI`, Induced full GC from `GC.Collect()`): gen0 begin 776,560 B, ~38% survive → 298,880 B promoted to gen1. Gen1/gen2 survival 0% → budgets reset to minimum (262,144). Gen0 budget set near max 16,777,216.
- **GC #2** (`2N`, AllocSmall): 16.78 MB in gen0 (exceeds gen0 budget) **and** 8 MB in LOH (exceeds 3 MB LOH budget → forces Full GC). Remaining budgets negative for gen0 (−13,168) and LOH (−4,854,328). ~99% gen0 survival → gen0 budget jumps to 134,217,728 (128 MB); LOH budget ×9.
- **GC #3** (`2N`): ~128 MB allocated; promotions cascade so gen0, gen1, gen2 remaining budgets all negative → condemned bumped to gen2 (Full GC). Gen0 budget pinned at 128 MB max.
- **GC #5** (`0N`): gen0 and gen2 budgets exceeded, but the check *stops at the first non-exceeded budget* — gen1's budget is not exceeded, so gen2 is never examined → stays a **gen0-only GC**. (Once gen1's budget is later exceeded, it becomes a Full GC.)

**Takeaway**: LOH allocations, promotion-driven budget consumption, and the first-non-exceeded-budget stopping rule together explain why "gen0" allocations frequently escalate into Full GCs.

## Key Takeaways
1. A GC condemns one generation plus everything younger; LOH/POH ride with gen2, so LOH pressure forces Full GCs.
2. Avoid Full GCs — they mark the entire heap across segments and can cost orders of magnitude more than a gen0/gen1 collection.
3. The **allocation budget** (driven by survival rate) is *the* mechanism deciding when a GC fires and which generation is condemned; generation "size" is an emergent, dynamic value, not a setting.
4. `GC.Collect` is almost never justified — legitimate cases: known intermittent batch churn, pre-warming caches before going online, pre-benchmark cleanup, WeakReference/leaky-third-party tests. Cyclic use masks real leaks.
5. Diagnose GC with PerfView **GCStats** (GC Rollup by Generation, GC Events by Time, Condemned reasons for GCs), performance counters (`% Time in GC`, `Gen N heap size`, `# Induced GC`), or `dotnet-gcmon`/`dotnet-trace`.
6. "Stop the world" needs all threads at **safe points**; partially-interruptible JIT code (safe points at calls, preferred) vs fully-interruptible (every instruction — used for unbounded loops without calls).
7. Prefer fewer, reusable objects (`Span<T>` over a large LOH buffer) — Mark/Compact cost scales with survivors and references.

## Connects To
- **Ch 5**: segments, generations, ephemeral segment, card tables, segment standby list, VM hoarding, regions.
- **Ch 6**: the Allocator, allocation contexts, fast/slow allocation paths — the source of AllocSmall/AllocLarge/OutOfSpace triggers.
- **Ch 8**: the **Mark** phase (next step in the pipeline).
- **Ch 9**: the **Plan** phase and **plugs** of grouped live objects.
- **Ch 11**: Concurrent/Background GC, Workstation vs Server modes, latency modes, Finalizer thread.
- **Ch 15**: `GC.AddMemoryPressure`/`RemoveMemoryPressure`, `GC.TryStartNoGCRegion`.
- **CLR/runtime internals**: Book of the Runtime GC design goals, `gc_reason`, `collection_mode`, `static_data`/`dynamic_data`, `gc_heap::generation_to_condemn`; `SuppressGCTransition` (.NET 5), `GCHeapHardLimit`, `GCHighMemPercent`.
