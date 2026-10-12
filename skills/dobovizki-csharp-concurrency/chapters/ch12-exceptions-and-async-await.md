# Chapter 12: Exceptions and async/await

## Core Idea
Exceptions travel the *call stack*, but async continuations don't run on the original stack. The compiler bridges this by catching post-await exceptions and stashing them in the returned `Task`, which `await` rethrows — so a forgotten `await` silently swallows the error.

## Frameworks Introduced
- **How async exceptions are captured**: for a method with an `await`, the compiler wraps post-await code in try/catch and calls `TrySetException` on the returned Task → its `Status` becomes `Faulted`, exception in `Task.Exception` (an `AggregateException`). `await` on that task rethrows.
  - When to use: debugging async failures, deciding whether to inspect `Task.Exception` vs let `await` throw.
  - Key split: **before the first `await`** → a *regular* thrown exception; **after the first `await`** → stashed in the Task. Every async method can fail *both* ways.
- **`await` vs `Task.Exception` for `AggregateException`**: `Task.Exception` is always an `AggregateException`. `await` unwraps and throws only the **first** inner exception (the rest are lost). If a task truly represents multiple parallel ops and you care about all failures, don't `await` — read `Task.Exception` yourself.
- **The rule for `async void`**: it has no Task to stash exceptions in, so a thrown exception bubbles into the `SynchronizationContext` → likely crash. **Catch all exceptions inside `async void`; never let one escape.**

## Key Concepts
- **Call stack vs source structure**: a `throw` textually inside a `try` (in a lambda/continuation) runs later on a different stack — the `try` doesn't catch it. The compiler duplicates try/catch into continuations to make `await` + try/catch *look* seamless.
- **`async` without `await`**: compiler adds no try/catch; the method throws like a normal method (only wrapping the return in a Task).
- **Lost exception**: if you call an async method and *don't* `await` (forgot it, or fire-and-forget), the compiler-caught exception sits in the ignored Task and is silently dropped — the runtime thinks it was handled.
- **Timing**: the continuation usually runs *after* the method returns, so a faulted task may still be `Running`/`WaitingForActivation` when returned and flip to `Faulted` later.

## Mental Models
- Think "an async method has two exit doors for errors — throw (pre-await) and faulted Task (post-await); `await` merges them into one."
- A forgotten `await` = a muted exception. "Code stops with no error shown" → suspect a missing `await`.
- `await` is lossy on `AggregateException` — it keeps only the first. Multi-failure = read `Task.Exception`.

## Worked Example
Where the exception lands, and how it gets lost:

```csharp
// Post-await throw → compiler stashes it in the Task (conceptually):
public async Task<int> MyMethod() {
    await File.ReadAllBytesAsync("file.bin");
    throw new NotImplementedException();     // caught by generated code → result.TrySetException(...)
}

// await unwraps AggregateException to the FIRST inner exception:
var tcs = new TaskCompletionSource();
tcs.SetException(new NotSupportedException());
Console.WriteLine(tcs.Task.Exception.GetType());  // AggregateException
try { await tcs.Task; }
catch (Exception ex) { Console.WriteLine(ex.GetType()); }  // NotSupportedException (inner)

// THE LOST EXCEPTION — missing await swallows the error:
async Task MethodThatThrows() { await Task.Delay(100); throw new NotImplementedException(); }
async Task Caller() {
    MethodThatThrows();          // no await → exception stashed in an ignored Task → silently gone
}
```
**What it demonstrates**: post-await exceptions live in the Task; `await` rethrows the *first* inner exception of the `AggregateException`; and without `await` nobody reads it, so it vanishes (invisible under "just my code").

## Anti-patterns
- **Forgetting `await` on a call that can fail**: the exception is caught by generated code and then dropped — invisible failure.
- **Throwing from / letting an exception escape an `async void`**: crashes via the SynchronizationContext. Wrap the body in try/catch.
- **`await`ing when you need *all* failures of a multi-op task**: only the first inner exception survives; read `Task.Exception` instead.
- **Assuming try/catch around registering a lambda/continuation catches its throw**: it doesn't — different stack.
- **Not handling both throw-forms when consuming a task without `await`** (e.g. `WhenAny`/`WhenAll` collections): check both the thrown exception and the faulted Task.

## Key Takeaways
1. Continuations don't share the caller's call stack; the compiler stashes post-await exceptions in the Task and `await` rethrows them.
2. Pre-first-await errors throw normally; post-await errors fault the Task — every async method can do both.
3. `Task.Exception` is always an `AggregateException`; `await` throws only its first inner exception.
4. A forgotten `await` silently loses the exception — a prime suspect when code stops with no error.
5. `async void` has no Task for exceptions → catch everything inside; never let one escape.
6. For genuine multi-failure tasks, inspect `Task.Exception` rather than `await`.

## Connects To
- **Ch 3**: `AggregateException`, async void, `await` ≈ `ContinueWith`.
- **Ch 10**: `TaskCompletionSource.TrySetException` — how faults get into a Task.
- **Ch 11**: `SynchronizationContext` — where an `async void` exception bubbles to.
- **Ch 2**: lambdas compiled to separate methods — why the `try` doesn't catch the throw.
