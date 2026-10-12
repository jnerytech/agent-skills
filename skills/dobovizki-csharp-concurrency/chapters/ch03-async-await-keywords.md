# Chapter 3: The async and await Keywords

## Core Idea
`Task`/`Task<T>` are the "`IEnumerable<T>` of async" — the standard representation of a future event/value. `async` just flags a method for chunk-splitting; `await` doesn't wait — it ends the current chunk and returns control to the caller, resuming later via the task's continuation.

## Frameworks Introduced
- **Task = future event, Task<T> = future value**: a `Task` represents an event that may happen later (completion); `Task<T>` adds the value it produces. Elsewhere called *future*/*promise*/*deferred*. A Task is **not** a thread or a background operation — it only signals when one ends.
  - When to use: any API returning `Task`; reasoning about what a task does/doesn't give you.
  - How: a task is **completed** when it is `RanToCompletion`, `Canceled`, or `Faulted`.
- **Three ways to consume a Task**:
  - **"Are we there yet?" (polling)** — loop on `IsCompleted`/`Status`, doing *other work* between checks. Rare; only worth it when you have work to do and can't release the thread (e.g. UI thread).
  - **"Wake me up when we arrive"** — pass a callback to `ContinueWith(t => …)`; the task calls you on completion. This is the model `async/await` uses.
  - **Synchronous** — `Wait()` / `.Result` block the thread until done. Inefficient, can **deadlock**; use only to bridge into legacy sync code.
- **The async/await compiler transform**: `async` marks the method; the compiler splits it at each `await` into a **single state-machine method** (a `switch` on a position variable, not separate methods) driven by an internal **awaiter** (conceptually `ContinueWith`). Locals become fields on the state-machine object.
  - When to use: debugging async; understanding why code before the first `await` runs synchronously.
  - How: everything before the first `await` runs on the calling thread inline; `await` ends the chunk and returns; the continuation resumes the next chunk when the awaited task completes.

## Key Concepts
- **Polling**: repeatedly checking `IsCompleted` — only acceptable with real work between checks; otherwise wastes a thread AND CPU cycles.
- **`IsCompleted`**: true even if faulted/canceled — one check beats testing three `Status` values.
- **`IsFaulted` / `IsCanceled` / `IsCompletedSuccessfully`**: post-completion status checks (safe before completion — just return false).
- **`AggregateException`**: a faulted task wraps errors in `.Exception` as `AggregateException`; the real error is in `.InnerExceptions[0]` (plural — not the inherited singular `InnerException`).
- **`async void`**: legal only for event handlers (which must return void); caller can't await it or see its exceptions.
- **`ValueTask`/`ValueTask<T>`**: a struct holding the value directly when available synchronously, or a `Task<T>` reference otherwise.

## Mental Models
- Think "`async` = compiler flag, `await` = 'end chunk, return to caller, resume later.'" Neither creates a thread.
- Think of a Task as a *receipt* for a future result, not the worker doing the job.
- `Wait()` after completion is free and safe — it's only blocking *before* completion that's dangerous.

## Worked Example
The whole point — synchronous BMP-width reader vs its async version, changes minimal:

```csharp
// Async version — differs only by async, Task<int>, and await
public async Task<int> GetBitmapWidth(string path) {
    using (var file = new FileStream(path, FileMode.Open, FileAccess.Read)) {
        var fileId = new byte[2];
        var read = await file.ReadAsync(fileId, 0, 2);
        if (read != 2 || fileId[0] != 'B' || fileId[1] != 'M')
            throw new Exception("Not a BMP file");
        file.Seek(18, SeekOrigin.Begin);
        var widthBuffer = new byte[4];
        read = await file.ReadAsync(widthBuffer, 0, 4);
        if (read != 4) throw new Exception("Not a BMP file");
        return BitConverter.ToInt32(widthBuffer, 0);
    }
}
```

The same logic hand-written with `ContinueWith` becomes an unreadable, right-drifting mess that also breaks `using`, `return`, and `throw` — which is exactly what `async/await` fixes. Correct `async void` handler wraps everything in try/catch:

```csharp
private async void Button1_Click(object sender, EventArgs ea) {
    try {
        var text = await File.ReadAllTextAsync("source.txt");
        await File.WriteAllTextAsync("dest.txt", text);
    } catch (Exception ex) { /* handle — nobody else can */ }
}
```
**What it demonstrates**: async code reads like the synchronous logical flow while running as chunked continuations; `async void` must self-handle exceptions because no Task carries them out.

## Anti-patterns
- **`.Result` / `.Wait()` to block on a task**: negates async, wastes a thread, risks deadlock. (Safe only *after* completion.)
- **Tight `IsCompleted` polling loop with no work between checks**: burns a thread and CPU.
- **`async void` anywhere but an event handler**: caller can't observe completion or exceptions.
- **Throwing from `async void`**: the exception escapes to nowhere and likely crashes the app — catch everything inside.
- **Using a plain `Dictionary` as an async cache**: not thread-safe (see Ch 13).

## Key Takeaways
1. `Task` = future event; `Task<T>` = future value; "completed" includes canceled/faulted.
2. `async` only enables chunk-splitting; without an `await` the method runs fully synchronously (just wrapping the return in a Task).
3. `await` ends the current chunk and returns to the caller — it does not block.
4. Prefer `await` over `ContinueWith`; prefer both over `.Result`/`.Wait()`.
5. `async void` → only for event handlers, and catch all exceptions inside.
6. Return `ValueTask<T>` from often-synchronous hot methods to avoid allocating a `Task` on the fast path.
7. A faulted task's error lives in `AggregateException.InnerExceptions[0]`.

## Connects To
- **Ch 2**: same chunk-splitting state machine as `yield return`.
- **Ch 4–5**: *where* the continuation runs — the multithreading half of the story.
- **Ch 12**: exceptions, `AggregateException`, async void in depth.
- **Ch 13**: thread-safe collections for async caches.
