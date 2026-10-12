# Chapter 2: Writing tightly coupled code

## Core Idea
Drawing a three-layer diagram is a *declaration of intent* that guarantees nothing about the result. The chapter follows Mary Rowan, an experienced .NET developer, as she builds an ASP.NET Core MVC + EF Core e-commerce feature "the right way" (three separate Visual Studio projects for UI, domain, and data access) — yet produces **tightly coupled** code. The lesson is diagnostic, not prescriptive: it shows how easy it is to write tightly coupled code even with good intentions, and how to *evaluate* the damage by asking one question — "Is it possible to use each module in isolation?" The fix (DI) is deferred to Chapter 3.

## Frameworks Introduced (Name / When to use / How)
- **Composability analysis** / when you want to detect hidden coupling / Ask whether each module can be *replaced* in isolation without touching other modules. Even if you never intend to swap a module, the thought experiment surfaces coupling problems. If code is tightly coupled, all benefits of loose coupling are lost.
- **Dependency graph** / when Visual Studio's project references hide the important dependencies among BCL noise / Draw a graph where arrows point *toward* a module's dependency; inspect which layers depend on which.
- **Layered (n-layer) architecture** / a well-known, tried-and-tested approach to structuring complex apps / Compose the app from n distinct layers (here UI → Domain → Data access). The challenge is implementing it *correctly* — separate projects alone don't create real separation.

