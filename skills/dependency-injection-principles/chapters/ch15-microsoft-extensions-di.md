# Chapter 15: The Microsoft.Extensions.DependencyInjection DI Container

## Core Idea

**Microsoft.Extensions.DependencyInjection (MS.DI)** is Microsoft's official, open-source (Apache 2.0) DI Container, built into ASP.NET Core and shipping as a NuGet package for other project types. It is deliberately minimal: a "conforming container" whose small feature set covers well-behaved scenarios where every component uses Constructor Injection. Usage is an explicit two-step rhythm — **register once, resolve many**: you configure an **IServiceCollection**, then call `BuildServiceProvider` to produce an **IServiceProvider** that composes object graphs.

The authors' central verdict: MS.DI works fine for straightforward Auto-Wiring, but its LIMITATIONS — no Auto-Registration API, no built-in Decorator or Composite support, no property injection, no keyed/conditional registrations, no verification, and poor diagnostic messages — mean that anything designed around this book's patterns quickly turns into verbose, brittle, hand-rolled code. For those applications, Pure DI or a fuller container (Autofac, Simple Injector) is the better tool. The key lesson: DI is not tied to any container, so you should be able to swap containers by rewriting only the Composition Root.

## Frameworks Introduced (IServiceCollection registration model)

MS.DI enforces a **strict separation** between configuration and resolution. `IServiceCollection` (equivalent to Autofac's `ContainerBuilder`) accepts registrations but cannot resolve; `IServiceProvider` (the built container) resolves but is not reconfigured. All configuration is **Configuration as Code** via `Add...` extension methods — there is no support for configuration files or Auto-Registration. Registrations map an Abstraction to a concrete type, a delegate factory, or a pre-created instance, each tagged with a Lifestyle (Transient/Scoped/Singleton). The last registration for an Abstraction "wins" on a single resolve, but earlier ones are retained for sequence resolution.

## Key Concepts (MS.DI-specific)

1. **Register once, resolve many** — configure `ServiceCollection`, call `BuildServiceProvider(validateScopes: true)`, then resolve from the resulting provider.
2. **Never resolve from the root container** — always resolve from an `IServiceScope` (via `CreateScope()`). Resolving from the root leaks memory (tracked disposable Transients are never released) and risks concurrency bugs.
3. **`validateScopes: true`** — pass this to `BuildServiceProvider` to block accidental resolution of Scoped instances from the root. ASP.NET Core enables it automatically in Development; enable it everywhere.
4. **`GetRequiredService` vs `GetService`** — the former throws `InvalidOperationException` if unregistered; the latter returns null. Prefer `GetRequiredService`. Both have weakly typed (`Type`-based) overloads for when the type isn't known at design time.
5. **Torn Lifestyle** — each `AddScoped`/`AddSingleton` call creates its own cache. Registering the same implementation twice (e.g. `AddSingleton<T>()` and `AddSingleton<IAbstraction, T>()`) yields *separate* instances. Fix: register the concrete type once, then register the Abstraction as a delegate forwarding to it (`c => c.GetRequiredService<T>()`).
6. **Sequences via `IEnumerable<T>`** — MS.DI natively resolves `IEnumerable<TService>` to all registrations of `TService`; `GetServices<T>()` does the same. Auto-Wiring of sequence Dependencies "just works."
7. **`ActivatorUtilities.CreateInstance<T>`** — the escape hatch for Auto-Wiring a type while explicitly overriding some constructor arguments (params matched left-to-right). Used to hack Decorators and to disambiguate multi-arg constructors. It is *not* compiler-verified — reordering same-typed parameters fails silently.
8. **No Auto-Registration API** — you must scan assemblies yourself with LINQ + reflection and loop `services.Add...`. Order of `Assembly.GetTypes()` is undefined, so duplicate closed-generic registrations resolve unpredictably across restarts.
9. **Transient can inject into Singleton** — MS.DI treats a Transient as living as long as its consumer, so it permits Transient-into-Singleton (a Captive Dependency risk), while blocking Scoped-into-Singleton under scope validation.
10. **Confusing exceptions** — MS.DI throws generic messages (even `StackOverflowException` on a cyclic Composite), unlike the descriptive errors of mature containers.

## Mental Models

- **The scope is a request-specific cache.** A Scoped component is a Singleton *within its scope* — same instance every resolve inside it, a different instance in a second scope. Disposing the scope releases (and disposes) everything the scope created. Dependencies resolve at or below the consumer's scope.
- **MS.DI is a conforming container, not a fully featured one.** It intentionally exposes the smallest common denominator so many containers can back the same abstraction. Fighting its limits means "building a new DI Container on top of MS.DI" — a signal to switch tools.
- **Building around MS.DI's gaps means writing container plumbing by hand.** Every missing feature (scanning, decoration, composition) becomes LINQ/reflection code that lives in your Composition Root and takes a hard dependency on `IServiceProvider`/`ActivatorUtilities`.

## Anti-patterns (fighting MS.DI's limits instead of choosing a fuller container)

- **Resolving from the root container** instead of a scope — memory leaks and concurrency bugs.
- **Splitting registrations** into multiple `AddSingleton`/`AddScoped` calls for one implementation — produces Torn Lifestyles (multiple instances where you expected one).
- **Reinventing the container** — layering ever-more scanning, conditional-decoration, and lifetime code on top of MS.DI to reproduce Autofac/Simple Injector features. The authors explicitly discourage this; use Pure DI or a fuller container instead.
- **Relying on `ActivatorUtilities` positional overrides** for ambiguous constructors — brittle, not compiler- or resolve-time-verified, fails silently on parameter reordering.
- **Leaving a Composite/Decorator in a scanned assembly** — the LINQ query picks it up, making it depend on itself (cyclic graph → `StackOverflowException`). Filter it out or move it to the Composition Root's assembly.

## Code Examples

```csharp
// Basic mapping with Lifestyles — register once, resolve from a scope.
var services = new ServiceCollection();

services.AddSingleton<IIngredient, SauceBéarnaise>();   // one shared instance
services.AddScoped<ICourse, Course>();                  // one per IServiceScope
services.AddTransient<IMeal, Meal>();                   // new instance each resolve

ServiceProvider container =
    services.BuildServiceProvider(validateScopes: true); // safety: block Scoped-from-root

using (IServiceScope scope = container.CreateScope())
{
    IMeal meal = scope.ServiceProvider.GetRequiredService<IMeal>();
    meal.Consume();
} // scope disposal releases Transients/Scoped created here
```

**What it demonstrates:** the two-step register/resolve rhythm, all three Add... lifetime methods, `validateScopes: true`, and resolving/releasing through an `IServiceScope` rather than the root.

```csharp
// Avoiding a Torn Lifestyle when exposing one instance under two service types.
services.AddSingleton<SauceBéarnaise>();                       // the single cache
services.AddSingleton<IIngredient>(
    c => c.GetRequiredService<SauceBéarnaise>());              // forwards — same instance
```

**What it demonstrates:** why `AddSingleton<SauceBéarnaise>()` + `AddSingleton<IIngredient, SauceBéarnaise>()` would tear the Lifestyle into two instances, and the delegate-forwarding fix.

## Reference Tables

MS.DI lifetime → book Lifestyle → meaning:

| MS.DI method / name | Book Lifestyle | Meaning |
|---|---|---|
| `AddTransient` / Transient | Transient | New instance per resolve. Tracked and disposed by the container (leaks if resolved from root). Expected to live as long as its consumer. |
| `AddScoped` / Scoped | Scoped | One instance per `IServiceScope`; reused within the scope, disposed when the scope is disposed. Different scope → different instance. |
| `AddSingleton` / Singleton | Singleton | One instance for the container's lifetime; disposed only when the container is disposed. |

MS.DI limitations vs Autofac / Simple Injector:

| Capability | MS.DI | Autofac / Simple Injector |
|---|---|---|
| Auto-Registration (assembly scanning) | None — hand-roll with LINQ/reflection | Built-in (`AsClosedTypesOf`, etc.) |
| Decorators | None — hack via `ActivatorUtilities` | First-class (`RegisterDecorator` / `RegisterGenericDecorator`) |
| Disambiguation (multiple same-type deps) | Manual code blocks / `ActivatorUtilities` | Keyed (Autofac) / Conditional (Simple Injector) registrations |
| Property injection | Not supported | Supported |
| Verification / diagnostics | None; generic, confusing exceptions | Configuration verification, clear messages |
| Composite wiring | Manual, verbose, cycle-prone | Concise, a few lines |

## Commands & APIs

- `new ServiceCollection()` — create the registration container.
- `services.AddTransient<TService, TImpl>()` / `AddScoped<...>()` / `AddSingleton<...>()` — map Abstraction to concrete type with a Lifestyle.
- `services.AddTransient<TService>(Func<IServiceProvider, TService> factory)` — delegate/code-block registration (primitives, static factories, disambiguation).
- `services.AddSingleton(typeof(T), preCreatedInstance)` — register a pre-created instance (non-generic overload accepts value types the generic API blocks).
- `services.BuildServiceProvider(validateScopes: true)` — build the `IServiceProvider`.
- `provider.CreateScope()` → `IServiceScope` (`IDisposable`, has `.ServiceProvider`).
- `scope.ServiceProvider.GetRequiredService<T>()` / `GetService<T>()` / `GetServices<T>()`.
- `ActivatorUtilities.CreateInstance<T>(IServiceProvider provider, params object[] parameters)` — Auto-Wire with explicit overrides.

## Worked Example

Registering an object graph in an ASP.NET Core `ConfigureServices` method (the hosting environment supplies the `IServiceCollection`):

```csharp
public void ConfigureServices(IServiceCollection services)
{
    // Cross-cutting infrastructure
    services.AddSingleton<Flavoring>(
        new Flavoring(Spiciness.Medium, extraSalty: true)); // pre-created Parameter Object

    // Data + domain, mixed Lifestyles
    services.AddScoped<IInventoryRepository, SqlInventoryRepository>();

    // Multiple ICourse implementations resolved as a sequence
    services.AddTransient<ICourse, Rillettes>();
    services.AddTransient<ICourse, CordonBleu>();
    services.AddTransient<ICourse, MousseAuChocolat>();
    services.AddTransient<IMeal, Meal>();   // Meal(IEnumerable<ICourse> courses) auto-wired

    // Hand-rolled Auto-Registration for command handlers (no built-in API)
    Assembly assembly = typeof(AdjustInventoryService).Assembly;
    var mappings =
        from type in assembly.GetTypes()
        where !type.IsAbstract && !type.IsGenericType
        from i in type.GetInterfaces()
        where i.IsGenericType
           && i.GetGenericTypeDefinition() == typeof(ICommandService<>)
        select new { service = i, implementation = type };

    foreach (var m in mappings)
        services.AddTransient(m.service, m.implementation);
}
```

Refactoring `ThreeCourseMeal(ICourse entrée, ICourse mainCourse, ICourse dessert)` to `Meal(IEnumerable<ICourse> courses)` removes the ambiguity that would otherwise force a fragile code block or `ActivatorUtilities` call — a better design beats fighting the container.

## Key Takeaways

1. MS.DI is a deliberately minimal "conforming container": great for Constructor-Injection-only graphs, weak for this book's advanced patterns.
2. Always `BuildServiceProvider(validateScopes: true)` and resolve from an `IServiceScope` — never from the root container — to avoid memory leaks and concurrency bugs.
3. Configuration is separated from resolution: `IServiceCollection` registers, `IServiceProvider` resolves; the collection cannot resolve.
4. Three Lifestyles only — Transient, Singleton, Scoped — and each duplicate `AddScoped`/`AddSingleton` call risks a Torn Lifestyle; forward through a delegate to keep one instance.
5. There is no Auto-Registration, Decorator, or Composite support; you rebuild these with LINQ/reflection and `ActivatorUtilities`, which is verbose, brittle, and cycle-prone.
6. `ActivatorUtilities` overrides and scanning are not verified — errors surface as generic runtime exceptions (even `StackOverflowException`), unlike mature containers.
7. When you find yourself building a container on top of MS.DI, switch to Pure DI, Autofac, or Simple Injector — DI is container-agnostic, so only the Composition Root changes.

## Connects To

- **Ch 8 (Lifestyles / Lifetime Management):** MS.DI's Transient/Scoped/Singleton map directly to the book's Lifestyles; the same Captive Dependency risk applies when a Transient (or worse, a longer-lived dependency) is injected into a Singleton.
- **Ch 12 (Using a DI Container):** MS.DI is Configuration-as-Code only — it omits the configuration-files and Auto-Registration axes discussed there.
- **Ch 13 (Autofac) & Ch 14 (Simple Injector):** the same sample graphs (difficult APIs, sequences, Decorators, Composites) are far shorter in those containers; MS.DI's limitations are the explicit contrast that motivates choosing a fuller container or Pure DI.
