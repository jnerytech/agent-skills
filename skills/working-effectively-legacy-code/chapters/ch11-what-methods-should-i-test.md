# Chapter 11: I Need to Make a Change. What Methods Should I Test?

## Core Idea

Before you change tangled legacy code, you have to know *where* to pin behavior with **characterization tests**. The naive answer — "test each method you change" — is not enough, because in legacy code a change in one place can ripple to behavior somewhere else, and without a test you'll never see it. This chapter gives you a disciplined way to reason about that ripple: trace the **chain of effects** flowing out of every change point until you reach a place where the effect can be *sensed* (observed from outside). Those sensing locations are where you write your tests. It's a learnable skill, not a tool: "Know your language" is the most important instrument, because the language's own rules ('firewalls') tell you where effects *cannot* go, so you don't have to chase them past the boundary.

## Frameworks Introduced

### Effect Sketch / Effect Graph reasoning

An **effect sketch** is a tiny, low-syntax diagram (bubbles and arrows) that shows what a change can affect at runtime.

How to draw one:
1. Make a separate **bubble for each variable** that can be affected and **each method whose return value can change**.
2. Draw an **arrow from a thing to everything whose value can change** because of it. Bubbles can live on the same object or different objects — it doesn't matter.
3. Start at your **change points** and propagate outward: change point → variable it touches → methods that read that variable → their callers, and so on, until you hit something a client can observe.

There is "not much syntax" deliberately — the value is in the discipline of tracing, not in formal notation. A good measure of code quality: in well-structured code, complicated external effects are the *sum of a much simpler set* of internal effects, so most methods have simple effect structures. Anything that makes the sketch simpler makes the code more understandable and maintainable.

### Interception Points

An **interception point** is a place where you can *sense* the effect of a change — somewhere in the effect graph where you can write a test that detects whether the change behaved correctly. In the `InMemoryDirectory` example, "the only way that users of the class can sense effects is through `getElementCount` and `getElement`" — those are the interception points. Once you know all the spots where an effect can be detected, you "pick and choose among them" when writing tests.

How to find them: complete the effect sketch from your change points, then look at the *endpoints* (the outermost observable bubbles — usually methods returning values to clients). Each observable endpoint is a candidate interception point.

### Pinch Point

A **pinch point** is a narrow interception point that covers *many* effects at once — a place where the effect graph fans back in, so one test there exercises a large swath of behavior. (The term is developed further in the next chapter, but the seed is here.) Prefer interception points with the most fan-in: in the `CppClass` sketch, `getInterface` is the best place to test because it "exercises declarations a bit more" — sensing things you can't easily reach through `getDeclaration`/`getDeclarationCount`. Even better is when one method internally *uses* another (e.g., `getInterface` calling `getDeclaration`): testing the outer method automatically exercises the inner one, collapsing the sketch's endpoints into a natural pinch point.

How to use: find the bubble that the most arrows funnel into, confirm it's observable from clients, and write the bulk of your characterization tests there for maximum coverage per test.

## Key Concepts

