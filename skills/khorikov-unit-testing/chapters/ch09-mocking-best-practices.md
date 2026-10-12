# Chapter 9: Mocking Best Practices

## Core Idea
Limiting mocks to unmanaged dependencies gets you two-thirds of the way to high-value integration tests. This chapter delivers the remaining guidelines that max out a mock's protection against regressions and resistance to refactoring: **mock at the system edges**, replace mocks with **spies** for edge classes, never assert against production code, **verify the number of calls**, use mocks in integration tests only, and **mock types you own**.

## Frameworks Introduced (name, when, how)
- **Verify interactions at the system edges** — when picking *which* type to mock. Mock the **last** type in the chain between the controller and the unmanaged dependency (e.g. `IBus`, not `IMessageBus`).
- **Spy (handwritten mock)** — when the mocked type sits at the system edge. Write a manual test double that records calls and exposes a fluent assertion API.
- **Mock types you own (Freeman/Pryce)** — when interacting with a third-party library that reaches an unmanaged dependency. Wrap it in your own adapter; mock the adapter.

## Key Concepts (5–10)
1. **Edge of the system** — the boundary type that actually talks to the external world. Mocking it executes more production code (more regression protection) and detaches the test from internals (more refactoring resistance).
2. **Two wrappers, two jobs** — `IBus` hides the external library's complexity; `IMessageBus` holds domain-specific messages in one place. Same split as `ILogger` (generic) vs `IDomainLogger` (business-specific). Keep them separate.
3. **Observable side effect** — external systems consume *text messages*, not calls to your `MessageBus` class. Asserting on the actual message text survives refactorings; asserting on a method call does not.
4. **Spies beat mocks at the edge** — they let you reuse assertion code, shrinking and clarifying the test via a fluent interface.
5. **Don't assert against production code** — `BusSpy` is test code; `MessageBus` is production code. A spy is an independent auditor; a mock on `IMessageBus` over-trusts production code (risking **tautology tests**).
6. **Verify the number of calls** — confirm both the existence of expected calls (`Times.Once`) and the absence of unexpected ones (`VerifyNoOtherCalls()`).
7. **Logging is the exception** — for logs, message *structure* isn't critical, only existence and content. Mocking `IDomainLogger` directly (not `ILogger` at the edge) is enough.
8. **Mocks are for integration tests only** — controllers (orchestration) talk to unmanaged dependencies; domain model (complexity) does not. So unit tests on the domain model use no mocks.
9. **No "one mock per test" rule** — a unit is a unit of *behavior*, not code. Mock count is dictated solely by the number of unmanaged dependencies in the operation.

## Mental Models
- **Auditor:** a good test, like an auditor, double-checks the auditee instead of taking its word at face value. The spy is your independent checkpoint.
- **Last stage before it leaves:** a call passes through several stages before exiting your app — pick the last one to guarantee backward compatibility with external systems.
- **Anti-corruption layer:** owned adapters restrict a library upgrade's ripple effect to a single class, expose only needed features, and speak your domain language.

## Anti-patterns
- Mocking an intermediate type (`IMessageBus`, `EventDispatcher`) instead of the edge type (`IBus`) — sacrifices regression protection and refactoring resistance.
- Asserting that a method on a custom class was called rather than verifying the actual text/message sent externally.
- Reusing production constants/classes in assertions — produces tautology tests that verify nothing.
- Verifying a call exists but not that it happened *exactly once* (missing absence-of-unexpected-calls check).
- Using mocks in unit tests on the domain model.
- Enforcing "only one mock per test."
- Mocking third-party interfaces directly instead of your own adapter.
- Wrapping in-process or managed dependencies (date/time APIs, ORMs) — unnecessary; wrapping is rarely worth it for anything but unmanaged dependencies.

## Code Examples
Edge type vs intermediate wrapper:
```csharp
public interface IMessageBus { void SendEmailChangedMessage(int userId, string newEmail); }
public class MessageBus : IMessageBus {
    private readonly IBus _bus;
    public void SendEmailChangedMessage(int userId, string newEmail) {
        _bus.Send("Type: USER EMAIL CHANGED; " + $"Id: {userId}; " + $"NewEmail: {newEmail}");
    }
}
public interface IBus { void Send(string message); } // <-- system edge
```

Spy with a fluent assertion API:
```csharp
public class BusSpy : IBus {
    private List<string> _sentMessages = new List<string>();
    public void Send(string message) => _sentMessages.Add(message);

    public BusSpy ShouldSendNumberOfMessages(int number) {
        Assert.Equal(number, _sentMessages.Count);
        return this;
    }
    public BusSpy WithEmailChangedMessage(int userId, string newEmail) {
        string message = "Type: USER EMAIL CHANGED; " + $"Id: {userId}; " + $"NewEmail: {newEmail}";
        Assert.Contains(_sentMessages, x => x == message);
        return this;
    }
}
```

