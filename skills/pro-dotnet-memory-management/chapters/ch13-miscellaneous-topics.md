# Chapter 13: Miscellaneous Topics

## Core Idea
A grab-bag of advanced, purely-practical memory mechanisms: dependent handles, thread local storage internals, and the whole family of managed-pointer / value-type features (ref locals/returns/params, readonly & ref structs, ref fields, fixed-size/inline arrays, struct layout, unmanaged & blittable types) that let performance-aware C# avoid copies and heap allocations while cooperating safely with the GC.

## Frameworks Introduced
- **Dependent handle**: A bidirectional handle coupling a *target* (primary) and *dependent* (secondary) object. From dependent→target it is a *weak* handle; from target→dependent it is a *strong* handle. The dependent lives as long as the target lives.
  - When to use: dynamically "add fields" to objects at runtime, caching keyed by object lifetime, weak-event patterns (WPF `WeakEventManager`), Edit-and-Continue.
  - How: `DependentHandle` (System.Runtime.CompilerServices, .NET 6+) or the wrapper `ConditionalWeakTable<TKey,TValue>` (dictionary with weak keys compared by `Object.ReferenceEquals`, one value per key). Dispose/`Clear` to free unmanaged handles.
  - Failure mode: dependent handles are NOT aged — all scanned during gen0 collection — and need *multipass* scanning during Mark (chained dependencies A→B→C require repeated re-scans). Use sparingly.
- **Managed pointer (byref)**: A typed pointer (`System.Int32&` in CIL) that may point to a local, parameter, field of a compound type, or array element — not just an object's start. Surfaced in C# as `ref` (params, locals, returns since C# 7).
  - When to use: avoid copying large value types type-safely; expose collection elements by reference; direct in-place mutation.
  - How: mark both sides of assignment with `ref`. Allowed only as local vars, parameter signatures, method return types, and ref-struct fields — never on the heap (no object fields, no boxing, no array elements).
  - Why the limits: a managed pointer may point to the stack (would outlive its target if heaped) and is reported to the GC as an *interior pointer*, resolved via bricks + plug trees — too expensive to allow in arbitrary object graphs.
- **Thread Local Storage (TLS)**: Global-by-name data stored separately per thread, avoiding synchronization. Three flavors: `[ThreadStatic]` fields (fastest), `ThreadLocal<T>` (deterministic lazy init), thread data slots (obsolete wrapper over `ThreadLocal<T>`).

