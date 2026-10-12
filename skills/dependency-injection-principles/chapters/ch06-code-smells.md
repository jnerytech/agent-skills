# Chapter 6: Code smells

## Core Idea

A **code smell** is a hint that something *might* be wrong — not a certainty, and not an attack. It marks a construct that warrants a closer look, distinct from an **anti-pattern** (a common "solution" with decidedly negative consequences). This chapter is a catalog of the most common smells that surface when you apply DI, and their refactorings. The recurring root cause is a violation of the **Single Responsibility Principle** (SRP): DI doesn't create these problems, it *reveals* them. Constructor Injection makes an overloaded class impossible to ignore, so treat the discomfort as a gift, not a defect.

## Frameworks Introduced

- **Constructor Over-injection smell** → refactor via **Facade Services** or **domain events**.
- **Abuse of Abstract Factories** → two sub-cases: (a) factories used to manage lifetime → replace with a **Proxy**; (b) factories used to select a dependency from runtime data → replace with an **Adapter**.
- **Fixing cyclic Dependencies** → redesign strategies ordered from best to worst: split classes → .NET events → Property Injection (last resort) / Virtual Proxy.

## Key Concepts

1. **Code smell vs. anti-pattern.** A smell might cause problems and warrants investigation; an anti-pattern reliably causes them. Some items here (e.g. service Abstractions exposing service Abstractions) are called smells *because exceptions exist*.
2. **Constructor Over-injection.** When a constructor's parameter list grows too large it signals the class has too many responsibilities — an SRP violation magnified by, but not caused by, DI.
3. **The ~4-argument rule of thumb.** The authors' personal threshold is **four** constructor arguments; a third already prompts a rethink. Cross your limit → investigate.
4. **Facade Service.** An abstract Facade that hides a *natural cluster of interacting Dependencies, along with their behavior, behind a single Abstraction*. Related to Parameter Objects, but exposes only encapsulated *behavior*, not the constituents.
5. **Domain event.** A type capturing an action that can trigger a change to application state. Promoting notifications to explicit types + a generic `IEventHandler<TEvent>` removes ever-growing notification interfaces.
6. **Leaky Abstraction.** An interface leaking implementation details (layer-specific types, or `IDisposable`). Parameterless factory `Create()` methods and disposable Abstractions are Leaky Abstractions.
7. **Abstract Factory abuse.** Factories injected as Dependencies are often overused. Legitimate factories *conceptually require a runtime value*; introducing one just to build a known concrete type signals a Leaky Abstraction.
8. **Cyclic Dependency.** A depends on B whose implementation depends on A — an object graph that can't be satisfied. Object graph is cyclic even when the *method call* graph isn't recursive. Typically caused by an SRP violation.
9. **Interface Segregation Principle (ISP).** "No client should be forced to depend on methods it doesn't use." The conceptual underpinning of the SRP; thin interfaces ease Proxies, Decorators, and Test Doubles.

## Mental Models

- **Chicken-or-egg.** A cyclic dependency is the causality dilemma made literal: each class needs the other to already exist before it can be constructed. No composition order works until you cut the cycle.
- **The smell as a smoke alarm.** Over-injection isn't the fire; it's the alarm telling you a class took on too much. Silencing it (moving args to Property Injection or a base class) mutes the alarm without lowering complexity — the wrong fix.
- **Conceptually one instance.** From a consumer's viewpoint there is exactly one instance of a service Abstraction. Any construct (a parameterless factory) that leaks "there are many, and you must manage them" is not designed for the consumer's benefit.
- **Natural clusters.** Refactoring to Facade Services isn't a trick to shrink parameter lists — it surfaces implicit domain concepts (e.g. "order fulfillment") and makes them explicit.

## Anti-patterns

