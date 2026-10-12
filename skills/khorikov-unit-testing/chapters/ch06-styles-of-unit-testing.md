# Chapter 6: Styles of Unit Testing

## Core Idea
There are three styles of unit testing — **output-based testing**, **state-based testing**, and **communication-based testing**. Scored against the four pillars (chapter 4), output-based produces the highest-quality tests, state-based is second-best, and communication-based should be used only occasionally. Output-based testing only applies to code written in a purely functional way, so the strategy is to restructure production code toward a **functional architecture** (a **functional core, mutable shell**) so that more tests can be written in the output-based style. The aim is not to convert *every* test, but as many as reasonably possible.

## Frameworks Introduced (name, when, how)
- **The three styles of unit testing** — use to classify and compare any test. Output-based feeds an input and checks the return value; state-based checks final state; communication-based uses mocks to verify interactions with collaborators.
- **Functional programming / mathematical functions** — use when you want output-based tests. Make methods have no hidden inputs or outputs so all I/O is explicit in the signature (referential transparency).
- **Functional architecture (functional core, mutable shell)** — use to separate business logic from side effects. Push side effects to the edges; the immutable core makes decisions, the mutable shell acts on them.
- **Read-decide-act transition** — use to migrate state/communication-based tests to output-based: shell *reads* inputs, core *decides* (returns value instructions), shell *acts* (applies side effects).

## Key Concepts (5–10)
1. **Output-based testing (functional)** — feed input to the SUT, verify the return value. Assumes no side effects. Only applicable to mathematical-function code.
2. **State-based testing** — verify the state of the SUT, a collaborator, or an out-of-process dependency after the operation completes.
3. **Communication-based testing** — use mocks to verify communications between SUT and its collaborators.
4. **Mathematical function (pure function)** — a method with no hidden inputs/outputs; all I/O is in the signature; same output for the same input every time.
5. **Referential transparency** — you can replace a method call with its return value without changing program behavior. The litmus test for a mathematical function.
6. **Hidden inputs/outputs** — side effects (mutating state, writing files), exceptions, and references to internal/external state (e.g. `DateTime.Now`, a DB query, a private mutable field).
7. **Functional core / immutable core** — code that makes decisions; written with mathematical functions; covered extensively with output-based tests.
8. **Mutable shell** — code that acts on decisions, converting them into side effects (DB writes, messages); kept "dumb"; covered by a small number of integration tests.
9. **Collaborators vs. values** — a collaborator is mutable or a proxy to out-of-memory data (shared dependency) and precludes output-based testing; a value (e.g. an immutable config field) does not. The core should work with the *product* of a collaborator's work, a value.
10. **Functional architecture ⊂ hexagonal architecture** — both separate concerns with one-way dependency flow; they differ only in side-effect treatment.

## Mental Models
- **"Replace the call with its return value"** — if you can do so without changing behavior, it's a mathematical function and output-based testable.
- **Read → Decide → Act** — shell gathers inputs, core decides (returns value instructions), shell converts decisions to side effects.
- **Functional architecture = hexagonal taken to an extreme** — hexagonal allows side effects inside the domain layer (contained); functional architecture pushes *all* side effects out of the core.
- **Immutability replaces encapsulation** — "OOP makes code understandable by encapsulating moving parts; FP makes code understandable by minimizing moving parts." (Michael Feathers) You can't corrupt what can't change.
- **Instructions are values** — a functional core always returns a value (or set of values); two instances are interchangeable if their contents match — so turn them into value objects for cleaner assertions.

## Anti-patterns
- **Overusing communication-based testing** → shallow tests that verify a thin slice and mock everything else.
- **Verifying interactions with stubs** → always brittle; only verify mocks at the application boundary whose side effects are visible externally.
- **Mock chains** (mocks returning mocks returning mocks) → large, unreadable, unmaintainable tests.
- **Exposing private state to enable state-based assertions** → couples tests to implementation details (false positives).
- **Code pollution** — adding production code (e.g. value-object members) whose sole purpose is to ease testing, when the class isn't inherently a value (covered in chapter 11).
- **Passing a collaborator (e.g. `IDatabase`) into the core** → introduces a hidden input; the method ceases to be a mathematical function and loses output-based testability.
- **Forcing functional purity everywhere** → in simple or low-value code bases the initial investment never pays off; apply strategically.

## Code Examples
Output-based (Listing 6.1) — verifies only the return value:
```csharp
public class PriceEngine
{
    public decimal CalculateDiscount(params Product[] products)
    {
        decimal discount = products.Length * 0.01m;
        return Math.Min(discount, 0.2m);
    }
}

[Fact]
public void Discount_of_two_products()
{
    var product1 = new Product("Hand wash");
    var product2 = new Product("Shampoo");
    var sut = new PriceEngine();

    decimal discount = sut.CalculateDiscount(product1, product2);

    Assert.Equal(0.02m, discount);
}
```

Referential transparency — `Increment` is a mathematical function (`int y = Increment(4);` ≡ `int y = 5;`); the version below is **not**, because mutating `x` is a hidden output:
```csharp
int x = 0;
public int Increment()
{
    x++;          // side effect = hidden output
    return x;
}
```

## Reference Tables
**Table 6.1 — The three styles of unit testing (protection against regressions and feedback speed omitted; all three score equally there):**

|                                                     | Output-based | State-based | Communication-based |
|-----------------------------------------------------|--------------|-------------|---------------------|
| Due diligence to maintain resistance to refactoring | Low          | Medium      | Medium              |
| Maintainability costs                               | Low          | Medium      | High                |

