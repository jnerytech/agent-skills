# Chapter 1: The Goal of Unit Testing

## Core Idea
The goal of unit testing is to **enable sustainable growth** of a software project; more tests are not better—only high-quality tests whose value exceeds their upkeep cost belong in the suite. Coverage metrics and the testability of code are good *negative* indicators but bad *positive* ones.

## Frameworks Introduced
- **Sustainable growth (the goal of unit testing)**: tests act as a safety net against regressions so development speed is maintained over the project's life instead of decaying into stagnation.
  - When to use: as the lens for every decision about whether/what to test—ask "does this test help the project grow sustainably?"
  - How: keep only tests of positive net value; focus effort on the domain model; run tests on every change.
- **Negative-vs-positive indicator principle**: a signal that reliably flags badness but cannot confirm goodness.
  - When to use: evaluating testability of code AND coverage numbers.
  - How: low signal (hard to test code; coverage <60%) = real problem. High signal (easy to test; 100% coverage) = proves nothing.
- **Cost-benefit (net value) analysis of a test**: value minus upkeep cost.
  - When to use: deciding whether a test stays in the suite.
  - How: weigh benefit (catching regressions) against cost components: refactoring the test when code changes, running it each change, dealing with false alarms, and reading it to understand code.
- **Successful test suite (3 attributes)**: (1) integrated into the development cycle, (2) targets only the most important parts of the code base (the domain model), (3) provides maximum value with minimum maintenance cost.

## Key Concepts
- **Sustainable growth**: maintaining development pace over the long run, not just at the start.
- **Software entropy**: code's tendency to deteriorate—each change increases disorder until the system stagnates without refactoring.
- **Regression**: a feature stops working after a code change; synonym for software bug.
- **Coverage metric**: how much source code a test suite *executes*, from 0% to 100%.
- **Code coverage (test coverage)**: lines executed ÷ total lines of production code.
- **Branch coverage**: branches traversed ÷ total branches (control structures); ignores line count.
- **Assertion-free testing**: tests with no assertions—execute code, verify nothing, always pass; an extreme coverage-gaming case.
- **Domain model**: the business-logic part of the code base; highest-return target for tests.
- **Code is a liability, not an asset**: more code (including test code) = more surface for bugs and more upkeep.

## Mental Models
- **Think of testability and coverage as a thermometer**: a high temperature flags illness, but you don't "treat" the patient by pointing an A/C at the thermometer. Targeting a coverage number is gaming the gauge.
- **Use coverage as an indicator, never a goal**: a mandatory % creates a perverse incentive that distracts from testing what matters.
- **Think of recognizing a good test vs. writing one as recognizing a good song vs. composing one**: judging value is far cheaper than producing value (which requires code-design skill).
- **Use tests as a safety net** against regressions—the payoff is in the project's later stages, not day one.

## Anti-patterns
- **Chasing a coverage target (100/90/70%)**: incentivizes gaming over meaningful testing; high coverage ≠ quality.
- **Assertion-free / try-catch-wrapped tests**: show 100% coverage but verify nothing; pure upkeep cost, negative value.
- **Treating tests as free additions**: ignores that test code is itself a liability requiring maintenance.
- **"More tests = better"**: tests of zero or negative net value drag the project down even if they delay stagnation.

## Code Examples
```csharp
public static bool WasLastStringLong { get; private set; }
public static bool IsStringLong(string input)
{
    bool result = input.Length > 5;
    WasLastStringLong = result;   // implicit (second) outcome — NOT verified
    return result;                // explicit (first) outcome
}
public void Test()
{
    bool result = IsStringLong("abc");
    Assert.Equal(false, result);  // only checks the explicit outcome
}
```
- **What it demonstrates**: coverage shows 100% code / 50% branch even though the second outcome is unverified—coverage proves execution, not testing.

## Reference Tables
| Metric | Formula | Strength | Weakness |
|--------|---------|----------|----------|
| Code coverage | lines executed ÷ total lines | simple, common | gameable by inlining/compacting code |
| Branch coverage | branches taken ÷ total branches | ignores line count, more precise | ignores assertions; blind to external-library paths |

## Worked Example
`IsStringLong("abc")` against `if (input.Length > 5) return true; return false;` (5 lines incl. braces): the test runs 4 of 5 lines (skips `return true;`) → **80% code coverage**. Inline it to `return input.Length > 5;` and the same test now executes all 3 lines → **100% code coverage**—yet nothing improved; the code was merely compacted. Branch coverage exposes this: the method has **two** branches (length > 5 / not), the test exercises one → **50%**, unchanged by the rewrite. Two further holes remain even at high branch coverage: (1) an implicit outcome (a recorded property) can go unasserted, and (2) `int.Parse(input)` reports 100% branch coverage while ignoring the .NET library's hidden paths (null, empty, non-numeric, overflow). Real story: a company mandated 100% coverage; developers wrapped tests in `try/catch` with no assertions to pass the gate—worthless tests, pure upkeep, requirement eventually retracted.

## Key Takeaways
1. The goal of unit testing is sustainable growth, not test count or coverage.
2. Code deteriorates (entropy); good tests are the safety net that overturns the trend.
3. Both production and test code are liabilities—keep only tests of positive net value.
4. Testability and coverage are good negative indicators, bad positive ones.
5. Branch coverage beats code coverage but still ignores assertions and external library paths.
6. Mandating a coverage number creates a perverse incentive; use it as an indicator only.
7. Focus testing on the domain model; isolate it from infrastructure/glue code.

## Connects To
- **Ch 2**: defines what a unit *is* (classical vs. London schools), refining "unit testing."
- **Ch 4**: the frame of reference for what makes a good vs. bad test (the four pillars).
- **Ch 5**: mocks and test fragility—why London-style tests can raise false alarms (an upkeep cost named here).
