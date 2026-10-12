# Chapter 2: Low-Level Memory Management

## Core Idea
The .NET runtime and its GC are shaped by hardware and OS constraints — DRAM timings, CPU caches (cache lines), virtual memory, and NUMA. Understanding these leaky abstractions explains why sequential access, data locality, and alignment matter, and why the GC does what it does.

## Frameworks Introduced
- **Cache-line reasoning (spatial/temporal locality)**: All RAM↔CPU transfer happens in fixed 64-byte **cache lines**; nothing smaller is ever read/written.
  - When to use: designing hot-path data structures, loops over large arrays.
  - How: keep data small and contiguous; iterate sequentially so each loaded cache line is fully consumed; exploit **temporal locality** (reuse loaded data) and **spatial locality** (neighbors get loaded free). A **cache hit** is near-free; a **cache miss** stalls the CPU while a full line loads from DRAM.
  - Why it works: DRAM sequential burst reads avoid costly row precharge/RAS/CAS timing penalties; the whole 64 bytes come nearly for free, so full utilization amortizes the miss.
- **False sharing avoidance**: Threads writing to *distinct* variables that land on the *same* cache line force constant cross-core invalidation via the cache-coherency protocol (**MESI**: Modified/Exclusive/Shared/Invalid).
  - When to use: any multithreaded code with per-thread counters/state in a shared array or object.
  - How: pad/space per-thread data so each sits on its own 64-byte line; also account for object headers (array length) sharing the first line — offset past it (see Worked Example).
  - Failure mode: naive adjacent per-thread elements → up to 7× slowdown from coherency traffic.
- **Virtual memory reserve/commit model**: OS maps per-process virtual address space to physical RAM in **pages** (typically 4 kB) via the MMU, page directories, and **TLB** caches.
  - When to use: understanding how the CLR obtains memory from the OS.
  - How: On Windows the CLR calls `VirtualAlloc` with `MEM_RESERVE` (claim contiguous address range, no physical RAM) then commits pages on demand; frees with `VirtualFree`/`MEM_DECOMMIT`. Linux has no reserve step (lazy allocation) — simulated with `PROT_NONE`.

## Key Concepts
- **Cache line**: Fixed 64-byte block; the atomic unit of transfer between RAM and CPU cache.
- **Cache hit / miss**: Data found in cache (fast) vs. must load from RAM (slow, stalls CPU).
- **Stall**: CPU cycles wasted waiting on a memory access.
- **Data locality**: Temporal (reuse same region soon) + spatial (access nearby addresses) — the basis caches rely on.
- **Hierarchical cache**: L1 (split L1i/L1d, per-core), L2 (per-core), L3 (shared) — smaller/faster to larger/slower.
- **False sharing**: Independent data on one cache line causing needless coherency invalidations across cores.
- **Cache coherency / MESI**: Protocol keeping per-core cache copies consistent; imposes memory-traffic overhead.
- **Virtual memory / page / TLB**: OS abstraction mapping virtual→physical in 4 kB pages; TLB caches translations to avoid page-directory walks.
- **NUMA / NUMA factor**: Memory access cost varies by which CPU/node accesses it; extra cost of non-local memory is the NUMA factor.
- **Working set / private bytes / RSS**: Committed pages resident in RAM vs. all committed pages (incl. paged) — the "how much memory?" indicators.

## Mental Models
- Think of memory as **not** a flat byte array — every access drags in a 64-byte line, so random 1-byte reads waste 63/64 of the bandwidth and the cache.
- Use **Modified Harvard Architecture** framing: instructions (L1i) and data (L1d) split only at L1; unified above.
- Think of **reserve** as "claim address space" and **commit** as "back it with real RAM" — the CLR reserves big, commits lazily (also how thread stacks grow).
- All non-trivial abstractions are leaky (Joel Spolsky): the cache/ISA "hides" hardware, yet access patterns still leak through as measurable slowdowns.

## Anti-patterns
- **Column-by-column (non-sequential) array traversal**: Loads a full cache line to use one element, then evicts it — up to 7× slower than row-by-row.
- **Adjacent per-thread data**: Triggers false sharing; coherency overhead dominates.
- **Random / pointer-chasing access (e.g., doubly-linked lists)**: Defeats prefetching and cache reuse.
- **Defaulting to non-temporal / prefetch instructions as a "fast path"**: Tricky, alignment-sensitive, easy to make code slower; use only in proven hotspots.

## Code Examples
```csharp
// Version #1 false sharing; tune offset/gap to move each thread to its own cache line
const int offset = 1; const int gap = 0;
public static int[] sharedData = new int[4 * offset + gap * offset];
public static long DoFalseSharingTest(int threadsCount, int size = 100_000_000) {
    Thread[] workers = new Thread[threadsCount];
    for (int i = 0; i < threadsCount; ++i) {
        workers[i] = new Thread(new ParameterizedThreadStart(idx => {
            int index = (int)idx + gap;
            for (int j = 0; j < size; ++j)
                sharedData[index * offset] = sharedData[index * offset] + 1;
        }));
    }
    for (int i = 0; i < threadsCount; ++i) workers[i].Start(i);
    for (int i = 0; i < threadsCount; ++i) workers[i].Join();
    return 0;
}
```
- **What it demonstrates**: How element spacing (offset/gap) determines whether threads collide on one cache line — the source of false sharing.

