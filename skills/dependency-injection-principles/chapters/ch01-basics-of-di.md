# Chapter 1: The basics of Dependency Injection: What, why, and how

## Core Idea
Dependency Injection is a set of design principles and patterns that enables loose coupling, which is the practical route to maintainable code — it is a means to an end (maintainability), not a goal, and it revolves entirely around injecting **Volatile Dependencies** into consumers rather than letting consumers create them.

## Frameworks Introduced
- **Stable vs. Volatile Dependency classification**: the decision tool for *what to inject and what not to inject*. You do not abstract everything; you introduce a **Seam** only around Volatile Dependencies.
  - When to use: whenever you reference a type and must decide whether to program against an Abstraction or use it directly.
  - How — treat a Dependency as **Volatile** (inject it) if ANY criterion holds: (1) it requires setting up/configuring a runtime environment (DB, filesystem, message queue, web service, other out-of-process resource); (2) it doesn't yet exist / is still in development; (3) it isn't installed on all dev machines (expensive/OS-bound third-party libs); (4) it has nondeterministic behavior (random, `DateTime.Now`, crypto RNG). Otherwise treat it as **Stable** (use directly). Stable criteria: already exists, no expected breaking changes, deterministic algorithm, never expected to replace/wrap/decorate/Intercept.

- **DI in three dimensions**: DI encompasses Object Composition, Object Lifetime, and Interception.
  - When to use: as the mental frame for the whole book — Composition is the foundation, Lifetime handles side effects, Interception is where you reap benefits.
  - How: compose classes at the entry point; let a third party control when instances are created/disposed; wrap Dependencies (Decorator) before passing them to consumers.

## Key Concepts
- **Dependency Injection (DI)**: a set of software design principles and patterns that enables you to develop loosely coupled code.
- **Constructor Injection**: statically defining a class's required Dependencies by declaring them as constructor parameters; the preferred injection method.
- **Pure DI**: applying DI without a DI Container (composing objects by hand). Replaces the 1st-edition term **Poor Man's DI**.
- **DI Container**: an optional library that eases wiring an application; useful but never required — reference it only at the entry point.
- **Volatile Dependency**: a Dependency that threatens loose-coupling benefits (needs runtime setup, is nondeterministic, unavailable, or in development) — the focal point of DI.
- **Stable Dependency**: a Dependency that is safe to consume directly (already exists, deterministic, backward-compatible, never wrapped/replaced).
- **Seam**: a place where an application is assembled from its parts (wherever you program against an Abstraction instead of a concrete type); lets you take the app apart and work with modules in isolation.
- **Object Composition**: the task, taken away from consumers, of creating instances of Dependencies and assembling them into an application.
- **Interception**: modifying/wrapping a Dependency before passing it to its consumer; an application of the Decorator pattern, the path toward AOP and Cross-Cutting Concerns.
- **Service Locator**: an "Abstract Factory on steroids" with an unspecified, endless list of resolvable types — the exact *opposite* of DI (an anti-pattern).
- **Test Double**: a stand-in implementation of a Dependency (Stub, Mock, Fake, Spy) used only in tests; enabled by loose coupling via the Liskov Substitution Principle.

## Mental Models
- **Sockets and plugs**: an interface is a socket; an implementation is a plug. Tightly coupled code is a hair dryer hardwired into the wall; loose coupling lets anyone swap appliances. This maps GoF patterns directly: swapping plugs = Liskov Substitution, a safety-plug = Null Object, a UPS in-line = Decorator, a power strip = Composite, a travel adapter = Adapter.
- **Inject only what's Volatile**: don't abstract every BCL type. Ask "does this Dependency threaten late binding, extensibility, parallel development, or Testability?" If yes, put a Seam around it.
- **DI is the opposite of a Service Locator**: never *ask* for Dependencies imperatively; *require* consumers to *supply* them (state a need — "something to drink with lunch" — rather than raiding the fridge).
- **Think of DI as pervasive, not retrofittable**: loose coupling only pays off when it's everywhere; you can't easily bolt it onto an existing tightly coupled code base.

## Anti-patterns
- **Service Locator**: classes ask a third party for their Dependencies. It hides dependencies and inverts DI's intent (covered as an anti-pattern in ch. 5).
- **Believing DI requires a DI Container**: a myth; leads to over-tooling. Pure DI is fully legitimate.
- **Treating DI as an Abstract Factory / general-purpose factory**: conflates DI with Service Locator.
- **Constrained Construction**: the shortcut of late-binding via `Activator.CreateInstance` on a config-supplied type name (shown in listing 1.2) — covered in ch. 5.
- **Over-abstracting Stable Dependencies**: adds Seams (extra work) with no payoff.

