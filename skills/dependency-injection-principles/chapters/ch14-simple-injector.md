# Chapter 14: The Simple Injector DI Container

## Core Idea

**Simple Injector** (created by Steven van Deursen in 2010; co-maintained with Mark Seemann) is a DI Container built around *strictness* and *verifiability*. Where most containers try to guess what you meant, Simple Injector refuses to guess: it fails fast on ambiguity, blocks pitfalls at the API level, and — uniquely — lets you **verify the entire configuration up front** to catch misconfigurations like Captive Dependencies before the app ever runs.

Registration and resolution live on the **same `Container` instance** (unlike Autofac's `ContainerBuilder` → `IContainer` split), but the container *locks itself after the first resolve*, enforcing the "register once, resolve many" rhythm. Four design choices set it apart:

- **Scopes are ambient** — you always resolve from the `Container` itself, never from a scope, so you can't accidentally leak memory.
- **Sequences use a separate API** (`Collection.Register`) so stacked registrations can't silently override each other.
- **Primitive types can't be registered** — removes Auto-Wiring ambiguity by construction.
- **Object graphs are verifiable** — `Container.Verify()` walks every registration and diagnoses lifetime mismatches.

## Frameworks Introduced (Simple Injector's verifiable, correctness-first model)

The two-step process is **Configure → Resolve**, but *Configure* itself splits into **Register → Verify** (fig 14.4). Verification is a first-class phase, not an afterthought. The motto is "better safe than sorry": Simple Injector treats a resolvable-but-wrong configuration (e.g. a Transient captured inside a Singleton) as an error worth throwing on, because most container bugs are lifetime misconfigurations that are hard to trace at runtime.

NuGet package: `SimpleInjector` (chapter based on v4.4.3). MIT-licensed, open source. Integration packages exist to wrap scopes around web requests automatically.

## Key Concepts (Simple Injector-specific)

1. **`GetInstance<T>()`** — the resolve method (equivalent to Autofac's `Resolve<T>`). A weakly typed overload `GetInstance(Type)` returns `object` for reflection-driven scenarios (e.g. `IControllerActivator`). Concrete types with resolvable constructors resolve with *no* configuration via Auto-Wiring.
2. **`Register<TService, TImplementation>()`** — maps an Abstraction to an implementation, with compile-time generic constraints (`where TImplementation : class, TService`). Registering the same Abstraction twice **throws** (unlike stacking containers).
3. **De-duplication, no Torn Lifestyles** — registering a type both by concrete type and by its Abstraction is fine; Simple Injector de-duplicates under the hood so the Lifestyle isn't torn (a real hazard in Autofac).
4. **`Collection.Register` / `Collection.Append`** — the *separate* API for sequences. A consumer depending on `IEnumerable<T>` (or `IList<T>`, `ICollection<T>`, `IReadOnlyList<T>`) gets all registered implementations. `GetAllInstances<T>()` resolves them explicitly.
5. **Ambient scopes** — `Scope` instances are stored in an `AsyncLocal<T>` by `AsyncScopedLifestyle`, so scopes flow across `await` even onto other threads. `Lifestyle.Scoped.GetCurrentScope(container)` returns the active scope (or `null`). Not to be confused with the Ambient Context anti-pattern — scopes live only inside the Composition Root.
6. **`Container.Verify()`** — walks all registrations, instantiates graphs, and runs diagnostics. Catches **Lifestyle Mismatch** (Simple Injector's name for Captive Dependencies), disposable-Transient warnings, and more.
7. **Batch / Auto-Registration** — `container.Register(typeof(ICommandService<>), assembly)` scans assemblies and registers all closed-generic implementations; open-generics, Decorators, and Composites are auto-skipped. `GetTypesToRegister<T>(assembly)` returns types for LINQ filtering without registering them.
8. **`RegisterDecorator`** — first-class Decorator support (non-generic and open-generic). Decorators applied **in registration order**.
9. **`RegisterConditional<TService, TImpl>(Predicate<PredicateContext>)`** — inject different implementations based on the consumer/target (e.g. constructor parameter name). Simple Injector throws on zero *or* multiple matches — never guesses.
10. **Sequences are streams** — `IEnumerable<T>` (and other collection abstractions) resolve lazily; iterating calls back into the container per element by its Lifestyle. Injecting a stream is nearly free; a Singleton stream can safely hold Transient elements without them becoming Captive Dependencies.

## Mental Models

- **The container is a strict editor, not an autocomplete.** It won't finish your sentence. Ambiguity (two impls of one Abstraction, multiple constructors, a `string` parameter) is a compile-time-style error, surfaced early with a descriptive message — often pointing you at the exact fix URL.
- **Verify() is a compiler pass for your object graph.** Registration is cheap and order-independent; correctness is proven in one batch step at the end. If it verifies, the wiring is sound.
- **Ambient scope = `TransactionScope` for object lifetimes.** You open a scope with a `using`, resolve from the root container inside it, and everything scoped joins that ambient boundary automatically — no need to thread a scope object through your code.
- **Difficult APIs blind the container.** A `Register(() => new Foo(...))` code block hides dependencies from diagnostics. Prefer Auto-Wiring (via Parameter Objects) so `Verify()` can still see the whole graph.

## Anti-patterns

- **Skipping `Verify()`.** Being able to *resolve* a graph is no proof it's *correct*. Without verification, a Captive Dependency (Transient captured in a Singleton) ships silently and lives for the whole app lifetime. Always call `Verify()` at the end of configuration.
- **Mis-scoped lifestyles (Lifestyle Mismatch).** Registering a consumer as `Singleton` while its dependency is `Transient` is a Captive Dependency — Simple Injector *throws* on this (opposite of Autofac's lenient `InstancePerDependency`). Fix the lifetimes; only `SuppressDiagnosticWarning(..., justification: "...")` when you genuinely know better (the justification is mandatory documentation).
- **Not registering topmost/root types.** Unregistered concrete types resolve, but aren't verified. Explicitly register roots (e.g. MVC controllers) so `Verify()` covers the *complete* graph.
- **Overusing code blocks / delegates.** Registering with a factory lambda disables Auto-Wiring and hides dependencies from diagnostics. Extract primitive constructor args into **Parameter Objects** instead.
- **Using `Register` where `Collection.Register` is needed** (and vice versa). Multiple `Register` calls for one Abstraction throw; use `Collection.Register` for sequences, plain `Register` for single mappings and Composites.

## Code Examples

```csharp
// Register + RegisterDecorator + Verify — the full correctness-first cycle
var container = new Container();

// 1. Scoped lifestyle must be configured before scoped registrations
container.Options.DefaultScopedLifestyle = new AsyncScopedLifestyle();

// 2. Auto-Register all closed-generic command services from an assembly
Assembly assembly = typeof(AdjustInventoryService).Assembly;
container.Register(typeof(ICommandService<>), assembly);

// 3. Stack open-generic Decorators — applied in registration order
container.RegisterDecorator(
    typeof(ICommandService<>), typeof(AuditingCommandServiceDecorator<>));
container.RegisterDecorator(
    typeof(ICommandService<>), typeof(TransactionCommandServiceDecorator<>));
container.RegisterDecorator(
    typeof(ICommandService<>), typeof(SecureCommandServiceDecorator<>));

// 4. A single mapping with an explicit Lifestyle
container.Register<IIngredient, SauceBéarnaise>(Lifestyle.Singleton);

// 5. Verify the ENTIRE configuration up front — the differentiator
container.Verify();
```

**What it demonstrates:** the register-once/verify/resolve rhythm; open-generic batch registration; ordered Decorator chaining via `RegisterDecorator`; and the up-front `Verify()` that no other mainstream container makes a first-class step.

```csharp
// Verify() catching a Captive Dependency (Lifestyle Mismatch)
var container = new Container();
container.Register<EggYolk>(Lifestyle.Transient);       // short-lived
container.Register<Mayonnaise>(Lifestyle.Singleton);    // long-lived consumer!
container.Register<SunflowerOil>(Lifestyle.Singleton);

container.Verify();
// throws: [Lifestyle Mismatch] Mayonnaise (Singleton) depends on EggYolk (Transient).
```

**What it demonstrates:** `Verify()` detects that a Transient is captured by a Singleton — an error at rest that most containers never report.

## Reference Tables

### Simple Injector Lifestyle → meaning → when

| Simple Injector Lifestyle | Meaning | When to use |
|---|---|---|
| **`Lifestyle.Transient`** *(default)* | New instance every resolve. **Not tracked, never disposed.** Diagnostics warn if a disposable is registered Transient. | Default, safest choice; stateless lightweight services. |
| **`Lifestyle.Singleton`** | One instance for the container's lifetime; disposed when the container is disposed. | Thread-safe, stateless, expensive-to-create services. More efficient but must be registered explicitly. |
| **`Lifestyle.Scoped`** | One instance per scope; disposed when the scope is disposed. Requires a concrete `ScopedLifestyle` set via `Container.Options.DefaultScopedLifestyle`. | Per-request / per-unit-of-work state (e.g. DbContext). |
| **`AsyncScopedLifestyle`** | The most common `ScopedLifestyle` impl for .NET Core; stores the `Scope` in `AsyncLocal<T>` so it flows across `await`. | ASP.NET Core and any async app needing scoped lifetimes. |

Note: Simple Injector treats **Transient-in-Singleton** as a Captive Dependency and throws — stricter than Autofac.

## Commands & APIs

| API | Purpose |
|---|---|
| `new Container()` | Create the container (config + resolve in one instance). |
| `Register<TService, TImpl>([Lifestyle])` | Map Abstraction → implementation. |
| `Register<TConcrete>([Lifestyle])` | Register a concrete/root type. |
| `Register(typeof(ISvc<>), assembly)` | Open-generic batch / Auto-Registration. |
| `Register<T>(Func<T>)` | Code-block registration (disables Auto-Wiring; hides deps from diagnostics). |
| `RegisterInstance<T>(instance)` | Register a pre-built single instance (e.g. a Parameter Object). |
| `RegisterConditional<TSvc, TImpl>(predicate)` | Context-based selection among candidates. |
| `RegisterDecorator(typeof(ISvc<>), typeof(Dec<>))` | Register a Decorator (order = wrap order). |
| `Collection.Register<T>(types \| assembly)` | Register a sequence; auto-skips Decorators/Composites. |
| `Collection.Append<T, TImpl>([Lifestyle])` | Add one implementation to a sequence. |
| `Collection.Create<T>(types...)` | Build a subset stream (not registered in container). |
| `GetInstance<T>()` / `GetInstance(Type)` | Resolve one (generic / weakly typed). |
| `GetAllInstances<T>()` | Resolve the full sequence. |
| `GetTypesToRegister<T>(assembly)` | List candidate types for filtering (no registration). |
| `Container.Verify()` | Diagnose the whole configuration; throws on warnings. |
| `Lifestyle.Scoped.GetCurrentScope(container)` | Get the ambient scope (or null). |
| `AsyncScopedLifestyle.BeginScope(container)` | Open a disposable scope. |
| `reg.SuppressDiagnosticWarning(type, justification)` | Silence a specific diagnostic (justification required). |
| `container.Dispose()` | Dispose the container and its Singletons. |

## Worked Example

Register a notification graph, wrap it in a Composite, add a Decorator, verify, and resolve within a scope:

```csharp
var container = new Container();
container.Options.DefaultScopedLifestyle = new AsyncScopedLifestyle();

// Auto-Register the peers as a SEQUENCE (Composites/Decorators auto-filtered out)
Assembly asm = typeof(OrderApprovedReceiptSender).Assembly;
container.Collection.Register<INotificationService>(asm);

// Register the Composite as a SINGLE mapping — it wraps the sequence
container.Register<INotificationService, CompositeNotificationService>();

// Add a cross-cutting Decorator over the notification abstraction
container.RegisterDecorator<INotificationService, LoggingNotificationDecorator>();

// Prove the whole graph before first resolve
container.Verify();

// Resolve within an ambient scope — note: resolve from the CONTAINER, not the scope
using (AsyncScopedLifestyle.BeginScope(container))
{
    var svc = container.GetInstance<INotificationService>();
    svc.OrderApproved(order);   // -> Logging( Composite( [receipt, accounting, fulfillment] ) )
}
```

The resulting graph mirrors this Pure DI form:

```csharp
new LoggingNotificationDecorator(
    new CompositeNotificationService(new INotificationService[]
    {
        new OrderApprovedReceiptSender(),
        new AccountingNotifier(),
        new OrderFulfillment()
    }));
```

Because `Collection.Register` separates sequence registration from single mappings, the Composite is *not* accidentally injected into its own sequence (a trap Autofac falls into). `Verify()` confirms the wiring before any request is served.

## Key Takeaways

1. **`Container.Verify()` is the differentiator.** No other mainstream .NET container makes up-front, full-graph verification a first-class configuration phase. Call it at the end of registration to catch Captive Dependencies (Lifestyle Mismatches), disposable-Transient warnings, and unresolvable graphs *before* runtime.
2. **Strictness by design prevents whole bug classes.** Duplicate registrations throw, primitives can't be registered, multiple constructors throw, ambiguous conditionals throw — Simple Injector never guesses, so misconfigurations surface early with actionable messages.
3. **Ambient scopes make resolving from the root container safe.** Scopes flow via `AsyncLocal<T>`; you always `GetInstance` from the `Container`, never a scope object, without risking memory leaks or concurrency bugs.
4. **Sequences are a separate API and behave as streams.** Use `Collection.Register`/`Append` for sequences; `IEnumerable<T>` resolves lazily per-element by Lifestyle, keeping injection cheap and preventing accidental Captive Dependencies inside Singletons.
5. **Decorators and Composites are effortless.** `RegisterDecorator` chains aspects in registration order; `Collection.Register` auto-filters Decorators/Composites out of the wrapped sequence.
6. **When configuration is hard, fix the design — not the registration.** Difficulty configuring Simple Injector (ambiguity, primitives, multiple constructors) is a signal to refactor toward Parameter Objects, single constructors, and cleaner abstractions.
7. **Transient default is safest; Singleton is faster but must be explicit** — and Simple Injector will stop you from capturing a Transient inside a Singleton.

## Connects To

- **Ch 8 (Lifetime Management / Lifestyles):** Simple Injector's Transient/Singleton/Scoped map directly to the conceptual Lifestyles of Ch 8; `Verify()` operationalizes Ch 8's Captive Dependency pitfall (§8.4.1) as an automatic diagnostic ("Lifestyle Mismatch").
- **Ch 9 (Interception / Decorators):** `RegisterDecorator` is the container-level realization of the Decorator-based Cross-Cutting Concern approach from Ch 9; generic Decorators wrap open-generic abstractions like `ICommandService<T>`.
- **Ch 12 (DI Container fundamentals):** Simple Injector implements the Configuration-as-Code and Auto-Registration approaches of Ch 12 (§12.2, §12.3) while deliberately omitting file-based config, and embodies Ch 12's Auto-Wiring concept (§12.1.2).
- **Ch 10 (Parameter Objects / OCP):** Extracting primitive dependencies into Parameter Objects (Ch 10, §10.3.3) is the recommended fix for Simple Injector's block on registering primitives.
- **Ch 13 (Autofac) & Ch 15 (MS.DI):** Sibling container chapters for comparison — Autofac's lenient Torn-Lifestyle/InstancePerDependency behavior contrasts sharply with Simple Injector's strict de-duplication and Lifestyle-Mismatch enforcement.
