# Chapter 2: Pythonic Code

## Core Idea
Idioms are coded, language-specific ways to perform a task, and following Python's idioms ("Pythonic" code) makes code more compact, often faster, and familiar to every Python reader. The core of Pythonic code is to implement Python's protocols through magic methods so your objects work naturally with `[]`, `with`, `for`, `in`, attribute access, and calls, while avoiding the language's known caveats.

## Frameworks Introduced
- **Protocols via magic methods (Table 2.1)**: Make your objects blend with Python syntax by implementing the matching dunder methods. Declare the class against an ABC from `collections.abc` (`Sequence`, `Container`, etc.).
  - When to use: Any domain object that behaves like a container, resource, iterable, or function.
  - How: (1) Pick the protocol that matches the behavior you want (see the table below). (2) Inherit from the `collections.abc` interface. This reveals intent, forces you to implement the required methods, and makes `isinstance()` work. (3) If you wrap a built-in object, delegate to it (composition) so the behavior stays compatible.
  - **Why it works / failure mode**: Readers already know the semantics of `in`, `with`, and slicing, so the code declares the problem instead of describing the mechanics (`coord in self.limits`). Failure mode: breaking the expected semantics, such as a slice that returns the wrong type, an end-inclusive range, or `__getattr__` raising something other than `AttributeError`. Users then hit surprising bugs.
- **Context managers (PEP-343)**: Use them for code that has preconditions and postconditions, such as resource management or any before/after invariant. `__enter__` runs first, and its return value is bound by `as`. `__exit__(exc_type, ex_value, ex_traceback)` always runs, even when an exception occurs.
  - When to use: Files, connections, sockets, temp files, and also to separate concerns such as "stop the DB, back up, always restart".
  - How, choosing an implementation:
    1. Use a class with `__enter__`/`__exit__` when the context needs state or belongs to an object.
    2. Use `@contextlib.contextmanager` on a generator function when the context doesn't belong to any object. Everything before `yield` is enter logic, and everything after it (put it in `finally`) is exit logic. This avoids a "fake" class.
    3. Subclass `contextlib.ContextDecorator` to apply the context as a decorator (`@dbhandler_decorator()`) and reuse the invariant logic across many functions. Its downside is that the decorated function can't access the context object.
    4. Use `contextlib.suppress(Exc)` to state explicitly that an exception is safe to ignore.
  - **Why it works / failure mode**: Cleanup is guaranteed without try/finally noise, and the main logic stays isolated. Failure mode: returning `True` from `__exit__` swallows the exception, and "errors should never pass silently".
- **Iterable vs. sequence choice**: You can make an object iterable through `__iter__`/`__next__` (the iterator protocol). As a fallback, `iter()` also accepts a sequence that implements `__len__` + `__getitem__` with indexes starting at 0. Otherwise it raises `TypeError`.
  - How: Choose based on the memory vs. CPU trade-off. An iterable holds one item at a time but takes O(n) to reach the nth element. A sequence holds everything but indexes in O(1). In general, prefer iteration, and generators even more.

## Key Concepts
- **Idiom**: A coded, language-dependent way of doing a task. It differs from design patterns, which are high-level and language-independent.
- **`slice`**: The built-in object behind `seq[start:stop:step]`. Missing parts are `None`, and the end is excluded.
- **Sequence**: An object implementing `__getitem__` and `__len__` (list, tuple, str).
- **Container**: An object implementing `__contains__`, which backs the `in` operator.
- **Container iterable**: An iterable whose `__iter__` creates a new generator on every call, so it can be iterated repeatedly.
- **Name mangling**: A leading `__attr` becomes `_<ClassName>__attr`. It exists to avoid name collisions in heavily extended classes, not to make attributes private.
- **Property**: `@property` (a query) and `@<name>.setter` (a command) wrap get/set logic, for example validation, behind attribute syntax.
- **Command and query separation (CC08)**: A method should either answer something or do something, never both.
- **Assignment expression (PEP-572, `:=`)**: Binds a temporary name inside an expression, for example within a comprehension, to avoid repeated calls.
- **Dataclass (PEP-557)**: `@dataclass` generates `__init__` from annotated class attributes. Use `field(default_factory=...)` for mutable defaults and `__post_init__` for validation.
- **Coroutine**: An `async def` function. Calling it creates a coroutine object that must be `await`ed (or run with `asyncio.run`). Otherwise its body never runs.

