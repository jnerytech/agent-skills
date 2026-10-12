# Cheatsheet — Clean Code in Python (Anaya)

## Decision rules
| When… | Do… | Because… |
|---|---|---|
| A default argument would be mutable | Default to `None`, build in body | Defaults are created once and shared across calls |
| You need a custom dict/list/str | Subclass `UserDict`/`UserList`/`UserString` (or compose) | CPython built-ins don't call your overrides |
| An attribute should be private | Single `_underscore`; never `__double` | Mangling is collision avoidance, not privacy |
| Access needs logic | `@property` — not `get_x`/`set_x` everywhere | Command/query separation, Pythonic API |
| Converting an exception | `raise NewError(...) from e` | Keeps original traceback in `__cause__` |
| Choosing a check style | EAFP over LBYL | More intention-revealing in Python |
| Using `assert` | Never catch `AssertionError`; never run prod with `-O` | Asserts flag impossible states (defects) |
| Function has too many args | Refactor (pass owning object, reify a concept) | It's a smell; don't silence pylint |
| Subclass overrides a method | Same signature; no stricter pre / weaker postconditions | LSP; mypy/pylint catch the obvious cases |
| Class needs a collaborator | Inject via `__init__` | Flexible + testable without `patch` |
| Writing any decorator | `@wraps(f)` on the inner wrapper | Otherwise name/doc/annotations/doctests lost |
| Decorator has side effects | Put them in the wrapper (call time) | Body runs at import — except deliberate registration |
| Decorator takes params | Make them keyword-only | No context at the decoration site |
| Decorating a coroutine | Wrapper must be `async def` too | Sync wrapper returns an un-awaited coroutine |
| Storing data in a descriptor | `instance.__dict__[self.name]` | Descriptor attrs are shared; `setattr` recurses |
| Feeding `sum`/`min`/`max` | Generator expression | No intermediate list |
| Looping an iterator twice | `itertools.tee` (or a container iterable) | Generators exhaust after one pass |
| Sending into a coroutine | Prime with `next()` first | Else `TypeError` |
| Test needs heavy patching | Refactor toward DI | Patch-heavy tests mean a missing abstraction |
| Lookup misses | Raise or return a domain null object | `None` causes `AttributeError` far away |
| Need a singleton | Module-level object / shared state | Singletons = hard-to-test globals |
| Adapting third-party API | Composition, not inheritance | Inheritance = IS-A + unknown coupling |

## Thresholds & defaults
- **Rule of three**: abstract (decorator, descriptor, pattern) only after the 3rd occurrence; reusable code is ~3× harder to build.
- **Coverage**: ~80% as a *floor*, never a target — executed ≠ tested.
- **Formatting**: black on new repos; yapf only for partial formatting of legacy code.
- **Interfaces**: size by cohesion ("do one thing"), often one method; `__enter__`/`__exit__` stay together.
- **Dependencies**: `setup.py` ranges below next major; pinned, compiled `requirements.txt`; Docker installs only from it.

## Which tool? (decision tree)
- Reusable **behavior around a call** → decorator (Ch 5)
  - needs params → decorator class or `function=None` + `partial`
  - must work on methods too → universal decorator (`__get__`)
- Reusable **logic on attribute access** → descriptor (Ch 6)
  - only read-side / caching → non-data (`__get__`)
  - validation/always win over `__dict__` → data (`__set__`)
  - one-off → plain `@property`
- **Pre/post around a block** → context manager (Ch 2)
- **Stream of values** → generator; **async stream** → async generator (Ch 7)
- **Growing `if/elif` over types** → polymorphism + `__subclasses__()` (OCP, Ch 4) or State/Chain (Ch 9)

## Library vs service (Ch 10)
| | Library (package) | Service |
|---|---|---|
| Consumers all Python | ✅ | overkill |
| Multi-language consumers | ❌ | ✅ |
| Independent deploy/scaling | ❌ | ✅ |
| Cost | low | latency, contracts, SLAs |

## Smells
- `if/elif` on `type`/flags → missing polymorphism (OCP) or reification (State)
- Class name ends in a pattern (`QueryDecorator`) → not intention-revealing
- Empty `except:` / `except Exception: pass` → errors passing silently
- `# type: ignore` on an override → LSP violation hidden
- `__getattr__` not raising `AttributeError` → breaks `getattr(obj, n, default)`
- Imports of the ORM all over the domain → the tool is "screaming", not the use cases
