# Glossary

**Allocation budget** — per-generation limit (a.k.a. `desired_allocation`) on bytes allocated before that generation's next GC; derived from survival rate and the mechanism deciding when a GC fires and which generation is condemned (Ch 7).

**Allocation context** — a per-thread span of pre-zeroed memory between `alloc_ptr` and `alloc_limit` used for lock-free bump-pointer allocation (TLAB) (Ch 6).

**Allocation quantum** — amount (default 8 kB SOH) by which an allocation context grows on the slow path (Ch 6).

**AoS → SoA** — Array-of-Structures to Structure-of-Arrays transformation storing one array per field for cache-friendly sequential access (Ch 14).

**Background GC (BGC)** — modern name for concurrent GC; marks/sweeps while user threads run using a mark array, write barriers/write watch, and revisiting, accepting floating garbage; never compacts (Ch 11).

**Bump pointer allocation** — sequential allocation fast path that moves `alloc_ptr` forward by the object size; a few assembly instructions (Ch 6).

**Boxing** — converting a value type to a reference type by allocating a boxed object on the heap and bitwise-copying the value in (Ch 4).

**Brick / brick table** — a fixed address range (4,096 B on 64-bit / 2,048 B on 32-bit) holding one plug-tree root, indexed by a 16-bit brick table to translate an object's address to its post-compaction address (Ch 9).

**Card table** — bitmap (1 bit = 256 B on 64-bit / 128 B on 32-bit) marking heap regions that contain older-to-younger cross-generational references as "dirty" (Ch 5).

**Card bundles** — higher-level bitmap (1 bit = 256 KB) for fast scanning of sparse card tables (Ch 5).

**Cache line** — fixed 64-byte block; the atomic unit of transfer between RAM and CPU cache (Ch 2).

**CIL (Common Intermediate Language)** — stack-machine bytecode all .NET languages compile to, JITted to native code per platform (Ch 4).

**ClrMD** — `Microsoft.Diagnostics.Runtime`, a managed API using the DAC to introspect live processes/dumps, SOS-equivalent from C# (Ch 15).

**Compact** — GC phase that moves surviving plugs together to eliminate gaps and rewrites all references to them (Ch 10).

**Condemned generation** — the generation a GC targets; it collects that generation and everything younger (Ch 7).

**Conservative vs Precise Collector** — conservative guesses pointers by scanning; precise has full type/layout info; .NET is Precise (Ch 1).

**Cooperative vs Preemptive mode** — cooperative = thread may be touching GC references (must reach a safe point); preemptive = running non-managed code, safe to ignore (Ch 7).

**DATAS (Dynamically Adapting to Application Sizes)** — dynamically adjusts gen0 budget and the number of server heaps based on last-3-GC metrics; built on conservative mode (Ch 11).

**Demotion** — an object ending up in a lower generation than expected (opposite of promotion), an optimization reusing gaps left by pinning (Ch 5, Ch 9).

**Dependent handle** — bidirectional handle coupling a target (weak from dependent) and dependent (strong from target); dependent lives as long as target (Ch 13).

**Disposable pattern** — combining explicit `Dispose()` with an optional finalizer safety net that shares one cleanup path, plus `GC.SuppressFinalize` (Ch 12).

**Eager root collection** — Release/Tier1 JIT optimization where a local stops being a live root at its last use, not end of lexical scope (Ch 8).

**EE suspension** — Execution Engine suspending all managed threads ("stop the world") at safe points (Ch 7).

**Ephemeral generations** — gen0 and gen1, treated as "young"; gen2 is "old" (Ch 5).

**Escape analysis** — JIT optimization allocating a reference type on the stack when it proves the reference never escapes; partial and disabled by default in .NET 8 (Ch 4).

**ETW (Event Tracing for Windows)** — low-overhead machine-wide event pipeline (event/session/provider/controller/consumer) with kernel buffers (Ch 3).

**EventPipe** — cross-platform diagnostic channel (Named Pipes/Unix Domain Sockets) by which .NET Core emits events and counters (Ch 3).

**False sharing** — independent per-thread data on one cache line causing needless MESI coherency invalidations across cores (up to ~7× slowdown) (Ch 2).

**Finalization queue** — array of addresses of all live finalizable objects, kept generation-aware via fill pointers (Ch 12).

**Finalizer** — C# `~Type()` compiled to an override of `Object.Finalize`; non-deterministic cleanup run on a dedicated thread (Ch 12).

**Floating garbage** — dead objects that survive a cycle because concurrent marking already marked them (Ch 11).

**Foreground GC** — a regular non-concurrent ephemeral GC that runs during a background GC (Ch 11).

