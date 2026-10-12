# Chapter 3: General Traits of Good Code

## Core Idea
The code is the design: robust, maintainable code comes from applying general design principles (Design by Contract, defensive programming, separation of concerns, high cohesion/low coupling, DRY, YAGNI, KIS, EAFP, composition over misused inheritance, lean function signatures, orthogonality) so that defects are minimized or made evident when they occur.

## Frameworks Introduced
- **Design by Contract (DbC)**: both parties agree on a contract that, if violated, raises an exception clearly stating why execution cannot continue. A contract has **preconditions** (bind the client), **postconditions** (bind the supplier), and optionally documented **invariants** and **side effects**. Only pre/postconditions are enforced in code.
  - When to use: critical components and internal APIs between layers, where you need to know immediately who broke the rules.
  - How: (1) check preconditions before running the core logic — if they fail, do not run the function at all; (2) check postconditions before returning; (3) raise `ValueError`/`RuntimeError` or a custom exception; (4) keep precondition code, postcondition code, and core logic separated (small functions or a decorator); (5) prefer the **demanding** approach (function validates its own input) over the **tolerant** one (client validates); (6) obey the **non-redundancy principle** — each precondition is enforced by one side only, never both.
  - Why it works / failure mode: it localizes blame — precondition failure = client defect, postcondition failure = supplier defect. It fails when contracts only re-check parameter types (that is mypy's job, done better with annotations); validate meaningful properties instead.
- **Defensive programming**: make every object, function, or method able to protect itself against invalid input. Complements DbC rather than replacing it.
  - When to use: data input and calls to external components (expected errors → error handling); impossible conditions (→ assertions).
  - How: choose among **value substitution**, **error logging**, **exception handling**; use `assert` only for conditions that must never happen.
  - Why it works / failure mode: the program degrades gracefully on anticipated errors. Fails when it becomes "too defensive" — empty `except` blocks that silence real bugs.
- **Error-handling strategies**: value substitution (default, constant, sentinel, or neutral value such as `0` in a sum) trades correctness for robustness; defaults for *missing* data are safe, substituting *erroneous* data with "legal close values" masks errors. For critical/sensitive software, favor correctness and fail.
- **Acronyms to live by**: DRY/OAOO, YAGNI, KIS, EAFP/LBYL — empirical mnemonics, not formal rules.
- **Signature-compaction rules** (for functions with too many arguments): (1) pass the common object instead of its parts; (2) group parameters into a container — **reify** the missing abstraction; (3) last resort: `*args`/`**kwargs`, with thorough documentation.

## Key Concepts
- **Precondition**: guarantee a function expects before running; imposes a constraint on the caller.
- **Postcondition**: guarantee about the state after the function returns; lets any client use the result safely.
- **Non-redundancy principle**: a precondition is enforced by the client or the function, never both.
- **Ripple effect**: propagation of a change (or error) from one point to remote parts of the code base.
- **Cohesion**: objects have a small, well-defined purpose and do as little as possible.
- **Coupling**: degree of mutual dependency; causes no code reuse, ripple effects, low level of abstraction.
- **Leaky abstraction**: a function whose caller knows everything it needs (many params), so it abstracts little.
- **Mixin**: a base class encapsulating reusable behavior, not useful alone, combined via multiple inheritance.
- **MRO (C3 linearization)**: Python's deterministic order for resolving methods in multiple-inheritance hierarchies (`cls.mro()`).
- **Orthogonality**: changing one component has no impact on others; side effects stay local.

## Mental Models
- Think of **exceptions as weakening encapsulation**: every exception a function raises is something the caller must know about. If a function raises too many, it is not cohesive — split it.
- Use **assertions as self-checks for correctness** (invariants of an algorithm), and **exceptions for unexpected situations related to business logic**. Exceptions will be far more common.
- Think of **code as knowledge**: duplication appears when domain knowledge (e.g., a scoring formula) has no name or rightful location. Name it and duplication disappears.
- Use **inheritance for specialization only**: if a subclass overrides or ignores most of what it inherits, the superclass is vague or the subclass is not a real specialization. Otherwise, compose ("uses a", not "is a").

## Anti-patterns
- **Exceptions as go-to for business logic**: spans call-stack levels, breaks abstraction levels, mixes core logic with error handling.
- **Mixing exception levels in one method** (`ConnectionError` and `ValueError` caught together in `deliver_event`): handle each at the abstraction level it belongs to.
- **Empty `except: pass`** ("the most diabolical Python anti-pattern"): never fails even when it should. Catch a specific exception and actually handle it (log with `logger.exception`, substitute, or re-raise); use `contextlib.suppress(KeyError)` to ignore explicitly. Configure CI to flag it.
- **Exposing tracebacks to end users**: information disclosure useful to attackers; log details internally, show generic messages.
- **Changing exception type without chaining**: always `raise NewError(...) from e` (PEP-3134; sets `__cause__`).
- **Catching `AssertionError` for control flow / asserting on function calls**: calls may have side effects and are not repeatable; assign to a local first. Never run production with `python -O`.
- **YAGNI violations**: speculative base classes and premature design patterns biased by current requirements become the wrong abstraction.
- **Over-complicated interfaces** (`ComplicatedNamespace.init_with_data`), meta-classes/meta-programming without strong justification, decorators to remove three duplicated lines.
- **Domain object inheriting from implementation object** (`TransactionalPolicy(collections.UserDict)`): wrong hierarchy plus coupling to `pop()`, `items()`, etc.
- **Mutating function arguments**; reading specific keys from `**kwargs`; positional-only for meaningful arguments; suppressing pylint's too-many-arguments warning instead of refactoring.
- **Large files with many definitions**: split into a package.

## Code Examples
```python
def connect_with_retry(connector: Connector, retry_n_times: int, retry_backoff: int = 5):
    """Tries to establish the connection of <connector> retrying
    <retry_n_times>, and waiting <retry_backoff> seconds between attempts.
    """
    for _ in range(retry_n_times):
        try:
            return connector.connect()
        except ConnectionError as e:
            logger.info("%s: attempting new connection in %is", e, retry_backoff)
            time.sleep(retry_backoff)
    exc = ConnectionError(f"Couldn't connect after {retry_n_times} times")
    logger.exception(exc)
    raise exc


class DataTransport:
    _RETRY_BACKOFF: int = 5
    _RETRY_TIMES: int = 3

    def __init__(self, connector: Connector) -> None:
        self._connector = connector
        self.connection = None

    def deliver_event(self, event: Event):
        self.connection = connect_with_retry(
            self._connector, self._RETRY_TIMES, self._RETRY_BACKOFF
        )
        self.send(event)

    def send(self, event: Event):
        try:
            return self.connection.send(event.decode())
        except ValueError as e:
            logger.error("%r contains incorrect data: %s", event, e)
            raise
```
- **What it demonstrates**: handling each exception at its own level of abstraction — connection concerns in one function, decode errors in `send`.

```python
class InternalDataError(Exception):
    """An exception with the data of our domain problem."""

def process(data_dictionary, record_id):
    try:
        return data_dictionary[record_id]
    except KeyError as e:
        raise InternalDataError("Record not present") from e
```
- **What it demonstrates**: wrapping a low-level exception in a domain exception while preserving the original traceback.

```python
class UpperIterableMixin:
    def __iter__(self):
        return map(str.upper, super().__iter__())

class Tokenizer(UpperIterableMixin, BaseTokenizer):
    pass
```
- **What it demonstrates**: a mixin acting like a decorator via the MRO — `super()` delegates to `BaseTokenizer.__iter__`.

## Reference Tables

| Approach | Where validation lives | Author's preference |
|---|---|---|
| Tolerant | Client validates before calling | — |
| Demanding | Function validates its own input | Preferred (safer, industry norm) |

| Mechanism | Use for | Never |
|---|---|---|
| Exception | Unexpected situations callers must know about | Business-logic flow control |
| Assertion | Impossible conditions / invariants (defects) | Catch it, use with side-effecting calls, disable with `-O` |
| Value substitution | Missing data → defaults (`dict.get`, `os.getenv`, default params) | Replacing erroneous data in critical software |

| Style | Pattern | Recommendation |
|---|---|---|
| LBYL | `if os.path.exists(f): open(f)` | Natural in C-like languages |
| EAFP | `try: open(f) except FileNotFoundError` | Default in Python — more intention-revealing |

| Parameter syntax | Meaning | When |
|---|---|---|
| `def f(x, y, /)` | positional-only (PEP-570, 3.8+) | Only when names are meaningless (e.g., two words in an anagram check) |
| `def f(x, *, kw)` / `*args, kw` | keyword-only (PEP-3102) | Arguments that need context (`use_new_implementation=True`); backward-compatible extension |
| `*args, **kwargs` | variadic | Perfect wrappers only (decorators, `super()` calls) |

## Worked Example
**Inheritance → composition (TransactionalPolicy).** An insurance module needs `policy[customer_id]` access plus `change_in_policy()`. Before: `class TransactionalPolicy(collections.UserDict)` — gets subscripting "for free" but now *is a* dictionary, exposing public `clear`, `pop`, `popitem`, `items`, `update`… that callers may call with unintended side effects; the one method it needs isn't inherited anyway. After:
```python
class TransactionalPolicy:
    def __init__(self, policy_data, **extra_data):
        self._data = {**policy_data, **extra_data}

    def change_in_policy(self, customer_id, **new_policy_data):
        self._data[customer_id].update(**new_policy_data)

    def __getitem__(self, customer_id):
        return self._data[customer_id]

    def __len__(self):
        return len(self._data)
```
It *uses* a dict privately; swapping the data structure won't affect callers, unit tests stay unchanged, ripple effects shrink. Rule: extend implementation classes only to create more specific implementation classes; same for domain classes.

**DRY companion:** a ranking lambda `s.passed * 11 - s.failed * 5 - s.years * 2` duplicated in `sorted(key=...)` and a print statement → extract `score_for_student(student)` and use it in both places.

**Orthogonality companion:** `str_final_price(base_price, tax, discount, fmt_function=str)` composes `calculate_price` and an injected formatter (`show_price`); either can change without touching the other, and their tests are independent.

## Key Takeaways
1. Use DbC on critical components: preconditions bind the client, postconditions bind the supplier; validate meaningful properties, not just types.
2. Exceptions announce exceptional situations, never business flow; handle them at the right abstraction level, chain with `raise ... from e`, never leave empty `except` blocks.
3. Assertions guard impossible conditions; don't catch `AssertionError`, don't assert on function calls, never run production with `-O`.
4. Aim for high cohesion and low coupling; separation of concerns minimizes ripple effects.
5. Apply DRY by naming domain knowledge; YAGNI and KIS by building only what current requirements need, in a way that is easy to change later (design bottom-up). Prefer EAFP when in doubt.
6. Inherit only to specialize (base handlers, ABC interfaces, exception hierarchies); otherwise compose. Mixins are a valid use of multiple inheritance.
7. Too many arguments is a code smell: pass the owning object, reify a new abstraction, and reserve `*args/**kwargs` for perfect wrappers; don't mutate arguments.

## Connects To
- **Ch 1**: mypy, pylint and CI tooling enforce types, flag empty excepts and too-many-arguments.
- **Ch 2**: context managers, `contextlib`, Pythonic idioms used to reduce duplication.
- **Ch 4**: SRP builds on cohesion; LSP builds on DbC (preconditions/postconditions in hierarchies); ISP uses multiple inheritance of ABCs.
- **Ch 5**: decorators to separate contract checks and remove duplication (with KIS caveat).
- **Ch 7**: generators/iterators as DRY tools; returning generators improves orthogonality.
- **Ch 8**: orthogonal components yield orthogonal unit tests; contracts deserve tests.
- **Ch 9**: adapter pattern via multiple inheritance; null object pattern; premature patterns violate YAGNI.
- **Ch 10**: separation of concerns and package structuring at the architecture level.
- **Bertrand Meyer, Object-Oriented Software Construction**: origin of Design by Contract.
- **The Pragmatic Programmer**: source of DRY and orthogonality.