Verifying number of calls (Moq vs spy):
```csharp
messageBusMock.Verify(x => x.SendEmailChangedMessage(user.UserId, "new@gmail.com"), Times.Once);
messageBusMock.VerifyNoOtherCalls();

// BusSpy: ShouldSendNumberOfMessages(1) encompasses both Times.Once AND VerifyNoOtherCalls()
busSpy.ShouldSendNumberOfMessages(1)
      .WithEmailChangedMessage(user.UserId, "new@gmail.com");
```

## Reference Tables

| Dependency type | Mock it? | Where? |
|---|---|---|
| Unmanaged (message bus, SMTP, third-party API) | Yes | At the system edge (`IBus`) |
| Unmanaged logging | Yes | At the domain wrapper (`IDomainLogger`) — structure not critical |
| Managed (your own DB) | No | Use the real thing |
| In-process / in-memory (date/time, ORM) | No | Use as-is |

| Test double | Written by | Best for |
|---|---|---|
| Mock | Mocking framework (Moq) | Quick setup |
| Spy | Hand (manual) | Edge classes — reusable, readable assertions |

## Worked Example
**Retargeting a mock to the system edge, then replacing it with a spy.**

Starting point: the integration test mocks `IMessageBus` and asserts `SendEmailChangedMessage(...)` was called. Problem: `IMessageBus` is an intermediate wrapper; the assertion checks a call to *our own class*, which external systems never see.

Step 1 — move the mock to the edge. Replace the mock on `IMessageBus` with a mock on `IBus`, and feed it through a real `MessageBus`:
```csharp
var busMock = new Mock<IBus>();
var messageBus = new MessageBus(busMock.Object);     // concrete class, not the interface
var sut = new UserController(db, messageBus, loggerMock.Object);
// ...
busMock.Verify(x => x.Send(
    "Type: USER EMAIL CHANGED; " + $"Id: {user.UserId}; " + "NewEmail: new@gmail.com"),
    Times.Once);
```
Now the test runs *more* production code (`MessageBus` is exercised, not stubbed) and asserts the actual text sent externally. `IMessageBus` had a single implementation and existed only to be mocked — it can now be deleted. The test stays green through any refactoring that preserves the message structure.

Step 2 — swap the mock for a `BusSpy`. The spy records sent messages and offers a chainable, plain-English assertion:
```csharp
var busSpy = new BusSpy();
var messageBus = new MessageBus(busSpy);
var sut = new UserController(db, messageBus, loggerMock.Object);
// ...
busSpy.ShouldSendNumberOfMessages(1)
      .WithEmailChangedMessage(user.UserId, "new@gmail.com");
```
This *looks* like the original `IMessageBus` mock, but the crucial difference is that `BusSpy` is test code while `MessageBus` is production code — the spy is an independent auditor of the message structure. `IDomainLogger` stays mocked as-is (not retargeted to `ILogger`) because log structure doesn't demand strict backward compatibility.

## Key Takeaways
- Mock the **last** type in the chain before an unmanaged dependency; this maximizes both regression protection and refactoring resistance.
- Assert on the **observable side effect** (the message text), not on calls to your own classes.
- Use a **spy** for edge classes — handwritten, fluent, reusable assertions.
- Never make assertions against production code; duplicate literals/constants into tests to avoid **tautology tests**.
- Always **verify the number of calls**: expected calls exist *and* unexpected ones are absent.
- Mocks belong in **integration tests** only; mock count is irrelevant (driven by number of unmanaged dependencies).
- **Mock only types you own** — wrap third-party libraries in adapters; this doesn't apply to in-process or managed dependencies.

## Connects To
- **Ch. 5** (test doubles): definitions of mock vs spy; mocks examine interactions.
- **Ch. 8** (integration testing): mock only unmanaged dependencies; `IDomainLogger`/`ILogger` split.
- **Ch. 7** (separating business logic & orchestration): domain model vs controllers → why mocks are integration-only.
- **Ch. 4** (four pillars): protection against regressions = amount of code executed; resistance to refactoring.
- **Ch. 2** (what is a unit test): a unit = unit of behavior, not unit of code → no "one mock per test."
- External: *Growing Object-Oriented Software, Guided by Tests* (Freeman & Pryce) — "mock types you own"; *Domain-Driven Design* (Evans) — anti-corruption layer.
