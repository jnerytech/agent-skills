# Chapter 5: Using Decorators to Improve Our Code

## Core Idea
A decorator is syntactic sugar: `@modifier` over `def original` means `original = modifier(original)`. Used well, decorators remove duplication (DRY), separate concerns, and expose clean APIs. Used carelessly, they add indirection, hide side effects, and destroy the wrapped object's metadata.

## Frameworks Introduced
- **The `functools.wraps` formula**: every simple decorator follows `def decorator(original_function): @wraps(original_function) def decorated_function(*args, **kwargs): ...; return original_function(*args, **kwargs); return decorated_function`.
  - When to use: always, on the inner wrapper of any decorator you write.
  - How: (1) define the outer function that takes the wrapped object; (2) decorate the inner function with `@wraps(original)`; (3) do the extra work inside the inner function; (4) call and return the original; (5) return the inner function.
  - **Why it works / failure mode**: `wraps` copies `__name__`, `__qualname__`, `__doc__`, `__annotations__` and adds `__wrapped__`. Without it, every decorated function is called `wrapped`, `help()` shows the wrapper's signature, annotations become `{}`, and doctests in docstrings stop running.
- **Delay side effects to the innermost function**: anything the decorator does besides wrapping (logging, timing, I/O, reading config) goes inside the inner function, so it runs at call time and not at import time.
  - When to use: by default. "If in doubt, err on the side of caution."
  - Exception: registration decorators (adding classes to a public registry) *need* to run at import time. Put that code in the outer scope, outside the closure, even when an inner wrapper exists.
  - **Why it works / failure mode**: the decorator body runs once, when the module is imported. Code placed there runs before the function is ever called. Example: `start_time` gets frozen at import time, so every call reports more elapsed time than the last. External services or config may not exist yet at that point.
- **Parametrized decorators (two forms)**:
  - *Nested functions*: three levels. The outer function takes the parameters, the middle one is the decorator, and the inner one is the wrapper. `@retry(a, b)` means `f = retry(a, b)(f)`.
  - *Decorator objects*: pass the parameters to `__init__` and put the decorator logic in `__call__`. Prefer this form for readability, because it's easier to reason about an object than about three nested closures.
- **Rule of three for decorators (from Glass, *Facts and Fallacies*)**: reuse is acceptable only if (1) you don't write the decorator from scratch: wait until the pattern emerges, then refactor; (2) it will be applied at least three times; (3) the code inside it stays minimal. Reusable components are also about three times harder to build than simple ones.
- **Traits of good decorators**: *encapsulation / separation of concerns* (no leaky abstraction; clients use it as a black box), *orthogonality* (independent of what it decorates), and *reusability* (generic enough for many targets; otherwise it should just be a function).

## Key Concepts
- **Decorator / decorated function (wrapped object)**: the modifier is the decorator, and the original object it transforms is the wrapped object. This is not the GoF decorator design pattern.
- **Class decorator (PEP-3129)**: receives a class and returns a class, for example to add methods or enforce an interface across many classes. It's simpler than a metaclass.
- **Stacking/chaining**: decorators apply bottom-up (`@Serialization` over `@dataclass`), and the order matters.
- **Keyword-only decorator arguments**: at the decoration site there is little context, so named values read better.
- **Positional-only decorated parameter**: `def retry(operation, /)` makes it explicit that the decorator takes no arguments. This is optional.
- **Decorators for coroutines**: replace a function with a function and a coroutine with a coroutine. Use `async def` for the wrapper and `await` the original when the decorator needs the result.
- **PEP-614 extended syntax (3.9)**: any expression may follow `@`, even lambdas. Use it only if readability survives.
- **`__wrapped__`**: the original, undecorated function exposed by `wraps`. It's handy in unit tests but shouldn't be used in production.
- **Universal decorator**: a decorator class that implements `__get__`, so it works on both functions and methods.