## Mental Models
- **Think of the single underscore as the interface boundary**: Everything that isn't part of an object's interface gets a `_` prefix. Respect it as private, so you can refactor internals without ripple effects. Accessing it from unit tests is a pragmatic exception that still costs you maintainability.
- **Many private methods and attributes are a smell**: They suggest the class violates the single responsibility principle, so extract collaborators.
- **Use `__getattr__` when it removes lots of duplicated boilerplate** (proxies that delegate to a wrapped object, or dynamically resolved attributes such as Graphene `resolve_X`). Remember you are always trading compactness against maintainability.
- **Use a callable object (`__call__`) when a function needs state across calls**, such as memoization, caches, call counting, or better decorators.
- **"Python will start programming you"**: Once small, clean interfaces become your habit, you will build similar abstractions (for example, context-manager-like guarantees) in any language.

## Anti-patterns
- **Mutable default arguments**: `def f(user_metadata: dict = {...})` creates the dict once, when the function is defined. Mutating it breaks every later default call with `KeyError`. Default to `None` and build the value in the body.
- **Subclassing `dict`/`list`/`str` directly**: In CPython, built-in methods don't call each other, so an overridden `__getitem__` is ignored by iteration or `join`. Extend `collections.UserDict`, `UserList`, or `UserString` instead.
- **Leading double underscores for "privacy"**: Non-Pythonic. The resulting `AttributeError` says the attribute "doesn't exist", which is a side effect of mangling, not real privacy. Also, don't define your own dunder methods.
- **Custom `get_*`/`set_*` for every attribute**: Plain attributes are usually enough. Use properties only when access needs logic.
- **Methods that do something and also report status** (`if self.set_email(...)`): These violate CQS and leave readers guessing. Split them into separate statements. Keep properties idempotent; the only exception is a lazy property.
- **Forced one-liners**: Compact is not always better. If the comprehension gets convoluted, write a for loop (KIS).
- **Slices that return a different type**: A slice of a custom sequence should return an instance of the same class, the way `range(1, 100)[25:50]` returns `range(26, 51)`. It must also exclude the end.
- **Self-iterator objects (`__iter__` returns `self`)**: They get exhausted after one pass, so `max()` after a `join` fails with "empty sequence".
- **Assuming dataclass annotations convert types**: They don't. Do the conversions explicitly.
- **Hand-rolled loops that skip elements**: Use slice syntax instead.

## Code Examples
```python
import contextlib

@contextlib.contextmanager
def db_handler():
    try:
        stop_database()
        yield
    finally:
        start_database()

with db_handler():
    db_backup()
```
- **What it demonstrates**: The code before `yield` acts as `__enter__`, and the `finally` code acts as `__exit__`. The backup logic stays isolated from maintenance tasks, and the DB restarts even if the backup fails.

```python
class Boundaries:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def __contains__(self, coord):
        x, y = coord
        return 0 <= x < self.width and 0 <= y < self.height


class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.limits = Boundaries(width, height)

    def __contains__(self, coord):
        return coord in self.limits


def mark_coordinate(grid, coord):
    if coord in grid:
        grid[coord] = MARKED
```
- **What it demonstrates**: Composition plus delegation plus `__contains__`. A duplicated, intention-hiding bounds check (`if 0 <= coord.x < grid.width and ...`) becomes a cohesive object and a self-explanatory `in` test.

```python
from typing import List
from dataclasses import dataclass, field

R = 26

@dataclass
class RTrieNode:
    size = R
    value: int
    next_: List["RTrieNode"] = field(
        default_factory=lambda: [None] * R)

    def __post_init__(self):
        if len(self.next_) != self.size:
            raise ValueError(f"Invalid length provided for next list")
```
- **What it demonstrates**: The unannotated `size` is a shared class attribute, not part of `__init__`. `value` is required. The mutable default comes from a factory with a controlled length (`default_factory=list` would lose that control). `__post_init__` validates the object. The trailing underscore on `next_` avoids shadowing the built-in `next`.

## Reference Tables
**Table 2.1: Magic methods and their behavior in Python**

