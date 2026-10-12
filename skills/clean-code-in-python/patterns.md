# Patterns & Techniques — Clean Code in Python (2nd ed.)

## Quality Checklist Pipeline (Ch 1)
**When to use**: every project with more than one contributor.
**How**: one `make checklist` target runs lint (pylint) → typehint (mypy) → format check (`black --check`) → tests; CI calls the same target and fails the build.
**Trade-offs**: setup cost once; in return, style debates leave code review and tools can be swapped without changing anyone's workflow.

## Context Manager via `@contextmanager` / `ContextDecorator` (Ch 2)
**When to use**: pre/post logic (resource acquire/release, maintenance windows) not belonging to an object.
**How**: generator with `try: yield` / `finally:` cleanup; or subclass `ContextDecorator` and apply as `@handler()` to many functions.
**Trade-offs**: no fake class; `ContextDecorator` can't expose the context object to the function.

## Composition + Delegation instead of Inheriting Built-ins (Ch 2, Ch 3)
**When to use**: a domain class tempted to inherit from `dict`/`list`, or repeated bounds checks.
**How**: keep the structure in a private attribute; expose only needed dunders (`__getitem__`, `__contains__`); if extension is really needed, subclass `UserDict`/`UserList`.
**Trade-offs**: slight boilerplate; avoids leaking the whole data-structure API and IS-A misuse.

## Design by Contract with Validation at One Side (Ch 3)
**When to use**: public functions with input assumptions.
**How**: state preconditions/postconditions; check each in exactly one place (non-redundancy); raise domain exceptions at the right level, chaining with `raise X from e`.
**Trade-offs**: extra checks vs early, obvious failures.

## Polymorphic Discovery (OCP) (Ch 4)
**When to use**: a growing `if/elif` chain over types.
**How**: each subclass implements `meets_condition(data)`; client iterates `Base.__subclasses__()` (or a registry); fall back to a null object (`UnknownEvent`).
**Trade-offs**: perfect closure is impossible; choose the axis most likely to change.

## Interface + Constructor Injection (DIP) (Ch 4, Ch 8)
**When to use**: high-level code depends on a volatile detail (I/O, third-party API).
**How**: define an ABC for the message needed (`send()`), make details implement it, inject via `__init__` with a sensible default; use `pinject` for big graphs.
**Trade-offs**: one more abstraction; big win in testability (no fragile `mock.patch` paths).

## `@wraps` Decorator with Call-Time Side Effects (Ch 5)
**When to use**: cross-cutting concerns (retry, logging, timing, serialization).
**How**: `def deco(f): @wraps(f) def wrapped(*a, **kw): ...` — side effects inside `wrapped`; parameters keyword-only; parametrized form as a class (`__init__` params, `__call__` logic) or `function=None` + `partial` for defaults.
**Trade-offs**: indirection; only create after the rule of three; one responsibility per decorator.

## Universal Decorator (Ch 5)
**When to use**: decorator must work on functions and methods alike.
**How**: decorator class with `__get__` returning `self.__class__(MethodType(self.function, instance))`.
**Trade-offs**: needs class form and descriptor knowledge.

## Validating / Transforming Field Descriptor (Ch 6)
**When to use**: the same property-setter logic repeated across attributes/classes.
**How**: `__set_name__` captures the name; `__set__` validates and stores in `instance.__dict__[name]`; `__get__` returns `self` when `instance is None`; variants via `partial(Base, transformation=...)`.
**Trade-offs**: smaller client classes; complex descriptor, so keep business logic out.

## Lazy Generator Pipeline (Ch 7)
**When to use**: producer builds a list the consumer just streams.
**How**: replace `append` with `yield`; chain generator expressions, `filter`, `itertools.islice`/`tee`; use `next(genexpr, default)` to flatten nested-loop searches.
**Trade-offs**: low memory; single pass only.

## `yield from` Delegation & Async Protocols (Ch 7)
**When to use**: composing generators/coroutines; async resources and streams.
**How**: `result = yield from sub()`; async: `__aenter__`/`__aexit__`, `__aiter__`/`__anext__` or async generators.
**Trade-offs**: async leaks upward through every caller.

## Testability-Driven Refactoring (Ch 8)
**When to use**: a test needs heavy patching or overriding internals.
**How**: split compose from deliver, inject the transport, test with simple Mocks; parametrize with `@pytest.mark.parametrize`, share setup via fixtures/`conftest.py`; strengthen with hypothesis and mutation testing.
**Trade-offs**: one extra abstraction; much less fragile tests.

## Shared State instead of Singleton (Ch 9)
**When to use**: several instances must see one updatable value.
**How**: module-level object; or `SharedAttribute` descriptor; or Borg (`SharedAllMixin`) as last resort.
**Trade-offs**: avoids hard-to-test global classes; Borg replicates everything.

## Pythonic GoF Set (Ch 9)
**When to use**: after the problem appears three times.
**How**: Adapter (composition), Composite, Decorator (class or function form), Facade (`__init__.py`), Chain of responsibility, Template method, Command (`do()`), State (reify states as classes), Null object.
**Trade-offs**: never name classes after patterns; never force a pattern a simpler solution covers.

## Architectural Adapters & Packaging (Ch 10)
**When to use**: any external boundary (ORM, web framework, broker); delivering services.
**How**: own `storage`/`web` packages return domain objects; ship shared code as a library with `setup.py` ranges, compile a pinned `requirements.txt`, install only from it in Docker; expose CLIs via `console_scripts`.
**Trade-offs**: indirection; some traits (async) still leak; library < service in cost unless multi-language/independent deploy.
