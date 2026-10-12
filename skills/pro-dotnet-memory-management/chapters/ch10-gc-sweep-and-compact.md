# Chapter 10: Garbage Collection - Sweep and Compact

## Core Idea
Sweep and Compact are the final GC phases that merely *consume* the decisions already computed in the Plan phase — Sweep turns gaps into free-list items while Compact moves objects and rewrites references — yet because both touch/move memory, they are the most performance-impactful phases despite being the simplest to implement.

## Frameworks Introduced
- **Sweep Phase (SOH)**: Turn all no-longer-reachable objects into free space using Plan-phase info.
  - When to use: Plan phase decided NOT to compact (fragmentation acceptable / compaction not worth the cost).
  - How: (1) Create free-list items from every gap bigger than two minimal objects (smaller gaps counted only as fragmentation); (2) Restore saved pre-/post-plugs by writing them back over the "destroyed" object endings; (3) Update finalization queue for new generation boundaries and age/rejuvenate surviving handles; (4) Rearrange segments/regions, removing unneeded ones (or storing in a reusable list under VM hoarding).
  - Why it works: All heavy calculation was done in Plan; Sweep does only local modifications = little memory traffic = fast. Source: `gc_heap::plan_phase`, else-block of `should_compact`; key methods `make_free_lists` and `recover_saved_pinned_info`.
- **UOH Sweep (LOH/POH)**: No Plan phase involved at all.
  - How: Scan heap object-by-object (like SOH Plan), create free-list items between marked objects, delete no-longer-needed UOH segments/regions (unless VM hoarding keeps them in a reuse list).
  - Failure mode: Simple and efficient, but its only disadvantage is fragmentation — users can explicitly ask for LOH compaction.
- **Compact Phase**: Two-part process — (1) update all references to moved objects, then (2) move (copy) the objects.
  - When to use: Plan phase decided to compact, or compaction was explicitly requested.
  - How (SOH): (a) Get a new ephemeral segment if Plan showed gen0/1 won't fit (not for regions); (b) **Relocate references** — rewrite every address of soon-to-move objects using bricks + plug trees; (c) **Compact objects** — copy plug by plug via relocation offsets, restore pre-/post-plug info; (d) Fix generation boundaries; (e) Delete/decommit unneeded segments; (f) Create free-list items before pinned plugs; (g) Age roots.
  - Why order matters: References are updated BEFORE moving, since final addresses are already known from Plan. Source: `relocate_phase` then `compact_phase` (→ `compact_in_brick` → `compact_plug`).

## Key Concepts
- **Sweep**: Transform gaps into free-list items in place; no objects moved.
- **Compact**: Move surviving plugs to eliminate gaps + rewrite all references to them.
- **Relocation**: Translating a current object address to its new (post-move) address via bricks and the plug tree (`gc_heap::relocate_address`).
- **Sliding compaction**: Always copy lower addresses first in small enough pieces that a plug's destination never overwrites its own not-yet-copied source.
- **memcopy (unrolled)**: The pointer-by-pointer copy loop, unrolled to 4 pointer-sized regions at a time, compiled to a handful of `mov` instructions.
- **Pre-/post-plug restore**: Object endings overwritten by plug bookkeeping are restored from the pinned plug queue entry.
- **Typical GC combination**: Sweep the LOH first, then compact the SOH (order matters).
- **LOH fragmentation**: Live large objects (mostly arrays/strings) interleaved with free holes that are poorly reused; LOH is not auto-compacted.

## Mental Models
- **Think of Sweep/Compact as "consumers" not "deciders."** All intelligence lives in the Plan phase; these phases just execute the plan. That's why they're short in the book but expensive at runtime.
- **Use the copy-in-small-pieces model, not the Lego-brick model.** Objects are just contiguous memory; copying lowest-address-first in ≥1-pointer chunks makes self-overlap impossible — no temp buffer needed (which would double memory traffic).
- **The more reference fields your objects hold, the more Relocate work you create.** On a hot path with complex data structures, consider avoiding direct object references.
- **UOH sweep before SOH compaction** means only survivors remain in LOH/POH during full-GC relocation, so they scan efficiently one-by-one without brick support.

## Anti-patterns
- **Using an intermediate buffer to copy plugs**: Doubles memory traffic (copy twice) — unacceptable; CLR uses sliding in-place memcopy instead.
- **Slightly-growing large allocations (each frame > previous)**: Creates LOH free-item holes with low chance of reuse → maximal fragmentation.
- **Excessive explicit string interning (.NET Framework)**: Intern tables land in LOH and cause fragmentation (not an issue on modern .NET — POH stores them).
- **Reflexively forcing LOH compaction**: Blocking, slow (100–200 ms for a few hundred MB survivors; >1 s for several GB); prefer array/object pooling if you own the code.

## Code Examples
```cpp
void memcopy (uint8_t* dmem, uint8_t* smem, size_t size) {
    const size_t sz4ptr = sizeof(PTR_PTR)*4;
    // ...
    // copy in groups of four pointer sized things at a time
    if (size >= sz4ptr) {
        do {
            ((PTR_PTR)dmem)[0] = ((PTR_PTR)smem)[0];
            ((PTR_PTR)dmem)[1] = ((PTR_PTR)smem)[1];
            ((PTR_PTR)dmem)[2] = ((PTR_PTR)smem)[2];
            ((PTR_PTR)dmem)[3] = ((PTR_PTR)smem)[3];
            dmem += sz4ptr; smem += sz4ptr;
        } while ((size -= sz4ptr) >= sz4ptr);
    }
    // copy remaining 16 and/or 8 bytes
}
```
- **What it demonstrates**: Sliding compaction's core — an unrolled pointer-by-pointer copy (compiles to a few `mov` instructions) that avoids self-overwrite without a temp buffer.

