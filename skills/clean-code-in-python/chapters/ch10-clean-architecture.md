# Chapter 10: Clean Architecture

## Core Idea
The principles of clean code apply at every level. Separation of concerns, abstraction, dependency inversion and intention revealing scale up from functions to components and services. Clean code is the foundation without which no architecture survives.

## Frameworks Introduced
- **Layers of abstraction / hexagonal architecture (HEX)**: Insulate the core of the application from external dependencies you don't control. Each dependency must conform to an API your application defines, and never the other way round.
  - When to use: Any boundary with things that can change: databases, ORMs, web frameworks, external services.
  - How: (1) Define pure domain objects for the business rules, with no ORM models or framework objects. (2) Wrap each technical detail in its own package or layer, such as `storage` or `web`, that exposes domain objects. (3) Put an adapter between the third-party API and your API. An ORM is itself a dependency, not the abstraction. (4) Make sure imports flow only toward the kernel: the application imports `storage`, and `storage` never imports the application. (5) Give packages names that don't reveal technology.
  - Why it works / failure mode: The kernel of business logic is protected from change. To swap a query, an ORM or a database you only rewrite `DeliveryStatusQuery.get()`, as long as it still returns a `DeliveryOrder`. It fails when the dependency arrow is inverted, for example when the database or abstraction layer knows about application logic. Abstractions also leak: interface traits such as `async` cannot be hidden.
- **Screaming architecture (SCREAM) / intention revealing**: "Good architecture should reveal the intent of the system it entails. It should not mention the tools it's built with."
  - When to use: When you name components or packages, and when you review the top-level layout.
  - How: Reading the application code should tell you what the system does (get the delivery status). It should not tell you whether the data comes from SQL, NoSQL or another service, nor which web framework is in use. Defer details as much as possible.
  - Why it works / failure mode: The code becomes declarative: it states the problem, not the steps. If you can't name the framework from the application code, the encapsulation worked.
- **Component packaging (library vs service)**: Choose between a Python package and a service (microservice in a Docker container) for each cohesive component.
  - When to use: You are deciding how to reuse logic or split a system.
  - How: Use a package when consumers are in the same language and you want code reuse plus conceptual integrity, meaning one reference way of doing something (a safe tar extractor, a config parser, a client library for your service). Use a service when you need total decoupling: different languages or frameworks, independent deployment, isolated testing. Microservices also bring strong contracts, SLAs/SLOs and latency from network I/O.
- **Repeatable dependency baseline**: Always know the full, pinned list of packages and versions that you ship.
  - How: (1) In `setup.py`, declare version ranges that stop below the next major version (`"sanic>=20,<21"`). (2) Compile the full transitive tree with `pip-compile setup.py` and put the resulting `requirements.txt` under version control. (3) In the Dockerfile, install only from `requirements.txt`. (4) To upgrade, re-run with `-U`. (5) Point all builds at an internal package server. (6) Automate pull requests for new versions and security checks, then merge when CI is green. (7) Bump your own artifact's version according to PEP-440 when its dependencies change.

## Key Concepts
- **Quality attributes**: Architectural traits such as scalability, security, performance and endurance. Operability, CI and ease of release also count.
- **Component (architecture)**: Any working unit of the system that can be released or deployed on its own cycle, whether a package or a service.
- **Separation of Concerns (SoC)**: Distribute responsibilities across cohesive, loosely coupled components so that each new requirement has a single correct place to change.
- **Adapter (architectural)**: An object or package that adapts an external implementation, such as a framework or DB driver, to the API the application defines. `View` in the `web` package is an adapter built by inheritance.
- **Dependency flow**: Dependencies point only toward the kernel of business rules, as you can trace in the import statements.
- **Conceptual integrity**: A library is the single point of reference for how something is done across teams.
- **Baseline**: The complete list of delivered packages and their versions. It makes builds repeatable and lets you pinpoint a bad dependency.
- **Entry point (`console_scripts`)**: A command placed in the virtualenv's `bin/` that runs a given function in the full environment, for example `"status-service = statusweb.service:main"`.
- **Declarative vs imperative**: Declare what you want (the delivery status for an ID) instead of spelling out connect, query, parse and load.
- **Outdated dependencies as technical debt**: You miss features and security patches, and the gap is harder to close the longer you wait.

## Mental Models
- Think of architecture as **clean code scaled up**: "Keep in mind good design principles when looking at the big picture." A monolith that owns everything is the architectural version of a god object.
- Think of the **ORM as a dependency, not an abstraction**. Put your own layer above it, so that whether it uses an ORM underneath is a coincidence.
- Use **packages for reuse and containers for services**. Packages unify criteria, and containers deliver small components with a clear purpose that run the same way in every environment.
- Remember that **principles are not laws**: "practicality beats purity." When abstracting from a framework is impossible or impractical, accept it.

## Anti-patterns
- **A single component owning everything (monolith as source of truth)**: Changes are hard to isolate and testing is ineffective.
- **Treating the ORM or framework as your abstraction**: It couples the domain to a library you don't control and makes it harder to replace later.
- **Reversed dependencies**: If storage or the database knows the application logic, they are coupled.
- **A microservice by reflex for shared code**: You pay for latency, contracts and SLAs when a library would do. Use a service only if consumers are in different languages or need independent deployment.
- **Unpinned or untracked transitive dependencies; relying on public PyPI or VCS**: Builds are not repeatable, you depend on someone else's availability and good faith (npm left-pad, REGISTER01), and internal IP can't be published publicly.
- **Shipping tests or fixtures in the package; mixing runtime and dev dependencies**: The production image becomes bloated and fragile.
- **Delaying upgrades**: It accumulates technical debt and unpatched vulnerabilities.

