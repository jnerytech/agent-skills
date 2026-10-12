# Chapter 6: Getting More Out of Our Objects with Descriptors

## Core Idea
A descriptor is an object, placed as a **class attribute**, whose class implements part of the descriptor protocol (`__get__`, `__set__`, `__delete__`, `__set_name__`). Attribute access on instances then runs that logic instead of returning the object itself. Use descriptors to build generic, reusable attribute behavior for libraries, frameworks and internal APIs, not to hold business logic.

## Frameworks Introduced
- **Descriptor protocol (ClientClass / DescriptorClass)**: `ClientClass` (domain abstraction) holds `descriptor = DescriptorClass()` as a class attribute, and `client = ClientClass()`. Accessing `client.descriptor` calls `DescriptorClass.__get__` instead of returning the descriptor.
  - When to use: when the same property-like logic (validation, tracing, transformation) would otherwise be repeated across attributes or classes.
  - How: (1) write a class with only the protocol methods you need; (2) capture the attribute name in `__set_name__`; (3) store per-instance data in `instance.__dict__[self._name]`; (4) in `__get__`, `if instance is None: return self`; (5) assign it in the class body, never in `__init__`.
  - **Why it works / failure mode**: attribute lookup checks for descriptors on the class. If the descriptor is created as an instance attribute, the protocol never fires. Storing data on the descriptor itself (`self.value`) shares it across *all* instances, because the class attribute is a single object.
- **Data vs. non-data descriptors (precedence rule)**: a descriptor that implements `__set__` or `__delete__` is a **data descriptor** and always takes precedence over the instance `__dict__`. One that implements only `__get__` is a **non-data descriptor**, and the instance `__dict__` wins if it has a key with the same name. `__set_name__` doesn't affect this classification.
  - When to use: use non-data descriptors for computed/read-only behavior that may be shadowed, such as functions and methods. Use data descriptors when every assignment must go through your logic.
  - **Why it works / failure mode**: with a non-data descriptor, `client.descriptor = 43` writes into `__dict__` and silently hides the descriptor until `del`. With a data descriptor, `del client.descriptor` raises `AttributeError: __delete__` unless `__delete__` is implemented.
- **Storage strategy: instance `__dict__` (preferred) vs. `WeakKeyDictionary`**: "Always store and return the data from the `__dict__` attribute of the instance." The alternative is a `weakref.WeakKeyDictionary` mapping on the descriptor.
  - Trade-offs of `WeakKeyDictionary`: the object no longer holds its own attributes (`vars(client)` is incomplete), and instances must be hashable (which may force custom `__hash__`/`__eq__`). A plain dict of instances creates circular references, which leak memory.
- **Universal decorator recipe**: implement the decorator as a class and add `__get__` that returns `types.MethodType(self, instance)` (or a rebound copy), so it works on both functions and methods.

