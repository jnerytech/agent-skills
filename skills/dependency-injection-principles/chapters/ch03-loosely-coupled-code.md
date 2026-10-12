# Chapter 3: Writing loosely coupled code

## Core Idea

Chapter 2 diagnosed why Mary's tightly coupled e-commerce app fails; Chapter 3 rebuilds it the *right* way. The central move is to **invert the dependency** between the domain layer and the data access layer: instead of the domain depending on data access, the data access layer depends on the domain. This is achieved not by editing Mary's code but by re-creating it (an explicit choice for teaching — the authors stress that big rewrites are costly and high risk; prefer slow, step-by-step refactorings in real life). The tools are **Constructor Injection**, **programming to an interface**, and abstractions **owned** by their consumers, all wired together at a single **Composition Root**. Where Mary had 4 classes, the loose version has 9 classes and 3 interfaces — more moving parts, but each concern is separated and independently replaceable, testable, and developable in parallel.

## Frameworks Introduced

**Outside-in development**
- *When to use:* Building a new feature from scratch when stakeholders care most about visible behavior (usually the UI).
- *How:* Start at the most significant/visible place (the UI), then work inward, adding just enough to finish one feature before moving on. Contrast with Mary's inside-out approach (starting at the database). Outside-in gives quicker feedback and avoids overengineering; it is closely related to YAGNI ("You Aren't Gonna Need It"). Combined here with TDD (write the unit test the moment a new class is prompted).

**Constructor Injection**
- *When to use:* Whenever a class has a **Volatile Dependency** it needs for its whole lifetime. The default DI pattern.
- *How:* Statically declare required Dependencies as constructor parameters against an **abstraction** (interface). Store them in `readonly` fields after a **Guard Clause** null-check. The class never learns how or by whom the instance was created; that burden is pushed up to the Composition Root.

**Method Injection**
- *When to use:* Short-lived objects — especially **Entities** — that need a Dependency only for a single operation.
- *How:* Pass the Dependency as a parameter to the method that needs it (e.g., `Product.ApplyDiscountFor(IUserContext user)`), rather than through the constructor. Detailed in Chapter 4.

**Composition Root**
- *When to use:* Every application, exactly once, as close as possible to the entry point (`Main` in .NET Core).
- *How:* Centralize all object construction in one place, so classes plug together like electrical appliances. Compose manually (**Pure DI**) or delegate to a **DI Container**. Detailed in Chapter 4.

**Adapter pattern**
- *When to use:* Bridging an application-owned abstraction to an incompatible framework API.
- *How:* Implement the target abstraction, translate/forward calls to the framework "adaptee." Here `AspNetUserContextAdapter` implements `IUserContext` by delegating to ASP.NET Core's `HttpContextAccessor`.

## Key Concepts

1. **Dependency inversion (the layer flip):** IProductRepository is *defined in the domain layer* though *implemented in data access*, so the arrow points from data access up to the domain. The domain layer ends up with zero dependencies — a standalone module.
2. **Programming to an interface:** The cornerstone that lets one concrete implementation be swapped for another. Does *not* mean every class gets an interface.
3. **Seam:** A place where behavior can be replaced, intercepted, or mocked. Introducing `IProductService` gives `HomeController` a seam so it can be tested in isolation and `ProductService` developed in parallel.
4. **Volatile vs. Stable Dependency:** `ProductService` (not yet built, subject to replacement) is Volatile → hide behind an abstraction. The .NET BCL types are Stable → safe to depend on directly.
5. **POCOs / DTOs / view models are DI-uninteresting:** `FeaturedProductsViewModel`, `ProductViewModel`, `DiscountedProduct` carry data, contain no behavior to intercept/mock, so they need **no** interface and are safe to `new` up directly.
6. **Contextual runtime data behind an abstraction:** User identity, current time — metadata the user shouldn't influence — is best hidden behind an abstraction (`IUserContext`) and injected, rather than passed as a raw `bool` through the UI (which risks accidental security bugs).
7. **Entity:** A DDD term for a domain object with a long-term identity that outlives any single process/object instance (identified by a primary key). `Product` is an Entity.
8. **Persistence ignorance:** EF Core lets Entities stay plain POCOs with no framework dependency, so the domain `Product` can be reused by the data layer with no upstream leakage.

## Mental Models

