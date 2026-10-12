# Chapter 8: Unit Testing and Refactoring

## Core Idea
Unit tests are core code, not secondary code. They are the formal proof that the program meets its specification, the safety net that makes refactoring possible, and a heuristic for design quality: code that is hard to test is poorly designed. Treat test code with the same clean-code principles as production code.

## Frameworks Introduced
- **Traits of a unit test**: **Isolation** (no database or HTTP calls; tests are independent and can run in any order), **Performance** (fast, so you can run them repeatedly), **Repeatability** (deterministic; a failing test keeps failing until the code is fixed; not flaky or random), **Self-validating** (the run decides the result: `.` pass, `F` failed assertion, `E` exception, non-zero exit code on failure).
  - When to use: as a checklist when you write or review any unit test.
  - How: patch the boundaries, keep each test small, avoid shared state, and make no manual interpretation necessary.
  - Why it works / failure mode: fast, deterministic tests can run constantly and form the safety net. When tests become flaky or slow, people ignore or disable them, and then "the entire production code is in jeopardy". The author still allows pragmatism: if a "unit" test needs a Docker database, go for it, because *practicality beats purity*.
- **Testability as a design driver** ("There are no tricks to writing tests; there are only tricks to writing testable code" — Miško Hevery).
  - When to use: whenever a test is awkward, needs heavy mocking, or exercises far more code than its target.
  - How: (1) try to test the unit; (2) notice the friction (nested logic, hard-wired dependencies); (3) extract the missing abstraction (a wrapper or adapter, a smaller method); (4) inject the dependency instead of creating it inside; (5) test the new abstraction directly.
  - Why it works / failure mode: the friction exposes missing abstractions and hard dependencies. Treating mocks as the fix instead of the symptom leads to shallow, fragile tests.
- **Defining the boundaries of what to test**: test your own code. For third-party dependencies, verify only that they are *called correctly* with the right parameters, and patch at the system's boundaries.
- **Refactoring under tests**: change internal structure without changing external behavior. Unit tests act as the "external observer" that checks the contract still holds. Automated unit tests are the most cost-effective regression tests.
- **TDD (red-green-refactor)**: (1) write a test describing the desired behavior and watch it fail; (2) make the minimal change that makes it pass; (3) refactor and run it again.
- **Property-based testing** (`hypothesis`) and **mutation testing** (`mutpy`): answer "are the tests enough?" and "who tests the tests?".

## Key Concepts
- **Unit test**: code that imports business logic and asserts scenarios on a small unit such as a function or method. A *test suite* is a collection of unit tests.
- **Integration test**: tests several components together, with side effects allowed. External internet dependencies are replaced, for example with Docker services.
- **Acceptance test**: validates the system from a user's perspective by running use cases. It is slower, so it runs less often.
- **Test double**: an object that replaces a real one in tests: dummy, stub, spy, or mock.
- **Mock / MagicMock**: `Mock` returns configured values and records calls. `MagicMock` also supports magic methods (`__getitem__`, `__len__`, ...).
- **Patching (`unittest.mock.patch`)**: replaces an object, given by its import-path string, at runtime.
- **Parameterized test**: the same test condition run over different data (`subTest`, `@pytest.mark.parametrize`).
- **Fixture**: a reusable object or setup provided to tests (`setUp()`, `@pytest.fixture`, `autouse=True`, `conftest.py`).
- **Code coverage**: the lines executed while tests run. It shows blind spots but doesn't prove correctness.
- **Mutant**: a version of the code with altered logic (swapped operators, inverted conditions). A good test suite *kills* mutants.
- **Equivalence class**: a partition of inputs that the code treats the same way. One representative per class is enough.

## Mental Models
- Think of **unit tests as a mirror of the code**: when code is easy to test, it is clear and well designed.
- Think of **coverage as a necessary but insufficient condition**. Use it to find blind spots, never as a goal. Around 80% is a reasonable minimum threshold, but high coverage can still miss half the conditions in a single line.
- Use **heavy patching as a code smell detector**. If you have to patch a lot in proportion to the code under test, an abstraction is missing; inject the dependency instead.
- When you write tests, **adopt a mindset of breaking the code**: target boundaries, equivalence classes, and edge cases. "The best thing about hypothesis is that it makes us think harder about our unit tests."

