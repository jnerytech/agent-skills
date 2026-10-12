# Chapter 11: Controlling on Which Thread Your Asynchronous Code Runs

## Core Idea
Where code after `await` runs is governed by `SynchronizationContext` and `TaskScheduler`, not magic. UI frameworks install a context so `await` returns to the UI thread; `ConfigureAwait(false)` opts out of that — useful in libraries, harmful in application/UI code.

## Frameworks Introduced
- **The real rules for where code after `await` runs** (in order):
  1. **Task already complete** → continues on the *same thread* immediately. `ConfigureAwait(false)` has no effect here.
  2. **Current thread has a `SynchronizationContext`** (and no `ConfigureAwait(false)`) → uses it (UI thread, ASP.NET Classic request).
  3. **Current task has a `TaskScheduler`** (and no `ConfigureAwait(false)`) → uses it.
  4. Otherwise (or `ConfigureAwait(false)`) → **thread pool**.
  - Simplified: UI thread → same thread; ASP.NET Classic → same thread; everything else (console, ASP.NET Core, pool, `Thread`-class threads) → thread pool.
- **`SynchronizationContext`**: .NET's generic "run this code on that thread" abstraction (`Post` = don't wait, `Send` = wait; `await` uses only `Post`). Associated via `SetSynchronizationContext`, read via `.Current`. WinForms/WPF/ASP.NET Classic install one; console/ASP.NET Core leave it null.
  - When to use: understanding thread affinity; writing a custom single-thread context.
- **`ConfigureAwait(false)`**: makes `await` ignore the current `SynchronizationContext`/`TaskScheduler` → continuation on the thread pool.
  - When to use: **library code that doesn't care about context** — on *every* await. **Not** in application/UI code.
  - Debunked myths: it does NOT mean "same thread vs another thread" — without a context you already leave the thread; and on an already-completed task it does *nothing*.
  - To *leave* the current context deliberately, use `Task.Run`, not `ConfigureAwait(false)` (which no-ops on completed tasks).
- **`Task.Yield`**: the async equivalent of `Application.DoEvents` — `await Task.Yield()` queues the continuation at the end of the input queue so pending UI events run, keeping the app responsive.

## Key Concepts
- **The async/blocking deadlock**: UI thread blocks on `.Result` while the awaited continuation needs the UI thread → deadlock. Fixes: (a) use `await` instead of `.Result` (best); (b) `ConfigureAwait(false)` *inside the library method* so it resumes on the pool; (c) `Application.DoEvents` loop (pumps messages, but 100% CPU).
- **Why non-UI `await` switches threads**: a `Thread`-class thread returns/terminates at the await (no way to re-enter it), so the continuation goes to the pool.
- **`TaskScheduler`**: the async infrastructure under `await`; `.Default` = thread pool; `FromCurrentSynchronizationContext()` wraps a context. Can't set "current", but can pass to `Task.Run`/`ContinueWith`.
- **.NET 8 `ConfigureAwaitOptions`**: `None` (= `false`, worse-named), `ContinueOnCapturedContext` (default), `ForceYielding` (always yield to pool), `SuppressThrowing` (only post-first-await errors; throws on `Task<T>`). Author: avoid; stick with `ConfigureAwait(bool)` (the new form isn't even supported on `ValueTask`).

## Mental Models
- Think "`await` returns to a *SynchronizationContext*, not a *thread*" — no context set = pool, even without `ConfigureAwait(false)`.
- `ConfigureAwait(false)` = "I don't care about the UI/request context" — a library promise, not a deadlock cure-all.
- A completed task's continuation is inline — that's why `ConfigureAwait(false)` and `ForceYielding` matter for "always returns completed" methods.

## Worked Example
The classic deadlock and three fixes:

```csharp
// DEADLOCK: UI thread blocks on .Result; continuation needs the UI thread
private void button1_Click(object s, EventArgs e) {
    var task = DoSomething();
    label1.Text = task.Result;                 // blocks UI thread
}
private async Task<string> DoSomething() {
    await Task.Delay(500);                      // continuation wants UI thread → stuck
    return "done";
}

// FIX 1 (best): await, don't block
private async void button1_Click(object s, EventArgs e) => label1.Text = await DoSomething();

// FIX 2 (library): ConfigureAwait(false) INSIDE DoSomething → resumes on pool, .Result unblocks
private async Task<string> DoSomething() { await Task.Delay(500).ConfigureAwait(false); return "done"; }
```

`ConfigureAwait(false)` *everywhere* breaks the UI update — you must marshal back manually, which defeats `await`:

```csharp
private async void button1_Click(object s, EventArgs e) {
    var result = await DoSomething().ConfigureAwait(false);   // now off the UI thread
    label1.BeginInvoke((Action)(() => label1.Text = result)); // forced back — looks like pre-await code
}
```
**What it demonstrates**: the deadlock is "UI waits for UI"; the cleanest fix is `await` not `.Result`; `ConfigureAwait(false)` belongs *inside context-agnostic library methods*, not on UI-touching application awaits.

## Anti-patterns
- **`ConfigureAwait(false)` on every await in application/UI code**: forces manual `BeginInvoke`, negates async's benefits; Microsoft says libraries only.
- **Mixing `await` with `.Result`/`.Wait()` on a context-bound thread**: deadlock.
- **Believing `ConfigureAwait(false)` always switches threads**: no-op on completed tasks; irrelevant without a context.
- **Using the .NET 8 `ConfigureAwaitOptions`** in normal code: misleading names, not on `ValueTask`.
- **Long loops on the UI thread without `Task.Yield`/`DoEvents`**: frozen UI.

## Key Takeaways
1. `await` returns to a `SynchronizationContext`/`TaskScheduler`, else the thread pool — an already-complete task stays inline.
2. UI/ASP.NET-Classic install a context so `await` resumes on the right thread; console/ASP.NET Core don't.
3. `ConfigureAwait(false)` = ignore the context → pool. Libraries: yes (every await); application/UI: no.
4. The async/blocking deadlock is best fixed by `await` (not `.Result`), not by blanket `ConfigureAwait(false)`.
5. To leave a context on purpose, use `Task.Run`, not `ConfigureAwait(false)`.
6. `await Task.Yield()` keeps a UI loop responsive (async `DoEvents`).
7. Avoid the .NET 8 `ConfigureAwaitOptions`; use `ConfigureAwait(bool)`.

## Connects To
- **Ch 5**: introduced the where-does-await-run rules; UI thread marshaling.
- **Ch 3**: `await` ≈ `ContinueWith` — the "more complicated" part is this chapter.
- **Ch 8**: `BlockingCollection` work queue reused to build the custom `SynchronizationContext`.
- **Ch 12**: exception differences when using `await` vs `.Result`.
