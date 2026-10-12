# Glossary — Dive Into Design Patterns

Terms with chapter references. Pattern names in **bold caps**.

**Abstract Factory** — creational pattern producing families of related objects without naming concrete classes (Ch05).
**Abstract Class** — base holding the template method + abstract/optional steps for subclasses to fill (Ch24).
**Abstract Product** — interface for one product type in a family (Ch05).
**Abstraction (OOP)** — a model of a real object limited to a specific context (Ch01).
**Abstraction (Bridge)** — the high-level control layer that delegates work to an implementation (Ch10).
**Adaptee / Service** — the incompatible class an Adapter wraps (Ch09).
**Adapter** — structural pattern; a wrapper translating one interface into another so incompatible classes collaborate (Ch09).
**Additional Facade** — a second facade carved out to keep one facade from becoming a god object (Ch13).
**Aggregation** — one object references another that can exist independently (empty-diamond) (Ch01, Ch03).
**Architectural pattern** — high-level, whole-application pattern, language-independent (Ch02).
**Association** — a permanent link where one object uses or interacts with another (Ch01).
**Backreference (State)** — a state's pointer to its context, used to trigger transitions (Ch22).
**Base Decorator** — decorator holding a component-typed wrappee and delegating to it (Ch12).
**Base Handler** — optional class holding the `next` reference and default forwarding (Ch16).
**Behavioral patterns** — patterns about object communication and assignment of responsibilities (Ch02, Ch16–25).
**Bridge** — structural pattern splitting a class into independent Abstraction and Implementation hierarchies (Ch10).
**Builder** — creational pattern building complex objects step by step (Ch06).
**Caretaker** — holds Mementos but cannot read their contents (Ch20).
**Chain of Responsibility (CoR)** — behavioral pattern passing a request along a chain of handlers (Ch16).
**Class** — a blueprint defining the structure and behavior of objects (Ch01).
**Class adapter** — adapter via multiple inheritance (needs language support, e.g. C++) (Ch09).
**Client** — the code that uses a pattern's objects through their interfaces (most chapters).
**Combinatorial explosion** — subclass blow-up when extending a class across multiple dimensions (Ch03, Ch10).
**Command** — behavioral pattern turning a request into a stand-alone object (Ch17).
**Command History** — stack of executed commands enabling undo/redo (Ch17, Ch07).
**Component (Bridge/Composite/Decorator)** — the shared interface for tree nodes or wrappers (Ch11, Ch12); a peer object in Mediator (Ch19).
**Composite** — structural pattern composing objects into trees treated uniformly (Ch11).
**Composition** — one object owns another and controls its lifecycle (filled-diamond) (Ch01, Ch03).
**Concrete Class/Product/Factory/Handler/State/Strategy/Visitor** — a concrete implementation of the corresponding role interface (various).
**Context (State/Strategy)** — object that delegates to the current state or strategy (Ch22, Ch23).
**Context (Flyweight)** — object holding extrinsic state plus a reference to a shared flyweight (Ch14).
**Creational patterns** — patterns about object creation mechanisms (Ch02, Ch04–08).
**Creator** — declares the factory method and holds business logic (Ch04).
**Decorator (Wrapper)** — structural pattern stacking new behavior by wrapping same-interface objects at runtime (Ch12).
**Dependency** — the weakest object relation; a change in one class may affect another that uses it (Ch01).
**Dependency Inversion Principle (DIP)** — depend on abstractions, not concretions; high-level modules shouldn't depend on low-level ones (Ch03).
**Design pattern** — a customizable blueprint for solving a recurring design problem, not copy-paste code (Ch02).
**Director** — defines the order of Builder construction steps (Ch06).
**Double Dispatch** — technique letting an Element pick the correct Visitor method via `accept` (Ch25).
**Encapsulate What Varies** — isolate the parts that change so changes don't ripple (Ch03).
**Encapsulation** — hiding an object's internals behind a public interface (Ch01).
**EventManager** — composed dispatcher helper centralizing Observer subscription logic (Ch21).
**Extensibility** — designing so new behavior can be added with minimal change (Ch03).
**Extrinsic state** — unique, contextual data passed to a flyweight as parameters (Ch14).
**Facade** — structural pattern; a simplified single entry point to a complex subsystem (Ch13).
**Factory Method (Virtual Constructor)** — creational pattern letting subclasses decide which product to instantiate (Ch04).
**Finite-State Machine (FSM)** — model of states + transitions underlying the State pattern (Ch22).
**Flyweight (Cache)** — structural pattern sharing common (intrinsic) state across many objects to save RAM (Ch14).
**Four Pillars of OOP** — Abstraction, Encapsulation, Inheritance, Polymorphism (Ch01).
**GoF (Gang of Four)** — Gamma, Helm, Johnson, Vlissides; 1995 book cataloguing 23 patterns (Ch02).
**God Object** — anti-pattern: one class that knows/does too much (risk in Facade, Mediator) (Ch13, Ch19).
**Handler** — interface declaring `handle`; link in a Chain of Responsibility (Ch16).
**Hook** — an empty optional step in a Template Method providing an extension point (Ch24).
**Idiom** — the lowest-level, language-specific pattern (Ch02).
**Immutability** — flyweights set state once via constructor, no setters (Ch14).
**Implementation (Bridge)** — interface of primitive operations the abstraction delegates to (a.k.a. platform) (Ch10).
**Inheritance** — building a class on another, acquiring its fields and methods (Ch01).
**Interface Segregation Principle (ISP)** — keep interfaces narrow; clients shouldn't depend on methods they don't use (Ch03).
**Intrinsic state** — constant, shareable data stored inside a flyweight (Ch14).
**Invariant / pre-/post-conditions** — the LSP contract a subtype must honor (Ch03).
**Invoker / Sender** — triggers a Command via its reference (Ch17).
**Iterator** — behavioral pattern traversing a collection without exposing its representation (Ch18).
**Lazy initialization** — creating an object only on first use (Ch08, Ch15).
**Leaf** — a Composite node with no children that does real work (Ch11).
**Liskov Substitution Principle (LSP)** — subtypes must be substitutable for their base types (Ch03).
**Mediator (Intermediary, Controller)** — behavioral pattern routing component collaboration through one object (Ch19).
**Memento (Snapshot)** — behavioral pattern saving/restoring object state without breaking encapsulation (Ch20).
**Mental model** — a reusable way of reasoning about a problem (throughout).
**Object** — a concrete instance of a class with state and behavior (Ch01).
**Object adapter** — adapter via composition (works in all languages) (Ch09).
**Object Tree** — alias for Composite structure (Ch11).
**Observer** — behavioral pattern; a subscription mechanism notifying subscribers of publisher events (Ch21).
**Open/Closed Principle (OCP)** — classes open for extension, closed for modification (Ch03).
**Originator** — object whose state a Memento captures and restores (Ch20).
**Polymorphism** — invoking the real subtype's method behind a base-type reference (Ch01).
**Program to an Interface, not an Implementation** — depend on abstractions to stay flexible (Ch03).
**Prototype (Clone)** — creational pattern copying objects without depending on their classes (Ch07).
**Prototype Registry** — catalog of pre-built prototypes to clone by key (Ch07).
**Proxy** — structural pattern; a same-interface placeholder controlling access to a real object (Ch15).
**Proxy types** — virtual (lazy), protection, remote, logging, caching, smart reference (Ch15).
**Publisher / Subject** — the observed object holding state and a subscriber list (Ch21).
**Receiver** — object that performs the real work for a Command (Ch17).
**Refined Abstraction** — a variant of the abstraction's control logic (Ch10).
**Relations with Other Patterns** — the book's recurring section linking each pattern to others (all pattern chapters).
**Single Responsibility Principle (SRP)** — a class should have one reason to change (Ch03).
**Singleton** — creational pattern ensuring one instance with a global access point (Ch08).
**SOLID** — Martin's five principles: SRP, OCP, LSP, ISP, DIP (Ch03).
**State** — behavioral pattern altering behavior when internal state changes (FSM) (Ch22).
**Strategy** — behavioral pattern defining interchangeable algorithms in separate classes (Ch23).
**Structural patterns** — patterns about assembling objects/classes into larger structures (Ch02, Ch09–15).
**Subscriber / Subscription mechanism** — Observer's listener interface and the add/remove machinery (Ch21).
**Telescopic constructor** — anti-pattern of many overloaded constructors; Builder fixes it (Ch06).
**Template method** — the superclass method fixing an algorithm's step order (Ch24).
**Transition** — a predefined switch from one State to another (Ch22).
**Virtual Constructor** — alias for Factory Method (Ch04).
**Visitor** — behavioral pattern separating an algorithm from the object structure it runs on (Ch25).
**Wrapper** — alias for both Adapter and Decorator (Ch09, Ch12).