## Code Examples
```csharp
public class Salutation
{
    private readonly IMessageWriter writer;

    public Salutation(IMessageWriter writer)         // Constructor Injection
    {
        if (writer == null)
            throw new ArgumentNullException("writer"); // Guard Clause
        this.writer = writer;
    }

    public void Exclaim()
    {
        this.writer.Write("Hello DI!");
    }
}
```
- **What it demonstrates**: Constructor Injection with a Guard Clause — `Salutation` depends only on the `IMessageWriter` Abstraction and has no awareness of the concrete `ConsoleMessageWriter`.

## Reference Tables
Benefits gained from loose coupling (each is always available but valued differently):

| Benefit | Description | When is it valuable? |
|---|---|---|
| Late binding | Services swapped without recompiling code | Valuable in standard software; less so in enterprise apps with a well-defined runtime |
| Extensibility | Code extended/reused in unplanned ways | Always valuable |
| Parallel development | Code developed in parallel | Valuable in large, complex apps; not small ones |
| Maintainability | Clearly-defined responsibilities ease maintenance | Always valuable |
| Testability | Classes can be unit tested | Always valuable |

## Worked Example
**Hello DI!** — a one-line "Hello World" deliberately made more complex to expose DI's shape. The composition happens in `Main` (Pure DI, no container):

```csharp
private static void Main()
{
    IMessageWriter writer = new ConsoleMessageWriter();
    var salutation = new Salutation(writer);
    salutation.Exclaim();
}
```

`ConsoleMessageWriter : IMessageWriter` wraps `Console.WriteLine` — a small Adapter over the BCL. A **Seam** exists between `Salutation` and `ConsoleMessageWriter` because `Salutation` writes only through the `IMessageWriter` Abstraction. The chapter then shows the three benefits *without touching `Salutation`*:
- **Extensibility (Decorator)**: add `SecureMessageWriter : IMessageWriter` that also *consumes* `IMessageWriter` plus `IIdentity`, writing only if authenticated. Compose it in `Main` by wrapping: `new SecureMessageWriter(new ConsoleMessageWriter(), WindowsIdentity.GetCurrent())`. Open for extension, closed for modification.
- **Testability (Test Spy)**: inject a `SpyMessageWriter` in a `[Fact]` unit test, exercise `sut.Exclaim()`, and `Assert.Equal("Hello DI!", writer.WrittenMessage)`.
- **Late binding**: optionally pull the concrete type name from `appsettings.json` and reflectively `Activator.CreateInstance` it — but this shortcut is the Constrained Construction anti-pattern.

## Key Takeaways
1. Inject **Volatile Dependencies** via Constructor Injection; consume **Stable Dependencies** directly — classify before abstracting.
2. Program to interfaces (Abstractions), not implementations; the only hard question ("where do instances come from?") is what DI answers.
3. Prefer **Constructor Injection**; add a **Guard Clause** to reject null Dependencies.
4. You don't need a **DI Container** — **Pure DI** (hand-composition in the entry point) upholds every DI principle.
5. Never use a **Service Locator**; require consumers to be supplied their Dependencies, don't let them ask.
6. Move all object creation to the application entry point (Composition Root idea) — one place to compose, Intercept, and manage lifetimes.
7. Apply DI **pervasively**; loose coupling can't be effectively retrofitted onto a tightly coupled code base.

## Connects To
- **Ch 2–3**: a larger, more realistic example that makes the maintainability payoff visible where Hello DI! makes DI look like overengineering.
- **Ch 4**: Constructor Injection in depth, the Null Object pattern, and the Open/Closed Principle.
- **Ch 5**: why Service Locator is an anti-pattern; the Constrained Construction anti-pattern.
- **Ch 8 / 9 / 10–11**: the three dimensions — Object Lifetime; Interception (Decorator); Aspect-Oriented Programming and Cross-Cutting Concerns.
- **SOLID principles**: Liskov Substitution (enables substitutable implementations), Single Responsibility (removing Dependency creation from consumers), Open/Closed (extend by adding classes).
- **Inversion of Control (IoC)**: DI is a subset of IoC — IoC over Dependencies specifically (Martin Fowler's coinage).
- **Working Effectively with Legacy Code** (Feathers): source of the **Seam** concept and the "legacy = untested code" definition.
