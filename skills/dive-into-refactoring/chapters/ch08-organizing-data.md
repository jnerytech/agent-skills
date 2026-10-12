# Chapter 8: Organizing Data (Refactoring Techniques)

## Core Idea
Replace primitives with rich classes, untangle class associations, and encapsulate access — making classes more portable, reusable, and self-validating.

## Refactorings
- **Self Encapsulate Field**: Access a *private* field via getters/setters inside its own class — enables lazy init, validation, and overriding accessors in subclasses. (Distinct from Encapsulate Field, which hides *public* fields.)
- **Replace Data Value with Object**: A primitive field that grew associated data/behavior → move it into its own class. A special case of Extract Class (cause differs). Often followed by `Change Value to Reference`.
- **Change Value to Reference**: Many identical instances that should be one shared object → convert to a single reference (via `Replace Constructor with Factory Method` + a registry/storage). Use for real-world entities (user/order/product). *Anti:* Change Reference to Value.
- **Change Reference to Value**: A tiny, rarely-changed reference object costly to manage → make it an **immutable value** (no setters, add an equality method, public constructor). Use for dates/money/ranges/colors. *Anti:* Change Value to Reference.
- **Replace Array with Object**: An array holding heterogeneous data (`row[0]`=name, `row[1]`=wins) → a class with named fields/accessors. *Cures:* Primitive Obsession.
- **Duplicate Observed Data**: Domain data trapped in GUI classes → split domain from GUI, sync via the **Observer** pattern (SRP + Open/Closed). Not for web apps where objects are recreated per request.
- **Change Unidirectional Association to Bidirectional**: Both classes now need each other → add the reverse field; pick a **dominant** class owning association-updates. *Anti:* the reverse.
- **Change Bidirectional Association to Unidirectional**: One side no longer uses the other → drop the unused association. Simpler, less coupling, avoids GC/memory-bloat issues. *Cures:* Inappropriate Intimacy.
- **Replace Magic Number with Symbolic Constant**: A number with hidden meaning → a named `static final` constant (live documentation). Not every number is magic (`i < count`). If it's type code, use the type-code refactorings instead.
- **Encapsulate Field**: A public field → private + accessors. Encapsulation is a pillar of OO. *When not to use:* rare perf-critical hot fields (e.g. `Point` x/y in Java).
- **Encapsulate Collection**: A collection field with plain getter/setter → getter returns a **read-only** copy; provide `add`/`remove` methods so the owner controls mutation. Consider renaming the setter to `replace`.
- **Replace Type Code with Class**: Type code **not** used in conditionals / not affecting behavior → a dedicated type class enabling type-checking. *Cures:* Primitive Obsession.
- **Replace Type Code with Subclasses**: Type code that **drives behavior via conditionals** and is **immutable after creation** → a subclass per value; move behavior down; finish with `Replace Conditional with Polymorphism`. Not if a hierarchy already exists or the code changes at runtime.
- **Replace Type Code with State/Strategy**: Type code driving behavior but subclassing is blocked (existing hierarchy) or the code **changes at runtime** → a state object plugged in and swapped. **Strategy** = choosing an algorithm; **State** = the value governs the whole object condition.
- **Replace Subclass with Fields**: Subclasses differing only by constant-returning methods → collapse into parent fields set in a protected constructor via a factory. *Anti:* Replace Type Code with Subclasses.

## Mental Models
- **Reference vs Value**: one program object per real-world thing (reference: user/order) vs many objects for one thing (value: date/money). Immutability points toward value.
- **Type-code decision**: no behavior → Class; behavior + immutable + no hierarchy → Subclasses; behavior + runtime-changing or hierarchy-blocked → State/Strategy.
- **Encapsulate everything mutable** — collections return read-only, mutate via methods.

## Anti-patterns
- Exposing a **live collection** through a getter — callers mutate it behind the owner's back.
- **Magic numbers** duplicated across the codebase; find-and-replace is unsafe (same number, different meanings).

## Worked Example (Replace Magic Number)
```java
double potentialEnergy(double mass, double height) {
    return mass * height * 9.81;
}
```
→
```java
static final double GRAVITATIONAL_CONSTANT = 9.81;
double potentialEnergy(double mass, double height) {
    return mass * height * GRAVITATIONAL_CONSTANT;
}
```

## Key Takeaways
1. Encapsulate fields and collections; return read-only, mutate through methods.
2. Choose the right type-code cure by behavior + mutability + existing hierarchy.
3. Reference vs value hinges on identity and immutability.
4. Prune bidirectional associations to the direction actually used.

## Connects To
- **Ch 1 / Ch 2**: cures Primitive Obsession and the type-code/switch smells.
- **Ch 9**: type-code subclassing finishes with `Replace Conditional with Polymorphism`.
- **Ch 10 / Ch 11**: `Replace Constructor with Factory Method`, `Push Down Field/Method` support these.
