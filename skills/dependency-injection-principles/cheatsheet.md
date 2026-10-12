# Cheatsheet — DI Principles, Practices, and Patterns

## Inject or not? (Volatile vs Stable)
**Rule**: inject only **Volatile** Dependencies; `new` up **Stable** ones directly.
A dependency is **Volatile** if ANY holds → inject it:
- introduces a resource/external system (DB, filesystem, clock, network, config)
- nondeterministic / has side effects (`DateTime.Now`, `Random`, `Guid.NewGuid`)
- doesn't exist yet or must be swapped (test doubles, plug-ins)
Otherwise it's **Stable** (`string`, `List<T>`, value objects, pure algorithms) → just `new` it. Injecting stable deps is noise.

## Which DI pattern? (decision rule)
| Situation | Pattern |
|---|---|
| Required, static dependency | **Constructor Injection** (default) |
| Per-call value / caller-supplied context | **Method Injection** |
| Truly optional AND has a safe Local Default | **Property Injection** |
| Creating your own volatile dep with `new` | ❌ Control Freak — inject instead |
**Default**: *"When in doubt, Constructor Injection."*

## Anti-pattern smell → fix
| See this | It's | Fix |
|---|---|---|
| `new` on a volatile dependency | Control Freak | Constructor-inject the abstraction |
| Class pulls deps from a container/`ServiceLocator.Get<T>()` | Service Locator | Inject deps; resolve only in Composition Root |
| Static accessor (`Clock.Now`, static `Logger`) | Ambient Context | Inject an abstraction |
| Every impl must have identical ctor signature | Constrained Construction | Let the container/root build it freely |
| Overloaded ctor with a Foreign Default | Bastard Injection | Single ctor, inject the dependency |

## Code-smell thresholds
- **Constructor Over-injection**: constructor with **> ~4** dependencies → extract **Facade Services** (likely SRP breach).
- More than one public constructor on an injectable → smell; prefer a **single** public constructor.
- Optional dependency defaulting to `null` (not a Null Object) → risk of NRE + Temporal Coupling.

## Composition Root rules
- Exactly **one** per app, near the entry point.
- **Only** place that references concrete types / the container.
- Resolve the graph **once** (the root object). Resolving elsewhere = Service Locator.
- Keep framework activators/factories thin — delegate into the root.

## Lifestyle (lifetime) picker
| Lifestyle | One instance per | Use when | Watch out |
|---|---|---|---|
| **Singleton** | container lifetime | stateless & thread-safe services | must be thread-safe; can capture shorter deps |
| **Scoped** | scope (e.g. web request) | per-request state (DbContext, UoW) | resolving from root/singleton → captive |
| **Transient** | every resolve | cheap, stateless, or stateful-per-use | many disposables to track |

**Captive Dependency rule**: a component's dependency must live **≥ as long** as the component. Never inject a **Scoped/Transient** into a **Singleton**. Simple Injector `Verify()` catches this.

## Pure DI vs DI Container
| Prefer **Pure DI** when | Prefer **DI Container** when |
|---|---|
| small/medium graph | large graph, many similar registrations |
| want compile-time safety + easy debug | want Auto-Registration by convention |
| few developers, simple lifetimes | complex lifetimes/interception at scale |
Rule: start Pure DI; adopt a container when hand-wiring the root costs more than the magic it hides.

## Cross-cutting concern → apply as
Decorator (design-based AOP) first. Reach for **Dynamic Interception / compile-time weaving** only when decorators would need an impractical number of near-identical wrappers.

## Container lifetime API mapping
| Book Lifestyle | Autofac | Simple Injector | MS.DI |
|---|---|---|---|
| Singleton | `SingleInstance()` | `Lifestyle.Singleton` | `AddSingleton` |
| Scoped | `InstancePerLifetimeScope()` | `Lifestyle.Scoped` | `AddScoped` |
| Transient | `InstancePerDependency()` | `Lifestyle.Transient` | `AddTransient` |

**MS.DI limits**: no property injection, no built-in decoration/interception, no verification → for heavy interception/auto-registration pick Autofac or Simple Injector.
