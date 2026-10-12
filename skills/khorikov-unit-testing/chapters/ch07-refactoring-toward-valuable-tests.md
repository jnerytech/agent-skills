# Chapter 7: Refactoring toward valuable unit tests

## Core Idea
You can't significantly improve a test suite without refactoring the production code it covers — tests and code are intrinsically connected. Categorize all production code along two dimensions (complexity/domain significance vs. number of collaborators) to find the **overcomplicated code** that is hard to test yet too risky to leave uncovered. Split it into **domain model and algorithms** (deep, few collaborators — unit-test these heavily) and **controllers** (wide, many collaborators — cover briefly with integration tests) using the **Humble Object pattern**. Keep side effects in memory until the end of a business operation so they can be tested without out-of-process dependencies.

## Frameworks Introduced (name, when, how)
- **Types-of-code quadrant** — *when:* deciding what is worth unit testing; *how:* plot each class/method by complexity-or-domain-significance (vertical) against number of collaborators (horizontal) to get four categories.
- **Humble Object pattern** (Gerard Meszaros, *xUnit Test Patterns*) — *when:* code is hard to test because it's coupled to a framework/out-of-process dependency; *how:* extract the testable logic into a separate class; the remaining code becomes a thin, humble wrapper (a controller) that glues the hard-to-test dependency to the extracted component and contains little/no logic.
- **CanExecute/Execute pattern** — *when:* you must split decision-making into granular steps without leaking business logic into controllers; *how:* add a `CanDo()` method per `Do()` method and make `CanDo() == null` a precondition of `Do()`.
- **Domain events** — *when:* you need to notify external systems of meaningful changes without putting that decision in the controller; *how:* domain classes record immutable past-tense event objects in a collection; the controller dispatches them after the operation.

## Key Concepts (5–10)
1. **Cyclomatic complexity** = `1 + <number of branching points>`; counts simplest predicates (`IF a AND b` = complexity 3). Also the number of tests for 100% branch coverage.
2. **Domain significance** — how connected the code is to end-users' goals. Domain code need not be complex (e.g., an order-price calc with complexity 1 is still business-critical).
3. **Collaborators** — mutable or out-of-process dependencies (explicit or implicit). Immutable values/value objects don't count. More collaborators → larger, costlier tests.
4. **Out-of-process collaborators are a no-go for the domain model** — they force mock machinery and threaten resistance to refactoring. Delegate them to classes outside the domain layer.
5. **Code depth vs. width** — code can be deep (complex/important) or wide (many collaborators), but never both. "The more important or complex the code, the fewer collaborators it should have."
6. **Active Record pattern** — a domain class that retrieves and persists itself; works in small projects but fails to scale because it merges business logic with persistence.
7. **Test preconditions only if they have domain significance** (e.g., `NumberOfEmployees >= 0` is a Company invariant — test it; `data.Length >= 3` in a factory — don't).
8. **Observable behavior as onion layers** — test each layer from the outer layer's perspective; calls a layer makes to underlying layers are implementation details. Switch perspective as you peel down.

## Mental Models
- **Deep vs. wide blocks**: controllers are wide and short (many arrows in, little height); domain classes are tall and narrow.
- **Onion layers**: client→controller→User→Company. At each level the inner call has an immediate connection to the current client's goal (test it) but the calls *it* makes are implementation details (don't verify them with mocks).
- **Abstractions over future side effects**: domain events abstract upcoming bus messages; changes in domain objects abstract upcoming DB writes. "It's easier to test abstractions than the things they abstract."

## Anti-patterns
- **Fat controllers** — controllers that do complex work themselves instead of delegating → overcomplicated quadrant.
- **Active Record** in growing code bases (domain model talking directly to the database).
- **Making implicit dependencies explicit via interfaces and mocking them** (Take 1): an out-of-process dependency behind an interface is *still* out-of-process — mocking the database causes test fragility. Insufficient.
- **Injecting out-of-process dependencies into the domain model** — drags code into the overcomplicated quadrant; avoid.
- **Chasing 100% coverage** — goal is a suite where each test adds significant value. Better to not write a test than to write a bad one.
- **Business logic fragmentation** — splitting a decision between controller and domain class (e.g., moving the `IsEmailConfirmed` check into the controller) weakens domain-model encapsulation.

## Code Examples
Domain model after refactoring (no collaborators except `Company`):
```csharp
public void ChangeEmail(string newEmail, Company company)
{
    if (Email == newEmail) return;
    UserType newType = company.IsEmailCorporate(newEmail)
        ? UserType.Employee : UserType.Customer;
    if (Type != newType)
    {
        int delta = newType == UserType.Employee ? 1 : -1;
        company.ChangeNumberOfEmployees(delta);
    }
    Email = newEmail;
    Type = newType;
}
```

