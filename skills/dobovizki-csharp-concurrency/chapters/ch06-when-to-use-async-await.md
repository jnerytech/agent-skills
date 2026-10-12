# Chapter 6: When to Use async/await

## Core Idea
async/await's three big wins (higher load, fewer resources, easy thread-marshaling) usually outweigh its costs — but it is contagious, adds edge cases, and is expensive vs single-threaded code. Use it deliberately, guided by a priority-ordered decision list.

## Frameworks Introduced
- **The async decision list (priority-ordered — earlier wins ties)**:
  1. Managing **many simultaneous connections** → use async wherever you can.
  2. Using an **async-only API** → use async there.
  3. **Native UI freezing** → make the specific long-running code async.
  4. **Thread-per-request + significant I/O** (network/file) → consider async.
  5. Adding to a codebase that **already uses async** → use it where sensible.
  6. Adding to a codebase that **doesn't** → avoid it (or refactor callers if you introduce it).
  7. Code that does **only one thing at a time** → don't use async.
  8. Everything else → weigh the trade-offs yourself.
  - When to use: choosing async vs blocking for a given piece of code.
- **The three benefits**: (a) handles higher load, (b) uses fewer resources even at low load, (c) makes multithreading-with-thread-affinity (UI) easy.

## Key Concepts
- **"Asynchronous all the way down" (contagion)**: any caller of async code must itself be async — the change propagates up to the entry point.
- **Async edge cases**: unfreezing the UI lets users re-trigger actions → new race-like bugs (e.g. mixing results from two clicks); fix by disabling controls during the operation.
- **Hidden multithreading**: outside WinForms, an added `await` can make code multithreaded (thread pool) without you realizing.
- **Cost**: `Thread.Sleep(1000)` decompiles to ~8 lines; `await Task.Delay(1000)` to ~63 — a full state-machine class. Expensive vs single-threaded, but still cheaper than non-async multithreading.

## Mental Models
- Think of async as a load/resource multiplier for I/O-bound servers: the benchmark shows the async server handling 2× the connections on a fraction of the threads.
- Think of the decision list as a tie-break hierarchy, not independent rules — the highest matching bullet dominates.
- "async is expensive *relative to single-threaded*, cheap *relative to threaded*" — don't pay it for one-thing-at-a-time code.

## Worked Example
The benchmark (static-file server, one laptop) — async wins decisively on threads and ceiling:

| Connections | Non-async failures | Non-async threads | Async failures | Async threads |
|---|---|---|---|---|
| 50 | 0 | 56 | 0 | 27 |
| 100 | 0 | 106 | 0 | 27 |
| 200 | 61 | (failed) | 0 | 27 |
| 300 | 168 | (failed) | 0 | 27 |

Non-async peaked ~130 connections; async ~300+. The *only* code difference:

```csharp
// One-thread-per-request → async: swap 4 calls + add async/await
var connection = await listenSocket.AcceptAsync();      // was Accept()
Task.Run(async () => {                                   // was new Thread(...)
    using var file = new FileStream("somefile.bin", FileMode.Open, FileAccess.Read);
    var buffer = new byte[1024 * 1024];
    while (true) {
        int read = await file.ReadAsync(buffer, 0, buffer.Length);   // was Read()
        if (read != 0) await connection.SendAsync(                    // was Send()
            new ArraySegment<byte>(buffer, 0, read), SocketFlags.None);
        else { connection.Shutdown(SocketShutdown.Both); connection.Dispose(); return; }
    }
});
```

Contagion fix — an async camera call forces the whole chain async:

```csharp
public async Task TakeSinglePicture() {         // was void
    cameraApi.AquireCamera();
    await cameraApi.TakePictureAsync();          // must await, or camera released mid-shot
    cameraApi.ReleaseCamera();
}
```
**What it demonstrates**: near-identical code, async holds threads flat (27) while blocking scales them linearly and collapses; and one async call ripples `async Task` up every caller.

## Anti-patterns
- **`.Wait()`/`.Result` to "escape" contagion**: risks deadlocks, some APIs throw, and it kills the async benefit.
- **Adding `await` to UI handlers without disabling controls**: re-entrant clicks produce inconsistent state.
- **Using async for strictly sequential, single-operation code**: pure overhead.
- **Sprinkling async into a synchronous codebase**: contagion spreads; either commit (refactor callers) or abstain.

## Key Takeaways
1. Three wins: higher load, fewer resources, easy UI thread-marshaling.
2. async is contagious — "all the way down" to the entry point.
3. Unfreezing the UI creates new re-entrancy bugs — disable controls during the op.
4. An added `await` can silently introduce multithreading outside UI frameworks.
5. async is expensive vs single-threaded (~8→63 lines) but cheaper than threaded blocking.
6. Follow the priority list; when only the last bullet fits, judge the trade-offs.

## Connects To
- **Ch 5**: the thread-affinity + Task.Run/UI mechanics behind the benefits.
- **Ch 7**: the multithreading pitfalls that "more edge cases" refers to.
- **Ch 3**: `ValueTask`, async void — cost-reduction and contagion details.