## Key Concepts
- **`ConditionalWeakTable`**: Container of dependent handles; keys weak, auto-removed when key dies; single value per key (use multiple tables for more). Released by finalizer or explicit `Clear`.
- **`[ThreadStatic]` gotcha**: A field initializer runs only on the thread that first ran the static ctor; other threads see the default value.
- **`ThreadLocal<T>`**: Wrapper over a thread-static field with a value factory; `trackAllValues:true` exposes `Values`; has a finalizer and takes a global lock on construction/finalization (contention risk).
- **Interior pointer**: A managed pointer into the middle of a heap object; always reported to the GC as interior, resolved to its containing object via brick/plug-tree traversal; can be the *sole root* keeping an object alive.
- **Ref return / ref local**: Return/store a managed pointer whose lifetime must extend beyond the method (not a plain method local). Consume with `ref`, by value (dereferenced copy), or by direct assignment (`coll.GetBookById(2) = new Book{...}`).
- **Readonly ref / `in` parameter**: Pass by reference but forbid mutation. For value-type target: whole value protected. For reference-type target: only the reference is protected (target fields still mutable).
- **Defensive copy**: When a method is called on a `readonly ref`/`in` struct, the compiler copies the struct first (unless the struct is marked `readonly`) — surprising and costly.
- **Readonly struct / ref struct / ref field**: `readonly struct` (all fields readonly, no defensive copies); `ref struct` (byref-like, stack-only, may hold a managed pointer, never boxed/heaped/shared across threads); `ref` field (C# 11) holds a managed pointer.
- **Unmanaged vs blittable type**: *Unmanaged* = value type with no reference fields at any nesting (enables `T*`, `sizeof(T)`, `stackalloc T`). *Blittable* = identical managed/unmanaged memory layout for Interop; stricter (excludes `decimal`, `bool`, `char`, `DateTime`, `Guid`).

## Mental Models
- Think of a `ref` variable as **a variable holding an address, not a pointer** — "refs are not pointers" (Sadov). Its whole reason to exist: avoid copying large structs type-safely.
- Think of TLS as **thread-affinity, not magic-fast memory** — the OS TLS slot only holds a pointer to `ThreadLocalInfo`; actual thread-static data lives in the CLR private heap and GC heap like normal statics. It removes synchronization, it does not speed access up (static access is orders of magnitude slower than plain fields).
- Use `readonly struct` whenever a struct can be immutable — it lets the compiler *skip defensive copies* on `in`/`readonly ref`.
- Use `LayoutKind.Auto` for high-performance structs you'll never pass to Interop — it reorders fields to minimize padding.

## Anti-patterns
- **Storing back-references inside `ThreadLocal<T>` without disposing it**: values live until the thread dies; if items reference back to the owner, they root the `ThreadLocal<T>` and leak the whole object graph. Always `Dispose`.
- **Passing large structs by value in hot paths**: copying cost grows with struct size — use `ref`/`in`.
- **Expecting `ref readonly`/`in` struct method calls to mutate**: they run on a throwaway defensive copy (unless struct is `readonly`).
- **Sequential struct layout for dense general-purpose data**: default `LayoutKind.Sequential` wastes padding (e.g., 11 of 24 bytes).
- **Overusing dependent handles**: not aged, scanned every gen0, multipass Mark cost.

## Code Examples
```csharp
static object _target = new object();
static void TestDependent() {
    var dependent = new Object();
    var dependentWeakRef = new WeakReference(dependent);
    var dependentHandle = new DependentHandle(_target, dependent);
    Console.WriteLine(dependentHandle.Target == null); // False
    Console.WriteLine(dependentWeakRef.IsAlive);        // True
    var (target2, dependent2) = dependentHandle.TargetAndDependent; // atomic
    _target = null;      // Clear the target
    GC.Collect(2);
    Console.WriteLine(dependentHandle.Target == null);  // True
    Console.WriteLine(dependentWeakRef.IsAlive);        // False
    dependentHandle.Dispose();
}
```
- **What it demonstrates**: the strong-from-target / weak-from-dependent lifetime coupling of a dependent handle — the dependent survives only while the target is reachable.

```csharp
// ref return exposes internal storage; direct assignment writes into it
public ref Book GetBookById(int id) => ref books[id];
collection.GetBookById(2) = new Book { Title = "The Hobbit", Author = "Tolkien" };
```
- **What it demonstrates**: consuming a ref-return by direct assignment (omit `ref`, put call on the left of `=`).

## Reference Tables

Thread-safe counter benchmark (.NET 8, 32 threads):

| Method               | Iterations | Mean       | Allocated |
|----------------------|-----------:|-----------:|----------:|
| InterlockedIncrement |  1,000,000 |   715.2 ms |   4.71 KB |
| Lock                 |  1,000,000 | 1,323.9 ms |   5.04 KB |
| ThreadLocal          |  1,000,000 |    23.6 ms |  20.43 KB |

`ThreadLocal<T>` (per-thread sub-counters + final aggregate) wins massively under max contention; allocates more.

By-value vs by-ref struct passing (constant time regardless of size for byref):

| Method          | Mean     | Allocated |
|-----------------|---------:|----------:|
| Struct 32B      | 1.560 ns | 0 B |
| Struct 112B     | 5.229 ns | 0 B |
| Struct 192B     | 7.457 ns | 0 B |
| ByRefStruct 32B | 1.332 ns | 0 B |
| ByRefStruct 192B| 1.329 ns | 0 B |
| ClassAccess     | 1.098 ns | 0 B |

`StructLayout` kinds:

| LayoutKind | Behavior | Default for |
|------------|----------|-------------|
| Sequential | Fields in declaration order, aligned/padded | unmanaged structs |
| Auto | Fields reordered to minimize padding; cannot Interop | classes, non-unmanaged structs |
| Explicit | You set every `[FieldOffset]`; overlaps allowed (discriminated unions) | — |

Ref-field readonly semantics (C# 11): `readonly ref` = pointer fixed, value assignable; `ref readonly` = pointer reassignable, value fixed; `readonly ref readonly` = both fixed.

## Worked Example
**Interior pointer as sole root (WinDbg).** A method builds an `ArrayWrapper { Array=new[]{1,2,3}, Field=0 }`, returns `ref wrapper.Field`, and hands out a `WeakReference` to observe liveness. Back in `Main`, the local `ref int byRef` points at the wrapper's `Field`. Repeated `GC.Collect()` prints `4 True` — the wrapper stays alive with no visible reference, because the interior pointer on the stack roots it. `!gcroot` confirms it:
```
> !gcroot 0000027b00023d20
Thread 3f48:
  ...Program.Main(System.String[])
  rbp-50: ...(interior) -> 0000027b00023d20 ArrayWrapper
Found 1 unique roots
```
Now change the return to `ref wrapper.Array[index]`. Output flips to `4 False` — the interior pointer roots the inner `int[]`, but nothing roots the `ArrayWrapper`, so the wrapper is collected while the array survives. The GC resolves the interior pointer to its containing object via the brick table + plug tree (Ch 9), so it correctly keeps only the array alive.

## Key Takeaways
1. Dependent handles / `ConditionalWeakTable` attach lifetime-coupled data to objects without keeping keys alive — but they're unaged and multipass-scanned, so use sparingly and dispose.
2. `[ThreadStatic]` is fastest but its initializer runs on one thread only; `ThreadLocal<T>` gives deterministic lazy init at a construction/finalization-lock cost. Dispose `ThreadLocal<T>` to avoid leaks.
3. TLS is thread-affinity, not fast memory — data lives on normal heaps; the OS slot only holds a `ThreadLocalInfo` pointer, and static access stays orders of magnitude slower than plain fields.
4. `ref` params/locals/returns exist to avoid copying value types type-safely; managed pointers can't live on the heap because they may point to the stack and are GC-resolved as interior pointers.
5. `readonly ref`/`in` and `readonly struct` control mutability; mark structs `readonly` to eliminate defensive copies.
6. `ref struct` (byref-like) guarantees stack-only, single-thread, never-boxed — the foundation for `Span<T>` (Ch 14); ref fields (C# 11) let it hold a managed pointer.
7. Struct layout matters: `Sequential` (default, Interop-safe, padded) vs `Auto` (reordered, dense, no Interop) vs `Explicit` (`[FieldOffset]`, unions). Inspect with ObjectLayoutInspector, sharplab.io, or `!dumpvc`.

## Connects To
- **Ch 4**: object reference vs managed pointer; struct value semantics; MethodTable / object header layout.
- **Ch 6**: closures/boxing (why ref structs can't be captured); `unmanaged` types and `stackalloc`.
- **Ch 8**: interruptible vs atomic JITted methods, GCInfo, early root collection, safepoints.
- **Ch 9**: brick table + plug trees used to resolve interior pointers during Mark/Plan/relocation.
- **Ch 12**: weak references (long weak references) and weak-event pattern.
- **Ch 14**: `Span<T>`, fixed-size/inline arrays, and data-oriented design build directly on ref structs and struct layout.
- **CLR internals**: `JIT_GetSharedGCThreadStaticBaseOptimized`, `ThreadLocalInfo`/`ThreadLocalModule`, `gc_heap::find_object`, `CollectionsMarshal`, `MemoryMarshal.CreateSpan`, `InlineArrayAttribute`.
