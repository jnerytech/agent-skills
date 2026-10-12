# Chapter 11: Dealing with Generalization (Refactoring Techniques)

## Core Idea
Abstraction refactorings move functionality up and down the inheritance hierarchy, create classes/interfaces, and swap inheritance for delegation (and back) to get the right structure.

## Refactorings — the pull/push axis
- **Pull Up Field**: Same field in sibling subclasses → move to superclass (private → protected). Kills duplication.
- **Pull Up Method**: Sibling subclasses have similar methods → make them identical, move to superclass. For fields/methods only in subclasses, declare them abstract in the superclass. *Anti:* Push Down Method.
- **Pull Up Constructor Body**: Subclass constructors share code → create a superclass constructor, call `super(...)` from subclasses. Differs from Pull Up Method: constructors aren't inherited, and common code must be at the *start* (super runs first).
- **Push Down Method**: Superclass behavior used by only one/few subclasses → move it down. *Cures:* Refused Bequest. *Anti:* Pull Up Method.
- **Push Down Field**: Field used by only a few subclasses → move it down. *Cures:* Refused Bequest.

## Refactorings — extract & collapse
- **Extract Subclass**: A class has features used only in certain cases → move them to a new subclass. *Cures:* Large Class. *Drawback:* single-inheritance dead end when you need two axes (size × fur) — prefer **Compose over Inherit** (Strategy).
- **Extract Superclass**: Two classes share fields/methods → create a shared superclass, pull the commonality up. Can't apply if a superclass already exists. *Cures:* Duplicate Code.
- **Extract Interface**: Multiple clients use the same slice of an interface, or two classes share part of one → extract that slice into an interface. Isolates common *interfaces*, not common *code* (use Extract Superclass / Extract Class for shared code).
- **Collapse Hierarchy**: Subclass ≈ superclass → merge them. A variation of Inline Class (moving to super or sub). *Cures:* Lazy Class, Speculative Generality. Watch Liskov violations if other subclasses remain.

## Refactorings — inheritance ⇄ delegation
- **Form Template Method**: Subclasses run algorithms with the **same steps in the same order** → move the skeleton + identical steps to the superclass, leave differing steps abstract. Open/Closed; implements **Template Method**. *Cures:* Duplicate Code.
- **Replace Inheritance with Delegation**: A subclass uses only part of its superclass (or violates Liskov) → hold the former superclass in a **field**, delegate needed methods, drop inheritance. Yields the **Strategy** pattern. *Drawback:* many simple delegating methods. *Anti:* Replace Delegation with Inheritance.
- **Replace Delegation with Inheritance**: A class delegates to **all** public methods of another → make it a subclass and delete the delegating methods. Only if it delegates to *all* methods (else Liskov violation) and has no existing parent. *Anti:* Replace Inheritance with Delegation.

## Mental Models
- **Pull up to share, push down to specialize.** Duplication rises; single-use behavior sinks.
- **Compose over Inherit**: when two independent variation axes appear (size × fur), inheritance dead-ends — use component fields (Strategy) instead of subclasses.
- **Delegation is more flexible; inheritance is leaner.** Swap toward delegation for flexibility/Liskov safety, toward inheritance to shed boilerplate — but only when *all* methods are delegated.
- **Template Method** = fix the algorithm skeleton in the parent, vary steps in children.

## Anti-patterns
- **Inheriting to reuse code** when it's not an is-a → Refused Bequest; prefer delegation.
- **Two-axis subclass explosion** (LargeSmoothDog, SmallShaggyDog…) — compose instead.
- **Collapsing a hierarchy carelessly** — can make unrelated classes wrongly inherit (Liskov break).

## Worked Example (Pull Up Constructor Body)
```java
// before
class Manager extends Employee {
    public Manager(String name, String id, int grade) {
        this.name = name; this.id = id; this.grade = grade;
    }
}
// after
class Manager extends Employee {
    public Manager(String name, String id, int grade) {
        super(name, id);   // common code moved to Employee constructor
        this.grade = grade;
    }
}
```

## Key Takeaways
1. Pull up shared members; push down single-use ones (cures Refused Bequest).
2. Extract Superclass/Interface/Subclass to introduce the right abstraction after the fact.
3. Template Method captures same-steps-same-order algorithms; Open/Closed for new variants.
4. Trade inheritance for delegation (Strategy) for flexibility/Liskov — and back only when delegating to *all* methods.

## Connects To
- **Ch 2 / Ch 3 / Ch 4**: cures Refused Bequest, Divergent Change, Duplicate Code, Lazy Class, Speculative Generality.
- **Ch 8**: `Replace Type Code with Subclasses` builds the hierarchies these operate on.
- **Ch 9**: `Replace Conditional with Polymorphism` needs the hierarchy built here.
