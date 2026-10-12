# Chapter 23: STRATEGY

## Core Idea
Strategy is a behavioral pattern that lets you define a family of algorithms, put each into a separate class, and make their objects interchangeable at runtime.

## Frameworks Introduced
- **Strategy**: Extract the varying algorithms from a bloated class into separate strategy classes sharing one interface; the original class (context) holds a reference to a strategy and delegates the work to it.
  - When to use: when you want different variants of an algorithm and switch them at runtime; when you have many similar classes differing only in behavior; to isolate business logic from algorithm details; when a massive conditional switches between variants of the same algorithm.
  - How: (1) identify a change-prone algorithm (or big conditional) in the context; (2) declare the strategy interface; (3) extract each algorithm into its own class implementing it; (4) add a strategy field + setter in the context, working only via the interface; (5) clients pick and pass a suitable strategy.

## Key Concepts
- **Strategy interface**: common to all variants; declares the method the context calls to execute the algorithm.
- **Concrete Strategy**: one implementation/variant of the algorithm.
- **Context**: holds a strategy reference, delegates execution, and knows nothing about which concrete strategy it uses.
- **Setter**: lets clients swap the active strategy at runtime.
- **Client**: aware of strategy differences; selects and injects the right one.

## Mental Models
- **Real-World Analogy**: Getting to the airport — bus, cab, or bicycle are interchangeable transportation strategies chosen by budget/time constraints.
- Think of the context as a device with a swappable battery (the strategy): same device, different power source.
- "Decorator changes the skin of an object; Strategy changes the guts."

## Anti-patterns
- **Overengineering**: if you have only a couple of rarely-changing algorithms, the extra classes/interfaces aren't worth it.
- **Hiding strategy choice from clients**: clients must understand differences to pick correctly.
- **Ignoring functional types**: in languages with lambdas, anonymous functions can replace strategy classes, avoiding boilerplate.

## Code Examples
```
interface Strategy is
    method execute(a, b)

class ConcreteStrategyAdd implements Strategy is
    method execute(a, b) is return a + b
class ConcreteStrategySubtract implements Strategy is
    method execute(a, b) is return a - b

class Context is
    private strategy: Strategy
    method setStrategy(Strategy strategy) is
        this.strategy = strategy
    method executeStrategy(a, b) is
        return strategy.execute(a, b)   // delegate

// client
if (action == addition) then
    context.setStrategy(new ConcreteStrategyAdd())
result = context.executeStrategy(first, second)
```
- **What it demonstrates**: The context runs arithmetic via interchangeable strategy objects chosen by the client at runtime, with no conditional inside the context.

## Reference Tables
| Pros | Cons |
|------|------|
| Swap algorithms at runtime | Overkill for few/stable algorithms |
| Isolate algorithm implementation from its user | Clients must know strategy differences |
| Replace inheritance with composition | Functional types may make classes redundant |
| Open/Closed: add strategies without changing context | |

### State vs. Strategy
| Strategy | State |
|----------|-------|
| Strategies are independent, unaware of each other | States may know each other and trigger transitions |
| Different ways of doing the same thing | Behavior bound to a lifecycle |
| State is an extension of Strategy | |

### Template Method vs. Strategy
| Template Method | Strategy |
|-----------------|----------|
| Inheritance; alter parts via subclasses | Composition; supply different strategies |
| Class level — static | Object level — switch at runtime |

## Worked Example
A navigation app built routes only over roads; then walking, public transport, cyclist, and tourist-attraction routes were added. Each new algorithm doubled the navigator's main class, made bug fixes risky, and caused merge conflicts. Strategy extracts each routing algorithm into a class with a single `buildRoute(origin, destination)` returning checkpoints. The navigator just renders checkpoints and exposes a method (used by UI buttons) to switch the active routing strategy — staying independent of concrete strategies.

## Key Takeaways
1. Strategy turns a family of algorithms into interchangeable objects behind one interface.
2. The context delegates and never knows the concrete strategy — enabling OCP.
3. The client chooses the strategy and can switch it at runtime.
4. It replaces inheritance with composition and kills algorithm-selecting conditionals.
5. Use lambdas instead of classes when the language supports functional types and the logic is small.

## Connects To
- **Bridge, State, Strategy, Adapter**: similar composition-based structures, different problems.
- **Command**: both parameterize objects with actions, but Command converts an operation into an object (queue/log/defer) while Strategy describes different ways of doing the same thing.
- **Decorator** changes skin; Strategy changes guts.
- **Template Method**: inheritance/static vs. Strategy's composition/runtime.
- **State**: an extension of Strategy that allows inter-state dependencies.