### Abuse of Abstract Factories
- **What:** Injecting an `IThingFactory` with a parameterless `Create()` (to control a Dependency's lifetime), or a `Create(runtimeData)` that *selects* which implementation to return.
- **Why it fails:** The factory is a Leaky Abstraction — it tells consumers "there are multiple instances / this one is disposable," coupling them to implementation details. It also silently *increases* the dependency count: a consumer of `IRouteAlgorithmFactory` really depends on both the factory *and* `IRouteAlgorithm`, which bites hard in unit tests.
- **Fix (lifetime):** Delete the factory; inject the Dependency directly. Move deterministic cleanup to a **Proxy** in the Composition Root (`SqlProductRepositoryProxy` keeps its factory-like `Create()` *encapsulated*, so nothing leaks). Abstractions must not implement `IDisposable`.
- **Fix (runtime selection):** Replace the factory with an **Adapter** (`IRouteCalculator`) that internally dispatches (e.g. a `Dictionary<RouteType, IRouteAlgorithm>`), so the consumer has one Dependency, not two. General guideline: *service Abstractions shouldn't expose other service Abstractions in their definition.*

### Cyclic Dependencies
- **What:** `Chicken(IEgg)` and `Egg(IChicken)` — an unsatisfiable object graph. Real case: adding `IAuditTrailAppender` to `SqlUserRepository` closes a loop through `AspNetUserContextAdapter` → `IUserRepository` → back to the appender; the Composition Root won't compile.
- **Why it fails:** Typically an **SRP violation** — a broad class (`IUserRepository` grouped everything "user") is pulled in two directions. Ever-changing Abstractions are the tell.
- **Fix:** Split the class (extract `GetByName` into `IUserByNameRetriever`, which does *not* depend on the appender) — this breaks the cycle and is the preferred solution. Fallbacks: raise **.NET events** instead of invoking a Dependency; as a **last resort**, refactor one class from Constructor Injection to **Property Injection** (or wrap it in a **Virtual Proxy**) — this only treats symptoms and introduces Temporal Coupling.

## Code Examples

```csharp
// SMELL: Constructor Over-injection — five Dependencies signal an SRP violation.
public class OrderService : IOrderService
{
    public OrderService(
        IOrderRepository orderRepository,
        IMessageService messageService,
        IBillingSystem billingSystem,
        ILocationService locationService,
        IInventoryManagement inventoryManagement) { /* ... */ }

    public void ApproveOrder(Order order)
    {
        this.UpdateOrder(order);   // saves the order
        this.Notify(order);        // messaging + billing + fulfillment
    }
}
```

```csharp
// FIX (step 1): a Facade Service hides a natural cluster (location + inventory).
public interface IOrderFulfillment { void Fulfill(Order order); }

public class OrderFulfillment : IOrderFulfillment   // 2 deps — fine
{
    public OrderFulfillment(
        ILocationService locationService,
        IInventoryManagement inventoryManagement) { /* ... */ }

    public void Fulfill(Order order)
    {
        this.locationService.FindWarehouses(/* ... */);
        this.inventoryManagement.NotifyWarehouses(/* ... */);
    }
}

// FIX (step 2): unify all notifications behind one Abstraction + a Composite.
public interface INotificationService { void OrderApproved(Order order); }

public class CompositeNotificationService : INotificationService
{
    private readonly IEnumerable<INotificationService> services;
    public CompositeNotificationService(IEnumerable<INotificationService> services)
        => this.services = services;
    public void OrderApproved(Order order)
    {
        foreach (var service in this.services) service.OrderApproved(order);
    }
}

// RESULT: OrderService drops from five Dependencies to two.
public class OrderService : IOrderService
{
    public OrderService(
        IOrderRepository orderRepository,
        INotificationService notificationService) { /* ... */ }

    public void ApproveOrder(Order order)
    {
        this.UpdateOrder(order);
        this.notificationService.OrderApproved(order);
    }
}
```

**What it demonstrates:** Constructor Injection makes the SRP violation *visible* (five args). Facade Services collapse a natural cluster (`OrderFulfillment`) and a Composite unifies three notifiers behind one interface — dropping `OrderService` to two constructor arguments *without* changing its observable behavior (a true refactoring). Wiring stays in the Composition Root; no single constructor exceeds two parameters.

## Reference Tables

| Strategy for breaking a Dependency cycle | When / cost |
|---|---|
| **Split classes** (preferred) | Class has too many methods; extract a narrower interface so one side no longer needs the other. Cures the root SRP violation. |
| **.NET events** | One side only invokes `void` methods on the other; raise an event instead of holding the Dependency. |
| **Property Injection** (last resort) | Design can't be changed. Cut where it "hurts least"; introduces Temporal Coupling and signals an *optional* Dependency. |
| **Virtual Proxy** | Like Property Injection but keeps the original class's invariants intact — a lazy proxy takes the real Dependency via a settable property. |

| Abstract Factory misuse | Better alternative |
|---|---|
| Parameterless `Create()` to manage lifetime | Inject the Dependency directly; move cleanup to a **Proxy** in the Composition Root |
| `Create(runtimeData)` to select implementation | **Adapter** that dispatches internally (e.g. a dictionary) |

## Worked Example — Breaking Mary's cyclic Dependency

Mary adds an audit-trail feature. `SqlAuditTrailAppender` needs `IUserContext` to know the current user; `AspNetUserContextAdapter` (the `IUserContext`) needs `IUserRepository` to load users; and `SqlUserRepository.Update` now calls `IAuditTrailAppender.Append`. The Composition Root won't compile — `userContext` is used before it's declared, and shuffling the variable order just moves the error around. There's a cycle:

```
AspNetUserContextAdapter → IUserRepository → SqlUserRepository → IAuditTrailAppender → SqlAuditTrailAppender → IUserContext → (back to adapter)
```

The method call graph, notably, is *not* recursive — so it's not a stack overflow, it's a **design** problem. Root cause: `IUserRepository` groups everything "user" (retrieve, query, store) — too broad, an SRP violation.

**Refactor:** extract the read path. `GetByName` moves out of `IUserRepository` into a new `IUserByNameRetriever` / `SqlUserByNameRetriever`. Crucially, `SqlUserByNameRetriever` does *not* depend on `IAuditTrailAppender`. `AspNetUserContextAdapter` now depends on the thin `IUserByNameRetriever` instead of the whole repository, so the graph is acyclic and the Composition Root composes cleanly:

```csharp
var userContext = new AspNetUserContextAdapter(new SqlUserByNameRetriever(context));
var appender    = new SqlAuditTrailAppender(userContext, context, timeProvider);
var repository  = new SqlUserRepository(context, appender);
```

Splitting the class fixed the smell at its source. (Only if redesign were impossible would Mary fall back to Property Injection or a `LazyAuditTrailAppender` Virtual Proxy — treating the symptom, accepting Temporal Coupling.)

## Key Takeaways

1. **DI reveals design problems; it doesn't cause them.** Embrace the discomfort of a fat constructor — it's Constructor Injection alerting you to an SRP violation.
2. **More than ~4 constructor arguments is a smell.** The authors draw the line at four (rethink at three). Beyond your threshold, investigate — don't paper over it with Property Injection or a base class, which hide complexity without reducing it.
3. **Refactor Over-injection with Facade Services or domain events.** A Facade Service hides a natural cluster of Dependencies behind one Abstraction; domain events + a generic `IEventHandler<TEvent>` let you add features without touching existing code.
4. **Don't abuse Abstract Factories.** Legitimate factories need a runtime value that maps conceptually to an Abstraction. For lifetime, use a Proxy; for runtime selection, use an Adapter. A factory always adds a hidden Dependency and complexity.
5. **Service Abstractions shouldn't expose other service Abstractions** — doing so forces clients to know about both (a smell, not an absolute rule).
6. **A Dependency cycle is a design smell; find where you failed.** The usual cause is an SRP violation — split the offending class. Reserve Property Injection / Virtual Proxy for cases where redesign is genuinely out of your control.
7. **Thinner Abstractions solve many problems at once** — easier Proxies, Decorators, and Test Doubles, and fewer ISP/SRP violations.

## Connects To

- **Ch. 4 (Constructor Injection):** the pattern whose "over-use" this chapter diagnoses; Property Injection and its Temporal Coupling caveat come from here.
- **Ch. 3 (Dependency Inversion Principle):** the consumer owns and shapes the Abstraction — the lens used to condemn factory abuse.
- **Ch. 5 (anti-patterns):** the Control Freak anti-pattern (why a Proxy belongs in the Composition Root) and the smell/anti-pattern distinction.
- **Ch. 8 (Lifetime Management):** where disposal responsibility properly lives, instead of leaking through factories.
- **Ch. 9–10 (Interception / Aspect-Oriented Programming):** Decorators for Cross-Cutting Concerns as an alternative to injecting them; ISP as the enabler of effective DI + AOP.
- **SOLID principles:** SRP (root cause throughout), ISP (thin interfaces), OCP (add features without changing existing code).
