# Chapter 3: Change Preventers (Code Smells)

## Core Idea
Change Preventers mean one change forces edits in many places. Development becomes slow and expensive. The cure is realigning responsibilities so change is local.

## Smells & Their Cures
- **Divergent Change**: You change *many unrelated methods* in **one class** for different reasons (adding a product type forces edits to find, display, and order methods). One class, many reasons to change.
  - Cure: `Extract Class` to split behaviors by responsibility; if several classes share behavior, unify via `Extract Superclass` + `Extract Subclass`.
- **Shotgun Surgery**: The opposite — *one change* forces *many small edits across many classes*. A single responsibility got scattered (often from overzealous Divergent-Change fixing).
  - Cure: `Move Method` + `Move Field` to gather the scattered behavior into one class (create one if none fits); if the emptied classes are now useless → `Inline Class`.
- **Parallel Inheritance Hierarchies**: Every time you subclass class A, you must also subclass class B. A special case of Shotgun Surgery.
  - Cure: make instances of one hierarchy refer to instances of the other, then remove the referred hierarchy using `Move Method` + `Move Field`.

## Mental Models
- **Divergent Change = one class, many reasons to change** (violates SRP). **Shotgun Surgery = one reason, many classes to change.** They are mirror images.
- The fix direction is opposite: Divergent Change *splits* a class; Shotgun Surgery *gathers* scattered code together.
- Parallel hierarchies: **a subclass prefix duplicated across two trees** (e.g. every `X`-class needs an `X`-handler) signals the coupling.

## Anti-patterns
- **Over-applying Extract Class** until responsibility is smeared across too many classes → you've created Shotgun Surgery.
- Chasing de-duplication of parallel hierarchies into **uglier code** — sometimes the parallel structure is the lesser evil.

## Worked Example (recognizing the pair)
Adding a new `Product` type:
- If you edit `findProduct`, `displayProduct`, `orderProduct` all inside `ProductManager` → **Divergent Change** → `Extract Class` into `ProductFinder`, `ProductRenderer`, `ProductOrderer`.
- If adding one product type forces touching `Catalog`, `Cart`, `Invoice`, `Report` → **Shotgun Surgery** → `Move Method`/`Move Field` to centralize product logic.

## When to Ignore
- **Parallel Inheritance Hierarchies**: if de-duplication attempts produce even uglier code, revert and live with the parallel structure — it may be avoiding a bigger architectural mess.

## Key Takeaways
1. Diagnose by the *shape* of change: one-class-many-methods (Divergent) vs one-change-many-classes (Shotgun).
2. Divergent Change → split (Extract Class). Shotgun Surgery → gather (Move Method/Field, Inline Class).
3. Both smells are SRP violations at different granularities.
4. Not all parallel hierarchies are worth un-parallelizing.

## Connects To
- **Ch 4**: `Data Class`, `Lazy Class` often appear after gathering/splitting.
- **Ch 7**: `Extract Class`, `Inline Class`, `Move Method`, `Move Field` — the primary tools here.
- **Ch 11**: `Extract Superclass` / `Extract Subclass` for combining shared behavior.
