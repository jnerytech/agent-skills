# Chapter 7: Generators, Iterators, and Asynchronous Programming

## Core Idea
Iteration is built into Python through the iterator protocol, and generators are the simplest way to implement it: they produce values lazily (saving memory) and act as an abstraction over *how* a loop works. Generators also grew `send()`/`throw()`/`close()`, return values, and `yield from`, and that machinery is the basis of coroutines and `async`/`await`.

## Frameworks Introduced
- **Iteration protocol (`__iter__` + `__next__`)**: an *iterable* implements `__iter__` and returns an *iterator*; an *iterator* implements `__next__`, produces one value per call, and raises `StopIteration` when it runs out.
  - When to use: any object that should work in a `for` loop, `zip()`, `list()`, `sum()` and so on, instead of a custom `.next()` method.
  - How: (1) implement `__next__` to produce the next value; (2) implement `__iter__` (often `return self`); (3) raise `StopIteration` to finish. Prefer a generator function when you can, because it does all three for you.
  - Why it works / failure mode: it is a "standard contract" that every Python developer already knows, so you don't have to agree on a home-grown interface with your team. If you implement only `__next__`, `for` loops fail with `TypeError: ... object is not iterable`. If you rely on the `__getitem__`/`__len__` sequence fallback, the object iterates only by coincidence.
- **Generator as lazy producer**: replace "build a list and return it" with `yield` for each element. The consumer's `for` loop stays the same.
  - When to use: the consumer processes items one at a time but the producer loads them all into memory, for example reading a large file.
  - How: remove the accumulator list, `append`, and `return`; `yield` each value instead. Chain filters lazily with `filter`, `itertools.islice` and generator expressions.
  - Why it works / failure mode: generators are polymorphic with `for` loops, and memory use drops sharply. The cost is possibly more CPU time, which is usually acceptable. A generator is **exhausted** after one pass, so consuming it twice silently gives empty results.
- **Generator interface as coroutine (PEP-342)**: `close()`, `throw(ex_type[, ex_value[, ex_traceback]])`, `send(value)`, plus `receive = yield produced`.
  - When to use: to understand what `async`/`await` does underneath. In modern Python you rarely write these coroutines by hand.
  - How: prime the coroutine with `next()` first. Use `send()` to pass data in. Catch `GeneratorExit` to release resources on `close()`. Handle domain exceptions passed in with `throw()` and keep going.
- **Delegation with `yield from` (PEP-380)**: forwards iteration, `send()` and `throw()` to a sub-generator, and evaluates to the sub-generator's return value (`StopIteration.value`).
  - When to use: to split a large coroutine into smaller ones, chain iterables, or collect a sub-coroutine's final result.

## Key Concepts
- **Generator**: any function containing `yield`. Calling it only creates a generator object, which is an iterator.
- **Generator expression**: a comprehension written with `()` instead of `[]`. It is lazy and is consumed only once.
- **Iterable vs iterator**: an iterable has `__iter__` and can be used in `for ... in`. An iterator has `__next__`, produces values on demand, and stays idle between calls.
- **Sequence fallback**: an object with `__getitem__` and `__len__` is iterable even without `__iter__`. Iteration stops on `IndexError`.
- **`next(it, default)`**: advances an iterator. With a default, it returns that value instead of raising `StopIteration`.
- **`itertools.tee`**: splits one iterable into *n* independent iterators so the source is traversed only once.
- **Coroutine**: a function whose execution can be suspended and resumed later. In Python, "coroutines are just fancy generators" that are semantically different from them.
- **Awaitable / native coroutine**: an object with `__await__`, created by `async def`. Using `await` on a non-awaitable fails immediately, unlike `yield from` on any iterable.
- **Event loop**: schedules coroutines and resumes another one while a coroutine waits on `await`. It is `asyncio` by default; `uvloop` and `trio` follow the same API.
- **Asynchronous generator (PEP-525)**: an `async def` that contains `yield`. Inside an `async def`, `yield` produces a value for the caller; it does not suspend the coroutine.

## Mental Models
- Think of **a generator as an abstraction over iteration**, much as a context manager is an abstraction over setup and teardown. The `for` loop doesn't need to know how values are produced.
- Use a **generator function instead of an iterator class** whenever possible. It is syntactically simpler, just as a function-based decorator is simpler than a class-based one.
- Think of **generators and coroutines as technically the same but semantically different**. Generators are for efficient iteration; coroutines are for suspending and resuming execution, usually around non-blocking I/O. `async def`/`await` exist so that mixing the two up fails early instead of at runtime.
- Use **`itertools` as your first stop** for any iteration problem. Even if the exact answer isn't there, its recipes will give you ideas.

## Anti-patterns
- **Loading everything into a list when the consumer streams**: the program may run out of memory on large inputs for no benefit.
- **Passing a list comprehension to `sum()`/`min()`/`max()`**: `sum([x**2 for x in ...])` builds an unnecessary list. Pass a generator expression instead.
- **Putting filter conditions inside a processing class** (`if purchase > 1000.0:` in `process`): it makes the class rigid and couples it to client needs. Filter outside with `filter`/`islice` instead.
- **Looping over the same data several times**: use `itertools.tee` instead.
- **Escaping nested loops with flags or exceptions**: flags clutter the code, and exceptions should not be used for control flow. Flatten the iteration into one loop with a generator.
- **Designing an object as a sequence just so it can be iterated**: implement `__iter__` instead.
- **Calling `send()` on a coroutine that hasn't been primed**: it raises `TypeError: can't send non-None value to a just-started generator`.
- **Async versions of other magic methods** (a coroutine in `__getattr__`, an async `__init__`): they signal misplaced responsibilities. Magic methods should depend only on the object's internal state, and `__init__` should receive dependencies that are already initialized.

## Code Examples
```python
def _iterate_array2d(array2d):
    for i, row in enumerate(array2d):
        for j, cell in enumerate(row):
            yield (i, j), cell

