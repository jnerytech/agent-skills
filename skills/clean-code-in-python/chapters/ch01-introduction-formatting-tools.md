# Chapter 1: Introduction, Code Formatting, and Tools

## Core Idea
Clean code is code other engineers can read and change, because programming languages exist to communicate ideas to other developers, not just to machines. Formatting and style guides are a **necessary but not sufficient** condition for clean code, so delegate them entirely to automated tools in the CI build and spend human review time on design and meaning.

## Frameworks Introduced
- **Necessary but not sufficient (formatting vs. clean code)**: Code can be 100% PEP-8 compliant and still be unmaintainable. Clean code is about readability, maintainability, keeping technical debt to a minimum, and communicating intent.
  - When to use: Deciding where to spend review effort and what to automate.
  - How: (1) Adopt a coding guideline (PEP-8 or an adaptation of it) and write it down for the team. (2) Encode it in tool configuration files kept under version control. (3) Make the CI build fail when checks fail. (4) In code review, ask only the human questions: Is this easy to understand and follow? Does it speak in terms of the domain of the problem? Could a new team member work with it effectively?
  - **Why it works / failure mode**: Automated checks turn style debates into an objective pass/fail, so no reviewer has to repeat the same PEP-8 comments. Failure mode: treating a green linter as proof of quality. Tools catch layout and type mistakes, not bad abstractions.
- **Technical debt (two directions)**: Problems in the software that result from a compromise or bad decision. Look at it from the present to the past (are today's problems caused by previously written bad code?) and from the present to the future (what problems does today's shortcut create?).
  - When to use: Arguing for refactoring, estimating delivery predictability, judging whether to skip quality.
  - How: Treat the extra cost of changing code later as the *interest* on the debt, which grows every day. A team that keeps stopping to fix code before it can deliver is paying that interest. Some shortcuts are worse than debt: they are time-bombs, such as a mutable default argument that works until some condition finally triggers it.
  - **Why it works / failure mode**: Debt is silent and spread across the whole project, so it raises no alarm until it becomes a show-stopper. A code base full of code smells is rigid, the opposite of agile.
- **Legitimate exceptions to clean code**: Skip quality checks only for code nobody will ever have to read again: hackathons, one-off scripts, code competitions, proofs of concept, prototypes that will really be thrown away, and legacy projects that are certain to be decommissioned soon.
  - How: Check the premise that the code needs no maintenance. If a project is in maintenance mode but will *not* be deprecated, paying off its debt is still worth it, because a bug will eventually need fixing.
- **The `make checklist` pipeline**: One Makefile target that every developer and the CI build run: lint/format check, then type check, then tests. If any step fails, the whole process fails.

## Key Concepts
- **Clean code**: Code that other engineers can read and maintain. Only professionals can judge it, not tools.
- **PEP-8**: Python's main style guide (spacing, naming, line length). It is the baseline; projects may adapt parts of it, such as line length.
- **Searchability**: PEP-8 writes keyword arguments without spaces (`location=current_location`) and assignments with spaces (`current_location = get_location()`), so searching for `location=` and `location =` finds call sites and assignments separately.
- **Docstring**: Documentation embedded in source as a string literal and available at runtime via `__doc__`. It is explanation, not justification. Docstrings are not comments.
- **Annotations (PEP-3107)**: Metadata that hints at the expected types or meaning of arguments and return values, stored in `__annotations__`. Python does not enforce them.
- **Type hinting (PEP-484)**: Checking types through annotations with external tools. Python "will remain a dynamically typed language".
- **Type alias**: A named type such as `Seconds = float` or `Client = Tuple[int, str]`. It adds domain meaning and gives you one place to change the representation.
- **mypy / pytype**: Static type checkers. pytype also infers whether the code will be correct at runtime, so it tolerates temporary type violations.
- **pylint**: A strict, configurable linter that goes beyond PEP-8 (missing docstrings, too many parameters). You configure it in `pylintrc`, and you can extend it with plugins.
- **black**: A deterministic, nearly unconfigurable formatter that formats to a stricter subset of PEP-8. It does not support partial formatting.
- **yapf**: A highly configurable formatter that supports partial (line-range) formatting.

## Mental Models
- **Think of the code as the road**: The car on the road is your delivery pace. On a smooth road (clean code) you can estimate arrival. On a broken road you keep stopping to move rocks (technical debt), so you can't make reliable estimates.
- **Think of experienced developers as chess masters (Perceptions in Chess, 1973)**: Masters beat novices only on positions that follow real-game patterns, and they do no better on random positions. Consistent code lets experts see patterns and spot anomalies. Inconsistent code reduces everyone to a novice.
- **Use annotations for types and docstrings for the data's shape**: Annotations replace the type information that docstrings used to carry. That frees the docstring for behavior, examples of nested or dynamic data, and the exceptions a function raises.
- **Software is only useful to the degree it can be easily changed**: Requirements are rarely frozen, and code that can't change becomes useless.

