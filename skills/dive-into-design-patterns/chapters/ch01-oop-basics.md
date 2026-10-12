# Chapter 1: Introduction to OOP

## Core Idea
OOP wraps data and the behavior related to that data into objects (instances built from class blueprints); it rests on four pillars (abstraction, encapsulation, inheritance, polymorphism) and four kinds of relations between objects.

## Frameworks Introduced
- **Four Pillars of OOP**: the concepts that differentiate OOP from other paradigms — Abstraction, Encapsulation, Inheritance, Polymorphism.
  - When to use: whenever modeling a domain as collaborating objects.
  - How: model only context-relevant attributes/behaviors (abstraction); expose a public interface and hide internals (encapsulation); build new classes atop existing ones for reuse (inheritance); let a program call the right implementation for an object's real type (polymorphism).

## Key Concepts
- **Class**: a blueprint that defines the structure (fields + methods) for objects.
- **Object**: a concrete instance of a class; same fields as siblings, but different values.
- **Fields / Methods / Members**: attributes (state), behaviors, and the two collectively.
- **State vs Behavior**: data in fields is state; methods define behavior.
- **Superclass / Subclass**: parent class and its children; subclasses inherit state and behavior, adding or overriding only what differs.
- **Class hierarchy**: a pyramid of classes where a subclass inherits from all ancestors (e.g. Cat ← Animal ← Organism).
- **Interface**: the public part of an object, open to interactions with other objects.
- **Abstraction**: a model of a real object limited to a specific context, keeping relevant details and omitting the rest.
- **Encapsulation**: hiding implementation behind a simple public interface (start switch, not crankshaft wiring).
- **Polymorphism**: a program detecting an object's real class and calling its implementation even when the type is unknown in context.

## Mental Models
- Think of a **class as a blueprint** and an **object as a building** made from it.
- Think of **encapsulation as a car's controls**: you turn a key; the engine internals stay hidden under the hood.
- Think of **polymorphism as objects pretending to be a generic supertype** — cats and dogs in a bag all act as Animals until you make them speak.
- Use an **abstract method** when every subclass must supply its own behavior and no sensible default exists (e.g. `makeSound`).

## Anti-patterns
- **Modeling a real object with 100% fidelity**: pointless — model only what the context needs.
- **Trying to hide an inherited method in a subclass**: impossible — subclasses share the superclass interface and must implement all abstract methods even when meaningless.

## Code Examples
```
bag = [new Cat(), new Dog()]
foreach (Animal a : bag)
    a.makeSound()
// Meow!
// Woof!
```
- **What it demonstrates**: polymorphism — the loop calls each object's real `makeSound` without knowing its concrete type.

## Reference Tables
| Relation | Meaning | Lifecycle control | UML notation |
|---|---|---|---|
| Association | one object uses/interacts with another (like a field) | independent | plain arrow (point each end if bi-directional) |
| Dependency | weaker association; one class changes when another's definition changes (param, instantiation, use) | independent, no permanent link | dashed arrow |
| Aggregation | container holds a reference; component can exist alone and be shared | container does NOT control | line + empty diamond at container |
| Composition | whole-part; component exists only as part of the container | container controls | line + filled diamond at container |

Inheritance/implementation are the other two relations: a subclass can extend only one superclass but implement many interfaces.

## Worked Example
Oscar and Luna are both objects of the `Cat` class — same fields (name, sex, age, color), different values. Cats and dogs share name/sex/age/color and breathe/sleep/run, so extract a base `Animal` superclass; `Cat` adds `meow`, `Dog` adds `bark`. Go further and add `Organism` above `Animal` and `Plant`, forming a hierarchy where `Cat` inherits from both.

## Key Takeaways
1. Define structure once in a class; create many objects from it.
2. Use inheritance for code reuse, but accept that subclasses share (and must satisfy) the parent interface.
3. Expose a minimal interface; hide implementation so it can change freely.
4. Lean on polymorphism + interfaces to write code that works with any implementing type.
5. Distinguish the four relations — especially composition (controls lifecycle) vs aggregation (merely references).

## Connects To
- **Ch 2**: these OOP relations are the vocabulary used to describe pattern structures.
- **Ch 3**: encapsulation, interfaces, and composition vs inheritance become explicit design principles.
