# Chapter 14: Advanced Techniques

## Core Idea
Modern high-performance .NET means eliminating heap allocations and copies: `Span<T>`/`Memory<T>` give a single, sliceable, zero-allocation view over any contiguous memory; `Unsafe`/`MemoryMarshal` expose IL-level tricks; data-oriented design and Pipelines restructure code around cache-friendly, zero-copy data flow.

## Frameworks Introduced
- **`Span<T>` / `ReadOnlySpan<T>`**: A `ref struct` (byref-like) holding a managed pointer + length, representing any contiguous memory (heap array, `stackalloc`, native, string).
  - When to use: high-performance, general-purpose code needing zero-allocation slicing; prefer as a method argument over `Memory<T>`.
  - How: construct from array/`stackalloc`/`void*`; call `.Slice(start, length)` for allocation-free subranges; `str.AsSpan()` yields `ReadOnlySpan<char>`. Cannot escape to heap, be boxed, be a class field, or be used in `async`/iterators.
  - Why it works: as a `ref struct` it lives only on the stack, so it can safely hold a managed *interior* pointer as a field without creating a GC hole.
- **`Memory<T>` / `ReadOnlyMemory<T>`**: A regular (non-ref) `struct` that *can* live on the heap — a "span factory."
  - When to use: async code and object fields, where `Span<T>` is illegal. Wraps array, string (`ReadOnlyMemory<char>`), or an `IMemoryOwner<T>`.
  - How: get a `Span<T>` via `.Span` for local work; `.Slice(...)`, `.ToArray()`, `.ToString()`; `.Pin()` returns a `MemoryHandle` for P/Invoke. Cannot wrap `stackalloc`.
- **`IMemoryOwner<T>` / `MemoryManager<T>`**: Ownership abstraction (`IDisposable`) for memory needing explicit cleanup (e.g. pooled/native). Exactly one owner calls `Dispose`; owning types must themselves be disposable. `MemoryPool<T>.Shared.Rent(n)` returns an owner backed by `ArrayPool<T>.Shared`.
- **`Unsafe` class**: `System.Runtime.CompilerServices.Unsafe` wraps IL ops inexpressible in C#, callable from *safe* code. Groups: casting/reinterpretation (`As`, `AsPointer`, `AsRef`, `BitCast`), pointer arithmetic (`Add`, `Subtract`, `AddByteOffset`), info (`SizeOf`, `ByteOffset`, `AreSame`), memory access (`Read`, `Write`, `CopyBlock`, `InitBlock`).
- **Data-Oriented Design (Tactical vs Strategic)**: Design data/layout for sequential, cache-line-friendly access and easy parallelization. Tactical = local field-layout tweaks (drops into OOP). Strategic = architectural mind-shift (AoS→SoA, ECS).
- **Pipelines (`System.IO.Pipelines`)**: Stream-like, pooled, async, thread-safe producer/consumer buffers for zero-copy high-scale I/O (built for Kestrel).

## Key Concepts
- **byref-like field**: A managed (interior) pointer stored as a field — legal only inside a `ref struct`; enables "fast span."
- **"Fast span" vs "slow span"**: Fast (.NET Core 2.1+) stores one byref field (runtime support); slow (.NET Framework) stores object ref + `IntPtr` offset + length. Slow is ~2× slower on pure indexing.
- **`ValueStringBuilder`**: Internal `ref struct` StringBuilder backed by a storage-agnostic `Span<char>` (stackalloc → `ArrayPool` on grow); has `Dispose` but can't implement `IDisposable` (ref structs can't implement interfaces).
- **AoS → SoA**: Array-of-Structures → Structure-of-Arrays; one array per field so hot-path loops read densely packed, prefetcher-friendly data.
- **Entity Component System (ECS)**: Composition over inheritance — Entity (id only), Component (data only), System (logic over filtered entities); component data stored SoA-style.
- **`ReadOnlySequence<byte>`**: Pipeline read buffer of one or more segments; `IsSingleSegment`, `.First` (`ReadOnlyMemory<byte>`), enumerable.
- **`MemoryMarshal`**: Helpers for span/memory magic: `AsBytes`, `Cast<TFrom,TTo>`, `TryGetArray`, `GetReference`.

## Mental Models
- Use `Span<T>` for synchronous local buffers; switch to `Memory<T>` the moment code goes `async` or must store the buffer in a field.
- Think of `Memory<T>` as a heap-safe *box* whose contents are only reachable by producing a `Span<T>` from it.
- Prefer read-only versions: a method taking `ReadOnlySpan<T>` accepts both `Span<T>` and `ReadOnlySpan<T>`; the reverse fails.
- In DoD, "Customer" stops being an object — it's just a shared index across parallel arrays (SoA).

## Anti-patterns
- **Ternary `stackalloc` vs `ArrayPool.Rent` into one `Span<T>`**: You lose the original array reference and can never `Return` it to the pool. Use the `unsafe` two-branch form keeping a separate `int[] array` variable.
- **`sync-over-async` with Pipelines** (`FlushAsync().GetAwaiter().GetResult()`): kills scalability; move only the `Span<T>` code into a synchronous *local function* instead.
- **Naive pipeline read/write** (`Writer.Write(new byte[]...)`, `result.Buffer.ToArray()`): re-introduces the very heap allocations/copies pipelines exist to avoid; use `GetSpan`/`GetMemory` + `Advance` and consume `ReadOnlySequence` in place.
- **`Unsafe.As` to break type hierarchies / mutability**: reinterpreting a primitive as a reference typically throws `AccessViolationException`; only for well-controlled low-level libs.
- **Cluttering the Business Layer with `Span<T>`/`Memory<T>`**: keep these Infrastructure-level; don't over-engineer domain code.

