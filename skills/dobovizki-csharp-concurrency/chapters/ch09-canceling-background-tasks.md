# Chapter 9: Canceling Background Tasks

## Core Idea
There is no safe built-in way to stop a thread — `Abort` is gone, `IsBackground` only helps on exit. `CancellationToken` is the .NET standard: at heart just a thread-safe, abuse-resistant boolean flag that *cooperatively* signals code to stop itself.

## Frameworks Introduced
- **`CancellationTokenSource` / `CancellationToken`** (the split-flag pattern): the *source* controls/triggers cancellation; the *token* is handed to cancelable code, which only *checks* it. This split (derived here from a hand-built `CancelFlag`/`CancelFlagSource`) stops callees from canceling each other.
  - When to use: any cancelable operation — the universal .NET convention.
  - How: `var cts = new CancellationTokenSource(); pass cts.Token; ... cts.Cancel();` Cancelable code polls `token.IsCancellationRequested`.
- **Cooperative cancellation** (three ways to react):
  1. **Poll + return**: `if (token.IsCancellationRequested) return;` — clutters code, consumes the return value.
  2. **Throw**: `token.ThrowIfCancellationRequested()` (throws `OperationCanceledException`) — cleaner, no `if` at each call site, preserves return values.
  3. **Register a callback**: `token.Register(() => legacyApi.Cancel());` for APIs you can't insert checks into.
- **Timeouts**: `cts.CancelAfter(TimeSpan.FromSeconds(30))` — built-in. Re-calling resets the timer; `CancelAfter(-1)` cancels the timeout; calling after cancellation does nothing.
- **Linked tokens**: `CancellationTokenSource.CreateLinkedTokenSource(tokenA, tokenB, …)` — the new source's token cancels if *any* input cancels. Lets you add a timeout to a token you were only *given*.

## Key Concepts
- **Cooperative, not preemptive**: a token can't force-stop anything; long uninterrupted work delays cancellation until it checks (a 1-minute inner loop → up to 1-minute lag). Thread cancellation checks into inner methods.
- **Why a raw `bool` flag fails**: per-core CPU cache + compiler reordering (Ch 7) mean a plain flag may never propagate; wrap access in a lock — or use the encapsulated `CancellationToken`.
- **`Register` callback runs on the *canceling* thread** (the one calling `Cancel`), not the background thread — keep it thread-safe and quick.
- **`CancellationToken.None`**: a token that never cancels (for APIs that demand one). `new CancellationToken(true)`: already-canceled — useful in unit tests.

## Mental Models
- Think "a token is a shared boolean with good manners" — no magic, doesn't know how to stop work.
- Source = the remote control; token = the "please stop when convenient" note the worker keeps checking.
- Throwing `OperationCanceledException` turns scattered `if`-checks into one exception path.

## Worked Example
The evolution flag → locked flag → encapsulated → `CancellationToken`, plus cooperative long-op:

```csharp
// The standard shape
var cts = new CancellationTokenSource();
var token = cts.Token;
new Thread(() => BackgroundProc(token)).Start();
Console.ReadKey();
cts.Cancel();                       // request cancellation

void BackgroundProc(CancellationToken token) {
    int i = 0;
    while (true) {
        token.ThrowIfCancellationRequested();   // cleaner than: if (token.IsCancellationRequested) return;
        Console.WriteLine(i++);
    }
}

// Long inner op must check periodically or cancellation lags up to its full duration
bool Calculate(CancellationToken token) {
    var start = DateTime.UtcNow;
    while ((DateTime.UtcNow - start).TotalMinutes < 1) {
        if (token.IsCancellationRequested) return false;   // inner check
        /* work */
    }
    return true;
}
```

Add a timeout to a token you were only given, via a linked source:

```csharp
public async Task<string> GetTextFromServer(CancellationToken canceledByUser) {
    using var combined = CancellationTokenSource.CreateLinkedTokenSource(canceledByUser);
    combined.CancelAfter(TimeSpan.FromSeconds(30));   // user-cancel OR 30s timeout
    using var http = new HttpClient();
    return await http.GetStringAsync("http://example.com", combined.Token);
}
```
**What it demonstrates**: the source/token split, `ThrowIfCancellationRequested` for clean cooperative cancellation, the need to check inside long inner work, and linking to combine cancel-reasons.

## Anti-patterns
- **`Thread.Abort`**: removed — throws `PlatformNotSupportedException` in .NET Core/5+; could corrupt state mid-operation.
- **`IsBackground = true` as your cancellation strategy**: only works on full program exit and kills the thread mid-op.
- **A plain unlocked `bool` cancel flag**: cache/reordering can delay or eliminate the check (fails in release, on many-core servers).
- **Sharing one cancel flag across independent operations**: one canceling itself cancels the others — split source from token.
- **Assuming a token stops work by itself**: it's cooperative; without checks, nothing stops.
- **Heavy/unsafe work in a `Register` callback**: it runs on the canceling thread.

## Key Takeaways
1. `CancellationToken` is the standard, cooperative cancellation mechanism — just a well-wrapped flag.
2. `CancellationTokenSource` triggers; the `CancellationToken` only checks — keep them separate.
3. Prefer `ThrowIfCancellationRequested()` over manual `if`-return.
4. Check the token inside long-running inner work or cancellation lags.
5. `CancelAfter` implements timeouts; `CreateLinkedTokenSource` combines cancel reasons.
6. Use `Register` for non-token legacy APIs; `CancellationToken.None` when an API requires a token you'll never cancel.

## Connects To
- **Ch 7**: why an unprotected flag fails (caching, reordering) → locks.
- **Ch 8**: cancelling the background/parallel processing built there.
- **Ch 3**: `...Async(…, CancellationToken)` overloads throughout .NET.
- **Ch 12**: `OperationCanceledException` and async exception handling.
