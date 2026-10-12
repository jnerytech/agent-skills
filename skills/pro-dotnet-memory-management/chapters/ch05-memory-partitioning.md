# Chapter 5: Memory Partitioning

## Core Idea
The GC Managed Heap is too big to treat uniformly, so .NET partitions it by object **size** (SOH/LOH) and **lifetime** (generations), plus special kind-based heaps (POH, NonGC Heap) — enabling the Collector to reclaim young objects cheaply and often while touching old objects rarely.

## Frameworks Introduced
- **Partitioning strategies**: A GC can split the heap by one of five object properties — **Size**, **Lifetime**, **Mutability**, **Type**, **Kind**. .NET (and Mono) chose only the first two (size + lifetime); it just manages "N bytes," ignoring type/mutability, with later optimizations for string literals and pinned arrays.
- **Size partitioning (SOH vs LOH)**: Single threshold of **85,000 bytes** (NOT 85·1024) splits Small Object Heap from Large Object Heap.
  - When to use: separates cheap-to-copy small objects from expensive-to-copy large ones.
  - How: objects `< 85,000` bytes → SOH (compactable); `>= 85,000` bytes → LOH (sweep-only by default). Threshold is **shallow size** (references count as pointers). Raise via `LOHThreshold` (cannot lower).
  - Why: compacting large objects has huge copy cost; sweep avoids it at cost of fragmentation.
- **Generational GC (lifetime partitioning)**: SOH is split into **gen0 (young)**, **gen1 (intermediate)**, **gen2 (old)** by number of GCs survived.
  - When to use: exploits the generational hypothesis to collect gen0 frequently, gen2 rarely.
  - How: object survives gen N GC → **promoted** to gen N+1. .NET promotes via logical address boundaries (fast), not copying. Collecting a generation always collects it **and all younger** ones.
  - Why it works: **Weak generational hypothesis** (infant mortality) — most young objects die fast. Failure mode: violating it causes "Mid-Life Crisis" (Rule 18).
- **Remembered sets + card tables + write barriers**: Mechanism to track older-to-younger cross-generational references so partial (young-only) collections stay correct without traversing the whole graph.
  - How: JIT emits a **write barrier** on reference field writes; it dirties a **card** covering the source object; Mark phase treats objects in dirty cards as extra roots.

## Key Concepts
- **GC Heap / Managed Heap**: The Free Store region managed solely by the GC (vs Domain/Low/High Frequency heaps used by the Execution Engine).
- **SOH / LOH**: Small (`<85K`) / Large (`>=85K`) Object Heap; LOH tracked internally as **generation 3** but collected only with gen2.
- **Ephemeral generations**: gen0 and gen1 (treated as "young"); gen2 is "old."
- **Promotion / demotion**: Moving an object to an older generation on survival; demotion (not promoting) is the exception.
- **Remembered set**: Separately managed collection of older-to-younger references, added during Mark phase as roots.
- **Card table**: Bitmap where each bit = 256 bytes (64-bit) / 128 bytes (32-bit); marks regions containing cross-gen references "dirty."
- **Card bundles**: Higher-level bitmap (1 bit = 32 card words = 256 KB) for fast scanning of sparse card tables.
- **Write barrier**: JIT-injected code on reference writes that sets cards; runtime-patchable placeholder.
- **NonGC Heap (NGCH / Frozen heap)**: Immortal readonly literal strings (<64K) and `typeof()`/`GetType()` runtime types; outside GC.
- **Pinned Object Heap (POH)**: Since .NET 5; for pinned arrays of blittable types via `GC.AllocateArray`/`AllocateUninitializedArray`.
- **Segment vs Region**: Pre-.NET 7 uses **segments** (one ephemeral segment holds gen0/1); .NET 7+ (64-bit) uses **regions** (each gen/heap-kind its own region, no ephemeral segment).