```csharp
// Row (sequential) vs column (non-sequential) indexing of the same 5000x5000 array
for (int i = 0; i < n; ++i) for (int j = 0; j < m; ++j) tab[i, j] = 1; // by rows
for (int i = 0; i < n; ++i) for (int j = 0; j < m; ++j) tab[j, i] = 1; // by columns
```
- **What it demonstrates**: Identical work, but column order breaks spatial locality → multi-fold slowdown.

## Reference Tables

Latency to access memory levels (Haswell i7, ~0.4 ns/cycle):

| Operation   | Latency    |
|-------------|------------|
| L1 cache    | < 2.0 ns   |
| L2 cache    | 4.8 ns     |
| L3 cache    | 14.4 ns    |
| Main memory | 71.4 ns    |
| HDD         | 150 000 ns |

Row vs. column indexing (5000×5000 ints):

| Pattern    | PC    | Laptop | Raspberry Pi 2 |
|------------|-------|--------|----------------|
| By Rows    | 52ms  | 127ms  | 918ms          |
| By Columns | 401ms | 413ms  | 2001ms         |

False sharing benchmark (Listing 2-6):

| Version                | PC   | Laptop | Raspberry Pi 2 |
|------------------------|------|--------|----------------|
| #1 (offset=1, gap=0)   | 5.0s | 6.7s   | 29.0s          |
| #2 (offset=16, gap=0)  | 2.4s | 2.6s   | 13.8s          |
| #3 (offset=16, gap=16) | 0.7s | 0.8s   | 12.1s          |

Windows virtual address space limits (User/Kernel):

| Process Type | Win 32-Bit | Win 8/Server 2012 | Win 8.1+/Server 2012+ |
|--------------|-----------|-------------------|-----------------------|
| 32-bit       | 2/2GB     | 2/2GB             | 2/2GB                 |
| 32-bit (LAA) | 3/1GB     | 4 GB/8 TB         | 4 GB/128 TB           |
| 64-bit       | -         | 8/8 TB            | 128/128 TB            |

DRAM timings (e.g., DDR3 9-9-9-24): **tCL** (CAS latency), **tRCD** (RAS→CAS delay), **tRP** (row precharge), **tRAS** (row active delay). Row changes are the expensive ones — the reason sequential access wins.

## Worked Example
**Eliminating false sharing in three steps** (Table 2-3). Four threads each increment "their own" int in a shared array on a 4-core PC.

1. **Version #1 (offset=1, gap=0)** — 5.0s. All four ints sit within one 64-byte cache line. Each increment on any core marks the line Modified, invalidating the other three cores' copies. Cores fight over one line via MESI → maximum coherency traffic.
2. **Version #2 (offset=16, gap=0)** — 2.4s. Use every 16th element (16 × 4 bytes = 64 bytes) so each thread's data is on its own line. Much faster, but *still* one line is constantly invalidated.
3. **Diagnosis of the residual cost**: In .NET the array object stores its **length at its beginning**, and every indexed access does a bounds check reading that header. So core 0's data shares the first cache line with the header that all cores read on every access → false sharing on the header line.
4. **Version #3 (offset=16, gap=16)** — 0.7s (~7× faster than #1). Add a full cache-line gap so element data starts past the header line. Each core now has a private read-only copy of the header line and modifies only its own data line — zero coherency overhead.

Takeaway: measurable performance depended on understanding cache lines *plus* the .NET object layout (header + bounds check).

## Key Takeaways
1. Everything moves in 64-byte cache lines — sub-line random access wastes bandwidth and cache; iterate sequentially.
2. Sequential DRAM access avoids row precharge/RAS/CAS penalties and enables hardware prefetching; random access defeats both.
3. False sharing can cost ~7×; space multithreaded per-thread data onto separate cache lines and account for object headers.
4. Non-local NUMA memory is slower; the .NET GC is NUMA-aware and balances allocations to the executing thread's node.
5. The CLR uses only the low-level Virtual API (`VirtualAlloc`/`VirtualFree`) — reserve big, commit lazily; Linux fakes reserve with `PROT_NONE`.
6. "Memory used" is ambiguous: track private working set / private resident (RSS) for real RAM impact, but private bytes reveal leaks.
7. Advanced tools (large pages, non-temporal `StoreAlignedNonTemporal`/MOVNT*, software prefetch, hardware intrinsics since .NET Core 3.0) are last-resort, hotspot-only, and easy to get wrong.

## Connects To
- **Ch 1**: Builds on Mechanical Sympathy and the heap/allocator theory; introduces book Rules 2–4 (avoid random access, improve locality, consider advanced options).
- **Ch 5**: Write barrier — how Linux replaces Windows' `GetWriteWatch`/`MEM_WRITE_WATCH` GC page-tracking.
- **Ch 6 / Ch 10**: CLR Allocator; reserve/commit/decommit lifecycle of GC pages.
- **Ch 13**: Object memory layout, data alignment, and data-oriented design.
- **CLR / OS APIs**: `VirtualAlloc`/`VirtualFree`/`VirtualLock`, `mmap`/`brk`, MMU/TLB, page directories, MESI, NUMA, DATAS-adjacent GC tuning (`DOTNET_GCLargePages`, `GCCpuGroup`, `gcServer`).
