# Chapter 3: The Anatomy of a Unit Test

## Core Idea
A good unit test has a uniform, predictable structure that makes any test in the suite easy to read. That structure is **Arrange, Act, Assert (AAA)**: one test verifies one unit of behavior, expressed as a single, atomic *fact* about the application — readable enough that a non-programmer who knows the domain could understand it. Deviations from this shape (multiple AAA blocks, `if` statements, multi-line act sections, cryptic names) are signals of deeper problems in either the test or the production code's API.

## Frameworks Introduced
- **Arrange, Act, Assert (AAA)** — *when*: every unit test. *How*: split each test into three parts — Arrange (bring the SUT and its dependencies to a desired state), Act (call methods on the SUT, capture output), Assert (verify the outcome: return value, final state, or collaborator calls). Also called the *3A pattern*.
- **Given-When-Then** — *when*: tests shared with non-technical people. *How*: same three parts (Given=Arrange, When=Act, Then=Assert); only difference is the wording reads more naturally to non-programmers.
- **xUnit** — *when*: the .NET test framework used throughout the book (preferred over NUnit/MSTest for being cleaner). *How*: `[Fact]` marks a test method; any public class can hold tests (no `[TestFixture]`); share setup via the constructor, clean up via `IDisposable.Dispose()`.
- **Parameterized tests (`[Theory]` + `[InlineData]`/`[MemberData]`)** — *when*: grouping similar facts that differ only by input. *How*: `[Theory]` marks the method, each `[InlineData(...)]` line is one test case; use `[MemberData(nameof(...))]` for runtime-generated data.
- **Fluent Assertions** — *when*: improving assertion readability. *How*: `result.Should().Be(30)` reads as a `[Subject][action][object]` story.

## Key Concepts
1. **SUT (system under test)** — the single entry-point class that triggers the behavior; always name its instance `sut` to distinguish it from dependencies.
2. **Unit of behavior, not unit of code** — a single behavior can have multiple outcomes; it's fine to assert all of them in one test. The "one assertion per test" rule is wrong.
3. **Act section ≤ one line** — for business-logic code, a multi-line act signals a broken SUT API (the client must remember a second call).
4. **Invariant violation** — an inconsistency that arises when operations that must happen together can be split apart. **Encapsulation** is protecting code against these.
5. **Test fixture** — (1) an object the test runs against that must be in a known, fixed state before each run; (2) NUnit's `[TestFixture]` attribute. The book uses meaning (1).
6. **Reuse via private factory methods, not the constructor** — factory methods keep tests decoupled and self-contained while still reducing duplication.
7. **No rigid naming policy** — avoid `[MethodUnderTest]_[Scenario]_[ExpectedResult]`; it focuses on implementation details. Use plain-English phrases with underscores.
8. **Don't include the method-under-test name in the test name** — you test behavior, not code; renaming a method shouldn't force renaming a test.
9. **Test = an atomic fact** — `[Fact]` is named "Fact" because each passing test proves a story holds true. Use `is`, not `should be`.
10. **Teardown is not part of AAA** — most unit tests need none (no out-of-process side effects); it's a separate, reused method.

## Mental Models
- **A test tells a story.** Not a dull enumeration of what the code does — a higher-level description of behavior meaningful to business people. `[Fact]` reinforces this: each test is one fact.
- **The SUT is just a door.** It's an entry point into a behavior that may span one or many classes. `[ClassName]Tests` names the door, not a limit on what's verified.
- **The test's shape is a diagnostic.** Multiple acts → it's really an integration test. Multi-line act → broken encapsulation. `if` statement → too many things tested at once. Cryptic name → focus on code instead of behavior.

## Anti-patterns
- **Multiple Arrange/Act/Assert sections** in one test → verifies multiple behaviors; split into one test per action. (Allowed *only* in already-slow integration tests as an optimization, never in unit tests.)
- **`if` statements in tests** → branching means too many things at once; split it. No integration-test exception here.
- **Multi-line act section** (business code) → SUT API forces the client to make a second call; fix the API, not the test.
- **High coupling between tests** via shared mutable state (private fields initialized in the constructor) → a change to one test's arrangement breaks others.
- **Initializing fixtures in the constructor** → diminishes readability (test no longer self-contained) and couples tests.
- **Rigid naming convention** (`Sum_TwoNumbers_ReturnsSum`) → cryptic, implementation-coupled, imposes a cognitive tax.
- **`should be` / `considered` wording** → a fact needs no wish or filler; say `is`.

