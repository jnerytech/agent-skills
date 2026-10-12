# Chapter 4: Unit testing with xUnit

## Core Idea
Unit tests exercise the smallest units (classes) in isolation, enforcing a contract per unit so that any source change must either honor the contract or explicitly change it. They enable safe refactoring (changing code without changing external behavior). xUnit is the .NET Core-native test framework: no test-class attribute needed, terse `Assert` verbs, and it plugs into `dotnet test` via the `xunit.runner.visualstudio` package. Design units around the single-responsibility principle so each is independently verifiable — the business-day calculator does this by splitting each business-day rule into its own `IRule` implementation.

## Frameworks Introduced
- **xUnit**: .NET Core unit-testing framework, favored by early adopters.
  - When to use: default choice for testing .NET Core class libraries; anything runnable through `dotnet test`.
  - How: `dotnet new xunit` scaffolds a test project; add a `<ProjectReference>` to the library under test; write `[Fact]`/`[Theory]` methods; run `dotnet test`.
- **`dotnet test` CLI**: runs the test suite; supports `--filter` for Traits.
  - When to use: CI, terminal, or IDE-integrated runs.
  - How: `dotnet test` discovers and executes; `dotnet test --filter Holiday=true` runs a Trait subset.

## Key Concepts
- **`[Fact]`**: a test that is *always* true — no inputs; asserts an invariant.
- **`[Theory]` + `[InlineData]`**: a test true only for a specific data set; each `[InlineData]` row becomes its own test case, and failure messages include the parameters.
- **`[MemberData(nameof(...))]`**: supplies theory data from a **static** property returning `IEnumerable<object[]>` (via `yield return`). Use when there are many cases or when data can't be a compile-time constant (e.g. `new DateTime(...)` can't go in an attribute).
- **Shared context**: xUnit constructs a *fresh test-class instance per test method* (including per theory row), enabling parallel/random-order execution. Setup/cleanup is shared via four mechanisms below.
- **`ITestOutputHelper`**: inject via constructor to log per-test output; correlates output to the failing test. Output only surfaces when a test fails.
- **Traits**: `[Trait("name","value")]` — arbitrary string name/value pairs for categorizing/filtering tests.

