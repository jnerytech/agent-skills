# Chapter 7: PROTOTYPE

*Also known as: Clone. Category: Creational.*

## Core Idea
Prototype lets you copy existing objects without making your code dependent on their classes.

## Frameworks Introduced
- **Prototype**: Delegates cloning to the objects themselves via a common interface (usually a single `clone` method), so copying doesn't couple your code to concrete classes.
  - When to use: Use it when your code shouldn't depend on the concrete classes of objects that you need to copy. Use it when you want to reduce the number of subclasses that only differ in the way they initialize their respective objects.
  - How: (1) Create a prototype interface with a `clone` method (or add it to an existing hierarchy). (2) Give each prototype class an alternative constructor that accepts an object of its own class and copies all its fields; subclasses call the parent constructor to copy private parent fields. (3) The clone method is usually one line: `new` with the prototypical constructor — each class must override it with its own class name. (4) Optionally build a prototype registry cataloguing frequently used prototypes.

## Key Concepts
- **Prototype (interface)**: Declares the cloning method(s), commonly just `clone`.
- **Concrete Prototype**: Implements cloning; may handle edge cases like linked objects and recursive dependencies.
- **Client**: Produces a copy of any object that follows the prototype interface.
- **Prototype Registry**: Stores pre-built, ready-to-copy prototypes (simplest = name → prototype hash map).
- **Prototype constructor**: Alternative constructor initializing a fresh object from an existing one's field values.

## Mental Models
- **Real-World Analogy**: Mitotic cell division — the original cell acts as a prototype and takes an *active* role in producing an identical copy (unlike passive industrial prototypes that don't copy themselves).
- Think of pre-built prototypes as configuration presets you clone instead of subclassing.

## Anti-patterns
- **Copying "from the outside"**: manually reading fields fails because some fields are private and invisible; let the object clone itself.
- **Class-coupled duplication**: needing the concrete class to copy creates a dependency — especially broken when you only know an interface, not the class.
- **Cloning objects with circular references**: can get very tricky.

## Code Examples
```
abstract class Shape is
    field X, Y: int
    field color: string
    constructor Shape(source: Shape) is   // prototype constructor
        this.X = source.X
        this.Y = source.Y
        this.color = source.color
    abstract method clone():Shape

class Rectangle extends Shape is
    field width, height: int
    constructor Rectangle(source: Rectangle) is
        super(source)                    // copy parent's private fields
        this.width = source.width
        this.height = source.height
    method clone():Shape is
        return new Rectangle(this)
```
- **What it demonstrates**: Each subclass overrides `clone` using its own type; `super(source)` copies inherited fields. Until the constructor finishes, nobody can access the partly-built clone, keeping results consistent.

## Reference Tables
| Pros | Cons |
|------|------|
| Clone objects without coupling to their concrete classes | Cloning objects with circular references is tricky |
| Get rid of repeated initialization code via pre-built prototypes | |
| Produce complex objects more conveniently | |
| Alternative to inheritance for configuration presets | |

## Worked Example
Cloning geometric shapes. All shapes implement a `clone` method. The client holds a `shapes` array of mixed `Circle`/`Rectangle` objects and, in `businessLogic`, iterates calling `s.clone()` on each. Thanks to polymorphism, each call dispatches to the real subclass's clone, yielding proper typed copies — the client never needs to know the concrete element types. A registry could store frequently used pre-configured shapes for lookup-and-clone.

## Key Takeaways
1. Objects clone themselves, so cloning code stays independent of concrete classes.
2. A prototype constructor copies fields; subclasses call `super` for parent's private fields.
3. Every class must override `clone` with its own class name or you'll get a parent-type object.
4. Prototypes are an alternative to subclassing for many pre-configured variants.
5. A registry centralizes access to frequently used prototypes.

## Connects To
- **Factory Method**: Prototype isn't inheritance-based (no subclass drawbacks) but needs complex clone init; Factory Method is inheritance-based but needs no init step. Designs evolve from Factory Method toward Prototype.
- **Abstract Factory**: can use Prototype to compose its creation methods.
- **Command**: Prototype helps save copies of Commands into history.
- **Composite / Decorator**: clone complex structures instead of rebuilding from scratch.
- **Memento**: Prototype can be a simpler alternative for straightforward state without external links.
- **Singleton**: Abstract Factories, Builders, and Prototypes can all be implemented as Singletons.