## Anti-patterns
- **Comments that explain unclear code**: "Comments in code are a symptom of our inability to express our code correctly." Before writing a comment, try a better name or a new function instead.
- **Commented-out code**: Delete it mercilessly. Version control keeps it, and leaving it around pollutes the knowledge the code carries with contradictions.
- **Redundant docstrings on trivial functions**: Docstrings need constant manual maintenance. Skip them when the function is simple and self-explanatory.
- **Overly generic type annotations**: `Iterable[str]` lets `broadcast_notification("welcome", "user1@domain.com")` pass mypy, and the function then iterates characters as if they were emails. Narrower types catch the bug.
- **Large `try/except` blocks**: Keep them minimal (PEP-8). A larger error surface makes it more likely you swallow an exception and mask a bug.
- **Intermediate invalid states**: Even if pytype tolerates them, don't break the invariants your types declare.
- **Manual style policing in reviews**: It wastes reviewer attention. Make the build fail instead.

## Code Examples
```python
Seconds = float

def launch_task(delay: Seconds):
    ...

from typing import Tuple
Client = Tuple[int, str]

def process_clients(clients: list[Client]):
    ...
```
- **What it demonstrates**: Type aliases as small domain abstractions. The annotation stays correct when `Client` later becomes a class.

```python
def broadcast_notification(
    message: str,
    relevant_user_emails: Iterable[str]
):
    for email in relevant_user_emails:
        logger.info("Sending %r to %r", message, email)
```
- **What it demonstrates**: The annotation is too loose, because a `str` is also an `Iterable[str]`. Restricting it to `Union[List[str], Tuple[str]]` makes mypy report `incompatible type "str"`.

```python
from dataclasses import dataclass

@dataclass
class Point:
    lat: float
    long: float

# >>> Point.__annotations__
# {'lat': <class 'float'>, 'long': <class 'float'>}
```
- **What it demonstrates**: Annotations (PEP-526) plus `@dataclass` (PEP-557) declare instance attributes without writing `__init__`.

## Reference Tables
| Tool | Purpose | Key trait |
|---|---|---|
| mypy | Static type checking | Main tool. Silence false positives with `# type: ignore` |
| pytype | Static type checking | Interprets runtime correctness and tolerates temporary violations |
| pycodestyle / flake8 | PEP-8 compliance | Report each violating line. flake8 can also rewrite code |
| pylint | Broad linting beyond PEP-8 | Strict. Configured via `pylintrc`, e.g. `[DESIGN] disable=missing-function-docstring`. Plugins allowed |
| Coala | Multi-language checks | Suggests auto-fix patches. Supports custom modules |
| black | Formatter | Deterministic, all-or-nothing. `--check` mode for CI. `black -l 79 *.py` |
| yapf | Formatter | Configurable, partial (line-range) formatting. Good for legacy repos |
| Sphinx + autodoc | Docs generation | Builds documentation pages from docstrings |

| Adopting black on a legacy repo | Trade-off |
|---|---|
| One milestone PR that reformats everything | Noise. Pollutes version-control history |
| Rewrite history, applying black to every commit | Looks clean from the start, but everyone must refresh their clones, and it is slow with many commits |
| Use yapf on changed regions (pre-commit hook) | Converges gradually without a big-bang change |

## Worked Example
**Making a docstring earn its place.** Start with `def data_from_response(response: dict) -> dict:`. It raises `ValueError` if `response["status"] != 200` and otherwise returns `{"data": response["payload"]}`. The annotations say "dict in, dict out" and nothing more. Add a docstring that shows the data's shape:

```python
def data_from_response(response: dict) -> dict:
    """If the response is OK, return its payload.

    - response: A dict like::

    {
        "status": 200, # <int>
        "timestamp": "....", # ISO format string of the current date time
        "payload": { ... } # dict with the returned data
    }

    - Returns a dictionary like::

    {"data": { .. } }

    - Raises:
    - ValueError if the HTTP status is != 200
    """
    if response["status"] != 200:
        raise ValueError
    return {"data": response["payload"]}
```
The readers now know the keys, their types, and the failure mode. The example data is also ready to use as unit-test input. The cost is verbosity and ongoing maintenance.

**Tool pipeline.** The Makefile targets are: `typehint` (`mypy --ignore-missing-imports src/`), `test` (`pytest tests/`), `lint` (`pylint src/`), `checklist: lint typehint test`, plus `black` and `clean`. CI calls `make checklist`, which keeps CI configuration minimal. If you later swap tools (yapf to black), `make format` still works for everyone.

## Key Takeaways
1. The "language" in programming language is for other developers. Developers spend far more time reading code than writing it.
2. Technical debt is silent, compounds like interest, and makes a team rigid instead of agile.
3. Skip quality only for code that truly won't be maintained, and verify that premise.
4. A written coding guideline (PEP-8-based) is the bare minimum. Enforce it with tools that fail the CI build.
5. Prefer docstrings and annotations to comments. Docstrings document design and data shapes, and annotations document types. They complement each other.
6. Keep type annotations specific enough that checkers can catch real bugs.
7. Use black on new repos. On legacy repos where all-or-nothing formatting is unacceptable, use yapf.

## Connects To
- **Ch 2**: Moves from layout to idiomatic, "Pythonic" code. It covers the dataclass and the mutable-default-argument time-bomb in depth.
- **Ch 3**: General traits of good code (KIS, DRY, contracts) that tools can't judge.
- **Ch 4**: Annotations declare interfaces for dependency injection.
- **Ch 8**: Docstring examples feed unit tests, and tests act as actionable documentation. Covers refactoring to pay down debt.
- **Ch 9**: Annotations help decouple design patterns from concrete implementations.
- **Code Complete / Perceptions in Chess**: The pattern-recognition argument for consistency.
- **Go's `go fmt`**: The precedent for a canonical formatter like black.
