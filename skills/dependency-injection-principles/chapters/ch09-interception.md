# Chapter 9: Interception

## Core Idea

**Interception** is the ability to intercept calls between two collaborating components — a consumer and a service — so you can enrich or change the behavior of the Dependency *without changing either collaborator*. You run your own code before, after, or instead of the real service invocation.

This power falls directly out of loose coupling. When you program to an interface (an Abstraction), you can transform or enhance a core implementation by wrapping it in another implementation of that same interface. At its core, Interception is nothing more than an application of the **Decorator** design pattern. The whole edifice rests on DI principles — loose coupling and the Liskov Substitution Principle — without them, Interception is impossible.

The payoff: you can apply the Single Responsibility Principle and Separation of Concerns with ease, harvesting **Cross-Cutting Concerns** (logging, auditing, security, caching, fault tolerance) as reusable wrappers rather than tangling them into feature code. The cooking metaphor: a plain veal cutlet becomes cordon bleu by *adding* to it — breading and filling — never by changing the core ingredient.

## Frameworks Introduced

**Decorator for interception**

*When to use it* — Apply a Decorator when you need to add a **Cross-Cutting Concern** (auditing, logging, validation, security, caching, error handling, fault tolerance) to an existing service without modifying that service or its consumers. It is the tool of choice whenever a concern "cuts across" many features and you want to honor the **Open/Closed Principle** (add new types instead of editing existing ones).

*How it works* — A Decorator implements the *same* Abstraction it wraps and holds a reference (the *decoratee*) to another implementation of that Abstraction, injected via Constructor Injection. Each method:
1. optionally acts on the input,
2. delegates to `this.decoratee.Method(...)`,
3. optionally acts on the return value or exception.

Because the wrapper and the wrapped share one interface, a Composer can slot the Decorator in front of the real service transparently. Decorators nest like Russian nesting dolls — a pipeline of interception — with a self-contained "actual component" at the core.

## Key Concepts

1. **Interception** — Intercept calls between consumer and service; enrich/change the Dependency's behavior without changing either collaborator.
2. **Decorator design pattern** (Gamma et al., 1994) — "Attach additional responsibilities to an object dynamically." A flexible alternative to subclassing; the wrapper implements and wraps the same Abstraction.
3. **Cross-Cutting Concerns** — Non-functional aspects (often non-functional requirements) that touch many unrelated areas across modules and layers: auditing, logging, performance monitoring, validation, security, caching, error handling, fault tolerance. In layered diagrams they are the vertical blocks spanning all layers.
4. **Decoratee** — The wrapped instance the Decorator delegates to, injected as the *abstract* type (the interface, not a concrete class).
5. **Nesting / pipeline** — A Decorator can wrap another Decorator, composing input-modifying and output-modifying behaviors in one chain.
6. **Guard Clause** — Early check inside a Decorator method that may short-circuit (return default or throw) *without* invoking the decoratee — used for null defaults or authorization.
7. **Replace vs. enrich** — Skipping the decoratee *replaces* behavior (edging toward Chain of Responsibility); delegating and adding *enriches* it. Enriching is the norm.
8. **Liskov Substitution Principle** — Since the Decorator wraps the interface, it must treat all decorated objects equally and remain substitutable.
9. **Open/Closed Principle** — Adding behavior via new Decorator types, never editing `SqlUserRepository` etc., keeps existing code closed to modification but open to extension.
10. **"Circuit Breaker"** — A stability pattern (Nygard, *Release It!*) that fails fast when an out-of-process resource errors, preventing fault propagation; a canonical complex Cross-Cutting Concern.

## Mental Models

- **Breaded cutlet** — The core service is the raw cutlet; each Decorator is a layer of breading. It embellishes without altering the ingredient, and the breading itself has substance (its own injected Dependencies, e.g. `IAuditTrailAppender`).
- **Russian nesting dolls (Matryoshka)** — Outermost Decorator → inner Decorator → actual component. A call travels inward; each layer gets a shot at the input on the way in and the return value on the way out.
- **Vertical slice beside the layers** — A Cross-Cutting Concern is drawn as a vertical bar spanning UI, domain, and data layers, because it belongs to none of them yet touches all.
- **Circuit Breaker as an electrical switch** — Closed = current flows; an error *trips* it Open (no calls pass, throws immediately); after a timeout it goes Half-Open to test a single call, then back to Closed on success or Open on failure.

