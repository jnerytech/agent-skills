# Chapter 12: DECORATOR

## Core Idea
Decorator (aka Wrapper) is a structural pattern that attaches new behaviors to objects by placing them inside special wrapper objects that share the same interface and contain the added behavior.

## Frameworks Introduced
- **Decorator**: wrap an object in another object of the same interface; the wrapper delegates to the target and adds behavior before/after. Stack multiple wrappers for combined behavior.
  - When to use: Use when you need to assign extra behaviors to objects at runtime without breaking code that uses them; and when extending behavior via inheritance is awkward or impossible (e.g., a `final` class can only be reused by wrapping it).
  - How: (1) Represent the domain as a primary component plus optional layers. (2) Declare a component interface with methods common to component and layers. (3) Create a concrete component with the base behavior. (4) Create a base decorator class with a field (typed as the component interface) holding the wrapped object; delegate all work to it. (5) Ensure all classes implement the component interface. (6) Create concrete decorators extending the base decorator, executing behavior before/after the parent call. (7) Client creates and composes the decorators.

## Key Concepts
- **Component**: common interface for both wrappers and wrapped objects.
- **Concrete Component**: object being wrapped; defines the basic behavior.
- **Base Decorator**: holds a component-typed reference to a wrapped object and delegates all operations to it.
- **Concrete Decorator**: adds extra behavior before/after delegating to the parent.
- **Wrapper / wrappee**: the decorator and the object it links to.
- **Stack**: chain of wrappers, where the outermost is the object the client uses.

## Mental Models
- **Real-World Analogy**: wearing clothes — a sweater, then a jacket, then a raincoat. Each garment "extends" your behavior, isn't part of you, and can be taken off anytime.
- Think of a decorator as an onion layer: each layer adds something while passing the request inward.

## Anti-patterns
- **Inheritance for every behavior combination**: extending Notifier into SMS/Slack/Facebook subclasses, then combining them, causes a combinatorial explosion of subclasses and bloats both library and client code.
- **Inheritance's caveats**: it's static (can't change behavior at runtime) and single-parent (no multiple behaviors) — Decorator (composition) overcomes both.
- **Order-dependent decorators**: hard to make behavior independent of stack order; hard to remove a specific wrapper from the stack.

## Code Examples
```
// Component interface.
interface DataSource is
    method writeData(data)
    method readData(): data

// Concrete component.
class FileDataSource implements DataSource is
    method writeData(data) is // Write to file.
    method readData(): data is // Read from file.

// Base decorator: wraps a DataSource, delegates everything.
class DataSourceDecorator implements DataSource is
    protected field wrappee: DataSource
    constructor DataSourceDecorator(source) is wrappee = source
    method writeData(data) is wrappee.writeData(data)
    method readData(): data is return wrappee.readData()

// Concrete decorators add behavior around the delegate.
class EncryptionDecorator extends DataSourceDecorator is
    method writeData(data) is // encrypt, then wrappee.writeData
    method readData(): data is // wrappee.readData, then decrypt

class CompressionDecorator extends DataSourceDecorator is
    method writeData(data) is // compress, then delegate

// Assemble a stack: Encryption > Compression > FileDataSource
source = new FileDataSource("salary.dat")
source = new CompressionDecorator(source)
source = new EncryptionDecorator(source)
source.writeData(salaryRecords)  // compressed + encrypted
```
- **What it demonstrates**: encryption and compression are added independently of the file code; wrappers stack and remain interchangeable because all share the DataSource interface.

## Reference Tables
| Pros | Cons |
|------|------|
| Extend behavior without subclassing | Hard to remove a specific wrapper from the stack |
| Add/remove responsibilities at runtime | Hard to make behavior independent of stack order |
| Combine behaviors by stacking multiple decorators | Initial layer-configuration code can look ugly |
| Single Responsibility: split a monolithic class into smaller ones | |

### Decorator vs. Inheritance
| Decorator (composition) | Inheritance |
|-------------------------|-------------|
| Dynamic — change behavior at runtime | Static — fixed at compile time |
| Combine many behaviors via multiple wrappers | One parent class; combinations explode into subclasses |
| Swap the helper object freely | Must replace the whole object with another subclass instance |

## Worked Example
A notification library starts with a Notifier that emails a fixed list. Users want SMS, Facebook, and Slack too — and several channels at once. Subclassing for each combination explodes. Solution: keep basic email in the base Notifier, turn each other channel into a decorator sharing the Notifier interface. The client wraps a base notifier in whatever decorators it wants (SMS over Slack over email), forming a stack. The outermost decorator is what the client calls; because every decorator implements the same interface, the rest of the code can't tell a plain notifier from a decorated one.

## Key Takeaways
1. Decorator adds responsibilities dynamically by wrapping, not subclassing.
2. Wrappers share the component interface, so they're interchangeable and stackable.
3. Composition over inheritance overcomes inheritance's static, single-parent limits.
4. A base decorator delegates all work; concrete decorators add behavior before/after.
5. Watch out for order-dependence and the difficulty of removing a specific layer.

## Connects To
- **Adapter**: changes interface; Decorator enhances/keeps the interface and supports recursive composition.
- **Proxy**: same interface as the wrapped object (and manages its lifecycle); Decorator gives an enhanced interface and is controlled by the client.
- **Chain of Responsibility**: similar structure, but CoR handlers act independently and can stop the request; decorators keep the interface consistent and never break the flow.
- **Composite**: similar recursive-composition diagram, but a Decorator has one child and adds responsibilities; they can cooperate.
- **Strategy**: Decorator changes an object's "skin," Strategy changes its "guts."
- **Prototype**: clone heavily decorated/composed structures instead of rebuilding.
