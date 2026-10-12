# Chapter 9: Garbage Collection - Plan Phase

## Core Idea
The **Plan phase** simulates a compaction *without actually moving objects*, producing precise information (plug relocation offsets, gap sizes, compaction efficiency) that is then consumed directly by either the Compact or Sweep phase. It is the "main horsepower" of the GC — the paradox it resolves is that to accurately predict the result of a compaction, you effectively have to perform it.

## Frameworks Introduced
- **Plugs and Gaps grouping**: During an object-by-object scan of the condemned + younger generations, marked and unmarked objects are grouped into interleaving runs.
  - **Plug**: an adjacent group of marked (reachable) objects.
  - **Gap**: an adjacent group of not-marked (unreachable) objects.
  - When to use: SOH (gen 0/1/2) planning; how the GC computes both sweep and compact results at once.
  - How: walk the heap treating it like a linked list (advance pointer by object size from the method table); free space is filled with a dummy `Free` object (a fake byte-array) so the walker can "jump" over it. For each pair, record the **gap size/location** (future free-list items if Sweep) and the **plug relocation offset/location** (where the plug moves if Compact).
  - Why it works: the most frequent collections (gen0/gen1) are compacting, so the simulated results are rarely discarded.
- **Plug info stored in-heap**: Instead of a separate memory area, plug/gap data is written into the *end of the preceding gap* (safe — it holds only dead objects). This improves CPU cache locality and avoids extra allocations.
  - Plug info = **24 bytes** on 64-bit, **12 bytes** on 32-bit: contains gap size, relocation offset (2 bits are part of it), and left/right child offsets.
  - This is the core reason even an empty object must be **24 bytes** (64-bit): a gap before a plug holds ≥1 object, guaranteeing room for the plug info.
- **Binary plug tree (BST) + Brick table**: to answer "what is the new address of object at X?" efficiently.
  - How: each plug info's left/right offsets form a balanced BST (left children = lower addresses, right = higher). Tree roots are indexed by a **brick table** covering fixed address ranges.
- **decide_on_compacting**: after planning, compare planned fragmentation against per-generation thresholds to choose Compact vs Sweep.

## Key Concepts
- **Free object**: a fake 1-byte-element array with a dedicated MT that fills free space so the heap stays walkable.
- **Relocation offset**: amount subtracted from an object's address X to get its post-compaction address; accumulated by the internal bump-pointer allocator over "virtual space."
- **Brick**: a fixed address range holding one plug-tree root — **2,048 B** (32-bit) / **4,096 B** (64-bit).
- **Brick table entry** (16-bit): `0` = no plugs; `>0` = plug-tree root offset (+1); `<0` = continuation, jump back N bricks (plug spans multiple bricks).
- **Pinned plug**: a group of pinned (thus marked) objects; relocation offset forced to 0 — the allocator "allocates" it exactly where it is.
- **Pre-plug**: cut-off ending of a normal object that precedes a pinned plug, overwritten to store pinned plug info and saved in the pinned plug queue.
- **Post-plug**: object ending saved when a pinned plug is extended into a following marked object, then a normal plug begins after it.
- **Pinned plug queue**: holds extra pinned-plug data that won't fit in standard plug info; reuses `mark_stack_array` (with `mark_stack_tos`/`bos`).
- **Demotion**: an object ends up in a *lower* generation than expected (opposite of promotion), an optimization to reuse gaps left by pinning.

## Mental Models
- Think of the heap during Plan as **a giant linked list** navigated by object sizes — Free objects are the "nodes" bridging dead space.
- Think of the internal allocator as building a **virtual compacted heap** in parallel: it bumps a pointer as if moving each plug, but only records the offset instead of copying.
- Use **plug extension** intuition: pinning is contagious — the GC will pin one *extra* normal object to keep plug handling generic, accepting a little wasted memory to avoid special cases.

## Anti-patterns
- **Excessive pinning**: forces zero relocation offsets, pre/post-plug copying (extra memory traffic), and can extend an unmovable region — the more pinned objects, the higher overhead and fragmentation. Avoidance covered in Ch 13.
- **Analyzing a dump captured mid-Plan phase**: heap is not walkable; SOS/`!dumpheap`/`!verifyheap` report invalid structures or false consistency errors (see Scenario 9-1).

## Code Examples
The guard that flags an in-progress Plan phase (only place in .NET where this protection exists):
```cpp
GCScan::GcRuntimeStructuresValid(FALSE);
plan_phase(n);
GCScan::GcRuntimeStructuresValid(TRUE);
```
- **What it demonstrates**: why a dump taken during `plan_phase` yields "GC data structures are not in a valid state for traversal."

Local-variable pinning source found while diagnosing (decompiled `System.Data.SqlServerCe`):
```csharp
fixed (IntPtr* ptr = this.accessor.DbBinding) { /* ... */ }
```
- **What it demonstrates**: `fixed` implicitly creates a short-lived local pinned variable — a common pinning root.