## Mental Models
- **Fact = proof; Theory = evidence**: use a Fact when you can assert an invariant; use a Theory when you can only sample a subset of possible inputs (you can't prove all cases).
- **New instance per test**: never rely on state leaking between test methods — xUnit throws the object away and rebuilds it each time. This is *why* order-independence and parallelism are safe.
- **Constructor/Dispose = per test; Fixture = per class/collection**: pick the sharing scope by how expensive setup is and how far it must reach.

## Anti-patterns
- Writing a `[Fact]` for logic with many possible inputs (e.g. every date) — it silently ignores untested cases; use a `[Theory]` instead.
- Using `Console.WriteLine` for test output — parallel tests interleave output and passing tests hide it; use `ITestOutputHelper`.
- Stacking dozens of `[InlineData]` attributes when cases are numerous or computed — switch to `[MemberData]`.
- Putting non-constant expressions (like `new DateTime(...)`) in `[InlineData]` — attributes only accept constant expressions; pass a string and `DateTime.Parse`, or use `[MemberData]`.
- Cramming all rules into one long chain of `if` statements instead of separate, independently testable `IRule` classes.
- Forgetting to call the wrapped resource's `Dispose` inside your test class's `Dispose` (leaks file handles/sockets).

## Code Examples
```csharp
using System;
using System.Collections.Generic;
using BizDayCalc;
using Xunit;
using Xunit.Abstractions;

namespace BizDayCalcTests
{
    // [Fact] — an invariant, no inputs
    public class WeekendRuleTest
    {
        [Fact]
        public void TestCheckIsBusinessDay()
        {
            var rule = new WeekendRule();
            Assert.True(rule.CheckIsBusinessDay(new DateTime(2016, 6, 27)));  // Monday
            Assert.False(rule.CheckIsBusinessDay(new DateTime(2016, 6, 26))); // Sunday
        }

        // [Theory] with [InlineData] — one test case per row, multiple params
        [Theory]
        [InlineData(true,  "2016-06-27")] // Monday
        [InlineData(true,  "2016-03-01")] // Tuesday
        [InlineData(false, "2016-06-26")] // Sunday
        [InlineData(false, "2016-11-12")] // Saturday
        public void IsBusinessDay(bool expected, string date)
        {
            var rule = new WeekendRule();
            Assert.Equal(expected, rule.CheckIsBusinessDay(DateTime.Parse(date)));
        }
    }

    // Class fixture — created ONCE, shared across all methods in the test class
    public class USRegionFixture
    {
        public Calculator Calc { get; private set; }
        public USRegionFixture()
        {
            Calc = new Calculator();
            Calc.AddRule(new WeekendRule());
            Calc.AddRule(new HolidayRule());
        }
        // cleanup: implement IDisposable on the fixture if needed
    }

    public class USRegionTest : IClassFixture<USRegionFixture>
    {
        private readonly USRegionFixture fixture;
        private readonly ITestOutputHelper output;

        // xUnit injects both the fixture and ITestOutputHelper via the constructor
        public USRegionTest(USRegionFixture fixture, ITestOutputHelper output)
        {
            this.fixture = fixture;
            this.output = output;
        }

        [Theory]
        [InlineData("2016-01-01")]
        [InlineData("2016-12-25")]
        [Trait("Holiday", "true")]
        public void TestHolidays(string date)
        {
            output.WriteLine($@"TestHolidays(""{date}"")");
            Assert.False(fixture.Calc.IsBusinessDay(DateTime.Parse(date)));
        }
    }
}
```
- **What it demonstrates**: the progression Fact → Theory (multi-param `[InlineData]`) → shared context via `IClassFixture<T>`, plus constructor-injected `ITestOutputHelper` and a `[Trait]` for filtering. `Assert` verbs are terse (`True`/`False`/`Equal`, not `IsTrue`).

## Reference Tables

### Fact vs Theory
| Aspect | `[Fact]` | `[Theory]` |
|---|---|---|
| Meaning | Always true (an invariant) | True only for a given data set |
| Inputs | None | Parameters supplied by data attributes |
| Test count | One | One per data row |
| Data sources | — | `[InlineData]`, `[MemberData]` |
| Use when | You can prove the case outright | You can only sample inputs (can't prove all cases) |
| Failure output | The assertion | Includes the parameter values for the failing row |

### Theory data attributes
| Attribute | Source | Constraint |
|---|---|---|
| `[InlineData(...)]` | Constants in the attribute | Only compile-time constants; supports multiple params |
| `[MemberData(nameof(Prop))]` | `static` property → `IEnumerable<object[]>` (`yield return`) | Property must be **static**; allows computed/non-constant data like `DateTime` |

### The four sharing mechanisms — scope of each
| Mechanism | Runs | Scope | How |
|---|---|---|---|
| Constructor | Before **every** test method (incl. each theory row) | Per test instance | Put setup in the test class's constructor |
| `Dispose()` (`IDisposable`) | After **every** test method | Per test instance | Test class implements `IDisposable`; call wrapped resource's `Dispose` |
| `IClassFixture<T>` | **Once** for the whole test class | Shared across methods of one class | Fixture class holds setup; test class implements `IClassFixture<T>`, receives `T` via constructor; cleanup via `IDisposable` on the fixture |
| `ICollectionFixture<T>` | **Once** across multiple test classes | Shared across a named collection of classes | `[CollectionDefinition("name")]` class implements `ICollectionFixture<T>`; test classes marked `[Collection("name")]`, receive `T` via constructor (no `IClassFixture` needed) |

## Worked Example
Business-day calculator test suite, evolved in three steps.

**1. Start with a `[Fact]`** for `WeekendRule` — asserts a business day and a non-business day:
```csharp
[Fact]
public void TestCheckIsBusinessDay()
{
    var rule = new WeekendRule();
    Assert.True(rule.CheckIsBusinessDay(new DateTime(2016, 6, 27)));  // Mon
    Assert.False(rule.CheckIsBusinessDay(new DateTime(2016, 6, 26))); // Sun
}
```
Problem: weekends have countless date inputs — a Fact can't prove them all.

**2. Convert to a `[Theory]`** so each date is its own case (a bad row like `"2017-09-17"`, a Sunday asserted True, fails and the message names the offending date):
```csharp
[Theory]
[InlineData(true,  "2016-06-27")] // Mon
[InlineData(true,  "2016-03-01")] // Tue
[InlineData(false, "2016-06-26")] // Sun
[InlineData(false, "2016-11-12")] // Sat
public void IsBusinessDay(bool expected, string date)
{
    var rule = new WeekendRule();
    Assert.Equal(expected, rule.CheckIsBusinessDay(DateTime.Parse(date)));
}
```
When cases grow or need `DateTime` objects, switch to `[MemberData]`:
```csharp
public static IEnumerable<object[]> Days()
{
    yield return new object[] { true,  new DateTime(2016, 6, 27) };
    yield return new object[] { false, new DateTime(2016, 6, 26) };
}

[Theory]
[MemberData(nameof(Days))]
public void TestCheckIsBusinessDay(bool expected, DateTime date)
{
    var rule = new WeekendRule();
    Assert.Equal(expected, rule.CheckIsBusinessDay(date));
}
```

**3. Add shared context via a class fixture** — building a `Calculator` with all rules is expensive (imagine loading rules from a DB), so do it once:
```csharp
public class USRegionFixture
{
    public Calculator Calc { get; private set; }
    public USRegionFixture()
    {
        Calc = new Calculator();
        Calc.AddRule(new WeekendRule());
        Calc.AddRule(new HolidayRule());
    }
}

public class USRegionTest : IClassFixture<USRegionFixture>
{
    private readonly USRegionFixture fixture;
    public USRegionTest(USRegionFixture fixture) => this.fixture = fixture;

    [Theory]
    [InlineData("2016-01-01")] // New Year's
    [InlineData("2016-12-25")] // Christmas
    public void TestHolidays(string date)
        => Assert.False(fixture.Calc.IsBusinessDay(DateTime.Parse(date)));
}
```
The fixture constructor runs exactly once (verify with a `Console.WriteLine`), versus the per-test constructor in `USHolidayTest` which ran six times. To share the same fixture across *multiple* test classes, promote it to a collection fixture:
```csharp
[CollectionDefinition("US region collection")]
public class USRegionCollection : ICollectionFixture<USRegionFixture> { }

[Collection("US region collection")]  // no IClassFixture needed
public class USRegionTest { /* ctor still receives USRegionFixture */ }
```

## Key Takeaways
- A test class needs *no* attribute — the presence of `[Fact]`/`[Theory]` methods is enough.
- `Assert` methods drop verbs: `Assert.True/False/Equal`, not `IsTrue`.
- xUnit builds a new test-class instance per test method (incl. each theory row) → order-independent, parallelizable.
- Constructor = per-test setup; `Dispose` (`IDisposable`) = per-test cleanup; `IClassFixture<T>` = once per class; `ICollectionFixture<T>` = once across a `[Collection]`. Fixture cleanup reuses the dispose pattern.
- `[InlineData]` for static constants; `[MemberData]` (static property) for many or computed cases.
- Use `ITestOutputHelper` (namespace `Xunit.Abstractions`), constructor-injected, to log — output appears only for failing tests.
- `[Trait("k","v")]` categorizes tests; filter with `dotnet test --filter k=v`.

## Connects To
- **Ch 9**: performance/benchmarking with xUnit.Performance — extends the same test tooling to measure, not just verify, behavior.
- **Ch 5/6**: testing data access — the `IDisposable`/constructor and fixture patterns here become essential for setting up and tearing down database/connection state in data-layer tests (as previewed by the CSV-parser `Dispose` example).
