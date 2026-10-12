# Patterns Catalog — 23 GoF Patterns

Each: **When to use** / **How** / **Trade-offs**. Grouped by intent. Full detail in chapter files.

---

## Creational — object creation

## Factory Method (Ch04)
**When to use**: you don't know up front the exact object types your code needs; you want to let users extend a framework's components; you want to reuse existing objects instead of rebuilding.
**How**: declare a factory method in the creator that returns the product interface; subclasses override it to return different concrete products. Creator's business logic uses products only via the interface.
**Trade-offs**: + decouples creator from concrete products, honors OCP/SRP. − can balloon subclass count.

## Abstract Factory (Ch05)
**When to use**: code must work with multiple families of related products without depending on their concrete classes.
**How**: declare interfaces per product type; one factory interface with a creation method per product; each concrete factory builds one variant family; client uses abstract interfaces only.
**Trade-offs**: + guarantees compatible product families, isolates concretes. − many new interfaces/classes.

## Builder (Ch06)
**When to use**: get rid of a telescopic constructor; build different representations of a product; construct complex/Composite trees step by step.
**How**: extract construction steps into a Builder interface; concrete builders implement them; an optional Director defines step order; client fetches the result from the builder.
**Trade-offs**: + step-by-step control, reuse construction code. − more moving parts.

## Prototype / Clone (Ch07)
**When to use**: your code shouldn't depend on the concrete classes of objects you copy; reduce subclasses that differ only in initialization.
**How**: declare a `clone` method on a prototype interface; each class clones itself (incl. private fields); optionally keep a Prototype Registry of ready-made copies.
**Trade-offs**: + clone without coupling, alternative to subclassing. − cloning objects with circular refs is tricky.

## Singleton (Ch08)
**When to use**: exactly one instance must be shared by all clients (e.g. one DB connection); you need stricter control than a global variable.
**How**: private constructor + static `getInstance()` that creates the instance once (lazy) and caches it.
**Trade-offs**: + controlled single access. − violates SRP, hides dependencies, hard to unit-test, needs care under multithreading.

---

## Structural — assembling objects

## Adapter / Wrapper (Ch09)
**When to use**: reuse an existing class whose interface is incompatible with your code.
**How**: object adapter wraps the service via composition and translates calls; class adapter inherits both (where multiple inheritance exists).
**Trade-offs**: + reuse legacy/3rd-party code, SRP/OCP. − adds another layer of indirection.

## Bridge (Ch10)
**When to use**: a monolithic class has variants on two independent dimensions; you want to switch implementations at runtime.
**How**: split into Abstraction (control) and Implementation (platform) hierarchies; abstraction holds a reference to an implementation and delegates.
**Trade-offs**: + extend dimensions independently, hide platform details. − adds complexity to simple classes.

## Composite / Object Tree (Ch11)
**When to use**: the core model is tree-like and clients should treat leaves and containers uniformly.
**How**: a Component interface; Leaf does the work; Composite holds children and delegates/aggregates results recursively.
**Trade-offs**: + work with complex trees easily, OCP. − overly general interface can become hard to design.

## Decorator / Wrapper (Ch12)
**When to use**: add/remove behavior at runtime without breaking client code, or when inheritance is awkward (e.g. `final` classes).
**How**: a base decorator holds a same-interface wrappee and delegates; concrete decorators add behavior before/after delegating; stack wrappers.
**Trade-offs**: + combine behaviors at runtime, avoid subclass explosion. − hard to remove a specific wrapper; stack order matters.

## Facade (Ch13)
**When to use**: you need a simple, limited interface to a complex subsystem; or want to layer a subsystem.
**How**: a facade class exposes a few high-level methods and forwards to the subsystem; add a second facade if one grows into a god object.
**Trade-offs**: + isolates code from subsystem complexity. − the facade can become a god object coupled to everything.

## Flyweight / Cache (Ch14)
**When to use**: a huge number of similar objects barely fit in RAM and share duplicable state.
**How**: split state into intrinsic (shared, stored in immutable flyweights) and extrinsic (passed in by contexts); a Flyweight Factory pools and reuses flyweights.
**Trade-offs**: + big RAM savings. − trades RAM for CPU; code gets more complex; flyweights must be immutable.

