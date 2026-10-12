# Chapter 13: Thread-Safe Collections

## Core Idea
Regular `System.Collections.Generic` collections corrupt under concurrent writes, and wrapping them in locks is subtly wrong (composing thread-safe ops isn't thread-safe). .NET offers three purpose-built families: **concurrent** (safe mutation), **immutable** (safe by never changing), and **frozen** (read-optimized, never changes).

## Frameworks Introduced
- **Concurrent collections** (`System.Collections.Concurrent`): fine-grained/lock-free; combine check+act into one atomic call to kill race windows.
  - `ConcurrentDictionary<K,V>`: no `Add` (→ `TryAdd`), plus `GetOrAdd`, `TryRemove`, `TryUpdate(key, new, expected)`. `GetOrAdd(key, factory)` replaces the whole 21-line locked cache in one line.
  - `ConcurrentQueue<T>`/`ConcurrentStack<T>`: `TryDequeue`/`TryPop` fuse check+remove. `ConcurrentBag<T>`: unordered, per-thread queues + work-stealing — only when the *same* threads both add and take.
  - `BlockingCollection<T>`: adds producer/consumer *waiting* + bounded capacity on top of a concurrent backing (Queue default / Stack / Bag). `Add`/`Take`/`GetConsumingEnumerable`/`CompleteAdding`. **Blocking — doesn't fit async.**
  - `Channel<T>`: async multi-producer/consumer queue — the async substitute for `BlockingCollection` (`Writer.WriteAsync`, `Reader.ReadAsync`, `Complete()`).
- **Immutable collections** (`System.Collections.Immutable`): every "change" returns a *new* collection sharing most nodes (stack = linked list, queue = 2 lists, rest = trees). Thread-safe because unchangeable.
  - **Critical caveat**: the *variable* holding "the current version" is still a plain variable — concurrent reassignment needs synchronization. Use `ImmutableInterlocked` (`TryUpdate`, `GetOrAdd`, `Push`/`TryPop`, …) for lock-free swaps — all-or-nothing, single-collection only. If you reach for it, `ConcurrentDictionary` is usually simpler/faster.
  - `ImmutableArray<T>`: the exception — backed by an array → slowest to modify, fastest to read; treat like a frozen collection.
- **Frozen collections** (`FrozenDictionary<K,V>`, `FrozenSet<T>`): slow to build, fastest to read, *cannot* be modified at all. For data that (almost) never changes.

## Key Concepts
- **Why lock-wrapping fails**: `TryGetValue` then (unlock) initialize then (lock) `Add` — two threads both miss, both init, second `Add` throws `ArgumentException`. Even `[]` overwrite loses one thread's object. Correct hand-rolled version is ~21 lines.
- **Why the concurrent interface differs**: `Count>0` then `Dequeue` has a race window; `TryDequeue(out x)` closes it.
- **Arrays & CPU cache**: standard collections use arrays (contiguous → cache-predictable, ~33 ops per memory fetch); immutable collections use nodes/trees (not contiguous → slower reads) to enable structural sharing.
- **Builders**: `ToBuilder()` → mutable, not thread-safe; batch many edits, then `ToImmutable()` = one new collection. Or `AddRange`/`RemoveRange` for bulk.
- **Frozen duplicates**: `ToFrozenSet`/`ToFrozenDictionary` keep the *last* duplicate (regular collections throw).

## Mental Models
- Concurrent = "safe to mutate concurrently"; Immutable = "safe because it never mutates"; Frozen = "immutable AND read-optimized, build-once."
- Immutable collection object = thread-safe; the *reference variable* to it = not. That's the whole gotcha.
- `GetOrAdd`/`TryUpdate`-loop is the atomic replacement for check-then-act.

## Decision Table

| Need | Use |
|---|---|
| Concurrent read+write dictionary/queue/stack | `ConcurrentDictionary`/`ConcurrentQueue`/`ConcurrentStack` |
| Same threads add & consume, order irrelevant | `ConcurrentBag<T>` |
| Producer/consumer, block when empty (own threads) | `BlockingCollection<T>` |
| Producer/consumer, **async** | `Channel<T>` |
| Functional style / undo / preserve prior states | immutable collections |
| Pass a collection to untrusted code, staleness OK | immutable (no defensive copy) |
| Read-only sequential, thread-safe | `ImmutableArray<T>` |
| Data (almost) never changes, read-hot | `FrozenDictionary`/`FrozenSet` |
| You already hold a lock for your own logic | plain `Dictionary`/`Queue`/`Stack` (simpler, faster) |

## Worked Example
Race-free cache — one line vs. 21:

```csharp
// The GetOrAdd replaces the entire lock-release-relock-recheck dance
var item = dictionary.GetOrAdd(itemId, CreateAndInitializeItem);
// Note: with the factory overload, CreateAndInitializeItem may run in several threads,
// but GetOrAdd returns the SAME object to all of them.

// Lock-free increment via optimistic retry
public void Increment(string key) {
    while (true) {
        int prev = _dictionary[key];
        if (_dictionary.TryUpdate(key, prev + 1, prev)) break;   // succeeds only if unchanged
    }
}
```

Immutable inventory — the variable, not the dictionary, is the hazard:

```csharp
// SAFE: ImmutableInterlocked.TryUpdate atomically swaps the whole dictionary
public bool TryToBuyBook(string bookId) {
    while (true) {
        if (!_bookIdToQuantity.TryGetValue(bookId, out var stock)) return false;
        if (stock == 0) return false;
        if (ImmutableInterlocked.TryUpdate(ref _bookIdToQuantity, bookId, stock - 1, stock))
            return true;   // retries if another thread changed it
    }
}
```
**What it demonstrates**: `GetOrAdd`/`TryUpdate` fuse check-and-act atomically; and even with an *immutable* dictionary you must guard the reference variable (here via `ImmutableInterlocked`) — at which point `ConcurrentDictionary` would often be simpler.

## Anti-patterns
- **Concurrent writes to a plain `Dictionary`/`List`/etc.**: corruption; even `foreach` needs no concurrent writer.
- **Wrapping a generic collection in short locks around each call**: composing thread-safe ops → race (double-init, lost updates).
- **`BlockingCollection.Take`/`GetConsumingEnumerable` in async code**: it blocks — use `Channel<T>`.
- **`BlockingCollection.AddToAny`/`TakeFromAny` for load balancing**: no balancing — piles work on the first collection.
- **`ConcurrentBag` in async code / when different threads add vs take**: work-stealing overhead, wrong thread ownership.
- **Assuming an immutable collection is fully thread-safe**: the holding variable still needs synchronization.
- **Mixing `ImmutableInterlocked` with the collection's own mutation methods**: not thread-safe — pick one.
- **Frozen collections for changing data**: rebuild cost dwarfs read savings.

## Key Takeaways
1. Generic collections allow concurrent reads only; concurrent writes corrupt them.
2. Concurrent collections change the interface (`TryAdd`/`GetOrAdd`/`TryDequeue`) to fuse check-and-act atomically.
3. `GetOrAdd` is the correct one-line thread-safe cache; `TryUpdate` enables lock-free optimistic updates.
4. `BlockingCollection<T>` = own-thread producer/consumer; `Channel<T>` = async equivalent.
5. Immutable = safe by never changing, but the reference variable still needs sync (`ImmutableInterlocked`, single-collection only).
6. `ImmutableArray<T>` reads fast/writes slow — treat like frozen.
7. Frozen collections: build-once, read-fast, no mutation — for near-static data.

## Connects To
- **Ch 5**: the naive async cache this chapter fixes properly.
- **Ch 8**: `BlockingCollection` work queue (single consumer) generalized to many consumers + async.
- **Ch 14**: turning `Channel<T>`'s `while(true)`+exception loop into `await foreach` / `IAsyncEnumerable`.
- **Ch 4/7**: `lock`, `Interlocked`, composing-thread-safe-ops-isn't-thread-safe.
