# Patterns & Techniques — DI Principles, Practices, and Patterns

## Composition Root
**When to use**: always — every application needs exactly one.
**How**: compose the entire object graph in a single location as close to the entry point as possible (`Main`, `Startup.ConfigureServices`, `Global.asax`, platform bootstrapper). Only this place references concrete types or the DI Container.
**Trade-offs**: centralizes all wiring (good). Must keep framework-imposed roots (activators, controller factories) thin and delegating.

## Constructor Injection *(default pattern)*
**When to use**: for required, static Volatile Dependencies — the 95% case.
**How**: declare an abstraction parameter in a single public constructor, Guard-Clause null-check it, assign to a `private readonly` field. The type advertises its dependencies as a compile-time contract.
**Trade-offs**: dependencies are explicit and immutable. Too many params → Constructor Over-injection smell (that's a feature — it surfaces SRP breaks).

## Method Injection
**When to use**: a dependency (often a runtime value) varies per call, or is passed down from the caller's context.
**How**: pass the abstraction as a method parameter; Guard-Clause it; do not store it.
**Trade-offs**: good for per-operation data; risks Temporal Coupling if the caller must sequence calls.

## Property Injection (Setter Injection)
**When to use**: the dependency is genuinely optional AND a good Local Default exists.
**How**: expose a settable property initialized to a safe Local Default (often a Null Object); Guard against null assignment.
**Trade-offs**: use sparingly — hides dependencies, invites Temporal Coupling. Never use it as a workaround for a required dependency.

## Pure DI (formerly Poor Man's DI)
**When to use**: small/medium apps, or when you want full compile-time checking and no container magic.
**How**: hand-write the object graph with `new` in the Composition Root.
**Trade-offs**: fully debuggable and refactor-safe; verbose as the graph grows. Switch to a container when maintenance of the root outweighs its clarity.

## Facade Services *(cures Constructor Over-injection)*
**When to use**: a constructor takes too many (~>4) related dependencies that cluster around a sub-responsibility.
**How**: extract the cluster behind a new, higher-level abstraction whose implementation aggregates them; inject the facade instead.
**Trade-offs**: reduces params and reveals a missing domain concept; don't create facades that are just data bags — they must carry behavior/policy.

## Decorator (for Interception)
**When to use**: add a Cross-Cutting Concern (logging, auditing, caching, retry, security, transactions) to an existing abstraction.
**How**: implement the same interface, take the wrapped instance as a constructor dependency, add behavior before/after delegating. Register it wrapping the real component in the Composition Root.
**Trade-offs**: honors OCP — no edits to the decorated class. Ordering of stacked decorators matters and is set at composition.

## AOP by design
**When to use**: cross-cutting concerns you can express through abstractions.
**How**: apply SOLID (especially SRP + OCP + DIP) so components become decoratable; realize aspects as decorators, not tooling.
**Trade-offs**: keeps code plain C#, fully debuggable; more boilerplate than tool-based weaving but no magic and no tool lock-in.

## Tool-based AOP (Dynamic Interception / Compile-time weaving)
**When to use**: only when design-based decorators would require an impractical number of near-identical wrappers.
**How**: Dynamic Interception = runtime dynamic proxies (Castle DynamicProxy); Compile-time weaving = IL rewriting (PostSharp/Fody), usually attribute-driven.
**Trade-offs**: less boilerplate but obscures control flow, complicates debugging, and couples you to a tool. The authors prefer design-based AOP.

## Register-Resolve-Release (RRR)
**When to use**: the mental model for any DI Container usage.
**How**: (1) Register all abstraction→implementation mappings with Lifestyles; (2) Resolve only the composition root object once; (3) Release/dispose the graph at end of scope.
**Trade-offs**: Resolve must be called only inside the Composition Root — calling it elsewhere is Service Locator.

## Auto-Registration
**When to use**: many components follow a naming/shape convention (e.g. all `I*Handler` → `*Handler`).
**How**: scan assemblies by convention and batch-register, instead of one line per type.
**Trade-offs**: less config churn as you add types; convention drift can silently miss or mis-map types — verify (e.g. Simple Injector `Verify()`).

## Breaking cyclic dependencies
**When to use**: A depends on B which depends back on A.
**How**: break the cycle by (1) splitting a responsibility, (2) introducing an event/domain event, or (3) using Property Injection on one side as a last resort. Prefer redesign over the property hack.
**Trade-offs**: usually reveals a genuine design flaw worth fixing at the root.