## Key Concepts
- **`__get__(self, instance, owner)`**: called on read. `instance` is `None` when accessed from the class, which is why `owner` is passed separately.
- **`__set__(self, instance, value)`**: called on assignment (`client.descriptor = "value"`). It's the generic form of `@property.setter`.
- **`__delete__(self, instance)`**: called on `del client.descriptor`. It's rarely needed.
- **`__set_name__(self, owner, name)` (3.6+)**: receives the attribute name, so you don't repeat it (`DescriptorWithName("descriptor")`). Keep an `__init__` default for flexibility, since `__init__` can override it.
- **Shared state issue**: class attributes are shared by every instance, so data stored on the descriptor leaks across objects. That's only desirable for Borg-like sharing.
- **Infinite recursion trap**: calling `setattr(instance, name, value)` inside `__set__` re-triggers `__set__`. Write to `instance.__dict__` directly.
- **Functions are non-data descriptors**: `function.__get__` binds the function to the instance and produces a method. `instance.method(...)` ≡ `MyClass.method(instance, ...)`.
- **Built-in descriptors**: `@property`, `@classmethod`, `@staticmethod`, and `__slots__` (one descriptor per slot, no `__dict__`, less memory, no dynamic attributes, can't mix class-attribute defaults).
- **Property**: a particular case of a descriptor implementing the full protocol. Descriptors are the more generic mechanism.

## Mental Models
- Think of a descriptor as **a reusable property**: whenever you'd copy-paste the same `@property`/`.setter` logic, it's a descriptor candidate (after the rule of three).
- Think of descriptors as **implementation logic, not business logic**. They're closer to defining a new data structure or tool that business code consumes. A good descriptor knows nothing about `Traveler` or `LoginEvent`.
- Use **"what would Python do?"** as the quality bar. A good descriptor behaves like `property`, functions or `classmethod`: it returns itself when accessed from the class (unless, like `classproperty`, you need `owner`).
- Treat descriptors as **ordinary objects**. Apply OOP to them (base classes, Template Method, `functools.partial` to stamp out variants, OCP), but respect LSP and ISP.

## Anti-patterns
- **Descriptor as an instance attribute** (set in `__init__`): the protocol never runs.
- **Storing values on the descriptor** (`self.value = value`): every instance sees the last write.
- **`setattr`/assignment to the same attribute inside `__set__`**: infinite recursion.
- **Descriptor keeping strong references to clients**: circular dependencies are never garbage-collected, which leaks memory.
- **Assigning to a non-data descriptor attribute by accident**: it silently shadows the descriptor.
- **Implementing more protocol methods than needed**: a large interface goes against ISP. Most needs are met by `__get__` alone.
- **A subclass adding `__set__` to a `__get__`-only base descriptor**: it enhances the interface beyond the parent, which violates LSP.
- **Business logic in descriptors, or descriptors with no proven repetition**: complexity that doesn't pay off.
- **Forcing precise type annotations**: this causes circular imports, and if exact types are known, the descriptor is probably not generic enough. Write good docstrings instead.
- **Non-identifier descriptor names**: the name becomes a `__dict__` key read as an attribute, so use a valid Python identifier.
- **`__slots__` on objects that need dynamism**: it removes `__dict__`, so `vars()` raises `TypeError` and adding attributes raises `AttributeError`.

## Code Examples
```python
class Validation:
    def __init__(
        self, validation_function: Callable[[Any], bool], error_msg: str
    ) -> None:
        self.validation_function = validation_function
        self.error_msg = error_msg

    def __call__(self, value):
        if not self.validation_function(value):
            raise ValueError(f"{value!r} {self.error_msg}")

class Field:
    def __init__(self, *validations):
        self._name = None
        self.validations = validations

    def __set_name__(self, owner, name):
        self._name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__[self._name]

    def validate(self, value):
        for validation in self.validations:
            validation(value)

    def __set__(self, instance, value):
        self.validate(value)
        instance.__dict__[self._name] = value

class ClientClass:
    descriptor = Field(
        Validation(lambda x: isinstance(x, (int, float)), "is not a number"),
        Validation(lambda x: x >= 0, "is not >= 0"),
    )
```
- **What it demonstrates**: the canonical data-descriptor idiom (`__set_name__` + `__dict__` storage + `instance is None` guard) used as a reusable validating setter.

```python
class BaseFieldTransformation:
    def __init__(self, transformation: Callable[[], str]) -> None:
        self._name = None
        self.transformation = transformation

    def __get__(self, instance, owner):
        if instance is None:
            return self
        raw_value = instance.__dict__[self._name]
        return self.transformation(raw_value)

    def __set_name__(self, owner, name):
        self._name = name

    def __set__(self, instance, value):
        instance.__dict__[self._name] = value

ShowOriginal = partial(BaseFieldTransformation, transformation=lambda x: x)
HideField = partial(
    BaseFieldTransformation, transformation=lambda x: "**redacted**"
)
FormatTime = partial(
    BaseFieldTransformation,
    transformation=lambda ft: ft.strftime("%Y-%m-%d %H:%M"),
)

class LoginEvent(BaseEvent):
    username = ShowOriginal()
    password = HideField()
    ip = ShowOriginal()
    timestamp = FormatTime()
```
- **What it demonstrates**: descriptors replacing the Ch 5 `@Serialization` class decorator. `partial` simulates subclasses, and adding a transformation never touches the base class (OCP). Raw values stay in `__dict__`, and reads return the transformed value.

```python
class classproperty:
    def __init__(self, fget):
        self.fget = fget

    def __get__(self, instance, owner):
        return self.fget(owner)
```
- **What it demonstrates**: a descriptor-based decorator that deliberately uses `owner` (`instance` is expected to be `None`), so `TableEvent.topic` and `TableEvent().topic` both work.

## Reference Tables
| Name | Meaning (Table 6.1) |
|---|---|
| `ClientClass` | Domain abstraction that uses the descriptor; holds it as a class attribute |
| `DescriptorClass` | Class implementing the descriptor protocol methods |
| `client` | Instance of `ClientClass` |
| `descriptor` | Instance of `DescriptorClass`, a class attribute of `ClientClass` |

| | Non-data descriptor | Data descriptor |
|---|---|---|
| Implements | `__get__` only | `__set__` and/or `__delete__` |
| Precedence vs instance `__dict__` | `__dict__` wins | Descriptor always wins |
| `obj.attr = x` | Writes `__dict__`, shadows descriptor | Calls `__set__` |
| `del obj.attr` | Removes `__dict__` key, descriptor reappears | Calls `__delete__` (else `AttributeError`) |
| Examples | functions/methods | `property`, slots |

| Storage | Pros | Cons |
|---|---|---|
| `instance.__dict__[name]` (preferred) | Object owns its data; `vars()` complete; common idiom | Needs the attribute name (`__set_name__`) |
| `WeakKeyDictionary` on descriptor | No `__dict__` access needed | Data not on object; instances must be hashable |
| `self.value` on descriptor | (none, unless Borg) | Shared across all instances |

## Worked Example
**Tracking every city a `Traveler` visits.**
*Before*: a `current_city` property whose setter appends to `_cities_visited` when the value changes, plus a `cities_visited` property. This is fine for one attribute, but tickets, countries, or other classes would each repeat the logic. A `__setattr__` mixin would couple the hierarchy, as discussed in Ch 5.

*After*: a generic `HistoryTracedAttribute(trace_attribute_name)` data descriptor:
- `__set_name__` stores `_name` (the traced attribute, `current_city`).
- `__set__` calls `_track_change_in_value_for_instance`, which first calls `_set_default`: `instance.__dict__.setdefault(self.trace_attribute_name, [])` creates the tracer list on first use.
- `_needs_to_track_change` returns `True` on `KeyError` (first assignment in `__init__`), otherwise `value != current_value`. On a change, it appends to the tracer list, then writes `instance.__dict__[self._name] = value`.
- The client class shrinks to:
```python
class Traveler:
    current_city = HistoryTracedAttribute("cities_visited")

    def __init__(self, name: str, current_city: str) -> None:
        self.name = name
        self.current_city = current_city
```
The descriptor's complexity is justified only by repeated use. It contains no domain terms, so it can be applied to any class or project. Caveat: don't build one until the repetition is real.

## Key Takeaways
1. Descriptors must be class attributes. Keep per-instance data in `instance.__dict__`, keyed by the name from `__set_name__`.
2. Know data vs. non-data precedence: `__set__`/`__delete__` make the descriptor override the instance dictionary.
3. In `__get__`, return `self` when `instance is None`, unless you deliberately need `owner`.
4. Never call `setattr` on the same attribute inside `__set__`, and avoid strong back-references (memory leaks).
5. Implement the minimum protocol (usually just `__get__`). Apply ISP, LSP and OCP to descriptors like any other object.
6. Make decorators that must work on methods into classes that implement `__get__` with `types.MethodType`.
7. Reserve descriptors for generic, reusable implementation logic (libraries, frameworks, internal APIs), not business rules. Prefer docstrings over complicated type annotations.

## Connects To
- **Ch 2**: `@property`, `__getattr__`/`__setattr__`, `__dict__`, dataclasses. Descriptors generalize properties.
- **Ch 3**: DRY and the rule of three for reusable components.
- **Ch 4**: ISP (small descriptor interface), LSP (don't add `__set__` in a subclass), OCP (new transformation = new partial/subclass).
- **Ch 5**: fixes the method-decorator `self`-shift bug and offers a more compact alternative to the `@Serialization` class decorator.
- **Ch 9**: Borg pattern (intentional shared state) and Template Method for descriptor hierarchies.
- **External**: Python Descriptor HowTo Guide; the data-model docs on "implementing descriptors"; `weakref.WeakKeyDictionary`; `types.MethodType`; `__slots__`; metaprogramming and metaclasses (which descriptors and class decorators make unnecessary).
