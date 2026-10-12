# Chapter 2: What is a unit test?

## Core Idea
A unit test is an automated test that (1) verifies a small piece of code (a *unit*), (2) does it quickly, and (3) does it in an **isolated manner**. The whole chapter hinges on the **isolation issue**: the word "isolation" is interpreted in two incompatible ways, and that single disagreement spawns the **classical school** (a.k.a. Detroit/classicist) and the **London school** (a.k.a. mockist). Khorikov prefers the classical school because mock-heavy London tests tend to be more brittle (couple to implementation details). By chapter's end the unit-test definition is refined to: verifies a single **unit of behavior**, does it quickly, and does it **in isolation from other tests**.

## Frameworks Introduced
- **Classical (Detroit) school**: isolate *unit tests from each other*, not the code. Tests may exercise several real classes at once, as long as none reaches out to a **shared dependency**. A unit is a *unit of behavior* (one or more classes). Use test doubles only for **shared dependencies**.
  - When to use: Khorikov's default; produces more resilient, refactoring-friendly tests.
  - How: build real collaborators in the arrange phase, assert against resulting state; replace only shared/out-of-process dependencies (DB, file system) with doubles.
- **London (mockist) school**: isolate the *system under test (SUT) from its collaborators*. A unit is a class; replace *all but immutable* dependencies with test doubles (mocks).
  - When to use: when you want strict one-class-at-a-time granularity and pinpoint bug location (Khorikov argues these benefits are overstated).
  - How: introduce an interface per collaborator, inject a `Mock<T>`, set up return values, and `Verify` interactions.
- **Test-Driven Development (TDD)**: write a failing test → write just enough code to pass → refactor under the test's protection. London drives **outside-in TDD** (start from high-level tests, mock collaborators, work inward); classical drives **inside-out** (start from domain model, add layers outward).

