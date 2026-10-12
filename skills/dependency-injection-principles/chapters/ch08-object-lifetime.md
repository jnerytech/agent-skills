# Chapter 8: Object lifetime

## Core Idea

Object Composition is only half of DI; the other half is **managing the lifetime** of the Dependencies you compose. Once you accept Inversion of Control and let a **Composer** supply your Dependencies, you also surrender control over *when they are created and destroyed*. A consumer never creates its Dependencies (the Composer does) and, in a garbage-collected runtime, cannot explicitly destroy them either — it merely keeps them alive by holding a reference in a private field. So lifetime is a property the Composer decides, and it decides it well because "composing and managing components is its single responsibility."

The Composer has more influence over lifetime than any single consumer: by choosing whether to *share* an instance across consumers, it decides whether a Dependency dies with one consumer or lives until all consumers are gone. The authors formalize the intended lifetime of a Dependency as a **Lifestyle**. Getting Lifestyles wrong doesn't just waste memory — it produces resource leaks and concurrency bugs that only surface in production under concurrent load.

> **DEFINITION** A **Lifestyle** is a formalized way of describing the intended lifetime of a Dependency.

> **DEFINITION** A **Composer** is any object or method that composes Dependencies — often a DI Container, but also any Pure DI method that builds object graphs by hand. It is a core part of the Composition Root.

## Frameworks Introduced (the Lifestyle catalog)

The chapter's central artifact is the **catalog of three stock Lifestyles**. In most situations one of these is the right match, so knowing them in advance equips you for most challenges:

1. **Singleton Lifestyle** — a single instance is perpetually reused. Within one Composer there is exactly one instance; every request returns the same object. (Not the same as the GoF Singleton *design pattern* — the Singleton Lifestyle offers no global static access point, and two Composers yield two instances.)
2. **Transient Lifestyle** — a new instance is served every time it's requested. The safest but least efficient choice.
3. **Scoped Lifestyle** — at most one instance per type is served per an implicitly or explicitly defined scope (e.g., a web request). Behaves like a Singleton *within* the scope but is not shared across scopes; each scope has its own cache.

Supporting the catalog is a **Releasing** protocol: the Composition Root asks the Composer for a graph, uses it, then tells the Composer it's finished — the Composer decides which Dependencies to dereference/dispose and which to keep for reuse.

## Key Concepts

- **Lifetime follows from composition** — whether a Dependency is shared or private (a compose-time choice) *is* what determines its lifetime. Injecting one instance into two consumers means both must go out of scope before it can be collected.
- **Consumers can't manage lifetime** — they don't control creation (the Composer does) and can't force destruction (the GC does). They only keep a Dependency alive by referencing it.
- **Releasing ≠ Disposing** — *releasing* is the Composer deciding which Dependencies can be dereferenced and *possibly* disposed; a shared Dependency may be released by one consumer yet kept alive for others.
- **"disposing dependencies" is the Composer's job** — it alone knows when it created a disposable, so it alone knows when to dispose it. It must **track every disposable it served** and dispose in the **opposite order of creation** (outside-in), because an object may call its Dependencies during its own disposal.
- **Disposable Abstractions are a Leaky Abstraction** — putting `: IDisposable` on an interface is a design smell that leaks implementation detail into the contract and adds an unused member (an ISP violation). Model it on the *implementation*, not the Abstraction.
- **Ephemeral disposable** — an object with a clear, short lifetime not exceeding a single method call (e.g., a WCF channel, an ADO.NET command). Create it, use it, dispose it inside the method (via `using`); never inject it — inject a *factory* instead.
- **Mixing Lifestyles is allowed** — a graph can freely combine Singleton, Scoped, and Transient Dependencies, with one hard rule (below).
- **The lifetime rule** — a component may only reference Dependencies whose expected lifetime is **equal to or longer than its own**. Violating this creates a Captive Dependency.
- **Thread-safety drives the choice** — stateless services, immutable types, and deliberately thread-safe classes can be Singletons; anything not thread-safe must be Transient or Scoped.

## Mental Models

- **The sommelier** — you trust the sommelier to manage the wine cellar (buy, sample, match, hold bottles for years) far better than you could. Likewise, trust the Composer to manage Dependency lifetimes better than any consumer.
- **Three-phase composition** — structure a Pure DI Composition Root into distinct phases: (1) Singletons created at application start-up, (2) Scoped instances created at the start of each request, (3) the per-request graph mixing Transient/Scoped/Singleton. Separating the phases makes Captive Dependencies easy to spot.
- **The scope as an isolated bubble** — a "request" is broader than a web request: a dequeued work item, a button press, a timer tick. Give each its own bubble of Dependencies and operations run in isolation, even in parallel.
- **Wrap, don't leak** — when a Lifestyle concern (laziness, multiplicity) threatens to escape into a consumer's constructor, hide it inside the Composition Root behind a Virtual Proxy (`Lazy<T>`/`Func<T>`) or a Composite (`IEnumerable<T>`) that still implements the original Abstraction.