## Mental Models
- **Think of generations as boundaries, not boxes**: .NET promotes by moving logical address boundaries — no copy needed — so promotion is nearly free.
- **Card table is a trade-off dial**: card too small → full remembered-set overhead; card too big → whole-graph traversal. 256 bytes/card (whole byte set = 2048 bytes) balances it.
- **Reserved ≠ committed**: A Server-mode heap may "reserve" 18 GB but commit only 8 MB. Never read reserved memory as real usage (Scenario 5-3).
- **Use gen2 size trend to detect leaks**: gen0/gen1 stay small; a rising gen2 sawtooth ceiling signals a leak.

## Anti-patterns
- **Reading `Gen 0 heap size` counter as real gen0 size**: It reports the **allocation budget** (bytes until next gen0 GC), not size — misleading. Use ETW for true gen0.
- **Excessive LOH allocations** (Rule 15): large short-lived arrays/JSON scatter and fragment the sweep-only LOH. Pool reusable buffers.
- **Unnecessary heap references** (Rule 12): every intergenerational reference triggers the card-table machinery; the best cross-gen reference is none.
- **32-bit arrays of doubles ≥1000 elements**: land in LOH and fragment it — pool them.

## Code Examples
```csharp
double[] array1 = new double[999];
Console.WriteLine(GC.GetGeneration(array1)); // prints 0
double[] array2 = new double[1000];
Console.WriteLine(GC.GetGeneration(array2)); // prints 2
```
- **What it demonstrates**: On 32-bit runtime, `double[]` with ≥1000 elements is force-allocated in LOH (8-byte alignment) even at ~8000 bytes, breaking the 85K rule.

```asm
01. LEAF_ENTRY JIT_WriteBarrier_PostGrow64, _TEXT
03.   mov  [rcx], rdx        ; store value (rdx) at address (rcx)
06.   mov  rax, 0F0F...0h    ; lower ephemeral bound (patched at runtime)
07.   cmp  rdx, rax
08.   jb   Exit              ; source below young gen -> skip
11.   mov  r8,  0F0F...0h    ; upper ephemeral bound (patched)
12.   cmp  rdx, r8
13.   jae  Exit              ; source above young gen -> skip
16.   mov  rax, 0F0F...0h    ; card table address (patched)
17.   shr  rcx, 0Bh          ; divide dest address by 2048
18.   cmp  byte ptr [rcx+rax], 0FFh
19.   jne  UpdateCardTable
20.   REPRET
22.   mov  byte ptr [rcx+rax], 0FFh  ; set whole byte (8 cards)
```
- **What it demonstrates**: The write barrier only checks if the **source** ref is in ephemeral (young) generations, then dirties a whole byte (2048 bytes) of the card table. It does NOT check the target generation — young-to-young cards are set but ignored during Mark.

## Reference Tables

**Generation size measurement sources (Table 5-1):**
| Generation | GC event (GCHeapStats_V2) | Perf Counter / dotnet-counters |
|---|---|---|
| 0 | GenerationSize0 | Gen 0 heap size (**allocation budget!**) / Gen 0 Size (B) |
| 1 | GenerationSize1 | Gen 1 heap size / Gen 1 Size (B) |
| 2 | GenerationSize2 | Gen 2 heap size / Gen 2 Size (B) |
| 3 (LOH) | GenerationSize3 | Large Object Heap size / LOHSize (B) |
| 4 (POH) | GenerationSize4 | Pinned Object Heap size / POH Size (B) |

