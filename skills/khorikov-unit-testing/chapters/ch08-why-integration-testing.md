# Chapter 8: Why Integration Testing?

## Core Idea
Unit tests verify business logic in isolation, but they can never confirm the system works *as a whole* — how the code glues the domain model to out-of-process dependencies (database, message bus, SMTP). That gap is the job of integration tests: any test that is not a unit test. The chapter's central decision is **which out-of-process dependencies to exercise with real instances and which to replace with mocks**, governed by the distinction between **managed** and **unmanaged dependencies**. The guiding balance is the **Test Pyramid**: cover edge cases cheaply with unit tests, and use a small number of integration tests for one happy path plus edge cases units can't reach.

## Frameworks Introduced (name, when, how)
- **Test Pyramid (revisited)** — when balancing the test suite. Majority = fast/cheap unit tests covering edge cases; minority = slow/expensive integration tests verifying the system as a whole. Shape varies with complexity; trivial apps can flatten to a rectangle (equal unit/integration) or have no unit tests.
- **Managed vs unmanaged dependency classification** — when deciding what to test directly. Use real managed dependencies; mock unmanaged ones.
- **Fail Fast principle** — when an edge case's incorrect execution crashes the app immediately. Throw exceptions to stop the operation early; a viable alternative to writing an integration test.
- **Interfaces with a single implementation rule** — when adding interfaces for dependencies. Only introduce one to enable mocking, i.e. only for unmanaged dependencies.
- **Three-layer architecture** — when structuring a backend: domain model, application services (controllers), infrastructure.

## Key Concepts (5–10)
1. **Integration test = any test that is not a unit test.** It fails at least one of: single behavior, fast, isolated from other tests. In practice it verifies integration with out-of-process dependencies (the controllers quadrant).
2. **Managed dependency** — out-of-process dependency you fully control, accessed *only* through your app; interactions are invisible externally. Example: the application database. Communications with it are *implementation details*.
3. **Unmanaged dependency** — out-of-process dependency other applications also access; interactions are *observable externally*. Examples: SMTP server, message bus. Communications with it are *part of observable behavior*.
4. **Rule of thumb:** use real instances of managed dependencies (verify final state); replace unmanaged dependencies with mocks (verify communication pattern, to preserve backward compatibility).
5. **Longest happy path** — for an integration test pick the path touching the most out-of-process dependencies/side effects; add more tests if no single path covers all.
6. **Fail Fast principle** — stop on any unexpected error (throw exceptions). Shortens the feedback loop and protects persistence state from corruption. Preconditions and config validation at startup are examples.
7. **Dependency that is both managed and unmanaged** — e.g. a shared database. Treat externally-visible tables as unmanaged (mock, preserve communication pattern); treat the rest as managed (verify final state).
8. **Interfaces with a single implementation are not abstractions** — genuine abstractions are *discovered, not invented*, requiring ≥2 implementations. Single-impl interfaces exist only to enable mocking.
9. **Test database state independently of input** — query the DB back through the same code the controller uses (Database, factories), so the test exercises both writes and reads.

## Mental Models
- **Observable behavior vs implementation detail** is the master lens. Anything observable to external parties (unmanaged deps, support logs) must have its *communication pattern* preserved → mock. Anything private (managed deps, diagnostic logs) → verify only the end *state*.
- **Backward compatibility is why you mock unmanaged deps.** Other apps depend on the exact messages; mocks lock that contract against refactoring. The DB has no external contract, so its schema can be refactored freely as long as final state matches.
- **The bar for an integration test is higher than for a unit test:** it must score higher on protection-against-regressions and resistance-to-refactoring to justify its worse maintainability and speed.
- **Genuine abstractions are discovered, not invented** — post factum, once a second implementation actually exists.

## Anti-patterns
- **Mocking managed dependencies**: Replacing a real database with a mock destroys the integration test's resistance to refactoring and weakens protection against regressions. If the DB is the only out-of-process dependency, such a mocked test verifies nothing beyond which repository methods the controller calls — no value over existing unit tests.
- **If you can't use a real managed dependency**: Don't mock it anyway. Write *no* integration tests and rely exclusively on unit testing the domain model. A bad/low-value test is worse than no test.
- **Interfaces with a single implementation for in-process/domain classes (`IUser`)**: A huge red flag — its only use is to mock interactions between domain classes, producing brittle tests coupled to implementation details. Never check interactions between domain classes.
- **Speculative single-impl interfaces "for the future" (OCP)**: Violates YAGNI — opportunity cost plus carrying more code than needed.
- **Excessive layers of indirection**: Blur the controller/domain boundary, breed low-value per-layer tests that mock the layer beneath → poor regression protection and poor refactoring resistance.
- **Circular dependencies (callbacks)**: Add cognitive load; tempt you toward interfaces+mocks. Interfaces only mask the cycle at compile time; it persists at runtime. Break it with a returned value object.
- **Ambient context for loggers (static `LogManager.GetLogger`)**: Hides the dependency and hampers testing; masks root problems (too much logging or too many layers). Inject explicitly.
- **Multiple act sections**: A code smell except when a hard-to-manage out-of-process dependency justifies combining acts; never in a unit test.

## Code Examples
Controller with explicit injection — concrete class for the managed dependency, interface for the unmanaged one:
```csharp
public class UserController
{
    private readonly Database _database;          // A concrete class (managed)
    private readonly IMessageBus _messageBus;     // The interface (unmanaged)

    public UserController(Database database, IMessageBus messageBus)
    {
        _database = database;
        _messageBus = messageBus;
    }

    public string ChangeEmail(int userId, string newEmail)
    {
        /* uses _database and _messageBus */
    }
}
```