## Anti-patterns

**Captive Dependency** (a bug) — *What:* a short-lived Dependency is inadvertently kept alive too long because its consumer was given a longer lifetime (classically, a non-thread-safe Dependency injected into a Singleton). *Why it fails:* the Singleton pins the Dependency for the Composer's whole life, so a per-request, non-thread-safe object like an EF `CommerceContext`/`DbContext` gets reused across threads and requests, causing corruption/concurrency bugs that appear only under production load. *Fix:* enforce "reference only Dependencies whose lifetime ≥ your own"; use the three-phase Composition Root so Scoped things are created per request, not captured in Singleton fields; lean on DI Containers that analyze graphs to detect captives.

**Leaking disposables** (a bug) — *What:* a consumer disposes an *injected* Dependency (e.g., `OrderService : IDisposable` calling `repository.Dispose()`). *Why it fails:* the injected instance may be shared; disposing it destroys the Dependency out from under other consumers, throwing exceptions when they next use it. Conversely, ignoring a disposable Abstraction leaks resources. *Fix:* keep Abstractions non-disposable (disposable Abstractions are Leaky Abstractions); let the **Composer** track and release disposables in reverse creation order; for short-lived resources create/dispose them on demand behind a factory rather than holding a reference.

**Leaking Lifestyle choices** (design issue) — injecting `Lazy<T>`, `Func<T>`, or `IEnumerable<T>` into an application component pushes a Composition Root concern onto every consumer, complicating each consumer and its tests and forcing sweeping cascading changes. *Fix:* hide `Lazy<T>`/`Func<T>` behind a **Virtual Proxy** and a collection behind a **Composite**, both inside the Composition Root.

**Per-thread Lifestyle** (a bug) — tying a Dependency's lifetime to a thread (`[ThreadStatic]`) is error-prone: thread lifespans are unclear (pooled threads may outlive requests or be reused), and async frameworks resume a request on a *different* thread, so a thread-specific, non-thread-safe Dependency gets shared across concurrent requests. *Fix:* scope to the request/operation instead, storing Scoped Dependencies in local variables.

## Code Examples

```csharp
// Captive Dependency bug: a per-request, non-thread-safe DbContext
// captured inside a Singleton consumer.
public class Composer
{
    private readonly IProductRepository repository;   // stored => Singleton

    public Composer(string connectionString)
    {
        // SqlProductRepository becomes a Singleton, held for the app's life...
        this.repository = new SqlProductRepository(
            new CommerceContext(connectionString));   // ...capturing CommerceContext
    }
    // CommerceContext is now a Captive Dependency: not thread-safe,
    // not meant to be reused across threads/requests, yet effectively a Singleton.
}
```

**What it demonstrates:** How a Captive Dependency arises even in Pure DI — because `SqlProductRepository` is created once and holds `CommerceContext` in a private field, there is effectively one `CommerceContext` for the whole application, violating the rule that a component's Dependencies must live at least as long as the component.

```csharp
// Fix: three-phase Pure DI. Singletons at start-up; Scoped per request;
// the graph assembled from all three, so nothing short-lived is captured.
public class CommerceControllerActivator : IControllerActivator
{
    private readonly string connStr;                  // Singleton
    private readonly IUserContext userContext;        // Singleton

    public CommerceControllerActivator(string connectionString)
    {
        this.connStr = connectionString;
        this.userContext = new AspNetUserContextAdapter();
    }

    public object Create(ControllerContext ctx)
    {
        // Scoped: one CommerceContext created per request
        var context = new CommerceContext(this.connStr);

        var type = ctx.ActionDescriptor.ControllerTypeInfo.AsType();
        if (type == typeof(HomeController))
            return new HomeController(
                new ProductService(
                    new SqlProductRepository(context),  // Transient, uses Scoped ctx
                    this.userContext));                 // Singleton injected in
        throw new Exception("Unknown controller " + type.Name);
    }
}
```

**What it demonstrates:** Separating creation into Singleton / Scoped / per-request phases makes the correct lifetimes obvious and prevents the Scoped `CommerceContext` from being captured by a Singleton.

## Reference Tables

