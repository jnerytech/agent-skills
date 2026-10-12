# Chapter 10: Testing the Database

## Core Idea
The database is the last piece of integration testing: a **managed out-of-process dependency** that must be used as-is (no mocks). Real-database tests give bulletproof regression protection but require setup discipline. Before testing, get prerequisites right (schema in source control, reference data, per-developer instances, **migration-based database delivery**). During tests, manage transactions to mirror production, control the **test data life cycle** (clean at the start), and shorten tests by extracting technical bits. Never substitute an **in-memory database** for the real one.

## Frameworks Introduced (name, when, how)
- **Migration-based database delivery** — when releasing to production and data already exists. Store explicit, immutable migration scripts (forward + backward) in source control; tools like Flyway, Liquibase, or FluentMigrator apply them in order.
- **Transaction + Repositories split** — when a business operation mutates multiple rows/tables. Repositories decide *what* to update (short-lived); a `Transaction` decides whether to commit or roll back (lives the whole operation). Repositories enlist into the current transaction.
- **Unit of work** (upgrade of Transaction) — when an ORM is available. Defers all updates to the end of the operation, shortening the DB transaction and reducing congestion. NHibernate (`ISession`) and Entity Framework (`DbContext`) implement it for you.
- **Object Mother** — to reuse arrange-section code. Factory method/class with default arguments creating test fixtures.
- **Test Data Builder** — fluent alternative to Object Mother (`new UserBuilder().WithEmail(...).Build()`); more boilerplate, so prefer Object Mother in C#.

## Key Concepts
1. **Schema in source control**: treat schema (tables, views, indexes, stored procedures) as code; a "model database" as source of truth is an anti-pattern (no history, two competing sources of truth).
2. **Reference data**: data that must be prepopulated for the app to operate (e.g., a `UserType` table referenced by a foreign key). Heuristic: if the app can modify it, it's regular data; if not, it's reference data. Store as `INSERT` statements under migrations.
3. **Separate instance per developer** (preferably local) to avoid test interference and blocking non-backward-compatible changes.
4. **State-based vs. migration-based**: state-based makes *state* explicit and lets a comparison tool implicitly control migrations; migration-based makes *migrations* explicit and leaves state implicit.
5. **Data motion**: changing the shape of existing data to fit the new schema. Migrations handle it; comparison tools cannot (data is context-dependent). Data motion matters far more than merge conflicts once you have production data.
6. **Atomic updates**: all-or-nothing; rely on the underlying DB's transaction mechanism.
7. **Separate connections from transactions**: split "what to update" (repository) from "keep or roll back" (transaction).
8. **Three+ transactions per test**: arrange, act, and assert each get their own context/unit of work, so the act section matches production and the assert section reads state independently (ORM caching).
9. **Test data life cycle**: tests must not depend on DB state; bring it to the required condition themselves. Run integration tests sequentially; clean leftover data at the start.

## Mental Models
- **Migrations are an append-only log**: once committed, never edit a migration; write a new one (exception: a migration that causes data loss).
- **Commit() is a decision, Dispose() is mechanical**: the controller calls `Commit()` only on the happy path; infrastructure always calls `Dispose()`, which persists if committed, else rolls back.
- **Tests must replicate production as closely as possible**: any deviation (shared context, overarching never-committed transaction, different DB vendor) risks false positives/negatives.
- **Distill essentials, amplify the scenario**: move technicalities (context creation, cleanup, querying) out; keep the business intent visible.

## Anti-patterns
- **Using in-memory databases for integration tests**: SQLite and similar aren't functionally consistent with the real DBMS. Tests run fast and self-isolate but produce false positives/negatives from vendor differences, so protection is illusory. Use the same DBMS as production (version/edition may differ; vendor must not).
- **Model database as source of truth**: no change history, competing source of truth alongside Git.
- **State-based delivery after release**: comparison tools mangle data motion; impractical once production data exists (fine only pre-release).
- **Reusing one `CrmContext`/unit of work across arrange/act/assert**: doesn't match production (where each operation gets an exclusive context) and ORM caching corrupts the assert.
- **Cleaning up at the end of a test**: fast but skips cleanup if the build server crashes or you stop in the debugger, leaving data for later runs.
- **Wrapping each test in a never-committed transaction**: solves skipped cleanup but introduces an overarching transaction that diverges from production behavior.
- **Editing a committed migration**: create a new one instead.
- **Testing repositories or `EventDispatcher` directly**: same maintenance cost as integration tests but inferior, overlapping protection.

