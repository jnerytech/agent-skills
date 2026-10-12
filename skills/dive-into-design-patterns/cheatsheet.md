# Cheatsheet — Design Patterns Decisions

One page of judgment: when to reach for what, and which lookalike to pick.

## First filter — what's the problem?

| Symptom | Pattern group | Likely pattern |
|---|---|---|
| `new ConcreteClass()` scattered, types vary | Creational | Factory Method → Abstract Factory |
| Telescopic constructor / many optional params | Creational | Builder |
| Need copies but coupled to classes | Creational | Prototype |
| Must guarantee one shared instance | Creational | Singleton |
| Incompatible interfaces must talk | Structural | Adapter |
| Class explodes across two dimensions | Structural | Bridge |
| Tree of part-whole objects | Structural | Composite |
| Add behavior at runtime, no subclassing | Structural | Decorator |
| Complex subsystem, want simple door | Structural | Facade |
| Too many objects, RAM blows up | Structural | Flyweight |
| Need to control/guard access to an object | Structural | Proxy |
| Request handled by one of many, order matters | Behavioral | Chain of Responsibility |
| Need undo / queue / log operations | Behavioral | Command |
| Traverse collection without exposing it | Behavioral | Iterator |
| Objects too tangled, talk directly | Behavioral | Mediator |
| Snapshot/restore state | Behavioral | Memento |
| Many objects must react to changes | Behavioral | Observer |
| Behavior changes by state, big `if`s | Behavioral | State |
| Swap algorithm at runtime | Behavioral | Strategy |
| Same algorithm, a few differing steps | Behavioral | Template Method |
| Add ops to a hierarchy without editing it | Behavioral | Visitor |

## Design-principle decision rules (Ch03)

- **Changing tested, in-use code?** Extend, don't modify — add a subclass/strategy (OCP).
- **Inheritance multiplying subclasses across dimensions?** Switch to composition (Favor Composition Over Inheritance → often Bridge/Strategy).
- **A field or behavior that keeps changing?** Encapsulate What Varies — isolate it behind a method/class.
- **Depending on a concrete class?** Depend on its interface instead (Program to an Interface; DIP).
- **Class doing many unrelated things?** Split it (SRP). **Fat interface?** Split it (ISP).
- **Subclass can't honor the base contract?** You're breaking LSP — rethink the hierarchy.

## Lookalike disambiguation (the part people get wrong)

| If confused between… | Pick by this tell |
|---|---|
| **Factory Method vs Abstract Factory** | One product via subclassing → FM. A *family* of products → AF (often built from FMs). |
| **Abstract Factory vs Builder** | AF returns the product immediately; Builder runs extra steps before you fetch it. |
| **Adapter vs Decorator vs Proxy** | Adapter = *different* interface; Decorator = *enhanced* interface (adds behavior); Proxy = *same* interface (controls access, manages lifecycle itself). |
| **Adapter vs Bridge** | Adapter retrofits *existing* incompatible code; Bridge is designed up front to split dimensions. |
| **Decorator vs Composite** | Both tree-shaped: Decorator wraps *one* child and adds behavior; Composite holds *many* children and aggregates. |
| **Facade vs Adapter** | Facade = new simple interface to a *subsystem*; Adapter = usable interface to *one* object. |
| **Facade vs Mediator** | Subsystem objects don't know the Facade and still talk directly; Mediator's components talk *only* through it. |
| **Facade vs Proxy** | Both buffer a complex/heavy object; Proxy shares the service's interface and is interchangeable, Facade doesn't. |
| **State vs Strategy** | States *know each other* and trigger transitions; Strategies are independent and unaware of each other. State = extension of Strategy. |
| **Strategy vs Template Method** | Strategy = composition, swap at runtime; Template Method = inheritance, fixed at compile time. |
| **Command vs Strategy** | Same shape; Command = an *action/request* (with undo, receiver); Strategy = a *way of doing* a computation. |
| **Visitor vs Command** | Visitor = a more powerful Command that runs over a whole object structure via double dispatch. |
| **Flyweight vs Singleton** | Flyweight = *many* immutable shared objects; Singleton = *one* (usually mutable) instance. |

## Pattern → can-be-a-Singleton

Abstract Factory, Builder, Prototype, Facade often end up implemented as a single instance — but prefer dependency injection over Singleton when testability matters.

## Common pairings

- Abstract Factory **is built from** Factory Methods.
- Builder **builds** Composite trees.
- Iterator **traverses** Composite; Visitor **operates on** Composite, often using an Iterator.
- Command **uses** Memento for undo; **stored in** Prototype-cloned history.
- Mediator often **implemented on top of** Observer.
- Chain of Responsibility, Command, Mediator, Observer = four ways to wire **senders ↔ receivers**.

## Tells & smells → reach for a pattern

- Giant `switch`/`if` on a type field → **Strategy** or **State**.
- Duplicate traversal loops everywhere → **Iterator**.
- "Undo" requested late in the project → **Command** + **Memento**.
- One class importing half the codebase → **Facade** (or you built a god object).
- `new` of a third-party class deep in business logic → wrap in **Adapter**/**Factory Method**.
- Subclass count = dimensions multiplied → **Bridge**.

## Anti-pattern cautions

- **Singleton** hides dependencies and fights unit tests — use sparingly.
- **Facade / Mediator** can rot into a **god object** — split when they grow.
- Patterns add indirection: don't apply one without a real, recurring problem (Ch02 criticism).