- **Reasoning forward** — from a change point, ask: "If I make this change, how could it possibly affect the rest of the program?" Follow effects downstream. This is the mode for writing characterization tests *before* changing.
- **Reasoning backward** — from an unexpected result back to its source. This is the *debugging* mode, used when you already have a wrong value to explain.
- **Three ways effects propagate** (the rule for finding effects in OO code):
  1. **Return values** used by a caller.
  2. **Modification of objects passed as parameters** that are used later (sneaky — Java/C# pass object references by value, so any method can mutate state through the handle).
  3. **Modification of static or global data** used later (the sneakiest — invisible in method signatures; e.g., `addText` secretly calling `View.getCurrentDisplay().addText(...)`).
- **Firewalls** — language features that *stop* effect propagation so you needn't look past them: `private` vs package/`protected` scope, Java `String` immutability, `final`, C++ `const` (but beware `mutable`, which lets `const` methods mutate state — "Take `const` to mean `const`... without really checking" is dangerous).
- **"But that would be stupid" rules** — contextual, often-unstated invariants of a codebase (e.g., "the `declarations` list won't change after construction") that let you stop reasoning early. Good code has many; bad code has few or rules "littered with exceptions."

## Mental Models

- **Effects radiate like ripples from a stone.** Every functional change has an associated chain of effects flowing back toward a system boundary — but many parts of the code never change because they don't call the affected method directly or indirectly.
- **Test where the effect surfaces, not where it starts.** You don't have to test at the change point; you test wherever the change becomes *observable*. Choose the observation point that covers the most.
- **Encapsulation is a tool, not a goal.** "Encapsulation isn't an end in itself; it is a tool for understanding." It matters because it reduces the paths you must follow when reasoning about effects. When encapsulation and test coverage conflict, **bias toward test coverage** — tests let you reason about code *directly*, and often help you regain encapsulation later.
- **Narrowing effects makes programming easier** — you need to know less to understand a piece of code (the limit case is functional languages). Restricting effects in OO code makes testing easier with no real downside.

## Anti-patterns

- **Testing only the methods you literally edit.** Misses ripple effects that surface elsewhere.
- **Trusting method signatures to reveal effects.** Information hiding hides exactly the static/global side effects you most need to know about.
- **Trusting a keyword without checking.** Assuming `const`/`final` truly forbids mutation without verifying (`mutable`, reflection, package-scope back doors).
- **Forgetting superclasses and subclasses.** If any field is public, protected, or package-scoped, a sub/superclass can be an unconsidered client modifying it. "Make sure that you have found all of the clients of the class."
- **Skipping collaborator objects.** Glossing over helper classes (the `Element` class) that participate in the effect path.

## Code Examples

Sneaky global-data effect — only line 2 of `addText` differs from the benign version, and the signature gives no hint:

```java
public void addText(String newText) {
    text += newText;
    View.getCurrentDisplay().addText(newText);  // hidden effect on global state
}
```

A firewall difference that changes how far you must look:

```java
private double x = 0;   // effects reach clients ONLY through distance()
double y = 0;           // package scope: clients/subclasses may read it directly
```

## Worked Example

**Effect sketch for `CppClass`** (a Java class manipulating C++ declarations):

```java
public class CppClass {
    private String name;
    private List declarations;
    public CppClass(String name, List declarations) {
        this.name = name; this.declarations = declarations;
    }
    public int getDeclarationCount()      { return declarations.size(); }
    public String getName()               { return name; }
    public Declaration getDeclaration(int i){ return (Declaration)declarations.get(i); }
    public String getInterface(String n, int[] idx) { /* loops over declarations */ }
}
```

**Exercise:** list everything that, after construction, could change a method's result.

1. Someone could **add elements to `declarations`** after passing it to the constructor — the list is held *by reference*, so this alters `getDeclarationCount`, `getDeclaration`, and `getInterface`.
2. Someone could **mutate or replace an object inside `declarations`** — same affected methods.
3. `getName`? Tempting, but Java `String` is **immutable** (a firewall) — `getName` always returns the same value. *Not* an effect.

**The sketch:** bubbles for `declarations` (and a single `declaration`) with arrows fanning out to `getDeclarationCount`, `getDeclaration`, `getInterface`.

```
declarations ───┬──► getDeclarationCount
                ├──► getDeclaration
                └──► getInterface
declaration ────────► getInterface (and getDeclaration)
```

**Picking the interception point / pinch point:** the three methods are observable endpoints. `getInterface` exercises `declarations` the most, so it's the strongest interception point. If `getInterface` is rewritten to call `getDeclaration` internally, the sketch collapses — testing `getInterface` now also exercises `getDeclaration`, giving a tighter pinch point and an easier testing decision.

**Widening the picture:** `CppClass` is created only in `ClassReader.parse()`, and `declarations` is populated only in `matchVirtualDeclaration` — all *before* the object exists. The tokens hold an unchanging string and int; `Declaration` is immutable after creation. Conclusion: once a `CppClass` is built, its list and contents won't change — a "but that would be stupid" rule we could even lock in with `final`. That knowledge shrinks where we must test.

## Key Takeaways

- For every change, trace the **chain of effects** to find where behavior can be sensed; write **characterization tests** at those **interception points**.
- Draw **effect sketches**: a bubble per affected variable/return value, an arrow to everything it can change.
- **Reason forward** to place tests; reason backward to debug.
- Effects propagate exactly three ways: **return values, mutated parameters, mutated static/global data**.
- Prefer **pinch points** — narrow interception points with high fan-in — to cover many effects with few tests.
- **Know your language**: scope, immutability, `final`, `const`/`mutable` are firewalls (or false firewalls) that bound your search.
- Always check **superclasses, subclasses, and collaborator objects** for hidden clients.
- When encapsulation fights coverage, **favor coverage** — encapsulation serves understanding, not the other way around.

## Connects To

- **Ch. 13 (Characterization Tests)** — this chapter answers *where*; Ch. 13 answers *how* to write the tests that pin existing behavior.
- **Ch. 12 (companion)** — extends interception points and the **pinch point** into a full strategy for testing a cluster of changes at once.
- **Ch. 2 / Legacy Code Change Algorithm** — effect reasoning supports step 1–2 (identify change points, find test points) of: identify change points → find test points → break dependencies → write tests → make changes and refactor.
- **Seams & enabling points** — once you know which effects to sense, you choose between **sensing** (observing through a seam, e.g., fake/mock objects) and **separation** to get the code under test.
- **Dependency-breaking refactorings** (e.g., *Parameterize Constructor*) — these may break encapsulation and add effect paths; the bias toward test coverage in this chapter justifies that trade.