## Mental Models
- Think of a decorator as **the place where a cross-cutting concern lives once**: retry, tracing, validation, parameter adaptation, registration.
- Think of the decorator body as **import-time code** and the wrapper body as **call-time code**. Ask "when does this line run?" for every line.
- Use a class decorator **instead of a mixin** when the base class exists only for implementation reasons. A `Customer` is not a `BaseResolverMixin`, so composition beats inheritance.
- Think of good decorators as **API surface**. `@app.task` (Celery) and `@route("/", method=["GET"])` tell the user *what* happens, never *how*.

## Anti-patterns
- **Manual reassignment far from the definition** (`original = modifier(original)` many lines later): readers can't find the full definition in one place.
- **Omitting `@wraps`**: you lose the name, docstring, annotations and doctests, and tracing and debugging get harder.
- **Side effects in the decorator body**: they run on import with the wrong timing (frozen timers, logs before any call), and they fail if config isn't loaded yet.
- **Multi-responsibility decorators**: for example, `traced_function` both logs the call and measures the time. Apply SRP: split it into `log_execution` and `measure_time`, then stack them.
- **Premature generic decorators**: indirection with fewer than ~3 uses costs more than it saves. Use a plain function or a small class instead.
- **Function-only decorators applied to methods**: `self` shifts the arguments, which raises `TypeError: wrapped() takes 1 positional argument but 2 were given`.
- **Sync wrapper around a coroutine when you need its result**: the wrapper returns an un-awaited coroutine inside a dict, and the caller then tries to `await` a dict.
- **Unintentional signature changes**: changing a signature is only good when it's deliberate, for example to adapt a convoluted API.
- **Overly clever `@` expressions** (PEP-614 lambdas) that compress the code but hurt readability.

## Code Examples
```python
_DEFAULT_RETRIES_LIMIT = 3

class WithRetry:
    def __init__(
        self,
        retries_limit: int = _DEFAULT_RETRIES_LIMIT,
        allowed_exceptions: Optional[Sequence[Exception]] = None,
    ) -> None:
        self.retries_limit = retries_limit
        self.allowed_exceptions = allowed_exceptions or (ControlledException,)

    def __call__(self, operation):
        @wraps(operation)
        def wrapped(*args, **kwargs):
            last_raised = None
            for _ in range(self.retries_limit):
                try:
                    return operation(*args, **kwargs)
                except self.allowed_exceptions as e:
                    logger.warning(
                        "retrying %s due to %s", operation.__qualname__, e
                    )
                    last_raised = e
            raise last_raised
        return wrapped

@WithRetry(retries_limit=5)
def run_with_custom_retries_limit(task):
    return task.run()
```
- **What it demonstrates**: a parametrized decorator implemented as an object (`__init__` holds the parameters, `__call__` decorates). This is cleaner than three nested functions.

```python
def decorator(function=None, *, x=DEFAULT_X, y=DEFAULT_Y):
    if function is None:
        return partial(decorator, x=x, y=y)   # called as @decorator(...)

    @wraps(function)
    def wrapped():
        return function(x, y)
    return wrapped
```
- **What it demonstrates**: one decorator that supports both `@decorator` and `@decorator(x=3, y=4)`. The keyword-only parameters make `function is None` a reliable test.

```python
from functools import wraps
from types import MethodType

class inject_db_driver:
    """Convert a string to a DBDriver instance and pass this to the wrapped function."""
    def __init__(self, function) -> None:
        self.function = function
        wraps(self.function)(self)

    def __call__(self, dbstring):
        return self.function(DBDriver(dbstring))

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self.__class__(MethodType(self.function, instance))
```
- **What it demonstrates**: a decorator that "always works". `__get__` rebinds the callable to the instance, so methods work. Plain functions never trigger `__get__`, so they work too.

