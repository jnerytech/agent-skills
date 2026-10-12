# Chapter 7: Application composition

## Core Idea

Loosely coupled components are worthless until something wires them together. That wiring happens in exactly one place: the **Composition Root** — the single location, as close to the application's **entry point** as possible, where the object graph is built. The book compares it to the culinary principle of *mise en place*: prepare every component (class, module, layer) well in advance, then compose them at the last responsible moment, when integration of the different modules is actually required.

The act of building up hierarchies of related components is **Object Composition**, and it takes place *inside* the Composition Root. At runtime, Object Composition is the *first* thing that happens: as soon as the object graph is wired up, composition is finished and the constituent components take over. Unlike *mise en place*, Object Composition does not happen "as late as possible" in wall-clock terms — it happens in the one place where module integration is required.

The chapter's real subject is not composition itself (that's easy) but the *frameworks* you compose within. Each .NET framework exposes a different **Seam** (extensibility point) for hooking in your Composition Root, and the difficulty scales with how much **Inversion of Control** the framework imposes. Console apps give you full control; ASP.NET Core inverts control and makes you find the right hook.

## Frameworks Introduced (Composition Root placement per app type)

- **Console applications** — Easiest. Virtually no external Inversion of Control. When execution hits `Main` in the `Program` class, you're on your own: no events to subscribe to, no interfaces to implement. The `Program` class *is* the Composition Root.
- **UWP (Universal Windows Platform) applications** — Almost as easy. The entry point lives in the `App` class (`App.xaml` / `App.xaml.cs`), specifically the `OnLaunched` method, which is analogous to `Main`. The `App` class becomes the Composition Root. Uses the MVVM pattern; ViewModels are the DI-composed components.
- **ASP.NET Core MVC applications** — Harder, because of Inversion of Control, but explicitly *designed* for DI. The framework-level Seam is the **`IControllerActivator`** interface. Registration happens in the **`Startup`** class's **`ConfigureServices`** method. (Web API composition is identical to MVC in ASP.NET Core.)

## Key Concepts (5–10)