Integration test assertions — verify DB *state* (read back independently), verify mock *interaction*:
```csharp
Assert.Equal("OK", result);

object[] userData = db.GetUserById(user.UserId);
User userFromDb = UserFactory.Create(userData);
Assert.Equal("new@gmail.com", userFromDb.Email);
Assert.Equal(UserType.Customer, userFromDb.Type);

object[] companyData = db.GetCompany();
Company companyFromDb = CompanyFactory.Create(companyData);
Assert.Equal(0, companyFromDb.NumberOfEmployees);

messageBusMock.Verify(
    x => x.SendEmailChangedMessage(user.UserId, "new@gmail.com"),
    Times.Once);
```

Breaking a circular dependency by returning a value instead of a callback:
```csharp
public class CheckOutService
{
    public void CheckOut(int orderId)
    {
        var service = new ReportGenerationService();
        Report report = service.GenerateReport(orderId); // returns a value
        /* other work */
    }
}
public class ReportGenerationService
{
    public Report GenerateReport(int orderId) { /* ... */ }
}
```

## Reference Tables

| | Managed dependency | Unmanaged dependency |
|---|---|---|
| Definition | Fully controlled; accessible only via your app | Other apps access it too |
| Visibility of interactions | Not observable externally | Observable externally |
| Communications are | Implementation detail | Part of observable behavior |
| Examples | Application database | SMTP server, message bus |
| In integration tests | Use **real instance**, verify final **state** | Replace with **mock**, verify **interactions** |
| Use an interface? | No — inject concrete class | Yes — interface to enable mocking |

| Test type | Hosting | Out-of-process deps | Managed dep | Unmanaged dep |
|---|---|---|---|---|
| Unit | in-process | none/all mocked | — | mocked |
| Integration | same process | managed only | real, check state | mocked |
| End-to-end | deployed app | all real | check only *through* the app | check directly |

## Worked Example
The sample CRM `ChangeEmail` use case has two out-of-process dependencies, and they fall on opposite sides of the managed/unmanaged line:

1. **Categorize.** The **application database is a managed dependency** — no other system reaches it; external clients only care about final state. → Use a **real instance**. The **message bus is an unmanaged dependency** — its sole purpose is communicating with other systems, so the messages are an external contract. → **Mock it.**

2. **Pick scenarios.** Cover the **longest happy path**: changing from a *corporate* to a *non-corporate* email, which produces the maximum side effects — user type and email change, company's employee count changes (DB), and a message is sent (bus). The only edge case (email can't be changed) is *not* worth an integration test: the controller's `CanChangeEmail()` precondition makes the app **fail fast** if missing, so a unit test on the precondition suffices. Result: a single integration test, `Changing_email_from_corporate_to_non_corporate()`.

3. **Execute.** Arrange via reusable `CreateUser`/`CreateCompany` helpers that insert real rows. Act by calling the controller against the real DB with a mocked bus. Assert by **reading the DB back independently** (query user and company, rebuild via `UserFactory`/`CompanyFactory`, assert their state) — exercising both writes and reads — and by `Verify`-ing the bus mock was called once with the expected message.

4. **End-to-end?** None needed here. Because integration tests include the managed dependency for real and mock only the unmanaged one, they approach end-to-end protection. At most add one overarching E2E test through the longest happy path that checks the message bus directly but verifies DB state *through the application*.

5. **Logging variant.** If business requires logging user-type changes (support logging = observable behavior), don't pollute `User` with a `DomainLogger` call (that turns it into overcomplicated code). Instead raise a `UserTypeChangedEvent` domain event; the controller's `EventDispatcher` converts it into a `_domainLogger.UserTypeHasChanged(...)` call. Then the single integration test mocks `DomainLogger` like any other unmanaged dependency, while diagnostic logging stays untested.

## Key Takeaways
- An integration test is any test that is not a unit test; it verifies integration with out-of-process dependencies and covers the controllers quadrant.
- Follow the **Test Pyramid**: many cheap unit tests for edge cases; few integration tests for one happy path plus units' blind spots. Simple apps flatten the pyramid.
- **Use real managed dependencies (verify state); mock unmanaged dependencies (verify communication pattern).** Managed = invisible to outside (DB); unmanaged = observable (bus, SMTP).
- For a shared DB, split it: external-facing tables are unmanaged (mock), the rest is managed (verify state).
- Apply the **Fail Fast principle** instead of testing edge cases that immediately crash the app; throw exceptions to shorten the feedback loop and protect persisted state.
- **Interfaces with a single implementation are not abstractions**; introduce them only to enable mocking — so only for unmanaged dependencies. Never for domain/in-process classes.
- Improve testability structurally: explicit domain-model boundary, ≤3 layers, no circular dependencies, single act section (except hard out-of-process deps).
- Test **support logging** (observable, business requirement) via a `DomainLogger`; never test **diagnostic logging**; always inject loggers explicitly, never via ambient context.

## Connects To
- **Ch 5 (Mocks and test fragility):** mocking unmanaged dependencies preserves their communication pattern / backward compatibility; mocking managed deps or domain interactions creates brittle tests.
- **Ch 7 (Refactoring toward valuable tests):** the code quadrants (domain model, controllers, trivial, overcomplicated), domain events, and the `CanChangeEmail` precondition reused here.
- **Ch 2 (What is a unit test?):** the three unit-test requirements and the Test Pyramid baseline; E2E as a subset of integration tests.
- **Ch 9 (Mocking best practices) & Ch 10 (Testing the database):** promised improvements to the message-bus mock and DB testing.
- **Ch 11:** interfaces vs base classes for mocking dependencies without an interface.
- **External:** Freeman & Pryce *GOOS* (support vs diagnostic logging); van Deursen & Seemann *DI Principles, Practices, Patterns* (ambient context anti-pattern); YAGNI/OCP.
