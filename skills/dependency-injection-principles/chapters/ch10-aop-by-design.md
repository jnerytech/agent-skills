# Chapter 10: Aspect-Oriented Programming by design

## Core Idea

**Aspect-Oriented Programming (AOP)** is a paradigm for applying **cross-cutting
concerns** (auditing, logging, security, transactions, caching, fault tolerance)
effectively and maintainably — implementing each concern *once*, in a single
place, and applying it broadly "without modifying the code itself." Its central
enemy is repetition: naive Decorators duplicate near-identical plumbing across
every method of every Abstraction, violating DRY.

The chapter's thesis is that **AOP does not require tooling**. This is "AOP by
design" — you drive AOP with well-known design patterns (the Decorator) and the
five **SOLID** principles *before* reaching for specialized tools like dynamic
Interception libraries or compile-time weavers (covered in ch. 11, both with
serious disadvantages). SOLID is not just a checklist; each principle actively
*pushes* a design toward the shape where a single Decorator can carry an aspect
across the whole application. Applied rigorously, SOLID makes an entire codebase
converge on **one-membered generic Abstractions** (e.g. `ICommandService<TCommand>`),
onto which one Decorator per aspect can be layered — no sweeping changes when
adding features *or* concerns.

## Frameworks Introduced (AOP-by-design; each SOLID principle as a driver)

- **AOP by design** — the "most ideal form" of AOP: apply aspects using
  Decorators around reusable Abstractions defined for groups of classes by
  behavior. Advantages: no tooling, aspects easy to implement, focuses on design,
  improves maintainability. Contrast with the two tool-based methods:
  - *Dynamic Interception* — runtime-generated Decorators (Interceptors); easy to
    retrofit but couples aspects to the AOP tool and loses compile-time support.
  - *Compile-time weaving* — IL weaving rewrites the compiled assembly; described
    as "the antithesis of DI" because aspects are baked in and cannot be composed
    or omitted.
- **SRP as driver** — separates a concern into its own class so it *can* become a
  Decorator with a specifically defined scope.
- **OCP as driver** — the direct motivation for AOP: extend behavior (add an
  aspect) without modifying existing classes; strongly related to DRY.
- **LSP as driver** — makes a Decorator a safe drop-in for the class it wraps;
  the foundation that makes injecting Dependencies worthwhile at all.
- **ISP as driver** — pushes toward fine-grained (ideally one-membered)
  Abstractions, which is "crucial when it comes to effectively applying AOP."
- **DIP as driver** — the consumer owns the Abstraction's shape, keeping
  interfaces narrow and stable so aspects attach cleanly.

## Key Concepts

- **Cross-cutting concern** — functionality (auditing, logging, security,
  transactions, validation, performance monitoring, fault tolerance) needed across
  many use cases, orthogonal to core business logic.
- **Aspect** — a single, reusable implementation of a cross-cutting concern,
  applied to many operations; in AOP-by-design, an aspect is a Decorator.
- **Single Responsibility Principle (SRP)** — every class should have exactly one
  reason to change. Judge via *cohesion* (functional relatedness of a class's
  elements); low cohesion signals an SRP violation. Constructor Injection makes
  violations more obvious.
- **Open/Closed Principle (OCP)** — a class should be open for extension, closed
  for modification: extend behavior without editing existing source. Closely tied
  to DRY (OCP focuses on *code*; DRY on *knowledge*). Full closure is neither
  possible nor desirable — balance risk against cost.
- **Liskov Substitution Principle (LSP)** — any implementation of an Abstraction
  must be substitutable for another without breaking consumers; every Dependency
  must behave as its Abstraction defines. The foundation of DI.
- **Interface Segregation Principle (ISP)** — prefer fine-grained over wide
  Abstractions; a consumer forced to depend on members it doesn't use signals a
  violation. ISP is "the conceptual underpinning of the SRP."
- **Dependency Inversion Principle (DIP)** — program against Abstractions, and the
  *consuming* layer controls the Abstraction's shape. Adding members to satisfy a
  specific implementation almost certainly violates DIP.
- **Parameter Object** — a group of parameters that naturally belong together;
  once a command's parameters are extracted into one, the object itself *becomes*
  the definition (contract) of the use case.