**Free-list allocation** — bucketed scan of per-generation free gaps, balancing best-fit (many buckets) vs first-fit (one bucket) (Ch 6).

**Free object** — a fake 1-byte-element array with a dedicated method table filling free space so the heap stays walkable (Ch 6, Ch 9).

**fReachable queue** — objects found dead at end of Mark but still needing their finalizer to run, reachable only because of finalization (Ch 12).

**Full GC** — gen2 condemned; marks all generations plus LOH and POH; the costliest collection (Ch 7).

**Gap** — an adjacent group of not-marked (unreachable) objects identified during Plan (Ch 9).

**GC Info** — per-method densely packed binary metadata describing, per safe point, which slots hold live object references (Ch 8).

**GCHandle** — handle-table root created via `GCHandle.Alloc`; kinds include strong, pinned, weak, and weak-track-resurrection (Ch 8, Ch 12).

**Gen0 budget** — allocation budget for gen0; the misleading "Gen 0 heap size" counter reports this budget, not actual size (Ch 5, Ch 7).

**Generational GC** — SOH split into gen0/gen1/gen2 by GCs survived, exploiting the weak generational hypothesis to collect young often, old rarely (Ch 5).

**Heap balancing** — Server GC reassigning the most-allocating thread's context to another heap and moving the thread to the matching CPU (Ch 6).

**Hidden allocation** — object created implicitly by an operation (delegate, closure, boxing, params array, LINQ iterator, async state machine) (Ch 6).

**IMemoryOwner<T>** — `IDisposable` ownership abstraction for memory needing explicit cleanup; exactly one owner calls `Dispose` (Ch 14).

**Induced GC** — any explicitly requested collection (`GC.Collect`, internal runtime calls) (Ch 7).

**Interior pointer** — a pointer into the middle of an object (array element, struct field) rather than its header; resolved to the containing object via bricks/plug trees (Ch 1, Ch 8, Ch 13).

**Latency mode** — dynamically-settable `GCSettings.LatencyMode` (Batch, Interactive, LowLatency, SustainedLowLatency, NoGCRegion) dialing GC intrusiveness (Ch 11).

**Little's Law** — `occupancy = latency * throughput` (stable systems only) (Ch 3).

**Loader Heap** — conceptual per-AppDomain grouping of High/Low Frequency, Stub, and Virtual Call Stub heaps storing type metadata; not freed until AppDomain unloads (Ch 4).

**LOH (Large Object Heap)** — heap for objects ≥ 85,000 bytes; sweep-only by default (fragments), tracked internally as generation 3, collected with gen2 (Ch 5).

**Managed pointer (byref)** — a typed pointer (`Int32&`) surfaced in C# as `ref`; allowed only as locals, parameters, returns, and ref-struct fields, never on the heap (Ch 13).

**Mark phase** — first main GC phase: from every root, recursively traverse the object graph depth-first via a mark stack, setting a mark bit on each reachable object (Ch 8).

**Mark array** — separate bitmap (1 bit per 16-byte region on 64-bit) used by concurrent/background marking instead of flipping the MethodTable bit (Ch 11).

**Mark stealing** — Server GC threads stealing batches of objects to visit from each other to balance unequal heaps (Ch 11).

**Memory<T>** — a regular (non-ref) struct "span factory" that can live on the heap and in async code, producing a `Span<T>` via `.Span` (Ch 14).

**MESI** — cache-coherency protocol (Modified/Exclusive/Shared/Invalid) keeping per-core cache copies consistent (Ch 2).

**MethodTable (TypeHandle)** — per-type structure holding GCInfo, flags, instance size, EEClass reference, method and static-field data; the pointer through which EE and GC cooperate (Ch 4).

**Midlife crisis** — objects that live just long enough to be promoted to gen2 then die immediately; the worst case for the GC, solved by pooling (Ch 5, Ch 6).

**Mutator / Allocator / Collector triad** — Dijkstra's three cooperating abstractions of any automatic memory system (Ch 1).

**NonGC Heap (Frozen heap / NGCH)** — kind-based heap for immortal read-only literals (string literals, runtime types) that the GC never scans or collects (Ch 4, Ch 5).

**NoGCRegion** — reserved memory budget within which GC is disallowed; set via `GC.TryStartNoGCRegion` and paired with `EndNoGCRegion` (Ch 11, Ch 15).

**NUMA factor** — the extra cost of accessing non-local memory; the .NET GC is NUMA-aware (Ch 2).

**Object header (sync block)** — per-object header word preceding the MethodTable pointer; minimum object size is 12 B (32-bit) / 24 B (64-bit) (Ch 4).

**Pinned plug** — a group of pinned (marked) objects forced to relocation offset 0 so the allocator leaves it in place (Ch 9).