## Proxy (Ch15)
**When to use**: lazy initialization (virtual), access control (protection), remote execution, logging, caching, or smart-reference cleanup.
**How**: proxy implements the same service interface, holds a reference to the real service, runs logic before/after delegating.
**Trade-offs**: + control the service transparently, works without client changes. − adds indirection; can delay responses.

---

## Behavioral — communication & responsibility

## Chain of Responsibility (Ch16)
**When to use**: multiple handlers may process a request, the set/order is decided at runtime, or handlers must run in sequence.
**How**: handlers share an interface and a `next` link; each either handles the request or forwards it; client builds the chain and triggers any link.
**Trade-offs**: + decouples sender from receivers, OCP. − a request may go unhandled if the chain is misbuilt.

## Command / Action / Transaction (Ch17)
**When to use**: parametrize objects with operations, queue/schedule/log requests, support undo/redo.
**How**: wrap a request in a command object with `execute()` that delegates to a receiver; the invoker triggers it; keep a history stack for undo.
**Trade-offs**: + decouples invoker from receiver, enables undo/queues, SRP/OCP. − more classes per operation.

## Iterator (Ch18)
**When to use**: traverse a complex/hidden collection, remove duplicate traversal code, or traverse different structures uniformly.
**How**: an iterator object holds traversal state and exposes `hasMore`/`getNext`; the collection exposes a factory method returning iterators.
**Trade-offs**: + clean traversal, multiple parallel traversals, SRP/OCP. − overkill for simple collections.

## Mediator / Intermediary / Controller (Ch19)
**When to use**: components are tightly coupled and hard to reuse/change because they reference each other directly.
**How**: components talk only to a mediator via `notify(sender, event)`; the concrete mediator encodes the relationships and coordinates peers.
**Trade-offs**: + decouples components, centralizes control, OCP. − the mediator can grow into a god object.

## Memento / Snapshot (Ch20)
**When to use**: capture and restore prior state (undo, rollback) without exposing the object's internals.
**How**: originator produces an immutable memento of its state; a caretaker stores mementos (e.g. a stack) but cannot read them; originator restores from one.
**Trade-offs**: + preserves encapsulation while snapshotting. − can use lots of RAM; caretakers must manage lifecycle.

## Observer (Ch21)
**When to use**: changes to one object must notify an unknown/dynamic set of others; objects subscribe for a limited time.
**How**: publisher keeps a subscriber list and a subscription mechanism (add/remove); on an event it calls each subscriber's `update`.
**Trade-offs**: + OCP, runtime subscribe/unsubscribe. − subscribers notified in unpredictable order.

## State (Ch22)
**When to use**: behavior depends on state, there are many states, and state-specific code changes often; class is full of field-based conditionals.
**How**: extract each state into a class implementing a state interface; context delegates to the current state; states may trigger transitions via a backreference.
**Trade-offs**: + organizes state code, removes big conditionals, SRP/OCP. − overkill for few rarely-changing states.

## Strategy (Ch23)
**When to use**: you need interchangeable variants of an algorithm switchable at runtime; isolate algorithm details; replace a big algorithm-picking conditional.
**How**: define a strategy interface; each algorithm is a concrete strategy; context holds and delegates to a strategy, swappable via setter.
**Trade-offs**: + swap algorithms at runtime, isolate logic, OCP. − client must know the strategies; overhead for few stable algorithms.

## Template Method (Ch24)
**When to use**: several classes share an algorithm differing only in some steps; clients should extend particular steps, not the structure.
**How**: a superclass template method fixes the step order; subclasses override abstract/optional steps and hooks.
**Trade-offs**: + reuse common structure, control extension points. − limited by the skeleton; inheritance-based (less flexible than Strategy).

## Visitor (Ch25)
**When to use**: run an operation across all elements of a complex/object structure; keep auxiliary behavior out of the element classes; behavior only fits some classes of a hierarchy.
**How**: elements expose `accept(visitor)`; visitors declare one `visit` method per element type; double dispatch routes to the right method.
**Trade-offs**: + add new operations without touching elements, OCP/SRP. − must update all visitors when a new element class appears; may break element encapsulation.