def search_nested(array, desired_value):
    try:
        coord = next(
            coord
            for (coord, cell) in _iterate_array2d(array)
            if cell == desired_value
        )
    except StopIteration as e:
        raise ValueError(f"{desired_value} not found") from e
    logger.info("value %r found at [%i, %i]", desired_value, *coord)
    return coord
```
- **What it demonstrates**: flattening nested loops with a helper generator, plus the `next(genexpr)` idiom for finding the first match.

```python
def stream_db_records(db_handler):
    retrieved_data = None
    page_size = 10
    try:
        while True:
            page_size = (yield retrieved_data) or page_size
            retrieved_data = db_handler.read_n_records(page_size)
    except GeneratorExit:
        db_handler.close()
```
- **What it demonstrates**: a coroutine that receives values through `send()` (`receive = yield produced`) and releases resources on `close()`.

```python
def sequence(name, start, end):
    logger.info("%s started at %i", name, start)
    yield from range(start, end)
    logger.info("%s finished at %i", name, end)
    return end

def main():
    step1 = yield from sequence("first", 0, 5)
    step2 = yield from sequence("second", step1, 10)
    return step1 + step2   # StopIteration: 15
```
- **What it demonstrates**: `yield from` collects a sub-generator's return value. `send()` and `throw()` sent to `main` reach the active sub-generator transparently.

## Reference Tables
**Table 7.1: Iterables and iterators**

| Python concept | Magic method | Considerations |
|---|---|---|
| Iterable | `__iter__` | Uses an iterator to build the iteration logic; works in `for ... in ...:` |
| Iterator | `__next__` | Produces values one at a time; `StopIteration` ends it; values are read with `next()` |

**Table 7.2: Asynchronous syntax and their magic methods (PEP-492)**

| Concept | Magic methods | Syntax usage |
|---|---|---|
| Context manager | `__aenter__` `__aexit__` | `async with async_cm() as x: ...` |
| Iteration | `__aiter__` `__anext__` | `async for e in aiter: ...` |

**Sync vs async iteration end signals**: `StopIteration` for `next()`/`for`; `StopAsyncIteration` for `__anext__`/`async for`. `next()` doesn't work on async iterators, so write a custom `anext()` wrapper or use `await it.__anext__()`.

## Worked Example
**Purchase statistics (`PurchasesStats`)**
- *Before*: `_load_purchases(filename)` builds `purchases = []`, appends `float(price_raw)` for every line, and returns the list. `PurchasesStats` holds `iter(purchases)` and updates min, max and average in one `for` loop, with about 40 lines of `_update_min`, `_update_max`, `_update_avg` and `_initialize`, which raises `ValueError` when the input is empty. With large files, memory use explodes.
- *Step 1 (lazy producer)*: change the loader to `yield float(price_raw)` inside `with open(filename) as f: for line in f:`. The consumer code doesn't change, and memory use drops significantly.
- *Step 2 (filtering outside the class)*: `purchases = islice(filter(lambda p: p > 1000.0, purchases), 10)` and then `PurchasesStats(purchases).process()`. Everything stays lazy and the class keeps a single responsibility.
- *Step 3 (collapse the class)*:
```python
def process_purchases(purchases):
    min_, max_, avg = itertools.tee(purchases, 3)
    return min(min_), max(max_), median(avg)
```
  The source is traversed once, and `min()` raises on empty input by itself. (The author's listing calls `median` on the third branch; use `statistics.mean` for a true average.)

**Async iteration**: a `RecordStreamer` class with `__aiter__` (returns `self`) and `async def __anext__` (awaits a coroutine, raises `StopAsyncIteration`) reduces to:
```python
async def record_streamer(max_rows):
    current_row = 0
    while current_row < max_rows:
        row = (current_row, await coroutine())
        current_row += 1
        yield row
```

## Key Takeaways
1. Pass generator expressions, not lists, to functions that accept iterables (`sum`, `min`, `max`). Remember that generators are exhausted after one pass.
2. Implement the iteration protocol (`__iter__`/`__next__`) rather than custom `.next()` methods, and prefer generator functions over iterator classes.
3. Use `next(genexpr, default)` to find the first match. Before iterating the same data twice, consider `itertools.tee`. Flatten nested loops into one generator.
4. Prime coroutines with `next()` before `send()`. Use `close()`/`GeneratorExit` for cleanup and `throw()` to pass in exceptions.
5. `yield from` captures sub-generator return values and forwards `send()`/`throw()`, and that makes coroutines behave like lightweight threads.
6. `async def`/`await` is an API for the event loop. `await` accepts only awaitables, so a mixed-up type fails early.
7. Prefer asynchronous generators over `__aiter__`/`__anext__` classes. Use `@contextlib.asynccontextmanager` for async context managers.

## Connects To
- **Ch 2**: magic methods, context managers, `contextlib`, and the first introduction to async code. This chapter adds the iteration protocol and async magic methods.
- **Ch 3**: cohesion and the danger of rigid code. Filtering outside `PurchasesStats` keeps its responsibility narrow.
- **Ch 5**: function-based vs class-based decorators is the same trade-off as generator vs iterator class; `@prepare_coroutine` is a priming decorator.
- **Ch 4**: the dependency-injection argument against async `__init__`.
- **Ch 9**: the iterator design pattern (GoF) is built into the language.
- **PEP-234/255/342/380/492/525**: iterators, generators, enhanced generators, `yield from`, `async`/`await`, async generators.
- **Lazy evaluation (Haskell)**: generators make infinite sequences and lazy pipelines possible.
