# Chapter 2: Object-Orientation Abusers (Code Smells)

## Core Idea
These smells are incomplete or incorrect application of OO principles — code that fights the object model instead of using it.

## Smells & Their Cures
- **Switch Statements**: A complex `switch` or `if/else` chain. Code for one switch often scatters across the program; a new case forces edits everywhere. **When you see `switch`, think polymorphism.**
  - Cure: isolate with `Extract Method` + `Move Method`; type-code switch → `Replace Type Code with Subclasses` / `State-Strategy`, then `Replace Conditional with Polymorphism`; same method + different params → `Replace Parameter with Explicit Methods`; a `null` branch → `Introduce Null Object`.
- **Temporary Field**: Fields set only under certain circumstances, empty the rest of the time — usually created to avoid passing many params into one algorithm. Confusing: fields you expect populated are almost always empty.
  - Cure: `Extract Class` for the field + its algorithm (= a method object); replace existence-checks with `Introduce Null Object`.
- **Refused Bequest**: A subclass uses only some inherited members; the rest go unused or throw. Inheritance was chosen only to reuse code, but the classes are truly different.
  - Cure: no real relationship → `Replace Inheritance with Delegation`; relationship valid → extract shared members into a new class both inherit (`Extract Superclass`).
- **Alternative Classes with Different Interfaces**: Two classes do the same job but with different method names. Author 2 didn't know class 1 existed.
  - Cure: `Rename Method` to align names; `Move Method`, `Add Parameter`, `Parameterize Method` to align signatures; partial overlap → `Extract Superclass`. Then delete one class if possible.

## Mental Models
- **See `switch` → reach for polymorphism.** A rare `switch` is an OO hallmark; a common one is a smell.
- Think of a Temporary Field as **a method object trying to escape** — the field + its algorithm belong in their own class.
- Refused Bequest asks: **"Is this really an is-a?"** If Dog inherits Chair because both have 4 legs, it's not.

## Anti-patterns
- **Inheriting purely for code reuse** when there's no is-a relationship → Refused Bequest.
- **Cramming an algorithm's scratch state into object fields** instead of a dedicated class → Temporary Field.

## Worked Example (Switch on type code → polymorphism)
The `getSpeed()` `switch (type)` over `EUROPEAN / AFRICAN / NORWEGIAN_BLUE` becomes an abstract `Bird.getSpeed()` with a subclass per case (see Ch 9 `Replace Conditional with Polymorphism`). Adding a bird type = adding a subclass, touching no existing code (Open/Closed).

## When to Ignore
- **Switch Statements**: leave simple switches alone; factories (`Factory Method`, `Abstract Factory`) legitimately switch to select a class.
- **Alternative Classes**: merging is pointless when the classes live in different libraries each with their own version.

## Key Takeaways
1. `switch` on type is the canonical trigger for the type-code refactorings and polymorphism.
2. Temporary Fields → `Extract Class`; the algorithm and its scratch data move together.
3. Distinguish Refused Bequest (bad inheritance → delegation) from a valid hierarchy needing an intermediate superclass.
4. Duplicate-behavior classes with mismatched names get unified via renaming + `Extract Superclass`.

## Connects To
- **Ch 8**: `Replace Type Code with Subclasses / State-Strategy` — the deeper cure for type-driven switches.
- **Ch 9**: `Replace Conditional with Polymorphism`, `Introduce Null Object`.
- **Ch 11**: `Replace Inheritance with Delegation`, `Extract Superclass` — cures for Refused Bequest.
