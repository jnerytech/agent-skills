# Chapter 2: The Compiler Rewrites Your Code

## Core Idea
async/await is implemented mostly by the **C# compiler**, not the .NET runtime. Before tackling it, learn the same rewrite tricks on two simpler features — lambda functions and `yield return` — because "there is no magic; the compiler just writes code you could write yourself."

## Frameworks Introduced
- **Compiler code transformation**: the compiler rearranges your source so the emitted IL differs from what you wrote, to (a) cut boilerplate and (b) add features the runtime lacks.
  - When to use: understanding/debugging async behavior — the running code is not your source.
  - How: lambdas → hoisted methods (+ a class when they capture locals); `yield return`/`async` → a state-machine class split into chunks.
- **Closure hoisting (lambdas)**: a captured local variable is moved to a field of a compiler-generated class shared by the outer method and the lambda.
  - When to use: explaining why a captured variable behaves like shared mutable state.
  - How: compiler makes a hidden class, promotes the local to a field, both methods reference it. Multiple lambdas in one method share one class.
- **Coroutine / iterator state machine**: `yield return` compiles to a class implementing `IEnumerator<T>`, splitting your method at each `yield` into steps driven by `MoveNext()` and a `_step` field.
  - When to use: understanding lazy, suspend/resume evaluation — the direct precursor to async.
  - How: each chunk sets `Current`; `MoveNext` switch()es on `_step` to run the next chunk; returns false when done.

## Key Concepts
- **Coroutine**: code that can suspend, resume, and return multiple values. C# calls these *iterator methods* (`yield return`) and *async methods* (`async/await`).
- **`IEnumerable<T>`**: the universal "sequence of items" interface; its one job is to hand back an `IEnumerator<T>`.
- **`IEnumerator<T>`**: does the real work — exposes `Current` and `MoveNext()`.
- **Lazy generation**: with `yield return`, each value is produced only when requested, not all upfront.
- **Finite state machine**: the `_step`-driven `MoveNext` is exactly one.

## Mental Models
- Think of `yield return` as async/await minus the threading — same suspend/resume rewrite, no asynchrony.
- Think of a captured local as secretly a field on a hidden object, not a stack variable.

## Worked Example
Non-yield vs `yield return` — same output `Got 1 / Got 2`, different execution:

```csharp
// Eager: whole list built, then consumed
private IEnumerable<int> NoYieldDemo() {
    var result = new List<int>();
    result.Add(1); result.Add(2);
    return result;
}
// Lazy: each value produced on demand
private IEnumerable<int> YieldDemo() {
    yield return 1;
    yield return 2;
}
```

The compiler rewrites `YieldDemo` into an enumerator — conceptually:

```csharp
public class YieldDemo_Enumerator : IEnumerator<int> {
    public int Current { get; private set; }
    private void Step0() { Current = 1; }
    private void Step1() { Current = 2; }
    private int _step = 0;
    public bool MoveNext() {
        switch (_step) {
            case 0: Step0(); ++_step; return true;
            case 1: Step1(); ++_step; return true;
            case 2: return false;   // done
        }
        return false;
    }
    object IEnumerator.Current => Current;
    public void Dispose() { } public void Reset() { }
}
```
**What it demonstrates**: suspend/resume is faked by splitting the method into chunks and a `switch` that remembers which chunk runs next. async/await uses the exact same trick.

## Anti-patterns
- **Assuming compiled code mirrors your source**: it doesn't — hidden classes/methods/state machines appear. Debug with that in mind.
- **Expecting `yield return` to run eagerly**: it suspends at start and runs the minimum per requested value.

## Key Takeaways
1. async/await is a compiler feature; the runtime barely knows about it.
2. Lambdas → hidden methods; captured locals → fields on a hidden shared class.
3. `yield return` → an `IEnumerator<T>` state machine that runs one chunk per `MoveNext`.
4. `IEnumerable<T>` is the standard "sequence" contract so any consumer (`foreach`) works with any producer.
5. No magic: everything the compiler emits, you could hand-write with the same runtime access.

## Connects To
- **Ch 3**: async/await applies this same chunk-splitting to `Task`/`Task<T>`.
- **Ch 1**: this is the "how" behind the async "why."
