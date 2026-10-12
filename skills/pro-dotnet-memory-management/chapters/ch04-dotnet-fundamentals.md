# Chapter 4: .NET Fundamentals

## Core Idea
The .NET runtime (CLR) turns CIL into machine code via the JIT and manages many distinct memory regions; understanding value vs. reference type *semantics* (not the "stack vs. heap" mantra), strings, boxing, and static storage is the foundation for all later GC work.

## Frameworks Introduced
- **CLR responsibility split — Execution Engine (VES) vs. Garbage Collector**: EE handles JIT, type system, exception handling, P/Invoke; GC handles allocation and reclaiming. ECMA-335 names EE the "Virtual Execution System."
- **The memory-diagnosis scenario pattern**: the book's recurring "Scenario N" method for diagnosing a leak.
  - When to use: user reports growing memory / OutOfMemory.
  - How: (1) monitor perf counters (Working Set - Private, Private Bytes, Virtual Bytes, .NET CLR Memory\# Total committed Bytes) over time; (2) identify *which* region grows (managed heap vs. native Heap vs. Virtual/Unusable vs. Loader Heap) with VMMap / dotnet-counters; (3) pick the matching ETW provider in PerfView (OS Heap for malloc/new, VirtAlloc for VirtualAlloc, Loader keyword for assembly loads, .NET Alloc for managed strings); (4) expand highest Inc% call stack to root cause.
  - Why it works: each memory region maps to a distinct root cause, so the growing region tells you which tool to reach for.
- **Escape Analysis ("object stack allocation")**: JIT may allocate a reference type on the stack if it proves the reference never escapes the method and isn't shared across threads. Partial in .NET 8, **disabled by default** — enable with `DOTNET_JitObjectStackAllocation=1`. Blocked by: arrays, strings, boxed structs, class >8 KB, allocation in a loop, no method inlining (no interprocedural analysis).

## Key Concepts
- **CIL (Common Intermediate Language)**: stack-machine bytecode all .NET languages compile to; JIT converts it to native code per platform.
- **Assembly / module / AppDomain**: assembly = deployment unit of CIL (≈ one DLL/EXE = one module); AppDomain = runtime isolation boundary. .NET Core dropped AppDomains — use `AssemblyLoadContext` instead.
- **Collectible assembly**: dynamic assembly unloadable without unloading the AppDomain, via collectible `AssemblyLoadContext` (since .NET Core 3.0). Uses **cooperative unloading** — unloads only after no threads have its methods on-stack and no non-weak references remain.
- **MethodTable (TypeHandle)**: per-type structure holding GCInfo, Flags, basic instance size, EEClass reference, method descriptions, static field data. Object's MethodTable pointer is how EE and GC cooperate.
- **Value type vs. reference type**: value = instance directly contains all its data (self-contained, pass-by-value, no identity); reference = instance holds a *reference* to data elsewhere (shared, pass-by-reference, identity = location). ECMA-335 mentions neither stack nor heap.
- **Boxing**: converting a value type to a reference type — (1) allocate boxed-type object on heap, (2) bitwise-copy the value in. Adds allocation + GC pressure.
- **String interning**: dedup mechanism keeping one copy of equal strings; by default applies only to *string literals*. Interned strings live forever (never collected).
- **Loader Heap**: conceptual grouping of High/Low Frequency + Stub + Virtual Call Stub heaps per AppDomain; stores type metadata. Not a real region — types loaded here aren't freed until AppDomain unloads.
- **NonGC Heap (Frozen heap)**: holds read-only objects (string literals, System.Type, static readonly simple types); GC never manages their lifetime.

## Mental Models
- **"Value on stack / reference on heap" is a leaky abstraction, not a rule.** Think: *lifetime + sharing* decide storage. A local struct → stack or register; a struct field of a heap object → heap; a struct on the evaluation stack → CPU register.
- **Think of a reference as a pointer with runtime safety.** Copying a reference copies the address, not the data.
- **Use a struct when** data is small, short-lived, local, and copied rarely (or passed by `ref`) — for data locality and zero-allocation. **Use a class when** you need identity, sharing, or inheritance.
- **Interning trades allocation for immortality.** Only worth it for many duplicated strings that live long; harmful for temporary bursts.

## Anti-patterns
- **`XmlSerializer` with the wrong constructor**: any constructor other than `XmlSerializer(Type)` / `XmlSerializer(Type, String)` regenerates assemblies that are never unloaded → assembly-count memory leak (Scenario 4-4).
- **Never unregistering events across an `AssemblyLoadContext` boundary**: a plugin subscribing to a host event (`context.OnCommandExecuted += ...`) keeps the collectible assembly reachable → never unloads (Scenario 4-5).
- **Inefficient `VirtualAlloc` of a single 4 KB page**: 64 KB allocation granularity wastes 60 KB per call as "Unusable" virtual memory (Scenario 4-3).
- **Naive string concatenation with `+=`**: each `+=` compiles to `String.Concat`, creating hidden temporary strings. Use `StringBuilder`, `string.Format`, or interpolation.
- **Interning temporary strings**: makes soon-to-be-collected strings immortal, increasing memory instead of reducing it.

## Code Examples
```
Samples.ExampleClass.Main(Int32)   ; struct version (Listing 4-11)
mov eax, edx
ret
```
- **What it demonstrates**: In Release mode RyuJIT x64 optimizes an entire local-struct pass-by-value + method call down to a single `mov` — no stack, no copy, no struct at all. The class counterpart (Listing 4-19) instead calls `JIT_TrialAllocSFastMP_InlineGetThread` (heap allocation).

```
int i = 123;
object o = i;   // implicit boxing → CIL: box System.Int32
```
- **What it demonstrates**: implicit boxing allocates a `System.Int32` on the heap and copies the value in.

## Reference Tables

Object memory layout (per heap object):

| Part | 32-bit | 64-bit |
|------|--------|--------|
| Object header (sync block) | 4 B | 8 B (4 used + 4 alignment pad) |
| MethodTable reference | 4 B | 8 B |
| Data placeholder (min 1 pointer-wide field) | 4 B | 8 B |
| **Minimum object size** | **12 B** | **24 B** |

Struct vs. class micro-benchmark (Table 4-1, .NET 8):

| Method | Mean | Allocated |
|--------|------|-----------|
| ConsumeStruct | 0.0327 ns | 0 B |
| ConsumeClass | 4.3562 ns | 32 B |

Array data-locality benchmark (Table 4-2, 1M elements):

| Method | Mean | Allocated |
|--------|------|-----------|
| StructArrayAccess | 491.2 us | 0 B |
| ClassArrayAccess | 2247.6 us | 0 B |

PerfView ETW provider by symptom:

| Growing region | Tool/provider | Root cause found |
|----------------|---------------|------------------|
| Native Heap (Private Data) | OS Heap Exe/Process | `malloc`/`new` |
| Virtual + Unusable | VirtAlloc | inefficient `VirtualAlloc` |
| Loader / assembly count | `Microsoft-Windows-DotNETRuntime:LoaderKeyword:Always:@StacksEnabled=true` | dynamic assembly creation |
| Managed strings | .NET Alloc (or dotnet-dstrings) | string duplication |

## Worked Example
**Scenario 4-4 — managed memory grows with assembly count.** Symptom: all sizes grow, crash on OOM, but `.NET CLR Memory\# Total committed Bytes` (managed heap) is *stable*. VMMap shows dozens of "Domain 1 / Low Frequency / High Frequency Heap" regions — GC region grows slowly, Loader Heap explodes. Confirm with counters `Bytes in Loader Heap`, `Current Classes Loaded`, `Current Assemblies` (all rising) and dotnet-counters `Number of Assemblies Loaded` (75,000+) / `Number of Methods Jitted` (500,000+). PerfView Loader events → open `AssemblyLoad` stack → group out `clr`/`mscoree`, ungroup own module → stack points at an `XmlSerializer` constructor in `XmlSerializerLeak.Run()`. Fix: use `XmlSerializer(Type)` so generated assemblies are reused, or cache them in a Hashtable.

## Key Takeaways
1. Every method ends up JITted to native code; there is one runtime instance per process, and .NET is *not* a virtual machine — it reuses OS stack/heap/threads.
2. Diagnose leaks by *region*: managed heap, native Heap (malloc/new), Virtual/Unusable, or Loader Heap — each has its own counter, VMMap view, and PerfView provider.
3. Value vs. reference is about lifetime, sharing, and identity — not stack vs. heap. The JIT decides actual storage (stack, heap, or register).
4. Structs win on allocation avoidance and data locality (arrays of structs are contiguous; arrays of classes are contiguous *references* to scattered objects) but risk hidden boxing and copy cost — pass by `ref` for large structs.
5. Minimum heap object is 12 B (32-bit) / 24 B (64-bit); a struct's raw size has no such overhead.
6. Strings are immutable reference types; `+=` hides `String.Concat` allocations — use StringBuilder. Interning helps only for long-lived, highly-duplicated strings.
7. Static reference-type data lives on the GC heap referenced by an internal statics table (in POH via PinnedHeapHandleTable) → promoted to gen2 forever; static reference-free structs live boxed in the NonGC heap for fastest access (since .NET 7).

## Connects To
- **Ch 1**: pointers, references, the abstract stack machine.
- **Ch 2**: virtual memory regions, allocation granularity (64 KB), cache lines / data locality, Law of Leaky Abstractions.
- **Ch 3**: tools — WinDbg/SOS, VMMap, PerfView, dotnet-counters, dnSpy.
- **Ch 5**: SOH/LOH/POH generations, NonGC (NGCH) heap, gen0 budget.
- **Ch 6**: hidden allocations, string performance, "Avoid Hidden Allocation" rule.
- **Ch 13–14**: managed pointers, `ref`/`in`/`out`, `Span<T>`, inlined arrays, advanced pass-by-reference optimization.
- **ECMA-335 / ISO/IEC 23271 (CLI)**, Microsoft x64 calling convention (RCX, RDX, R8, R9; RAX return).
- **Rules introduced**: Rule 6 Measure Your Program, Rule 7 Do Not Assume There Is (No) Memory Leak, Rule 8 Consider Using Struct, Rule 9 Consider Using String Interning, Rule 10 Avoid Boxing.