## Anti-patterns
- **Treating tests as second-class code**: they decay, become a liability, and then get ignored or disabled.
- **Testing third-party libraries**: it never ends. They have their own tests, so check only that you call them correctly.
- **Overriding an internal collaborator in a test** (`wrapped_client.client = Mock()`): it means the dependency should be injected.
- **Mock/patch abuse**: string patch paths break when code moves, patching adds runtime overhead, and you lose contact with the real code, so tests become shallower.
- **Using `Mock` where code calls magic methods**: `TypeError: 'Mock' object is not subscriptable`. Use `MagicMock` instead.
- **Treating coverage as a target**: chasing 100% isn't productive, and a line that ran is not a line that was tested.
- **Mixing several test conditions in one parameter set**: instead, stack `parametrize` decorators to get the cartesian product.
- **Repeating values from the same equivalence class**: it adds no value.
- **Checking only the exception type**: also match the message (`assertRaisesRegex`, `pytest.raises(..., match=...)`) so a different error of the same type doesn't pass by chance.

## Code Examples
```python
class WrappedClient:
    def __init__(self):
        self.client = MetricsClient()

    def send(self, metric_name, metric_value):
        return self.client.send(str(metric_name), str(metric_value))

class TestWrappedClient(unittest.TestCase):
    def test_send_converts_types(self):
        wrapped_client = WrappedClient()
        wrapped_client.client = Mock()
        wrapped_client.send("value", 1)
        wrapped_client.client.send.assert_called_with("value", "1")
```
- **What it demonstrates**: trying to test a type bug in `Process` revealed a missing adapter-like abstraction. The test's override of `client` points to dependency injection as the next step.

```python
@pytest.mark.parametrize("context,expected_status", (
    ({"downvotes": set(), "upvotes": set()}, MergeRequestStatus.PENDING),
    ({"downvotes": set(), "upvotes": {"dev1"}}, MergeRequestStatus.PENDING),
    ({"downvotes": "dev1", "upvotes": set()}, MergeRequestStatus.REJECTED),
    ({"downvotes": set(), "upvotes": {"dev1", "dev2"}}, MergeRequestStatus.APPROVED),
),)
def test_acceptance_threshold_status_resolution(context, expected_status):
    assert AcceptanceThreshold(context).status() == expected_status

@pytest.fixture(autouse=True)   # tests/unit/conftest.py
def no_requests():
    with patch("requests.post"):
        yield
```
- **What it demonstrates**: pytest parametrization, where each tuple becomes its own test case and the body is one line, plus a global autouse fixture that keeps unit tests free of HTTP side effects.

```python
def test_cannot_vote_on_closed_merge_request():
    merge_request = MergeRequest()
    merge_request.close()
    pytest.raises(MergeRequestException, merge_request.upvote, "dev1")
    with pytest.raises(
        MergeRequestException,
        match="can't vote on a closed merge request",
    ):
        merge_request.downvote("dev1")
```
- **What it demonstrates**: asserting an exception both as a call and as a context manager with a message match.

## Reference Tables
| Aspect | `unittest` (stdlib) | `pytest` (pip) |
|---|---|---|
| Style | Object-oriented, JUnit/Smalltalk heritage; `TestCase` subclasses with `test_*` methods | Plain functions with `assert`; classes optional |
| Assertions | `assertEqual(actual, expected)`, `assertRaises`, `assertRaisesRegex` | `assert`, `pytest.raises(..., match=...)` |
| Parametrization | Loop plus `self.subTest(context=...)` inside one test | `@pytest.mark.parametrize`: one test per case; stack decorators for the cartesian product |
| Fixtures | `setUp()` (runs before each test) | `@pytest.fixture`, injected by argument name; `autouse`; `conftest.py` |
| Best for | Simple scenarios; it ships with Python | Complex systems: patching, fixtures, parametrization. It also runs `unittest` tests, so migration can be gradual |

