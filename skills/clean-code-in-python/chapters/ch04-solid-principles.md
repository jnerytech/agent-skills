# Chapter 4: The SOLID Principles

## Core Idea
SOLID (Single responsibility, Open/closed, Liskov's substitution, Interface segregation, Dependency inversion) gives proven guidelines for object-oriented designs that are extensible and flexible enough to change. The goal is not to get every requirement right in version one but to keep the design adaptable as requirements evolve.

## Frameworks Introduced
- **Single responsibility principle (SRP)**: a software component (in general, a class) must have only one responsibility, and therefore **only one reason to change**.
  - When to use: whenever a class groups mutually exclusive, unrelated methods, or must change for several different domain reasons.
  - How: (1) list the reasons the class might change; each reason is a responsibility; (2) look for partitions in attributes/methods (methods that don't use the same attributes); (3) extract each into its own cohesive class; (4) recompose them as collaborators. A class can still have several methods if they serve the same logic. If the boundaries are unclear, write a monolithic class first to discover the internal collaborations, then split.
  - Why it works / failure mode: changes become local and classes become reusable (e.g., `ActivityWatcher` reused elsewhere without carrying `stream_events()`). Fails when misread as "one method per class".
- **Open/closed principle (OCP)**: a module should be **open to extension but closed to modification** — when something new appears in the domain problem, only add new code, don't change existing code.
  - When to use: a method with a growing `if/elif` chain over concrete types, or any place where new domain variants keep arriving.
  - How: (1) make the client interact with an abstraction instead of concrete classes; (2) move the per-type logic into a polymorphic method on each type (`meets_condition`); (3) have the client iterate over the types generically (`__subclasses__()`, the `abc` registry, or a custom registry); (4) new variant = new subclass, zero changes to the client.
  - Why it works / failure mode: avoids ripple effects; relies on effective polymorphism. Fails because perfect closure is not always possible — some abstractions collide; choose the closure that protects against the requirements most likely to need extension.
- **Liskov's substitution principle (LSP)**: if S is a subtype of T, then objects of type T may be replaced by objects of type S without breaking the program — clients must use any subtype indistinguishably.
  - When to use: every time you subclass or implement an interface; in code review of overridden methods.
  - How: (1) keep signatures identical (parameter types, number of parameters, return type); (2) let mypy and pylint catch blatant violations and never silence them; (3) review contracts manually: a subclass can **never make preconditions stricter** and **never make postconditions weaker** than the parent.
- **Interface segregation principle (ISP)**: when an interface provides multiple methods, break it into multiple smaller ones, each with a specific and accurate scope (preferably one method).
  - When to use: an ABC whose implementers must stub out methods they don't need.
  - How: split disjoint capabilities into separate ABCs; let a concrete class implement several via multiple inheritance. Size by cohesion — "do one thing", not "one method" (`__enter__`/`__exit__` must stay together).
- **Dependency inversion principle (DIP)**: abstractions must not depend on details; details (concrete implementations) must depend on abstractions. Force the volatile detail to adapt to your code via an API, not the reverse.
  - When to use: high-level code depending on something fragile, volatile, or out of your control (external library, another team's module, an I/O target).
  - How: (1) identify the message the high-level class actually needs (`.send()`); (2) define an ABC for it (`DataTargetClient`); (3) make low-level classes extend it (`Syslog`); (4) inject the dependency through `__init__` (**dependency injection**); (5) for complex graphs, declare bindings and let a tool (e.g. `pinject`) build objects.

## Key Concepts
- **God object**: a class with multiple, mostly unrelated responsibilities; knows more than it should.
- **Reason to change**: the SRP's unit of responsibility — one domain change should affect one class.
- **Closure**: the property that a piece of code is protected from modification against a given kind of change (e.g., new event types).
- **Null object pattern**: returning a typed default object (`UnknownEvent`) instead of `None` to preserve polymorphism.
- **Duck typing**: an object is defined by the methods it has ("walks like a duck, quacks like a duck").
- **Abstract base class (PEP-3119)**: `abc` construct that defines an interface; `@abstractmethod` forces derived classes to implement methods.
- **Virtual subclass**: a type registered into an ABC hierarchy via `abc` — "...or it says it is a duck".
- **Dependency injection**: providing a dependency dynamically (through `__init__`) instead of creating it internally.
- **Binding specification**: in `pinject`, an object whose `provide_<dependency>` methods return the dependency with that name.

## Mental Models
- Think of SRP as **normalization in relational databases**: partitions in an object's attributes/methods signal two abstractions mixed into one.
- Use the **"does X have to change because Y changed?" test**: does a system monitor have to change because we changed the data representation? No — so that's a separate responsibility.
- Think of **LSP as DbC applied to hierarchies**: the parent class defines the contract; subclasses inherit the obligation to honor it. LSP contributes to OCP — an incompatible subclass can only be added by modifying the closed client.
- Place **abstractions at flexibility points**: concrete implementations change far more often than interfaces, so put interfaces where you expect the system to change.

## Anti-patterns
- **God objects / `SystemMonitor` with `load_activity`, `identify_events`, `stream_events`**: orthogonal actions in one class make it rigid, fragile, error-prone.
- **Monolithic type-dispatch method** (`if ... elif ...` returning concrete event classes): grows unbounded, not closed for modification.
- **Silencing tool errors** with `# type: ignore` or disabling pylint's `arguments-differ`: tools are reporting a real design flaw — refactor.
- **Subclass demanding extra input keys** (`event_data["before"]["session"]` when the contract only guarantees `"before"`/`"after"`): strengthens preconditions, raises `KeyError` for clients.
- **Fat interfaces** (`from_xml` + `from_json` in one ABC): forces implementers to carry unneeded methods; also breaks SRP.
- **Over-segregation**: splitting methods that must go together (context manager's `__enter__`/`__exit__`) produces a broken, dangerous component.
- **Creating dependencies in `__init__`** (`self._target = Syslog()`): rigid, hard to test (requires patching), carries creation side effects.

## Code Examples
```python
class Event:
    def __init__(self, raw_data):
        self.raw_data = raw_data

    @staticmethod
    def meets_condition(event_data: dict) -> bool:
        return False


class UnknownEvent(Event):
    """A type of event that cannot be identified from its data"""


class LoginEvent(Event):
    @staticmethod
    def meets_condition(event_data: dict):
        return (
            event_data["before"]["session"] == 0
            and event_data["after"]["session"] == 1
        )


class SystemMonitor:
    """Identify events that occurred in the system."""

    def __init__(self, event_data):
        self.event_data = event_data

    def identify_event(self):
        for event_cls in Event.__subclasses__():
            try:
                if event_cls.meets_condition(self.event_data):
                    return event_cls(self.event_data)
            except KeyError:
                continue
        return UnknownEvent(self.event_data)


class TransactionEvent(Event):
    """Represents a transaction that has just occurred on the system."""

    @staticmethod
    def meets_condition(event_data: dict):
        return event_data["after"].get("transaction") is not None
```
- **What it demonstrates**: OCP — `identify_event` is closed; adding `TransactionEvent` required only a new class.

```python
from abc import ABCMeta, abstractmethod

class XMLEventParser(metaclass=ABCMeta):
    @abstractmethod
    def from_xml(xml_data: str):
        """Parse an event from a source in XML representation."""

class JSONEventParser(metaclass=ABCMeta):
    @abstractmethod
    def from_json(json_data: str):
        """Parse an event from a source in JSON format."""

class EventParser(XMLEventParser, JSONEventParser):
    def from_xml(xml_data):
        pass

    def from_json(json_data: str):
        pass
```
- **What it demonstrates**: ISP — segregated interfaces composed via multiple inheritance; omitting an abstract method raises `TypeError: Can't instantiate abstract class ...`.

```python
class EventStreamer:
    def __init__(self, target: DataTargetClient):
        self._target = target

    def stream(self, events: list[Event]) -> None:
        for event in events:
            self._target.send(event.serialise())
```
- **What it demonstrates**: DIP + dependency injection — any `DataTargetClient` (or a test double) can be passed in.

## Reference Tables

| LSP violation | Example | Detected by |
|---|---|---|
| Different parameter type | `meets_condition(self, event_data: list)` vs `dict` | mypy: `Argument 1 of "meets_condition" incompatible with supertype "Event"` |
| Different return type | returns non-`bool` | mypy |
| Different signature (extra param) | `meets_condition(self, event_data: dict, override: bool)` | pylint: `Parameters differ from overridden 'meets_condition' method (arguments-differ)` |
| Stricter precondition / weaker postcondition | subclass requires `"session"` key | Code review only |

| Principle | Smell it fixes | Mechanism |
|---|---|---|
| SRP | Many reasons to change | Split into cohesive collaborators |
| OCP | Editing existing code for each new variant | Polymorphism over an abstraction |
| LSP | Subtypes not interchangeable | Preserve signatures and contracts |
| ISP | Implementers stubbing unneeded methods | Small, cohesive ABCs |
| DIP | High-level code tied to a volatile detail | Interface + injection |

## Worked Example
**Events system evolving through the principles.**
1. *SRP*: `SystemMonitor` loads, parses, and streams — three reasons to change. Split into `ActivityWatcher` (load), `SystemMonitor` (identify), and an output/streamer class, collaborating through contracts.
2. *OCP*: the first `identify_event` hardcodes `if before.session == 0 and after.session == 1: LoginEvent ... elif ...: LogoutEvent ... else UnknownEvent`. Refactor: each `Event` subclass gets a static `meets_condition(event_data)`; the monitor loops over `Event.__subclasses__()`. Adding `TransactionEvent` touches nothing else — `SystemMonitor({"after": {"transaction": "Tx001"}})` → `TransactionEvent`.
3. *LSP*: add a precondition `Event.validate_precondition(event_data)` — must be a `Mapping` with `"before"` and `"after"` keys whose values are `Mapping`s, else `ValueError`. The monitor validates once, then uses `next((cls for cls in Event.__subclasses__() if cls.meets_condition(...)), UnknownEvent)` and no longer needs to know about `KeyError`. `LoginEvent`/`LogoutEvent` violated LSP by requiring `"session"` (stricter precondition); fixing `["session"]` → `.get("session")` restores substitutability, so `{"before": {}, "after": {"transaction": "Tx001"}}` works.
4. *ISP*: event parsing split into `XMLEventParser` and `JSONEventParser`.
5. *DIP*: `EventStreamer` stops depending on `Syslog`; it depends on `DataTargetClient.send()`, injected via `__init__`. Optionally wire with `pinject`: a `_EventStreamerBindingSpec` with `provide_target(self): return Syslog()`, then `object_graph.provide(EventStreamer)`.

## Key Takeaways
1. One class, one reason to change; the smaller and more cohesive the class, the better — but not one method per class.
2. Design toward abstractions so new domain variants mean new code, not modified code; choose closure strategically.
3. Subclasses must be substitutable: same signatures, no stricter preconditions, no weaker postconditions. Never silence mypy/pylint on these.
4. Keep interfaces small in terms of cohesion; methods that must work together stay together.
5. Depend on interfaces you own; inject dependencies via `__init__` rather than creating them. Declaring the ABC is optional in Python but improves readability ("Syslog *is a* DataTargetClient").
6. The principles reinforce each other: LSP enables OCP, DIP yields OCP, ISP violations cause SRP violations.
7. Don't aim to get the principles right in the first design; aim for a design that can evolve toward a stable one.

## Connects To
- **Ch 1**: mypy and pylint detect LSP violations automatically.
- **Ch 2**: Pythonic code and the Unix philosophy behind cohesive objects.
- **Ch 3**: SRP extends cohesion/separation of concerns; LSP extends DbC; exceptions weaken encapsulation (why moving `KeyError` out of the client helps).
- **Ch 5**: decorators applied with these principles in mind.
- **Ch 8**: dependency injection makes classes testable with test doubles.
- **Ch 9**: null object pattern (`UnknownEvent`), dependency inversion behind several design patterns.
- **Ch 10**: dependency inversion as a cornerstone of clean architecture.
- **Barbara Liskov, "Data Abstraction and Hierarchy"**: original formulation of LSP.
- **PEP-3119**: abstract base classes, the Python vehicle for ISP and DIP.
