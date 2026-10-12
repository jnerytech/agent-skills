# Chapter 6: Memory Allocation

## Core Idea
Allocation in .NET is fast because most objects are created via **bump pointer allocation** inside a per-thread **allocation context** (a few assembly instructions), but this "fast path" can fall back to expensive slow paths (free-list scans, committing memory, triggering a GC) — so a performance-aware developer minimizes both explicit and hidden allocations.

## Frameworks Introduced
- **Bump Pointer Allocation (sequential allocation)**: Allocate by moving an `alloc_ptr` forward by the object size and returning its previous value. Used in SOH gen0.
  - When to use: the CLR's fast path for all small objects without a finalizer.
  - How: `if (alloc_ptr + amount <= alloc_limit)` bump the pointer (fast path); else run `try_allocate_more_space()` (slow path). Memory is pre-zeroed in advance inside the context.
  - Why it works: no locking needed — each thread owns its context (thread affinity via TLS, aka **TLAB**), so `Allocate` needs no synchronization and gives good data locality.
- **Allocation Context**: A span of ready-to-use, zeroed memory between `alloc_ptr` (allocation pointer) and `alloc_limit` (allocation limit). Grows by at least an **allocation quantum** (default 8 kB for SOH, dynamically 1,024–8,096 B) when exhausted; the SOH segment commits 16 pages (~64 kB) at a time.
- **Free-List Allocation (bucketed)**: Scan a per-generation list of free gaps ("free objects") to find one big enough. Buckets balance **best-fit** (many buckets) vs **first-fit** (one bucket) — fast scan without excessive fragmentation.
  - How: start at first appropriate bucket, take first matching free item, unlink it, zero it (only for user allocations), and re-link the remainder if it exceeds min size of two objects (48 B on 64-bit).
- **Allocation Helpers / Decision Tree**: JIT emits a helper for `newobj` at compile time (zero runtime overhead). Large or finalizable objects → generic slow `JIT_New` (`CORINFO_HELP_NEWFAST`); otherwise fast `JIT_TrialAllocSFastMP` (`CORINFO_HELP_NEWSFAST`).
- **Heap Balancing** (Server GC): Reassigns the most-allocating thread's context to another heap when heaps become unbalanced, then calls `SetThreadIdealProcessorEx` (Windows) to move the thread to the matching CPU. LOH balanced since .NET 4.5.

## Key Concepts
- **allocation quantum**: amount by which an allocation context grows on the slow path (default 8 kB SOH).
- **thread affinity**: each managed thread has its own allocation context in TLS, enabling lock-free allocation.
- **"free object"**: a dummy array-like object with a special "free object" method table (`g_pFreeObjectMethodTable`, 1-byte elements) marking free space on the heap so the scanner can jump over it; may carry an `undo` field.
- **undo element**: temporarily stores a removed free item's address during the Plan phase so a sweeping collection can revert planned allocations.
- **UOH (User Old Heap)**: shared code base for LOH + POH allocation (`GC_ALLOC_USER_OLD_HEAP = LARGE | PINNED`); no fast path, always slow-path, must zero (costly for MBs). LOH threshold = 85,000 bytes.
- **soh_try_fit / uoh_try_fit**: slow-path state machines — try free-list → committed memory → commit more → trigger GC(s) → `OutOfMemoryException`.
- **midlife crisis**: objects that live just long enough to be promoted to gen2 then die immediately — the worst case for the GC; solved by object pooling.
- **hidden allocation**: object created implicitly by an operation (delegate, closure, boxing, params array, LINQ iterator, async state machine).

## Mental Models
- Think of "allocations are cheap" as true **only on the fast path** — one bump of a pointer into pre-zeroed memory. The moment the context is exhausted you may hit free-list scans or a full GC.
- Use **structs over classes** when passing small, method-local data (Rule 16) — no heap allocation, better locality; pass by `ref` to avoid copies.
- Use **pooling** (ArrayPool, ObjectPool, RecyclableMemoryStream) when the same buffer/object is needed repeatedly or is large enough to hit LOH.
- Use **stackalloc + Span<T>** for small (<1 kB) temporary buffers to eliminate heap allocation entirely; the memory is implicitly pinned.

## Anti-patterns
- **Blindly using classes / heavy-allocating libraries**: every `new` is a potential slow path + GC pressure.
- **Excessive UOH allocations (Rule 15)**: zeroing multi-MB objects can take tens of ms; pool them instead.
- **String concatenation in loops**: each `+=` allocates a new immutable string — use StringBuilder / interpolation / String.Create.
- **`stackalloc` with unbounded/large size**: risks uncatchable `StackOverflowException`; guard with a size check.
- **Returning `Task<T>` from often-synchronous async methods**: allocates a Task; use `ValueTask<T>` (but not as a blanket Task replacement).
- **Boxing**: value type used as object/interface, `params object[]`, non-overridden `GetHashCode`/`ToString`, `GetType()`, foreach over `IEnumerable<T>` (boxes the struct enumerator).

