# Chapter 5: DI anti-patterns

## Core Idea

An **anti-pattern** is a commonly occurring solution to a problem that generates decidedly negative consequences, even though better-documented alternatives exist. Chapter 4 showed the *right* DI patterns; this chapter shows the four ways developers *sincerely try* to do DI and end up doing more harm than good. Every one of these is a well-intentioned attempt to program to interfaces or achieve loose coupling that fails because it doesn't fully comply with DI fundamentals — chiefly, keeping the composition of Volatile Dependencies inside the **Composition Root**.

The four anti-patterns, in order of importance: **Control Freak** (most common, most damaging), **Service Locator** (most dangerous, because it *almost* works), **Ambient Context**, and **Constrained Construction**. Every one is curable by refactoring toward a proper DI pattern from chapter 4 — usually **Constructor Injection**. The unifying diagnostic question: *"Is a Volatile Dependency being created or resolved somewhere other than the Composition Root?"* If yes, you have an anti-pattern.

> WARNING (from the book): Most code in this chapter is an example of how *not* to do DI. Don't copy it.

## Frameworks Introduced

None. This chapter is diagnostic, not constructive — its "framework" is the catalog of four anti-patterns and their refactorings back to Constructor Injection.

## Key Concepts

- **Volatile Dependency** — a dependency you want to be able to replace, intercept, or fake (database access, external services, non-deterministic behavior like the clock, cross-cutting concerns). Creating one outside the Composition Root is the root cause of all four anti-patterns.
- **Stable Dependency** — deterministic, in-process, no side effects. `new`-ing these up is fine; they are not what these anti-patterns are about.
- **`new` as a code smell** — the `new` keyword next to a *Volatile* Dependency is the tell-tale sign of Control Freak. `new` isn't illegal; it's a smell only for volatile types outside the Composition Root.
- **Static classes are dependencies too** — you never `new` a static class, but depending on one causes the same coupling problems.
- **Foreign Default** — a default implementation of a Volatile Dependency defined in a *different module* than its consumer (e.g., `ProductService` defaulting to `SqlProductRepository`). Drags an unwanted module dependency along and defeats loose coupling. Contrast with a **Local Default** (default defined in the same module).
- **Temporal Coupling** — the correctness of code depends on doing things in a required order (e.g., you must `Register` before you `GetService`, or initialize an Ambient Context before first use). Introduced by Service Locator and Ambient Context.
- **Dishonest API** — a class whose public surface (e.g., a parameterless constructor) hides its true dependencies, so it looks simple but fails at runtime. Service Locator and Ambient Context both produce dishonest APIs.
- **Late binding** — selecting an implementation at runtime from configuration without recompiling. The (legitimate) desire behind Constrained Construction; the anti-pattern is *how* it's naively achieved.
- **It's about role, not mechanics** — the same `T Resolve<T>()` signature is a Service Locator in application code but an infrastructure component inside the Composition Root. The static structure is identical; the *role* differs.

## Mental Models

**How to recognize each anti-pattern:**

1. **Control Freak → spot the `new` (or static factory) on a Volatile Dependency outside the Composition Root.** Includes disguised forms: concrete/abstract/static factories, and test-specific constructor overloads that chain to a Foreign Default. If a field is typed as an interface but always resolves to one concrete type at runtime, control was never inverted.
2. **Service Locator → spot classes that *query* for their dependencies instead of *declaring* them.** A parameterless constructor plus a `Locator.GetService<T>()` / `container.Resolve<T>()` call somewhere in the class body. The dependencies are invisible to IntelliSense and to consumers.
3. **Ambient Context → spot a single Volatile Dependency reached through a *static accessor*** (`TimeProvider.Current`, `LogManager.GetLogger(...)`). Like a Singleton, but the instance is swappable. Global mutable state.
4. **Constrained Construction → spot a *convention* that all implementations of an abstraction share an identical constructor signature** (often parameterless, or "one connection string"), so `Activator.CreateInstance` can build them from a config-file type name.

## Anti-patterns