## Code Examples
```python
class DispatchedOrder:
    """An order that was just created and notified to start its delivery."""

    status = "dispatched"

    def __init__(self, when):
        self._when = when

    def message(self) -> dict:
        return {
            "status": self.status,
            "msg": "Order was dispatched on {0}".format(
                self._when.isoformat()
            ),
        }

class DeliveryOrder:
    def __init__(
        self,
        delivery_id: str,
        status: Union[DispatchedOrder, OrderInTransit, OrderDelivered],
    ) -> None:
        self._delivery_id = delivery_id
        self._status = status

    def message(self) -> dict:
        return {"id": self._delivery_id, **self._status.message()}
```
- **What it demonstrates**: Pure domain models with no framework or ORM ties. The status is a polymorphic collaborator (`OrderInTransit` and `OrderDelivered` follow the same shape).

```python
from storage import DBClient, DeliveryStatusQuery, OrderNotFoundError
from web import NotFound, View, app, register_route

class DeliveryView(View):
    async def _get(self, request, delivery_id: int):
        dsq = DeliveryStatusQuery(int(delivery_id), await DBClient())
        try:
            result = await dsq.get()
        except OrderNotFoundError as e:
            raise NotFound(str(e)) from e
        return result.message()

register_route(DeliveryView, "/status/<delivery_id:int>")
```
- **What it demonstrates**: Screaming, declarative application code. You can't tell which web framework or database is used. Dependencies flow inward, and the storage client is injected.

```dockerfile
FROM python:3.9-slim-buster
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python-dev \
        gcc \
        musl-dev \
        make \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ADD . /app

RUN pip install /app/libs/web /app/libs/storage
RUN pip install /app

EXPOSE 8080
CMD ["/usr/local/bin/status-service"]
```
- **What it demonstrates**: A service delivered as a container. The image installs OS-level dependencies, then the internal packages, then the application, and `CMD` runs the `console_scripts` entry point.

## Reference Tables
| Criterion | Python package (library) | Service (microservice / container) |
|---|---|---|
| Purpose | Reuse code, conceptual integrity | Deliver an application or service with a small, clear purpose |
| Language constraint | Consumers must be Python | Any language or framework |
| Deployment | Bundled into the consumer | Independent deployment and testing |
| Cost | More rigid; a possible single point of failure | Strong contracts, SLAs/SLOs, network latency (HTTP/gRPC) |
| Performance | Efficient (no I/O hop) | Slower due to remote calls |

| Packaging rule | Reason |
|---|---|
| Put sources under `src/` and use `find_packages(where="src/")` | Platform-independent; no local files or tests leak into the release |
| Don't ship unit tests or fixtures | The production image doesn't need them |
| Separate runtime from dev dependencies | Different needs |
| Add entry points for the most-used commands | They run in the full venv context without activating it |
| Match the `name=` in `setup.py` to the import name | `pip install apptool` maps to `from apptool import ...` |
| Fail early in `setup.py` when OS libraries are missing | Gives a helpful error at install time |

## Worked Example
**Delivery-status service.** A food-delivery app needs a REST endpoint that returns the JSON status of an order. The service has two concerns, fetching the order (from a DB, though that is a detail) and presenting it as JSON over HTTP. Both are pushed into packages: `storage` wraps the DB and returns `DeliveryOrder` domain objects, and `web` adapts a web framework by exposing `View`, `NotFound` and `register_route`. The `statusweb` application imports both, defines `DeliveryView`, and declares `install_requires=["web==0.1.0", "storage==0.1.0"]` plus the `status-service` entry point. A Dockerfile builds the image. `curl http://localhost:5000/status/1` returns `{"id":1,"status":"dispatched","msg":"Order was dispatched on ..."}`.

Analysis:
- **Dependency flow**: The application imports from `storage` and never the reverse. Any storage only needs to provide an object with an async `get()` that returns a `DeliveryOrder`, so the dependency is inverted.
- **Change tolerance**: You can swap the query, ORM or database without touching the application. Moving REST to GraphQL or gRPC only changes glue code.
- **Limitations**: The `async` interface is a hard constraint that cannot be abstracted away, and some framework features will eventually seep in.
- **Testability**: Pure domain objects make unit tests simple without a DB, adapters stay thin, and components can be mocked for component tests. Integration tests across all components are still needed (the testing pyramid).

## Key Takeaways
1. Clean code is the cornerstone of a clean architecture. A badly written codebase fails however good its architecture is.
2. Separate concerns into cohesive components, and decide deliberately whether each one should be a package or a service.
3. Insulate the domain with your own abstraction layers and adapters. An ORM or framework is a dependency, not an abstraction.
4. Dependencies must flow toward the business-rule kernel. Check this through the import statements.
5. Architecture should scream its intent. If the application code doesn't reveal the tools, the details are properly encapsulated.
6. Make builds repeatable: use version ranges in `setup.py`, a compiled and versioned `requirements.txt`, an internal package index and automated upgrade PRs.
7. These are principles, not laws: practicality beats purity.

## Connects To
- **Ch 3**: Separation of concerns, cohesion/coupling and DRY reappear at system scale. Conceptual integrity extends DRY across teams.
- **Ch 4**: The DIP becomes architectural dependency inversion between layers.
- **Ch 7**: The `async` interface leaks through the abstraction boundary.
- **Ch 8**: The testing pyramid (unit, then component, then integration) shapes how you test components.
- **Ch 9**: The adapter pattern implements the layer boundaries, and the facade pattern guides the layout of `__init__.py` and packages.
- **Hexagonal Architecture (Alistair Cockburn)** / **The Clean Architecture** and **Screaming Architecture (Robert C. Martin)**: The architectural sources of this chapter.
- **PEP-440 / PEP-508**: The version-numbering and dependency-specification standards.