## Code Examples
FluentMigrator migration (forward + backward):
```csharp
[Migration(1)]
public class CreateUserTable : Migration
{
    public override void Up() { Create.Table("Users"); }
    public override void Down() { Delete.Table("Users"); }
}
```

Transaction with repositories — `Commit()` only on the happy path:
```csharp
public string ChangeEmail(int userId, string newEmail)
{
    object[] userData = _userRepository.GetUserById(userId);
    User user = UserFactory.Create(userData);
    string error = user.CanChangeEmail();
    if (error != null) return error;          // early return -> no commit

    object[] companyData = _companyRepository.GetCompany();
    Company company = CompanyFactory.Create(companyData);
    user.ChangeEmail(newEmail, company);
    _companyRepository.SaveCompany(company);
    _userRepository.SaveUser(user);
    _eventDispatcher.Dispatch(user.DomainEvents);
    _transaction.Commit();                    // commit at the very end
    return "OK";
}
```

Object Mother with default values for arrange reuse:
```csharp
private User CreateUser(
    string email = "user@mycorp.com",
    UserType type = UserType.Employee,
    bool isEmailConfirmed = false)
{ /* ... SaveUser + context.SaveChanges() ... */ }
```

## Reference Tables
| Approach | State of the database | Migration mechanism |
|----------|----------------------|---------------------|
| State-based | Explicit | Implicit |
| Migration-based | Implicit | Explicit |

| Cleanup option | Verdict |
|----------------|---------|
| Restore DB backup before each test | Works, but far too slow |
| Clean up at end of test | Fast, but skips on crash/debugger stop |
| Wrap test in never-committed transaction | Avoids skipped cleanup, but diverges from production |
| **Clean up at start of test** | **Best**: fast, consistent, never skipped |

## Worked Example
**Test data life cycle — clean at the start, not the end.**

The shared per-developer database means tests must isolate themselves. Two rules: run integration tests sequentially, and remove leftover data between runs. Of the four cleanup options, only cleaning at the **start** is safe — it is fast, doesn't create production/test divergence, and can never be skipped (no separate teardown to crash through). Put the deletion script in a base class so it runs before every test:

```csharp
public abstract class IntegrationTests
{
    private const string ConnectionString = "...";
    protected IntegrationTests() { ClearDatabase(); }

    private void ClearDatabase()
    {
        string query =
            "DELETE FROM dbo.[User];" +
            "DELETE FROM dbo.Company;";
        using (var connection = new SqlConnection(ConnectionString))
        {
            var command = new SqlCommand(query, connection)
                { CommandType = CommandType.Text };
            connection.Open();
            command.ExecuteNonQuery();
        }
    }
}
```

Two constraints: write the deletion order **by hand** to honor foreign keys (don't auto-generate scripts or disable constraints — manual is simpler and more controllable), and the script must delete **all regular data but no reference data** (reference data is owned by migrations). There's no separate teardown phase; teardown lives in the arrange section. Reserve the base class strictly for what must run every test (cleanup) — put factory methods in the test class, not the base.

## Key Takeaways
- Store schema (including reference data) in source control; never use a model database as the source of truth.
- Prefer migration-based over state-based delivery: data motion beats merge conflicts in importance. Never edit committed migrations.
- Give each developer a separate DB instance, ideally local.
- Make mutating business operations atomic via the DB's transaction mechanism; prefer a unit of work (ORM) to defer updates.
- Use at least three transactions/units of work per integration test — one each for arrange, act, assert.
- Run integration tests sequentially; clean leftover data at the **start** of each test.
- Avoid in-memory databases; use the same DBMS vendor as production.
- Shorten tests by extracting technicalities: Object Mother for arrange, decorator method for act, fluent interface for assert (accept the extra transactions as a maintainability trade-off).
- Set a higher bar for testing reads than writes; don't test repositories or `EventDispatcher` in isolation.

## Connects To
- **Ch 8 (Integration testing)**: managed dependencies included as-is, never mocked; check DB state independently of input.
- **Ch 9 (Mocking best practices)**: `BusSpy` and fluent assertion helpers; unmanaged dependencies (`MessageBus`, `IDomainLogger`) still mocked here.
- **Ch 7 (Refactoring toward valuable tests)**: repositories sit in the controllers quadrant (low complexity + out-of-process dependency); extract complexity into self-contained algorithms (`UserFactory`).
- **Ch 5–6 (Mocks/encapsulation)**: reads need no domain model because encapsulation guards data changes, of which reads have none.
- **Ch 3 (Anatomy of a unit test)**: private factory methods for arrange-section reuse.
- **Ch 4 (Four pillars)**: fast feedback vs. maintainability trade-off when transaction count rises.