1. **Composition Root** — The single place where all modules from all layers are wired together. The entry point plus the Composition Root are the *only* code in the executable that knows about concrete types.
2. **The four responsibilities** — A Composition Root should do only four things: (1) load configuration values, (2) build the object graph, (3) invoke the desired functionality, and (4) release the object graph (covered in ch. 8). Then it gets out of the way.
3. **Pure DI** — Composing the object graph *by hand*, with `new`, without a DI Container. Every example in this chapter uses Pure DI; each is trivially swappable for a container later.
4. **Seam / extensibility point** — The framework-specific hook where you plug in composition. Finding the correct Seam is the whole game when a framework imposes Inversion of Control.
5. **Separate config loading from composition** — Loading configuration values must be decoupled from the methods that do Object Composition, so composition is testable without a valid config file present.
6. **`IControllerActivator`** — ASP.NET Core MVC's Seam. Its `Create(ControllerContext)` builds a controller with its Dependencies; `Release(context, controller)` disposes resources.
7. **Constructor Injection** — The preferred mechanism throughout; the Composition Root supplies Dependencies through constructors of the composed types.
8. **The Composer** — Any object or method that composes Dependencies (e.g. UWP's `CreatePage`, or `CreateCurrencyParser`). A named part of the Composition Root.
9. **Middleware composition** — ASP.NET Core middleware is a small piece of the Composition Root: register a function that constructs the middleware component with its Dependencies and invokes it.

## Mental Models (2–4)

- **Compose as close to the entry point as possible.** The executable's entire "brain" about concrete wiring lives in one thin shell at the top; everything below consumes only Abstractions. Push composition up, never bury it in business logic.
- **Mise en place.** Prepare all components in advance (loosely coupled, independently), then compose them fast at the single integration point. Preparation and composition are separated — in cooking by *time*, in software by *modules and layers*.
- **Find the Seam, then invert.** Easy frameworks (console, UWP) hand you control at `Main`/`OnLaunched`. Hard frameworks (ASP.NET Core) invert control, so your job is to locate the one extensibility point (`IControllerActivator`) and register your composer there.
- **The Composition Root is a thin executable shell.** Even when a diagram of it "looks complicated," it represents almost the entire code base of the executable — because everything else has been delegated down to lower layers.

## Anti-patterns

- **Scattering composition across the codebase** — Any `new` of a concrete Dependency outside the Composition Root leaks composition responsibility and defeats loose coupling.
- **Coupling composition to the configuration system** — Doing `ConfigurationBuilder` work inside your object-graph-building method makes composition untestable without a real config file. Load config separately.
- **Abstract Factory overuse** — Generally viewed "with suspicion," but acceptable *only* when confined to the Composition Root (as `IExchangeRateProvider` is used as an Abstract Factory there).
- **Replacing ASP.NET Core's built-in container** — The authors call the ability to swap out the built-in DI Container a "grave mistake." Keep the built-in container even if you use a third-party one for your own components.
- **Doing real work in a controller** — Controllers should delegate to Dependencies (query, validate, invoke domain logic), not perform it inline. That delegation is where DI enters.

## Code Examples

```csharp
// A Pure DI Composition Root for an ASP.NET Core MVC app: the custom
// IControllerActivator. This IS the Composition Root — it wires every
// controller to its Dependencies by hand (no container).
public class CommerceControllerActivator : IControllerActivator
{
    private readonly string connectionString;

    public CommerceControllerActivator(string connectionString)
    {
        this.connectionString = connectionString;
    }

    public object Create(ControllerContext context)
    {
        Type type = context.ActionDescriptor.ControllerTypeInfo.AsType();

        if (type == typeof(HomeController))
            return this.CreateHomeController();
        else if (type == typeof(RouteController))
            return this.CreateRouteController();
        else
            throw new Exception("Unknown controller " + type.Name);
    }

    private HomeController CreateHomeController()
    {
        // Constructor Injection all the way down — Pure DI.
        return new HomeController(
            new ProductService(
                new SqlProductRepository(
                    new CommerceContext(this.connectionString)),
                new AspNetUserContextAdapter()));
    }

    private RouteController CreateRouteController()
    {
        var routeAlgorithms = /* ... */;
        return new RouteController(new RouteCalculator(routeAlgorithms));
    }

    public void Release(ControllerContext context, object controller)
    {
        // Left empty for now; resource disposal is covered in ch. 8.
    }
}
```

**What it demonstrates:** A complete Pure DI Composition Root for ASP.NET Core MVC. `Create` receives the controller `Type` from the `ControllerContext`, and a private factory method hand-wires the full Dependency chain via Constructor Injection. No DI Container is involved — only the activator (registered in `Startup`) knows the concrete types; controllers and services consume only Abstractions.

```csharp
// Registering the custom activator in the ASP.NET Core Startup class.
public void ConfigureServices(IServiceCollection services)
{
    services.AddMvc();

    var controllerActivator = new CommerceControllerActivator(
        Configuration.GetConnectionString("CommerceConnectionString"));

    // AddSingleton makes ASP.NET Core intercept controller creation
    // with your custom activator.
    services.AddSingleton<IControllerActivator>(controllerActivator);
}
```

**What it demonstrates:** The Seam registration. `ConfigureServices` is where the Composition Root is plugged into the framework — the custom `IControllerActivator` is registered as a singleton so the framework routes all controller creation through it.

## Reference Tables

| Application type | Composition Root lives in | Entry point / Seam | IoC level |
|---|---|---|---|
| Console | `Program` class | `Main` method | None — full control |
| UWP | `App` class (`App.xaml.cs`) | `OnLaunched` method | Minimal — no explicit DI Seams, but composable |
| ASP.NET Core MVC / Web API | `Startup` + custom `IControllerActivator` | `IControllerActivator.Create` (registered in `ConfigureServices`) | High — must find the Seam |

| The four (and only) jobs of a Composition Root |
|---|
| 1. Load configuration values |
| 2. Build the object graph |
| 3. Invoke the desired functionality |
| 4. Release the object graph (ch. 8) |

## Worked Example: Composing an ASP.NET Core MVC application end to end

**1. The problem.** ASP.NET Core MVC receives an HTTP request and needs a controller (e.g. `HomeController`) to handle it. It comes with its own built-in composition engine, but it does *not* force you to register your own application components in that container — you may use Pure DI.

**2. Find the Seam.** The request pipeline works like this: a request arrives → the runtime asks its *controller activator* to create a controller for the URL, passing the controller `Type` → the activator returns a new instance → the framework invokes the appropriate action method → when finished, the framework calls `Release` so the activator can dispose resources. The extensibility point is therefore `IControllerActivator`:

```csharp
public interface IControllerActivator
{
    object Create(ControllerContext context);
    void Release(ControllerContext context, object controller);
}
```

**3. Implement the activator (the Composition Root).** Write `CommerceControllerActivator` (shown above). `Create` reads the controller type from `context.ActionDescriptor.ControllerTypeInfo.AsType()`, then dispatches to a private factory (`CreateHomeController`, `CreateRouteController`) that hand-wires each controller's full Dependency graph with Constructor Injection. Although each controller's *immediate* Dependencies are few (e.g. `IProductService`, `IRouteCalculator`), the object graph beneath them is considerably deeper — and all of it is built here.

**4. Register the activator in `Startup`.** In `ConfigureServices`, call `services.AddMvc()`, construct the activator (passing the connection string pulled from `Configuration`), and register it with `services.AddSingleton<IControllerActivator>(controllerActivator)`. This intercepts controller creation so your custom activator is always used.

**5. (Optional) Compose middleware.** Extract pipeline logic into a class (e.g. `LoggingMiddleware`) with its Dependencies injected via constructor and its behavior in an `Invoke(HttpContext, Func<Task> next)` method. In `Startup`, register a lambda on the pipeline that constructs the middleware with its Dependencies and awaits `Invoke`. This is a small slice of the Composition Root. If a middleware's object graph grows complex, move its construction into your main composer (e.g. `CommerceControllerActivator`). Note: object graph construction should always be fast, do no I/O, and stay synchronous — so async/await never complicates DI.

The result: one Seam (`IControllerActivator`), one registration in `Startup`, and a Pure DI Composition Root that keeps every controller, service, and repository loosely coupled.

## Key Takeaways

1. **There is one Composition Root per application, placed as close to the entry point as possible** — it and the entry point are the only code in the executable that references concrete types.
2. **A Composition Root does only four things:** load config, build the object graph, invoke functionality, release the object graph — then gets out of the way.
3. **Placement is framework-specific:** console → `Program`/`Main`; UWP → `App`/`OnLaunched`; ASP.NET Core MVC → custom `IControllerActivator` registered in `Startup.ConfigureServices`.
4. **Applying DI in any framework reduces to finding the correct Seam.** The more Inversion of Control a framework imposes, the harder the Seam is to find — but a DI-friendly framework like ASP.NET Core still provides one.
5. **Pure DI (composing by hand) is a first-class option everywhere** — no container is required; the chapter composes all three app types by hand.
6. **Separate configuration loading from Object Composition** so composition stays unit-testable without a real config file.
7. **Object Composition is only one of three dimensions of DI;** the others — Lifetime Management (Object Lifetime / releasing instances) and Interception — follow in later chapters.

## Connects To

- **Ch. 4 (Object Composition basics):** This chapter builds directly on §4.1's rules for *when and how* to compose, applying them to real frameworks rather than repeating theory.
- **Ch. 8 (Object Lifetime):** The fourth Composition Root responsibility — *releasing* the object graph — is deferred here. `Release` on `IControllerActivator` and `HttpContext.Response.RegisterForDispose` are the ASP.NET Core hooks for disposal.
- **Ch. 6 (patterns / Abstract Factory):** Reinforces that Abstract Factory is acceptable only inside the Composition Root.
- **Ch. 11 (Interception) & the third DI dimension:** Object Composition is one of three dimensions; Interception and Lifetime Management complete the picture.
- **Ch. 12 & Part 4 (DI Containers):** Every Pure DI example here is swappable for a DI Container; ch. 12 covers choosing between Pure DI and a container, and ch. 15 covers ASP.NET Core's built-in container.
- **MVVM (UWP):** ViewModels are the DI-composed components; contrast with MVC's behaviorless View Model, which is simply `new`ed up.