**Pinning** — preventing object movement via `fixed` (pinned local) or a pinned `GCHandle`; sets a pinning flag during GC (Ch 8, Ch 9).

**Plan phase** — GC phase that simulates compaction without moving objects, producing plug relocation offsets and gap sizes consumed by Sweep or Compact (Ch 9).

**Plug** — an adjacent group of marked (reachable) objects identified during Plan (Ch 9).

**POH (Pinned Object Heap)** — kind-based heap (since .NET 5) for pinned arrays of blittable types via `GC.AllocateArray` (Ch 5).

**Pre-plug / post-plug** — object endings overwritten to store pinned-plug info and saved in the pinned plug queue, restored during Sweep/Compact (Ch 9).

**Promotion** — moving an object to an older generation on survival; .NET promotes by moving logical address boundaries, not copying (Ch 5).

**Provisional mode** — transient auto-mode converting an expensive Full GC into a compacting Gen1 GC under high memory + fragmented gen2 (Ch 7).

**Reachability** — a decidable proxy for liveness: an object is reachable if a chain of references leads to it from a root (Ch 1).

**Reference counting** — per-object counter incremented/decremented on assignment; deterministic but cannot reclaim circular references (Ch 1).

**Region vs Segment** — .NET 7+ (64-bit) uses per-generation regions (no ephemeral segment); pre-.NET 7 uses segments with one ephemeral segment for gen0/1 (Ch 5).

**Relocation offset** — amount subtracted from an object's address to get its post-compaction address (Ch 9).

**Remembered set** — separately managed collection of older-to-younger references added during Mark as extra roots (Ch 5).

**Resurrection** — a finalizer reassigning `this` to a live root, making a dead object reachable again (Ch 12).

**Root** — a starting reference for reachability: local variables/arguments (stack/registers), statics, and internal Collector structures (Ch 1, Ch 8).

**ref struct (byref-like)** — a stack-only struct that may hold a managed pointer, never boxed, heaped, or shared across threads; foundation for `Span<T>` (Ch 13, Ch 14).

**readonly struct** — a struct with all fields readonly, letting the compiler skip defensive copies on `in`/`readonly ref` (Ch 13).

**SafeHandle** — critically finalizable, ref-counted `IntPtr` wrapper preferred over custom finalizers; blocks handle-recycling attacks (Ch 12).

**Safe point** — a location (typically a call site) where a thread can be suspended for GC; roots reported per safe point in GC Info (Ch 7, Ch 8).

**Server vs Workstation GC** — Server maximizes throughput (one heap per logical core, parallel, more memory); Workstation minimizes pause latency (single heap, small footprint) (Ch 7, Ch 11).

**Shallow / total / retained size** — object itself; shallow plus dependency subgraph; memory reclaimed if the object were removed (Ch 3).

**SOH (Small Object Heap)** — heap for objects < 85,000 bytes; compactable and split into gen0/1/2 (Ch 5).

**Span<T> / ReadOnlySpan<T>** — a `ref struct` holding a managed pointer + length representing any contiguous memory, giving zero-allocation slicing on the stack (Ch 14).

**Survival rate** — survived bytes ÷ total bytes in a generation; the main driver of the new allocation budget (Ch 7).

**Sweep** — GC phase turning gaps into free-list items in place without moving objects (Ch 10).

**Sliding compaction** — copying lower addresses first in ≥1-pointer chunks so a plug's destination never overwrites its own uncopied source (Ch 10).

**TraceEvent** — `Microsoft.Diagnostics.Tracing.TraceEvent`, a library to collect/process CLR events via ETW or EventPipe (Ch 15).

**TLS (Thread Local Storage)** — global-by-name data stored per thread (`[ThreadStatic]`, `ThreadLocal<T>`); thread-affinity, not fast memory (Ch 13).

**UOH (User Old Heap)** — shared code base for LOH + POH allocation; no fast path, always slow-path, must zero memory (Ch 6).

**Value type vs reference type** — value instances directly contain their data (no identity); reference instances hold a reference to shared data with identity; storage is decided by lifetime/sharing, not "stack vs heap" (Ch 4).

**Virtual memory reserve/commit** — OS model where the CLR reserves address space (`MEM_RESERVE`) then commits pages on demand; reserved ≠ committed (Ch 2, Ch 5).

**Weak reference** — a reference the GC does not treat as a root; short handle zeroes before finalizers, long handle tracks resurrection (Ch 12).

**Weak generational hypothesis** — infant mortality: most young objects die fast, the basis of generational GC (Ch 5).

**Write barrier** — JIT-injected code on reference-field writes that dirties a card covering the source object; also used by concurrent marking's write watch (Ch 5, Ch 11).
