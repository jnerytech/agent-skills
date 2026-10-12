# Chapter 6: Designing for Extensibility

## Core Idea
Extensibility mechanisms range from cheap-but-weak to powerful-but-expensive. **Choose the least costly mechanism that meets the requirement** — you can always add extensibility later, but you can never take it away without a breaking change.

## Frameworks Introduced
- **The extensibility cost ladder** (cheap→expensive / weak→powerful): unsealed classes → protected members → events/callbacks → virtual members → abstractions (abstract types/interfaces).
- **Template Method for scoped extensibility**: public non-virtual method does the arg-checking, then defers to a `protected virtual XxxCore` — limits extensibility to exactly the intended point (§9.9).

## Reference Tables

| Mechanism | Power | Cost | When |
|---|---|---|---|
| Unsealed class (no virtuals/protecteds) | Low | Very low (cheap tests) | Default; lets users add ctors, methods, mocks |
| Protected members | — | Public-equivalent | Advanced customization without cluttering public API |
| Events / callbacks | Comparable to virtual | Heavier (delegate ~2× slower, allocs) | Customization *at runtime*; approachable to non-OO devs |
| Virtual members | High | High (design/test/maintain) | Specialization; compile-time only |
| Abstractions (abstract class/interface) | Highest | Very high design cost | Plug-ins, IoC, pipelines, testability |

## Key Concepts
- **Unsealed by default**: classes are unsealed in most languages, and that's the recommended default — but being unsealed is *part of the contract* and should be a deliberate choice (it also blocks devirtualization/inlining optimizations).
- **Protected == public for security** (Abrams): anyone can subclass and reach protected members, so review/validate/document them exactly like public members.
- **Events vs. callbacks**: events are callbacks with convenient syntax + Visual Studio integration; more familiar to a broad audience. Callbacks execute *arbitrary user code in your context* — analyze for security/correctness/compatibility.
- **`Func<>`/`Action<>`/`Expression<>` over custom delegates**: `Func`/`Action` to *run* code; `Expression` to *reason about* code (analyze/serialize/optimize/remote — e.g., LINQ-to-SQL). (Custom delegates only when you need named args, `ref`, or non-generic-able types like pointers/`ref struct`.)
- **Abstraction**: a type describing a contract without full implementation (`Stream`, `IEnumerable<T>`, `Object`). The hard part is the *right* member set — too many → unimplementable, too few → useless. `ICloneable` is the cautionary tale: undocumented shallow-vs-deep-copy contract made it useless.
- **Base class**: designed for subclasses to reuse a default implementation (`Collection<T>`, `KeyedCollection<TKey,TItem>`); sits mid-hierarchy. Not a good abstraction itself (too much implementation).

## Mental Models
- **Prefer protected over public for virtual members**: public method provides the consumer contract; a protected virtual provides the extension point. Convenience overloads are non-virtual and funnel into the one virtual implementation.
- **Don't invoke callbacks under a lock**: risks deadlock and reentrancy. Copy the handler out first (`var h = handler; h?.Invoke(...)` or `handler?.Invoke(...)`) — invoke outside the lock. If a predicate must run under the lock, document the restrictions (no cross-thread, no reentrancy).
- **Overrides should preserve the base contract, not necessarily call base** (Cwalina): calling base is often the easiest way, but rarely the *only* way.
- **Sealing is limiting extensibility on purpose** — but it feels abrasive to users who inherit for non-obvious reasons (convenience members, mocks). Seal only with a good reason.

## Code Examples
Scope extensibility with Template Method:
```csharp
public class Control {
    public void SetBounds(...) { /* validate */ SetBoundsCore(...); }
    protected virtual void SetBoundsCore(...) { /* real work */ }
}
```
Constrain a hierarchy to a fixed set (internal ctor on root, protected on the sanctioned subclasses):
```csharp
public class LivingOrganism { internal LivingOrganism() {} }
public class Animal : LivingOrganism { protected Animal() {} }
public class Plant  : LivingOrganism { protected Plant()  {} }
// third parties can extend Animal/Plant, but not LivingOrganism
```
- **What it demonstrates**: `internal` constructor seals the *root* without sealing the whole tree.

## Anti-patterns
- **Sprinkling virtual members "for extensibility"** (Mariani): you often still can't get the extensibility you needed, and everything is now permanently slower and compatibility-locked. Understand the requirement first.
- **Making members virtual without cause**: virtuals aren't inlined, are compatibility-brittle, and promise "subtle observable behaviors forever" (Jan Gray).
- **Callbacks in performance-sensitive APIs** (delegate ~2× a virtual call + memory).
- **Shipping an abstraction untested** — validate with 2–3 implementations and 2–3 consumers before shipping (Toub); ship reference/conformance tests.
- **`Base` suffix on a public base class** (`Collection<T>` isn't `CollectionBase`) — the base-ness is irrelevant to API consumers.
- **protected/virtual members on a sealed type** — uncallable/unoverridable.

## Key Takeaways
1. Pick the cheapest mechanism that works; you can widen extensibility later but never narrow it without breaking callers.
2. Unsealed-with-no-virtuals is a cheap, appreciated default; unseal deliberately, not by accident.
3. Treat protected members as public for security/docs/compat.
4. Prefer events over raw callbacks over virtuals for broad-audience customization; never invoke user callbacks under a lock.
5. Use `Func`/`Action`/`Expression`; reserve `Expression` for code you must analyze/serialize/optimize.
6. Abstractions are the most powerful and most expensive — get the member set right, document the contract, validate with multiple impls/consumers.
7. Consider making base classes `abstract` (signals "inherit me"); place them in a separate advanced namespace.
8. Don't seal without a reason (static class, many inherited virtuals, or perf-critical attributes are good ones); consider sealing your overrides.

## Connects To
- **Ch 2**: limiting abstractions in mainline APIs; layered namespaces for advanced base classes.
- **Ch 4**: class vs. interface for abstractions (§4.3); static classes; sealing.
- **Ch 5**: virtual/overload design; event design (§5.4); the `On`+protected-virtual raise pattern.
- **Ch 9**: Template Method (§9.9) — the primary tool for scoped virtual extensibility.