**Audit-system evolution across the four pillars (Tables 6.2–6.4):**

|                                | Initial version | With mocks | Output-based |
|--------------------------------|-----------------|------------|--------------|
| Protection against regressions | Good            | Good       | Good         |
| Resistance to refactoring      | Good            | Good       | Good         |
| Fast feedback                  | Bad             | Good       | Good         |
| Maintainability                | Bad             | Moderate   | Good         |

## Worked Example
**Refactoring an audit system from communication-based toward output-based testing.**

*Stage 0 — Initial:* `AuditManager.AddRecord` calls `Directory.GetFiles`, `File.ReadAllLines`, `File.WriteAllText` directly. Tests must touch the filesystem (a shared dependency): slow, non-parallelizable, hard to maintain — really integration tests.

*Stage 1 — Mocks:* extract an `IFileSystem` interface, inject it, and verify writes with a mock. This is a *legitimate* mock (files are observable to end users at the application boundary). Feedback becomes fast, but setups are convoluted:
```csharp
fileSystemMock.Verify(x => x.WriteAllText(
    @"audits\audit_3.txt", "Alice;2019-04-06T18:00:00"));
```

*Stage 2 — Functional architecture:* move side effects out entirely. `AuditManager` becomes the **functional core** — it receives `FileContent[]` (the inputs gathered up front) and *returns a decision* `FileUpdate` instead of writing:
```csharp
public FileUpdate AddRecord(
    FileContent[] files, string visitorName, DateTime timeOfVisit)
{
    (int index, FileContent file)[] sorted = SortByIndex(files);
    string newRecord = visitorName + ';' + timeOfVisit;
    if (sorted.Length == 0)
        return new FileUpdate("audit_1.txt", newRecord);

    (int currentFileIndex, FileContent currentFile) = sorted.Last();
    List<string> lines = currentFile.Lines.ToList();
    if (lines.Count < _maxEntriesPerFile)
    {
        lines.Add(newRecord);
        string newContent = string.Join("\r\n", lines);
        return new FileUpdate(currentFile.FileName, newContent);
    }
    else
    {
        int newIndex = currentFileIndex + 1;
        return new FileUpdate($"audit_{newIndex}.txt", newRecord);
    }
}
```
A trivial **mutable shell** `Persister` does the I/O (no `if` branches): `ReadDirectory` returns `FileContent[]`, `ApplyUpdate` writes the `FileUpdate`. An `ApplicationService` glues them — *read* (`Persister.ReadDirectory`) → *decide* (`AuditManager.AddRecord`) → *act* (`Persister.ApplyUpdate`).

*The test now uses plain inputs and outputs — no mocks (Listing 6.15):*
```csharp
[Fact]
public void A_new_file_is_created_when_the_current_file_overflows()
{
    var sut = new AuditManager(3);
    var files = new FileContent[]
    {
        new FileContent("audit_1.txt", new string[0]),
        new FileContent("audit_2.txt", new string[]
        {
            "Peter; 2019-04-06T16:30:00",
            "Jane; 2019-04-06T16:40:00",
            "Jack; 2019-04-06T17:00:00"
        })
    };

    FileUpdate update = sut.AddRecord(
        files, "Alice", DateTime.Parse("2019-04-06T18:00:00"));

    Assert.Equal("audit_3.txt", update.FileName);
    Assert.Equal("Alice;2019-04-06T18:00:00", update.NewContent);
}
```
Make `FileUpdate` a value object (struct or custom equality members) to collapse the two asserts into one:
```csharp
Assert.Equal(
    new FileUpdate("audit_3.txt", "Alice;2019-04-06T18:00:00"), update);
```

## Key Takeaways
- Prefer **output-based testing** over everything else; fall back to state-based, and use communication-based only occasionally.
- Output-based tests resist refactoring (couple only to the method under test) and are the most maintainable (short, no out-of-process dependencies).
- A **mathematical function** has no hidden inputs/outputs; side effects and exceptions are hidden outputs, references to internal/external state are hidden inputs.
- **Functional architecture** = functional core (decisions) + mutable shell (side effects), gathering inputs up front (read-decide-act).
- Functional architecture is **hexagonal architecture taken to an extreme** — it pushes *all* side effects out of the domain, whereas hexagonal tolerates contained ones.
- Pass **values, not collaborators**, into the core; a collaborator (mutable or shared dependency, like `IDatabase`) introduces a hidden input and kills output-based testability.
- Drawbacks: functional architecture isn't always attainable (mid-flow dependency queries), costs **performance** (more out-of-process calls under read-decide-act) and a **larger code base**. It's a performance-vs-maintainability trade-off — apply strategically.

## Connects To
- **Ch. 4 — The four pillars**: the frame of reference (protection against regressions, resistance to refactoring, fast feedback, maintainability) used to score the styles.
- **Ch. 5 — Mocks and test fragility**: communication-based testing, legitimate mocking only at the application boundary, observable behavior vs. implementation details, hexagonal architecture's domain/application-service split.
- **Ch. 2 — What is a unit test**: classical vs. London schools (both use output-based); collaborators vs. values; filesystem tests as integration tests.
- **Ch. 7 — Refactoring toward valuable tests**: balancing performance vs. separation of concerns; deepening the functional-core/mutable-shell split (Humble Object).
- **Ch. 11 — Unit testing anti-patterns**: code pollution from exposing/adding production code purely to enable testing.
