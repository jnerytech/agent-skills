# Chapter 11: Unit Testing Anti-patterns

## Core Idea
This chapter aggregates common unit testing anti-patterns — recurring "solutions" that look appropriate on the surface but cause problems later. Each is analyzed through the four attributes of a good test from chapter 4 (protection against regressions, **resistance to refactoring**, fast feedback, maintainability). Nearly all the anti-patterns share one root cause: they couple tests to implementation details by giving tests special privileges or by polluting production code for testing's sake. The remedy is consistently the same — test observable behavior only, and keep test concerns out of production code.

## Frameworks Introduced
*(Minimal — this chapter is mostly anti-patterns.)* The main constructive frameworks are reused from earlier chapters: the publicity/purpose table (ch. 5), the Humble Object pattern (ch. 7), and the four attributes of a good test (ch. 4).

## Key Concepts
- **Test observable behavior only**: The foundational rule. Tests must interact with the SUT exactly as production code does, with no special privileges.
- **Private methods as proxies for implementation details**: Testing private methods isn't bad in itself — it's bad because private methods are usually a proxy for implementation details, and testing those leads to brittleness.
- **Missing abstraction signal**: A private method too complex to cover via the public API indicates a missing abstraction that should be extracted into its own class (and tested directly, often in output-based style).
- **Uncovered private code = dead code or missing abstraction**: The two explanations when public-API tests leave a private method under-covered.
- **Private + observable behavior (the N/A exception)**: Rare methods (e.g. an ORM's private constructor) are both private and part of observable behavior because they fulfill a real contract. Exposing them — or using reflection — is acceptable.
- **Leaking domain knowledge**: Tests that reimplement the production algorithm in their arrange/assert sections.
- **Code pollution**: Adding production code that's only needed for testing.
- **Mocking concrete classes**: Subclass-mocking to preserve part of a class's behavior; a symptom of a Single Responsibility violation.
- **Ambient Context**: A static accessor (e.g. for time) used in place of a framework call; an anti-pattern.
- **Time as explicit dependency**: Injecting time as a service or — preferably — as a plain value.

## Mental Models
- **No special privileges**: If your test reaches into private state or private methods, ask "could production code do this?" If not, you're testing implementation details.
- **Hardcode, don't recompute**: An expected value calculated by the same logic as the SUT proves nothing. Precalculate it *another way* (domain expert, legacy system) and hardcode it.
- **If you must mock part of a class, the class does too much**: The need to preserve some behavior while substituting the rest is a design smell, not a testing technique.
- **Push pollution toward interfaces**: When test-only code is unavoidable in production, an interface (a contract with no executable body) is the least harmful form — you can't have bugs in it.

## Anti-patterns

- **Unit testing private methods**: Exposing methods you'd otherwise keep private just to test them violates "test observable behavior only," couples tests to implementation details, and damages resistance to refactoring (the most important metric). *Instead*: test private methods indirectly through the overarching observable behavior. If coverage is then insufficient, the code is either dead (delete it) or hides a **missing abstraction** (extract it into a separate class, e.g. pulling complex `GetPrice()` out of `Order` into a `PriceCalculator`). *Exception*: a method that is both private AND part of observable behavior (e.g. a private constructor that fulfills an ORM contract) may be made public or reached via reflection without causing brittleness.

- **Exposing private state to enable testing**: Making a private field public so a test can assert on it (e.g. exposing `_status` to verify `Promote()`). Tests then gain special privileges production code doesn't have, coupling them to implementation details. *Instead*: verify the same way production code observes the object. Production doesn't read `_status`; it reads the *discount*. So assert that a new customer has no discount and a promoted one gets 5%. Note: **widening the public API surface for the sake of testability is a bad practice.**

- **Leaking domain knowledge to tests**: Tests that duplicate the production algorithm in their arrange section — e.g. `int expected = value1 + value2;` to test `Calculator.Add`. Such tests score near-zero on resistance to refactoring and cannot distinguish legitimate failures from false positives; when the algorithm changes, the team just copies the new version into the test. *Instead*: hardcode precalculated expected results (`InlineData(1, 3, 4)`), computed by something other than the SUT — ideally a domain expert, or a legacy system you're replacing.

- **Code pollution**: Adding production code that's only needed for testing — often a Boolean switch like `Logger(bool isTestEnvironment)` that disables behavior during tests. It mixes test and production code and raises production maintenance cost, and risks accidentally invoking a test-only code path in production. *Instead*: introduce an `ILogger` interface with a real `Logger` and a `FakeLogger`, and retarget the consumer to the interface. The interface is itself a mild form of pollution, but it's harmless: it's a contract with no code, so it adds no surface area for bugs.

- **Mocking concrete classes**: Subclass-mocking a class (`new Mock<StatisticsCalculator> { CallBase = true }`, overriding a virtual `GetDeliveries()`) to keep some behavior while substituting an out-of-process dependency. *The need to do this is a result of violating the Single Responsibility principle* — the class mixes domain logic (`Calculate`) with talking to the unmanaged dependency (`GetDeliveries`). *Instead*: split it into a `StatisticsCalculator` (pure logic) and a `DeliveryGateway : IDeliveryGateway`. Mock the interface, not a concrete class. This is the **Humble Object** pattern.

- **Testing the current time (Ambient Context)**: Replacing `DateTime.Now` with a static `DateTimeServer.Now => _func()` configured differently for tests vs. production. The Ambient Context pollutes production code, makes testing harder, and its static field is a shared dependency that quietly turns unit tests into integration tests. *Instead*: inject time as an explicit dependency — a service (`IDateTimeServer`) or, preferably, a plain `DateTime` value. Plain values are easier to use in production and to stub in tests.

## Code Examples

Code pollution removed by introducing an interface:
```csharp
public interface ILogger { void Log(string text); }

public class Logger : ILogger {           // Belongs in the production code
    public void Log(string text) { /* Log the text */ }
}
public class FakeLogger : ILogger {       // Belongs in the test code
    public void Log(string text) { /* Do nothing */ }
}
public class Controller {
    public void SomeMethod(ILogger logger) {
        logger.Log("SomeMethod is called");
    }
}
```

Leaking domain knowledge vs. the fix:
```csharp
// Anti-pattern: test reimplements the algorithm
int expected = value1 + value2;          // The leakage
int actual = Calculator.Add(value1, value2);

// Fix: hardcode precalculated results
[Theory]
[InlineData(1, 3, 4)]
[InlineData(11, 33, 44)]
[InlineData(100, 500, 600)]
public void Adding_two_numbers(int value1, int value2, int expected) {
    int actual = Calculator.Add(value1, value2);
    Assert.Equal(expected, actual);
}
```

## Reference Tables

The code's publicity vs. purpose (from ch. 5; explains the private-method exception):

|         | Observable behavior | Implementation detail |
|---------|---------------------|-----------------------|
| Public  | Good                | Bad                   |
| Private | N/A                 | Good                  |

The N/A cell is "rarely" violated: a method can be private yet part of observable behavior when it fulfills a non-public contract (ORM, factory).

## Worked Example
**Passing time as an explicit dependency instead of an Ambient Context.**

Anti-pattern — Ambient Context:
```csharp
public static class DateTimeServer {
    private static Func<DateTime> _func;
    public static DateTime Now => _func();
    public static void Init(Func<DateTime> func) { _func = func; }
}
DateTimeServer.Init(() => DateTime.Now);            // production
DateTimeServer.Init(() => new DateTime(2020, 1, 1)); // unit tests
```
The static `_func` is shared across tests, so any test relying on it depends on global mutable state — they can no longer run in isolation.

Better — inject time explicitly, service at the boundary, value within the operation:
```csharp
public interface IDateTimeServer { DateTime Now { get; } }
public class DateTimeServer : IDateTimeServer {
    public DateTime Now => DateTime.Now;
}

public class InquiryController {
    private readonly DateTimeServer _dateTimeServer;
    public InquiryController(DateTimeServer dateTimeServer) {
        _dateTimeServer = dateTimeServer;       // injected as a service
    }
    public void ApproveInquiry(int id) {
        Inquiry inquiry = GetById(id);
        inquiry.Approve(_dateTimeServer.Now);   // passed onward as a plain value
        SaveInquiry(inquiry);
    }
}
```
Because DI frameworks don't play well with value objects, the compromise is: inject time as a *service* at the start of a business operation, then pass it as a *value* through the rest. The `Inquiry` domain class receives a plain `DateTime`, which is trivial to stub when testing its `Approve` logic.

## Key Takeaways
- Don't test private methods directly; test them through observable behavior. Insufficient coverage means dead code or a missing abstraction — not "expose it."
- Rare exception: methods that are both private and part of a real contract (ORM constructor) may be exposed or reached via reflection.
- Never expose private state for testing. Assert on what production code observes, not on internal fields. Widening the public API for testability is a bad practice.
- Don't leak domain knowledge: hardcode precalculated expected values rather than recomputing them with the SUT's own logic.
- Code pollution (test-only production code, especially Boolean switches) raises maintenance cost; replace switches with interfaces and fakes.
- Mocking a concrete class to keep part of its behavior signals a Single Responsibility violation — split logic from out-of-process communication (Humble Object) and mock the interface.
- Represent time as an explicit dependency, preferring a plain value over a service; the Ambient Context is an anti-pattern.

## Connects To
- **Ch. 4** (four attributes of a good test; black-box vs. white-box testing) — the lens used to judge every anti-pattern here.
- **Ch. 5** (observable behavior vs. implementation details; well-designed API; publicity/purpose table) — the foundation for the private-method and private-state rules.
- **Ch. 6** (styles of unit testing) — extracted abstractions like `PriceCalculator` enable the output-based/functional style.
- **Ch. 7** (Humble Object pattern) — the fix for mocking concrete classes.
- **Ch. 8** (mocking, testing loggers, Ambient Context) — where the logger and Ambient Context examples originate.
