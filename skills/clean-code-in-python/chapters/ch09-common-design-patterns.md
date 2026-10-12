# Chapter 9: Common Design Patterns

## Core Idea
Design patterns are discovered, not invented. Let them emerge from refactoring a domain-driven design, and implement them the Pythonic way: some are invisible in Python (iterator, strategy, factory), some are simpler, and some (decorator, composite, state, chain of responsibility) still pay off in full.

## Frameworks Introduced
- **Patterns emerge, they are not forced**: "We should not force the application of a design pattern to the solution we are building, but rather evolve, refactor, and improve our solution until a pattern emerges."
  - When to use: Any design discussion where a pattern name comes up before the problem is understood.
  - How: (1) Model the domain problem and build the right abstractions first. (2) Wait for the rule of three (three or more instances of the same problem) before you generalize. (3) Recognize the pattern that has emerged and use its name to communicate. (4) If a simpler solution works, skip the pattern. Forcing it is over-engineering.
  - Why it works / failure mode: A pattern that emerges fits the real forces in the code, and its name gives the team a shared vocabulary ("strategy" makes everyone picture the same classes). The failure mode is futurology: patterns applied to requirements nobody has yet. That adds indirection and no flexibility.
- **Pythonic pattern triage**: classify each GoF pattern by how Python treats it.
  - When to use: Before porting a pattern from Java/C++ literature.
  - How: **Invisible**, because the language provides it: iterator (`__iter__`/`for`), facade (`os` over `posix`/`nt`, a package's `__init__.py`). **Simpler**: factory (classes and functions are first-class, so a function call is a factory), strategy (pass a function), singleton (use a module-level object). **Still needed, with small adaptations**: decorator, composite, adapter, chain of responsibility, template method, command, state, null object, builder.
  - Why it works / failure mode: Patterns were partly designed to work around static type systems that lack first-class functions. If you copy the canonical version (an `Iterator` class with `has_next()`, a `FactoryFactory`), the result is non-Pythonic boilerplate.
- **Shared state over singleton (monostate)**: Replicate the data across many ordinary instances instead of forcing a single instance.
  - When to use: Several objects must see the same, updatable value (for example, the current Git tag).
  - How: For one attribute, use a class variable behind a property. For reusable or multiple attributes, use a `SharedAttribute` descriptor. To share every attribute, use the Borg pattern: `self.__dict__ = self.__class__._attributes`, ideally through a `SharedAllMixin`.
- **Null object pattern**: Functions and methods must return objects of a consistent type, so callers can rely on polymorphism without extra checks.
  - When to use: A lookup can fail, for example a chain of responsibility with no handler or a user that isn't found.
  - How: Either raise an exception or return a domain-specific empty object (`UnknownUser`) that has the same interface and does nothing. Never return `None`.

## Key Concepts
- **Creational / structural / behavioral patterns**: The three GoF categories (23 patterns in total). They cover object instantiation, composing simpler interfaces into richer objects, and how objects cooperate at runtime.
- **Well-known object**: A unique object created once and reused, such as `None`, `True` or `False`. The author distinguishes it from a singleton class, which returns the same instance however many times you call it.
- **Monostate (SNGMONO)**: Many ordinary instances whose state is transparently synchronized.
- **Borg pattern**: A monostate in which all instances of a class share the same `__dict__`, so every attribute is replicated.
- **Adapter (wrapper)**: Makes an incompatible interface, often one you don't control, conform to the one your code expects.
- **Composite**: A tree of leaves and containers that clients treat uniformly. Containers delegate the request to their children.
- **Decorator pattern**: Objects with the same interface that are chained so that each adds a step to the wrapped object's result. It extends behaviour dynamically without inheritance. It is not the same thing as Python's `@decorator`.
- **Facade**: A single hub in front of many objects. It replaces O(N²) many-to-many connections and hides internals, so they can be refactored freely.
- **Chain of responsibility**: Handlers that each have a `successor`. Each one processes the request if it can and otherwise forwards it. The chain is assembled at runtime.
- **Template method**: A public method in the parent class holds the generic algorithm and calls private hooks that subclasses override.
- **Command**: Separates defining an action from executing it. The object accumulates and modifies parameters until `do()`/`__call__()` runs, as with a SQLAlchemy query or a psycopg2 cursor.
- **State (reification)**: A domain concept that has behaviour becomes an explicit object instead of an enum, string or flag.

## Mental Models
- Think of design patterns as **chess openings**: settled theory you understand deeply once and then reuse to save mental energy. They are building blocks and a shared vocabulary.
- Use **composition rather than inheritance for adapters**. Inheritance is for IS-A specification, and you don't know what else a third-party class brings along.
- Use **state objects when an enum starts to grow behaviour**. Once transitions carry rules, the value needs to be an object.
- Think of a package's **`__init__.py` as a facade**. Clients import from the package root only, which leaves you free to rearrange the files behind it.

## Anti-patterns
- **Singletons**: They are global variables for object-oriented code. They are hard to unit test, any code can modify them at any time, and they produce surprising side effects. If you truly need one, use a module-level object.
- **Base-class Borg dictionary**: If you put `_attributes` on the shared base class, values mix across different subclasses. Each class needs its own dictionary, which the mixin creates lazily.
- **Generic `__getattr__` adapters or delegation**: These are too generic and can have unanticipated side effects, and they hurt readability. Prefer explicit boilerplate, or document the interface with a type annotation, for example `self._state: MergeRequestState`.
- **Generic do-anything null objects or Mocks as null objects**: They lose domain meaning, and because they accept any call they hide a legitimate `AttributeError`.
- **Returning `None` on a miss**: It doesn't describe what happened, and the caller hits `AttributeError: 'NoneType' object has no attribute 'keys'`.
- **Naming classes after patterns** (`EnhancedQueryDecorator`): This breaks intention-revealing naming. Call it `Query` or `EnhancedQuery`. A mention in a docstring is acceptable.
- **Forcing a pattern where a simpler solution works**: This is over-engineering.

## Code Examples
```python
class SharedAttribute:
    def __init__(self, initial_value=None):
        self.value = initial_value
        self._name = None

    def __get__(self, instance, owner):
        if instance is None:
            return self
        if self.value is None:
            raise AttributeError(f"{self._name} was never set")
        return self.value

    def __set__(self, instance, new_value):
        self.value = new_value

    def __set_name__(self, owner, name):
        self._name = name


class GitFetcher:
    current_tag = SharedAttribute()
    current_branch = SharedAttribute()

    def __init__(self, tag, branch=None):
        self.current_tag = tag
        self.current_branch = branch
```
- **What it demonstrates**: A monostate built with a descriptor. It is reusable (DRY), it keeps `GitFetcher` cohesive, and you only need to unit-test the descriptor itself.

```python
class SharedAllMixin:
    def __init__(self, *args, **kwargs):
        try:
            self.__class__._attributes
        except AttributeError:
            self.__class__._attributes = {}
        self.__dict__ = self.__class__._attributes
        super().__init__(*args, **kwargs)

class TagFetcher(SharedAllMixin, BaseFetcher):
    def pull(self):
        logger.info("pulling from tag %s", self.source)
        return f"Tag = {self.source}"
```
- **What it demonstrates**: The Borg pattern abstracted into a mixin. Each class gets its own shared `__dict__`, so values are not mixed across siblings.

```python
class QueryEnhancer:
    def __init__(
        self,
        query: DictQuery,
        *decorators: Iterable[Callable[[Dict[str, str]], Dict[str, str]]]
    ) -> None:
        self._decorated = query
        self._decorators = decorators

    def render(self):
        current_result = self._decorated.render()
        for deco in self._decorators:
            current_result = deco(current_result)
        return current_result

# QueryEnhancer(query, remove_empty, case_insensitive).render()
```
- **What it demonstrates**: The function-based decorator pattern. It keeps the `render()` interface and composes plain dict-transforming functions at runtime. The class-based version, `CaseInsensitive(RemoveEmpty(original))` with each step subclassing `QueryEnhancer`, is the better choice when a step needs data from the decorated object itself.

## Reference Tables
| Pattern | Category | Python treatment |
|---|---|---|
| Factory | Creational | Mostly unnecessary. Classes and functions are first-class, and a function call works as a factory. Use a DI library (pinject) for complex setups. |
| Singleton | Creational | Avoid it. Use a module-level well-known object, or shared state / Borg. |
| Builder | Creational | Language-agnostic. Reserve it for framework or API design consumed by many users. |
| Adapter | Structural | Prefer composition. Use inheritance or mixin adapters only if justified. |
| Composite | Structural | Needed. Give leaves and containers a uniform interface, for example a `price` property. |
| Decorator | Structural | Needed. Use duck typing (no base class required) or a list of functions. |
| Facade | Structural | Often invisible: the `os` module, a package's `__init__.py`. |
| Iterator / Strategy | Behavioral | Invisible or trivial: use `__iter__`, or pass a function. |
| Chain of responsibility | Behavioral | Needed. Runtime-ordered chain of objects. |
| Template method | Behavioral | Needed. A parent's public method calls overridable private hooks. |
| Command | Behavioral | Needed when the command is modified before it executes. Otherwise use a closure or `__call__`. |
| State | Behavioral | Needed when states have behaviour or transitions. |
| Null object | Behavioral | Needed in duck-typed code to keep return types consistent. |

| Shared-state option | Shares | Use when |
|---|---|---|
| Class variable + property | One attribute | A single value must be synced. |
| `SharedAttribute` descriptor | Chosen attributes | A reusable, testable, cohesive solution is needed (rule of three). |
| Borg / `SharedAllMixin` | All attributes | You need it as a rare exception. It is riskier because every attribute replicates. |

## Worked Example
**State pattern for a merge request.** Before: `MergeRequest` holds an enum status. New rules are coming: closing resets approvals, opening sets approvals to 0, merging deletes the source branch, and invalid transitions must be forbidden. Putting all of that in `MergeRequest` would give it too many responsibilities and a lot of `if` statements.

After: an abstract `MergeRequestState(abc.ABC)` declares `open`/`close`/`merge`, and `Open`, `Closed` and `Merged` implement them. `MergeRequest` delegates to its state collaborator through double dispatch:
```python
class Closed(MergeRequestState):
    def open(self):
        logger.info("reopening closed merge request %s", self._merge_request)
        self._merge_request.state = Open
    def close(self):
        """Current state."""
    def merge(self):
        raise InvalidTransitionError("can't merge a closed request")

class MergeRequest:
    def __init__(self, source_branch: str, target_branch: str) -> None:
        self.source_branch = source_branch
        self.target_branch = target_branch
        self._state = None
        self.approvals = 0
        self.state = Open

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state_cls):
        self._state = new_state_cls(self)

    def open(self):
        return self.state.open()
    # close(), merge() likewise
```
Design decisions:
- The `state` setter is the single place where states are created, and it passes `self` to each new state.
- The ABC forces every state to implement the whole interface. An empty method such as `Closed.close` is an explicit no-op, which is clearer than a silent default or an incidental `AttributeError`.
- The link between `MergeRequest` and its state stays 1:1. When the state changes, the old state object is garbage-collected. A weak reference is optional.

Usage: after `mr.merge()`, calling `mr.close()` raises `InvalidTransitionError: already merged request`.

## Key Takeaways
1. Patterns are discovered, not invented. Design for the domain first, apply the rule of three, and then name the pattern that emerges.
2. A pattern's greatest value is its vocabulary. The best implementations are transparent to their users, as the iterator and the `os` facade are.
3. Avoid singletons. Prefer module-level objects, then shared state through a descriptor, and use Borg only as a rare exception.
4. Polymorphism doesn't require inheritance. Duck typing is enough for decorator, composite and adapter, and composition beats inheritance for adapters.
5. A chain of responsibility built from objects can be reordered at runtime, which a version based on `__subclasses__()` cannot do.
6. When behaviour attaches to a value, reify it: replace the enum with state objects.
7. Always return a consistent type. Use a domain null object or raise an exception, never `None`.

## Connects To
- **Ch 2**: The iterator protocol and `__getattr__` are what make some patterns invisible or generic in Python.
- **Ch 3**: The rule of three, DRY and design by contract govern when you abstract and what you return.
- **Ch 4**: Open/closed and Liskov substitution underpin template method and chain of responsibility. DIP and pinject replace factories.
- **Ch 5**: The decorator pattern is distinct from Python's `@decorator` syntax.
- **Ch 6**: `SharedAttribute` is a descriptor that uses `__set_name__`.
- **Ch 8**: The `MergeRequest` enum is refactored here into the state pattern.
- **Ch 10**: Adapters are the mechanism that isolates frameworks and storage in a clean architecture.
- **GoF (Gamma, Helm, Johnson, Vlissides)**: The canonical source of the 23 patterns.
- **Robert C. Martin, "SINGLETON and MONOSTATE"** and **Bobby Woolf, "The Null Object Pattern"**: The primary references for these two ideas.