| Lifestyle | Description | Thread-safety needs | When to use |
|-----------|-------------|---------------------|-------------|
| **Singleton** | A single instance is perpetually reused for the Composer's lifetime; same instance served every request. | **Must be thread-safe** — shared among many concurrent consumers. Stateless/immutable types qualify automatically. | Use *whenever possible* (efficient, minimal memory). Ideal for stateless services, immutable types, caches, Circuit Breaker, Mediator — anything that must be shared or is safely shareable. |
| **Transient** | A new instance is served every time it's requested; each consumer gets its own. | **None** — each consumer has a private instance, so no sharing. | The safe default when unsure about thread-safety; but least efficient (many allocations). Prefer swapping to Scoped when sequential sharing within a request suffices. |
| **Scoped** | At most one instance per type per defined scope (e.g., web request); like a Singleton inside the scope, not shared across scopes. | **Not required to be thread-safe** *if* the scope guarantees sequential access (as ASP.NET Core does per awaited request). | Long-running apps processing isolated operations in parallel with per-operation state — web requests, queue items. Excellent for EF Core `DbContext` (one per request). |

## Worked Example

**The bug.** In `CommerceControllerActivator`, suppose the constructor eagerly builds the repository once and stores it: `this.repository = new SqlProductRepository(new CommerceContext(connStr));`. Because the activator is the Composer and lives for the whole application, that `SqlProductRepository` is a **Singleton** — and it holds `CommerceContext` in a private field. Entity Framework's `DbContext` is **not thread-safe** and is meant to last only a single request. Yet here a *single* `CommerceContext` is now shared across every concurrent web request.

**Why it hurts.** Development and manual testing run one request at a time, so nothing breaks. In production, multiple users hit the app concurrently; two requests use the same `CommerceContext` on different threads simultaneously, producing corrupted state and intermittent exceptions — classic hard-to-reproduce concurrency bugs. The Dependency has been kept *captive* past its expected release time.

**The fix.** Restructure the Composition Root into three phases. Keep genuinely long-lived, thread-safe Dependencies (`connStr`, `AspNetUserContextAdapter`) as Singleton fields set in the constructor. Create `CommerceContext` as a **Scoped** Dependency *inside* `Create`, once per request, in a local variable. Assemble the per-request graph (`SqlProductRepository` → `ProductService` → `HomeController`) from that local Scoped context plus the injected Singletons. Now each request gets its own `CommerceContext`, honoring the rule that a component may only reference Dependencies whose lifetime is equal to or longer than its own. (Because `CommerceContext` is `IDisposable`, also track it against the request and dispose it in reverse order when the request is released — e.g., via `HttpContext.Response.RegisterForDispose`.)

## Key Takeaways

1. **Composition determines lifetime.** Whether you inject a shared or a private instance *is* the lifetime decision — and it belongs to the Composer, not the consumer.
2. **Learn the three Lifestyles.** Singleton (reuse forever), Transient (new every time), Scoped (one per scope). Prefer Singleton when thread-safe; use Scoped for per-request non-thread-safe Dependencies like `DbContext`; use Transient as the safe fallback.
3. **The golden rule:** a component must only reference Dependencies whose expected lifetime is **≥ its own**. Break it and you get a **Captive Dependency**.
4. **Disposal is the Composer's responsibility.** Track every disposable served and dispose in the **opposite order of creation**; keep `IDisposable` off your Abstractions (it's a **Leaky Abstraction**).
5. **Don't leak Lifestyle concerns** (`Lazy<T>`, `Func<T>`, `IEnumerable<T>`) into consumers — hide them behind a **Virtual Proxy** or **Composite** in the Composition Root.
6. **Never tie a Dependency's lifetime to a thread** — async frameworks migrate work across threads; scope to the request instead.
7. **These bugs hide until production.** Captive and per-thread mistakes only manifest under concurrency, so favor DI Containers that detect captives and structure Pure DI roots into explicit phases.

## Connects To

- **Chapter 7 (Composition Roots):** lifetime management is applied *inside* the Composition Root; the Composer introduced there is the object that now also owns lifetime and releasing.
- **Chapter 6 (Abstractions) / DIP & ISP:** disposable and multiplicity-leaking Abstractions are the same Leaky Abstraction / Interface Segregation violations discussed there.
- **Liskov Substitution Principle:** consumers stay unaware that a Dependency is shared precisely because any implementation must be substitutable without breaking correctness.
- **Chapter 9 (Interception / Decorators):** the recommended answer to "exotic" lifetime needs — redesign or Interception rather than custom Lifestyles; Circuit Breaker (a Singleton) is revisited there.
- **Chapter 12 (DI Containers):** containers excel at Lifetime Management, offer explicit `Release`, handle complex Lifestyle mixes, and can analyze graphs to detect Captive Dependencies.
- **Entity Framework Core:** `DbContext` (non-thread-safe, disposable, poolable) is the recurring real-world driver for choosing Scoped over Singleton.
