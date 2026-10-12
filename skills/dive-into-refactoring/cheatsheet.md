# Cheatsheet — Dive Into Refactoring

## Smell → Refactoring (decision rules)
| See this smell | Do this |
|---|---|
| Long Method | Extract Method; locals block it → Replace Temp with Query / Method Object |
| Large Class | Extract Class / Subclass / Interface |
| Primitive Obsession | Replace Data Value with Object; Replace Type Code with * |
| Long Parameter List | Preserve Whole Object / Introduce Parameter Object / Replace Parameter with Method Call |
| Data Clumps | Extract Class (fields) / Introduce Parameter Object (params) |
| Switch Statements | Replace Conditional with Polymorphism (after type-code subclassing) |
| Temporary Field | Extract Class / Introduce Null Object |
| Refused Bequest | Replace Inheritance with Delegation / Push Down Method+Field |
| Alternative Classes, Diff Interfaces | Rename Method + Extract Superclass |
| Divergent Change | Extract Class (split) |
| Shotgun Surgery | Move Method+Field (gather) / Inline Class |
| Comments | Extract Method/Variable + Rename Method |
| Duplicate Code | Extract Method (same class) / Extract Superclass (unrelated) / Form Template Method (similar) |
| Lazy Class | Inline Class / Collapse Hierarchy |
| Data Class | Encapsulate Field+Collection; Move Method in |
| Dead / Speculative | Delete / Inline / Remove Parameter / Collapse Hierarchy |
| Feature Envy | Move Method (to the data) |
| Inappropriate Intimacy | Move Method+Field / Change Bidirectional→Unidirectional |
| Message Chains | Hide Delegate |
| Middle Man | Remove Middle Man |
| Incomplete Library Class | Introduce Foreign Method (1) / Local Extension (many) |

## Trigger heuristics (tells & smells)
- Method **> ~10 lines** → suspect Long Method.
- **> 3–4 parameters** → Long Parameter List.
- **Feel like commenting inside a method** → Extract Method instead.
- **See `switch` / `if-else` on a type** → think polymorphism.
- **Rightward-drifting nested `if` arrow** → Guard Clauses.
- **`a.b().c().d()`** → Message Chain → Hide Delegate.
- **Fields empty most of the time** → Temporary Field.
- **Delete one var and the rest make no sense** → Data Clump.
- **Method both returns a value and mutates** → Separate Query from Modifier.

## Type Code decision tree
- Value **not** used in conditionals / no behavior → **Replace Type Code with Class**
- Drives behavior, **immutable**, no existing hierarchy → **Replace Type Code with Subclasses** → finish with Replace Conditional with Polymorphism
- Drives behavior, **changes at runtime** OR hierarchy blocked → **Replace Type Code with State/Strategy**
  - Strategy = pick an algorithm · State = value governs whole object condition

## Reference vs Value
| | Reference | Value |
|---|---|---|
| Mapping | one obj per real thing | many objs per thing |
| Examples | user, order, product | date, money, range, color |
| Mutability | mutable, shared | immutable preferred |
| Cost | needs storage/lookup | easy to implement |

## Inheritance vs Delegation
- Subclass uses **only part** of superclass / breaks Liskov → **Replace Inheritance with Delegation** (→ Strategy).
- Class delegates to **all** methods of another, no parent yet → **Replace Delegation with Inheritance**.
- Two independent variation axes (size × fur) → **Compose over Inherit**, not subclasses.

## Paired inverses (anti-refactorings)
Extract Method ⇄ Inline Method · Extract Variable ⇄ Inline Temp · Extract Class ⇄ Inline Class · Hide Delegate ⇄ Remove Middle Man · Change Value ⇄ Reference · Uni ⇄ Bidirectional Association · Parameterize Method ⇄ Replace Parameter with Explicit Methods · Add ⇄ Remove Parameter · Pull Up ⇄ Push Down · Replace Inheritance ⇄ Delegation · Replace Error Code with Exception ⇄ Replace Exception with Test

## Safe signature-change mechanic (Rename/Add/Remove Parameter)
1. Copy old method → new method with the change.
2. Point old method's body at the new one.
3. Redirect all callers to new.
4. Delete old — **unless public API → mark deprecated instead.**
(Also: check super/subclass overrides before starting.)

## Guiding principles invoked
- **SRP** — Extract Class, Duplicate Observed Data, Replace Type Code with Subclasses
- **Open/Closed** — polymorphism, subclasses, Template Method
- **Liskov** — inheritance⇄delegation, Collapse Hierarchy
- **Tell-Don't-Ask** — Replace Conditional with Polymorphism
- **CQRS** — Separate Query from Modifier
- **Things that change together belong together** — Move Method (Feature Envy)