## Code Examples
```csharp
public class CalculatorTests
{
    [Fact]
    public void Sum_of_two_numbers()
    {
        // Arrange
        double first = 10;
        double second = 20;
        var sut = new Calculator();

        // Act
        double result = sut.Sum(first, second);

        // Assert
        Assert.Equal(30, result);
    }
}
```
- **What it demonstrates**: clean AAA structure; the SUT named `sut`; a single-line act section; one fact ("sum of two numbers") named in plain English. Section comments may be dropped and replaced by blank lines when the arrange/assert sections need no internal blank lines.

## Reference Tables

| Section | Ideal size | Smell if larger |
|---|---|---|
| Arrange | Largest (≈ act + assert combined) | Extract to factory methods / Object Mother / Test Data Builder |
| Act | One line | Broken SUT API (business code); breach of encapsulation |
| Assert | Can be several | Too many → missing abstraction (define equality members) |
| Teardown | Usually none | Needed mostly for integration tests |

| Reuse approach | Verdict |
|---|---|
| Constructor / `[SetUp]` fields | Anti-pattern — couples tests, hurts readability |
| Private factory methods | Preferred — decoupled, readable, reusable |
| Base-class constructor | OK only when used by ~all tests (e.g. DB connection in integration tests) |

## Worked Example
**Renaming a test toward the guidelines.** Starting from a rigid-policy name and improving step by step:

```csharp
// Rigid policy — cryptic, implementation-coupled
public void IsDeliveryValid_InvalidDate_ReturnsFalse()

// 1. Plain English; method name dropped
public void Delivery_with_invalid_date_should_be_considered_invalid()
// 2. Be specific: "invalid" means a past date
public void Delivery_with_past_date_should_be_considered_invalid()
// 3. Drop "considered" (verbose)
public void Delivery_with_past_date_should_be_invalid()
// 4. Replace "should be" with "is" (state a fact, not a wish)
public void Delivery_with_past_date_is_invalid()
// 5. Allow basic grammar / articles
public void Delivery_with_a_past_date_is_invalid()
```

**Then collapse similar facts into a parameterized test** (soonest allowed date is 2 days out):

```csharp
public class DeliveryServiceTests
{
    [InlineData(-1, false)]
    [InlineData(0, false)]
    [InlineData(1, false)]
    [InlineData(2, true)]
    [Theory]
    public void Can_detect_an_invalid_delivery_date(int daysFromNow, bool expected)
    {
        DeliveryService sut = new DeliveryService();
        DateTime deliveryDate = DateTime.Now.AddDays(daysFromNow);
        Delivery delivery = new Delivery { Date = deliveryDate };

        bool isValid = sut.IsDeliveryValid(delivery);

        Assert.Equal(expected, isValid);
    }
}
```
Each `[InlineData]` is a separate fact; `[Theory]` ("a bunch of facts") replaces `[Fact]`. Trade-off: generic names lose readability — extract the positive case into its own `[Fact]` when the input doesn't make valid/invalid self-evident. Note `[InlineData]` content is evaluated at compile time (only constants, literals, `typeof()`), so `DateTime.Now` won't work inline — use `[MemberData(nameof(Data))]` with a static method returning `List<object[]>` for runtime data.

## Key Takeaways
- Structure every unit test as **Arrange, Act, Assert**; one behavior per test.
- Multiple AAA sections, `if` statements, or a multi-line act are smells — fix the test or the SUT's API.
- Name the SUT instance `sut`; separate sections with blank lines or `// Arrange/Act/Assert` comments.
- Reuse arrange code with **private factory methods**, never via constructor-initialized shared fields.
- Name tests as plain-English facts (`is`, not `should be`), underscore-separated, without the method-under-test name.
- Use `[Theory]`/`[InlineData]`/`[MemberData]` to group similar facts; use Fluent Assertions (`result.Should().Be(30)`) for story-like reads.

## Connects To
- **Ch. 2 (What is a unit test?)** — defines a unit as a *unit of behavior*; classical-school isolation underpins the "no shared state between tests" rule and the unit-vs-integration distinction that forbids multiple acts.
- **Ch. 4 (Four pillars of a good test)** — readability and maintainability goals that these structural/naming rules serve.
- **Ch. 5 (Mocks and test fragility)** — why coupling tests to implementation details (e.g. method-name-based test names) harms maintainability.
- **Ch. 11 / Part 3** — proper teardown and fixture reuse for integration tests that touch a database.
