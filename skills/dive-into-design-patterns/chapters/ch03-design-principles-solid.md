# Chapter 3: Software Design Principles

## Core Idea
Good design aims for code reuse and extensibility (planning for inevitable change); three foundational principles plus the five SOLID principles make architectures flexible, stable, and maintainable — and most patterns in this book are built on them.

## Frameworks Introduced
- **Encapsulate What Varies**: identify the aspects that vary and separate them from what stays the same, to minimize the effect of changes.
  - When to use: when you can anticipate a part of the code will change often (e.g. tax rules, shipping methods).
  - How: extract the changing logic into its own method, then (if it grows) its own class, isolating change behind a stable interface.
- **Program to an Interface, not an Implementation**: depend on abstractions, not concrete classes.
  - When to use: when two classes must collaborate and you want a flexible, extensible connection.
  - How: (1) determine what one object needs from the other; (2) describe those methods in a new interface/abstract class; (3) make the dependency implement it; (4) make the client depend on the interface, not the concrete class.
- **Favor Composition Over Inheritance**: reuse behavior via "has-a" (composition/aggregation) instead of "is-a" (inheritance).
  - When to use: when inheritance would multiply subclasses across several dimensions (combinatorial explosion).
  - How: extract each dimension of functionality into its own class hierarchy and delegate to those objects; behavior can then be swapped at runtime.
- **Single Responsibility Principle (SRP)**: a class should have just one reason to change.
  - When to use: when a class grows large and hard to focus on.
  - How: give each class responsibility for one part of the functionality, fully encapsulated; split out unrelated behaviors (e.g. move report printing out of `Employee`).
- **Open/Closed Principle (OCP)**: classes should be open for extension but closed for modification.
  - When to use: when adding features to already-tested, in-use code.
  - How: extend via subclassing / new strategy classes instead of editing existing code; do NOT use it to avoid fixing actual bugs.
- **Liskov Substitution Principle (LSP)**: subclass objects must be substitutable for superclass objects without breaking client code.
  - When to use: always when extending classes, especially in libraries/frameworks used by code you can't change.
  - How: follow the formal checklist — params equal/more abstract; returns equal/subtype; throw only same/subtype exceptions; don't strengthen pre-conditions or weaken post-conditions; preserve invariants; don't touch private fields.
- **Interface Segregation Principle (ISP)**: clients shouldn't be forced to depend on methods they don't use.
  - When to use: when an interface is "fat" and some implementers can't satisfy all of it.
  - How: break fat interfaces into granular ones; a class implements only the refined interfaces it needs (don't over-split).
- **Dependency Inversion Principle (DIP)**: high-level classes shouldn't depend on low-level classes; both depend on abstractions, and abstractions don't depend on details.
  - When to use: when business-logic classes risk being tied to primitive low-level (DB, disk, network) classes.
  - How: (1) describe low-level operations as interfaces in business terms (e.g. `openReport(file)`); (2) make high-level classes depend on those interfaces; (3) make low-level classes implement them, inverting the dependency direction.

## Key Concepts
- **Code reuse**: reducing cost/time by reusing existing code; hindered by tight coupling, concrete dependencies, hardcoding.
- **Extensibility**: designing for inevitable change (new platforms, trends, requirements).
- **Reuse levels**: classes < patterns < frameworks (more reuse but more risk going right).
- **Composition vs Aggregation**: composition manages the component's lifecycle; aggregation only references it.
- **Combinatorial explosion**: multiplying subclasses when extending inheritance across multiple dimensions.
- **SOLID**: mnemonic (SRP, OCP, LSP, ISP, DIP) from Robert Martin for understandable, flexible, maintainable design.
- **Pre/post-conditions & invariants**: contract elements LSP forbids breaking in subclasses.

## Mental Models
- Think of **Encapsulate What Varies as a ship's sealed compartments**: a hit (change) floods one compartment, not the whole hull.
- Think of **inheritance as "is-a" and composition as "has-a"** — a car *is a* transport but *has an* engine.
- Use **"one reason to change" as the test** for whether a class violates SRP.
- Remember OCP: a class can be **open (for extension) and closed (for modification) at the same time**.

## Anti-patterns
- **Mixing volatile logic into a general method** (tax math inside `getOrderTotal`): forces frequent edits to unrelated code.
- **Reusing code via deep inheritance**: breaks encapsulation, couples subclass to superclass, can't reduce the parent interface, breeds parallel hierarchies.
- **Subclass that throws on an inherited method** (read-only doc's `save` throws): violates LSP and forces type checks in clients (also breaks OCP).
- **Fat interfaces with stub methods**: a change breaks even clients that don't use the changed methods.
- **Applying SOLID dogmatically**: over-applying adds needless complexity — be pragmatic.

## Code Examples
```
// BEFORE: tax logic mixed in
method getOrderTotal(order) is
  total = 0
  foreach item in order.lineItems
    total += item.price * item.quantity
  if (order.country == "US")  total += total * 0.07
  else if (order.country == "EU") total += total * 0.20
  return total

// AFTER: encapsulate what varies
method getOrderTotal(order) is
  total = 0
  foreach item in order.lineItems
    total += item.price * item.quantity
  total += total * getTaxRate(order.country)
  return total

method getTaxRate(country) is
  if (country == "US") return 0.07
  else if (country == "EU") return 0.20
  else return 0
```
- **What it demonstrates**: extracting the varying tax logic into its own method isolates change (and is now easy to promote to a class).

## Reference Tables
| SOLID | Statement | One-line goal |
|---|---|---|
| S — SRP | A class should have one reason to change | Reduce complexity |
| O — OCP | Open for extension, closed for modification | Don't break existing code adding features |
| L — LSP | Subclasses substitutable for parents | Keep subclasses behaviorally compatible |
| I — ISP | Don't force clients to depend on unused methods | Narrow, granular interfaces |
| D — DIP | Depend on abstractions, not concretions | Invert high→low dependency |

LSP method checklist: params equal/more abstract • returns equal/subtype • exceptions same/subtype • don't strengthen pre-conditions • don't weaken post-conditions • preserve invariants • don't change private fields.

## Worked Example
An e-commerce `Order` class hardcodes all shipping methods, so each new method means editing (and risking) `Order` — violating OCP. Apply the Strategy pattern: extract shipping methods into separate classes behind a common `Shipping` interface. Now adding a method means deriving a new class from `Shipping` without touching `Order`; client code links the order to the chosen shipping object. As a bonus, delivery-time calculation moves to the relevant classes (SRP).

## Key Takeaways
1. Plan for change: isolate what varies behind stable interfaces.
2. Depend on abstractions, not concrete classes, to keep collaboration flexible.
3. Prefer composition + delegation over multi-dimensional inheritance to avoid class explosion (and gain runtime swapping).
4. Keep each class to one responsibility and extend rather than modify proven code.
5. Honor LSP's formal contract and split fat interfaces — but apply SOLID pragmatically, not dogmatically.

## Connects To
- **Ch 1**: builds on encapsulation, interfaces, inheritance, and composition vs aggregation.
- **Ch 2**: these principles underlie most patterns; examples already foreshadow Factory Method and Strategy.
