# Chapter 1: Basic Concepts

## Core Idea
Even fully automatic memory management can cause real problems (memory leaks, cost, latency), so a professional must understand the theoretical foundations — stack, heap, pointers, and the Mutator/Allocator/Collector model — that underlie .NET's precise tracing garbage collector.

## Frameworks Introduced
- **Mutator / Allocator / Collector triad** (Dijkstra's terminology): the three cooperating abstractions in any automatic memory system.
  - When to use: as the vocabulary for reasoning about *any* GC design and where overhead lands ("overhead on Mutator").
  - How: Mutator = entity running app code (usually a thread) exposing `New(amount)`, `Write(address,value)`, `Read(address)`; Allocator = manages dynamic memory via `Allocate(amount)` / `Deallocate(address)` (Deallocate is internal, never exposed to Mutator under auto-GC); Collector = runs reclamation code. GC = "a simulation of a computer with an infinite amount of memory."
  - Why it works: the Mutator's three operations are the injection points where a GC plugs in *barriers* (read/write barrier) to synchronize with the Collector.
- **Reachability as a proxy for liveness**: since true liveness (will an object be used again?) is undecidable, the Collector approximates it.
  - How: an object is *reachable* if a chain of references leads to it from a **root**. Roots = local variables & subroutine arguments (stack/registers), statically allocated objects (heap), and internal Collector structures. Not reachable ⇒ dead ⇒ reclaimable.
  - Failure mode: reachable ≠ live. An object kept in a graph but never accessed stays reachable forever — "this misalignment between liveness and reachability is the cause of most managed memory leaks."
- **Reference Counting**: each object holds a counter; incremented on assignment to a variable/field, decremented off the old referent; counter → 0 means deallocate.
  - When to use: environments without runtime support (implementable as a library, e.g. C++ smart pointers, Swift ARC, Rust).
  - Failure mode: cannot reclaim **circular references** (counters never reach zero); big overhead on the very-common `Mutator.Write`; needs synchronization when multithreaded.
- **Tracking (Tracing) Garbage Collector**: uses global object-graph knowledge. Two steps: **Mark** (find reachability from roots) then **Collect** (reclaim unreachable). .NET extends this to Mark-Plan-Sweep-Compact. This is what "Garbage Collector" almost always means.

## Key Concepts
- **Static allocation**: size and location known at compile time; global/static variables live for whole program lifetime.
- **Stack**: LIFO region; each subroutine call pushes an **activation frame** (a.k.a. stack frame) holding arguments, return address, and local variables. Grows downward; overflow ⇒ `StackOverflowException`.
- **Heap** (a.k.a. free store): region for **dynamic memory allocation** — size/location unknown at compile time, so referenced by pointer.
- **Pointer**: variable storing a memory address; size tied to word length (32/64-bit).
- **Heap fragmentation**: enough total free space exists but no single contiguous block large enough for a new object.
- **Register machine vs stack machine**: register machines (x86/x64/ARM) operate on registers via load/store; stack machines operate on an **evaluation/expression stack**. .NET and the JVM are (impure) stack machines mapped onto register hardware — chosen for platform independence and dense code.
- **Barrier**: augmentation of a Read or Write operation used to synchronize the Mutator with the Collector.
- **Conservative vs Precise Collector**: conservative *guesses* what is a pointer by scanning stack/statics/registers; precise has full type/layout info from the compiler/runtime. .NET is **Precise**.
- **Interior pointer**: a pointer into the middle of an object (not just its start).

## Mental Models
- Think of the **stack as the well-ordered clerk** and the **heap as the messy "free store"** — the LIFO stack frees by moving the stack pointer; the heap is a black box you ask for memory with different allocation strategies.
- Use the **manual-gear car metaphor** for manual vs automatic memory: manual (C/C++ `malloc`/`free`) gives full control but distracts from business goals with "ceremony code"; automatic GC lets you focus on the destination.
- Think of GC as **simulating infinite memory**: the Mutator can only ask for more, never explicitly free — a "Null/Zero GC" that never frees is valid on an infinite (or short-lived) machine.
- Use **Mechanical Sympathy** (Jackie Stewart / Martin Thompson): you don't need to be an engine builder to race, but you must "feel the car" — likewise, understand the runtime beneath your framework.

## Anti-patterns
- **Forgetting `free`**: memory leak; **double-free** and **dangling pointers** (not NULLing after free) cause undefined behavior / access violations.
- **Buffer overflow**: allocating too little; writing past bounds ⇒ segfault/access violation, data corruption, security holes.
- **Relying on reference counting with cycles**: double-linked lists etc. never drop to zero and leak unless cycles are prevented at the language level.
- **Comparing GCs in isolation**: GCs are tightly coupled to their runtime; "every comparison is from the ground up very ambiguous."

## Code Examples
```c
#include <stdio.h>
void printReport(int* data) { printf("Report: %d\n", *data); }
int main(void) {
    int* ptr;
    ptr = (int*)malloc(sizeof(int));
    if (ptr == NULL) { printf("ERROR: Out of memory\n"); return 1; }
    *ptr = 25;
    printReport(ptr);
    free(ptr);
    ptr = NULL;
    return 0;
}
```
- **What it demonstrates**: the full "ceremony" of manual memory management — allocate, cast, null-check, dereference, free, NULL-out — for a one-line business goal.

```
Mutator.New(amount)          { obj = Allocator.Allocate(amount); obj.counter = 0; return obj; }
Mutator.Write(address, value){ if (address != NULL) ReferenceCountingCollector.DecreaseCounter(address);
                               *address = value;
                               if (value != NULL) value.counter++; }
ReferenceCountingCollector.DecreaseCounter(address) {
    *address.counter--;
    if (*address.counter == 0) Allocator.Deallocate(address); }
```
- **What it demonstrates**: reference counting adds heavy overhead to the ultra-common `Write` (assignment) path.

## Reference Tables

Stack vs Heap (Table 1-1, condensed):

| Property | The Stack | The Heap |
|----------|-----------|----------|
| Lifetime | Function scope (push on entry, pop on exit) | Explicit (allocate + optional free) |
| Scope | Local (per thread) | Global (anyone with a pointer) |
| Access | Local vars, function arguments | Pointer |
| Access time | Fast (cached) | Slower (may even hit disk) |
| Allocation | Move stack pointer | Different strategies |
| Alloc time | Very fast | Slower (depends on strategy) |
| Capacity | Limited (few MB/thread) | Virtually unlimited; ≤4 GB on 32-bit |
| Variable size | No | Yes (reallocate) |
| Fragmentation | No | Likely |
| Main risks | Stack overflow | Memory leak, fragmentation |

Collect-phase strategies:

| Approach | Mechanism | Trade-off |
|----------|-----------|-----------|
| **Sweep** | Mark dead objects as free space (free-list; best-fit vs first-fit) | Fast; leads to fragmentation |
| **Copying Compacting** | Copy all live objects to a new region | High memory traffic + 2× memory overhead |
| **In-Place Compacting** | Slide live objects together to remove gaps | No double memory; tricky to avoid overwriting. **.NET uses this** (Ch 9) |

## Worked Example
**Mark phase graph traversal (Figure 1-13), depth-first, three states** — white = not visited, light gray = queued, dark gray = visited/reachable:
1. All objects white.
2. Root object **A** queued.
3. A has fields → **B** and **D**; both queued, A marked reachable.
4. Visit **B**: no outgoing refs → marked reachable.
5. Visit **D**: single ref → **E** queued; D marked reachable.
6. Visit **E**: ref → **G** queued; E marked reachable.
7. Visit **G**: no refs, marked reachable. Queue empty ⇒ **C and F never marked = unreachable (dead)**, ready to reclaim.

Marking also solves cycles: revisiting an already-marked object is inspected only once. In non-concurrent GCs all Mutators are stopped ("stop the world") during Mark so the graph stays consistent; concurrent variants (CMS/G1 in JVM, and .NET — Ch 11) mark alongside running Mutators.

## Key Takeaways
1. Care about memory even under automatic management — it drives cloud cost (Azure Functions bill in GB-seconds), server count, and long-run leaks.
2. The stack frees for free (move the pointer); the heap needs an allocation strategy and risks fragmentation.
3. Automatic GC removes explicit `Deallocate` from the programmer and approximates liveness via **reachability from roots**.
4. Reference counting is deterministic and needs no runtime support, but pays per-assignment overhead and cannot handle cycles.
5. Tracing GC (Mark + Collect) uses global reachability, handles cycles, imposes little Mutator overhead — but is nondeterministic and may "stop the world."
6. .NET = **Precise, tracing, in-place compacting** collector; know these terms before later chapters.
7. Rule 1 — **Educate Yourself**: cultivate Mechanical Sympathy for the runtime beneath your code.

## Connects To
- **Ch 2**: from theory to low-level hardware/memory design (RAM, CPU cache, access patterns).
- **Ch 4**: .NET's Intermediate Language (IL) as an (impure) stack machine; sequential vs free-list allocators; escape analysis for true liveness; JIT.
- **Ch 5**: how the heap is partitioned into smaller parts.
- **Ch 9–11**: in-place compaction data structures; precise GC internals; concurrent marking; background GC.
- **CLR / external**: C++ RAII & smart pointers (`unique_ptr`/`shared_ptr`), Swift ARC, Rust ownership, Boehm-Demers-Weiser conservative GC, Mono SGen.
