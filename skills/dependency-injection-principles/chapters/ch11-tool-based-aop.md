# Chapter 11: Tool-based Aspect-Oriented Programming

## Core Idea

Chapter 10 applied Aspect-Oriented Programming (AOP) in its purest form — solely through SOLID design practices (Decorators, interfaces, Constructor Injection). This chapter examines the *tool-based* alternatives: **Dynamic Interception** and **Compile-time weaving**. Both automate the mechanical, repetitive work of writing Decorators for Cross-Cutting Concerns, but they do so at a cost.

The authors' stance is deliberately cautious and asymmetric:

- **Design-based AOP** (chapter 10) is the ideal and default.
- **Dynamic Interception** is the acceptable *next-best* fallback — a reasonable temporary solution "until the right time arrives" to refactor toward SOLID.
- **Compile-time weaving** is flatly labeled a **DI anti-pattern** — "the opposite of DI." It is covered only because it is well-known enough that developers must be warned against it.

The recurring motivation for tools is DRY. A hand-written Circuit Breaker Decorator repeats identical `Guard()/try/Succeed()/catch/Trip()` plumbing across every method (`Insert`, `Update`, `Delete`), differing only in which decoratee method is called. That repetition looks like a template, and templates invite automation.

## Frameworks Introduced

### Dynamic Interception (Castle DynamicProxy)

