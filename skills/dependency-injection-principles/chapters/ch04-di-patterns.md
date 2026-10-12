# Chapter 4: DI patterns

## Core Idea

Chapter 4 is a mini-catalog of the four foundational DI design patterns — prescriptive, named solutions to the question *"How do I inject my Dependencies?"* The patterns are **not of equal importance and not interchangeable**: **Composition Root** and **Constructor Injection** dominate and should be used in almost every situation, while **Method Injection** and **Property Injection** are specialized tools for narrow cases. Each pattern is presented with the same framing — a short description, how it works, when to use it (advantages/disadvantages), and a known/worked example. The chapter's spine is a single rule: **when in doubt, choose Constructor Injection — you can't go terribly wrong with that choice.**

The patterns answer two orthogonal questions: *where* do you compose object graphs (Composition Root — as close to the entry point as possible) and *how* do you hand each class its Dependencies (the three injection patterns). Together they let you implement either Pure DI (plain C#) or a DI Container.

## Frameworks Introduced

**Composition Root** — *When to use:* always, in every startup project. It answers "Where should we compose object graphs?" with "As close as possible to the application's entry point." *How:* Concentrate all object-graph construction into a single logical location (the `Main` method, an ASP.NET Core `Startup` class, `App.xaml.cs`, etc.). It is a *concept*, not a class or method — it may span multiple classes as long as they live in one module. It takes a direct dependency on all other modules. If a DI Container is used, this is the **only** place it may be referenced; using it elsewhere degrades into the Service Locator anti-pattern. When spinning off concurrent operations, the Composition Root creates a fresh object graph per operation.

**Constructor Injection** — *When to use:* the **default** for DI; use it almost exclusively, whenever a class has a required Dependency with no reasonable Local Default. Answers "How do we guarantee a necessary Volatile Dependency is always available?" with "By requiring all callers to supply it as a constructor parameter." *How:* Expose a single public constructor taking the Dependency as an argument; add a Guard Clause rejecting null; store it in a `readonly` field. The constructor must contain no other logic. The signature statically documents the class's Dependencies and the compiler enforces that callers supply them.

**Method Injection** — *When to use:* when a Dependency (or the consumer of it) **varies with each operation/call**, and the injection happens *outside* the Composition Root — typically add-in/framework scenarios passing runtime context, or domain Entities that mix data with behavior. Answers "How can we inject a Dependency when it's different for each operation?" with "By supplying it as a method parameter." *How:* Add the Dependency as a parameter to the method that needs it, with a Guard Clause. The method should **use or pass on** the Dependency, never store it. The Dependency becomes part of the method's/Abstraction's public API — acceptable only when it carries runtime context supplied by direct callers.

**Property Injection** (a.k.a. Setter Injection) — *When to use:* only in **reusable libraries** where a class has a **good Local Default** but you want to leave the Dependency **optional** and overridable for extensibility. Answers "How do we enable DI as an option when we have a good Local Default?" with "By exposing a writable property callers may set to override the default." *How:* Expose a public settable property of the Dependency's type, seed it with the Local Default, guard the setter against null, and enforce Popsicle immutability (an internal flag forbidding changes after initialization). Harder to implement robustly than it looks.

## Key Concepts

- **Composition Root definition** — a single, *logical* location where modules are composed together. Only startup projects have one; Composition Roots are application-specific and never reused.
- **Local Default** — a default implementation of a Dependency that originates in the *same module or layer* as the consumer. Contrast **Foreign Default** — a default living in a *different* assembly; hard-referencing one is the Control Freak anti-pattern. Transitivity: a Local Default becomes a Foreign Default if one of *its* Dependencies is a Foreign Default.
- **Pure DI** — composing object graphs with plain C# (`new`), no container. Both Pure DI and DI Containers are valid ways to implement a Composition Root.
- **Guard Clause** — a null check in the constructor/method/setter guaranteeing the Dependency is present, so members can use it without re-checking.
- **`readonly` field** — marks the stored Dependency immutable after construction; possible with Constructor Injection, *impossible* with Property Injection (the property stays writable).
- **Single public constructor rule** — application components must have exactly one constructor; overloaded constructors create ambiguity for callers and DI Containers. Reusable libraries (like the BCL: `StreamWriter(Stream, Encoding, ...)`) legitimately have multiple.
- **The apparent dependency explosion** — the complaint that the Composition Root depends on all assemblies. It's an illusion: assembly dependencies are **transitive**, so tightly coupled code actually has *more* total dependencies. Counting dependencies means counting each module-to-module reference, not modules.
- **Popsicle immutability** — allowing a client to set a Dependency only *during initialization*, then freezing it (Eric Lippert's term); used to make Property Injection robust.
- **Two Method Injection use cases** — (1) the *consumer* varies each call (e.g. many `Customer` Entities reusing one `IVoucherRedemptionService`); (2) the *Dependency* varies each call (e.g. add-ins receiving an `IApplicationContext`).
- **Open/Closed Principle & Null Object** — Property Injection opens classes for extension; where only an extensibility point is needed, implement the Local Default as a Null Object (no-op).

## Mental Models

- **The chef's mise en place (composition near the entry point).** Just as a cook assembles all ingredients in one station before cooking, the Composition Root assembles the whole object graph in one place near `Main`, then the graph does the work. Defer the wiring decision as long as possible to keep your options open.
- **Constructor as a contract.** The constructor signature is compiled into the type and visible to all — it is an honest, statically-checked declaration of what the class needs to function. A caller literally cannot compile without honoring it.
- **Push responsibility up, then stop.** Constructor Injection pushes the responsibility for creating Dependencies up to consumers, who push it further up — but the buck stops at the Composition Root, the single third party that connects consumers to services. You can't defer creation indefinitely.
- **"When in doubt, Constructor Injection."** The decision tree exists, but the safe default under uncertainty is always Constructor Injection.

## Anti-patterns

Each pattern guards against a specific failure:

- **Composition Root** guards against **Service Locator** (using a DI Container outside the root) and **Control Freak** (classes `new`-ing up their own Foreign Defaults). Composing objects in scattered locations limits your ability to Intercept/replace behavior.
- **Constructor Injection** guards against **Temporal Coupling** and optional-Dependency null-check clutter. Its own disadvantage: frameworks applying the **Constrained Construction** anti-pattern (assuming a parameterless constructor) can make it awkward.
- **Method Injection** guards against building up data-centric Entities with all their Dependencies via the constructor. But it must **not** be used inside the Composition Root, where it causes **Temporal Coupling** (the `Initialize`-then-`DoSomething` trap). A method must never *store* an injected Dependency — that risks Temporal Coupling, **Captive Dependencies**, or hidden side effects.
- **Property Injection** guards against forcing a required Dependency on callers who have a good default — but is itself fraught: it causes **Temporal Coupling**, is hard to implement robustly, and must not be used as a workaround for **Constructor Over-injection** (too many Dependencies is a code smell a property won't cure). Never use it in application code.

## Code Examples

```csharp
// Canonical Constructor Injection (Listing 4.5)
public class HomeController
{
    private readonly IProductService service;   // readonly: frozen after construction

    public HomeController(IProductService service)   // single public constructor
    {
        if (service == null)                         // Guard Clause: reject null
            throw new ArgumentNullException("service");

        this.service = service;                      // store; no other logic
    }

    // Every member can now use `this.service` without null-checking —
    // it is guaranteed present once the constructor returns.
}
```

**What it demonstrates:** the four non-negotiables of Constructor Injection — a single public constructor that *statically declares* the required Dependency, a Guard Clause that turns a null argument into an immediate exception, a `readonly` backing field, and a constructor free of all logic except guarding and storing. After the constructor returns the object is in a consistent, fully-initialized state.

## Reference Tables

| Pattern | Question it answers | When to use | Key advantage | Key trade-off / disadvantage |
|---|---|---|---|---|
| **Composition Root** | Where do we compose object graphs? | Always — every startup project; near the entry point | Single place controls all wiring; enables interception & per-thread graphs | Depends on all modules (apparent, not real, explosion) |
| **Constructor Injection** | How guarantee a required Dependency is always available? | **Default choice**; required Dependency, no reasonable Local Default | Injection guaranteed; easy; statically declares Dependencies | Constrained Construction frameworks; whole graph built eagerly |
| **Method Injection** | How inject a Dependency that differs per operation? | Dependency or consumer varies per call; outside Composition Root; add-ins, domain Entities | Passes operation-specific context; injects into data-centric objects | Limited applicability; pollutes the public API/Abstraction |
| **Property Injection** | How make DI optional when a good Local Default exists? | Reusable libraries only; optional Dependency with good Local Default | Easy to understand; sensible defaults simplify API | Hard to implement robustly; limited; causes Temporal Coupling; libraries only |

**Decision process (Figure 4.9):** Do you *need* the Dependency or *need to supply* it onward? → *supply it* ⇒ **Method Injection**. → *need it*: Who needs it? → *data-centric object* (Entity) ⇒ **Method Injection**. → *component*: What kind of code? → *application code* ⇒ **Constructor Injection**. → *reusable library*: Is there a Local Default? → *Yes* ⇒ **Property Injection**; *No* ⇒ **Constructor Injection**.

## Worked Example

**Decision: Mary needs to convert a `Product`'s price to the user's currency via `ICurrencyConverter`.**

1. **First cut — Constructor Injection into `ProductService`.** `ICurrencyConverter` represents an out-of-process resource (rates from a web service/DB), so it belongs in a data access library — there is **no reasonable Local Default**. `ProductService` is application component code that *requires* it. Walking the tree: need it → component → application code ⇒ **Constructor Injection**. Mary adds it as a third constructor argument alongside `IProductRepository` and `IUserContext`, guards all three, stores them `readonly`.

2. **Refinement — move conversion into the `Product` Entity.** Currency conversion recurs across the app, so Mary centralizes it on the `Product` Entity to avoid duplication. But `Product` is a **data-centric domain object**, created inside the repository, *not* in the Composition Root. Injecting `ICurrencyConverter` through `Product`'s constructor would force every `Product` to be built with all its Dependencies even when unused — complicating construction and testing. Re-walking the tree: need it → *who needs it?* → data-centric object ⇒ **Method Injection**.

   ```csharp
   public Product ConvertTo(Currency currency, ICurrencyConverter converter)
   {
       if (currency == null)  throw new ArgumentNullException("currency");
       if (converter == null) throw new ArgumentNullException("converter");
       var newUnitPrice = converter.Exchange(this.UnitPrice, currency);
       return this.WithUnitPrice(newUnitPrice);   // uses, doesn't store
   }
   ```

   `GetFeaturedProducts` now passes the injected `converter` on to each `Product.ConvertTo(...)`. Note the two patterns compose: `ProductService` *received* `ICurrencyConverter` via Constructor Injection and *passes it on* via Method Injection — it uses/forwards the Dependency without storing it in the Entity. Same Dependency, differing consumers per call — the classic Method Injection case.

**Outcome:** Constructor Injection for the long-lived service; Method Injection for the short-lived Entity. Property Injection never entered consideration — this is application code, not a reusable library.

## Key Takeaways

1. **Constructor Injection is the default.** It is the most generally applicable, most reliable, and easiest DI pattern to implement correctly; you can build entire applications with it alone. When in doubt, choose it — you can't go terribly wrong.
2. **Compose at the entry point.** Concentrate all object-graph construction into one Composition Root as close to `Main` as possible; it's the sole place that knows the graph's structure and the only place a DI Container may appear.
3. **Keep constructors dumb.** A Constructor-Injection constructor does nothing but apply Guard Clauses and store Dependencies in `readonly` fields — making object graphs fast and reliable. One public constructor per application component.
4. **Dependencies should hardly ever be optional.** Instead of null-checking optional Dependencies, make them required and inject a **Null Object** from the Composition Root when no real implementation exists.
5. **Use Method Injection when the Dependency or its consumer varies per operation** — add-ins receiving context, or domain Entities — always *outside* the Composition Root, and never store the injected Dependency (that breeds Temporal Coupling).
6. **Reserve Property Injection for reusable libraries** with a good Local Default and a genuinely optional Dependency. In application code, never use it — Constructor Injection is simpler and more robust.
7. **The dependency "explosion" is a myth.** Because assembly dependencies are transitive, loosely coupled code with a Composition Root has *fewer* total module-to-module dependencies than tightly coupled code.

## Connects To

- **Chapter 3 (writing loosely coupled code):** this chapter formalizes the patterns the e-commerce example used implicitly; Listing 4.1 is chapter 3's object graph.
- **Chapter 5 (DI anti-patterns):** the antitheses of these patterns — **Control Freak**, **Service Locator** (the antithesis of DI), **Ambient Context**, and **Constrained Construction**. Each pattern here guards against one of them.
- **Chapter 6 (DI code smells):** **Constructor Over-injection** (too many Dependencies), Cyclic Dependencies; general solutions that move code toward these patterns.
- **Chapter 7 (application frameworks):** how to enable Constructor Injection despite framework Seams like MVC's `IControllerActivator`.
- **Chapter 8 (object lifetime):** Captive Dependencies, and delaying/optimizing large object-graph creation.
- **Chapters 9–10 (interception & aspects):** Decorators and the Open/Closed Principle that Property Injection and Abstractions enable.
- **SOLID principles:** Single Responsibility (dumb constructors), Open/Closed (Property Injection extensibility), Dependency Inversion (program against Abstractions), plus the Null Object and Strategy patterns.