## Anti-patterns

- **Baking the concern into the service** — Injecting `IAuditTrailAppender` into `SqlUserRepository` itself forces the repository to know about auditing: a Single Responsibility Principle violation. Use a Decorator instead.
- **Editing existing classes to add behavior** — Modifying `SqlUserRepository` or the consumer to add a concern violates the **Open/Closed Principle**.
- **Suppressing all exceptions** — An error-handling Decorator that catches `Exception` broadly is dangerous; catch only a known set (`CommunicationException`, `InvalidOperationException`).
- **Tripping the breaker on the wrong errors** — Trip on timeouts/communication errors, not on bugs like `NullReferenceException`; ideally use a threshold, not a single sporadic error.
- **Wrong lifestyle for stateful Decorators** — A stateful `CircuitBreaker` created Transient means multiple breakers guard one shared remote service, defeating its purpose; it wants Singleton (which then demands explicit thread-safety).
- **Per-method code duplication** — The real weakness: each Decorator repeats the same template across every interface method, and again for every new Abstraction. This maintainability drag is what motivates Aspect-Oriented Programming (Chapter 10).

## Code Examples

```csharp
// Auditing as a Cross-Cutting Concern via the Decorator pattern.
public class AuditingUserRepositoryDecorator : IUserRepository
{
    private readonly IAuditTrailAppender appender;
    private readonly IUserRepository decoratee;

    // Constructor Injection: wrap any IUserRepository, plus the audit service.
    public AuditingUserRepositoryDecorator(
        IAuditTrailAppender appender,
        IUserRepository decoratee)
    {
        this.appender = appender;
        this.decoratee = decoratee;
    }

    public User GetById(Guid id)          // Pure read: no auditing, just delegate.
    {
        return this.decoratee.GetById(id);
    }

    public void Update(User user)         // Write: delegate, THEN audit on success.
    {
        this.decoratee.Update(user);
        this.appender.Append(user);
    }
}
```

**What it demonstrates** — A Decorator implements the same Abstraction (`IUserRepository`) it decorates, delegates the real work to its `decoratee`, and adds the cross-cutting behavior (auditing) only where needed. Reads pass straight through; writes are enriched *after* the delegated call returns successfully. Neither `SqlUserRepository` nor its consumers change — Single Responsibility and Open/Closed are both preserved.

## Reference Tables

Common **Cross-Cutting Concerns** (illustrative, not exhaustive):

| Aspect | What it does |
|---|---|
| Auditing | Records data-altering operations: timestamp, who, what changed. |
| Logging | Records events reflecting application/business state (broader than auditing). |
| Performance monitoring | Captures performance data (e.g. custom counters) for SLAs. |
| Validation | Invokes and processes validation results around operations. |
| Security | Restricts operations to authorized users/roles. |
| Caching | Adds/removes caching per data-access implementation without touching it. |
| Error handling | Catches, logs, transforms, or surfaces exceptions to the user. |
| Fault tolerance | Robustness patterns such as **Circuit Breaker** around flaky out-of-process calls. |

Composing a decorated service (wiring, honoring Open/Closed):

```csharp
IAuditTrailAppender appender = new SqlAuditTrailAppender(userContext, context);

IUserRepository userRepository =
    new AuditingUserRepositoryDecorator(          // Decorator...
        appender,
        new SqlUserRepository(context));          // ...wraps the real repo.
// ProductService sees only IUserRepository — knows nothing of the Decorator.
```

## Worked Example

**Reconstructing a "Circuit Breaker" Decorator around a repository.**

`WcfProductRepository` calls a remote WCF service and has no error handling, so any communication error bubbles up. We want to *fail fast* once errors start, to avoid blocking threads and swamping the service. We intercept with a Decorator that delegates its state logic to a reusable `ICircuitBreaker` (Guard / Succeed / Trip, backed by the State pattern).

