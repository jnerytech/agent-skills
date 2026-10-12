# Glossary — Dependency Injection Principles, Practices, and Patterns

**Abstract Factory** — a factory abstraction that creates instances of another abstraction; legitimate for runtime values but often abused (Ch 6).

**Ambient Context** — anti-pattern: a dependency exposed via a static accessor (e.g. `DateTime.Now`, a static `Logger`), hiding it from the constructor (Ch 5).

**Auto-Registration** — registering many types by convention/reflection instead of one line each ("convention over configuration") (Ch 12, Ch 13–15).

**Aspect** — an encapsulated cross-cutting concern (logging, security, caching) applied across many components (Ch 9–11).

**Aspect-Oriented Programming (AOP)** — modularizing cross-cutting concerns into aspects; "by design" via decorators vs "tool-based" via proxies/weaving (Ch 10–11).

**Bastard Injection** — Foreign Default supplied through an overloaded constructor; a Control Freak variant (Ch 5).

**Captive Dependency** — a long-lived component holding a shorter-lived dependency, keeping it alive past its intended scope; a bad Lifestyle choice (Ch 8).

**Compile-time weaving** — tool-based AOP that injects aspect code into IL at build time (e.g. PostSharp, Fody) (Ch 11).

**Composition Root** — the single, unique place near the application's entry point where the object graph is composed; the only place a container is used (Ch 4, Ch 7, Ch 12).

**Conforming Container** — an abstraction over multiple DI Containers; an anti-pattern that reduces every container to its lowest common denominator (Ch 12, Ch 15).

**Constrained Construction** — anti-pattern: requiring every implementation to have a specific constructor signature (e.g. for `Activator.CreateInstance`) (Ch 5).

**Constructor Injection** — the default DI pattern: static dependencies are passed as constructor parameters and stored in `readonly` fields (Ch 4).

**Constructor Over-injection** — code smell: a constructor with too many (~>4) dependencies, signaling an SRP violation; fix with Facade Services (Ch 6).

**Control Freak** — the most common anti-pattern: creating a Volatile Dependency with `new` instead of injecting it (Ch 5).

**Cross-Cutting Concern** — behavior needed across many components (logging, auditing, security, caching, error handling) (Ch 9).

**Decorator** — GoF pattern used for Interception: wraps a component with the same abstraction to add behavior without changing it (Ch 9).

**Dependency Injection (DI)** — supplying a class's Volatile Dependencies from outside rather than creating them internally.

**Dependency Inversion Principle (DIP)** — high-level modules and low-level modules both depend on abstractions; abstractions are owned by the higher-level/consuming module (Ch 3, Ch 10).

**DI Container (IoC Container)** — a library that automates composing object graphs via Register-Resolve-Release (Ch 12–15).

**Dynamic Interception** — tool-based AOP using runtime dynamic proxies (e.g. Castle DynamicProxy) (Ch 11).

**Facade Services** — refactoring that groups related dependencies behind a new higher-level abstraction to cure Constructor Over-injection (Ch 6).

**Foreign Default** — a default implementation that lives in a different module than its abstraction; injecting it as a hard default couples the modules (Ch 4–5).

**Interception** — inserting behavior between a caller and a callee without either knowing; realized with Decorators (Ch 9).

**Inversion of Control (IoC)** — a program's flow/creation is controlled by an external framework/container rather than the code itself; DI is a form of IoC.

**IServiceCollection / IServiceProvider** — Microsoft.Extensions.DependencyInjection's registration and resolution abstractions (Ch 15).

**Leaky Abstraction** — an abstraction that forces consumers to know implementation details (e.g. that an implementation is `IDisposable`) (Ch 8).

**Lifestyle** — the authors' term for a dependency's lifetime policy: Singleton, Scoped, or Transient (Ch 8).

**Local Default** — a default implementation living in the same module as its abstraction; safe to reference (Ch 4).

**Method Injection** — passing a dependency as a method parameter; used for per-operation runtime values (Ch 4).

**Object Composition** — building the object graph by wiring components together, ideally only in the Composition Root (Ch 7).

**Open/Closed Principle (OCP)** — modules open for extension, closed for modification; decorators achieve it (Ch 10).

**Poor Man's DI / Pure DI** — composing object graphs by hand with `new`, without a DI Container (the book renames "Poor Man's DI" to "Pure DI") (Ch 1, Ch 12).

**Property Injection (Setter Injection)** — supplying an optional dependency through a settable property with a safe Local Default (Ch 4).

**Register-Resolve-Release (RRR)** — the three-phase container API: register mappings, resolve the root, release/dispose the graph (Ch 12).

**Scoped Lifestyle** — one instance per well-defined scope (e.g. per web request) (Ch 8, Ch 15).

**Seam** — a place where behavior can be changed without editing in place; a DI seam is an injected abstraction (Ch 3).

**Service Locator** — anti-pattern: a component asks a container/registry for its dependencies at runtime, hiding them and coupling to the locator (Ch 5).

**Singleton Lifestyle** — one shared instance for the lifetime of the container; must be thread-safe (Ch 8).

**Single Responsibility Principle (SRP)** — a class should have one reason to change; Over-injection signals an SRP breach (Ch 6, Ch 10).

**SOLID** — SRP, OCP, LSP, ISP, DIP; the design principles that drive AOP and good DI (Ch 10).

**Stable Dependency** — a dependency safe to depend on directly (deterministic, always present, no side effects — e.g. `string`, `List<T>`) (Ch 1).

**Temporal Coupling** — a hidden ordering requirement (e.g. must set a property before use); a hazard of Property/Method Injection done wrong (Ch 4–5).

**Transient Lifestyle** — a new instance every time the dependency is requested (Ch 8).

**Verify() (Simple Injector)** — a container self-check that walks all registrations at startup to catch misconfigurations (e.g. Captive Dependencies) (Ch 14).

**Volatile Dependency** — a dependency worth injecting: introduces external resources, nondeterminism, must be replaced/swapped, or doesn't exist yet (Ch 1).