**Default segment size (pre-.NET 7, Table 5-3):**
| | WS 32-bit | WS 64-bit | Server 32-bit | Server 64-bit |
|---|---|---|---|---|
| SOH | 16 MB | 256 MB | 64/32/16 MB (by #CPU) | 4/2/1 GB (by #CPU) |
| LOH | 16 MB | 128 MB | 32 MB | 256 MB |

**Card table granularity (64-bit):** 1 bit = 256 B; 1 byte = 2048 B; card word (4 B) = 8192 B. Card bundle: 1 bit = 32 card words = 256 KB; 4-byte bundle word = 8 MB.

**Region sizes (.NET 7+):** Basic (SOH gen0/1/2) = usually 4 MB (or 2/1 MB); Large (LOH/POH) = 8× basic; Huge = arbitrary (LOH allocations exceeding large region).

## Worked Example
**Scenario 5-2 — nopCommerce memory leak diagnosis (WinDbg + SOS):**
1. Perf counters show `# Total committed Bytes` climbing then dropping repeatedly; **gen2** sawtooths up to ~1.3 GB while gen0/gen1 stay stable → gen2 is the suspect (LOH grows only ~38 MB, a red herring).
2. VMMap shows many Domain 1 Low/High Frequency heaps — **false clue**: loader-heap counters (`Current Classes Loaded`, `Current Assemblies`) don't move; those heaps are just nopCommerce's many dynamic types.
3. VMMap gen2 segments are 16 MB + single ephemeral segment → 32-bit Workstation GC (confirmed via `!eeversion`, `lmf` showing 32-bit clr.dll, .NET Framework 4.7).
4. `!heapstat` + `!eeheap`: gen2 = 1,217,024,356 bytes, low free space → not fragmentation, a real leak.
5. `!dumpheap -stat` on a segment: 33,786 `Microsoft.Extensions.Caching.Memory.CacheEntry` instances.
6. `!DumpObj` on the `<Key>k__BackingField` reveals keys like `Nop.pres.widget-79740-1-...`. `netext`'s `!wfrom` (LINQ-over-objects) lists all keys → each differs only by a customer-id number.
7. `!gcroot` traces: `ProductTagService → MemoryCacheManager → MemoryCache → CacheEntry`.
8. **Root cause**: cache key includes `CurrentCustomer.Id` (from cookie for anonymous users); the JMeter load test lacked an HTTP Cookie Manager, so every request was a new customer → unbounded cache growth. A test-harness bug, not a nopCommerce bug.

## Key Takeaways
1. Two active partitioning axes in .NET: **size** (SOH `<85K` / LOH `>=85K`) and **lifetime** (gen0/1/2). LOH is gen3 internally, collected with gen2.
2. Promotion in .NET moves **logical boundaries**, not objects — nearly free; "collect gen N" always collects all younger gens too.
3. Older-to-younger references are tracked by a **write barrier → card table → card bundles** pipeline; young-to-old is handled implicitly by always collecting younger gens.
4. Monitor **gen2 trend** (not gen0's misleading budget counter) plus `% Time in GC` to spot leaks and churn (Rule 11).
5. **Reserved vs committed**: huge reserved address space is not memory waste, especially 64-bit — check committed bytes (Scenario 5-3).
6. .NET 7+ replaces segments with **regions** (per-generation, poolable, reusable across generations), enabling Dynamic Promotion And Demotion (DPAD).
7. NonGC/Frozen heap and POH are kind-based heaps for immortal literals and pinned blittable arrays respectively.

## Connects To
- **Ch 1**: Free Store / CLI heap, copying GC, Mutator.Write write-barrier concept.
- **Ch 4**: Domain/Low/High Frequency heaps, string interning, PinnedHeapHandleTable, NGCH literal strings.
- **Ch 6**: Allocation, segment growth, Rule 15 (Avoid Excessive LOH Allocations).
- **Ch 7**: Sweep vs compact, Plan phase, pinning, LOH compaction, `% Time in GC` (Scenario 7-1).
- **Ch 8**: Dynamic Promotion And Demotion (DPAD), reading GC config (Scenario 8-1).
- **Ch 9 / 11**: Brick table (finding object start in a card), background GC (page-committed segment header).
- **Ch 10**: Rule 18 — Avoid Mid-Life Crisis (generational-hypothesis violation).
- **CLR/x64**: JIT_WriteBarrier / JIT_CheckedWriteBarrier helpers, `heap_segment`/`gc_heap`/`GCHeap` classes, `MEM_WRITE_WATCH`, `GetWriteWatch`, VM Hoarding (`GCRetainVM`/`System.GC.RetainVM`).
