# Chapter 25: VISITOR

## Core Idea
Visitor is a behavioral pattern that lets you separate algorithms from the objects on which they operate — adding new operations to a class hierarchy without modifying those classes.

## Frameworks Introduced
- **Visitor**: Place new behavior in a separate visitor class with a method per element type; elements "accept" a visitor and call back the matching method (Double Dispatch).
  - When to use: when you need to perform an operation over all elements of a complex object structure (e.g., an object tree); to clean auxiliary behaviors out of primary business classes; when a behavior makes sense only in some classes of a hierarchy.
  - How: (1) declare the visitor interface with one visiting method per concrete element class; (2) declare/add the element `accept(visitor)` method on the hierarchy's base; (3) implement `accept` in each concrete element to redirect to the matching visiting method; (4) elements know visitors only via the interface, while visitors know all concrete elements; (5) per new behavior, create a concrete visitor; (6) client creates visitors and passes them into elements via `accept`.

## Key Concepts
- **Visitor interface**: declares a set of visiting methods, one per element type (same names allowed via overloading, but distinct parameter types).
- **Concrete Visitor**: implements one variant of the behavior for every element class.
- **Element interface**: declares the `accept(visitor)` method.
- **Concrete Element**: implements `accept` to redirect the call to the visiting method matching its class.
- **Double Dispatch**: technique where the element (knowing its own class) picks the correct visitor method, avoiding type-checking conditionals.
- **Client**: usually a collection or Composite tree iterated over, unaware of concrete element classes.

## Mental Models
- **Real-World Analogy**: A seasoned insurance agent visiting buildings — selling medical insurance to a residence, theft insurance to a bank, fire/flood insurance to a coffee shop, depending on the occupant type.
- Think of `accept` as the element raising its hand to say "I'm a City — call doForCity on yourself."

## Anti-patterns
- **`instanceof`/type-checking chains to dispatch**: the nightmare Visitor replaces; use Double Dispatch via `accept`.
- **Relying on method overloading alone**: fails because the element's concrete class is unknown at compile time — overloading defaults to the base type.
- **Using Visitor on an unstable hierarchy**: every added/removed element class forces updating all visitors.

## Code Examples
```
interface Shape is
    method accept(v: Visitor)

class Dot extends Shape is
    method accept(v: Visitor) is
        v.visitDot(this)          // tells visitor the concrete class
class Circle extends Dot is
    method accept(v: Visitor) is
        v.visitCircle(this)

interface Visitor is
    method visitDot(d: Dot)
    method visitCircle(c: Circle)
    method visitRectangle(r: Rectangle)
    method visitCompoundShape(cs: CompoundShape)

class XMLExportVisitor is
    method visitDot(d: Dot) is        // export id + center
    method visitCircle(c: Circle) is  // export id, center, radius

// client
foreach (shape in allShapes) do
    shape.accept(exportVisitor)
```
- **What it demonstrates**: Double Dispatch — `shape.accept(v)` lets each shape route to the right `visit*` method, so XML export lives entirely in the visitor without conditionals.

## Reference Tables
| Pros | Cons |
|------|------|
| Open/Closed: add new behavior over many classes without changing them | Must update all visitors when an element class is added/removed |
| Single Responsibility: group versions of one behavior in one class | Visitors may lack access to elements' private fields/methods |
| A visitor can accumulate state while traversing a structure | |

## Worked Example
A geographic app stores data as a colossal graph; each node type (City, Industry, SightSeeing) is its own class. A task requires exporting the graph to XML, but the architect forbids changing the production-tested node classes — and more export formats are likely coming. Putting export code in nodes would also pollute their geodata responsibility. Visitor extracts export into an `ExportVisitor` with `doForCity`, `doForIndustry`, `doForSightSeeing`. To dispatch correctly each node gets a trivial `accept(v)` that calls the matching method (`v.doForCity(this)`). New behaviors then need only a new visitor class. The chapter's pseudocode reuses this for a Shape hierarchy (Dot, Circle, Rectangle, CompoundShape) exported via `XMLExportVisitor`.

## Key Takeaways
1. Visitor moves operations out of element classes into separate visitor classes.
2. Double Dispatch (element `accept` → visitor `visit*`) replaces type-checking conditionals.
3. One concrete visitor = one behavior implemented for every element type.
4. Adding a behavior is cheap; adding/removing an element type is expensive (touch every visitor).
5. A single trivial change (the `accept` method) to elements is the only modification required.

## Connects To
- **Command**: Visitor is like a powerful version of Command — its objects execute operations over objects of different classes.
- **Composite**: use Visitor to run an operation over an entire Composite tree.
- **Iterator**: use Visitor with Iterator to traverse a complex structure and operate on elements of different classes.