**Pushing the burden upward.** Constructor Injection doesn't eliminate the responsibility of creating Dependencies — it *relocates* it. Each class declares its needs and defers; the burden slides up the n-layer stack until it lands at the top, in the Composition Root. This is the point, not a leak.

**DIP = "what", DI = "how".** The **Dependency Inversion Principle** prescribes the *goal* (higher- and lower-level modules both depend on abstractions) but is silent on *how* a consumer obtains its Dependencies. Dependency Injection is the *how*.

**The abstraction owner.** DIP's less-known half: an abstraction should be **owned by the module that uses it** — the consumer controls the abstraction's shape and ships it. So `IUserContext` and `IProductRepository` live in the *domain* (its consumers), tailored to the domain's needs, even though the UI and data layers respectively implement them. This is why the app defines its own `IUserContext` instead of leaning on the BCL's generic `IPrincipal`.

**Appliances and plugs.** Loose coupling makes classes composable like electrical appliances snapped together — but only if construction is centralized (the socket = Composition Root).

## Anti-patterns

- **Depending on a Volatile Dependency** ("a cardinal sin"): as soon as `HomeController` newed up `ProductService` directly, it would be tightly coupled to a type still in flux.
- **Leaking contextual data through the UI:** letting `HomeController` pass a `bool isPreferredCustomer` invites copy-paste repetition and accidental security bugs (e.g., passing `true` for `false`).
- **God Object via abstract base classes:** abstract classes are easily abused as ever-growing base classes; derivatives couple tightly to Volatile base behavior. Interfaces push you toward "Composition over Inheritance."
- **Expecting a DI Container to fix coupling:** a container automates Object Composition, Interception, and Lifetime Management but will *not* magically turn tightly coupled code into loosely coupled code.
- **Big-bang rewrite as default:** re-creating from scratch is a teaching device here, not a recommendation.

## Code Examples

```csharp
public class HomeController : Controller
{
    private readonly IProductService productService;

    public HomeController(IProductService productService)   // Constructor Injection
    {
        if (productService == null)                         // Guard Clause
            throw new ArgumentNullException("productService");
        this.productService = productService;
    }

    public ViewResult Index()
    {
        IEnumerable<DiscountedProduct> products =
            this.productService.GetFeaturedProducts();
        var vm = new FeaturedProductsViewModel(
            from product in products
            select new ProductViewModel(product));
        return this.View(vm);
    }
}
```
**What it demonstrates:** Constructor Injection against a **seam** (`IProductService`). The class declares its Volatile Dependency, guards against null, and stays ignorant of how the instance is created.

```csharp
public class ProductService : IProductService
{
    private readonly IProductRepository repository;
    private readonly IUserContext userContext;

    public ProductService(IProductRepository repository, IUserContext userContext)
    {
        if (repository == null)  throw new ArgumentNullException("repository");
        if (userContext == null) throw new ArgumentNullException("userContext");
        this.repository = repository;
        this.userContext = userContext;
    }

    public IEnumerable<DiscountedProduct> GetFeaturedProducts() =>
        from product in this.repository.GetFeaturedProducts()
        select product.ApplyDiscountFor(this.userContext);   // Method Injection
}
```
**What it demonstrates:** A pure domain-model class with two constructor-injected abstractions, forwarding `userContext` to the short-lived `Product` Entity via **Method Injection**.

```csharp
public class AspNetUserContextAdapter : IUserContext
{
    private static HttpContextAccessor Accessor = new HttpContextAccessor();

    public bool IsInRole(Role role) =>
        Accessor.HttpContext.User.IsInRole(role.ToString());
}
```
**What it demonstrates:** The **Adapter pattern** placed in the UI layer, translating the domain-owned `IUserContext` abstraction to the framework's `HttpContext`, keeping the domain and data layers framework-ignorant.

```csharp
new HomeController(
    new ProductService(
        new SqlProductRepository(
            new CommerceContext(connectionString)),
        new AspNetUserContextAdapter()));
```
**What it demonstrates:** The **object graph** assembled in the **Composition Root** (Pure DI). Every Volatile Dependency is resolved here, near the entry point.

## Reference Tables

| Abstraction | Defined in (owner) | Implemented in | Consumed by |
|---|---|---|---|
| `IProductService` | Domain | Domain (`ProductService`) | UI (`HomeController`) |
| `IProductRepository` | Domain | Data access (`SqlProductRepository`) | Domain (`ProductService`) |
| `IUserContext` | Domain | UI (`AspNetUserContextAdapter`) | Domain (`ProductService`) |

