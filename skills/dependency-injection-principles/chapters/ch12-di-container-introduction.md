# Chapter 12: DI Container introduction

## Core Idea

Dependency Injection is first and foremost a **technique** — Part 3 built entire applications by hand-composing object graphs (**Pure DI**). A **DI Container** (a.k.a. **IoC Container**) is *technology* layered on top of that technique: a general-purpose software library that automates Object Composition, Lifetime Management, and Interception. The book's analogy: making ice cream by hand vs. using an electric ice cream maker — same technique, less labor.

Formal definition: *a DI Container is a software library that provides DI functionality and automates many of the tasks involved in Object Composition, Interception, and Lifetime Management. It's an engine that resolves and manages object graphs.* Object Composition is a **Generic Subdomain** — a problem solvable once, for all applications — which is precisely why a reusable library makes sense (just like logging or data access).

The load-bearing message of the chapter is the last section: **DI does not depend on a DI Container.** A container is a *useful but optional* tool. The real decision — the theme to internalize — is **when to use a DI Container vs. Pure DI**, and that decision hinges on project size and complexity, not fashion.

## Frameworks Introduced

**Register-Resolve-Release (RRR) pattern** — the lifecycle discipline for any container:
1. **Register** — configure the container: map Abstractions to concrete types (done once, at startup, in the Composition Root).
2. **Resolve** — ask the container to compose an object graph (`Resolve` / `GetInstance`). A single method call.
3. **Release** — the container tears down / disposes the resolved graph when the scope ends.
Corollary rule: **never reconfigure the container after you've started resolving** — that "will only give you grief."

**Auto-Wiring** — the engine underneath Resolve. Using reflection plus the type information the compiler baked into classes, the container reads a class's constructor, recursively resolves each argument's type, then constructs the type. Because Constructor Injection *statically advertises* a class's dependencies, containers can Auto-Wire arbitrarily deep graphs from a flat list of Abstraction→concrete mappings.

**Auto-Registration** (a.k.a. Batch Registration / Assembly Scanning) — **Convention over Configuration** applied to registration. Instead of writing one registration per component, you scan one or more assemblies and register every type matching a convention (e.g., "concrete class whose name ends in `Repository`, mapped to its single interface") with a single rule. This is the technique that can make a container "invisible."

## Key Concepts

1. **DI Container / IoC Container** — engine that resolves and manages object graphs; a Stable Dependency, but still a third-party library with costs.
2. **Pure DI** — hand-composition of object graphs in code, no container. The Part 1–3 default. Complete applications can be built with it alone.
3. **The Resolve API** — weakly typed `object Resolve(Type serviceType)` (Autofac) / `GetInstance` (Simple Injector); often a strongly typed `T Resolve<T>()` overload. Returns a fully populated graph. Throws a descriptive exception when configuration is incomplete.
4. **Auto-Wiring** — reflection-driven recursive composition from Abstraction→concrete maps.
5. **Configuration as Code** — mappings expressed explicitly in source code (`AddTransient<IProductService, ProductService>()`). Compiler-checked, high control, no late binding.
6. **Configuration files (XML/JSON)** — mappings in external files. Only benefit: late binding (change behavior without recompiling). Verbose, brittle, no compile-time checks. "Configuration files don't scale."
7. **Auto-Registration / Convention over Configuration** — rules + assembly scanning replace per-type registration. Less effort, enforces consistency, but weakly typed and less control.
8. **Late binding vs. early binding** — can you swap an implementation without recompiling? Only configuration files (and assembly-folder scanning) give true late binding.
9. **Open vs. closed generics** — `ICommandService<>` (open, definition) vs. `ICommandService<AdjustInventory>` (closed). Simple Injector's Auto-Registration shines here, registering all closed implementations (and generic Decorators) of an open-generic Abstraction in one call.
10. **Costs and risks of libraries** — learning curve, opinionated quirks, yak shaving, the **bus factor**, and abandonment risk. With containers the alternative is *not* "build your own" — it's Pure DI.

## Mental Models

