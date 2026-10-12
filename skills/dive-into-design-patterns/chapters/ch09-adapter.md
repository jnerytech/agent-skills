# Chapter 9: ADAPTER

## Core Idea
Adapter (aka Wrapper) is a structural pattern that lets objects with incompatible interfaces collaborate by inserting a translator object that converts one interface into another.

## Frameworks Introduced
- **Adapter**: a middle-layer object that converts the interface of a service so the client can call it.
  - When to use: Use when you want to use an existing class but its interface is incompatible with the rest of your code (legacy, 3rd-party, weird interface). Also use to reuse several existing subclasses lacking common functionality that can't be added to the superclass.
  - How: (1) Find at least two classes with incompatible interfaces — an unchangeable service and client(s). (2) Declare the client interface. (3) Create adapter class implementing the client interface (empty methods). (4) Add a field to hold the service object (set via constructor). (5) Implement each client-interface method, delegating real work to the service and handling only conversion. (6) Clients use the adapter only via the client interface.

## Key Concepts
- **Client**: class containing existing business logic.
- **Client Interface**: protocol classes must follow to collaborate with the client.
- **Service**: useful but incompatible class (usually 3rd-party/legacy).
- **Adapter**: implements client interface while wrapping the service; translates calls.
- **Object adapter**: uses composition — adapter wraps the service object.
- **Class adapter**: uses multiple inheritance — adapter inherits from both client and service.
- **Two-way adapter**: converts calls in both directions.

## Mental Models
- **Real-World Analogy**: A power plug adapter — US plug won't fit a German socket, so the adapter has an American-style socket and a European-style plug.
- Think of the adapter as a translator between two parties who speak different languages.
- Think of the square-peg-in-round-hole problem: the adapter pretends the square peg is a round peg.

## Anti-patterns
- **Adding an adapter when you could just change the service**: if you control the service class, simply matching it to your code may be simpler than introducing new interfaces/classes.
- **Coupling client code to a concrete adapter**: always work via the client interface so adapters can be swapped without breaking clients.

## Code Examples
```
// RoundHole works with RoundPeg via getRadius().
class RoundHole is
    method fits(peg: RoundPeg) is
        return this.getRadius() >= peg.radius()

// Incompatible: SquarePeg has getWidth(), not radius.
class SquarePeg is
    method getWidth() is ...

// Object adapter: extends RoundPeg, wraps a SquarePeg.
class SquarePegAdapter extends RoundPeg is
    private field peg: SquarePeg
    constructor SquarePegAdapter(peg) is this.peg = peg
    method getRadius() is
        return peg.getWidth() * Math.sqrt(2) / 2

hole.fits(small_sqpeg)          // won't compile (incompatible)
hole.fits(new SquarePegAdapter(small_sqpeg))  // true
```
- **What it demonstrates**: the adapter makes a SquarePeg usable wherever a RoundPeg is expected by translating width into an equivalent radius.

## Reference Tables
| Pros | Cons |
|------|------|
| Single Responsibility Principle: separates conversion code from business logic | Overall complexity increases — new interfaces and classes |
| Open/Closed Principle: introduce new adapters without breaking client code | Sometimes simpler to just change the service class |

| Object adapter | Class adapter |
|----------------|---------------|
| Uses composition (wraps service object) | Uses inheritance (inherits both interfaces) |
| Works in all popular languages | Needs multiple inheritance (e.g., C++) |
| Can adapt the service and its subclasses | Adaptation happens in overridden methods; usable in place of client class |

## Worked Example
A stock-market monitoring app downloads stock data in XML and renders charts. You want to integrate a smart 3rd-party analytics library that only accepts JSON — and you can't modify the library. Solution: build XML-to-JSON adapters for each analytics class your code touches. Each adapter implements the interface your app expects, translates incoming XML into JSON, and forwards calls to the wrapped analytics object. Your code now talks to the library only through these adapters.

## Key Takeaways
1. Adapter makes two incompatible interfaces work together without changing either party's code.
2. Object adapter (composition) is more flexible and portable than class adapter (inheritance).
3. The wrapped service is unaware of the adapter.
4. Clients depend on the client interface, not the concrete adapter — enabling Open/Closed.
5. Best for retrofitting legacy/3rd-party code into an existing app.

## Connects To
- **Bridge**: designed up-front for independent development; Adapter retrofits existing incompatible classes.
- **Decorator**: enhances an object without changing its interface and supports recursive composition; Adapter changes the interface and usually wraps one object.
- **Proxy**: same interface as wrapped object; Adapter gives a different one; Decorator gives an enhanced one.
- **Facade**: defines a new interface over a whole subsystem; Adapter makes an existing single object's interface usable.
- **Bridge/State/Strategy**: share Adapter's composition-based structure but solve different problems.