- **Command-Query Separation (CQS)** — each method either returns a result without
  changing state (query) or changes state without returning a value (command);
  propagated here from the method level to the interface level.

## Mental Models

- **SOLID is a gravitational pull, not a gate.** Applying the principles honestly
  doesn't just *permit* AOP — it drags the design toward one-membered generic
  Abstractions where a single Decorator serves as an aspect. The end shape emerges;
  you don't design it up front.
- **Class count is a bad maintainability metric.** Refactoring 2 types into 15
  (one interface, 7 Parameter Objects, 7 services) *improved* maintainability,
  because sweeping changes became rare. Group by namespace/project, not by cramming
  methods into one class.
- **DI makes violations visible.** Constructor Injection surfaces SRP violations
  (too many dependencies); a DI Container surfaces LSP violations (ambiguous
  Abstractions complicate the Composition Root). The pain is diagnostic.
- **Design first, tools last.** Don't reject tool-based AOP outright, but your
  first instinct should be to improve design; reach for tooling only when design
  alone can't solve the maintainability problem.

## Anti-patterns

- **Aspect logic duplicated per method/Decorator.** A Circuit Breaker or auditing
  Decorator repeats identical try/Guard/Trip plumbing in every method — DRY and
  OCP violation. Repetition scales with feature count until adding features becomes
  too costly.
- **Wide "I...Service" interfaces** (`IProductService` with 10 methods). Violates
  ISP (no consumer uses all methods; Test Doubles must implement every member),
  which drags in an SRP violation (many reasons to change, low cohesion), which
  drags in an OCP violation (new features ripple through the implementation, every
  Decorator, and every Test Double).
- **Adding interface members to satisfy specific implementations** — DIP violation.
- **Ambiguous Abstractions** (a non-generic `ICommandService` taking `object` and
  casting internally) — an LSP violation: any implementation compiles but the wrong
  one breaks the consumer at runtime; also forces a cast code smell in every impl.

## Code Examples

```csharp
// The problem: aspect plumbing duplicated across every method (DRY/OCP violation).
public void Insert(Product product)
{
    this.breaker.Guard();
    try
    {
        this.decoratee.Insert(product);   // ONLY line that differs from Delete()
        this.breaker.Succeed();
    }
    catch (Exception ex)
    {
        this.breaker.Trip(ex);
        throw;
    }
}
```

**What it demonstrates:** cross-cutting Circuit Breaker logic is nearly identical
in every method; the sole difference is which decoratee method is called. Adding a
member or a new Abstraction re-copies the plumbing — the repetition AOP exists to
eliminate.

```csharp
// The destination: one generic, one-membered Abstraction...
public interface ICommandService<TCommand>
{
    void Execute(TCommand command);       // TCommand = the command type handled
}

// ...and ONE Decorator per aspect, covering every command in the codebase.
public class TransactionCommandServiceDecorator<TCommand>
    : ICommandService<TCommand>
{
    private readonly ICommandService<TCommand> decoratee;

    public TransactionCommandServiceDecorator(ICommandService<TCommand> decoratee)
        => this.decoratee = decoratee;

    public void Execute(TCommand command)
    {
        using (var scope = new TransactionScope())
        {
            this.decoratee.Execute(command);
            scope.Complete();
        }
    }
}
```

**What it demonstrates:** once SOLID collapses the design onto
`ICommandService<TCommand>`, a transaction (or auditing, logging, security…)
aspect is a *single* generic Decorator. Adding a concern = adding one class;
changing a concern = editing one class. No sweeping changes.

## Reference Tables

| SOLID principle | What it says | How it relates to AOP / DI |
|---|---|---|
| **SRP** | One class, one reason to change; measured by cohesion | Lets a concern be extracted into its own class so it can *become* an aspect (Decorator). Constructor Injection makes violations obvious. |
| **OCP** | Open for extension, closed for modification | The direct driver of AOP: add an aspect without editing existing code. Repetition/sweeping changes signal violation; closely tied to DRY. |
| **LSP** | Any implementation substitutes for its Abstraction without breaking clients | Foundation of DI. A Decorator must honor the wrapped Abstraction's contract to be a safe drop-in; violations make DI pointless and the system fragile. |
| **ISP** | Prefer fine-grained over wide Abstractions | "Crucial" for effective AOP: narrow (ideally one-membered) interfaces give a common shape onto which a single Decorator applies. |
| **DIP** | Program against Abstractions; the consumer owns the Abstraction's shape | Keeps interfaces narrow and stable so aspects attach cleanly; prevents members added for specific impls that would bloat the surface. |

