# Chapter 5: Mocks and Test Fragility

## Core Idea
Mocks have a deep, almost inevitable connection to test fragility. The key to using them well is recognizing that **mocks should verify only inter-system communications that cross the application boundary and whose side effects are visible to the external world**. Verifying communications between classes *inside* your application couples tests to implementation details, destroying their resistance to refactoring. This chapter applies the four-attribute frame of reference from Chapter 4 to dissect exactly when mocking helps and when it hurts.

## Frameworks Introduced (name, when, how)
- **Test double taxonomy (mock vs stub)** — *when:* deciding how to substitute a dependency. *how:* group Meszaros's five variations (dummy, stub, spy, mock, fake) into two types. Mocks emulate **and examine** outcoming interactions (calls that change a dependency's state). Stubs only emulate incoming interactions (calls that fetch input data). Never assert on stubs.
- **Command Query Separation (CQS)** — *when:* designing methods and choosing test-double type. *how:* every method is either a command (side effect, returns `void`) or a query (returns a value, side-effect free), never both. Test doubles substituting commands → mocks; substituting queries → stubs.
- **Observable behavior vs implementation detail** — *when:* deciding what a test may assert. *how:* code is observable behavior only if it exposes an operation or state that helps a client achieve a goal; everything else is an implementation detail to hide.
- **Hexagonal architecture (Cockburn)** — *when:* structuring the app to separate business logic from orchestration. *how:* a hexagon = domain layer (business logic) + application services layer (orchestration); hexagons interact with other hexagons (external apps).
- **Intra-system vs inter-system communications** — *when:* deciding whether a collaboration may be mocked. *how:* intra-system = between classes inside the app (implementation detail, don't mock); inter-system = across the app boundary (observable behavior, mock it).

## Key Concepts (5–10)
1. **Test double** — overarching term for any non-production-ready fake dependency (from "stunt double").
2. **Mock vs stub** — mocks examine outcoming (state-changing) calls; stubs emulate incoming (input-providing) calls. The five variations collapse to these two; spies are handwritten mocks, dummies/fakes are stub-like.
3. **Mock (the tool) vs mock (the test double)** — the `Mock<T>` class from a library is a tool that can create *either* a mock or a stub; don't conflate them.
4. **Don't assert interactions with stubs** — a call to a stub is a means, not an end result. Asserting it is **overspecification** and causes fragility.
5. **Observable behavior is not the same as a public API** — two independent dimensions: public/private API and observable behavior/implementation detail. A well-designed API makes these coincide.
6. **Leaking implementation details** — when the public API extends beyond observable behavior. Rule of thumb: if achieving one goal needs more than one operation on a class, it likely leaks.
7. **Encapsulation & tell-don't-ask** — hide details and bundle data with operations to protect invariants; leaking details often breaches encapsulation.
8. **Fractal nature of behavior/tests** — well-designed API applies to a whole layer or a single class; tests verify the same behavior at different levels (use case → subgoal).
9. **Inter-system = backward-compatible contract** — the communication pattern with external apps must survive refactoring, so mocking it is legitimate.
10. **Not all out-of-process dependencies should be mocked** — an out-of-process dependency accessible *only* through your app (e.g., the application database) acts as part of the app; mocking it produces brittle tests.

## Mental Models
- **"Whats, not hows."** Tests must verify the end result (observable behavior), not the steps taken to produce it.
- **Neurons in the brain.** Verifying communications between classes is like deriving a person's behavior by measuring signals between neurons — too granular. The client cares only about the help provided, not which neurons fired.
- **Behavior flows inward.** The external client's coarse-grained goal is translated into subgoals achieved by domain classes; every piece of observable behavior traces recursively back to a business use case.
- **Hexagon talking to hexagons.** Inside the hexagon = implementation detail. Lines crossing between hexagons = observable behavior / contract.
- **Ask a question, don't change the answer.** CQS: queries must be side-effect free so a method's signature alone tells you what it does.

## Anti-patterns
- **Asserting on implementation details**: Verifying intra-system calls (e.g., `storeMock.Verify(x => x.RemoveInventory(...))` between two domain classes) couples the test to *how* the result is produced, not *what* is produced. The test breaks on harmless refactoring.
- **Asserting interactions with stubs (overspecification)**: e.g., `stub.Verify(x => x.GetNumberOfUsers(), Times.Once)`. The call fetches input; it is not part of the end result. Easy to spot — tests should never check any interaction with a stub.
- **Leaking implementation details to the public API**: making `NormalizeName()` public so the client must call it before setting `Name`. Forces clients through extra operations and lets them bypass invariants.
- **Indiscriminate mocking (London school)**: mocking all but immutable dependencies without distinguishing intra- from inter-system communications, so tests check class-to-class collaboration and lose resistance to refactoring.
- **Mocking application-only out-of-process dependencies**: mocking an application database that no external system can observe; tests turn red on harmless schema/stored-proc changes. Treat the database and app as one system.

## Code Examples

**Mock (the tool) creating a mock (the test double) — verifies an outcoming command:**
```csharp
[Fact]
public void Sending_a_greetings_email()
{
    var mock = new Mock<IEmailGateway>();
    var sut = new Controller(mock.Object);
    sut.GreetUser("user@email.com");
    mock.Verify(
        x => x.SendGreetingsEmail("user@email.com"),
        Times.Once);
}
```

**Same tool creating a stub — emulates an incoming query, never asserted:**
```csharp
[Fact]
public void Creating_a_report()
{
    var stub = new Mock<IDatabase>();
    stub.Setup(x => x.GetNumberOfUsers()).Returns(10);
    var sut = new Controller(stub.Object);
    Report report = sut.CreateReport();
    Assert.Equal(10, report.NumberOfUsers);
    // stub.Verify(...) here would be overspecification — DON'T
}
```

**Leaking implementation detail (bad) → well-designed API (good):**
```csharp
// BAD: client must call two operations; can bypass the invariant
public class User
{
    public string Name { get; set; }
    public string NormalizeName(string name) { /* trim to 50 */ }
}
// caller: var n = user.NormalizeName(newName); user.Name = n;

// GOOD: detail hidden, invariant enforced, one operation
public class User
{
    private string _name;
    public string Name
    {
        get => _name;
        set => _name = NormalizeName(value);
    }
    private string NormalizeName(string name) { /* trim to 50 */ }
}
// caller: user.Name = newName;
```

## Reference Tables

**Mock vs stub:**
| Aspect | Mock | Stub |
|---|---|---|
| Interaction type | Outcoming (changes dependency state) | Incoming (provides input data) |
| Role | Emulate **and examine** | Emulate only |
| CQS mapping | Substitutes a command | Substitutes a query |
| Assert on it? | Yes (the call is the end result) | **Never** (overspecification) |
| Example | `SendGreetingsEmail()` | `GetNumberOfUsers()` |
| If both in one double | Still called a mock | — |

**Publicity vs purpose (Table 5.1) — avoid making implementation details public:**
| | Observable behavior | Implementation detail |
|---|---|---|
| **Public** | Good | Bad |
| **Private** | N/A (can't hide observable behavior) | Good |

**London vs classical schools (Table 5.2):**
| | Isolation of | A unit is | Test doubles for |
|---|---|---|---|
| London | Units | A class | All but immutable dependencies |
| Classical | Unit tests | A class or set of classes | Shared dependencies |

## Worked Example
**The purchase use case — classifying internal vs external communication.** A `CustomerController` application service orchestrates domain classes (`Customer`, `Product`, `Store`) and an external `EmailGateway` (proxy to an SMTP service):

```csharp
public bool Purchase(int customerId, int productId, int quantity)
{
    Customer customer = _customerRepository.GetById(customerId);
    Product product = _productRepository.GetById(productId);
    bool isSuccess = customer.Purchase(_mainStore, product, quantity);
    if (isSuccess)
        _emailGateway.SendReceipt(customer.Email, product.Name, quantity);
    return isSuccess;
}
```

Two communications exist:
- **Inter-system**: `CustomerController` → SMTP service (`SendReceipt`). This crosses the application boundary; the side effect (email) is visible to the external world and directly serves the client's goal. It is part of the contract / observable behavior. **Mocking it is legitimate** — you want this pattern preserved across refactorings:
  ```csharp
  mock.Verify(x => x.SendReceipt("customer@email.com", "Shampoo", 5), Times.Once);
  ```
  (The returned `isSuccess` flag is also observable but needs only a value comparison, not a mock.)
- **Intra-system**: `Customer` → `Store` (`RemoveInventory`). Both caller and recipient live inside the app. `RemoveInventory()` is neither an operation nor a state the client needs — only `Purchase()` and `GetInventory()` connect to the client's goal. `RemoveInventory()` is an intermediate step, an implementation detail. **Mocking and verifying it (`storeMock.Verify(x => x.RemoveInventory(...))`) produces a fragile test.**

The lesson: identical-looking `mock.Verify` calls are correct or fragile depending solely on whether the verified communication crosses the application boundary with an externally visible side effect.

## Key Takeaways
- Group the five test doubles into two: **mocks** (examine outcoming/command interactions) and **stubs** (emulate incoming/query interactions). Never assert on a stub.
- The `Mock<T>` class is a *tool*; it can produce either a mock or a stub. A double that is both is still called a mock.
- **CQS** maps cleanly: commands → mocks, queries → stubs.
- Tests must verify **observable behavior**, not **implementation details**. A well-designed API makes the public API coincide with observable behavior; hide everything else (and you improve unit tests automatically).
- **Hexagonal architecture**: domain (business logic) + application services (orchestration), one-way dependency flow inward, external apps connect only through application services.
- **Intra-system communications are implementation details; inter-system communications are observable behavior** — except for out-of-process dependencies accessible only through your app (e.g., application database), which are also implementation details.
- Mocking is legitimate **only** for inter-system communications crossing the application boundary with externally visible side effects. This is why the author prefers the **classical school** over the indiscriminate-mocking **London school**.

## Connects To
- **Chapter 2** — London vs classical schools; the test-isolation disagreement and shared/out-of-process/private dependency definitions.
- **Chapter 3** — encapsulation, invariants, and the anatomy of a good unit test.
- **Chapter 4** — the four attributes; resistance to refactoring as a (mostly binary) metric and false positives from coupling to implementation details.
- **Chapters 6–7** — styles of unit testing and testing out-of-process dependencies (the unmocked application-database problem) without sacrificing fast feedback.