## Reference Tables

**Table 9-1. Fragmentation Thresholds for Generations** (both must be exceeded to compact):

|      | Fragmentation Size | Fragmentation Ratio |
|------|--------------------|---------------------|
| Gen0 | 40,000             | 50%                 |
| Gen1 | 80,000             | 50%                 |
| Gen2 | 200,000            | 25%                 |

Backing fields: `fragmentation_limit` (size) and `fragmentation_burden_limit` (ratio), from static generation data (Tables 7-1/7-2).

**Pinned-plug placement scenarios (SOH):**

| Layout | Handling |
|--------|----------|
| Pinned plug after a gap | Store plug info in gap end as usual; reloc offset = 0 |
| Pinned plug after normal plug | Overwrite the preceding object; save its end as **pre-plug** |
| Pinned plug before normal plug | Merge the following object *into* the pinned plug (extend by one object) |
| Pinned plug inside a marked block | Save both **pre-plug** and **post-plug**; three plugs created |

**Key .NET source methods:**

| Method | Role |
|--------|------|
| `gc_heap::plan_phase` | Main Plan phase |
| `allocate_in_condemned_generations` / `allocate_in_older_generations` | Compute new plug location |
| `gc_heap::plan_loh` | LOH planning |
| `gc_heap::decide_on_compacting` | Compact-vs-Sweep decision |
| `gc_heap::record_interesting_data_point` | Pinning stats (`!DumpGCData`) |

## Worked Example
**Diagnosing pinning (Scenario 9-2).** A high `.NET CLR Memory\# of Pinned Objects` counter (Framework only; no equivalent for .NET Core) prompts investigation. Two sources exist: **local pinned variables** (`fixed`, method-scoped, only partially visible in a dump) and **pinned handles** (`GCHandle.Alloc`, live for app lifetime, easily dumped).

Steps taken:
1. Record an ETW session in PerfView with the `.NET` checkbox. Open **GCStats** → the **Pinned Obj** column confirms pinned counts per GC (works for .NET Core too, where counters are absent).
2. One `PinObjectAtGCTime` ETW event is emitted per pinned object during the **Mark phase**; inspect its `TypeName`. (Note: stack traces on these events point into GC code, not the pinning site — useless even with `@StacksEnabled=true`.)
3. Use PerfView's **Pinning At GC Time Stacks** (Advanced group). "By Name" groups into a `NonGen2` source; "Goto Item in Callers" (F10) reveals `StackPinned` types — here `SqlCeCommand`, `SqlCeConnection`, `MEDBBINDING[]` from `System.Data.SqlServerCe`.
4. For handle pinning, run `!GCHandles` in WinDbg on a dump — lists pinned `System.Byte[]`/`System.Object[]` (intern pool, statics, Kestrel buffers, etc.). No WinDbg extension lists stack-based pinning.

Conclusion: `PinObjectAtGCTime` covers *both* sources; SOS lists *only* handle pinning. Result in this example: pinning came mainly from local `fixed` variables.

## Key Takeaways
1. The Plan phase produces one dataset that serves both Sweep (gap locations → free-list) and Compact (plug relocation offsets), so its work is rarely wasted.
2. The 24-byte minimum object size exists specifically to guarantee room to store 24-byte plug info in the gap preceding each plug.
3. Address translation "new address = X − relocation offset" is made fast via a per-brick balanced BST of plugs, indexed by a 16-bit brick table.
4. Pinning is the source of nearly all Plan-phase complexity: zero reloc offsets, pre/post-plugs (which overwrite objects — safe only because all threads are suspended), and single-object plug extension.
5. **Demotion** reuses gaps left before pinned plugs, so a pinned object may stay in gen0 or drop from gen2→1/0 instead of being promoted — an optimization with no useful diagnostic surface.
6. LOH planning is far simpler: each object is its own plug, 32-byte padding stores plug info, no brick table, no generation boundaries, no demotion — and it's almost always Sweep anyway.
7. Compaction is chosen when fragmentation exceeds *both* a size and ratio threshold (or is forced: pre-OOM, explicit `GC.Collect`, ephemeral/region exhaustion, high memory load).

## Connects To
- **Ch 6**: Free-List Allocation — the dummy `Free` object mechanism reused for heap walking.
- **Ch 7**: static generation data (Tables 7-1/7-2), regions vs segments, gen2→ephemeral segment conversion, region promotion (Figures 7-7/7-8).
- **Ch 8**: Mark phase — supplies the marked/pinned bits the Plan phase consumes.
- **Ch 10**: Compact and Sweep phases — the direct consumers of Plan-phase data.
- **Ch 11**: `ConserveMemory` triggering LOH compaction.
- **Ch 13**: techniques to avoid excessive pinning.
- **CLR internals**: `plan_phase`, brick table, BST plug tree, `mark_stack_array`, SIP (swept-in-plan) and dynamic promotion under experimental `DOTNET_GCEnableSpecialRegions=1` (regions-only).