## Code Examples
```asm
; rcx = MethodTable pointer; rax = new object address
LEAF_ENTRY JIT_TrialAllocSFastMP_InlineGetThread, _TEXT
mov     edx, [rcx + OFFSET__MethodTable__m_BaseSize]  ; object size (multiple of 8)
INLINE_GETTHREAD r11                                  ; TLS address
mov     r10, [r11 + OFFSET__Thread__m_alloc_context__alloc_limit]
mov     rax, [r11 + OFFSET__Thread__m_alloc_context__alloc_ptr]
add     rdx, rax          ; rdx = alloc_ptr + size
cmp     rdx, r10          ; compare to alloc_limit
ja      AllocFailed
mov     [r11 + OFFSET__Thread__m_alloc_context__alloc_ptr], rdx  ; bump alloc_ptr
mov     [rax], rcx        ; store MethodTable => new object
ret
AllocFailed:
jmp     JIT_NEW           ; fast path failed -> slow path
```
- **What it demonstrates**: the entire SOH fast path is a compare + add — the reason "allocations are cheap."

```csharp
// stackalloc + Span<T>, safe (no unsafe), guarded against stack overflow
Span<DataStruct> data = list.Count < 100
    ? stackalloc DataStruct[list.Count]
    : new DataStruct[list.Count];
```
- **What it demonstrates**: zero-allocation temporary buffer with a safety fallback to the heap for large sizes.

## Reference Tables

Free-List Bucket Configuration per Generation (Table 6-1):
| Region             | First Bucket Size | Number of Buckets |
|--------------------|-------------------|-------------------|
| Generation 0 and 1 | Int.Max           | 1                 |
| Generation 2       | 256 B (64-bit) / 128 B (32-bit) | 12  |
| LOH                | 64 kB             | 7                 |
| POH                | 256 B             | 19                |

(gen0/1 = single bucket, first-fit; gen2 uses a double-linked list since .NET 6 so it isn't reset at GC start.)

String formatting benchmark, format four D4 ints, .NET 8 (Table 6-8):
| Method              | Mean      | Allocated |
|---------------------|-----------|-----------|
| StringConcatenation | 295.5 ns  | 368 KB    |
| StringBuilder       | 211.1 ns  | 256 KB    |
| StringFormat        | 204.7 ns  | 208 KB    |
| StringInterpolation | 131.9 ns  | 56 KB     |
| WithHandler (stackalloc) | 101.6 ns | 56 KB |
| StringCreate        | 80.3 ns   | 56 KB     |

Async return types: `ValueTask<T>` is a struct discriminated union (result | Task | IValueTaskSource); avoids Task allocation on synchronous completion. `Task.FromResult` caches: `bool` (both), `int` −1..9, numeric 0, null.

## Worked Example
**Scenario 6-2 — Investigating allocations with dotnet-trace + PerfView.** An app parses Gutenberg books into a trie; `dotnet-counters` shows a 200 MB/s allocation rate but that number is meaningless without context.
1. Collect with allocation sampling: `dotnet-trace collect --profile gc-verbose -- WordStatsApp.exe --pages 5`.
2. Open the `.nettrace` in PerfView → **GC Heap Alloc Ignore Free (Coarse Sampling) Stacks**.
3. In **By Name**, sort by **Exc** descending → top offenders; use *Goto → Goto Item in Callers* to find where e.g. `System.CharEnumerator` is allocated.
4. To blame a method: set `[No grouping]`, Find `TryNormalize`, *Goto → Goto Item in Callees*.
   - Diagnosis: `TryNormalize` allocates 200+ MB of `Char[]` — from `word.ToLowerInvariant()`, `.Trim(...)`, and `result.Any(c => ...)` (a delegate + closure + iterator). Classic hidden allocations. Fixing them (Span-based normalization) removes the churn.
   - Aside: `GC.GetAllocatedBytesForCurrentThread()` gives exact per-thread bytes allocated.

## Key Takeaways
1. The fast path is a few assembly instructions bumping a per-thread `alloc_ptr`; everything else (free-list, committing, GC) is comparatively expensive.
2. LOH/POH (UOH) have **no** fast path and must zero memory — big-object allocation cost is dominated by zeroing; pool them (Rule 15).
3. `OutOfMemoryException` is thrown after the GC already ran (even full compacting) — manually triggering GC rarely helps (except LOH compaction); seeing free RAM at OOM is normal (often 32-bit VM fragmentation → recompile to 64-bit).
4. Prefer **structs, ValueTuple, stackalloc, ArrayPool, ObjectPool, RecyclableMemoryStream, ValueTask** to cut allocations — measured 2–4× speedups and often 0 B allocated.
5. Hunt **hidden allocations**: delegates (cache non-capturing lambdas — static field since .NET 8 for method groups too), closures (`<>c__DisplayClass`), boxing, `params` arrays, `yield`/async state machines, LINQ iterators (~48 B each).
6. Don't over-optimize — apply Rule 5 (Measure GC Early); only attack allocations on hot paths (Rule 14).

## Connects To
- **Ch 5**: allocation happens inside segments/regions, ephemeral segment (gen0/1), all-at-once memory strategy, reserve/commit two-stage building.
- **Ch 7**: Plan/compact/sweep phases, `undo`-based reversal of planned allocations, LOH compaction.
- **Ch 11**: Concurrent Sweep and foreground GC motivated the gen2 double-linked free-list (.NET 6).
- **Ch 12**: finalizers add overhead (Rule 25), Gen2GcCallback drives ArrayPool trimming.
- **Ch 14**: `Span<T>`, `ref` locals, System.IO.Pipelines as lower-allocation Stream alternative.
- **CLR internals / x64 ABI**: TLS-based allocation contexts (TLAB), 16-byte stack alignment for `localloc`, NUMA-aware heap-to-CPU assignment.