## Code Examples
```csharp
// Storage-agnostic ValueStringBuilder growth: stackalloc -> ArrayPool
private void Grow(int additionalCapacityBeyondPos) {
    int minimumLength = (int)Math.Max((uint)(_pos + additionalCapacityBeyondPos),
                            Math.Min((uint)(_chars.Length * 2), 2147483591u));
    char[] array = ArrayPool<char>.Shared.Rent(minimumLength);
    _chars.Slice(0, _pos).CopyTo(array);
    char[] arrayToReturnToPool = _arrayToReturnToPool;
    _chars = (_arrayToReturnToPool = array);
    if (arrayToReturnToPool != null)
        ArrayPool<char>.Shared.Return(arrayToReturnToPool);
}
```
- **What it demonstrates**: How a `ref struct` grows a `Span<char>` transparently from stack to pooled heap storage without the caller noticing.

```csharp
// SoA: no "Customer" object — data organized per field for cache locality
class CustomerRepository {
    int NumberOfCustomers;
    double[] Scoring; double[] Earnings; DateTime[] DateOfBirth; bool[] IsSmoking;
    public void UpdateScorings() {
        for (int i = 0; i < NumberOfCustomers; ++i)
            Scoring[i] = Earnings[i] * (IsSmoking[i] ? 0.8 : 1.0) * ProcessAge(DateOfBirth[i]);
    }
}
```
- **What it demonstrates**: Structure-of-Arrays — each array is densely packed and read sequentially, so the CPU prefetcher engages per array.

## Reference Tables

Span access benchmark (indexer, 128 bytes):

| Method       | Job                | Mean     | Allocated |
|--------------|--------------------|----------|-----------|
| SpanAccess   | .NET 8.0           | 50.66 ns | -         |
| ArrayAccess  | .NET 8.0           | 63.23 ns | -         |
| SpanAccess   | .NET Framework 4.8 | 96.56 ns | -         |
| ArrayAccess  | .NET Framework 4.8 | 66.49 ns | -         |

"Fast span" (.NET 8) beats a raw array (better bounds-check elimination, smaller struct); "slow span" (Framework) is ~50% slower.

Span vs Memory internal layout:

| Type | Kind | Fields | Heap? | async? |
|------|------|--------|-------|--------|
| Fast `Span<T>` | ref struct | byref `_reference`, `int _length` | no | no |
| Slow `Span<T>` | ref struct | `Pinnable<T>`, `IntPtr _byteOffset`, `int _length` | no | no |
| `Memory<T>` | struct | `object _object`, `int _index`, `int _length` | yes | yes |

## Worked Example
**Zero-copy pipeline read (Kestrel `ParseRequestLine`).** The reader awaits `ReadAsync()`, receiving a `ReadOnlySequence<byte>` buffer. `ProcessBuffer` sets `consumed = sequence.Start`, `examined = sequence.End`, then:
1. If `IsSingleSegment`, consume `sequence.First.Span` directly (no copy).
2. Else `foreach` segment, consuming each `segment.Span`.
For HTTP parsing it scans `span.IndexOf(ByteLF)`. If a `\n` is found, `consumed = buffer.GetPosition(lineIndex + 1, consumed)` and the line span is sliced/parsed under `fixed`. If no newline yet, it returns leaving `consumed` at start but `examined = buffer.End`. The distinction matters: `reader.AdvanceTo(consumed, examined)` tells the pipeline data up to `consumed` may be released, while data between `consumed` and `examined` is *replayed* on the next `ReadAsync` together with newly arrived bytes — so a partial message is re-presented until complete, with no buffering or copying in user code.

## Key Takeaways
1. `Span<T>` unifies array/`stackalloc`/native/string behind one sliceable, allocation-free API and simplifies overloaded APIs down to `Parse(ReadOnlySpan<char>)`.
2. `Span<T>` is a `ref struct` precisely because it must hold an interior pointer safely on the stack; that's also why it's banned from the heap, boxing, fields, and `async`.
3. Reach for `Memory<T>` + `IMemoryOwner<T>` when the buffer must survive an `await` or be owned; always pair pooled/native memory with an explicit `Dispose`.
4. `Unsafe` and `MemoryMarshal` let safe C# do IL-only reinterpretation and pointer arithmetic — powerful, crash-prone, infrastructure-only.
5. For the narrow class of throughput-critical apps (trading, big data, games, ML), restructure data for cache lines: fit hot fields in the first cache line, then AoS→SoA, then ECS.
6. Pipelines deliver pooled, async, thread-safe, zero-copy I/O — but only via `GetSpan`/`GetMemory`+`Advance` and in-place `ReadOnlySequence` consumption; never `sync-over-async`.
7. Don't over-engineer: keep these types in an Infrastructure library, out of the Business/domain layer.

## Connects To
- **Ch 13**: Direct continuation — ref types, ref returns, `ref struct`, object/struct layout underpin fast span and DoD.
- **Ch 2**: Cache hierarchy, cache lines, spatial/temporal locality, false sharing (Rule 2/Rule 3) motivate all data-oriented design here.
- **Ch 4**: Data locality of value-type arrays vs reference-type arrays (Figure 4-25).
- **CLR/runtime**: byref-like instance fields intrinsic added in .NET Core 2.1; `ref` fields in `ref struct` since C# 11 (CS8352/CS9080 escape rules).
- **`ArrayPool<T>` / `MemoryPool<T>`**: pooling backbone for `ValueStringBuilder`, `IMemoryOwner<T>`, and Pipelines.
