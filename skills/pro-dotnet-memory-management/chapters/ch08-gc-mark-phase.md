# Chapter 8: Garbage Collection - Mark Phase

## Core Idea
The Mark phase is the first main GC phase: a tracing collector suspends all managed threads, then starts from every kind of GC root and recursively traverses the object graph (depth-first, via a heap-allocated mark stack), setting a mark bit on every reachable object. Anything not reached is dead. Mastering the different root types is the single most useful skill for diagnosing memory growth and leaks.

## Frameworks Introduced
- **Marking traversal (per root)**: Given a root address, the GC does three things.
  - How: (1) Translate to the object start — needed for an *interior pointer* (points inside an array/struct, not at the header). (2) Set the pinning flag in the object header if pinned (POH objects are always pinned). (3) Traverse outgoing references depth-first via the **mark stack**: if the target is already visited or in an older generation, skip; otherwise mark it (set a bit in its `MethodTable` pointer) and push its references. Ends when the mark stack empties.
  - Why iterative not recursive: recursion risks stack overflow on deep graphs; a growable heap-based mark stack is safe. In .NET code: `GCHeap::Promote` → `gc_heap::mark_object_simple` → `mark_object_simple1` (uses `mark_stack_array`, `mark_stack_bos/tos`).

- **Eager root collection**: In Release + Tier1, a local variable stops being a live root as soon as it is last *used*, not at the end of its lexical scope.
  - When to use: it's automatic; understand it to explain "works in Debug, breaks in Release."
  - How: the C# compiler records real usage; the JIT shortens slot lifetimes (reusing registers) and emits tighter GC Info. Debug/Tier0 instead extend every local to end-of-lexical-scope (for debuggability).
  - Failure mode: objects with lifetime-tied side effects (`Timer`, `Mutex`, file handles) can be collected while seemingly in scope — even while one of their own methods runs, if that method doesn't touch `this`. Fix with `GC.KeepAlive` or `Dispose`.

- **GC Info**: Per-method, densely packed binary metadata the JIT emits describing, for each safe point, which slots (stack offsets or registers) hold live object references. This is what the stack walker consults during marking.

## Key Concepts
- **Stack roots**: Live local variables of all methods in every managed thread's call stack — stored on the stack OR in CPU registers.
- **Interior pointer**: A root pointing inside an object (e.g. an array element) rather than at its header; GC translates it to the object start.
- **Untracked root**: An argument/local whose lifetime info isn't available; assumed live for the entire method body (unless it holds zero).
- **Pinned local variable**: Created implicitly by the C# `fixed` keyword; emitted in CIL as a `pinned` local, marked pinned+interior in GC Info so GC won't move it.
- **GC internal roots**: Older-to-younger cross-generational references found via the card mechanism during gen0/gen1 GCs.
- **Strong handle / Pinned handle**: Handle-table roots created via `GCHandle.Alloc`; pinned handles also set the object's pinning bit. Async pinned handles auto-unpin when I/O completes.
- **Finalization roots**: Objects in the finalization queues, scanned one by one as roots.
- **Card efficiency ratio**: Fraction of set cards actually pointing at gen0; if below threshold (default 30%, `DOTNET_GCLowSkipRatio`), GC condemns gen1 instead of gen0.

## Mental Models
- **Lexical scope ⊇ actual liveness**: Debug marks live for the whole scope; Release marks live only through the last real use. Think "the JIT frees objects the instant your code stops touching them."
- **Safe point = on return, not on call**: A call site reports no live roots for the arguments — keeping them alive is the *callee's* responsibility. That's why `!u -gcinfo` shows safe points with no roots.
- **Setting a local to `null` is (almost) pointless**: The JIT already sees real scope and optimizes out redundant `x = null`. Exception: *untracked* variables, which stay live the whole method.
- **Memory leaks are never marking bugs**: Growing memory means something is still *rooting* the objects. Find the root, not a GC defect.

## Anti-patterns
- **Relying on lexical scope for lifetime-critical objects**: A `Timer` or `Mutex` in a local can be collected mid-use in Release. Use `GC.KeepAlive(obj)` at the end or `Dispose()`/`using`.
- **Starting leak analysis from strings**: Strings are always the most numerous objects; they're usually legitimate. Explore other leads first, circle back last.
- **Assuming gen2 growth = leak**: Only a leak if memory keeps growing *despite* compacting full gen2 GCs. Otherwise it may just be uncollected gen2, or fragmentation from non-compacting background GCs.

## Code Examples
```csharp
static void Main(string[] args)
{
    Timer timer = new Timer((obj) => Console.WriteLine(DateTime.Now.ToString()), null, 0, 100);
    Console.WriteLine("Hello World!");
    GC.Collect();       // simulate GC happening here
    Console.ReadLine();
}
// Release output: "Hello World!" then maybe one timestamp — timer is
// eagerly collected after line 3 and stops ticking.
```
- **What it demonstrates**: Eager root collection kills the `Timer` because it isn't used after creation. Fix: append `GC.KeepAlive(timer);`.

```csharp
[Intrinsic]
[MethodImplAttribute(MethodImplOptions.NoInlining)]
public static void KeepAlive(Object obj) { }
```
- **What it demonstrates**: `GC.KeepAlive` is an empty, non-inlined (JIT intrinsic since .NET 5) method whose only job is to force the argument to be treated as used, extending its GC Info liveness to that point.