```csharp
public class CircuitBreakerProductRepositoryDecorator : IProductRepository
{
    private readonly ICircuitBreaker breaker;
    private readonly IProductRepository decoratee;

    public CircuitBreakerProductRepositoryDecorator(
        ICircuitBreaker breaker,
        IProductRepository decoratee)
    {
        this.breaker = breaker;
        this.decoratee = decoratee;
    }

    public void Insert(Product product)
    {
        this.breaker.Guard();                 // Open -> throws immediately (fail fast).
        try
        {
            this.decoratee.Insert(product);   // Closed/Half-Open let the call through.
            this.breaker.Succeed();           // Success: Half-Open -> Closed, or stay Closed.
        }
        catch (Exception ex)                  // (Real code: only trip on selected types.)
        {
            this.breaker.Trip(ex);            // Failure: -> Open, starts the timeout.
            throw;
        }
    }

    public IEnumerable<Product> GetAll()
    {
        this.breaker.Guard();
        var products = this.decoratee.GetAll(); // Methods returning a value must hold it...
        this.breaker.Succeed();
        return products;                         // ...before returning, to signal success.
    }
}
```

Composition wires a `CircuitBreaker` (with a timeout) around the real repository — ideally Singleton so one breaker governs the single remote endpoint, which in turn requires thread-safety because the breaker holds state:

```csharp
var timeout = TimeSpan.FromMinutes(1);
ICircuitBreaker breaker = new CircuitBreaker(timeout);

IProductRepository repository =
    new CircuitBreakerProductRepositoryDecorator(
        breaker,
        new WcfProductRepository(channelFactory));
```

The lesson: you can **Intercept** with arbitrarily complex logic — the Cross-Cutting Concern (the breaker) can be more complex than the core implementation it wraps. A breaker still *throws* (just faster), so it is often stacked with an `ErrorHandlingProductRepositoryDecorator` that catches known exceptions and alerts the user, and a `SecureProductRepositoryDecorator` whose Guard Clause checks `IUserContext.IsInRole(...)` before create/update/delete operations — three Decorators nested around one repository.

## Key Takeaways

1. **Interception = Decorator applied to DI.** Wrapping one implementation of an Abstraction in another of the same Abstraction lets you enrich behavior without changing consumer or service.
2. **Loose coupling and LSP are the enablers.** Without programming to interfaces and substitutability, Interception cannot exist.
3. **Cross-Cutting Concerns belong in Decorators, not in services.** Auditing, logging, security, caching, error handling, and fault tolerance stay out of the core, upholding Single Responsibility.
4. **Adding types beats editing code** — every Decorator you introduce instead of modifying an existing class honors the **Open/Closed Principle**.
5. **Decorators nest** into pipelines (Circuit Breaker → error handling → security), each layer touching input and/or output; a self-contained component sits at the core.
6. **Mind the lifestyle of stateful Decorators** — a "Circuit Breaker" wants Singleton scope and therefore explicit thread-safety.
7. **The per-method duplication is the catch** — repeating the same template across methods and Abstractions is the pain that motivates Aspect-Oriented Programming.

## Connects To

- **Chapter 8 (Object Composition)** — Interception is where the loose-coupling investment pays off; the Virtual Proxy in listing 8.19 was an early wrapping example, and Composers wire Decorators into the object graph.
- **Chapter 6 (DI patterns)** — The auditing example revisits the `IAuditTrailAppender` used to fix Dependency cycles, now relocated into a Decorator.
- **Chapter 4 / SOLID** — Direct expression of the Open/Closed, Single Responsibility, and Liskov Substitution Principles.
- **Chapter 10 (Aspect-Oriented Programming)** — The next step: eliminating the code duplication that hand-written Decorators produce across methods and Abstractions.
- **GoF patterns** — Decorator, Chain of Responsibility (skip-the-decoratee variant), State (inside `CircuitBreaker`); Nygard's *Release It!* for the Circuit Breaker stability pattern.
