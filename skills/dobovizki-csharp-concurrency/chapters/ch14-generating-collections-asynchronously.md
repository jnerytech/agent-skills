# Chapter 14: Generating Collections Asynchronously — await foreach and IAsyncEnumerable

## Core Idea
`IAsyncEnumerable<T>` + `await foreach` are the async twins of `IEnumerable<T>` + `foreach`: they let you `yield return` from an `async` iterator and consume asynchronously-produced sequences (streams, channels) with the same clean loop syntax.

## Frameworks Introduced
- **`IAsyncEnumerable<T>` / `IAsyncEnumerator<T>`**: async versions of the enumeration interfaces. `GetAsyncEnumerator()` (returns quickly, not itself async); `MoveNextAsync()` returns `ValueTask<bool>`; `DisposeAsync()` returns `ValueTask`.
  - When to use: any sequence where *getting the next item* is asynchronous (stream/network/channel reads).
- **`await foreach`**: `foreach` that adds an `await` at each iteration.
  - How: `await foreach (var x in collection) {...}` → `await using` the enumerator + `while (await enumerator.MoveNextAsync())`.
- **Async `yield return`**: mark an iterator `async` and return `IAsyncEnumerable<T>` → you can `await` *and* `yield return` in the same method. Compiler applies both the Ch 2 (yield state machine) and Ch 3 (await) transforms.
- **Cancellation**: `GetAsyncEnumerator` takes an optional token, but `await foreach` hides the call. Bridge with `.WithCancellation(token)` on the consumer side, and `[EnumeratorCancellation]` on the generator's token parameter so the compiler wires it through.
- **`ToBlockingEnumerable()`**: wraps an `IAsyncEnumerable<T>` as a blocking `IEnumerable<T>` for non-async code — equivalent to `Wait()` per item; can deadlock, last resort.
- **`ConfigureAwait` on `IAsyncEnumerable<T>`**: applies `ConfigureAwait` to every `MoveNextAsync` (Ch 11 rules).

## Key Concepts
- **`foreach` is sugar** for `GetEnumerator` + `while(MoveNext())`; `await foreach` just inserts the `await`.
- **`yield return` can't live inside a `try`**: when catching (e.g. `ChannelClosedException`), assign inside try, `yield return` outside.
- **Cancellation is still cooperative**: `WithCancellation` before an already-canceled loop still yields the first value — nobody checks the token until the first `await` (e.g. `Task.Delay(..., token)`).
- **No built-in async LINQ** (as of .NET 9): use the RX team's `System.Linq.Async` NuGet.
- **Channel → BlockingCollection-like ergonomics**: wrap `Channel<T>` in a `GetAsyncConsumingEnumerable()` so consumers use `await foreach` instead of a `while(true)`+exception loop.

## Mental Models
- Think "`await foreach` = `foreach` with an `await` bolted onto `MoveNext`."
- An `async IAsyncEnumerable<T>` method is the Ch 2 iterator state machine *and* the Ch 3 async state machine composed.
- `WithCancellation` is the plumbing that carries a token across the compiler-generated `GetAsyncEnumerator` call you can't touch.

## Worked Example
Async stream reader — the async version differs only by keywords:

```csharp
// Async: IEnumerable→IAsyncEnumerable, Read→ReadAsync, foreach→await foreach
private async IAsyncEnumerable<int> GetNumbers(Stream stream) {
    var buffer = new byte[4];
    while (await stream.ReadAsync(buffer, 0, 4) == 4)
        yield return BitConverter.ToInt32(buffer);
}
public async Task ProcessStream(Stream stream) {
    await foreach (var number in GetNumbers(stream))
        Console.WriteLine(number);
}
```

An async, `await foreach`-able queue over `Channel<T>` (note yield return *outside* the try):

```csharp
public class ChannelAsyncCollection<T> {
    private Channel<T> _channel = Channel.CreateUnbounded<T>();
    public void Add(T item) => _channel.Writer.TryWrite(item);
    public void CompleteAdding() => _channel.Writer.Complete();
    public async IAsyncEnumerable<T> GetAsyncConsumingEnumerable() {
        while (true) {
            T next;
            try { next = await _channel.Reader.ReadAsync(); }
            catch (ChannelClosedException) { yield break; }   // signals "no more items"
            yield return next;                                 // must be outside the try
        }
    }
}
// Consumer: 10 workers, clean loop
workers[i] = Task.Run(async () => {
    await foreach (var v in asyncCollection.GetAsyncConsumingEnumerable()) { /* process v */ }
});
```
**What it demonstrates**: async iterators turn a stream/channel into an `await foreach`-friendly sequence, giving `Channel<T>` the clean `GetConsumingEnumerable` ergonomics that `BlockingCollection` had but without blocking.

## Anti-patterns
- **`yield return` inside a `try`**: won't compile — assign in try, yield after.
- **Expecting `WithCancellation` to stop iteration by itself**: token is a flag; the generator must actually observe it (pass it to the awaited call).
- **`ToBlockingEnumerable()` in async-capable code**: blocks per item, can deadlock — only to bridge to legacy sync code.
- **Forgetting `[EnumeratorCancellation]`**: the compiler won't route the token into the generator.
- **`async void` iterator consumers**: make the consuming method `async Task`, not `async void` (Ch 3).

## Key Takeaways
1. `IAsyncEnumerable<T>`/`await foreach` = async `IEnumerable`/`foreach`; `MoveNextAsync` returns `ValueTask<bool>`.
2. An `async` method returning `IAsyncEnumerable<T>` can both `await` and `yield return`.
3. `await foreach` is `foreach` with an `await` on each `MoveNext`.
4. Cancel via `.WithCancellation(token)` + `[EnumeratorCancellation]`; it's still cooperative.
5. `yield return` can't sit inside a `try` — yield outside.
6. Wrap `Channel<T>` in an async iterator to regain `GetConsumingEnumerable`-style loops.
7. Async LINQ needs the `System.Linq.Async` NuGet; `ToBlockingEnumerable` bridges to sync code (with `Wait`'s risks).

## Connects To
- **Ch 2**: `yield return` iterator state machine — reused, now async.
- **Ch 3**: the `await` transform composed on top; `ValueTask`.
- **Ch 8/13**: `BlockingCollection` work queue and `Channel<T>` — this chapter gives `Channel` the clean loop.
- **Ch 9**: `CancellationToken` cooperative model behind `WithCancellation`.
- **Ch 11**: `ConfigureAwait` semantics applied per iteration.