| Statement | Magic method | Behavior |
|---|---|---|
| `obj[key]`, `obj[i:j]`, `obj[i:j:k]` | `__getitem__(key)` | Subscriptable object |
| `with obj: ...` | `__enter__` / `__exit__` | Context manager |
| `for i in obj: ...` | `__iter__` / `__next__` or `__len__` / `__getitem__` | Iterable object / Sequence |
| `obj.<attribute>` | `__getattr__` | Dynamic attribute retrieval |
| `obj(*args, **kwargs)` | `__call__(*args, **kwargs)` | Callable object |
| `element in obj` | `__contains__` | Container |

| Implementation | Memory | Access to nth element | Re-iterable? |
|---|---|---|---|
| `__iter__` returns `self` + `__next__` | Low | O(n) | No (exhausts) |
| Container iterable (`__iter__` yields) | Low | O(n) | Yes |
| Sequence (`__getitem__` + `__len__` over a list) | High | O(1), negative indexes work | Yes |

## Worked Example
**Collecting account IDs from ARNs, refined three times.**

Before (naive): Initialize an empty `collected_account_ids = set()`, loop over `arns`, call `re.match(ARN_REGEX, arn)`, check `if matched is not None`, extract `groupdict()["account_id"]`, `.add()` it, and return the set. That is many statements for a simple job, which invites mistakes.

Step 2 (functional style):
```python
def collect_account_ids_from_arns(arns):
    matched_arns = filter(None, (re.match(ARN_REGEX, arn) for arn in arns))
    return {m.groupdict()["account_id"] for m in matched_arns}
```

Step 3 (assignment expression, a single statement):
```python
def collect_account_ids_from_arns(arns: Iterable[str]) -> Set[str]:
    return {
        matched.groupdict()["account_id"]
        for arn in arns
        if (matched := re.match(ARN_REGEX, arn)) is not None
    }
```
The author prefers step 3 because it has fewer indirections and everything is in one scope, and `re.match` runs only once per item. Steps 2 and 3 both clearly beat step 1. If the one-liner turns convoluted, though, fall back to the plain loop.

**Fixing the mutable default argument:**
```python
def user_display(user_metadata: dict = None):
    user_metadata = user_metadata or {"name": "John", "age": 30}
    name = user_metadata.pop("name")
    age = user_metadata.pop("age")
    return f"{name} ({age})"
```

## Key Takeaways
1. Prefer built-in idioms: negative indexes, slices (also as `slice` objects), comprehensions, and `with`. They are more readable and usually faster, because a comprehension is a single operation instead of repeated `append` calls.
2. Implement custom behavior through protocols and `collections.abc` interfaces. Delegate to wrapped built-ins so your objects stay consistent with Python's semantics.
3. Use context managers to separate concerns around pre/post conditions. Pick a class, `@contextmanager`, or `ContextDecorator` according to whether the context needs state, belongs to an object, or should be reused as a decorator. Never return `True` from `__exit__` by accident.
4. Use a single underscore for private members, never double. Use properties instead of getters/setters, and keep commands and queries separate.
5. Use dataclasses for data containers (an alternative to namedtuples or namespaces), with `default_factory` for mutable defaults and `__post_init__` for validation.
6. Build container iterables with generators. Choose between an iterable and a sequence based on the memory vs. CPU trade-off.
7. Always avoid mutable default arguments and direct subclassing of built-ins. Always `await` coroutines.

## Connects To
- **Ch 1**: The mutable default argument was the "time-bomb" example. Dataclasses and annotations were introduced there.
- **Ch 3**: KIS (don't force one-liners), separation of concerns, and avoiding side effects.
- **Ch 4**: Many private members suggest a single responsibility principle (SRP) violation. `collections.abc` interfaces act as contracts.
- **Ch 5**: Callable objects (`__call__`) and `ContextDecorator` build better decorators.
- **Ch 6**: Descriptors generalize properties and attribute-access control.
- **Ch 7**: Generators, the iterator protocol in depth, and coroutines, which are built on generators.
- **Ch 9**: Proxies via `__getattr__` delegation.
- **EWD831 (Dijkstra)**: Why indexes start at zero and slices exclude the end.
- **Clean Code (Robert C. Martin)**: Command and query separation. Functions do one thing.