- **When to use:** When the chapter-10 design approach is "too radical" for your situation, or as a temporary measure to apply Cross-Cutting Concerns without large refactorings while still programming to interfaces and using Pure DI.
- **How:** The .NET runtime can *dynamically emit types* — generate a fully functional class at runtime from an abstract model, with no source file. A dynamic Interception library uses this to auto-generate a Decorator ("Proxy," in Castle's terms) once per Abstraction. You write the aspect as an **Interceptor** implementing `Castle.DynamicProxy.IInterceptor` (a single `Intercept(IInvocation)` method). The `IInvocation` parameter represents the intercepted method call; calling `invocation.Proceed()` lets the call flow to the next implementation on the stack. The Interceptor still uses Constructor Injection and is composed in the **Composition Root** — so Pure DI still works even though Castle controls Decorator construction.

Castle Dynamic Proxy is the de facto standard for dynamic Interception in .NET — free, open source, and used under the hood by most DI Containers.

### Compile-time weaving (PostSharp / Fody / IL weaving)

- **When to use (per authors):** Essentially never for **Volatile Dependencies**. It may hold marginal value only for Stable Dependencies, which are uninteresting from a DI standpoint. "Favor applying the SOLID principles, or fall back to dynamic Interception if that isn't possible."
- **How:** A *post-compiler* alters the compilation process. After the C# compiler produces an IL assembly, the weaving tool reads that assembly, modifies the IL to inject aspect code, and writes a modified assembly back to disk — replacing the original. Aspects are declared "attribute-based": you place a custom **aspect attribute** (e.g. `[Transaction]`, `[CircuitBreaker]`) on a class, member, or assembly. With PostSharp you inherit from `OnMethodBoundaryAspect` and override `OnEntry`, `OnSuccess`, and `OnExit`, passing state between them via `MethodExecutionTag`.

## Key Concepts

1. **Interceptor** — a hand-written aspect class implementing the tool's interceptor interface; holds the Cross-Cutting logic (e.g. Circuit Breaker plumbing).
2. **`IInvocation` / `Proceed()`** — the reified method call. `Proceed()` continues to the decorated instance; the invocation also exposes arguments, return value, and method metadata via reflection.
3. **Runtime-generated Decorator (Proxy)** — the class Castle emits once per Abstraction; wraps both the real target and the Interceptor, and is injectable wherever the Abstraction is expected.
4. **Aspect attribute** — a custom attribute that signifies/implements an aspect, applied declaratively to code you want woven.
5. **Method boundaries only** — both tool approaches (and design-based AOP) can only extend behavior at the boundaries of virtual/abstract/interface methods; private methods can't be intercepted (the authors call the *need* to intercept private methods a code smell).
6. **Loss of compile-time support** — Interceptors rely on runtime reflection (casting, boxing of value-type arguments), making them harder to read and maintain than a plain Decorator.
7. **Tooling coupling** — Interceptors are strongly coupled to the library (`Castle.DynamicProxy.*` types), adding an external dependency that must be learned; confining it to the Composition Root prevents that coupling from spreading to other assemblies.
8. **DI-unfriendliness of weaving** — .NET attributes accept only primitive constructor arguments, and attribute instances are created by the runtime at a different time/place than your object graph, so Constructor Injection into a woven aspect is impossible.
9. **Ambient Context / Service Locator workarounds** — the only ways to feed a Volatile Dependency into a woven aspect; both are hacks (see anti-patterns).
10. **Compile-time coupling** — once woven, aspects are baked into the assembly and cannot be turned off, so you can never call the code *without* the aspect applied.

## Mental Models

- **Template automation ladder.** A repeated Decorator body is a template. You can implement that template by hand (chapter 10), have a tool emit it at runtime (Dynamic Interception), or have a tool bake it into IL (Compile-time weaving). As you climb the ladder toward more automation, you trade away clarity, testability, and DI-friendliness.
- **Runtime composition vs compile-time baking.** DI's whole aim is to compose Volatile Dependencies at *runtime* in the Composition Root, behind Seams. Dynamic Interception preserves this (Castle builds the Proxy at runtime, you still inject via the Composition Root). Compile-time weaving violates it (the aspect and its dependency are fused into the code at *compile* time) — which is precisely why it's "the opposite of DI."
- **"Doesn't fix the disease, only a symptom."** Tool-based AOP addresses only Cross-Cutting Concerns. It accepts the status quo of a poor design (e.g. a bloated `IProductService`). You end up with a system marginally more maintainable than before, but considerably *less* maintainable than one refactored with SOLID.

## Anti-patterns

Over-reliance on tool-based AOP fails for concrete reasons:

- **Dynamic Interception as a permanent solution.** It's meant as a temporary bridge. Leaning on it indefinitely means you accept the status quo and never do the SOLID refactoring — if you did design your Abstractions properly, you'd be doing AOP by design instead. Downsides: lost compile-time support, tooling coupling, not universally applicable, and it doesn't fix underlying design problems.
- **Compile-time weaving on Volatile Dependencies — a DI anti-pattern.** Two core failures:
  - *DI-unfriendly.* Constructor Injection is impossible. The workarounds are both bad: **Ambient Context** (a `public static` property on the aspect) causes **Temporal Coupling** — forget to set it and you get a `NullReferenceException` — plus **Captive Dependencies** (a static holding a shorter-lived dependency) and **Interdependent Tests** (static state leaks between test cases, forcing Fixture Teardown after every test). **Service Locator** is worse still: same Temporal Coupling and Interdependent Tests, *plus* it hides the true set of dependencies and drags along a redundant dependency.
  - *Compile-time coupling.* Woven aspects can't be removed, so you can't run code without them. A `[CheckAuthorization]` aspect forces even integration tests through a login flow; a caching aspect can make a "database" test silently hit the cache and never touch the DB. This wrecks Testability and slows suites.
- **Boilerplate for its own sake.** The PostSharp `TransactionAttribute` requires overriding three methods, decorating with several attributes, and shuttling state via `MethodExecutionTag` — far more code and less naturally than the equivalent SOLID Decorator, especially around `catch`/`finally`/`using` blocks.

## Code Examples

```csharp
// Dynamic Interception: a Circuit Breaker written as a Castle Interceptor.
public class CircuitBreakerInterceptor
    : Castle.DynamicProxy.IInterceptor
{
    private readonly ICircuitBreaker breaker;

    // Constructor Injection still works — composed in the Composition Root.
    public CircuitBreakerInterceptor(ICircuitBreaker breaker)
    {
        this.breaker = breaker;
    }

    // One general method replaces the per-method Decorator plumbing.
    public void Intercept(IInvocation invocation)
    {
        this.breaker.Guard();
        try
        {
            invocation.Proceed();      // let the call reach the real decoratee
            this.breaker.Succeed();
        }
        catch (Exception ex)
        {
            this.breaker.Trip(ex);
            throw;
        }
    }
}
```

```csharp
// Wiring it up in the Composition Root with Pure DI.
var generator = new Castle.DynamicProxy.ProxyGenerator(); // cache for app lifetime
var breaker = new CircuitBreaker(TimeSpan.FromMinutes(1));
var interceptor = new CircuitBreakerInterceptor(breaker);
var wcfRepository = new WcfProductRepository();

IProductRepository repository = generator
    .CreateInterfaceProxyWithTarget<IProductRepository>(
        wcfRepository,   // the real target
        interceptor);    // the aspect wrapped around it
```

**What it demonstrates:** A single `Intercept` method captures Cross-Cutting logic that would otherwise be duplicated in every Decorator method (via the generalized `IInvocation`/`Proceed()` model). Because the Interceptor uses Constructor Injection and Castle's Proxy is created at runtime inside the Composition Root, Pure DI is fully preserved — the key reason Dynamic Interception is an acceptable fallback while Compile-time weaving is not.

## Reference Tables

| Dimension | Design-based AOP (ch. 10) | Dynamic Interception | Compile-time weaving |
|---|---|---|---|
| Verdict | **Preferred / ideal** | Acceptable temporary fallback | **DI anti-pattern** (for Volatile Deps) |
| Aspect authored as | Plain Decorator (SOLID) | Interceptor (`IInterceptor`) | Aspect attribute (`OnMethodBoundaryAspect`) |
| Example tool | None (hand-written) | Castle DynamicProxy | PostSharp / Fody / IL weaving |
| When applied | Runtime, in Composition Root | Runtime (proxy emitted) | Compile time (IL rewrite) |
| Constructor Injection | Yes | Yes | **No** (attributes take primitives only) |
| Volatile Dep workaround | none needed | none needed | Ambient Context / Service Locator (hacks) |
| Compile-time safety | Full | Reduced (reflection) | Full-but-fused |
| Tooling coupling | None | Coupled to Castle types | Coupled + baked into assembly |
| Can run code without aspect | Yes | Yes | **No** |
| Testability | High | Medium | Low (aspects always present) |
| DRY on repetitive plumbing | Manual | Automated | Automated (but boilerplate-heavy) |
| Fixes underlying design | Yes | No | No |

| Dynamic Interception disadvantage | Why it hurts |
|---|---|
| Loss of compile-time support | Reflection over `IInvocation.Arguments` needs casting/boxing → harder to read/maintain |
| Coupled to tooling | Aspects depend on Castle library; confine to Composition Root |
| Not universally applicable | Only virtual/abstract/interface method boundaries; no private methods |
| Doesn't fix design problems | Only addresses Cross-Cutting Concerns; leaves poor design intact |

## Worked Example

A team has a `WcfProductRepository` whose network calls must be guarded by a Circuit Breaker. The hand-written `CircuitBreakerProductRepositoryDecorator` duplicated the same `Guard/try/Succeed/catch/Trip` block across `Insert` and `Delete`, differing only by which decoratee method ran.

They refactor to Dynamic Interception (listings above): the duplicated blocks collapse into one `Intercept` method operating over `IInvocation`, with `invocation.Proceed()` standing in for the specific `decoratee.Xxx(...)` call. In the Composition Root, `ProxyGenerator.CreateInterfaceProxyWithTarget<IProductRepository>(wcfRepository, interceptor)` produces a runtime Decorator wrapping both the real repository and the breaker Interceptor. The generator is created once and cached.

Result: DRY is restored, Constructor Injection of `ICircuitBreaker` still works, and Pure DI is intact — but the code now leans on runtime reflection and a Castle dependency, and it hasn't improved the repository's underlying design. If the same aspect had been applied via a PostSharp `[CircuitBreaker]` attribute, there would be *no* way to inject `ICircuitBreaker` at all (`[CircuitBreakerAttribute(???)]`), forcing an Ambient Context static property with all its Temporal-Coupling and test-isolation pain.

## Key Takeaways

1. **Prefer design-based AOP (SOLID) above all.** The authors' explicit ordering: favor SOLID Decorators; fall back to Dynamic Interception only if that isn't possible; avoid Compile-time weaving for Volatile Dependencies entirely.
2. **Dynamic Interception is the acceptable fallback** — it automates repetitive Decorators via runtime-emitted Proxies while preserving Constructor Injection and Pure DI, making it a fine *temporary* bridge until you can refactor toward SOLID.
3. **Its four costs are real:** loss of compile-time support (reflection), coupling to the tooling, applicability only at virtual/interface method boundaries, and it does nothing to fix underlying design problems.
4. **Compile-time weaving is a DI anti-pattern** for Volatile Dependencies: it fuses aspects into the IL at compile time — the exact opposite of composing dependencies at runtime in the Composition Root.
5. **Weaving is DI-unfriendly** because attributes take only primitive constructor args and are instantiated by the runtime; the only workarounds (Ambient Context, Service Locator) introduce Temporal Coupling, Captive Dependencies, and Interdependent Tests.
6. **Weaving causes compile-time coupling** — you can never run code without the aspect, which breaks unit and integration test isolation (auth flows, silent cache hits).
7. **Tools don't cure bad design.** No amount of interception or weaving substitutes for well-factored, one-membered Abstractions applied at the right granular level.

## Connects To

- **Chapter 10 (Aspect-Oriented Programming by Design):** the preferred baseline — Decorators, the Circuit Breaker/Transaction aspects, and the SOLID refactoring of `IProductService` that this chapter deliberately does *not* fix.
- **Chapter 4 (DI patterns):** Constructor Injection and Composition Root, the patterns Dynamic Interception preserves and Compile-time weaving breaks.
- **Chapter 5 (DI anti-patterns):** Ambient Context and Service Locator, invoked here as weaving workarounds and their Temporal Coupling.
- **Chapter 8 (Object Lifetime):** Captive Dependencies arising from static aspect properties.
- **Chapter 1:** Volatile vs Stable Dependencies — the distinction that determines whether weaving is merely unhelpful (Stable) or an anti-pattern (Volatile).
- **Part 4 (DI Containers):** many containers use Castle Dynamic Proxy internally for interception; chapter 12 weighs container vs Pure DI.