*Note: `IProductService` is owned by the domain yet consumed by the UI — a deliberate, pragmatic **DIP violation** left in place to avoid two extra projects.*

| Interfaces vs. abstract classes (authors' app preference: interfaces) |
|---|
| Abstract classes rot into God-Object base classes; interfaces force Composition over Inheritance |
| A class can implement many interfaces but derive from one base class |
| Interface syntax is terser (no `abstract`/`public` on members) |
| *For reusable NuGet libraries:* abstract classes win — you can add members without a breaking change |

## Worked Example: before → after

**Before (Chapter 2, inside-out, tightly coupled).** The view casts `ViewData["Products"]` to `IEnumerable<Product>`, formats price with `UnitPrice.ToString("C")` (a real bug — it uses the visitor's browser culture, so a Danish user pays krone prices for dollar amounts). Domain and UI both depend downward on data access; `ProductService` hard-references the data layer; the discount is a `bool` argument.

**After (Chapter 3, outside-in, loosely coupled), built in layer order UI → domain → data:**
1. **UI first.** `Index.cshtml` binds `@model FeaturedProductsViewModel`; each row is just `@product.SummaryText`. Rendering/culture logic moves into `ProductViewModel` (explicit `CultureInfo("en-US")` — bug fixed). Initially `HomeController.Index` returns a **hard-coded stub** so stakeholders see a running page immediately.
2. Replace the stub with an injected `IProductService` (Constructor Injection + Guard Clause). UI layer done; creating `HomeController` is now the Composition Root's job, not the UI's.
3. **Domain next.** A plain C# library holding POCOs (`DiscountedProduct`, `Product` Entity) and domain-owned abstractions (`IProductService`, `IProductRepository`, `IUserContext`). `ProductService` gets `IProductRepository` + `IUserContext` via Constructor Injection; `Product.ApplyDiscountFor` receives `IUserContext` via Method Injection. Domain now compiles with **zero outward dependencies**.
4. **Data access last.** `SqlProductRepository : IProductRepository` wraps a persistence-ignorant EF Core `CommerceContext`, whose connection string is now an *explicit* constructor Dependency (was implicit before). Data access depends *up* on the domain — inversion achieved.
5. `AspNetUserContextAdapter` (Adapter, in UI) implements `IUserContext`.
6. **Composition Root** near `Main` news up the full object graph.

**Result:** the domain layer stands alone; the web UI could be swapped for WPF, and the SQL data layer for Azure Table Service (via late binding on a config setting), because everything depends only on domain-owned abstractions.

## Key Takeaways

1. **Invert the dependency:** put abstractions in the consuming (higher-level) module and let lower-level modules implement them — the domain should depend on nothing.
2. **Constructor Injection is the default;** declare Volatile Dependencies as constructor parameters, guard against null, and push construction up to the **Composition Root**.
3. **Own your abstractions:** tailor them to the consumer's needs (`IUserContext` over the BCL's generic `IPrincipal`); DIP is about ownership, not just loose coupling.
4. **Don't abstract data:** POCOs, DTOs, and view models have no behavior to mock — no interface, safe to `new`.
5. **Use Method Injection for short-lived Entities** that need a Dependency for one operation only.
6. **Build outside-in** (UI → domain → data) with runnable stubs for fast stakeholder feedback and YAGNI discipline.
7. **A DI Container is optional** and never a substitute for understanding these patterns — it won't loosen tight coupling for you.

## Connects To

- **Chapter 1:** first definitions of Constructor Injection, Composition Root, Adapter pattern, DI Container.
- **Chapter 2:** the tightly coupled "before" version and the composability questions this chapter answers.
- **Chapter 4:** Composition Root, Pure DI vs. DI Container, and Method Injection in depth.
- **Chapter 7:** wiring the object graph into ASP.NET Core via a custom `IControllerActivator`; registering `HttpContextAccessor`.
- **Part 4:** DI Containers — Object Composition, Interception, Lifetime Management.
- **Related principles:** Dependency Inversion Principle (Martin), Single Responsibility Principle, Composition over Inheritance, YAGNI, Repository & Adapter patterns; DDD Entities (Evans); refactoring legacy code (Feathers).
