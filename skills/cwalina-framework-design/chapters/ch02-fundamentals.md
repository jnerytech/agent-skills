# Chapter 2: Framework Design Fundamentals

## Core Idea
A general-purpose framework must serve a *diverse* audience (skills, languages, scenarios) with both power and simplicity. The way to reconcile them is a set of foundational principles anchored on scenario-driven design and the Pit of Success.

## Frameworks Introduced
- **The Pit of Success** (Rico Mariani): design so customers "fall into" winning practices by default; make it *hard* to do the wrong thing.
  - When to use: every default, overload, and API shape decision.
  - How: the most natural way to use the system must be correct, secure, and performant.
- **The Principle of Scenario-Driven Design**: write the *client code* for the top 5–10 scenarios FIRST, then design the object model to support those samples.
  - When to use: at the start of any public API feature.
  - How: produce a scenario-driven API spec (see App. C); scenarios ≈ end-user use cases ("read from a file", not "open/read line/close"); write samples in ≥2 dissimilar languages (e.g., C# + F#), consider a dynamic language (PowerShell/IronPython).
  - Why it works: standard OO design methodologies optimize for *implementation maintainability*, not *API usability* — scenario-first inverts that.
- **The Principle of Low Barrier to Entry**: nonexperts must be able to experiment without reading docs or wiring up many objects.
  - How: main-scenario namespaces hold only common types (advanced → subnamespaces); provide simple overloads; require instantiating ≤1 type; minimal initialization; good defaults; communicate mistakes via clear exceptions.
- **The Principle of Self-Documenting Object Models**: simple scenarios must be usable *without* documentation.
  - How: reserve the best/most intuitive names for the types users instantiate most; use descriptive (even verbose) names; strong typing over property bags; consistency with existing .NET APIs; limit abstractions.
- **The Principle of Layered Architecture**: split the API into low-level types (power/expressiveness) and high-level types (productivity) that wrap them.
  - How: factor layers into separate related namespaces (preferred for most frameworks) or the same namespace (simple features only). Layers must be well integrated and independently understandable (don't force catching another layer's exceptions).

## Key Concepts
- **Progressive framework**: a *single* framework with a gradual learning curve that lets knowledge transfer from simple → advanced scenarios (vs. the old multi-framework approach: VB/Win32/MFC/ATL, where skills didn't transfer).
- **80/20 (Pareto)**: 20% of scenarios/APIs matter most — invest design there.
- **Convenience overload**: an overload with a short parameter list / good defaults, lowering the entry barrier.
- **Strong typing**: `Customer.Name` (typed) beats `Customer.Properties["Name"]`; single biggest factor in intuitiveness.
- **Limiting abstractions**: too many interfaces/abstract classes force users to become architecture experts before writing simple code.

## Mental Models
- **Think of the object model as a map** (Chris Anderson): properties are signs; an abstract base with no obvious derivations is a dead-end sign.
- **"Build for the engineer at the next bench" is WRONG for APIs** (Brad Abrams): design for the *customer's* scenarios, not for people like you.
- **Scenario-driven ≈ TDD for APIs** — write the code you wish you could write, then work backward to the object model.
- **Addition through subtraction** — fewer concepts = more productive users.

## Code Examples
Scenario samples drive the object model. Writing these two samples first:
```csharp
// scenario #1: measure elapsed time
Stopwatch watch = Stopwatch.StartNew();
DoSomething();
Console.WriteLine(watch.Elapsed);

// scenario #2: reuse stopwatch
watch.Reset();
watch.Start();
DoSomething();
Console.WriteLine(watch.Elapsed);
```
...leads directly to this object model:
```csharp
public class Stopwatch {
    public static Stopwatch StartNew();
    public void Start();
    public void Reset();
    public TimeSpan Elapsed { get; }
    public long ElapsedMilliseconds { get; }
}
```
- **What it demonstrates**: the API is *derived from* desired usage, not the reverse.

Low-barrier example — usable immediately with good defaults:
```csharp
var ordersQueue = new MessageQueue(path);
ordersQueue.Send(order); // uses default priority, encryption, etc.
```

## Reference Tables

| Principle | One-line rule |
|---|---|
| Scenario-Driven Design | Write top 5–10 client code samples first, then design the object model. |
| Low Barrier to Entry | Experiment-ready: ≤1 explicit `new`, minimal init, good defaults, clear exceptions. |
| Self-Documenting | Usable in simple scenarios with zero docs; reserve best names; strong types. |
| Layered Architecture | Low-level (power) + high-level (productivity) wrapper; separate namespaces usually. |
| Pit of Success | Natural usage = correct + secure + fast; hard to misuse. |

## Worked Example
The System.IO cautionary tale (Cwalina/Abrams): .NET 1.0 shipped `System.IO` *without* usability testing. Post-ship, 8 of 8 average developers **failed to read text from a file in 30 minutes**. Lesson institutionalized: run usability studies (even informal "hey, look at this" ones — hand a stubbed API to someone unfamiliar, give them 30 min, watch) *early*, because fixing an unusable API without breaking changes is enormously expensive. Stephen Toub's refinement: you don't even need a real implementation — a compile-only stubbed API surface reveals whether devs find the right types and patterns via IntelliSense.

## Key Takeaways
1. Design starts from scenarios and client code, never from the object model — "there is simply no other way to design a great framework" (Cwalina).
2. Optimize for IntelliSense: an intuitive API + IntelliSense covers ~80% of what a new dev needs.
3. Lower the barrier: minimal initialization, ≤1 explicit constructor, good defaults, convenience overloads.
4. Prefer strong typing; use property bags only as the exception, and still add typed helpers for common members.
5. Reserve the best, most-intuitive names for the most commonly used types — don't "burn" `File` on an abstract base.
6. Avoid many abstractions in mainline-scenario APIs; too many = overengineering (and can hurt perf).
7. Use a layered design to get power *and* simplicity in one framework.

## Connects To
- **Ch 1**: operationalizes the 7 qualities (esp. simplicity + consistency).
- **Ch 3**: naming guidelines — the self-documenting principle in detail.
- **Ch 6**: designing for extensibility — where abstractions *do* belong.
- **Ch 7**: exception design — the "communicate mistakes via exceptions" thread.
- **App. C**: the sample scenario-driven API specification.
