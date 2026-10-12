# Chapter 7: Classic Multithreading Pitfalls and How to Avoid Them

## Core Idea
Five failure modes — partial updates, deadlocks, race conditions, synchronization, starvation — plus memory reordering, are tamed by a small set of lock rules. The rules deliberately conflict (hold locks for the whole operation vs. hold them briefly), so judgment is required.

## Frameworks Introduced
- **The rules for easy multithreading**:
  1. **Always use a lock when accessing shared data** (reads too) — memory reordering means you can't trust order otherwise.
  2. **Always acquire locks in the same order** — *lock hierarchy*. Any consistent order works (even alphabetical).
  3. **Never call code you don't control while holding a lock** — external callbacks/events may take other locks → cross-file deadlock. Invoke them *after* releasing.
  4. **Hold locks for the entire operation** — composing thread-safe ops isn't thread-safe.
  5. **Hold locks for the shortest possible duration** — long locks cause synchronization/starvation.
  6. **Don't change thread priority or processor affinity.**
  - The tension: #4 vs #5. Aim for the middle; when impossible, **prefer longer locks** — race conditions (wrong results) beat synchronization (slow results).
- **Acquire/release semantics & memory model**: acquiring a lock has *acquire semantics* ("don't move reads earlier") and gives up-to-date values; releasing has *release semantics* ("don't move writes later") and flushes changes to memory. A *memory barrier* blocks both directions.
  - When to use: understanding why locks fix visibility, not just mutual exclusion.
  - How: if you always lock around shared data, reordering "just works" — no need for `volatile`.

## Key Concepts
- **Partial update**: another thread sees a half-written value. Happens even on single assignments — `Guid` (struct, member-wise copy), `decimal` (128-bit → two 64-bit writes), `long` on 32-bit systems.
- **Memory access reordering**: compiler/CPU reorder & eliminate memory ops as long as *single-threaded* results are unchanged — which silently destroys hand-rolled flag synchronization.
- **`volatile`**: does NOT do what you think — doesn't guarantee latest value, adds problems. Don't use it.
- **Deadlock**: threads waiting in a cycle (A↔B, or a ring, or a thread re-acquiring a non-recursive lock).
- **Recursive lock**: `lock`/`Mutex` allow the same thread to re-acquire (release equally many times); `Semaphore`/exclusive files do not → self-deadlock.
- **Race condition**: result depends on uncontrollable timing.
- **Synchronization**: parallel work forced sequential (sometimes desired — e.g. bank transactions).
- **Starvation**: one thread/group monopolizes a resource (long-held lock, or higher priority + affinity), starving others.

## Mental Models
- Think "a lock is a memory barrier, not just a mutex" — it both excludes *and* publishes memory.
- Think of lock hierarchy as a global total order every code path must respect, even when it's inconvenient.
- Race condition vs synchronization = "wrong but fast" vs "right but slow" — when forced, pick slow.

## Worked Example
Deadlock from inconsistent lock order, and the hierarchy fix:

```csharp
// BUG: Multiply locks left→right, Add locks right→left → deadlock under contention
public int Multiply() { lock(_leftOperandLock)  { lock(_rightOperandLock) { return _left * _right; } } }
public int Add()      { lock(_rightOperandLock) { lock(_leftOperandLock)  { return _left + _right; } } }

// FIX: both acquire in the SAME order (lock hierarchy: left before right)
public int Add()      { lock(_leftOperandLock)  { lock(_rightOperandLock) { return _left + _right; } } }
```

Rule #3 — a `DivideByZero` *event* invoked while holding operand locks can deadlock against a caller that locks `_outputLock`. Fix: release locks first, invoke the event last:

```csharp
public int Divide() {
    lock(_leftOperandLock) lock(_rightOperandLock) {
        if (_right != 0) return _left / _right;      // compute inside locks
    }
    DivideByZeroEvent?.Invoke(this, EventArgs.Empty); // foreign code AFTER releasing locks
    return 0;
}
```

Rule #4 — two short locks aren't one lock; `Add` and `SetOperands` each lock one operand at a time and interleave into a partial update. Rule #5/starvation — a thread that takes a lock *before* an infinite loop writes only `-`; the other never runs.

**What it demonstrates**: consistent order kills deadlocks; foreign code must run outside locks; and splitting one operation into two short locks re-introduces the very partial update locks were meant to prevent.

## Anti-patterns
- **`lock(this)` / exposing the lock object**: external code may lock the same object → deadlock. Use a private `object`/`Lock`.
- **Hand-rolled boolean flag synchronization**: reordering/caching eliminate it; use real locks.
- **`volatile` as a fix**: it isn't one.
- **Locking right-then-left in one method, left-then-right in another**: classic deadlock.
- **Calling events/virtual/delegate code while holding a lock**: unknown locks → deadlock.
- **Breaking lock order "to avoid unnecessary locking"**: reintroduces deadlock; if you must go out of order, release and re-acquire in order (and re-check state).
- **Changing priority/affinity**: starvation; Windows anti-starvation and Linux ignoring priority both prove it's unreliable.

## Key Takeaways
1. Lock every access to shared data — reads included — for both exclusion and memory visibility.
2. Establish and always honor a single lock order (lock hierarchy).
3. Never invoke foreign code while holding a lock.
4. Hold a lock for the whole logical operation; composing thread-safe ops isn't thread-safe.
5. But hold locks briefly to avoid synchronization/starvation — when 4 and 5 conflict, favor correctness (longer).
6. Even single assignments (`decimal`, `long` on 32-bit, structs) can partial-update.
7. Don't touch `volatile`, thread priority, or processor affinity.

## Connects To
- **Ch 4**: introduced `lock`, deadlock, `Interlocked`, priority dangers.
- **Ch 8**: strategies (queues, producer/consumer) that avoid manual locking.
- **Ch 13**: thread-safe/immutable collections that encapsulate correct locking.
- **Ch 11**: async deadlocks (`ConfigureAwait(false)`).