### **Control Freak**
- **What it looks like:** A class creates its own Volatile Dependencies — `new SqlProductRepository()` in a constructor or method — or hides that creation behind a Concrete Factory, Abstract Factory, Static Factory, or a test-only constructor overload that chains to a Foreign Default (`public ProductService() : this(new SqlProductRepository())`).
- **Why it fails:** It's the antithesis of Inversion of Control and a violation of the **Dependency Inversion Principle**. Declaring a field as an interface gains nothing if it's hard-coded to one concrete type — you can't intercept or replace it without recompiling. You can't reuse the module (it drags its dependencies along), parallel development suffers, and testability is lost (no Test Doubles). Factories only *move* the problem: a Static Factory that news up `Sql-` and `Azure-` repositories forces the consumer to transitively depend on *both* concrete types, dragging along DLLs it doesn't use and causing **cyclic dependencies** between the domain and data-access layers.
- **How to fix:** (1) Ensure you're programming to an abstraction (extract an interface if needed). (2) Consolidate all creation of the dependency into one place, returning the abstraction. (3) Move that creation *out* of the class via **Constructor Injection**. Push composition up to the Composition Root.

### **Service Locator**
- **What it looks like:** A class with a parameterless constructor that asks a static (or abstract) locator for its dependencies: `IProductService svc = Locator.GetService<IProductService>()`. The locator is a Static Factory pre-configured with concrete services.
- **Why it fails:** It's *dangerous because it almost works* — it supports late binding, parallel development, separation of concerns, and even Test Doubles. But it wrecks **reusability**: the consuming class (a) drags along the locator as a redundant dependency that exists only for mechanical reasons, and (b) is **dishonest** — its public API advertises a parameterless constructor while hiding real dependencies, so it compiles but throws `KeyNotFoundException` at runtime if you forget to register something. It's weakly typed despite generics. It lets you add dependencies in a new version without a compile error, silently breaking callers. In tests it causes **Interdependent Tests** (registrations linger in memory) requiring manual `Locator.Reset()` teardown, and **Temporal Coupling** between `Register` and use.
- **How to fix:** Consolidate all locator calls to one place, back the dependency with a `private readonly` field, then replace the locator call with a **Constructor Injection** parameter and delete the locator dependency. Refactor top-most classes first, working down the graph. (Note: a DI Container *resolving the whole graph from the Composition Root* is **not** a Service Locator — it's an infrastructure component. The anti-pattern is application code querying for granular services.)

### **Ambient Context**
- **What it looks like:** A single strongly-typed Volatile Dependency reached through a static member: `ITimeProvider p = TimeProvider.Current;` or `LogManager.GetLogger(typeof(X))`. Variations use static behavior methods, a merged base-class/static accessor, or a `Func<DateTime>` delegate.
- **Why it fails:** Structurally it's a mutable Singleton over a Volatile Dependency. It (a) **hides** the dependency (dishonest API, masks Constructor Over-injection / SRP violations), (b) makes **testing harder** via shared global state that leaks across tests unless teardown reverts it, (c) makes it hard to give different consumers different implementations (e.g., request-fixed vs. live-updating time), and (d) introduces **Temporal Coupling** — the app fails on first use if the context wasn't initialized in the Composition Root, instead of failing fast. Common with logging because devs copy library docs and want to avoid injecting a logger into every constructor — but that itch is a design smell, not a justification.
- **How to fix:** Centralize the ambient call in the constructor: add a `private readonly` field, a constructor parameter with a Guard Clause, and use the field everywhere. This is a straightforward refactor *if* the app already applies DI (only the Composition Root and tests break). The harder part — fixing an over-eager logging strategy — is a separate design problem (see ch. 10 on cross-cutting concerns via decorators).

### **Constrained Construction**
- **What it looks like:** All implementations of an abstraction are *required by convention* to share an identical constructor signature so they can be late-bound: read a type name from config, then `Activator.CreateInstance(type, connectionString)`. Every `IProductRepository` must take exactly one `string`.
- **Why it fails:** It imposes an *implicit* constraint (a fixed constructor shape) on top of the *explicit* one (implement the interface). A connection string as a constructor arg leaks an implementation choice — it makes no sense for an XML-file or REST-based repository. The common "parameterless constructor" variant is even more limiting: you can't compose layered object graphs or **share a single instance** among multiple consumers (each class ends up creating its own). Trying to rescue it with an Abstract Factory just relocates the constraint to the factory and creates an inflexible **Abstract Composition Root** that takes hard dependencies on concrete types in other assemblies and can't manage Object Lifetime.
- **How to fix:** Model construction on **explicit constraints only** (interface/base class). Let the Composition Root handle any constructor or factory shape. When you genuinely need to plug in new assemblies without recompiling, use a general-purpose **DI Container** — it reads constructor signatures via reflection, so the Abstract Composition Root only maps abstraction→implementation. But most apps don't need this: if you can recompile the startup project, keep the Composition Root centralized and avoid late binding entirely — it adds complexity and maintenance cost.

## Code Examples

```csharp
// ============ SMELL: Control Freak (the most common anti-pattern) ============
public class ProductService : IProductService
{
    private readonly IProductRepository repository;

    public ProductService()
    {
        // The field is typed as the abstraction, but it is hard-wired to ONE
        // concrete, Volatile implementation. `new` on a Volatile Dependency is
        // the tell-tale smell. At runtime this is ALWAYS SqlProductRepository —
        // you cannot intercept, replace, or fake it without recompiling.
        this.repository = new SqlProductRepository();
    }
}

// ============ SMELL: Service Locator (dangerous — it "almost works") =========
public class HomeController : Controller
{
    public HomeController() { }               // dishonest: looks dependency-free

    public ViewResult Index()
    {
        // Queries for its dependency instead of declaring it. Compiles fine;
        // throws at runtime if IProductService was never Register()-ed.
        IProductService service = Locator.GetService<IProductService>();
        var products = service.GetFeaturedProducts();
        return this.View(products);
    }
}
```

**What it demonstrates:** Both classes *program to an interface* yet gain none of DI's benefits. Control Freak binds the field to a concrete type via `new`. Service Locator hides the dependency behind a parameterless constructor and a static lookup, turning a compile-time contract into a runtime landmine. In both, the dependency lives outside the Composition Root.

## Reference Tables

| Anti-pattern | Symptom / how it looks | Root problem | Fix |
|---|---|---|---|
| **Control Freak** | `new VolatileType()`, or concrete/abstract/static factory, or test-only ctor overload chaining to a Foreign Default | Class controls creation of its Volatile Dependencies; violates DIP; tight coupling, no interception, cyclic layer deps | **Constructor Injection** — program to abstraction, consolidate creation, push to Composition Root |
| **Service Locator** | Parameterless ctor + `Locator.GetService<T>()` / `Resolve<T>()` in class body | Dishonest API; drags locator as redundant dep; runtime-only failures; Interdependent Tests; Temporal Coupling | **Constructor Injection** — back with `readonly` field, add ctor param, delete locator |
| **Ambient Context** | Static accessor to one Volatile dep: `TimeProvider.Current`, `LogManager.GetLogger()` | Mutable global Singleton; hidden dep; global test state; Temporal Coupling; masks SRP violations | **Constructor Injection** — inject the abstraction (e.g., `ITimeProvider`), Guard Clause |
| **Constrained Construction** | All impls forced to share a ctor signature; `Activator.CreateInstance(type, args)` from config type-name | Implicit ctor constraint; leaks impl choice; can't share instances / compose graphs | Explicit constraints only; use a **DI Container** for real late binding, else avoid late binding |

## Worked Example

**Before — Control Freak via an overloaded constructor + Foreign Default:**

```csharp
public class ProductService : IProductService
{
    private readonly IProductRepository repository;

    // Parameterless ctor forwards a Foreign Default (SqlProductRepository lives
    // in the data-access module) — this couples the domain layer to SQL.
    public ProductService()
        : this(new SqlProductRepository())
    {
    }

    public ProductService(IProductRepository repository)  // "for testing"
    {
        if (repository == null)
            throw new ArgumentNullException("repository");
        this.repository = repository;
    }
}

// Consumers can call `new ProductService()` — looks convenient, but it
// disables interception in production and drags the SQL DLL everywhere.
```

Why this is still Control Freak: the "best of both worlds" ctor pair *seems* to allow faking for tests while staying convenient for production. But the parameterless path news up a Volatile Dependency from another module (a Foreign Default), forcing strong coupling and preventing interception in the real application.

**After — refactored to plain Constructor Injection:**

```csharp
public class ProductService : IProductService
{
    private readonly IProductRepository repository;

    // ONE constructor. The dependency is honest, required, and immutable.
    // Composition happens in the Composition Root, not here.
    public ProductService(IProductRepository repository)
    {
        if (repository == null)
            throw new ArgumentNullException("repository");
        this.repository = repository;
    }

    public IEnumerable<DiscountedProduct> GetFeaturedProducts() =>
        from p in this.repository.GetFeaturedProducts()
        select p.ApplyDiscountFor(/* ... */);
}
```

The same three-step refactoring rescues a Service Locator: consolidate the `GetService` calls into one `readonly` field, then replace the lookup with a constructor parameter and delete the locator. Composition moves up to the single Composition Root, the API becomes honest, and failures shift from runtime back to compile time (with Pure DI) or startup verification (with a DI Container).

## Key Takeaways

1. **Control Freak is the most common and most damaging** — every `new` (or static factory) on a Volatile Dependency outside the Composition Root. It prevents any proper DI. Fix it first, before the others.
2. **Service Locator is the most dangerous** because it *almost* works — it satisfies most loose-coupling goals but destroys reusability, produces dishonest APIs, and converts compile-time contracts into runtime failures. It's the role, not the `T Resolve<T>()` signature, that makes it an anti-pattern.
3. **Ambient Context is a mutable Singleton over a Volatile Dependency** — hidden dependency, global test state, Temporal Coupling. Less destructive (one dependency, not many) but still has no place in a well-designed codebase.
4. **Constrained Construction only bites when you use late binding** — it forces a uniform constructor signature that leaks implementation choices and blocks instance sharing. If you can recompile the startup project, don't use late binding at all.
5. **`new` is a smell only for Volatile Dependencies** — it's perfectly fine for Stable Dependencies. Also beware static classes: you never `new` them, but depending on them couples you just the same.
6. **All four are cured by the same move:** consolidate creation/lookup, back it with a `readonly` field, and hoist composition to the Composition Root via **Constructor Injection**.
7. **The Composition Root is exempt** — a DI Container resolving whole object graphs there is infrastructure, not a Service Locator. The Composition Root already knows about everything, so it can't hide or drag along dependencies.

## Connects To

- **Chapter 3 (DI fundamentals):** These anti-patterns violate the **Dependency Inversion Principle** and the notion of Volatile vs. Stable Dependencies introduced there.
- **Chapter 4 (DI patterns):** Every anti-pattern here refactors to a pattern from ch. 4 — almost always **Constructor Injection**, and always concentrating composition in the **Composition Root**.
- **Chapter 6 (code smells):** Abstract Factories are "more often than not a code smell"; **Constructor Over-injection** (which Ambient Context hides) is analyzed here.
- **Chapter 8 (Object Lifetime):** Why Constrained Construction's inability to *share instances* matters; lifetime management belongs in the Composition Root, not in factories.
- **Chapter 10 (cross-cutting concerns):** The right way to apply ubiquitous concerns like logging (decorators) — the design fix behind the Ambient Context logging trap.
- **Part 4 (DI Containers):** The tool that legitimately enables late binding without Constrained Construction, by reading constructor signatures via reflection.
- **External:** *Working Effectively with Legacy Code* (Feathers) for the small, safe steps needed to refactor these anti-patterns out of existing code.
