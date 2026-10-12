# Chapter 13: The Autofac DI Container

## Core Idea

Autofac is a comprehensive, consistently-designed DI Container (popular since 2007) whose overriding theme is **explicitness**: it never guesses what you mean; instead it offers an easy API that lets you opt into features. Usage follows a strict two-step rhythm — **register once, resolve many**. You configure a **`ContainerBuilder`**, call `Build()` to get an `IContainer`, then resolve components. Crucially, a `ContainerBuilder` cannot resolve, and you should never resolve from the root container directly — always resolve from a **lifetime scope**. This chapter maps the book's earlier patterns (Constructor Injection, Lifestyles, Decorators, Composites, Auto-Registration) onto Autofac's concrete API.

## Frameworks Introduced (Autofac's model: ContainerBuilder → Container)

The pipeline is: **`ContainerBuilder`** (configure) → `Build()` → **`IContainer`** (root) → `BeginLifetimeScope()` → **`ILifetimeScope`** (resolve here).

- **Configuration split**: configuration and consumption are separate concerns. The builder only registers; the container only resolves. This enforces the Register/Resolve separation the book advocates.
- **Reverse mapping direction**: unlike most containers, Autofac starts with the *concrete* type (`RegisterType<TConcrete>()`) and maps it *to* the Abstraction (`.As<TAbstraction>()`). Most other containers do the reverse.
- **Three configuration sources** (mixable in one container): Configuration as Code (the strongly-typed builder API), convention-based **Auto-Registration** (`RegisterAssemblyTypes`), and configuration files (via the separate `Autofac.Configuration` package, loaded as a **module** with `RegisterModule(new ConfigurationModule(config))`).

## Key Concepts (Autofac-specific)