## Key Concepts
- **Tightly coupled** — Modules are bound so directly (via `new` and hard-coded references) that none can be reused or replaced in isolation.
- **Composability** — The ability to combine modules in new, unanticipated ways *without modifying* existing modules.
- **Dependency** — Anything you take on every time you add a project/assembly reference; the thing a module needs to function.
- **Volatile Dependency** — A dependency (like `ProductService` or `CommerceContext`) that introduces a requirement to set up/configure external infrastructure (a relational database); the kind of coupling worth avoiding.
- **Stable Dependency** — A dependency safe to couple to directly; tight coupling to it isn't harmful.
- **Late binding** — Loading the correct implementation (e.g., SQL Server vs. Azure Table) at deploy/run time; impossible when layers are tightly coupled.
- **Cross-Cutting Concerns** — Features like security that span many classes; costly to plug in when everything is tightly coupled.
- **Single Responsibility Principle (SRP)** — A class should have only one reason to change; viewed through *cohesion* (functional relatedness of a class's elements) — lower cohesion means higher SRP-violation risk.
- **Separation of Concerns** — Addressing each concern (security, domain, UI) in isolation; misused by Jens to justify putting security logic in the wrong layer.

## Mental Models
- **Use composability analysis when** you want to prove whether a "layered" app is genuinely decoupled — try to remove a layer and see if anything is left standing.
- **Use a dependency graph when** the project's real coupling is obscured by IDE convenience and BCL references.
- **Use the "Volatile vs. Stable" test when** deciding whether a given tight coupling is acceptable — coupling to Stable Dependencies is fine; coupling to Volatile Dependencies is the problem.

## Anti-patterns
- **`new` keyword inside a consumer** (`this.dbContext = new CommerceContext();`) — Hard-codes the dependency into `ProductService`; there's no reasonable way to Intercept and replace it. Every `new` introduces tight coupling.
- **Lasagna / Spaghetti Code** — Separate projects that *look* layered but are monolithic underneath; when it's layered spaghetti the authors call it "Lasagna."
- **Domain types defined in the data access layer** — `Product` lives in the data layer, so every consumer (even the UI) must reference the data layer to compile. A public `Product` class belongs in the domain model.
- **Loading configuration inside a reusable library** — `CommerceContext` reads `appsettings.json` itself; this "implicitness contains a trap." Only the finished application (entry point) should read config files and feed values down.
- **Pushing business logic into the UI** — Determining a "PreferredCustomer" via `HttpContext` in the controller is business logic misplaced in the presentation layer; Jens's buzzword defense (SoC, SRP, "the Agile way") is no excuse.
- **Fat views** — The Razor view does casts and string formatting that belong in the underlying model.

## Code Examples
```csharp
// Domain layer — the offending class
public class ProductService
{
    private readonly CommerceContext dbContext;

    public ProductService()
    {
        this.dbContext = new CommerceContext();   // hard-coded coupling to data access layer
    }

    public IEnumerable<Product> GetFeaturedProducts(bool isCustomerPreferred)
    {
        decimal discount = isCustomerPreferred ? .95m : 1;

        var featuredProducts =
            from product in this.dbContext.Products
            where product.IsFeatured
            select product;

        return
            from product in featuredProducts.AsEnumerable()
            select new Product
            {
                Id = product.Id,
                Name = product.Name,
                Description = product.Description,
                IsFeatured = product.IsFeatured,
                UnitPrice = product.UnitPrice * discount
            };
    }
}
```
```csharp
// UI layer — HomeController tightly coupled to ProductService (a Volatile Dependency)
public ViewResult Index()
{
    bool isPreferredCustomer = this.User.IsInRole("PreferredCustomer");
    var service = new ProductService();                       // hard-coded again
    var products = service.GetFeaturedProducts(isPreferredCustomer);
    this.ViewData["Products"] = products;
    return this.View();
}
```
**What it demonstrates:** The constructor's `new CommerceContext()` welds the domain layer to the data access layer, and the method signature `IEnumerable<Product> GetFeaturedProducts(...)` leaks a data-layer type — forcing the UI to also reference the data layer. Two hard-coded `new` statements make interception, replacement, and testing impossible.

## Reference Tables
| Benefit of loose coupling | Why Mary's app lacks it |
| --- | --- |
| **Late binding** | Can't deploy one build on SQL Server and another on Azure Table — the data layer can't be swapped. |
| **Extensibility** | Plugging in Cross-Cutting Concerns (e.g., security) requires changing many classes. |
| **Maintainability** | Each added concern makes every touched class more complex and harder to read. |
| **Parallel development** | Sweeping changes cause merge conflicts; developers step on each other. |
| **Testability** | No way to test without a real database; can't unit test or easily integration test. |

## Worked Example
Mary builds three projects mirroring the three-layer diagram: a **data access layer** (`Product` class + `CommerceContext : DbContext`, EF Core against SQL Server), a **domain layer** (`ProductService.GetFeaturedProducts`, applying the 5% preferred-customer discount), and a **UI layer** (`HomeController.Index` + Razor view). It compiles, F5 runs, the page renders — success, apparently.

Then composability is stress-tested against real stakeholder requests:
- **Replace the Web UI with WPF?** *Possible* — no module depends on the UI, so it can be swapped freely.
- **Replace the relational data access layer with Azure Table Storage?** *Impossible* — both UI and domain depend on the EF-based data layer. Remove it and *nothing compiles*; you'd have to replace all three layers together. There's no seam to tell the domain layer to use a different data layer.

Root-cause analysis: even if you break the UI→data-layer reference (by returning a domain type instead of the data-layer `Product`), the **domain layer still depends on the data access layer** because `ProductService`'s constructor does `new CommerceContext()`. The dependency direction is wrong. The desired graph *inverts* it: the data access layer should depend on the domain layer, and the UI should depend only on the domain — a spoiler for Chapter 3's rewrite.

## Key Takeaways
1. Separate projects/layers are cosmetic — real decoupling is about which module depends on which, and in what direction.
2. Every `new` on a Volatile Dependency introduces tight coupling you can't later Intercept; not all tight coupling is bad, but tight coupling to Volatile Dependencies is.
3. Test decoupling by asking "Can I replace each module in isolation?" — if removing one layer collapses the app, it isn't composable.
4. Leaking a lower-layer type through a method signature forces every caller to reference that lower layer.
5. Reusable libraries must be configured *by their callers*; only the application's entry point should read configuration files.
6. Tight coupling forfeits five concrete benefits: late binding, extensibility, maintainability, parallel development, and Testability.
7. The desired dependency graph *inverts* the domain↔data-access dependency so the data access layer depends on the domain, not vice versa.

## Connects To
- **Ch 1**: Introduced Volatile vs. Stable Dependencies, DI's purpose, and the security Cross-Cutting Concern referenced here; this chapter supplies the concrete pain those concepts warn about.
- **Ch 3**: Rewrites Mary's exact app loosely coupled with DI, realizing the inverted dependency graph (figure 2.10) and fixing the section 2.3.3 issues.
- **DEPENDENCY INVERSION PRINCIPLE**: The inverted graph (data access → domain) is the concrete motivation for depending on abstractions owned by the higher-level policy layer.
- **SRP / Separation of Concerns** (Robert C. Martin): Misapplied by Jens; correctly framed via cohesion.
- **AntiPatterns** (Brown et al.): Source of "Spaghetti Code," which layering degrades into as "Lasagna."