## Reference Tables

`_GC_ROOT_KIND` enum (from `MarkWithType` ETW events; values are cumulative in this order):

| Value | Name | Meaning |
|-------|------|---------|
| 0 | GC_ROOT_STACK | Stack/register roots |
| 1 | GC_ROOT_FQ | Finalization queue |
| 2 | GC_ROOT_HANDLES | GC handles |
| 3 | GC_ROOT_OLDER | Older-to-younger (cross-gen) |
| 4 | GC_ROOT_SIZEDREF | SizedRef handles |
| 5 | GC_ROOT_OVERFLOW | Mark stack overflow |
| 6 | GC_ROOT_DH_HANDLES | Dependent handles |
| 7 | GC_ROOT_NEW_FQ | New finalization queue |
| 8 | GC_ROOT_STEAL | Work stealing |
| 9 | GC_ROOT_BGC | Background GC |

Diagnostic commands (WinDbg + SOS):

| Command | Purpose |
|---------|---------|
| `!name2ee <dll>!<Type.Method>` | Find a method's `MethodDesc` |
| `!gcinfo <MethodDesc>` | List safe points + live stack roots |
| `!u -gcinfo <MethodDesc>` | Interleave JITted asm with GC Info |
| `!gcroot <addr>` | Show what roots an object |
| `!gchandles` | List all GC handles (filterable) |
| `!gcwhere <addr>` | Which heap/segment/generation |
| `!dumpheap -type <T>` | Find instances of a type |

## Worked Example
**Reading GC Info to see eager root collection** (`LexicalScopeExample`, partially interruptible):

`!gcinfo <MethodDesc>` reports five safe points and `Return Kind: Scalar`, `Code size: 58`. Running `!u -gcinfo` interleaves the assembly:

```
mov rcx,...(MT: ClassOne)
call CORINFO_HELP_NEWSFAST
00000016 is a safepoint:        ; no live roots reported
call (ClassOne.Check())
0000001f is a safepoint:
...
```

Key insight: every safe point reports **zero** live roots even though `c1` is "in scope." Because suspension happens when a method *returns*, at each call site the callee owns keeping its own arguments alive — so `LexicalScopeExample` reports nothing. For a **fully interruptible** method (`RegisterMap`, a loop with dynamic bounds), the output instead shows `interruptible` regions with slot-liveness deltas like `00000019 +rax` (rax becomes a live root) and `00000024 -rax` (rax dies) — and thanks to inlining, the `SomeClass` root dies *before the loop even starts*.

**Rooting different objects** (Listing 8-25 via `!gcroot`): a `Normal` local → "Found 0 unique roots" (eagerly collected); an explicitly `Pinned`-handle object → `HandleTable: ...(pinned handle)`; a `static` field → `HandleTable: ...(strong handle) -> System.Object[] -> Static` (statics live in a POH `Object[]` held by a strong handle); a `GC.KeepAlive`'d object → `Thread ...: Run() rbx:` (enregistered stack root).

## Key Takeaways
1. Marking traverses depth-first from roots via a growable mark stack; the mark bit lives in the `MethodTable` pointer's low bits, cleared in the Plan phase.
2. In Release/Tier1, object liveness follows *last use*, not lexical scope — never rely on scope for `Timer`/`Mutex`/handles; use `GC.KeepAlive` or `Dispose`.
3. There are five root categories: stack, finalization, GC-internal (cross-gen cards), and GC handles (strong/pinned) — plus interned strings and statics, which live in POH `Object[]` arrays rooted by handles.
4. GC Info (viewed with `!gcinfo` / `!u -gcinfo`) records live slots per safe point; fully interruptible methods use liveness deltas, partially interruptible ones use safe points at calls.
5. `fixed` (pinned local) and `GCHandle.Alloc(obj, Pinned)` both prevent movement but differ in root type (stack vs handle table); pinning bits are set only during GC and cleared before it ends — hard to spot in a dump (use the `PinObjectAtGCTime` ETW event).
6. Confirm a real managed leak only when memory grows despite compacting gen2 GCs (force one via keyword `0x800000` / `dotnet-trace ... :800000`); then diff two heap snapshots in PerfView.
7. Use `MarkWithType` events + generational aware analysis (`DOTNET_GCGenAnalysisGen`/`Bytes`/`Index`) to see which root kinds promote the most bytes and what younger objects older gens hold.

## Connects To
- **Ch 4**: References vs reference-type data; local variables in registers/stack; GC handles.
- **Ch 5**: Card table / card words / bundles that back GC internal (cross-gen) roots; Scenario 5-2 (same nopCommerce leak).
- **Ch 7**: EE suspension, safe points, partially/fully interruptible methods, collection tuning / condemned reasons.
- **Ch 9 (next)**: Plan phase — where pinned/marked bits are cleared; bricks used to find first object in a card region.
- **Ch 12**: Finalization mechanism and weak handles.
- **CLR internals**: `GCHeap::Promote`, `GCScan::GcScanRoots/GcScanHandles`, `mark_through_cards_*`; POH (Pinned Object Heap), NGCH/Frozen object heap for string literals.