| Test type | Isolation | Speed | When it runs |
|---|---|---|---|
| Unit | Full, no I/O | Fast | Constantly, while coding |
| Integration | Side effects allowed; external services replaced by Docker | Slow | CI, on each merge request |
| Acceptance | User perspective | Slowest | Less frequently |

**Testing heuristics**: *Boundaries* (for `if remaining_days > 0`, test 0; test both ends of a range, empty lists, full stacks) · *Equivalence classes* (one representative per partition, for example even and odd) · *Edge cases* (leap years, February 29th, around the new year).

## Worked Example
**`BuildStatus` notifier: from patching to dependency injection**
- *Before*: a `@classmethod notify(cls, merge_request_id, status)` builds `{"id", "status", "built_at": cls.build_date()}` and calls `requests.post(STATUS_ENDPOINT, json=...)` directly. Testing it needs `@mock.patch("mock_2.requests")` plus `mock.patch("mock_2.BuildStatus.build_date", return_value=...)`, because `datetime` is written in C and can't be patched (freezegun would be overkill). That is a lot of patching for a few lines, and the string paths break when files move.
- *After*:
```python
class BuildStatus:
    endpoint = STATUS_ENDPOINT

    def __init__(self, transport):
        self.transport = transport

    @staticmethod
    def build_date() -> str:
        return datetime.utcnow().isoformat()

    def compose_payload(self, merge_request_id, status) -> dict:
        return {"id": merge_request_id, "status": status,
                "built_at": self.build_date()}

    def deliver(self, payload):
        response = self.transport.post(self.endpoint, json=payload)
        response.raise_for_status()
        return response

    def notify(self, merge_request_id, status):
        return self.deliver(self.compose_payload(merge_request_id, status))

@pytest.fixture
def build_status():
    bstatus = BuildStatus(Mock())
    bstatus.build_date = Mock(return_value="2018-01-01T00:00:01")
    return bstatus
```
  `notify` becomes compose + deliver, and the transport is injected (dependency inversion, with `requests` as an implicit interface). The test just asserts `build_status.transport.post.assert_called_with(build_status.endpoint, json=expected_payload)`, with no string patching.

**Mutation testing**: `evaluate_merge_request(upvote_count, downvotes_count)` with one test, `evaluate_merge_request(3, 0) == APPROVED`. Running `mut.py --target ... --unit-test ... --operator ROR ... --show-mutants` creates a mutant `if downvotes_count < 0:`. The test kills it, and the mutation score is reported as killed, survived, incompetent, or timeout.

**Coverage illusion**: `return "even" if number % 2 == 0 else "odd"` tested only with `(2, "even")` reports 100% coverage while the `odd` branch never runs. Fix it with one representative per equivalence class.

## Key Takeaways
1. Unit tests are first-class code. Design and refactor them too, for example with domain helpers like `assert_rejected()`/`assert_approved()` that grow into a declarative testing API.
2. If code is hard to test, improve the code. Extract abstractions, keep methods small, and inject dependencies.
3. Patch at your system's boundaries and only check that third-party code is called correctly. Excessive patching is a smell.
4. Coverage is a metric, not a target. Around 80% is a sensible minimum, and you still need to test the lines that are already covered.
5. Refactoring isn't safe without automated regression tests, and unit tests are the most cost-effective kind.
6. Use parametrization for equivalence classes (one scenario per parameter set), fixtures for DRY setup, and message-matching for exceptions.
7. Strengthen the suite with property-based testing (hypothesis) and mutation testing (mutpy). Use TDD's red-green-refactor when you write new code or reproduce bugs.

## Connects To
- **Ch 1**: tools and quality gates in CI; coverage thresholds sit next to linters and formatters.
- **Ch 3**: DRY applied to tests; small, cohesive functions improve testability.
- **Ch 4**: dependency inversion and dependency injection (`BuildStatus(transport)`); SRP scopes a test suite to one class.
- **Ch 9**: `WrappedClient` is the adapter pattern.
- **Ch 10**: component testing with mocked dependencies at the architecture level.
- **Ch 2**: `MagicMock` is needed because idiomatic code relies on magic methods.
- **Martin Fowler's Refactoring / Glenford Myers' The Art of Software Testing**: external grounding for refactoring and test design.