- **Technique vs. technology (ice cream maker).** DI is the technique; the container is the appliance. You can always fall back to doing it by hand. Never confuse "we do DI" with "we use a container."
- **Value/cost quadrant (Figure 12.6).** Two axes: Simple↔Sophisticated and Valuable↔Pointless. **Pure DI** sits top-left (valuable *because* simple). **Auto-Registration** sits top-right (valuable when wielded sophisticatedly — best value/cost ratio). **Configuration as Code** as the *center of gravity* of a Composition Root sits at the bottom: **pointless** — you pay the container's costs (learning, weak typing, replacement risk) while still registering every class by hand, i.e., linear growth without the payoff.
- **Container as background infrastructure.** Done right with conventions, the container "drops to the background"; you rarely touch it and focus on features. Done wrong, it becomes automagical and someone becomes a bottleneck ("critical resource").
- **Feedback-cycle length.** Pure DI is strongly typed → the *compiler* verifies composition (fastest feedback, catches missing deps and some Captive Dependencies). Containers rely on reflection → configuration errors surface only at *runtime*.

## Anti-patterns

- **Calling `Resolve` outside the Composition Root = Service Locator.** The `Resolve` signature ("give me any type, code still compiles") is exactly the Service Locator signature. If application code calls the container, you've reintroduced the Service Locator anti-pattern (ch. 5.2). Constrain all container interaction to the Composition Root; this keeps the rest of the code unaware a container even exists.
- **Building your own DI Container.** Listing 12.1 is flagged *bad code — do not use at work.* A real container needs Lifetime Management, Interception, Auto-Registration, cycle detection, good diagnostics, extensibility, and docs — years to mature. Use an existing one or Pure DI.
- **Configuration-file-centric configuration.** XML/JSON is verbose, brittle, uncompiled, and doesn't scale (the Spring.NET hundred-man-year horror story: merge conflicts, wasted hours). Reserve files for the rare truly late-bound handful of types.
- **A Composition Root centered on Configuration as Code.** Pointless — should be avoided. Center it on Pure DI (with a few late-bound types) *or* on Auto-Registration (with a little Configuration as Code / Pure DI).
- **Reconfiguring the container after first Resolve** — violates Register-Resolve-Release.
- **Auto-Registering a component that can't be Auto-Wired.** If a type needs hand wiring, *exclude* it from the convention or it'll error.

## Code Examples

```csharp
// Configuration as Code with Microsoft.Extensions.DependencyInjection.
// This is the "Register" phase of Register-Resolve-Release,
// and it lives entirely in the Composition Root.
var services = new ServiceCollection();

// Auto-Wired mappings: Abstraction -> concrete type, per lifestyle.
services.AddSingleton<IUserContext, AspNetUserContextAdapter>();
services.AddTransient<IProductRepository, SqlProductRepository>();
services.AddTransient<IProductService, ProductService>();

// A concrete type that maps to itself (typical for MVC controllers).
services.AddTransient<HomeController>();

// Hand wiring via a Func<T> delegate — needed because CommerceContext
// takes a primitive `string`, which the container can't disambiguate.
services.AddScoped<CommerceContext>(
    p => new CommerceContext(connectionString));
```

**What it demonstrates:** the container's core job is a *flat list of mappings*; from these, Auto-Wiring recursively composes the full `HomeController` graph on Resolve. Strongly typed generic overloads give compile-time checks. Note the escape hatch: adopting a container does **not** force you to abandon hand wiring — the `Func<T>` overload lets you hand-wire the one type (`CommerceContext`) that can't be Auto-Wired, because DI Containers resolve by *type* and several components might need a `string`.

## Reference Tables

**Configuration styles**

| Style | Explicit? | Late binding? | Compile-time checks | Verdict |
|---|---|---|---|---|
| Configuration files (XML/JSON) | Explicit | Yes | No | Only for the rare truly late-bound types |
| Configuration as Code | Explicit | No | Yes | Prefer over files; but not as a Composition Root's center |
| Auto-Registration | Implicit (conventions) | Middle (scan folder/assembly) | No | Preferred starting point; scales best |

**Pure DI vs. DI Container — when to pick which**

| Dimension | Pure DI | DI Container (esp. with Auto-Registration) |
|---|---|---|
| What it is | Hand-composition in code | Library that Auto-Wires object graphs |
| Typing / feedback | Strongly typed; **compiler** verifies; fastest feedback | Reflection-based; errors surface at **runtime** |
| Learning cost | Trivial — no API to learn | Must learn container API + quirks; bus-factor risk |
| Composition Root maintenance | Grows **linearly**; every ctor refactor breaks the root (merge conflicts) | Auto-Wiring absorbs ctor changes; Auto-Registration → near-**zero** maintenance |
| Object-graph clarity | Explicit, hard-coded, easy to read | Opaque; hard for newcomers to trace |
| Detects Captive/Torn/disposable issues | Limited (some Captive Deps only) | Often auto-detects disposables & Captive Dependencies |
| Replacement risk | None | Real — swapping containers repays learning cost |
| **Best when** | Composition Root is **small**; small apps | Composition Root maintenance becomes a **problem**; big apps, many convention-capturable classes |