CanExecute/Execute pattern:
```csharp
public string CanChangeEmail()
{
    if (IsEmailConfirmed)
        return "Can't change a confirmed email";
    return null;
}
public void ChangeEmail(string newEmail, Company company)
{
    Precondition.Requires(CanChangeEmail() == null);
    /* the rest of the method */
}
```
The controller still has an `if` calling `CanChangeEmail()`, but you don't test that `if` — there's no option *not* to call it, so the decision is fully owned by `User`.

## Reference Tables

### Figure 7.1 — The four types of code

| | **Few collaborators** | **Many collaborators** |
|---|---|---|
| **High complexity or domain significance** | **Domain model and algorithms** — best ROI; valuable + cheap. Unit-test heavily. | **Overcomplicated code** (e.g., fat controllers) — hard to test, risky to skip. **Refactor**: split into algorithms + controllers. |
| **Low complexity and domain significance** | **Trivial code** (parameterless ctors, one-line properties) — close-to-zero value. Don't test. | **Controllers** — orchestrate domain classes & external apps. Test briefly via integration tests. |

### Conditional logic in controllers — pick two of three (Figure 7.12)

| Option | Controller simplicity | Domain testability | Performance |
|---|---|---|---|
| Push all reads/writes to the edges | ✅ | ✅ | ❌ |
| Inject out-of-process deps into domain model | ✅ | ❌ | ✅ |
| Split decision-making into granular steps | ❌ | ✅ | ✅ |

Recommended: the third option (performance matters, and injecting deps overcomplicates the domain) — then mitigate controller complexity with CanExecute/Execute and domain events.

## Worked Example
**CRM — changing a user's email** (3 rules: corporate domain → mark employee; track employee count; notify message bus).

- **Listing 7.1 (start):** `User.ChangeEmail` reads/writes `Database` and `MessageBus` itself (Active Record). High domain significance + 2 out-of-process collaborators ⇒ **overcomplicated quadrant**.
- **Take 1 — make implicit deps explicit:** introduce interfaces, mock them. Rejected: still out-of-process, still fragile.
- **Take 2 — application services layer:** add `UserController` to handle DB/bus; `User.ChangeEmail(newEmail, companyDomainName, numberOfEmployees)` becomes collaborator-free → moves to domain quadrant. But the controller now reconstructs `User` from raw data and `User` awkwardly returns an updated employee count.
- **Take 3 — remove complexity from controller:** extract reconstruction into `UserFactory.Create(object[] data)` (uses `Precondition.Requires(data.Length >= 3)`). The hidden branches in casts/array indexing make it test-worthy but it has no domain significance (utility code).
- **Take 4 — introduce `Company`:** the awkward return value signals a missing abstraction. `Company` bundles `ChangeNumberOfEmployees(delta)` and `IsEmailCorporate(email)` (tell-don't-ask). `User.ChangeEmail(newEmail, company)` now delegates. Plus `CompanyFactory`.

Final controller — pure orchestration:
```csharp
public void ChangeEmail(int userId, string newEmail)
{
    object[] userData = _database.GetUserById(userId);
    User user = UserFactory.Create(userData);
    object[] companyData = _database.GetCompany();
    Company company = CompanyFactory.Create(companyData);
    user.ChangeEmail(newEmail, company);
    _database.SaveCompany(company);
    _database.SaveUser(user);
    _messageBus.SendEmailChangedMessage(userId, newEmail);
}
```
**Result:** all side effects stay in memory (changed email, employee count) until the controller persists them last. Domain model is fully output/state-based testable; no mocks needed. Later, the *send-only-on-change* bug is fixed with **domain events**: `User` adds `EmailChangedEvent` to a collection when the email actually changes, and the controller dispatches the collection to the bus.

## Key Takeaways
- Two dimensions classify all code: complexity/domain significance and number of collaborators.
- Unit-test the **domain model and algorithms** quadrant (valuable + cheap); skip **trivial code**; integration-test **controllers** briefly; eliminate **overcomplicated code** by splitting it.
- The **Humble Object pattern** extracts business logic so the remainder becomes a thin controller; hexagonal and functional architectures are both instances of it.
- Keep the domain model free of out-of-process collaborators; push communication to the application services layer.
- For mid-operation decisions you can only have two of {controller simplicity, domain testability, performance} — split decision-making and use **CanExecute/Execute** + **domain events** to keep controllers thin.
- Test preconditions with domain significance only.
- Don't mock calls between domain classes; only the entry call and out-of-process side effects are observable behavior.

## Connects To
- **Ch. 4** — the four attributes of a good test (protection against regressions, resistance to refactoring, fast feedback, maintainability) drive what's worth testing.
- **Ch. 5** — resistance to refactoring; observable behavior vs. implementation details; tell-don't-ask.
- **Ch. 6** — functional architecture / output-based testing; this chapter generalizes that to enterprise apps without a pure functional core.
- **Ch. 2** — definition of collaborators (mutable / out-of-process).
- **Ch. 8 (Part 3)** — integration testing the controllers quadrant and verifying out-of-process side effects.