- **RegisterType + As**: `builder.RegisterType<SauceBéarnaise>().As<IIngredient>()` maps concrete to abstraction. There are **no generic type constraints** between `RegisterType` and `As` — mapping incompatible types compiles but throws at `Build()` time.
- **Lifetime scope**: a throw-away derived container (`BeginLifetimeScope()`) defining a boundary where components are reused. It inherits the parent's true Singletons but also acts as a container of *local* singletons (scoped instances). Implements `IDisposable`; disposing it releases the components it created.
- **Instance scopes** (Autofac's name for Lifestyles): `InstancePerDependency` (default/Transient), `SingleInstance` (Singleton), `InstancePerLifetimeScope` (Scoped).
- **Releasing = decommissioning**: Autofac has no explicit Release method. You dispose the scope. Releasing signals eligibility for decommissioning — scoped disposables get disposed; singletons live until the root container is disposed.
- **Root-container danger**: resolving scoped instances from the root always returns the same instance (concurrency bugs); resolving disposable Transients from the root keeps them alive for eventual disposal (memory leaks, since root lives for app lifetime).
- **Auto-Registration in Autofac**: `RegisterAssemblyTypes(assembly)` is "the plural of `RegisterType`" — it returns the same fluent interface, so `.As<T>()`, `.Where(...)`, `.Except<T>()`, and lifetime methods all still work. Filter with `Where`/`Except` predicates.
- **AsClosedTypesOf**: `RegisterAssemblyTypes(asm).AsClosedTypesOf(typeof(ICommandService<>))` registers every type implementing a *closed* version of an open-generic interface. Ideal for hundreds of `ICommandService<TCommand>` use-case handlers.
- **Torn Lifestyle**: supplying multiple service types via *one* `As` call (`.As<Sauce, IIngredient>()`) is NOT the same as multiple `RegisterType` calls. Each `RegisterType` gets its own cache, so a non-Transient lifestyle becomes *torn* (a separate instance per registration).
- **Relationship types**: Autofac has no "ResolveAll". Resolve `IEnumerable<T>` (or `T[]`) to get all registered components of a service — a convention interpreted by the container.
- **Named / Keyed registrations**: `Named<IIngredient>("meat")` / `Keyed<IIngredient>(keyObj)` disambiguate multiple implementations; resolve via `ResolveNamed`/`ResolveKeyed`. Named/keyed components don't count as the default. Last unnamed registration wins as default (`PreserveExistingDefaults()` opts out).

## Mental Models

- **"Register once, resolve many"**: the container is built once at startup; resolution happens repeatedly through short-lived scopes (e.g., one per web request).
- **Lifetime scope = throw-away copy of the container**: a scoped component is a Singleton *within* its scope; query a second scope and you get a different instance. Dependencies always resolve at or below the consumer's scope — a Transient injected into a Singleton is tracked in the root so it outlives any nested scope.
- **Configuration difficulty is a design smell**: if a registration is hard (verbose `WithParameter`, ambiguity, cyclic Composites), Autofac is signaling a design problem. Refactor the API (e.g., `ThreeCourseMeal(entrée, main, dessert)` → `Meal(IEnumerable<ICourse>)`) rather than fighting the container.
- **Explicitness over magic**: Autofac won't auto-guess sequences vs. subsets, static factories, or Decorator order — you opt in via dedicated methods.

## Anti-patterns

- **Resolving from the root container** instead of a lifetime scope → concurrency bugs (shared scoped instances) and memory leaks (retained disposable Transients). Always `BeginLifetimeScope()`.
- **Tearing a Lifestyle** by splitting a multi-service registration into multiple `RegisterType` calls when using Singleton/Scoped.
- **Injecting application-wide configuration objects** as broad Parameter Objects — an Interface Segregation Principle violation. Prefer narrow, focused Parameter Objects containing only what a consumer needs.
- **Overusing `Resolve` with names/keys** outside the Composition Root — a sign of ambiguity that should be designed away.
- **Auto-Registering a Composite/Decorator alongside its own service type** → `Circular component dependency detected`. The Composite ends up inside the sequence injected into itself.
- **Relying on parameter-name matching** (`p.Name`) — convenient but not refactoring-safe; renaming a parameter silently breaks the config.

## Code Examples

```csharp
// Registration + mapping + lifetime scope
var builder = new ContainerBuilder();

builder.RegisterType<SauceBéarnaise>()
    .As<IIngredient>()          // concrete → abstraction
    .SingleInstance();          // Singleton lifestyle

builder.RegisterType<Steak>().As<IIngredient>();       // last wins as default

IContainer container = builder.Build();

// NEVER resolve from the root container — always from a scope:
using (var scope = container.BeginLifetimeScope())
{
    IMeal meal = scope.Resolve<IMeal>();               // strongly typed
    object weak = scope.Resolve(typeof(IMeal));        // weakly typed overload
    IEnumerable<IIngredient> all =                     // relationship type: get all
        scope.Resolve<IEnumerable<IIngredient>>();
    meal.Consume();
}   // Dispose releases the scoped/transient graph
```

**What it demonstrates**: the register-once/resolve-many rhythm, the concrete→abstraction mapping direction, lifetime configuration via a fluent modifier, resolving all implementations through `IEnumerable<T>`, and the mandatory use of a disposable lifetime scope for resolution and release.

```csharp
// Auto-Registration + generic Decorators
Assembly assembly = typeof(AdjustInventoryService).Assembly;

builder.RegisterAssemblyTypes(assembly)                // "plural of RegisterType"
    .Where(t => t.Name.EndsWith("Service"))
    .AsClosedTypesOf(typeof(ICommandService<>));       // all closed generics

builder.RegisterGenericDecorator(
    typeof(TransactionCommandServiceDecorator<>),
    typeof(ICommandService<>));                        // applied in registration order
```

**What it demonstrates**: convention-based Auto-Registration of open-generic use-case handlers, filtering with `Where`, and stacking generic Decorators with `RegisterGenericDecorator` (Decorators apply in order of registration).

## Reference Tables

**Autofac lifetime API → book Lifestyle → meaning**

| Autofac name (instance scope) | Autofac API method | Book Lifestyle | Meaning |
|---|---|---|---|
| Per-dependency | `.InstancePerDependency()` (default) | Transient | New instance per request; tracked by container for disposal. Safest, not always efficient. |
| Single instance | `.SingleInstance()` | Singleton | One instance for the container's lifetime; disposed when the container is disposed. Best for thread-safe services. |
| Per-lifetime scope | `.InstancePerLifetimeScope()` | Scoped | One instance per lifetime scope; a local singleton within that scope, disposed when the scope is disposed. |

In config files, set `"instance-scope": "single-instance"` (omitting it defaults to per-dependency).

## Commands & APIs

- `new ContainerBuilder()` — start configuration.
- `RegisterType<TConcrete>()` — register a concrete type; chain `.As<TAbstraction>()` (1–3 generic overloads, or non-generic for more).
- `Register<T>(c => ...)` — code-block/delegate registration (type-safe but **disables Auto-Wiring**); use for static factories, primitives.
- `RegisterInstance<T>(instance)` — register a pre-built single instance.
- `RegisterAssemblyTypes(params Assembly[])` — Auto-Registration; combine with `.Where(...)`, `.Except<T>()`, `.As(...)`, `.AsClosedTypesOf(typeof(IFoo<>))`.
- `RegisterGeneric(typeof(Foo<>)).As(typeof(IFoo<>))` — open-generic mapping.
- `RegisterDecorator<TDecorator, TService>()` / `RegisterGenericDecorator(typeof(Dec<>), typeof(ISvc<>))` — built-in Decorator support (order = registration order).
- `RegisterModule(new ConfigurationModule(config))` — plug in a **module**, e.g. file-based registrations from `Autofac.Configuration`.
- `.Named<T>("name")` / `.Keyed<T>(key)` — disambiguating registrations; `.PreserveExistingDefaults()` to not override prior defaults.
- `.WithParameter(name, value)` or `.WithParameter(predicate, valueAccessor)` — override Auto-Wiring for specific constructor parameters (wraps `ResolvedParameter`).
- `Build()` → `IContainer`; `BeginLifetimeScope()` → `ILifetimeScope`; `Resolve<T>()` / `Resolve(Type)` / `ResolveNamed<T>("name")` / `ResolveKeyed<T>(key)`; `Dispose()`.

## Worked Example

Register and resolve a simple object graph — a `Meal` composed of ingredients, with a cross-cutting Decorator:

```csharp
var builder = new ContainerBuilder();

// Primitive dependency wrapped in a focused Parameter Object
var flavoring = new Flavoring(Spiciness.Medium, extraSalty: false);
builder.RegisterInstance(flavoring);                       // single shared config value

// Concrete ingredients mapped to their abstraction
builder.RegisterType<VealCutlet>().As<IIngredient>();
builder.RegisterDecorator<Breading, IIngredient>();        // VealCutlet wrapped in Breading

// A Meal auto-wired with ALL registered ICourse components
builder.RegisterType<Meal>().As<IMeal>().InstancePerLifetimeScope();

// A class needing a static factory → code block
builder.Register<IMeal>(c => JunkFoodFactory.Create("chicken meal"));

IContainer container = builder.Build();

using (var scope = container.BeginLifetimeScope())         // per-request boundary
{
    var meal = scope.Resolve<IMeal>();                     // Auto-Wired graph
    meal.Consume();
}   // graph released here
```

The container Auto-Wires the constructor graph, applies `Breading` around `VealCutlet`, injects the shared `Flavoring`, and uses the code block for the factory-created type. All resolution happens inside a disposable scope.

## Key Takeaways

1. **Two steps, two objects**: configure a `ContainerBuilder`, `Build()` an `IContainer`, and always resolve from a `BeginLifetimeScope()` — never from the root container.
2. **Map concrete → abstraction** with `RegisterType<T>().As<IAbstraction>()`; remember there are no compile-time constraints, so mismatches fail at `Build()`.
3. **Three instance scopes** cover the book's Lifestyles: `InstancePerDependency` (Transient, default), `SingleInstance` (Singleton), `InstancePerLifetimeScope` (Scoped).
4. **Scale registrations with Auto-Registration**: `RegisterAssemblyTypes` + `Where`/`Except`/`AsClosedTypesOf` — the plural of `RegisterType`.
5. **Multiple implementations** are handled via `IEnumerable<T>` sequences, `Named`/`Keyed` selection, `RegisterDecorator`/`RegisterGenericDecorator`, and delegate-built Composites (filter the Composite/Decorators out to avoid cycles).
6. **Let Autofac guide your design**: verbose or ambiguous configuration is a signal to refactor the API, not to fight the container.

## Connects To

- **Ch 8 (Lifestyles / Lifetime Management)**: Autofac's instance scopes are the concrete realization of the conceptual Transient/Scoped/Singleton Lifestyles; lifetime scopes implement releasing and decommissioning.
- **Ch 12 (Using DI Containers)**: this chapter instantiates Ch 12's configuration taxonomy (Configuration as Code, Auto-Registration, config files) and the register-resolve-release lifecycle in Autofac's specific API. Chapters 14–15 do the same for Simple Injector and Microsoft.Extensions.DependencyInjection.