## Reference Tables
| Need | Implementation choice |
|---|---|
| No parameters | Plain function + inner `@wraps` wrapper |
| Parameters, few, simple | Nested functions (3 levels) |
| Parameters, readability matters / state | Decorator class (`__init__` + `__call__`) |
| Must work on functions **and** methods | Decorator class + `__get__` with `types.MethodType` |
| Support `@deco` and `@deco(...)` | `function=None` + keyword-only params + `functools.partial` |
| Function **and** coroutine | Two wrappers, dispatch on `inspect.iscoroutinefunction` (a facade) |
| Must act at import time (registry) | Side effect in outer scope, return object unchanged |

| Good use | Example |
|---|---|
| Transforming parameters / adapting signatures | `@DomainArgs def resolver_function(helper)` hides `(root, args, context, info)` |
| Tracing code | logging calls/params, timing, metrics |
| Validating parameters | preconditions/postconditions (Design by Contract) |
| Retry operations | `@with_retry(retries_limit=4, allowed_exceptions=(...))` |
| Simplifying classes (DRY) | `@Serialization(...)`, `@with_resolver` |

## Worked Example
**Event serialization: from per-event serializer classes to a class decorator.**
*Before*, each event has its own `LoginEventSerializer` with a hand-written `serialize()` that redacts the password and formats the timestamp. `LoginEvent` holds `SERIALIZER = LoginEventSerializer` and a `serialize()` that delegates to it. This leads to too many classes (one per event), poor reuse (hiding the password must be re-called in each class), and boilerplate (`serialize()` repeated, or a dubious mixin).

*After*, small transformation functions (`hide_field`, `format_time`, `show_original`), an `EventSerializer` that applies `{field: transformation(getattr(event, field))}`, and a class decorator:
```python
class Serialization:
    def __init__(self, **transformations):
        self.serializer = EventSerializer(transformations)

    def __call__(self, event_class):
        def serialize_method(event_instance):
            return self.serializer.serialize(event_instance)
        event_class.serialize = serialize_method
        return event_class

@Serialization(
    username=str.lower,
    password=hide_field,
    ip=show_original,
    timestamp=format_time,
)
@dataclass
class LoginEvent:
    username: str
    password: str
    ip: str
    timestamp: datetime
```
The decoration arguments document how each field is treated. The decorator is justified specifically because it *adds a method to the class*; otherwise a class attribute would have been enough. (Ch 6 later replaces this with descriptors.)

## Key Takeaways
1. Always apply `functools.wraps` to the inner wrapper.
2. Keep side effects inside the wrapper (call time), except for deliberate import-time registration.
3. Prefer decorator classes for parametrized decorators. Make the parameters keyword-only.
4. Make decorators universal: match the signature when you need to touch the arguments, use `*args, **kwargs` for generality, and use `__get__` for methods.
5. Replace a function with a function and a coroutine with a coroutine.
6. One responsibility per decorator. Compose small decorators by stacking them, and remember that order matters.
7. Create a decorator only after you've seen the pattern at least three times. Good decorators are encapsulated, orthogonal, reusable, and act as a clean API.

## Connects To
- **Ch 2**: `@dataclass`, `__getattr__`, positional-only/keyword-only syntax, and `@property` as built-in decorator examples.
- **Ch 3**: DRY, separation of concerns, Design by Contract (validation decorators), composition over inheritance.
- **Ch 4**: SRP applied to decorators. Mixin inheritance that breaks the "is a" relation (LSP).
- **Ch 6**: descriptors explain the `__get__` fix for method decorators and offer an alternative to the serialization class decorator.
- **Ch 7**: decorating generators and coroutines, and the async syntax differences.
- **Ch 9**: adapter-like signature adaptation; the GoF Decorator pattern, which is distinct from Python decorators.
- **External**: PEP-318, PEP-3129, PEP-614, `functools.wraps`/`partial`, the `wrapt` library (universal decorators), Glass's *Facts and Fallacies of Software Engineering* (rule of three).
