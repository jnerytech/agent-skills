# Chapter 6: BUILDER

*Category: Creational.*

## Core Idea
Builder lets you construct complex objects step by step, producing different types and representations of an object using the same construction code.

## Frameworks Introduced
- **Builder**: Extracts object-construction code into separate builder objects that expose construction steps (`buildWalls`, `setEngine`, …); you call only the steps you need.
  - When to use: Use it to get rid of a "telescopic constructor" (a constructor overloaded with many optional parameters). Use it when you want your code to be able to create different representations of some product (for example, stone and wooden houses). Use it to construct Composite trees or other complex objects step by step.
  - How: (1) Confirm common construction steps exist for all representations. (2) Declare those steps in the base builder interface. (3) Create a concrete builder per representation, each with its own `getProduct` fetch method (can't go in the interface if products differ). (4) Optionally add a Director encapsulating reusable construction sequences. (5) Client creates builder + director and passes the builder to the director. (6) Fetch result from the director only if all products share an interface; otherwise from the builder.

## Key Concepts
- **Builder (interface)**: Declares construction steps common to all builders.
- **Concrete Builders**: Different implementations of the steps; may produce products that don't share an interface.
- **Products**: Resulting objects; products from different builders need not share a class/hierarchy.
- **Director**: Defines the *order* of construction steps; encapsulates reusable configurations. Optional.
- **Client**: Associates a builder with the director, launches construction, fetches the result from the builder.

## Mental Models
- **Real-World Analogy**: Same set of building steps, different materials — one builder uses wood and glass (a house), another stone and iron (a castle), another gold and diamonds (a palace). The director knows the sequence; builders know the materials.
- Think of the director as a recipe and builders as cooks with different pantries.

## Anti-patterns
- **Telescopic constructor**: `Pizza(size)`, `Pizza(size, cheese)`, `Pizza(size, cheese, pepperoni)`… — ugly calls where most params go unused. Builder replaces it.
- **Subclass explosion**: a subclass for every config combination breeds an unmanageable hierarchy.
- **Builder for simple objects**: it requires creating multiple new classes — only worth it when products are genuinely complex.
- **Exposing the unfinished product**: the builder must not let clients fetch an incomplete result mid-construction.

## Code Examples
```
interface Builder is
    method reset()
    method setSeats(...)
    method setEngine(...)
    method setTripComputer(...)
    method setGPS(...)

class CarBuilder implements Builder is
    private field car:Car
    method reset() is this.car = new Car()
    method setEngine(...) is // install engine
    method getProduct():Car is
        product = this.car
        this.reset()
        return product

class Director is
    method constructSportsCar(builder: Builder) is
        builder.reset()
        builder.setSeats(2)
        builder.setEngine(new SportEngine())
        builder.setTripComputer(true)
        builder.setGPS(true)
```
- **What it demonstrates**: The director's `constructSportsCar` sequence works against any `Builder`; results are fetched from the concrete builder (since `Car` and `Manual` share no interface).

## Reference Tables
| Pros | Cons |
|------|------|
| Construct objects step-by-step, defer or recurse steps | Overall code complexity rises (multiple new classes) |
| Reuse the same construction code for various representations | |
| Single Responsibility: isolate construction from business logic | |

## Worked Example
Building cars and their manuals. A `CarBuilder` configures `Car` parts; a `CarManualBuilder` implements the *same* steps but writes documentation into a `Manual`. The same `Director.constructSportsCar(builder)` sequence drives either one. Because a metal car and a paper manual share no interface, `getProduct()` lives on each concrete builder, not the director — so the director stays uncoupled from concrete products. Client can also skip the director and drive a builder directly for a fine-tuned model.

## Key Takeaways
1. Builder turns a giant constructor into a sequence of optional steps.
2. The Director owns the *order*; builders own the *implementation*; both are decoupled from concrete products.
3. The Director is optional — clients can call steps directly.
4. Fetch results from the builder when products don't share an interface.
5. Use it for complex objects, Composite trees, and to kill telescopic constructors.

## Connects To
- **Factory Method**: designs often start with it and evolve toward Builder.
- **Abstract Factory**: returns products immediately; Builder runs extra steps before fetching the product.
- **Composite**: Builder's recursive steps suit building Composite trees.
- **Bridge**: combine them — the director acts as the abstraction, builders as implementations.
- **Singleton**: Abstract Factories, Builders, and Prototypes can all be implemented as Singletons.