```csharp
if (GC.GetTotalMemory() > LOH_COMPACTION_THRESHOLD) {
    GCSettings.LargeObjectHeapCompactionMode = GCLargeObjectHeapCompactionMode.CompactOnce;
    GC.Collect();
}
```
- **What it demonstrates**: Forcing a one-time LOH compaction during the next *blocking* GC (background GC ignores this setting, hence the explicit `GC.Collect()`).

## Reference Tables

Relocate References — memory areas scanned & updated during SOH compaction:

| Area scanned | Notes |
|---|---|
| References on the stack | All managed threads' stack frames |
| Cross-generational remembered set (cards) | Non-Full GC only; SOH + LOH cross-gen refs |
| Objects on SOH and UOH | SOH via bricks + plug trees; UOH one-by-one (swept first) |
| Pre-/post-plugs | Damaged endings held in pinned plug queue |
| Ready-to-finalize queue objects | Finalization queue addresses |
| Handle tables | Handles update their pointers |

Scenario 10-1 — Expected vs Observed LOH size (Table 10-1):

|   # Objects |   Expected [MB] |   Observed [MB] |
|-------------|-----------------|-----------------|
|       1,000 |     102,400,000 |     152,769,104 |
|       2,000 |     204,800,000 |     324,972,048 |
|       3,000 |     307,200,000 |     463,287,752 |
|       4,000 |     409,600,000 |     686,795,056 |

GCAllocationTick `AllocationKind`: 0 = SOH, 1 = LOH, 2 = POH (event emitted per 100 KB, per heap).

## Worked Example
**Scenario 10-1 — Diagnosing LOH fragmentation.** A batch image processor stores 100 KB `byte[]` blocks plus > 85,000-byte input/output frames — all land in LOH. Memory usage runs ~50% above expectation.

1. **Confirm fragmentation (PerfView, "GC Collect Only")**: GCStats "GC Events by Time" shows `LOH Frag %` ≈ 48% — nearly half the space wasted.
2. **Find what's dying (PerfView, ".NET" option)**: Open *Gen 2 Object Deaths (Coarse Sampling) Stacks* (includes LOH). Many `System.Byte[]` dying. Select the type → *Goto Item in Callers* → allocation stacks reveal two sources: `Reader.ReadBytes()` (one dying array) and `Processor.Process` (thousands). Sampling is driven by the `GCAllocationTick` event (per 100 KB).
3. **Cross-check with WinDbg + SOS**:
   - `!heapstat -inclUnrooted` → LOH free space 22% + unrooted-but-uncollected 25% = ~47% expected fragmentation.
   - `!eeheap -gc` → many 128 MB LOH segments (64-bit Workstation GC); higher address = newer data.
   - `!dumpheap <oldest segment>` → 78,974-byte Free holes interleaved with 102,424-byte live arrays; `!gcroot` → rooted by `largeBlocks` (`List<byte[]>`) in `Main`.
   - `!dumpheap <newest segment>` → same pattern but with not-yet-collected objects (99,6xx-byte arrays) between the holes; `!gcroot` traces them to `DataFrame` in `Program.Main` and `Processor.Process` — the fragmentation culprits.
4. **Fixes**: Explicit `CompactOnce` LOH compaction (blocking, slow — pause scales linearly with survivor size) *or* enable `GCConservativeMode` (Ch 11) *or*, preferably if you own the code, use **ArrayPool / object pooling** (Ch 6). Note: hard memory limits (e.g. dockerized app) can make LOH compaction automatic (Ch 7).

## Key Takeaways
1. Sweep is fast (local modifications, little memory traffic); Compact is where most time is spent (copying plugs across the heap = heavy memory traffic).
2. The Plan phase owns the decision; Sweep/Compact only execute — so optimizing them means optimizing what Plan has to move.
3. Compact updates references *before* moving objects, because final addresses are already known.
4. Sliding compaction copies lowest addresses first in ≥1-pointer chunks, avoiding both self-overwrite and any temp buffer.
5. LOH is swept (not compacted) by default → fragmentation from interleaved large arrays/strings; compaction must be requested explicitly and is slow.
6. Rules 17–22 (chapter-end): watch runtime suspensions (< 1 ms), avoid mid-life crisis, avoid gen2/LOH fragmentation, avoid explicit GC, avoid memory leaks, use pinning carefully (prefer POH; short `fixed` scopes or long-lived reused pinned buffers).

## Connects To
- **Ch 9 (Plan phase)**: Supplies all offsets, plug trees, and the should_compact decision consumed here.
- **Ch 6**: Free-list items; ArrayPool / object pooling as the real fix for fragmentation.
- **Ch 5**: Card table / cross-generational remembered set relocated during Compact.
- **Ch 7**: Ephemeral segment expansion, explicit GC triggers, auto LOH compaction under hard memory limits.
- **Ch 11**: `GCConservativeMode` alternative for LOH fragmentation.
- **Ch 12**: Finalization queue relocation; IDisposable is *not* GC-triggering.
- **CLR internals**: `plan_phase`, `relocate_phase`, `compact_phase`, `relocate_address`, `make_free_lists`, `GCSettings.LargeObjectHeapCompactionMode`.