## Worked Example

Mary's `IProductService` accreted 10 methods, violating **three** principles at
once: **ISP** (no consumer uses all methods; a `MockProductService` Test Double
must stub all 10 to `Assert` "should not be called"), **SRP** (many reasons to
change: discounts, inventory, search, new features — low cohesion), and **OCP**
(a new feature or a new concern ripples through the implementation, every
Decorator, and every Test Double).

Applying SOLID step by step drives the design to its natural conclusion:

1. **Separate reads from writes (CQS).** Split into `IProductQueryServices` and
   `IProductCommandServices` — finer-grained, but still causes sweeping changes.
2. **Fix ISP + SRP by segregating.** Break the 7-method command interface into
   seven one-membered interfaces, each with its own class (one use case per class).
   Now ISP- and SRP-clean — but 7 interfaces × 10 aspects = **70 Decorators**, with
   no commonality to exploit.
3. **Fix OCP with Parameter Objects.** Extract each method's parameters into a
   Parameter Object and rename the method `Execute`. A pattern emerges: every
   Abstraction has one method, named `Execute`, returning `void`, taking one input.
   Extract the common `ICommandService` — one Decorator per aspect now covers
   everything.
4. **Fix the accidental LSP violation.** The non-generic `ICommandService` takes
   `object` and casts inside `Execute`; injecting the wrong implementation compiles
   but fails the cast at runtime (fragile, and the DI Container surfaces the
   ambiguity). Redefine as generic `ICommandService<TCommand>`: `Execute` accepts
   the exact command type, no cast, and the compiler prevents supplying the wrong
   handler.

The Decorator/aspect wasn't imposed — it *emerged*. SOLID, followed honestly, made
`ICommandService<TCommand>` the only sensible shape, and onto that shape a single
`TransactionCommandServiceDecorator<TCommand>` (or auditing, security, logging…)
drops in cleanly. Notably this signature is identical to `IEventHandler<TEvent>`:
one-membered generic message handlers are the structure SOLID keeps producing
(elsewhere named `IHandler<T>`, `ICommandHandler<T>`, `IMessageHandler<T>`).

## Key Takeaways

1. **AOP by design beats tool-based AOP.** SOLID + Decorators apply cross-cutting
   concerns with no tooling, no lost compile-time safety, and better maintainability
   than dynamic Interception or compile-time weaving.
2. **OCP is the engine of AOP**, and DRY is its twin — both exist to minimize
   repetition and prevent sweeping changes.
3. **Each SOLID principle drives toward the aspect-friendly shape:** SRP isolates
   the concern, ISP narrows the interface, DIP keeps the consumer in control, LSP
   makes the Decorator substitutable, OCP demands extension without modification.
4. **Applied SOLID converges on one-membered generic Abstractions** onto which one
   Decorator per aspect fits — the domain/business-operation boundary
   (`ICommandService<TCommand>`), not the repository, is the right granularity.
5. **DI is a means, not an end** — it makes violations visible: Constructor
   Injection exposes SRP breaks; a DI Container exposes LSP breaks.
6. **Number of classes is a poor maintainability metric.** 2 → 15 types improved
   maintainability by making sweeping changes rare; organize with namespaces.

## Connects To

- **Chapter 9 (Interception / Decorators):** supplies the auditing, Circuit
  Breaker, and security Decorators whose repetition motivates this chapter.
- **Chapter 11 (Tool-based AOP):** dynamic Interception and compile-time weaving —
  the alternatives to reach for *only after* design fails; each with notable
  drawbacks.
- **Chapters 2, 3, 4, 6, 8:** the original, per-principle introductions of SRP,
  DIP, OCP, ISP, and LSP recapped here.
- **DRY & CQS:** cross-cutting design principles reinforcing OCP and the
  command/query split.
- **Decorator & Mediator patterns (GoF):** Decorator is the aspect vehicle;
  Mediator is the fallback when a language lacks generics.
