# Chapter 1: Asynchronous Programming and Multithreading

## Core Idea
Multithreading and asynchronous programming both let a computer do useful work while it would otherwise wait — but they solve it differently: threading interleaves work; async frees the thread during out-of-CPU operations. Combined, they let one server handle thousands of clients.

## Frameworks Introduced
- **The Pizzeria Metaphor**: cook = CPU, pizza baking = blocking I/O, oven beep = async callback.
  - When to use: reasoning about *why* a technique helps before touching code.
  - How: single-threaded synchronous (cook waits at oven) → multithreaded (cook timer-switches between pizzas, pays context-switch tax) → async (cook starts next pizza while first bakes, checks oven when free) → async+threads (oven beeps → any free cook handles it).
- **Blocking vs Nonblocking operations**: a *blocking operation* (file/network/anything outside CPU+memory, or waiting on another thread) parks the thread in a **blocked state** — OS gives it no CPU until the op finishes. A *nonblocking (async)* op queues the work with the OS/device and returns immediately, freeing the thread.
  - When to use: deciding whether a call wastes a thread.
  - How: if it touches disk, network, or another thread → it can block → prefer an async variant.

## Key Concepts
- **Thread**: one sequence of operations that can run in parallel with others; has real memory + management overhead.
- **Context switch**: CPU saving one thread's state and loading another's — pure overhead, paid every switch.
- **Blocked state**: OS parks a thread doing a blocking op; assigns it no CPU until the op completes.
- **Multicore CPU**: N single cores on one chip → N threads *truly* simultaneous, but shared resources raise interference risk.
- **Thread affinity**: pinning a thread to a specific core — almost always a mistake; don't.
- **Serverless / cloud efficiency**: you pay per resource used, so shaving time per request directly saves money.

## Mental Models
- Think of a CPU as *mostly idle*, waiting on slower components — async's job is to reclaim that wait time.
- Multithreading buys throughput under waiting-heavy loads but taxes you with overhead "every step of the way."
- Multicore cuts *processing* time, not *waiting* time — so it never halves total latency for I/O-bound work.
- "The Free Lunch Is Over" (Herb Sutter): single-core speed stopped doubling → performance now comes only from concurrency.

## Anti-patterns
- **A thread per connection at scale**: fine for low/medium load; at thousands of connections the thread overhead slows or crashes the server.
- **Pinning thread affinity**: removes the scheduler's freedom to move threads between cores for no real gain.
- **Assuming more cores = proportionally faster**: waiting time doesn't shrink with cores.

## Code Examples
*(Chapter 1 is conceptual — no code. First code appears in Ch2.)*

## Key Takeaways
1. Multithreading = fast switching to fake simultaneity; async = don't wait, get notified.
2. A blocked thread costs memory but no CPU; a thread pool + async avoids holding threads during I/O.
3. Multicore parallelizes processing, not waiting — I/O-bound gains come from async, not more cores.
4. Async alone (single thread) can beat multithreading for I/O-bound servers, and is the most performant option in this chapter's diagrams.
5. Combine async + threads: callback on completion runs on a thread-pool thread because the original thread moved on.
6. In the cloud you pay per use, so efficiency is money.

## Connects To
- **Ch 2**: how the compiler rewrites code (lambdas, yield) — the same machinery behind async/await.
- **Ch 4**: multithreading mechanics in C#.
- **Ch 5**: how async/await and multithreading actually interact.
