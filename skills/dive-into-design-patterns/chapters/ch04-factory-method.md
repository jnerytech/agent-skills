# Chapter 4: FACTORY METHOD

*Also known as: Virtual Constructor. Category: Creational.*

## Core Idea
Factory Method provides an interface for creating objects in a superclass, but allows subclasses to alter the type of objects that will be created. Direct `new` calls are replaced by calls to a special factory method.

## Frameworks Introduced
- **Factory Method**: A method in the creator (super)class that returns product objects; subclasses override it to change the product type.
  - When to use: Use it when you don't know beforehand the exact types and dependencies of the objects your code should work with. Use it when you want to provide users of your library or framework with a way to extend its internal components. Use it when you want to save system resources by reusing existing objects instead of rebuilding them each time.
  - How: (1) Make all products follow a common interface. (2) Add an empty factory method in the creator with the product interface as return type. (3) Replace product constructor calls in creator code with calls to the factory method (a temporary type parameter may help). (4) Create creator subclasses per product type and override the factory method. (5) If too many product types, reuse a control parameter instead of subclassing. (6) If the base method becomes empty make it abstract, else keep a default.

## Key Concepts
- **Product**: Interface common to all objects the creator and its subclasses can produce.
- **Concrete Products**: Different implementations of the product interface.
- **Creator**: Declares the factory method (return type = product interface); usually also holds core business logic that relies on products.
- **Concrete Creators**: Override the base factory method to return a different product type.
- **Client code**: Uses the creator via its base interface; treats all products as the abstract product.

## Mental Models
- **Real-World Analogy**: A software company's primary function is writing code, not "producing programmers" — yet it may have a training department. Likewise, product creation is *not* the creator's primary responsibility; the factory method merely decouples business logic from concrete product classes.
- Think of the factory method as a hook: the base class owns the workflow, subclasses decide which concrete piece plugs in.

## Anti-patterns
- **Introducing the pattern with no existing creator hierarchy**: forces many new subclasses, raising complexity. Best applied when you already have a creator hierarchy to slot it into.
- **Returning products without a shared interface**: subclasses may only vary the product type if all products share a common base class/interface; otherwise the client breaks.

## Code Examples
```
class Dialog is
    abstract method createButton()
    method render() is
        Button okButton = createButton()   // call factory method
        okButton.onClick(closeDialog)
        okButton.render()

class WindowsDialog extends Dialog is
    method createButton() is
        return new WindowsButton()

class WebDialog extends Dialog is
    method createButton() is
        return new HTMLButton()

interface Button is
    method render()
    method onClick(f)
```
- **What it demonstrates**: The base `Dialog` owns `render()`'s workflow while subclasses decide the concrete `Button` — same logic, OS-specific products.

## Reference Tables
| Pros | Cons |
|------|------|
| Avoids tight coupling between creator and concrete products | Code can grow complicated — many new subclasses needed |
| Single Responsibility: product creation lives in one place | Best case only when added to an existing creator hierarchy |
| Open/Closed: add new product types without breaking client code | |

## Worked Example
Cross-platform UI: a base `Dialog` renders a window using buttons. Declaring `createButton()` as a factory method lets `WindowsDialog` return `WindowsButton` and `WebDialog` return `HTMLButton`, both implementing `Button`. The `Application` reads config (`config.OS`) and instantiates the matching dialog, then works with it through the base `Dialog` interface — no dialog logic is rewritten per OS. Adding more factory methods nudges you toward Abstract Factory.

## Key Takeaways
1. Replace `new` with a factory method so subclasses control the product type.
2. All products must share a common interface; the factory method's return type is that interface.
3. The creator's main job is business logic, not creation — the pattern decouples the two.
4. Extend by adding a creator subclass (Open/Closed), no client changes.
5. A factory method may return cached/pooled objects, not just fresh ones.

## Connects To
- **Abstract Factory**: often built from a set of Factory Methods; designs evolve from Factory Method toward it.
- **Prototype / Builder**: also evolutionary targets (more flexible, more complex). Prototype isn't inheritance-based (no subclass drawbacks) but needs complex clone init; Factory Method is inheritance-based but needs no init step.
- **Iterator**: Factory Method lets collection subclasses return compatible iterators.
- **Template Method**: Factory Method is a specialization of it and may serve as one of its steps.
