# Chapter 5: async/await and Multithreading

## Core Idea
The same tools (`Task`, `Task.Run`, `WhenAll`) drive both async and threads — but async I/O holds *no* thread while waiting, whereas `Task.Run` blocking I/O ties up a pool thread per operation. And `await` resumes on a thread of the *same type*, which is what makes UI code and locks work.

## Frameworks Introduced
- **Async I/O vs threaded blocking I/O**: `Task.Run(() => File.ReadAllBytes(...))` uses a pool thread that then *blocks* waiting on disk (up to N threads idle-blocked). `Task.Run(async () => await File.ReadAllBytesAsync(...))` uses a thread only to *start* the read, frees it during the wait, and grabs a thread again only when data arrives.
  - When to use: any I/O-bound parallel work — prefer the async form.
  - How: swap blocking calls for their `...Async` versions + `async`/`await`; make the caller async and use `await Task.WhenAll` (not `Task.WaitAll`) to free the caller's thread too.
- **Where code runs after `await`** (the key rule): `await` tries to resume on a thread of the *same type*; else the thread pool.
  - UI thread (WinForms/WPF/UWP) → resumes on the **same UI thread**.
  - ASP.NET Classic request → same thread. Custom `SynchronizationContext`/`TaskFactory` → uses those.
  - Everything else (thread-pool caller, ASP.NET **Core**, main thread of non-UI app, a `Thread`-class thread) → **thread pool** (possibly a different thread).
  - If the awaited task is *already complete*, execution usually continues inline with no thread switch.
- **Locks + await**: you **cannot** `await` inside a `lock` block — won't compile.
  - Why: conceptually, `await` runs unknown code while holding the lock (deadlock risk); practically, the resumed code may be on a different thread, but a `lock` must be released by the same thread that took it.
  - How: rearrange so `await` is *outside* the lock — hold the lock only around the shared-state access before and after the await.

## Key Concepts
- **`Task.WhenAll` vs `Task.WaitAll`**: `WhenAll` awaits asynchronously (frees the caller's thread); `WaitAll` blocks it.
- **Contagion of thread type**: an innocent `await` in non-UI code can silently make your code multithreaded.
- **Naive async cache**: locking only the dictionary accesses (not the await) means concurrent first-callers may both do the expensive call before the cache is populated — acceptable only if repeating the work is OK; use `[]` not `Add` to overwrite.

## Mental Models
- Think of async I/O as "reserve a thread only when there's CPU work to do" — not while waiting.
- Think of `await` on the UI thread as a bookmark that guarantees you resume *on the UI thread*, so post-await UI updates are legal.
- `await Task.Run(...)` is wasteful everywhere *except* offloading work from the UI thread — there it's the idiom.

## Worked Example
Offload long work from the UI thread and safely update the UI after:

```csharp
// WRONG: frozen UI (runs on UI thread)                | WRONG: no freeze, but crashes —
// result set, but nothing runs concurrently           | UI touched from a pool thread
private void MyButtonClick(object s, EventArgs e) {     | Task.Run(() => { var r = LongCalculation();
    MyLabel.Text = LongCalculation().ToString();       |                  MyLabel.Text = r.ToString(); });
}                                                      |  // exception!

// RIGHT: await Task.Run frees the UI thread, then resumes ON the UI thread
private async void MyButtonClick(object s, EventArgs e) {
    int result = 0;
    await Task.Run(() => { result = LongCalculation(); });  // background
    MyLabel.Text = result.ToString();                       // back on UI thread — safe
}
```

Lock rearranged around an await (the compiling, thread-safe cache):

```csharp
public async Task<string> GetResult(string query) {
    lock (_cacheLock) { if (_cache.TryGetValue(query, out var c)) return c; }
    var result = await new HttpClient().GetStringAsync("https://example.com?" + query);
    lock (_cacheLock) { _cache[query] = result; }   // await is OUTSIDE the lock
    return result;
}
```
**What it demonstrates**: `await` on the UI thread resumes on the UI thread (so UI updates are safe); and you protect shared state around the await, never across it.

## Anti-patterns
- **`await` inside `lock`**: compiler error — move the await out.
- **`Task.Run` blocking I/O for parallel reads**: ties up one thread per read while it waits; use async I/O instead.
- **`Task.WaitAll`/blocking the caller** when you could make the caller async and `WhenAll`.
- **Touching UI from a background thread**: throws; marshal back via `await` on the UI thread or `BeginInvoke`.

## Key Takeaways
1. Same tools for async and threads; async I/O uses far fewer threads because it holds none while waiting.
2. `await` resumes on a same-type thread (UI→UI), else the thread pool.
3. An already-completed awaited task usually continues inline with no thread switch.
4. You can't `await` inside a `lock`; rearrange so the await sits between two small locked regions.
5. `await Task.Run` is right *only* to offload the UI thread.
6. Make callers async + `WhenAll` to free their threads too.

## Connects To
- **Ch 3**: `await` ≈ `ContinueWith`, now with thread-affinity rules.
- **Ch 4**: threads, thread pool, `lock`.
- **Ch 11**: SynchronizationContext, `ConfigureAwait(false)`, deadlocks in detail.
- **Ch 13**: proper thread-safe/concurrent collections for caches.