## Key Concepts
- **isolation issue**: the disputed third attribute of a unit test; root of the classical/London split.
- **test double**: an object that looks/behaves like its release counterpart but is a simplified version that facilitates testing (Meszaros). Overarching term for all fake dependencies.
- **mock**: a special kind of test double that lets you examine *interactions* between SUT and collaborators; a subset of test doubles.
- **shared dependency**: a dependency shared between tests that lets them affect each other's outcome (e.g., static mutable field, database).
- **private dependency**: a dependency that is not shared.
- **out-of-process dependency**: a dependency running outside the app's process; a proxy to data not yet in memory (DB, file system). Usually—but not always—shared.
- **volatile dependency**: a dependency that either requires extra runtime setup beyond a default dev machine (DB, API) *or* exhibits nondeterministic behavior (RNG, current date/time).
- **collaborator**: a dependency that is either shared or mutable (e.g., `Store`, DB-access class); contrast with **value/value object**.
- **value object**: an immutable dependency identified solely by content, no identity (e.g., C# `enum Product`, the number `5`); interchangeable, never mocked.
- **SUT / MUT**: system under test (the class) / method under test (the method called by the test).
- **unit of behavior vs. unit of code**: behavior is meaningful to a business person; code is a class/method. Tests should verify behavior.
- **integration test**: a test that fails at least one of the three unit-test criteria; **end-to-end test** is a subset that exercises all/most out-of-process dependencies.

## Mental Models
- **Dependency hierarchy**: dependency → *shared* OR *private*; private → *mutable* OR *immutable (value object)*. All shared dependencies are mutable, but a mutable dependency is only shared if reused by tests. Classical replaces shared; London additionally replaces private-mutable.
- **Shared ⊃ communication channel**: a dependency is shared only if it gives tests a means to communicate (mutate shared state) and interfere. A read-only API or a fresh-per-test Docker DB is out-of-process but *not* shared.
- **Shared vs. volatile overlap but differ**: DB = shared + volatile; file system = shared but *not* volatile (deterministic, pre-installed); RNG = volatile but *not* shared (new instance per test).
- **Dog story (units of behavior)**: "When I call my dog, he comes right to me" (good, cohesive) vs. listing every leg/head/tail movement (meaningless). Testing individual classes = testing the legs; test the behavior instead.
- **Test the behavior, not the class**: number of classes implementing a behavior is irrelevant—could be many classes or a tiny method.
- **Two reasons to substitute shared dependencies**: (1) isolate tests from each other, (2) speed—shared deps cross the process boundary (DB call ≈ hundreds of ms), pushing tests into integration territory.

## Anti-patterns
- **Mocking a concrete class** instead of an interface (covered in ch. 11).
- **Aiming for granularity / "one class per test"** as a goal—it makes tests verify units of code, obscuring what behavior is checked.
- **Using mocks to test a large interconnected object graph**: hides the real problem. Hard-to-test code is a *negative indicator* of poor design; mocks mask the root cause instead of fixing it.
- **Over-specification**: coupling tests to the SUT's implementation details—the biggest issue with the London school and ubiquitous mocking.

## Code Examples
Classical style — assert against collaborator **state** (real `Store`):
```csharp
[Fact]
public void Purchase_succeeds_when_enough_inventory() {
    var store = new Store();
    store.AddInventory(Product.Shampoo, 10);
    var customer = new Customer();
    bool success = customer.Purchase(store, Product.Shampoo, 5);
    Assert.True(success);
    Assert.Equal(5, store.GetInventory(Product.Shampoo)); // state check
}
```
London style — assert against **interactions** (mocked `IStore`):
```csharp
[Fact]
public void Purchase_succeeds_when_enough_inventory() {
    var storeMock = new Mock<IStore>();
    storeMock.Setup(x => x.HasEnoughInventory(Product.Shampoo, 5)).Returns(true);
    var customer = new Customer();
    bool success = customer.Purchase(storeMock.Object, Product.Shampoo, 5);
    Assert.True(success);
    storeMock.Verify(x => x.RemoveInventory(Product.Shampoo, 5), Times.Once); // interaction check
}
```
Note: `Product.Shampoo` and `5` are value objects—left as real objects, never mocked. (Mocking framework: Moq; alternatives NSubstitute, and Mockito/JMock/EasyMock in Java.)

## Reference Tables
| | Isolation of | A unit is | Uses test doubles for |
|------------------|--------------|-----------------------------|--------------------------------|
| London school | Units | A class | All but immutable dependencies |
| Classical school | Unit tests | A class or a set of classes | Shared dependencies |

Dependency classification:
| Dependency | Shared? | Mutable? | Replace in classical? | Replace in London? |
|------------------------|---------|----------|-----------------------|--------------------|
| Database | Yes | Yes | Yes | Yes |
| `Store` instance | No | Yes | No | Yes |
| `Product` / number `5` | No | No (value object) | No | No |

## Worked Example
**Online store, one use case: a customer purchases a product.** Enough inventory → purchase succeeds and store inventory drops by the amount; not enough → fails and nothing changes. `Customer` is the SUT, `Store` the collaborator.

- *Classical:* arrange a real `Store` with inventory, call `customer.Purchase(store, ...)`, assert on both the boolean output and `store.GetInventory(...)`. The test verifies `Customer` **and** `Store` together—any `Store` bug fails the test. They are not isolated from each other.
- *London:* introduce `IStore`, create `new Mock<IStore>()`, `Setup` `HasEnoughInventory` to return true/false, call `Purchase(storeMock.Object, ...)`, then `Verify` that `RemoveInventory` was called `Times.Once` (success) or `Times.Never` (failure). The mock reacts regardless of any real `Store` state; `Customer` is isolated.

**Why `Store` but not `Product`/`5` is mocked:** only `Store` carries mutable internal state and is a collaborator. `Product` (a C# enum) and `5` are immutable value objects—interchangeable by content—so they're used as-is, exactly as you'd never mock the literal `5`.

## Key Takeaways
- The classical/London split reduces entirely to one question: isolate *the code* (London) or *the tests* (classical)?
- Refined unit-test definition: verifies a single **unit of behavior**, quickly, **in isolation from other tests**.
- Test **behavior**, not classes; the number of classes is irrelevant.
- Replace only **shared dependencies** (classical) for two reasons: test isolation and speed.
- "Shared," "out-of-process," and "volatile" overlap but are distinct—shared requires a mutable communication channel between tests.
- Inability to unit test cheaply is a good negative indicator of design problems; mocks hide rather than fix it.
- Integration test = fails ≥1 unit-test criterion; E2E = integration test covering all/most out-of-process dependencies, run late (build server).

## Connects To
- **Ch. 1**: ability to unit test as a *negative indicator* of code quality; goal = sustainable project growth.
- **Ch. 3**: AAA (arrange-act-assert) structure, xUnit, naming.
- **Ch. 4**: pillars of a good test (resistance to refactoring vs. over-specification).
- **Ch. 5**: mocks vs. stubs, observable behavior vs. implementation details, brittleness of mock-based tests.
- **Ch. 8 & 11**: interfaces for isolation; mocking concrete classes as an anti-pattern; integration testing.
- External: Beck, *TDD by Example* (classical); Freeman & Pryce, *Growing Object-Oriented Software, Guided by Tests* (London); van Deursen & Seemann, *Dependency Injection* (dependency management); Meszaros, *xUnit Test Patterns* (test doubles).