No hard numbers exist — it depends on project size, team experience, and risk appetite. Rule of thumb: **start with Pure DI; switch to Auto-Registration when the Composition Root becomes a maintenance burden.**

## Worked Example

Five near-identical registrations violate DRY:

```csharp
services.AddTransient<IProductRepository,  SqlProductRepository>();
services.AddTransient<ICustomerRepository, SqlCustomerRepository>();
services.AddTransient<IOrderRepository,    SqlOrderRepository>();
// ...IShipmentRepository, IImageRepository — same shape
```

Convention observed: all repositories live in one assembly, each concrete name ends in `Repository`, each implements exactly one interface. Replace the list with a single scanning rule (Simple Injector + LINQ over reflection):

```csharp
var assembly = typeof(SqlProductRepository).Assembly;   // pick a representative type

var repositoryTypes =
    from type in assembly.GetTypes()
    where !type.IsAbstract
    where type.Name.EndsWith("Repository")
    select type;

foreach (Type type in repositoryTypes)
    container.Register(type.GetInterfaces().Single(), type);  // e.g. IProductRepository -> SqlProductRepository
```

For four types this is *more* code — but it scales to hundreds with zero further edits, and new repositories register themselves the moment they follow the convention. For generic Abstractions, scanning by hand breaks down, so containers offer first-class support: `container.Register(typeof(ICommandService<>), assembly)` registers every closed `ICommandService<TCommand>` implementation in one line (equivalent to N manual `Configuration as Code` calls), and `RegisterDecorator(typeof(ICommandService<>), typeof(AuditingCommandServiceDecorator<>))` wraps them all with a Decorator.

## Key Takeaways

1. **DI ≠ DI Container.** DI is a technique; a container is an optional engine. Complete apps ship on Pure DI alone.
2. **Auto-Wiring is the payoff of Constructor Injection** — because constructors statically advertise dependencies, a container recursively composes deep graphs from a flat mapping list, and the Composition Root becomes resilient to constructor changes.
3. **Configuration hierarchy:** prefer **Auto-Registration** (start here) → complement with **Configuration as Code** for special cases → reserve **configuration files** only for the rare types needing late binding. Files don't scale.
4. **Confine the container to the Composition Root.** Calling `Resolve` elsewhere is the Service Locator anti-pattern; isolation keeps app code container-agnostic.
5. **Pure DI's edge is strong typing** → compiler feedback (fastest), clearer graphs, Captive-Dependency detection. Its cost is a Composition Root that grows linearly and breaks on every ctor refactor.
6. **The verdict:** small Composition Root → **Pure DI**; when maintaining it hurts → **Auto-Registration** with Convention over Configuration (minimizes maintenance to ~zero, best value/cost). A Configuration-as-Code-centered root is pointless.
7. **Never build your own container**, and weigh the costs/risks (learning curve, bus factor, abandonment) of any you adopt.

## Connects To

- **Ch. 3–4 (Composition Root, Constructor Injection):** the container lives *only* in the Composition Root; Auto-Wiring is powered by Constructor Injection's static advertising.
- **Ch. 5 (Service Locator):** `Resolve` has the Service Locator signature — the anti-pattern this chapter fences off to the Composition Root.
- **Ch. 8 (Lifetime Management / Lifestyles):** Singleton/Transient/Scoped registrations; containers can detect Captive/Torn/Ambiguous Lifestyles the compiler can't.
- **Ch. 6 (Object graphs):** Dependency cycles → the naive AutoWireContainer throws `StackOverflowException`; real containers detect cycles.
- **Ch. 9–10 (Interception / Decorators, open generics):** Auto-Registration of open-generic Abstractions and generic Decorators (`RegisterDecorator`) is a headline container capability.
- **Ch. 1 (benefits of DI, Stable Dependency):** late binding as a DI benefit; a container as a Stable Dependency with real costs/risks.
- **Ch. 13–15:** concrete containers — Autofac, Simple Injector, Microsoft.Extensions.DependencyInjection.
