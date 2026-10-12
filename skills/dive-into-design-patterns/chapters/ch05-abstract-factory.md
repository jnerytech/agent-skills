# Chapter 5: ABSTRACT FACTORY

*Category: Creational.*

## Core Idea
Abstract Factory lets you produce families of related objects without specifying their concrete classes.

## Frameworks Introduced
- **Abstract Factory**: An interface with creation methods for every product in a family (e.g. `createChair`, `createSofa`); each concrete factory produces one consistent variant.
  - When to use: Use it when your code needs to work with various families of related products, but you don't want it to depend on the concrete classes of those products — they might be unknown beforehand or you simply want to allow for future extensibility. Also consider it when you have a class with a set of Factory Methods that blur its primary responsibility.
  - How: (1) Map a matrix of product types vs variants. (2) Declare abstract product interfaces for all types; make concrete products implement them. (3) Declare the abstract factory interface with creation methods for all abstract products. (4) Implement one concrete factory class per variant. (5) Add factory initialization code that picks a concrete factory by config/environment and passes it to product-constructing classes. (6) Replace direct product constructor calls with factory creation-method calls.

## Key Concepts
- **Abstract Products**: Interfaces for a set of distinct but related products in a family (Chair, Sofa, CoffeeTable).
- **Concrete Products**: Variant-grouped implementations; each product type implemented in every variant.
- **Abstract Factory**: Interface declaring a creation method per abstract product.
- **Concrete Factories**: Implement those methods; each corresponds to one variant and creates only that variant's products. Their signatures return abstract products.
- **Client**: Works with factories and products only through abstract interfaces.

## Mental Models
- **Real-World Analogy**: A furniture shop simulator. Chair + Sofa + CoffeeTable come in Modern, Victorian, ArtDeco variants; a `ModernFactory` produces only Modern pieces so a customer never gets a Modern sofa with Victorian chairs.
- Think of a concrete factory as a "matched set" guarantee: whatever it returns is style-compatible with everything else it returns.

## Anti-patterns
- **Mixing variants**: directly instantiating concrete products risks pairing incompatible variants (macOS controls inside a Windows app). Route all creation through one factory.
- **Pattern overuse**: it introduces many new interfaces/classes; the code may become more complicated than the problem warrants.

## Code Examples
```
interface GUIFactory is
    method createButton():Button
    method createCheckbox():Checkbox

class WinFactory implements GUIFactory is
    method createButton():Button is   return new WinButton()
    method createCheckbox():Checkbox is return new WinCheckbox()

class MacFactory implements GUIFactory is
    method createButton():Button is   return new MacButton()
    method createCheckbox():Checkbox is return new MacCheckbox()

class Application is
    constructor Application(factory: GUIFactory) is
        this.factory = factory
    method createUI() is
        this.button = factory.createButton()
```
- **What it demonstrates**: One factory interface, OS-specific concrete factories; the `Application` gets a whole compatible UI family without naming concrete classes.

## Reference Tables
| Pros | Cons |
|------|------|
| Products from a factory are guaranteed compatible | Code can become more complicated than it should be |
| Avoids tight coupling between concrete products and client | Many new interfaces and classes are introduced |
| Single Responsibility: creation code in one place | |
| Open/Closed: add new variants without breaking client code | |

## Worked Example
Cross-platform UI elements. `GUIFactory` declares `createButton()` / `createCheckbox()`. `WinFactory` and `MacFactory` each produce a matching family. At launch, `ApplicationConfigurator` reads `config.OS`, instantiates the matching factory, and hands it to `Application`. The rest of the code uses only `GUIFactory`, `Button`, `Checkbox` — adding a new OS means adding a factory class plus a line in init, with no client changes.

## Key Takeaways
1. Abstract Factory creates whole *families* of related, mutually compatible objects.
2. One concrete factory = one variant; signatures return abstract product types.
3. Compatibility is the core benefit over plain Factory Method.
4. The app picks the concrete factory once, at init, by config/environment.
5. Open/Closed for variants, at the cost of more classes.

## Connects To
- **Factory Method**: Abstract Factory classes are often based on a set of Factory Methods; designs start with Factory Method and evolve toward Abstract Factory.
- **Builder**: Abstract Factory returns products immediately; Builder runs extra construction steps before returning. Both can target the evolution from Factory Method.
- **Prototype**: can compose an Abstract Factory's methods instead of Factory Methods.
- **Facade**: Abstract Factory can be an alternative when you only want to hide how subsystem objects are created.
- **Bridge**: pair them when some Bridge abstractions only work with specific implementations.
- **Singleton**: Abstract Factories, Builders, and Prototypes can all be implemented as Singletons.
